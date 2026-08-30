---
profile: smartdca-okf/0.5
type: agent-instructions
title: "Agent contract"
description: "Root invariant contract every agent reads before changing SmartDCA work or knowledge."
knowledge_role: operational
status: stable
original_record: true
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-30T09:57:10Z
generation_run: urn:uuid:eb95df4b-cddd-4d8f-987c-dca42e3ecc68
verified:
  - by: openai-codex/smartdca-wiki-0.1
    at: 2026-08-23T16:21:37Z
    review_run: urn:uuid:66222a92-a082-4617-b191-77c124239e73
  - by: openai-codex/standards-review-0.1
    at: 2026-08-23T20:30:00Z
    review_run: urn:uuid:e99ebedf-be97-4645-9ada-70efce93a3b2
---
# Agent contract

Select every branch that matches the change:

- **Ticket work:** follow the [Wayfinder ticket workflow](docs/agents/wayfinder-ticket-workflow.md). It governs orientation, one-ticket claiming, execution, review, synchronization, persistence, and the user significance gate.
- **Domain work:** follow [Domain documentation](docs/agents/domain.md) when terminology, assumptions, the mathematical or financial model, or an ADR may change.
- **Knowledge work:** follow the [LLM-Wiki workflow](docs/agents/llm-wiki-workflow.md) when bundle membership changes, or when creating or revising a bundle concept, its assigned path, metadata, provenance joins, lifecycle, index row, or log event. Its normative [SmartDCA OKF profile](docs/knowledge/okf-profile.md) defines the representation.
- **Scientific work:** link every changed claim to its evidence under `research/notes/` and run the corresponding scripts under `reproducibility/checks/`.

Keep each kind of information in its authoritative layer:

| Layer | Authoritative home |
|---|---|
| Project frontier | `.scratch/smartdca/map.md` |
| Effort contract and state | `.scratch/smartdca/efforts/<effort>/spec.md`, `map.md` |
| Ticket work and resolution | `.scratch/smartdca/efforts/<effort>/issues/`; resolved legacy history remains in `.scratch/smartdca/issues/` |
| Canonical terminology and results | `CONTEXT.md`, `research/definitions/`, `research/theorems/` |
| Detailed reasoning and executable evidence | `research/notes/`, `reproducibility/checks/` |
| Agent procedure and knowledge policy | `docs/agents/`, `docs/knowledge/okf-profile.md` |

Preserve published Concept IDs, immutable external-source bytes, claim-level provenance, and a semantic review run distinct from generation where the profile requires one. Treat structural CI as conformance evidence, not semantic approval.

Root `.agents/` is repository tooling outside the SmartDCA knowledge bundle. SmartDCA concept metadata, index and log entries, and knowledge validation do not apply inside that tree.

**Publishable when:** the current ticket, effort specification, effort map, and master map agree, every changed concept passes the LLM-Wiki publish gate, every changed scientific claim passes its linked checks, and no result depends on hidden conversation context.
