---
profile: smartdca-okf/0.5
type: workflow
title: "SmartDCA LLM-Wiki workflow"
description: "How agents author, ingest, promote, review, and supersede knowledge in the wiki."
knowledge_role: operational
status: draft
original_record: true
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-30T09:39:25Z
generation_run: urn:uuid:c151b2eb-777f-4ae7-9f49-877a6401860e
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
  - by: openai-codex/smartdca-wiki-0.1
    at: 2026-08-23T16:21:37Z
    review_run: urn:uuid:66222a92-a082-4617-b191-77c124239e73
---
# SmartDCA LLM-Wiki workflow

Use this workflow when a concept, path, metadata field, provenance join, lifecycle state, index row, or log event changes. The normative [SmartDCA OKF profile](../knowledge/okf-profile.md) defines representation; the [Wayfinder ticket workflow](wayfinder-ticket-workflow.md) governs work state.

## Invariants

- The repository root is the OKF bundle root.
- Root `.agents/` and `.git/` are non-bundle repository infrastructure. Every non-reserved Markdown bundle member is a concept and needs a registered path assignment, including members below other hidden directories.
- `index.md` is the complete discovery inventory; `.scratch/smartdca/map.md` is the active research frontier; `README.md` is the human introduction.
- Type, authority role, lifecycle, trust, and workflow state are distinct fields.
- One normalized claim has one canonical home. Evidence and operational records preserve history and link to it.
- Published Concept IDs are stable. Supersession preserves the old path.
- External snapshots are immutable, fingerprinted bytes under a non-`.md` suffix.
- A high-risk concept becomes stable only after a qualifying semantic review run distinct from generation. Structural CI supplies conformance evidence.

## 1. Orient

1. Follow the Wayfinder workflow until exactly one eligible ticket is claimed.
2. Read the index row, canonical home, linked evidence, and internal dependencies for every claim the ticket may change.
3. Read the profile sections governing the target path, type, lifecycle, provenance, and trust.
4. Keep knowledge-system validation under `tools/okf/` separate from scientific checks under `reproducibility/checks/`.

**Complete when:** the ticket, canonical home, evidence, dependencies, target path, and applicable profile rules are all identified.

## 2. Author or revise a concept

1. Identify the claim's canonical home and existing evidence before writing.
2. Confirm the target path is assigned by the active profile. If not, make a versioned profile/path decision first.
3. Keep one concept unless a semantic boundary has independent identity and at least one of reuse, provenance, review, lifecycle, or retrieval value.
4. Add the required universal metadata and the path-specific type, role, and lifecycle state.
5. Record provenance: use `original_record: true` for an internally authored record; for derived content, record complete sources and join each derived claim to its source ID with a footnote.
6. For a meaningful agent change, update `generated.at` and `generation_run`; set changed high-risk content to draft until review.
7. Update the root index row and append a root log event in the same change.
8. Run report validation and inspect both layers.

**Complete when:** the claim has one canonical home, metadata and provenance satisfy the profile, the index and log agree with the concept, and report validation has no unexplained finding.

## 3. Ingest one external source

Ingest under supervision, one source per ticket step:

1. Fetch the authoritative resource and retain the exact response bytes used for analysis.
2. Determine an upstream version; record `unversioned` when no stable identifier exists.
3. Calculate SHA-256 over the unmodified bytes.
4. When redistribution permits, save those bytes at a new versioned non-`.md` path such as `references/raw/<source>/<version>/source.md.raw`; preserve every earlier edition at its existing path.
5. Create a conformant summary concept with `source_kind: external`, origin URL, retrieval time, upstream version, fingerprint, and optional local artifact path.
6. Attribute externally derived claims with footnotes joined to source IDs.
7. Run structural validation plus provenance, orphan, canonical-home, and contradiction review.
8. Append the index row and log event.

Create a synthesis only when cross-source integration or conflict resolution is reusable. A contradiction remains preserved in evidence; an unresolved synthesis remains draft.

**Complete when:** the source has one fingerprinted summary, every retained byte artifact is immutable and versioned, every derived claim is joined to a source ID, and structural plus semantic ingest reviews pass.

## 4. Promote a query result

Ordinary answers are ephemeral. Promote a query result only when it reveals reusable knowledge not already captured.

1. Search the index and canonical concepts first, then follow internal sources into evidence.
2. Prefer stable canonical concepts and surface lifecycle, trust, freshness, and unresolved conflict.
3. When the result restates existing knowledge, keep the answer ephemeral and record the non-promotion decision if the ticket requires it.
4. When reusable knowledge is missing, create or update its canonical home, attach provenance, apply the required draft state, and run the authoring procedure.

**Complete when:** reusable new knowledge has a canonical home, while a restatement leaves no duplicate concept.

## 5. Review and promote

Treat mechanical validation as conformance evidence and semantic review as claim approval.

1. Review the current content against its sources and internal dependencies.
2. Use a `review_run` distinct from the generation run. The GitHub Actions process actor cannot qualify.
3. Ensure the qualifying verification time is not earlier than the last meaningful generated change.
4. Resolve or explicitly preserve substantive contradictions.
5. Promote to stable only when the profile's risk and path-specific rules pass.
6. Update trust indicators in the index and append a `Verification` log event.

When a dependency changes after verification, demote the dependent or perform a new review. Re-verification may add an event without changing `generated.at` when the content itself did not change.

**Complete when:** the review covers current content and dependencies, every substantive conflict is resolved or preserved, the profile permits the lifecycle state, and index trust plus log history match the verification.

## 6. Deprecate, supersede, or move

Preserve a stable concept's published identity when a successor replaces it.

1. Create the successor at an assigned path.
2. Change the old concept to `status: deprecated`.
3. Add `superseded_by` with the successor Concept ID without `.md`.
4. Retain a short forwarding body link and the historical provenance.
5. Update both index rows and append a `Supersession` event.

**Complete when:** both Concept IDs resolve, the predecessor forwards to the successor with its history intact, and the index and log describe the transition.

## 7. Publish gate

Run:

```bash
python -m unittest tools.okf.tests.test_validate_cli
python tools/okf/validate.py .
python tools/okf/validate.py . --strict
```

Structural checks run on every knowledge change. Provenance, orphan, canonical-home, and contradiction checks run after every ingest or promotion. A full semantic audit runs at ticket resolution and release.

Use report mode while iterating. Strict validation is the merge gate; a new Markdown concept first needs a profile-assigned path, type, and role.

**Complete when:** unit tests pass, report findings are understood, strict validation exits zero, the semantic review required by the risk tier is recorded, and the ticket, map, index, log, and changed concepts agree.

## Scale gates

Keep ingestion supervised until structural freeze and three consecutive supervised ingests complete without schema changes, conformance failures, or high-severity semantic corrections. Record the streak in its ingestion ticket; evaluate the gate in the structural-freeze ticket. Keep the first batch draft until batch-level review.

Treat structural freeze as a revocable certification. When work needs a schema change, bump the profile version, record the decision, mark the freeze lapsed, restart the ingest streak, and re-certify before resuming gated work.

Introduce hybrid search after measured retrieval failures or scale near 100 sources or several hundred concepts. Reserve `Attested Computation` for evidence with a specified runtime, inputs, receipt, verdict, and attester protocol; current Python checks remain linked executable evidence.
