# Indicative Colour Temperature and the Limits of a Transferred Sensor Matrix

*October 2019*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

A broad-band colour sensor can order source colours consistently, with its temperature scale set by the colour calibration. Example APDS-9960 counts are corrected for dark offsets, normalized by the clear response and transformed using a provisional RGB-to-XYZ matrix before applying McCamy's cubic approximation. Interior-window means are 2548, 3935 and 6114 K for warm, intermediate and cool states, with within-window standard deviations of 25, 18 and 91 K. The matrix is traced to a TCS3414CS application note, linking the temperature conversion to the transfer of a sensor-specific spectral calibration. The analysis distinguishes repeatable numerical conversion from colorimetric accuracy and from the physical temperature of an emitting body.

**Keywords:** Correlated colour temperature, spectral mismatch, RGB calibration, chromaticity, Planckian radiation.

## Colour temperature requires a colour measurement

Correlated colour temperature (CCT) relates a source's chromaticity to that of a Planckian radiator. It does not imply that the source itself is a blackbody. The CIE's terminology guidance emphasizes the restrictions that arise when a spectrum departs from Planckian radiation [1](https://doi.org/10.25039/TN.013.2022). A narrow-band source and a thermal source can therefore require different descriptions even if a numerical conversion returns a plausible value in kelvin.

McCamy's explicit cubic provides an efficient approximation to the chromaticity–CCT relation [2](https://doi.org/10.1002/col.5080170211). Its input must first be a meaningful colorimetric coordinate. An RGB sensor supplies device-specific spectral integrals, whereas CIE XYZ coordinates are defined through standard colour-matching functions. Treating the two triples as interchangeable omits the most consequential calibration step.

This issue is concrete for the conversion considered here. Its matrix coefficients are identical to those in Smith's application note for the TAOS TCS3414CS [3](https://look.ams-osram.com/m/57eb503c1d12d800/original/TCS34xx-AN000517.pdf). That note derives a transform for that sensor using reference sources and describes obtaining a new matrix for another calibration family. The APDS-9960 has its own filtered photodiodes and spectral response [4](https://docs.broadcom.com/doc/AV02-4191EN). Transferring the numerical matrix to another sensor makes its spectral response part of the calibration.

## From counts to provisional chromaticity

Figure 1 separates the relative-light acquisition from the independent reference needed to calibrate a colour transform. A fixed aperture and source geometry help maintain a reproducible incident spectrum. Covered readings determine electronic offsets; a change in ambient illumination is a separate contribution because it also has a spectrum.

*A relative sensor and independent colour reference view a reproducible source condition. A matrix fit requires several reference colours spanning the intended source family.* View apparatus schematic (built locally at `output/pdf/colour-temperature.pdf`)

For the example, the dark values are $D_C=3$, $D_R=D_G=2$ and $D_B=1$ counts. The normalized colour responses are $q_k=(C_k-D_k)/(C-D_C)$. They are transformed according to
$$
\begin{bmatrix}X\\Y\\Z\end{bmatrix}
 =\begin{bmatrix}
 -.14282&1.54924&-.95641\\
 -.32466&1.57837&-.73191\\
 -.68202&.77073&.56332
 \end{bmatrix}
 \begin{bmatrix}q_R\\q_G\\q_B\end{bmatrix}.
\tag{1}
$$
Here XYZ are provisional relative coordinates. Chromaticities are then $x=X/(X+Y+Z)$ and $y=Y/(X+Y+Z)$, subject to positive-domain checks. Because this matrix transformation is homogeneous, the common corrected-clear denominator cancels exactly in $x$ and $y$. The clear reading therefore contributes a working-range and validity check, rather than an independent chromaticity coordinate. This cancellation cannot correct an error in the spectral shape of the colour-channel response.

The adopted McCamy convention is
$$
n=\frac{x-.3320}{.1858-y},
\tag{2}
$$

$$
T_{\rm cp}/\mathrm{K}=449n^3+3525n^2+6823.3n+5520.33.
\tag{3}
$$
The positive cubic and linear coefficients are consistent with this denominator sign. Reversing the sign of the denominator requires reversing the odd-power terms. Values close to $y=.1858$, nonphysical coordinates and outputs outside the chosen 2000–10000 K screening interval are excluded. That numerical interval is a screen; it is not a calibrated accuracy specification or a test of distance from the Planckian locus.

## The example colour sequence

The data pass from a warm state through an intermediate state to a cool state and return to warm. Four interior windows exclude transitions. Their chromaticity means move systematically from larger to smaller $x$ and $y$ across the three states. Returning to the initial colour brings both coordinates close to their earlier values.

*CCT estimates and chromaticity coordinates calculated with the transferred RGB-to-XYZ matrix through a warm–intermediate–cool–warm sequence. Both track the source-colour ordering.* View data figure (built locally at `output/pdf/colour-temperature.pdf`)

*Interior-window mean chromaticities and CCT estimates computed with the transferred matrix. SD is the within-window sample standard deviation of CCT.*

| Window (s) | $x$ | $y$ | Mean (K) | SD (K) |
|---|---|---|---|---|
| 2–13 | .48965 | .44141 | 2548 | 25 |
| 21–29 | .38907 | .39847 | 3935 | 18 |
| 36–44 | .31759 | .35895 | 6114 | 91 |
| 52–59 | .48945 | .44133 | 2550 | 26 |

The final warm-state mean differs from the first by approximately $1.7\,\mathrm{K}$, much less than the approximately $25\,\mathrm{K}$ scatter of individual warm-state values. This demonstrates close return in the converted coordinates of the example. It does not bound an absolute systematic error: a fixed matrix bias would be shared by both warm intervals.

The cool state's scatter is approximately $91\,\mathrm{K}$, five times that of the intermediate state. The conversion is nonlinear and has different local sensitivity at different chromaticities. For the cool window, applying the conversion to the mean raw counts gives $6111.6\,\mathrm{K}$, whereas averaging the individual converted values gives $6113.8\,\mathrm{K}$. The $2.2\,\mathrm{K}$ difference is small relative to individual scatter but illustrates that averaging and nonlinear conversion are different estimators.

## Calibration, uncertainty and physical temperature

The RGB dark corrections and matrix coefficients are shared inputs to both chromaticities, so their errors are correlated. The common clear-channel scale cancels in chromaticity, as noted above; counting it as an independent CCT noise contribution would be incorrect for this homogeneous transform. A covariance propagation through Eqs. (1)–(3) would describe local random sensitivity. Sensor-specific spectral calibration also enters the uncertainty budget. Additional readings reduce neither that transform error nor the ambiguity between distinct spectra with the same few channel integrals.

An appropriate calibration would use independent XYZ references for several sources spanning the intended family, estimate a matrix, and test sources excluded from the fit. It would also assess linearity, aperture effects and repeatability after remounting. A three-source fit that reproduces its own calibration points is not an independent assessment of transfer to fluorescent, LED and thermal spectra.

CCT further requires proximity to the Planckian locus in an appropriate uniform-colour space. Positive XYZ and a plausible temperature do not establish that proximity. A source with substantial line emission may have a colour description without admitting the same thermodynamic interpretation as a heated filament. Likewise, a star's surface temperature is inferred through atmospheric and spectral modelling that relates observed colours to the emitting atmosphere.

The example therefore supports a clear ordering and repeatable numerical separation of source colours. Its values in kelvin are useful for examining the reduction and its sensitivity, with the transferred matrix making the role of sensor-specific spectral calibration explicit. Keeping those two conclusions distinct allows the experiment to teach colour measurement without overstating temperature inference.

## References

1. R. Young, T. Goodman, Y. Ohno and J. Ledig (2022). [Terms Related to Planckian Radiation Temperature for Light Sources, CIE TN013:2022](https://doi.org/10.25039/TN.013.2022).
2. C. S. McCamy (1992). [Correlated Color Temperature as an Explicit Function of Chromaticity Coordinates](https://doi.org/10.1002/col.5080170211).
3. J. Smith (2009). [Calculating Color Temperature and Illuminance Using the TAOS TCS3414CS Digital Color Sensor](https://look.ams-osram.com/m/57eb503c1d12d800/original/TCS34xx-AN000517.pdf).
4. Avago Technologies. [APDS-9960 data sheet, AV02-4191EN](https://docs.broadcom.com/doc/AV02-4191EN).
