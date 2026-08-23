---
profile: smartdca-okf/0.4
type: research-note
title: "Primary-source audit of the causal DCA boundary and constructive relaxations"
description: "Novelty audit positioning the causal DCA boundary and ordering the admissible constructive relaxations."
knowledge_role: evidence
status: stable
sources:
  - id: ticket-08
    title: "Audit the novelty of the causal DCA boundary and choose a constructive relaxation"
    resource: .scratch/smartdca/issues/08-audit-causal-dca-novelty-and-relaxation
    source_kind: internal
  - id: causal-boundary
    title: "Pathwise DCA dominance under causal budget feasibility"
    resource: research/notes/pathwise-dca-dominance-under-causal-budget
    source_kind: internal
  - id: primary-literature
    title: "primary pointwise no-arbitrage and DCA minimax sources"
    resource: "primary mathematical and financial literature cited inline in this note"
    source_kind: scope
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-16T11:04:00Z
generation_run: urn:uuid:15b108f2-1ab8-4916-965a-89faffe7b3f6
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T07:38:00Z
    review_run: urn:uuid:16bd7b25-9e03-4aef-9c9a-5301cb317903
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T09:48:00Z
    review_run: urn:uuid:9a0f9f9a-73a7-4e3f-931d-a34c08fad81a
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T10:30:00Z
    review_run: urn:uuid:46a8aeeb-e6d2-49da-a062-28c4c51c1348
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T10:48:00Z
    review_run: urn:uuid:efbd9162-3fdb-43a6-a3c7-7ef6b7141532
  - by: openai-codex/smartdca-wiki-0.1
    at: 2026-08-16T11:14:00Z
    review_run: urn:uuid:5fdc289a-b5ff-4e1f-9d84-777c58a093f2
---
# Primary-source audit of the causal DCA boundary and constructive relaxations

Canonical home: [Causal DCA dominance impossibility](../theorems/causal-dca-dominance-impossibility.md) for the positioning and [Epsilon-DCA safety is exactly a causal unit-coverage guardrail](../theorems/epsilon-dca-safety-unit-guardrail.md) for the relaxation this note selected. This note carries the novelty audit and the ordering of admissible relaxations.

Research date: 2026-08-15

## Executive verdict

I did not locate a primary source that states
[the causal DCA dominance impossibility](../theorems/causal-dca-dominance-impossibility.md)
in its full DCA-specific form: arbitrary finite positive price paths, arbitrary exogenous
deposits, decisions after observing the current price but before future prices,
cash carry without interest, long-only buy-only purchases, no borrowing, the
same horizon, and terminal wealth including cash.

That non-discovery does **not** make the mathematical obstruction new. The core
impossibility is a **direct corollary of pointwise no-arbitrage after a
ticket-specific reduction**:

1. fix a deposit sequence;
2. subtract DCA from the candidate, so the common deposits cancel and the
   difference is a predictable, zero-initial-cost, self-financing strategy in
   stock and cash; and
3. observe that universal weak dominance with strict improvement on one path is
   exactly a one-point arbitrage.

Burzoni, Frittelli, Hou, Maggis, and Obłój define that arbitrage and prove that
it is absent precisely when every scenario is charged by a finite-support
martingale measure ([Burzoni et al. 2019, Definition 2.2 and Proposition 2.5](https://doi.org/10.1287/moor.2018.0956)).
The two results are numbered Definition 1 and Proposition 1 in the authors' arXiv preprint
and Definition 2.2 and Proposition 2.5 in the journal article; this note cites the journal
numbering wherever it cites the DOI, matching
[the ticket-04 positioning note](pathwise-dca-dominance-primary-sources.md), and keeps the
preprint numbering only where it cites the preprint PDF.
Every finite strictly positive price path is charged by such a measure on the
full positive path space. Therefore their result rules out strict universal
outperformance after the reduction. The additional conclusion that equality of
terminal wealth on all paths forces the candidate to equal DCA transaction by
transaction follows by an elementary backward/adversarial-continuation argument
using the richness of the positive path space; I did not find that DCA-specific
identification stated in the reviewed literature.

The safest manuscript position is therefore:

> The theorem is a DCA-specific specialization of pointwise no-arbitrage, with
> new-to-this-project deposit accounting and a sharp transaction-level equality
> case. Its exact published formulation was not located, but the core
> impossibility should not be advertised as a conceptually new no-arbitrage
> theorem.

The recommended constructive pivot is to retain every price path and all of the
implementation/accounting assumptions, but replace the unattainable floor

\[
W^S/W^{DCA}\ge 1
\]

by the arbitrarily close **epsilon-relative floor**

\[
W^{S_\varepsilon}/W^{DCA}\ge 1-\varepsilon,
\qquad 0<\varepsilon<1.
\]

A DCA-anchored construction can reserve a $1-\varepsilon$ share of each
deposit for DCA and send the remaining share to a causal, fully funded SmartDCA
component. This is a source-informed theorem target, not a theorem found in the
cited papers and not proved in this note. It is the weakest clean relaxation
reviewed: it changes only the performance threshold, is scale-free on unbounded
price/deposit domains, covers every path, and approaches the impossible boundary
as \(\varepsilon\downarrow0\).

## The theorem being positioned

The canonical statement of the positioned theorem, and of the comparison model it uses, is
[Causal DCA dominance impossibility](../theorems/causal-dca-dominance-impossibility.md);
the restatement below fixes the notation this audit's reduction argues in.

At purchase dates $t=1,\ldots,n$, let $p_t>0$ be the observed price and
$d_t\ge0$ the exogenous deposit. A candidate spends $x_t$, holds cash
$C_t=C_{t-1}+d_t-x_t\ge0$, and accumulates units
$Q_t=Q_{t-1}+x_t/p_t$. Its decision is causal and
$0\le x_t\le C_{t-1}+d_t$. At a later common evaluation price
$p_{n+1}>0$,

\[
W^S=C_n+p_{n+1}Q_n,
\qquad
W^{DCA}=p_{n+1}\sum_{t=1}^n\frac{d_t}{p_t}.
\]

That theorem proves that if $W^S\ge W^{DCA}$ for every positive price path and
every deposit sequence, then $x_t=d_t$ after every history. The candidate is
DCA, equality holds on every path, and strict improvement anywhere is
impossible.

Several details distinguish this statement from the usual use of “DCA” in the
literature. Deposits arrive exogenously rather than being slices of an initial
lump sum; the candidate cannot spend more than deposited cash; DCA is a causal
benchmark rather than an offline optimum; and unused cash is included in the
terminal payoff.

## Why pointwise no-arbitrage is a direct corollary envelope

### Equal-flow reduction

Fix any deposit sequence. Both portfolios receive exactly the same external
cash flow. Subtracting DCA's stock and cash holdings from the candidate's
holdings cancels those flows. The resulting signed difference portfolio starts
from zero and is self-financing between decision dates. Signed holdings in the
*difference* do not violate the project's long-only rule: each underlying
portfolio remains long-only and fully funded.

The difference payoff at evaluation is exactly

\[
V_{n+1}=W^S-W^{DCA}.
\]

Thus a candidate that is nonnegative relative to DCA on every path and positive
on one path produces the “one-point arbitrage” of Burzoni et al.: a predictable
self-financing gain that is nonnegative on the scenario set and strictly
positive at one scenario
([Definition 1](https://arxiv.org/pdf/1612.07618)).

### Why every positive path is martingale-supported

Burzoni et al.'s Proposition 2.5 says there is no one-point arbitrage on a
scenario set precisely when every scenario belongs to the support of a
finite-support martingale measure. The full finite positive path space has this
property. Given a target path, at each target node with current price $s>0$:

- if its target successor $y>s$, add a second positive successor $z<s$;
- if $y<s$, add a second successor $z>s$;
- if $y=s$, a single flat successor suffices.

Positive branch probabilities can be chosen so their conditional mean is
$s$. Freeze the off-target branches and repeat along the target branch. This
gives a finite tree, defines a martingale measure, and assigns positive mass to
the entire target path. Consequently every path is martingale-supported and a
one-point arbitrage is impossible.

This establishes the no-strict-improvement part as a direct corollary after the
equal-flow reduction. It also shows why all of the following matter: causality
(predictability), equal deposits (zero cost of the difference), self-financing
budget accounting, cash in terminal wealth, and an unrestricted positive path
space.

### What still comes from the ticket's own proof

Pointwise no-arbitrage implies that universal weak dominance cannot be strict;
it gives $W^S=W^{DCA}$ on every path. Transaction-level identity is then
obtained from the path space, not from a DCA theorem in the source. If a residual
cash amount first appears at price $p_t$, a later constant price and evaluation
level $M>p_t$ turns the missed units into a strict loss. Equivalently, backward
variation of the next price forces each difference holding to vanish at every
node. This identifies $x_t=d_t$ successively.

The distinction matters for novelty. The accounting reduction and equality-case
specialization may be worth presenting because they make the finance claim
transparent, but they do not turn a known no-arbitrage obstruction into a new
general principle.

## Primary-source comparison

The classifications below use “direct corollary” only when the ticket follows
after an explicit reduction. “Analogy” means that a source motivates a
relaxation or technique but does not imply the ticket under its stated
hypotheses.

| Area and primary source | Precise setting/result used here | Relation to ticket 04 |
|---|---|---|
| Pointwise/model-free finance: [Burzoni et al. (2019)](https://doi.org/10.1287/moor.2018.0956) | Finite-horizon predictable self-financing trading on a scenario set; a one-point arbitrage is nonnegative everywhere and positive somewhere. Proposition 2.5 characterizes its absence by finite-support martingale measures charging every scenario. | **Direct corollary envelope** after common deposits are cancelled. No DCA, deposit process, buy-only candidate, or transaction-level equality statement appears in the paper. |
| Probability-free finance: [Riedel (2015)](https://arxiv.org/abs/1107.1078) | A probability-free FTAP in a topological state space; full-support martingale measures arise endogenously under continuity assumptions. | Conceptual precursor/analogy. Burzoni et al. is the cleaner direct source because it uses one-point arbitrage and scenario-by-scenario martingale support. |
| DCA/minimax regret: [Pye (1971)](https://doi.org/10.1287/mnsc.17.7.379) | A fixed sum must be irreversibly converted into stock over a fixed number of periods. Under an arithmetic random walk with symmetric maximum up/down changes, dollar averaging is a **nonsequential minimax-regret** policy; Pye also derives a sequential minimax threshold policy tied to the running maximum. | **Closest DCA-specific criterion precedent**, but still an analogy. It starts with one lump sum, assumes a bounded/symmetric price-change model, optimizes regret rather than terminal wealth relative to same-deposit DCA, and does not assert universal dominance. |
| Classical DCA choice theory: [Constantinides (1979)](https://doi.org/10.2307/2330513) | Treats DCA as a policy depending on total wealth and wealth composition and shows it is dominated by optimal sequential and optimal nonsequential investment policies in the paper's expected-utility portfolio-choice setting. | Analogy. “Dominated” is model- and utility-based, not terminal-wealth dominance on every path; the capital is available for portfolio choice rather than arriving as ticket-04 deposits. |
| Stochastic dominance of DCA: [Vanduffel, Ahcan, Henrard, and Maj (2012)](https://doi.org/10.1142/S0219024912500136) | Under Lévy log returns and a fixed horizon, constructs a static portfolio of path-independent options preferred to DCA by risk-averse decision makers; in the Brownian case the construction uses power options. | Analogy and evidence for a stochastic-objective relaxation. It assumes a return law and enlarged tradable set, and its preference dominance is not stock-and-cash pathwise dominance with recurring deposits. |
| Universal portfolios: [Cover (1991)](https://doi.org/10.1111/j.1467-9965.1991.tb00002.x) | A nonanticipating, continually rebalanced portfolio approaches the best constant-rebalanced portfolio in hindsight in long-run exponential growth, path by path. The original analysis uses bounds involving the daily return range. | Analogy. The comparator is hindsight CRP, the result is asymptotic/relative, rebalancing permits sales, and there is one compounding wealth account rather than exogenous deposits. |
| Optimal universal ratio: [Ordentlich and Cover (1998)](https://doi.org/10.1287/moor.23.4.960) | Solves the finite-horizon max-min game for the wealth ratio between a nonanticipating strategy and the best constant-rebalanced portfolio in hindsight. The optimal ratio is below one at nontrivial finite horizons and decreases only polynomially. | Strong methodological analogy for a multiplicative performance relaxation. It quantifies the cost of causality but uses a different comparator, repeated rebalancing, and no deposits. |
| Online log-wealth regret: [Helmbold et al. (1998)](https://www.schapire.net/papers/HelmboldScSiWa98.pdf) | Exponentiated-gradient portfolio updates compete in cumulative log wealth with the best constant-rebalanced portfolio; each period selects a simplex portfolio and wealth is rebalanced. | Regret analogy only. The loss, comparator, trading technology, and capital-flow model differ from SmartDCA. |
| One-way trading: [El-Yaniv, Fiat, Karp, and Turpin (2001)](https://doi.org/10.1007/s00453-001-0003-0) | A trader starts with a fixed dollar budget and irrevocably converts fractions at sequentially announced exchange rates. Optimal competitive ratios are derived for variants using price bounds or information about the maximum-rate distribution; remaining wealth is ultimately converted. | Close buy-only online analogy, not a proof of the ticket. It compares with an offline best conversion, begins with a lump sum, requires bounds/distributional information in the relevant variants, and has no same-deposit DCA benchmark. |
| Bounded-return buy-and-hold: [Chen, Kao, Lyuu, and Wong (2001)](https://arxiv.org/abs/cs/0011018) | Under bounded daily returns, derives the unique optimal static online buy-and-hold algorithm and its exact competitive ratio; the paper also compares the rule empirically with dollar averaging. | Analogy supporting competitive criteria under a restricted price model. It changes both the path domain and comparator and does not model recurring deposits. |
| Pathwise relative arbitrage: [Karatzas and Kim (2020)](https://doi.org/10.1007/s00780-019-00414-2) | Probability-free functional generation on continuous market-weight paths yields sufficient conditions for strong relative arbitrage over suitable horizons, using structural variation conditions. | Analogy supporting path restriction as a route to exact outperformance. The benchmark is the market portfolio, trading is continuous and rebalancing-based, and the admissible path class has structural conditions absent from ticket 04. |
| SmartDCA source: [Calvet, Herranz-Celotti, and Valimamode (2023)](https://arxiv.org/abs/2308.05200) | Claims superiority through average-price/mean inequalities for price-responsive purchases, including bounded constructions. | Not an exact match or corollary. Ticket 04's same-deposit, fully funded terminal-wealth comparison was introduced precisely because average acquisition cost with strategy-dependent spending does not establish economic dominance. |

### Exact-match versus corollary verdict

- **Exact literature match found:** no.
- **Known result from which the core theorem follows:** yes, Burzoni et al.'s
  pointwise no-arbitrage result, after equal-flow cancellation and verification
  that the positive path space is martingale-supported.
- **Part not found verbatim:** the recurring-deposit DCA formulation and the
  transaction-by-transaction equality case.
- **Defensible novelty language:** “a DCA-specific specialization and sharp
  accounting/equality formulation,” not “a new impossibility principle.”

## One-assumption relaxations

Every option below is assessed while trying to retain causality, long-only
buy-only trading, full funding, the same deposits/horizon, and cash-inclusive
terminal wealth.

| Relaxation | What changes | What can plausibly become constructive | Main cost |
|---|---|---|---|
| Restrict deterministic paths | Replace all positive paths by a declared class; keep exact $W^S\ge W^{DCA}$. | Waiting rules dominate on nonincreasing paths; more elaborate structural variation classes are the pathwise-relative-arbitrage paradigm of Karatzas--Kim. | Exact dominance is retained, but the restriction must eliminate the adverse rising continuation after every history at which the strategy waits. Broad, economically natural classes are therefore hard to obtain, and a monotone class is strong. |
| Stochastic/expected objective | Replace the universal path quantifier by $E[W]$, expected utility, or stochastic dominance under a specified return law. | Dynamic programming or a causal threshold/mean-reversion rule may outperform DCA for the chosen estimand. Constantinides and Vanduffel et al. demonstrate that DCA can be improved under model/preference criteria. | Adds a probability law and often a utility function; conclusions become model-sensitive. Existing constructions commonly start with lump-sum capital or use options, so they do not transfer directly. |
| Additive regret | Permit $W^S\ge W^{DCA}-K$. | Potentially meaningful after normalizing deposits and bounding price relatives. | On the ticket's unbounded positive price and deposit domain, a fixed currency bound is not scale-free: the rising-continuation loss from any delayed amount can be made arbitrarily large. It therefore also requires bounds/normalization. |
| Competitive ratio with price bounds | Require $W^S\ge cW^{DCA}$ or compete with an offline benchmark on a bounded price domain. | One-way-trading and bounded-return algorithms provide mature tools and nontrivial optimal ratios. | Known results generally add price bounds and replace DCA by an offline comparator, changing more than one element of the ticket. |
| Epsilon-relative DCA floor | On every positive path require $W^{S_\varepsilon}\ge(1-\varepsilon)W^{DCA}$, with ε fixed ex ante. | A DCA-anchored, causal, fully funded, buy-only SmartDCA strategy can budget an ε share for adaptive purchases while retaining a universal downside floor and possible strict gains on favorable paths. | Gives up only an explicitly bounded fraction of DCA wealth. It does not promise weak dominance. |
| Asymptotic log-growth/regret | Compare long-run growth rates or cumulative log wealth. | Universal-portfolio methods obtain vanishing per-period regret against rich benchmarks. | Changes finite-horizon terminal-wealth meaning, usually assumes a single reinvested wealth account, and requires sales/rebalancing. |
| Relax causality | Permit future prices or a future-minimum oracle while retaining all paths. | Exact pathwise dominance is immediate by buying each deposit at a future minimum. | Violates the implementability requirement and is ruled out by this ticket's preservation criteria. |
| Enlarge funding/tradables | Permit borrowing, shorting, derivatives, or unequal deposits. | Options or leverage can create other dominance/preference results. | Changes the economic comparison rather than finding an implementable SmartDCA rule under the agreed model. |

## Recommendation: the epsilon-relative floor

This section and the next were written as targets for the following ticket, and their
mathematical content has since been proved. It is retained in the future tense as the
provenance of the choice rather than rewritten as a result: the canonical home of what was
proved is [the epsilon-DCA unit-coverage guardrail](../theorems/epsilon-dca-safety-unit-guardrail.md),
and the bounded component it asked for is
[the guarded corrected-mean SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md).
Requirements 1 to 4 of the recommended target below were delivered exactly. Requirement 5
was not delivered by the guardrail or score construction. The later
[two-purchase DCA boundary](../theorems/two-purchase-guarded-smartdca-boundary.md)
now gives the exact realized-path strict-win condition at the smallest horizon,
but it also proves that the strict-loss region is nonempty and that \(\beta\)
drops out. A uniformly favourable path class, stochastic estimand, or utility
criterion therefore remains open even though ticket 11 itself is resolved.
Two of this section's guesses were also overtaken: the guardrail is not the DCA-anchored
sleeve construction sketched here but the strictly larger class of all prefix-covering
strategies, of which the sleeve is one member; and the floor turned out to be exactly
attained rather than merely respected, so \(\lambda\) is sharp and not conservative.

The next constructive theorem should use a **multiplicative downside budget
relative to DCA**, not a stochastic objective or a narrow price class.

Recommended target (to be proved in the next ticket, not here): for every
$0<\varepsilon<1$ and horizon with at least two purchase dates, construct a
non-DCA strategy $S_\varepsilon$ such that

1. it is causal, long-only, buy-only, and fully funded;
2. it uses exactly the same exogenous deposits and horizon as DCA;
3. terminal wealth includes cash;
4. $W^{S_\varepsilon}\ge(1-\varepsilon)W^{DCA}$ on every finite positive
   price path and every deposit sequence; and
5. it strictly exceeds DCA on a nonempty, explicitly characterized favorable
   path class (and, later, its expected gain can be evaluated under declared
   stochastic models).

The natural construction is DCA-anchored: reserve $1-\varepsilon$ of every
deposit for immediate DCA purchases and allocate at most the remaining
ε share using a bounded causal rule induced by the corrected out quasi-Gini
score. Linearity of stock-and-cash accounting makes the universal floor
plausible without price bounds. The substantive work for the next theorem is
not the floor alone; it is to specify the bounded SmartDCA component, prove its
budget feasibility, and sharply characterize when its ε-funded sleeve beats
its DCA sleeve.

### Sharper candidate characterization

The next ticket should test and prove a stronger characterization, suggested by
the ticket's own accounting rather than by a located source. Put

\[
\lambda=1-\varepsilon,
\qquad
Q_t^{DCA}=\sum_{i=1}^t\frac{d_i}{p_i}.
\]

Under the arbitrary-positive-continuation hypothesis, the exact candidate is

\[
W^S\ge\lambda W^{DCA}\text{ on every path and deposit sequence}
\quad\Longleftrightarrow\quad
Q_t^S\ge\lambda Q_t^{DCA}
\text{ after every history and every }t.
\tag{*}
\]

The corresponding causal purchase constraint is

\[
x_t\ge
\left[
\lambda d_t-p_t\bigl(Q_{t-1}^S-\lambda Q_{t-1}^{DCA}\bigr)
\right]_+.
\tag{**}
\]

This appears sound and is a better theorem target than merely exhibiting the
DCA-anchored construction. Terminal prefix coverage is sufficient because cash
is nonnegative. For necessity, the proposed adversarial check is to take any
prefix unit deficit, set all later purchase prices to $P^2$, and evaluate at
$P$; for sufficiently large finite $P$, the deficit's terminal value exceeds
the finite cash and future-deposit offset. Equation (**) is then the algebraic
form of prefix coverage. These are proof directions for the next ticket, not a
completed proof in this literature note.

At λ=1, the constraint should collapse inductively to DCA, recovering ticket
04. At every λ<1, it leaves a nonempty discretionary region while retaining a
sharp universal terminal-wealth floor. A DCA-anchored strategy is one simple
member of this larger feasible class; the corrected out quasi-Gini rule can be
used only within the discretionary region.

I found no primary-source statement of (*) or (**) for recurring-deposit DCA.
They resemble a benchmark-superhedging/viability invariant, so the appropriate
position before a broader citation search is “a sharp DCA-specific
characterization suggested by the general no-arbitrage envelope,” not an
established novelty claim.

Both (\*) and (\*\*) were subsequently proved as stated, together with the third
equivalent form and the exact worst-case factor, and are now owned by
[the epsilon-DCA unit-coverage guardrail](../theorems/epsilon-dca-safety-unit-guardrail.md).
The proposed adversarial check above is the argument that the proof uses. The novelty
position in the paragraph above is unchanged by that proof and still stands.

This recommendation is weakest in three useful senses:

- **one threshold changes:** all paths and all implementation/accounting rules
  remain fixed, while the factor $1$ becomes $1-\varepsilon$;
- **arbitrarily close to the boundary:** ε can be selected as small as desired,
  whereas ε=0 is exactly
  [the impossibility boundary](../theorems/causal-dca-dominance-impossibility.md); and
- **scale-free:** unlike a fixed additive regret allowance, the guarantee remains
  meaningful when prices and deposits are unbounded.

Path restriction is the preferred alternative only if the paper insists on the
word “dominance.” It retains exact outperformance but pays for it by excluding
adverse continuations, and any useful class will need an independent economic
justification. A stochastic objective is better reserved for a second layer of
the paper because it introduces estimation and model risk. Noncausality is not
an implementable relaxation.

## Search coverage and limits

This was a targeted primary-source audit, not a proof of bibliographic novelty.
I searched publisher pages and full texts, author-hosted manuscripts, and arXiv
across these clusters:

- dollar-cost and dollar-averaging theory, including sequential, minimax,
  regret, utility, and stochastic-dominance formulations;
- online portfolio selection, universal portfolios, log-wealth regret, and
  finite-horizon hindsight ratios;
- one-way trading, online search, bounded daily returns, and buy-and-hold
  competitive analysis;
- pointwise/model-free finance, probability-free FTAP, one-point arbitrage, and
  pathwise relative arbitrage; and
- the SmartDCA source and its stated superiority criterion.

Searches included combinations of “dollar-cost averaging,” “pathwise,”
“terminal wealth,” “causal,” “one-point arbitrage,” “dominance,” “minimax
regret,” “one-way trading,” “competitive ratio,” “universal portfolio,” and
“exogenous deposits.” I followed relevant claims to the original articles or
author manuscripts and did not rely on surveys for the classifications above.

Limits remain material:

- no exhaustive citation-graph search in Scopus, Web of Science, MathSciNet, or
  zbMATH was available;
- some older journal full texts were paywalled, so their publisher abstracts
  and accessible author versions constrained the hypothesis checks;
- the search was English-language and targeted rather than exhaustive across
  adjacent savings-plan, actuarial, optimal-execution, and consumption-investment
  literatures; and
- exact wording can be absent even when a result is folklore or an unstated
  corollary.

Accordingly, “no exact match found” must not be converted into a novelty claim.
The positive evidence is stronger and sufficient for positioning: pointwise
no-arbitrage already supplies the general mathematical envelope.
