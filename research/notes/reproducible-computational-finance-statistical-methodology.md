# Reproducible computational-finance and statistical methodology

## Search protocol and limits

This note supports the thesis section on outcome-blind registration,
overlapping-window inference, multiplicity, computational reproducibility, and
provenance-bound release. The search was completed on **2026-09-04**. All DOI,
publisher, author, and standards links in this note were last accessed on that
date.

The search followed title and concept queries to original journal articles,
DOI records, openly available author manuscripts, and official standards or
institutional publications. The principal query concepts were:

- `preregistration confirmatory exploratory outcome access data snooping`;
- `financial models overlapping observations dependence`;
- `stationary observations moving block bootstrap circular block resampling`;
- `Holm sequentially rejective familywise error arbitrary dependence`;
- `p-value effect size confidence interval estimation`;
- `computational reproducibility same data code independent replication`;
- `PROV entity activity agent derivation content hash name-data integrity`;
  and
- `FAIR authentication authorization clear data usage license`.

Included sources are original statistical or financial-econometric papers,
official methodological reports, and normative standards that directly own a
definition or method used in the thesis. A later source is used only when it
provides an official terminology boundary or an openly inspectable statement
that the early paper does not. Tertiary explainers, vendor marketing, and
generic software-development advice were excluded. The W3C, IETF, and FAIR
sources support artifact identity, lineage, and access vocabulary only; they
are not treated as financial evidence.

The review is **not exhaustive**. No subscription citation index or complete
forward-citation census was available, and the bounded search **does not
establish novelty**. Publisher or stable bibliographic records were available
for every source. Full text was directly inspectable for Nosek et al., Künsch,
the Politis--Romano Stanford report, Hernán--Robins, Wasserstein--Lazar,
Gardner--Altman, Peng, the National Academies report, PROV-DM, RFC 6920, and
the FAIR principles. The independent citation review additionally inspected an
original-article scan of Holm and confirmed Scheme 1 and Theorem 1 against the
stable journal record. For White, Richardson--Smith, and Harvey--Liu--Zhu, the
primary DOI or stable journal record and available abstract were checked;
claims here are limited to the method and scope established by those records.

This is a methodological positioning exercise, not a reanalysis. It neither
recomputes the historical results nor tests the assumptions required by the
registered bootstrap. Reproducible execution can repeat a misspecified model
or a coding error, and valid uncertainty calculations do not convert an
observational historical comparison into causal evidence.

## Authoritative source coverage

### Outcome-blind design and financial data snooping

Nosek et al. define preregistration as committing to research questions and an
analysis plan before observing the research outcomes. Their central purpose is
to distinguish prediction from postdiction, or confirmatory from exploratory
analysis; they explicitly preserve a valuable role for postdiction when it is
identified as such. They also qualify the case for improved reproducibility as
being true "in principle" and explain that benefits are lost when the
registration is not followed. This supports a temporal and reporting boundary,
not a certification that a design, model, or interpretation is correct
([Nosek et al., 2018, pp. 2600--2606](https://doi.org/10.1073/pnas.1708274114),
especially "Preregistration Distinguishes Prediction and Postdiction" and
"Preregistration in Practice"; `nosek2018preregistration`).

White's reality check addresses a related but different problem: inference
after a specification search. It tests whether the best model encountered in
a declared search has predictive superiority over a benchmark while accounting
for data snooping. It does not turn an undisclosed or outcome-expanded search
universe into a prespecified confirmatory design, and it is not the procedure
used for the thesis's 36 tests
([White, 2000, pp. 1097--1126](https://doi.org/10.1111/1468-0262.00152),
official abstract; `white2000datasnooping`).

Together these sources justify two restrained statements. Reusing one history
to choose and assess a preferred rule creates a selection problem, and
recording a sufficiently specific plan before outcome access makes advance
tests distinguishable from result-contingent analyses. Neither source implies
that registration removes all researcher judgment, proves absence of all prior
knowledge, supplies causal identification, or makes a repository registration
equivalent to an externally peer-reviewed Registered Report.

### Overlapping financial observations and block resampling

Richardson and Smith develop tests for restrictions implied by financial
models when the observations overlap. Their method explicitly models the
dependence induced by overlap instead of treating the resulting multiperiod
observations as independent. This is the closest finance-specific source for
the thesis's warning that different rolling start dates are not independent
replications when their investment windows reuse market observations
([Richardson and Smith, 1991, pp. 227--254](https://doi.org/10.1093/rfs/4.2.227),
official abstract; `richardsonsmith1991overlap`). Their paper does not
study SmartDCA episodes and does not prescribe the thesis's block length.

Künsch extends jackknife and bootstrap standard-error estimation from
independent data to a general stationary sequence by resampling blocks of
consecutive observations. The paper's asymptotic justification uses conditions
on the dependence and on block length, including a block length that grows
while remaining small relative to sample size; the name "block bootstrap" is
therefore not a finite-sample validity guarantee for any arbitrary block rule
([Künsch, 1989, pp. 1217--1241](https://doi.org/10.1214/aos/1176347265),
abstract and Sections 2--3; `kunsch1989blockbootstrap`).

Politis and Romano place the observed series on a circle and sample fixed-length
blocks from all start positions, allowing blocks at the end to wrap to the
beginning. Circularization treats positions symmetrically and avoids the edge
underrepresentation of a noncircular moving-block list. It is a resampling
construction for stationary data: the wrap does not assert that the first and
last historical dates are literally adjacent, and it does not create new
independent financial histories
([Politis and Romano, 1992, pp. 263--270](https://purl.stanford.edu/xh812zd4638),
also Stanford Technical Report EFS NSF 370, March 1991;
`politisromano1992circular`).

Hernán and Robins distinguish causal effects from associational quantities and
make identification depend on a causal question, a study design, and explicit
assumptions. Their framework is cited only for that boundary. Adjusting a
sampling distribution for serial dependence changes uncertainty estimation;
it supplies none of the treatment assignment, exchangeability, consistency,
positivity, or measurement conditions that a causal interpretation would need
([Hernán and Robins, 2020, Part I](https://miguelhernan.org/whatifbook);
`hernanrobins2020`).

### Multiplicity, effect magnitude, and interval reporting

For $m$ valid marginal $p$-values ordered as
$p_{(1)}\le\cdots\le p_{(m)}$, Holm's sequentially rejective Bonferroni
procedure compares $p_{(i)}$ with $\alpha/(m-i+1)$ in order and stops at
the first nonrejection. Equivalently, the ordered adjusted values are

\[
  \widetilde p_{(i)}
  =\min\!\left\{1,
    \max_{1\le j\le i}(m-j+1)p_{(j)}
  \right\}.
\]

Holm proves family-wise error control without requiring independence among the
tests. The guarantee still requires valid input $p$-values and a defined
family; it cannot repair a misspecified resampling distribution or a family
expanded after outcomes are seen
([Holm, 1979, pp. 65--70](https://www.jstor.org/stable/4615733),
especially the sequential procedure and Theorem 1; `holm1979`). Applying Holm
to test $p$-values does not by itself make separately calculated percentile
intervals simultaneous or multiplicity-adjusted.

The finance-specific reason to take the family seriously is illustrated by
Harvey, Liu, and Zhu. Their census and multiple-testing analysis of hundreds of
published return factors shows why the conventional single-test hurdle is too
permissive after extensive factor search. Their proposed thresholds and factor
setting are not the thesis's Holm procedure, but the paper is direct evidence
that multiple testing is a material financial-econometric concern
([Harvey, Liu, and Zhu, 2016, pp. 5--68](https://doi.org/10.1093/rfs/hhv059),
official abstract; `harveyliuzhu2016`).

The American Statistical Association's six principles state, among other
things, that scientific conclusions should not be based only on whether a
$p$-value crosses a threshold, that selective reporting requires
transparency, and that a $p$-value does not measure effect size or result
importance. A rejection decision is therefore not a magnitude estimate, and a
nonrejection does not establish a zero effect or equivalence
([Wasserstein and Lazar, 2016, pp. 129--133](https://doi.org/10.1080/00031305.2016.1154108),
p. 131; `wassersteinlazar2016`). Gardner and Altman likewise argue for reporting
an estimate with a confidence interval so that magnitude and precision remain
visible rather than reducing a finding to a significance label
([Gardner and Altman, 1986, pp. 746--750](https://doi.org/10.1136/bmj.292.6522.746);
`gardneraltman1986`). These are general statistical reporting authorities, not
evidence for the economic desirability of any investment policy.

### Computational reproducibility and replication

Peng describes reproducible computational research as making the analytic data
and code available so that others can inspect and rerun the analysis. He calls
this an attainable minimum standard when full independent replication is not
feasible and explicitly distinguishes reanalysis of the same data from a study
using independently collected data
([Peng, 2011, pp. 1226--1227](https://doi.org/10.1126/science.1213847);
`peng2011reproducible`).

The National Academies sharpen that vocabulary. Their adopted definitions are:

- **reproducibility**: consistent computational results using the same input
  data, computational steps, methods, code, and conditions of analysis; and
- **replicability**: consistent results across studies addressing the same
  scientific question when each study obtains its own data.

The report recommends recording inputs, computational steps, parameters, and
environmental details. It also recognizes legal and proprietary restrictions
on nonpublic data and calls for alternative mechanisms in such settings. Exact
or bitwise reproduction may often be expected, but is not a universal
requirement; most importantly, the report states that exact reproduction can
repeat the same code error and does not guarantee correctness
([National Academies, 2019, Conclusion 3-1, Recommendation 4-1,
Chapter 4's "Assessing Reproducibility," and Recommendation 6-5](https://doi.org/10.17226/25303);
`nasem2019reproducibility`).

### Provenance, content identity, and licensed access

PROV-DM defines provenance in terms of entities, activities, and agents. Its
core relations include generation, usage, derivation, attribution, and
association; a detailed derivation can identify the input entity, producing
activity, usage, and generated entity. The model supports a record of how an
artifact came to exist. It does not say that a recorded derivation is
scientifically sound, that the source data are accurate, or that an
interpretation is true
([Moreau and Missier, 2013, Sections 2.1 and 5.2](https://www.w3.org/TR/2013/REC-prov-dm-20130430/);
`moreaumissier2013prov`).

RFC 6920 standardizes names that incorporate a hash-function output. Its
security discussion calls the resulting property a **name--data integrity
binding**: a verifier can compare the bytes returned for a name with the hash
in that name. The RFC also states that the evidence is only as good as the
integrity of the starting name, depends on the selected hash and truncation,
and does not protect confidentiality. A SHA-256 digest can therefore bind a
declared identity to exact bytes; it does not make the storage physically
immutable, authenticate every semantic claim, or disclose the referenced
object
([Farrell et al., 2013, Sections 2 and 10](https://www.rfc-editor.org/rfc/rfc6920);
`farrell2013rfc6920`).

The FAIR principles separate accessibility from unrestricted openness. A1.2
permits authentication and authorization where necessary, A2 requires metadata
to remain accessible even when data are not, and R1.1 calls for a clear and
accessible data-usage licence. These principles support a documented restricted
access route; they do not themselves supply a licence or override a provider's
terms
([Wilkinson et al., 2016, Box 2](https://doi.org/10.1038/sdata.2016.18);
`wilkinson2016fair`). A fingerprinted private source and a public metadata
receipt can therefore preserve FAIR-compatible access metadata and remain
auditable without implying a right to publicly redistribute the source
observations. This note does not claim that the repository or restricted data
package fully satisfies every FAIR principle.

## Statistical-method synthesis

### Registration fixes a reporting boundary, not empirical truth

The repository's **outcome-blind confirmatory registration** and
provider-replacement protocol freeze
the two confirmatory hypotheses, estimand, datasets, primary horizons and
coverage grid, frictionless scope, circular moving-block bootstrap, and one
36-test Holm family before confirmatory outcome access.[^protocols] The
provider replacement records the narrow source change and preserves the
inherited outcome-relevant design. This is appropriately described as an
**outcome-blind protocol** within the documented access history. It should not
be described as blindness to all prior market knowledge or as a
preregistration deposited in a third-party registry. A Registered Report is a
separate peer-reviewed publication format, not a synonym for either record.

The evidence tiers follow when each analysis became eligible for its label:

| Tier | Repository meaning | Permitted interpretation |
| --- | --- | --- |
| Confirmatory | Frozen H1/H2 primary cells, estimand, block procedure, and Holm family evaluated after the registration boundary. | Registered inference under the stated design and statistical assumptions. |
| Secondary | Prespecified architecture, mechanism, and compatibility summaries that were not members of H1/H2. | Descriptive support for accounting or mechanism; no promotion into the confirmatory family. |
| Descriptive robustness | A separately identified plan frozen after the primary confirmatory run but before the extension's own outcomes, with no registered uncertainty analysis. | Within-grid signed summaries and coverage information; no new $p$-value, interval, parameter ranking, or revision of H1/H2. |
| Exploratory | Diagnostics or hypotheses suggested after seeing relevant outcomes. | Hypothesis generation and transparent description, not a confirmatory test on the same observations. |

Calling the extension "registered robustness" records its own prospective
identity. It does not move those post-confirmatory rows backward across the
primary outcome-access boundary. Conversely, an exploratory or descriptive
result is not scientifically worthless; the label prevents its evidential
strength from being overstated.

### Overlap changes uncertainty and effective information

For a rolling start $s$, an episode statistic is a function of a span of
market observations and the policy ledger over that span. Starts $s$ and
$s+1$ reuse most of the same observations for a horizon longer than one
stride. Distinct nominal dates therefore do not justify an independent and
identically distributed episode bootstrap. Overlap generally induces
dependence mechanically, and serial dependence in the underlying prices or
returns can add dependence beyond the shared-window span. The effective
information cannot be read from the raw episode count as though every row were
an independent market history; this note does not claim a single numerical
"effective sample size."

The **historical inferential unit** has three linked roles that must not be
pooled or renamed:

| Role | Unit in the primary historical study | Boundary |
| --- | --- | --- |
| Sampling unit | One ordered nominal monthly episode start, yielding one relative terminal-wealth gap for a named comparison. | $N$ is the number of included episode starts in that asset--horizon cell, not a count of independent histories. |
| Resampling unit | A consecutive circular block of the ordered episode starts and their episode-level gaps; blocks are concatenated and truncated back to $N$. | The block preserves local ordering within the resample; it does not make the original episodes independent. |
| Multiplicity unit | One declared asset--horizon--coverage--comparison cell hypothesis. | The 36 cells form a testing family, not 36 exchangeable observations for a pooled performance test. |

Within each asset--horizon cell, the implementation sorts episode estimands by
nominal start, draws circular blocks uniformly from the $N$ possible starts,
uses block length equal to the horizon in monthly-stride units, truncates the
last block at $N$, and recomputes the median relative terminal-wealth gap for
10,000 replicates.[^protocols] The horizon-length rule is frozen and
reproducible, but the cited literature does not prove it optimal. It need not
capture every longer-run market dependence, and circular wrapping is an
inferential device rather than a claim that the sample endpoints are adjacent
in calendar time.

The resulting percentile interval is a cellwise uncertainty summary. The
centered, Monte Carlo, two-sided $p$-value is a separate registered
calculation. Both depend on the adequacy of the ordered stationary/dependence
approximation. Block resampling addresses dependence in uncertainty
estimation; it **does not create causal identification**. No market treatment
was randomized, no exogenous policy adoption was observed, and no causal
effect of the signal on market outcomes follows from the resample.

### Holm decisions remain separate from estimates

The primary family contains

\[
  2\ \text{assets}\times3\ \text{horizons}\times
  3\ \text{non-unit primary coverage levels}\times
  2\ \text{confirmatory comparisons}=36
\]

two-sided tests. H1 is the complete-system corrected-guarded versus DCA
comparison; H2 is the corrected-guarded versus neutral-guarded signal
comparison. Holm is applied once across their 36 registered unadjusted
$p$-values. Conditional on their validity, it controls the probability of at
least one false rejection in that declared family without requiring the cell
tests to be mutually independent. It does not alter the observed median,
resampled statistic stream, or cellwise percentile interval.[^historical-audit]

The manuscript should report, for each material cell or clearly delimited
summary, the signed median relative terminal-wealth gap, episode count,
cellwise interval, unadjusted $p$-value, and Holm-adjusted decision where
applicable. The signed relative median is the effect-size estimand; the
$p$-values are diagnostics under the registered null and resampling rule.
Neither a small $p$-value nor a wholly negative interval establishes economic
importance without the magnitude and denominator. No H2 rejection means the
study did not confirm incremental signal value under that test; it does not
establish equality, equivalence, or a zero signal.

The secondary architecture cells and post-confirmatory robustness cells stay
outside the family. Appending them after their outcomes were known would change
the family rather than "strengthen" the original correction. Likewise, counts
of negative cells across horizons, assets, deterministic cases, stochastic
families, and historical episodes are heterogeneous summaries, not independent
trials that can be silently pooled.

## Reproducibility and provenance synthesis

### Four reproducibility and release claims

The repository uses narrower operational terms so that one successful rerun is
not mistaken for new empirical confirmation:

| Claim | Inputs and implementation | What can be learned | What cannot be claimed |
| --- | --- | --- | --- |
| Deterministic regeneration | The same accepted software is rerun on the same accepted inputs and declared conditions in a new output root; declared files or values are compared with the retained bundle. | The retained computation can be produced again under the declared conditions, including byte identity where the route promises it. | New-data replication, model validity, or freedom from a shared code error. |
| Independent reconciliation | A reviewer uses a separately implemented recurrence, regrouping, or inferential calculation against the same retained evidence. | Disagreement can reveal producer-code, aggregation, seed, bootstrap, Holm, join, or transcription defects; agreement reduces dependence on one implementation. | Independent-data replication or evidence about an unobserved provider series. The data and scientific design remain shared. |
| Provider-data receipt | A sanitized record binds provider and series semantics, request and parser metadata, coverage, byte length, and digest to access-controlled retained artifacts. | An authorized reviewer who possesses the bytes can check their identity and their declared provenance joins. | Reconstruction of the observations from the receipt, correctness of provider semantics, permission to access, or permission to redistribute. |
| Public redistribution | Source-bearing observations or artifacts are made publicly available under an applicable permission or licence. | A public reviewer may directly obtain those released bytes subject to the stated terms. | This right does not arise from a hash, manifest, citation, FAIR metadata, or successful private audit. |

Under the National Academies vocabulary, deterministic regeneration and much
of same-data reconciliation are computational reproducibility activities.
Independent reconciliation is stronger than replaying the producer's output
alone because its calculation path is separate, but it remains same-data
verification. The package has not performed a new study that obtained an
independent market dataset, so the historical review is not described as
replication.[^package-review]

The public route regenerates unrestricted deterministic and synthesis
artifacts. Historical acquisition inputs, episode rows, and price-bearing
ledgers remain access controlled. A public run can verify the sanitized receipt
for a previously completed private review; without the private bytes it cannot
rerun or independently inspect the historical observations. The claim must be
"receipt-bound private reconciliation," not "fully public historical
reproduction."

### Immutability is an identity rule

The project's accepted protocols, inputs, and run bundles use a no-overwrite
rule: changed accepted bytes receive a new version or content-derived identity,
and an existing run identity is a collision target rather than an output
directory to replace.[^artifact-adr] In this repository, **immutable** therefore
means immutable *under the publication protocol*. It does not mean that a
filesystem is physically incapable of mutation.

A manifest combines the identities and digests of inputs, code, and outputs;
PROV supplies the conceptual distinction among those entities and the
activities and agents that connect them. SHA-256 fingerprints implement a
content-identity check consistent with RFC 6920's name--data integrity
boundary. Given a trusted expected digest and accessible bytes, a mismatch
makes changed content detectable. A match does not by itself prove who created
the bytes, when they existed, whether a parser interpreted them correctly, or
whether the scientific conclusion is true.

### Provenance and access are orthogonal to financial evidence

The historical source receipt follows the glossary: it distinguishes Yahoo
Finance as provider from the pinned acquisition client, records the selected
series and field semantics, identifies the canonical client export rather than
calling it a raw provider response, fingerprints the retained bytes, and states
the redistribution decision.[^provider-review] This is a provenance and
retention control. It cannot replace the private source when a reviewer needs
to recompute an episode, and a content address is not a licence.

FAIR A1.2 permits an authenticated and authorized access path, while R1.1 asks
the publisher to state a clear data-usage licence. That separation is exactly
why access-controlled retention, sanitized public receipts, and public derived
aggregates can coexist. It does not imply that restricted data are publicly
reproducible, and it does not manufacture redistribution permission that the
provider has not granted.

Finally, the engineering controls and scientific evidence answer different
questions:

- hashes, manifests, identities, and provenance answer *which bytes and
  derivations are being discussed?*;
- regeneration and reconciliation answer *can declared computations be rerun
  or independently recomputed on those bytes?*;
- the statistical design and estimates answer *what did the registered sample
  show, with what dependence-aware uncertainty?*; and
- theorems answer *what follows for every path inside their stated models?*

Only the latter two layers bear on the financial conclusions, and only within
their assumptions. Software engineering can make a claim auditable; it **does
not establish a financial result**.

## Claim-to-evidence map

| Claim identifier | Manuscript-safe content | Primary or official sources and locators | Repository authority | Claim limit |
| --- | --- | --- | --- | --- |
| `claim-lit-method-registration` | The outcome-blind protocol fixed H1/H2 and their primary analysis before confirmatory outcome access; separately identified post-confirmatory robustness remains descriptive robustness, and later diagnostics remain exploratory. | `nosek2018preregistration`, pp. 2600--2606, especially the prediction/postdiction sections; `white2000datasnooping`, official abstract on the specification-search null and benchmark. | [Original protocol](../../experiments/protocols/safety-adaptivity-v1.json), [Yahoo replacement protocol](../../experiments/protocols/safety-adaptivity-yahoo-v2.json), [historical report](../../reports/experiments/confirmatory-historical-evaluation.md), and [run audit](confirmatory-historical-evaluation-audit.md). | Registration exposes the timing of choices; it does not validate assumptions, prove absence of bias, confer causal identification, or equal external Registered Report review. |
| `claim-lit-method-overlap-resampling` | Rolling starts reuse market observations and cannot be treated as independent histories; the registered circular moving-block bootstrap resamples ordered episode gaps within cells for dependence-aware uncertainty. | `richardsonsmith1991overlap`, official abstract; `kunsch1989blockbootstrap`, abstract and Sections 2--3; `politisromano1992circular`, pp. 263--270; `hernanrobins2020`, Part I causal/associational boundary. | [Yahoo protocol, `episode_design` and `uncertainty`](../../experiments/protocols/safety-adaptivity-yahoo-v2.json), [registered inference audit](confirmatory-historical-evaluation-audit.md), and [uncertainty artifact](../../reports/experiments/runs/smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221/uncertainty.json). | The frozen horizon-length block is not claimed optimal; bootstrap validity remains conditional, episodes do not become independent, and dependence handling does not create causal identification. |
| `claim-lit-method-multiplicity-reporting` | One 36-test H1/H2 family uses Holm family-wise error control; signed relative medians, cellwise intervals, and counts remain visible beside test decisions, and the ordered rolling starts remain the within-cell sampling units. | `holm1979`, pp. 65--70 and Theorem 1; `wassersteinlazar2016`, p. 131; `gardneraltman1986`, pp. 746--750; `harveyliuzhu2016`, official abstract. | [Protocol multiplicity and uncertainty](../../experiments/protocols/safety-adaptivity-yahoo-v2.json), [historical report](../../reports/experiments/confirmatory-historical-evaluation.md), and [registered inference audit](confirmatory-historical-evaluation-audit.md). | Holm assumes valid marginal $p$-values, does not adjust the percentile intervals, does not measure effect magnitude, and does not turn no rejection into equivalence. |
| `claim-lit-method-computational-reproducibility` | Deterministic regeneration reruns accepted code and inputs; independent reconciliation recomputes selected joins, ledgers, aggregates, bootstrap streams, and Holm values by a separate route. Neither is an independent-data replication. | `peng2011reproducible`, pp. 1226--1227; `nasem2019reproducibility`, Conclusion 3-1, Recommendation 4-1, Chapter 4's "Assessing Reproducibility," and Recommendation 6-5. | [Independent empirical-package review](safety-adaptivity-empirical-package-review.md) and [review checkpoint](../../reproducibility/checks/check_empirical_package_publication_review.py). | Exact replay can repeat a shared defect; byte identity is claimed only where declared, and restricted historical inputs prevent a fully public same-data rerun. |
| `claim-lit-method-provenance-release` | Versioned entities, derivations, hashes, and receipts bind the released claims to declared bytes; authenticated private audit and public redistribution are distinct. | `moreaumissier2013prov`, Sections 2.1 and 5.2; `farrell2013rfc6920`, Sections 2 and 10; `wilkinson2016fair`, Box 2 A1.2, A2, and R1.1. | [Artifact-layer ADR](../../docs/adr/0008-place-empirical-protocol-input-run-layers.md), [package review](safety-adaptivity-empirical-package-review.md), and [provider review](yahoo-finance-historical-data-provider-review.md). | A hash is an identity/fixity check rather than physical immutability, a receipt is not the source bytes, and neither provenance nor FAIR metadata grants a licence or validates a finance claim. |

## Citation and statistical-language verdict

**Independent review: pass (2026-09-04).** The reviewer compared the manuscript,
all 15 bibliography entries and section-local citations, five claim records,
glossary, both frozen protocols, historical report and audit, registered
uncertainty, package review, artifact ADR, and the original or official sources.
The initial pass found a sampling-versus-resampling-unit error, inconsistent
source-access and locator records, an insufficiently conditional Holm scope,
an implicit registry/Registered-Report distinction, and one mislabeled protocol
link. All were corrected. Follow-up review found no remaining citation or
statistical-language issue. The accepted boundaries are:

- use **outcome-blind registration** for the documented pre-outcome boundary,
  not as a claim that every source of judgment or bias was eliminated;
- call H1/H2 **confirmatory**, the separately executed extension
  **descriptive robustness**, and outcome-suggested work **exploratory**;
- say overlapping episodes are dependence-bearing analysis units and that
  circular blocks are the resampling device, not independent histories;
- describe block-bootstrap inference as conditional on the registered
  time-series approximation and keep it separate from causal identification;
- describe Holm as family-wise error control conditional on valid unadjusted
  $p$-values, while retaining signed effect sizes and cellwise intervals;
- reserve **replication** for a new study obtaining its own data under the
  National Academies definition;
- distinguish deterministic regeneration, independent same-data
  reconciliation, provider-data receipts, and public redistribution; and
- state that provenance and software engineering improve auditability but are
  not financial evidence.

The bounded review is **not exhaustive** and **does not establish novelty** for
any method or release pattern. The review establishes traceability and wording
fitness for this manuscript slice, not statistical validity outside the stated
assumptions or correctness of the financial conclusions.

### Primary and official references with intended bibliography keys

All links were accessed **2026-09-04**.

- `nosek2018preregistration`: B. A. Nosek, C. R. Ebersole, A. C. DeHaven,
  and D. T. Mellor, ["The Preregistration Revolution"](https://doi.org/10.1073/pnas.1708274114),
  *Proceedings of the National Academy of Sciences* 115(11) (2018),
  2600--2606.
- `white2000datasnooping`: H. White,
  ["A Reality Check for Data Snooping"](https://doi.org/10.1111/1468-0262.00152),
  *Econometrica* 68(5) (2000), 1097--1126.
- `richardsonsmith1991overlap`: M. Richardson and T. Smith,
  ["Tests of Financial Models in the Presence of Overlapping Observations"](https://doi.org/10.1093/rfs/4.2.227),
  *Review of Financial Studies* 4(2) (1991), 227--254.
- `kunsch1989blockbootstrap`: H. R. Künsch,
  ["The Jackknife and the Bootstrap for General Stationary Observations"](https://doi.org/10.1214/aos/1176347265),
  *Annals of Statistics* 17(3) (1989), 1217--1241.
- `politisromano1992circular`: D. N. Politis and J. P. Romano,
  ["A Circular Block-Resampling Procedure for Stationary Data"](https://purl.stanford.edu/xh812zd4638),
  in R. LePage and L. Billard, eds., *Exploring the Limits of Bootstrap*
  (Wiley, 1992), 263--270; official Stanford report EFS NSF 370 (March 1991).
- `hernanrobins2020`: M. A. Hernán and J. M. Robins,
  [*Causal Inference: What If*](https://miguelhernan.org/whatifbook)
  (Chapman & Hall/CRC, 2020).
- `holm1979`: S. Holm,
  ["A Simple Sequentially Rejective Multiple Test Procedure"](https://www.jstor.org/stable/4615733),
  *Scandinavian Journal of Statistics* 6(2) (1979), 65--70.
- `wassersteinlazar2016`: R. L. Wasserstein and N. A. Lazar,
  ["The ASA's Statement on \(p\)-Values: Context, Process, and Purpose"](https://doi.org/10.1080/00031305.2016.1154108),
  *American Statistician* 70(2) (2016), 129--133.
- `gardneraltman1986`: M. J. Gardner and D. G. Altman,
  ["Confidence Intervals Rather than P Values: Estimation Rather than Hypothesis Testing"](https://doi.org/10.1136/bmj.292.6522.746),
  *British Medical Journal* 292(6522) (1986), 746--750.
- `harveyliuzhu2016`: C. R. Harvey, Y. Liu, and H. Zhu,
  ["… and the Cross-Section of Expected Returns"](https://doi.org/10.1093/rfs/hhv059),
  *Review of Financial Studies* 29(1) (2016), 5--68.
- `peng2011reproducible`: R. D. Peng,
  ["Reproducible Research in Computational Science"](https://doi.org/10.1126/science.1213847),
  *Science* 334(6060) (2011), 1226--1227.
- `nasem2019reproducibility`: National Academies of Sciences, Engineering,
  and Medicine, [*Reproducibility and Replicability in Science*](https://doi.org/10.17226/25303)
  (National Academies Press, 2019).
- `moreaumissier2013prov`: L. Moreau and P. Missier,
  [*PROV-DM: The PROV Data Model*](https://www.w3.org/TR/2013/REC-prov-dm-20130430/),
  W3C Recommendation, 30 April 2013.
- `farrell2013rfc6920`: S. Farrell, D. Kutscher, C. Dannewitz, B. Ohlman,
  A. Keränen, and P. Hallam-Baker,
  [*Naming Things with Hashes*](https://www.rfc-editor.org/rfc/rfc6920),
  RFC 6920 (IETF, April 2013), DOI
  [10.17487/RFC6920](https://doi.org/10.17487/RFC6920).
- `wilkinson2016fair`: M. D. Wilkinson et al.,
  ["The FAIR Guiding Principles for Scientific Data Management and Stewardship"](https://doi.org/10.1038/sdata.2016.18),
  *Scientific Data* 3 (2016), 160018.

[^protocols]: Design join: [original frozen protocol](../../experiments/protocols/safety-adaptivity-v1.json) and [accepted Yahoo replacement protocol](../../experiments/protocols/safety-adaptivity-yahoo-v2.json), especially `registration_statement`, `episode_design`, `hypotheses`, `multiplicity`, `uncertainty`, and `analysis_tiers`.
[^historical-audit]: Inferential join: [audit of the confirmatory historical evaluation and robustness extension](confirmatory-historical-evaluation-audit.md), especially "Registered inference audit" and "Registered robustness extension audit."
[^package-review]: Reproduction join: [independent review of the safety-adaptivity empirical package](safety-adaptivity-empirical-package-review.md), especially "Independent reproduction," "Provenance, dependencies, and retention," and "Accounting and statistical audit."
[^artifact-adr]: Artifact-identity join: [ADR 0008: Place empirical protocols, inputs, and run bundles in versioned layers](../../docs/adr/0008-place-empirical-protocol-input-run-layers.md).
[^provider-review]: Source and rights join: [Yahoo Finance historical-data provider review](yahoo-finance-historical-data-provider-review.md), especially "Provider, client, and series identifiers" and "Dependency and redistribution decision."
