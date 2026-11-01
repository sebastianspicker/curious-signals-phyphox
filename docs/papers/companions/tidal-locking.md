# From Illumination Geometry to Thermal Contrast

*November 2020*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

## Abstract

Illumination geometry determines where energy arrives; thermal exchange determines how a body responds. These stages require different observables. Twelve fixed-distance, labelled detector observations test a seasonal geometry but show large positional changes even at zero tilt and no northern–southern exchange. The corresponding continuous plateaus reveal fluctuations much smaller than those changes. A separate fixed-illumination example gives a day-to-night illuminance ratio of 450 and baseline-corrected thermal contrasts of 19.41 K for the infrared object-temperature indication and 11.48 K for barometer die temperature. A common framework connects incidence angle, rotation and two-region energy balance while retaining the distinction between optical response, absorbed power and temperature. The examples show which symmetry tests constrain the forcing and which additional measurements are needed to identify thermal redistribution.

**Keywords:** Illumination geometry, obliquity, synchronous rotation, thermal contrast, infrared thermometry.

## Geometry before a temperature interpretation

A tilted model under a lamp can represent incidence angle, daylight duration or persistent hemispheric forcing, depending on how it moves. These are distinct questions. A synchronously rotating planet on a circular orbit with negligible obliquity can keep the same hemisphere facing its star. The corresponding condition is $\Omega_{\rm spin}=n_{\rm orbit}$, which requires angular-rate information; a fixed light or temperature contrast does not measure synchronism.

For latitude $\varphi$, stellar declination $\delta$ and local hour angle $h$, the ideal incidence factor is

$$
\mu=\sin\varphi\sin\delta+\cos\varphi\cos\delta\cos h. \tag{1}
$$

A small horizontal patch under a collimated beam receives irradiance proportional to $\max(0,\mu)$. Obliquity $\epsilon$ and solar longitude $\lambda$ determine declination through $\sin\delta=\sin\epsilon\sin\lambda$, when longitude is measured from the northern spring equinox. Consequently, zero and 180 degrees denote equinoxes under that convention. An orbital label without a defined origin does not identify a season.

Instantaneous incidence also differs from daily energy input. For a circular orbit and stellar irradiance $S$ normal to the rays, the daily mean is

$$
\bar Q=\frac{S}{\pi}\left[H_0\sin\varphi\sin\delta+
\cos\varphi\cos\delta\sin H_0\right], \tag{2}
$$

where $H_0$ is the sunrise hour angle, with appropriate polar-day and polar-night limits. Paillard distinguishes these instantaneous and integrated quantities and their conventions [1]. A stationary detector snapshot does not perform the rotation integral.

These relations supply useful symmetry tests. At zero obliquity, equal-distance configurations at the same latitude and rotation phase should show no seasonal difference. Opposite solstitial configurations should exchange the northern and southern illumination. At local noon with $\delta=\pm23.5^\circ$, the ideal response ratio at $+60^\circ$ and $-60^\circ$ is about 7.10 and reverses with declination. This numerical prediction presupposes the specified geometry. Synchronous planets with obliquity or eccentricity can have moving substellar points, as Dobrovolskis' insolation calculations illustrate [2]; synchronism alone does not prescribe an invariant illumination map.

## Optical response and thermal measurands

Figure 1 shows the controls needed for the two cases. In an orbital comparison, the rotation axes remain parallel in the room, the local detector normal follows the intended latitude, and rotation phase is documented. Keeping lamp distance constant controls only one variable. A nearby extended lamp, board shadow or changed source direction can still change the detector response.

Figure 1 (built locally at `output/pdf/tidal-locking.pdf`). Geometry and response are controlled separately. Upper: a fixed-distance orbital comparison with documented local orientation. Lower: fixed illumination of two model regions, observed with matched optical views and independent surface-temperature references.

The seasonal observations use the APDS-9960 clear channel. It reports spectrally weighted counts whose gain and integration affect the response [3]; conversion to irradiance depends on calibration of its angular response. Angular acceptance is itself a source of irradiance error [4]. Counts are therefore interpreted here as relative detector response, rather than converted to absorbed power.

The fixed-illumination example uses OPT3001 illuminance, TMP007 infrared object and die temperatures, and BMP280 die temperatures. The OPT3001 weights visible light approximately by the human photopic response and rejects much infrared radiation [5]. Lux describes the visible illumination pattern, not broadband absorbed flux. The TMP007 infers object temperature from its thermopile signal and die temperature; emissivity, reflected surroundings and target filling of its view enter that inference [6]. The BMP280 indication instead follows its die and board thermal environment [7]. These channels require separate interpretations even when placed in the same nominal region.

## The seasonal symmetry test

The twelve labelled observations span latitudes $-60^\circ$, $0^\circ$ and $+60^\circ$, tilt labels zero and $23.5^\circ$, and orbital labels 0 and 180 degrees. The latter are denoted A and B throughout the comparison. Every source distance is recorded as $100\,\mathrm{cm}$. Each snapshot is matched to the corresponding device-time sample in twelve consecutive five-second states, preserving the independent receive coordinate. The match is exact at the recorded precision.

For clear count $X$, dark count $X_d$ and reference count $X_r$, define

$$
R=\frac{X-X_d}{X_r-X_d}. \tag{3}
$$

Here $X_d=10$ and $X_r=1100$ counts, giving $(X-10)/1090$. Responses above unity are retained: an entered reference need not equal the largest observed signal. Table 1 contains all twelve conditions.

**Table 1.** Relative snapshot response $R=(X-10)/1090$ at a recorded source distance of $100\,\mathrm{cm}$. A/B denote orbital positions labelled 0/180 degrees.

| Latitude | $0^\circ$, A | $0^\circ$, B | $23.5^\circ$, A | $23.5^\circ$, B |
| --- | --- | --- | --- | --- |
| $-60^\circ$ | 0.522 | 0.188 | 0.450 | 0.105 |
| $0^\circ$ | 1.052 | 0.983 | 1.032 | 0.939 |
| $+60^\circ$ | 0.514 | 0.189 | 0.453 | 0.112 |

At zero tilt, A-to-B response falls by 0.334 at the southern location and 0.325 at the northern location; the equatorial fall is 0.0688. Such orbital dependence is absent from the ideal zero-obliquity, fixed-phase model. At $23.5^\circ$ tilt, the northern-minus-southern differences remain only 0.0037 at A and 0.0073 at B. Both hemispheres decrease together rather than exhibiting the predicted exchange. The shared positional response occurs at unchanged recorded distance. Attribution to seasonal declination depends on local normal, rotation phase, source direction and detector acceptance.

The continuous record quantifies the scale of that discrepancy. Select device-time windows $[5i+1,5i+4)\,\mathrm{s}$ for states $i=0,\ldots,11$, avoiding transitions. Their sample SDs range from 2.76 to 12.10 counts; the largest snapshot-minus-plateau-mean difference is 14.13 counts. These fluctuations are much smaller than the hundreds of counts separating high-latitude A/B states. They therefore do not account for the failed symmetry test. With one snapshot per geometry, these fluctuations describe within-state scatter; repeat-placement uncertainty is a separate quantity estimated from repeated complete configurations.

## Persistent forcing and the measured thermal contrast

The separate fixed-illumination example turns its lamp on at 30 s and off at 210 s. Baseline means use 0–30 s, late-heating means use 180–210 s, and all windows are half open. For each temperature channel, define

$$
D_T=(\bar T_{d,h}-\bar T_{d,0})
-(\bar T_{n,h}-\bar T_{n,0}), \tag{4}
$$

where $d,n$ denote illuminated and shaded regions and $h$ the late interval. Each channel retains its own grid: 1.0 s for BMP280, 0.3 s for TMP007 and 0.8 s for OPT3001 in the example. Transient interpretation also requires checking acquisition timestamps and relative alignment.

**Table 2.** Day/night rises above 0–30 s baselines during 180–210 s, and day-minus-night contrast $D_T$, by channel.

| Channel | Day (K) | Night (K) | $D_T$ (K) |
| --- | --- | --- | --- |
| TMP007 object | 20.24 | 0.83 | 19.41 |
| BMP280 die | 12.57 | 1.09 | 11.48 |
| TMP007 die | 2.00 | 1.19 | 0.81 |

The uncorrected late infrared-object contrast is 20.015 K; subtracting its initial 0.602-K contrast gives 19.413 K. The corresponding BMP280 values are 11.979 and 0.502 K, giving 11.477 K. Baseline correction removes a stable additive difference while retaining the distinct thermal interpretation of each channel.

Illuminance means over the entire illuminated interval, 30–210 s, are 12353.83 and 27.45 lx. Their ratio of means is 450.06. The shaded region has a small but nonzero visible signal. Conversion of this illuminance ratio to an absorbed-power contrast depends on source- and target-specific spectral and angular calibration. Figure 2 places the seasonal observations and persistent-forcing results in separate panels; each retains its own detector scale.

Figure 2 (built locally at `output/pdf/tidal-locking.pdf`). Seasonal clear counts and labelled snapshots (a); separate fixed-illumination day/night illuminance (b) and baseline-corrected temperature contrasts (c). Each channel retains its own time grid. Dashed lines mark lamp switching; panel (b) displays illuminances from 1 lx upward.

## From forcing to thermal redistribution

For effective regional temperatures near a common boundary temperature $T_a$, write

$$
C_i\dot\theta_i=Q_i-G_i\theta_i-K(\theta_i-\theta_j),
\quad\theta_i=T_i-T_a. \tag{5}
$$

$Q_i$ is absorbed power, $G_i$ local heat loss and $K$ exchange between the regions. For equal capacitances $C$ and loss coefficients $G$,

$$
C\dot{\Delta T}=\Delta Q-(G+2K)\Delta T. \tag{6}
$$

The equilibrium contrast is $\Delta Q/(G+2K)$ and its relaxation time is $C/(G+2K)$. Stronger coupling reduces the contrast under fixed forcing, but weaker absorption can produce the same effect. A temperature-difference curve cannot identify these explanations separately.

A characterized temperature channel must first represent the intended thermal node. The different object and die responses in Table 2 motivate channel-specific thermal nodes. Changes at nominal switch-off call for separate branch initial states or an explicit transition model when fitting heating and cooling.

The geometry and thermal tests therefore constrain different parts of the explanation. An upright, fixed-phase configuration should first reproduce the same response at opposite orbital positions; a known tilted configuration can then test hemispheric exchange or integrate a complete rotation. Under fixed illumination, exchanged sensor positions and reference surface temperatures test offsets, emissivity and mounting effects. Repeated complete configurations, rather than adjacent samples, establish reproducibility. During transients, calibration covariance and relative timing affect baseline-corrected contrasts.

Planetary heat redistribution additionally involves atmospheric pressure, optical thickness and circulation. Koll's scaling relates those properties to the balance between radiation and atmospheric motion [8]. The laboratory two-region model focuses on imposed forcing and thermal coupling. Its useful inference follows the same order as the physical problem: constrain the geometry, characterize absorbed forcing, then ask which thermal parameters the observed response can distinguish.

## References

[1] D. Paillard. [On the computation of several “insolation” quantities relevant to climatology or planetology](https://doi.org/10.5194/cp-22-647-2026). *Climate of the Past* **22**, 647–673 (2026).

[2] A. R. Dobrovolskis. [Insolation on exoplanets with eccentricity and obliquity](https://meetingorganizer.copernicus.org/EPSC-DPS2011/EPSC-DPS2011-136.pdf). *EPSC-DPS Joint Meeting 2011*, volume 6, EPSC-DPS2011-136 (2011).

[3] Avago Technologies. [*APDS-9960: Digital Proximity, Ambient Light, RGB and Gesture Sensor*](https://docs.broadcom.com/doc/AV02-4191EN). Datasheet AV02-4191EN.

[4] Vijeta, R. K. Kapri, S. Saha, V. K. Jaiswal and P. Sharma. [Theoretical simulation for evaluating error in irradiance measurement using optical detectors having different cosine responses](https://doi.org/10.1007/s12647-021-00486-6). *MAPAN* **36**(3), 473–480 (2021).

[5] Texas Instruments. [*OPT3001 Ambient Light Sensor*](https://www.ti.com/lit/ds/symlink/opt3001.pdf). SBOS681C, November 2017.

[6] Texas Instruments. [*TMP007 Infrared Thermopile Sensor with Integrated Math Engine*](https://www.ti.com/lit/ds/sbos685c/sbos685c.pdf). SBOS685C, July 2015.

[7] Bosch Sensortec. [*BMP280: Digital Pressure Sensor*, revision 1.26](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf). BST-BMP280-DS001-26, October 2021.

[8] D. D. B. Koll. [A scaling for atmospheric heat redistribution on tidally locked rocky planets](https://doi.org/10.3847/1538-4357/ac3b48). *The Astrophysical Journal* **924**(2), 134 (2022).
