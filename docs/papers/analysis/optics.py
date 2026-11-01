"""Reproduce the three optical papers' numerical reductions from example CSVs."""

from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path


def read_rows(data_root: Path, relative: str) -> list[dict[str, float]]:
    with (data_root / relative).open(encoding="utf-8", newline="") as source:
        return [{key: float(value) for key, value in row.items()} for row in csv.DictReader(source)]


def select(
    rows: list[dict[str, float]], time_column: str, start: float, stop: float
) -> list[dict[str, float]]:
    # A tolerance keeps literal decimal boundaries stable after binary conversion.
    return [row for row in rows if start - 1e-9 <= row[time_column] < stop - 1e-9]


def describe(rows: list[dict[str, float]], column: str) -> dict[str, float]:
    values = [row[column] for row in rows]
    return {"mean": statistics.mean(values), "sample_sd": statistics.stdev(values)}


def analyze(data_root: Path) -> dict:
    light = read_rows(data_root, "core/light_plot_v1-2.example.csv")
    columns = list(light[0])
    baseline = [describe(select(light, columns[0], 0, 4), column)["mean"] for column in columns[1:]]
    light_result = {
        "columns": columns,
        "samples": len(light),
        "first_time": light[0][columns[0]],
        "last_time": light[-1][columns[0]],
        "dim_baseline_0_4": baseline,
        "plateaus": {},
    }
    windows = {
        "white": (6, 14),
        "red": (16, 24),
        "green": (26, 34),
        "blue": (36, 44),
        "saturation": (46, 49),
    }
    for name, (start, stop) in windows.items():
        rows = select(light, columns[0], start, stop)
        moments = [describe(rows, column) for column in columns[1:]]
        means = [moment["mean"] for moment in moments]
        net = [value - background for value, background in zip(means, baseline, strict=True)]
        light_result["plateaus"][name] = {
            "window_s": [start, stop],
            "n": len(rows),
            "means": means,
            "sample_sd": [moment["sample_sd"] for moment in moments],
            "dim_subtracted_RGB_fractions": [value / sum(net[1:]) for value in net[1:]],
            "clipped_all_fraction": statistics.mean(
                all(row[column] == 4100 for column in columns[1:]) for row in rows
            ),
        }

    albedo_result = {}
    for name in ("sensortag", "phone"):
        rows = read_rows(data_root, f"astronomy/albedo_{name}.example.csv")
        time_column, signal_column = list(rows[0])[:2]
        dark_rows = select(rows, time_column, 0, 7) + select(rows, time_column, 57, 60.5)
        dark = describe(dark_rows, signal_column)["mean"]
        reference = describe(select(rows, time_column, 9, 23), signal_column)["mean"]
        signals = [row[signal_column] for row in rows]
        result = {
            "n": len(rows),
            "dark_windows_s": [[0, 7], [57, 60.5]],
            "dark_mean": dark,
            "reference_window_s": [9, 23],
            "reference_mean": reference,
            "plateaus": {},
            "extrema_contrast_percent": 100 * (max(signals) - min(signals)) / max(signals),
        }
        for target, (start, stop) in {"grey": (25, 39), "black": (41, 55)}.items():
            moments = describe(select(rows, time_column, start, stop), signal_column)
            result["plateaus"][target] = {
                "window_s": [start, stop],
                "mean": moments["mean"],
                "sd": moments["sample_sd"],
                "ratio": (moments["mean"] - dark) / (reference - dark),
            }
        albedo_result[name] = result

    infrared = read_rows(data_root, "astronomy/ir-dist_habitable.example.csv")
    counts = [row["d (a.u.)"] for row in infrared]
    indicated = [row["T_IR (°C)"] for row in infrared]
    die = [row["T_amb (°C)"] for row in infrared]
    infrared_result = {
        "n": len(infrared),
        "time_s": [infrared[0]["Time (s)"], infrared[-1]["Time (s)"]],
        "mouse_count_range": [min(counts), max(counts)],
        "apparent_temperature_range_C": [min(indicated), max(indicated)],
        "die_temperature_mean_C": statistics.mean(die),
        "die_temperature_range_C": [min(die), max(die)],
        "plateaus": {},
    }
    windows = {
        "out_0.15m": (0, 1.5),
        "out_0.50m": (10.5, 12),
        "out_0.80m": (19.5, 21),
        "in_0.50m": (26.4, 27.3),
    }
    for name, (start, stop) in windows.items():
        rows = select(infrared, "Time (s)", start, stop)
        moments = describe(rows, "T_IR (°C)")
        infrared_result["plateaus"][name] = {
            "window_s": [start, stop],
            "n": len(rows),
            "mean_T_IR_C": moments["mean"],
            "mean_d_counts": statistics.mean(row["d (a.u.)"] for row in rows),
            "sample_sd_T_IR_C": moments["sample_sd"],
        }
    infrared_result["out_minus_return_at_1750_counts_K"] = (
        infrared_result["plateaus"]["out_0.50m"]["mean_T_IR_C"]
        - infrared_result["plateaus"]["in_0.50m"]["mean_T_IR_C"]
    )
    return {"light-rgb": light_result, "albedo": albedo_result, "ir-distance": infrared_result}


if __name__ == "__main__":
    import sys

    result = analyze(Path(sys.argv[1]))
    destination = Path(__file__).with_name("metrics.json")
    destination.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(destination)
