# First Slip, Inclination, and the Meaning of Static Friction

*March 2018*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

**Abstract.** 
A breakaway angle identifies a static-friction estimate only when the inclination belongs to the contact state preceding motion. We combine gravity-sensitive acceleration with a separately timed linear-acceleration trigger and retain the first sustained excursion after arming. In the data, the first above-threshold sample occurs at 20.002 s, confirmation follows at 20.142 s, and the selected pre-slip inclination is $25.104^\circ$, giving $\mu_s=0.4685$. Timing, mounting and contact history enter the interpretation differently: the small local angular scatter does not determine the uncertainty of a material coefficient from one slip event.

**Keywords:** Static friction, breakaway, inclination, accelerometer, event detection.

## Breakaway as an operational quantity

ASTM G219 defines the tangent of the inclination at macroscopic breakaway as the static-friction coefficient for the sliding couple [1]. The measurand belongs to a prepared contact under a specified loading history: surface preparation, prior sliding, dwell and raising rate can all matter. The first slip is therefore the relevant event. A later impact or larger inclination concerns a contact that has already moved.

For a block resting on a ramp at angle $\theta$, the tangential load is $mg\sin\theta$ and the normal force is $mg\cos\theta$. Under the elementary Coulomb model, impending motion gives
$$
\mu_s=\tan\theta_c.
\tag{1}
$$
The mass cancels provided gravity and the ramp reaction are the only external loads, the body neither tips nor rolls, and raising is quasi-static. A cable tug or catching edge introduces an additional force and invalidates this balance.

Acceleration during sliding can instead be used to estimate kinetic friction, as in Baldock and Johnson's smartphone investigation [2]. Here it only locates the onset event. Contact-age dependence in Dieterich's controlled shear experiments explains why dwell and loading history deserve attention [3]; the rock-specific constitutive parameters are not transferred to the present contact.

## Inclination before the acceleration excursion

A rigid mount fixes a phone to the rider with the screen plane parallel to the contact plane, as in Fig. 1. A broad padded tray catches the rider after breakaway. While the assembly is quasi-static, its accelerometer components provide the inclination estimator
$$
\hat\theta=\operatorname{atan2}\!\left(\sqrt{g_x^2+g_y^2},|g_z|\right).
\tag{2}
$$
The absolute normal component permits the screen to face either upwards or downwards. It does not correct a wedge between the phone and ramp. Stationary comparisons at independently known angles are needed to separate mounting error from sensor offsets and cross-axis response; gravity-based accelerometer characterization treats those distinctions explicitly [4].

**Figure 1.** Inclined-ramp arrangement. The phone is rigidly attached to the rider, with its normal axis perpendicular to the contact plane; the tray catches the rider after breakaway. View figure (built locally at `output/pdf/static-friction.pdf`).

Each acceleration stream retains its own timestamps. For the example reduction, arming is at 5 s, the linear-acceleration threshold is $1.0\,\mathrm{m\,s^{-2}}$, and the required sustained duration is 0.15 s after the last below-threshold sample. A gap longer than 0.15 s invalidates the onset until another low sample is observed. This prevents missing observations from masquerading as sustained acceleration.

Once an excursion qualifies, inclination is queried 0.10 s before its last low sample. The most recent gravity reading preceding that query is selected; a future reading is never substituted. The accepted reading must be no more than 0.20 s old, have magnitude between 9.3 and $10.3\,\mathrm{m\,s^{-2}}$, and give an angle at most $85^\circ$. These screens reject conspicuous inconsistency, but a near-gravitational magnitude does not prove that translational acceleration is absent. The first valid event remains selected even if a later jolt is larger. A visual observation of sliding remains necessary because a tap or rocking motion can also trigger the accelerometer.

## The event resolved in the data

Figure 2 shows the increasing inclination and the short initial acceleration excursion. The 0--5 s linear-acceleration baseline has mean $0.126\,\mathrm{m\,s^{-2}}$ and sample standard deviation $0.079\,\mathrm{m\,s^{-2}}$. Its magnitude is positive even in the resting interval; magnitude noise should not be treated as a signed, zero-mean acceleration. The gravity norm over that interval is $9.812\,\mathrm{m\,s^{-2}}$, with sample scatter $0.020\,\mathrm{m\,s^{-2}}$.

**Figure 2.** (a) Gravity-derived inclination and (b) linear-acceleration magnitude around the first sustained excursion. Separate stream timestamps determine the pre-onset inclination used for the friction estimate. View figure (built locally at `output/pdf/static-friction.pdf`).

**Table 1.** Detection times, pre-slip angle and friction estimate.

| Quantity | Value |
| --- | --- |
| Last below-threshold time (s) | 19.9820 |
| First above-threshold time (s) | 20.0020 |
| Sustained-event confirmation (s) | 20.1421 |
| Selected gravity time (s) | 19.8819 |
| Selected angle (deg) | 25.1043 |
| $\tan\hat\theta$ | 0.46853 |

Table 1 separates three times that would otherwise be conflated. Acceleration onset is bracketed by the last low and first high samples, a roughly 20-ms interval. Confirmation is another 0.140 s later. The selected gravity sample is 0.120 s before the first high sample and only 0.00014 s older than the pre-slip query. Its norm is $9.808\,\mathrm{m\,s^{-2}}$. The resulting coefficient is 0.4685; confirmation latency has not shifted the angle forward into the slip excursion.

The ramp is not raised at a constant rate. A straight-line fit over 5--19.8 s leaves an angular RMS residual of $0.934^\circ$, so applying one global raising rate as a timing correction would be inappropriate. A local fit over 19--19.8 s gives $0.475\,\mathrm{deg\,s^{-1}}$ and residual scatter $0.110^\circ$. Its extrapolated angle change across the 0.120-s selection offset is about $0.057^\circ$. This is a local sensitivity estimate, not a unique bias correction through the curved approach to the plateau.

## What the coefficient can support

At the selected angle,
$$
\mathrm d\mu_s=\sec^2\theta\,\mathrm d\theta,
\tag{3}
$$
with angular increments in radians. The local $0.110^\circ$ scatter corresponds to a coefficient scale of about 0.0023. A $1^\circ$ mounting error would contribute about 0.021, almost an order of magnitude larger. Averaging many adjacent acceleration readings cannot remove that geometric error or turn one breakaway into repeated trials.

The later 25--29 s inclination is $25.012^\circ$ with $0.133^\circ$ sample scatter, consistent with a ramp that has stopped rising. That average cannot replace the earlier contact state. Repeated preparations and slips characterize contact variability alongside within-event scatter.

The trigger also has a fundamental limit: uniform sliding has zero linear acceleration. Motion can therefore continue below threshold even for an ideal sensor, and slow creep may begin without triggering the detector. The reported coefficient is an operational breakaway estimate conditional on visual confirmation of the first slip and on the stated detection criterion.

## References

1. [ASTM International (2024), G219-24: inclined-plane static-friction guide](https://store.astm.org/g0219-24.html).
2. [Baldock and Johnson (2016), Investigation of kinetic friction using an iPhone, Physics Education 51, 065005](https://doi.org/10.1088/0031-9120/51/6/065005).
3. [Dieterich (1979), Modeling of rock friction: 1. Experimental results and constitutive equations, J. Geophys. Res. 84, 2161–2168](https://doi.org/10.1029/JB084iB05p02161).
4. [Geist et al. (2017), Gravity-based characterization of three-axis accelerometers in terms of intrinsic accelerometer parameters, J. Res. NIST 122, 32](https://doi.org/10.6028/jres.122.032).
