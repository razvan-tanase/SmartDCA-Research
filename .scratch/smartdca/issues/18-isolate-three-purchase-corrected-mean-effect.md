---
profile: smartdca-okf/0.5
type: research-ticket
title: "Isolate the first nontrivial corrected-mean effect at three purchases"
description: "Resolved task ticket isolating the first beta-dependent guarded SmartDCA boundary at three purchases."
knowledge_role: operational
status: stable
ticket_type: task
ticket_status: resolved
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-16T11:28:00Z
generation_run: urn:uuid:1d09cb3f-94ee-4b73-b0f2-393b4227167d
---
# Isolate the first nontrivial corrected-mean effect at three purchases

Type: task
Status: resolved
Blocked by: 11
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

For the exact guarded corrected-mean rule, use exactly three purchase dates
and positive purchase/evaluation prices with nonnegative deposits. Since the
third score is the first one whose lagged reference has two inputs, derive a
necessary-and-sufficient DCA wealth condition that isolates how
\((\alpha,\beta,f)\) enters through \(R_2\) and \(a_3\). Determine whether
changing \(\beta\) while holding the two-purchase calibration fixed can change
the DCA win/tie/loss classification, and give an exact witness or prove that
no such witness exists under the intended countercyclical conditions. Do not
generalize to arbitrary horizons, fit parameters, or make a stochastic claim.

## Comments

- Created during resolution of [Characterize the two-purchase DCA win/loss boundary](11-characterize-two-purchase-dca-win-loss-boundary.md), which proves that \(\beta\) drops out at two purchases because the lagged reference is the singleton \((1)\).
- The ticket was left open and unclaimed pending the ticket 11 significance
  gate; the user's explicit request to resolve ticket 18 passed that gate on
  2026-08-16.
- The exact-rational verifier covers both date-two and date-three floor
  branches, the off-diagonal and diagonal references, finite ties, all-win
  slices, zero deposits, constant prices, and the \(\lambda=1\) collapse.
- A separate domain-review run re-derived the spending deviations and affine
  threshold, reproduced the witness gaps without importing the new checker,
  checked every ticket clause and linked artifact, and resolved two findings:
  the text now separates the earlier \((\alpha,f)\) calibration channel from
  beta's date-three-only channel, and the checker now exercises the diagonal
  \(\beta=0\) reference explicitly. No mathematical finding remains
  unresolved.

## Answer

Put

\[
q=\frac{p_2}{p_1},\qquad h=\frac{p_3}{p_2},\qquad
y=\frac{P}{p_3},\qquad \delta=\frac{1-\lambda}{2},
\]

and let

\[
a=a_2=\frac{1}{1+(f(q)/f(1))^{1-\alpha}}.
\]

The second score is beta-independent because its lagged reference is the
singleton \(R_1=1\). Define the fixed two-date state and the date-three
discretionary interval by

\[
m_2=[\lambda d_2-\delta d_1q]_+,\quad
H_2=\delta d_1+d_2-m_2,\quad C_2=(1-a)H_2,
\]

\[
\kappa_2=[\delta d_1q-\lambda d_2]_++aH_2,\quad
m_3=[\lambda d_3-h\kappa_2]_+,\quad
H_3=C_2+d_3-m_3.
\]

At date three the lagged reference is the first nontrivial two-input value
\(R_2(\beta)=\widehat G_{\alpha,\beta}^{f,\mathrm{out}}(1,q)\), with the
canonical diagonal extension, and

\[
b_\beta=a_3=
\frac{1}{1+\left(f(hq/R_2(\beta))/f(1)\right)^{1-\alpha}}.
\]

Set

\[
c_\beta=(1-b_\beta)H_3,\qquad
g=\delta d_1h(1-q)+C_2(1-h).
\]

Direct cash-inclusive accounting gives the necessary-and-sufficient condition

\[
\boxed{
W_3^S-W_3^{DCA}
=c_\beta(1-y)+gy
=c_\beta-y(c_\beta-g),
}
\]

so the rule beats DCA exactly when \(c_\beta-y(c_\beta-g)>0\). For
\(0<\lambda<1\) and a nonzero deposit triple, \(H_3,c_\beta>0\). Its extended
boundary is

\[
T_\beta=
\begin{cases}
c_\beta/(c_\beta-g),&c_\beta-g>0,\\
+\infty,&c_\beta-g\le0.
\end{cases}
\]

The rule wins below \(T_\beta\), ties at a finite threshold, and loses above
a finite threshold; \(+\infty\) is an all-win slice. At \(\lambda=1\), or
when all deposits are zero, every case ties.

Changing \(\beta\) while holding the two-purchase calibration fixed leaves
\(a,C_2,\kappa_2,m_3,H_3\), and \(g\) unchanged. For two beta values,

\[
\Delta_\beta-\Delta_{\widetilde\beta}
=H_3(b_{\widetilde\beta}-b_\beta)(1-y).
\]

Their classifications differ exactly when \(y\) lies between unequal
extended thresholds, with tie-versus-strict outcomes at finite endpoints.
Such a threshold difference is possible exactly when the third scores differ,
\(g\ne0\), and—when \(g>0\)—the variants are not both already all-win with
\(c\le g\).

An exact witness exists inside the intended countercyclical conditions. Take

\[
\lambda=\frac12,\quad(d_1,d_2,d_3)=(1,1,1),\quad
(p_1,p_2,p_3,P)=\left(1,4,2,\frac73\right),\quad
f(u)=u,\quad\alpha=0.
\]

Both variants first buy \((x_1,x_2)=(3/4,1/4)\). Changing only beta gives

\[
\begin{array}{c|c|c|c|c}
\beta&R_2&b_\beta&T_\beta&W_3^S-W_3^{DCA}\\ \hline
-1&8/5&4/9&25/22&-1/36\\
 1&5/2&5/9&20/17& 1/144.
\end{array}
\]

Thus beta changes a strict DCA loss into a strict win while the entire
two-purchase calibration and state remain fixed.

The complete proof and boundary-equality analysis are in
[Exact three-purchase corrected-mean effect](../../../research/notes/three-purchase-corrected-mean-effect.md);
the canonical statement is
[Three-purchase guarded SmartDCA has an exact beta-sensitive DCA boundary](../../../research/theorems/three-purchase-corrected-mean-effect.md).
The
[verification script](../../../reproducibility/checks/check_three_purchase_corrected_mean_effect.py)
passes 46,656 exact terminal valuations, 7,680 generated boundary ties, and
744 all-win slices, and reproduces the witness fractions directly.

This result proves beta sensitivity, not beta superiority. It ranks no
parameter, fits no data, and makes no arbitrary-horizon or stochastic claim.
