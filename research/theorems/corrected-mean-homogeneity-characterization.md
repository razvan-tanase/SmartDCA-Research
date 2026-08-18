---
profile: smartdca-okf/0.3
type: theorem
title: "Homogeneity characterization of the corrected out quasi-Gini mean"
description: "The corrected mean is degree-one homogeneous exactly when the transform cancels or is normalized-multiplicative, hence a power under project regularity."
knowledge_role: canonical
status: stable
sources:
  - id: homogeneity
    title: "Primary-source note: homogeneity of the canonical corrected out quasi-Gini mean"
    resource: research/notes/ticket-07-homogeneity-primary-sources
    source_kind: internal
  - id: ticket-07
    title: "Characterize homogeneity of the corrected out quasi-Gini mean"
    resource: .scratch/smartdca/issues/07-characterize-homogeneity-of-corrected-out-quasi-gini
    source_kind: internal
  - id: prior-theory
    title: "Prior theory for the proposed corrected out quasi-Gini normalization"
    resource: research/notes/prior-theory-corrected-out-quasi-gini
    source_kind: internal
generated:
  by: claude-code/smartdca-wiki-0.1
  at: 2026-08-16T09:40:00Z
generation_run: urn:uuid:efe6420b-e236-40b6-96d4-c92a95d505d2
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T09:48:00Z
    review_run: urn:uuid:d037e1ce-def8-4614-a42d-6053d0d49415
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T10:32:00Z
    review_run: urn:uuid:6e8b3b72-0624-46b2-91ff-071b4879d9d4
---
# Homogeneity characterization of the corrected out quasi-Gini mean

## Statement

Take [the corrected out quasi-Gini mean](../definitions/corrected-out-quasi-gini-mean.md) with positive external weights and at least two coordinates carrying positive weight. Homogeneity means \(M(cx;w)=cM(x;w)\) for every \(c>0\), with the weights held fixed. Then:[^homogeneity]

- at a fixed off-diagonal parameter point (\(d=\alpha-\beta\ne0\)) the mean is degree-one homogeneous **iff** \(\alpha=1\), or \(f/f(1)\) is multiplicative;
- at a fixed diagonal point \(\alpha=\beta=q\) it is degree-one homogeneous **iff** \(q=1\), or \(f/f(1)\) is multiplicative;

where normalized multiplicativity means \(f(xy)/f(1)=\bigl(f(x)/f(1)\bigr)\bigl(f(y)/f(1)\bigr)\) for all \(x,y>0\).

Consequently homogeneity at any single non-exceptional parameter point forces normalized multiplicativity, and therefore makes the *entire* two-parameter family homogeneous. Under any of monotonicity, measurability, or continuity, normalized multiplicativity forces the power form \(f(t)=Ct^{r}\) with \(C>0\), so a non-power increasing transform is homogeneous exactly on the transform-blind locus \(\alpha=1\), including the diagonal point \((1,1)\).

## Sharpness and its cost

The criterion is exact and needs no regularity: without a regularity assumption the correct conclusion is normalized multiplicativity, not the power form, because pathological non-linear additive functions produce homogeneous and potentially discontinuous means outside the continuous Gini classification.[^homogeneity]

The consequence for this project is deliberately unflattering. In the power case the corrected mean *is* a reparameterized classical weighted Gini mean, \(\widehat G^{f,\mathrm{out}}_{\alpha,\beta}=G_{p,s}\) with \(p=1+r(\alpha-1)\) and \(s=p-d\).[^homogeneity][^prior-theory] So one transform can make the whole family homogeneous only by collapsing it onto known theory: scale invariance and transform novelty cannot be had at once. That is why [the guarded SmartDCA rule](../definitions/guarded-corrected-mean-smartdca-rule.md) obtains currency-scale invariance by normalizing its inputs rather than by assuming the mean is homogeneous.

## What it does not establish

The exceptional locus \(\alpha=1\) is transform-blind precisely because \(f^{0}=1\) there, so it carries no transform novelty either. The necessity argument needs two effective support points: for a single coordinate homogeneity is automatic, and zero weights can reduce effective arity below the hypothesis. The claim is invariance under rescaling the inputs only; it says nothing about rescaling or endogenizing the weights. The diagonal statement concerns the stated geometric extension and does not independently prove that this extension is the pathwise \(d\to0\) limit.[^homogeneity]

No novelty is claimed. The exact weighted specialization was not located verbatim in the literature, but it is an elementary corollary in a mature theory: Aczél–Daróczy classify homogeneous Bajraktarević *mappings* as Gini mappings under continuity hypotheses, and the two-point ratio argument is what forces this project's normalized transform condition.[^homogeneity] The literature coverage behind that positioning is focused rather than an exhaustive novelty search.[^prior-theory]

The proof, the exact weighted specialization, the fixed-point-versus-family table, and the seven recorded limitations are in [the homogeneity note](../notes/ticket-07-homogeneity-primary-sources.md),[^homogeneity] resolved under [its ticket](../../.scratch/smartdca/issues/07-characterize-homogeneity-of-corrected-out-quasi-gini.md).[^ticket-07] The executable check is [`check_corrected_out_quasi_gini_homogeneity.py`](../../reproducibility/checks/check_corrected_out_quasi_gini_homogeneity.py).

[^homogeneity]: [Primary-source note: homogeneity of the canonical corrected out quasi-Gini mean](../notes/ticket-07-homogeneity-primary-sources.md)
[^ticket-07]: [Characterize homogeneity of the corrected out quasi-Gini mean](../../.scratch/smartdca/issues/07-characterize-homogeneity-of-corrected-out-quasi-gini.md)
[^prior-theory]: [Prior theory for the proposed corrected out quasi-Gini normalization](../notes/prior-theory-corrected-out-quasi-gini.md)
