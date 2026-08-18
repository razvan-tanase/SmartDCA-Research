---
profile: smartdca-okf/0.3
type: research-ticket
title: "Implement the SmartDCA OKF profile and report-only validator"
description: "Resolved task ticket implementing the SmartDCA OKF profile and its report-only validator."
knowledge_role: operational
status: stable
ticket_type: task
ticket_status: resolved
---
# Implement the SmartDCA OKF profile and report-only validator

Type: task
Status: resolved
Blocked by: 12
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

Transcribe [Design a repository-root LLM-Wiki using OKF v0.2](12-design-repository-root-llm-wiki-okf.md)'s accepted schema and complete path mapping into the normative `docs/knowledge/okf-profile.md`; write `docs/agents/llm-wiki-workflow.md`; and reduce root `AGENTS.md` to the concise invariant contract with links to both. Implement `tools/okf/validate.py` with a pinned YAML dependency and automated fixtures, but run it only in report mode against the current corpus.

The validator must report base OKF v0.2 and `smartdca-okf/0.1` results separately. Base fixtures must accept a document with only non-empty `type`, unknown types and keys, broken links, `verified` as a mapping or list, and absent `status` as stable. Profile fixtures must cover the registered schema and path mapping, role/status/risk combinations, every conditional field, `sources[].resource`, source kinds and raw fingerprints, footnote joins, actor and distinct run identities, re-verification after meaningful edits, supersession, ticket and ADR state, dependency freshness, reserved log structure, complete role-grouped index coverage/order, immutable external Markdown under a non-`.md` path, and the five required edge cases in [Design a repository-root LLM-Wiki using OKF v0.2](12-design-repository-root-llm-wiki-okf.md). Produce a complete current violation inventory. Do not add corpus frontmatter or enable blocking CI.

## Comments

- Created during resolution of [Design a repository-root LLM-Wiki using OKF v0.2](12-design-repository-root-llm-wiki-okf.md).
- Claimed on 2026-08-15 after the user chose **Continue** and [PR 1](https://github.com/razvan-tanase/SmartDCA-Research/pull/1) merged the reviewed architecture into `main`.
- Repository tooling remains separate from scientific checks under `reproducibility/checks/`.
- [Atomically migrate the repository to SmartDCA OKF 0.1](14-atomically-migrate-repository-to-okf.md), not this work, activates strict validation after the atomic corpus migration.
- Independent Standards and specification reviews completed after implementation. All actionable findings were corrected, and both final re-reviews returned PASS with no remaining finding.

## Answer

The normative [`smartdca-okf/0.1` profile](../../../docs/knowledge/okf-profile.md) now transcribes the accepted schema, complete initial path mapping, authority/lifecycle/trust model, provenance and immutable-source rules, stable identity policy, exact root index and log contracts, validation modes, and deferred scale gates. The companion [LLM-Wiki workflow](../../../docs/agents/llm-wiki-workflow.md) defines authoring, supervised ingestion, query promotion, independent review, dependency freshness, supersession, validation cadence, and batch/search gates. Root [`AGENTS.md`](../../../AGENTS.md) is reduced to the invariant contract linking both.

[`tools/okf/validate.py`](../../../tools/okf/validate.py) exposes a report-only text or JSON CLI with a pinned `PyYAML==6.0.3` dependency. It reports base OKF v0.2 conformance errors and advisory optional-family warnings separately from SmartDCA-profile findings. SmartDCA validation covers the registered types and exhaustive path policy; universal and conditional fields; roles, lifecycle, and high-risk review; source kinds, resources, footnote joins, raw fingerprints, and Git-backed artifact immutability; actor and run identities; re-verification and dependency freshness; supersession; ticket and ADR states; stable links; complete role-then-type index coverage/order; and structural plus Git-backed immutable root log history. Findings return exit status 0; invalid invocation returns 2. No strict mode or CI hook was added.

Nineteen public-CLI fixtures pass, including the deliberately permissive base cases and all five required edge cases. All four scientific checks also pass. The complete reproducible [current violation inventory](../../../reports/okf/current-violations.json) records 39 Markdown concepts, 39 base conformance findings, three base advisory warnings, and 71 profile findings. This intentional nonconformance is the input to [Atomically migrate the repository to SmartDCA OKF 0.1](14-atomically-migrate-repository-to-okf.md); this ticket added no corpus frontmatter and did not enable blocking CI.
