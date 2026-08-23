---
profile: smartdca-okf/0.4
type: research-ticket
title: "Audit whether the source out quasi-Gini functional is a mean"
description: "Resolved research ticket classifying exactly when the source out quasi-Gini functional is a mean."
knowledge_role: operational
status: stable
ticket_type: research
ticket_status: resolved
---
# Audit whether the source out quasi-Gini functional is a mean

Type: research
Status: resolved
Blocked by: none
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

For the out construction in Eq. (70) of *SmartDCA superiority*, determine exactly which mean axioms hold or fail for general positive increasing \(f\) and real parameters. Verify constant-vector behavior, internality, classical-Gini recovery, recovery of the out quasi-Lehmer line, and behavior near \(\alpha=\beta\). Identify source-paper errors, unstated assumptions, and the minimal mathematical requirements any correction must satisfy.

## Comments

- This is the only research ticket authorized to run during initial charting.
- This audit predates the formal Wayfinder ticket workflow. Its original evidence and conclusion are contemporaneous; claim-state, synchronization, and significance-gate steps from the later workflow are not attributed retroactively.
- A later independent [retrospective validation](06-retrospectively-validate-source-audit-and-gate.md) rechecked the source pages, classification proof, counterexamples, and diagonal conclusion without changing the result.
- Subsequent [prior-theory work](03-locate-prior-theory-for-correction.md) showed that the natural common-weight correction is a known weighted Bajraktarević subfamily, not a new mean class. This later positioning does not alter the source-functional audit.

## Answer

The source out functional is a mean on the full positive domain **if and only if**
\(\alpha-\beta=1\) or \(f=\mathrm{id}\). Away from those cases, constant vectors show
that it fails reflexivity and hence internality, even for positive, continuous, strictly
increasing \(f\). Symmetry always holds; continuity, degree-one homogeneity, and
coordinatewise monotonicity do not follow from the source assumptions. The two claimed
special-case reductions are algebraically correct, but a global finite
\(\alpha\to\beta\) extension exists only for \(f=\mathrm{id}\). Full proofs,
counterexamples, and correction requirements are recorded in the
[research note](../../../research/notes/source-out-quasi-gini-audit.md).
