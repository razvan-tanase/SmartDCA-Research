# SmartDCA Research

A proof-first research project auditing and extending the out quasi-Gini construction in *SmartDCA superiority* (Calvet, Herranz-Celotti, and Valimamode, arXiv:2308.05200v1).

The project currently establishes:

- the exact failure boundary of the source paper's Eq. (70);
- a canonical numerator-preserving corrected out quasi-Gini mean, conservatively identified as a weighted Bajraktarević mean rather than a new mean class;
- the causal, fully funded boundary showing that universal DCA dominance forces DCA itself;
- a sharp epsilon-DCA unit-coverage guardrail; and
- a bounded, causal corrected-mean score inside that guardrail, with exact cash, unit, terminal-wealth, and acquisition-cost accounting.

No result currently claims that the non-DCA rule strictly outperforms DCA without an explicit path or stochastic criterion.

## Current frontier

Tickets 01–10 are resolved. Ticket 11, [Characterize the two-purchase DCA win/loss boundary](.scratch/smartdca/issues/11-characterize-two-purchase-dca-win-loss-boundary.md), is open and unclaimed pending the ticket-10 significance gate.

The authoritative project state is the [Wayfinder map](.scratch/smartdca/map.md).

## Repository layout

| Path | Purpose |
|---|---|
| `.scratch/smartdca/` | Authoritative Wayfinder map and numbered research tickets. |
| `research/notes/` | Detailed proofs, theorem notes, and primary-source positioning. |
| `research/prototypes/` | Preserved exploratory artifacts. |
| `reproducibility/checks/` | Deterministic and exhaustive verification programs. |
| `references/` | Source material used by the project. |
| `CONTEXT.md` | Canonical domain glossary and language constraints. |
| `docs/agents/` | Agent-facing tracker, workflow, and domain-consumption rules. |
| `docs/adr/` | Durable repository and research-process decisions. |

The separation is intentional: tickets record questions and concise resolutions, research notes hold detailed reasoning once, and executable checks provide reproducible evidence.

## Verification

The current checks use only the Python standard library:

```bash
python reproducibility/checks/check_pathwise_dca_dominance.py
python reproducibility/checks/check_corrected_out_quasi_gini_homogeneity.py
python reproducibility/checks/check_epsilon_dca_safety_guardrail.py
python reproducibility/checks/check_guarded_corrected_mean_smartdca.py
```

GitHub Actions runs all four checks on every push and pull request.

## Research workflow

Before advancing the project, read `AGENTS.md`, `CONTEXT.md`, the map, and the [Wayfinder ticket workflow](docs/agents/wayfinder-ticket-workflow.md). Work on one claimed ticket at a time, preserve evidence and review findings, and stop at the user significance gate before claiming the next ticket.

## Source

The preserved source paper is [2308.05200v1.pdf](references/2308.05200v1.pdf). The corresponding arXiv record is <https://arxiv.org/abs/2308.05200>.
