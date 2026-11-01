"""Shared CSV readers and the time-window rule for the analysis modules (stdlib only)."""

from __future__ import annotations

import csv
from pathlib import Path


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
