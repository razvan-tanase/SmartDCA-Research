# Sharp causal epsilon-DCA safety and its unit-coverage guardrail

## Scope and model

Fix a finite horizon with purchase dates \(t=1,\ldots,n\), where \(n\ge1\).
At date \(t\), an exogenous deposit \(d_t\ge0\) and price \(p_t>0\) are
observed. A deterministic causal strategy chooses a purchase \(x_t\) using only
the history through date \(t\), subject to

\[
0\le x_t\le C_{t-1}+d_t,
\qquad
C_t=C_{t-1}+d_t-x_t,
\qquad
Q_t=Q_{t-1}+\frac{x_t}{p_t},
\]

with \(C_0=Q_0=0\). Thus the strategy is long-only, buy-only, and funded only
by deposited cash; unused cash carries without interest. DCA spends \(d_t\)
immediately and therefore has

\[
A_t:=Q_t^{DCA}=\sum_{i=1}^t\frac{d_i}{p_i}.
\]

At a common evaluation price \(p_{n+1}>0\), terminal wealth is

\[
W^S=C_n+p_{n+1}Q_n,
\qquad
W^{DCA}=p_{n+1}A_n.
\]

No transaction costs, interest, borrowing, short sales, or future-price
information are allowed. The strategy may know the finite horizon; no
horizon-consistency assumption is needed.

Fix \(\lambda=1-\varepsilon\in(0,1]\). A strategy is
\(\lambda\)-DCA-safe when

\[
W^S\ge\lambda W^{DCA}
\tag{1}
\]

for every finite positive price path and every nonnegative deposit sequence.

## Theorem: exact robust-safety characterization

For a causal fully funded strategy, the following are equivalent.

1. The terminal guarantee (1) holds on every price path and deposit sequence.
2. After every reachable purchase history and every \(t\),
   \[
   Q_t\ge\lambda A_t.
   \tag{2}
   \]
3. After every history, the current purchase obeys
   \[
   x_t\ge m_t(\lambda):=
   \left[
   \lambda d_t-p_t\bigl(Q_{t-1}-\lambda A_{t-1}\bigr)
   \right]_+.
   \tag{3}
   \]

Moreover, the lower bound is always feasible:

\[
0\le m_t(\lambda)\le\lambda d_t\le d_t\le C_{t-1}+d_t.
\tag{4}
\]

Consequently every \(\lambda\)-DCA-safe strategy, and only such a strategy,
can be written after each history as

\[
x_t=m_t(\lambda)+a_t
\bigl(C_{t-1}+d_t-m_t(\lambda)\bigr),
\qquad 0\le a_t\le1,
\tag{5}
\]

where \(a_t\) is any causal score. Formula (5) is the complete discretionary
interface: the guardrail supplies robust safety and the score controls only the
remaining funded interval.

### Proof that prefix coverage is sufficient

If (2) holds, it holds in particular at \(t=n\). Since \(C_n\ge0\),

\[
W^S=C_n+p_{n+1}Q_n
\ge p_{n+1}\lambda A_n
=\lambda W^{DCA}.
\]

This uses the carried cash rather than omitting it, so the comparison has the
same economic accounting on both sides.

### Proof that prefix coverage is necessary

Assume the universal terminal guarantee but suppose that after some reachable
history at date \(t\),

\[
\delta:=\lambda A_t-Q_t>0.
\]

Let \(B=C_t\). Complete the deposit sequence with any fixed finite future
deposits having total \(F\ge0\). Set every remaining purchase price equal to
\(P^2\) and the evaluation price equal to \(P\). Whatever the causal strategy
does later, it can spend at most \(B+F\), so

\[
Q_n\le Q_t+\frac{B+F}{P^2},
\qquad
C_n\le B+F.
\]

DCA's future units are \(F/P^2\). Therefore

\[
\begin{aligned}
W^S-\lambda W^{DCA}
&=C_n+P(Q_n-\lambda A_n)\\
&\le B+F-P\delta+\frac{B+(1-\lambda)F}{P}\\
&\le B+F-P\delta+\frac{B+F}{P}.
\end{aligned}
\tag{6}
\]

Choose a finite \(P\ge1\) with \(P\delta>2(B+F)\). The right-hand side of
(6) is then negative, contradicting the universal guarantee. When \(t=n\),
the same argument simply varies the evaluation price and takes \(F=0\).
Thus every reachable prefix must satisfy (2).

This continuation also works if a formulation requires strictly positive
future deposits: take any fixed positive continuation and then choose \(P\)
large enough.

### Proof of the local guardrail and feasibility

Define the unit-coverage cushion

\[
R_{t-1}:=Q_{t-1}-\lambda A_{t-1}.
\]

Given coverage through date \(t-1\), \(R_{t-1}\ge0\). Using the recursions for
\(Q_t\) and \(A_t\), condition (2) at date \(t\) is equivalent to

\[
x_t\ge\lambda d_t-p_tR_{t-1}.
\]

Together with \(x_t\ge0\), this is exactly (3). Since
\(R_{t-1}\ge0\), the inequalities in (4) follow, proving that the minimum
purchase never exceeds even the new deposit, much less all available cash.
Induction from \(R_0=0\) proves that any causal choice from the interval in
(5) preserves coverage. Conversely, every safe purchase lies in that interval
and therefore has representation (5), with the evident endpoint convention
when the interval has zero length.

## Exact worst-case factor

For any fixed strategy and horizon, restrict to admissible cases with at least
one positive deposit and define

\[
\Gamma(S):=
\inf_{\text{full admissible paths}}
\frac{W^S}{W^{DCA}}.
\]

Then

\[
\Gamma(S)=
\inf_{\substack{\text{reachable histories }h_t\\A_t(h_t)>0}}
\frac{Q_t(h_t)}{A_t(h_t)}.
\tag{7}
\]

Indeed, terminal cash is nonnegative, so every full path has
\(W^S/W^{DCA}\ge Q_n/A_n\). Conversely, the \(P^2\)-purchase, \(P\)-evaluation
continuation above makes cash and future units negligible relative to the
value of any chosen prefix as \(P\to\infty\), so its terminal ratio approaches
that prefix's unit-coverage ratio. Equation (7) makes the factor sharp rather
than merely sufficient.

## Boundary cases and constructive consequences

### Exact boundary \(\lambda=1\)

At the first date, (3) requires \(x_1\ge d_1\), while funding requires
\(x_1\le d_1\). Hence \(x_1=d_1\), \(C_1=0\), and \(R_1=0\). Induction gives
\(x_t=d_t\) at every date. Thus 1-DCA safety uniquely recovers DCA and ticket
04's impossibility boundary.

### Every \(0<\lambda<1\) admits a non-DCA strategy

The fixed reserve rule

\[
x_t=\lambda d_t
\tag{8}
\]

has \(Q_t=\lambda A_t\) and
\(C_t=(1-\lambda)\sum_{i=1}^t d_i\). It is causal, fully funded, and non-DCA
whenever some deposit is positive and \(\lambda<1\). Its terminal wealth is

\[
W^S=\lambda W^{DCA}
 +(1-\lambda)\sum_{t=1}^n d_t.
\tag{9}
\]

It beats DCA exactly when DCA's terminal wealth is below total nominal
deposits, ties when they are equal, and trails DCA otherwise while never
falling below the \(\lambda\) floor. With one purchase at price 1 and
evaluation price \(P\), its ratio is

\[
\frac{W^S}{W^{DCA}}
=\lambda+\frac{1-\lambda}{P}\downarrow\lambda,
\]

so no larger uniform factor is valid for this construction.

### Zero deposits

Before the first positive deposit, \(A_t=Q_t=C_t=0\) and (3) gives
\(m_t=0\). If every deposit is zero, both terminal wealths are zero and the
guarantee holds trivially.

### One purchase date

For \(n=1\), the complete characterization is simply
\(\lambda d_1\le x_1\le d_1\). An arbitrarily large evaluation price exposes
any purchase below \(\lambda d_1\), so the result does not rely on multiple
purchase dates.

### Constant prices

If all purchase prices and the evaluation price equal \(p>0\), every fully
funded allocation has terminal wealth \(\sum_t d_t\). Equality on this one
path therefore identifies neither DCA nor the guardrail; robust identification
comes from the full continuation class.

### Limit \(\lambda\downarrow0\)

The minimum purchase tends to zero and the safety statement tends to the
vacuous nonnegativity guarantee \(W^S\ge0\). At the excluded endpoint
\(\lambda=0\) (equivalently \(\varepsilon=1\)), every fully funded strategy is
safe and (2)--(5) remain valid with a zero floor.

## Numerical example

Take \(\lambda=0.9\), deposits \((100,100)\), and the fixed reserve rule
\(x=(90,90)\).

- At purchase prices \((100,80)\) and evaluation price 70, the candidate has
  wealth 161.75 versus DCA's 157.50, so it strictly wins.
- At purchase prices \((100,120)\) and evaluation price 130, the candidate has
  wealth 234.50 versus DCA's 238.33, but remains above the required floor
  \(0.9\times238.33=214.50\).

Exact exhaustive checks of the algebra, boundary cases, adversarial
continuations, and construction are in
[`check_epsilon_dca_safety_guardrail.py`](../../reproducibility/checks/check_epsilon_dca_safety_guardrail.py).

## Interpretation and limitation

The theorem does not establish that a corrected quasi-Gini score improves DCA.
It creates a sharp separation of responsibilities: the guardrail supplies the
model-free downside factor, while a later theorem must define a bounded causal
score \(a_t\), prove its economic/accounting identities, and characterize the
paths or stochastic objective on which the discretionary allocation adds
value. Ticket 08's source audit found no exact published DCA statement of this
characterization, but non-discovery is not proof of novelty; it should remain
positioned as a DCA-specific robust-superhedging result until a broader
citation review accompanies the manuscript.
