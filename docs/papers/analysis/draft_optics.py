"""Reproduce the six optics draft papers from immutable example observations.

Only the standard library is used. Scatters describe selected observations, not
calibration uncertainty. Leave-one-window ranges and +/-1 mm origin tests are
sensitivity analyses, not confidence intervals. Clocks are paired explicitly.
"""

from __future__ import annotations

import bisect
import json
import math
import statistics as st
from pathlib import Path

from _common import draft_rows as read
from _common import window

SLUGS = (
    "rgb-filter-transmission",
    "illuminance-distance",
    "illuminance-distance-manual",
    "malus-law",
    "colour-temperature",
    "detector-characterization",
)


def finite_max(values: list[float]) -> float:
    """max() over NaN is order-dependent, so refuse NaN."""
    if any(math.isnan(v) for v in values):
        raise ValueError("NaN in values to be maximised")
    return max(values)


def mean(rows: list[list[float]], col: int) -> float:
    return st.mean(row[col] for row in rows)


def sd(rows: list[list[float]], col: int) -> float:
    return st.stdev(row[col] for row in rows)


def linear(x: list[float], y: list[float]) -> dict[str, float]:
    mx, my = st.mean(x), st.mean(y)
    slope = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sum((a - mx) ** 2 for a in x)
    intercept = my - slope * mx
    residual = [b - intercept - slope * a for a, b in zip(x, y)]
    return {
        "slope": slope,
        "intercept": intercept,
        "residual_sd": math.sqrt(sum(v * v for v in residual) / (len(x) - 2)),
    }


def power_fit(rows: list[list[float]], offset: float = 0) -> dict[str, float]:
    result = linear([math.log(row[0] + offset) for row in rows], [math.log(row[1]) for row in rows])
    return {
        "exponent": -result["slope"],
        "amplitude": math.exp(result["intercept"]),
        "log_residual_sd": result["residual_sd"],
    }


def solve(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    a = [row[:] + [value] for row, value in zip(matrix, rhs)]
    for k in range(len(a)):
        pivot = max(range(k, len(a)), key=lambda i: abs(a[i][k]))
        a[k], a[pivot] = a[pivot], a[k]
        divisor = a[k][k]
        a[k] = [value / divisor for value in a[k]]
        for i in range(len(a)):
            if i != k:
                factor = a[i][k]
                a[i] = [v - factor * w for v, w in zip(a[i], a[k])]
    return [row[-1] for row in a]


def malus_fit(angles: list[float], signals: list[float]) -> dict[str, float]:
    design = [[1, math.cos(2 * math.radians(t)), math.sin(2 * math.radians(t))] for t in angles]
    coefficients = solve(
        [[sum(row[i] * row[j] for row in design) for j in range(3)] for i in range(3)],
        [sum(row[i] * value for row, value in zip(design, signals)) for i in range(3)],
    )
    a, b, c = coefficients
    radius = math.hypot(b, c)
    residual = [
        y - sum(p * q for p, q in zip(row, coefficients)) for row, y in zip(design, signals)
    ]
    return {
        "floor_counts": a - radius,
        "amplitude_counts": 2 * radius,
        "angle_zero_deg": math.degrees(math.atan2(c, b)) / 2,
        "residual_rms_counts": math.sqrt(st.mean(value * value for value in residual)),
    }


def colour(raw: list[float]) -> list[float]:
    c, r, g, b = raw
    if (
        not all(math.isfinite(value) for value in raw)
        or c <= 3
        or r < 2
        or g < 2
        or b < 1
        or max(raw) >= 4100
    ):
        return [math.nan, math.nan, math.nan]
    qr, qg, qb = (r - 2) / (c - 3), (g - 2) / (c - 3), (b - 1) / (c - 3)
    xx = -0.14282 * qr + 1.54924 * qg - 0.95641 * qb
    yy = -0.32466 * qr + 1.57837 * qg - 0.73191 * qb
    zz = -0.68202 * qr + 0.77073 * qg + 0.56332 * qb
    if min(xx, yy, zz) < 0 or xx + yy + zz <= 0:
        return [math.nan, math.nan, math.nan]
    x, y = xx / (xx + yy + zz), yy / (xx + yy + zz)
    if abs(0.1858 - y) <= 0.001:
        return [x, y, math.nan]
    n = (x - 0.3320) / (0.1858 - y)
    temperature = 449 * n**3 + 3525 * n * n + 6823.3 * n + 5520.33
    return [x, y, temperature if 2000 < temperature < 10000 else math.nan]


def reductions(data_root: Path) -> tuple[dict, dict[str, list[list[float]]]]:
    results, tables = {}, {}
    rgb = read(data_root, "rgb-filter-transmission")
    dark, nominal = [3, 2, 2, 1], [1800, 900, 1050, 620]
    reference = window(rgb, 4.5, 5.5)
    references = [mean(reference, col) for col in range(2, 6)]
    local = []
    for row in rgb:
        local.append(
            [row[0]] + [(row[j + 2] - dark[j]) / (references[j] - dark[j]) for j in range(4)]
        )
    tables["drafts/optics-rgb-local"] = local
    turns = []
    for t in [5, 15, 25, 35, 45]:
        selected = window(rgb, t - 0.5, t + 0.5)
        turns.append(
            {
                "window_s": [t - 0.5, t + 0.5],
                "n": len(selected),
                "counts": [mean(selected, k) for k in range(2, 6)],
                "reference_normalized": [mean(selected, k) for k in range(6, 10)],
                "locally_rereferenced": [
                    (mean(selected, j + 2) - dark[j]) / (references[j] - dark[j]) for j in range(4)
                ],
            }
        )
    results[SLUGS[0]] = {
        "windows": "Half-open device-time intervals; local extrema are transitions, not plateaux",
        "dark_counts": dark,
        "entered_reference_counts": nominal,
        "local_reference_mean_counts": references,
        "turning_windows": turns,
        "max_counts": max(row[j] for row in rgb for j in range(2, 6)),
        "n": len(rgb),
        "units": {"transmission": "1", "signal": "counts", "time": "s"},
    }

    light, mouse = (
        read(data_root, "illuminance-distance_light"),
        read(data_root, "illuminance-distance_mouse"),
    )
    mouse_t = [row[0] for row in mouse]
    paired = []
    mismatches = []
    for row in light:
        index = bisect.bisect_right(mouse_t, row[0]) - 1
        r = 0.15 + 0.0002 * mouse[index][5] if index >= 0 else math.nan
        paired.append([row[0], r, row[3]])
        mismatches.append(abs(r - row[5]))
        word = int(row[1])
        decoded = 0.01 * (2 ** (word // 4096)) * (word % 4096)
        assert math.isclose(decoded, row[2], rel_tol=1e-8)
    plateaux = []
    for k in range(15):
        selected = window(paired, 4 * k + 1, 4 * k + 3.5)
        r, ev = mean(selected, 1), mean(selected, 2)
        plateaux.append([r, ev, ev * r * r])
    fit = power_fit(plateaux)
    deletions = [
        power_fit(plateaux[:i] + plateaux[i + 1 :])["exponent"] for i in range(len(plateaux))
    ]
    residuals = [[r, ev, ev - fit["amplitude"] / r ** fit["exponent"]] for r, ev, _ in plateaux]
    tables["drafts/optics-distance-observations"] = residuals
    tables["drafts/optics-distance-fit"] = [
        [r, fit["amplitude"] / r ** fit["exponent"]] for r in [0.2 + 0.006 * k for k in range(101)]
    ]
    results[SLUGS[1]] = {
        "plateau_windows_s": [[4 * k + 1, 4 * k + 3.5] for k in range(15)],
        "method": (
            "Most recent actual mouse receive time, then unweighted log-log fit of plateau means"
        ),
        "fit": fit,
        "leave_one_plateau_out_exponent_range": [min(deletions), max(deletions)],
        "origin_shift_minus_plus_1mm_exponents": [
            power_fit(plateaux, d)["exponent"] for d in [-0.001, 0.001]
        ],
        "plateaux_r_m_lux_product": plateaux,
        "product_mean_lx_m2": st.mean(row[2] for row in plateaux),
        "product_sd_lx_m2": st.stdev(row[2] for row in plateaux),
        "max_repaired_pairing_distance_difference_m": finite_max(mismatches),
        "pairing_rows_differing": sum(v > 1e-8 for v in mismatches),
        "hid_signed_byte_overflow_rows": sum(abs(row[j]) > 127 for row in mouse for j in [1, 2]),
        "units": {"distance": "m", "illuminance": "lx", "product": "lx m^2"},
    }

    raw, obs = (
        read(data_root, "illuminance-distance-manual"),
        read(data_root, "illuminance-distance-manual_observations"),
    )
    snapshots = [[row[0], row[4], row[7]] for row in obs]
    averaged = []
    for k, row in enumerate(obs):
        selected = window(raw, 5 * k + 1.5, 5 * k + 3.5)
        signal = mean(selected, 2) - 10
        averaged.append([row[0], signal, signal * row[0] ** 2])
        nearest = min(raw, key=lambda sample: abs(sample[0] - row[1]))
        assert abs(nearest[2] - row[3]) < 1e-8 and abs(nearest[1] - row[2]) < 1e-8
    sf, af = power_fit(snapshots), power_fit(averaged)
    tables["drafts/optics-manual-observations"] = [
        [a[0], a[1], a[2], b[1], b[2]] for a, b in zip(snapshots, averaged)
    ]
    tables["drafts/optics-manual-fit"] = [
        [r, af["amplitude"] / r ** af["exponent"]] for r in [0.2 + 0.005 * k for k in range(101)]
    ]
    repeats = []
    for k in range(6):
        a, b = averaged[k], averaged[11 - k]
        repeats.append([a[0], snapshots[k][2], snapshots[11 - k][2], a[2], b[2]])
    results[SLUGS[2]] = {
        "snapshot_fit": sf,
        "plateau_fit": af,
        "plateau_windows_s": [[5 * k + 1.5, 5 * k + 3.5] for k in range(12)],
        "snapshot_product_mean": st.mean(row[2] for row in snapshots),
        "snapshot_product_sd": st.stdev(row[2] for row in snapshots),
        "plateau_product_mean": st.mean(row[2] for row in averaged),
        "plateau_product_sd": st.stdev(row[2] for row in averaged),
        "origin_shift_minus_plus_1mm_exponents": [
            power_fit(averaged, d)["exponent"] for d in [-0.001, 0.001]
        ],
        "return_pairs_r_snapshot_out_in_plateau_out_in": repeats,
        "units": {"distance": "m", "signal": "counts", "product": "count m^2"},
        "method": (
            "Two-second interior means versus one paired snapshot per ruler position; log OLS"
        ),
    }

    raw, obs = read(data_root, "malus-law"), read(data_root, "malus-law_observations")
    angles = [row[0] for row in obs]
    shots = [row[3] for row in obs]
    plateaux = [mean(window(raw, 6 * k + 1, 6 * k + 5.5), 2) for k in range(10)]
    single_fit, averaged_fit = malus_fit(angles, shots), malus_fit(angles, plateaux)
    model = []
    for t, signal, avg in zip(angles, shots, plateaux):
        prediction = math.cos(math.radians(t)) ** 2
        model.append(
            [
                t,
                (signal - 10) / 1000,
                prediction,
                (avg - 10) / 1000,
                (signal - 10) / 1000 - prediction,
                (avg - 10) / 1000 - prediction,
            ]
        )
    tables["drafts/optics-malus-observations"] = model
    f = averaged_fit
    tables["drafts/optics-malus-fit"] = [
        [
            t,
            (
                f["floor_counts"]
                + f["amplitude_counts"] * math.cos(math.radians(t - f["angle_zero_deg"])) ** 2
                - 10
            )
            / 1000,
        ]
        for t in range(91)
    ]
    for row in obs:
        nearest = min(raw, key=lambda sample: abs(sample[0] - row[1]))
        assert nearest[2] == row[3] and abs(nearest[1] - row[2]) < 1e-8
    results[SLUGS[3]] = {
        "snapshot_fit": single_fit,
        "plateau_fit": averaged_fit,
        "plateau_windows_s": [[6 * k + 1, 6 * k + 5.5] for k in range(10)],
        "snapshot_residual_rms_normalized": math.sqrt(st.mean(row[4] ** 2 for row in model)),
        "angle_deg_shot_plateau_counts": [[t, s, a] for t, s, a in zip(angles, shots, plateaux)],
        "method": (
            "Linear least squares in 1,cos(2 theta),sin(2 "
            "theta); phase and amplitude recovered algebraically"
        ),
        "units": {"angle": "degree", "signal": "counts", "normalized_signal": "1"},
    }

    raw = read(data_root, "colour-temperature")
    colour_windows = []
    for name, start, stop in [
        ("warm", 2, 13),
        ("intermediate", 21, 29),
        ("cool", 36, 44),
        ("warm return", 52, 59),
    ]:
        selected = window(raw, start, stop)
        calculated = [colour(row[2:6]) for row in selected]
        colour_windows.append(
            {
                "name": name,
                "window_s": [start, stop],
                "n": len(selected),
                "mean_cct_K": st.mean(row[2] for row in calculated),
                "sample_sd_cct_K": st.stdev(row[2] for row in calculated),
                "mean_chromaticity": [st.mean(row[k] for row in calculated) for k in [0, 1]],
                "cct_of_mean_counts_K": colour([mean(selected, k) for k in range(2, 6)])[2],
            }
        )
    discrepancies = [abs(colour(row[2:6])[2] - row[18]) for row in raw]
    results[SLUGS[4]] = {
        "windows": colour_windows,
        "dark_counts": [3, 2, 2, 1],
        "max_reduction_difference_K": finite_max(discrepancies),
        "method": (
            "Dark-correct raw counts; normalize by corrected "
            "clear; donor matrix; guarded McCamy cubic"
        ),
        "units": {"cct": "K", "chromaticity": "1"},
        "calibration_scope": (
            "Donor matrix comes from TCS3414CS application note, not an APDS calibration"
        ),
    }

    raw = read(data_root, "detector-characterization")
    summary = read(data_root, "detector-characterization_summary")[0]
    baseline = window(raw, 12, 28 + 1e-9)
    dark = window(raw, 0, 9)
    dt = [b[0] - a[0] for a, b in zip(raw, raw[1:])]
    dr = [b[1] - a[1] for a, b in zip(raw, raw[1:])]
    mu, sigma = mean(baseline, 2), sd(baseline, 2)
    derived = [
        st.mean(dt),
        st.mean(dr),
        st.stdev(dt),
        st.stdev(dr),
        1 / st.mean(dt),
        1 / st.mean(dr),
        len(baseline),
        mu,
        sigma,
        0.02 * (mu - 8),
        0.02 * (mu - 8) / sigma,
        1 / st.mean(dt),
    ]
    assert all(math.isclose(a, b, rel_tol=1e-7, abs_tol=1e-7) for a, b in zip(derived, summary))
    features = []
    for start, duration in [(30, 0.5), (34, 1), (38, 2), (44, 4)]:
        event = window(raw, start, start + duration)
        phases = [len(window(raw[phase::16], start, start + duration)) for phase in range(16)]
        features.append(
            {
                "window_s": [start, start + duration],
                "n": len(event),
                "mean_counts": mean(event, 2),
                "sample_sd_counts": sd(event, 2),
                "depth_from_global_baseline": (mu - mean(event, 2)) / (mu - mean(dark, 2)),
                "single_sample_snr": (mu - mean(event, 2)) / sigma,
                "stride_16_count_range": [min(phases), max(phases)],
                "stride_16_phases_missing": phases.count(0),
            }
        )
    blocks = [mean(window(raw, k, k + 1), 2) for k in range(12, 28)]
    lag_numerator = sum(
        (a - mu) * (b - mu) for a, b in zip([r[2] for r in baseline], [r[2] for r in baseline][1:])
    )
    rho = lag_numerator / sum((row[2] - mu) ** 2 for row in baseline)
    tables["drafts/optics-detector-intervals"] = [
        [b[0], d * 1000, r * 1000] for b, d, r in zip(raw[1:], dt, dr)
    ]
    results[SLUGS[5]] = {
        "summary_values": summary,
        "recomputed_summary_max_abs_difference": max(abs(a - b) for a, b in zip(derived, summary)),
        "baseline_window_s": [12, 28],
        "dark_window_s": [0, 9],
        "dark_mean_counts": mean(dark, 2),
        "baseline_mean_counts": mu,
        "baseline_sample_sd_counts": sigma,
        "baseline_n": len(baseline),
        "device_mean_interval_s": st.mean(dt),
        "receive_mean_interval_s": st.mean(dr),
        "device_interval_sd_s": st.stdev(dt),
        "receive_interval_sd_s": st.stdev(dr),
        "delivered_device_rate_Hz": 1 / st.mean(dt),
        "lag_one_baseline_correlation": rho,
        "one_second_block_mean_sd_counts": st.stdev(blocks),
        "feature_results": features,
        "method": (
            "Actual timestamp differences; summary cross-check; interior "
            "event windows; all 16 stride phases"
        ),
        "units": {"time": "s", "signal": "counts", "rate": "Hz", "snr": "1"},
    }
    return results, tables


def analyze(data_root: Path) -> dict[str, dict]:
    return reductions(data_root)[0]


def tables(data_root: Path) -> dict[str, list[list[float]]]:
    return reductions(data_root)[1]


def figures() -> dict[str, dict]:
    def curve(file, column, label="", color=0, x=0, options="", scale=1, offset=0):
        return dict(
            file="drafts/" + file,
            column=column,
            label=label,
            color=color,
            x=x,
            options=options,
            scale=scale,
            offset=offset,
        )

    def panel(ylabel, curves, title="", options=""):
        return dict(ylabel=ylabel, curves=curves, title=title, options=options)

    def figure(panels, xlabel="Device time (s)", height="3.2cm"):
        physical_limits = {
            "Source distance (m)": ["ymin=0,ymax=3300", "ymin=-15,ymax=36"],
            "Ruler distance (m)": ["ymin=0,ymax=3300", "ymin=99,ymax=108"],
            "Analyzer angle (degree)": ["ymin=-0.05,ymax=1.3", "ymin=-0.003,ymax=0.055"],
        }
        if xlabel in physical_limits:
            for item, limits in zip(panels, physical_limits[xlabel]):
                item["options"] += ",enlarge x limits=0.03," + limits
        return dict(panels=panels, xlabel=xlabel, height=height)

    return {
        SLUGS[0]: figure(
            [
                panel(
                    "Clear (counts)",
                    [curve("rgb-filter-transmission", 2)],
                    "Broad-band attenuation",
                ),
                panel(
                    "Transmission (1)",
                    [
                        curve("optics-rgb-local", j + 2, c, [1, 2, 0][j])
                        for j, c in enumerate(["Red", "Green", "Blue"])
                    ],
                    "Referenced to 4.5--5.5 s",
                ),
            ]
        ),
        SLUGS[1]: figure(
            [
                panel(
                    "Illuminance (lx)",
                    [
                        curve(
                            "optics-distance-observations",
                            1,
                            "Means",
                            0,
                            options="only marks,mark=*",
                        ),
                        curve("optics-distance-fit", 1, "Power fit", 1),
                    ],
                    "Settled windows",
                ),
                panel(
                    "Residual (lx)",
                    [curve("optics-distance-observations", 2, "", 0, options="only marks,mark=*")],
                    "Observed minus fit",
                ),
            ],
            xlabel="Source distance (m)",
        ),
        SLUGS[2]: figure(
            [
                panel(
                    "Signal (counts)",
                    [
                        curve(
                            "optics-manual-observations",
                            1,
                            "Snapshot",
                            0,
                            options="only marks,mark=*",
                        ),
                        curve("optics-manual-fit", 1, "Mean fit", 1),
                    ],
                    "Ruler observations",
                ),
                panel(
                    r"$Qr^2$ (count m$^2$)",
                    [
                        curve(
                            "optics-manual-observations",
                            2,
                            "Snapshot",
                            0,
                            options="only marks,mark=*",
                        ),
                        curve(
                            "optics-manual-observations",
                            4,
                            "2-s mean",
                            2,
                            options="only marks,mark=triangle*",
                        ),
                    ],
                    "Position-normalized signal",
                ),
            ],
            xlabel="Ruler distance (m)",
        ),
        SLUGS[3]: figure(
            [
                panel(
                    "Transmission (1)",
                    [
                        curve(
                            "optics-malus-observations",
                            1,
                            "Snapshot",
                            0,
                            options="only marks,mark=*",
                        ),
                        curve("optics-malus-fit", 1, "Mean fit", 1),
                    ],
                    "Polarization response",
                    options=r"width=0.96\columnwidth",
                ),
                panel(
                    "Residual (1)",
                    [
                        curve(
                            "optics-malus-observations",
                            4,
                            "Snapshot",
                            0,
                            options="only marks,mark=*",
                        ),
                        curve(
                            "optics-malus-observations",
                            5,
                            "4.5-s mean",
                            2,
                            options="only marks,mark=triangle*",
                        ),
                    ],
                    r"Relative to $\cos^2\theta$",
                    options=r"width=0.96\columnwidth",
                ),
            ],
            xlabel="Analyzer angle (degree)",
        ),
        SLUGS[4]: figure(
            [
                panel(
                    "Indicative CCT (K)",
                    [curve("colour-temperature", 18)],
                    "Provisional conversion",
                ),
                panel(
                    "Chromaticity (1)",
                    [
                        curve("colour-temperature", 14, "$x$", 0),
                        curve("colour-temperature", 15, "$y$", 1),
                    ],
                    "Matrix-derived chromaticities",
                ),
            ]
        ),
        SLUGS[5]: figure(
            [
                panel(
                    "Clear (counts)",
                    [curve("detector-characterization", 2)],
                    "Baseline and short features",
                ),
                panel(
                    "Clear (counts)",
                    [curve("detector-characterization", 2)],
                    "Feature detail",
                    options="xmin=29,xmax=49,ymin=920,ymax=1060",
                ),
                panel(
                    "Interval (ms)",
                    [
                        curve("optics-detector-intervals", 1, "Device", 0),
                        curve("optics-detector-intervals", 2, "Receive", 1),
                    ],
                    "Successive notifications",
                ),
            ]
        ),
    }


def check() -> None:
    """Independent exact-model fixtures for fit algebra and invalid colour domains."""
    result = linear([0, 1, 2], [1, 3, 5])
    assert result == {"slope": 2, "intercept": 1, "residual_sd": 0}
    power = power_fit([[0.2, 2500], [0.4, 625], [0.8, 156.25]])
    assert math.isclose(power["exponent"], 2, abs_tol=1e-12)
    assert math.isclose(power["amplitude"], 100, abs_tol=1e-10)
    angles = [0, 30, 60, 90]
    signals = [5 + 100 * math.cos(math.radians(angle - 10)) ** 2 for angle in angles]
    fit = malus_fit(angles, signals)
    assert math.isclose(fit["floor_counts"], 5, abs_tol=1e-10)
    assert math.isclose(fit["amplitude_counts"], 100, abs_tol=1e-10)
    assert math.isclose(fit["angle_zero_deg"], 10, abs_tol=1e-10)
    # A homogeneous RGB transform loses the common clear denominator in x,y,CCT.
    first, second = colour([2000, 1200, 1200, 300]), colour([3000, 1200, 1200, 300])
    assert all(math.isclose(a, b, abs_tol=1e-10) for a, b in zip(first, second))
    for raw in [[3, 10, 10, 10], [100, -1, 10, 10], [math.nan, 10, 10, 10]]:
        assert all(math.isnan(value) for value in colour(raw))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_root", type=Path)
    args = parser.parse_args()
    check()
    print(json.dumps(analyze(args.data_root), indent=2, allow_nan=False))
