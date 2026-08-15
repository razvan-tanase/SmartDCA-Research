# Design a repository-root LLM-Wiki using OKF v0.2

Type: grilling
Status: claimed
Blocked by: 10
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

Design the repository itself as a human- and agent-navigable LLM-Wiki whose root is a conformant Open Knowledge Format v0.2 Knowledge Bundle. Specify the document authority model, concept taxonomy, metadata profile, stable-identity policy, navigation and agent contracts, semantic splitting and redundancy rules, provenance and trust workflow, validation gates, ingest/query/lint lifecycle, and staged migration of the existing corpus. Preserve the established separation between research state, detailed reasoning, and executable evidence, and do not resume ticket 11 until this architecture reaches its significance gate.

## Comments

- Claimed on 2026-08-15 after the user explicitly chose to pause the research frontier for this architecture work.
- Primary phase-one purpose: a repository-native knowledge system for human and agent navigation; public presentation and external distribution remain downstream projections.
- The repository root, not a subdirectory, will be the OKF v0.2 Knowledge Bundle. Consequently, every non-reserved Markdown file in the tree must conform.
- Document kind, knowledge authority, lifecycle, and trust are separate dimensions. The SmartDCA profile will use `knowledge_role: canonical|evidence|operational`.
- Existing paths become stable Concept IDs. Later splits add semantic pages while old compound documents remain as evidence, indexes, or deprecated forwarding pages.
- `README.md`, root `index.md`, and `.scratch/smartdca/map.md` will remain distinct entry points for people, knowledge retrieval, and active research state.
- `AGENTS.md` will hold the short repository-wide contract and link to detailed schema and workflow documents.
- Agents may publish stable pages after risk-tiered validation: all pages require mechanical validation; definitions, theorems, decisions, and cross-source syntheses additionally require independent semantic review.
- Full corpus conversion, page splitting, deduplication, and ticket resolution remain pending the rest of the design interview and independent review.
- The SmartDCA profile uses a small registered `type` vocabulary: `project-overview`, `domain-glossary`, `definition`, `theorem`, `research-note`, `source-summary`, `experiment-report`, `decision-record`, `research-map`, `research-ticket`, `workflow`, and `agent-instructions`.
- Every concept requires `type`, `title`, `description`, `knowledge_role`, and `status`; `generated`, `sources`, `verified`, and ticket extension fields are conditionally required according to authorship, authority, risk, and operational state.
- Migration is two-pass: first convert every Markdown file atomically without changing bodies, add the root index, and activate validation; only then split, synthesize, and clean redundancy.
- CI will fail on structural/profile violations and broken internal links from stable concepts, while draft-only quality gaps may remain warnings.
- Documents split only at semantic boundaries that warrant independent identity, reuse, provenance, verification, lifecycle, or cross-query retrieval; no word- or token-count threshold defines a concept.
- Imported external source artifacts are immutable after ingestion; changed upstream editions become new versioned artifacts. Internal tickets, research notes, and canonical concepts remain editable through their governed workflows and Git history.
- Canonical high-risk concepts use document-level OKF `sources` plus claim-level Markdown footnotes joined to source IDs; one-source summaries may use document-level attribution unless a claim needs separate qualification.
- Each normalized claim has one canonical home. Evidence and operational records retain only the local context needed to remain understandable and link to the canonical concept.
- Conflicting source claims remain preserved as evidence; a separately reviewed `synthesis` concept states the resolution, links both directions, and remains draft while the conflict is unresolved. `synthesis` is added to the registered type vocabulary.
- A replaced stable concept is retained at its Concept ID with `status: deprecated`, a `superseded_by` extension, a brief reason, and a link to its successor; stable concepts are not deleted.
- Redundancy cleanup begins only after metadata migration, green CI, complete role classification and indexing, and one successful end-to-end ingest-query-lint cycle establish a structural freeze; the research itself need not be finished.
- Initial ingestion is supervised and one source at a time. Batch ingestion is deferred until repeated successful cycles show that the schema and validators handle the corpus safely.
- Query outputs are promoted only when they add reusable knowledge not already captured and are normalized through type, role, provenance, index placement, and risk-tier validation; ordinary answers remain ephemeral.
- Root `index.md` is a complete inventory grouped first by knowledge role and then topic or type, with link, title, one-line description, type, status, and concise trust/provenance indicators; stable canonical concepts are presented first.
- Append-only root `log.md` records durable knowledge operations with UTC machine-parseable headings; ordinary read-only queries are not logged because Git already records file diffs and the log records intent.
- Lint is event-driven: every change gets structural/profile/link/index checks; every ingest or promoted query gets provenance, orphan, canonical-home, and contradiction checks; every ticket resolution and release gets a full semantic audit.
- Stable actors are `human:github:razvan-tanase`, `agent:openai:codex`, and `process:github-actions:smartdca-wiki-ci`; execution details live in extensions or the log. Semantic verification must come from a reviewer distinct from the producing agent, and CI does not count as semantic review.
- Retrieval starts with `index.md` and repository search. Hybrid search is a later recorded decision triggered by measured failures or scale near 100 sources or several hundred concepts.
- `stale_after` is reserved for genuinely time-sensitive concepts. Timeless mathematics has no calendar expiry; dependency changes, deprecation, or supersession trigger freshness review.
- Batch ingestion requires structural freeze plus three consecutive supervised ingests without schema changes, conformance failures, or high-severity semantic corrections; the first batch remains draft until batch-level review passes.
- Full OKF Attested Computation is deferred until runtime packaging, inputs, receipts, verdicts, and an attester are defined. Current Python checks remain versioned evidence assets linked from knowledge concepts.
- External sources are preserved locally when redistribution permits, with origin, retrieval date, upstream edition/version, and SHA-256. Otherwise the authoritative URL and provenance metadata are retained without an unauthorized local copy; a changed edition is a new artifact.
- Ticket 12 ends with the reviewed architecture and significance gate. Sequential tracer tickets then implement: profile/validator; atomic metadata migration plus index/log; supervised foundation-source ingestion; semantic concept extraction and structural-freeze audit; and post-freeze redundancy cleanup.
- Wiki tooling lives at `tools/okf/validate.py`; the normative local profile at `docs/knowledge/okf-profile.md`; and agent procedures at `docs/agents/llm-wiki-workflow.md`. A small pinned YAML dependency supports local and CI validation.
- Initial roles are canonical for `README.md`, `CONTEXT.md`, and accepted ADRs; evidence for `research/notes/*.md`; operational for `AGENTS.md`, `docs/agents/*.md`, the Wayfinder map, and tickets. Future definitions, theorems, and reviewed syntheses are canonical.
- Open or claimed tickets are OKF draft and resolved tickets stable; `ticket_status` remains separate. ADR acceptance uses `decision_status`, while OKF `status` remains `draft|stable|deprecated`.

- The validator lands first in report-only mode; the atomic metadata migration, root index/log, and strict CI activation land together so `main` is never intentionally broken.
- Agents may mark validated branch concepts stable and open a draft PR, while merge into `main` remains an explicit user checkpoint at the ticket significance gate.
- Every concept declares `profile: smartdca-okf/0.1`; root `index.md` declares `okf_version: "0.2"` in frontmatter and the active SmartDCA profile in its body.
- Ticket 12 is accepted only after the design, glossary, ADRs, edge cases, migration decomposition, map, independent architecture review, and draft-PR checkpoint agree.
- Foundation sources are ingested one at a time in this order: Karpathy LLM-Wiki; normative OKF v0.2 spec; OKF v0.2 trust article; official examples/reference implementation; historical v0.1 announcement.

## Answer

The repository root will become both the SmartDCA LLM-Wiki and a conformant OKF v0.2 Knowledge Bundle governed by the versioned local profile `smartdca-okf/0.1`. Every non-reserved Markdown document is therefore a concept, including hidden Wayfinder state and agent instructions. The wiki is repository-native and optimized first for human and agent navigation; public rendering and external search remain later projections.

### Knowledge model

- `type` identifies document kind from the registered vocabulary: `project-overview`, `domain-glossary`, `definition`, `theorem`, `research-note`, `source-summary`, `synthesis`, `experiment-report`, `decision-record`, `research-map`, `research-ticket`, `workflow`, or `agent-instructions`.
- `knowledge_role` independently identifies answer authority: `canonical`, `evidence`, or `operational`.
- OKF `status` records lifecycle: `draft`, `stable`, or `deprecated`; OKF `verified` records trust. Ticket and ADR state use `ticket_status` and `decision_status`, never overloaded OKF fields.
- Every concept requires `profile`, `type`, `title`, `description`, `knowledge_role`, and `status`. `generated`, `sources`, `verified`, and operational extension fields are conditionally required by authorship, role, risk, and document kind.
- Stable high-risk definitions, theorems, decisions, and syntheses require mechanical validation and independent semantic review by an actor distinct from the producer. Stable actors are `human:github:razvan-tanase`, `agent:openai:codex`, and `process:github-actions:smartdca-wiki-ci`; execution details remain separate.

### Identity, content, and provenance

Repository-relative paths without `.md` are stable Concept IDs. Documents split only at semantic boundaries justified by independent identity plus reuse, provenance, verification, lifecycle, or cross-query retrieval. A split adds new concepts and retains the old page as evidence, an index, or a deprecated forwarding concept. Stable concepts are never deleted merely because they are superseded.

Each normalized claim has one canonical home. Evidence and operational pages may preserve enough local repetition to remain intelligible but link to the canonical concept. Conflicting claims remain preserved as evidence and are reconciled in a separately reviewed `synthesis`; unresolved syntheses remain draft. Deprecated concepts retain their path, reason, and `superseded_by` link.

Imported external sources are immutable after ingestion. When redistribution permits, the repository preserves a local version identified by origin, retrieval date, upstream edition/version, and SHA-256; otherwise it preserves authoritative URL-based provenance without an unauthorized copy. Canonical high-risk concepts use document-level OKF `sources` and claim-level Markdown footnotes joined to source IDs. Internal tickets, notes, and concepts remain governed, versioned, editable knowledge.

### Navigation and operation

`README.md` remains the human introduction, root `index.md` becomes the complete role-aware query inventory, and the Wayfinder map remains the active research frontier. `AGENTS.md` contains the short invariant contract and links to the normative profile and detailed LLM-Wiki workflow. Root `log.md` appends machine-parseable UTC records for durable knowledge operations, not ordinary read-only queries.

Ingestion begins supervised and one source at a time. Query results are promoted only when reusable and normalized through type, role, provenance, indexing, and risk-tier validation. Lint is event-driven: structural checks on every change; provenance, orphan, canonical-home, and contradiction checks after each ingest or promotion; and full semantic audits at ticket resolution and release. Timeless mathematics has no arbitrary expiry; dependency changes trigger freshness review. Hybrid search is deferred until measured retrieval failures or scale near 100 sources or several hundred concepts.

Batch ingestion is enabled only after structural freeze and three consecutive supervised ingests without schema changes, conformance failures, or high-severity semantic corrections; its first output remains draft pending batch review. Full OKF Attested Computation is deferred until its execution and attestation protocol is specified; existing Python checks remain linked evidence assets.

### Migration and implementation sequence

1. Implement `docs/knowledge/okf-profile.md`, `docs/agents/llm-wiki-workflow.md`, and report-only `tools/okf/validate.py` with pinned YAML support and tests.
2. In one merge transaction, add metadata to every existing Markdown body without semantic edits, add root `index.md` and `log.md`, and switch CI to strict enforcement.
3. Ingest the five foundation sources individually in the agreed order.
4. Extract initial semantic concepts and certify structural freeze after a complete ingest-query-lint cycle.
5. Only then clean redundancy and apply deprecation or supersession.

Initial roles are canonical for `README.md`, `CONTEXT.md`, and accepted ADRs; evidence for `research/notes/*.md`; and operational for `AGENTS.md`, `docs/agents/*.md`, the map, and tickets. Future definitions, theorems, and reviewed syntheses are canonical. Open or claimed tickets are OKF draft; resolved tickets are stable.

### Required edge-case behavior

- A new untyped Markdown file is reported before migration and fails strict CI after activation.
- A contradicted source claim remains evidence; a draft synthesis states the conflict until independent review supports a stable resolution.
- A requested path move preserves the old stable Concept ID as a deprecated forwarding concept with `superseded_by`.
- A revised external source becomes a new fingerprinted artifact rather than overwriting the ingested edition.
- An agent-generated theorem records generation and claim-level provenance, remains draft through independent proof/source review, and becomes stable only when verification is recorded.

Implementation proceeds through tickets 13–17. Ticket 11 remains open but blocked until the wiki sequence reaches its cleanup checkpoint.
