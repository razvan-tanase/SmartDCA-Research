---
profile: smartdca-okf/0.4
type: decision-record
title: "Adopt effort-scoped work tracking"
description: "Decision to give each active research effort its own approved specification, map, and locally numbered ticket directory."
knowledge_role: canonical
status: stable
original_record: true
decision_status: accepted
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-23T20:17:00Z
generation_run: urn:uuid:ed95ae0b-06ee-4d96-a841-5724e383cc65
verified:
  - by: openai-codex/spec-review-0.1
    at: 2026-08-23T20:31:00Z
    review_run: urn:uuid:15c9b810-1adb-4eed-b833-45e31bcad2f1
---
# ADR 0007: Adopt effort-scoped work tracking

## Context

The original tracker placed project history, a large frontier specification,
and all active tracer tickets in `.scratch/smartdca/issues/`. As the research
expanded, ticket numbers stopped communicating which bounded investigation a
ticket belonged to, and the parent specification was indistinguishable from an
executable work item.

Resolved tickets 01–19 already form provenance-bearing project history. Open
tickets 20–25 belong to one approved arbitrary-horizon investigation and have
not yet established stable Concept IDs.

## Decision

Use a prospective effort-scoped layout:

- `.scratch/smartdca/map.md` remains the master project frontier;
- each active effort lives at `.scratch/smartdca/efforts/<effort>/`;
- `spec.md` is the approved operational contract for that effort;
- `map.md` records state and routing inside the effort;
- `issues/<NN>-<slug>.md` contains locally numbered tracer tickets;
- cross-effort blockers use full repository-relative Concept IDs;
- `.scratch/smartdca/issues/` is retained as a resolved-ticket archive.

Migrate only draft open tickets 20–25. Preserve resolved tickets 01–19 at
their existing paths. Because the migrated concepts were draft, do not create
deprecated forwarders for their former paths.

Register the operational `work-specification` type and enforce the new layout
in `smartdca-okf/0.4`. Publishing tickets requires both effort anchors and a
stable, user-approved effort specification.

## Consequences

Each workstream gains a visible contract and independent progress map, ticket
numbers stay short, and the master map no longer carries detailed execution
state. Links and automation must include the effort path because local numbers
are not globally unique.

The profile schema changes, so the prior structural-freeze certification
lapses and the supervised-ingest streak resets. Re-certification is separate
future work after the revised structure demonstrates stability.

## Status

Accepted by the user on 2026-08-23 and promoted after independent standards
and specification review.
