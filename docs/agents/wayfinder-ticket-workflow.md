---
profile: smartdca-okf/0.3
type: workflow
title: "Wayfinder ticket workflow"
description: "Authoritative ticket lifecycle from orientation through the user significance gate."
knowledge_role: operational
status: stable
original_record: true
---
# Wayfinder ticket workflow

Use this lifecycle whenever work touches a ticket under `.scratch/<effort>/issues/`. The map is the index; the ticket is the single source of truth for its question and answer.

## Invariants

- Work on one ticket at a time unless the user explicitly authorizes a batch.
- Keep at most one ticket in `Status: claimed`.
- Use ticket names in user-facing text; identifiers appear only inside links or dependency metadata.
- Resolve the current ticket completely before modifying the substance of a later ticket.
- End every resolved ticket at the significance gate. The next ticket remains unclaimed until the user explicitly continues.

## Lifecycle

### 1. Orient

Read the effort's `map.md`, the selected ticket, `CONTEXT.md`, relevant ADRs, and this workflow. Read related resolved tickets only when the current question depends on their detail.

**Complete when:** the destination, current question, assumptions, dependencies, and out-of-scope boundary can each be stated without guessing.

### 2. Select and claim

Use a user-named ticket when it is open and unblocked. Otherwise choose the first open, unblocked, unclaimed child in tracker order. Confirm that no other ticket is claimed, then change the selected ticket to `Status: claimed` before starting work.

**Complete when:** exactly one eligible ticket is claimed and every blocking ticket is resolved.

### 3. Choose the execution branch

- `research`: use the research skill and a background agent; prefer primary sources and write one cited Markdown note.
- `prototype`: use the prototype skill with the user and link the concrete artifact.
- `grilling`: use the grilling and domain-modeling skills in a live user exchange.
- `task`: execute the prerequisite work or give the human a precise checklist when human action is required.

Load every skill named by the map or selected branch before acting. Keep all work inside the current ticket's question.

**Complete when:** the branch, required skills, evidence standard, and output location are fixed.

### 4. Resolve the question

Answer every clause of the ticket. Separate proved facts, empirical observations, assumptions, counterexamples, and unresolved points. Link supporting notes or artifacts instead of duplicating their full contents into the ticket.

For mathematical tickets, test constant inputs, boundary parameters, limiting cases, and at least one nontrivial numerical or symbolic example whenever applicable. For empirical tickets, record data provenance, code version, seeds, estimands, and failure cases.

**Complete when:** every clause has an evidence-backed answer or an explicit unresolved status with the reason it cannot yet be answered.

### 5. Review and verify

When a subagent or background agent produced or changed any deliverable, the parent executor must independently review that work before accepting it. The producing agent's self-check is evidence, not final approval.

Use the review skill appropriate to the artifact:

- For repository code changes, invoke the `code-review` skill against a fixed point and the originating ticket or specification.
- For research, proofs, experiments, documents, and other non-code artifacts, invoke the applicable domain-specific review skill when one is available. Otherwise, the parent executor performs and records an independent domain-specific review.

Review against both the ticket's specification and the project's documented standards. Resolve every actionable finding, or record it explicitly as an unresolved blocker, before continuing.

Check that cited sources support their nearby claims, proofs cover their declared domains, counterexamples satisfy every stated assumption, artifact links resolve, and no later ticket was substantively advanced. Re-run any relevant calculations or tests after fixes.

**Complete when:** someone other than the producing agent has reviewed every delegated deliverable, all actionable findings are resolved or explicitly block the ticket, all checks pass, and the result can be reviewed without relying on hidden conversation context.

### 6. Record and synchronize

1. Append the concise resolution under `## Answer` in the ticket.
2. Change the ticket to `Status: resolved`.
3. Add one named link and one-line gist to the map's `## Decisions so far`.
4. Update `CONTEXT.md` immediately for newly settled terminology.
5. Add newly visible tickets, wire real blocking dependencies, graduate clarified fog, and move newly excluded work to `## Out of scope`.

Keep detailed reasoning in exactly one place: the ticket or its linked artifact. The map only indexes it.

**Complete when:** the ticket, map, glossary, dependencies, and linked artifacts agree.

### 7. Preserve the checkpoint

Save every changed reusable file through the project's persistent-file workflow and verify that each promised file is accessible. Preserve existing file identity when updating an earlier artifact.

**Complete when:** every changed project artifact is available and no intended update remains only in transient working state.

### 8. Significance gate

Report the ticket's result and why it matters. Ask the user to choose one of:

- **Continue** — accept the result and recompute the frontier.
- **Narrow** — retain the result but reduce the destination or next question.
- **Pivot** — revise the route and invalidate or replace affected tickets.
- **Stop** — preserve the map as the final checkpoint.

An explicit grilling checkpoint ticket may record a particularly important gate; otherwise the gate is part of this lifecycle.

**Complete when:** the user makes an explicit choice. Until then, leave every next ticket unclaimed and perform no new ticket work.

### 9. Advance

After **Continue**, reload the map, recompute the frontier from current file state, and restart at **Orient**. After **Narrow**, **Pivot**, or **Stop**, update the map first and then follow the resulting frontier or finish.

**Complete when:** the next eligible ticket is identified from the updated map, never from stale conversation memory.

## Interrupted work

If work cannot complete, append the evidence gathered and the exact blocker under `## Comments`. Keep `Status: claimed` only while an executor is actively working. Otherwise return it to `Status: open`, create or link the blocking ticket, and synchronize the map before stopping.
