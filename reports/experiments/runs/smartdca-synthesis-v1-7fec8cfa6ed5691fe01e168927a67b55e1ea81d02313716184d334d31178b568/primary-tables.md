# Generated primary synthesis tables

Every value below is generated from the exact reviewed aggregates bound by the synthesis manifest.
Cells are never pooled across evidence layers, and a displayed range is not an independent-sample interval.

## Reviewed evidence inventory

| Evidence layer | Source | Reviewed aggregate cells | Episode-evidence route |
|---|---|---:|---|
| Deterministic | `deterministic-primary-v1` | 648 | public episode rows independently reproduced and reconciled |
| Stochastic | `stochastic-primary-v1` | 1080 | public episode rows independently regrouped and reconciled |
| Historical | `historical-confirmatory-v1` | 216 | private episode rows retained by receipt and independently reconciled to public aggregates |
| Historical | `historical-registered-robustness-v1` | 810 | private episode rows retained by receipt and independently reconciled to public aggregates |

## Cross-layer findings

| Evidence slice | Analysis tier | Comparison | Cells | N/cell min–max | Negative / zero / positive medians | Median range | Holm significant | Boundary |
|---|---|---|---:|---:|---:|---:|---:|---|
| Deterministic primary catalog at lambda=0.75 | primary | Complete-system performance | 14 | 1–1 | 9 / 1 / 4 | -4.978% to +26.105% | not registered | fixed catalog; signs are not frequencies |
| Deterministic primary catalog at lambda=0.75 | primary | Corrected-mean signal contribution | 14 | 1–1 | 5 / 1 / 8 | -2.901% to +1.520% | not registered | fixed catalog; signs are not frequencies |
| Deterministic primary catalog at lambda=0.75 | primary | Safety-architecture behavior | 14 | 1–1 | 10 / 1 / 3 | -4.526% to +29.873% | not registered | fixed catalog; signs are not frequencies |
| Stochastic primary families at 60 months and lambda=0.75 | primary | Complete-system performance | 5 | 3–3 | 3 / 0 / 2 | -0.773% to +0.115% | not registered | three saved seeds per family; no population inference |
| Stochastic primary families at 60 months and lambda=0.75 | primary | Corrected-mean signal contribution | 5 | 3–3 | 1 / 0 / 4 | -0.029% to +0.071% | not registered | three saved seeds per family; no population inference |
| Stochastic primary families at 60 months and lambda=0.75 | primary | Safety-architecture behavior | 5 | 3–3 | 3 / 0 / 2 | -0.745% to +0.095% | not registered | three saved seeds per family; no population inference |
| Historical primary non-unit frictionless cells | confirmatory | Complete-system performance | 18 | 72–383 | 18 / 0 / 0 | -4.593% to -0.335% | 9 / 18 | overlapping windows; registered block-bootstrap inference only for H1/H2 |
| Historical primary non-unit frictionless cells | confirmatory | Corrected-mean signal contribution | 18 | 72–383 | 17 / 0 / 1 | -0.545% to +0.052% | 0 / 18 | overlapping windows; registered block-bootstrap inference only for H1/H2 |
| Historical primary non-unit frictionless cells | secondary | Safety-architecture behavior | 18 | 72–383 | 18 / 0 / 0 | -4.365% to -0.340% | not registered | overlapping windows; registered block-bootstrap inference only for H1/H2 |
| Historical monthly robustness coverage cells | robustness | Complete-system performance | 30 | 72–383 | 30 / 0 / 0 | -4.813% to -0.034% | not registered | descriptive only; no uncertainty or multiplicity test |
| Historical monthly robustness coverage cells | robustness | Corrected-mean signal contribution | 30 | 72–383 | 30 / 0 / 0 | -0.5836% to -0.0002% | not registered | descriptive only; no uncertainty or multiplicity test |
| Historical monthly robustness coverage cells | robustness | Safety-architecture behavior | 30 | 72–383 | 30 / 0 / 0 | -4.722% to -0.034% | not registered | descriptive only; no uncertainty or multiplicity test |
| Historical quarterly robustness horizon cells | robustness | Complete-system performance | 48 | 4–130 | 48 / 0 / 0 | -23.484% to -0.026% | not registered | descriptive within schedule; no uncertainty or multiplicity test |
| Historical quarterly robustness horizon cells | robustness | Corrected-mean signal contribution | 48 | 4–130 | 40 / 0 / 8 | -9.216% to +0.057% | not registered | descriptive within schedule; no uncertainty or multiplicity test |
| Historical quarterly robustness horizon cells | robustness | Safety-architecture behavior | 48 | 4–130 | 48 / 0 / 0 | -15.718% to -0.026% | not registered | descriptive within schedule; no uncertainty or multiplicity test |

## Gross frictionless safety-factor curve

This table uses the complete-system comparison. Each row summarizes source aggregate cells within one declared slice and coverage; it does not pool episodes.

| Evidence slice | Analysis tier | λ | Cells | Median of cell medians | Minimum 5% downside | Worst observed shortfall | Cash drag | Asset exposure | Floor activation | Purchases | Mean cash / deposits | Mean unit value / deposits |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Deterministic primary catalog | primary | 0.5 | 14 | -0.859% | -8.565% | 8.565% | 15.708% | 84.775% | 42.857% | 5.5 | +16.876% | -18.146% |
| Deterministic primary catalog | primary | 0.75 | 14 | -0.852% | -4.978% | 4.978% | 13.542% | 88.108% | 92.857% | 5.5 | +13.301% | -14.449% |
| Deterministic primary catalog | primary | 0.9 | 14 | -0.343% | -1.991% | 1.991% | 5.818% | 95.113% | 100.000% | 5.5 | +5.575% | -6.026% |
| Deterministic primary catalog | primary | 1 | 14 | +0.000% | +0.000% | 0.000% | 0.000% | 100.000% | 100.000% | 5.5 | +0.000% | +0.000% |
| Stochastic primary families | primary | 0.5 | 15 | -0.497% | -1.571% | 1.647% | 2.991% | 97.243% | 6.481% | 36.0 | +4.458% | -4.869% |
| Stochastic primary families | primary | 0.75 | 15 | -0.407% | -1.447% | 1.537% | 2.991% | 97.244% | 17.593% | 36.0 | +4.448% | -4.809% |
| Stochastic primary families | primary | 0.9 | 15 | -0.253% | -0.788% | 0.805% | 2.991% | 97.245% | 50.000% | 36.0 | +3.301% | -3.504% |
| Stochastic primary families | primary | 1 | 15 | +0.000% | +0.000% | 0.000% | 0.000% | 100.000% | 100.000% | 36.0 | +0.000% | +0.000% |
| Historical primary monthly design | confirmatory | 0.5 | 6 | -2.323% | -15.292% | 18.961% | 6.106% | 97.516% | 6.756% | 36.0 | +6.300% | -22.505% |
| Historical primary monthly design | confirmatory | 0.75 | 6 | -2.188% | -12.058% | 15.762% | 6.106% | 97.523% | 17.581% | 36.0 | +6.279% | -20.744% |
| Historical primary monthly design | confirmatory | 0.9 | 6 | -1.236% | -7.673% | 7.925% | 5.268% | 97.542% | 50.219% | 36.0 | +4.985% | -14.756% |
| Historical primary monthly design | secondary | 1 | 6 | +0.000% | +0.000% | 0.000% | 0.000% | 100.000% | 100.000% | 36.0 | +0.000% | +0.000% |
| Historical monthly robustness coverage | robustness | 0.25 | 6 | -2.381% | -16.108% | 20.223% | 6.106% | 97.513% | 2.836% | 36.0 | +6.302% | -22.994% |
| Historical monthly robustness coverage | robustness | 0.6 | 6 | -2.310% | -13.895% | 18.162% | 6.106% | 97.517% | 9.607% | 36.0 | +6.298% | -22.086% |
| Historical monthly robustness coverage | robustness | 0.8 | 6 | -2.009% | -10.951% | 13.812% | 6.106% | 97.526% | 22.926% | 36.0 | +6.231% | -19.818% |
| Historical monthly robustness coverage | robustness | 0.95 | 6 | -0.731% | -4.160% | 4.616% | 3.228% | 97.939% | 96.087% | 36.0 | +3.613% | -9.636% |
| Historical monthly robustness coverage | robustness | 0.99 | 6 | -0.153% | -0.863% | 0.923% | 0.670% | 99.528% | 100.000% | 36.0 | +0.830% | -2.148% |
| Historical monthly robustness coverage | secondary | 1 | 6 | +0.000% | +0.000% | 0.000% | 0.000% | 100.000% | 100.000% | 36.0 | +0.000% | +0.000% |
| Historical quarterly robustness horizons | robustness | 0.25 | 6 | -4.209% | -27.382% | 32.158% | 19.347% | 88.741% | 13.194% | 8.0 | +21.225% | -244.852% |
| Historical quarterly robustness horizons | robustness | 0.5 | 6 | -3.028% | -23.746% | 25.875% | 19.280% | 88.894% | 29.749% | 8.0 | +18.313% | -229.532% |
| Historical quarterly robustness horizons | robustness | 0.6 | 6 | -2.502% | -21.482% | 23.506% | 19.191% | 89.038% | 40.362% | 8.0 | +16.545% | -216.884% |
| Historical quarterly robustness horizons | robustness | 0.75 | 6 | -1.907% | -17.580% | 18.791% | 13.661% | 89.848% | 73.152% | 8.0 | +13.480% | -181.382% |
| Historical quarterly robustness horizons | robustness | 0.8 | 6 | -1.715% | -15.402% | 15.773% | 11.346% | 91.272% | 91.415% | 8.0 | +11.982% | -159.739% |
| Historical quarterly robustness horizons | robustness | 0.9 | 6 | -1.194% | -9.124% | 9.143% | 5.674% | 95.471% | 99.653% | 8.0 | +7.958% | -94.474% |
| Historical quarterly robustness horizons | robustness | 0.95 | 6 | -0.740% | -4.744% | 4.753% | 3.235% | 97.682% | 100.000% | 8.0 | +5.292% | -50.809% |
| Historical quarterly robustness horizons | robustness | 0.99 | 6 | -0.148% | -0.952% | 0.954% | 0.656% | 99.531% | 100.000% | 8.0 | +1.020% | -10.171% |
| Historical quarterly robustness horizons | robustness | 1 | 6 | +0.000% | +0.000% | 0.000% | 0.000% | 100.000% | 100.000% | 8.0 | +0.000% | +0.000% |

## Net-of-cost empirical robustness

These rows are visually and inferentially separate from gross frictionless safety. Every row is outside the current epsilon-DCA theorem and has no confirmatory test.

| Evidence source | Analysis/design slice | Cost route | Comparison | Cells | Negative / zero / positive medians | Median range | Worst observed shortfall |
|---|---|---|---|---:|---:|---:|---:|
| `deterministic-primary-v1` | exploratory | fixed-1-usd | Complete-system performance | 3 | 0 / 0 / 3 | +9.781% to +22.754% | 0.000% |
| `deterministic-primary-v1` | exploratory | proportional-10bps | Complete-system performance | 3 | 0 / 0 / 3 | +9.780% to +22.755% | 0.000% |
| `deterministic-primary-v1` | primary | fixed-1-usd | Complete-system performance | 42 | 27 / 3 / 12 | -8.572% to +34.915% | 8.572% |
| `deterministic-primary-v1` | primary | proportional-10bps | Complete-system performance | 42 | 27 / 0 / 15 | -8.548% to +34.917% | 8.548% |
| `deterministic-primary-v1` | regression | fixed-1-usd | Complete-system performance | 9 | 1 / 3 / 5 | -0.253% to +2.519% | 0.253% |
| `deterministic-primary-v1` | regression | proportional-10bps | Complete-system performance | 9 | 1 / 0 / 8 | -0.231% to +2.533% | 0.231% |
| `historical-confirmatory-v1` | robustness | fixed-1-usd | Complete-system performance | 18 | 18 / 0 / 0 | -4.598% to -0.335% | 18.979% |
| `historical-confirmatory-v1` | robustness | proportional-10bps | Complete-system performance | 18 | 18 / 0 / 0 | -4.592% to -0.330% | 18.957% |
| `historical-registered-robustness-v1` | robustness / primary / primary-monthly-robustness-coverage | fixed-1-usd | Complete-system performance | 30 | 30 / 0 / 0 | -4.818% to -0.034% | 20.243% |
| `historical-registered-robustness-v1` | robustness / primary / primary-monthly-robustness-coverage | proportional-10bps | Complete-system performance | 30 | 30 / 0 / 0 | -4.805% to -0.033% | 20.217% |
| `historical-registered-robustness-v1` | robustness / robustness / robustness-quarterly-horizons | fixed-1-usd | Complete-system performance | 48 | 48 / 0 / 0 | -23.508% to -0.026% | 32.190% |
| `historical-registered-robustness-v1` | robustness / robustness / robustness-quarterly-horizons | proportional-10bps | Complete-system performance | 48 | 48 / 0 / 0 | -23.484% to -0.026% | 32.148% |
| `stochastic-primary-v1` | exploratory | fixed-1-usd | Complete-system performance | 45 | 17 / 0 / 28 | -1.207% to +1.207% | 2.652% |
| `stochastic-primary-v1` | exploratory | proportional-10bps | Complete-system performance | 45 | 17 / 0 / 28 | -1.196% to +1.214% | 2.641% |
| `stochastic-primary-v1` | primary | fixed-1-usd | Complete-system performance | 45 | 33 / 0 / 12 | -0.897% to +0.204% | 1.648% |
| `stochastic-primary-v1` | primary | proportional-10bps | Complete-system performance | 45 | 33 / 0 / 12 | -0.887% to +0.206% | 1.639% |

## Analysis-tier boundary

| Tier | Permitted interpretation |
|---|---|
| Confirmatory H1/H2 | Historical primary frictionless non-unit cells only; dependence-aware block bootstrap and the sealed 36-test Holm family apply. |
| Secondary | Lambda-one collapse, safety-architecture, mechanisms, exposure, downside, cash/unit attribution, and purchases are descriptive. |
| Registered robustness | Additional historical coverage, quarterly horizons, and all cost rows are descriptive and do not enter H1/H2. |
| Controlled stochastic primary | Baseline stochastic families are finite sensitivity evidence over three saved seeds, not population estimates. |
| Exploratory | Explicit stochastic sensitivity configurations and the deterministic design iteration remain hypothesis-generating; no historical exploratory regime result was run. |
