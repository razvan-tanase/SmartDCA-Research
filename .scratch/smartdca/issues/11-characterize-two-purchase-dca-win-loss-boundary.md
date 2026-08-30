---
profile: smartdca-okf/0.5
type: research-ticket
title: "Characterize the two-purchase DCA win/loss boundary"
description: "Resolved task ticket characterizing the two-purchase DCA win/loss boundary."
knowledge_role: operational
status: stable
ticket_type: task
ticket_status: resolved
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-16T11:12:00Z
generation_run: urn:uuid:15b108f2-1ab8-4916-965a-89faffe7b3f6
---
# Characterize the two-purchase DCA win/loss boundary

Type: task
Status: resolved
Blocked by: 10, 17
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

For the exact guarded corrected-mean rule fixed in [Choose the guarded corrected-mean SmartDCA score](10-choose-guarded-corrected-mean-score.md), restrict first to
two purchase dates with positive prices \((p_1,p_2)\), nonnegative deposits
\((d_1,d_2)\), and a positive evaluation price \(P\). Derive a necessary and
sufficient condition for

\[
W_2^S>W_2^{DCA},
\]

expressed in the observable price ratios, deposits, safety factor, and the score from
[Choose the guarded corrected-mean SmartDCA score](10-choose-guarded-corrected-mean-score.md). Prove that the strict-win and strict-loss regions are each
nonempty when \(0<\lambda<1\), characterize their boundary and the
\(\lambda=1\) collapse, and determine exactly where the corrected-mean score
changes the result relative to a neutral \(a_t=1/2\) selector. Do not
generalize to arbitrary horizons or make a stochastic claim in this ticket.

## Comments

- Opened after [Choose the guarded corrected-mean SmartDCA score](10-choose-guarded-corrected-mean-score.md) supplied a fully specified causal rule with exact accounting.
- This is the smallest decisive test of whether the corrected-mean discretion creates a mathematically informative strict-improvement region.
- It remains unclaimed until the user passes the significance gate for [Choose the guarded corrected-mean SmartDCA score](10-choose-guarded-corrected-mean-score.md).
- On 2026-08-15 the user paused the research frontier for the repository-root LLM-Wiki sequence; this ticket resumes only after [Clean redundancy after structural freeze](17-clean-redundancy-after-structural-freeze.md) completes.
- Both blockers are now resolved: [Choose the guarded corrected-mean SmartDCA score](10-choose-guarded-corrected-mean-score.md) supplied the rule and [Clean redundancy after structural freeze](17-clean-redundancy-after-structural-freeze.md) closed the wiki sequence on 2026-08-16. The `Blocked by` line above is retained as history, following the convention every resolved ticket in this tracker uses; at that checkpoint this ticket was open, unblocked, and unclaimed pending the user's significance gate.
- Claimed on 2026-08-16 after the user explicitly requested resolution; no other ticket was claimed.
- The exact-rational verifier covers zero and positive deposits, both floor branches, finite and all-win boundaries, generated ties, neutral/countercyclical/momentum selectors, and the \(\lambda=1\) collapse.
- A separate domain-review run re-derived the raw-purchase accounting and threshold ordering, checked every ticket clause and linked artifact, and resolved four findings: the zero-deposit qualification, a circular provenance draft, two stale open-ticket statements, and overview punctuation. No mathematical finding remains unresolved.

## Answer

Write

\[
q=\frac{p_2}{p_1},\qquad y=\frac{P}{p_2},\qquad
\delta=\frac{1-\lambda}{2}.
\]

At date one the rule has \(a_1=1/2\), so
\(x_1=(1-\delta)d_1\), \(C_1=\delta d_1\), and
\(K_1=\delta d_1/p_1\). At date two define

\[
a=a_2(q)=
\frac{1}{1+\left(f(q)/f(1)\right)^{1-\alpha}},
\qquad
H=\delta d_1+d_2-\left[\lambda d_2-\delta d_1q\right]_+.
\]

Here \(H\) is the exact discretionary interval length and terminal cash is
\(c=(1-a)H\). With \(g=\delta d_1(1-q)\), direct cash-inclusive accounting
gives the necessary-and-sufficient condition

\[
\boxed{
W_2^S-W_2^{DCA}
=c(1-y)+gy
=c-y(c-g),
}
\]

so \(W_2^S>W_2^{DCA}\) exactly when \(c-y(c-g)>0\). For
\(0<\lambda<1\) and \(d_1+d_2>0\), \(c>0\). If \(c-g>0\), the exact
boundary is

\[
y=T_a(q):=\frac{c}{c-g};
\]

the guarded rule wins below it, ties on it, and loses above it. If
\(c-g\le0\), every finite \(y>0\) is a strict win on that fixed slice.
Both global strict regions are nonempty for every \(0<\lambda<1\) and every
nonzero deposit pair: set \(q=1\), where \(T_a=1\), and choose respectively
\(y<1\) and \(y>1\). If both deposits are zero, both wealths are identically
zero; this necessary degeneracy qualifies the ticket's nonnegative-deposit
wording.

At \(\lambda=1\), \(\delta=H=c=0\), the two purchases are exactly
\((d_1,d_2)\), and every case ties DCA regardless of the score.

For a neutral selector, replace \(c\) by \(c_0=H/2\) and define the same
extended threshold \(T_0=c_0/(c_0-g)\) when \(c_0-g>0\), otherwise
\(T_0=+\infty\). The score's exact wealth effect is

\[
\Delta_a-\Delta_{1/2}
=H\left(\frac12-a\right)(1-y).
\]

The strict DCA classifications differ exactly when \(y\) lies strictly
between \(T_a\) and \(T_0\), with tie-versus-strict outcomes at finite
endpoints. For nondecreasing \(f\) and \(\alpha\le1\), \(T_a\ge T_0\):
the intended countercyclical score changes a strict result only on
\(T_0<y<T_a\), converting a neutral loss into a win. This is a sign
classification, not dominance over the neutral policy.

The complete proof, strict threshold conditions, limits, and exact examples
are in [Exact two-purchase DCA win/loss boundary](../../../research/notes/two-purchase-dca-win-loss-boundary.md);
the canonical statement is
[Two-purchase guarded SmartDCA has an exact DCA boundary](../../../research/theorems/two-purchase-guarded-smartdca-boundary.md).
The [verification script](../../../reproducibility/checks/check_two_purchase_dca_win_loss_boundary.py)
passes 2,700 exact portfolio cases, 333 generated boundary ties, 1,800 neutral
comparisons, and explicit classification-flip and all-win examples.

The corrected mean itself is not yet tested nontrivially: at date two its
lagged input is the singleton \((1)\), so reflexivity gives \(R_1=1\) and
\(\beta\) disappears. This result is deterministic, two-purchase only, and
makes no stochastic or arbitrary-horizon claim.
