"""Reproduce the thermal-paper calculations from the supplied example CSVs."""

from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

from _common import in_window, read_dicts


def time_s(row: dict[str, float]) -> float:
    return round(row["Time (s)"] if "Time (s)" in row else row["Time (min)"] * 60, 6)


def window(rows: list[dict[str, float]], start: float, end: float) -> list[dict[str, float]]:
    return [row for row in rows if in_window(time_s(row), start, end)]


def average(rows: list[dict[str, float]], column: str) -> float:
    return statistics.mean(row[column] for row in rows)


def fit_heating(rows: list[dict[str, float]], column: str, baseline: float) -> dict[str, float]:
    """Profile out amplitude, then minimize heating-only squared residuals in tau."""
    selected = window(rows, 70, 350)
    points = [(time_s(row) - 60, row[column] - baseline) for row in selected]

    def evaluate(tau: float) -> tuple[float, float]:
        basis = [1 - math.exp(-t / tau) for t, _ in points]
        amplitude = sum(x * value for x, (_, value) in zip(basis, points, strict=True)) / sum(
            x * x for x in basis
        )
        sse = sum((value - amplitude * x) ** 2 for x, (_, value) in zip(basis, points, strict=True))
        return sse, amplitude

    lo, hi = bounds = 20.0, 1000.0
    ratio = (math.sqrt(5) - 1) / 2
    left, right = hi - ratio * (hi - lo), lo + ratio * (hi - lo)
    for _ in range(100):
        if evaluate(left)[0] < evaluate(right)[0]:
            hi, right = right, left
            left = hi - ratio * (hi - lo)
        else:
            lo, left = left, right
            right = lo + ratio * (hi - lo)
    tau = (lo + hi) / 2
    if any(abs(tau - bound) < 1e-6 for bound in bounds):
        raise ValueError("tau search ended at its bound; widen the search interval")
    sse, amplitude = evaluate(tau)
    return {
        "tau_s": tau,
        "asymptotic_rise_K": amplitude,
        "residual_rms_K": math.sqrt(sse / len(points)),
        "samples": len(points),
    }


def analyze(data_root: Path) -> dict:
    result = {}
    rows = read_dicts(data_root / "astronomy" / "greenhouse.example.csv")
    baseline, heating, cooling = window(rows, 0, 60), window(rows, 330, 360), window(rows, 540, 600)
    columns = ["Temperature 1 (°C)", "Temperature 2 (°C)"]
    initial = [average(baseline, col) for col in columns]
    late = [average(heating, col) for col in columns]
    result["greenhouse"] = {
        "files": ["astronomy/greenhouse.example.csv"],
        "time_column": "Time (min)",
        "time_to_seconds": 60,
        "columns": columns,
        "windows_s": {
            "baseline": [0, 60],
            "late_heating": [330, 360],
            "late_cooling": [540, 600],
            "fit": [70, 350],
        },
        "window_rule": (
            "start inclusive, end exclusive; minute timestamps converted "
            "then rounded to 6 decimal seconds"
        ),
        "sample_counts": [len(baseline), len(heating), len(cooling)],
        "baseline_mean_C": initial,
        "late_heating_mean_C": late,
        "late_heating_rise_K": [b - a for a, b in zip(initial, late, strict=True)],
        "baseline_difference_2_minus_1_K": initial[1] - initial[0],
        "late_heating_difference_2_minus_1_K": late[1] - late[0],
        "baseline_subtracted_late_heating_difference_K": (late[1] - late[0])
        - (initial[1] - initial[0]),
        "late_cooling_mean_C": [average(cooling, col) for col in columns],
        "fit_model": (
            "T(t)=baseline+A*(1-exp(-(t-60)/tau)); baseline fixed to mean on [0,60), "
            "linear amplitude profiled out and tau minimized on [20,1000] s"
        ),
        "fit": [fit_heating(rows, col, base) for col, base in zip(columns, initial, strict=True)],
        "switch_off_jump_K": [
            next(row[col] for row in rows if time_s(row) == 360)
            - next(row[col] for row in rows if time_s(row) == 359)
            for col in columns
        ],
    }

    rows = read_dicts(data_root / "astronomy" / "pt-star.example.csv")
    specs = {
        "baseline": [0, 30],
        "compressed": [55, 60],
        "later_compressed": [70, 85],
        "recovered": [150, 180],
    }
    states = {}
    for key, bounds in specs.items():
        selected = window(rows, *bounds)
        states[key] = {
            "samples": len(selected),
            "pressure_mean_hPa": average(selected, "Pressure (hPa)"),
            "die_temperature_mean_C": average(selected, "Temperature (°C)"),
        }
    p0 = states["baseline"]["pressure_mean_hPa"]
    p1 = states["compressed"]["pressure_mean_hPa"]
    result["pt-star"] = {
        "files": ["astronomy/pt-star.example.csv"],
        "time_column": "Time (min)",
        "time_to_seconds": 60,
        "columns": ["Pressure (hPa)", "Temperature (°C)"],
        "windows_s": specs,
        "window_rule": (
            "start inclusive, end exclusive; timestamps rounded to 6 decimal seconds "
            "after conversion"
        ),
        "states": states,
        "pressure_rise_hPa": p1 - p0,
        "die_temperature_rise_K": states["compressed"]["die_temperature_mean_C"]
        - states["baseline"]["die_temperature_mean_C"],
        "pressure_reduction_early_to_later_hPa": p1
        - states["later_compressed"]["pressure_mean_hPa"],
        "conditional_isothermal_volume_ratio": p0 / p1,
        "conditional_isothermal_volume_reduction_percent": 100 * (1 - p0 / p1),
        "conditional_model_note": (
            "V1/V0=p0/p1 requires a closed ideal gas at unchanged gas temperature; "
            "chamber volume and gas temperature are not CSV observables."
        ),
    }

    bmp = read_dicts(data_root / "astronomy" / "tidal-locking_bmp280.example.csv")
    ir = read_dicts(data_root / "astronomy" / "tidal-locking_tmp007.example.csv")
    light = read_dicts(data_root / "astronomy" / "tidal-locking_opt3001.example.csv")
    channel_specs = [
        ("bmp280", bmp, ["Temperature 1 (°C)", "Temperature 2 (°C)"]),
        ("tmp007_object", ir, ["Object temperature 1 (°C)", "Object temperature 2 (°C)"]),
        ("tmp007_die", ir, ["Ambient temperature 1 (°C)", "Ambient temperature 2 (°C)"]),
    ]
    thermal = {}
    for key, rows, columns in channel_specs:
        start = window(rows, 0, 30)
        end = window(rows, 180, 210)
        initial = [average(start, col) for col in columns]
        late = [average(end, col) for col in columns]
        thermal[key] = {
            "columns": columns,
            "sample_counts_baseline_late": [len(start), len(end)],
            "baseline_mean_C": initial,
            "late_heating_mean_C": late,
            "late_heating_rise_K": [b - a for a, b in zip(initial, late, strict=True)],
            "baseline_contrast_day_minus_night_K": initial[0] - initial[1],
            "late_heating_contrast_day_minus_night_K": late[0] - late[1],
            "baseline_subtracted_late_heating_contrast_K": (late[0] - late[1])
            - (initial[0] - initial[1]),
        }
    illuminated = window(light, 30, 210)
    eday = average(illuminated, "Illuminance 1 (lx)")
    enight = average(illuminated, "Illuminance 2 (lx)")
    result["tidal-locking"] = {
        "files": [
            "astronomy/tidal-locking_bmp280.example.csv",
            "astronomy/tidal-locking_tmp007.example.csv",
            "astronomy/tidal-locking_opt3001.example.csv",
        ],
        "time_column": "Time (s)",
        "windows_s": {"baseline": [0, 30], "late_heating": [180, 210], "illuminated": [30, 210]},
        "window_rule": "start inclusive, end exclusive, retain independent channel time grids",
        "thermal": thermal,
        "illuminated_samples": len(illuminated),
        "illuminance_mean_day_lx": eday,
        "illuminance_mean_night_lx": enight,
        "illuminance_ratio_of_means_day_to_night": eday / enight,
    }
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("data_root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    text = json.dumps(analyze(args.data_root), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
