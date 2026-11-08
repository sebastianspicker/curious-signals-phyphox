# Sensors, acquisition, and how the example data are shaped

This note records the physical quantity, configuration, resolution, typical
accuracy, acquisition rate, and modelled error sources for every sensor used by
the experiments. The numbers are component-level specifications from the
datasheets and from the repository's research companion papers. They describe
the sensor, not a particular board, phone, or room.

The example files reproduce the dominant behaviour that a real export would
show: sensor-native units, quantisation, offsets, noise, drift, thermal lag,
saturation, and the timing limits of the acquisition chain.

## At a glance

| Sensor | Host / experiment | Quantity | Range used here | Resolution | Typical accuracy | Rate in these files |
| --- | --- | --- | --- | --- | --- | --- |
| ST LSM9DS1 accelerometer | Nano 33 BLE Sense, mode 1 | specific force | ±4 g | 0.122 mg | offset and mounting dominate; datasheet zero-g offset is tens of mg | 20 Hz |
| ST LSM9DS1 gyroscope | Nano 33 BLE Sense, mode 2 | angular rate | ±2000 °/s | 0.061035 °/s (library) | zero-rate offset and scale error dominate | 20 Hz |
| ST LSM9DS1 magnetometer | Nano 33 BLE Sense, mode 3 | magnetic induction | ±4 gauss = ±400 µT | 0.012207 µT (library) | hard/soft iron and scale error dominate | 20 Hz |
| ST LPS22HB | Nano 33 BLE Sense, mode 4 | absolute pressure | 260–1260 hPa | 0.000244 hPa/code | ±1 hPa uncalibrated, ±0.1 hPa after one-point calibration | 20 Hz |
| ST HTS221 | Nano 33 BLE Sense, mode 5 | temperature, relative humidity | −40–120 °C, 0–100 %RH | 0.016 °C, 0.004 %RH | ±0.5 °C, ±3.5 %RH (20–80 %) | 20 Hz frames, slow sensor |
| Broadcom APDS-9960 | Nano 33 BLE Sense, mode 6 | RGBC counts | 16-bit, nominal 4100-count saturation | 1 count | relative only; no lux calibration | 20 Hz |
| nRF52840 SAADC | Nano 33 BLE Sense, mode 9 | voltage at A0–A2 | 0–3.3 V, 10-bit software range | 3.226 mV/count | reference, gain, and loading dominate | 20 Hz |
| Bosch BMP280 | SensorTag, greenhouse / mission / pt-star / tidal | pressure, die temperature | 300–1100 hPa | 0.01 hPa, 0.01 °C | ±1 hPa, ±0.5–1 °C die | 1 s or 0.1 s |
| TI TMP007 | SensorTag, IR distance / tidal | object and die temperature | −40–125 °C | 0.03125 °C | ±1 °C typical object, ±0.5 °C die | 0.3 s |
| TI OPT3001 | SensorTag, albedo / tidal / transit | illuminance | 0.01–83 865.6 lx | 0.01 lx at lowest range | ±10 % typical, 2 % linearity above 40 lx | 0.8 s |
| Owon B35T | transit / debug | DC voltage | 6 V range | 1 mV | ±(0.5 % + 2 digits) | 2 Hz in the app, 3 Hz on the meter |
| Phone light sensor | albedo / transit | relative illuminance | model dependent | model dependent | model dependent | 10 Hz assumed |
| Phone barometer | mission to Mars | absolute pressure | model dependent | model dependent | model dependent | 10 Hz assumed |
| Bluetooth HID mouse | IR distance | displacement | counts | 1 count | scale and slip unknown | event driven |

## The Arduino BLE chain

The firmware sends a 20-byte notification: five little-endian `float32` values.
CH1 is device time in seconds, CH2–CH5 are the four mode-dependent channels.
The notification interval is at least 50 ms, so the maximum nominal rate is
20 Hz. The internal sensor rates are often higher:

- LSM9DS1 accelerometer and gyroscope: 119 Hz internally, decimated by the
  20 Hz notification schedule.
- LSM9DS1 magnetometer: 20 Hz internally, so a frame boundary can occasionally
  miss a fresh sample; that channel becomes `NaN`.
- LPS22HB: one-shot conversion per read.
- HTS221: one-shot temperature and humidity conversions per read.
- APDS9960: about 11.12 ms integration per RGBC conversion.
- SAADC: three sequential conversions per frame.

The example core files start at `t = 0` for readability. A real device time
counts from the BLE connection and may begin at several seconds when recording
starts after connecting. The timestamp
advances in 50 ms or 51 ms steps because the loop is scheduled from integer
milliseconds, not from a hardware timer.

Unavailable channels are `NaN`. Only the magnetometer file includes a few NaN
rows, because the 20 Hz magnetometer rate is the one that can miss a 20 Hz frame
boundary. The other core channels are always ready at the 20 Hz schedule in these
files.

## ST LSM9DS1 accelerometer

**What it measures.** Specific force along three board axes. Gravity is part of
the signal. A board lying flat and still reads about `+1 g` on the axis that
points up. The firmware returns the library's `g` values and computes the
Euclidean magnitude before transmission.

**Configuration.** The pinned `Arduino_LSM9DS1` library selects a nominal ±4 g
range and a 119 Hz internal output rate. The 16-bit code is converted with
`4/32768 g` per LSB, i.e. 0.122070 mg per code. The experiment multiplies by
standard gravity 9.80665 for the m/s² export (the example record keeps the
historical 9.81 factor); the firmware does **not** send m/s².

**Accuracy.** The selected range is not an accuracy statement. Datasheet zero-g
offset is tens of mg and depends on the part, temperature, and soldering stress.
Mounting alignment and board flexure can be larger than the sensor noise. The
example uses small offsets of order 1–3 mg, 1.2 mg broadband noise, 0.6–0.7 mg slow
drift, and the exact 0.122 mg quantisation. Tilts and taps follow a rotation
model, so the magnitude stays close to 1 g except during the shake.

**Rate.** 20 Hz notifications. A 119 Hz internal rate does not make the exported
record a 119 Hz time series. Hand motion above 10 Hz aliases.

**Example file.** `core/accelerometer_plot_v1-2.example.csv` contains both the `g`
export and the `m/s²` export. The magnitude columns are computed from the three
transmitted components, not added independently.

## ST LSM9DS1 gyroscope

**What it measures.** Angular rate around the three board axes in degrees per
second. The firmware computes the magnitude. The experiment converts to rad/s
with `3.14159/180` and keeps the deg/s export.

**Configuration.** The pinned library selects ±2000 °/s and uses
`2000/32768 = 0.061035 °/s` per LSB. The datasheet sensitivity at this range is
70 mdps/LSB. The ratio is about 0.87193, so the library output is systematically
low relative to the datasheet sensitivity. These files apply that ratio: a
true 45 °/s plateau is reported near 39.2 °/s. This is a nominal scaling discrepancy,
not a calibration of a particular board.

**Accuracy.** Zero-rate offset, temperature drift, and scale error dominate.
Datasheet zero-rate offset at ±2000 °/s is tens of °/s before calibration; a
practical board after warm-up and bias removal is much better. These files use
a 0.05–0.11 °/s bias, 0.06 °/s broadband noise, 0.015–0.020 °/s slow drift, and
the 0.061 °/s quantisation. Hand tremor is added as a low-frequency modulation.

**Rate.** 20 Hz notifications. The internal 119 Hz stream is not exported. The
configured gyro bandwidth is wider than the 10 Hz Nyquist limit of a uniform
20 Hz record, and no matched anti-alias filter is documented.

**Example file.** `core/gyroscope_plot_v1-2.example.csv` contains the deg/s and rad/s
exports. The stationary baseline is deliberately nonzero.

## ST LSM9DS1 magnetometer

**What it measures.** Magnetic induction in the board frame, in microtesla. The
firmware computes the magnitude. The experiment does no further conversion.

**Configuration.** The pinned library selects ±4 gauss = ±400 µT and uses
`400/32768 = 0.012207 µT` per LSB. The datasheet sensitivity is
0.14 mgauss/LSB = 0.014 µT/LSB. The same 0.87193 library-to-datasheet ratio
applies, so an uncalibrated magnitude reads low. The example data apply it.

**Accuracy.** Hard-iron offsets, soft-iron distortion, nearby steel, currents,
and the board's own magnetic environment can easily exceed the Earth-field
signal. Datasheet zero-gauss offset at ±4 gauss is about ±1 gauss (≈100 µT)
before calibration. The example data use a small calibrated-looking offset of a few µT,
a 1–2 % soft-iron matrix, 0.12 µT noise, and 0.04–0.05 µT slow drift. The Earth
field is about 48.3 µT total at Cologne, with a realistic inclination. A magnet
approach raises the field to about 160 µT, still inside the ±400 µT range.

**Rate.** 20 Hz internally. The example data include four `NaN` rows where a fresh sample is
not available at the frame boundary. This is the only core file with missing
values.

**Example file.** `core/magnetometer_plot_v1-2.example.csv`. The values are
sensor-frame components, not a compass heading.

## ST LPS22HB barometer

**What it measures.** Absolute pressure at the sensor port. The library returns
kilopascals; the experiment multiplies by 10 for the hPa export.

**Configuration and resolution.** The LPS22HB covers 260–1260 hPa with a 24-bit
output and 4096 LSB/hPa, i.e. 0.000244 hPa per code. The Arduino library starts a
one-shot conversion, waits for completion, and divides the assembled code by
40960. The example data quantise to `1/4096 hPa` and then rounds the kPa value to
`float32`.

**Accuracy.** Typical absolute accuracy without one-point calibration is ±1 hPa
over 0–65 °C; after the specified one-point calibration it is ±0.1 hPa. Relative
accuracy is ±0.1 hPa over 800–1100 hPa at 25 °C. The 0.0075 hPa RMS noise figure
belongs to particular high-rate and filtering conditions, not to this 20 Hz
one-shot chain. The example data use a +0.55 hPa offset, 0.02 hPa noise, 0.01 hPa slow
drift, and a 0.8 s port/equilibration lag.

**Rate.** 20 Hz maximum nominal; one-shot conversion and BLE scheduling can
lengthen intervals. Device time is formed before the sensor read, so the
timestamp precedes the conversion.

**Example file.** `core/pressure_plot_v1-2.example.csv`. The scenario includes a 1.2 m
lift, a 3 m stair climb, a sealed-bag +8 hPa squeeze, and slow room drift. The
1.2 m lift changes pressure by about 0.14 hPa, which is close to the noise; the
3 m climb changes it by about 0.36 hPa.

## ST HTS221 temperature and humidity

**What it measures.** Temperature at the sensor package and relative humidity of
the air near the package. Relative humidity is a percentage, not a fraction.

**Configuration and resolution.** The HTS221 has a 16-bit temperature channel
with 0.016 °C/LSB and a 16-bit humidity channel with 0.004 %RH/LSB. Typical
accuracy is ±0.5 °C over 15–40 °C and ±3.5 %RH over 20–80 %RH. Humidity response
time is about 10 s at 25 °C and 1 m/s airflow; the temperature response is
slower, about 15 s in the repository's design note. The example data apply a 15 s
temperature lag and a 10 s humidity lag.

**Accuracy and coupling.** The package microenvironment is not the room. Board
self-heating, radiation, airflow, and thermal gradients matter. Relative
humidity also depends on temperature: at constant vapour content, warming lowers
RH. These files therefore follow a vapour pressure, compute the true RH from
the Magnus saturation curve, and pass it through a sensor lag. They do not
simply draw two independent sine waves. They add a +0.32 °C offset, a +1.7 %RH
offset, 0.007 °C and 0.03 %RH noise, and slow drift.

**Rate.** 20 Hz frames, but the sensor conversion is one-shot and the physical
response is much slower. The firmware reads temperature first and humidity
second, so the two numbers in a frame are not simultaneous.

**Example file.** `core/temperature_plot_v1-2.example.csv`. The run includes board
warm-up, two breath events, and a lamp/hand warming interval. The breath raises
RH to about 64 % in the example data because the sensor lag and the simultaneous
temperature rise reduce the peak; a real breath directly on the package can go
higher.

## Broadcom APDS-9960 RGBC sensor

**What it measures.** Clear, red, green, and blue photodiode counts. These are
relative detector counts, not lux, irradiance, or a calibrated colour. The clear
channel is unfiltered within the sensor's UV/IR-blocked passband and is usually
larger than each colour channel.

**Configuration.** The Arduino library writes an integration register that
corresponds to four integration cycles, about 11.12 ms, and a gain setting whose
register value is 16× even though a library comment says 4×. At four cycles the
nominal saturation is `min(65535, 1025 × 4) = 4100` counts, not the 16-bit
register maximum. The example data clip at 4100 and use integer counts.

**Accuracy.** No absolute calibration is provided. Dark counts are 0–3, channel
gains differ, and the spectral responses overlap. These files use channel
gains of 1.02, 1.05, 0.97, and 0.92 for clear, red, green, and blue; dark
counts of 3, 2, 2, and 1; and noise that grows with the count level. A 3.7 Hz lamp ripple is
added below the 10 Hz Nyquist limit; a 50 Hz lamp ripple would alias.

**Rate.** 20 Hz frames. The 11.12 ms integration fits inside the 50 ms interval.
The sensor does not preserve every internal integration cycle in the BLE stream.

**Example file.** `core/light_plot_v1-2.example.csv`. The scenario moves from dim room
to warm lamp to red, green, and blue cards to a saturated flashlight and back.
The flashlight saturates all four channels at 4100.

## nRF52840 SAADC and analog inputs

**What it measures.** Voltages at A0, A1, and A2 relative to board ground. The
default Arduino API returns 10-bit codes 0–1023. The experiment multiplies by
3.226 mV/count, which is the rounded `3300/1023` endpoint conversion.

**Accuracy.** The real reference is not exactly 3.3 V, the converter has offset
and gain errors, and source impedance affects settling. The nRF52840 hardware
converter has more than 10 bits of capability, but this firmware does not change
the resolution. The example data use a 3.31 V reference, per-channel gains of 1.004,
0.997, and 1.001, offsets of +1.2, −0.8, and +0.5 counts, and integer
quantisation. A2 also gets 50 Hz mains pickup, which aliases at the 20 Hz
sampling rate.

**Rate and timing.** 20 Hz frames. A0, A1, and A2 are converted sequentially
within a frame and have no individual timestamps. Device time precedes the
conversions, so cross-channel phase at high frequency is not trustworthy.

**Example file.** `core/analog_input_plot_v1-2.example.csv`. A0 is a potentiometer
sweep, A1 is a light-dependent-resistor step, and A2 is a 1 s RC charge and
discharge. Both raw ADC counts and the nominal mV export are included.

## Bosch BMP280 in the SensorTag

**What it measures.** Absolute barometric pressure and the barometer die
temperature. The die temperature is not an independent air thermometer; Bosch
warns that it is affected by PCB temperature and self-heating.

**Configuration and resolution.** The BMP280 covers 300–1100 hPa. Its compensated
pressure word is scaled by 0.01 hPa in the SensorTag XML; the temperature word is
scaled by 0.01 °C. The datasheet quotes ±1 hPa absolute accuracy, ±0.12 hPa
relative accuracy, and 0.01 °C temperature resolution. The example data use a +0.55 to
+0.60 hPa offset, +0.4 to +0.7 °C die offset, 0.02 hPa and 0.015–0.02 °C noise,
and 0.01 hPa/°C quantisation.

**Rate.** The SensorTag service is configured for 1 s in greenhouse, pt-star,
and tidal-locking, and 0.1 s in mission-to-Mars. Notifications are not
guaranteed; the XML reconstructs time from the sample count, so a dropped packet
compresses the time axis.

**Example files.** `astronomy/greenhouse.example.csv`,
`astronomy/missiontomars_sensortag.example.csv`, `astronomy/pt-star.example.csv`, and
`astronomy/tidal-locking_bmp280.example.csv`.

## TI TMP007 infrared thermopile in the SensorTag

**What it measures.** An object-temperature indication from the thermopile and
the die temperature. The object indication depends on incident radiation,
package temperature, emissivity, reflected background, and field-of-view
filling. It is not a contact thermometer.

**Configuration and resolution.** The TMP007 has 0.03125 °C resolution, a 0.25 s
conversion time, a 90° field of view, and typical object accuracy of ±1 °C for
die 20–40 °C and object 20–60 °C. The XML uses an unsigned 16-bit read and
`floor(word/4) * 0.03125`; this is valid only for nonnegative temperatures. The
example keeps all temperatures above 20 °C and includes the raw object and die
words.

**Rate.** 0.3 s in the IR-distance and tidal-locking experiments. That is just
above the 0.25 s conversion time. There is no common hardware trigger with the
mouse or the other SensorTag channels.

**Example files.** `astronomy/ir-dist_habitable.example.csv` and
`astronomy/tidal-locking_tmp007.example.csv`.

## TI OPT3001 ambient light sensor in the SensorTag

**What it measures.** Illuminance with a photopic spectral response and strong
IR rejection. It is much closer to a lux meter than the APDS-9960, but the
assembled instrument is still not a calibrated photometer.

**Configuration and resolution.** The OPT3001 covers 0.01–83 865.6 lx with
automatic range selection. At the lowest range the resolution is 0.01 lx; at
higher ranges the step grows with the exponent. The datasheet quotes about
±10 % typical accuracy, 2 % linearity above 40 lx, and 800 ms conversion in the
configured mode. The XML decodes the exponent/mantissa word as
`0.01 × mantissa × 2^exponent`.

**Rate.** 0.8 s, set by AA73 = 0x50 (80 × 10 ms). Time is reconstructed as
0.8 s × sample count.

**Example files.** `astronomy/albedo_sensortag.example.csv`,
`astronomy/tidal-locking_opt3001.example.csv`, and
`astronomy/transitmethode_sensortag.example.csv`. Raw OPT3001 words are included
so the decoder can be checked.

## Owon B35T digital multimeter

**What it measures.** A DC voltage at the meter terminals. In the transit
activity it is the voltage across a solar cell or shunt. The meter's input
resistance loads the circuit; the cell's optical response is not necessarily
linear in voltage.

**Configuration and resolution.** The B35T is a 6000-count meter. On the 6 V DC
range the resolution is 1 mV; the datasheet accuracy is ±(0.5 % + 2 digits). The
meter updates its digital data 3 times per second; the Owon app path updates
about twice per second. The example data use 0.5 s (2 Hz) rows, 1 mV quantisation,
0.2 % gain error, 0.4 mV offset, and 0.3–0.4 mV noise.

**Decoder.** The B35T branch of the supplied XML reads a five-character numeric
field, a decimal code, and a unit code. The example data use decimal code 1
(`10^-3`) and unit code 0 (`1`), so `"01854"`, `1`, `0` decodes to 1.854 V. The
negative step uses the same field format, e.g. `"-1002"`, `1`, `0` for −1.002 V.
The W18B branch is not represented in the example data.

**Rate and timing.** The analysis sleep of 0.05 s is not an acquisition rate.
The export time is a receive time; it is not a conversion timestamp. The example data
keep the 6 V range selected for the whole staircase; a real auto-ranging meter
would switch to a finer range below 0.6 V.

**Example files.** `astronomy/owon_digital_multimeter-debug.example.csv` and
`astronomy/transitmethode_owon.example.csv`.

## Phone ambient-light sensor

**What it measures.** A model-dependent light level, usually reported in lux
after the operating system's own calibration and automatic gain. The spectral
response, integration time, and update rate vary by phone.

**Assumptions in the example data.** 10 Hz, 0.1–2 % noise, small timestamp jitter, and
different optical gain from the SensorTag. The phone values are not expected to
match the OPT3001 values. The two files are alternative acquisition paths, not
simultaneous measurements.

**Example files.** `astronomy/albedo_phone.example.csv` and
`astronomy/transitmethode_phone.example.csv`.

## Phone barometer

**What it measures.** Absolute pressure in hectopascals. The sensor model,
filtering, and update rate vary by phone.

**Assumptions in the example data.** 10 Hz, 0.01 hPa resolution, 0.015 hPa noise, a
−0.3 hPa offset, and small timestamp jitter. The phone and SensorTag files are
alternative runs, not simultaneous measurements.

**Example file.** `astronomy/missiontomars_phone.example.csv`.

## Bluetooth HID mouse displacement

**What it measures.** Signed horizontal and vertical movement reports from a
standard BLE HID mouse. The experiment accumulates the reports and computes a
2-D displacement magnitude in mouse counts. It is not a surveyed distance, and
the reported counts depend on the tracking surface, DPI setting, and slip.

**Assumptions in the example data.** About 0.0002 m per count (5000 counts/m), a small
slip event, and a fixed 0.3 s sampling interval synchronized to the TMP007
updates. The experiment has no shared hardware trigger, so moving during a
sample adds an unknown spatial pairing error. The example data move in steps and
settles between them.

**Example file.** `astronomy/ir-dist_habitable.example.csv`.

## What the example data do not include

- Radio packet loss, reconnection, or multi-board discovery conflicts.
- BLE scheduling latency beyond the 50/51 ms core timestamp pattern.
- Sensor initialization failure. Every core mode is assumed available; the
  magnetometer's `NaN` rows are a fresh-sample miss, not an init failure.
- Full calibration coefficients, temperature coefficients, or per-board
  serial numbers.
- Phone model differences beyond the stated light and pressure assumptions.
- Magnetic disturbances from the USB cable, battery, or nearby steel beyond the
  simple hard/soft-iron model.
- Optical spectra. The light data are channel counts or photopic lux, not
  spectra.
- The W18B multimeter branch, unsupported SensorTag generations, or negative
  TMP007 temperatures through the unsigned XML conversion.

The example data are useful for software, plotting, teaching dry runs, and
analysis development.
