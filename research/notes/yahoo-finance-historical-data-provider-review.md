# Yahoo Finance historical-data provider review

This note is **pre-outcome static research** for ticket 04's proposed move from
Alpha Vantage to Yahoo Finance through `yfinance`. It used only Yahoo legal,
Yahoo Finance help and symbol pages, and the official `yfinance` repository at
release `1.7.0` (commit `3d9d2f0cacb662bff689874cd6113bae3a30a885`),
accessed 2026-08-31. No market-data endpoint or historical-data request was
made, no SPY or BTC-USD history was downloaded, and no policy outcome was
computed.

One source-search result unexpectedly displayed one current SPY quote. The
value is intentionally not repeated or used. No endpoint or history row was
requested; the quote falls after the frozen 2025-12-31 data cutoff and did not
inform the user-selected provider or any inherited study choice.

## Decision

Yahoo Finance is technically reachable through a pinned `yfinance` client,
but this is not a drop-in replacement for the frozen Alpha Vantage requests.
The provider would be **Yahoo Finance** and `yfinance` would be an unaffiliated
client: its own README says it uses Yahoo's publicly available APIs, is not
affiliated with or endorsed by Yahoo, and directs users to Yahoo's terms for
data-use rights
([`yfinance` README](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/README.md#L15-L26)).

The proposed acquisition contract should pin `yfinance==1.7.0`, use explicit
dates and flags, retain Yahoo's returned metadata, and identify every retained
table as **client-processed Yahoo Finance data**. The public history surface
does not expose exact response bytes or headers: it requests Yahoo's chart
route, decodes JSON, performs cleanup and transformations, and returns a
`DataFrame`
([history request and JSON decoding](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/scrapers/history.py#L275-L318),
[post-processing and return path](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/scrapers/history.py#L380-L640)).
Consequently, a fingerprint of a serialized `DataFrame` is not a fingerprint
of the provider response. Satisfying ticket 04's exact-source-byte requirement
would require a separately reviewed capture seam around the chart response;
otherwise a revised protocol must explicitly define and fingerprint a
canonical client-output artifact instead.

This static review does not establish authorization for live retrieval.
Yahoo's current U.S. Terms prohibit automated access or collection without
express prior permission and prohibit commercial reuse absent an express
exception. Provider authorization is therefore a gate, not something supplied
by installing `yfinance`
([Yahoo Terms of Service, “Member conduct” and “Use of Services,” last updated
4 August 2026](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html)).

## Provider, client, and series identifiers

Yahoo Finance's static symbol pages label `SPY` as State Street SPDR S&P 500
ETF Trust and `BTC-USD` as Bitcoin paired with USD
([SPY](https://finance.yahoo.com/quote/SPY/),
[BTC-USD](https://finance.yahoo.com/quote/BTC-USD/)). These pages support the
requested ticker strings and display identities. They do not, by themselves,
establish an investability methodology, a total-return-index identity, or the
venue and aggregation method behind `BTC-USD`.

Yahoo's provider guide lists Commodity Systems, Inc. for U.S.-equity
historical data and lists both Coinbase and CoinMarketCap for global
cryptocurrency coverage, but it does not map either reviewed symbol to one
upstream supplier. Receipts should therefore name Yahoo Finance as the source
service and leave the exact upstream supplier unverified unless response
metadata or provider documentation binds it
([Yahoo Finance exchanges and data providers](https://help.yahoo.com/kb/finance/SLN2310.html)).

At the reviewed release, `yfinance` builds history requests against Yahoo's
`query2.finance.yahoo.com/v8/finance/chart/{ticker}` route
([base host](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/const.py#L1-L3),
[chart path](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/scrapers/history.py#L252-L291)).
That implementation fact does not convert the route into a documented,
provider-supported historical-data API or supply a service-level guarantee.

## Locked client call and field semantics

For one ticker at a time, the reproducible call should lock all outcome-relevant
options instead of inheriting defaults:

| Option | Locked value | Reason |
| --- | --- | --- |
| `interval` | `"1d"` | The study declares daily observations. |
| `start` | explicit eligible start | Avoid a clock-relative `period`. |
| `end` | `"2026-01-01"` | `end` is exclusive, so this bounds the request at the 2025-12-31 cutoff. |
| `auto_adjust` | `False` | Preserve Yahoo's raw `Close` and `Adj Close` fields for explicit selection and audit. |
| `actions` | `True` | Retain dividend, split, and capital-gain event columns where supplied. |
| `repair` | `False` | Prevent heuristic reconstruction or value repair. |
| `keepna` | `True` | Preserve all-null rows returned by Yahoo for explicit seam handling. |
| `rounding` | `False` | Prevent optional client rounding. |
| `prepost` | `False` | Exclude extended-hours data; fixed even though the requested interval is daily. |
| `threads` | `False` when using `download` | Make acquisition serial and its request log easier to audit. |
| `ignore_tz` | `False` when using `download` | Retain the client-localized timezone instead of the daily default's timezone stripping. |
| `progress` | `False` when using `download` | Keep the acquisition channel machine-readable. |
| `multi_level_index` | explicit when using `download` | Freeze the returned schema rather than inherit a library default. |

The reviewed `download` signature defaults `auto_adjust=True`, `actions=False`,
`repair=False`, `keepna=False`, `threads=True`, and daily `ignore_tz=True`; it
also documents inclusive `start`, exclusive `end`, supported intervals,
rounding, timeout, and schema controls
([`download` contract](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/multi.py#L54-L113),
[daily timezone default](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/multi.py#L125-L145)).
`Ticker.history` has the same date boundaries but defaults `actions=True`; the
adapter must record which public surface it uses
([`Ticker.history` contract](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/scrapers/history.py#L104-L150)).

For SPY, select the returned `Adj Close` without auto-adjust transformation or
repair. Yahoo defines adjusted close as close after applicable split and
dividend-distribution adjustments and describes its split and dividend
multipliers
([Yahoo Finance Help, “What is the adjusted close?”](https://help.yahoo.com/kb/SLN28256.html)).
For BTC-USD, select the unmodified returned `Close` column. Static sources do
not establish that Yahoo's `Adj Close` always equals `Close` for this symbol,
so `auto_adjust=True` must not be used to infer that equality.

`auto_adjust=True` is a client transformation: `yfinance` computes
`Adj Close / Close`, applies that ratio to open, high, and low, drops the raw
OHLC columns, and renames adjusted values back to OHLC
([implementation](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/utils.py#L506-L523)).
`actions=True` controls whether event columns survive in the returned table;
the history implementation requests and parses dividends, splits, and capital
gains before that output filter
([event request and parsing](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/scrapers/history.py#L252-L266),
[event merge and output filter](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/scrapers/history.py#L437-L523)).
Action columns are audit evidence; they must not be counted again on top of the
SPY adjusted-close price series.

`repair=True` can alter adjusted values, reconstruct missing data from finer
intervals, and repair currency-unit, split, dividend, and zero-value problems;
the official documentation also acknowledges possible false positives
([price-repair documentation](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/doc/source/advanced/price_repair.rst#L1-L18),
[reconstruction and false-positive warning](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/doc/source/advanced/price_repair.rst#L100-L126)).
Keeping it false is necessary for a provider-faithful input and prevents
repair-driven extra history requests.

## Date and timezone semantics

`yfinance` interprets a timezone-naive date or datetime at midnight in the
ticker's exchange timezone, then converts it to epoch seconds for `period1`
and `period2`
([date parser](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/utils.py#L454-L471),
[request-bound conversion](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/scrapers/history.py#L194-L258)).
The exchange timezone is obtained from Yahoo response metadata and persisted
in a local cache
([timezone retrieval](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/base.py#L138-L199),
[cache documentation](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/doc/source/advanced/caching.rst#L1-L18)).

For daily data, the client converts timestamps into that returned exchange
timezone, applies a DST-date correction, and relabels each row at local
midnight. The multi-ticker `download` daily default subsequently removes the
timezone unless `ignore_tz=False`
([daily localization](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/scrapers/history.py#L418-L425),
[daily-midnight labeling](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/scrapers/history.py#L492-L501),
[`download` timezone stripping](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/multi.py#L209-L246)).
The receipt must therefore retain the runtime `exchangeTimezoneName`, the
timezone-aware pre-normalization index, and the adapter's later normalization.
It must reject rather than silently relabel a runtime timezone inconsistent
with the revised protocol's `America/New_York` or UTC convention.

## Authentication, cache state, and determinism

The reviewed history signature has no API-key parameter. `yfinance` creates a
session, obtains and persists Yahoo cookies, fetches and reuses a crumb, and
switches between `basic` and `csrf` cookie strategies on failure; it can also
continue to the chart route without a crumb after some transient or rate-limit
failures
([session and cookie state](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/data.py#L80-L109),
[cookie/crumb strategies](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/data.py#L226-L400),
[request and retry behavior](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/data.py#L425-L508)).
The CSRF path also submits Yahoo cookie-consent fields automatically
([consent path](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/data.py#L291-L348)).
These are client-managed request side effects, not proof of provider
authorization.

The acquisition must run in a fresh process with an explicit isolated cache
directory. The receipt may record anonymous versus explicitly authorized
login mode and the cookie strategy, but must never store cookie values, crumbs,
CSRF tokens, or login cookies. `yfinance` documents that its persistent cache
contains both timezones and cookies and can be redirected
([cache documentation](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/doc/source/advanced/caching.rst#L4-L18)).

No reviewed source promises immutable live results. Deterministic replay
begins only after an accepted source artifact is immutably retained: pin the
client and complete dependency lock, record all flags and the Python runtime,
serialize with a versioned canonical schema, fingerprint before normalization,
and replay without network access. The receipt must also record every
auxiliary request, because an uncached ticker can trigger a timezone preflight
and cookie/crumb traffic before the declared chart request
([timezone preflight](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/base.py#L171-L199),
[cookie/crumb traffic](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/data.py#L226-L400)).

## Dependency and redistribution decision

Pin the direct dependency to `yfinance==1.7.0`; the reviewed tag declares that
version, Apache-2.0 for the client code, Python 3.12 support, and runtime
dependencies including pandas, NumPy, and `curl_cffi`
([version](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/version.py#L1),
[package metadata](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/pyproject.toml#L5-L47)).
The release prefers `curl_cffi` with browser impersonation and falls back to
plain `requests` when unavailable; pin and record the selected backend because
the project warns that fallback traffic may be rate-limited or blocked
([HTTP backend](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/_http.py#L1-L12),
[session construction](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/yfinance/_http.py#L58-L69)).
The Apache license covers `yfinance` code, not Yahoo-supplied data; the project
README makes that distinction explicitly
([legal notice](https://github.com/ranaroussi/yfinance/blob/3d9d2f0cacb662bff689874cd6113bae3a30a885/README.md#L66-L77)).

Yahoo's Terms say service use does not transfer ownership, prohibit
reproduction, modification, distribution, derivative works, and commercial
exploitation absent explicit written permission, and prohibit automated data
collection without express prior permission
([Yahoo Terms of Service, “Member conduct,” “Use of Services,” and “Ownership
and Reuse”](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html#s2)).
Yahoo Finance's own data-provider guide is more direct: information displayed
on or provided by Yahoo Finance must not be redistributed
([Yahoo Finance exchanges and data providers](https://help.yahoo.com/kb/finance/SLN2310.html)).
The separate Yahoo Developer API terms do not identify the chart route used
by `yfinance` as a licensed API and require compliance with API-specific
documentation and application-identification requirements where applicable
([Yahoo Developer API Terms of Use](https://legal.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/index.html)).

The conservative repository decision is therefore:

- do not perform the live automated retrieval until the researcher has
  provider permission that covers this route and research use;
- do not commit or redistribute raw Yahoo responses, client-returned rows, or
  normalized observations;
- if permission covers retention, keep accepted bytes or canonical client
  output immutable and access-controlled outside Git; and
- commit only code, fictional fixtures, field-level schemas, sanitized
  receipts, coverage metadata, and cryptographic fingerprints.

This is a conservative publication policy, not a legal conclusion that every
private research or archival use is forbidden. A broader data publication
requires an affirmative license or written provider permission.

## Claims left for authorized runtime verification

| Claim | Static status | Required handling |
| --- | --- | --- |
| `SPY` has complete daily coverage from 1993-02-01 through the cutoff | Not established. | Record returned coverage and reject if insufficient. |
| Runtime `SPY` currency and timezone are USD and `America/New_York` | Not established by the static symbol page. | Retain and validate Yahoo metadata. |
| Runtime SPY `Adj Close` and action fields implement the documented semantics without missing or anomalous rows | Not established. | Preserve raw fields, validate schema, and audit fixtures without opening aggregate outcomes. |
| `BTC-USD` is a daily spot series with a UTC close boundary | The symbol pairing is established; “spot,” venue/aggregation, and close-boundary semantics are not. | Obtain provider documentation or retain bounded protocol language and validate runtime metadata. |
| The exact upstream supplier for each symbol is known | Yahoo lists relevant supplier categories but does not map these symbols to a supplier. | Preserve Yahoo Finance as source service; record an upstream supplier only with series-specific evidence. |
| BTC-USD `Adj Close` always equals raw `Close` and has no actions | Not established. | Select raw `Close`; retain action fields only as audit evidence. |
| One public client call equals one provider response | False as an operational assumption. | Account for timezone and cookie/crumb requests and separately identify the price-history response. |
| A repeated live call returns identical bytes or rows | Not established and not promised. | Accept once under a new input identity, retain immutably, and replay offline. |
| Raw or normalized Yahoo rows may be published | No affirmative grant located. | Keep them outside Git unless written permission says otherwise. |

These findings do not amend immutable protocol `safety-adaptivity-v1`, which
names Alpha Vantage and Alpha Vantage-specific requests. Replacing the provider,
request surface, source-byte rule, authentication model, or client
transformations requires a new protocol and input identity before any target
history is accessed.

## Independent protocol review

On 2026-08-31, the proposed
`experiments/protocols/safety-adaptivity-yahoo-v2.json` was reviewed against
this note and `safety-adaptivity-v1` without accessing market data. The exact
reviewed draft had SHA-256
`b4291c5147ac13a5ae355cc6654a210e39e4dc8058113393b317b8b48050cb03`.
A parsed top-level comparison found changes only in protocol identity and
registration metadata, disclosures, historical datasets,
retrieval/fingerprint metadata, and the acquisition-only runtime dependency.
`episode_design`, `coverage`,
`corrected_mean`, `cost_scenarios`, `hypotheses`, `estimands`, `multiplicity`,
`uncertainty`, `analysis_tiers`, `exclusions`, `robustness_design`,
`canonical_run`, and `runner_contract` are unchanged. The non-provider study
design therefore passes the inheritance check.

The proposed protocol also correctly uses `SPY` and `BTC-USD`, explicit
eligible starts, exclusive `end="2026-01-01"`, `interval="1d"`,
`auto_adjust=false`, `actions=true`, `repair=false`, `keepna=true`,
`prepost=false`, and `rounding=false`. It distinguishes Yahoo Finance as
provider from the pinned `yfinance==1.7.0` acquisition dependency, describes
the canonical CSV as a client export rather than provider bytes, and preserves
the bounded BTC-USD spot-proxy language.

Result: **pass with required corrections before live acquisition**.

1. The retrieval and redistribution language calls the data “personal-use
   source material” and specifies no researcher credential, but that does not
   satisfy Yahoo's express-prior-permission requirement for automated
   collection. Add a recorded provider-authorization status and make live
   retrieval conditional on permission covering the chart route, research
   use, and retention. Preserve the existing no-redistribution rule.
2. Dataset field `endpoint: "Ticker.history"` names a client method, not a
   Yahoo provider endpoint. Separate `client_method: "Ticker.history"` from
   the provider route, or rename the field so receipts cannot misidentify the
   client as the provider.
3. Dataset `timezone` values are frozen normalization targets, while the
   actual Yahoo `exchangeTimezoneName` values remain runtime evidence. Name
   that distinction explicitly and require a typed rejection on mismatch
   rather than silently relabeling the client-localized index.
4. Make the acquisition's isolated cache, cookie/crumb redaction, selected
   HTTP backend, full dependency lock, and client source commit explicit
   receipt inputs. `yfinance` can perform timezone, cookie, crumb, and consent
   requests around the one declared `Ticker.history` call; `one_export_per_dataset`
   must not be interpreted as one provider response.
5. With `actions=true`, retain every action column supplied by the client,
   including `Capital Gains` where present. Keep those columns as audit
   evidence and do not strengthen Yahoo's documented split-and-dividend
   adjusted-close semantics.

Until these corrections are incorporated and re-reviewed, the protocol is a
validly separated draft but does not clear the provider authorization,
provenance, or timezone gates described in this note.

### Final re-review

The corrected draft was re-reviewed on 2026-08-31 at SHA-256
`a5194248f7b55073e60b357c01c4993c1e50ed20c9c9672daf4780db1127f2be`,
again without market-data access. The parsed non-provider study objects remain
identical to version 1. The draft now separates the Yahoo chart route from
`yfinance.Ticker.history`, distinguishes normalization timezones from runtime
source timezones and requires equality, pins the source commit and complete
dependency lock, records the HTTP backend, isolates and redacts client state,
acknowledges auxiliary requests, and retains all returned SPY action columns.
Corrections 2 through 5 therefore pass.

Correction 1 is mechanically gated but not externally resolved. The new
`YAHOO_FINANCE_AUTOMATED_ACCESS_AUTHORIZED=true` precondition prevents an
accidental request, but a researcher-set environment value is not itself
Yahoo's express prior permission. Before setting it, the retained private
authorization record must identify the grant that covers the chart route,
automated research access, and local retention; the sanitized receipt or
ticket should bind that record without disclosing it. “Personal-use source
material” must not be read as an independent authorization supplied by
`yfinance`.

Final result: **protocol alignment passes; live Yahoo acquisition remains
blocked on external provider authorization**. The authorization gate must fail
closed until that evidence exists.

## Authorized runtime receipt

After the reviewed protocol was committed at `bae0faf`, the researcher
affirmatively approved the guarded acquisition prompt confirming authorization
for Yahoo chart-route automation and private research retention. The command
then set `YAHOO_FINANCE_AUTOMATED_ACCESS_AUTHORIZED=true` for that process only.
The underlying authorization material and all yfinance cookie or crumb state
remain private and are not repository artifacts.

The acquisition ran at `2026-08-31T10:02:47Z`. A pre-acceptance receipt review
corrected one provenance label from “provider bytes” to “canonical client
export,” without changing either retained export or its content fingerprint.
The accepted version-2 source-set receipt has SHA-256
`346676eb699d4e64cee7f687a04f207d6ab4daff92abae780719368d259f97f4`;
the provisional version-1 receipt remains preserved as review history.
The [sanitized acquisition receipt](../../experiments/inputs/historical-yahoo-receipts-v2.json)
binds it to the independently reviewed protocol SHA-256, client source commit,
complete dependency-lock fingerprint, exact call arguments, source timezones,
source currencies, canonical-export fingerprints, and the conservative
no-redistribution decision. Provider response bodies and headers remain
unavailable through the public yfinance seam, as preregistered.

Offline preparation accepted both sources without executing a policy. The
[normalization receipts](../../experiments/inputs/historical-yahoo-normalization-receipts-v2.json)
record these audited, outcome-free facts:

| Dataset | Rows | Coverage | Selected field | Source timezone | Source currency |
| --- | ---: | --- | --- | --- | --- |
| `spy-adjusted-daily` | 8,287 | 1993-02-01 through 2025-12-31 | `adjusted_close` | `America/New_York` | USD |
| `btc-usd-daily` | 4,018 | 2015-01-01 through 2025-12-31 | `close` | UTC | USD |

The [preparation validation](../../experiments/inputs/historical-yahoo-preparation-validation-v2.json)
binds 12,305 observations to 1,365 included rolling episodes, zero excluded
episodes, runner-input SHA-256
`d49a5a6e0304a7da213082698990d46bec7f7cac2399533990f84a40183bec88`,
and `policy_execution=not-run`. The corresponding
[preparation manifest](../../experiments/inputs/historical-yahoo-preparation-manifest-v5.json)
records run identity
`smartdca-historical-input-v1-4da2c9a1982b48cc821969e802118270d7a95e44cc03107e8d2846729df0e14f`.
No provider price value, episode price, policy decision, estimand, or aggregate
outcome is included in these receipts or this note.
