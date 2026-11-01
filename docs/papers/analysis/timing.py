"""Reproduce short-paper reductions of the six timing/pressure example CSVs."""

from __future__ import annotations

import csv
import json
import statistics as stats
from pathlib import Path

from _common import in_window


def read(data_root: Path, name: str) -> tuple[list[str], list[dict[str, str]]]:
    with (data_root / "astronomy" / name).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def mean_window(t: list[float], y: list[float], a: float, b: float) -> float:
    return stats.mean(v for ti, v in zip(t, y) if in_window(ti, a, b))


def slope(t: list[float], y: list[float], a: float, b: float) -> float:
    xy = [(ti, yi) for ti, yi in zip(t, y) if in_window(ti, a, b)]
    tm, ym = stats.mean(x for x, _ in xy), stats.mean(y for _, y in xy)
    return sum((x - tm) * (y - ym) for x, y in xy) / sum((x - tm) ** 2 for x, _ in xy)


def analyze(data_root: Path) -> dict:
    result = {"mission-to-mars": {}, "owon-interface": {}, "transit-method": {}}
    for path in ("sensortag", "phone"):
        name = f"missiontomars_{path}.example.csv"
        fields, rows = read(data_root, name)
        t = [float(r[fields[0]]) for r in rows]
        y = [float(r[fields[1]]) for r in rows]
        baseline = mean_window(t, y, 0, 15)
        early = mean_window(t, y, 30, 35)
        late = mean_window(t, y, 50, 55)
        result["mission-to-mars"][path] = {
            "file": f"astronomy/{name}",
            "time_column": fields[0],
            "signal_column": fields[1],
            "rows": len(t),
            "median_dt_s": stats.median(b - a for a, b in zip(t, t[1:])),
            "baseline_window_s": [0, 15],
            "baseline_hpa": baseline,
            "early_window_s": [30, 35],
            "early_excess_hpa": early - baseline,
            "late_window_s": [50, 55],
            "late_excess_hpa": late - baseline,
            "early_to_late_drop_hpa": early - late,
            "slope_window_s": [30, 55],
            "ols_slope_hpa_per_s": slope(t, y, 30, 55),
            "range_hpa": max(y) - min(y),
            "final_window_s": [90, 120],
            "final_minus_initial_hpa": mean_window(t, y, 90, 120) - baseline,
        }

    name = "owon_digital_multimeter-debug.example.csv"
    fields, rows = read(data_root, name)
    t = [float(r[fields[0]]) for r in rows]
    y = [float(r[fields[1]]) for r in rows]
    d = {0: 1, 1: 1e-3, 2: 1e-2, 4: 1e-1}
    u = {0: 1, 16: 1e6, 32: 1e3, 64: 1e-3, 128: 1e-6}
    decoded = [float(r[fields[2]]) * d[int(r[fields[3]])] * u[int(r[fields[4]])] for r in rows]
    steps = []
    for a, nominal in ((0, 0), (10, 1), (20, 1.5), (30, 2), (40, -1), (50, 0.5)):
        vals = [yi for ti, yi in zip(t, y) if a + 1 <= ti < a + 9]
        steps.append(
            {
                "window_s": [a + 1, a + 9],
                "nominal_v": nominal,
                "n": len(vals),
                "mean_v": stats.mean(vals),
                "sd_v": stats.stdev(vals),
                "mean_minus_nominal_mv": 1e3 * (stats.mean(vals) - nominal),
            }
        )
    xs = [s["nominal_v"] for s in steps]
    ys = [s["mean_v"] for s in steps]
    xm, ym = stats.mean(xs), stats.mean(ys)
    gain = sum((x - xm) * (v - ym) for x, v in zip(xs, ys)) / sum((x - xm) ** 2 for x in xs)
    offset = ym - gain * xm
    result["owon-interface"] = {
        "file": f"astronomy/{name}",
        "rows": len(rows),
        "median_dt_s": stats.median(b - a for a, b in zip(t, t[1:])),
        "decoder": "float(raw numeric)*d[decimal code]*u[unit code]",
        "max_abs_decoder_residual_v": max(abs(a - b) for a, b in zip(decoded, y)),
        "negative_rows": sum(yi < 0 for yi in y),
        "steps": steps,
        "plateau_fit": {
            "model": "mean_v = offset + gain * nominal_v",
            "gain": gain,
            "offset_v": offset,
            "maximum_absolute_residual_mv": 1e3
            * max(abs(v - (offset + gain * x)) for x, v in zip(xs, ys)),
        },
    }

    for path in ("sensortag", "phone", "owon"):
        name = f"transitmethode_{path}.example.csv"
        fields, rows = read(data_root, name)
        t = [float(r[fields[0]]) for r in rows]
        y = [float(r[fields[1]]) for r in rows]
        events = []
        for center in (22, 52, 82):
            baseline = stats.mean(yi for ti, yi in zip(t, y) if 3 <= abs(ti - center) < 6)
            floor = stats.mean(yi for ti, yi in zip(t, y) if abs(ti - center) <= 1)
            below = [
                (ti, yi) for ti, yi in zip(t, y) if abs(ti - center) < 3 and yi / baseline < 0.98
            ]
            onset = below[0][0]
            end = next(ti for ti, yi in zip(t, y) if ti > below[-1][0] and yi / baseline >= 0.98)
            events.append(
                {
                    "center_s": center,
                    "baseline_window_abs_offset_s": [3, 6],
                    "plateau_window_abs_offset_s": [0, 1],
                    "baseline": baseline,
                    "plateau_mean": floor,
                    "depth_fraction": 1 - floor / baseline,
                    "threshold_fraction": 0.98,
                    "onset_s": onset,
                    "end_s": end,
                    "threshold_duration_s": end - onset,
                    "samples_within_nominal_four_s_event": sum(abs(ti - center) < 2 for ti in t),
                }
            )
        onsets = [e["onset_s"] for e in events]
        result["transit-method"][path] = {
            "file": f"astronomy/{name}",
            "time_column": fields[0],
            "signal_column": fields[1],
            "rows": len(t),
            "median_dt_s": stats.median(b - a for a, b in zip(t, t[1:])),
            "events": events,
            "mean_depth_fraction": stats.mean(e["depth_fraction"] for e in events),
            "global_extrema_depth_fraction": (max(y) - min(y)) / max(y),
            "onset_intervals_s": [b - a for a, b in zip(onsets, onsets[1:])],
            "mean_onset_interval_s": (onsets[-1] - onsets[0]) / 2,
            "mean_threshold_duration_s": stats.mean(e["threshold_duration_s"] for e in events),
        }
    return result


if __name__ == "__main__":
    import sys

    data = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "example-data"
    print(json.dumps(analyze(data), indent=2))
