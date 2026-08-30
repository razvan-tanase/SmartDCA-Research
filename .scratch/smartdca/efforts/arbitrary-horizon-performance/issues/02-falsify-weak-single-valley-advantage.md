# 02 — Falsify the weak single-valley advantage conjecture

Type: task
Status: resolved
Blocked by: 01
Parent: [Arbitrary-horizon guarded SmartDCA performance](../spec.md)

## Question

Using the verified arbitrary-horizon seam, determine whether weak single-valley
purchase-price paths alone are sufficient to give the guarded corrected-mean
rule a predictable terminal-wealth advantage over DCA or the neutral guarded
selector in the restricted countercyclical setting. Search deterministically
before attempting a general proof and minimize every decisive witness.

## What to build

A reproducible falsification report states the scope and limits of the declared
finite search. If the conjecture fails, the report supplies the
smallest exact counterexample under the declared ordering. If it survives, the
report preserves the complete search domain and states explicitly that finite
non-discovery is not proof.

## Acceptance criteria

- [x] The weak single-valley predicate is defined independently of strategy output and validated for every generated path.
- [x] The search covers declared rational grids at horizons four through eight with equal positive deposits, declared countercyclical parameters, the identity transform, and an explicit evaluation-price grid.
- [x] The grid, enumeration order, pruning rules, and computational limits are recorded.
- [x] Results distinguish corrected-versus-DCA and corrected-versus-neutral comparisons.
- [x] Guardrail-floor activation is recorded, and every reported score effect identifies whether floor activation contributed.
- [x] Any counterexample is minimized by horizon, price complexity, parameter complexity, and deposit complexity.
- [x] Every reported witness is replayed as a named exact regression case.
- [x] If no counterexample is found, the resolution limits its claim to survival of the declared finite search.

## Comments

- Created from the approved ticket decomposition of the effort specification on
  2026-08-23.
- Independent Standards and Spec review rejected a floor-divergence proxy as
  causal attribution and found two emitted genuine-cycle witnesses without
  named assertions. The final implementation uses an exact floor-disabled
  counterfactual, covers the equal-floor false-negative case, and replays all
  six emitted witness names.
- Standards review also found malformed notation, untyped search-slice keys,
  a duplicated fixture, and stale reproducibility provenance. Each finding was
  corrected and the final re-review reported no remaining actionable finding.

## Answer

The [experiment report](../../../../../reports/experiments/weak-single-valley-falsification.md)
records an exhaustive deterministic search of 61,398 exact-rational scenarios
over 2,274 independently validated weak single-valley paths at horizons four
through eight. It finds 38,132 corrected-versus-DCA losses and 16,033
corrected-versus-neutral losses on the declared grid.

The [evidence note](../../../../../research/notes/weak-single-valley-advantage-falsification.md)
derives strict four-date counterexamples at the terminal purchase price:
prices \((1,1/2,2/3,1)\) give corrected-minus-DCA wealth \(-7/32\), and
prices \((1,2/3,1,2)\) give corrected-minus-neutral wealth \(-109/8640\).
For the latter, disabling both floors changes the score comparison to
\(+49/360\); the exact floor contribution is therefore \(-257/1728\) and
reverses the sign.

The public [search](../../../../../reproducibility/weak_single_valley_search.py)
emits the complete machine-readable record, and the
[exact regression check](../../../../../reproducibility/checks/check_weak_single_valley_falsification.py)
replays every reported witness. Weak and even strict single-valley price
geometry is therefore insufficient for either proposed universal advantage.
Ticket 03 is unblocked and remains unclaimed pending the user significance
gate.
