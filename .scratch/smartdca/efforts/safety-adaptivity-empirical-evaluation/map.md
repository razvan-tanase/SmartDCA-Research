# Safety-adaptivity empirical evaluation effort map

## Contract

The approved problem, outcome requirements, implementation and testing
decisions, and exclusions live in the [effort specification](spec.md). The
project-wide scientific context lives in the
[SmartDCA research map](../../map.md). When selecting or changing a ticket,
follow the [work-tracking workflow](../../../../docs/agents/work-tracking.md).

## Ticket route

| Ticket | Purpose | Status | Dependencies |
|---|---|---|---|
| [01](issues/01-preregister-protocol-establish-canonical-run.md) | Freeze the protocol and establish one complete non-confirmatory empirical run. | resolved | — |
| [02](issues/02-evaluate-deterministic-adversarial-paths.md) | Evaluate deterministic synthetic and adversarial path families. | resolved | 01 |
| [03](issues/03-evaluate-seeded-stochastic-families.md) | Evaluate seeded stochastic path families. | resolved | 01 |
| [04](issues/04-establish-historical-data-episode-seam.md) | Establish fingerprinted historical inputs and rolling episodes without opening confirmatory outcomes. | resolved | 01 |
| [05](issues/05-run-confirmatory-historical-evaluation.md) | Execute the frozen rolling S&P 500 and Bitcoin evaluation. | claimed | 04 |
| [06](issues/06-synthesize-safety-adaptivity-tradeoff.md) | Synthesize deterministic, stochastic, and historical evidence. | open | 02, 03, 05 |
| [07](issues/07-review-publish-empirical-package.md) | Independently reproduce, review, and publish the empirical package. | open | 06 |

## Current frontier

Ticket [05](issues/05-run-confirmatory-historical-evaluation.md) remains claimed.
Its immutable primary [confirmatory
run](../../../../reports/experiments/confirmatory-historical-evaluation.md) is
complete, but final specification review requires the separately registered
robustness coverage and quarterly-horizon grids before resolution. Ticket 06
therefore remains blocked. Resolved ticket answers and linked reports are the
authority for completed run identities, detailed results, and publication
gates.
