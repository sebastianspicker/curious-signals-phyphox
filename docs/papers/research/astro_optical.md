# Optical and astronomical revisions

Research date: 26 October 2026. This is a broad, topic-directed narrative review,
not a systematic-review claim. Each article was searched across its physical
forward model, calibration and uncertainty, inference, instrument documentation,
and related experimental work. Six substantive references are retained per
article. Existing analytical modules, original figures, inputs and experiment
definitions are unchanged. The new numerical reductions are in
`analysis/revision_astro_optical.py`; auxiliary paths are recorded in
`astro_optical-entries.json`.

## Albedo: directional surface comparison and spectral weighting

### Search and reading

Queries included `Nicodemus 1977 reflectance factor bidirectional NIST reference
substitution albedo`; `NIST reflectance measurement reference standard spectral
directional hemispherical`; `Heng Morris Kitzmann 2021 geometric albedos reflected
light phase curves arxiv`; `APDS-9960 spectral response`; and the original
astro-lab@home title. The literature was followed from radiometric definitions
through calibrated substitution to planetary phase integration. A separate
channel-response example was chosen because it exposes information lost by a
single broadband ratio without treating transmission as surface reflectance.

Selected keys and claims:

- **astrolab2022**: Spicker, Küpper and Bresges, *astro-lab@home—Bringing Science
  to the Sofa*, CAPjournal 31, 37–41 (October 2022). Read the original five-page
  institutional PDF, including its albedo/distance activity context:
  <https://physikdidaktik.uni-koeln.de/sites/physikdidaktik/Publikationen/CAPjournal_No-31_October-2022_astrolab-at-home_Bringing-Science-to-the-Sofa.pdf>.
  Used for the activity's experimental lineage, not a learning-effect claim.
- **nicodemus1977**: Nicodemus, Richmond, Hsia, Ginsberg and Limperis,
  *Geometrical Considerations and Nomenclature for Reflectance*, NBS Monograph
  160 (October 1977), DOI 10.6028/NBS.MONO.160. Read original definitions and
  section IV.F on reference standards, printed pp. 32–33:
  <https://nvlpubs.nist.gov/nistpubs/Legacy/MONO/nbsmonograph160.pdf>.
  Supports the distinction between directional, hemispherical and reference
  factors and the need to preserve throughput in substitution.
- **opt3001**: Texas Instruments, *OPT3001 Ambient Light Sensor*, SBOS681C,
  revised November 2017. Original manufacturer PDF description, optical
  characteristics and conversion-time fields read:
  <https://www.ti.com/lit/ds/symlink/opt3001.pdf>.
  Supports photopic weighting, not an unmeasured absolute calibration of the
  assembled apparatus.
- **barnes1998** (new): P. Yvonne Barnes, Edward A. Early and Albert C. Parr,
  *Spectral Reflectance*, NIST SP 250-48 (1998), DOI 10.6028/NIST.SP.250-48.
  Original report cover verifies author order (Barnes, Early, Parr); NIST's
  catalogue lists the same authors in another order. Read the original report's
  instrumentation, standards and measurement-equation context:
  <https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication250-48.pdf>.
  Sections 4.3–4.4, printed pp. 44–45, explicitly describe master/sample/master/background ordering, drift interpolation and scale transfer. Supports transfer from characterized reference standards and geometry-specific
  reflectance, rather than assigning unity to an arbitrary white surface.
- **apds9960**: Avago, *APDS-9960: Digital Proximity, Ambient Light, RGB and
  Gesture Sensor*, AV02-4191EN. Read original manufacturer RGBC characteristics,
  gain/integration controls and spectral-response figure:
  <https://docs.broadcom.com/doc/AV02-4191EN>.
  Supports overlapping channel weighting and controlled integration/gain.
- **heng2021**: Heng, Morris and Kitzmann, *Closed-Form ab Initio Solutions of
  Geometric Albedos and Reflected Light Phase Curves of Exoplanets*, Nature
  Astronomy 5, 1001–1008 (2021), DOI 10.1038/s41550-021-01444-7. Publisher page
  redirected to an inaccessible login; read the authors' full accepted-version
  text, especially equations 1–2 and 12:
  <https://arxiv.org/html/2103.02673v4>. Supports geometric/spherical/Bond
  distinctions, phase integral and reflected planet-to-star flux ratio. No
  numerical result from its exoplanet retrieval is transferred to the example.

Considered but excluded: NIST's current Reference Integrating Sphere description
(<https://www.nist.gov/laboratories/tools-instruments/reference-integrating-sphere-spectral-reflectance>),
read for a concrete directional–hemispherical implementation relative to PTFE;
it duplicates the selected metrology report. NIST SP 250-101 (2024) was considered
through its instrument/validation overview, but newer instrumentation details
would not change this example's inference. Hanssen et al., Applied Optics 57,
432 (2018), DOI 10.1364/AO.57.000432, was considered for sphere experimental
validation; its infrared sphere protocol is less directly relevant than the
selected spectral-reflectance reference. Generic uncertainty guidance was
removed from this article's citation list; the covariance derivatives remain
explicitly derived in the article.

### Numerical interpretation

Preserved original grey/black surface ratios and extrema statistic. The auxiliary
RGB reduction uses the actual device clock: dark [56,60), initial reference [4,6),
and red/green/blue windows [14,16), [24,26), [34,36) seconds. It recomputes ratios
from raw channel means, without silently substituting the pre-entered reference.
The red-window red/blue ratios are 0.882914/0.163547. The late [44,46)-s reference
changes 1.40–1.70% across channels. Smooth transitions are explicitly acknowledged;
the selected windows are not called asymptotic plateaux. The spectral integral
is a forward model, not a reconstruction of an unknown spectrum.

## Transit method: area, timing and model identification

### Search and reading

Queries included `Spicker Kupper 2024 exoplanet hunting classroom 5.0125305`;
`Mandel Agol 2002 analytic light curves planetary transit searches`;
`Kipping 2010 binning sinning finite integration`; `Kipping 2011 LUNA algorithm
exomoon planet overlap`; `stellar spots transit anomaly Oshagh 2013`; and
`Hamadani Campanelli PV characterization artificial low irradiance reference
solar cells`. These cover related classroom apparatus, uniform/nonuniform source
geometry, finite integration, extra silhouettes, spotted emission and electrical
photometry.

Selected keys and claims:

- **transit2024**: Spicker and Küpper, *Exoplanet Hunting in the Classroom: An
  Easy-to-Implement Experiment Based on Video-Aided Light Curve Analysis with
  Smartphones*, The Physics Teacher 62(3), 226–229 (2024), DOI
  10.1119/5.0125305. The publisher endpoint was inaccessible on retry. Read the
  first author's detailed account and reference list, including the source
  geometry, external-sensor alternatives and synchronized video rationale:
  <https://sebastianspicker.github.io/posts/exoplanet-hunting-smartphones/>.
  Journal metadata matched the existing reference and author bibliography.
  Retained for the original teaching experiment only; no claimed classroom
  efficacy or detector performance is imported.
- **mandelagol**: Mandel and Agol, *Analytic Light Curves for Planetary Transit
  Searches*, ApJ Letters 580, L171–L175 (2002), DOI 10.1086/345520. Read original
  author-hosted five-page paper, including model definitions and limb-darkening
  context: <https://faculty.washington.edu/agol/MandelAgol2002.pdf>.
  Supports the need for a source-intensity model beyond projected area.
- **kipping2010**: David M. Kipping, *Binning is Sinning: Morphological
  Light-Curve Distortions Due to Finite Integration Time*, MNRAS 408(3),
  1758–1769 (2010), DOI 10.1111/j.1365-2966.2010.17242.x. Read author full text,
  especially finite-integration/contact definitions and depth discussion:
  <https://arxiv.org/html/1004.3741>. Supports response convolution and the
  distinction between sampling and ingress resolution.
- **hamadani2020**: Hamadani and Campanelli, *Photovoltaic Characterization under
  Artificial Low Irradiance Conditions Using Reference Solar Cells*, IEEE
  Journal of Photovoltaics 10(4) (2020), DOI 10.1109/JPHOTOV.2020.2996241.
  Read original article text served in the indexed PMC record, including
  reference-cell methodology, spectral mismatch and I–V operating conditions:
  <https://pmc.ncbi.nlm.nih.gov/articles/PMC7808256/>. Direct later opens met the
  PMC challenge, so retained claims are confined to the already retrieved
  original text. PubMed metadata verified full title and Mark B. Campanelli's
  middle initial; the replacement BibTeX corrects these without guessing pages.
  Supports linear photocurrent versus arbitrary voltage normalization and
  spectral-response matching.
- **luna2011** (new): David M. Kipping, *LUNA: An Algorithm for Generating Dynamic
  Planet–Moon Transits*, MNRAS 416(1), 689–709 (2011), DOI
  10.1111/j.1365-2966.2011.19086.x. Publisher metadata read at
  <https://academic.oup.com/mnras/article/416/1/689/1216488>; original full author
  PDF read at <https://arxiv.org/pdf/1105.3499>. Supports mutual shadow overlap,
  limb darkening and dynamical timing as distinct ingredients. Window contrasts
  are not represented as an orbital moon detection or mass measurement.
- **oshagh2013** (new): Oshagh, Santos, Boisse, Boué, Montalto, Dumusque and
  Haghighipour, *Effect of Stellar Spots on High-Precision Transit Light-Curve*,
  A&A 556, A19 (2013), DOI 10.1051/0004-6361/201321309. Publisher metadata
  verified through the DOI; full author manuscript sections 2–3 read at
  <https://arxiv.org/html/1306.0739v2>. Supports upward spot-crossing anomalies
  and possible depth/duration/timing biases, without transferring the paper's
  scenario-dependent bias magnitudes to the lamp example.

Considered but excluded: Gordon and Agol's later exact two-body mutual-transit
model (2022), DOI 10.3847/1538-3881/ac82b1, read in the publisher's comparison to
LUNA. It would duplicate the overlap claim and require unnecessary derivatives
and numerical implementation detail. NASA discovery counts and exomoon news
stories were omitted: they neither constrain the bench model nor establish a
moon from an upward bump. Sensor datasheet and GUM citations were removed from
this article's lean bibliography while preserving the necessary weighting and
covariance discussion.

### Numerical interpretation

Original three-path depths, timing windows and figure remain unchanged. The four
new optical examples are independent scenarios. Each baseline is re-estimated
from stated receive-time windows, retaining the entered 10-count background as a
conditional assumption because no covered sequence is present. Nano baseline
115.26257 counts gives event depths 3.76446, 4.76197 and 4.39049%, mean 4.30564%
and projected radius ratio 0.207500. It does not silently reuse the entered
110-count baseline. Moon extra depth/overlap brightening are 2.81877/1.47652%;
spot anomaly 3.23632%; binary primary/secondary depths 30.97669/10.39769%.
All state/baseline windows and sample counts are machine-readable in the module.
No standard error based on thousands of correlated rows is reported. The source
brightness integral, mutual area and luminous-companion denominator explain why
these signals require different physical inversions.

## Owon interface: decoding, voltage calibration and optical loading

### Search and reading

Queries included `OWON B35T user manual DC voltage input impedance accuracy`;
`35 Series B35T Input impedance`; `Arduino analogReadResolution 10 bits`;
`nRF52840 SAADC source resistance calibration`; `phyphox Bluetooth notification
timestamp`; and the Hamadani artificial-light reference-cell title. The review
separates packet scaling, electrical reference transfer, finite input loading and
optical transduction rather than treating one successful conversion as all four.

Selected keys and claims:

- **phyphox2018**: Staacks, Hütz, Heinke and Stampfer, *Advanced Tools for
  Smartphone-Based Experiments: phyphox*, Physics Education 53(4), 045009 (2018),
  DOI 10.1088/1361-6552/aac05e. Read original author full text at
  <https://arxiv.org/html/1804.06239>, especially app and analysis sections.
  Supports acquisition/analysis context, not new BLE timing performance.
- **owon35**: manufacturer *Digital Multimeter User Manual: B35(T)(+), D35(T),
  B41T(+)*, canonical
  <https://files.owon.com.cn/probook/OWON_35_Series%26B41T_USER_MANUAL.pdf>.
  Canonical PDF timed out. Read the manufacturer's B35 manual text reproduced at
  <https://manualzz.com/doc/20182044/owon-b35-digital-multimeter-user-manual>,
  sections on DC polarity/ranges and technical specifications. The current
  manufacturer regional product table also confirms the DC range/accuracy:
  <https://www.owon.co.jp/products/b35-series/>. Verified 6.000-V range,
  ±(0.5% + 2 digits), 10-Mohm input and stated environmental conditions.
  The paper's ±7-mV illustration is a specification bound, not a standard
  uncertainty or a calibration result.
- **gum**: JCGM 100:2008, *Evaluation of Measurement Data—Guide to the Expression
  of Uncertainty in Measurement*, BIPM. Existing reference retained for joint
  calibration covariance, shared scale effects and resolution. The canonical PDF
  <https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf> timed out in
  this pass; the local previous research review records the official covariance
  section inspection. No new clause-specific claim depends on an unread section.
- **analogread**: Arduino, *analogReadResolution()* language reference. Read
  official content at
  <https://docs.arduino.cc/language-reference/pt/en/functions/analog-io/analogReadResolution>
  and the Nano-specific official language variant
  <https://docs.arduino.cc/language-reference/de/funktionen/analog-io/analogReadResolution>.
  Supports the distinction between requested output bits and actual ADC
  resolution. No assumption that supply voltage certifies internal reference.
- **phyphoxble**: official BLE format documentation, read notification/polling,
  conversion and time-input semantics:
  <https://phyphox.org/docs/file-format/bluetooth-low-energy/>. Supports the
  separation of notification delivery from physical conversion time.
- **hamadani2020**: original artificial-low-irradiance cell study described
  above. Here it earns a separate role: spectral responsivity, fixed electrical
  operating point and controlled optical transfer are required before a voltage
  dip can be interpreted as a light deficit.

Considered but excluded: independent hobbyist B35T reviews and distributor
tables, because the manufacturer manual and manufacturer regional table answer
the range/specification question. Nordic's nRF52840 specification was considered
for sample-and-hold source impedance, but no apparatus-specific numerical ADC
performance claim is needed and Arduino's primary documentation suffices for the
stated bit-width issue. The transit classroom citation was removed here because
the interface's own physical boundary is better served by calibration and
photovoltaic references.

### Numerical interpretation

Original staircase sign/scaling, fit and figure retained. The auxiliary original
three-channel analog example obeys 3.226 mV/count throughout, maximum residual
4.55e-13 mV. Ideal bin width for an explicitly conditional 3.3-V 10-bit ADC is
3.22265625 mV, whereas the Owon example digit is 1 mV. This compares numerical
granularity only; the two records are neither synchronized nor an empirical
instrument comparison. At 1 V the stated meter limit is 5 + 2 = 7 mV. No invented
source accuracy or photometric calibration is inferred.

## Infrared distance: irradiance, heat balance and radiometric scene

### Search and reading

Queries included `TMP007 calibration guide size source emissivity infrared
thermopile`; `TMP007 SBOS685C field of view calibration`; `de Lucas 2022 8284
radiation thermometers size source`; `inverse square photometry NIST reference
plane calibration`; `NIST SP 250-95 Zong`; and `Kopparapu 2013 habitable zones
stellar spectrum`. The search distinguishes geometrical irradiance dilution,
thermal equilibration and sensor angular coverage.

Selected keys and claims:

- **astrolab2022**: original activity lineage, read as above. No new
  habitability measurement is claimed.
- **tmp007**: Texas Instruments, *TMP007 Infrared Thermopile Sensor with
  Integrated Math Engine*, SBOS685C, revised July 2015. Manufacturer canonical
  <https://www.ti.com/lit/ds/sbos685c/sbos685c.pdf> and alternative TI endpoints
  were intermittently inaccessible. Manufacturer-indexed section 7.3.5 and
  specification content verified calibration for target geometry/emissivity,
  die sensing and object calculation; the calibration guide below supplies
  directly read primary full-text support. No disputed default-emissivity
  number from different revisions is asserted in the manuscript.
- **tmp007cal**: TI *TMP007 Calibration Guide*, SBOU142 (August 2014). Read
  full primary manufacturer document on TI's own archive:
  <https://e2echina.ti.com/cfs-file/__key/telligent-evolution-components-attachments/00-60-01-00-00-23-50-98/sbou142.pdf>.
  Sections 1–2 define object/die temperature, optical geometry, material,
  calibration range and environmental compensation; section 6 covers common
  calibration failures. Supports fixed scene and independent temperature
  reference, not generic blackbody accuracy for an arbitrary target.
- **delucas2022**: Javier de Lucas, *Measurement, Validation and Uncertainty of
  an Experimental Procedure to Characterize the Size-of-Source Effect of
  Radiation Thermometers, in the Framework of an Industrial Calibration
  Laboratory*, Sensors 22(21), 8284 (2022), DOI 10.3390/s22218284.
  Publisher page/PDF and browser PMC retries were blocked/rate limited.
  Retrieved the complete primary article XML through the Europe PMC archival API
  <https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9658027/fullTextXML>.
  Read the introduction, section 2.4 measurement process/model/uncertainty,
  results, discussion and conclusions. The procedure varies source aperture,
  repeats with realignment, and accounts for background/aperture effects.
  Metadata agree with <https://pubmed.ncbi.nlm.nih.gov/36365981/> and the publisher.
  Supports explicit size-of-source testing; no industrial high-temperature
  performance number is transferred to the TMP007 example.
- **zong2018** (new): Zong, Nadal, Tsai and Miller, *NIST Measurement Services:
  Photometric Calibrations*, NIST SP 250-95 (2018), DOI
  10.6028/NIST.SP.250-95. Metadata verified at
  <https://www.nist.gov/publications/nist-measurement-services-photometric-calibrations-0>.
  Read original government-hosted 147-page report, particularly section 3.6.1
  on photometer reference planes and close-source departures:
  <https://www.govinfo.gov/content/pkg/GOVPUB-C13-b9792684143ee5e8849d18ff822a8780/pdf/GOVPUB-C13-b9792684143ee5e8849d18ff822a8780.pdf>.
  Supports the physical distance origin and finite-source qualification.
- **kopparapu2013**: Kopparapu et al., *Habitable Zones around Main-Sequence
  Stars: New Estimates*, ApJ 765, 131 (2013), DOI
  10.1088/0004-637X/765/2/131 (existing reference includes the erratum).
  Read original author full text and radiative-convective model discussion:
  <https://arxiv.org/html/1301.6674>. Supports dependence on stellar spectrum,
  atmospheric absorption and climate assumptions rather than temperature alone.

Considered but excluded: IES inverse-square definition
<https://ies.org/definitions/inverse-square-law/> (useful confirmation of normal
incidence and finite-source caveat, but the NIST calibration treatment is more
specific); Ohno's 2017 photometry handbook chapter (duplicates the same law);
Gravely's 1973 photometry relations, DOI 10.1364/AO.12.002789 (a general
derivation adds no calibration insight beyond the selected report). No sensor
datasheet limit is substituted for an uncertainty in the example scene.

### Numerical interpretation

Original IR count coordinates, die/object statistics, branch separation and
figure retained. All twelve ruler-distance captures are used with their stated
10-count background; none is synchronized to the IR stream. Log–log OLS slope
is -1.986052627; separate outward/return slopes -1.987333310/-1.984771945.
An independent endpoint-pair ratio gives -1.983851006. The mean Sr² is
102.481667 count m², range 100.35–105.35 and relative sample SD 1.77709%.
This is an example optical shape, not absolute irradiance calibration. The
article derives the low-temperature-excess r^-2 limit and the radiation-dominated
high-temperature r^-1/2 limit from the energy balance and explains why neither
is established by the history-dependent IR sequence.

## Verification record

The extension is standard-library Python and returns only the four owned slugs.
Ruff formatting and linting, repeatable analysis execution, direct numerical
checks, temporary merged-bibliography LaTeX builds and all-page visual inspection
are recorded in the final handoff. Temporary build files remain inside this
isolated checkout; `references.bib` itself is not modified. Manuscript captions
retain “Example data.”; prose contains no input-format/build-origin narrative.

Final checks (26 October 2026): `ruff format --check` and `ruff check` on
`revision_astro_optical.py`, exit 0. Analysis execution and independent checks of
the log-slope normal equations, endpoint-pair slope, four RGB sum-based ratios
and B35 specification arithmetic, exit 0. Four `latexmk -pdf -interaction=nonstopmode
-halt-on-error` temporary-wrapper builds, each exit 0; no unresolved citation or
overfull warnings. All twelve PDF pages rendered with `pdftoppm -png -r 135`
(exit 0) and inspected individually at readable resolution. Baseline SHA-256
audit changes exactly the four owned manuscript bodies; all existing data, XML,
analysis, figures, source snapshots and shared bibliography are unchanged.

A read-only integration review identified inherited prose describing old
sample-index timing. The albedo and transit articles now distinguish the regular
example cadence from current notification-arrival timestamps: missed packets
leave gaps rather than compressing time. IR prose now states the actual
previous-report position pairing; its signed mouse increments are still
accumulated to two-axis coordinates whose norm is the displayed displacement.
These fidelity corrections do not change any numerical reduction.
