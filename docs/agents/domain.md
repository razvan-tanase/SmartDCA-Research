---
profile: smartdca-okf/0.3
type: agent-instructions
title: "Domain documentation"
description: "Single-context rule for reading the glossary and ADRs before domain work."
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
# Domain documentation

Use this procedure when work may change project terminology, assumptions, the mathematical or financial model, or an architectural decision.

## Orient

1. Read the relevant section of root `CONTEXT.md`; it is the canonical vocabulary.
2. List ADR titles with `rg '^title:' docs/adr/`, then read each accepted decision whose scope intersects the change.
3. Reuse the glossary's named concepts in the ticket, proof, script, and review findings.

## Place the decision

- When adding or revising a domain term, load the domain-modeling skill and update `CONTEXT.md` through its workflow.
- Record implementation and repository-layout decisions in an ADR.
- When a proposed change conflicts with an accepted ADR, present the conflict and resolve the decision before implementation.

**Complete when:** every changed term has one canonical definition, every affected accepted ADR is accounted for, and the ticket, canonical concept, evidence, and code use the same vocabulary.
