# Draft experiment example data

This guide covers the 28 draft experiments in `experiments/drafts/`. Each entry
records the measured quantity, sensor and acquisition path, nominal rate,
accuracy limits, the example scenario, and the matching CSV files.

| Draft | Sensor / path | Rate | Files |
| --- | --- | --- | --- |
| Audio and magnetic motor | Phone microphone + magnetometer | 48 kHz blocks / 20 Hz | `audio-magnetic_audio.example.csv`, `audio-magnetic_magnetic.example.csv` |
| CC2541 accelerometer | KXTJ9 | 10 Hz | `cc2541-accelerometer.example.csv` |
| CC2541 gyroscope | IMU-3000 | 10 Hz assumed | `cc2541-gyroscope.example.csv` |
| CC2541 humidity | SHT21 | 1 Hz assumed | `cc2541-humidity.example.csv` |
| CC2541 IR temperature | TMP006 | 1 Hz assumed | `cc2541-ir-temperature.example.csv` |
| CC2541 magnetometer | MAG3110 | 10 Hz | `cc2541-magnetometer.example.csv` |
| CC2541 pressure | T5400 | 1 Hz poll | `cc2541-pressure.example.csv` |
| Colour temperature | APDS-9960 | 20 Hz | `colour-temperature.example.csv` |
| Coronagraph contrast | Camera + external ROI analysis | manual | `coronagraph-contrast.example.csv` |
| Detector characterization | APDS-9960 | 20 Hz | `detector-characterization.example.csv`, `_summary.example.csv` |
| Eclipsing binary | APDS-9960 | 20 Hz | `eclipsing-binary.example.csv` |
| Exomoon photometry | APDS-9960 | 20 Hz | `exomoon-photometry.example.csv` |
| Single SensorTag warming | BMP280 die temperature | 1 s | `greenhouse-single.example.csv` |
| Illuminance vs distance | OPT3001 + HID mouse | 0.8 s + event | `illuminance-distance_light.example.csv`, `_mouse.example.csv` |
| Manual ruler distance | APDS-9960 + ruler | 20 Hz + manual | `illuminance-distance-manual.example.csv`, `_observations.example.csv` |
| Magnetic current | Phone magnetometer | 10 Hz | `magnetic-current.example.csv` |
| Malus' law | APDS-9960 + protractor | 20 Hz + manual | `malus-law.example.csv`, `_observations.example.csv` |
| Nano transit | APDS-9960 | 20 Hz | `nano-transit.example.csv` |
| PocketLab gyroscope | Voyager gyroscope | 50 Hz assumed | `pocketlab-gyroscope.example.csv` |
| Pressure-dependent boiling | Pressure and temperature instruments | manual | `pressure-boiling.example.csv` |
| Puck.js light | Puck.light | 4 Hz | `puck-light.example.csv` |
| RGB filter transmission | APDS-9960 | 20 Hz | `rgb-filter-transmission.example.csv` |
| Seasons and obliquity | APDS-9960 + labels | 20 Hz + manual | `seasons-obliquity.example.csv`, `_observations.example.csv` |
| SensorTag environmental | HDC1000 + BMP280 | 2.55 s each | `sensortag-environmental_humidity.example.csv`, `_barometer.example.csv` |
| Spectral fingerprints | Calibrated spectrometer | manual | `spectral-fingerprints.example.csv` |
| Starspot crossing | APDS-9960 | 20 Hz | `starspot-crossing.example.csv` |
| Static friction | Phone accelerometer + linear acceleration | 50 Hz | `static-friction_gravity.example.csv`, `_linear.example.csv` |
| UV transmission | External detector on A0 | 20 Hz + manual | `uv-transmission_raw.example.csv`, `_observations.example.csv` |

## 1. Audio and magnetic motor comparison

**Measurand.** Slow motor-off and motor-on plateaus in microphone RMS and phone
magnetic field. The audio and magnetic records have separate clocks.

**Acquisition.** Phone microphone at 48 kHz, analysed in 0.1 s blocks; phone
magnetometer at 20 Hz. The audio table has 601 blocks over 60 s; the magnetic
table has 1201 samples.

**Accuracy.** Audio is a relative digital amplitude affected by microphone gain
and AGC; it is not A-weighted or certified SPL. The magnetometer is a
model-dependent phone sensor with an accuracy code. The motor field is a few µT
and the Earth field is about 48 µT.

**Example scenario.** Three 10 s motor-on intervals at 10–20, 30–40, and 50–60 s.
Motor-off RMS is about 0.012; motor-on RMS is about 0.045.

**Files.** `audio-magnetic_audio.example.csv`,
`audio-magnetic_magnetic.example.csv`.

## 2. CC2541 accelerometer

**Measurand.** Three signed acceleration components and their magnitude.

**Acquisition.** KXTJ9 at ±2 g, 8-bit, 64 counts/g; AA13 = 0x0A requests 100 ms.
The example has 601 samples over 60 s.

**Accuracy.** The 8-bit step is 0.153 m/s². Zero-g offset, axis orientation, and
mounting dominate. A raw −128 count must remain negative. The example uses bias
0.20, −0.25, 0.35 m/s² and 0.02 m/s² noise.

**Example scenario.** Flat, ±20° tilts, a short shake, a 60° roll, and a return
to flat.

**File.** `cc2541-accelerometer.example.csv`.

## 3. CC2541 gyroscope

**Measurand.** Three signed angular-rate components and the magnitude in rad/s.

**Acquisition.** IMU-3000; 500/65536 °/s per count; 100 ms assumed period. The
example has 601 samples over 60 s.

**Accuracy.** Zero-rate bias, scale error, and the legacy packet scale dominate.
The example uses a small bias in rad/s and 0.8 °/s noise.

**Example scenario.** Stationary, ±125 °/s yaw, ±200 °/s roll/pitch, then
stationary again.

**File.** `cc2541-gyroscope.example.csv`.

## 4. CC2541 humidity

**Measurand.** SHT21 temperature and relative humidity, with both raw words.

**Acquisition.** AA21 notification; 1 s assumed period. The example has 61 rows.

**Accuracy.** SHT21 equations are `T = 175.72 ST/65536 − 46.85 °C` and
`RH = 125 SRH/65536 − 6 %`. The low two status bits are masked. Outside 0–100 %
the checked humidity is `nan`; the unbounded value remains exported.

**Example scenario.** Slow warming with a short humidity breath event near 30 s.

**File.** `cc2541-humidity.example.csv`.

## 5. CC2541 IR temperature

**Measurand.** TMP006 thermopile voltage, die temperature, and the application
model object temperature.

**Acquisition.** AA01 notification; 1 s assumed period. The example has 61 rows.

**Accuracy.** Voltage is 156.25 nV/count; die is 1/128 °C per count. Object
temperature depends on the application coefficients, target emissivity, field of
view, and reflected background. The example uses example calibration values and
a target sequence near 23, 35, 45, and 30 °C.

**File.** `cc2541-ir-temperature.example.csv`.

## 6. CC2541 magnetometer

**Measurand.** Signed MAG3110 components and magnitude in µT.

**Acquisition.** AA31 notification; AA33 = 0x0A requests 100 ms. The example has
601 rows.

**Accuracy.** Nominal 0.1 µT/count; the scale-verified gate is assumed enabled.
Bias is 5, −3, 8 µT; noise is 0.12 µT. Hard/soft iron and nearby fields dominate.

**Example scenario.** Earth-field baseline, 80° yaw, 20° tilt, a magnet approach
near 43 s, then return.

**File.** `cc2541-magnetometer.example.csv`.

## 7. CC2541 pressure

**Measurand.** T5400 pressure and temperature from raw UT/UP words.

**Acquisition.** AA41 poll at 1 Hz. The example has 61 rows.

**Accuracy.** The manufacturer polynomial with the draft fixture coefficients is
used. Calibration is assumed loaded and verified. The receive time is the
data-read arrival time. Pressure is 1008–1028 hPa over a +20 hPa excursion.

**File.** `cc2541-pressure.example.csv`.

## 8. Colour temperature

**Measurand.** APDS-9960 RGBC counts, corrected channel ratios, chromaticity, and
an indicative McCamy CCT.

**Acquisition.** Nano mode 6 at 20 Hz; 1201 rows over 60 s.

**Accuracy.** Broad-band RGBC is not a spectrometer. The donor XYZ matrix and
McCamy polynomial are provisional. The accepted CCT is gated to 2000–10000 K and
to positive XYZ. The example CCT range is about 2470–6390 K.

**Example scenario.** Warm 2700 K, neutral 4000 K, cool 6500 K, and warm again.

**File.** `colour-temperature.example.csv`.

## 9. Coronagraph contrast

**Measurand.** Target ROI mean, local background, contrast, net rate, and
noise-normalized signal from separate images.

**Acquisition.** Manual external image analysis; no camera pipeline. Two repeats
at six separations and two mask states (24 rows).

**Accuracy.** Fixed exposure, linear unsaturated data, matched ROI areas, and
independent uncertainty estimates are required. The example uses a 255-unit
ceiling and 10 ms exposure. Contrast is local, not a planet/star flux ratio.

**File.** `coronagraph-contrast.example.csv`.

## 10. Detector characterization

**Measurand.** Raw APDS counts, delivered interval statistics, baseline noise,
expected single-sample SNR, and samples per feature.

**Acquisition.** Nano mode 6 at 20 Hz; 1201 raw rows plus one summary row.

**Accuracy.** The delivered rate is not the sensor-chip bandwidth. The example
baseline is about 1023 counts with 10.6 counts sample SD; a 2 % drop gives SNR
about 1.9. These are planning quantities, not detections.

**Example scenario.** Dark, stable baseline, then 1 %, 2 %, 4 %, and 8 % features.

**Files.** `detector-characterization.example.csv`,
`detector-characterization_summary.example.csv`.

## 11. Eclipsing binary

**Measurand.** Clear light curve, normalized flux, primary and secondary eclipse
depths, and phase.

**Acquisition.** Nano mode 6 at 20 Hz; 2401 rows over 120 s.

**Accuracy.** Counts are relative. The example uses dark 10 and baseline 210
counts; primary depth 30 %, secondary 10 %; period 30 s and epoch 20 s.

**File.** `eclipsing-binary.example.csv`.

## 12. Exomoon photometry

**Measurand.** Clear light curve and normalized flux through planet-only,
separated-moon, and overlapping-moon intervals.

**Acquisition.** Nano mode 6 at 20 Hz; 2401 rows over 120 s.

**Accuracy.** The intended ordering is baseline ≥ planet-only ≥ overlap ≥
separated ≥ dark. The example uses 110, 100, 99, 97, and 10 counts. Extra depth
and overlap brightening are analysis results computed from window means.

**File.** `exomoon-photometry.example.csv`.

## 13. Single SensorTag warming

**Measurand.** BMP280 die temperature and baseline-corrected rise.

**Acquisition.** CC2650/CC1350 AA41 notification; AA44 = 0x64 requests 1 s. The
example has 301 rows over 300 s.

**Accuracy.** Signed 24-bit word scaled by 0.01 °C. The die includes self-heating
and mounting conduction. The example starts at 22 °C, adds +0.7 °C self-heating,
and warms by about 8 K under the lamp.

**File.** `greenhouse-single.example.csv`.

## 14. Illuminance versus calibrated distance

**Measurand.** OPT3001 illuminance and BLE HID mouse rail position, paired by the
most recent previous mouse sample.

**Acquisition.** OPT3001 at 0.8 s (76 rows); mouse at 20 Hz (1201 rows). The two
receive clocks are independent.

**Accuracy.** OPT3001 is about ±10 % typical with 0.01 lx resolution at the lowest
range. The mouse scale is about 0.0002 m/count and the origin is 0.15 m. The
example uses a 2 lx background and 1/r² illumination from 0.20 to 0.80 m.

**Files.** `illuminance-distance_light.example.csv`,
`illuminance-distance_mouse.example.csv`.

## 15. Relative light versus manual ruler distance

**Measurand.** Nano clear counts at entered ruler positions, with a paired
observation table.

**Acquisition.** Nano mode 6 at 20 Hz (1201 raw rows); twelve recorded manual
observations. The raw table and observation table are separate.

**Accuracy.** Counts are relative, not lux. Background is 10 counts and the
example uses 1/r² illumination from 0.20 to 0.70 m. The corrected signal times
distance squared is about 100 count m².

**Files.** `illuminance-distance-manual.example.csv`,
`illuminance-distance-manual_observations.example.csv`.

## 16. Magnetic current

**Measurand.** Phone z-axis magnetic field and a two-point affine current
estimate.

**Acquisition.** Phone magnetometer at 10 Hz; 601 rows over 60 s.

**Accuracy.** Bz = 30 µT + 50 µT/A × current; 0.35 µT noise. The calibration is
B1 = 30 µT at 0 A and B2 = 50 µT at 0.4 A. The example is a settled DC record,
not an AC clamp meter.

**File.** `magnetic-current.example.csv`.

## 17. Malus' law

**Measurand.** Nano clear counts at settled protractor angles, normalized
transmission, cos² prediction, and residual.

**Acquisition.** Nano mode 6 at 20 Hz (1201 raw rows); ten angle observations.

**Accuracy.** Background 10 counts, parallel signal 1010 counts, angle zero 0°.
The example steps 0–90° in 10° increments. The detector is fixed; the angle is a
manual observation, not a gyro measurement.

**Files.** `malus-law.example.csv`, `malus-law_observations.example.csv`.

## 18. Nano transit

**Measurand.** Clear light curve and normalized flux for three model transits.

**Acquisition.** Nano mode 6 at 20 Hz; 2401 rows over 120 s.

**Accuracy.** Dark 10, baseline 110, transit plateau 106 counts; 4 % depth. The
example transits are 4 s long at 20, 50, and 80 s. Threshold timing and projected
radius are analysis outputs, not columns here.

**File.** `nano-transit.example.csv`.

## 19. PocketLab Voyager gyroscope

**Measurand.** Signed Voyager gyro counts, bias-corrected rad/s, and magnitude.

**Acquisition.** AA15 notification; 50 Hz assumed. The example has 3001 rows.

**Accuracy.** 2000/32768 °/s per count; x at byte 8, y at byte 6, z at byte 10.
The example uses a small bias and 1.5 °/s noise. This is a Voyager adapter, not a
PocketLab One compatibility claim.

**File.** `pocketlab-gyroscope.example.csv`.

## 20. Pressure-dependent boiling

**Measurand.** Paired absolute pressure and liquid temperature with an observed
boiling code.

**Acquisition.** Manual observations; 15 rows from 101.3 kPa down to 5 kPa.

**Accuracy.** The example uses 0.1 kPa and 0.2 K uncertainties and the Antoine
water curve. Code 1 is sustained boiling; code 0 is sub-boiling liquid; code 2 is
uncertain. The table is an observation map, not a phase-boundary fit.

**File.** `pressure-boiling.example.csv`.

## 21. Puck.js light

**Measurand.** Relative light, device clock, receive clock, and dark/reference
ratio.

**Acquisition.** Puck.js Nordic UART; 4 Hz timer; 241 rows over 60 s.

**Accuracy.** `Puck.light()` is 0–1, uncalibrated and spectrum dependent. The
example uses dark 0.02, reference 0.90, and 0.02 noise. The ratio is gated by
reference validity.

**File.** `puck-light.example.csv`.

## 22. RGB filter transmission

**Measurand.** Raw RGBC counts and per-channel transmission through coloured
filters.

**Acquisition.** Nano mode 6 at 20 Hz; 1201 rows over 60 s.

**Accuracy.** Transmission is `(S−D)/(R−D)` with same-geometry dark and
unfiltered references. The example uses reference clear 1800, red 900, green
1050, blue 620; the filters are passive and mostly below the reference. Counts
are not spectra or lux.

**File.** `rgb-filter-transmission.example.csv`.

## 23. Seasons and obliquity

**Measurand.** Nano clear/RGB counts and a labeled observation table for trial,
latitude, orbit position, and obliquity.

**Acquisition.** Nano mode 6 at 20 Hz (1201 raw rows); twelve recorded
observations. The labels are manual.

**Accuracy.** The example uses dark 10 and baseline 1100 counts; relative
response is `(row_clear−dark)/(baseline−dark)`. It is a detector-illumination
proxy, not a temperature or a climate model.

**Files.** `seasons-obliquity.example.csv`,
`seasons-obliquity_observations.example.csv`.

## 24. SensorTag environmental channels

**Measurand.** HDC1000 humidity/temperature and BMP280 pressure/die temperature on
one CC2650/CC1350 tag.

**Acquisition.** Both services request 2.55 s. Humidity and barometer tables have
48 rows each, with independent receive times (the barometer is offset by 0.4 s).

**Accuracy.** HDC1000: `T = 165 raw/65536 − 40 °C`, `RH = 100 raw/65536`;
±0.2 °C and ±3 %RH typical. BMP280 words are scaled by 0.01. The two clocks are
not interchangeable.

**Files.** `sensortag-environmental_humidity.example.csv`,
`sensortag-environmental_barometer.example.csv`.

## 25. Spectral fingerprints

**Measurand.** Paired calibrated wavelength bins, sample/star/reference/dark
intensities, normalized transmission, and line depth.

**Acquisition.** Manual calibrated spectra; 21 bins from 400 to 700 nm.

**Accuracy.** All intensities share a linear arbitrary unit; dark 2, ceiling 200,
wavelength uncertainty 0.2 nm. The example includes stellar and sample features
near 589 and 656 nm. It does not identify molecules automatically.

**File.** `spectral-fingerprints.example.csv`.

## 26. Starspot crossing

**Measurand.** Clear light curve and normalized flux for normal transits and a
crossing over a dark source patch.

**Acquisition.** Nano mode 6 at 20 Hz; 2401 rows over 120 s.

**Accuracy.** Dark 10, patched baseline 110, adjacent plateau 95, crossing 98
counts. The local upward contrast is computed from those window means; it is a
relative detector contrast, not a spot temperature or radius.

**File.** `starspot-crossing.example.csv`.

## 27. Static friction

**Measurand.** Gravity vector, inclination angle, linear acceleration, and the
first sustained slip.

**Acquisition.** Phone accelerometer and linear acceleration at 50 Hz; 1501 rows
each over 30 s. The streams keep separate timestamps.

**Accuracy.** The example uses 0.02 m/s² gravity noise and 0.1 m/s² linear
baseline. The ramp rises to 25°; the linear stream has a 0.5 s 2 m/s² slip
excursion at 20 s. The capture summary is analysis output.

**Files.** `static-friction_gravity.example.csv`,
`static-friction_linear.example.csv`.

## 28. UV transmission

**Measurand.** External UV detector A0 counts, sample/reference/dark
transmission, calibrated voltage, and optional irradiance.

**Acquisition.** Nano mode 9 at 20 Hz (1201 raw rows); six recorded observations.

**Accuracy.** ADC counts 0–1023; gain 3.3 V/1023 V per count; dark 10; reference
610; samples 310, 250, 180, 310, 250, 310. Transmission is a detector-weighted
band ratio, not a resolved UV spectrum. Absolute irradiance assumes a measured
detector gain of 0.01 W/m²/V.

**Files.** `uv-transmission_raw.example.csv`,
`uv-transmission_observations.example.csv`.

## Reading notes

1. The draft XML files are development editions. These example files let you
   exercise their columns and arithmetic without claiming native-app, BLE, or
   apparatus validation.
2. Files with two clocks keep those clocks separate. Do not subtract one clock
   from the other or zip two tables by row number.
3. Raw packets, raw counts, and calibrated values are retained where the draft
   exports them. Manual tables contain entered values and their derived columns.
4. The example scenarios are chosen to show the intended ordering and domain
   checks, not to represent a particular classroom run.
