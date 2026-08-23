---
profile: smartdca-okf/0.4
type: research-note
title: "Arbitrary-horizon cash-timing identity and exact-rational verification seam"
description: "Proof of the finite-horizon cash-timing identities and specification of the exact-rational DCA, corrected, and neutral ledger interface."
knowledge_role: evidence
status: stable
sources:
  - id: ticket-01
    title: "Establish the arbitrary-horizon accounting and verification seam"
    resource: .scratch/smartdca/efforts/arbitrary-horizon-performance/issues/01-establish-accounting-verification-seam
    source_kind: internal
  - id: guarded-rule
    title: "The guarded corrected-mean SmartDCA rule"
    resource: research/definitions/guarded-corrected-mean-smartdca-rule
    source_kind: internal
  - id: two-purchase-boundary
    title: "Two-purchase guarded SmartDCA has an exact DCA boundary"
    resource: research/theorems/two-purchase-guarded-smartdca-boundary
    source_kind: internal
  - id: three-purchase-effect
    title: "Three-purchase guarded SmartDCA has an exact beta-sensitive DCA boundary"
    resource: research/theorems/three-purchase-corrected-mean-effect
    source_kind: internal
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-23T22:31:24Z
generation_run: urn:uuid:62ed4e2a-e3aa-4fb9-933c-8335a647cadc
verified:
  - by: openai-codex/spec-review-0.1
    at: 2026-08-23T22:36:39Z
    review_run: urn:uuid:7d7be1a1-3482-44ae-be16-e07cd8bc3010
---
# Arbitrary-horizon cash-timing identity and exact-rational verification seam

Canonical home: [Arbitrary-horizon terminal wealth has an exact cash-timing identity](../theorems/arbitrary-horizon-cash-timing-identity.md). That concept carries the statement; this note carries the proof, executable-interface contract, independent accounting routes, and exact regression evidence.

## 1. Model and notation

Fix an arbitrary finite horizon \(n\ge1\), purchase prices
\(p_1,\ldots,p_n>0\), nonnegative exogenous deposits
\(d_1,\ldots,d_n\ge0\), and a common evaluation price \(P>0\). A strategy
chooses purchases \(x_t\) without borrowing; its carried cash, accumulated
units, and terminal wealth are

\[
C_0=0,qquad C_t=C_{t-1}+d_t-x_t\ge0,qquad
Q_n=\sum_{t=1}^n\frac{x_t}{p_t},qquad
W_n=C_n+PQ_n.
\tag{1}
\]

DCA purchases \(d_t\) at each date, carries no cash, and has

\[
W_n^{DCA}=P\sum_{t=1}^n\frac{d_t}{p_t}.
\tag{2}
\]

This is the same fully funded, cash-inclusive comparison model inherited by
the guarded corrected-mean rule.[^guarded-rule]

## 2. Proof of the arbitrary-horizon identity

The cash recursion in (1) gives the pointwise spending difference

\[
x_t-d_t=C_{t-1}-C_t.
\tag{3}
\]

Substitute (3) into direct terminal-wealth accounting:

\[
\begin{aligned}
W_n-W_n^{DCA}
&=C_n+P\sum_{t=1}^n\frac{x_t-d_t}{p_t}\\
&=C_n+P\sum_{t=1}^n\frac{C_{t-1}-C_t}{p_t}.
\end{aligned}
\tag{4}
\]

Because \(C_0=0\), shifting the first sum in (4) by one index yields

\[
\sum_{t=1}^n\frac{C_{t-1}-C_t}{p_t}
=\sum_{t=1}^{n-1}C_t
\left(\frac1{p_{t+1}}-\frac1{p_t}\right)
-\frac{C_n}{p_n}.
\tag{5}
\]

Combining (4) and (5) proves

\[
\boxed{
W_n
=W_n^{DCA}
+C_n\left(1-\frac{P}{p_n}\right)
+P\sum_{t=1}^{n-1}C_t
\left(\frac1{p_{t+1}}-\frac1{p_t}\right).
}
\tag{6}
\]

No property of the strategy beyond the common deposits is needed for the
algebra. Full funding supplies the financial interpretation \(C_t\ge0\).
Positive prices and a positive evaluation price make every term finite.

## 3. Two-strategy form

Let \(S\) and \(T\) be two strategies on the same prices and deposits. Apply
(6) to both and subtract the common DCA term. With
\(\Delta C_t=C_t^S-C_t^T\),

\[
\boxed{
W_n^S-W_n^T
=\Delta C_n\left(1-\frac{P}{p_n}\right)
+P\sum_{t=1}^{n-1}\Delta C_t
\left(\frac1{p_{t+1}}-\frac1{p_t}\right).
}
\tag{7}
\]

Equation (7) is the required cash-path-difference identity. Taking \(T\) to
be DCA sets \(C_t^T=0\) and recovers (6). Taking \(S\) and \(T\) to be the
corrected and neutral guarded selectors isolates the discretionary score while
holding the shared guardrail implementation fixed.

The coefficients make the economics explicit. Carried cash helps across a
price fall, hurts across a price rise, and has no intermediate effect across a
flat step. The terminal coefficient compares holding cash with purchasing at
\(p_n\) and valuing at \(P\). These signs do not themselves determine the
whole sum, so the identity is not a performance theorem.

## 4. Exact-rational scenario interface

[`reproducibility/arbitrary_horizon.py`](../../reproducibility/arbitrary_horizon.py)
exposes one public seam:

```python
from fractions import Fraction as F
from reproducibility.arbitrary_horizon import RationalScenario, evaluate_scenario

ledger = evaluate_scenario(
    RationalScenario(
        prices=(F(1), F(4), F(2)),
        deposits=(F(1), F(1), F(1)),
        evaluation_price=F(7, 3),
        safety_factor=F(1, 2),
        alpha=F(0),
        beta=F(1),
    )
)
```

The seam deliberately implements the effort's initial \(f=\mathrm{id}\),
equal-weight region. Every numeric input is a `Fraction`; floats are rejected.
Off the diagonal it evaluates

\[
R=\left(\frac{\sum_i z_i^\alpha}{\sum_i z_i^\beta}
\right)^{1/(\alpha-\beta)},
\tag{8}
\]

and on the diagonal it evaluates

\[
R=\prod_i z_i^{z_i^\alpha/\sum_jz_j^\alpha},
\tag{9}
\]

using a canonical radical normal form plus exact integer-root checks. The
score is \(a=[1+r^{1-\alpha}]^{-1}\). Irrational terms may cancel: the seam
accepts a reference whenever the final result is rational, even if individual
radicals are not. It raises `ExactRationalError` only when an externally
required corrected reference or score is not rational; it never rounds or uses
a tolerance.

The three returned policy ledgers are:

- `dca`, calculated independently by investing each deposit immediately;
- `corrected`, using the corrected reference and guarded score; and
- `neutral`, using the same guardrail engine with score \(1/2\) at every
  discretionary date.

Each guarded `PolicyStep` exposes the price, deposit, available cash,
corrected reference, relative price, score, coverage before purchase, raw and
clipped guardrail floor, floor-branch flag, discretionary interval, purchase,
carried cash, units, DCA units, and coverage after purchase. The neutral
ledger exposes the same reference as a diagnostic, but its score remains
\(1/2\). At the first date the reference is `None` because only the warm-up
relative price \(r_1=1\) is defined. When the guardrail leaves no discretionary
cash, an irrelevant corrected reference is not evaluated: its reference,
relative-price, and corrected-score fields are `None`. DCA's inapplicable
reference, score, and guardrail fields are also `None`.

Each `PolicyLedger` exposes direct terminal wealth, every term in (6), and
cash-timing terminal wealth. `ScenarioLedger.gap(left, right)` exposes the
direct gap, the independently evaluated difference-cash-path form (7), and
the exact `win`, `tie`, or `loss` classification. Construction fails if the
two routes disagree.

## 5. Named exact checks

[`check_arbitrary_horizon_accounting_verification.py`](../../reproducibility/checks/check_arbitrary_horizon_accounting_verification.py)
keeps the earlier exact verifiers as regression prior art rather than
re-deriving its expected fractions from the new engine.[^two-purchase-boundary][^three-purchase-effect]

| Named check | Exact evidence |
|---|---|
| One-purchase ledger | With \(p=1,d=2,P=3,\lambda=1/2\), the corrected and neutral purchase is \(3/2\), terminal cash is \(1/2\), and both accounting routes give the DCA gap \(-1\). |
| Two-purchase corrected/neutral flip | At \((p_1,p_2,P)=(1,2,3/2)\), the corrected gap is \(1/48\) and the neutral gap is \(-1/32\). |
| Two-purchase win/tie/loss | On constant purchase prices with \(P=1/2,1,2\), the corrected gaps are \(1/4,0,-1/2\). |
| Two-purchase all-win witness | With \(d=(1,0)\), \(p=(1,1/2)\), and \(P=500\), terminal cash is \(1/12\) and the exact gap is \(167/4\); the prior result gives the whole slice as \(1/12+y/24>0\). |
| Three-purchase beta flip | On the settled witness, \(\beta=-1\) gives \(R_2=8/5,a_3=4/9,\Delta=-1/36\), while \(\beta=1\) gives \(R_2=5/2,a_3=5/9,\Delta=1/144\). |
| Diagonal three-purchase reference | The same witness at \(\alpha=\beta=0\) gives \(R_2=2,a_3=1/2,\Delta=-1/96\). |
| True neutral selector | A score of \(1/2\) at every date gives \(-5/24\) on the beta witness; this is distinct from the diagonal corrected rule because the latter keeps the beta-independent date-two score \(1/5\). |
| Guardrail branches | The beta witness has active/inactive/active floor branches; a five-date constant path has active/active/inactive/inactive/inactive branches. |
| Arbitrary horizons | Five-date constant and six-date nonconstant scenarios verify direct and cash-timing wealth for DCA, corrected, and neutral ledgers and all three pairwise gaps. |
| Boundaries | Constant prices at the common evaluation price tie, all-zero deposits produce zero ledgers, and \(\lambda=1\) makes both guarded policies collapse transaction by transaction to DCA without evaluating irrelevant irrational references. |
| Exact-domain boundary | Fractional parameters \((\alpha,\beta)=(1/2,-1/2)\) reproduce \(R_2=2,a_3=1/3\). Both a diagonal cube-root cancellation and an off-diagonal radical-sum cancellation return the final rational reference \(2\); an attempted final reference \(R_2=\sqrt2\) raises `ExactRationalError`. |

The legacy two- and three-purchase programs still pass independently. The new
check is run with

```bash
python -m reproducibility.checks.check_arbitrary_horizon_accounting_verification
```

## 6. Scope limit

The theorem is arbitrary-horizon accounting; the executable scenarios are
finite exact regressions. Their agreement does not turn enumeration into a
proof, and the proof does not show that the corrected score has a favorable
sign. This ticket establishes the reusable seam for the later falsification
search. It does not search horizons four through eight, assert cash-path
single crossing, or advance the next ticket.[^ticket-01]

[^ticket-01]: [Establish the arbitrary-horizon accounting and verification seam](../../.scratch/smartdca/efforts/arbitrary-horizon-performance/issues/01-establish-accounting-verification-seam.md)
[^guarded-rule]: [The guarded corrected-mean SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md)
[^two-purchase-boundary]: [Two-purchase guarded SmartDCA has an exact DCA boundary](../theorems/two-purchase-guarded-smartdca-boundary.md)
[^three-purchase-effect]: [Three-purchase guarded SmartDCA has an exact beta-sensitive DCA boundary](../theorems/three-purchase-corrected-mean-effect.md)
