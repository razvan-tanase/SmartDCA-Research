---
profile: smartdca-okf/0.5
type: theorem
title: "Epsilon-DCA safety is exactly a causal unit-coverage guardrail"
description: "Universal relative-wealth safety, prefix unit coverage, and a sharp per-purchase floor are equivalent, and the floor is always feasible."
knowledge_role: canonical
status: stable
sources:
  - id: guardrail
    title: "Sharp causal epsilon-DCA safety and its unit-coverage guardrail"
    resource: research/notes/sharp-epsilon-dca-safety-guardrail
    source_kind: internal
  - id: ticket-09
    title: "Prove the sharp epsilon-DCA safety guardrail"
    resource: .scratch/smartdca/issues/09-prove-sharp-epsilon-dca-safety-guardrail
    source_kind: internal
  - id: ticket-08
    title: "Audit the novelty of the causal DCA boundary and choose a constructive relaxation"
    resource: .scratch/smartdca/issues/08-audit-causal-dca-novelty-and-relaxation
    source_kind: internal
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-16T11:00:00Z
generation_run: urn:uuid:15b108f2-1ab8-4916-965a-89faffe7b3f6
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T09:48:00Z
    review_run: urn:uuid:d037e1ce-def8-4614-a42d-6053d0d49415
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T10:32:00Z
    review_run: urn:uuid:6e8b3b72-0624-46b2-91ff-071b4879d9d4
  - by: openai-codex/smartdca-wiki-0.1
    at: 2026-08-16T11:14:00Z
    review_run: urn:uuid:5fdc289a-b5ff-4e1f-9d84-777c58a093f2
---
# Epsilon-DCA safety is exactly a causal unit-coverage guardrail

## Statement

Work in the same model as [the causal DCA dominance impossibility](causal-dca-dominance-impossibility.md): causal, long-only, buy-only, fully funded purchases, cash carried without interest, terminal wealth including cash. Fix \(\lambda=1-\varepsilon\in(0,1]\) and write \(A_t=Q_t^{DCA}=\sum_{i\le t}d_i/p_i\). For a causal fully funded strategy the following are **equivalent**:[^guardrail]

1. \(W^S\ge\lambda W^{DCA}\) for every finite positive price path and every nonnegative deposit sequence;
2. \(Q_t\ge\lambda A_t\) after every reachable history and every \(t\);
3. after every history the purchase satisfies \(x_t\ge m_t(\lambda):=\bigl[\lambda d_t-p_t(Q_{t-1}-\lambda A_{t-1})\bigr]_+\).

The floor is always feasible: \(0\le m_t(\lambda)\le\lambda d_t\le d_t\le C_{t-1}+d_t\). Hence every \(\lambda\)-safe strategy, and only such a strategy, can be written after each history as \(x_t=m_t(\lambda)+a_t\bigl(C_{t-1}+d_t-m_t(\lambda)\bigr)\) with an arbitrary causal score \(a_t\in[0,1]\). That representation is the complete discretionary interface: the guardrail supplies the guarantee and the score controls only what is left.

## Sharpness

The factor is exact, not merely sufficient. For any fixed strategy and horizon, the worst-case wealth ratio equals the worst-case prefix unit-coverage ratio,

\[
\Gamma(S)=\inf_{\text{admissible paths}}\frac{W^S}{W^{DCA}}
=\inf_{\substack{\text{reachable }h_t\\ A_t>0}}\frac{Q_t(h_t)}{A_t(h_t)} ,
\]

because the adversarial continuation that sets remaining purchase prices to \(P^2\) and the evaluation price to \(P\) makes cash and future units negligible against any chosen prefix as \(P\to\infty\).[^guardrail]

The two endpoints are sharp in opposite directions. At \(\lambda=1\) the floor forces \(x_t=d_t\) at every date, so 1-DCA safety uniquely recovers DCA and reproduces the impossibility boundary. For every \(0<\lambda<1\) a non-DCA safe strategy exists — the fixed reserve rule \(x_t=\lambda d_t\), whose ratio tends to exactly \(\lambda\) as the evaluation price grows, so no larger uniform factor is valid for it. This positive tolerance is what buys a nontrivial discretionary budget, and it is the relaxation ticket 08 selected.[^ticket-08]

## What it does not establish

Epsilon-DCA safety is a uniform relative-wealth **floor**, not dominance and
not near-superiority: for \(\varepsilon>0\) the strategy may end below DCA on
a given path, only never below the \(\lambda\) fraction. This theorem alone
does not show that any corrected-mean score improves on DCA; it separates the
guardrail's guarantee from the score's allocation. The
[guarded SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md)
supplies that score, and
[its two-purchase boundary](two-purchase-guarded-smartdca-boundary.md)
now identifies exact realized strict-win and strict-loss regions without
claiming universal, arbitrary-horizon, or stochastic improvement.[^guardrail]

Boundary behaviour is recorded rather than glossed: before the first positive deposit the floor is zero and the guarantee is trivial; if all deposits are zero both wealths are zero; on constant prices every fully funded allocation ties, so a single flat path identifies neither DCA nor the guardrail; and as \(\lambda\downarrow0\) the statement degenerates to \(W^S\ge0\). Novelty is not claimed — ticket 08's audit found no exact published DCA statement of this characterization, but non-discovery is not proof, so it stays positioned as a DCA-specific robust-superhedging result pending a broader citation review with the manuscript.[^guardrail][^ticket-08]

The equivalence proof in both directions, the adversarial continuation, the exact worst-case factor, the boundary cases, and the numerical example are in [the guardrail note](../notes/sharp-epsilon-dca-safety-guardrail.md),[^guardrail] resolved under [its ticket](../../.scratch/smartdca/issues/09-prove-sharp-epsilon-dca-safety-guardrail.md).[^ticket-09] The executable check is [`check_epsilon_dca_safety_guardrail.py`](../../reproducibility/checks/check_epsilon_dca_safety_guardrail.py).

[^guardrail]: [Sharp causal epsilon-DCA safety and its unit-coverage guardrail](../notes/sharp-epsilon-dca-safety-guardrail.md)
[^ticket-09]: [Prove the sharp epsilon-DCA safety guardrail](../../.scratch/smartdca/issues/09-prove-sharp-epsilon-dca-safety-guardrail.md)
[^ticket-08]: [Audit the novelty of the causal DCA boundary and choose a constructive relaxation](../../.scratch/smartdca/issues/08-audit-causal-dca-novelty-and-relaxation.md)
