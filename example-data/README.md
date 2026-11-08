# Example sensor data

This directory contains example CSV data for every experiment in the
repository: the seven Arduino Nano 33 BLE Sense experiments, the eight astronomy
activities, and the 28 draft experiments. Each file is an example export from
the named sensor, at the named acquisition rate, with the sensor's native units,
resolution, offsets, noise, drift, saturation, and timing limits.

The files are rebuilt by `generate_example_data.py` from fixed seeds. They are
useful for developing plotting and analysis code, testing import/export paths,
classroom dry runs, and visual comparisons.

## What is here

```text
example-data/
├── README.md                     this file
├── SENSORS.md                    sensor physics, ranges, resolution, accuracy, rates
├── EXPERIMENTS.md                experiment-by-experiment acquisition and scenarios
├── manifest.json                 machine-readable index and metadata
├── generate_example_data.py      main build script
├── generate_draft_example_data.py  draft build script
├── validate_example_data.py      main validator
├── validate_draft_example_data.py  draft validator
├── drafts/                        example data for the 28 draft experiments
├── core/
│   ├── accelerometer_plot_v1-2.example.csv
│   ├── analog_input_plot_v1-2.example.csv
│   ├── gyroscope_plot_v1-2.example.csv
│   ├── light_plot_v1-2.example.csv
│   ├── magnetometer_plot_v1-2.example.csv
│   ├── pressure_plot_v1-2.example.csv
│   └── temperature_plot_v1-2.example.csv
└── astronomy/
    ├── albedo_phone.example.csv
    ├── albedo_sensortag.example.csv
    ├── greenhouse.example.csv
    ├── ir-dist_habitable.example.csv
    ├── missiontomars_phone.example.csv
    ├── missiontomars_sensortag.example.csv
    ├── owon_digital_multimeter-debug.example.csv
    ├── pt-star.example.csv
    ├── tidal-locking_bmp280.example.csv
    ├── tidal-locking_opt3001.example.csv
    ├── tidal-locking_tmp007.example.csv
    ├── transitmethode_owon.example.csv
    ├── transitmethode_phone.example.csv
    └── transitmethode_sensortag.example.csv
```

`EXPERIMENTS.md` has the quick index with rates, durations, and scenarios.
`SENSORS.md` explains what each sensor measures and where its accuracy limits
come from. The draft collection has its own [README](drafts/README.md),
[SENSORS](drafts/SENSORS.md), and [EXPERIMENTS](drafts/EXPERIMENTS.md) guides.

## File conventions

- UTF-8, comma-separated, one header row, `.` as the decimal separator.
- One row per notification or reconstructed sample.
- `nan` marks a channel that had no fresh value. Only the magnetometer core file
  uses it, matching the 20 Hz magnetometer rate at a 20 Hz frame boundary.
- Core files contain both the wire-unit export and the display-unit export where
  the experiment provides both. For example, the accelerometer file has `g` and
  `m/s²` columns; the m/s² columns are the g columns times 9.81 (the historical factor;
  the current experiment uses 9.80665), not independent measurements.
- Astronomy files follow the experiment's primary measurement export set. Where
  a raw sensor word is important for checking a decoder, it is appended as an
  extra trailing column with `(a.u.)` in the name. The raw columns are not part
  of the phyphox export. Derived results tables, such as the transit `Timing`
  set, are not duplicated; they are produced by the experiment's analysis.
- The `.example.csv` suffix marks these files as example exports.

Column names use the experiment's export labels, including spaces, parentheses,
and Unicode units such as `µT`, `°C`, and `m/s²`. Quote them when using a shell
tool or a parser that does not handle spaces in headers.

## Index

### Core Arduino experiments

| File | Sensor | Nominal rate | Duration | Exported quantities |
| --- | --- | --- | --- | --- |
| `core/accelerometer_plot_v1-2.example.csv` | LSM9DS1 accelerometer | 20 Hz | 60 s | x/y/z and magnitude in g and m/s² |
| `core/gyroscope_plot_v1-2.example.csv` | LSM9DS1 gyroscope | 20 Hz | 60 s | x/y/z and magnitude in °/s and rad/s |
| `core/magnetometer_plot_v1-2.example.csv` | LSM9DS1 magnetometer | 20 Hz | 60 s | x/y/z and magnitude in µT |
| `core/pressure_plot_v1-2.example.csv` | LPS22HB | 20 Hz | 180 s | pressure in kPa and hPa |
| `core/temperature_plot_v1-2.example.csv` | HTS221 | 20 Hz | 180 s | temperature °C and relative humidity % |
| `core/light_plot_v1-2.example.csv` | APDS-9960 | 20 Hz | 60 s | clear/red/green/blue counts |
| `core/analog_input_plot_v1-2.example.csv` | nRF52840 SAADC | 20 Hz | 60 s | A0/A1/A2 counts and nominal mV |

### Astronomy activities

| File | Sensor / path | Nominal rate | Duration | Exported quantities |
| --- | --- | --- | --- | --- |
| `astronomy/albedo_sensortag.example.csv` | OPT3001 | 1.25 Hz | 60 s | time, relative light, raw word |
| `astronomy/albedo_phone.example.csv` | Phone light | 10 Hz | 60 s | time, relative light |
| `astronomy/greenhouse.example.csv` | BMP280 ×2 | 1 Hz | 600 s | time (min), two temperatures, raw words |
| `astronomy/ir-dist_habitable.example.csv` | TMP007 + HID mouse | 3.33 Hz | 30 s | time, mouse counts, IR and die temperature, raw words |
| `astronomy/missiontomars_sensortag.example.csv` | BMP280 | 10 Hz | 120 s | time, pressure, raw pressure/temperature words |
| `astronomy/missiontomars_phone.example.csv` | Phone barometer | 10 Hz | 120 s | time, pressure |
| `astronomy/owon_digital_multimeter-debug.example.csv` | Owon B35T | 2 Hz | 60 s | time, voltage, B35T raw fields |
| `astronomy/pt-star.example.csv` | BMP280 | 1 Hz | 180 s | time (min), pressure, temperature, raw words |
| `astronomy/tidal-locking_bmp280.example.csv` | BMP280 ×2 | 1 Hz | 300 s | time, two temperatures, raw words |
| `astronomy/tidal-locking_tmp007.example.csv` | TMP007 ×2 | 3.33 Hz | 300 s | time, four temperatures, raw words |
| `astronomy/tidal-locking_opt3001.example.csv` | OPT3001 ×2 | 1.25 Hz | 300 s | time, two illuminances, raw words |
| `astronomy/transitmethode_sensortag.example.csv` | OPT3001 | 1.25 Hz | 89.6 s | time, relative signal, raw word |
| `astronomy/transitmethode_phone.example.csv` | Phone light | 10 Hz | 90 s | time, relative signal |
| `astronomy/transitmethode_owon.example.csv` | Owon B35T + solar cell | 2 Hz | 90 s | time, voltage, B35T raw fields |

### Draft experiments

The 28 draft experiments have their own [index](drafts/README.md), [sensor
guide](drafts/SENSORS.md), and [experiment guide](drafts/EXPERIMENTS.md). The
draft collection adds 37 CSV files with independent sensor streams and manual
observation tables.

## Quick start

With Python and pandas:

```python
import pandas as pd

df = pd.read_csv("example-data/core/accelerometer_plot_v1-2.example.csv")
print(df.head())
print(df.describe())
```

Without pandas, the files are ordinary CSV:

```python
import csv

with open("example-data/core/temperature_plot_v1-2.example.csv", newline="") as handle:
    for row in csv.DictReader(handle):
        if float(row["relative Humidity (%)"]) > 60:
            print(row["Time t (s)"], row["relative Humidity (%)"])
```

To see the metadata for every file:

```sh
python3 -m json.tool example-data/manifest.json | less
```

## What the examples show

Each file includes the behaviour that makes the experiment interesting:

- Accelerometer: gravity, orientation, magnitude consistency, hand shake, tap
  ring-down, and the 20 Hz Nyquist limit.
- Gyroscope: zero-rate bias, the library-to-datasheet scale ratio of 0.87193,
  hand tremor, and the difference between signed rate and magnitude.
- Magnetometer: Earth field, rotation, hard/soft-iron distortion, a magnet
  approach, and a few missing samples.
- Pressure: barometric height change, a sealed-bag excursion, port lag, noise,
  and slow drift.
- Temperature/humidity: coupled vapour pressure and temperature, thermal lag,
  breath events, and board self-heating.
- Light/RGB: dark counts, colour gains, lamp ripple, relative units, and
  saturation at 4100 counts.
- Analog input: 10-bit quantisation, reference/gain errors, an RC curve, and
  50 Hz pickup aliased by 20 Hz sampling.
- Astronomy: reconstructed SensorTag time bases, BMP280 die-temperature
  self-heating, TMP007 field-of-view effects, OPT3001 exponent/mantissa
  encoding, Owon packet decoding, phone-sensor assumptions, and the different
  rates of the three SensorTag services.

`EXPERIMENTS.md` describes the scenario in each file. `SENSORS.md` explains the
sensor-side reasons.

## Rebuild

The build scripts use only the Python standard library and fixed seeds per
dataset:

```sh
python3 example-data/generate_example_data.py
python3 example-data/generate_draft_example_data.py
```

The main build writes 21 CSV files and `manifest.json`; the draft build writes
37 CSV files and `drafts/manifest.json`. Repeated runs are deterministic: the
same seeds, the same code, and the same output. If you change a scenario, update
the matching section in `EXPERIMENTS.md` or `drafts/EXPERIMENTS.md` and the
metadata in the matching build script.

The script is checked by the repository's Ruff configuration. From the
repository root:

```sh
ruff check example-data/generate_example_data.py example-data/generate_draft_example_data.py
ruff format --check example-data/generate_example_data.py example-data/generate_draft_example_data.py
```

The generators start with a local `# ruff: noqa: E501` because their manifest
strings are long descriptive sentences; the rest of the code follows the
repository style.

## Validation and internal consistency

The build scripts check that every row has the same number of cells as its header.
The main collection was also checked for:

- Monotonic nonnegative timestamps. Missing channels are marked `nan` only in
  the magnetometer file.
- Magnitude columns equal to the Euclidean norm of their components within the
  float32 representation.
- Pressure `hPa = kPa × 10` in the core pressure file.
- Analog counts in the 0–1023 range and `mV = counts × 3.226`.
- Light counts in the 0–4100 range, with the flashlight interval saturated.
- Raw OPT3001 words decode to the exported lux values.
- Raw TMP007 words decode to the exported temperatures with
  `floor(word/4) × 0.03125`.
- Raw BMP280 words decode to the exported pressure/temperature with `× 0.01`.
- B35T numeric/decimal/unit fields decode to the exported voltage.
- BMP280 pressure in `pt-star` stays inside the 300–1100 hPa rated range.
- Core magnetometer `NaN` rows are the only missing values.

These checks establish internal consistency across the main collection.

The draft collection has a separate validator:

```sh
python3 example-data/validate_draft_example_data.py
```

It covers the 37 draft files: manifest coverage, time ordering, raw count ranges,
magnitudes, packet conversions, and the principal derived columns. See
`drafts/README.md` for the draft index.

## Relationship to the static preview

The `demo/` directory has its own small deterministic preview data, designed
for the browser preview and not replaced by this collection. The example files
are larger, sensor-specific datasets intended for analysis and testing. If you
want to drive the preview from them, convert the relevant columns to the shape
expected by the preview code; do not edit the core experiment files to point at
CSV files.

## Provenance and licence

The example-data tooling and these CSV files are part of the repository's
tooling and documentation. The core experiment software is LGPL-3.0-or-later and the
astronomy collection is GPL-3.0; see the repository `README.md` and `LICENSE`
for the full terms. The example data are intended for development and teaching.
