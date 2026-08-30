---
profile: smartdca-okf/0.5
type: domain-glossary
title: "Triage labels"
description: "Operational mapping from canonical triage roles to this project's labels."
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
# Triage labels

Use this mapping only when a triage workflow emits a canonical role.

| Canonical role | Project label | Meaning |
|---|---|---|
| `needs-triage` | `needs-triage` | Maintainer evaluation is required. |
| `needs-info` | `needs-info` | More information is required. |
| `ready-for-agent` | `ready-for-agent` | Fully specified and ready for an agent. |
| `ready-for-human` | `ready-for-human` | Human action is required. |
| `wontfix` | `wontfix` | The item will not be actioned. |

Apply the project label in the same row as the emitted role. The mapping is complete when every emitted role has exactly one project-label translation.
