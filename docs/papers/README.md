# Curious Signals research companions

Twenty-one topic papers summarize work from 2018 to 2024 at the Institute of Physics Education, University of Cologne. They cover all forty-three experiment definitions and all fifty-eight example datasets. Complementary sensors share a physical model and analysis framework within a single article; longer comparisons replace separate hardware variants.

**Data provenance.** The datasets analysed here are deterministic example data, generated for the October 2026 edition from fixed seeds by the scripts in `example-data/`. They are modelled on the named sensors' units, sampling, resolution, noise and limits, so the methods can be followed and rerun; they are not recordings from the original work. The month and year on each paper are the author's approximate dating of that work, not of these data.

The [consolidation record](research/consolidation.md) maps the earlier forty-three articles to the canonical topics and explains which reductions and distinctions were retained. All articles have full editable Markdown companions as well as LaTeX sources. The [experiment index](../drafts/README.md) retains the device-specific phyphox definitions and their validation status.

**Authors:** Sebastian J. Spicker and Alexander Küpper  
**Affiliation:** Institute of Physics Education, University of Cologne  
**Edition:** October 2026

## Individual arXiv submissions

`make arxiv` writes twenty-one independent submission folders under
`arxiv/<paper>/`; they are generated locally and are not tracked in this
repository. Each folder has its own bibliography, figures and plot
data. Its PDF and TeX file sit side by side as `YYYY-MM_paper-title.pdf` and
`YYYY-MM_paper-title.tex`. Each paper has its own running header, its date and
the data provenance note and a brief retrospective footnote. The canonical manuscripts supply these submission
copies; their verified final PDFs also supply the retrospective collection.

Run `make arxiv` to prepare and verify every package, including compilation after
extracting each final ZIP outside the repository. Upload ZIPs are written to
`output/arxiv/` and exclude the local PDF proof. `make check-arxiv` checks the
prepared sources, proofs and upload archives without rewriting them.

## Read the collection

Run `make papers`, then open the retrospective PDF (built locally at `output/pdf/2026-10_curious-signals-retrospective.pdf`).
It contains a cover, a two-page synthesis of the papers, a full-title contents
list with dates and page ranges, and all twenty-one final arXiv papers. Page
numbers run continuously and agree with the PDF viewer, contents and bookmarks.
The cover counts as page 1 without displaying a numeral. Paper-specific headers,
figures, references and links are retained.

The retrospective source bundle (built locally at `output/pdf/2026-10_curious-signals-retrospective-sources.zip`)
contains the editable front matter, builder and final article inputs for an
independent rebuild. The individual PDF archive (built locally at `output/pdf/curious-signals-individual-papers.zip`)
uses the same dated filenames as the arXiv proofs. The full analysis source archive (built locally at `output/pdf/curious-signals-latex-sources.zip`)
also contains the canonical manuscripts, data and numerical generators. All
deliverables remain under the gitignored `output/pdf/`; the older collection
filename remains a byte-identical compatibility copy.

With current arXiv packages, `make retrospective` rebuilds only the collection.
`make check-retrospective` checks the current sources and PDFs, contents targets,
page ranges, page numbers, bookmarks and preserved article links. Its
`retrospective-build-summary.json` records each article's physical start and end
pages. The current edition has five front-matter pages and 79 article pages.

| Paper | Date | Article source | Markdown | PDF |
| --- | --- | --- | --- | --- |
| Specific Force, Inclination and the Limits of Resolution | February 2021 | [LaTeX](content/accelerometer.tex) | [Read](companions/accelerometer.md) | `output/pdf/accelerometer.pdf` |
| Angular Rate, Reversal and Integrated Rotation | June 2021 | [LaTeX](content/gyroscope.tex) | [Read](companions/gyroscope.md) | `output/pdf/gyroscope.pdf` |
| Magnetic Vector Calibration and Indirect DC Current Measurement | February 2022 | [LaTeX](content/magnetometer.tex) | [Read](companions/magnetometer.md) | `output/pdf/magnetometer.pdf` |
| Voltage Measurement and Circuit Inference: ADC Codes and Multimeter Readings | July 2022 | [LaTeX](content/analog-inputs.tex) | [Read](companions/analog-inputs.md) | `output/pdf/analog-inputs.pdf` |
| First Slip, Inclination, and the Meaning of Static Friction | March 2018 | [LaTeX](content/static-friction.tex) | [Read](companions/static-friction.md) | `output/pdf/static-friction.pdf` |
| Motor-State Comparisons from Sound Envelopes and Magnetic Fields | February 2019 | [LaTeX](content/audio-magnetic.tex) | [Read](companions/audio-magnetic.md) | `output/pdf/audio-magnetic.pdf` |
| Barometric Height Changes with Bracketed Pressure References | November 2023 | [LaTeX](content/pressure.tex) | [Read](companions/pressure.md) | `output/pdf/pressure.pdf` |
| Temperature and Humidity: Local Air State, Calibration and Dynamic Response | October 2021 | [LaTeX](content/temperature-humidity.tex) | [Read](companions/temperature-humidity.md) | `output/pdf/temperature-humidity.pdf` |
| Enclosure Heating and Thermal Response | May 2019 | [LaTeX](content/greenhouse.tex) | [Read](companions/greenhouse.md) | `output/pdf/greenhouse.pdf` |
| Pressure, Compression and Relaxation in Gas Enclosures | September 2020 | [LaTeX](content/mission-to-mars.tex) | [Read](companions/mission-to-mars.md) | `output/pdf/mission-to-mars.pdf` |
| Pressure-Dependent Boiling: Equilibrium Curves and Observational Thresholds | December 2019 | [LaTeX](content/pressure-boiling.tex) | [Read](companions/pressure-boiling.md) | `output/pdf/pressure-boiling.pdf` |
| Optical Response, Reference Substitution and Detector-Weighted Transmission | July 2023 | [LaTeX](content/light-rgb.tex) | [Read](companions/light-rgb.md) | `output/pdf/light-rgb.pdf` |
| Inverse-Square Photometry: Distance, Timing and Averaging | March 2020 | [LaTeX](content/illuminance-distance.tex) | [Read](companions/illuminance-distance.md) | `output/pdf/illuminance-distance.pdf` |
| From Reflected Light to Relative Reflectance | June 2018 | [LaTeX](content/albedo.tex) | [Read](companions/albedo.md) | `output/pdf/albedo.pdf` |
| Settled-Angle Polarimetry: Scale, Floor and Angular Zero in Malus' Law | September 2018 | [LaTeX](content/malus-law.tex) | [Read](companions/malus-law.md) | `output/pdf/malus-law.pdf` |
| Indicative Colour Temperature and the Limits of a Transferred Sensor Matrix | October 2019 | [LaTeX](content/colour-temperature.tex) | [Read](companions/colour-temperature.md) | `output/pdf/colour-temperature.pdf` |
| Infrared Radiometry: Calibration and Distance-Dependent Heating | August 2020 | [LaTeX](content/ir-distance.tex) | [Read](companions/ir-distance.md) | `output/pdf/ir-distance.pdf` |
| Paired Spectral Ratios: Separating Shared Features from Additional Attenuation | February 2024 | [LaTeX](content/spectral-fingerprints.tex) | [Read](companions/spectral-fingerprints.md) | `output/pdf/spectral-fingerprints.pdf` |
| From Illumination Geometry to Thermal Contrast | November 2020 | [LaTeX](content/tidal-locking.tex) | [Read](companions/tidal-locking.md) | `output/pdf/tidal-locking.pdf` |
| Laboratory Transit Photometry: Calibration, Temporal Resolution and Visible-Area Models | September 2024 | [LaTeX](content/transit-method.tex) | [Read](companions/transit-method.md) | `output/pdf/transit-method.pdf` |
| Occulting Masks: Background Suppression and Target Detectability | April 2022 | [LaTeX](content/coronagraph-contrast.tex) | [Read](companions/coronagraph-contrast.md) | `output/pdf/coronagraph-contrast.pdf` |

## Data, analysis and literature

All 58 example datasets contribute to the figures and calculations. The [manifest](manifest.json) keeps forty-three source records in `analysis_sources` and maps their ownership to the twenty-one canonical `papers` through `analysis_ids`. Each source retains its primary data, related comparisons and historical context. [Acquisition details](implementation-notes.md) record conventions and implementation constraints outside the articles. The example datasets remain unchanged.

[`prepare_examples.py`](prepare_examples.py) reproduces the original reductions. [`prepare_drafts.py`](prepare_drafts.py) prepares the new figures and supplementary analyses. [Original results](example-analysis.json), [new companion results](draft-analysis.json) and [supplementary results](revision-analysis.json) record analysis methods, windows, units and numerical values. Independent acquisition paths retain their own time coordinates.

The [topic literature reviews](research/README.md) document the expanded research for every paper: search questions, primary sources read, selected references and reasons for excluding less useful material. The [earlier literature review](literature-review.md) remains available as background. The shared [bibliography](references.bib) contains the selected and historical entries; each article prints only its own citations.

## Build and verify

Required: Python 3.11+, PyMuPDF, `latexmk`, `pdflatex`, BibTeX and Poppler (`pdfinfo`, plus `pdftoppm` for visual review). TeX Live needs IEEEtran, Latin Modern, AMS math, booktabs, siunitx, TikZ, PGFPlots, microtype, hyperref, geometry, adjustbox, fancyhdr, longtable, flafter and xurl. The analysis uses only the Python standard library; PyMuPDF assembles and numbers the collection while preserving vector content and links. Install the paper extra in the project's virtual environment with `python -m pip install -e '.[papers]'`. Once dependencies are installed, builds need no network access or shell escape.

```sh
# Recreate analysis tables and plot definitions after changing data or analysis:
python3 docs/papers/prepare_examples.py
python3 docs/papers/prepare_drafts.py
make check-papers
make papers

# Build one final standalone paper (former source IDs also resolve to its topic):
python3 docs/papers/build.py --only transit-method

# Reassemble the current standalone proofs with the retrospective front matter:
make retrospective
make check-retrospective
```

The full analysis source archive includes the twenty-one canonical articles and Markdown companions, all 58 example CSVs, their metadata and generators, analysis modules, prepared plot tables, figures, bibliography and acquisition definitions. Superseded full manuscripts are excluded. Portable navigation and the per-device companion redirects are included. Extract it, install PyMuPDF in a virtual environment, and run:

```sh
python3 prepare_examples.py --check
python3 prepare_drafts.py --check
python3 build.py --output ./pdf
# Or compile a single article directly:
latexmk -pdf -interaction=nonstopmode -halt-on-error transit-method.tex
```

`check-papers` verifies unique topic ownership of all source investigations,
experiment and data coverage, reproducible analyses, bibliography keys, declared
plot inputs and canonical companions.
The build rejects undefined references, missing glyphs, oversized floats and
overfull boxes. It first verifies each arXiv proof, preparing missing or stale
packages, then assembles the final papers and retrospective. It produces
individual PDFs, source and PDF archives, and JSON summaries of page counts,
pagination and links. Length limits
are recorded per article: up to three times its prior single-paper baseline for
a consolidation and up to 1.5 times for a retained paper. The build checks those
limits without treating them as targets. Known superseded PDFs move to
`output/pdf/retired/` only after a successful full build. Visual review remains
necessary for diagram labels, legends and page balance.

Project checks:

```sh
make lint
make validate
make check-generated
TMPDIR=/private/tmp make security
```

## Attribution and historical context

The core experiment software was developed by Gautier Creutzer and Frédéric Bouquet, with revisions by Spicker and Bouquet. Those credits remain in [the source attribution](../../src/phyphox/README.md).

The source registry retains the research contexts: the September 2020 star-formation workshop, the January 2022 Mission to Mars publication, the July 2022 Arduino–phyphox project, the October 2022 astro-lab programme paper and the March 2024 transit paper. Bibliographic entries preserve the original publications’ authorship.

The original acquisition code is retained in repository snapshot `0a5cf6f`.
Firmware is unchanged; the revised experiment definitions
have a separate current snapshot. Documentation remains under the repository’s
GPL-3.0 terms.
