"""Independent auxiliary reductions for the seven original core manuscripts.

All time windows are left closed and right open. Independent examples retain
separate clocks; no row-wise comparison between instruments is performed.
"""

from __future__ import annotations

import json
import math
import statistics as stats
from pathlib import Path

from _common import ols, read_lists, window


def mean(rows: list[list[float]], column: int) -> float:
    return stats.mean(row[column] for row in rows)


def slope(rows: list[list[float]], x: int, y: int) -> float:
    return ols([r[x] for r in rows], [r[y] for r in rows])[0]


def integral(rows: list[list[float]], column: int) -> float:
    return sum((b[0] - a[0]) * (a[column] + b[column]) / 2 for a, b in zip(rows, rows[1:]))


def vapour(rows: list[list[float]], temperature: int, humidity: int) -> dict:
    # Transform paired channels before averaging: mean p_v differs from p_v(means).
    values = [
        r[humidity] / 100 * 610.94 * math.exp(17.625 * r[temperature] / (r[temperature] + 243.04))
        for r in rows
    ]
    return {
        "n": len(rows),
        "mean_temperature_C": mean(rows, temperature),
        "mean_RH_percent": mean(rows, humidity),
        "mean_vapour_pressure_Pa": stats.mean(values),
        "method": "paired-channel Magnus transform, then arithmetic mean",
    }


def analyze(data_root: Path) -> dict[str, dict]:
    accel = read_lists(data_root / "drafts/cc2541-accelerometer.example.csv")
    accel_step = slope(accel, 1, 4)
    flat = window(accel, 0, 8)
    gyro = read_lists(data_root / "core/gyroscope_plot_v1-2.example.csv")
    gyro_turn = window(gyro, 9, 29)
    ccgyro = read_lists(data_root / "drafts/cc2541-gyroscope.example.csv")
    mag = read_lists(data_root / "drafts/magnetic-current.example.csv")
    mag_slope = slope(mag, 5, 3)
    mag_intercept = mean(mag, 3) - mag_slope * mean(mag, 5)
    boiling = read_lists(data_root / "drafts/pressure-boiling.example.csv")
    out_of_range = [r for r in boiling if not 26 <= r[1] <= 126]
    hts = read_lists(data_root / "core/temperature_plot_v1-2.example.csv")
    hdc = read_lists(data_root / "drafts/sensortag-environmental_humidity.example.csv")
    sht = read_lists(data_root / "drafts/cc2541-humidity.example.csv")
    rgb = read_lists(data_root / "drafts/rgb-filter-transmission.example.csv")
    uv = read_lists(data_root / "drafts/uv-transmission_observations.example.csv")
    valid_uv = [r for r in uv if r[3] == 1 and 0 < r[2] < r[1] < 1023 and r[2] <= r[9] < 1023]
    uv_result = []
    for r in valid_uv:
        ratio = (r[9] - r[2]) / (r[1] - r[2])
        uv_result.append(
            {
                "observation_id": int(r[0]),
                "sample_count": r[9],
                "dark_count": r[2],
                "reference_count": r[1],
                "transmission": ratio,
                "uncorrected_count_ratio": r[9] / r[1],
                "reported_ratio_residual": ratio - r[12],
            }
        )
    result = {
        "accelerometer": {
            "auxiliary_dataset": "drafts/cc2541-accelerometer.example.csv",
            "code_step_m_s2": accel_step,
            "local_small_angle_code_step_degree": math.degrees(accel_step / 9.80665),
            "nominal_nano_step_m_s2": 0.122e-3 * 9.80665,
            "step_ratio_cc2541_to_nano": accel_step / (0.122e-3 * 9.80665),
            "flat_window_s": [0, 8],
            "flat_samples": len(flat),
            "flat_x_unique_codes": len({r[1] for r in flat}),
            "flat_x_sd_m_s2": stats.stdev(r[4] for r in flat),
            "flat_mean_norm_m_s2": mean(flat, 7),
            "method": "OLS corrected x versus packet x over complete record; no time alignment",
        },
        "gyroscope": {
            "window_s": [9, 29],
            "actual_endpoints_s": [gyro_turn[0][0], gyro_turn[-1][0]],
            "signed_z_integral_degree": integral(gyro_turn, 3),
            "norm_integral_degree": integral(gyro_turn, 4),
            "method": "trapezoidal integration on timestamps; indicated, uncorrected Nano rates",
            "auxiliary_dataset": "drafts/cc2541-gyroscope.example.csv",
            "cc2541_step_rad_s": slope(ccgyro, 1, 4),
            "cc2541_final_z_mean_degree_s": math.degrees(mean(window(ccgyro, 55, 60), 6)),
        },
        "magnetometer": {
            "auxiliary_dataset": "drafts/magnetic-current.example.csv",
            "Bz_vs_derived_current_slope_uT_A": mag_slope,
            "Bz_vs_derived_current_intercept_uT": mag_intercept,
            "maximum_affine_residual_uT": max(
                abs(r[3] - mag_intercept - mag_slope * r[5]) for r in mag
            ),
            "current_error_per_1uT_background_shift_A": 1 / mag_slope,
            "method": "OLS full record; current derives from Bz, not an independent reference",
        },
        "pressure": {
            "auxiliary_dataset": "drafts/pressure-boiling.example.csv",
            "observation_count": len(boiling),
            "pressure_range_kPa": [min(r[1] for r in boiling), max(r[1] for r in boiling)],
            "outside_lps22hb_range_ids": [int(r[0]) for r in out_of_range],
            "boiling_observation_count": sum(r[3] == 1 for r in boiling),
            "boiling_outside_lps22hb_count": sum(r[3] == 1 for r in out_of_range),
            "method": "classify all observations against 26--126 kPa range, irrespective of phase",
        },
        "temperature-humidity": {
            "hts_baseline_20_30s": vapour(window(hts, 20, 30), 1, 2),
            "hts_warming_90_96s": vapour(window(hts, 90, 96), 1, 2),
            "hdc_baseline_0_25s": vapour(window(hdc, 0, 25), 2, 1),
            "hdc_pulse_45_60s": vapour(window(hdc, 45, 60), 2, 1),
            "sht_baseline_0_20s": vapour(window(sht, 0, 20), 5, 4),
            "auxiliary_datasets": [
                "drafts/sensortag-environmental_humidity.example.csv",
                "drafts/cc2541-humidity.example.csv",
            ],
            "method": "independent receive clocks; paired T and RH within each sensor only",
        },
        "light-rgb": {
            "auxiliary_dataset": "drafts/rgb-filter-transmission.example.csv",
            "local_red_window_s": [14.8, 15.2],
            "local_red_RGB_transmissions": [mean(window(rgb, 14.8, 15.2), i) for i in (7, 8, 9)],
            "local_blue_window_s": [34.8, 35.2],
            "local_blue_RGB_transmissions": [mean(window(rgb, 34.8, 35.2), i) for i in (7, 8, 9)],
            "method": "mean dark/reference-normalized transmission in local device-time windows",
        },
        "analog-inputs": {
            "auxiliary_datasets": ["drafts/uv-transmission_observations.example.csv"],
            "valid_observations": uv_result,
            "method": "independent sample-minus-dark / reference-minus-dark; checked linear pairs",
        },
    }

    thermal = result["temperature-humidity"]
    thermal["hts_warming_vapour_change_percent"] = 100 * (
        thermal["hts_warming_90_96s"]["mean_vapour_pressure_Pa"]
        / thermal["hts_baseline_20_30s"]["mean_vapour_pressure_Pa"]
        - 1
    )
    result["light-rgb"]["max_reported_transmission_residual"] = max(
        abs(r[6 + i] - (r[2 + i] - dark) / (reference - dark))
        for r in rgb
        for i, (dark, reference) in enumerate(zip((3, 2, 2, 1), (1800, 900, 1050, 620)))
    )
    return result


if __name__ == "__main__":
    import sys

    print(json.dumps(analyze(Path(sys.argv[1])), ensure_ascii=False, indent=2))
