#!/usr/bin/env python3
"""Prepare and verify one self-contained arXiv submission per canonical paper.

Sources and PDF proofs live in arxiv/<slug>; upload ZIPs and build evidence live
in output/arxiv. No compilation runs inside a source folder.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from build import check_tex_log, pages_in, strip_comments, tex_env, write_zip_member
from publication import load_manifest, local_path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] if HERE.parent.name == "docs" else HERE
SOURCE_ROOT = ROOT / "arxiv"
OUTPUT = ROOT / "output" / "arxiv"
INPUT = re.compile(r"\\(?:input|include)\{([^{}]+)\}")
CSV = re.compile(r"\{(data/[^{}]+\.csv)\}")
CITE = re.compile(r"\\cite(?:\[[^\]]*\])?\{([^{}]+)\}")
BIBITEM = re.compile(r"\\bibitem(?:\[[^\]]*\])?\{([^{}]+)\}")
NAME = re.compile(r"[a-zA-Z0-9_+.,=/-]+")
NOTE = (
    r"Part of the 2026 \emph{Curious Signals} retrospective of work carried out in "
    "{year}; references, apparatus descriptions and supporting materials updated "
    "in October 2026."
)
LAYOUT = (
    r"\usepackage[letterpaper,margin=1in,includeheadfoot,headheight=12pt,"
    r"headsep=12pt,footskip=20pt]{geometry}"
    "\n"
    r"\usepackage{adjustbox}"
    "\n"
)


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def paper_stem(paper: dict) -> str:
    """Use the historical work month and the complete article title."""
    month, year = paper["period"].split()
    month_number = list(calendar.month_name).index(month)
    title = unicodedata.normalize("NFKD", paper["title"]).encode("ascii", "ignore").decode()
    title = re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "")).strip("-")
    return f"{year}-{month_number:02d}_{title}"


def fit_tex(content: bytes, name: str) -> bytes:
    """Constrain existing diagrams and tables to the new column width."""
    text = content.decode("utf-8")
    if name == "content/transit-method.tex":
        original = (
            r"X_i=D+g\int h_i(t_i-\tau)\mathcal{L}(\tau)\,d\tau+\epsilon_i,"
            "\n"
            r"\qquad \int h_i(u)\,du=1."
        )
        reflow = (
            r"\begin{aligned}"
            "\n"
            r"X_i&=D+g\int h_i(t_i-\tau)\mathcal{L}(\tau)\,d\tau+\epsilon_i,\\"
            "\n"
            r"\int h_i(u)\,du&=1."
            "\n"
            r"\end{aligned}"
        )
        if text.count(original) != 1:
            raise ValueError("Transit response equation changed; review its arXiv line breaks")
        text = text.replace(original, reflow)
    for environment in ("tikzpicture", "tabular"):
        start = r"\begin{" + environment + "}"
        end = r"\end{" + environment + "}"
        wrap = (
            (start, r"\begin{adjustbox}{max width=\linewidth}" + "\n" + start),
            (end, end + "\n" + r"\end{adjustbox}"),
        )
        for old, new in wrap:
            # A match after an unescaped % is commented out; a newline would revive it.
            def live(match: re.Match) -> str:
                before = text[text.rfind("\n", 0, match.start()) + 1 : match.start()]
                return new if strip_comments(before) == before else old

            text = re.sub(re.escape(old), live, text)
    return text.encode("utf-8")


def checked_path(base: Path, name: str) -> Path:
    """Require portable spelling, exact case, and a file contained in base."""
    relative = local_path(name)
    if not NAME.fullmatch(name) or any(part.startswith(".") for part in relative.parts):
        raise ValueError(f"Non-portable source path: {name}")
    current = base
    for part in relative.parts:
        if part not in {entry.name for entry in current.iterdir()}:
            raise ValueError(f"Missing or incorrectly cased source: {name}")
        current = current / part
    if not current.is_file() or not current.resolve().is_relative_to(base.resolve()):
        raise ValueError(f"Source escapes package: {name}")
    return current


def citations(text: str) -> set[str]:
    return {key.strip() for match in CITE.findall(text) for key in match.split(",")}


def bibliography(keys: set[str]) -> bytes:
    """Select complete entries from this repository's plain BibTeX database."""
    text = (HERE / "references.bib").read_text(encoding="utf-8")
    starts = list(re.finditer(r"(?m)^@(\w+)\s*\{\s*([^,\s]+)\s*,", text))
    if any(match.group(1).lower() in {"string", "preamble", "comment"} for match in starts):
        raise ValueError("Add explicit support before using special BibTeX entries")
    entries = {}
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        key = match.group(2)
        if key in entries:
            raise ValueError(f"Duplicate bibliography key: {key}")
        entries[key] = text[match.start() : end].strip()
    missing = keys - entries.keys()
    if missing:
        raise ValueError(f"Missing bibliography entries: {sorted(missing)}")
    return ("\n\n".join(entries[key] for key in sorted(keys)) + "\n").encode("utf-8")


def main_source(paper: dict) -> bytes:
    common = (HERE / "common.tex").read_text(encoding="utf-8")
    common = common[common.index(r"\documentclass") :]
    old = r"\quad\textperiodcentered\quad\paperperiod}\thanks{\dataprovenance}}%"
    note = NOTE.replace("{year}", paper["period"].split()[-1])
    new = r"\quad\textperiodcentered\quad\paperperiod}\thanks{\dataprovenance}"
    new += r"\thanks{" + note + "}}%"
    if common.count(old) != 1:
        raise ValueError("Shared author format changed; update arXiv title adaptation")
    common = common.replace(old, new)
    header = (
        r"\markboth{Curious Signals --- Measurements and Laboratory Models}%"
        "\n"
        r"    {Spicker and K\"upper: \papershorttitle}%"
    )
    if common.count(header) != 1:
        raise ValueError("Shared running-header format changed; update arXiv adaptation")
    common = common.replace(header, r"\markboth{\papershorttitle}{\papershorttitle}%")
    common = common.replace(
        r"\usepackage{cite,microtype}",
        r"\usepackage{cite,microtype}" + "\n" + r"\microtypesetup{protrusion=false}",
    )
    common = common.replace(
        r"\setlength{\emergencystretch}{1em}", r"\setlength{\emergencystretch}{2em}"
    )
    common = common.replace(
        r"\documentclass[journal]{IEEEtran}", r"\documentclass[journal]{IEEEtran}" + "\n" + LAYOUT
    )
    wrapper = (HERE / f"{paper['slug']}.tex").read_text(encoding="utf-8")
    if wrapper.count(r"\input{common.tex}") != 1:
        raise ValueError(f"{paper['slug']}: unexpected wrapper preamble")
    return wrapper.replace(r"\input{common.tex}", common).encode("utf-8")


def source_files(paper: dict) -> tuple[dict[str, bytes], set[str]]:
    filename = paper_stem(paper) + ".tex"
    files = {filename: main_source(paper)}
    pending = [filename]
    keys = set()
    while pending:
        name = pending.pop()
        text = strip_comments(files[name].decode("utf-8"))
        if re.search(r"\\(?:includegraphics|externaldocument|addbibresource|write18)\b", text):
            raise ValueError(f"{name}: unsupported external dependency command")
        if re.search(r"\\(?:input|include)\b(?!\{)", text):
            raise ValueError(f"{name}: only braced literal TeX inputs are supported")
        keys.update(citations(text))
        dependencies = [
            target if target.endswith(".tex") else target + ".tex" for target in INPUT.findall(text)
        ]
        dependencies.extend(CSV.findall(text))
        for target in dependencies:
            if target in files:
                continue
            if not target.startswith(("content/", "figures/", "topic-figures/", "data/")):
                raise ValueError(f"{name}: unsupported dependency {target}")
            files[target] = checked_path(HERE, target).read_bytes()
            if target.endswith(".tex"):
                files[target] = fit_tex(files[target], target)
                pending.append(target)
    if not keys:
        raise ValueError(f"{paper['slug']}: no citations")
    files["references.bib"] = bibliography(keys)
    config = {
        "spec_version": 1,
        "texlive_version": 2025,
        "process": {"compiler": "pdflatex"},
        "sources": [{"filename": filename, "usage": "toplevel"}],
    }
    files["00README.json"] = (json.dumps(config, indent=2) + "\n").encode("utf-8")
    if paper["slug"] == "transit-method":
        source = "drafts/detector-characterization_summary.example.csv"
        summary = checked_path(ROOT / "example-data", source)
        files["anc/detector-characterization-summary.csv"] = summary.read_bytes()
        with summary.open(encoding="utf-8", newline="") as stream:
            row = next(csv.DictReader(stream))
        analysis = json.loads((HERE / "draft-analysis.json").read_text(encoding="utf-8"))
        detector = analysis["metrics"]["detector-characterization"]
        start, stop = detector["baseline_window_s"]
        count = int(float(row["Selected baseline count (1)"]))
        drop = float(row["Proposed signal drop (counts)"])
        ratio = float(row["Expected single-sample SNR (1)"])
        files["anc/README.txt"] = (
            "Detector characterization: numerical summary\n\n"
            "detector-characterization-summary.csv is an unchanged copy of\n"
            "example-data/drafts/detector-characterization_summary.example.csv\n"
            "from the Curious Signals example-data collection. It is the\n"
            "accompanying numerical summary discussed in this paper.\n\n"
            "Sensor: Arduino Nano 33 BLE Sense APDS-9960. Acquisition path:\n"
            "derived summary from the 20 Hz example record. The selected\n"
            f"illuminated baseline spans device times {start} to {stop} s and has {count}\n"
            "readings. This is an example dataset, not a newly measured result.\n\n"
            "The proposed 2% signal drop uses an entered dark value of 8 counts,\n"
            f"giving a {drop:.3f}-count decrement and a single-sample planning\n"
            f"amplitude ratio of {ratio:.3f}. The observed dark mean is "
            f"{detector['dark_mean_counts']:.3f} counts.\n"
            "These distinct values are retained as explained in the manuscript;\n"
            "the planning ratio is not a detection significance.\n"
        ).encode("utf-8")
    return dict(sorted(files.items())), keys


def write_files(folder: Path, files: dict[str, bytes]) -> None:
    for name, content in files.items():
        destination = folder / local_path(name)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)


def refuse_hand_edits(slug: str, folder: Path, files: dict[str, bytes]) -> None:
    """Never overwrite a source file that differs from both the new build and the last one."""
    try:
        report = json.loads((OUTPUT / "build-summary.json").read_text(encoding="utf-8"))
        recorded = next(item for item in report["papers"] if item["slug"] == slug)["source_sha256"]
    except (OSError, ValueError, KeyError, StopIteration):
        recorded = {}
    edited = sorted(
        name
        for name, content in existing_files(folder).items()
        if name in files and content != files[name] and recorded.get(name) != digest(content)
    )
    if edited:
        raise ValueError(
            f"{slug}: {edited} differ from the previous build; move the hand edits "
            "into docs/papers or delete the file first"
        )


def command(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        args, cwd=cwd, env=tex_env(), capture_output=True, text=True, check=False
    )
    if result.returncode:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(args)}\n"
            + result.stdout[-10000:]
            + result.stderr[-4000:]
        )
    return result.stdout


def validate_recorder(folder: Path, stem: str, files: dict[str, bytes]) -> list[str]:
    """Every project input must come from this isolated compilation directory."""
    used = set()
    system_root = Path(command(["kpsewhich", "--var-value=TEXMFROOT"], folder).strip()).resolve()
    for line in (folder / f"{stem}.fls").read_text(encoding="utf-8").splitlines():
        if not line.startswith("INPUT "):
            continue
        raw = Path(line[6:])
        path = (folder / raw).resolve() if not raw.is_absolute() else raw.resolve()
        if path.is_relative_to(folder.resolve()):
            name = path.relative_to(folder.resolve()).as_posix()
            if name in files:
                used.add(name)
            elif name not in {f"{stem}.aux", f"{stem}.out"}:
                raise ValueError(f"Unexpected generated input: {name}")
        elif not path.is_relative_to(system_root):
            raise ValueError(f"Input outside submission and TeX distribution: {path}")
    expected = {
        name
        for name in files
        if name not in {"00README.json", "references.bib"} and not name.startswith("anc/")
    }
    if used != expected:
        raise ValueError(f"Unused or unrecorded submission inputs: {sorted(expected ^ used)}")
    return sorted(used)


def validate_bbl(content: bytes, keys: set[str]) -> None:
    text = content.decode("utf-8")
    found = BIBITEM.findall(text)
    if set(found) != keys or len(found) != len(keys) or r"\begin{thebibliography}" not in text:
        raise ValueError("Prepared bibliography does not match this paper's citations")


def compile_paper(folder: Path, stem: str, *, bibtex: bool) -> None:
    args = [
        "pdflatex",
        "-no-shell-escape",
        "-recorder",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        f"{stem}.tex",
    ]
    command(args, folder)
    if bibtex:
        command(["bibtex", stem], folder)
    for _ in range(4):
        before = [(folder / f"{stem}.{suffix}").read_bytes() for suffix in ("aux", "out")]
        command(args, folder)
        after = [(folder / f"{stem}.{suffix}").read_bytes() for suffix in ("aux", "out")]
        if before == after:
            break
    else:
        raise ValueError("TeX references did not converge")
    check_tex_log(folder / f"{stem}.log", stem)


def archive_bytes(files: dict[str, bytes], destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            write_zip_member(archive, name, content, (2026, 10, 27, 0, 0, 0))


def existing_files(folder: Path) -> dict[str, bytes]:
    if not folder.is_dir():
        return {}
    result = {}
    for path in folder.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Source folder contains a symbolic link: {path}")
        if path.is_file() and path.name != ".DS_Store":
            result[path.relative_to(folder).as_posix()] = path.read_bytes()
    return result


def check_paper(paper: dict, files: dict[str, bytes], keys: set[str]) -> None:
    stem = paper_stem(paper)
    folder = SOURCE_ROOT / paper["slug"]
    actual = existing_files(folder)
    bbl = actual.pop(f"{stem}.bbl", None)
    pdf = actual.pop(f"{stem}.pdf", None)
    if actual != files:
        missing = sorted(files.keys() - actual.keys())
        extra = sorted(actual.keys() - files.keys())
        changed = sorted(
            name for name in files.keys() & actual.keys() if files[name] != actual[name]
        )
        raise ValueError(
            f"{paper['slug']}: source folder is stale: missing={missing}, extra={extra}, "
            f"changed={changed}; run make arxiv"
        )
    if bbl is None:
        raise ValueError(f"{paper['slug']}: missing {stem}.bbl; run make arxiv")
    if pdf is None:
        raise ValueError(f"{paper['slug']}: missing adjacent PDF proof; run make arxiv")
    validate_bbl(bbl, keys)
    # Recreate only BibTeX's inputs, outside the source folder, to detect stale
    # bibliographic fields even when citation keys have not changed.
    citation_commands = []

    def visit(name: str) -> None:
        text = strip_comments(files[name].decode("utf-8"))
        pattern = r"\\(?:input|include)\{([^{}]+)\}|\\cite(?:\[[^\]]*\])?\{([^{}]+)\}"
        for match in re.finditer(pattern, text):
            target, cited = match.groups()
            if cited is not None:
                citation_commands.append(r"\citation{" + cited + "}")
            else:
                visit(target if target.endswith(".tex") else target + ".tex")

    visit(f"{stem}.tex")
    with tempfile.TemporaryDirectory(prefix="curious-signals-arxiv-bibliography-") as temporary:
        folder = Path(temporary)
        aux = "\n".join(
            [r"\relax", *citation_commands, r"\bibstyle{IEEEtran}", r"\bibdata{references}", ""]
        )
        (folder / f"{stem}.aux").write_text(aux, encoding="utf-8")
        (folder / "references.bib").write_bytes(files["references.bib"])
        command(["bibtex", stem], folder)
        if (folder / f"{stem}.bbl").read_bytes() != bbl:
            raise ValueError(f"{paper['slug']}: prepared bibliography is stale; run make arxiv")
    expected = {**files, f"{stem}.bbl": bbl}
    report_path = OUTPUT / "build-summary.json"
    if not report_path.is_file():
        raise ValueError("Missing arXiv build evidence; run make arxiv")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    record = next((item for item in report["papers"] if item["slug"] == paper["slug"]), None)
    if record is None or record.get("stem") != stem:
        raise ValueError(f"{paper['slug']}: missing current build evidence; run make arxiv")
    paths = artifact_paths(paper)
    if any(record.get(name) != path for name, path in paths.items()):
        raise ValueError(f"{paper['slug']}: artifact paths differ from build evidence")
    if record["source_sha256"] != {name: digest(data) for name, data in sorted(expected.items())}:
        raise ValueError(f"{paper['slug']}: source hashes differ from build evidence")
    if record["pdf_sha256"] != digest(pdf):
        raise ValueError(f"{paper['slug']}: adjacent PDF differs from verified build")
    archive_path = ROOT / paths["source_zip"]
    if not archive_path.is_file() or record["zip_sha256"] != digest(archive_path.read_bytes()):
        raise ValueError(f"{paper['slug']}: upload ZIP differs from verified build")
    with zipfile.ZipFile(archive_path) as archive:
        if (
            len(archive.namelist()) != len(expected)
            or {name: archive.read(name) for name in archive.namelist()} != expected
        ):
            raise ValueError(f"{paper['slug']}: upload ZIP is not the exact source package")


def artifact_paths(paper: dict) -> dict[str, str]:
    stem = paper_stem(paper)
    return {
        "tex": f"arxiv/{paper['slug']}/{stem}.tex",
        "pdf": f"arxiv/{paper['slug']}/{stem}.pdf",
        "source_zip": f"output/arxiv/{stem}.zip",
    }


def build_paper(paper: dict, files: dict[str, bytes], keys: set[str]) -> dict:
    slug = paper["slug"]
    stem = paper_stem(paper)
    existing = existing_files(SOURCE_ROOT / slug)
    extras = existing.keys() - files.keys() - {f"{stem}.bbl", f"{stem}.pdf"}
    if extras:
        raise ValueError(
            f"{slug}: preserve or relocate unexpected source files first: {sorted(extras)}"
        )
    refuse_hand_edits(slug, SOURCE_ROOT / slug, files)
    with tempfile.TemporaryDirectory(prefix=f"curious-signals-arxiv-{slug}-") as temporary:
        work = Path(temporary)
        compile_dir = work / "compile"
        compile_dir.mkdir()
        write_files(compile_dir, files)
        compile_paper(compile_dir, stem, bibtex=True)
        files = {**files, f"{stem}.bbl": (compile_dir / f"{stem}.bbl").read_bytes()}
        validate_bbl(files[f"{stem}.bbl"], keys)
        validate_recorder(compile_dir, stem, files)
        count = pages_in(compile_dir / f"{stem}.pdf")
        limit = paper.get("page_limit", count)
        if count > limit:
            print(
                f"{slug}: {count} pages exceeds collection limit {limit}; "
                "retained to meet arXiv margins.",
                flush=True,
            )
        archive_path = work / f"{stem}.zip"
        archive_bytes(files, archive_path)
        extracted = work / "extracted"
        extracted.mkdir()
        with zipfile.ZipFile(archive_path) as archive:
            if archive.testzip() is not None:
                raise ValueError(f"{slug}: corrupt source ZIP")
            archive.extractall(extracted)
        if existing_files(extracted) != files:
            raise ValueError(f"{slug}: extracted ZIP differs from prepared sources")
        compile_paper(extracted, stem, bibtex=False)
        used = validate_recorder(extracted, stem, files)
        if pages_in(extracted / f"{stem}.pdf") != count:
            raise ValueError(f"{slug}: uploaded bibliography changed pagination")
        for name in (f"{stem}.log", f"{stem}.fls", f"{stem}.blg"):
            source = extracted / name if (extracted / name).exists() else compile_dir / name
            target = OUTPUT / "logs" / slug / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        write_files(SOURCE_ROOT / slug, files)
        OUTPUT.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(archive_path, OUTPUT / f"{stem}.zip")
        shutil.copyfile(extracted / f"{stem}.pdf", SOURCE_ROOT / slug / f"{stem}.pdf")
        return {
            "slug": slug,
            "stem": stem,
            **artifact_paths(paper),
            "title": paper["title"],
            "period": paper["period"],
            "pages": count,
            "collection_page_limit": limit,
            "exceeds_collection_page_limit": count > limit,
            "citations": sorted(keys),
            "recorded_inputs": used,
            "source_sha256": {name: digest(content) for name, content in sorted(files.items())},
            "zip_sha256": digest(archive_path.read_bytes()),
            "pdf_sha256": digest((extracted / f"{stem}.pdf").read_bytes()),
            "verified_extracted_zip_without_bibtex": True,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Check source freshness without writing"
    )
    parser.add_argument("--only", help="Prepare/check just one canonical paper slug")
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="Number of independent paper builds to run at once (default: 1)",
    )
    args = parser.parse_args()
    if args.jobs < 1:
        raise ValueError("--jobs must be positive")
    catalog = load_manifest(HERE / "manifest.json")
    papers = catalog["papers"]
    if args.only:
        papers = [paper for paper in papers if paper["slug"] == args.only]
        if not papers:
            raise ValueError(f"Unknown canonical paper: {args.only}")
    programs = ("bibtex",) if args.check else ("pdflatex", "bibtex", "kpsewhich", "pdfinfo")
    for program in programs:
        if shutil.which(program) is None:
            raise ValueError(f"Missing required program: {program}")

    def process(paper: dict) -> dict | None:
        files, keys = source_files(paper)
        if args.check:
            check_paper(paper, files, keys)
            print(f"Checked {paper['slug']}: self-contained sources are current", flush=True)
            return None
        else:
            result = build_paper(paper, files, keys)
            print(
                f"Prepared {paper['slug']}: {result['pages']} pages, extracted ZIP verified",
                flush=True,
            )
            return result

    order = {paper["slug"]: index for index, paper in enumerate(catalog["papers"])}
    report_path = OUTPUT / "build-summary.json"
    pdflatex = None if args.check else command(["pdflatex", "--version"], HERE).splitlines()[0]

    def record(result: dict) -> None:
        """Merge one finished paper into the build summary, so evidence matches the files."""
        try:
            previous = json.loads(report_path.read_text(encoding="utf-8"))["papers"]
        except (OSError, ValueError, KeyError):
            previous = []
        kept = [
            item
            for item in previous
            if item.get("slug") in order and item["slug"] != result["slug"]
        ]
        report = {
            "edition_date": catalog["edition_date"],
            "target_texlive": 2025,
            "local_pdflatex": pdflatex,
            "compiler": "pdflatex",
            "shell_escape": False,
            "papers": sorted([*kept, result], key=lambda item: order[item["slug"]]),
        }
        OUTPUT.mkdir(parents=True, exist_ok=True)
        temporary = report_path.with_name(report_path.name + ".tmp")
        temporary.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, report_path)

    failures = []
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        pending = {executor.submit(process, paper): paper["slug"] for paper in papers}
        for future in as_completed(pending):
            try:
                result = future.result()
                if result is not None:
                    record(result)
            except (OSError, ValueError, RuntimeError, KeyError, zipfile.BadZipFile) as error:
                failures.append(f"{pending[future]}: {error}")
    if failures:
        raise RuntimeError("\n".join(failures))
    print(f"{'Checked' if args.check else 'Prepared'} {len(papers)} independent arXiv submissions.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, KeyError, zipfile.BadZipFile) as error:
        print(f"arxiv: {error}", file=sys.stderr)
        raise SystemExit(1) from error
