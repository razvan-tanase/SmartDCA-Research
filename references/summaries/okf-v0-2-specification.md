---
profile: smartdca-okf/0.4
type: source-summary
title: "Source summary: Open Knowledge Format v0.2 specification"
description: "Summary of the normative OKF v0.2 specification, its conformance criteria, and its optional metadata families."
knowledge_role: evidence
status: stable
sources:
  - id: okf-spec
    title: "Open Knowledge Format (OKF) specification, version 0.2"
    resource: https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/SPEC.md
    source_kind: external
    retrieved_at: 2026-08-16T08:10:00Z
    upstream_version: "0.2"
    sha256: 5a3311d270bebb16d558010e75064f5b75323f284992641732b1c8097511f948
    local_artifact: references/raw/okf-spec/0.2/SPEC.md.raw
  - id: ticket-15
    title: "Ingest the LLM-Wiki and OKF foundation sources"
    resource: .scratch/smartdca/issues/15-ingest-llm-wiki-okf-foundation-sources
    source_kind: internal
generated:
  by: claude-code/smartdca-wiki-0.1
  at: 2026-08-16T08:38:00Z
generation_run: urn:uuid:57953b52-1968-45dc-a791-5610c4b1ec4d
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T09:05:00Z
    review_run: urn:uuid:fc6ec26a-db24-4044-9b78-983f4d090084
---
# Source summary: Open Knowledge Format v0.2 specification

This is the second foundation source ingested under [Ingest the LLM-Wiki and OKF foundation sources](../../.scratch/smartdca/issues/15-ingest-llm-wiki-okf-foundation-sources.md).[^ticket-15] It is the **normative** source for this bundle: everything the [SmartDCA OKF profile](../../docs/knowledge/okf-profile.md) specializes is defined here. Claims in this summary are specification statements, not blog explanation and not example convention.

## Snapshot identity

The snapshot is the self-declared version 0.2 of `okf/SPEC.md` from the `GoogleCloudPlatform/knowledge-catalog` repository, whose last upstream change to that path at retrieval time was commit `3fcbb9f828c2f23d109c855ee403c3a4c81f3a96` (2026-07-24). The repository is Apache-2.0 licensed, so the exact bytes are preserved at [`references/raw/okf-spec/0.2/SPEC.md.raw`](../raw/okf-spec/0.2/SPEC.md.raw) and are byte-verifiable against the recorded fingerprint. The origin URL tracks the moving `main` branch, so the fingerprint, not the URL, identifies this edition.

## Conformance is the whole of the hard requirement

A bundle is conformant with v0.2 if every non-reserved `.md` file contains a parseable YAML frontmatter block, every such block contains a non-empty `type`, and every reserved filename (`index.md`, `log.md`) follows its defined structure when present. `type` is the only always-required key: a concept carrying just `type` is fully conformant. Consumers MUST NOT reject a bundle for missing optional frontmatter, unknown `type` values, unknown additional keys, broken cross-links, or missing `index.md` files, and MUST treat a bare `verified` mapping as a one-element list. Everything else is soft guidance.[^okf-spec]

## Structure, identity, and linking

A bundle is a directory tree of Markdown files, distributable as a git repository, an archive, or a subdirectory of a larger repository. A Concept ID is the concept file's bundle path with `.md` removed. `index.md` and `log.md` are reserved at any level; all other `.md` files are concepts. Links are ordinary Markdown links, either bundle-relative beginning with `/` (recommended, because it survives moves within a subdirectory) or relative; a link asserts an untyped relationship whose kind lives in the surrounding prose. A `references/` subdirectory conventionally mirrors external material, run instructions, or code as first-class concepts — a naming convention, not a requirement.[^okf-spec]

## The optional families

`sources` records the materials a concept derives from. Each entry requires `resource`, which names either a followable artifact (URL, bundle-relative path, path into `references/`) or a population or scope descriptor such as "all queries in project X"; `id` is optional but SHOULD be present when the body cites the source; `title` is optional. Per-claim attribution uses a Markdown footnote whose label equals a `sources[].id`, and the label — not footnote prose and not a positional index — is the join key, precisely because agents constantly rewrite and reorder these documents. Entries MAY carry the objective credibility signals `author`, `usage_count`, and `last_modified`, framed by a `usage_window` sibling. The specification deliberately records signals rather than a credibility score, on the grounds that a score is subjective, unportable between consumers, and stale the moment it is written. Lineage is expressed through links rather than a dedicated field, and deeper lineage is out of scope for v0.2.[^okf-spec]

`generated: { by, at }` records how the current content was produced and when it last meaningfully changed; `by` is required within it. `verified` is a list of `{ by, at }` confirmation events and is kept deliberately distinct from `generated`, because who wrote a concept need not be who confirmed it; content can change without re-confirmation and facts can be re-confirmed without regeneration. Consumers derive three advisory **trust tiers** from `verified`: absent is unverified, non-`human:` actors only is machine-confirmed, and any `human:<id>` actor is human-reviewed. Tiers are signals, never access control. `status` moves a concept through `draft`, `stable`, and `deprecated`, with absence meaning `stable`. `stale_after` is a single absolute `YYYY-MM-DD` date, chosen over a relative time-to-live so staleness is a plain date comparison independent of when the concept was read.[^okf-spec]

Identity-bearing fields use one **actor convention**: `<producer>/<version>` for agents and tools, `human:<id>` for people, `process:<id>` for automated processes. Producers MUST use the `human:` prefix for hand-authored or human-confirmed content, because trust classification keys off it.[^okf-spec]

## Reserved files and attested computation

An `index.md` may appear in any directory to support progressive disclosure; it carries no frontmatter, with the single exception that a bundle-root `index.md` MAY carry `okf_version`. Its body groups linked entries under headings and entries SHOULD reuse the linked concept's description. A `log.md` may appear at any level and is a flat list of date-grouped entries, newest first, with `## YYYY-MM-DD` headings required and the leading bold operation word a convention rather than a requirement.[^okf-spec]

The new `Attested Computation` type carries a sanctioned way to compute a value plus the means to confirm the sanctioned thing ran: a required `runtime`, typed `parameters` the agent may fill but never author, an optional `computation` path or an inline `# Computation` fence, an `executor` whose `receipt` declares what a run must return, and a deterministic no-LLM `attester` that turns a receipt into a verdict. Receipts and verdicts are runtime artifacts and are explicitly not stored in the bundle. Verification and attestation are distinct and both required: `verified` confirms the definition still matches policy, slowly and at document level; attestation confirms one run produced its value correctly, per call. The full runtime protocol, attester ABI and sandboxing, attestation caching, and semantic-layer templates are deferred to a future revision.[^okf-spec]

## Versioning and the relationship to v0.1

Revisions are `<major>.<minor>`; a minor bump adds backward-compatible optional fields and conventional headings, a major bump may break. Bundles MAY declare `okf_version: "0.2"` in the bundle-root `index.md`. The specification states that v0.2 supersedes v0.1 as a minor bump **except for two deliberate breaking changes**: `timestamp` is superseded by `generated.at`, and the body `# Citations` list is superseded by `sources`. In both cases a v0.2 consumer MAY fall back to the v0.1 form. Everything else — bundle structure, reserved filenames, the required `type`, the recommended `title`, `description`, `resource`, and `tags`, cross-linking, index and log files, and permissive conformance — carries forward unchanged.[^okf-spec]

## Bearing on this bundle

This specification is the layer the local profile treats as its floor: the profile's base-OKF checks implement exactly the three conformance criteria and the five mandated permissive behaviours above, and its stricter rules are declared as a separate validation layer so a document can conform to OKF while failing the profile. Three specification choices are adopted verbatim rather than specialized — footnote labels keyed to `sources[].id`, the actor convention, and the absolute-date form of `stale_after`. Two are specialized more strictly: this bundle requires `type` plus five further universal fields, and it constrains index and log formats to parseable row grammars that the specification leaves loose. One is currently in tension with the specification's own examples; that conflict is recorded in [Conflicts across the OKF foundation sources](../../research/synthesis/okf-foundation-source-conflicts.md).

## Limits

The specification fixes interfaces, not packaging, and explicitly declines to define a concept-type taxonomy, storage or serving infrastructure, or a replacement for domain schemas. It therefore cannot settle any question about what belongs in *this* project's type vocabulary or path mapping. Its normative force also stops at conformance: nearly all of the metadata guidance above is `SHOULD`, so a bundle can be fully conformant while recording no provenance or trust at all.

[^okf-spec]: Open Knowledge Format (OKF) specification, version 0.2, retrieved 2026-08-16
[^ticket-15]: [Ingest the LLM-Wiki and OKF foundation sources](../../.scratch/smartdca/issues/15-ingest-llm-wiki-okf-foundation-sources.md)
