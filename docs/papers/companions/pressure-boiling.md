# Pressure-Dependent Boiling: Equilibrium Curves and Observational Thresholds

*December 2019*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

**Abstract.** Fifteen paired pressure–temperature observations in the data distinguish a visible boiling threshold from an equilibrium coexistence curve. The five sustained-boiling observations have an RMS deviation of 0.25 K from IAPWS saturation, while liquid-labelled observations lie about 5.0 K below it. A Clausius–Clapeyron fit gives an interval-dependent apparent enthalpy of 42.5 kJ/mol. Conditional uncertainty, instrument range and comparison with Martian pressure delimit the inference: the lowest example pressure remains 7.92 times the planetary reference.

**Keywords:** Boiling, saturation pressure, phase equilibrium, nucleation, thermometry.

## Equilibrium and the appearance of bubbles

The familiar boiling temperature near 100 $^\circ$C belongs to a particular absolute pressure. Equality of liquid and vapour chemical potentials defines a coexistence curve whose slope follows the Clapeyron equation,
$$
\frac{dp_\sigma}{dT}=\frac{\Delta h_{\rm vap}}{T(v_g-v_l)}, \tag{1}
$$
with specific enthalpy change $\Delta h_{\rm vap}$ and specific volumes $v_g$ and $v_l$. Taking the vapour as ideal, neglecting liquid volume and treating the molar enthalpy as constant gives
$$
\ln(p_\sigma/p_*)=a-\frac{\Delta H_{\rm vap}}{RT}. \tag{2}
$$
The arbitrary reference pressure $p_*$ makes the logarithm dimensionless. This approximation describes a restricted interval; the numerical comparison below instead uses the temperature-dependent IAPWS saturation relation [1](https://iapws.org/technical-guidance/release/Supp-sat).

Surface tension, dissolved gas, nucleation sites and pressure history influence visible bubble formation. Homogeneous and heterogeneous nucleation need not follow a simple equilibrium threshold [2](https://doi.org/10.1002/aic.690210502); isolated bubbles after evacuation are therefore insufficient evidence of coexistence. Observation labels retain this distinction: zero denotes liquid without sustained boiling, one sustained boiling, and two an uncertain judgement. Only label one enters the enthalpy fit.

## Paired pressure and liquid temperature

Figure 1 combines a pressure-rated vessel, a calibrated absolute-pressure instrument and an independent immersed temperature probe. Wet isolation protects dry pressure electronics from water and condensation. The paired readings are transferred manually. Liquid temperature must be measured directly; the barometer chip's temperature cannot substitute for it.

*Figure 1. Apparatus schematic. Independent instruments measure liquid temperature and chamber absolute pressure while wet isolation protects the pressure connection.* View paper (built locally at `output/pdf/pressure-boiling.pdf`)

Expansion and evaporation can cool the liquid while the probe continues to relax. Pairing an immediate pressure with a delayed temperature would combine different states. Settled readings, known probe response and a reversible pressure sequence help distinguish equilibrium from lag and leakage. Gauge pressure requires an atmospheric reference before conversion to absolute pressure; the vessel's operating limits constrain the sequence.

A submerged nucleation site experiences an additional pressure approximately $\rho gh$. Probe depth and bubble location therefore affect comparison with a free-surface saturation curve. Noncondensable gas also separates total pressure from water-vapour partial pressure. Neither contribution should be absorbed into an unexplained thermometer correction.

The fifteen paired observations span 5.04–101.18 kPa and 32.06–96.60 $^\circ$C. Conversion uses $T=T_C+273.15$; temperature is not inferred from pressure. Bounded numerical inversion of the IAPWS saturation relation [1](https://iapws.org/technical-guidance/release/Supp-sat) supplies $T_\sigma(p)$ for comparison, independently of the observation label.

*Figure 2. Absolute pressure versus liquid temperature. The solid curve gives IAPWS saturation; open markers show all paired observations, and filled markers identify sustained boiling.* View paper (built locally at `output/pdf/pressure-boiling.pdf`)

## Saturation-temperature residuals and apparent enthalpy

With $r=T-T_\sigma(p)$, the five sustained-boiling observations have mean residual $-0.18$ K and RMS residual 0.25 K (Table 1). The liquid-labelled and uncertain groups have mean residuals $-5.00$ and $-0.99$ K. Joining all fifteen pairs into one phase boundary would erase this distinction between states and judgement confidence.

*Table 1. Sustained-boiling observations, residuals $r=T-T_\sigma(p)$ and propagated standard uncertainties $u_r$, treating the entered pressure and temperature uncertainties as independent standard uncertainties.*

| p (kPa) | Temperature (°C) | Residual (K) | u residual (K) |
| --- | --- | --- | --- |
| 90.04 | 96.60 | -0.10 | 0.20 |
| 60.00 | 85.62 | -0.30 | 0.20 |
| 39.92 | 75.35 | -0.46 | 0.21 |
| 25.14 | 65.09 | 0.01 | 0.22 |
| 10.13 | 46.00 | -0.05 | 0.28 |

Unweighted least squares of $\ln(p/1\,\mathrm{kPa})$ against $1/T$ for these five observations gives $\Delta H_{\rm app}=42.5\,\mathrm{kJ\,mol^{-1}}$ through Equation (2). This interval-dependent value summarizes the thermal dependence of vapour pressure; it does not resolve latent-heat variation or vapour nonideality. Regression scatter alone cannot establish its thermodynamic uncertainty.

At 39.92 kPa, the liquid temperature is 75.35 $^\circ$C rather than the reference 75.81 $^\circ$C. The discrepancy is small on the graph but material relative to the entered uncertainties. Its interpretation depends on probe response, pressure referencing and the boiling judgement.

## Uncertainty and the accessible inference

Interpreting the entered 0.1 kPa and 0.2 K as independent standard uncertainties gives
$$
u_r^2=u_T^2+\left(\frac{u_p}{dp_\sigma/dT}\right)^2. \tag{3}
$$
This conditional propagation excludes lag, common calibration bias and judgement uncertainty. The largest normalized residual is 2.20. At lower pressure, the smaller saturation-curve slope gives pressure uncertainty a larger temperature-equivalent contribution, explaining the rise of $u_r$ towards 10 kPa. A common thermometer offset would not diminish through averaging five observations.

## Instrument range and the planetary comparison

The lowest example pressure, 5.039 kPa, remains 7.92 times NASA's 0.636-kPa Martian reference at mean radius; the reported seasonal interval is about 0.40–0.87 kPa [3](https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html). Water's triple point is approximately 0.611657 kPa at 273.16 K. IAPWS inversion at 0.636 kPa gives a conditional saturation temperature of about 0.55 $^\circ$C. The stable-liquid relation must not be extrapolated below the triple-point pressure.

The LPS22HB and BMP280 lower limits, 26 and 30 kPa [4](https://www.st.com/resource/en/datasheet/lps22hb.pdf), [5](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf), are about 41 and 47 times the Martian reference. Five example states, including two sustained-boiling observations, lie below both limits. Covering even the full example interval therefore requires an appropriate lower-range instrument and wet-compatible connection.

Thermodynamically favourable coordinates alone do not establish persistent Martian liquid water: ice and heat availability, atmospheric undersaturation and evaporation matter, while salts change the phase relations [6](https://doi.org/10.1029/2000JE001360). The observations establish the pressure dependence of the visible boiling threshold over the measured interval.

## References

1. [IAPWS (1992), Revised Supplementary Release on Saturation Properties of Ordinary Water Substance, SR1-86(1992).](https://iapws.org/technical-guidance/release/Supp-sat)
2. [M. Blander and J. L. Katz (1975), Bubble Nucleation in Liquids, AIChE Journal 21, 833–848.](https://doi.org/10.1002/aic.690210502)
3. [D. R. Williams, Mars Fact Sheet, NASA Goddard/NSSDCA; pressure at mean radius, accessed October 2026.](https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html)
4. [STMicroelectronics (2017), LPS22HB: MEMS Nano Pressure Sensor, DocID027083, revision 6.](https://www.st.com/resource/en/datasheet/lps22hb.pdf)
5. [Bosch Sensortec (2021), BMP280 Digital Pressure Sensor, BST-BMP280-DS001, revision 1.26.](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf)
6. [R. M. Haberle et al. (2001), On the Possibility of Liquid Water on Present-Day Mars, Journal of Geophysical Research: Planets 106(E10), 23317–23326.](https://doi.org/10.1029/2000JE001360)
