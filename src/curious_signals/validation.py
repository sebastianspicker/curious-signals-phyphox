"""Complete non-mutating validation of protocol, core XML, and astronomy assets."""

from __future__ import annotations

import re

from . import ToolError
from .checkout import Checkout
from .generation import render_core_experiments, source_inventory_errors, xml_safety_errors
from .phyphox_xml import check_astronomy_experiment, check_core_experiment
from .protocol import Protocol, contract_errors, parse_protocol, read_contract
from .xmllint import find_xmllint, run_xmllint


def firmware_contract_errors(sketch: str, raw: dict) -> list[str]:
    """Return contract literals the self-contained firmware sketch does not repeat."""

    # shortcut: substring match, so a literal kept only in a comment also passes;
    # parse the declarations if the sketch ever carries stale copies in comments.

    name = raw["device"]["name"]
    frame = raw["frame"]
    selection = frame["config"]["selection"]
    expected = [
        f'"{raw["bluetooth"][key]}"'
        for key in ("service_uuid", "data_char_uuid", "config_char_uuid")
    ]
    expected += [
        f'BLE.setDeviceName("{name}")',
        f'BLE.setLocalName("{name}")',
        f"kSendPeriodMs = {frame['sample_period_ms']};",
        f"kPayloadSizeBytes = {frame['data']['byte_length']};",
        f"kConfigWireSizeBytes = {frame['config']['byte_length']};",
        f"configValue < {selection['minimum']}f || "
        f"configValue >= {selection['maximum_exclusive']}f",
    ]
    errors = [
        f"firmware: missing contract literal {item}" for item in expected if item not in sketch
    ]
    enum = re.search(r"enum class Mode : int \{(.*?)\};", sketch, re.DOTALL)
    ids = {int(value) for value in re.findall(r"=\s*(\d+)", enum.group(1))} if enum else set()
    if ids != {mode["id"] for mode in raw["modes"]["active"]}:
        errors.append(f"firmware: Mode enum {sorted(ids)} differs from the contract's active modes")
    return errors


def _firmware_errors(checkout: Checkout, raw: dict, protocol: Protocol) -> list[str]:
    sketch_path = checkout.sketch_dir / f"{checkout.sketch_dir.name}.ino"
    try:
        sketch = sketch_path.read_text(encoding="utf-8")
    except OSError as error:
        return [f"{sketch_path}: cannot read firmware: {error}"]
    errors = firmware_contract_errors(sketch, raw)
    # The guard must fire on a copy without the data UUID, or it proves nothing.
    if not firmware_contract_errors(sketch.replace(protocol.data_char_uuid, ""), raw):
        errors.append("firmware contract check cannot detect a missing UUID")
    return errors


def validate(checkout: Checkout) -> list[str]:
    """Run the local contract, XML safety, core, astronomy, and rendering checks."""

    try:
        raw = read_contract(checkout.contract)
    except ToolError as error:
        return [str(error)]
    sources = checkout.core_sources()
    includes = checkout.includes()
    generated = checkout.generated_experiments()
    astronomy = checkout.astronomy_experiments()
    errors = contract_errors(raw)
    protocol = None if errors else parse_protocol(raw)
    if protocol is not None:
        errors.extend(source_inventory_errors(checkout, protocol))
        errors.extend(_firmware_errors(checkout, raw, protocol))
    errors.extend(
        xml_safety_errors([*sources, *includes, *generated, *astronomy], checkout.include_dir)
    )
    if errors or protocol is None:
        return errors
    if not generated:
        errors.append(f"No generated experiments found at {checkout.experiments_dir}/*.phyphox.")
    if {path.name for path in generated} != set(protocol.experiments):
        errors.append(
            f"{checkout.experiments_dir}: generated filenames do not match protocol contract"
        )
    for path in generated:
        errors.extend(
            check_core_experiment(path, protocol, expected_mode=protocol.mode_id_for(path.name))
        )
    for path in astronomy:
        errors.extend(check_astronomy_experiment(path))
    if errors:
        return errors
    try:
        xmllint = find_xmllint()
    except ToolError as error:
        return [str(error)]
    for path in [*includes, *sources, *generated, *astronomy]:
        try:
            run_xmllint([xmllint, "--noout", str(path)])
        except ToolError as error:
            errors.append(str(error))
    try:
        render_core_experiments(checkout, protocol)
    except ToolError as error:
        errors.append(str(error))
    return errors
