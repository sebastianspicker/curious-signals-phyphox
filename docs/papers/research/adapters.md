# Adapter-paper literature and numerical research

Research completed 26 October 2026. The ten papers use eleven primary example tables. Primary models, measurement methods and device documentation were searched separately; citations were selected for a concrete claim rather than to lengthen reference lists. An accessible manufacturer document hosted by an archive remains identified as that manufacturer's document. Existing verified keys are reused without duplicating their entries in adapters.bib. No source's reported instrument performance is assigned to these adapters.

## greenhouse-single

Queries/angles: `greenhouse effect classroom experiment sensor heating radiation convection temperature thermometer thermal response primary paper`; `temperature sensor time constant self heating radiation error calibration paper`; `Burt response times meteorological air temperature sensors`; radiation-induced indoor sensor errors and greenhouse ventilation models.

Read: Burt and de Podesta, response-time theory and measured ventilation dependence (publisher full text); Lundström and Mattsson, heat-balance model, reference apparatus and radiation-error discussion (publisher content and institutional full text); BMP280 manufacturer description of the compensation temperature; Boulard and Baille's greenhouse heat/moisture/ventilation model. Considered the 2001 Journal of Geoscience Education classroom greenhouse experiment and Vovna et al. 2020 low-cost temperature-sensor calibration. Excluded the former because its gas-production and enclosure interventions do not identify this one-tag thermal response; excluded the latter as a less direct discussion of radiation/response than the selected papers.

Selected keys and claims:
- `burt2020`: thermal time constant belongs to the mounted sensor and airflow conditions. [Publisher, verified authors/title/year/DOI](https://doi.org/10.1002/qj.3817); [institutional full text](https://centaur.reading.ac.uk/90725/9/qj.3817.pdf).
- `lundstrom2020`: probe temperature reflects competing radiation and convection, so it need not equal air temperature. [DOI](https://doi.org/10.1016/j.expthermflusci.2020.110082); [author-institution full text](https://hig.diva-portal.org/smash/get/diva2%3A1412981/FULLTEXT01.pdf).
- `bmp280`: reported temperature supports the barometer's compensation and is a die indication. [Manufacturer](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf).
- `boulard1993`: a greenhouse heat balance also involves ventilation/moisture, preventing a one-die trace from identifying a unique gas greenhouse mechanism. [DOI](https://doi.org/10.1016/0168-1923(93)90001-X).

Analysis: measured baseline 0–55 s; heating fit 65–235 s with onset 60 s; fixed-baseline, profiled-amplitude least squares. The 239–240 s discontinuity is retained and discussed, never fitted away. The exported 22°C baseline differs from the observed 22.701°C lamp-off mean.

## sensortag-environmental

Queries/angles: `HDC1000 humidity sensor dynamic response calibration humidity temperature lag primary paper`; `low cost humidity sensors calibration response time hysteresis`; local saturation pressure, humidity fixed-point calibration and asynchronous thermal channels.

Read: HDC1000 datasheet Rev. C (capacitance, temperature, response/thermal-mass notes); BMP280 datasheet; Alduchov–Eskridge Magnus approximation; Greenspan saturated-solution fixed points and uncertainties. Considered Cunningham 1998 microclimate sensor study, Vovna et al. 2020 greenhouse temperature calibration and Electronics 2022 response/information-quality comparisons. Excluded the conversion-time comparisons because electrical conversion duration is not a mounted sensor's humidity step response; the other devices do not calibrate this particular thermal arrangement.

Selected:
- `hdc1000`: paired local T/RH and thermal/airflow dependence. [TI Rev. C](https://www.ti.com/lit/ds/symlink/hdc1000.pdf).
- `bmp280`: a second package temperature has its own role and thermal path. [Bosch](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf).
- `alduchov1996`: Magnus-form saturation pressure for calculating local vapour pressure, not a new humidity calibration. [DOI](https://doi.org/10.1175/1520-0450(1996)035%3C0601:IMFAOS%3E2.0.CO;2).
- `greenspan1977`: equilibrium humidity references require controlled temperature and equilibration. [NIST full text](https://nvlpubs.nist.gov/nistpubs/jres/81A/jresv81An1p89_A1b.pdf), DOI 10.6028/jres.081A.011.

Analysis: both 48-row services are primary; each uses native receive windows. Only the temperature-difference diagnostic uses nearest-neighbour pairing with ≤0.5 s tolerance. The 0.4 s pair offset is not called latency or thermal lag. Vapour pressure is computed from the paired HDC1000 T/RH within each observation before averaging.

## puck-light

Queries/angles: `LED photodiode sensor Mims sun photometer 1992 Applied Optics spectral`; `Dietz Yerazunis Leigh Very Low Cost Sensing Communication Bidirectional LEDs 2003`; detector spectral weighting, relative attenuation, dark/reference ratio uncertainty, Puck light API and sampling limits.

Read: Mims 1992 original three-page optical detector report; Dietz et al. MERL report/proceedings record and detector-circuit discussion; official Puck light API. Considered Mims 1999 student haze network, Mims 2002 LED sun-photometer stability, and Lau et al. 2004 fused-LED colorimetry. Excluded atmospheric retrieval and fused-sample numerical performance as apparatus-specific, redundant with the selected detector-principle references and unrelated to this simple attenuation ratio.

Selected:
- `mims1992`: LEDs can serve as spectrally selective detectors; this supports source/detector weighting, not Puck responsivity values. [Publisher](https://opg.optica.org/abstract.cfm?uri=ao-31-33-6965), DOI 10.1364/AO.31.006965; original text also inspected at https://patarnott.com/atms360/pdf_atms360/02860Mims.pdf.
- `dietz2003`: LED/microcontroller sensing principle. [Author laboratory and verified bibliographic record](https://www.merl.com/publications/TR2003-35), DOI 10.1007/978-3-540-39653-6_14. Authors Paul Dietz, William Yerazunis, Darren Leigh; UbiComp 2003, pp.175–191.
- `pucklight2026`: relative 0–1 output, spectrum dependence and ≤5 Hz calls. [Official API](https://www.espruino.com/Reference#l_Puck_light).

Analysis: bracketing receive-time windows are 1–9, 12–18, 24–36, 42–48 and 52–59 s. Equal weight is assigned to each bracket mean. Negative near-dark precomputed ratios remain diagnostic values; the adapter's nonnegative-transmission XML gate displays them as gaps. Device-column time is used in the plot, and the clock relation is fitted without claiming an external time calibration.

## cc2541-accelerometer

Queries/angles: `MEMS accelerometer six position calibration bias scale factor uncertainty`; `six position accelerometer calibration low cost MEMS experimental`; `Allan variance inertial sensors calibration noise model`; KXTJ9 code width, gravity projection and static calibration.

Read: TI CC2541 sensor identification; official phyphox legacy definition; Stančin–Tomažič full model and static calibration; Tedaldi et al. multi-orientation calibration. Considered Liu et al. 2016 improved six-position Kalman method (DOI 10.12720/jcm.11.5.516-522), and Allan variance. Excluded their numerical error reductions, Kalman model and long-term stochastic metrics because the example's identical static codes cannot establish them.

Selected:
- `cc2541quick`: KXTJ9 identity, [TI SWRU324B](https://www.ti.com/lit/ug/swru324b/swru324b.pdf).
- `cc2541protocol`: legacy signed byte path and intended scaling, [official adapter page and linked source](https://phyphox.org/wiki/index.php/Texas_Instruments_SensorTag_CC2541).
- `stancin2014`: twelve-parameter scale/offset/nonorthogonality model and defined static positions, [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4179040/), [DOI](https://doi.org/10.3390/s140814885).
- `tedaldi2014`: multi-orientation IMU calibration; does not validate the example sensor, [DOI](https://doi.org/10.1109/ICRA.2014.6907297).

Analysis: static windows 0–8,16–19,26–29,46–49,56–60 s. atan2 of mean gravity components, signed byte quantisation, unique raw triplet count and norm changes. Zero observed SD is discussed as code locking, not zero uncertainty.

## cc2541-gyroscope

Queries/angles: `MEMS gyroscope six position calibration bias scale experimental`; `MEMS inertial sensor Allan variance bias instability measurement`; `time efficient calibration MEMS 3D accelerometer gyroscopes`; signed-rate integration and finite timestamp windows.

Read: TI sensor identity, legacy phyphox service, Stančin–Tomažič calibration model and El-Sheimy et al. Allan-variance method. Considered turntable/deep-learning bias correction in Yampolsky et al. (existing key), and generic smartphone gyroscope teaching demonstrations. Excluded them because direct signed-rate and offset inference needs no learned model, and phone demonstrations do not establish external IMU-3000 sensitivity.

Selected:
- `cc2541quick`, `cc2541protocol`: identity and legacy full-span conversion, [TI](https://www.ti.com/lit/ug/swru324b/swru324b.pdf), [phyphox](https://phyphox.org/wiki/index.php/Texas_Instruments_SensorTag_CC2541).
- `stancin2014`: calibration requires independent nonzero motions as well as stationary bias, [DOI](https://doi.org/10.3390/s140814885).
- `elsheimy2008`: Allan variance relates drift/noise to averaging time, requiring long stationary observations, [DOI](https://doi.org/10.1109/TIM.2007.908635).

Analysis: actual changing-rate extrema (9–11,19–21 s) are not presented as calibration plateaux; settled y interval 42–48 s; residual stationary 56–60 s. Trapezoidal integration over actual retained samples inside40–50s, with no invented boundary samples or count clock.

## cc2541-magnetometer

Queries/angles: `triaxis magnetometer calibration magnetic domain ellipsoid hard iron soft iron experimental`; `magnetometer ellipsoid calibration uncertainty soft iron nonorthogonality`; raw chip sensitivity versus BLE scaling; constant-field rotation versus external field perturbation.

Read: Renaudin et al. full error model and ellipsoid geometry, Kok–Schön inertial-assisted calibration, MAG3110 Rev.9.2 sensitivity table and official legacy packet definition. Considered basic compass tutorials and a scalar hard-iron-only approach. Excluded them as insufficient for soft-iron/misalignment and absolute heading. Renaudin full text was inspected via the original article reproduction; author/title/DOI verified against publisher/DOI records.

Selected:
- `renaudin2010`: complete offset/scale/nonorthogonality and magnetic deviation model, [DOI](https://doi.org/10.1155/2010/967245).
- `kok2016`: inertial constraints on calibration and frame alignment, [DOI](https://doi.org/10.1109/JSEN.2016.2569160).
- `mag3110`: nominal 0.10 µT/LSB chip sensitivity, [NXP-hosted manufacturer PDF](https://www.nxp.com/docs/en/data-sheet/MAG3110.pdf).
- `cc2541protocol`: physical conversion still needs firmware verification, [official definition links](https://phyphox.org/wiki/index.php/Texas_Instruments_SensorTag_CC2541).

Analysis: both raw and corrected components enter the analysis; their exact differences identify the applied (5,-3,8)µT correction, not a calibrated truth. Norms for0–15,27–35,42–44,53–60s distinguish reorientation from a field change. Limited rotational coverage is not claimed to establish ellipsoid parameters or heading.

## cc2541-humidity

Queries/angles: `humidity fixed points binary saturated aqueous solutions NIST Greenspan`; `uncertainty evaluation humidity sensors calibrated saturated salt solutions`; `relative humidity sensor calibration salt solutions uncertainty temperature measurement points`; SHT21 status mask/intercepts and vapour-pressure pulse.

Read: SHT21 datasheet equations, mounting/hysteresis guidance, Greenspan original NIST fixed-point analysis and Alduchov–Eskridge saturation model. Considered Lu and Chen 2007 uncertainty evaluation (Measurement40:591–599, DOI10.1016/j.measurement.2006.09.012); its abstract was verified but full publisher content was unavailable, so its quantitative uncertainty claims are not used. Also excluded generic humidity-sensor reviews in favour of the manufacturer and primary reference method.

Selected:
- `sht21`: correct intercepts, low-bit masking and moisture-sensitive mounting, [Sensirion version5](https://sensirion.com/media/documents/120BBE4C/63500094/Sensirion_Datasheet_Humidity_Sensor_SHT21.pdf).
- `cc2541protocol`: paired local words on one receive clock, [official source links](https://phyphox.org/wiki/index.php/Texas_Instruments_SensorTag_CC2541).
- `greenspan1977`: equilibrium reference, temperature and uncertainty, [NIST](https://nvlpubs.nist.gov/nistpubs/jres/81A/jresv81An1p89_A1b.pdf).
- `alduchov1996`: local saturation-pressure reduction, [DOI](https://doi.org/10.1175/1520-0450(1996)035%3C0601:IMFAOS%3E2.0.CO;2).

Analysis: initial0–10s,pulse26–35s,recovered50–60s. Per-observation vapour pressure and correct status-masked conversion. The hypothetical wrong intercept is applied to the actual initial mean and reported as the18-point conversion error; no physical humidity calibration is inferred.

## cc2541-pressure

Queries/angles: `systematic MEMS sensor calibration framework BMP085 BMP180 T5400`; `pressure sensor calibration temperature pressure reference MEMS experimental hysteresis`; `EPCOS T5400 pressure sensor calibration coefficients datasheet`; chamber pressure-decay inference versus isothermal gas amount.

Read: Dickow–Feiertag full paper (actual T5400/BMP085/BMP180 calibration at multiple pressures/temperatures); manufacturer T5400 memory-transfer and operating-range description; official phyphox pressure coefficient signs/state path and equations. Considered generic pressure-altitude and leak-test articles; excluded altitude because the example is an imposed chamber pressure excursion, and excluded flow claims without volume/temperature constraints. The manufacturer's basic datasheet does not print the polynomial, so the article attributes that equation to the published legacy definition rather than claiming otherwise.

Selected:
- `dickow2015`: calibration point selection, withheld test conditions and temperature/pressure dependence, [full text and bibliographic metadata](https://jsss.copernicus.org/articles/4/97/2015/), DOI10.5194/jsss-4-97-2015.
- `t5400`: actual device calibration parameters precede raw conversion, [manufacturer PDF archive](https://cdn.sparkfun.com/datasheets/Sensors/Weather/T5400.pdf), p.8.
- `cc2541protocol`: signed UT, unsigned UP, mixed coefficient signs and polynomial, [linked original pressure definition](https://phyphox.org/wiki/images/f/f5/TI_SensorTag_CC2541_Pressure.phyphox).

Analysis: baseline0–18s,peak26–30s,release52–60s; time regression28–44s. Empirical raw-word slope is explicitly local to the narrow temperature range. Fractional pressure decay is not converted to molar flow; gas temperature and chamber volume are unprovided independent quantities.

## cc2541-ir-temperature

Queries/angles: `infrared temperature measurement uncertainty unchopped thermopile case thermal gradients`; `TMP006 object temperature emissivity calibration user guide blackbody`; `calibration uncertainty MEMS thermopile imager emissivity thermal gradient blackbody`.

Read: TMP006 Rev.E voltage/die registers and object-temperature equations; original TI SBOU107 calibration/geometry guide (primary document reproduced at SparkFun); Sebastián et al. thermopile gradient model and indexed abstract. Authors independently verified as Eduardo Sebastián, Carlos Armiens, Javier Gómez-Elvira against bibliographic cross-records. Considered Paes et al.2022 MEMS thermopile-array calibration, DOI10.1016/j.infrared.2021.103978; excluded its array nonuniformity and numerical performance as not transferable to the point sensor. Generic thermal-camera calibration was also excluded.

Selected:
- `tmp006`: signed scale and compensated radiance model, [TI datasheet](https://www.ti.com/lit/ds/symlink/tmp006.pdf).
- `tmp006guide`: surface emissivity, target coverage and application sensitivity against a contact reference, [TI primary guide archive](https://cdn.sparkfun.com/datasheets/Sensors/Temp/sbou107.pdf), sections3,5,6. The verified manufacturer-document archive URL is retained in BibTeX because the former TI guide URL was unavailable.
- `sebastian2011`: case thermal gradients add uncertainty not represented by a single die reading, [DOI](https://doi.org/10.1016/j.infrared.2010.12.038). No numerical performance is transplanted from its Mars radiometer context.

Analysis: target/die/voltage means in0–9,12–19,28–38,42–48,53–60s; hot-state sensitivity scaled±10% while holding other terms fixed. This is a controlled model perturbation, not a confidence interval. The column headed Compensated flux voltage numerically contains u=V−Vos, so the quadratic correction f=u+13.4u² is recomputed from voltage and offset before perturbing S. The independent reconstruction at original S agrees with the stored44.909007°C hot mean. Negative voltage words are retained and interpreted as offset-referenced signal.

## pocketlab-gyroscope

Queries/angles: `PocketLab Voyager gyroscope calibration rotation physics education paper`; `PocketLab Voyager specifications gyroscope data rate`; signed rotation integration, gyro calibration, Allan bias analysis, rigid-body orientation and norm path length.

Read: manufacturer Voyager specifications; actual upstream phyphox Voyager byte order/configuration; Stančin–Tomažič defined-motion calibration; El-Sheimy et al. stochastic stability analysis. Considered PocketLab Voyager LIDAR teaching activity (manufacturer archive, rotating rangefinder/gyro averaging) and generic PocketLab One material. Excluded the first as an apparatus example without independent angular-rate calibration; excluded One because its gyro protocol is not established by the mislabelled archive scaffold.

Selected:
- `voyagerspec`: genuine Voyager range and delivered-rate specification, [manufacturer](https://support.thepocketlab.com/knowledge/pocketlab-voyager-manual).
- `voyagerprotocol`: signed big-endian x8/y6/z10 path and nominal scale, [upstream primary definition](https://github.com/phyphox/phyphox-experiments/blob/master/bluetooth/PocketLab%20Voyager%20Acc%20Gyro%20Mag.phyphox).
- `stancin2014`: calibration needs defined motions and axis geometry, [DOI](https://doi.org/10.3390/s140814885).
- `elsheimy2008`: longer stationary sequences for averaging-time-dependent stability, [DOI](https://doi.org/10.1109/TIM.2007.908635).

Analysis: stationary0–9s; smooth extrema19–21,29–31,49–51s are not calibration plateaux. Signed x, absolute x and vector-norm integrals use the identical actual sampled extent inside10–40s. Three-dimensional noncommutativity prevents zero net x from becoming a full orientation-return claim.
