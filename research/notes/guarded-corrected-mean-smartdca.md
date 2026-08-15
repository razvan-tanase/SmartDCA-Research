# A guarded corrected-mean SmartDCA rule

## 1. Setting

Fix a safety factor \(\lambda=1-\varepsilon\in(0,1]\). At purchase date
\(t\), the positive prices \(p_1,\ldots,p_t\), nonnegative deposits
\(d_1,\ldots,d_t\), and the portfolio state through \(t-1\) are known. Let
\(C_{t-1}\) be carried cash, \(Q_{t-1}\) the strategy's units, and
\(Q_{t-1}^{DCA}\) DCA's units. Write

\[
K_{t-1}=Q_{t-1}-\lambda Q_{t-1}^{DCA}\ge0
\]

for the unit-coverage cushion. Ticket 09 proves that the exact safe purchase
interval is

\[
m_t=\left[\lambda d_t-p_tK_{t-1}\right]_+,
\qquad
x_t=m_t+a_t(C_{t-1}+d_t-m_t),
\qquad a_t\in[0,1].
\tag{1}
\]

Both strategies start from the zero portfolio:
\(C_0=Q_0=Q_0^{DCA}=0\), hence \(K_0=0\).

The remaining question is how to choose \(a_t\) causally from the corrected
out quasi-Gini statistic.

## 2. Lagged dimensionless reference

Let \(f:(0,\infty)\to(0,\infty)\) be the same positive transform used by the
corrected mean, and fix real \((\alpha,\beta)\). The canonical rule uses equal
weights and the first observed price as a predeclared anchor. Put

\[
z_i=\frac{p_i}{p_1}.
\]

For \(t\ge2\), calculate the lagged reference

\[
R_{t-1}
=\widehat G_{\alpha,\beta}^{f,\mathrm{out}}
  (z_1,\ldots,z_{t-1};1,\ldots,1)
\tag{2}
\]

using the numerator-preserving definition from ticket 05, including its
function-weighted geometric extension when \(\alpha=\beta\). Define the
current relative price by

\[
r_t=\frac{z_t}{R_{t-1}}.
\tag{3}
\]

At the first date set \(r_1=1\). This is the only warm-up convention needed.

The normalization has three purposes. First, the inputs to \(f\) are
dimensionless. Second, multiplying every price by the same positive currency
conversion leaves every \(z_i\), hence the entire rule, unchanged even when
the corrected mean is not homogeneous. Third, the reference excludes the
current price. Thus, holding the past fixed, changing \(p_t\) changes \(r_t\)
but not its own benchmark. An unnormalized price-level reference would require
the homogeneity conditions from ticket 07; a current-inclusive reference would
also inherit the corrected mean's generally unresolved coordinatewise
monotonicity.

Equal weights are canonical because they introduce no recency or horizon
hyperparameter. The results also hold for strictly positive weights that are
predeclared by index or determined solely from the lagged dimensionless
history. Weights depending on the current or a future price are excluded;
arbitrary price-level-dependent weights could also destroy currency-scale
invariance. Any non-equal weighting is an additional modeling choice.

## 3. Canonical bounded score

Normalize the source-style raw score at the neutral relative price:

\[
s_t
=\left(\frac{f(r_t)}{f(1)}\right)^{\alpha-1}>0.
\tag{4}
\]

Choose the discretionary fraction by equating its odds to this score:

\[
\boxed{
\frac{a_t}{1-a_t}=s_t,
\qquad
a_t=\frac{s_t}{1+s_t}
=\frac{1}{1+\left(f(r_t)/f(1)\right)^{1-\alpha}}.
}
\tag{5}
\]

This odds calibration is the parameter-free bounded map selected for the
paper. It preserves the ordering of the raw score, maps the neutral score to
\(1/2\), obeys \(a(1/s)=1-a(s)\), and avoids clipping or any sample-dependent
normalization. Equivalently,

\[
\operatorname{logit}(a_t)
=(\alpha-1)\bigl(\log f(r_t)-\log f(1)\bigr),
\]

so \(\alpha-1=\rho\) retains the source score's parameter meaning.

The complete guarded rule is (1) with (2)--(5).

## 4. Well-definedness and comparative statics

### Proposition 1 (causality, boundedness, and edge cases)

Suppose prices are positive, deposits are nonnegative, \(f\) is positive and
finite on \((0,\infty)\), and the corrected mean uses positive weights. For
all real \((\alpha,\beta)\), using the diagonal extension when
\(\alpha=\beta\), the rule is causal and

\[
0<a_t<1.
\]

If \(t=1\), then \(a_1=1/2\). If the observed prices through \(t\) are
constant, then \(R_{t-1}=1\), \(r_t=1\), and \(a_t=1/2\). No future price,
full-sample extremum, or ex-post budget normalization appears.

**Proof.** The corrected mean is positive and internal on positive inputs, so
\(R_{t-1}\), \(r_t\), and \(s_t\) are positive and finite. Equation (5) then
lies strictly between zero and one. All inputs at date \(t\) are prefix
measurable. Reflexivity of the corrected mean gives the constant-history
claim. The first-date convention gives the short-history claim. \(\square\)

### Proposition 2 (monotone current-price response)

Hold the past, deposit, and portfolio state fixed. If \(f\) is nondecreasing
and \(\alpha\le1\), then both \(a_t\) and the actual purchase \(x_t\) are
nonincreasing functions of the current price \(p_t\). The score response is
strict when \(f\) is strictly increasing and \(\alpha<1\).

**Proof.** The lagged reference is fixed, so \(r_t\) increases with \(p_t\).
For \(\alpha\le1\), equation (5) is nonincreasing in \(f(r_t)\). Also

\[
m_t(p)=\left[\lambda d_t-pK_{t-1}\right]_+
\]

is nonincreasing in \(p\). With \(B_t=C_{t-1}+d_t\), the function
\(g(a,m)=m+a(B_t-m)\) is nondecreasing in each argument on
\([0,1]\times[0,B_t]\). Indeed, along a covered history,
\(m_t\le\lambda d_t\le d_t\le B_t\). Hence
\(x_t=g(a_t,m_t)\) is nonincreasing. Strictness of \(a_t\) follows directly
under the stated stronger conditions. \(\square\)

For \(\alpha=1\), \(a_t=1/2\) and only the guardrail responds to price. For
\(\alpha>1\), (5) is a momentum score and no general countercyclical purchase
claim is valid. Continuity of the response follows if \(f\) is continuous.
Changes in lagged prices require comparative statics of the corrected mean;
those are not claimed for a general increasing transform.

## 5. Compatibility identities

The score preserves the two established special cases through its reference.

1. **Weighted Gini case.** If \(f(u)=u\), then (2) is the classical weighted
   Gini mean \(G_{\alpha,\beta}\) of the normalized lagged history, and
   \[
   a_t=\frac{1}{1+r_t^{1-\alpha}}.
   \tag{6}
   \]
2. **Out quasi-Lehmer case.** If \(\alpha-\beta=1\), then (2) is exactly the
   corrected/source weighted out quasi-Lehmer mean
   \[
   R_{t-1}
   =\frac{\sum_{i<t}z_i f(z_i)^{\alpha-1}}
          {\sum_{i<t}f(z_i)^{\alpha-1}},
   \tag{7}
   \]
   while (4) retains the normalized source score with
   \(\rho=\alpha-1\).

These are identity preservations, not claims that the bounded odds map itself
appears in the source paper.

## 6. Exact accounting

Let

\[
B_t=C_{t-1}+d_t,
\qquad
D_t=\sum_{j=1}^t d_j,
\qquad
S_t=\sum_{j=1}^t x_j.
\]

For the guarded score rule,

\[
\boxed{C_t=B_t-x_t=(1-a_t)(B_t-m_t)}
\tag{8}
\]

and, from the stated zero initial portfolio,

\[
\boxed{C_t=D_t-S_t.}
\tag{9}
\]

Asset units obey

\[
\boxed{
Q_t=Q_{t-1}+\frac{x_t}{p_t}
=\sum_{j=1}^t\frac{x_j}{p_j},
\qquad
Q_t^{DCA}=\sum_{j=1}^t\frac{d_j}{p_j}.
}
\tag{10}
\]

The coverage cushion has the exact recursion

\[
K_t
=K_{t-1}+\frac{x_t-\lambda d_t}{p_t}
=\left[K_{t-1}-\frac{\lambda d_t}{p_t}\right]_+
 +\frac{a_t(B_t-m_t)}{p_t}\ge0.
\tag{11}
\]

Thus (5) is only a selector inside the complete safe interval; boundedness of
\(a_t\) and ticket 09's theorem imply the universal epsilon-DCA floor.

For a positive evaluation price \(P\), terminal wealth satisfies

\[
W_t^S=C_t+PQ_t,
\qquad
W_t^{DCA}=PQ_t^{DCA},
\]

and therefore

\[
\boxed{W_t^S-\lambda W_t^{DCA}=C_t+PK_t\ge0.}
\tag{12}
\]

Whenever \(Q_t>0\), the average acquisition cost is exactly

\[
\boxed{
\bar p_t^S
=\frac{S_t}{Q_t}
=\frac{D_t-C_t}{Q_t}
=\frac{\sum_{j\le t}x_j}{\sum_{j\le t}x_j/p_j}.
}
\tag{13}
\]

It is undefined when no units have been bought. Equation (13) is a
spending-weighted harmonic price identity. It is not generally equal to the
corrected mean, and being below DCA's average acquisition cost does not prove
greater terminal wealth when spending differs.

## 7. Boundary example and scope

At \(t=1\), \(m_1=\lambda d_1\), so the neutral convention invests
\((1+\lambda)d_1/2\). At \(\lambda=1\), ticket 09 forces the discretionary
interval to collapse along every reachable history and the rule is DCA,
regardless of the score. For \(0<\lambda<1\), the interval is generally
nontrivial and (5) supplies a causal corrected-mean allocation inside it.

The companion script checks the compatibility identities, constant and short
histories, currency-scale and causal-prefix invariance, boundedness, monotone
current-price response, exact accounting, and the epsilon-DCA terminal floor.
It evaluates the formulas in log space. Because an off-diagonal quotient with
\(|\alpha-\beta|\) extremely close to zero is ill-conditioned in binary64, the
verifier dispatches to the diagonal only when \(\alpha=\beta\) exactly and
rejects nonzero gaps below \(10^{-10}\) with an instruction to use arbitrary
precision. This is a numerical restriction of the verifier, not a restriction
of the mathematical rule.

No strict outperformance claim is made here. Relative to DCA itself, the
accounting identity is

\[
W_t^S-W_t^{DCA}=C_t+P(Q_t-Q_t^{DCA})
\]

but no sign is asserted for it in this ticket. A later ticket must state and
prove a favorable path class, stochastic estimand, or utility criterion before
calling this rule an improvement.
