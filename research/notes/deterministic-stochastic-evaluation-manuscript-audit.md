# Deterministic and stochastic evaluation manuscript audit

Review status: **passed** independent domain, statistical-language, and
rendered-visual review on 2026-09-04.

## Audit target

This note governs Chapter 7 and the synthetic part of Appendix E. It checks
that the thesis projects the already accepted deterministic and seeded-
stochastic evidence without changing a protocol, input, run bundle, theorem,
or empirical conclusion. The two immutable source identities are:

- `smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db`;
  and
- `smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25`.

Their publication-ready reports are
[Deterministic synthetic and adversarial path evaluation](../../reports/experiments/deterministic-adversarial-paths.md)
and [Seeded stochastic path-family evaluation](../../reports/experiments/seeded-stochastic-families.md).
The independent empirical-package review remains the acceptance authority for
the underlying runs; this note audits only their manuscript projection.

## Evidence reconciliation

The public generator
[`reproducibility/synthetic_evaluation_assets.py`](../../reproducibility/synthetic_evaluation_assets.py)
first checks the two outer-manifest SHA-256 values and study IDs. It then
checks every artifact it reads against the corresponding manifest inventory:
the deterministic mechanism CSV and boundary receipt, both runner-validation
receipts, and the stochastic aggregate JSON. It rejects population drift from
the accepted counts:

| Layer | Attempts | Generated | Excluded | Runner ledgers | Comparison rows |
|---|---:|---:|---:|---:|---:|
| Deterministic | 21 | 18 | 3 | 648 | 648 |
| Seeded stochastic | 90 | 90 | 0 | 3,240 | 3,240 |

For the stochastic layer it additionally requires the saved seeds `104729`,
`130363`, and `155921`, all `1,080` aggregate cells, and the accepted 12-,
36-, and 60-month horizon set. The deterministic boundary receipt must have
status `passed` and scope `finite-regression-not-proof`.

The generator independently groups machine rows for presentation rather than
copying numerical strings from either narrative report. Its selected slices
are fixed in code:

- all fourteen required primary deterministic families at frictionless
  coverage `0.75`, with one path per row;
- all eighteen deterministic paths for the three non-unit coverage ranges and
  the three cost scopes;
- the five primary 60-month stochastic family cells at frictionless coverage
  `0.75`, with three saved seeds per cell;
- the five separately labelled exploratory stochastic sensitivity cells at
  the same horizon and coverage; and
- five-family stochastic mechanism ranges at coverage `0.9`, `0.75`, and
  `0.5`.

The resulting committed presentation assets are:

| Asset | SHA-256 after reviewer correction | Contents |
|---|---|---|
| `manuscript/generated/deterministic-evaluation.tex` | `8c165ac78bc4927667a74e4ba290538a7369b37c8967dfb4c8609278fb92a2cf` | primary deterministic table and layer-sign figure |
| `manuscript/generated/stochastic-evaluation.tex` | `a05e3b2ff26de5c3242ae6cd828a016e9dedfd33471932ef0ecaddb3925b94d2` | primary stochastic table |
| `manuscript/generated/stochastic-mechanisms.tex` | `39510a88fc732d286d52007e8fbaab57435655008d185f145ada5615d762cb4e` | terminal-attribution figure and mechanism table |
| `manuscript/generated/synthetic-supplementary.tex` | `b093515eb8fd2744f76db453eedd3ff2fd1b170181f28cf794a37f68fc902e58` | deterministic coverage/cost tables, exploratory stochastic table, coverage diagnostics, and validation inventory |

The public checkpoint regenerates these four files in a temporary directory
and compares them byte for byte with the manuscript assets. The original
deterministic and stochastic study checks separately replay the complete
accepted run outputs. No file under `experiments/` or an accepted run directory
is an output target of manuscript generation.

Numerical spot reconciliation against the machine artifacts gives:

- deterministic monotone-rise complete, signal, and architecture gaps of
  `-4.712%`, `-0.460%`, and `-4.271%` after display rounding;
- deterministic monotone-decline complete and architecture gaps of `+5.260%`
  and `+6.202%`, with a `-0.887%` signal-only gap;
- hostile-adaptive-timing cash and unit contributions of `-200.736...` and
  `+136.684...` dollars for corrected versus neutral;
- stochastic primary trend median/downside/worst of `-0.269%`, `-0.273%`, and
  `0.273%`, and primary mean-reversion median/downside/worst of `+0.111%`,
  `+0.097%`, and `0.000%`;
- trend mean cash and unit contributions of `+1015.595...` and `-1143.872...`
  dollars, and mean-reversion contributions of `+894.404...` and
  `-782.925...` dollars; and
- primary 60-month activation ranges of `30.0--31.7%`, `10.6--11.1%`, and
  `3.9--3.9%` at coverage `0.9`, `0.75`, and `0.5`.

Those values agree with the retained reports after the declared display
rounding. Cash plus evaluation-price-valued unit contribution reconstructs the
mean signed terminal-wealth difference in dollars; it must not be equated with
the separately reported median relative gap.

## Claim and scope audit

The claim-to-evidence register maps each chapter claim and generated item as
follows. All records link back to this note as the manuscript-slice audit and
to their machine or theorem authority.

| Claim ID | Manuscript role | Governing boundary |
|---|---|---|
| `claim-empirical-synthetic-populations` | run identities and separate execution counts | completeness receipt, not pooled inference or independent-data replication |
| `claim-empirical-deterministic-mixed` | fixed-path signs and deterministic mechanisms | finite catalog, not probabilities or market frequencies |
| `claim-empirical-stochastic-sensitive` | primary and exploratory three-seed variation | controlled sensitivity, not calibration, expected return, or stochastic optimality |
| `claim-empirical-synthetic-mechanisms` | cash/unit attribution, cash drag, exposure, and floor activation | ledger-conditioned descriptive summaries, not a monotone law |
| `claim-empirical-observed-safety-floor` | finite frictionless regression receipt | implementation agreement, not a second proof |
| `claim-empirical-synthetic-cost-scope` | proportional- and fixed-fee outputs | net empirical performance outside the current frictionless theorem |
| `claim-table-deterministic-primary` | fourteen required deterministic families | one fixed path per row; varying dates explicit |
| `claim-figure-deterministic-layers` | four mechanism-representative path views | different comparator denominators; bars are not additive |
| `claim-table-stochastic-primary` | primary 60-month effect size and downside | three saved seeds per family; descriptive quantiles |
| `claim-figure-stochastic-attribution` | mean cash and unit contributions in dollars | corrected versus DCA only; mean signed dollar differences |
| `claim-table-stochastic-mechanisms` | activation, cash drag, exposure, attribution | five primary cells at the displayed slice |
| `claim-table-deterministic-coverage-ranges` | exact ranges and signs over eighteen fixed paths | catalog counts are not frequencies |
| `claim-table-deterministic-cost-ranges` | frictionless and two fee routes | fee rows do not inherit the theorem label |
| `claim-table-stochastic-sensitivity` | five exploratory configurations | no replacement or pooling of primary rows |
| `claim-table-stochastic-coverage-diagnostics` | ranges across five family summaries | family summaries are not a new inferential sample |
| `claim-table-synthetic-validation-inventory` | attempts, exclusions, ledgers, and comparisons | layer-specific completeness accounting only |

The chapter also remains subject to `nonclaim-universal-superiority`,
`nonclaim-frictional-safety`, and `nonclaim-empirical-causality`. The exact
two- and three-purchase fixtures are described as strict finite witnesses and
linked to their analytical classifications. Their runner receipt does not
replace the proof or generalize a witness to the full catalog.

## Statistical-language audit

Status: **passed** by independent review.

- Deterministic loss/tie/win counts are called catalog counts, never win rates.
- A stochastic cell is always identified by tier, family configuration,
  horizon, coverage, corrected mean, cost, and comparison before its three
  saved paths are summarized.
- The displayed stochastic 5% value is called a linearly interpolated
  descriptive quantile, not a tail estimate or confidence bound.
- Primary and exploratory stochastic rows remain separate. Neither is pooled
  with deterministic paths or historical episodes.
- No p-value, significance claim, expected-return claim, causal comparison,
  process calibration, or optimal safety-factor claim is introduced.
- Mean signed cash/unit contributions in dollars are distinguished from median
  relative gaps.
- Frictionless validation and net fee calculations retain separate theorem
  labels.

## Visual review

Status: **passed** with no source-layout blocker. The independent reviewer
inspected Chapter 7 and Appendix E tables, both monochrome bar figures,
captions, wrapping, font size, zero axes, value labels, float placement,
cross-references, and accessibility without color. The reviewed preliminary
pages were legible, unclipped, and monochrome-accessible. The deterministic
generated input was then moved after the complete constant-path paragraph so
that its figure cannot interrupt that sentence, and an explicit float barrier
keeps both deterministic assets ahead of the following interpretation.

The final canonical build passed as a 95-page A4 PDF. Its log contains no
LaTeX, package, overfull/underfull box, unresolved-reference, or multiply
defined-label warning. Final inspection covered physical PDF pages 55--60 and
87--89 (printed pages 45--50 and 77--79): the tables, bars, captions, and prose
are legible and unclipped; no float interrupts a sentence; signed-dollar
language renders without a broken compound; and Appendix E.3 correctly names
four generated presentation assets.

## Independent domain review

Independent reviewer Pauli completed the domain, statistical-language, and
visual audit on 2026-09-04. The review compared the chapter, generated assets,
claim records, deterministic and stochastic reports, stochastic audit,
terminal-inventory theorem, unit-guardrail theorem, and rendered pages. It
checked policy comparators, populations, units, horizons, coverage, costs,
downside wording, attribution arithmetic, strict-witness scope, non-pooling,
and the frictionless/net boundary.

The reviewer found four blocking presentation defects, all resolved before the
verdict:

- the signed mean dollar terminal-wealth difference was incorrectly called an
  absolute gap; the prose, caption generator, generated asset, and this audit
  now use signed-difference language;
- the deterministic figure caption now expands corrected guarded, neutral
  guarded, and DCA and defines each right-hand comparator denominator;
- the stochastic coverage-diagnostics caption now states the frictionless
  frozen-identity-mean scope and defines activation, cash-drag, asset-exposure,
  and complete-system denominators; and
- three appendix-table references now identify tables rather than appearing to
  name appendix sections, while the deterministic figure source was moved so
  it cannot interrupt the constant-path sentence.

Final verdict: **domain pass, statistical-language pass, and visual pass**.
Comparators, populations, units, horizons, coverage, costs, strict-witness
scope, cash/unit attribution, theorem-versus-simulation scope,
frictionless-versus-net scope, descriptive quantiles, signed-dollar means, and
non-pooling all agree with the accepted evidence.

No publication blocker remains for ticket 10.
