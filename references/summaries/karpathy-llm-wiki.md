---
profile: smartdca-okf/0.3
type: source-summary
title: "Source summary: Karpathy's LLM Wiki proposal"
description: "Summary of the LLM Wiki gist that proposes an LLM-maintained persistent wiki over immutable raw sources."
knowledge_role: evidence
status: stable
sources:
  - id: llm-wiki
    title: "LLM Wiki (Andrej Karpathy, gist)"
    resource: https://gist.githubusercontent.com/karpathy/442a6bf555914893e9891c11519de94f/raw/
    source_kind: external
    retrieved_at: 2026-08-16T08:10:00Z
    upstream_version: unversioned
    sha256: dc3efe98ae62f23dd08acad13aba2e95287beb20b6bec2f4af0423557fe37401
    author: human:github:karpathy
  - id: ticket-15
    title: "Ingest the LLM-Wiki and OKF foundation sources"
    resource: .scratch/smartdca/issues/15-ingest-llm-wiki-okf-foundation-sources
    source_kind: internal
generated:
  by: claude-code/smartdca-wiki-0.1
  at: 2026-08-16T08:32:00Z
generation_run: urn:uuid:57953b52-1968-45dc-a791-5610c4b1ec4d
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T09:05:00Z
    review_run: urn:uuid:fc6ec26a-db24-4044-9b78-983f4d090084
---
# Source summary: Karpathy's LLM Wiki proposal

This is the first of the five foundation sources ingested under [Ingest the LLM-Wiki and OKF foundation sources](../../.scratch/smartdca/issues/15-ingest-llm-wiki-okf-foundation-sources.md).[^ticket-15] It is the origin of the LLM-Wiki pattern this repository implements.

## Snapshot identity

The source is a public GitHub gist titled *LLM Wiki*, authored by Andrej Karpathy and fetched from its raw endpoint; the human-readable page is [gist 442a6bf5](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). It carries no version marker and the gist revision API was unavailable at retrieval time, so its `upstream_version` is `unversioned` and the SHA-256 in this concept's frontmatter is the only edition identifier. The gist bears no redistribution licence, so no local artifact is stored: the fingerprint is recorded, the bytes are not.

## What the source says

The proposal contrasts retrieval-augmented generation, where the model rediscovers knowledge from raw documents on every question, with a wiki the model **incrementally builds and maintains** as a persistent, compounding artifact. Cross-references, flagged contradictions, and synthesis are compiled once and then kept current rather than re-derived per query. The human curates sources, explores, and asks questions; the model does the summarizing, cross-referencing, filing, and bookkeeping.[^llm-wiki]

Three layers are specified. **Raw sources** are a curated, immutable collection the model reads but never modifies. **The wiki** is a directory of model-generated Markdown — summaries, entity pages, concept pages, comparisons, an overview, a synthesis — owned entirely by the model. **The schema** is a document such as `CLAUDE.md` or `AGENTS.md` that tells the model how the wiki is structured and what workflows to follow, co-evolved by the human and the model.[^llm-wiki]

Four operations are described. **Ingest** reads one source, discusses takeaways, writes a summary page, updates the index, updates affected entity and concept pages, and appends a log entry, potentially touching ten to fifteen pages; the author states a personal preference for one source at a time with the human involved, while noting that batch ingestion with less supervision is also possible. **Query** searches the wiki and synthesizes a cited answer, with the explicit insight that good answers can be filed back as new pages rather than lost to chat history. **Lint** is a periodic health check for contradictions, claims superseded by newer sources, orphan pages, missing pages for mentioned concepts, missing cross-references, and data gaps. Two special files support navigation: a content-oriented `index.md` catalog updated on every ingest and read first when answering, and a chronological append-only `log.md`. The author reports that this works "surprisingly well at moderate scale (~100 sources, ~hundreds of pages)" and avoids embedding-based retrieval infrastructure; a proper search engine is offered as optional tooling beyond that point.[^llm-wiki]

The closing rationale is that the bookkeeping, not the reading or thinking, is what makes humans abandon knowledge bases, and that models do not get bored and can touch fifteen files in one pass. The document explicitly positions itself as abstract — an idea file to be handed to an agent, whose directory structure, schema conventions, page formats, and tooling are all left to the reader's domain.[^llm-wiki]

## Bearing on this bundle

Almost every structural choice in this repository traces to this source: immutable raw sources under `references/raw/`, an agent-maintained concept layer, `AGENTS.md` as the schema document, the ingest/query/lint operation triple, the complete `index.md`, the append-only `log.md`, and the deferral of hybrid search until roughly one hundred sources. Two divergences are deliberate. This bundle's schema is a normative, machine-validated profile rather than a co-evolved convention file, and it keeps supervised ingestion mandatory until an explicit gate instead of treating batch ingestion as an equal option. The source is a pattern proposal and carries no conformance criteria, so it constrains nothing mechanically; where it and the [Open Knowledge Format specification](okf-v0-2-specification.md) prescribe different conventions for the same file, the specification governs.

## Limits

The document is deliberately implementation-free and offers no schema, no validation rules, and no trust or provenance model — the gap the Open Knowledge Format later fills. Its scale claim is a personal report, not a measurement. Because the bytes are unlicensed for redistribution and the gist is unversioned, a future reader can only re-fetch the current edition and compare fingerprints to detect that it changed, not recover this edition.

[^llm-wiki]: LLM Wiki (Andrej Karpathy, gist), retrieved 2026-08-16
[^ticket-15]: [Ingest the LLM-Wiki and OKF foundation sources](../../.scratch/smartdca/issues/15-ingest-llm-wiki-okf-foundation-sources.md)
