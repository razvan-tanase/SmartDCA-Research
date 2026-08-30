---
profile: smartdca-okf/0.5
type: research-ticket
title: "Exclude repository-local agent tooling from the OKF bundle"
description: "Resolved task ticket reserving the .agents tooling tree outside the SmartDCA knowledge bundle without changing its files."
knowledge_role: operational
status: stable
original_record: true
ticket_type: task
ticket_status: resolved
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-30T10:07:02Z
generation_run: urn:uuid:b3da5f0b-dc5e-45f3-840f-51f3445d0f32
verified:
  - by: openai-codex/standards-review-0.1
    at: 2026-08-30T10:09:30Z
    review_run: urn:uuid:0cf9e427-2b3e-40eb-a2f3-d5f93b17e175
  - by: openai-codex/spec-review-0.1
    at: 2026-08-30T10:09:30Z
    review_run: urn:uuid:0423e158-4c18-4bb7-bfe3-ba3e7b07b882
  - by: openai-codex/writing-for-agents-0.1
    at: 2026-08-30T10:09:30Z
    review_run: urn:uuid:d86b1a84-4750-43ec-9c0e-62ff07a8587e
---
# 08 — Exclude repository-local agent tooling from the OKF bundle

Type: task
Status: resolved
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

- [x] The decision evaluates both excluding `.agents` as executable tooling and treating `.agents/skills/**/*.md` as operational concepts against the pinned OKF v0.2 specification and accepted repository-root ADRs, then records the user's explicit choice.
- [x] Public validator fixtures fail before implementation and cover ordinary hidden-directory discovery, `.agents` base/profile exclusion, root-index exclusion, and a representative unchanged `SKILL.md` frontmatter block.
- [x] An accepted ADR and versioned profile revision reserve the complete `.agents/` tree outside bundle membership without renaming, deleting, or editing any file below it.
- [x] `git diff 5b928e7 -- .agents` is empty, and the root index contains no `.agents` path.
- [x] The validator, profile, agent-facing workflow, root index, and immutable log agree on the new rule and active profile version.
- [x] The structural-freeze lapse and zeroed supervised-ingest streak are recorded without invalidating published concepts.
- [x] Writing-for-Agents review covers the complete active instruction surface, and Standards and specification review against `5b928e7` leave no actionable finding.
- [x] Validator fixtures, report mode, strict mode, JSON inspection, and the complete repository verification workflow pass.

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
- Independent Standards, specification, and Writing-for-Agents reviews against
  `5b928e7` found no remaining actionable issue. The complete instruction
  surface consistently describes a declared bundle view rather than claiming
  that the raw repository is itself OKF-conformant.

## Answer

The accepted [tooling-boundary decision](../../../../../docs/adr/0009-exclude-agents-tooling-from-knowledge-bundle.md)
records the user's choice: root `.agents/` is executable repository tooling,
not SmartDCA knowledge. Treating its 47 imported Markdown files as operational
concepts was rejected because that would transfer third-party-style tool
payloads into the repository knowledge policy and require mass metadata edits.
No file below `.agents/` was renamed, deleted, or edited.

Profile `smartdca-okf/0.5` now defines the repository root as the anchor of a
declared bundle view. Root `.git/` and `.agents/` are excluded before both base
member checks and SmartDCA-profile validation; every other hidden-directory
Markdown path remains discoverable. Because base OKF v0.2 supplies no
ignore-tree mechanism, validator output explicitly reports
`scope: smartdca_bundle_members` and
`raw_repository_conformance_claimed: false` instead of making an unqualified
raw-repository conformance claim.

Public fixtures cover the pre-implementation failure and the accepted rule:
ordinary hidden paths are still scanned, `.agents` contributes no base or
profile finding, its paths never enter the root index, and representative
`SKILL.md` frontmatter remains unchanged. The complete fixture suite, human and
JSON report modes, strict mode, and repository verification workflow pass.
`git diff 5b928e7 -- .agents` is empty, and the index contains no `.agents`
member.

The profile revision deliberately lapses the prior structural-freeze
certification and resets the supervised-ingest streak to zero. It does not
invalidate any published Concept ID, lifecycle state, or verification. The
normative profile, amended root-bundle decision, LLM-Wiki workflow, glossary,
validator, index, and append-only log now state the same boundary.
