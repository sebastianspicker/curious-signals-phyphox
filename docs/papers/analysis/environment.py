"""Reproduce the pressure, humidity and voltage paper examples (stdlib only)."""

from __future__ import annotations

import json
import math
import statistics
import sys
from functools import partial
from pathlib import Path

from _common import PRESSURE_BASELINE_S, read_dicts
from _common import window as _window

window = partial(_window, clock="Time t (s)")


def mean(record: list[dict[str, float]], column: str) -> float:
    return statistics.fmean(row[column] for row in record)


def summary(record: list[dict[str, float]], column: str) -> dict:
    values = [row[column] for row in record]
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "sd": statistics.stdev(values),
        "minimum": min(values),
        "maximum": max(values),
    }


def pressure_difference(record, pre, event, post):
    column = "Pressure (hPa)"
    before, during, after = [window(record, *bounds) for bounds in (pre, event, post)]
    t0, te, t1 = [mean(part, "Time t (s)") for part in (before, during, after)]
    fraction = (te - t0) / (t1 - t0)
    baseline = (1 - fraction) * mean(before, column) + fraction * mean(after, column)
    pe = mean(during, column)
    return {
        "pre_window_s": pre,
        "event_window_s": event,
        "post_window_s": post,
        "event_n": len(during),
        "baseline_interpolated_hpa": baseline,
        "event_mean_hpa": pe,
        "event_sd_hpa": statistics.stdev(row[column] for row in during),
        "change_hpa": pe - baseline,
        "height_m_at_293_15K": 287.05 * 293.15 / 9.80665 * math.log(baseline / pe),
    }


def fit_exponential(record, start, stop, column, t0):
    data = window(record, start, stop)
    times = [row["Time t (s)"] - t0 for row in data]
    values = [row[column] for row in data]
    ym = statistics.fmean(values)

    def profile(tau):
        basis = [math.exp(-t / tau) for t in times]
        xm = statistics.fmean(basis)
        amplitude = sum((x - xm) * (y - ym) for x, y in zip(basis, values)) / sum(
            (x - xm) ** 2 for x in basis
        )
        asymptote = ym - amplitude * xm
        sse = sum((y - asymptote - amplitude * x) ** 2 for x, y in zip(basis, values))
        return sse, asymptote, amplitude

    low, high = bounds = 0.3, 3.0
    ratio = (math.sqrt(5) - 1) / 2
    for _ in range(100):
        left, right = high - ratio * (high - low), low + ratio * (high - low)
        if profile(left)[0] < profile(right)[0]:
            high = right
        else:
            low = left
    tau = (low + high) / 2
    if any(abs(tau - bound) < 1e-6 for bound in bounds):
        raise ValueError("tau search ended at its bound; widen the search interval")
    sse, asymptote, amplitude = profile(tau)
    return {
        "window_s": [start, stop],
        "n": len(data),
        "t0_s": t0,
        "tau_s": tau,
        "asymptote_mv": asymptote,
        "amplitude_mv": amplitude,
        "residual_rms_mv": math.sqrt(sse / len(data)),
        "model": (
            "U=asymptote+amplitude*exp(-(t-t0)/tau); profile OLS; "
            "free asymptote/amplitude; golden-section tau"
        ),
    }


def analyze(data_root: Path) -> dict:
    pressure = read_dicts(data_root / "core" / "pressure_plot_v1-2.example.csv")
    humidity = read_dicts(data_root / "core" / "temperature_plot_v1-2.example.csv")
    analog = read_dicts(data_root / "core" / "analog_input_plot_v1-2.example.csv")
    first_breath = window(humidity, 35, 60)
    heating = window(humidity, 65, 115)
    temp_max = max(heating, key=lambda row: row["Temperature (°C)"])
    rh_min = min(heating, key=lambda row: row["relative Humidity (%)"])
    breath_max = max(first_breath, key=lambda row: row["relative Humidity (%)"])
    baseline_humidity = window(humidity, 20, 30)
    result = {
        "window_convention": "start inclusive, stop exclusive; all times use Time t (s)",
        "pressure": {
            "file": "core/pressure_plot_v1-2.example.csv",
            "samples": len(pressure),
            "lift": pressure_difference(pressure, [20, 28], [36, 42], [52, 60]),
            "stairs": pressure_difference(pressure, [60, 68], [78, 84], [98, 106]),
            "bag": pressure_difference(pressure, [110, 118], [124, 128], [145, 153]),
            "initial_baseline": summary(window(pressure, *PRESSURE_BASELINE_S), "Pressure (hPa)"),
            "maximum_kpa_to_hpa_residual": max(
                abs(row["Pressure (hPa)"] - 10 * row["Pressure (kPa)"]) for row in pressure
            ),
        },
        "temperature-humidity": {
            "file": "core/temperature_plot_v1-2.example.csv",
            "samples": len(humidity),
            "baseline_window_s": [20, 30],
            "baseline_temperature_c": summary(baseline_humidity, "Temperature (°C)"),
            "baseline_relative_humidity_percent": summary(
                baseline_humidity, "relative Humidity (%)"
            ),
            "first_breath_window_s": [35, 60],
            "first_breath_rh_max_percent": breath_max["relative Humidity (%)"],
            "first_breath_rh_max_time_s": breath_max["Time t (s)"],
            "heating_window_s": [65, 115],
            "heating_temperature_max_c": temp_max["Temperature (°C)"],
            "heating_temperature_max_time_s": temp_max["Time t (s)"],
            "heating_rh_min_percent": rh_min["relative Humidity (%)"],
            "heating_rh_min_time_s": rh_min["Time t (s)"],
            "heating_temperature_rise_k": temp_max["Temperature (°C)"]
            - mean(baseline_humidity, "Temperature (°C)"),
            "heating_rh_change_percentage_points": rh_min["relative Humidity (%)"]
            - mean(baseline_humidity, "relative Humidity (%)"),
        },
        "analog-inputs": {
            "file": "core/analog_input_plot_v1-2.example.csv",
            "samples": len(analog),
            "display_mv_per_count": 3.226,
            "a0_code_range": [
                min(row["Analog Input A0"] for row in analog),
                max(row["Analog Input A0"] for row in analog),
            ],
            "a0_display_range_mv": [
                min(row["Voltage at A0 (mV)"] for row in analog),
                max(row["Voltage at A0 (mV)"] for row in analog),
            ],
            "a2_charge": fit_exponential(analog, 5, 12, "Voltage at A2 (mV)", 5),
            "a2_discharge": fit_exponential(analog, 35, 42, "Voltage at A2 (mV)", 35),
            "a2_charge_early": fit_exponential(analog, 5, 10, "Voltage at A2 (mV)", 5),
            "a2_discharge_early": fit_exponential(analog, 35, 40, "Voltage at A2 (mV)", 35),
            "max_code_to_mv_residual": max(
                abs(row[f"Voltage at A{i} (mV)"] - row[f"Analog Input A{i}"] * 3.226)
                for row in analog
                for i in range(3)
            ),
        },
    }
    # A sealed-bag compression has no hydrostatic-height interpretation.
    result["pressure"]["bag"].pop("height_m_at_293_15K")
    return result


if __name__ == "__main__":
    data_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "example-data"
    print(json.dumps(analyze(data_root), indent=2, ensure_ascii=False))
