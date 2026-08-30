---
profile: smartdca-okf/0.5
type: theorem
title: "Exact mean classification of the source out quasi-Gini functional"
description: "The source Eq. (70) out functional is a mean exactly when the transform is the identity or the parameter gap is one."
knowledge_role: canonical
status: stable
sources:
  - id: audit
    title: "Audit of the source out quasi-Gini functional"
    resource: research/notes/source-out-quasi-gini-audit
    source_kind: internal
  - id: ticket-01
    title: "Audit whether the source out quasi-Gini functional is a mean"
    resource: .scratch/smartdca/issues/01-audit-source-out-quasi-gini-functional
    source_kind: internal
  - id: ticket-06
    title: "Retrospectively validate the source audit and continuation gate"
    resource: .scratch/smartdca/issues/06-retrospectively-validate-source-audit-and-gate
    source_kind: internal
  - id: source-summary
    title: "Source summary: SmartDCA superiority (arXiv:2308.05200v1)"
    resource: references/summaries/smartdca-superiority-source-paper
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
# Exact mean classification of the source out quasi-Gini functional

## Statement

Fix an arity \(m\ge1\), real parameters with \(d=\alpha-\beta\ne0\), and a positive function \(f:(0,\infty)\to(0,\infty)\). The source paper's out construction[^source-summary]

\[
Q_{\alpha,\beta}^{f}(x_1,\ldots,x_m)
=\left(
\frac{\sum_{i=1}^m x_i f(x_i)^{\alpha-1}}
     {\sum_{i=1}^m f(x_i)^{\beta}}
\right)^{1/d},
\qquad x_i>0,
\]

is a mean on \((0,\infty)^m\) **if and only if** \(d=1\) or \(f(x)=x\) for every \(x>0\).

Separately, the family has a global finite diagonal extension as \(\alpha\to\beta\) — one valid at every positive input vector rather than at particular vectors — **only** for \(f=\mathrm{id}\).[^audit]

## Sharpness

The classification is exact, and it needs no regularity on \(f\). Monotonicity is not used; assuming \(f\) positive and even *strictly* increasing does not extend meanhood beyond the two cases, and \(f(x)=2x\) with \((\alpha,\beta)=(2,0)\) already fails reflexivity on a constant vector. The diagonal obstruction is likewise visible on constant vectors alone, so assigning a value on \(\alpha=\beta\) cannot repair continuity of the general family.[^audit]

## What it establishes and what it does not

This is a mathematical classification, not a report of a missing proof: the noun "mean" is false for a general positive increasing transform away from \(d=1\). It settles reflexivity and internality exactly, and it separately records that continuity, degree-one homogeneity, and coordinatewise monotonicity are each not guaranteed under the source's stated assumptions — coordinatewise monotonicity failing even for \(f=\mathrm{id}\) in a case that *is* a genuine mean.[^audit]

It does not impugn the paper's two algebraic compatibility claims, which are correct: \(f=\mathrm{id}\) gives the classical Gini formula and \(d=1\) gives the paper's out quasi-Lehmer construction.[^audit][^source-summary] It does not choose a repair — that is [the corrected out quasi-Gini mean](../definitions/corrected-out-quasi-gini-mean.md) — and it says nothing about the paper's in construction, which is out of scope.

The proof, the four counterexamples, the property-by-property audit table, and the diagonal limit calculation are in [the audit note](../notes/source-out-quasi-gini-audit.md),[^audit] resolved under [the audit ticket](../../.scratch/smartdca/issues/01-audit-source-out-quasi-gini-functional.md)[^ticket-01] and independently rechecked against the source pages, the classification proof, the counterexamples, and the diagonal argument without change.[^ticket-06]

[^audit]: [Audit of the source out quasi-Gini functional](../notes/source-out-quasi-gini-audit.md)
[^ticket-01]: [Audit whether the source out quasi-Gini functional is a mean](../../.scratch/smartdca/issues/01-audit-source-out-quasi-gini-functional.md)
[^ticket-06]: [Retrospectively validate the source audit and continuation gate](../../.scratch/smartdca/issues/06-retrospectively-validate-source-audit-and-gate.md)
[^source-summary]: [Source summary: SmartDCA superiority (arXiv:2308.05200v1)](../../references/summaries/smartdca-superiority-source-paper.md)
