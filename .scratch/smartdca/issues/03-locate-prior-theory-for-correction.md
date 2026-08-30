---
profile: smartdca-okf/0.5
type: research-ticket
title: "Locate prior theory for a corrected out quasi-Gini mean"
description: "Resolved research ticket locating prior theory for the corrected out quasi-Gini normalization."
knowledge_role: operational
status: stable
ticket_type: research
ticket_status: resolved
---
# Locate prior theory for a corrected out quasi-Gini mean

Type: research
Status: resolved
Blocked by: 02
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

Which primary sources on classical Gini means, Beckenbach-Gini-Lehmer means, weighted power means, and related generalized means already cover any candidate normalization or its required properties, and what genuinely novel mathematical space remains?

## Comments

- Claimed after the user accepted the source audit at its significance gate.
- Search primary mathematical sources and separate exact prior coverage from analogies or naming similarities.
- Verified the decisive identification algebraically, including constants, both required boundary cases, a nontrivial internal example, and the two-sided diagonal limit.
- The search was targeted rather than exhaustive; it supports safe positioning, not an absolute novelty claim.

## Answer

The natural common-weight normalization is not a new mean class. For
\(d=\alpha-\beta\ne0\), it is exactly the weighted Bajraktarević mean
\(A_{t^{-d},\,t f(t)^{\alpha-1}}\). Its \(d=1\) slice is the
Beckenbach--Gini--Lehmer/out quasi-Lehmer form, every power transform reduces to
a classical weighted Gini mean after a parameter change, and its diagonal is a
function-weighted geometric Bajraktarević mean.

Prior theory therefore already covers the construction's meanhood, external
weights, classical diagonal and parameter results, and broad comparison,
equality, and homogeneity questions. The definition itself cannot carry a
novelty claim. The defensible remaining space is a theorem for the family coupled
across parameters by one fixed transform, a correction theorem contrasting its
finite diagonal with the source functional's failure, sharp specialized property
regions, and the causal/budget-feasible SmartDCA application. See the
[primary-source research note](../../../research/notes/prior-theory-corrected-out-quasi-gini.md).
