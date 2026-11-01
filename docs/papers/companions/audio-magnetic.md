# Motor-State Comparisons from Sound Envelopes and Magnetic Fields

*February 2019*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

**Abstract.** 
Sound and stray magnetic field provide different views of a motor's operating state. Their slow changes can be compared without assuming a common spectral response or precise sample synchronization. In the data, three on-minus-off comparisons give an energy-based relative audio-level change of 11.56 dB and a mean magnetic-magnitude change of $4.03\,\mathrm{\mu T}$. The calculation retains separate time axes, weights audio blocks by their actual sample counts, and distinguishes a vector-field change from a change in its norm. Signal amplitude, relative channel timing and the block-averaging intervals determine the timescale of these comparisons.

**Keywords:** Audio RMS, stray magnetic field, motor state, relative level, asynchronous sampling.

## Two observables of one operating state

An energized motor can change both its acoustic environment and the magnetic field outside its enclosure. Those changes have different physical pathways. Sound depends on mechanical vibration, airflow, mounting and radiation into the room; the external magnetic field contains contributions from windings, magnetic material and supply leads. Fixed placement is consequently part of the measurement definition. Moving a lead or a reflecting surface may change one observable while leaving the other nearly unchanged.

Liu *et al.* demonstrate operating-load information in the stray field of an induction machine using dedicated magnetic sensors [1]. That result motivates the observable, while its machine-specific load calibration remains separate. Here the inference is a contrast between settled on/off states, rather than a diagnosis of the motor's internal dynamics.

Figure 1 gives the arrangement: an enclosed low-voltage DC motor, a fixed phone and stationary leads. The supply and switch should be far enough from the phone that operating them does not move nearby metal or dominate the field. A switch-only control and an alternative motor distance help distinguish a motor-associated change from operator motion and lead fields. The phone remains electrically separate from the circuit.

**Figure 1.** Motor-state comparison with fixed phone, motor and return lead. Slow switching changes the acoustic and magnetic observables while preserving the sensing geometry. View figure (built locally at `output/pdf/audio-magnetic.pdf`).

A rigid rotation preserves the norm of a uniform field, but sensor offsets and unequal axis responses can make the indicated norm orientation dependent [2]. Keeping the phone fixed suppresses that ambiguity. Retaining all three components then permits a directional comparison of the operating-state change.

## Energy reduction and separate clocks

For audio block $j$ with $N_j$ samples $x_{jk}$, define
$$
r_j^2=\frac{1}{N_j}\sum_{k=1}^{N_j}x_{jk}^2,
 \qquad L_j=20\log_{10}\frac{r_j}{r_{\rm ref}}.
\tag{1}
$$
The values are digital relative amplitudes, with $r_{\rm ref}=0.020$ and an assigned reference level of 0 dB. They are not pressures referenced to $20\,\mathrm{\mu Pa}$. Specified frequency weighting and the performance of the complete instrument are central to IEC sound-level metrology [3]. Kardous and Shaw's microphone-calibration study illustrates why the acquisition path must be characterized before device-specific acoustic accuracy can be asserted [4].

Every example block contains 4800 samples at $48000\,\mathrm{s^{-1}}$, corresponding to 0.100 s. The actual sample count and recorded rate define the averaging interval; a nominal requested rate need not be realized on every platform [5]. For a collection of blocks, the energy-consistent reduction is
$$
r_{\rm agg}^2=\frac{\sum_j N_j r_j^2}{\sum_j N_j},
 \qquad L_{\rm agg}=10\log_{10}\frac{r_{\rm agg}^2}{r_{\rm ref}^2}.
\tag{2}
$$
This is a sample-weighted mean square. With a constant rate it is also time weighted; varying rates would require duration weights for a time average. An arithmetic mean of block decibels describes a different statistic because the logarithm is nonlinear.

The audio timestamps refer to block processing on the experiment-session clock; magnetic readings carry their own sensor times. The 601 audio blocks and 1201 magnetic samples are not paired by row. Each stream is selected independently over 1--9, 11--19, 21--29, 31--39, 41--49 and 51--59 s, using left-closed, right-open intervals. Each window contains 80 audio blocks and 159 magnetic readings. For channel latencies shorter than the one-second margin at switching boundaries, the selected windows compare settled motor states.

## State contrasts in the data

Figure 2 shows the shared slow switching pattern. The first off/on windows have aggregate RMS amplitudes 0.01190 and 0.04506, respectively, corresponding to $-4.510$ and $7.056$ dB relative to the chosen reference. Their difference is 11.566 dB. Averaging the off-state block levels instead gives $-4.640$ dB, a 0.129-dB difference from the energy-based value; the choice of averaging convention is already visible in this short record.

**Figure 2.** (a) Audio-block RMS and (b) magnetic-field magnitude through three motor switching cycles. Each stream retains its recorded session timestamps. View figure (built locally at `output/pdf/audio-magnetic.pdf`).

With angle brackets denoting the sample mean within each state, the magnetic contrasts are
$$
\begin{aligned}
 \Delta B_{\rm norm}&=\langle|\bm B|\rangle_{\rm on}-\langle|\bm B|\rangle_{\rm off},\\
 \Delta B_{\rm vec}&=\big|\langle\bm B\rangle_{\rm on}-\langle\bm B\rangle_{\rm off}\big|.
 \end{aligned}
\tag{3}
$$

**Table 1.** Cyclewise on-minus-off contrasts: audio level, mean field magnitude and magnitude of the mean field-vector difference.

| Cycle | $\Delta L$ (dB) | $\Delta B_{\rm norm}$ ($\,\mathrm{\mu T}$) | $\Delta B_{\rm vec}$ ($\,\mathrm{\mu T}$) |
| --- | --- | --- | --- |
| 1 | 11.566 | 4.040 | 4.222 |
| 2 | 11.520 | 4.056 | 4.240 |
| 3 | 11.582 | 3.983 | 4.177 |

Across the three cycle contrasts in Table 1, the mean audio change is 11.556 dB with cycle sample standard deviation 0.032 dB. The corresponding magnetic-norm change is $4.026\,\mathrm{\mu T}$ with cycle scatter $0.039\,\mathrm{\mu T}$. These are spreads among three state comparisons. Adjacent readings share a motor state and acquisition conditions, so their much larger count cannot be treated as an equal number of independent repetitions.

For the first cycle, the component difference is approximately $(2.009,-1.183,3.519)\,\mathrm{\mu T}$, whose norm is $4.222\,\mathrm{\mu T}$. It differs from the $4.040\,\mathrm{\mu T}$ change in total magnitude because the motor-associated vector adds to a nonzero background.

The two estimators generally differ. A norm contrast can be small even for a detectable component change if that change is largely perpendicular to the background.

## Noise floor and identifiable information

Using a background RMS reference $r_n=0.010$, the independent-noise model gives $r_s=\sqrt{r^2-r_n^2}$ only when $r>r_n$. Forty of the 601 blocks are at or below this reference. Their zero-valued corrected amplitudes are therefore interpreted as unresolved positive amplitudes, not exact silence. The guarded inverse leaves them censored. For the first off plateau, subtracting noise after energy aggregation gives 0.00645, far smaller than the uncorrected 0.01190 and correspondingly sensitive to the chosen noise reference.

That subtraction presumes stable, uncorrelated background and unchanged gain. Automatic gain changes or structure-borne vibration can violate those assumptions. Near the floor, uncertainty in the background dominates the recovered amplitude; the result cannot establish acoustic power. The block envelopes also omit the waveform information needed for a new acoustic spectrum.

The common switching pattern associates both observables with operating state. Comparisons of phase, propagation delay and transfer response depend on relative channel timing and waveform-resolved signals.

## References

1. [Liu et al. (2017), Non-invasive load monitoring of induction motor drives using magnetic flux sensors, IET Power Electronics 10, 189–195](https://doi.org/10.1049/iet-pel.2016.0304).
2. [Kok and Schön (2016), Magnetometer calibration using inertial sensors, IEEE Sensors Journal 16, 5679–5689](https://doi.org/10.1109/JSEN.2016.2569160).
3. [IEC (2013), IEC 61672-1: Electroacoustics—Sound level meters—Part 1: Specifications](https://webstore.iec.ch/en/publication/5708).
4. [Kardous and Shaw (2016), Evaluation of smartphone sound measurement applications using external microphones—A follow-up study, J. Acoust. Soc. Am. 140, EL327–EL333](https://doi.org/10.1121/1.4964639).
5. [phyphox Development Team, Input reference (accessed October 2026)](https://phyphox.org/docs/file-format/input/).
