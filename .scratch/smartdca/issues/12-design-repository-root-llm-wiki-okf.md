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

## Answer

Pending.
