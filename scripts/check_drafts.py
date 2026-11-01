#!/usr/bin/env python3
"""Check draft coverage, XML references, acquisition contracts, and numerical fixtures."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from defusedxml import ElementTree as ET  # noqa: E402

from curious_signals.phyphox_xml import _data_errors  # noqa: E402


def inside(root: Path, name: str, folder: str) -> Path:
    """Resolve a manifest path while rejecting absolute paths and traversal."""
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe manifest path: {name}")
    path = root / relative
    if not path.resolve().is_relative_to((root / folder).resolve()) or not path.is_file():
        raise ValueError(f"Missing or misplaced manifest artifact: {name}")
    return path


def check_xml(path: Path, entry: dict, contract: dict) -> list[str]:
    root = ET.parse(path).getroot()
    if root.tag != "phyphox" or not root.get("version"):
        return [f"{path.name}: missing phyphox root or format version"]
    errors = _data_errors(str(path), root)
    # Manual observation tools validly omit input; the core root check requires it.
    for section in ("title", "category", "description", "data-containers", "analysis", "views"):
        if root.find(section) is None:
            errors.append(f"{path.name}: missing {section}")
    if root.get("locale") != "en" or not root.findtext("title", "").startswith("Draft: "):
        errors.append(f"{path.name}: English root and Draft title required")
    if root.findtext("category") != "Curious Signals drafts":
        errors.append(f"{path.name}: incorrect draft category")
    if not root.findall("./export/set/data"):
        errors.append(f"{path.name}: no exported measurements")
    if not root.findall("./views/view/info"):
        errors.append(f"{path.name}: missing setup information")
    inputs = root.find("input")
    if entry["acquisition"] == "manual":
        if inputs is not None and len(inputs):
            errors.append(f"{path.name}: manual metadata contradicts automatic input")
        if not root.findall("./views/view/button"):
            errors.append(f"{path.name}: manual observations have no capture button")
    else:
        if inputs is None or not len(inputs):
            errors.append(f"{path.name}: live metadata has no input")
        analysis = root.find("analysis")
        if analysis is not None and analysis.get("onUserInput", "false") == "true":
            errors.append(f"{path.name}: live analysis cannot run only on user input")
    for button in root.findall("./views/view/button"):
        source, target = button.findall("input"), button.findall("output")
        if len(source) != len(target):
            errors.append(f"{path.name}: unmatched button transfers")
        for output in target:
            if output.get("clear") == "false" or output.get("append") == "true":
                errors.append(f"{path.name}: native buttons replace buffers; append is ineffective")
    # Existing Nano packet/mode facts remain normative for every draft adapter.
    bluetooth = contract["bluetooth"]
    data_char = bluetooth["data_char_uuid"].lower()
    config_char = bluetooth["config_char_uuid"].lower()
    for source in root.findall("./input/bluetooth"):
        data = [n for n in source.findall("output") if n.get("char", "").lower() == data_char]
        # Recognise the Nano by name too: a mistyped data UUID must not skip these checks.
        if source.get("name") != contract["device"]["name"] and not data:
            continue
        if not data:
            errors.append(
                f"{path.name}: Nano source does not read the contract data characteristic"
            )
            continue
        if source.get("name") != contract["device"]["name"] or not source.get("id"):
            errors.append(f"{path.name}: Nano needs the contract device name and id")
        if not any(n.get("extra") == "time" for n in data):
            errors.append(f"{path.name}: Nano receive timestamps missing")
        decoded = [n for n in data if n.get("extra") != "time"]
        offsets = [int(n.get("offset", "-1")) for n in decoded]
        if 0 not in offsets or any(o not in {0, 4, 8, 12, 16} for o in offsets):
            errors.append(f"{path.name}: Nano device time or packet offsets incorrect")
        if any(n.get("conversion") != "float32LittleEndian" for n in decoded):
            errors.append(f"{path.name}: incorrect Nano packet conversion")
        blocks = [b for b in root.findall("./output/bluetooth") if b.get("id") == source.get("id")]
        configs = [n for b in blocks for n in b.findall("config")]
        modes = [n for n in configs if n.get("char", "").lower() == config_char]
        if len(modes) != 1 or modes[0].get("conversion") != "float32LittleEndian":
            errors.append(f"{path.name}: missing matching Nano mode configuration")
        elif float(modes[0].text or "nan") not in {1, 2, 3, 4, 5, 6, 9}:
            errors.append(f"{path.name}: invalid or reserved Nano mode")
    return errors


def check(root: Path, *, fixtures: bool = True) -> dict:
    catalog = json.loads((root / "docs/drafts/manifest.json").read_text(encoding="utf-8"))
    entries = catalog["experiments"]
    if catalog.get("schema_version") != 1 or not entries:
        raise ValueError("Invalid or empty draft manifest")
    ids = [entry["id"] for entry in entries]
    if len(ids) != len(set(ids)) or any(
        not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", x) for x in ids
    ):
        raise ValueError("Duplicate or invalid draft id")
    contract = json.loads((root / "protocol/contract.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    covered = set()
    manuscripts = set()
    for entry in entries:
        if entry["acquisition"] not in {"live", "manual", "adapter"}:
            raise ValueError(f"Unknown acquisition type: {entry['id']}")
        if not all(entry.get(key) for key in ("title", "hardware", "sources", "limitations")):
            raise ValueError(f"Incomplete draft metadata: {entry['id']}")
        path = inside(root, entry["experiment"], "experiments/drafts")
        if path.name != entry["id"] + ".phyphox":
            raise ValueError(f"Draft id and filename disagree: {entry['id']}")
        manuscript = inside(root, entry["manuscript"], "docs/drafts")
        text = manuscript.read_text(encoding="utf-8")
        if not text.startswith("# ") or "draft" not in text.lower():
            errors.append(f"{manuscript.name}: missing title or draft status")
        covered.add(path.resolve())
        manuscripts.add(manuscript.resolve())
        errors.extend(check_xml(path, entry, contract))
    actual = {p.resolve() for p in (root / "experiments/drafts").rglob("*.phyphox")}
    if covered != actual:
        errors.append(f"Draft experiment coverage mismatch: {sorted(map(str, actual ^ covered))}")
    established = {
        p.resolve()
        for folder in (root / "experiments", root / "experiments/astronomy")
        for p in folder.glob("*.phyphox")
    }
    all_experiments = {p.resolve() for p in (root / "experiments").rglob("*.phyphox")}
    if all_experiments != established | covered:
        errors.append("Unregistered experiment outside established and draft collections")
    if errors:
        raise ValueError("\n".join(errors))
    if fixtures:
        for name in catalog["fixture_scripts"]:
            path = inside(root, name, "scripts")
            spec = importlib.util.spec_from_file_location(path.stem, path)
            if spec is None or spec.loader is None:
                raise ValueError(f"Cannot load fixture: {name}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.check(root)
    print(f"Checked {len(entries)} draft experiments and {len(manuscripts)} companion manuscripts.")
    return catalog


def check_schemas(root: Path, catalog: dict, rng: Path, sch: Path) -> None:
    # Optional full format validation, using explicitly selected pinned schemas.
    from lxml import etree, isoschematron

    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    relax = etree.RelaxNG(etree.parse(str(rng), parser))
    schematron = isoschematron.Schematron(etree.parse(str(sch), parser), store_report=True)
    for entry in catalog["experiments"]:
        path = root / entry["experiment"]
        document = etree.parse(str(path), parser)
        if not relax.validate(document):
            raise ValueError(f"{path.name}: Relax NG: {relax.error_log}")
        if not schematron.validate(document):
            findings = schematron.validation_report.xpath(
                "//s:failed-assert/s:text/text()",
                namespaces={"s": "http://purl.oclc.org/dsdl/svrl"},
            )
            raise ValueError(f"{path.name}: Schematron: {findings}")
    print(f"Both official schema checks passed for {len(catalog['experiments'])} drafts.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--rng", type=Path)
    parser.add_argument("--sch", type=Path)
    args = parser.parse_args()
    if bool(args.rng) != bool(args.sch):
        parser.error("Pass both --rng and --sch for full schema validation")
    try:
        catalog = check(args.root)
        if args.rng:
            check_schemas(args.root, catalog, args.rng, args.sch)
    except (ValueError, OSError, AssertionError) as error:
        print(f"Draft validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
