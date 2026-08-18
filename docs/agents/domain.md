---
profile: smartdca-okf/0.3
type: agent-instructions
title: "Domain documentation"
description: "Single-context rule for reading the glossary and ADRs before domain work."
knowledge_role: operational
status: stable
original_record: true
---
# Domain documentation

This is a single-context research repository.

## Before work

1. Read root `CONTEXT.md` for the canonical mathematical and financial vocabulary.
2. Read ADRs under `docs/adr/` that affect the work.
3. Use the glossary's named concepts in tickets, proofs, scripts, and review findings.

If a needed concept is missing, update `CONTEXT.md` through the domain-modeling workflow. Keep implementation and repository-layout decisions in ADRs rather than the glossary. Surface any proposed change that conflicts with an accepted ADR.
