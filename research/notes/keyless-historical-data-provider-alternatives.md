# Keyless historical-data provider alternatives

This note records **pre-outcome static research** requested after Yahoo
Finance authorization remained unresolved. It reviews whether Stooq or another
first-party, keyless automated source can supply both the declared investable
S&P 500 proxy and BTC/USD daily history through 2025-12-31. Only provider-owned
documentation, help, product, and legal pages were used, accessed 2026-08-31.
No symbol-specific data endpoint was called, no SPY or BTC price history was
downloaded or retained, and no policy outcome was computed. The separate
[Yahoo Finance review](yahoo-finance-historical-data-provider-review.md)
contains the earlier out-of-cutoff quote disclosure.

## Decision

No reviewed keyless source clears both the technical and authorization gates.
Stooq cannot be selected from first-party static evidence because its exact
symbols, adjustment rules, timezone/date semantics, coverage commitment, and
automation or redistribution license could not be established. Coinbase
Exchange documents a public BTC-USD candle interface, but the reviewed
documentation identifies no S&P 500 investable proxy and does not promise the
required BTC history. State Street identifies SPY and publishes fund materials,
but does not document a keyless automated daily adjusted-market-price export.

Accordingly, do not replace Yahoo Finance with Stooq on the basis of
third-party clients, remembered symbol conventions, or an empirical inspection
of returned rows. The viable next paths are to obtain documented Yahoo
permission, procure a licensed provider, or preregister a split-provider design
after an authorized SPY source is found. Any such change requires a new
protocol identity before target observations are accessed.

## Stooq

Stooq has first-party historical-download and bulk-history landing paths
([historical download](https://stooq.com/q/d/),
[bulk history](https://stooq.com/db/h/)). On the review date, static access to
those pages returned only Stooq's browser-verification challenge. No
symbol-specific download route was called.

No accessible first-party data dictionary or legal page was found that binds
all of the following:

- `SPY.US`, `SPY`, or another exact Stooq identifier to an investable S&P 500
  fund;
- an exact Stooq BTC/USD identifier and its venue or aggregation method;
- whether daily equity values are raw, split-adjusted, dividend-adjusted, or a
  total-return construction;
- the daily date boundary or timezone;
- historical coverage through 2025-12-31; or
- permission for automated retrieval, retention, and redistribution.

These are evidence gaps, not findings that Stooq lacks the instruments. They
prevent a preregistered, auditable selection. A URL that happens to return CSV
is not itself a data license or a stable semantics contract. **Stooq is not
accepted.**

## Coinbase Exchange: BTC-only partial candidate

Coinbase Exchange distinguishes authenticated trading APIs from public market
data APIs
([Exchange API introduction](https://docs.cdp.coinbase.com/exchange/introduction/welcome)).
Its official product documentation uses `BTC-USD` for a product whose base is
BTC and quote currency is USD
([products](https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-all-known-trading-pairs)).
This establishes a provider-owned, keyless market-data surface and the exact
pair identity.

The public Exchange candle route is
`GET /products/{product_id}/candles`. It supports `86400`-second buckets, limits
one request to 300 candles, requires multiple explicit start/end ranges for a
larger span, identifies each returned time as the bucket start, and warns that
historical rates may be incomplete and that intervals without ticks have no
published row
([Get product candles](https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-candles)).
The static page does not promise coverage from 2015-01-01 through 2025-12-31,
state inclusive/exclusive boundary behavior strongly enough for this protocol,
or separately define a daily timezone label. It documents raw candle OHLCV,
not an adjusted-close or total-return field.

The candle specification declares no request security, but the documentation
also binds market-data use to separate terms
([Coinbase Market Data Terms of Use](https://www.coinbase.com/legal/market_data)).
The reviewed first-party material did not establish permission for durable
research archiving or redistribution. A public endpoint is therefore evidence
of keyless technical access, not an affirmative license to commit or publish
observations.

Coinbase is therefore a technically documented **BTC-only conditional
candidate**. It does not solve the S&P 500 series, and its exact coverage and
date mapping remain runtime acceptance checks. Selecting it would also replace
one-source retrieval with a deterministic sequence of bounded requests and
would require a new protocol and source-bundle identity.

## State Street: SPY identity but no required history interface

State Street's official fund page identifies `SPY` as the State Street SPDR
S&P 500 ETF Trust and offers fund documents, historical distributions, and a
product-data workbook
([SPY fund page](https://www.ssga.com/us/en/intermediary/etfs/state-street-spdr-sp-500-etf-trust-spy)).
The reviewed page does not document a public automated API or CSV that supplies
daily adjusted market prices over the required period. Nor does it define the
timezone and date boundary or grant redistribution rights for such a series.
NAV, distribution history, and periodic total-return performance are not an
interchangeable substitute for a documented daily adjusted market-price
series. **State Street is not accepted as the historical-price source.**

## Acceptance matrix

| Candidate | Exact target series | Keyless automation | Adjustment and date semantics | Coverage through cutoff | Retention / redistribution | Result |
| --- | --- | --- | --- | --- | --- | --- |
| Stooq | Not established from accessible first-party docs | Not established | Not established | Not established | Not established | Reject |
| Coinbase Exchange | `BTC-USD` only | Public market-data API; candle operation declares no request security | Raw 86400-second candle; some boundary/timezone semantics unresolved | Not promised; incomplete intervals warned | Durable retention and redistribution not established | BTC-only conditional |
| State Street | `SPY` identity established | No required automated daily history interface documented | No daily adjusted-market-price contract found | Not established for such an interface | Not established for such an interface | Reject |

No row in the matrix supplies both target series, explicit automated access,
the required semantics, and a usable retention boundary. The provider search
therefore closes with **no fully viable keyless alternative identified from
the reviewed primary sources**.
