"""Shared CSV readers and the time-window rule for the analysis modules (stdlib only)."""

from __future__ import annotations

import csv
import math
import statistics
import sys
from pathlib import Path

# Python 3.12 made float sum() compensated; the published numbers depend on it.
if sys.version_info < (3, 12):
    raise SystemExit("The paper pipeline needs Python 3.12 or newer (float sum changed in 3.12).")

# Analysis windows (seconds), shared with prepare_examples.py so figures cannot drift.
PRESSURE_BASELINE_S = (0, 20)
ALBEDO_DARK_S = ((0, 7), (57, 60.5))
ALBEDO_REFERENCE_S = (9, 23)
MARS_BASELINE_S = (0, 15)
TRANSIT_BASELINE_OFFSET_S = (3, 6)


def read_table(path: Path) -> tuple[list[str], list[list[float]]]:
    """Return the header and float rows; reject empty or ragged files."""
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream)
        headers = next(reader)
        rows = [[float(value) for value in row] for row in reader]
    if not rows or any(len(row) != len(headers) for row in rows):
        raise ValueError(f"Invalid CSV shape: {path}")
    return headers, rows


def read_lists(path: Path) -> list[list[float]]:
    return read_table(path)[1]


def read_dicts(path: Path) -> list[dict[str, float]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return [{key: float(value) for key, value in row.items()} for row in csv.DictReader(stream)]


def draft_rows(root: Path, name: str) -> list[list[float]]:
    return read_lists(root / "drafts" / f"{name}.example.csv")


def in_window(t: float, start: float, stop: float) -> bool:
    """The one window rule: lower bound inclusive, upper bound exclusive."""
    return start <= t < stop


def window(rows: list, start: float, stop: float, clock: int | str = 0) -> list:
    """Rows whose `row[clock]` (list index or dict key) lies in [start, stop)."""
    return [row for row in rows if in_window(row[clock], start, stop)]


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


def ols(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Ordinary least-squares (slope, intercept); callers filter non-finite pairs themselves."""
    xm, ym = statistics.mean(xs), statistics.mean(ys)
    sxx = sum((a - xm) ** 2 for a in xs)
    if sxx == 0:
        raise ValueError("OLS needs at least two distinct x values")
    slope = sum((a - xm) * (b - ym) for a, b in zip(xs, ys, strict=True)) / sxx
    return slope, ym - slope * xm
