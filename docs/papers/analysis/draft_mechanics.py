#!/usr/bin/env python3
"""Reductions for three mechanics lessons; example inputs remain unchanged."""

from __future__ import annotations

import argparse
import bisect
import json
import math
import statistics as st
from pathlib import Path

from _common import draft_rows as read
from _common import ols, window

SLUGS = ("static-friction", "audio-magnetic", "magnetic-current")


def finite(values):
    return [x for x in values if math.isfinite(x)]


def stats(values) -> dict:
    xs = finite(values)
    return {"n": len(xs), "mean": st.mean(xs), "sd": st.stdev(xs) if len(xs) > 1 else None}


def line_fit(x, y) -> dict:
    pairs = [(a, b) for a, b in zip(x, y) if math.isfinite(a) and math.isfinite(b)]
    xx, yy = zip(*pairs)
    slope, intercept = ols(xx, yy)
    residual = [b - intercept - slope * a for a, b in pairs]
    return {
        "n": len(pairs),
        "intercept": intercept,
        "slope": slope,
        "residual_rms": math.sqrt(st.mean(r * r for r in residual)),
        "residual_sd": math.sqrt(sum(r * r for r in residual) / (len(pairs) - 2)),
    }


def first_slip(
    gravity, linear, arm=5.0, threshold=1.0, debounce=0.15, prelag=0.10, maxage=0.20, maxgap=0.15
):
    """Independent sequential implementation of first-valid sustained excursion.

    The origin is the most recent actual below-threshold sample. A long gap
    invalidates that origin until another actual low sample arrives. Gravity is
    selected by previous timestamp, never by the row index of the other stream.
    """
    gt = [r[3] for r in gravity]
    low = None
    previous = None
    onset = None
    for a, t in linear:
        if t < arm or not (math.isfinite(a) and math.isfinite(t)):
            continue
        if previous is not None and t - previous > maxgap:
            low, onset = None, None
        previous = t
        if a <= threshold:
            low, onset = t, None
            continue
        if low is None:
            continue
        if onset is None:
            onset = t
        if t - low < debounce:
            continue
        query = low - prelag
        index = bisect.bisect_right(gt, query) - 1
        if index < 0:
            continue
        gx, gy, gz, sample_t, *_ = gravity[index]
        norm = math.sqrt(gx * gx + gy * gy + gz * gz)
        angle = math.degrees(math.atan2(math.hypot(gx, gy), abs(gz)))
        if not (0 <= query - sample_t <= maxage and 9.3 <= norm <= 10.3 and 0 <= angle <= 85):
            continue
        return {
            "trigger_s": t,
            "last_low_s": low,
            "first_high_s": onset,
            "pre_query_s": query,
            "pre_sample_s": sample_t,
            "pre_age_s": query - sample_t,
            "angle_deg": angle,
            "mu": math.tan(math.radians(angle)),
            "gravity_norm_m_s2": norm,
            "confirmation_delay_s": t - onset,
        }
    return None


def friction(data_root):
    g = read(data_root, "static-friction_gravity")
    a = read(data_root, "static-friction_linear")
    capture = first_slip(g, a)
    if capture is None:
        raise ValueError("No valid slip in example data")
    ramp = window(g, 5, 19.8, 3)
    fit = line_fit(
        [r[3] for r in ramp],
        [math.degrees(math.atan2(math.hypot(r[0], r[1]), abs(r[2]))) for r in ramp],
    )
    baseline = window(g, 0, 5, 3)
    local = window(g, 19, 19.8, 3)
    local_fit = line_fit([r[3] for r in local], [r[4] for r in local])
    derivative = 1 / math.cos(math.radians(capture["angle_deg"])) ** 2 * math.pi / 180
    return {
        "capture": capture,
        "ramp_line_diagnostic_deg_s": fit,
        "local_fit_deg_s": local_fit,
        "baseline_linear_m_s2": stats(r[0] for r in window(a, 0, 5, 1)),
        "baseline_gravity_m_s2": stats(r[5] for r in baseline),
        "local_angle_residual_deg": local_fit["residual_sd"],
        "noise_only_mu_scale": derivative * local_fit["residual_sd"],
        "one_degree_mu_scale": derivative,
        "prelag_angle_bias_deg": local_fit["slope"]
        * (capture["first_high_s"] - capture["pre_sample_s"]),
        "post_angle_deg": stats(r[4] for r in window(g, 25, 29, 3)),
        "max_angle_export_error_deg": max(
            abs(r[4] - math.degrees(math.atan2(math.hypot(r[0], r[1]), abs(r[2])))) for r in g
        ),
        "settings": {
            "arm_s": 5,
            "threshold_m_s2": 1,
            "debounce_s": 0.15,
            "prelag_s": 0.1,
            "maxage_s": 0.2,
            "maxgap_s": 0.15,
        },
        "windows": {
            "baseline_s": [0, 5],
            "ramp_s": [5, 19.8],
            "local_noise_s": [19, 19.8],
            "post_s": [25, 29],
        },
        "method": (
            "Left-closed/right-open windows; raw-component angle; "
            "previous gravity timestamp; no SEM from adjacent rows."
        ),
    }


def block_summary(rows, reference=0.02, noise=0.01):
    n = sum(r[2] for r in rows)
    energy = sum(r[2] * r[1] ** 2 for r in rows)
    rms = math.sqrt(energy / n)
    return {
        "blocks": len(rows),
        "samples": int(n),
        "duration_s": sum(r[2] / r[3] for r in rows),
        "aggregate_rms": rms,
        "aggregate_level_db": 20 * math.log10(rms / reference),
        "mean_block_level_db": st.mean(20 * math.log10(r[1] / reference) for r in rows if r[1] > 0),
        "sd_block_level_db": st.stdev(20 * math.log10(r[1] / reference) for r in rows if r[1] > 0),
        "noise_corrected_aggregate_rms": math.sqrt(rms * rms - noise * noise)
        if rms > noise
        else None,
        "sub_noise_blocks": sum(r[1] <= noise for r in rows),
    }


def audio(data_root):
    a = read(data_root, "audio-magnetic_audio")
    b = read(data_root, "audio-magnetic_magnetic")
    plateaus = []
    for start in (1, 11, 21, 31, 41, 51):
        aa, bb = window(a, start, start + 8), window(b, start, start + 8)
        plateaus.append(
            {
                "window_s": [start, start + 8],
                "state": "on" if start % 20 == 11 else "off",
                "audio": block_summary(aa),
                "magnetic_n": len(bb),
                "magnetic_components_uT": [st.mean(r[i] for r in bb) for i in (1, 2, 3)],
                "magnetic_norm_uT": stats(r[4] for r in bb),
            }
        )
    contrasts = []
    for off, on in zip(plateaus[::2], plateaus[1::2]):
        delta = [y - x for x, y in zip(off["magnetic_components_uT"], on["magnetic_components_uT"])]
        contrasts.append(
            {
                "audio_difference_db": on["audio"]["aggregate_level_db"]
                - off["audio"]["aggregate_level_db"],
                "magnetic_norm_difference_uT": on["magnetic_norm_uT"]["mean"]
                - off["magnetic_norm_uT"]["mean"],
                "magnetic_vector_difference_uT": delta,
                "vector_change_magnitude_uT": math.sqrt(sum(x * x for x in delta)),
            }
        )
    return {
        "plateaus": plateaus,
        "contrasts": contrasts,
        "contrast_audio_db": stats(r["audio_difference_db"] for r in contrasts),
        "contrast_magnetic_norm_uT": stats(r["magnetic_norm_difference_uT"] for r in contrasts),
        "full_record_sub_noise_blocks": sum(r[1] <= 0.01 for r in a),
        "stored_sub_noise_zeros": sum(r[1] <= 0.01 and r[5] == 0 for r in a),
        "max_level_recalculation_error_db": max(
            abs(r[6] - 20 * math.log10(r[1] / 0.02)) for r in a
        ),
        "max_duration_recalculation_error_s": max(abs(r[4] - r[2] / r[3]) for r in a),
        "audio_count": len(a),
        "magnetic_count": len(b),
        "audio_time_range_s": [a[0][0], a[-1][0]],
        "magnetic_time_range_s": [b[0][0], b[-1][0]],
        "settings": {"reference_rms": 0.02, "assigned_reference_db": 0, "noise_rms": 0.01},
        "method": (
            "Each stream windowed on own session timestamps; 1 s transition exclusion. "
            "N-weighted mean square then dB. Three cycle contrasts, not adjacent "
            "samples, describe cycle spread. No lag/coherence inference."
        ),
    }


def magnetic(data_root):
    rows = read(data_root, "magnetic-current")
    currents = [0, 0.1, 0.2, 0.3, 0.4, 0.2, 0]
    plateaus = []
    for j, ref in enumerate(currents):
        start, stop = 8 * j + 1, min(8 * j + 7, 59)
        block = window(rows, start, stop)
        plateaus.append(
            {
                "window_s": [start, stop],
                "assigned_current_A": ref,
                "field_uT": stats(r[3] for r in block),
                "exported_current_A": stats(r[5] for r in block),
            }
        )
    b1, b2 = plateaus[0]["field_uT"]["mean"], plateaus[4]["field_uT"]["mean"]
    gain = 0.4 / (b2 - b1)
    fit = line_fit(
        [p["assigned_current_A"] for p in plateaus[:5]],
        [p["field_uT"]["mean"] for p in plateaus[:5]],
    )
    for p in plateaus:
        value = (p["field_uT"]["mean"] - b1) * gain
        p["endpoint_calibrated_current_A"] = value
        p["endpoint_residual_mA"] = 1000 * (value - p["assigned_current_A"])
    pooled_sd = math.sqrt(
        sum((p["field_uT"]["n"] - 1) * p["field_uT"]["sd"] ** 2 for p in plateaus)
        / sum(p["field_uT"]["n"] - 1 for p in plateaus)
    )
    return {
        "plateaus": plateaus,
        "ascending_plateau_fit_B_vs_I": fit,
        "endpoint_calibration": {
            "b1_uT": b1,
            "i1_A": 0,
            "b2_uT": b2,
            "i2_A": 0.4,
            "field_span_uT": b2 - b1,
            "gain_A_per_uT": gain,
        },
        "pooled_within_plateau_sd_uT": pooled_sd,
        "single_reading_noise_mA": 1000 * gain * pooled_sd,
        "zero_return_shift_uT": plateaus[-1]["field_uT"]["mean"] - b1,
        "zero_return_shift_mA": plateaus[-1]["endpoint_residual_mA"],
        "max_withheld_residual_mA": max(
            abs(p["endpoint_residual_mA"]) for j, p in enumerate(plateaus) if j not in (0, 4)
        ),
        "max_affine_export_error_A": max(abs(r[5] - (r[3] - 30) / 50) for r in rows),
        "one_uT_background_bias_mA": 1000 * gain,
        "method": (
            "Assigned protocol current levels, not an independent measured current channel. "
            "Windows omit 1 s after and before each 8 s step; final zero uses49--55 s. "
            "Ascending fit uses five plateau means. Endpoint calibration uses1--7 "
            "and33--39 s. Row scatter not replicate uncertainty."
        ),
    }


def analyze(data_root: Path) -> dict[str, dict]:
    return {
        "static-friction": friction(data_root),
        "audio-magnetic": audio(data_root),
        "magnetic-current": magnetic(data_root),
    }


def curve(file, column, label, color=0, x=0, **kwargs):
    return {
        "file": "drafts/" + file,
        "column": column,
        "label": label,
        "color": color,
        "x": x,
        "scale": 1,
        "offset": 0,
        "options": "",
        **kwargs,
    }


def figures() -> dict[str, dict]:
    return {
        "static-friction": {
            "xlabel": "Session time (s)",
            "height": "3.2cm",
            "panels": [
                {
                    "ylabel": r"$\theta$ (deg)",
                    "title": "Inclination",
                    "options": "xmin=16,xmax=25",
                    "curves": [curve("static-friction_gravity", 4, "", x=3)],
                },
                {
                    "ylabel": r"$a_{\rm lin}$ ($\mathrm{m\,s^{-2}}$)",
                    "title": "First sustained excursion",
                    "options": "xmin=16,xmax=25",
                    "curves": [curve("static-friction_linear", 0, "", x=1)],
                },
            ],
        },
        "audio-magnetic": {
            "xlabel": "Session time (s)",
            "height": "3.2cm",
            "panels": [
                {
                    "ylabel": "RMS (relative)",
                    "title": "Audio blocks",
                    "options": r"xmin=0,xmax=60,width=0.94\columnwidth",
                    "curves": [curve("audio-magnetic_audio", 1, "")],
                },
                {
                    "ylabel": r"$|\bm B|$ ($\mu$T)",
                    "title": "Magnetic samples",
                    "options": r"xmin=0,xmax=60,width=0.94\columnwidth",
                    "curves": [curve("audio-magnetic_magnetic", 4, "", color=2)],
                },
            ],
        },
        "magnetic-current": {
            "xlabel": "Session time (s)",
            "height": "3.2cm",
            "panels": [
                {
                    "ylabel": r"$B_z$ ($\mu$T)",
                    "title": "Fixed-geometry field",
                    "options": "xmin=0,xmax=60",
                    "curves": [curve("magnetic-current", 3, "")],
                },
                {
                    "ylabel": "$I$ (A)",
                    "title": "Nominal affine conversion",
                    "options": "xmin=0,xmax=60",
                    "curves": [curve("magnetic-current", 5, "", color=1)],
                },
            ],
        },
    }


def check(data_root: Path) -> None:
    # Exact synthetic fit and unequal-block energy reduction are independent
    # numerical checks of the reducers, including the logarithm domain.
    fit = line_fit([0, 1, 2, 3], [7, 10, 13, 16])
    assert abs(fit["intercept"] - 7) < 1e-12 and abs(fit["slope"] - 3) < 1e-12
    block = block_summary([[0.1, 1.0, 1, 10, 0.1], [0.2, 3.0, 3, 10, 0.3]], reference=1, noise=0)
    assert abs(block["aggregate_rms"] - math.sqrt(7)) < 1e-12
    assert abs(block["aggregate_level_db"] - 10 * math.log10(7)) < 1e-12
    g = [[9.81 * math.sin(0.3), 0, 9.81 * math.cos(0.3), t] for t in (0, 0.1, 0.2, 0.3, 0.4)]
    event = first_slip(g, [[0, 0], [2, 0.1], [2, 0.2], [0, 0.3], [9, 0.4]], arm=0, prelag=0)
    assert event is not None and abs(event["angle_deg"] - math.degrees(0.3)) < 1e-12
    assert event["trigger_s"] == 0.2
    metrics = analyze(data_root)
    assert 24 < metrics["static-friction"]["capture"]["angle_deg"] < 26
    assert metrics["static-friction"]["max_angle_export_error_deg"] < 1e-6
    assert metrics["audio-magnetic"]["max_level_recalculation_error_db"] < 1e-6
    assert metrics["magnetic-current"]["max_affine_export_error_A"] < 1e-8
    # JSON output deliberately has no NaN/Infinity metrics.
    json.dumps(metrics, allow_nan=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-root", type=Path, default=Path(__file__).resolve().parents[3] / "example-data"
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check(args.data_root)
    print(json.dumps(analyze(args.data_root), indent=2, allow_nan=False))
