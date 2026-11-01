# Core sensor manuscripts: literature and revision audit

Research date: 26 October 2026. Scope: seven original core papers. The original numerical analyses, plots, acquisition sources and example inputs remain unchanged. `analysis/revision_core.py` supplies independent extensions; `core-entries.json` declares every auxiliary input. No independent clocks are aligned. The example data support physical interpretations and reduction checks, not a new experimental campaign.

Searches below were run through web search, followed by primary-source pages, author/institutional repositories, manufacturer documentation and relevant technical sections. DOI, authors, date and title were checked against the linked primary record. Access failures are distinguished from sources read. An institutional abstract is adequate evidence for a narrowly attributed method claim; numerical specifications were checked in the underlying datasheets or pinned implementations. General catalogues, aggregators and snippets were used for discovery, not as manuscript authority.

## Accelerometer — gravity, calibration and quantisation

**Search angles and queries.** `gravity based characterization accelerometers intrinsic parameters Geist Afridi McGray Gaitan 2017 Frosio autocalibration`; `Bosch BMA250 datasheet 2g 8 bit SensorTag CC2541 accelerometer user guide`; `CC2541 SensorTag user guide accelerometer 64 g gyroscope magnetometer`; `Autocalibration of MEMS Accelerometers Frosio Pedersini Borghese`; NIST constant-rotation/low-frequency calibration. This covered the static gravity model, calibration identifiability, resolution and an alternative dynamic calibration route. Initial BMA250 discovery was not assumed to identify this SensorTag: the actual example identifies a KXTJ9.

**Selected six references and earned claims.**

- `frosio2009`: Frosio, Pedersini and Borghese, *Autocalibration of MEMS Accelerometers*, IEEE TIM 58(6), 2034–2041 (2009), DOI [10.1109/TIM.2008.2006137](https://doi.org/10.1109/TIM.2008.2006137). [Author institution's record and abstract](https://expertise.unimi.it/resource/item/120540?language=en_US) explicitly identify static gravity magnitude, bias, scale and symmetric cross-axis parameters. Retained for the constant-norm calibration argument; no claimed accuracy is transferred.
- `geist2017`: Geist, Afridi, McGray and Gaitan, *Gravity-Based Characterization of Three-Axis Accelerometers in Terms of Intrinsic Accelerometer Parameters*, J. Res. NIST 122, 32 (2017). [Full primary paper](https://doi.org/10.6028/jres.122.032) and [NIST record](https://www.nist.gov/publications/gravity-based-characterization-three-axis-mems-accelerometers-terms-intrinsic) checked. Separates intrinsic cross-axis parameters from gimbal mounting alignment; underpins the unresolved orientation argument.
- `lsm9ds1`: [ST datasheet, March 2015, Rev. 3](https://www.st.com/resource/en/datasheet/lsm9ds1.pdf), Table 3 inspected: 0.122 mg/LSB at ±4g. Used as nominal component resolution, expressly not calibration accuracy.
- `arduinoimu`: [Arduino_LSM9DS1 1.1.1 pinned implementation](https://raw.githubusercontent.com/arduino-libraries/Arduino_LSM9DS1/1.1.1/src/LSM9DS1.cpp), initialization/conversion inspected; establishes configuration and output conversion.
- `cc2541phyphox`: [original configuration authors' documentation](https://phyphox.org/wiki/index.php/Texas_Instruments_SensorTag_CC2541), accelerometer section read. Establishes eight transmitted bits per axis. The 64-count/g scale is independently recovered from the example, rather than attributed to an unrelated chip datasheet.
- `gum`: [JCGM 100:2008](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf), correlated-input treatment in §5.2 and F.1.2 checked through the primary indexed text. Supports component covariance propagation; no repeated citation for elementary gravity equations.

**Considered/excluded.** [Gaitan and Geist's constant-rotation extension](https://www.nist.gov/publications/calibration-triaxial-accelerometers-constant-rotation-gravitational-field) was read at the NIST record; relevant to a later low-frequency dynamic calibration but unnecessary for the static record. BMA250 catalogues rejected as the wrong sensor identification. Generic phone-accelerometer demonstrations and the general phyphox paper omitted to retain calibration-specific references.

**New analysis.** OLS of corrected x against signed packet x over the complete CC2541 example gives 0.153228906 m/s²/count. The local small-angle equivalent is 0.8952466° and the nominal step ratio to the Nano is 128.0738. The separate [0,8) s flat window has 81 identical x codes and zero sample SD. The manuscript interprets this as unresolved quantisation, without inventing sub-code precision or comparing noise between devices.

## Gyroscope — reversal, stochastic error and integration

**Queries/angles.** `Tedaldi Pretto Menegatti 2014 IMU calibration without external equipments PDF`; `El Sheimy Hou Niu 2008 Allan variance inertial sensors ITG3200 datasheet sensitivity 14.375`; `Analysis and Modeling of Inertial Sensors Using Allan Variance pdf`; SensorTag protocol and LSM9DS1 full-scale conversion. Angles: calibration design, bias evolution, unit conversion and the distinction between signed angle and integrated norm.

**Selected five references.**

- `tedaldi2014`: Tedaldi, Pretto and Menegatti, *A Robust and Easy to Implement Method for IMU Calibration without External Equipments*, ICRA 2014, 3042–3049, DOI [10.1109/ICRA.2014.6907297](https://doi.org/10.1109/ICRA.2014.6907297). [Author-hosted paper](https://albertopretto.altervista.org/papers/tpm_icra2014.pdf) first-page model/abstract and [author publication record](https://albertopretto.altervista.org/print.php?mod=01_Research) read; direct subsequent PDF fetch timed out. Narrow attribution retained: multi-position bias/scale/misalignment calibration, rather than a claim about its performance on this board.
- `elsheimy2008`: El-Sheimy, Hou and Niu, *Analysis and Modeling of Inertial Sensors Using Allan Variance*, IEEE TIM 57(1), 140–149 (2008), [10.1109/TIM.2007.908635](https://doi.org/10.1109/TIM.2007.908635). Publisher abstract/introduction and methodology description inspected. Supports averaging-time-dependent stochastic error analysis; no bias-instability estimate is extracted from this short moving record.
- `lsm9ds1`: manufacturer table inspected: ±2000 degree/s, nominal 70 mdps/LSB. [Primary PDF](https://www.st.com/resource/en/datasheet/lsm9ds1.pdf).
- `arduinoimu`: pinned source read: conversion 2000/32768, configuration 119 Hz. [Primary implementation](https://raw.githubusercontent.com/arduino-libraries/Arduino_LSM9DS1/1.1.1/src/LSM9DS1.cpp).
- `gum`: JCGM 100:2008 §5.2, gain/offset covariance and common calibration terms. [Primary text](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf).

**Considered/excluded.** ITG-3200 manufacturer information is genuine but identifies the wrong gyro for the CC2541 example (IMU-3000); no sensitivity is transferred. Yampolsky/Klein's data-driven calibration reference removed because the reversal model and Allan study directly address the present inference with fewer tangential claims. Hou/El-Sheimy ION 2003 study considered but superseded here by the fuller 2008 article. No generic phyphox reference needed for this physical argument.

**New analysis.** Timestamp trapezoids on Nano samples in [9,29) s, actual endpoints 9.01099968 and 28.9880009 s: signed z integral 2.4672079°, norm integral 742.912065°. Rates deliberately remain indicated/unadjusted. Independent CC2541 code-to-rate regression gives 0.0001331580545 rad/s/count. No cross-device timing, noise ranking or inferred reference turn is asserted.

## Magnetometer — calibration frame, disturbances and indirect current

**Queries/angles.** `Kok Schön Magnetometer calibration using inertial sensors 2016`; `magnetometer calibration Renaudin Afzal Lachapelle complete triaxis magnetic domain`; magnetic-current geometry/current reversal; higher-order models and platform versus environmental disturbances.

**Selected five references.**

- `kok2016`: Kok and Schön, *Magnetometer Calibration Using Inertial Sensors*, IEEE Sensors Journal 16(14), 5679–5689 (2016), [10.1109/JSEN.2016.2569160](https://doi.org/10.1109/JSEN.2016.2569160). [Author manuscript HTML](https://arxiv.org/html/1601.05257v3), measurement model and ellipsoid-initialization/alignment sections read; journal metadata explicitly verified in the manuscript. Supports the unresolved rotation of magnetic-only fitting and the additional alignment needed for inertial heading.
- `renaudin2010`: Renaudin, Afzal and Lachapelle, *Complete Triaxis Magnetometer Calibration in the Magnetic Domain*, Journal of Sensors 2010, 967245. [Publisher primary record and model abstract](https://onlinelibrary.wiley.com/doi/abs/10.1155/2010/967245) read; DOI/title/authors/year verified. Supports combined instrument and host-platform hard-/soft-iron terms. No transferred heading accuracy.
- `lsm9ds1`: ±4-gauss nominal magnetic sensitivity 0.14 mgauss/LSB checked in [ST Table 3](https://www.st.com/resource/en/datasheet/lsm9ds1.pdf).
- `arduinoimu`: range, 20-Hz magnetic configuration and 400/32768 conversion checked in the [pinned source](https://raw.githubusercontent.com/arduino-libraries/Arduino_LSM9DS1/1.1.1/src/LSM9DS1.cpp).
- `gum`: [JCGM §5.2/F.1.2](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf), used only for shared reference/geometry covariance in vector calibration.

**Considered/excluded.** Cowart/Petrich higher-order/neural calibration removed: the original paper's limited rotational coverage does not motivate that model. [Afzal/Renaudin/Lachapelle 2011 gyroscope-error study](https://www.mdpi.com/1424-8220/11/12/11390) and the [2010 ION orientation paper](https://www.ion.org/publications/abstract.cfm?articleID=8951) considered; the selected 2010 calibration and 2016 alignment articles address the actual model more directly. Field mapping and GNSS-assisted calibration require apparatus outside this study.

**New analysis.** Full magnetic-current example regressed against its derived current: slope 49.99999999 µT/A, intercept 30.000000001 µT, maximum residual 5.23e-8 µT. This is explicitly circular, not a validation fit. The corresponding sensitivity to a 1-µT background change is 0.020 A. The positive-current sequence does not test reversal. No undocumented coil dimensions are introduced.

## Pressure — differential barometry and thermodynamic range

**Queries/angles.** `Precise Indoor and Outdoor Altitude Estimation Based on Smartphone 2023 Li Chen`; `barometric altitude hypsometric equation pressure temperature uncertainty`; `IAPWS R7-97 saturation pressure temperature revised release 2012`; LPS22HB calibrated range/accuracy. Covers reference pressure, drift, atmospheric model, and a different pressure-dependent thermodynamic observable.

**Selected four references.**

- `li2023altitude`: Li, Chen, Wang and Nie, *Precise Indoor and Outdoor Altitude Estimation Based on Smartphone*, IEEE TIM 72, 9513111 (2023), [10.1109/TIM.2023.3315391](https://doi.org/10.1109/TIM.2023.3315391). [Authors' institutional record](https://research.polyu.edu.hk/en/publications/precise-indoor-and-outdoor-altitude-estimation-based-on-smartphon/) read: separates systematic pressure bias from a spatial/meteorological pressure reference. Only that distinction is borrowed, not their achieved errors.
- `lps22hb`: [ST datasheet, June 2017 Rev. 6](https://www.st.com/resource/en/datasheet/lps22hb.pdf), pressure range and parameter table read. Supports 260–1260 hPa rated interval, code scale and typical calibration-qualified accuracy.
- `iapws1997`: [IAPWS R7-97(2012) release](https://iapws.org/technical-guidance/release/IF97-Rev), release description/history and region-4 saturation formulation checked via [primary PDF](https://www.iapws.org/relguide/IF97-Rev.pdf). Title and editorial revision year verified. Used as reference saturation relation, not a claim that visual boiling automatically establishes equilibrium.
- `gum`: [JCGM 100:2008](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf), covariance of shared pressure calibrations.

**Considered/excluded.** NIST-hosted EURAMET air-density/calibration guidance read for atmospheric pressure/reference context; it does not replace the declared isothermal height model. The Mars teaching article is historically related but not necessary for this pressure-difference argument. General phyphox citation omitted. No boiling-curve fit imposed on observations labelled liquid or uncertain.

**New analysis.** All 15 auxiliary paired observations checked against 26–126 kPa, independent of their phase labels. Range 5.0391–101.1827 kPa; IDs 11–15 outside range, including two sustained-boiling labels. This exposes a sensor operating-domain limit rather than falsely extending the Nano measurement capability.

## Temperature and humidity — vapour content, local heat and lag

**Queries/angles.** `humidity sensor calibration temperature self heating HTS221 saturated salts Greenspan 1977 Holik 2024`; `HDC1000 thermal humidity sensor self heating datasheet`; `SHT21 datasheet relative humidity temperature`; `Improved Magnus Form Approximation Alduchov Eskridge 1996`; ST assembled-sensor response guidelines. Covers equilibrium vapour pressure, reference humidity, temperature-dependent calibration and thermal integration.

**Selected six references.**

- `hts221`: [ST datasheet, March 2023 Rev. 5](https://www.st.com/resource/en/datasheet/hts221.pdf), Table 3 inspected. Typical accuracy and 10-/15-s RH/T response times retained with specified airflow/temperature qualifications.
- `alduchov1996`: Alduchov and Eskridge, *Improved Magnus Form Approximation of Saturation Vapor Pressure*, J. Applied Meteorology 35(4), 601–609 (1996), DOI [10.1175/1520-0450(1996)035<0601:IMFAOS>2.0.CO;2](https://doi.org/10.1175/1520-0450%281996%29035%3C0601%3AIMFAOS%3E2.0.CO%3B2). Original paper's abstract/equations were read from an institutional-hosted copy; direct publisher fetch returned 403. The 610.94/17.625/243.04 water saturation approximation supplies the paired-channel transform.
- `greenspan1977`: Greenspan, *Humidity Fixed Points of Binary Saturated Aqueous Solutions*, J. Res. NBS 81A(1), 89–96 (1977), DOI 10.6028/jres.081A.011. [Primary full paper](https://nvlpubs.nist.gov/nistpubs/jres/81A/jresv81An1p89_A1b.pdf) read. Temperature-dependent equilibrium salt references, with equilibration and contamination constraints.
- `holik2024`: Holik, Barac, Zidar and Stojkov, *Dual-Approach Calibration Unlocks Potential of Low-Power, Low-Cost Temperature and Humidity Sensors*, Tehnički vjesnik 31(4), 1335–1347 (2024), [10.17559/TV-20240606001753](https://doi.org/10.17559/TV-20240606001753). Publisher/indexed original abstract and conclusions read from [primary journal archive](https://hrcak.srce.hr/file/460251); later direct fetch returned 418. Narrow claim: including temperature affects HTS221TR calibration. Published correction coefficients and performance are not transferred.
- `hdc1000`: [TI datasheet, January 2016 Rev. C](https://www.ti.com/lit/ds/symlink/hdc1000.pdf), capacitive sensing and paired conversions checked; datasheet notes assembled thermal mass/airflow affect response. Existing key reused; its bibliographic entry now records the verified January 2016 revision instead of a consultation/provenance note.
- `sht21`: [Sensirion datasheet, October 2022 Version 5](https://sensirion.com/resource/datasheet/sht21), §2.3 temperature effects and §6 conversions read. Warns against heat conducted from the board and excessive active duty cycle. New key contains verified revision/date.

**Considered/excluded.** [ST HTS221 hardware integration application note](https://www.st.com.cn/resource/en/application_note/dm00208002-hts221-digital-humidity-sensor-hardware-guidelines-for-system-integration-stmicroelectronics.pdf) read for vent/dead-volume response, but the datasheet and SHT thermal guidance already cover the necessary argument. No GUM or general phyphox citation added; channel covariance is explained directly. BMP die temperature is not substituted for HDC air temperature; the barometer's distinct clock is not merged by row number.

**New analysis.** Paired Magnus transforms, then means: HTS [20,30) s 1296.630 Pa versus [90,96) s 1286.881 Pa, change -0.75188%; HDC [0,25) s 1238.441 Pa versus [45,60) s 2054.191 Pa; SHT [0,20) s 1263.175 Pa. Separate environmental histories preclude inter-device bias estimates. The HTS result is compatible with nearly unchanged vapour content, not a precise demonstration of moisture conservation.

## RGBC light — spectral weighting, clipping and filters

**Queries/angles.** `RGB color sensor colorimetric calibration CCT McCamy 1992 Robertson 1968 spectral mismatch`; `Flexible Calibration Method Besozzi Gibertoni Rovati Gibaldi 2026`; `Advanced Analysis of Solutions Keresteš Pohanka 2024`; APDS9960 integration ceiling and geometrical reflectance. Covers forward spectral model, apparatus geometry, related quantitative detector studies and color-temperature identifiability.

**Selected five references.**

- `apds9960`: [Avago APDS-9960 datasheet AV02-4191EN](https://docs.broadcom.com/doc/AV02-4191EN), RGBC path and ATIME register sections read. 2.78-ms integration cycles and 1025-count/cycle ceiling imply 4100 at four cycles; 16-bit register width alone does not determine usable range.
- `arduinoapds`: [Arduino_APDS9960 1.0.4 primary source](https://raw.githubusercontent.com/arduino-libraries/Arduino_APDS9960/1.0.4/src/Arduino_APDS9960.cpp), pinned integration and gain configuration used by original analysis.
- `nicodemus1977`: Nicodemus, Richmond, Hsia, Ginsberg and Limperis, *Geometrical Considerations and Nomenclature for Reflectance*, NBS Monograph 160 (1977), [primary full monograph](https://nvlpubs.nist.gov/nistpubs/Legacy/MONO/nbsmonograph160.pdf), reflectance geometry definitions inspected. Supports the need to specify incidence/viewing directions.
- `besozzi2026`: Besozzi, Gibertoni, Rovati and Gibaldi, *Flexible calibration method: Photometric and radiometric measurements with compact low-cost multi-channel sensors*, Acta IMEKO 15(2), 1–12 (June 2026), DOI [10.21014/actaimeko.v15i2.2267](https://doi.org/10.21014/actaimeko.v15i2.2267). [Primary full paper](https://acta.imeko.org/index.php/acta-imeko/article/view/2267/3207), methods §3.1–3.5 read: independent spectrometer/power references, configuration scaling and spectral reconstruction. Explicitly different sensor models; no performance transfer to APDS9960.
- `gum`: [JCGM 100:2008 §5.2](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf), shared baseline and the constrained RGB-fraction covariance.

**Considered/excluded.** McCamy 1992 (10.1002/col.5080170211) identified, but a numerical CCT polynomial is not needed to establish the prerequisite of calibrated standard colour coordinates; no unverified CCT values added. Keresteš/Pohanka 2024 metadata identified, but primary full-text requests failed (429), so the original sentence relying on that article was replaced with the directly read Besozzi calibration study. ML8511 documentation concerns a UV device, not APDS visible-colour calibration. Generic RGB tutorials rejected.

**New analysis.** Independent clocks preserved. Device-time local windows [14.8,15.2) s and [34.8,35.2) s give RGB transmissions (0.91203,0.23092,0.14903) and (0.17678,0.20348,0.77706). Explicitly local extrema neighbourhoods, not settled plateaux. Independent raw-count check using the declared dark/reference settings agrees with all normalized transmission entries to <4.9e-9. A source-weighted integral explains why channels do not sum to one or determine a unique spectrum.

## Analogue inputs — transient invariance, loading and UV ratios

**Queries/angles.** `Experimenting with RC and RL series circuits using smartphones Torriente Garcia 2023`; `nrf52840 SAADC acquisition time source resistance`; `silicon photodiodes technical information linearity spectral response dark current`; `ultraviolet sensor ML8511 spectral responsivity ADC offset calibration datasheet`. Covers an analogous transient experiment, the physical ADC front end, radiometric conversion and a second affine-invariant observable.

**Selected five references.**

- `torriente2023rc`: Torriente-García, Muñoz-Pérez, Martí, Monteiro, Castro-Palacio and Monsoriu, *Experimenting with RC and RL series circuits using smartphones as signal generators and oscilloscopes*, Rev. Bras. Ens. Fís. 45, e20230143 (2023), [10.1590/1806-9126-RBEF-2023-0143](https://doi.org/10.1590/1806-9126-RBEF-2023-0143). [Authors' manuscript](https://arxiv.org/html/2303.16249v3) and [institutional final-paper record](https://www.colibri.udelar.edu.uy/jspui/handle/20.500.12008/42287) read; transient circuit model, authors and year verified. Only the separation of timescale from amplitude motivates the comparison.
- `nrf52840`: [Nordic manufacturer product specification](https://docs-be.nordicsemi.com/bundle/nRF52-Series-PS/raw/resource/enus/nRF52840_PS_v1.0.pdf), original cited edition retained; the manufacturer's indexed v1.1 SAADC §§6.23.1/6.23.1.1 corroborates sampling capacitance, sequential conversion and acquisition-time/source-resistance dependence. Direct raw PDF fetches returned 530, so no numerical ENOB/accuracy specification is newly asserted.
- `arduinocore`: [pinned ArduinoCore-mbed 4.5.0 implementation](https://raw.githubusercontent.com/arduino/ArduinoCore-mbed/4.5.0/cores/arduino/wiring_analog.cpp), `read_resolution=10` and conversion read. Hardware maximum resolution is not substituted for this configured resolution.
- `hamamatsuPD`: [Hamamatsu *Technical Note: Si Photodiodes*](https://www.hamamatsu.com/content/dam/hamamatsu-photonics/sites/documents/99_SALES_LIBRARY/ssd/si_pd_kspd9001e.pdf), December 2025 date and §§2-2/2-3/2-4/2-6 checked. Separates linearity, load-dependent saturation, responsivity, dark/noise and response speed; no detector model is falsely assigned to the generic external UV example.
- `gum`: [JCGM 100:2008](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf), coefficient covariance and uniform within-code uncertainty model, with the repeated-code independence caveat.

**Considered/excluded.** [LAPIS ML8511 original datasheet](https://cdn.sparkfun.com/datasheets/Sensors/LightImaging/ML8511_3-8-13.pdf) and manufacturer reference-board manual were read: an instructive analogue UV sensor, but the example does not specify this detector, so neither its 365-nm slope nor dark voltage is assumed. Microchip acquisition-time guidance considered, then rejected in favour of the actual Nordic architecture. General phyphox citation removed to keep circuit and detector sources central.

**New analysis.** Six checked observation rows independently recomputed from counts; first three sample/dark/reference triples give transmissions 0.500, 0.400, 0.283333. Uncorrected ratios are 0.508197, 0.409836, 0.295082. Their difference establishes why a common voltage-scale cancellation does not justify dropping optical/electrical background. Original RC reductions remain untouched.

## Verification record

- Independent Luna numeric audit: separate calculations confirmed representative windows, trapezoidal integrals, Magnus transforms, code-step regression, UV ratios and pressure-domain counts; no numerical mismatch found.
- `python3 docs/papers/analysis/revision_core.py example-data`: standard-library extension succeeds and emits JSON with all seven slugs. Formatting and final build/render checks are recorded below after completion.
- Main/reference inputs are read-only; temporary bibliography merging and compilations occur exclusively in `docs/papers/output/core-check`.

Final checks (all exit 0):

- `ruff check docs/papers/analysis/revision_core.py` and `ruff format --check docs/papers/analysis/revision_core.py`.
- `python3 docs/papers/analysis/revision_core.py example-data`, final output `output/core-check/revision-core-metrics.json`.
- Citation-key resolution, reference counts (6/5/5/4/6/5/5), auxiliary-path existence and figure-caption/prose checks in a focused standard-library script.
- `latexmk -pdf -interaction=nonstopmode -halt-on-error <slug>.tex` for all seven wrappers, against source copies and a temporary bibliography merged by key under `output/core-check`. No unresolved citations, LaTeX warnings or overfull boxes in the final logs. Existing wrapper titles/authors remain unchanged.
- `pdftoppm -png -r 105 <slug>.pdf <slug>` for every final PDF. All seven PDFs have two pages. Every final page (14 total) was opened and visually inspected after a concision pass eliminated nearly empty third reference pages; no clipped diagrams, table cells, labels or references remain.

The final concision pass removed repeated standalone conclusions and duplicated instructions; all new numeric findings, physical equations and selected references remain. Final manuscript SHA-256 prefixes, in the order above: accelerometer `2fffea662c11`, gyroscope `2d85ff1605ae`, magnetometer `06a23d908f7b`, pressure `6ef099c38f5f`, temperature-humidity `95cfc4c6d4d0`, light-rgb `cbf307fc4123`, analog-inputs `5946635b9d2f`.

Status: ready for the parent's requested independent review and collection integration. No known scientific or build blockers. No example input, experiment XML, firmware, original analysis module, shared bibliography, common typography or original figure was edited.
