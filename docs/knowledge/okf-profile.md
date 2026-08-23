---
profile: smartdca-okf/0.3
type: specification
title: "SmartDCA Open Knowledge Format profile"
description: "Normative smartdca-okf/0.3 profile specializing Open Knowledge Format v0.2 for this bundle."
knowledge_role: canonical
status: stable
sources:
  - id: okf-spec
    title: "Open Knowledge Format v0.2 specification"
    resource: https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/SPEC.md
    source_kind: external
    retrieved_at: 2026-08-16T08:10:00Z
    upstream_version: "0.2"
    sha256: 5a3311d270bebb16d558010e75064f5b75323f284992641732b1c8097511f948
    local_artifact: references/raw/okf-spec/0.2/SPEC.md.raw
  - id: ticket-12
    title: "Design a repository-root LLM-Wiki using OKF v0.2"
    resource: .scratch/smartdca/issues/12-design-repository-root-llm-wiki-okf
    source_kind: internal
  - id: ticket-13
    title: "Implement the SmartDCA OKF profile and report-only validator"
    resource: .scratch/smartdca/issues/13-implement-smartdca-okf-profile-validator
    source_kind: internal
  - id: adr-0002
    title: "Make the repository root an OKF knowledge bundle"
    resource: docs/adr/0002-repository-root-okf-knowledge-bundle
    source_kind: internal
  - id: adr-0003
    title: "Separate document kind, authority, lifecycle, and trust"
    resource: docs/adr/0003-separate-knowledge-authority-and-trust
    source_kind: internal
  - id: adr-0004
    title: "Preserve path-based concept identity through supersession"
    resource: docs/adr/0004-preserve-path-based-concept-identity
    source_kind: internal
  - id: adr-0005
    title: "Assign source-summary and synthesis paths in profile 0.2"
    resource: docs/adr/0005-assign-source-summary-and-synthesis-paths
    source_kind: internal
  - id: adr-0006
    title: "Assign definition, theorem, and experiment-report paths in profile 0.3"
    resource: docs/adr/0006-assign-definition-theorem-and-experiment-report-paths
    source_kind: internal
generated:
  by: claude-code/smartdca-wiki-0.1
  at: 2026-08-16T10:24:00Z
generation_run: urn:uuid:51b6a4df-c98b-4784-83e4-3b068e4014ab
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T07:46:00Z
    review_run: urn:uuid:b5b1666e-e77c-41a4-8781-fb0d5a965582
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T07:46:00Z
    review_run: urn:uuid:da31a04e-0105-4659-9d05-895a4364b107
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T07:55:00Z
    review_run: urn:uuid:e4ba41a1-1d8a-4cf6-b7a1-2c42a746b28f
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T08:26:00Z
    review_run: urn:uuid:84b7d96d-6547-4bbf-b78e-f4334f5f3c41
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T09:09:00Z
    review_run: urn:uuid:37f6c387-3dc8-4d4f-83ca-f782eb3453a5
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T09:26:00Z
    review_run: urn:uuid:0b6608b4-7e9f-4ba5-a07e-d6e8537908fd
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T10:06:00Z
    review_run: urn:uuid:6186d423-474a-44ee-8d3d-c36f938ad51a
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T10:32:00Z
    review_run: urn:uuid:6e8b3b72-0624-46b2-91ff-071b4879d9d4
  - by: human:github:razvan-tanase
    at: 2026-08-23T15:45:00Z
    review_run: urn:uuid:f1558f7f-31a3-431b-9ff5-a0fc3c67ae13
---
# SmartDCA Open Knowledge Format profile

This document is the normative local profile for the repository-root SmartDCA knowledge bundle. It specializes [Open Knowledge Format (OKF) v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)[^okf-spec] as `smartdca-okf/0.3` and transcribes the accepted design in [Design a repository-root LLM-Wiki using OKF v0.2](../../.scratch/smartdca/issues/12-design-repository-root-llm-wiki-okf.md)[^ticket-12].

The words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, and MAY are normative. Base OKF and this profile are separate validation layers: a document can conform to OKF while failing this profile.

## Bundle and identity

The repository root is the bundle root, by the decision in [Make the repository root an OKF knowledge bundle](../adr/0002-repository-root-okf-knowledge-bundle.md)[^adr-0002]. The root `README.md` is repository-interface documentation for humans and GitHub and is deliberately outside the OKF concept corpus; it MUST NOT carry concept frontmatter. Every other UTF-8 file whose final suffix is `.md` is either a concept or a reserved file, including Markdown below hidden directories. `index.md` and `log.md` are reserved at every depth; all remaining Markdown files are concepts.

A Concept ID is the bundle-relative path without the `.md` suffix. A published Concept ID is stable. Moving a stable concept creates the new concept and retains the old path as a deprecated forwarding concept with `superseded_by`; it does not delete or silently redirect the old identity. That is the durable-identity decision in [Preserve path-based concept identity through supersession](../adr/0004-preserve-path-based-concept-identity.md)[^adr-0004].

External Markdown snapshots are not concepts. Their exact upstream bytes MUST use a non-`.md` final suffix, normally `.md.raw`, under a versioned path such as `references/raw/<source>/<version>/source.md.raw`. A separate conformant concept summarizes and cites the snapshot.

## Base OKF v0.2 conformance

The base layer implements OKF v0.2 conformance without importing stricter SmartDCA rules. It requires parseable top-of-file YAML frontmatter and a non-empty `type` for every Markdown concept file, plus the reserved-file structures defined by OKF. The root `README.md` is not passed to base concept validation.

The base layer MUST accept:

- a concept containing only a non-empty `type`;
- unknown `type` values and extension keys;
- broken cross-links;
- `verified` as one mapping or a list;
- missing optional metadata families; and
- absent `status`, which base OKF interprets as `stable`.

The SmartDCA layer may report any of those states when this profile makes the constraint stricter. Base and profile findings MUST never be collapsed into one verdict.

Malformed optional OKF families are surfaced as advisory base warnings rather than conformance failures. This includes invalid `status`, `generated`, `verified`, `sources`, `stale_after`, and an Attested Computation without `runtime`. Advisory warnings do not change base `ok`; they preserve OKF's rule that optional-family guidance is soft.

## Concept schema

Every concept MUST have these fields:

| Field | Rule |
|---|---|
| `profile` | Exactly `smartdca-okf/0.3`. |
| `type` | One registered type below. |
| `title` | Non-empty human-readable string. |
| `description` | Non-empty, one-line retrieval description. |
| `knowledge_role` | `canonical`, `evidence`, or `operational`. |
| `status` | Explicit `draft`, `stable`, or `deprecated`. |

Registered `type` values are:

- `project-overview`
- `specification`
- `domain-glossary`
- `definition`
- `theorem`
- `research-note`
- `source-summary`
- `synthesis`
- `experiment-report`
- `decision-record`
- `research-map`
- `research-ticket`
- `workflow`
- `agent-instructions`

Adding a type, changing an enum, or assigning a new Markdown path requires a profile version change.

`knowledge_role` expresses answer authority, independently of type, lifecycle, and trust:

- `canonical` is the preferred source for the knowledge it governs;
- `evidence` holds proofs, experiments, source analysis, or detailed reasoning; and
- `operational` holds project state or instructions and is not a preferred research answer.

`status` is only OKF lifecycle. `verified` is trust. Ticket and ADR state use their extensions below and MUST NOT be encoded by overloading `status`. Keeping these four axes independent is the decision in [Separate document kind, authority, lifecycle, and trust](../adr/0003-separate-knowledge-authority-and-trust.md)[^adr-0003].

## Provenance

`original_record` is an optional boolean whose default is false. It may be true only when the concept itself is the internally authored record and no prior material was transformed into it. Git history is then the record provenance. It never excuses uncited external claims.

Canonical and evidence concepts MUST carry a non-empty `sources` list unless `original_record: true`. Each source is a mapping with:

| Field | Rule |
|---|---|
| `id` | Required, non-empty, and unique within the concept. It is the Markdown footnote join key. |
| `title` | Required non-empty display label. |
| `resource` | Required non-empty OKF resource: URL, scope descriptor, or internal concept path. |
| `source_kind` | Exactly `internal`, `external`, or `scope`. |
| `author` | Optional. When present it MUST follow the actor convention below, so OKF's own `team:<id>` example spelling is reported here. |

An `internal` resource MUST resolve to a concept. A stable concept MUST NOT depend on a draft or deprecated concept. If an internal dependency's `generated.at` is later than the dependent concept's latest verification, the dependent is stale and MUST return to draft or be re-reviewed.

An `external` source is an immutable snapshot identity and additionally requires:

| Field | Rule |
|---|---|
| `retrieved_at` | ISO 8601 datetime. |
| `upstream_version` | Non-empty upstream identifier, or the literal `unversioned`. |
| `sha256` | Exactly 64 lowercase hexadecimal characters over the raw upstream bytes. |
| `local_artifact` | Optional safe bundle-relative path with a non-`.md` suffix. When present, it MUST exist and its bytes MUST match `sha256`. |

A revised external source creates a new versioned artifact and fingerprint. Existing artifacts are never overwritten. When redistribution is unsuitable, omit `local_artifact` but retain the origin, retrieval time, version, and fingerprint calculated from the fetched bytes.

Claim attribution uses Markdown footnotes whose labels equal `sources[].id`. Links and footnote labels inside a fenced code block or an inline code span are illustrative syntax and are neither references nor joins. Every body footnote label MUST resolve to a source. Every external source MUST be joined from at least one body footnote. Every source on a canonical high-risk concept MUST likewise be joined from the claim body, including internal sources. Footnote prose is explanatory; the source mapping is authoritative.

## Generation, verification, and freshness

When an agent meaningfully creates or changes content, `generated` MUST be a mapping with a valid actor in `by` and an ISO 8601 datetime in `at`. It MUST be accompanied by `generation_run: urn:uuid:<uuid>`. `generated` records the actor and time of the last meaningful change, not original authorship, and its absence means no agent change has been recorded under this profile rather than that the concept was written by a human.

Actors follow OKF:

- agent or tool: `<producer>/<version>`; the registered local producers are `openai-codex/smartdca-wiki-0.1` and `claude-code/smartdca-wiki-0.1`;
- human: `human:<id>`; the registered project owner is `human:github:razvan-tanase`;
- process: `process:<id>`; structural CI is `process:github-actions:smartdca-wiki-ci`.

Stable high-risk concepts MUST normalize `verified` to a list. Each event requires `by`, ISO 8601 `at`, and `review_run: urn:uuid:<uuid>`. A qualifying semantic verification:

- is not performed by `process:github-actions:smartdca-wiki-ci`;
- has `verified.at >= generated.at` when the current content is agent-generated; and
- uses a `review_run` distinct from `generation_run`.

High-risk concepts are canonical `domain-glossary`, `definition`, `theorem`, `synthesis`, and `decision-record` concepts, plus any concept that resolves a substantive conflict. A meaningful agent edit demotes a high-risk concept to draft until a fresh qualifying review. Older verification events may remain as history but do not qualify for the changed content.

`stale_after`, when present, MUST be an absolute `YYYY-MM-DD` date and is used only for genuinely time-sensitive knowledge. A stable concept is stale on and after that date. Timeless mathematics has no arbitrary calendar expiry; it becomes stale through dependency change.

## Lifecycle extensions

A `research-ticket` MUST retain the body fields `Type:` and `Status:` and mirror them in frontmatter:

- `ticket_type`: `research`, `prototype`, `grilling`, or `task`;
- `ticket_status`: `open`, `claimed`, or `resolved`.

Open and claimed tickets use OKF `status: draft`; resolved tickets use `status: stable`.

A `decision-record` requires `decision_status: proposed|accepted|deprecated|superseded`. Proposed decisions are draft. Accepted decisions may be draft while awaiting review and become stable only after qualifying review. Deprecated or superseded decisions use OKF `status: deprecated`.

`superseded_by`, when present, requires `status: deprecated` and names an existing repository-relative successor Concept ID without `.md`.

## Profile versioning

A profile version is the value every concept declares in `profile`; the schema rule requiring a version change is stated once, above.

`smartdca-okf/0.2` made exactly three changes, recorded in [Assign source-summary and synthesis paths in profile 0.2](../adr/0005-assign-source-summary-and-synthesis-paths.md)[^adr-0005]: it assigned `references/summaries/*.md` and `research/synthesis/*.md`, it stated the one-source rule for a summary, and it added this section. No other rule of 0.1 changed, so a 0.1 concept satisfies 0.2 as soon as its `profile` value is relabelled. Separately from the rule set, this document's own OKF citation stopped being declared scope and became the fingerprinted snapshot; that is provenance, not a rule change.

`smartdca-okf/0.3` makes exactly one change, recorded in [Assign definition, theorem, and experiment-report paths in profile 0.3](../adr/0006-assign-definition-theorem-and-experiment-report-paths.md)[^adr-0006]: it assigns `research/definitions/*.md`, `research/theorems/*.md`, and `reports/experiments/*.md`. No other rule of 0.2 changes, so a 0.2 concept satisfies 0.3 as soon as its `profile` value is relabelled. Every registered type now has a destination, so the path mapping below is complete rather than partial and no further path assignment is pending.

Relabelling across profile versions is a metadata migration: it does not update `generated.at`, demote a high-risk concept to draft, or invalidate a recorded verification. Only a concept whose body actually changed in the same transaction carries a new generation time.

## Path mapping

These assignments are exhaustive for active concept paths in profile 0.3. The registered `project-overview` type currently has no active concept instance because the root `README.md` is repository-interface documentation rather than knowledge corpus content. A non-reserved Markdown concept path not matched here fails the profile even if all of its metadata is otherwise valid.

| Path | Type | Role | Lifecycle rule |
|---|---|---|---|
| `README.md` | repository interface | not a concept | No YAML concept frontmatter; human/GitHub landing page only. |
| `CONTEXT.md` | `domain-glossary` | canonical | Draft until sources and bootstrap semantic review are recorded. |
| `docs/adr/*.md` | `decision-record` | canonical | Accepted records become stable only after independent review; otherwise draft or deprecated as mapped above. |
| `research/notes/*.md` | `research-note` | evidence | Stable only when the linked resolved ticket and review are documented; otherwise draft. |
| `research/definitions/*.md` | `definition` | canonical | Draft until a review independent of the run that wrote it promotes it. |
| `research/theorems/*.md` | `theorem` | canonical | Draft until a review independent of the run that wrote it promotes it. |
| `reports/experiments/*.md` | `experiment-report` | evidence | Stable only when the run's inputs, code version, seeds, and review are documented; otherwise draft. |
| `AGENTS.md` | `agent-instructions` | operational | Stable. |
| `docs/agents/domain.md` | `agent-instructions` | operational | Stable. |
| `docs/agents/triage-labels.md` | `domain-glossary` | operational | Stable. |
| `docs/agents/issue-tracker.md` | `workflow` | operational | Stable. |
| `docs/agents/wayfinder-ticket-workflow.md` | `workflow` | operational | Stable. |
| `docs/agents/llm-wiki-workflow.md` | `workflow` | operational | Draft until workflow review; stable after review. |
| `.scratch/smartdca/map.md` | `research-map` | operational | Stable authoritative frontier. |
| `.scratch/smartdca/issues/*.md` | `research-ticket` | operational | Resolved is stable; open or claimed is draft. |
| `docs/knowledge/okf-profile.md` | `specification` | canonical | Draft until independent review; stable after review. |
| `references/summaries/*.md` | `source-summary` | evidence | Stable only when the ingest's independent review is recorded; otherwise draft. |
| `research/synthesis/*.md` | `synthesis` | canonical | Draft until a review independent of the run that wrote the resolutions promotes it, and draft for as long as any recorded conflict is unresolved. |
| Root `index.md`, `log.md` | reserved | reserved | Reserved-file rules below; never concept frontmatter. |

A `source-summary` concept covers exactly one ingested source and MUST NOT digest several. One source MAY comprise more than one artifact of a single upstream edition — a specification plus a worked example from the same commit, say — in which case every artifact is fingerprinted as its own `external` entry under the one summary. It lives beside the immutable `references/raw/` snapshots it fingerprints, inside the `references/` tree that base OKF already reserves by convention for mirrored external material. It never restates a mathematical result as project knowledge; the extraction work does that.

A `definition` concept is the canonical home of one named construction: the object, its domain and parameter conditions, any limiting extension it needs to be total, and the identities it must preserve. A `theorem` concept is the canonical home of one proved statement: its hypotheses, the exact claim, whether the characterization is sharp, and what it does not establish. Neither carries the proof. The proof, the counterexamples, the numerical boundary work, and the literature positioning stay in the `research/notes/*.md` evidence they cite, which is why a definition or theorem concept is short and its note is long.

An `experiment-report` concept records one executed run: its estimand, data provenance, code version, seeds, and failure cases. It is evidence and never promotes a simulation to a proof.

## Stable links and supersession

Base OKF tolerates broken links. This profile reports a broken local Markdown link from a stable concept. Draft concepts may link to planned concepts. Deprecated forwarding concepts retain a body link to their successor and `superseded_by`.

Documents split only at a semantic boundary justified by independent identity and at least one of reuse, provenance, verification, lifecycle, or cross-query retrieval. A split adds concepts and retains the old page as evidence, an index, or a deprecated forwarder. Each normalized claim has one canonical home; local repetition in evidence or operational records is allowed when needed for intelligibility.

Conflicting claims remain evidence. A synthesis may preserve and describe the conflict but remains draft until an independent semantic review supports a stable resolution.

## Root index

The root `index.md` MUST contain exactly this frontmatter and no other key:

```yaml
---
okf_version: "0.2"
---
```

Its body declares the active profile as `` `smartdca-okf/0.3` `` and contains exactly one section for each role in this order:

```markdown
## Canonical
## Evidence
## Operational
```

Within each role, rows are grouped under a registered type heading such as `### theorem`; this makes the ordering role first and type second. Canonical type subgroups and their rows are ordered so every stable canonical concept precedes every draft or deprecated canonical concept. Empty role sections contain `_None._`. Every concept appears exactly once. Each inventory row uses this exact, parseable form:

```markdown
- [<title>](<bundle-relative .md path>) — <description> — type: <type>; status: <status>; trust: <indicator>; provenance: <indicator>
```

The link, title, description, type, status, and role MUST match the concept. Trust and provenance indicators are concise discovery hints, not substitute metadata.

## Root log

The root `log.md` has no frontmatter. It is immutable event history: existing events are never edited, reordered within a date group, or deleted. Date groups are newest first and use exactly `## YYYY-MM-DD`. Each group contains a flat bullet list. New events are inserted into the newest applicable group using:

```markdown
- YYYY-MM-DDTHH:MM:SSZ | <Operation> | <Title> | [concept](path.md), [change](https://example.test/change)
```

The timestamp is UTC and its date matches the group. The operation is a concise event type such as `Creation`, `Update`, `Verification`, `Deprecation`, or `Supersession`. The title is human-readable and the final field contains Markdown links.

When Git history is available, validation requires every previously committed event bullet to remain a verbatim subsequence of the current event bullets. This permits insertion of new events while reporting edits, deletions, and reordering of existing history.

## Validator contract

Install the pinned dependency and run the public command from the bundle root:

```bash
python -m pip install -r tools/okf/requirements.txt
python tools/okf/validate.py .
python tools/okf/validate.py . --format json
python tools/okf/validate.py . --strict
```

The validator has two modes. Report mode is the default: content findings always return process status 0, so nonconformance is inventory rather than a gate. Strict mode returns 1 when either layer reports a conformance finding and 0 otherwise; advisory base warnings never change the status because OKF keeps optional-family guidance soft. In both modes an invalid invocation or nonexistent bundle root returns 2, and human text and JSON identify `base_okf` and `smartdca_profile` separately.

[Implement the SmartDCA OKF profile and report-only validator](../../.scratch/smartdca/issues/13-implement-smartdca-okf-profile-validator.md)[^ticket-13] exposed report mode only. [Atomically migrate the repository to SmartDCA OKF 0.1](../../.scratch/smartdca/issues/14-atomically-migrate-repository-to-okf.md) added strict mode and, in the same merge transaction as the corpus migration, made `python tools/okf/validate.py . --strict` a blocking CI step alongside the validator fixtures. Every later change to a Markdown concept therefore has to conform before it can merge.

The validator scans the complete repository tree except `.git`, validates every final-suffix `.md` file except the root repository-interface `README.md`, and intentionally does not treat `.md.raw` artifacts as concepts. Automated fixtures exercise the base permissiveness contract, the complete path mapping, registered types, conditional fields, actor and run identities, source kinds and fingerprints, footnote joins, re-verification, supersession, ticket and ADR states, dependency freshness, stable links, reserved files, index coverage/order, raw snapshots, and all five accepted edge cases.

## Structural freeze

Structural freeze is a certification that nothing further is owed to this schema at the time it is made: no field, enum, registered type, path assignment, role, index or log grammar, validator rule, or retrieval mechanism is known to be required. It certifies the container, not the contents.

Freeze MUST NOT be read as a commitment to never change this profile. A later revision is always permitted through the ordinary mechanism above — bump the version, record the decision, relabel. Freeze creates no barrier to that and imposes no penalty for it.

A schema change made after a freeze has exactly two consequences, and no others. The freeze claim lapses on the date of that change and MUST be re-certified before anything that depends on it proceeds. The supervised-ingest streak restarts from zero. Concepts already published stay valid; a lapsed freeze never invalidates content, retracts a verification, or demotes a concept.

## Deferred capabilities

Hybrid search is deferred until measured retrieval failures, about 100 sources, or several hundred concepts. Batch ingestion is deferred until structural freeze and the supervised-ingest gate. Full OKF Attested Computation is deferred until the runtime, inputs, receipt, verdict, and attester protocol is specified. Existing Python checks remain linked evidence rather than attested computations.

## Sources

[^okf-spec]: [Open Knowledge Format v0.2 specification](../../references/summaries/okf-v0-2-specification.md), ingested snapshot at [`references/raw/okf-spec/0.2/SPEC.md.raw`](../../references/raw/okf-spec/0.2/SPEC.md.raw)
[^ticket-12]: [Design a repository-root LLM-Wiki using OKF v0.2](../../.scratch/smartdca/issues/12-design-repository-root-llm-wiki-okf.md)
[^ticket-13]: [Implement the SmartDCA OKF profile and report-only validator](../../.scratch/smartdca/issues/13-implement-smartdca-okf-profile-validator.md)
[^adr-0002]: [Make the repository root an OKF knowledge bundle](../adr/0002-repository-root-okf-knowledge-bundle.md)
[^adr-0003]: [Separate document kind, authority, lifecycle, and trust](../adr/0003-separate-knowledge-authority-and-trust.md)
[^adr-0004]: [Preserve path-based concept identity through supersession](../adr/0004-preserve-path-based-concept-identity.md)
[^adr-0005]: [Assign source-summary and synthesis paths in profile 0.2](../adr/0005-assign-source-summary-and-synthesis-paths.md)
[^adr-0006]: [Assign definition, theorem, and experiment-report paths in profile 0.3](../adr/0006-assign-definition-theorem-and-experiment-report-paths.md)
