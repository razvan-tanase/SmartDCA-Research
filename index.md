---
okf_version: "0.2"
---
# SmartDCA knowledge index

This is the complete inventory of the repository-root knowledge bundle. Its active
profile is `smartdca-okf/0.3`, defined normatively in
[the SmartDCA OKF profile](docs/knowledge/okf-profile.md). Entries are grouped first by
knowledge role and then by concept type; within the canonical role, stable concepts
precede every other lifecycle state. [`README.md`](README.md) is the human
introduction, [the Wayfinder map](.scratch/smartdca/map.md) is the active research
frontier, and [`log.md`](log.md) is the immutable event history.

Trust and provenance are concise discovery hints. The concept itself carries the
authoritative metadata.

## Canonical


### domain-glossary

- [Quasi-Gini SmartDCA Research](CONTEXT.md) — Canonical mathematical, financial, and knowledge-system vocabulary with its forbidden alternatives. — type: domain-glossary; status: stable; trust: reviewed 2026-08-16; provenance: cites internal concepts

### specification

- [SmartDCA Open Knowledge Format profile](docs/knowledge/okf-profile.md) — Normative smartdca-okf/0.3 profile specializing Open Knowledge Format v0.2 for this bundle. — type: specification; status: stable; trust: reviewed 2026-08-16; provenance: cites the fingerprinted OKF v0.2 snapshot and internal concepts

### decision-record

- [Keep research state and evidence in separate versioned layers](docs/adr/0001-versioned-research-layout.md) — Decision keeping map state, detailed reasoning, and executable evidence in separate versioned layers. — type: decision-record; status: stable; trust: reviewed 2026-08-16; provenance: original record, Git history
- [Make the repository root an OKF knowledge bundle](docs/adr/0002-repository-root-okf-knowledge-bundle.md) — Decision making the repository root itself the conformant OKF v0.2 knowledge bundle. — type: decision-record; status: stable; trust: reviewed 2026-08-16; provenance: original record, Git history
- [Separate document kind, authority, lifecycle, and trust](docs/adr/0003-separate-knowledge-authority-and-trust.md) — Decision keeping type, knowledge role, OKF lifecycle, and review trust as independent axes. — type: decision-record; status: stable; trust: reviewed 2026-08-16; provenance: original record, Git history
- [Preserve path-based concept identity through supersession](docs/adr/0004-preserve-path-based-concept-identity.md) — Decision preserving path-based Concept IDs and replacing concepts through supersession, never moves. — type: decision-record; status: stable; trust: reviewed 2026-08-16; provenance: original record, Git history
- [Assign source-summary and synthesis paths in profile 0.2](docs/adr/0005-assign-source-summary-and-synthesis-paths.md) — Decision assigning ingest summary and synthesis paths and relabelling the bundle as smartdca-okf/0.2. — type: decision-record; status: stable; trust: reviewed 2026-08-16; provenance: original record, Git history
- [Assign definition, theorem, and experiment-report paths in profile 0.3](docs/adr/0006-assign-definition-theorem-and-experiment-report-paths.md) — Decision assigning the three remaining semantic type paths and relabelling the bundle as smartdca-okf/0.3. — type: decision-record; status: stable; trust: reviewed 2026-08-16; provenance: original record, Git history

### definition

- [The corrected out quasi-Gini mean](research/definitions/corrected-out-quasi-gini-mean.md) — Canonical definition of the numerator-preserving corrected out quasi-Gini mean and its diagonal extension. — type: definition; status: stable; trust: reviewed 2026-08-16; provenance: cites internal tickets and evidence notes
- [The guarded corrected-mean SmartDCA rule](research/definitions/guarded-corrected-mean-smartdca-rule.md) — Canonical definition of the guarded SmartDCA rule: the epsilon-DCA safety floor plus the bounded corrected-mean score inside it. — type: definition; status: stable; trust: reviewed 2026-08-16; provenance: cites internal tickets and evidence notes

### theorem

- [Exact mean classification of the source out quasi-Gini functional](research/theorems/source-out-functional-mean-classification.md) — The source Eq. (70) out functional is a mean exactly when the transform is the identity or the parameter gap is one. — type: theorem; status: stable; trust: reviewed 2026-08-16; provenance: cites the audit evidence and the ingested source summary
- [Causal DCA dominance impossibility](research/theorems/causal-dca-dominance-impossibility.md) — DCA is the unique causal fully funded strategy that can weakly dominate DCA in terminal wealth on every positive price path. — type: theorem; status: stable; trust: reviewed 2026-08-16; provenance: cites internal proof and positioning evidence
- [Epsilon-DCA safety is exactly a causal unit-coverage guardrail](research/theorems/epsilon-dca-safety-unit-guardrail.md) — Universal relative-wealth safety, prefix unit coverage, and a sharp per-purchase floor are equivalent, and the floor is always feasible. — type: theorem; status: stable; trust: reviewed 2026-08-16; provenance: cites internal proof evidence and its relaxation ticket
- [Homogeneity characterization of the corrected out quasi-Gini mean](research/theorems/corrected-mean-homogeneity-characterization.md) — The corrected mean is degree-one homogeneous exactly when the transform cancels or is normalized-multiplicative, hence a power under project regularity. — type: theorem; status: stable; trust: reviewed 2026-08-16; provenance: cites internal proof and primary-source evidence
- [Two-purchase guarded SmartDCA has an exact DCA boundary](research/theorems/two-purchase-guarded-smartdca-boundary.md) — The two-purchase guarded rule beats DCA exactly below an explicit affine evaluation-price boundary, with a sharp neutral-score comparison. — type: theorem; status: stable; trust: reviewed 2026-08-16; provenance: cites internal proof evidence and its ticket
- [Three-purchase guarded SmartDCA has an exact beta-sensitive DCA boundary](research/theorems/three-purchase-corrected-mean-effect.md) — At three purchases the DCA wealth boundary depends on beta only through the first two-input corrected reference and can flip exactly. — type: theorem; status: stable; trust: reviewed 2026-08-16; provenance: cites internal proof evidence and its ticket

### synthesis

- [Conflicts across the OKF foundation sources](research/synthesis/okf-foundation-source-conflicts.md) — Cross-source integration of the five foundation sources and the four divergences the local profile has to resolve. — type: synthesis; status: stable; trust: reviewed 2026-08-16; provenance: cites the five ingested source summaries and the local profile

## Evidence

### source-summary

- [Source summary: Karpathy's LLM Wiki proposal](references/summaries/karpathy-llm-wiki.md) — Summary of the LLM Wiki gist that proposes an LLM-maintained persistent wiki over immutable raw sources. — type: source-summary; status: stable; trust: reviewed 2026-08-16; provenance: fingerprinted external snapshot, bytes not redistributable
- [Source summary: Open Knowledge Format v0.2 specification](references/summaries/okf-v0-2-specification.md) — Summary of the normative OKF v0.2 specification, its conformance criteria, and its optional metadata families. — type: source-summary; status: stable; trust: reviewed 2026-08-16; provenance: fingerprinted external snapshot, bytes preserved
- [Source summary: Google's OKF v0.2 trust-signals article](references/summaries/okf-v0-2-trust-signals-article.md) — Summary of the non-normative Google Cloud article explaining why OKF v0.2 adds provenance, trust, and attestation. — type: source-summary; status: stable; trust: reviewed 2026-08-16; provenance: fingerprinted external snapshot, origin not byte-reproducible
- [Source summary: the OKF knowledge-catalog examples and reference implementation](references/summaries/okf-reference-implementation-and-examples.md) — Summary of the official OKF reference producer, visualizer, and sample bundles, and what their conventions do not settle. — type: source-summary; status: stable; trust: reviewed 2026-08-16; provenance: two fingerprinted external snapshots, bytes preserved
- [Source summary: the original OKF announcement (historical v0.1 context)](references/summaries/okf-v0-1-announcement.md) — Summary of the June 2026 OKF v0.1 announcement, retained as historical context superseded by v0.2. — type: source-summary; status: stable; trust: reviewed 2026-08-16; provenance: fingerprinted external snapshot, origin not byte-reproducible
- [Source summary: SmartDCA superiority (arXiv:2308.05200v1)](references/summaries/smartdca-superiority-source-paper.md) — Summary of the source paper this project audits, its six theorems, its price-per-unit criterion, and what it does not settle. — type: source-summary; status: stable; trust: reviewed 2026-08-16; provenance: fingerprinted external snapshot, bytes preserved, import-time retrieval

### research-note

- [A guarded corrected-mean SmartDCA rule](research/notes/guarded-corrected-mean-smartdca.md) — The canonical guarded corrected-mean score inside the epsilon-DCA guardrail with exact accounting. — type: research-note; status: stable; trust: reviewed 2026-08-16; provenance: cites internal concepts
- [Primary-source positioning for pathwise DCA dominance](research/notes/pathwise-dca-dominance-primary-sources.md) — Primary-source review placing the causal DCA obstruction inside pointwise no-arbitrage theory. — type: research-note; status: stable; trust: reviewed 2026-08-16; provenance: cites internal concepts and declared scope
- [Pathwise DCA dominance under causal budget feasibility](research/notes/pathwise-dca-dominance-under-causal-budget.md) — Proof that DCA is the unique causal fully funded strategy able to weakly dominate DCA on every path. — type: research-note; status: stable; trust: reviewed 2026-08-16; provenance: cites internal concepts
- [Prior theory for the proposed corrected out quasi-Gini normalization](research/notes/prior-theory-corrected-out-quasi-gini.md) — Primary-source positioning identifying the corrected normalization as a known weighted Bajraktarevic mean. — type: research-note; status: stable; trust: reviewed 2026-08-16; provenance: cites internal concepts and declared scope
- [Sharp causal epsilon-DCA safety and its unit-coverage guardrail](research/notes/sharp-epsilon-dca-safety-guardrail.md) — Proof that universal epsilon-DCA safety is exactly a causal cumulative-unit coverage guardrail. — type: research-note; status: stable; trust: reviewed 2026-08-16; provenance: cites internal concepts
- [Audit of the source out quasi-Gini functional](research/notes/source-out-quasi-gini-audit.md) — Proof that the source Eq. (70) out construction is a mean exactly when f is the identity or alpha minus beta is one. — type: research-note; status: stable; trust: reviewed 2026-08-16; provenance: cites internal concepts and declared scope
- [Primary-source note: homogeneity of the canonical corrected out quasi-Gini mean](research/notes/ticket-07-homogeneity-primary-sources.md) — Characterization of when the corrected mean is degree-one homogeneous, with its source hypotheses. — type: research-note; status: stable; trust: reviewed 2026-08-16; provenance: cites internal concepts and declared scope
- [Primary-source audit of the causal DCA boundary and constructive relaxations](research/notes/ticket-08-causal-dca-novelty-primary-sources.md) — Novelty audit positioning the causal DCA boundary and ordering the admissible constructive relaxations. — type: research-note; status: stable; trust: reviewed 2026-08-16; provenance: cites internal concepts and declared scope
- [Exact two-purchase DCA win/loss boundary](research/notes/two-purchase-dca-win-loss-boundary.md) — Derivation of the necessary-and-sufficient two-purchase wealth boundary and exact neutral-score comparison. — type: research-note; status: stable; trust: reviewed 2026-08-16; provenance: cites internal concepts
- [Exact three-purchase corrected-mean effect](research/notes/three-purchase-corrected-mean-effect.md) — Derivation of the exact three-purchase DCA boundary and an all-rational beta-driven classification flip. — type: research-note; status: stable; trust: reviewed 2026-08-16; provenance: cites internal concepts

## Operational

### agent-instructions

- [Agent contract](AGENTS.md) — Root invariant contract every agent reads before changing SmartDCA work or knowledge. — type: agent-instructions; status: stable; trust: unreviewed; provenance: original record, Git history
- [Domain documentation](docs/agents/domain.md) — Single-context rule for reading the glossary and ADRs before domain work. — type: agent-instructions; status: stable; trust: unreviewed; provenance: original record, Git history

### workflow

- [Issue tracker: Local Markdown](docs/agents/issue-tracker.md) — Where research maps, tickets, and their state fields live and how they are named. — type: workflow; status: stable; trust: unreviewed; provenance: original record, Git history
- [SmartDCA LLM-Wiki workflow](docs/agents/llm-wiki-workflow.md) — How agents author, ingest, promote, review, and supersede knowledge in the wiki. — type: workflow; status: stable; trust: reviewed 2026-08-16; provenance: original record, Git history
- [Wayfinder ticket workflow](docs/agents/wayfinder-ticket-workflow.md) — Authoritative ticket lifecycle from orientation through the user significance gate. — type: workflow; status: stable; trust: unreviewed; provenance: original record, Git history

### domain-glossary

- [Triage labels](docs/agents/triage-labels.md) — Operational mapping from canonical triage roles to this project's labels. — type: domain-glossary; status: stable; trust: unreviewed; provenance: original record, Git history

### research-map

- [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](.scratch/smartdca/map.md) — Authoritative Wayfinder map holding the destination, settled decisions, and active research frontier. — type: research-map; status: stable; trust: unreviewed; provenance: Git history

### research-ticket

- [Audit whether the source out quasi-Gini functional is a mean](.scratch/smartdca/issues/01-audit-source-out-quasi-gini-functional.md) — Resolved research ticket classifying exactly when the source out quasi-Gini functional is a mean. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Decide whether the source-audit gap is significant enough to continue](.scratch/smartdca/issues/02-assess-source-audit-significance.md) — Resolved grilling ticket accepting the source-audit gap as significant enough to continue. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Locate prior theory for a corrected out quasi-Gini mean](.scratch/smartdca/issues/03-locate-prior-theory-for-correction.md) — Resolved research ticket locating prior theory for the corrected out quasi-Gini normalization. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Test pathwise DCA dominance under causal budget feasibility](.scratch/smartdca/issues/04-test-pathwise-dca-dominance.md) — Resolved research ticket testing pathwise DCA dominance under causal budget feasibility. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Choose the corrected out quasi-Gini definition](.scratch/smartdca/issues/05-choose-corrected-out-quasi-gini-definition.md) — Resolved prototype ticket choosing the canonical corrected out quasi-Gini definition. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Retrospectively validate the source audit and continuation gate](.scratch/smartdca/issues/06-retrospectively-validate-source-audit-and-gate.md) — Resolved task ticket retrospectively validating the source audit and its continuation gate. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Characterize homogeneity of the corrected out quasi-Gini mean](.scratch/smartdca/issues/07-characterize-homogeneity-of-corrected-out-quasi-gini.md) — Resolved research ticket characterizing homogeneity of the corrected out quasi-Gini mean. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Audit the novelty of the causal DCA boundary and choose a constructive relaxation](.scratch/smartdca/issues/08-audit-causal-dca-novelty-and-relaxation.md) — Resolved research ticket auditing causal DCA novelty and choosing a constructive relaxation. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Prove the sharp epsilon-DCA safety guardrail](.scratch/smartdca/issues/09-prove-sharp-epsilon-dca-safety-guardrail.md) — Resolved task ticket proving the sharp epsilon-DCA safety guardrail and its unit-coverage form. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Choose the guarded corrected-mean SmartDCA score](.scratch/smartdca/issues/10-choose-guarded-corrected-mean-score.md) — Resolved task ticket choosing the guarded corrected-mean SmartDCA score. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Characterize the two-purchase DCA win/loss boundary](.scratch/smartdca/issues/11-characterize-two-purchase-dca-win-loss-boundary.md) — Resolved task ticket characterizing the two-purchase DCA win/loss boundary. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Design a repository-root LLM-Wiki using OKF v0.2](.scratch/smartdca/issues/12-design-repository-root-llm-wiki-okf.md) — Resolved grilling ticket designing the repository-root LLM-Wiki as an OKF v0.2 knowledge bundle. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Implement the SmartDCA OKF profile and report-only validator](.scratch/smartdca/issues/13-implement-smartdca-okf-profile-validator.md) — Resolved task ticket implementing the SmartDCA OKF profile and its report-only validator. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Atomically migrate the repository to SmartDCA OKF 0.1](.scratch/smartdca/issues/14-atomically-migrate-repository-to-okf.md) — Task ticket atomically migrating every concept to smartdca-okf/0.1 and activating blocking CI. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Ingest the LLM-Wiki and OKF foundation sources](.scratch/smartdca/issues/15-ingest-llm-wiki-okf-foundation-sources.md) — Resolved research ticket ingesting the five LLM-Wiki and OKF foundation sources one at a time. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Extract initial semantic concepts and certify structural freeze](.scratch/smartdca/issues/16-extract-semantic-concepts-certify-freeze.md) — Resolved task ticket extracting initial semantic concepts and certifying structural freeze. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Clean redundancy after structural freeze](.scratch/smartdca/issues/17-clean-redundancy-after-structural-freeze.md) — Resolved task ticket cleaning redundancy and applying supersession after structural freeze. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Isolate the first nontrivial corrected-mean effect at three purchases](.scratch/smartdca/issues/18-isolate-three-purchase-corrected-mean-effect.md) — Resolved task ticket isolating the first beta-dependent guarded SmartDCA boundary at three purchases. — type: research-ticket; status: stable; trust: unreviewed; provenance: Git history
- [Audit and sharpen agent-facing wiki instructions](.scratch/smartdca/issues/19-audit-agent-facing-writing.md) — Task ticket auditing the full wiki for agent-consumed writing and sharpening the active instruction surfaces. — type: research-ticket; status: draft; trust: unreviewed; provenance: Git history
