# Safety-adaptivity discussion manuscript audit

Review status: **passed** independent domain and statistical-language review
on 2026-09-05, and final Standards/specification rechecks on 2026-09-06.

## Scope and authority

Ticket [12](../../.scratch/smartdca/efforts/thesis-manuscript-assembly/issues/12-synthesize-safety-adaptivity-tradeoff-limitations.md)
replaces the Chapter 9 structural placeholder in the
[canonical manuscript](../../manuscript/source/thesis.tex) with the central
finding, comparison of evidence layers, comparator and mechanism interpretation,
contribution synthesis, limitations, and future-research boundary. Chapters 7
and 8 remain the detailed result homes. No accepted protocol, input, run bundle,
scientific theorem, or underlying empirical conclusion changes.

The governing evidence is the [publication-ready synthesis
report](../../reports/experiments/safety-adaptivity-tradeoff-synthesis.md), its
[detailed audit](safety-adaptivity-tradeoff-synthesis-audit.md), and the
[independent empirical-package review](safety-adaptivity-empirical-package-review.md).
The accepted synthesis identity remains
`smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26`.
Its [cross-layer summary](../../reports/experiments/runs/smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26/cross-layer-summary.csv)
and [claim receipts](../../reports/experiments/runs/smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26/claim-receipts.json)
reconcile the numerical statements. Chapter 9 introduces no computed table or
figure: existing generated assets remain in Chapters 7--8 and Appendix E and
are referenced at their original scope.

## Claim reconciliation

| Claim ID | Chapter 9 role | Authority and boundary |
|---|---|---|
| `claim-empirical-central-synthesis` | central safety-adaptivity finding | [impossibility](../theorems/causal-dca-dominance-impossibility.md), [guardrail](../theorems/epsilon-dca-safety-unit-guardrail.md), [terminal boundary](../theorems/arbitrary-horizon-performance-boundary.md), and accepted synthesis; the proof supplies safety independently of the selector |
| `claim-discussion-layer-comparison` | four evidence layers | machine cross-layer summary and synthesis audit; signs and counts are not pooled or treated as independent replications |
| `claim-discussion-comparators-mechanisms` | H1, H2, S1, floor feedback, cash and units | [cash-feedback note](cash-single-crossing-mechanism.md), terminal boundary, synthesis audit, and [historical manuscript audit](historical-robustness-evaluation-manuscript-audit.md); mean dollar attribution is not additive median-relative attribution or causal isolation |
| `claim-discussion-contributions` | five contribution categories and negative result | contribution/non-claim controls, [mean-theory review](corrected-mean-prior-theory-literature.md), and [methodology literature](reproducible-computational-finance-statistical-methodology.md); no new mean class or invented statistical method |
| `claim-discussion-limitations` | financial, data, parameter, dependence, regime, and external-validity limits | theorem, synthesis audit, [methodology manuscript audit](empirical-methodology-reproducibility-manuscript-audit.md), historical audit, and [provider review](yahoo-finance-historical-data-provider-review.md) |
| `claim-discussion-future-boundary` | deferred research | approved ticket/specification, synthesis audit, and [ADR 0008](../../docs/adr/0008-place-empirical-protocol-input-run-layers.md); proposals do not enter accepted evidence |

The existing historical and synthetic claim records remain authoritative for
individual results. The new layer-comparison record maps their integrative
restatement, rather than introducing a second statistical result. No notation
is introduced: policy superscripts, coverage, and terminal differences retain
the definitions already recorded in the notation register.

The Chapter 9 numerical restatements are limited to:

- the primary 60-month, lambda 0.75 stochastic slice: complete-system family
  medians have 3 negative and 2 positive signs; signal-only medians have 1
  negative and 4 positive signs, each cell using 3 saved seeds;
- primary history: 18 negative H1 medians and 9 Holm rejections in the negative
  direction; 17 negative and 1 positive H2 median with 0 Holm rejections;
- non-unit frictionless monthly additional-coverage robustness: 30 negative H1-comparator and 30
  negative H2-comparator medians; non-unit frictionless quarterly robustness: 48 negative
  complete-system medians and 40 negative plus 8 positive signal-only medians;
- the source dates, monthly and quarterly horizons, USD 1000 deposit, primary
  identity-transform alpha=beta=0 equal-weight configuration, four unexecuted
  alternate configurations, and four quarterly 120-month BTC-USD starts already
  specified in Chapters 6 and 8.

These are source-specific statements, not sums of sampling units. Primary H1
and H2 use the shared 36-cell registered Holm family; S1 and robustness retain
no confirmatory significance claim. The contribution matrix now explicitly
calls safety observations finite implementation checks consistent with the
proof, and includes descriptive robustness separately. The non-claim matrix
also records no capital/drawdown protection, optimal coverage, or inclusion of
future evidence.

## Reconciliation of the presentation plans

The independent specification review found six accepted Chapter 9 display
plans still targeting absent table or figure labels. Ticket 12 explicitly
retires these manuscript-display plans, not their underlying evidence or
scientific claims. Their stable IDs, original targets, wording, and immutable
source authorities are retained for traceability. Each record is now
non-mandatory, reviewed, marked `retired-manuscript-display-plan`, and points
to the actual discussion section and its current integrative claim.

| Retired display-plan ID | Current discussion location | Current claim |
|---|---|---|
| `claim-table-cross-layer` | `sec:discussion-evidence-layers` | `claim-discussion-layer-comparison` |
| `claim-table-cost-scope` | `sec:discussion-limitations` | `claim-discussion-limitations` |
| `claim-figure-safety-factor` | `sec:discussion-mechanisms` | `claim-discussion-comparators-mechanisms` |
| `claim-figure-mechanisms` | `sec:discussion-mechanisms` | `claim-discussion-comparators-mechanisms` |
| `claim-figure-terminal-attribution` | `sec:discussion-mechanisms` | `claim-discussion-comparators-mechanisms` |
| `claim-figure-net-cost` | `sec:discussion-limitations` | `claim-discussion-limitations` |

This is an editorial placement decision within the approved body-versus-linked-
supplementary-material boundary: Chapters 7--8 and Appendix E already display
the detailed generated results, and Chapter 9 connects their meaning. The
complete cross-layer tables and curves remain in the accepted synthesis report,
now directly hyperlinked from Chapter 9 at the immutable base commit. No
planned display is silently counted as rendered, no table/figure number is
invented, and no scientific requirement or accepted evidence is removed.
The historical `planned-table` and `planned-figure` entry types identify the
retained original plans; their explicit presentation status records retirement.

## Interpretation of limitations

The principal/drawdown distinction follows directly from the theorem's
DCA-relative terminal-wealth criterion; neither a deposit floor nor a running
peak occurs in that guarantee. The vintage-data limitation is a scope
inference from the accepted acquisition design: prefix-only computation on a
retained adjusted series does not itself certify availability of the same
adjusted values at historical decision time. It is not a claim that a specific
accepted value was unavailable or that a measured look-ahead effect occurred.
Provider and adjustment semantics remain those of the reviewed source seam;
this slice makes no new current provider-policy assertion.

The mathematical, computational, methodological, empirical, and integrative
contribution records now link to this audit and Chapter 9. The introduction,
conclusion, and abstract remain ticket 13. The future questions are proposals
requiring separate specification, appropriate registration, new evidence
identities, and independent review; none is an executed extension.

## Verification and review record

The independent domain reviewer read the canonical theorems, cash-feedback
note, source protocols, synthesis and historical audits, provider review, and
manuscript controls. Result: **pass**, with no scientific blocker. The review
confirmed theorem scope, guardrail attribution, ledger conditioning,
selector-dependent feedback, source/vintage scope, and future-work exclusions.

The independent statistical-language reviewer verified source artifact hashes,
recomputed all 15 displayed slice/comparator sign counts, checked the shared
36-cell uncertainty family (9 negative H1 rejections and 0 H2), and verified
positive mean cash contributions outweighed by negative mean unit contributions
in all 18 H1 cells. Result: **pass**, with no blocker. Its sole requested
clarification was applied: robustness counts explicitly identify the non-unit
frictionless slices. The review found no pooled inference, equivalence,
additive-median, causal, expected-performance, or optimality overclaim.

Focused validation passed under CPython 3.12:

- 19 tests across `check_safety_adaptivity_synthesis`,
  `check_deterministic_stochastic_evaluation`, and
  `check_historical_robustness_manuscript`, including accepted synthesis
  regeneration and existing generated-asset byte comparisons;
- 29 manuscript control, release-check, and rendered-build tests;
- exact scientific checks for pathwise DCA impossibility, epsilon-DCA safety,
  the guarded corrected-mean rule, cash single crossing, and the
  arbitrary-horizon performance boundary; and
- `python manuscript/check_controls.py` and
  `python tools/check_markdown_links.py .`.

The canonical `python manuscript/build.py` output is a controlled partial draft,
not a submission candidate. The executor visually inspected Chapter 9's six
pages (printed 59--64), correcting a long-line overflow and an almost-empty
continuation page. The final 113-page A4 build passed after the presentation
reconciliation; every Chapter 9 page was re-rendered and inspected with no
clipping, overlapping text, broken references, or unreadable symbols. The final
LaTeX/BibTeX logs contain no warnings, overfull/underfull boxes, or undefined
references/citations. The combined 48-test focused suite passed again on the
reconciled source. The release checker still exits with expected status 1 for
the pre-existing unresolved submission requirements and draft placeholders.

### Standards review

The independent Standards review passed the original slice with zero hard
violations and zero baseline smell findings. The separate correction review
also passed: stable IDs and scientific sources are preserved; presentation
retirement is explicit; additional metadata documents the editorial decision
without claiming automated enforcement; and the immutable report link respects
the artifact and manuscript-source policies.

### Specification review

The independent Spec review initially found one P2 issue: six accepted display
plans targeted absent Chapter 9 labels. The correction reconciled those plans
as documented above. Independent recheck on 2026-09-06 confirmed that the
parent specification permits linked supplementary material, all actual
sections and integrative claims exist, and no scientific evidence or acceptance
requirement is removed. The finding is resolved; there are no remaining
specification findings.

Final review totals: Standards 0 findings; Spec 1 corrected, 0 remaining.
Ticket 12 has no outstanding implementation or review blocker.
