# Draft experiment example data

This directory contains example exports for the 28 draft experiments in
`experiments/drafts/`. The files use the drafts' export columns, sensor units,
acquisition rates, and dominant error sources. They are intended for software,
plotting, and teaching development alongside the draft XML.

There are **37 CSV files**: some drafts have two independent sensor streams or a
separate observation table. The drafts themselves remain development editions;
these files do not replace native-app, BLE, or apparatus checks.

## What is here

```text
drafts/
├── README.md
├── SENSORS.md                  sensor ranges, resolution, accuracy, rates
├── EXPERIMENTS.md              one entry per draft, with scenarios and files
├── manifest.json               machine-readable index and metadata
├── audio-magnetic_audio.example.csv
├── audio-magnetic_magnetic.example.csv
├── cc2541-accelerometer.example.csv
├── cc2541-gyroscope.example.csv
├── cc2541-humidity.example.csv
├── cc2541-ir-temperature.example.csv
├── cc2541-magnetometer.example.csv
├── cc2541-pressure.example.csv
├── colour-temperature.example.csv
├── coronagraph-contrast.example.csv
├── detector-characterization.example.csv
├── detector-characterization_summary.example.csv
├── eclipsing-binary.example.csv
├── exomoon-photometry.example.csv
├── greenhouse-single.example.csv
├── illuminance-distance_light.example.csv
├── illuminance-distance_mouse.example.csv
├── illuminance-distance-manual.example.csv
├── illuminance-distance-manual_observations.example.csv
├── magnetic-current.example.csv
├── malus-law.example.csv
├── malus-law_observations.example.csv
├── nano-transit.example.csv
├── pocketlab-gyroscope.example.csv
├── pressure-boiling.example.csv
├── puck-light.example.csv
├── rgb-filter-transmission.example.csv
├── seasons-obliquity.example.csv
├── seasons-obliquity_observations.example.csv
├── sensortag-environmental_barometer.example.csv
├── sensortag-environmental_humidity.example.csv
├── spectral-fingerprints.example.csv
├── starspot-crossing.example.csv
├── static-friction_gravity.example.csv
├── static-friction_linear.example.csv
├── uv-transmission_observations.example.csv
└── uv-transmission_raw.example.csv
```

## File conventions

- UTF-8 CSV, one header row, comma-separated, `.` as the decimal separator.
- Column names follow the draft export sets. Parentheses and Unicode units are
  part of the names.
- Files with two independent clocks are split rather than zipped by row number.
  Examples: audio and magnetic, light and mouse, humidity and barometer, gravity
  and linear acceleration.
- Raw packet words and raw ADC/RGBC counts are retained where the draft exports
  them. Derived columns use the draft formulas.
- Manual observation tables have no nominal acquisition rate.
- `nan` marks a value that is unavailable or outside the draft's validity domain.

## Quick index

| Draft | Files | Sensor / path | Rate |
| --- | --- | --- | --- |
| Audio and magnetic motor | `audio-magnetic_audio`, `_magnetic` | Phone mic + magnetometer | 48 kHz blocks / 20 Hz |
| CC2541 accelerometer | `cc2541-accelerometer` | KXTJ9 | 10 Hz |
| CC2541 gyroscope | `cc2541-gyroscope` | IMU-3000 | 10 Hz assumed |
| CC2541 humidity | `cc2541-humidity` | SHT21 | 1 Hz assumed |
| CC2541 IR temperature | `cc2541-ir-temperature` | TMP006 | 1 Hz assumed |
| CC2541 magnetometer | `cc2541-magnetometer` | MAG3110 | 10 Hz |
| CC2541 pressure | `cc2541-pressure` | T5400 | 1 Hz poll |
| Colour temperature | `colour-temperature` | APDS-9960 | 20 Hz |
| Coronagraph contrast | `coronagraph-contrast` | Camera ROI analysis | manual |
| Detector characterization | `detector-characterization`, `_summary` | APDS-9960 | 20 Hz |
| Eclipsing binary | `eclipsing-binary` | APDS-9960 | 20 Hz |
| Exomoon photometry | `exomoon-photometry` | APDS-9960 | 20 Hz |
| Single SensorTag warming | `greenhouse-single` | BMP280 | 1 s |
| Illuminance vs distance | `illuminance-distance_light`, `_mouse` | OPT3001 + HID mouse | 0.8 s + event |
| Manual ruler distance | `illuminance-distance-manual`, `_observations` | APDS-9960 + ruler | 20 Hz + manual |
| Magnetic current | `magnetic-current` | Phone magnetometer | 10 Hz |
| Malus' law | `malus-law`, `_observations` | APDS-9960 + protractor | 20 Hz + manual |
| Nano transit | `nano-transit` | APDS-9960 | 20 Hz |
| PocketLab gyroscope | `pocketlab-gyroscope` | Voyager gyro | 50 Hz assumed |
| Pressure-dependent boiling | `pressure-boiling` | Pressure + temperature instruments | manual |
| Puck.js light | `puck-light` | Puck.light | 4 Hz |
| RGB filter transmission | `rgb-filter-transmission` | APDS-9960 | 20 Hz |
| Seasons and obliquity | `seasons-obliquity`, `_observations` | APDS-9960 + labels | 20 Hz + manual |
| SensorTag environmental | `sensortag-environmental_humidity`, `_barometer` | HDC1000 + BMP280 | 2.55 s |
| Spectral fingerprints | `spectral-fingerprints` | Calibrated spectrometer | manual |
| Starspot crossing | `starspot-crossing` | APDS-9960 | 20 Hz |
| Static friction | `static-friction_gravity`, `_linear` | Phone accelerometer + linear | 50 Hz |
| UV transmission | `uv-transmission_raw`, `_observations` | External UV detector on A0 | 20 Hz + manual |

## Rebuild

```sh
python3 example-data/generate_draft_example_data.py
```

The build script writes all 37 CSV files and `manifest.json`. The generator uses
the existing example-data helpers and a fixed seed for each draft. Repeated runs
produce byte-identical files.

## Validate

```sh
python3 example-data/validate_draft_example_data.py
```

The validator checks manifest coverage, column and row counts, monotonic time
columns, raw count ranges, magnitude relations, packet conversions, and the main
derived-column formulas.

## Relationship to the draft collection

The readable companions and validation notes are in `docs/drafts/`. This
directory only supplies example CSV data. It does not change the draft XML, the
firmware, the protocol contract, or the original fifteen example datasets.

For the main collection, see `example-data/README.md`. For the draft sensor
reference, see `SENSORS.md`; for the per-draft scenarios, see `EXPERIMENTS.md`.
