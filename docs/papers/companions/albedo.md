# From Reflected Light to Relative Reflectance

*June 2018*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

Surface brightness becomes a reflectance measurement only after illumination, viewing geometry and detector weighting have been specified. In example phone and SensorTag records, dark-subtracted grey-to-reference ratios are 0.364 and 0.368; black-to-reference ratios are approximately 0.042 and 0.041. The full-record extrema contrast instead approaches 100% because the sequence includes a covered sensor. Calibrated reflectance requires a characterized reference and matched geometry, while a planetary albedo additionally depends on angular scattering and spectral integration.

**Keywords:** Reflectance, albedo, optical sensors, reference substitution, astronomy education.

## From reflected light to albedo

The astro-lab activity compares lamp-illuminated reflecting surfaces using a phone or SensorTag [1](https://physikdidaktik.uni-koeln.de/sites/physikdidaktik/Publikationen/CAPjournal_No-31_October-2022_astrolab-at-home_Bringing-Science-to-the-Sofa.pdf). At fixed illumination and viewing directions, reference substitution compares surfaces while preserving optical throughput. The signal nevertheless retains the detector's wavelength weighting and restricted collection angle.

Nicodemus and colleagues distinguish directional measurements, hemispherically integrated reflectance and whole-planet albedo [2](https://doi.org/10.6028/NBS.MONO.160). The experiment directly establishes a detector-weighted sample-to-reference ratio. Absolute reflectance requires a characterized reference and matching geometry. Planetary albedo additionally requires the illuminated body's angular scattering and, for an energy budget, spectral integration.

## Instrument and geometry

Use a stable lamp, an exchangeable sample holder and a baffled detector arranged as in Fig. 1. The lamp, detector, incidence angle, viewing angle and illuminated area remain fixed while the target is replaced. Prevent direct lamp radiation from reaching the detector. Record surface orientation because texture and gloss can make reflection strongly directional.

*Apparatus schematic. Reference and sample occupy the same holder. Fixed incidence and viewing directions define the comparison; the baffle suppresses direct illumination of the sensor.* View apparatus schematic (built locally at `output/pdf/albedo.pdf`)

The OPT3001 approximately follows human photopic sensitivity  [3](https://www.ti.com/lit/ds/symlink/opt3001.pdf). This weighting matters for coloured targets: a photometric ratio need not equal a ratio of total radiant power. The phone has its own sensor response and gain, so the two acquisition paths are reduced separately.

The example SensorTag spacing is 0.8 s, compared with approximately 0.1 s for the phone. Both resolve the stable target plateaux. SensorTag timestamps record notification arrival, while phone timestamps follow sensor events. Missing notifications therefore leave time gaps; delivery jitter and integration still affect the time assigned to an optical change.

## Reference substitution and example reduction

Let $D$ be the covered-sensor mean, $X_r$ the reference mean and $X_s$ the sample mean. The operational ratio is
$$
q_s=\frac{X_s-D}{X_r-D}.
\tag{1}
$$
For a characterized reference factor $\rho_r$, a corresponding sample factor is $\rho_s=\rho_r q_s$ only when the geometry and spectral transfer are appropriate. We report $q_s$ as the sample-to-reference ratio, with the characterized reference factor defining the corresponding reflectance scale.

Both sequences progress from a covered sensor to a white reference, grey and black targets, then another covered interval. Estimate $D$ by pooling samples in $[0,7)$ and $[57,60.5)$ s. The reference, grey and black means use $[9,23)$, $[25,39)$ and $[41,55)$ s, respectively. These interior windows exclude transitions. Figure 2 expresses each trace relative to its own dark-subtracted reference.

*Dark-subtracted phone and SensorTag signals normalized to their respective white references. Grey and black plateaux retain approximately 0.36 and 0.04 of the reference signal.* View data figure (built locally at `output/pdf/albedo.pdf`)

*Phone and SensorTag mean signals (arbitrary units) and dark-subtracted sample-to-reference ratios $q$.*

| Quantity | Phone | SensorTag |
|---|---|---|
| Covered-sensor mean $D$ | 0.317 | 0.832 |
| White-reference mean $X_r$ | 522.30 | 432.39 |
| Grey-target mean $X_g$ | 190.36 | 159.50 |
| Black-target mean $X_b$ | 22.19 | 18.55 |
| Grey ratio $q_g$ | 0.3641 | 0.3677 |
| Black ratio $q_b$ | 0.04190 | 0.04106 |

The grey ratios differ by approximately 0.0036, or 1% of their magnitude. This agreement compares the two reductions; its interpretation across instruments depends on matched spectra, geometry and instrument responses. The black ratios are more sensitive to the covered-sensor correction because their net signals are small.

The built-in display instead calculates the full-record contrast
$$
C=100\frac{X_{\max}-X_{\min}}{X_{\max}}.
\tag{2}
$$
It gives 99.990% for the phone record and 99.818% for SensorTag. The near-total contrast is caused by including the deliberately covered intervals. It contains little information about the grey target's reflectance. Maxima and minima also depend on noise and record length. Predeclared plateau means address the intended surface comparison more directly.

## Uncertainty and validation

For $A=X_s-D$ and $H=X_r-D$, the ratio sensitivities are
$$
\frac{\partial q_s}{\partial X_s}=\frac{1}{H},\quad
 \frac{\partial q_s}{\partial X_r}=-\frac{A}{H^2},\quad
 \frac{\partial q_s}{\partial D}=\frac{A-H}{H^2}.
\tag{3}
$$
The same dark estimate enters both numerator and denominator, so two independent dark-error terms would be inappropriate. Propagate the joint input covariance. Reference interpolation and lamp drift can introduce further correlations. The scatter of individual readings should be distinguished from variability between complete target replacements.

A laboratory sequence should alternate reference, sample and reference rather than acquire all references first. Compare dark readings before and after the sequence, test linearity over the working signal range, and repeat each physical replacement. Then use a second characterized surface, withheld from calibration, to check the inferred factor. This follows the reference-transfer logic of spectral reflectance metrology, where calibrated standards and defined collection geometry establish the scale [4](https://doi.org/10.6028/NIST.SP.250-48). These checks distinguish repeatability within a plateau from transfer across physical target replacements. Changing the viewing angle and lamp spectrum tests the range over which the comparison remains transferable.

## Spectral weighting and planetary interpretation

For a fixed geometry, channel $c$ responds schematically as
$$
X_c-D_c=G_c\int E_\lambda\,\rho_{\rm geom}(\lambda)
 S_c(\lambda)\,d\lambda,
\tag{4}
$$
where $E_\lambda$ is the illuminating spectrum, $S_c$ the channel responsivity and $G_c$ the fixed geometrical and electronic factor. A ratio cancels $G_c$ when sample and reference share it, but the integral retains its spectral weighting. The two grey-target ratios can therefore agree even if the detectors would disagree for a strongly coloured surface or another lamp. Such agreement does not determine the responsivity curves or the surface's resolved reflectance spectrum.

For reflected light from a distant, unresolved planet,
$$
\frac{F_p}{F_\star}=A_g\left(\frac{R_p}{a}\right)^2\Phi(\alpha),
\tag{5}
$$
where $A_g$ is geometric albedo and $\Phi$ the phase function normalized at full phase. Modern phase-curve models explicitly connect albedo to scattering and viewing geometry [5](https://doi.org/10.1038/s41550-021-01444-7). A single brightness contrast therefore leaves radius, illumination and phase-function dependencies unresolved. At each wavelength the phase integral $Q=2\int_0^\pi\Phi(\alpha)\sin\alpha\,d\alpha$ connects spherical and geometric albedo, $A_s=Q A_g$. Bond albedo then averages $A_s$ over the incident stellar spectrum. Neither the directional sample ratio nor three broad colour channels determine these integrations.

## References

1. S. J. Spicker, A. Küpper and A. Bresges (2022). [astro-lab@home—Bringing Science to the Sofa](https://physikdidaktik.uni-koeln.de/sites/physikdidaktik/Publikationen/CAPjournal_No-31_October-2022_astrolab-at-home_Bringing-Science-to-the-Sofa.pdf).
2. F. E. Nicodemus et al. (1977). [Geometrical Considerations and Nomenclature for Reflectance, NBS Monograph 160](https://doi.org/10.6028/NBS.MONO.160).
3. Texas Instruments (2017). [OPT3001 Ambient Light Sensor, Rev. C](https://www.ti.com/lit/ds/symlink/opt3001.pdf).
4. P. Y. Barnes, E. A. Early and A. C. Parr (1998). [Spectral Reflectance, NIST SP250-48](https://doi.org/10.6028/NIST.SP.250-48).
5. K. Heng, B. M. Morris and D. Kitzmann (2021). [Closed-Form ab Initio Solutions of Geometric Albedos and Reflected Light Phase Curves of Exoplanets](https://doi.org/10.1038/s41550-021-01444-7).
