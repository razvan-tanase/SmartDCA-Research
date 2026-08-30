---
profile: smartdca-okf/0.5
type: definition
title: "The corrected out quasi-Gini mean"
description: "Canonical definition of the numerator-preserving corrected out quasi-Gini mean and its diagonal extension."
knowledge_role: canonical
status: stable
sources:
  - id: ticket-05
    title: "Choose the corrected out quasi-Gini definition"
    resource: .scratch/smartdca/issues/05-choose-corrected-out-quasi-gini-definition
    source_kind: internal
  - id: prior-theory
    title: "Prior theory for the proposed corrected out quasi-Gini normalization"
    resource: research/notes/prior-theory-corrected-out-quasi-gini
    source_kind: internal
  - id: audit
    title: "Audit of the source out quasi-Gini functional"
    resource: research/notes/source-out-quasi-gini-audit
    source_kind: internal
  - id: homogeneity
    title: "Primary-source note: homogeneity of the canonical corrected out quasi-Gini mean"
    resource: research/notes/ticket-07-homogeneity-primary-sources
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
# The corrected out quasi-Gini mean

This is the canonical home of the two-parameter construction this project adopts in place of the source paper's Eq. (70). The construction the paper actually wrote is not defined here as project knowledge, because [the source out-functional mean classification](../theorems/source-out-functional-mean-classification.md) proves it is not a mean over the parameter plane; the paper's own formula is recorded in [its source summary](../../references/summaries/smartdca-superiority-source-paper.md).

## Definition

Let \(f:(0,\infty)\to(0,\infty)\), let the external weights \(w_i>0\), let the inputs \(x_i>0\), and let \(\alpha,\beta\) be real with \(d=\alpha-\beta\). Off the diagonal, for \(d\ne0\),

\[
\widehat G_{\alpha,\beta}^{f,\mathrm{out}}(x;w)
=\left(
\frac{\sum_i w_i x_i f(x_i)^{\alpha-1}}
     {\sum_i w_i x_i^{1-\alpha+\beta}f(x_i)^{\alpha-1}}
\right)^{1/(\alpha-\beta)} .
\]

On the diagonal \(\alpha=\beta=q\), the parameter-continuous function-weighted geometric extension is

\[
\widehat G_{q,q}^{f,\mathrm{out}}(x;w)
=\exp\!\left(
\frac{\sum_i w_i x_i f(x_i)^{q-1}\log x_i}
     {\sum_i w_i x_i f(x_i)^{q-1}}
\right).
\]

Both branches are positive and finite whenever \(f\) is positive and finite, so the definition is total on positive inputs for every real parameter pair.

## Why this normalization

It is the **numerator-preserving** repair: the source numerator is kept exactly and the denominator is rebuilt as the same weighted sum with \(x_i\) replaced by \(x_i^{1-d}\), so that every constant vector maps to its common value.[^ticket-05] That is the minimal change that restores reflexivity, and reflexivity is precisely what the source formula loses.[^audit] Among the smallest common-weight repairs this one was chosen because it also conservatively retains the source's \(\alpha-1=\rho\) score semantics, which is what lets [the guarded SmartDCA rule](guarded-corrected-mean-smartdca-rule.md) inherit the paper's parameter meaning.[^ticket-05]

## Identities it must preserve

Three compatibility requirements are part of the definition's justification, not optional properties:[^ticket-05][^prior-theory]

- with \(f=\mathrm{id}\) it is the classical weighted Gini mean;
- with \(d=1\) it is the weighted source out quasi-Lehmer mean, so the entire quasi-Lehmer line survives the repair; and
- it accepts arbitrary positive external weights rather than only equal weights.

## What this definition does not claim

It is **not a new class of means**. For \(d\ne0\) it is exactly the weighted Bajraktarević mean \(A_{t^{-d},\,t f(t)^{\alpha-1}}\), and its \(d=1\) slice is Beckenbach–Gini–Lehmer; power transforms reduce it to classical weighted Gini means.[^prior-theory] Any contribution has to come from transform-coupled theorems, the correction contrast, or the SmartDCA application — not from meanhood.

Reflexivity, internality, symmetry, and positivity follow from the construction, but continuity, homogeneity, and coordinatewise monotonicity do not: homogeneity holds only on the exceptional locus characterized in [the homogeneity characterization](../theorems/corrected-mean-homogeneity-characterization.md),[^homogeneity] and coordinatewise monotonicity is unresolved for a general increasing transform. Causality alone does not make this repair unique, and no off-slice average-acquisition-cost identity is established for it.[^ticket-05] Choosing this mean does not evade the causal DCA impossibility boundary; see [that theorem](../theorems/causal-dca-dominance-impossibility.md).

The proof that the diagonal branch is the parameter-continuous limit, the counterexamples that rule out weaker repairs, and the literature search behind the Bajraktarević identification are all in the cited evidence notes, which remain the place to look for reasoning rather than statement.

[^ticket-05]: [Choose the corrected out quasi-Gini definition](../../.scratch/smartdca/issues/05-choose-corrected-out-quasi-gini-definition.md)
[^prior-theory]: [Prior theory for the proposed corrected out quasi-Gini normalization](../notes/prior-theory-corrected-out-quasi-gini.md)
[^audit]: [Audit of the source out quasi-Gini functional](../notes/source-out-quasi-gini-audit.md)
[^homogeneity]: [Primary-source note: homogeneity of the canonical corrected out quasi-Gini mean](../notes/ticket-07-homogeneity-primary-sources.md)
