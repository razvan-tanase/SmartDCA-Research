---
profile: smartdca-okf/0.5
type: source-summary
title: "Source summary: the OKF knowledge-catalog examples and reference implementation"
description: "Summary of the official OKF reference producer, visualizer, and sample bundles, and what their conventions do not settle."
knowledge_role: evidence
status: stable
sources:
  - id: okf-readme
    title: "Open Knowledge Format reference implementation README (knowledge-catalog)"
    resource: https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/README.md
    source_kind: external
    retrieved_at: 2026-08-16T08:10:01Z
    upstream_version: 780fe9d30b5bbca8931256edf1d0290d6bda5462
    sha256: e7f3bec9a90a5cbf1ba16c91a879d155d7a826f0ecc4fe028df01b7bb13ea786
    local_artifact: references/raw/okf-reference-implementation/780fe9d3/README.md.raw
  - id: acme-example
    title: "Example concept: acme_retail metrics/gross-margin.md (knowledge-catalog)"
    resource: https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/bundles/acme_retail/metrics/gross-margin.md
    source_kind: external
    retrieved_at: 2026-08-16T08:10:01Z
    upstream_version: 780fe9d30b5bbca8931256edf1d0290d6bda5462
    sha256: aeb3589af67e70c27c54cfaadf81fdc3165461dd27fa6439ed60d79275b3a0fa
    local_artifact: references/raw/okf-reference-implementation/780fe9d3/acme-retail-gross-margin.md.raw
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
# Source summary: the OKF knowledge-catalog examples and reference implementation

This is the fourth foundation source ingested under [Ingest the LLM-Wiki and OKF foundation sources](../../.scratch/smartdca/issues/15-ingest-llm-wiki-okf-foundation-sources.md).[^ticket-15] It is **non-normative example material**. Both upstream sources describe themselves as proofs of concept, so nothing here constrains this bundle; example conventions are evidence of one reading of the specification, not a requirement.

## Snapshot identity

Two artifacts were captured from the Apache-2.0 licensed `GoogleCloudPlatform/knowledge-catalog` repository at commit `780fe9d30b5bbca8931256edf1d0290d6bda5462` (2026-07-24): the `okf/README.md` that documents the reference producer and consumer, and one representative example concept, `okf/bundles/acme_retail/metrics/gross-margin.md`, from the companion bundle the trust article uses. Both are preserved byte-exactly at [`references/raw/okf-reference-implementation/780fe9d3/README.md.raw`](../raw/okf-reference-implementation/780fe9d3/README.md.raw) and [`acme-retail-gross-margin.md.raw`](../raw/okf-reference-implementation/780fe9d3/acme-retail-gross-margin.md.raw). Both origin URLs track the moving `main` branch, so the commit and the fingerprints identify the edition; the artifact directory uses the abbreviated commit while `upstream_version` carries the full one.

## What the reference implementation is

The README states outright that the repository is primarily about the format, that the format is not tied to any agent, framework, model provider, or serving system, and that the agent it ships is a proof of concept demonstrating *one* way to produce bundles. It argues for plain Markdown plus frontmatter over a service-owned metadata store on nine grounds: readability without an SDK, version control out of the box, portability without a proprietary API, a deliberate split between queryable frontmatter and readable body, first-class trust and provenance, minimal opinionation with free extensibility, composition with existing Markdown tooling, progressive disclosure through generated `index.md` files, and a graph rather than merely a tree because concepts cross-link.[^okf-readme]

The producer is a two-pass enrichment agent: a metadata pass writes one document per concept the source advertises, then a web pass runs the model as its own crawler over seed URLs, deciding per fetched page whether to enrich existing concepts, mint a standalone `references/<slug>` document, or skip, under a hard page cap and a same-domain host filter enforced inside the tool so the agent cannot overrun. The consumer is a `visualize` subcommand that renders a bundle as one self-contained HTML file with a force-directed graph coloured by type, a detail panel that rewires internal links to navigate inside the viewer, a "Cited by" backlinks list computed from the reverse link graph, search, type filtering, and switchable layouts. Four sample bundles are checked in — GA4 e-commerce, Stack Overflow, Bitcoin, and Acme Retail — each pairing a recipe that records the seed URLs and exact command with the bundle it produced.[^okf-readme]

## What the example concept shows

The `gross-margin` metric is the most informative single example because it demonstrates conventions the specification does not mandate. It carries `generated` by an agent actor and `verified` by a `human:` actor, `status: stable`, and `stale_after: 2026-12-31` with a body section that explains the freshness reasoning in prose. It cites two policy concepts by bundle-relative path in `sources`, each with `author` and `last_modified` credibility signals, and attributes its definitional claim with a `[^margin-standard]` footnote. It links a separate `Attested Computation` concept and states that consumers MUST run and attest it, keeping the readable metric and the sanctioned computation in different concepts. It preserves a superseded definition as a distinct `status: deprecated` concept for historical query reproducibility instead of deleting it, and explains what changed and why in the body.[^acme-example]

Two details are conventions invented by the example rather than specification features. It carries a producer-defined `not:` frontmatter key listing a forbidden alternative term with a reason and a replacement — the extensibility escape hatch used to encode exactly the "avoid this phrasing" discipline this project keeps in prose. It also declares a second source, `revenue-policy`, that appears only as a trailing footnote definition and is never joined to any claim in the body.[^acme-example]

## Bearing on this bundle

The example independently corroborates four choices already made here: preserving a superseded definition at its own identity rather than deleting it, separating a readable narrative concept from the machine-checkable artifact it links, recording freshness reasoning in the body alongside the frontmatter date, and using footnote joins for definitional claims. Its `not:` key is the closest upstream analogue of this bundle's glossary *Avoid* lines, and it is evidence that encoding forbidden alternatives as structured metadata is a viable later option rather than an invention. The reference producer's hard page cap and host filter are a useful precedent for bounding an automated ingest, but no automated ingest is in scope here — ingestion in this bundle is supervised and one source at a time.

The example's unjoined `revenue-policy` source is a concrete instance of the looseness this bundle deliberately tightens: the specification only says `id` SHOULD be present when the body cites a source, so an unjoined declared source is conformant upstream while this profile reports it for external and high-risk canonical sources.

## Limits

Neither artifact is normative and neither is a conformance test. The README documents an implementation that requires BigQuery and Gemini credentials, so nothing in it is reproducible here, and its claims about the format restate the specification and the announcement without adding authority. The example bundle is a fictional retail company built for a blog post; its type vocabulary (`Metric`, `BigQuery Table`, `Attested Computation`) and directory layout are one producer's choices and settle nothing about this project's registered types or path mapping. A single example concept was captured rather than the full bundle, so conventions visible only in other files of that bundle are outside this snapshot.

[^okf-readme]: Open Knowledge Format reference implementation README (knowledge-catalog), commit 780fe9d3, retrieved 2026-08-16
[^acme-example]: Example concept acme_retail metrics/gross-margin.md (knowledge-catalog), commit 780fe9d3, retrieved 2026-08-16
[^ticket-15]: [Ingest the LLM-Wiki and OKF foundation sources](../../.scratch/smartdca/issues/15-ingest-llm-wiki-okf-foundation-sources.md)
