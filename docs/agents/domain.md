# Domain Docs

Use this guide when an agent explores or changes domain language, model
assumptions, or durable design decisions.

## Routing

- For domain terms, definitions, assumptions, or claims, read the relevant
  sections of root `CONTEXT.md`.
- For durable design or process decisions, read the relevant records in root
  `docs/adr/`.
- If a root `CONTEXT-MAP.md` appears later, follow it to the context-specific
  `CONTEXT.md` files and read the ADRs that intersect the change.
- If a referenced document is absent, continue with the documents that exist
  and record a missing source only when it blocks the work.

## Current layout

This is a single-context repository:

```text
/
├── CONTEXT.md
├── docs/adr/
└── src/
```

## Glossary discipline

Use the glossary’s exact domain terms in issue titles, hypotheses, tests, and
reports. Preserve each term’s stated claim boundary. If a needed concept is
absent or ambiguous, route the terminology change through `/domain-modeling`.

## ADR conflicts

Surface contradictions with existing ADRs explicitly before changing direction:

> Contradicts ADR-XXXX (`title`), but worth reopening because ...
