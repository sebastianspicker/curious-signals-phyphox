# Infrared Radiometry: Calibration and Distance-Dependent Heating

*August 2020*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

**Abstract.** An infrared temperature indication combines scene radiation with the detector's thermal state and application calibration. Two example investigations expose different parts of that inference. A TMP006 compensation model gives a target-temperature rise of 21.88 K while die temperature rises by only 0.204 K; changing sensitivity by ten percent shifts the hot-interval result from 44.91 $^\circ$C to 43.12 or 47.06 $^\circ$C. A separate TMP007 distance sequence has an outward–return difference of 1.040 K at the same displacement. The first example quantifies a calibration dependence hidden by small short-term scatter; the second prevents an equilibrium heating law from being inferred from a history-dependent trace. A constant-view translation geometry separates source-distance heating from changes in the thermometer's view.

**Keywords:**
Infrared thermometry, thermopile compensation, application calibration, emissivity, thermal response, radiative balance.

## From scene radiation to target temperature

A thermopile senses radiative exchange rather than making thermal contact with its target. Its indicated object temperature therefore depends on the target's emission, reflected surroundings, angular coverage and the sensor's own temperature. The TMP006 reports thermopile voltage and die temperature for an external calculation[1]; the TMP007 incorporates an object-temperature calculation internally[2]. Neither arrangement removes the need to characterize the optical scene. An output labelled ambient is the detector die temperature, not an independent room-air measurement.

Two distances must also be distinguished. Moving a thermometer away from a fixed target changes the target's angular size and potentially the fraction of the detector view that it fills. Moving target and thermometer together away from a heating lamp can instead preserve their internal viewing geometry while changing incident heating. The astronomical distance–temperature activity[3] becomes quantitatively useful only after these causal changes are separated.

Figure 1 connects stationary calibration to the translating-stage experiment. A high-emissivity target with a contact reference establishes temperature independently of the infrared indication. Target material, aperture, viewing angle and surrounding surfaces remain fixed while calibration temperatures are varied. The calibration then applies to the assembled optical arrangement, including any window or enclosure[4], [5]. A surface that partly fills the field of view or reflects a hot lamp cannot be represented solely by its contact temperature.

**Figure 1.** A contact reference anchors stationary radiometric calibration. For a heating-distance test, target and thermopile move together relative to the lamp, preserving target coverage and viewing angle. An independent rail reference establishes source distance. View figure in the paper (built locally at `output/pdf/ir-distance.pdf`).

## Compensation and application sensitivity

The TMP006 example makes the conversion explicit. For die temperature $T_d$ expressed in kelvin, reference temperature $T_{\rm ref}=298.15\,\mathrm{K}$ and $\Delta=T_d-T_{\rm ref}$, use

$$
\begin{aligned}
 S&=S_0(1+A_1\Delta+A_2\Delta^2),\\
 V_{\rm os}&=B_0+B_1\Delta+B_2\Delta^2,\\
 u&=V_{\rm obj}-V_{\rm os},\qquad f=u+C_2u^2,\\
 T_o&=(T_d^4+f/S)^{1/4}.
 \end{aligned}
\tag{1}
$$

This temperature-dependent model follows the TMP006 calibration treatment[4]. The numerical reduction uses the example's per-observation sensitivities and offsets, with $S_0=5.0\times10^{-14}\,\mathrm{V\,K^{-4}}$ and $C_2=13.4\,\mathrm{V^{-1}}$. The nonlinear correction is applied to the voltage residual $u$ at each observation. It is $f$, rather than $u$ alone, that enters the fourth-power relation. Positive sensitivity and a positive fourth-root argument are required; Celsius output is obtained only after subtracting 273.15 from the result in kelvin.

Thermopile voltage retains its sign through this calculation. Twenty-one of the 61 example observations have negative voltage. Such a value is admissible for an offset-referenced radiometric signal and is not a negative absolute radiation level or a negative absolute target temperature. An unsigned interpretation would fail before optical calibration was considered. Signed voltage and die indication provide the observables used by the application-sensitivity model.

Table 1 gives half-open receive-time windows inside the temperature levels. The ambient interval $[0,9)\,\mathrm{s}$ averages $23.024\,\mathrm{^\circ C}$ for the model object temperature and $23.049\,\mathrm{^\circ C}$ for the die. The hot interval $[28,38)\,\mathrm{s}$ gives 44.909 and $23.253\,\mathrm{^\circ C}$, respectively. The inferred target change of 21.885 K is therefore distinct from the 0.204-K die change. Intermediate levels accompany corresponding changes in signed thermopile voltage, as Fig. 2 shows.

**Table 1.** TMP006 die-temperature means and object-temperature means calculated with Eq. (1) and the adopted sensitivity. SD$_o$ is the within-interval sample standard deviation of object temperature.

| Window (s) | $T_o$ ($^\circ$C) | $T_d$ ($^\circ$C) | SD$_o$ (K) |
| --- | --- | --- | --- |
| 0–9 | 23.024 | 23.049 | 0.137 |
| 12–19 | 34.971 | 23.136 | 0.063 |
| 28–38 | 44.909 | 23.253 | 0.100 |
| 42–48 | 30.028 | 23.319 | 0.181 |

**Figure 2.** TMP006 object-temperature calculation and die indication (a), and signed thermopile voltage (b), on the receive-time axis. The independent TMP007 record (c) shows distinct outward and return temperature branches against mouse displacement, alongside the die indication. View figure in the paper (built locally at `output/pdf/ir-distance.pdf`).

The hot-state object SD is $0.0997\,\mathrm{K}$, but that small scatter does not establish sensitivity accuracy. Recalculate each hot observation with $S$ multiplied by 1.1 or 0.9, retaining its voltage, offset and die temperature and the complete nonlinear correction. The mean becomes 43.117 or $47.059\,\mathrm{^\circ C}$, compared with $44.909\,\mathrm{^\circ C}$. These changed-model values are not confidence limits. They demonstrate a scale dependence much larger than the interval fluctuations.

At fixed corrected signal $f$, the local sensitivity is

$$
\frac{\partial T_o}{\partial S}=-\frac{f}{4S^2T_o^3}.
\tag{2}
$$

Coefficient covariance, reference temperature and optical coupling also enter a calibration uncertainty. In particular, die compensation from one local temperature need not remove spatial or transient package gradients; unchopped-thermopile measurements require these gradients to be controlled[6]. Calibration across independently varied target and die temperatures separates these contributions more effectively than fitting one warming trajectory. Additional temperature combinations and remounting tests assess transfer beyond the fitted conditions.

## Distance and acquisition history

The TMP007 example adds a displacement coordinate to an object-temperature indication. It spans 27.594–38.125 $^\circ$C, while die temperature spans 22.750–23.188 $^\circ$C and averages 22.993 $^\circ$C. The different ranges are physically meaningful, but their difference is not a measured target-to-air temperature difference.

Signed mouse increments accumulate into two-axis coordinates whose norm is displacement $d$. A straight rail on one side of the reset origin permits the calibration $r=r_0+kd$, with independently determined origin $r_0$ and scale $k$. The example is expressed in displacement counts; conversion to source distance uses the origin and scale in the relation above. The norm describes displacement from the reset position, rather than total travel length.

Infrared and mouse reports retain separate receive timestamps. Each infrared indication is associated with the most recent mouse position. The example infrared spacing is 0.3 s; it does not establish either a synchronized physical trigger or a detector response time. During motion, position age and delivery latency can introduce a position error of order velocity times timing mismatch. Stationary selection suppresses that term but does not by itself establish thermal equilibrium.

At 1750 counts, the outward mean over $[10.5,12)\,\mathrm{s}$ is $29.894\,\mathrm{^\circ C}$, whereas the return mean over $[26.4,27.3)\,\mathrm{s}$ is $28.854\,\mathrm{^\circ C}$. Their difference is 1.040 K. Table 2 retains endpoint comparisons as well. The branch separation demonstrates dependence on acquisition history at a repeated displacement. Target heat capacity, detector settling, lamp drift and position error can all contribute; this trajectory cannot identify those causes separately.

**Table 2.** TMP007 mean object-temperature indications and sample counts $N$ in half-open time windows. Outward and return values at 1750 displacement counts differ by 1.040 K.

| Window (s) | Counts | $N$ | Mean ($^\circ$C) |
| --- | --- | --- | --- |
| Outward, 0–1.5 | 0 | 5 | 38.031 |
| Outward, 10.5–12 | 1750 | 5 | 29.894 |
| Outward, 19.5–21 | 3250 | 5 | 27.850 |
| Return, 26.4–27.3 | 1750 | 3 | 28.854 |

## What an equilibrium heating law would require

For a target of heat capacity $C_{\rm th}$, illuminated area $A$, absorptivity $\alpha$ and emissivity $\epsilon$, a useful lumped energy balance is

$$
C_{\rm th}\dot T_s=\alpha A F(r)-G(T_s-T_b)
 -\epsilon\sigma A(T_s^4-T_b^4),
\tag{3}
$$

where $G$ represents linearized conductive and convective losses and $T_b$ a thermal background. The fourth-power terms require absolute temperature. An inverse-square source law concerns incident irradiance $F(r)$, rather than Celsius temperature or a thermometer indication. Establishing optical dilution is consequently an earlier part of the experiment, separate from estimating thermal response.

At equilibrium and for $|T_s-T_b|\ll T_b$, linearizing the radiation term gives

$$
T_s-T_b\simeq\frac{\alpha A F(r)}{G+4\epsilon\sigma A T_b^3}.
\tag{4}
$$

A small temperature excess can therefore follow $r^{-2}$ when loss coefficients are constant. In the contrasting radiation-dominated limit with $T_s\gg T_b$, $T_s$ can approach $r^{-1/2}$. Neither limit is established by the history-dependent TMP007 branches, and neither can be selected solely because a falling curve resembles a power law.

The radiometric scene must remain controlled while testing either limit. An opaque surface emits its own radiation and reflects the surroundings. Under a grey approximation, a full-view radiance contribution involves $\epsilon T_s^4+(1-\epsilon)T_{\rm refl}^4$; partial coverage adds surrounding surfaces to the detector view. Application calibration explicitly depends on material, size, distance and environmental heat transfer[5]. Size-of-source tests probe this dependence in radiation-thermometer calibration[7]. Moving target and detector together preserves angular coverage; moving only the detector does not.

The two examples thus impose complementary tests. First establish that a contact-referenced target, scene geometry and detector thermal environment support the temperature conversion. Then establish stationary target temperatures at independently calibrated source distances. Agreement of longer-dwell outward and return observations, including repeated reference positions, is necessary before fitting an equilibrium law. The temperature conversion, equilibrium assessment and radiometric calibration enter as distinct steps in interpreting the temperature–distance relation.

## References

1. [Texas Instruments, *TMP006/B Infrared Thermopile Sensor in Chip-Scale Package*, SBOS518E (2015).](https://www.ti.com/lit/ds/symlink/tmp006.pdf)

2. [Texas Instruments, *TMP007 Infrared Thermopile Sensor with Integrated Math Engine*, SBOS685C (2015).](https://www.ti.com/lit/ds/sbos685c/sbos685c.pdf)

3. [S. J. Spicker, A. Küpper and A. Bresges, “astro-lab@home—Bringing Science to the Sofa,” *Communicating Astronomy with the Public Journal* 31, 37–41 (2022).](https://physikdidaktik.uni-koeln.de/sites/physikdidaktik/Publikationen/CAPjournal_No-31_October-2022_astrolab-at-home_Bringing-Science-to-the-Sofa.pdf)

4. [Texas Instruments, *TMP006 User’s Guide*, SBOU107 (2011).](https://cdn.sparkfun.com/datasheets/Sensors/Temp/sbou107.pdf)

5. [Texas Instruments, *TMP007 Calibration Guide*, SBOU142 (2014).](https://www.ti.com/lit/ug/sbou142/sbou142.pdf)

6. [E. Sebastián, C. Armiens and J. Gómez-Elvira, “Infrared Temperature Measurement Uncertainty for Unchopped Thermopile in Presence of Case Thermal Gradients,” *Infrared Physics & Technology* 54, 75–83 (2011).](https://doi.org/10.1016/j.infrared.2010.12.038)

7. [J. de Lucas, “Measurement, Validation and Uncertainty of an Experimental Procedure to Characterize the Size-of-Source Effect of Radiation Thermometers, in the Framework of an Industrial Calibration Laboratory,” *Sensors* 22, 8284 (2022).](https://doi.org/10.3390/s22218284)

