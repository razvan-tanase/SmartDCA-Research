# Safety-adaptivity empirical evaluation effort map

## Contract

The approved problem, outcome requirements, implementation and testing
decisions, and exclusions live in the [effort specification](spec.md). The
project-wide scientific context lives in the
[SmartDCA research map](../../map.md).

## Ticket route

| Ticket | Purpose | Status | Blocked by |
|---|---|---|---|
| [01](issues/01-preregister-protocol-establish-canonical-run.md) | Freeze the protocol and establish one complete non-confirmatory empirical run. | resolved | — |
| [02](issues/02-evaluate-deterministic-adversarial-paths.md) | Evaluate deterministic synthetic and adversarial path families. | resolved | — |
| [03](issues/03-evaluate-seeded-stochastic-families.md) | Evaluate seeded stochastic path families. | resolved | — |
| [04](issues/04-establish-historical-data-episode-seam.md) | Establish fingerprinted historical inputs and rolling episodes without opening confirmatory outcomes. | open | — |
| [05](issues/05-run-confirmatory-historical-evaluation.md) | Execute the frozen rolling S&P 500 and Bitcoin evaluation. | open | 04 |
| [06](issues/06-synthesize-safety-adaptivity-tradeoff.md) | Synthesize deterministic, stochastic, and historical evidence. | open | 02, 03, 05 |
| [07](issues/07-review-publish-empirical-package.md) | Independently reproduce, review, and publish the empirical package. | open | 06 |

## Current frontier

[Preregister the empirical protocol and establish one canonical run](issues/01-preregister-protocol-establish-canonical-run.md)
is resolved after Standards, specification, and independent empirical review.
[Evaluate deterministic synthetic and adversarial paths](issues/02-evaluate-deterministic-adversarial-paths.md)
is also resolved after byte-identical clean-room replay of its 18 generated
paths, retained exclusions, and exhaustive finite adversarial search. The
[seeded stochastic evaluation](issues/03-evaluate-seeded-stochastic-families.md)
is also resolved: its 90 paths, 3,240 ledgers, 1,080 reconciled aggregate cells,
and byte-identical replay provide reviewed controlled sensitivity evidence with
mixed signs across families. Its report and audit remain draft pending the
registered historical-slice gate. Ticket 04 is the next open unclaimed stage;
ticket 05 still needs that historical-data seam, while synthesis and publication
remain blocked until their full evidence dependencies resolve.
