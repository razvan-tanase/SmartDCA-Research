# SmartDCA Open Knowledge Format profile

This document is the normative local profile for the repository-root SmartDCA knowledge bundle. It specializes [Open Knowledge Format (OKF) v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) as `smartdca-okf/0.1` and transcribes the accepted design in [Design a repository-root LLM-Wiki using OKF v0.2](../../.scratch/smartdca/issues/12-design-repository-root-llm-wiki-okf.md).

The words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, and MAY are normative. Base OKF and this profile are separate validation layers: a document can conform to OKF while failing this profile.

## Bundle and identity

The repository root is the bundle root. Every UTF-8 file whose final suffix is `.md` is either a concept or a reserved file, including Markdown below hidden directories. `index.md` and `log.md` are reserved at every depth; all other Markdown files are concepts.

A Concept ID is the bundle-relative path without the `.md` suffix. A published Concept ID is stable. Moving a stable concept creates the new concept and retains the old path as a deprecated forwarding concept with `superseded_by`; it does not delete or silently redirect the old identity.

External Markdown snapshots are not concepts. Their exact upstream bytes MUST use a non-`.md` final suffix, normally `.md.raw`, under a versioned path such as `references/raw/<source>/<version>/source.md.raw`. A separate conformant concept summarizes and cites the snapshot.

## Base OKF v0.2 conformance

The base layer implements OKF v0.2 conformance without importing stricter SmartDCA rules. It requires parseable top-of-file YAML frontmatter and a non-empty `type` for every non-reserved Markdown file, plus the reserved-file structures defined by OKF.

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
| `profile` | Exactly `smartdca-okf/0.1`. |
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

`status` is only OKF lifecycle. `verified` is trust. Ticket and ADR state use their extensions below and MUST NOT be encoded by overloading `status`.

## Provenance

`original_record` is an optional boolean whose default is false. It may be true only when the concept itself is the internally authored record and no prior material was transformed into it. Git history is then the record provenance. It never excuses uncited external claims.

Canonical and evidence concepts MUST carry a non-empty `sources` list unless `original_record: true`. Each source is a mapping with:

| Field | Rule |
|---|---|
| `id` | Required, non-empty, and unique within the concept. It is the Markdown footnote join key. |
| `title` | Required non-empty display label. |
| `resource` | Required non-empty OKF resource: URL, scope descriptor, or internal concept path. |
| `source_kind` | Exactly `internal`, `external`, or `scope`. |

An `internal` resource MUST resolve to a concept. A stable concept MUST NOT depend on a draft or deprecated concept. If an internal dependency's `generated.at` is later than the dependent concept's latest verification, the dependent is stale and MUST return to draft or be re-reviewed.

An `external` source is an immutable snapshot identity and additionally requires:

| Field | Rule |
|---|---|
| `retrieved_at` | ISO 8601 datetime. |
| `upstream_version` | Non-empty upstream identifier, or the literal `unversioned`. |
| `sha256` | Exactly 64 lowercase hexadecimal characters over the raw upstream bytes. |
| `local_artifact` | Optional safe bundle-relative path with a non-`.md` suffix. When present, it MUST exist and its bytes MUST match `sha256`. |

A revised external source creates a new versioned artifact and fingerprint. Existing artifacts are never overwritten. When redistribution is unsuitable, omit `local_artifact` but retain the origin, retrieval time, version, and fingerprint calculated from the fetched bytes.

Claim attribution uses Markdown footnotes whose labels equal `sources[].id`. Every body footnote label MUST resolve to a source. Every external source MUST be joined from at least one body footnote. Every source on a canonical high-risk concept MUST likewise be joined from the claim body, including internal sources. Footnote prose is explanatory; the source mapping is authoritative.

## Generation, verification, and freshness

When an agent meaningfully creates or changes content, `generated` MUST be a mapping with a valid actor in `by` and an ISO 8601 datetime in `at`. It MUST be accompanied by `generation_run: urn:uuid:<uuid>`.

Actors follow OKF:

- agent or tool: `<producer>/<version>`; the registered local producer is `openai-codex/smartdca-wiki-0.1`;
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

## Initial path mapping

These assignments are exhaustive for profile 0.1. A non-reserved Markdown path not matched here fails the profile even if all of its metadata is otherwise valid.

| Path | Type | Role | Lifecycle rule |
|---|---|---|---|
| `README.md` | `project-overview` | canonical | Stable original record after migration review. |
| `CONTEXT.md` | `domain-glossary` | canonical | Draft until sources and bootstrap semantic review are recorded. |
| `docs/adr/*.md` | `decision-record` | canonical | Accepted records become stable only after independent review; otherwise draft or deprecated as mapped above. |
| `research/notes/*.md` | `research-note` | evidence | Stable only when the linked resolved ticket and review are documented; otherwise draft. |
| `AGENTS.md` | `agent-instructions` | operational | Stable. |
| `docs/agents/domain.md` | `agent-instructions` | operational | Stable. |
| `docs/agents/triage-labels.md` | `domain-glossary` | operational | Stable. |
| `docs/agents/issue-tracker.md` | `workflow` | operational | Stable. |
| `docs/agents/wayfinder-ticket-workflow.md` | `workflow` | operational | Stable. |
| `docs/agents/llm-wiki-workflow.md` | `workflow` | operational | Draft until workflow review; stable after review. |
| `.scratch/smartdca/map.md` | `research-map` | operational | Stable authoritative frontier. |
| `.scratch/smartdca/issues/*.md` | `research-ticket` | operational | Resolved is stable; open or claimed is draft. |
| `docs/knowledge/okf-profile.md` | `specification` | canonical | Draft until independent review; stable after review. |
| Root `index.md`, `log.md` | reserved | reserved | Reserved-file rules below; never concept frontmatter. |

No semantic destination for future `definition`, `theorem`, `source-summary`, `synthesis`, or `experiment-report` files is registered yet. The extraction work must make and version that path decision before adding those files.

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

Its body declares the active profile as `` `smartdca-okf/0.1` `` and contains exactly one section for each role in this order:

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
```

[Implement the SmartDCA OKF profile and report-only validator](../../.scratch/smartdca/issues/13-implement-smartdca-okf-profile-validator.md) exposes report mode only. Content findings always return process status 0; an invalid invocation or nonexistent bundle root returns 2. Human text and JSON both identify `base_okf` and `smartdca_profile` separately. Strict failure and CI activation belong exclusively to [Atomically migrate the repository to SmartDCA OKF 0.1](../../.scratch/smartdca/issues/14-atomically-migrate-repository-to-okf.md) after the atomic metadata migration.

The validator scans the complete repository tree except `.git`, validates every final-suffix `.md` file, and intentionally does not treat `.md.raw` artifacts as concepts. Automated fixtures exercise the base permissiveness contract, the complete initial path mapping, registered types, conditional fields, actor and run identities, source kinds and fingerprints, footnote joins, re-verification, supersession, ticket and ADR states, dependency freshness, stable links, reserved files, index coverage/order, raw snapshots, and all five accepted edge cases.

## Deferred capabilities

Hybrid search is deferred until measured retrieval failures, about 100 sources, or several hundred concepts. Batch ingestion is deferred until structural freeze and the supervised-ingest gate. Full OKF Attested Computation is deferred until the runtime, inputs, receipt, verdict, and attester protocol is specified. Existing Python checks remain linked evidence rather than attested computations.
