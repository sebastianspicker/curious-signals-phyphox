#!/usr/bin/env python3
"""Assemble verified arXiv proofs into a continuously numbered retrospective.

Scientific pages are copied as PDF objects. Only their local header numerals
are removed and replaced; links are recreated with resolved global targets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from pathlib import Path

try:
    import pymupdf as pdf
except ImportError as error:
    raise SystemExit(
        "Install the papers extra or PyMuPDF>=1.28.2,<2 to build this volume"
    ) from error

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] if HERE.parent.name == "docs" else HERE
MANIFEST = HERE / "manifest.json"
ARXIV_REPORT = ROOT / "output/arxiv/build-summary.json"
TEMPLATE = HERE / "collection.tex"
GENERATOR = Path(__file__).resolve()
TITLE = "Curious Signals: Measurements and Laboratory Models"
ALIAS = "curious-signals-research-companions.pdf"
SUMMARY = "retrospective-build-summary.json"
NUMBER_FONT = "lmroman8-regular.otf"
TEX_ENV_VARS = ("TEXINPUTS", "BIBINPUTS", "BSTINPUTS", "TEXMFHOME", "TEXMFOUTPUT")
RESOLUTION = 2


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def input_path(name: str) -> Path:
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"Unsafe input path: {name}")
    result = ROOT / path
    if not result.is_file() or not result.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError(f"Missing or external input: {name}")
    return result


def run(command: list[str], cwd: Path) -> str:
    # Do not let a developer's search path hide a missing package input. This script
    # ships alone in the source ZIP, so it cannot import build.tex_env.
    env = {k: v for k, v in os.environ.items() if k not in TEX_ENV_VARS}
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n"
            + result.stdout[-10000:]
            + result.stderr[-4000:]
        )
    return result.stdout


def load_inputs() -> tuple[dict, list[dict], dict[str, str]]:
    manifest, arxiv = read_json(MANIFEST), read_json(ARXIV_REPORT)
    papers = manifest.get("papers", [])
    records = arxiv.get("papers", [])
    if not papers or [item["slug"] for item in papers] != [item["slug"] for item in records]:
        raise ValueError("arXiv proofs do not match the canonical paper order and membership")
    inputs = {
        relative(path): sha(path.read_bytes())
        for path in (
            MANIFEST,
            ARXIV_REPORT,
            TEMPLATE,
            GENERATOR,
            ROOT / "LICENSE",
            ROOT / "COPYING.LESSER",
        )
    }
    result = []
    for paper, record in zip(papers, records, strict=True):
        slug = paper["slug"]
        if any(record.get(key) != paper[key] for key in ("title", "period")):
            raise ValueError(f"{slug}: title/date mismatch between canonical and arXiv records")
        folder = ROOT / "arxiv" / slug
        expected = set(record["source_sha256"]) | {Path(record["pdf"]).name}
        actual = {
            path.relative_to(folder).as_posix()
            for path in folder.rglob("*")
            if path.is_file() and path.name != ".DS_Store"
        }
        if actual != expected:
            raise ValueError(f"{slug}: arXiv folder contains missing or unexpected files")
        for name, expected_hash in record["source_sha256"].items():
            path = input_path(f"arxiv/{slug}/{name}")
            if sha(path.read_bytes()) != expected_hash:
                raise ValueError(f"{slug}: arXiv source changed: {name}")
            inputs[relative(path)] = expected_hash
        for field, hash_field in (("pdf", "pdf_sha256"), ("source_zip", "zip_sha256")):
            path = input_path(record[field])
            if sha(path.read_bytes()) != record[hash_field]:
                raise ValueError(f"{slug}: {field} differs from verified arXiv proof")
            inputs[relative(path)] = record[hash_field]
        with zipfile.ZipFile(ROOT / record["source_zip"]) as archive:
            if (
                len(archive.namelist()) != len(record["source_sha256"])
                or {name: sha(archive.read(name)) for name in archive.namelist()}
                != record["source_sha256"]
            ):
                raise ValueError(f"{slug}: upload ZIP does not contain the verified sources")
        with pdf.open(ROOT / record["pdf"]) as document:
            if len(document) != record["pages"]:
                raise ValueError(f"{slug}: PDF page count differs from arXiv record")
            if document.metadata.get("title") != paper["title"]:
                raise ValueError(f"{slug}: PDF title differs from canonical title")
            for page in document:
                if page.rotation or list(page.annots() or []) or list(page.widgets() or []):
                    raise ValueError(f"{slug}: rotated pages, annotations or widgets need review")
        result.append(
            {
                **paper,
                "proof": record["pdf"],
                "pages": record["pages"],
                "source_pdf_sha256": record["pdf_sha256"],
            }
        )
    return manifest, result, dict(sorted(inputs.items()))


def tex(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def page_ranges(papers: list[dict], front_pages: int) -> list[dict]:
    first = front_pages + 1
    result = []
    for paper in papers:
        last = first + paper["pages"] - 1
        result.append({**paper, "first_page": first, "last_page": last})
        first = last + 1
    return result


def front_source(papers: list[dict], front_pages: int) -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    groups = list(dict.fromkeys(paper["group"] for paper in papers))
    if len(groups) != 4:
        raise ValueError("The retrospective contents layout expects four canonical topic groups")
    halves: list[list[str]] = [[], []]
    previous = None
    definitions = []
    for paper in page_ranges(papers, front_pages):
        slug, group = paper["slug"], paper["group"]
        half = halves[0 if group in groups[:2] else 1]
        if group != previous:
            half.append(r"\multicolumn{3}{@{}l}{\contentsgroup{" + tex(group) + r"}}\\[0.65em]")
        half.append(
            r"\paperlink{"
            + slug
            + "}{"
            + tex(paper["title"])
            + "} & "
            + tex(paper["period"])
            + r" & \paperpages{"
            + slug
            + r"}\\"
        )
        previous = group
        definitions.append(
            r"\expandafter\def\csname paperpages@"
            + slug
            + r"\endcsname{"
            + f"{paper['first_page']}--{paper['last_page']}"
            + "}"
        )
    replacements = {
        "% PAPER_COUNT": str(len(papers)),
        "% BODY_PAGE_COUNT": str(sum(paper["pages"] for paper in papers)),
        "% PAPER_PAGE_DEFINITIONS": "\n".join(definitions),
        "% CONTENTS_ROWS_1": "\n".join(halves[0]),
        "% CONTENTS_ROWS_2": "\n".join(halves[1]),
    }
    for marker, value in replacements.items():
        if marker not in template:
            raise ValueError(f"Frontmatter template is missing {marker}")
        template = template.replace(marker, value)
    return template


def compile_front(papers: list[dict], work: Path) -> tuple[Path, str, int]:
    count = 5
    for _ in range(5):
        source = front_source(papers, count)
        (work / "frontmatter.tex").write_text(source, encoding="utf-8")
        for _ in range(3):
            run(
                [
                    "pdflatex",
                    "-no-shell-escape",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "-file-line-error",
                    "frontmatter.tex",
                ],
                work,
            )
        log = (work / "frontmatter.log").read_text(encoding="utf-8", errors="replace")
        problems = [
            line
            for line in log.splitlines()
            if any(
                term in line
                for term in (
                    "Overfull ",
                    "undefined references",
                    "multiply-defined labels",
                    "Missing character:",
                    "Float too large",
                    "Citation `",
                )
            )
        ]
        if problems:
            raise ValueError("Frontmatter typesetting diagnostics:\n" + "\n".join(problems))
        path = work / "frontmatter.pdf"
        with pdf.open(path) as document:
            actual = len(document)
        if actual == count:
            return path, source, count
        count = actual
    raise ValueError("Frontmatter page count failed to converge")


def header_numerals(page: pdf.Page) -> list[dict]:
    return [
        span
        for block in page.get_text("dict")["blocks"]
        if block["type"] == 0
        for line in block["lines"]
        for span in line["spans"]
        if span["text"].strip().isdigit()
        and span["bbox"][0] > page.rect.width - 140
        and 40 < span["bbox"][1] < 100
    ]


def replace_number(
    page: pdf.Page, local: int, global_number: int, font: pdf.Font, font_path: Path
) -> dict:
    candidates = header_numerals(page)
    if len(candidates) != 1 or candidates[0]["text"] != str(local):
        raise ValueError(f"Expected one local header number {local}, found {candidates}")
    span = candidates[0]
    original = pdf.Rect(span["bbox"])
    # MuPDF's text-only redaction can round unrelated vector coordinates while
    # filtering a page. Retain the original scientific stream and resources,
    # restoring them after redaction with only the verified header text show
    # removed. The supported TeX header has two TJ operators: title, then number.
    content = page.read_contents()
    number = rb"[-0-9.]+"
    header = re.match(
        rb"\s*0 g 0 G\s+BT\s+/\S+\s+"
        + number
        + rb"\s+Tf\s+"
        + number
        + rb"\s+"
        + number
        + rb"\s+Td\s+\[[^\]]*\]TJ\s+"
        + number
        + rb"\s+"
        + number
        + rb"\s+Td\s+"
        + rb"(?P<numeral>\[\("
        + str(local).encode("ascii")
        + rb"\)\]TJ)",
        content,
    )
    if header is None:
        raise ValueError("Unsupported PDF header stream; cannot safely preserve scientific content")
    start, end = header.span("numeral")
    preserved = content[:start] + b"[]TJ" + content[end:]
    resource_type, resource_value = page.parent.xref_get_key(page.xref, "Resources")
    resource_xref = int(resource_value.split()[0]) if resource_type == "xref" else None
    resource_object = page.parent.xref_object(resource_xref) if resource_xref else None
    redaction = original + (-0.1, -0.1, 0.1, 0.1)
    page.add_redact_annot(redaction, fill=False)
    page.apply_redactions(images=0, graphics=0, text=0)
    if resource_xref is not None:
        page.parent.update_object(resource_xref, resource_object)
    page.parent.xref_set_key(page.xref, "Resources", resource_value)
    stream_xref = page.parent.get_new_xref()
    page.parent.update_object(stream_xref, "<<>>")
    page.parent.update_stream(stream_xref, preserved)
    page.set_contents(stream_xref)
    page.insert_font(fontname="CSGlobal", fontfile=str(font_path))
    value = str(global_number)
    width = font.text_length(value, fontsize=span["size"])
    point = (original.x1 - width, span["origin"][1])
    page.insert_text(point, value, fontname="CSGlobal", fontsize=span["size"], color=(0, 0, 0))
    inserted = header_numerals(page)
    if len(inserted) != 1 or inserted[0]["text"] != value:
        raise ValueError(f"Global header number {global_number} did not replace the local number")
    changed = original | pdf.Rect(inserted[0]["bbox"])
    changed += (-0.6, -0.6, 0.6, 0.6)
    return {
        "local_page": local,
        "global_page": global_number,
        "old_number_rect": list(original),
        "number_rect": list(changed),
        "baseline": span["origin"][1],
        "font_size": span["size"],
    }


def resolve_links(
    page: pdf.Page, offset: int, page_count: int, targets: dict[str, int] | None = None
) -> list[dict]:
    links = []
    for link in page.get_links():
        rect = [float(value) for value in link["from"]]
        if link["kind"] == pdf.LINK_URI:
            uri = link["uri"]
            if uri.startswith("cs-paper:"):
                slug = uri.removeprefix("cs-paper:")
                if targets is None or slug not in targets:
                    raise ValueError(f"Unknown retrospective link: {uri}")
                links.append(
                    {
                        "kind": "goto",
                        "rect": rect,
                        "page": targets[slug] - 1,
                        "point": [0.0, 0.0],
                        "zoom": 0.0,
                        "paper_slug": slug,
                    }
                )
            else:
                links.append({"kind": "uri", "rect": rect, "uri": uri})
        elif (
            link["kind"] in {pdf.LINK_GOTO, pdf.LINK_NAMED}
            and isinstance(link.get("page"), int)
            and 0 <= link["page"] < page_count
            and "to" in link
        ):
            links.append(
                {
                    "kind": "goto",
                    "rect": rect,
                    "page": offset + link["page"],
                    "point": [float(value) for value in link["to"]],
                    "zoom": float(link.get("zoom", 0)),
                }
            )
        else:
            raise ValueError(f"Unsupported or unresolved PDF link: {link}")
    return links


def insert_links(page: pdf.Page, links: list[dict]) -> None:
    for link in links:
        value = {
            "kind": pdf.LINK_URI if link["kind"] == "uri" else pdf.LINK_GOTO,
            "from": pdf.Rect(link["rect"]),
        }
        if link["kind"] == "uri":
            value["uri"] = link["uri"]
        else:
            value.update(page=link["page"], to=pdf.Point(link["point"]), zoom=link["zoom"])
        page.insert_link(value)


def normal_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).replace("’", "'").replace("–", "-")
    return re.sub(r"\s+", "", text)


def outline(front: pdf.Document, papers: list[dict]) -> tuple[list[list], int]:
    contents = [
        index + 1
        for index, page in enumerate(front)
        if re.search(r"(?m)^Contents$", page.get_text())
    ]
    if not contents:
        raise ValueError("Frontmatter has no identifiable contents page")

    def entry(
        level: int,
        title: str,
        page_number: int,
        point: tuple[float, float] | list[float] = (0.0, 0.0),
        zoom: float = 0.0,
    ) -> list:
        return [
            level,
            title,
            page_number,
            {"kind": pdf.LINK_GOTO, "page": page_number - 1, "to": list(point), "zoom": zoom},
        ]

    result = [
        entry(1, "Cover", 1),
        entry(1, "Retrospective overview", 2),
        entry(1, "Contents", contents[0]),
    ]
    group = None
    for paper in papers:
        if paper["group"] != group:
            result.append(entry(1, paper["group"], paper["first_page"]))
            group = paper["group"]
        result.append(entry(2, paper["title"], paper["first_page"]))
        with pdf.open(ROOT / paper["proof"]) as document:
            for level, title, page_number, destination in document.get_toc(simple=False):
                if (
                    not 1 <= page_number <= len(document)
                    or destination.get("kind") not in {pdf.LINK_GOTO, pdf.LINK_NAMED}
                    or destination.get("page") != page_number - 1
                    or "to" not in destination
                ):
                    raise ValueError(f"{paper['slug']}: unsupported/unresolved section bookmark")
                result.append(
                    entry(
                        level + 2,
                        title,
                        paper["first_page"] + page_number - 1,
                        list(destination["to"]),
                        float(destination.get("zoom", 0)),
                    )
                )
    return result, contents[0]


def assemble(
    front_path: Path, papers: list[dict], output: Path, font_path: Path, manifest: dict
) -> dict:
    font = pdf.Font(fontfile=str(font_path))
    document = pdf.open()
    page_records = []
    expected_links = []
    targets = {paper["slug"]: paper["first_page"] for paper in papers}
    with pdf.open(front_path) as front:
        document.insert_pdf(front, links=False, annots=False, widgets=False)
        for index, page in enumerate(front):
            expected_links.append(resolve_links(page, 0, len(front), targets))
        bookmarks, contents_page = outline(front, papers)
        for paper in papers:
            with pdf.open(ROOT / paper["proof"]) as source:
                offset = len(document)
                document.insert_pdf(source, links=False, annots=False, widgets=False)
                for local, page in enumerate(source):
                    expected_links.append(resolve_links(page, offset, len(source)))
                    record = replace_number(
                        document[offset + local], local + 1, offset + local + 1, font, font_path
                    )
                    page_records.append({**record, "slug": paper["slug"]})
        for index, links in enumerate(expected_links):
            insert_links(document[index], links)
        document.set_toc(
            [item[:3] + [{**item[3], "to": pdf.Point(item[3]["to"])}] for item in bookmarks]
        )
        document.set_page_labels([{"startpage": 0, "prefix": "", "style": "D", "firstpagenum": 1}])
        date = manifest["edition_date"].replace("-", "")
        document.set_metadata(
            {
                "title": TITLE,
                "author": ", ".join(manifest["authors"]),
                "subject": "October 2026 retrospective of work from 2018 to 2024",
                "keywords": "physics education, measurement, calibration, uncertainty",
                "creator": "Curious Signals retrospective builder",
                "producer": f"PyMuPDF {pdf.VersionBind}",
                "creationDate": f"D:{date}000000Z",
                "modDate": f"D:{date}000000Z",
            }
        )
        document.del_xml_metadata()
        document.save(output, garbage=4, deflate=True)
    document.close()
    return {
        "page_number_changes": page_records,
        "expected_links": expected_links,
        "outline": bookmarks,
        "contents_first_page": contents_page,
    }


def compare_links(page: pdf.Page, expected: list[dict]) -> None:
    actual = resolve_links(page, 0, page.parent.page_count)

    def key(link: dict) -> tuple:
        return (
            link["kind"],
            link.get("uri", ""),
            link.get("page", -1),
            tuple(round(value, 1) for value in link["rect"]),
        )

    if len(actual) != len(expected):
        raise ValueError(f"Page {page.number + 1}: link count changed")
    for found, wanted in zip(sorted(actual, key=key), sorted(expected, key=key), strict=True):
        if (
            found["kind"] != wanted["kind"]
            or found.get("uri") != wanted.get("uri")
            or found.get("page") != wanted.get("page")
        ):
            raise ValueError(f"Page {page.number + 1}: link destination changed")
        for name in ("rect", "point"):
            if name in wanted and any(
                abs(left - right) > 0.02
                for left, right in zip(found[name], wanted[name], strict=True)
            ):
                raise ValueError(f"Page {page.number + 1}: link {name} changed")
        if "zoom" in wanted and abs(found["zoom"] - wanted["zoom"]) > 0.02:
            raise ValueError(f"Page {page.number + 1}: link zoom changed")


def masked_render(page: pdf.Page, number_rect: list[float]) -> str:
    pixmap = page.get_pixmap(matrix=pdf.Matrix(RESOLUTION, RESOLUTION), alpha=False, annots=False)
    rect = pdf.Rect(number_rect) * RESOLUTION
    x0, x1 = max(0, math.floor(rect.x0)), min(pixmap.width, math.ceil(rect.x1))
    y0, y1 = max(0, math.floor(rect.y0)), min(pixmap.height, math.ceil(rect.y1))
    content = memoryview(pixmap.samples)
    digest = hashlib.sha256()
    stride, channels = pixmap.stride, pixmap.n
    digest.update(f"{pixmap.width},{pixmap.height},{channels}".encode())
    for row in range(pixmap.height):
        start = row * stride
        if y0 <= row < y1:
            digest.update(content[start : start + x0 * channels])
            digest.update(content[start + x1 * channels : start + stride])
        else:
            digest.update(content[start : start + stride])
    return digest.hexdigest()


def verify_pdf(
    path: Path, papers: list[dict], front_count: int, evidence: dict, manifest: dict
) -> dict:
    with pdf.open(path) as document:
        if len(document) != front_count + sum(paper["pages"] for paper in papers):
            raise ValueError("Collected page count does not match current article lengths")
        if document.metadata.get("title") != TITLE:
            raise ValueError("Incorrect retrospective PDF title")
        if document.metadata.get("author") != ", ".join(manifest["authors"]):
            raise ValueError("Incorrect retrospective PDF authors")
        if document.get_toc() != [item[:3] for item in evidence["outline"]]:
            raise ValueError(
                "Retrospective outline does not match paper/group/section destinations"
            )
        for found, wanted in zip(document.get_toc(simple=False), evidence["outline"], strict=True):
            actual, expected = found[3], wanted[3]
            if (
                actual.get("kind") != pdf.LINK_GOTO
                or actual.get("page") != expected["page"]
                or any(
                    abs(left - right) > 0.02
                    for left, right in zip(actual["to"], expected["to"], strict=True)
                )
                or abs(float(actual.get("zoom", 0)) - expected["zoom"]) > 0.02
            ):
                raise ValueError(f"Section bookmark destination changed: {wanted[1]}")
        for index, page in enumerate(document):
            if page.get_label() != str(index + 1):
                raise ValueError(f"Page {index + 1}: viewer page label is incorrect")
            values = header_numerals(page)
            if index == 0:
                if values:
                    raise ValueError("Cover must not print a page number")
            elif len(values) != 1 or values[0]["text"] != str(index + 1):
                raise ValueError(f"Page {index + 1}: printed page number is not unique/correct")
            compare_links(page, evidence["expected_links"][index])
        front_text = normal_text(
            "\n".join(document[index].get_text() for index in range(front_count))
        )
        for paper in papers:
            page_range = f"{paper['first_page']}-{paper['last_page']}"
            # Ignore discretionary word-breaking hyphens in extracted title text.
            # The exact title spelling is also bound by the generated TeX hash.
            if normal_text(paper["title"]).replace("-", "") not in front_text.replace(
                "-", ""
            ) or any(
                normal_text(value) not in front_text for value in (paper["period"], page_range)
            ):
                raise ValueError(f"{paper['slug']}: contents title/date/range was not rendered")
            count = sum(
                1
                for links in evidence["expected_links"][
                    evidence["contents_first_page"] - 1 : front_count
                ]
                for link in links
                if link.get("paper_slug") == paper["slug"]
            )
            if count < 2:
                raise ValueError(
                    f"{paper['slug']}: contents title and page-range links are missing"
                )
        changes = {record["global_page"]: record for record in evidence["page_number_changes"]}
        render_hashes = {}
        font_xrefs = set()
        for paper in papers:
            with pdf.open(ROOT / paper["proof"]) as source:
                for local, original in enumerate(source):
                    global_page = paper["first_page"] + local
                    collected = document[global_page - 1]
                    if collected.rect != original.rect:
                        raise ValueError(f"Page {global_page}: scientific page geometry changed")
                    number_rect = changes[global_page]["number_rect"]
                    before, after = (
                        masked_render(original, number_rect),
                        masked_render(collected, number_rect),
                    )
                    if before != after:
                        raise ValueError(
                            f"Page {global_page}: rendered content changed outside header numeral"
                        )
                    render_hashes[str(global_page)] = before
                    fonts = [item for item in collected.get_fonts() if item[4] == "CSGlobal"]
                    if not fonts:
                        raise ValueError(f"Page {global_page}: global-number font is missing")
                    font_xrefs.update(item[0] for item in fonts)
        for xref in font_xrefs:
            if not document.extract_font(xref)[3]:
                raise ValueError("Global-number font was not embedded")
        return {
            "body_render_sha256_outside_number_rect": render_hashes,
            "render_dpi": RESOLUTION * 72,
            "global_number_font_embedded": True,
            "body_link_count": sum(
                len(links) for links in evidence["expected_links"][front_count:]
            ),
            "front_link_count": sum(
                len(links) for links in evidence["expected_links"][:front_count]
            ),
            "total_pages": len(document),
        }


def source_archive(path: Path, inputs: dict[str, str], script_name: str) -> None:
    readme = (
        "# Curious Signals retrospective: standalone rebuild\n\n"
        "These inputs preserve all 21 standalone arXiv proofs and their source packages.\n"
        "The builder compiles only the front matter, then assembles the scientific PDF\n"
        "pages and replaces their local header numerals in the collection copy.\n\n"
        "Requires Python 3.11+, PyMuPDF>=1.28.2,<2, pdflatex, kpsewhich, and standard\n"
        "TeX Live packages: Latin Modern, geometry, fancyhdr, booktabs, array, xcolor,\n"
        "microtype and hyperref. No scientific-paper compilation is required.\n"
        "Latin Modern is obtained from your TeX installation, not vendored here.\n\n"
        "Repository licensing applies; see LICENSE and COPYING.LESSER.\n\n"
        "From the extracted archive directory:\n\n```sh\n"
        "python3 -m pip install 'PyMuPDF>=1.28.2,<2'\n"
        f"python3 {script_name} --output output/pdf\n"
        f"python3 {script_name} --output output/pdf --check\n```\n"
    )
    members = {}
    for name, expected in inputs.items():
        content = input_path(name).read_bytes()
        if sha(content) != expected:
            raise ValueError(f"Input changed during the retrospective build: {name}")
        members[name] = content
    members["README-retrospective.md"] = readme.encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 27, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, content)
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None or {
            name: sha(archive.read(name)) for name in archive.namelist()
        } != {name: sha(content) for name, content in members.items()}:
            raise ValueError("Generated retrospective source ZIP failed verification")


def names(manifest: dict) -> tuple[str, str]:
    prefix = manifest["edition_date"][:7] + "_curious-signals-retrospective"
    return prefix + ".pdf", prefix + "-sources.zip"


def check(output: Path, manifest: dict, papers: list[dict], inputs: dict[str, str]) -> None:
    report = read_json(output / SUMMARY)
    pdf_name, archive_name = names(manifest)
    if report["edition_date"] != manifest["edition_date"]:
        raise ValueError("Retrospective edition date differs from the canonical manifest")
    body_pages = sum(paper["pages"] for paper in papers)
    if (
        report["body_pages"] != body_pages
        or report["total_pages"] != report["front_pages"] + body_pages
    ):
        raise ValueError("Retrospective report page counts do not match current proofs")
    if report["frontmatter_source_sha256"] != sha(
        front_source(papers, report["front_pages"]).encode("utf-8")
    ):
        raise ValueError("Retrospective frontmatter source/ranges changed; rebuild the volume")
    if set(report["output_sha256"]) != {pdf_name, ALIAS, archive_name}:
        raise ValueError("Retrospective report does not name the exact expected output artifacts")
    if report["input_sha256"] != inputs:
        raise ValueError("Retrospective inputs changed; rebuild the volume")
    font_path = Path(run(["kpsewhich", NUMBER_FONT], HERE).strip())
    if report["number_font_sha256"] != sha(font_path.read_bytes()):
        raise ValueError("Number font changed; rebuild the volume")
    for name, expected in report["output_sha256"].items():
        if sha((output / name).read_bytes()) != expected:
            raise ValueError(f"Retrospective artifact changed: {name}")
    if (output / pdf_name).read_bytes() != (output / ALIAS).read_bytes():
        raise ValueError("Compatibility PDF is not byte-identical to the retrospective")
    ranges = page_ranges(papers, report["front_pages"])
    expected_ranges = [
        {
            key: paper[key]
            for key in (
                "slug",
                "title",
                "period",
                "pages",
                "first_page",
                "last_page",
                "proof",
                "source_pdf_sha256",
            )
        }
        for paper in ranges
    ]
    if report["papers"] != expected_ranges:
        raise ValueError("Reported article ranges no longer match actual inputs")
    verified = verify_pdf(
        output / pdf_name, ranges, report["front_pages"], report["evidence"], manifest
    )
    if verified != report["verification"]:
        raise ValueError("Retrospective PDF semantics differ from the verified build")
    with zipfile.ZipFile(output / archive_name) as archive:
        expected_members = set(inputs) | {"README-retrospective.md"}
        if set(archive.namelist()) != expected_members or len(archive.namelist()) != len(
            expected_members
        ):
            raise ValueError("Retrospective source archive has unexpected members")
        if any(sha(archive.read(name)) != expected for name, expected in inputs.items()):
            raise ValueError("Retrospective source archive inputs do not match the verified build")
    print(
        f"Checked retrospective: {len(papers)} papers, {verified['total_pages']} continuous pages."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "output/pdf")
    parser.add_argument(
        "--check", action="store_true", help="Verify current inputs, artifacts and semantics"
    )
    args = parser.parse_args()
    manifest, papers, inputs = load_inputs()
    output = args.output.resolve()
    if args.check:
        check(output, manifest, papers, inputs)
        return 0
    for program in ("pdflatex", "kpsewhich"):
        if shutil.which(program) is None:
            raise ValueError(f"Missing required program: {program}")
    font_path = Path(run(["kpsewhich", NUMBER_FONT], HERE).strip())
    if not font_path.is_file():
        raise ValueError(f"TeX Live does not provide {NUMBER_FONT}")
    output.mkdir(parents=True, exist_ok=True)
    pdf_name, archive_name = names(manifest)
    with tempfile.TemporaryDirectory(prefix=".retrospective-stage-", dir=output) as temporary:
        stage = Path(temporary)
        front, generated_source, front_count = compile_front(papers, stage)
        ranges = page_ranges(papers, front_count)
        evidence = assemble(front, ranges, stage / pdf_name, font_path, manifest)
        verified = verify_pdf(stage / pdf_name, ranges, front_count, evidence, manifest)
        shutil.copyfile(stage / pdf_name, stage / ALIAS)
        source_archive(stage / archive_name, inputs, relative(GENERATOR))
        report = {
            "edition_date": manifest["edition_date"],
            "title": TITLE,
            "front_pages": front_count,
            "body_pages": sum(paper["pages"] for paper in papers),
            "total_pages": verified["total_pages"],
            "input_sha256": inputs,
            "number_font": NUMBER_FONT,
            "number_font_sha256": sha(font_path.read_bytes()),
            "frontmatter_source_sha256": sha(generated_source.encode("utf-8")),
            "papers": [
                {
                    key: paper[key]
                    for key in (
                        "slug",
                        "title",
                        "period",
                        "pages",
                        "first_page",
                        "last_page",
                        "proof",
                        "source_pdf_sha256",
                    )
                }
                for paper in ranges
            ],
            "evidence": evidence,
            "verification": verified,
            "output_sha256": {
                name: sha((stage / name).read_bytes()) for name in (pdf_name, ALIAS, archive_name)
            },
        }
        (stage / SUMMARY).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        for name in (pdf_name, ALIAS, archive_name, SUMMARY):
            (stage / name).replace(output / name)
    print(
        f"Built retrospective: {len(papers)} papers, {front_count} front pages, "
        f"{verified['total_pages']} continuously numbered pages."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, KeyError, zipfile.BadZipFile) as error:
        print(f"retrospective: {error}", file=sys.stderr)
        raise SystemExit(1) from error
