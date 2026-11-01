# Paired Spectral Ratios: Separating Shared Features from Additional Attenuation

*February 2024*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

**Abstract.** Paired spectra can distinguish a shared absorption feature from additional attenuation only when wavelength registration and intensity normalization are preserved. The data contain twenty-one wavelength bins from 400 to 700 nm, with sample, star-only, continuum-reference and dark intensities. At 595 nm the sample is 55.2% below the entered continuum reference, but the star-only spectrum already contains a substantial depression. Dividing the two dark-subtracted spectra leaves an additional depth of 0.132, only 0.0225 above the neighbouring-bin baseline. The 15-nm sampling interval describes broad spectral sampling; narrow-line identification also depends on the instrumental line-spread function. The analysis relates these distinctions to transmission spectroscopy and shows why wavelength calibration uncertainty alone cannot establish spectral resolution or detection significance.

**Keywords:** Spectral ratios, transmission spectroscopy, wavelength calibration, resolving power, continuum normalization.

## A spectral feature needs a comparison

The physical meaning of a dark interval depends on the spectrum used as its reference. A stellar absorption line, a terrestrial absorber, a filter and a reduction artifact can all lower the detected intensity. Transit spectroscopy therefore compares spectra obtained in different configurations while retaining the stellar contribution. Seager and Sasselov developed predictions for atmospheric signatures superimposed on stellar radiation [1](https://doi.org/10.1086/309088); Brown formulated wavelength-dependent spectrum ratios and examined their dependence on atmospheric structure [2](https://doi.org/10.1086/320950). The classroom comparison considered here retains that logic while treating the extra absorber as a separate sample.

A useful scale comparison is the sodium result of Charbonneau et al. [3](https://doi.org/10.1086/338770): their differential transit depth was $(2.32\pm0.57)\times10^{-4}$ in a specifically defined bandpass. The additional depths in the present example are of order $10^{-1}$. They illustrate normalization and shared-feature rejection, rather than the observing precision or geometric dilution of an actual exoplanet atmosphere. Passing all source light through a filter does not reproduce the small atmospheric annulus of a transiting planet.

Each detected bin is itself an optical integral. For configuration $i$ and bin $j$, a linear model is
$$
C_{ij}=D_j+g_it_i\int L_j(\lambda)\eta(\lambda)F_i(\lambda)\,d\lambda,
\tag{1}
$$
where $L_j$ describes the bin and instrumental line-spread function, $\eta$ the spectral response, and $D_j$ the dark offset. A ratio of these integrals is generally a weighted mean, not the monochromatic transmission at the labelled centre. This distinction becomes decisive when the bins are wider than the feature of interest.

## Matched wavelength and intensity scales

A separate wavelength-calibrated spectrometer supplies the intensities. The comparison is transferred manually; three broad RGB channels cannot supply resolved line measurements. Figure 1 shows an interchangeable sample in a fixed optical path. Source-only, sample, continuum-reference and covered-detector observations must share slit geometry, detector response, exposure and gain, or be corrected to a common linear intensity scale. Independent peak normalization would remove some real attenuation and change the additional-depth estimator.

*Figure 1. Apparatus schematic. A separate spectrometer observes matched optical configurations. A covered-detector observation supplies the dark correction; all comparisons retain a common wavelength grid.* View paper (built locally at `output/pdf/spectral-fingerprints.pdf`)

Let $S,A,R,D$ denote sample, star-only, continuum-reference and dark intensity at one common wavelength. The normalized spectra and additional depth are
$$
T_S=\frac{S-D}{R-D},\qquad T_A=\frac{A-D}{R-D},
\tag{2}
$$

$$
d_{\rm add}=1-\frac{T_S}{T_A}=1-\frac{S-D}{A-D}.
\tag{3}
$$
The shared continuum reference cancels algebraically from $d_{\rm add}$. It remains essential to the separate normalized spectra and to defining an apparent line depth $1-T_S$. A near-zero star-only denominator amplifies noise, so no additional depth should be assigned there. Saturation invalidates the assumed linear ratios even if a subsequent normalization gives an innocuous value.

The example uses a common dark intensity of 2 arbitrary units, a ceiling of 200 and twenty-one checked wavelength pairs. All listed signals lie below that ceiling. Every result is evaluated at its actual calibrated wavelength, in 15-nm increments; the observation index is not used as a spectral coordinate. A separately entered comparison wavelength is a candidate location, not an identification assigned by the analysis.

*Figure 2. Upper: dark-subtracted sample and star-only intensities divided by the common continuum reference. Lower: additional depth $1-(S-D)/(A-D)$. Points are spaced by 15 nm; connecting lines guide the eye.* View paper (built locally at `output/pdf/spectral-fingerprints.pdf`)

## A shared depression near 595 nm

The most pronounced sample depression occurs at 595 nm, where $T_S=0.4479$ and $T_A=0.5162$. Relative to the entered continuum reference, the apparent sample depth is 0.5521. Much of this depression is shared by the star-only comparison. The additional depth after division is 0.1323, as Table 1 shows.

*Table 1. Normalized sample and star-only signals and additional attenuation depth at four wavelengths.*

| Wavelength (nm) | T sample | T star | Additional depth |
| --- | --- | --- | --- |
| 580 | 0.6260 | 0.7031 | 0.1097 |
| 595 | 0.4479 | 0.5162 | 0.1323 |
| 610 | 0.6348 | 0.7131 | 0.1097 |
| 655 | 0.6019 | 0.7103 | 0.1526 |

For an explicit local comparison, take the arithmetic mean of the 580- and 610-nm bins as a straight-line continuum at 595 nm. The resulting local depressions are 28.94% for the sample and 27.10% for the star-only spectrum. Applying the same neighbouring-bin baseline to $d_{\rm add}$ leaves an excess of 0.0225, or 2.25 percentage points. This is a descriptive local contrast, not a fitted line equivalent width. A curved continuum or a broad overlapping band would change it.

Across 400–700 nm, additional depth ranges from 0.1097 to 0.2973. This broad variation remains after the shared feature is suppressed. The 55.2% depression relative to the continuum reference therefore cannot be assigned entirely to the extra absorber. Shared features and broad attenuation must be separated before interpreting a local residual. The data instead support broad selective attenuation plus a modest local departure near a shared depression.

## Resolution and identifiability

The entered wavelength uncertainty is 0.2 nm, whereas the grid spacing is 15 nm. These quantities describe different properties. Calibration uncertainty concerns the wavelength assigned to a bin; resolution depends on the instrumental line-spread function and the available sampling. Robertson shows why even a line-spread function's FWHM does not define a universal resolving-power comparison [4](https://doi.org/10.1017/pasa.2013.26). The ratio $\lambda/(15\,\mathrm{nm})$ describes the sampling scale; measured resolving power additionally depends on the instrumental width.

The sodium D components tabulated by NIST lie near 589.0 and 589.6 nm [5](https://doi.org/10.18434/T4W30F). Their approximately 0.5974-nm separation is about twenty-five times smaller than the example grid interval. The 595-nm point is also 6 nm from the entered 589-nm comparison value. Species assignment uses the resolved profile, several consistent features, the instrumental response and the treatment of stellar and terrestrial contributions.

The 0.0225 local excess is the measured additional-depth contrast. Its detection significance depends on the intensity uncertainties and covariance of the paired spectra. Uncertainty in a shared dark estimate correlates wavelength ratios, and imperfect wavelength registration can leave a false differential feature where a stellar spectrum has a steep slope. These effects must enter a covariance model or repeated matched observations before interpreting a residual chemically. The present comparison establishes how normalization changes the physical question; it does not uniquely determine composition, temperature or atmospheric abundance.

## References

1. [S. Seager and D. D. Sasselov (2000), Theoretical Transmission Spectra during Extrasolar Giant Planet Transits, ApJ 537, 916–921.](https://doi.org/10.1086/309088)
2. [T. M. Brown (2001), Transmission Spectra as Diagnostics of Extrasolar Giant Planet Atmospheres, ApJ 553, 1006–1026.](https://doi.org/10.1086/320950)
3. [D. Charbonneau, T. M. Brown, R. W. Noyes and R. L. Gilliland (2002), Detection of an Extrasolar Planet Atmosphere, ApJ 568, 377–384.](https://doi.org/10.1086/338770)
4. [J. G. Robertson (2013), Quantifying Resolving Power in Astronomical Spectra, PASA 30, e048.](https://doi.org/10.1017/pasa.2013.26)
5. [A. Kramida, Yu. Ralchenko, J. Reader and NIST ASD Team (2024), NIST Atomic Spectra Database, version 5.12.](https://doi.org/10.18434/T4W30F)
