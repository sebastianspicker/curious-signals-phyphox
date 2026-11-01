# Consolidation of the research collection

The collection is organized around physical questions. Twenty-one topic papers replace forty-three standalone articles while retaining all forty-three experiment definitions and all fifty-eight example datasets. Longer comparative articles develop shared models and calibration methods once, then use complementary devices or experimental configurations to test their consequences.

The cover identifies the collection as a summary of work from 2018 to 2024 at the Institute of Physics Education, University of Cologne. The collected edition and literature review were prepared in October 2026.

## Topic ownership

| Canonical topic | Source investigations |
| --- | --- |
| [Specific force, static inclination and quantisation](../companions/accelerometer.md) | Specific Force; Eight-Bit Tilt Measurement |
| [Scale, rate reversal, signed integration and angular path](../companions/gyroscope.md) | Angular Velocity and Bias; Legacy Signed Angular Rate; Voyager Signed Rotation |
| [Vector calibration, field disturbance and indirect current](../companions/magnetometer.md) | Magnetic Measurements; Reorientation and Magnetic Disturbance; Magnetic DC Current Calibration |
| [Hydrostatic height and bracketing baseline drift](../companions/pressure.md) | Pressure and Relative Height |
| [Warming, added moisture and local vapour pressure](../companions/temperature-humidity.md) | Temperature and Humidity; Humidity Pulse Metrology; Independent Environmental Clocks |
| [Spectral weighting, reference substitution and transmission](../companions/light-rgb.md) | Relative Colour Measurements; Broad-Band Filter Transmission; Relative LED Photometry; Ultraviolet Transmission |
| [Voltage calibration, loading and circuit response](../companions/analog-inputs.md) | Voltage Measurement; Bluetooth Multimeter Acquisition |
| [Directional reflectance and planetary albedo](../companions/albedo.md) | Relative Reflectance |
| [Paired and sequential enclosure heating](../companions/greenhouse.md) | Enclosure Heating; Single-Sensor Warming |
| [Thermopile calibration and distance-dependent heating](../companions/ir-distance.md) | Infrared Temperature and Distance; Thermopile Application Calibration |
| [Pressure loading, compression and thermal relaxation](../companions/mission-to-mars.md) | Mission to Mars; Pressure Excursion and Compensation; Compression and Star Formation |
| [Illumination geometry, forcing and thermal response](../companions/tidal-locking.md) | Day–Night Thermal Response; Obliquity and Illumination |
| [Occultation geometry, source brightness and detectability](../companions/transit-method.md) | Transit Photometry; Nano Transit Photometry; Sampling and Detectability; Planet–Moon Photometry; Starspot Crossings; Eclipsing Binary Photometry |
| [Inverse-square response and position calibration](../companions/illuminance-distance.md) | Inverse-Square Photometry; Paired Ruler Photometry |
| [Polarisation and angular response](../companions/malus-law.md) | Settled-Angle Polarimetry |
| [Chromaticity transforms and source-dependent calibration](../companions/colour-temperature.md) | Indicative Colour Temperature |
| [Contact preparation, first slip and inclination](../companions/static-friction.md) | First Slip and Static Friction |
| [Complementary sound and field observations of motor state](../companions/audio-magnetic.md) | Sound Envelopes and Magnetic Fields |
| [Phase equilibrium and operational boiling observations](../companions/pressure-boiling.md) | Pressure-Dependent Boiling |
| [Paired spectral ratios, registration and resolution](../companions/spectral-fingerprints.md) | Paired Spectral Ratios |
| [Spatial suppression, target throughput and detectability](../companions/coronagraph-contrast.md) | Occulting-Mask Contrast |

## Reduction choices

Length ceilings allow additional derivation or comparison without making length
a target. For a merged topic, the longest constituent paper in the previous
edition defines the baseline, with a maximum of three times that page count.
Retained papers allow up to 1.5 times their prior length, rounded down to a whole
page ceiling. These limits are recorded in the publication manifest and checked
before a completed edition is published locally.

The dedicated primary reductions define the principal estimates. Earlier auxiliary summaries sometimes used different windows on the same observations. Their numerical reports remain available for reproducibility; the canonical articles do not present those alternatives as additional independent results.

- Nano transit depth uses the dedicated local reduction (4.26%), starspot brightening uses 2.92 percentage points, and binary eclipse depths use 31.05% and 10.49%.
- The single-sensor warming comparison uses the 0–55 s baseline and 210–235 s late interval, giving a 5.2916 K rise.
- HDC1000 moisture-pulse means use the dedicated 40–60 s pulse interval; SHT21 uses its dedicated 0–10 s baseline.
- Each source keeps its own device or receive time. Unrelated examples are compared through defined observables and models, not treated as simultaneous measurements or used to rank sensor accuracy.

## Boundaries retained

Hydrostatic height, gas-chamber mechanics and boiling remain separate because they use different state constraints and observables. Static friction retains contact history and first-slip detection as its central question. Spectral identification, radiometric colour estimation and coronagraphic imaging also remain distinct despite shared optical terminology.

The consolidated occultation paper develops a common brightness-integral model before comparing dark transits, overlapping silhouettes, spotted sources and two luminous components. The planetary illumination paper follows geometry through optical forcing to thermal response, keeping the separate examples and their limitations explicit.

## Sources and reproducibility

The original topic research records retain the wider searches and source checks. Consolidation records document the selected references and editorial decisions for each canonical group:

- [Motion and magnetic measurements](consolidation-motion.md)
- [Environmental and voltage measurements](consolidation-environment.md)
- [Relative optics and retained optical topics](consolidation-optical.md)
- [Distance photometry and infrared radiometry](consolidation-radiometry.md)
- [Occultation photometry](consolidation-photometry.md)
- [Thermal and planetary models](consolidation-thermal.md)
- [Barometry, boiling, spectra and imaging](consolidation-observations.md)
- [Contact mechanics and motor observations](consolidation-mechanics.md)

The manifest separates source analyses from publications. All original numerical modules, prepared observations and source hashes remain unchanged. The active source and PDF archives contain only the twenty-one canonical articles. The earlier complete edition is retained locally under `output/archive/2026-10-26-before-consolidation/`, outside the active publication collection.
