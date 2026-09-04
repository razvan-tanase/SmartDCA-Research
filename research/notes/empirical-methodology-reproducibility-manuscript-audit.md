# Empirical methodology and reproducibility manuscript audit

## Scope and governing authorities

This note reconstructs the methodology stated in Chapter 6 and Appendices C--D
from accepted evidence without reopening an empirical outcome, changing an
accepted artifact, or using hidden conversation context. The governing design
is the locked [original protocol](../../experiments/protocols/safety-adaptivity-v1.json)
and its [Yahoo Finance provider replacement](../../experiments/protocols/safety-adaptivity-yahoo-v2.json).
The replacement changed provider-, client-, acquisition-, and provenance-facing
fields together with protocol identity, registration, disclosure, runtime, and
supersession metadata before in-sample observation access while preserving
every enumerated outcome-relevant design object.

The chapter also depends on:

- the [canonical guarded-policy definition](../definitions/guarded-corrected-mean-smartdca-rule.md)
  for the three policies and their common guardrail;
- the reviewed [deterministic](../../reports/experiments/deterministic-adversarial-paths.md),
  [stochastic](../../reports/experiments/seeded-stochastic-families.md),
  [historical](../../reports/experiments/confirmatory-historical-evaluation.md),
  and [cross-layer synthesis](../../reports/experiments/safety-adaptivity-tradeoff-synthesis.md)
  reports for layer roles and accepted run identities;
- the [historical source seam](../../reports/experiments/historical-data-episode-seam.md),
  [Yahoo provider review](yahoo-finance-historical-data-provider-review.md), and
  accepted source and preparation receipts for point-in-time semantics and the
  private/public boundary;
- the [statistical-methodology synthesis](reproducible-computational-finance-statistical-methodology.md)
  for registration, dependence, multiplicity, effect-size, reproducibility,
  provenance, and redistribution language; and
- the [independent empirical-package review](safety-adaptivity-empirical-package-review.md)
  and its sanitized receipt for the accepted reproduction claim.

No accepted protocol, input, source receipt, preparation manifest, run bundle,
or review receipt is modified by this manuscript slice.

## Frozen-design reconstruction

### Policies and comparisons

Every episode supplies the same realized price path, deposits, mapped purchase
dates, exact horizon, evaluation date and price, safety factor, and cost rule to
three fully specified policies. DCA selects all available cash as its
fee-inclusive target budget. Neutral guarded selects the midpoint between the
same floor expression and available cash; corrected guarded replaces the
one-half selector with the lagged corrected-mean score. Each target is clamped
to available cash. The policy-specific floor values may later differ because
policy cash and unit histories differ; the expression does not.

The target budget is not the asset notional under costs. For fixed fee `F_0`
and proportional rate `varpi`, a target at or below `F_0` produces no purchase
and no fee; otherwise asset notional is `(target-F_0)/(1+varpi)` and the fee is
`F_0` plus `varpi` times that notional. Cash falls by notional plus fee and
units rise by notional over price. The implementation uses 60-digit `Decimal`
arithmetic with the
notional division rounded downward. Frictionless accounting sets
`F_0=varpi=0`, so target and notional coincide and the sharp floor applies. The
10-basis-point and fixed-USD-1 routes use the same target rule but may buy less
than the floor expression and are outside the theorem; each fee-route floor expression uses
the DCA unit ledger under that same cost route. At lambda one the accepted
regression compares actual purchase, fee, cash, and units, not the diagnostic
`target_purchase_budget`, whose guarded and DCA serialization conventions
differ after Decimal rounding.

The three ordered comparisons are:

| Thesis name | Runner comparison | Design question |
| --- | --- | --- |
| complete system | `corrected_guarded_vs_dca` | How does the complete guarded corrected-mean policy compare with same-deposit DCA? |
| signal only | `corrected_guarded_vs_neutral_guarded` | What is the realized difference from replacing the neutral selector with the corrected score inside the same safety architecture? |
| architecture only | `neutral_guarded_vs_dca` | How does the configured neutral guardrail compare with DCA without crediting the corrected score? |

Each relative gap uses its own right-hand comparator as denominator. The three
percentages are not additive, and the architecture contrast is descriptive
rather than a causal decomposition.

### Evidence layers

The deterministic layer is a finite mechanism, regression, stress, and
counterexample catalog. Its null seed and catalog signs do not define a market
frequency. The stochastic layer uses five deliberately simple constructions,
three saved seeds (`104729`, `130363`, and `155921`), primary and exploratory
family configurations, and 12-, 36-, and 60-month horizons. Its three paths per
configuration are controlled sensitivity, not calibrated market probabilities
or population inference.

The rolling historical layer is the only confirmatory layer. It evaluates H1
and H2 on dependent monthly episode starts with the registered circular block
bootstrap and one Holm family. The robustness layer is a separately locked
post-confirmatory execution of declared coverage and quarterly-horizon axes.
It has no registered bootstrap or multiplicity decision and remains
descriptive. Cross-layer summaries may compare patterns but may not pool these
incompatible inferential units.

### Historical series, receipts, and episodes

The provider is Yahoo Finance; `yfinance==1.7.0` is the pinned acquisition
client. The client implementation parses and transforms Yahoo chart responses
before returning `Ticker.history` data
([pinned implementation](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/scrapers/history.py)).
The accepted canonical CSV therefore identifies client-export bytes rather
than raw provider-response bytes.

SPY selects `Adj Close` with `auto_adjust=false` and `repair=false`, retains
raw close and action columns for audit, and does not add dividends again. Yahoo
describes adjusted close as accounting for applicable split and distribution
adjustments ([Yahoo Finance Help](https://help.yahoo.com/kb/SLN28256.html)).
BTC-USD selects raw `Close` as a USD quotation proxy. Exact venue and
aggregation semantics remain unverified. The declared normalization timezones
are `America/New_York` and UTC. Runtime metadata must agree or acquisition
fails.

The [accepted source receipt](../../experiments/inputs/historical-yahoo-receipts-v2.json)
publishes provenance and fingerprints without observations. The source-set ID
is `yahoo-finance-historical-8b6758e9ad215699e21cd8907e233e00407a70c1b13b13b5490e1578921e260b`.
Its canonical-export SHA-256 values are
`eaf69d50bef6d77ff68fb6a52e0cc162c12eded8d8f00ef48d79922d0784458d`
for SPY and
`add11cc84321e32785034c07eced636fc01be8c7202867926b9e2ee77e23b3ee`
for BTC-USD.

For horizon `H`, a primary episode receives exactly `H` USD 1000 deposits at
monthly offsets `0` through `H-1`; the exact horizon receives none. Purchases
map forward to the first eligible observation; evaluation maps backward from
the exact horizon. SPY allows seven calendar days and BTC-USD one. There is no
interpolation or carry, and duplicate purchase mappings are rejected. Each
attempt is retained as included or with one typed reason before policy
execution.

The [accepted preparation manifest](../../experiments/inputs/historical-yahoo-preparation-manifest-v5.json)
has identity
`smartdca-historical-input-v1-4da2c9a1982b48cc821969e802118270d7a95e44cc03107e8d2846729df0e14f`,
records `policy_execution=not-run`, and binds runner-input SHA-256
`d49a5a6e0304a7da213082698990d46bec7f7cac2399533990f84a40183bec88`.
Provider exports, normalized rows, schedules, row-level outcomes, and
price-bearing ledgers remain access-controlled. Yahoo's terms and data guide
did not provide an affirmative redistribution grant
([terms](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html),
[data-provider guide](https://help.yahoo.com/kb/finance/SLN2310.html)). A
fingerprint is identity evidence, not source bytes or a licence.

### Schedules, parameters, costs, and validation

The primary historical horizons are 12, 36, and 60 months on a one-month
rolling stride. Primary coverage is `1`, `0.9`, `0.75`, and `0.5`; only the
three non-unit values enter H1/H2. The primary corrected-mean configuration is
`identity-a0-b0`: identity transform, alpha zero, beta zero, equal weights.
The three cost routes are frictionless, 10-basis-point proportional cost, and
a fixed USD 1 fee paid only when the selected budget exceeds one dollar.

The declared robustness coverage is `0.99`, `0.95`, `0.8`, `0.6`, and `0.25`.
The [locked robustness plan](../../experiments/inputs/historical-yahoo-registered-robustness-v1.json)
reuses primary monthly episodes for that coverage and constructs quarterly
episodes at 6, 24, and 120 months with deposit offsets `0,3,...,H-3` and a
three-month stride. Four alternate corrected-mean configurations remain
declared but unexecuted.

Typed exclusions cover invalid configuration or provider material, fingerprint
or semantic mismatch, nonpositive prices, unavailable or duplicate mappings,
out-of-range episodes, nonpositive comparator wealth, numerical or accounting
failure, and identity collision. Included ledgers pass causal-prefix, funding,
cash, buy-only, direct-wealth, cash/unit attribution, common-floor,
frictionless coverage, independent-DCA, lambda-one, and theorem-scope checks.

### Estimands and registered inference

For an ordered comparison `S` versus `T`, the episode gap is
`(W_S-W_T)/W_T`; `W_T <= 0` causes a typed exclusion. The primary cell
estimand is the median relative gap. Secondary summaries comprise the mean,
5th/10th/25th percentiles, extrema, worst shortfall, wealth-ratio distribution,
win/tie/loss counts, terminal cash and unit attribution, cash drag, asset
exposure, floor activation and level, purchase count, and fees.

Cash drag is terminal cash over deposits. Asset exposure is terminal asset
value over terminal wealth when positive. Floor activation is the fraction of
purchase steps with an active clipped floor, and mean floor is the arithmetic
mean over all steps. Cash plus evaluation-price unit contribution must equal
the direct terminal-wealth difference.

H1 is corrected guarded versus DCA and H2 is corrected guarded versus neutral;
both are two-sided median-gap tests. Two assets, three horizons, three non-unit
coverage values, and two comparisons form 36 cells. S1, neutral guarded versus
DCA, is secondary and not a 37th hypothesis.

Within a cell, ordered nominal episode starts are sampling units and circular
blocks of starts are resampling units. Block length equals the 12-, 36-, or
60-month horizon in one-month stride units. Each of 10,000 replicates draws
uniform circular block starts, concatenates length-`L` blocks, truncates to
exactly `N`, and recomputes the median. Write the observed median as
`theta-hat` and a replicate median as `theta-hat_b`, keeping `T` for the
right-hand policy comparator. The base seed is `20260825`; cell seeds use the
first 16 hex digits of SHA-256 over the exact pipe-separated registered fields.

The interval uses the uncentered 2.5th and 97.5th replicate percentiles with
linear interpolation at `(B-1)p`. The raw centered two-sided finite-run value
is `(1 + count(abs(theta-hat_b-theta-hat) >= abs(theta-hat))) / (B+1)`. Holm
applies to all 36 raw values using the registered deterministic tie order and
cumulative maxima. Registered family-wise alpha is `0.05`, and the accepted
report counts adjusted values strictly below `0.05` as rejections. Intervals
remain cellwise, and the Holm guarantee is conditional on valid cellwise
values. Bootstrap validity is itself conditional on the adequacy of the
ordered stationary/dependence approximation; dependence-aware resampling does
not make the episodes independent, prove the frozen block length optimal, or
create causal identification.

### Analysis labels and theorem scope

Confirmatory is reserved for H1/H2 in the sealed family. Lambda-one accounting,
architecture-only contrasts, and mechanism summaries are secondary. Registered
robustness remains post-confirmatory descriptive evidence without uncertainty.
Outcome-suggested diagnostics are exploratory.

Only frictionless rows are within the current epsilon-DCA theorem. Proportional
and fixed-fee rows are finite net-of-cost empirical robustness calculations
tagged `outside-current-safety-theorem`. An observed numerical floor under fees
would neither prove a cost theorem nor extend the gross theorem.

### Reproducibility boundary

The accepted evaluation software uses CPython 3.12 and the standard library.
Acquisition alone uses the 23-dependency lock headed by `yfinance==1.7.0` and
is not a test dependency. Protocols, versioned inputs or receipts,
content-derived run bundles, and narrative reports occupy four versioned
layers with the distinct rules fixed by [ADR 0008](../../docs/adr/0008-place-empirical-protocol-input-run-layers.md):
accepted protocol bytes are sealed, inputs or receipts receive new versions,
run-bundle identities are collision protected, and narrative reports remain
revisable while keeping artifact links and publication state accurate.

The [package review](safety-adaptivity-empirical-package-review.md) accepts
seven publication run manifests and review identity
`smartdca-empirical-package-review-v1-6cb6c1cd94b901be90ebd553a022c922e53984afafeb22948747be084b37c14f`.
Its [sanitized receipt](../../reports/experiments/runs/smartdca-empirical-package-review-v1-6cb6c1cd94b901be90ebd553a022c922e53984afafeb22948747be084b37c14f/review-receipt.json)
contains no private value. Public regeneration verifies unrestricted bundles
and that retained receipt; authorized private reconciliation additionally
replays source joins, ledgers, primary aggregates, bootstrap streams, Holm, and
robustness grouping through a separate implementation. Same-data
reconciliation is not independent-data replication.

## Claim-to-evidence map

| Claim ID | Manuscript location | Detailed authorities | Boundary |
| --- | --- | --- | --- |
| `claim-method-policy-comparisons` | Chapter 6, policies and tiers | protocol; guarded-policy definition; shared runner | identical conditions; ordered contrasts are not additive or causal |
| `claim-method-evidence-layers` | Chapter 6, evidence roles | four reports; package review | no pooled inferential unit |
| `claim-method-historical-source` | Chapter 6, historical seam | replacement protocol; provider review; source and preparation receipts | provider/client distinction; restricted rows stay private |
| `claim-method-frozen-grid` | Chapter 6 and Appendix C | both protocols; robustness plan; historical seam | no outcome-driven tuning; alternate mean settings unexecuted |
| `claim-method-estimands-inference` | Chapter 6 and Appendix C | protocol; methods note; uncertainty artifact; package review | exact median, bootstrap, finite-run p-value, and Holm rules |
| `claim-method-analysis-scope` | Chapter 6 and Appendix C | protocol; robustness plan; safety theorem; historical report | confirmatory/secondary/robustness/exploratory and gross/net boundaries |
| `claim-method-reproducibility` | Chapter 6 and Appendix D | ADR 0008; package review and receipt; clean build | regeneration is not replication; private bytes are not published |
| `claim-table-protocol-grid` | Appendix C, protocol grid | both protocols; robustness plan; this audit | readable projection of registered axes; no extension of the sealed H1/H2 family |
| `claim-table-reproducibility` | Appendix D, artifact inventory | ADR 0008; package review; this audit | distinct identity, overwrite, and revision rules; private bytes excluded |

All nine register entries include this note as their manuscript-slice audit.
External provider and software facts use the pinned client source, Yahoo Help,
Yahoo terms, and Yahoo data guide. Statistical-method claims retain the
original literature citations already reviewed in the methods synthesis.

## Artifact preservation audit

The implementation must verify before resolution that the following accepted
bytes are unchanged relative to the pre-ticket commit:

- both protocol JSON files;
- deterministic and stochastic study inputs;
- Yahoo source, normalization, preparation, and robustness-plan receipts;
- all accepted run bundles and the empirical-package review bundle.

Only manuscript source, bibliography, controls, this note, the dedicated
methodology control/check, tracked state, and build instructions are intended
to change. No new empirical output or revised scientific source edition is
created.

## Independent domain review

Initial result on 2026-09-04: changes requested. A reviewer who did not draft
the chapter compared the manuscript, claim register, both protocols, accepted
source and preparation receipts, robustness plan, uncertainty artifact,
package review, runner implementation, and rendered output. The review found:

1. fee-inclusive target budget had been conflated with asset notional;
2. the empirical CPython 3.12 runtime had been attributed incorrectly to the
   Debian manuscript-only build;
3. family-wise alpha and the conditional dependence approximation were absent;
4. the claimed public canonical replay lacked its Appendix D command and check;
5. the reproducibility-table claim described more than the table contained;
6. claim-declared method and provenance citations were not section-local or
   audit-enforced;
7. the provider replacement's metadata changes were understated;
8. the observed median reused the right-hand comparator's symbol `T`;
9. source/preparation receipt privacy had been overstated to every receipt; and
10. long artifact identities overflowed the rendered text block.

The implementation response separates target, notional, and fee algebra;
qualifies the two Python environments; adds alpha, dependence conditions,
canonical commands, and claim-local citations; narrows the table and receipt
claims; corrects provider-replacement wording and bootstrap notation; and uses
breakable identity formatting.

Source/control follow-up result on 2026-09-04: pass. The independent reviewer
rechecked the fee clamp and execution algebra, Decimal rounding, same-cost DCA
unit reference, diagnostic-field asymmetry, lambda-one ledger invariant,
protocol inheritance, alpha and dependence conditions, public canonical route,
claim-local citations and enforcement, runtime split, table and receipt scope,
and global notation. No source or control finding remains.

Rendered-output follow-up result on 2026-09-04: pass. A fresh supported build
produced an 88-page A4 PDF with no overfull boxes, undefined references or
citations, or package warnings. Independent inspection of Chapter 6 pages
45--54 and Appendices C--D pages 73--81 confirmed that tables, equations,
commands, headings, citations, long paths, hashes, run identities, and
environment variables remain legible and within the text block; the seven
underfull lines are the intended break points in immutable identifiers.
