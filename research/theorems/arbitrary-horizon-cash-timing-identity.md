---
profile: smartdca-okf/0.4
type: theorem
title: "Arbitrary-horizon terminal wealth has an exact cash-timing identity"
description: "Every fully funded finite-horizon strategy's terminal wealth is DCA wealth plus an exact functional of its carried-cash path."
knowledge_role: canonical
status: stable
sources:
  - id: accounting-note
    title: "Arbitrary-horizon cash-timing identity and exact-rational verification seam"
    resource: research/notes/arbitrary-horizon-accounting-verification-seam
    source_kind: internal
  - id: ticket-01
    title: "Establish the arbitrary-horizon accounting and verification seam"
    resource: .scratch/smartdca/efforts/arbitrary-horizon-performance/issues/01-establish-accounting-verification-seam
    source_kind: internal
  - id: comparison-model
    title: "Causal DCA dominance impossibility"
    resource: research/theorems/causal-dca-dominance-impossibility
    source_kind: internal
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-23T22:31:24Z
generation_run: urn:uuid:62ed4e2a-e3aa-4fb9-933c-8335a647cadc
verified:
  - by: openai-codex/spec-review-0.1
    at: 2026-08-23T22:36:39Z
    review_run: urn:uuid:7d7be1a1-3482-44ae-be16-e07cd8bc3010
---
# Arbitrary-horizon terminal wealth has an exact cash-timing identity

## Statement

Use the project's common-deposit comparison model: a finite horizon \(n\ge1\),
positive purchase prices \(p_1,\ldots,p_n\), nonnegative deposits
\(d_1,\ldots,d_n\), and a common positive evaluation price \(P\). For any
fully funded strategy \(S\), let \(C_t^S\) be its carried cash after purchase
date \(t\), with \(C_0^S=0\). Then[^comparison-model][^accounting-note]

\[
\boxed{
W_n^S
=W_n^{DCA}
+C_n^S\left(1-\frac{P}{p_n}\right)
+P\sum_{t=1}^{n-1}C_t^S
\left(\frac1{p_{t+1}}-\frac1{p_t}\right).
}
\]

For any two fully funded strategies \(S\) and \(T\) using the same deposits,
write \(\Delta C_t=C_t^S-C_t^T\). Subtraction gives the exact two-strategy
form

\[
\boxed{
W_n^S-W_n^T
=\Delta C_n\left(1-\frac{P}{p_n}\right)
+P\sum_{t=1}^{n-1}\Delta C_t
\left(\frac1{p_{t+1}}-\frac1{p_t}\right).
}
\]

Both identities are necessary accounting equalities, not bounds and not
strategy-specific approximations. The proof and exact-rational independent
verification routes are in the [evidence note](../notes/arbitrary-horizon-accounting-verification-seam.md).[^ticket-01]

## Interpretation

Cash carried across a falling purchase-price step has a positive timing
coefficient; cash carried across a rising step has a negative one. Terminal
cash is favorable relative to buying at \(p_n\) when \(P<p_n\), neutral when
\(P=p_n\), and unfavorable when \(P>p_n\). The identity therefore isolates
where delayed investment helps or hurts without assigning a sign in advance.

## Scope limit

The result applies to every finite horizon in the declared model and does not
depend on the guarded corrected-mean rule. It does not prove DCA dominance,
SmartDCA outperformance, cash-path single crossing, or any stochastic claim.
Those require additional restrictions on the cash path or price path.

[^accounting-note]: [Arbitrary-horizon cash-timing identity and exact-rational verification seam](../notes/arbitrary-horizon-accounting-verification-seam.md)
[^ticket-01]: [Establish the arbitrary-horizon accounting and verification seam](../../.scratch/smartdca/efforts/arbitrary-horizon-performance/issues/01-establish-accounting-verification-seam.md)
[^comparison-model]: [Causal DCA dominance impossibility](causal-dca-dominance-impossibility.md)
