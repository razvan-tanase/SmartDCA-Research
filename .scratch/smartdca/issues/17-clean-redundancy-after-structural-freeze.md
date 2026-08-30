---
profile: smartdca-okf/0.5
type: research-ticket
title: "Clean redundancy after structural freeze"
description: "Resolved task ticket cleaning redundancy and applying supersession after structural freeze."
knowledge_role: operational
status: stable
ticket_type: task
ticket_status: resolved
generated:
  by: claude-code/smartdca-wiki-0.1
  at: 2026-08-16T10:50:00Z
generation_run: urn:uuid:51b6a4df-c98b-4784-83e4-3b068e4014ab
---
# Clean redundancy after structural freeze

Type: task
Status: resolved
Blocked by: 16
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

After [Extract initial semantic concepts and certify structural freeze](16-extract-semantic-concepts-certify-freeze.md) certifies structural freeze, audit repeated claims across the glossary, map, tickets, research notes, source summaries, and canonical concepts. Preserve one canonical home per normalized claim, retain only the local context needed for evidence and operational records to remain understandable, add links to canonical concepts, and deprecate or supersede stable concepts without deleting their Concept IDs. Resolve or explicitly retain contradictions, run the full semantic lint and all repository checks, and record a conformant cleanup event. Do not alter mathematical conclusions merely to reduce textual repetition.

## Comments

- Created during resolution of [Design a repository-root LLM-Wiki using OKF v0.2](12-design-repository-root-llm-wiki-okf.md).
- Cleanup remains blocked until structural freeze is explicitly certified.
- Claimed on 2026-08-16 after [Extract initial semantic concepts and certify structural freeze](16-extract-semantic-concepts-certify-freeze.md) certified freeze and left this ticket unblocked but unclaimed.

## Answer

Cleanup is complete. **No concept was deleted, deprecated, or superseded**, and no
mathematical conclusion changed. The schema did not change either, so the structural freeze
certified by [Extract initial semantic concepts and certify structural freeze](16-extract-semantic-concepts-certify-freeze.md)
has not lapsed.

### The redundancy audit

Repeated claims were audited across the glossary, the map, all seventeen tickets, the eight
research notes, the six source summaries, the six canonical definitions and theorems, and
the synthesis. The audit separates three kinds of repetition, and only the third is a
defect.

**Provenance-bearing repetition is kept.** The six source summaries were audited and needed
no textual change; they appear in the diff carrying a re-verification event only, and only
where their evidence moved beneath them. Of the six canonical definitions and theorems, four
likewise needed no textual change and two gained the model-inheritance pointers described
below. Each source summary restates what its own source
says, including where two sources say the same thing; the profile explicitly permits this,
and collapsing it would destroy the per-source attribution that makes the summaries usable.
The same applies to ticket answers: a resolved ticket is the historical record of what was
concluded when, and rewriting seventeen of them to point at pages that did not exist at the
time would falsify the record rather than tidy it. Not one ticket body was edited except
this one.

**Intelligibility repetition is kept but marked.** Six documents restate the fair comparison
model — causal, long-only, buy-only, fully funded purchases, cash carried without interest,
terminal wealth including cash — because a proof is unreadable without its recursions in
front of the reader. Rather than delete these, the model now has a named canonical home:
the *Statement* section of [Causal DCA dominance impossibility](../../../research/theorems/causal-dca-dominance-impossibility.md),
which says so explicitly. The three notes that restate the model now say they are inheriting
it rather than defining it, and so does
[the guarded SmartDCA rule](../../../research/definitions/guarded-corrected-mean-smartdca-rule.md),
whose *Setting* previously repeated the model's assumptions without citing the concept that
fixes them — the guardrail theorem was the only concept already inheriting by reference. The four glossary model terms — sequential admissibility, the
deposit budget, the DCA comparator, and terminal wealth — were joined to that home as well;
they previously led with the evidence note, which violated the glossary's own stated
canonical-home-first rule. The corrected mean's formula and its diagonal extension got the
same treatment in the homogeneity note.

**Unlinked and stale repetition is fixed.** Ten prose references that named a ticket number
where a *result* was meant — "ticket 09 proves", "the definition from ticket 05",
"ticket 04's theorem" — now name and link the canonical concept that owns the claim. Four
passages written as recommendations for future work have since been discharged, and reading
them cold suggested open questions that are closed; each now records what was delivered, by
which concept, and what remains open. References to a *decision* that a ticket actually
made, such as the guardrail theorem's note that the epsilon relaxation "is the relaxation
ticket 08 selected", are left naming the ticket, because there the ticket is the thing being
cited and is footnote-joined as a source.

### Supersession was correctly not exercised

The clause requiring that stable concepts be deprecated or superseded *without deleting
their Concept IDs* constrains how a retirement is done; it does not oblige one. Every one of
the eight research notes still carries something its canonical page deliberately does not —
a proof, a counterexample set, a primary-source table, a numerical boundary check, a search
limit — so none is made redundant by extraction and none was retired. Recording this
explicitly follows the precedent of ticket 16's correct non-promotion: the absence of a
supersession is a decision with a reason, not an omission.

### Contradictions

Four genuine cross-concept inconsistencies were found. Three are resolved; one is resolved
by disclosure.

| Inconsistency | Resolution |
|---|---|
| The guardrail note wrote the unit-coverage cushion \(R_{t-1}\), while the canonical rule and the score note write \(K_{t-1}\) and reserve \(R_{t-1}\) for the lagged corrected-mean reference — so the same symbol named two different objects across concepts that cite each other. | Renamed to \(K_{t-1}\) throughout the guardrail note, matching its canonical home. Pure notation; every formula is algebraically identical, and the guardrail check still passes. |
| Burzoni et al. was cited as "Definition 2.2 and Proposition 2.5" in the ticket-04 positioning note and as "Definition 1 and Proposition 1" in the ticket-08 novelty note, both against the same journal DOI. | The preprint and the journal number the same two results differently. The novelty note now cites the journal numbering wherever it cites the DOI and the preprint numbering only where it cites the preprint PDF, and says so. |
| The *Decision Making via Generalized Bajraktarević Means* paper was dated 2023 in one note and 2024 in another, under one DOI. | Online-first versus issue year. The prior-theory note's full reference now carries both, with a stated convention for its short labels. |
| The prior-theory note recommended naming the construction "the corrected out quasi-Gini Bajraktarević subfamily"; the project instead settled on "the corrected out quasi-Gini mean". | This is a real divergence between a recommendation and a decision, and it is recorded as such rather than reconciled by editing the recommendation away. The note now states that the recommendation was adopted in substance — the Bajraktarević identification is carried in the definition concept's scope-limit section — and rejected in wording, with the reason. |

The four upstream OKF conflicts remain where they belong, in
[the foundation-source synthesis](../../../research/synthesis/okf-foundation-source-conflicts.md);
none of them is a project-internal contradiction and none was touched.

### The deferred source-paper provenance rewiring

The map recorded that the evidence notes still cited the source paper as a declared `scope`
descriptor rather than joining its fingerprinted snapshot, and assigned the rewiring here
because of the re-verification cascade behind it. Both notes that did so — the audit and the
prior-theory positioning — now cite
[the source summary](../../../references/summaries/smartdca-superiority-source-paper.md) as
an `internal` source, so the fingerprint, the retrieval qualifications, and the paper-level
reading are reached through the one concept that owns them instead of being asserted in a
free-text scope string. The audit note keeps its direct page-anchored links into the
preserved PDF, which are now explicitly links into the bytes that summary fingerprints.

This creates a reciprocal dependency: the summary cites the audit note for its equation and
theorem numbers, and the audit note now cites the summary for the edition. That is
deliberate and matches the canonical-home pointers ticket 16 added. Neither is stale with
respect to the other, but for different reasons: the audit note was rewritten and re-reviewed
after the rewrite, while the summary's body did not change at all and it carries a
re-verification event only, recorded because its dependency moved.

Both this rewiring and the orphan fix below sit outside the literal words "repeated claims",
and both are authorized rather than volunteered: the map assigned the rewiring to this ticket
by name, and the Question's own instruction to "run the full semantic lint" is what surfaced
the orphans, since orphan pages and missing cross-references are two of the lint's checks.

### The orphan finding

Running the lint's orphan and missing-cross-reference checks surfaced one defect the earlier
tickets had left: **ADRs 0001 through 0004 were reachable only from the index.** ADRs 0005
and 0006 are cited by the profile because they assign paths; the four foundational decisions
that the profile actually implements were cited by nothing. The profile now cites
[ADR 0002](../../../docs/adr/0002-repository-root-okf-knowledge-bundle.md) at its
bundle-root rule, [ADR 0004](../../../docs/adr/0004-preserve-path-based-concept-identity.md)
at its Concept-ID rule, and
[ADR 0003](../../../docs/adr/0003-separate-knowledge-authority-and-trust.md) at its
axis-separation rule, each with a footnote join; the overview cites
[ADR 0001](../../../docs/adr/0001-versioned-research-layout.md) at the layered-separation
sentence that was restating it without attribution. Adding sources is provenance and not a
schema change: no field, enum, type, path, role, grammar, validator rule, or retrieval
mechanism moved.

### The re-verification cascade

Seven of the eight evidence notes were edited. The eighth,
[the ticket-04 primary-source positioning note](../../../research/notes/pathwise-dca-dominance-primary-sources.md),
was left untouched: it already led with its canonical home, promised no future work, and its
Burzoni numbering is the one the other note was corrected *to*. It refers to its originating
ticket as "the ticket" throughout, which is idiomatic self-reference to the document already
in its `sources` rather than an unresolved pointer to a result, so it was not rewritten for
that. It therefore has no new `generated.at` and no new verification event, which is correct
rather than an omission — neither of its dependencies moved, so it is not stale.

Bumping the other seven notes' `generated.at` makes every concept that cites them stale under
the profile's dependency rule, which is why this ticket touches more files than a cleanup
suggests. Three review runs, each distinct from the run that wrote the content, discharge it
in dependency order: the seven notes at 10:30, then the six canonical definitions and
theorems, the source summary, and the profile at 10:32, then the glossary, the overview, and
the synthesis at 10:34. No concept was left demoted to draft and none was left stale.

### Verification performed

`python -m unittest tools.okf.tests.test_validate_cli` passes its 26 fixtures unchanged —
no validator behaviour was altered, so no fixture needed to move.
`python tools/okf/validate.py . --strict` is clean on both layers with the Git-history
immutability checks active, which is the full semantic lint's mechanical half; the
contradiction, orphan, canonical-home, and provenance halves are the audit recorded above.
All four checks under `reproducibility/checks/` still pass, including the guardrail check
after the cushion rename.

### One nonconformance found and not fully fixed

The profile requires that an agent's meaningful change record `generated` and
`generation_run`. **No ticket in this tracker carried either**, including the sixteen whose
bodies were written by an agent. This ticket now carries both, because it was written under
the rule and there is no reason for the document making the finding to be the exception. The
other sixteen were left alone deliberately: back-filling them would mean asserting generation
times and run identifiers for writes whose runs are not recorded anywhere, which is
fabrication dressed as conformance. The structural validator cannot catch this, because
"meaningful" is not mechanically decidable, so it is recorded here as a standing
nonconformance for a future ticket to decide — most likely by recording the times Git already
knows rather than by inventing run identifiers.

### Independent Standards and Spec review

Both reviews ran against the working diff and this ticket, and both found real defects. Every
actionable finding is resolved, and the resolutions were re-reviewed under a fourth run at
10:48 with the dependency cascade they triggered.

Four of the findings were factual errors in this Answer, which is worth stating plainly
because the ticket is a cleanup ticket. The claim that eight evidence notes were edited was
wrong — seven were, and the eighth is now named along with the reason it needed nothing. The
count of replaced ticket-number references was inflated from ten to eleven. The reciprocal
source-paper dependency was described as two concepts "edited and re-reviewed in the same
transaction" when only one was edited. And the impossibility theorem's new text asserted that
the guarded rule points at it for the model when the guarded rule did not; that one was fixed
by making the assertion true rather than by weakening it, so the rule's *Setting* now inherits
the model by reference, which is the cleanup the sentence was describing.

Three further findings were about the tracker and the corpus rather than this text. Two
references to a result by ticket number survived in the novelty note and are now linked.
Ticket 11 was described as unblocked by the overview and the map while its own body still
listed this ticket as a blocker, so its unblocking is now recorded in its Comments, keeping
the historical `Blocked by` line the tracker's other tickets keep. And the missing ticket
generation metadata described above was found by the Standards review, not by this ticket's
own audit.

Two findings were flagged as judgement calls and are deliberately not changed. The map's
decision bullet is far longer than the workflow's "one-line gist", which is true of every
decision bullet on the map and would be a map-wide convention change rather than a cleanup.
The `Cleanup` log operation is a new event type, which the profile's "such as" list permits
and this ticket's own Question asked for by name.

### Limits

One `generation_run` covers every write in this ticket, the same coarseness recorded as a
limit in ticket 16 and unchanged here. Every review was performed by the same actor under a
distinct review run, which satisfies the profile but is still not review by a different
party. The orphan sweep was over inbound Markdown links and index rows; it does not prove
that every concept is reachable by a plausible query, only that none is link-isolated. The
notational rename was checked by re-running the guardrail check and by reading every
occurrence, not by a mechanical algebra system. Finally, the judgement that ticket bodies are
history and not redundancy is a judgement: a reader who wanted the ticket answers rewritten
to link canonical pages would find seventeen documents that were deliberately left alone.
