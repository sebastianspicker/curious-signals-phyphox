# Photometry research and analysis record

Date: 2026-10-26. Scope: nano-transit, exomoon-photometry, starspot-crossing, eclipsing-binary and seasons-obliquity. Each search covered the physical model, measurement/uncertainty, experimental or educational precedent, and instrument response where it affects the inference. The papers select a small subset of the literature screened below. “Read” distinguishes full primary text from an abstract or metadata record; no inaccessible source is represented as fully examined.

## Nano transit photometry

Searches: “Mandel Agol 2002 analytic light curves planetary transit searches arxiv”; “Kipping 2010 binning is sinning finite integration time transit”; “Pont Zucker Queloz 2006 effect red noise planetary transit detection”; “Exoplanet Hunting in the Classroom Spicker Küpper PDF”; APDS-9960 integration, gain and saturation. These angles connect the inverse geometry, finite response, statistical covariance and an actual classroom apparatus rather than treating the normalized signal as intrinsically calibrated.

Selected five references:

- `transit2024`: Spicker and Küpper, The Physics Teacher 62, 226–229 (2024), [DOI](https://doi.org/10.1119/5.0125305). Publisher metadata and source manuscript in the article archive checked; the journal page was not consistently retrievable. Supports the video-aided physical analogue and its purpose, not validation of the present Nano configuration. Author record also [locates the paper](https://sebastianspicker.com/).
- `mandelagol`: Mandel and Agol, ApJ Letters (2002), [full primary text](https://arxiv.org/html/astro-ph/0210099v1), [DOI](https://doi.org/10.1086/345520). Read uniform-source and limb-darkening sections. Supports distinction between area-ratio special case and brightness-dependent transit models.
- `kipping2010`: Kipping, MNRAS 408, 1758–1769 (2010), [full primary text](https://arxiv.org/html/1004.3741v2), [DOI](https://doi.org/10.1111/j.1365-2966.2010.17242.x). Read effects of integration and numerical response treatment. Supports exposure smoothing and bias; neither BLE cadence nor averaging defines geometric contacts.
- `pont2006`: Pont, Zucker and Queloz, MNRAS 373, 231–242 (2006), [publisher text](https://academic.oup.com/mnras/article/373/1/231/1378493), [DOI](https://doi.org/10.1111/j.1365-2966.2006.11012.x). Read Section 2.3 covariance of depth and discussion of block scatter. Journal pagination verified against publisher, rather than the inconsistent arXiv “journal reference”. Supports avoiding row-count precision under correlated noise.
- `apds9960`: Avago Technologies, APDS-9960 datasheet AV02-4191EN, [official PDF](https://docs.broadcom.com/doc/AV02-4191EN), especially electrical/optical characteristics and ATIME register. Read gain/integration and count-limit definitions. Supports sensor-response conditions, not a measured device error budget.

Considered/excluded: Price and Rogers (2014), “Transit Light Curves with Finite Integration Time”, found through the Kipping search, provides a more detailed Fisher/covariance treatment; excluded as redundant with the selected response and covariance sources for a window-mean analysis. Kipping (2023), “The SNR of a transit”, considered for exposure smoothing, excluded because no detection-probability calculation is made. Generic phyphox or GUM citations would not replace the relevant optical/time-series assumptions and were not added.

Analysis: device-time local baseline windows ±3–6 s and plateau ±1 s around 20, 50, 80 s. Adopted background 10 counts retained explicitly. Local mean depth 0.04259694; event SD 0.00589873. Whole-record extrema depth 0.19298246. Local baseline 115.224 counts exceeds entered reference 110; no dark interval independently identifies an offset. Clock intervals computed independently. No fitted contact times or physical radius.

## Exomoon photometry

Searches: “Sato Asada 2009 mutual transits light curves”; “Kipping LUNA algorithm planet moon transits 2011”; “analytic light curve mutual transits Gordon Agol 2022”; “Heller exomoon detection methods”; classroom exomoon motor lesson and its published metadata. Read multiple generations of the photometric model to distinguish projected overlap from timing dynamics and avoid unqualified radius inference.

Selected five references:

- `exomoonlesson2023`: Küpper and Spicker, “Ein Analogieexperiment zur Suche nach Exomonden”, MNU-Journal 76(3), 223–227 (2023). Publisher [contents/abstract PDF](https://www.mnu.de/images/publikationen/zeitschrift/Heft_3-23/MNU_Inhalt_03_2023_Abstracts.pdf) verifies title/authors/issue; the author-uploaded [published article](https://www.researchgate.net/publication/370844826_Ein_Analogieexperiment_zur_Suche_nach_Exomonden) and supplied proof were read. Source archive anchor: `beitraege-forschung/exomonde/Ph 22-67.pdf`, physical pp.2–8, particularly motor obstruction p.4 and overlap interpretation pp.5–7. Supports physical adaptation and video control, not new efficacy claims.
- `sato2009`: Sato and Asada, PASJ 61, L29–L34 (2009), [full primary text](https://arxiv.org/html/0906.2590v1), [DOI](https://doi.org/10.1093/pasj/61.4.L29). Read mutual-blocking geometry and contrast sign. Supports the apparent brightening when silhouettes overlap.
- `kipping2011`: Kipping, MNRAS 416, 689–709 (2011), [full publisher text](https://academic.oup.com/mnras/article/416/1/689/1216488), [DOI](https://doi.org/10.1111/j.1365-2966.2011.19086.x). Read introduction, geometry and distinction between the moon's own photometric transit and TTV/TDV. Supports why plateau means alone do not supply dynamical parameters.
- `gordon2022`: Gordon and Agol, AJ 164, 111 (2022), [full primary text](https://arxiv.org/html/2207.06024v1), [DOI](https://doi.org/10.3847/1538-3881/ac82b1). Read overlap cases and exposure integration. Supports exact two-body mutual-transit brightness integration; its LUNA comparison notes restrictions/corrections, so the article does not present LUNA as an exact universal geometric solution.
- `pont2006`: primary covariance treatment above. Supports block-dispersion diagnostics without an invented detection significance.

Considered/excluded: Heller's general detection discussions, NASA's 2015 HEK computing account and later candidate news were screened but excluded because they do not improve the characteristic-area reduction and could distract toward changing detection-status claims. Pandora (Hippke and Heller, A&A 2022, DOI 10.1051/0004-6361/202243129) read at publisher discussion; an open photodynamical alternative, redundant here with LUNA plus the exact Gordon/Agol model. Tusnski/Valio moon-and-ring model appears in source bibliography, but rings are not represented by these observations.

Analysis: explicit settled windows for four states; local baseline 115.326 counts and adopted dark10. Extra deficit 0.0282230; overlap brightening 0.0148261; recovery ratio0.525320. One-second block SDs are descriptive fluctuation scales. Same-phase recurrence follows integer Tplanet/Tmoon; this corrects the supplied proof's reversed multiple statement. No orbital fit, moon radius, TTV or TDV.

## Starspot crossing

Searches: “Silva 2003 method spot detection solar-like stars”; “Oshagh stellar spots high precision transit 2013”; “Rackham Apai Giampapa transit light source effect”; baseline and correlated-noise treatment; workshop spot station. This covers local occulted brightness, unocculted-source dilution, false timing signals and the actual proposed physical surface modification.

Selected five references: `agphotometry2024`, `oshagh2013`, `mandelagol`, `rackham2018`, `pont2006`.

- `agphotometry2024`: Küpper and Spicker, “Sensorbasierte Smartphone-Experimente rund um die Exoplaneten-Lichtkurve”, invited AG teacher workshop, Cologne, 2024. Title/authors read on physical p.1 and station on physical p.32 of supplied `beitraege-forschung/ag2024/VortragAGLehrerfortbildungKoeln24_2.pdf`; event verified on the [author's publication list](https://sebastianspicker.com/). No invented DOI or public slide URL. Supports station provenance.
- `oshagh2013`: Oshagh, Santos, Boisse, Boué, Montalto, Dumusque and Haghighipour, A&A 556, A19 (2013), [full primary text](https://www.aanda.org/articles/aa/full_html/2013/08/aa21309-13/aa21309-13.html), [DOI](https://doi.org/10.1051/0004-6361/201321309). Read model assumptions, anomaly amplitude and fitted-parameter consequences. Supports depth/duration/timing bias, not transferring the paper's numerical bias to this example.
- `rackham2018`: Rackham, Apai and Giampapa, ApJ 853, 122 (2018), [full primary text](https://arxiv.org/html/1711.05691v3), [DOI](https://doi.org/10.3847/1538-4357/aaa08c). Read contamination model and discussion. Supports mismatch between a transit chord and the disc-integrated reference, and degeneracy of activity coverage versus photometric modulation.
- `mandelagol` and `pont2006`: full sources above, selected for brightness integration and covariance rather than generic instrumentation references.

Considered/excluded: Silva (2003), DOI10.1086/374324, foundational spot method, bibliographic metadata and author conference account located; primary article could not be retrieved, so no unread detailed claim is attributed to it. SOAP-T (Oshagh et al., A&A549 A35, DOI10.1051/0004-6361/201220173) was considered as the forward-model implementation but the later quantitative study directly supports the discussion. Stellar rotation from recurring spots is excluded because no spot recurrence/rotation analysis is available.

Analysis: explicit baseline, adjacent, crossing and control windows. Local upward contrast0.0291895; fraction of adjacent deficit recovered0.203686. The square-root comparison would give a radius factor0.892364, illustrating model misuse, not a physical radius change. Deeper controls differ from the adjacent plateau and do not establish matched area. One-second block SDs not converted to an overconfident mean uncertainty.

## Eclipsing binary

Searches: Wilson/Devinney original light-curve model; Prša/Zwitter inverse degeneracy and PHOEBE2016 flux integration; accurate masses/radii from detached eclipsing systems; primary/secondary phase conventions, finite integration and covariance; AG2024 turntable proposal. The purpose is to place simple two-light deficits within the wider physical inverse problem without fitting unavailable orbital information.

Selected five references: `agphotometry2024`, `prsa2005`, `prsa2016`, `pont2006`, `torres2010`.

- `prsa2005`: Prša and Zwitter, ApJ628,426–438(2005), [full primary text](https://arxiv.org/html/astro-ph/0503361v1), [DOI](https://doi.org/10.1086/430591). Read inverse-problem and external-constraint sections. Supports correlations and why a double minimum is not a unique physical solution.
- `prsa2016`: Prša et al., ApJS227,29(2016), [full primary text](https://arxiv.org/html/1609.08135v2), [DOI](https://doi.org/10.3847/1538-4365/227/2/29). Read phase, passband intensities, flux integration and finite-exposure sections. Supports the combined luminous denominator and omitted physical effects.
- `torres2010`: Torres, Andersen and Giménez, A&A Review18,67–126(2010), [full primary text](https://arxiv.org/html/0908.2624v1), [DOI](https://doi.org/10.1007/s00159-009-0025-1). Read mass determination and light-curve-analysis sections, not only the catalogue abstract. Supports additional orbital-velocity and geometry requirements for absolute dimensions.
- `agphotometry2024`: physical p.46 is explicitly a development proposal; physical pp.38–39 provide simulation context. The manuscript preserves that distinction.
- `pont2006`: depth/timing covariance source as above; intervals sharing endpoints are also analyzed algebraically.

Considered/excluded: Wilson and Devinney (1971), DOI10.1086/150986, publisher/NASA metadata and abstract verified, primary PDF fetch failed. Excluded from the lean list because Prša2005 and2016 provide accessible primary methods covering the relevant physics. Binary mass catalogues and machine-learning period classifiers were screened but unnecessary: this article neither derives masses nor runs a period-discovery classifier. No half-phase constraint is generalized to eccentric orbits.

Analysis: local windows around4primary/3secondary minima; depths0.3104797 and0.1049063, event SD0.002030 and0.001151. Depth ratio2.95959 remains conditional on overlap for a brightness interpretation. Primary midpoint-onset intervals29.9892,29.9906,30.0045s; mean29.99477s. Entered phase is verified separately with maximum rounding residual1.7e-8, not called a fitted ephemeris.

## Seasons and obliquity

Searches (focused read-only Luna research followed by direct parent inspection): daily mean insolation equations and longitude convention; obliquity and annual latitude distribution; seasons misconceptions and diagram effects; photovoltaic-detector teaching analogies; detector cosine/angular response; APDS sensor response. These distinguish instantaneous measurements, day-length integration and climate rather than treating voltage/counts as temperature.

Selected five references: `galano2020`, `paillard2026`, `apds9960`, `vijeta2021`, `rose2017`.

- `galano2020`: Galano, Monti, Bozzo, Daffara and Testa, “Investigating the Interplay of Practical Work and Visual Representations on Students' Misconceptions: The Case of Seasons”, pp.183–195(2020), [institutional record](https://www.iris.unina.it/handle/11588/820298), [DOI](https://doi.org/10.1007/978-3-030-51182-1_15). Metadata and author/institution abstract read; restricted chapter not represented as fully read. Supports the specific prior use of photovoltaic panels to separate angle/distance. The present article makes no efficacy claim.
- `paillard2026`: Paillard, Climate of the Past22,647–673(2026), [full primary text](https://cp.copernicus.org/articles/22/647/2026/), [DOI](https://doi.org/10.5194/cp-22-647-2026). Read instantaneous and daily equations and longitude convention. Supports distinction between uncalibrated orbital labels and equinox/solstice angles.
- `vijeta2021`: Vijeta, Kapri, Saha, Jaiswal and Sharma, MAPAN36,473–480(2021), [publisher](https://link.springer.com/article/10.1007/s12647-021-00486-6), [open primary text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8236222/), DOI10.1007/s12647-021-00486-6. Supports nonideal angular response as a separate irradiance error source; does not calibrate an APDS package.
- `rose2017`: Rose, Cronin and Bitz, ApJ846,28(2017), [primary PDF](https://www.atmos.albany.edu/facstaff/brose/resources/Publications/Rose_2017_ApJ_846_28.pdf), DOI10.3847/1538-4357/aa8306. Read obliquity/insolation and energy-balance setup. Supports separation of annual input and climate response. The ~55degree annual-gradient reversal is deliberately not invoked to interpret these23.5degree snapshots.
- `apds9960`: official sensor text above. No ideal cosine calibration is inferred from a detector datasheet.

Considered/excluded: Berger1978 long-term insolation (DOI10.1175/1520-0469(1978)035<2362:LTVODI>2.0.CO;2), primary publisher inaccessible, replaced by directly readable Paillard. Atwood and Atwood1996, JRST33,553–563, DOI10.1002/(SICI)1098-2736(199605)33:5<553::AID-TEA6>3.0.CO;2-Q, and Lee2010, Science Education94,985–1007, DOI10.1002/sce.20403, considered for misconception/diagram evidence. Excluded because the paper analyzes physical geometry and makes no generalized claim about learner prevalence or diagram causation. Supplied worksheet context read at `beitraege-forschung/schuelerlabor/Material_SLab_neu_Astropaenz.pdf`, physical pp.11–14; solutions physical pp.6–7. Source attribution remains in this log; no figures/text copied.

Analysis: every recorded snapshot checked against the nearest device-time raw sample. All distances100cm; per-state plateau windows[5i+1,5i+4)s. At zero tilt the high-latitude A/B response declines0.334south/0.325north, inconsistent with an ideal fixed-distance, fixed-hour-angle zero-tilt comparison. Tilted N-S differences0.00367/0.00734 remain small and do not demonstrate hemispheric exchange. No source-cause reconstruction or climate/temperature fit is made. This is a substantive model-consistency result, not a claim of apparatus validation.
