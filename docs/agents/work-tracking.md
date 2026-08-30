# Work tracking

Load this workflow when the user requests tracked work or an investigation has
multiple independently resolvable research stages. Execute a bounded change
directly.

## Records

- `.scratch/smartdca/map.md` records the project frontier across efforts.
- `.scratch/smartdca/efforts/<effort>/spec.md` is the user-approved contract
  for one effort.
- An effort's `map.md` records its route and current state.
- `issues/<NN>-<slug>.md` contains locally numbered tickets for that effort.
- `.scratch/smartdca/issues/` is read-only legacy research history. Use it as
  evidence when revisiting a legacy decision; preserve its bytes.

A ticket records `Type:`, `Status:`, and `Blocked by:`. `Blocked by` lists
prerequisite ticket numbers or repository-relative paths; a prerequisite stops
selection only while it is unresolved. Use `none` when there is no
prerequisite. `## Question` and its acceptance criteria are the work contract,
`## Comments` holds execution history or blockers, and `## Answer` holds the
resolution. Status is `open`, `claimed`, or `resolved`.

## Flow

1. **Orient.** Read the effort specification, effort map, selected ticket,
   relevant glossary entries, evidence, and ADRs. Orientation is complete when
   the outcome, prerequisites, exclusions, and authoritative evidence homes
   are explicit.
2. **Select.** Use a user-named open ticket or the first open ticket whose
   prerequisites are resolved. Set it to `claimed`. Selection is complete when
   exactly one ticket in the effort is claimed.
3. **Execute.** Satisfy every contract clause and acceptance criterion. Put
   detailed reasoning in one linked note or artifact; keep each map result to
   one line.
4. **Verify.** Run every check covering the change. For a substantive theorem,
   definition, model-assumption, or empirical-conclusion change, record an
   independent domain review in the evidence note or ticket. Verification is
   complete when all required checks and reviews pass. If one cannot pass,
   follow **Interrupted work** below.
5. **Resolve.** Record the answer, set `Status: resolved`, and update the
   effort map. Update the project map only when the cross-effort frontier or a
   project-level decision changes. Resolution is complete when the
   specification, ticket, maps, evidence, and checks describe the same state.

## Interrupted work

Record the evidence produced and the exact blocker. Leave a ticket `claimed`
only while an executor is actively working; otherwise return it to `open`.
