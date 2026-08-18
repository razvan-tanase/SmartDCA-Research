---
profile: smartdca-okf/0.3
type: theorem
title: "Two-purchase guarded SmartDCA has an exact DCA boundary"
description: "The two-purchase guarded rule beats DCA exactly below an explicit affine evaluation-price boundary, with a sharp neutral-score comparison."
knowledge_role: canonical
status: stable
sources:
  - id: boundary-note
    title: "Exact two-purchase DCA win/loss boundary"
    resource: research/notes/two-purchase-dca-win-loss-boundary
    source_kind: internal
  - id: ticket-11
    title: "Characterize the two-purchase DCA win/loss boundary"
    resource: .scratch/smartdca/issues/11-characterize-two-purchase-dca-win-loss-boundary
    source_kind: internal
  - id: guarded-rule
    title: "The guarded corrected-mean SmartDCA rule"
    resource: research/definitions/guarded-corrected-mean-smartdca-rule
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
# Two-purchase guarded SmartDCA has an exact DCA boundary

## Statement

Apply [the guarded corrected-mean SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md) at exactly two purchase dates, with positive prices \((p_1,p_2)\), nonnegative deposits \((d_1,d_2)\), positive evaluation price \(P\), and safety factor \(0<\lambda\le1\). Set[^guarded-rule]

\[
q=\frac{p_2}{p_1},\qquad y=\frac{P}{p_2},\qquad
\delta=\frac{1-\lambda}{2},
\]

\[
a(q)=\frac{1}{1+\left(f(q)/f(1)\right)^{1-\alpha}},
\qquad
H(q)=\delta d_1+d_2-\left[\lambda d_2-\delta d_1q\right]_+,
\]

and \(c=(1-a)H\), \(g=\delta d_1(1-q)\). Then the terminal-wealth gap is exactly[^boundary-note]

\[
\boxed{W_2^S-W_2^{DCA}=c(1-y)+gy=c-y(c-g).}
\]

Provided \(0<\lambda<1\) and \(d_1+d_2>0\), one has \(c>0\).
If \(c-g>0\), the rule wins exactly when
\(0<y<c/(c-g)\), ties at equality, and loses above it. If
\(c-g\le0\), it wins for every finite \(y>0\). This is necessary and
sufficient, not merely a sufficient path condition.[^ticket-11]

For every \(0<\lambda<1\) and \(d_1+d_2>0\), both global strict regions are
nonempty: at \(q=1\) the boundary is \(y=1\). If both deposits are zero,
both wealths are identically zero. At \(\lambda=1\), the discretionary
interval collapses, the rule is DCA at both dates, and every case ties.[^boundary-note]

## Neutral-selector comparison

Continue to assume \(0<\lambda<1\) and \(d_1+d_2>0\).
For a selector \(s\in\{a,1/2\}\), put \(c_s=(1-s)H\) and define its
extended boundary

\[
T_s=\begin{cases}
c_s/(c_s-g),&c_s-g>0,\\
+\infty,&c_s-g\le0.
\end{cases}
\]

The corrected and neutral selectors have opposite strict DCA signs exactly
when \(y\) lies strictly between \(T_a\) and \(T_{1/2}\); at a finite
endpoint one ties while the other is strict. Their gap difference is

\[
\Delta_a-\Delta_{1/2}
=H\left(\frac12-a\right)(1-y).
\]

When \(f\) is nondecreasing and \(\alpha\le1\),
\(T_a\ge T_{1/2}\). Thus the intended countercyclical score changes a strict
classification only on \(T_{1/2}<y<T_a\), where it converts a neutral loss
into a win; it never converts a neutral win into a loss. This statement is
only about the DCA sign classification and is not dominance over the neutral
policy.[^boundary-note]

## Sharpness and scope

The two-purchase boundary is affine in the evaluation ratio and all cases in
the statement occur. It is deterministic and makes no stochastic or
arbitrary-horizon claim. At date two the lagged corrected-mean input is the
singleton \((1)\), so reflexivity forces its reference to \(1\) and \(\beta\)
drops out. The result therefore tests the guarded score calibration, not a
nontrivial multi-input corrected-mean reference; \(\beta\) can first affect a
purchase at date three.[^boundary-note]

The complete derivation, boundary cases, strict threshold conditions, and
exact examples are in [the evidence note](../notes/two-purchase-dca-win-loss-boundary.md).[^boundary-note]
The executable check is
[`check_two_purchase_dca_win_loss_boundary.py`](../../reproducibility/checks/check_two_purchase_dca_win_loss_boundary.py).

[^boundary-note]: [Exact two-purchase DCA win/loss boundary](../notes/two-purchase-dca-win-loss-boundary.md)
[^ticket-11]: [Characterize the two-purchase DCA win/loss boundary](../../.scratch/smartdca/issues/11-characterize-two-purchase-dca-win-loss-boundary.md)
[^guarded-rule]: [The guarded corrected-mean SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md)
