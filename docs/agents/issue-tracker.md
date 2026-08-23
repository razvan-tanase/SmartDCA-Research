---
profile: smartdca-okf/0.3
type: workflow
title: "Issue tracker: Local Markdown"
description: "Where research maps, tickets, and their state fields live and how they are named."
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
# Issue tracker: Local Markdown

Use this reference to locate project work and interpret tracker fields. The versioned files under `.scratch/` are the authoritative project state; GitHub supplies durable history and review.

## Conventions

- One effort per directory: `.scratch/<effort>/`.
- The map is `.scratch/<effort>/map.md`.
- Tickets are one file each at `.scratch/<effort>/issues/<NN>-<slug>.md`.
- `Type:` records `research`, `prototype`, `grilling`, or `task`.
- `Status:` records `open`, `claimed`, or `resolved`.
- `Blocked by:` lists ticket numbers; a ticket is unblocked only when every listed ticket is resolved.
- `## Question` is the preserved work contract.
- `## Comments` holds execution history, blockers, and review findings.
- `## Answer` holds the complete resolution; the map contains only a linked gist.

The active effort is `.scratch/smartdca/`. Follow the [Wayfinder ticket workflow](wayfinder-ticket-workflow.md) for frontier selection, claiming, execution, review, resolution, interruption, and the user significance gate.

**Coherent when:** the body and frontmatter states match, every `Blocked by:` edge names an existing ticket, at most one ticket is claimed, and the map points to every settled decision needed to recompute the frontier.
