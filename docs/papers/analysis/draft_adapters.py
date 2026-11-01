"""Reproduce the ten adapter-paper reductions using independent receive clocks.

Intervals are left-closed/right-open. Sample SD describes within-window scatter,
not standard error; no independence between successive rows is assumed.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics as st
from pathlib import Path

from _common import draft_rows as read
from _common import window

SLUGS = (
    "greenhouse-single",
    "sensortag-environmental",
    "puck-light",
    "cc2541-accelerometer",
    "cc2541-gyroscope",
    "cc2541-magnetometer",
    "cc2541-humidity",
    "cc2541-pressure",
    "cc2541-ir-temperature",
    "pocketlab-gyroscope",
)


def stats(rows: list[list[float]], column: int, low: float, high: float) -> dict:
    chosen = window(rows, low, high)
    values = [r[column] for r in chosen if math.isfinite(r[column])]
    return {
        "window_s": [low, high],
        "closed": "left",
        "n": len(values),
        "mean": st.mean(values),
        "sd": st.stdev(values) if len(values) > 1 else None,
        "min": min(values),
        "max": max(values),
    }


def linear(xs: list[float], ys: list[float]) -> dict:
    pairs = [(x, y) for x, y in zip(xs, ys) if math.isfinite(x) and math.isfinite(y)]
    xx, yy = zip(*pairs)
    xm, ym = st.mean(xx), st.mean(yy)
    slope = sum((x - xm) * (y - ym) for x, y in pairs) / sum((x - xm) ** 2 for x in xx)
    offset = ym - slope * xm
    return {
        "slope": slope,
        "intercept": offset,
        "rms_residual": math.sqrt(st.mean((y - offset - slope * x) ** 2 for x, y in pairs)),
    }


def integral(
    rows: list[list[float]],
    column: int,
    low: float,
    high: float,
    bias: float = 0,
    absolute: bool = False,
) -> float:
    selected = window(rows, low, high)
    value = 0.0
    for a, b in zip(selected, selected[1:]):
        ya, yb = a[column] - bias, b[column] - bias
        if math.isfinite(ya) and math.isfinite(yb):
            if absolute:
                ya, yb = abs(ya), abs(yb)
            value += (b[0] - a[0]) * (ya + yb) / 2
    return value


def vapor_pressure(temp_C: float, rh_pct: float) -> float:
    return rh_pct * 0.01 * 6.1094 * math.exp(17.625 * temp_C / (temp_C + 243.04))


def heating_fit(rows: list[list[float]]) -> dict:
    baseline = stats(rows, 3, 0, 55)["mean"]
    chosen = window(rows, 65, 235)

    def fit(tau: float) -> tuple[float, float]:
        basis = [1 - math.exp(-(r[0] - 60) / tau) for r in chosen]
        amplitude = sum(x * (r[3] - baseline) for x, r in zip(basis, chosen)) / sum(
            x * x for x in basis
        )
        loss = st.mean((r[3] - baseline - amplitude * x) ** 2 for x, r in zip(basis, chosen))
        return loss, amplitude

    low, high = 20.0, 500.0
    for _ in range(100):
        a, b = low + (high - low) / 3, high - (high - low) / 3
        if fit(a)[0] < fit(b)[0]:
            high = b
        else:
            low = a
    tau = (low + high) / 2
    loss, amplitude = fit(tau)
    return {
        "window_s": [65, 235],
        "onset_s": 60,
        "baseline_C": baseline,
        "amplitude_K": amplitude,
        "tau_s": tau,
        "rms_K": math.sqrt(loss),
        "method": (
            "Fixed measured baseline; least-squares amplitude for each positive tau; "
            "ternary search."
        ),
    }


def analyze(data_root: Path) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for slug in SLUGS:
        if slug == "sensortag-environmental":
            continue
        rows = read(data_root, slug)
        result[slug] = {
            "datasets": ["drafts/" + slug + ".example.csv"],
            "rows": len(rows),
            "time_unit": "s",
            "median_receive_interval_s": st.median(b[0] - a[0] for a, b in zip(rows, rows[1:])),
            "method": (
                "Finite per-channel values; left-closed/right-open receive-time windows; sample SD."
            ),
        }
    r = read(data_root, "greenhouse-single")
    g = result["greenhouse-single"]
    g.update(
        baseline=stats(r, 3, 0, 55),
        early=stats(r, 3, 90, 120),
        late=stats(r, 3, 210, 235),
        end=stats(r, 3, 280, 300),
        heating_fit=heating_fit(r),
    )
    g["exported_minus_measured_baseline_K"] = stats(r, 4, 0, 55)["mean"]
    g["rise_late_K"] = g["late"]["mean"] - g["baseline"]["mean"]
    adjacent = max(zip(r, r[1:]), key=lambda ab: ab[1][3] - ab[0][3])
    g["largest_upward_step"] = {
        "times_s": [adjacent[0][0], adjacent[1][0]],
        "delta_K": adjacent[1][3] - adjacent[0][3],
    }
    h, b = (
        read(data_root, "sensortag-environmental_humidity"),
        read(data_root, "sensortag-environmental_barometer"),
    )
    e = [[x[0], vapor_pressure(x[2], x[1])] for x in h]
    paired = [(x, min(b, key=lambda y: abs(y[0] - x[0]))) for x in h]
    paired = [(x, y) for x, y in paired if abs(y[0] - x[0]) <= 0.5]
    result["sensortag-environmental"] = {
        "datasets": [
            "drafts/sensortag-environmental_humidity.example.csv",
            "drafts/sensortag-environmental_barometer.example.csv",
        ],
        "rows_humidity": len(h),
        "rows_barometer": len(b),
        "pairing_tolerance_s": 0.5,
        "median_pair_offset_s": st.median(y[0] - x[0] for x, y in paired),
        "paired_rows": len(paired),
        "method": (
            "Native windows on each clock. Nearest-neighbour temperature diagnostic "
            "only within 0.5s. Magnus vapor pressure from simultaneous HDC T/RH."
        ),
        "baseline_RH": stats(h, 1, 0, 25),
        "humid_RH": stats(h, 1, 40, 60),
        "recovered_RH": stats(h, 1, 85, 115),
        "baseline_hdc_C": stats(h, 2, 0, 25),
        "humid_hdc_C": stats(h, 2, 40, 60),
        "recovered_hdc_C": stats(h, 2, 85, 115),
        "baseline_bmp_C": stats(b, 2, 0, 25),
        "humid_bmp_C": stats(b, 2, 40, 60),
        "baseline_vapor_hPa": stats(e, 1, 0, 25),
        "humid_vapor_hPa": stats(e, 1, 40, 60),
        "recovered_vapor_hPa": stats(e, 1, 85, 115),
        "pressure_hPa": stats(b, 1, 0, 121),
        "baseline_T_difference_K": st.mean(y[2] - x[2] for x, y in paired if 0 <= x[0] < 25),
    }
    r = read(data_root, "puck-light")
    p = result["puck-light"]
    for name, lo, hi in [
        ("dark_before", 1, 9),
        ("reference_before", 12, 18),
        ("sample", 24, 36),
        ("reference_after", 42, 48),
        ("dark_after", 52, 59),
    ]:
        p[name] = stats(r, 2, lo, hi)
    d = (p["dark_before"]["mean"] + p["dark_after"]["mean"]) / 2
    ref = (p["reference_before"]["mean"] + p["reference_after"]["mean"]) / 2
    p.update(
        dark_estimate=d,
        reference_estimate=ref,
        ratio_reestimated=(p["sample"]["mean"] - d) / (ref - d),
        ratio_exported=stats(r, 4, 24, 36),
        dark_shift=p["dark_after"]["mean"] - p["dark_before"]["mean"],
        reference_shift=p["reference_after"]["mean"] - p["reference_before"]["mean"],
        negative_ratio_count=sum(rw[4] < 0 for rw in r if math.isfinite(rw[4])),
    )
    p["receive_vs_device_fit"] = linear([x[1] - r[0][1] for x in r], [x[0] for x in r])
    r = read(data_root, "cc2541-accelerometer")
    a = result["cc2541-accelerometer"]
    for name, lo, hi in [
        ("flat", 0, 8),
        ("positive", 16, 19),
        ("negative", 26, 29),
        ("roll", 46, 49),
        ("returned", 56, 60),
    ]:
        a[name] = {
            axis: stats(r, c, lo, hi) for axis, c in [("x", 4), ("y", 5), ("z", 6), ("norm", 7)]
        }
    a["tilt_deg"] = {
        name: math.degrees(math.atan2(a[name]["x"]["mean"], a[name]["z"]["mean"]))
        for name in ["positive", "negative"]
    }
    a["roll_deg"] = math.degrees(math.atan2(-a["roll"]["y"]["mean"], a["roll"]["z"]["mean"]))
    a["step_m_s2"] = 9.80665 / 64
    a["angular_step_deg"] = math.degrees(1 / 64)
    a["flat_unique_raw_xyz"] = len({tuple(x[1:4]) for x in window(r, 0, 8)})
    for slug in ["cc2541-gyroscope", "pocketlab-gyroscope"]:
        r = read(data_root, slug)
        q = result[slug]
        final = (56, 60) if slug == "cc2541-gyroscope" else (0, 9)
        q["stationary"] = {
            axis: stats(r, c, *final) for axis, c in [("x", 4), ("y", 5), ("z", 6), ("norm", 7)]
        }
        q["mean_dps"] = {axis: math.degrees(q["stationary"][axis]["mean"]) for axis in "xyz"}
        q["motion_windows"] = {}
        for name, col, lo, hi in (
            [("negative_y", 5, 42, 48), ("positive_z", 6, 9, 11), ("negative_z", 6, 19, 21)]
            if slug == "cc2541-gyroscope"
            else [("positive_x", 4, 19, 21), ("negative_x", 4, 29, 31), ("negative_y", 5, 49, 51)]
        ):
            w = stats(r, col, lo, hi)
            w["mean_dps"] = math.degrees(w["mean"])
            q["motion_windows"][name] = w
        col = 5 if slug == "cc2541-gyroscope" else 4
        lo, hi = (40, 50) if slug == "cc2541-gyroscope" else (10, 40)
        bias = q["stationary"]["y" if col == 5 else "x"]["mean"]
        q["integrals"] = {
            "window_s": [lo, hi],
            "sample_extent_s": [window(r, lo, hi)[0][0], window(r, lo, hi)[-1][0]],
            "bias_rad_s": bias,
            "signed_deg": math.degrees(integral(r, col, lo, hi, bias)),
            "absolute_component_deg": math.degrees(integral(r, col, lo, hi, bias, True)),
            "norm_deg": math.degrees(integral(r, 7, lo, hi)),
        }
        q["raw_max_abs"] = max(abs(v) for row in r for v in row[1:4])
    r = read(data_root, "cc2541-magnetometer")
    m = result["cc2541-magnetometer"]
    for name, lo, hi in [
        ("initial", 0, 15),
        ("rotated", 27, 35),
        ("near_magnet", 42, 44),
        ("returned", 53, 60),
    ]:
        m[name] = {
            axis: stats(r, c, lo, hi) for axis, c in [("x", 4), ("y", 5), ("z", 6), ("norm", 7)]
        }
    m["rotated_norm_change_pct"] = 100 * (
        m["rotated"]["norm"]["mean"] / m["initial"]["norm"]["mean"] - 1
    )
    m["field_peak_uT"] = max(x[7] for x in r)
    m["peak_to_baseline"] = m["field_peak_uT"] / m["initial"]["norm"]["mean"]
    m["inferred_offsets_uT"] = [st.mean(x[c] * 0.1 - x[c + 3] for x in r) for c in [1, 2, 3]]
    r = read(data_root, "cc2541-humidity")
    q = result["cc2541-humidity"]
    e = [[x[0], vapor_pressure(x[5], x[4])] for x in r]
    for name, lo, hi in [("initial", 0, 10), ("pulse", 26, 35), ("recovered", 50, 60)]:
        q[name] = {
            "RH": stats(r, 4, lo, hi),
            "T_C": stats(r, 5, lo, hi),
            "vapor_hPa": stats(e, 1, lo, hi),
        }
    peak = max(r, key=lambda x: x[4])
    q["peak_RH"] = {"time_s": peak[0], "value_pct": peak[4]}
    q["rh_step_pct"] = 125 * 4 / 65536
    q["temperature_step_C"] = 175.72 * 4 / 65536
    q["wrong_intercept_initial_pct"] = q["initial"]["RH"]["mean"] - 18
    r = read(data_root, "cc2541-pressure")
    q = result["cc2541-pressure"]
    q["baseline"] = stats(r, 3, 0, 18)
    q["peak"] = stats(r, 3, 26, 30)
    q["released"] = stats(r, 3, 52, 60)
    q["excursion_hPa"] = q["peak"]["mean"] - q["baseline"]["mean"]
    chosen = window(r, 28, 44)
    q["decay_fit"] = linear([x[0] for x in chosen], [x[3] for x in chosen])
    q["decay_fit"]["window_s"] = [28, 44]
    q["temperature_C"] = stats(r, 4, 0, 61)
    q["word_slope_hPa"] = linear([x[1] for x in r], [x[3] for x in r])["slope"]
    q["word_temperature_C"] = linear([x[2] for x in r], [x[4] for x in r])["slope"]
    q["isothermal_fractional_rate_s_inv"] = q["decay_fit"]["slope"] / st.mean(x[3] for x in chosen)
    r = read(data_root, "cc2541-ir-temperature")
    q = result["cc2541-ir-temperature"]
    for name, lo, hi in [
        ("ambient", 0, 9),
        ("warm", 12, 19),
        ("hot", 28, 38),
        ("cool", 42, 48),
        ("returned", 53, 60),
    ]:
        q[name] = {
            "object_C": stats(r, 8, lo, hi),
            "die_C": stats(r, 4, lo, hi),
            "voltage_V": stats(r, 3, lo, hi),
        }
    chosen = window(r, 28, 38)

    def changed_sensitivity(scale: float) -> float:
        return st.mean(
            ((x[4] + 273.15) ** 4 + ((x[3] - x[6]) + 13.4 * (x[3] - x[6]) ** 2) / (x[5] * scale))
            ** 0.25
            - 273.15
            for x in chosen
        )

    q["hot_model_at_original_sensitivity_C"] = changed_sensitivity(1.0)
    q["flux_header_residual_max_error_V"] = max(abs(x[7] - (x[3] - x[6])) for x in r)
    q["hot_sensitivity_plus10pct_C"] = changed_sensitivity(1.1)
    q["hot_sensitivity_minus10pct_C"] = changed_sensitivity(0.9)
    q["negative_voltage_count"] = sum(x[1] < 0 for x in r)
    q["inferred_S0_V_K4"] = st.mean(
        x[5] / (1 + 0.00175 * (x[4] - 25) - 0.00001678 * (x[4] - 25) ** 2) for x in r
    )
    q["object_rise_K"] = q["hot"]["object_C"]["mean"] - q["ambient"]["object_C"]["mean"]
    q["die_rise_K"] = q["hot"]["die_C"]["mean"] - q["ambient"]["die_C"]["mean"]
    return result


def curve(
    file: str,
    column: int,
    label: str,
    color: int = 0,
    x: int = 0,
    scale: float = 1,
    offset: float = 0,
) -> dict:
    return dict(
        file="drafts/" + file,
        column=column,
        label=label,
        color=color,
        x=x,
        scale=scale,
        offset=offset,
        options="",
    )


def panel(ylabel: str, curves: list[dict], title: str = "") -> dict:
    return dict(ylabel=ylabel, curves=curves, title=title, options="")


def figures() -> dict[str, dict]:
    result = {}
    for slug in [
        "cc2541-accelerometer",
        "cc2541-gyroscope",
        "cc2541-magnetometer",
        "pocketlab-gyroscope",
    ]:
        unit = {
            "cc2541-accelerometer": r"$\mathrm{m\,s^{-2}}$",
            "cc2541-magnetometer": r"$\mu\mathrm{T}$",
        }.get(slug, r"$\mathrm{rad\,s^{-1}}$")
        result[slug] = {
            "panels": [
                panel(
                    "Components (" + unit + ")",
                    [curve(slug, i + 4, "$" + axis + "$", i) for i, axis in enumerate("xyz")],
                ),
                panel("Magnitude (" + unit + ")", [curve(slug, 7, "")]),
            ],
            "xlabel": "Receive time (s)",
            "height": "3.0cm",
        }
    result["greenhouse-single"] = {
        "panels": [
            panel(
                r"Die temperature ($^\circ$C)",
                [
                    curve("greenhouse-single", 3, "indication"),
                    curve("greenhouse-single_fit", 1, "heating fit", 1),
                ],
            ),
            panel(
                "Baseline rise (K)",
                [
                    curve("greenhouse-single", 4, "exported"),
                    curve("greenhouse-single_fit", 2, "measured baseline", 1),
                ],
            ),
        ],
        "xlabel": "Receive time (s)",
        "height": "3.1cm",
    }
    result["sensortag-environmental"] = {
        "panels": [
            panel(
                r"Relative humidity (\%)", [curve("sensortag-environmental_humidity", 1, "HDC1000")]
            ),
            panel(
                r"Temperature ($^\circ$C)",
                [
                    curve("sensortag-environmental_humidity", 2, "HDC1000"),
                    curve("sensortag-environmental_barometer", 2, "BMP280", 1),
                ],
            ),
        ],
        "xlabel": "Receive time (s)",
        "height": "3.1cm",
    }
    result["puck-light"] = {
        "panels": [
            panel("Relative response", [curve("puck-light", 2, "Puck.light")]),
            panel("Reference ratio", [curve("puck-light", 4, "")]),
        ],
        "xlabel": "Device clock (s)",
        "height": "3.0cm",
    }
    # Keep clock origin explicit, rather than using count/rate.
    for p in result["puck-light"]["panels"]:
        for c in p["curves"]:
            c["x"] = 1
    result["cc2541-humidity"] = {
        "panels": [
            panel(r"Relative humidity (\%)", [curve("cc2541-humidity", 4, "SHT21")]),
            panel(r"Temperature ($^\circ$C)", [curve("cc2541-humidity", 5, "")]),
        ],
        "xlabel": "Receive time (s)",
        "height": "3.0cm",
    }
    result["cc2541-pressure"] = {
        "panels": [
            panel("Pressure (hPa)", [curve("cc2541-pressure", 3, "T5400")]),
            panel(r"Temperature ($^\circ$C)", [curve("cc2541-pressure", 4, "")]),
        ],
        "xlabel": "Read receive time (s)",
        "height": "3.0cm",
    }
    result["cc2541-ir-temperature"] = {
        "panels": [
            panel(
                r"Temperature ($^\circ$C)",
                [
                    curve("cc2541-ir-temperature", 8, "object model"),
                    curve("cc2541-ir-temperature", 4, "die", 1),
                ],
            ),
            panel(r"Thermopile ($\mu$V)", [curve("cc2541-ir-temperature", 3, "", scale=1e6)]),
        ],
        "xlabel": "Receive time (s)",
        "height": "3.0cm",
    }
    return result


def tables(data_root: Path) -> dict[str, list[list[float]]]:
    rows = read(data_root, "greenhouse-single")
    fit = heating_fit(rows)
    return {
        "drafts/greenhouse-single_fit": [
            [
                r[0],
                fit["baseline_C"] + fit["amplitude_K"] * (1 - math.exp(-(r[0] - 60) / fit["tau_s"]))
                if 60 <= r[0] < 235
                else math.nan,
                r[3] - fit["baseline_C"],
            ]
            for r in rows
        ]
    }


def self_check() -> None:
    fit = linear([0, 1, 2, 3], [4, 7, 10, 13])
    assert abs(fit["slope"] - 3) < 1e-12 and abs(fit["intercept"] - 4) < 1e-12
    assert abs(integral([[0, 0], [1, 1], [2, 0]], 1, 0, 3) - 1) < 1e-12
    assert abs(vapor_pressure(0, 100) - 6.1094) < 1e-12
    # Reversal cancels signed angle, while the norm/absolute integral cannot.
    assert integral([[0, 1], [1, 0], [2, -1]], 1, 0, 3) == 0
    assert integral([[0, 1], [1, 0], [2, -1]], 1, 0, 3, absolute=True) == 1
    analytic = [
        [float(t), 0, 0, 23 + (8 * (1 - math.exp(-(t - 60) / 150)) if t >= 60 else 0)]
        for t in range(301)
    ]
    fitted = heating_fit(analytic)
    assert abs(fitted["tau_s"] - 150) < 1e-3
    assert abs(fitted["amplitude_K"] - 8) < 1e-5
    assert len(figures()) == 10


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-root", type=Path, default=Path(__file__).resolve().parents[3] / "example-data"
    )
    args = parser.parse_args()
    self_check()
    print(json.dumps(analyze(args.data_root), indent=2, allow_nan=False))
