# Draft validation and remaining apparatus checks

Experiment validation date: 26 October 2026. The collection contains 28 phyphox
definitions, each linked to its consolidated research companion. All definitions pass both official format schemas
and the repository's numerical, packet and processing-cycle fixtures. Independent
Codex reviews covered optics/photometry, mechanics/observations and adapters;
the recording and invalid-domain findings were fixed and rechecked. The
research companions analyze all 37 additional example datasets within the
[21-paper research collection](../papers/README.md).
Manuscript completion does not change the apparatus validation status below.

## Reproduce the software checks

Use the Python development environment described in [CONTRIBUTING](../../CONTRIBUTING.md).

```sh
make lint
make validate
make check-generated
make check-papers
TMPDIR=/private/tmp make security
make bundle-drafts
```

`make validate` runs the original experiment checks and all five draft fixture
groups. `make check-drafts` runs only draft coverage and fixtures. The checks
read the actual XML rather than a separate copy of its equations. They cover
references and export headings, packet offsets/units, missing data, calibration
domains, independent clocks, complete transit events, first-slip capture and
repeated Record/Clear behavior. The original fifteen experiments, firmware,
protocol and example datasets remain unchanged by this draft addition.

For the additional schema pass, obtain both files from the official
[format validators](https://phyphox.org/docs/reference/validators/), install
`lxml` in the chosen validation environment, then run:

```sh
python scripts/check_drafts.py --rng /path/to/phyphox.rng --sch /path/to/phyphox.sch
```

Direct schema downloads: [Relax NG](https://phyphox.org/docs/assets/validators/phyphox.rng)
and [Schematron](https://phyphox.org/docs/assets/validators/phyphox.sch).

The schemas used for this edition had these SHA-256 values:

```text
ad622d394825c025d08a970ede8f72306b4ed78ad772b2942ad62065756ca58f  phyphox.rng
b62715a5477fa2578c5264f77068b4a612892e3715605ed39757daf8e83de130  phyphox.sch
```

The schemas are external validation inputs, not automatically fetched by the
normal gate. Both structural errors and Schematron assertions must pass. A
format version is an XML-format version, not an app release number.

## Native behavior represented by the fixtures

The focused runner is a small software model, not a native phyphox runtime. Its
button and formula behavior was checked against the Android implementation:

- A button replaces its destination buffer and copies the whole source buffer.
  Setting an append attribute does not turn it into a row accumulator.
- Record therefore copies singleton values into pending fields; one analysis
  pass appends them and consumes the request. Multiple presses before that pass
  can coalesce, so the interface asks users to wait for the recorded-row count.
- Formula input references to an empty buffer emit no value. Missing acquisition
  must be represented explicitly to keep later observation rows aligned.
- Division uses IEEE nonfinite values. Dividing by a zero validity predicate
  can create infinity, which may turn into a plausible zero in a later
  reciprocal. The drafts use explicit NaN masks or finite-output guards.
- Live streams need periodic analysis; `onUserInput=true` suppresses that
  schedule. User actions can still trigger analysis while paused.

Implementation references:
[button transfers](https://github.com/phyphox/phyphox-android/blob/master/app/src/main/java/de/rwth_aachen/phyphox/ExpView.java),
[formula evaluation](https://github.com/phyphox/phyphox-android/blob/master/app/src/main/java/de/rwth_aachen/phyphox/FormulaParser.java),
[analysis scheduling](https://github.com/phyphox/phyphox-android/blob/master/app/src/main/java/de/rwth_aachen/phyphox/PhyphoxExperiment.java).
These are implementation evidence, not a claim that every Android/iOS release
behaves identically or that native imports were performed.

## What still requires an app and apparatus

The experiment instructions identify the relevant calibration checks. Before classroom use,
import the file on the intended Android/iOS versions, inspect all views and
units, acquire actual data, pause/resume, record two different observations,
clear and export. For a row-capture file, record once before acquisition and
once after a real sample; earlier unavailable rows must not shift later data.
Verify that editing a setting has the documented effect on captured versus
recalculated results.

| Area | Unverified physical or runtime behavior |
| --- | --- |
| Nano optics and photometry | Delivered cadence, dropped notifications, clipping, linearity, source geometry, lamp drift and feature detectability |
| HID distance | Mouse report compatibility, displacement scale, axis direction, timestamp alignment and rail geometry |
| Phone mechanics/audio | Sensor axes, mounting, slip threshold/debounce, microphone gain/AGC, magnetic background and current calibration |
| Puck.js | Script transmission/execution, MTU/notification behavior, reconnection, timer lifecycle and other UART traffic |
| CC2541 pressure | Calibration-read ordering, requested state transition and device coefficients on the actual firmware |
| CC2541 magnetic/IR | Firmware magnetic sensitivity and application-specific TMP006 sensitivity/thermal calibration |
| Voyager and environmental adapters | Exact supported hardware, BLE setup and notification layout on the intended device firmware |
| External observations | Independent instrument/image/spectrum calibration, paired timing, transcription and uncertainty |
| UV | Electrical input limits, spectral response, reference geometry, linearity and irradiance calibration |

The papers provide quantitative analyses of the example data, with figures
captioned **Example data**. Native screenshots, BLE sessions and apparatus
calibrations remain outstanding. Promotion from draft requires evidence
appropriate to the particular experiment, rather than schema acceptance alone.
