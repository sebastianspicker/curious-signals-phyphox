#!/usr/bin/env python3
"""Reproducible reductions of the five photometry lessons (standard library).

Device time defines plateau windows where present. Receive time remains a
separate plotted/acquisition clock. One-second block dispersion is a diagnostic
of fluctuation, not a standard error inferred from all recorded rows.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics as st
from pathlib import Path

from _common import draft_rows as read
from _common import in_window

SLUGS = (
    "nano-transit",
    "exomoon-photometry",
    "starspot-crossing",
    "eclipsing-binary",
    "seasons-obliquity",
)


def selected(
    rows: list[list[float]], windows: list[tuple[float, float]], clock: int = 1
) -> list[list[float]]:
    return [r for r in rows if any(in_window(r[clock], a, b) for a, b in windows)]


def state(rows: list[list[float]], windows: list[tuple[float, float]]) -> dict:
    picked = selected(rows, windows)
    values = [r[2] for r in picked if math.isfinite(r[2])]
    blocks = []
    for a, b in windows:
        for i in range(math.floor(b - a)):
            vv = [r[2] for r in picked if a + i <= r[1] < a + i + 1 and math.isfinite(r[2])]
            if vv:
                blocks.append(st.mean(vv))
    return dict(
        mean=st.mean(values),
        sample_sd=st.stdev(values),
        n=len(values),
        block_sd=st.stdev(blocks) if len(blocks) > 1 else None,
        block_means=blocks,
        block_count=len(blocks),
        windows=windows,
        clock="device seconds",
        unit="count",
    )


def clocks(rows: list[list[float]]) -> dict:
    return {
        "median_receive_interval_s": st.median(b[0] - a[0] for a, b in zip(rows, rows[1:])),
        "median_device_interval_s": st.median(b[1] - a[1] for a, b in zip(rows, rows[1:])),
        "receive_span_s": rows[-1][0] - rows[0][0],
        "device_span_s": rows[-1][1] - rows[0][1],
        "method": "Adjacent differences within each clock; no clock alignment.",
    }


def depth(baseline: float, plateau: float, dark: float = 10) -> float:
    return (baseline - plateau) / (baseline - dark) if baseline > dark else math.nan


def transit_metrics(rows: list[list[float]]) -> dict:
    events = []
    for c in (20, 50, 80):
        base = state(rows, [(c - 6, c - 3), (c + 3, c + 6)])
        plate = state(rows, [(c - 1, c + 1)])
        d = depth(base["mean"], plate["mean"])
        events.append(
            dict(
                center_s=c,
                baseline=base,
                plateau=plate,
                depth=d,
                apparent_projected_radius_ratio=math.sqrt(d),
            )
        )
    baseline = st.mean(e["baseline"]["mean"] for e in events)
    return dict(
        clocks=clocks(rows),
        dark_adopted_count=10,
        stored_reference_count=110,
        events=events,
        mean_depth=st.mean(e["depth"] for e in events),
        event_depth_sd=st.stdev(e["depth"] for e in events),
        mean_baseline_count=baseline,
        stored_out_of_event_normalized=(baseline - 10) / 100,
        raw_extrema_depth=depth(max(r[2] for r in rows), min(r[2] for r in rows)),
        projected_ratio=math.sqrt(st.mean(e["depth"] for e in events)),
        interpretation="Depth scatter across three events, not a sample-count standard error.",
    )


def moon_metrics(rows: list[list[float]]) -> dict:
    windows = {
        "baseline": [(3, 17), (93, 107)],
        "planet": [(22, 33), (77, 88)],
        "separated": [(37, 48), (62, 73)],
        "overlap": [(52, 58)],
    }
    ss = {key: state(rows, w) for key, w in windows.items()}
    b, p, s, o = [ss[k]["mean"] for k in ("baseline", "planet", "separated", "overlap")]
    den = b - 10
    return dict(
        clocks=clocks(rows),
        states=ss,
        dark_adopted_count=10,
        extra_depth=(p - s) / den,
        overlap_brightening=(o - s) / den,
        recovered_fraction=(o - s) / (p - s),
        planet_depth=(b - p) / den,
        separated_depth=(b - s) / den,
        overlap_depth=(b - o) / den,
        extra_block_scale=math.hypot(ss["planet"]["block_sd"], ss["separated"]["block_sd"]) / den,
        brightening_block_scale=math.hypot(ss["overlap"]["block_sd"], ss["separated"]["block_sd"])
        / den,
        uncertainty_note="Quadrature of state one-second block SDs / (baseline-10); "
        "fluctuation scale, not confidence interval for a mean.",
    )


def spot_metrics(rows: list[list[float]]) -> dict:
    windows = {
        "baseline": [(5, 15), (65, 75), (95, 105)],
        "control": [(20.5, 23.5), (80.5, 83.5)],
        "adjacent": [(45.5, 48.5), (55.5, 58.5)],
        "crossing": [(50.5, 53.5)],
    }
    ss = {key: state(rows, w) for key, w in windows.items()}
    b, a, x, c = [ss[k]["mean"] for k in ("baseline", "adjacent", "crossing", "control")]
    return dict(
        clocks=clocks(rows),
        states=ss,
        dark_adopted_count=10,
        anomaly_contrast=(x - a) / (b - 10),
        adjacent_depth=depth(b, a),
        crossing_depth=depth(b, x),
        control_depth=depth(b, c),
        deficit_recovered=(x - a) / (b - a),
        inappropriate_radius_factor=math.sqrt((b - x) / (b - a)),
        anomaly_block_scale=math.hypot(ss["adjacent"]["block_sd"], ss["crossing"]["block_sd"])
        / (b - 10),
        note="One-second blocks describe fluctuation; control is a separate "
        "depth comparison, not evidence for equal occulted area.",
    )


def binary_metrics(rows: list[list[float]]) -> dict:
    groups = {}
    for kind, centers in [("primary", (20, 50, 80, 110)), ("secondary", (35, 65, 95))]:
        events = []
        for c in centers:
            base = state(rows, [(c - 6, c - 3), (c + 3, c + 6)])
            plate = state(rows, [(c - 0.75, c + 0.75)])
            level = (base["mean"] + plate["mean"]) / 2
            # Large-amplitude primary crossings are localized within each event.
            falling = next(r for r in rows if c - 3 <= r[1] < c and r[2] < level)
            events.append(
                dict(
                    center_s=c,
                    baseline=base,
                    plateau=plate,
                    depth=depth(base["mean"], plate["mean"]),
                    half_depth_onset_receive_s=falling[0],
                    half_depth_onset_device_s=falling[1],
                )
            )
        groups[kind] = dict(
            events=events,
            mean_depth=st.mean(e["depth"] for e in events),
            event_depth_sd=st.stdev(e["depth"] for e in events),
        )
    onsets = [e["half_depth_onset_receive_s"] for e in groups["primary"]["events"]]
    periods = [b - a for a, b in zip(onsets, onsets[1:])]
    p, s = [groups[k]["mean_depth"] for k in ("primary", "secondary")]
    return dict(
        clocks=clocks(rows),
        groups=groups,
        primary_minus_secondary=p - s,
        depth_ratio=p / s,
        primary_onset_intervals_s=periods,
        mean_onset_period_s=st.mean(periods),
        interval_sd_s=st.stdev(periods),
        endpoint_period_s=(onsets[-1] - onsets[0]) / 3,
        phase_epoch_receive_s=20,
        phase_period_s=30,
        max_stored_phase_residual=max(abs(r[7] - ((r[0] - 20) / 30) % 1) for r in rows),
        note="Intervals share endpoints; SD is descriptive, not uncertainty "
        "of independent replicated periods. Adopted background 10 counts.",
    )


def season_metrics(raw: list[list[float]], observations: list[list[float]]) -> dict:
    records = []
    for index, row in enumerate(observations):
        plateau = state(raw, [(5 * index + 1, 5 * index + 4)])
        nearest = min(raw, key=lambda r: abs(r[1] - row[0]))
        assert nearest[:6] == [row[1], row[0], *row[2:6]]
        relative = (row[2] - row[12]) / (row[13] - row[12])
        assert abs(relative - row[14]) < 1e-8
        records.append(
            dict(
                trial=int(row[6]),
                latitude_deg=row[7],
                orbit_label_deg=row[8],
                obliquity_deg=row[9],
                distance_cm=row[10],
                snapshot_count=row[2],
                relative=relative,
                plateau=plateau,
                plateau_relative=(plateau["mean"] - row[12]) / (row[13] - row[12]),
                snapshot_minus_plateau_count=row[2] - plateau["mean"],
            )
        )
    lookup = {(r["obliquity_deg"], r["latitude_deg"], r["orbit_label_deg"]): r for r in records}
    contrasts = []
    for tilt in (0, 23.5):
        for lat in (-60, 0, 60):
            one, two = [lookup[(tilt, lat, p)]["relative"] for p in (0, 180)]
            contrasts.append(
                dict(
                    obliquity_deg=tilt,
                    latitude_deg=lat,
                    orbit180_minus_orbit0=two - one,
                    orbit180_over_orbit0=two / one,
                )
            )
    symmetry = []
    for tilt in (0, 23.5):
        for orbit in (0, 180):
            north, south = [lookup[(tilt, lat, orbit)]["relative"] for lat in (60, -60)]
            symmetry.append(
                dict(obliquity_deg=tilt, orbit_label_deg=orbit, north_minus_south=north - south)
            )
    return dict(
        clocks=clocks(raw),
        observations=records,
        orbital_contrasts=contrasts,
        hemisphere_contrasts=symmetry,
        distances_cm=sorted({r["distance_cm"] for r in records}),
        max_snapshot_plateau_difference_count=max(
            abs(r["snapshot_minus_plateau_count"]) for r in records
        ),
        note="Twelve distinct labelled settings, one snapshot each; no independent "
        "replicate uncertainty. Each snapshot checked against raw acquisition.",
    )


def analyze(data_root: Path) -> dict[str, dict]:
    result = {}
    for slug in SLUGS:
        rows = read(data_root, slug)
        reducer = {
            "nano-transit": transit_metrics,
            "exomoon-photometry": moon_metrics,
            "starspot-crossing": spot_metrics,
            "eclipsing-binary": binary_metrics,
        }.get(slug)
        result[slug] = (
            reducer(rows)
            if reducer
            else season_metrics(rows, read(data_root, "seasons-obliquity_observations"))
        )
    return result


def tables(data_root: Path) -> dict[str, list[list[float]]]:
    result = {}
    for slug in SLUGS[:-1]:
        rows = read(data_root, slug)
        binned = []
        # The final partial second is deliberately dropped so every block averages a full second.
        for start in range(120):
            block = selected(rows, [(start, start + 1)])
            if block:
                binned.append(
                    [
                        st.mean(r[0] for r in block),
                        st.mean(r[2] for r in block),
                        st.stdev(r[2] for r in block),
                    ]
                )
        result["drafts/" + slug + "-blocks"] = binned
    obs = read(data_root, "seasons-obliquity_observations")
    bykey = {(r[9], r[8], r[7]): r[14] for r in obs}
    result["drafts/seasons-obliquity-latitude"] = [
        [lat, *[bykey[(tilt, orbit, lat)] for tilt in (0, 23.5) for orbit in (0, 180)]]
        for lat in (-60, 0, 60)
    ]
    return result


def curve(
    name: str, column: int, label: str, color: int = 0, x: int = 0, options: str = ""
) -> dict:
    return dict(
        file="drafts/" + name,
        column=column,
        label=label,
        color=color,
        x=x,
        scale=1,
        offset=0,
        options=options,
    )


def figures() -> dict[str, dict]:
    result = {}
    ranges = {
        "nano-transit": ("xmin=10,xmax=90", "Three transits"),
        "exomoon-photometry": ("xmin=10,xmax=100", "Separated and overlapping silhouettes"),
        "starspot-crossing": ("xmin=40,xmax=64", "Local upward anomaly"),
        "eclipsing-binary": ("xmin=10,xmax=118", "Alternating minima"),
    }
    for slug, (limits, title) in ranges.items():
        result[slug] = dict(
            panels=[
                dict(
                    ylabel="Clear (count)",
                    curves=[
                        curve(slug, 2, "Raw", 0, options="opacity=0.30"),
                        curve(slug + "-blocks", 1, "1 s means", 1),
                    ],
                    options=limits,
                    title=title,
                )
            ],
            xlabel="Receive time (s)",
            height="4.4cm",
        )
    result["seasons-obliquity"] = dict(
        panels=[
            dict(
                ylabel="Clear (count)",
                curves=[curve("seasons-obliquity", 2, "", 0)],
                options=r"xmin=0,xmax=60,width=0.96\columnwidth",
                title="Receive time (s)",
            ),
            dict(
                ylabel="Relative response",
                curves=[
                    curve("seasons-obliquity-latitude", i + 1, label, i, options="mark=*")
                    for i, label in enumerate(
                        [r"$0^\circ$, A", r"$0^\circ$, B", r"$23.5^\circ$, A", r"$23.5^\circ$, B"]
                    )
                ],
                options=r"xmin=-65,xmax=65,xtick={-60,0,60},width=0.96\columnwidth",
                title="A/B: orbital labels 0/180 deg",
            ),
        ],
        xlabel="Latitude (deg)",
        height="3.4cm",
    )
    return result


def check(data_root: Path) -> None:
    """Independent dimensional/domain and current-observation checks."""
    assert math.isclose(depth(110, 106, 10), 0.04)
    assert math.isclose(depth(225, 217, 25), 0.04)  # affine response with matched dark
    assert math.isnan(depth(10, 9, 10))
    assert math.isnan(depth(9, 8, 10))
    b, p, d = 115.0, 111.0, 10.0
    expected = ((p - d) / (b - d) ** 2, -1 / (b - d), (b - p) / (b - d) ** 2)
    for index, derivative in enumerate(expected):
        above, below = [b, p, d], [b, p, d]
        above[index] += 1e-4
        below[index] -= 1e-4
        numeric = (depth(*above) - depth(*below)) / 2e-4
        assert math.isclose(numeric, derivative, rel_tol=1e-8)
    metrics = analyze(data_root)
    # Independent fsum of current raw count windows, with exact calendar boundaries.
    rows = read(data_root, "nano-transit")
    base = [r[2] for r in rows if 14 <= r[1] < 17 or 23 <= r[1] < 26]
    plateau = [r[2] for r in rows if 19 <= r[1] < 21]
    raw_b, raw_p = math.fsum(base) / len(base), math.fsum(plateau) / len(plateau)
    first = metrics["nano-transit"]["events"][0]
    assert math.isclose(first["depth"], (raw_b - raw_p) / (raw_b - 10), rel_tol=1e-14)
    for slug in ("nano-transit", "exomoon-photometry", "starspot-crossing"):
        for row in read(data_root, slug):
            assert abs(row[6] - (row[2] - 10) / 100) < 1e-8
    assert metrics["eclipsing-binary"]["max_stored_phase_residual"] < 2e-8
    obs = read(data_root, "seasons-obliquity_observations")
    assert obs[0][2] == 579 and math.isclose(obs[0][14], 569 / 1090, abs_tol=1e-9)
    # Opposite hemispheres have the same-sign A/B change: cannot label it a reversal.
    contrasts = metrics["seasons-obliquity"]["orbital_contrasts"]
    assert all(row["orbit180_minus_orbit0"] < 0 for row in contrasts)
    assert len(metrics["seasons-obliquity"]["observations"]) == 12
    print(
        "Photometry: affine-depth/domain, derivative, raw-window, phase "
        "and paired-label checks pass."
    )


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
