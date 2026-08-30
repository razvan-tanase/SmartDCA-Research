# The guarded corrected-mean SmartDCA rule

This page defines the implementable strategy: a mandatory safety floor that
does the guaranteeing, and a bounded causal score that spends only what the
floor leaves free. The floor supplies the guarantee; the score supplies the
corrected-mean adaptation.

## Setting

The comparison model — causal decisions, long-only buy-only purchases, full funding from
exogenous deposits, cash carried without interest, and terminal wealth including cash — is
inherited from [the causal DCA dominance impossibility](../theorems/causal-dca-dominance-impossibility.md).
Only the observables this rule reads are named below.

Fix a safety factor \(\lambda=1-\varepsilon\in(0,1]\). At purchase date \(t\) the positive prices \(p_1,\ldots,p_t\), the nonnegative deposits \(d_1,\ldots,d_t\), the carried cash \(C_{t-1}\), the strategy's units \(Q_{t-1}\), and DCA's units \(Q_{t-1}^{DCA}\) are observed. Write \(K_{t-1}=Q_{t-1}-\lambda Q_{t-1}^{DCA}\) for the unit-coverage cushion, and \(B_t=C_{t-1}+d_t\) for available cash. The portfolio starts empty, so \(K_0=0\).

## The rule

**Floor.** The purchase must be at least

\[
m_t=\bigl[\lambda d_t-p_t K_{t-1}\bigr]_+ ,
\]

which [the guardrail theorem](../theorems/epsilon-dca-safety-unit-guardrail.md) proves is exactly the sharp causal requirement for universal \(\lambda\)-DCA safety and is always feasible.[^guardrail]

**Reference.** Anchor prices at the first observed price, \(z_i=p_i/p_1\). For \(t\ge2\) form the lagged, equally weighted, dimensionless reference from [the corrected out quasi-Gini mean](corrected-out-quasi-gini-mean.md),

\[
R_{t-1}=\widehat G_{\alpha,\beta}^{f,\mathrm{out}}(z_1,\ldots,z_{t-1};1,\ldots,1),
\qquad
r_t=\frac{z_t}{R_{t-1}},
\]

using the diagonal extension when \(\alpha=\beta\). At the first date set \(r_1=1\); that is the only warm-up convention.[^guarded-score]

**Score and purchase.** Normalize the source-style raw score at the neutral relative price and equate its odds to the discretionary fraction:

\[
a_t=\frac{1}{1+\bigl(f(r_t)/f(1)\bigr)^{1-\alpha}},
\qquad
x_t=m_t+a_t\,(B_t-m_t).
\]

Equivalently \(\operatorname{logit}(a_t)=(\alpha-1)\bigl(\log f(r_t)-\log f(1)\bigr)\), so \(\alpha-1=\rho\) keeps the source's score parameter meaning.[^ticket-10]

## Properties that are part of the choice

The rule is causal, uses no future price, no full-sample extremum, and no ex-post budget normalization. The score is strictly interior, \(0<a_t<1\), and equals \(1/2\) on a one-point or constant history. Lagging the reference and anchoring at \(p_1\) make the rule invariant to a common currency rescaling *even where the corrected mean is not homogeneous*, and keep the current price out of its own benchmark. Equal weights are canonical because they add no recency or horizon hyperparameter. With \(f\) nondecreasing and \(\alpha\le1\) both the score and the purchase are nonincreasing in the current price, which is the countercyclical behaviour the rule is for.[^guarded-score]

The accounting is exact: \(C_t=D_t-S_t\), \(Q_t=\sum_{j\le t}x_j/p_j\), the cushion recursion keeps \(K_t\ge0\), the terminal identity is \(W_t^S-\lambda W_t^{DCA}=C_t+PK_t\ge0\), and the average acquisition cost is the spending-weighted harmonic price \(S_t/Q_t\).[^guarded-score]

## What this definition does not claim

No universal or stochastic improvement on DCA. The rule's guarantee is the
\(\lambda\) floor and nothing stronger. Its exact realized wealth sign is
characterized only at [two purchases](../theorems/two-purchase-guarded-smartdca-boundary.md)
and [three purchases](../theorems/three-purchase-corrected-mean-effect.md):
both strict-win and strict-loss regions occur, and the three-purchase result
shows by exact witness that changing \(\beta\) can flip the DCA
classification while the first two actions stay fixed. Neither theorem makes
an arbitrary-horizon or stochastic claim. At \(\lambda=1\) the discretionary
interval collapses along every reachable history and the rule *is* DCA
regardless of the score, which is the impossibility boundary showing
through.[^guardrail]

Average acquisition cost below DCA's does not establish greater terminal wealth when spending differs — the exact gap the source paper's criterion leaves open. For \(\alpha>1\) the score is a momentum rule and the countercyclical claim is invalid; at \(\alpha=1\) the score is constant at \(1/2\) and only the floor responds to price. Response to changes in *lagged* prices needs comparative statics of the corrected mean that are not claimed for a general increasing transform.[^guarded-score]

[^ticket-10]: [Choose the guarded corrected-mean SmartDCA score](../../.scratch/smartdca/issues/10-choose-guarded-corrected-mean-score.md)
[^guarded-score]: [A guarded corrected-mean SmartDCA rule](../notes/guarded-corrected-mean-smartdca.md)
[^guardrail]: [Sharp causal epsilon-DCA safety and its unit-coverage guardrail](../notes/sharp-epsilon-dca-safety-guardrail.md)
