#!/usr/bin/env python3
"""Evaluate mechanics draft XML; not native-app or physical validation."""

from __future__ import annotations

import argparse
import math
import xml.etree.ElementTree as ET
from pathlib import Path

from check_experiment_math import Experiment


def close(actual: float, expected: float) -> None:
    assert math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-10), (actual, expected)


def load_friction(
    exp: Experiment, times: list[float], acc: list[float], angles: list[float]
) -> None:
    exp.set("lin_t", times)
    exp.set("lin_a", acc)
    exp.set("gravity_t", times)
    exp.set("gx", [9.81 * math.sin(math.radians(x)) for x in angles])
    exp.set("gy", [0.0] * len(times))
    exp.set("gz", [9.81 * math.cos(math.radians(x)) for x in angles])


def check(root: Path) -> None:
    paths = root / "experiments" / "drafts"
    for slug in ["static-friction", "audio-magnetic", "magnetic-current"]:
        xml = ET.parse(paths / f"{slug}.phyphox").getroot()
        names = [n.text for n in xml.findall("./data-containers/container")]
        assert len(names) == len(set(names))
        assert xml.find("analysis").get("onUserInput") == "false"
        for section, tags in [
            ("input", {"output"}),
            ("analysis", {"input", "output"}),
            ("views", {"input", "output"}),
            ("export", {"data"}),
        ]:
            for item in xml.find(section).iter():
                if item.tag in tags and item.get("type", "buffer") == "buffer":
                    assert item.text in names, (slug, item.text)
        for export in xml.findall("./export/set"):
            headings = [n.get("name") for n in export.findall("data")]
            assert len(headings) == len(set(headings))

    exp = Experiment(paths / "static-friction.phyphox")
    exp.run()
    assert math.isnan(exp.last("mu"))
    # Arm after stationary acquisition, with first a brief disturbance and then
    # a genuine sustained excursion. Later motion has a much larger inclination.
    times = [i / 20 for i in range(101)]
    acc = [2.0 if 1.4 <= t < 1.45 or 2 <= t <= 2.5 or 3.5 <= t <= 4.5 else 0.1 for t in times]
    angles = [20.0 if t < 2 else 60.0 for t in times]
    load_friction(exp, times[:21], acc[:21], angles[:21])
    exp.press("Arm first slip")
    close(exp.last("arm_time"), 1)
    close(exp.last("armed_threshold"), 1)
    exp.set("threshold", 99)  # only affects NEXT arming
    load_friction(exp, times, acc, angles)
    exp.run()
    close(exp.last("slip_angle"), 20)
    close(exp.last("mu"), math.tan(math.radians(20)))
    assert 2.1 <= exp.last("trigger_time") <= 2.2
    assert exp.last("pre_time") < 2
    before = exp.last("trigger_time")
    exp.run()
    close(exp.last("trigger_time"), before)
    assert exp.buffers["lin_t"] == times
    exp.press("Clear capture")
    exp.run()
    assert math.isnan(exp.last("slip_angle"))
    assert math.isnan(exp.last("trigger_time"))
    assert math.isnan(exp.last("pre_time"))
    assert exp.buffers["lin_t"] == times
    # Re-arm at session time 5 s; old events cannot be selected.
    exp.set("threshold", 1)
    exp.press("Arm first slip")
    exp.run()
    assert math.isnan(exp.last("mu"))
    times2 = [i / 20 for i in range(131)]
    acc2 = acc + [0.1 if t < 5.7 else 2.0 for t in times2[101:]]
    angles2 = angles + [30.0] * 30
    load_friction(exp, times2, acc2, angles2)
    exp.run()
    close(exp.last("slip_angle"), 30)
    assert exp.last("trigger_time") > 5.7
    # No below-threshold sample means no valid initial onset.
    bad = Experiment(paths / "static-friction.phyphox")
    load_friction(bad, [0.0], [2.0], [20.0])
    bad.press("Arm first slip")
    load_friction(bad, [i / 20 for i in range(11)], [2.0] * 11, [20.0] * 11)
    bad.run()
    assert math.isnan(bad.last("mu"))
    # A long sensor gap resets rather than fulfilling a sustained duration.
    bad = Experiment(paths / "static-friction.phyphox")
    load_friction(bad, [0.0], [0.1], [20.0])
    bad.press("Arm first slip")
    load_friction(bad, [0, 0.05, 1.0, 1.05], [0.1, 2, 2, 2], [20.0] * 4)
    bad.run()
    assert math.isnan(bad.last("mu"))
    # A gap occurring while already above threshold is not itself a new onset.
    bad = Experiment(paths / "static-friction.phyphox")
    load_friction(bad, [0.0], [0.1], [20.0])
    bad.press("Arm first slip")
    gap_times = [0, 0.05] + [i / 20 for i in range(20, 31)]
    load_friction(bad, gap_times, [0.1] + [2.0] * (len(gap_times) - 1), [20.0] * len(gap_times))
    bad.set("gravity_t", [i / 20 for i in range(31)])
    bad.set("gx", [9.81 * math.sin(math.radians(20))] * 31)
    bad.set("gy", [0.0] * 31)
    bad.set("gz", [9.81 * math.cos(math.radians(20))] * 31)
    bad.run()
    assert math.isnan(bad.last("mu"))
    # A first excursion without quasi-static gravity is invalid; choose the
    # next valid excursion, rather than permanently blocking on the bad one.
    bad = Experiment(paths / "static-friction.phyphox")
    load_friction(bad, times[:21], acc[:21], angles[:21])
    bad.press("Arm first slip")
    load_friction(bad, times, acc, angles)
    bad.set("gx", [0.0 if 1.7 <= t < 2 else x for t, x in zip(times, bad.buffers["gx"])])
    bad.set("gz", [0.0 if 1.7 <= t < 2 else x for t, x in zip(times, bad.buffers["gz"])])
    bad.run()
    close(bad.last("slip_angle"), 60)
    assert bad.last("trigger_time") > 3.5
    # Out-of-range/absent pre-slip gravity must not become an apparent result.
    for invalid in [[], [0.0] * len(times)]:
        bad = Experiment(paths / "static-friction.phyphox")
        load_friction(bad, times[:21], acc[:21], angles[:21])
        bad.press("Arm first slip")
        load_friction(bad, times, acc, angles)
        bad.set("gx", invalid)
        bad.set("gz", invalid)
        bad.run()
        assert math.isnan(bad.last("mu"))

    exp = Experiment(paths / "audio-magnetic.phyphox")
    exp.set("audio_rate", 48000)
    exp.set("mag_t", [0.03, 0.08])
    exp.set("bx", [3, 0])
    exp.set("by", [4, 0])
    exp.set("bz", [0, 12])
    raw = []
    for now, block in [(0.1, [1.0, -1.0, 1.0, -1.0]), (0.27, [0.0, 2.0, -2.0])]:
        exp.timer_time = now
        exp.set("recording", block)
        exp.run()
        raw.extend(block)
        close(exp.last("audio_rms"), math.sqrt(sum(x * x for x in block) / len(block)))
        close(exp.last("audio_t"), now)
        close(exp.last("audio_n"), len(block))
        close(exp.last("audio_duration"), len(block) / 48000)
        assert exp.buffers["audio_raw"] == raw
    assert exp.buffers["audio_t"] == [0.1, 0.27]
    assert exp.buffers["mag_t"] == [0.03, 0.08]
    assert exp.buffers["mag_norm"] == [5, 12]
    # Repeated paused cycle with no new audio does not duplicate a block.
    exp.timer_time = 0.5
    exp.run()
    assert exp.buffers["audio_t"] == [0.1, 0.27]
    assert exp.buffers["audio_raw"] == raw
    exp.set("reference_rms", 0.5)
    exp.set("level_enabled", 1)
    exp.run()
    close(exp.buffers["level"][0], 20 * math.log10(2))
    exp.set("noise_rms", 1)
    exp.run()
    assert math.isnan(exp.buffers["noise_corrected_rms"][0])
    close(exp.buffers["noise_corrected_rms"][1], math.sqrt(8 / 3 - 1))
    for reference in [0, -0.5]:
        exp.set("reference_rms", reference)
        exp.run()
        assert len(exp.buffers["level"]) == 2
        assert all(math.isnan(x) for x in exp.buffers["level"])
    # Silence has no finite logarithmic level; explicit domain guards produce
    # NaN, rather than IEEE infinity from log(0) or a zero reference.
    exp.set("reference_rms", 0.5)
    exp.set("recording", [0.0, 0.0])
    exp.timer_time = 0.6
    exp.run()
    assert math.isnan(exp.last("level"))
    exp.set("reference_rms", [])
    exp.run()
    assert not exp.buffers["level"]
    exp.set("reference_rms", 0.5)
    exp.set("level_enabled", 0)
    exp.run()
    assert len(exp.buffers["level"]) == len(exp.buffers["audio_t"])
    assert all(math.isnan(x) for x in exp.buffers["level"])

    exp = Experiment(paths / "magnetic-current.phyphox")
    exp.set("mag_t", [0.0, 0.1, 0.2])
    exp.set("bz", [30, 42, 50])
    exp.run()
    assert all(math.isnan(x) for x in exp.buffers["current"])
    for key, val in {"b1": 30, "b2": 50, "i1": 0, "i2": 0.4, "cal_enabled": 1}.items():
        exp.set(key, val)
    exp.run()
    for actual, expected in zip(exp.buffers["current"], [0, 0.24, 0.4]):
        close(actual, expected)
    exp.run()
    assert len(exp.buffers["current"]) == 3
    # Reversed sensitivity is valid; no unsigned-field or coil-factor assumption.
    exp.set("b1", 50)
    exp.set("b2", 30)
    exp.run()
    close(exp.buffers["current"][1], 0.16)
    for settings in [
        {"b2": 50},
        {"b2": 50.5},
        {"b2": 30, "i2": 0},
        {"b2": 30, "i2": 0.4, "cal_enabled": 0},
    ]:
        for key, value in settings.items():
            exp.set(key, value)
        exp.run()
        assert all(math.isnan(x) for x in exp.buffers["current"]), settings
    exp.set("bz", [])
    exp.run()
    assert not exp.buffers["current"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    check(args.root)
    print("Mechanics draft XML numerical/cycle fixtures passed.")
