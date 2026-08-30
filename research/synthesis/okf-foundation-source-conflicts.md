---
profile: smartdca-okf/0.5
type: synthesis
title: "Conflicts across the OKF foundation sources"
description: "Cross-source integration of the five foundation sources and the four divergences the local profile has to resolve."
knowledge_role: canonical
status: stable
sources:
  - id: karpathy
    title: "Source summary: Karpathy's LLM Wiki proposal"
    resource: references/summaries/karpathy-llm-wiki
    source_kind: internal
  - id: spec
    title: "Source summary: Open Knowledge Format v0.2 specification"
    resource: references/summaries/okf-v0-2-specification
    source_kind: internal
  - id: trust-article
    title: "Source summary: Google's OKF v0.2 trust-signals article"
    resource: references/summaries/okf-v0-2-trust-signals-article
    source_kind: internal
  - id: examples
    title: "Source summary: the OKF knowledge-catalog examples and reference implementation"
    resource: references/summaries/okf-reference-implementation-and-examples
    source_kind: internal
  - id: announcement
    title: "Source summary: the original OKF announcement (historical v0.1 context)"
    resource: references/summaries/okf-v0-1-announcement
    source_kind: internal
  - id: profile
    title: "SmartDCA Open Knowledge Format profile"
    resource: docs/knowledge/okf-profile
    source_kind: internal
generated:
  by: claude-code/smartdca-wiki-0.1
  at: 2026-08-16T09:46:00Z
generation_run: urn:uuid:efe6420b-e236-40b6-96d4-c92a95d505d2
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T09:50:00Z
    review_run: urn:uuid:870e8116-8283-4769-ad8d-e27fd596fd3a
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T10:06:00Z
    review_run: urn:uuid:6186d423-474a-44ee-8d3d-c36f938ad51a
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T10:34:00Z
    review_run: urn:uuid:86b3e187-d6a2-44c5-997c-8c06f5fdbf87
  - by: openai-codex/spec-review-0.1
    at: 2026-08-23T20:31:00Z
    review_run: urn:uuid:15c9b810-1adb-4eed-b833-45e31bcad2f1
---
# Conflicts across the OKF foundation sources

This concept exists because the five foundation sources do not speak with one voice and three of them are routinely quoted as if they were the specification. It records the authority ordering that resolves that, then the four substantive divergences and how this bundle answers each. Two of the resolutions bind the local profile, so promotion waited on a review run independent of the one that wrote them; that review is recorded in the frontmatter and its coverage is stated under Open points below.

## Authority ordering

The sources fall into four distinct authority classes, and conflating them is the failure mode this concept prevents:

1. The **v0.2 specification** is the only normative source. It alone defines conformance.[^spec]
2. The **examples and reference implementation** are self-declared proofs of concept. They evidence one reading of the specification and bind nothing.[^examples]
3. The **trust-signals article** is contemporaneous explanation of v0.2. It is authoritative about rationale and not about requirements.[^trust-article]
4. The **v0.1 announcement** is superseded. Its field-level claims describe a version this bundle never used.[^announcement]

The **LLM Wiki proposal** sits outside that ordering entirely: it is the pattern the format formalizes — the announcement credits it by name — and it prescribes workflow rather than format.[^karpathy][^announcement] Where it and the specification give different conventions for the same artifact, the specification governs.

## Conflict 1: the actor convention versus `team:` authors

The specification defines exactly three actor forms — `<producer>/<version>`, `human:<id>`, and `process:<id>` — and says a `sources[].author` credibility signal uses that convention. Its own examples then write `author: team:ga4-docs` and `author: team:finance-fpa`, and the trust article's worked example writes `author: team:data-platform`. A `team:` prefix is in none of the three forms, so the specification's normative §7 and its illustrative examples disagree.[^spec][^trust-article] The example concept captured from the official bundle uses a conformant `human:` author, so the divergence is not uniform even upstream.[^examples]

**Resolution.** This bundle follows normative §7 and rejects `team:`: the profile validates `sources[].author` against the three-form convention, so a `team:` author is reported as a finding rather than accepted.[^profile] This is a deliberate departure from upstream example practice and the reason a bundle copied verbatim from the OKF samples would fail this profile. The cost is real — team attribution has no conformant spelling short of a `process:` identifier — and this is the resolution most likely to be revisited if upstream regularizes `team:` in a later revision.

## Conflict 2: breaking changes versus renames

The specification says v0.2 supersedes v0.1 as a minor bump "except for two deliberate **breaking changes**", naming the supersession of `timestamp` by `generated.at` and of the body `# Citations` list by `sources`.[^spec] The trust article calls the same two changes "two deliberate **renames**" in a bump that is "additive, backward-compatible", and states that "a v0.1 bundle drops in unchanged".[^trust-article]

**Resolution.** Both are defensible readings of the same fallback rule — a v0.2 consumer *may* fall back to the v0.1 form, so a v0.1 bundle is consumable but not conformant on those two fields — and the disagreement is one of framing, not mechanism. This bundle adopts the specification's wording, treats the two changes as breaking, and records the fallback as a consumer courtesy rather than a compatibility guarantee. Nothing here depends on the outcome: this bundle has never used `timestamp` or a `# Citations` body list.[^announcement] The resolution matters only for how this project describes OKF versioning to others, and it is the reason the local profile states that its own 0.1-to-0.2 relabelling is metadata-only rather than borrowing the "drops in unchanged" claim.[^profile]

## Conflict 3: log and index conventions

The LLM Wiki proposal recommends one heading per log entry with a parseable prefix such as `## [2026-04-02] ingest | Article Title`, so that shell tools can slice the log.[^karpathy] The specification instead requires `## YYYY-MM-DD` date-group headings, newest first, with entries as a flat bullet list whose leading bold operation word is a convention rather than a requirement.[^spec] The two are structurally incompatible: one groups by entry, the other by date. The index files diverge less sharply but still differ, with the proposal describing a category-organized catalog with optional metadata and the specification specifying heading-grouped link entries that reuse the linked concept's description.[^karpathy][^spec]

**Resolution.** The specification's date-group form governs, because reserved-file structure is part of conformance while the proposal's suggestion is a convenience. This bundle keeps the proposal's underlying goal by making entries parseable *within* the conformant shape: a fixed pipe-delimited row carrying a UTC timestamp, operation, title, and links, and index rows carrying role, type, status, and trust.[^profile] That is a strict specialization — every event line remains a valid specification log entry — so no conflict survives.

## Conflict 4: batch ingestion and supervision

The proposal states a personal preference for ingesting one source at a time while staying involved, and explicitly offers batch ingestion of many sources with less supervision as an equally available choice.[^karpathy] Nothing in the specification, the article, or the examples constrains ingestion supervision at all; the reference producer instead runs unsupervised under a hard page cap and a same-domain host filter.[^examples]

**Resolution.** No upstream source forbids either option, so this is a project choice rather than a contradiction to adjudicate, and it is recorded here because the sources are otherwise easy to cite as permission. This bundle makes supervised one-source ingestion mandatory until structural freeze and a three-ingest stability record, and treats the reference producer's caps as precedent for bounding an automated ingest later rather than as authorization to batch now.[^profile]

## What is not in conflict

The four divergences above are the complete set found across the five sources; everything else is agreement or silence. The proposal, the announcement, the specification, and the examples concur on immutable raw sources separate from a maintained concept layer, path-based concept identity, links as an untyped graph richer than the directory tree, a schema document that tells the agent how to work, `type` as the single hard requirement, permissive consumption of unknown types and broken links, and signals recorded in frontmatter instead of a credibility score.[^karpathy][^spec][^trust-article][^examples][^announcement] The one scale figure any source offers — roughly one hundred sources and several hundred pages before plain index navigation stops sufficing — appears only in the proposal and is a personal report, which is why this bundle treats it as a threshold to watch rather than a measured limit.[^karpathy]

## Open points

Conflict 1 is the only resolution with a live cost, and it should be rechecked whenever the upstream specification is re-ingested at a new fingerprint.

**What the promoting review could and could not check.** Every claim resting on the two Apache-2.0 snapshots was re-verified against the preserved bytes: the specification snapshot does write `author: team:ga4-docs` and `author: team:finance-fpa` in its own examples while §7 admits only three actor forms, and the captured example concept does use a conformant `human:` author in its `sources` entries, so Conflict 1 stands exactly as stated and is not a conflation of `verified.by` with `sources[].author`. Two quoted specifics cannot be re-verified from this bundle at all, because their sources are non-redistributable and dynamically rendered: the proposal's per-entry log-heading form and the trust article's `team:data-platform` worked example rest on fingerprints that identify an analysed response rather than a recoverable artifact. Neither carries a resolution on its own — Conflict 3 is settled by the specification's requirement and Conflict 1 by the specification's own examples — but a future reader should know that those two quotations are attested only by the ingesting run.

The source authority ordering above has now been lifted into the canonical glossary, which this concept becoming stable is what permitted.
