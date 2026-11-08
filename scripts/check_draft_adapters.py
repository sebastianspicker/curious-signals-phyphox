#!/usr/bin/env python3
"""Packet/layout, independent numerical and repeated-cycle checks for adapter XML.

This does not simulate BLE transport or establish native or physical validation.
"""

from __future__ import annotations

import argparse
import math
import struct
from pathlib import Path

from check_experiment_math import Experiment, reference_errors

NAN = float("nan")
SLUGS = (
    "greenhouse-single",
    "puck-light",
    "sensortag-environmental",
    "cc2541-accelerometer",
    "cc2541-gyroscope",
    "cc2541-magnetometer",
    "cc2541-humidity",
    "cc2541-pressure",
    "cc2541-ir-temperature",
    "pocketlab-gyroscope",
)


def close(actual: list[float], expected: list[float]) -> None:
    assert len(actual) == len(expected), (actual, expected)
    for aa, ee in zip(actual, expected):
        assert (math.isnan(aa) and math.isnan(ee)) or math.isclose(
            aa, ee, rel_tol=1e-11, abs_tol=1e-11
        ), (aa, ee)


def packet(exp: Experiment, suffix: str, payload: bytes, time: float) -> None:
    """Read the checked-in output conversion, offset and width for this fixture."""
    for output in exp.root.findall("./input/bluetooth/output"):
        if not output.get("char", "").lower().startswith(suffix.lower()):
            continue
        name = output.text.strip()
        if output.get("extra") == "time":
            value = time
        elif output.get("conversion") == "formattedString":
            value = float(
                payload.decode().split(output.get("separator", ","))[int(output.get("index", "0"))]
            )
        else:
            conversion = output.get("conversion")
            width = int(output.get("length", "2"))
            offset = int(output.get("offset", "0"))
            data = payload[offset : offset + width]
            assert len(data) == width, (name, offset, width, payload)
            assert conversion in {
                "int8",
                "int16LittleEndian",
                "uInt16LittleEndian",
                "int24LittleEndian",
                "uInt24LittleEndian",
                "int16BigEndian",
            }, conversion
            value = float(
                int.from_bytes(
                    data,
                    "big" if "Big" in conversion else "little",
                    signed=conversion.startswith("int"),
                )
            )
        exp.buffers[name].append(value)
        if exp.sizes[name]:
            exp.buffers[name] = exp.buffers[name][-exp.sizes[name] :]


def check(root: Path) -> None:
    base = root / "experiments/drafts"
    for slug in SLUGS:
        exp = Experiment(base / (slug + ".phyphox"))
        assert exp.root.get("version") == "1.17"
        assert exp.root.get("locale") == "en"
        assert exp.root.findtext("title").startswith("Draft: ")
        assert not reference_errors(exp.root, slug)
        assert not exp.root.findall("./analysis/ramp"), slug
        exp.run()  # Empty acquisition must not fabricate a sample.
        for output in exp.root.findall("./input/bluetooth/output"):
            if exp.sizes[output.text.strip()] == 0:
                assert not exp.buffers[output.text.strip()], slug

    # A single physical tag: signed BMP packet and baseline validity.
    exp = Experiment(base / "greenhouse-single.phyphox")
    packet(exp, "F000AA41", b"\xc4\x09\x00\x00\x00\x00", 0.4)
    packet(exp, "F000AA41", b"\xe8\x03\x00\x00\x00\x00", 60.4)
    exp.run()
    close(exp.buffers["temperature_C"], [25, 10])
    assert all(math.isnan(v) for v in exp.buffers["rise_K"])
    exp.set("baseline_C", 20)
    exp.set("baseline_valid", 1)
    for _ in range(3):
        exp.run()
        close(exp.buffers["rise_K"], [5, -10])
        close(exp.buffers["receive_min"], [0.4 / 60, 60.4 / 60])
        close(exp.buffers["temperature_raw"], [2500, 1000])

    # Two services are asynchronous. Do not borrow a humidity count clock.
    exp = Experiment(base / "sensortag-environmental.phyphox")
    packet(exp, "F000AA21", b"\x00\x80\x03\x80", 0.2)
    packet(exp, "F000AA21", b"\x00\x40\x00\x40", 2.9)
    packet(exp, "F000AA41", b"\x38\xff\xff\xcd\x8b\x01", 0.8)
    for _ in range(3):
        exp.run()
        close(exp.buffers["humidity_pct"], [50, 25])
        close(exp.buffers["hdc_temperature_C"], [42.5, 1.25])
        close(exp.buffers["bmp_temperature_C"], [-2])
        close(exp.buffers["pressure_hPa"], [1013.25])
        close(exp.buffers["humidity_receive_s"], [0.2, 2.9])
        close(exp.buffers["pressure_receive_s"], [0.8])

    # Native Puck script is scoped, rate limited, and encoded in MTU-sized chunks.
    exp = Experiment(base / "puck-light.phyphox")
    chunks = [n.text for n in exp.root.findall("./input/bluetooth/config")]
    script = "".join(chunks)
    assert all(len(chunk.encode()) <= 50 for chunk in chunks)
    assert "reset(" not in script and "clearInterval()" not in script
    assert "clearInterval(csLight.timer)" in script and "},250)" in script
    for i, value in enumerate([0.1, 0.5, 1.1]):
        packet(exp, "6e400003", f"{101 + i * 0.25},{value}".encode(), i * 0.31)
    exp.set("dark", 0.1)
    exp.set("reference", 0.9)
    exp.set("reference_valid", 1)
    for _ in range(3):
        exp.run()
        close(exp.buffers["light_relative"], [0.1, 0.5, NAN])
        close(exp.buffers["relative_transmission"], [0, 0.5, NAN])
        close(exp.buffers["device_s"], [101, 101.25, 101.5])
        close(exp.buffers["receive_s"], [0, 0.31, 0.62])
    exp.set("reference", 0.1)
    exp.run()
    assert all(math.isnan(v) for v in exp.buffers["relative_transmission"])

    for slug, wire, payload, raw, scale in [
        ("cc2541-accelerometer", "F000AA11", b"\x40\xc0\x80", [64, -64, -128], 9.80665 / 64),
        (
            "cc2541-gyroscope",
            "F000AA51",
            b"\x00\x40\x00\xc0\x00\x80",
            [16384, -16384, -32768],
            math.radians(500 / 65536),
        ),
        ("cc2541-magnetometer", "F000AA31", b"\xf4\x01\x0c\xfe\x00\x80", [500, -500, -32768], 0.1),
        (
            "pocketlab-gyroscope",
            "F000AA15",
            bytes.fromhex("0000 0000 0000 c000 4000 8000"),
            [16384, -16384, -32768],
            math.radians(2000 / 32768),
        ),
    ]:
        exp = Experiment(base / (slug + ".phyphox"))
        packet(exp, wire, payload, 0.37)
        packet(exp, wire, payload, 1.91)
        if slug == "cc2541-magnetometer":
            exp.run()
            assert math.isnan(exp.last("magnitude"))
            exp.set("scale_verified", 1)
        for axis in "xyz":
            exp.set("bias_" + axis, 0.25)
        expected = [r * scale - 0.25 for r in raw]
        for _ in range(4):
            exp.run()
            for axis, rr, value in zip("xyz", raw, expected):
                close(exp.buffers["raw_" + axis], [rr, rr])
                close(exp.buffers["value_" + axis], [value, value])
            close(exp.buffers["magnitude"], [math.hypot(*expected)] * 2)
            close(exp.buffers["receive_s"], [0.37, 1.91])
        exp.set("raw_x", [NAN, raw[0]])
        exp.run()
        assert math.isnan(exp.buffers["magnitude"][0])
        if slug == "cc2541-magnetometer":
            exp.set("scale", 0)
            exp.run()
            assert all(math.isnan(v) for v in exp.buffers["magnitude"])
        if slug == "pocketlab-gyroscope":
            assert exp.root.find("./input/bluetooth").get("name") == "PL Voyager"
            assert (
                exp.root.find("./input/bluetooth/config").get("char")
                == "F000AA14-0452-4000-B000-000000000000"
            )

    # SHT21 low two status bits, correct -6% intercept, independent T equation.
    exp = Experiment(base / "cc2541-humidity.phyphox")
    for traw, hraw, time in [(0x8003, 0x8003, 0.1), (0x0003, 0x0003, 2), (0xFFFF, 0xFFFF, 7)]:
        packet(exp, "F000AA21", struct.pack("<HH", traw, hraw), time)
    for _ in range(3):
        exp.run()
        close(exp.buffers["humidity_unbounded"], [56.5, -6, 65532 * 125 / 65536 - 6])
        close(exp.buffers["humidity_pct"], [56.5, NAN, NAN])
        close(exp.buffers["temperature_C"], [41.01, -46.85, 65532 * 175.72 / 65536 - 46.85])
        close(exp.buffers["receive_s"], [0.1, 2, 7])

    # T5400 actual read path, mixed coefficient signedness, missing-cal gate.
    exp = Experiment(base / "cc2541-pressure.phyphox")
    assert exp.root.find("./input/bluetooth").get("mode") == "poll"
    packet(exp, "F000AA41", struct.pack("<hH", -1000, 40000), 0.5)
    exp.set("requested_state", 1)
    exp.set("calibration_verified", 1)
    exp.run()
    assert math.isnan(exp.last("pressure_hPa"))
    coefficients = [30000, 400, 40000, 1000, -200, 100, -300, 50]
    packet(exp, "F000AA43", struct.pack("<HHHHhhhh", *coefficients), 0.8)
    packet(exp, "F000AA41", struct.pack("<hH", 2000, 41000), 2.2)
    expected_p, expected_t, expected_s, expected_o = [], [], [], []
    for traw, praw in [(-1000, 40000), (2000, 41000)]:
        # Independently express the manufacturer's fixed-point powers of two.
        c0, c1, c2, c3, c4, c5, c6, c7 = coefficients
        ss = c2 + c3 * traw / 2**17 + c4 * traw**2 / 2**34
        oo = c5 * 2**14 + c6 * traw / 2**3 + c7 * traw**2 / 2**19
        expected_s.append(ss)
        expected_o.append(oo)
        expected_p.append((ss * praw + oo) / 2**14 / 100)
        expected_t.append(100 * (c0 * traw / 2**8 + c1 * 2**6) / 2**16)
    for _ in range(3):
        exp.run()
        close(exp.buffers["sensitivity"], expected_s)
        close(exp.buffers["offset"], expected_o)
        close(exp.buffers["pressure_hPa"], expected_p)
        close(exp.buffers["temperature_C"], expected_t)
        close(exp.buffers["receive_s"], [0.5, 2.2])
    exp.set("requested_state", 2)
    exp.run()
    assert all(math.isnan(v) for v in exp.buffers["pressure_hPa"])
    exp.set("requested_state", 1)
    exp.set("c4", [])
    exp.run()
    assert all(math.isnan(v) for v in exp.buffers["pressure_hPa"])

    # TMP006 signed words, sample-wise compensation, missing/application guards.
    exp = Experiment(base / "cc2541-ir-temperature.phyphox")
    for vr, dr, time in [(-160, 3200, 0.2), (20, -1280, 2.3), (100, 3840, 2.7)]:
        packet(exp, "F000AA01", struct.pack("<hh", vr, dr), time)
    exp.run()
    assert all(math.isnan(v) for v in exp.buffers["object_C"])
    exp.set("S0", 6.4)
    exp.set("calibration_verified", 1)
    vv, dc, dk, dt, ss, vo, net, flux, obj = ([] for _ in range(9))
    for raw_voltage, raw_die in [(-160, 3200), (20, -1280), (100, 3840)]:
        voltage = raw_voltage * 156.25e-9
        die = raw_die / 128
        kelvin = die + 273.15
        delta = kelvin - 298.15
        sensitivity = 6.4e-14 * (1 + 1.75e-3 * delta - 1.678e-5 * delta**2)
        offset = -2.94e-5 - 5.7e-7 * delta + 4.63e-9 * delta**2
        residual = voltage - offset
        corrected = residual + 13.4 * residual**2
        result = (kelvin**4 + corrected / sensitivity) ** 0.25 - 273.15
        for values, value in zip(
            [vv, dc, dk, dt, ss, vo, net, flux, obj],
            [voltage, die, kelvin, delta, sensitivity, offset, residual, corrected, result],
        ):
            values.append(value)
    for _ in range(4):
        exp.run()
        for name, expected in zip(
            [
                "voltage_V",
                "die_C",
                "die_K",
                "delta_K",
                "sensitivity",
                "voltage_offset",
                "net_voltage",
                "flux_model",
                "object_C",
            ],
            [vv, dc, dk, dt, ss, vo, net, flux, obj],
        ):
            close(exp.buffers[name], expected)
        close(exp.buffers["receive_s"], [0.2, 2.3, 2.7])
    for setting, value in [("S0", 0), ("S0", -6.4), ("calibration_verified", 0)]:
        exp.set(setting, value)
        exp.run()
        assert all(math.isnan(v) for v in exp.buffers["object_C"])
    exp.set("S0", 6.4)
    exp.set("calibration_verified", 1)
    exp.set("die_raw", [-40000])
    exp.set("voltage_raw", [-32768])
    exp.run()
    assert math.isnan(exp.last("object_C"))
    print("Ten adapter XML packet, formula, invalid-input and repeated-cycle fixtures passed.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    check(parser.parse_args().root)


if __name__ == "__main__":
    main()
