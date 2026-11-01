# Optics research and reduction record

Revision: October 2026. Scope: six short articles and their editable companions. All ten assigned example observations are read only. Article captions use **Example data.** Research/source metadata is kept here rather than inserted as a data-origin note in the articles. Literature claims are separated from results calculated from the example data.

## Broad-band filter transmission (`rgb-filter-transmission`)

Search angles included optical definition and reference geometry, practical low-cost filter experiments, spectral response and ambiguity, and the exoplanet-atmosphere analogy. Queries: `dark reference measurement ratio transmission spectrophotometer Beer Lambert law uncertainty source primary method`; `physics education smartphone light sensor coloured transparent filters transmission experiment paper`; `Resolution of Light Transmission via Arduino-Based STEM Education Material`; `exoplanet transmission spectrum broadband photometry filter effective wavelength transit depth atmospheric height paper`; `APDS-9960 data sheet AV02-4191EN`.

Selected sources, opened/read and metadata checked:

- `ErolDemir2024`: Erol and Demir, JPFI 20(2), 165–172 (2024), DOI [10.15294/jpfi.v20i2.17564](https://doi.org/10.15294/jpfi.v20i2.17564). Journal article/PDF describes red and blue acetate, thickness dependence and a baffled Arduino arrangement. Supports the analogous laboratory geometry; no efficacy or current-apparatus performance claim is imported. Primary PDF: <https://journal.unnes.ac.id/journals/JPFI/article/download/17564/2180/50257>.
- `Hosker2018`: Bill S. Hosker, J. Chem. Educ. 95(1), 178–181, DOI [10.1021/acs.jchemed.7b00548](https://doi.org/10.1021/acs.jchemed.7b00548). ACS abstract and author repository <https://researchspace.bathspa.ac.uk/10244/> read. Uses wavelength-selective smartphone spectrophotometry; supports the distinction from unfiltered RGB projection, not a claim that this apparatus is a spectrometer.
- `BurkeMavrodineanu1983`: title page and method sections of NBS SP260-81, DOI [10.6028/NBS.SP.260-81](https://doi.org/10.6028/NBS.SP.260-81), <https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nbsspecialpublication260-81.pdf>. Defines transmission/reference conditions and discusses boundary/interreflection/collection effects. Author order follows title page rather than reversed catalog display.
- `apds9960` (existing key): Avago APDS-9960, <https://docs.broadcom.com/doc/AV02-4191EN>. Spectral-response and RGBC integration/saturation sections read. Supports channel overlap and device-specific response, not lux calibration.
- `Pont2008`: Pont, Knutson, Gilliland, Moutou and Charbonneau, MNRAS385(1),109–118, DOI [10.1111/j.1365-2966.2008.12852.x](https://doi.org/10.1111/j.1365-2966.2008.12852.x), author preprint <https://arxiv.org/abs/0712.1374>. Read abstract/method discussion: wavelength-resolved effective transit radius, haze, stellar and instrumental effects. Earns its place by bounding the atmospheric analogy.

Considered/excluded: Malisorn et al., Phys. Educ.55,015012, DOI10.1088/1361-6552/ab51ea (primary university metadata) is a sound smartphone liquid absorption/scattering analogue but redundant with Erol/Hosker. Camera calibration studies by Burggraaff et al.2019 and Ciaccheri et al.2023 concern additional imaging pipelines; device datasheet and explicit weighted-integral model are more direct here. The source archive's AG2024 XML slide30 motivates the filter/atmosphere question; it is not an independent photometric validation.

Reduction: all 1201 RGB rows are plotted; one-second half-open device-time windows centre on 5,15,25,35,45s. The trajectory continuously changes, so these are **local turning windows**, not settled plateaux. Separate specified reference counts and the observed 4.5–5.5s reference are retained. The blue extremum is0.77480 under the first normalization and0.84660 under the second. No stationary-transmission standard error is inferred from transition scatter.

## Independently timed inverse-square photometry (`illuminance-distance`)

Queries/angles: `inverse square law light extended source laboratory experiment photometry source distance uncertainty NIST`; `inverse square law daylight Vera Rivera Ortiz 2014`; `Investigative photometry experiments on planar extended-light sources`; `inverse square law finite photosensitive area Shibuya`; `OPT3001 exponent mantissa conversion result register`. Searched source geometry, background isolation, calibration, decoder and asynchronous association.

Selected primary sources:

- `zong2018photometry`: Zong, Nadal, Tsai and Miller, NIST SP250-95 (2018), DOI [10.6028/NIST.SP.250-95](https://doi.org/10.6028/NIST.SP.250-95). Official catalog <https://www.nist.gov/publications/nist-measurement-services-photometric-calibrations-0> verifies date/authors; source-distance/aperture and uncertainty sections of <https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.250-95.pdf> support inverse-square use in the far field and separation of spectral/length calibration.
- `vera2014`: Vera, Rivera and Ortíz, Eur.J.Phys.35,015015 (2014), DOI [10.1088/0143-0807/35/1/015015](https://doi.org/10.1088/0143-0807/35/1/015015). Publisher abstract/metadata read; full text blocked by publisher crawler policy. Claim is limited to documented design purpose: isolating source falloff in daylight, with no borrowed numerical result or detailed procedure.
- `campione2024`: Campione, Pietropaolo and Bussetti, Eur.J.Phys.45,065301 (2024), DOI [10.1088/1361-6404/ad6e44](https://doi.org/10.1088/1361-6404/ad6e44). University author record <https://www.boa.unimib.it/handle/10281/513384> and primary full-text search extraction read; direct PDF subsequently returned403. Supports departure from point-source decay for planar extended sources, not a universal source-size rule.
- `opt3001` (existing): official TI Rev.C, <https://www.ti.com/lit/ds/symlink/opt3001.pdf>. Result-register exponent/mantissa conversion and spectral-response sections read. Used for exact digital decode and distinction from complete mounted-instrument accuracy.

Excluded/redundant: Shibuya, Kitaguchi and Iwanaga2020, DOI10.1177/1477153519871324, primary abstract read; finite detector area is pertinent but overlaps the broader finite-geometry discussion without being constrained by the example aperture. Commercial inverse-square “five-times” rules and Wikipedia were excluded in favour of NIST/extended-source research. Generic phyphox references were not needed for the optical argument.

Reduction: both clock streams used. Actual previous mouse time is located by bisection; source distance r=.15m+.0002m/count*d. Decoder independently recomputed from uint16. Fifteen stationary windows [4j+1,4j+3.5)s have three light observations each; log OLS of window means yields n2.001221. Leave-one-window range1.996604–2.003198 is a sensitivity range, not a confidence interval. A ±1mm common-origin perturbation gives1.996199/2.006240. First mouse increment is250counts and cannot be one signed-int8 HID report: article treats that position as an initial anchor, and no decoder-validation claim is made from it. Subsequent integrated motion and actual-time pairing are analyzed honestly without changing any inputs.

## Paired ruler photometry (`illuminance-distance-manual`)

Separate search focus: `manual inverse square light ruler source origin background uncertainty`; smartphone/extended-source experiments above; APDS integration and relative response. Re-read the distance-origin and background sections for the manual observation model rather than assuming electronic distance acquisition. Selected `vera2014` for source/background separation, `zong2018photometry` for defined source/aperture distance, `apds9960` for the detector working range, and `campione2024` for finite-source interpretation. URLs and metadata are verified above; each claim is independently relevant to this adapter.

Excluded: mouse/HID documentation is irrelevant to a manually read coordinate. NIST absolute calibration uncertainty numbers are not transplanted to an uncalibrated count scale. Commercial ranging and smartphone camera distance papers address a different independent variable and were omitted.

Reduction: both the full light record and all12 paired ruler observations are used. Snapshot device time/receive time/count match their corresponding raw observation. Mean windows [5j+1.5,5j+3.5)s use the same12 positions; no ruler interpolation. Background10counts is retained. Exponents1.986053(snapshot) and1.988005(mean); product scatter1.82119 versus0.57978 count m² is descriptive across states. A ±1mm origin sensitivity gives1.982401/1.993605. No sqrt(N) uncertainty reduction is claimed because temporal correlation and shared geometrical errors are not established independently.

## Settled-angle polarization (`malus-law`)

Queries: `Malus law smartphone Monteiro Stari Cabeza Marti 2017 polarization`; `Malus law experiment smartphone polarizer non ideal extinction ratio angle offset fit`; `Arduino-based experiment demonstrating Malus 035034`; `AN ARDUINO BASED EXPERIMENT TO PROVE AND TEACH MALUS LAW`; `Realization of Polarization Malus Colak 2020`. Angles covered model, angular calibration, relative detector linearity, floor/extinction and analogous instrumentation.

Selected:

- `monteiro2017malus`: Monteiro, Stari, Cabeza and Martí, Phys.Teach.55(5),264–266 (2017), DOI [10.1119/1.4981030](https://doi.org/10.1119/1.4981030). Full author preprint <https://arxiv.org/pdf/1607.02659> read. Supports LCD + orientation/light apparatus and fixed-spectrum proportionality; its exponent1.96±.02 is not presented as an outcome here.
- `freitas2018malus`: Freitas, Cena, Alves and Goncalves, Phys.Educ.53,035034, DOI [10.1088/1361-6552/aab43d](https://doi.org/10.1088/1361-6552/aab43d). Primary publisher/ADS abstract read, <https://scixplorer.org/abs/2018PhyEd..53c5034F/abstract>. Mechanically coupled potentiometer measures analyzer rotation; cited to motivate explicit angle observation, without borrowing an accuracy claim.
- `onder2021malus`: Bilal Önder, Önder and Oğur, J.Eng.Sci.Design9(3),833–842, DOI [10.21923/jesd.874073](https://doi.org/10.21923/jesd.874073). Primary journal page <https://dergipark.org.tr/en/pub/jesd/article/874073> and full paper <https://dergipark.org.tr/en/download/article-file/1554632> read. Baffled Arduino/LDR arrangement motivates suppression of stray light; does not validate APDS linearity.
- `apds9960`: primary RGBC response/integration specification as above; source-spectrum and linearity relevance only.

Considered: Çolak/Erol2020, JPFI16(1),9–13, DOI10.15294/jpfi.v16i1.18571. Primary page and complete five-page paper <https://pdfs.semanticscholar.org/9606/cc0dd828c0eebd560ed2b1a6bec3374168a8.pdf> read. The rail geometry is useful, but duplicates the selected Arduino studies; the abstract's “square of angle” wording is imprecise and is not repeated. ETH's2021 teaching instruction PDF was search-readable but subsequently403; not needed in the selected list. Older Gladden1950 and Fakhruddin2008 metadata were found but full text not inspected, so neither is cited.

Reduction: all10 angle snapshots and full continuous light record used. Windows [6j+1,6j+5.5)s define stationary means. Linear least squares in 1,cos2θ,sin2θ yields floor, amplitude and phase. Snapshot/mean residual RMS7.1250/.513697counts. No phase confidence interval or sub-degree hardware accuracy is inferred. The fixed entered normalization retains reference mismatch, while fitted floor13.0419/amplitude1020.4376 explain its residuals.

## Indicative colour temperature (`colour-temperature`)

Queries: `McCamy 1992 Correlated color temperature as explicit function chromaticity DOI formula`; `CIE Planckian radiation temperature TN013 definition`; `RGB sensor color temperature calibration spectral mismatch LED chromaticity`; `TAOS TCS3414CS RGB XYZ -.14282 1.54924`; APDS query above. Angles covered physical definition, polynomial/sign/domain, sensor-matrix provenance, calibration and spectral nonuniqueness.

Selected:

- `McCamy1992`: Color Res.Appl.17(2),142–144, DOI [10.1002/col.5080170211](https://doi.org/10.1002/col.5080170211); Wiley primary abstract/metadata read. Supports explicit cubic approximation from chromaticity, not an unconditional accuracy interval.
- `CIE2022TN013`: Young, Goodman, Ohno and Ledig, CIE TN013:2022, DOI [10.25039/TN.013.2022](https://doi.org/10.25039/TN.013.2022). Official publication page and complete note <https://files.cie.co.at/CIE_TN_013_2022.pdf> read. Supports distinction between CCT and physical emitting temperature and applicability near Planckian radiation.
- `Smith2009TAOSAN000517`: Joe Smith, TAOS Designer's Notebook25,Rev.C(Feb2009), <https://look.ams-osram.com/m/57eb503c1d12d800/original/TCS34xx-AN000517.pdf>. Pages3–6 explicitly derive the **same matrix for TCS3414CS**, using6500K fluorescent,3000K fluorescent and60W incandescent references; discuss fitting new source-family matrices and warn about far-off-locus green. Exact adopted n sign/cubic verified. Accuracy statements about correctly known chromaticities are not transferred to APDS counts.
- `apds9960`: device-specific RGBC spectral response, official datasheet as above. This fourth reference earns its place by establishing the matrix-transfer problem.

Considered/excluded: Hernández-Andrés, Lee and Romero1999, Appl.Opt.38,5703–5709, DOI10.1364/AO.38.005703, primary abstract read; wider daylight/skylight approximation is useful but not required for this limited example. Burggraaff et al.2019, DOI10.1364/OE.27.019075, and recent camera calibration2025 work support per-device calibration, but different camera pipelines are less direct than the sensor-specific TAOS/APDS contrast. Generic online CCT calculators and unsupported2000–12500K claims excluded.

Reduction: all raw RGBC values independently reduced with dark(3,2,2,1), donor matrix and internally consistent McCamy convention. Four interior windows give2547.879,3934.657,6113.835,2549.536K; SD25.129,18.294,90.764,25.567K are descriptive single-value scatter. Mean-of-conversion versus conversion-of-mean is explicitly distinguished. No CCT accuracy or Planckian-distance inference is manufactured from these values.

## Sampling and short-feature detectability (`detector-characterization`)

Queries: `sampling light curve finite integration time Kipping 2010 binning sinning`; `Pont Zucker Queloz 2006 red noise transit detection`; `Communication in the Presence of Noise Shannon 1949`; `APDS-9960 integration gain saturation`; feature-duration versus cadence research in Price/Rogers2014 and transit SNR2023. Searched reconstruction assumptions, exposure convolution, correlated uncertainty, actual timing and detector behavior.

Selected:

- `shannon1949`: C.E.Shannon, Proc.IRE37(1),10–21, DOI [10.1109/JRPROC.1949.232969](https://doi.org/10.1109/JRPROC.1949.232969). IEEE primary metadata/abstract and original-paper reprint extraction <https://www.math.unl.edu/~bdeng1/Teaching/math943/Topics/Genetics/Shannon1949.pdf> read (direct fetch subsequently timed out). Supports band-limited reconstruction condition, not an assertion that two samples resolve a transient.
- `kipping2010` (existing): D.M.Kipping, MNRAS408(3),1758–1769, DOI10.1111/j.1365-2966.2010.17242.x, complete author paper <https://arxiv.org/pdf/1004.3741> read. Finite integration alters light-curve morphology; decimation is explicitly distinguished from integration.
- `pont2006red`: Pont,Zucker,Queloz,MNRAS373(1),231–242, DOI [10.1111/j.1365-2966.2006.11012.x](https://doi.org/10.1111/j.1365-2966.2006.11012.x), complete author paper <https://arxiv.org/pdf/astro-ph/0608597> read. Supports event-timescale covariance and limits of independent-point significance. Astronomical thresholds/numerical performance are not transplanted.
- `apds9960`: integration/filter specification, distinguished from delivered firmware/BLE/app rate.

Excluded: Price/Rogers2014 and a2023 transit-SNR analysis overlap the selected finite-integration argument and require a parameter-estimation model beyond these four laboratory events. Nominal chip-rate summaries and workshop's historical1.25Hz values are not used as evidence of the present chain's measured performance.

Reduction: full record and the single-row summary are both used. Summary independently checked to rounding. Device differences give19.864918Hz; interval SD.473955ms vs receive4.244605ms. Baseline12≤t≤28s, dark0≤t<9s. Summary entered dark8counts is retained separately from observed mean11.1564counts. Event windows[30,30.5),[34,35),[38,40),[44,48)s. All16 stride phases assessed: the shortest event is missed by6; event counts10/20/40/79 at full rate, coarse ranges0–1/1–2/2–3/4–5. Lag-one correlation and one-second block scatter are descriptive; no independent-replication assumption or fabricated detection probability.

## Final reproducibility and layout checks

`analysis/draft_optics.py` exposes analyze/tables/figures and an independent `check()` fixture: exact affine and inverse-square solutions, known phase/amplitude/floor recovery for Malus response, invalid colour domains and invariance to common clear normalization. The last test verifies that the homogeneous transform cancels the common corrected-clear denominator in chromaticity and CCT; article uncertainty discussion states this explicitly. Raw summary and snapshot association checks run during reduction. All10 assigned primary examples are used exactly once in manuscript metadata. No input observations, XML, firmware or protocol are changed.

Local preview builds use a temporary merged bibliography under the isolated checkout output directory, leaving shared references unchanged. Every article contains one data figure, one in-column apparatus schematic and a compact numerical table. Captions begin “Example data.”; all selected bibliography keys resolve. All pages are rendered with Poppler and inspected at1600-pixel page height. Reproducibility numbers retain full precision; article tables use rounded values without invented confidence intervals.
