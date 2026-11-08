#!/usr/bin/env python3
"""Build final paper proofs, the retrospective collection and reproducible archives."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from prepare_drafts import prepare as prepare_drafts
from prepare_examples import DATA_ROOT, prepare
from publication import (
    load_manifest,
    local_path,
    paper_experiments,
    source_hashes,
    source_owners,
    source_registry,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] if HERE.parent.name == "docs" else HERE

# Every paper analyses generator output (example-data/generate_*example_data.py),
# so each companion, the collection guide and the PDF title block must say so.
DATA_PROVENANCE = (
    "**Data provenance.** The datasets analysed here are deterministic example data, "
    "generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`."
)
DATA_PROVENANCE_TEX = r"\thanks{\dataprovenance}"


def strip_comments(text: str) -> str:
    """Drop unescaped TeX comments (``%`` to end of line) before scanning commands."""
    return re.sub(r"(?<!\\)((?:\\\\)*)%[^\n]*", r"\1", text)


def manifest() -> list[dict[str, str]]:
    return load_manifest(HERE / "manifest.json")["papers"]


def snapshots() -> list[dict]:
    """Keep the historical snapshot intact and optionally verify the draft revision."""
    paths = [HERE / "source-snapshot.json"]
    draft = HERE / "draft-source-snapshot.json"
    if draft.is_file():
        paths.append(draft)
    return [json.loads(path.read_text(encoding="utf-8")) for path in paths]


def check_sources(papers: list[dict], catalog: dict | None = None) -> None:
    # Imported here because the arXiv packager imports this module's helpers.
    from prepare_arxiv import citations

    catalog = load_manifest(HERE / "manifest.json") if catalog is None else catalog
    sources = catalog["analysis_sources"]
    indexes = [
        json.loads((DATA_ROOT / name).read_text(encoding="utf-8"))
        for name in ("manifest.json", "drafts/manifest.json")
    ]
    records = [item for index in indexes for item in index["datasets"]]
    known_data = {item["file"]: item["experiment"] for item in records}
    if len(known_data) != len(records):
        raise ValueError("Duplicate input dataset registration")
    covered_data = []
    covered_experiments = []
    bibliography = (HERE / "references.bib").read_text(encoding="utf-8")
    found_keys = re.findall(r"@\w+\s*\{\s*([^,\s]+)", bibliography)
    keys = set(found_keys)
    if len(keys) != len(found_keys):
        raise ValueError("Duplicate bibliography key")
    for source in sources:
        if not source.get("datasets"):
            raise ValueError(f"{source['slug']}: missing primary input datasets")
        experiment = local_path(source["experiment"], folder="experiments")
        covered_experiments.append(str(experiment))
        for dataset in source["datasets"]:
            local_path(dataset)
            if known_data.get(dataset) != experiment.name:
                raise ValueError(f"{source['slug']}: mismatched dataset {dataset}")
            covered_data.append(dataset)
        for dataset in source.get("related_datasets", []):
            if dataset not in known_data:
                raise ValueError(f"{source['slug']}: unknown related dataset {dataset}")
        if source["date_basis"] not in keys:
            raise ValueError(f"{source['slug']}: missing historical date source")
    if set(covered_data) != set(known_data) or len(covered_data) != len(set(covered_data)):
        raise ValueError("Every supplied CSV must be assigned to exactly one analysis source")
    if len(covered_experiments) != len(set(covered_experiments)):
        raise ValueError("An experiment is assigned to multiple analysis sources")
    for paper in papers:
        wrapper = HERE / f"{paper['slug']}.tex"
        body = HERE / "content" / f"{paper['slug']}.tex"
        if not wrapper.is_file() or not body.is_file():
            raise ValueError(f"{paper['slug']}: missing canonical wrapper or body")
        date_command = r"\newcommand{\paperperiod}{" + paper["period"] + "}"
        if date_command not in wrapper.read_text(encoding="utf-8"):
            raise ValueError(f"{paper['slug']}: title date does not match the publication manifest")
        text = body.read_text(encoding="utf-8")
        if text.count(r"\begin{figure}") + text.count(r"\begin{figure*}") < 2:
            raise ValueError(f"{body.name}: expected apparatus and analysis figures")
        if r"\begin{tikzpicture}" not in text:
            raise ValueError(f"{body.name}: missing apparatus diagram")
        if r"\begin{table}" not in text and r"\begin{table*}" not in text:
            raise ValueError(f"{body.name}: missing quantitative table")
        declared = paper.get("figures")
        if not isinstance(declared, list) or not declared or len(declared) != len(set(declared)):
            raise ValueError(f"{body.name}: declare a nonempty, unique figure list")
        inputs = {
            name if name.endswith(".tex") else name + ".tex"
            for name in re.findall(r"\\input\{([^}]+)\}", strip_comments(text))
            if name.startswith(("figures/", "topic-figures/"))
        }
        if inputs != set(declared):
            raise ValueError(f"{body.name}: declared plot paths do not match article inputs")
        for name in declared:
            relative = local_path(name)
            if (
                relative.parts[0] not in {"figures", "topic-figures"}
                or not (HERE / relative).is_file()
            ):
                raise ValueError(f"{body.name}: missing or misplaced plot {name}")
        if re.search(r"\bexample[\s~-]+data\b", text, re.IGNORECASE):
            raise ValueError(
                f"{body.name}: use direct descriptions without the repeated data label"
            )
        companion = HERE / local_path(paper["markdown"], folder="companions")
        if not companion.is_file() or not companion.read_text(encoding="utf-8").startswith("# "):
            raise ValueError(f"{paper['slug']}: missing canonical Markdown companion")
        if f"\n\n*{paper['period']}*\n\n" not in companion.read_text(encoding="utf-8"):
            raise ValueError(
                f"{paper['slug']}: Markdown date does not match the publication manifest"
            )
        if DATA_PROVENANCE not in companion.read_text(encoding="utf-8"):
            raise ValueError(f"{paper['slug']}: companion must state its data provenance")
        cited = citations(strip_comments(text))
        if cited - keys:
            raise ValueError(f"{body.name}: unknown bibliography keys {sorted(cited - keys)}")
        if not 3 <= len(cited) <= 10:
            raise ValueError(f"{body.name}: expected 3--10 selectively cited references")
    if DATA_PROVENANCE not in (HERE / "README.md").read_text(encoding="utf-8"):
        raise ValueError("README.md: collection guide must state the data provenance")
    if DATA_PROVENANCE_TEX not in (HERE / "common.tex").read_text(encoding="utf-8"):
        raise ValueError("common.tex: the title block must carry the data provenance note")
    experiment_dir = ROOT / "experiments"
    if experiment_dir.is_dir():
        actual = {
            str(path.relative_to(ROOT))
            for folder in (
                experiment_dir,
                experiment_dir / "astronomy",
                experiment_dir / "drafts",
            )
            for path in folder.glob("*.phyphox")
        }
        if actual != set(covered_experiments):
            raise ValueError(
                f"Experiment coverage mismatch: {sorted(actual ^ set(covered_experiments))}"
            )
        for snapshot in snapshots():
            for name, expected in snapshot["sha256"].items():
                if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
                    raise ValueError(f"Source changed since the documented snapshot: {name}")
    original = json.loads((HERE / "example-analysis.json").read_text(encoding="utf-8"))
    draft = json.loads((HERE / "draft-analysis.json").read_text(encoding="utf-8"))
    revision = json.loads((HERE / "revision-analysis.json").read_text(encoding="utf-8"))
    original_ids = {
        source["slug"]
        for source in sources
        if not source["experiment"].startswith("experiments/drafts/")
    }
    draft_ids = set(source_registry(catalog)) - original_ids
    if set(original["metrics"]) != original_ids or set(draft["metrics"]) != draft_ids:
        raise ValueError("Every analysis source must retain its reproducible numerical reductions")
    if set(revision["metrics"]) != original_ids:
        raise ValueError("Every original source must retain its supplementary analysis")
    for source in sources:
        report = draft if source["slug"] in draft_ids else revision
        inputs = report["papers"][source["slug"]]["inputs"]
        expected = set(source["datasets"]) | set(source.get("related_datasets", []))
        if set(inputs) != expected:
            raise ValueError(f"{source['slug']}: incomplete analysis-source provenance")
    print(
        f"Checked {len(papers)} canonical papers, {len(sources)} analysis sources, "
        f"and {len(known_data)} CSV inputs."
    )


def run(command: list[str], *, cwd: Path) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode:
        print(result.stdout[-10000:], file=sys.stderr)
        print(result.stderr[-4000:], file=sys.stderr)
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command)}")
    return result.stdout


TEX_ENV_VARS = ("TEXINPUTS", "BIBINPUTS", "BSTINPUTS", "TEXMFHOME", "TEXMFOUTPUT")


def tex_env() -> dict[str, str]:
    """Do not let a developer's search path hide a missing package input."""
    return {key: value for key, value in os.environ.items() if key not in TEX_ENV_VARS}


def tex_log_problems(path: Path) -> list[str]:
    log = path.read_text(encoding="utf-8", errors="replace")
    bad = (
        "There were undefined references",
        "There were multiply-defined labels",
        "Citation `",
        "Overfull ",
        "Float too large",
        "Missing character:",
    )
    return [line for line in log.splitlines() if any(term in line for term in bad)]


def check_tex_log(path: Path, name: str) -> None:
    warnings = tex_log_problems(path)
    if warnings:
        raise RuntimeError(f"{name}: unresolved typesetting diagnostics:\n" + "\n".join(warnings))


def write_zip_member(
    archive: zipfile.ZipFile, name: str, content: bytes, date_time: tuple[int, ...]
) -> None:
    info = zipfile.ZipInfo(name, date_time=date_time)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, content)


def pages_in(path: Path) -> int:
    info = run(["pdfinfo", str(path)], cwd=HERE)
    match = re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE)
    if match is None:
        raise ValueError(f"Could not read PDF page count: {path}")
    return int(match.group(1))


MARKDOWN_LINK = re.compile(r"(!?)\[([^\]]+)\]\((<[^>]+>|[^)\s]+)(\s+\"[^\"]*\")?\)")


def portable_markdown(
    text: str,
    source: Path,
    destination: Path,
    mapping: dict[Path, Path],
    pdf_names: set[str],
) -> str:
    """Relocate packaged links and leave unavailable repository context as plain labels."""

    def relocate(match: re.Match) -> str:
        image, label, raw_target, title = match.groups()
        target = urlsplit(raw_target.strip("<>"))
        if target.scheme or target.netloc or not target.path:
            return match.group(0)
        resolved = (source.parent / unquote(target.path)).resolve()
        archived = mapping.get(resolved)
        if resolved.parent in {
            (ROOT / "output/pdf").resolve(),
            (ROOT / "pdf").resolve(),
        }:
            canonical = source_owners(load_manifest(HERE / "manifest.json")).get(
                resolved.stem, resolved.stem
            )
            name = f"{canonical}.pdf" if resolved.suffix == ".pdf" else resolved.name
            if name in pdf_names:
                archived = Path("pdf") / name
        if archived is None:
            return label
        relative = posixpath.relpath(archived.as_posix(), destination.parent.as_posix())
        url = quote(relative, safe="/.@-_")
        if target.query:
            url += "?" + target.query
        if target.fragment:
            url += "#" + target.fragment
        return f"{image}[{label}]({url}{title or ''})"

    return MARKDOWN_LINK.sub(relocate, text)


def portable_readme(papers: list[dict], available: set[Path]) -> str:
    lines = [
        "# Curious Signals research companions",
        "",
        f"Editable LaTeX sources for {len(papers)} papers, their analyses,",
        "and all 58 example CSVs.",
        "The original inputs and source snapshots are retained. PDF links below become available",
        "after rebuilding this archive.",
        "",
        "Required: Python 3.11+, PyMuPDF, latexmk, pdflatex, BibTeX, and Poppler (pdfinfo).",
        "The LaTeX installation needs IEEEtran, TikZ/PGFPlots, siunitx, booktabs,",
        "Latin Modern, AMS math, microtype, hyperref, geometry, adjustbox, fancyhdr,",
        "longtable, and xurl.",
        "The numerical preparation uses the Python standard library.",
        "",
        "Run these commands from the extracted directory:",
        "",
        "```sh",
        "python3 -m venv .venv",
        ". .venv/bin/activate",
        "python3 -m pip install 'PyMuPDF>=1.28.2,<2'",
        "python3 prepare_examples.py --check",
        "python3 prepare_drafts.py --check",
        "python3 build.py --check",
        "python3 build.py --output ./pdf",
        "```",
        "",
        "To regenerate prepared results after editing an analysis,",
        "run `python3 prepare_examples.py`",
        "and `python3 prepare_drafts.py` before checking. To build one paper, add `--only <slug>`",
        "to the build command. The build prepares and verifies independent arXiv copies,",
        "then assembles their final PDFs with the retrospective overview and continuous pages.",
        "Each canonical article also compiles directly with `latexmk -pdf <slug>.tex`.",
        "",
        "[Retrospective PDF](pdf/2026-10_curious-signals-retrospective.pdf) ·",
        "[Individual PDF ZIP](pdf/curious-signals-individual-papers.zip) ·",
        "[Rebuilt source ZIP](pdf/curious-signals-latex-sources.zip)",
        "",
        "[Paper and analysis-source manifest](manifest.json) ·",
        "[Original data index](example-data/manifest.json) ·",
        "[Additional data index](example-data/drafts/manifest.json) ·",
        "[Acquisition notes](implementation-notes.md) · [GPL text](LICENSE) ·",
        "[LGPL text](COPYING.LESSER)",
        "",
    ]
    for path, label in (
        ("draft-companions/README.md", "Editable companion index"),
        ("research/README.md", "Literature research index"),
    ):
        if Path(path) in available:
            lines.extend([f"[{label}]({path})", ""])
    lines.extend(["| Paper | Sources | Rebuilt PDF |", "| --- | --- | --- |"])
    for paper in papers:
        slug = paper["slug"]
        title = paper["title"].replace("|", r"\|")
        sources = [f"[LaTeX]({slug}.tex)"]
        companion = local_path(paper["markdown"], folder="companions")
        if companion in available:
            sources.append(f"[Markdown]({companion.as_posix()})")
        for index, name in enumerate(
            paper_experiments(paper, load_manifest(HERE / "manifest.json")), 1
        ):
            experiment = Path(name)
            if experiment in available:
                sources.append(f"[phyphox {index}]({experiment.as_posix()})")
        lines.append(f"| {title} | {' · '.join(sources)} | [PDF](pdf/{slug}.pdf) |")
    return "\n".join(lines) + "\n"


def source_archive(output: Path) -> None:
    catalog = load_manifest(HERE / "manifest.json")
    active = {paper["slug"] for paper in catalog["papers"]}
    companions = {local_path(paper["markdown"], folder="companions") for paper in catalog["papers"]}
    allowed = {".tex", ".bib", ".json", ".py", ".md", ".csv", ".phyphox"}
    snapshot_names = {name for snapshot in snapshots() for name in snapshot["sha256"]}
    license_names = {"LICENSE", "COPYING.LESSER"}
    paths = [(path, path.relative_to(HERE)) for path in HERE.rglob("*")]
    paths.extend((ROOT / name, Path(name)) for name in license_names)
    if DATA_ROOT != HERE / "example-data":
        paths.extend(
            (path, Path("example-data") / path.relative_to(DATA_ROOT))
            for path in DATA_ROOT.rglob("*")
        )
    # Preserve snapshot verification and include only the collection's source context.
    if ROOT != HERE:
        paths.extend((ROOT / name, Path(name)) for name in snapshot_names)
        paths.extend(
            (path, path.relative_to(ROOT))
            for path in (ROOT / "experiments/drafts").glob("*.phyphox")
        )
        paths.extend(
            (path, Path("draft-companions") / path.name)
            for path in (ROOT / "docs/drafts").glob("*")
            if path.suffix == ".md" or path.name == "manifest.json"
        )
    members: dict[Path, Path] = {}
    mapping: dict[Path, Path] = {}
    for path, relative in sorted(paths):
        if not path.is_file():
            continue
        if path.suffix not in allowed and str(relative) not in snapshot_names | license_names:
            continue
        if any(
            part.startswith(".") or part in {"__pycache__", "output", "pdf"}
            for part in relative.parts
        ):
            continue
        if relative.parts[0] == "arxiv":
            # A portable rebuild creates these beside the canonical sources.
            # They belong to the dedicated submission/retrospective bundles.
            continue
        if relative.suffix == ".tex":
            if len(relative.parts) == 1 and relative.name not in {
                "common.tex",
                "collection.tex",
            }:
                if relative.stem not in active:
                    continue
            if relative.parts[0] == "content" and relative.stem not in active:
                continue
        if relative.parts[0] == "companions" and relative not in companions:
            continue
        members.setdefault(relative, path)
        mapping.setdefault(path.resolve(), relative)
    # Snapshot-hashed Markdown is immutable. Supply aliases for its relocated targets.
    for relative, path in list(members.items()):
        if str(relative) not in snapshot_names or path.suffix != ".md":
            continue
        for match in MARKDOWN_LINK.finditer(path.read_text(encoding="utf-8")):
            target = urlsplit(match.group(3).strip("<>"))
            if target.scheme or target.netloc or not target.path:
                continue
            resolved = (path.parent / unquote(target.path)).resolve()
            if resolved in mapping:
                alias = resolved.relative_to(ROOT.resolve())
                members.setdefault(alias, resolved)
    papers = manifest()
    pdf_names = {f"{paper['slug']}.pdf" for paper in papers} | {
        "curious-signals-research-companions.pdf",
        "2026-10_curious-signals-retrospective.pdf",
        "2026-10_curious-signals-retrospective-sources.zip",
        "curious-signals-individual-papers.zip",
        "curious-signals-latex-sources.zip",
    }
    readme = portable_readme(papers, set(members))
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative, path in sorted(members.items()):
            content = path.read_bytes()
            if relative == Path("README.md"):
                content = readme.encode("utf-8")
            elif path.suffix == ".md" and str(relative) not in snapshot_names:
                content = portable_markdown(
                    content.decode("utf-8"), path, relative, mapping, pdf_names
                ).encode("utf-8")
            write_zip_member(archive, str(relative), content, (2026, 10, 26, 0, 0, 0))


def publish_edition(catalog: dict, stage: Path, output: Path) -> None:
    """Publish a complete build and retain obsolete managed PDFs outside the active edition."""
    active = {paper["slug"] for paper in catalog["papers"]}
    obsolete = set(source_registry(catalog)) - active
    retired = output / "retired" / catalog["edition_date"]
    for slug in sorted(obsolete):
        old = output / f"{slug}.pdf"
        if not old.is_file():
            continue
        retired.mkdir(parents=True, exist_ok=True)
        target = retired / old.name
        if target.exists():
            digest = hashlib.sha256(old.read_bytes()).hexdigest()[:12]
            target = retired / f"{slug}-{digest}.pdf"
        if target.exists():
            if target.read_bytes() != old.read_bytes():
                raise ValueError(f"Retirement target collision: {target}")
            old.unlink()
        else:
            shutil.move(old, target)
    # The summary is the completion marker and is published last.
    for path in sorted(
        stage.iterdir(), key=lambda path: (path.name == "build-summary.json", path.name)
    ):
        if path.name == ".DS_Store":
            path.unlink()
            continue
        path.replace(output / path.name)
    stage.rmdir()


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current_pdfs(catalog: dict) -> list[Path]:
    """Return the proofs of the completed edition; raise ValueError naming what is stale."""
    output = ROOT / "output/pdf"
    summary = json.loads((output / "build-summary.json").read_text(encoding="utf-8"))
    if summary.get("manifest_sha256") != sha256_of(HERE / "manifest.json"):
        raise ValueError("manifest changed since the build")
    records = {paper["slug"]: paper for paper in summary["papers"]}
    if len(records) != len(summary["papers"]) or set(records) != {
        paper["slug"] for paper in catalog["papers"]
    }:
        raise ValueError("paper list differs from the manifest")
    paths = []
    for paper in catalog["papers"]:
        name = f"{paper['slug']}.pdf"
        record = records[paper["slug"]]
        if record["file"] != name or record["analysis_ids"] != paper["analysis_ids"]:
            raise ValueError(f"{name}: record differs from the manifest")
        if record.get("source_sha256") != source_hashes(paper, HERE):
            raise ValueError(f"{name}: sources changed since the build")
        if sha256_of(output / name) != summary["sha256"][name]:
            raise ValueError(f"{name}: file differs from the build")
        paths.append(output / name)
    return paths


def check_built(catalog: dict) -> None:
    """When a finished build exists, require it to match the current sources."""
    output = ROOT / "output/pdf"
    if not (output / "build-summary.json").is_file():
        print("No output/pdf build summary; skipped built-artifact check.")
        return
    # Imported here because the arXiv packager imports this module's helpers.
    from prepare_arxiv import paper_stem

    try:
        current_pdfs(catalog)
        summary = json.loads((output / "build-summary.json").read_text(encoding="utf-8"))
        for name, expected in summary["sha256"].items():
            if sha256_of(output / name) != expected:
                raise ValueError(f"{name}: file differs from the build")
        for paper in summary["papers"]:
            stem = paper_stem(next(p for p in catalog["papers"] if p["slug"] == paper["slug"]))
            for path, key in (
                (ROOT / "arxiv" / paper["slug"] / f"{stem}.pdf", "arxiv_pdf_sha256"),
                (ROOT / "output/arxiv" / f"{stem}.zip", "arxiv_source_zip_sha256"),
            ):
                if sha256_of(path) != paper[key]:
                    raise ValueError(f"{path.relative_to(ROOT)}: differs from the build")
    except ValueError as error:
        raise ValueError(f"output/pdf is stale: {error}; run make papers") from error
    except (OSError, KeyError, TypeError, StopIteration) as error:
        raise ValueError(f"output/pdf is incomplete or unreadable ({error!r})") from error
    print("Built papers and archives match the current sources.")


def prepared_papers(papers: list[dict]) -> dict[str, dict]:
    """Reuse verified standalone proofs, rebuilding only missing or stale packages."""
    # Import here because the arXiv packager reuses our log and page-count helpers.
    from prepare_arxiv import check_paper, source_files

    for paper in papers:
        files, keys = source_files(paper)
        try:
            check_paper(paper, files, keys)
        except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
            print(f"Preparing {paper['slug']}: {error}", flush=True)
            print(
                run(
                    [sys.executable, str(HERE / "prepare_arxiv.py"), "--only", paper["slug"]],
                    cwd=HERE,
                ),
                end="",
            )
            check_paper(paper, files, keys)
    report = json.loads((ROOT / "output/arxiv/build-summary.json").read_text(encoding="utf-8"))
    return {paper["slug"]: paper for paper in report["papers"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check sources without building PDFs")
    parser.add_argument("--only", help="Build one canonical paper or resolve a former analysis ID")
    parser.add_argument("--output", type=Path, default=ROOT / "output" / "pdf")
    args = parser.parse_args()
    catalog = load_manifest(HERE / "manifest.json")
    papers = catalog["papers"]
    prepare(check=True)
    prepare_drafts(check=True)
    check_sources(papers, catalog)
    if args.check:
        check_built(catalog)
        return 0
    for program in ("latexmk", "pdflatex", "bibtex", "pdfinfo"):
        if shutil.which(program) is None:
            raise RuntimeError(f"Missing required program: {program}")
    active = {paper["slug"] for paper in papers}
    selected = args.only
    if selected and selected not in active:
        selected = source_owners(catalog).get(selected)
        if selected is None:
            raise ValueError(f"Unknown paper or analysis ID: {args.only}")
        print(f"{args.only} is included in {selected}; building the canonical paper.")
    chosen = [paper for paper in papers if not selected or paper["slug"] == selected]
    prepared = prepared_papers(chosen)
    output = args.output.resolve()
    build_dir = output / ".build"
    build_dir.mkdir(parents=True, exist_ok=True)
    # A fresh stage per run, so nothing under a user-chosen --output is ever deleted;
    # a failed run removes only the mkdtemp directory it created itself.
    stage = None if args.only else Path(tempfile.mkdtemp(dir=build_dir, prefix="edition-stage-"))
    try:
        assemble(args, catalog, chosen, prepared, output, stage)
    except BaseException:
        if stage is not None and stage.is_dir():
            shutil.rmtree(stage)
        raise
    return 0


def assemble(
    args: argparse.Namespace,
    catalog: dict,
    chosen: list[dict],
    prepared: dict[str, dict],
    output: Path,
    stage: Path | None,
) -> None:
    """Copy verified proofs; for a full edition, also build and publish the collection."""
    papers = catalog["papers"]
    destination = output if stage is None else stage
    paths = []
    counts = []
    for paper in chosen:
        source_pdf = ROOT / local_path(prepared[paper["slug"]]["pdf"])
        count = pages_in(source_pdf)
        limit = paper.get("page_limit")
        if limit is not None and count > limit:
            raise ValueError(
                f"{paper['slug']}: {count} pages exceeds the declared limit of {limit}"
            )
        final = destination / f"{paper['slug']}.pdf"
        shutil.copyfile(source_pdf, final)
        paths.append(final)
        counts.append(count)
        print(f"Verified {final.name}: {counts[-1]} pages", flush=True)
    if not args.only:
        print(
            run(
                [sys.executable, str(HERE / "build_retrospective.py"), "--output", str(stage)],
                cwd=HERE,
            ),
            end="",
        )
        retrospective = json.loads(
            (stage / "retrospective-build-summary.json").read_text(encoding="utf-8")
        )
        collected = stage / f"{catalog['edition_date'][:7]}_curious-signals-retrospective.pdf"
        source_archive(stage / "curious-signals-latex-sources.zip")
        with zipfile.ZipFile(
            stage / "curious-signals-individual-papers.zip",
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as archive:
            for paper, path in zip(papers, paths, strict=True):
                name = prepared[paper["slug"]]["stem"] + ".pdf"
                write_zip_member(archive, name, path.read_bytes(), (2026, 10, 27, 0, 0, 0))
        report = {
            "edition_date": catalog["edition_date"],
            "manifest_sha256": hashlib.sha256((HERE / "manifest.json").read_bytes()).hexdigest(),
            "papers": [
                {
                    "slug": paper["slug"],
                    "file": path.name,
                    "pages": count,
                    "analysis_ids": paper["analysis_ids"],
                    "source_sha256": source_hashes(paper, HERE),
                    "arxiv_pdf_sha256": prepared[paper["slug"]]["pdf_sha256"],
                    "arxiv_source_zip_sha256": prepared[paper["slug"]]["zip_sha256"],
                }
                for paper, path, count in zip(papers, paths, counts, strict=True)
            ],
            "collection": {
                "file": collected.name,
                "pages": pages_in(collected),
                "pagination_report": "retrospective-build-summary.json",
                "retrospective_edition_date": retrospective["edition_date"],
            },
            "analysis_source_count": len(catalog["analysis_sources"]),
            "sha256": {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(stage.iterdir())
                if path.is_file() and path.name != ".DS_Store"
            },
        }
        (stage / "build-summary.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        publish_edition(catalog, stage, output)
        print(
            f"Collected {len(paths)} canonical papers: {report['collection']['pages']} pages. "
            "Source and PDF ZIPs ready."
        )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError) as error:
        print(f"papers: {error}", file=sys.stderr)
        raise SystemExit(1) from error
