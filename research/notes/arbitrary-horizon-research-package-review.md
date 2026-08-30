---
profile: smartdca-okf/0.5
type: research-note
title: "Independent review of the arbitrary-horizon research package"
description: "Ledger-first re-derivation, exact-witness reproduction, and publication audit of the complete arbitrary-horizon performance result."
knowledge_role: evidence
status: stable
sources:
  - id: ticket-05
    title: "Review and publish the arbitrary-horizon research package"
    resource: .scratch/smartdca/efforts/arbitrary-horizon-performance/issues/05-review-publish-research-package
    source_kind: internal
  - id: effort-spec
    title: "Arbitrary-horizon guarded SmartDCA performance"
    resource: .scratch/smartdca/efforts/arbitrary-horizon-performance/spec
    source_kind: internal
  - id: accounting
    title: "Arbitrary-horizon cash-timing identity and exact-rational verification seam"
    resource: research/notes/arbitrary-horizon-accounting-verification-seam
    source_kind: internal
  - id: falsification
    title: "Weak single-valley prices do not determine guarded SmartDCA advantage"
    resource: research/notes/weak-single-valley-advantage-falsification
    source_kind: internal
  - id: mechanism
    title: "Differential guardrail feedback defeats cash single crossing"
    resource: research/notes/cash-single-crossing-mechanism
    source_kind: internal
  - id: boundary
    title: "Exact arbitrary-horizon evaluation-price boundary for guarded SmartDCA"
    resource: research/notes/arbitrary-horizon-performance-boundary
    source_kind: internal
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-24T21:29:22Z
generation_run: urn:uuid:c8785a76-9c52-4377-ab6e-4a44c3e403e6
verified:
  - by: openai-codex/independent-math-review-0.1
    at: 2026-08-24T21:12:56Z
    review_run: urn:uuid:1694bf39-9777-4b36-bd09-5c6abc74460e
  - by: openai-codex/standards-review-0.1
    at: 2026-08-24T21:31:55Z
    review_run: urn:uuid:8185820b-9b80-4607-91f0-43335cfbdff5
  - by: openai-codex/spec-review-0.1
    at: 2026-08-24T21:31:55Z
    review_run: urn:uuid:8da58364-ea0f-42bb-a729-d559abe6e7e7
---
# Independent review of the arbitrary-horizon research package

## Verdict

The package is scientifically cleared for publication. An independent
ledger-first derivation agrees with the cash-timing theorem and the exact
affine evaluation-price boundary; a separate standard-library `Fraction`
implementation reproduces every decisive ticket 01--04 witness. The review
found no mathematical or computational error. Its initial audit flagged the
experiment reports' older shared-engine fingerprint as a provenance concern.
Standards review established that the fingerprint correctly binds each
original run; a separately identified publication verification run now
records the current code and reproduced outputs without altering those
reports.[^ticket-05][^effort-spec]

## Independence protocol and derivation

The reviewer first read the comparison model, policy ledger contract, and
canonical statements, while withholding the three producing proof notes. From

\[
C_t=C_{t-1}+d_t-x_t
\]

the reviewer independently obtained

\[
x_t=d_t+C_{t-1}-C_t
\]

and hence, for any fully funded strategy (S),

\[
Q_n^S-Q_n^{DCA}
=\sum_{t<n}C_t^S\left(\frac1{p_{t+1}}-\frac1{p_t}\right)
-\frac{C_n^S}{p_n}.
\]

Direct substitution into cash-inclusive terminal wealth gives

\[
W_n^S-W_n^{DCA}
=C_n^S\left(1-\frac P{p_n}\right)
+P\sum_{t<n}C_t^S\left(\frac1{p_{t+1}}-\frac1{p_t}\right).
\]

For two policies, replace \(C_t^S\) by
\(D_t=C_t^S-C_t^T\). With

\[
H=D_n,
\qquad
U=\sum_{t<n}D_t\left(\frac1{p_{t+1}}-\frac1{p_t}\right)
-\frac{D_n}{p_n},
\]

the derivation gives both \(U=Q_n^S-Q_n^T\) and

\[
W_n^S(P)-W_n^T(P)=H+PU.
\]

Opposite signs of \(H\) and \(U\) therefore give the unique positive root
\(-H/U\); like signs give a fixed strict sign; one zero leaves the sign of the
other coefficient for \(P>0\); and \(H=U=0\) gives an identity tie. At
\(P=p_n\), terminal cash cancels, and splitting the reciprocal-price
increments at the first trough gives \(p_n(A-B)\). Only after recording this
derivation did the reviewer compare it with the producing notes, where it
agreed term for term.[^accounting][^boundary]

## Exact witness reproduction

The independent replay implemented the policy recurrence, corrected
reference, score, clipped unit floor, direct terminal wealth, cash-timing
wealth, and terminal units without importing repository code.

| Effort slice | Independently reproduced exact result |
|---|---|
| Ticket 01, one purchase | \(x=3/2\), \(C=1/2\), and corrected-minus-DCA wealth \(-1\). |
| Ticket 01, two-policy flip | Corrected-minus-DCA \(=1/48\); neutral-minus-DCA \(=-1/32\). |
| Constant-price boundary | At \(P=(1/2,1,2)\), corrected-minus-DCA \(=(1/4,0,-1/2)\). |
| Two-date all-win witness | Terminal cash \(1/12\); gap \(167/4\). |
| Three-date beta witness | \(\beta=-1:(R,a,\Delta)=(8/5,4/9,-1/36)\); \(\beta=1:(5/2,5/9,1/144)\); diagonal \((2,1/2,-1/96)\). |
| Minimum DCA loss | \(p=(1,1,1,1)\), \(P=2\): \(-7/8\). |
| Minimum neutral loss | \(p=(1,2/3,2/3,2/3)\), \(P=1/3\): \(-273/5984\); floors disabled \(-373/5984\); floor contribution \(25/1496\). |
| Genuine-cycle DCA loss | \(p=(1,2/3,2/3,1)\): \(-49/264\). |
| Strict-cycle DCA loss | \(p=(1,1/2,2/3,1)\): \(-7/32\). |
| Strict/genuine neutral loss | \(p=(1,2/3,1,2)\): \(-109/8640\); floors disabled \(49/360\); floor contribution \(-257/1728\). |
| Minimum cash double reversal | \(p=(1,2,32,32)\): \(D=(0,3/128,-665/147712,3183/308480)\). |
| Strict cash double reversal | \(p=(1,1/16,1,8)\): \(D=(0,-12495/1052672,174032415/616865792,-142575068237/2843751301120)\); floors disabled \(D^\circ=(0,-765/1028,70545/602408,585268881/555420176)\). |
| Common-floor sufficient case | \(D=(0,-7/48,-7/96,41/320)\). |
| Diagonal boundary case | \(D=(0,-39/160,-39/320,389/1920)\). |
| Strict aligned all-floor case | \(D=(0,-39/640,133/2304,22903/115200)\). |
| Alignment non-necessity | \(D=(0,-11/240,-397/4992,841/149760)\); date-three score/floor components \(-125/1664\) and \(11/832\). |
| Aligned joint win | \((H_D,U_D)=(16807/28800,-7199/9600)\), \((H_0,U_0)=(22903/115200,-5171/38400)\); at \(P=1/2\), gaps \(12017/57600\) and \(30293/230400\). |
| Same ledger, high-price loss | At \(P=2\), gaps \(-26387/28800\) and \(-8123/115200\). |
| Aligned joint loss | \(p=(1,2/3,1,2)\), \(P=2\): gaps \(-1141/2160\) and \(-109/8640\). |
| Misaligned all-price neutral win | \((H_0,U_0)=(841/149760,841/99840)\); DCA and neutral gaps \(389/18720\) and \(841/74880\). |
| Negative-terminal-cash win | \((H_0,U_0)=(-103/832,2003/8320)\); DCA and neutral gaps \(57/520\) and \(229/6240\). |
| Nontrivial flat-trough tie | \((H_0,U_0)=(-59/240,59/120)\); DCA gap \(1/4\), neutral gap \(0\). |
| Outside-alignment failure | Double-reversal neutral gap \(-339578505/616865792\). |
| Safety endpoint | At \(\lambda=1\), both selectors buy every deposit; all \(H\), \(U\), and wealth gaps are zero. |

The values agree with the accounting, falsification, mechanism, and final
boundary evidence, including floor-disabled attribution rather than an
activation-flag proxy.[^accounting][^falsification][^mechanism][^boundary]

## Assumptions and branch audit

The review checked positive purchase and evaluation prices, common
nonnegative deposits, cash-inclusive wealth, long-only buy-only purchases,
and no borrowing. Within the restricted mechanism and search family it also
checked equal positive deposits, \(f=\mathrm{id}\), \(0<\lambda<1\),
\(\alpha<1\), and \(\alpha\beta\le0\). The cited primary-source result for
the weighted Gini region supports the last coordinatewise-monotonicity
condition.[^mechanism]

The replay covers every named weak and strict valley, endpoint and flat
trough, constant path, and explicit non-valley path; both comparators; every
affine sign branch; finite roots; zero coefficients; identical-ledger and
nontrivial ties; active, inactive, repeated, unequal, common, and clipping-
boundary floors; floor-disabled attribution; and the \(\lambda=1\) collapse.
The safety statement remains attributable solely to the unit floor. No
stochastic, universal-dominance, parameter-superiority, or novelty conclusion
is inferred.

## Reproducibility, provenance, and link audit

All eleven scientific checks passed, including the clean-room replay preserved
as
[the independent publication check](../../reproducibility/checks/check_arbitrary_horizon_publication_review.py).
Its SHA-256 is
`f25519530fa0f151ace68a732f004a532cd92bd873167b4b04b6596fd6cb23c4`.
The 32 validator fixtures and strict OKF
validation also passed.

The separate publication verification run
`urn:uuid:8fd14f92-d220-4e36-ad3a-32a008e4b541` executed
`python -m reproducibility.weak_single_valley_search` and
`python -m reproducibility.cash_single_crossing_search` from
2026-08-24T21:26:10Z through 2026-08-24T21:27:03Z on CPython 3.12.13,
Linux x86-64. Its code identities were:

- `reproducibility/arbitrary_horizon.py`:
  `35ff108c5b58e992878b82f47e294e2fb0cbf0992e7a89dff141c5c22eb4f2f1`;
- `reproducibility/weak_single_valley_search.py`:
  `de46e79bb08b62fc2a3350adfe4830cc4e46f11d826d0ebb8fc50742c701099f`;
- `reproducibility/cash_single_crossing.py`:
  `4d5d7536bf644ae7aeec2c675cf19d45aee987f24d6a8593690a579cd183a572`;
- `reproducibility/cash_single_crossing_search.py`:
  `038241095989f2bbd22b159db5cf2747563da38708540eafc1fd7956df8ee735`.

The deterministic outputs reproduced:

- 2,274 weak single-valley paths and 61,398 scenarios, with exact
  corrected-versus-DCA win/tie/loss counts \(23210/56/38132\), neutral counts
  \(44329/1036/16033\), no exact-domain rejection, and JSON SHA-256
  `d6756a20dcd13bc374a2941276eb51fed86ade73d3cffffb20327e6636fcd082`;
- 559 cash-mechanism paths and 11,739 scenarios, with 27 multiple reversals,
  5,371 aligned cases, no aligned failure, no exact-domain rejection, and JSON
  SHA-256
  `19b703d36a6cedf094cfd8d2b0dd6a2a876dec22d06249d19139804e215b05f9`.

The experiment reports correctly retain their original run IDs, runtimes, and
pre-ticket-04 shared-engine SHA-256
`5dbd9b34fc91d3315a90af6814d797fef10c65df1bb140c2edb8ee661896d47e`.
The initial audit proposed replacing that value with the current hash, but
Standards review found that doing so would conflate two executions. Restoring
the original one-run records and recording the publication run separately
above resolves the provenance finding.

The publication-structure re-review then required preserving the clean-room
replay as a named CI check, using descriptive exact-rational names, and
synchronizing lifecycle state, freshness, the root inventory, and the
immutable event log. Those publication findings were resolved before
promotion.

Every active scientific and operational artifact link resolves. Six old
links in immutable `log.md` events name the pre-migration locations of tickets
20--25. The later migration event links the live effort paths; rewriting the
historical events would violate the immutable-log rule. The reserved-history
links are therefore a documented nonblocking limitation, and strict
validation accepts them.

## Publication conclusion

The package has one canonical result, one detailed proof, exact executable
checks—including a repository-independent standard-library replay—and this
independent review record. Its strongest claim is the exact
terminal cash-and-unit boundary at every finite horizon; weak single-valley
geometry and cash single crossing alone remain insufficient. The empirical
study, dynamic safety ratchet, minimax policy design, and manuscript assembly
were not advanced.[^ticket-05]

[^ticket-05]: [Review and publish the arbitrary-horizon research package](../../.scratch/smartdca/efforts/arbitrary-horizon-performance/issues/05-review-publish-research-package.md)
[^effort-spec]: [Arbitrary-horizon guarded SmartDCA performance](../../.scratch/smartdca/efforts/arbitrary-horizon-performance/spec.md)
[^accounting]: [Arbitrary-horizon cash-timing identity and exact-rational verification seam](arbitrary-horizon-accounting-verification-seam.md)
[^falsification]: [Weak single-valley prices do not determine guarded SmartDCA advantage](weak-single-valley-advantage-falsification.md)
[^mechanism]: [Differential guardrail feedback defeats cash single crossing](cash-single-crossing-mechanism.md)
[^boundary]: [Exact arbitrary-horizon evaluation-price boundary for guarded SmartDCA](arbitrary-horizon-performance-boundary.md)
