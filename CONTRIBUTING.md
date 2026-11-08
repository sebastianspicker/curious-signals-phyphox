# Contributing

Thanks for looking. This is a small set of teaching artifacts, so the most
useful contributions tend to be corrections, clearer explanations, or a
genuinely missing capability rather than broad rewrites.

Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) before you change a boundary
between components. It explains why the firmware, the experiment files, the
preview, and the tooling are kept apart, and which of them may depend on which.

## Set up a working environment

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

The paper pipeline (`make check-papers`, `make papers`) needs Python 3.12 or
newer, because Python 3.12 changed how `sum()` adds floats and the published
numbers were computed that way. Add the `papers` extra for PDF assembly:
`python -m pip install -e '.[dev,papers]'`.

Scientific XML regression fixtures run as part of `make validate` and can also
be run with `make check-experiment-math`. They exercise actual analysis blocks
with known physical inputs, invalid values and repeated processing cycles.
The broader behavioural suite is maintained separately. The `make` targets
below are the public gate; `make ci` runs them plus the firmware provision and
compile steps. Run the narrower checks
while you work and the full gate before you open a pull request:

```sh
make lint
make validate
make check-generated
make security
```

## Changing a core experiment

Core experiments are generated. Edit the sources in `src/phyphox/`, plus any
shared fragments under `src/phyphox/includes/`, then rebuild and check parity:

```sh
make build
make check-generated
make validate
git diff -- src/phyphox experiments
```

`make check-generated` has to pass once you are happy with the generated diff.
Never edit a root `experiments/*.phyphox` file directly; the next `make build`
would overwrite it.

## Changing an astronomy experiment

Files in `experiments/astronomy/` are hand-maintained and never pass through the
Arduino generator. Keep English as the root locale and keep the German and
French translations. Preserve the activity's real input path — phone sensor,
SensorTag, HID input, or Owon multimeter — and do not reroute it through
`phyphox-sense`.

`owon_digital_multimeter-debug.phyphox` is an intentional integration helper.
Its name does not make it disposable build output.

```sh
make validate
```

If you change an activity's input path, model, or scope limit, update its note
in [docs/ASTRONOMY_EXPERIMENTS_COMPANION.md](docs/ASTRONOMY_EXPERIMENTS_COMPANION.md)
in the same change.

## Changing an additional draft

Edit `experiments/drafts/<id>.phyphox` and its companion under `docs/drafts/`
together. Register every file in `docs/drafts/manifest.json`, including its
actual acquisition type, hardware, source anchors and material limitations.
Keep the Draft title and category until native and physical validation supports
promotion. These files do not pass through the core generator.

```sh
make check-drafts
make bundle-drafts
```

The checks evaluate actual XML, including repeated processing, missing inputs,
calibration domains and Record/Clear behavior. They run within `make validate`.
Phyphox buttons replace destination buffers; use singleton pending snapshots
and request-gated analysis when collecting rows. Native arithmetic can produce
infinity, so a zero-denominator guard alone does not guarantee a NaN. Preserve
raw data and acquired clocks. See [validation notes](docs/drafts/validation.md)
for optional full-schema checks and the app/hardware checks still required.

## Changing the firmware or the protocol

`protocol/contract.json` owns the shared device name, UUIDs, frame layout,
timing, mode numbers, channel meanings, and filenames. When you change a fact
there, update every concrete implementation that depends on it, including the
preview example data. The sketch keeps its own literals so it stays a single file,
so keep them consistent with the contract by hand.

```sh
make validate
make check-generated
make compile
```

`make compile` builds the sketch but never uploads it or tests a connected
board. Report BLE, sensor, electrical, and phyphox-app verification separately
from anything CI can check.

## Changing build, validation, or CI

Keep `make` as the contributor-facing interface and treat
`src/curious_signals/` as an internal implementation detail. CI and validation
must never rewrite tracked artifacts.

```sh
make lint
make validate
make check-generated
make security
```

`make provision` installs the versions recorded in
`arduino/toolchain.json` and is the only step that needs the network.
`make compile` verifies those installed versions and builds without refreshing
indexes or installing packages. `make ci` provisions and therefore needs network
access.

## Pull requests

Please include:

- what behavior or contract changed;
- which source and generated files are affected;
- the commands you ran and their exact outcomes;
- which hardware or mobile-app checks you did, and which you skipped;
- the compatibility impact;
- anything still uncertain about release or provenance.

Leave generated archives, local environments, caches, analysis state, and
credentials out of the diff.
