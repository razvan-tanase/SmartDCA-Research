# Work tracking

Use this workflow only when the user requests tracked work or an investigation
has multiple independently resolvable research stages. A bounded change does
not need a ticket.

## Layout

- `.scratch/smartdca/map.md` records the project frontier across efforts.
- `.scratch/smartdca/efforts/<effort>/spec.md` is the user-approved contract
  for one effort.
- An effort's `map.md` records its route and current state.
- `issues/<NN>-<slug>.md` contains locally numbered tickets for that effort.
- `.scratch/smartdca/issues/` contains read-only legacy research history.

A ticket records `Type:`, `Status:`, and `Blocked by:` in its body. Its
`## Question` is the work contract, `## Comments` holds execution history or
blockers, and `## Answer` holds the resolution. Status is `open`, `claimed`,
or `resolved`.

## Flow

1. **Orient.** Read the effort specification, effort map, selected ticket,
   relevant glossary terms, evidence, and ADRs. Start when the outcome,
   dependencies, and exclusions are explicit.
2. **Select.** Use a user-named open ticket or the first open unblocked ticket
   in the effort map. Keep only one ticket claimed while tracked work is
   active.
3. **Execute.** Answer every clause of the ticket. Put detailed reasoning in
   one linked note or artifact and keep the map to a one-line result.
4. **Verify.** Run the relevant checks. Independently review a substantive
   theorem, definition, model-assumption, or empirical-conclusion change.
5. **Resolve.** Record the answer, set `Status: resolved`, and update the
   effort map. Update the project map only when the cross-effort frontier or a
   project-level decision changed.

If work stops mid-ticket, record the evidence and exact blocker. Keep the
ticket claimed only while an executor is actively working; otherwise return
it to open. The tracked state is coherent when the specification, tickets,
and maps describe the same frontier.
