---
profile: smartdca-okf/0.3
type: workflow
title: "Issue tracker: Local Markdown"
description: "Where research maps, tickets, and their state fields live and how they are named."
knowledge_role: operational
status: stable
original_record: true
---
# Issue tracker: Local Markdown

Research maps, specifications, and tickets for this repository live as Markdown under `.scratch/`. Stripe's internal GitHub Enterprise (`git.corp.stripe.com`) hosts and reviews the repository; the versioned ticket files remain the authoritative project state.

## Conventions

- One effort per directory: `.scratch/<effort>/`.
- The map is `.scratch/<effort>/map.md`.
- Tickets are one file each at `.scratch/<effort>/issues/<NN>-<slug>.md`.
- `Type:` records `research`, `prototype`, `grilling`, or `task`.
- `Status:` records `open`, `claimed`, or `resolved`.
- `Blocked by:` lists ticket numbers; a ticket is unblocked only when every listed ticket is resolved.
- Conversation history and review findings belong under `## Comments`.
- The ticket's complete resolution belongs under `## Answer`; the map contains only a linked gist.

## Wayfinder operations

- **Frontier:** scan `.scratch/<effort>/issues/` in numeric order for the first open, unblocked, unclaimed ticket.
- **Claim:** save `Status: claimed` before starting substantive work.
- **Resolve:** answer every clause, complete review, set `Status: resolved`, synchronize the map and glossary, and preserve the checkpoint.
- **Advance:** wait for the user's explicit significance-gate choice before claiming another ticket.

The active effort is `.scratch/smartdca/`. Its detailed lifecycle is in `docs/agents/wayfinder-ticket-workflow.md`.
