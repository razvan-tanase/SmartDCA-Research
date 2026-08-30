# Safety-adaptivity stakeholder requirements

Approval: part of the user-approved empirical effort dated 2026-08-25
Parent: [Safety-adaptivity empirical evaluation](spec.md)

Read these stories when changing effort scope, auditing requirement coverage,
or translating findings into the thesis and defense narrative. Executors use
the [effort specification](spec.md) and their selected ticket for the active
work contract.

## User stories

1. As a master's researcher, I want a preregistered empirical protocol, so that the study cannot quietly adapt its hypotheses after seeing favorable results.
2. As a master's researcher, I want one bounded empirical effort, so that the thesis gains practical evidence without becoming an open-ended backtesting project.
3. As a master's researcher, I want the study organized around the safety-adaptivity trade-off, so that the empirical question follows directly from the mathematical contribution.
4. As a master's researcher, I want negative or null findings preserved, so that the thesis reports discovery honestly rather than forcing a superiority narrative.
5. As a thesis committee member, I want DCA, the neutral guarded selector, and the corrected-mean guarded rule compared side by side, so that I can distinguish the safety architecture from the adaptive signal.
6. As a thesis committee member, I want the guarantee and the observed performance stated separately, so that a historical backtest is not presented as a theorem.
7. As a thesis committee member, I want a simple explanation of what changing \(\lambda\) does, so that I can understand the investor-facing trade-off without following the full proof.
8. As a paper reader, I want primary and secondary estimands declared in advance, so that I can tell which conclusions were confirmatory and which were exploratory.
9. As a paper reader, I want episode construction and evaluation dates declared, so that look-ahead bias and endpoint selection are visible.
10. As a paper reader, I want asset-series semantics declared, so that I know whether dividends, splits, and currency denomination are represented consistently.
11. As a paper reader, I want transaction costs deducted through an explicit accounting rule, so that net results are economically interpretable.
12. As a paper reader, I want gross and net results reported separately, so that transaction costs do not silently alter the scope of the mathematical safety claim.
13. As a paper reader, I want rolling start dates and multiple horizons, so that conclusions do not rest on one hand-picked period.
14. As a paper reader, I want dependence between overlapping windows handled explicitly, so that uncertainty is not understated by treating episodes as independent.
15. As a paper reader, I want corrected-versus-neutral results reported alongside corrected-versus-DCA results, so that the signal's contribution is directly observable.
16. As a paper reader, I want distributions and downside summaries rather than only average returns, so that the practical cost of adaptive freedom is visible.
17. As a future researcher, I want complete run manifests and input fingerprints, so that I can reproduce the exact evidence even if a data provider later changes.
18. As a future researcher, I want raw episode-level outputs preserved, so that I can test new estimands without rerunning or reverse-engineering the original analysis.
19. As a future researcher, I want exploratory findings labeled and retained, so that promising regimes can motivate later mathematical work without being mistaken for confirmed results.
20. As a future strategy designer, I want guardrail activation frequency and size reported, so that I can see whether the safety mechanism materially constrains the selector.
21. As a future strategy designer, I want cash drag and asset exposure measured, so that I can understand the mechanism behind gains and losses.
22. As a future strategy designer, I want the terminal cash/unit attribution reported for every policy comparison, so that final wealth gaps connect to the accepted arbitrary-horizon boundary.
23. As an empirical researcher, I want deterministic synthetic paths, so that known edge cases and theorem boundaries remain interpretable.
24. As an empirical researcher, I want deliberately hostile paths, so that implementation failures and asymmetric downside are exposed before historical evaluation.
25. As an empirical researcher, I want seeded stochastic path families, so that sensitivity to controlled regimes can be reproduced exactly.
26. As an empirical researcher, I want constant, monotone, single-valley, multiple-valley, crash, and rebound families, so that the study remains connected to the completed mathematical investigation.
27. As an empirical researcher, I want the historical datasets selected by rule rather than outcome, so that market choice does not become another source of data snooping.
28. As an empirical researcher, I want parameter selection separated from evaluation, so that the corrected-mean rule is not tuned on its reported test episodes.
29. As an empirical researcher, I want robustness grids distinguished from primary configurations, so that multiple comparisons do not masquerade as one predeclared test.
30. As an implementing agent, I want one public experiment-runner interface, so that configuration, execution, validation, and output production share one reproducible seam.
31. As an implementing agent, I want every policy to receive the same prices, deposits, dates, costs, and evaluation point, so that comparisons are fair by construction.
32. As an implementing agent, I want DCA calculated independently from the guarded-policy implementation, so that a shared bug cannot validate all policies simultaneously.
33. As an implementing agent, I want the two guarded policies to share the exact guardrail contract, so that their difference isolates the selector rather than infrastructure drift.
34. As an implementing agent, I want each ledger to expose deposits, purchases, fees, cash, units, references, scores, and floor activation, so that every aggregate can be audited back to decisions.
35. As an implementing agent, I want deterministic configuration validation, so that invalid horizons, unavailable prices, ambiguous timings, and unsupported parameters fail before execution.
36. As an implementing agent, I want resumable runs with immutable identities, so that a long study can recover safely without mixing outputs from different configurations.
37. As a proof reviewer, I want frictionless episode ledgers checked against the epsilon-DCA unit-coverage condition, so that empirical code does not contradict the proved safety theorem.
38. As a proof reviewer, I want the terminal wealth gap reconciled with the terminal cash/unit identity, so that performance attribution is independently verified.
39. As a statistical reviewer, I want uncertainty intervals and dependence assumptions declared, so that descriptive differences are not overstated as precise population effects.
40. As a statistical reviewer, I want failure cases, missing data, and excluded episodes reported, so that the effective sample is transparent.
41. As a statistical reviewer, I want primary multiplicity controlled or explicitly bounded, so that a large parameter grid does not inflate apparent evidence.
42. As a reproducibility reviewer, I want one clean-environment command or notebook route, so that the complete report can be regenerated without hidden manual steps.
43. As a reproducibility reviewer, I want code version, dependency versions, seeds, and data receipts recorded, so that the run is computationally identifiable.
44. As a thesis author, I want figure-ready data generated from the same reviewed outputs as the tables, so that the defense does not depend on manually transcribed numbers.
45. As a thesis author, I want one concise empirical conclusion for each policy comparison, so that the defense can explain both the guardrail's cost and the selector's incremental value.
46. As a thesis author, I want limitations stated beside the findings, so that the final narrative remains credible under questioning.
