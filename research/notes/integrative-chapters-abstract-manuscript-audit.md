# Integrative chapters and bilingual abstract manuscript audit

Review status: **passed** independent domain, headline, statistical-language,
citation, Standards, and specification review on 2026-09-06.

## Scope and authorities

Ticket [13](../../.scratch/smartdca/efforts/thesis-manuscript-assembly/issues/13-draft-integrative-chapters-abstract.md)
replaces the introduction, conclusion, Romanian synopsis, and English abstract
placeholders and adds a closing synthesis to the reviewed literature chapter.
The [canonical source](../../manuscript/source/thesis.tex) now tells the approved
Financial Computing story through the three research questions. Detailed
proofs, results, protocols, inputs, run identities, and generated quantitative
assets retain their existing homes and bytes. No new signal, experiment,
parameter selection, scientific result, or defense material is introduced.

The [architecture](../../manuscript/controls/architecture.json),
[contributions](../../manuscript/controls/contributions.json), and
[non-claims](../../manuscript/controls/non-claims.json) supply the approved
framing. Scientific authority remains in the detailed notes linked by the
[claim register](../../manuscript/controls/claims.json), particularly the
[discussion audit](safety-adaptivity-discussion-manuscript-audit.md),
[historical audit](historical-robustness-evaluation-manuscript-audit.md), and
[independent empirical-package review](safety-adaptivity-empirical-package-review.md).

## Headline reconciliation

Existing claim IDs and primary manuscript locations are preserved.
`restatement_locations` index their repeated headlines in the new sections;
these are not new scientific claims or additional statistical observations.
The audit checks every indexed label and reads each restatement against its
primary authority. The generic control checker establishes structural control
validity, not semantic headline consistency.

| Headline | Detailed authority | Required boundary |
|---|---|---|
| RQ1: universal dominance forces DCA | [Impossibility proof](pathwise-dca-dominance-under-causal-budget.md), Chapter 4, Appendix A | Arbitrary finite positive prices, same exogenous deposits, causal fully funded long-only buy-only decisions, no cash interest, cash-inclusive common terminal valuation; no claim forbidding realized wins |
| RQ2: the unit guardrail supplies a sharp relative floor | [Guardrail proof](sharp-epsilon-dca-safety-guardrail.md), Chapter 4, Appendix A | The constraint supplies safety; full coverage collapses to DCA; positive relaxation permits discretion; no capital, drawdown, frictional, or performance guarantee |
| Exact performance is ledger-conditioned | [Boundary proof](arbitrary-horizon-performance-boundary.md), Chapter 5, Appendix B | Realized cash and unit differences and a common evaluation price classify the gap; no prediction, frequency, or expected-return assertion |
| RQ3: historical signal value is unconfirmed | [Primary audit](confirmatory-historical-evaluation-audit.md), Chapter 8 | All 18 non-unit primary frictionless H1 medians negative, nine negative Holm decisions, zero H2 Holm decisions; shared 36-test family; H2 non-rejection is not equivalence |
| Synthetic and robustness results retain their roles | [Synthesis audit](safety-adaptivity-tradeoff-synthesis-audit.md), Chapters 7--9 | Deterministic possibilities, three-seed sensitivities, registered primary inference, descriptive post-confirmatory robustness; no pooled inference |
| Corrected mean and novelty | [Mean-theory review](corrected-mean-prior-theory-literature.md), Chapters 2--3 | Known weighted Bajraktarević family; project correction/classification and bounded properties, not a new general mean class |
| Limits and future work | [Discussion audit](safety-adaptivity-discussion-manuscript-audit.md), Chapter 9 | Fixed assets, provider, schedules, horizons, parameters, overlapping episodes, finite seeds; proposed extensions require separate work and new evidence identities |

The abstracts were written after the introduction, conclusion, and literature
synthesis. They repeat the same problem, model, impossibility, floor/selector
separation, analytical role, distinct evaluation layers, historical signs, H2
non-confirmation, non-equivalence, and frictionless scope in both languages.
The Romanian synopsis has 171 whitespace-delimited source words and the
English abstract has 159. Neither introduces notation or a new citation-dependent
claim. The retained institutional contract requires at most 200 words each
on one shared page. The build test checks populated rendered text on that
shared page and both word ceilings in the authoritative prose. T1 comma-below
accents split Romanian words during PDF text extraction, so the source count
avoids treating extraction fragments as separate words. The same rendered test
now verifies the contribution table's required 9-point typography.

## Literature and contribution reconciliation

The new literature closing section connects the three already reviewed strands:
[DCA/adaptive/causal safety](dca-adaptive-causal-safety-literature.md),
[corrected-mean theory](corrected-mean-prior-theory-literature.md), and
[computational/statistical methodology](reproducible-computational-finance-statistical-methodology.md).
It contrasts the objects to which their guarantees apply rather than repeating
the source-by-source review. Existing bibliography keys support each external
positioning statement. No new external source or current provider-policy
assertion is introduced. General no-arbitrage, mean families, registration,
block resampling, and Holm adjustment remain attributed to prior literature;
project-specific formulation, artifacts, and synthesis retain bounded novelty.

The five contribution records now locate the introduction and conclusion.
The non-claim records locate their repeated boundaries there, with bilingual
locations for the four central non-claims. No notation is introduced before
its registered first use: the introductory exposition uses verbal definitions.
The frozen research questions and conservative answers are unchanged.

Two accepted display plans are realized, retaining their stable IDs:

- `claim-table-contribution-matrix`: Table 1.1 is an editorial projection of
  the contribution and non-claim registers, with detailed chapter references.
  Each row is reconciled to its register; no computed result is transcribed.
- `claim-figure-thesis-logic`: Figure 1.1 is a conceptual navigation diagram
  derived from the approved specification and architecture. Its two branches
  distinguish the guardrail's guarantee from the selector's performance.
  Its arrows are explicitly not a causal graph or a quantitative model.

The canonical LaTeX source contains both non-quantitative displays. There are
no absent introduction display labels or newly selected quantitative assets.
The manuscript README reflects the drafted integrative sections without
claiming complete-release assembly, supervisor approval, or submission readiness.

## Verification and independent review

The independent domain reviewer compared all new headline sections with
Chapters 3--9, the glossary, controls, canonical theorem notes, reviewed
literature notes, and empirical authorities. It independently joined all 36
primary uncertainty medians to historical aggregates and recomputed the shared
36-test Holm adjustment using exact fractions: zero mismatches. It confirmed
18 negative H1 medians and nine negative rejections, 17 negative plus one
positive H2 median and zero H2 rejections, no stronger Romanian translation,
no pooled or equivalence inference, and no unsupported novelty claim.

The reviewer checked all 90 initial occurrence references across 32 existing
claim records, then suggested two additional supported occurrence links for
the introduction's finite-safety checks and the conclusion's reproduction
boundary. Both were added; all 92 final references resolve. No scientific
wording or evidence needed correction.

### Standards

The independent Standards review found one P2: Table 1.1 initially used a
larger font than the institutional 9-point rule. The correction puts the
explicit font selection after the spacing command, which otherwise resets
the font. Independent rendered-XML recheck confirms 9-point text. The final
review also passes the kept-together RQ2 block, abstract checks, and occurrence
mappings. No baseline smell finding or documented-standard violation remains.

### Specification

The independent Spec review passed with zero findings. It verified the
approved narrative order, three conservative answers, five contribution
categories, non-claims, bounded synthesis, populated bilingual abstracts,
display labels, and traceability. Pending completion records were appropriately
kept pending during active execution. No new scientific artifact, experiment,
parameter, or defense material was introduced.

### Verification and rendered inspection

The canonical build produces a 119-page A4 controlled draft with no LaTeX or
BibTeX warnings, overfull/underfull boxes, or unresolved references/citations.
The executor inspected the bilingual page (printed vii), Introduction (1--4),
revised literature opening (5) and closing synthesis (13--14), and Conclusions
(68--70). The contribution table, conceptual diagram, references, typography,
and chapter transitions are legible with no clipping or overlapping content.
The RQ2 question and answer now stay together instead of splitting its heading
at the foot of a page. The final table and affected introduction pages were
rendered again after the last formatting correction.

The following ten directly intersecting scientific programs passed: pathwise
DCA dominance, corrected-mean homogeneity, epsilon-DCA guardrail, guarded
corrected-mean policy, two-purchase boundary, three-purchase boundary,
arbitrary-horizon accounting, weak-single-valley falsification, cash single
crossing, and arbitrary-horizon performance boundary. The focused unit suites
cover manuscript controls/build/release, links, synthesis and result assets,
foundations, policy architecture, analytical boundaries, methodology, and all
three literature strands. Final combined test results are recorded in the
ticket alongside the canonical build and link check.

The submission checker still exits with expected status 1 for the pre-existing
institutional/supervisor requirements and release inputs. This ticket does
not resolve those human decisions or perform ticket 14's complete-release
assembly. Accepted protocols, provider observations, run bundles, and computed
assets are unchanged.

Final review totals: Standards 1 corrected, 0 remaining; Spec 0; independent
domain/headline/statistical-language/citation review 0 blockers.
