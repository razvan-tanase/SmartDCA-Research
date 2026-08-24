---
profile: smartdca-okf/0.4
type: research-note
title: "Differential guardrail feedback defeats cash single crossing"
description: "Exact decomposition, comparative static, and a horizon-minimal strict single-valley counterexample separating corrected-score behavior from policy-specific guardrail floors."
knowledge_role: evidence
status: stable
sources:
  - id: ticket-03
    title: "Characterize the cash single-crossing mechanism"
    resource: .scratch/smartdca/efforts/arbitrary-horizon-performance/issues/03-characterize-cash-single-crossing-mechanism
    source_kind: internal
  - id: guarded-rule
    title: "The guarded corrected-mean SmartDCA rule"
    resource: research/definitions/guarded-corrected-mean-smartdca-rule
    source_kind: internal
  - id: corrected-mean
    title: "The corrected out quasi-Gini mean"
    resource: research/definitions/corrected-out-quasi-gini-mean
    source_kind: internal
  - id: gini-region
    title: "Prior theory for the proposed corrected out quasi-Gini normalization"
    resource: research/notes/prior-theory-corrected-out-quasi-gini
    source_kind: internal
  - id: accounting-seam
    title: "Arbitrary-horizon cash-timing identity and exact-rational verification seam"
    resource: research/notes/arbitrary-horizon-accounting-verification-seam
    source_kind: internal
  - id: weak-valley
    title: "Weak single-valley prices do not determine guarded SmartDCA advantage"
    resource: research/notes/weak-single-valley-advantage-falsification
    source_kind: internal
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-24T11:05:28Z
generation_run: urn:uuid:8ebc8071-ab67-4268-a7ca-41e133539603
verified:
  - by: openai-codex/standards-review-0.1
    at: 2026-08-24T11:10:20Z
    review_run: urn:uuid:a85e3b86-c811-468c-a420-88980df31ea6
  - by: openai-codex/spec-review-0.1
    at: 2026-08-24T11:10:20Z
    review_run: urn:uuid:b3dae0f4-d2b0-4258-a251-f697f9c36cc2
---
# Differential guardrail feedback defeats cash single crossing

## Answer

Weak single-valley prices do not force the guarded corrected rule's cash path
to cross the neutral selector's cash path at most once. The corrected-mean
**score** does have an exact one-crossing comparative static, and that property
passes to cash whenever the two policies face the same clipped guardrail floor.
It fails for the realized guarded policies because their unit histories make
their later floors policy-specific. A strict four-date single-valley witness
has guarded cash-difference signs

\[
-,\ +,\ -,
\]

after their mandatory first-date tie, while the same scores with both floors
disabled have signs \(-,+,+\). Thus policy-specific repeated-floor feedback,
not an oscillating corrected-mean signal, creates the second cash crossing.
Four dates are horizon-minimal for this failure.[^ticket-03][^weak-valley]

A nonempty mechanism class survives: **reference-aligned guardrail feedback**
makes the corrected/neutral cash difference change sign at most once, from
nonpositive to nonnegative. Equal clipped floors are a simple special case.
More generally, the same conclusion holds whenever the observable one-step
**effective cash forcing** defined below changes sign at most once in that
direction. None of these conditions mentions an evaluation price or a
terminal-wealth sign, and none by itself determines the cash-timing
sum.[^accounting-seam]

## 1. Cash crossing and the exact recurrence

Fix a finite horizon \(n\) and equal positive deposits \(d_t=d>0\). Let
\(C_t^c,C_t^0\) denote carried cash after date \(t\) for the guarded corrected
rule and the neutral guarded selector, respectively, and put

\[
D_t:=C_t^c-C_t^0,\qquad D_0=0.
\tag{1}
\]

Both policies use the canonical guardrail, but their prior unit cushions can
differ. Write their clipped floors as \(m_t^c,m_t^0\), let \(a_t\in(0,1)\)
be the corrected score, and define the neutral post-floor discretionary base

\[
H_t^0:=C_{t-1}^0+d_t-m_t^0\ge0,
\qquad \Delta m_t:=m_t^c-m_t^0.
\tag{2}
\]

The guarded purchase representation gives

\[
C_t^c=(1-a_t)(C_{t-1}^c+d_t-m_t^c),
\qquad
C_t^0=\frac12(C_{t-1}^0+d_t-m_t^0).
\]

Subtracting yields the exact state recursion

\[
\boxed{
D_t=(1-a_t)D_{t-1}+g_t,
\qquad
g_t:=\left(\frac12-a_t\right)H_t^0
      -(1-a_t)\Delta m_t .
}
\tag{3}
\]

Equation (3) separates the two mechanisms. The first term in \(g_t\) is the
discretionary-score forcing on the neutral post-floor base. The second is the
entire incremental effect of policy-specific floor amounts. Merely recording
that both floors are active is insufficient: when both raw floors are
positive, different unit cushions generally give different floor amounts.
The definitions of the floor, score, and neutral selector are inherited from
the canonical guarded rule.[^guarded-rule]

Delete zeros from \((D_1,\ldots,D_n)\). In this note, **cash single crossing**
means that the remaining sign word is empty, constant, or a block of minus
signs followed by a block of plus signs. This is the direction generated by
the corrected score on a single-valley path. A sequence with signs
\(-,+,-\) therefore fails both this directional definition and the weaker
"at most one sign change" definition.

## 2. The corrected reference crosses the current price at most once

The effort fixes \(f=\mathrm{id}\) and equal weights. For normalized positive
lagged prices \(z_1,\ldots,z_s\), the corrected mean is therefore the
classical equal-weight Gini mean[^corrected-mean]

\[
R_s=
\left(\frac{\sum_{i=1}^s z_i^\alpha}
           {\sum_{i=1}^s z_i^\beta}\right)^{1/(\alpha-\beta)}
\quad(\alpha\ne\beta),
\tag{4}
\]

with its weighted-geometric diagonal when \(\alpha=\beta\). This family is
coordinatewise monotone exactly on the declared classical region
\(\alpha\beta\le0\), but the append-one-observation fact needed here is
stronger in parameter coverage and has a direct proof.[^gini-region]

Let \(d=\alpha-\beta\ne0\) and
\(B_s=\sum_{i=1}^s z_i^\beta>0\). From (4),

\[
R_{s+1}^{d}
=\frac{B_sR_s^d+z_{s+1}^\beta z_{s+1}^d}
       {B_s+z_{s+1}^\beta}.
\tag{5}
\]

The right side is a strict convex combination of \(R_s^d\) and
\(z_{s+1}^d\). Whether \(d\) is positive or negative, inversion through the
strictly monotone map \(x\mapsto x^d\) gives

\[
\min(R_s,z_{s+1})\le R_{s+1}\le\max(R_s,z_{s+1}),
\tag{6}
\]

with strict inequalities when \(R_s\ne z_{s+1}\). On the diagonal,

\[
\log R_{s+1}
=\frac{B_s\log R_s+z_{s+1}^\alpha\log z_{s+1}}
       {B_s+z_{s+1}^\alpha},
\]

where now \(B_s=\sum_i z_i^\alpha\), so (6) follows from the same convex-
combination argument. This proves the required comparative static on the
whole identity-transform parameter plane, including the ticket's restricted
region.

Now let the purchase prices be weak single-valley and let \(k\) be the first
trough date. On the descent, \(z_t\le z_i\) for every \(i<t\), so internality
gives \(z_t\le R_{t-1}\). On the nondecreasing recovery, once
\(z_t\ge R_{t-1}\), (6) gives \(R_t\le z_t\le z_{t+1}\); hence the inequality
persists at every later date. Therefore the comparison of current price with
the lagged reference changes direction at most once.

For \(\alpha<1\), the canonical score is

\[
a_t=\frac{1}{1+(z_t/R_{t-1})^{1-\alpha}},
\]

so

\[
a_t\ge\frac12\quad\Longleftrightarrow\quad z_t\le R_{t-1}.
\tag{7}
\]

Consequently \((1/2-a_t)\) is nonpositive and then, at most once, becomes
nonnegative. The corrected-mean signal itself cannot generate a
\(-,+,-\) effective-forcing pattern on a weak single-valley path.

## 3. Reference-aligned guardrail feedback is sufficient

By Section 2, there is a boundary \(j\) such that

\[
\frac12-a_t\le0\quad(t\le j),
\qquad
\frac12-a_t\ge0\quad(t>j).
\tag{8}
\]

Suppose the clipped floor differences are aligned with that boundary:

\[
\Delta m_t\ge0\quad(t\le j),
\qquad
\Delta m_t\le0\quad(t>j).
\tag{9}
\]

Before the boundary, both the score component and the floor component in
\(g_t\) are nonpositive. After it, both are nonnegative. Hence \(g_t\) has
the same one-crossing direction as the corrected retention signal. Induction
in (3) gives \(D_t\le0\) before the boundary; afterward, once \(D_t\ge0\),
the positive coefficient \(1-a_t\) and nonnegative forcing keep it
nonnegative. Thus the cash path has at most one crossing, from nonpositive to
nonnegative.

Condition (9) is an online-observable guardrail condition: before the
reference crossing, the corrected floor is no smaller than the neutral floor;
afterward, it is no larger. It is sufficient, not necessary. It permits
different and repeatedly active floors, provided their feedback reinforces
rather than opposes the score's crossing.

The broadest version used by this proof is simply that the exact effective
forcing \(g_t\) in (3) is nonpositive up to some date and nonnegative
thereafter. That condition is formulated entirely in terms of current scores,
carried cash, deposits, and clipped guardrail floors; it does not inspect
terminal wealth.

### Why alignment is not necessary

Condition (9) controls the score and floor components separately, but the
recurrence only needs their sum \(g_t\) to have the required sign. A
misaligned floor component can therefore be outweighed by same-period score
forcing. This is an exact obstruction to necessity, not merely finite
non-discovery.

With unit deposits,

\[
p=(1,2/3,1/2,2/3),\qquad
\lambda=3/4,\qquad(\alpha,\beta)=(0,-1),
\]

the strict valley has reference boundary \(j=3\) and

\[
\Delta m=\left(0,0,-\frac{11}{320},-\frac{1699}{18720}\right).
\]

The negative date-three floor difference violates the required
\(\Delta m_3\ge0\). At that date the carry, score, and floor components are

\[
-\frac{11}{624},\qquad -\frac{125}{1664},\qquad \frac{11}{832},
\]

so the score and floor terms still sum to
\(g_3=-103/1664<0\). Consequently,

\[
D=\left(0,-\frac{11}{240},-\frac{397}{4992},
\frac{841}{149760}\right)
\]

has the permitted sign word \(-,-,+\). Thus (9) is not necessary for cash
single crossing.

### Common clipped floors

Suppose

\[
m_t^c=m_t^0\qquad(t=1,\ldots,n).
\tag{10}
\]

Repeated activation is allowed in (10); it requires only that the two clipped
amounts agree. Equation (3) reduces to

\[
D_t=(1-a_t)D_{t-1}
    +\left(\frac12-a_t\right)H_t^0.
\tag{11}
\]

Before the score crossing, the forcing in (11) is nonpositive, so induction
from \(D_0=0\) gives \(D_t\le0\). After the score crossing the forcing is
nonnegative. Since \(1-a_t>0\), once \(D_t\ge0\) it remains nonnegative.
Thus the cash path has at most one crossing, from nonpositive to
nonnegative. The proof also covers the floor-disabled counterfactual
\(m_t^c=m_t^0=0\).

The subfamily is nonempty beyond constant prices. With unit deposits,

\[
p=(1,1/2,2/3,1),\qquad
\lambda=1/2,\qquad(\alpha,\beta)=(0,-1),
\tag{12}
\]

the path is a strict single valley. The common corrected/neutral floor path is

\[
(1/2,3/8,0,0),
\]

so the floor activates repeatedly at dates one and two without diverging.
The nonneutral corrected scores are

\[
(1/2,2/3,1/2,2/5),
\]

and the exact cash differences are

\[
\left(0,-\frac7{48},-\frac7{96},\frac{41}{320}\right).
\tag{13}
\]

This gives a nonconstant, strict member of the surviving class whose cash
path actually crosses once.

The larger class in (9) also contains a strict interior case with unequal
policy floors. For unit deposits,

\[
p=(1,1/4,1/2,1),\qquad
\lambda=7/8,\qquad(\alpha,\beta)=(0,-1),
\]

the boundary is \(j=2\), the retention differences are

\[
(0,-3/10,1/18,1/5),
\]

the floor differences are

\[
(0,0,-39/320,-37/5760),
\]

and

\[
D=(0,-39/640,133/2304,22903/115200).
\]

The strict score, floor, cash-sign, and active-branch margins persist under a
small perturbation of the non-warm-up inputs, so this is a nonempty strict
region rather than only an equality slice.

## 4. Horizon-minimal guarded counterexample

Take four unit deposits and

\[
p=\left(1,\frac1{16},1,8\right),\qquad
P=p_4,\qquad
\lambda=\frac{63}{64},\qquad
(\alpha,\beta)=(-1,0),\qquad f=\mathrm{id}.
\tag{14}
\]

The purchase prices form a strict single valley with the trough at date two.
The parameters satisfy \(0<\lambda<1\), \(\alpha<1\), and
\(\alpha\beta=0\), so (14) lies inside the declared coordinatewise-monotone
weighted-Gini region. The evaluation price is recorded only to make (14) a
complete public-ledger scenario; cash crossing does not depend on it.

The exact lagged references and corrected scores are

| Date | \(R_{t-1}\) | \(a_t\) | Score side of \(1/2\) |
|---:|---:|---:|:---:|
| 1 | warm-up | \(1/2\) | tie |
| 2 | \(1\) | \(256/257\) | above |
| 3 | \(2/17\) | \(4/293\) | below |
| 4 | \(1/6\) | \(1/2305\) | below |

Thus the score crosses once, between dates two and three, exactly as (7)
predicts. The guarded floor paths are

\[
\begin{aligned}
m^c&=\left(\frac{63}{64},\frac{2015}{2048},
             \frac{9919}{16448},
             \frac{2267493}{2409632}\right),\\
m^0&=\left(\frac{63}{64},\frac{2015}{2048},
             \frac{203}{256},\frac{111}{1024}\right).
\end{aligned}
\tag{15}
\]

Both policies activate the floor at all four dates, but their floor amounts
first diverge at date three. The date-three difference is negative, aligned
with the post-reference-crossing score, whereas the date-four difference is
positive and violates (9). The resulting exact guarded cash differences are

\[
\boxed{
D=\left(
0,
-\frac{12495}{1052672},
\frac{174032415}{616865792},
-\frac{142575068237}{2843751301120}
\right).
}
\tag{16}
\]

After deleting the first-date zero, (16) has signs \(-,+,-\), so it has two
cash crossings. This is horizon-minimal: the warm-up score and common first
floor force \(D_1=0\), and two sign changes require at least three subsequent
nonzero entries, hence at least four dates. No claim of globally minimal
fraction height is needed for that exact horizon statement.

The floor-disabled replay of the same prices, deposits, and scores gives

\[
D^{\circ}=\left(
0,
-\frac{765}{1028},
\frac{70545}{602408},
\frac{585268881}{555420176}
\right),
\tag{17}
\]

whose sign word is \(-,+,+\). Equivalently, the guarded effective forcing
in (3) has signs \(-,+,-\), whereas the floor-disabled forcing has signs
\(-,+,+\). The score and reference sequence is identical in the two replays;
only the guardrail floors are disabled. Equations (15)--(17) therefore isolate
the failed single crossing to policy-specific repeated-floor feedback. All
fractions above are returned by the public exact-rational ledger, whose direct
and cash-timing routes verify one another.[^accounting-seam]

## 5. Executable evidence and unresolved boundary

The exact witness, decomposition, surviving condition, and finite-search
context are replayed by
[`check_cash_single_crossing_mechanism.py`](../../reproducibility/checks/check_cash_single_crossing_mechanism.py).
The deterministic
[`cash_single_crossing_search.py`](../../reproducibility/cash_single_crossing_search.py)
enumerates 559 independently validated four-date weak single-valley paths
using the declared 12-level rational price grid, seven safety factors, three
exact-rational parameter pairs, unit deposits, and \(P=p_4\). Among 11,739
accepted scenarios, with zero exact-domain rejection, it observes 27 cases
with at least two cash sign changes; 25 are genuine strict cycles. The strict
witness in (14) is the first such cycle under the run's lexicographic horizon,
price-complexity, parameter-complexity, and fixed deposit-complexity ordering.

The same diagnostic over ticket 02's earlier price, safety, and parameter grid
accepts 20,466 scenarios and observes no multiple cash sign change. That
finite non-discovery explains why the mechanism survived the earlier grid; it
does not weaken the exact counterexample above.[^weak-valley] Conversely, the
5,371 cases in the new grid satisfying reference-aligned guardrail feedback
have no single-crossing failure, as required by the proof rather than inferred
from the count. Named checks also cover the diagonal
\((\alpha,\beta)=(0,0)\), the common-floor boundary, the strict interior case,
and the exact non-necessity obstruction.

The following points remain unresolved and belong to the later boundary work:

- whether reference-aligned guardrail feedback has a useful ex ante
  price-and-deposit characterization that avoids running both policy ledgers;
- whether a useful observable necessary-and-sufficient condition can sharpen
  (9), which the exact obstruction above proves is not necessary; and
- which additional timing-and-magnitude condition converts a surviving cash
  crossing into a terminal-wealth ordering.

The arbitrary-horizon statements in Sections 2 and 3 are proofs; the named
fractions in Section 4 are an exact counterexample; the aggregate counts in
this section are finite-grid computational observations.

## 6. Consequence and scope limit

The proposed mechanism does not survive the initially declared weak
single-valley class, and strict slopes do not repair it. What survives is a
clean score-level theorem and a cash-level theorem conditional on
nondivergent—or, more generally, single-crossing effective—floor forcing.
These are useful diagnostic conditions for the next boundary ticket because
they are causal-ledger observables rather than outcome labels.

Cash single crossing is not itself a terminal-performance theorem. The
two-strategy cash-timing identity weights cash differences positively across
falls, negatively across rises, and adds a terminal-cash coefficient when
\(P\ne p_n\). A one-crossing cash path therefore still needs a separate
timing-and-magnitude condition before its weighted sum has a predictable sign.
This note proves no corrected-versus-neutral or corrected-versus-DCA terminal
wealth ordering and makes no stochastic claim.[^accounting-seam]

[^ticket-03]: [Characterize the cash single-crossing mechanism](../../.scratch/smartdca/efforts/arbitrary-horizon-performance/issues/03-characterize-cash-single-crossing-mechanism.md)
[^guarded-rule]: [The guarded corrected-mean SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md)
[^corrected-mean]: [The corrected out quasi-Gini mean](../definitions/corrected-out-quasi-gini-mean.md)
[^gini-region]: [Prior theory for the proposed corrected out quasi-Gini normalization](prior-theory-corrected-out-quasi-gini.md)
[^accounting-seam]: [Arbitrary-horizon cash-timing identity and exact-rational verification seam](arbitrary-horizon-accounting-verification-seam.md)
[^weak-valley]: [Weak single-valley prices do not determine guarded SmartDCA advantage](weak-single-valley-advantage-falsification.md)
