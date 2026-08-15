# Design a repository-root LLM-Wiki using OKF v0.2

Type: grilling
Status: resolved
Blocked by: 10
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

Design the repository itself as a human- and agent-navigable LLM-Wiki whose root is a conformant Open Knowledge Format v0.2 Knowledge Bundle. Specify the document authority model, concept taxonomy, metadata profile, stable-identity policy, navigation and agent contracts, semantic splitting and redundancy rules, provenance and trust workflow, validation gates, ingest/query/lint lifecycle, and staged migration of the existing corpus. Preserve the established separation between research state, detailed reasoning, and executable evidence, and do not resume ticket 11 until this architecture reaches its significance gate.

## Comments

- Claimed on 2026-08-15 after the user explicitly paused the research frontier for this architecture work.
- The user accepted the recommended choices across eleven design rounds covering scope, root-bundle topology, authority, trust, identity, schema, migration, ingestion, retrieval, maintenance, and delivery.
- Independent OKF and SmartDCA workflow reviews found actor-syntax, log-format, raw-Markdown, re-verification, schema-completeness, glossary-purity, ADR, and ticket-sequencing issues. The answer below incorporates their actionable findings.
- Implementation-ticket decomposition is specified below but later tickets are not created or modified while ticket 12 remains claimed.
- Independent OKF and SmartDCA standards/specification reviews completed on 2026-08-15. All actionable findings were corrected, and both final re-reviews returned PASS with no remaining finding.
- Tickets 13–17 are created only now, during resolution, and remain open with sequential blockers.

## Answer

The repository root will become both the SmartDCA LLM-Wiki and a conformant OKF v0.2 Knowledge Bundle governed by the versioned local profile `smartdca-okf/0.1`. Every non-reserved Markdown document is therefore a concept, including hidden Wayfinder state and agent instructions. The wiki is repository-native and optimized first for human and agent navigation; public rendering and external search remain later projections.

### Concept model

The registered `type` vocabulary is `project-overview`, `specification`, `domain-glossary`, `definition`, `theorem`, `research-note`, `source-summary`, `synthesis`, `experiment-report`, `decision-record`, `research-map`, `research-ticket`, `workflow`, and `agent-instructions`. Adding a type requires a profile version change.

`knowledge_role` independently states answer authority:

- `canonical`: preferred source for the knowledge it governs;
- `evidence`: supporting source, proof, experiment, or detailed reasoning;
- `operational`: project state or instructions, not a preferred research answer.

OKF `status` independently records lifecycle as `draft`, `stable`, or `deprecated`; `verified` records trust. Workflow and ADR state use extensions rather than overloading OKF fields.

### SmartDCA profile schema

| Field | Applies | SmartDCA rule |
|---|---|---|
| `profile` | Every concept | Exactly `smartdca-okf/0.1`. Root `index.md` declares the active profile in its body because its frontmatter may contain only `okf_version`. |
| `type` | Every concept | Non-empty registered value. The base-OKF validator separately recognizes that OKF itself permits unknown values. |
| `title` | Every concept | Non-empty human-readable string. |
| `description` | Every concept | Non-empty one-line retrieval description. |
| `knowledge_role` | Every concept | Exactly `canonical`, `evidence`, or `operational`. |
| `status` | Every concept | Explicitly `draft`, `stable`, or `deprecated`, even though bare OKF defaults absence to stable. |
| `original_record` | Internally authored record with no prior source | Boolean, default false. When true, Git history is the record's provenance and `sources` may be omitted; it never excuses uncited external claims. |
| `sources` | Canonical/evidence concepts unless `original_record: true` | List of mappings. Every entry requires `id`, `title`, OKF-required `resource`, and `source_kind: internal|external|scope`; footnote labels join to `id`. An external snapshot additionally requires ISO 8601 `retrieved_at`, non-empty `upstream_version` (or explicit `unversioned`), and `sha256` as 64 lowercase hexadecimal characters over the raw upstream bytes. `resource` is its authoritative origin URL; optional `local_artifact` is the bundle-relative non-`.md` raw-copy path when redistribution permits. |
| `generated` | Current content meaningfully created or changed by an agent | Mapping with required `by` and `at`; `at` is the last meaningful content change. |
| `generation_run` | Whenever `generated` is required | `urn:uuid:<uuid>` identifying the producing run. |
| `verified` | Stable high-risk concepts | SmartDCA-normalized list of events with required OKF `by` and `at`, plus `review_run: urn:uuid:<uuid>`. Base OKF still accepts either one mapping or a list. |
| `superseded_by` | Deprecated concept replaced by another | Repository-relative successor Concept ID without `.md`. |
| `ticket_type` / `ticket_status` | Research tickets | Mirror workflow `Type:` and `Status:` as registered extension enums without removing the body fields. |
| `decision_status` | Decision records | `proposed`, `accepted`, `deprecated`, or `superseded`; OKF lifecycle remains in `status`. |
| `stale_after` | Genuinely time-sensitive concepts only | Absolute OKF date. Timeless mathematics uses dependency freshness instead of calendar expiry. |

The conformant agent/tool actor is `openai-codex/smartdca-wiki-0.1`; model, workflow, and commit details are recorded as execution metadata. Human and process actors are `human:github:razvan-tanase` and `process:github-actions:smartdca-wiki-ci`. A qualifying semantic review requires a `review_run` distinct from `generation_run`; CI never counts as semantic review.

High-risk concepts are canonical `domain-glossary`, `definition`, `theorem`, `synthesis`, and `decision-record` documents, plus any concept that resolves a substantive conflict. They require mechanical validation and independent semantic review before becoming stable. A meaningful change updates `generated.at` when agent-authored and demotes a high-risk concept to draft; prior verification may remain historical but does not qualify unless `verified.at >= generated.at`, and a new distinct review run is required.

### Initial path mapping

| Path | Type | Role | Initial lifecycle rule |
|---|---|---|---|
| `README.md` | `project-overview` | canonical | Stable as an original record after migration review. |
| `CONTEXT.md` | `domain-glossary` | canonical | Draft until bootstrap semantic review and sources are recorded. |
| `docs/adr/*.md` | `decision-record` | canonical | Accepted records become stable only when acceptance and independent review are documented; otherwise draft. |
| `research/notes/*.md` | `research-note` | evidence | Stable when its linked resolved ticket and required review are documented; otherwise draft. |
| `AGENTS.md` | `agent-instructions` | operational | Stable. |
| `docs/agents/domain.md` | `agent-instructions` | operational | Stable. |
| `docs/agents/triage-labels.md` | `domain-glossary` | operational | Stable. |
| `docs/agents/issue-tracker.md` | `workflow` | operational | Stable. |
| `docs/agents/wayfinder-ticket-workflow.md` | `workflow` | operational | Stable. |
| `.scratch/smartdca/map.md` | `research-map` | operational | Stable as the authoritative current frontier. |
| `.scratch/smartdca/issues/*.md` | `research-ticket` | operational | Resolved tickets stable; open or claimed tickets draft. |
| `docs/knowledge/okf-profile.md` | `specification` | canonical | Stable only after independent review. |
| `docs/agents/llm-wiki-workflow.md` | `workflow` | operational | Stable after workflow review. |
| Root `index.md`, `log.md` | reserved | reserved | Follow OKF reserved-file rules, not concept frontmatter. |

Any future Markdown path not matched by the mapping fails the SmartDCA profile until its type and role are assigned. Migration may translate documented prior human acceptance and independent review into `verified`; it must not fabricate review. Any high-risk canonical concept without sufficient evidence starts draft and receives explicit bootstrap review before promotion.

### Identity, content, and provenance

Repository-relative paths without `.md` are stable Concept IDs. Documents split only at semantic boundaries justified by independent identity plus reuse, provenance, verification, lifecycle, or cross-query retrieval. A split adds new concepts and retains the old page as evidence, an index, or a deprecated forwarding concept. Stable concepts are never deleted merely because they are superseded.

Each normalized claim has one canonical home. Evidence and operational pages may preserve enough local repetition to remain intelligible but link to the canonical concept. Conflicting claims remain preserved as evidence and are reconciled only when useful in a separately reviewed `synthesis`; unresolved syntheses remain draft. Deprecated concepts retain their path, reason, and `superseded_by` Concept ID.

Imported external sources are immutable after ingestion. Exact upstream Markdown bytes are stored under a non-`.md` suffix such as `references/raw/<source>/<version>/source.md.raw` or in an archive, while a separate conformant source-summary concept links to them. Every external snapshot records its authoritative origin URL, retrieval time, upstream version or explicit `unversioned`, and the SHA-256 of the raw upstream bytes; when redistribution is inappropriate, `local_artifact` is omitted but the fetched bytes are still fingerprinted rather than stored. Canonical high-risk claims use Markdown footnotes joined to `sources[].id`; internal concepts remain governed, versioned, editable knowledge.

### Navigation, logs, and validation

`README.md` remains the human introduction, root `index.md` becomes the complete role-aware query inventory, and the Wayfinder map remains the active research frontier. The SmartDCA validator requires the index to cover every concept and group entries first by role, then topic/type, with link, title, description, type, status, concise trust/provenance indicators, and stable canonical concepts first.

Root `log.md` is immutable event history with newest date groups first. Headings are exactly `## YYYY-MM-DD`; each group contains a flat bullet list whose entries include a full UTC timestamp, operation type, title, and links. Existing events are never edited or deleted; new events are inserted into the newest applicable date group.

The validator reports base OKF v0.2 and SmartDCA-profile results separately. Base fixtures must prove acceptance of: a concept containing only non-empty `type`; unknown types and extension keys; broken links; `verified` as either a mapping or list; and absent `status` as stable. SmartDCA fixtures cover registered types, universal and conditional fields, role/status/risk rules, source resources and footnotes, full-index coverage/order, immutable raw Markdown, stable links, supersession, generation/review run separation, re-verification after meaningful changes, ticket/ADR extensions, freshness, and every required edge case.

Ingestion begins supervised and one source at a time. Query results are promoted only when reusable uncaptured knowledge exists; ordinary answers remain ephemeral. Lint is event-driven: structural checks on every change; provenance, orphan, canonical-home, and contradiction checks after each ingest or promotion; and full semantic audits at ticket resolution and release. Timeless mathematics has no arbitrary expiry; dependency changes trigger freshness review. Hybrid search is deferred until measured failures or scale near 100 sources or several hundred concepts.

Batch ingestion is enabled only after structural freeze and three consecutive supervised ingests without schema changes, conformance failures, or high-severity semantic corrections. The ingestion ticket records only the three-ingest evidence; the structural-freeze ticket evaluates the complete gate. The first batch remains draft pending batch-level review. Full OKF Attested Computation is deferred until its runtime, input, receipt, verdict, and attester protocol is specified; existing Python checks remain linked evidence assets.

### Migration and sequential implementation

Ticket 12 ends with this reviewed architecture and its significance gate. Only during resolution are the following open tickets created and wired sequentially:

1. Implement the normative profile, agent workflow, and report-only validator with all base/profile fixtures and a complete violation inventory.
2. In one merge transaction, preserve existing Markdown bodies while adding metadata, populate the complete index, add conformant event history, perform any required bootstrap semantic reviews, and switch CI to strict enforcement.
3. Ingest the five foundation sources individually: Karpathy LLM-Wiki; normative OKF v0.2 spec; v0.2 trust article; official examples/reference implementation; historical v0.1 announcement. Every source gets a summary; synthesis is created only for reusable cross-source integration or conflict resolution. Record the three-ingest prerequisite, not the complete batch gate.
4. Extract initial semantic concepts and certify structural freeze after a named supervised ingest plus query and lint cycle. Promote a query result only if reusable uncaptured knowledge is actually found; otherwise record that promotion was correctly skipped. Then evaluate the complete batch gate.
5. After structural freeze, clean redundancy and apply deprecation or supersession without altering mathematical conclusions merely to shorten text.

Ticket 11 remains open and is blocked by the fifth implementation ticket once those tickets are created.

### Required edge-case behavior

- A new untyped Markdown file is reported before migration and fails strict CI after activation.
- A contradicted source claim remains evidence; a draft synthesis states the conflict until independent review supports a stable resolution.
- A requested path move preserves the old stable Concept ID as a deprecated forwarding concept with `superseded_by`.
- A revised external source becomes a new raw fingerprinted artifact rather than overwriting the ingested edition.
- An agent-generated theorem records generation and claim-level provenance, remains draft through a distinct proof/source review run, becomes stable only when qualifying verification is recorded, and returns to draft after a later meaningful edit until re-reviewed.
