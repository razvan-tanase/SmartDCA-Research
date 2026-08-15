# Primary-source positioning for pathwise DCA dominance

Research date: 2026-08-15

## Bottom line

The reviewed primary sources do **not** state the ticket's exact theorem for a
causal, fully funded, long-only, buy-only strategy with exogenous deposits and a
DCA comparator. The closest exact prior coverage is more general: pointwise
no-arbitrage for predictable self-financing strategies. The DCA, online-portfolio,
and relative-arbitrage papers below are analogies or constructive relaxations,
not substitutes for the ticket's self-contained proof.

The safest positioning is:

> After fixing the exogenous deposit sequence, subtracting DCA from any candidate
> cancels the common cash inflows and produces a zero-initial-cost, predictable,
> self-financing **difference** strategy. Universal weak terminal-wealth dominance,
> with strict inequality on one path, is therefore a one-point arbitrage in the
> terminology of model-free finance.

This reduction is ticket-specific; it is not stated in the cited papers.

## Exact general envelope: pointwise no-arbitrage

Burzoni, Frittelli, Hou, Maggis, and Obłój model a finite-horizon strategy as a
predictable process $H$, with self-financing gain
\(\sum_t H_t\cdot\Delta S_t\). They define a **one-point arbitrage** as a
strategy whose terminal gain is nonnegative on every scenario and strictly
positive on at least one scenario. Their Proposition 2.5 says that no such
arbitrage exists exactly when every scenario is charged by some finite-support
martingale measure ([Burzoni et al. 2019, Definition 2.2 and Proposition
2.5](https://doi.org/10.1287/moor.2018.0956)).

For the ticket's full positive-price path space, the martingale-support condition
can be verified directly. Fix any target path. At each node on it, add one positive
next-price branch on the opposite side of the current price from the target's next
price, choose the two probabilities so their conditional mean is the current
price, and freeze every off-target branch thereafter. Repeating this construction
gives a finite-support martingale measure assigning positive mass to the entire
target path. A flat target step needs no auxiliary branch. Thus every positive
finite path is martingale-supported.

Consequently, once the common deposits are shown to cancel in the accounting,
the general pointwise theorem rules out a payoff difference that is weakly
positive everywhere and positive somewhere. A short direct proof is also
available: under the finite-support martingale charging the alleged strict path,
the nonnegative difference payoff has positive expectation, whereas a predictable
zero-cost self-financing gain has expectation zero.

This is **exact prior coverage after an explicit reduction**, but not direct prior
coverage of the DCA theorem. Two qualifications must remain visible:

- Burzoni et al. allow signed positions. That is sufficient here only because the
  signed object is the difference of two individually feasible portfolios; the
  candidate itself remains long-only and buy-only.
- Their paper has no exogenous-deposit process. The equal-deposit cancellation,
  unused-cash accounting, and purchase/evaluation timing must therefore be proved
  in the ticket's own model.

The same argument yields equality of terminal wealth on every path if weak
dominance is imposed. Identifying the **strategy** with DCA node by node needs a
separate backward/continuation argument: arbitrary future price moves force the
difference holding to vanish at each decision node. The ticket fixes evaluation
after the last purchase date, so its endpoint convention identifies every
purchase. A different model permitting a simultaneous terminal trade would
need to quotient out that terminally neutral allocation.

## Related primary results: analogy only

| Source | What it establishes | Why it does not prove this ticket |
|---|---|---|
| [Cover 1991](https://doi.org/10.1111/j.1467-9965.1991.tb00002.x) | A nonanticipating universal portfolio matches the best constant-rebalanced portfolio in hindsight to first order in exponential growth, path by path. | The guarantee is asymptotic/relative, the comparator is hindsight CRP, and continual rebalancing permits sales; there are no exogenous deposits or exact finite-horizon dominance. |
| [Ordentlich--Cover 1998](https://doi.org/10.1287/moor.23.4.960) | Computes the optimal worst-case finite-horizon wealth ratio of a nonanticipating strategy to the best constant-rebalanced portfolio in hindsight; the unavoidable ratio is below one in nontrivial cases and decays only polynomially. | This quantifies the cost of causality against a different, hindsight comparator. It supports a regret/competitive-ratio relaxation, not exact dominance of DCA. |
| [El-Yaniv et al. 2001](https://doi.org/10.1007/s00453-001-0003-0) | Gives optimal competitive ratios for sequential one-way conversion of a fixed budget under price bounds, a close buy-only online analogue. | It starts with a fixed budget, compares with an offline optimum, assumes bounded rates, and guarantees a factor rather than pathwise domination. |
| [Constantinides 1979](https://doi.org/10.2307/2330513) | Shows classical DCA to be suboptimal relative to optimal sequential and nonsequential policies in a standard portfolio-choice formulation. | Its dominance is model/criterion based and concerns gradual investment of available wealth, not identical exogenous deposits and terminal wealth on every positive path. |
| [Vanduffel et al. 2012](https://doi.org/10.1142/S0219024912500136) | Under Lévy log returns, constructs a static portfolio of path-independent options preferred to DCA by risk-averse decision makers. | The result assumes a return law, uses options, and is preference/stochastic dominance, not stock-and-cash pathwise dominance under the ticket's constraints. |
| [Karatzas--Kim 2020](https://doi.org/10.1007/s00780-019-00414-2) | Constructs probability-free, pathwise portfolios that strongly outperform a market portfolio over suitable horizons under structural conditions on market weights and pathwise variation. | The market comparator, continuous-time rebalancing, and structural path conditions differ. It is evidence that pathwise outperformance becomes possible after restricting the scenario class, not that DCA can be dominated on all positive paths. |

## Safe implications for the paper

The exact result should be presented as a DCA-specific, budget-accounting
specialization of pointwise no-arbitrage, with its elementary proof included.
The defensible constructive relaxations are:

1. restrict the admissible price paths by genuine structural conditions;
2. replace exact dominance by regret, competitive ratio, or asymptotic growth;
3. impose a probabilistic return model and an expected-utility or stochastic-
   dominance criterion; or
4. enlarge the tradable set beyond long-only stock purchases and cash.

These relaxations are materially different. None licenses a claim that a causal,
fully funded SmartDCA rule dominates DCA in terminal wealth on **all** finite
positive paths with the same deposits.

## Search and citation limits

This was a targeted primary-source search, not an exhaustive novelty search. No
direct paper was found combining all of: arbitrary positive finite paths,
arbitrary exogenous deposits, same-deposit DCA, unused cash in terminal wealth,
and a causal long-only buy-only candidate. Absence from the reviewed sources is
not proof of novelty. The bibliographic data and statements above were checked
against publisher pages or author/publisher manuscripts. A July 2026 unrefereed
preprint on pathwise portfolio viability was encountered but is not relied upon.
