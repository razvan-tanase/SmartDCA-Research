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

The independently reviewed arbitrary-horizon checkpoint is complete. The
approved [safety-adaptivity empirical effort](.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/spec.md)
is now active. Its first ticket—[preregister the protocol and establish a
canonical run](.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/issues/01-preregister-protocol-establish-canonical-run.md)—is
resolved after Standards, specification, and independent empirical review. The
confirmatory design is frozen before historical outcome access, and the
deterministic three-policy runner reproduces its canonical synthetic bundle
byte for byte. [Ticket 02's deterministic and adversarial study](.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/issues/02-evaluate-deterministic-adversarial-paths.md)
is also resolved after Standards, specification, and independent empirical
replay. [Ticket 03's seeded stochastic study](.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/issues/03-evaluate-seeded-stochastic-families.md)
is resolved after independent review and byte-identical replay of all 90 paths,
3,240 ledgers, and 1,080 aggregate cells. Its mixed controlled results support
sensitivity analysis, not a superiority claim. The separate
[repository-conformance ticket](.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/issues/08-exclude-agents-from-okf-bundle.md)
is also resolved: profile 0.5 excludes unchanged `.agents/` tooling from the
declared knowledge-bundle view without claiming raw-repository OKF conformance.
Ticket 04 is the next open unclaimed tracer. The synthetic empirical reports
remain draft until the registered historical-slice reproduction is completed.

The authoritative project state is the [Wayfinder map](.scratch/smartdca/map.md). The complete inventory of every knowledge concept is the root [index](index.md).

## Repository layout

| Path | Purpose |
|---|---|
| `.scratch/smartdca/` | Authoritative Wayfinder map and numbered research tickets. |
| `.agents/` | Repository-local agent tooling outside SmartDCA knowledge-bundle membership and validation. |
| `research/definitions/` | Canonical definitions of the constructions the project adopts. |
| `research/theorems/` | Canonical statements of the results the project has proved. |
| `research/notes/` | Detailed proofs, theorem notes, and primary-source positioning behind those canonical pages. |
| `research/prototypes/` | Preserved exploratory artifacts. |
| `experiments/` | Immutable empirical protocols and versioned runner inputs. |
| `reports/experiments/` | Reviewable experiment reports and fingerprinted canonical run bundles. |
| `reproducibility/checks/` | Deterministic and exhaustive verification programs. |
| `references/` | Source material, immutable fingerprinted external snapshots under `raw/`, and their summaries under `summaries/`. |
| `research/synthesis/` | Cross-source integration and recorded conflict resolution. |
| `CONTEXT.md` | Canonical domain glossary and language constraints. |
| `docs/agents/` | Agent-facing tracker, workflow, and domain-consumption rules. |
| `docs/adr/` | Durable repository and research-process decisions. |
| `docs/knowledge/` | Normative knowledge-format profile for the repository bundle. |
| `index.md` | Complete role-aware inventory of every knowledge concept. |
| `log.md` | Immutable event history of the knowledge bundle. |

The separation is intentional, and its reasons are recorded in [Keep research state and evidence in separate versioned layers](docs/adr/0001-versioned-research-layout.md): tickets record questions and concise resolutions, research notes hold detailed reasoning once, and executable checks provide reproducible evidence. The [empirical artifact-layer decision](docs/adr/0008-place-empirical-protocol-input-run-layers.md) extends that split to immutable protocols, versioned inputs, deterministic run bundles, and their narrative reports. Since the semantic extraction, `research/definitions/` and `research/theorems/` carry the statements those notes prove, so a reader who wants a result reads the canonical page and a reader who wants the argument follows it into the note.

## Verification

The current checks use only the Python standard library:

```bash
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
```

GitHub Actions runs all fourteen checks on every push and pull request, together with the knowledge-system fixtures and strict [SmartDCA OKF](docs/knowledge/okf-profile.md) validation.

## Research workflow

Before advancing the project, read `AGENTS.md`, `CONTEXT.md`, the map, and the [Wayfinder ticket workflow](docs/agents/wayfinder-ticket-workflow.md). Work on one claimed ticket at a time, preserve evidence and review findings, and stop at the user significance gate before claiming the next ticket.

## Source

The preserved source paper is [2308.05200v1.pdf](references/2308.05200v1.pdf), fingerprinted and summarized as an ingested source in [its source summary](references/summaries/smartdca-superiority-source-paper.md). The corresponding arXiv record is <https://arxiv.org/abs/2308.05200>.
