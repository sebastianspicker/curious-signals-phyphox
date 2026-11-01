#!/usr/bin/env python3
"""Write reproducible draft experiment and companion ZIP files after validation."""

from __future__ import annotations

import hashlib
import json
import posixpath
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

from check_drafts import ROOT, check

sys.path.insert(0, str(ROOT / "docs/papers"))

from publication import load_manifest, local_path, source_hashes  # noqa: E402


def current_pdfs(catalog: dict) -> list[Path]:
    """Include proofs only when they belong to this exact completed edition."""
    output = ROOT / "output/pdf"
    try:
        summary = json.loads((output / "build-summary.json").read_text(encoding="utf-8"))
        digest = hashlib.sha256((ROOT / "docs/papers/manifest.json").read_bytes()).hexdigest()
        if summary.get("manifest_sha256") != digest:
            return []
        records = {paper["slug"]: paper for paper in summary["papers"]}
        if len(records) != len(summary["papers"]):
            return []
        if set(records) != {paper["slug"] for paper in catalog["papers"]}:
            return []
        paths = []
        for paper in catalog["papers"]:
            name = f"{paper['slug']}.pdf"
            record = records[paper["slug"]]
            if record["file"] != name or record["analysis_ids"] != paper["analysis_ids"]:
                return []
            if record.get("source_sha256") != source_hashes(paper, ROOT / "docs/papers"):
                return []
            path = output / name
            if hashlib.sha256(path.read_bytes()).hexdigest() != summary["sha256"][name]:
                return []
            paths.append(path)
        return paths
    except (OSError, ValueError, KeyError, TypeError):
        return []


def paper_index(catalog: dict, destination: Path, *, pdfs: bool) -> bytes:
    def link(target: Path) -> str:
        return posixpath.relpath(target.as_posix(), destination.parent.as_posix())

    lines = [
        "# Curious Signals: experiment definitions and topic companions",
        "",
        "This reading bundle contains the 28 draft acquisition definitions and redirect notes,",
        f"plus {len(catalog['papers'])} canonical scientific Markdown companions.",
        "The draft status of an acquisition definition is independent of its article.",
        "",
        "The complete LaTeX and numerical sources are distributed separately as",
        "`curious-signals-latex-sources.zip`. In the repository, run `make papers` to build",
        "the PDFs, then `make bundle-drafts` to include verified current proofs here.",
        "",
        "Current PDF proofs are included."
        if pdfs
        else "Matching PDF proofs were unavailable; this bundle contains Markdown.",
        "",
        "| Topic | Companion | PDF proof |",
        "| --- | --- | --- |",
    ]
    for paper in catalog["papers"]:
        companion = Path("docs/papers") / local_path(paper["markdown"], folder="companions")
        proof = Path("output/pdf") / f"{paper['slug']}.pdf"
        pdf = f"[PDF]({link(proof)})" if pdfs else "Build from the publication sources"
        title = paper["title"].replace("|", r"\|")
        lines.append(f"| {title} | [Markdown]({link(companion)}) | {pdf} |")
    return ("\n".join(lines) + "\n").encode("utf-8")


def archive(path: Path, files: list[Path], overrides: dict[Path, bytes] | None = None) -> None:
    contents = {source.relative_to(ROOT): source.read_bytes() for source in sorted(set(files))}
    contents.update(overrides or {})
    for relative, content in list(contents.items()):
        if relative.suffix != ".md":
            continue

        def retain_available(match: re.Match) -> str:
            target = urlsplit(match.group(2).strip("<>"))
            if target.scheme or target.netloc or not target.path:
                return match.group(0)
            resolved = (ROOT / relative.parent / unquote(target.path)).resolve()
            if resolved.is_relative_to(ROOT.resolve()):
                if resolved.relative_to(ROOT.resolve()) in contents:
                    return match.group(0)
            return match.group(1)

        contents[relative] = re.sub(
            r"!?\[([^\]]+)\]\((<[^>]+>|[^)\s]+)(?:\s+\"[^\"]*\")?\)",
            retain_available,
            content.decode("utf-8"),
        ).encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for relative, content in sorted(contents.items()):
            entry = zipfile.ZipInfo(str(relative), date_time=(2026, 10, 26, 0, 0, 0))
            entry.external_attr = 0o644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            output.writestr(entry, content)


def main() -> None:
    catalog = check(ROOT)
    destination = ROOT / "output/drafts"
    destination.mkdir(parents=True, exist_ok=True)
    experiments = [ROOT / e["experiment"] for e in catalog["experiments"]]
    companions = sorted((ROOT / "docs/drafts").glob("*.md"))
    manifest = ROOT / "docs/drafts/manifest.json"
    notices = [ROOT / "LICENSE", ROOT / "COPYING.LESSER", ROOT / "docs/drafts/source-review.md"]
    archive(destination / "curious-signals-draft-experiments.zip", experiments + notices)
    publications = load_manifest(ROOT / "docs/papers/manifest.json")
    canonical = [
        ROOT / "docs/papers" / local_path(paper["markdown"], folder="companions")
        for paper in publications["papers"]
    ]
    proofs = current_pdfs(publications)
    indexes = {
        path: paper_index(publications, path, pdfs=bool(proofs))
        for path in (Path("README.md"), Path("docs/papers/README.md"))
    }
    archive(
        destination / "curious-signals-draft-collection.zip",
        experiments
        + companions
        + canonical
        + proofs
        + notices
        + [manifest, ROOT / "docs/papers/manifest.json", ROOT / "protocol/contract.json"],
        indexes,
    )
    hashes = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in experiments
    }
    (destination / "experiment-sha256.json").write_text(
        json.dumps(hashes, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Draft experiment ZIP, companion ZIP, and hashes written to {destination}")


if __name__ == "__main__":
    main()
