---
profile: smartdca-okf/0.5
type: research-ticket
title: "Evaluate deterministic synthetic and adversarial paths"
description: "Resolved task ticket executing the preregistered three-policy study on deterministic synthetic and adversarial price-path families."
knowledge_role: operational
status: stable
original_record: true
ticket_type: task
ticket_status: resolved
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-25T11:18:28Z
generation_run: urn:uuid:1e2029d0-e145-456a-ba97-2ddca88bc388
verified:
  - by: openai-codex/standards-review-0.1
    at: 2026-08-25T11:16:26Z
    review_run: urn:uuid:34df7016-c817-4ad7-b05a-36773412a89c
  - by: openai-codex/spec-review-0.1
    at: 2026-08-25T11:12:41Z
    review_run: urn:uuid:3423b393-7949-4da7-999c-dcfc0747fc29
  - by: openai-codex/independent-empirical-review-0.1
    at: 2026-08-25T11:15:20Z
    review_run: urn:uuid:8a76cee8-e9c9-4ade-9e4d-b08f61a6046c
---
# 02 — Evaluate deterministic synthetic and adversarial paths

Type: task
Status: resolved
Label: ready-for-agent
Blocked by: 01
Parent: [Safety-adaptivity empirical evaluation](../spec.md)

## Question

How do DCA, the neutral guarded selector, and the guarded corrected-mean
SmartDCA rule behave across interpretable deterministic and deliberately hostile
price paths when the preregistered coverage and cost configurations are applied?

## What to build

A researcher can reproduce a named deterministic study covering the mathematical
boundary cases and economically interpretable stress paths, then inspect raw
three-policy ledgers, aggregate comparisons, mechanism attribution, failures,
and a bounded experiment report generated through the shared runner.

## Acceptance criteria

- [x] The executed families include constant prices, monotone rises, monotone declines, weak and strict single valleys, incomplete and completed recoveries, multiple valleys, crashes, sudden rebounds, prolonged drawdowns, flat segments, and paths deliberately hostile to carried cash or adaptive timing.
- [x] Every generated path is identified by saved family parameters and satisfies its declared path predicate independently of policy performance.
- [x] All three policies run under identical prices, deposits, dates, evaluation points, safety factors, corrected-mean configurations, and cost scenarios from the preregistered protocol.
- [x] The results report complete-system, signal-only, and safety-architecture comparisons together with relative terminal wealth, downside, cash drag, exposure, guardrail activation, purchase activity, and terminal cash/unit attribution.
- [x] Frictionless runs verify the epsilon-DCA unit-coverage condition and terminal cash/unit identity; cost-adjusted runs remain explicitly empirical net-performance results.
- [x] Boundary fixtures connect the study to the existing constant, two-purchase, three-purchase, single-valley, repeated-floor-activation, and arbitrary-horizon results without presenting finite experiments as proof.
- [x] Every attempted configuration, exclusion, validation failure, and successful result is retained rather than reporting only favorable paths or parameters.
- [x] Raw episode results, aggregates, tables, and figure-ready data regenerate from one immutable run manifest in a fresh environment.
- [x] The experiment report states which mechanisms appear in each path family and what deterministic evidence cannot establish about historical or stochastic performance.
- [x] The ticket, report, checks, effort map, and repository verification gates agree at resolution.

## Comments

- Created from the user-approved seven-ticket decomposition on 2026-08-25.
- This ticket may proceed in parallel with tickets 03 and 04 after ticket 01
  resolves.
- Claimed on `agent/evaluate-deterministic-adversarial-paths` after confirming
  ticket 01 is resolved and no other ticket is claimed.
- Implementation proceeded test-first from path predicates and rejection
  receipts through the complete immutable run. The final checkpoint has 14
  public-contract tests and seven executable boundary contracts.
- Initial Standards and specification review found incomplete source identity,
  tag-only boundary fixtures, transcription-only report tables, an undeclared
  performance-based hostile-path selection, and missing seed/provenance joins.
  Follow-up review found one generated Markdown artifact and untested narrative
  attributions. Every finding was corrected and re-reviewed to a pass.
- Independent empirical review reproduced all 23 final bundle files byte for
  byte and recomputed the search, accounting, attribution, and theorem-scope
  receipts without a blocking or non-blocking finding.
- The experiment report intentionally remains draft because the effort's
  stable-promotion gate awaits the registered historical-slice reproduction in
  ticket 04. No historical provider response or stochastic outcome was used.

## Answer

The saved [deterministic study](../../../../../experiments/inputs/deterministic-adversarial-v1.json)
has SHA-256
`40b4ba6e22de4f34ce558be2d96239528bbd11890245ddbe4ccf68e583aae456`.
The [study runner](../../../../../reproducibility/deterministic_study.py) binds
that input, the frozen protocol, its own source, the shared empirical runner,
and the explicit null seed into immutable run
`smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db`.
Its [manifest](../../../../../reports/experiments/runs/smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db/manifest.json)
fingerprints 22 pre-manifest artifacts.

The main study retains 21 attempted configurations: 18 generated paths and
three typed validation exclusions. Fourteen named primary families plus exact
regression paths produce 648 complete three-policy ledgers and 648 comparison
rows. Seven executable boundary receipts match the existing constant,
two-purchase, three-purchase, single-valley, repeated-floor, and
arbitrary-horizon checks. The declared finite adversarial search retains all
729 candidate sequences, admits 42 by its policy-independent predicate,
retains 687 exclusions, and executes 1,512 additional ledgers and comparison
rows. Its lexicographic minimum is candidate `hostile-adaptive-timing-grid-v1-637`
with prices `[150, 100, 150, 100, 150, 60]`.

At frictionless \(\lambda=0.75\), the hostile carried-cash path puts corrected
guarded 4.978% below DCA and 0.473% below neutral guarded. On the selected
adaptive-timing path, corrected guarded is 2.901% below neutral even though
neutral is 29.873% above DCA and the complete corrected system remains 26.105%
above DCA. This separates selector downside from guardrail-architecture upside;
it does not estimate a market frequency or establish stochastic, historical,
or universal performance.

The 14-case [checkpoint](../../../../../reproducibility/checks/check_deterministic_adversarial_study.py)
reproduces the complete bundle byte for byte, derives every report table and
exact hostile-path narrative receipt from committed episode rows, and is wired
into repository verification. The independently reviewed
[experiment report](../../../../../reports/experiments/deterministic-adversarial-paths.md)
records the mechanism attribution, cost scopes, hashes, and limitations.
Standards, specification, and clean-room empirical re-review report no remaining
finding.
