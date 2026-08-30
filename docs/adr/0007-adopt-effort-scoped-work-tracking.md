# Use effort-scoped work tracking when work needs it

The original tracker mixed project history, large frontier specifications, and
all executable work in one numbered directory. As the research expanded,
ticket numbers stopped identifying their investigation and parent
specifications looked like claimable work.

For user-requested or multi-stage tracked research, keep the project frontier
in `.scratch/smartdca/map.md` and give each effort its own directory under
`.scratch/smartdca/efforts/<effort>/`. An effort contains an approved
`spec.md`, a local `map.md`, and locally numbered tickets under `issues/`.
Cross-effort blockers use repository-relative paths. The remaining files in
`.scratch/smartdca/issues/` are read-only legacy research history.

This layout keeps each workstream's contract and progress together while the
project map stays small. Bounded changes do not need an effort or ticket; that
scope rule is recorded in [Retire the OKF knowledge layer](0010-retire-okf-knowledge-layer.md).
