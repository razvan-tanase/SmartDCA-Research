# 07 — Draft the impossibility-to-safety policy architecture

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 03, 06
Parent: [Thesis manuscript assembly](../spec.md)

## Question

Can the thesis explain why universal same-deposit DCA dominance collapses to DCA itself and how the epsilon-DCA guardrail enables a distinct causal policy without overstating what is guaranteed?

## What to build

A committee reader can follow the pivot from an impossible universal-superiority ambition to an exact safety architecture, understand the guarded algorithm, and distinguish the guardrail's guarantee from the corrected signal's empirical role.

## Acceptance criteria

- [x] The causal DCA impossibility theorem is stated with its full path, funding, causality, trading, comparator, and terminal-wealth assumptions.
- [x] The proof idea is understandable in the body, with complete proof machinery retained in an appendix.
- [x] The narrative explains why the result motivates a weaker safety target rather than presenting the pivot as an unrelated construction.
- [x] Epsilon-DCA safety is defined as a relative-wealth floor and never described as dominance when epsilon is positive.
- [x] The sharp unit-coverage purchase floor, cushion, and funded discretionary allocation are stated exactly.
- [x] The corrected-mean score is presented only as the discretionary selector inside the guardrail.
- [x] The complete policy is shown to be causal, fully funded, long-only, and buy-only under the declared frictionless model.
- [x] The lambda-equals-one collapse and the boundary between frictionless safety and net-of-cost evidence are explicit.
- [x] Policy logic, theorem statements, notation, non-claims, and evidence mappings pass independent domain review and the canonical build.

## Comments

- Created from the user-approved 17-ticket decomposition on 2026-09-01.
- This ticket is a vertical manuscript slice: its prose, citations, evidence mappings, generated assets where applicable, and canonical build must agree before resolution.
- Claimed for implementation on 2026-09-04 after tickets 03 and 06 were verified resolved.
- Independent domain/specification review on 2026-09-04 checked the complete comparison model, adverse-continuation proof, safety equivalence, guardrail floor, policy accounting, lambda-one boundary, frictionless scope, citations, and claim controls. Follow-up review passed with no remaining finding after the necessity statement was narrowed to policies retaining a universal DCA-relative floor and the Grossman--Zhou drawdown citation was mapped. Independent Standards review passed after common audit parsing and authority-path validation moved to `reproducibility/control_support.py` and the manuscript build gates became data-driven.
- Final verification on 2026-09-04 passed all 70 reachable link, manuscript, release, literature, foundation, and policy-architecture tests; the direct controls and repository-link checks; 64 identity, 108 adversarial, 1,548 prefix, 2,916 oracle, and 1,080 nonincreasing-path cases; 18,653 guarded path-factor cases with 64,613 adverse-prefix checks; and 59,049 guarded ledgers with 177,147 terminal valuations. The canonical 56-page A4 PDF built successfully, and Chapter 4 pages 23--25 were visually inspected with a clean, legible Figure 4.1. The release gate remains expectedly closed only on retained institutional placeholders.

## Answer

Ticket 07 is resolved. Chapter 4 now turns the full-assumption causal DCA impossibility theorem into the motivation for epsilon-DCA safety, states the sharp unit-coverage floor and complete discretionary interface, and defines the guarded corrected-mean policy with direct causal, funding, long-only, buy-only, lambda-one, and cost-scope arguments. Appendix A retains both complete proofs, while Figure 4.1, four claim records, four notation records, two non-claims, and the fail-closed architecture audit keep the policy logic traceable to reviewed evidence. Ticket 08 is the next unblocked drafting frontier.
