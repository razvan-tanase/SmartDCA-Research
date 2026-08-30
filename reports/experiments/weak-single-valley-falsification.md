# Exact-rational weak single-valley falsification search

## Verdict

The declared finite grid contains exact losses for the guarded corrected-mean
rule against both DCA and the neutral guarded selector. Weak single-valley
purchase prices therefore do not by themselves imply either proposed wealth
ordering. The failure persists on genuine strict decline-recovery cycles when
the evaluation price equals the last purchase price. The exact witnesses make
those universal conjectures false; the aggregate counts remain finite-grid
computational evidence rather than probabilities or an arbitrary-domain
theorem.[^ticket-02]

## Run contract

Run ID: `urn:uuid:a46848a1-4ba7-4e5e-abb7-7a9b7f2f2720`

Command:

```bash
python -m reproducibility.weak_single_valley_search
```

The command evaluates every scenario through the public exact-rational
three-policy ledger and emits a deterministic JSON record.[^accounting-seam]
No random sampling is used, so the seed is `none`.

| Input | Declared values |
|---|---|
| Horizons | (n=4,5,6,7,8) |
| Price normalization | (p_1=1) |
| Purchase-price levels | ({1/2,2/3,1,3/2,2}) |
| Equal deposits | (d_t=1) for every date |
| Safety factors, in order | (lambda=(1/2,1/4,3/4)) |
| Parameter pairs, in order | ((\alpha,\beta)=((0,-1),(0,1),(-1,0))) |
| Transform | (f=\mathrm{id}) |
| Evaluation multipliers, in order | (P/p_n=(1,1/2,2)) |

All parameter pairs have \(\alpha<1\) and \(\alpha\beta\le0\), the documented
coordinatewise-monotone classical Gini region.[^gini-region] The selected
unit-gap integer pairs keep every reference and score rational: the reference
is harmonic or arithmetic, and the score exponent is one or two. The run had
zero exact-domain rejections.

## Predicate, ordering, and pruning

For a positive price tuple, let (k) be its first minimum. The independent
predicate accepts exactly

\[
p_1\ge\cdots\ge p_k\le\cdots\le p_n.
\]

It is evaluated before any policy. Every retained tuple is checked again at
the search boundary. A **genuine cycle** has at least one strict decline and
one strict recovery. A **strict cycle** is strictly decreasing before its
interior trough and strictly increasing afterward.

Candidates are ordered lexicographically by:

1. horizon;
2. price complexity: number of distinct levels, number of transitions, total
   variation, then the price-level index tuple;
3. the declared safety-factor order;
4. the declared ((\alpha,\beta)) order;
5. the declared evaluation-multiplier order; and
6. deposit complexity, which is fixed at the unit equal-deposit normalization.

Two scale copies are pruned ex ante. Fixing (p_1=1) removes common
price/evaluation scaling. Fixing (d_t=1) removes common equal-deposit scaling:
for fixed prices and parameters, cash, purchases, units, and wealth gaps all
scale linearly with the common deposit. No outcome-dependent pruning is used.

The path counts are (53,134,301,616,1170) at horizons four through eight,
respectively: 2,274 paths in total, of which 2,059 are genuine cycles and 30
are strict cycles. Combining each path with three safety factors, three
parameter pairs, and three evaluation multipliers gives 61,398 evaluated
scenarios.

## Results

| Slice | Scenarios | Corrected vs DCA W/T/L | Corrected vs neutral W/T/L |
|---|---:|---:|---:|
| Complete grid | 61,398 | 23,210 / 56 / 38,132 | 44,329 / 1,036 / 16,033 |
| (P=p_n) | 20,466 | 3,250 / 55 / 17,161 | 16,122 / 945 / 3,399 |
| (P=p_n/2) | 20,466 | 19,472 / 0 / 994 | 18,777 / 45 / 1,644 |
| (P=2p_n) | 20,466 | 488 / 1 / 19,977 | 9,430 / 46 / 10,990 |
| Genuine cycles | 55,593 | 19,982 / 10 / 35,601 | 42,439 / 1 / 13,153 |
| Genuine cycles, (P=p_n) | 18,531 | 2,305 / 10 / 16,216 | 16,122 / 0 / 2,409 |
| Strict cycles, (P=p_n) | 270 | 9 / 0 / 261 | 227 / 0 / 43 |

These are classifications of a deliberately non-probabilistic grid. Their
only universal use is falsification: one valid loss is decisive against the
corresponding weak-advantage conjecture.

## Minimized and diagnostic witnesses

All witnesses use four unit deposits, (f=\mathrm{id}), and
((\alpha,\beta)=(0,-1)). They are named and replayed exactly by
[`check_weak_single_valley_falsification.py`](../../reproducibility/checks/check_weak_single_valley_falsification.py).

| Named witness | Prices; (P); (lambda) | Exact gap | Floor diagnosis |
|---|---|---:|---|
| Smallest corrected-vs-DCA loss | ((1,1,1,1)); (2); (1/2) | (-7/8) | Corrected and neutral coincide; active at dates 1–2. This is a guardrail/cash-carry failure, not a corrected-score effect. |
| Smallest corrected-vs-neutral loss | ((1,2/3,2/3,2/3)); (1/3); (1/2) | (-273/5984) | Corrected active at 1–2, neutral at 1–3. Disabling both floors gives (-373/5984), so the floor contribution is (+25/1496): nonzero, but not sign-changing. |
| Smallest strict-cycle DCA loss at (P=p_n) | ((1,1/2,2/3,1)); (1); (1/2) | (-7/32) | Corrected active at dates 1–2. The comparison is against DCA, so score-floor mediation is not applicable. |
| Smallest strict-cycle neutral loss at (P=p_n) | ((1,2/3,1,2)); (2); (3/4) | (-109/8640) | Both are active at dates 1–3. Disabling both floors gives (+49/360), so the floor contribution is (-257/1728) and reverses the sign. |

The first two rows are the smallest losses under the complete declared
ordering. The latter two deliberately rule out explanations based only on
constant prices, endpoint troughs, flat troughs, absent recovery, or an
evaluation price different from the last purchase price.

For every corrected-versus-neutral witness, the machine-readable record
defines the exact guardrail contribution as
\[
\Delta_{\mathrm{floor}}
=\bigl(W^{\mathrm{corrected}}-W^{\mathrm{neutral}}\bigr)_{\mathrm{guarded}}
-\bigl(W^{\mathrm{corrected}}-W^{\mathrm{neutral}}\bigr)_{\mathrm{floors\ disabled}}.
\]
Both replays use the same scenario and score rules; only the two guardrail
floors are set to zero. A nonzero value establishes contribution. The
corrected-versus-DCA rows are not score effects, so this diagnostic is marked
not applicable.

## Reproducibility record and limits

The observed reference run used CPython 3.12.13 on Linux x86-64 and completed
in 52.841328 seconds in one process. Code versions are identified by SHA-256:

- `reproducibility/arbitrary_horizon.py`:
  `5dbd9b34fc91d3315a90af6814d797fef10c65df1bb140c2edb8ee661896d47e`;
- `reproducibility/weak_single_valley_search.py`:
  `de46e79bb08b62fc2a3350adfe4830cc4e46f11d826d0ebb8fc50742c701099f`;
- `reproducibility/checks/check_weak_single_valley_falsification.py`:
  `7f267820a825054b872b6dba2b465b5b02ebffbe1d6d1fe138c074c0316b7e49`.

The SHA-256 of the deterministic JSON string, before the command's final
newline, is
`d6756a20dcd13bc374a2941276eb51fed86ade73d3cffffb20327e6636fcd082`.

The computational limit is exactly the declared finite Cartesian grid. It
does not cover other rational levels, continuous parameter regions, unequal
deposits, other transforms, or horizons outside four through eight. Finite
non-discovery would not have proved a positive claim; here the exact named
witnesses do prove that weak and even strict single-valley structure is
insufficient for the two proposed universal orderings.

[^ticket-02]: [Falsify the weak single-valley advantage conjecture](../../.scratch/smartdca/efforts/arbitrary-horizon-performance/issues/02-falsify-weak-single-valley-advantage.md)
[^accounting-seam]: [Arbitrary-horizon cash-timing identity and exact-rational verification seam](../../research/notes/arbitrary-horizon-accounting-verification-seam.md)
[^gini-region]: [Prior theory for the corrected normalization](../../research/notes/prior-theory-corrected-out-quasi-gini.md)
