# Continuous integration

`.github/workflows/ci.yml` runs on every push, pull request, and manual dispatch.
It asks for read-only repository permissions and cancels superseded runs on the
same ref, so a branch that is pushed twice only tests once.

## XML and Python

The first job installs Python 3.11, the `dev` extra (Ruff), `xmllint`, ShellCheck,
and `ripgrep`, then runs:

```sh
make lint
make validate
make check-generated
```

Validation covers the protocol catalog, source inventory, XInclude safety, core
XML, the expanded core experiments, the committed generated artifacts, and the
astronomy XML and locales.

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
Pages. It triggers on pushes to `main` that touch `demo/` or the workflow
itself, and it can also be started by hand.

This workflow needs a one-time repository setup: under **Settings → Pages**, set
**Source** to **GitHub Actions**. Once that is done, the preview is served at
`https://<owner>.github.io/curious-signals-phyphox/`. The job uploads the `demo/`
directory as a Pages artifact, so the published site contains only the preview
and nothing else from the repository.

## Releases

`.github/workflows/release.yml` runs when a tag matching `v*` is pushed. It
refuses tags whose commit is not on `main`, reruns `make validate` and
`make check-generated`, then publishes a GitHub release for that tag with the
`make bundle` ZIP of the seven core experiments, a ZIP of the astronomy
collection, and every `.phyphox` file as a separate asset. Only this job gets
`contents: write`.

To cut a release from a commit that is already on `main`:

```sh
git tag -a v0.1.0-alpha.1 -m "Curious Signals 0.1.0 alpha 1"
git push origin v0.1.0-alpha.1
```

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
