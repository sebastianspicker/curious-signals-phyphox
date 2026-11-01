"""Auxiliary optical reductions; retain all original paper analyses unchanged."""

from __future__ import annotations

import json
import math
import statistics as st
from pathlib import Path

from _common import read_dicts, window


def mean(rows, column):
    return st.fmean(row[column] for row in rows)


def linear_fit(x, y):
    xm, ym = st.fmean(x), st.fmean(y)
    slope = sum((a - xm) * (b - ym) for a, b in zip(x, y, strict=True)) / sum(
        (a - xm) ** 2 for a in x
    )
    intercept = ym - slope * xm
    residual = [b - intercept - slope * a for a, b in zip(x, y, strict=True)]
    return {
        "slope": slope,
        "intercept": intercept,
        "residual_rms": math.sqrt(st.fmean(v * v for v in residual)),
    }


def analyze(data_root: Path) -> dict[str, dict]:
    result = {slug: {} for slug in ("albedo", "transit-method", "owon-interface", "ir-distance")}
    rgb = read_dicts(data_root / "drafts/rgb-filter-transmission.example.csv")
    channels = [f"{name} (counts)" for name in ("clear", "red", "green", "blue")]
    dark = [mean(window(rgb, 56, 60, "device_t (s)"), col) for col in channels]
    reference = [mean(window(rgb, 4, 6, "device_t (s)"), col) for col in channels]
    late = [mean(window(rgb, 44, 46, "device_t (s)"), col) for col in channels]
    ratios = {}
    for name, bounds in {"red": (14, 16), "green": (24, 26), "blue": (34, 36)}.items():
        rows = window(rgb, *bounds, "device_t (s)")
        values = [mean(rows, col) for col in channels]
        ratios[name] = {
            "device_window_s": list(bounds),
            "n": len(rows),
            "mean_counts": values,
            "ratios": [(v - d) / (r - d) for v, d, r in zip(values, dark, reference, strict=True)],
        }
    result["albedo"] = {
        "auxiliary_dataset": "drafts/rgb-filter-transmission.example.csv",
        "channel_order": channels,
        "dark_window_s": [56, 60],
        "reference_window_s": [4, 6],
        "late_reference_window_s": [44, 46],
        "dark_counts": dark,
        "reference_counts": reference,
        "later_reference_change_percent": [
            100 * (b - a) / (a - d) for a, b, d in zip(reference, late, dark, strict=True)
        ],
        "selected_windows": ratios,
        "method": (
            "Ratios of window means after covered-detector subtraction; "
            "fixed initial reference, device clock. Smooth transitions remain; "
            "no plateau-equilibrium assumption."
        ),
    }

    photometry = {}
    for slug in ("nano-transit", "exomoon-photometry", "starspot-crossing", "eclipsing-binary"):
        rows = read_dicts(data_root / f"drafts/{slug}.example.csv")
        tc = "receive_time"
        baseline_windows = (
            [(2, 15), (95, 118)] if slug != "eclipsing-binary" else [(2, 12), (40, 44), (100, 104)]
        )
        baseline_rows = [row for a, b in baseline_windows for row in window(rows, a, b, tc)]
        baseline = mean(baseline_rows, "clear")
        dark = 10.0
        specs = {
            "nano-transit": {"event1": [(19, 21)], "event2": [(49, 51)], "event3": [(79, 81)]},
            "exomoon-photometry": {
                "planet": [(22, 33), (77, 88)],
                "separated": [(37, 48), (62, 73)],
                "overlap": [(52, 58)],
            },
            "starspot-crossing": {"adjacent": [(45, 49), (55, 59)], "crossing": [(50, 54)]},
            "eclipsing-binary": {
                "primary": [(19, 21), (49, 51), (79, 81), (109, 111)],
                "secondary": [(34, 36), (64, 66), (94, 96)],
            },
        }[slug]
        states = {}
        for name, bounds in specs.items():
            selected = [row for a, b in bounds for row in window(rows, a, b, tc)]
            value = mean(selected, "clear")
            states[name] = {
                "receive_windows_s": bounds,
                "n": len(selected),
                "mean_clear_counts": value,
                "conditional_depth": (baseline - value) / (baseline - dark),
            }
        info = {
            "auxiliary_dataset": f"drafts/{slug}.example.csv",
            "baseline_receive_windows_s": baseline_windows,
            "baseline_mean_clear_counts": baseline,
            "assumed_dark_counts": dark,
            "states": states,
            "median_receive_spacing_s": st.median(b[tc] - a[tc] for a, b in zip(rows, rows[1:])),
            "method": (
                "Raw clear-channel means on receive clock; dark fixed at "
                "example's entered 10 counts, not independently measured. "
                "Device clock remains separate."
            ),
        }
        if slug == "nano-transit":
            info["mean_conditional_depth"] = st.fmean(
                v["conditional_depth"] for v in states.values()
            )
            info["conditional_projected_radius_ratio"] = math.sqrt(info["mean_conditional_depth"])
        elif slug == "exomoon-photometry":
            info["extra_depth"] = (
                states["planet"]["mean_clear_counts"] - states["separated"]["mean_clear_counts"]
            ) / (baseline - dark)
            info["overlap_brightening"] = (
                states["overlap"]["mean_clear_counts"] - states["separated"]["mean_clear_counts"]
            ) / (baseline - dark)
        elif slug == "starspot-crossing":
            info["anomaly"] = (
                states["crossing"]["mean_clear_counts"] - states["adjacent"]["mean_clear_counts"]
            ) / (baseline - dark)
        photometry[slug] = info
    result["transit-method"] = photometry

    analog = read_dicts(data_root / "core/analog_input_plot_v1-2.example.csv")
    result["owon-interface"] = {
        "auxiliary_dataset": "core/analog_input_plot_v1-2.example.csv",
        "display_mV_per_count": 3.226,
        "maximum_scale_residual_mV": max(
            abs(row[f"Voltage at A{i} (mV)"] - 3.226 * row[f"Analog Input A{i}"])
            for row in analog
            for i in range(3)
        ),
        "ideal_3V3_10bit_mV_per_bin": 3300 / 1024,
        "Owon_example_V_per_digit": 0.001,
        "nominal_bin_ratio_ADC_to_Owon": 3.226,
        "conditional_1V_B35_specification_limit_mV": 1000 * (0.005 * 1 + 2 * 0.001),
        "method": (
            "Exact conversion consistency across all three raw-count channels; "
            "numerical resolution comparison only; B35 manufacturer limit "
            "at 1 V on 6.000 V range."
        ),
    }

    obs = read_dicts(data_root / "drafts/illuminance-distance-manual_observations.example.csv")
    distance = [row["Entered ruler distance (m)"] for row in obs]
    corrected = [row["Background-corrected signal (counts)"] for row in obs]
    products = [s * r * r for s, r in zip(corrected, distance, strict=True)]
    fit = linear_fit([math.log(r) for r in distance], [math.log(s) for s in corrected])
    branches = []
    for selected in (slice(0, 6), slice(6, 12)):
        branches.append(
            linear_fit(
                [math.log(r) for r in distance[selected]],
                [math.log(s) for s in corrected[selected]],
            )
        )
    result["ir-distance"] = {
        "auxiliary_dataset": "drafts/illuminance-distance-manual_observations.example.csv",
        "distance_range_m": [min(distance), max(distance)],
        "n_captures": len(obs),
        "background_counts": 10,
        "maximum_subtraction_residual_counts": max(
            abs(
                row["Captured clear signal (counts)"]
                - 10
                - row["Background-corrected signal (counts)"]
            )
            for row in obs
        ),
        "log_log_fit": fit,
        "outward_return_log_log_fits": branches,
        "signal_times_r2_mean_count_m2": st.fmean(products),
        "signal_times_r2_range_count_m2": [min(products), max(products)],
        "signal_times_r2_relative_sample_sd_percent": 100 * st.stdev(products) / st.fmean(products),
        "endpoint_power_exponent": math.log(
            (corrected[0] + corrected[-1]) / (corrected[5] + corrected[6])
        )
        / math.log(distance[0] / distance[5]),
        "method": (
            "OLS ln(background-corrected clear counts) against "
            "ln(entered ruler distance), all 12 captures; each direction also fit "
            "separately. No interpolation or clock alignment with IR data; "
            "fit scatter is not total uncertainty."
        ),
    }
    return result


if __name__ == "__main__":
    import sys

    print(json.dumps(analyze(Path(sys.argv[1])), indent=2))
