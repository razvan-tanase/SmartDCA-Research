---
profile: smartdca-okf/0.5
type: work-specification
title: "Test arbitrary-horizon guarded SmartDCA performance on single-valley paths"
description: "Approved effort contract for a falsification-oriented arbitrary-horizon performance boundary for the guarded corrected-mean SmartDCA rule."
knowledge_role: operational
status: stable
original_record: true
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-23T21:46:49Z
generation_run: urn:uuid:8e4b4958-2ede-401f-888d-1d3f31b1cdfa
verified:
  - by: openai-codex/writing-for-agents-0.1
    at: 2026-08-23T21:32:48Z
    review_run: urn:uuid:d87a04a7-92ae-43c4-a446-998b6f1a8d14
  - by: human:github:razvan-tanase
    at: 2026-08-23T21:46:49Z
    review_run: urn:uuid:d0e39bb8-dc33-4e02-a42c-71ac62981756
---
# Arbitrary-horizon guarded SmartDCA performance

Approval: approved by the user on 2026-08-23
Parent: [SmartDCA research map](../../map.md)

## Question

For the exact guarded corrected-mean SmartDCA rule, characterize an economically
interpretable class of arbitrary finite price paths on which the discretionary
corrected-mean allocation has a predictable terminal-wealth advantage over DCA
or the neutral guarded selector without weakening epsilon-DCA safety. Begin
with single-valley paths in a restricted countercyclical parameter setting.
Derive the general cash-timing identity, test the proposed cash single-crossing
mechanism with exact-rational counterexample search, and deliver either a sharp
positive theorem or a rigorous negative boundary identifying which additional
conditions are necessary.

## Problem Statement

The project has an arbitrary-horizon safety theorem but only two- and
three-purchase performance characterizations for the guarded corrected-mean
SmartDCA rule. It therefore cannot yet explain when the rule's adaptive
discretionary allocation helps over a realistic investment cycle.

From the user's perspective, this is the missing bridge in a Financial
Computing thesis narrative. The research began by trying to improve DCA,
discovered that exact causal dominance is impossible, and derived a sharp
epsilon-DCA unit guardrail. The next step must show what the adaptive component
contributes beyond that guardrail, or establish a clear boundary showing why an
apparently favorable path class is still insufficient.

The required result applies to every finite horizon in a path class defined
independently of the strategy's realized wealth gap; a four-purchase extension
alone is outside the completion boundary.

## Solution

Build one bounded, falsification-oriented arbitrary-horizon research package.

First, prove the accounting identity for any fully funded strategy:

\[
W_n^S-W_n^{DCA}
=
C_n\left(1-\frac{P}{p_n}\right)
+
P\sum_{t=1}^{n-1}
C_t\left(\frac1{p_{t+1}}-\frac1{p_t}\right).
\]

Then apply the identity both to the guarded corrected-mean SmartDCA rule versus
DCA and to that rule versus a neutral guarded selector that uses the same
epsilon-DCA floor with the constant discretionary score \(1/2\).

Start with finite single-valley purchase-price paths, equal positive deposits,
\(0<\lambda<1\), \(f=\mathrm{id}\), \(\alpha<1\), and parameters in a
coordinatewise-monotone weighted Gini region. State any terminal evaluation
price condition explicitly. Investigate whether the corrected rule carries
more cash before the decline, deploys more cash near the trough, and exhibits a
cash-path single crossing that implies a wealth ordering.

Use exact-rational enumeration at horizons four through eight to falsify the
candidate theorem before attempting a general proof. If the conjecture fails,
minimize the counterexample and refine the path class only with ex ante,
economically interpretable conditions such as a bounded rebound,
reference-crossing behavior, deposit regularity, or a restriction on repeated
floor activation.

The effort is complete with either:

- a necessary-and-sufficient or otherwise sharp arbitrary-horizon theorem on a
  nonempty, independently defined path class; or
- a rigorous negative result showing that the initial single-valley class is
  insufficient, together with an exact counterexample and the sharpest
  independently defined additional condition justified by the investigation.

## Outcome requirements

- Deliver one arbitrary-horizon positive or negative boundary tied to an
  interpretable investment-cycle use case.
- Separate the inherited epsilon-DCA safety guarantee from the performance of
  the discretionary corrected-mean score.
- Compare the corrected rule with both DCA and the neutral guarded selector
  under identical prices, deposits, and evaluation conditions.
- Define every path class and evaluation-price condition independently of the
  resulting terminal-wealth sign.
- Preserve exact counterexamples, deterministic search inputs, proof evidence,
  and independent verification as one reproducible package.
- Express the accepted result as a concise Financial Computing thesis claim,
  with detailed proof machinery remaining in the paper and evidence record.

## User Stories

These approved stories preserve the stakeholder rationale behind the concise
outcomes above. Consult them when interpreting scope, reviewing completeness,
or translating the result into the thesis and defense narrative.

1. As a master's researcher, I want one arbitrary-horizon result, so that the thesis advances beyond finite examples without becoming an open-ended mathematics project.
2. As a master's researcher, I want the result tied to an investment-cycle use case, so that the defense can center on a Financial Computing problem rather than proof technique.
3. As a master's researcher, I want negative findings to count as valid outcomes, so that the work reports discovery honestly instead of forcing a superiority claim.
4. As a thesis committee member, I want the practical question stated before the mathematics, so that I can understand why the theorem matters.
5. As a thesis committee member, I want the safety mechanism separated from the discretionary signal, so that I can distinguish what is guaranteed from what is merely adaptive.
6. As a paper reader, I want an arbitrary-horizon cash-timing identity, so that I can see exactly how delayed investment creates gains or losses relative to DCA.
7. As a paper reader, I want the favorable path class defined independently of terminal performance, so that the theorem is not tautological.
8. As a paper reader, I want every evaluation-price condition stated explicitly, so that the result's economic scope is visible.
9. As a paper reader, I want the corrected rule compared with both DCA and the neutral guarded selector, so that the contribution of the score is not confused with the contribution of the guardrail.
10. As a future researcher, I want exact counterexamples preserved, so that failed conjectures become reusable boundary knowledge.
11. As a future researcher, I want the smallest failed path and parameter configuration, so that I can identify which assumption breaks the conjecture.
12. As a future researcher, I want any refined condition to be economically interpretable, so that later work can connect it to empirical market regimes.
13. As an implementing agent, I want a fixed initial parameter region, so that the first search does not mix transform, monotonicity, and financial questions.
14. As an implementing agent, I want exact-rational calculations, so that classifications near a boundary do not depend on floating-point error.
15. As an implementing agent, I want every guardrail branch exposed in the scenario output, so that floor activation cannot silently explain an apparent score effect.
16. As an implementing agent, I want a deterministic finite search grid, so that another agent can reproduce every candidate and counterexample.
17. As a proof reviewer, I want the general accounting identity verified independently from the strategy formula, so that an allocation bug cannot validate its own theorem.
18. As a proof reviewer, I want constant paths, boundary parameters, ties, and nontrivial examples checked, so that the declared domain is fully covered.
19. As a proof reviewer, I want computational evidence kept separate from proof, so that exhaustive search over a finite grid is not presented as an arbitrary-horizon theorem.
20. As an empirical researcher, I want the surviving theoretical path conditions recorded explicitly, so that a later empirical study can measure how often and how strongly they occur.
21. As an empirical researcher, I want the safety parameter kept visible, so that later experiments can study the trade-off between DCA coverage and adaptive freedom.
22. As a future strategy designer, I want the score's performance compared within the complete safe-policy interface, so that later work can replace the corrected mean without re-proving the guardrail.
23. As a thesis author, I want the final result expressible without detailed proof machinery, so that it can become a clear defense slide while the full proof remains available in the paper.
24. As a thesis author, I want one explicit stopping condition, so that this frontier investigation does not delay the empirical study indefinitely.

## Implementation Decisions

- Inherit the established comparison model: positive finite prices, exogenous deposits, causal long-only buy-only purchases, no leverage, cash carried without interest, and terminal wealth including cash.
- Keep the epsilon-DCA unit guardrail fixed as inherited infrastructure; evaluate only the discretionary allocation.
- Use a weak single-valley definition initially: purchase prices are nonincreasing through one trough and nondecreasing afterward. Record separately whether strict slopes, a genuine decline, or a genuine recovery are needed.
- Prove the arbitrary-horizon cash-timing identity before specializing the strategy. Derive its two-strategy form by replacing cash with the difference between the two strategies' cash paths.
- Compare three policies under identical deposits and prices: DCA, the guarded corrected-mean rule, and the neutral guarded selector with discretionary score \(1/2\).
- Begin with \(f=\mathrm{id}\), equal positive deposits, \(0<\lambda<1\), \(\alpha<1\), and a coordinatewise-monotone weighted Gini parameter region. Defer general transforms and unequal deposits until the restricted question is settled.
- Treat cash-path single crossing around the trough as a conjectured mechanism and require proof before using it in a theorem.
- Search horizons four through eight over a declared finite rational grid before committing to a general proof. Record the grid, enumeration order, and all pruning rules.
- Exercise every reachable guardrail-floor branch and distinguish score effects from floor effects in the result record.
- When the initial conjecture fails, minimize the counterexample lexicographically by horizon, price complexity, parameter complexity, and deposit complexity before proposing a narrower class.
- Admit a narrowing condition only when it is stated using observable price, deposit, reference, or guardrail structure rather than the sign of eventual relative wealth.
- Prefer a necessary-and-sufficient statement. If that is not feasible, require a proved sufficient condition, a proved obstruction showing why it is not necessary, and a nonempty strict region.
- Develop coordinatewise comparative statics of the corrected mean only when the arbitrary-horizon proof requires them; keep generic axiom enumeration deferred.
- Preserve a negative conclusion as a first-class result when single-valley structure is insufficient.
- Record detailed derivations and counterexamples as evidence, extract a concise canonical theorem only after proof and review, and keep operational state in the effort map and tickets.
- Stop this effort after one defensible arbitrary-horizon boundary. Dynamic safety ratchets and optimization over all safe policies require later efforts.

## Testing Decisions

- Use one end-to-end exact-rational scenario engine as the primary verification seam. Given prices, deposits, an evaluation price, the safety factor, and corrected-mean parameters, it must expose purchases, cash, units, floor activation, references, scores, and terminal-wealth gaps for all three policies.
- Test externally visible portfolio identities and classifications rather than helper-function implementation details.
- Reuse the established guardrail, two-purchase, and three-purchase verification behavior as regression prior art.
- Verify the cash-timing identity against direct portfolio accounting for deterministic rational examples across multiple horizons.
- Verify that the arbitrary-horizon engine reproduces the existing two- and three-purchase formulas and their exact win, tie, loss, and beta-flip witnesses.
- Verify both active and inactive guardrail-floor branches, including repeated activation across a path.
- Verify constant prices, a trough at either endpoint, flat segments around the trough, exact ties, zero discretionary interval where reachable, and the \(\lambda=1\) DCA collapse as boundary checks.
- Verify that every generated test path satisfies the declared single-valley predicate independently of the strategy result.
- Verify the corrected and neutral selectors from the same starting ledger and guardrail implementation, while calculating DCA independently.
- Run the exhaustive search with deterministic enumeration and exact rational arithmetic; every reported classification must be independent of random seeds and floating-point tolerances.
- For every counterexample used in the result, replay it as a named regression case and verify every assumption mechanically.
- For every positive theorem, test samples inside, on the boundary of, and outside the claimed class, and keep outside-class failures visible.
- Run an independent mathematical review that re-derives the accounting identity, checks every proof case, and reproduces each exact witness without relying on the producing derivation.
- Run the repository's structural and scientific verification gates after all documentation and evidence are synchronized.

## Out of Scope

- A closed-form boundary for exactly four purchases.
- Universal dominance or guaranteed strict improvement over DCA.
- Claims that increasing \(\beta\) is generally beneficial or that one parameter value is optimal.
- Stochastic outperformance, expected utility, regret, or minimax optimality.
- Historical-market backtesting, transaction costs, taxes, execution slippage, or parameter fitting.
- A general-transform coordinatewise-monotonicity theorem unless it becomes necessary for the restricted financial proof.
- Unequal or stochastic deposits in the first investigation.
- Dynamic or ratcheting DCA safety factors.
- Optimization over the complete class of epsilon-DCA-safe policies.
- Manuscript assembly or the empirical-study protocol.

## Further Notes

This effort is the mathematical bridge in the thesis narrative:

> impossible exact dominance → sharp attainable safety → adaptive guarded rule →
> arbitrary-horizon performance boundary → empirical evaluation.

Either a strict positive result or a rigorous insufficiency result completes
the scientific objective. In the negative branch, identify the exact missing
structure so the boundary remains reusable for the next researcher.

The existing [guardrail theorem](../../../../research/theorems/epsilon-dca-safety-unit-guardrail.md)
already covers every finite horizon. The existing
[three-purchase theorem](../../../../research/theorems/three-purchase-corrected-mean-effect.md)
shows that the corrected mean can change a realized outcome. This effort must
connect those two facts without overstating either one.

The user and verification seam are already agreed: one reproducible
arbitrary-horizon research package must connect the identity, exact-rational
falsification search, final positive or negative theorem, evidence record, and
canonical summary. Completion requires this integrated package.

## Comments

- Synthesized from the thesis-narrative and mathematical-frontier discussion on
  2026-08-23.
- The user confirmed that the previously proposed arbitrary-horizon frontier
  still stands and should now be pursued inside the Financial Computing
  narrative.
- The 24 approved user stories were restored verbatim on 2026-08-24 at the
  user's request after their earlier consolidation-only treatment.
