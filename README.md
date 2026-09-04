# SmartDCA Research

A proof-first research project auditing and extending the out quasi-Gini construction in *SmartDCA superiority* (Calvet, Herranz-Celotti, and Valimamode, arXiv:2308.05200v1).

The project currently establishes nine theorems and two constructions, each with its own canonical page:

- [the exact mean classification](research/theorems/source-out-functional-mean-classification.md) of the source paper's Eq. (70);
- [the corrected out quasi-Gini mean](research/definitions/corrected-out-quasi-gini-mean.md), conservatively identified as a weighted Bajraktarević mean rather than a new mean class;
- [its homogeneity characterization](research/theorems/corrected-mean-homogeneity-characterization.md), which shows scale invariance and transform novelty cannot be had at once;
- [the causal DCA dominance impossibility](research/theorems/causal-dca-dominance-impossibility.md), showing universal dominance forces DCA itself;
- [the sharp epsilon-DCA unit-coverage guardrail](research/theorems/epsilon-dca-safety-unit-guardrail.md);
- [the guarded corrected-mean SmartDCA rule](research/definitions/guarded-corrected-mean-smartdca-rule.md) inside that guardrail, with exact cash, unit, terminal-wealth, and acquisition-cost accounting;
- [the exact two-purchase DCA boundary](research/theorems/two-purchase-guarded-smartdca-boundary.md), including the score's sharp comparison with a neutral selector;
- [the exact three-purchase beta-sensitive boundary](research/theorems/three-purchase-corrected-mean-effect.md), including a countercyclical path on which changing only beta flips a DCA loss into a win;
- [the arbitrary-horizon cash-timing identity](research/theorems/arbitrary-horizon-cash-timing-identity.md), which decomposes every fully funded strategy's terminal-wealth gap into exact coefficients on carried cash;
- [the reference-aligned cash single-crossing theorem](research/theorems/reference-aligned-guardrail-cash-single-crossing.md), including the exact way policy-specific floors can defeat the unqualified mechanism; and
- [the exact arbitrary-horizon terminal-inventory boundary](research/theorems/arbitrary-horizon-performance-boundary.md), which classifies every realized corrected-rule gap against DCA and the neutral selector from terminal cash, terminal units, and the common evaluation price.

The finite examples prove that both strict-win and strict-loss regions are
nonempty. The arbitrary-horizon result is an exact ledger-conditioned
classification, not a universal or stochastic outperformance claim.

## Thesis-facing result

The research began with the ambition of making DCA adaptive while retaining a
universal superiority guarantee. Fair same-deposit accounting showed why that
ambition fails: under causal, fully funded, long-only trading, exact pathwise
dominance forces the strategy to be DCA itself. The project therefore pivoted
from guaranteed superiority to guaranteed safety and proved the sharp
epsilon-DCA unit guardrail, which reserves a protected DCA allocation while
leaving a funded interval for the corrected-mean score.

The arbitrary-horizon investigation then asked whether a realistic
single-valley investment cycle was enough to make that adaptive allocation
predictably beneficial. It is not. The accepted result is sharper: for every
finite realized purchase path, the corrected rule's terminal-wealth gap
against DCA or the neutral guarded selector is exactly
\(H+P U\), where \(H\) is its terminal cash difference, \(U\) its terminal
unit difference, and \(P\) the common evaluation price. This advances the work
by cleanly separating the model-free safety guarantee supplied by the floor
from the path-dependent performance of the adaptive score, and it gives the
later empirical study an auditable boundary to measure rather than a vague
superiority claim. The [canonical theorem](research/theorems/arbitrary-horizon-performance-boundary.md)
links the complete proof, exact witnesses, executable checks, and independent
publication review.

## Current frontier

The independently reviewed arbitrary-horizon checkpoint and the immutable
primary [confirmatory historical
run](reports/experiments/confirmatory-historical-evaluation.md) are complete.
Across all 18 non-unit primary frictionless historical cells, corrected guarded
had a negative median gap against DCA; nine H1 cells were Holm-significant in
the negative direction, while no signal-only H2 cell was Holm-significant. The
linked [audit note](research/notes/confirmatory-historical-evaluation-audit.md)
preserves the run identity, evidence, independent domain review, and claim
limits. The separately identified registered robustness run is also complete:
all 30 monthly robustness-coverage and all 48 quarterly non-unit frictionless
complete-system medians were negative, while the quarterly signal-only rows
had 40 negative and eight positive medians. Those post-confirmatory results are
descriptive, do not change H1/H2, and retain the primary run unchanged. Ticket
05 passed independent domain, Standards, and specification review. The
independently reviewed [cross-layer
synthesis](reports/experiments/safety-adaptivity-tradeoff-synthesis.md) now
joins 2,754 reviewed deterministic, stochastic, and historical aggregate cells
without pooling their inferential units. It supports a proved frictionless
safety floor but no universal, optimal, or confirmed incremental superiority
claim for the corrected-mean signal. The final [independent empirical-package
review](research/notes/safety-adaptivity-empirical-package-review.md)
regenerated the accepted deterministic study and synthesis, reproduced a
383-episode historical slice from retained inputs, and reconciled all 54
primary/architecture historical aggregates and all 36 registered bootstrap
and Holm cells. The empirical effort is complete with no publication blocker;
the [retained private-pass
receipt](reports/experiments/runs/smartdca-empirical-package-review-v1-6cb6c1cd94b901be90ebd553a022c922e53984afafeb22948747be084b37c14f/review-receipt.json)
keeps the final review reproducible without publishing provider observations.
Thesis manuscript tickets 01--09 are now resolved: the institutional contract, canonical build, thesis architecture, and evidence controls are frozen; Chapter 2 has reviewed investment, mean-theory, and computational-method synthesis; Chapter 3 establishes the fair same-deposit model and corrected-signal foundations; Chapter 4 with Appendix A carries the reviewed causal impossibility theorem, sharp epsilon-DCA guardrail, and complete guarded policy; Chapter 5 with Appendix B gives the reviewed finite witnesses, arbitrary-horizon accounting, qualified cash-crossing mechanism, and exact realized-ledger boundary; and Chapter 6 with Appendices C--D now defines the frozen empirical design, inference limits, provenance model, versioned artifact lifecycle, and reproduction routes. Tickets 10 and 11 are the parallel unblocked drafting frontiers. The [effort
map](.scratch/smartdca/efforts/thesis-manuscript-assembly/map.md)
and [project map](.scratch/smartdca/map.md) record the completed state and next
frontier.

## Repository map

| Path | Authoritative content |
|---|---|
| `.scratch/smartdca/` | Optional tracked efforts, maps, and numbered research tickets. |
| `.agents/` | Repository-local agent skills and tooling. |
| `research/definitions/` | Canonical definitions of the constructions the project adopts. |
| `research/theorems/` | Canonical statements of the results the project has proved. |
| `research/notes/` | Detailed proofs, theorem notes, and primary-source positioning behind those canonical pages. |
| `research/prototypes/` | Preserved exploratory artifacts. |
| `experiments/` | Immutable empirical protocols and versioned runner inputs. |
| `reports/experiments/` | Reviewable experiment reports and fingerprinted canonical run bundles. |
| `reproducibility/checks/` | Deterministic and exhaustive verification programs. |
| `references/` | Preserved source material and its research-facing summary. |
| `manuscript/` | Authoritative thesis source, institutional contract, bibliography, build, and fail-closed release check. |
| `CONTEXT.md` | Canonical domain glossary and language constraints. |
| `docs/agents/` | Optional work-tracking workflow. |
| `docs/adr/` | Durable repository and research-process decisions. |
| `tools/` | Small repository checks with no third-party dependencies. |

The separation is intentional, and its reasons are recorded in [Keep research
state and evidence in separate versioned layers](docs/adr/0001-versioned-research-layout.md):
tracked work records questions and concise resolutions, research notes hold
detailed reasoning once, and executable checks provide reproducible evidence.
The [empirical artifact-layer decision](docs/adr/0008-place-empirical-protocol-input-run-layers.md)
extends that split to immutable protocols, versioned inputs, deterministic run
bundles, and their narrative reports. Definitions and theorem pages state the
results; their linked notes carry the arguments.

## Verification

The link and scientific checks use only the Python standard library. The
manuscript build and rendered-PDF test additionally use the declared TeX and
Poppler tools documented in [`manuscript/README.md`](manuscript/README.md):

```bash
python -m unittest tools.test_check_markdown_links
python tools/check_markdown_links.py .
python reproducibility/checks/check_pathwise_dca_dominance.py
python reproducibility/checks/check_corrected_out_quasi_gini_homogeneity.py
python reproducibility/checks/check_epsilon_dca_safety_guardrail.py
python reproducibility/checks/check_guarded_corrected_mean_smartdca.py
python reproducibility/checks/check_two_purchase_dca_win_loss_boundary.py
python reproducibility/checks/check_three_purchase_corrected_mean_effect.py
python -m reproducibility.checks.check_arbitrary_horizon_accounting_verification
python -m reproducibility.checks.check_weak_single_valley_falsification
python -m reproducibility.checks.check_cash_single_crossing_mechanism
python -m reproducibility.checks.check_arbitrary_horizon_performance_boundary
python reproducibility/checks/check_arbitrary_horizon_publication_review.py
python -m unittest reproducibility.checks.check_empirical_protocol_canonical_run
python -m unittest reproducibility.checks.check_deterministic_adversarial_study
python -m unittest reproducibility.checks.check_stochastic_family_study
python -m unittest reproducibility.checks.check_historical_data_episode_seam
python -m unittest reproducibility.checks.check_historical_confirmatory_evaluation
python -m unittest reproducibility.checks.check_historical_robustness_evaluation
python -m unittest reproducibility.checks.check_safety_adaptivity_synthesis
python -m unittest reproducibility.checks.check_empirical_package_publication_review
python -m unittest reproducibility.checks.check_financial_model_corrected_signal_foundations
python -m unittest reproducibility.checks.check_impossibility_safety_policy_architecture
python -m unittest reproducibility.checks.check_finite_arbitrary_horizon_boundaries
python -m unittest reproducibility.checks.check_empirical_methodology_reproducibility
python -m unittest reproducibility.checks.check_deterministic_stochastic_evaluation
python -m unittest reproducibility.checks.check_dca_literature_synthesis
python -m unittest reproducibility.checks.check_corrected_mean_literature_synthesis
python -m unittest reproducibility.checks.check_computational_finance_statistics_literature_synthesis
python -m unittest manuscript.tests.test_controls
python -m unittest manuscript.tests.test_release_check
python -m unittest manuscript.tests.test_manuscript_build
python manuscript/check_controls.py
python manuscript/build.py
```

GitHub Actions runs the link check and the manuscript
control/build/release tests on every push and pull request. The twenty-six
scientific checks remain in the separate [Reproducibility workflow](.github/workflows/reproducibility.yml):
it runs automatically only when `research/`, `reproducibility/`,
`experiments/`, or `reports/` changes (or when its workflow file changes) and
can also be started manually. Manuscript-only changes therefore do not invoke the
scientific suite. The controlled partial draft is intentionally not a submission
candidate: `python manuscript/check_release.py` must exit with status 1 while
the owned institutional and supervisor decisions in the [manuscript
contract](manuscript/contract/institutional-contract.md) remain unresolved.

The command catalog above is the repository-wide/release suite, not the
default for every bounded ticket. Local agents mirror the workflow split in
[`AGENTS.md`](AGENTS.md); manuscript work can use the focused
[single-process Homebrew helper](manuscript/README.md#managed-macos-agent-sandboxes)
when managed sandboxing would otherwise hide TeX or Poppler between calls.

Authorized Yahoo Finance acquisition is a separate, pinned input-production
step rather than a test dependency. Create its CPython 3.12 environment with
`python3.12 -m venv .venv` and
`.venv/bin/python -m pip install -r requirements-historical.txt`, then follow
the fail-closed acquisition and offline-preparation commands in the
[historical seam report](reports/experiments/historical-data-episode-seam.md).
The final [publication review](research/notes/safety-adaptivity-empirical-package-review.md)
documents the single clean-environment route that regenerates the public
deterministic and synthesis evidence and, when the receipt-bound private paths
are present, independently replays the historical slice and registered
inference without redistributing source observations.

## Research workflow

For agent execution, the [agent contract](AGENTS.md) routes each change to its
authoritative context and completion gates. It discloses [work
tracking](docs/agents/work-tracking.md) only for explicitly tracked or
multi-stage research.

## Source

The preserved source paper is [2308.05200v1.pdf](references/2308.05200v1.pdf),
with provenance, fingerprint, and scope recorded in [its source
summary](references/summaries/smartdca-superiority-source-paper.md). The
corresponding arXiv record is <https://arxiv.org/abs/2308.05200v1>.
