# Consolidation: thermal and planetary laboratory models

Date: 27 October 2026. Scope: seven source investigations become three canonical
articles, following the authoritative consolidation mapping. Work was confined to
the isolated `thermal` copy. All original investigations, analyses, prepared
products and example inputs remain available; the active articles use fewer,
more informative combined plots.

## Greenhouse → enclosure heating and thermal response

Merged `greenhouse` and `greenhouse-single`. The integrated question is what a
warming response identifies about absorbed power, heat loss and the sensor's
thermal state. One enclosure balance and one weak-loading sensor-node equation
replace separate introductions to the same thermal physics. The experimental
design section compares paired measurements with sequential A–B–A preparations.
The article retains their different inference and repeatability requirements.

Canonical reductions:

- Paired vessels: baseline [0,60) s; late heating [330,360) s; heating fit
  [70,350) s with fixed baseline and 60-s onset. Rises 3.565833 and 6.786500 K;
  extra covered rise 3.220667 K. Apparent time constants 179.454 and 150.201 s;
  fitted amplitudes 4.492028 and 7.995905 K.
- Single sensor: baseline [0,55) s; late heating [210,235) s; fit [65,235) s.
  Measured baseline 22.700893 °C, late mean 27.992500 °C, rise **5.291607 K**.
  Fitted amplitude 7.995735 K, time constant 149.6618 s, RMS 0.019198 K.
  The older auxiliary [210,240) result of 5.334353 K is deliberately omitted.
- The entered 22 °C reference contributes an initial 0.700893-K offset. The
  single adjacent-sample change at nominal lamp-off is 2.61 K; paired changes
  are 1.06 and 1.34 K. The text relates these to failure of the fitted single-node
  branch continuation without claiming to resolve an instantaneous physical jump.

The combined plot uses the original paired table, single-sensor table and its
existing fitted table. It compares baseline-relative curves on separate run axes;
no amplitude or time constant is pooled across preparations. The quantitative
comparison table replaces repeated baseline/result tables.

Selected references (seven): `bmp280`, `lundstrom2020`, `boulard1993`, `burt2020`,
`gum`, `wagoner2010`, `pierrehumbert2011`. Radiation bias, mounted response,
ventilation, covariance and the atmospheric/enclosure distinction each have a
specific role. `elyounsi2021` is omitted here because Burt and de Podesta supply
the relevant thermometer-response argument; Elyounsi remains in the gas article.
The general programme context is not another introductory reference.

## Mission to Mars → gas-enclosure mechanics and thermodynamics

Merged `mission-to-mars`, `cc2541-pressure` and `pt-star` under the new title
*Pressure, Compression and Relaxation in Gas Enclosures*. One force relation and
one ideal-gas state/differential model organize the independent cases. T5400
compensation is kept as a short measurement-model subsection, rather than a
hardware-specific article or packet tutorial. The compression path is a distinct
case of the same state constraint. Spacecraft loading and stellar cooling are
brief concluding contexts; boiling and Martian phase-equilibrium numbers are
omitted and belong to the separate pressure-boiling article.

Canonical reductions:

- Phone/BMP280 enclosure cases: [0,15) s baselines, [30,35) and [50,55) s
  plateaus, [30,55) s local line fits. Early excesses 34.807322/34.829200 hPa;
  declines 1.0274/1.0314 hPa; slopes −0.0513497/−0.0514941 hPa/s.
- T5400: [0,18) s baseline, [26,30) s early state, [52,60) s release and
  [28,44) s slope fit. Excursion 20.005044 hPa, slope −0.0909123 hPa/s,
  residual RMS 0.034310 hPa. Local code sensitivities remain approximately
  0.0244 hPa/count and 0.179 K/count. The conditional fractional pressure decline
  is −8.84924×10⁻⁵ s⁻¹, not an inferred flow rate.
- Compression: [0,30), [55,60), [70,85), [150,180) s states, using the original
  minute coordinate converted to seconds. Rise 75.029333 hPa and die rise
  1.400333 K. Conditional isothermal/adiabatic volume ratios are
  0.93056684/0.94989770 at γ=1.4. With the stated initial gas-temperature
  assumption, adiabatic warming is 6.160289 K. Die substitution would give
  0.93496106. The later 2.524-hPa pressure reduction requires 0.695935-K
  cooling under the stated closed fixed-volume assumption, while observed die
  cooling is 0.002667 K.

The four-panel combined figure retains separate clocks for phone/BMP280,
T5400 and compression cases. It plots pressure excess and the compression die
rise from existing prepared tables; no raw-data or analysis change was needed.
Two compact tables present the excursion/slope comparison and compression states.

Selected references (seven): `mars2022`, `bmp280`, `t5400`, `dickow2015`,
`elyounsi2021`, `larson1969`, `bhandare2025`. The original protocol source is
omitted because packet/coefficient formats remain in technical documentation;
the manufacturer supports the per-device compensation requirement. The unavailable
historical workshop reference `star2020` is unnecessary for the integrated
physical argument and is omitted. Saturation/IAPWS/NASA phase references are left
to the boiling article. Existing verified bibliography entries are reused.

## Tidal locking → geometry, forcing and response

Merged `tidal-locking` and `seasons-obliquity` under *From Illumination Geometry to
Thermal Contrast*. The order of reasoning is incidence/rotation geometry,
measured optical response, seasonal symmetry tests, persistent illumination and
thermal redistribution. Instantaneous incidence and daily integrated insolation
are distinguished once. Orbital labels A/B are never silently assigned to
solstices. The complete twelve-condition table replaces the shorter repeated
high-latitude table in the original tidal paper.

Canonical reductions:

- All twelve seasonal snapshots remain, with source distance 100 cm and
  normalization (X−10)/1090. Each is checked against its matching raw device-time
  observation while preserving receive time. Plateaus use [5i+1,5i+4) s on
  device time, i=0…11. Sample SD range 2.76–12.10 counts and maximum
  snapshot-to-plateau difference 14.13 counts remain as fluctuation diagnostics.
- Zero-tilt A-to-B high-latitude changes are −0.334/−0.325 in relative response;
  the equatorial change is −0.0688. Tilted northern-minus-southern differences
  are 0.0037 and 0.0073. These values do not establish the ideal solstitial
  exchange. The separate conditional local-noon geometry ratio is 7.101007.
- Fixed illumination: baseline [0,30), late heating [180,210), light average
  [30,210) s. Baseline-corrected object/BMP280-die/TMP007-die contrasts are
  19.4134375/11.477/0.81375 K. Mean day/night illuminances are
  12353.8318/27.4496 lx, ratio 450.055805. Native group grids remain separate.

One three-panel plot shows the raw seasonal plateaus with their snapshots,
fixed-illumination lux, and the three thermal-contrast curves. Contrast arithmetic
uses the already established original baseline differences; no interpolation or
new reduction API was introduced. Counts, lux and absorbed power remain distinct.

Selected references (eight): `paillard2026`, `dobrovolskis2011`, `apds9960`,
`vijeta2021`, `opt3001`, `tmp007`, `bmp280`, `koll2022`. Galano's practical-work
context and the general astro-lab programme are omitted because geometry is
introduced directly. Rose's climate calculations and Wirth's atmospheric-regime
study are beyond the retained two-region argument; Koll provides the necessary
planetary heat-transport connection. All retained entries were verified in the
preceding research edition. No new scientific claim or bibliographic entry
required a new source search during consolidation.

## Verification and proof

The full canonical Markdown companions follow the same argument, equations,
windows, result tables and numbered citation order as their LaTeX articles. They
include human-readable linked references and PDF figure links. Their table
separators, metadata mapping and figure data dependencies were checked directly.

Checks (final exit codes):

- `python3 output/consolidation-thermal/numeric-check.py`: 0. Independent direct
  reductions reproduce canonical heating windows, the two paired fit minima
  through a separate 0.1-s grid-profile calculation, chamber excursions and a
  pairwise-expression slope, adiabatic state relations, all twelve raw/snapshot
  correspondences, three thermal contrasts and the lux ratio.
- Metadata/Markdown/plot-dependency Python checks: 0. Mapping equals the root
  mapping; three titles and all 22 selected reference entries match; all five
  tables have valid Markdown structure and every plot dependency exists.
- Preservation audit against `baseline-hashes.json`: 0. All 416 baseline-tracked
  non-owned files in the isolated copy remain unchanged. A separate byte check
  finds all 246 protected data/experiment/analysis/prepared files identical to
  current main. Root's later shared typography/date edits were not copied into
  or written from this copy.
- Each `latexmk -pdf -interaction=nonstopmode -halt-on-error
  -outdir=../../output/consolidation-thermal <slug>.tex` from `docs/papers`: 0.
  Each article is three pages. Final logs have no overfull boxes, unresolved
  citations/references, missing glyphs or oversized floats.
- Each `pdftoppm -scale-to 1500 -png output/consolidation-thermal/<slug>.pdf
  output/consolidation-thermal/<slug>`: 0. All nine final pages were inspected.
  Plot labels are outside the signal region; schematic labels are separated;
  the gas article's references start together in the final right column.

PDF proofs and page PNGs are in `output/consolidation-thermal/`. Final owned-file
SHA256 values are recorded there in `owned-sha256.txt`. The read-only scientific
review independently reproduced the principal numerical results and checked plot
columns, clock conversion and baseline constants; final hashes are supplied for
its closing verdict. No source data, analysis, generated plot tables, XML,
protocol, firmware or shared bibliography/build file was edited.
