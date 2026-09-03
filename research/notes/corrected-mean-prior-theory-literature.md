# Corrected-mean prior-theory literature synthesis

Ticket: [Position the corrected mean within prior mean
theory](../../.scratch/smartdca/efforts/thesis-manuscript-assembly/issues/04-position-corrected-mean-prior-theory.md)

Project authorities: [source
summary](../../references/summaries/smartdca-superiority-source-paper.md),
[source-functional audit](source-out-quasi-gini-audit.md), [canonical
source-functional
classification](../theorems/source-out-functional-mean-classification.md),
[canonical corrected
definition](../definitions/corrected-out-quasi-gini-mean.md), [prior-theory
technical note](prior-theory-corrected-out-quasi-gini.md), and [canonical
homogeneity
characterization](../theorems/corrected-mean-homogeneity-characterization.md).

Research date: 2026-09-04

## Bottom line

The source paper's Appendix B, Equation (70), is safely called the **out
quasi-Gini functional** until meanhood has been established. The paper calls
the expression a mean but does not prove reflexivity, internality, continuity,
homogeneity, coordinatewise monotonicity, or a diagonal extension.[^calvet]
The project's exact classification, not prior literature, proves that this
unmodified functional is a mean exactly when the parameter gap is one or the
transform is the identity.[^source-classification]

The adopted numerator-preserving correction is not a new general mean class.
Off the diagonal it is exactly a weighted Bajraktarević mean. Its
power-transform cases are classical weighted Gini means, its
parameter-gap-one slice has the weighted Beckenbach--Gini--Lehmer form, power
function weights on that slice give weighted Lehmer means, and its diagonal is
a function-weighted geometric Bajraktarević mean. Those family identifications
belong to prior theory; this project owns the repair choice, the exact
classification of the source functional, and the transform-coupled
homogeneity specialization.

## Search protocol and limits

The review began from the repository map in [README](../../README.md), then
followed only the domain and evidence surfaces reached by the ticket:
[CONTEXT](../../CONTEXT.md), the retained source-paper summary and PDF, the
corrected definition, the source-functional and homogeneity theorems, their
detailed notes, the existing bibliography, and the deterministic homogeneity
check. The fingerprinted source snapshot was read directly at Appendix B,
Equations (54), (55), and (70), and at the conclusion's forward-looking
quasi-Gini statement.

External searching was restricted to primary mathematical material: original
journal records or scans, publisher versions, open journal PDFs, and author or
journal preprints. Exact formulas were checked algebraically against the
corrected construction rather than assigned to a family by name resemblance.
The directly inspected modern papers were:

- Páles and Zakaria, *Results in Mathematics* 75 (2020), pp. 2--3, for the
  weighted $A_{\varphi,f}$ and symmetric $B_{g,f}$ definitions and their
  hypotheses;[^pales-zakaria]
- Páles and Pasteczka, *Journal of Inequalities and Applications* 2018:99,
  Sections 4.3--4.4, especially Equation (4.2), for weighted quasi-arithmetic
  and weighted Gini means;[^kedlaya]
- Páles and Pasteczka, *Annals of Operations Research* 332 (2024), Theorem 3,
  Equations (3.3)--(3.6), Example 2, and Section 7.2, for weighted
  Bajraktarević and Gini formulas and the classical comparison and
  coordinatewise-monotonicity regions;[^decision]
- Matkowski and Wróbel, *Mathematics* 8 (2020), pp. 1--4 and Section 7,
  especially Theorem 7, for modern Beckenbach--Gini--Lehmer terminology and
  the arithmetic-generator form;[^bgl]
- Páles and Pasteczka, *Mathematical Inequalities & Applications* 19 (2016),
  pp. 1143--1144, for the unweighted Bajraktarević definition and the explicit
  recall of Aczél--Daróczy's homogeneous-mapping classification;[^hardy]
- Chu and Zhao, *Journal of Inequalities and Applications* 2015:396,
  Example 1.2(5), p. 2, for an explicit modern primary-paper convention for
  the Lehmer ratio.[^chu-zhao]

The search is targeted and **not exhaustive**. It does not cover every
language, database, equality representation, or application of these mature
mean families. The following access limitations are material:

- the previously recorded URL for Gini's 1938 *Metron* scan did not resolve
  during this review, so the original bibliographic record was cross-checked
  against later primary papers that reproduce the formula and cite Gini;
- the publisher records for Lehmer 1971 and Beckenbach 1950 were accessible,
  but their full text was not; the displayed formulas below therefore also
  rest on inspected open modern primary papers;
- no full scan of Bajraktarević 1958 was located; its bibliographic identity
  and priority statement were checked against the journal record and the
  explicit retrospective statement and definition in Páles--Zakaria 2020;
- the official Aczél--Daróczy 1963 scan was retrieved but is image-only; the
  theorem used here was independently checked in the explicit primary-paper
  restatement on p. 1143 of Páles--Pasteczka 2016.

These limits are source gaps, not invitations to infer originality. This
search **does not establish novelty** for the transform coupling or the
SmartDCA application.

## Primary-source coverage

### Source functional and the correction seam

With $\alpha=\rho+1$, $\beta=\gamma$, and
$d=\alpha-\beta\ne0$, the source paper's Equation (70) is

\[
Q_{\alpha,\beta}^{f}(x)
=\left(
\frac{\sum_i x_i f(x_i)^{\alpha-1}}
     {\sum_i f(x_i)^\beta}
\right)^{1/d}.
\]

The source introduces it "for the sake of completeness," calls it a
quasi-Gini mean, and says it becomes its quasi-Lehmer construction when
$\rho=\gamma$, equivalently $d=1$ (Appendix B, PDF p. 12, Equation
(70)).[^calvet] Equation (54) on PDF p. 11 supplies that out quasi-Lehmer
form. The conclusion on PDF p. 8 describes future strategies based on the
quasi-Gini generalization, but the paper supplies no mean-property proof or
diagonal definition.

For a constant vector, the source expression is

\[
Q_{\alpha,\beta}^{f}(c,\ldots,c)
=c^{1/d}f(c)^{(d-1)/d}.
\]

The project's [canonical
theorem](../theorems/source-out-functional-mean-classification.md) therefore
classifies the source object as a mean exactly when $d=1$ or
$f=\mathrm{id}$, and it proves that a global finite diagonal extension exists
only in the identity case.[^source-audit] This is a **classification of the
source functional**, not a theorem found in or attributed to the source
paper. Until that classification applies, manuscript prose should retain the
word "functional."

### Generalized, Gini, Lehmer, and Beckenbach--Gini--Lehmer roots

"Generalized mean" is only an umbrella description here. The primary sources
support several related but non-interchangeable families:

1. Páles--Pasteczka 2018, Section 4.3, places weighted quasi-arithmetic means
   in the Kolmogorov--Nagumo lineage and defines

   \[
   A_h(x;w)=h^{-1}\!\left(\frac{\sum_iw_i h(x_i)}{\sum_iw_i}\right).
   \]

   This is background vocabulary, not the narrowest classification of the
   corrected formula.[^kedlaya]
2. The weighted Gini family is

   \[
   G_{p,q}(x;w)=
   \left(\frac{\sum_iw_ix_i^p}{\sum_iw_ix_i^q}\right)^{1/(p-q)}
   \quad(p\ne q),
   \]

   with diagonal

   \[
   G_{p,p}(x;w)=
   \exp\!\left(\frac{\sum_iw_ix_i^p\log x_i}
                     {\sum_iw_ix_i^p}\right).
   \]

   Páles--Pasteczka 2016, Equation (1.7), and Páles--Pasteczka 2018,
   Equation (4.2), reproduce these branches and attribute the family to
   Gini's 1938 paper.[^hardy][^kedlaya]
3. One common modern Lehmer convention is

   \[
   L_s(x;w)=\frac{\sum_iw_i x_i^{s+1}}{\sum_iw_i x_i^s}.
   \]

   Chu--Zhao 2015 displays the equal-weight two-variable formula as
   $L_s(x,y)=(x^{s+1}+y^{s+1})/(x^s+y^s)$ in Example 1.2(5).[^chu-zhao]
   The source paper instead labels
   $\sum_i x_i^a/\sum_i x_i^{a-1}$ as $L_a$ in Equation (55), so its
   index is shifted by one from the Chu--Zhao convention. Claims should
   display the formula or declare the convention instead of relying on the
   subscript alone. Lehmer 1971 supplies the historical bibliographic
   lineage; the open modern source supplies the directly inspected displayed
   ratio.[^lehmer]
4. Matkowski--Wróbel 2020 calls

   \[
   M_{[h]}(x_1,\ldots,x_n)
   =\frac{\sum_i x_i h(x_i)}{\sum_i h(x_i)},\qquad h>0,
   \]

   the Beckenbach--Gini--Lehmer form (Introduction and Remark 1).[^bgl]
   Their directly studied formula has equal external weights. Adding fixed
   external weights is the standard weighted extension, but their mapping
   theorems must not be cited as if they prove every arbitrary-$d$,
   externally weighted statement in this project.

### Exact weighted Bajraktarević identification

For the corrected mean, let

\[
R_\alpha(t)=t f(t)^{\alpha-1},
\qquad \varphi_d(t)=t^{-d}.
\]

The weighted Bajraktarević mean in Páles--Zakaria 2020 is

\[
A_{\varphi,R}(x;w)
=\varphi^{-1}\!\left(
\frac{\sum_iw_iR(x_i)\varphi(x_i)}{\sum_iw_iR(x_i)}
\right),
\]

where $\varphi$ is continuous and strictly monotone and $R$ is positive;
their weight vectors may be nonnegative with positive total
weight.[^pales-zakaria] Here $\varphi_d$ satisfies the generator conditions
for every $d\ne0$, and $R_\alpha>0$ whenever $f>0$. Direct substitution gives

\[
A_{\varphi_d,R_\alpha}(x;w)
=\left(
\frac{\sum_i w_i x_i f(x_i)^{\alpha-1}}
     {\sum_i w_i x_i^{1-d}f(x_i)^{\alpha-1}}
\right)^{1/d}
=\widehat G_{\alpha,\beta}^{f,\mathrm{out}}(x;w).
\]

Thus the identification is exact for every positive finite transform, not an
analogy and not a new mean-family definition. It also gives the pointwise
power-mean representation

\[
\widehat G_{\alpha,\beta}^{f,\mathrm{out}}(x;w)
=P_{-d}\bigl(x;\lambda^{\mathrm{eff}}\bigr),
\qquad
\lambda_i^{\mathrm{eff}}=w_i x_i f(x_i)^{\alpha-1}>0,
\]

which proves internality but does not make the corrected mapping an ordinary
fixed-weight power mean: the effective weights depend on the inputs.

The exact specializations are:

- if $f(t)=Ct^r$, then
  $\widehat G_{\alpha,\beta}^{f,\mathrm{out}}=G_{p,q}$ with
  $p=1+r(\alpha-1)$ and $q=p-d$; for $f=\mathrm{id}$, this is
  $G_{\alpha,\beta}$;
- if $d=1$, then

  \[
  \widehat G_{\alpha,\alpha-1}^{f,\mathrm{out}}(x;w)
  =\frac{\sum_iw_i x_i f(x_i)^{\alpha-1}}
         {\sum_iw_i f(x_i)^{\alpha-1}},
  \]

  the weighted Beckenbach--Gini--Lehmer form and exactly the source-aligned
  out quasi-Lehmer slice; if $f(t)^{\alpha-1}=t^s$, it is the weighted Lehmer
  mean $L_s$ under the convention displayed above;
- on $\alpha=\beta=q$, the adopted extension is

  \[
  \widehat G_{q,q}^{f,\mathrm{out}}(x;w)
  =\exp\!\left(
    \frac{\sum_iw_i x_i f(x_i)^{q-1}\log x_i}
         {\sum_iw_i x_i f(x_i)^{q-1}}
  \right)
  =A_{\log,R_q}(x;w).
  \]

  For fixed finite $x,w$ and positive finite values $f(x_i)$, this is the
  $d\to0$ limit of the corrected family; no input differentiability of $f$
  is needed.[^prior-theory]

## Property boundaries

The following table separates properties that are often conflated. Its
project-specific rows are governed by the linked canonical definition and
theorems, not inferred from family names alone.

| Property | Safe claim region | Boundary that must remain explicit |
| --- | --- | --- |
| Meanhood, reflexivity, and internality | The corrected off-diagonal formula is a Bajraktarević mean for every positive finite $f$ and positive external weights; its stated diagonal is also a function-weighted geometric mean. | Meanhood alone supplies neither input continuity, homogeneity, nor coordinatewise monotonicity. |
| Continuity in the parameters | For a fixed finite positive input and fixed positive weights, the corrected branches are continuous through $d=0$ for every positive finite $f$, using the finite-vector power-mean limit. | This is not continuity as the input vector varies. |
| Continuity in the inputs | Continuous $f$ is a clean sufficient condition. The transform-independent points remain continuous even if $f$ is not. | Positivity or monotonicity of $f$ alone permits jumps. No necessity claim is made because equivalent generator pairs can represent the same mapping. |
| Coordinatewise monotonicity | In the power-transform case, write the mapping as $G_{p,q}$; the classical weighted Gini criterion is exactly $pq\le0$ (Páles--Pasteczka 2024, Section 7.2, p. 478). | This criterion does not transfer to arbitrary $f$. It fails, for example, at the classical $G_{2,1}$, so even a valid mean need not be coordinatewise nondecreasing.[^source-audit] |
| Parameter monotonicity | At fixed $\alpha$, the effective weights are fixed and power-mean monotonicity shows the corrected value is nondecreasing in $\beta$. On $d=1$, the source's Theorem 3 gives its separate quasi-Lehmer parameter result under a positive increasing transform.[^calvet] | Changing $\alpha$ generally changes both the power order and the effective weights; no blanket two-parameter ordering follows. Parameter monotonicity is not coordinatewise monotonicity. |
| Degree-one homogeneity | Off diagonal, with fixed external weights and at least two effective coordinates, homogeneity holds iff $\alpha=1$ or $f/f(1)$ is multiplicative. On the diagonal, replace the exception by $q=1$. Under monotonicity, measurability, or continuity, normalized multiplicativity forces $f(t)=Ct^r$.[^homogeneity] | Without regularity, the exact condition is multiplicativity, not a power law. One effective coordinate is degenerate, and the weights are held fixed under input scaling. |
| Transform independence | Off diagonal, the universal transform-blind slice is $\alpha=1$, because $f^{\alpha-1}=1$; on the diagonal the corresponding point is $q=1$. | Particular transforms, constant input vectors, or one-point supports can coincide elsewhere. The family-wide statement should not be enlarged from such accidental equalities. |

The homogeneity placement has a particularly firm prior-theory boundary.
Aczél--Daróczy classified continuous homogeneous Bajraktarević mappings on the
positive half-line as Gini mappings; Páles--Pasteczka 2016 recalls that result
explicitly on p. 1143.[^aczel-daroczy][^hardy] The project's theorem is a
narrower transform-coupled, arbitrary-positive-external-weight
specialization: its two-point argument identifies exactly when the displayed
$f$ produces a homogeneous mapping.[^homogeneity] For a power transform, the
whole family is already a reparameterized classical Gini family. For a
non-power increasing transform, only the transform-blind $\alpha=1$ locus is
homogeneous. Therefore the thesis cannot claim scale invariance and transform
novelty simultaneously for this mean.

## Claim-to-evidence map

| Claim identifier | Manuscript-safe content | Repository authority | Intended bibliography keys and direct locator | Claim limit |
| --- | --- | --- | --- | --- |
| `claim-lit-mean-source-functional` | The source introduces Equation (70) as a quasi-Gini mean without a mean-property or diagonal proof; use **out quasi-Gini functional** until the project classification applies. | [Source summary](../../references/summaries/smartdca-superiority-source-paper.md), [audit](source-out-quasi-gini-audit.md), and [classification](../theorems/source-out-functional-mean-classification.md). | `calvet2023smartdca`: Appendix B, PDF p. 12, Equation (70); related Equation (54), PDF p. 11. | Attribute the formula and omissions to the source; attribute the iff classification only to the project. |
| `claim-lit-mean-generalized-roots` | Gini, Lehmer, and Beckenbach--Gini--Lehmer are established related families with convention-sensitive names. | This note and [prior-theory note](prior-theory-corrected-out-quasi-gini.md). | `gini1938`; `lehmer1971`; `chuzhao2015`, Example 1.2(5), p. 2; `beckenbach1950`; `matkowskiwrobel2020`, pp. 1--4. | Use "generalized mean" only as an umbrella; display the Lehmer exponents or state the index convention. |
| `claim-lit-mean-family-identification` | The correction is exactly $A_{t^{-d},\,t f^{\alpha-1}}$; power transforms give weighted Gini, $d=1$ gives the weighted B--G--L/source-aligned quasi-Lehmer form, and the diagonal is function-weighted geometric. | [Canonical definition](../definitions/corrected-out-quasi-gini-mean.md) and [prior-theory note](prior-theory-corrected-out-quasi-gini.md). | `bajraktarevic1958`; `paleszakaria2020`, pp. 2--3; `palespasteczka2018`, Section 4.4; `palespasteczka2024`, Theorem 3 and Example 2; `matkowskiwrobel2020`; `lehmer1971`; `chuzhao2015`. | Exact known-family identification; no new general mean-class claim. |
| `claim-lit-mean-property-boundaries` | State input continuity, coordinatewise monotonicity, homogeneity, parameter continuity, and transform independence only in the regions tabulated above. | [Homogeneity theorem](../theorems/corrected-mean-homogeneity-characterization.md), [homogeneity evidence](ticket-07-homogeneity-primary-sources.md), and [executable check](../../reproducibility/checks/check_corrected_out_quasi_gini_homogeneity.py). | `aczeldaroczy1963`; `palespasteczka2016`, pp. 1143--1144; `palespasteczka2024`, Section 7.2. | General increasing $f$ does not import the classical Gini property regions. |
| `claim-lit-mean-contribution-boundary` | Prior theory owns the known families and broad property theory; the project owns the repair choice (**correction**), the iff result for the unmodified source (**classification**), and the exact transform condition for this specialization (**characterization**). | [Corrected definition](../definitions/corrected-out-quasi-gini-mean.md), [source classification](../theorems/source-out-functional-mean-classification.md), and [homogeneity characterization](../theorems/corrected-mean-homogeneity-characterization.md). | `calvet2023smartdca`; `paleszakaria2020`; `aczeldaroczy1963`. | The targeted search does not establish priority for the transform coupling or application. |

## Citation and novelty verdict

**Qualified pass for manuscript use.** Every family attribution needed by the
proposed section has an intended bibliography key and an exact formula or
locator in an inspected source or an explicitly declared early-source record.
The early-source access gaps above must remain visible in the evidence layer;
the open modern primary papers are what make the displayed formulas directly
verifiable.

The novelty accounting is:

- **Prior theory:** quasi-arithmetic, Gini, Lehmer,
  Beckenbach--Gini--Lehmer, Bajraktarević, weighted constructions, and broad
  comparison and homogeneous-mapping theory.
- **Correction:** the repository's numerator-preserving replacement of the
  source denominator and its parameter-continuous diagonal branch.
- **Classification:** the repository's exact meanhood and diagonal result for
  the unmodified source functional.
- **Characterization:** the repository's exact normalized-multiplicativity
  condition for homogeneity of this transform-coupled, externally weighted
  specialization.

The defensible synthesis is therefore: the corrected construction is a known
weighted Bajraktarević mean selected to repair the source expression, and the
project proves bounded statements about that source and specialization. The
search found no basis for calling the corrected formula a new general mean
class, and absence of the exact cross-parameter coupling from this bounded
source set is not evidence of novelty.

## Independent citation and novelty review

On 2026-09-04, an independent reviewer who had not drafted the note or
manuscript compared the ticket, Chapter 2 section, claim register,
bibliography, canonical project authorities, and directly accessible primary
sources. The reviewer rechecked the source Equation (54)/(70) locators, the
weighted Bajraktarević substitution, Gini/Lehmer/B--G--L special cases, the
$pq\le0$ classical monotonicity region, the continuity distinctions, the
homogeneity locus, and the transform-independent slice.

The first pass found one medium traceability defect: citations existed in the
chapter but not beside the contribution-boundary claim itself. The manuscript
now cites that summary locally, the audit checks citations within each labelled
subsection instead of anywhere in the thesis, and a negative test preserves
that behavior. The same reviewer then reported the finding resolved, no new
blocker, and a **pass** for citation and novelty positioning. The early-source
access limits above remain part of that accepted verdict.

## Primary references and intended keys

- `calvet2023smartdca`: E. Calvet, L. Herranz-Celotti, and K. Valimamode,
  *SmartDCA superiority*, arXiv:2308.05200v1 (2023), retained [source
  PDF](../../references/2308.05200v1.pdf).[^calvet]
- `gini1938`: C. Gini, “Di una formula comprensiva delle medie,” *Metron* 13
  (1938), 3--22.[^gini]
- `lehmer1971`: D. H. Lehmer, “On the Compounding of Certain Means,”
  *Journal of Mathematical Analysis and Applications* 36(1) (1971),
  183--200.[^lehmer]
- `chuzhao2015`: Y.-M. Chu and T.-H. Zhao, “Convexity and Concavity of the
  Complete Elliptic Integrals with Respect to Lehmer Mean,” *Journal of
  Inequalities and Applications* 2015:396 (2015).[^chu-zhao]
- `beckenbach1950`: E. F. Beckenbach, “A Class of Mean Value Functions,”
  *American Mathematical Monthly* 57(1) (1950), 1--6.[^beckenbach]
- `matkowskiwrobel2020`: J. Matkowski and M. Wróbel, “On the
  Beckenbach--Gini--Lehmer Means and Means Mappings,” *Mathematics* 8(9)
  (2020), 1569.[^bgl]
- `bajraktarevic1958`: M. Bajraktarević, “Sur une équation fonctionnelle aux
  valeurs moyennes,” *Glasnik Mat.-Fiz. Astronom. Društvo Mat. Fiz.
  Hrvatske*, Ser. II 13 (1958), 243--248.[^bajraktarevic]
- `paleszakaria2020`: Z. Páles and A. Zakaria, “On the Equality of
  Bajraktarević Means to Quasi-Arithmetic Means,” *Results in Mathematics*
  75 (2020), article 19.[^pales-zakaria]
- `palespasteczka2018`: Z. Páles and P. Pasteczka, “On Kedlaya-Type
  Inequalities for Weighted Means,” *Journal of Inequalities and
  Applications* 2018:99.[^kedlaya]
- `palespasteczka2024`: Z. Páles and P. Pasteczka, “Decision Making via
  Generalized Bajraktarević Means,” *Annals of Operations Research* 332
  (2024), 461--480 (online first 2023).[^decision]
- `aczeldaroczy1963`: J. Aczél and Z. Daróczy, “Über verallgemeinerte
  quasilineare Mittelwerte, die mit Gewichtsfunktionen gebildet sind,”
  *Publicationes Mathematicae Debrecen* 10 (1963),
  171--190.[^aczel-daroczy]
- `palespasteczka2016`: Z. Páles and P. Pasteczka, “Characterization of the
  Hardy Property of Means and the Best Hardy Constants,” *Mathematical
  Inequalities & Applications* 19(4) (2016), 1141--1158.[^hardy]

[^calvet]: E. Calvet, L. Herranz-Celotti, and K. Valimamode, [*SmartDCA superiority*](https://arxiv.org/abs/2308.05200v1), arXiv:2308.05200v1 (2023), especially Appendix B, Equations (54), (55), and (70), PDF pp. 11--12.
[^source-classification]: [Exact mean classification of the source out quasi-Gini functional](../theorems/source-out-functional-mean-classification.md).
[^source-audit]: [Audit of the source out quasi-Gini functional](source-out-quasi-gini-audit.md).
[^prior-theory]: [Prior theory for the proposed corrected out quasi-Gini normalization](prior-theory-corrected-out-quasi-gini.md), especially Equations (3), (5), (7), and (10).
[^homogeneity]: [Primary-source note: homogeneity of the canonical corrected out quasi-Gini mean](ticket-07-homogeneity-primary-sources.md), especially the fixed-parameter table and limitations.
[^gini]: C. Gini, “Di una formula comprensiva delle medie,” *Metron* 13 (1938), 3--22; formula cross-checks in [Páles--Pasteczka 2016](https://doi.org/10.7153/MIA-19-84), Equation (1.7), and [Páles--Pasteczka 2018](https://doi.org/10.1186/s13660-018-1685-z), Equation (4.2).
[^lehmer]: D. H. Lehmer, [“On the Compounding of Certain Means”](https://doi.org/10.1016/0022-247X(71)90029-1), *Journal of Mathematical Analysis and Applications* 36(1) (1971), 183--200. The publisher record was inspected; the displayed modern ratio was checked independently in Chu--Zhao 2015.
[^chu-zhao]: Y.-M. Chu and T.-H. Zhao, [“Convexity and Concavity of the Complete Elliptic Integrals with Respect to Lehmer Mean”](https://doi.org/10.1186/s13660-015-0926-7), *Journal of Inequalities and Applications* 2015:396, Example 1.2(5), p. 2.
[^beckenbach]: E. F. Beckenbach, [“A Class of Mean Value Functions”](https://doi.org/10.1080/00029890.1950.11999469), *American Mathematical Monthly* 57(1) (1950), 1--6; formula cross-check in Matkowski--Wróbel 2020, pp. 1--4.
[^bgl]: J. Matkowski and M. Wróbel, [“On the Beckenbach--Gini--Lehmer Means and Means Mappings”](https://doi.org/10.3390/math8091569), *Mathematics* 8(9) (2020), 1569, especially the Introduction, Remark 1, and Theorem 7.
[^bajraktarevic]: M. Bajraktarević, “Sur une équation fonctionnelle aux valeurs moyennes,” *Glasnik Mat.-Fiz. Astronom. Društvo Mat. Fiz. Hrvatske*, Ser. II 13 (1958), 243--248; bibliographic record and retrospective definition checked in Páles--Zakaria 2020, pp. 2--3.
[^pales-zakaria]: Z. Páles and A. Zakaria, [“On the Equality of Bajraktarević Means to Quasi-Arithmetic Means”](https://doi.org/10.1007/s00025-019-1141-5), *Results in Mathematics* 75 (2020), article 19, pp. 2--3.
[^kedlaya]: Z. Páles and P. Pasteczka, [“On Kedlaya-Type Inequalities for Weighted Means”](https://doi.org/10.1186/s13660-018-1685-z), *Journal of Inequalities and Applications* 2018:99, Sections 4.3--4.4 and Equation (4.2).
[^decision]: Z. Páles and P. Pasteczka, [“Decision Making via Generalized Bajraktarević Means”](https://doi.org/10.1007/s10479-023-05582-1), *Annals of Operations Research* 332 (2024), 461--480, Theorem 3, Example 2, and Section 7.2.
[^aczel-daroczy]: J. Aczél and Z. Daróczy, [“Über verallgemeinerte quasilineare Mittelwerte, die mit Gewichtsfunktionen gebildet sind”](https://doi.org/10.5486/PMD.1963.10.1-4.24), *Publicationes Mathematicae Debrecen* 10 (1963), 171--190; [official record and scan](https://publi.math.unideb.hu/paper/2901).
[^hardy]: Z. Páles and P. Pasteczka, [“Characterization of the Hardy Property of Means and the Best Hardy Constants”](https://doi.org/10.7153/MIA-19-84), *Mathematical Inequalities & Applications* 19(4) (2016), 1141--1158, especially pp. 1143--1144.
