# 01 — Establish the arbitrary-horizon accounting and verification seam

Type: task
Status: resolved
Blocked by: `.scratch/smartdca/issues/18-isolate-three-purchase-corrected-mean-effect`
Parent: [Arbitrary-horizon guarded SmartDCA performance](../spec.md)

## Question

Prove the arbitrary-horizon cash-timing identity for every fully funded strategy
in the established comparison model, derive its two-strategy form, and expose
one deterministic exact-rational scenario interface for DCA, the guarded
corrected-mean SmartDCA rule, and the neutral guarded selector. Verify that the
same interface reproduces the settled two- and three-purchase results before it
is used to investigate longer horizons.

## What to build

A researcher can submit one finite rational scenario and inspect a complete,
internally consistent ledger for all three policies: purchases, carried cash,
asset units, guardrail-floor activation, corrected references, discretionary
scores, and terminal-wealth gaps. The mathematical identity and the executable
ledger must verify each other from independent accounting routes.

## Acceptance criteria

- [x] The cash-timing identity is proved for arbitrary finite horizons, positive prices, nonnegative deposits, and a common positive evaluation price.
- [x] The two-strategy identity is derived using the difference between the strategies' cash paths.
- [x] The exact-rational scenario interface exposes every externally relevant ledger quantity for DCA, the corrected rule, and the neutral selector.
- [x] The interface reproduces the existing two-purchase win, tie, loss, and all-win cases.
- [x] The interface reproduces the existing three-purchase beta-flip witness exactly.
- [x] Active, inactive, and repeated guardrail-floor branches are covered by named checks.
- [x] Constant-price behavior, zero deposits, and the lambda-equals-one DCA collapse are checked.
- [x] The evidence record, executable check, and ticket resolution can be reviewed without hidden conversation context.

## Comments

- Created from the approved ticket decomposition of the effort specification on
  2026-08-23.
- Independent Standards and Spec review found malformed inline mathematics,
  duplicated cash-timing coefficients, unrestricted policy labels, eager
  boundary evaluation, and failure to preserve final-rational radical
  cancellations. The implementation and evidence were corrected before
  resolution.

## Answer

The [canonical theorem](../../../../../research/theorems/arbitrary-horizon-cash-timing-identity.md)
states the exact arbitrary-horizon cash-timing identity and its two-strategy
cash-path-difference form. The
[evidence note](../../../../../research/notes/arbitrary-horizon-accounting-verification-seam.md)
contains the proof, interface contract, and named exact results.

The public [scenario engine](../../../../../reproducibility/arbitrary_horizon.py)
accepts finite `Fraction` scenarios and returns independently checked DCA,
corrected, and neutral policy ledgers. Its direct portfolio accounting agrees
exactly with the cash-timing route. It preserves final rational corrected
references when irrational radical terms cancel, rejects externally required
irrational outputs without rounding, and skips irrelevant reference evaluation
when the discretionary interval is zero.

The [executable check](../../../../../reproducibility/checks/check_arbitrary_horizon_accounting_verification.py)
reproduces the settled two- and three-purchase fractions, exercises all
guardrail branches and boundary cases, and verifies five- and six-purchase
ledgers. The earlier independent two- and three-purchase checks and the full
scientific suite also pass. This resolves only the reusable accounting seam;
ticket 02 became unblocked but remained unclaimed pending user approval.
