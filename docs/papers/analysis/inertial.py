"""Reproduce the inertial-paper example reductions from the original CSVs.

Only the Python standard library is required. Windows use a closed left
endpoint and open right endpoint. Sample SD uses N-1; missing values are
excluded per channel without deleting their timestamps from the source.
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

from _common import read_dicts
from _common import window as rows_in_window

WINDOWS = {
    "accelerometer": {
        "baseline": (0, 8),
        "positive_tilt": (16, 19),
        "negative_tilt": (26, 29),
        "quarter_turn": (46, 49),
        "tap_sequence": (33, 38),
    },
    "gyroscope": {
        "baseline": (0, 7),
        "positive_yaw": (11, 17),
        "negative_yaw": (21, 27),
        "positive_roll": (31, 37),
        "negative_pitch": (41, 47),
        "final_baseline": (52, 59),
    },
    "magnetometer": {
        "baseline": (0, 8),
        "reoriented": (22, 28),
        "magnet_approach": (29, 40),
        "final_baseline": (52, 59),
    },
}


def analyze(data_root: Path) -> dict:
    """Read the three core files under data_root and return all reductions."""
    result = {}
    time_column = "Time t (s)"
    for slug, windows in WINDOWS.items():
        relative_path = Path("core") / f"{slug}_plot_v1-2.example.csv"
        rows = read_dicts(data_root / relative_path)
        columns = list(rows[0])
        summary = {
            "file": str(relative_path),
            "n": len(rows),
            "columns": columns,
            "time_end": rows[-1][time_column],
            "median_dt": statistics.median(
                right[time_column] - left[time_column] for left, right in zip(rows, rows[1:])
            ),
            "windows": {},
        }
        for name, (lower, upper) in windows.items():
            selected = rows_in_window(rows, lower, upper, time_column)
            window = {
                "interval_s": [lower, upper],
                "closed": "left",
                "n": len(selected),
                "statistics": {},
            }
            for column in columns[1:]:
                values = [row[column] for row in selected if math.isfinite(row[column])]
                window["statistics"][column] = {
                    "n_valid": len(values),
                    "mean": statistics.mean(values),
                    "sample_sd": statistics.stdev(values),
                    "min": min(values),
                    "max": max(values),
                }
            summary["windows"][name] = window
        summary["missing_rows"] = [
            index
            for index, row in enumerate(rows)
            if any(not math.isfinite(value) for value in row.values())
        ]
        magnitude_column = columns[4]
        peak = max(
            (row for row in rows if math.isfinite(row[magnitude_column])),
            key=lambda row: row[magnitude_column],
        )
        summary["peak"] = {
            "time_s": peak[time_column],
            "column": magnitude_column,
            "value": peak[magnitude_column],
        }
        if slug == "gyroscope":
            z_column = "Angular Velocity z (deg/s)"
            positive = summary["windows"]["positive_yaw"]["statistics"][z_column]["mean"]
            negative = summary["windows"]["negative_yaw"]["statistics"][z_column]["mean"]
            summary["reversal"] = {
                "reported_positive_mean_dps": positive,
                "reported_negative_mean_dps": negative,
                "bias_dps": (positive + negative) / 2,
                "slope_for_nominal_45_dps": (positive - negative) / 90,
                "nominal_library_slope": (2000 / 32768) / 0.070,
                "nominal_correction_factor": 0.070 / (2000 / 32768),
            }
        result[slug] = summary
    return result


if __name__ == "__main__":
    source_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("example-data")
    print(json.dumps(analyze(source_root), indent=2, ensure_ascii=False))
