#!/usr/bin/env python3
# ruff: noqa: E501
"""Build sensor-specific example data for the 28 draft experiments.

The files are example exports for software, plotting, and teaching development.
They use the draft experiments' export columns, acquisition rates, units, and
dominant sensor behaviour. Run from the repository root:

    python3 example-data/generate_draft_example_data.py
"""

from __future__ import annotations

import csv
import json
import math
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from generate_example_data import (  # noqa: E402
    bmp280_pressure_encode,
    bmp280_temp_encode,
    clamp,
    core_times,
    fixed_times,
    fmt,
    keyframe,
    opt3001_decode,
    opt3001_encode,
    quantize,
    rotate_field,
    smooth_pulse,
)

ROOT = HERE / "drafts"
MANIFEST_PATH = ROOT / "manifest.json"
SEED = 20261026


@dataclass
class Dataset:
    path: Path
    columns: tuple[str, ...]
    rows: list[tuple[object, ...]]
    meta: dict[str, object] = field(default_factory=dict)


DATASETS: list[Dataset] = []


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def nano_clock(count: int, rng: random.Random) -> tuple[list[float], list[float]]:
    """20 Hz device time and a later, monotonic phone receive time."""
    device = core_times(count, rng)
    receive: list[float] = []
    last = 0.0
    for value in device:
        current = max(last + 0.001, value + 0.035 + rng.gauss(0.0, 0.003))
        receive.append(current)
        last = current
    return device, receive


def sensor_clock(count: int, period: float, rng: random.Random, start: float = 0.0) -> list[float]:
    """Monotonic receive times for a Bluetooth sensor service."""
    current = start
    out: list[float] = []
    for _ in range(count):
        out.append(current)
        current += max(period * 0.5, period + rng.gauss(0.0, period * 0.002))
    return out


def apds_counts(
    clear: float,
    red: float,
    green: float,
    blue: float,
    rng: random.Random,
) -> tuple[int, int, int, int]:
    """APDS-9960 RGBC counts with channel gains, dark counts, and noise."""
    gains = (1.02, 1.05, 0.97, 0.92)
    darks = (3.0, 2.0, 2.0, 1.0)
    counts: list[int] = []
    for channel, value in enumerate((clear, red, green, blue)):
        value = value * gains[channel] + darks[channel]
        value *= 1.0 + rng.gauss(0.0, 0.003)
        value += rng.gauss(0.0, 2.0 + 0.008 * value)
        counts.append(int(round(clamp(value, 0.0, 4100.0))))
    return counts[0], counts[1], counts[2], counts[3]


def add_dataset(
    filename: str,
    columns: Sequence[str],
    rows: Sequence[Sequence[object]],
    *,
    experiment: str,
    sensor: str,
    acquisition_path: str,
    nominal_rate_hz: float | None,
    duration_s: float | None,
    scenario: str,
    realism: Sequence[str],
    notes: str = "",
) -> None:
    path = ROOT / filename
    columns_tuple = tuple(columns)
    rows_list = [tuple(row) for row in rows]
    for row in rows_list:
        if len(row) != len(columns_tuple):
            raise ValueError(f"{filename}: {len(row)} cells for {len(columns_tuple)} columns")
    meta: dict[str, object] = {
        "file": f"drafts/{filename}",
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
        "source": "example-data/generate_draft_example_data.py",
        "seed": SEED,
        "example": True,
        "note": "Example exports for the 28 draft experiments.",
        "datasets": [
            dataset.meta for dataset in sorted(DATASETS, key=lambda item: item.meta["file"])
        ],
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# 1. Audio and magnetic motor comparison
# ---------------------------------------------------------------------------


def make_audio_magnetic() -> None:
    rng = random.Random(SEED + 101)
    count = 1201
    _, receive = nano_clock(count, rng)
    rows: list[tuple[object, ...]] = []
    for t in receive:
        motor_on = (
            1.0 if any(start <= t < end for start, end in ((10, 20), (30, 40), (50, 60))) else 0.0
        )
        bx = (
            18.9
            + motor_on * 2.0 * (1.0 + 0.08 * math.sin(2.0 * math.pi * 5.0 * t))
            + rng.gauss(0.0, 0.15)
        )
        by = motor_on * -1.2 + rng.gauss(0.0, 0.15)
        bz = (
            44.5
            + motor_on * 3.5 * (1.0 + 0.06 * math.sin(2.0 * math.pi * 5.0 * t))
            + rng.gauss(0.0, 0.15)
        )
        rows.append((t, bx, by, bz, math.sqrt(bx * bx + by * by + bz * bz), 3))
    add_dataset(
        "audio-magnetic_magnetic.example.csv",
        ("mag_t", "bx", "by", "bz", "mag_norm", "mag_accuracy"),
        rows,
        experiment="audio-magnetic.phyphox",
        sensor="Phone magnetometer",
        acquisition_path="phyphox magnetic_field sensor, 20 Hz",
        nominal_rate_hz=20.0,
        duration_s=60.0,
        scenario="Stationary phone beside a small motor switched on for three 10 s intervals.",
        realism=[
            "Earth field near 48 µT plus a motor-dependent vector of a few µT.",
            "0.15 µT broadband noise and a small 5 Hz motor ripple.",
            "Accuracy code 3 is reported as a high-confidence phone magnetometer sample.",
        ],
    )

    blocks = 601
    audio_rows: list[tuple[object, ...]] = []
    for index in range(blocks):
        t = 0.1 * (index + 1)
        on = any(start <= t < end for start, end in ((10, 20), (30, 40), (50, 60)))
        rms = 0.012 if not on else 0.045 * (1.0 + 0.05 * math.sin(2.0 * math.pi * 2.0 * t))
        rms = max(0.0, rms + rng.gauss(0.0, 0.0015))
        noise_corrected = math.sqrt(max(0.0, rms * rms - 0.010**2))
        level = 20.0 * math.log10(rms / 0.020) if rms > 0 else math.nan
        audio_rows.append((t, rms, 4800, 48000.0, 0.1, noise_corrected, level))
    add_dataset(
        "audio-magnetic_audio.example.csv",
        (
            "audio_t",
            "audio_rms",
            "audio_n",
            "audio_fs",
            "audio_duration",
            "noise_corrected_rms",
            "level",
        ),
        audio_rows,
        experiment="audio-magnetic.phyphox",
        sensor="Phone microphone",
        acquisition_path="phyphox audio input, 48 kHz, 0.1 s analysis blocks",
        nominal_rate_hz=10.0,
        duration_s=60.0,
        scenario="Motor-off and motor-on plateaus, with 0.1 s block RMS values.",
        realism=[
            "48 kHz sample rate and 4800 samples per 0.1 s block.",
            "Relative digital amplitude, not calibrated or A-weighted sound pressure.",
            "10 dB motor-on level change with block-to-block variation.",
            "Raw audio samples are omitted because the full 48 kHz stream is large; the block table is the analysis record.",
        ],
    )


# ---------------------------------------------------------------------------
# 2-7. CC2541 adapters
# ---------------------------------------------------------------------------


def make_cc2541_accelerometer() -> None:
    rng = random.Random(SEED + 102)
    times = sensor_clock(601, 0.1, rng)
    pitch_keys = (
        (0.0, 0.0),
        (10.0, 0.0),
        (15.0, 20.0),
        (20.0, 20.0),
        (25.0, -20.0),
        (30.0, -20.0),
        (35.0, 0.0),
        (40.0, 0.0),
        (45.0, 0.0),
        (60.0, 0.0),
    )
    roll_keys = (
        (0.0, 0.0),
        (30.0, 0.0),
        (40.0, 0.0),
        (45.0, 60.0),
        (50.0, 60.0),
        (55.0, 0.0),
        (60.0, 0.0),
    )
    bias = (0.20, -0.25, 0.35)
    scale = 9.80665 / 64.0
    rows: list[tuple[object, ...]] = []
    for t in times:
        pitch = math.radians(keyframe(t, pitch_keys))
        roll = math.radians(keyframe(t, roll_keys))
        ax = math.sin(pitch)
        ay = -math.sin(roll) * math.cos(pitch)
        az = math.cos(roll) * math.cos(pitch)
        shake = smooth_pulse(t, 30.0, 1.0, 4.0, 2.0)
        ax += 0.06 * shake * math.sin(2.0 * math.pi * 4.0 * t)
        az += 0.08 * shake * math.sin(2.0 * math.pi * 5.5 * t)
        true = (ax * 9.80665, ay * 9.80665, az * 9.80665)
        raw = tuple(int(round(clamp((true[i] + bias[i]) / scale, -128, 127))) for i in range(3))
        corrected = tuple(raw[i] * scale - bias[i] for i in range(3))
        magnitude = math.sqrt(sum(value * value for value in corrected))
        rows.append((t, *raw, *corrected, magnitude))
    add_dataset(
        "cc2541-accelerometer.example.csv",
        (
            "Receive time (s)",
            "Signed packet x (count)",
            "Signed packet y (count)",
            "Signed packet z (count)",
            "Bias corrected x (m/s²)",
            "Bias corrected y (m/s²)",
            "Bias corrected z (m/s²)",
            "Vector magnitude (m/s²)",
        ),
        rows,
        experiment="cc2541-accelerometer.phyphox",
        sensor="TI CC2541 SensorTag KXTJ9 accelerometer",
        acquisition_path="SensorTag AA11 notification, AA13=0x0A (100 ms)",
        nominal_rate_hz=10.0,
        duration_s=60.0,
        scenario="Flat, ±20° tilts, a short shake, a 60° roll, and a return to flat.",
        realism=[
            "±2 g, 8-bit KXTJ9 setting with 64 counts per g.",
            "Signed int8 counts, including the -128 minimum byte.",
            "Bias of 0.20, -0.25, 0.35 m/s² and 0.02 m/s² noise.",
            "10 Hz receive-time stream; the 100 ms request is not a guaranteed conversion clock.",
        ],
    )


def make_cc2541_gyroscope() -> None:
    rng = random.Random(SEED + 103)
    times = sensor_clock(601, 0.1, rng)
    keys = {
        "x": ((0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (30.0, 200.0), (40.0, 0.0), (60.0, 0.0)),
        "y": ((0.0, 0.0), (30.0, 0.0), (40.0, -200.0), (50.0, -200.0), (55.0, 0.0), (60.0, 0.0)),
        "z": ((0.0, 0.0), (10.0, 125.0), (20.0, -125.0), (30.0, 0.0), (60.0, 0.0)),
    }
    bias_dps = (0.286, -0.229, 0.401)
    scale_dps = 500.0 / 65536.0
    rows: list[tuple[object, ...]] = []
    for t in times:
        true = tuple(keyframe(t, keys[axis]) + rng.gauss(0.0, 0.8) for axis in ("x", "y", "z"))
        raw = tuple(
            int(round(clamp((true[i] + bias_dps[i]) / scale_dps, -32768, 32767))) for i in range(3)
        )
        corrected = tuple(
            raw[i] * math.radians(scale_dps) - math.radians(bias_dps[i]) for i in range(3)
        )
        magnitude = math.sqrt(sum(value * value for value in corrected))
        rows.append((t, *raw, *corrected, magnitude))
    add_dataset(
        "cc2541-gyroscope.example.csv",
        (
            "Receive time (s)",
            "Signed packet x (count)",
            "Signed packet y (count)",
            "Signed packet z (count)",
            "Bias corrected x (rad/s)",
            "Bias corrected y (rad/s)",
            "Bias corrected z (rad/s)",
            "Vector magnitude (rad/s)",
        ),
        rows,
        experiment="cc2541-gyroscope.phyphox",
        sensor="TI CC2541 SensorTag IMU-3000 gyroscope",
        acquisition_path="SensorTag AA51 notification, 100 ms assumed period",
        nominal_rate_hz=10.0,
        duration_s=60.0,
        scenario="Stationary, ±125 °/s yaw, ±200 °/s roll/pitch, then stationary again.",
        realism=[
            "500 °/s total span and 500/65536 °/s per signed count.",
            "Small zero-rate bias in rad/s and 0.8 °/s rate noise.",
            "Signed little-endian 16-bit packet components.",
            "Receive time is a phone clock, not a device conversion time.",
        ],
    )


def make_cc2541_humidity() -> None:
    rng = random.Random(SEED + 104)
    times = sensor_clock(61, 1.0, rng)
    rows: list[tuple[object, ...]] = []
    for t in times:
        temperature = 22.5 + 0.3 * (1.0 - math.exp(-t / 60.0)) + rng.gauss(0.0, 0.05)
        humidity = (
            45.0 + 20.0 * math.exp(-((t - 30.0) ** 2) / 120.0) - 2.0 * (1.0 - math.exp(-t / 60.0))
        )
        temperature = clamp(temperature, -40.0, 120.0)
        humidity = clamp(humidity, 0.0, 100.0)
        raw_t = int(round((temperature + 46.85) * 65536.0 / 175.72)) | 3
        raw_h = int(round((humidity + 6.0) * 65536.0 / 125.0)) | 3
        masked_t = (raw_t // 4) * 4
        masked_h = (raw_h // 4) * 4
        unbounded = 125.0 * masked_h / 65536.0 - 6.0
        checked = unbounded if 0.0 <= unbounded <= 100.0 else math.nan
        temp = 175.72 * masked_t / 65536.0 - 46.85
        rows.append((t, raw_t, raw_h, unbounded, checked, temp))
    add_dataset(
        "cc2541-humidity.example.csv",
        (
            "Receive time (s)",
            "Unsigned temperature packet word",
            "Unsigned humidity packet word",
            "Unbounded RH equation (%)",
            "Domain checked RH (%)",
            "SHT21 temperature (°C)",
        ),
        rows,
        experiment="cc2541-humidity.phyphox",
        sensor="TI CC2541 SensorTag SHT21",
        acquisition_path="SensorTag AA21 notification, 1 s assumed period",
        nominal_rate_hz=1.0,
        duration_s=60.0,
        scenario="Slow warming with a short humidity breath event near 30 s.",
        realism=[
            "SHT21 equations RH = 125 SRH/65536 - 6 and T = 175.72 ST/65536 - 46.85.",
            "Low two status bits set and masked before conversion.",
            "0.05 °C and 0.4 %RH noise; outside-domain RH becomes nan.",
            "One receive clock shared by the paired temperature and humidity words.",
        ],
    )


def make_cc2541_ir_temperature() -> None:
    rng = random.Random(SEED + 105)
    times = sensor_clock(61, 1.0, rng)
    coeffs = {
        "s0": 5.0e-14,
        "a1": 1.75e-3,
        "a2": -1.678e-5,
        "b0": -2.94e-5,
        "b1": -5.7e-7,
        "b2": 1.9e-8,
        "c2": 13.4,
        "tref": 298.15,
    }
    rows: list[tuple[object, ...]] = []
    for t in times:
        die = 23.0 + 0.6 * (1.0 - math.exp(-t / 60.0)) + rng.gauss(0.0, 0.03)
        target = 23.0
        if 10.0 <= t < 25.0:
            target = 35.0
        elif 25.0 <= t < 40.0:
            target = 45.0
        elif 40.0 <= t < 50.0:
            target = 30.0
        target += rng.gauss(0.0, 0.15)
        die_k = die + 273.15
        delta = die_k - coeffs["tref"]
        sensitivity = coeffs["s0"] * (1.0 + coeffs["a1"] * delta + coeffs["a2"] * delta * delta)
        offset = coeffs["b0"] + coeffs["b1"] * delta + coeffs["b2"] * delta * delta
        flux = sensitivity * ((target + 273.15) ** 4 - die_k**4)
        discriminant = 1.0 + 4.0 * coeffs["c2"] * flux
        if discriminant <= 0.0 or sensitivity <= 0.0:
            voltage = 0.0
        else:
            voltage = (-1.0 + math.sqrt(discriminant)) / (2.0 * coeffs["c2"]) + offset
        voltage_word = int(round(clamp(voltage / 156.25e-9, -32768, 32767)))
        die_word = int(round(die * 128.0))
        voltage_back = voltage_word * 156.25e-9
        die_back = die_word / 128.0
        die_k_back = die_back + 273.15
        delta_back = die_k_back - coeffs["tref"]
        sensitivity_back = coeffs["s0"] * (
            1.0 + coeffs["a1"] * delta_back + coeffs["a2"] * delta_back * delta_back
        )
        offset_back = (
            coeffs["b0"] + coeffs["b1"] * delta_back + coeffs["b2"] * delta_back * delta_back
        )
        compensated = voltage_back - offset_back
        flux_back = compensated + coeffs["c2"] * compensated * compensated
        object_k = (die_k_back**4 + flux_back / sensitivity_back) ** 0.25
        object_c = object_k - 273.15
        rows.append(
            (
                t,
                voltage_word,
                die_word,
                voltage_back,
                die_back,
                sensitivity_back,
                offset_back,
                compensated,
                object_c,
            )
        )
    add_dataset(
        "cc2541-ir-temperature.example.csv",
        (
            "Receive time (s)",
            "Signed thermopile packet word",
            "Signed die packet word",
            "Thermopile voltage (V)",
            "Die temperature (°C)",
            "Temperature dependent sensitivity (V/K^4)",
            "Voltage offset (V)",
            "Compensated flux voltage (V)",
            "Application model object temperature (°C)",
        ),
        rows,
        experiment="cc2541-ir-temperature.phyphox",
        sensor="TI CC2541 SensorTag TMP006 infrared thermopile",
        acquisition_path="SensorTag AA01 notification, 1 s assumed period",
        nominal_rate_hz=1.0,
        duration_s=60.0,
        scenario="A warm target is held near 35 °C and 45 °C, then cools, while the die warms slightly.",
        realism=[
            "156.25 nV per thermopile count and 1/128 °C per die count.",
            "Signed voltage and die words, including negative voltage counts.",
            "Application model coefficients are example calibration values, not a certificate.",
            "Object output is the TMP006 compensated fourth-root result.",
        ],
    )


def make_cc2541_magnetometer() -> None:
    rng = random.Random(SEED + 106)
    times = sensor_clock(601, 0.1, rng)
    yaw_keys = ((0.0, 0.0), (20.0, 0.0), (30.0, 80.0), (40.0, 80.0), (50.0, 0.0), (60.0, 0.0))
    pitch_keys = ((0.0, 0.0), (30.0, 0.0), (40.0, 20.0), (50.0, 0.0), (60.0, 0.0))
    bias = (5.0, -3.0, 8.0)
    scale = 0.1
    rows: list[tuple[object, ...]] = []
    for t in times:
        bx, by, bz = rotate_field(
            (18.9, 0.0, 44.5), keyframe(t, yaw_keys), keyframe(t, pitch_keys), 0.0
        )
        magnet = smooth_pulse(t, 40.0, 2.0, 3.0, 4.0)
        bx += magnet * 70.0 * math.exp(-((t - 43.0) ** 2) / 14.0)
        by -= magnet * 35.0 * math.exp(-((t - 43.0) ** 2) / 18.0)
        bz += magnet * 80.0 * math.exp(-((t - 43.0) ** 2) / 12.0)
        bx += rng.gauss(0.0, 0.12) + bias[0]
        by += rng.gauss(0.0, 0.12) + bias[1]
        bz += rng.gauss(0.0, 0.12) + bias[2]
        raw = tuple(int(round(clamp(value / scale, -32768, 32767))) for value in (bx, by, bz))
        corrected = tuple(raw[i] * scale - bias[i] for i in range(3))
        magnitude = math.sqrt(sum(value * value for value in corrected))
        rows.append((t, *raw, *corrected, magnitude))
    add_dataset(
        "cc2541-magnetometer.example.csv",
        (
            "Receive time (s)",
            "Signed packet x (count)",
            "Signed packet y (count)",
            "Signed packet z (count)",
            "Bias corrected x (µT)",
            "Bias corrected y (µT)",
            "Bias corrected z (µT)",
            "Vector magnitude (µT)",
        ),
        rows,
        experiment="cc2541-magnetometer.phyphox",
        sensor="TI CC2541 SensorTag MAG3110",
        acquisition_path="SensorTag AA31 notification, AA33=0x0A (100 ms)",
        nominal_rate_hz=10.0,
        duration_s=60.0,
        scenario="Earth-field baseline, 80° yaw, 20° tilt, a magnet approach near 43 s, then return.",
        realism=[
            "MAG3110 nominal 0.1 µT per signed count and 10 Hz period request.",
            "Bias of 5, -3, 8 µT and 0.12 µT noise.",
            "Hard-iron offset and a magnet disturbance are retained as sensor-frame components.",
            "The scale-verified gate is assumed enabled for this example.",
        ],
    )


def make_cc2541_pressure() -> None:
    rng = random.Random(SEED + 107)
    times = sensor_clock(61, 1.0, rng)
    c0, c1, c2, c3, c4, c5, c6, c7 = 30000, 400, 40000, 1000, -200, 100, -300, 50
    rows: list[tuple[object, ...]] = []
    for t in times:
        target_t = 23.0 + 0.4 * (1.0 - math.exp(-t / 60.0)) + rng.gauss(0.0, 0.04)
        leak = 1.5 * clamp((t - 28.0) / 17.0, 0.0, 1.0)
        target_p = 1008.0 + (20.0 - leak) * smooth_pulse(t, 20.0, 5.0, 20.0, 5.0)
        target_p += rng.gauss(0.0, 0.03)
        ut = int(round(((target_t * 65536.0 / 100.0) - c1 * 64.0) * 256.0 / c0))
        ut = int(clamp(ut, -32768, 32767))
        sensitivity = c2 + c3 * ut / 2**17 + c4 * ut**2 / 2**34
        offset = c5 * 2**14 + c6 * ut / 8 + c7 * ut**2 / 2**19
        up = int(round((target_p * 100.0 * 2**14 - offset) / sensitivity))
        up = int(clamp(up, 0, 65535))
        pressure = (sensitivity * up + offset) / 2**14 / 100.0
        temperature = 100.0 * (c0 * ut / 256.0 + c1 * 64.0) / 65536.0
        rows.append((t, up, ut, pressure, temperature))
    add_dataset(
        "cc2541-pressure.example.csv",
        (
            "Data read receive time (s)",
            "Unsigned pressure word",
            "Signed temperature word",
            "Pressure (hPa)",
            "T5400 temperature (°C)",
        ),
        rows,
        experiment="cc2541-pressure.phyphox",
        sensor="TI CC2541 SensorTag EPCOS T5400",
        acquisition_path="SensorTag AA41 poll, 1 Hz",
        nominal_rate_hz=1.0,
        duration_s=60.0,
        scenario="A near-ambient baseline, a +20 hPa chamber excursion, a small leak, and release.",
        realism=[
            "T5400 compensation polynomial with the fixture calibration coefficients.",
            "Signed UT and unsigned UP 16-bit words.",
            "1 Hz polling timestamps receipt of the data read, not the conversion instant.",
            "Calibration is assumed loaded and verified for this example.",
        ],
    )


# ---------------------------------------------------------------------------
# 8. Colour temperature
# ---------------------------------------------------------------------------


COLOUR_TARGETS = (
    (2700.0, (0.60, 0.60, 0.15)),
    (4000.0, (0.15, 0.75, 0.15)),
    (6500.0, (0.20, 0.85, 0.55)),
)


def colour_target(cct: float) -> tuple[float, float, float]:
    """Interpolate a plausible RGBC ratio set for warm, neutral, and cool lamps."""
    if cct <= COLOUR_TARGETS[0][0]:
        return COLOUR_TARGETS[0][1]
    for (t0, q0), (t1, q1) in zip(COLOUR_TARGETS, COLOUR_TARGETS[1:]):
        if cct <= t1:
            u = (cct - t0) / (t1 - t0)
            return tuple(q0[i] + (q1[i] - q0[i]) * u for i in range(3))
    return COLOUR_TARGETS[-1][1]


def make_colour_temperature() -> None:
    rng = random.Random(SEED + 108)
    count = 1201
    device, receive = nano_clock(count, rng)
    cct_keys = (
        (0.0, 2700.0),
        (15.0, 2700.0),
        (20.0, 4000.0),
        (30.0, 4000.0),
        (35.0, 6500.0),
        (45.0, 6500.0),
        (50.0, 2700.0),
        (60.0, 2700.0),
    )
    dark = (3.0, 2.0, 2.0, 1.0)
    rows: list[tuple[object, ...]] = []
    for i, (t_dev, t_rec) in enumerate(zip(device, receive)):
        cct = keyframe(t_dev, cct_keys)
        q_r, q_g, q_b = colour_target(cct)
        clear = 2000.0 + rng.gauss(0.0, 12.0)
        red = q_r * (clear - dark[0]) + dark[0] + rng.gauss(0.0, 6.0)
        green = q_g * (clear - dark[0]) + dark[1] + rng.gauss(0.0, 6.0)
        blue = q_b * (clear - dark[0]) + dark[2] + rng.gauss(0.0, 6.0)
        clear, red, green, blue = apds_counts(clear, red, green, blue, rng)
        corrected_clear = clear - dark[0]
        q = (
            (red - dark[1]) / corrected_clear,
            (green - dark[2]) / corrected_clear,
            (blue - dark[3]) / corrected_clear,
        )
        big_x = -0.14282 * q[0] + 1.54924 * q[1] - 0.95641 * q[2]
        big_y = -0.32466 * q[0] + 1.57837 * q[1] - 0.73191 * q[2]
        big_z = -0.68202 * q[0] + 0.77073 * q[1] + 0.56332 * q[2]
        total = big_x + big_y + big_z
        if total > 0 and big_x > 0 and big_y > 0 and big_z > 0:
            chroma_x = big_x / total
            chroma_y = big_y / total
            n = (
                (chroma_x - 0.3320) / (0.1858 - chroma_y)
                if abs(chroma_y - 0.1858) > 1e-6
                else math.nan
            )
            candidate = (
                449.0 * n**3 + 3525.0 * n**2 + 6823.3 * n + 5520.33
                if not math.isnan(n)
                else math.nan
            )
            accepted = candidate if 2000.0 <= candidate <= 10000.0 else math.nan
        else:
            chroma_x = chroma_y = n = candidate = accepted = math.nan
        rows.append(
            (
                t_dev,
                t_rec,
                clear,
                red,
                green,
                blue,
                corrected_clear,
                q[0],
                q[1],
                q[2],
                big_x,
                big_y,
                big_z,
                total,
                chroma_x,
                chroma_y,
                n,
                candidate,
                accepted,
            )
        )
    add_dataset(
        "colour-temperature.example.csv",
        (
            "device_t (s)",
            "receive_t (s)",
            "clear (counts)",
            "red (counts)",
            "green (counts)",
            "blue (counts)",
            "Dark-corrected clear (counts)",
            "Red / clear corrected (1)",
            "Green / clear corrected (1)",
            "Blue / clear corrected (1)",
            "Provisional X (relative)",
            "Provisional Y (relative)",
            "Provisional Z (relative)",
            "Provisional XYZ sum (relative)",
            "Chromaticity x (1)",
            "Chromaticity y (1)",
            "McCamy n (1)",
            "Unvalidated polynomial candidate (K)",
            "Accepted indicative CCT (K)",
        ),
        rows,
        experiment="colour-temperature.phyphox",
        sensor="Arduino Nano 33 BLE Sense APDS-9960 RGBC",
        acquisition_path="Nano mode 6 BLE notification, 20 Hz",
        nominal_rate_hz=20.0,
        duration_s=60.0,
        scenario="Warm 2700 K, neutral 4000 K, cool 6500 K, and warm again, each held for 10–15 s.",
        realism=[
            "Raw RGBC counts with APDS channel gains and 4100-count clamping.",
            "The documented donor XYZ matrix and McCamy polynomial are applied.",
            "The accepted CCT is gated to the 2000–10000 K screening interval.",
            "Broad-band RGBC cannot establish a full spectrum or a stellar temperature.",
        ],
    )


# ---------------------------------------------------------------------------
# 9. Coronagraph observations
# ---------------------------------------------------------------------------


def make_coronagraph() -> None:
    rng = random.Random(SEED + 109)
    rows: list[tuple[object, ...]] = []
    observation_id = 1
    for repeat in range(2):
        for mask in (0, 1):
            for separation in (30, 60, 90, 120, 150, 180):
                if mask == 0:
                    target = 120.0 + 80.0 / (separation / 30.0) + rng.gauss(0.0, 2.0)
                    background = 50.0 + rng.gauss(0.0, 1.5)
                    sigma = 4.0 + 0.01 * target
                else:
                    target = 45.0 + 25.0 / (separation / 30.0) + rng.gauss(0.0, 1.2)
                    background = 18.0 + rng.gauss(0.0, 0.8)
                    sigma = 2.0 + 0.01 * target
                ceiling = 255.0
                exposure = 10.0
                net = target - background
                contrast = net / background if background > 0 else math.nan
                rate = 1000.0 * net / exposure
                snr = net / sigma if sigma > 0 else math.nan
                rows.append(
                    (
                        observation_id,
                        mask,
                        separation,
                        exposure,
                        target,
                        background,
                        sigma,
                        ceiling,
                        1,
                        net,
                        contrast,
                        rate,
                        snr,
                        contrast if mask == 0 else math.nan,
                        contrast if mask == 1 else math.nan,
                    )
                )
                observation_id += 1
    add_dataset(
        "coronagraph-contrast.example.csv",
        (
            "Observation ID",
            "Mask code (0 absent, 1 present)",
            "Image separation (pixel)",
            "Exposure duration (ms)",
            "Target ROI mean (a.u.)",
            "Local background ROI mean (a.u.)",
            "Uncertainty of target-minus-background mean (a.u.)",
            "Unsaturated ceiling (a.u.)",
            "Fixed linear image settings checked (1=yes)",
            "Target minus background (a.u.)",
            "Local relative contrast",
            "Net signal rate (a.u./s)",
            "Noise-normalized signal",
            "Unmasked local contrast",
            "Masked local contrast",
        ),
        rows,
        experiment="coronagraph-contrast.phyphox",
        sensor="Fixed-exposure camera and external ROI analysis",
        acquisition_path="Manual image-region statistics, two repeats per mask/separation",
        nominal_rate_hz=None,
        duration_s=None,
        scenario="Six image separations from 30 to 180 px, each with mask absent and present.",
        realism=[
            "Target and background ROI means in arbitrary linear image units.",
            "A 10 ms fixed exposure and a 255-unit unsaturated ceiling.",
            "Masked images reduce both target and background, as a real occulting disk would.",
            "Contrast is local (target minus background)/background, not a planet/star flux ratio.",
        ],
    )


# ---------------------------------------------------------------------------
# 10. Detector characterization
# ---------------------------------------------------------------------------


def make_detector_characterization() -> None:
    rng = random.Random(SEED + 110)
    count = 1201
    device, receive = nano_clock(count, rng)
    rows: list[tuple[object, ...]] = []
    for t in device:
        if t < 10.0:
            clear = 8.0
        else:
            clear = 1000.0
            for start, depth, duration in (
                (30.0, 0.01, 0.5),
                (34.0, 0.02, 1.0),
                (38.0, 0.04, 2.0),
                (44.0, 0.08, 4.0),
            ):
                if start <= t < start + duration:
                    clear *= 1.0 - depth
        red = clear * 0.55
        green = clear * 0.62
        blue = clear * 0.38
        c, r, g, b = apds_counts(clear, red, green, blue, rng)
        rows.append((t, receive[len(rows)], c, r, g, b))
    add_dataset(
        "detector-characterization.example.csv",
        (
            "device_t (s)",
            "receive_t (s)",
            "clear (counts)",
            "red (counts)",
            "green (counts)",
            "blue (counts)",
        ),
        rows,
        experiment="detector-characterization.phyphox",
        sensor="Arduino Nano 33 BLE Sense APDS-9960",
        acquisition_path="Nano mode 6 BLE notification, 20 Hz",
        nominal_rate_hz=20.0,
        duration_s=60.0,
        scenario="Dark, stable 1000-count baseline, then 1%, 2%, 4%, and 8% light features.",
        realism=[
            "APDS counts with channel gains and 4100-count clamping.",
            "The feature depths are relative to the illuminated baseline.",
            "Device and phone receive clocks are both present and not identical.",
            "The summary row reports delivered rates and baseline noise, not chip bandwidth.",
        ],
    )

    intervals_device = [b - a for a, b in zip(device, device[1:])]
    intervals_receive = [b - a for a, b in zip(receive, receive[1:])]
    baseline = [row[2] for row in rows if 12.0 <= row[0] <= 28.0]
    mean_device = sum(intervals_device) / len(intervals_device)
    mean_receive = sum(intervals_receive) / len(intervals_receive)
    sd_device = (
        sum((value - mean_device) ** 2 for value in intervals_device) / (len(intervals_device) - 1)
    ) ** 0.5
    sd_receive = (
        sum((value - mean_receive) ** 2 for value in intervals_receive)
        / (len(intervals_receive) - 1)
    ) ** 0.5
    baseline_mean = sum(baseline) / len(baseline)
    baseline_sd = (
        sum((value - baseline_mean) ** 2 for value in baseline) / (len(baseline) - 1)
    ) ** 0.5
    expected_drop = 0.02 * (baseline_mean - 8.0)
    add_dataset(
        "detector-characterization_summary.example.csv",
        (
            "Mean device interval (s)",
            "Mean receive interval (s)",
            "Device interval sample SD (s)",
            "Receive interval sample SD (s)",
            "Mean delivered device rate (Hz)",
            "Mean delivered receive rate (Hz)",
            "Selected baseline count (1)",
            "Baseline mean (counts)",
            "Baseline sample SD (counts)",
            "Proposed signal drop (counts)",
            "Expected single-sample SNR (1)",
            "Mean samples per feature (1)",
        ),
        [
            (
                mean_device,
                mean_receive,
                sd_device,
                sd_receive,
                1.0 / mean_device,
                1.0 / mean_receive,
                len(baseline),
                baseline_mean,
                baseline_sd,
                expected_drop,
                expected_drop / baseline_sd,
                1.0 / mean_device,
            )
        ],
        experiment="detector-characterization.phyphox",
        sensor="Arduino Nano 33 BLE Sense APDS-9960",
        acquisition_path="Derived summary from the 20 Hz example record",
        nominal_rate_hz=20.0,
        duration_s=60.0,
        scenario="Summary of the measured intervals and 12–28 s baseline.",
        realism=[
            "Intervals are computed from the actual example timestamps.",
            "Baseline mean and sample standard deviation use the selected window.",
            "The SNR is a planning quantity for a 2% drop, not a detection claim.",
        ],
    )


# ---------------------------------------------------------------------------
# 11-12. Eclipsing binary and exomoon photometry
# ---------------------------------------------------------------------------


def make_eclipsing_binary() -> None:
    rng = random.Random(SEED + 111)
    count = 2401
    device, receive = nano_clock(count, rng)
    rows: list[tuple[object, ...]] = []
    for t, r in zip(device, receive):
        clear = 210.0
        for center, depth, duration in (
            (20.0, 0.30, 4.0),
            (35.0, 0.10, 3.0),
            (50.0, 0.30, 4.0),
            (65.0, 0.10, 3.0),
            (80.0, 0.30, 4.0),
            (95.0, 0.10, 3.0),
            (110.0, 0.30, 4.0),
        ):
            if center - duration / 2 <= t < center + duration / 2:
                clear *= 1.0 - depth
        c, rr, g, b = apds_counts(clear, clear * 0.55, clear * 0.62, clear * 0.38, rng)
        normalized = (c - 10.0) / (210.0 - 10.0)
        phase = ((r - 20.0) / 30.0) % 1.0
        rows.append((r, t, c, rr, g, b, normalized, phase))
    add_dataset(
        "eclipsing-binary.example.csv",
        ("receive_time", "device_time", "clear", "red", "green", "blue", "normalized", "phase"),
        rows,
        experiment="eclipsing-binary.phyphox",
        sensor="Arduino Nano 33 BLE Sense APDS-9960",
        acquisition_path="Nano mode 6 BLE notification, 20 Hz",
        nominal_rate_hz=20.0,
        duration_s=120.0,
        scenario="Alternating 30% primary and 10% secondary minima with a 30 s primary-to-primary period.",
        realism=[
            "Raw clear/RGB counts with APDS gains and noise.",
            "Normalized light uses dark 10 counts and baseline 210 counts.",
            "Phase uses epoch 20 s and period 30 s.",
            "Primary and secondary labels are observationally defined, not an orbital fit.",
        ],
    )


def make_exomoon() -> None:
    rng = random.Random(SEED + 112)
    count = 2401
    device, receive = nano_clock(count, rng)
    rows: list[tuple[object, ...]] = []
    for t, r in zip(device, receive):
        if 20 <= t < 35:
            clear = 100.0
        elif 35 <= t < 50:
            clear = 97.0
        elif 50 <= t < 60:
            clear = 99.0
        elif 60 <= t < 75:
            clear = 97.0
        elif 75 <= t < 90:
            clear = 100.0
        else:
            clear = 110.0
        c, rr, g, b = apds_counts(clear, clear * 0.55, clear * 0.62, clear * 0.38, rng)
        normalized = (c - 10.0) / (110.0 - 10.0)
        rows.append((r, t, c, rr, g, b, normalized))
    add_dataset(
        "exomoon-photometry.example.csv",
        ("receive_time", "device_time", "clear", "red", "green", "blue", "normalized"),
        rows,
        experiment="exomoon-photometry.phyphox",
        sensor="Arduino Nano 33 BLE Sense APDS-9960",
        acquisition_path="Nano mode 6 BLE notification, 20 Hz",
        nominal_rate_hz=20.0,
        duration_s=120.0,
        scenario="Baseline, planet-only, separated moon, overlapping moon, separated moon, planet-only, baseline.",
        realism=[
            "Counts follow the intended ordering baseline ≥ planet-only ≥ overlap ≥ separated ≥ dark.",
            "Normalized light uses dark 10 and baseline 110 counts.",
            "The overlap interval is a local brightening relative to the separated interval.",
            "The example does not assign a moon radius or a barycentric orbit.",
        ],
    )


# ---------------------------------------------------------------------------
# 13. Single SensorTag warming
# ---------------------------------------------------------------------------


def make_greenhouse_single() -> None:
    rng = random.Random(SEED + 113)
    times = sensor_clock(301, 1.0, rng)
    rows: list[tuple[object, ...]] = []
    for t in times:
        if t < 60:
            temperature = 22.0 + 0.7 + rng.gauss(0.0, 0.02)
        elif t < 240:
            temperature = (
                22.0 + 8.0 * (1.0 - math.exp(-(t - 60.0) / 150.0)) + 0.7 + rng.gauss(0.0, 0.02)
            )
        else:
            temperature = 22.2 + 8.0 * math.exp(-(t - 240.0) / 180.0) + 0.7 + rng.gauss(0.0, 0.02)
        temperature = quantize(temperature, 0.01)
        raw = bmp280_temp_encode(temperature)
        rise = temperature - 22.0
        rows.append((t, t / 60.0, raw, temperature, rise))
    add_dataset(
        "greenhouse-single.example.csv",
        (
            "Receive time (s)",
            "Receive time (min)",
            "Signed BMP280 packet count",
            "Die temperature (°C)",
            "Baseline corrected rise (K)",
        ),
        rows,
        experiment="greenhouse-single.phyphox",
        sensor="TI SensorTag CC2650/CC1350 BMP280 die temperature",
        acquisition_path="SensorTag AA41 notification, AA44=0x64 (1 s)",
        nominal_rate_hz=1.0,
        duration_s=300.0,
        scenario="Lamp off for 60 s, on for 180 s, then off again; the die warms by about 8 K.",
        realism=[
            "BMP280 signed 24-bit temperature word with 0.01 °C scaling.",
            "Baseline 22 °C, +0.7 °C self-heating, and 0.02 °C noise.",
            "Receive time is used directly, not reconstructed from sample count.",
            "Die temperature is a device proxy, not isolated gas temperature.",
        ],
    )


# ---------------------------------------------------------------------------
# 14. Illuminance versus calibrated distance
# ---------------------------------------------------------------------------


def make_illuminance_distance() -> None:
    rng = random.Random(SEED + 114)
    distance_keys = (
        (0.0, 0.20),
        (4.0, 0.20),
        (4.5, 0.25),
        (8.0, 0.25),
        (8.5, 0.30),
        (12.0, 0.30),
        (12.5, 0.35),
        (16.0, 0.35),
        (16.5, 0.40),
        (20.0, 0.40),
        (20.5, 0.50),
        (24.0, 0.50),
        (24.5, 0.60),
        (28.0, 0.60),
        (28.5, 0.70),
        (32.0, 0.70),
        (32.5, 0.80),
        (36.0, 0.80),
        (36.5, 0.75),
        (40.0, 0.75),
        (40.5, 0.70),
        (44.0, 0.70),
        (44.5, 0.60),
        (48.0, 0.60),
        (48.5, 0.50),
        (52.0, 0.50),
        (52.5, 0.40),
        (56.0, 0.40),
        (56.5, 0.30),
        (60.0, 0.30),
    )
    origin = 0.15
    scale = 0.0002
    mouse_count = 1201
    mouse_t = sensor_clock(mouse_count, 0.05, rng)
    mouse_rows: list[tuple[object, ...]] = []
    previous = 0.0
    x = 0.0
    y = 0.0
    for t in mouse_t:
        distance = keyframe(t, distance_keys)
        target_counts = (distance - origin) / scale
        delta = target_counts - previous
        previous = target_counts
        dx = int(round(delta + rng.gauss(0.0, 0.4)))
        dy = int(round(rng.gauss(0.0, 0.2)))
        x += dx
        y += dy
        displacement = math.sqrt(x * x + y * y)
        mouse_rows.append((t, dx, dy, x, y, displacement))
    add_dataset(
        "illuminance-distance_mouse.example.csv",
        (
            "Mouse receive time (s)",
            "Mouse delta x (counts)",
            "Mouse delta y (counts)",
            "Integrated mouse x (counts)",
            "Integrated mouse y (counts)",
            "Radial mouse displacement (counts)",
        ),
        mouse_rows,
        experiment="illuminance-distance.phyphox",
        sensor="BLE HID boot mouse",
        acquisition_path="HID report characteristic 2A33, event-driven",
        nominal_rate_hz=20.0,
        duration_s=60.0,
        scenario="Carriage moves outward from 0.20 to 0.80 m and back in 0.05–0.10 m steps.",
        realism=[
            "0.0002 m per count and a 0.15 m reset-origin distance.",
            "Signed dx/dy reports integrated into x and y.",
            "Small tracking noise and a straight rail; no arbitrary 2-D path.",
            "Mouse and light clocks are independent.",
        ],
    )

    light_times = fixed_times(76, 0.8)
    light_rows: list[tuple[object, ...]] = []
    for t in light_times:
        distance = keyframe(t, distance_keys)
        lux = 2.0 + 100.0 / (distance * distance)
        lux *= 1.0 + rng.gauss(0.0, 0.01)
        raw = opt3001_encode(lux * 1.03)
        decoded = opt3001_decode(raw)
        corrected = max(0.0, decoded - 2.0)
        index = max(0, min(len(mouse_rows) - 1, int(t / 0.05)))
        displacement = mouse_rows[index][5]
        paired_distance = origin + scale * displacement
        inverse_square = 1.0 / paired_distance**2 if paired_distance > 0 else math.nan
        scaled = corrected * paired_distance**2
        log_distance = math.log(paired_distance) if paired_distance > 0 else math.nan
        log_light = math.log(corrected) if corrected > 0 else math.nan
        light_rows.append(
            (
                t,
                raw,
                decoded,
                corrected,
                displacement,
                paired_distance,
                inverse_square,
                scaled,
                log_distance,
                log_light,
            )
        )
    add_dataset(
        "illuminance-distance_light.example.csv",
        (
            "Light receive time (s)",
            "OPT3001 raw word (uint16)",
            "Decoded illuminance (lx)",
            "Background-corrected illuminance (lx)",
            "Previous mouse displacement at light time (counts)",
            "Calibrated source distance (m)",
            "Inverse square distance (1/m²)",
            "Corrected illuminance times distance squared (lx m²)",
            "ln(distance / m)",
            "ln(corrected illuminance / lx)",
        ),
        light_rows,
        experiment="illuminance-distance.phyphox",
        sensor="TI SensorTag CC2650 OPT3001",
        acquisition_path="SensorTag AA71 notification, AA73=0x50 (0.8 s)",
        nominal_rate_hz=1.25,
        duration_s=60.0,
        scenario="Lamp-off background 2 lx and a 1/r² illuminance sweep from 0.20 to 0.80 m.",
        realism=[
            "Exact OPT3001 exponent/mantissa encoding and 3% gain error.",
            "1% optical noise and a 2 lx background.",
            "At each light time the most recent previous mouse sample supplies the distance.",
            "Mouse and light receive clocks are separate.",
        ],
    )


# ---------------------------------------------------------------------------
# 15. Manual ruler distance with Nano light
# ---------------------------------------------------------------------------


def make_illuminance_distance_manual() -> None:
    rng = random.Random(SEED + 115)
    count = 1201
    device, receive = nano_clock(count, rng)
    distances = (0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.70, 0.60, 0.50, 0.40, 0.30, 0.20)
    raw_rows: list[tuple[object, ...]] = []
    for t, r in zip(device, receive):
        block = min(11, int(t // 5.0))
        distance = distances[block]
        clear = 10.0 + 100.0 / (distance * distance)
        c, rr, g, b = apds_counts(clear, clear * 0.55, clear * 0.62, clear * 0.38, rng)
        raw_rows.append((t, r, c, rr, g, b))
    add_dataset(
        "illuminance-distance-manual.example.csv",
        (
            "device_t (s)",
            "receive_t (s)",
            "clear (counts)",
            "red (counts)",
            "green (counts)",
            "blue (counts)",
        ),
        raw_rows,
        experiment="illuminance-distance-manual.phyphox",
        sensor="Arduino Nano 33 BLE Sense APDS-9960",
        acquisition_path="Nano mode 6 BLE notification, 20 Hz",
        nominal_rate_hz=20.0,
        duration_s=60.0,
        scenario="Six ruler positions from 0.20 to 0.70 m, with settles between moves.",
        realism=[
            "Raw APDS counts and both device and receive clocks.",
            "Clear signal follows 1/r² with a 10-count background.",
            "RGB counts track the same lamp spectrum.",
            "The paired observation table is a separate example file.",
        ],
    )

    observations: list[tuple[object, ...]] = []
    for index, distance in enumerate(distances):
        target_t = 2.5 + index * 5.0
        nearest = min(range(len(device)), key=lambda i: abs(device[i] - target_t))
        clear = raw_rows[nearest][2]
        corrected = max(0.0, clear - 10.0)
        inverse_square = 1.0 / distance**2
        scaled = corrected * distance**2
        observations.append(
            (
                distance,
                device[nearest],
                receive[nearest],
                clear,
                corrected,
                distance,
                inverse_square,
                scaled,
                math.log(distance),
                math.log(corrected) if corrected > 0 else math.nan,
            )
        )
    add_dataset(
        "illuminance-distance-manual_observations.example.csv",
        (
            "Entered ruler distance (m)",
            "Captured device time (s)",
            "Captured receive time (s)",
            "Captured clear signal (counts)",
            "Background-corrected signal (counts)",
            "Positive ruler distance (m)",
            "Inverse square distance (1/m²)",
            "Corrected signal times distance squared (count m²)",
            "ln(distance / m)",
            "ln(corrected signal / count)",
        ),
        observations,
        experiment="illuminance-distance-manual.phyphox",
        sensor="Arduino Nano 33 BLE Sense APDS-9960 and manual ruler",
        acquisition_path="Recorded snapshots from the 20 Hz light stream",
        nominal_rate_hz=None,
        duration_s=60.0,
        scenario="Twelve settled ruler observations, forward and back.",
        realism=[
            "Each row captures the latest light sample and its two timestamps.",
            "Background 10 counts and positive-distance gates are applied.",
            "The corrected signal times distance squared is nearly constant.",
            "No interpolation between manual positions is implied.",
        ],
    )


# ---------------------------------------------------------------------------
# 16. Magnetic current
# ---------------------------------------------------------------------------


def make_magnetic_current() -> None:
    rng = random.Random(SEED + 116)
    times = sensor_clock(601, 0.1, rng)
    currents = (0.0, 0.1, 0.2, 0.3, 0.4, 0.2, 0.0)
    rows: list[tuple[object, ...]] = []
    for t in times:
        index = min(len(currents) - 1, int(t // 8.0))
        current = currents[index]
        bz = 30.0 + 50.0 * current + rng.gauss(0.0, 0.35)
        bx = 2.0 + rng.gauss(0.0, 0.25)
        by = -1.0 + rng.gauss(0.0, 0.25)
        rows.append((t, bx, by, bz, 3, (bz - 30.0) * 0.4 / 20.0))
    add_dataset(
        "magnetic-current.example.csv",
        ("mag_t", "bx", "by", "bz", "mag_accuracy", "current"),
        rows,
        experiment="magnetic-current.phyphox",
        sensor="Phone magnetometer",
        acquisition_path="phyphox magnetic_field sensor, 10 Hz",
        nominal_rate_hz=10.0,
        duration_s=60.0,
        scenario="DC current steps 0, 0.1, 0.2, 0.3, 0.4, 0.2, and 0 A, each held for 8 s.",
        realism=[
            "Bz = 30 µT + 50 µT/A × current with 0.35 µT noise.",
            "Two-point calibration B1=30 µT at 0 A and B2=50 µT at 0.4 A.",
            "Accuracy code 3 is reported; DC plateaus only.",
            "Geometry and nearby magnetic background are assumed fixed.",
        ],
    )


# ---------------------------------------------------------------------------
# 17. Malus law
# ---------------------------------------------------------------------------


def make_malus_law() -> None:
    rng = random.Random(SEED + 117)
    count = 1201
    device, receive = nano_clock(count, rng)
    raw_rows: list[tuple[object, ...]] = []
    for t, r in zip(device, receive):
        angle = 10.0 * min(9, int(t // 6.0))
        clear = 10.0 + 1000.0 * math.cos(math.radians(angle)) ** 2
        c, rr, g, b = apds_counts(clear, clear * 0.55, clear * 0.62, clear * 0.38, rng)
        raw_rows.append((t, r, c, rr, g, b))
    add_dataset(
        "malus-law.example.csv",
        (
            "device_t (s)",
            "receive_t (s)",
            "clear (counts)",
            "red (counts)",
            "green (counts)",
            "blue (counts)",
        ),
        raw_rows,
        experiment="malus-law.phyphox",
        sensor="Arduino Nano 33 BLE Sense APDS-9960",
        acquisition_path="Nano mode 6 BLE notification, 20 Hz",
        nominal_rate_hz=20.0,
        duration_s=60.0,
        scenario="Analyzer angle stepped from 0° to 90° in 10° increments, with settles.",
        realism=[
            "Clear counts follow 10 + 1000 cos²(theta).",
            "APDS channel gains, noise, and 4100-count clipping.",
            "The angle is a manual protractor observation, not a gyro measurement.",
            "The paired observation table is a separate example file.",
        ],
    )

    observations: list[tuple[object, ...]] = []
    for index, angle in enumerate(range(0, 100, 10)):
        target_t = 5.0 + index * 6.0
        nearest = min(range(len(device)), key=lambda i: abs(device[i] - target_t))
        clear = raw_rows[nearest][2]
        prediction = math.cos(math.radians(angle)) ** 2
        normalized = (clear - 10.0) / (1010.0 - 10.0)
        observations.append(
            (
                angle,
                device[nearest],
                receive[nearest],
                clear,
                angle,
                prediction,
                normalized,
                normalized - prediction,
            )
        )
    add_dataset(
        "malus-law_observations.example.csv",
        (
            "Observed protractor angle (deg)",
            "Captured device time (s)",
            "Captured receive time (s)",
            "Captured clear signal (counts)",
            "Angle from parallel (deg)",
            "Cos-squared prediction (1)",
            "Normalized transmission (1)",
            "Measured minus cos-squared (1)",
        ),
        observations,
        experiment="malus-law.phyphox",
        sensor="Arduino Nano 33 BLE Sense APDS-9960 and manual protractor",
        acquisition_path="Recorded settled angle snapshots from the 20 Hz light stream",
        nominal_rate_hz=None,
        duration_s=60.0,
        scenario="Ten angle observations with an aligned parallel axis and a 10-count floor.",
        realism=[
            "Cos-squared prediction with an angle zero of 0°.",
            "Normalized transmission uses background 10 and parallel signal 1010 counts.",
            "Small residuals reflect count noise and angle settling.",
            "The table does not acquire the Nano gyroscope simultaneously.",
        ],
    )


# ---------------------------------------------------------------------------
# 18. Nano transit
# ---------------------------------------------------------------------------


def make_nano_transit() -> None:
    rng = random.Random(SEED + 118)
    count = 2401
    device, receive = nano_clock(count, rng)
    rows: list[tuple[object, ...]] = []
    for t, r in zip(device, receive):
        clear = 110.0
        for center in (20.0, 50.0, 80.0):
            depth = 0.040 * smooth_pulse(t, center - 2.0, 0.8, 2.4, 0.8)
            clear *= 1.0 - depth
        c, rr, g, b = apds_counts(clear, clear * 0.55, clear * 0.62, clear * 0.38, rng)
        normalized = (c - 10.0) / (110.0 - 10.0)
        rows.append((r, t, c, rr, g, b, normalized))
    add_dataset(
        "nano-transit.example.csv",
        ("receive_time", "device_time", "clear", "red", "green", "blue", "normalized"),
        rows,
        experiment="nano-transit.phyphox",
        sensor="Arduino Nano 33 BLE Sense APDS-9960",
        acquisition_path="Nano mode 6 BLE notification, 20 Hz",
        nominal_rate_hz=20.0,
        duration_s=120.0,
        scenario="Three 4% transits of 4 s duration at 20, 50, and 80 s.",
        realism=[
            "Clear/RGB counts with APDS gains, noise, and 4100-count clipping.",
            "Normalized light uses dark 10 and baseline 110 counts.",
            "A 4 s event spans about 80 samples at 20 Hz.",
            "Threshold timing and projected radius remain analysis results, not columns here.",
        ],
    )


# ---------------------------------------------------------------------------
# 19. PocketLab Voyager gyroscope
# ---------------------------------------------------------------------------


def make_pocketlab_gyroscope() -> None:
    rng = random.Random(SEED + 119)
    times = sensor_clock(3001, 0.02, rng)
    keys = {
        "x": ((0.0, 0.0), (10.0, 0.0), (20.0, 500.0), (30.0, -500.0), (40.0, 0.0), (60.0, 0.0)),
        "y": ((0.0, 0.0), (30.0, 0.0), (40.0, 250.0), (50.0, -250.0), (55.0, 0.0), (60.0, 0.0)),
        "z": ((0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (30.0, 0.0), (40.0, 0.0), (60.0, 0.0)),
    }
    bias = (0.01, -0.02, 0.015)
    scale = math.radians(2000.0 / 32768.0)
    rows: list[tuple[object, ...]] = []
    for t in times:
        true = tuple(keyframe(t, keys[axis]) + rng.gauss(0.0, 1.5) for axis in ("x", "y", "z"))
        raw = tuple(
            int(round(clamp(math.radians(true[i]) / scale, -32768, 32767))) for i in range(3)
        )
        corrected = tuple(raw[i] * scale - bias[i] for i in range(3))
        magnitude = math.sqrt(sum(value * value for value in corrected))
        rows.append((t, *raw, *corrected, magnitude))
    add_dataset(
        "pocketlab-gyroscope.example.csv",
        (
            "Receive time (s)",
            "Signed packet x (count)",
            "Signed packet y (count)",
            "Signed packet z (count)",
            "Bias corrected x (rad/s)",
            "Bias corrected y (rad/s)",
            "Bias corrected z (rad/s)",
            "Vector magnitude (rad/s)",
        ),
        rows,
        experiment="pocketlab-gyroscope.phyphox",
        sensor="PocketLab Voyager gyroscope",
        acquisition_path="Voyager AA15 notification, 50 Hz assumed",
        nominal_rate_hz=50.0,
        duration_s=60.0,
        scenario="Stationary, ±500 °/s yaw, +250/−250 °/s roll, then stationary.",
        realism=[
            "2000/32768 °/s per signed big-endian count.",
            "Gyro x at byte 8, y at byte 6, z at byte 10.",
            "Bias of 0.01, -0.02, 0.015 rad/s and 1.5 °/s rate noise.",
            "Receive time is a phone clock; no device timestamp is present.",
        ],
    )


# ---------------------------------------------------------------------------
# 20. Pressure-dependent boiling
# ---------------------------------------------------------------------------


def saturation_temperature_kpa(pressure_kpa: float) -> float:
    mm_hg = pressure_kpa / 0.133322
    return 1730.63 / (8.07131 - math.log10(mm_hg)) - 233.426


def make_pressure_boiling() -> None:
    rng = random.Random(SEED + 120)
    pressures = (
        101.3,
        90.0,
        80.0,
        70.0,
        60.0,
        50.0,
        45.0,
        40.0,
        35.0,
        30.0,
        25.0,
        20.0,
        15.0,
        10.0,
        5.0,
    )
    rows: list[tuple[object, ...]] = []
    for index, pressure in enumerate(pressures):
        if index % 3 == 0:
            code = 0
            temperature = saturation_temperature_kpa(pressure) - 5.0
        elif index % 3 == 1:
            code = 1
            temperature = saturation_temperature_kpa(pressure)
        else:
            code = 2
            temperature = saturation_temperature_kpa(pressure) - 1.0
        temperature += rng.gauss(0.0, 0.25)
        pressure += rng.gauss(0.0, 0.08)
        valid = 1
        kelvin = temperature + 273.15 if valid and pressure > 0 else math.nan
        pressure_valid = pressure if valid and pressure > 0 else math.nan
        boiling = pressure if valid and code == 1 and pressure > 0 else math.nan
        rows.append(
            (
                index + 1,
                pressure,
                temperature,
                code,
                valid,
                0.1,
                0.2,
                kelvin,
                pressure_valid,
                boiling,
            )
        )
    add_dataset(
        "pressure-boiling.example.csv",
        (
            "Observation ID",
            "Absolute pressure (kPa)",
            "Liquid temperature (degC)",
            "Observation code (0 liquid, 1 sustained boiling, 2 uncertain)",
            "Pair checked (1=yes)",
            "Pressure uncertainty (kPa)",
            "Temperature uncertainty (K)",
            "Checked liquid temperature (K)",
            "Checked absolute pressure (kPa)",
            "Observed sustained-boiling pressure (kPa)",
        ),
        rows,
        experiment="pressure-boiling.phyphox",
        sensor="Calibrated absolute-pressure instrument and liquid-temperature probe",
        acquisition_path="Manual paired observations",
        nominal_rate_hz=None,
        duration_s=None,
        scenario="Fifteen settled pressure/temperature pairs from 101.3 kPa down to 5 kPa, with liquid, boiling, and uncertain codes.",
        realism=[
            "Saturation temperatures follow the Antoine water curve.",
            "Pressure uncertainty 0.1 kPa and temperature uncertainty 0.2 K.",
            "Boiling code 1 is an operator judgement, not an automatic phase-boundary detection.",
            "The table is a classroom observation map, not a complete phase diagram.",
        ],
    )


# ---------------------------------------------------------------------------
# 21. Puck.js light
# ---------------------------------------------------------------------------


def make_puck_light() -> None:
    rng = random.Random(SEED + 121)
    times = sensor_clock(241, 0.25, rng)
    rows: list[tuple[object, ...]] = []
    for index, t in enumerate(times):
        if t < 10.0:
            light = 0.02
        elif t < 20.0:
            light = 0.90
        elif t < 40.0:
            light = 0.50
        elif t < 50.0:
            light = 0.90
        else:
            light = 0.02
        light = clamp(light + rng.gauss(0.0, 0.02), 0.0, 1.0)
        relative = (
            (light - 0.02) / (0.90 - 0.02)
            if t >= 20.0 and t < 40.0
            else (light - 0.02) / (0.90 - 0.02)
        )
        rows.append((t, 1000.0 + 0.25 * index, light, light, relative))
    add_dataset(
        "puck-light.example.csv",
        (
            "Receive time (s)",
            "Puck getTime clock (s)",
            "Raw relative light",
            "Domain checked relative light",
            "Dark corrected reference ratio",
        ),
        rows,
        experiment="puck-light.phyphox",
        sensor="Espruino Puck.js light sensor",
        acquisition_path="Puck.js Nordic UART notification, 4 Hz timer",
        nominal_rate_hz=4.0,
        duration_s=60.0,
        scenario="Dark, open reference, sample, open reference, dark intervals.",
        realism=[
            "Puck.light() is a relative 0..1 response, not lux.",
            "4 Hz sampling with independent device and receive clocks.",
            "0.02 noise and a 0.02 dark / 0.90 reference calibration.",
            "The ratio is gated by the reference validity in the experiment.",
        ],
    )


# ---------------------------------------------------------------------------
# 22. RGB filter transmission
# ---------------------------------------------------------------------------


def make_rgb_filter() -> None:
    rng = random.Random(SEED + 118 + 5)
    count = 1201
    device, receive = nano_clock(count, rng)
    reference = (1800.0, 900.0, 1050.0, 620.0)
    dark = (3.0, 2.0, 2.0, 1.0)
    targets = (
        (0.0, (10.0, 5.0, 6.0, 4.0)),
        (5.0, reference),
        (15.0, (1200.0, 780.0, 250.0, 100.0)),
        (25.0, (1100.0, 200.0, 820.0, 150.0)),
        (35.0, (900.0, 150.0, 220.0, 520.0)),
        (45.0, reference),
        (55.0, (10.0, 5.0, 6.0, 4.0)),
        (60.0, (10.0, 5.0, 6.0, 4.0)),
    )
    rows: list[tuple[object, ...]] = []
    for t, r in zip(device, receive):
        target = tuple(
            keyframe(t, [(time, value[channel]) for time, value in targets]) for channel in range(4)
        )
        c, rr, g, b = apds_counts(*target, rng)
        transmission = tuple(
            (value - dark[channel]) / (reference[channel] - dark[channel])
            if reference[channel] > dark[channel]
            else math.nan
            for channel, value in enumerate((c, rr, g, b))
        )
        rows.append((t, r, c, rr, g, b, *transmission))
    add_dataset(
        "rgb-filter-transmission.example.csv",
        (
            "device_t (s)",
            "receive_t (s)",
            "clear (counts)",
            "red (counts)",
            "green (counts)",
            "blue (counts)",
            "clear transmission (1)",
            "red transmission (1)",
            "green transmission (1)",
            "blue transmission (1)",
        ),
        rows,
        experiment="rgb-filter-transmission.phyphox",
        sensor="Arduino Nano 33 BLE Sense APDS-9960",
        acquisition_path="Nano mode 6 BLE notification, 20 Hz",
        nominal_rate_hz=20.0,
        duration_s=60.0,
        scenario="Dark, unfiltered reference, red, green, blue filters, reference, dark.",
        realism=[
            "Raw APDS counts with channel gains, noise, and 4100-count clipping.",
            "Transmission = (S−D)/(R−D) per channel with same-geometry references.",
            "Filter plateaus are not spectra and are not calibrated lux.",
            "The count ceiling is a screening bound, not a measured linearity limit.",
        ],
    )


# ---------------------------------------------------------------------------
# 23. Seasons and obliquity
# ---------------------------------------------------------------------------


def make_seasons() -> None:
    rng = random.Random(SEED + 122)
    count = 1201
    device, receive = nano_clock(count, rng)
    rows: list[tuple[object, ...]] = []
    labels: list[tuple[float, float, float, int]] = []
    for index in range(12):
        trial = index // 6 + 1
        obliquity = 0.0 if trial == 1 else 23.5
        orbit = 0.0 if index % 2 == 0 else 180.0
        latitude = (-60.0, 0.0, 60.0)[index % 3]
        labels.append((trial, latitude, orbit, obliquity))
    for index, (t, r) in enumerate(zip(device, receive)):
        block = min(11, int(t // 5.0))
        trial, latitude, orbit, obliquity = labels[block]
        incidence = math.radians(abs(latitude) + (0.0 if orbit == 0 else 20.0) + obliquity * 0.2)
        clear = 1100.0 * max(0.0, math.cos(incidence)) + 20.0
        c, rr, g, b = apds_counts(clear, clear * 0.55, clear * 0.62, clear * 0.38, rng)
        rows.append((r, t, c, rr, g, b))
    add_dataset(
        "seasons-obliquity.example.csv",
        ("receive_time", "device_time", "clear", "red", "green", "blue"),
        rows,
        experiment="seasons-obliquity.phyphox",
        sensor="Arduino Nano 33 BLE Sense APDS-9960",
        acquisition_path="Nano mode 6 BLE notification, 20 Hz",
        nominal_rate_hz=20.0,
        duration_s=60.0,
        scenario="Twelve 5 s plateaus: upright or tilted axis, two orbital positions, three latitudes.",
        realism=[
            "Clear counts follow a cosine-like illumination proxy.",
            "Raw RGBC counts include APDS gains, noise, and clipping.",
            "Labels are manual operator entries, not electronic geometry.",
            "The observation table is a separate example file.",
        ],
    )

    observation_rows: list[tuple[object, ...]] = []
    for index, (trial, latitude, orbit, obliquity) in enumerate(labels):
        target_t = 2.5 + index * 5.0
        nearest = min(range(len(device)), key=lambda i: abs(device[i] - target_t))
        _, _, clear, red, green, blue = rows[nearest]
        relative = (clear - 10.0) / (1100.0 - 10.0)
        observation_rows.append(
            (
                device[nearest],
                receive[nearest],
                clear,
                red,
                green,
                blue,
                trial,
                latitude,
                orbit,
                obliquity,
                100.0,
                1,
                10.0,
                1100.0,
                relative,
            )
        )
    add_dataset(
        "seasons-obliquity_observations.example.csv",
        (
            "row_device_time",
            "row_receive_time",
            "row_clear",
            "row_red",
            "row_green",
            "row_blue",
            "row_trial",
            "row_latitude",
            "row_orbit_position",
            "row_obliquity",
            "row_source_distance",
            "row_enabled",
            "row_dark",
            "row_baseline",
            "row_relative",
        ),
        observation_rows,
        experiment="seasons-obliquity.phyphox",
        sensor="Arduino Nano 33 BLE Sense APDS-9960 and manual labels",
        acquisition_path="Recorded observation rows from the 20 Hz light stream",
        nominal_rate_hz=None,
        duration_s=60.0,
        scenario="Twelve labeled observations covering trial, latitude, orbit position, and obliquity.",
        realism=[
            "Source distance is fixed at 100 cm for all rows.",
            "Dark 10 counts and baseline 1100 counts are stored per row.",
            "Relative response is a detector comparison, not a temperature ratio.",
            "Labels and positions are manual, not electronic measurements.",
        ],
    )


# ---------------------------------------------------------------------------
# 24. SensorTag environmental channels
# ---------------------------------------------------------------------------


def make_sensortag_environmental() -> None:
    rng = random.Random(SEED + 123)
    times = sensor_clock(48, 2.55, rng)
    humidity_rows: list[tuple[object, ...]] = []
    for t in times:
        temperature = 23.0 + 1.5 * smooth_pulse(t, 30.0, 10.0, 20.0, 20.0) + rng.gauss(0.0, 0.05)
        humidity = (
            45.0
            + 25.0 * smooth_pulse(t, 30.0, 10.0, 20.0, 20.0)
            - 5.0 * (1.0 - math.exp(-t / 60.0))
            + rng.gauss(0.0, 0.4)
        )
        temperature = clamp(temperature, -40.0, 125.0)
        humidity = clamp(humidity, 0.0, 100.0)
        hdc_raw = int(round((temperature + 40.0) * 65536.0 / 165.0))
        hum_raw = int(round(humidity * 65536.0 / 100.0)) | 3
        hum_pct = (hum_raw // 4) * 4 / 65536.0 * 100.0
        hdc_temp = hdc_raw / 65536.0 * 165.0 - 40.0
        humidity_rows.append((t, hum_pct, hdc_temp, hum_raw, hdc_raw))
    add_dataset(
        "sensortag-environmental_humidity.example.csv",
        (
            "Receive time (s)",
            "Relative humidity (%)",
            "HDC1000 temperature (°C)",
            "humidity_raw (packet count)",
            "hdc_temperature_raw (packet count)",
        ),
        humidity_rows,
        experiment="sensortag-environmental.phyphox",
        sensor="TI SensorTag CC2650 HDC1000",
        acquisition_path="SensorTag AA21 notification, AA23=0xFF (2.55 s)",
        nominal_rate_hz=0.392,
        duration_s=120.0,
        scenario="Slow warming and a humidity pulse from 30 to 80 s.",
        realism=[
            "HDC1000 conversions T = 165 raw/65536 − 40 and RH = 100 raw/65536.",
            "Low two humidity status bits set and masked.",
            "0.05 °C and 0.4 %RH noise; no condensation correction.",
            "Humidity and barometer notifications keep separate receive clocks.",
        ],
    )

    pressure_rows: list[tuple[object, ...]] = []
    for t in times:
        pressure = 1008.0 + 0.5 * math.sin(2.0 * math.pi * t / 120.0) + rng.gauss(0.0, 0.02)
        temperature = 24.0 + 0.6 * (1.0 - math.exp(-t / 60.0)) + rng.gauss(0.0, 0.02)
        pressure_raw = bmp280_pressure_encode(pressure)
        temp_raw = bmp280_temp_encode(temperature)
        pressure_rows.append(
            (t + 0.4, pressure_raw / 100.0, temp_raw / 100.0, pressure_raw, temp_raw)
        )
    add_dataset(
        "sensortag-environmental_barometer.example.csv",
        (
            "Receive time (s)",
            "Pressure (hPa)",
            "BMP280 die temperature (°C)",
            "pressure_raw (packet count)",
            "bmp_temperature_raw (packet count)",
        ),
        pressure_rows,
        experiment="sensortag-environmental.phyphox",
        sensor="TI SensorTag CC2650 BMP280",
        acquisition_path="SensorTag AA41 notification, AA44=0xFF (2.55 s)",
        nominal_rate_hz=0.392,
        duration_s=120.0,
        scenario="Near-ambient pressure and a slowly warming barometer die.",
        realism=[
            "Pressure and die temperature words are scaled by 0.01.",
            "0.02 hPa and 0.02 °C noise.",
            "Barometer receive times are offset from the humidity stream.",
            "No interpolation or common clock is implied.",
        ],
    )


# ---------------------------------------------------------------------------
# 25. Spectral fingerprints
# ---------------------------------------------------------------------------


def make_spectral_fingerprints() -> None:
    rng = random.Random(SEED + 124)
    rows: list[tuple[object, ...]] = []
    for index, wavelength in enumerate(range(400, 701, 15)):
        reference = 100.0 + 8.0 * math.sin(2.0 * math.pi * wavelength / 180.0)
        star = 80.0 + 5.0 * math.sin(2.0 * math.pi * wavelength / 220.0)
        sample = 64.0 + 4.0 * math.sin(2.0 * math.pi * wavelength / 260.0)
        for line, depth in ((589.0, 18.0), (656.0, 12.0)):
            if abs(wavelength - line) < 8.0:
                star -= depth
                sample -= depth * 0.5
        if abs(wavelength - 589.0) < 8.0:
            sample -= 10.0
        star += rng.gauss(0.0, 0.4)
        sample += rng.gauss(0.0, 0.4)
        reference += rng.gauss(0.0, 0.4)
        dark = 2.0
        ceiling = 200.0
        sample_transmission = (sample - dark) / (reference - dark)
        star_transmission = (star - dark) / (reference - dark)
        sample_depth = 1.0 - sample_transmission
        extra_depth = (
            1.0 - sample_transmission / star_transmission if star_transmission != 0 else math.nan
        )
        comparison = 589.0 if wavelength <= 622.0 else 656.0
        delta = wavelength - comparison
        rows.append(
            (
                index + 1,
                wavelength,
                comparison,
                sample,
                star,
                reference,
                dark,
                ceiling,
                1,
                0.2,
                sample_transmission,
                star_transmission,
                sample_depth,
                extra_depth,
                delta,
            )
        )
    add_dataset(
        "spectral-fingerprints.example.csv",
        (
            "Observation ID",
            "Calibrated wavelength (nm)",
            "Comparison line wavelength (nm)",
            "Sample intensity (a.u.)",
            "Star-only intensity (a.u.)",
            "Continuum reference intensity (a.u.)",
            "Dark intensity (a.u.)",
            "Unsaturated ceiling (a.u.)",
            "Same wavelength and intensity scale (1=yes)",
            "Wavelength uncertainty (nm)",
            "Sample over continuum reference",
            "Star over continuum reference",
            "Sample line depth",
            "Extra sample depth",
            "Offset from selected comparison line (nm)",
        ),
        rows,
        experiment="spectral-fingerprints.phyphox",
        sensor="Calibrated spectrometer or calibrated spectrum files",
        acquisition_path="Manual paired wavelength bins",
        nominal_rate_hz=None,
        duration_s=None,
        scenario="Twenty-one 15 nm bins from 400 to 700 nm with stellar and sample absorption features.",
        realism=[
            "All four intensities are in the same linear arbitrary units.",
            "Reference exceeds dark; sample and star remain below the 200-unit ceiling.",
            "A 589 nm comparison line is used below 622 nm and 656 nm above.",
            "Line depths are relative to the entered continuum, not a molecular retrieval.",
        ],
    )


# ---------------------------------------------------------------------------
# 26. Starspot crossing
# ---------------------------------------------------------------------------


def make_starspot() -> None:
    rng = random.Random(SEED + 125)
    count = 2401
    device, receive = nano_clock(count, rng)
    rows: list[tuple[object, ...]] = []
    for t, r in zip(device, receive):
        clear = 110.0
        if 20.0 <= t < 24.0:
            clear = 90.0
        elif 45.0 <= t < 49.0:
            clear = 95.0
        elif 50.0 <= t < 54.0:
            clear = 98.0
        elif 55.0 <= t < 59.0:
            clear = 95.0
        elif 80.0 <= t < 84.0:
            clear = 90.0
        c, rr, g, b = apds_counts(clear, clear * 0.55, clear * 0.62, clear * 0.38, rng)
        normalized = (c - 10.0) / (110.0 - 10.0)
        rows.append((r, t, c, rr, g, b, normalized))
    add_dataset(
        "starspot-crossing.example.csv",
        ("receive_time", "device_time", "clear", "red", "green", "blue", "normalized"),
        rows,
        experiment="starspot-crossing.phyphox",
        sensor="Arduino Nano 33 BLE Sense APDS-9960",
        acquisition_path="Nano mode 6 BLE notification, 20 Hz",
        nominal_rate_hz=20.0,
        duration_s=120.0,
        scenario="Normal transits at 20 and 80 s; an adjacent plateau at 45–49/55–59 s; a spot crossing at 50–54 s.",
        realism=[
            "Raw APDS counts with channel gains and noise.",
            "Normalized light uses dark 10 and patched baseline 110 counts.",
            "The spot crossing is an upward anomaly relative to the adjacent plateau.",
            "No spot radius, temperature, or unique stellar map is inferred.",
        ],
    )


# ---------------------------------------------------------------------------
# 27. Static friction
# ---------------------------------------------------------------------------


def make_static_friction() -> None:
    rng = random.Random(SEED + 126)
    times = sensor_clock(1501, 0.02, rng)
    angle_keys = ((0.0, 0.0), (5.0, 0.0), (20.0, 25.0), (30.0, 25.0))
    gravity_rows: list[tuple[object, ...]] = []
    linear_rows: list[tuple[object, ...]] = []
    for t in times:
        angle = keyframe(t, angle_keys)
        gx = 9.81 * math.sin(math.radians(angle)) + rng.gauss(0.0, 0.02)
        gy = rng.gauss(0.0, 0.02)
        gz = 9.81 * math.cos(math.radians(angle)) + rng.gauss(0.0, 0.02)
        measured_angle = math.degrees(math.atan2(math.hypot(gx, gy), abs(gz)))
        gnorm = math.sqrt(gx * gx + gy * gy + gz * gz)
        gravity_rows.append((gx, gy, gz, t, measured_angle, gnorm))
        if 20.0 <= t < 20.5:
            linear = 2.0 + rng.gauss(0.0, 0.1)
        elif 20.5 <= t < 24.0:
            linear = 0.8 + rng.gauss(0.0, 0.1)
        else:
            linear = 0.1 + rng.gauss(0.0, 0.1)
        linear_rows.append((abs(linear), t))
    add_dataset(
        "static-friction_gravity.example.csv",
        ("gx", "gy", "gz", "gravity_t", "angle", "gnorm"),
        gravity_rows,
        experiment="static-friction.phyphox",
        sensor="Phone accelerometer (gravity-sensitive)",
        acquisition_path="phyphox accelerometer sensor, 50 Hz",
        nominal_rate_hz=50.0,
        duration_s=30.0,
        scenario="Ramp held at 0° for 5 s, raised to 25° by 20 s, then held while slip begins.",
        realism=[
            "Gravity vector in phone coordinates with 0.02 m/s² noise.",
            "Inclination from atan2(hypot(gx,gy), abs(gz)).",
            "The mount is assumed parallel to the contact plane.",
            "The capture summary is analysis output, not a per-sample column here.",
        ],
    )
    add_dataset(
        "static-friction_linear.example.csv",
        ("lin_a", "lin_t"),
        linear_rows,
        experiment="static-friction.phyphox",
        sensor="Phone linear acceleration",
        acquisition_path="phyphox linear_acceleration sensor, 50 Hz",
        nominal_rate_hz=50.0,
        duration_s=30.0,
        scenario="Stationary noise, a 0.5 s 2 m/s² slip excursion at 20 s, then 0.8 m/s² motion.",
        realism=[
            "Absolute linear acceleration in m/s².",
            "Baseline noise about 0.1 m/s².",
            "The slip threshold is a detection setting, not a calibrated material constant.",
            "Gravity and linear acceleration retain separate clocks.",
        ],
    )


# ---------------------------------------------------------------------------
# 28. UV transmission
# ---------------------------------------------------------------------------


def make_uv_transmission() -> None:
    rng = random.Random(SEED + 127)
    count = 1201
    device, receive = nano_clock(count, rng)
    raw_rows: list[tuple[object, ...]] = []
    for t, r in zip(device, receive):
        if t < 5.0:
            a0 = 10.0
        elif t < 10.0:
            a0 = 610.0
        elif t < 15.0:
            a0 = 310.0
        elif t < 20.0:
            a0 = 250.0
        elif t < 25.0:
            a0 = 180.0
        elif t < 30.0:
            a0 = 310.0
        elif t < 35.0:
            a0 = 250.0
        elif t < 40.0:
            a0 = 310.0
        elif t < 45.0:
            a0 = 610.0
        else:
            a0 = 10.0
        a0 += rng.gauss(0.0, 1.5)
        a1 = rng.gauss(0.0, 1.0)
        a2 = rng.gauss(0.0, 1.0)
        raw_rows.append(
            (
                t,
                r,
                int(round(clamp(a0, 0, 1023))),
                int(round(clamp(a1, 0, 1023))),
                int(round(clamp(a2, 0, 1023))),
            )
        )
    add_dataset(
        "uv-transmission_raw.example.csv",
        ("Device time (s)", "Receive time (s)", "A0 (count)", "A1 (count)", "A2 (count)"),
        raw_rows,
        experiment="uv-transmission.phyphox",
        sensor="External UV detector on Nano A0",
        acquisition_path="Nano mode 9 BLE notification, 20 Hz",
        nominal_rate_hz=20.0,
        duration_s=60.0,
        scenario="Dark, unfiltered reference, UV sample, reference, dark.",
        realism=[
            "10-bit ADC counts 0–1023 with the default firmware resolution.",
            "A0 dark 10 counts, reference 610 counts, sample 310 counts.",
            "A1 and A2 carry only noise in this example.",
            "The APDS RGB sensor is not used as a UV detector.",
        ],
    )

    observation_rows: list[tuple[object, ...]] = []
    for index, sample in enumerate((310, 250, 180, 310, 250, 310)):
        reference = 610
        dark = 10
        gain = 3.3 / 1023.0
        offset = 0.0
        uv_gain = 0.01
        transmission = (sample - dark) / (reference - dark)
        sample_voltage = sample * gain + offset
        dark_voltage = dark * gain + offset
        irradiance = (sample_voltage - dark_voltage) * uv_gain
        target_t = 12.5 + index * 5.0
        nearest = min(range(len(device)), key=lambda i: abs(device[i] - target_t))
        observation_rows.append(
            (
                index + 1,
                reference,
                dark,
                1,
                gain,
                offset,
                1,
                uv_gain,
                1,
                sample,
                device[nearest],
                receive[nearest],
                transmission,
                sample_voltage,
                dark_voltage,
                irradiance,
            )
        )
    add_dataset(
        "uv-transmission_observations.example.csv",
        (
            "Observation ID",
            "Unfiltered reference (count)",
            "Covered detector dark (count)",
            "Paired linear readings checked (1=yes)",
            "Measured ADC voltage gain (V/count)",
            "Measured ADC voltage offset (V)",
            "ADC calibration checked (1=yes)",
            "Measured detector irradiance gain (W/m2/V)",
            "Irradiance calibration checked (1=yes)",
            "Captured A0 (count)",
            "Captured device time (s)",
            "Captured receive time (s)",
            "UV detector weighted transmission",
            "Calibrated sample voltage (V)",
            "Calibrated dark voltage (V)",
            "Calibrated detector-band irradiance (W/m2)",
        ),
        observation_rows,
        experiment="uv-transmission.phyphox",
        sensor="External UV detector on Nano A0",
        acquisition_path="Recorded observations from the 20 Hz analog stream",
        nominal_rate_hz=None,
        duration_s=60.0,
        scenario="Six observations with sample counts 310, 250, 180, 310, 250, 310.",
        realism=[
            "ADC gain 3.3 V / 1023 counts and zero offset.",
            "Detector irradiance gain 0.01 W/m²/V as an example calibration.",
            "Transmission is a detector-weighted band ratio, not a resolved UV spectrum.",
            "All voltage values stay inside the 0–3.3 V input range.",
        ],
    )


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def main() -> None:
    DATASETS.clear()
    make_audio_magnetic()
    make_cc2541_accelerometer()
    make_cc2541_gyroscope()
    make_cc2541_humidity()
    make_cc2541_ir_temperature()
    make_cc2541_magnetometer()
    make_cc2541_pressure()
    make_colour_temperature()
    make_coronagraph()
    make_detector_characterization()
    make_eclipsing_binary()
    make_exomoon()
    make_greenhouse_single()
    make_illuminance_distance()
    make_illuminance_distance_manual()
    make_magnetic_current()
    make_malus_law()
    make_nano_transit()
    make_pocketlab_gyroscope()
    make_pressure_boiling()
    make_puck_light()
    make_rgb_filter()
    make_seasons()
    make_sensortag_environmental()
    make_spectral_fingerprints()
    make_starspot()
    make_static_friction()
    make_uv_transmission()
    write_all()
    print(f"wrote {len(DATASETS)} draft datasets to {ROOT}")


if __name__ == "__main__":
    main()
