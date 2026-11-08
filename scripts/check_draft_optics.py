#!/usr/bin/env python3
"""Actual-XML fixtures for six optics drafts; no BLE or native-app validation."""

from __future__ import annotations

import argparse
import ast
import math
import re
import struct
from pathlib import Path

from check_experiment_math import Experiment, all_nan, ingest_nano, reference_errors

SLUGS = (
    "rgb-filter-transmission",
    "illuminance-distance",
    "illuminance-distance-manual",
    "malus-law",
    "colour-temperature",
    "detector-characterization",
)


def close(actual: float, expected: float) -> None:
    assert math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9), (actual, expected)


def rows(actual: list[float], expected: list[float]) -> None:
    assert len(actual) == len(expected), (actual, expected)
    for aa, bb in zip(actual, expected):
        if math.isnan(bb):
            assert math.isnan(aa), actual
        else:
            close(aa, bb)


def unchanged(exp: Experiment) -> None:
    """An idle cycle must preserve raw/captured rows and replace derived histories."""
    before = {name: list(values) for name, values in exp.buffers.items()}
    exp.run()
    for name, values in before.items():
        rows(exp.buffers[name], values)


def nano_frame(exp: Experiment, values: tuple[float, ...], receive: float) -> None:
    """Decode a real 20-byte mode-6-shaped fixture using checked-in XML offsets."""
    payload = struct.pack("<5f", *values)
    bluetooth = exp.root.find("./input/bluetooth")
    assert bluetooth is not None and bluetooth.get("name") == "phyphox-sense"
    assert bluetooth.get("id") == exp.root.find("./output/bluetooth").get("id")
    assert exp.root.findtext("./output/bluetooth/config") == "6"
    decoded = ingest_nano(exp, payload, receive)
    expected = dict(
        zip(["device_t", "clear", "red", "green", "blue", "receive_t"], [*values, receive])
    )
    for name, value in decoded.items():
        assert value == expected[name.removeprefix("current_")]
    for name in ["current_device_t", "current_receive_t", "current_clear"]:
        if name in exp.buffers:
            assert len(exp.buffers[name]) == 1


def check(root: Path) -> None:
    base = root / "experiments/drafts"

    def load(slug: str) -> Experiment:
        exp = Experiment(base / f"{slug}.phyphox")
        assert exp.root.get("version") == "1.17"
        assert exp.root.get("locale") == "en"
        assert exp.root.findtext("title").startswith("Draft: ")
        assert exp.root.findtext("category") == "Curious Signals drafts"
        assert exp.root.find("analysis").get("onUserInput") == "false"
        assert not reference_errors(exp.root, slug)
        for formula in exp.root.findall("./analysis/formula"):
            # Check syntax even when missing buffers mean no numerical output rows.
            code = re.sub(r"\[\d+_?\]", "(1)", formula.get("formula")).replace("^", "**")
            ast.parse(code, mode="eval")
        return exp

    experiments = {slug: load(slug) for slug in SLUGS}
    nan = math.nan
    rgb = experiments["rgb-filter-transmission"]
    for channel in ["clear", "red", "green", "blue"]:
        rgb.set(channel, [10, 510, 1010, 4100, 5])
        rgb.set("dark_" + channel, 10)
        rgb.set("reference_" + channel, 1010)
    rgb.set("device_t", [1, 2, 3, 4, 5])
    rgb.run()
    assert all_nan(rgb.buffers["transmission_red"])
    rgb.set("enabled", 1)
    rgb.run()
    rows(rgb.buffers["transmission_red"], [0, 0.5, 1, nan, nan])
    unchanged(rgb)
    rgb.set("reference_red", 10)
    rgb.run()
    assert all_nan(rgb.buffers["transmission_red"])

    distance = experiments["illuminance-distance"]
    distance.set("dx", [0, 10, 10])
    distance.set("dy", [0, 0, 0])
    distance.set("mouse_t", [1, 2, 3])
    distance.set("light_t", [0.5, 1.5, 2.5, 3.5])
    distance.set("light_raw", [1000, 4096 + 500, 8192 + 250, 49152])
    distance.set("scale", 0.01)
    distance.set("origin", 0.2)
    distance.set("background", 2)
    distance.run()
    assert all_nan(distance.buffers["distance"])
    distance.set("enabled", 1)
    distance.run()
    rows(distance.buffers["distance"], [nan, 0.2, 0.3, 0.4])
    rows(distance.buffers["lux"], [10, 10, 10, nan])
    rows(distance.buffers["corrected_lux"], [8, 8, 8, nan])
    rows(distance.buffers["inverse_square"], [nan, 25, 1 / 0.3**2, 6.25])
    unchanged(distance)
    distance.set("scale", 0)
    distance.run()
    assert all_nan(distance.buffers["distance"])
    missing = load("illuminance-distance")
    missing.set("light_t", [1])
    missing.set("light_raw", [1000])
    missing.run()
    assert not missing.buffers["distance"]
    distance.set("scale", 0.01)
    distance.set("origin", 0)
    distance.set("background", 11)
    distance.run()
    assert math.isnan(distance.buffers["distance"][1])
    assert all_nan(distance.buffers["log_light"])
    distance.set("origin", -1)
    distance.run()
    assert all_nan(distance.buffers["distance"])
    assert all_nan(distance.buffers["inverse_square"])
    assert all_nan(distance.buffers["scaled_light"])

    manual = experiments["illuminance-distance-manual"]
    manual.run()
    manual.press("Record")
    manual.run()
    assert len(manual.buffers["row_clear"]) == len(manual.buffers["row_distance"]) == 1
    assert math.isnan(manual.last("row_clear"))
    # Preserve this first unavailable row, then acquire real data: later rows must not shift.
    unchanged(manual)
    nano_frame(manual, (10, 410, 100, 200, 300), 0.125)
    manual.set("background", 10)
    manual.run()
    manual.set("entered_distance", 0.5)
    manual.press("Record")
    manual.run()
    unchanged(manual)
    nano_frame(manual, (11, 110, 90, 80, 70), 0.875)
    manual.run()
    manual.set("entered_distance", 1)
    manual.press("Record")
    manual.run()
    rows(manual.buffers["row_distance"], [0, 0.5, 1])
    rows(manual.buffers["row_clear"], [nan, 410, 110])
    rows(manual.buffers["row_device_t"], [nan, 10, 11])
    rows(manual.buffers["row_receive_t"], [nan, 0.125, 0.875])
    rows(manual.buffers["scaled_light"], [nan, 100, 100])
    unchanged(manual)
    manual.press("Clear observations")
    manual.run()
    assert not manual.buffers["row_distance"] and not manual.buffers["scaled_light"]
    assert manual.buffers["clear"] == [410, 110]
    manual.set("entered_distance", -1)
    manual.press("Record")
    manual.run()
    assert math.isnan(manual.last("valid_distance"))
    assert math.isnan(manual.last("inverse_square"))
    assert math.isnan(manual.last("scaled_light"))
    assert math.isnan(manual.last("log_distance"))

    malus = experiments["malus-law"]
    malus.set("background", 10)
    malus.set("parallel", 1010)
    malus.set("angle_zero", 10)
    malus.run()
    malus.press("Record")
    malus.run()
    assert math.isnan(malus.last("row_clear"))
    for index, (angle, signal) in enumerate([(10, 1010), (40, 760), (100, 10)]):
        nano_frame(malus, (20 + index, signal, 100, 200, 300), index + 0.25)
        malus.run()
        malus.set("entered_angle", angle)
        malus.press("Record")
        malus.run()
    assert all_nan(malus.buffers["normalized"])
    malus.set("enabled", 1)
    malus.run()
    rows(malus.buffers["row_device_t"], [nan, 20, 21, 22])
    rows(malus.buffers["row_receive_t"], [nan, 0.25, 1.25, 2.25])
    rows(malus.buffers["theta"], [-10, 0, 30, 90])
    rows(malus.buffers["prediction"], [math.cos(math.radians(-10)) ** 2, 1, 0.75, 0])
    rows(malus.buffers["normalized"], [nan, 1, 0.75, 0])
    rows(malus.buffers["residual"], [nan, 0, 0, 0])
    unchanged(malus)
    malus.set("parallel", 10)
    malus.run()
    assert all_nan(malus.buffers["normalized"])
    malus.press("Clear observations")
    malus.run()
    assert not malus.buffers["row_angle"] and len(malus.buffers["clear"]) == 3

    colour = experiments["colour-temperature"]
    # An identity matrix isolates chromaticity and independently checks polynomial signs.
    for coord in "XYZ":
        for channel in ["red", "green", "blue"]:
            colour.set(
                "m" + coord + channel, float(channel == dict(X="red", Y="green", Z="blue")[coord])
            )
    colour.set("clear", [100, 100, 0, 4100, 100, 100])
    colour.set("red", [33.2, 35, 33.2, 33.2, 33.2, -1])
    colour.set("green", [30, 35, 30, 30, 18.58, 30])
    colour.set("blue", [36.8, 30, 36.8, 36.8, 48.22, 71])
    colour.run()
    assert all_nan(colour.buffers["cct"])
    colour.set("enabled", 1)
    colour.run()
    n = (0.35 - 0.3320) / (0.1858 - 0.35)
    expected = 449 * n**3 + 3525 * n**2 + 6823.3 * n + 5520.33
    rows(colour.buffers["cct"], [5520.33, expected, nan, nan, nan, nan])
    assert math.isnan(colour.buffers["clear_corrected"][2])
    assert math.isnan(colour.buffers["ratio_red"][2])
    assert math.isnan(colour.buffers["n"][4])
    unchanged(colour)
    donor = load("colour-temperature")
    for channel, val in [("clear", 100), ("red", 50), ("green", 70), ("blue", 30)]:
        donor.set(channel, [val])
    donor.run()
    close(donor.last("X"), -0.14282 * 0.5 + 1.54924 * 0.7 - 0.95641 * 0.3)
    close(donor.last("Y"), -0.32466 * 0.5 + 1.57837 * 0.7 - 0.73191 * 0.3)
    close(donor.last("Z"), -0.68202 * 0.5 + 0.77073 * 0.7 + 0.56332 * 0.3)

    detector = experiments["detector-characterization"]
    detector.set("device_t", [10, 10.05, 10.11, 10.2])
    detector.set("receive_t", [0.1, 0.2, 0.21, 0.4])
    detector.set("clear", [100, 102, 98, 100])
    detector.set("baseline_start", 10)
    detector.set("baseline_end", 10.11)
    detector.set("dark", 10)
    detector.set("depth", 0.1)
    detector.set("duration", 0.2)
    detector.run()
    rows(detector.buffers["dt_device_t"], [0.05, 0.06, 0.09])
    rows(detector.buffers["dt_receive_t"], [0.1, 0.01, 0.19])
    close(detector.last("mean_rate_device_t"), 15)
    close(detector.last("mean_rate_receive_t"), 10)
    close(detector.last("baseline_mean"), 100)
    close(detector.last("baseline_sd"), 2)
    close(detector.last("expected_drop"), 9)
    close(detector.last("snr"), 4.5)
    close(detector.last("samples_per_feature"), 3)
    unchanged(detector)
    detector.set("clear", [100, 100, 100, 100])
    detector.run()
    close(detector.last("baseline_sd"), 0)
    assert math.isnan(detector.last("snr"))
    detector.set("baseline_end", 10)
    detector.run()
    assert math.isnan(detector.last("snr"))
    detector.set("baseline_start", 50)
    detector.run()
    assert math.isnan(detector.last("baseline_mean"))
    detector.set("device_t", [10, 10, 9, 10])
    detector.run()
    assert math.isnan(detector.buffers["rate_device_t"][0])
    assert math.isnan(detector.buffers["rate_device_t"][1])
    assert math.isnan(detector.last("mean_rate_device_t"))
    assert math.isnan(detector.last("samples_per_feature"))
    print("Optics: 6 actual-XML fixtures passed; no native/BLE/physical validation")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    check(parser.parse_args().root)
