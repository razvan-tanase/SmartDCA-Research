---
profile: smartdca-okf/0.3
type: agent-instructions
title: "Agent contract"
description: "Root invariant contract every agent reads before changing SmartDCA work or knowledge."
knowledge_role: operational
status: stable
original_record: true
generated:
  by: claude-code/smartdca-wiki-0.1
  at: 2026-08-16T07:40:00Z
generation_run: urn:uuid:e52c437c-4218-43bd-a25e-5b1e3f1a0d24
---
# Agent contract

- Before changing SmartDCA work, read `.scratch/smartdca/map.md`, the claimed ticket, `CONTEXT.md`, and [the Wayfinder ticket workflow](docs/agents/wayfinder-ticket-workflow.md). Claim and resolve exactly one ticket at a time.
- Before creating, moving, ingesting, reviewing, or changing the lifecycle of knowledge, follow the [SmartDCA OKF profile](docs/knowledge/okf-profile.md) and [LLM-Wiki workflow](docs/agents/llm-wiki-workflow.md).
- Preserve the separation between ticket state, detailed reasoning, executable evidence, and canonical knowledge. Do not overload type, role, lifecycle, trust, or workflow state.
- Preserve published Concept IDs, immutable external-source bytes, claim provenance, and independent review boundaries. Structural CI is not semantic review.
- Run `python -m unittest tools.okf.tests.test_validate_cli` and `python tools/okf/validate.py . --strict` for knowledge-system changes. Strict validation blocks CI, so every Markdown concept must conform before merging; drop `--strict` only while iterating.
- For proof, theorem, score-definition, or accounting changes, run the linked check under `reproducibility/checks/`, then every scientific check before publishing.
