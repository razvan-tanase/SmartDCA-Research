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
