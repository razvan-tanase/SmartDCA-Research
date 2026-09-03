# Thesis manuscript build

This directory contains the authoritative thesis source, the implemented
official-template layer, the thesis architecture and evidence controls, and the
fail-closed submission gate. The current PDF is a complete structural shell,
not a submission candidate and not continuous chapter prose.

## Authority

- [`contract/institutional-contract.md`](contract/institutional-contract.md)
  freezes verified requirements, provenance, and owned unresolved decisions.
- [`contract/requirements.json`](contract/requirements.json) is the
  machine-readable release contract.
- The retained [official faculty thesis
  template](../references/institutional/acs-official-thesis-template-2018.pdf)
  governs covers, front matter, layout recommendations, and manuscript
  guidance; current university rules govern newer identity and declaration
  requirements.
- [`source/thesis.tex`](source/thesis.tex) is the authoritative manuscript
  source.
- [`controls/`](controls/README.md) governs the three-question manuscript
  spine, chapter and appendix route, contribution and non-claim boundaries,
  claim-to-evidence mapping, notation, generated assets, feedback, and release
  transitions.
- [`bibliography/references.bib`](bibliography/references.bib) is the
  bibliography input.
- [`generated/asset-placeholder.tex`](generated/asset-placeholder.tex) proves
  the generated-asset seam while remaining visibly non-releasable.

## Draft build

The direct build and focused test require Python 3.12, `latexmk`, pdfLaTeX,
BibTeX, `pdftotext`, `pdfinfo`, and the standard LaTeX packages named in the
source. The two PDF inspection commands are supplied by Poppler:

```bash
python manuscript/build.py
```

The derived PDF is written to `manuscript/build/thesis.pdf`. It implements the
template's bilingual cover/front-matter route, A4/25.4 mm layout, body spacing,
and heading hierarchy. It renders all ten planned body chapters and five
appendices with their purpose, prerequisites, reader outcome, and placement
boundary. Before LaTeX starts, the build runs the architecture/evidence control
check and fails on an invalid package. A successful draft build does not imply
submission readiness.

Run the control check directly with:

```bash
python manuscript/check_controls.py
```

## Clean-environment build

With Docker available, one command builds the dated Debian/TeX environment and
renders the same source without relying on a local TeX installation:

```bash
./manuscript/build-clean.sh
```

The container starts from the dated official Debian image declared in
[`environment/Dockerfile`](environment/Dockerfile), installs only the declared
build packages, mounts the repository source, and writes the derived PDF to the
same ignored build directory. GitHub Actions executes this route from a clean
runner.

## Submission gate

```bash
python manuscript/check_release.py
```

The checker rejects a candidate when a blocking institutional requirement is
not release-ready, an authoritative claim lacks provenance, the narrative and
machine-readable contracts are out of sync, a required build input is missing,
a declared placeholder marker remains, a LaTeX citation has no bibliography
entry, a bibliography entry is never cited, or the thesis architecture and
evidence controls are invalid. Failure remains expected while the owned
institutional decisions and visible placeholders are unresolved.

## Focused verification

```bash
python -m unittest manuscript.tests.test_controls
python -m unittest manuscript.tests.test_release_check
python -m unittest manuscript.tests.test_manuscript_build
python manuscript/check_controls.py
python tools/check_markdown_links.py .
```
