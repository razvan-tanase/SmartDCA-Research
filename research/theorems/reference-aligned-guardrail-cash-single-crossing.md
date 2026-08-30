# Reference-aligned guardrail feedback preserves cash single crossing

## Statement

Use the guarded corrected-mean rule and its neutral guarded selector with the
same positive purchase prices and equal positive deposits. Fix equal reference
weights, the identity transform, \(\alpha<1\), and \(\alpha\beta\le0\). Let
\(D_t=C_t^c-C_t^0\) be corrected-minus-neutral carried cash, let
\(m_t^c,m_t^0\) be the policies' clipped unit-guardrail floors, using the
score and floor conventions in the canonical rule.[^guarded-rule] Put

\[
H_t^0=C_{t-1}^0+d_t-m_t^0,
\qquad \Delta m_t=m_t^c-m_t^0.
\]

At every finite horizon,

\[
\boxed{
D_t=(1-a_t)D_{t-1}
    +\left(\frac12-a_t\right)H_t^0
    -(1-a_t)\Delta m_t,
\qquad D_0=0.
}
\tag{1}
\]

If the prices are weak single-valley, the corrected score has a boundary
\(j\) at which \(1/2-a_t\) changes at most once from nonpositive to
nonnegative. If, at one such boundary,

\[
\Delta m_t\ge0\quad(t\le j),
\qquad
\Delta m_t\le0\quad(t>j),
\tag{2}
\]

then, after zeros are deleted, the sign word of
\((D_1,\ldots,D_n)\) is a block of minus signs followed by a block of plus
signs, with either block possibly empty. Thus corrected-minus-neutral cash
changes sign at most once and only from nonpositive to nonnegative. Common
clipped floors \(m_t^c=m_t^0\) are a nonempty special case of (2), including
cases with repeated floor activation.[^mechanism-note]

The unconditional cash single-crossing statement is false, even for strict
four-date valleys. With unit deposits,

\[
p=(1,1/16,1,8),\quad P=p_4,\quad
\lambda=63/64,\quad(\alpha,\beta)=(-1,0),
\]

the exact cash differences have signs \(-,+,-\) after the first-date tie.
The same scores with both floors disabled have signs \(-,+,+\). Four dates
are horizon-minimal because the common warm-up forces \(D_1=0\), while two
sign changes require three later nonzero entries.[^mechanism-note][^ticket-03]

## Sharpness and interpretation

Condition (2) is sufficient, not necessary. The exact broad sufficient
condition is that the one-step forcing in (1) is nonpositive and then
nonnegative; (2) is the economically interpretable version that separately
aligns the observable corrected reference/score comparison and clipped-floor
feedback.

Non-necessity is exact. With unit deposits,
\(p=(1,2/3,1/2,2/3)\), \(\lambda=3/4\), and
\((\alpha,\beta)=(0,-1)\), the strict valley violates (2) at date three but
has cash differences

\[
\left(0,-\frac{11}{240},-\frac{397}{4992},
\frac{841}{149760}\right),
\]

which single-cross. At the violating date, the score component
\(-125/1664\) outweighs the floor component \(11/832\), leaving the required
negative net forcing. Conversely, a strict active-floor case at
\(p=(1,1/4,1/2,1)\), \(\lambda=7/8\), and
\((\alpha,\beta)=(0,-1)\) satisfies (2) with strict post-boundary floor and
cash-sign margins, so the sufficient class contains a nonempty strict region.
The double-reversal witness shows that weak or strict single-valley geometry
alone cannot replace the guardrail condition.[^mechanism-note]

## Scope limit

This theorem is about corrected-versus-neutral carried cash. It does not give
a terminal-wealth ordering against the neutral selector or DCA. The
cash-timing identity still weights the timing and magnitude of every cash
difference, so a separate condition is required to sign terminal wealth.

[^mechanism-note]: [Differential guardrail feedback defeats cash single crossing](../notes/cash-single-crossing-mechanism.md)
[^ticket-03]: [Characterize the cash single-crossing mechanism](../../.scratch/smartdca/efforts/arbitrary-horizon-performance/issues/03-characterize-cash-single-crossing-mechanism.md)
[^guarded-rule]: [The guarded corrected-mean SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md)
