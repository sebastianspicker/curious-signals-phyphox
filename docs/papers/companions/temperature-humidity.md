# Temperature and Humidity: Local Air State, Calibration and Dynamic Response

*October 2021*

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The date above is the author's approximate dating of that work, not of these data.

Relative humidity and temperature describe a coupled local air state. Interpreting either channel alone can confuse heating with a change in water-vapour content. Three independent capacitive-sensor examples illustrate the distinction. During HTS221 warming, mean relative humidity falls from 46.84 to 40.40%, while paired-channel vapour pressure changes by only $-0.75\%$. SHT21 and HDC1000 moisture pulses instead raise vapour pressure from 12.24 to $17.24\,\mathrm{hPa}$ and from 12.38 to $20.56\,\mathrm{hPa}$. A second board-temperature channel in the HDC1000 apparatus records a different thermal trajectory. A common thermodynamic reduction therefore requires sensor-local temperature, explicit pairing and calibration over both environmental variables.

## One air state, several thermal locations
Relative humidity is a temperature-dependent ratio. Warming an air volume can lower its relative humidity without removing water, whereas a moisture pulse can increase both relative humidity and temperature. The distinction is especially important near powered electronics: the sensing element observes its local microenvironment, which can differ from the room or enclosure average.

The HTS221 on the original Nano 33 BLE Sense, the SHT21 on the CC2541 SensorTag and the HDC1000 on later SensorTags all use capacitive humidity sensing with an associated temperature channel [1, 2, 3]. Their common principle supports a shared reduction, but their packages, mounting and response functions differ. The later SensorTag also provides a BMP280 die-temperature channel for the barometer [4]. That second temperature is useful as a thermal diagnostic; it is not automatically the temperature to use in the humidity equation.

Environmental comparison with device and reference in nearby air volumes. Humidity reduction uses the sensing element's local temperature; a separate package-temperature channel diagnoses board heating. See the article figure (built locally at `output/pdf/temperature-humidity.pdf`).

Use a mixed enclosure, a reference thermometer and a reference hygrometer, with reproducible board support and controlled airflow. Shield against external radiation without blocking moisture exchange. A humid-air perturbation should reach the device and reference without producing droplets. Electrical self-heating, support conduction and water absorbed by enclosure materials can all change the state at the sensor relative to the intended air volume.

The example investigations ask complementary questions. The HTS221 record contains moisture pulses and a broader warming interval. The SHT21 record isolates a short humidity pulse on a slowly warming background. The HDC1000 record adds another temperature location and an independent barometric stream. Each record is reduced in its own time coordinate and environmental conditions.

## A single paired-channel reduction
Write relative humidity as $H$ in percent and water-vapour partial pressure as $p_v$:
$$
H=100\frac{p_v}{p_{\rm sat}(T)},\qquad
 p_v=\frac{H}{100}p_{\rm sat}(T). \tag{1}
$$
For the room-temperature range, the Magnus approximation gives [5]
$$
p_{\rm sat}(T)=610.94\exp\!\left(\frac{17.625T}{T+243.04}\right)\,\mathrm{Pa}, \tag{2}
$$
with $T$ entered numerically in degrees Celsius. Transform paired local temperature--humidity readings first, then average the derived $p_v$. Evaluating the nonlinear saturation function only at a window's mean temperature is a different estimator, especially during a transient.

At fixed $p_v$,
$$
\frac{d\ln H}{dT}=-\frac{17.625\times243.04}{(T+243.04)^2}. \tag{3}
$$
Near $23\,\mathrm{^\circ C}$ this is about $-0.06\,\mathrm{K^{-1}}$: a 1-K increase lowers RH by about six percent of its current value, not by six percentage points. This explains why local temperature must be part of a moisture measurement.

Numerical conversion is a prerequisite for applying this model. The SHT21's low two status bits are removed from both raw words before using $T=175.72S_T/65536-46.85$ and $H=125S_H/65536-6$ [2]. Subtracting 24 in the humidity equation would shift every result downward by eighteen percentage points; repeated averaging cannot correct that systematic error. The HDC1000 uses different coefficients, $T=165S_T/65536-40$ and $H=100S_H/65536$ [3]. A visually similar notification is insufficient reason to interchange conversion formulas between sensor generations.

The HTS221 example uses the Nano's device timestamp; the SHT21, HDC1000 and BMP280 examples use Bluetooth receive times. Within-record temperature--humidity pairing preserves the local association but does not remove differences in conversion time or response. HDC1000 temperature and humidity also share one notification family, whereas BMP280 pressure and temperature keep their own arrival times. In the HDC1000 example the two families have a 0.400-s offset. Nearest-neighbour temperature comparisons are accepted only within 0.5 s; this timing relation is not a measurement of sensor lag or radio latency. The vapour-pressure calculation uses only the HDC1000 temperature--humidity pair.

## Heating, moisture and recovery
Figure 2 displays the three trajectories in local temperature--humidity space. Table 1 uses half-open intervals, including the lower and excluding the upper boundary in each record's own time coordinate. These dedicated windows avoid combining a temperature extremum with a humidity extremum taken at another instant. The readings describe the response to each trial's environmental inputs; inter-sensor comparisons additionally depend on matched reference conditions.

Paired local temperature--humidity trajectories: (a) HTS221, (b) SHT21 and (c) HDC1000. The HTS221 warming branch lowers RH; the SHT21 and HDC1000 moisture pulses raise RH. Each trajectory follows its own record. See the article figure (built locally at `output/pdf/temperature-humidity.pdf`).

Paired-channel interval means; $p_v$ is transformed per observation before averaging. Times belong to each independent record.

| Sensor | Interval (s) | $T$ ($^\circ$C) | $H$ (%) | $p_v$ (hPa) |
| --- | --- | --- | --- | --- |
| HTS221 | 20--30 | 22.788 | 46.84 | 12.966 |
|  | 90--96 | 25.123 | 40.40 | 12.869 |
| SHT21 | 0--10 | 22.484 | 45.05 | 12.241 |
|  | 26--35 | 22.599 | 62.99 | 17.237 |
|  | 50--60 | 22.678 | 43.95 | 12.084 |
| HDC1000 | 0--25 | 23.003 | 44.16 | 12.384 |
|  | 40--60 | 24.488 | 67.04 | 20.558 |
|  | 85--115 | 22.987 | 40.99 | 11.485 |

### Warming at nearly fixed vapour pressure
The HTS221 baseline over 20--30 s gives $T=22.788\,\mathrm{^\circ C}$ and $H=46.842\%$. During 90--96 s, the corresponding means are $25.123\,\mathrm{^\circ C}$ and $40.403\%$. Paired-channel vapour pressure changes from 1296.6 to $1286.9\,\mathrm{Pa}$, a decrease of only 0.75%. Most of the RH decrease is therefore compatible with warming at nearly fixed local vapour pressure. The remaining difference cannot be assigned uniquely to moisture loss, calibration or unequal channel lag.

The same record also contains a distinct moisture pulse with maximum $63.69\%$ RH in the 35--60-s interval. Its later temperature maximum and humidity minimum occur at slightly different times. These extrema describe the temperature–humidity trajectory; interpreting their separation in terms of channel response involves the driving air history and the channel response functions.

### Moisture pulses at two sensor locations
For the SHT21, mean RH rises from $45.05\%$ over 0--10 s to $62.99\%$ over 26--35 s. The accompanying temperature increase is only $0.115\,\mathrm{K}$, while $p_v$ rises from 12.241 to $17.237\,\mathrm{hPa}$. Heating alone cannot explain an increase in RH under Eq. (1). During 50--60 s the sensor is slightly warmer than initially, with $p_v=12.084\,\mathrm{hPa}$. The lower recovered RH thus combines a thermal effect with a small remaining vapour-pressure difference. Environmental drift and sensor memory enter the interpretation of the recovered state.

The HDC1000 event is larger: RH rises from 44.16 to $67.04\%$ while local temperature rises by $1.485\,\mathrm{K}$. Vapour pressure increases from 12.384 to $20.558\,\mathrm{hPa}$ over the specified baseline and 40--60-s pulse windows. By 85--115 s it is $11.485\,\mathrm{hPa}$. The physical inference is a moisture-rich interval followed by a different recovered state, conditional on local equilibrium and the calibration model.

The accompanying BMP280 indications make the thermal-location issue concrete. Its die-temperature means are $24.106\,\mathrm{^\circ C}$ over 0--25 s and $24.335\,\mathrm{^\circ C}$ over 40--60 s, compared with HDC1000 means of 23.003 and $24.488\,\mathrm{^\circ C}$. An initial difference of $1.103\,\mathrm{K}$ therefore does not provide a universal correction between packages. Barometric pressure spans 1007.46--$1008.49\,\mathrm{hPa}$ in its own record; that channel supplies environmental context, not an independent humidity calibration.

## Calibration and dynamic interpretation
Calibrate over a grid of humidity and temperature, with both rising and falling humidity sequences and reference conditions reserved for validation. Saturated salt solutions provide established equilibrium humidity points when their temperature dependence and equilibration requirements are respected [6]. Keep droplets and salt contamination away from the sensor. A temperature-dependent HTS221TR study reinforces the need to include temperature in the calibration design [7]; its fitted correction is specific to the tested devices, not a transferable coefficient set.

Equilibrium accuracy and dynamic response need separate experiments. The HTS221 datasheet gives typical 63%-response times of 15 s for temperature and 10 s for humidity under its stated conditions [1]. These are much longer than the nominal 50-ms wireless frame spacing. The SHT21 and HDC1000 mounting guidance similarly makes thermal exposure and airflow relevant [2, 3]. More transmitted rows do not create more independently equilibrated air states.

A useful first-order description is
$$
\tau_T\dot T_s+T_s=T_a,\qquad
 \tau_H\dot H_s+H_s=H_a. \tag{4}
$$
The right-hand quantities refer to the air at the sensing location. An independently observed environmental step is needed to distinguish that input history from the assembled sensor response. Applying the equilibrium Magnus reduction to differently lagged channels can create an apparent vapour-pressure transient even when each channel is internally consistent.

For $p_v=Hp_{\rm sat}(T)/100$, uncertainty propagation includes both local sensitivities and their covariance. Shared thermal gradients and reference corrections can correlate temperature and RH errors. The short-interval HTS221 baseline SDs, about $0.013\,\mathrm{K}$ and 0.030 percentage points, describe dispersion rather than absolute accuracy. Average settled intervals or use block estimates for correlated records, then assess reproducibility across independent environmental trials.

## References

1. STMicroelectronics (2023). [HTS221: Capacitive Digital Sensor for Relative Humidity and Temperature](https://www.st.com/resource/en/datasheet/hts221.pdf).
2. Sensirion (2022). [Datasheet SHT21: Humidity and Temperature Sensor IC](https://sensirion.com/media/documents/120BBE4C/63500094/Sensirion_Datasheet_Humidity_Sensor_SHT21.pdf).
3. Texas Instruments (2016). [HDC1000 Low Power, High Accuracy Digital Humidity Sensor with Temperature Sensor](https://www.ti.com/lit/ds/symlink/hdc1000.pdf).
4. Bosch Sensortec (2021). [BMP280: Digital Pressure Sensor](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf).
5. Alduchov, Oleg A.; Eskridge, Robert E. (1996). [Improved Magnus Form Approximation of Saturation Vapor Pressure](https://doi.org/10.1175/1520-0450%281996%29035%3C0601:IMFAOS%3E2.0.CO;2). DOI: 10.1175/1520-0450(1996)035<0601:IMFAOS>2.0.CO;2.
6. Greenspan, Lewis (1977). [Humidity Fixed Points of Binary Saturated Aqueous Solutions](https://doi.org/10.6028/jres.081A.011). DOI: 10.6028/jres.081A.011.
7. Holik, Mario; Barac, Antun; Zidar, Josip; Stojkov, Marinko (2024). [Dual-Approach Calibration Unlocks Potential of Low-Power, Low-Cost Temperature and Humidity Sensors](https://doi.org/10.17559/TV-20240606001753). DOI: 10.17559/TV-20240606001753.
