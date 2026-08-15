# Prove the sharp epsilon-DCA safety guardrail

Type: task
Status: resolved
Blocked by: 04, 08
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

In the project's arbitrary finite positive-price, exogenous-deposit model, let
\(\lambda=1-\varepsilon\in(0,1]\). Prove or refute that a causal, long-only,
buy-only, fully funded strategy satisfies

\[
W^S\ge \lambda W^{DCA}
\]

for every positive price path and deposit sequence if and only if, after every
purchase history,

\[
Q_t^S\ge \lambda Q_t^{DCA}.
\]

If true, derive the equivalent local minimum-purchase guardrail, prove that it
is always budget-feasible, characterize its discretionary region, recover DCA
uniqueness at \(\lambda=1\), give at least one non-DCA construction for
\(0<\lambda<1\), and determine sharpness of the terminal-wealth factor. State
all horizon and deposit assumptions precisely and include cash in terminal
wealth.

## Comments

- Claimed after the user chose **Continue** at ticket 08's significance gate on 2026-08-15.
- This is a mathematical task, not a new literature search. Ticket 08 already records the primary-source positioning and novelty limits.
- The proof must test zero deposits, one purchase date, constant prices, extreme evaluation prices, \(\lambda=1\), \(\lambda\downarrow0\), and a nontrivial multi-date example.
- Detailed proof and reproducible finite/adversarial checks should live in a linked theorem note and verification script; the ticket answer should remain a concise resolution.
- Domain-specific review re-derived the sufficiency and adverse-continuation directions, checked the cash-inclusive accounting, and tested the local algebra separately. The first exhaustive run exposed that minimum-purchase feasibility must be asserted only along previously covered histories; the test was corrected, while the theorem already had that hypothesis. No mathematical finding remained unresolved.

## Answer

The equivalence is true. The complete statement and proof are in [Sharp causal epsilon-DCA safety and its unit-coverage guardrail](../../../research/notes/sharp-epsilon-dca-safety-guardrail.md).

For \(\lambda=1-\varepsilon\in(0,1]\), a causal, long-only, buy-only, fully funded strategy satisfies \(W^S\ge\lambda W^{DCA}\) on every finite positive price path and nonnegative deposit sequence **if and only if**

\[
Q_t^S\ge\lambda Q_t^{DCA}
\]

after every reachable purchase history. A prefix unit deficit is fatal: setting later purchase prices to \(P^2\) and the evaluation price to \(P\) makes all finite future cash and purchases negligible relative to the deficit as finite \(P\) becomes large.

The prefix condition is equivalent to the sharp local floor

\[
m_t(\lambda)=
\left[\lambda d_t-p_t\bigl(Q_{t-1}^S-\lambda Q_{t-1}^{DCA}\bigr)\right]_+,
\qquad
x_t\in[m_t(\lambda),C_{t-1}+d_t].
\]

Along every covered history, \(m_t(\lambda)\le\lambda d_t\le d_t\), so the floor is always budget-feasible. Every safe strategy, and only a safe strategy, is obtained by choosing a causal score \(a_t\in[0,1]\) and setting

\[
x_t=m_t+a_t(C_{t-1}+d_t-m_t).
\]

The strategy's exact worst-case terminal-wealth factor is the infimum, over all reachable nonzero-deposit prefixes, of \(Q_t^S/Q_t^{DCA}\). At \(\lambda=1\), funding and the guardrail force \(x_t=d_t\) inductively, recovering unique DCA. For every \(0<\lambda<1\), the non-DCA rule \(x_t=\lambda d_t\) is exactly \(\lambda\)-safe, beats DCA on paths where DCA's terminal wealth is below nominal deposits, and has no larger uniform factor. The \(\lambda\downarrow0\) limit is the vacuous nonnegative-wealth guarantee.

The [verification script](../../../reproducibility/checks/check_epsilon_dca_safety_guardrail.py) passed exact rational checks over 12,357 feasible schedules, 55,959 terminal-floor cases, 64,613 adverse-prefix cases, 1,485 constant-price cases, and 9,828 construction cases, including both strict wins and strict losses relative to DCA.

This is a sharp constructive bridge, but not yet a complete SmartDCA result: the corrected quasi-Gini score must next be mapped into \(a_t\), and its strict-improvement region must still be proved. The theorem retains ticket 08's conservative novelty position as a DCA-specific robust-superhedging characterization rather than claiming a new general principle.
