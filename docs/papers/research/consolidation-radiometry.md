# Radiometry consolidation

27 October 2026. Four source investigations become two canonical papers. Only
canonical bodies/wrappers, their complete Markdown companions, two combined plot
sources and this merger metadata are edited. Original observations, prepared
numeric tables, all analysis modules/results, generated figures, XML, shared
bibliography and previous research logs remain unchanged.

## Inverse-square photometry

Sources: `illuminance-distance` and `illuminance-distance-manual`.

One source-distance/response model now precedes a comparison of electronic
previous-position pairing with ruler snapshots and stationary light means.
Position calibration, finite-source effects, background and origin covariance
are stated once. The paper retains the difference between lux and relative
counts; these independent runs cannot establish an instrument accuracy ranking.
The apparatus diagram supports both methods. One combined figure uses the
existing electronic stationary-mean/fit tables and the manual snapshot/mean
products, replacing four original plot panels with two complementary panels.

Canonical reductions come from `analysis/draft_optics.py` and
`draft-analysis.json`, without using older auxiliary summaries:

- Electronic light and mouse receive clocks remain separate. Each light sample
  uses the most recent mouse report. Fifteen half-open windows
  `[4j+1,4j+3.5)` seconds, j=0…14, contain three light observations each.
  Scale/origin are 0.0002 m/count and 0.15 m, with initial coordinate 250 counts.
  Background is 2 lx. Unweighted log OLS gives n=2.0012213464, A=103.178447 lx,
  log-residual sample SD 0.007664871. Mean Qr²=103.281038 lx m² and sample
  SD=0.763947 lx m². Leave-one-state-out n spans 1.996604–2.003198.
- Manual observations retain all twelve paired snapshots and all twelve
  two-second device-time windows `[5j+1.5,5j+3.5)`, j=0…11. Background is
  10 counts. Snapshot n=1.9860526274 and mean-based n=1.9880052031;
  logarithmic sample residual SDs are 0.017425787 and 0.001951170.
  Qr² mean/SD changes 102.481667/1.821188 to 102.809642/0.579781 count m².
- ±1-mm origin sensitivity is retained as changed-model analysis, not a
  confidence interval: electronic n=1.996199/2.006240 and manual mean-based
  n=1.982401/1.993605. Direction-specific manual products at 0.20 and 0.70 m
  demonstrate why repeat positioning and a distance-dependent trend differ.
- The initial mouse coordinate remains an explicit position initial condition.
  The source example's single-row signed-byte inconsistency is already recorded
  by the untouched analysis/technical documentation; packet-format details are
  not repeated in the physical article.

Five existing primary references are retained: `zong2018` for reference planes
and metrological distance; `campione2024` for finite sources; `vera2014` for
background-isolated inverse-square experiments; `opt3001` and `apds9960` for the
specific optical indications. There is no duplicated union of the old lists and
no new claim requiring a literature search.

## Infrared radiometry and heating

Sources: `ir-distance` and `cc2541-ir-temperature`.

A common radiometric scene/calibration argument connects the TMP006 external
compensation model to TMP007 object-temperature indication. Sensor generation
is an implementation difference, not a separate physical topic. The TMP006
example establishes how small short-term scatter coexists with strong
application-sensitivity dependence. The TMP007 example then establishes why a
history-dependent temperature–position trajectory cannot determine an equilibrium
heating law. The apparatus combines contact-referenced calibration with a rigid
constant-view target/detector stage. A single three-panel plot retains TMP006
model/die temperature and signed voltage, plus independent TMP007 branches.

Canonical results remain in `analysis/draft_adapters.py`, `analysis/optics.py`,
`draft-analysis.json` and `example-analysis.json`:

- TMP006 uses signed thermopile voltage, temperature-dependent S and offset,
  u=Vobj−Vos, and **f=u+13.4u²** in the fourth-root model. The original field
  labelled corrected flux is actually u; it is never substituted for f.
  S0=5e−14 V K−4 and C2=13.4 V−1. All corrections use the same observation.
  An independent reconstruction finds that the example offsets use
  B2=1.9e−8 V/K² (maximum offset-column residual below 5e−14 V), whereas the
  unchanged XML default is 4.63e−9 V/K². The paper explicitly uses the example
  per-observation offsets/sensitivities; it does not claim those numbers verify
  default XML coefficients. Reconstructing with the example coefficient and
  signed voltage reproduces all three sensitivity means within 1e−7 K.
- Half-open receive windows [0,9), [12,19), [28,38), [42,48) seconds preserve
  model-object means 23.024423, 34.971250, 44.909007 and 30.028010 °C.
  Ambient-to-hot object/die changes are 21.884584/0.203906 K; hot object SD is
  0.099694 K. Twenty-one of 61 raw voltage observations are negative.
- Recomputed hot means at 1.1S and 0.9S, using the complete nonlinear f, remain
  43.117308 and 47.058537 °C. These are sensitivity scenarios, not uncertainties.
- TMP007 retains original half-open windows [0,1.5), [10.5,12), [19.5,21),
  [26.4,27.3) seconds. The 1750-count outward/return means are 29.893750 and
  28.854167 °C, difference 1.039583 K. Counts remain uncalibrated in length.
  The example 0.3-s spacing is distinct from sensor response/integration time.
  Current acquisition pairs each IR receive time with the latest mouse report.
- Removed the complete duplicate manual inverse-square reduction and its plot
  discussion. Incident optical dilution is mentioned only as a conceptual
  prerequisite. The small-rise r−2 and radiation-dominated r−1/2 thermal limits
  remain model deductions with explicit equilibrium/domain assumptions.

Seven existing primary references are selected: `tmp006`, `tmp007`,
`tmp006guide`, `tmp007cal`, `astrolab2022`, `sebastian2011` and `delucas2022`.
Their distinct jobs are instrument model, application calibration, original
heating activity, package gradients and size-of-source effects. `zong2018` now
belongs to the distance paper rather than a second complete optical reduction;
`kopparapu2013` is omitted because the canonical article makes no habitability
inference. No new references or changed bibliography entries are required.

## Verification and proof

The two complete Markdown companions match the scientific bodies, equations,
window definitions and quantitative tables. Their numeric citations link to
human-readable primary references. Plot sources read existing prepared tables;
no new reduction API or generated data is introduced.

Verification evidence and freeze hashes are supplied in the final handoff.

Final verification (27 October 2026):

- Existing `draft_optics.analyze` and `draft_adapters.analyze` reproduce all
  three assigned draft metric dictionaries exactly (exit 0).
- Independent normal-equation calculation from the manual captured counts
  gives n=1.9860526273556387 (exit 0). Independent reconstruction of S, Vos and
  f from signed voltage, die temperature and the actual example coefficient
  B2=1.9e−8 gives 44.9090073831, 43.1173083816 and 47.0585373779 °C at original,
  +10% and −10% sensitivity, respectively (exit 0).
- `latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=output <slug>.tex`
  exits 0 for both wrappers, three pages each. No overfull box, unresolved
  reference/citation, missing character or oversized float. The IR wrapper
  keeps the bibliography together in the next column rather than splitting
  the last reference across columns.
- `pdftoppm -png -r 140 output/<slug>.pdf output/<slug>` exits 0 for both proofs;
  all six final pages were inspected. Short plot-panel titles remain inside
  their axes, all tables are legible and no figure precedes the abstract.
- Metadata matches both mapping arrays exactly. Companions retain the complete
  argument, numeric tables and five/seven linked numbered references.
- Baseline SHA-256 audit changes exactly the four owned existing body/wrapper
  files; the other six deliverables are new. All example inputs, analyses,
  prepared data, original figures, XML and shared references are byte-identical.
  Twelve unrelated architecture/image paths absent from the isolated copy were
  already excluded when that copy was made; none was edited or removed here.

Proofs: `docs/papers/output/illuminance-distance.pdf` and
`docs/papers/output/ir-distance.pdf`; rendered pages use the same base names.
Final hashes of the ten deliverables are supplied in
`docs/papers/output/consolidation-radiometry-freeze.json` and the handoff.
