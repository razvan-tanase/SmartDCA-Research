---
profile: smartdca-okf/0.3
type: workflow
title: "SmartDCA LLM-Wiki workflow"
description: "How agents author, ingest, promote, review, and supersede knowledge in the wiki."
knowledge_role: operational
status: stable
original_record: true
generated:
  by: claude-code/smartdca-wiki-0.1
  at: 2026-08-16T10:04:00Z
generation_run: urn:uuid:efe6420b-e236-40b6-96d4-c92a95d505d2
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T07:46:00Z
    review_run: urn:uuid:b5b1666e-e77c-41a4-8781-fb0d5a965582
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T07:46:00Z
    review_run: urn:uuid:da31a04e-0105-4659-9d05-895a4364b107
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T10:06:00Z
    review_run: urn:uuid:6186d423-474a-44ee-8d3d-c36f938ad51a
---
# SmartDCA LLM-Wiki workflow

This workflow maintains the repository-root LLM-Wiki defined by the normative [SmartDCA OKF profile](../knowledge/okf-profile.md). It complements, and does not replace, the [Wayfinder ticket workflow](wayfinder-ticket-workflow.md): Wayfinder governs work state; the profile governs knowledge representation.

## Invariants

- The repository root is the OKF bundle root.
- Every non-reserved Markdown file is a concept and needs a registered path assignment.
- `index.md` is the complete discovery inventory; `.scratch/smartdca/map.md` is the active research frontier; `README.md` is the human introduction.
- Type, authority role, lifecycle, trust, and workflow state are distinct fields.
- One normalized claim has one canonical home. Evidence and operational records preserve history and link to it.
- Published Concept IDs are stable. Supersession preserves the old path.
- External snapshots are immutable, fingerprinted bytes under a non-`.md` suffix.
- A high-risk concept cannot become stable through its generating run or structural CI.

## Orient and select work

1. Read `.scratch/smartdca/map.md`, the claimed ticket, `CONTEXT.md`, and the relevant ADRs.
2. Read the profile before creating, moving, deprecating, or changing lifecycle metadata on a concept.
3. Claim exactly one ticket and preserve its existing body contract.
4. Keep knowledge-system tooling separate from scientific checks under `reproducibility/checks/`.

## Author or revise a concept

1. Identify the claim's canonical home and existing evidence before writing.
2. Confirm the target path is assigned by the active profile. If not, make a versioned profile/path decision first.
3. Split only on a semantic boundary with independent identity plus reuse, provenance, review, lifecycle, or retrieval value. Do not split by token count alone.
4. Add the required universal metadata and the path-specific type, role, and lifecycle state.
5. Record provenance. Use `original_record: true` only for an internally authored record; otherwise add complete sources and claim-level footnote joins.
6. For an agent's meaningful change, update `generated.at` and `generation_run`. Demote changed high-risk content to draft.
7. Update the root index row and append a root log event in the same change.
8. Run report validation and inspect both layers.

The atomic migration preserved every existing body. It changed a body only where the profile itself required attribution the body did not yet carry — the canonical glossary gained footnote joins to its recorded sources — or where a concept stated project state that the migration itself changed. No content was split, synthesized, deduplicated, or rewritten. Later semantic edits follow normal review rules.

## Ingest one external source

Ingestion starts supervised, one source per ticket step:

1. Fetch the authoritative resource and retain the exact response bytes used for analysis.
2. Determine an upstream version; record `unversioned` when no stable identifier exists.
3. Calculate SHA-256 over the unmodified bytes.
4. When redistribution permits, save those bytes at a new versioned non-`.md` path such as `references/raw/<source>/<version>/source.md.raw`. Never overwrite an earlier edition.
5. Create a conformant summary concept with `source_kind: external`, origin URL, retrieval time, upstream version, fingerprint, and optional local artifact path.
6. Attribute externally derived claims with footnotes joined to source IDs.
7. Run structural validation plus provenance, orphan, canonical-home, and contradiction review.
8. Append the index row and log event.

Create a synthesis only when cross-source integration or conflict resolution is reusable. A contradiction remains preserved in evidence; an unresolved synthesis remains draft.

## Promote query results

Ordinary answers are ephemeral. Promote a query result only when it reveals reusable knowledge not already captured.

1. Search the index and canonical concepts first, then follow internal sources into evidence.
2. Prefer stable canonical concepts. Surface lifecycle, trust, freshness, and unresolved conflict rather than hiding them.
3. If the result merely restates existing knowledge, do not create a concept; record that promotion was correctly skipped when a ticket requires the decision.
4. If reusable knowledge is missing, create or update the canonical home, attach provenance, keep it draft as required, and run the authoring workflow.

## Review and promote

Mechanical validation is necessary but never a semantic review.

1. Review the current content against its sources and internal dependencies.
2. Use a `review_run` distinct from the generation run. The GitHub Actions process actor cannot qualify.
3. Ensure the qualifying verification time is not earlier than the last meaningful generated change.
4. Resolve or explicitly preserve substantive contradictions.
5. Promote to stable only when the profile's risk and path-specific rules pass.
6. Update trust indicators in the index and append a `Verification` log event.

When a dependency changes after verification, demote the dependent or perform a new review. Re-verification may add an event without changing `generated.at` when the content itself did not change.

## Deprecate, supersede, or move

Never delete a stable concept merely because a better version exists.

1. Create the successor at an assigned path.
2. Change the old concept to `status: deprecated`.
3. Add `superseded_by` with the successor Concept ID without `.md`.
4. Retain a short forwarding body link and the historical provenance.
5. Update both index rows and append a `Supersession` event.

## Validation cadence

Run:

```bash
python -m unittest tools.okf.tests.test_validate_cli
python tools/okf/validate.py .
python tools/okf/validate.py . --strict
```

Structural checks run on every knowledge change. Provenance, orphan, canonical-home, and contradiction checks run after every ingest or promotion. A full semantic audit runs at ticket resolution and release.

[Atomically migrate the repository to SmartDCA OKF 0.1](../../.scratch/smartdca/issues/14-atomically-migrate-repository-to-okf.md) migrated every concept, created the complete index and log, performed the required bootstrap reviews, and activated strict validation in the same merge transaction. Blocking validation is now the default: use report mode while iterating, but a change that leaves any concept nonconformant cannot merge. Adding a Markdown file at an unassigned path fails CI until the profile assigns its path, type, and role.

## Scale gates

Keep ingestion supervised until structural freeze and three consecutive supervised ingests complete without schema changes, conformance failures, or high-severity semantic corrections. The ingestion ticket records the three-ingest evidence; the structural-freeze ticket evaluates the full gate. The first batch remains draft pending batch-level review.

Structural freeze is revocable by design, on the terms the profile states. If later work needs a schema change, make it: bump the profile version and record the decision as usual. Do not treat a standing freeze as a reason to avoid a change the work genuinely needs, and do not work around the schema to protect the claim. Instead record that the freeze lapsed, restart the ingest streak, and re-certify before resuming anything the freeze gated.

Do not add hybrid search before measured retrieval failures or scale near 100 sources or several hundred concepts. Do not label current Python evidence as OKF Attested Computation until a runtime and attestation protocol is specified.
