# Acquisition and reproduction details

These notes collect file and software details supporting the topic papers.
The [manifest](manifest.json) maps every article to its acquisition file and
example CSVs. Exact analysis windows and numerical results are recorded in
[example-analysis.json](example-analysis.json); the original channel names,
units and scenarios are documented under `example-data/`.

## Expanded research edition

The twenty-one topic papers cover all forty-three experiments and all fifty-eight
example datasets. The manifest keeps the forty-three acquisition and analysis
records in `analysis_sources`; each canonical paper lists the sources it develops
in `analysis_ids`. The original numerical reductions remain in
`example-analysis.json`; `draft-analysis.json` records the twenty-eight new
analyses, and `revision-analysis.json` records supplementary comparisons in the
original fifteen investigations. Each report carries input and analysis-code hashes.
The prepare scripts read the examples without regenerating or changing them.

The [consolidation record](research/consolidation.md) maps the earlier papers to
their canonical topics and identifies the principal reduction for repeated
examples. Auxiliary calculations remain reproducible, including alternative
windows that are no longer repeated as competing headline results in the papers.

The topic research notes under `research/` record the literature search and
reference selection. Figures use the caption label **Example data**. The
articles discuss physical results and inference; these notes retain the
acquisition and reproduction details.

The expanded analyses also distinguish stored diagnostic columns from the
current reductions. The audio example floors a negative background-subtracted
power at zero; the paper excludes that interval from a logarithmic contrast.
The Puck example includes pre-gate ratios below the dark level; those values are
outside the accepted transmission domain. For TMP006, the column headed
“Compensated flux” contains the intermediate voltage difference
`u = V - V_offset`; the temperature and sensitivity calculation uses the full
`f = u + 13.4 u²` correction. The UV observation and continuous records differ
by up to three counts at matched times. The distance example's initial mouse
displacement is treated as a position anchor, not a valid signed-byte report.
These distinctions are retained in the analyses without changing the inputs.

The TMP006 example also uses an offset coefficient `B2 = 1.9e-8 V/K²`, whereas
the experiment's default is `4.63e-9 V/K²`. Its quoted target temperatures and
sensitivity perturbations therefore use the example-specific offsets and
sensitivities. They are not a replay under unchanged default coefficients.

Several comparisons are conditional rather than independent calibration tests.
The magnetic-current example's displayed current follows its nominal affine
conversion; the paper evaluates repeatability without using that column as an
independent reference. The colour-temperature conversion uses a matrix devised
for the TCS3414CS, so it does not establish an APDS-9960 calibration. The seasons
example fails the expected hemispheric reversal and is analyzed as a geometry
test. Heating fits stop before discontinuities at lamp-off. Per-paper methods,
numerical windows and supporting sources are recorded in the analysis reports
and topic research notes.

## Experiment revision after the research analysis

The original example CSVs and their primary reductions remain unchanged. They
describe the earlier acquisition implementation, whose exact hashes are retained
in [example-source-snapshot.json](example-source-snapshot.json). The tables below
document that historical implementation, including its known limitations; they
are not instructions for the revised files. The current experiment definitions
are recorded separately in [source-snapshot.json](source-snapshot.json).

The research findings now inform the importable experiments:

- Core files expose measured axis gains/biases, temperature/humidity biases,
  pressure-reference differences, dark subtraction and per-input affine voltage
  calibration. Acceleration uses standard gravity 9.80665, angular conversion
  uses a full-precision π, and the default ADC endpoint scale is exactly
  3300/1023 mV/count. Raw readings and parameter settings remain exportable.
- SensorTag paths record Bluetooth receive times per device and characteristic.
  They do not synthesize time from sample counts or reuse another tag's clock.
  These are delivery timestamps with radio latency, not sensor conversion times.
- Thermal comparisons use separate measured lamp-off baselines. BMP280 and
  TMP007 die temperature are distinguished from gas/air temperature. TMP007
  words now decode signed temperatures correctly. Pressure/temperature exports
  include kelvin without asserting that chip temperature is gas temperature.
- Optical comparisons use entered plateau means with denominator/domain checks;
  full-record extrema remain diagnostic. Transit radius includes the detector
  distance ratio. Timing averages available complete events, rejects initial
  partial dips, and keeps invalid readings from arming a false transit.
- Transit histories remain separate until explicit source selection. Owon
  model selection prevents a malformed B35T scale code from falling through to
  W18B decoding. W18B hardware compatibility is still unverified.
- IR distance records pair temperature timestamps with preceding mouse positions
  and offer measured scale/origin controls while retaining uncalibrated counts.

Updated exports include settings and independent sensor time axes, so their
sheet names and column layouts can differ from the historical examples. See
the [core guide](../../src/phyphox/README.md#calibration-and-physical-setup) and
[astronomy companion](../ASTRONOMY_EXPERIMENTS_COMPANION.md) for current workflows.
The translated in-app setup instructions describe the physical improvements
needed; no new apparatus measurements or calibration coefficients are implied.

## Original core sensor records

The seven core experiments use the original Arduino Nano 33 BLE Sense. They
share a device timestamp and four channel values in a 20-byte BLE frame.
The timestamp precedes sensor reads, and the notification interval is at least
50 ms. The pinned library and firmware versions are identified in the repository
configuration and [example acquisition snapshot](example-source-snapshot.json).

| Paper | File representation or conversion |
| --- | --- |
| Accelerometer | Mode 1; library values are `4q/32768` in g; the SI columns multiply by 9.81. The two unit sets are alternate representations of one measurement. |
| Gyroscope | Mode 2; library scale `2000/32768` degrees/s per count; radians/s use `3.14159/180`. The discrepancy from the nominal datasheet sensitivity affects the paper's rate analysis. |
| Magnetometer | Mode 3; library scale `400/32768` µT per count. Missing values occur at zero-based rows 217, 583, 901 and 1102. They are excluded from statistics without joining the plotted gaps. |
| Pressure | Mode 4; firmware kPa values are multiplied by ten for hPa. These columns are not separate pressure measurements. |
| Temperature and humidity | Mode 5; temperature and humidity are requested sequentially. The shared timestamp does not imply simultaneous conversion. |
| Clear/RGB light | Mode 6; the configured integration is approximately 11.12 ms with 16× gain. The effective ceiling is about 4100 counts despite 16-bit output words. |
| Analogue inputs | Mode 9; ten-bit codes are displayed using 3.226 mV/count. Raw codes are retained for a different calibration. A0, A1 and A2 are converted sequentially. |

For the core figures, time is taken directly from the supplied device-time
column. The accelerometer plot uses the SI columns; the voltage plot converts
display millivolts to volts. RGB plots express counts in thousands. These are
unit changes, not fitted corrections.

## Original astronomy records and interfaces

The phone, SensorTag and multimeter alternatives are separate records, not
synchronized observations. The SensorTag examples reconstruct time from sample
count. Lost notifications would therefore change the apparent timing; the
phone and multimeter paths have different timestamp semantics.

| Activity | Implementation detail |
| --- | --- |
| Albedo | The OPT3001 word uses a four-bit exponent and twelve-bit mantissa: `0.01 m × 2^e`. The SensorTag interval is 0.8 s. Each path is dark-subtracted and reference-normalized separately. |
| Greenhouse | BMP280 die-temperature words are scaled by 0.01. Time is exported in minutes; both channels use the first tag's sample-count axis. Analysis converts this to seconds, while the figure retains minutes. |
| Infrared temperature and distance | The original export lacks timestamps; the example adds a time column. TMP007 updates every 0.3 s and is paired with the latest mouse displacement. Its unsigned temperature conversion does not represent negative temperatures correctly. The positive-temperature example does not exercise that case. |
| Mission to Mars | The SensorTag pressure word uses 0.01 hPa increments and a nominal 0.1-s interval. Phone timestamps are separate. The application's extrema and mean displays are distinct from the window-based reduction in the paper. |
| Owon interface | B35T and W18B decoder branches share a characteristic and output container without an explicit model selector. The example exercises the B35T field interpretation only. The W18B unsigned-word/sign-magnitude branch needs separate packet tests. |
| Pressure and temperature | BMP280 pressure and die-temperature words are scaled by 0.01. The nominal sample interval is 1 s and the export time is in minutes. |
| Tidal locking | BMP280, TMP007 and OPT3001 have separate 1.0-, 0.3- and 0.8-s grids. Each paired group reuses its first tag's count-based axis. The TMP007 negative-temperature decoding limitation also applies here. |
| Transits | The built-in depth is the global extrema contrast. Its six-event timing summary cannot be filled by the three-event examples. The paper calculates local depths and two onset intervals independently. The multimeter path records voltage. |

The B35T example uses decimal code 1 and unit code 0, so a signed numeric field
is multiplied by 0.001 V. All fields reproduce the recorded values to a maximum
absolute floating-point difference of about 2.3 × 10⁻¹⁶ V. The utility's 0.05-s
analysis sleep is a processing interval, not a 20-Hz meter acquisition rate.

## Plot transformations and analysis

All source rows are preserved in the prepared numeric tables. Missing values
remain nonfinite; plotting never substitutes zero. The relevant plot
transformations are:

- Pressure zoom: subtract the initial 0–20 s mean. The height table separately
  uses local interpolated baselines as specified in the paper.
- Albedo: subtract each path's pooled covered-sensor mean and divide by its
  dark-subtracted white-reference mean.
- Greenhouse difference: subtract each channel's 0–60 s mean before taking
  covered minus open.
- Infrared branches: outward samples have `t < 21 s`; return samples have
  `t >= 21 s`. Samples retain acquisition order. The position axis remains in
  mouse counts.
- Mission to Mars: subtract each record's own 0–15 s mean.
- Transit figures: divide each full record by its first event's local baseline.
  Numerical depth estimates instead use a local baseline for each event.

The greenhouse and tidal-locking examples contain discontinuities at lamp-off.
The analysis preserves them and restricts heating fits or comparison windows to
the preceding heating branch. It does not fit one continuous exponential across
the change.

The analysis modules preserve the stated interval-boundary conventions. Minute
timestamps in the thermal examples are converted to seconds and rounded to six
decimal places to avoid moving a boundary sample because of CSV decimal
rounding. This numerical convention is recorded with the computed results.

The editable archive contains the original example generator for provenance,
but building the papers does not run it or alter the supplied CSVs.
