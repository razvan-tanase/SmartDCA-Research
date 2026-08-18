---
profile: smartdca-okf/0.3
type: research-ticket
title: "Extract initial semantic concepts and certify structural freeze"
description: "Resolved task ticket extracting initial semantic concepts and certifying structural freeze."
knowledge_role: operational
status: stable
ticket_type: task
ticket_status: resolved
---
# Extract initial semantic concepts and certify structural freeze

Type: task
Status: resolved
Blocked by: 15
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

Apply the semantic-boundary rule from [Design a repository-root LLM-Wiki using OKF v0.2](12-design-repository-root-llm-wiki-okf.md) to the current corpus. Create independently useful definition, theorem, and source-summary concepts, plus synthesis concepts only when reusable cross-source integration or conflict resolution warrants them without moving or deleting stable source paths; assign one canonical home per normalized claim; add claim-level provenance and reciprocal links; and preserve tickets, notes, and the map in their accepted roles.

Run a supervised ingest of the existing *SmartDCA superiority* source paper at `references/2308.05200v1.pdf` (Calvet, Herranz-Celotti, and Valimamode, arXiv:2308.05200v1) as the named freeze-audit cycle, then execute a representative query and full lint. Promote the query result only if it contains reusable uncaptured knowledge; otherwise record that correct non-promotion was exercised. Independently review every high-risk canonical concept and certify structural freeze only if profile, index, workflow, roles, validation, and retrieval require no schema change. After certification, combine the freeze result with the three-ingest evidence from [Ingest the LLM-Wiki and OKF foundation sources](15-ingest-llm-wiki-okf-foundation-sources.md) to decide the complete batch-ingestion gate. Do not perform broad redundancy cleanup.

## Comments

- Created during resolution of [Design a repository-root LLM-Wiki using OKF v0.2](12-design-repository-root-llm-wiki-okf.md).
- Failure to meet the freeze criteria must identify the required schema change and keep [Clean redundancy after structural freeze](17-clean-redundancy-after-structural-freeze.md) blocked.
- Claimed on 2026-08-16 after the user resumed work past the Stop checkpoint recorded at the ingest gate.
- At the significance gate the user accepted the "no further schema change" reading of the freeze criterion, and asked that freeze be made explicitly revocable rather than left implicit. The concern was that a standing freeze would discourage a schema change that later work genuinely needs. The profile now has a `## Structural freeze` section stating that freeze certifies only that nothing is currently owed, that a later revision is always permitted, and that a post-freeze change has exactly two consequences — the claim lapses and the ingest streak restarts — while never invalidating a published concept. The workflow adds the matching instruction not to work around the schema to protect the claim, and `CONTEXT.md` gains the **structural freeze** term, which was previously a load-bearing gate with no entry in the ubiquitous language.

## Answer

Structural freeze is **certified**. The complete batch-ingestion gate is **not opened**.

### Prerequisite: profile 0.3

Extraction was blocked on the same class of obstruction that blocked ingestion: profile 0.2's path mapping is exhaustive and registered no destination for `definition`, `theorem`, or `experiment-report`, and assigning a path requires a profile version change. [Assign definition, theorem, and experiment-report paths in profile 0.3](../../../docs/adr/0006-assign-definition-theorem-and-experiment-report-paths.md) assigns `research/definitions/*.md` and `research/theorems/*.md` as canonical and `reports/experiments/*.md` as evidence, and the whole bundle was relabelled as a metadata-only migration on the terms ADR 0005 established. `experiment-report` was assigned now, before any experiment exists, precisely so that the first experiment does not force another bump.

That closes the mapping: **every registered type now has a destination**, which is the substantive reason freeze is credible after 0.3 and was not after 0.2.

### Extraction

Six canonical concepts were created, each the single canonical home of one normalized claim, each short, and each citing the long evidence note that carries its reasoning:

| Concept | Claim it owns |
|---|---|
| [The corrected out quasi-Gini mean](../../../research/definitions/corrected-out-quasi-gini-mean.md) | The numerator-preserving repair and its diagonal extension |
| [The guarded corrected-mean SmartDCA rule](../../../research/definitions/guarded-corrected-mean-smartdca-rule.md) | The safety floor plus the bounded causal score inside it |
| [Exact mean classification of the source out functional](../../../research/theorems/source-out-functional-mean-classification.md) | Eq. (70) is a mean iff \(f=\mathrm{id}\) or \(d=1\) |
| [Homogeneity characterization](../../../research/theorems/corrected-mean-homogeneity-characterization.md) | Degree-one homogeneity iff the transform cancels or is normalized-multiplicative |
| [Causal DCA dominance impossibility](../../../research/theorems/causal-dca-dominance-impossibility.md) | Universal weak dominance forces DCA transaction by transaction |
| [Epsilon-DCA safety is exactly a unit-coverage guardrail](../../../research/theorems/epsilon-dca-safety-unit-guardrail.md) | Terminal floor, prefix coverage, and the sharp per-purchase floor are equivalent |

The split rule applied throughout: a definition concept carries the object, its conditions, its limiting extension, and the identities it must preserve; a theorem concept carries hypotheses, the exact claim, its sharpness, and what it does not establish; neither carries the proof. Every concept has a `## What it does not claim` section, because the failure mode this corpus is exposed to is a true statement quoted without its scope.

Nothing was moved or deleted. All eight evidence notes keep their paths and stable identities and gained a reciprocal **canonical home** pointer, so the graph is bidirectional: canonical concepts cite their notes in `sources` with footnote joins, and each note names the concept that now carries its statement. The map, tickets, and prototype keep their accepted roles untouched. No `experiment-report` was created, because no experiment has been run.

The glossary was rewired rather than extended for its own sake: each mathematical term now leads with its canonical home, and the three note or ticket citations that existed only as stand-ins for a missing canonical page were removed because the canonical page now carries them. Three terms were added — **definition concept**, **theorem concept**, and **source authority ordering**.

No new synthesis was warranted. The one cross-source integration this corpus needs already existed as a draft; nothing in the freeze-audit ingest created a second reusable conflict, since the source paper's disagreements with this project are recorded per claim in the theorem concepts rather than needing reconciliation across sources.

### The named freeze-audit ingest

[The SmartDCA superiority source paper](../../../references/summaries/smartdca-superiority-source-paper.md) was ingested as one supervised cycle: fingerprint, summary, index row, log event, lint, review. Its bytes were already in the repository, so two provenance qualifications are recorded in the summary rather than papered over — `retrieved_at` is the Git-recorded import time rather than an observed fetch, and `resource` is the arXiv abstract page as the stable citable origin. The immutable arXiv `v1` identifier is the stronger edition evidence.

The summary records the paper's six theorems, its \(\rho\)- and \((f)\)-SmartDCA family, its in/out split, its Eq. (54)/(70)/(71) appendix material, and its S&P 500 and Bitcoin backtests, then states four structural gaps: the criterion is price per unit under unequal spending rather than terminal wealth on a common deposit sequence; there is no budget model; the reference price is unpinned, so causality is not determined; and the empirical design is favourable by construction. It also discloses its own limit — the text extraction lost Greek letters and subscripts, so it describes structure and prose claims and cross-checks every equation and theorem number against the previously reviewed audit note rather than transcribing glyphs.

### Representative query and the promotion decision

Query: *can the SmartDCA rule be claimed to beat DCA, and under what conditions?* Retrieval ran off the root index into the canonical theorem group, then into the guarded rule and the glossary — no hybrid search, two hops. The answer assembles cleanly: no causal fully funded strategy weakly dominates DCA on every positive path; at any positive tolerance the guarantee available is a relative-wealth floor and not dominance; the guarded rule claims exactly that floor and no more; and a strict improvement requires a stated path class, stochastic estimand, or utility criterion, which remains open. Two sharper probes — whether average acquisition cost equals the corrected mean, and which source governs when the OKF specification and the trust article disagree — were also answered from existing concepts.

**Promotion was correctly skipped.** Every link of the chain is already stated in the concept that owns it, including the negative clauses, so the query result is a traverse rather than new knowledge and remains ephemeral. One term *was* added to the glossary in this ticket, the source authority ordering, but that is a consequence of promoting the synthesis to stable and not a query-result promotion; the distinction is recorded here deliberately.

### Independent review of the high-risk canonical concepts

Every high-risk canonical concept was reviewed under a run distinct from the run that wrote it: the six new definitions and theorems against their evidence notes and their originating tickets; ADR 0006 and the amended profile against the validator they specify; the glossary against its rewired sources; and the draft [foundation-source synthesis](../../../research/synthesis/okf-foundation-source-conflicts.md), which is now **stable**.

The synthesis review produced a substantive result. Its sharpest resolution, Conflict 1, was re-verified byte-exactly against the preserved Apache-2.0 snapshots: the specification snapshot does write `author: team:ga4-docs` and `author: team:finance-fpa` in its own examples while admitting only three actor forms, and the captured example concept does carry a conformant `human:` author in its `sources` entries — so the claim is accurate and is not a conflation of `verified.by` with `sources[].author`, which was the reviewer's initial suspicion. Two quoted specifics cannot be re-verified from this bundle at all, because their origins are non-redistributable and dynamically rendered: the proposal's per-entry log-heading form and the trust article's `team:data-platform` example. Neither carries a resolution on its own, and that coverage boundary is now recorded in the synthesis rather than left implicit.

### Freeze certification

Certified, under the explicit reading that the criterion is *no further schema change is required*, not *no schema change occurred in this ticket*. A schema change did occur here, and this is the second consecutive ticket to make one, so the reading is stated rather than assumed.

| Dimension | Verdict |
|---|---|
| Profile | No further change required. The path mapping is complete: every registered type has a destination and no assignment is pending. The field schema, the type vocabulary, the roles, and the lifecycle extensions are unchanged since 0.1; the only non-path rule added since is 0.2's one-source rule for a summary. |
| Index | No change. The role-then-type grammar absorbed two new type subgroups with no format change. |
| Workflow | No change. The [LLM-Wiki workflow](../../../docs/agents/llm-wiki-workflow.md) was not edited: its authoring, ingest, query-promotion, and review steps covered this ticket as written. |
| Roles | No change. `definition` and `theorem` are canonical, `experiment-report` is evidence; no fourth role was needed. |
| Validation | No structural change. The validator gained three path rules and one reworded message — data, not a new rule kind, finding code, or harness. |
| Retrieval | No change. The query ran off the index and canonical concepts at 52 concepts and 6 sources, well below the ~100-source threshold for hybrid search. |

The honest counter is that two consecutive tickets each needed a path assignment, which is a pattern rather than an accident. What ends the pattern is that the mapping is now closed: the remaining way to force a version change is to add a *type*, which is a far rarer event than filling in a destination the profile itself already flagged as owed.

### The complete batch-ingestion gate

The gate requires structural freeze **and** three consecutive supervised ingests without schema changes, conformance failures, or high-severity semantic corrections. Freeze is certified; the ingest streak is not.

[Ticket 15](15-ingest-llm-wiki-okf-foundation-sources.md) recorded its first three ingests as consecutive, supervised, and clean, and left the two qualifiers for this ticket: profile 0.2 landed immediately *before* ingest 1, and a smaller profile amendment landed after ingest 5. The freeze-audit ingest here was itself clean — no schema change during it, no conformance failure, and no high-severity semantic correction, since the review confirmed the summary's claims and corrected nothing — but profile 0.3 landed immediately before it too.

**Decision: the gate stays closed.** It reopens on three consecutive supervised ingests performed *after* this certification. The freeze-audit ingest does **not** count toward them: it ran at 09:32 and the certification is timestamped 09:54, so it preceded the very certification that is supposed to make the schema stable. Three ingests are still needed, not two.

The discriminator is deliberately the certification and not the gap between ingests. Judging the streak by whether a schema change happened to fall between two ingests is what makes the ticket-15 evidence unreadable — that streak is bracketed by a change immediately before it and two after it, and the freeze-audit ingest here is likewise preceded by profile 0.3. On that criterion no streak in this project's history is clean, and the one here would be no cleaner than ticket 15's. Certification is a different kind of fact: it is the claim that the mapping is closed and nothing further is owed, which is exactly the condition the gate wants evidence for. So the rejected alternative — counting ticket 15's streak as satisfying the letter of the gate, on the reading that schema changes count only *between* the three ingests — is rejected not because that reading is wrong but because it measures the wrong thing. The first batch, when it comes, still remains draft pending batch-level review.

No document needed amending to record this, because the [LLM-Wiki workflow](../../../docs/agents/llm-wiki-workflow.md) already assigns the full-gate verdict to this ticket and the profile already defers batch ingestion to "structural freeze and the supervised-ingest gate". That nothing had to change to record the decision is itself part of the freeze evidence.

[Clean redundancy after structural freeze](17-clean-redundancy-after-structural-freeze.md) is therefore unblocked. It is not claimed: no broad redundancy cleanup was performed here, and the notes still cite the source paper as declared `scope` rather than joining the newly fingerprinted snapshot, which is cleanup work with a real re-verification cascade behind it.

### Verification performed

`python -m unittest tools.okf.tests.test_validate_cli` passes 26 fixtures — the complete-path-mapping fixture was extended to cover all five paths assigned since 0.1, closing a gap left by ticket 15, and a new fixture pins type and role per path for the three 0.3 assignments. That fixture was mutation-tested: remapping `research/definitions/` to `research-note`/`evidence` in the validator makes it fail, so it is not passing vacuously. `python tools/okf/validate.py . --strict` is clean on both layers with Git-history checks active. All four checks under `reproducibility/checks/` still pass; no mathematical content was changed.

### Independent Standards and Spec review

Both reviews ran against the working diff and this ticket, and both found real defects. Every actionable finding is resolved.

The blanket `0.2`-to-`0.3` relabelling overreached into historical prose. It rewrote the profile's own changelog paragraph so that 0.2's three changes were attributed to 0.3 and contradicted the adjacent 0.3 paragraph, and it rewrote ticket 15's record of what that ticket published. Both are restored, and the 0.3 paragraph now states the 0.2-to-0.3 relabelling rule it had omitted. A dangling reference to the renamed "initial path mapping" section in the validator contract is fixed.

The glossary rewiring was applied inconsistently: two terms kept both their canonical home and their evidence note while the homogeneity and guardrail terms silently lost theirs. The rule is now stated in the glossary's own Sources section — canonical home first, then the note whose proof, counterexamples, or primary sources the canonical page deliberately does not carry — and applied uniformly, so the two notes are restored. Only `ticket-05` remains dropped, because the definition concept now carries that ticket's content in full.

The batch-gate reasoning was internally inconsistent: it disqualified ticket 15's streak partly because a schema change preceded its first ingest, then counted the freeze-audit ingest as a fresh first despite the same being true of it. The reasoning above is rewritten to make certification, not the spacing of schema changes, the discriminator, and the freeze-audit ingest no longer counts — three post-certification ingests are needed rather than two. The freeze table's claim that the schema was "unchanged since 0.1" is corrected to name 0.2's one-source rule. One log event that covered two distinct review runs is split into the three events the frontmatter actually records.

The Spec review's sharpest point is recorded rather than resolved by argument: this ticket's Comments say that *failure* to meet the freeze criteria must identify the required schema change and keep ticket 17 blocked, and this ticket did identify a required schema change — the three unassigned paths. The reading taken here is that the clause addresses a schema change still *owed* at certification time rather than one discharged during the ticket, since the literal alternative makes the Question self-contradictory: it mandates definition and theorem concepts that profile 0.2 had no conformant path for. That reading is the reviewer's flagged judgement call, it is the user's to overturn at the significance gate, and if overturned the consequence is precise — freeze is withheld, ticket 17 returns to blocked, and profile 0.3 is the identified schema change.

### Limits

One `generation_run` covers every write in this ticket, from the profile revision at 09:24 to the map synchronization at 09:54, so a review run recorded at 09:26 shares its subject identifier with content generated later. That follows the precedent of the migration and the ingest ticket, and no profile rule is broken — each review's `at` is still at or after the `generated.at` of the content it reviewed, and no reviewed body changed afterwards — but the run identifier is coarser than the per-operation granularity the field name suggests, and a future ticket may want one run per logged operation.

Every review here was performed by the same actor under a distinct review run. That satisfies the profile and follows the precedent set by the migration, but it is not review by a different party, and this standing limitation is unchanged. The freeze certification is a statement about the schema, not about content: it does not assert that the corpus is complete or free of redundancy. Two of the six sources ingested to date, plus the gist, retain fingerprints that identify an analysed response rather than a recoverable artifact. The source-paper summary's structural reading of the paper rests on a lossy text extraction, mitigated by cross-checking against the independently reviewed audit note but not eliminated.
