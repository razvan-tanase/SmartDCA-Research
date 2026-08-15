# Atomically migrate the repository to SmartDCA OKF 0.1

Type: task
Status: open
Blocked by: 13
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

Using ticket 13's reviewed profile, add conformant frontmatter to every non-reserved Markdown file while preserving each existing body and workflow header. Add root `index.md` with only `okf_version: "0.2"` in its frontmatter and a body declaring `smartdca-okf/0.1`; add machine-parseable append-only root `log.md`; and switch the validator from report-only to blocking CI in the same merge transaction. Apply the accepted initial type, role, lifecycle, ticket-state, and ADR-state mapping; verify all internal links and rerun every scientific check. Do not split, synthesize, or deduplicate content in this ticket.

## Comments

- Created from the accepted ticket-12 architecture.
- `main` must never land in an intentionally nonconformant or permanently report-only state.

## Answer

Pending.
