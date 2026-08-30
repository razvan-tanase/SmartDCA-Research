---
profile: smartdca-okf/0.5
type: research-ticket
title: "Exclude repository-local agent tooling from the OKF bundle"
description: "Blocking task ticket reserving the .agents tooling tree outside the repository knowledge bundle without changing its files."
knowledge_role: operational
status: draft
original_record: true
ticket_type: task
ticket_status: claimed
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-30T09:34:27Z
generation_run: urn:uuid:e54b04fe-969e-4f95-81f4-1121a2423495
---
# 08 — Exclude repository-local agent tooling from the OKF bundle

Type: task
Status: claimed
Label: ready-for-agent
Blocked by: none
Parent: [Safety-adaptivity empirical evaluation](../spec.md)

## Question

Which explicit, versioned bundle-membership rule keeps the `.agents/` tooling
tree outside SmartDCA knowledge validation while preserving base OKF v0.2
semantics for every bundle member and leaving every tooling file unchanged?

## What to build

A maintainer can validate the SmartDCA bundle in strict mode, distinguish its
knowledge members from repository-local agent tooling, and verify that hidden
knowledge paths remain discoverable while `.agents/` is neither rewritten nor
inventoried as knowledge.

## Acceptance criteria

- [ ] The decision evaluates both excluding `.agents` as executable tooling and treating `.agents/skills/**/*.md` as operational concepts against the pinned OKF v0.2 specification and accepted repository-root ADRs, then records the user's explicit choice.
- [ ] Public validator fixtures fail before implementation and cover ordinary hidden-directory discovery, `.agents` base/profile exclusion, root-index exclusion, and a representative unchanged `SKILL.md` frontmatter block.
- [ ] An accepted ADR and versioned profile revision reserve the complete `.agents/` tree outside bundle membership without renaming, deleting, or editing any file below it.
- [ ] `git diff 5b928e7 -- .agents` is empty, and the root index contains no `.agents` path.
- [ ] The validator, profile, agent-facing workflow, root index, and immutable log agree on the new rule and active profile version.
- [ ] The structural-freeze lapse and zeroed supervised-ingest streak are recorded without invalidating published concepts.
- [ ] Writing-for-Agents review covers the complete active instruction surface, and Standards and specification review against `5b928e7` leave no actionable finding.
- [ ] Validator fixtures, report mode, strict mode, JSON inspection, and the complete repository verification workflow pass.

## Comments

- Created under the interrupted-work rule when ticket 03's already reviewed
  stochastic evidence reached a repository-wide knowledge gate unrelated to
  its empirical question. Ticket 03 returned to open and names this ticket as
  its blocker, leaving exactly one claimed ticket.
- The starting inventory is commit `ea7cca3`, which imported 47 Markdown files
  below `.agents/skills/`. The inventory motivated an explicit boundary rather
  than any edit to those files.
- The initial handoff preferred treating skill Markdown as operational concepts
  if exclusion could not be reconciled with the pinned base. Before any
  `.agents` edit landed, the user explicitly selected the other architecture:
  `.agents` is excluded from every repository knowledge rule and remains
  byte-for-byte untouched. Profile 0.5 therefore defines it as a non-bundle
  tooling tree, while all other hidden directories retain ordinary discovery.

## Answer

_Not yet resolved._
