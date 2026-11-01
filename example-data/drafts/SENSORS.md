# Draft sensors and acquisition limits

This note records the physical quantity, range, resolution, typical accuracy,
acquisition rate, and modelled behaviour for the sensors used by the 28 draft
experiments. The numbers are component-level specifications and the draft
manuscripts' stated assumptions. They describe the sensor, not a particular
board, phone, or room.

## At a glance

| Sensor | Draft use | Quantity | Range | Resolution | Typical accuracy | Rate in the examples |
| --- | --- | --- | --- | --- | --- | --- |
| APDS-9960 | Nano optics and photometry | clear/red/green/blue counts | 16-bit, 4100-count nominal saturation | 1 count | relative only | 20 Hz |
| OPT3001 | illuminance-distance | illuminance | 0.01–83 865.6 lx | 0.01 lx at lowest range | ±10 % typical | 0.8 s |
| BLE HID mouse | illuminance-distance | displacement | counts | 1 count | scale and slip unknown | event driven |
| BMP280 | greenhouse-single, sensortag-environmental | pressure, die temperature | 300–1100 hPa | 0.01 hPa, 0.01 °C | ±1 hPa, ±0.5–1 °C die | 1 s or 2.55 s |
| HDC1000 | sensortag-environmental | temperature, relative humidity | −20–85 °C, 0–100 %RH | 14-bit | ±0.2 °C, ±3 %RH | 2.55 s |
| KXTJ9 | cc2541-accelerometer | acceleration | ±2 g, 8-bit | 64 counts/g | offset and scale dominate | 10 Hz |
| IMU-3000 | cc2541-gyroscope | angular rate | 500 °/s total span | 500/65536 °/s | zero-rate bias and scale error | 10 Hz assumed |
| MAG3110 | cc2541-magnetometer | magnetic field | ±1000 µT | 0.1 µT | offset, hard/soft iron | 10 Hz |
| SHT21 | cc2541-humidity | temperature, relative humidity | −40–125 °C, 0–100 %RH | 0.01 °C, 0.04 %RH | ±0.3 °C, ±2 %RH | 1 Hz assumed |
| T5400 | cc2541-pressure | absolute pressure, temperature | 300–1100 hPa | polynomial words | about ±1 hPa after calibration | 1 Hz poll |
| TMP006 | cc2541-ir-temperature | thermopile voltage, die temperature | object model dependent | 156.25 nV, 1/128 °C | ±1 °C with application calibration | 1 Hz assumed |
| PocketLab Voyager | pocketlab-gyroscope | angular rate | ±2000 °/s | 2000/32768 °/s | zero-rate bias, scale error | 50 Hz assumed |
| Puck.js light | puck-light | relative light | 0–1 | device-dependent | uncalibrated | 4 Hz |
| Phone microphone | audio-magnetic | relative audio amplitude | device-dependent | device-dependent | gain/AGC dependent | 48 kHz, 0.1 s blocks |
| Phone magnetometer | audio-magnetic, magnetic-current | magnetic field | device-dependent | device-dependent | offset and accuracy code | 10–20 Hz |
| Phone accelerometer | static-friction | gravity vector | device-dependent | device-dependent | mounting and fusion latency | 50 Hz |
| Phone linear acceleration | static-friction | linear acceleration | device-dependent | device-dependent | mounting and fusion latency | 50 Hz |
| External UV detector | uv-transmission | conditioned voltage on A0 | 0–3.3 V | 10-bit ADC | detector/calibration dependent | 20 Hz |
| Calibrated spectrometer | spectral-fingerprints | wavelength and intensity | instrument dependent | 0.2 nm assumed | instrument dependent | manual |
| Fixed-exposure camera | coronagraph-contrast | ROI means | 0–255 example units | 1 unit | linearity and ROI noise | manual |
| Pressure/temperature instruments | pressure-boiling | absolute pressure, liquid temperature | apparatus dependent | 0.1 kPa, 0.2 K assumed | calibration dependent | manual |

## APDS-9960

The APDS-9960 provides clear, red, green, and blue detector counts. The pinned
firmware uses four integration cycles, about 11.12 ms, and a gain setting whose
register value is 16×. The nominal saturation is 4100 counts, not the 16-bit
register maximum. The draft examples use channel gains of 1.02, 1.05, 0.97, and
0.92 for clear, red, green, and blue; dark counts of 3, 2, 2, and 1; and count
noise that grows with the signal. Counts are relative, not lux or a resolved
spectrum.

Most Nano drafts use a 20 Hz notification stream. Device time and phone receive
time are separate clocks. The APDS integration time is short compared with the
50 ms notification interval, but the delivered rate can vary with BLE scheduling.

## OPT3001

The OPT3001 is a photopic illuminance sensor with automatic range selection. It
covers 0.01–83 865.6 lx with 0.01 lx resolution at the lowest range and about
±10 % typical accuracy. The SensorTag service is configured for 0.8 s in
`illuminance-distance`. The example data use exact exponent/mantissa words and a
3 % gain error. A BLE HID mouse supplies a separate displacement stream; it is
not clock-synchronised with the light sensor.

## BMP280 and HDC1000 in the SensorTag

The CC2650/CC1350 BMP280 provides absolute pressure and a die temperature. The
draft adapters scale the pressure and die-temperature words by 0.01. The BMP280
die is affected by PCB temperature and self-heating and is not an air
thermometer.

The HDC1000 provides temperature and relative humidity. Its conversions in the
draft XML are `T = 165 raw/65536 − 40 °C` and `RH = 100 raw/65536`. The two low
humidity status bits are masked. The requested period is 2.55 s for both the
HDC1000 and BMP280 services in `sensortag-environmental`; the two notification
families keep separate receive times.

## CC2541 KXTJ9 accelerometer

The KXTJ9 is configured for ±2 g and an 8-bit output. The draft uses 64 counts
per g. A signed count of −64 is −9.80665 m/s² before bias subtraction; −128 must
remain negative. The requested period is 100 ms, or 10 Hz. Zero-g offset, axis
orientation, and the low 8-bit resolution dominate the uncertainty. The example
data use a bias of 0.20, −0.25, 0.35 m/s² and add no noise.

## CC2541 IMU-3000 gyroscope

The IMU-3000 draft uses the legacy 500/65536 °/s per count scale, a 500 °/s total
span, and signed little-endian 16-bit words. The example data use a 10 Hz assumed
period, a small zero-rate bias, and 0.8 °/s rate noise. The receive time is a
phone clock; the legacy packet carries no device conversion timestamp.

## CC2541 MAG3110 magnetometer

The MAG3110 draft exposes signed 16-bit components and makes the physical scale an
explicit calibration gate. The manufacturer nominal sensitivity is 0.1 µT per
LSB. The example data use 0.1 µT/count, a bias of 5, −3, 8 µT, and 0.12 µT noise.
The scale is assumed verified; without that gate the experiment leaves the
physical field unavailable.

## CC2541 SHT21

The SHT21 uses `T = 175.72 ST/65536 − 46.85 °C` and
`RH = 125 SRH/65536 − 6 %`. The low two status bits are cleared before both
conversions. Typical accuracy is ±0.3 °C and ±2 %RH. The example data use a 1 s
assumed period and a shared receive clock for the paired words.

## CC2541 T5400 pressure

The T5400 is polled at 1 Hz. The example uses the manufacturer's compensation
polynomial with the draft fixture coefficients:

`S = c2 + c3 UT/2^17 + c4 UT²/2^34`

`O = c5 2^14 + c6 UT/8 + c7 UT²/2^19`

`p = (S UP + O)/2^14/100 hPa`

`T = 100(c0 UT/256 + c1 64)/65536 °C`

The 16-bit UT is signed and UP is unsigned. Calibration is assumed loaded and
verified. The receive time is the data-read arrival time, not the conversion
instant.

## CC2541 TMP006

The TMP006 reports a signed thermopile voltage word and a signed die word.
Voltage is `word × 156.25 nV`; die temperature is `word/128 °C`. The object
temperature requires the application model

`S = S0(1 + A1 Δ + A2 Δ²)`

`Vos = B0 + B1 Δ + B2 Δ²`

`u = Vobj − Vos`

`f = u + C2 u²`

`Tobj = (Td⁴ + f/S)^(1/4) − 273.15`

where `Δ = Td − Tref`. The example uses S0 = 5.0e-14 V/K⁴ and the draft's
example A1, A2, B0, B1, B2, C2, and Tref values. These are calibration
assumptions, not a certificate for a particular mounting.

## PocketLab Voyager gyroscope

The Voyager draft uses the verified upstream packet layout: signed big-endian
gyro x at byte 8, y at byte 6, z at byte 10, and 2000/32768 °/s per count. The
example data use a 50 Hz assumed notification period, a small bias in rad/s, and
1.5 °/s rate noise. The file is a Voyager adapter; it does not establish PocketLab
One compatibility.

## Puck.js light

The Puck.js script samples `Puck.light()` every 250 ms, or 4 Hz, and sends
`getTime(),light` over Nordic UART. `Puck.light()` is a relative 0–1 response,
uncalibrated and spectrum dependent. The example data use a 0.02 dark level, a
0.90 open reference, 0.02 noise, and independent device and receive clocks.

## Phone microphone and magnetometer

The audio draft uses the phone microphone at 48 kHz and 0.1 s analysis blocks.
The exported RMS is a relative digital amplitude; microphone gain, automatic
gain control, and processing differ by device. The magnetic stream is a 20 Hz
phone magnetometer record in microtesla with an accuracy code.

## Phone accelerometer and linear acceleration

The static-friction draft requests 50 Hz gravity-sensitive acceleration and
50 Hz linear acceleration. The example data use m/s², a 0.02 m/s² gravity noise,
and a 0.1 m/s² linear-acceleration baseline. The two sensor streams keep separate
timestamps. Mounting orientation, sensor-fusion latency, and the slip threshold
are part of the measurement model.

## External UV detector and Nano ADC

The UV draft uses an external detector conditioned to 0–3.3 V on A0 and the
Nano's default 10-bit ADC. The example uses 0–1023 counts, a 3.3 V/1023 V per
count gain, a 10-count dark level, and a 610-count reference. Absolute irradiance
requires a measured detector gain and an explicit calibration gate. The APDS
RGB sensor is not a UV detector.

## Manual observation instruments

`pressure-boiling` uses a calibrated absolute-pressure instrument and a liquid
temperature probe. The example uses 0.1 kPa and 0.2 K standard uncertainties and
the Antoine water saturation curve to choose plausible paired values.

`spectral-fingerprints` uses a wavelength-calibrated spectrometer or calibrated
spectrum files. The example uses 15 nm bins from 400 to 700 nm, 0.2 nm wavelength
uncertainty, a 200-unit unsaturated ceiling, and matched dark/reference/star/
sample intensities.

`coronagraph-contrast` uses fixed-exposure camera images and external ROI
analysis. The example uses 8-bit-like arbitrary units with a 255 ceiling, 10 ms
exposure, and two repeats at each mask/separation condition.

## What the draft examples do not include

- Native Android/iOS import, BLE pairing, or runtime button behavior.
- Full packet captures, reconnect events, or dropped-notification histories.
- Absolute calibration certificates for any sensor or apparatus.
- A complete climate, phase-boundary, spectral-retrieval, or astronomical model.
- The raw 48 kHz audio stream; the audio example provides the block-RMS table.

The draft experiments remain development editions. The example files are for
software, plotting, and teaching development.
