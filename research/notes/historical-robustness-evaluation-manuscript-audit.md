# Historical evaluation and robustness manuscript audit

Review status: **passed** independent domain, statistical-language, reproducibility, and rendered-visual review on 2026-09-05.

## Audit target

This note governs Chapter 8 and the historical part of Appendix E. It checks
that the thesis projects the already accepted primary historical and separately
registered robustness evidence without changing a protocol, input, accepted
run bundle, theorem, or empirical conclusion. The two immutable identities are:

- `smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221`;
  and
- `smartdca-historical-robustness-v1-0991d999e1a8070a2a6eb8046b08a91d0e42341995610a602372c52dfab14184`.

The publication-ready interpretation remains
[Confirmatory historical evaluation](../../reports/experiments/confirmatory-historical-evaluation.md).
The accepted primary and robustness audits remain authority for the underlying
runs; this note audits their manuscript projection.

## Evidence reconciliation

The public generator
[`reproducibility/historical_evaluation_assets.py`](../../reproducibility/historical_evaluation_assets.py)
checks both outer-manifest SHA-256 values and run identities, then verifies each
public artifact it reads against the corresponding manifest inventory. It
joins every primary H1/H2 aggregate cell to its registered uncertainty cell and
rejects drift in the registered statistic, sample count, 36-test family, method,
10,000-replicate count, or base seed. It also requires passed validation, zero
exclusions, empty deviation and protocol-violation lists, and the unchanged
private-data redistribution boundary.

| Evidence slice | Attempted | Included | Excluded | Ledgers / comparisons | Aggregate cells | Inference role |
|---|---:|---:|---:|---:|---:|---|
| Sealed primary monthly | 1,365 | 1,365 | 0 | 49,140 / 49,140 | 216 | 36 registered H1/H2 cells |
| Registered monthly coverage | 1,365 | 1,365 | 0 | 73,710 / 73,710 | 324 | descriptive robustness |
| Registered quarterly horizons | 428 | 428 | 0 | 34,668 / 34,668 | 486 | descriptive robustness |

The robustness total is therefore 1,793 included episodes, 108,378 ledgers and
comparison rows, and 810 cells: 792 robustness cells and 18 compatibility
cells. Robustness records `not-run-robustness` uncertainty and no change to the
sealed confirmatory family.

The committed, byte-regenerated presentation assets are:

| Asset | SHA-256 | Contents |
|---|---|---|
| `manuscript/generated/historical-primary.tex` | `1219f02093ae2039d72e4e4dc43a7ffb18952f778873bef1be66ded50ad88e46` | primary H1/H2 summary and all-cell H1 figure |
| `manuscript/generated/historical-mechanisms.tex` | `6fd7e934239e07649a8a9c2871fcae2c96464840b4a66211015239da6af527c3` | comparison tiers, mechanisms, and terminal attribution |
| `manuscript/generated/historical-robustness.tex` | `123457a25da8b989bcc443d41494050785e1fe679888e15431fe8b64249e88aa` | registered robustness and cost summaries |
| `manuscript/generated/historical-supplementary.tex` | `0b4a4e82f0bd755b09e368305d00e9d9c2011338d007d708c3900be8ee6a6f18` | all primary cells, robustness ranges, and completeness inventory |

The generator independently groups machine rows for presentation rather than
copying numerical strings from the narrative report. The dedicated check
regenerates the four assets in a fresh directory and compares their bytes with
the committed manuscript inputs. No path under `experiments/` or either
accepted run directory is an output target.

Numerical reconciliation against the machine artifacts gives:

- all 18 primary non-unit frictionless H1 medians are negative, spanning
  `-4.5931546...%` to `-0.3352664...%`; all 18 cellwise intervals lie below
  zero and nine H1 cells reject after Holm adjustment;
- H2 has 17 negative and one positive median, spanning `-0.5453427...%` to
  `+0.0517990...%`; seven cellwise intervals lie below zero and no H2 cell
  rejects after adjustment;
- all 18 S1 architecture-only medians are negative, while all 54 primary and
  all 108 robustness lambda-one aggregate rows are exact ties;
- in every H1 cell the mean cash contribution is positive and the mean
  evaluation-price-valued unit contribution is negative; the two contributions
  sum to the mean signed dollar terminal-wealth difference;
- monthly robustness contains 30 negative complete-system corrected--DCA and
  30 negative signal-only corrected--neutral medians; quarterly robustness
  contains 48 negative complete-system corrected--DCA medians and 40 negative
  plus eight positive signal-only corrected--neutral medians, with all eight
  positives confined to BTC-USD at six months; and
- the 36 primary and 156 extension cost-adjusted complete-system
  corrected--DCA medians are negative, but every fee row remains outside the
  current frictionless safety theorem.

## Claim and scope audit

The claim-to-evidence register maps the chapter and generated assets as
follows. Each record links to this manuscript-slice audit and to its machine,
report, protocol, or theorem authority.

| Claim ID | Manuscript role | Governing boundary |
|---|---|---|
| `claim-empirical-historical-populations` | immutable identities and execution counts | completeness, not independent samples or financial validity |
| `claim-empirical-historical-complete-system` | registered H1 effects and decisions | realized association, not universal or causal inferiority |
| `claim-empirical-historical-signal` | separately interpreted H2 effects and decisions | no confirmed incremental value and no equivalence result |
| `claim-empirical-robustness` | monthly coverage and quarterly-horizon extension | post-confirmatory descriptive evidence only |
| `claim-empirical-historical-architecture-mechanisms` | S1 and policy-state mechanisms | descriptive and ledger-conditioned, not causal decomposition |
| `claim-empirical-historical-safety-regressions` | lambda-one collapse and finite floor checks | implementation regression, not another proof |
| `claim-empirical-cost-scope` | primary and extension fee routes | net empirical calculations outside the frictionless theorem |
| `claim-table-historical-primary` | dataset--horizon H1/H2 primary summary | H1 and H2 retain separate decisions |
| `claim-figure-historical-primary-effects` | all 18 H1 primary point estimates | common zero scale; point estimates, not intervals |
| `claim-table-historical-comparison-tiers` | H1, H2, and S1 roles side by side | significance never transfers across tiers |
| `claim-table-historical-policy-mechanisms` | cash drag, asset exposure, and activation | policy-state summaries, not performance criteria |
| `claim-table-historical-risk-attribution` | downside and cash/unit signs | exact inventory accounting, not a causal explanation |
| `claim-table-registered-robustness` | registered monthly and quarterly signs and ranges | no interval, test, or primary-family revision |
| `claim-table-historical-cost-robustness` | primary and extension fee ranges | descriptive net outcomes outside theorem scope |
| `claim-table-historical-h1-cells` | all 18 H1 medians, intervals, and decisions | one sealed 36-test H1/H2 family |
| `claim-table-historical-h2-cells` | all 18 H2 medians, intervals, and decisions | non-rejection is not equivalence |
| `claim-table-historical-architecture-cells` | all 18 S1 cell summaries | secondary evidence without significance decisions |
| `claim-table-historical-monthly-robustness-ranges` | five additional coverages | within-schedule relative gaps only |
| `claim-table-historical-quarterly-robustness-ranges` | eight non-unit coverages and schedule-specific counts | raw wealth is not compared across cadences |
| `claim-table-historical-evidence-inventory` | attempts, inclusion, ledgers, cells, and uncertainty | public derived evidence; restricted observations remain private |

The chapter remains subject to `nonclaim-universal-superiority`,
`nonclaim-confirmed-signal-value`, `nonclaim-frictional-safety`, and
`nonclaim-empirical-causality`. H1, H2, and S1 always name different right-hand
comparators. Primary and robustness results retain distinct run identities,
grids, and inferential roles.

## Statistical-language audit

Status: **passed** by independent statistical-language review.

The independent review reconciled the exact H1/H2 ranges, signs, interval
counts, and Holm scope; confirmed that H1 complete-system, H2 signal-only, and
S1 architecture-only comparators retain their named denominators; and found no
statistical-language blocker. It specifically verified that ordered overlapping
starts are not called independent histories, cellwise intervals are not
substituted for Holm decisions, H2 non-rejection is not called equivalence,
robustness has no inferential procedure, quarterly cells with four starts are
exposed, and raw terminal wealth is never compared across cadences with
different deposit counts. Median relative gaps, mean dollar contributions,
downside quantiles, and worst observed shortfalls retain distinct units and
roles.

## Reproducibility review

Status: **passed** by independent reproducibility review.

The independent review ran the historical robustness manuscript check (11/11
underlying assertions), regenerated the four assets twice in isolated
directories, and matched both runs byte-for-byte to the committed assets and
the hashes above. Confirmatory historical checks (11/11), the historical data
seam (30/30), manuscript controls, and the 108-page temporary LaTeX build also
passed; the provider-private check was the only intentionally skipped check.
The review confirmed manifest and artifact fingerprints, accepted identities,
sample and cell counts, primary uncertainty joins, signed results, comparison
denominators, lambda-one ties, fee scope, claim authority existence, and
absence of any accepted-run mutation.

## Visual review

Status: **passed** by independent rendered-visual review.

The independent review inspected the canonical-layout Chapter 8 pages
(printed pages 52--58), including Tables 8.1--8.6 and Figure 8.1, and the
historical Appendix E pages (printed pages 88--92, Tables E.6--E.11). Tables,
captions, signs, zero axis, symbols, font size, wrapping, float placement,
cross-references, and monochrome accessibility were legible with no clipping or
overlap. The final LaTeX/BibTeX pass had no warnings, errors, overfull or
underfull boxes, undefined references, or undefined citations. A non-blocking
typography note is that one continuation line precedes section 8.4 on printed
page 55.

## Independent domain review

Status: **passed** by independent domain review.

The independent reviewer reconciled the source populations and private receipt
boundary, exact H1/H2 results, policy comparators and denominators, architecture
and terminal cash/unit mechanisms, robustness identity and cadence schedules,
deposit counts, cost scope, uncertainty and multiplicity language, and theorem-
versus-regression boundaries. No scientific overclaim or blocking domain issue
was found. The review also confirmed that primary and robustness evidence remain
separate and that generated assets regenerate byte-identically.

The implementation, four independent reviews, canonical build, and final code
review are the completion gates for this manuscript slice. No publication
blocker remains for Ticket 11.
