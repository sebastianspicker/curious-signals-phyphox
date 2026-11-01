# Literature selection

The expanded forty-three-paper edition has a [topic research index](research/README.md)
covering the new companions and the latest revisions to the original fifteen.
The earlier search record below is retained for continuity; the current articles
and bibliography determine which references appear in the edition.

Searches and source checks for the October 2026 revision. Each short paper retains only references used in its argument. This file records the broader review and the reasons for selection.

Editorial convention: state the reported findings directly. Describe a missing
measurement or procedure only when the record establishes its absence; otherwise
state the relevant model assumption without implying that work was not performed.
Unavailable original data limit independent reproduction; they do not establish
that reported results are synthetic, hypothetical or fabricated. Distinguish
repository demonstration data from the provenance of the reported studies.
Keep internal build and checksum commentary out of manuscripts.
Figure and table captions name the observable, comparison and statistic directly.
State necessary calibration or model assumptions through the definition of the
reported quantity; avoid generic example labels and repeated defensive contrasts.


## Inertial


Searched 26 October 2026. This is a narrative literature search, not a systematic review. The selection spans primary calibration methods, recent alternatives, manufacturer specifications, the pinned acquisition implementation, and measurement-uncertainty guidance. Manuscripts retain six references for acceleration, six for angular rate and five for magnetic field.

### Search queries

- `accelerometer calibration multi-position static orientation calibration 2023 2024 MEMS paper`
- `gyroscope calibration MEMS rate table bias Allan variance 2024 2025 paper`
- `magnetometer calibration ellipsoid identifiability rotation ambiguity 2024 paper`
- `LSM9DS1 datasheet 0.122 70 0.14 mgauss Arduino library`
- `Tedaldi Pretto Menegatti 2014 robust easy implement method IMU calibration without external equipments DOI`
- `Frosio Pedersini Borghese 2009 autocalibration triaxial accelerometers DOI`
- `Kok Schon magnetometer calibration inertial sensors maximum likelihood 2016 IEEE sensors DOI`
- `El-Sheimy Hou Niu 2008 analysis modeling inertial sensors Allan variance 2008 DOI`
- `site.nist.gov "Gravity-Based Characterization" "Geist"`
- `"Three-dimensional magnetometer calibration" Cowart Petrich 2024 2025 104903`
- `site.sciencedirect.com "Three-dimensional magnetometer calibration" "186" "2025"`

### Selected primary sources

1. STMicroelectronics, *LSM9DS1: iNEMO inertial module*, DocID025715 Rev.3, March 2015. Manufacturer PDF: https://www.st.com/resource/en/datasheet/lsm9ds1.pdf . Table 3 verifies the 0.122 mg/LSB accelerometer, 70 mdps/LSB gyroscope, and 0.14 mgauss/LSB magnetometer sensitivities. The datasheet's nominal figures are not individual calibration results.

2. Arduino, pinned *Arduino_LSM9DS1 1.1.1*, `LSM9DS1.cpp`: https://raw.githubusercontent.com/arduino-libraries/Arduino_LSM9DS1/1.1.1/src/LSM9DS1.cpp . Opened and inspected the primary source: configuration lines 67–71; conversion lines 112–114, 150–152 and 182–184; sample rates lines 134–136, 166–168 and 197–199. The firmware's notification cadence is independently obtained from the local firmware. Keep this citation because it explains the gyro and magnetic scale mismatch; it is not implementation trivia.

3. I. Frosio, F. Pedersini and N. A. Borghese, “Autocalibration of MEMS accelerometers,” *IEEE Transactions on Instrumentation and Measurement* 58(6), 2034–2041 (2009), DOI https://doi.org/10.1109/TIM.2008.2006137 . University author record and abstract: https://air.unimi.it/handle/2434/141904 . Establishes static norm-based bias, sensitivity and symmetric cross-axis calibration.

4. J. Geist, M. Y. Afridi, C. D. McGray and M. Gaitan, “Gravity-Based Characterization of Three-Axis Accelerometers in Terms of Intrinsic Accelerometer Parameters,” *Journal of Research of NIST* 122, article 32 (2017), DOI https://doi.org/10.6028/jres.122.032 . Official publication record: https://www.nist.gov/publications/gravity-based-characterization-three-axis-mems-accelerometers-terms-intrinsic . NIST's volume index confirms exact published title without MEMS: https://www.nist.gov/nist-research-library/journal-research-nist/journal-research-nist-volume-122 . Explains why a calibration matrix depends on mounting orientation. Replaces vague claims that norm calibration alone certifies laboratory axes.

5. S. Staacks, S. Hütz, H. Heinke and C. Stampfer, “Advanced tools for smartphone-based experiments: phyphox,” *Physics Education* 53(4), 045009 (2018), DOI https://doi.org/10.1088/1361-6552/aac05e . Retained once in the acceleration manuscript for acquisition context, rather than repeatedly in all three papers. Publisher robots blocked a fresh open; bibliographic metadata matched the existing collection reference and public search results. No new technical sensor claim rests on this paper.

6. D. Tedaldi, A. Pretto and E. Menegatti, “A robust and easy to implement method for IMU calibration without external equipments,” *ICRA 2014*, 3042–3049, DOI https://doi.org/10.1109/ICRA.2014.6907297 . Author-hosted primary paper indexed at https://albertopretto.altervista.org/papers/tpm_icra2014.pdf ; author bibliography https://albertopretto.altervista.org/print.php?mod=01_Research . Search engine provided full first-page introduction/abstract; direct PDF retry timed out. The author bibliography contains a first-initial typo for Tedaldi; use the actual paper's David Tedaldi. Retained to connect reversal calibration to well-established complete IMU calibration.

7. N. El-Sheimy, H. Hou and X. Niu, “Analysis and Modeling of Inertial Sensors Using Allan Variance,” *IEEE Transactions on Instrumentation and Measurement* 57(1), 140–149 (2008), DOI https://doi.org/10.1109/TIM.2007.908635 . Publisher indexed full abstract and metadata verified. Retained for interpretation of longer stationary stability records; the manuscripts do not fit Allan coefficients to the short moving CSV.

8. Z. Yampolsky and I. Klein, “Data-Driven Gyroscope Calibration” (2024), arXiv https://arxiv.org/abs/2410.12485 , DOI https://doi.org/10.48550/arXiv.2410.12485 . Opened original author submission, abstract and revision history. Cited explicitly as a preprint rather than inventing a journal publication. This recent alternative uses a turntable-based reference dataset; no claimed performance is transferred to the LSM9DS1 example.

9. M. Kok and T. B. Schön, “Magnetometer Calibration Using Inertial Sensors,” *IEEE Sensors Journal* 16(14), 5679–5689 (2016), DOI https://doi.org/10.1109/JSEN.2016.2569160 . Opened author submission https://arxiv.org/abs/1601.05257 ; original journal metadata and authors verified there. Provides calibration with alignment and magnetic disturbances.

10. J. Cowart III and J. Petrich, “Three-dimensional magnetometer calibration using higher order models embedded into neural networks,” *Robotics and Autonomous Systems* 186, 104903 (April 2025), DOI https://doi.org/10.1016/j.robot.2024.104903 . Publisher indexed abstract and issue metadata: https://www.sciencedirect.com/science/article/abs/pii/S0921889024002872 . DOI suffix is 2024, but issue year is 2025. Publisher search result explicitly confirms volume 186 and April 2025. Direct fetch returns 403; claims are restricted to the indexed original abstract/conclusion: higher-order polynomial models, model complexity and rotational ambiguity. This is the recent calibration extension cited in the magnetic paper.

11. JCGM, *Evaluation of measurement data—Guide to the expression of uncertainty in measurement*, JCGM100:2008, DOI https://doi.org/10.59161/JCGM100-2008E . Official current publication list: https://www.bipm.org/en/committees/jc/jcgm/publications . Retained for covariance-aware propagation. The official list also records the 2026 nonlinearity amendment and newer model-development guide; manuscript uses the general covariance framework and flags breakdown near zero norm without claiming first-order propagation is universal.

### Sources considered but omitted

- 2026 multi-orientation accelerometer conference paper, DOI 10.1109/AQTR70159.2026.11577881: original publisher abstract verified, but a further offset/sensitivity method would duplicate the two complementary static-calibration references already retained.
- 2024 *Enhancing Accuracy in Actigraphic Measurements: A Lightweight Calibration Method for Triaxial Accelerometers*: university-hosted PDF discovered, direct fetch timed out. Activity-specific calibration adds no essential claim to this short general inclination paper; not cited.
- 2026 temperature self-calibrated gyroscope, https://pmc.ncbi.nlm.nih.gov/articles/PMC13006449/ : primary research concerns a specialized control architecture rather than an accessible LSM9DS1 calibration. Its high-performance bias figures do not apply here.
- 2024 gyroscope noise-mechanism research, DOI 10.1109/JSEN.2024.3435482: useful specialized device physics, but the short paper needs a general stability interpretation rather than detailed mode-split tuning.
- 2024 MAGYC preprint https://arxiv.org/abs/2412.09690 and SLAM calibration https://arxiv.org/abs/2409.01242 : useful modern sensor-fusion applications, omitted because inertial-assisted calibration and a newer higher-order model already cover the relevant alternatives without adding navigation-specific material.
- Generic software articles, product retail pages and secondary summaries were used only to locate originals and do not support manuscript claims.

### Numerical interpretation safeguards

- All table means and SDs are computed from the supplied files. SD is N-1 sample scatter, not a reported calibration uncertainty.
- Acceleration analysis uses the file's existing SI conversion with its 9.81 factor. The two unit exports are not independent observations.
- Gyro reversal uses nominal inputs from the example scenario, not an external calibration certificate; laboratory calibration requires independent rates. The 0.87189 estimate is an internal example check.
- Magnetic orientation coverage is incomplete, and the magnet changes the environmental field. The paper does not fit an unsupported full ellipsoid or infer a geomagnetic reference from these data.
- The 22–28 s magnetic interval is explicitly moving, so component means are not interpreted as a single orientation.
- Nonfinite magnetic rows are excluded per channel for statistics and retained as gaps in plots.


## Environment


Searched 26 October 2026. This was a targeted literature review, not a systematic review or claim of exhaustive indexing. Searches combined sensor names and primary application/model terms. Retained sources directly supporting the concise papers; excluded tangential applications and secondary explanations.

### Pressure

Queries included `barometric height measurement MEMS pressure sensor smartphone calibration pressure temperature differential height uncertainty research`, `LPS22HB datasheet absolute accuracy one point 0.1 hPa`, and smartphone bias/altitude literature.

Selected four references:

- STMicroelectronics, **LPS22HB**, DocID027083 Rev 6, June 2017: https://www.st.com/resource/en/datasheet/lps22hb.pdf. Read the physical description, Table 3 and its footnotes, and conversion section. Supports 260–1260 hPa range, piezoresistive membrane, 4096 LSB/hPa, and typical accuracy conditions. Filtered RMS noise was deliberately omitted because this firmware's one-shot configuration does not establish the published filtering conditions.
- Li, Y., Chen, W., Wang, J., and Nie, X. (2023), **Precise Indoor and Outdoor Altitude Estimation Based on Smartphone**, IEEE TIM 72, 9513111, https://doi.org/10.1109/TIM.2023.3315391. Metadata and author abstract verified through the authors' institutional repository: https://research.polyu.edu.hk/en/publications/precise-indoor-and-outdoor-altitude-estimation-based-on-smartphon/. Cited only for the need to treat bias and atmospheric reference separately, not to import its reported accuracy into this instrument.
- Staacks et al. (2018), phyphox, https://doi.org/10.1088/1361-6552/aac05e, existing foundational interface paper.
- JCGM 100:2008, https://doi.org/10.59161/JCGM100-2008E. Verified publisher catalogue at https://www.bipm.org/en/web/guest/publications/guides and covariance section in the official PDF. Supports propagation of shared calibration covariance.

Also considered the original 2019 pressure-pair floor-localization study (https://pmc.ncbi.nlm.nih.gov/articles/PMC6720727/) and 2020 barometric activity review (https://pmc.ncbi.nlm.nih.gov/articles/PMC7731380/). Omitted them because the 2023 primary application study plus the sensor datasheet are sufficient for the claims retained. No claim about achieved height accuracy is borrowed from any application paper.

### Temperature and humidity

Queries included `relative humidity temperature capacitive sensor calibration hysteresis response Greenspan 1977 Sonntag 1990`, `HTS221 response self heating calibration 2023 2024 2025`, and `Alduchov Eskridge 1996 Improved Magnus form approximation saturation vapor pressure DOI`.

Selected six references:

- STMicroelectronics, **HTS221**, DocID026333 Rev 5, March 2023: https://www.st.com/resource/en/datasheet/hts221.pdf. Read Table 3 and footnotes and physical description. Confirms the typical 15 s temperature and 10 s humidity 63%-response times; humidity response condition 25 °C, 1 m/s airflow. Typical values are not guaranteed, and the assembled board requires separate qualification.
- Alduchov, O. A., and Eskridge, R. E. (1996), **Improved Magnus Form Approximation of Saturation Vapor Pressure**, Journal of Applied Meteorology 35(4), 601–609, https://doi.org/10.1175/1520-0450(1996)035%3C0601:IMFAOS%3E2.0.CO;2. Publisher metadata/abstract verified at https://journals.ametsoc.org/doi/pdf/10.1175/1520-0450%281996%29035%3C0601%3AIMFAOS%3E2.0.CO%3B2. The displayed 610.94, 17.625, 243.04 Magnus relation also matches the example-data generator.
- Greenspan, L. (1977), **Humidity Fixed Points of Binary Saturated Aqueous Solutions**, J. Res. NBS A 81A(1), 89–96, https://doi.org/10.6028/jres.081A.011. Verified NIST primary scan https://nvlpubs.nist.gov/nistpubs/jres/81a/jresv81an1p89_a1b.pdf and NIST archive https://nistdigitalarchives.contentdm.oclc.org/digital/collection/p16009coll6/id/81246/. Supports temperature-dependent equilibrium salt reference points, not a claim that placing a salt near the board immediately calibrates it.
- Holik, M., Barac, A., Zidar, J., and Stojkov, M. (2024), **Dual-Approach Calibration Unlocks Potential of Low-Power, Low-Cost Temperature and Humidity Sensors**, Tehnički vjesnik 31(4), 1335–1347, https://doi.org/10.17559/TV-20240606001753. Verified journal-hosted metadata and abstract at https://hrcak.srce.hr/en/318495. Directly studies HTS221TR and temperature-dependent humidity calibration. Paper uses only that methodological observation, not its performance numbers or a claim that its coefficients generalize.
- Staacks et al. 2018 and JCGM 100:2008 as above.

Considered older polymer humidity-response/hysteresis research and more elaborate contemporary correction models. These add little to the short paper once the specific sensor datasheet, Magnus relation, fixed-point reference method and recent sensor-specific calibration study are present. Excluded machine-learning detail because the provided CSV cannot justify fitting such a calibration.

### Analogue inputs

Queries included `nRF52840 SAADC source resistance acquisition time 10 bit analog calibration input impedance Nordic specification`, `Arduino RC circuit time constant smartphone phyphox capacitor experiment voltage nonlinear fit paper`, and the exact RC paper title.

Selected five references:

- Nordic Semiconductor, **nRF52840 Product Specification**, 4413_417 v1.0, section 6.23. Vendor-hosted indexed primary PDF: https://docs-be.nordicsemi.com/bundle/nRF52-Series-PS/raw/resource/enus/nRF52840_PS_v1.0.pdf. Search results exposed source-resistance/acquisition-time table and gain/reference equations. Direct PDF fetch timed out, so no unverified revision date is assigned in BibTeX. The v1.1 indexed PDF supports the same source-resistance relationship; the prose avoids numerical performance claims beyond the cited acquisition mechanism and rail constraint.
- ArduinoCore-mbed 4.5.0, `wiring_analog.cpp`: https://raw.githubusercontent.com/arduino/ArduinoCore-mbed/4.5.0/cores/arduino/wiring_analog.cpp. Directly inspected initial `read_resolution=10` and `read_u16() >> (16-read_resolution)`. Confirms returned ten-bit software codes without asserting that supply voltage determines the internal ADC reference.
- Torriente-García, I., Muñoz-Pérez, F. M., Martí, A. C., Monteiro, M., Castro-Palacio, J. C., and Monsoriu, J. A. (2023), **Experimenting with RC and RL series circuits using smartphones as signal generators and oscilloscopes**, Revista Brasileira de Ensino de Física 45, e20230143, https://doi.org/10.1590/1806-9126-RBEF-2023-0143. Verified authors/title at https://arxiv.org/abs/2303.16249 and journal PDF held in author institution repository https://www.colibri.udelar.edu.uy/jspui/bitstream/20.500.12008/42287/1/10.1590.1806-9126-RBEF-2023-0143.pdf. Supports the shape-derived time-constant argument despite arbitrary voltage gain.
- Staacks et al. 2018 and JCGM 100:2008 as above.

Considered a 2024 Arduino RC demonstration (Tidar et al.), but selected the stronger peer-reviewed original with a directly relevant amplitude-scale discussion. Excluded unrelated MCU performance studies because they would not establish this pinned acquisition configuration's uncertainty.

### Numerical reduction and wording

`compute_metrics.py` provides `analyze(data_root: Path) -> dict` using only the standard library. It reads the three original CSVs, applies half-open windows to actual timestamps, interpolates bracketing pressure means, and profiles the exponential time constant by ordinary least squares with a golden-section scalar search. `metrics.json` records exact results and intervals; manuscripts use sensible rounded values.

Data figures and tables use direct descriptive captions without a repeated dataset label. Data origin is stated once per paper, in the title-block data-provenance footnote and at the top of each Markdown companion, not in captions. The papers state the quantities actually calculated and do not turn fitted residual RMS or plateau dispersion into invented calibrated uncertainty. The parent retains original data and build provenance outside presentation prose.


## Optics


Reviewed 2026-10-26. Only primary research, original agency publications and manufacturer documents support the draft text. Each paper retains five or six references, selected for the actual inference rather than breadth of citation. No source is quoted verbatim in the manuscripts.

### Light and RGB

Searches included: APDS-9960 integration/gain/saturation datasheet; APDS9960 photometry calibration; RGB spectral responsivity/metamerism; low-cost multichannel optical calibration 2023–2026. The exact APDS sensor application and the more recent multichannel-calibration paper serve different purposes.

- Broadcom/Avago, APDS-9960 datasheet AV02-4191EN: https://docs.broadcom.com/doc/AV02-4191EN. Inspected official PDF. Supports RGBC channel architecture, gain decoding and integration-dependent count ceiling. The text uses approximately 100 words derived from device specifications, within source limits.
- Arduino_APDS9960 1.0.4 pinned source: https://raw.githubusercontent.com/arduino-libraries/Arduino_APDS9960/1.0.4/src/Arduino_APDS9960.cpp. Read initialization: integration argument truncates to252; CONTROL0x02 selects16× despite the4× comment. Used only for these configuration consequences.
- Keresteš and Pohanka (2024), Proceedings97(1),8; doi:10.3390/proceedings2024097008. Publisher record: https://www.mdpi.com/2504-3900/97/1/8. Search result supplies title, authors, publication date2024-03-13, proceedings status and actual APDS9960 application. Direct later opening was rate-limited429. Manuscript says only that the device was used with controlled LED illumination for a chemical assay. No performance claim transferred.
- Besozzi et al. (2026), Acta IMEKO15(2); doi:10.21014/actaimeko.v15i2.2267. https://acta.imeko.org/index.php/acta-imeko/article/view/2267. Official record dated2026-06-04 verifies authors/title/issue. Retained for distinction between responsivity calibration and spectral/photometric reconstruction, without importing its performance to APDS9960.
- Nicodemus et al. (1977), NBS Monograph160; doi:10.6028/NBS.MONO.160. https://www.nist.gov/publications/geometrical-considerations-and-nomenclature-reflectance and original https://nvlpubs.nist.gov/nistpubs/Legacy/MONO/nbsmonograph160.pdf. Foundational geometry-specific reflectance definitions.
- JCGM100:2008 GUM (existing verified collection reference): covariance propagation.

Considered but omitted: RGB/spectral reconstruction work based on trained colour books (doi:10.1111/cote.12691), AS7341 colour-temperature work (doi:10.1364/AO.569416), and multispectral-sensor comparisons (doi:10.1109/DSD64264.2024.00067). Their extra channels, trained mappings or different measurands are unnecessary for the present four-channel comparison. The actual data support colour fractions and saturation diagnostics, not a spectral reconstruction.

### Albedo

Searches included: bidirectional reflectance nomenclature; planetary geometric/Bond albedo and phase functions; classroom reflectance measurement; recent reflected-light phase-curve analysis. Retained references connect a defined laboratory ratio with the actual astronomical inference.

- Original astro-lab@home programme paper (Spicker, Küpper and Bresges2022, CAPjournal31,37–41): existing collection reference, retained for experiment context only.
- TI OPT3001 datasheet SBOS681C (Nov2017): https://www.ti.com/lit/ds/symlink/opt3001.pdf. Inspected official PDF. Supports exponent–mantissa conversion and photopic response. Avoids treating arbitrary export units as a certified optical calibration.
- Nicodemus et al.1977: above, establishes directional versus integrated reflectance.
- Heng, Morris and Kitzmann2021, Nature Astronomy5,1001–1008; doi:10.1038/s41550-021-01444-7. https://www.nature.com/articles/s41550-021-01444-7. Publisher metadata and abstract inspected. Supports connection among geometric albedo, phase function and scattering; no planet-specific numbers imported.
- GUM: shared-dark covariance.

Considered later A&A reflected-light work, doi:10.1051/0004-6361/202243831, and the2026 Earth visual phase-function study doi:10.3847/PSJ/ae2ec6. They do not change the laboratory inference; citing both would add references without adding needed content. Their observational applications reinforce why a single fixed-angle sample ratio cannot be labeled planetary Bond albedo.

### Infrared temperature and displacement

Searches included: TMP007 calibration/field of view/negative-temperature format; size-of-source calibration in radiation thermometry2021–2026; thermopile temperature–distance effects; stellar habitable-zone energy-balance assumptions.

- TI TMP007 SBOS685C, July2015: official indexed PDF https://www.ti.com/lit/ds/sbos685c/sbos685c.pdf. Web search extracts cover calibration, angular response and signed register format. Original /lit/pdf/SBOS685 intermittently returned404 on direct opening, while official search indexing and archived revision identify the document. Do not claim URL live availability without retesting.
- TI TMP007 Calibration Guide SBOU142, Aug2014: official link https://www.ti.com/lit/ug/sbou142/sbou142.pdf; full agency-hosted copy https://e2echina.ti.com/cfs-file/__key/telligent-evolution-components-attachments/00-60-01-00-00-23-50-98/sbou142.pdf. Search extracts verify metadata and field-of-view/background calibration principles. Direct official short path was inaccessible in web tool.
- Javier de Lucas2022, Sensors22(21),8284; doi:10.3390/s22218284. https://www.mdpi.com/1424-8220/22/21/8284. Publisher search record includes author, date and direct-method validation/uncertainty abstract; subsequent direct open hit429. Supports explicit size-of-source testing. No laboratory performance number imported.
- Kopparapu et al.2013, ApJ765(2),131; doi:10.1088/0004-637X/765/2/131. Official publisher record and erratum doi:10.1088/0004-637X/770/1/82 inspected. Retained only to support the atmospheric/stellar-spectrum dependence of habitable-zone models. No uncorrected boundary coefficient used. Erratum recorded within the same BibTeX entry rather than adding another reference.
- Astro-lab2022 original programme article, as above.

Considered radiation-thermometer interlaboratory comparison doi:10.1080/18824889.2021.1917181 and 2026 thermal-imager size-of-source correction doi:10.3390/s26072177. The latter concerns microbolometer arrays and medical thermometry rather than this single thermopile, so the instrument-matched TI guide and original single-thermometer calibration paper are more useful. A2025 thermopile-array paper doi:10.1038/s44172-025-00456-9 was also unnecessary; its array calibration does not validate this sensor's optical scene or settling.

### Local numerical verification

`compute_metrics.py` reads only the supplied CSVs and uses Python's standard library. `analyze(data_root)` returns the entire `metrics.json` structure. Intervals are half-open, with1e-9s tolerance for binary representations of decimal endpoints. Tables use rounded versions of these results. The infrared table uses count positions, avoiding an unsupported metre-axis conversion. Apparatus schematics have been redrawn for the required fixed geometries; data-figure LaTeX is left for the parent's common plotting pipeline.


## Timing


Research performed 2026-10-26. Draft papers keep four references (Mission to Mars),
five (Owon interface), and six (transit method). Their theoretical models and
worked calculations are developed directly rather than assembled from review prose.
Sources considered below are primary publications, author accounts or manufacturer
documentation. Research notes are for editorial verification, not article front matter.

### Mission to Mars

Searches: `"Mission to Mars" Spicker Küpper Bresges 2022 pressure`,
`site.pubs.aip.org "Mission to Mars" Spicker`,
`"smartphone" "pressure" "leak" Physics Education barometer`,
`"pressure" "temperature" "smartphone" "gas" "Physics Education" 2024`,
`Spicker Küpper Bresges "Helping Students" "47"`.

Retained:

- Spicker, Küpper and Bresges (2022), *The Physics Teacher* 60(1), 47–50,
  DOI <https://doi.org/10.1119/10.0009109>. Original experiment and design context.
  The DOI destination blocked tool access. Metadata corroborated by authors'
  institutional programme paper (below) and the author's detailed account:
  <https://sebastianspicker.github.io/posts/mission-to-mars/>.
- Staacks et al. (2018), *Physics Education* 53, 045009,
  DOI <https://doi.org/10.1088/1361-6552/aac05e>. Original phyphox paper.
- Bosch Sensortec, BMP280 datasheet revision 1.26 (October 2021),
  <https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf>.
  Opened and verified document revision, range, output characteristics, and internal
  temperature caveat. No claim that the 0.01 hPa export step equals hardware accuracy.
- JCGM 100:2008, <https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf>.
  Opened. Used only for propagation including covariance.

Considered but omitted:

- Spicker et al., *astro-lab@home*, CAPjournal 31 (2022), 37–41,
  <https://physikdidaktik.uni-koeln.de/sites/physikdidaktik/Publikationen/CAPjournal_No-31_October-2022_astrolab-at-home_Bringing-Science-to-the-Sofa.pdf>.
  Confirms original Mars citation but would repeat programme context in a short paper.
- Hafez et al. (2026), smartphone barometer enclosure coupling,
  <https://pmc.ncbi.nlm.nih.gov/articles/PMC12819426/>. Read search extract;
  speaker/tap inference is outside the chamber measurement question.
- Aldridge and Shastri (2026), *The Physics Teacher* 64, 130–133,
  DOI 10.1119/5.0215168. Search metadata only; dynamic hydrostatic/acceleration
  scope does not improve a pressure-chamber reduction, and full primary text
  was unavailable in the search results.
- Atmospheric pressure vs height study (2022), DOI
  10.1590/1806-9126-RBEF-2021-0422. Original study but overlaps the collection's
  separate height/barometry paper rather than this gas-mechanics experiment.

### Owon interface

Searches: `Owon B35T multimeter manual 6000 0.5% 2 digits`,
`site.owon.com.hk B35T digital multimeter user manual pdf`,
`site.nist.gov solar cell current voltage irradiance photodiode linearity calibration`,
`"PV Characterization under Artificial Low Irradiance Conditions" Hamadani Campanelli DOI`,
`"low-cost" "multimeter" "calibration" 2024 Bluetooth photometry`.

Retained:

- OWON 35-series/B41T manufacturer manual,
  <https://files.owon.com.cn/probook/OWON_35_Series%26B41T_USER_MANUAL.pdf>.
  Manufacturer search indexed document; direct open timed out. Range and
  specification corroborated against manufacturer's technical sheet
  <https://www.owontechnology.eu/_downloads/84b18e7bf3fb8d55ff5253378e76bd50>
  and regional manufacturer page <https://www.owon.co.jp/products/b35-series/>.
  Current redirect of the Japanese page targets a B35+ page, so the manuscript
  does not cite the redirect as a B35T-specific protocol source.
- Hamadani and Campanelli (2020), *IEEE Journal of Photovoltaics* 10,
  DOI <https://doi.org/10.1109/JPHOTOV.2020.2996241>.
  Primary publication verified through NIST institutional record:
  <https://www.nist.gov/publications/pv-characterization-under-artificial-low-irradiance-conditions-using-reference-solar>.
  Its spectral-response and effective-irradiance arguments directly address
  why lux and cell voltage cannot be assumed interchangeable.
- Staacks et al. (2018), original phyphox publication.
- Spicker and Küpper (2024), original classroom transit publication, for the
  circuit's application rather than a claim about a multimeter protocol.
- JCGM 100:2008, for calibration covariance and propagation.

Considered but omitted:

- Hamadani (2021), IEEE PVSC proceedings, DOI 10.1109/PVSC45281.2020.9300935.
  Same measurement programme; the fuller joint journal article is enough.
- NIST SRI 6014 reference-cell documentation,
  <https://www.nist.gov/sri/standard-reference-instruments/sri-6014-calibrated-reference-photovoltaic-cell>.
  Useful corroboration of short-circuit calibration but unnecessary alongside
  the primary article.
- 2026 MethodsX LED–LDR colorimeter, DOI 10.1016/j.mex.2026.103881.
  Uses a different optical transfer (LDR resistance/absorbance); not needed for
  voltage-decoder or solar-cell validation.
- Meter manuals from third-party reposts were used only to locate official
  manufacturer links, not as the paper's authority.

### Transit method

Searches: `"Exoplanet Hunting in the Classroom" 2024 Spicker Küpper`,
`Mandel Agol 2002 analytic light curves planetary transit Kipping 2010 binning is sinning`,
`"transit photometry" "finite integration" 2025 methods paper`,
`"Exoplanet Hunting in the Classroom" "226"`.

Retained:

- Spicker and Küpper (2024), *The Physics Teacher* 62(3), 226–229,
  DOI <https://doi.org/10.1119/5.0125305>. Original classroom study.
  Verified publisher-society TOC:
  <https://www.aapt.org/Publications/tpt_March2024.cfm>.
- Mandel and Agol (2002), *ApJ Letters* 580, L171–L175,
  DOI <https://doi.org/10.1086/345520>. Original analytic transit model;
  opened <https://arxiv.org/abs/astro-ph/0210099> and author-hosted PDF
  <https://faculty.washington.edu/agol/MandelAgol2002.pdf>.
- Kipping (2010), *MNRAS* 408(3), 1758–1769,
  DOI <https://doi.org/10.1111/j.1365-2966.2010.17242.x>.
  Opened publisher article and <https://arxiv.org/abs/1004.3741>.
  Direct support for finite-integration distortion; no assumption that BLE
  cadence equals exposure time.
- TI OPT3001 datasheet revision C (November 2017),
  <https://www.ti.com/lit/ds/symlink/opt3001.pdf>. Opened; verified photopic
  response. Kept because the distinction between photometry and bolometric
  flux is part of this experiment's measurement model.
- Hamadani and Campanelli (2020), for the solar-cell optical transfer.
- JCGM 100:2008, for shared-baseline and geometry uncertainty propagation.

Considered but omitted:

- Price and Rogers (2014), *ApJ* 794, 92,
  DOI <https://doi.org/10.1088/0004-637X/794/1/92>.
  Primary finite-integration covariance treatment read in publisher extract.
  It extends the same integration issue; Kipping is enough for this short
  paper, which does not present a Fisher-information calculation.
- Recent exoplanet parameter catalogues and discovery statistics: unnecessary
  for an experiment with fixed laboratory geometry and no discovery-rate claim.
- Author blog account, <https://sebastianspicker.github.io/posts/exoplanet-hunting-smartphones/>:
  helpful programme context, but original publication preferred in bibliography.

### Numerical checks

`compute_metrics.py` reproduces `metrics.json` with Python standard-library CSV
reading and explicit half-open windows. It reads all six supplied CSVs without
modifying them. The Owon nominal levels come from the example scenario rather
than an external voltage certificate. The transit algorithm reduces three
events, not six; six on/off transitions are not six complete events. The three
acquisition paths are analysed independently throughout.


## Thermal


Checked 26 October 2026. Broad discovery was followed by original articles,
author-deposited copies, and component datasheets. Sources retained in the short
papers have a specific role; additional discovered work was screened rather
than added simply to lengthen the bibliographies. Counts: greenhouse 5, pt-star
5, tidal-locking 6.

### Greenhouse

Search themes: covered versus uncovered classroom greenhouse experiments;
glasshouse convection and radiation; lumped greenhouse energy balance;
greenhouse heat-transfer models 2024–2026; planetary infrared transfer.

Selected:

- Spicker, Küpper and Bresges (2022), programme context. Original article and
  authors/issue/page metadata read at
  https://physikdidaktik.uni-koeln.de/sites/physikdidaktik/Publikationen/CAPjournal_No-31_October-2022_astrolab-at-home_Bringing-Science-to-the-Sofa.pdf
- Bosch BMP280, revision 1.26, October 2021. Official datasheet read at
  https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf
  Page 8 footnote 3 explicitly identifies PCB temperature, self-heating, and
  ambient temperature as influences on the internal temperature channel.
- Boulard and Baille (1993), original coupled energy/water-balance model,
  Agricultural and Forest Meteorology 65(3–4), 145–157,
  https://doi.org/10.1016/0168-1923(93)90001-X . Publisher was inaccessible;
  the author-uploaded original abstract and metadata were read at
  https://www.researchgate.net/publication/222776668_A_simple_greenhouse_climate_control_model_incorporating_effects_of_ventilation_and_evaporative_cooling .
- Pierrehumbert (2011), Physics Today 64(1), 33–38,
  https://doi.org/10.1063/1.3541943 . Original reprint read at
  https://courses.seas.harvard.edu/climate/eli/Courses/global-change-debates/Sources/CO2-saturation/more/Pierrehumbert-2011.pdf .
  This copy is the expanded AIP conference reprint; its first page explicitly
  identifies the 2011 Physics Today original, pages 33–38. Used only for the
  wavelength-dependent planetary-radiative mechanism, not a claim about vessel
  convection.
- JCGM 100:2008, official covariance-aware uncertainty guidance:
  https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf .

Screened but omitted: Wood's 1909 greenhouse note (historically interesting but
its planetary extrapolation is unsuitable); Nahle replication documents
(unsupported atmospheric extrapolation); 2024 active greenhouse HVAC and
photovoltaic/earth-air heat-exchanger models (unnecessary machinery for a short
two-vessel paper); 2024 spatial-temperature/soil-storage paper,
https://doi.org/10.1016/j.est.2023.109938 (supports the general need to distinguish
thermal nodes but does not displace the simpler original model selected).

### Pressure, temperature, and star formation

Search themes: first-law gas compression and slow/fast experimental paths;
protostellar collapse compressional heating, radiative cooling, and virial
reasoning; first hydrostatic core radiation hydrodynamics 2024–2025.

Selected:

- Spicker and Küpper's 24 September 2020 workshop, original title/authors/date
  verified from first page:
  https://astro-lab.app/pdf/Spicker-und-Kuepper_Sternentwicklung_LeFoBi-2020_150ppi.pdf .
- BMP280 official datasheet as above, for measurand and rated pressure range.
- Larson (1969), original protostellar-collapse calculation. Publisher record
  verifies Richard B. Larson, MNRAS 145(3), 271–295,
  https://academic.oup.com/mnras/article/145/3/271/2602795 ;
  DOI https://doi.org/10.1093/mnras/145.3.271 .
- Bhandare, Ahmad and Commerçon (2025), original radiation-hydrodynamic work
  connecting accretion and energy retention. Author-deposited original read at
  https://arxiv.org/abs/2509.15009 ; journal reference and author names verified
  there as A&A 702, L7, DOI https://doi.org/10.1051/0004-6361/202556128 .
- JCGM 100:2008 for propagation with joint input covariance.

Screened but omitted: McKee and Ostriker 2007 review (useful context but direct
original papers preferred); 2013 multigroup second-collapse calculations
https://doi.org/10.1051/0004-6361/201321423 (redundant beside foundational Larson
and the recent specific radiation-efficiency result); 2024 grain-growth first-core
paper https://doi.org/10.1051/0004-6361/202347847 (chemistry is beyond this
thermodynamics analogy); Bate 2025 stellar mass-function models
https://doi.org/10.1093/mnras/staf059 (cluster/IMF scope unnecessary).

### Tidal locking

Search themes: synchronous terrestrial-planet heat redistribution and day/night
contrast; two-box thermal balances; dynamical-regime limitations; recent
2026 analytic models; TMP007 field of view and OPT3001 photopic response.

Selected:

- Original astro-lab programme article as above, for experiment lineage.
- BMP280 as above, to identify die temperature.
- Official TMP007 SBOS685C, July 2015, indexed original at
  https://www.ti.com/lit/ds/sbos685c/sbos685c.pdf . Some TI alias opens returned
  404, so the bibliography uses the explicit revision URL. The tool's indexed
  original and page excerpts establish field-of-view-dependent response and
  object/die measurement distinction. The generic original alias
  https://www.ti.com/lit/pdf/SBOS685 was indexed but intermittently inaccessible.
- OPT3001 SBOS681C, November 2017, official original read at
  https://www.ti.com/lit/ds/symlink/opt3001.pdf . The stated measurand is photopic
  illuminance, with strong infrared rejection.
- Koll (2022), original heat-redistribution scaling, ApJ 924(2), 134,
  https://doi.org/10.3847/1538-4357/ac3b48 . Original PDF read at
  https://indico.dfa.unipd.it/event/421/attachments/350/665/Koll_2022_ApJ_924_134.pdf ;
  author publication list independently confirms metadata at
  https://danielkoll.github.io/publications/ .
- Wirth, Powell and Wordsworth (2026), original four-box/dynamical-regime study,
  https://arxiv.org/abs/2601.12556 . Authors/title and journal DOI verified from
  author-deposited original. Associated published record:
  https://doi.org/10.3847/1538-4357/ae3da9 , ApJ 999, 153 (issue metadata indexed
  by the Paris exoplanet bibliography). The text only uses the directly verified
  conclusion that dynamical regime affects day/night interpretation.

Screened but omitted: Wordsworth (2015), original atmospheric-collapse/heat
transport paper https://doi.org/10.1088/0004-637X/806/2/180 (foundational but
would duplicate Koll); Koll and Abbot (2016), temperature/circulation theory
https://pmc.ncbi.nlm.nih.gov/articles/PMC6267993/ (background for the selected
scaling); Hammond and Lewis (2021), circulation decomposition
https://pmc.ncbi.nlm.nih.gov/articles/PMC8020661/ (interesting but fluid-dynamical
detail is unsupported by the stationary laboratory model).

### Source-code and data checks

Read the current manuscript bodies, relevant example-data generator functions,
and the CSV headers/rows. The BMP temperature channels are kept distinct from
gas, air, and surface thermometry. All intervals are half-open. Greenhouse and
tidal examples have discontinuities at lamp-off; the papers explicitly exclude
those boundaries from late-heating calculations and continuous response fits.
Only greenhouse receives a heating-only descriptive fit. Data captions
begin directly with their description. Data origin is stated once per paper, in the title-block data-provenance footnote and at the top of each Markdown companion, not in captions.
