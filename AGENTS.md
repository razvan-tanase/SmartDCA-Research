# Agent contract

- Before changing SmartDCA work, read `.scratch/smartdca/map.md`, the claimed ticket, `CONTEXT.md`, and [the Wayfinder ticket workflow](docs/agents/wayfinder-ticket-workflow.md). Claim and resolve exactly one ticket at a time.
- Before creating, moving, ingesting, reviewing, or changing the lifecycle of knowledge, follow the [SmartDCA OKF profile](docs/knowledge/okf-profile.md) and [LLM-Wiki workflow](docs/agents/llm-wiki-workflow.md).
- Preserve the separation between ticket state, detailed reasoning, executable evidence, and canonical knowledge. Do not overload type, role, lifecycle, trust, or workflow state.
- Preserve published Concept IDs, immutable external-source bytes, claim provenance, and independent review boundaries. Structural CI is not semantic review.
- Run `python -m unittest tools.okf.tests.test_validate_cli` and `python tools/okf/validate.py .` for knowledge-system changes. The validator remains report-only until the atomic migration ticket enables strict CI.
- For proof, theorem, score-definition, or accounting changes, run the linked check under `reproducibility/checks/`, then every scientific check before publishing.
