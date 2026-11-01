# Environment and voltage consolidation

27 October 2026. Five source investigations are consolidated into two canonical topic papers. Example observations, all analysis modules and reports, experiment definitions and prior research logs remain unchanged. No new reduction API or bibliography entry is required.

## temperature-humidity

**Mapping:** temperature-humidity + cc2541-humidity + sensortag-environmental.

The integrated argument defines RH, saturation pressure and the paired-channel Magnus reduction once, then contrasts three physical cases: HTS221 warming at nearly unchanged local vapour pressure; SHT21 moisture pulse and recovery; HDC1000 moisture pulse with an independent BMP280 thermal-location diagnostic. One apparatus diagram replaces three repeated apparatus descriptions. A single three-panel temperature–RH trajectory plot retains each instrument's paired observations without inventing an inter-instrument time alignment. The independent BMP280 temperature and pressure observations remain substantively represented in the thermal-location discussion.

### Canonical reductions

All windows are start-inclusive and stop-exclusive on the relevant record's own time: Nano device time for HTS221 and Bluetooth receive time for the SensorTag streams. Vapour pressure is computed from simultaneous sensor-local T/RH at each observation and then averaged, using 610.94 exp(17.625 T/(T+243.04)) Pa for saturation pressure. The table presents hPa.

| Case | Window(s) | Retained result |
|---|---|---|
| HTS221 baseline/warming | 20–30 / 90–96 s | 22.788/25.123°C, 46.842/40.403% RH; 1296.630/1286.881 Pa; −0.7519% vapour-pressure change |
| HTS221 first moisture event | maximum over35–60 s | 63.688% RH; distinct from the warming comparison |
| SHT21 baseline/pulse/recovery | 0–10 /26–35 /50–60 s | 12.241/17.237/12.084 hPa; local T22.484/22.599/22.678°C |
| HDC1000 baseline/pulse/recovery | 0–25 /40–60 /85–115 s | 12.384/20.558/11.485 hPa; RH44.161/67.043/40.995% |
| BMP280 thermal locations | own0–25 /40–60 s | 24.106/24.335°C versus HDC1000 23.003/24.488°C; no universal offset |
| BMP280 pressure context | complete48-row record | 1007.46–1008.49 hPa |

Dedicated source-window decisions supersede older auxiliary summaries: the HDC pulse is40–60s (eight observations), not45–60s (six); the SHT baseline is0–10s, not0–20s. The latter would partly include the pulse approach and change the headline baseline from1224.1 to1263.2Pa. Earlier extrema remain descriptive but do not replace the paired HTS90–96s warming estimator. The0.400s HDC/BMP arrival offset is not labelled sensor lag or latency. Existing nearest-neighbour diagnostics retain their0.5s acceptance rule; the humidity reduction itself needs no BMP pairing.

### References selected

Seven existing verified sources are sufficient: `hts221`, `sht21`, `hdc1000` for sensor-local measurements, conversion and response conditions; `bmp280` for the second die temperature's compensation role; `alduchov1996` for saturation pressure; `greenspan1977` for equilibrium humidity references; and `holik2024` for a calibration design that includes temperature. The repeated protocol/packet reference is omitted because sensor-generation conversion is explained compactly and the linked primary datasheets support it. Separate general thermometry and humidity review citations add no distinct claim to this merger.

The full calibration argument appears once: joint temperature/RH reference design, rising/falling humidity paths, withheld validation points, dynamic input identifiability and correlated uncertainty. Independent runs do not establish inter-sensor offsets or an accuracy ranking. The repeated draft-status and implementation instructions are removed from the canonical companion.

## analog-inputs

**Mapping:** analog-inputs + owon-interface.

The common chain is numerical representation → terminal calibration → loading → physical inference. The ADC and DMM each contribute an independent test of this chain. One shared circuit diagram shows source resistance, capacitor, test readout and reference DVM. One combined data figure uses existing ADC channels and the signed multimeter staircase, with separately named Nano device-time and multimeter receive-time axes. Distinct tables support the six signed plateaux and the two RC fits. The duplicated UV transmission calculation, six UV observations and spectral-response digression are removed; their optical inference belongs to the canonical light/radiometry paper.

### Canonical reductions

| Case | Window / estimator | Retained result |
|---|---|---|
| Owon staircase | interior1–9,11–19,21–29,31–39,41–49,51–59s;16 readings each | nominal0,1,1.5,2,−1,0.5V; means0.000500,1.002500,1.503375,2.004500,−1.0015625,0.5016875V |
| Owon affine fit | OLS of six plateau means against nominal example levels | gain1.001994643; offset0.503571mV; maximum absolute residual0.186607mV |
| ADC A0 | complete record | codes187–870, display603.262–2806.62mV |
| ADC A1 | complete record | qualitative light-dependent circuit response; no calibrated illuminance inference |
| A2 charging | 5–12s, free asymptote/amplitude and profiled positive τ | τ0.9997203s; asymptote2995.357mV; RMS1.76049mV;139 observations |
| A2 discharging | 35–42s, same estimator | τ0.9994760s; asymptote1.72175mV; RMS1.91230mV;139 observations |
| RC interval sensitivity |5–10 /35–40s | τ0.9997614/0.9993518s; changes below0.2ms |

The existing environment.py profile-OLS/golden-section reduction was rerun directly against the current source observations and reproduces all four RC fit results. No analysis code was edited. The staircase was also checked independently from current rows. Software conversion residuals are retained as numerical-consistency evidence, not terminal accuracy. The3.226mV/count versus1mV digit comparison is granularity only; independent runs are not paired or ranked.

The loaded-circuit equation is stated for an explicit topology: the source remains connected through R in high and low states, so τ=(R||R_L)C. Disconnecting the source changes the discharge circuit. This prevents an unstated switching assumption from entering a capacitance claim. Photocell loading remains a compact electrical example, without duplicating an optical worked analysis.

### References selected and checked

Six existing verified sources: `nrf52840` for acquisition settling/reference configuration; `arduinocore` and `analogread` for intended ten-bit output and resolution semantics; `owon35` for selected range, digit size and stated manufacturer limits; `torriente2023rc` for the instructional RC measurement precedent; and `gum` for calibration coefficient covariance and reference uncertainty. Generic phyphox/interface citations are omitted because they do not independently calibrate voltage. Optical responsivity/UV citations are omitted with the transferred digression.

Primary source URLs already recorded in the verified bibliography were rechecked for the Owon manual and Nordic product specification. The web endpoint timed out/returned530, respectively; no new specification claim is inferred from that failure. The consolidation relies on the previously verified manual/specification and preserves the original range/acquisition claims. No new reference metadata is introduced.

## Verification and presentation

Both canonical Markdown companions contain the full argument, equations, tables, informative figure captions, and numbered human-readable references. All figure links use ../../../output/pdf/<canonical-slug>.pdf. The plots reference only existing prepared primary tables; no prepared table or generated figure source was changed. Wrappers load flafter to keep the abstract before floats. Final compilation and page-inspection evidence is reported to the parent with the owned-source hash manifest.
