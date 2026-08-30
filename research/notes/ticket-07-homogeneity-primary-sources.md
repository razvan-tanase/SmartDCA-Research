---
profile: smartdca-okf/0.5
type: research-note
title: "Primary-source note: homogeneity of the canonical corrected out quasi-Gini mean"
description: "Characterization of when the corrected mean is degree-one homogeneous, with its source hypotheses."
knowledge_role: evidence
status: stable
sources:
  - id: ticket-07
    title: "Characterize homogeneity of the corrected out quasi-Gini mean"
    resource: .scratch/smartdca/issues/07-characterize-homogeneity-of-corrected-out-quasi-gini
    source_kind: internal
  - id: primary-literature
    title: "primary sources on Bajraktarevic and weighted Gini mean homogeneity"
    resource: "primary mathematical and financial literature cited inline in this note"
    source_kind: scope
generated:
  by: claude-code/smartdca-wiki-0.1
  at: 2026-08-16T10:20:00Z
generation_run: urn:uuid:51b6a4df-c98b-4784-83e4-3b068e4014ab
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
---
# Primary-source note: homogeneity of the canonical corrected out quasi-Gini mean

Canonical home: [Homogeneity characterization of the corrected out quasi-Gini mean](../theorems/corrected-mean-homogeneity-characterization.md). That concept carries the criterion; this note carries the proof, the primary sources, and the seven recorded limitations.

## Verdict

The object (1) and its diagonal extension (2) are owned by
[The corrected out quasi-Gini mean](../definitions/corrected-out-quasi-gini-mean.md); they
are written out here as the hypotheses of the criterion, not as a second definition.

Let \(d=\alpha-\beta\ne0\), let \(f:(0,\infty)\to(0,\infty)\), and let the external weights \(w_i\) be positive. Write

\[
\widehat G_{\alpha,\beta}^{f,\mathrm{out}}(x;w)
=\left(
\frac{\sum_iw_i x_i f(x_i)^{\alpha-1}}
     {\sum_iw_i x_i^{1-d}f(x_i)^{\alpha-1}}
\right)^{1/d}.
\tag{1}
\]

Its stated diagonal extension is

\[
\widehat G_{q,q}^{f,\mathrm{out}}(x;w)
=\exp\!\left(
\frac{\sum_iw_i x_i f(x_i)^{q-1}\log x_i}
     {\sum_iw_i x_i f(x_i)^{q-1}}
\right).
\tag{2}
\]

The exact fixed-parameter criteria are:

- for \(d\ne0\), (1) is degree-one homogeneous for all positive inputs and weights iff either \(\alpha=1\), or \(f/f(1)\) is multiplicative;
- on the diagonal, (2) is degree-one homogeneous iff either \(q=1\), or \(f/f(1)\) is multiplicative.

Here normalized multiplicativity means

\[
\frac{f(xy)}{f(1)}
=\frac{f(x)}{f(1)}\frac{f(y)}{f(1)}
\qquad(x,y>0).
\tag{3}
\]

No regularity is needed for this criterion. If \(f\) is monotone, measurable, or continuous, (3) forces

\[
f(x)=Cx^r\qquad(C>0,\ r\in\mathbb R).
\tag{4}
\]

For the project's increasing transform, \(r>0\) under strict increase and \(r\ge0\) under nondecrease. Therefore a non-power increasing \(f\) has exactly the transform-blind homogeneous locus \(\alpha=1\), including the diagonal point \((1,1)\). Homogeneity at any single non-exceptional parameter point forces the power form and then makes the entire parameter family homogeneous.

## What primary sources already establish

Aczél and Daróczy developed equality and homogeneity theory for generalized quasi-linear means with function weights: [official journal record and scan](https://publi.math.unideb.hu/paper/2901), [DOI](https://doi.org/10.5486/PMD.1963.10.1-4.24). In the standard formulation, for continuous generators \(F,G\), with \(G>0\) and \(F/G\) strictly monotone, the homogeneous Bajraktarević mappings on \((0,\infty)\) are exactly Gini mappings. Páles and Pasteczka explicitly recall this result and its standard hypotheses on pp. 1143--1144: [journal PDF](https://files.ele-math.com/articles/mia-19-84.pdf), [DOI](https://doi.org/10.7153/MIA-19-84).

This is a classification of continuous **mappings**, not uniqueness of the displayed transform \(f\), and its standard all-arity unweighted statement does not directly supply the exact arbitrary-positive-external-weight criterion below. Modern primary work on equality and homogeneity of generalized integral Bajraktarević means likewise imposes explicit regularity and nondegeneracy hypotheses: [Páles--Zakaria preprint](https://arxiv.org/abs/1710.03607), [published DOI](https://doi.org/10.1007/s10474-019-01012-6).

Weighted Gini means and their diagonal are established objects. For positive weights \(\lambda_i\), Páles and Pasteczka give

\[
G_{p,s}(x;\lambda)
=\left(\frac{\sum_i\lambda_i x_i^p}
             {\sum_i\lambda_i x_i^s}\right)^{1/(p-s)}
\quad(p\ne s),
\]

and

\[
G_{p,p}(x;\lambda)
=\exp\!\left(
\frac{\sum_i\lambda_i x_i^p\log x_i}
     {\sum_i\lambda_i x_i^p}
\right).
\]

See Example 2 of [Páles--Pasteczka, *Decision Making via Generalized Bajraktarević Means*](https://doi.org/10.1007/s10479-023-05582-1). When \(d=1\), (1) is a function-weighted Beckenbach--Gini--Lehmer mean; homogeneity of that slice is prior theory in [Matkowski--Wróbel](https://doi.org/10.3390/math8091569). That paper should not be cited as if it states the full arbitrary-\(d\), external-weight theorem.

## Exact specialization and proof

For a positive function \(h\), define

\[
P_{d,h}(x;w)=
\begin{cases}
\left(\dfrac{\sum_iw_i h(x_i)x_i^d}{\sum_iw_i h(x_i)}\right)^{1/d},
&d\ne0,\\[1ex]
\exp\!\left(\dfrac{\sum_iw_i h(x_i)\log x_i}{\sum_iw_i h(x_i)}\right),
&d=0.
\end{cases}
\tag{5}
\]

Assume the family includes two variables with both weights positive. Then \(P_{d,h}\) is degree-one homogeneous iff \(h/h(1)\) is multiplicative.

For \(d\ne0\), scale two inputs by \(c>0\), cancel \(c^d\), and cross-multiply the two weighted averages of \(x^d\) and \(y^d\). For \(x\ne y\) this yields

\[
(x^d-y^d)w_1w_2
\big(h(cx)h(y)-h(x)h(cy)\big)=0.
\]

Thus \(h(cx)/h(x)\) is independent of \(x\). The \(d=0\) proof is identical with \(\log x-\log y\) in place of \(x^d-y^d\). Hence \(h(cx)=K(c)h(x)\); setting \(x=1\) gives \(K(c)=h(c)/h(1)\), which is exactly multiplicativity. The converse is immediate.

For (1),

\[
h_{\alpha,d}(t)=t^{1-d}f(t)^{\alpha-1}.
\tag{6}
\]

Since \(t^{1-d}\) is multiplicative, (6) is multiplicative automatically at \(\alpha=1\), and otherwise iff \(f/f(1)\) is multiplicative. There are no further exceptional values of \(d\ne0\), including for negative \(d\).

If \(f(t)=Ct^r\), then

\[
\widehat G_{\alpha,\beta}^{f,\mathrm{out}}
=G_{p,s},
\qquad
p=1+r(\alpha-1),\qquad s=p-d.
\tag{7}
\]

At \(\alpha=1\), the same identity holds with \(p=1\), \(s=1-d\) even for non-power \(f\), because \(f^0=1\).

For (2), take \(d=0\) in (5) with

\[
h_q(t)=t f(t)^{q-1}.
\tag{8}
\]

This proves the diagonal criterion. For \(f(t)=Ct^r\),

\[
\widehat G_{q,q}^{f,\mathrm{out}}=G_{p,p},
\qquad p=1+r(q-1),
\tag{9}
\]

while \(q=1\) gives \(G_{1,1}\) for every positive \(f\).

Finally, if \(m=f/f(1)\) is positive and multiplicative, then

\[
m(x)=\exp(A(\log x))
\]

for an additive \(A:\mathbb R\to\mathbb R\). Without regularity, pathological non-linear additive \(A\) exist, so (3), not (4), is the exact conclusion. Monotonicity, measurability, or continuity makes \(A\) linear and yields (4).

## Fixed-parameter versus family-wide result

| Scope | Exact criterion |
| --- | --- |
| Fixed off-diagonal point | \(\alpha=1\), or \(f/f(1)\) multiplicative. |
| Fixed diagonal point | \(q=1\), or \(f/f(1)\) multiplicative. |
| Any one non-exceptional point | Forces normalized multiplicativity of \(f\). |
| Entire parameter family | Homogeneous iff \(f/f(1)\) is multiplicative; under project regularity, iff \(f(x)=Cx^r\). |
| Non-power increasing \(f\) | Homogeneous exactly on \(\alpha=1\), including diagonal \((1,1)\). |

## Limitations

1. **No novelty claim.** The exact specialization was not located verbatim, but it is an elementary corollary in a mature theory.
2. **Mapping versus generator.** Aczél--Daróczy classifies homogeneous mappings; the two-point ratio proof is what forces this project's normalized \(f\).
3. **Regularity matters.** Pathological positive multiplicative functions produce homogeneous, potentially discontinuous means outside the continuous real-parameter Gini classification.
4. **Arity matters.** The necessity proof needs two effective support points. For \(n=1\), homogeneity is automatic; zero weights can reduce effective arity.
5. **Weights are fixed under input scaling.** The claim is \(M(cx;w)=cM(x;w)\), not simultaneous rescaling or endogenizing of \(w\).
6. **The diagonal claim concerns the stated extension.** It does not independently prove the pathwise \(d\to0\) limit.
7. **Coverage is focused.** The sources establish the broad classification, weighted Gini formulas, and B--G--L slice; they are not an exhaustive novelty search for the transform-coupled SmartDCA family.

## Primary sources

1. J. Aczél and Z. Daróczy, “Über verallgemeinerte quasilineare Mittelwerte, die mit Gewichtsfunktionen gebildet sind,” *Publicationes Mathematicae Debrecen* 10 (1963), 171--190. [Official record/full scan](https://publi.math.unideb.hu/paper/2901); [DOI](https://doi.org/10.5486/PMD.1963.10.1-4.24).
2. Z. Páles and P. Pasteczka, “Characterization of the Hardy Property of Means and the Best Hardy Constants,” *Mathematical Inequalities & Applications* 19 (2016), 1141--1158. [Journal PDF](https://files.ele-math.com/articles/mia-19-84.pdf); [DOI](https://doi.org/10.7153/MIA-19-84).
3. Z. Páles and A. Zakaria, “Equality and Homogeneity of Generalized Integral Means,” *Acta Mathematica Hungarica* 160 (2020), 412--443. [Preprint](https://arxiv.org/abs/1710.03607); [DOI](https://doi.org/10.1007/s10474-019-01012-6).
4. Z. Páles and P. Pasteczka, “Decision Making via Generalized Bajraktarević Means,” *Annals of Operations Research* 332 (2024), 461--480. [DOI/open article](https://doi.org/10.1007/s10479-023-05582-1).
5. J. Matkowski and M. Wróbel, “On the Beckenbach--Gini--Lehmer Means and Means Mappings,” *Mathematics* 8 (2020), 1569. [DOI/open article](https://doi.org/10.3390/math8091569).
