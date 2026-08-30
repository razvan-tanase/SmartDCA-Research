---
profile: smartdca-okf/0.5
type: decision-record
title: "Assign definition, theorem, and experiment-report paths in profile 0.3"
description: "Decision assigning the three remaining semantic type paths and relabelling the bundle as smartdca-okf/0.3."
knowledge_role: canonical
status: stable
original_record: true
decision_status: accepted
generated:
  by: claude-code/smartdca-wiki-0.1
  at: 2026-08-16T09:24:00Z
generation_run: urn:uuid:efe6420b-e236-40b6-96d4-c92a95d505d2
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T09:26:00Z
    review_run: urn:uuid:0b6608b4-7e9f-4ba5-a07e-d6e8537908fd
---
# Assign definition, theorem, and experiment-report paths in profile 0.3

Profile 0.2 registered `definition`, `theorem`, and `experiment-report` in the type vocabulary but deliberately left them without a path, and its path mapping is exhaustive: a Markdown file at an unassigned path fails the profile however good its metadata is. Semantic extraction cannot put a definition or a theorem anywhere conformant until that decision is made, exactly as ingestion could not put a summary anywhere conformant before [profile 0.2](0005-assign-source-summary-and-synthesis-paths.md).

Therefore profile `smartdca-okf/0.3` assigns three paths and every concept declares `profile: smartdca-okf/0.3`:

| Path | Type | Role |
|---|---|---|
| `research/definitions/*.md` | `definition` | canonical |
| `research/theorems/*.md` | `theorem` | canonical |
| `reports/experiments/*.md` | `experiment-report` | evidence |

The two mathematical destinations sit under `research/` beside the `research/notes/` evidence they are extracted from and the `research/synthesis/` concepts that integrate them, so the whole research layer is one subtree with role separated by directory rather than by filename. `reports/experiments/` sits under the existing `reports/` tree, which already holds generated report artifacts, and is `evidence` rather than `canonical` because an experiment illustrates and stress-tests theory instead of governing a claim — the map's standing rule that simulations are not proof.

`experiment-report` is assigned now even though no experiment report exists yet. Assigning it costs nothing, and leaving it unassigned would mean the first experiment forces another profile version bump, which is precisely the kind of pending schema change that structural freeze is supposed to rule out. With these three, every registered type has a destination and the path mapping is complete.

Relabelling 0.2 to 0.3 is a metadata migration on the same terms [ADR 0005](0005-assign-source-summary-and-synthesis-paths.md) established: it does not update `generated.at`, does not demote a high-risk concept to draft, and does not invalidate a recorded verification. Only concepts whose bodies actually changed in the same transaction carry a new generation time. No other rule of profile 0.2 changes, so a 0.2 concept is conformant under 0.3 once its `profile` value is relabelled.
