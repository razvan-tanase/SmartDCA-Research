---
profile: smartdca-okf/0.4
type: theorem
title: "Terminal cash and units give the exact arbitrary-horizon performance boundary"
description: "Every finite-horizon corrected-rule wealth gap has an exact affine evaluation-price boundary, while single-valley cash crossing alone remains insufficient."
knowledge_role: canonical
status: stable
sources:
  - id: performance-note
    title: "Exact arbitrary-horizon evaluation-price boundary for guarded SmartDCA"
    resource: research/notes/arbitrary-horizon-performance-boundary
    source_kind: internal
  - id: ticket-04
    title: "Prove the arbitrary-horizon performance boundary"
    resource: .scratch/smartdca/efforts/arbitrary-horizon-performance/issues/04-prove-arbitrary-horizon-performance-boundary
    source_kind: internal
  - id: cash-timing
    title: "Arbitrary-horizon terminal wealth has an exact cash-timing identity"
    resource: research/theorems/arbitrary-horizon-cash-timing-identity
    source_kind: internal
  - id: cash-crossing
    title: "Reference-aligned guardrail feedback preserves cash single crossing"
    resource: research/theorems/reference-aligned-guardrail-cash-single-crossing
    source_kind: internal
  - id: guardrail
    title: "Epsilon-DCA safety is exactly a causal unit-coverage guardrail"
    resource: research/theorems/epsilon-dca-safety-unit-guardrail
    source_kind: internal
  - id: package-review
    title: "Independent review of the arbitrary-horizon research package"
    resource: research/notes/arbitrary-horizon-research-package-review
    source_kind: internal
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-24T20:55:04Z
generation_run: urn:uuid:c8785a76-9c52-4377-ab6e-4a44c3e403e6
verified:
  - by: openai-codex/standards-review-0.1
    at: 2026-08-24T20:11:40Z
    review_run: urn:uuid:2d41dd92-0f83-4940-9eff-8eba11d4196d
  - by: openai-codex/spec-review-0.1
    at: 2026-08-24T20:11:40Z
    review_run: urn:uuid:c830b658-ad37-43ba-b537-690dda4f5455
  - by: openai-codex/independent-math-review-0.1
    at: 2026-08-24T21:12:56Z
    review_run: urn:uuid:1694bf39-9777-4b36-bd09-5c6abc74460e
  - by: openai-codex/standards-review-0.1
    at: 2026-08-24T21:31:55Z
    review_run: urn:uuid:8185820b-9b80-4607-91f0-43335cfbdff5
  - by: openai-codex/spec-review-0.1
    at: 2026-08-24T21:31:55Z
    review_run: urn:uuid:8da58364-ea0f-42bb-a729-d559abe6e7e7
---
# Terminal cash and units give the exact arbitrary-horizon performance boundary

## Statement

Fix any finite positive purchase-price path and common deposit sequence in the
project's fully funded comparison model. Run the guarded corrected-mean rule
\(c\), and let \(T\) be either DCA or the neutral guarded selector. Purchases do
not depend on the later common evaluation price \(P>0\). Define the terminal
cash and unit differences

\[
H_T=C_n^c-C_n^T,
\qquad
U_T=Q_n^c-Q_n^T.
\]

Then, at every finite horizon,[^performance-note][^cash-timing][^ticket-04]

\[
\boxed{W_n^c(P)-W_n^T(P)=H_T+P U_T.}
\tag{1}
\]

If \(D_t^T=C_t^c-C_t^T\), the same unit difference is recovered independently
from the complete cash path:

\[
\boxed{
U_T=
\sum_{t=1}^{n-1}D_t^T
\left(\frac1{p_{t+1}}-\frac1{p_t}\right)
-\frac{D_n^T}{p_n}.
}
\tag{2}
\]

Equations (1)--(2) give a necessary-and-sufficient evaluation-price
classification:

- if \(H_T>0\) and \(U_T<0\), corrected wins for
  \(0<P<H_T/(-U_T)\), ties at that boundary, and loses above it;
- if \(H_T<0\) and \(U_T>0\), the order reverses around
  \((-H_T)/U_T\);
- if \(H_T\) and \(U_T\) are both nonnegative and not both zero, corrected
  strictly wins for every \(P>0\), while two nonpositive values that are not
  both zero give a strict loss; and
- \(H_T=U_T=0\) gives a tie for every \(P>0\).

The zero-intercept cases inherit the sign of \(U_T\) for every positive \(P\).
The corrected rule beats both comparators exactly on the intersection of their
two strict-win regions.

## Weak single-valley specialization

Let the purchase path be weak single-valley with first trough at date \(k\),
and set \(P=p_n\). Define the signed reciprocal-price exposures

\[
A_T=\sum_{t<k}D_t^T
\left(\frac1{p_{t+1}}-\frac1{p_t}\right),
\qquad
B_T=\sum_{t\ge k}D_t^T
\left(\frac1{p_t}-\frac1{p_{t+1}}\right).
\]

Then the exact terminal-price boundary is

\[
\boxed{W_n^c(p_n)-W_n^T(p_n)=p_n(A_T-B_T).}
\tag{3}
\]

Thus corrected wins, ties, or loses exactly as \(A_T\) is greater than, equal
to, or less than \(B_T\). Against DCA, \(D_t^D=C_t^c\ge0\), so both exposures
are nonnegative. A trough at the final date makes \(B_D=0\) and yields a weak
DCA win; a trough at the first date makes \(A_D=0\) and yields a weak DCA
loss. Strictness is exactly positivity of the remaining exposure. Constant
paths tie at \(P=p_n\), and flat steps contribute zero without needing to be
excluded.[^performance-note]

Reference-aligned guardrail feedback makes corrected-minus-neutral cash
single-cross, but does not compare the signed magnitudes \(A_0\) and \(B_0\).
It is therefore insufficient to sign wealth.[^cash-crossing] Exact strict,
reference-aligned four-date valleys in the evidence include both a strict
joint win and a strict joint loss. The all-floors-active win lies in a
nonempty strict region. The loss proves that strict slopes, a completed
aligned cash crossing, repeated floor activation, and terminal-purchase-price
evaluation still do not replace (1)--(3).[^performance-note]

## Safety and scope

The corrected and neutral rules retain
\(W_n^S(P)\ge\lambda W_n^{DCA}(P)\) for every admissible path because their
purchases obey the epsilon-DCA unit guardrail.[^guardrail] That safety result
belongs to the floor. It is not supplied by the corrected-mean score, by a
cash crossing, or by a favorable region of (1).

At \(\lambda=1\), both guarded selectors collapse to DCA, so
\(H_T=U_T=0\) and all comparisons tie. The theorem otherwise covers active,
inactive, repeated, unequal, and clipping-boundary floor branches through the
realized ledgers. It makes no stochastic, expected-performance,
universal-dominance, parameter-superiority, or novelty claim. No price-only
necessary-and-sufficient characterization of \((H_T,U_T)\) is established;
the exact boundary requires the causal purchase ledgers.

The complete proof, exact affine trichotomy, strict regions, counterexamples,
and boundary cases are recorded in the
[evidence note](../notes/arbitrary-horizon-performance-boundary.md). The
[independent review](../notes/arbitrary-horizon-research-package-review.md)
records a ledger-first re-derivation and witness-by-witness replay, and the
[boundary check](../../reproducibility/checks/check_arbitrary_horizon_performance_boundary.py)
and [independent publication replay](../../reproducibility/checks/check_arbitrary_horizon_publication_review.py)
are the executable publication gates.[^performance-note][^package-review]

[^performance-note]: [Exact arbitrary-horizon evaluation-price boundary for guarded SmartDCA](../notes/arbitrary-horizon-performance-boundary.md)
[^ticket-04]: [Prove the arbitrary-horizon performance boundary](../../.scratch/smartdca/efforts/arbitrary-horizon-performance/issues/04-prove-arbitrary-horizon-performance-boundary.md)
[^cash-timing]: [Arbitrary-horizon terminal wealth has an exact cash-timing identity](arbitrary-horizon-cash-timing-identity.md)
[^cash-crossing]: [Reference-aligned guardrail feedback preserves cash single crossing](reference-aligned-guardrail-cash-single-crossing.md)
[^guardrail]: [Epsilon-DCA safety is exactly a causal unit-coverage guardrail](epsilon-dca-safety-unit-guardrail.md)
[^package-review]: [Independent review of the arbitrary-horizon research package](../notes/arbitrary-horizon-research-package-review.md)
