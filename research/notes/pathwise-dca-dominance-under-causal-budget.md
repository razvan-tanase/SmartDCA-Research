---
profile: smartdca-okf/0.4
type: research-note
title: "Pathwise DCA dominance under causal budget feasibility"
description: "Proof that DCA is the unique causal fully funded strategy able to weakly dominate DCA on every path."
knowledge_role: evidence
status: stable
sources:
  - id: ticket-04
    title: "Test pathwise DCA dominance under causal budget feasibility"
    resource: .scratch/smartdca/issues/04-test-pathwise-dca-dominance
    source_kind: internal
  - id: positioning
    title: "Primary-source positioning for pathwise DCA dominance"
    resource: research/notes/pathwise-dca-dominance-primary-sources
    source_kind: internal
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
# Pathwise DCA dominance under causal budget feasibility

Canonical home: [Causal DCA dominance impossibility](../theorems/causal-dca-dominance-impossibility.md). That concept carries the statement and its sharpness; this note carries the induction proof, the accounting identity, and the boundary checks.

## Result

Under the project's fair comparison model, DCA is the unique causal,
long-only, buy-only, fully funded strategy that can weakly dominate DCA in
terminal wealth on **every** finite positive price path and every exogenous
deposit sequence. Consequently, no economically distinct strategy can be
weakly better everywhere and strictly better somewhere.

The obstruction is not a property of the corrected out quasi-Gini mean. It is
an information-and-budget boundary: after any causal decision to leave part of
the currently available deposit uninvested, an admissible continuation can move
the price upward and keep it there. Later investment at that higher price cannot
recover the missed units.

## Model

The canonical statement of this comparison model is the *Statement* section of
[Causal DCA dominance impossibility](../theorems/causal-dca-dominance-impossibility.md);
[the epsilon-DCA guardrail theorem](../theorems/epsilon-dca-safety-unit-guardrail.md) and
[the guarded SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md) both
inherit it by reference rather than restating it. It is written out again below because the
induction proof needs the notation in front of the reader, not because a second definition
is in force.

Fix a known finite horizon with purchase dates \(t=1,\ldots,n\), followed by a
common evaluation date. Let

- \(p_t>0\) be the asset price at purchase date \(t\), and let \(p_{n+1}>0\)
  be its evaluation price;
- \(d_t\ge 0\) be the exogenous cash deposit observed at date \(t\);
- \(x_t\) be the candidate strategy's cash expenditure after observing
  \((p_1,d_1),\ldots,(p_t,d_t)\), but before observing any future price;
- \(C_t\) and \(Q_t\) be cash and asset units immediately after the date-\(t\)
  purchase.

Starting from \(C_0=Q_0=0\), sequential admissibility and full funding mean

\[
0\le x_t\le C_{t-1}+d_t,\qquad
C_t=C_{t-1}+d_t-x_t,\qquad
Q_t=Q_{t-1}+\frac{x_t}{p_t}.
\tag{1}
\]

Cash earns no interest. Terminal wealth includes both components:

\[
W^S=C_n+p_{n+1}Q_n.
\tag{2}
\]

DCA uses \(x_t^D=d_t\), so

\[
W^D=p_{n+1}\sum_{t=1}^n\frac{d_t}{p_t}.
\tag{3}
\]

The strategy may know \(n\). The proof below remains valid even if it is given
the entire future deposit schedule; it may not know future prices.

## Exact terminal-wealth identity

For any realized feasible expenditure schedule,

\[
\boxed{
W^S-W^D
=\sum_{t=1}^n(d_t-x_t)
 \left(1-\frac{p_{n+1}}{p_t}\right).
}
\tag{4}
\]

This is an accounting identity, not a dominance result. The individual
differences \(d_t-x_t\) need not be nonnegative because carried cash can make a
later purchase exceed the current deposit; full funding instead imposes the
prefix conditions

\[
C_t=\sum_{i=1}^t(d_i-x_i)\ge0.
\tag{5}
\]

For a fixed realized path, equality with DCA holds exactly when the right-hand
side of (4) is zero. This allows path-specific coincidences. In particular, if
all purchase prices equal the evaluation price, every feasible spending
schedule has the same terminal wealth as DCA.

## Impossibility and uniqueness theorem

**Theorem.** Fix \(n\ge1\). Let \(S\) be any causal strategy satisfying (1).
If

\[
W^S(p,d)\ge W^D(p,d)
\tag{6}
\]

for every \(p\in(0,\infty)^{n+1}\) and every
\(d\in[0,\infty)^n\), then, after every history,

\[
x_t=d_t,\qquad C_t=0,\qquad
Q_t=\sum_{i=1}^t\frac{d_i}{p_i}.
\tag{7}
\]

Thus \(S\) is DCA transaction by transaction and \(W^S=W^D\) on every path.
There is no non-DCA strategy satisfying economic dominance.

**Proof.** We use induction on the purchase date.

At date \(1\), feasibility gives \(0\le x_1\le d_1\). Write
\(r=d_1-x_1\). If \(r>0\), complete the price path by setting every remaining
purchase price and the evaluation price equal to a constant \(M>p_1\).
At price \(M\), every dollar subsequently deposited or carried has terminal
value exactly one dollar whether it remains cash or is used to buy the asset.
Relative to DCA, the date-1 residual therefore contributes

\[
r-M\frac{r}{p_1}=r\left(1-\frac{M}{p_1}\right)<0
\tag{8}
\]

to terminal wealth. All later deposits have equal terminal value under the two
strategies on this constant continuation, so they cannot offset (8). This
contradicts (6). Hence \(x_1=d_1\), and the states agree after date 1.

Suppose the states agree after every history through date \(t-1\). At an
arbitrary date-\(t\) history, the candidate therefore enters with zero cash and
the same units as DCA. Feasibility gives \(x_t\le d_t\). If
\(r=d_t-x_t>0\), use the same constant continuation with \(M>p_t\). The
terminal gap is again (8), with \(p_t\) in place of \(p_1\), contradicting
(6). Thus \(x_t=d_t\), completing the induction. \(\square\)

The same argument covers randomized strategies if (6) is required for every
realized seed. If (6) is imposed only after averaging over internal
randomization, then (8) contains \(\mathbb E[r]\); because \(r\ge0\), it still
forces \(r=0\) almost surely.

## Equality cases

There are two distinct notions of equality.

1. **Equality on one realized path.** It is characterized exactly by (4):
   \[
   \sum_t(d_t-x_t)(1-p_{n+1}/p_t)=0.
   \]
   Different purchase schedules may satisfy this equation. Flat prices and
   shifts between dates with the same price are immediate examples.
2. **Equality on every admissible path and deposit sequence.** Causality plus
   full funding force (7). Under the stated convention—evaluation occurs after
   the last purchase date—DCA is unique.

This distinction prevents path-specific equalities from being mistaken for an
alternative universal strategy.

## Sharp assumption boundary

The following package cannot be retained while obtaining a nontrivial positive
theorem:

- every finite positive price path;
- causal decisions;
- the same exogenous deposits and horizon;
- no borrowing or leverage;
- terminal wealth including unused cash.

There are two clean one-assumption relaxations.

### Retain every path: relax causality

For a horizon \(n\ge2\), an oracle assigns each deposit \(d_t\) to a date
attaining

\[
m_t=\min_{s=t,\ldots,n}p_s.
\]

The rule is long-only, buy-only, and fully funded, but it uses future prices.
Its units are \(\sum_t d_t/m_t\ge\sum_t d_t/p_t\), so it weakly dominates DCA
on every path and is strict whenever a positive deposit is followed by a
strictly lower purchase price. Equality holds exactly when
\(m_t=p_t\) for every \(t\) with \(d_t>0\).

For \(n=1\), there is no later purchase date, so this oracle coincides with DCA
and cannot supply strict improvement.

Therefore, if **universal pathwise dominance** is non-negotiable, causality is
the precise implementability assumption that must be relaxed (unless one
instead abandons fair funding or the economic terminal-wealth comparator).

### Retain implementability and fairness: relax the path universe

For \(n\ge2\), on the restricted class

\[
p_1\ge p_2\ge\cdots\ge p_n,
\]

the causal horizon-aware rule that carries all cash and buys at date \(n\)
has \((\sum_t d_t)/p_n\) units, at least DCA's
\(\sum_t d_t/p_t\). It is strict whenever some positive deposit arrives at a
price strictly above \(p_n\). For \(n=1\), the rule is DCA. Thus a constructive
causal result becomes possible by restricting the admissible path class. More generally, a practical
SmartDCA claim must replace “every positive path” with a stated deterministic
path condition, stochastic estimand, regret criterion, or utility objective.

## Boundary and numerical checks

- **One purchase date.** Holding \(r>0\) immediately loses
  \(r(M/p_1-1)\) relative to DCA when the evaluation price is \(M>p_1\).
- **Zero deposit.** Once the induction has forced zero carried cash,
  \(d_t=0\) implies \(x_t=0\), as required.
- **Constant prices.** Both cash and asset purchases preserve nominal value, so
  equality is expected and does not identify the strategy.
- **Rising continuation.** With \(d=(100,100)\), purchase prices
  \((10,20)\), and evaluation price \(20\), DCA ends with 15 units and wealth
  300. Waiting and buying 200 at 20 ends with 10 units and wealth 200.
- **Falling continuation.** Reversing the purchase prices to \((20,10)\) and
  evaluating at 10 gives DCA 15 units and wealth 150, while waiting gives 20
  units and wealth 200. The improvement on the falling path is paid for by the
  failure on the rising path.
- **Extreme evaluation prices.** As \(p_{n+1}\downarrow0\), cash retention can
  look favorable; as \(p_{n+1}\uparrow\infty\), any missed units dominate the
  comparison. The theorem needs only finite positive prices, choosing a finite
  \(M>p_t\) at each deviation.

The companion script
[`check_pathwise_dca_dominance.py`](../../reproducibility/checks/check_pathwise_dca_dominance.py)
checks (4), constructs the adversarial witness over a parameter grid, exhausts
deviations after nonempty DCA prefixes with later deposits and trades, exhausts
the oracle rule on small positive price/deposit grids, and exhausts the
wait-until-last rule on nonincreasing paths. These computations test the
algebra and examples; the theorem is established by the proof, not by
enumeration.

The separate
[primary-source positioning note](pathwise-dca-dominance-primary-sources.md)
relates the self-contained result to pointwise no-arbitrage and distinguishes
exact general coverage from regret, competitive-ratio, stochastic, and
restricted-path analogies.

## Implication for the SmartDCA paper

The paper should not claim that a causal, fully funded out-quasi-Gini allocation
economically dominates DCA on every positive path. The strongest honest route
is to make the theorem above the impossibility boundary, then derive positive
results under explicit path classes or stochastic/performance criteria. Lower
average acquisition cost remains only an accounting property unless it is tied
to the same deposits and terminal wealth.

The route the project actually took is the third option in that list — weaken the
criterion, keep every path — and it is now proved as
[the epsilon-DCA unit-coverage guardrail](../theorems/epsilon-dca-safety-unit-guardrail.md),
inside which [the guarded SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md)
spends only the discretion the guardrail leaves free.
