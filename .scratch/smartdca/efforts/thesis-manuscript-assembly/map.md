# Thesis manuscript assembly effort map

## Contract

The approved problem, outcome requirements, implementation and testing
decisions, and exclusions live in the [effort specification](spec.md). The
project-wide scientific context lives in the
[SmartDCA research map](../../map.md). When selecting or changing a ticket,
follow the [work-tracking workflow](../../../../docs/agents/work-tracking.md).

## Ticket route

| Ticket | Purpose | Status | Dependencies |
|---|---|---|---|
| [01](issues/01-freeze-institutional-contract-establish-manuscript-build.md) | Freeze submission requirements and establish one canonical manuscript-to-PDF seam. | resolved | — |
| [02](issues/02-establish-thesis-architecture-evidence-controls.md) | Create the chapter route and controls that keep every manuscript claim consistent and traceable. | resolved | 01 |
| [03](issues/03-synthesize-dca-adaptive-causal-safety-literature.md) | Position the financial problem and safety architecture against authoritative investment literature. | resolved | 02 |
| [04](issues/04-position-corrected-mean-prior-theory.md) | Establish conservative primary-source positioning for the corrected mean and its proved properties. | resolved | 02 |
| [05](issues/05-synthesize-reproducible-computational-finance-statistics-literature.md) | Ground the preregistered, dependence-aware, reproducible empirical design in authoritative methodology. | resolved | 02 |
| [06](issues/06-draft-financial-model-corrected-signal-foundations.md) | Write the financial model, fair DCA comparison, source audit, and corrected signal foundations. | resolved | 03, 04 |
| [07](issues/07-draft-impossibility-safety-policy-architecture.md) | Write the causal impossibility result, attainable safety relaxation, and guarded adaptive policy. | resolved | 03, 06 |
| [08](issues/08-draft-finite-arbitrary-horizon-boundaries.md) | Write the exact realized-path performance classifications from two purchases through arbitrary horizons. | open | 07 |
| [09](issues/09-draft-empirical-methodology-reproducibility.md) | Write the frozen empirical design, statistical plan, provenance model, and reproduction route. | open | 05, 07 |
| [10](issues/10-draft-deterministic-stochastic-evaluation.md) | Write the reviewed deterministic, adversarial, and seeded-stochastic results with reproducible assets. | open | 08, 09 |
| [11](issues/11-draft-historical-robustness-evaluation.md) | Write the frozen primary historical findings and separately registered robustness evidence. | open | 09 |
| [12](issues/12-synthesize-safety-adaptivity-tradeoff-limitations.md) | Integrate the analytical and empirical evidence into the thesis's central finding and limitations. | open | 10, 11 |
| [13](issues/13-draft-integrative-chapters-abstract.md) | Write the integrative chapters from the stabilized technical and empirical manuscript. | open | 12 |
| [14](issues/14-assemble-complete-manuscript-release.md) | Produce the first complete, internally consistent manuscript release candidate. | open | 13 |
| [15](issues/15-independently-audit-complete-draft.md) | Independently review the complete draft before it enters the supervisor feedback cycle. | open | 14 |
| [16](issues/16-integrate-supervisor-feedback.md) | Obtain, classify, resolve, and verify actual supervisor feedback without changing frozen science silently. | open | 15 |
| [17](issues/17-freeze-final-submission-release.md) | Perform the post-feedback release audit and freeze the submission PDF and archival package. | open | 16 |

## Current frontier

Ticket [01](issues/01-freeze-institutional-contract-establish-manuscript-build.md)
is resolved. It froze authoritative submission requirements and established the
canonical manuscript-to-PDF seam before continuous prose begins. Ticket [02](issues/02-establish-thesis-architecture-evidence-controls.md)
is resolved: the chapter architecture, evidence controls, and canonical structural shell are in place.
Ticket [03](issues/03-synthesize-dca-adaptive-causal-safety-literature.md) is resolved: its bounded
21-source synthesis now fixes the recurring-DCA, adaptive-decision, online-comparator, and safety-objective positioning used by Chapter 2.

Ticket [04](issues/04-position-corrected-mean-prior-theory.md) is resolved: its reviewed primary-source synthesis identifies the corrected construction as a known weighted Bajraktarević mean and separates prior theory from the project's correction, classification, and characterization. Ticket [05](issues/05-synthesize-reproducible-computational-finance-statistics-literature.md) is resolved: its reviewed 15-source synthesis fixes the registration, dependence, multiplicity, reporting, reproducibility, provenance, and release-language boundaries used by Chapter 2. Ticket [06](issues/06-draft-financial-model-corrected-signal-foundations.md) is resolved: Chapter 3 and Appendix A now establish the fair same-deposit model, exact accounting, source-functional audit, corrected construction, homogeneity boundary, and normalized lagged signal on reviewed evidence. Ticket [07](issues/07-draft-impossibility-safety-policy-architecture.md) is resolved: Chapter 4 and Appendix A now connect causal same-deposit dominance impossibility to the sharp epsilon-DCA unit guardrail and a fully funded guarded corrected-mean policy, with the safety claim assigned only to the floor. Ticket 08 is the next unblocked drafting frontier.
Tickets 10 and 11 can likewise draft the synthetic and historical empirical
layers in parallel after their genuine prerequisites resolve. Ticket 16 is an
intentional human gate: actual supervisor feedback and approval cannot be
automated, although an agent may integrate and verify recorded feedback.

Every drafting ticket must keep the manuscript source, bibliography,
claim-to-evidence register, notation register, generated assets, and canonical
build consistent. The effort closes only through ticket 17's independent
post-feedback complete-release review.
