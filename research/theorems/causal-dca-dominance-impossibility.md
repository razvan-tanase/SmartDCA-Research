# Causal DCA dominance impossibility

## Statement

The model fixed in this section is the canonical statement of the project's fair comparison
model, and every other financial concept inherits it by reference:
[the epsilon-DCA guardrail theorem](epsilon-dca-safety-unit-guardrail.md),
[the guarded SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md), and the
three evidence notes behind them all point here rather than defining a model of their own.
The notes restate the recursions locally because their proofs argue from them.

Fix a horizon \(n\ge1\) with purchase dates \(t=1,\ldots,n\) and a common evaluation price \(p_{n+1}>0\). Let \(S\) be any causal, long-only, buy-only, fully funded strategy: it chooses \(x_t\in[0,C_{t-1}+d_t]\) from the history through date \(t\), cash carries without interest, and terminal wealth is \(W^S=C_n+p_{n+1}Q_n\), including unused cash. If

\[
W^S(p,d)\ge W^{D}(p,d)
\]

for **every** \(p\in(0,\infty)^{n+1}\) and every \(d\in[0,\infty)^n\), then after every history \(x_t=d_t\), \(C_t=0\), and \(Q_t=\sum_{i\le t}d_i/p_i\).[^causal-boundary]

That is, \(S\) is DCA transaction by transaction and \(W^S=W^{D}\) on every path. No economically distinct causal fully funded strategy achieves economic dominance.

## Sharpness

The theorem is sharp as a package: the five assumptions — every finite positive price path, causal decisions, the same exogenous deposits and horizon, no borrowing, and terminal wealth including cash — cannot all be kept while obtaining a nontrivial positive result, and relaxing exactly one of them suffices.[^causal-boundary]

- **Relax causality**, keep every path: for \(n\ge2\) an oracle assigning each deposit to a later date attaining the running minimum price weakly dominates DCA everywhere and strictly somewhere. For \(n=1\) it collapses to DCA.
- **Relax the path universe**, keep implementability: on nonincreasing paths with \(n\ge2\), carrying all cash and buying at the last date weakly dominates DCA and is strict whenever a positive deposit arrives above the final price.

The obstruction is informational and budgetary, not a property of any mean: after any causal decision to leave part of the available deposit uninvested, an admissible continuation can raise the price and hold it there, and the missed units are unrecoverable. The strategy may even be given the entire future *deposit* schedule; only future prices are withheld. The argument also covers randomized strategies, per realized seed or in expectation.[^causal-boundary]

## What it does not establish

It is **not** the claim that DCA is optimal on each realized path, nor that no strategy can ever beat DCA. Path-specific equality is characterized exactly by the accounting identity \(W^S-W^{D}=\sum_t(d_t-x_t)\bigl(1-p_{n+1}/p_t\bigr)\), which many schedules satisfy — flat prices being the obvious case — so path coincidences must not be mistaken for a universal alternative.[^causal-boundary]

It is also not positioned as a new general impossibility theorem. It is best read as a DCA-specific specialization of pointwise no-arbitrage: exact general coverage here is distinct from the regret, competitive-ratio, stochastic, and restricted-path analogies in the literature.[^positioning][^novelty] The constructive route this project actually took was to keep the unrestricted path universe and fair accounting and instead weaken exact dominance, which yields [the epsilon-DCA safety guardrail](epsilon-dca-safety-unit-guardrail.md).[^novelty]

Finally, it bears on the source paper's claim only through the criterion: the paper proves statements about price per unit under unequal spending, and this theorem is about terminal wealth under a common deposit sequence. Lower average acquisition cost remains an accounting property.

The proof by induction, the exact terminal-wealth identity, the two relaxations, and the numerical boundary checks are in [the causal-boundary note](../notes/pathwise-dca-dominance-under-causal-budget.md),[^causal-boundary] resolved under [its ticket](../../.scratch/smartdca/issues/04-test-pathwise-dca-dominance.md).[^ticket-04] The executable check is [`check_pathwise_dca_dominance.py`](../../reproducibility/checks/check_pathwise_dca_dominance.py).

[^causal-boundary]: [Pathwise DCA dominance under causal budget feasibility](../notes/pathwise-dca-dominance-under-causal-budget.md)
[^ticket-04]: [Test pathwise DCA dominance under causal budget feasibility](../../.scratch/smartdca/issues/04-test-pathwise-dca-dominance.md)
[^novelty]: [Primary-source audit of the causal DCA boundary and constructive relaxations](../notes/ticket-08-causal-dca-novelty-primary-sources.md)
[^positioning]: [Primary-source positioning for pathwise DCA dominance](../notes/pathwise-dca-dominance-primary-sources.md)
