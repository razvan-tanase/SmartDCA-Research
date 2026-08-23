---
profile: smartdca-okf/0.4
type: research-ticket
title: "Test pathwise DCA dominance under causal budget feasibility"
description: "Resolved research ticket testing pathwise DCA dominance under causal budget feasibility."
knowledge_role: operational
status: stable
ticket_type: research
ticket_status: resolved
---
# Test pathwise DCA dominance under causal budget feasibility

Type: research
Status: resolved
Blocked by: 02
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

Prove or refute whether any non-DCA sequentially admissible, long-only, buy-only, fully funded strategy can economically dominate DCA in terminal wealth for every finite positive price path and exogenous deposit sequence. If universal dominance is impossible, characterize the equality case and the precise assumption that must be relaxed for a constructive result.

## Comments

- Claimed after tickets 01--03 were resolved and the user explicitly continued to ticket-04.
- Keep the comparator economically fair: same exogenous deposits and horizon, with unused cash included in terminal wealth.
- Verified the terminal-wealth identity on 64 feasible schedules, 108 one-date adversarial completions, 1,548 deviations after arbitrary DCA prefixes, 2,916 future-min oracle cases, and 1,080 nonincreasing-path cases.

## Answer

Universal non-DCA dominance is impossible. For any fixed finite horizon, if a
causal, long-only, buy-only, fully funded strategy has terminal wealth at least
that of DCA for every positive price path and every exogenous deposit sequence,
then after every history it must spend exactly the current deposit, carry zero
cash, and hold exactly the DCA units. Hence it is DCA transaction by transaction
and equality holds on every path; strict improvement anywhere is impossible.

The proof is an adversarial-continuation induction. If the strategy leaves
residual cash \(r>0\) after any purchase date with current price \(p_t\), choose
all later purchase prices and the evaluation price equal to a finite
\(M>p_t\). Later trading at \(M\) is terminal-value neutral, while the missed
units create the strictly negative gap
\(r(1-M/p_t)\).

For a single realized path, equality is broader and holds exactly when

\[
\sum_t(d_t-x_t)\left(1-\frac{p_{n+1}}{p_t}\right)=0.
\]

For horizons with at least two purchase dates, if dominance on **every** path is
retained, causality must be relaxed: a future-minimum oracle is fully funded and
pathwise dominates DCA. (With one purchase date it coincides with DCA.) If
causality, equal funding, and the terminal-wealth comparator are retained, the
universal path quantifier must instead be relaxed to an explicit path class or
probabilistic/performance criterion. Full definitions, proof, equality cases,
sharp relaxations, and reproducible finite checks are in the
[research note](../../../research/notes/pathwise-dca-dominance-under-causal-budget.md) and its
[verification script](../../../reproducibility/checks/check_pathwise_dca_dominance.py). The
[primary-source positioning note](../../../research/notes/pathwise-dca-dominance-primary-sources.md)
shows how the result reduces to pointwise no-arbitrage while separating exact
prior coverage from online-portfolio and DCA analogies.
