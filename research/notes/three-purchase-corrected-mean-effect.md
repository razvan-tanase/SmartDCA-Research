---
profile: smartdca-okf/0.5
type: research-note
title: "Exact three-purchase corrected-mean effect"
description: "Derivation of the exact three-purchase DCA boundary and an all-rational beta-driven classification flip."
knowledge_role: evidence
status: stable
sources:
  - id: ticket-18
    title: "Isolate the first nontrivial corrected-mean effect at three purchases"
    resource: .scratch/smartdca/issues/18-isolate-three-purchase-corrected-mean-effect
    source_kind: internal
  - id: guarded-rule
    title: "The guarded corrected-mean SmartDCA rule"
    resource: research/definitions/guarded-corrected-mean-smartdca-rule
    source_kind: internal
  - id: corrected-mean
    title: "The corrected out quasi-Gini mean"
    resource: research/definitions/corrected-out-quasi-gini-mean
    source_kind: internal
  - id: two-purchase-boundary
    title: "Two-purchase guarded SmartDCA has an exact DCA boundary"
    resource: research/theorems/two-purchase-guarded-smartdca-boundary
    source_kind: internal
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-16T11:28:00Z
generation_run: urn:uuid:1d09cb3f-94ee-4b73-b0f2-393b4227167d
verified:
  - by: openai-codex/smartdca-wiki-0.1
    at: 2026-08-16T11:30:00Z
    review_run: urn:uuid:d55d437b-21a4-4ffb-b393-de516fb58c2d
---
# Exact three-purchase corrected-mean effect

Canonical home: [Three-purchase guarded SmartDCA has an exact beta-sensitive DCA boundary](../theorems/three-purchase-corrected-mean-effect.md). That concept carries the result; this note carries the reduction, proof, complete boundary classification, beta-sensitivity criterion, edge cases, and exact witness.

## 1. Scope and notation

Apply the exact [guarded corrected-mean SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md) at precisely three purchase dates in its inherited fair comparison model.[^guarded-rule] Let

\[
p_1,p_2,p_3,P>0,\qquad d_1,d_2,d_3\ge0,
\qquad 0<\lambda\le1,
\]

where \(P\) is the common evaluation price after the third purchase. Use the observable ratios

\[
q:=\frac{p_2}{p_1},\qquad
h:=\frac{p_3}{p_2},\qquad
y:=\frac{P}{p_3},\qquad
\delta:=\frac{1-\lambda}{2}.
\tag{1}
\]

Write \(a:=a_2\) and \(b_\beta:=a_3\), displaying the parameter that can first enter nontrivially at date three. Prices are anchored at \(p_1\), so the normalized history through date three is \((1,q,hq)\).

This ticket asks for a deterministic realized-path sign condition, not a parameter fit, probability of winning, or arbitrary-horizon result.[^ticket-18]

## 2. The first multi-input reference

At date two the lagged reference is the singleton \(R_1=1\). Therefore

\[
a=\frac{1}{1+\left(f(q)/f(1)\right)^{1-\alpha}}
\tag{2}
\]

is independent of \(\beta\), exactly as the two-purchase theorem records.[^two-purchase-boundary]

At date three the equally weighted lagged input is \((1,q)\). From the canonical corrected mean,[^corrected-mean] its reference is

\[
R_2(\beta)=
\left(
\frac{f(1)^{\alpha-1}+qf(q)^{\alpha-1}}
     {f(1)^{\alpha-1}+q^{1-\alpha+\beta}f(q)^{\alpha-1}}
\right)^{1/(\alpha-\beta)},
\qquad \alpha\ne\beta,
\tag{3}
\]

and on the diagonal \(\alpha=\beta\),

\[
R_2(\alpha)
=\exp\!\left(
\frac{qf(q)^{\alpha-1}\log q}
     {f(1)^{\alpha-1}+qf(q)^{\alpha-1}}
\right).
\tag{4}
\]

Consequently the first beta-sensitive candidate score is

\[
\boxed{
b_\beta
=\frac{1}{1+
\left(f(hq/R_2(\beta))/f(1)\right)^{1-\alpha}}
}\in(0,1).
\tag{5}
\]

Equations (2)--(5) separate the two parameter channels: \((\alpha,f)\)
already enter the beta-independent two-date calibration \(a\), while
\((\alpha,\beta,f)\) enter the third decision through \(R_2\) and
\(b_\beta\). Conditional on the fixed two-date calibration, varying
\(\beta\) leaves every action and state through date two unchanged and can
act only through \(R_2(\beta)\) and \(b_\beta\).

## 3. Exact state reduction

The warm-up score is \(1/2\). As in the two-purchase reduction,

\[
x_1=(1-\delta)d_1,\qquad
C_1=\delta d_1,\qquad
K_1=\frac{\delta d_1}{p_1}.
\tag{6}
\]

The date-two floor and discretionary interval are

\[
m_2=[\lambda d_2-\delta d_1q]_+,
\qquad
H_2=\delta d_1+d_2-m_2.
\tag{7}
\]

Thus

\[
x_2=m_2+aH_2,
\qquad
C_2=(1-a)H_2.
\tag{8}
\]

Scale the post-date-two unit-coverage cushion by \(p_2\):

\[
\kappa_2:=p_2K_2
=[\delta d_1q-\lambda d_2]_++aH_2.
\tag{9}
\]

This follows directly from \(K_2=K_1+(x_2-\lambda d_2)/p_2\), split across the two branches of (7). It makes the date-three floor explicit in the chosen ratios:

\[
m_3=[\lambda d_3-h\kappa_2]_+,
\qquad
H_3=C_2+d_3-m_3.
\tag{10}
\]

The third purchase and terminal cash are therefore

\[
x_3=m_3+b_\beta H_3,
\qquad
c_\beta:=C_3=(1-b_\beta)H_3.
\tag{11}
\]

Everything in (6)--(10) is independent of \(\beta\). At three dates the parameter changes only \(b_\beta\), hence only the split of the fixed interval \(H_3\) between the third purchase and terminal cash.

## 4. Necessary-and-sufficient DCA wealth condition

Define the beta-independent prior-state shift

\[
g:=\delta d_1h(1-q)+C_2(1-h).
\tag{12}
\]

The deviations from DCA spending at the three dates are exactly

\[
x_1-d_1=-\delta d_1,\qquad
x_2-d_2=\delta d_1-C_2,\qquad
x_3-d_3=C_2-c_\beta.
\tag{13}
\]

Using \(P=yp_3=yhp_2\), direct cash-inclusive accounting gives

\[
\begin{aligned}
\Delta_\beta
&:=W_3^S-W_3^{DCA}\\
&=c_\beta+P\left(
-\frac{\delta d_1}{p_1}
+\frac{\delta d_1-C_2}{p_2}
+\frac{C_2-c_\beta}{p_3}
\right)\\
&=c_\beta(1-y)
+y\left[\delta d_1h(1-q)+C_2(1-h)\right].
\end{aligned}
\tag{14}
\]

Hence the requested condition is

\[
\boxed{
W_3^S>W_3^{DCA}
\iff
\Delta_\beta=c_\beta-y(c_\beta-g)>0.
}
\tag{15}
\]

This is necessary and sufficient, not a sufficient path condition.

Assume now \(0<\lambda<1\) and \(d_1+d_2+d_3>0\). From \(m_2\le\lambda d_2\),

\[
H_2\ge\delta d_1+(1-\lambda)d_2.
\]

If either of the first two deposits is positive, then \(H_2>0\) and \(C_2>0\). If both are zero, then \(d_3>0\). In either case, because \(m_3\le\lambda d_3\),

\[
H_3\ge C_2+(1-\lambda)d_3>0.
\tag{16}
\]

Since \(0<b_\beta<1\), this proves \(c_\beta>0\). Define

\[
T_\beta:=
\begin{cases}
\displaystyle\frac{c_\beta}{c_\beta-g},
&c_\beta-g>0,\\[8pt]
+\infty,&c_\beta-g\le0.
\end{cases}
\tag{17}
\]

The complete classification is

\[
\begin{array}{c|c}
\text{condition}&\text{DCA comparison}\\ \hline
0<y<T_\beta&W_3^S>W_3^{DCA},\\
y=T_\beta<\infty&W_3^S=W_3^{DCA},\\
y>T_\beta\text{ with }T_\beta<\infty&W_3^S<W_3^{DCA}.
\end{array}
\tag{18}
\]

When \(T_\beta=+\infty\), every finite \(y>0\) is a strict win on that fixed slice. Both global strict regions are nonempty for every \(0<\lambda<1\) and nonzero deposit triple: set \(q=h=1\), which gives \(g=0\), \(T_\beta=1\), and choose \(y<1\) or \(y>1\).

## 5. Exact beta-sensitivity criterion

Fix all inputs except \(\beta\), and compare \(\beta\) with \(\widetilde\beta\). The two variants have the same \(a,C_2,\kappa_2,m_3,H_3\), and \(g\). Their exact numerical wealth difference is

\[
\boxed{
\Delta_\beta-\Delta_{\widetilde\beta}
=H_3\bigl(b_{\widetilde\beta}-b_\beta\bigr)(1-y).
}
\tag{19}
\]

For a fixed evaluation ratio, their DCA win/tie/loss classifications differ exactly when \(y\) lies between their unequal extended thresholds \(T_\beta\) and \(T_{\widetilde\beta}\): in the open interval the strict signs are opposite, while at a finite endpoint one variant ties and the other is strict. If one threshold is \(+\infty\), the interval continues through all finite \(y\) above the finite endpoint.

The threshold equality cases are also exact. Let \(c_\beta=(1-b_\beta)H_3\).

- If \(b_\beta=b_{\widetilde\beta}\), then the thresholds and classifications coincide.
- If \(g=0\), every positive \(c\) has threshold \(1\), so beta can change the gap's magnitude but not its sign.
- If \(g<0\), the finite map \(c\mapsto c/(c-g)\) is strictly increasing; different third scores give different thresholds.
- If \(g>0\), the extended map is \(+\infty\) for \(c\le g\) and strictly decreasing for \(c>g\). Different scores give different thresholds unless both variants already lie in the all-win region \(c\le g\).

Thus some evaluation price produces a beta-driven classification change if and only if

\[
b_\beta\ne b_{\widetilde\beta},\qquad
g\ne0,
\qquad
\text{and not both }c_\beta,c_{\widetilde\beta}\le g\text{ when }g>0.
\tag{20}
\]

At \(y=1\), equation (14) reduces to \(\Delta_\beta=g\), so beta cannot change the classification there. The current-price countercyclical conditions \(f\) nondecreasing and \(\alpha\le1\) do not force (20) to fail: they control response to the current price, not parameter dependence of the lagged reference.

## 6. Exact countercyclical witness

Choose

\[
\lambda=\frac12,\qquad
(d_1,d_2,d_3)=(1,1,1),\qquad
(p_1,p_2,p_3,P)=\left(1,4,2,\frac73\right),
\tag{21}
\]

and use \(f(u)=u\), \(\alpha=0\). This is inside the intended region: \(f\) is strictly increasing and \(\alpha<1\). Here

\[
q=4,\qquad h=\frac12,\qquad y=\frac76,
\qquad a=\frac{1}{1+q}=\frac15.
\]

The entire two-date calibration and state are fixed:

\[
x_1=\frac34,\quad m_2=0,\quad H_2=\frac54,
\quad x_2=\frac14,\quad C_2=1,
\quad\kappa_2=\frac34.
\tag{22}
\]

At date three,

\[
m_3=\frac18,\qquad H_3=\frac{15}{8},\qquad g=\frac18.
\tag{23}
\]

For the identity transform and \(\alpha=0\), equation (3) is the classical two-input Gini reference

\[
R_2(\beta)=\left(\frac{1+q^\beta}{2}\right)^{1/\beta}
\qquad(\beta\ne0).
\]

Changing only \(\beta\) gives

\[
\begin{array}{c|c|c|c|c|c|c}
\beta&R_2&b_\beta&x_3&c_\beta&T_\beta&\Delta_\beta\\ \hline
-1&8/5&4/9&23/24&25/24&25/22&-1/36\\
 1&5/2&5/9&7/6&5/6&20/17& 1/144
\end{array}
\tag{24}
\]

Indeed,

\[
\frac{25}{22}<\frac76<\frac{20}{17}.
\]

Thus \(\beta=-1\) produces a strict DCA loss while \(\beta=1\) produces a strict DCA win on the same positive price path, deposits, evaluation price, safety factor, transform, \(\alpha\), and identical first two purchases. This is an exact beta-driven win/loss flip. The DCA unit total is \(7/4\), and direct cash-plus-units accounting gives the two gaps in (24), independently confirming (14).

The endpoint classifications also occur without changing the purchase path: at \(y=25/22\), the \(\beta=-1\) variant ties while \(\beta=1\) wins; at \(y=20/17\), the first loses while the second ties.

## 7. Boundary cases and scope limit

- If all three deposits are zero, both wealths are zero and no strict classification is possible.
- At \(\lambda=1\), every discretionary interval collapses, \(c_\beta=g=0\), and the rule is DCA regardless of \(\beta\).
- On a constant purchase-price history, \(q=h=R_2=1\), both non-warm-up scores are \(1/2\), and beta disappears.
- At \(\alpha=1\), the score is \(1/2\) for every reference, so beta cannot affect any purchase.
- A merely nondecreasing transform may be constant on the relevant arguments; the countercyclical assumptions alone guarantee no strict beta effect. The witness establishes existence, not universality.

The result does not rank beta values, claim that increasing beta is beneficial, select a parameter, or establish a probability of winning. It proves only that the first multi-input corrected-mean reference can alter the exact realized DCA classification at the third purchase. No arbitrary-horizon formula or stochastic claim is made.

## 8. Executable verification

[`check_three_purchase_corrected_mean_effect.py`](../../reproducibility/checks/check_three_purchase_corrected_mean_effect.py) checks (6)--(18) in exact rational arithmetic over 46,656 terminal valuations, including both date-two and date-three floor branches, 7,680 generated finite-boundary ties, 744 all-win slices, zero deposits, constant prices, and the \(\lambda=1\) collapse. It separately reproduces every fraction in (21)--(24), the strict win/loss flip, both tie endpoints, and equation (19).

[^ticket-18]: [Isolate the first nontrivial corrected-mean effect at three purchases](../../.scratch/smartdca/issues/18-isolate-three-purchase-corrected-mean-effect.md)
[^guarded-rule]: [The guarded corrected-mean SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md)
[^corrected-mean]: [The corrected out quasi-Gini mean](../definitions/corrected-out-quasi-gini-mean.md)
[^two-purchase-boundary]: [Two-purchase guarded SmartDCA has an exact DCA boundary](../theorems/two-purchase-guarded-smartdca-boundary.md)
