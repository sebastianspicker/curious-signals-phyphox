"""Reproducible reductions for four observation papers; standard library only."""

from __future__ import annotations

import json
import math
import statistics as stats
from pathlib import Path

from _common import draft_rows as read
from _common import ols, saturation_pressure_kPa, saturation_temperature_K

R_GAS = 8.31446261815324


def slope(x: list[float], y: list[float]) -> tuple[float, float]:
    b, a = ols(x, y)
    return a, b


def pressure_metrics(rows: list[list[float]]) -> dict:
    residuals = []
    for row in rows:
        ts = saturation_temperature_K(row[1])
        derivative = (
            saturation_pressure_kPa(ts + 0.001) - saturation_pressure_kPa(ts - 0.001)
        ) / 0.002
        u = math.hypot(row[6], row[5] / derivative)
        residuals.append(
            dict(
                id=int(row[0]),
                code=int(row[3]),
                pressure_kpa=row[1],
                temperature_c=row[2],
                saturation_temperature_c=ts - 273.15,
                residual_k=row[2] + 273.15 - ts,
                u_residual_k=u,
            )
        )
    boiling = [row for row in rows if row[3] == 1 and row[4] == 1]
    aa, bb = slope(
        [1 / (row[2] + 273.15) for row in boiling], [math.log(row[1]) for row in boiling]
    )
    by_code = {
        str(code): dict(
            n=sum(r["code"] == code for r in residuals),
            mean_residual_k=stats.mean(r["residual_k"] for r in residuals if r["code"] == code),
        )
        for code in (0, 1, 2)
    }
    return dict(
        n=len(rows),
        n_boiling=len(boiling),
        n_checked=sum(row[4] == 1 for row in rows),
        pressure_range_kpa=[min(row[1] for row in rows), max(row[1] for row in rows)],
        temperature_range_c=[min(row[2] for row in rows), max(row[2] for row in rows)],
        method="All paired rows; code 1 only for ln(p) vs 1/T OLS",
        units=dict(pressure="kPa absolute", temperature="K", molar_enthalpy="kJ/mol"),
        saturation_reference="IAPWS SR1-86(1992), page3 Eq1; bisection inversion",
        residuals=residuals,
        by_code=by_code,
        intercept=aa,
        inverse_temperature_slope_k=bb,
        apparent_enthalpy_kj_mol=-bb * R_GAS / 1000,
        boiling_rms_residual_k=math.sqrt(
            stats.mean(r["residual_k"] ** 2 for r in residuals if r["code"] == 1)
        ),
        maximum_boiling_abs_z=max(
            abs(r["residual_k"]) / r["u_residual_k"] for r in residuals if r["code"] == 1
        ),
    )


def spectral_metrics(rows: list[list[float]]) -> dict:
    values = []
    for row in rows:
        sample = (row[3] - row[6]) / (row[5] - row[6])
        star = (row[4] - row[6]) / (row[5] - row[6])
        values.append(
            dict(
                wavelength_nm=row[1],
                sample_transmission=sample,
                star_transmission=star,
                extra_depth=1 - sample / star,
                reference_offset_nm=row[1] - row[2],
            )
        )
    by_wave = {r["wavelength_nm"]: r for r in values}
    line = by_wave[595]
    local_star = (by_wave[580]["star_transmission"] + by_wave[610]["star_transmission"]) / 2
    local_sample = (by_wave[580]["sample_transmission"] + by_wave[610]["sample_transmission"]) / 2
    return dict(
        n=len(rows),
        wavelength_range_nm=[rows[0][1], rows[-1][1]],
        grid_step_nm=15,
        method="Dark-subtracted ratios at each common wavelength; 595nm local baseline=(580+610)/2",
        uncertainties=(
            "Only wavelength standard uncertainty is present (0.2nm); no intensity "
            "uncertainty supplied"
        ),
        values=values,
        sample_depth_at_595=1 - line["sample_transmission"],
        star_local_dip_at_595=1 - line["star_transmission"] / local_star,
        sample_local_dip_at_595=1 - line["sample_transmission"] / local_sample,
        differential_excess_at_595=line["extra_depth"]
        - (by_wave[580]["extra_depth"] + by_wave[610]["extra_depth"]) / 2,
        min_extra_depth=min(r["extra_depth"] for r in values),
        max_extra_depth=max(r["extra_depth"] for r in values),
        sodium_doublet_separation_nm=0.5974,
        grid_to_sodium_spacing=15 / 0.5974,
    )


def contrast_metrics(rows: list[list[float]]) -> dict:
    summary = []
    for separation in sorted({r[2] for r in rows}):
        groups = {mask: [r for r in rows if r[1] == mask and r[2] == separation] for mask in (0, 1)}
        item = dict(separation_pixel=separation)
        for mask, subset in groups.items():
            net = stats.mean(r[4] - r[5] for r in subset)
            background = stats.mean(r[5] for r in subset)
            u = math.sqrt(sum(r[6] ** 2 for r in subset)) / len(subset)
            item["masked" if mask else "unmasked"] = dict(
                n=len(subset),
                net=net,
                background=background,
                contrast=net / background,
                mean_individual_snr=stats.mean((r[4] - r[5]) / r[6] for r in subset),
                u_mean_net_if_independent=u,
            )
        item["net_retention"] = item["masked"]["net"] / item["unmasked"]["net"]
        item["background_retention"] = item["masked"]["background"] / item["unmasked"]["background"]
        item["snr_retention"] = (
            item["masked"]["mean_individual_snr"] / item["unmasked"]["mean_individual_snr"]
        )
        summary.append(item)
    return dict(
        n=len(rows),
        n_repeats=2,
        exposure_ms=10,
        method="Two observations per mask/separation; ratios of group means for contrast",
        uncertainty_note=(
            "ROI difference uncertainties retained; combining two rows presumes independent errors"
        ),
        groups=summary,
        mean_net_retention=stats.mean(r["net_retention"] for r in summary),
        mean_background_retention=stats.mean(r["background_retention"] for r in summary),
        mean_snr_retention=stats.mean(r["snr_retention"] for r in summary),
    )


def uv_metrics(raw: list[list[float]], observations: list[list[float]]) -> dict:
    windows = [
        (1, 4, "dark"),
        (6, 9, "reference"),
        (11, 14, "sample310a"),
        (16, 19, "sample250a"),
        (21, 24, "sample180"),
        (26, 29, "sample310b"),
        (31, 34, "sample250b"),
        (36, 39, "sample310c"),
    ]
    plateaux = []
    for start, stop, label in windows:
        chosen = [r[2] for r in raw if start <= r[0] < stop]
        plateaux.append(
            dict(
                label=label,
                start_s=start,
                stop_s=stop,
                n=len(chosen),
                mean_count=stats.mean(chosen),
                sd_count=stats.stdev(chosen),
            )
        )
    device_dt = [b[0] - a[0] for a, b in zip(raw, raw[1:])]
    delays = [r[1] - r[0] for r in raw]
    # A conservative precision illustration uses one plateau SD per reading,
    # not SD/sqrt(n): autocorrelation and independent remounting are unknown.
    lookup = {p["label"]: p for p in plateaux}
    sref, sdark = lookup["reference"]["sd_count"], lookup["dark"]["sd_count"]
    checked = []
    for row, label in zip(
        observations,
        ["sample310a", "sample250a", "sample180", "sample310b", "sample250b", "sample310c"],
        strict=True,
    ):
        q, ref, dark = row[9], row[1], row[2]
        trans = (q - dark) / (ref - dark)
        ss = lookup[label]["sd_count"]
        utrans = math.sqrt(ss**2 + trans**2 * sref**2 + (trans - 1) ** 2 * sdark**2) / (ref - dark)
        nearest = min(raw, key=lambda reading: abs(reading[0] - row[10]))
        assert abs(nearest[0] - row[10]) < 1e-6
        assert abs(nearest[1] - row[11]) < 1e-6
        checked.append(
            dict(
                id=int(row[0]),
                sample_count=q,
                raw_at_time_count=nearest[2],
                observation_minus_raw_count=q - nearest[2],
                transmission_from_raw=(nearest[2] - dark) / (ref - dark),
                transmission=trans,
                u_transmission_type_a=utrans,
                voltage_v=q * row[4] + row[5],
                irradiance_w_m2=row[7] * row[4] * (q - dark),
                device_time_s=row[10],
                receive_time_s=row[11],
                nominal_quantization_u_transmission=math.sqrt(1 + trans**2 + (trans - 1) ** 2)
                / (math.sqrt(12) * (ref - dark)),
            )
        )
    return dict(
        n_raw=len(raw),
        device_time_range_s=[raw[0][0], raw[-1][0]],
        n_observations=len(observations),
        windows=plateaux,
        method=(
            "Interior half-open windows in device time; separate receive clock; "
            "single-reading SD uncertainty illustration"
        ),
        median_device_dt_s=stats.median(device_dt),
        mean_device_dt_s=stats.mean(device_dt),
        delivered_rate_hz=(len(raw) - 1) / (raw[-1][0] - raw[0][0]),
        mean_clock_offset_s=stats.mean(delays),
        min_clock_offset_s=min(delays),
        max_clock_offset_s=max(delays),
        clock_note=(
            "receive-device offset is not measured network latency without synchronized "
            "clock origins"
        ),
        maximum_observation_raw_difference_count=max(
            abs(r["observation_minus_raw_count"]) for r in checked
        ),
        maximum_observation_raw_transmission_difference=max(
            abs(r["transmission"] - r["transmission_from_raw"]) for r in checked
        ),
        observations=checked,
        adc_gain_v_count=observations[0][4],
        detector_gain_w_m2_v=observations[0][7],
        calibration_note=(
            "Absolute scale conditional on entered coefficients; no coefficient "
            "uncertainty available"
        ),
    )


def analyze(data_root: Path) -> dict[str, dict]:
    return {
        "pressure-boiling": pressure_metrics(read(data_root, "pressure-boiling")),
        "spectral-fingerprints": spectral_metrics(read(data_root, "spectral-fingerprints")),
        "coronagraph-contrast": contrast_metrics(read(data_root, "coronagraph-contrast")),
        "uv-transmission": uv_metrics(
            read(data_root, "uv-transmission_raw"), read(data_root, "uv-transmission_observations")
        ),
    }


def tables(data_root: Path) -> dict[str, list[list[float]]]:
    metrics = analyze(data_root)
    pressure = metrics["pressure-boiling"]
    pressure_table = []
    for i in range(151):
        temp = 303.15 + i * 0.5
        pressure_table.append([temp - 273.15, saturation_pressure_kPa(temp)])
    contrast = []
    for item in metrics["coronagraph-contrast"]["groups"]:
        contrast.append(
            [
                item["separation_pixel"],
                item["unmasked"]["contrast"],
                item["masked"]["contrast"],
                item["unmasked"]["mean_individual_snr"],
                item["masked"]["mean_individual_snr"],
            ]
        )
    assert pressure["n_boiling"] == 5
    return {
        "drafts/pressure-boiling-saturation": pressure_table,
        "drafts/coronagraph-contrast-summary": contrast,
    }


def curve(file: str, column: int, label: str, color: int = 0, x: int = 0, **kwargs) -> dict:
    return dict(
        file="drafts/" + file,
        column=column,
        label=label,
        color=color,
        x=x,
        scale=kwargs.pop("scale", 1),
        offset=kwargs.pop("offset", 0),
        options=kwargs.pop("options", ""),
    )


def figures() -> dict[str, dict]:
    return {
        "pressure-boiling": dict(
            xlabel=r"Liquid temperature ($^\circ$C)",
            height="4.0cm",
            panels=[
                dict(
                    ylabel="Absolute pressure (kPa)",
                    title="",
                    options="",
                    curves=[
                        curve("pressure-boiling-saturation", 1, "Saturation", 0),
                        curve(
                            "pressure-boiling", 1, "All pairs", 1, x=2, options="only marks,mark=o"
                        ),
                        curve(
                            "pressure-boiling", 9, "Boiling", 2, x=2, options="only marks,mark=*"
                        ),
                    ],
                )
            ],
        ),
        "spectral-fingerprints": dict(
            xlabel="Wavelength (nm)",
            height="3.4cm",
            panels=[
                dict(
                    ylabel="Normalized intensity",
                    title="",
                    options="",
                    curves=[
                        curve("spectral-fingerprints", 10, "Sample", 0, x=1, options="mark=*"),
                        curve(
                            "spectral-fingerprints", 11, "Star-only", 1, x=1, options="mark=square*"
                        ),
                    ],
                ),
                dict(
                    ylabel="Additional depth",
                    title="",
                    options="",
                    curves=[curve("spectral-fingerprints", 13, "", 2, x=1, options="mark=*")],
                ),
            ],
        ),
        "coronagraph-contrast": dict(
            xlabel="Image separation (pixel)",
            height="3.4cm",
            panels=[
                dict(
                    ylabel="Local contrast",
                    title="",
                    options="",
                    curves=[
                        curve("coronagraph-contrast-summary", 1, "Unmasked", 0, options="mark=*"),
                        curve(
                            "coronagraph-contrast-summary", 2, "Masked", 1, options="mark=square*"
                        ),
                    ],
                ),
                dict(
                    ylabel=r"$N/u_N$",
                    title="",
                    options="",
                    curves=[
                        curve("coronagraph-contrast-summary", 3, "", 0, options="mark=*"),
                        curve("coronagraph-contrast-summary", 4, "", 1, options="mark=square*"),
                    ],
                ),
            ],
        ),
        "uv-transmission": dict(
            xlabel="Device time (s)",
            height="3.4cm",
            panels=[
                dict(
                    ylabel="A0 (count)",
                    title="",
                    options="xmin=0,xmax=40",
                    curves=[curve("uv-transmission_raw", 2, "", 0)],
                ),
                dict(
                    ylabel="Transmission",
                    title="",
                    options="xmin=0,xmax=40,ymin=0,ymax=1",
                    curves=[
                        curve(
                            "uv-transmission_observations",
                            12,
                            "",
                            1,
                            x=10,
                            options="only marks,mark=*",
                        )
                    ],
                ),
            ],
        ),
    }


def check(data_root: Path) -> None:
    result = analyze(data_root)
    assert slope([1, 2, 3], [4, 6, 8]) == (2, 2)
    assert math.isclose(saturation_pressure_kPa(373.15), 101.41799, abs_tol=0.002)
    assert math.isclose(saturation_pressure_kPa(273.16), 0.611657, abs_tol=0.00001)
    try:
        saturation_pressure_kPa(250)
    except ValueError:
        pass
    else:
        raise AssertionError("expected out-of-range saturation to raise")
    assert abs(saturation_temperature_K(101.325) - 373.124) < 0.02
    for slug, column_pairs in [
        (
            "spectral-fingerprints",
            [
                (10, lambda r: (r[3] - r[6]) / (r[5] - r[6])),
                (13, lambda r: 1 - (r[3] - r[6]) / (r[4] - r[6])),
            ],
        ),
        (
            "coronagraph-contrast",
            [(9, lambda r: r[4] - r[5]), (12, lambda r: (r[4] - r[5]) / r[6])],
        ),
    ]:
        for row in read(data_root, slug):
            for column, expected in column_pairs:
                assert math.isclose(row[column], expected(row), rel_tol=1e-7, abs_tol=1e-7)
    assert result["pressure-boiling"]["n_boiling"] == 5
    assert 42 < result["pressure-boiling"]["apparent_enthalpy_kj_mol"] < 43
    assert result["uv-transmission"]["maximum_observation_raw_difference_count"] == 3
    assert result["uv-transmission"]["observations"][0]["transmission"] == 0.5
    assert result["uv-transmission"]["observations"][2]["transmission"] == 17 / 60
    assert all(r["snr_retention"] < 1 for r in result["coronagraph-contrast"]["groups"])
    for config in figures().values():
        for panel in config["panels"]:
            for item in panel["curves"]:
                assert item["x"] >= 0
    json.dumps(result, allow_nan=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-root", type=Path, default=Path(__file__).resolve().parents[3] / "example-data"
    )
    args = parser.parse_args()
    check(args.data_root)
    print(json.dumps(analyze(args.data_root), indent=2))
