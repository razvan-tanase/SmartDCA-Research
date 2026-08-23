---
profile: smartdca-okf/0.4
type: decision-record
title: "Assign source-summary and synthesis paths in profile 0.2"
description: "Decision assigning ingest summary and synthesis paths and relabelling the bundle as smartdca-okf/0.2."
knowledge_role: canonical
status: stable
original_record: true
decision_status: accepted
generated:
  by: claude-code/smartdca-wiki-0.1
  at: 2026-08-16T08:24:00Z
generation_run: urn:uuid:57953b52-1968-45dc-a791-5610c4b1ec4d
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T08:26:00Z
    review_run: urn:uuid:84b7d96d-6547-4bbf-b78e-f4334f5f3c41
---
# Assign source-summary and synthesis paths in profile 0.2

Supervised ingestion needs somewhere conformant to put a summary before it can ingest anything, but profile 0.1's initial path mapping is exhaustive and registers no `source-summary` or `synthesis` destination, so a summary at any path fails strict validation. Profile 0.1 also requires a profile version change to assign a new Markdown path. The two rules together block ingestion outright until the profile is revised.

Therefore profile `smartdca-okf/0.2` assigns exactly two new paths — `references/summaries/*.md` for `source-summary` evidence and `research/synthesis/*.md` for `synthesis` canonical concepts — and every concept declares `profile: smartdca-okf/0.2`. `references/summaries/` sits under the `references/` tree that base OKF already reserves by convention for mirrored external material, next to the immutable `references/raw/` snapshots it summarizes. `definition`, `theorem`, and `experiment-report` remain unassigned; the semantic-extraction work makes that decision.

Relabelling 0.1 to 0.2 is a metadata migration and not a meaningful content change, so it does not update `generated.at`, does not demote a high-risk concept to draft, and does not invalidate a recorded verification. Only concepts whose bodies actually changed in the same transaction carry a new generation time. No other rule of profile 0.1 changes, so a 0.1 concept is conformant under 0.2 once its `profile` value is relabelled.
