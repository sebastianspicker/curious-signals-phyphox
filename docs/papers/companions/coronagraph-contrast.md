# Occulting Masks: Background Suppression and Target Detectability

*April 2022*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

**Abstract.** An occulting mask can reduce background glare while also attenuating a nearby target. The data comprise twenty-four fixed-exposure observations at six image separations, with two observations for each mask state. Across separations, the mask retains on average 36.1% of the local background and 36.4% of the background-subtracted target signal. Local relative contrast consequently changes little, while the mean individual noise-normalized signal falls to 78.8% of its unmasked value. Thus background suppression alone does not establish improved detectability. The analysis distinguishes local contrast, target throughput and statistical evidence, connecting a simple lamp-and-pinhead model to the measurement requirements of high-contrast imaging.

**Keywords:** Coronagraphy, occulting masks, image contrast, target throughput, detection statistics.

## Suppressing a bright source

An artificial eclipse makes a faint structure near a bright source easier to inspect only if the suppression mechanism preserves enough of the desired signal. Lyot's coronagraph addressed this problem through control of the optical path and unwanted light [1](https://doi.org/10.1093/mnras/99.8.580). A cardboard disk placed in front of a lamp provides a much simpler analogy: the visible glare can decrease, while diffraction, lens flare, pupil geometry and the target's own illumination each contribute to the image. The useful question is therefore quantitative: how much target signal survives relative to the relevant noise?

Figure 1 represents a lamp as the bright star and a nearby illuminated pinhead as the target. A camera observes both at fixed geometry. Removing and replacing a disk permits paired comparisons at a chosen image separation. The disk can obstruct light reaching the target, block target rays on their way to the camera, or alter scattering inside the lens. These mechanisms have different physical meanings, although each can change the final image.

*Figure 1. Apparatus schematic. A removable disk suppresses the lamp image while a nearby target is observed without changing camera settings. Target and background regions are evaluated separately.* View paper (built locally at `output/pdf/coronagraph-contrast.pdf`)

The camera response must remain linear over both regions, with exposure duration, gain, focus, colour channel and processing held fixed. The EMVA 1288 linear model separates photon response, system gain and noise contributions [2](https://www.emva.org/wp-content/uploads/EMVA1288Linear_4.0Release.pdf); the camera processing transfer is part of the photometric calibration. Clipped pixels, local tone mapping or automatic exposure can imitate an improvement after masking. Checking only a region's mean against the digital ceiling cannot reveal a saturated core hidden within that region.

## Signal, background and uncertainty

The paired observations use means from documented target and nearby background regions of interest. Let those means be $M$ and $B$ at exposure duration $t$. Define
$$
 N=M-B,\qquad C=\frac{N}{B},\qquad Q=\frac{N}{u_N}, \tag{1}
$$
where $u_N$ is the standard uncertainty of the difference of means. The local contrast $C$ is dimensionless, but it is neither a planet-to-star flux ratio nor a coronagraph suppression specification. The statistic $Q$ expresses signal relative to the particular uncertainty supplied. Its physical interpretation depends on how that uncertainty was established.

Image analysis supplies the ROI means. Equal documented areas and consistent masking of defective pixels are needed before comparing regions. Writing the standard uncertainties of the two ROI means as $u_M$ and $u_B$,
$$
 u_N^2=u_M^2+u_B^2
       -2\operatorname{cov}(\overline M,\overline B). \tag{2}
$$
For independent pixels within a region, $u_M^2=s_M^2/n_M$ and $u_B^2=s_B^2/n_B$. Spatial correlations require the corresponding pixel covariances or a justified block estimate instead. The covariance between ROI means vanishes if their errors are independent. Shared illumination drift, resampling and structured glare can violate that assumption. The standard deviation of background pixels alone is not $u_N$.

The example contains two observations for each mask state at image separations of 30, 60, 90, 120, 150 and 180 pixels. Exposure is 10 ms throughout, and all checked ROI means lie below the entered ceiling of 255 arbitrary units. Separations remain image coordinates: conversion to an angle would require a separate plate-scale calibration. The net rate $1000N/t$, with $t$ in milliseconds, is available, but equal exposures mean that this normalization cannot change the masked/unmasked ratios.

*Figure 2. Upper: local contrast from the mean net signal and mean background of two observations per state. Lower: mean individual $Q=N/u_N$. Masking lowers mean $Q$ at all six separations despite similar local contrasts.* View paper (built locally at `output/pdf/coronagraph-contrast.pdf`)

## Background reduction without a detection gain

For each separation, take the arithmetic mean of the two net signals and the two backgrounds. Their ratio defines the plotted local contrast. The mean of the two individual $Q$ values is reported separately. This choice avoids conflating the appearance of an averaged image with the statistical significance of a combined exposure. Table 1 gives representative separations.

*Table 1. Local contrast from grouped means and mean individual $Q=N/u_N$ at three separations. Subscripts 0 and 1 denote the unmasked and masked states, respectively.*

| Separation (pixel) | C unmasked | C masked | Mean Q unmasked | Mean Q masked |
| --- | --- | --- | --- | --- |
| 30 | 3.001 | 2.834 | 25.14 | 19.26 |
| 90 | 1.873 | 1.952 | 17.42 | 13.82 |
| 180 | 1.682 | 1.691 | 15.82 | 12.25 |

At 30 pixels, masking lowers the mean local background from 50.40 to 18.38 units. Yet the mean net target signal falls from 151.27 to 52.10 units. Background retention is 0.365 and net-signal retention 0.344, leaving slightly poorer local contrast. At 90 pixels, contrast increases from 1.873 to 1.952, but $\overline Q$ decreases from 17.42 to 13.82. This explicitly separates a favourable contrast ratio from improved noise-normalized detectability.

Averaging the six separation-specific retention ratios gives 0.361 for background, 0.364 for net signal and 0.788 for $\overline Q$. All six masked $\overline Q$ values are lower. The mask therefore removes nearly the same fraction of desired net signal as local background. The background and net-signal retention ratios make this throughput tradeoff explicit. Interpreting these retention ratios as optical throughputs additionally depends on separating target light from structured source light in the ROI.

At 30 pixels, combining the two entered $u_N$ values in quadrature would give conditional mean-signal uncertainties of 4.25 units unmasked and 1.91 units masked. Those numbers assume independent errors between observations. They do not establish the uncertainty of $C$, which also requires the background variance and its covariance with $N$. Two observations per state cannot independently characterize a non-Gaussian background tail or a stable systematic bias.

## What a useful mask must demonstrate

In astronomical coronagraphy, residual stellar speckles can be correlated and partly static; increasing exposure does not necessarily average them down like independent photon noise [3](https://doi.org/10.1086/520913). A lamp model need not reproduce that exact noise process, but it should retain the distinction between mean glare and fluctuating or structured background. An isolated-target comparison, acquired with the bright source blocked independently, would help estimate how much genuine target light the mask preserves.

Detection thresholds require a defined null distribution and a count of independent resolution elements. Mawet et al. show the importance of small-sample statistics near the inner working angle [4](https://doi.org/10.1088/0004-637X/792/2/97). A false-alarm interpretation of the reported $Q$ values depends on that null distribution and the stated uncertainty model. They are descriptive ratios based on entered uncertainties. The measurements show that the present mask lowers background substantially, but comparable loss of net target signal prevents a gain in the reported detectability statistic. A stronger design must demonstrate selective suppression together with preserved target throughput, rather than a darker image alone.

## References

1. [B. Lyot (1939), The Study of the Solar Corona and Prominences without Eclipses, MNRAS 99, 580–594.](https://doi.org/10.1093/mnras/99.8.580)
2. [European Machine Vision Association (2021), EMVA Standard 1288, Release 4.0 Linear.](https://www.emva.org/wp-content/uploads/EMVA1288Linear_4.0Release.pdf)
3. [R. Soummer, A. Ferrari, C. Aime and L. Jolissaint (2007), Speckle Noise and Dynamic Range in Coronagraphic Images, ApJ 669, 642–656.](https://doi.org/10.1086/520913)
4. [D. Mawet et al. (2014), Fundamental Limitations of High Contrast Imaging Set by Small Sample Statistics, ApJ 792, 97.](https://doi.org/10.1088/0004-637X/792/2/97)
