# Alpha Vantage historical-data provider review

This note records the provider and licensing evidence needed by ticket 04's
historical-data seam. The review used only Alpha Vantage's official website and
official source repository, accessed 2026-08-30. It did not call a market-data
endpoint, retrieve a historical response, inspect a price observation, or
compute a confirmatory outcome.

## Decision

The locked requests remain operationally plausible, subject to an appropriate
Alpha Vantage license and subscription. `TIME_SERIES_DAILY_ADJUSTED` is
currently a premium function; `DIGITAL_CURRENCY_DAILY` remains documented with
an authenticated CSV route. Exact response headers, coverage, and provider
metadata are runtime evidence and must be captured before parsing.

As a conservative repository policy, no raw Alpha Vantage response or
normalized observation may be committed under the reviewed terms. If the
researcher's license permits retention, exact accepted bytes must remain
immutable and access-controlled outside Git. Version control may contain only
code, synthetic fixtures, field-level schema descriptions, sanitized receipts,
coverage metadata, and cryptographic fingerprints. Publishing provider bytes
or normalized observations requires explicit written permission or a source
with an affirmative redistribution license.

## Equity series: `TIME_SERIES_DAILY_ADJUSTED` / `SPY`

Alpha Vantage describes the function's logical row schema as a daily date with
raw open, high, low, close, and volume values, an adjusted close, and historical
split and dividend events. `outputsize=full` means the full-length series of
20+ years, JSON is the default representation, CSV is supported, and `apikey`
is required. The function is currently marked Premium
([Daily Adjusted documentation](https://www.alphavantage.co/documentation/#dailyadj)).

The provider's support page says its adjustment method accounts for both stock
splits and cash dividends
([support FAQ](https://www.alphavantage.co/support/)). An official tutorial
distinguishes JSON field `5. adjusted close` from raw `4. close` and says the
adjusted field removes discontinuities from split and dividend-payout events
([adjusted-price tutorial](https://www.alphavantage.co/stock-price-tracker-website-python-django/#backend-logic)).
This supports the protocol's bounded statement that provider adjusted close
incorporates historical split and dividend events. It does not establish a
specific reinvestment formula, so the study must not strengthen that statement
into an independently verified total-return methodology.

The static official material does not publish the exact CSV header. In the
repository schema, `adjusted_close` is therefore the normalized name for the
received adjusted-close field, not a claim that this spelling is a stable
provider header. Acceptance must record the exact received header and reject a
response without one unambiguous adjusted-close field and the documented event
fields.

The Daily Adjusted page also does not state that a U.S. equity's daily date is
labelled in `America/New_York`, and it does not identify `SPY` as the SPDR S&P
500 ETF Trust. `America/New_York` is the protocol's normalization convention,
not a provider fact established by that page. The receipt must retain whatever
timezone or date semantics the authorized response actually supplies; the
implementation must not invent missing provider metadata. Instrument identity
needs separate issuer evidence or explicit provider confirmation before it is
stated as an externally verified claim.

## Digital-currency series: `DIGITAL_CURRENCY_DAILY` / `BTC`-`USD`

Alpha Vantage describes this function as daily history for a requested
cryptocurrency `symbol` traded on a requested `market`, refreshed daily at
midnight UTC, with prices and volumes quoted in both the market-specific
currency and USD. Its parameter list requires `function`, `symbol`, `market`,
and `apikey`; it lists no `outputsize` parameter or historical-coverage promise
([Digital Currency Daily documentation](https://www.alphavantage.co/documentation/#currency-daily)).
The page omits `datatype` from the parameter list but provides an official CSV
example using `datatype=csv`. Alpha Vantage's official implementation likewise
accepts `datatype`, defaults its wrapper to CSV, and forwards it to
`DIGITAL_CURRENCY_DAILY`
([official implementation at commit `93b9798`](https://github.com/alphavantage/alpha_vantage_mcp/blob/93b9798130882618153e0f8e4748fce69f7ace47/api/src/av_api/tools/cryptocurrencies.py#L64-L88)).

The official static sources do not publish the exact digital-currency CSV
header. `close_usd` is consequently the repository's normalized field name,
not a provider-header claim. The parser must record the received header, map
only a field unambiguously denoting the USD close, and reject an ambiguous
mapping. For `market=USD`, this is still the USD-quoted close; the docs do not
license choosing between differently labelled or duplicate fields by position.

The midnight-UTC refresh claim is directly supported. The protocol may use UTC
as its normalization convention, but the docs do not separately define every
daily date label as a UTC timestamp. They also do not describe the series as
venue-specific, aggregated, or explicitly "spot." Those stronger
interpretations must not be attributed to Alpha Vantage.

## Authentication and auditable retrieval

Both endpoint pages require `apikey`, and their examples place it in the query
parameters
([Daily Adjusted documentation](https://www.alphavantage.co/documentation/#dailyadj),
[Digital Currency Daily documentation](https://www.alphavantage.co/documentation/#currency-daily)).
The credential-bearing URL must therefore never enter logs or receipts. Build
the request in memory and record only the endpoint plus canonical parameters
with the credential omitted.

HTTP success is not payload success. Alpha Vantage's official client records
that failures may use HTTP 200 with JSON keys `Error Message`, `Information`,
or `Note`, including when the requested representation is CSV
([error-envelope handling at commit `93b9798`](https://github.com/alphavantage/alpha_vantage_mcp/blob/93b9798130882618153e0f8e4748fce69f7ace47/api/src/av_api/client.py#L85-L154)).
Alpha Vantage also asks wrapper authors to preserve original response content
in both success and error cases
([support FAQ](https://www.alphavantage.co/support/)). Accordingly, an attempt
must fingerprint untouched bytes before parsing, validate both HTTP metadata
and the payload envelope, and retain even a rejected attempt as a sanitized
machine-readable receipt. Exact response bytes may be retained only in the
access-controlled store described above.

An accepted receipt needs at least the endpoint; credential-free canonical
parameters including `datatype`, `outputsize` where applicable, and requested
entitlement; UTC retrieval time; HTTP status and relevant response headers;
byte length and SHA-256; exact received schema/header; parser version; row
count; minimum and maximum dates; and an accepted or typed-rejection result.
The SPY request additionally needs premium authorization because the endpoint
is currently premium. The BTC request must prove actual coverage because the
provider publishes no `outputsize` or coverage guarantee for that function.

## License and redistribution review

Alpha Vantage's Terms grant personal, non-commercial use absent a different
written agreement. They define some entity use and provision of accessed
information to others as commercial use, and the EULA license is
non-exclusive, non-sublicensable, non-transferable, non-assignable, and
revocable. Alpha Vantage also retains its rights in the platform, including its
database and files
([Terms of Service, sections 2, 3, and 5](https://www.alphavantage.co/terms_of_service/)).
The reviewed terms do not affirmatively authorize redistribution of raw API
responses, normalized price rows, or derived datasets. The support page's
permission to open-source a wrapper concerns wrapper code and does not say a
response dataset may be bundled with it
([support FAQ](https://www.alphavantage.co/support/)).

The receipt-only repository decision above is therefore conservative rather
than a claim that the terms expressly decide every archival or derived-data
case. A broader publication needs written permission. Because the Terms URL is
mutable and the PDF exposes no visible revision date, the exact PDF reviewed
on 2026-08-30 was 156,583 bytes with SHA-256
`88ed3d22fe0f3624e76e53a210db3498b4a90712ab0d934356cc84b19ed1468a`.

## Frozen-protocol audit

| Frozen statement | Current official-source finding | Ticket-04 handling |
| --- | --- | --- |
| SPY full-history adjusted CSV | Supported, but the entire function is currently Premium. | Require authorized premium access; reject a premium/error envelope. |
| SPY adjusted close includes splits and dividends | Supported at that level; no exact adjustment formula is published. | Use the provider field and preserve bounded wording. |
| SPY timezone is `America/New_York` | Not established by the static Daily Adjusted docs. | Treat it as a normalization convention and preserve received date/timezone semantics. |
| `SPY` denotes the named ETF | Not established by the reviewed Alpha Vantage static pages. | Do not promote the identity to a verified claim without separate evidence. |
| BTC/USD CSV with normalized `close_usd` | CSV is supported; that exact provider header is not documented. | Capture the header and make the USD-close mapping explicit or reject it. |
| BTC refreshes at midnight UTC | Directly supported. | Record the refresh boundary in UTC; distinguish normalized dates from provider-stated semantics. |
| BTC is an unadjusted spot series | No corporate-action adjustment is described, but "spot" and venue/aggregation semantics are not defined. | Keep the frozen label; do not attribute the stronger interpretation to the provider. |
| One BTC response supplies the required history | No pagination or `outputsize` is documented, but no coverage length is promised either. | Make one locked request and accept only if its recorded coverage satisfies the protocol. |
| Raw bytes await a ticket-04 license review | No clear redistribution grant was located. | Do not commit raw or normalized observations without written permission. |

These findings document operational constraints and interpretation gaps; they
do not alter the immutable version-1 protocol. Any outcome-relevant protocol
change still requires a new protocol identity under the preregistered rule.
