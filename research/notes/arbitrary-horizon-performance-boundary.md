---
profile: smartdca-okf/0.4
type: research-note
title: "Exact arbitrary-horizon evaluation-price boundary for guarded SmartDCA"
description: "Proof that every pairwise guarded SmartDCA wealth gap is affine in the evaluation price, together with the exact limit of reference-aligned cash single crossing."
knowledge_role: evidence
status: stable
sources:
  - id: ticket-04
    title: "Prove the arbitrary-horizon performance boundary"
    resource: .scratch/smartdca/efforts/arbitrary-horizon-performance/issues/04-prove-arbitrary-horizon-performance-boundary
    source_kind: internal
  - id: accounting
    title: "Arbitrary-horizon cash-timing identity and exact-rational verification seam"
    resource: research/notes/arbitrary-horizon-accounting-verification-seam
    source_kind: internal
  - id: mechanism
    title: "Differential guardrail feedback defeats cash single crossing"
    resource: research/notes/cash-single-crossing-mechanism
    source_kind: internal
  - id: weak-valley
    title: "Weak single-valley prices do not determine guarded SmartDCA advantage"
    resource: research/notes/weak-single-valley-advantage-falsification
    source_kind: internal
  - id: guarded-rule
    title: "The guarded corrected-mean SmartDCA rule"
    resource: research/definitions/guarded-corrected-mean-smartdca-rule
    source_kind: internal
  - id: guardrail
    title: "Epsilon-DCA safety is exactly a causal unit-coverage guardrail"
    resource: research/theorems/epsilon-dca-safety-unit-guardrail
    source_kind: internal
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-24T20:11:40Z
generation_run: urn:uuid:6a0602e3-5197-442d-bfc1-256ac8a382ba
verified:
  - by: openai-codex/standards-review-0.1
    at: 2026-08-24T20:11:40Z
    review_run: urn:uuid:2d41dd92-0f83-4940-9eff-8eba11d4196d
  - by: openai-codex/spec-review-0.1
    at: 2026-08-24T20:11:40Z
    review_run: urn:uuid:c830b658-ad37-43ba-b537-690dda4f5455
---
# Exact arbitrary-horizon evaluation-price boundary for guarded SmartDCA

## Answer

Reference-aligned guardrail feedback is enough to make corrected-minus-neutral
cash single-cross, but it is **not** enough to order terminal wealth. Even on
strict four-date valleys, with the evaluation price equal to the last purchase
price, the aligned class contains exact joint wins and exact joint losses
against DCA and the neutral guarded selector. Cash signs omit the magnitudes
and the unit position created by their timing.[^mechanism][^weak-valley]

The strongest exact boundary that survives is a pre-evaluation ledger
boundary. For either comparator, the corrected rule's terminal-wealth gap is
an affine function of the common evaluation price. Its intercept is the final
cash difference and its slope is the final unit difference, which is also an
exact functional of the entire cash-difference path. Those two quantities give
a necessary-and-sufficient win, tie, and loss classification at **every finite
horizon**. Reference alignment remains useful as a mechanism condition: after
adding a positive terminal corrected-minus-neutral cash difference, it gives a
nonempty low-evaluation-price class on which the corrected rule strictly beats
both comparators. The added cash and evaluation conditions are indispensable
to that conclusion, and neither is a consequence of the score alone.[^ticket-04]

## 1. Purchase-side setting

Fix any finite horizon \(n\ge1\), positive purchase prices
\(p_1,\ldots,p_n\), equal positive deposits \(d_t=d>0\), and a safety factor
\(0<\lambda<1\). Use the guarded corrected-mean rule \(c\), the neutral
guarded selector \(0\) with discretionary score \(1/2\), and DCA \(D\) on the
same inputs. For the single-valley specialization take \(f=\mathrm{id}\),
equal reference weights, \(\alpha<1\), and \(\alpha\beta\le0\). These are the
ticket's countercyclical, coordinatewise-monotone weighted-Gini restrictions;
the affine accounting result below itself needs none of the mean-specific
restrictions.[^guarded-rule][^mechanism]

The purchase rules do not read the eventual evaluation price \(P>0\).
Therefore all purchases, cash balances, units, references, scores, and clipped
floor branches are fixed before \(P\) is chosen. For a comparator
\(T\in\{D,0\}\), define the purchase-side differences

\[
D_t^T:=C_t^c-C_t^T,
\qquad
H_T:=D_n^T,
\tag{1}
\]

and the cash-timing slope

\[
U_T:=
\sum_{t=1}^{n-1}D_t^T
 \left(\frac1{p_{t+1}}-\frac1{p_t}\right)
-\frac{D_n^T}{p_n}.
\tag{2}
\]

Every quantity in (1)--(2) is observable from the two purchase ledgers and is
independent of \(P\). In particular, defining \(H_T\) or \(U_T\) does not use a
terminal-wealth sign or a win/loss label. The public exact-rational scenario
interface exposes the cash and unit ledgers independently and checks the
cash-timing identity against direct portfolio accounting.[^accounting]

## 2. Exact affine boundary

### Theorem

For every finite horizon and either comparator \(T\in\{D,0\}\),

\[
\boxed{
W_n^c(P)-W_n^T(P)=H_T+P U_T,
\qquad
U_T=Q_n^c-Q_n^T.
}
\tag{3}
\]

Consequently the following table is a complete necessary-and-sufficient
classification for every \(P>0\). Here \(R_T\) denotes the displayed positive
root when it exists.

| Purchase-side signs | Positive boundary | Exact classification as \(P\) increases |
|---|---:|---|
| \(H_T>0,\ U_T\ge0\) | none | strict win for every \(P>0\) |
| \(H_T>0,\ U_T<0\) | \(R_T=H_T/(-U_T)\) | win on \(0<P<R_T\); tie at \(R_T\); loss on \(P>R_T\) |
| \(H_T=0,\ U_T>0\) | none | strict win for every \(P>0\) |
| \(H_T=0,\ U_T=0\) | none | tie for every \(P>0\) |
| \(H_T=0,\ U_T<0\) | none | strict loss for every \(P>0\) |
| \(H_T<0,\ U_T>0\) | \(R_T=(-H_T)/U_T\) | loss on \(0<P<R_T\); tie at \(R_T\); win on \(P>R_T\) |
| \(H_T<0,\ U_T\le0\) | none | strict loss for every \(P>0\) |

The corrected rule strictly beats **both** DCA and neutral exactly when \(P\)
belongs to the intersection of the two strict-win intervals in the table.
Thus (3), rather than a cash sign word alone, is the sharp arbitrary-horizon
performance boundary.[^accounting]

### Proof

The two-strategy cash-timing identity gives

\[
\begin{aligned}
W_n^c(P)-W_n^T(P)
&=D_n^T\left(1-\frac{P}{p_n}\right)
 +P\sum_{t=1}^{n-1}D_t^T
 \left(\frac1{p_{t+1}}-\frac1{p_t}\right)\\
&=H_T+P U_T,
\end{aligned}
\tag{4}
\]

which proves the first identity in (3). Direct portfolio accounting on the
same fixed purchase ledger gives

\[
W_n^c(P)-W_n^T(P)
=(C_n^c-C_n^T)+P(Q_n^c-Q_n^T).
\tag{5}
\]

Comparing (4) and (5), or deriving both from the common cash recursion, gives
\(U_T=Q_n^c-Q_n^T\). An affine function on \(P>0\) has exactly the sign cases
in the table: a positive intercept and negative slope have the single positive
root \(H_T/(-U_T)\); a negative intercept and positive slope have the single
positive root \((-H_T)/U_T\); all remaining cases have constant strict sign or
are identically zero. This proves necessity, sufficiency, every tie statement,
and exhaustiveness. The proof uses no finite-grid inference.[^accounting]

### Single-valley exposure form

When the purchase prices are weak single-valley, let \(k\) be the first
trough date and put

\[
\begin{aligned}
A_T^\downarrow
&:=\sum_{t=1}^{k-1}D_t^T
\left(\frac1{p_{t+1}}-\frac1{p_t}\right),\\
A_T^\uparrow
&:=\sum_{t=k}^{n-1}D_t^T
\left(\frac1{p_t}-\frac1{p_{t+1}}\right).
\end{aligned}
\tag{5a}
\]

The reciprocal-price factors in both sums are nonnegative; flat steps
contribute zero. Splitting (2) at the trough gives

\[
U_T=A_T^\downarrow-A_T^\uparrow-\frac{H_T}{p_n},
\tag{5b}
\]

and therefore

\[
\boxed{
W_n^c(P)-W_n^T(P)
=H_T\left(1-\frac{P}{p_n}\right)
+P\left(A_T^\downarrow-A_T^\uparrow\right).
}
\tag{5c}
\]

In the important terminal-purchase-price evaluation \(P=p_n\), terminal cash
cancels exactly:

\[
\boxed{
W_n^c(p_n)-W_n^T(p_n)
=p_n\left(A_T^\downarrow-A_T^\uparrow\right).
}
\tag{5d}
\]

Thus corrected wins, ties, or loses at \(P=p_n\) exactly according as its
signed cash exposure across falling steps is greater than, equal to, or less
than its signed cash exposure across rising steps. Reference alignment
controls the order of the signs inside these sums but not their weighted
magnitudes, so it cannot establish the comparison by itself. Equations
(5a)--(5d) are an equivalent single-valley form of the affine theorem, not an
additional assumption.[^accounting][^mechanism]

## 3. What the guardrail and cash crossing add

### DCA comparison

Against DCA, \(H_D=C_n^c\). It is strictly positive under the section's
\(0<\lambda<1\) and \(d>0\) assumptions. Indeed, the unit guardrail always has
\(m_t\le\lambda d\). If \(B_t=C_{t-1}^c+d\), then

\[
B_t-m_t\ge C_{t-1}^c+(1-\lambda)d>0.
\]

The corrected score is strictly between zero and one, so
\(C_t^c=(1-a_t)(B_t-m_t)>0\) at every date. Hence the DCA boundary always
simplifies to

\[
\Pi_D:=
\begin{cases}
+\infty,&U_D\ge0,\\[2mm]
H_D/(-U_D),&U_D<0,
\end{cases}
\tag{6}
\]

and the corrected rule beats DCA exactly for \(0<P<\Pi_D\), ties at a finite
\(\Pi_D\), and loses above a finite \(\Pi_D\). If \(U_D\ge0\), it wins for
every positive evaluation price. This realized-path classification neither
asserts nor contradicts universal DCA dominance.[^guarded-rule]

Independently, the floor ensures

\[
W_n^c(P)\ge\lambda W_n^D(P)
\]

for every positive \(P\), including all regions where (6) says that corrected
wealth is below DCA wealth. The neutral selector inherits the same safety
factor from its own identical guardrail interface. Safety belongs to the
floor, not to the corrected-mean score and not to the affine boundary.[^guardrail]

### Reference-aligned, terminal-positive class

Now suppose the purchase prices are weak single-valley and reference-aligned
guardrail feedback holds at a corrected-score crossing boundary \(j\):

\[
m_t^c-m_t^0\ge0\quad(t\le j),
\qquad
m_t^c-m_t^0\le0\quad(t>j).
\tag{7}
\]

The mechanism theorem then makes \(D_t^0=C_t^c-C_t^0\) single-cross from a
possibly empty nonpositive block to a possibly empty nonnegative block. Add
the independent, pre-evaluation condition

\[
H_0=D_n^0>0.
\tag{8}
\]

When a negative block is present, (8) says that the cash crossing has actually
completed by the horizon. Define

\[
\Pi_0:=
\begin{cases}
+\infty,&U_0\ge0,\\[2mm]
H_0/(-U_0),&U_0<0.
\end{cases}
\tag{9}
\]

Equations (3), (6), and (9) prove the sharp joint statement

\[
\boxed{
W_n^c(P)>W_n^D(P)\ \text{and}\ W_n^c(P)>W_n^0(P)
\quad\Longleftrightarrow\quad
0<P<\min(\Pi_D,\Pi_0).
}
\tag{10}
\]

The right side is a nonempty interval because both finite boundaries are
positive and \(+\infty\) is allowed. If \(P\) equals the smaller finite
boundary, corrected ties the comparator attaining that boundary; if the two
finite boundaries coincide, it ties both. Above the smaller boundary it loses
to at least that comparator. Thus (10) is necessary and sufficient inside the
terminal-positive aligned class, not a one-sided estimate.[^mechanism]

Condition (7) supplies a clean investment-cycle interpretation of (8): the
corrected score first deploys more cash and later ends with more cash without
an intervening second reversal. It does **not** prove (8), sign \(U_0\), or
set the admissible evaluation-price range. Those are precisely the missing
timing-and-magnitude facts that cash single crossing alone cannot supply.

## 4. Exact strict region and sharp obstructions

All examples in this section have four unit deposits, \(f=\mathrm{id}\), and
use the public exact-rational ledger. They take
\((\alpha,\beta)=(0,-1)\) except for the explicitly marked double-reversal
witness. Each price path satisfies the single-valley predicate independently
of its reported wealth gaps.[^accounting][^weak-valley]

### A nonempty strict joint-win region

Take

\[
p=(1,1/4,1/2,1),
\qquad \lambda=7/8.
\tag{11}
\]

This is a strict interior-trough cycle. The reference boundary is \(j=2\),
all four clipped floors are active for both policies, and the unequal
post-boundary floor differences are strictly aligned. The exact
corrected-minus-neutral cash path is

\[
D^0=\left(0,-\frac{39}{640},\frac{133}{2304},
                  \frac{22903}{115200}\right).
\]

The pre-evaluation pairs are

\[
(H_D,U_D)=\left(\frac{16807}{28800},-\frac{7199}{9600}\right),
\qquad
(H_0,U_0)=\left(\frac{22903}{115200},-\frac{5171}{38400}\right).
\tag{12}
\]

Therefore

\[
\Pi_D=\frac{16807}{21597},
\qquad
\Pi_0=\frac{22903}{15513}.
\tag{13}
\]

At the explicit evaluation price \(P=1/2<\min(\Pi_D,\Pi_0)\),

\[
W^c-W^D=\frac{12017}{57600}>0,
\qquad
W^c-W^0=\frac{30293}{230400}>0.
\tag{14}
\]

The strict price slopes, active raw-floor margins, post-boundary alignment,
cash signs, unit gaps, and evaluation-price inequalities persist under a
sufficiently small perturbation that stays in the same guardrail branches.
Thus (11)--(14) exhibit a nonempty strict region, not an isolated equality
slice. They also show that the theorem includes unequal, repeatedly active
floors rather than only the common-floor special case.[^mechanism]

### Evaluation-price control is necessary

Reference alignment plus a completed cash crossing does not imply a win at
\(P=p_n\). Take the strict cycle

\[
p=(1,2/3,1,2),
\qquad \lambda=3/4,
\qquad P=p_4=2.
\tag{15}
\]

Its aligned boundary is \(j=2\), both policies activate the floor at dates
one through three, and

\[
D^0=\left(0,-\frac{11}{240},\frac{101}{1728},
                  \frac{1117}{3456}\right).
\]

Nevertheless

\[
(H_D,U_D)=\left(\frac{889}{864},-\frac{6727}{8640}\right),
\quad \Pi_D=\frac{1270}{961}<2,
\]

and

\[
(H_0,U_0)=\left(\frac{1117}{3456},-\frac{5803}{34560}\right),
\quad \Pi_0=\frac{11170}{5803}<2.
\]

The resulting exact losses are

\[
W^c-W^D=-\frac{1141}{2160},
\qquad
W^c-W^0=-\frac{109}{8640}.
\tag{16}
\]

Thus even strict slopes, reference-aligned differential floors, positive
terminal corrected-minus-neutral cash, repeated activation, and terminal-
purchase-price evaluation do not replace the explicit boundary in (10). The
evaluation condition \(P=p_n\) is favorable only when \(p_n\) lies in the
relevant interval from the affine table.[^weak-valley][^mechanism]

On the same all-floors-active path (11), choosing \(P=2\) instead of \(1/2\)
also lies outside both boundaries and gives

\[
W^c-W^D=-\frac{26387}{28800},
\qquad
W^c-W^0=-\frac{8123}{115200}.
\tag{17}
\]

This same-purchase-ledger reversal isolates the evaluation price: no score,
reference, floor, purchase, cash, or unit changes when \(P\) changes.

### Neither alignment nor terminal-positive cash is necessary

Alignment is sufficient for the cash mechanism but is not necessary for a
wealth win. With

\[
p=(1,2/3,1/2,2/3),
\qquad \lambda=3/4,
\qquad P=p_4=2/3,
\tag{18}
\]

the date-three floor difference violates (7). Same-period score forcing
outweighs the misaligned floor component, and the cash path still has signs
\(-,-,+\). Here

\[
(H_0,U_0)=\left(\frac{841}{149760},\frac{841}{99840}\right),
\]

so the corrected rule beats neutral for every positive \(P\). At the stated
evaluation price it also beats DCA:

\[
W^c-W^D=\frac{389}{18720},
\qquad
W^c-W^0=\frac{841}{74880}.
\tag{19}
\]

This is the exact obstruction to making reference alignment necessary for the
wealth result.[^mechanism]

Nor is (8) necessary. Keep the prices in (18), but take \(\lambda=1/4\).
The corrected and neutral clipped floors are common, so (7) holds at \(j=3\),
while

\[
(H_0,U_0)=\left(-\frac{103}{832},\frac{2003}{8320}\right).
\]

The neutral comparison is therefore a high-evaluation-price win with root
\(1030/2003\), rather than the low-price case in (9). At \(P=p_4=2/3\),

\[
W^c-W^D=\frac{57}{520},
\qquad
W^c-W^0=\frac{229}{6240}.
\tag{20}
\]

This exact aligned joint win with \(H_0<0\) proves that the terminal-positive
subclass is a useful sufficient interpretation, not a necessary description
of every win. The full table, not (8), remains the necessary-and-sufficient
boundary.

### What happens when alignment is dropped

The strict path

\[
p=(1,1/16,1,8),
\quad \lambda=63/64,
\quad(\alpha,\beta)=(-1,0),
\quad P=p_4
\]

has the exact cash-difference signs \(-,+,-\) after the mandatory first-date
tie because repeated policy-specific floors are not reference-aligned. Its
corrected-minus-neutral wealth gap is

\[
-\frac{339578505}{616865792}<0.
\tag{21}
\]

Disabling both floors preserves the scores and removes the second reversal.
This is a visible outside-alignment failure; it is not used to prove the
affine theorem, and its horizon-four minimality concerns the cash mechanism,
not a claim that four dates are special for (3).[^mechanism]

## 5. Boundary cases

### Constant purchase prices and one purchase

If \(p_t=p\) for every purchase date, the corrected relative price is one at
every scored date. Corrected and neutral therefore have identical scores,
floors, purchases, cash, and units, so \(H_0=U_0=0\) and they tie for every
\(P>0\). All intermediate cash-timing coefficients vanish. Against DCA,

\[
W_n^c(P)-W_n^D(P)=C_n^c\left(1-\frac{P}{p}\right),
\]

so corrected wins for \(P<p\), ties for \(P=p\), and loses for \(P>p\),
while retaining the \(\lambda\)-DCA floor. The same statement covers \(n=1\):
the warm-up score makes corrected and neutral identical, and their DCA
break-even evaluation price is the sole purchase price.[^guarded-rule][^accounting]

### Endpoint and flat troughs

The affine theorem does not require an interior or strict trough. The weak
single-valley specialization permits the first trough at date one or at date
\(n\), and permits flat descent, trough, and recovery segments. A flat price
step contributes zero to (2), but cash accumulated on that step still affects
later coefficients and \(H_T\).

For an exact flat endpoint-trough case, take

\[
p=(1,1,1/2,1/2),
\quad \lambda=1/2,
\quad(\alpha,\beta)=(0,-1).
\]

The policies have common clipped floors and an aligned boundary \(j=4\), but

\[
(H_0,U_0)=\left(-\frac{59}{240},\frac{59}{120}\right).
\]

Thus corrected loses to neutral for \(P<1/2\), ties at \(P=1/2=p_n\), and
wins for \(P>1/2\). At the tie it still beats DCA by \(1/4\). This covers a
nontrivial tie with different terminal cash and unit holdings; ties are not
limited to identical policies or constant paths. Interior flat troughs are
classified by the same zero-coefficient rule, whether or not their clipped
floors satisfy (7).[^accounting]

### Active, inactive, and boundary floor branches

Equations (1)--(5) use realized **clipped floor amounts**, so they cover an
active floor, an inactive floor, equality at the clipping boundary, repeated
activation, and policies occupying different branches. Condition (7) compares
amounts rather than activation flags. Example (11) has every floor active and
unequal after the boundary; example (20) has a common floor active only at the
first date; the constant example has repeated active floors followed by
inactive floors. No branch is silently attributed to the corrected score.
The only zero-discretionary boundary under the present positive-deposit family
is the \(\lambda=1\) collapse below.[^mechanism][^guarded-rule]

### The exact safety endpoint \(\lambda=1\)

At \(\lambda=1\), the guardrail forces both guarded selectors to purchase each
deposit exactly as DCA after every history. Their discretionary intervals are
zero, irrelevant corrected references need not be evaluated, and

\[
H_D=U_D=H_0=U_0=0.
\]

All three policies therefore tie for every finite horizon, every positive
purchase path, and every positive evaluation price. This is the DCA collapse,
not a strict member of the \(0<\lambda<1\) region.[^guardrail][^accounting]

## 6. Executable evidence, scope, and unresolved mathematical issue

The public
[performance-boundary report](../../reproducibility/performance_boundary.py)
exposes \(H_T\), \(U_T\), the positive break-even price when one exists, and
classifies every positive evaluation price on any finite positive purchase
path. A separate weak-single-valley analyzer exposes the decline/recovery
specialization only after validating that path class. The analyzers
independently assert that the cash-timing slope equals the direct
terminal-unit difference and, in the valley specialization, that both routes
reconstruct the same terminal-price gap. The named
[performance-boundary check](../../reproducibility/checks/check_arbitrary_horizon_performance_boundary.py)
replays horizons one through eight, evaluation prices below, at, and above a
boundary, an explicit non-valley path, the aligned joint win and loss, the
all-floors-active strict region, the nontrivial exact tie, constant and
endpoint/flat-trough paths, active and inactive floor branches, and the
\(\lambda=1\) collapse. The earlier accounting and cash-mechanism checks
remain independent regression evidence for the two identities used
here.[^accounting][^mechanism]

The proved result is deterministic and pathwise. It gives no probability of a
win, expectation, utility ranking, regret bound, universal dominance,
parameter superiority, or novelty claim. In particular, the strict examples
do not imply that increasing \(\beta\), changing \(\lambda\), or using the
corrected mean generally improves performance. Every loss remains compatible
with inherited \(\lambda\)-DCA safety.[^guardrail]

One mathematical compression remains unresolved: no price-only or
reference-only necessary-and-sufficient condition is known that signs
\((H_T,U_T)\) without executing the relevant purchase ledgers. The exact
affine boundary proves that these two pre-evaluation quantities exactly
determine the realized evaluation-price classification, while the
aligned win, aligned loss, non-necessity, flat-trough, and double-reversal
witnesses show why the cash sign word cannot replace them. Whether their signs
admit a useful simpler characterization in raw prices, deposits, parameters,
and guardrail states is open; it does not leave the every-finite-horizon
boundary in (3) unresolved.[^ticket-04]

[^ticket-04]: [Prove the arbitrary-horizon performance boundary](../../.scratch/smartdca/efforts/arbitrary-horizon-performance/issues/04-prove-arbitrary-horizon-performance-boundary.md)
[^accounting]: [Arbitrary-horizon cash-timing identity and exact-rational verification seam](arbitrary-horizon-accounting-verification-seam.md)
[^mechanism]: [Differential guardrail feedback defeats cash single crossing](cash-single-crossing-mechanism.md)
[^weak-valley]: [Weak single-valley prices do not determine guarded SmartDCA advantage](weak-single-valley-advantage-falsification.md)
[^guarded-rule]: [The guarded corrected-mean SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md)
[^guardrail]: [Epsilon-DCA safety is exactly a causal unit-coverage guardrail](../theorems/epsilon-dca-safety-unit-guardrail.md)
