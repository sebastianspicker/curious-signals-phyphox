# Settled-Angle Polarimetry: Scale, Floor and Angular Zero in Malus' Law

*September 2018*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

A settled-angle polarization experiment separates the angular response of an analyzer from the arbitrary scale of a light sensor. Ten paired example observations are compared with continuous light plateaux at the same protractor settings. A harmonic fit to the plateau means gives an amplitude of 1020.44 counts, a floor of 13.04 counts and an angular-zero estimate of 0.012 degrees. The root-mean-square residual decreases from 7.13 counts for individual snapshots to 0.51 counts for interior means. These estimates explain the positive residuals obtained when an independently specified parallel reference is used; angular accuracy is set by the angle reference, while the crossed-analyzer floor combines several optical and detector contributions.

**Keywords:** Malus' law, polarization, relative photometry, harmonic regression, angular calibration.

## An angular projection with a measurable floor

The intensity transmitted by an ideal analyzer follows from the projection of a linearly polarized electric field onto its transmission axis. Squaring the field amplitude gives
$$
S(\theta)=B+A\cos^2(\theta-\theta_0),
\tag{1}
$$
where $A$ is the parallel-minus-crossed signal, $B$ the angularly independent floor and $\theta_0$ the protractor reading corresponding to parallel axes. The square applies to the cosine, rather than to the angle itself. A detector need not provide an absolute radiometric unit to test this relative dependence; it must respond linearly while the spectrum and geometry remain fixed.

Monteiro and colleagues used a smartphone's ambient-light and orientation sensors with an LCD source [1](https://doi.org/10.1119/1.4981030). An Arduino implementation by Freitas and colleagues measured analyzer angle using a mechanically coupled potentiometer [2](https://doi.org/10.1088/1361-6552/aab43d). These arrangements emphasize complementary requirements: light and angle must refer to the same optical state, and the measured orientation must correspond to the angle between the polarization axes. A baffled Arduino arrangement also illustrates how stray-light suppression helps separate the angular signal from its floor [3](https://doi.org/10.21923/jesd.874073).

The present arrangement observes the angle on a protractor after rotation has stopped. An original Nano 33 BLE Sense supplies APDS-9960 clear counts while the analyzer alone rotates. The detector therefore remains in the same orientation. This avoids treating the detector board's movement as an independent measurement of analyzer angle, but requires an explicit manual association at each settled position.

## Geometry and paired observations

Figure 1 shows a fixed polarizer followed by a rotatable analyzer and detector. A verified linearly polarized LCD can replace the lamp–polarizer pair. Its displayed area and brightness must then remain fixed: translating the viewed region or changing screen settings can alter the detected signal independently of analyzer angle. The APDS-9960 has broad spectral channels and a programmable integration stage [4](https://docs.broadcom.com/doc/AV02-4191EN); the clear signal is used here as a relative optical observable.

*Fixed illumination and detector geometry with a rotating analyzer. The protractor angle is observed only after the light has settled.* View apparatus schematic (built locally at `output/pdf/malus-law.pdf`)

The data contain ten states from $0$ to $90$ degrees in $10$-degree increments, each lasting approximately six seconds. A paired observation includes the manual angle, one light count and its device and receive times. The captured count and both times match the continuous light record, so the snapshot association can be checked without assuming that the two clocks are equal.

For each setting $j=0,\ldots,9$, we also compute a mean over $[6j+1,6j+5.5)\,\mathrm{s}$ on the device clock. These 4.5-second interior windows exclude rotations and state boundaries. The resulting two reductions—one count per accepted observation and one mean per settled state—share the same ten angle values. They must not be interpreted as independent experiments.

## A fit that keeps angle zero explicit

The example's specified normalization is $(S-10)/1000$, equivalent to a floor of 10 counts and a parallel signal of 1010 counts. At zero degrees, the snapshot is 1029 counts, giving normalized transmission 1.019. At ten degrees, it is 1020 counts, giving 1.010 even though the ideal cosine-squared value is 0.96985. A value above unity is a useful diagnostic of the specified reference, rather than a reason to truncate the observation.

To estimate the shape without fixing the floor or parallel signal, rewrite Eq. (1) as
$$
S=a+b\cos2\theta+c\sin2\theta.
\tag{2}
$$
An unweighted linear least-squares solution gives $A=2\sqrt{b^2+c^2}$, $B=a-\sqrt{b^2+c^2}$ and $\theta_0=\tfrac12\operatorname{atan2}(c,b)$. The trigonometric arguments use radians internally. This parameterization handles an angular-zero offset without a logarithm near extinction, where both the signal and a cosine can approach zero.

*Upper: snapshot transmission and harmonic fit to settled means. Lower: snapshot and settled-mean residuals relative to $\cos^2\theta$, with the specified normalization retained. Their positive offset identifies the reference mismatch.* View data figure (built locally at `output/pdf/malus-law.pdf`)

*Harmonic-fit parameters for snapshots and 4.5-s means. Residual RMS summarizes scatter about each fit.*

| Quantity | Snapshots | 4.5-s means |
|---|---|---|
| $A$ (counts) | 1024.56 | 1020.44 |
| $B$ (counts) | 13.20 | 13.04 |
| $\theta_0$ (degrees) | $-0.097$ | 0.012 |
| Residual RMS (counts) | 7.13 | 0.51 |

The plateau fit implies a parallel response near 1033.5 counts, explaining the predominantly positive residuals against the specified 1010-count reference. The snapshot residual RMS relative to the fixed unit-amplitude, zero-offset cosine-squared curve is 0.0186 in normalized signal. Allowing amplitude, floor and zero to vary separates the fitted optical response from scatter around the model.

Averaging substantially reduces residual scatter. The fitted angular zero is a point estimate whose uncertainty depends on the protractor resolution and angular calibration. Reporting the numerical phase to hundredths of a degree distinguishes the fit's numerical precision from the uncertainty of the angle reference.

## Identifiability near extinction

The fitted floor combines every contribution that is approximately independent of angle: detector offset, ambient light, incomplete polarization and analyzer leakage can all enter $B$. A single sweep cannot identify these separately. A covered-detector reading, a source-off reading and a crossed-analyzer reading are physically different observations and should be compared before attributing the floor to polarizer extinction.

The angular sensitivity of normalized ideal transmission is $dT/d\theta=-\sin2(\theta-\theta_0)$ when angle is expressed in radians. Near 45 degrees, a one-degree zero error changes transmission by approximately 0.0175. Near parallel and crossed settings, the first derivative vanishes, so the same error enters at higher order. A small residual at the extrema is therefore a weak test of angular calibration; intermediate angles carry much of that information.

The example sequence supports a cosine-squared angular dependence after explicit allowance for its scale and floor. Repeating the sweep in both directions would distinguish backlash or angle-reading hysteresis from a stationary optical response. Rotating only the analyzer, retaining a stable spectrum and independently characterizing the floor are more informative than increasing the displayed fit precision.

## References

1. M. Monteiro, C. Stari, C. Cabeza and A. C. Martí (2017). [The Polarization of Light and Malus’ Law Using Smartphones](https://doi.org/10.1119/1.4981030).
2. W. P. S. Freitas, C. R. Cena, D. C. B. Alves and A. M. B. Goncalves (2018). [Arduino-Based Experiment Demonstrating Malus’s Law](https://doi.org/10.1088/1361-6552/aab43d).
3. E. Bilal Önder, F. Önder and M. Oğur (2021). [An Arduino Based Experiment to Prove and Teach Malus’ Law](https://doi.org/10.21923/jesd.874073).
4. Avago Technologies. [APDS-9960 data sheet, AV02-4191EN](https://docs.broadcom.com/doc/AV02-4191EN).
