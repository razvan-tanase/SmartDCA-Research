---
profile: smartdca-okf/0.5
type: research-ticket
title: "Ingest the LLM-Wiki and OKF foundation sources"
description: "Resolved research ticket ingesting the five LLM-Wiki and OKF foundation sources one at a time."
knowledge_role: operational
status: stable
ticket_type: research
ticket_status: resolved
---
# Ingest the LLM-Wiki and OKF foundation sources

Type: research
Status: resolved
Blocked by: 14
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

Run five supervised one-source ingest cycles in order: Karpathy's LLM-Wiki proposal; normative OKF v0.2 `SPEC.md`; Google's OKF v0.2 trust-signals article; the official knowledge-catalog examples and reference implementation; and the original OKF announcement marked as historical v0.1 context.

For each source, preserve exact upstream bytes under a non-`.md` path only when redistribution permits; always record source kind, authoritative origin, ISO retrieval time, upstream version or `unversioned`, and raw-byte SHA-256; create a conformant source-summary concept; update the complete index; record a conformant log event; run ingest lint; and apply risk-tier review. Create or update a synthesis only when reusable cross-source integration or conflict resolution warrants it. Record whether the first three ingests satisfy the three-ingest stability prerequisite, but do not claim the complete batch gate before [Extract initial semantic concepts and certify structural freeze](16-extract-semantic-concepts-certify-freeze.md) certifies structural freeze and do not batch these sources.

## Comments

- Created during resolution of [Design a repository-root LLM-Wiki using OKF v0.2](12-design-repository-root-llm-wiki-okf.md).
- Normative specification claims must remain distinct from blog explanation and non-normative examples.
- Claimed on 2026-08-16. The first clause was blocked immediately: profile 0.1's path mapping is exhaustive and registers no `source-summary` destination, while profile 0.1 also requires a profile version change to assign a new path, so no conformant summary could exist. The user chose to resolve that inside this ticket by publishing `smartdca-okf/0.2` rather than deferring to [Extract initial semantic concepts and certify structural freeze](16-extract-semantic-concepts-certify-freeze.md).

## Answer

All five sources are ingested individually and in order, behind a prerequisite profile revision.

### Prerequisite: profile 0.2

[Assign source-summary and synthesis paths in profile 0.2](../../../docs/adr/0005-assign-source-summary-and-synthesis-paths.md) assigns exactly two paths — `references/summaries/*.md` for `source-summary` evidence and `research/synthesis/*.md` for `synthesis` canonical concepts — and every concept, the validator, and the fixtures now declare `smartdca-okf/0.2`. Relabelling is defined as a metadata migration: it does not update `generated.at`, demote a high-risk concept, or invalidate a recorded verification, and only concepts whose bodies actually changed carry a new generation time. `definition`, `theorem`, and `experiment-report` remain unassigned for the extraction ticket. The profile's OKF citation also stopped being declared scope and now names the fingerprinted snapshot.

### The five ingests

| # | Source | Kind | Upstream version | Bytes preserved |
|---|---|---|---|---|
| 1 | [Karpathy's LLM Wiki proposal](../../../references/summaries/karpathy-llm-wiki.md) | pattern proposal | `unversioned` | No — gist carries no redistribution licence |
| 2 | [OKF v0.2 specification](../../../references/summaries/okf-v0-2-specification.md) | normative | `0.2` (commit `3fcbb9f8`) | Yes — Apache-2.0 |
| 3 | [OKF v0.2 trust-signals article](../../../references/summaries/okf-v0-2-trust-signals-article.md) | explanation | `unversioned` | No — blog content |
| 4 | [Knowledge-catalog examples and reference implementation](../../../references/summaries/okf-reference-implementation-and-examples.md) | non-normative example | commit `780fe9d3` | Yes — Apache-2.0, two artifacts |
| 5 | [Original OKF announcement](../../../references/summaries/okf-v0-1-announcement.md) | superseded announcement | `unversioned` | No — blog content |

Each summary records source kind, authoritative origin, ISO 8601 retrieval time, upstream version or `unversioned`, and the SHA-256 of the raw bytes; joins every external source from a body footnote; and states explicitly what the source does not settle. Each ingest appended its own index row and log event. Risk-tier review applies: `source-summary` is evidence rather than high-risk, so the five are stable with a recorded review under a run distinct from the run that wrote them; the synthesis is canonical high-risk and stays draft. That asymmetry is deliberate — [ADR 0005](../../../docs/adr/0005-assign-source-summary-and-synthesis-paths.md) is equally high-risk canonical but transcribes a decision the user made in this session under an independent review run, following the precedent set by the bootstrap promotions in [the migration](14-atomically-migrate-repository-to-okf.md), whereas the synthesis advances new claims about external sources and has to be checked by a run that did not write it.

### Synthesis

A synthesis was warranted, so [Conflicts across the OKF foundation sources](../../../research/synthesis/okf-foundation-source-conflicts.md) records a four-class authority ordering and four divergences: the specification's three-form actor convention against `team:` authors in its own examples and in the trust article (this bundle follows normative §7 and reports `team:`, which is the one resolution with a live cost); the specification calling two v0.2 changes breaking where the article calls them renames in a bundle that "drops in unchanged"; the proposal's per-entry log headings against the specification's date-group form, which this bundle satisfies by specializing inside the conformant shape; and batch-versus-supervised ingestion, where no source constrains anything and the gate is a project choice. It remains draft because a high-risk canonical concept cannot become stable through its generating run.

### Verification performed

Every quoted or attributed claim in the five summaries was checked back against the fetched bytes. Two drafting errors were found and corrected: the reference-implementation README argues nine grounds for Markdown-plus-frontmatter, not eight, and the announcement hyperlinks the exact gist ingested as source 1, which independently corroborates that source's identity. `python -m unittest tools.okf.tests.test_validate_cli` passes 25 fixtures, `python tools/okf/validate.py . --strict` is clean on both layers with Git-history checks active, and all four scientific checks under `reproducibility/checks/` still pass.

Independent Standards and Spec reviews then ran against the diff and the ticket. Their actionable findings are resolved: the profile now states that one summary covers one source while allowing several artifacts of a single upstream edition (source 4 has two), and the glossary term matches; the profile documents the `author` actor rule the validator already enforced, which is what the synthesis's Conflict 1 resolution depends on; the duplicated version-change sentence and the false "changes nothing else" claim are gone; the synthesis's draft rationale no longer asserts a rule that its own sibling ADR contradicts; the map and the two corrected summaries now record the generation and re-review events their changed bodies require; and the overstated per-cycle lint claim is replaced by the deviations below.

### Deviations from the ideal cycle

Three, all disclosed rather than papered over. All five sources were fetched in **one up-front pass** at 08:10Z to establish fingerprints before any writing, so the specification snapshot was already available when the prerequisite profile revision cited it at 08:24Z — the five *cycles* (summary, index row, log event) then ran one at a time in the order the ticket names, but the fetch step was not serialized. Lint ran on the **accumulating corpus** after the summaries and again after the synthesis and the review fixes, not once per cycle. The semantic re-check of quoted claims was a **single pass over all five** summaries at 09:05Z rather than five reviews interleaved with the ingests, so the review is batched even though the ingestion is not.

### Three-ingest prerequisite

Recorded, not claimed. The first three ingests — proposal, specification, trust article — completed consecutively and under supervision with no schema change, no conformance failure, and no high-severity semantic correction; both corrections above were low-severity accuracy fixes inside a summary body, and both landed outside the first three. The freeze ticket has two qualifiers to weigh. A schema change (profile 0.2) occurred in this ticket immediately *before* ingest 1, so the streak is clean only under the reading that the gate counts schema changes during the three ingests rather than anywhere in the same ticket. A second, smaller schema change followed the fifth ingest, when the review round added the one-source and `author` rules to the profile. The complete batch gate is deliberately not evaluated here and the sources were not batched.

### Limits

Two of the five origins are dynamically rendered: repeated fetches of the two Google Cloud blog articles returned different bytes with identical article text, so their fingerprints identify the analysed response and cannot detect a later change. With no redistributable artifact for those two or for the gist, three of five sources have fingerprints that are recorded but not independently verifiable. The synthesis's authority-ordering claim is reusable canonical vocabulary but was not added to [`CONTEXT.md`](../../../CONTEXT.md) because a stable glossary may not depend on a draft concept; only **source summary** was added, and the authority ordering waits on the freeze review. Every review here was performed by the same actor under a distinct review run, which is what the profile requires and what the migration established, but it is not review by a different party; that standing limitation is unchanged by this ticket. No mathematical content was touched.
