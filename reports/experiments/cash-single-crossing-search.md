# Exact-rational cash single-crossing mechanism search

## Verdict

The expanded exact grid contains strict four-date single-valley scenarios in
which corrected-minus-neutral cash has two sign changes. The decisive witness
is an exact counterexample, so weak and strict single-valley geometry cannot
support an unconditional cash single-crossing theorem. The same search finds
no failure among scenarios whose floor differences align with the corrected
reference boundary; that zero count checks the proved sufficient condition
but is not its proof.[^mechanism-note][^ticket-03]

## Run contract

Run ID: `urn:uuid:eae689ea-6439-41b7-bc18-396d11f863bf`

Command:

```bash
python -m reproducibility.cash_single_crossing_search
```

The command evaluates each scenario through the public exact-rational ledger
and emits deterministic JSON.[^accounting-seam] There is no random sampling,
so the seed is `none`.

| Input | Declared values |
|---|---|
| Horizon | \(n=4\) |
| Price normalization | \(p_1=1\) |
| Purchase-price levels | \(\{1/16,1/8,1/4,1/2,2/3,1,3/2,2,4,8,16,32\}\) |
| Equal deposits | \(d_t=1\) at every date |
| Safety factors, in complexity order | \(\lambda=(1/2,1/4,3/4,7/8,15/16,31/32,63/64)\) |
| Parameter pairs, in order | \((\alpha,\beta)=((0,-1),(0,1),(-1,0))\) |
| Transform | \(f=\mathrm{id}\) |
| Evaluation price | \(P=p_4\); cash paths are independent of \(P\) |

All parameter pairs satisfy \(\alpha<1\) and \(\alpha\beta\le0\). Unit-gap
integer exponents keep every evaluated reference and score rational on this
grid.[^gini-region] The run had zero exact-domain rejections.

## Predicate, ordering, and pruning

The independently validated weak single-valley predicate uses the first
minimum \(p_k\) and requires

\[
p_1\ge\cdots\ge p_k\le\cdots\le p_n.
\]

A genuine cycle has a strict fall and a strict recovery; a strict cycle is
strictly decreasing to an interior trough and strictly increasing afterward.
Paths are ordered by horizon, then number of distinct levels, transitions,
total variation, and the tuple of declared level indices. Parameter complexity
then orders \(\lambda\) by rational height
\(\max(|\operatorname{num}|,\operatorname{den})\), numerator-plus-denominator,
and value. It orders \((\alpha,\beta)\) by score exponent \(1-\alpha\),
reference gap \(|\alpha-\beta|\), then each rational's height,
numerator-plus-denominator, and value. Deposit complexity is last and fixed at
the unit equal-deposit normalization.

Fixing \(p_1=1\) removes common price scaling. Fixing every equal positive
deposit at one removes common deposit scaling because policy cash, purchases,
and units scale linearly. No outcome-dependent pruning is used.

## Results

The expanded grid has 559 price paths and 11,739 cash scenarios.

| Exact classification | Count |
|---|---:|
| More than one cash sign change | 27 |
| Failure of directional minus-then-plus crossing | 115 |
| More than one sign change on genuine cycles | 25 |
| More than one sign change on strict cycles | 25 |
| Scenarios with reference-aligned guardrail feedback | 5,371 |
| Reference-aligned guardrail failures | 0 |

As a regression check, the ticket-02 grid contributes 2,274 paths and 20,466
distinct cash scenarios after its three evaluation-price multipliers are
identified: carried cash is evaluation-price independent. That earlier grid
contains no literal or directional cash-crossing failure. The expanded safety
and price extremes together expose the mechanism in the new declared finite
search.

## Minimized witnesses and mechanism replay

Under the declared ordering, the first literal double reversal is the weak
path

\[
p=(1,2,32,32),\quad \lambda=31/32,\quad
(\alpha,\beta)=(-1,0),
\]

with cash differences

\[
\left(0,\frac3{128},-\frac{665}{147712},
\frac{3183}{308480}\right).
\]

The first genuine and strict-cycle double reversal is

\[
p=(1,1/16,1,8),\quad \lambda=63/64,\quad
(\alpha,\beta)=(-1,0),
\]

with exact guarded differences

\[
\left(
0,-\frac{12495}{1052672},
\frac{174032415}{616865792},
-\frac{142575068237}{2843751301120}
\right).
\]

The sign changes occur at dates three and four. Disabling both floors while
preserving the scenario and score rules leaves only the date-three change.
The decomposition checker verifies every period as previous cash carry plus
score forcing plus the policy-specific floor component. The evidence note
records the full references, floors, recurrence, and horizon-minimality
argument.[^mechanism-note]

The check also replays a nonconstant strict common-floor case,
\(p=(1,1/2,2/3,1)\), \(\lambda=1/2\), and
\((\alpha,\beta)=(0,-1)\). Its floor path is
\((1/2,3/8,0,0)\) for both policies and its cash difference crosses once,
from negative to positive. This proves the surviving class is nonempty
without requiring inactive guardrails.

Three additional named cases exercise the positive theorem's boundary and
sharpness. The diagonal \((\alpha,\beta)=(0,0)\) is evaluated exactly on
\(p=(1,1/4,1/2,1)\). At the same prices with \(\lambda=7/8\) and
\((\alpha,\beta)=(0,-1)\), unequal post-boundary floor differences are
strictly aligned and cash crosses once, exhibiting a strict interior member.
Finally,

\[
p=(1,2/3,1/2,2/3),\quad\lambda=3/4,\quad
(\alpha,\beta)=(0,-1)
\]

violates guardrail alignment at date three but still has cash signs
\(-,-,+\). The same-period score component outweighs the misaligned floor
component, so net forcing retains the correct sign. This exact component-
cancellation obstruction proves that alignment is sufficient but not
necessary.

## Reproducibility record and limits

The observed reference run used CPython 3.12.13 on Linux x86-64 and completed
in 4.159 seconds in one process. Code versions are identified by SHA-256:

- `reproducibility/arbitrary_horizon.py`:
  `5dbd9b34fc91d3315a90af6814d797fef10c65df1bb140c2edb8ee661896d47e`;
- `reproducibility/weak_single_valley_search.py`:
  `de46e79bb08b62fc2a3350adfe4830cc4e46f11d826d0ebb8fc50742c701099f`;
- `reproducibility/cash_single_crossing.py`:
  `4d5d7536bf644ae7aeec2c675cf19d45aee987f24d6a8593690a579cd183a572`;
- `reproducibility/cash_single_crossing_search.py`:
  `038241095989f2bbd22b159db5cf2747563da38708540eafc1fd7956df8ee735`;
- `reproducibility/checks/check_cash_single_crossing_mechanism.py`:
  `b71d661172906d6335cc73a1358fd7d47da5a33e1b9cd4835da382d4c1e0d812`.

The SHA-256 of the deterministic JSON string, before the command's final
newline, is
`19b703d36a6cedf094cfd8d2b0dd6a2a876dec22d06249d19139804e215b05f9`.

The computational limit is exactly the declared finite Cartesian grid. The
counts are observations, not probabilities and not proof outside that grid.
The exact named witness alone disproves the universal conjecture; the
reference-aligned positive statement is established analytically in the
canonical theorem and evidence note.

[^ticket-03]: [Characterize the cash single-crossing mechanism](../../.scratch/smartdca/efforts/arbitrary-horizon-performance/issues/03-characterize-cash-single-crossing-mechanism.md)
[^mechanism-note]: [Differential guardrail feedback defeats cash single crossing](../../research/notes/cash-single-crossing-mechanism.md)
[^accounting-seam]: [Arbitrary-horizon cash-timing identity and exact-rational verification seam](../../research/notes/arbitrary-horizon-accounting-verification-seam.md)
[^gini-region]: [Prior theory for the corrected normalization](../../research/notes/prior-theory-corrected-out-quasi-gini.md)
