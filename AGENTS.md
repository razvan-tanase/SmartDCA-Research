# Agent contract

Start with `README.md`. Read only the domain pages, evidence, decisions, and
work state relevant to the requested change.

## Choose the applicable branches

- **Scientific claims:** Link every new or changed claim to its detailed
  evidence under `research/notes/` and run its corresponding program under
  `reproducibility/checks/`. A change to a theorem, definition, model
  assumption, or empirical conclusion needs an independent domain review
  recorded in the evidence note or tracked ticket.
- **Sources and empirical artifacts:** Cite external claims. Treat retained
  scientific source bytes, accepted protocols and inputs, and existing run
  bundles as immutable; a revised source edition, accepted protocol or input,
  or run output receives a new version or identity. Narrative reports may be
  revised while keeping their artifact links and publication state accurate.
- **Domain language or durable decisions:** Read the relevant terms in
  `CONTEXT.md` and intersecting records under `docs/adr/`. Update the glossary
  when project language changes. Add an ADR only for a hard-to-reverse,
  surprising trade-off.
- **Tracked research:** Use [work tracking](docs/agents/work-tracking.md) only
  when the user requests it or the work spans multiple independently
  resolvable research stages. Execute bounded changes directly.

## Authoritative homes

| Information | Home |
|---|---|
| Project introduction and research navigation | `README.md` |
| Canonical terminology and assumptions | `CONTEXT.md` |
| Definitions and theorem statements | `research/definitions/`, `research/theorems/` |
| Proofs, source analysis, and detailed reasoning | `research/notes/` |
| Executable scientific evidence | `reproducibility/checks/` |
| Empirical protocols, inputs, reports, and runs | `experiments/`, `reports/experiments/` |
| Tracked project and effort state | `.scratch/smartdca/` |
| Durable repository and process decisions | `docs/adr/` |

## Completion

Run the checks that cover the changed behavior and
`python tools/check_markdown_links.py .`. For a repository-wide or release
change, run the complete verification suite documented in `README.md`. When
work tracking applies, synchronize the ticket and maps. Finish with a diff
whose claims, evidence, state, and instructions agree without relying on
hidden conversation context.
