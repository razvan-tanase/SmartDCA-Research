---
profile: smartdca-okf/0.5
type: decision-record
title: "Keep research state and evidence in separate versioned layers"
description: "Decision keeping map state, detailed reasoning, and executable evidence in separate versioned layers."
knowledge_role: canonical
status: stable
original_record: true
decision_status: accepted
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T07:38:00Z
    review_run: urn:uuid:16bd7b25-9e03-4aef-9c9a-5301cb317903
---
# Keep research state and evidence in separate versioned layers

The repository keeps the authoritative Wayfinder map and ticket state under `.scratch/smartdca/`, detailed mathematical reasoning under `research/notes/`, and executable evidence under `reproducibility/checks/`. This preserves the project's local-Markdown significance-gate workflow while using GitHub for durable versioning and review, prevents the map from duplicating proofs, and keeps reproducible checks discoverable without presenting exploratory artifacts as manuscript results.
