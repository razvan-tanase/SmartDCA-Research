---
profile: smartdca-okf/0.3
type: source-summary
title: "Source summary: the original OKF announcement (historical v0.1 context)"
description: "Summary of the June 2026 OKF v0.1 announcement, retained as historical context superseded by v0.2."
knowledge_role: evidence
status: stable
sources:
  - id: announcement
    title: "Introducing the Open Knowledge Format (Google Cloud blog)"
    resource: https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/
    source_kind: external
    retrieved_at: 2026-08-16T08:10:01Z
    upstream_version: unversioned
    sha256: c6ec0085a100af0a4a2394d13d8824a3611edd0c3b5d2829309ce2ffa5e74bf1
  - id: ticket-15
    title: "Ingest the LLM-Wiki and OKF foundation sources"
    resource: .scratch/smartdca/issues/15-ingest-llm-wiki-okf-foundation-sources
    source_kind: internal
generated:
  by: claude-code/smartdca-wiki-0.1
  at: 2026-08-16T09:06:00Z
generation_run: urn:uuid:57953b52-1968-45dc-a791-5610c4b1ec4d
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T09:05:00Z
    review_run: urn:uuid:fc6ec26a-db24-4044-9b78-983f4d090084
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T09:07:00Z
    review_run: urn:uuid:06eac3fc-e3fd-4ad9-a736-9d72d7c23ba0
---
# Source summary: the original OKF announcement (historical v0.1 context)

This is the fifth and last foundation source ingested under [Ingest the LLM-Wiki and OKF foundation sources](../../.scratch/smartdca/issues/15-ingest-llm-wiki-okf-foundation-sources.md).[^ticket-15] It is ingested **as historical v0.1 context only**. Every field-level claim in it describes the superseded version, so nothing in this concept may be cited as a current requirement; the [OKF v0.2 specification](okf-v0-2-specification.md) governs.

## Snapshot identity

The article is *Introducing the Open Knowledge Format* by Sam McVeety and Amir Hormati on the Google Cloud blog, published 2026-06-12, announcing OKF v0.1. It carries no version identifier and Google Cloud blog content is not licensed for redistribution, so no local artifact is stored. As with the trust-signals article, the origin is dynamically rendered and repeated fetches yield different bytes with identical article text, so the recorded fingerprint identifies the analysed response and is not reproducible.

## What the source says

The announcement positions OKF as an open specification that "formalizes the LLM-wiki pattern into a portable, interoperable format", vendor-neutral and friendly to both agents and humans. v0.1 is a directory of Markdown files with YAML frontmatter and a small set of conventions: no compression scheme, no runtime, no SDK. Its queryable frontmatter fields are named explicitly as `type`, `title`, `description`, `resource`, `tags`, and `timestamp`.[^announcement]

Its problem statement is fragmentation. The knowledge agents need is overwhelmingly internal — table schemas, metric meanings, runbooks, join paths, deprecation notices — and it lives scattered across catalogs with their own APIs, wikis and shared drives, code comments, and the heads of a few senior engineers. Every agent builder re-solves the same context-assembly problem and every vendor reinvents the same data models, so the answer is a format rather than another service: something anyone can produce without an SDK and consume without an integration, that survives moving between systems, lives in version control beside the code it describes, and is readable by humans and parseable by agents without a translation layer.[^announcement]

The announcement credits the pattern directly and by name: "Andrej Karpathy, the prominent AI researcher and educator, articulates this idea most crisply in his LLM Wiki gist," hyperlinking the phrase "LLM-wiki pattern" to gist `442a6bf555914893e9891c11519de94f` — the same gist ingested as the [first foundation source](karpathy-llm-wiki.md), which independently confirms that source's identity. It quotes that LLMs "don't get bored, don't forget to update a cross-reference, and can touch 15 files in one pass," and observes that the bookkeeping which makes humans abandon personal wikis is exactly what LLMs are good at. It lists the recurring bespoke instances — Obsidian vaults wired to coding agents, the `AGENTS.md` and `CLAUDE.md` family of convention files, repositories full of `index.md` and `log.md` artifacts that agents consult before doing real work, and "metadata as code" repositories — and identifies the gap as the absence of agreement on what fields every document should carry and what filenames mean.[^announcement]

Three stated design principles are carried forward unchanged into v0.2. **Minimally opinionated**: exactly one field, `type`, is required, and the specification defines the interoperability surface rather than the content model. **Producer/consumer independence**: who writes knowledge is cleanly separated from who consumes it, the format is the contract, and the tooling at each end is independently swappable. **Format, not platform**: no cloud, database, model provider, or agent framework, and never a proprietary account or SDK, because the value of a knowledge format comes from how many parties speak it rather than from who owns it. v0.1 shipped a two-pass enrichment agent, a self-contained HTML visualizer, and three sample bundles, all described as deliberate proofs of concept, and the announcement states that v0.1 is a starting point rather than a finished standard, versioned and explicitly designed for backward-compatible growth.[^announcement]

## Bearing on this bundle

The announcement's value here is genealogical and rhetorical, not technical. It establishes that the format was designed as a formalization of the same LLM-Wiki pattern this repository implements, which is why the [Karpathy proposal](karpathy-llm-wiki.md) and the specification agree on so much structure. It also names, as an existing bespoke instance, precisely the shape this repository has: a git repository of Markdown with `AGENTS.md`, `index.md`, and `log.md` that agents consult before doing real work. That is the clearest external justification for making the repository root itself the bundle rather than maintaining a separate wiki.

Its concrete field list is superseded and is retained only to read older material: `timestamp` is now `generated.at`, and the v0.1 body `# Citations` list is now the `sources` frontmatter family. This bundle has never used either v0.1 form, so no migration is required.

## Limits

Everything specific in this source is out of date by one minor version, and it predates the entire provenance, trust, lifecycle, and attestation vocabulary this bundle depends on. It is a product announcement with no normative force or conformance criteria, its "single page" characterization of the specification no longer holds, and its fingerprint is not reproducible. Cite it for lineage and design intent; cite nothing from it as a field requirement.

[^announcement]: Introducing the Open Knowledge Format (Google Cloud blog), published 2026-06-12, retrieved 2026-08-16
[^ticket-15]: [Ingest the LLM-Wiki and OKF foundation sources](../../.scratch/smartdca/issues/15-ingest-llm-wiki-okf-foundation-sources.md)
