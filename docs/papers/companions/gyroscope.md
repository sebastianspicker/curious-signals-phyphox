# Angular Rate, Reversal and Integrated Rotation

*June 2021*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

**Abstract.** Gyroscope calibration and angle integration depend on the sign of each rate component, information that a positive magnitude trace discards. We separate these issues using records for three instruments: the LSM9DS1 in the Arduino Nano 33 BLE Sense, the IMU-3000 in the CC2541 SensorTag and a PocketLab Voyager. In the Nano record, reversal evaluated against $\pm45\,\mathrm{degree\,s^{-1}}$ reference values gives sensitivity 0.87189, close to the ratio 0.87193 between the library conversion and the datasheet sensitivity. A settled CC2541 interval averages $-200.10\,\mathrm{degree\,s^{-1}}$ and integrates to approximately $-1961^\circ$ after a local residual-offset correction; the estimated uncertainty contribution from that correction is $1.3^\circ$. In the Voyager record, the corrected $x$ integral nearly cancels to $-0.10^\circ$, although the absolute-component integral exceeds $8100^\circ$. A common rate model explains why stationary offsets, independent reference rates and actual timestamps are needed for all three instruments. The reductions support signed fixed-axis angle and accumulated-motion comparisons; final three-dimensional attitude requires an additional orientation model.

**Keywords:** Gyroscope, rate reversal, bias, angular integration, orientation, uncertainty.

## The signed rate is the primary observable

A gyroscope responds to angular velocity about its sensing axes. For an aligned axis, write

$$
y=b+s\Omega+\epsilon,
\tag{1}
$$

where $y$ is the indicated rate, $b$ the zero-rate offset, $s$ the sensitivity, $\Omega$ the reference angular rate and $\epsilon$ the noise. Stationary observations constrain $b$ but contain no information about $s$. Opposed nonzero rates identify both when their magnitudes are independently known and the offset remains stable. The sign is essential: taking a norm before calibration replaces opposite rates with similar positive outputs.

A three-axis model extends Eq. 1 to

$$
\boldsymbol y=\boldsymbol b(T)+G\boldsymbol \omega_{\rm ref}+\boldsymbol \epsilon,
\tag{2}
$$

with a temperature-dependent offset $\boldsymbol b(T)$ and a sensitivity matrix $G$. Its off-diagonal elements combine cross-axis response with the mounting convention. Gravity-referenced static orientations and the motions between them can constrain such inertial calibration parameters, as demonstrated by Tedaldi *et al.* [1]. An explicit rate reversal makes visible which reference quantity determines each coefficient.

The three records apply that common model to different motion histories. The Nano record contains settled yaw reversals; the CC2541 record has rounded extrema followed by a sustained negative-axis interval; the Voyager record contains large reversals with simultaneous activity on other axes. The comparison concerns methods of inference, not the responses of three devices to one imposed motion.

## Reference motion and the numerical rate scale

Figure 1 defines the reference geometry for rate calibration. An encoder observed against an independent timebase supplies rate from unwrapped angle over a settled interval. A motor command alone is not that reference. A rigid mount, alternating rate signs and magnitudes, and interleaved zero-rate controls help separate alignment, sensitivity and thermal drift. Temperature must vary independently of rate sign if a temperature coefficient is to be estimated.

**Figure 1.** Reference arrangement for rate calibration. One sensor axis is aligned with the table. Encoder angle and reference time establish signed rate; repeated mountings test the separation of alignment from sensitivity. View figure in the article (built locally at `output/pdf/gyroscope.pdf`).

The output conversion precedes any physical comparison. Table 1 expresses the nominal increment per transmitted count in common units. In the Nano, the pinned Arduino_LSM9DS1 library configures the gyroscope for $\pm2000\,\mathrm{degree\,s^{-1}}$ at a 119-Hz output data rate and converts each count $q$ as $q(2000/32768)$ degrees per second [2]. The datasheet instead gives a typical sensitivity of $0.070\,\mathrm{degree\,s^{-1}/LSB}$ at that range [3]. The ratio is

$$
s_{\rm nom}=\frac{2000/32768}{0.070}=0.8719308.
\tag{3}
$$

For a device with the typical sensitivity, the library therefore indicates about 13% less than the applied rate, and a nominal correction multiplies the indication by 1.14688. Because the datasheet value is typical rather than guaranteed, only a reference-rate calibration establishes the sensitivity of an individual device.

**Table 1.** Count-to-rate conversion factors and delivered sampling cadence. Each factor specifies the numerical scaling of one transmitted count.

| Instrument | Step (deg/s) | Cadence (Hz) |
| --- | --- | --- |
| Nano LSM9DS1 | $2000/32768$ | $\simeq20$ |
| CC2541 IMU-3000 | $500/65536$ | $\simeq10$ |
| PocketLab Voyager | $2000/32768$ | $\simeq50$ |

The CC2541 SensorTag carries an InvenSense IMU-3000 [4]. Its legacy conversion uses a 500-degree-per-second total span [5]; that span must not be replaced by the range of another sensor merely because both transmit signed words. PocketLab specifies a $\pm2000\,\mathrm{degree\,s^{-1}}$ range and 50 samples per second for the Voyager gyroscope [6]. The phyphox definition decodes the Voyager words with that range and in $y,x,z$ packet order [7]; neither convention automatically applies to PocketLab One. The corresponding CC2541 and Voyager increments are $1.33158\times10^{-4}$ and $1.06526\times10^{-3}\,\mathrm{rad\,s^{-1}/count}$. Correct units, sign and body-axis convention are needed before integration; fine code spacing does not establish a small noise floor.

## Reversal identifies scale only with a reference

Figure 2 shows signed components alongside their positive norms. Every interval below is left-closed and right-open on that record's own clock, and observed timestamps are used throughout instead of a nominal fixed timestep.

**Figure 2.** Selected signed rate components and three-axis norms during the Nano, CC2541 and Voyager motion sequences. Component signs distinguish rotation direction; the norms combine motion across axes. The plots precede the additional local offset corrections used for the CC2541 and Voyager integrals. View figure in the article (built locally at `output/pdf/gyroscope.pdf`).

The Nano record contains positive and negative yaw plateaux, followed by roll and pitch intervals. The reduction uses an initial baseline $[0,7)$ s, positive yaw $[11,17)$ s and negative yaw $[21,27)$ s. The yaw means are $39.35998$ and $-39.11020\,\mathrm{degree\,s^{-1}}$. Using $\pm45\,\mathrm{degree\,s^{-1}}$ as the reference values, reversal gives

$$
\begin{aligned}
 \widehat b&=\frac{\bar y_++\bar y_-}{2}=0.12489\,\mathrm{degree\,s^{-1}},\\
 \widehat s&=\frac{\bar y_+-\bar y_-}{90}=0.87189.
 \end{aligned}
\tag{4}
$$

The sensitivity agrees with Equation 3 to within $5\times10^{-5}$. This numerical agreement relates the reversal result to the nominal conversion; a device calibration also includes the uncertainty of the independent reference rates. Initial and final $z$ means, the latter over $[52,59)$ s, are 0.1011 and $0.1502\,\mathrm{degree\,s^{-1}}$. Their difference shows why an initial offset need not describe the whole trajectory. Positive roll over $[31,37)$ s and negative pitch over $[41,47)$ s average $52.375$ and $-30.557\,\mathrm{degree\,s^{-1}}$ on their selected axes. Interpreting these additional amplitudes as sensitivity estimates likewise requires their own reference rates.

The other two records require a different interval interpretation. CC2541 $z$ means over $[9,11)$ and $[19,21)$ s are $123.20$ and $-123.46\,\mathrm{degree\,s^{-1}}$. Voyager $x$ means over $[19,21)$ and $[29,31)$ s are $492.16$ and $-493.40\,\mathrm{degree\,s^{-1}}$; its $y$ mean over $[49,51)$ s is $-242.03\,\mathrm{degree\,s^{-1}}$. These windows surround smooth extrema rather than constant-rate plateaux. Their means depend on the changing waveform and the window choice, so comparing them directly with peak reference values would confound temporal averaging with sensitivity.

By contrast, the CC2541 $[42,48)$ s interval is settled: its $y$ mean is $-200.10\,\mathrm{degree\,s^{-1}}$, and its sample SD is $0.01359\,\mathrm{rad\,s^{-1}}$, about $0.78\,\mathrm{degree\,s^{-1}}$. That SD describes variation within the interval. The settled mean and its scatter enter different parts of the analysis: the mean enters the rate comparison, while the scatter contributes to uncertainty after temporal correlation is considered.

## Fixed-axis angle and accumulated angular travel

For a fixed aligned axis, use the calibrated signed rate in a timestamp integral. A local residual offset $\widehat b$ gives the trapezoidal estimator

$$
\Delta\theta=\sum_i\frac{(y_i-\widehat b)+(y_{i+1}-\widehat b)}{2}
 (t_{i+1}-t_i).
\tag{5}
$$

The CC2541 correction uses the final $[56,60)$ s $y$ mean, $-0.0015193\,\mathrm{rad\,s^{-1}}$ or $-0.087\,\mathrm{degree\,s^{-1}}$. Those 40 stationary observations also have residual $x,z$ means $0.049$ and $0.327\,\mathrm{degree\,s^{-1}}$. With a sample SD of $0.86\,\mathrm{degree\,s^{-1}}$, the $y$ estimate has a standard error of $0.14\,\mathrm{degree\,s^{-1}}$ if successive observations are independent. Voyager instead uses its initial $[0,9)$ s $x$ mean, $-0.00978695\,\mathrm{rad\,s^{-1}}$ or $-0.561\,\mathrm{degree\,s^{-1}}$; its initial $y,z$ means are $1.139$ and $-0.903\,\mathrm{degree\,s^{-1}}$. These local stationary means estimate the residual offsets after the acquisition corrections.

**Table 2.** Signed-component, absolute-component and three-axis-norm integrals, in degrees. The first two use locally offset-corrected component rates; the norm integral uses the indicated three-axis magnitude. Each integral uses recorded timestamps.

| Instrument | Window (s) | Signed | Absolute | Norm |
| --- | --- | --- | --- | --- |
| CC2541, $y$ | 40–50 | $-1960.76$ | 1960.76 | 1961.65 |
| Voyager, $x$ | 10–40 | $-0.100$ | 8125.01 | 8882.49 |

The CC2541 integration uses only samples inside $[40,50)$ s, spanning approximately 40.098–49.902 s. The Voyager subset is $[10,40)$ s, spanning approximately 10.020–39.980 s. No boundary sample is invented at the requested endpoints. Converting angular units before integration yields Table 2.

For the nearly single-axis CC2541 interval, signed and absolute integrals differ only in sign. A constant rate of $-200\,\mathrm{degree\,s^{-1}}$ over the sampled span corresponds to $-1960.87^\circ$. The corrected integral differs from this value by $0.11^\circ$, less than the $1.3^\circ$ uncertainty contribution from the local offset estimate in Section V. Without that correction, the integral is $-1961.62^\circ$. For Voyager, opposite $x$ rotations nearly cancel in the signed integral, while the absolute-component integral counts motion in both directions. The larger norm integral also includes simultaneous transverse motion and the residual and noise contributions of those channels. The norm and component columns do not use identical offset corrections, so their difference is not an isolated transverse-angle estimate. A fully calibrated norm integral can describe accumulated angular travel, but it still cannot reveal turn direction or a net fixed-axis angle.

In general three-dimensional motion, the body axes themselves rotate. Successive rotations about different axes do not commute; integrating three components separately is therefore insufficient to reconstruct final attitude. A rotation-matrix or quaternion evolution with a stated body-frame convention is needed. The Voyager's nearly zero corrected $x$ integral does not demonstrate return to the original pose.

## Which errors survive integration?

A constant residual bias contributes linearly with duration. Its contribution to angle uncertainty is $T\,u(b)$; a residual $0.05\,\mathrm{degree\,s^{-1}}$ over 60 s contributes $3^\circ$. For the CC2541 correction, the $0.14\,\mathrm{degree\,s^{-1}}$ standard error contributes $1.3^\circ$ over the 9.8-s integration span. Finer sampling within the integration span does not reduce the effect of a common offset on the integral. Likewise, scale and reference-time errors affect the full integral coherently. Gain/offset covariance, reference-rate uncertainty and the uncertainty of correlated plateau means belong in the calibration budget [8].

El-Sheimy *et al.* describe Allan-variance analysis for separating stochastic inertial error contributions across averaging time [9]. Stationary runs, combinations of rate and temperature excluded from fitting, and repeated mountings provide complementary checks of long-term bias, thermal response and dynamic linearity.

Delivered sampling must also be distinguished from sensor bandwidth. Unresolved motion can alias into any of these records, while gaps change what can be integrated without interpolation assumptions. The useful hierarchy is consequently a signed component with an established rate scale, a finite-interval integral with an explicit bias and time model, and finally a three-dimensional orientation reconstruction. Taking a positive norm at the first stage cannot supply information needed at the later ones. The reported reversals and timestamp integrals show how sign, offset and timing determine the resulting rate and angle estimates.

## References

1. [D. Tedaldi, A. Pretto and E. Menegatti. “A Robust and Easy to Implement Method for IMU Calibration without External Equipments.” ICRA, 3042–3049 (2014).](https://doi.org/10.1109/ICRA.2014.6907297)

2. [Arduino. Arduino_LSM9DS1, version 1.1.1: acquisition configuration and numerical conversion.](https://raw.githubusercontent.com/arduino-libraries/Arduino_LSM9DS1/1.1.1/src/LSM9DS1.cpp)

3. [STMicroelectronics. LSM9DS1: iNEMO Inertial Module. Datasheet, revision 3 (2015).](https://www.st.com/resource/en/datasheet/lsm9ds1.pdf)

4. [Texas Instruments. CC2541 SensorTag Quick Start Guide, SWRU324B (2013).](https://www.ti.com/lit/ug/swru324b/swru324b.pdf)

5. [phyphox. Texas Instruments SensorTag CC2541: External Sensor Definitions.](https://phyphox.org/wiki/index.php/Texas_Instruments_SensorTag_CC2541)

6. [PocketLab. PocketLab Voyager Specifications.](https://support.thepocketlab.com/knowledge/pocketlab-voyager-manual)

7. [phyphox. PocketLab Voyager Accelerometer and Gyroscope Experiment Definition.](https://github.com/phyphox/phyphox-experiments/blob/master/bluetooth/PocketLab%20Voyager%20Acc%20Gyro%20Mag.phyphox)

8. [Joint Committee for Guides in Metrology. Evaluation of Measurement Data—Guide to the Expression of Uncertainty in Measurement. JCGM 100:2008.](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf)

9. [N. El-Sheimy, H. Hou and X. Niu. “Analysis and Modeling of Inertial Sensors Using Allan Variance.” IEEE Transactions on Instrumentation and Measurement 57(1), 140–149 (2008).](https://doi.org/10.1109/TIM.2007.908635)
