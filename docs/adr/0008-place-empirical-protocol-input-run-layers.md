---
profile: smartdca-okf/0.5
type: decision-record
title: "Place empirical protocols, inputs, and run bundles in versioned layers"
description: "Decision separating immutable empirical registrations, versioned inputs, machine-generated run bundles, and reviewable experiment reports."
knowledge_role: canonical
status: stable
original_record: true
decision_status: accepted
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-25T09:13:48Z
generation_run: urn:uuid:137eb6a1-90fe-4db5-899b-7d85483bdf43
verified:
  - by: openai-codex/standards-review-0.1
    at: 2026-08-25T09:13:48Z
    review_run: urn:uuid:8e4d4bc6-edf2-41c1-8eca-7bef42fbcb46
---
# Place empirical protocols, inputs, and run bundles in versioned layers

## Context

The repository already separates research state, detailed reasoning,
executable checks, and experiment-report concepts. The empirical effort adds
three non-Markdown artifact classes with different identity and mutability
rules: an outcome-blind registration, the bytes supplied to a run, and the
machine output of that run. Putting all three beside narrative reports would
hide those distinctions; putting them under `reproducibility/checks/` would
confuse executable verification with its data and output.

## Decision

Use these durable layers:

| Path | Authority and identity rule |
|---|---|
| `experiments/protocols/*.json` | Immutable preregistrations. Exact accepted bytes are fingerprinted; after the review seal or any outcome access, a change creates a new protocol ID and version instead of editing the registered identity in place. |
| `experiments/inputs/*.json` | Versioned runner inputs or input receipts. Exact accepted bytes are fingerprinted, credentials are excluded, and changed bytes after the review seal create a new input version. Provider bytes remain subject to the recorded license and redistribution rule. |
| `reports/experiments/runs/<run-id>/` | Deterministic machine outputs. The run ID binds the engine, runner source, protocol bytes, and input bytes; an existing identity is a collision rather than an overwrite. |
| `reports/experiments/*.md` | OKF `experiment-report` concepts that interpret and join a run to its protocol, input, code, review, and limits. The report never substitutes for the machine artifacts. |

The public runner stays under `reproducibility/`; its contract is verified
under `reproducibility/checks/`. JSON artifacts are not independent OKF
concepts, so the existing profile path mapping does not change. The root index
continues to inventory the Markdown experiment report, which is the discovery
entry point for its linked run bundle.

The first publication of a protocol/input pair has one narrow outcome-blind
review-correction window. Before any outcome access and before an independent
review accepts the artifacts, a reviewer may require corrections under the
provisional identity. The append-only log must record both the initial
creation and the correction, `confirmatory_outcomes_accessed` must remain
false, and the corrected run receives its new content-derived run ID. The
independent acceptance seals the final protocol and input fingerprints and
closes this window. This is not an amendment path after outcome access and is
not available to an already accepted artifact version.

## Consequences

One registered design can drive multiple immutable input versions and runs
without conflating their identities. A run can be replayed byte for byte, and
a report can remain draft while its artifacts are already durable. Generated
bundles may be large in later tickets; any future decision to move them to
external object storage must preserve content fingerprints, stable report
links or receipts, and the collision/no-overwrite rule.

Ticket 01 exercised the first-publication window: review found underspecified
timing/inference rules, missing stratum metadata, and invalid proportional-cost
rounding before any historical outcome access. The correction is explicit in
the event log; the accepted fingerprints, rather than the provisional draft
bytes, seal version 1.

This decision extends rather than replaces [the versioned research-layer
decision](0001-versioned-research-layout.md) and the
[experiment-report path decision](0006-assign-definition-theorem-and-experiment-report-paths.md).
