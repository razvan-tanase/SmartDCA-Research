---
profile: smartdca-okf/0.3
type: research-note
title: "Exact two-purchase DCA win/loss boundary"
description: "Derivation of the necessary-and-sufficient two-purchase wealth boundary and exact neutral-score comparison."
knowledge_role: evidence
status: stable
sources:
  - id: ticket-11
    title: "Characterize the two-purchase DCA win/loss boundary"
    resource: .scratch/smartdca/issues/11-characterize-two-purchase-dca-win-loss-boundary
    source_kind: internal
  - id: guarded-rule
    title: "The guarded corrected-mean SmartDCA rule"
    resource: research/definitions/guarded-corrected-mean-smartdca-rule
    source_kind: internal
  - id: guardrail
    title: "Epsilon-DCA safety is exactly a causal unit-coverage guardrail"
    resource: research/theorems/epsilon-dca-safety-unit-guardrail
    source_kind: internal
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-16T11:02:00Z
generation_run: urn:uuid:15b108f2-1ab8-4916-965a-89faffe7b3f6
verified:
  - by: openai-codex/smartdca-wiki-0.1
    at: 2026-08-16T11:14:00Z
    review_run: urn:uuid:5fdc289a-b5ff-4e1f-9d84-777c58a093f2
  - by: openai-codex/smartdca-wiki-0.1
    at: 2026-08-16T11:30:00Z
    review_run: urn:uuid:d55d437b-21a4-4ffb-b393-de516fb58c2d
---
# Exact two-purchase DCA win/loss boundary

Canonical home: [Two-purchase guarded SmartDCA has an exact DCA boundary](../theorems/two-purchase-guarded-smartdca-boundary.md). That concept carries the result; this note carries the derivation, boundary classification, neutral-selector comparison, edge cases, and exact example.

## 1. Scope and notation

Use exactly two purchase dates in the comparison model inherited by
[the guarded corrected-mean SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md).
Let

\[
p_1,p_2,P>0,\qquad d_1,d_2\ge0,\qquad 0<\lambda\le1,
\]

where \(P\) is the common evaluation price after the second purchase. Define
the observable ratios and the first-date reserve fraction

\[
q:=\frac{p_2}{p_1},\qquad
y:=\frac{P}{p_2},\qquad
\delta:=\frac{1-\lambda}{2}.
\tag{1}
\]

At date two, the lagged normalized history contains only \(z_1=1\). By
reflexivity, the corrected-mean reference is therefore \(R_1=1\), including
on the diagonal \(\alpha=\beta\). Hence

\[
r_2=q,\qquad
a:=a_2(q)=
\frac{1}{1+\left(f(q)/f(1)\right)^{1-\alpha}}\in(0,1).
\tag{2}
\]

The parameter \(\beta\) drops out completely. Thus a two-purchase comparison
tests the transform/\(\alpha\) score calibration and the guardrail, but not a
nontrivial multi-input corrected-mean reference. The earliest purchase date at
which \(\beta\) can affect the score is date three.

## 2. Exact two-date reduction

The warm-up score is \(a_1=1/2\). Since \(m_1=\lambda d_1\), the first
purchase, carried cash, and unit-coverage cushion are

\[
x_1=\frac{1+\lambda}{2}d_1=(1-\delta)d_1,
\qquad
C_1=\delta d_1,
\qquad
K_1=\frac{\delta d_1}{p_1}.
\tag{3}
\]

The date-two floor, available cash, and discretionary interval length are

\[
m_2(q)=\left[\lambda d_2-\delta d_1q\right]_+,
\qquad
B_2=\delta d_1+d_2,
\tag{4}
\]

\[
H(q):=B_2-m_2(q)
=\delta d_1+d_2-\left[\lambda d_2-\delta d_1q\right]_+.
\tag{5}
\]

Consequently

\[
x_2=m_2+aH,
\qquad
C_2=(1-a)H.
\tag{6}
\]

Write

\[
c_a(q):=(1-a(q))H(q),
\qquad
g(q):=\delta d_1(1-q).
\tag{7}
\]

The first quantity is exactly the terminal cash \(C_2\); the second is the
evaluation-scaled unit effect of shifting \(\delta d_1\) away from date one
before accounting for terminal cash.

## 3. Necessary-and-sufficient wealth condition

Let \(\Delta_a:=W_2^S-W_2^{DCA}\). Total-spending accounting gives

\[
x_2-d_2=\delta d_1-C_2.
\tag{8}
\]

Using \(x_1-d_1=-\delta d_1\), the exact wealth gap is

\[
\begin{aligned}
\Delta_a
&=C_2+P\left(
-\frac{\delta d_1}{p_1}
+\frac{\delta d_1-C_2}{p_2}
\right)\\
&=C_2\left(1-\frac{P}{p_2}\right)
+\delta d_1\frac{P}{p_2}
\left(1-\frac{p_2}{p_1}\right).
\end{aligned}
\tag{9}
\]

Equivalently, in only the requested ratios, deposits, safety factor, and
score,

\[
\boxed{
\Delta_a
=(1-a)H(1-y)+\delta d_1y(1-q)
=c_a-y\Gamma_a,
}
\tag{10}
\]

where

\[
\Gamma_a(q):=c_a(q)-g(q)
=(1-a(q))H(q)-\delta d_1(1-q).
\tag{11}
\]

Therefore the requested necessary-and-sufficient condition is simply

\[
\boxed{W_2^S>W_2^{DCA}\iff c_a-y\Gamma_a>0.}
\tag{12}
\]

For a geometric description, assume \(0<\lambda<1\) and
\(d_1+d_2>0\). Then

\[
H\ge \delta d_1+(1-\lambda)d_2>0,
\tag{13}
\]

because \(m_2\le\lambda d_2\). Since \(a\in(0,1)\), this gives
\(c_a>0\). Define the extended boundary height

\[
T_a(q):=
\begin{cases}
\displaystyle \frac{c_a(q)}{c_a(q)-g(q)},
&\Gamma_a(q)>0,\\[8pt]
+\infty,&\Gamma_a(q)\le0.
\end{cases}
\tag{14}
\]

Then the complete classification is

\[
\begin{array}{c|c}
\text{condition} & \text{DCA comparison}\\ \hline
0<y<T_a(q) & W_2^S>W_2^{DCA},\\
y=T_a(q)<\infty & W_2^S=W_2^{DCA},\\
y>T_a(q)\text{ with }T_a(q)<\infty & W_2^S<W_2^{DCA}.
\end{array}
\tag{15}
\]

When \(T_a=+\infty\), every finite \(y>0\) is a strict win; there is no tie
or loss on that fixed \((q,d_1,d_2,\lambda)\) slice. Equivalently, this
all-win case is possible only for \(q<1\) and occurs exactly when

\[
(1-a)H\le\delta d_1(1-q).
\tag{16}
\]

For \(q\ge1\), \(g\le0<c_a\), so the boundary is always finite. At
\(q=1\), \(a=1/2\), \(T_a=1\), and the tie is \(P=p_2=p_1\).

## 4. Nonempty regions and collapse

For every \(0<\lambda<1\) and every fixed nonzero deposit pair, set
\(q=1\). Equation (13) gives \(H>0\), while \(a=1/2\), \(g=0\), and
\(T_a=1\). Choosing \(0<y<1\) gives a strict win and choosing \(y>1\)
gives a strict loss. Thus the strict-win and strict-loss regions are each
nonempty. The qualification \(d_1+d_2>0\) is necessary: if both deposits are
zero, both wealths are identically zero.

At \(\lambda=1\), \(\delta=0\), \(m_2=d_2\), and \(H=0\). Equations
(3) and (6) reduce to \(x_1=d_1\), \(x_2=d_2\), and \(C_2=0\). Hence

\[
\boxed{W_2^S=W_2^{DCA}\quad\text{for all admissible inputs when }\lambda=1,}
\tag{17}
\]

regardless of the score. This is the exact two-date manifestation of the DCA
uniqueness boundary.

Two useful limits also follow directly from (10). As \(y\downarrow0\),
\(\Delta_a\to c_a>0\) for a nonzero deposit pair and \(\lambda<1\). As
\(y\to\infty\), a strict loss occurs exactly when \(\Gamma_a>0\); if
\(\Gamma_a\le0\), the fixed slice remains a strict win.

## 5. Exact comparison with a neutral selector

The neutral rule uses the same date-one state and date-two floor but sets
\(a_2=1/2\). Put

\[
c_0:=\frac{H}{2},
\qquad
\Gamma_0:=c_0-g,
\qquad
T_0:=
\begin{cases}
c_0/\Gamma_0,&\Gamma_0>0,\\
+\infty,&\Gamma_0\le0.
\end{cases}
\tag{18}
\]

The wealth effect of replacing the neutral selector by the corrected-mean
score is exactly

\[
\boxed{
\Delta_a-\Delta_{1/2}
=H\left(\frac12-a\right)(1-y).
}
\tag{19}
\]

Thus the score changes the numerical wealth gap only when
\(a\ne1/2\), \(y\ne1\), and \(H>0\). The DCA win/tie/loss *classification*
changes on a smaller, exact set. Each selector wins below its own extended
threshold and loses above a finite threshold, so:

- if \(T_a=T_0\), the three-way classification never changes;
- if \(T_a>T_0\), the corrected score wins while neutral loses exactly for
  \(T_0<y<T_a\); at a finite endpoint one policy ties while the other is
  strict;
- if \(T_a<T_0\), the corrected score loses while neutral wins exactly for
  \(T_a<y<T_0\), again with tie-versus-strict outcomes at finite endpoints.

Here an upper endpoint of \(+\infty\) means the corresponding open interval
continues through every finite \(y\). This is a necessary-and-sufficient
description: the three-way results differ exactly on the closed interval
between unequal extended thresholds, with the nonexistent point at infinity
excluded; the strict signs are opposite exactly in its interior.

### Intended countercyclical parameter region

If \(f\) is nondecreasing and \(\alpha\le1\), then

\[
q>1\Longrightarrow a\le\tfrac12,
\qquad
q<1\Longrightarrow a\ge\tfrac12.
\tag{20}
\]

For fixed \(g<0\) the finite map \(c\mapsto c/(c-g)\) is increasing.
For fixed \(g>0\), its extended version—\(+\infty\) on \(c\le g\)—is
nonincreasing. Equations (20) and \(c_a=(1-a)H\) therefore imply

\[
\boxed{T_a\ge T_0.}
\tag{21}
\]

So the intended countercyclical score never converts a neutral strict win
into a strict loss in this two-purchase classification. It changes the strict
result exactly on \(T_0<y<T_a\), where it converts a neutral loss into a win.
This is not dominance over the neutral policy: outside the classification-flip
strip, (19) can still make the corrected policy's wealth gap numerically
smaller while both policies retain the same sign.

The threshold enlargement is strict under precisely these additional
conditions:

- for \(q>1\): \(d_1>0\) and \(a<1/2\);
- for \(q<1\): \(d_1>0\), \(a>1/2\), and
  \(H/2>\delta d_1(1-q)\).

In the second case, if \(H/2\le\delta d_1(1-q)\), both the neutral and
corrected rules already win for every finite \(y\), so their classifications
cannot differ. The thresholds also coincide when \(d_1=0\), \(q=1\), or
\(a=1/2\). For strictly increasing \(f\) and \(\alpha<1\), score equality
\(a=1/2\) occurs only at \(q=1\). At \(\alpha=1\), the score is neutral
everywhere. With strictly increasing \(f\) and \(\alpha>1\), all weak
threshold inequalities reverse: the momentum score can change a neutral win
into a loss on \(T_a<y<T_0\).

## 6. Exact example and checks

Take

\[
\lambda=\frac12,\quad d_1=d_2=1,\quad
q=2,\quad f(u)=u,\quad \alpha=0,
\]

with arbitrary \(\beta\). Then \(\delta=1/4\), \(a=1/3\), \(m_2=0\),
and \(H=5/4\). The corrected and neutral thresholds are

\[
T_a=\frac{10}{13},\qquad T_0=\frac57.
\]

Choose \(y=3/4\), equivalently \((p_1,p_2,P)=(1,2,3/2)\). Since
\(5/7<3/4<10/13\), the corrected score wins while the neutral selector
loses. Directly,

\[
\Delta_a=\frac1{48}>0,
\qquad
\Delta_{1/2}=-\frac1{32}<0.
\tag{22}
\]

As an all-win slice, take the same \(\lambda,d_1,f,\alpha\), let
\(d_2=0\), and set \(q=1/2\). Then \(a=2/3\), \(c_a=1/12\), and
\(g=1/8\), so \(\Gamma_a<0\) and
\(\Delta_a=1/12+y/24>0\) for every \(y>0\).

The companion verifier checks (3)--(12) in exact rational arithmetic over
zero and positive deposits, both guardrail branches, countercyclical, neutral,
and momentum scores, finite and all-win boundaries, generated boundary ties,
the \(\lambda=1\) collapse, and the two examples. It also checks that each
selector's threshold predicts the direct portfolio comparison and that (19)
holds identically.

## 7. Scope limit

This is a deterministic, realized two-purchase characterization. It makes no
stochastic claim, supplies no probability of winning, and does not generalize
the formula to arbitrary horizons. Both strict regions remain nonempty for
every positive tolerance, so the result is not universal DCA dominance. Most
importantly, \(\beta\)'s disappearance means the result does not yet test
whether the multi-input corrected-mean reference adds value; that question
requires at least a third purchase date.
