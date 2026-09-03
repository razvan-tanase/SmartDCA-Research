# DCA, adaptive accumulation, causal decisions, and portfolio safety

## Purpose and conclusion

This note positions the thesis's recurring-deposit results against primary sources on dollar-cost
averaging (DCA), adaptive contribution rules, online portfolio decisions, and safety constraints. The
search was completed on **2026-09-03 (UTC)**. The search is **not exhaustive**: it is a bounded,
targeted review, not a systematic review or a proof that no earlier result exists.

The central distinction is economic, not terminological. The thesis studies a buy-only investor who
receives an **exogenous deposit at each date**, observes the current price before buying, cannot use
future information, cannot spend more cash than has arrived, and is compared with DCA under the
**same deposit sequence and horizon**. Performance is terminal cash plus the value of accumulated
units. That object differs from:

- deciding whether to invest an already available lump sum now or stage it through time;
- rebalancing a previously funded stock/bond portfolio;
- choosing contributions as an endogenous function of market prices or returns;
- rescaling a strategy retrospectively so that its total historical spend matches DCA; and
- giving individualized investment advice.

The sources reviewed contain close ingredients but not the complete combination. Classical DCA work
studies fixed initial wealth, expected utility, or a bounded stochastic/minimax model
([Constantinides, 1979](https://doi.org/10.2307/2330513);
[Pye, 1971](https://doi.org/10.1287/mnsc.17.7.379)); value-aware accumulation changes contribution
amounts ([Edleson, 2006](https://www.oreilly.com/library/view/value-averaging-the/9780470049778/11_ch003.html));
online portfolio selection generally rebalances one existing wealth account against a best portfolio
in hindsight ([Cover, 1991](https://doi.org/10.1111/j.1467-9965.1991.tb00002.x)); and safety-first,
portfolio-insurance, and conservative-learning work use different floors, comparators, or probability
qualifiers ([Roy, 1952](https://doi.org/10.2307/1907413);
[Cont and Tankov, 2009](https://doi.org/10.1111/j.1467-9965.2009.00377.x);
[Wu et al., 2016](https://proceedings.mlr.press/v48/wu16.html)). The thesis's exact no-dominance
statement should nevertheless **not** be advertised as a new general no-arbitrage principle: its gain
process lies inside the one-point-arbitrage framework of
[Burzoni et al. (2019)](https://doi.org/10.1287/moor.2018.0956). The defensible contribution is a
DCA-specific formulation that makes deposit matching, causal buy-only feasibility, cash accounting,
and equality conditions explicit; see the project's
[primary-source novelty note](ticket-08-causal-dca-novelty-primary-sources.md).

## Search protocol

### Routes and query concepts

The search used a general scholarly web index for title and citation discovery, then followed results
to DOI-resolving publisher pages, official institutional publications, author/institutional
repositories, arXiv, and PMLR. The repository's preserved SmartDCA source PDF was also inspected.
Search concepts (including close title searches and spelling variants) were:

- `dollar cost averaging recurring investment payroll versus lump sum`;
- `A Note on the Suboptimality of Dollar-Cost Averaging as an Investment Policy`;
- `Minimax Policies for Selling an Asset and Dollar Averaging`;
- `Dollar Cost Averaging Brennan Li Torous`;
- `value averaging Edleson contribution target portfolio value`;
- `enhanced dollar cost averaging Dunham Friesen`;
- `augmented dollar cost averaging macroeconomic indicators`;
- `SmartDCA dynamic spending average purchase price`;
- `universal portfolio best constant rebalanced portfolio hindsight`;
- `online portfolio multiplicative updates regret wealth`;
- `one-way trading online algorithm competitive ratio`;
- `safety first holding of assets Roy`;
- `constant proportion portfolio insurance floor gap risk`;
- `portfolio drawdown constraint running maximum`;
- `conservative bandits baseline guarantee`; and
- `one-point arbitrage discrete time Burzoni`.

No subscription-only citation index (for example, Scopus or Web of Science) was available, and no
forward-citation census was attempted. The result is therefore a reproducible conceptual search
boundary, not an exhaustive bibliography.

## Inclusion and exclusion boundaries

Included sources are original methodological papers, journal articles, books, official research
publications, or author manuscripts that define a representative strategy, comparator, objective, or
guarantee. Preference was given to stable DOI, publisher, institutional, PMLR, and arXiv URLs.
Surveys are used only to name a field or taxonomy, not to establish priority. Secondary web
explainers, marketing summaries, trading blogs, and unsourced claims were excluded. Empirical papers
were included only when they clarify the strategy or the type of evidence; this note does not treat a
historical backtest as a theorem.

Full text was available for the official Vanguard report, the preserved SmartDCA paper,
author/arXiv versions of several online-portfolio papers, and the PMLR conservative-bandit paper. For
Edleson's Wiley book, only a truncated excerpt hosted by the licensed O'Reilly aggregator was
accessible; the full book was not independently accessed. For several older or paywalled journal
articles, only publisher metadata, abstracts, and/or author-repository records were accessible.
Claims about those sources are limited to what those records establish. No empirical result was
independently replicated for this note.

## Do not collapse the comparison problems

### Recurring DCA versus staged investment of a lump sum

"DCA" is used for at least two cash-flow problems. Finlay and Zorn explicitly separate automatic
investment of wages from the decision to invest a windfall immediately or hold part of that already
available cash for staged investment; their analysis addresses the latter
([Vanguard Research, 2023](https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf)).
Constantinides likewise analyzes an investor allocating capital through time and evaluates the policy
inside an expected-utility model
([Constantinides, 1979](https://doi.org/10.2307/2330513)). Those results do not answer whether a
causal rule can use a stream of not-yet-arrived deposits to dominate the recurring DCA benchmark.

In this thesis, recurring DCA means investing deposit \(d_t\) when it arrives at date \(t\). Future
deposits are unavailable. Holding back part of today's deposit creates cash; it does not create access
to tomorrow's deposit. This timing convention is fixed in the
[causal DCA dominance theorem](../theorems/causal-dca-dominance-impossibility.md).

### Adaptive accumulation versus fixed-dollar DCA

Value averaging sets a target path for portfolio value and makes the period's transaction close the
gap between the target and the current portfolio value, rather than investing the same dollar amount
every period ([Edleson, 2006](https://www.oreilly.com/library/view/value-averaging-the/9780470049778/11_ch003.html)).
Thus its cash flow is endogenous to realized market performance. Algebraically, a value above the
target can call for no contribution or a withdrawal; that observation follows from the rule and is
not evidence that the method shares the thesis's buy-only, exogenous-deposit budget.

Enhanced DCA varies the next contribution with the preceding month's return. Dunham and Friesen
report simulation and historical comparisons with fixed DCA, including higher dollar-weighted returns
in many of their samples
([Dunham and Friesen, 2012](https://doi.org/10.3905/jwm.2012.15.1.041)). Augmented DCA uses prevailing
economic conditions to change investment intensity, and its authors report Sharpe-ratio and
stochastic-dominance comparisons on U.S. data from 1967--2018
([Kapalczynski and Lien, 2021](https://doi.org/10.1016/j.najef.2021.101370)). These are adaptive
contribution strategies, but the available records do not establish the thesis's same-deposit,
all-positive-path terminal-wealth guarantee. In particular, the point-in-time release and revision
treatment of the macroeconomic series could not be verified from the accessible abstract, so this
note does not label that empirical rule sequentially admissible.

SmartDCA makes purchase amounts functions of a reference level divided by the currently observed
price. Its source paper proves acquisition-price statements and reports return-on-investment and
average-price results for variants whose total expenditures differ materially from DCA
([Calvet, Herranz-Celotti, and Valimamode, 2023](https://arxiv.org/abs/2308.05200v1)). The strategy is
therefore relevant evidence for price-responsive accumulation, but a lower average acquisition price
under endogenous spending is not, by itself, a same-budget terminal-wealth dominance result.

### Rebalancing versus accumulation

Cover's universal portfolio causally reallocates one funded portfolio and approaches the exponential
growth rate of the best constant-rebalanced portfolio selected in hindsight
([Cover, 1991](https://doi.org/10.1111/j.1467-9965.1991.tb00002.x)). Ordentlich and Cover give exact
finite-horizon max-min wealth ratios to that hindsight comparator
([Ordentlich and Cover, 1998](https://doi.org/10.1287/moor.23.4.960)), while multiplicative-update
portfolio rules pursue nearly the wealth of the best constant-rebalanced portfolio and permit repeated
reallocation among assets
([Helmbold et al., 1998](https://doi.org/10.1111/1467-9965.00058)). These are causal online decisions
and can have pathwise sequence guarantees, but they normally allow sales/rebalancing, begin with one
wealth account, and compare against a hindsight portfolio rather than recurring DCA under common
deposits. The online-portfolio field's broader taxonomy is summarized by
[Li and Hoi (2014)](https://doi.org/10.1145/2512962), which is used here only as a survey pointer.

### Ex-post budget matching versus sequential admissibility

Suppose a raw adaptive rule proposes \(u_t(h_t)\), based on history \(h_t\), and a researcher later
rescales all purchases by

\[
  c(P_{1:T})=\frac{\sum_{t=1}^T d_t}{\sum_{t=1}^T u_t(h_t)}.
\]

The resulting purchases have the same **realized** total spend as DCA, but \(c(P_{1:T})u_t(h_t)\)
usually depends on prices after date \(t\). Unless the scaling factor was fixed from information
available at \(t\), the normalized series is an ex-post comparison object, not an implementable causal
policy. The project's formal information convention is stated in
[the causal DCA theorem](../theorems/causal-dca-dominance-impossibility.md). This does not invalidate
retrospective normalization as descriptive analysis; it prevents using it as proof of a sequential
same-deposit guarantee.

### Research comparison versus investment advice

The sources answer mathematical, historical, or simulated comparison questions under their own
assumptions. This note does not assess investor suitability, taxes, fees, liquidity needs, or any
particular security, and it makes no recommendation to adopt DCA or an adaptive rule. Even the
Vanguard lump-sum report frames its conclusion as conditional on cash availability, risk aversion,
and the evaluated asset allocations
([Finlay and Zorn, 2023](https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf)).

## Claim semantics

The qualifier is part of every performance claim. These categories are not interchangeable.

| Claim type | Logical content | What it does **not** imply | Representative source |
| --- | --- | --- | --- |
| Universal/pathwise | An inequality holds for every path in a stated path class, with a named comparator and horizon. A worst-case result may be universal only inside a bounded model class. | Positive expected performance, realism of the path class, or equality to a different comparator. | The finite-horizon universal-portfolio ratio is to the best constant-rebalanced portfolio in hindsight ([Ordentlich and Cover, 1998](https://doi.org/10.1287/moor.23.4.960)); Pye's minimax result is inside his bounded arithmetic-price-change model ([Pye, 1971](https://doi.org/10.1287/mnsc.17.7.379)). |
| Expected | An expectation, expected utility, or moment comparison is taken under a specified stochastic model or estimated distribution. | A guarantee on every realized path. | Constantinides evaluates DCA through expected utility ([Constantinides, 1979](https://doi.org/10.2307/2330513)); Brennan, Li, and Torous study it in a mean-reverting price environment ([Brennan, Li, and Torous, 2005](https://doi.org/10.1007/s10679-005-4999-x)). |
| Probabilistic/distributional | A loss probability, high-probability event, stochastic dominance relation, or quantile is controlled under assumptions. | A deterministic inequality outside the event or distribution. | Roy's safety-first criterion controls the chance of falling below a disaster level ([Roy, 1952](https://doi.org/10.2307/1907413)); conservative bandits provide expected or high-probability baseline guarantees ([Wu et al., 2016](https://proceedings.mlr.press/v48/wu16.html)). |
| Realized/simulated | A rule performed a certain way in a historical sample or a finite simulation design. | Population dominance, causal validity of revised inputs, or a theorem for unseen paths. | Enhanced DCA's reported frequencies are simulation and historical findings ([Dunham and Friesen, 2012](https://doi.org/10.3905/jwm.2012.15.1.041)); augmented DCA's comparisons use a U.S. historical sample ([Kapalczynski and Lien, 2021](https://doi.org/10.1016/j.najef.2021.101370)). |

A claim may carry more than one qualifier. For example, a statement can be high-probability and
uniform over all times, or pathwise but only over sequences satisfying declared price bounds. The
manuscript should always state the path/model class, information set, comparator, metric, and
quantifier together.

## Comparative synthesis

| Strategy/source | Information timing | Funding | Comparator | Performance criterion | Guarantee type |
| --- | --- | --- | --- | --- | --- |
| Staged investment of available cash ([Finlay and Zorn, 2023](https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf)) | Schedule chosen for money already available; not driven by future prices. | One initial windfall, with the uninvested portion temporarily in cash. | Immediate lump-sum investment. | Terminal wealth/distribution over the selected staging period. | Historical and simulation-based frequencies; not an all-path guarantee. |
| Classical policy analysis ([Constantinides, 1979](https://doi.org/10.2307/2330513)) | Dynamic allocation under the paper's market and preference assumptions. | Initially available capital allocated through time. | Feasible investment policies in the model. | Expected utility. | Model-contingent suboptimality, not pathwise recurring-deposit dominance. |
| Dollar averaging/minimax ([Pye, 1971](https://doi.org/10.1287/mnsc.17.7.379)) | Both nonsequential and sequential policies are considered. | A given sum is irreversibly converted over a fixed number of periods. | The model's hindsight or worst-case benchmark. | Minimax loss under bounded symmetric arithmetic price changes. | Worst-case result within a restricted price model; not all positive price paths with new deposits. |
| Value averaging ([Edleson, 2006](https://www.oreilly.com/library/view/value-averaging-the/9780470049778/11_ch003.html)) | Current portfolio value is compared with a preselected target path. | Contribution or withdrawal closes the target gap; cash flow is endogenous. | Fixed-dollar DCA and target-path goals. | Value-path tracking and return/accounting comparisons. | A strategy prescription and examples, not a universal same-deposit wealth floor. |
| Enhanced DCA ([Dunham and Friesen, 2012](https://doi.org/10.3905/jwm.2012.15.1.041)) | The next investment responds to the preceding month's return. | Periodic amount is raised or reduced, so cash flows differ by state unless separately constrained. | Fixed DCA. | Dollar-weighted return and wealth comparisons. | Simulation and historical evidence. |
| Augmented DCA ([Kapalczynski and Lien, 2021](https://doi.org/10.1016/j.najef.2021.101370)) | Investment intensity responds to prevailing macroeconomic conditions. | State-dependent accumulation; the accessible abstract does not establish identical deposit use. | Conventional DCA. | Sharpe ratio and first-/second-order stochastic dominance. | Historical U.S. evidence; real-time data-vintage admissibility was not established in this review. |
| SmartDCA ([Calvet, Herranz-Celotti, and Valimamode, 2023](https://arxiv.org/abs/2308.05200v1)) | Purchase size uses the current price and a reference price/statistic. | Buy-only variable expenditure; reported variants need not spend DCA's total. | Fixed DCA in acquisition-price and ROI tables. | Average acquisition price and ROI. | Algebraic acquisition-price results plus realized backtests; no same-deposit all-path terminal-wealth dominance result. |
| One-way trading ([El-Yaniv et al., 2001](https://doi.org/10.1007/s00453-001-0003-0)) | Current exchange rate is observed before each irrevocable conversion. | One initial cash budget; irreversible conversion, usually with a deadline. | Offline trader that knows the rate sequence. | Competitive ratio. | Worst-case and distribution-sensitive guarantees under declared rate information; no recurring deposits or DCA comparator. |
| Universal/online portfolio selection ([Cover, 1991](https://doi.org/10.1111/j.1467-9965.1991.tb00002.x); [Ordentlich and Cover, 1998](https://doi.org/10.1287/moor.23.4.960); [Helmbold et al., 1998](https://doi.org/10.1111/1467-9965.00058)) | Allocation is causal: weights precede the next market return. | One funded wealth account, repeatedly rebalanced; sales are generally allowed. | Best constant-rebalanced portfolio chosen in hindsight. | Relative wealth, exponential growth rate, or regret-like log-wealth shortfall. | Pathwise/asymptotic or finite-horizon competitive guarantees for that comparator, plus experiments. |
| Safety first ([Roy, 1952](https://doi.org/10.2307/1907413)) | Static portfolio choice from distributional beliefs. | Initially funded asset allocation. | Disaster-level shortfall event, not DCA. | Probability of terminal return/wealth below a threshold. | Distributional/probabilistic criterion. |
| Constant-proportion portfolio insurance ([Black and Perold, 1992](https://doi.org/10.1016/0165-1889(92)90043-E)) | Risk exposure is repeatedly adjusted from current cushion above a floor. | Rebalancing between risky and safe assets from initial wealth. | A wealth floor. | Downside protection with upside participation. | Model-contingent floor mechanism: continuous diffusion trading can avoid downside breach, while jumps create gap risk ([Cont and Tankov, 2009](https://doi.org/10.1111/j.1467-9965.2009.00377.x)). |
| Drawdown-constrained investment ([Grossman and Zhou, 1993](https://doi.org/10.1111/j.1467-9965.1993.tb00044.x)) | Dynamic exposure uses current wealth and its running maximum. | Continuously rebalanced risky/safe allocation from initial wealth. | Floor equal to a fraction of the strategy's own running maximum. | Expected utility subject to drawdown control. | Stochastic-model constrained optimum; not a DCA-relative pathwise floor. |
| Conservative bandits ([Wu et al., 2016](https://proceedings.mlr.press/v48/wu16.html)) | Actions use past observations and compare cumulative reward with a baseline policy. | An online learning reward budget, not a financial deposit account. | Fixed baseline policy. | Reward/regret while staying above a baseline fraction. | Expected or high-probability guarantees, including constraints uniform over time. |
| Thesis recurring-deposit rule ([causal theorem](../theorems/causal-dca-dominance-impossibility.md); [epsilon guardrail](../theorems/epsilon-dca-safety-unit-guardrail.md)) | Purchase at \(t\) uses deposits, prices, and portfolio state observed through \(t\), after seeing \(P_t\) but before future prices. | Exogenous recurring deposits; buy-only; unspent cash is retained; cumulative purchases cannot exceed cumulative deposits. | DCA investing the full same deposit at every date. | Cash-inclusive terminal wealth and its ratio to DCA. | Exact universal all-positive-path impossibility at \(\lambda=1\); exact universal relative floor for the stated epsilon guardrail. |

## Synthesis by literature strand

### 1. DCA and timing

Pye's dollar-averaging problem is unusually close in its irreversible conversion structure, but its
budget is present at the outset and its minimax conclusion is tied to bounded arithmetic price changes
([Pye, 1971](https://doi.org/10.1287/mnsc.17.7.379)). Constantinides asks an expected-utility policy
question for available capital ([Constantinides, 1979](https://doi.org/10.2307/2330513)). Brennan,
Li, and Torous model DCA under mean reversion
([Brennan, Li, and Torous, 2005](https://doi.org/10.1007/s10679-005-4999-x)), and Kirkby, Mitra, and
Nguyen derive moments and risk measures in a stochastic DCA/market-timing framework
([Kirkby, Mitra, and Nguyen, 2020](https://doi.org/10.1016/j.ejor.2020.04.055)). Vanduffel et al.
construct path-independent option alternatives that risk-averse investors prefer under their Lévy
return model ([Vanduffel et al., 2012](https://doi.org/10.1142/S0219024912500136)). Each is informative
about DCA under a declared model or preference, but none of those qualifiers is equivalent to the
thesis's universal comparison for every positive price path and every common deposit sequence.

The recurring-versus-lump-sum distinction should appear wherever the manuscript cites evidence that
"lump sum beats DCA." In the Vanguard study, the investor has the full sum on day one
([Finlay and Zorn, 2023](https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf));
in the thesis, future deposits do not yet exist. The first problem compares two schedules for a common
initial endowment. The second compares causal uses of an arrival process.

### 2. Adaptive and value-aware accumulation

The adaptive-accumulation literature establishes that responding to prices, recent returns, or state
variables is not itself novel. Value averaging responds to the gap from a target portfolio-value path
([Edleson, 2006](https://www.oreilly.com/library/view/value-averaging-the/9780470049778/11_ch003.html));
enhanced DCA responds to the preceding return
([Dunham and Friesen, 2012](https://doi.org/10.3905/jwm.2012.15.1.041)); augmented DCA responds to
economic conditions
([Kapalczynski and Lien, 2021](https://doi.org/10.1016/j.najef.2021.101370)); and SmartDCA responds to
the reference-to-current-price ratio
([Calvet, Herranz-Celotti, and Valimamode, 2023](https://arxiv.org/abs/2308.05200v1)).

What matters for the thesis is whether the adaptive purchase can be funded by the **same exogenous
deposits at the decision date** and what performance variable is compared. Contribution flexibility
can mechanically increase units purchased in low-price states, but it also changes total capital at
risk and cash timing. An acquisition-price mean, dollar-weighted return, or ROI ratio can therefore
answer a different question from terminal cash-inclusive wealth. The SmartDCA source itself reports
variant-specific total expenditure alongside its return and acquisition-price comparisons
([Calvet, Herranz-Celotti, and Valimamode, 2023](https://arxiv.org/abs/2308.05200v1)).

### 3. Causal and online decisions

One-way trading provides the closest generic online-algorithm analogy: current prices arrive
sequentially, conversions are irreversible, and performance is measured against an offline optimum
([El-Yaniv et al., 2001](https://doi.org/10.1007/s00453-001-0003-0)). Its resource is an initial budget,
however, and its comparator knows the future. Online portfolio selection is also causal, but its
canonical comparator is the best constant-rebalanced portfolio in hindsight and its action is a
rebalanced portfolio weight, not a buy-only use of recurring deposits
([Cover, 1991](https://doi.org/10.1111/j.1467-9965.1991.tb00002.x);
[Ordentlich and Cover, 1998](https://doi.org/10.1287/moor.23.4.960)).

These sources show why "causal" alone does not locate a theorem. A meaningful comparison also names
the resource arrival process, whether sales and borrowing are allowed, whether the comparator is
causal or hindsight, and whether the criterion is exact terminal wealth, asymptotic growth, regret, or
a competitive factor.

### 4. Safety constraints and guarantees

Safety-first, portfolio insurance, drawdown control, and conservative online learning all formalize a
notion of staying close to a floor or baseline, but the semantics differ:

- Roy minimizes the probability of falling below a disaster threshold, a distributional rather than
  pathwise statement ([Roy, 1952](https://doi.org/10.2307/1907413)).
- CPPI scales risky exposure with the cushion above a floor
  ([Black and Perold, 1992](https://doi.org/10.1016/0165-1889(92)90043-E)); the diffusion idealization
  and jump-induced gap risk are analyzed explicitly by
  [Cont and Tankov (2009)](https://doi.org/10.1111/j.1467-9965.2009.00377.x).
- Grossman and Zhou constrain wealth relative to its own running maximum inside a continuous-time
  stochastic control problem
  ([Grossman and Zhou, 1993](https://doi.org/10.1111/j.1467-9965.1993.tb00044.x)).
- Conservative bandits protect cumulative reward relative to a baseline with expected or
  high-probability learning guarantees
  ([Wu et al., 2016](https://proceedings.mlr.press/v48/wu16.html)).

The thesis's \(\varepsilon\)-DCA safety statement is instead an exact, cash-inclusive relative-wealth
floor against the DCA benchmark on every positive price path in its discrete buy-only model. Its
sharp unit-purchase characterization is recorded in the
[epsilon-DCA safety note](sharp-epsilon-dca-safety-guardrail.md). It should be positioned as a
specialized baseline-relative guardrail, not as the invention of downside control or safe online
decision-making.

## Why the accounting and information restrictions are material

### Sequential admissibility

At time \(t\), an implementable purchase can use \(P_t\) and the account state then visible, but not
\(P_{t+1:T}\). This restriction rules out hindsight triggers and retrospective normalization. It is
also what gives an adversarial continuation argument economic content: after today's funded choice,
tomorrow's price may move without the strategy revising today's trade. The precise filtration-free
definition used by the project is in the
[causal DCA theorem](../theorems/causal-dca-dominance-impossibility.md).

### Same deposits and funding

If the candidate may contribute more after low returns, borrow against future income, or withdraw
capital after gains while DCA cannot, a wealth difference combines timing skill with a financing
difference. Requiring the same deposit sequence removes that confound. Cumulative purchase feasibility
also prevents a rule from spending tomorrow's deposit today. It does **not** require investing each
deposit immediately: retained cash is an admissible state variable.

### Cash-inclusive terminal wealth

When a rule buys less stock than DCA, the difference remains as cash. Ignoring that cash understates
the candidate; comparing units alone overstates whichever rule spent more. The common economic
measure is

\[
  W_T=C_T+P_TQ_T,
\]

with cash \(C_T\), accumulated units \(Q_T\), and the same terminal evaluation price \(P_T\). Under
this accounting, equal deposits cancel from the terminal-wealth difference and expose the signed
trading gain used in the project's
[pathwise dominance note](pathwise-dca-dominance-under-causal-budget.md) and
[arbitrary-horizon boundary](arbitrary-horizon-performance-boundary.md).

Average acquisition cost, units purchased, ROI, and terminal wealth can rank rules differently when
total or timed contributions differ. The lower acquisition-price property studied by SmartDCA is a
valid statement about its own metric
([Calvet, Herranz-Celotti, and Valimamode, 2023](https://arxiv.org/abs/2308.05200v1)); it is not a
substitute for cash-inclusive wealth under a common funding process.

## Novelty and citation verdict

The targeted search supports the following bounded formulation:

1. Adaptive DCA, value-aware contributions, causal online investment, downside floors, and
   baseline-relative safety all have prior work represented by
   [Dunham and Friesen (2012)](https://doi.org/10.3905/jwm.2012.15.1.041),
   [Edleson (2006)](https://www.oreilly.com/library/view/value-averaging-the/9780470049778/11_ch003.html),
   [Cover (1991)](https://doi.org/10.1111/j.1467-9965.1991.tb00002.x),
   [Cont and Tankov (2009)](https://doi.org/10.1111/j.1467-9965.2009.00377.x), and
   [Wu et al. (2016)](https://proceedings.mlr.press/v48/wu16.html).
2. General pathwise no-one-point-arbitrage theory predates the thesis. Burzoni et al. define a
   self-financing gain that is nonnegative in every scenario and positive in at least one, and
   characterize absence of that opportunity using finite-support martingale measures
   ([Burzoni et al., 2019](https://doi.org/10.1287/moor.2018.0956)). After common deposits cancel, the
   thesis's exact DCA improvement would be such a gain in a specialized finite-horizon market.
3. The thesis adds a transaction-level DCA interpretation: with sequentially admissible, cash-funded,
   buy-only trades and equal deposit arrivals, universal weak terminal-wealth dominance forces the
   DCA purchases themselves. Its equality characterization is proved in the
   [causal theorem](../theorems/causal-dca-dominance-impossibility.md), rather than inferred from a
   literature search.
4. Within the English-language routes and query families listed above, no primary source was located
   that states the exact conjunction of recurring exogenous deposits, current-price causal purchases,
   no borrowing or sales, retained cash, cash-inclusive terminal wealth, DCA as the same-deposit
   comparator, an all-positive-path \(\lambda=1\) uniqueness result, and the project's sharp
   \(\lambda=1-\varepsilon\) local unit guardrail. This is a non-discovery statement, **not** a claim
   of priority or exhaustive novelty. In particular, non-discovery in this bounded search **does not establish novelty**.

Manuscript-safe wording is therefore:

> Existing work studies DCA timing, value-aware contributions, online portfolio choice, and
> downside or baseline-relative constraints under several distinct funding, information, and
> performance regimes. Our result isolates their intersection for recurring exogenous deposits: in
> the stated buy-only cash model, a causal rule cannot weakly dominate same-deposit DCA on every
> positive price path unless it is DCA, while a relaxed relative floor admits a sharp local unit
> guardrail. This is a DCA-specific specialization of a broader no-one-point-arbitrage principle, not
> a claim that adaptive investment or pathwise safety is new.

Avoid "the first," "unprecedented," or "no prior work" unless a later systematic search establishes
that stronger claim.

## Claim-to-evidence map

The following identifiers and BibTeX keys match the manuscript claim register. The keys are recorded
verbatim so the repository audit can trace each prose claim to its bibliography entries.

| Registered claim | Evidence supplied by this note | Required bibliography keys |
| --- | --- | --- |
| `claim-lit-dca-scope` | The recurring-deposit/lump-sum distinction and the separation of minimax, expected-utility, and stochastic-preference statements appear in the DCA sections and comparison grid. | `pye1971`, `constantinides1979`, `brennan2005`, `vanduffel2012`, `finlayzorn2023`, `kirkby2020` |
| `claim-lit-adaptive-accumulation` | The adaptive-accumulation section distinguishes sequential minimax conversion, target-value cash flows, and price-responsive SmartDCA by timing, funding, comparator, criterion, and guarantee. | `pye1971`, `edleson2006`, `calvet2023smartdca`, `dunhamfriesen2012`, `kapalczynskilien2021` |
| `claim-lit-online-decisions` | The online-decision section separates causal rebalancing and irreversible conversion from buy-only recurring deposits and identifies their hindsight/offline comparators. | `cover1991`, `helmbold1998`, `lihoi2014`, `elyaniv2001`, `ordentlichcover1998` |
| `claim-lit-safety-objectives` | The safety section distinguishes shortfall probability, an absolute portfolio-insurance floor, own-wealth drawdown control, and the project's DCA-relative floor. | `roy1952`, `blackperold1992`, `grossmanzhou1993`, `conttankov2009`, `wu2016` |
| `claim-lit-project-boundary` | The accounting section explains sequential admissibility, same-deposit funding, and cash-inclusive terminal wealth; the novelty verdict places strict improvement inside pointwise no-arbitrage. | `burzoni2019` |

### Detailed source-use controls

| ID | Claim that may be used in the manuscript | Primary support | Qualification that must travel with the claim |
| --- | --- | --- | --- |
| LIT-01 | The term DCA covers both recurring paycheck investment and staged deployment of an already available lump sum. | [Finlay and Zorn (2023)](https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf) | Their performance study is the lump-sum timing problem, not the thesis's deposit-arrival problem. |
| LIT-02 | Classical objections to DCA can be expected-utility/model results rather than universal pathwise claims. | [Constantinides (1979)](https://doi.org/10.2307/2330513) | Do not generalize beyond the paper's market and preference assumptions. |
| LIT-03 | Sequential dollar averaging has been studied under a minimax criterion. | [Pye (1971)](https://doi.org/10.1287/mnsc.17.7.379) | One initial sum and bounded arithmetic price changes; not recurring deposits over all positive paths. |
| LIT-04 | Value averaging makes cash flow respond to the gap from a target portfolio-value path. | [Edleson (2006)](https://www.oreilly.com/library/view/value-averaging-the/9780470049778/11_ch003.html) | Contributions are endogenous and can differ from DCA's deposits. |
| LIT-05 | Enhanced and augmented DCA are adaptive contribution strategies with simulation or historical evidence. | [Dunham and Friesen (2012)](https://doi.org/10.3905/jwm.2012.15.1.041); [Kapalczynski and Lien (2021)](https://doi.org/10.1016/j.najef.2021.101370) | Realized/simulated comparisons are not all-path guarantees; real-time macro-data treatment was not verified. |
| LIT-06 | SmartDCA uses price-responsive spending and studies acquisition price/ROI with differing expenditures across variants. | [Calvet, Herranz-Celotti, and Valimamode (2023)](https://arxiv.org/abs/2308.05200v1) | Do not translate a lower average acquisition price into same-budget terminal-wealth dominance. |
| LIT-07 | Universal and multiplicative-update portfolios compare causal rebalancing wealth with the best constant-rebalanced portfolio in hindsight. | [Cover (1991)](https://doi.org/10.1111/j.1467-9965.1991.tb00002.x); [Ordentlich and Cover (1998)](https://doi.org/10.1287/moor.23.4.960); [Helmbold et al. (1998)](https://doi.org/10.1111/1467-9965.00058) | Rebalancing, initial wealth, and the hindsight comparator differ from buy-only recurring DCA. |
| LIT-08 | One-way trading studies causal irreversible conversion against an offline comparator. | [El-Yaniv et al. (2001)](https://doi.org/10.1007/s00453-001-0003-0) | Its initial budget and competitive criterion differ from the thesis. |
| LIT-09 | Safety-first controls shortfall probability, whereas CPPI and drawdown control use dynamic floors. | [Roy (1952)](https://doi.org/10.2307/1907413); [Black and Perold (1992)](https://doi.org/10.1016/0165-1889(92)90043-E); [Grossman and Zhou (1993)](https://doi.org/10.1111/j.1467-9965.1993.tb00044.x) | State whether a claim is probabilistic, model-contingent, or relative to the strategy's own peak. |
| LIT-10 | CPPI's idealized floor is vulnerable to jump/gap risk. | [Cont and Tankov (2009)](https://doi.org/10.1111/j.1467-9965.2009.00377.x) | Do not call the floor universal in a jump market. |
| LIT-11 | Conservative online learning supplies baseline-relative safety analogies. | [Wu et al. (2016)](https://proceedings.mlr.press/v48/wu16.html) | Guarantees are expected/high-probability reward statements, not financial pathwise wealth guarantees. |
| LIT-12 | A universal DCA improvement is contained in the broader one-point-arbitrage envelope. | [Burzoni et al. (2019)](https://doi.org/10.1287/moor.2018.0956) and the project's [specialization note](ticket-08-causal-dca-novelty-primary-sources.md) | Credit the general principle; claim only the DCA-specific accounting and equality result proved here. |

## Primary bibliography

- Black, Fischer, and André Perold. 1992. "Theory of Constant Proportion Portfolio Insurance."
  *Journal of Economic Dynamics and Control* 16 (3--4): 403--426.
  [DOI](https://doi.org/10.1016/0165-1889(92)90043-E).
- Brennan, Michael J., Feifei Li, and Walter N. Torous. 2005. "Dollar Cost Averaging."
  *Review of Finance* 9 (4): 509--535.
  [DOI](https://doi.org/10.1007/s10679-005-4999-x).
- Burzoni, Matteo, Marco Frittelli, Zhaoxu Hou, Marco Maggis, and Jan Obloj. 2019. "Pointwise
  Arbitrage Pricing Theory in Discrete Time." *Mathematics of Operations Research* 44 (3):
  1034--1057. [DOI](https://doi.org/10.1287/moor.2018.0956);
  [author version](https://arxiv.org/abs/1612.07618).
- Calvet, Emmanuel, Luca Herranz-Celotti, and Karim Valimamode. 2023. "SmartDCA Superiority."
  arXiv:2308.05200v1.
  [Versioned manuscript](https://arxiv.org/abs/2308.05200v1).
- Constantinides, George M. 1979. "A Note on the Suboptimality of Dollar-Cost Averaging as an
  Investment Policy." *Journal of Financial and Quantitative Analysis* 14 (2): 443--450.
  [DOI](https://doi.org/10.2307/2330513).
- Cont, Rama, and Peter Tankov. 2009. "Constant Proportion Portfolio Insurance in the Presence of
  Jumps in Asset Prices." *Mathematical Finance* 19 (3): 379--401.
  [DOI](https://doi.org/10.1111/j.1467-9965.2009.00377.x).
- Cover, Thomas M. 1991. "Universal Portfolios." *Mathematical Finance* 1 (1): 1--29.
  [DOI](https://doi.org/10.1111/j.1467-9965.1991.tb00002.x).
- Dunham, Lee M., and Geoffrey C. Friesen. 2012. "Building a Better Mousetrap: Enhanced
  Dollar-Cost Averaging."
  *Journal of Wealth Management* 15 (1): 41--50.
  [DOI](https://doi.org/10.3905/jwm.2012.15.1.041);
  [institutional record](https://digitalcommons.unl.edu/financefacpub/26/).
- Edleson, Michael E. 2006. *Value Averaging: The Safe and Easy Strategy for Higher Investment
  Returns*. Hoboken, NJ: Wiley. ISBN 978-0-470-04977-8.
  [Truncated excerpt hosted by the licensed O'Reilly aggregator](https://www.oreilly.com/library/view/value-averaging-the/9780470049778/11_ch003.html).
- El-Yaniv, Ran, Amos Fiat, Richard M. Karp, and Gordon Turpin. 2001. "Optimal Search and One-Way
  Trading Online Algorithms." *Algorithmica* 30: 101--139.
  [DOI](https://doi.org/10.1007/s00453-001-0003-0).
- Finlay, Megan, and Josef Zorn. 2023. "Cost Averaging: Invest Now or Temporarily
  Hold Your Cash?" Vanguard Research.
  [Official report](https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf).
- Grossman, Sanford J., and Zhongquan Zhou. 1993. "Optimal Investment Strategies for Controlling
  Drawdowns." *Mathematical Finance* 3 (3): 241--276.
  [DOI](https://doi.org/10.1111/j.1467-9965.1993.tb00044.x).
- Helmbold, David P., Robert E. Schapire, Yoram Singer, and Manfred K. Warmuth. 1998. "On-Line
  Portfolio Selection Using Multiplicative Updates." *Mathematical Finance* 8 (4): 325--347.
  [DOI](https://doi.org/10.1111/1467-9965.00058);
  [author manuscript](https://www.schapire.net/papers/HelmboldScSiWa98.pdf).
- Kapalczynski, Anna, and Donald Lien. 2021. "Effectiveness of Augmented Dollar-Cost Averaging."
  *North American Journal of Economics and Finance* 56: 101370.
  [DOI](https://doi.org/10.1016/j.najef.2021.101370).
- Kirkby, J. Lars, Sovan Mitra, and Duy Nguyen. 2020. "An Analysis of Dollar Cost Averaging and
  Market Timing Investment Strategies." *European Journal of Operational Research* 286 (3):
  1168--1186. [DOI](https://doi.org/10.1016/j.ejor.2020.04.055).
- Li, Bin, and Steven C. H. Hoi. 2014. "Online Portfolio Selection: A Survey."
  *ACM Computing Surveys* 46 (3), Article 35.
  [DOI](https://doi.org/10.1145/2512962); [author version](https://arxiv.org/abs/1212.2129).
- Ordentlich, Erik, and Thomas M. Cover. 1998. "The Cost of Achieving the Best Portfolio in
  Hindsight." *Mathematics of Operations Research* 23 (4): 960--982.
  [DOI](https://doi.org/10.1287/moor.23.4.960).
- Pye, Gordon. 1971. "Minimax Policies for Selling an Asset and Dollar Averaging."
  *Management Science* 17 (7): 379--393. [DOI](https://doi.org/10.1287/mnsc.17.7.379).
- Roy, A. D. 1952. "Safety First and the Holding of Assets." *Econometrica* 20 (3): 431--449.
  [DOI](https://doi.org/10.2307/1907413).
- Vanduffel, Steven, Aleš Ahčan, Luc Henrard, and Mateusz Maj. 2012. "An Explicit Option-Based
  Strategy That Outperforms Dollar Cost Averaging." *International Journal of Theoretical and
  Applied Finance* 15 (2): 1250013. [DOI](https://doi.org/10.1142/S0219024912500136).
- Wu, Yifan, Roshan Shariff, Tor Lattimore, and Csaba Szepesvári. 2016. "Conservative Bandits."
  In *Proceedings of the 33rd International Conference on Machine Learning*, PMLR 48: 1254--1262.
  [Official proceedings](https://proceedings.mlr.press/v48/wu16.html).
