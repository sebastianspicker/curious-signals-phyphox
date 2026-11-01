# Specific Force, Inclination and the Limits of Resolution

*February 2021*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

**Abstract.** An accelerometer measures specific force. Its direction gives static inclination when translational acceleration is negligible, whereas its magnitude and dynamic content require a calibrated scale and a characterized frequency response. We examine these requirements using records for two instruments: the LSM9DS1 in the Arduino Nano 33 BLE Sense and the KXTJ9 in the CC2541 SensorTag, read as eight-bit values. In the Nano record, opposed tilts and a quarter-turn redistribute gravity between components at a nearly constant norm. For nominal $\pm20^\circ$ tilts, the KXTJ9 reductions give $19.97^\circ$ and $-20.48^\circ$; a nominal $60^\circ$ roll gives $60.20^\circ$. Its $0.15323\,\mathrm{m\,s^{-2}}$ code spacing corresponds to approximately $0.90^\circ$ near level. All 81 observations in its initial level interval share one raw triplet, yet the reduced pitch is $-0.27^\circ$: zero sample scatter does not imply zero angular uncertainty. A common vector calibration separates offset, sensitivity and alignment, and an independent angular reference supplies the alignment that norm constancy leaves undetermined.

**Keywords:** Specific force, inclination, quantization, accelerometer calibration, vector measurement.

## Gravity provides a direction and a magnitude

An accelerometer measures specific force, the non-gravitational force per unit mass acting on its proof mass; for a stationary sensor this is the support force that prevents free fall. With sensor-to-laboratory rotation $R$, laboratory acceleration $\boldsymbol a_\ell$ and gravitational acceleration $\boldsymbol g_\ell$, the ideal specific force in sensor axes is

$$
\boldsymbol f_s=R^\mathsf T(\boldsymbol a_\ell-\boldsymbol g_\ell).
\tag{1}
$$

Its magnitude equals $g$ at rest and vanishes in free fall. Reorientation redistributes the components while preserving the ideal norm. Component ratios therefore indicate inclination only when translational acceleration is negligible. The norm cannot separate the two contributions: subtracting $g$ from it leaves a scalar without direction.

Within a specified plane, calibrated components give

$$
\theta=\operatorname{atan2}(f_x,f_z).
\tag{2}
$$

The single-component projection $f_x=g\sin\theta$ becomes less sensitive to angle as $|\theta|$ approaches $90^\circ$. The two-component estimator has a component-error gradient of constant magnitude within the static measurement plane and is unaffected by a gain common to both axes. It requires known axis geometry and does not determine a complete three-dimensional attitude. The records below distinguish projected gravity, a sampled tap response and the angular information lost through coarse quantization.

Gravity-based calibration constrains bias, scale and cross-axis terms through the constant norm over many static poses [1]. It does not by itself establish laboratory alignment. The cross-sensitivity matrix of a three-axis accelerometer depends on how the package is mounted on the calibration fixture; Geist *et al.* therefore define intrinsic parameters that separate the device's own properties from that mounting [2]. Norm consistency and an angular reference answer different questions.

## Reference geometry and component scale

Figure 1 shows the reference geometry for the static comparison: a rigid tilt cradle and an independent angle reference. Rotation about an axis close to the package limits translational acceleration of the sensor; returns to earlier angles and remounting test stability. Temperature and local gravity belong to the reference conditions.

**Figure 1.** Reference arrangement for the static comparison. The cradle defines a reproducible sensor plane, and its angular reference is independent of the gravity projection being tested. View figure in the article (built locally at `output/pdf/accelerometer.pdf`).

In the original Nano 33 BLE Sense, the pinned Arduino_LSM9DS1 library configures the LSM9DS1 accelerometer for $\pm4g$ at a 119-Hz output data rate and converts each count as $4g/32768$ [3]. This agrees with the datasheet's typical sensitivity at that range, $0.122\,\mathrm{mg/LSB}$ or approximately $0.00120\,\mathrm{m\,s^{-2}}$ [4]. The CC2541 SensorTag instead carries a Kionix KXTJ9 [5], whose legacy interface delivers one signed byte per axis. The external phyphox definition for this device scales the bytes for a $\pm2g$ range, that is, 64 counts per $g$ [6]. With standard gravity, the code step is

$$
q_a=\frac{9.80665}{64}=0.15323\,\mathrm{m\,s^{-2}/count}.
\tag{3}
$$

This is about 128 times the nominal LSM9DS1 increment. The comparison concerns granularity only and does not rank accuracy or noise. Internal output rate, transmitted word width and delivered cadence are likewise separate properties.

The CC2541 export applies per-channel bias corrections of $0.20$, $-0.25$ and $0.35\,\mathrm{m\,s^{-2}}$ for $x,y,z$, entered in the acquisition definition and subtracted after scaling; the exported packet counts and corrected components reproduce this transformation exactly. The Nano export converts $g$ to $\mathrm{m\,s^{-2}}$ with a factor of 9.81. Its record covers nominal $\pm30^\circ$ pitch and a $90^\circ$ roll; the CC2541 record covers nominal $\pm20^\circ$ pitch and a $60^\circ$ roll. Delivered at approximately 20 and 10 Hz, the two records retain separate clocks and pose histories; their observations are not paired.

## What the static and moving intervals resolve

Figure 2 compares the two component records, and Table 1 lists the static window means. Means use left-closed, right-open intervals excluding transitions: baseline $[0,8)$ s, opposed tilts $[16,19)$ and $[26,29)$ s, and, in the Nano record, quarter-turn $[46,49)$ s.

**Figure 2.** Specific-force components and magnitude during reorientation and transient motion. (a) Nano: opposed tilts, taps and a quarter-turn. (b) CC2541: smaller opposed tilts, a short shake and a roll. Each panel uses its own record time. View figure in the article (built locally at `output/pdf/accelerometer.pdf`).

**Table 1.** Mean specific-force components and mean vector magnitude for the static poses, in $\mathrm{m\,s^{-2}}$. Time windows $[t_1,t_2)$ are in seconds and exclude transitions.

| Device | Interval | $\bar f_x$ | $\bar f_z$ | $\overline{\Vert\boldsymbol f\Vert}$ |
| --- | --- | --- | --- | --- |
| Nano | 0–8 | 0.017 | 9.833 | 9.834 |
| Nano | 16–19 | 4.927 | 8.521 | 9.843 |
| Nano | 26–29 | $-4.883$ | 8.526 | 9.826 |
| Nano | 46–49 | 0.028 | 0.040 | 9.824 |
| CC2541 | 0–8 | $-0.047$ | 9.763 | 9.763 |
| CC2541 | 16–19 | 3.324 | 9.150 | 9.736 |
| CC2541 | 26–29 | $-3.418$ | 9.150 | 9.768 |

For the Nano tilts, Equation 2 gives $30.04^\circ$ and $-29.80^\circ$. Their horizontal midpoint, $0.0222\,\mathrm{m\,s^{-2}}$, is an offset diagnostic when an independent angular reference establishes equal and opposite tilts. During the quarter-turn, $\bar f_y=-9.824\,\mathrm{m\,s^{-2}}$ and $\bar f_z=0.040\,\mathrm{m\,s^{-2}}$. The mean norm varies by less than $0.02\,\mathrm{m\,s^{-2}}$ across the four poses, consistent with gravity being redistributed between axes rather than changed.

In the CC2541 record, the $[16,19)$ and $[26,29)$ s windows cover the nominal $\pm20^\circ$ tilts. Equation 2 applied to their means gives $19.97^\circ$ and $-20.48^\circ$. Each window contains a single code triplet. The roughly half-degree asymmetry is smaller than one local angular code step and does not by itself identify hysteresis. The $[46,49)$ s roll, reduced with $\operatorname{atan2}(-\bar f_y,\bar f_z)$, gives $60.20^\circ$ for a nominal $60^\circ$. All of these are planar gravity projections.

All 81 observations in the initial $[0,8)$ s window share one raw triplet, $(1,-2,66)$. Their component sample standard deviations are zero, yet the reduced pitch is $-0.27^\circ$, and the norm, $9.7634\,\mathrm{m\,s^{-2}}$, lies $0.043\,\mathrm{m\,s^{-2}}$ below standard gravity. Sub-code variation can leave every recorded code unchanged, so zero sample scatter does not establish an exact angle or magnitude. For one projection $f_x=g\sin\theta$, the local angular code spacing is

$$
\delta\theta\simeq\frac{q_a}{g|\cos\theta|},
\tag{4}
$$

with $\delta\theta$ in radians. Near level this is $0.895^\circ$. A uniform within-code model gives a component standard uncertainty $q_a/\sqrt{12}$, equivalent to $0.26^\circ$ near level. Reducing that contribution by averaging additionally requires independently varying quantization errors; the locked observations provide no evidence for such variation. Without noise or dither spanning code boundaries, averaging does not reduce the quantization error, and retaining more decimal places does not improve angular resolution.

The Nano tap sequence addresses another regime. Its largest sampled magnitude is $1.3467g$ at 36.382 s. This is the largest sample, not necessarily the peak of the underlying specific-force waveform. The delivered cadence of about 20 Hz has a 10-Hz Nyquist frequency. Relating the sampled peak to the waveform requires the sensor's internal filtering and frequency response, as well as the sampling phase; content above 10 Hz can alias into the delivered record.

## Calibration and the uncertainty of inclination

For static pose $j$, a common calibration model is

$$
\begin{aligned}
 \boldsymbol y_j&=\boldsymbol b+S R_j^\mathsf T(-\boldsymbol g_\ell)+\boldsymbol \epsilon_j,\\
 \widehat{\boldsymbol f}&=\widehat S^{-1}(\boldsymbol y-\widehat{\boldsymbol b}),
 \end{aligned}
\tag{5}
$$

where $\boldsymbol y_j$ is the indicated output, $\boldsymbol b$ the offset, $S$ a sensitivity matrix whose off-diagonal elements describe cross-axis response, and $\boldsymbol\epsilon_j$ the noise. Opposed axis orientations constrain offset and sensitivity; oblique poses constrain cross-axis terms. A fit based only on the norm maps the indicated ellipsoid onto a sphere and therefore determines $S$ only up to a rotation; surveyed orientations supply the missing alignment. Withheld poses and remounting test whether the calibration transfers beyond the fitted sequence.

For the planar estimator, the sensitivity of $\theta$ to the components is

$$
\boldsymbol J_\theta=
 \left(\frac{f_z}{f_x^2+f_z^2},
       \frac{-f_x}{f_x^2+f_z^2}\right),
\tag{6}
$$

whose magnitude, $(f_x^2+f_z^2)^{-1/2}$, equals $1/g$ at every angle for a static pose in the measurement plane. The corrected-component covariance propagates as $u^2(\theta)=\boldsymbol J_\theta\Sigma_{xz}\boldsymbol J_\theta^\mathsf T$, with calibration uncertainty included in $\Sigma_{xz}$. A comparison with the cradle additionally involves reference-angle and mounting uncertainty. Offset and gain errors are common to every sample, and a joint calibration correlates them between components; treating them as independent sample-to-sample noise would overstate the benefit of averaging. A gain common to both axes cancels in Equation 2, whereas differential gains and offsets do not. In the reverse direction, a reference-angle uncertainty $u(\theta)$ contributes $g|\cos\theta|\,u(\theta)$ to the projected component $f_x$, with $u(\theta)$ in radians.

Known angle increments, reordered poses, thermal changes and remounting expose errors that a quiet trace or a constant norm can hide. These checks test the direction estimate used for inclination. Quantitative dynamic acceleration additionally requires a calibrated magnitude scale and a characterized frequency response. The reported component means, angular estimates and sampled peaks illustrate these distinct uses of the same specific-force record.

## References

1. [I. Frosio, F. Pedersini and N. A. Borghese. “Autocalibration of MEMS Accelerometers.” IEEE Transactions on Instrumentation and Measurement 58(6), 2034–2041 (2009).](https://doi.org/10.1109/TIM.2008.2006137)

2. [J. Geist, M. Y. Afridi, C. D. McGray and M. Gaitan. “Gravity-Based Characterization of Three-Axis Accelerometers in Terms of Intrinsic Accelerometer Parameters.” Journal of Research of NIST 122 (2017).](https://doi.org/10.6028/jres.122.032)

3. [Arduino. Arduino_LSM9DS1, version 1.1.1: acquisition configuration and numerical conversion.](https://raw.githubusercontent.com/arduino-libraries/Arduino_LSM9DS1/1.1.1/src/LSM9DS1.cpp)

4. [STMicroelectronics. LSM9DS1: iNEMO Inertial Module. Datasheet, revision 3 (2015).](https://www.st.com/resource/en/datasheet/lsm9ds1.pdf)

5. [Texas Instruments. CC2541 SensorTag Quick Start Guide, SWRU324B (2013).](https://www.ti.com/lit/ug/swru324b/swru324b.pdf)

6. [phyphox. Texas Instruments SensorTag CC2541: External Sensor Definitions.](https://phyphox.org/wiki/index.php/Texas_Instruments_SensorTag_CC2541)

