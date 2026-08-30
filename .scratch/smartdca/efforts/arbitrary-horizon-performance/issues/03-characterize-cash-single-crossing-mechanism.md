# 03 — Characterize the cash single-crossing mechanism

Type: research
Status: resolved
Blocked by: 02
Parent: [Arbitrary-horizon guarded SmartDCA performance](../spec.md)

## Question

Determine whether the corrected rule's cash path relative to the neutral guarded
selector changes sign at most once around a price trough in the restricted
single-valley setting. Prove the strongest valid single-crossing statement or
give an exact counterexample, then extract the narrowest economically
interpretable candidate condition that is stated without reference to eventual
terminal-wealth sign.

## What to build

The project gains a rigorous mechanism-level result connecting the
corrected-mean score, guardrail activation, and cash carried across price
movements. That result either identifies a nonempty candidate path class for
the final wealth theorem or explains precisely why cash single crossing cannot
support such a class under the initial restrictions.

## Acceptance criteria

- [x] Cash-path differences and the meaning and location of a single crossing are defined for every finite horizon.
- [x] The cash single-crossing conjecture on weak single-valley paths is proved or disproved using exact assumptions and witnesses.
- [x] The role of repeated guardrail-floor activation is separated from the role of the discretionary score.
- [x] Any comparative-static property of the corrected mean used by the argument is proved on the exact parameter region required.
- [x] Every failed statement is accompanied by a minimized exact counterexample satisfying all declared assumptions.
- [x] Any surviving condition is expressed using observable price, deposit, reference, or guardrail structure rather than terminal-wealth sign.
- [x] The surviving class is shown to be nonempty, or the resolution proves why no useful class arises from this mechanism under the restricted family.
- [x] The evidence and executable cases distinguish proved facts, computational observations, and unresolved questions.

## Comments

- Created from the approved ticket decomposition of the effort specification on
  2026-08-23.
- Claimed on 2026-08-24 after ticket 02 resolved; execution uses the exact-rational
  arbitrary-horizon accounting seam established by ticket 01.
- A separate research run re-derived the cash recurrence and score comparative
  static, then supplied an independent strict counterexample. The executable
  search minimized that witness under the declared deterministic ordering.
- Initial Standards and Spec review required a diagonal boundary regression,
  consistent guardrail terminology, a proved non-necessity obstruction,
  explicit parameter complexity, and named replay of every emitted witness.
  Each item is incorporated in the review draft.
- Final Standards, Spec, and independent mathematical re-review reported no
  actionable finding after correcting the non-necessity attribution to exact
  same-period score-floor cancellation and refreshing run provenance.

## Answer

The [canonical theorem](../../../../../research/theorems/reference-aligned-guardrail-cash-single-crossing.md)
and [evidence note](../../../../../research/notes/cash-single-crossing-mechanism.md)
show that weak single-valley prices make the corrected score cross neutral at
most once, but do not make guarded corrected-minus-neutral cash single-cross.
The exact recurrence separates prior-cash carry, score forcing, and the
policy-specific clipped-floor difference.

A strict horizon-minimal witness uses unit deposits,
\(p=(1,1/16,1,8)\), \(P=p_4\), \(\lambda=63/64\), and
\((\alpha,\beta)=(-1,0)\). Its guarded cash signs are \(-,+,-\) after the
mandatory first-date tie, while disabling both floors leaves \(-,+,+\).
Differential repeated-floor activation therefore creates the second reversal.

The surviving sufficient condition is reference-aligned guardrail feedback:
at a score-crossing boundary, the corrected-minus-neutral clipped-floor
difference is nonnegative before the boundary and nonpositive afterward.
Common clipped floors are a boundary case, while an unequal-floor strict case
with strict margins gives a nonempty region. The condition is not necessary:
an exact strict witness violates alignment at date three but retains cash
signs \(-,-,+\) because same-period score forcing outweighs the misaligned
floor component.

The [experiment report](../../../../../reports/experiments/cash-single-crossing-search.md)
records the deterministic grid, minimization order, exact counts, hashes, and
scope limits. The public [search](../../../../../reproducibility/cash_single_crossing_search.py)
and [regression check](../../../../../reproducibility/checks/check_cash_single_crossing_mechanism.py)
replay the recurrence, all three emitted counterexample names, diagonal and
common-floor boundaries, the strict interior and non-necessity cases, and the
earlier ticket-02 grid. Ticket 04 remains unclaimed pending the user
approval to continue.
