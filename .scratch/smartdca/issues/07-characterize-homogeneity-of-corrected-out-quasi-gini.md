# Characterize homogeneity of the corrected out quasi-Gini mean

Type: research
Status: resolved
Blocked by: 05
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

For the canonical numerator-preserving corrected out quasi-Gini mean, characterize exactly when degree-one homogeneity
\[
\widehat G_{\alpha,\beta}^{f,\mathrm{out}}(cx;w)
=c\,\widehat G_{\alpha,\beta}^{f,\mathrm{out}}(x;w)
\]
holds for every positive scale \(c\), positive input vector, and positive external weights. Cover off-diagonal and diagonal parameters, identify exceptional parameter values, state the weakest regularity needed for the transform classification, and separate prior theory from the project-specific proof.

## Comments

- Ticket 05 was accepted when the user explicitly chose to continue on 2026-08-15.
- Identifier 06 is already occupied by the resolved retrospective source-audit validation, so the recomputed frontier uses the next free identifier, 07.
- This ticket deliberately isolates one unresolved mean axiom; coordinatewise monotonicity and the remaining parameter-region questions stay outside its scope.
- Primary-source coverage is delegated under the research workflow; the parent executor independently reconstructs and reviews the theorem and all examples.
- Independent parent review checked the delegated literature note against the ticket and project standards, verified the fixed-parameter/family-wide distinction, source hypotheses, two-point necessity proof, diagonal argument, power-to-Gini parameter map, and limitations. No actionable source or proof finding remained.
- The final verification reran 4,005 seeded cases after review, compiled the script, and resolved every newly added local artifact link.

## Answer

Write \(d=\alpha-\beta\) and

\[
R_\alpha(t):=t f(t)^{\alpha-1}.
\]

### Exact fixed-parameter theorem

For \(d\ne0\), the following are equivalent:

1. \(\widehat G_{\alpha,\beta}^{f,\mathrm{out}}\) is degree-one homogeneous for every positive input vector of length at least two and every positive external-weight vector;
2. for each \(c>0\), the ratio \(f(ct)^{\alpha-1}/f(t)^{\alpha-1}\) is independent of \(t>0\);
3. either \(\alpha=1\), or \(g(t):=f(t)/f(1)\) is multiplicative on \((0,\infty)\): \(g(st)=g(s)g(t)\).

Under the project's standing assumption that \(f\) is positive and increasing, this becomes the sharp classification

\[
\boxed{
\widehat G_{\alpha,\beta}^{f,\mathrm{out}}
\text{ is homogeneous}
\iff
\alpha=1\ \text{or}\ f(t)=C t^r
}
\tag{1}
\]

with \(C>0\), \(r\ge0\) if “increasing” means nondecreasing, and \(r>0\) if it means strictly increasing.

On the diagonal \(\alpha=\beta=q\), exactly the same statement holds with \(q\) in place of \(\alpha\):

\[
\boxed{
\widehat G_{q,q}^{f,\mathrm{out}}
\text{ is homogeneous}
\iff
q=1\ \text{or}\ f(t)=C t^r.
}
\tag{2}
\]

There are no further exceptional values of \(d\). The exceptions \(\alpha=1\) and \(q=1\) are degenerate in the transform: the exponent of \(f\) is zero, so \(f\) cancels from the mean.

### Proof

Off the diagonal, use the weighted Bajraktarević representation

\[
\widehat G_{\alpha,\beta}^{f,\mathrm{out}}
=A_{\phi_d,R_\alpha},
\qquad \phi_d(t)=t^{-d}.
\]

Scaling the inputs by \(c>0\) gives

\[
A_{\phi_d,R_\alpha}(cx;w)
=c\,A_{\phi_d,R_{\alpha,c}}(x;w),
\qquad R_{\alpha,c}(t):=R_\alpha(ct),
\]

because \(\phi_d(ct)=c^{-d}\phi_d(t)\). Hence homogeneity is equivalent to equality of the two means with the same strictly monotone generator \(\phi_d\) and weight functions \(R_{\alpha,c}\) and \(R_\alpha\).

It is enough to use a two-point vector \((x,y)\) with \(x\ne y\). Cross-multiplying equality of the two weighted \(\phi_d\)-averages yields

\[
\bigl(R_{\alpha,c}(x)R_\alpha(y)
-R_\alpha(x)R_{\alpha,c}(y)\bigr)
\bigl(\phi_d(x)-\phi_d(y)\bigr)=0.
\]

The second factor is nonzero, so \(R_\alpha(ct)/R_\alpha(t)\) is independent of \(t\). The factor \(c\) contributed by \(R_\alpha(ct)=ct f(ct)^{\alpha-1}\) is itself independent of \(t\), leaving condition 2. If \(\alpha=1\), this condition is automatic. Otherwise, injectivity of the power map on positive numbers and setting \(t=1\) give

\[
f(ct)=\frac{f(c)f(t)}{f(1)},
\]

which is condition 3. Conversely, this scale equation makes \(R_{\alpha,c}\) proportional to \(R_\alpha\), and a common factor in the effective weights cancels, proving homogeneity.

For the diagonal mean, repeat the same argument with generator \(\phi_0(t)=\log t\). The additive identity \(\log(ct)=\log c+\log t\) contributes the required outer factor \(c\), and the same two-point cross-multiplication proves (2).

No regularity beyond positivity is needed for the exact multiplicative-function conclusion. Under the standing monotonicity assumption, \(a(u):=\log g(e^u)\) is monotone and additive, hence \(a(u)=ru\); therefore \(g(t)=t^r\). Standard measurability or local boundedness would also exclude pathological multiplicative solutions, but neither is needed here.

### Family-wide consequence and prior-theory position

A single transform makes the **entire** two-parameter corrected family homogeneous if and only if \(f(t)=Ct^r\). In that case the family is exactly classical weighted Gini after the parameter change

\[
p=1+r(\alpha-1),
\qquad q_G=p-(\alpha-\beta).
\]

Thus enforcing homogeneity across the family removes the non-power transform coupling; it does not create a new homogeneous mean class. This specializes the classical result that homogeneous Bajraktarević means are Gini means. The primary-source coverage and its hypotheses are recorded in [the ticket-07 literature note](../../../research/notes/ticket-07-homogeneity-primary-sources.md).

### Verification

The proof was checked against constant inputs, positive and negative \(d\), the diagonal, unequal external weights, the exceptional \(\alpha=q=1\) slice, and power exponents \(r=0,0.2,1,2.3\). The seeded script [checks 4,005 homogeneous cases](../../../reproducibility/checks/check_corrected_out_quasi_gini_homogeneity.py) with worst relative error \(2.91\times10^{-15}\).

For the non-power transform \(f(t)=1+t\), \(\alpha=2\), and \(\beta=1\),

\[
\widehat G(1,2)=\frac85,
\qquad
\widehat G(2,4)=\frac{13}{4}
\ne2\widehat G(1,2)=\frac{16}{5}.
\]

The same transform also fails homogeneity at the nonexceptional diagonal \(q=2\): the respective values are approximately \(1.68179283\) and \(3.40872159\ne2(1.68179283)\).

### Scope

This ticket settles only degree-one homogeneity. It does not settle coordinatewise monotonicity, the remaining parameter comparisons, convexity/concavity, or the causal purchase rule.

## Significance gate

**Recommendation: Continue.** The result is a sharp structural boundary: a genuinely non-power transform cannot coexist with degree-one homogeneity away from the transform-free \(\alpha=q=1\) slice. This is useful, but it is a specialization of established Bajraktarević/Gini theory rather than a new mean class.

Alternatives remain **Narrow**, **Pivot**, or **Stop**. No next ticket is claimed until the user explicitly chooses.
