---
profile: smartdca-okf/0.4
type: research-ticket
title: "Audit the novelty of the causal DCA boundary and choose a constructive relaxation"
description: "Resolved research ticket auditing causal DCA novelty and choosing a constructive relaxation."
knowledge_role: operational
status: stable
ticket_type: research
ticket_status: resolved
---
# Audit the novelty of the causal DCA boundary and choose a constructive relaxation

Type: research
Status: resolved
Blocked by: 04, 07
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

Against primary research on dollar-cost averaging, online portfolio selection, one-way trading, competitive analysis, regret, and pathwise/model-free finance:

1. determine whether ticket 04's theorem is already known, a direct corollary of a known result, or a potentially new theorem in its exact formulation;
2. identify the closest established results and the precise assumptions that separate them from the SmartDCA setting;
3. compare one-assumption relaxations of the impossibility package; and
4. recommend the weakest relaxation that preserves causality, full funding, the same exogenous deposits, and economically fair terminal-wealth accounting while permitting a non-DCA constructive theorem.

This ticket selects and specifies the next theorem target. It does not prove that constructive theorem.

## Comments

- Claimed after the user chose **Pivot** at ticket 07's significance gate on 2026-08-15.
- Generic continuity and axiom-region work is deferred because prior theory makes it a low-novelty route.
- The novelty search must use primary sources and distinguish an exact literature match from a broad no-arbitrage analogy.
- Candidate relaxations must be ordered by which assumption they change; a proposal that silently changes deposits, omits cash, or uses future prices is inadmissible.
- The research workflow delegates one primary-source note. The parent executor will independently review the sources, theorem mapping, and recommendation.
- The parent executor independently checked the equal-flow reduction against ticket 04, verified Burzoni et al.'s definition and martingale-support criterion in the primary paper, checked Pye's DCA-specific minimax assumptions, and re-derived the proposed adversarial continuation and trade-floor algebra. No actionable discrepancy remained after the source note was sharpened.

## Answer

The [primary-source audit](../../../research/notes/ticket-08-causal-dca-novelty-primary-sources.md) supports a conservative verdict: **no exact published statement of ticket 04 was located, but its core impossibility is a direct specialization of pointwise no-arbitrage and should not be claimed as a new general theorem**.

For a fixed common deposit stream, subtracting DCA from the candidate cancels all external cash flows. The difference is a predictable zero-initial-cost self-financing stock-and-cash strategy. Universal nonnegative relative payoff with a strict gain on one path is therefore a one-point arbitrage in the sense of Burzoni et al. Their pointwise fundamental theorem rules this out when every scenario is charged by a finite-support martingale measure; the full finite positive price-path space has that support property. Ticket 04's project-specific residue is the fair recurring-deposit accounting and the sharp equality case showing, by rich adversarial continuations, that payoff equality on all paths forces transaction-by-transaction DCA.

The literature relationships are:

| Primary result | What separates it from ticket 04 |
|---|---|
| Burzoni et al. (2019), pointwise no-arbitrage | Supplies the general corollary envelope after deposit cancellation, but contains no DCA comparator, exogenous-deposit accounting, buy-only candidate, or transaction-level equality statement. |
| Pye (1971), dollar averaging and minimax regret | Closest DCA-specific criterion precedent, but starts with a fixed lump sum, assumes an arithmetic random walk with bounded symmetric moves, and optimizes regret rather than same-deposit terminal wealth. |
| Constantinides (1979) and Vanduffel et al. (2012) | Improve on or compare DCA under stochastic return, utility, preference, or option-market assumptions—not on every path under the ticket's trading constraints. |
| Cover (1991), Ordentlich--Cover (1998), and online portfolio regret | Compete with a hindsight constant-rebalanced portfolio through asymptotic growth or a worst-case wealth ratio; they use a reinvested wealth account and rebalancing rather than recurring deposits and buy-only DCA. |
| El-Yaniv et al. (2001), one-way trading | Close irreversible online-allocation analogy, but uses an initial lump sum, an offline conversion comparator, and price bounds or distributional information. |
| Karatzas--Kim (2020), pathwise relative arbitrage | Positive pathwise outperformance requires structural variation and horizon conditions, uses a market-portfolio comparator, and permits continuous rebalancing. |

### Relaxation choice

One-assumption relaxations are not totally ordered. For this project, “weakest” means retaining the entire arbitrary positive path universe and every operational/accounting condition while changing only the performance threshold by an arbitrarily small amount. On that ordering:

- restricting paths can retain exact dominance, but excludes the adverse continuations that create the impossibility;
- stochastic, expected-utility, or stochastic-dominance objectives add a return law and often preferences or new tradables;
- additive regret is not scale-free on unbounded prices and deposits and therefore also needs normalization or bounds;
- classical competitive ratios normally add price bounds and change the comparator;
- relaxing causality, funding, or cash accounting abandons a core project requirement; and
- an **epsilon-relative DCA floor** changes only exact dominance to
  \[
  W^S\ge (1-\varepsilon)W^{DCA},\qquad 0<\varepsilon<1,
  \]
  for every admissible positive path and deposit sequence, with cash included in both sides.

The epsilon-relative floor is therefore selected. It is scale-free, can approach the impossible boundary arbitrarily closely, and preserves causality, long-only buy-only trading, full funding, the same deposits, the same horizon, and fair terminal wealth. It is a safety guarantee, not dominance.

### Selected next theorem target

The next mathematical ticket should prove the **sharp causal epsilon-DCA safety theorem**, not merely the elementary fixed-sleeve construction. Put \(\lambda=1-\varepsilon\), let \(Q_t^S\) and \(Q_t^{DCA}\) be the candidate's and DCA's cumulative asset units after purchase time \(t\), and let \(x_t\) be the candidate's current purchase from deposit \(d_t\) at price \(p_t\). The target equivalence is

\[
W^S\ge\lambda W^{DCA}\text{ on every positive continuation}
\quad\Longleftrightarrow\quad
Q_t^S\ge\lambda Q_t^{DCA}\text{ after every history}.
\]

Equivalently, a causal policy must obey the local minimum-purchase guardrail

\[
x_t\ge
\left[\lambda d_t-p_t\bigl(Q_{t-1}^S-\lambda Q_{t-1}^{DCA}\bigr)\right]_+.
\]

The theorem should establish necessity by an explicit adverse continuation, sufficiency including carried cash, feasibility of the guardrail under the deposit budget, the \(\varepsilon=0\) reduction to DCA uniqueness, and the discretionary region left when \(\varepsilon>0\). A fixed split—putting \(1-\varepsilon\) of each deposit into DCA and the rest into a causal SmartDCA sleeve—is only a simple sufficient special case. The sharper guardrail lets earlier unit surplus fund later discretion and is the useful interface for the corrected quasi-Gini score.

The source search found no exact primary-source match for this characterization, but that is not proof of novelty. It should initially be positioned as a DCA-specific robust-superhedging characterization. The publishable novelty, if it survives a further citation audit, would need to come from the exact guardrail characterization together with a nontrivial corrected-mean allocation inside its discretionary region and a sharp description of when that allocation beats DCA—not from the epsilon mixture alone.
