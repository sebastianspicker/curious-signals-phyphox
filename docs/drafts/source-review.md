# Source review and adaptation decisions

This collection follows a read-only review of `artikel-proofread-lectorate` on
26 October 2026. Source paths in the manuscripts and manifest are relative to
that folder. PDF page references use physical file pages; PowerPoint references
use slide order, which can differ from printed footer numbers. Repeated article
drafts, translations, graph layouts and hardware variants were compared without
counting them as separate scientific activities.

## Coverage

The inventory contained 815 files, including 251 DOCX, 172 PDF, 26 PPTX and nine
archives. Document text was extracted and screened; four image-only PDFs and a
Pages preview needed visual inspection. Relevant manuscripts, worksheets,
slides and experiment definitions were then read in detail. This was a search
for useful experiments, not a claim to have proofread every document.

There were 96 loose phyphox/XML variants and 25 archived phyphox occurrences,
representing 83 byte-distinct payloads. Every archived experiment duplicated a
loose file; no archive-only experiment was found. Eighty-two payloads parsed as
XML and 29 passed both contemporary official format schemas. The remaining
files included old attributes, version conflicts, missing calibration or
references, and one malformed XML. Format acceptance alone did not establish
scientific correctness. Archived scripts and firmware were inspected as text,
not executed.

## What became a draft

The workshop material supplied clear grounds for RGB transmission, exomoon
photometry, starspot crossings and detector characterization. Exomoon material
contains a developed apparatus and measured examples, although those source
measurements used a different acquisition platform. The new Nano implementation
is an adaptation. Starspot/RGB stations are less fully documented; their
manuscripts spell out the calibration and controlled comparisons required.

Published Malus-law studies support the optical relationship and apparatus
design. The supplied study used Physics Toolbox. The new phyphox draft combines
Nano light with entered protractor angles because the existing firmware cannot
stream its light and gyro modes simultaneously.

The seasons worksheets supply a distinct obliquity investigation. Its new draft
records illumination and geometry. It does not label solar-cell voltage or
light counts as a surface temperature. Eclipsing binaries were a concrete
workshop proposal; the draft retains that development status and does not infer
stellar masses or claim a validated mechanical model.

Useful XML families supplied inverse-square illumination, colour temperature,
first-slip friction, simultaneous sound/field acquisition and magnetic current
calibration. These received new acquisition or reduction logic rather than
cosmetic title changes. Nano transit and single-sensor warming extend existing
activities to useful hardware arrangements. Puck, environmental SensorTag and
legacy CC2541 adapters preserve their separate device contracts. The misleading
PocketLab One scaffold was replaced with the documented upstream Voyager path.

Pressure-dependent boiling, spectral fingerprints, UV transmission and
coronagraph contrast need equipment beyond the phone's ordinary sensors.
Their drafts use entered external observations or a real external detector on
Nano A0. They do not pretend that RGB provides a spectrum, a phone provides a
vacuum-compatible wet pressure probe, or phyphox performs image-region analysis.

## Corrections carried into the files

| Source issue | Draft behavior |
| --- | --- |
| RGB values divided by a moving maximum | Fixed measured dark/reference values and explicit validity gates |
| Sample-count clocks and assumed light/position correspondence | Acquired timestamps, separate asynchronous clocks and deliberate alignment |
| Friction angle captured before debounce or selected as a maximum | Armed settings, sustained valid onset and the first qualifying slip |
| Audio reduction tied to an assumed block length | Actual block size and sample rate; separate magnetic clock |
| Zero denominators and invalid domains | NaN guards that remain valid under native IEEE arithmetic |
| Repeated button writes assumed to append | Singleton pending snapshots, one-shot analysis appends and consistent clearing |
| CC2541 humidity offset of −24 | SHT21 relation with −6 percentage-point offset |
| Commented-out pressure coefficient reads | Active coefficient acquisition and an explicit verification/state workflow |
| Unsupported magnetometer or infrared absolute conversion | Raw data retained; physical output gated until device/application calibration |
| Puck reset and global timer replacement | Namespaced session timer at 4 Hz, without a reset or unrelated-timer clearing |

The source colour-temperature polynomial has a consistent sign convention:
`n = (x−0.3320)/(0.1858−y)` accompanies the positive cubic coefficients. It was
not “corrected” by reversing only one sign. The new file instead adds domain,
clipping and calibration controls.

For the exomoon model to return to the same moon phase after each planet orbit,
`Tplanet/Tmoon` must be an integer. Rational ratios can repeat after multiple
orbits. This corrects the reversed condition in the supplied proof's extension
discussion. Direct moon photometry and projected overlap are covered; no
transit-timing/ duration-variation method was recovered from that material.

## Already covered or not sufficiently developed

The existing fifteen experiments cover the older Nano plots, albedo, pressure
and thermal activities, Owon integration and ordinary transit variants. Their
basic/expert, translated, copied and archived versions did not justify extra
lessons. The old Nano sketch offers modes 1–6 and 9; it does not establish new
proximity or gesture modes.

References to ring transits, asteroseismology, stellar expansion/spin-up and
timing variations were not developed independent lessons in the reviewed
material. Sky-colour background, rocket/parachute design and general teaching
reviews could inspire future work, but would require new apparatus and methods.
Unrelated music-networking, teaching-research, editorial and administrative
documents were not converted into sensor activities.

## Attribution and reuse

The new companions are original English drafts. They cite the supplied material
for experimental ideas and evidence; the archive's article text, images and
measured curves are not republished here. Unlabelled donor XML was treated as a
description of behavior, not as a blanket license grant.

Original Curious Signals additions follow the repository's
[GPL-3.0 terms](../../LICENSE). The colour-temperature file retains the donor's
LGPL-3.0-or-later attribution to Spicker/Bouquet, the earlier Creutzer/Bouquet
work and McWethy's colour helpers; [COPYING.LESSER](../../COPYING.LESSER) and
[LICENSE](../../LICENSE) accompany the bundles. The Voyager packet adaptation
retains the upstream phyphox attribution to Dr. Sebastian Staacks, RWTH Aachen
University, under GPL-3.0. Individual manuscripts and XML comments identify
these specific sources. The existing core and astronomy attribution remains
unchanged.
