"""Auxiliary thermal/astronomy reductions; original analyses remain unchanged."""

from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path


def read(data_root: Path, relative: str) -> list[list[float]]:
    """Read numeric columns without altering missing-value markers or clocks."""
    with (data_root / relative).open(encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream)
        next(reader)
        return [[float(value) for value in row] for row in reader]


def mean_window(
    rows: list[list[float]], column: int, start: float, stop: float, *, scale: float = 1
) -> float:
    return statistics.mean(row[column] for row in rows if start <= round(row[0] * scale, 6) < stop)


def saturation_pressure_kPa(temperature_K: float) -> float:
    """IAPWS SR1-86(1992), eq. 1; triple-point to critical-point domain."""
    if not 273.16 <= temperature_K <= 647.096:
        raise ValueError("Outside stable liquid-vapor saturation domain")
    theta = 1 - temperature_K / 647.096
    coefficients = (-7.85951783, 1.84408259, -11.7866497, 22.6807411, -15.9618719, 1.80122502)
    powers = (1, 1.5, 3, 3.5, 4, 7.5)
    polynomial = sum(a * theta**b for a, b in zip(coefficients, powers, strict=True))
    return 22064 * math.exp(647.096 / temperature_K * polynomial)


def saturation_temperature_K(pressure_kPa: float) -> float:
    """Invert the monotonic saturation-pressure relation by bounded bisection."""
    low, high = 273.16, 647.096
    if not saturation_pressure_kPa(low) <= pressure_kPa <= 22064:
        raise ValueError("Outside stable liquid-vapor saturation domain")
    for _ in range(80):
        middle = (low + high) / 2
        if saturation_pressure_kPa(middle) < pressure_kPa:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def analyze(data_root: Path) -> dict[str, dict]:
    """Return JSON-compatible extensions with explicit selection/physical assumptions."""
    result: dict[str, dict] = {}
    rows = read(data_root, "drafts/greenhouse-single.example.csv")
    baseline = mean_window(rows, 3, 0, 60)
    late = mean_window(rows, 3, 210, 240)
    edge = next(i for i, row in enumerate(rows) if row[0] >= 240)
    result["greenhouse"] = {
        "related_datasets": ["drafts/greenhouse-single.example.csv"],
        "auxiliary_windows_s": {"baseline": [0, 60], "late_heating": [210, 240]},
        "auxiliary_window_rule": (
            "receive time, lower inclusive/upper exclusive; no clock alignment to paired run"
        ),
        "baseline_die_C": baseline,
        "late_heating_die_C": late,
        "late_heating_rise_K": late - baseline,
        "mean_displayed_rise_K": mean_window(rows, 4, 210, 240),
        "display_reference_C": statistics.mean(row[3] - row[4] for row in rows),
        "display_reference_minus_measured_baseline_K": 22 - baseline,
        "switch_off_step_K": rows[edge][3] - rows[edge - 1][3],
        "switch_off_times_s": [rows[edge - 1][0], rows[edge][0]],
        "note": (
            "A finite-capacitance thermal model is continuous across a finite power step; do "
            "not fit through the observed jump."
        ),
    }

    rows = read(data_root, "drafts/pressure-boiling.example.csv")
    selected = [row for row in rows if row[3] == 1 and row[4] == 1]
    residuals = []
    for row in selected:
        predicted = saturation_temperature_K(row[1])
        derivative = (
            saturation_temperature_K(row[1] + row[5]) - saturation_temperature_K(row[1] - row[5])
        ) / (2 * row[5])
        residuals.append(
            {
                "observation_id": int(row[0]),
                "pressure_kPa": row[1],
                "liquid_temperature_C": row[2],
                "saturation_temperature_C": predicted - 273.15,
                "observed_minus_saturation_K": row[2] + 273.15 - predicted,
                "combined_standard_uncertainty_K": math.hypot(row[6], derivative * row[5]),
            }
        )
    result["mission-to-mars"] = {
        "related_datasets": ["drafts/pressure-boiling.example.csv"],
        "selection": (
            "checked pairs with observation code 1, sustained boiling; no time-series alignment"
        ),
        "all_pressure_range_kPa": [min(row[1] for row in rows), max(row[1] for row in rows)],
        "sustained_boiling": residuals,
        "residual_rms_K": math.sqrt(
            statistics.mean(row["observed_minus_saturation_K"] ** 2 for row in residuals)
        ),
        "triple_point_pressure_kPa": saturation_pressure_kPa(273.16),
        "representative_Mars_pressure_kPa": 0.636,
        "conditional_Mars_saturation_temperature_C": saturation_temperature_K(0.636) - 273.15,
        "lowest_observation_to_Mars_pressure_ratio": min(row[1] for row in rows) / 0.636,
        "BMP280_lower_limit_to_Mars_pressure_ratio": 30 / 0.636,
        "uncertainty_note": (
            "u(p)=0.1 kPa, u(T)=0.2 K treated as independent standard uncertainties; finite- "
            "difference sensitivity, no fitted calibration."
        ),
    }

    rows = read(data_root, "astronomy/pt-star.example.csv")
    p0 = mean_window(rows, 1, 0, 30, scale=60)
    p1 = mean_window(rows, 1, 55, 60, scale=60)
    p2 = mean_window(rows, 1, 70, 85, scale=60)
    t0 = mean_window(rows, 2, 0, 30, scale=60) + 273.15
    t1 = mean_window(rows, 2, 55, 60, scale=60) + 273.15
    t2 = mean_window(rows, 2, 70, 85, scale=60) + 273.15
    gamma = 1.4
    result["pt-star"] = {
        "datasets": ["astronomy/pt-star.example.csv"],
        "comparison_windows_s": {
            "baseline": [0, 30],
            "compressed": [55, 60],
            "later_compressed": [70, 85],
        },
        "comparison_window_rule": (
            "original minute clock converted to seconds and rounded to 6 decimals, lower "
            "inclusive/upper exclusive"
        ),
        "assumed_gamma": gamma,
        "pressure_ratio": p1 / p0,
        "conditional_isothermal_volume_ratio": p0 / p1,
        "conditional_reversible_adiabatic_volume_ratio": (p0 / p1) ** (1 / gamma),
        "conditional_adiabatic_gas_rise_K": t0 * ((p1 / p0) ** ((gamma - 1) / gamma) - 1),
        "die_substitution_volume_ratio": (p0 / p1) * (t1 / t0),
        "die_substitution_p_over_T_change_percent": 100 * ((p1 / t1) / (p0 / t0) - 1),
        "conditional_gas_cooling_at_fixed_V_n_K": t1 * (1 - p2 / p1),
        "observed_die_cooling_K": t1 - t2,
        "note": (
            "Only pressure and die temperature are observed; gas predictions assume initial "
            "gas temperature equals baseline die temperature. Path endpoints do not identify "
            "heat flow, leakage or piston motion."
        ),
    }

    rows = read(data_root, "drafts/seasons-obliquity_observations.example.csv")
    groups = []
    for tilt in (0, 23.5):
        for orbit in (0, 180):
            poles = [
                row
                for row in rows
                if row[9] == tilt and row[8] == orbit and abs(row[7]) == 60 and row[11] == 1
            ]
            south = next(row[14] for row in poles if row[7] == -60)
            north = next(row[14] for row in poles if row[7] == 60)
            groups.append(
                {
                    "tilt_deg": tilt,
                    "orbital_label_deg": orbit,
                    "south_relative": south,
                    "north_relative": north,
                    "north_minus_south": north - south,
                }
            )
    result["tidal-locking"] = {
        "related_datasets": ["drafts/seasons-obliquity_observations.example.csv"],
        "selection": (
            "enabled labeled observations at +/-60 deg; one value per geometry, distinct from "
            "thermal and lux records"
        ),
        "relative_definition": "(clear-dark)/(baseline-dark)",
        "groups": groups,
        "max_relative_reconstruction_error": max(
            abs((row[2] - row[12]) / (row[13] - row[12]) - row[14]) for row in rows
        ),
        "ideal_noon_north_south_ratio_for_declination_23_5_deg": math.cos(math.radians(60 - 23.5))
        / math.cos(math.radians(60 + 23.5)),
        "note": (
            "The labeled examples show almost symmetric hemispheres at both tilts and a "
            "strong orbital-label dependence already at zero tilt; unrecorded local "
            "orientation prevents attribution to obliquity."
        ),
    }
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("data_root", type=Path)
    arguments = parser.parse_args()
    print(json.dumps(analyze(arguments.data_root), indent=2, allow_nan=False))
