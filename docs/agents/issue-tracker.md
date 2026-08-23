---
profile: smartdca-okf/0.4
type: workflow
title: "Issue tracker: Local Markdown"
description: "Where research maps, tickets, and their state fields live and how they are named."
knowledge_role: operational
status: stable
original_record: true
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-23T20:17:00Z
generation_run: urn:uuid:ed95ae0b-06ee-4d96-a841-5724e383cc65
verified:
  - by: openai-codex/smartdca-wiki-0.1
    at: 2026-08-23T16:21:37Z
    review_run: urn:uuid:66222a92-a082-4617-b191-77c124239e73
  - by: openai-codex/standards-review-0.1
    at: 2026-08-23T20:30:00Z
    review_run: urn:uuid:e99ebedf-be97-4645-9ada-70efce93a3b2
---
# Issue tracker: Local Markdown

Use this reference to locate project work and interpret tracker fields. The versioned files under `.scratch/` are the authoritative project state; GitHub supplies durable history and review.

## Conventions

- The master project map is `.scratch/smartdca/map.md`; it links bounded efforts and records the cross-effort frontier.
- Each active effort is `.scratch/smartdca/efforts/<effort>/` and contains an approved `spec.md`, a `map.md`, and `issues/`.
- Tickets are one file each at `.scratch/smartdca/efforts/<effort>/issues/<NN>-<slug>.md`; numbers are local to the effort.
- `.scratch/smartdca/issues/` is the immutable-in-place archive for resolved legacy tickets 01–19. Do not add open or claimed tickets there.
- `Type:` records `research`, `prototype`, `grilling`, or `task`.
- `Status:` records `open`, `claimed`, or `resolved`.
- `Blocked by:` lists local ticket numbers inside one effort and full bundle-relative Concept IDs for dependencies outside it; a ticket is unblocked only when every listed ticket is resolved.
- `## Question` is the preserved work contract.
- `## Comments` holds execution history, blockers, and review findings.
- `## Answer` holds the complete resolution; the map contains only a linked gist.

An effort specification is the user-approved contract: problem, outcome, acceptance boundary, implementation and testing decisions, and exclusions. It is not claimed or resolved like a ticket. Follow the [Wayfinder ticket workflow](wayfinder-ticket-workflow.md) for frontier selection, claiming, execution, review, resolution, interruption, and the user significance gate.

**Coherent when:** every active effort has a stable `spec.md` and `map.md`, the body and frontmatter ticket states match, every `Blocked by:` edge names an existing ticket, at most one ticket is claimed project-wide, and both map levels contain enough state to recompute the frontier.
