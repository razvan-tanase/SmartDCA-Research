---
profile: smartdca-okf/0.5
type: theorem
title: "Three-purchase guarded SmartDCA has an exact beta-sensitive DCA boundary"
description: "At three purchases the DCA wealth boundary depends on beta only through the first two-input corrected reference and can flip exactly."
knowledge_role: canonical
status: stable
sources:
  - id: effect-note
    title: "Exact three-purchase corrected-mean effect"
    resource: research/notes/three-purchase-corrected-mean-effect
    source_kind: internal
  - id: ticket-18
    title: "Isolate the first nontrivial corrected-mean effect at three purchases"
    resource: .scratch/smartdca/issues/18-isolate-three-purchase-corrected-mean-effect
    source_kind: internal
  - id: guarded-rule
    title: "The guarded corrected-mean SmartDCA rule"
    resource: research/definitions/guarded-corrected-mean-smartdca-rule
    source_kind: internal
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-16T11:20:00Z
generation_run: urn:uuid:1d09cb3f-94ee-4b73-b0f2-393b4227167d
verified:
  - by: openai-codex/smartdca-wiki-0.1
    at: 2026-08-16T11:30:00Z
    review_run: urn:uuid:d55d437b-21a4-4ffb-b393-de516fb58c2d
---
# Three-purchase guarded SmartDCA has an exact beta-sensitive DCA boundary

## Statement

Apply [the guarded corrected-mean SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md) at exactly three purchase dates with positive purchase and evaluation prices, nonnegative deposits, and \(0<\lambda\le1\). Put[^guarded-rule]

\[
q=\frac{p_2}{p_1},\qquad
h=\frac{p_3}{p_2},\qquad
y=\frac{P}{p_3},\qquad
\delta=\frac{1-\lambda}{2}.
\]

The second score is

\[
a=\frac{1}{1+(f(q)/f(1))^{1-\alpha}},
\]

which is independent of \(\beta\). Define

\[
m_2=[\lambda d_2-\delta d_1q]_+,
\quad H_2=\delta d_1+d_2-m_2,
\quad C_2=(1-a)H_2,
\]

\[
\kappa_2=[\delta d_1q-\lambda d_2]_++aH_2,
\quad m_3=[\lambda d_3-h\kappa_2]_+,
\quad H_3=C_2+d_3-m_3.
\]

At date three the first multi-input reference and its score are

\[
R_2(\beta)=
\left(
\frac{f(1)^{\alpha-1}+qf(q)^{\alpha-1}}
     {f(1)^{\alpha-1}+q^{1-\alpha+\beta}f(q)^{\alpha-1}}
\right)^{1/(\alpha-\beta)}
\]

off the diagonal, with the canonical function-weighted geometric extension on \(\alpha=\beta\), and

\[
b_\beta
=\frac{1}{1+
\left(f(hq/R_2(\beta))/f(1)\right)^{1-\alpha}}.
\]

Set

\[
c_\beta=(1-b_\beta)H_3,
\qquad
g=\delta d_1h(1-q)+C_2(1-h).
\]

Then the terminal-wealth gap is exactly[^effect-note]

\[
\boxed{
W_3^S-W_3^{DCA}
=c_\beta(1-y)+gy
=c_\beta-y(c_\beta-g).
}
\]

For \(0<\lambda<1\) and \(d_1+d_2+d_3>0\), one has \(H_3,c_\beta>0\). Therefore the guarded rule wins exactly below

\[
T_\beta=
\begin{cases}
c_\beta/(c_\beta-g),&c_\beta-g>0,\\
+\infty,&c_\beta-g\le0,
\end{cases}
\]

ties at a finite threshold, and loses above a finite threshold. An infinite threshold is an all-win slice. At \(\lambda=1\), or when all deposits are zero, every case ties DCA.[^ticket-18]

## Exact beta effect

Holding \(\alpha,f\), prices, deposits, and \(\lambda\) fixed while changing \(\beta\) leaves both purchases and the portfolio state through date two fixed. Only \(R_2\), \(b_\beta\), and \(c_\beta\) can change. For two beta values,

\[
\Delta_\beta-\Delta_{\widetilde\beta}
=H_3(b_{\widetilde\beta}-b_\beta)(1-y).
\]

Their classifications differ exactly when \(y\) lies between unequal extended thresholds: strict signs are opposite in the interior, and one variant ties at a finite endpoint while the other is strict. A beta-driven classification change is possible exactly when the third scores differ, \(g\ne0\), and—if \(g>0\)—the two variants are not both already in the all-win region \(c\le g\).[^effect-note]

Such a change occurs inside the intended countercyclical region. Take

\[
\lambda=\frac12,\quad(d_1,d_2,d_3)=(1,1,1),\quad
(p_1,p_2,p_3,P)=\left(1,4,2,\frac73\right),
\quad f(u)=u,\quad\alpha=0.
\]

The common first two purchases are \(x_1=3/4\) and \(x_2=1/4\). Changing only beta gives

\[
\begin{array}{c|c|c|c|c}
\beta&R_2&b_\beta&T_\beta&W_3^S-W_3^{DCA}\\ \hline
-1&8/5&4/9&25/22&-1/36\\
 1&5/2&5/9&20/17& 1/144.
\end{array}
\]

Thus the first multi-input corrected reference can flip a strict DCA loss into a strict DCA win while the two-purchase calibration remains unchanged.[^effect-note]

## Sharpness and scope

The condition is necessary and sufficient for exactly three purchase dates, and every branch—including finite ties, strict wins and losses, all-win slices, zero deposits, and the \(\lambda=1\) collapse—occurs. The witness proves existence of beta sensitivity, not that increasing beta is generally beneficial. At \(y=1\), \(g=0\), \(\alpha=1\), a constant purchase-price history, or whenever the two beta values produce the same third score, beta cannot change the classification in the corresponding way.

This theorem makes no arbitrary-horizon, parameter-fitting, universal-dominance, or stochastic claim. The proof, threshold-equality analysis, direct portfolio calculations, and exact boundary examples are in [the evidence note](../notes/three-purchase-corrected-mean-effect.md).[^effect-note] The executable check is [`check_three_purchase_corrected_mean_effect.py`](../../reproducibility/checks/check_three_purchase_corrected_mean_effect.py).

[^effect-note]: [Exact three-purchase corrected-mean effect](../notes/three-purchase-corrected-mean-effect.md)
[^ticket-18]: [Isolate the first nontrivial corrected-mean effect at three purchases](../../.scratch/smartdca/issues/18-isolate-three-purchase-corrected-mean-effect.md)
[^guarded-rule]: [The guarded corrected-mean SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md)
