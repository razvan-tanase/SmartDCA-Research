---
profile: smartdca-okf/0.5
type: decision-record
title: "Exclude .agents tooling from the SmartDCA knowledge bundle"
description: "Decision reserving the .agents tree as repository tooling outside SmartDCA bundle membership and validation."
knowledge_role: canonical
status: stable
decision_status: accepted
sources:
  - id: okf-spec
    title: "Source summary: Open Knowledge Format v0.2 specification"
    resource: references/summaries/okf-v0-2-specification
    source_kind: internal
  - id: repository-root
    title: "Make the repository root an OKF knowledge bundle"
    resource: docs/adr/0002-repository-root-okf-knowledge-bundle
    source_kind: internal
  - id: blocker-ticket
    title: "Exclude repository-local agent tooling from the OKF bundle"
    resource: .scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/issues/08-exclude-agents-from-okf-bundle
    source_kind: internal
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-30T09:57:10Z
generation_run: urn:uuid:eb95df4b-cddd-4d8f-987c-dca42e3ecc68
verified:
  - by: openai-codex/standards-review-0.1
    at: 2026-08-30T10:09:30Z
    review_run: urn:uuid:0cf9e427-2b3e-40eb-a2f3-d5f93b17e175
  - by: openai-codex/spec-review-0.1
    at: 2026-08-30T10:09:30Z
    review_run: urn:uuid:0423e158-4c18-4bb7-bfe3-ba3e7b07b882
---
# Exclude .agents tooling from the SmartDCA knowledge bundle

## Context

Open Knowledge Format v0.2 reserves only `index.md` and `log.md` inside a bundle
and validates every other final-suffix Markdown bundle member as a
concept.[^okf-spec] The earlier architecture described the repository root as
the conformant SmartDCA bundle and included authoritative agent workflows under
`docs/agents/`.[^repository-root] Commit `ea7cca3` later added a separate
repository-tooling payload below `.agents/`, creating an ambiguity about whether
physical containment alone made those tool instructions bundle members.[^blocker-ticket]

## Decision

Profile `smartdca-okf/0.5` makes bundle membership explicit: the root `.git/`
and `.agents/` trees are repository infrastructure, not bundle content. The
validator excludes them before both base OKF and SmartDCA-profile validation.
Every other final-suffix Markdown path, including paths below other hidden
directories, remains subject to the ordinary reserved-file and concept rules.

This decision narrows ADR 0002's phrase “every non-reserved Markdown file” to
Markdown bundle members. Its repository-root architecture, role separation,
and inclusion of authoritative `docs/agents/` workflows remain accepted.

OKF v0.2 does not define this membership filter. The validator therefore labels
its base result as member checks over the declared SmartDCA bundle view and
states that raw-repository OKF conformance is not claimed.

No file below `.agents/` receives profile metadata, an index row, a log event,
or any other SmartDCA knowledge treatment. Its skill-routing metadata and
instruction bodies remain byte-for-byte as imported.

All existing 0.4 concepts are relabelled 0.5 as a metadata migration. A concept
whose body changes in the same transaction records that meaningful change in
its own generation metadata; relabelling alone does not alter lifecycle or
trust.

## Rejected alternative

Treating `.agents/skills/**/*.md` as operational concepts would satisfy a purely
physical reading of the repository-root bundle, but it would place imported
executable tooling under repository knowledge policy and require mass metadata
edits. The user explicitly rejected that ownership boundary. The selected local
bundle-view rule prioritizes that ownership decision and gives up the earlier
unqualified claim that the raw repository root is itself OKF-conformant.

## Consequences

The root index continues to inventory only SmartDCA knowledge concepts, and
repository-local skill changes cannot create knowledge-gate findings. The
2026-08-30 bundle-membership change lapses structural freeze and resets the
supervised-ingest streak to zero. Published Concept IDs, lifecycle states, and
recorded verifications remain valid; a lapsed freeze does not retract
content.[^blocker-ticket]

## Status

Accepted by the user's explicit 2026-08-30 clarification. Independent
Writing-for-Agents, Standards, and specification reviews found no remaining
actionable issue.

[^okf-spec]: [Source summary: Open Knowledge Format v0.2 specification](../../references/summaries/okf-v0-2-specification.md)
[^repository-root]: [Make the repository root an OKF knowledge bundle](0002-repository-root-okf-knowledge-bundle.md)
[^blocker-ticket]: [Exclude repository-local agent tooling from the OKF bundle](../../.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/issues/08-exclude-agents-from-okf-bundle.md)
