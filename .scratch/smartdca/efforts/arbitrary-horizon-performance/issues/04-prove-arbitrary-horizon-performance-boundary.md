---
profile: smartdca-okf/0.5
type: research-ticket
title: "Prove the arbitrary-horizon performance boundary"
description: "Resolved research ticket proving the exact terminal-cash-and-units boundary for every finite-horizon guarded SmartDCA comparison."
knowledge_role: operational
status: stable
original_record: true
ticket_type: research
ticket_status: resolved
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-24T20:11:40Z
generation_run: urn:uuid:6a0602e3-5197-442d-bfc1-256ac8a382ba
verified:
  - by: openai-codex/writing-for-agents-0.1
    at: 2026-08-23T21:32:48Z
    review_run: urn:uuid:d87a04a7-92ae-43c4-a446-998b6f1a8d14
  - by: openai-codex/standards-review-0.1
    at: 2026-08-24T20:11:40Z
    review_run: urn:uuid:2d41dd92-0f83-4940-9eff-8eba11d4196d
  - by: openai-codex/spec-review-0.1
    at: 2026-08-24T20:11:40Z
    review_run: urn:uuid:c830b658-ad37-43ba-b537-690dda4f5455
---
# 04 — Prove the arbitrary-horizon performance boundary

Type: research
Status: resolved
Blocked by: 03
Parent: [Arbitrary-horizon guarded SmartDCA performance](../spec.md)

## Question

Use the accounting identity, falsification evidence, and cash-path mechanism to
prove one defensible arbitrary-horizon wealth result for the guarded
corrected-mean rule. The result may be a sharp positive theorem on an
independently defined nonempty path class or a rigorous negative theorem
showing why the strongest surviving candidate class remains insufficient.

## What to build

For every finite horizon, a reader can determine the exact scope in which the
corrected discretionary allocation has a predictable relationship to DCA and
to the neutral guarded selector. All evaluation-price conditions, strictness
conditions, safety implications, and counterexamples are explicit.

## Acceptance criteria

- [x] The theorem or negative boundary applies to every finite horizon in its declared class.
- [x] The path class and every evaluation-price condition are stated independently of eventual relative-wealth sign.
- [x] The result compares the corrected rule with DCA and with the neutral guarded selector wherever each comparison is claimed.
- [x] The epsilon-DCA safety guarantee remains inherited from the guardrail and is not attributed to the corrected-mean score.
- [x] A positive result proves a nonempty strict region and states whether its conditions are necessary, sufficient, or both.
- [x] A sufficient-only result includes a proved obstruction to necessity and preserves visible outside-class failures.
- [x] A negative result provides exact admissible counterexamples and identifies the strongest reusable missing structure justified by the proof.
- [x] Constant paths, troughs at endpoints, flat troughs, ties, floor branches, and the lambda-equals-one collapse are covered or explicitly excluded.
- [x] No stochastic, universal-dominance, parameter-superiority, or novelty claim is inferred from the theorem.
- [x] The complete proof and exact examples are recorded as evidence suitable for independent review.

## Comments

- Created from the approved tracer-bullet decomposition of the effort specification on
  2026-08-23.
- Claimed on 2026-08-24 after ticket 03 resolved; execution uses the approved
  exact-rational scenario engine as the public verification seam.
- An independent research run re-derived the cash-timing and direct-inventory
  routes, supplied the exact affine trichotomy and strict aligned witnesses,
  and wrote the complete proof note. The implementation was developed against
  the approved seam with named exact checks before repository-wide review.
- Standards and specification review required a universal non-valley analyzer,
  a separate valley diagnostic, canonical sign classification, shorter theorem
  evidence, and fresh provenance. Those findings were incorporated.
- Final Standards, specification, and independent mathematical re-review
  reported no remaining finding.

## Answer

The [canonical theorem](../../../../../research/theorems/arbitrary-horizon-performance-boundary.md)
and [complete proof](../../../../../research/notes/arbitrary-horizon-performance-boundary.md)
establish the exact every-finite-horizon boundary. For either DCA or the
neutral guarded selector \(T\), define the terminal corrected-minus-comparator
cash and unit differences

\[
H_T=C_n^c-C_n^T,\qquad U_T=Q_n^c-Q_n^T.
\]

Then \(W_n^c(P)-W_n^T(P)=H_T+P U_T\) for every positive evaluation price,
and the full cash path independently reconstructs \(U_T\). The signs of
\((H_T,U_T)\), with the unique positive root when their signs oppose, give a
necessary-and-sufficient win, tie, and loss classification. On a weak
single-valley path at \(P=p_n\), this becomes an exact balance between signed
reciprocal-price exposure on the decline and recovery.

Reference-aligned guardrail feedback remains a valid cash mechanism but is
not a wealth condition. Exact strict aligned valleys include an all-floors-
active joint win—\(p=(1,1/4,1/2,1)\), \(P=1/2\), \(\lambda=7/8\), and
\((\alpha,\beta)=(0,-1)\)—and a joint loss at
\(p=(1,2/3,1,2)\), \(P=2\), and \(\lambda=3/4\). The missing reusable
structure is therefore the terminal cash/unit pair, equivalently the
cash-weighted reciprocal-price balance, rather than another sign-only
crossing condition.

The public
[boundary report](../../../../../reproducibility/performance_boundary.py)
checks the cash-timing slope against direct terminal units on every positive
path and exposes the reciprocal-exposure specialization only for validated
weak single-valleys. Its
[named regression](../../../../../reproducibility/checks/check_arbitrary_horizon_performance_boundary.py)
covers horizons one through eight, an explicit non-valley path, prices
below/at/above a boundary, strict wins and losses, a nontrivial tie, constant
and endpoint/flat-trough paths, active/inactive/repeated floors, and the
\(\lambda=1\) DCA collapse. The epsilon-DCA guarantee remains inherited solely
from the unit guardrail. No stochastic, universal-dominance,
parameter-superiority, or novelty claim is made.
