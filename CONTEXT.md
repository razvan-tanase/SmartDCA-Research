# Quasi-Gini SmartDCA Research

This context develops a rigorous out quasi-Gini mean and studies whether it can generate a causal, fully funded SmartDCA strategy with exact accounting and a fair comparison against DCA.

## Language

**Out quasi-Gini functional**[^classification][^audit]:
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

**Corrected out quasi-Gini mean**[^corrected-definition][^prior-theory]:
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

**Scale-homogeneous corrected subfamily**[^homogeneity-theorem][^homogeneity]:
At fixed off-diagonal parameters, the corrected mean is degree-one homogeneous exactly when \(\alpha=1\) (where the transform cancels) or \(f(t)=Ct^r\) under the project's increasing-transform assumption; on the diagonal, \(q=1\) is the analogous exception. One transform makes the whole two-parameter family homogeneous exactly in the power-transform case, which is a reparameterized classical weighted Gini family.
_Avoid_: homogeneity for a general increasing transform, transform novelty on the \(\alpha=q=1\) slice

**Weighted Bajraktarević identification**[^prior-theory]:
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

**Sequentially admissible strategy**[^impossibility][^causal-boundary]:
A strategy whose purchase at time \(t\) depends only on deposits, prices, and portfolio state observed through time \(t\), after observing the current price and before observing any future price.
_Avoid_: future-aware strategy, ex-post normalized strategy

**Deposit budget**[^impossibility][^causal-boundary]:
Cash contributed through an exogenous deposit sequence; unused cash carries forward without interest, and purchases cannot exceed cash currently available.
_Avoid_: leverage, borrowing capacity

**DCA comparator**[^impossibility][^causal-boundary]:
The strategy that invests the entire new deposit at each purchase time at the current price, using the same deposit sequence and evaluation horizon as the candidate strategy.
_Avoid_: retrospectively budget-matched DCA

**Economic dominance**[^impossibility]:
Terminal wealth is at least that of the DCA comparator for every admissible positive price path and deposit sequence, and strictly greater for at least one admissible case.
_Avoid_: lower average cost alone

**Causal DCA impossibility boundary**[^impossibility][^causal-boundary]:
Under arbitrary finite positive price paths, the same exogenous deposits, and terminal wealth including cash, a causal fully funded buy-only strategy weakly dominates DCA only if it purchases each deposit exactly as DCA. A nontrivial positive result must restrict the path universe, relax causality, or weaken the performance criterion.
_Avoid_: DCA is optimal on each realized path, no strategy can ever beat DCA

**Epsilon-DCA safety**[^guardrail-theorem][^guardrail]:
For a fixed \(\varepsilon\in[0,1)\), terminal wealth including cash satisfies \(W^S\ge(1-\varepsilon)W^{DCA}\) for every admissible positive price path and deposit sequence. It is a uniform relative-wealth floor; it is not economic dominance when \(\varepsilon>0\).
_Avoid_: epsilon-dominance, near-superiority, guaranteed outperformance

**Epsilon-DCA unit guardrail**[^guardrail-theorem][^guardrail]:
With \(\lambda=1-\varepsilon\), the unit-coverage cushion \(Q_t^S-\lambda Q_t^{DCA}\) must remain nonnegative after every history; equivalently, each purchase must meet the sharp causal floor \([\lambda d_t-p_t(Q_{t-1}^S-\lambda Q_{t-1}^{DCA})]_+\). Purchases above that floor are the funded discretionary allocation.
_Avoid_: cash cushion, dominance budget, optional safety check

**Guarded corrected-mean score**[^guarded-rule]:
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

**Two-purchase DCA boundary**[^two-purchase-boundary][^two-purchase-boundary-note]:
For the exact guarded rule, write \(q=p_2/p_1\), \(y=P/p_2\),
\(\delta=(1-\lambda)/2\),
\[
H=\delta d_1+d_2-[\lambda d_2-\delta d_1q]_+,\qquad
c=(1-a_2)H,\qquad g=\delta d_1(1-q).
\]
Then \(W_2^S-W_2^{DCA}=c-y(c-g)\). For
\(0<\lambda<1\) and a nonzero deposit pair, the rule wins below
\(c/(c-g)\), ties there, and loses above it when \(c-g>0\); if
\(c-g\le0\), every positive finite \(y\) is a win. At \(\lambda=1\) every
case ties. The singleton lagged reference makes \(\beta\) irrelevant at two
purchases.
_Avoid_: win probability, arbitrary-horizon boundary, evidence that
\(\beta\) improves the rule

**Three-purchase beta-sensitive DCA boundary**[^three-purchase-effect][^three-purchase-effect-note]:
For exactly three purchases, let \(b_\beta=a_3\) be the score formed from
the first two-input lagged reference, let \(H_3\) be the date-three
discretionary interval, and set
\[
c_\beta=(1-b_\beta)H_3,\qquad
g=\delta d_1\frac{p_3}{p_2}
  \left(1-\frac{p_2}{p_1}\right)
  +C_2\left(1-\frac{p_3}{p_2}\right),\qquad
y=\frac{P}{p_3}.
\]
Then \(W_3^S-W_3^{DCA}=c_\beta-y(c_\beta-g)\), giving the exact extended
threshold \(c_\beta/(c_\beta-g)\) when its denominator is positive and an
all-win slice otherwise. Changing \(\beta\) leaves the first two purchases
fixed but can change this threshold: an exact countercyclical witness flips
from a DCA loss at \(\beta=-1\) to a win at \(\beta=1\).
_Avoid_: beta superiority, monotone benefit from increasing beta,
arbitrary-horizon boundary, stochastic outperformance

**Arbitrary-horizon cash-timing identity**[^cash-timing-identity][^cash-timing-note]:
The exact decomposition of a fully funded strategy's terminal wealth into DCA
wealth plus coefficients on its carried-cash path; subtracting two such paths
gives the corresponding two-strategy identity at every finite horizon.
_Avoid_: score-specific performance formula, stochastic attribution,
cash-timing advantage

**Corrected-neutral cash single crossing**[^cash-crossing-theorem][^cash-crossing-note]:
After zeros are deleted, corrected-minus-neutral carried cash has a block of
minus signs followed by a block of plus signs, with either block possibly
empty. On a weak single-valley path the corrected score has this direction,
but the guarded cash path need not: policy-specific clipped floors can create
a second reversal. A sufficient observable condition is **reference-aligned
guardrail feedback**: at one score-crossing boundary, the
corrected-minus-neutral clipped-floor difference is nonnegative before the
boundary and nonpositive after it. Equal clipped floors are a special case,
but the condition is not necessary because same-period score forcing can
outweigh a misaligned floor component.
_Avoid_: cash single crossing on every weak or strict single-valley path,
attributing a cash reversal to the score when floor amounts diverge,
terminal-wealth advantage from cash signs alone

**Arbitrary-horizon terminal-inventory boundary**[^performance-boundary-theorem][^performance-boundary-note]:
For either DCA or the neutral guarded selector \(T\), let
\(H_T=C_n^c-C_n^T\) and \(U_T=Q_n^c-Q_n^T\) be the terminal corrected-minus-
comparator cash and unit differences fixed by the causal purchase ledgers.
Then \(W_n^c(P)-W_n^T(P)=H_T+P U_T\) for every positive evaluation price, so
the signs of \((H_T,U_T)\) and their positive root, when one exists, give the
exact necessary-and-sufficient win/tie/loss classification at every finite
horizon. The cash-timing identity independently reconstructs \(U_T\). On a
weak single-valley path evaluated at \(P=p_n\), this becomes the exact balance
between signed reciprocal-price exposure on the decline and recovery.
Reference-aligned cash single crossing does not determine that balance.
_Avoid_: cash signs imply wealth order, corrected-score safety guarantee,
universal or stochastic outperformance, price-only boundary

**Terminal wealth**[^impossibility][^causal-boundary]:
Unspent cash plus the value of accumulated asset units at the common evaluation price.
_Avoid_: asset value with cash omitted

**Average acquisition cost**[^guarded-rule][^guarded-score]:
Total cash spent on the asset divided by total asset units acquired. It is a structural accounting quantity, not by itself a budget-equivalent performance measure.
_Avoid_: proof of economic superiority

## Sources

Each term above cites its governing definition or theorem and the evidence note
that carries the proof, counterexamples, or primary sources. The four model
terms—sequential admissibility, the deposit budget, the DCA comparator, and
terminal wealth—share one theorem because they describe one comparison model.

[^audit]: [Audit of the source out quasi-Gini functional](research/notes/source-out-quasi-gini-audit.md)
[^prior-theory]: [Prior theory for the proposed corrected out quasi-Gini normalization](research/notes/prior-theory-corrected-out-quasi-gini.md)
[^causal-boundary]: [Pathwise DCA dominance under causal budget feasibility](research/notes/pathwise-dca-dominance-under-causal-budget.md)
[^guarded-score]: [A guarded corrected-mean SmartDCA rule](research/notes/guarded-corrected-mean-smartdca.md)
[^corrected-definition]: [The corrected out quasi-Gini mean](research/definitions/corrected-out-quasi-gini-mean.md)
[^guarded-rule]: [The guarded corrected-mean SmartDCA rule](research/definitions/guarded-corrected-mean-smartdca-rule.md)
[^classification]: [Exact mean classification of the source out quasi-Gini functional](research/theorems/source-out-functional-mean-classification.md)
[^homogeneity-theorem]: [Homogeneity characterization of the corrected out quasi-Gini mean](research/theorems/corrected-mean-homogeneity-characterization.md)
[^impossibility]: [Causal DCA dominance impossibility](research/theorems/causal-dca-dominance-impossibility.md)
[^guardrail-theorem]: [Epsilon-DCA safety is exactly a causal unit-coverage guardrail](research/theorems/epsilon-dca-safety-unit-guardrail.md)
[^two-purchase-boundary]: [Two-purchase guarded SmartDCA has an exact DCA boundary](research/theorems/two-purchase-guarded-smartdca-boundary.md)
[^two-purchase-boundary-note]: [Exact two-purchase DCA win/loss boundary](research/notes/two-purchase-dca-win-loss-boundary.md)
[^three-purchase-effect]: [Three-purchase guarded SmartDCA has an exact beta-sensitive DCA boundary](research/theorems/three-purchase-corrected-mean-effect.md)
[^three-purchase-effect-note]: [Exact three-purchase corrected-mean effect](research/notes/three-purchase-corrected-mean-effect.md)
[^cash-timing-identity]: [Arbitrary-horizon terminal wealth has an exact cash-timing identity](research/theorems/arbitrary-horizon-cash-timing-identity.md)
[^cash-timing-note]: [Arbitrary-horizon cash-timing identity and exact-rational verification seam](research/notes/arbitrary-horizon-accounting-verification-seam.md)
[^cash-crossing-theorem]: [Reference-aligned guardrail feedback preserves cash single crossing](research/theorems/reference-aligned-guardrail-cash-single-crossing.md)
[^cash-crossing-note]: [Differential guardrail feedback defeats cash single crossing](research/notes/cash-single-crossing-mechanism.md)
[^performance-boundary-theorem]: [Terminal cash and units give the exact arbitrary-horizon performance boundary](research/theorems/arbitrary-horizon-performance-boundary.md)
[^performance-boundary-note]: [Exact arbitrary-horizon evaluation-price boundary for guarded SmartDCA](research/notes/arbitrary-horizon-performance-boundary.md)
[^homogeneity]: [Primary-source note on homogeneity of the canonical corrected mean](research/notes/ticket-07-homogeneity-primary-sources.md)
[^guardrail]: [Sharp causal epsilon-DCA safety and its unit-coverage guardrail](research/notes/sharp-epsilon-dca-safety-guardrail.md)
