# Additional experiment drafts

Twenty-eight importable phyphox drafts extend the Curious Signals series.
Their analyses are integrated into the [twenty-one topic papers](../papers/README.md),
which combine complementary devices within shared physical investigations.
The links below lead to the appropriate canonical companion and its PDF.
The collection develops the useful
activities and hardware variants found in `artikel-proofread-lectorate`. It
includes optical and astronomical investigations, mechanics, environmental
adapters and observation tables for measurements made with external instruments.

Every file appears in phyphox under **Curious Signals drafts**, with **Draft:** in
its title. These are development editions: numerical and format checks are
available, while native app, Bluetooth and apparatus validation remain to be
completed. Manuscript completion does not change the experimental validation
status of the accompanying phyphox definitions.

## Begin with the optical sequence

A useful first sequence is **detector characterization → RGB transmission →
Nano transit → exomoon photometry → starspot crossings**. It establishes sampling,
noise and reference measurements before interpreting subtle light-curve
features. Malus' law and seasons provide different physical questions using the
same Nano light channel. Eclipsing binaries require further apparatus development.

Read the companion before opening the corresponding experiment. Nano drafts use
the existing firmware for the **original Nano 33 BLE Sense**, with one active
sensor mode at a time. They do not add support for Rev2. The other files identify
their required device generation explicitly.

| Investigation | Research companion | phyphox file | Acquisition and reduction |
| --- | --- | --- | --- |
| Detector sampling and detectability | [Read](../papers/companions/transit-method.md) | [Open](../../experiments/drafts/detector-characterization.phyphox) | Nano RGBC, measured sample intervals, baseline noise and signal-to-noise ratio |
| RGB filters and model atmospheres | [Read](../papers/companions/light-rgb.md) | [Open](../../experiments/drafts/rgb-filter-transmission.phyphox) | Nano RGBC, fixed dark/reference transmission in each channel |
| Laboratory transit with Nano | [Read](../papers/companions/transit-method.md) | [Open](../../experiments/drafts/nano-transit.phyphox) | Clear light, complete-event timing and projected planet radius |
| Exomoon photometry and overlap | [Read](../papers/companions/transit-method.md) | [Open](../../experiments/drafts/exomoon-photometry.phyphox) | Clear light, entered comparison means, extra depth and overlap brightening |
| Starspot crossings | [Read](../papers/companions/transit-method.md) | [Open](../../experiments/drafts/starspot-crossing.phyphox) | Clear light and controlled transit/spot comparisons |
| Eclipsing binary light curves | [Read](../papers/companions/transit-method.md) | [Open](../../experiments/drafts/eclipsing-binary.phyphox) | Clear light, primary/secondary depths and phase from an entered period |
| Seasons and obliquity | [Read](../papers/companions/tidal-locking.md) | [Open](../../experiments/drafts/seasons-obliquity.phyphox) | Nano light snapshots with entered geometry and captured calibration |
| Malus' law | [Read](../papers/companions/malus-law.md) | [Open](../../experiments/drafts/malus-law.phyphox) | Nano light and entered protractor angles, cos² comparison and residuals |
| Illuminance versus distance | [Read](../papers/companions/illuminance-distance.md) | [Open](../../experiments/drafts/illuminance-distance.phyphox) | CC2650 light plus calibrated HID mouse position, explicit clock alignment |
| Relative light versus ruler distance | [Read](../papers/companions/illuminance-distance.md) | [Open](../../experiments/drafts/illuminance-distance-manual.phyphox) | Nano light snapshots and entered ruler distance, inverse-square comparison |
| Indicative colour temperature | [Read](../papers/companions/colour-temperature.md) | [Open](../../experiments/drafts/colour-temperature.phyphox) | Nano RGBC, editable colour matrix, guarded chromaticity and McCamy estimate |

## Mechanics and paired measurements

| Investigation | Research companion | phyphox file | Acquisition and reduction |
| --- | --- | --- | --- |
| Static friction at first slip | [Read](../papers/companions/static-friction.md) | [Open](../../experiments/drafts/static-friction.phyphox) | Phone acceleration, armed settings and first sustained valid slip |
| Sound and magnetic field near a motor | [Read](../papers/companions/audio-magnetic.md) | [Open](../../experiments/drafts/audio-magnetic.phyphox) | Phone audio blocks and magnetometer, separate clocks and relative level |
| Magnetic measurement of DC current | [Read](../papers/companions/magnetometer.md) | [Open](../../experiments/drafts/magnetic-current.phyphox) | Phone field component and measured two-point calibration |

## Observation tables and external detectors

The first three files below collect values measured or reduced outside phyphox.
Their Record buttons build paired tables; they do not acquire pressure probes,
spectra or camera images. The UV file has a real Nano analog input and requires
an external UV detector with suitable signal conditioning.

| Investigation | Research companion | phyphox file | Acquisition and reduction |
| --- | --- | --- | --- |
| Pressure-dependent boiling | [Read](../papers/companions/pressure-boiling.md) | [Open](../../experiments/drafts/pressure-boiling.phyphox) | Entered calibrated pressure, liquid temperature and observation code |
| Spectral fingerprints | [Read](../papers/companions/spectral-fingerprints.md) | [Open](../../experiments/drafts/spectral-fingerprints.phyphox) | Entered calibrated wavelength and matched spectral intensities |
| Coronagraph contrast | [Read](../papers/companions/coronagraph-contrast.md) | [Open](../../experiments/drafts/coronagraph-contrast.phyphox) | Entered fixed-exposure image-region statistics, contrast and noise |
| UV transmission | [Read](../papers/companions/light-rgb.md) | [Open](../../experiments/drafts/uv-transmission.phyphox) | External detector on Nano A0, reference transmission and gated irradiance |

## Hardware and access variants

These extend acquisition options rather than count as ten new physical lessons.
CC2541 and CC2650/CC1350 packets are different. The PocketLab adapter targets
**Voyager**: the archive's file labelled PocketLab One actually used SensorTag
characteristics and could not establish One compatibility.

| Adapter | Research companion | phyphox file | Scope |
| --- | --- | --- | --- |
| Single-sensor warming | [Read](../papers/companions/greenhouse.md) | [Open](../../experiments/drafts/greenhouse-single.phyphox) | One CC2650/CC1350 SensorTag; sequential thermal comparison |
| SensorTag environment | [Read](../papers/companions/temperature-humidity.md) | [Open](../../experiments/drafts/sensortag-environmental.phyphox) | HDC1000 humidity/temperature and BMP280 pressure/temperature with separate clocks |
| Puck relative light | [Read](../papers/companions/light-rgb.md) | [Open](../../experiments/drafts/puck-light.phyphox) | Scoped 4 Hz Espruino script; uncalibrated light and device/receive time |
| CC2541 acceleration | [Read](../papers/companions/accelerometer.md) | [Open](../../experiments/drafts/cc2541-accelerometer.phyphox) | Signed byte decoding and physical units |
| CC2541 angular velocity | [Read](../papers/companions/gyroscope.md) | [Open](../../experiments/drafts/cc2541-gyroscope.phyphox) | Legacy gyro packet and scale |
| CC2541 magnetic field | [Read](../papers/companions/magnetometer.md) | [Open](../../experiments/drafts/cc2541-magnetometer.phyphox) | Raw counts; physical scale requires firmware verification |
| CC2541 humidity | [Read](../papers/companions/temperature-humidity.md) | [Open](../../experiments/drafts/cc2541-humidity.phyphox) | Correct SHT21 conversion and status-bit masking |
| CC2541 pressure | [Read](../papers/companions/mission-to-mars.md) | [Open](../../experiments/drafts/cc2541-pressure.phyphox) | T5400 coefficient reads and an explicit calibration/state workflow |
| CC2541 infrared temperature | [Read](../papers/companions/ir-distance.md) | [Open](../../experiments/drafts/cc2541-ir-temperature.phyphox) | Signed TMP006 raw values; object result requires application sensitivity |
| PocketLab Voyager angular velocity | [Read](../papers/companions/gyroscope.md) | [Open](../../experiments/drafts/pocketlab-gyroscope.phyphox) | Verified upstream Voyager packet layout; no One compatibility claim |

## Recording and interpretation

Read each Setup view for the actual capture sequence. Record buttons stage one
snapshot for the next analysis cycle; wait for the row count or table to update
before pressing again. A paused live experiment records its last acquired
sample. Missing acquisition stays unavailable, including when a valid row is
recorded later. Clear observations removes the table; the app's Clear data is a
separate operation.

Observation and seasons rows retain their calibration settings. The ruler and
Malus comparisons deliberately apply the current calibration to their retained
raw table, as described in those companions. Export settings with results.
Invalid domains yield gaps. Nano RGBC values are counts, not lux, resolved
spectra or UV readings. Colour temperature remains an indicative estimate until
the detector response and source range are calibrated; acoustic level is not
certified or A-weighted SPL.

## Files and checks

Example CSV exports for all 28 drafts are in
[`example-data/drafts`](../../example-data/drafts/README.md). They use the
same export columns and acquisition rates as the draft XML.

The [manifest](manifest.json) maps every XML to its manuscript, hardware,
acquisition type, sources and limitations. The [source review](source-review.md)
records what was adapted, what was already covered and the attribution terms.
The [validation notes](validation.md) distinguish automated checks from the
remaining app and apparatus work.

```sh
make check-drafts
make bundle-drafts
```

The build writes an experiment ZIP (built locally at `output/drafts/curious-signals-draft-experiments.zip`),
a complete draft collection ZIP (built locally at `output/drafts/curious-signals-draft-collection.zip`)
and experiment hashes under the gitignored `output/drafts/`. The collection ZIP
contains the editable XML, canonical companions, protocol contract, attribution
and license texts. Current verified PDFs are included when available; bundling
the XML and text does not require a TeX installation. The complete research edition, individual PDFs, analysis code and
all example data are available through the [paper collection](../papers/README.md).
Source articles are not republished in either archive.
