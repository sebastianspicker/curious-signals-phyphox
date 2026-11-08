#!/usr/bin/env python3
"""Check the internal consistency of the draft example data.

Run from the repository root:

    python3 example-data/validate_draft_example_data.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_example_data import (  # noqa: E402
    check_infinite,
    check_time_column,
    number,
    opt3001_decode,
    read_csv,
)
from validate_example_data import close as shared_close  # noqa: E402

ROOT = Path(__file__).resolve().parent / "drafts"
MANIFEST = ROOT / "manifest.json"
TIME_KEYS = (
    "Receive time (s)",
    "Receive time (min)",
    "Data read receive time (s)",
    "Light receive time (s)",
    "Mouse receive time (s)",
    "Captured device time (s)",
    "Captured receive time (s)",
    "Device time (s)",
    "mag_t",
    "audio_t",
    "device_t (s)",
    "receive_t (s)",
    "receive_time",
    "device_time",
    "gravity_t",
    "lin_t",
    "row_device_time",
    "row_receive_time",
)
# Observation tables and summaries that legitimately have no time column.
NO_TIME_FILES = frozenset(
    {
        "coronagraph-contrast.example.csv",
        "detector-characterization_summary.example.csv",
        "pressure-boiling.example.csv",
        "spectral-fingerprints.example.csv",
    }
)


def close(actual: float, expected: float, tolerance: float = 1e-5) -> bool:
    return shared_close(actual, expected, tolerance)


def check_manifest() -> list[str]:
    errors: list[str] = []
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("example") is not True:
        errors.append("manifest does not mark the data as example")
    listed = {entry["file"].removeprefix("drafts/") for entry in manifest["datasets"]}
    on_disk = {path.name for path in ROOT.glob("*.csv")}
    for name in sorted(on_disk - listed):
        errors.append(f"{name}: not in manifest")
    for entry in manifest["datasets"]:
        path = ROOT / entry["file"].removeprefix("drafts/")
        if not path.exists():
            errors.append(f"missing file: {entry['file']}")
            continue
        columns, rows = read_csv(path)
        if columns != entry["columns"]:
            errors.append(f"{entry['file']}: columns differ from manifest")
        if len(rows) != entry["rows"]:
            errors.append(f"{entry['file']}: row count differs from manifest")
    return errors


def check_common(path: Path, rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return [f"{path.name}: no data rows"]
    errors: list[str] = []
    keys = [key for key in TIME_KEYS if key in rows[0]]
    if not keys and path.name not in NO_TIME_FILES:
        errors.append(f"{path.name}: no recognised time column")
    for key in keys:
        errors += check_time_column(path, rows, key, strict=False)
    return errors + check_infinite(path, rows)


def check_count_range(
    path: Path, rows: list[dict[str, str]], columns: tuple[str, ...], low: float, high: float
) -> list[str]:
    errors = [
        f"{path.name}: missing column {key}" for key in columns if rows and key not in rows[0]
    ]
    for index, row in enumerate(rows):
        for key in columns:
            if key not in row:
                continue
            value = number(row[key])
            if not low <= value <= high:
                errors.append(f"{path.name}: row {index} {key}={value} outside {low}..{high}")
    return errors


def check_magnitude(
    path: Path,
    rows: list[dict[str, str]],
    prefixes: tuple[str, str, str],
    magnitude_key: str,
) -> list[str]:
    errors: list[str] = []
    for index, row in enumerate(rows):
        values = [number(row[key]) for key in prefixes]
        expected = math.sqrt(sum(value * value for value in values))
        if not close(number(row[magnitude_key]), expected, tolerance=1e-6):
            errors.append(f"{path.name}: row {index} magnitude mismatch")
    return errors


def check_drafts() -> list[str]:
    errors: list[str] = []

    for path in sorted(ROOT.glob("*.csv")):
        _, rows = read_csv(path)
        errors += check_common(path, rows)

    # APDS / Nano files; the photometry records use bare channel names.
    labelled = ("clear (counts)", "red (counts)", "green (counts)", "blue (counts)")
    bare = ("clear", "red", "green", "blue")
    for name, columns in (
        ("detector-characterization.example.csv", labelled),
        ("eclipsing-binary.example.csv", bare),
        ("exomoon-photometry.example.csv", bare),
        ("illuminance-distance-manual.example.csv", labelled),
        ("malus-law.example.csv", labelled),
        ("nano-transit.example.csv", bare),
        ("rgb-filter-transmission.example.csv", labelled),
        ("seasons-obliquity.example.csv", bare),
        ("starspot-crossing.example.csv", bare),
        ("colour-temperature.example.csv", labelled),
    ):
        path = ROOT / name
        _, rows = read_csv(path)
        errors += check_count_range(path, rows, columns, 0.0, 4100.0)

    path = ROOT / "cc2541-accelerometer.example.csv"
    _, rows = read_csv(path)
    errors += check_count_range(
        path,
        rows,
        ("Signed packet x (count)", "Signed packet y (count)", "Signed packet z (count)"),
        -128,
        127,
    )
    errors += check_magnitude(
        path,
        rows,
        ("Bias corrected x (m/s²)", "Bias corrected y (m/s²)", "Bias corrected z (m/s²)"),
        "Vector magnitude (m/s²)",
    )

    for name in (
        "cc2541-gyroscope.example.csv",
        "cc2541-magnetometer.example.csv",
        "pocketlab-gyroscope.example.csv",
    ):
        path = ROOT / name
        _, rows = read_csv(path)
        errors += check_count_range(
            path,
            rows,
            ("Signed packet x (count)", "Signed packet y (count)", "Signed packet z (count)"),
            -32768,
            32767,
        )
        errors += (
            check_magnitude(
                path,
                rows,
                (
                    "Bias corrected x (rad/s)",
                    "Bias corrected y (rad/s)",
                    "Bias corrected z (rad/s)",
                ),
                "Vector magnitude (rad/s)",
            )
            if "gyroscope" in name
            else []
        )
        errors += (
            check_magnitude(
                path,
                rows,
                ("Bias corrected x (µT)", "Bias corrected y (µT)", "Bias corrected z (µT)"),
                "Vector magnitude (µT)",
            )
            if "magnetometer" in name
            else []
        )

    path = ROOT / "cc2541-humidity.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        raw_t = int(row["Unsigned temperature packet word"])
        raw_h = int(row["Unsigned humidity packet word"])
        masked_t = (raw_t // 4) * 4
        masked_h = (raw_h // 4) * 4
        rh = 125.0 * masked_h / 65536.0 - 6.0
        temperature = 175.72 * masked_t / 65536.0 - 46.85
        if not close(number(row["Unbounded RH equation (%)"]), rh):
            errors.append(f"{path.name}: row {index} RH equation mismatch")
        expected_rh = rh if 0.0 <= rh <= 100.0 else math.nan
        if not close(number(row["Domain checked RH (%)"]), expected_rh):
            errors.append(f"{path.name}: row {index} domain RH mismatch")
        if not close(number(row["SHT21 temperature (°C)"]), temperature):
            errors.append(f"{path.name}: row {index} temperature mismatch")

    path = ROOT / "cc2541-ir-temperature.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        voltage = int(row["Signed thermopile packet word"]) * 156.25e-9
        die = int(row["Signed die packet word"]) / 128.0
        if not close(number(row["Thermopile voltage (V)"]), voltage):
            errors.append(f"{path.name}: row {index} voltage mismatch")
        if not close(number(row["Die temperature (°C)"]), die):
            errors.append(f"{path.name}: row {index} die mismatch")

    path = ROOT / "cc2541-pressure.example.csv"
    _, rows = read_csv(path)
    c0, c1, c2, c3, c4, c5, c6, c7 = 30000, 400, 40000, 1000, -200, 100, -300, 50
    for index, row in enumerate(rows):
        ut = int(row["Signed temperature word"])
        up = int(row["Unsigned pressure word"])
        sensitivity = c2 + c3 * ut / 2**17 + c4 * ut**2 / 2**34
        offset = c5 * 2**14 + c6 * ut / 8 + c7 * ut**2 / 2**19
        pressure = (sensitivity * up + offset) / 2**14 / 100.0
        temperature = 100.0 * (c0 * ut / 256.0 + c1 * 64.0) / 65536.0
        if not close(number(row["Pressure (hPa)"]), pressure, tolerance=1e-4):
            errors.append(f"{path.name}: row {index} pressure mismatch")
        if not close(number(row["T5400 temperature (°C)"]), temperature):
            errors.append(f"{path.name}: row {index} temperature mismatch")

    path = ROOT / "greenhouse-single.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        if not close(
            number(row["Die temperature (°C)"]), int(row["Signed BMP280 packet count"]) / 100.0
        ):
            errors.append(f"{path.name}: row {index} temperature mismatch")

    path = ROOT / "illuminance-distance_light.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        word = int(row["OPT3001 raw word (uint16)"])
        decoded = opt3001_decode(word)
        if not close(number(row["Decoded illuminance (lx)"]), decoded, tolerance=1e-8):
            errors.append(f"{path.name}: row {index} OPT3001 decode mismatch")
        distance = number(row["Calibrated source distance (m)"])
        corrected = number(row["Background-corrected illuminance (lx)"])
        if not close(
            number(row["Corrected illuminance times distance squared (lx m²)"]),
            corrected * distance**2,
        ):
            errors.append(f"{path.name}: row {index} scaled light mismatch")

    path = ROOT / "magnetic-current.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        expected = (number(row["bz"]) - 30.0) * 0.4 / 20.0
        if not close(number(row["current"]), expected, tolerance=1e-8):
            errors.append(f"{path.name}: row {index} current mismatch")

    path = ROOT / "malus-law_observations.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        expected = (number(row["Captured clear signal (counts)"]) - 10.0) / 1000.0
        if not close(number(row["Normalized transmission (1)"]), expected):
            errors.append(f"{path.name}: row {index} normalized mismatch")

    path = ROOT / "rgb-filter-transmission.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        for channel in ("clear", "red", "green", "blue"):
            dark = {"clear": 3.0, "red": 2.0, "green": 2.0, "blue": 1.0}[channel]
            reference = {"clear": 1800.0, "red": 900.0, "green": 1050.0, "blue": 620.0}[channel]
            expected = (number(row[f"{channel} (counts)"]) - dark) / (reference - dark)
            if not close(number(row[f"{channel} transmission (1)"]), expected, tolerance=1e-5):
                errors.append(f"{path.name}: row {index} {channel} transmission mismatch")

    path = ROOT / "seasons-obliquity_observations.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        expected = (number(row["row_clear"]) - number(row["row_dark"])) / (
            number(row["row_baseline"]) - number(row["row_dark"])
        )
        if not close(number(row["row_relative"]), expected):
            errors.append(f"{path.name}: row {index} relative mismatch")

    path = ROOT / "sensortag-environmental_humidity.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        humidity = (int(row["humidity_raw (packet count)"]) // 4) * 4 / 65536.0 * 100.0
        temperature = int(row["hdc_temperature_raw (packet count)"]) / 65536.0 * 165.0 - 40.0
        if not close(number(row["Relative humidity (%)"]), humidity):
            errors.append(f"{path.name}: row {index} humidity mismatch")
        if not close(number(row["HDC1000 temperature (°C)"]), temperature):
            errors.append(f"{path.name}: row {index} temperature mismatch")

    path = ROOT / "sensortag-environmental_barometer.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        if not close(
            number(row["Pressure (hPa)"]), int(row["pressure_raw (packet count)"]) / 100.0
        ):
            errors.append(f"{path.name}: row {index} pressure mismatch")
        if not close(
            number(row["BMP280 die temperature (°C)"]),
            int(row["bmp_temperature_raw (packet count)"]) / 100.0,
        ):
            errors.append(f"{path.name}: row {index} temperature mismatch")

    path = ROOT / "spectral-fingerprints.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        sample = (number(row["Sample intensity (a.u.)"]) - number(row["Dark intensity (a.u.)"])) / (
            number(row["Continuum reference intensity (a.u.)"])
            - number(row["Dark intensity (a.u.)"])
        )
        star = (
            number(row["Star-only intensity (a.u.)"]) - number(row["Dark intensity (a.u.)"])
        ) / (
            number(row["Continuum reference intensity (a.u.)"])
            - number(row["Dark intensity (a.u.)"])
        )
        if not close(number(row["Sample over continuum reference"]), sample):
            errors.append(f"{path.name}: row {index} sample transmission mismatch")
        if not close(number(row["Star over continuum reference"]), star):
            errors.append(f"{path.name}: row {index} star transmission mismatch")

    path = ROOT / "static-friction_gravity.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        gx, gy, gz = (number(row[key]) for key in ("gx", "gy", "gz"))
        angle = math.degrees(math.atan2(math.hypot(gx, gy), abs(gz)))
        if not close(number(row["angle"]), angle, tolerance=1e-5):
            errors.append(f"{path.name}: row {index} angle mismatch")
        if not close(number(row["gnorm"]), math.sqrt(gx * gx + gy * gy + gz * gz), tolerance=1e-5):
            errors.append(f"{path.name}: row {index} norm mismatch")

    path = ROOT / "uv-transmission_observations.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        sample = number(row["Captured A0 (count)"])
        reference = number(row["Unfiltered reference (count)"])
        dark = number(row["Covered detector dark (count)"])
        transmission = (sample - dark) / (reference - dark)
        if not close(number(row["UV detector weighted transmission"]), transmission):
            errors.append(f"{path.name}: row {index} transmission mismatch")

    return errors


def main() -> int:
    errors = check_manifest()
    errors += check_drafts()
    if errors:
        print(f"{len(errors)} problem(s) found:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("draft example data: all internal consistency checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
