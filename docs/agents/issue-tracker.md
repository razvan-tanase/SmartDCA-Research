# Issue tracker: Local Markdown

Issues and specs live as Markdown files in `.scratch/`.

## Paths and records

- One effort occupies `.scratch/<effort-slug>/`.
- Its specification is `.scratch/<effort-slug>/spec.md`.
- Its map is `.scratch/<effort-slug>/map.md`.
- Each ticket is `.scratch/<effort-slug>/issues/<NN>-<slug>.md`, numbered from
  `01`.
- Each ticket has `Type:`, `Status:`, and `Blocked by:` lines near the top.
- Ticket status is `open`, `claimed`, or `resolved`.
- Append execution history under `## Comments`; append the outcome under
  `## Answer`.

For tracked-research execution and completion gates, read
`docs/agents/work-tracking.md`.

## Skill operations

When a skill says “publish to the issue tracker,” create or update the relevant
Markdown record under `.scratch/<effort-slug>/`.

When a skill says “fetch the relevant ticket,” read the path supplied by the
user or the ticket number in the relevant effort directory.

## Wayfinding

`/wayfinder` treats `.scratch/<effort-slug>/map.md` as the effort map and each
file under `issues/` as a child ticket.

- A ticket is unblocked when every path or ticket in `Blocked by:` is resolved.
- The frontier is the first numbered ticket that is open, unblocked, and
  unclaimed.
- Claim by setting `Status: claimed` before execution.
- Resolve by adding `## Answer`, setting `Status: resolved`, and adding a
  concise context pointer to the map’s decisions.
