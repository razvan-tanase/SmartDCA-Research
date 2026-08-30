# Safety-adaptivity empirical evaluation

Approval: approved by the user through `@To Spec` on 2026-08-25
Parent: [SmartDCA research map](../../map.md)

## Question

Across synthetic, adversarial, and historical recurring-investment episodes,
what realized performance is obtained at different guaranteed DCA coverage
levels, and how much of that performance comes from the corrected-mean signal
rather than from the epsilon-DCA unit guardrail?

## Problem Statement

The project now has a coherent mathematical foundation. Exact causal dominance
over DCA is impossible for an economically distinct fully funded strategy; the
epsilon-DCA unit guardrail gives the sharp attainable model-free safety floor;
and the arbitrary-horizon terminal-inventory boundary explains every realized
wealth gap through terminal cash and asset-unit differences. The completed
single-valley investigation also shows that intuitive price geometry and cash
single crossing alone do not justify a predictable advantage for the guarded
corrected-mean SmartDCA rule.

What remains unknown is the practical value of the adaptive freedom left by
the guardrail. The current reproducibility programs verify mathematics; they do
not estimate realized performance on declared investment episodes. The project
therefore cannot yet answer how the safety factor changes cash drag, exposure,
relative downside, or upside; whether the corrected-mean selector adds value
beyond a neutral selector using the same safety architecture; how results vary
across market regimes and horizons; or how transaction costs affect conclusions
that are exact only in the frictionless model.

From the user's perspective, this is the empirical bridge required by the
Financial Computing thesis narrative. The study must evaluate a working causal
investment algorithm without converting historical wins into universal claims,
without selecting parameters on test outcomes, and without confusing the
guardrail's theorem with the corrected-mean signal's observed performance.

## Solution

Build one preregistered, reproducible empirical research package around the
settled three-policy comparison:

1. the DCA comparator, which invests each deposit immediately;
2. the neutral guarded selector, which uses the epsilon-DCA unit guardrail and
   allocates the funded discretionary interval with score \(1/2\); and
3. the guarded corrected-mean SmartDCA rule, which uses the same guardrail and
   applies the corrected-mean score only to the funded discretionary interval.

Freeze an empirical protocol before inspecting confirmatory historical results.
The protocol must declare data sources and fingerprints, asset-series semantics,
episode construction, deposit timing, evaluation timing, horizons, the DCA
coverage grid, corrected-mean parameter selection, transaction-cost scenarios,
missing-data handling, primary and secondary estimands, uncertainty methods,
and the boundary between confirmatory analysis and exploratory robustness work.

Use a single highest-level experiment-runner seam. Given an immutable study
configuration and versioned inputs, one run must execute all three policies
under identical observable information and economic conditions, then emit a
manifest, complete ledgers, validation results, episode-level estimands,
aggregates, tables, and figure-ready data. DCA accounting must remain
independent of the two guarded policies, while the guarded policies must share
the same guardrail contract so their difference isolates the selector.

Evaluate three evidence layers:

- **Deterministic synthetic and adversarial paths:** constant markets,
  monotone rises and declines, weak and strict single valleys, incomplete and
  completed recoveries, multiple valleys, crashes, sudden rebounds, prolonged
  drawdowns, flat segments, and paths deliberately hostile to carried cash or
  adaptive timing.
- **Seeded stochastic synthetic families:** declared regime, trend,
  mean-reversion, jump, and volatility constructions used for controlled
  sensitivity rather than proof.
- **Historical recurring-investment episodes:** rolling, point-in-time-valid
  episodes for a declared S&P 500 investable or total-return proxy and a
  declared Bitcoin/USD spot series, with data provenance and overlapping-window
  dependence handled explicitly.

For every episode and coverage level, report the complete-system comparison
against DCA and the signal-only comparison against the neutral guarded selector.
Attribute terminal performance using the accepted terminal cash/unit boundary,
and report cash holdings, asset exposure, guardrail activation, purchases,
references, and discretionary scores so an observed result can be explained
from the ledger rather than only from a final return.

The effort is complete when a fresh environment can reproduce one reviewed
experiment report, its declared datasets or retrieval receipts, immutable
configurations, raw episode results, aggregate tables, and figure-ready outputs;
every primary conclusion is traceable to a preregistered estimand; gross
frictionless safety is verified separately from net-of-cost performance; and
the interpretation states what the evidence does and does not establish.

## Outcome requirements

- Quantify the realized safety-adaptivity trade-off across a predeclared grid of
  \(\lambda=1-\varepsilon\) values, including the \(\lambda=1\) DCA collapse.
- Separate complete-system performance from corrected-mean signal contribution
  by comparing all three policies under identical conditions.
- Preserve the theorem-consistent frictionless ledger as the safety audit and
  report transaction-cost results as empirical net performance, not as covered
  by the existing epsilon-DCA theorem.
- Use rolling historical episodes and controlled synthetic/adversarial paths so
  conclusions do not depend on one favorable starting date or one market shape.
- Freeze confirmatory hypotheses, configurations, parameter rules, datasets,
  estimands, and uncertainty methods before reading confirmatory outcomes.
- Make every reported number reproducible from a versioned run manifest and a
  complete observable ledger.
- Explain relative performance through terminal cash, terminal asset-unit
  difference, cash drag, exposure, and guardrail activation rather than through
  win rates alone.
- Deliver a conservative thesis claim that connects the impossibility result,
  sharp guardrail, arbitrary-horizon boundary, and empirical evidence without
  claiming universal or causal market superiority.

## Stakeholder requirements

The 46 approved user stories live in [the stakeholder-requirements
reference](stakeholder-requirements.md). Read them when changing scope,
auditing requirement coverage, or translating findings into the thesis and
defense narrative. Ticket execution is governed by this specification's
decisions and the selected ticket's acceptance criteria.

## Implementation Decisions

- Inherit the settled financial model for the theorem-consistent baseline: finite positive prices, exogenous deposits, causal long-only buy-only purchases, no leverage, cash carried without interest, and terminal wealth including cash.
- Use exactly three primary policies: DCA, the neutral guarded selector with discretionary score \(1/2\), and the guarded corrected-mean SmartDCA rule. Run them on identical episode inputs.
- Treat \(\lambda=1-\varepsilon\) as the experimental safety-control variable. The preregistered grid must include \(\lambda=1\), several values close to one, and lower-coverage values that expose the adaptivity curve; exact grid values are frozen before confirmatory outcomes are read.
- Keep the epsilon-DCA unit guardrail unchanged in the primary analysis. Any altered or dynamic guardrail is a different policy and requires a later effort.
- Use one public experiment-runner contract accepting a validated immutable configuration plus versioned datasets and producing a run identity, manifest, policy ledgers, validation receipts, episode estimands, aggregate summaries, tables, and figure-ready data.
- Reuse the accepted arbitrary-horizon ledger semantics and terminal cash/unit attribution. Extend the computational layer only where empirical dates, batches, costs, and datasets require it.
- Calculate DCA through an accounting route independent of the guarded selectors. Calculate the corrected and neutral selectors through the same guardrail interface and distinguish them only at the discretionary-score interface.
- Define the primary observation as one recurring-investment episode with a declared deposit schedule, purchase timestamps, horizon, and evaluation timestamp. Each policy sees only information available at each purchase timestamp.
- Freeze the primary deposit cadence, episode horizons, evaluation convention, and rolling-window stride before confirmatory execution. Secondary schedules and horizons are labeled robustness analyses.
- Use a declared S&P 500 investable or total-return proxy and a declared Bitcoin/USD spot series. Record the exact provider, series identifier, timezone, adjustment semantics, retrieval timestamp, license or redistribution constraint, and content fingerprint.
- Use point-in-time-valid prices. Missing observations follow one preregistered market-calendar and carry/skip rule shared by all policies; the engine never silently interpolates.
- Separate deterministic adversarial families, seeded stochastic synthetic families, and historical episodes in both configuration and reporting. Synthetic evidence stress-tests mechanisms; historical evidence estimates realized behavior; neither proves universal performance.
- Freeze corrected-mean primary configurations using theoretical admissibility and information available before confirmatory evaluation. Do not choose \(\alpha\), \(\beta\), transforms, or weights from confirmatory test outcomes.
- Keep exploratory parameter grids separate from primary configurations. Record the full attempted grid, all outcomes, and the multiplicity policy; never report only the best parameter.
- Use a zero-cost frictionless baseline to audit the proved guardrail. Add predeclared proportional or fixed cost scenarios symmetrically through each policy's purchase ledger and report them as net empirical results outside the theorem's current scope.
- Report complete-system performance as guarded corrected-mean versus DCA, signal contribution as guarded corrected-mean versus neutral guarded, and safety-architecture behavior as neutral guarded versus DCA.
- Use relative terminal-wealth gaps and ratios as primary economic outcomes. Add downside quantiles, worst relative shortfall, cash drag, asset exposure, guardrail activation, turnover or purchase count, and terminal cash/unit components as mechanism and risk outcomes.
- Report win rates only as descriptive complements. Do not use them as substitutes for effect sizes, distributions, or downside analysis.
- Declare how overlapping historical episodes affect inference. Use a dependence-aware interval method such as calendar-block resampling or a justified alternative, with block construction frozen before confirmatory reporting.
- Distinguish confirmatory hypotheses, secondary analyses, robustness checks, and exploratory regime mining in both outputs and prose.
- Preserve every excluded or failed episode with a machine-readable reason. Do not silently drop invalid configurations, missing data, numerical failures, or safety-check failures.
- Generate all manuscript tables and figure-ready data from reviewed run outputs. Manual spreadsheet transcription is not an authoritative computation path.
- Keep detailed run evidence in experiment reports and machine-readable artifacts; later canonical or manuscript claims must link back to the reviewed report.

## Testing Decisions

- Use the complete study run as the highest verification seam: one immutable configuration and its input receipts must regenerate policy ledgers, episode estimands, aggregates, and report assets with the same run identity.
- Test externally observable investment behavior and accounting invariants rather than helper-function implementation details.
- Reuse the existing exact-rational arbitrary-horizon scenario engine as mathematical regression prior art. The empirical runner must reproduce its named two-purchase, three-purchase, constant-path, and repeated-floor-activation cases in frictionless mode.
- Verify that DCA invests each eligible deposit at the declared purchase time and that its terminal wealth is computed from an accounting implementation independent of the guarded policies.
- Verify after every frictionless purchase that each guarded policy is fully funded, long-only, buy-only, causal, and satisfies the epsilon-DCA unit-coverage condition for its configured \(\lambda\).
- Verify that \(\lambda=1\) collapses both guarded policies transaction by transaction to DCA, not merely to equal terminal wealth.
- Verify the complete-system, signal-only, and architecture-only terminal wealth gaps by direct portfolio subtraction and by the accepted terminal cash/unit boundary.
- Verify that corrected and neutral runs share deposits, prices, costs, timing, evaluation points, and guardrail floors before their selector difference is accepted.
- Verify cost accounting through named zero-cost, proportional-cost, fixed-cost, small-cash, and zero-purchase-boundary cases. A net-of-cost safety violation must be reported as outside the existing theorem, not hidden or relabeled.
- Verify deterministic path predicates independently of policy outcomes for constant, monotone, single-valley, multiple-valley, crash, rebound, and hostile families.
- Verify that every stochastic generator is fully determined by its saved family parameters and seed, and that repeating a run produces identical paths and outputs.
- Verify market-calendar alignment, timezone normalization, adjusted-price semantics, missing-observation handling, deposit-date mapping, and evaluation-date mapping with small hand-checkable fixtures.
- Verify that a policy cannot read future observations by testing truncated prefixes and confirming identical decisions through the shared prefix.
- Verify configuration rejection for nonpositive prices, invalid coverage levels, ambiguous or reversed dates, unavailable horizon endpoints, unsupported parameter regions, duplicate run identities, and incompatible cost models.
- Verify that resumable execution never combines artifacts from different code versions, configurations, data fingerprints, or seeds.
- Verify every aggregate from independently recomputed episode-level outputs, including sample counts, exclusions, quantiles, relative gaps, activation frequencies, and cash/unit decomposition totals.
- Verify that overlapping-window uncertainty code reproduces hand-checkable small samples and records its exact block construction and random seed where applicable.
- Verify that primary tables cannot include undeclared datasets, horizons, coverage levels, parameters, or estimands without changing the run configuration and its identity.
- Run the repository link check, scientific checks, and an independent
  empirical review before treating an experiment report as publication-ready.
- The independent review must reproduce at least one complete synthetic run and one historical slice from raw inputs, audit provenance and exclusions, check the statistical interpretation, and confirm that the prose does not overstate theorem or empirical scope.

## Out of Scope

- Universal, pathwise, stochastic, or causal claims that SmartDCA outperforms DCA.
- Re-proving or modifying the epsilon-DCA unit guardrail.
- Extending the safety theorem to transaction costs, taxes, slippage, interest on cash, dividends not already embedded in the declared series, or market impact.
- Dynamic safety ratchets or time-varying \(\lambda\).
- Minimax, regret-optimal, expected-utility-optimal, or otherwise optimal policy design over the complete epsilon-DCA-safe class.
- Training a forecasting model, using future information, or redefining the corrected-mean selector from empirical outcomes.
- Choosing and reporting only the best corrected-mean parameter after searching the confirmatory test set.
- A production trading service, broker integration, order execution, portfolio custody, or individualized investment advice.
- Taxes, account-specific constraints, short selling, leverage, borrowing, multi-asset rebalancing, and currency hedging.
- Comprehensive coverage of assets beyond the declared S&P 500 proxy and Bitcoin/USD series.
- Using a four-purchase formula, more isolated beta-flip examples, or generic mean-axiom results as substitutes for the empirical study.
- Full manuscript assembly, venue selection, or defense-slide production; the reviewed report and figure-ready data are inputs to that later work.
- New mathematical claims inferred from exploratory regime patterns; those require a separately specified mathematical effort.

## Further Notes

This effort is the empirical step in the thesis narrative:

> attempted adaptive DCA → impossible universal dominance → sharp attainable
> safety → guarded adaptive rule → exact arbitrary-horizon performance boundary
> → measured safety-adaptivity trade-off.

The [epsilon-DCA safety theorem](../../../../research/theorems/epsilon-dca-safety-unit-guardrail.md)
defines the frictionless guarantee. The
[arbitrary-horizon performance theorem](../../../../research/theorems/arbitrary-horizon-performance-boundary.md)
defines the accepted terminal cash/unit attribution and explains why intuitive
path geometry alone is insufficient. The empirical study must use both results
as interpretation and validation infrastructure, not as evidence that the
corrected-mean selector will perform well.

The agreed verification seam is one reproducible end-to-end experiment runner
with independent DCA accounting, a shared guarded-policy interface, complete
ledgers, and report generation from immutable run outputs. The [effort
map](map.md) is authoritative for route and current state. The historical-data
boundary keeps confirmatory aggregate outcomes closed until the seam passes
review.

## Comments

- Synthesized from the accepted arbitrary-horizon result and the agreed
  recommendation to proceed directly to empirical evaluation.
- The user accepted the proposed empirical direction and previously described
  the thesis as a Financial Computing use-case narrative in which negative and
  bounded advances remain legitimate contributions.
