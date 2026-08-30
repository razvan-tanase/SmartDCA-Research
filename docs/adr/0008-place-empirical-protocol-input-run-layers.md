# Place empirical protocols, inputs, and run bundles in versioned layers

The empirical effort produces four artifact classes with different identity
and mutability rules. Keep them in these durable layers:

| Path | Authority and identity rule |
|---|---|
| `experiments/protocols/*.json` | Immutable preregistrations. After review or outcome access, changed bytes receive a new protocol ID and version. |
| `experiments/inputs/*.json` | Versioned runner inputs or receipts. Fingerprint accepted bytes, exclude credentials, and create a new version when accepted bytes change. |
| `reports/experiments/runs/<run-id>/` | Deterministic machine outputs. The run ID binds engine, runner, protocol, and input bytes; an existing identity is a collision, not an overwrite target. |
| `reports/experiments/*.md` | Narrative reports that link a run to its protocol, input, code, review, and limits without substituting for machine artifacts. |

The public runner remains under `reproducibility/`, with its contract checked
under `reproducibility/checks/`. The first publication of a protocol/input pair
has one narrow correction window: before outcome access and independent
acceptance, review may correct provisional bytes. Record the correction in the
tracked research, keep `confirmatory_outcomes_accessed` false, and give the
corrected run its content-derived ID. Acceptance seals the fingerprints and
closes the window.

One registered design can drive multiple immutable input versions and runs
without conflating their identities. A future move to external storage must
preserve fingerprints, stable report links or receipts, and the
collision/no-overwrite rule. This extends [the versioned research-layer
decision](0001-versioned-research-layout.md).
