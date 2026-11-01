# Laboratory Transit Photometry: Calibration, Temporal Resolution and Visible-Area Models

*September 2024*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

A laboratory transit is an inverse problem involving visible area, surface brightness and detector response. A common measurement model connects phone, SensorTag, photocell–multimeter and Nano examples to tests of temporal resolution and to more complex occultations. Local deficits in three independent acquisition examples are 3.95, 3.99 and 4.00%; a shallow Nano sequence gives 4.26%, whereas a whole-record extrema estimator gives 19.30%. A separate sampling example shows why a nominally adequate cadence can still miss a short feature: six of sixteen coarse sampling phases contain no reading in a half-second decrement. Planet–moon overlap and the occultation of a dark source patch both produce upward anomalies, but through different changes in the brightness integral. Their example contrasts are 1.48 and 2.92 percentage points, respectively. A sequence with two luminous bodies adds unequal eclipse depths of 31.05 and 10.49% and a 29.995-s recurrence estimate. These quantities support different physical inferences; none permits a universal conversion from a light-curve minimum to an object radius.

## The inverse problem shared by the experiments

An opaque object moving across a lamp makes the transit method accessible without astronomical distances or faint targets. The visible dip is nevertheless only the first observable. Its depth, duration and recurrence depend on different parts of the apparatus, and a change in any one of them need not imply a change in the object's radius. The useful laboratory question is therefore which properties of the optical configuration remain identifiable from the recorded signal.

Video-aided light-curve analysis [1] provides an independent view of the source, occulter and supports. It can establish whether the smaller silhouette is completely inside the luminous disc, whether its projected area remains approximately constant during a selected plateau, and whether a motor housing contributes to the shadow. These observations constrain an interpretation that the integrated light curve alone cannot determine. The same strategy extends to a moon carried around the model planet [2], a dark patch attached to the emitting surface, or a second luminous body.

We develop these configurations within a single brightness model. Independent detector examples first establish the distinction between a local signal deficit and a physical flux ratio. A separate optical sequence then examines the amplitude and time coverage of short features. Finally, two kinds of upward anomaly and alternating binary minima test what changes when the source is nonuniform or the companion emits light. The records have their own baselines, clocks and geometries. Similar numerical depths across them do not constitute a detector accuracy comparison, and superposing traces does not synchronize the physical events.

**Figure 1.** Common apparatus and configuration insets. The detector integrates the visible, projected brightness. Distances are measured from the detector, and supports remain outside the source silhouette. Moon overlap changes the union of dark areas; a source patch changes the brightness being blocked; a luminous companion changes both the obscured contribution and the unobscured denominator. Article figure (built locally at `output/pdf/transit-method.pdf`).

## Visible brightness, projection and detector response

### A common forward model

Let $J_j(\lambda,\bm{x},t)$ denote the image-plane brightness of luminous body $j$, and let $\Omega_j^{\rm vis}(t)$ be its visible projected region after occultation. A detector with fixed spectral weighting $w(\lambda)$ receives a contribution proportional to

$$
\mathcal{L}(t)=\int w(\lambda)\sum_j\int_{\Omega_j^{\rm vis}(t)}
J_j(\lambda,\bm{x},t)\,d^2x\,d\lambda. \tag{1}
$$

The projection includes the source–detector geometry. For an opaque dark planet, only the luminous source enters the sum, while its visible domain excludes the planetary silhouette. For two emitting bodies, each contributes its own brightness over whichever part remains visible. A dark surface patch modifies $J$ itself rather than adding a second foreground body.

Within a linear operating range, a useful measurement model is

$$
X_i=D+g\int h_i(t_i-\tau)\mathcal{L}(\tau)\,d\tau+\epsilon_i,
\qquad \int h_i(u)\,du=1. \tag{2}
$$

Here $D$ is the additive background in signal units, $g$ is a constant response factor, $h_i$ is the temporal response kernel, and $\epsilon_i$ represents residual fluctuations. A source-blocked observation must reproduce the relevant ambient illumination and detector state if it is to estimate $D$. A covered-sensor offset and the room background are not automatically the same quantity.

The response kernel precedes notification and display. It can include optical integration and other averaging. Notification timestamps specify when readings are reported; they do not measure that kernel. Finite integration rounds a sharp ingress and can bias parameters retrieved with an instantaneous transit model [3]. Subsequent averaging adds another kernel. Conversely, discarding samples changes time coverage without reproducing a slower detector's integration or filtering.

### The area-ratio special case

For a uniform source and a smaller opaque silhouette fully inside its disc, the brightness integral reduces to an area ratio. With small angular sizes and physical radii and distances defined in Figure 1,

$$
\delta=\left(\frac{R_p d_s}{R_s d_p}\right)^2,
\qquad R_p=R_s\frac{d_p}{d_s}\sqrt{\delta}. \tag{3}
$$

The quantity $\sqrt{\delta}$ is directly an angular or projected radius ratio, not generally $R_p/R_s$. A physical radius requires measured $R_s$, $d_s$ and $d_p$. A grazing trajectory, transparency or a brightness gradient changes the inverse problem before any statistical uncertainty is considered.

Stellar transit models account for limb darkening [4]; the same reasoning requires a laboratory source to have a measured or otherwise justified brightness distribution. The clear, red, green and blue channels of the APDS-9960 are also spectrally weighted detector outputs with programmable gain and integration [5]. They do not directly supply a bolometric intensity map or a resolved spectrum. A stable source spectrum and fixed detector acceptance are conditions of the simple relative-photometry model. Check for clipping and verify response proportionality over the interval spanning baseline and plateau; a nonclipped trace alone does not establish linearity.

The alternative acquisition paths impose related conditions. A phone ambient-light response depends on its sensor and processing; the SensorTag supplies another ambient-light observable. A photocell attached to a multimeter supplies voltage. Before a normalized voltage is treated as a flux ratio, its transfer must be established at the actual load, temperature and light level. Reference-cell work at low irradiance [6] illustrates why electrical operating conditions belong in an optical calibration rather than being absorbed into a dimensionless ratio.

## Local baselines across four acquisition examples

### One estimator, explicit background conventions

Let $B$ be an unobscured local mean and $P$ the corresponding plateau mean. Under the conditions of Eq. (2), the background-subtracted deficit is

$$
\widehat\delta=\frac{B-P}{B-D},\qquad B>D. \tag{4}
$$

A normalization is useful only insofar as its reference represents the intended physical state. Ignoring a positive background dilutes the inferred source deficit: if $D$ is the true additive contribution, then $(B-P)/B=\delta(B-D)/B$. An incorrect baseline can instead move the entire normalized unobscured trace away from unity. Neither effect is repaired by collecting more samples of the same biased reference.

Three acquisition examples contain events near their own record times $c=22$, 52 and $82\,\mathrm{s}$. For each event, $B$ is the mean over samples satisfying $3\leq|t-c|<6\,\mathrm{s}$ and $P$ is the mean over samples with $|t-c|\leq1\,\mathrm{s}$. The reported observable for this reduction is the unsubtracted signal deficit $1-P/B$. The arithmetic mean of the three event deficits is 3.948% for the SensorTag, 3.993% for the phone and 3.997% for the photocell–multimeter. For the photocell–multimeter, conversion of the voltage deficit to an optical flux deficit depends on the load-specific transfer.

**Figure 2.** Upper: first events from the independent SensorTag, phone and photocell–multimeter records, each normalized by its local baseline. The photocell trace is a voltage ratio. Lower: raw clear counts and one-second means for the separate shallow Nano sequence. Article figure (built locally at `output/pdf/transit-method.pdf`).

**Table 1.** Transit signal deficits, cadence, threshold spans and recurrence from four independent acquisition paths. Tag, phone and cell use unsubtracted signal ratios; Nano uses a 10-count background and receive-clock spacing. Dashes identify unassigned timing.

| Quantity | Tag | Phone | Cell | Nano |
| --- | --- | --- | --- | --- |
| Median spacing (s) | 0.800 | 0.09985 | 0.500 | 0.05043 |
| Local deficit (%) | 3.948 | 3.993 | 3.997 | 4.260 |
| Extrema deficit (%) | 5.267 | 5.223 | 4.357 | 19.298 |
| Mean interval (s) | 30.000 | 30.009 | 30.000 | — |
| Mean span (s) | 2.933 | 3.198 | 3.500 | — |

### A shallow Nano sequence tests reference choice

The Nano events occur around device times $c=20$, 50 and $80\,\mathrm{s}$. Their primary reduction uses baseline windows $[c-6,c-3)$ and $[c+3,c+6)$, with plateau windows $[c-1,c+1)\,\mathrm{s}$. Device time selects samples associated with the signal; the separate receive time is retained for plotting. The adopted background is 10 counts. This reduction treats the dark offset as an adopted parameter.

The three local baseline means are 115.14, 115.28 and 115.25 counts, whereas the plateau means are 111.33, 110.23 and 110.68 counts. Their deficits are 3.63, 4.80 and 4.35%, giving a mean of 4.26% and an event-to-event standard deviation of 0.59 percentage points. That standard deviation describes the repeatability of three window reductions. It is not a confidence interval obtained from the total number of recorded readings.

The mean local baseline, 115.22 counts, also exposes the difference between a measured state and an entered normalization. The adopted reference of 110 counts gives an unobscured normalized level of 1.0522 under the same 10-count subtraction. This normalization places the measured unobscured level above unity. Re-estimating the local baseline addresses that particular discrepancy while leaving the adopted background and detector linearity as separate assumptions.

A whole-record extrema estimator, $(X_{\max}-X_{\min})/(X_{\max}-D)$, gives 19.30% for the Nano sequence. Its baseline sample scatter is 2.72–2.81 counts, compared with local mean deficits of only 3.82–5.05 counts. Selecting the highest and lowest samples from a long record accentuates those fluctuations and does not compare equivalent optical states. The smaller extrema excesses in the three other examples have the same statistical vulnerability. Their different magnitudes cannot be used to rank detector accuracy because the examples have independent signal levels, noise and timing.

Within the uniform-source model, the Nano mean deficit corresponds to $\sqrt{\delta}=0.2064$. Conversion to a physical planet radius additionally depends on the geometry in Eq. (3). Even the projected ratio inherits the uncertainty and model dependence of the adopted background. The estimator, adopted background and physical geometry jointly determine the radius interpretation.

### Uncertainty belongs to the shared reference

For Eq. (4), the sensitivity vector with respect to $(B,P,D)$ is

$$
\begin{aligned}
\bm{a}&=\left(\frac{P-D}{(B-D)^2},\ -\frac{1}{B-D},
\frac{B-P}{(B-D)^2}\right),
\\
 u^2(\delta)&=\bm{a}\,\bm{\Sigma}\,\bm{a}^{\mathsf T},
\end{aligned} \tag{5}
$$

where $\bm{\Sigma}$ contains their variances and covariances. A common baseline or background couples all normalized points. Photometric covariance can therefore dominate an apparent improvement obtained by increasing the point count [7]. The relevant averaging behaviour must be examined over the duration of the event or anomaly, not inferred solely from adjacent-sample scatter.

If a physical radius is justified, the logarithmic sensitivity is $d\ln R_p=d\ln R_s+d\ln(d_p/d_s)+\tfrac12d\ln\delta$. Independent contributions can be combined in quadrature only when their independence is defensible; otherwise the geometry and depth covariances remain. A changing source brightness map is a model error, not an additional independent count fluctuation. A known second silhouette, a separately measured background and a load-specific optical transfer each constrain a different part of this inference.

## Temporal resolution: cadence, integration and noise

### A delivered sequence has two clocks

The shallow Nano sequence has median device and receive intervals of 0.05000 and $0.05043\,\mathrm{s}$. Those numbers describe that sequence, not an optical bandwidth. A separate detector-characterization example makes the clock distinction more visible. Adjacent differences of its device timestamps have mean $50.340\,\mathrm{ms}$ and sample standard deviation $0.474\,\mathrm{ms}$. Receive intervals have a similar mean, $50.344\,\mathrm{ms}$, but a $4.245\,\mathrm{ms}$ standard deviation. The receive-interval scatter is about nine times larger even though the mean rates agree closely.

The reciprocal mean device interval is $19.8649\,\mathrm{Hz}$. Association of each device reading with its notification permits the two spacing series to be compared against the device time of the later sample, as in Figure 3. It does not synchronize the clocks or establish an absolute latency. A missed notification should remain a gap in elapsed receive time. Replacing measured times with sample number times a nominal period would obscure that distinction.

**Figure 3.** Upper: short decrements on device time. Lower: device and receive intervals plotted at the later device timestamp. Receive-interval scatter is about nine times larger, while mean intervals agree closely. Article figure (built locally at `output/pdf/transit-method.pdf`).

An integration kernel changes the continuous shape before these spacings are considered. Ingress and egress become rounded; the apparent interval between crossings depends on the kernel as well as the chosen threshold. The finite-exposure analysis of Kipping [3] supplies the astronomical counterpart. In the laboratory, reducing the model's speed while holding detector settings fixed tests whether the recovered shape or depth is limited by temporal response. A high notification rate alone cannot establish that test's outcome.

### The amplitude budget is not a detection probability

In the characterization example, the illuminated device-time interval $12\leq t\leq28\,\mathrm{s}$ contains 318 readings with mean $\mu=1022.736$ counts and sample standard deviation $s=10.636$ counts. The dark interval $0\leq t<9\,\mathrm{s}$ has mean 11.156 counts. The accompanying numerical summary reproduces the directly calculated interval and baseline quantities to its rounding precision, including the baseline count.

For a proposed fractional decrement $\delta$, a planning amplitude ratio is

$$
\rho_1=\frac{\delta(\mu-D)}{s}. \tag{6}
$$

The summary's 2% proposal uses an entered dark value of 8 counts, giving a 20.295-count decrement and $\rho_1=1.908$. That entered value is distinct from the observed dark mean. The event reductions below instead use the latter in the denominator. The planning and event reductions therefore use different stated background conventions.

The baseline's lag-one correlation is 0.055, and the standard deviation of sixteen one-second block means is 2.64 counts. These are diagnostics over one finite interval. They do not establish stationarity at longer times or a universal square-root law for uncertainty. In particular, $\rho_1$ is not a false-alarm probability, a fitted event significance or an uncertainty of a mean. Lamp flicker and mechanical repetition can create covariance on timescales quite different from one sample [7].

**Table 2.** Feature depths and single-reading amplitude ratios in half-open device-time windows. Coarse $N$ gives the sample-count range across all sixteen phases of retaining every sixteenth reading.

| Window (s) | $N$ | Depth (%) | $\rho_1$ | Coarse $N$ |
| --- | --- | --- | --- | --- |
| $[30,30.5)$ | 10 | 0.61 | 0.58 | 0–1 |
| $[34,35)$ | 20 | 2.29 | 2.18 | 1–2 |
| $[38,40)$ | 40 | 3.98 | 3.78 | 2–3 |
| $[44,48)$ | 79 | 7.86 | 7.47 | 4–5 |

### Sampling phase can remove a feature entirely

The first feature contains ten readings in its half-second window, yet its mean deficit is only 0.61% of the background-subtracted illuminated level. The progressively longer features have mean deficits of 2.29, 3.98 and 7.86% (Table 2). These are measured means over the stated feature windows. The shallow first feature is difficult to distinguish from the baseline scatter even before time coverage is reduced.

Retaining every sixteenth sample gives a spacing near $0.805\,\mathrm{s}$. Counting retained readings in each unchanged feature window for all sixteen possible starting phases shows that six phases miss the half-second feature completely; the remaining ten contain one reading each. The one-second feature retains one or two readings, while the four-second feature retains four or five. These counts use the actual time boundaries, not a duration divided by a rounded mean rate.

Decimation does not reproduce a slower instrument. Its integration, anti-alias filtering, sensitivity and noise may all differ. The calculation isolates temporal coverage: a large decrement would still be absent from a phase that contains no sample. Averaging groups would ask a different question by spreading a short decrement across a longer response window. Thus amplitude, time coverage and integration need separate checks. A nominal rate chosen relative to the planet's slow orbital repetition can be adequate for recurrence while failing to resolve a much shorter moon or spot feature.

## Threshold spans and recurrence are different observables

The original three-path examples illustrate this distinction without fitting an orbital model. For each event, consider readings with $|t-c|<3\,\mathrm{s}$ and a threshold of $0.98B_k$, using that event's local baseline. The onset is the first below-threshold sample in this window. The end is the first recovered sample after the last below-threshold sample in the window. This windowed span includes any intervening recrossings and uses no interpolation. It should not be identified with geometric first-to-fourth contact or with a differently configured live hysteresis rule.

The resulting mean spans are 2.933, 3.198 and $3.500\,\mathrm{s}$ for SensorTag, phone and photocell–multimeter, respectively. Their mean onset intervals are nevertheless 30.000, 30.009 and $30.000\,\mathrm{s}$. The SensorTag's individual intervals are 30.4 and $29.6\,\mathrm{s}$ on its 0.8-s example grid, while the phone gives 30.073 and $29.945\,\mathrm{s}$. Similar mean recurrence therefore coexists with visibly different threshold spans and interval quantization. These differences do not establish which detector is more accurate in a common experiment.

Three events give two adjacent intervals, whose mean is

$$
\overline T=\frac{(t_1-t_0)+(t_2-t_1)}{2}
=\frac{t_2-t_0}{2}. \tag{7}
$$

The middle onset cancels. Shared endpoints correlate the adjacent intervals, so their apparent scatter cannot be treated as independent replicated timing errors. Delivery latency, finite integration and threshold choice can shift onsets relative to the physical event even when the recorded timestamps are retained correctly. Conversely, a fitted transit centre and a threshold onset need not have the same uncertainty or physical interpretation.

The shallow Nano deficit is only modestly larger than its per-sample scatter, so a first isolated threshold crossing there can be a fluctuation. We therefore retain its primary window-mean depth and do not assign a new threshold period from the densely sampled sequence. The stronger binary minima below permit a separate localized onset estimate. This choice reflects the observable supported by each example, rather than applying one event detector indiscriminately.

## Two upward anomalies, two physical mechanisms

### Mutual overlap recovers duplicated blocked area

For a planet and moon fully projected onto a uniform source, let $A_p$, $A_m$ and $A_{pm}$ denote planet, moon and mutual-overlap areas in the same projection. Equation (1) becomes

$$
F=1-\frac{A_p+A_m-A_{pm}}{A_s}. \tag{8}
$$

Increasing $A_{pm}$ removes duplicated blocking from the sum and therefore increases the received light. Mutual-transit models [8] show this geometrical brightening; the classroom moon experiment [2] makes the projected configurations visible. It is not emission by the dark companions.

Use four characteristic means: baseline $B$, planet-only $P_0$, separated silhouettes $S$ and overlap $O$. With a common background $D$, define

$$
E=\frac{P_0-S}{B-D},\qquad
C_m=\frac{O-S}{B-D},\qquad
q=\frac{O-S}{P_0-S}. \tag{9}
$$

$E$ is the resolved extra deficit and $C_m$ the overlap brightening. Under matched geometry and brightness, $q$ is the recovered fraction of the extra blocked area. Its cancellation of the common denominator removes that particular normalization sensitivity, not the need for matching silhouettes.

The primary moon reduction uses device-time windows $[3,17)$ and $[93,107)\,\mathrm{s}$ for baseline; $[22,33)$ and $[77,88)$ for planet only; $[37,48)$ and $[62,73)$ for separated silhouettes; and $[52,58)$ for overlap. Their mean clear counts are 115.33, 104.99, 102.02 and 103.58, respectively. With the adopted $D=10$ counts, the extra deficit is 2.82 percentage points and the overlap brightening is 1.48 points. The recovered fraction is $q=0.525$: only about half of the extra deficit is reversed, and the overlap level remains below the planet-only level.

**Figure 4.** Two independent sequences produce local upward features. Moon overlap reduces the union of dark silhouettes in the upper panel; a planet hiding a dim source patch removes less brightness in the lower panel. Each panel uses its own receive clock. One-second means display the characteristic-state contrasts. Article figure (built locally at `output/pdf/transit-method.pdf`).

### A source patch reduces the brightness being hidden

A patch on the emitting surface changes the integrand of Eq. (1). If the same planet area $A$ covers brightness $J_b$ outside the patch and $J_s<J_b$ over it, the recovered contribution is proportional to $A(J_b-J_s)$. The anomaly consequently constrains a covered-area–brightness-contrast product. A small dark patch and a larger weakly dim patch can produce the same integrated change. This is distinct from the union-area mechanism in Eq. (8) even though both can make a positive excursion during a deficit.

The spotted-source comparison uses baseline windows $[5,15)$, $[65,75)$ and $[95,105)\,\mathrm{s}$. Adjacent plateaus use $[45.5,48.5)$ and $[55.5,58.5)$; the crossing uses $[50.5,53.5)$. Their baseline, adjacent and crossing means are 115.11, 100.05 and 103.12 counts. The local contrast,

$$
C_s=\frac{X_{\rm cross}-X_{\rm adjacent}}{B-D}, \tag{10}
$$

is 2.92 percentage points with $D=10$ counts, recovering 20.4% of the adjacent deficit. The adjacent and crossing depths remain 14.33 and 11.41%, so the upward anomaly does not restore the unobscured level.

These windows compare settled characteristic states. The intervening returns to higher light are excluded; the entire central sequence is not fitted as a single uninterrupted geometrical crossing. Separate deeper control windows, $[20.5,23.5)$ and $[80.5,83.5)\,\mathrm{s}$, give 19.16% deficit. They establish another observed level. Interpreting its difference from the adjacent plateau as a spot covering fraction depends on matching the two projected silhouettes.

If the adjacent and crossing depths were nevertheless inserted into the uniform-source square-root relation, their inferred projected radii would differ by a factor 0.892. This apparent 10.8% reduction illustrates a model mismatch, not a physical radius change. Stellar calculations show how unmodelled spot anomalies can bias fitted radius, duration and timing [9]. Their quantitative corrections depend on spot location and brightness; they cannot be transferred as a universal adjustment to a lamp model.

**Table 3.** Moon and source-patch contrasts from characteristic-state means, each using its local baseline and a 10-count background. Scale is the quadrature combination of one-second block SDs divided by the net baseline.

| Comparison | Change (count) | Contrast (pp) | Scale (pp) |
| --- | --- | --- | --- |
| Moon extra deficit | 2.97 | 2.82 | 0.81 |
| Moon overlap recovery | 1.56 | 1.48 | 0.96 |
| Spot crossing recovery | 3.07 | 2.92 | 0.63 |

### What distinguishes the two explanations

The one-second block dispersions are 0.54, 0.66 and 0.76 counts for the moon's planet-only, separated and overlapping states. Combining the relevant dispersions in quadrature and dividing by the local net baseline gives the descriptive scales in Table 3. The spot comparison has adjacent and crossing block dispersions of 0.50 and 0.43 counts. There are only six complete overlap blocks and three crossing blocks. Those counts are not independent physical repetitions, and the scales do not establish a detection probability.

The discrimination instead comes from controlled geometry. A moon interpretation requires separated and overlapping silhouettes, with both bodies inside the source in the compared windows. A source-patch interpretation requires the dim region to be attached to the emitting surface and a comparable planetary silhouette on either side of the anomaly. A motor-only control, a no-patch control and a detector-view image test different alternatives. A rod leaving the beam can brighten either configuration without realizing the intended astronomical mechanism.

Moon mass and spot temperature depend on dynamical and brightness information, respectively. A moon radius additionally needs a resolved fully superimposed silhouette, source scale and projection distances. Dynamical transit-timing or transit-duration variations depend on recurring orbital information in addition to the characteristic brightness means. For an identical moon phase every planetary orbit, the phase advance is $2\pi T_p/T_m$, so $T_p/T_m$ must be an integer; a rational noninteger ratio repeats only after several planetary orbits. The state sequence itself does not establish either period. Spot amplitude likewise leaves its area, brightness and track position degenerate.

## Two luminous bodies change the denominator

The binary configuration makes a further alteration to the same brightness integral. For two uniform projected discs, let $J_1,J_2$ be detector-weighted surface brightnesses and $A_1,A_2$ their unobscured areas. The baseline source contribution is $L=J_1A_1+J_2A_2$. If the same overlap area $A_o$ is hidden at the two conjunctions,

$$
\delta_1=\frac{J_1A_o}{L},\qquad
\delta_2=\frac{J_2A_o}{L}. \tag{11}
$$

Only under those equal-overlap conditions would the depth ratio give $J_1/J_2$. It would still not give the total luminosity ratio without the two areas. Partial eclipses, unequal projected overlaps and source brightness structure change the relation. Modern binary calculations integrate local passband intensities over the two visible surfaces [10]; the dark-planet square-root rule discards the companion's contribution to $L$.

Primary denotes the deeper observed minimum, not necessarily the eclipse of the larger object. The example primary centres are near device times 20, 50, 80 and $110\,\mathrm{s}$, and secondary centres are near 35, 65 and $95\,\mathrm{s}$. For every centre $c$, the local baseline uses $[c-6,c-3)$ and $[c+3,c+6)$, and the minimum uses $[c-0.75,c+0.75)\,\mathrm{s}$. This common central window lies inside both types of minimum. The background is the adopted 10 counts, while the local baseline replaces an entered 210-count normalization reference.

**Figure 5.** Unequal alternating minima distinguish successive eclipse events from a full primary-to-primary cycle. Raw clear counts and one-second means retain the contrast between primary and secondary states; the two types also have different apparent durations. Article figure (built locally at `output/pdf/transit-method.pdf`).

The four primary reductions have mean depth 31.05% and event standard deviation 0.20 percentage points; the three secondary reductions give 10.49% and 0.12 points. Their mean depth difference is 20.56 points and their ratio is 2.96. These are unequal removed contributions. Interpretation of the depth ratio as a brightness ratio depends on matched projected overlap areas, with the differing apparent durations providing a geometrical constraint. Component temperatures, radii and masses additionally depend on surface-brightness, geometrical and dynamical constraints.

**Table 4.** Binary eclipse depths and primary-onset intervals. SD summarizes event-to-event depth variation or interval variation; adjacent intervals share endpoints.

| Depth statistic | Primary | Secondary |
| --- | --- | --- |
| Number of events | 4 | 3 |
| Mean depth (%) | 31.05 | 10.49 |
| Event SD (percentage points) | 0.20 | 0.12 |

Primary onset intervals (s): 29.989, 29.991, 30.005 Mean interval: 29.995 s; descriptive SD: 0.008 s

A separate timing reduction locates each primary onset as the first sample below the midpoint between its local baseline and minimum mean, searching only within $[c-3,c)$ on the device clock. The associated receive time supplies the onset coordinate. Its intervals are 29.989, 29.991 and $30.005\,\mathrm{s}$, with mean $29.995\,\mathrm{s}$ and sample standard deviation $0.008\,\mathrm{s}$. The strong primary deficit makes the localized crossing unambiguous in this example. Decimal resolution does not establish equivalent physical timing accuracy, and the shared endpoints again prevent treating the intervals as independent period repetitions.

The entered phase definition is $\phi=\operatorname{frac}[(t_{\rm rec}-20\,\mathrm{s})/(30\,\mathrm{s})]$. The reported phase follows this stated phase convention to numerical rounding. Folding at the separation between adjacent unequal minima would mix primary and secondary states. Conversely, a secondary near half-phase here does not justify imposing half-phase on an eccentric binary. Absolute masses and dimensions depend on dynamical and geometrical constraints alongside the integrated light measurement.

A physical two-source mount must therefore establish actual mutual occultation of extended luminous surfaces. A point LED, direction-dependent emission, changing distance or a turntable support can produce a double modulation for another reason. One-source-at-a-time and support-only controls, together with the detector view, distinguish those effects. A centre-fixed laboratory lamp is useful for projected illumination but does not reproduce two stars orbiting their common centre of mass.

## A hierarchy of defensible inferences

The examples support progressively different statements. A local mean deficit is the least demanding reduction, provided its reference windows and background convention are stated. A projected radius ratio adds a uniform-source and complete-overlap model. A physical radius adds measured scale and distance projection. A threshold span adds a timing rule and temporal response, while orbital parameters require an adequate dynamical description. More elaborate curves do not automatically justify moving further up that hierarchy.

The most informative controls correspond to the term being interpreted. Bracketed unobscured measurements address baseline change; a source-blocked observation constrains additive background; a known attenuator or silhouette tests transfer and projection. Varying speed at fixed optical settings probes temporal resolution. Source-patch and moon controls discriminate two brightening mechanisms that otherwise share the same sign, and separate luminous-body measurements constrain the binary denominator. Event repetition characterizes scatter in these comparisons; source-model choice and clock response enter as separate contributions to the interpretation.

Taken together, local photometry, actual time coverage and an independently constrained view of the apparatus turn a visible dip into a quantitative investigation. The four detector examples recover similar shallow deficits under explicitly different reference conventions, the phase test exposes a failure of short-feature coverage, and the extended configurations show why a minimum alone does not identify an astronomical object. The scientific interpretation therefore depends on matching each estimator to its physical assumptions, rather than assigning one universal radius or significance to every light-curve feature.

## References

1. Spicker, Sebastian J.; Küpper, Alexander (2024). [Exoplanet Hunting in the Classroom: An Easy-to-Implement Experiment Based on Video-Aided Light Curve Analysis with Smartphones](https://doi.org/10.1119/5.0125305). The Physics Teacher.

2. Küpper, Alexander; Spicker, Sebastian J. (2023). [Ein Analogieexperiment zur Suche nach Exomonden](https://www.mnu.de/images/publikationen/zeitschrift/Heft_3-23/MNU_Inhalt_03_2023_Abstracts.pdf). MNU-Journal.

3. Kipping, David M. (2010). [Binning is Sinning: Morphological Light-Curve Distortions Due to Finite Integration Time](https://doi.org/10.1111/j.1365-2966.2010.17242.x). Monthly Notices of the Royal Astronomical Society.

4. Mandel, Kaisey; Agol, Eric (2002). [Analytic Light Curves for Planetary Transit Searches](https://doi.org/10.1086/345520). The Astrophysical Journal Letters.

5. Avago Technologies. [APDS-9960: Digital Proximity, Ambient Light, RGB and Gesture Sensor](https://docs.broadcom.com/doc/AV02-4191EN). Datasheet AV02-4191EN.

6. Hamadani, Behrang H.; Campanelli, Mark B. (2020). [Photovoltaic Characterization under Artificial Low Irradiance Conditions Using Reference Solar Cells](https://doi.org/10.1109/JPHOTOV.2020.2996241). IEEE Journal of Photovoltaics.

7. Pont, Frédéric; Zucker, Shay; Queloz, Didier (2006). [The Effect of Red Noise on Planetary Transit Detection](https://arxiv.org/abs/astro-ph/0608597). Monthly Notices of the Royal Astronomical Society.

8. Sato, Masanao; Asada, Hideki (2009). [Effects of Mutual Transits by Extrasolar Planet–Companion Systems on Light Curves](https://arxiv.org/abs/0906.2590). Publications of the Astronomical Society of Japan.

9. Oshagh, M.; Santos, N. C.; Boisse, I.; Boué, G.; Montalto, M.; Dumusque, X.; Haghighipour, N. (2013). [Effect of Stellar Spots on High-Precision Transit Light-Curve](https://doi.org/10.1051/0004-6361/201321309). Astronomy & Astrophysics.

10. Prša, A.; Conroy, K. E.; Horvat, M.; Pablo, H.; Kochoska, A.; Bloemen, S.; Giammarco, J.; Hambleton, K. M.; Degroote, P. (2016). [Physics of Eclipsing Binaries. II. Toward the Increased Model Fidelity](https://arxiv.org/abs/1609.08135). The Astrophysical Journal Supplement Series.
