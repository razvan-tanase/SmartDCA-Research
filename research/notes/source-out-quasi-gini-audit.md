# Audit of the source out quasi-Gini functional

Statement: [Exact mean classification of the source out quasi-Gini functional](../theorems/source-out-functional-mean-classification.md). This note carries the proof, counterexamples, and property-by-property audit.

## Scope and notation

The audited edition is the fingerprinted arXiv:2308.05200v1 snapshot whose identity,
provenance qualifications, and paper-level reading are recorded in
[its source summary](../../references/summaries/smartdca-superiority-source-paper.md);
the page references below point into the preserved bytes that summary fingerprints.

Calvet, Herranz-Celotti, and Valimamode define the out construction in Appendix B,
Eq. (70), and call it a quasi-Gini mean. With the project's independent parameters
\(\alpha=\rho+1\), \(\beta=\gamma\), and \(d=\alpha-\beta\ne0\), the construction is

\[
Q_{\alpha,\beta}^{f}(x_1,\ldots,x_m)
=
\left(
\frac{\sum_{i=1}^m x_i f(x_i)^{\alpha-1}}
     {\sum_{i=1}^m f(x_i)^\beta}
\right)^{1/d},
\qquad x_i>0,
\]

where \(f:(0,\infty)\to(0,\infty)\) is assumed increasing. The source merely
introduces Eq. (70) "for the sake of completeness" and states its reduction to the
quasi-Lehmer construction; it gives no proof of reflexivity, internality, continuity,
homogeneity, coordinatewise monotonicity, or a diagonal extension
([source PDF, Appendix B, Eq. (70), PDF p. 12](../../references/2308.05200v1.pdf#page=12)).

A function is a mean on an interval when its value lies between the minimum and
maximum of its arguments. In particular, internality forces
\(M(c,\ldots,c)=c\). This is the definition used in the mean-theory literature
([Matkowski and Wrobel, 2020, Section 2](https://doi.org/10.3390/math8091569)).

## Main result: exact mean classification off the diagonal

**Proposition.** Fix \(m\ge1\), \(d\ne0\), and a positive function \(f\). The source
functional \(Q_{\alpha,\beta}^{f}\) is a mean on \((0,\infty)^m\) if and only if

\[
\boxed{\ d=1\quad\text{or}\quad f(x)=x\text{ for every }x>0.\ }
\]

The conclusion does not require monotonicity of \(f\). Consequently, assuming that
\(f\) is positive and even *strictly* increasing does not make Eq. (70) a mean over
the full parameter plane.

**Proof - necessity.** On a constant vector \(x_i=c\),

\[
Q_{\alpha,\beta}^{f}(c,\ldots,c)
=c^{1/d}f(c)^{(d-1)/d}.
\]

Reflexivity therefore requires
\(f(c)^{d-1}=c^{d-1}\) for every \(c>0\). If \(d\ne1\), positivity and injectivity of
the nonzero real power imply \(f(c)=c\) for every \(c\). Thus internality is
impossible unless \(d=1\) or \(f\) is the identity.

**Proof - sufficiency on \(d=1\).** Here \(\alpha=\beta+1\), so

\[
Q_{\beta+1,\beta}^{f}(x)
=\frac{\sum_i x_i f(x_i)^\beta}{\sum_i f(x_i)^\beta}.
\]

This is a weighted arithmetic mean with strictly positive weights
\(f(x_i)^\beta\), hence it lies between \(\min_i x_i\) and \(\max_i x_i\).

**Proof - sufficiency for \(f(x)=x\).** In this case

\[
Q_{\alpha,\beta}^{\mathrm{id}}(x)
=\left(\frac{\sum_i x_i^\alpha}{\sum_i x_i^\beta}\right)^{1/(\alpha-\beta)},
\]

the classical two-parameter Gini formula. Writing
\(x_i^\alpha=x_i^\beta x_i^d\), the ratio inside the power is a positive weighted
average of the \(x_i^d\). If \(d>0\), applying the increasing \(1/d\) power gives
internality; if \(d<0\), both order reversals cancel and give the same conclusion.
This completes the proof.

**Strict counterexample.** Let \(f(x)=2x\), \(\alpha=2\), \(\beta=0\), and take the
constant vector \((1,\ldots,1)\). Then \(d=2\) and
\(Q_{2,0}^{f}(1,\ldots,1)=\sqrt2\ne1\). The transform is positive, continuous, and
strictly increasing, so none of these stronger regularity assumptions rescues
reflexivity or internality.

## Property-by-property audit

| Property | Rigorous status under only positive increasing \(f\) | Reason |
| --- | --- | --- |
| Positivity and well-definedness | Holds for \(d\ne0\) | Both sums and their ratio are positive, so every real power is defined. |
| Symmetry | Holds | Both sums are invariant under permutations of the coordinates. |
| Reflexivity | Holds **iff** \(d=1\) or \(f=\mathrm{id}\) | Exact constant-vector calculation above. |
| Internality | Holds **iff** \(d=1\) or \(f=\mathrm{id}\) | Necessity follows from reflexivity; both sufficient cases are proved above. |
| Continuity | Not guaranteed; holds if \(f\) is continuous | Finite sums, quotients with positive denominator, and positive real powers preserve continuity. Monotonicity alone permits jumps. |
| Homogeneity of degree one | Not guaranteed | It holds for \(f=\mathrm{id}\); on \(d=1\), it also holds whenever relative weights are scale-invariant, e.g. \(f(tx)=k(t)f(x)\). General increasing transforms need not have this property. |
| Coordinatewise monotonicity | Not guaranteed, even in a valid-mean case | A classical Gini/Lehmer example below decreases when one coordinate increases. |

### Continuity counterexample

Use the strictly increasing but discontinuous transform

\[
f(x)=\begin{cases}x,&0<x<1,\\x+1,&x\ge1,\end{cases}
\]

and take \((\alpha,\beta)=(2,1)\). For \(x=(s,2)\),

\[
\lim_{s\uparrow1}Q_{2,1}^{f}(s,2)=\frac74,
\qquad
Q_{2,1}^{f}(1,2)=\frac85.
\]

Thus "positive increasing" is insufficient for continuity. Continuity of \(f\) is
a clean sufficient assumption, though it is not necessary in parameter cases where
the dependence on \(f\) cancels (for example, \((\alpha,\beta)=(1,0)\)).

### Homogeneity counterexample and sufficient cases

Let \(f(x)=1+x\) and again use \((\alpha,\beta)=(2,1)\). Then

\[
Q_{2,1}^{f}(1,2)=\frac85,
\qquad
Q_{2,1}^{f}(2,4)=\frac{13}{4}\ne2\frac85.
\]

Hence positivity, continuity, and strict increase of \(f\) do not imply homogeneity.
Two directly verified sufficient cases are:

1. \(f=\mathrm{id}\), for every \(d\ne0\); and
2. \(d=1\) with \(f(tx)=k(t)f(x)\) for a positive scale factor \(k(t)\), because the
   common factor \(k(t)^\beta\) cancels from the weights. The arithmetic case
   \(\beta=0\) is homogeneous independently of \(f\).

### Coordinatewise monotonicity counterexample

Coordinatewise monotonicity is distinct from the source's Theorem 3, which concerns
monotonicity in the *parameter* \(\rho\) on the quasi-Lehmer line
([source PDF, Theorem 3, PDF pp. 11-12](../../references/2308.05200v1.pdf#page=11)).
It fails even for the identity transform in a case that is a genuine mean. With
\((\alpha,\beta)=(2,1)\),

\[
Q_{2,1}^{\mathrm{id}}(x_1,x_2)=\frac{x_1^2+x_2^2}{x_1+x_2},
\]

and

\[
\left.\frac{\partial Q_{2,1}^{\mathrm{id}}(x_1,10)}{\partial x_1}\right|_{x_1=1}
=-\frac{79}{121}<0.
\]

Thus raising the first coordinate near \((1,10)\) lowers the functional. For context,
when \(f=\mathrm{id}\), \(\alpha\beta\le0\) is an immediately provable sufficient
region for coordinatewise nondecrease: after using symmetry in the two parameters to
take \(\alpha>\beta\), the logarithmic derivative is

\[
\frac{1}{\alpha-\beta}
\left(
\frac{\alpha x_j^{\alpha-1}}{\sum_i x_i^\alpha}
-\frac{\beta x_j^{\beta-1}}{\sum_i x_i^\beta}
\right)\ge0
\]

when \(\alpha\ge0\ge\beta\). No corresponding sign follows from positivity and
increase of a general \(f\).

## Compatibility identities

Both algebraic compatibility statements motivating the source definition are correct.

1. **Identity transform.** If \(f(x)=x\), then Eq. (70) becomes exactly

   \[
   \left(\frac{\sum_i x_i^\alpha}{\sum_i x_i^\beta}\right)^{1/(\alpha-\beta)},
   \]

   the classical Gini formula.

2. **Out quasi-Lehmer line.** If \(\alpha-\beta=1\), equivalently
   \(\rho=\gamma\), then

   \[
   Q_{\beta+1,\beta}^{f}(x)
   =\frac{\sum_i x_i f(x_i)^\beta}{\sum_i f(x_i)^\beta},
   \]

   exactly the source's out quasi-Lehmer construction in Eq. (54). The source's
   sentence following Eq. (70) is therefore correct
   ([source PDF, Eqs. (54) and (70), PDF pp. 11-12](../../references/2308.05200v1.pdf#page=11)).

## Behavior as \(\alpha\to\beta\)

Fix \(\beta\), set \(d=\alpha-\beta\), and define

\[
A_0=\sum_i x_i f(x_i)^{\beta-1},
\qquad
B_0=\sum_i f(x_i)^\beta.
\]

Then

\[
\log Q_{\beta+d,\beta}^{f}(x)
=\frac{1}{d}
\log\left(
\frac{\sum_i x_i f(x_i)^{\beta-1+d}}{B_0}
\right).
\]

If \(A_0/B_0>1\), the limit is \(+\infty\) as \(d\downarrow0\) and \(0\) as
\(d\uparrow0\); if \(A_0/B_0<1\), the two one-sided behaviors are reversed. A finite
limit for a particular vector requires \(A_0=B_0\), in which case l'Hopital's rule
gives

\[
\lim_{\alpha\to\beta}Q_{\alpha,\beta}^{f}(x)
=
\exp\left(
\frac{\sum_i x_i f(x_i)^{\beta-1}\log f(x_i)}
     {\sum_i x_i f(x_i)^{\beta-1}}
\right).
\]

For this finite-limit condition to hold for *every* vector, it must hold in particular
for each constant vector \((c,\ldots,c)\). There \(A_0/B_0=c/f(c)\), so it forces
\(f(c)=c\) for every \(c>0\). Therefore:

\[
\boxed{\text{The source family has a global finite diagonal extension only for }f=\mathrm{id}.}
\]

In that identity case, the familiar weighted-geometric diagonal value is

\[
Q_{\beta,\beta}^{\mathrm{id}}(x)
=\exp\left(
\frac{\sum_i x_i^\beta\log x_i}{\sum_i x_i^\beta}
\right).
\]

The obstruction is visible even on constant vectors. For \(f(x)=2x\) and \(c=1\),
\(Q_{\beta+d,\beta}^{f}(1,\ldots,1)=2^{1-1/d}\), which tends to \(0\) from
\(d>0\) and to \(+\infty\) from \(d<0\). Merely assigning a value on
\(\alpha=\beta\) cannot make the general source family continuous there.

## Audit verdict and implications for a correction

The algebra in Eq. (70) correctly recovers both intended special cases, but the noun
"mean" is false for a general positive increasing transform away from
\(\alpha-\beta=1\). This is a mathematical classification, not just a missing proof.
The source also supplies no route to a general diagonal extension, and its assumptions
do not guarantee continuity, homogeneity, or coordinatewise monotonicity.

Any corrected two-parameter construction must therefore, at minimum:

1. alter or normalize the off-diagonal formula so every constant vector maps to its
   common value;
2. preserve the identity-transform Gini formula and the full \(d=1\) out
   quasi-Lehmer line;
3. make the numerator-denominator log difference vanish to first order as
   \(d\to0\), if a finite diagonal limit is required; and
4. state continuity, homogeneity, and coordinate-monotonicity assumptions separately,
   because none follows merely from positivity and increase of \(f\).

This audit does not choose a normalization; that was a separate research decision, since
settled by [The corrected out quasi-Gini mean](../definitions/corrected-out-quasi-gini-mean.md),
which defines the repair and carries the four requirements above as design
constraints.

## Sources

- Emmanuel Calvet, Luca Herranz-Celotti, and Karim Valimamode,
  [*SmartDCA superiority*](https://arxiv.org/abs/2308.05200), arXiv:2308.05200v1
  (2023), especially Appendix B, Eqs. (54) and (70). The exact audited version is the
  [attached PDF](../../references/2308.05200v1.pdf).
- Janusz Matkowski and Malgorzata Wrobel,
  [*On the Beckenbach-Gini-Lehmer Means and Means Mappings*](https://doi.org/10.3390/math8091569),
  *Mathematics* 8(9):1569 (2020), especially Section 2 for the mean, symmetry, and
  homogeneity definitions.
