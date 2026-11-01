# Thermal and astronomical revisions — 26 October 2026

Scope: enrich the existing `greenhouse`, `mission-to-mars`, `pt-star` and
`tidal-locking` papers. The four original reductions and figures remain intact.
`analysis/revision_astro_thermal.py` supplies auxiliary calculations only. Article
text discusses the physics of the example data; no new physical experiment is
claimed. Each article selects six references. New entries are isolated in
`astro_thermal.bib`; existing entries are reused without changing shared files.

The queries below were made separately for the listed physical, instrumental,
uncertainty and teaching/astronomical questions. “Read” identifies content actually
opened, rather than treating a search result as evidence. Publisher metadata and
primary institutional/author versions were used to check authorship, title, date,
volume/pages, DOI and document revision where applicable. Access failures are
recorded explicitly. None of the excluded secondary pages supplies a manuscript
claim.

## Greenhouse

### Questions and search queries

- Enclosure heat balance versus atmospheric infrared transfer: `Wood 1909 Note on
  the theory of the greenhouse Philosophical Magazine 17 319 320`; `Wagoner Liu
  Tobin 2010 climate change shoebox greenhouse effect American Journal Physics`.
- Coupled heat loss and ventilation: `Boulard Baille 1993 simple greenhouse climate
  control model ventilation evaporative cooling pdf`.
- Sensor calibration and dynamic response: `thermal response BMP280 calibration
  temperature time constant`; `TMP007 SBOS685C pdf ti`; `Pierrehumbert Infrared
  radiation planetary temperature 2011 pdf`.
- Uncertainty: opened the official JCGM 100:2008, including the treatment of
  correlations and sensitivity coefficients.

### Candidates read and selected claims

1. **`bmp280`**, Bosch, *BMP280: Digital Pressure Sensor*, revision 1.26, October
   2021, BST-BMP280-DS001-26. Read the specification table, especially its
   temperature footnote, and measurement/filter sections. It establishes that the
   temperature channel responds to die/PCB self-heating and ambient conditions,
   rather than directly measuring enclosure air. Existing metadata confirmed at
   <https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf>.
2. **`boulard1993`**, T. Boulard and A. Baille, *A Simple Greenhouse Climate Control
   Model Incorporating Effects of Ventilation and Evaporative Cooling*,
   *Agricultural and Forest Meteorology* 65(3–4), 145–157 (1993),
   DOI **10.1016/0168-1923(93)90001-X**. Publisher route failed; read the authors'
   abstract and description of coupled linearized heat/water balances in the
   author-uploaded record at
   <https://www.researchgate.net/publication/222776668_A_simple_greenhouse_climate_control_model_incorporating_effects_of_ventilation_and_evaporative_cooling>.
   Retained for the modest claim that ventilation and radiative/sensible exchanges
   are coupled; no coefficients or validation performance are transferred.
3. **`wagoner2010`**, P. Wagoner, C. Liu and R. G. Tobin, *Climate Change in a
   Shoebox: Right Result, Wrong Physics*, *American Journal of Physics* 78(5),
   536–540 (May 2010), DOI **10.1119/1.3322738**. Read the author-hosted full text,
   especially the argon control and equations separating convection and radiation:
   <https://dl.tufts.edu/downloads/1c18dt418?filename=rr1728965.pdf>.
   Publisher metadata independently verified at
   <https://pubs.aip.org/aapt/ajp/article-abstract/78/5/536/1040040/Climate-change-in-a-shoebox-Right-result-wrong>.
   Selected for the concrete experimental lesson about competing heat-transfer
   mechanisms; its gas experiment is not claimed to be the same enclosure setup.
4. **`elyounsi2021`**, A. Elyounsi and A. N. Kalashnikov, *Ultrasonic Oscillating
   Temperature Sensor for Operation in Air*, *Engineering Proceedings* 10(1), 62
   (2021), DOI **10.3390/ecsa-8-11276**. Read apparatus, step-response results and
   conclusions in the institutional author manuscript:
   <https://shura.shu.ac.uk/29268/1/Kalashnikov-UltrasonicOscillatingTemperature(VoR).pdf>.
   This copy has provisional front-matter placeholders, so final bibliographic
   facts were verified separately at the publisher's conference record
   <https://sciforum.net/paper/11276> and issue listing
   <https://www.mdpi.com/2673-4591/10?issue=1>.
   Selected for observed differing transient responses of co-mounted BMP280/AHT20
   sensors, without adopting their offset correction or an intrinsic time constant.
5. **`gum`**, JCGM 100:2008. Read official treatment of model propagation and
   correlated input quantities at
   <https://www.bipm.org/utils/common/documents/jcgm/JCGM_100_2008_E.pdf>.
   Retained specifically for covariance of baseline-subtracted temperatures,
   rather than as a generic badge of uncertainty analysis.
6. **`pierrehumbert2011`**, R. T. Pierrehumbert, *Infrared Radiation and Planetary
   Temperature*, *Physics Today* 64(1), 33–38 (2011), DOI
   **10.1063/1.3541943**. Read the author article reprint at
   <https://courses.seas.harvard.edu/climate/eli/Courses/global-change-debates/Sources/CO2-saturation/more/Pierrehumbert-2011.pdf>.
   It explicitly identifies the original Physics Today article; the reprint has
   its own conference DOI, which is not substituted for the original citation.
   Selected for atmospheric wavelength-dependent radiative transfer.

### Exclusions and resulting revision

Wood's 1909 historical experiment was located and publisher metadata checked at
<https://www.tandfonline.com/doi/abs/10.1080/14786440208636602>, but Wagoner gives
more directly useful modern controls and quantitative heat-transfer reasoning.
Wood is therefore omitted. The astro-lab programme paper was read, but its general
context was redundant here and removed to keep six substantive references.
Unsourced sensor-forum offsets and climate polemics were excluded.

The single-sensor auxiliary example has baseline 22.70082 °C and late heating
28.03517 °C, hence a rise of 5.33435 K. Its 22 °C subtraction reference instead gives
6.03517 K: a baseline choice contributes 0.70082 K. A 2.61 K jump at switch-off
violates continuity for the proposed finite-capacitance cooling model. The article
therefore does not fit across it or compare unmatched heating amplitudes as though
they came from simultaneous conditions. A second sensor node explains why an
apparent fitted time constant need not be the enclosure time constant.

## Mission to Mars

### Questions and search queries

- Original design/teaching purpose: `Mission to Mars 10.0009109 Spicker 2022 pdf`;
  `Mission to Mars Spicker 47 pressure 2022`; `site:astro-lab.app Mission to Mars pdf`.
- Absolute versus gauge pressure and instrumental limits: official BMP280
  datasheet; official GUM covariance treatment.
- Water phase equilibrium: `IAPWS supplementary release saturation properties
  ordinary water substance 1992 2018`; `IAPWS saturation pressure -7.85951783
  647.096`.
- Martian environment: `Haberle McKay Schaeffer 2001 possibility liquid water
  present day Mars 106 E10`; `Mars fact sheet 6.36 millibars NASA surface pressure`.

### Candidates read and selected claims

1. **`mars2022`**, S. J. Spicker, A. Küpper and A. Bresges, *Mission to Mars—Concept
   and Implementation of a Design-Based (Hands-On) Smartphone Experiment Helping
   Students Understand the Effects Caused by Differences in Air Pressure*, *The
   Physics Teacher* 60(1), 47–50 (January 2022), DOI **10.1119/10.0009109**.
   Verified metadata and abstract; read the authors' primary nine-page teaching
   materials, especially the prototype pressure-retention assignment:
   <https://astro-lab.app/pdf/missiontomars_teaching-materials.pdf>.
   The publisher full-text route was unavailable. The article is retained for
   historical context only, not a claim of demonstrated learning gains.
2. **`bmp280`**, official revision 1.26, as above. Read specification limits and
   distinguish increment from accuracy. Selected for the 300–1100 hPa domain and
   die-temperature interpretation.
3. **`gum`**, official JCGM source as above. Selected for covariance of repeated
   plateau estimates and sensitivity-based propagation.
4. **`iapwssat1992`**, IAPWS *Revised Supplementary Release on Saturation Properties
   of Ordinary Water Substance*, **SR1-86(1992)**, September 1992. Verified official
   document identity and revision history:
   <https://iapws.org/technical-guidance/release/Supp-sat> and
   <https://iapws.org/public/documents/6dGkr/Supp-sat.pdf>.
   The seven-page PDF's text extraction exposes only its identifier. Checked the
   saturation relation and six coefficients against the primary NIST authors'
   reference-formulation review, section 5.4, equation 3 and table 2:
   <https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=935265>.
   The code implements the six-term relation on 273.16–647.096 K and bounded
   inversion; it does not extrapolate stable liquid coexistence below the triple
   point. The release is the selected reference; the review is redundant in print.
5. **`haberle2001`**, R. M. Haberle, C. P. McKay, J. Schaeffer, N. A. Cabrol,
   E. A. Grin, A. P. Zent and R. Quinn, *On the Possibility of Liquid Water on
   Present-Day Mars*, *JGR: Planets* 106(E10), 23317–23326 (2001), DOI
   **10.1029/2000JE001360**. Read the primary publisher abstract and conclusions
   about minimum pressure/temperature requirements and evaporative constraints:
   <https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2000JE001360>.
   Selected for the limited inference that favorable thermodynamic coordinates
   alone do not establish sustained liquid water.
6. **`nasamarsfacts`**, D. R. Williams, *Mars Fact Sheet*, NASA Goddard/NSSDCA.
   Read the atmosphere table and author/curator footer:
   <https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html>.
   Selected for the explicitly defined 6.36-mbar surface pressure at mean radius,
   with its seasonal variation. No invented publication year is supplied.

### Exclusions and resulting revision

The generic phyphox reference adds no new pressure physics and is removed.
ESA's Mars fact sheet was checked but duplicates NASA's pressure reference; NASA
states the reference radius and variation more explicitly. A NASA astrobiology
news story was considered but excluded in favor of Haberle's research paper.
An Antoine curve is not fitted to arbitrary liquid/uncertain observations.

Only five checked sustained-boiling states enter the saturation comparison. Their
residual RMS is 0.25118 K; the 39.922-kPa point is −0.45852 K from saturation,
compared with an independent-input combined standard uncertainty of 0.20886 K.
The full auxiliary range is 5.039–101.183 kPa, not Martian pressures. The lowest
value is 7.923 times the NASA reference pressure, and the BMP280 lower specified
limit is 47.17 times that reference. IAPWS gives 0.548 °C saturation at 0.636 kPa,
close to its triple point. Mechanical pressure differences and absolute-pressure
phase conditions are explicitly separated.

## Compression and star formation (`pt-star`)

### Questions and search queries

- Thermodynamic path and teaching comparison: `adiabatic compression gas smartphone
  thermometry pressure heat capacity ratio Physics Education experiment`;
  `An Arduino-Based Experiment Designed to Investigate Gas Pressure DOI`;
  `Complete Cycle Experiments Using the Adiabatic Gas Law Apparatus DOI`.
- Sensor response/calibration: `thermal response BMP280 calibration temperature
  time constant`, official BMP280 specification, official GUM.
- Collapse and energy loss: `Larson 1969 numerical calculations dynamics collapsing
  proto star 145 271`; `Bhandare Ahmad Commercon Turn up light radiative efficiency
  protostars birth 2025`.

### Candidates read and selected claims

1. **`star2020`**, S. J. Spicker and A. Küpper, the existing September 24, 2020
   teacher-development lecture. Its archival URL
   <https://astro-lab.app/pdf/Spicker-und-Kuepper_Sternentwicklung_LeFoBi-2020_150ppi.pdf>
   returned HTTP 503 on two attempts. This existing historical citation is
   retained unchanged and used only to identify the associated workshop; no new
   scientific or educational efficacy claim is based on it. Its re-verification
   remains an access limitation, rather than a newly verified source.
2. **`bmp280`**, read official specification/temperature footnote; selected for the
   chip-versus-gas distinction and pressure range.
3. **`elyounsi2021`**, full author manuscript and final publisher bibliographic
   record read as documented above. Selected for observed dynamic disagreement
   among co-mounted temperature sensors. Its setup-specific bias is not adopted.
4. **`gum`**, read official input-covariance and sensitivity treatment; selected for
   the joint pressure–volume–gas-temperature measurement model.
5. **`larson1969`**, R. B. Larson, *Numerical Calculations of the Dynamics of a
   Collapsing Proto-Star*, *MNRAS* 145(3), 271–295 (August 1969), DOI
   **10.1093/mnras/145.3.271**. Publisher metadata and research abstract read at
   <https://academic.oup.com/mnras/article/145/3/271/2602795?login=false>;
   author's publication index checked at <https://www.astro.yale.edu/larson/pubs.html>.
   Publisher PDF was inaccessible. Selected for nonhomologous collapse and core
   formation; the cooling/opacity sequence was also read directly in Bhandare's
   introduction, which explicitly develops Larson's result.
6. **`bhandare2025`**, A. Bhandare, A. A. Ahmad and B. Commerçon, *Turn Up the Light:
   Radiative Efficiency of Protostars at Birth*, *Astronomy & Astrophysics* 702,
   L7 (2025), DOI **10.1051/0004-6361/202556128**. Read the authors' accepted
   manuscript, especially introduction, radiative efficiency definition and
   radiation-hydrodynamic results:
   <https://arxiv.org/html/2509.15009v1>.
   Verified title/authors/accepted date and linked journal record. Selected for
   radiative versus retained accretion energy, without importing its numerical
   efficiencies into the laboratory analogy.

### Exclusions and resulting revision

Salar's *An Arduino-Based Experiment Designed to Investigate Gas Pressure*, *TPT*
59(3), 202–203 (2021), was considered through its abstract and publisher search.
Its claim that the pressure chip removes the need for separate thermometry does
not resolve the dynamic gas-temperature inference here; not selected. Kutzner and
Plantak's *Complete Cycle Experiments Using the Adiabatic Gas Law Apparatus*
(2014) was considered through the primary institutional abstract at
<https://digitalcommons.andrews.edu/physics-pubs/11/>; full cycle calorimetry is
beyond these endpoints, so not selected. A university piston demonstration was
read at <https://atoc.colorado.edu/TeachingandLearning/Demonstrations/AdiabaticExpansion/Adiabatic_expansion.htm>;
its explicit small-mass thermometer, volume and pressure channels reinforce the
apparatus requirements but add no necessary seventh reference. General star
formation reviews were excluded in favor of Larson and the recent primary study.

The pressure ratio 1.074614 is compatible with conditional isothermal and reversible
adiabatic volume ratios 0.930567 and 0.949898 respectively. With an assumed initial
gas temperature 296.55 K, the latter predicts 6.1603 K warming. The observed 1.40-K
die rise cannot select the path. Using the die as gas temperature would give a
third answer, 0.934961. The later pressure decrease would require 0.69593 K cooling
at fixed amount/volume under the stated 297.95-K initial assumption; die cooling
is 0.00267 K. The distinction is integrated into the competing-path analysis,
rather than presented as evidence of leakage or a measured gas-temperature lag.

## Tidal locking and seasonal illumination

### Questions and search queries

- Rotation and obliquity: `Dobrovolskis 2009 Insolation exoplanets eccentricity
  obliquity Icarus`; `Insolation patterns on synchronous exoplanets with obliquity
  pdf`; `Insolation patterns synchronous NASA pdf`.
- Planetary heat balance: `A Scaling for Atmospheric Heat Redistribution Koll 2022
  arxiv`; `Wirth Powell Analytic Modeling 2026 ae3da9`.
- Sensor interpretation/calibration: official BMP280, TMP007 and OPT3001
  datasheets; `TMP007 SBOS685C pdf ti`; TMP007 calibration guide.
- Teaching context: original astro-lab programme article and its tidal-locking
  section, as opposed to general planetary-climate news.

### Candidates read and selected claims

1. **`astrolab2022`**, S. J. Spicker, A. Küpper and A. Bresges, *astro-lab@home—
   Bringing Science to the Sofa*, *CAPjournal* 31, 37–41 (October 2022). Read
   especially the tidal-locking activity on page 38 and its description of
   permanent illuminated/shaded regions:
   <https://physikdidaktik.uni-koeln.de/sites/physikdidaktik/Publikationen/CAPjournal_No-31_October-2022_astrolab-at-home_Bringing-Science-to-the-Sofa.pdf>.
   Selected for historical activity context only.
2. **`bmp280`**, official revision 1.26 read; selected for die temperature rather
   than planetary surface temperature.
3. **`tmp007`**, TI *TMP007 Infrared Thermopile Sensor with Integrated Math Engine*,
   SBOS685C, July 2015. Primary TI indexed PDF content at
   <https://www.ti.com/lit/ds/sbos685c/sbos685c.pdf> verifies final revision and
   characterization; direct opens failed. Read field-of-view, calibration and
   transient-correction sections from the earlier TI revision B text (mirrored at
   <https://studylib.net/doc/25238392/tmp007>), and final-revision indexed text
   concerning board coupling. Selected only for sensor operating principles:
   thermopile plus die temperature, viewing geometry and emissivity dependence.
   No final-revision numerical accuracy specification is inferred from rev B.
4. **`opt3001`**, TI *OPT3001 Ambient Light Sensor*, SBOS681C, November 2017.
   Read official description and spectral-response/specification sections:
   <https://www.ti.com/lit/ds/symlink/opt3001.pdf>.
   Selected for photopic weighting and infrared rejection: lux cannot be assumed
   to represent absorbed broadband power.
5. **`dobrovolskis2011`**, A. R. Dobrovolskis, *Insolation on Exoplanets with
   Eccentricity and Obliquity*, EPSC Abstracts 6, EPSC-DPS2011-136 (2011). Read
   the full primary two-page meeting contribution, including substellar tracks,
   dependence on rotation/longitude and polar-insolation equations:
   <https://meetingorganizer.copernicus.org/EPSC-DPS2011/EPSC-DPS2011-136.pdf>.
   Selected for the dependence of insolation on spin/orbit/obliquity geometry.
6. **`koll2022`**, D. D. B. Koll, *A Scaling for Atmospheric Heat Redistribution on
   Tidally Locked Rocky Planets*, *ApJ* 924(2), 134 (2022), DOI
   **10.3847/1538-4357/ac3b48**. Read author's full manuscript, especially heat
   redistribution, weak-temperature-gradient balance and dependence on pressure
   and optical thickness: <https://arxiv.org/html/1907.13145v2>.
   Author publication index confirms journal metadata:
   <https://danielkoll.github.io/publications/>.
   Selected to connect the two-node laboratory balance to the processes absent
   from it; its planetary scaling is not fitted to the bench temperatures.

### Exclusions and resulting revision

Dobrovolskis (2009), *Insolation Patterns on Synchronous Exoplanets with Obliquity*,
*Icarus* 204(1), 1–10, DOI **10.1016/j.icarus.2009.06.007**, was identified and
publisher metadata/abstract verified; full publisher access failed (403).
The fully accessible 2011 primary contribution covers the required claim and is
selected instead. Wirth, Powell and Wordsworth (2026), DOI
**10.3847/1538-4357/ae3da9**, was checked through the primary manuscript
<https://arxiv.org/html/2601.12556v1> (abstract/intro: limits of weak-temperature-
gradient approximations). It is useful for specialist atmospheric retrievals, but
Koll already supplies the physical contrast needed here, so Wirth is omitted to
leave room for obliquity geometry. TMP007 calibration-guide access failed; no
application-specific calibration coefficient is asserted. General exoplanet and
climate summaries are not used.

The enabled labeled observations at ±60° show northern/southern responses
(0.514,0.522) and (0.189,0.188) at zero tilt, then (0.453,0.450) and (0.112,0.105)
at 23.5° tilt for the two orbital labels. They do not exhibit the ideal
solstitial hemispheric reversal; positional response already changes at zero
tilt. The article states which geometry is missing rather than assigning the
change to obliquity. The ideal local-noon ratio for ±60° latitude and 23.5°
declination is 7.101, computed independently of the detector data. Normalized
counts are not converted to the older lux ratio or thermal contrast.

## Reproducibility and verification

`revision_astro_thermal.analyze(data_root)` returns four JSON-serializable metric
dictionaries. It reads only current input data, retains independent clocks, uses
explicit half-open windows, and records conditional physical assumptions. No new
figure/table data products are required: original plots remain unchanged, and
the two compact auxiliary tables are direct presentations of these metrics.
`astro_thermal-entries.json` records only actual auxiliary source datasets for
manifest integration.

Validation results and exact commands are appended after the final rendering pass.

Final checks (all in the isolated `astro_thermal` copy):

- `python3 docs/papers/analysis/revision_astro_thermal.py example-data` — exit 0;
  strict JSON serialization also passed. Metrics retained under
  `output/revision-metrics.json` for review.
- `ruff check docs/papers/analysis/revision_astro_thermal.py` — exit 0.
- `ruff format --check docs/papers/analysis/revision_astro_thermal.py` — exit 0.
- Independent numeric checks (Python inline check, exit 0): saturation at
  373.15 K agrees with 101.418 kPa within 0.001 kPa; inversion at 101.325 kPa
  agrees with 373.1243 K within 0.001 K; triple point agrees with 0.611657 kPa
  within 0.000001 kPa. Pressures −1, 0.5 and 25000 kPa are rejected by the
  stable saturation-domain inversion. An independent named-column reader and
  the alternate adiabatic temperature–volume relation reproduce the conditional
  compression endpoints. Analytic differentiation of log saturation pressure
  reproduces all five propagated uncertainties within 0.00001 K, independently
  of the numerical pressure-perturbation calculation.
- Byte comparisons of all 58 original/new example CSVs, original thermal and
  environment analysis modules, and the four original figure sources against
  the source checkout — exit 0 (64 unchanged inputs/products in total).
- Local temporary wrappers `revision-check-<slug>.tex` use the temporary merged
  `revision-check.bib`; `references.bib` remains untouched. For each of four
  slugs, `latexmk -pdf -interaction=nonstopmode -halt-on-error
  -outdir=../../output/revision-check revision-check-<slug>.tex` from `docs/papers`
  — exit 0. All papers are three pages, each with six references. Final logs
  have no undefined citations/references, missing glyphs, oversized floats or
  overfull boxes.
- `pdftoppm -scale-to 1400 -png <PDF> <prefix>` — exit 0 for each PDF. All twelve
  pages were visually inspected with `view_image`, including schematic labels,
  all original data panels, both new auxiliary tables and reference lists.
  The final page is shorter than the earlier pages but has no collision or
  clipping.

Read-only scientific review identified inherited acquisition wording that
conflicted with the current experiment timestamp semantics. All four manuscripts
now describe the uniform example grids separately from the actual per-channel
acquisition timestamps needed for physical transient inference. No experiment,
source data, original analysis or plot was changed.

The working copy is a source copy without `.git`; `git status --short` therefore
returned exit 128. No main-checkout or shared-file write was made. The access
limitations for retained historical references above remain disclosed; the new
quantitative analysis does not depend on unavailable workshop content.

Source-location clarification for the transient claim: in the Elyounsi and
Kalashnikov author manuscript, original article page 3 identifies the co-mounted
AHT20/BMP280 arrangement immediately before Figure 4; article page 4, section 3,
discusses the divergent step responses in Figures 7–8, and article page 5 discusses
the transient differences shown in Figures 9–11. The institutional PDF adds a
cover sheet, making those PDF pages 4–6 respectively (one-based). The primary
conference manuscript at <https://sciforum.net/paper/download/11276/manuscript>
contains the same apparatus and result paragraphs. These full-text locations,
not the shorter Sciforum abstract, support the manuscript claim.
