---
profile: smartdca-okf/0.5
type: workflow
title: "Wayfinder ticket workflow"
description: "Authoritative ticket lifecycle from orientation through the user significance gate."
knowledge_role: operational
status: stable
original_record: true
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-23T20:29:00Z
generation_run: urn:uuid:ed95ae0b-06ee-4d96-a841-5724e383cc65
verified:
  - by: openai-codex/smartdca-wiki-0.1
    at: 2026-08-23T16:21:37Z
    review_run: urn:uuid:66222a92-a082-4617-b191-77c124239e73
  - by: openai-codex/standards-review-0.1
    at: 2026-08-23T20:30:00Z
    review_run: urn:uuid:e99ebedf-be97-4645-9ada-70efce93a3b2
---
# Wayfinder ticket workflow

Use this lifecycle when executing an active ticket under `.scratch/smartdca/efforts/<effort>/issues/`. Resolved records under `.scratch/smartdca/issues/` are read-only historical inputs: consult them when a current dependency requires their detail, but never claim or reopen them through this lifecycle. The master map selects the effort, the effort specification fixes its contract, the effort map indexes its route, and the active ticket is the single source of truth for its question and answer.

## Invariants

- Work on one ticket at a time unless the user explicitly authorizes a batch.
- Keep at most one ticket in `Status: claimed`.
- Lead user-facing text with ticket names; keep identifiers in links and dependency metadata.
- Resolve the current ticket completely before modifying the substance of a later ticket.
- End every resolved ticket at the significance gate. The next ticket remains unclaimed until the user explicitly continues.

## Lifecycle

### 1. Orient

Read the master map, the effort's `spec.md` and `map.md`, the selected ticket, [Domain documentation](domain.md), and this workflow. Follow the domain procedure to select glossary sections and ADRs. Open a resolved legacy ticket only when the current question depends on its historical detail.

**Complete when:** the project destination, effort outcome, current question, assumptions, dependencies, and out-of-scope boundary can each be stated without guessing.

### 2. Select and claim

Use a user-named ticket when it is open and unblocked. Otherwise choose the first open, unblocked, unclaimed child in tracker order. Confirm that no other ticket is claimed, then change the selected ticket to `Status: claimed` before starting work.

**Complete when:** exactly one eligible ticket is claimed and every blocking ticket is resolved.

### 3. Choose the execution branch

- `research`: use the research skill, prefer primary sources, and write one cited Markdown note; delegate only when the request or loaded skill requires it.
- `prototype`: use the prototype skill with the user and link the concrete artifact.
- `grilling`: use the grilling and domain-modeling skills in a live user exchange.
- `task`: execute the bounded work; when it requires human action, provide a checklist whose completion can be verified.

Load every skill named by the map or selected branch before acting. Keep all work inside the current ticket's question.

**Complete when:** the branch, required skills, evidence standard, and output location are fixed.

### 4. Resolve the question

Answer every clause of the ticket. Separate proved facts, empirical observations, assumptions, counterexamples, and unresolved points. Link supporting notes or artifacts instead of duplicating their full contents into the ticket.

For mathematical tickets, test constant inputs, boundary parameters, limiting cases, and at least one nontrivial numerical or symbolic example whenever applicable. For empirical tickets, record data provenance, code version, seeds, estimands, and failure cases.

**Complete when:** every clause has an evidence-backed answer or an explicit unresolved status with the reason it cannot yet be answered.

### 5. Review and verify

When delegated work produced or changed a deliverable, an executor other than its producer reviews it before acceptance. The producing agent's self-check remains supporting evidence.

Use the review skill appropriate to the artifact:

- For repository code changes, invoke the `code-review` skill against a fixed point and the originating ticket or specification.
- For agent instructions or workflows, invoke the Writing for Agents skill against the complete active instruction surface.
- For research, proofs, experiments, documents, and other non-code artifacts, invoke the applicable domain-specific review skill when one is available. Otherwise, the parent executor performs and records an independent domain-specific review.

Review against both the ticket's specification and the project's documented standards. Resolve every actionable finding, or record it explicitly as an unresolved blocker, before continuing.

Check that cited sources support their nearby claims, proofs cover their declared domains, counterexamples satisfy every stated assumption, artifact links resolve, and no later ticket was substantively advanced. Re-run any relevant calculations or tests after fixes.

**Complete when:** every delegated deliverable has a reviewer other than its producer, every actionable finding is resolved or explicitly blocks the ticket, all checks pass, and the result can be reviewed without hidden conversation context.

### 6. Record and synchronize

1. Append the concise resolution under `## Answer` in the ticket.
2. Change the ticket to `Status: resolved`.
3. Add one named link and one-line gist to the effort map; update the master map only when the cross-effort frontier or a project-level decision changes.
4. Update `CONTEXT.md` immediately for newly settled terminology.
5. Add newly visible tickets, wire real blocking dependencies, graduate clarified fog, and move newly excluded work to `## Out of scope`.

Keep detailed reasoning in exactly one place: the ticket or its linked artifact. The map only indexes it.

**Complete when:** the ticket, effort map, master map where relevant, glossary, dependencies, and linked artifacts agree.

### 7. Preserve the checkpoint

Commit every changed reusable file through the authorized repository workflow. Inspect the final diff, preserve existing file identity, and verify the published branch or pull-request link when publication is part of the request.

**Complete when:** every intended file is present in the final diff, every promised remote artifact is accessible, and no intended update exists only in transient state.

### 8. Significance gate

Report the ticket's result and why it matters. Ask the user to choose one of:

- **Continue** — accept the result and recompute the frontier.
- **Narrow** — retain the result but reduce the destination or next question.
- **Pivot** — revise the route and invalidate or replace affected tickets.
- **Stop** — preserve the map as the final checkpoint.

An explicit grilling checkpoint ticket may record a particularly important gate; otherwise the gate is part of this lifecycle.

**Complete when:** the user makes an explicit choice. Until then, leave every next ticket unclaimed and perform no new ticket work.

### 9. Advance

After **Continue**, reload the map, recompute the frontier from current file state, and restart at **Orient**. After **Narrow**, **Pivot**, or **Stop**, update the map first, then follow the resulting frontier or finish.

**Complete when:** the next eligible ticket is identified from the updated map, never from stale conversation memory.

## Interrupted work

If work cannot complete, append the evidence gathered and the exact blocker under `## Comments`. Keep `Status: claimed` only while an executor is actively working. Otherwise return it to `Status: open`, create or link the blocking ticket, and synchronize the map before stopping.
