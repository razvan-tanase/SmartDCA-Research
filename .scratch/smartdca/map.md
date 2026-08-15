# Find the rigorous out quasi-Gini route to a complete SmartDCA paper

Label: wayfinder:map

## Destination

A journal-grade, self-contained scientific paper suitable for arXiv and peer review that develops a genuine two-parameter out quasi-Gini mean, derives a sequentially admissible and fully funded SmartDCA rule with exact accounting, establishes the strongest valid comparison with DCA (including an impossibility boundary if universal dominance fails), and supports the theory with reproducible experiments.

## Notes

- The attached source is *SmartDCA superiority* (Calvet, Herranz-Celotti, and Valimamode, arXiv:2308.05200v1), especially Appendix B, Eq. (70).
- The project audits rather than assumes the source paper's claims.
- Only the out construction is in scope.
- Use independent parameters \((\alpha,\beta)\), with \(\alpha=\rho+1\) and \(\beta=\gamma\) when translating the source.
- The abstract theory covers real parameters, the diagonal limiting case, positive external weights, and a general positive increasing transform \(f\); each theorem must state any stronger conditions it needs.
- A corrected family must recover the classical Gini mean when \(f(x)=x\) and the source out quasi-Lehmer mean when \(\alpha-\beta=1\).
- Calling an object a mean requires proof or precise characterization of reflexivity, internality, symmetry, continuity, homogeneity, coordinatewise monotonicity, parameter monotonicity, and limiting behavior.
- The core financial model uses arbitrary finite positive price paths, exogenous deposits, causal information, cash carry without interest, long-only buy-only trades, no leverage, and no spending beyond deposited cash.
- DCA invests every new deposit immediately. Economic dominance compares terminal wealth including unused cash. Average acquisition cost is a structural identity, not by itself proof of superiority.
- Negative and impossibility results are acceptable central contributions.
- Experiments illustrate and stress-test theory; they do not prove universal claims. The eventual workflow is Google Colab-compatible, seeded, provenance-documented, and includes synthetic/adversarial paths plus controlled S&P 500 and Bitcoin source comparisons.
- Execution through a proof-complete manuscript and reproducibility package is part of this map, overriding Wayfinder's planning-only default.
- Every ticket follows the authoritative [Wayfinder ticket workflow](../../docs/agents/wayfinder-ticket-workflow.md): one claimed ticket, evidence-backed resolution, synchronized map, preserved checkpoint, and an explicit user significance gate before the next claim. Parallel work requires explicit approval.
- Consult the research, domain-modeling, PDF, and relevant artifact skills as each ticket requires.

## Decisions so far

- **Source out-functional audit:** Eq. (70) is a mean exactly when \(f=\mathrm{id}\) or \(\alpha-\beta=1\); otherwise it fails reflexivity/internality and has no global finite diagonal limit. See the [audit note](../../research/notes/source-out-quasi-gini-audit.md).
- **Continue after the source audit:** The exact failure classification is significant enough to proceed, subject next to a primary-source novelty check. See [Decide whether the source-audit gap is significant enough to continue](issues/02-assess-source-audit-significance.md).
- **Prior-theory location:** The natural common-weight correction is exactly a weighted Bajraktarević mean. Its \(\alpha-\beta=1\) and power-transform cases are already covered by Beckenbach--Gini--Lehmer and weighted Gini theory. Any contribution must come from transform-coupled theorems, the correction contrast, and the SmartDCA application—not from meanhood itself. See [Locate prior theory for a corrected out quasi-Gini mean](issues/03-locate-prior-theory-for-correction.md).
- **Causal pathwise DCA boundary:** Under the fair same-deposit terminal-wealth comparison, universal weak dominance forces a causal fully funded strategy to be DCA transaction by transaction; no non-DCA strategy can be weakly better on every positive path. Universal dominance becomes constructive only by relaxing causality, while an implementable positive result must restrict the path universe or change the performance criterion. See [Test pathwise DCA dominance under causal budget feasibility](issues/04-test-pathwise-dca-dominance.md).
- **Retrospective source-audit validation:** An independent recheck of the source pages, classification proof, counterexamples, diagonal argument, and original continuation gate passed without changing tickets 01 or 02; it also records that ticket 01 predates the formal workflow. See [Retrospectively validate the source audit and continuation gate](issues/06-retrospectively-validate-source-audit-and-gate.md).
- **Canonical corrected definition:** Among the smallest common-weight repairs, choose the numerator-preserving normalization \(\widehat G_{\alpha,\beta}^{f,\mathrm{out}}=[\sum_iw_ix_if(x_i)^{\alpha-1}/\sum_iw_ix_i^{1-\alpha+\beta}f(x_i)^{\alpha-1}]^{1/(\alpha-\beta)}\), with its function-weighted geometric diagonal. It is a known weighted Bajraktarević mean, preserves weighted Gini and the full out quasi-Lehmer line, and accepts positive external weights. The choice conservatively retains the source's \(\alpha-1=\rho\) score semantics; causality alone does not make it unique, no off-slice acquisition-cost identity is yet established, and it does not evade the causal DCA impossibility boundary. See [Choose the corrected out quasi-Gini definition](issues/05-choose-corrected-out-quasi-gini-definition.md).
- **Homogeneity boundary:** At fixed parameters, the corrected mean is degree-one homogeneous exactly when the transform cancels (\(\alpha=1\), or \(q=1\) on the diagonal) or the positive increasing transform is a power \(f(t)=Ct^r\). Hence one transform makes the entire two-parameter family homogeneous only by reducing it to a reparameterized classical weighted Gini family. See [Characterize homogeneity of the corrected out quasi-Gini mean](issues/07-characterize-homogeneity-of-corrected-out-quasi-gini.md).
- **Pivot to a novelty-first route:** At ticket 07's significance gate, the user chose **Pivot** on 2026-08-15. Generic axiom enumeration is deferred; the active route first audits whether the causal fully funded DCA uniqueness theorem is new and identifies the weakest literature-grounded relaxation that permits a non-DCA constructive result. See [Audit the novelty of the causal DCA boundary and choose a constructive relaxation](issues/08-audit-causal-dca-novelty-and-relaxation.md).
- **Causal-boundary novelty and constructive pivot:** The ticket 04 obstruction is best positioned as a DCA-specific specialization of pointwise no-arbitrage, not a new general impossibility theorem. Retain the unrestricted positive-path and fair-accounting model but relax exact dominance to epsilon-DCA safety; the selected next target is a sharp equivalence between the relative-wealth floor and a causal cumulative-unit guardrail, leaving a discretionary budget for the corrected-mean score. See [Audit the novelty of the causal DCA boundary and choose a constructive relaxation](issues/08-audit-causal-dca-novelty-and-relaxation.md).
- **Sharp epsilon-DCA safety guardrail:** A causal fully funded strategy has a universal \((1-\varepsilon)\)-DCA terminal-wealth floor exactly when its cumulative units cover that fraction of DCA after every history; the equivalent minimum purchase is always feasible and every safe policy is a causal score inside the remaining funded interval. The zero-tolerance boundary uniquely gives DCA, while every positive tolerance admits non-DCA strategies. See [Prove the sharp epsilon-DCA safety guardrail](issues/09-prove-sharp-epsilon-dca-safety-guardrail.md).
- **Canonical guarded corrected-mean score:** Normalize each lagged price history by its first price, compare the current normalized price with the lagged corrected out quasi-Gini mean, and map the normalized source score into purchase odds: \(a_t=[1+(f(r_t)/f(1))^{1-\alpha}]^{-1}\). This is causal, bounded, currency-scale invariant for general positive transforms, neutral on short/constant histories, and countercyclical in the current price for nondecreasing \(f\) and \(\alpha\le1\). Inserted into ticket 09's exact interval, it preserves the epsilon-DCA floor and has complete cash, unit, and average-cost accounting, but no strict DCA improvement is claimed. See [Choose the guarded corrected-mean SmartDCA score](issues/10-choose-guarded-corrected-mean-score.md).

## Not yet specified

- Deferred unless required by the manuscript: the remaining generic axiom and parameter-region theorems after homogeneity.
- The favorable path class, stochastic estimand, or utility objective on which the guarded SmartDCA rule can strictly improve on DCA without weakening its universal safety floor.
- The behavior of the corrected-mean reference under changes in lagged prices outside parameter/transform regions where coordinatewise monotonicity is known.
- The first sharp strict-improvement test is the open two-purchase boundary ticket: [Characterize the two-purchase DCA win/loss boundary](issues/11-characterize-two-purchase-dca-win-loss-boundary.md).
- The research frontier is temporarily paused while [Design a repository-root LLM-Wiki using OKF v0.2](issues/12-design-repository-root-llm-wiki-okf.md) is claimed and resolved; ticket 11 remains open and unmodified until this architecture reaches its significance gate.
- The exact empirical estimands, datasets, transaction-cost assumptions, robustness grid, and statistical reporting protocol.
- The manuscript outline, target venue, literature positioning, proof organization, reproducibility package, and final verification process.

## Out of scope

- The source paper's in quasi-Gini construction.
- Short selling, borrowing, leverage, or future-price information in the implementable strategy.
- Treating stochastic simulations or upward historical trends as proof of the core theorem.
- Treating lower average acquisition cost under unequal spending as economic dominance.
- Presenting an ex-post normalized or unbounded rule as the practical strategy.
