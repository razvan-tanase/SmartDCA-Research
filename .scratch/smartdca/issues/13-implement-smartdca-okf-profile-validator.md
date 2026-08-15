# Implement the SmartDCA OKF profile and report-only validator

Type: task
Status: open
Blocked by: 12
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

Transcribe ticket 12's accepted schema and complete path mapping into the normative `docs/knowledge/okf-profile.md`; write `docs/agents/llm-wiki-workflow.md`; and reduce root `AGENTS.md` to the concise invariant contract with links to both. Implement `tools/okf/validate.py` with a pinned YAML dependency and automated fixtures, but run it only in report mode against the current corpus.

The validator must report base OKF v0.2 and `smartdca-okf/0.1` results separately. Base fixtures must accept a document with only non-empty `type`, unknown types and keys, broken links, `verified` as a mapping or list, and absent `status` as stable. Profile fixtures must cover the registered schema and path mapping, role/status/risk combinations, every conditional field, `sources[].resource`, source kinds and raw fingerprints, footnote joins, actor and distinct run identities, re-verification after meaningful edits, supersession, ticket and ADR state, dependency freshness, reserved log structure, complete role-grouped index coverage/order, immutable external Markdown under a non-`.md` path, and ticket 12's five required edge cases. Produce a complete current violation inventory. Do not add corpus frontmatter or enable blocking CI.

## Comments

- Created during resolution of the independently reviewed ticket-12 architecture.
- Repository tooling remains separate from scientific checks under `reproducibility/checks/`.
- Ticket 14, not this ticket, activates strict validation after the atomic corpus migration.

## Answer

Pending.
