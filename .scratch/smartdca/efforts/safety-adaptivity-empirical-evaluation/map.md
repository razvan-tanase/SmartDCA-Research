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
| [04](issues/04-establish-historical-data-episode-seam.md) | Establish fingerprinted historical inputs and rolling episodes without opening confirmatory outcomes. | open | 01 |
| [05](issues/05-run-confirmatory-historical-evaluation.md) | Execute the frozen rolling S&P 500 and Bitcoin evaluation. | open | 04 |
| [06](issues/06-synthesize-safety-adaptivity-tradeoff.md) | Synthesize deterministic, stochastic, and historical evidence. | open | 02, 03, 05 |
| [07](issues/07-review-publish-empirical-package.md) | Independently reproduce, review, and publish the empirical package. | open | 06 |

## Current frontier

No ticket is claimed. [Ticket
04](issues/04-establish-historical-data-episode-seam.md) is open: its executable
acquisition, preparation, and validation seam is implemented, fully verified,
and clean on both review axes, but an authorized provider retrieval is still
required to close the received-series and coverage gate. Ticket 05 remains
blocked; tickets 06 and 07 remain behind their listed dependencies. The
resolved ticket answers and linked reports are the authority for completed-run
details. The seeded stochastic report remains draft until the registered
historical-slice gate is complete.
