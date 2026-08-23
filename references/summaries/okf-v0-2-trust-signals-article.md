---
profile: smartdca-okf/0.4
type: source-summary
title: "Source summary: Google's OKF v0.2 trust-signals article"
description: "Summary of the non-normative Google Cloud article explaining why OKF v0.2 adds provenance, trust, and attestation."
knowledge_role: evidence
status: stable
sources:
  - id: trust-article
    title: "Open Knowledge format v0.2 tackles agentic trust (Google Cloud blog)"
    resource: https://cloud.google.com/blog/products/data-analytics/okf-v0-2-adds-trust-signals/
    source_kind: external
    retrieved_at: 2026-08-16T08:10:00Z
    upstream_version: unversioned
    sha256: 02dd997074e2ba05e297226de2209cc8a23cf5c891218850ebdb026e219ed7ab
  - id: ticket-15
    title: "Ingest the LLM-Wiki and OKF foundation sources"
    resource: .scratch/smartdca/issues/15-ingest-llm-wiki-okf-foundation-sources
    source_kind: internal
generated:
  by: claude-code/smartdca-wiki-0.1
  at: 2026-08-16T08:44:00Z
generation_run: urn:uuid:57953b52-1968-45dc-a791-5610c4b1ec4d
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T09:05:00Z
    review_run: urn:uuid:fc6ec26a-db24-4044-9b78-983f4d090084
---
# Source summary: Google's OKF v0.2 trust-signals article

This is the third foundation source ingested under [Ingest the LLM-Wiki and OKF foundation sources](../../.scratch/smartdca/issues/15-ingest-llm-wiki-okf-foundation-sources.md).[^ticket-15] It is **explanation, not specification**. Where it and the [OKF v0.2 specification](okf-v0-2-specification.md) differ, the specification governs; this concept records the article's rationale and its wording separately for exactly that reason.

## Snapshot identity

The article is *Open Knowledge format v0.2 tackles agentic trust* by Sam McVeety and Amir Hormati on the Google Cloud blog, published 2026-07-25 and carrying no version identifier. Google Cloud blog content is not licensed for redistribution, so no local artifact is stored. The origin is dynamically rendered: two fetches minutes apart produced different bytes and therefore different SHA-256 values while the article text was identical. The recorded fingerprint identifies the exact response analysed here and is **not** reproducible by re-fetching; it cannot be used to detect that the article changed.

## What the source says

The article frames v0.2 around accountability. A human-authored wiki page carries an implicit guarantee that a person wrote it and can be held responsible; when an agent generates ten thousand concepts overnight that guarantee is gone, so a consumer — usually another agent — must judge each concept on explicit signals. It gives five questions: provenance, trust, freshness, lifecycle, and attestation.[^trust-article]

Its central design argument is why these signals belong in frontmatter rather than the body: most interactions with a concept never reach the body, because a consumer first has to decide whether the concept is relevant and trustworthy at all. Frontmatter's narrower job is to elevate exactly the signals needed to make that decision cheaply and often, without spending tokens on prose, so that trust becomes something you can filter on before committing to a read. The article characterizes v0.1's fields as *describing* a concept and v0.2's additions as letting you *decide* something about it before reading.[^trust-article]

On provenance it repeats the deliberate omission: OKF records objective signals (`author`, `usage_count`, `last_modified`), not a credibility score, because a score is subjective, does not port across consumers, and goes stale the moment it is written; credibility is inferred by the consumer. On trust it stresses that `generated` and `verified` are kept distinct because who wrote something need not be who confirmed it, and that the derived tiers let a consumer say "only surface human-reviewed metrics in the executive dashboard" as a frontmatter filter. On freshness it gives the reason for an absolute `stale_after` over a relative time-to-live: staleness becomes a plain date comparison with no reference to when the concept happened to be read, which is the determinism a non-LLM consumer wants.[^trust-article]

On attestation it draws the line this bundle relies on. Provenance answers where a claim came from; attestation answers whether a number was produced the way it was supposed to be, or whether the agent improvised its own query. The agent may fill only declared parameters and must never author or edit the computation; a run returns a receipt, and a deterministic no-LLM attester compares the canonicalized executed artifact against the sanctioned one, so a rewritten query, a swapped computation file, or a mutated dependency fails. OKF records the computation and how to check it and never executes anything itself. Verification and attestation are distinct: a stale definition can still attest cleanly, and a freshly verified definition still needs attestation on every run.[^trust-article]

On compatibility the article says v0.2 "is a minor version bump that is additive, backward-compatible, with two deliberate **renames**" — `timestamp` to `generated.at` and the body `# Citations` list to `sources` — and that "a v0.1 bundle drops in unchanged". It also emphasizes that v0.2 "adds vocabulary, not rules": `type` remains the only always-required field, every new field is opt-in, custom keys are preserved rather than rejected, and a bundle adopting none of the additions is exactly as valid as under v0.1 — though the absence of a signal now carries meaning, since an unverified concept is distinguishable from a verified one while never being rejected for it. The v0.2 release itself covers a reference agent that emits provenance and trust as it generates, a static visualizer that surfaces trust tier, status, and staleness, updated sample bundles, and a Knowledge Catalog round-trip demo; the reference implementations are described as deliberate proofs of concept that nothing about OKF requires.[^trust-article]

## Bearing on this bundle

The article supplies the reasoning behind three profile decisions rather than any new constraint. It is the clearest statement of why this bundle puts role, lifecycle, and trust in frontmatter and keeps the body for what must actually be read; why the profile records review events instead of a confidence score; and why `stale_after` is an absolute date reserved for genuinely time-sensitive knowledge instead of a calendar expiry on timeless mathematics. Its verification-versus-attestation distinction is the reason this bundle's Python checks remain linked evidence and are not labelled Attested Computation until a runtime and attestation protocol exists.

Its compatibility wording is where it diverges from the specification, which calls the same two changes breaking rather than renames. That conflict is recorded in [Conflicts across the OKF foundation sources](../../research/synthesis/okf-foundation-source-conflicts.md).

## Limits

The article is a product announcement with no normative force, no conformance criteria, and no complete field reference; its frontmatter excerpts are illustrative and abbreviated. It describes the trust model in terms of a fictional retail bundle whose concerns — dashboards, general-ledger reconciliation, executive filters — do not map onto mathematical research evidence. Because its fingerprint is not reproducible, it is the weakest of the five snapshots for provenance purposes and should be cited for rationale rather than for any exact requirement.

[^trust-article]: Open Knowledge format v0.2 tackles agentic trust (Google Cloud blog), published 2026-07-25, retrieved 2026-08-16
[^ticket-15]: [Ingest the LLM-Wiki and OKF foundation sources](../../.scratch/smartdca/issues/15-ingest-llm-wiki-okf-foundation-sources.md)
