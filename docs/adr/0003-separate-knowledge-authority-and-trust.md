---
profile: smartdca-okf/0.5
type: decision-record
title: "Separate document kind, authority, lifecycle, and trust"
description: "Decision keeping type, knowledge role, OKF lifecycle, and review trust as independent axes."
knowledge_role: canonical
status: stable
original_record: true
decision_status: accepted
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T07:38:00Z
    review_run: urn:uuid:16bd7b25-9e03-4aef-9c9a-5301cb317903
---
# Separate document kind, authority, lifecycle, and trust

The SmartDCA OKF profile records what a document is in `type`, whether it is a preferred answer source in `knowledge_role: canonical|evidence|operational`, its lifecycle in OKF `status`, and its review evidence in OKF `verified`. These axes remain independent so a resolved ticket can be stable operational history without being mistaken for a canonical mathematical result. Stable high-risk knowledge requires mechanical validation plus semantic review from a run distinct from its producer; a meaningful edit demotes it to draft until verification at or after the edit is recorded.
