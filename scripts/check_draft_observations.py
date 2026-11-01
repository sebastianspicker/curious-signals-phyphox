#!/usr/bin/env python3
"""Evaluate the four observation XML drafts, including native Record/Clear transfers.

These fixtures use the repository's focused XML interpreter. They do not claim
native phyphox, instrument calibration, BLE delivery or physical validation.
"""

from __future__ import annotations

import argparse
import math
import xml.etree.ElementTree as ET
from pathlib import Path

from check_experiment_math import Experiment

SLUGS = ("pressure-boiling", "spectral-fingerprints", "uv-transmission", "coronagraph-contrast")
NAN = float("nan")


def close(actual: float, expected: float) -> None:
    if math.isnan(expected):
        assert math.isnan(actual), actual
    else:
        assert math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12), (actual, expected)


def enter(exp: Experiment, **values: float) -> None:
    for name, value in values.items():
        exp.set(name + "_in", value)


def record(exp: Experiment, **values: float) -> None:
    enter(exp, **values)
    exp.press("Record row")
    exp.run()


def row_names(exp: Experiment) -> list[str]:
    return [name for name in exp.buffers if name.endswith("_row")]


def invariant_cycles(exp: Experiment) -> None:
    """Changes to controls and repeated processing cannot rewrite captured rows."""
    before = {name: list(exp.buffers[name]) for name in row_names(exp)}
    for item in exp.root.findall("./views/view/edit/output"):
        exp.set(item.text, 9999)
    exp.run()
    exp.run()
    for name, expected in before.items():
        actual = exp.buffers[name]
        assert len(actual) == len(expected), (name, actual, expected)
        for aa, bb in zip(actual, expected):
            close(aa, bb)
    assert exp.last("record_request") == 0
    for item in exp.root.findall("./export/set[@name='Captured observation rows']/data"):
        if not item.text.endswith("_row"):
            assert all(not math.isinf(value) for value in exp.buffers[item.text]), item.text
    assert len({len(exp.buffers[n]) for n in row_names(exp)}) == 1


def clear_and_cancel(exp: Experiment) -> None:
    """Clear cancels even an unprocessed button press, then permits a new row."""
    raw = {
        name: list(exp.buffers[name])
        for name in ("a0", "device_t", "receive_t")
        if name in exp.buffers
    }
    exp.press("Record row")
    exp.press("Clear rows")
    exp.run()
    exp.run()
    assert all(not exp.buffers[name] for name in row_names(exp))
    assert exp.last("row_count") == 0
    for name, expected in raw.items():
        assert exp.buffers[name] == expected
    # Validity can be off: raw observations must still be captured once.
    record(exp, id=42)
    exp.run()
    assert exp.buffers["id_row"] == [42]
    assert all(len(exp.buffers[n]) == 1 for n in row_names(exp))


def check_structure(path: Path) -> None:
    root = ET.parse(path).getroot()
    assert root.get("version") == "1.17" and root.get("locale") == "en"
    assert root.findtext("title").startswith("Draft: ")
    names = {item.text for item in root.findall("./data-containers/container")}
    sizes = {
        item.text: int(item.get("size", "1"))
        for item in root.findall("./data-containers/container")
    }
    for node in root.iter():
        if node.tag in {"input", "output", "data"} and node.text and node.text.strip():
            if node.get("type", "buffer") == "buffer":
                assert node.text.strip() in names, (path.name, node.text)
    for button in root.findall("./views/view/button"):
        for item in button.findall("input"):
            if item.get("type", "buffer") == "buffer":
                assert sizes[item.text] == 1, (path.name, button.get("label"), item.text)
    for dataset in root.findall("./export/set"):
        labels = [node.get("name") for node in dataset.findall("data")]
        assert len(labels) == len(set(labels)), (path.name, labels)
    # Histories are appended only by request-gated if modules.
    for module in root.findall("./analysis/*"):
        for output in module.findall("output"):
            if output.text.endswith("_row"):
                assert module.tag == "if" and output.get("append") == "true"
                assert module.findtext("input") == "record_request"


def pressure(path: Path) -> None:
    exp = Experiment(path)
    exp.run()
    assert exp.buffers["kelvin"] == []
    enter(exp, id=1, pressure=101.325, temperature=100, valid=1, code=1, up=0.1, ut=0.2)
    exp.press("Record row")
    # Button snapshots survive a subsequent edit before the analysis consumes them.
    enter(exp, pressure=999)
    exp.run()
    record(exp, id=2, pressure=50, temperature=80, valid=1, code=0)
    assert exp.buffers["pressure_row"] == [101.325, 50]
    assert exp.buffers["kelvin"] == [373.15, 353.15]
    close(exp.buffers["boiling_pressure"][0], 101.325)
    assert math.isnan(exp.last("boiling_pressure"))
    for p, t, valid in [
        (0, 20, 1),
        (-1, 20, 1),
        (50, -273.15, 1),
        (50, -274, 1),
        (50, 20, 0),
        (NAN, 20, 1),
        (50, NAN, 1),
        (float("inf"), 20, 1),
        (50, float("inf"), 1),
    ]:
        record(exp, pressure=p, temperature=t, valid=valid, code=1)
        assert math.isnan(exp.last("pressure_valid"))
    invariant_cycles(exp)
    clear_and_cancel(exp)


def spectra(path: Path) -> None:
    exp = Experiment(path)
    record(
        exp,
        id=1,
        wavelength=589.0,
        reference_line=589.1,
        sample=64,
        star=80,
        reference=100,
        dark=0,
        ceiling=200,
        paired=1,
        uw=0.2,
    )
    record(exp, id=2, wavelength=590.0, sample=50, star=100, reference=110, dark=10)
    close(exp.buffers["sample_transmission"][0], 0.64)
    close(exp.buffers["extra_sample_depth"][0], 0.2)
    close(exp.last("sample_transmission"), 40 / 100)
    close(exp.last("star_transmission"), 90 / 100)
    close(exp.last("extra_sample_depth"), 1 - 40 / 90)
    close(exp.buffers["delta_wavelength"][0], -0.1)
    record(exp, star=10)
    assert exp.last("star_transmission") == 0
    assert math.isnan(exp.last("extra_sample_depth"))
    base = dict(wavelength=589, sample=64, star=80, reference=100, dark=0, ceiling=200, paired=1)
    for change in [
        dict(reference=0),
        dict(paired=0),
        dict(paired=2),
        dict(wavelength=0),
        dict(sample=-1),
        dict(dark=-1),
        dict(sample=200),
        dict(star=201),
        dict(reference=200),
        dict(sample=NAN),
        dict(reference=NAN),
        dict(wavelength=float("inf")),
        dict(ceiling=float("inf")),
    ]:
        record(exp, **(base | change))
        assert math.isnan(exp.last("sample_transmission")), change
    invariant_cycles(exp)
    clear_and_cancel(exp)


def coronagraph(path: Path) -> None:
    exp = Experiment(path)
    record(
        exp,
        id=1,
        mask=0,
        separation=20,
        exposure=10,
        target=120,
        background=100,
        sigma=5,
        ceiling=255,
        paired=1,
    )
    record(exp, id=2, mask=1, target=40, background=20, sigma=2)
    assert exp.buffers["net_signal"] == [20, 20]
    assert exp.buffers["net_rate"] == [2000, 2000]
    assert exp.buffers["snr"] == [4, 10]
    close(exp.buffers["unmasked_contrast"][0], 0.2)
    assert math.isnan(exp.last("unmasked_contrast"))
    close(exp.last("masked_contrast"), 1)
    record(exp, target=10, background=20, sigma=0)
    assert exp.last("contrast") == -0.5  # Negative evidence is preserved.
    assert math.isnan(exp.last("snr"))
    base = dict(
        mask=1, separation=20, exposure=10, target=40, background=20, sigma=2, ceiling=255, paired=1
    )
    record(exp, **(base | dict(background=0)))
    assert math.isnan(exp.last("contrast"))
    assert exp.last("net_rate") == 4000
    for change in [
        dict(exposure=0),
        dict(separation=-1),
        dict(paired=0),
        dict(mask=2),
        dict(target=255),
        dict(background=255),
        dict(target=-1),
        dict(target=NAN),
        dict(exposure=float("inf")),
        dict(ceiling=float("inf")),
    ]:
        record(exp, **(base | change))
        assert math.isnan(exp.last("net_signal")), change
    invariant_cycles(exp)
    clear_and_cancel(exp)


def uv(path: Path) -> None:
    exp = Experiment(path)
    assert exp.root.find("analysis").get("onUserInput") == "false"
    bt = exp.root.find("./input/bluetooth")
    assert bt.get("name") == "phyphox-sense"
    assert bt.get("id") == exp.root.find("./output/bluetooth").get("id")
    assert float(exp.root.findtext("./output/bluetooth/config")) == 9
    fields = {node.text: node for node in bt.findall("output")}
    for name, offset in [("device_t", 0), ("a0", 4), ("a1", 8), ("a2", 12)]:
        assert fields[name].get("offset") == str(offset)
        assert fields[name].get("conversion") == "float32LittleEndian"
    assert fields["receive_t"].get("extra") == "time"
    exp.run()  # Missing streams produce scalar NaNs, keeping row lengths paired.
    record(exp, id=0, paired=1)
    assert math.isnan(exp.last("sample_row"))
    assert math.isnan(exp.last("transmission"))
    # Keep the missing observation: the first valid acquisition must append after it.
    for name, values in dict(a0=[7, 10], device_t=[1, 2], receive_t=[3, 4]).items():
        exp.set(name, values)
    exp.run()
    exp.press("Capture dark")
    assert exp.last("dark_in") == 10
    exp.set("a0", [7, 10, 610])
    exp.set("device_t", [1, 2, 4])
    exp.set("receive_t", [3, 4, 8])
    exp.run()
    exp.press("Capture reference")
    exp.set("a0", [7, 10, 610, 310])
    exp.set("device_t", [1, 2, 4, 5])
    exp.set("receive_t", [3, 4, 8, 9])
    exp.run()
    record(exp, id=1, paired=1, adc_gain=0.003, adc_offset=0.01, adc_valid=1, uv_gain=2, absolute=0)
    close(exp.last("transmission"), 0.5)
    assert math.isnan(exp.last("irradiance"))
    record(exp, id=2, absolute=1)
    close(exp.last("sample_voltage"), 0.94)
    close(exp.last("irradiance"), (0.94 - 0.04) * 2)
    for name, expected in [
        ("sample_row", [310, 310]),
        ("device_time_row", [5, 5]),
        ("receive_time_row", [9, 9]),
    ]:
        assert math.isnan(exp.buffers[name][0])
        assert exp.buffers[name][1:] == expected
    assert exp.buffers["id_row"] == [0, 1, 2]
    assert all(len(exp.buffers[name]) == 3 for name in row_names(exp))
    for name in ["transmission", "sample_voltage", "dark_voltage", "irradiance"]:
        assert len(exp.buffers[name]) == 3
        assert math.isnan(exp.buffers[name][0])
    for sample, ref, dark, paired in [
        (0, 610, 10, 1),
        (1023, 610, 10, 1),
        (310, 10, 10, 1),
        (5, 610, 10, 1),
        (310, 1023, 10, 1),
        (310, 610, 10, 0),
        (NAN, 610, 10, 1),
    ]:
        exp.set("a0", [sample])
        exp.run()
        record(exp, reference=ref, dark=dark, paired=paired)
        assert math.isnan(exp.last("transmission"))
    exp.set("a0", [310])
    exp.run()
    for changes in [
        dict(adc_valid=0),
        dict(absolute=0),
        dict(adc_gain=0),
        dict(uv_gain=-1),
        dict(adc_offset=4),
        dict(uv_gain=float("inf")),
    ]:
        base = dict(
            reference=610,
            dark=10,
            paired=1,
            adc_gain=0.003,
            adc_offset=0.01,
            adc_valid=1,
            uv_gain=2,
            absolute=1,
        )
        record(exp, **(base | changes))
        assert math.isnan(exp.last("irradiance")), changes
    invariant_cycles(exp)
    clear_and_cancel(exp)


def check(root: Path) -> None:
    folder = root / "experiments" / "drafts"
    for slug in SLUGS:
        check_structure(folder / f"{slug}.phyphox")
    pressure(folder / "pressure-boiling.phyphox")
    spectra(folder / "spectral-fingerprints.phyphox")
    coronagraph(folder / "coronagraph-contrast.phyphox")
    uv(folder / "uv-transmission.phyphox")
    print("Four observation draft XML numerical, native-button and repeated-cycle fixtures passed.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    check(parser.parse_args().root)


if __name__ == "__main__":
    main()
