# Agent contract

Start with `README.md`. Use its repository map to load only the domain terms,
evidence, decisions, and work state that the requested change reaches.

## Route the change

Apply every matching branch:

- **Scientific claims:** Link every new or changed claim to its detailed
  evidence under `research/notes/` and run its corresponding program under
  `reproducibility/checks/`. A change to a theorem, definition, model
  assumption, or empirical conclusion needs an independent domain review
  recorded in the evidence note or tracked ticket.
- **External sources:** Cite every claim that depends on material outside the
  repository.
- **Versioned artifacts:** Preserve retained scientific source bytes,
  accepted protocols and inputs, and existing run bundles. A revised source
  edition, accepted protocol or input, or run output receives a new version or
  identity. Keep a revised narrative report's artifact links and publication
  state accurate.
- **Domain language:** Read the relevant entries in `CONTEXT.md`; update the
  glossary when terminology or model assumptions change.
- **Durable decisions:** Read intersecting records under `docs/adr/`. Add an
  ADR only for a surprising trade-off that is hard to reverse.
- **Tracked research:** Use [work tracking](docs/agents/work-tracking.md) only
  when the user requests it or the work spans multiple independently
  resolvable research stages. Execute bounded changes directly.

## Completion

Run the checks that cover the changed behavior and
`python tools/check_markdown_links.py .`. For a repository-wide or release
change, run the complete verification suite documented in `README.md`. When
work tracking applies, synchronize the ticket and maps. The final diff is
self-contained when its claims, evidence, state, and instructions agree.

## Agent skills

### Issue tracker

When creating, selecting, claiming, resolving, or fetching work, use local
Markdown under `.scratch/`; read `docs/agents/issue-tracker.md` for tracker
conventions.

### Triage labels

When triaging or labeling an issue, read `docs/agents/triage-labels.md` and use
its canonical mappings.

### Domain docs

When exploring or changing domain terms, model assumptions, or durable
decisions, read `docs/agents/domain.md`, then the relevant `CONTEXT.md` and
`docs/adr/` records.
