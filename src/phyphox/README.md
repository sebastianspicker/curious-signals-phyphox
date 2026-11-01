# Core phyphox sources

The seven root files in `experiments/*.phyphox` are generated. Their sources
live here, in `src/phyphox/*.phyphox.xml`.

Sources pull in the shared data containers and Bluetooth mappings from
`src/phyphox/includes/` through XInclude. The file format has no way to include
a single attribute or a translation string, so view definitions and translated
text are repeated wherever they are needed.

## Calibration and physical setup

Each experiment includes **Setup** and **Calibration** views in English,
German, and French. Coefficients start at nominal values; measure them on the
actual apparatus. Changing a coefficient recomputes the recorded trace, and
clearing experiment data restores the defaults. Exports include original
readings, corrected quantities, calibration settings, device time and BLE
receive time. Receive time is a delivery timestamp, not a second sensor clock.

| Experiment | Calculation and calibration |
| --- | --- |
| Accelerometer | Per-axis `k(raw − b)` in g, converted with standard gravity `9.80665 m/s²`; magnitude is recalculated from corrected components. Six stationary orientations constrain offsets and gains. This does not remove gravity. |
| Gyroscope | Per-axis `k(raw − b) × π/180`; determine bias at rest and gain with independently measured positive/negative rates. The library/datasheet nominal scale comparison is not a measured calibration. |
| Magnetometer | Per-axis `k(raw − b)` and corrected magnitude. This diagonal model cannot correct cross-axis coupling; a complete soft-iron calibration needs a matrix. |
| Pressure | `10 × raw_kPa − bias_hPa`; pressure change is shown only after entering a positive reference pressure. Reference means and event readings must use the same bias correction. |
| Temperature/humidity | Separate indicated-minus-reference biases; values are not silently restricted to a physical range. Use nearby reference probes, radiation shielding and controlled airflow. |
| Light/RGB | Separate covered-sensor dark subtraction. A raw-channel ceiling indicator screens for the approximately 4100-count limit at the pinned gain/integration settings; it does not certify linearity. |
| Analogue inputs | Independent `U = kq + c` calibrations. The default `k = 3300/1023 mV/count` is a nominal endpoint scale. Keep pin voltages within 0–3.3 V and account for source impedance and loading. |

The existing example CSVs and papers describe the acquisition revision that
preceded these changes. Their original numerical results are retained; see
[acquisition notes](../../docs/papers/implementation-notes.md) for the distinction.

## Editing

Work on the `.phyphox.xml` sources and the shared include files. Treat the
matching generated files as build output, not as independent sources.

Rebuild and verify from the repository root:

```sh
make build
make check-generated
make validate
```

`make build` intentionally updates tracked files in `experiments/`.
`make check-generated` rebuilds into a temporary directory and compares the
result byte for byte, which is what CI uses to catch drift.

## Attribution

- Original authors: Gautier Creutzer and Frédéric Bouquet, La Physique
  Autrement, Laboratoire de Physique des Solides, Université Paris-Saclay
- Revisions 1.1 and 1.2: Sebastian J. Spicker and Frédéric Bouquet, including
  the German translation, units, views, axis labels, and consistency changes
- [Related English and French material](https://vulgarisation.fr/?lang=en)
- [Related German material](https://astro-lab.app/arduino-und-phyphox/)
- Related project: phyphox, RWTH Aachen University

## License status

The seven sources and the generated files say "LGPL-3.0+" (that is,
`LGPL-3.0-or-later`) in their header comments. The shared fragments in `includes/` exist only to be expanded
into those files and are under the same terms. The LGPL text is in
[`COPYING.LESSER`](../../COPYING.LESSER), and the GPL text it builds on is the
root [`LICENSE`](../../LICENSE). The root README has the table of terms for each
component.
