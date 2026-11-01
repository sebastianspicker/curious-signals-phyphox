# Voltage Measurement and Circuit Inference: ADC Codes and Multimeter Readings

*July 2022*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

**Abstract.** Voltage acquisition requires a numerical conversion, an electrical calibration and a defined circuit load. Microcontroller inputs and an external multimeter expose these requirements in different forms. A six-level multimeter staircase gives a gain of 1.001995 and an offset of $0.504\,\mathrm{mV}$ relative to nominal example settings; raw and displayed values agree under the defined numerical conversion. In the independent microcontroller example, capacitor charging and discharging give time constants of 0.9997 and $0.9995\,\mathrm{s}$. A common affine voltage error changes fitted amplitudes and asymptotes while preserving this timescale, whereas timebase error or loading can alter its physical interpretation. Granularity, calibration covariance and circuit dynamics must therefore be assessed at the stage where each affects the inferred quantity.

**Keywords:** Voltage measurement, ADC, digital multimeter, calibration, loading, RC circuits.

## A shared measurement chain
A converter code or a Bluetooth notification becomes a voltage indication only after scale, sign and units have been assigned. Physical voltage measurement then requires an independently checked transfer relation and a circuit whose operating point is not changed unknowingly by the readout. The same distinction applies to a microcontroller input and a digital multimeter, even though their resolutions, input circuits and conversion timing differ.

For an ADC code $q$, write an affine indication
$$
U_d=a+bq.
\tag{1}
$$
A multimeter notification instead represents a signed displayed number together with function, decimal scaling and a unit prefix. Recovering that number correctly verifies the representation. It does not determine the electrical gain or offset at the terminals. Conversely, a calibrated meter does not guarantee that an unrecognised range or packet format will be interpreted correctly.

The examples are used for different tests. The Nano's A0 potentiometer sweep checks a broad code interval, A1 follows a light-dependent circuit, and A2 provides charging and discharging branches. The Owon staircase supplies repeated positive, zero and negative plateaux for a signed affine reduction. The Nano record uses device timestamps and the multimeter uses Bluetooth receive times. The runs compare numerical granularity across the two acquisition paths.

## Calibration at the terminals and loading in the circuit

**Figure 1.** Calibration and RC apparatus. A reference DVM observes the same terminals as the test readout. For a capacitor transient, all input paths load the capacitor node; their parallel resistance enters the dynamic model. See the article figure (built locally at `output/pdf/analog-inputs.pdf`).

Apply several independently known voltages to each channel, including interior levels and both polarities where the input permits them. Interleave a repeated level and reverse the sweep to distinguish drift from nonlinearity. Keep source resistance, input impedance, range and settling conditions in the calibration record. The reference must observe the same terminals as the instrument under test, not merely another nominally equal source setting.

The Nano's nRF52840 has a successive-approximation ADC with configurable reference, gain and acquisition time [1]. The board-core acquisition requests ten-bit results [2]; requested output width and physical converter capability are distinct [3]. The example uses $3.226\,\mathrm{mV/count}$, close to the endpoint convention $3300/1023$, whereas a 3.3-V, ten-bit bin width is $3300/1024=3.2227\,\mathrm{mV}$. Neither convention establishes the actual reference voltage or terminal scale.

An ADC acquires charge on an internal sampling capacitor. Source resistance and acquisition time determine settling, particularly after switching from another channel at a different potential [1]. The three channels are sequentially acquired at approximately 20 Hz; a common frame time does not establish simultaneous conversion for phase measurements. The supply rails constrain allowable pin voltage independently of the numerical conversion scale.

For the Owon B35T's 6.000-V DC range, one display digit is $1\,\mathrm{mV}$. The specified limit $\pm(0.5\%\text{ of reading}+2\text{ digits})$ corresponds to $\pm7\,\mathrm{mV}$ at 1.000 V [4]. This manufacturer limit is much larger than the scatter of the example plateau means. It applies under the manual's conditions and is not an uncertainty assigned solely from a stable sequence of repeated digits.

Loading has to be included in the physical model. A photocell observed across a shunt $R_s$ and meter input $R_m$ supplies
$$
I=U(R_s^{-1}+R_m^{-1}).
\tag{2}
$$
The burden voltage must remain within the intended current-source operating region. Open-circuit cell voltage and loaded photocurrent do not have the same relation to illumination. Correct decoding cannot remove this electrical change in operating point.

## The signed reference staircase
Figure 2 contrasts the circuit transient and the independent multimeter staircase. The meter sequence has nominal levels 0, 1.0, 1.5, 2.0, $-1.0$ and 0.5 V. Exclude the first and last second of each ten-second level, leaving 16 readings per plateau. Every interval below includes its lower endpoint and excludes its upper endpoint.

**Figure 2.** Indicated voltages on each record's own clock: (a) ADC channels A0 (potentiometer), A1 (light-dependent circuit) and A2 (capacitor); (b) the independent multimeter's signed DC-voltage staircase. See the article figure (built locally at `output/pdf/analog-inputs.pdf`).

**Table 1.** Interior multimeter plateau means and deviations from nominal voltage levels.

| Window (s) | Nominal (V) | Mean (V) | Deviation (mV) |
| --- | --- | --- | --- |
| 1--9 | 0.0 | 0.00050 | 0.500 |
| 11--19 | 1.0 | 1.00250 | 2.500 |
| 21--29 | 1.5 | 1.50338 | 3.375 |
| 31--39 | 2.0 | 2.00450 | 4.500 |
| 41--49 | $-1.0$ | $-1.00156$ | $-1.562$ |
| 51--59 | 0.5 | 0.50169 | 1.687 |

The raw numeric field on the selected range has a millivolt scale. Recalculation reproduces the indicated voltages, including the negative step, to floating-point rounding precision. This checks sign and numerical scaling independently of the nominal settings. Overload, an unknown prefix and the wrong meter interpretation are invalid states to reject, rather than small numerical errors to include in a calibration fit.

Fit the plateau means to $U_d=a+gU_{\rm nominal}$ by ordinary least squares. The result is $g=1.0019946$ and $a=0.5036\,\mathrm{mV}$, with maximum absolute plateau residual $0.1866\,\mathrm{mV}$. Within-plateau sample SDs range from 0.479 to $0.516\,\mathrm{mV}$. These quantities quantify the scale and offset relative to the stated levels. Repeated codes also do not independently sample every quantisation phase.

The Nano record illustrates the same distinction in a different form. All displayed voltages reproduce the stated count multiplication to numerical rounding precision. A0 spans codes 187--870, displayed as approximately 603--2807 mV, while A1 follows a slower light-dependent response. That response includes the external sensor circuit; conversion to an illumination scale depends on the circuit's calibration. The ADC display increment is 3.226 times the multimeter's 1-mV digit on the chosen range. This is a comparison of numerical granularity, not a measurement of either instrument's absolute accuracy.

## Circuit parameters that survive an affine scale
The capacitor channel permits a shape-based inference despite an uncertain common voltage gain. Smartphone RC experiments use the same distinction between amplitude calibration and a physical timescale [5]. Fit each branch using actual recorded times and
$$
U(t)=U_\infty+A\exp[-(t-t_0)/\tau].
\tag{3}
$$
The time origins are 5 s for charging and 35 s for discharge. For each trial positive $\tau$, estimate $A$ and $U_\infty$ by linear least squares, then minimise the residual sum of squares over $\tau$. With free amplitude, $t_0$ fixes the amplitude convention rather than introducing another independent shape parameter.

**Table 2.** Exponential fits to capacitor charging and discharging. Residual RMS is $\sqrt{\mathrm{SSE}/N}$; $\tau$ is the fitted time constant.

| Quantity | Charging | Discharging |
| --- | --- | --- |
| Fit window (s) | 5--12 | 35--42 |
| Observations | 139 | 139 |
| $\tau$ (s) | 0.9997 | 0.9995 |
| $U_\infty$ (mV) | 2995.4 | 1.7 |
| Residual RMS (mV) | 1.76 | 1.91 |

Shortening the windows to 5--10 and 35--40 s changes the two time constants by less than $0.2\,\mathrm{ms}$. This is an interval-sensitivity check, not a reference-clock or circuit-model uncertainty. A constant voltage offset and gain are absorbed into $U_\infty$ and $A$, leaving $\tau$ unchanged. Timebase scale error transfers directly into $\tau$, and input-dependent gain or additional relaxation processes can change its fitted value.

For the illustrated topology, the source remains connected through $R$ during both high and low states. With total parallel readout resistance $R_L$, the time constant is
$$
\tau=(R\parallel R_L)C,
 \qquad U_{\infty,\rm high}=U_s\frac{R_L}{R+R_L}.
\tag{4}
$$
Disconnecting the source instead of switching it low creates a different discharge circuit. An inferred capacitance therefore requires the actual switching topology, resistances and reference timing. Agreement of the example charging and discharging fits tests consistency within the exponential model, without identifying $R$, $C$ and loading separately.

## Uncertainty attached to the inferred quantity
For a voltage correction, propagate reference uncertainty and the joint covariance of fitted offset and gain, together with drift, resolution and loading [6]. A display step is a resolution statement. Under a uniform within-code model, the ADC's $3.226/\sqrt{12}=0.931\,\mathrm{mV}$ single-reading contribution does not decrease merely because identical codes are repeated. Avoid counting quantisation twice when repeatability already includes code fluctuations.

For a time constant, voltage-scale covariance is largely absorbed by the free amplitude and asymptote, but timebase uncertainty and circuit-model error remain. Residual structure near the step can indicate incomplete settling, leakage or an additional time constant. Repeat with another known resistance and check the predicted loaded scaling, rather than interpreting small residuals alone as validation.

Dynamic multimeter work additionally needs independently timed source transitions to establish conversion and delivery behaviour. Receive timestamps do not reveal the instrument's integration aperture. Thus the staircase establishes signed numerical consistency and an affine example reduction, while the RC trace identifies an approximately one-second relaxation under a stated model. The electrical reference, load and timing determine which further voltage or component claims those numbers can support.

## References

1. Nordic Semiconductor (accessed October 2026). [nRF52840 Product Specification](https://docs-be.nordicsemi.com/bundle/nRF52-Series-PS/raw/resource/enus/nRF52840_PS_v1.0.pdf).
2. Arduino (accessed October 2026). [ArduinoCore-mbed, Version 4.5.0, Analog Input Implementation](https://github.com/arduino/ArduinoCore-mbed/blob/4.5.0/cores/arduino/wiring_analog.cpp).
3. Arduino (accessed October 2026). [analogReadResolution() Language Reference](https://docs.arduino.cc/language-reference/en/functions/analog-io/analogReadResolution/).
4. OWON (accessed October 2026). [Digital Multimeter User Manual: B35(T)(+), D35(T), B41T(+)](https://files.owon.com.cn/probook/OWON_35_Series%26B41T_USER_MANUAL.pdf).
5. Torriente-García, Ives; Muñoz-Pérez, Francisco M.; Martí, Arturo C.; Monteiro, Martín; Castro-Palacio, Juan C.; Monsoriu, Juan A. (2023). [Experimenting with RC and RL Series Circuits Using Smartphones as Signal Generators and Oscilloscopes](https://doi.org/10.1590/1806-9126-RBEF-2023-0143). DOI: 10.1590/1806-9126-RBEF-2023-0143.
6. Joint Committee for Guides in Metrology (2008). [Evaluation of Measurement Data---Guide to the Expression of Uncertainty in Measurement](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf).
