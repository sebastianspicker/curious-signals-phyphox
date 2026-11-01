# Continuous integration

`.github/workflows/ci.yml` starts on pushes, pull requests and manual dispatch.
Its security job remains automatic. The XML/Python and Arduino jobs run only
for Dependabot-authored pull requests or manual dispatch; pushes and ordinary
pull requests do not start those generic checks. Permissions are read-only,
and superseded runs on the same ref are canceled.

## XML and Python

The first job installs Python 3.11, the `dev` extra (Ruff), `xmllint`, ShellCheck,
and `ripgrep`, then runs:

```sh
make lint
make validate
make check-generated
```

Validation covers the protocol catalog, the firmware's UUID, device-name,
timing, frame-size and mode literals, source inventory, XInclude safety, core
XML, the expanded core experiments, the committed generated artifacts, and the
astronomy XML and locales. It also runs `scripts/check_experiment_math.py`:
known-input fixtures exercise the actual XML analysis for calibration, optical
ratios, decoder selection, missing values, complete-event timing and independent
sensor clocks. The focused interpreter covers the modules used by the fixtures;
it does not replace Android/iOS import or hardware testing.

Validation also runs `scripts/check_drafts.py`: all additional drafts must have
a companion and metadata entry, valid container/export references and a real
declared acquisition path. Five numerical fixture groups exercise their XML,
including native button replacement, empty inputs, IEEE nonfinite values,
calibration gates and repeated capture/clear cycles. Full official RelaxNG and
Schematron validation is an additional explicit check documented in
[the draft validation notes](drafts/validation.md); those schemas and lxml are
not part of the default dependency set.

`scripts/check_doc_links.py` fails if a tracked Markdown file links to
a path the repository does not contain, such as the gitignored `output/`.

Finally, the two example-data validators check every CSV in both manifests:
increasing time, no infinite values, detector count ranges, magnitudes and
decoded raw words.

`make check-generated` rebuilds in a temporary directory and compares bytes. CI
never runs `make build`, so a job can fail on drift but can never rewrite a
tracked artifact.

## Firmware

The Arduino job downloads Arduino CLI 1.4.1 and verifies the SHA-256 of the
pinned Linux archive before unpacking it. It sets up Python 3.11 for the
repository tooling, restores the Arduino package cache, runs `make provision` to
install the Nano core and the sensor libraries pinned in
`arduino/toolchain.json`, then runs `make compile` to verify the
installed versions and build for `arduino:mbed_nano:nano33ble` without
refreshing indexes or installing anything new.

This job never uploads firmware or runs it on a physical board, and the
package-index, core, and library downloads remain a separate trust boundary from
the checksum-verified CLI archive.

## Security

The security job installs `ripgrep`, then runs `make security`. That gate
searches tracked and untracked files for a narrow set of credential patterns in
bounded batches. A scanner that cannot run fails the gate; when it does find something, the report carries filenames and line numbers
but never the matched credential contents.

`.github/dependabot.yml` opens monthly, grouped version-update pull requests for
the pinned GitHub Actions and the Python dependencies. The Arduino CLI version
and checksum in `ci.yml` and the core and library pins in
`arduino/toolchain.json` are outside Dependabot's reach and are bumped by hand.

These are repository guardrails. They do not replace supply-chain review,
firmware review, hardware or electrical testing, or content-provenance review.

## Preview deployment

`.github/workflows/pages.yml` publishes the static preview in `demo/` to GitHub
Pages. It runs only when manually dispatched on the repository's default
branch. Pushes and pull requests do not publish the preview.

This workflow needs a one-time repository setup: under **Settings → Pages**, set
**Source** to **GitHub Actions**. Once that is done, the preview is served at
`https://<owner>.github.io/curious-signals-phyphox/`. The job uploads the `demo/`
directory as a Pages artifact, so the published site contains only the preview
and nothing else from the repository.

## Releases

`.github/workflows/release.yml` runs only when manually dispatched on the
default branch, with an existing `v`-prefixed `tag` input. It checks out that
exact tag and refuses tags whose commit is not on the default branch. It
reruns `make validate` and
`make check-generated`, then publishes a GitHub release for that tag with the
`make bundle` ZIP of the seven core experiments, a ZIP of the astronomy
collection, the `make bundle-drafts` ZIP of the twenty-eight drafts (XML, licences
and attribution notes, not the companion collection), and every core, astronomy and
draft `.phyphox` file as a separate asset; it fails if two of those files share
a name. Only this job gets
`contents: write`.

To cut a release from a commit that is already on `main`:

```sh
git tag -a v0.1.0-alpha.1 -m "Curious Signals 0.1.0 alpha 1"
git push origin v0.1.0-alpha.1
gh workflow run release.yml --ref main -f tag=v0.1.0-alpha.1
```

Creating or pushing a tag alone does not publish anything. Dispatch from the
default branch (currently `main`) after reviewing the tagged commit.

Releases are published as full releases, not pre-releases, because
`releases/latest/download/<file>` links (which the README offers for phyphox QR
codes) skip pre-releases. GitHub generates the release notes from the commits
since the previous tag; edit them on GitHub afterwards if testers need more
context.

## Running the same checks locally

```sh
make ci
```

The full local target does not rewrite your checkout, but it does include the
network-backed provisioning step and may update user-level Arduino CLI state. If
you already have the pinned packages installed and just want a build, use
`make compile` instead.
