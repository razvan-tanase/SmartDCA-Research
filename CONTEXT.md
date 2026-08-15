# Quasi-Gini SmartDCA Research

This context develops a rigorous out quasi-Gini mean and studies whether it can generate a causal, fully funded SmartDCA strategy with exact accounting and a fair comparison against DCA.

## Language

**Out quasi-Gini functional**:
The source-paper construction
\[
G^{f,\mathrm{out}}_{\alpha,\beta}(x)=
\left(
\frac{\sum_i x_i f(x_i)^{\alpha-1}}
     {\sum_i f(x_i)^\beta}
\right)^{1/(\alpha-\beta)},
\qquad \alpha\ne\beta,
\]
with \(\alpha=\rho+1\) and \(\beta=\gamma\). It is called a functional until its mean properties are established.
_Avoid_: Gini coefficient, out quasi-Gini mean when referring to the unverified source definition

**Corrected out quasi-Gini mean**:
The canonical numerator-preserving normalization
\[
\widehat G_{\alpha,\beta}^{f,\mathrm{out}}(x;w)
=\left(
\frac{\sum_i w_i x_i f(x_i)^{\alpha-1}}
     {\sum_i w_i x_i^{1-\alpha+\beta}f(x_i)^{\alpha-1}}
\right)^{1/(\alpha-\beta)}
\]
off the diagonal, with the parameter-continuous function-weighted geometric extension on
\(\alpha=\beta\). It is a weighted Bajraktarević mean, recovers weighted Gini
for \(f=\mathrm{id}\), and recovers the weighted source out quasi-Lehmer mean
when \(\alpha-\beta=1\).
_Avoid_: new mean class, repaired Eq. (70) without stating the normalization, automatic continuity/homogeneity/coordinate monotonicity

**Scale-homogeneous corrected subfamily**:
At fixed off-diagonal parameters, the corrected mean is degree-one homogeneous exactly when \(\alpha=1\) (where the transform cancels) or \(f(t)=Ct^r\) under the project's increasing-transform assumption; on the diagonal, \(q=1\) is the analogous exception. One transform makes the whole two-parameter family homogeneous exactly in the power-transform case, which is a reparameterized classical weighted Gini family.
_Avoid_: homogeneity for a general increasing transform, transform novelty on the \(\alpha=q=1\) slice

**Weighted Bajraktarević identification**:
For \(d=\alpha-\beta\ne0\), the natural common-weight candidate
\[
\left(
\frac{\sum_i w_i x_i f(x_i)^{\alpha-1}}
     {\sum_i w_i x_i^{1-d}f(x_i)^{\alpha-1}}
\right)^{1/d}
\]
is exactly the weighted Bajraktarević mean
\(A_{t^{-d},\,t f(t)^{\alpha-1}}\). Its \(d=1\) slice is
Beckenbach--Gini--Lehmer/out quasi-Lehmer, and power transforms reduce to
classical weighted Gini means.
_Avoid_: new class of means, or Beckenbach--Gini as a name for the full family

**Sequentially admissible strategy**:
A strategy whose purchase at time \(t\) depends only on deposits, prices, and portfolio state observed through time \(t\), after observing the current price and before observing any future price.
_Avoid_: future-aware strategy, ex-post normalized strategy

**Deposit budget**:
Cash contributed through an exogenous deposit sequence; unused cash carries forward without interest, and purchases cannot exceed cash currently available.
_Avoid_: leverage, borrowing capacity

**DCA comparator**:
The strategy that invests the entire new deposit at each purchase time at the current price, using the same deposit sequence and evaluation horizon as the candidate strategy.
_Avoid_: retrospectively budget-matched DCA

**Economic dominance**:
Terminal wealth is at least that of the DCA comparator for every admissible positive price path and deposit sequence, and strictly greater for at least one admissible case.
_Avoid_: lower average cost alone

**Causal DCA impossibility boundary**:
Under arbitrary finite positive price paths, the same exogenous deposits, and terminal wealth including cash, a causal fully funded buy-only strategy weakly dominates DCA only if it purchases each deposit exactly as DCA. A nontrivial positive result must restrict the path universe, relax causality, or weaken the performance criterion.
_Avoid_: DCA is optimal on each realized path, no strategy can ever beat DCA

**Epsilon-DCA safety**:
For a fixed \(\varepsilon\in[0,1)\), terminal wealth including cash satisfies \(W^S\ge(1-\varepsilon)W^{DCA}\) for every admissible positive price path and deposit sequence. It is a uniform relative-wealth floor; it is not economic dominance when \(\varepsilon>0\).
_Avoid_: epsilon-dominance, near-superiority, guaranteed outperformance

**Epsilon-DCA unit guardrail**:
With \(\lambda=1-\varepsilon\), the unit-coverage cushion \(Q_t^S-\lambda Q_t^{DCA}\) must remain nonnegative after every history; equivalently, each purchase must meet the sharp causal floor \([\lambda d_t-p_t(Q_{t-1}^S-\lambda Q_{t-1}^{DCA})]_+\). Purchases above that floor are the funded discretionary allocation.
_Avoid_: cash cushion, dominance budget, optional safety check

**Guarded corrected-mean score**:
The canonical discretionary score anchors prices at \(p_1\), forms the lagged
dimensionless corrected-mean reference
\(R_{t-1}=\widehat G(p_1/p_1,\ldots,p_{t-1}/p_1)\), sets
\(r_t=(p_t/p_1)/R_{t-1}\), and uses
\[
a_t=\frac{1}{1+(f(r_t)/f(1))^{1-\alpha}}.
\]
It is a causal odds calibration inside the epsilon-DCA guardrail, neutral on
one-point and constant histories, and countercyclical in the current price when
\(f\) is nondecreasing and \(\alpha\le1\).
_Avoid_: ex-post normalization, an unnormalized nonhomogeneous price-level
reference, strict DCA outperformance without a proved criterion

**Terminal wealth**:
Unspent cash plus the value of accumulated asset units at the common evaluation price.
_Avoid_: asset value with cash omitted

**Average acquisition cost**:
Total cash spent on the asset divided by total asset units acquired. It is a structural accounting quantity, not by itself a budget-equivalent performance measure.
_Avoid_: proof of economic superiority
