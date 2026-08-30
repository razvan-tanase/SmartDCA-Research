# Historical-data and rolling-episode seam

## Verdict

The historical-input seam is executable without exposing a confirmatory result.
It acquires one exact response for each locked Alpha Vantage request, fingerprints
the untouched bytes before parsing, records credential-free source receipts,
normalizes only an unambiguous declared price field, constructs and reconciles
every rolling episode attempt, and writes a confirmatory runner input without
executing a policy. A separate non-confirmatory fixture route proves that one
episode for each declared asset can pass through DCA, neutral guarded, and
corrected guarded accounting and emit the standard run artifacts.[^protocol]

This is infrastructure evidence, not a historical performance result. No
licensed Alpha Vantage market response was available in the execution
environment, no provider price row is committed, and no confirmatory policy
aggregate was computed or reported. The retained fixture values are fictional.

## Provider and redistribution boundary

The locked requests remain the Alpha Vantage
`TIME_SERIES_DAILY_ADJUSTED` SPY adjusted-close series and
`DIGITAL_CURRENCY_DAILY` BTC/USD series. Current official documentation supports
the adjusted equity field's split/dividend semantics and the crypto endpoint's
midnight-UTC refresh, but does not publish either exact CSV header. It also does
not establish every stronger label in the frozen protocol: the SPY timezone and
fund identity are study conventions unless separately confirmed, while
`close_usd` is a normalized repository name rather than a documented provider
header. The complete source audit records these distinctions and direct primary
citations.[^provider-review]

The reviewed terms do not clearly grant response-data redistribution. The
repository therefore contains only code, fictional fixtures, sanitized schema
and coverage receipts, and fingerprints. Any real raw response and normalized
observation output must remain access-controlled under `data/raw/` or another
authorized store outside Git unless written redistribution permission is
obtained. This applies even though a response is content-addressed.[^provider-review]

## Public interface

[`reproducibility.historical_data`](../../reproducibility/historical_data.py)
provides one historical preparation module with two source adapters:

- `AlphaVantageProvider` retrieves each credential-bearing request in memory;
  `acquire_historical_sources` persists its untouched body and writes a
  credential-free content-addressed source set;
- a local-file adapter loads exact retained responses or the committed
  hand-authored fixtures through `HistoricalSourceSet`;
- `prepare_historical_input` produces source receipts, normalized rows, every
  included or excluded episode attempt, reconciliation counts, and a standard
  fingerprinted `VersionedInput`;
- `write_historical_preparation` writes the full confirmatory handoff with
  `policy_execution=not-run`; and
- `run_historical_validation` executes only an explicitly non-confirmatory
  validation source set and nests the standard public runner bundle.

The live acquisition command requires `ALPHAVANTAGE_API_KEY`. It writes the key
to neither a URL receipt nor an artifact:

```bash
python -m reproducibility.historical_data acquire \
  --config experiments/protocols/safety-adaptivity-v1.json \
  --source-root data/raw/alpha-vantage-accepted-v1
```

After authorized responses pass schema and coverage validation, construct the
full registered episode input without running a policy:

```bash
python -m reproducibility.historical_data prepare \
  --config experiments/protocols/safety-adaptivity-v1.json \
  --source-set data/raw/alpha-vantage-accepted-v1/historical-source-set.json \
  --source-root data/raw/alpha-vantage-accepted-v1 \
  --output-root data/raw/smartdca-historical-preparation
```

Both commands fail with machine-readable reason codes. Exact response paths and
run directories are collision targets, never overwrite targets. A changed
provider body creates a changed source-set and runner-input identity under the
empirical artifact decision.[^empirical-layers]

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
[`smartdca-historical-validation-v1-dccb2033929ec8ccb4e90245582fe3b73126c57d16c5bbb0355a47329cca132a`](runs/smartdca-historical-validation-v1-dccb2033929ec8ccb4e90245582fe3b73126c57d16c5bbb0355a47329cca132a/manifest.json).
Its outer manifest binds:

- protocol SHA-256 `a508b4f064dcb3930f137e7754180ca0ec43749680278acb5b42fe2345c8d6e4`;
- exact source-set SHA-256 `2138cd2e16856dbc6695ae8183f38153b8c91660cf57e4773ebc21fbed5eed36`;
- generated runner-input SHA-256 `d44c18dae06138671bd530eec956a667f80df1bec664e0c9bf9e61c51355b24e`;
- historical module SHA-256 `cfb39f904fdbdebf079db744693fc5f7ffe91f961a8a60c91133d277e3555304`;
- shared runner SHA-256 `7fd480fd07a80a914bc02aa133a59d975fc2f756c7bc75de052771c1ff256fee`;
  and
- CPython 3.12.14 with no third-party dependency.

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
python -m reproducibility.historical_data validate \
  --config experiments/protocols/safety-adaptivity-v1.json \
  --source-set experiments/inputs/historical-validation-sources-v1.json \
  --source-root . \
  --output-root "$(mktemp -d)"
```

Then run:

```bash
python -m unittest reproducibility.checks.check_historical_data_episode_seam
```

The 18 public-contract checks regenerate every committed validation artifact
byte for byte, exercise typed acquisition and parsing failures, verify adjusted
field and calendar semantics, retain missing endpoints, check overlap and
future-extension prefixes, and prove the confirmatory preparation command stops
before policy execution.

This checkpoint establishes the historical-data and episode interface; it does
not supply a licensed Alpha Vantage input, estimate historical behavior, test a
confirmatory hypothesis, run the registered bootstrap, or support a claim of
market superiority. Ticket 05 still requires authorized provider responses
whose exact headers and date coverage pass these gates before it may execute the
frozen confirmatory input.[^effort-spec]

[^effort-spec]: [Safety-adaptivity empirical evaluation specification](../../.scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/spec.md)
[^protocol]: [Frozen safety-adaptivity protocol](../../experiments/protocols/safety-adaptivity-v1.json)
[^provider-review]: [Alpha Vantage historical-data provider review](../../research/notes/alpha-vantage-historical-data-provider-review.md)
[^empirical-layers]: [Place empirical protocols, inputs, and run bundles in versioned layers](../../docs/adr/0008-place-empirical-protocol-input-run-layers.md)
