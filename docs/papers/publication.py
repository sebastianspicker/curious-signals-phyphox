"""Resolve publication metadata without changing the underlying analysis IDs."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


def load_manifest(path: Path) -> dict:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if catalog.get("schema_version") != 2:
        raise ValueError("The paper manifest must use schema_version 2")
    for key in ("analysis_sources", "papers"):
        entries = catalog.get(key)
        if not isinstance(entries, list) or not entries:
            raise ValueError(f"The paper manifest needs a nonempty {key} list")
        slugs = [entry.get("slug", "") for entry in entries]
        if any(not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) for slug in slugs):
            raise ValueError(f"Invalid {key} slug")
        if len(slugs) != len(set(slugs)):
            raise ValueError(f"Duplicate {key} slug")
    sources = source_registry(catalog)
    owners = {}
    for paper in catalog["papers"]:
        for field in ("title", "short_title", "group", "markdown", "period"):
            if not isinstance(paper.get(field), str) or not paper[field]:
                raise ValueError(f"{paper['slug']}: missing publication field {field}")
        if paper["markdown"] != f"companions/{paper['slug']}.md":
            raise ValueError(f"{paper['slug']}: Markdown path must match the canonical slug")
        period = re.fullmatch(
            r"(January|February|March|April|May|June|July|August|September|October|"
            r"November|December) "
            r"([0-9]{4})",
            paper["period"],
        )
        work_period = catalog.get("work_period", {})
        start, end = work_period.get("start", 1), work_period.get("end", 9999)
        if period is None or not start <= int(period.group(2)) <= end:
            raise ValueError(f"{paper['slug']}: period must be a month within the work period")
        limit = paper.get("page_limit")
        if "page_limit" in paper and (type(limit) is not int or limit <= 0):
            raise ValueError(f"{paper['slug']}: page_limit must be a positive integer")
        ids = paper.get("analysis_ids")
        if not isinstance(ids, list) or not ids:
            raise ValueError(f"{paper['slug']}: analysis_ids must be nonempty")
        for source_id in ids:
            if not isinstance(source_id, str) or source_id not in sources:
                raise ValueError(f"{paper['slug']}: unknown analysis ID {source_id}")
            if source_id in owners:
                raise ValueError(f"Analysis ID assigned more than once: {source_id}")
            owners[source_id] = paper["slug"]
    for paper in catalog["papers"]:
        if paper["slug"] in sources and owners.get(paper["slug"]) != paper["slug"]:
            raise ValueError(f"Canonical slug conflicts with another source owner: {paper['slug']}")
    missing = sources.keys() - owners.keys()
    if missing:
        raise ValueError(f"Unassigned analysis IDs: {sorted(missing)}")
    return catalog


def source_registry(catalog: dict) -> dict[str, dict]:
    return {source["slug"]: source for source in catalog["analysis_sources"]}


def source_owners(catalog: dict) -> dict[str, str]:
    return {
        source_id: paper["slug"]
        for paper in catalog["papers"]
        for source_id in paper["analysis_ids"]
    }


def paper_sources(paper: dict, catalog: dict) -> list[dict]:
    sources = source_registry(catalog)
    return [sources[source_id] for source_id in paper["analysis_ids"]]


def paper_experiments(paper: dict, catalog: dict) -> list[str]:
    return list(dict.fromkeys(source["experiment"] for source in paper_sources(paper, catalog)))


def source_hashes(paper: dict, here: Path) -> dict[str, str]:
    """Bind a proof to its manuscript and the edition's numerical reproduction sources."""
    pending = {
        f"{paper['slug']}.tex",
        f"content/{paper['slug']}.tex",
        paper["markdown"],
        "common.tex",
        "references.bib",
        "example-analysis.json",
        "draft-analysis.json",
        "revision-analysis.json",
        "prepare_examples.py",
        "prepare_drafts.py",
        "prepare_arxiv.py",
        *paper["figures"],
    }
    pending.update(path.relative_to(here).as_posix() for path in (here / "analysis").rglob("*.py"))
    hashes = {}
    while pending:
        name = min(pending)
        pending.remove(name)
        if name in hashes:
            continue
        relative = local_path(name)
        content = (here / relative).read_bytes()
        hashes[name] = hashlib.sha256(content).hexdigest()
        if relative.suffix == ".tex":
            text = content.decode("utf-8")
            for target in re.findall(r"\\(?:input|include)\{([^}]+)\}", text):
                pending.add(target if target.endswith(".tex") else target + ".tex")
            pending.update(re.findall(r"\{(data/[^{}]+\.csv)\}", text))
    catalog = load_manifest(here / "manifest.json")
    root = here.parents[1] if here.parent.name == "docs" else here
    data_root = here / "example-data" if (here / "example-data").is_dir() else root / "example-data"
    for source in paper_sources(paper, catalog):
        for name in source["datasets"] + source.get("related_datasets", []):
            content = (data_root / local_path(name)).read_bytes()
            hashes[f"example-data/{name}"] = hashlib.sha256(content).hexdigest()
    return dict(sorted(hashes.items()))


def local_path(name: str, *, folder: str | None = None) -> Path:
    """Validate a portable relative manifest path before opening or archiving it."""
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError(f"Unsafe manifest path: {name}")
    if folder is not None and relative.parts[0] != folder:
        raise ValueError(f"Expected path under {folder}: {name}")
    return relative
