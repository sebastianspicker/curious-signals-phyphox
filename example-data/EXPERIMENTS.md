# Experiment-by-experiment guide to the example data

This guide follows the order of the repository: seven core Arduino experiments,
then eight astronomy activities. For each experiment it records what the
experiment measures, how the data are acquired, what the exported columns mean,
where the accuracy limits are, and what the corresponding example file contains.

Every file is an example export. See `README.md` for conventions and
`SENSORS.md` for the sensor specifications.

## Quick index

| Experiment | Example file(s) | Sensor / path | Nominal rate | Duration |
| --- | --- | --- | --- | --- |
| Accelerometer | `core/accelerometer_plot_v1-2.example.csv` | LSM9DS1 accelerometer | 20 Hz | 60 s |
| Gyroscope | `core/gyroscope_plot_v1-2.example.csv` | LSM9DS1 gyroscope | 20 Hz | 60 s |
| Magnetometer | `core/magnetometer_plot_v1-2.example.csv` | LSM9DS1 magnetometer | 20 Hz | 60 s |
| Pressure | `core/pressure_plot_v1-2.example.csv` | LPS22HB | 20 Hz | 180 s |
| Temperature and humidity | `core/temperature_plot_v1-2.example.csv` | HTS221 | 20 Hz | 180 s |
| Light and RGB | `core/light_plot_v1-2.example.csv` | APDS-9960 | 20 Hz | 60 s |
| Analog input | `core/analog_input_plot_v1-2.example.csv` | nRF52840 SAADC | 20 Hz | 60 s |
| Albedo | `astronomy/albedo_sensortag.example.csv`, `astronomy/albedo_phone.example.csv` | OPT3001 / phone light | 1.25 Hz / 10 Hz | 60 s |
| Greenhouse | `astronomy/greenhouse.example.csv` | BMP280 die temperature ×2 | 1 Hz | 600 s |
| IR distance | `astronomy/ir-dist_habitable.example.csv` | TMP007 + HID mouse | 3.33 Hz | 30 s |
| Mission to Mars | `astronomy/missiontomars_sensortag.example.csv`, `astronomy/missiontomars_phone.example.csv` | BMP280 / phone barometer | 10 Hz | 120 s |
| Owon debug | `astronomy/owon_digital_multimeter-debug.example.csv` | Owon B35T | 2 Hz | 60 s |
| PT star | `astronomy/pt-star.example.csv` | BMP280 pressure and die temperature | 1 Hz | 180 s |
| Tidal locking | `astronomy/tidal-locking_bmp280.example.csv`, `_tmp007.example.csv`, `_opt3001.example.csv` | BMP280 + TMP007 + OPT3001 ×2 | 1 / 3.33 / 1.25 Hz | 300 s |
| Transit method | `astronomy/transitmethode_sensortag.example.csv`, `_phone.example.csv`, `_owon.example.csv` | OPT3001 / phone light / Owon | 1.25 / 10 / 2 Hz | 90 s nominal |

---

# Core Arduino experiments

The core experiments share one firmware and one 20-byte BLE frame. Each file
below already contains the experiment's exported columns, both wire units and
display units where the experiment exports both.

## 1. Accelerometer

**Measurand.** Specific force along the board's x, y, and z axes, plus the
Euclidean magnitude. Gravity is part of the signal. The board at rest flat on a
table reads about 1 g on z.

**Acquisition.** Mode 1. The LSM9DS1 is configured for ±4 g and 119 Hz
internally; the firmware notifies at most every 50 ms, so the export is a 20 Hz
record. The library returns g. The experiment multiplies by 9.81 for the m/s²
export. The magnitude is computed in firmware from the three components.

**Columns.** `Time t (s)`, the x/y/z components and magnitude in g, then the same
four quantities in m/s². The two sets are not independent measurements; the
second is the first multiplied by 9.81.

**Accuracy.** The 0.122 mg code step is resolution, not accuracy. Zero-g offset,
mounting alignment, board flexure, temperature, and vibration matter more. The
example includes 1–3 mg offsets, 1.2 mg noise, slow drift, and the exact code step.

**Example scenario.** Flat, ±30° tilts, a pick-up and shake, three desk taps with a
7.5 Hz ring-down, a 90° roll, and a return to flat. At 20 Hz the hand motion is
resolved, but the 7.5 Hz tap ring-down is close to the 10 Hz Nyquist limit.

**File.** `core/accelerometer_plot_v1-2.example.csv`.

**What it cannot show.** A calibrated inclination, free-fall acceleration, or a
translation-only acceleration. Subtracting 1 g from the magnitude is not a valid
way to recover translation.

## 2. Gyroscope

**Measurand.** Angular rate around the three board axes, plus the magnitude. The
sign distinguishes clockwise from counterclockwise rotation; the magnitude does
not.

**Acquisition.** Mode 2. ±2000 °/s range, 119 Hz internal, 20 Hz notifications.
The library uses 0.061035 °/s per LSB. The experiment converts to rad/s with
`3.14159/180` and keeps the deg/s export.

**Accuracy.** The important systematic effect is the library-to-datasheet scale
ratio of about 0.87193. A true 45 °/s plateau is reported near 39.2 °/s. The
example data apply this ratio so the data show the same scale error a real board
would show under the pinned library. They also include a small zero-rate bias,
0.06 °/s noise, slow drift, hand tremor, and the 0.061 °/s code step.

**Example scenario.** Stationary baseline, +45 °/s yaw, −45 °/s yaw, +60 °/s roll,
−35 °/s pitch, and stationary again. The plateaus are deliberately not exactly
the commanded values because of the scale error and tremor.

**File.** `core/gyroscope_plot_v1-2.example.csv`.

**What it cannot show.** A calibrated rate or a precise integrated angle. A
residual bias of 0.05 °/s alone gives 3° of angle error after 60 s. The magnitude
channel is a motion detector, not a signed rate.

## 3. Magnetometer

**Measurand.** Magnetic induction in the board frame, plus the magnitude. The
local field includes the Earth's field and any nearby magnets, steel, or
currents.

**Acquisition.** Mode 3. ±4 gauss = ±400 µT range, 20 Hz internal rate, 20 Hz
notifications. The library uses 0.012207 µT per LSB. The experiment does no
further conversion.

**Accuracy.** The library-to-datasheet ratio is again about 0.87193, so an
uncalibrated magnitude reads low. Hard-iron offset, soft-iron distortion, and
environmental disturbances dominate. The example data use a realistic Earth
field of about 48.3 µT total, a small hard-iron offset, a 1–2 % soft-iron
matrix, 0.12 µT noise, slow drift, and four `NaN` rows from a missed 20 Hz
magnetometer frame.

**Example scenario.** Earth-field baseline, 80° yaw, 25° tilt, a magnet approach
near 30 s that raises the magnitude to about 160 µT, then a return to the
starting orientation. The plotted components rotate as the board turns.

**File.** `core/magnetometer_plot_v1-2.example.csv`.

**What it cannot show.** A compass heading without tilt compensation and
calibration, an absolute field accurate to sub-percent, or a clean magnitude
after a magnet has been nearby. The magnitude is computed from the disturbed
components, not from a separate sensor.

## 4. Pressure

**Measurand.** Absolute barometric pressure at the sensor port. The firmware
sends kPa; the experiment multiplies by 10 for hPa.

**Acquisition.** Mode 4. The LPS22HB is read one-shot at up to 20 Hz. It covers
260–1260 hPa, has a 24-bit output with 4096 LSB/hPa, and is specified at ±1 hPa
uncalibrated or ±0.1 hPa after a one-point calibration. The example data use a
+0.55 hPa offset, 0.02 hPa noise, slow drift, and a 0.8 s port lag.

**Columns.** `Time t (s)`, `Pressure (kPa)`, `Pressure (hPa)`. The hPa column is
the kPa column multiplied by 10, not an independent measurement.

**Example scenario.** Indoor baseline near 1009 hPa, a 1.2 m lift, a 3 m stair
climb, a sealed-bag +8 hPa squeeze around 120 s, and slow room drift. The 3 m
climb is the clearest pressure step (about 0.36 hPa); the 1.2 m lift (about
0.14 hPa) is close to the noise.

**File.** `core/pressure_plot_v1-2.example.csv`.

**What it cannot show.** A calibrated altitude without a reference pressure and
a temperature/humidity model, a Martian pressure (the sensor range stops at
260 hPa), or a leak rate without a volume and thermal model.

## 5. Temperature and humidity

**Measurand.** Temperature at the HTS221 package and relative humidity near the
package. Relative humidity is a percentage; 45 %RH is written 45.0.

**Acquisition.** Mode 5. The HTS221 is read one-shot at up to 20 Hz. Its
temperature resolution is 0.016 °C; humidity resolution is 0.004 %RH. Typical
accuracy is ±0.5 °C and ±3.5 %RH. The physical response is much slower: about
15 s for temperature and 10 s for humidity in the repository's design note.

**Accuracy.** The package microenvironment, board self-heating, radiation,
airflow, and thermal gradients matter. RH also falls when temperature rises at
constant vapour content. The example data follow a vapour pressure and a Magnus
saturation curve, then applies the sensor lags, a +0.32 °C offset, a +1.7 %RH
offset, 0.007 °C and 0.03 %RH noise, and slow drift. The two channels are
therefore physically coupled, not independent.

**Example scenario.** Powered-board warm-up, two breath events, and a lamp/hand
warming interval. The breath raises RH to about 64 % in the example data; the sensor lag
and the simultaneous temperature rise reduce the peak. The warming interval
raises temperature to about 25.2 °C and lowers RH to about 40 %.

**File.** `core/temperature_plot_v1-2.example.csv`.

**What it cannot show.** Undisturbed room air temperature, a fast air-temperature
transient, or a calibrated vapour pressure without a pressure input and a
saturation-pressure model. The firmware reads temperature before humidity, so
the two values in a frame are not simultaneous.

## 6. Light and RGB

**Measurand.** Clear, red, green, and blue detector counts from the APDS-9960.
These are arbitrary units, not lux or a calibrated colour.

**Acquisition.** Mode 6. The library uses four integration cycles, about
11.12 ms, and a 16× gain register setting. The nominal saturation is 4100
counts, not 65535. The firmware reads colour only when a fresh conversion is
available; the notification rate is 20 Hz.

**Accuracy.** There is no absolute calibration. Dark counts, channel gains,
spectral overlap, and saturation matter. The example data use channel gains, dark
counts, count-dependent noise, a 3.7 Hz lamp ripple, and a hard clip at 4100.

**Example scenario.** Dim room, warm white lamp, red card, green card, blue card, a
saturated phone flashlight, and dim room again. The clear channel is generally
larger than each colour channel, and all channels clip at 4100 under the
flashlight.

**File.** `core/light_plot_v1-2.example.csv`.

**What it cannot show.** Lux, a calibrated reflectance, a full spectrum, or a
colour coordinate. Four broad channels cannot identify an arbitrary spectrum.

## 7. Analog input

**Measurand.** Voltages at A0, A1, and A2 relative to board ground. The raw ADC
codes are 10-bit (0–1023) and the experiment displays a nominal millivolt value
using 3.226 mV/count.

**Acquisition.** Mode 9. The three channels are converted sequentially within a
20 Hz frame. The default Arduino API resolution is 10 bits, even though the
nRF52840 converter has more hardware capability. Device time precedes the
conversions.

**Accuracy.** The real reference is not exactly 3.3 V, and each channel has
offset and gain errors. Source impedance and acquisition time can also affect
settling. The example data use a 3.31 V reference, per-channel gains and offsets,
integer quantisation, and 50 Hz mains pickup on the high-impedance A2 channel.
The pickup aliases at 20 Hz.

**Example scenario.** A0 is a manual potentiometer sweep, A1 is an LDR step when a
lamp is switched on and off, and A2 is a 1 s RC charge and discharge. The RC
curve is sampled about 20 times per time constant.

**File.** `core/analog_input_plot_v1-2.example.csv`.

**What it cannot show.** A calibrated voltage without an external reference, a
simultaneous three-channel sample, or a trustworthy phase measurement between
channels. The 3.226 mV/count factor is a display convention, not an accuracy
specification.

---

# Astronomy collection

The astronomy files are independent of the Arduino firmware. They use phone
sensors, TI SensorTags, a BLE HID mouse, or an Owon multimeter. Their time axes
have different meanings from the core files.

## 8. Relative reflected light / albedo

**Measurand.** A relative light signal under fixed geometry. The experiment's
built-in result is the run contrast `(max - min) / max × 100`. That is an
extrema statistic, not a calibrated albedo.

**Paths and rates.**
- SensorTag OPT3001: 0.8 s reconstructed time; raw word encoded as
  `0.01 × mantissa × 2^exponent`.
- Phone light sensor: 10 Hz assumed, model-dependent.

**Accuracy.** The OPT3001 is a photopic lux sensor with about ±10 % typical
accuracy and automatic range selection. The phone sensor is model-dependent.
Both are detector-weighted relative measurements; a coloured surface and a white
reference can have different spectral shapes even under the same lamp.

**Example scenario.** Covered sensor, white reference tile (about 420 lx on the
SensorTag, 520 lx on the phone), grey sample (155 / 190 lx), black sample
(18 / 22 lx), then covered again. A lamp warm-up drift and 1–2 % noise are
included. Because the dark intervals are included, the built-in extrema contrast
over the whole file is dominated by the dark level; trim to the illuminated
plateaus if you want a surface-to-surface contrast.

**Files.** `astronomy/albedo_sensortag.example.csv`,
`astronomy/albedo_phone.example.csv`. The SensorTag file includes raw OPT3001 words.

**What it cannot show.** A calibrated directional reflectance, a geometric
albedo, or a Bond albedo. Those require a reference standard, geometry, and
spectral information.

## 9. Greenhouse effect

**Measurand.** Two BMP280 die temperatures in an open and a covered vessel under
the same lamp. The die temperature is a device-temperature proxy, not the air
temperature.

**Acquisition.** Two SensorTags, each configured for a 1 s BMP280 period. The
experiment reconstructs time from the first tag's sample count, so a dropped
packet or a different startup phase can misalign the two columns.

**Accuracy.** The BMP280 die temperature is affected by PCB temperature and
self-heating; it is typically above ambient. The XML scales the signed 24-bit
word by 0.01 °C. A paired difference cancels some common terms but not
independent offsets, spatial gradients, or unequal thermal contact.

**Example scenario.** Both vessels start at 22 °C. The lamp turns on at 60 s. The
open vessel rises by about 4.5 K with a 180 s time constant; the covered vessel
rises by about 8 K with a 150 s time constant. The lamp turns off at 360 s and
both cool. A +0.70 °C self-heating term and different tag offsets are included.

**File.** `astronomy/greenhouse.example.csv`. Time is in minutes.

**What it cannot show.** An air-temperature contrast, a thermal time constant of
the gas, or the isolated greenhouse mechanism. The cover changes convection,
conduction, short-wave transmission, and long-wave exchange at the same time.

## 10. IR temperature versus distance

**Measurand.** TMP007 object-temperature indication, TMP007 die temperature, and
accumulated BLE HID mouse displacement. The mouse displacement is an
uncalibrated distance proxy.

**Acquisition.** TMP007 at 0.3 s (0.25 s conversion time), HID mouse reports
appended when a new IR value is processed. There is no common hardware trigger
and no exported timestamp in the XML; the example data add a `Time (s)` column for
readability.

**Accuracy.** TMP007 object accuracy is about ±1 °C typical (20–60 °C), with
0.03125 °C resolution and a 90° field of view. Emissivity, reflected background,
and field-of-view filling matter. The XML uses an unsigned temperature word, so
it cannot represent negative temperatures correctly. The example data keep all values
positive. Mouse counts depend on DPI, surface, and slip; the example data use about
0.0002 m/count and includes a slip event.

**Example scenario.** The target and SensorTag move together from 0.15 m to 0.80 m
and back in 0.05 m steps, with a 1.4 s thermal lag. The apparent IR temperature
falls from about 38 °C to about 27.6 °C. The die temperature stays near 23 °C.

**File.** `astronomy/ir-dist_habitable.example.csv`.

**What it cannot show.** An absolute source–target distance, an inverse-square
law, or a habitable-zone boundary. The apparent temperature is not the target
surface temperature, and the mouse displacement is not metrology.

## 11. Mission to Mars / spaceship atmosphere

**Measurand.** Absolute pressure in a chamber or prototype, and the mean,
minimum, maximum, and range of the record. The activity is a near-ambient
pressure analogue, not a Martian atmosphere measurement.

**Paths and rates.**
- SensorTag BMP280: 0.1 s period, 0.01 hPa word scaling.
- Phone barometer: 10 Hz assumed, model-dependent.

**Accuracy.** The BMP280 covers 300–1100 hPa and is specified at about ±1 hPa
absolute. The phone sensor is model-dependent. The SensorTag run uses a +0.6 hPa
offset, 0.02 hPa noise, and a 0.35 s chamber lag; the phone run uses a −0.3 hPa
offset and 0.015 hPa noise.

**Example scenario.** Baseline near 1008 hPa, pressurisation to +35 hPa, a slow
1.5 hPa leak over 30 s, release, and a final baseline. The excursion stays inside
the BMP280 range. The phone run shows a slightly different offset and a filter
edge at the step.

**Files.** `astronomy/missiontomars_sensortag.example.csv`,
`astronomy/missiontomars_phone.example.csv`. The SensorTag file includes raw
pressure and temperature words. The phone run has a different offset and noise
level, not a simultaneous recording.

**What it cannot show.** A Martian pressure (a few hPa), a leak rate without a
volume and thermal model, or a force without an effective area.

## 12. Owon digital multimeter debug

**Measurand.** A decoded DC voltage from an Owon B35T or W18B path. The file is
an integration helper, not a stand-alone astronomy lesson.

**Acquisition.** Owon BDM BLE notifications on characteristic FFF4. The meter
updates digital data 3 times/s; the app path updates about 2 times/s. The
analysis sleep of 0.05 s is not a 20 Hz acquisition rate. The export time is a
receive time, not a conversion timestamp.

**Accuracy.** The B35T is a 6000-count meter; on the 6 V DC range the resolution
is 1 mV and the datasheet accuracy is ±(0.5 % + 2 digits). The example data use 1 mV
quantisation, 0.2 % gain error, 0.4 mV offset, 0.3 mV noise, and a slow drift.

**Example scenario.** A DC staircase: 0 V, 1.0 V, 1.5 V, 2.0 V, −1.0 V, 0.5 V, each
held about 10 s. The raw fields follow the B35T branch: a five-character numeric
field, decimal code 1 (`10^-3`), and unit code 0 (`1`). For example `"01854"`,
`1`, `0` decodes to 1.854 V.

**File.** `astronomy/owon_digital_multimeter-debug.example.csv`.

**What it cannot show.** A verified meter protocol for every B35T/W18B firmware,
a current or resistance calibration, or a 20 Hz sampling rate. The two decoder
branches share one characteristic and one output container in the XML.

## 13. Pressure and temperature: star-formation analogy

**Measurand.** BMP280 absolute pressure and barometer die temperature in a
variable-volume chamber. The activity is an analogy for coupled thermodynamic
quantities, not a model of stellar collapse.

**Acquisition.** One SensorTag BMP280 at a 1 s period. Time is reconstructed from
the sample count and exported in minutes. The pressure and temperature words are
scaled by 0.01.

**Accuracy.** Pressure is the compensated absolute value; temperature is the
barometer die temperature, not an independent gas thermometer. The example data use a
+0.55 hPa and +0.40 °C offset, 0.02 hPa and 0.015 °C noise, and 0.01
quantisation.

**Example scenario.** A slow 7 % volume reduction raises pressure by about 75 hPa
(from 1005 to about 1081 hPa) and warms the die by about 1.4 °C, followed by a
release and a small leak. The peak stays inside the BMP280 300–1100 hPa range.

**File.** `astronomy/pt-star.example.csv`. Time is in minutes.

**What it cannot show.** A gas temperature, an adiabatic exponent, or a
star-formation model. The die temperature responds to the PCB and the chamber
walls as well as the gas.

## 14. Tidal locking

**Measurand.** A thermal and optical contrast between two model regions under a
fixed illumination pattern. The BMP280, TMP007, and OPT3001 channels respond to
different physical parts of the experiment and are not interchangeable.

**Paths and rates.**
- BMP280 die temperature: 1 s.
- TMP007 object and die temperature: 0.3 s.
- OPT3001 illuminance: 0.8 s.

**Accuracy.** The XML uses tag 1's sample count for all three time axes, so
different startup phases and dropped packets are not resolved. The TMP007
unsigned conversion cannot represent negative temperatures. The OPT3001 is
photopic, not bolometric. The example data keep all temperatures positive and
include raw words for each channel.

**Example scenario.** The lamp is on from 30 s to 210 s. The day-side BMP280 rises
from about 23 to 39 °C; the night side stays near 23–25 °C. The day-side TMP007
object rises to about 46 °C; the night side stays near 24 °C. The day-side
OPT3001 sees about 12 000 lx; the night side sees about 28 lx of stray light.
Both sides cool after 210 s.

**Files.**
- `astronomy/tidal-locking_bmp280.example.csv`
- `astronomy/tidal-locking_tmp007.example.csv`
- `astronomy/tidal-locking_opt3001.example.csv`

**What it cannot show.** A planetary climate, atmospheric redistribution, or a
rotation/orbit measurement. The activity produces a persistent spatial
asymmetry under a documented lamp geometry.

## 15. Transit method

**Measurand.** A relative light signal over time, from which the experiment
computes an extrema-based transit depth, a radius estimate, and event timing.
The signal can come from a phone light sensor, a SensorTag OPT3001, or a solar
cell through an Owon multimeter.

**Paths and rates.**
- SensorTag OPT3001: 0.8 s.
- Phone light sensor: 10 Hz assumed.
- Owon B35T: 2 Hz.

**Accuracy.** The built-in depth is `(max - min) / max × 100`, not a fitted
baseline-to-plateau depth. The radius estimate uses the source radius input and
assumes a simple area ratio. Timing is threshold-based and depends on the sample
phase. At 0.8 s the SensorTag sees only about 5 samples per 4 s transit, so the
event is intentionally undersampled. The 10 Hz phone path resolves it better.
The Owon path adds the solar cell's nonlinearity and the meter's 1 mV
quantisation.

**Example scenario.** Three 4 % transits of 4 s duration at 22 s, 52 s, and 82 s,
with a stable baseline (850 lx SensorTag, 520 lx phone, 1.85 V Owon). The
SensorTag and Owon files include the raw decoder fields.

**Files.**
- `astronomy/transitmethode_sensortag.example.csv`
- `astronomy/transitmethode_phone.example.csv`
- `astronomy/transitmethode_owon.example.csv`

The experiment's derived `Timing` export set is not included. It is produced by
the XML's threshold logic from the raw signal, so it is analysis output rather
than an independent measurement.

**What it cannot show.** An exoplanet discovery, a calibrated radius without
the source geometry, or a normalized light curve on the Owon path. The Owon
export is a voltage, not a normalized flux.

---

## Cross-experiment reading notes

1. **Resolution is not accuracy.** The smallest displayed step is often much
   smaller than the offset, scale, drift, or environmental uncertainty. The
   example data include both, but the step alone should not be quoted as
   accuracy.
2. **The core files are 20 Hz records, not sensor-native records.** The
   LSM9DS1 runs faster internally, the HTS221 and LPS22HB are one-shot, and the
   APDS-9960 integrates for about 11 ms. The BLE notification schedule is the
   exported time base.
3. **The astronomy files use reconstructed time.** SensorTag time is a sample
   count times 0.1 s, 0.3 s, 0.8 s, or 1 s. A dropped notification compresses the
   time axis. Phone time comes from the operating system's sensor interface; the
   Owon time is a receive time. Neither replaces a hardware conversion timestamp
   on the SensorTag.
4. **Two files for one experiment are alternative paths, not simultaneous
   measurements.** Albedo, mission-to-Mars, and transit each have more than one
   input path. The values differ because the optics or pressure sensors differ.
5. **The example data include realistic imperfections.** Offsets, scale errors,
   lag, saturation, missing samples, and drift are present. A perfectly smooth sine
   wave would not be a useful test of an analysis pipeline.
