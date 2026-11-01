# Motion consolidation: editorial and scientific record

Date: 27 October 2026. Status: ready for the parent's requested independent review. This consolidation owns three canonical papers and preserves the eight investigation IDs in the authoritative mapping. The articles are rewritten around common physical models, not assembled as sequential device notes. Existing examples, numerical modules/reports, original figure sources and bibliography remain unchanged.

## Sources and common argument

- **accelerometer** absorbs `accelerometer` and `cc2541-accelerometer`: one specific-force model, one reference apparatus, and one vector calibration connect static projection, angular quantisation and the distinct dynamic tap regime. Nano/CC2541 code granularity is compared explicitly; their unrelated pose histories are not treated as a performance comparison.
- **gyroscope** absorbs `gyroscope`, `cc2541-gyroscope` and `pocketlab-gyroscope`: one signed-rate model precedes Nano reversal calibration, CC2541 sustained-axis integration and Voyager cancellation/path/orientation distinctions. Rate extrema are distinguished from true plateaux. The indicated norm is not silently given the component's local bias correction.
- **magnetometer** absorbs `magnetometer`, `cc2541-magnetometer` and `magnetic-current`: a common sensor-frame vector model leads from reorientation/norm diagnostics to controlled coils, then to scalar current inversion at a fixed geometry. The independent field scale, frame alignment and electrical current reference resolve different unidentified quantities. Derived-current circularity is explained once alongside the more useful assigned-state endpoint reduction.

Three new combined plot sources use only existing normalized tables. Each panel retains a distinct record clock. The magnetic current panel plots field only: a second panel of the derived current would visually duplicate the same information. Packet layouts are reduced to the physical scale and identity needed for interpretation; low-level protocols remain in their technical sources.

## Canonical reduction decisions

All statistical windows are left closed/right open. Sample SD is interval variation, not uncertainty of a mean estimated with N independent replicates. No new numerical API is needed.

### Accelerometer

Primary reductions: `analysis/inertial.py` and `analysis/draft_adapters.py`.

- Nano: initial [0,8) s; positive/negative tilts [16,19), [26,29); quarter-turn [46,49). Means (fx,fz,norm) are (0.017,9.833,9.834), (4.927,8.521,9.843), (-4.883,8.526,9.826), (0.028,0.040,9.824) m/s² at displayed precision. Quarter-turn y mean -9.824 m/s².
- Nano opposed-x midpoint 0.0222 m/s²; whole-record sampled norm maximum 1.3467g at 36.382 s. The text preserves the distinction between a sampled transient and an independently characterized impact maximum.
- CC2541: initial [0,8) s, tilts [16,19), [26,29), roll [46,49). Canonical tilt estimates are atan2 of component means: +19.966°, -20.482°; roll 60.195°. The initial 81 observations share one raw triplet. Norms 9.76338, 9.73550 and 9.76784 m/s² are preserved in the table. No alternate tilt-window estimates from auxiliary summaries are promoted.
- Code step 9.80665/64 = 0.1532289 m/s²; local near-level angular spacing 0.895247°. The 128-fold comparison uses the stated nominal LSM9DS1 0.122 mg increment, not an inferred noise ratio.
- The planar atan2 derivative is written explicitly to connect component covariance to angle uncertainty. This is algebraic propagation, not an additional fitted result.

### Gyroscope

Primary reductions: `analysis/inertial.py` and `analysis/draft_adapters.py`.

- Nano: baseline [0,7), positive yaw [11,17), negative yaw [21,27), roll [31,37), pitch [41,47), final baseline [52,59) s. Canonical yaw means +39.35998 and -39.11020 deg/s; nominal-input reversal gives offset 0.124891 deg/s and gain 0.8718909. Preserve nominal conversion ratio 0.8719308 and correction factor 1.14688. Initial/final z means 0.101144/0.150173 deg/s remain drift diagnostics.
- CC2541: final residual-offset window [56,60) s (not the [55,60) auxiliary summary), y mean -0.0015192684 rad/s. Sustained y interval [42,48) gives -200.105 deg/s and SD 0.01359 rad/s. The [9,11) and [19,21) z windows are smooth extrema, not calibration plateaux. Integral window [40,50) spans retained samples approximately 40.098–49.902 s. Baseline-subtracted y signed/absolute integrals -1960.763/+1960.763°, original indicated norm 1961.646°.
- Voyager: initial offset [0,9) s; x mean -0.0097869471 rad/s. The [19,21), [29,31), [49,51) component means describe smooth extrema. Integral window [10,40) spans retained samples approximately 10.020–39.980 s. Corrected signed x -0.09964°, corrected absolute x 8125.010°, original indicated norm 8882.492°.
- The old auxiliary Nano [9,29) integral headline is omitted. The dedicated CC2541 and Voyager integration cases already establish the physical distinction with explicit local offset/window conventions. No new shared integration or cross-device fitted parameter is asserted.
- The plot converts CC2541/Voyager rates from rad/s to deg/s exactly for display; it does not change any prepared table. The integral table explicitly distinguishes component-offset corrections from the uncorrected norm.

### Magnetometer and current inversion

Primary reductions: `analysis/inertial.py`, `analysis/draft_adapters.py` and `analysis/draft_mechanics.py`.

- Nano norm statistics: [0,8), [22,28), [52,59) s; missing values remain excluded per channel without clock reassignment. Initial/reoriented/final means 46.173/45.203/46.136 µT. Four missing observations stay as plot gaps. Whole-record peak 162.596 µT at 32.940 s; reorientation change approximately-0.971 µT; return difference-0.0369 µT.
- CC2541: initial [0,15), reorientation [27,35), near magnet [42,44), return [53,60) s. Norm means 48.337/48.363/147.957/48.365 µT and SDs 0.133/0.117/3.085/0.119 µT. Whole-record peak 151.14 µT. The 0.055% reorientation comparison concerns the same example's norm consistency, not cross-device accuracy.
- Current: assigned levels 0, 0.1, 0.2, 0.3, 0.4, 0.2, 0 A. Canonical plateau windows [1,7),[9,15),[17,23),[25,31),[33,39),[41,47),[49,55) s. Endpoint reference means 30.07436396 µT and 49.95639995 µT at 0/0.4 A; field span 19.882036 µT and inverse sensitivity 0.020118664 A/µT. All seven residuals retained; largest withheld-state residual 2.352 mA.
- The first five ascending means give OLS intercept 30.0456292 µT, slope 49.7659944 µT/A and RMS mean residual 0.0226722 µT. This alternative fit is retained as an explicitly different linearity diagnostic. Pooled sample SD 0.357728 µT gives 7.197 mA single-reading scatter under the endpoint slope.
- Returned zero shift -0.116893 µT corresponds to -2.352 mA. A 1-µT background change corresponds to 20.1 mA at endpoint sensitivity. Protocol assignments are never called independent ammeter observations.
- The earlier pointwise derived-current regression is reduced to its conceptual circularity; its tiny floating-point residual is not retained as an impressive-looking numerical result.

## Literature selection

No new broad research or bibliography entries were required. Existing selected sources were verified in the prior topic research records; consolidation adds no new hardware specification or empirical literature claim.

- **Acceleration, six references:** Frosio2009 for gravity-constrained fitting; Geist2017 for intrinsic/alignment separation; ArduinoLSM9DS1 and STLSM9DS1 for the pinned scale/configuration; TI CC2541 quick guide and original phyphox CC2541 definitions for hardware/interface identity; covariance propagation is written explicitly without adding a generic GUM citation. The separate CC2541 article's Stančin2014/Tedaldi2014 citations are omitted because the selected gravity-calibration studies more directly establish this paper's model. The duplicate CC2541 wiki key is not carried twice.
- **Rotation, eight references:** Tedaldi2014 for vector calibration; ArduinoLSM9DS1/STLSM9DS1 for the known scale relation; CC2541 definitions for legacy conversion; Voyager manufacturer specifications and supported definition for identity/range/conversion; GUM for coefficient covariance; El-Sheimy2008 for averaging-time-dependent inertial noise. Repeated Stančin2014 and TI quick-guide entries are omitted here; no replacement broad methods citation is needed.
- **Magnetism, nine references:** Renaudin2010 and Kok2016 supply magnetic distortion/alignment models; ArduinoLSM9DS1/STLSM9DS1, CC2541 definitions and MAG3110 datasheet establish the two scales; original phyphox ammeter lesson establishes fixed-geometry current context; GUM and Bartel2016 address coefficient covariance and errors in the calibration coordinate. NIST's general straight-line web guidance is omitted because the retained physical intercept model and Bartel's primary calibration treatment suffice.

Each Markdown companion mirrors its canonical LaTeX argument, quantitative tables, equation ordering and figure captions, using numbered citations and linked human-readable references. It has no Draft boilerplate.

## Checks

Independent Luna verification recomputed canonical primary reductions and supplied a ledger of units, intervals and estimator cautions. Final source, compilation and rendering checks are recorded below. No experiment, example data, original analysis/report, generated data/figure, shared typography or bibliography is edited.


Final checks (all exit 0):

- `python3 output/motion/check_sources.py`: citation resolution, exact mapping, body/companion decimal-number parity, table/figure paths, captions and clean typesetting logs pass. All 57 recorded original-source snapshot hashes and all 58 example-input hashes match the unchanged reports.
- `latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=../../output/motion <slug>.tex`, from `docs/papers`, passes for all three canonical wrappers. Final page counts: accelerometer 2; gyroscope 3; magnetometer 3. No overfull boxes, undefined references/citations, missing glyphs or oversized-float diagnostics remain.
- `pdftoppm -png -r 105 output/motion/<slug>.pdf output/motion/<slug>` passes for every final PDF. All eight final pages were opened at readable scale and inspected. A final acceleration concision pass eliminated an orphan reference page without removing its equations, numerical results or physical distinctions. The comparative plots use readable common fonts and thicker 0.7-pt lines.
- Independent Luna audit recomputed dedicated primary windows/integrals and checked normalized plot columns and inference limitations. No blocking scientific issue or lost source case was found. The parent's separate reviewer has the final sources for independent review.
- Markdown companions were regenerated from the same article bodies, with matching tables, numbered equations/citations, linked human-readable references and figure captions. The name Schön is normalized in Markdown prose.

Frozen source paths and SHA-256 values are in `output/motion/frozen-sources.sha256` and `output/motion/frozen-sources.json`. PDF proofs and final build/check logs are in `output/motion/`. No new BibTeX entry or numerical analysis API was required. The eight source investigations remain registered through `analysis_ids`; no experiment, dataset, existing analysis, report or original figure has been deleted or modified.
