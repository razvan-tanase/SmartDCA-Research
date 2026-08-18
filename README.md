---
profile: smartdca-okf/0.3
type: project-overview
title: "SmartDCA Research"
description: "Human introduction to the project, its established results, layout, and verification commands."
knowledge_role: canonical
status: stable
original_record: true
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-16T11:24:00Z
generation_run: urn:uuid:1d09cb3f-94ee-4b73-b0f2-393b4227167d
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T07:46:00Z
    review_run: urn:uuid:b5b1666e-e77c-41a4-8781-fb0d5a965582
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T07:46:00Z
    review_run: urn:uuid:da31a04e-0105-4659-9d05-895a4364b107
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T09:10:00Z
    review_run: urn:uuid:e26b6a0b-a55b-47f0-ae7f-88873e0ac8ab
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T09:48:00Z
    review_run: urn:uuid:3b0e6083-180e-43b5-9314-df22687e68de
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T10:34:00Z
    review_run: urn:uuid:86b3e187-d6a2-44c5-997c-8c06f5fdbf87
  - by: openai-codex/smartdca-wiki-0.1
    at: 2026-08-16T11:14:00Z
    review_run: urn:uuid:5fdc289a-b5ff-4e1f-9d84-777c58a093f2
  - by: openai-codex/smartdca-wiki-0.1
    at: 2026-08-16T11:30:00Z
    review_run: urn:uuid:d55d437b-21a4-4ffb-b393-de516fb58c2d
---
# SmartDCA Research

A proof-first research project auditing and extending the out quasi-Gini construction in *SmartDCA superiority* (Calvet, Herranz-Celotti, and Valimamode, arXiv:2308.05200v1).

The project currently establishes six theorems and two constructions, each with its own canonical page:

- [the exact mean classification](research/theorems/source-out-functional-mean-classification.md) of the source paper's Eq. (70);
- [the corrected out quasi-Gini mean](research/definitions/corrected-out-quasi-gini-mean.md), conservatively identified as a weighted Bajraktarević mean rather than a new mean class;
- [its homogeneity characterization](research/theorems/corrected-mean-homogeneity-characterization.md), which shows scale invariance and transform novelty cannot be had at once;
- [the causal DCA dominance impossibility](research/theorems/causal-dca-dominance-impossibility.md), showing universal dominance forces DCA itself;
- [the sharp epsilon-DCA unit-coverage guardrail](research/theorems/epsilon-dca-safety-unit-guardrail.md);
- [the guarded corrected-mean SmartDCA rule](research/definitions/guarded-corrected-mean-smartdca-rule.md) inside that guardrail, with exact cash, unit, terminal-wealth, and acquisition-cost accounting;
- [the exact two-purchase DCA boundary](research/theorems/two-purchase-guarded-smartdca-boundary.md), including the score's sharp comparison with a neutral selector; and
- [the exact three-purchase beta-sensitive boundary](research/theorems/three-purchase-corrected-mean-effect.md), including a countercyclical path on which changing only beta flips a DCA loss into a win.

The two- and three-purchase theorems give explicit realized-path criteria and
prove that both strict-win and strict-loss regions are nonempty. No result
claims universal, arbitrary-horizon, or stochastic outperformance.

## Current frontier

Tickets 01–18 are resolved. The latest mathematical result is
[Isolate the first nontrivial corrected-mean effect at three purchases](.scratch/smartdca/issues/18-isolate-three-purchase-corrected-mean-effect.md).
No next ticket is claimed pending its significance gate.

The authoritative project state is the [Wayfinder map](.scratch/smartdca/map.md). The complete inventory of every knowledge concept is the root [index](index.md).

## Repository layout

| Path | Purpose |
|---|---|
| `.scratch/smartdca/` | Authoritative Wayfinder map and numbered research tickets. |
| `research/definitions/` | Canonical definitions of the constructions the project adopts. |
| `research/theorems/` | Canonical statements of the results the project has proved. |
| `research/notes/` | Detailed proofs, theorem notes, and primary-source positioning behind those canonical pages. |
| `research/prototypes/` | Preserved exploratory artifacts. |
| `reproducibility/checks/` | Deterministic and exhaustive verification programs. |
| `references/` | Source material, immutable fingerprinted external snapshots under `raw/`, and their summaries under `summaries/`. |
| `research/synthesis/` | Cross-source integration and recorded conflict resolution. |
| `CONTEXT.md` | Canonical domain glossary and language constraints. |
| `docs/agents/` | Agent-facing tracker, workflow, and domain-consumption rules. |
| `docs/adr/` | Durable repository and research-process decisions. |
| `docs/knowledge/` | Normative knowledge-format profile for the repository bundle. |
| `index.md` | Complete role-aware inventory of every knowledge concept. |
| `log.md` | Immutable event history of the knowledge bundle. |

The separation is intentional, and its reasons are recorded in [Keep research state and evidence in separate versioned layers](docs/adr/0001-versioned-research-layout.md): tickets record questions and concise resolutions, research notes hold detailed reasoning once, and executable checks provide reproducible evidence. Since the semantic extraction, `research/definitions/` and `research/theorems/` carry the statements those notes prove, so a reader who wants a result reads the canonical page and a reader who wants the argument follows it into the note.

## Verification

The current checks use only the Python standard library:

```bash
python reproducibility/checks/check_pathwise_dca_dominance.py
python reproducibility/checks/check_corrected_out_quasi_gini_homogeneity.py
python reproducibility/checks/check_epsilon_dca_safety_guardrail.py
python reproducibility/checks/check_guarded_corrected_mean_smartdca.py
python reproducibility/checks/check_two_purchase_dca_win_loss_boundary.py
python reproducibility/checks/check_three_purchase_corrected_mean_effect.py
```

GitHub Actions runs all six checks on every push and pull request, together with the knowledge-system fixtures and strict [SmartDCA OKF](docs/knowledge/okf-profile.md) validation.

## Research workflow

Before advancing the project, read `AGENTS.md`, `CONTEXT.md`, the map, and the [Wayfinder ticket workflow](docs/agents/wayfinder-ticket-workflow.md). Work on one claimed ticket at a time, preserve evidence and review findings, and stop at the user significance gate before claiming the next ticket.

## Source

The preserved source paper is [2308.05200v1.pdf](references/2308.05200v1.pdf), fingerprinted and summarized as an ingested source in [its source summary](references/summaries/smartdca-superiority-source-paper.md). The corresponding arXiv record is <https://arxiv.org/abs/2308.05200>.
