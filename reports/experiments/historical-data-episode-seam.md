# Historical-data and rolling-episode seam

## Verdict

The historical-input seam is complete without exposing a confirmatory policy
result. Its original Alpha Vantage adapter remains reproducible, and the
reviewed Yahoo Finance replacement acquires one exact canonical yfinance export
for each locked series, fingerprints it before historical parsing, records
sanitized source receipts, normalizes only the declared price field, constructs
and reconciles every rolling episode attempt, and writes a confirmatory runner
input without executing a policy. A separate non-confirmatory fixture route
proves that one episode for each declared asset can pass through DCA, neutral
guarded, and corrected guarded accounting and emit the standard run
artifacts.[^protocol][^yahoo-protocol]

This is infrastructure evidence, not a historical performance result. No
provider price row is committed, no confirmatory policy was executed, and no
estimand or aggregate was computed or reported. The retained fixture values
are fictional; the accepted Yahoo observations and rolling inputs remain
access-controlled outside Git.

## Provider replacement and redistribution boundary

Version 1 retains the Alpha Vantage
`TIME_SERIES_DAILY_ADJUSTED` SPY adjusted-close series and
`DIGITAL_CURRENCY_DAILY` BTC/USD series. Current official documentation supports
the adjusted equity field's split/dividend semantics and the crypto endpoint's
midnight-UTC refresh, but does not publish either exact CSV header. It also does
not establish every stronger label in the frozen protocol: the SPY timezone and
fund identity are study conventions unless separately confirmed, while
`close_usd` is a normalized repository name rather than a documented provider
header. The complete source audit records these distinctions and direct primary
citations.[^provider-review]

Because premium Alpha Vantage access was unavailable, the user selected Yahoo
Finance through yfinance before any in-sample observation was retrieved. The
immutable [replacement protocol](../../experiments/protocols/safety-adaptivity-yahoo-v2.json)
inherits every non-provider study object from version 1 and locks Yahoo symbols
`SPY` and `BTC-USD`, the chart route, `yfinance==1.7.0`, explicit date and
transformation flags, exact canonical-export fingerprints, runtime currency
and timezone validation, and the authorization gate. Its provider review
distinguishes Yahoo Finance from the unaffiliated client and records both the
technical semantics and the independent protocol review. A separate
[keyless-alternatives review](../../research/notes/keyless-historical-data-provider-alternatives.md)
found no first-party-supported source that cleared both declared series,
semantics, automation, and retention gates.[^yahoo-provider-review]

Neither provider review establishes a redistribution grant. The repository
therefore contains only code, fictional fixtures, sanitized schema and coverage
receipts, and fingerprints. Real provider responses, canonical client exports,
normalized observations, and rolling episode rows remain access-controlled
under `data/raw/` or another authorized store outside Git. This applies even
when an artifact is content-addressed.[^provider-review][^yahoo-provider-review]

## Authorized Yahoo input checkpoint

After the researcher approved the fail-closed authorization gate, acquisition
and offline preparation completed against protocol SHA-256
`a5194248f7b55073e60b357c01c4993c1e50ed20c9c9672daf4780db1127f2be`.
The committed [acquisition receipt](../../experiments/inputs/historical-yahoo-receipts-v2.json)
has SHA-256
`346676eb699d4e64cee7f687a04f207d6ab4daff92abae780719368d259f97f4`;
the [normalization receipts](../../experiments/inputs/historical-yahoo-normalization-receipts-v2.json)
record:

| Series | Rows | Coverage | Field | Timezone | Currency |
| --- | ---: | --- | --- | --- | --- |
| `SPY` | 8,287 | 1993-02-01 through 2025-12-31 | `adjusted_close` | `America/New_York` | USD |
| `BTC-USD` | 4,018 | 2015-01-01 through 2025-12-31 | `close` | UTC | USD |

The [preparation validation](../../experiments/inputs/historical-yahoo-preparation-validation-v2.json)
reconciles 12,305 observations into 1,365 included episodes and zero exclusions.
Its runner input has SHA-256
`d49a5a6e0304a7da213082698990d46bec7f7cac2399533990f84a40183bec88`.
The [preparation manifest](../../experiments/inputs/historical-yahoo-preparation-manifest-v3.json)
records immutable run identity
`smartdca-historical-input-v1-c4e1222c907ffcffe6fd237fd34d97987566a415e45903577cc507fffff12d0f`,
`policy_execution=not-run`, and hashes for every private artifact. No receipt
contains a price observation or policy outcome.

The version-1 Yahoo receipts and preparation manifest and the version-2
preparation manifest are retained as pre-acceptance review history. Source
receipt version 2 changes only the redistribution label from raw-provider
wording to the accurate canonical-client-export wording; preparation manifest
version 3 binds the final reviewed source code. The two source content
fingerprints and all observed coverage are unchanged.

## Public interface

[`reproducibility.historical_data`](../../reproducibility/historical_data.py)
provides one historical preparation module with two source adapters:

- `AlphaVantageProvider` retrieves each credential-bearing request in memory;
  `acquire_historical_sources` persists its untouched body and writes a
  credential-free content-addressed source set;
- `YFinanceProvider` fails closed without the authorization attestation,
  isolates client cache state, verifies the pinned client and runtime series
  metadata, and emits one deterministic canonical CSV per declared series;
- a local-file adapter loads exact retained responses or the committed
  hand-authored fixtures through `HistoricalSourceSet`;
- `prepare_historical_input` produces source receipts, normalized rows, every
  included or excluded episode attempt, reconciliation counts, and a standard
  fingerprinted `VersionedInput`;
- `write_historical_preparation` writes the full confirmatory handoff with
  `policy_execution=not-run`; and
- `run_historical_validation` executes only an explicitly non-confirmatory
  validation source set and nests the standard public runner bundle.

Create the acquisition environment from the complete CPython 3.12 lock:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-historical.txt
```

Only after the researcher has authorization covering automated Yahoo chart
access and private retention, acquire the two locked exports. The environment
value is an attestation gate, not permission supplied by yfinance:

```bash
YAHOO_FINANCE_AUTOMATED_ACCESS_AUTHORIZED=true \
  .venv/bin/python -m reproducibility.historical_data acquire \
  --config experiments/protocols/safety-adaptivity-yahoo-v2.json \
  --source-root data/raw/yahoo-finance-accepted-v1
```

After both exports pass schema and coverage validation, construct the full
registered episode input without running a policy:

```bash
.venv/bin/python -m reproducibility.historical_data prepare \
  --config experiments/protocols/safety-adaptivity-yahoo-v2.json \
  --source-set data/raw/yahoo-finance-accepted-v1/historical-source-set.json \
  --source-root data/raw/yahoo-finance-accepted-v1 \
  --output-root data/raw/smartdca-historical-preparation-yahoo-v1
```

Both acquisition adapters and the preparation command fail with machine-readable
reason codes. Exact export paths and run directories are collision targets,
never overwrite targets. Changed source bytes create a changed source-set and
runner-input identity under the empirical artifact decision.[^empirical-layers]

## Hand-checkable fixtures and episode construction

The immutable [validation source set](../../experiments/inputs/historical-validation-sources-v1.json)
binds two provider-shaped fictional CSV fixtures:

| Fixture | Rows | Date coverage | Selected field | SHA-256 |
| --- | ---: | --- | --- | --- |
| SPY adjusted schema | 15 | 2020-01-02 to 2021-02-01 | `adjusted_close` | `ef89a54abb12a7c074bf8d6fdc4ee0ce9dce0f1bedcabf6bccc3d4d0944a0df4` |
| BTC/USD schema | 14 | 2020-01-01 to 2021-02-01 | `close` for requested `market=USD` | `9b0342e9c39a0be17ac2ae7ff61485541a4eb3422b8f48377cd0a815bfefcd74` |

The SPY fixture gives raw close 280 and adjusted close 140 on its declared
split row, so the normalized price route is visibly not the raw-close route.
Its January nominal deposit maps from the New Year's Day boundary to January 2;
February 1 maps across a weekend to February 3; and the exact 2021-01-01 horizon
maps backward to 2020-12-31. The BTC fixture retains weekend first-of-month
dates without an equity-calendar shift. No route creates an interpolated price
or an invented intraday timestamp.

For each asset, January and February 2020 starts form overlapping 12-month
episodes with eleven shared mapped purchase dates. A March start lacks an
evaluation endpoint within the registered tolerance. The attempt ledger retains
both exclusions as `unavailable_mapped_evaluation_date`, including the exact
horizon, tolerance, and nearest observed dates. The resulting reconciliation is
29 observations, six attempts, four included episodes, two exclusions, and two
selected validation episodes.

Extending either fixture with later rows changes its immutable source and input
identity but leaves every earlier DCA, neutral, and corrected transaction
decision unchanged. The shared runner separately replays every truncated
purchase prefix.

## Immutable validation bundle

The accepted non-confirmatory bundle is
[`smartdca-historical-validation-v1-9523135380007cb4597b991600acb7d5b0c244e955fb17b36d244d6158155a10`](runs/smartdca-historical-validation-v1-9523135380007cb4597b991600acb7d5b0c244e955fb17b36d244d6158155a10/manifest.json).
Its outer manifest binds:

- protocol SHA-256 `a508b4f064dcb3930f137e7754180ca0ec43749680278acb5b42fe2345c8d6e4`;
- exact source-set SHA-256 `2138cd2e16856dbc6695ae8183f38153b8c91660cf57e4773ebc21fbed5eed36`;
- generated runner-input SHA-256 `d44c18dae06138671bd530eec956a667f80df1bec664e0c9bf9e61c51355b24e`;
- historical module SHA-256 `82d947a07737168a39d6f8876413da0bc3982b2a9b7f47735a820429c1488baa`;
- shared runner SHA-256 `7fd480fd07a80a914bc02aa133a59d975fc2f756c7bc75de052771c1ff256fee`;
  and
- CPython 3.12 with no third-party dependency.

The two selected episodes cross four primary coverage values, one primary
corrected-mean configuration, and three cost routes. The nested standard bundle
therefore contains 72 complete policy ledgers and 72 three-way comparison rows,
plus its manifest, validation receipts, aggregates, policy table, and
figure-ready data. The outer validation labels every result
`non-confirmatory-infrastructure-validation` and records confirmatory aggregate
outcomes as `unopened-and-unreported`. This report intentionally gives no
fixture performance number.

## Reproduction and limits

Rebuild the committed validation bundle into a fresh directory:

```bash
python3.12 -m reproducibility.historical_data validate \
  --config experiments/protocols/safety-adaptivity-v1.json \
  --source-set experiments/inputs/historical-validation-sources-v1.json \
  --source-root . \
  --output-root "$(mktemp -d)"
```

Then run:

```bash
python3.12 -m unittest reproducibility.checks.check_historical_data_episode_seam
```

The public-contract checks regenerate every accepted validation artifact
byte for byte, exercise typed acquisition and parsing failures, verify adjusted
field and calendar semantics, retain missing endpoints, check overlap and
future-extension prefixes, enforce the Yahoo authorization and provenance
boundary, and prove the confirmatory preparation command stops before policy
execution.

The initial
[`smartdca-historical-validation-v1-dccb2033929ec8ccb4e90245582fe3b73126c57d16c5bbb0355a47329cca132a`](runs/smartdca-historical-validation-v1-dccb2033929ec8ccb4e90245582fe3b73126c57d16c5bbb0355a47329cca132a/manifest.json)
and intermediate
[`smartdca-historical-validation-v1-bee2ccc740eeaa7b0c6be4aa300934c993f525dfce4a0125e2d0044895a2cddd`](runs/smartdca-historical-validation-v1-bee2ccc740eeaa7b0c6be4aa300934c993f525dfce4a0125e2d0044895a2cddd/manifest.json)
and
[`smartdca-historical-validation-v1-80dbd990f0afd98ce553d229cb470fe874bac1ec736763855c7efec755797e62`](runs/smartdca-historical-validation-v1-80dbd990f0afd98ce553d229cb470fe874bac1ec736763855c7efec755797e62/manifest.json)
bundles are retained as review history. The accepted identity adds the Yahoo
adapter contract while preserving protocol-bound live
provenance, full schedules for excluded episodes, durable dataset-failure
attempts, actual-evidence-bound rejected identities, mode-correct input counts,
and patch-independent CPython 3.12 runtime metadata.

This checkpoint establishes the historical-data and episode interface and an
accepted Yahoo source/input handoff. It does not estimate historical behavior,
test a confirmatory hypothesis, run the registered bootstrap, or support a
claim of market superiority. Ticket 05 may consume the exact private runner
input only under the replacement protocol and retained receipt identities; any
refresh or design change receives a new identity.[^effort-spec]

[^effort-spec]: [Safety-adaptivity empirical evaluation specification](../../.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/spec.md)
[^protocol]: [Frozen safety-adaptivity protocol](../../experiments/protocols/safety-adaptivity-v1.json)
[^yahoo-protocol]: [Frozen Yahoo Finance replacement protocol](../../experiments/protocols/safety-adaptivity-yahoo-v2.json)
[^provider-review]: [Alpha Vantage historical-data provider review](../../research/notes/alpha-vantage-historical-data-provider-review.md)
[^yahoo-provider-review]: [Yahoo Finance historical-data provider review](../../research/notes/yahoo-finance-historical-data-provider-review.md)
[^empirical-layers]: [Place empirical protocols, inputs, and run bundles in versioned layers](../../docs/adr/0008-place-empirical-protocol-input-run-layers.md)
