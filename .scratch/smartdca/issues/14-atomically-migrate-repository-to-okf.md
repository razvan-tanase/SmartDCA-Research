---
profile: smartdca-okf/0.5
type: research-ticket
title: "Atomically migrate the repository to SmartDCA OKF 0.1"
description: "Task ticket atomically migrating every concept to smartdca-okf/0.1 and activating blocking CI."
knowledge_role: operational
status: stable
ticket_type: task
ticket_status: resolved
generated:
  by: claude-code/smartdca-wiki-0.1
  at: 2026-08-16T07:52:00Z
generation_run: urn:uuid:e52c437c-4218-43bd-a25e-5b1e3f1a0d24
---
# Atomically migrate the repository to SmartDCA OKF 0.1

Type: task
Status: resolved
Blocked by: 13
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

Using the reviewed profile and report from [Implement the SmartDCA OKF profile and report-only validator](13-implement-smartdca-okf-profile-validator.md), add conformant metadata to every non-reserved Markdown file while preserving each existing body and workflow header. Apply [Design a repository-root LLM-Wiki using OKF v0.2](12-design-repository-root-llm-wiki-okf.md)'s complete initial type, role, lifecycle, ticket-state, ADR-state, and profile mapping. Translate documented prior acceptance and review into verification only when evidence exists; otherwise keep high-risk canonical concepts draft and perform explicit bootstrap semantic review before promotion.

Add root `index.md` with only `okf_version: "0.2"` in frontmatter and `smartdca-okf/0.1` declared in its body. Populate a complete inventory grouped first by role and then topic/type, with every required entry indicator and stable canonical concepts first. Add root `log.md` with newest `## YYYY-MM-DD` groups and flat UTC event bullets whose prior entries are never edited or deleted. Switch report-only validation to blocking CI in the same merge transaction, verify all internal links, and rerun every scientific check. Do not split, synthesize, or deduplicate content.

## Comments

- Created during resolution of [Design a repository-root LLM-Wiki using OKF v0.2](12-design-repository-root-llm-wiki-okf.md).
- [Implement the SmartDCA OKF profile and report-only validator](13-implement-smartdca-okf-profile-validator.md) may expose the repository's existing nonconformance in report mode; this migration must combine complete metadata conversion with strict-CI activation atomically.
- Claimed on 2026-08-16, with no other ticket claimed. The report-mode baseline before migration was 39 base conformance findings and 71 profile findings.
- Prior review of the corpus is documented but its producing and reviewing runs predate run-identity recording, so no historical `review_run` exists to translate and inventing one would be fabricated provenance. Documented prior acceptance and review remain supporting evidence in tickets 01--13, and verification is recorded from reviews actually performed during this ticket.
- Bootstrap review observation, not actionable here: [the causal-novelty note](../../../research/notes/ticket-08-causal-dca-novelty-primary-sources.md) cites Burzoni et al. as "Definition 1 and Proposition 1" while [the pathwise positioning note](../../../research/notes/pathwise-dca-dominance-primary-sources.md) cites the same paper as "Definition 2.2 and Proposition 2.5". The two notes link the preprint and the journal version respectively, so this reads as preprint versus published numbering. Unifying the citation belongs to manuscript preparation, not to this migration, which must not rewrite bodies.
- External bibliographic claims in the evidence notes were reviewed for internal consistency, hedging, and citation hygiene rather than by re-fetching each publication; ingestion with raw fingerprints is [the next ticket](15-ingest-llm-wiki-okf-foundation-sources.md).
- Independent Standards and specification reviews ran after the first migration commit, in runs distinct from the run that produced it. They raised, and this ticket resolved, five actionable findings: producer self-review on the four concepts whose bodies this run edited; an actor-registry sentence that made `generated` read as original authorship; missing root-log `Update` events for those body changes; a `generated.at` on the glossary that predated its own footnote-join change; and a fenced-block scanner that let a shorter marker close a longer fence. Three judgement calls were also accepted: a `prose` free function that envied `Document`, a mysterious `fence` variable, and a duplicated test runner.
- Trust on the four concepts whose bodies this run edited (`README.md`, `CONTEXT.md`, the profile, and the wiki workflow) therefore comes from those independent review runs rather than from this run's bootstrap review, because [the glossary](../../../CONTEXT.md) forbids producer self-review. The bootstrap review by this run still carries the twelve concepts whose bodies it did not touch: the four ADRs and the eight evidence notes.
- Review-run identities: `urn:uuid:b5b1666e-e77c-41a4-8781-fb0d5a965582` is the independent Standards review, `urn:uuid:da31a04e-0105-4659-9d05-895a4364b107` the independent specification review, and `urn:uuid:16bd7b25-9e03-4aef-9c9a-5301cb317903` this run's bootstrap review. All three are distinct from the migration's `generation_run`.
- An independent re-review then confirmed all six resolutions and raised two more, both fixed: four concepts carried a `generated.at` earlier than the root-log event recording their own body change, and no event recorded this ticket's own rewrite. It also caught three stale counts in the text below, which now match the tree. Its `review_run` is `urn:uuid:e4ba41a1-1d8a-4cf6-b7a1-2c42a746b28f`, and it is the qualifying verification for the profile and the glossary because the profile's body changed in the fix round.
- Two reported findings were deliberately not actioned. A root-log bullet lists `index.md` among a verification event's links, which reads as if a reserved file were verified; the log is immutable, so the entry stays and this comment records the ambiguity. Log bullets also carry no `[change](...)` URL because the merge commit is not addressable until this branch merges; the profile requires only that the final field contain Markdown links.
- Amending the profile at version 0.1 is within its own rule: it requires a version change only for "[a]dding a type, changing an enum, or assigning a new Markdown path". Registering a producer, clarifying that fenced examples are not references, and documenting strict mode are none of those, and strict-mode activation is this ticket's mandate.

## Answer

Every one of the 39 non-reserved Markdown files is now a conformant `smartdca-okf/0.1` concept, and the two reserved root files exist. Base OKF v0.2 and the SmartDCA profile both report zero findings, and validation is blocking from this merge onward.

Metadata follows [the profile's](../../../docs/knowledge/okf-profile.md) complete initial path mapping with no exceptions: the project overview, glossary, four ADRs, and the profile are canonical; the eight research notes are evidence; the agent contract, four agent workflows, the map, and seventeen tickets are operational. Ticket extensions mirror each `Type:`/`Status:` body header, resolved tickets are stable and open or claimed tickets draft, and all four ADRs record `decision_status: accepted`, replacing the bare `status: accepted` header that three of them carried. Bodies were preserved: the only body changes are the glossary's footnote joins to its recorded sources, which the profile requires of a high-risk canonical concept, and factual state updates to the overview, map, workflow, and agent contract that this migration itself caused. Nothing was split, synthesized, or deduplicated.

Provenance is recorded rather than invented. Internally authored records use `original_record: true` with Git history as their provenance; the glossary, the profile, and the evidence notes carry explicit `sources` with internal Concept IDs and declared scope entries. `generated` and `generation_run` appear only on the concepts whose content this run actually changed.

Trust separates by who produced the body. The runs that produced the pre-existing bodies predate run-identity recording, so no historical `review_run` was available to translate; documented prior acceptance in tickets 01--13 is real evidence but carries no run identity, and inventing one would be fabricated provenance. Those twelve concepts — the four ADRs and the eight evidence notes — were therefore promoted on an explicit bootstrap semantic review by this run, which is independent of every run that wrote them: each proof, counterexample, accounting identity, and numerical example was re-derived, and the guardrail and homogeneity examples were independently confirmed by the scientific checks. For the four concepts whose bodies this run did edit, a bootstrap review by this run would be producer self-review, which the glossary forbids; their verification comes from the two independent review runs instead, each with its own `review_run`. Sixteen concepts are promoted in total, and no qualifying verification shares a run with the generation that produced its content.

Root [`index.md`](../../../index.md) carries only `okf_version: "0.2"`, declares the active profile in its body, and lists every concept exactly once in `Canonical`, `Evidence`, `Operational` order with `### <type>` subgroups and the required link, title, description, type, status, trust, and provenance fields. Root [`log.md`](../../../log.md) opens the immutable event history with a single newest-first date group of flat UTC bullets.

Four defects in the ticket-13 validator surfaced during migration and review, each fixed with a fixture. Links and footnote labels inside fenced code blocks were treated as real references, which made the profile's own row and log examples look like broken links; they are now ignored, and the profile states that rule. The first version of that scanner also let a shorter marker close a longer fence, so a nested example block could reopen prose, and it still read link syntax quoted in an inline code span as a reference; a fence now closes only on a marker of the same character that is at least as long, and code spans are stripped too. Strict mode did not exist: `--strict` now returns 1 when either layer reports a conformance finding, leaves advisory base warnings non-blocking, and still returns 2 for invalid invocation. A `knowledge` CI job installs the pinned dependency, runs the fixtures, and enforces strict validation with full Git history so the log-immutability and artifact-immutability checks work.

Verification after migration and review: 25 validator fixtures pass, strict validation exits 0 with both layers clean, all four scientific checks pass unchanged, and all 220 local Markdown links in the repository resolve. The [ticket-13 violation inventory](../../../reports/okf/current-violations.json) is deliberately left as that ticket's historical record of pre-migration state.

Scope deliberately left open: the five foundation sources are not ingested, so external material is cited as declared `scope` rather than as fingerprinted immutable snapshots, and no path is registered yet for future `definition`, `theorem`, `source-summary`, `synthesis`, or `experiment-report` concepts. Both belong to [the ingestion ticket](15-ingest-llm-wiki-okf-foundation-sources.md) and [the extraction ticket](16-extract-semantic-concepts-certify-freeze.md).
