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

## Answer

Pending.
