# Thesis manuscript build

This directory contains the authoritative thesis source, the implemented
official-template layer, the thesis architecture and evidence controls, and the
fail-closed submission gate. The current PDF is a complete integrated draft:
Chapter 2 supplies the reviewed literature positioning; Chapter 3 supplies the
financial-model and corrected-signal foundations; Chapter 4 supplies the
impossibility-to-safety policy architecture; Chapter 5 supplies the finite- and
arbitrary-horizon realized performance boundaries; Chapter 6 fixes the frozen
empirical design, inferential limits, and reproduction route; Chapter 7 reports
the reviewed deterministic and seeded-stochastic evaluation; Chapter 8 reports
the primary historical and separately registered robustness evaluation;
Chapter 9 integrates the safety-adaptivity finding, contributions, limitations,
and future-research boundary; and Appendices A--E retain detailed proofs,
cases, protocols, artifact identities, generated result tables, and clean
commands. The introduction, closing literature synthesis, conclusion, and
English abstract now connect those results through the approved research
questions and contribution boundaries. The current source follows the
candidate's requested English-only front matter: one English cover and one
English abstract. The retained institutional contract still records the
template's bilingual route, verified long-form institution identity, and
unresolved current-brand evidence. The attached-reference cover intentionally
uses its shorter institution line and supplied brand marks; that presentation
choice remains subject to supervisor/faculty confirmation and stays a release
blocker until confirmed. The reproducible package command below assembles its
source, PDF, evidence map, and supervisor brief. Ticket 14 remains open because
its institutional
acceptance criteria are not met; this draft is not a review-candidate or
submission candidate.

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
- [`generated/`](generated/) contains the policy diagram and reproducible
  deterministic, stochastic, primary-historical, and robustness tables and
  figures. The quantitative assets are regenerated from accepted immutable run
  bundles by
  [`reproducibility/synthetic_evaluation_assets.py`](../reproducibility/synthetic_evaluation_assets.py)
  and
  [`reproducibility/historical_evaluation_assets.py`](../reproducibility/historical_evaluation_assets.py).

Generated tables use unscaled 9-point type, content-specific column widths,
bold aligned headings, and spaced rows. The presentation-only width registry
in [`reproducibility/manuscript_table_layout.py`](../reproducibility/manuscript_table_layout.py)
is applied by both asset generators; change it and regenerate the fragments
instead of editing generated TeX. Table captions and rules are styled in the
thesis preamble. Check the rendered pages as well as the warning-free build
when changing a layout, and preserve the accepted data and captions.

## Draft build

Identity-bound empirical regeneration and the supported focused suite require
CPython 3.12. The manuscript control and rendering scripts themselves require
a compatible Python 3, `latexmk`, pdfLaTeX, BibTeX, `pdftotext`, `pdftohtml`,
`pdfinfo`, and the standard LaTeX packages named in the source. The dated
Docker route uses Debian Bookworm's distribution `python3` only for manuscript
validation and rendering; it does not regenerate empirical identities. The
three PDF inspection commands are supplied by Poppler:

```bash
python manuscript/build.py
```

The derived PDF is written to `manuscript/build/thesis.pdf`. It implements the
current English-only cover/front-matter route requested for this draft, A4/25.4
mm layout, body spacing, and heading hierarchy. It renders all ten completed
body chapters and five appendices. Before LaTeX starts, the build runs the
architecture/evidence control
check and the DCA/adaptive/causal-safety, corrected-mean prior-theory, and
reproducible computational-finance/statistical-method literature traceability
checks, followed by the financial-model/corrected-signal and
impossibility-to-safety policy audits, and fails on an invalid package. A
successful draft build does not imply submission readiness. The build also
runs the finite/arbitrary-horizon boundary, empirical-methodology,
deterministic/stochastic evaluation, and historical/robustness evaluation
audits before LaTeX so scope, notation, evidence mappings, Appendices B--E,
generated result assets, frozen protocol identities, and private/public
boundaries cannot drift independently.

Run the control check directly with:

```bash
python manuscript/check_controls.py
```

## Portable LaTeX editor project

For an editor such as Overleaf, export a complete uploadable project:

```bash
python manuscript/export_latex.py
```

Upload `manuscript/build/smartdca-thesis-latex.zip` as a new project, select
`thesis.tex` as the main document, and use pdfLaTeX. The ZIP contains the cover
images, all nine included TeX fragments, and the bibliography. Paths are
relocated only in the exported thesis; the retained inputs remain unchanged.
The Verification workflow also provides the ZIP as the
`smartdca-thesis-latex` artifact.

Downloading only `source/thesis.tex` or `source/` is insufficient: it omits
the sibling `generated/` and `bibliography/` directories. This causes
`File '../generated/policy-architecture.tex' not found` and interrupts the
first LaTeX pass, leaving citations and cross-references unresolved.

For a local build of the extracted ZIP, run `latexmk -pdf -bibtex thesis.tex`
from the extracted directory. The same command works from `manuscript/source/`
in a complete checkout: its `latexmkrc` supplies an absolute bibliography search
path, including when output goes to another directory. In the extracted ZIP,
without latexmk, run `pdflatex thesis.tex`,
`bibtex thesis`, and then `pdflatex thesis.tex` twice. The first pass may report
undefined references; inspect the final pass after BibTeX and the reruns.
If an editor retains auxiliary files from the failed upload, recompile from
scratch after uploading the complete project.

The portable project is a derived editing convenience. Use the canonical
Python build for evidence validation and the integrated review package below
for provenance and submission-gate results.

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

## Integrated review package

From a clean checkout, one command assembles the complete package:

```bash
./manuscript/assemble-clean.sh
```

With the declared TeX/Poppler tools already installed, use:

```bash
python manuscript/assemble.py
```

Both routes run the canonical build, regenerate and compare all eight empirical
fragments, audit display ownership and rendered references, and write a
content-addressed ZIP below `manuscript/build/packages/`. The ZIP contains the
PDF, a complete public source snapshot, bibliography, generated assets,
controls, a claim-to-evidence CSV with printed pages, assembly audit,
[supervisor review brief](release/supervisor-review.md), institutional blocker
list, and manifest. Every payload file is hashed. Private provider observations
are excluded because they are not versioned repository inputs.

The state is **integrated-draft**. Assembly success does not approve the
submission gate, resolve ticket 14, or advance tickets 15–17. The package
records the submission checker verdict and retains all missing personal,
institutional, and supervisor evidence. See the
[assembly audit](../research/notes/complete-manuscript-assembly-audit.md).

New files must be staged before assembling a working checkout: the inventory
uses tracked paths and hashes their actual working bytes and executable modes, recording HEAD and
whether the checkout is modified. An exported package uses its bound
`SOURCE-FILES.json` and can rebuild without Git history. A relocated export
reproduces identical PDF and ZIP bytes under the same toolchain. The dated
Docker image installs distribution packages whose versions may evolve; the
manifest records actual versions, and cross-toolchain byte identity is not
assumed. Full scientific verification remains a separate required release
gate documented in the root README; ordinary package assembly reconciles
accepted outputs without rerunning every experiment.

Run the assembly seam independently:

```bash
python manuscript/assembly_controls.py --build-dir manuscript/build
python -m unittest manuscript.tests.test_assembly
```

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
institutional decisions and front-matter placeholders are unresolved.

## Focused verification

```bash
python -m unittest manuscript.tests.test_assembly
python -m unittest manuscript.tests.test_controls
python -m unittest manuscript.tests.test_release_check
python -m unittest manuscript.tests.test_manuscript_build
python -m unittest reproducibility.checks.check_financial_model_corrected_signal_foundations
python -m unittest reproducibility.checks.check_impossibility_safety_policy_architecture
python -m unittest reproducibility.checks.check_finite_arbitrary_horizon_boundaries
python -m unittest reproducibility.checks.check_empirical_methodology_reproducibility
python -m unittest reproducibility.checks.check_deterministic_stochastic_evaluation
python -m unittest reproducibility.checks.check_historical_robustness_manuscript
python -m unittest reproducibility.checks.check_dca_literature_synthesis
python -m unittest reproducibility.checks.check_corrected_mean_literature_synthesis
python -m unittest reproducibility.checks.check_computational_finance_statistics_literature_synthesis
python reproducibility/checks/check_pathwise_dca_dominance.py
python reproducibility/checks/check_epsilon_dca_safety_guardrail.py
python reproducibility/checks/check_guarded_corrected_mean_smartdca.py
python reproducibility/checks/check_two_purchase_dca_win_loss_boundary.py
python reproducibility/checks/check_three_purchase_corrected_mean_effect.py
python -m reproducibility.checks.check_arbitrary_horizon_accounting_verification
python -m reproducibility.checks.check_weak_single_valley_falsification
python -m reproducibility.checks.check_cash_single_crossing_mechanism
python -m reproducibility.checks.check_arbitrary_horizon_performance_boundary
python reproducibility/checks/check_arbitrary_horizon_publication_review.py
python manuscript/check_controls.py
python tools/check_markdown_links.py .
```

## Managed macOS agent sandboxes

Some managed agent sandboxes allow an approved Homebrew installation but do
not expose its `/opt` changes to a later tool call. Keep dependency installation
and the focused manuscript checks in one approved process:

```bash
./manuscript/verify-homebrew.sh
./manuscript/verify-homebrew.sh --build
```

The helper installs Homebrew's CPython 3.12, TeX Live, and Poppler, then runs
the link, manuscript control/build/release, literature, foundation,
impossibility-to-safety, performance-boundary, empirical-methodology, directly
intersecting scientific, and rendered-PDF checks listed above. In these
sandboxes, only the first process tree after
installation can still see the tools, so `--build` performs the canonical build
as a separate single-process invocation. Both modes require approval because
Homebrew writes outside the repository. Run additional scientific programs
only for the claims or artifacts reached by the ticket; use the complete
root-README suite for repository-wide or release work.
