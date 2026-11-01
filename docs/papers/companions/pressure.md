# Barometric Height Changes with Bracketed Pressure References

*November 2023*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

**Abstract.** Metre-scale elevation changes produce small pressure differences that can be obscured by ambient drift. An LPS22HB example record is reduced using reference intervals before and after each event. Interpolation at the event's mean time gives pressure changes of $-0.132$ and $-0.351$ hPa, corresponding to height differences of 1.12 and 2.99 m for an isothermal air column at 293.15 K. A separate $+7.96$-hPa sealed-bag excursion demonstrates why a pressure change cannot be assigned a height without identifying its physical cause. The analysis makes the bracketed-reference estimator explicit and separates within-window scatter, calibration covariance and atmospheric-model uncertainty.

**Keywords:** Barometry, relative height, bracketed references, ambient drift, differential pressure.

## From pressure to relative height

A barometer measures absolute pressure at its vent; height follows only after specifying a reference and an atmospheric model. Raising the sensor, changing room ventilation and compressing a sealed enclosure can all move the pressure trace. The hydrostatic interpretation applies when the sensor remains in communication with a sufficiently settled air column. Smartphone altitude estimation likewise separates pressure bias from the atmospheric reference needed for absolute height [1](https://doi.org/10.1109/TIM.2023.3315391). The present question is narrower: what relative displacement is consistent with a short, locally referenced traverse?

Combining $dp/dz=-\rho g$ with $\rho=p/(R_aT)$ gives, for an isothermal column,
$$
\Delta h=\frac{R_aT}{g}\ln\frac{p_b}{p_e}, \tag{1}
$$
where $p_e$ is the event pressure and $p_b$ the pressure at the reference height at the same time. The model assumes a representative air temperature and negligible changes in composition and gravity over the displacement. For small changes, $\Delta h\simeq-(R_aT/gp_b)\Delta p$. A simultaneous pressure reference is useful, but a return to the original height before and after the event can also constrain slow drift.

The LPS22HB on the original Nano 33 BLE Sense supplies a temperature-compensated digital pressure reading. Its specified interval is 260–1260 hPa and its output scale is 4096 codes per hectopascal [2](https://www.st.com/resource/en/datasheet/lps22hb.pdf). The resulting code spacing, about 0.000244 hPa, describes digitization rather than measurement uncertainty. Typical absolute-accuracy limits and one-point calibration specifications must not be treated as the standard uncertainty of a particular traverse. A small pressure difference can remain informative when a stable offset is common to both levels.

## A traverse with a bracketed reference

The moving barometer returns to the same reference height around each elevated interval, as in Figure 1. Its vent remains open to the room, shielded from handling-induced airflow and free of obstruction. Hold the board in a repeatable orientation and allow the pressure port and powered assembly to settle after motion. A stationary second barometer would test the assumed ambient evolution, but it is not required to calculate the single-instrument estimator used here.

*Figure 1. Apparatus schematic. A single barometer is raised and returned to its reference height. Settled intervals before and after the event bracket the evolving room-pressure reference.* View paper (built locally at `output/pdf/pressure.pdf`)

Let $\overline p_-,\overline p_e,\overline p_+$ denote the means of the before, event and after intervals, and let $\overline t_-,\overline t_e,\overline t_+$ be their actual mean timestamps. Define
$$
\lambda=\frac{\overline t_e-\overline t_-}{\overline t_+-\overline t_-}, \tag{2}
$$

$$
p_b=(1-\lambda)\overline p_-+\lambda\overline p_+,\qquad
 \Delta p=\overline p_e-p_b. \tag{3}
$$
Using actual mean timestamps accommodates unequal sample counts without assuming that every observation lies exactly at the nominal cadence. The interpolation removes a linear ambient trend between references. It cannot reconstruct a curved pressure change or a ventilation disturbance that occurs only during the raised interval.

The example's device-time increments are approximately 0.05 s. Cadence alone does not establish pressure-port bandwidth or the time of the physical conversion. The event windows below exclude the movement transitions, so the reported quantities are settled interval means rather than estimates of transient peak pressure.

## Reduction of the example traverse

Figure 2 retains the full pressure range and a separate expanded view of the two elevation intervals. The lower panel uses the 0–20 s mean only as a visual reference; the numerical height estimates use their own surrounding intervals through Equation (3). A single early baseline would leave subsequent ambient evolution mixed into the inferred displacement.

*Figure 2. (a) Full pressure record, including sealed-bag compression. (b) Expanded elevation intervals relative to the 0–20 s mean. Height estimates use the local bracketing references defined in the text.* View paper (built locally at `output/pdf/pressure.pdf`)

All windows are half-open. The first elevation uses before, event and after windows $[20,28)$, $[36,42)$ and $[52,60)$ s. The second uses $[60,68)$, $[78,84)$ and $[98,106)$ s. For the bag excursion, the corresponding windows are $[110,118)$, $[124,128)$ and $[145,153)$ s. Table 1 reports the resulting differences. Heights use $T=293.15\,\mathrm{K}$, $R_a=287.05\,\mathrm{J\,kg^{-1}K^{-1}}$ and $g=9.80665\,\mathrm{m\,s^{-2}}$.

*Table 1. Pressure changes relative to interpolated local references, with isothermal height estimates for the two open-air elevation intervals.*

| Interval | Samples | Pressure difference (hPa) | Height (m) |
| --- | --- | --- | --- |
| First elevation | 119 | -0.132 | 1.12 |
| Second elevation | 120 | -0.351 | 2.99 |
| Bag compression | 79 | 7.96 | — |

For the first elevation, the interpolated reference is 1009.8119 hPa and the event mean is 1009.6803 hPa. The second gives 1009.7764 and 1009.4250 hPa. These changes have the sign expected for increased height. Their within-event standard deviations are 0.019 and 0.021 hPa, respectively. Those dispersions describe pressure variability within each selected interval, including any drift. The height-uncertainty model combines interval statistics with reference, calibration and atmospheric-model contributions.

The positive bag excursion answers a different causal question. Its reference and event means are 1009.7100 and 1017.6744 hPa. Applying a hydrostatic height conversion to this sealed volume would describe a fictitious descent.

## Calibration and uncertainty of the difference

Calibration against a reference should span the working pressures and include return points after changes in pressure or board temperature. Both instruments must share equilibrated gas pressure; flow or a port-height difference introduces a physical mismatch. A first response model may include offset, gain and board-temperature dependence, but a monotonic pressure sweep during warm-up cannot identify those terms separately.

For fixed interpolation weights, write $\mathbf p=(\overline p_-,\overline p_e,\overline p_+)^{\mathsf T}$ and $\mathbf w=(-(1-\lambda),1,-\lambda)^{\mathsf T}$. The pressure-difference variance is
$$
u^2(\Delta p)=\mathbf w^{\mathsf T}\boldsymbol\Sigma\mathbf w, \tag{4}
$$
where $\boldsymbol\Sigma$ contains the covariance of the three interval means [3](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf). Shared offset uncertainty can cancel from the difference; time-varying calibration and common ambient disturbances require their actual covariance. Timing uncertainty and departures from linear ambient drift add separate contributions. Correlated samples cannot be treated as independent simply because a window contains many observations.

The height model additionally depends on the absolute pressure ratio and representative temperature. A common multiplicative scale cancels from the ratio, whereas a common additive offset cancels exactly from $\Delta p$ but only approximately from the logarithmic height conversion. Near 1010 hPa and 293 K, the local sensitivity is about 8.5 m/hPa. The metre-scale results are therefore sensitive to small baseline errors even when digitization is fine. A measured temperature profile and humidity correction would refine the atmospheric model; an unobstructed vent and repeated returns to the reference height test whether that refinement is warranted by the pressure observations themselves.

## References

1. [Y. Li, W. Chen, J. Wang and X. Nie (2023), Precise Indoor and Outdoor Altitude Estimation Based on Smartphone, IEEE Transactions on Instrumentation and Measurement 72, 9513111.](https://doi.org/10.1109/TIM.2023.3315391)
2. [STMicroelectronics (2017), LPS22HB: MEMS Nano Pressure Sensor, DocID027083, revision 6.](https://www.st.com/resource/en/datasheet/lps22hb.pdf)
3. [JCGM (2008), Evaluation of Measurement Data—Guide to the Expression of Uncertainty in Measurement, JCGM 100:2008.](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf)
