# Choose the guarded corrected-mean SmartDCA score

Type: task
Status: resolved
Blocked by: 05, 09
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

Using the canonical corrected out quasi-Gini mean from ticket 05 and the exact
safe-policy parameterization from ticket 09,

\[
x_t=m_t+a_t(C_{t-1}+d_t-m_t),
\qquad a_t\in[0,1],
\]

choose and justify a canonical causal map from observed price history and the
corrected-mean statistic to the bounded score \(a_t\). The rule must avoid
future prices and ex-post normalization, remain well-defined on constant and
short histories, preserve the established Gini and out quasi-Lehmer special
cases where meaningful, and state the parameter/transform conditions needed
for boundedness and monotone price response. Derive its exact cash, unit, and
average-acquisition-cost accounting, but do not yet claim strict outperformance
outside a separately proved path or stochastic criterion.

## Comments

- Opened after ticket 09 made the safe discretionary interface exact.
- Claimed after the user explicitly continued to ticket 10 on 2026-08-15.
- Independent Standards and Spec reviews re-derived the construction and accounting, exposed five boundary/verification issues, and confirmed that all were resolved. The final verifier passed after the fixes.

## Answer

Use the first observed price as a fixed causal anchor, normalize the lagged
history by it, and let

\[
R_{t-1}=\widehat G_{\alpha,\beta}^{f,\mathrm{out}}
  (p_1/p_1,\ldots,p_{t-1}/p_1),
\qquad
r_t=\frac{p_t/p_1}{R_{t-1}}
\]

for \(t\ge2\), with \(r_1=1\). The canonical bounded score sets its odds
equal to the normalized source-style score:

\[
\boxed{
a_t
=\frac{1}{1+\left(f(r_t)/f(1)\right)^{1-\alpha}}.
}
\]

This rule is causal, currency-scale invariant even for a nonhomogeneous
transform, neutral at \(1/2\) on one-point and constant histories, and strictly
inside \((0,1)\) for every positive finite transform. If \(f\) is
nondecreasing and \(\alpha\le1\), both \(a_t\) and the guarded purchase are
nonincreasing in the current price holding the past and state fixed; the score
response is strict for strictly increasing \(f\) and \(\alpha<1\). No
restriction on \(\beta\) is needed for this current-price comparative static.

For \(f=\mathrm{id}\), the reference is the weighted classical Gini mean and
\(a_t=(1+r_t^{1-\alpha})^{-1}\). For
\(\alpha-\beta=1\), the reference is exactly the weighted out quasi-Lehmer
mean and the raw odds retain \(\rho=\alpha-1\). Equal lagged weights are the
canonical no-extra-parameter choice.

The complete proof and cash, unit, coverage, terminal-wealth, and average-cost
identities are in [A guarded corrected-mean SmartDCA rule](../../../research/notes/guarded-corrected-mean-smartdca.md).
The [verification script](../../../reproducibility/checks/check_guarded_corrected_mean_smartdca.py) passed the
special-case, constant/short-history, scale, causal-prefix, boundedness,
monotonicity, and integration checks, plus exact rational accounting on 59,049
guarded paths and 177,147 terminal valuations.

Because \(a_t\in[0,1]\), ticket 09 supplies the universal
\(\lambda=1-\varepsilon\) DCA floor. The result does **not** assert strict
outperformance over DCA; that requires a separately proved path or stochastic
criterion.
