---
profile: smartdca-okf/0.5
type: research-ticket
title: "Audit and sharpen agent-facing wiki instructions"
description: "Resolved task ticket auditing the full wiki for agent-consumed writing and sharpening the active instruction surfaces."
knowledge_role: operational
status: stable
ticket_type: task
ticket_status: resolved
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-23T16:21:37Z
generation_run: urn:uuid:fc39df1d-3e43-487c-8bc6-9a1e72abaff8
---
# Audit and sharpen agent-facing wiki instructions

Type: task
Status: resolved
Blocked by: none
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

Audit the complete repository-root wiki for writing that an agent consumes as
instructions, workflow, task specification, or a context pointer. Apply the
Writing for Agents criteria: trigger quality, information hierarchy,
co-location, completion criteria, leading words, positive direction,
single-source-of-truth discipline, environmental lookups, relevance, and
no-op pruning.

Sharpen the active instruction surfaces (`AGENTS.md` and `docs/agents/*.md`),
remove stale operational claims, and synchronize the OKF index, log, map, and
this ticket. Treat resolved research tickets as historical operational records:
inspect their agent-facing contracts, but preserve their questions and answers
unless a defect still controls future work.

Complete the ticket only when every Markdown path has been classified for this
audit, every active agent instruction has an explicit trigger and checkable
completion bound, strict OKF validation and all tests pass, and the final diff
contains no unexplained change to scientific claims.

## Comments

- The user explicitly requested the repository-wide audit and invoked the
  Writing for Agents skill on 2026-08-23.
- A second Writing for Agents pass reviewed the complete active instruction
  surface against the ticket and the skill's criteria. It found and fixed one
  weak skill pointer in the domain procedure. No actionable finding remains.

## Answer

All 62 Markdown paths were classified before editing:

| Class | Count | Audit outcome |
|---|---:|---|
| Active agent instructions and workflows | 6 | All six sharpened and reviewed. |
| Normative OKF profile | 1 | Reviewed as disclosed reference; its rules remain the single source of truth. |
| Map and ticket records | 20 | Map and this ticket synchronized; 18 resolved tickets preserved as history. |
| Canonical and evidentiary knowledge | 32 | No operational role confusion requiring an edit. |
| Human interface, inventory, and event history | 3 | Kept in their existing roles; index and log synchronized. |

The active instruction audit produced six material improvements:

1. `AGENTS.md` now routes by ticket, domain, knowledge, and scientific branches,
   names the authoritative layer for each information kind, and ends on one
   publishable-state criterion.
2. `docs/agents/issue-tracker.md` no longer claims that Stripe's internal
   GitHub Enterprise hosts the repository. It defines storage and fields, then
   points lifecycle operations to the Wayfinder workflow instead of duplicating
   them.
3. `docs/agents/domain.md` now has a precise trigger, an environment-backed ADR
   lookup, a strong domain-modeling skill pointer, co-located placement rules,
   and a completion criterion.
4. `docs/agents/llm-wiki-workflow.md` now separates its seven execution stages,
   gives every stage an exhaustive completion bound, removes migration history
   from the live recipe, and states target behavior positively where possible.
5. `docs/agents/wayfinder-ticket-workflow.md` now avoids unconditional
   background-agent use, adds the Writing for Agents review branch, and replaces
   the vague persistence step with a verifiable repository checkpoint.
6. `docs/agents/triage-labels.md` now states its invocation condition and exact
   mapping completion rule.

The 18 earlier tickets remain unchanged because their resolved questions and
answers are provenance-bearing operational history. Future ticket behavior is
controlled in one place by the sharpened Wayfinder workflow. No mathematical,
financial, or scientific claim changed.
