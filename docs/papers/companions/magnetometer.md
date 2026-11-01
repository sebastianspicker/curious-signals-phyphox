# Magnetic Vector Calibration and Indirect DC Current Measurement

*February 2022*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

**Abstract.** Magnetic reorientation, local field change and indirect current measurement share an observable but require different references. We combine two vector-field examples with a fixed-geometry current example. The LSM9DS1 norm changes by approximately $0.971\,\mathrm{\mu T}$ on reorientation, while corrected MAG3110 initial and reoriented means are 48.337 and $48.363\,\mathrm{\mu T}$. These patterns diagnose different consistency properties without ranking device accuracy. A current-step reduction gives sensitivity $0.02012\,\mathrm{A/\mu T}$ and a single-reading scatter scale of 7.2 mA. The analysis separates vector calibration, assigned current states and the field-derived current reduction. Absolute induction, geographic heading and current accuracy each require reference information absent from a stable norm alone.

**Keywords:** Magnetic induction, vector calibration, hard iron, soft iron, DC current, inverse prediction.

## A field measurement in a moving frame

A magnetometer measures local magnetic induction in its own axes. The field includes terrestrial induction, nearby magnets, steel fixtures and currents. A changing laboratory field is a physical change of the measurand, whereas a fixed sensor-frame offset can imitate a field component. Calibration begins by deciding whether the desired result is local induction, heading or a controlled field change.

With sensor-to-laboratory rotation $R_j$, background $\boldsymbol B_0$ and controlled laboratory field $\boldsymbol B_{c,j}$, a linear model is

$$
\boldsymbol y_j=\boldsymbol b+A R_j^\mathsf T(\boldsymbol B_0+\boldsymbol B_{c,j})+\boldsymbol \epsilon_j.
\tag{1}
$$

Here $\boldsymbol b$ is fixed in sensor coordinates and $A$ represents scale, cross-axis response and fixed mounting-related distortion. Renaudin *et al.* describe a calibration model combining instrumentation and host-platform hard- and soft-iron effects [1]. Kok and Schön address the additional alignment needed when magnetic observations are combined with inertial orientation information [2].

A board-mounted magnetic object rotates with the sensor; a separate magnet generally does not. Moving either changes the conditions of the model. Reorientation in a uniform stable field preserves the true norm, so a displaced ellipsoid can reveal offset and anisotropy. Mapping it to a sphere leaves an arbitrary rotation unresolved. If the reference field magnitude is unknown, absolute scale is unresolved as well. A fitted sphere is consequently insufficient to establish calibrated laboratory components or geographic heading.

## Controlled fields and the instrument scale

The LSM9DS1 acquisition configures a $\pm400\,\mathrm{\mu T}$ range and 20-Hz magnetic output rate [3]. Its numerical conversion is $400/32768=0.012207\,\mathrm{\mu T/count}$, compared with the manufacturer's nominal $0.014\,\mathrm{\mu T/LSB}$ at the corresponding range [4]. Their ratio is 0.87193. Multiplying by the inverse ratio addresses only that nominal scale difference; it cannot remove offset or anisotropy.

The CC2541 legacy service supplies signed MAG3110 component words [5]. The chip specifies $0.10\,\mathrm{\mu T/LSB}$ [6], but a chip sensitivity does not establish the transmitted scale of every installed firmware version. The example assumes a checked conversion of $0.1\,\mathrm{\mu T/count}$ and subtracts offsets $(5,-3,8)\,\mathrm{\mu T}$. Raw-to-corrected differences reproduce these offsets and the applied transformation. The Nano and CC2541 records are separate field histories, not colocated comparisons.

A controlled coil fixture supplies the field reference. For ideal thin Helmholtz coils with $N_c$ turns each, radius and separation $R$, the central field is

$$
B_c=\mu_0\left(\frac45\right)^{3/2}\frac{N_cI}{R}.
\tag{2}
$$

Winding dimensions, alignment, positioning and a current reference qualify this calculation; field uniformity must be checked over the sensing volume. The schematic in Fig. 1 emphasizes the rigid geometry common to vector calibration and current inference. Its dimensions are not inferred from the example gain.

**Figure 1.** Reference geometry for magnetic calibration and indirect current measurement. Surveyed coils and axes establish the vector-field reference (upper); a separate ammeter establishes current with the coil and sensor fixed (lower). View figure in the article (built locally at `output/pdf/magnetometer.pdf`).

Widely distributed orientations, interspersed with stationary controls, constrain the offset and distortion matrix. At a surveyed pose, the half-difference $[\boldsymbol y(+I)-\boldsymbol y(-I)]/2$ suppresses a stable background. Repeated zero-current states expose changes between reversals. Independent orientations and remountings are stronger tests than dense sampling of one angular arc. Near zero field the nonnegative norm has a positive noise bias; a first-order norm uncertainty based on the gradient $\boldsymbol B/\|\boldsymbol B\|$ may then be inadequate.

## Reorientation and a changed local field

Figure 2 retains the separate clocks and scales of the field records. Table 1 uses finite-value means and sample SDs on left-closed, right-open intervals. Four missing Nano observations remain gaps; they are excluded from interval statistics without shifting the remaining times.

**Figure 2.** Nano (a) and CC2541 (b) records show the signed $x$ component and field norm through reorientation and local perturbations. Panel (c) shows $B_z$ during assigned current steps in fixed geometry. Each record retains its own clock. View figure in the article (built locally at `output/pdf/magnetometer.pdf`).

**Table 1.** Interval means and sample standard deviations of field norms ($\mu$T). Dispersions include motion within the selected windows.

| Instrument | Window (s) | Mean | SD |
| --- | --- | --- | --- |
| Nano, initial | 0–8 | 46.173 | 0.127 |
| Nano, reoriented | 22–28 | 45.203 | 0.230 |
| Nano, return | 52–59 | 46.136 | 0.128 |
| CC2541, initial | 0–15 | 48.337 | 0.133 |
| CC2541, reoriented | 27–35 | 48.363 | 0.117 |
| CC2541, near magnet | 42–44 | 147.957 | 3.085 |
| CC2541, return | 53–60 | 48.365 | 0.119 |

The Nano reorientation norm is $0.971\,\mathrm{\mu T}$ below its initial mean. A rigid rotation in a uniform stable field cannot explain that difference alone; under the example assumptions it diagnoses remaining offset or anisotropy. The interval's changing component means do not represent one fixed attitude. The initial and final norms differ by $-0.0369\,\mathrm{\mu T}$, smaller than their approximately $0.13\,\mathrm{\mu T}$ sample scatter, establishing return consistency for this trajectory rather than absolute accuracy.

For the corrected CC2541 example, initial and reoriented norms differ by only 0.055% while the components redistribute substantially. This is consistent with a nearly constant field over those poses. Calibration also depends on orientation coverage and common gain: limited coverage can hide distortion, and a common gain error preserves relative norm constancy. The two records describe these diagnostics under their respective field conditions.

The largest Nano norm is $162.596\,\mathrm{\mu T}$ at 32.940 s, about 3.52 times its initial mean. The CC2541 maximum is $151.14\,\mathrm{\mu T}$, about 3.13 times its initial mean. These large changes are consistent with local magnetic perturbations; they should be excluded from constant-background ellipsoid fitting. The CC2541 near-magnet SD reflects motion through a gradient, not noise at a fixed point. Averaging that interval cannot establish the field at one specified location. Heading would additionally require tilt compensation and alignment with an external horizontal reference.

## From a vector field to an indirect current

For a fixed air-core geometry and one selected axis, a local current relation is

$$
B_z=B_0+mI+\epsilon_B.
\tag{3}
$$

The intercept includes ambient projection and sensor offset; $m$ includes coil, lead and sensor geometry. Zero current therefore need not give zero field. The original phyphox current arrangement uses two field–current references and warns that moving the phone or coil invalidates the calibration [7]. A positioning clip alone does not make an air-core arrangement equivalent to a characterized commercial clamp meter.

Inverting two distinct measured pairs gives

$$
\widehat I=I_1+(B_z-B_1)\frac{I_2-I_1}{B_2-B_1}.
\tag{4}
$$

The field span must exceed its noise-based minimum. Current must be established with an independent ammeter for a physical calibration; field alone cannot identify both the current and the geometry factor. Many coil dimensions and sensor locations can produce the same slope.

The example assigns states 0, 0.1, 0.2, 0.3, 0.4, 0.2 and 0 A. Their values provide the coordinate for a worked reduction, not a second measured current channel. The indicated current trace is defined by $(B_z-30)/50$ when field is in microtesla. Regressing that derived current against the same $B_z$ merely recovers the definition, so its pointwise arithmetic agreement is not a linearity test.

Settled field plateaux provide a comparison with the assigned current states. The seven windows in Table 2 exclude transitions; each contains 60 observations except $[9,15)$ s, which contains 61. Using the first and fifth means as endpoint references gives

$$
\begin{aligned}
 B_1&=30.0744\,\mathrm{\mu T},\qquad B_2=49.9564\,\mathrm{\mu T},\\
 \frac{I_2-I_1}{B_2-B_1}&=0.0201187\,\mathrm{A/\mu T}.
 \end{aligned}
\tag{5}
$$

The remaining means test consistency without individually determining the endpoint relation.

**Table 2.** Current residuals from the two-endpoint conversion, relative to assigned states. The first and fifth plateaux define the conversion; remaining plateaux test its consistency.

| Window (s) | Assigned $I$ (A) | $\bar B_z$ ($\mu$T) | $\delta I$ (mA) |
| --- | --- | --- | --- |
| 1–7 | 0.0 | 30.074 | 0.00 |
| 9–15 | 0.1 | 34.992 | $-1.06$ |
| 17–23 | 0.2 | 39.977 | $-0.77$ |
| 25–31 | 0.3 | 44.994 | 0.17 |
| 33–39 | 0.4 | 49.956 | 0.00 |
| 41–47 | 0.2 | 39.969 | $-0.93$ |
| 49–55 | 0.0 | 29.957 | $-2.35$ |

An ordinary least-squares fit to the first five ascending plateau means gives intercept $30.0456\,\mathrm{\mu T}$ and slope $49.7660\,\mathrm{\mu T/A}$, with RMS residual $0.0227\,\mathrm{\mu T}$. This is an alternative linearity diagnostic on averaged points. The pooled within-plateau sample scatter is instead $0.358\,\mathrm{\mu T}$, corresponding to about 7.2 mA for one reading under the endpoint conversion. The small fit residual cannot be assigned to a future individual reading, nor can it establish uncertainty of an independently measured reference current.

## Background sensitivity and inverse uncertainty

The mean field on return to zero current lies $0.1169\,\mathrm{\mu T}$ below the initial zero-current mean, equivalent to $-2.35$ mA under the endpoint conversion. That return and the repeated 0.2-A state probe one trajectory. Repeated calibration cycles, current reversals and remountings would distinguish offset drift, direction dependence and geometry changes. The positive-current sequence alone does not test cancellation of ambient field under reversal.

A $1\,\mathrm{\mu T}$ background change causes a current error of about 20.1 mA at this sensitivity, larger than the single-reading scatter scale. Rotation can change the ambient projection without changing current; moving the return lead can change $m$. More averaging removes neither effect. This connects the vector-calibration problem directly to the validity interval of a scalar current conversion.

For $I=(B-B_0)/m$, when a new field observation is independent of the calibration coefficients,

$$
u_I^2=\frac{u_B^2+u_{B_0}^2+I^2u_m^2+
 2I\operatorname{cov}(B_0,m)}{m^2}.
\tag{6}
$$

The covariance term follows from the shared fit and cannot generally be omitted [8]. Current-reference uncertainty contributes to the coefficient uncertainty. Ordinary least squares treats assigned currents as exact; appreciable uncertainty in the reference coordinate calls for an errors-in-variables treatment, as discussed in Bartel's calibration analysis [9]. The uncertainty expression keeps the field and calibration contributions explicit when reporting current uncertainty.

Absolute magnetic induction requires an external field scale; heading also requires orientation information; current inference additionally requires a stable current-to-field geometry and an electrical reference. The common observable does not make those references interchangeable. Their explicit separation turns component motion, norm changes and current plateaux into complementary tests of a physical measurement model.

## References

1. [V. Renaudin, M. H. Afzal and G. Lachapelle. “Complete Triaxis Magnetometer Calibration in the Magnetic Domain.” Journal of Sensors 2010, 967245 (2010).](https://doi.org/10.1155/2010/967245)

2. [M. Kok and T. B. Schön. “Magnetometer Calibration Using Inertial Sensors.” IEEE Sensors Journal 16(14), 5679–5689 (2016).](https://doi.org/10.1109/JSEN.2016.2569160)

3. [Arduino. Arduino_LSM9DS1, version 1.1.1: acquisition configuration and numerical conversion.](https://raw.githubusercontent.com/arduino-libraries/Arduino_LSM9DS1/1.1.1/src/LSM9DS1.cpp)

4. [STMicroelectronics. LSM9DS1: iNEMO Inertial Module. Datasheet, revision 3 (2015).](https://www.st.com/resource/en/datasheet/lsm9ds1.pdf)

5. [phyphox. Texas Instruments SensorTag CC2541: External Sensor Definitions.](https://phyphox.org/wiki/index.php/Texas_Instruments_SensorTag_CC2541)

6. [Freescale Semiconductor. MAG3110: Xtrinsic Three-Axis Digital Magnetometer. Datasheet, revision 9.2 (2013).](https://www.nxp.com/docs/en/data-sheet/MAG3110.pdf)

7. [phyphox Development Team. Smartphones as Ammeters (2018).](https://phyphox.org/wiki/index.php?title=Smartphones_as_ammeters)

8. [Joint Committee for Guides in Metrology. Evaluation of Measurement Data—Guide to the Expression of Uncertainty in Measurement. JCGM 100:2008.](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf)

9. [T. W. Bartel. Implementation of Errors-in-Variables Regression and Monte Carlo Uncertainty Evaluation into Force Calibration Reporting at NIST. NIST Technical Note 1942 (2016).](https://doi.org/10.6028/NIST.TN.1942)

