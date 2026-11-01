#!/usr/bin/env python3
"""Evaluate actual draft XML arithmetic, protocol fields and native-button cycles.

These fixtures are software evidence; no app, BLE link or physical apparatus is
validated. Expected values below are independent of XML formula construction.
"""

from __future__ import annotations

import argparse
import math
import struct
from pathlib import Path

from check_experiment_math import Experiment

SLUGS = (
    "nano-transit",
    "exomoon-photometry",
    "starspot-crossing",
    "eclipsing-binary",
    "seasons-obliquity",
)


def near(actual: float, expected: float) -> None:
    assert math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-10), (actual, expected)


def ingest(exp: Experiment, packet: bytes, arrival: float) -> None:
    """Decode the fixture packet using the checked-in offsets, preserving history."""
    for item in exp.root.findall("./input/bluetooth/output"):
        name = item.text.strip()
        if item.get("extra") == "time":
            value = arrival
        else:
            assert item.get("conversion") == "float32LittleEndian"
            value = struct.unpack_from("<f", packet, int(item.get("offset", "0")))[0]
        values = exp.buffers[name] + [value]
        size = exp.sizes[name]
        exp.set(name, values[-size:] if size else values)


def calibrated(exp: Experiment) -> None:
    for name, value in [("enabled", 1), ("dark", 10), ("baseline", 110)]:
        exp.set(name, value)


def check(root: Path) -> None:
    folder = root / "experiments/drafts"
    for slug in SLUGS:
        exp = Experiment(folder / f"{slug}.phyphox")
        xml = exp.root
        assert xml.get("version") == "1.17" and xml.get("locale") == "en"
        assert xml.findtext("title").startswith("Draft: ")
        assert xml.findtext("category") == "Curious Signals drafts"
        assert xml.find("analysis").get("onUserInput", "false") == "false"
        names = [e.text for e in xml.findall("./data-containers/container")]
        assert len(names) == len(set(names)), slug
        for section, tags in [
            ("input", {"output"}),
            ("output", {"input"}),
            ("analysis", {"input", "output"}),
            ("views", {"input", "output"}),
            ("export", {"data"}),
        ]:
            for item in xml.find(section).iter():
                if item.tag in tags and item.get("type", "buffer") == "buffer":
                    assert (item.text or "").strip() in names, (slug, item.text)
        for dataset in xml.findall("./export/set"):
            headings = [item.get("name") for item in dataset]
            assert len(headings) == len(set(headings)), (slug, headings)
        inp, out = xml.find("./input/bluetooth"), xml.find("./output/bluetooth")
        assert inp.get("name") == out.get("name") == "phyphox-sense"
        assert inp.get("id") == out.get("id")
        config = out.find("config")
        assert config.get("char") == "cddf1003-30f7-4671-8b43-5e40ba53514a"
        assert config.get("conversion") == "float32LittleEndian" and float(config.text) == 6
        ingest(exp, struct.pack("<5f", 100, 70, 30, 40, 50), 0.2)
        ingest(exp, struct.pack("<5f", 100.5, 90, 31, 41, 51), 1.7)
        assert exp.buffers["device_time"] == [100, 100.5]
        assert exp.buffers["receive_time"] == [0.2, 1.7]
        assert exp.buffers["clear"] == [70, 90]
        assert exp.buffers["red"] == [30, 31]
        assert exp.buffers["green"] == [40, 41]
        assert exp.buffers["blue"] == [50, 51]
        exp.run()
        assert all(math.isnan(v) for v in exp.buffers["normalized"])
        calibrated(exp)
        for _ in range(3):
            exp.run()
            assert len(exp.buffers["normalized"]) == 2
            for a, b in zip(exp.buffers["normalized"], [0.6, 0.8]):
                near(a, b)
            assert exp.buffers["clear"] == [70, 90]
            assert exp.buffers["receive_time"] == [0.2, 1.7]
        for baseline in [10, 9]:
            exp.set("baseline", baseline)
            exp.run()
            assert all(math.isnan(v) for v in exp.buffers["normalized"])
        calibrated(exp)
        exp.set("clear", [70, float("nan")])
        exp.run()
        near(exp.buffers["normalized"][0], 0.6)
        assert math.isnan(exp.buffers["normalized"][1])
        assert exp.buffers["receive_time"] == [0.2, 1.7]
        empty = Experiment(folder / f"{slug}.phyphox")
        empty.run()
        assert not empty.buffers["normalized"]

    exp = Experiment(folder / "nano-transit.phyphox")
    calibrated(exp)
    for n, value in [("plateau", 106), ("R_star", 5), ("distance_ratio", 0.5)]:
        exp.set(n, value)
    exp.run()
    near(exp.last("transit_depth"), 4)
    near(exp.last("R_planet"), 0.5)
    near(exp.last("Quot_R"), 10)
    for n, value in [
        ("plateau", 111),
        ("plateau", 9),
        ("R_star", 0),
        ("R_star", -1),
        ("distance_ratio", 0),
        ("distance_ratio", -1),
    ]:
        exp.set("plateau", 106)
        exp.set("R_star", 5)
        exp.set("distance_ratio", 0.5)
        exp.set(n, value)
        exp.run()
        assert math.isnan(exp.last("R_planet")), (n, value)
    exp = Experiment(folder / "nano-transit.phyphox")
    calibrated(exp)
    exp.set("dark", 0)
    exp.set("baseline", 100)
    times = list(range(28))
    signal = [96 if t < 2 or 5 <= t < 8 or 14 <= t < 17 or 23 <= t < 26 else 100 for t in times]
    exp.set("receive_time", times)
    exp.set("device_time", [900 + t for t in times])
    exp.set("clear", signal)
    for _ in range(3):
        exp.run()
        assert exp.last("complete_count") == 3
        near(exp.last("avg_transit_time"), 3)
        near(exp.last("avg_year_duration"), 9)
        assert [exp.last(f"on{i}") for i in range(3)] == [5, 14, 23]
        assert math.isnan(exp.last("on3"))
    exp.set("clear", signal[:25])
    exp.set("receive_time", times[:25])
    exp.run()
    assert exp.last("complete_count") == 2 and math.isnan(exp.last("off2"))
    exp.set("threshold_high", 0.97)
    exp.run()
    assert exp.last("complete_count") == 0

    exp = Experiment(folder / "exomoon-photometry.phyphox")
    calibrated(exp)
    for n, value in [("planet_mean", 100), ("separate_mean", 97), ("overlap_mean", 99)]:
        exp.set(n, value)
    exp.run()
    near(exp.last("extra_depth"), 0.03)
    near(exp.last("overlap_brightening"), 0.02)
    for n, bad in [("separate_mean", 101), ("overlap_mean", 101), ("separate_mean", 9)]:
        exp.set(n, bad)
        exp.run()
        assert math.isnan(exp.last("extra_depth")) and math.isnan(exp.last("overlap_brightening"))
        exp.set(n, {"separate_mean": 97, "overlap_mean": 99}[n])
    exp.set("enabled", 0)
    exp.run()
    assert math.isnan(exp.last("extra_depth"))

    exp = Experiment(folder / "starspot-crossing.phyphox")
    calibrated(exp)
    exp.set("adjacent_mean", 95)
    exp.set("crossing_mean", 98)
    exp.run()
    near(exp.last("spot_contrast"), 0.03)
    for n, value in [("crossing_mean", 94), ("crossing_mean", 111), ("adjacent_mean", 9)]:
        exp.set("adjacent_mean", 95)
        exp.set("crossing_mean", 98)
        exp.set(n, value)
        exp.run()
        assert math.isnan(exp.last("spot_contrast"))

    exp = Experiment(folder / "eclipsing-binary.phyphox")
    calibrated(exp)
    exp.set("baseline", 210)
    exp.set("primary_mean", 150)
    exp.set("secondary_mean", 190)
    exp.set("receive_time", [0, 2, 7, 12])
    exp.set("clear", [210, 150, 190, 150])
    exp.run()
    near(exp.last("primary_depth"), 0.3)
    near(exp.last("secondary_depth"), 0.1)
    near(exp.last("depth_contrast"), 0.2)
    assert all(math.isnan(v) for v in exp.buffers["phase"])
    exp.set("phase_enabled", 1)
    exp.set("period", 10)
    exp.set("epoch", 2)
    exp.run()
    assert exp.buffers["phase"] == [0.8, 0, 0.5, 0]
    exp.set("period", 0)
    exp.run()
    assert all(math.isnan(v) for v in exp.buffers["phase"])
    for n, value in [("primary_mean", 191), ("primary_mean", 9), ("secondary_mean", 211)]:
        exp.set("primary_mean", 150)
        exp.set("secondary_mean", 190)
        exp.set(n, value)
        exp.run()
        assert all(
            math.isnan(exp.last(x)) for x in ["primary_depth", "secondary_depth", "depth_contrast"]
        )

    exp = Experiment(folder / "seasons-obliquity.phyphox")
    # No measured packet: all paired sample fields remain NaN, including times.
    exp.press("Record observation")
    exp.run()
    assert math.isnan(exp.last("row_clear")) and math.isnan(exp.last("row_receive_time"))
    assert math.isnan(exp.last("row_relative"))
    # Retain the missing row while adding a valid row; sample/time pairing must
    # survive a leading NaN without compaction or division-based false values.
    calibrated(exp)
    exp.set("source_distance", 100)
    ingest(exp, struct.pack("<5f", 99, 70, 30, 40, 50), 0.1)
    exp.press("Record observation")
    exp.run()
    assert len(exp.buffers["row_clear"]) == 2
    assert math.isnan(exp.buffers["row_clear"][0])
    assert math.isnan(exp.buffers["row_receive_time"][0])
    assert math.isnan(exp.buffers["row_relative"][0])
    near(exp.buffers["row_clear"][1], 70)
    near(exp.buffers["row_receive_time"][1], 0.1)
    near(exp.buffers["row_relative"][1], 0.6)
    assert len(exp.buffers["row_device_time"]) == 2
    exp.press("Clear observation rows")
    exp.run()
    # Start the next fixture with fresh acquired history, like a new run.
    for name in ["device_time", "receive_time", "clear", "red", "green", "blue"]:
        exp.set(name, [])
    calibrated(exp)
    exp.set("source_distance", 100)
    exp.set("latitude", 30)
    exp.set("obliquity", 23.5)
    exp.set("orbit_position", 0)
    exp.set("trial", 1)
    ingest(exp, struct.pack("<5f", 100, 70, 30, 40, 50), 0.2)
    exp.run()
    exp.press("Record observation")
    exp.run()
    near(exp.last("row_relative"), 0.6)
    for _ in range(5):
        exp.run()
        assert exp.buffers["row_clear"] == [70]
    exp.set("latitude", -30)
    exp.set("orbit_position", 180)
    exp.set("trial", 2)
    ingest(exp, struct.pack("<5f", 101, 90, 31, 41, 51), 1.7)
    exp.run()
    exp.press("Record observation")
    exp.run()
    assert exp.buffers["row_clear"] == [70, 90]
    assert exp.buffers["row_device_time"] == [100, 101]
    assert exp.buffers["row_receive_time"] == [0.2, 1.7]
    assert exp.buffers["row_latitude"] == [30, -30]
    assert exp.buffers["row_orbit_position"] == [0, 180]
    assert exp.buffers["row_trial"] == [1, 2]
    exp.set("baseline", 999)
    exp.run()
    assert exp.buffers["row_baseline"] == [110, 110]
    for a, b in zip(exp.buffers["row_relative"], [0.6, 0.8]):
        near(a, b)
    exp.set("enabled", 0)
    exp.press("Record observation")
    exp.run()
    assert math.isnan(exp.last("row_relative")) and len(exp.buffers["row_clear"]) == 3
    exp.press("Clear observation rows")
    exp.run()
    assert not exp.buffers["row_clear"] and not exp.buffers["row_relative"]
    assert exp.buffers["clear"] == [70, 90] and exp.last("latitude") == -30
    print(
        "Photometry: five XML protocols, guarded reductions, event cycles "
        "and paired Record fixtures passed."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    check(parser.parse_args().root)
