# 07 — Draft the impossibility-to-safety policy architecture

Type: task
Status: open
Triage: ready-for-agent
Blocked by: 03, 06
Parent: [Thesis manuscript assembly](../spec.md)

## Question

Can the thesis explain why universal same-deposit DCA dominance collapses to DCA itself and how the epsilon-DCA guardrail enables a distinct causal policy without overstating what is guaranteed?

## What to build

A committee reader can follow the pivot from an impossible universal-superiority ambition to an exact safety architecture, understand the guarded algorithm, and distinguish the guardrail's guarantee from the corrected signal's empirical role.

## Acceptance criteria

- [ ] The causal DCA impossibility theorem is stated with its full path, funding, causality, trading, comparator, and terminal-wealth assumptions.
- [ ] The proof idea is understandable in the body, with complete proof machinery retained in an appendix.
- [ ] The narrative explains why the result motivates a weaker safety target rather than presenting the pivot as an unrelated construction.
- [ ] Epsilon-DCA safety is defined as a relative-wealth floor and never described as dominance when epsilon is positive.
- [ ] The sharp unit-coverage purchase floor, cushion, and funded discretionary allocation are stated exactly.
- [ ] The corrected-mean score is presented only as the discretionary selector inside the guardrail.
- [ ] The complete policy is shown to be causal, fully funded, long-only, and buy-only under the declared frictionless model.
- [ ] The lambda-equals-one collapse and the boundary between frictionless safety and net-of-cost evidence are explicit.
- [ ] Policy logic, theorem statements, notation, non-claims, and evidence mappings pass independent domain review and the canonical build.

## Comments

- Created from the user-approved 17-ticket decomposition on 2026-09-01.
- This ticket is a vertical manuscript slice: its prose, citations, evidence mappings, generated assets where applicable, and canonical build must agree before resolution.
