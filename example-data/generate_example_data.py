#!/usr/bin/env python3
# ruff: noqa: E501
"""Generate deterministic, sensor-specific example data for every experiment.

The collection mirrors the units, sample rates, export columns, resolution, and
dominant error sources of the sensors named in each experiment.

Run from the repository root:

    python3 example-data/generate_example_data.py

Every dataset uses its own fixed seed, so repeated runs are byte-identical.
"""

from __future__ import annotations

import csv
import json
import math
import random
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "manifest.json"

# One seed for the whole collection; each dataset adds a fixed offset.
SEED = 20261026


@dataclass
class Dataset:
    """A CSV dataset plus the metadata written to manifest.json."""

    path: Path
    columns: tuple[str, ...]
    rows: list[tuple[object, ...]]
    meta: dict[str, object] = field(default_factory=dict)


DATASETS: list[Dataset] = []


# ---------------------------------------------------------------------------
# Numeric helpers
# ---------------------------------------------------------------------------


def f32(value: float) -> float:
    """Round a value to IEEE-754 binary32, as the firmware does before sending."""
    return struct.unpack("<f", struct.pack("<f", value))[0]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def quantize(value: float, step: float) -> float:
    return round(value / step) * step


def smoothstep(x: float) -> float:
    x = clamp(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def keyframe(t: float, points: Sequence[tuple[float, float]]) -> float:
    """Smoothly interpolate a scalar through time-value keyframes."""
    if t <= points[0][0]:
        return points[0][1]
    for (t0, v0), (t1, v1) in zip(points, points[1:]):
        if t <= t1:
            if t1 == t0:
                return v1
            return v0 + (v1 - v0) * smoothstep((t - t0) / (t1 - t0))
    return points[-1][1]


def smooth_pulse(t: float, start: float, rise: float, hold: float, fall: float) -> float:
    """A smooth 0-1-0 pulse with independent rise, hold, and fall durations."""
    if t <= start:
        return 0.0
    if t < start + rise:
        return smoothstep((t - start) / rise)
    if t < start + rise + hold:
        return 1.0
    if t < start + rise + hold + fall:
        return 1.0 - smoothstep((t - start - rise - hold) / fall)
    return 0.0


def ou_noise(rng: random.Random, count: int, sigma: float, tau: float, dt: float) -> list[float]:
    """Stationary Ornstein-Uhlenbeck noise, useful as slow sensor drift."""
    decay = math.exp(-dt / tau)
    drive = sigma * math.sqrt(max(0.0, 1.0 - decay * decay))
    value = 0.0
    out: list[float] = []
    for _ in range(count):
        value = decay * value + drive * rng.gauss(0.0, 1.0)
        out.append(value)
    return out


def lowpass(values: Sequence[float], tau: float, dt: float) -> list[float]:
    """First-order low-pass response to a sampled input."""
    alpha = dt / (tau + dt)
    state = values[0]
    out: list[float] = []
    for value in values:
        state += alpha * (value - state)
        out.append(state)
    return out


def core_times(count: int, rng: random.Random) -> list[float]:
    """Device time for the 20 Hz firmware stream, quantised to integer millis."""
    milliseconds = 0
    out: list[float] = []
    for _ in range(count):
        out.append(f32(milliseconds / 1000.0))
        milliseconds += 50 + rng.choice((0, 0, 0, 0, 1, 1))
    return out


def fixed_times(count: int, dt: float) -> list[float]:
    """Time reconstructed from a sample count, as the astronomy XML does."""
    return [i * dt for i in range(count)]


def phone_times(count: int, dt: float, rng: random.Random, jitter: float = 0.002) -> list[float]:
    """Phone sensor timestamps with small, monotonic arrival jitter."""
    value = 0.0
    out: list[float] = []
    for _ in range(count):
        out.append(max(0.0, value))
        value += max(0.5 * dt, dt + rng.gauss(0.0, jitter))
    return out


def fmt(value: object) -> str:
    """Format one CSV cell without losing sensor-relevant precision."""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    number = float(value)
    if math.isnan(number):
        return "nan"
    if math.isinf(number):
        return "inf" if number > 0 else "-inf"
    return f"{number:.9g}"


def add_dataset(
    relative_path: str,
    columns: Sequence[str],
    rows: Sequence[Sequence[object]],
    *,
    experiment: str,
    sensor: str,
    acquisition_path: str,
    nominal_rate_hz: float,
    duration_s: float,
    scenario: str,
    realism: Sequence[str],
    notes: str = "",
) -> None:
    """Register one CSV dataset and its manifest metadata."""
    path = ROOT / relative_path
    columns_tuple = tuple(columns)
    rows_list = [tuple(row) for row in rows]
    for row in rows_list:
        if len(row) != len(columns_tuple):
            raise ValueError(
                f"{relative_path}: row has {len(row)} cells, expected {len(columns_tuple)}"
            )
    meta = {
        "file": relative_path,
        "experiment": experiment,
        "sensor": sensor,
        "acquisition_path": acquisition_path,
        "nominal_rate_hz": nominal_rate_hz,
        "duration_s": duration_s,
        "rows": len(rows_list),
        "columns": list(columns_tuple),
        "scenario": scenario,
        "realism": list(realism),
        "example": True,
    }
    if notes:
        meta["notes"] = notes
    DATASETS.append(Dataset(path=path, columns=columns_tuple, rows=rows_list, meta=meta))


# ---------------------------------------------------------------------------
# Sensor encodings
# ---------------------------------------------------------------------------


def opt3001_encode(lux: float) -> int:
    """Encode illuminance in the OPT3001 exponent/mantissa result format."""
    lux = clamp(lux, 0.0, 83865.6)
    if lux <= 0.0:
        return 0
    exponent = 0
    while exponent < 11 and lux > 0.01 * (2**exponent) * 4095:
        exponent += 1
    mantissa = int(round(lux / (0.01 * (2**exponent))))
    mantissa = int(clamp(mantissa, 0, 4095))
    return (exponent << 12) | mantissa


def opt3001_decode(word: int) -> float:
    exponent = word >> 12
    mantissa = word & 0x0FFF
    return 0.01 * mantissa * (2**exponent)


def tmp007_encode(celsius: float) -> int:
    """Encode TMP007 temperature; the XML uses floor(word / 4) * 0.03125."""
    code = int(round(celsius / 0.03125))
    return clamp(code * 4, 0, 65535)


def tmp007_decode(word: int) -> float:
    return math.floor(word / 4) * 0.03125


def bmp280_temp_encode(celsius: float) -> int:
    return int(round(celsius / 0.01)) & 0xFFFFFF


def bmp280_pressure_encode(hpa: float) -> int:
    return int(round(hpa / 0.01)) & 0xFFFFFF


def b35t_encode(volts: float) -> tuple[str, int, int]:
    """Return the B35T numeric field, decimal code, and unit code.

    The supplied decoder uses a five-character field, d(1) = 10^-3, and u(0) = 1,
    so a 1.000 V reading is represented as "01000", 1, 0.
    """
    numeric = int(round(volts * 1000.0))
    numeric = int(clamp(numeric, -99999, 99999))
    return f"{numeric:05d}", 1, 0


def adc_counts(volts: float, vref: float, gain: float, offset: float) -> int:
    codes = (volts / vref) * 1023.0 * gain + offset
    return int(round(clamp(codes, 0.0, 1023.0)))


def rotate_field(
    field_vector: tuple[float, float, float], yaw_deg: float, pitch_deg: float, roll_deg: float
) -> tuple[float, float, float]:
    """Rotate a laboratory field into the board frame (R = Rz Ry Rx)."""
    bx, by, bz = field_vector
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    roll = math.radians(roll_deg)
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cr, sr = math.cos(roll), math.sin(roll)
    x1 = cy * bx + sy * by
    y1 = -sy * bx + cy * by
    z1 = bz
    x2 = cp * x1 - sp * z1
    y2 = y1
    z2 = sp * x1 + cp * z1
    x3 = x2
    y3 = cr * y2 + sr * z2
    z3 = -sr * y2 + cr * z2
    return x3, y3, z3


def saturation_vapour_pressure(celsius: float) -> float:
    """Magnus formula, returned in pascals."""
    return 610.94 * math.exp(17.625 * celsius / (celsius + 243.04))


# ---------------------------------------------------------------------------
# Core Arduino experiments
# ---------------------------------------------------------------------------


def make_accelerometer() -> None:
    rng = random.Random(SEED + 1)
    count = 1201
    times = core_times(count, rng)
    drift = ou_noise(rng, count, sigma=0.0007, tau=8.0, dt=0.05)
    drift_y = ou_noise(rng, count, sigma=0.0005, tau=10.0, dt=0.05)
    drift_z = ou_noise(rng, count, sigma=0.0006, tau=12.0, dt=0.05)
    pitch_keys = (
        (0.0, 0.0),
        (10.0, 0.0),
        (15.0, 30.0),
        (20.0, 30.0),
        (25.0, -30.0),
        (30.0, -30.0),
        (33.0, 0.0),
        (40.0, 0.0),
        (45.0, 0.0),
        (50.0, 0.0),
        (55.0, 0.0),
        (60.0, 0.0),
    )
    roll_keys = (
        (0.0, 0.0),
        (10.0, 0.0),
        (15.0, 0.0),
        (20.0, 0.0),
        (25.0, 0.0),
        (30.0, 0.0),
        (33.0, 0.0),
        (40.0, 0.0),
        (45.0, 90.0),
        (50.0, 90.0),
        (55.0, 0.0),
        (60.0, 0.0),
    )
    rows: list[tuple[object, ...]] = []
    for index, t in enumerate(times):
        pitch = keyframe(t, pitch_keys)
        roll = keyframe(t, roll_keys)
        # Hand tremor, mostly visible during the holds.
        tremor = 0.35 * math.sin(2.0 * math.pi * 1.15 * t)
        pitch += tremor
        roll += 0.25 * math.sin(2.0 * math.pi * 0.73 * t + 0.8)
        # A brief shake while the board is picked up.
        shake_envelope = smooth_pulse(t, 33.0, 0.8, 5.0, 1.2)
        shake = shake_envelope * (
            1.4 * math.sin(2.0 * math.pi * 4.6 * t) + 0.7 * math.sin(2.0 * math.pi * 7.3 * t + 1.1)
        )
        pitch += shake
        roll += 0.6 * shake_envelope * math.sin(2.0 * math.pi * 5.1 * t + 0.4)

        p = math.radians(pitch)
        r = math.radians(roll)
        ax = math.sin(p)
        ay = -math.sin(r) * math.cos(p)
        az = math.cos(r) * math.cos(p)

        # Three light taps on the desk. At 20 Hz a 7.5 Hz ring-down is visible.
        for tap_time in (34.2, 35.1, 36.35):
            if t >= tap_time:
                dt = t - tap_time
                envelope = math.exp(-dt / 0.18)
                ax += 0.22 * envelope * math.sin(2.0 * math.pi * 7.5 * dt + 0.6)
                az += 0.40 * envelope * math.sin(2.0 * math.pi * 7.5 * dt)

        ax += 0.0015 + drift[index] + rng.gauss(0.0, 0.0012)
        ay += -0.0010 + drift_y[index] + rng.gauss(0.0, 0.0012)
        az += 0.0030 + drift_z[index] + rng.gauss(0.0, 0.0012)

        lsb = 4.0 / 32768.0
        ax = f32(quantize(ax, lsb))
        ay = f32(quantize(ay, lsb))
        az = f32(quantize(az, lsb))
        magnitude = f32(math.sqrt(ax * ax + ay * ay + az * az))
        rows.append(
            (
                t,
                ax,
                ay,
                az,
                magnitude,
                ax * 9.81,
                ay * 9.81,
                az * 9.81,
                magnitude * 9.81,
            )
        )

    add_dataset(
        "core/accelerometer_plot_v1-2.example.csv",
        (
            "Time t (s)",
            "Acceleration x (g)",
            "Acceleration y (g)",
            "Acceleration z (g)",
            "Absolute Acceleration (g)",
            "Acceleration x (m/s²)",
            "Acceleration y (m/s²)",
            "Acceleration z (m/s²)",
            "Absolute Acceleration (m/s²)",
        ),
        rows,
        experiment="accelerometer_plot_v1-2.phyphox",
        sensor="ST LSM9DS1 accelerometer",
        acquisition_path="Nano 33 BLE Sense -> BLE notification (mode 1)",
        nominal_rate_hz=20.0,
        duration_s=60.0,
        scenario=(
            "Board resting flat, tilted ±30 degrees, picked up and shaken, tapped "
            "three times, then rolled 90 degrees and returned flat."
        ),
        realism=[
            "Firmware sends acceleration in g; phyphox multiplies by 9.81 for the m/s² columns.",
            "±4 g selected by the pinned Arduino_LSM9DS1 library; 16-bit LSB = 4/32768 g.",
            "119 Hz internal rate is decimated to a 20 Hz notification stream.",
            "Magnitude is computed from the transmitted components, not added independently.",
            "Small zero-g offsets, 1/f drift, broadband noise, and a 7.5 Hz ring-down are included.",
        ],
        notes="The timestamp advances in 50 ms or 51 ms steps, matching millis()-driven scheduling.",
    )


def make_gyroscope() -> None:
    rng = random.Random(SEED + 2)
    count = 1201
    times = core_times(count, rng)
    drift = ou_noise(rng, count, sigma=0.018, tau=6.0, dt=0.05)
    drift_y = ou_noise(rng, count, sigma=0.015, tau=8.0, dt=0.05)
    drift_z = ou_noise(rng, count, sigma=0.020, tau=7.0, dt=0.05)
    wx_keys = (
        (0.0, 0.0),
        (8.0, 0.0),
        (10.0, 0.0),
        (20.0, 0.0),
        (28.0, 0.0),
        (30.0, 60.0),
        (38.0, 60.0),
        (40.0, 0.0),
        (60.0, 0.0),
    )
    wy_keys = (
        (0.0, 0.0),
        (8.0, 0.0),
        (10.0, 0.0),
        (20.0, 0.0),
        (28.0, 0.0),
        (30.0, 0.0),
        (38.0, 0.0),
        (40.0, -35.0),
        (48.0, -35.0),
        (50.0, 0.0),
        (60.0, 0.0),
    )
    wz_keys = (
        (0.0, 0.0),
        (8.0, 0.0),
        (10.0, 45.0),
        (18.0, 45.0),
        (20.0, -45.0),
        (28.0, -45.0),
        (30.0, 0.0),
        (60.0, 0.0),
    )
    rows: list[tuple[object, ...]] = []
    library_scale = (2000.0 / 32768.0) / 0.070
    for index, t in enumerate(times):
        wx_true = keyframe(t, wx_keys)
        wy_true = keyframe(t, wy_keys)
        wz_true = keyframe(t, wz_keys)
        tremor = 0.9 * math.sin(2.0 * math.pi * 1.25 * t) + 0.45 * math.sin(
            2.0 * math.pi * 2.7 * t + 1.2
        )
        wx_true += 0.35 * tremor
        wy_true += 0.25 * tremor
        wz_true += 0.55 * tremor

        # The pinned library uses 2000/32768 deg/s per LSB, while the datasheet
        # sensitivity at ±2000 deg/s is 70 mdps/LSB. The ratio is 0.87193.
        wx = wx_true * library_scale + 0.07 + drift[index] + rng.gauss(0.0, 0.06)
        wy = wy_true * library_scale - 0.05 + drift_y[index] + rng.gauss(0.0, 0.06)
        wz = wz_true * library_scale + 0.11 + drift_z[index] + rng.gauss(0.0, 0.06)

        lsb = 2000.0 / 32768.0
        wx = f32(quantize(wx, lsb))
        wy = f32(quantize(wy, lsb))
        wz = f32(quantize(wz, lsb))
        magnitude = f32(math.sqrt(wx * wx + wy * wy + wz * wz))
        factor = 3.14159 / 180.0
        rows.append(
            (
                t,
                wx,
                wy,
                wz,
                magnitude,
                wx * factor,
                wy * factor,
                wz * factor,
                magnitude * factor,
            )
        )

    add_dataset(
        "core/gyroscope_plot_v1-2.example.csv",
        (
            "Time t (s)",
            "Angular Velocity x (deg/s)",
            "Angular Velocity y (deg/s)",
            "Angular Velocity z (deg/s)",
            "Absolute Angular Velocity (deg/s)",
            "Angular Velocity x (rad/s)",
            "Angular Velocity y (rad/s)",
            "Angular Velocity z (rad/s)",
            "Absolute Angular Velocity (rad/s)",
        ),
        rows,
        experiment="gyroscope_plot_v1-2.phyphox",
        sensor="ST LSM9DS1 gyroscope",
        acquisition_path="Nano 33 BLE Sense -> BLE notification (mode 2)",
        nominal_rate_hz=20.0,
        duration_s=60.0,
        scenario=(
            "Stationary baseline, ±45 deg/s yaw plateaus, +60 deg/s roll, "
            "-35 deg/s pitch, then stationary again."
        ),
        realism=[
            "Firmware sends deg/s; phyphox multiplies by pi/180 for the rad/s columns.",
            "±2000 deg/s range; 16-bit LSB = 2000/32768 deg/s = 0.061035 deg/s.",
            "The library-to-datasheet scale ratio 0.87193 is applied, so a true 45 deg/s plateau reads about 39.2 deg/s.",
            "Zero-rate bias, 1/f drift, 0.06 deg/s broadband noise, and hand tremor are included.",
            "Magnitude is computed from the three transmitted components.",
        ],
        notes="A stationary board still reports a small nonzero rate; the bias is not removed.",
    )


def make_magnetometer() -> None:
    rng = random.Random(SEED + 3)
    count = 1201
    times = core_times(count, rng)
    drift = ou_noise(rng, count, sigma=0.04, tau=12.0, dt=0.05)
    drift_y = ou_noise(rng, count, sigma=0.035, tau=15.0, dt=0.05)
    drift_z = ou_noise(rng, count, sigma=0.05, tau=10.0, dt=0.05)
    yaw_keys = (
        (0.0, 0.0),
        (10.0, 0.0),
        (20.0, 80.0),
        (30.0, 80.0),
        (40.0, 80.0),
        (50.0, 0.0),
        (60.0, 0.0),
    )
    pitch_keys = (
        (0.0, 0.0),
        (20.0, 0.0),
        (30.0, 25.0),
        (40.0, 25.0),
        (50.0, 0.0),
        (60.0, 0.0),
    )
    roll_keys = (
        (0.0, 0.0),
        (30.0, 0.0),
        (40.0, -10.0),
        (50.0, 0.0),
        (60.0, 0.0),
    )
    earth_field = (18.9, 0.0, 44.5)
    library_scale = (400.0 / 32768.0) / 0.014
    rows: list[tuple[object, ...]] = []
    for index, t in enumerate(times):
        yaw = keyframe(t, yaw_keys)
        pitch = keyframe(t, pitch_keys)
        roll = keyframe(t, roll_keys)
        bx, by, bz = rotate_field(earth_field, yaw, pitch, roll)

        # A small magnet is brought near the board and removed again.
        magnet = smooth_pulse(t, 29.0, 2.0, 4.0, 5.0)
        bx += magnet * 92.0 * math.exp(-((t - 33.0) ** 2) / 18.0)
        by += magnet * -48.0 * math.exp(-((t - 33.0) ** 2) / 22.0)
        bz += magnet * 108.0 * math.exp(-((t - 33.0) ** 2) / 16.0)

        # Library scale error, then a small hard-iron offset and soft-iron matrix.
        bx = bx * library_scale + 2.2 + drift[index] + rng.gauss(0.0, 0.12)
        by = by * library_scale - 1.4 + drift_y[index] + rng.gauss(0.0, 0.12)
        bz = bz * library_scale + 2.8 + drift_z[index] + rng.gauss(0.0, 0.12)
        bx *= 1.02
        by *= 0.98
        bz *= 1.01

        lsb = 400.0 / 32768.0
        bx = f32(quantize(bx, lsb))
        by = f32(quantize(by, lsb))
        bz = f32(quantize(bz, lsb))
        magnitude = f32(math.sqrt(bx * bx + by * by + bz * bz))
        if index in (217, 583, 901, 1102):
            bx = by = bz = magnitude = math.nan
        rows.append((t, bx, by, bz, magnitude))

    add_dataset(
        "core/magnetometer_plot_v1-2.example.csv",
        (
            "Time t (s)",
            "Magnetometer x (µT)",
            "Magnetometer y (µT)",
            "Magnetometer z (µT)",
            "Absolute magnetic field (µT)",
        ),
        rows,
        experiment="magnetometer_plot_v1-2.phyphox",
        sensor="ST LSM9DS1 magnetometer",
        acquisition_path="Nano 33 BLE Sense -> BLE notification (mode 3)",
        nominal_rate_hz=20.0,
        duration_s=60.0,
        scenario=(
            "Earth-field baseline, 80 degree yaw, 25 degree tilt, a magnet "
            "approach near 30 s, then return to the starting orientation."
        ),
        realism=[
            "±4 gauss range = ±400 µT; 16-bit LSB = 400/32768 µT = 0.012207 µT.",
            "The library-to-datasheet scale ratio 0.87193 is applied, so the uncalibrated magnitude reads low.",
            "Earth field is about 48.3 µT total in Cologne; hard-iron and soft-iron terms shift the components.",
            "Four NaN rows represent magneticFieldAvailable() returning false at the 20 Hz frame boundary.",
            "Magnitude is computed from the transmitted components, including the disturbed interval.",
        ],
        notes="µT values are sensor-frame components; they are not a calibrated compass heading.",
    )


def make_pressure() -> None:
    rng = random.Random(SEED + 4)
    count = 3601
    times = core_times(count, rng)
    base = 1009.2
    height_keys = (
        (0.0, 0.0),
        (30.0, 0.0),
        (33.0, 1.2),
        (43.0, 1.2),
        (46.0, 0.0),
        (70.0, 0.0),
        (75.0, 3.0),
        (85.0, 3.0),
        (90.0, 0.0),
        (180.0, 0.0),
    )
    drift = ou_noise(rng, count, sigma=0.010, tau=30.0, dt=0.05)
    true_values: list[float] = []
    for t in times:
        height = keyframe(t, height_keys)
        # Isothermal barometric relation, T = 293.15 K.
        pressure = base * math.exp(-9.80665 * height / (287.05 * 293.15))
        # Slow indoor/weather drift.
        pressure += 0.06 * math.sin(2.0 * math.pi * t / 180.0)
        # A sealed bag is squeezed between 120 s and 140 s.
        pressure += 8.0 * smooth_pulse(t, 120.0, 1.5, 8.0, 3.0)
        pressure -= 0.4 * smooth_pulse(t, 132.0, 1.0, 4.0, 5.0)
        true_values.append(pressure)

    lagged = lowpass(true_values, tau=0.8, dt=0.05)
    rows: list[tuple[object, ...]] = []
    for index, t in enumerate(times):
        pressure_hpa = lagged[index] + 0.55 + drift[index] + rng.gauss(0.0, 0.020)
        pressure_hpa = quantize(pressure_hpa, 1.0 / 4096.0)
        pressure_kpa = f32(pressure_hpa / 10.0)
        rows.append((t, pressure_kpa, pressure_kpa * 10.0))

    add_dataset(
        "core/pressure_plot_v1-2.example.csv",
        ("Time t (s)", "Pressure (kPa)", "Pressure (hPa)"),
        rows,
        experiment="pressure_plot_v1-2.phyphox",
        sensor="ST LPS22HB barometer",
        acquisition_path="Nano 33 BLE Sense -> BLE notification (mode 4)",
        nominal_rate_hz=20.0,
        duration_s=180.0,
        scenario=(
            "Indoor baseline near 1009 hPa, a 1.2 m lift, a 3 m stair climb, "
            "a sealed-bag squeeze near 120 s, and slow room drift."
        ),
        realism=[
            "Firmware sends kPa; phyphox multiplies by 10 for the hPa column.",
            "24-bit output with 4096 LSB/hPa, i.e. 0.000244 hPa per code.",
            "A +0.55 hPa uncalibrated offset, 0.02 hPa noise, and 30 s drift are included.",
            "Pressure follows a 0.8 s port/equilibration lag rather than the height step instantly.",
            "A 1.2 m lift changes pressure by about 0.144 hPa; 3 m by about 0.36 hPa.",
        ],
        notes="The 8 hPa bag excursion stays well inside the 260-1260 hPa sensor range.",
    )


def make_temperature_humidity() -> None:
    rng = random.Random(SEED + 5)
    count = 3601
    times = core_times(count, rng)
    t_drift = ou_noise(rng, count, sigma=0.010, tau=40.0, dt=0.05)
    rh_drift = ou_noise(rng, count, sigma=0.05, tau=30.0, dt=0.05)
    air_temps: list[float] = []
    vapour: list[float] = []
    base_vapour = 0.45 * saturation_vapour_pressure(22.4)
    for t in times:
        air = 22.4 + 0.03 * math.sin(2.0 * math.pi * t / 180.0)
        air += 0.35 * (1.0 - math.exp(-t / 60.0))
        air += 0.55 * smooth_pulse(t, 35.0, 2.0, 2.0, 18.0)
        air += 2.9 * smooth_pulse(t, 65.0, 10.0, 10.0, 25.0)
        air += 0.45 * smooth_pulse(t, 125.0, 1.5, 1.0, 14.0)
        air_temps.append(air)

        pv = base_vapour + 20.0 * math.sin(2.0 * math.pi * t / 180.0)
        pv += 1050.0 * smooth_pulse(t, 35.0, 1.5, 1.0, 14.0)
        pv += 900.0 * smooth_pulse(t, 125.0, 1.0, 0.8, 12.0)
        vapour.append(pv)

    sensor_temp = lowpass(air_temps, tau=15.0, dt=0.05)
    true_rh = [100.0 * vapour[i] / saturation_vapour_pressure(air_temps[i]) for i in range(count)]
    sensor_rh = lowpass(true_rh, tau=10.0, dt=0.05)
    rows: list[tuple[object, ...]] = []
    for index, t in enumerate(times):
        temperature = sensor_temp[index] + 0.32 + t_drift[index] + rng.gauss(0.0, 0.007)
        humidity = sensor_rh[index] + 1.7 + rh_drift[index] + rng.gauss(0.0, 0.03)
        temperature = quantize(temperature, 0.016)
        humidity = quantize(clamp(humidity, 0.0, 100.0), 0.004)
        rows.append((t, temperature, humidity))

    add_dataset(
        "core/temperature_plot_v1-2.example.csv",
        ("Time t (s)", "Temperature (°C)", "relative Humidity (%)"),
        rows,
        experiment="temperature_plot_v1-2.phyphox",
        sensor="ST HTS221 temperature and humidity sensor",
        acquisition_path="Nano 33 BLE Sense -> BLE notification (mode 5)",
        nominal_rate_hz=20.0,
        duration_s=180.0,
        scenario=(
            "Powered-board warm-up, two breath events, and a lamp/hand warming "
            "interval that raises temperature and lowers relative humidity."
        ),
        realism=[
            "Humidity is derived from a conserved vapour pressure and the Magnus saturation curve, so it falls when temperature rises.",
            "A 15 s temperature lag and a 10 s humidity lag follow the HTS221 response times.",
            "Typical offsets (+0.32 °C, +1.7 %RH), 0.016 °C and 0.004 %RH quantisation, and 1/f drift are included.",
            "The firmware reads temperature first and humidity second; the two numbers are not simultaneous conversions.",
            "The board self-heating term is separate from the air-temperature changes.",
        ],
        notes="Relative humidity is a percentage, not a fraction; 45 %RH is written 45.0 here.",
    )


def make_light_rgb() -> None:
    rng = random.Random(SEED + 6)
    count = 1201
    times = core_times(count, rng)
    drift = [ou_noise(rng, count, sigma=0.004, tau=10.0, dt=0.05) for _ in range(4)]
    plateaus = (
        (0.0, (35.0, 8.0, 10.0, 6.0)),
        (5.0, (35.0, 8.0, 10.0, 6.0)),
        (5.5, (1850.0, 900.0, 1050.0, 620.0)),
        (15.0, (1850.0, 900.0, 1050.0, 620.0)),
        (15.5, (2400.0, 1800.0, 300.0, 120.0)),
        (25.0, (2400.0, 1800.0, 300.0, 120.0)),
        (25.5, (2200.0, 250.0, 1600.0, 180.0)),
        (35.0, (2200.0, 250.0, 1600.0, 180.0)),
        (35.5, (2000.0, 180.0, 260.0, 1500.0)),
        (45.0, (2000.0, 180.0, 260.0, 1500.0)),
        (45.3, (6000.0, 6000.0, 6000.0, 6000.0)),
        (50.0, (6000.0, 6000.0, 6000.0, 6000.0)),
        (50.5, (35.0, 8.0, 10.0, 6.0)),
        (60.0, (35.0, 8.0, 10.0, 6.0)),
    )
    gains = (1.02, 1.05, 0.97, 0.92)  # clear, red, green, blue
    darks = (3.0, 2.0, 2.0, 1.0)
    rows: list[tuple[object, ...]] = []
    for index, t in enumerate(times):
        target = [keyframe(t, [(p[0], p[1][channel]) for p in plateaus]) for channel in range(4)]
        # A small lamp ripple below the 10 Hz Nyquist limit.
        ripple = (
            1.0
            + 0.012 * math.sin(2.0 * math.pi * 3.7 * t)
            + 0.006 * math.sin(2.0 * math.pi * 0.43 * t + 0.7)
        )
        counts: list[int] = []
        for channel, value in enumerate(target):
            value = value * ripple * gains[channel] + darks[channel]
            value *= 1.0 + drift[channel][index]
            value += rng.gauss(0.0, 2.0 + 0.008 * value)
            counts.append(int(round(clamp(value, 0.0, 4100.0))))
        rows.append((t, counts[0], counts[1], counts[2], counts[3]))

    add_dataset(
        "core/light_plot_v1-2.example.csv",
        (
            "Time t (s)",
            "Relative light level (a.u.)",
            "Red (a.u.)",
            "Green (a.u.)",
            "Blue (a.u.)",
        ),
        rows,
        experiment="light_plot_v1-2.phyphox",
        sensor="Broadcom APDS-9960 RGBC sensor",
        acquisition_path="Nano 33 BLE Sense -> BLE notification (mode 6)",
        nominal_rate_hz=20.0,
        duration_s=60.0,
        scenario=(
            "Dim room, warm white lamp, red/green/blue cards, a saturated phone "
            "flashlight, then dim room again."
        ),
        realism=[
            "Raw 16-bit RGBC counts, not lux; phyphox displays arbitrary units.",
            "The library's 4-cycle integration gives a nominal 4100-count saturation, not 65535.",
            "Channel gains, dark counts, shot-like noise, and a 3.7 Hz lamp ripple are included.",
            "Clear is generally larger than each colour channel; all channels clip at 4100.",
            "The 11.12 ms integration is much shorter than the 50 ms notification interval.",
        ],
        notes="Counts are integers, matching the sensor registers and the firmware's int-to-float cast.",
    )


def make_analog_inputs() -> None:
    rng = random.Random(SEED + 7)
    count = 1201
    times = core_times(count, rng)
    a0_keys = (
        (0.0, 1.65),
        (8.0, 1.65),
        (25.0, 2.80),
        (35.0, 0.60),
        (45.0, 0.70),
        (60.0, 0.65),
    )
    rows: list[tuple[object, ...]] = []
    for t in times:
        a0 = keyframe(t, a0_keys) + 0.004 * math.sin(2.0 * math.pi * 0.8 * t)
        a1 = 0.90
        if t >= 15.0:
            a1 += 1.50 * (1.0 - math.exp(-(t - 15.0) / 1.5))
        if t >= 40.0:
            a1 -= 1.50 * (1.0 - math.exp(-(t - 40.0) / 2.0))
        a1 += 0.008 * math.sin(2.0 * math.pi * 1.1 * t + 0.4)
        a2 = 0.0
        if t >= 5.0:
            a2 = 3.0 * (1.0 - math.exp(-(t - 5.0) / 1.0))
        if t >= 35.0:
            a2 *= math.exp(-(t - 35.0) / 1.0)
        a2 += 0.0015 * math.sin(2.0 * math.pi * 50.0 * t)
        a2 += rng.gauss(0.0, 0.0012)

        # The ADC reference is 3.31 V, not the nominal 3.3 V, and each channel
        # has a small gain/offset error. Counts are quantised by the 10-bit ADC.
        counts = (
            adc_counts(a0, 3.31, 1.004, 1.2),
            adc_counts(a1, 3.31, 0.997, -0.8),
            adc_counts(a2, 3.31, 1.001, 0.5),
        )
        rows.append(
            (
                t,
                counts[0],
                counts[1],
                counts[2],
                counts[0] * 3.226,
                counts[1] * 3.226,
                counts[2] * 3.226,
            )
        )

    add_dataset(
        "core/analog_input_plot_v1-2.example.csv",
        (
            "Time t (s)",
            "Analog Input A0",
            "Analog Input A1",
            "Analog Input A2",
            "Voltage at A0 (mV)",
            "Voltage at A1 (mV)",
            "Voltage at A2 (mV)",
        ),
        rows,
        experiment="analog_input_plot_v1-2.phyphox",
        sensor="nRF52840 SAADC, 10-bit software range",
        acquisition_path="Nano 33 BLE Sense -> BLE notification (mode 9)",
        nominal_rate_hz=20.0,
        duration_s=60.0,
        scenario=(
            "A0 potentiometer sweep, A1 light-dependent-resistor step, and A2 "
            "RC charge/discharge with tau = 1 s."
        ),
        realism=[
            "Default 10-bit codes 0-1023; phyphox multiplies by 3.226 mV/count.",
            "Actual reference 3.31 V and per-channel gain/offset errors make the displayed mV slightly wrong.",
            "Counts are integers and clip at the ADC rails.",
            "A2 includes 50 Hz mains pickup, which aliases at the 20 Hz sampling rate.",
            "A0, A1, and A2 are converted sequentially; there is no simultaneous-sample guarantee.",
        ],
        notes="The RC curve is sampled about 20 times per time constant, so the shape is resolved but not oversampled.",
    )


# ---------------------------------------------------------------------------
# Astronomy experiments
# ---------------------------------------------------------------------------


def make_albedo() -> None:
    # SensorTag OPT3001 path, 0.8 s reconstructed time.
    rng = random.Random(SEED + 20)
    count = 76
    times = fixed_times(count, 0.8)
    plateaus = (
        (0.0, 0.8),
        (8.0, 0.8),
        (8.0, 420.0),
        (24.0, 420.0),
        (24.0, 155.0),
        (40.0, 155.0),
        (40.0, 18.0),
        (56.0, 18.0),
        (56.0, 0.8),
        (60.0, 0.8),
    )
    rows: list[tuple[object, ...]] = []
    for t in times:
        lux = keyframe(t, plateaus)
        lux *= 1.0 + 0.005 * t / 60.0  # lamp warm-up
        lux *= 1.0 + 0.002 * math.sin(2.0 * math.pi * 0.11 * t)
        lux *= 1.03  # OPT3001 gain error
        lux += rng.gauss(0.0, max(0.02, 0.01 * lux))
        word = opt3001_encode(max(0.0, lux))
        decoded = opt3001_decode(word)
        rows.append((t, decoded, word))

    add_dataset(
        "astronomy/albedo_sensortag.example.csv",
        ("t (s)", "Relative light level (a.u.)", "Raw OPT3001 word (a.u.)"),
        rows,
        experiment="albedo.phyphox",
        sensor="TI OPT3001 ambient light sensor (SensorTag)",
        acquisition_path="SensorTag BLE AA71 notification, AA73=0x50 (0.8 s)",
        nominal_rate_hz=1.25,
        duration_s=60.0,
        scenario=(
            "Covered sensor, white reference tile, grey sample, black sample, "
            "then covered again; the lamp is left running throughout."
        ),
        realism=[
            "Exact OPT3001 exponent/mantissa encoding; the exported value is decoded from the raw word.",
            "0.01 lx resolution at the lowest range, automatic range selection, 3% gain error, and 1% noise.",
            "The XML reconstructs time as 0.8 s times the sample count, not from packet timestamps.",
            "The built-in contrast (max-min)/max is an extrema statistic, not a calibrated albedo.",
        ],
        notes="The trailing raw word is not part of the phyphox export; it is provided for decoder checks.",
    )

    # Phone light-sensor path, 10 Hz.
    rng = random.Random(SEED + 21)
    count = 601
    times = phone_times(count, 0.1, rng, jitter=0.0015)
    plateaus_phone = (
        (0.0, 0.3),
        (8.0, 0.3),
        (8.0, 520.0),
        (24.0, 520.0),
        (24.0, 190.0),
        (40.0, 190.0),
        (40.0, 22.0),
        (56.0, 22.0),
        (56.0, 0.3),
        (60.0, 0.3),
    )
    rows = []
    for t in times:
        lux = keyframe(t, plateaus_phone)
        lux *= 1.0 + 0.008 * t / 60.0
        lux *= 1.0 + 0.006 * math.sin(2.0 * math.pi * 0.9 * t)
        lux += rng.gauss(0.0, max(0.1, 0.02 * lux))
        rows.append((t, max(0.0, lux)))

    add_dataset(
        "astronomy/albedo_phone.example.csv",
        ("t (s)", "Relative light level (a.u.)"),
        rows,
        experiment="albedo.phyphox",
        sensor="Phone ambient-light sensor",
        acquisition_path="phyphox phone light sensor",
        nominal_rate_hz=10.0,
        duration_s=60.0,
        scenario="Same reference/sample/dark sequence as the SensorTag run, recorded on a phone.",
        realism=[
            "Phone light sensors are model-dependent; this trace assumes a 10 Hz sensor with 2% noise.",
            "The values differ from the SensorTag run because the optical gain and spectral weighting differ.",
            "Time jitter is small but nonzero because the phone supplies sensor timestamps.",
            "The two files are alternative runs, not simultaneous measurements.",
        ],
    )


def make_greenhouse() -> None:
    rng = random.Random(SEED + 22)
    count = 601
    times = fixed_times(count, 1.0)
    rows: list[tuple[object, ...]] = []
    for t in times:
        if t < 60.0:
            ambient = 22.0
            covered = 22.0
        elif t < 360.0:
            ambient = 22.0 + 4.5 * (1.0 - math.exp(-(t - 60.0) / 180.0))
            covered = 22.0 + 8.0 * (1.0 - math.exp(-(t - 60.0) / 150.0))
        else:
            ambient = 22.2 + 4.5 * math.exp(-(t - 360.0) / 240.0)
            covered = 22.2 + 8.0 * math.exp(-(t - 360.0) / 300.0)
        # BMP280 die temperature is typically above air because of self-heating.
        temp1 = ambient + 0.70 + 0.25 + rng.gauss(0.0, 0.02)
        temp2 = covered + 0.70 - 0.15 + rng.gauss(0.0, 0.02)
        temp1 = quantize(temp1, 0.01)
        temp2 = quantize(temp2, 0.01)
        rows.append((t / 60.0, temp1, temp2, bmp280_temp_encode(temp1), bmp280_temp_encode(temp2)))

    add_dataset(
        "astronomy/greenhouse.example.csv",
        (
            "Time (min)",
            "Temperature 1 (°C)",
            "Temperature 2 (°C)",
            "Raw temperature 1 word (a.u.)",
            "Raw temperature 2 word (a.u.)",
        ),
        rows,
        experiment="greenhouse.phyphox",
        sensor="Bosch BMP280 die temperature (two SensorTags)",
        acquisition_path="SensorTag BLE AA41 notification, AA44=0x64 (1 s)",
        nominal_rate_hz=1.0,
        duration_s=600.0,
        scenario=(
            "Open and covered vessels start at 22 °C, a lamp is switched on at "
            "60 s, and both cool after 360 s; the covered vessel rises faster and higher."
        ),
        realism=[
            "The XML uses the BMP280 die-temperature word, not the HDC1000 air sensor; a self-heating offset is included.",
            "Signed 24-bit temperature word with 0.01 °C scaling, as in the experiment.",
            "The covered vessel has a larger asymptote and a shorter time constant than the open vessel.",
            "Time is reconstructed from the first tag's sample count at 1 s per sample.",
            "The two tags have different offsets and noise, so the difference is not a clean physical contrast.",
        ],
        notes="The trailing raw words are not exported by the XML; they let the decoder be checked.",
    )


def make_ir_distance() -> None:
    rng = random.Random(SEED + 23)
    count = 101
    times = fixed_times(count, 0.3)
    rows: list[tuple[object, ...]] = []
    # Outbound 0.15 m to 0.80 m, then inbound; 0.05 m steps with short dwells.
    positions = [0.15 + 0.05 * (index // 5) for index in range(70)]
    positions += [0.80 - 0.05 * (index // 3) for index in range(31)]
    lagged_ir = lowpass(
        [24.0 + 14.0 * (0.15 / max(0.15, r)) ** 0.8 for r in positions],
        tau=1.4,
        dt=0.3,
    )
    for index, t in enumerate(times):
        distance = positions[index]
        # Mouse counts with 0.0002 m/count, plus a small slip event.
        counts = (distance - 0.15) / 0.0002
        if 60 <= index <= 64:
            counts += 28.0
        ir = lagged_ir[index] + rng.gauss(0.0, 0.08)
        ambient = 23.0 + 0.15 * math.sin(2.0 * math.pi * t / 30.0) + rng.gauss(0.0, 0.04)
        ir = quantize(ir, 0.03125)
        ambient = quantize(ambient, 0.03125)
        rows.append((t, counts, ir, ambient, tmp007_encode(ir), tmp007_encode(ambient)))

    add_dataset(
        "astronomy/ir-dist_habitable.example.csv",
        (
            "Time (s)",
            "d (a.u.)",
            "T_IR (°C)",
            "T_amb (°C)",
            "Raw object word (a.u.)",
            "Raw die word (a.u.)",
        ),
        rows,
        experiment="ir-dist_habitable.phyphox",
        sensor="TI TMP007 infrared thermopile (SensorTag) and Bluetooth HID mouse",
        acquisition_path="SensorTag AA01 notification, AA03=0x1E (0.3 s), plus BLE HID mouse",
        nominal_rate_hz=3.333,
        duration_s=30.0,
        scenario=(
            "A warm target and SensorTag move together on a rail from 0.15 m to "
            "0.80 m and back; the apparent IR temperature settles at each stop."
        ),
        realism=[
            "TMP007 conversion time is 0.25 s; the file samples at 0.3 s and includes a 1.4 s thermal lag.",
            "Object temperature word is 0.03125 °C resolution; the die word is the ambient channel.",
            "Mouse distance uses about 0.0002 m/count, with a small slip event near 60 samples.",
            "The unsigned XML conversion requires nonnegative temperatures; this run stays above 20 °C.",
            "The file has no export timestamp in the XML; Time (s) is added here for readability.",
        ],
        notes="d (a.u.) is accumulated mouse counts, not metres. Divide by 5000 for an approximate metre reading after calibration.",
    )


def make_mission_to_mars() -> None:
    # SensorTag BMP280 path at 0.1 s.
    rng = random.Random(SEED + 24)
    count = 1201
    times = fixed_times(count, 0.1)
    true_pressure: list[float] = []
    for t in times:
        pressure = 1008.4 + 0.05 * math.sin(2.0 * math.pi * t / 120.0)
        leak = 1.5 * clamp((t - 28.0) / 30.0, 0.0, 1.0)
        pressure += (35.0 - leak) * smooth_pulse(t, 20.0, 8.0, 30.0, 8.0)
        true_pressure.append(pressure)
    lagged = lowpass(true_pressure, tau=0.35, dt=0.1)
    rows: list[tuple[object, ...]] = []
    for index, t in enumerate(times):
        pressure = lagged[index] + 0.60 + rng.gauss(0.0, 0.020)
        pressure = quantize(pressure, 0.01)
        temperature = 23.2 + 0.4 * smooth_pulse(t, 20.0, 8.0, 30.0, 8.0) + rng.gauss(0.0, 0.02)
        temperature = quantize(temperature, 0.01)
        rows.append(
            (
                t,
                pressure,
                bmp280_pressure_encode(pressure),
                bmp280_temp_encode(temperature),
            )
        )

    add_dataset(
        "astronomy/missiontomars_sensortag.example.csv",
        (
            "Time (s)",
            "Pressure (hPa)",
            "Raw pressure word (a.u.)",
            "Raw temperature word (a.u.)",
        ),
        rows,
        experiment="missiontomars.phyphox",
        sensor="Bosch BMP280 absolute pressure (SensorTag)",
        acquisition_path="SensorTag BLE AA41 notification, AA44=0x0A (0.1 s)",
        nominal_rate_hz=10.0,
        duration_s=120.0,
        scenario=(
            "Near-ambient baseline, pump to +35 hPa, a slow 1.5 hPa leak over "
            "30 s, release, and a final baseline."
        ),
        realism=[
            "BMP280 range is 300-1100 hPa; the 35 hPa excursion remains inside it.",
            "Pressure word is 0.01 hPa resolution, with +0.6 hPa offset and 0.02 hPa noise.",
            "A 0.35 s port/equilibration lag is applied to the chamber step.",
            "The XML reconstructs time as 0.1 s times the sample count.",
            "The auxiliary temperature word is included as a raw column even though the XML does not export it.",
        ],
        notes="This is a classroom chamber run, not a Martian pressure measurement.",
    )

    # Phone barometer path at 10 Hz.
    rng = random.Random(SEED + 25)
    count = 1201
    times = phone_times(count, 0.1, rng, jitter=0.001)
    rows = []
    for t in times:
        pressure = 1008.1 + 0.05 * math.sin(2.0 * math.pi * t / 120.0)
        leak = 1.5 * clamp((t - 28.0) / 30.0, 0.0, 1.0)
        pressure += (35.0 - leak) * smooth_pulse(t, 20.0, 8.0, 30.0, 8.0)
        pressure += -0.30 + rng.gauss(0.0, 0.015)
        pressure = quantize(pressure, 0.01)
        rows.append((t, pressure))

    add_dataset(
        "astronomy/missiontomars_phone.example.csv",
        ("Time (s)", "Pressure (hPa)"),
        rows,
        experiment="missiontomars.phyphox",
        sensor="Phone barometer",
        acquisition_path="phyphox phone pressure sensor",
        nominal_rate_hz=10.0,
        duration_s=120.0,
        scenario="The same chamber pressure profile recorded on a phone barometer.",
        realism=[
            "Phone barometers are model-dependent; this trace assumes 10 Hz, 0.01 hPa resolution, and 0.015 hPa noise.",
            "A -0.3 hPa offset and a slightly different noise level distinguish it from the SensorTag run.",
            "Phone timestamps have small arrival jitter.",
            "The two files are alternative runs, not simultaneous measurements.",
        ],
    )


def make_owon_debug() -> None:
    rng = random.Random(SEED + 26)
    count = 121
    times = fixed_times(count, 0.5)
    keys = (
        (0.0, 0.0),
        (10.0, 0.0),
        (10.0, 1.0),
        (20.0, 1.0),
        (20.0, 1.5),
        (30.0, 1.5),
        (30.0, 2.0),
        (40.0, 2.0),
        (40.0, -1.0),
        (50.0, -1.0),
        (50.0, 0.5),
        (60.0, 0.5),
    )
    rows: list[tuple[object, ...]] = []
    for t in times:
        voltage = keyframe(t, keys)
        voltage = voltage * 1.002 + 0.0004 + 0.0002 * t / 60.0
        voltage += rng.gauss(0.0, 0.0003)
        voltage = quantize(voltage, 0.001)
        field, decimal_code, unit_code = b35t_encode(voltage)
        rows.append((t, voltage, field, decimal_code, unit_code))

    add_dataset(
        "astronomy/owon_digital_multimeter-debug.example.csv",
        (
            "Time (s)",
            "y",
            "Raw numeric field (a.u.)",
            "Raw decimal code (a.u.)",
            "Raw unit code (a.u.)",
        ),
        rows,
        experiment="owon_digital_multimeter-debug.phyphox",
        sensor="Owon B35T digital multimeter, DC voltage",
        acquisition_path="Owon BDM BLE notification, characteristic FFF4",
        nominal_rate_hz=2.0,
        duration_s=60.0,
        scenario=(
            "A DC calibration staircase: 0 V, 1 V, 1.5 V, 2 V, -1 V, and 0.5 V, "
            "each held for about 10 s."
        ),
        realism=[
            "The Owon B35T updates digital data 3 times/s on the meter and about 2 times/s in the app.",
            "The 6 V DC range has 1 mV resolution; a 0.2% gain error, 0.4 mV offset, and 0.3 mV noise are included.",
            "Raw fields follow the B35T branch of the supplied decoder: 5-character numeric field, decimal code 1, unit code 0.",
            "The debug XML exports only Time (s) and y; the raw fields are extra columns for decoder testing.",
            "The analysis sleep of 0.05 s is not a 20 Hz acquisition rate.",
        ],
        notes="The positive and negative steps exercise the decoder's sign handling.",
    )


def make_pt_star() -> None:
    rng = random.Random(SEED + 27)
    count = 181
    times = fixed_times(count, 1.0)
    rows: list[tuple[object, ...]] = []
    for t in times:
        pressure = 1005.0
        pressure += 75.0 * smooth_pulse(t, 30.0, 25.0, 30.0, 25.0)
        pressure -= 2.5 * smooth_pulse(t, 60.0, 0.1, 30.0, 0.1)
        pressure += 0.04 * math.sin(2.0 * math.pi * t / 180.0)
        pressure = quantize(pressure + 0.55 + rng.gauss(0.0, 0.02), 0.01)
        temperature = 23.0 + 1.4 * smooth_pulse(t, 30.0, 25.0, 30.0, 35.0)
        temperature = quantize(temperature + 0.40 + rng.gauss(0.0, 0.015), 0.01)
        rows.append(
            (
                t / 60.0,
                pressure,
                temperature,
                bmp280_pressure_encode(pressure),
                bmp280_temp_encode(temperature),
            )
        )

    add_dataset(
        "astronomy/pt-star.example.csv",
        (
            "Time (min)",
            "Pressure (hPa)",
            "Temperature (°C)",
            "Raw pressure word (a.u.)",
            "Raw temperature word (a.u.)",
        ),
        rows,
        experiment="pt-star.phyphox",
        sensor="Bosch BMP280 pressure and die temperature (SensorTag)",
        acquisition_path="SensorTag BLE AA41 notification, AA44=0x64 (1 s)",
        nominal_rate_hz=1.0,
        duration_s=180.0,
        scenario=(
            "A slow 7% volume reduction raises pressure by about 75 hPa and "
            "warms the barometer die by about 1.4 °C, followed by a release."
        ),
        realism=[
            "Pressure is the compensated BMP280 absolute value, scaled by 0.01 hPa.",
            "Temperature is the barometer die temperature, not an independent gas thermometer.",
            "The compression is slow enough to be nearly isothermal; the die warming is mostly self-heating and work.",
            "Reconstructed time is 1 s per sample and is exported in minutes.",
            "A +0.55 hPa and +0.40 °C offset plus 0.02 hPa and 0.015 °C noise are included.",
        ],
        notes="The 1081 hPa peak stays inside the BMP280 300-1100 hPa rated interval. The scenario is illustrative, not a validated chamber run.",
    )


def make_tidal_locking() -> None:
    # BMP280 die temperature, 1 s.
    rng = random.Random(SEED + 28)
    count = 301
    times = fixed_times(count, 1.0)
    bmp_rows: list[tuple[object, ...]] = []
    for t in times:
        day = 23.0
        night = 22.8
        if 30.0 <= t < 210.0:
            day += 15.0 * (1.0 - math.exp(-(t - 30.0) / 90.0))
            night += 1.7 * (1.0 - math.exp(-(t - 30.0) / 160.0))
        elif t >= 210.0:
            day = 23.5 + 14.5 * math.exp(-(t - 210.0) / 120.0)
            night = 22.9 + 1.6 * math.exp(-(t - 210.0) / 150.0)
        temp1 = quantize(day + 0.70 + 0.20 + rng.gauss(0.0, 0.02), 0.01)
        temp2 = quantize(night + 0.70 - 0.10 + rng.gauss(0.0, 0.02), 0.01)
        bmp_rows.append((t, temp1, temp2, bmp280_temp_encode(temp1), bmp280_temp_encode(temp2)))

    add_dataset(
        "astronomy/tidal-locking_bmp280.example.csv",
        (
            "Time (s)",
            "Temperature 1 (°C)",
            "Temperature 2 (°C)",
            "Raw temperature 1 word (a.u.)",
            "Raw temperature 2 word (a.u.)",
        ),
        rows=bmp_rows,
        experiment="tidal-locking.phyphox",
        sensor="Bosch BMP280 die temperature (two SensorTags)",
        acquisition_path="SensorTag BLE AA41 notification, AA44=0x64 (1 s)",
        nominal_rate_hz=1.0,
        duration_s=300.0,
        scenario=(
            "Day-side and night-side model regions; the lamp is on from 30 s to "
            "210 s, then both sides cool."
        ),
        realism=[
            "Both columns are BMP280 die temperatures, not validated surface or air temperatures.",
            "The day side has a larger rise and a faster initial response; the night side stays nearly flat.",
            "Offsets differ between tags and 0.01 °C quantisation/noise is included.",
            "Time is reconstructed from tag 1's sample count for both columns.",
        ],
    )

    # TMP007 infrared object and die temperatures, 0.3 s.
    rng = random.Random(SEED + 29)
    count = 1001
    times = fixed_times(count, 0.3)
    ir_rows: list[tuple[object, ...]] = []
    for t in times:
        day = 23.0
        night = 22.9
        if 30.0 <= t < 210.0:
            day += 22.0 * (1.0 - math.exp(-(t - 30.0) / 65.0))
            night += 1.2 * (1.0 - math.exp(-(t - 30.0) / 140.0))
        elif t >= 210.0:
            day = 24.0 + 21.0 * math.exp(-(t - 210.0) / 80.0)
            night = 23.0 + 1.1 * math.exp(-(t - 210.0) / 130.0)
        amb1 = quantize(
            23.0 + 2.0 * smooth_pulse(t, 30.0, 20.0, 160.0, 40.0) + rng.gauss(0.0, 0.04), 0.03125
        )
        amb2 = quantize(
            22.9 + 1.2 * smooth_pulse(t, 30.0, 25.0, 160.0, 40.0) + rng.gauss(0.0, 0.04), 0.03125
        )
        obj1 = quantize(day + 1.0 + rng.gauss(0.0, 0.08), 0.03125)
        obj2 = quantize(night + 0.5 + rng.gauss(0.0, 0.08), 0.03125)
        ir_rows.append(
            (
                t,
                amb1,
                obj1,
                amb2,
                obj2,
                tmp007_encode(amb1),
                tmp007_encode(obj1),
                tmp007_encode(amb2),
                tmp007_encode(obj2),
            )
        )

    add_dataset(
        "astronomy/tidal-locking_tmp007.example.csv",
        (
            "Time (s)",
            "Ambient temperature 1 (°C)",
            "Object temperature 1 (°C)",
            "Ambient temperature 2 (°C)",
            "Object temperature 2 (°C)",
            "Raw ambient 1 word (a.u.)",
            "Raw object 1 word (a.u.)",
            "Raw ambient 2 word (a.u.)",
            "Raw object 2 word (a.u.)",
        ),
        rows=ir_rows,
        experiment="tidal-locking.phyphox",
        sensor="TI TMP007 infrared thermopile (two SensorTags)",
        acquisition_path="SensorTag BLE AA01 notification, AA03=0x1E (0.3 s)",
        nominal_rate_hz=3.333,
        duration_s=300.0,
        scenario="The same day/night illumination cycle seen by two TMP007 channels.",
        realism=[
            "Object and ambient/die temperature words use 0.03125 °C resolution.",
            "The object channel includes a 1 °C offset and 0.08 °C noise; the die channel is smoother.",
            "The day-side object temperature rises by about 22 °C under the lamp; the night side stays near ambient.",
            "The XML's unsigned conversion is valid here because all temperatures are positive.",
        ],
        notes="The trailing raw words are extra columns; the XML exports the four converted temperatures.",
    )

    # OPT3001 illuminance, 0.8 s.
    rng = random.Random(SEED + 30)
    count = 376
    times = fixed_times(count, 0.8)
    light_rows: list[tuple[object, ...]] = []
    for t in times:
        day = 0.0
        night = 0.0
        if 30.0 <= t < 210.0:
            day = 12000.0
            night = 28.0
        day *= 1.0 + 0.006 * math.sin(2.0 * math.pi * 0.13 * t)
        night *= 1.0 + 0.02 * math.sin(2.0 * math.pi * 0.17 * t)
        day = max(0.0, day + rng.gauss(0.0, max(0.05, 0.008 * day)))
        night = max(0.0, night + rng.gauss(0.0, max(0.02, 0.01 * night)))
        day_word = opt3001_encode(day * 1.03)
        night_word = opt3001_encode(night * 0.98)
        light_rows.append(
            (
                t,
                opt3001_decode(day_word),
                opt3001_decode(night_word),
                day_word,
                night_word,
            )
        )

    add_dataset(
        "astronomy/tidal-locking_opt3001.example.csv",
        (
            "Time (s)",
            "Illuminance 1 (lx)",
            "Illuminance 2 (lx)",
            "Raw light 1 word (a.u.)",
            "Raw light 2 word (a.u.)",
        ),
        rows=light_rows,
        experiment="tidal-locking.phyphox",
        sensor="TI OPT3001 ambient light sensor (two SensorTags)",
        acquisition_path="SensorTag BLE AA71 notification, AA73=0x50 (0.8 s)",
        nominal_rate_hz=1.25,
        duration_s=300.0,
        scenario="Day-side illuminance near 12,000 lx and night-side stray light near 28 lx, lamp on 30-210 s.",
        realism=[
            "OPT3001 automatic range selection and 0.01 lx encoding; the raw words are exported here for traceability.",
            "The 12,000 lx day side and 28 lx night side differ by more than two orders of magnitude.",
            "A 3% gain error, 0.8% noise, and a slow lamp ripple are included.",
            "The XML labels both light columns identically; this file suffixes them 1 and 2 for readability.",
        ],
    )


def make_transit() -> None:
    # SensorTag OPT3001 path, 0.8 s.
    rng = random.Random(SEED + 31)
    count = 113
    times = fixed_times(count, 0.8)
    rows: list[tuple[object, ...]] = []
    for t in times:
        baseline = 850.0 * (1.0 + 0.003 * math.sin(2.0 * math.pi * t / 90.0))
        depth = 0.0
        for center in (22.0, 52.0, 82.0):
            depth += 0.040 * smooth_pulse(t, center - 2.0, 0.8, 2.4, 0.8)
        lux = baseline * (1.0 - depth)
        lux += rng.gauss(0.0, 0.002 * lux)
        word = opt3001_encode(max(0.0, lux))
        rows.append((t, opt3001_decode(word), word))

    add_dataset(
        "astronomy/transitmethode_sensortag.example.csv",
        ("t (s)", "Relative Signal (a.u.)", "Raw OPT3001 word (a.u.)"),
        rows,
        experiment="transitmethode.phyphox",
        sensor="TI OPT3001 ambient light sensor (SensorTag)",
        acquisition_path="SensorTag BLE AA71 notification, AA73=0x50 (0.8 s)",
        nominal_rate_hz=1.25,
        duration_s=89.6,
        scenario="Three 4% transits of 4 s duration at 22 s, 52 s, and 82 s, with a stable 850 lx baseline.",
        realism=[
            "Transit depth is 4.0%, with 0.8 s ingress/egress, comparable to the sampling interval.",
            "The 0.8 s cadence gives only about 5 samples per transit, so the event is intentionally undersampled.",
            "A 0.2% noise level and slow lamp drift are included.",
            "The XML reconstructs time as 0.8 s times the sample count.",
            "The trailing raw word is provided for decoder checks, not by the XML export.",
        ],
        notes="The event centres and duration are chosen so the built-in threshold logic can find six on/off transitions.",
    )

    # Phone light-sensor path, 10 Hz.
    rng = random.Random(SEED + 32)
    count = 901
    times = phone_times(count, 0.1, rng, jitter=0.0012)
    rows = []
    for t in times:
        baseline = 520.0 * (1.0 + 0.004 * math.sin(2.0 * math.pi * t / 90.0))
        depth = 0.0
        for center in (22.0, 52.0, 82.0):
            depth += 0.040 * smooth_pulse(t, center - 2.0, 0.8, 2.4, 0.8)
        lux = baseline * (1.0 - depth)
        lux += rng.gauss(0.0, 0.0015 * lux)
        rows.append((t, max(0.0, lux)))

    add_dataset(
        "astronomy/transitmethode_phone.example.csv",
        ("t (s)", "Relative Signal (a.u.)"),
        rows,
        experiment="transitmethode.phyphox",
        sensor="Phone ambient-light sensor",
        acquisition_path="phyphox phone light sensor",
        nominal_rate_hz=10.0,
        duration_s=90.0,
        scenario="The same three-transit sequence recorded at 10 Hz on a phone.",
        realism=[
            "The 10 Hz cadence resolves the 4 s events with about 40 samples each.",
            "A 0.15% noise level and small timestamp jitter are included.",
            "The baseline differs from the SensorTag run because the phone's optical gain and spectral response differ.",
            "The file is an alternative acquisition path, not a simultaneous measurement.",
        ],
    )

    # Owon multimeter path, 2 Hz, solar-cell voltage.
    rng = random.Random(SEED + 33)
    count = 181
    times = fixed_times(count, 0.5)
    rows = []
    for t in times:
        baseline = 1.850 * (1.0 + 0.002 * math.sin(2.0 * math.pi * t / 90.0))
        depth = 0.0
        for center in (22.0, 52.0, 82.0):
            depth += 0.040 * smooth_pulse(t, center - 2.0, 0.8, 2.4, 0.8)
        voltage = baseline * (1.0 - depth)
        voltage = voltage * 1.002 + 0.0004 + rng.gauss(0.0, 0.0004)
        voltage = quantize(voltage, 0.001)
        field, decimal_code, unit_code = b35t_encode(voltage)
        rows.append((t, voltage, field, decimal_code, unit_code))

    add_dataset(
        "astronomy/transitmethode_owon.example.csv",
        (
            "Time (s)",
            "Relative Signal (a.u.)",
            "Raw numeric field (a.u.)",
            "Raw decimal code (a.u.)",
            "Raw unit code (a.u.)",
        ),
        rows,
        experiment="transitmethode.phyphox",
        sensor="Solar cell through an Owon B35T digital multimeter",
        acquisition_path="Owon BDM BLE notification, characteristic FFF4",
        nominal_rate_hz=2.0,
        duration_s=90.0,
        scenario="The same three-transit sequence seen as a 1.85 V solar-cell signal with 4% dips.",
        realism=[
            "The Owon app path updates about twice per second, so a 4 s transit contains only about 8 samples.",
            "The solar-cell voltage is assumed to be in a linear operating region; real open-circuit cells are logarithmic.",
            "1 mV quantisation, 0.2% gain error, 0.4 mV offset, and 0.4 mV noise are included.",
            "The raw fields follow the B35T decoder branch used by the experiment.",
            "The XML exports this path as a relative signal in volts, not as a normalized light curve.",
        ],
        notes="This path demonstrates why transducer linearity and meter range are part of the measurement model.",
    )


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def write_all() -> None:
    for dataset in DATASETS:
        dataset.path.parent.mkdir(parents=True, exist_ok=True)
        with dataset.path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(dataset.columns)
            for row in dataset.rows:
                writer.writerow([fmt(value) for value in row])

    manifest = {
        "schema_version": 1,
        "source": "example-data/generate_example_data.py",
        "seed": SEED,
        "example": True,
        "note": "Example exports for software, UI, and analysis development.",
        "datasets": [
            dataset.meta for dataset in sorted(DATASETS, key=lambda item: item.meta["file"])
        ],
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> None:
    DATASETS.clear()
    make_accelerometer()
    make_gyroscope()
    make_magnetometer()
    make_pressure()
    make_temperature_humidity()
    make_light_rgb()
    make_analog_inputs()
    make_albedo()
    make_greenhouse()
    make_ir_distance()
    make_mission_to_mars()
    make_owon_debug()
    make_pt_star()
    make_tidal_locking()
    make_transit()
    write_all()
    print(f"wrote {len(DATASETS)} datasets to {ROOT}")


if __name__ == "__main__":
    main()
