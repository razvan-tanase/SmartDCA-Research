---
profile: smartdca-okf/0.5
type: decision-record
title: "Preserve path-based concept identity through supersession"
description: "Decision preserving path-based Concept IDs and replacing concepts through supersession, never moves."
knowledge_role: canonical
status: stable
original_record: true
decision_status: accepted
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T07:38:00Z
    review_run: urn:uuid:16bd7b25-9e03-4aef-9c9a-5301cb317903
---
# Preserve path-based concept identity through supersession

Repository-relative paths without `.md` are durable Concept IDs once the SmartDCA OKF migration establishes them. Later restructuring creates new concepts instead of silently moving stable ones; a replaced concept remains at its original path with deprecated status, a reason, and a `superseded_by` link so citations and provenance survive cleanup.
