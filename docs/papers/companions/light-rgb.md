# Optical Response, Reference Substitution and Detector-Weighted Transmission

*July 2023*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

Relative optical measurements depend on a reference, a collection geometry and the spectral response of the detector. We develop one reduction framework for RGBC counts, an LED-based relative sensor and an external analog UV detector. Example colour records distinguish selective response from saturation: all four RGBC channels clip at 4100 counts, while unsaturated filter extrema retain 0.872, 0.781 and 0.847 in their favoured channels after local referencing. A bracketed LED measurement gives a relative sample response of 0.553. The UV observations distinguish transmissions of 0.500, 0.400 and 0.283, with single-reading precision near 0.003 estimated from plateau scatter; their absolute irradiances use separate electrical and radiometric calibration factors. These comparisons identify what reference substitution cancels, which spectral and geometrical dependencies remain, and why small numerical scatter alone cannot establish an optical scale.

**Keywords:** Relative photometry, spectral responsivity, transmission, reference substitution, UV radiometry, calibration.

## One response model, different optical quantities

A light sensor observes the radiation admitted by its aperture through a spectral response that is generally unequal to that of another detector. For a linearized indication $Y_k$, a useful model is
$$
Y_k=D_k+K_k\int s_k(\lambda)E_\lambda\,d\lambda+\epsilon_k,
\tag{1}
$$
where $D_k$ is the offset, $K_k$ combines fixed gain and integration factors, $s_k$ is effective spectral responsivity and $E_\lambda$ is incident spectral irradiance. Changing a coloured scene changes $E_\lambda$. Inserting a filter replaces it by $E_\lambda\tau(\lambda)$, where $\tau$ is spectral transmission. Neither operation implies that the detector indication is illuminance or total radiant power.

Three acquisition paths make these distinctions concrete. The APDS-9960 on the original Nano 33 BLE Sense supplies clear, red, green and blue counts with overlapping spectral bands [1](https://docs.broadcom.com/doc/AV02-4191EN). Puck.js uses an LED as a relative detector; LED photodetection is well established [2](https://doi.org/10.1364/AO.31.006965), but its light function's 0–1 output has no absolute optical unit [3](https://www.espruino.com/Reference#l_Puck_light). The UV path instead uses an external detector and signal conditioner feeding an analog input. Its optical band is determined by that detector, not by the board's RGB sensor.

Equation (1) relates the measured indication to incident irradiance. The Puck ratios compare relative response across the bracketed optical states; their interpretation as power ratios depends on response linearity. Multichannel-sensor calibration also requires separate treatment of spectral responsivity and absolute scale, as illustrated by Besozzi and colleagues for other compact detectors [4](https://doi.org/10.21014/actaimeko.v15i2.2267). The examples considered here are separate optical comparisons; their response ratios cannot rank instrument accuracy or be treated as observations of one shared sample and spectrum.

## What reference substitution cancels

Figure 1 fixes the source, aperture and detector while the sample or opaque stop is exchanged. Direct stray light that bypasses a sample does not follow its transmission, so baffling is part of the definition of the measurement. Reflection, scattering and fluorescence can also change which radiation reaches the detector. Reference spectrophotometry consequently specifies the collection geometry as well as the sample and reference [5](https://doi.org/10.6028/NBS.SP.260-81).

*Reference-substitution arrangement for each detector. A covered detector supplies the offset; the open path defines the reference. Source and detector geometry are held fixed as the sample or opaque stop is exchanged.* View apparatus schematic (built locally at `output/pdf/light-rgb.pdf`)

For sample, open-reference and dark indications $S$, $R$ and $D$, respectively, define
$$
T_w=\frac{S-D}{R-D},\qquad R>D.
\tag{2}
$$
When the indication is proportional to incident power and the gain is unchanged, this becomes
$$
T_w=\frac{\int s(\lambda)E_\lambda\tau(\lambda)\,d\lambda}
 {\int s(\lambda)E_\lambda\,d\lambda}.
\tag{3}
$$
Stable multiplicative gain cancels. The source spectrum and detector weighting remain. A spectrally neutral attenuator yields the same ideal ratio across detectors, whereas a coloured filter generally does not. Nor can three broad ratios uniquely recover an arbitrary transmission spectrum.

The reference must represent the same physical state apart from the sample. A dim-room baseline describes one illuminated scene; it is not automatically a covered-detector electronic dark. Interleaving open references and dark observations tests different aspects of stability. A changed open reference can reveal lamp or throughput drift, while a changed dark level is especially important when the sample signal is weak.

## Colour coordinates, selective attenuation and clipping

The first RGBC example proceeds from a dim scene through white and coloured conditions to an overexposed interval. Its dim means over $[0,4)\,\mathrm{s}$ are 38.50, 10.41, 11.80 and 6.81 counts for clear, red, green and blue. For a stationary colour interval, a useful detector coordinate is
$$
p_k=\frac{\bar C_k-B_k}{\sum_{j\in\{R,G,B\}}(\bar C_j-B_j)},
 \qquad k\in\{R,G,B\},
\tag{4}
$$
where $B_k$ is that dim-scene mean. The fractions sum to one; they describe relative changes from the starting scene rather than standard chromaticity. Table 1 calculates them from channel means over interior windows. Averaging instantaneous fractions would be a different estimator.

The same table applies Eq. (2) to a separate filter sequence. Here the specified offsets are 3, 2, 2 and 1 counts, and the open-reference means over $[4.5,5.5)\,\mathrm{s}$ are 1824.55, 940.40, 1017.40 and 567.50 counts. Those observed means are used consistently as denominators. The filter sequence changes continuously, so the one-second windows around its extrema describe local transitions, not equilibrium filter plateaux.

*Dim-subtracted RGB fractions (upper group) and locally referenced filter transmissions (lower group). Fractions sum to one; each transmission uses its own channel reference. Time windows are half-open and in seconds.*

| Condition/window | Red | Green | Blue |
|---|---|---|---|
| **Dim-subtracted colour fractions $p_k$** |  |  |  |
| White, 6–14 | .374 | .401 | .224 |
| Red, 16–24 | .830 | .124 | .046 |
| Green, 26–34 | .130 | .788 | .082 |
| Blue, 36–44 | .100 | .135 | .765 |
| **Locally referenced filter transmissions $T_k$** |  |  |  |
| 14.5–15.5 | .872 | .238 | .162 |
| 24.5–25.5 | .224 | .781 | .245 |
| 34.5–35.5 | .169 | .212 | .847 |

Figure 2 separates channel discrimination from saturation. The coloured intervals favour their corresponding channels, while white does not give equal fractions because both illumination and channel responsivities are unequal. During $[46,49)\,\mathrm{s}$, all four channels remain at 4100 counts. Their near-equal fractions then reflect lost information, and zero scatter reflects clipping. The nominal ceiling follows the pinned approximately $11.12\,\mathrm{ms}$ integration and $16\times$ gain configuration [6](https://raw.githubusercontent.com/arduino-libraries/Arduino_APDS9960/1.0.4/src/Arduino_APDS9960.cpp), [1](https://docs.broadcom.com/doc/AV02-4191EN); the register's bit width does not define the usable optical range.

*Upper: raw clear and RGB counts, including the clipped interval. Lower: channel transmissions referenced to the open-window mean of a separate filter sequence. Each panel retains its own record time.* View data figure (built locally at `output/pdf/light-rgb.pdf`)

Reference choice has a visible numerical effect. With the specified, rather than locally observed, reference counts of 1800, 900, 1050 and 620, the nominally open interval gives RGB ratios 1.045, 0.969 and 0.915. Its mismatch is channel dependent, so one common intensity rescaling cannot remove it. Re-referencing changes the blue extremum from 0.775 to 0.847. The later open-window ratios over $[44.5,45.5)\,\mathrm{s}$ are 1.007, 1.001 and 1.007. This close return is useful, but neighbouring transitions still contribute to both windows; their difference is not a unique estimate of lamp drift or sample-replacement uncertainty.

## Bracketing a scalar relative detector

The LED example supplies a complementary test of the reference rather than another colour coordinate. The source and detector remain fixed while the path is blocked, opened, attenuated and reopened. Table 2 uses half-open receive-time windows that exclude transitions. Equal weight is assigned to the two dark-window means and to the two open-window means; longer intervals are not implicitly given a larger calibration weight.

*Bracketed LED-detector response in relative units. Means and sample SDs summarize within-window levels and fluctuations.*

| Receive interval (s) | Mean | SD |
|---|---|---|
| Dark, 1–9 | .01935 | .01766 |
| Open, 12–18 | .89762 | .02044 |
| Sample, 24–36 | .50592 | .02315 |
| Open, 42–48 | .89613 | .01441 |
| Dark, 52–59 | .02467 | .01802 |

The bracketed estimates are $D=0.022010$ and $R=0.896878$, giving $T_w=0.553126$. The mean ratio calculated with fixed entered levels $D=0.02$ and $R=0.90$ is 0.552185. Their difference of 0.000941 is an estimator choice, rather than an additional physical attenuation. The open means differ by $-0.001492$ detector unit and the dark means by $+0.005317$. The dark change is small relative to the open-minus-dark span but increasingly consequential for weak sample signals.

There are 41 negative pre-gate ratios near the dark intervals. These are background-subtraction diagnostics, not negative physical transmission. Silently clipping them before estimating an offset would bias the retained indications upward. The transmission display may exclude nonphysical results while preserving the underlying observations for this check. The Puck's sampling setting is $4\,\mathrm{Hz}$, below its documented $5\,\mathrm{Hz}$ limit [3](https://www.espruino.com/Reference#l_Puck_light); that setting does not establish a uniform delivered sequence.

Figure 3 retains the Puck's device-clock origin at $1000\,\mathrm{s}$. Its numerical windows use the separate receive clock. Regressing receive time against elapsed device time gives slope 0.999818 and an RMS residual of $2.24\,\mathrm{ms}$. This describes the relation between two example clocks, not either clock's absolute accuracy or a one-way transport latency. Bracketing stable states reduces the sensitivity of a mean ratio to such timing differences without making the clocks interchangeable.

## UV transmission and two stages of absolute calibration

The external UV example exposes another distinction: the ratio in Eq. (2) can cancel electrical scale factors, while an irradiance in $\,\mathrm{W\,m^{-2}}$ requires them. First relate ADC indication $q$ to terminal voltage, then voltage to a specified irradiance:
$$
U=gq+c,
\tag{5}
$$

$$
E=k(U_s-U_D)=kg(q_s-D).
\tag{6}
$$
A stable additive voltage offset cancels; uncertainty in $g$ and $k$ remains. Detector responsivity calibration needs a defined optical scale and spectral conditions [7](https://doi.org/10.6028/NIST.SP.250-41e2008). Spectral mismatch, out-of-band response and geometry can remain even when an electrical calibration is satisfactory [8](https://doi.org/10.6028/jres.106.030). A broad-band filter ratio is also distinct from a biologically weighted UV protection factor [9](https://www.cie.co.at/publications/characterization-and-calibration-methods-uv-radiometers).

*Upper: bracketed LED response on the Puck device clock. Lower: continuous UV counts and paired observations on their device-time axis, showing agreement within three counts.* View data figure (built locally at `output/pdf/light-rgb.pdf`)

For the UV trace, dark and open means over $[1,4)$ and $[6,9)\,\mathrm{s}$ are 9.85 and 609.90 counts, with sample SDs 1.30 and 1.54 counts. Sample means over $[11,14)$, $[16,19)$ and $[21,24)\,\mathrm{s}$ are 310.05, 250.19 and 180.20 counts. The paired observations use $D=10$ and $R=610$ counts. Table 3 retains that observation estimator rather than replacing it silently with plateau means.

*UV transmission and irradiance calculated with the stated electrical and detector coefficients. $u_T$ is single-reading precision from plateau scatter; coefficient calibration uncertainties enter the irradiance budget.*

| $q_s$ (count) | $T_w$ | $u_T$ | $E$ (mW/m$^2$) |
|---|---|---|---|
| 310 | .500 | .0030 | 9.68 |
| 250 | .400 | .0030 | 7.74 |
| 180 | .283 | .0030 | 5.48 |

The entered coefficients are $g=3.22580645\,\mathrm{mV/count}$, $c=0$ and $k=0.01\,\mathrm{W\,m^{-2}\,V^{-1}}$. The first equals the nominal $3.3\,\mathrm{V}$ endpoint divided by 1023, giving the nominal voltage-per-count scale used in the irradiance calculation. An external detector and conditioner must remain within the verified analog input range; the RGB sensor itself supplies no UV measurement.

Timestamp matching tests the observation association separately from the scale. At $12.477\,\mathrm{s}$ the paired value is 310 counts and the continuous signal is 309. At $27.505\,\mathrm{s}$ they are 310 and 313 counts. Across all six observation times, the largest discrepancy is three counts, equivalent to 0.005 in transmission for the 600-count denominator. The observations support plateau-level attenuation comparisons but not exact identity with individual continuous samples. The continuous record's approximately $50\,\mathrm{ms}$ median spacing does not resolve that value discrepancy.

## Precision, shared references and optical identifiability

For independent single-reading uncertainties in sample, reference and dark indications, Eq. (2) gives
$$
u_T^2=\frac{u_S^2+T_w^2u_R^2+(T_w-1)^2u_D^2}{(R-D)^2}.
\tag{7}
$$
This expression uses one dark uncertainty because the same estimate enters numerator and denominator. Reusing dark and reference observations across several samples introduces covariance between their ratios. Temporal correlation and positioning variation also prevent the number of readings from being treated automatically as the number of independent trials.

Using the UV plateau SDs as single-reading uncertainties gives approximately 0.0030 for the first three observations. This conditional precision excludes gain calibration, spectral mismatch and geometry. Independent ideal ADC rounding alone would contribute about 0.00059 to the first ratio. It is smaller than the observed fluctuation contribution; adding it again to the empirical SD would double-count the rounding already present in those fluctuations.

The RGB transition windows and Puck sample interval constrain different aspects of this budget. Variation through a deliberate filter transition cannot be assigned a stationary-transmission standard error. Likewise, dividing the Puck sample SD of 0.02315 by the square root of 48 does not by itself establish an uncertainty of the mean. Complete sample replacements, repeated brackets and block statistics at relevant timescales would distinguish source drift, temporal covariance and geometrical repeatability.

A neutral-attenuator test at several source levels assesses proportionality while holding spectral shape fixed. Repeating it with a second source spectrum tests transfer of the spectral weighting. These checks answer different questions from moving farther from a lamp, which can confound source geometry and detector nonlinearity. For RGB channels, retaining the full vector also prevents apparent brightness stability from concealing a colour change.

The common reduction thus supports several precise but different conclusions: an unsaturated colour coordinate, a detector-weighted filter ratio, a bracketed scalar indication and a UV irradiance evaluated with the stated calibration coefficients. Resolved spectra, molecular identification and absolute optical calibration involve spectral resolution, reference measurements and the detector response in addition to relative signal precision. Reference substitution becomes informative when these remaining dependencies are kept attached to the quantity being inferred.

## References

1. Avago Technologies. [APDS-9960 data sheet, AV02-4191EN](https://docs.broadcom.com/doc/AV02-4191EN).
2. F. M. Mims III (1992). [Sun Photometer with Light-Emitting Diodes as Spectrally Selective Detectors](https://doi.org/10.1364/AO.31.006965).
3. Espruino. [Puck.light() and Puck.js Hardware Reference](https://www.espruino.com/Reference#l_Puck_light).
4. A. Besozzi, G. Gibertoni, L. Rovati and A. Gibaldi (2026). [Flexible Calibration Method: Photometric and Radiometric Measurements with Compact Low-Cost Multi-Channel Sensors](https://doi.org/10.21014/actaimeko.v15i2.2267).
5. R. W. Burke and R. Mavrodineanu (1983). [Accuracy in Analytical Spectrophotometry, NBS SP260-81](https://doi.org/10.6028/NBS.SP.260-81).
6. Arduino. [Arduino_APDS9960, version 1.0.4: pinned implementation](https://raw.githubusercontent.com/arduino-libraries/Arduino_APDS9960/1.0.4/src/Arduino_APDS9960.cpp).
7. T. C. Larason and J. M. Houston (2008). [Spectroradiometric Detector Measurements: Ultraviolet, Visible, and Near-Infrared Detectors for Spectral Power](https://doi.org/10.6028/NIST.SP.250-41e2008).
8. T. C. Larason and C. L. Cromer (2001). [Sources of Error in UV Radiation Measurements](https://doi.org/10.6028/jres.106.030).
9. International Commission on Illumination (2016). [Characterization and Calibration Methods of UV Radiometers, CIE 220:2016](https://www.cie.co.at/publications/characterization-and-calibration-methods-uv-radiometers).
