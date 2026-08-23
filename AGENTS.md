---
profile: smartdca-okf/0.3
type: agent-instructions
title: "Agent contract"
description: "Root invariant contract every agent reads before changing SmartDCA work or knowledge."
knowledge_role: operational
status: stable
original_record: true
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-23T16:18:42Z
generation_run: urn:uuid:fc39df1d-3e43-487c-8bc6-9a1e72abaff8
verified:
  - by: openai-codex/smartdca-wiki-0.1
    at: 2026-08-23T16:21:37Z
    review_run: urn:uuid:66222a92-a082-4617-b191-77c124239e73
---
# Agent contract

Select every branch that matches the change:

- **Ticket work:** follow the [Wayfinder ticket workflow](docs/agents/wayfinder-ticket-workflow.md). It governs orientation, one-ticket claiming, execution, review, synchronization, persistence, and the user significance gate.
- **Domain work:** follow [Domain documentation](docs/agents/domain.md) when terminology, assumptions, the mathematical or financial model, or an ADR may change.
- **Knowledge work:** follow the [LLM-Wiki workflow](docs/agents/llm-wiki-workflow.md) and its normative [SmartDCA OKF profile](docs/knowledge/okf-profile.md) when a concept, path, metadata field, provenance join, lifecycle state, index row, or log event changes.
- **Scientific work:** link every changed claim to its evidence under `research/notes/` and run the corresponding scripts under `reproducibility/checks/`.

Keep each kind of information in its authoritative layer:

| Layer | Authoritative home |
|---|---|
| Work state and resolution | `.scratch/smartdca/` |
| Canonical terminology and results | `CONTEXT.md`, `research/definitions/`, `research/theorems/` |
| Detailed reasoning and executable evidence | `research/notes/`, `reproducibility/checks/` |
| Agent procedure and knowledge policy | `docs/agents/`, `docs/knowledge/okf-profile.md` |

Preserve published Concept IDs, immutable external-source bytes, claim-level provenance, and a semantic review run distinct from generation where the profile requires one. Treat structural CI as conformance evidence, not semantic approval.

**Publishable when:** the current ticket and map agree, every changed concept passes the LLM-Wiki publish gate, every changed scientific claim passes its linked checks, and no result depends on hidden conversation context.
