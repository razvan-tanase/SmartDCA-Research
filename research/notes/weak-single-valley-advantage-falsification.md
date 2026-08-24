---
profile: smartdca-okf/0.4
type: research-note
title: "Weak single-valley prices do not determine guarded SmartDCA advantage"
description: "Exact counterexamples showing that weak and strict single-valley paths do not guarantee corrected-rule wealth advantage over DCA or the neutral guarded selector."
knowledge_role: evidence
status: stable
sources:
  - id: ticket-02
    title: "Falsify the weak single-valley advantage conjecture"
    resource: .scratch/smartdca/efforts/arbitrary-horizon-performance/issues/02-falsify-weak-single-valley-advantage
    source_kind: internal
  - id: accounting-seam
    title: "Arbitrary-horizon cash-timing identity and exact-rational verification seam"
    resource: research/notes/arbitrary-horizon-accounting-verification-seam
    source_kind: internal
  - id: experiment
    title: "Exact-rational weak single-valley falsification search"
    resource: reports/experiments/weak-single-valley-falsification
    source_kind: internal
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-24T08:28:53Z
generation_run: urn:uuid:f667d9d5-4345-4a36-b336-a56d37564458
verified:
  - by: openai-codex/standards-review-0.1
    at: 2026-08-24T08:32:57Z
    review_run: urn:uuid:8e47900a-b265-4440-819f-2a5326ed440f
  - by: openai-codex/spec-review-0.1
    at: 2026-08-24T08:32:57Z
    review_run: urn:uuid:a7c4c38d-001a-494a-a8de-cd2211240855
  - by: openai-codex/standards-review-0.1
    at: 2026-08-24T08:38:49Z
    review_run: urn:uuid:8a97bf17-69e6-4d16-bcc0-5755d83d8785
  - by: openai-codex/spec-review-0.1
    at: 2026-08-24T08:38:49Z
    review_run: urn:uuid:96546068-7247-4999-906a-ef18ccb9a474
---
# Weak single-valley prices do not determine guarded SmartDCA advantage

## Answer

Weak single-valley purchase prices alone are insufficient to give the guarded
corrected-mean rule a predictable terminal-wealth advantage over either DCA
or the neutral guarded selector. Exact four-date counterexamples remain after
requiring a genuine strict decline and recovery and fixing the evaluation
price at the final purchase price. This settles the ticket's falsification
question negatively without ranking the corrected rule in general.[^ticket-02]

The complete deterministic search domain, counts, code fingerprints, and all
named replay inputs are preserved in the companion experiment report.[^experiment]

## Independent path class

For positive prices (p=(p_1,\ldots,p_n)), take the first minimum (p_k).
The path is weak single-valley exactly when

\[
p_1\ge\cdots\ge p_k\le\cdots\le p_n.
\tag{1}
\]

Definition (1) uses prices only. A genuine cycle has at least one strict fall
and one strict rise. A strict cycle has an interior trough, strictly falling
prices before it, and strictly rising prices after it. The search validates
this predicate before policy evaluation and again for every retained path.

## Why the DCA conjecture fails on a strict cycle

Choose unit deposits,

\[
p=(1,1/2,2/3,1),\qquad P=1,\qquad
\lambda=1/2,\qquad (\alpha,\beta)=(0,-1).
\tag{2}
\]

This is a strict single-valley cycle and (P=p_4). The exact corrected cash
path returned through the verified scenario seam is

\[
C=(1/4,7/24,31/48,79/80).
\tag{3}
\]

The guardrail floor is active at dates one and two. Applying the independent
cash-timing identity gives[^accounting-seam]

\[
\begin{aligned}
W^{\mathrm{corrected}}-W^{\mathrm{DCA}}
&=\frac14(2-1)
 +\frac7{24}\left(\frac32-2\right)
 +\frac{31}{48}\left(1-\frac32\right)\\
&=\frac14-\frac7{48}-\frac{31}{96}
=-\frac7{32}.
\end{aligned}
\tag{4}
\]

The terminal-cash coefficient vanishes because (P=p_4). Cash retained
through the recovery outweighs the benefit of cash retained before the fall.
Thus genuine recovery, strict slopes, and terminal-price evaluation still do
not determine an advantage over DCA.

## Why the corrected score can lose to the neutral score

Choose instead

\[
p=(1,2/3,1,2),\qquad P=2,\qquad
\lambda=3/4,\qquad (\alpha,\beta)=(0,-1).
\tag{5}
\]

This is also a strict cycle with (P=p_4). The corrected and neutral cash
paths are

\[
C^{\mathrm{corrected}}
=(1/8,11/60,203/432,889/864),
\tag{6}
\]

\[
C^{\mathrm{neutral}}
=(1/8,11/48,79/192,271/384).
\tag{7}
\]

Hence the relevant cash differences are

\[
\Delta C_1=0,\qquad
\Delta C_2=-\frac{11}{240},\qquad
\Delta C_3=\frac{101}{1728}.
\tag{8}
\]

The two-strategy cash-timing identity yields

\[
\begin{aligned}
W^{\mathrm{corrected}}-W^{\mathrm{neutral}}
&=2\Delta C_1\left(\frac32-1\right)
 +2\Delta C_2\left(1-\frac32\right)
 +2\Delta C_3\left(\frac12-1\right)\\
&=\frac{11}{240}-\frac{101}{1728}
=-\frac{109}{8640}.
\end{aligned}
\tag{9}
\]

Both policies activate the floor at dates one through three. Their floors are
equal through date two, where the corrected score first changes the purchase,
but differ at date three: (27/80) for corrected and (13/32) for neutral.
An exact replay with both guardrail floors disabled gives

\[
\left(W^{\mathrm{corrected}}-W^{\mathrm{neutral}}\right)_{\mathrm{no\ floor}}
=\frac{49}{360}.
\tag{10}
\]

Thus enabling the floors changes the score gap by

\[
-\frac{109}{8640}-\frac{49}{360}
=-\frac{257}{1728}.
\tag{11}
\]

The nonzero counterfactual difference establishes that guardrail activation
contributes here, and its magnitude shows that it reverses the sign. The
effect is therefore not attributed to the corrected reference alone.

## Minimized boundary and finite evidence

Under the declared ordering, the smallest corrected-vs-DCA loss is the
constant four-date path ((1,1,1,1)) at (P=2), with gap (-7/8). It is a
valid weak path but has no corrected-score effect: corrected and neutral
coincide, including their floor paths. The smallest corrected-vs-neutral loss
is ((1,2/3,2/3,2/3)) at (P=1/3), with gap (-273/5984); their first
differing clipped floor occurs at date three. Disabling both floors changes
that gap to (-373/5984), an exact floor contribution of (+25/1496). Both
use unit deposits, (lambda=1/2), and
((\alpha,\beta)=(0,-1)).[^experiment]

The broader run evaluates 61,398 exact scenarios and finds losses in both
comparisons at every evaluation multiplier. On the most restrictive recorded
slice—strict cycles with (P=p_n)—261 of 270 scenarios lose to DCA and 43 of
270 lose to neutral. These ratios are not probabilities and do not show that
the corrected rule is generally inferior. They show that excluding flat and
endpoint cases does not rescue either universal conjecture.

## Consequence for the research route

Single-valley geometry controls the signs of the cash-timing coefficients but
not the magnitudes or crossing pattern of the corrected cash path. A useful
positive boundary therefore needs additional observable structure. The next
ticket should test the proposed cash-path single-crossing mechanism and
separate discretionary-score behavior from repeated floor activation. This
note does not assume that mechanism, propose a theorem for it, or advance the
later boundary ticket.

The inherited epsilon-DCA safety result is unaffected. A relative safety
floor and a strict terminal-wealth advantage are different claims; the
counterexamples falsify only the latter.

[^ticket-02]: [Falsify the weak single-valley advantage conjecture](../../.scratch/smartdca/efforts/arbitrary-horizon-performance/issues/02-falsify-weak-single-valley-advantage.md)
[^accounting-seam]: [Arbitrary-horizon cash-timing identity and exact-rational verification seam](arbitrary-horizon-accounting-verification-seam.md)
[^experiment]: [Exact-rational weak single-valley falsification search](../../reports/experiments/weak-single-valley-falsification.md)
