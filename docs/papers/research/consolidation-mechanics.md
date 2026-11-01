# Mechanics consolidation record — 27 October 2026

The authoritative mapping retains `static-friction` and `audio-magnetic` as separate canonical topics, each with one source analysis ID. Their physical questions differ from the calibration papers: the first identifies a contact-state transition, while the second compares motor-state contrasts across two observables. `magnetic-current` belongs to the consolidated magnetometer article and is outside this edit. Existing analysis modules, numerical reports, data, experiment XML, original research logs and bibliography remain unchanged.

## static-friction

Retain the first-valid-event estimator: arm at5s; linear-acceleration threshold1.0m/s²; sustain0.15s; sampling-gap limit0.15s; query inclination0.10s before the most recent low sample; previous gravity reading must be at most0.20s old with magnitude9.3–10.3m/s² and angle0–85°. A gap cannot count as an actual low-acceleration observation. Later impacts do not replace the first valid event.

Canonical results remain the dedicated `draft_mechanics` reduction: last low19.9820467s, first high20.0019916s, confirmation20.1420557s, selected gravity19.8819076s, angle25.1043064°, μ0.4685259. Retain the diagnostic straight-line fit over5–19.8s (RMS residual0.934°), local19–19.8s slope0.475°/s and residual scatter0.110°, timing sensitivity0.057°, coefficient scatter scale0.0023, and1° mounting sensitivity0.021. The25–29s plateau is a consistency comparison, not a replacement critical angle.

Edits reduce repeated discussion of contact history and duplicate generic caveats. The opening states why the first slip belongs to the prepared contact. The final interpretation now explicitly distinguishes acceleration detection from motion detection: uniform sliding has zero acceleration, so absence of a trigger cannot establish rest. This is a consequence of the same mechanics model, not a new reduction. A rigid phone mount is described without an unnecessary magnetic-material constraint. Timing and mounting uncertainty remain next to their relevant estimates.

References retained: `astmg2192024` for the operational breakaway definition; `baldock2016` for the distinct kinetic-friction inference; `dieterich1979` for contact-history motivation without transferring rock parameters; `geist2017` for mounting/sensor-response distinctions. No new references or uncertain scientific claims required browsing. Previously considered interface-front and general teaching references remain omitted because these observations do not resolve those phenomena.

## audio-magnetic

Retain separate measured time axes and independently select left-closed/right-open1–9,11–19,21–29,31–39,41–49,51–59s windows. Each contains80 audio blocks and159 magnetic readings. Compute sample-count-weighted mean square before the logarithm; all example rates are48000s⁻¹ and each block has4800 samples. Preserve the distinction between sample weighting and time weighting when rates vary.

Canonical results remain mean three-cycle energy-level contrast11.5562532dB (cycle SD0.0320519dB) and magnetic mean-magnitude contrast4.0264897µT (cycle SD0.0388130µT). Retain first-cycle aggregate RMS0.01190/0.04506, the0.129dB energy-versus-arithmetic-level difference, and vector change(2.009,−1.183,3.519)µT. The magnetic table/equation now distinguish the difference of mean magnitudes from the magnitude of the difference between mean vectors explicitly; values4.040/4.222µT for cycle1 are unchanged.

Edits remove repeated statements about fault diagnosis, efficiency and generic information limits. They sharpen the rotation argument: a rigid rotation preserves the true norm of a uniform field, whereas offset/axis-response errors can make the indicated norm orientation dependent. The one-second boundary exclusion is explicitly conditional on channel latency being smaller than that margin; no latency is inferred. Keep601 audio blocks/1201 magnetic readings and the40 sub-noise blocks: corrected zeros are unresolved amplitudes, not exact silence. Noise inversion, background stability, gain dependence and lack of waveform/phase information retain their physical roles.

References retained: `liu2017stray` for analogous state information in motor stray fields; `kok2016` for orientation/calibration effects; `iec61672` and `kardous2016` for acoustic-level/calibration distinctions; `phyphoxinputs2026` for actual rate/block timing semantics. No extra generic calibration references are added. No new bibliography entries are needed.

## Publication and checks

Both wrappers retain their titles and shared typography, with `flafter` controlling float order. A controlled column break keeps the final motor-state interpretation paragraph intact. Each article retains its apparatus schematic, one two-panel data figure, and quantitative table. Full canonical Markdown lives under `companions/` without editorial-status boilerplate; numbered citations link to human-readable references, and figure links resolve through `../../../output/pdf/`.

Verification uses the unchanged dedicated analysis API and numerical report, checks canonical values independently, compiles each wrapper directly, scans final logs, and renders every final PDF page. Final hashes and page counts are reported to the parent with proof locations. No edits to shared preparation/build/analysis sources are required.

Final verification: direct `latexmk -pdf -interaction=nonstopmode -halt-on-error` compilation exits0 for both wrappers; each PDF has2pages. All4 final pages were rendered at125dpi and inspected, with no clipping or overlaps. Final logs contain no Overfull/Underfull, undefined-reference/citation, Warning or Error diagnostics. Both unchanged analysis reductions equal their canonical numerical reports exactly; independent tangent/contrast checks, mapping/metadata and reference-key checks pass (exit0). The SHA256 manifest is reported separately so it does not hash itself.
