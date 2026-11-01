# Astronomy Experiments Companion

The eight files in `experiments/astronomy/` are independent of the Arduino
`phyphox-sense` kit. They read from phone sensors, TI SensorTags, a Bluetooth HID
mouse, or an Owon multimeter. Treat every one of them as a classroom model or
analogy rather than a calibrated astronomical instrument.

All of them use English as the root locale and include German and French
translations; phyphox falls back to the English text on any other device
language.

For detailed sensor physics, apparatus schematics, calibration procedures,
measurement models, and worked example-data analyses, see the eight astronomy
papers in the [research companion collection](papers/README.md). Acquisition
and reproduction details are collected in the accompanying documentation.

A few things the files themselves do not settle:

- They do not say which TI SensorTag generation they expect.
- The Owon decoder branches are labeled for B35T and W18B models, but those
  labels are not a statement that the current hardware still matches.
- Pairing, wiring, and live device behavior still need to be checked against the
  equipment you actually have in the room.

Every activity includes a translated **Setup** view. Measure calibration and
baseline values on the actual apparatus; the example CSVs do not supply those
values for a new experiment. Enter settled interval means, keep the intervals
and their spread in the lab record, and export settings along with measurements.
Changing settings recomputes the recorded analysis. Clear data between different
physical configurations and re-enter any settings restored to their defaults.

SensorTag records now use a separate Bluetooth receive timestamp for each
device and characteristic. Delayed or lost notifications no longer shorten an
invented sample-count clock. Receive time still includes radio and processing
latency; it is not the time of the underlying sensor conversion. Phone sensor
timestamps remain separate. To compare two sensors, use the same settled time
interval or an explicitly justified time alignment, never matching row numbers.
Exports have changed to keep independently timed records in separate sheets.

## The activities

### `albedo.phyphox`

Compares reflected light from a phone or SensorTag light sensor under fixed
geometry. Enter dark, reference and sample plateau means separately for each
instrument, then enable the reduction. The relative reflectance is
`q = (sample − dark)/(reference − dark)`, requiring reference above dark and
sample at least dark. A sample brighter than the reference can give `q > 1`;
this is a relative ratio, not an absolute albedo. The old extrema statistic is
labelled **Full-record contrast** and is not used as the sample reflectance.

Fix source distance, incidence and viewing angles, sample area and detector
position; use a baffle against direct lamp light. Bracket sample observations
with reference observations and verify detector linearity without clipping.

### `greenhouse.phyphox`

Records BMP280 die temperature from two SensorTags. Enter each tag's own
equilibrated lamp-off mean to compare `T(t) − T_baseline` on its own time axis.
For a paired contrast, compare the rises over the same time interval; a direct
array subtraction would incorrectly pair asynchronous samples.

Match vessels, lamp distances, mounting and airflow; co-locate the tags first,
then exchange them between vessels to check sensor and position effects. Use
shielded independent probes for gas-temperature claims. This comparison also
responds to convection and conduction; it does not isolate atmospheric infrared
absorption or reproduce a complete planetary greenhouse effect.

### `ir-dist_habitable.phyphox`

Plots SensorTag infrared object-temperature estimates and detector die
temperature against mouse displacement. Signed decoding now includes negative
temperatures. Mouse positions are held at their latest preceding timestamp for
each infrared sample; repeated analysis cycles do not duplicate temperatures.
The raw counts remain available, with an optional measured distance origin and
metres-per-count scale for a fixed, one-sided rail.

Keep the mouse axes fixed, calibrate travel against a ruler, hold at each
position until temperatures settle, and repeat the outward/return sequence.
Keep target emissivity and the filled field of view constant. Detector die
temperature is not an air-temperature measurement. Even a calibrated distance
axis does not turn object temperature into irradiance or establish an
inverse-square law or habitable-zone boundary.

### `missiontomars.phyphox`

Uses a phone or SensorTag pressure sensor to record ambient pressure in `hPa`
and report whole-record minimum, maximum, mean and range. An unavailable phone
barometer no longer prevents using the external path. Compare settled windows
against an independent absolute-pressure reference in the same volume, retain
vent access, and allow thermal equilibration. Leakage requires a pressure,
temperature and volume model; the experiment does not measure Mars's atmosphere.

### `owon_digital_multimeter-debug.phyphox`

Exposes raw fields and decoder channels for the Owon B35T and W18B paths, with
an explicit model selector. Unknown B35T scale codes give an invalid value
instead of falling through to the binary decoder. Raw fields and receive times
are retained for diagnosis. It supports the transit activity as an integration
utility; W18B packet fixtures check the declared interpretation, not current
hardware compatibility. Confirm the meter mode and units against its display
and a stable reference before connecting a solar-cell circuit.

### `pt-star.phyphox`

Records SensorTag pressure and BMP280 die temperature with a receive-time axis.
A kelvin column supports dimensionally correct discussion. Die temperature is
not necessarily gas temperature: a gas-law test needs an independent immersed
gas probe, known volume, equilibration and an appropriate compression model.
Compare slow and faster changes without exceeding equipment ratings. The
activity is a thermodynamic analogy, not a simulation of stellar collapse.

### `tidal-locking.phyphox`

Uses two SensorTags to compare BMP280 die temperature, TMP007 object-temperature
estimates and detector die temperature, and OPT3001 illuminance. Each device and
sensor characteristic retains its own clock. Enter separate lamp-off baselines
for the six temperature channels; use common time windows for day/night rise
contrasts. Optical export headings identify tag 1 and tag 2 distinctly.

Co-locate and exchange the tags, match thermal contact, fix emissivity and IR
view geometry, and shield thermometers appropriately. Illuminance is photopic,
not total radiative heat flux. Persistent spatial asymmetry in this apparatus
does not establish a tidally locked planet's atmospheric heat transport.

### `transitmethode.phyphox`

Retains separate phone, SensorTag and Owon histories; select the source used for
analysis explicitly. Enter a local out-of-transit baseline, an in-transit
plateau mean and background to obtain
`depth = (baseline − plateau)/(baseline − background)`. Enable the mean-based
reduction after entering valid values. Invalid denominators or depths outside
`[0, 1]` suppress the radius estimate.

For a uniform source and opaque central silhouette,
`R_planet = R_star × (d_planet/d_star) × sqrt(depth)`, where both distances are
measured from the detector. The distance ratio is an explicit setting. Fix
source brightness, geometry and background, and verify a linear signal response.
A solar cell's open-circuit voltage is not generally proportional to flux;
use a defined load and check the working range before interpreting depth.

Alternating lower and upper crossings provide hysteresis. Timing reports
threshold-dependent durations for up to six complete events and averages the
available valid durations/periods. An initially incomplete dip is excluded;
absent events are not filled with zeros. Finite timing pairs exclude invalid
meter readings, while raw exports retain gaps. Gaps and sample cadence still
limit edge timing. These are model-transit measurements, not geometric contact
times or exoplanet-discovery precision.

## Teaching and maintenance

Introduce each activity in this order: the measured quantity, the model
interpretation, and the claim the setup cannot support. That keeps direct
observations separate from inferred or analogical conclusions.

When you change a file here, update its note above if the input path, the model,
or the scope limit moved, then run:

```sh
make validate
```

Implementation checks follow the official [phyphox analysis semantics](https://phyphox.org/docs/file-format/analysis/),
[BLE timestamp documentation](https://phyphox.org/docs/file-format/bluetooth-low-energy/)
and [format validators](https://phyphox.org/docs/reference/validators/).
The [TMP007 datasheet](https://www.ti.com/lit/ds/sbos685c/sbos685c.pdf) specifies
the signed temperature words. Sensor physics and the remaining primary
references are developed in the research companions.
