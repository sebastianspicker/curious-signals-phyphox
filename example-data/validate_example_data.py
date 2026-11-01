#!/usr/bin/env python3
"""Check the internal consistency of the example data.

Run from the repository root:

    python3 example-data/validate_example_data.py

The checks cover self-consistency: magnitudes match their components, raw words
decode to the exported values, units agree, and the declared ranges are
respected.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "manifest.json"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def number(value: str) -> float:
    return float(value)


def close(actual: float, expected: float, tolerance: float = 1e-6) -> bool:
    if math.isnan(actual) and math.isnan(expected):
        return True
    if math.isnan(actual) or math.isnan(expected):
        return False
    return abs(actual - expected) <= tolerance * max(1.0, abs(expected))


def check_manifest() -> list[str]:
    errors: list[str] = []
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("example") is not True:
        errors.append("manifest does not mark the data as example")
    for entry in manifest["datasets"]:
        path = ROOT / entry["file"]
        if not path.exists():
            errors.append(f"missing file: {entry['file']}")
            continue
        columns, rows = read_csv(path)
        if columns != entry["columns"]:
            errors.append(f"{entry['file']}: columns differ from manifest")
        if len(rows) != entry["rows"]:
            errors.append(f"{entry['file']}: row count differs from manifest")
        errors += check_common(path, rows)
        if entry["file"] != "core/magnetometer_plot_v1-2.example.csv":
            if any(value == "nan" for row in rows for value in row.values()):
                errors.append(f"{entry['file']}: unexpected NaN value")
    return errors


def check_common(path: Path, rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return [f"{path.name}: no data rows"]
    errors: list[str] = []
    time_keys = ("Time t (s)", "Time (s)", "t (s)", "Time (min)")
    time_key = next((key for key in time_keys if key in rows[0]), None)
    if time_key is None:
        errors.append(f"{path.name}: no recognised time column")
    else:
        previous = -math.inf
        for index, row in enumerate(rows):
            try:
                current = number(row[time_key])
            except (KeyError, ValueError):
                errors.append(f"{path.name}: row {index} has a non-numeric time")
                continue
            if not math.isfinite(current) or current < 0:
                errors.append(f"{path.name}: row {index} has invalid time {current}")
            if current <= previous:
                errors.append(f"{path.name}: row {index} time is not increasing")
            previous = current

    for row in rows:
        for key, value in row.items():
            if value == "inf" or value == "-inf":
                errors.append(f"{path.name}: infinite value in {key}")
    return errors


def check_magnitude(
    path: Path,
    rows: list[dict[str, str]],
    axis_prefix: str,
    axis_suffix: str,
    magnitude_key: str,
) -> list[str]:
    errors: list[str] = []
    for index, row in enumerate(rows):
        values = [number(row[f"{axis_prefix}{axis}{axis_suffix}"]) for axis in ("x", "y", "z")]
        magnitude = number(row[magnitude_key])
        if any(math.isnan(value) for value in values):
            if not math.isnan(magnitude):
                errors.append(f"{path.name}: row {index} magnitude should be NaN")
            continue
        expected = math.sqrt(sum(value * value for value in values))
        if not close(magnitude, expected, tolerance=1e-6):
            errors.append(f"{path.name}: row {index} magnitude mismatch")
    return errors


def check_core() -> list[str]:
    errors: list[str] = []

    path = ROOT / "core/accelerometer_plot_v1-2.example.csv"
    _, rows = read_csv(path)
    errors += check_magnitude(path, rows, "Acceleration ", " (g)", "Absolute Acceleration (g)")
    errors += check_magnitude(
        path, rows, "Acceleration ", " (m/s²)", "Absolute Acceleration (m/s²)"
    )
    for index, row in enumerate(rows):
        for axis in ("x", "y", "z"):
            if not close(
                number(row[f"Acceleration {axis} (m/s²)"]),
                number(row[f"Acceleration {axis} (g)"]) * 9.81,
                tolerance=1e-6,
            ):
                errors.append(f"{path.name}: row {index} {axis} g/m/s² mismatch")

    path = ROOT / "core/gyroscope_plot_v1-2.example.csv"
    _, rows = read_csv(path)
    errors += check_magnitude(
        path, rows, "Angular Velocity ", " (deg/s)", "Absolute Angular Velocity (deg/s)"
    )
    errors += check_magnitude(
        path, rows, "Angular Velocity ", " (rad/s)", "Absolute Angular Velocity (rad/s)"
    )
    for index, row in enumerate(rows):
        for axis in ("x", "y", "z"):
            if not close(
                number(row[f"Angular Velocity {axis} (rad/s)"]),
                number(row[f"Angular Velocity {axis} (deg/s)"]) * 3.14159 / 180.0,
                tolerance=1e-5,
            ):
                errors.append(f"{path.name}: row {index} {axis} deg/rad mismatch")

    path = ROOT / "core/magnetometer_plot_v1-2.example.csv"
    _, rows = read_csv(path)
    errors += check_magnitude(path, rows, "Magnetometer ", " (µT)", "Absolute magnetic field (µT)")
    nan_rows = sum(1 for row in rows if row["Magnetometer x (µT)"] == "nan")
    if nan_rows != 4:
        errors.append(f"{path.name}: expected 4 NaN rows, found {nan_rows}")

    path = ROOT / "core/pressure_plot_v1-2.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        if not close(
            number(row["Pressure (hPa)"]),
            number(row["Pressure (kPa)"]) * 10.0,
            tolerance=1e-6,
        ):
            errors.append(f"{path.name}: row {index} kPa/hPa mismatch")

    path = ROOT / "core/light_plot_v1-2.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        values = [int(row[key]) for key in row if key != "Time t (s)"]
        if any(value < 0 or value > 4100 for value in values):
            errors.append(f"{path.name}: row {index} count outside 0-4100")
        clear = int(row["Relative light level (a.u.)"])
        colour = max(int(row["Red (a.u.)"]), int(row["Green (a.u.)"]), int(row["Blue (a.u.)"]))
        if clear * 1.05 < colour:
            errors.append(f"{path.name}: row {index} clear channel well below a colour channel")
    if not any(
        all(
            int(row[key]) == 4100
            for key in ("Relative light level (a.u.)", "Red (a.u.)", "Green (a.u.)", "Blue (a.u.)")
        )
        for row in rows
    ):
        errors.append(f"{path.name}: the flashlight interval never saturates all channels")

    path = ROOT / "core/analog_input_plot_v1-2.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        for channel in ("A0", "A1", "A2"):
            counts = int(row[f"Analog Input {channel}"])
            if counts < 0 or counts > 1023:
                errors.append(f"{path.name}: row {index} {channel} outside 0-1023")
            if not close(
                number(row[f"Voltage at {channel} (mV)"]),
                counts * 3.226,
                tolerance=1e-6,
            ):
                errors.append(f"{path.name}: row {index} {channel} count/mV mismatch")
    return errors


def opt3001_decode(word: int) -> float:
    exponent = word >> 12
    mantissa = word & 0x0FFF
    return 0.01 * mantissa * (2**exponent)


def tmp007_decode(word: int) -> float:
    return math.floor(word / 4) * 0.03125


def b35t_decode(field: str, decimal_code: int, unit_code: int) -> float:
    decimal = {0: 1.0, 1: 1e-3, 2: 1e-2, 4: 1e-1}[decimal_code]
    unit = {0: 1.0, 16: 1e6, 32: 1e3, 64: 1e-3, 128: 1e-6}[unit_code]
    return int(field) * decimal * unit


def check_astronomy() -> list[str]:
    errors: list[str] = []

    path = ROOT / "astronomy/albedo_sensortag.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        if not close(
            number(row["Relative light level (a.u.)"]),
            opt3001_decode(int(row["Raw OPT3001 word (a.u.)"])),
            tolerance=1e-9,
        ):
            errors.append(f"{path.name}: row {index} OPT3001 decode mismatch")

    path = ROOT / "astronomy/greenhouse.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        for tag in ("1", "2"):
            if not close(
                number(row[f"Temperature {tag} (°C)"]),
                int(row[f"Raw temperature {tag} word (a.u.)"]) * 0.01,
                tolerance=1e-9,
            ):
                errors.append(f"{path.name}: row {index} tag {tag} temperature decode mismatch")

    path = ROOT / "astronomy/ir-dist_habitable.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        if not close(
            number(row["T_IR (°C)"]),
            tmp007_decode(int(row["Raw object word (a.u.)"])),
            tolerance=1e-9,
        ):
            errors.append(f"{path.name}: row {index} object decode mismatch")
        if not close(
            number(row["T_amb (°C)"]),
            tmp007_decode(int(row["Raw die word (a.u.)"])),
            tolerance=1e-9,
        ):
            errors.append(f"{path.name}: row {index} die decode mismatch")

    path = ROOT / "astronomy/missiontomars_sensortag.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        if not close(
            number(row["Pressure (hPa)"]),
            int(row["Raw pressure word (a.u.)"]) * 0.01,
            tolerance=1e-9,
        ):
            errors.append(f"{path.name}: row {index} pressure decode mismatch")

    path = ROOT / "astronomy/owon_digital_multimeter-debug.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        decoded = b35t_decode(
            row["Raw numeric field (a.u.)"],
            int(row["Raw decimal code (a.u.)"]),
            int(row["Raw unit code (a.u.)"]),
        )
        if not close(number(row["y"]), decoded, tolerance=1e-9):
            errors.append(f"{path.name}: row {index} B35T decode mismatch")

    path = ROOT / "astronomy/pt-star.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        pressure = number(row["Pressure (hPa)"])
        if not 300.0 <= pressure <= 1100.0:
            errors.append(f"{path.name}: row {index} pressure outside BMP280 range")
        if not close(
            pressure,
            int(row["Raw pressure word (a.u.)"]) * 0.01,
            tolerance=1e-9,
        ):
            errors.append(f"{path.name}: row {index} pressure decode mismatch")
        if not close(
            number(row["Temperature (°C)"]),
            int(row["Raw temperature word (a.u.)"]) * 0.01,
            tolerance=1e-9,
        ):
            errors.append(f"{path.name}: row {index} temperature decode mismatch")

    path = ROOT / "astronomy/tidal-locking_bmp280.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        for tag in ("1", "2"):
            if not close(
                number(row[f"Temperature {tag} (°C)"]),
                int(row[f"Raw temperature {tag} word (a.u.)"]) * 0.01,
                tolerance=1e-9,
            ):
                errors.append(f"{path.name}: row {index} tag {tag} decode mismatch")

    path = ROOT / "astronomy/tidal-locking_tmp007.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        pairs = (
            ("Ambient temperature 1 (°C)", "Raw ambient 1 word (a.u.)"),
            ("Object temperature 1 (°C)", "Raw object 1 word (a.u.)"),
            ("Ambient temperature 2 (°C)", "Raw ambient 2 word (a.u.)"),
            ("Object temperature 2 (°C)", "Raw object 2 word (a.u.)"),
        )
        for value_key, raw_key in pairs:
            if not close(
                number(row[value_key]),
                tmp007_decode(int(row[raw_key])),
                tolerance=1e-9,
            ):
                errors.append(f"{path.name}: row {index} {value_key} decode mismatch")

    path = ROOT / "astronomy/tidal-locking_opt3001.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        for tag in ("1", "2"):
            if not close(
                number(row[f"Illuminance {tag} (lx)"]),
                opt3001_decode(int(row[f"Raw light {tag} word (a.u.)"])),
                tolerance=1e-9,
            ):
                errors.append(f"{path.name}: row {index} light {tag} decode mismatch")

    path = ROOT / "astronomy/transitmethode_sensortag.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        if not close(
            number(row["Relative Signal (a.u.)"]),
            opt3001_decode(int(row["Raw OPT3001 word (a.u.)"])),
            tolerance=1e-9,
        ):
            errors.append(f"{path.name}: row {index} OPT3001 decode mismatch")

    path = ROOT / "astronomy/transitmethode_owon.example.csv"
    _, rows = read_csv(path)
    for index, row in enumerate(rows):
        decoded = b35t_decode(
            row["Raw numeric field (a.u.)"],
            int(row["Raw decimal code (a.u.)"]),
            int(row["Raw unit code (a.u.)"]),
        )
        if not close(number(row["Relative Signal (a.u.)"]), decoded, tolerance=1e-9):
            errors.append(f"{path.name}: row {index} B35T decode mismatch")

    return errors


def main() -> int:
    errors = check_manifest()
    errors += check_core()
    errors += check_astronomy()
    if errors:
        print(f"{len(errors)} problem(s) found:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("example data: all internal consistency checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
