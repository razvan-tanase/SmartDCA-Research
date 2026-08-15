# Prior theory for the proposed corrected out quasi-Gini normalization

Research date: 2026-08-15

## Bottom line

For positive inputs \(x_i\), positive external weights \(w_i\), a positive function
\(f\), and \(d=\alpha-\beta\ne0\), consider

\[
M_{\alpha,\beta}^{f}(x;w)
=
\left(
\frac{\sum_i w_i x_i f(x_i)^{\alpha-1}}
     {\sum_i w_i x_i^{1-d}f(x_i)^{\alpha-1}}
\right)^{1/d}.
\tag{1}
\]

Equation (1) is **exactly a weighted Bajraktarević mean**, not merely a formula
resembling one. Indeed, set

\[
R_\alpha(t):=t f(t)^{\alpha-1}>0,
\qquad
\varphi_d(t):=t^{-d}.
\]

The weighted Bajraktarević form introduced in the literature is

\[
A_{\varphi,R}(x,w)
=
\varphi^{-1}\!\left(
\frac{\sum_i w_iR(x_i)\varphi(x_i)}{\sum_i w_iR(x_i)}
\right).
\tag{2}
\]

Since \(\varphi_d^{-1}(u)=u^{-1/d}\), substitution in (2) gives

\[
A_{\varphi_d,R_\alpha}(x,w)
=
\left(
\frac{\sum_i w_i x_i^{1-d}f(x_i)^{\alpha-1}}
     {\sum_i w_i x_i f(x_i)^{\alpha-1}}
\right)^{-1/d}
=M_{\alpha,\beta}^{f}(x;w).
\tag{3}
\]

This is precisely the function-weighted quasi-arithmetic definition recalled by
Páles and Zakaria: the generator must be continuous and strictly monotone, while
the weighting function need only be positive. Here \(\varphi_d(t)=t^{-d}\) meets
those generator hypotheses for every \(d\ne0\), and \(R_\alpha>0\) follows from
\(f>0\). Their formulation also allows nonnegative external weights with positive
total weight; the present assumption \(w_i>0\) is stronger
([Páles--Zakaria 2020, introduction and Eqs. defining \(A_{\varphi,f}\) and
\(B_{g,f}\)](https://doi.org/10.1007/s00025-019-1141-5)).

Consequently, meanhood, reflexivity, and internality of (1) are already consequences
of the established Bajraktarević framework. A claim that the normalized formula
itself is a new class of means would therefore be unsafe.

## Scope, method, and search limits

The search was restricted to primary mathematical sources: original papers,
publisher versions, author preprints, and journal/archive scans. It covered the
classical two-parameter Gini family, weighted Gini and power means, Beckenbach--Gini--Lehmer
means, Bajraktarević means, and primary work on equality, comparison, homogeneity,
and mean-type mappings. The exact candidate was checked algebraically against the
definitions, rather than classified by name matching.

This was a targeted, not exhaustive, literature search. In particular:

- some early papers are not fully text-searchable; where a historical scan could
  not be inspected reliably, a later primary research paper's explicit definition
  and attribution were used;
- the search does not establish that no paper studies the exact cross-parameter
  coupling \(R_\alpha(t)=t f(t)^{\alpha-1}\) as a family;
- absence from the sources below is not evidence of novelty, especially for older
  German, French, Italian, Croatian, Hungarian, or Serbian literature;
- no novelty conclusion about the SmartDCA application can be drawn without a
  separate finance/portfolio-strategy search.

## Two exact representations and their consequences

### 1. Standard Bajraktarević representation

Equation (3) is the cleanest identification. Equivalently, using the symmetric
two-generator notation requested in the ticket, define

\[
F(t)=t f(t)^{\alpha-1},
\qquad
H(t)=t^{1-d}f(t)^{\alpha-1}.
\]

Then \(F/H=t^d\), and

\[
M_{\alpha,\beta}^{f}(x;w)
=
\left(\frac{F}{H}\right)^{-1}
\left(\frac{\sum_iw_iF(x_i)}{\sum_iw_iH(x_i)}\right).
\tag{4}
\]

This is exactly the weighted form
\(B_{F,H}\). Standard definitions require \(H>0\) and \(F/H\) continuous and
strictly monotone; all hold here for \(d\ne0\) and positive \(f\), even if \(f\)
itself is discontinuous. Páles and Zakaria also note the generator-pair symmetry
\(B_{F,H}=B_{H,F}\) when both functions are nonzero
([Páles--Zakaria 2020](https://doi.org/10.1007/s00025-019-1141-5)).

This exact identification is stronger than the narrower Beckenbach--Gini--Lehmer
analogy. In current mean-theory usage, the full class in (2)--(4) is normally called
the **Bajraktarević class**. Matkowski and Wróbel use
“Beckenbach--Gini--Lehmer” for the arithmetic-generator subclass

\[
M_{[q]}(x,y)=\frac{xq(x)+yq(y)}{q(x)+q(y)},
\]

not for every power-generator case
([Matkowski--Wróbel 2020, introduction](https://doi.org/10.3390/math8091569)).

### 2. Pointwise weighted-power-mean representation

For fixed \(x\) and \(\alpha\), let

\[
\lambda_i^{\rm eff}:=w_iR_\alpha(x_i)
=w_ix_if(x_i)^{\alpha-1}>0.
\]

Then

\[
M_{\alpha,\beta}^{f}(x;w)
=P_{-d}(x;\lambda^{\rm eff}),
\tag{5}
\]

where \(P_r(x;\lambda)=(\sum_i\lambda_ix_i^r/\sum_i\lambda_i)^{1/r}\)
and \(P_0\) is the weighted geometric mean. This proves internality immediately.
It also gives an exact fixed-\(\alpha\) parameter comparison:

\[
d_1<d_2
\quad\Longrightarrow\quad
M_{\alpha,\alpha-d_1}^{f}(x;w)
\ge M_{\alpha,\alpha-d_2}^{f}(x;w),
\tag{6}
\]

with strict inequality for a nonconstant input vector. This is just the classical
power-mean monotonicity in the order \(-d\). Equivalently, for fixed \(\alpha\),
the candidate is nondecreasing in \(\beta\).

There is an important qualification: as a mapping of \(x\), the effective weights
in (5) depend on the inputs. Thus (1) is not an ordinary fixed-weight power mean,
and coordinatewise monotonicity in the inputs does not follow from power-mean
theory. Function-weighted quasi-arithmetic means need not be nondecreasing in
their entries in general; this issue is treated as a separate property in the
weighting-function literature and in the deviation-mean formulation
([Páles--Pasteczka 2018, Sections 4.1--4.5](https://doi.org/10.1186/s13660-018-1685-z)).

## Exact special cases

### Classical weighted Gini family

If \(f(t)=t^r\), define

\[
p:=1+r(\alpha-1),
\qquad q:=p-d.
\]

Then (1) becomes exactly

\[
G_{p,q}(x;w)
=
\left(\frac{\sum_iw_ix_i^p}{\sum_iw_ix_i^q}\right)^{1/(p-q)}.
\tag{7}
\]

The identity transform is the subcase \(r=1\), for which \((p,q)=(\alpha,\beta)\).
Thus all classical weighted-Gini results apply exactly for power transforms, not for
an arbitrary transform merely because the notation has two parameters.

The modern primary-source definition includes arbitrary nonnegative weights and the
diagonal value

\[
G_{p,p}(x;w)
=
\exp\!\left(
\frac{\sum_iw_ix_i^p\log x_i}{\sum_iw_ix_i^p}
\right),
\tag{8}
\]

and records \(G_{p,0}=P_p\), symmetry in \(p,q\), and a concavity region
([Páles--Pasteczka 2018, Eq. (4.2) and Section 4.4](https://doi.org/10.1186/s13660-018-1685-z)).
The family originates with Gini's 1938 paper
([journal scan, *Metron* 13(2), 3--22](https://lipari.istat.it/digibib/Metron/MetronV13N2_1938.pdf)).

For fixed external weights, \(\log G_{p,q}\) is the secant slope of the convex
log-moment function \(s\mapsto\log\sum_iw_ix_i^s\); hence the classical Gini mean
is nondecreasing in each parameter. More precisely, the weighted comparison
theorem says
\[
G_{p,q}\le G_{r,s}
\quad\Longleftrightarrow\quad
\min(p,q)\le\min(r,s)\ \text{and}\ \max(p,q)\le\max(r,s).
\]
Páles and Pasteczka recall this criterion, the weighted off-diagonal formula,
the diagonal formula, and the fact that \(G_{p,q}\) is coordinatewise monotone
as a mean exactly when \(pq\le0\)
([Páles--Pasteczka 2023, Example 2 and Section 7.2](https://doi.org/10.1007/s10479-023-05582-1)).
Those statements do **not** transfer wholesale to (1) when \(\alpha\) changes,
because \(R_\alpha\) then changes too. Primary work on local/global comparison of
generalized Bajraktarević means supplies generator criteria rather than a blanket
two-parameter ordering
([Páles--Zakaria 2017](https://doi.org/10.1016/j.jmaa.2017.05.073)).

### Beckenbach--Gini--Lehmer slice

If \(d=1\), then

\[
M_{\alpha,\alpha-1}^{f}(x;w)
=
\frac{\sum_iw_ix_if(x_i)^{\alpha-1}}
     {\sum_iw_if(x_i)^{\alpha-1}},
\tag{9}
\]

which is exactly the weighted arithmetic/function-weighted
Beckenbach--Gini--Lehmer form. If its weight generator is a power, (9) is a
weighted Lehmer mean. Beckenbach's original mean-value-function paper is
[Beckenbach 1950](https://doi.org/10.1080/00029890.1950.11999469); the modern
primary paper of Matkowski and Wróbel studies this slice, its complementary means,
homogeneity, and arithmetic-invariant mean-type mappings
([Matkowski--Wróbel 2020](https://doi.org/10.3390/math8091569)). Those mapping
results do not by themselves cover the general \(d\ne1\) candidate.

### Dresher nomenclature

Dresher's 1953 moment-space paper concerns the moment-quotient inequalities whose
discrete forms use ratios of power sums
([Dresher 1953](https://doi.org/10.1215/S0012-7094-53-02026-2)), extending
Beckenbach's inequality. The identity/power-transform cases of (1) therefore sit
inside the same discrete moment-ratio structure. Modern mean-theory primary sources,
however, call (7) the **Gini mean**. It is safest to reserve “Dresher” for the
associated Beckenbach--Dresher moment inequalities unless a cited source explicitly
uses “Dresher mean” for the formula at hand.

## The diagonal \(d\to0\)

Let \(d\to0\) along any path for which \(\alpha(d)\to\tau\) and
\(\beta(d)=\alpha(d)-d\). From (5), the order \(-d\to0\) and the normalized
effective weights converge to those generated by

\[
R_\tau(t)=t f(t)^{\tau-1}.
\]

For a finite input vector, the usual power-mean limit gives

\[
\boxed{
M_{\tau,\tau}^{f}(x;w)
:=
\exp\!\left(
\frac{\sum_iw_ix_if(x_i)^{\tau-1}\log x_i}
     {\sum_iw_ix_if(x_i)^{\tau-1}}
\right).}
\tag{10}
\]

No derivative of \(f\) is needed: only its finitely many positive values at the
inputs enter. Formula (10) is itself exactly a weighted Bajraktarević mean,
\(A_{\log,R_\tau}\). With \(f(t)=t\), it reduces to the classical weighted-Gini
diagonal (8). Thus a finite, reflexive diagonal is naturally available for every
positive \(f\) under the corrected normalization.

The **specific limit calculation for the coupled family** may still be worth stating
and proving in the paper, especially because it contrasts sharply with the divergent
diagonal of the source functional. But (10) is a standard function-weighted geometric
Bajraktarević mean, so neither the value itself nor its meanhood should be presented
as a new kind of mean. I did not locate, in this targeted search, a primary paper that
states exactly the pathwise limit above with the same \((\alpha,\beta,f)\) coupling;
that is a search result, not a novelty proof.

### Direct verification checks

- **Constants.** If every input is \(c>0\), the quotient in (1) is \(c^d\),
  so \(M_{\alpha,\beta}^{f}(c,\ldots,c;w)=c\).
- **Required boundaries.** Setting \(f(t)=t\) gives the classical weighted Gini
  mean \(G_{\alpha,\beta}\). Setting \(d=1\) gives (9), the source's normalized
  out quasi-Lehmer slice.
- **Nontrivial internality check.** For \(x=(1,4)\), \(w=(2,1)\),
  \(f(t)=1+t\), \(\alpha=2\), and \(\beta=0\), formula (1) gives
  \(M=\sqrt{32/7}\approx2.13809\), which lies strictly between 1 and 4.
- **Diagonal check.** For the same \(x,w,f\) with diagonal parameter
  \(\tau=0\), (10) gives \(4^{4/9}\approx1.85175\). Direct evaluations of
  (1) at \(d=0.1,0.01,0.001\) and \(d=-0.001,-0.01,-0.1\) approach this
  value from the two sides, as predicted by the power-mean limit.

## Homogeneity, input monotonicity, and comparisons

- **Homogeneity.** Every classical Gini mean is positively homogeneous. More
  generally, Aczél and Daróczy's classification states that the homogeneous means
  in the continuous Bajraktarević class on \((0,\infty)\) are exactly Gini means
  as mappings
  ([Aczél--Daróczy 1963](https://doi.org/10.5486/PMD.1963.10.1-4.24), as recalled
  explicitly in [Páles--Pasteczka 2016, pp. 1143--1144](https://doi.org/10.7153/MIA-19-84)).
  For the candidate, \(f(t)=Ct^r\) is a direct sufficient condition, because (7)
  results; \(\alpha=1\) also removes \(f\). General positive or increasing \(f\)
  does not ensure homogeneity. The example \(f(t)=1+t\), \(\alpha=2\), \(d=1\)
  gives \(M(1,2)=8/5\) but \(M(2,4)=13/4\ne2M(1,2)\).

- **Coordinatewise monotonicity.** It is not automatic, even in the classical
  Gini subfamily. For weighted Gini means, the exact region is \(pq\le0\)
  ([Páles--Pasteczka 2023, Section 7.2](https://doi.org/10.1007/s10479-023-05582-1)).
  For \(f(t)=t\), \((\alpha,\beta)=(2,1)\), and two equal external weights, the
  candidate is \((x_1^2+x_2^2)/(x_1+x_2)\), whose derivative with respect to
  \(x_1\) at \((1,10)\) is \(-79/121\). General deviation-mean theory treats
  increasingness as an additional generator condition
  ([Páles--Pasteczka 2018, Section 4.1](https://doi.org/10.1186/s13660-018-1685-z)).

- **Parameter comparison.** Fixed-\(\alpha\) comparison in \(d\) is already
  settled by (5)--(6). Classical fixed-weight Gini parameter comparison applies
  to the power-transform cases. For general \(f\), changing \(\alpha\) changes
  both the power order and the input-dependent weights, so no general monotonicity
  claim should be imported without checking the generator criteria in the
  Bajraktarević comparison literature. Bajraktarević himself studied comparison
  of function-weighted means in 1969; modern local/global conditions are given by
  Páles and Zakaria 2017 (DOI above).

- **Continuity.** Meanhood under (2) needs only \(R_\alpha>0\), but continuity as
  a function of the entries generally needs continuity of the weighting function,
  here normally supplied by continuity of \(f\). Positivity or monotonicity of
  \(f\) alone should not be conflated with continuity.

## Source-to-coverage map

| Primary source | Exact coverage relevant here | Implication for ticket 03 | Confidence |
| --- | --- | --- | --- |
| [Gini, “Di una formula comprensiva delle medie,” *Metron* 13(2), 1938, 3--22 (scan)](https://lipari.istat.it/digibib/Metron/MetronV13N2_1938.pdf) | Origin of the two-parameter power-sum family now called Gini means. | Exact for \(f(t)=t^r\) after the parameter change in (7), including \(f=\mathrm{id}\). | High; formula cross-checked in later primary papers because the scan is not reliably searchable. |
| [Beckenbach, “A Class of Mean Value Functions,” *Amer. Math. Monthly* 57 (1950), 1--6](https://doi.org/10.1080/00029890.1950.11999469) | Function-weighted mean-value functions and the inequality later extended by Dresher. | Direct historical predecessor; exact arithmetic-generator/B--G--L slice at \(d=1\), not the best name for all \(d\). | High. |
| [Dresher, “Moment Spaces and Inequalities,” *Duke Math. J.* 20 (1953), 261--271](https://doi.org/10.1215/S0012-7094-53-02026-2) | Moment-ratio inequalities of Beckenbach--Dresher type. | Exact moment-ratio setting for power cases; supports an inequality connection, not a blanket nomenclature claim. | Medium-high; historical scope is clear, but naming varies. |
| M. Bajraktarević, “Sur une équation fonctionnelle aux valeurs moyennes,” *Glasnik Mat.-Fiz. Astronom.* Ser. II 13 (1958), 243--248; [journal record](https://web.math.pmf.unizg.hr/glasnik/mostcited.html) | Original function-weighted quasi-arithmetic/Bajraktarević class. | The candidate is exactly in this class for every \(d\ne0\) and positive \(f\). | Very high, using the explicit modern primary restatement below. |
| [Aczél--Daróczy, “Über verallgemeinerte quasilineare Mittelwerte, die mit Gewichtsfunktionen gebildet sind,” *Publ. Math. Debrecen* 10 (1963), 171--190](https://doi.org/10.5486/PMD.1963.10.1-4.24) | Equality and homogeneity theory for function-weighted quasi-linear means; homogeneous Bajraktarević mappings are Gini mappings. | General homogeneity is substantially prior theory, not a fresh axiom problem. | High. |
| [Páles--Pasteczka, “Characterization of the Hardy Property of Means and the Best Hardy Constants,” *Math. Inequal. Appl.* 19 (2016), 1141--1158](https://doi.org/10.7153/MIA-19-84) | Explicit Gini diagonal, Bajraktarević definition, and recall of the homogeneous-classification theorem. | Authoritative formula and terminology check. | Very high. |
| [Páles--Pasteczka, “On Kedlaya-Type Inequalities for Weighted Means,” *J. Inequal. Appl.* 2018:99](https://doi.org/10.1186/s13660-018-1685-z) | Weighted Gini formula off and on the diagonal; \(G_{p,0}=P_p\); deviation, concavity, and monotonicity framework. | Exact weighted classical and diagonal coverage; gives property pointers. | Very high. |
| [Páles--Pasteczka, “Decision Making via Generalized Bajraktarević Means,” *Ann. Oper. Res.* (2023)](https://doi.org/10.1007/s10479-023-05582-1) | General weighted Bajraktarević construction; weighted Gini off-diagonal and diagonal; exact Gini comparison and coordinate-monotonicity criteria recalled in Section 7.2. | Confirms the weighted framework and sharp classical \(G_{p,q}\) property regions used here. | Very high. |
| [Páles--Zakaria, “On the Equality of Bajraktarević Means to Quasi-Arithmetic Means,” *Results Math.* 75 (2020), paper 19](https://doi.org/10.1007/s00025-019-1141-5) | Weighted \(A_{\varphi,R}\) and symmetric \(B_{F,H}\) definitions, exact hypotheses, equality theory. | Supplies the decisive exact identification (3)--(4), including external weights and merely positive function weights. | Very high. |
| [Páles--Zakaria, “On the Local and Global Comparison of Generalized Bajraktarević Means,” *J. Math. Anal. Appl.* 455 (2017), 792--815](https://doi.org/10.1016/j.jmaa.2017.05.073) | Local and global comparison conditions for generalized Bajraktarević means. | General comparison is prior theory; the constrained family must be specialized against these criteria. | High. |
| [Matkowski--Wróbel, “On the Beckenbach--Gini--Lehmer Means and Means Mappings,” *Mathematics* 8 (2020), 1569](https://doi.org/10.3390/math8091569) | B--G--L arithmetic-generator means, complementary means, homogeneity, and arithmetic-invariant mean-type mappings. | Exact for the unweighted \(d=1\) slice and structurally relevant to weighted extensions; not exact coverage of all \(d\). | High. |

## Coverage verdicts

| Question | Verdict | Confidence |
| --- | --- | --- |
| Is (1) already a known mean construction? | **Yes—exactly a weighted Bajraktarević mean** \(A_{t^{-d},\,t f^{\alpha-1}}\), equivalently \(B_{t f^{\alpha-1},\,t^{1-d}f^{\alpha-1}}\). | Very high. |
| Are positive increasing \(f\) and positive weights enough for meanhood? | **Yes; even monotonicity of \(f\) is unnecessary for internality.** Positivity is enough because the Bajraktarević generator \(t^{-d}\) is continuous and strictly monotone. | Very high. |
| Is it an ordinary weighted power mean? | Pointwise yes after using the effective weights in (5); as a mapping of \(x\), no, because those weights depend on \(x\). | Very high. |
| Is it a classical weighted Gini mean? | Exactly when the chosen transform is a power (including the identity), and possibly in other cases that generate an equivalent Gini mapping; not for arbitrary \(f\) merely by notation. | High. |
| Is it a B--G--L/Lehmer mean? | The \(d=1\) slice is exactly B--G--L; power weights give Lehmer. The full family is more accurately called Bajraktarević. | High. |
| Is the diagonal finite and known in form? | Yes: (10) is the weighted geometric/function-weighted Bajraktarević value and recovers the Gini diagonal. The exact coupled path statement was not located verbatim. | High for the mathematics; medium for literature exhaustiveness. |
| Are homogeneity and monotonicity automatic? | No. Homogeneity is classified broadly by prior Bajraktarević theory; coordinatewise monotonicity requires extra conditions and can fail even classically. | High. |
| Does the limited search establish novelty of the constrained family or SmartDCA application? | No. | Very high. |

## What may still remain worth doing, stated safely

1. **Family-level coupling.** For a fixed \(\alpha\ne1\), the substitution
   \(R_\alpha(t)=t f(t)^{\alpha-1}\) is essentially a reparameterization of a
   positive Bajraktarević weight function. What is more specific is requiring one
   fixed transform \(f\) to couple the weights across the entire two-parameter
   family. A theorem about that cross-parameter family may be useful, but its
   novelty requires a more targeted search.

2. **Diagonal continuity as a correction theorem.** The concise pathwise result
   (10), contrasted with the source functional's divergent diagonal, is a rigorous
   and paper-relevant correction. Novelty-safe wording is: “We derive the diagonal
   extension of this transform-coupled Bajraktarević subfamily,” not “we discover a
   new mean.”

3. **Sharp property regions under restrictions on \(f\).** Exact conditions for
   homogeneity, coordinatewise monotonicity, concavity, or two-parameter ordering
   after imposing that the *same* \(f\) is positive/increasing/continuous may yield
   specialized results. They should be positioned as a specialization of
   Bajraktarević comparison and homogeneity theory. Fixed-\(\alpha\) monotonicity
   in \(d\) is already immediate from power-mean theory and is unlikely to be a
   novelty claim.

4. **SmartDCA application.** Causal strategy construction, deposit-budget
   accounting, and comparison with DCA may supply the paper's applied contribution.
   Safe wording is: “We apply a normalized Bajraktarević subfamily to SmartDCA and
   analyze its sequential economic properties.” Do not claim the application is
   first without a separate finance search.

Recommended naming in the next ticket is therefore **“the corrected out
quasi-Gini Bajraktarević subfamily”**, followed immediately by the exact
identification (3). Use **“weighted Gini”** for the power-transform special cases
and **“Beckenbach--Gini--Lehmer”** for the (d=1) slice.
