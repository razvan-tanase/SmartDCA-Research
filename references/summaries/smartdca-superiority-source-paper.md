# Source summary: SmartDCA superiority (arXiv:2308.05200v1)

This is the source the project exists to audit. Every mathematical result here
either classifies what the paper proves or repairs something it asserts without
proof.

The paper's claims are recorded here as *the paper's claims*. Where this project
has established that a claim is false or unproved, the summary says so and
links the corrected statement; it never attributes the project's mathematics
to the paper.

## Snapshot identity

The snapshot is [arXiv:2308.05200v1](https://arxiv.org/abs/2308.05200v1)
(2023), *SmartDCA superiority*, by Emmanuel Calvet, Luca Herranz-Celotti, and
Karim Valimamode, who declare equal contribution. The exact bytes are the
697,854-byte PDF preserved at
[`references/2308.05200v1.pdf`](../2308.05200v1.pdf), with SHA-256
`4dda676c7e4c61dd64b186d3a44d408b3019e962ba0f137f5e1c63fc7cdfeda2`.
The document is 14 pages and typeset in a journal template whose running head
reads `VOL. 1 NO. 53 SMARTDCA SUPERIORITY` and `PAPERS AND PROCEEDINGS 08
2023`; that header is template furniture, not evidence of journal publication,
and the citable identity is the arXiv version.

The recorded retrieval time, `2026-08-15T15:20:58Z`, is the Git-recorded time
at which the PDF entered this repository, not an observed fetch from arXiv. The
artifact predates this provenance note and was imported with the initial
research structure. The immutable `v1` identifier is therefore stronger
edition evidence than the timestamp.

## What the paper claims

The paper proposes **SmartDCA**: instead of investing a fixed cash amount at each purchase date as DCA does, invest an amount that varies inversely with the current price. Section II builds this up from a two-purchase example — regular investing gives an arithmetic-mean cost per unit, DCA gives a harmonic mean, and the basic SmartDCA rule gives the reciprocal of a contraharmonic mean — and proves the two-purchase inequality chain by elementary algebra, reducing it to \((x-y)^2\ge0\). Section II then generalizes to \(m\) purchases and to a parametrized family. Appendix A proves the \(m\)-purchase statement using the Cauchy–Schwarz inequality.[^source-paper]

Six numbered theorems carry the argument:[^source-paper]

| Theorem | Claim |
|---|---|
| 1 | Over \(m\) purchase events, SmartDCA gives a better price per unit than DCA. |
| 2 | For \(\rho\)-SmartDCA, a higher \(\rho\) gives a better price per unit. |
| 3 | For positive monotone increasing \(f\), the **out** quasi-Lehmer mean is monotone increasing in \(\rho\); the **in** version is not in general. |
| 4 | \((f)\)-SmartDCA (out) improves with \(\rho\), and since \(\rho=0\) recovers DCA, it therefore outperforms DCA. |
| 5 | An analogue of Theorem 3 holds for higher quasi-Lehmer moments. |
| 6 | An analogue holds for a monotone increasing expectation transform. |

The family is built in stages. \(\rho\)-SmartDCA raises the price ratio to a power \(\rho\), which the paper acknowledges can demand unbounded investment when the price falls far. To bound the demand it wraps the ratio in a positive monotone increasing \(f\) — `tanh`, a sigmoid, and a capped sine are the choices exercised — giving two variants distinguished only by where the power sits relative to \(f\): the *in* form invests proportionally to \(f\bigl((p_r/p_i)^\rho\bigr)\) and the *out* form to \(f(p_r/p_i)^\rho\), against a reference price \(p_r\). With bounded \(f\) the per-purchase demand cannot exceed the base cost. Supporting this, Appendix B introduces the two **quasi-Lehmer means** at Eq. (54) as generalizations of the Lehmer mean, proves Theorem 3, and defines the higher moments at Eq. (71).

Eq. (70) is the construction this project audits. Appendix B introduces the **quasi-Gini means** — an out and an in form — explicitly "for the sake of completeness", notes that they reduce to the quasi-Lehmer means when the two parameters coincide, and calls them means. It states no proof of reflexivity, internality, continuity, homogeneity, or coordinatewise monotonicity, and gives no diagonal extension.[^source-paper] The concluding discussion presents the quasi-Gini generalization of Theorems 5 and 6 as a basis for designing "even more universal investment strategies" in future work, so Eq. (70) carries the paper's forward-looking claim rather than a load-bearing proof.

Section III is empirical. Prices drawn uniformly from \((0,2)\) show every variant achieving a lower price per unit than DCA even with no trend, with unbounded \(\rho\)-SmartDCA lowest but demanding what the paper itself calls absurd investments at low prices. Backtests then run on the S&P 500 through an ETF over rolling five-year windows from 1973 to 2023 and on Bitcoin over windows from 2018, reporting return on investment. The paper states that the assets were chosen because investment strategies "are of interest on an overall up-trend".[^source-paper]

## What the paper does not settle

The gap this whole project turns on is the **performance criterion**. Every theorem above is a statement about *price per unit* — total cash spent divided by total units acquired — and the strategies being compared do not spend the same total cash on the same path. A lower average acquisition cost under unequal spending is an accounting identity, not a claim about wealth; the paper never compares terminal wealth including uninvested cash on a common deposit sequence. So "outperforms DCA in any market condition" is proved for the paper's criterion and not for the comparison a fair investor faces.

Four further gaps are structural rather than arithmetical:

1. **No budget model.** There is no deposit sequence, no carried-cash account, and no feasibility constraint. The rule scales a base cost by a price ratio, so the cash it demands is an output rather than something a budget bounds; this is exactly the unboundedness the paper mitigates with a bounded \(f\) instead of with funding.
2. **The reference price is unpinned.** The rules are written against a reference price \(p_r\) whose selection and information timing are not specified. Whether the rule is causal depends entirely on that choice, and an ex-post reference — a full-sample mean or extremum — would make the comparison inadmissible.
3. **Eq. (70) is asserted, not proved.** The project's [audit](../../research/notes/source-out-quasi-gini-audit.md)[^audit] proves the construction is a mean exactly when the transform is the identity or the parameter gap is one, and that it has a global finite diagonal limit only for the identity transform. The corrected statement is governed by [the source out-functional mean classification](../../research/theorems/source-out-functional-mean-classification.md) and the repair by [the corrected out quasi-Gini mean](../../research/definitions/corrected-out-quasi-gini-mean.md).
4. **Empirical scope is favourable by construction.** Both assets are selected for long-term appreciation and the synthetic prices are independent uniform draws. Neither design can support a universal claim, and the paper does not report a case where a variant loses.

The paper also settles nothing about novelty. It names quasi-Lehmer and quasi-Gini means as new definitions; the project's [prior-theory positioning](../../research/notes/prior-theory-corrected-out-quasi-gini.md) locates the corrected construction inside established weighted Bajraktarević theory, with the parameter-gap-one slice already covered by Beckenbach–Gini–Lehmer results.

## Limits of this summary

The summary was prepared from a text extraction of the fingerprinted PDF in which Greek letters, subscripts, and some mathematical operators were lost, so it deliberately describes structure, criteria, and prose claims rather than transcribing formulae from the glyphs. Every equation number, theorem number, and page reference asserted here was cross-checked against the previously and independently reviewed [audit note](../../research/notes/source-out-quasi-gini-audit.md)[^audit], which read the same fingerprinted artifact; where the two could disagree, the audit note governs. Only the **out** construction is in scope for this project, so the paper's in variants and its Theorems 5 and 6 analogues are recorded as present and not analysed.

[^source-paper]: Emmanuel Calvet, Luca Herranz-Celotti, and Karim Valimamode, *SmartDCA superiority*, arXiv:2308.05200v1 (2023), fingerprinted snapshot at [`references/2308.05200v1.pdf`](../2308.05200v1.pdf)
[^audit]: [Audit of the source out quasi-Gini functional](../../research/notes/source-out-quasi-gini-audit.md)
