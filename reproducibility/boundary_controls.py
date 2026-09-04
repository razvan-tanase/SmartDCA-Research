#!/usr/bin/env python3
"""Fail-closed controls for the thesis finite/arbitrary-horizon boundary slice."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reproducibility.control_support import (  # noqa: E402
    extract_latex_chapter,
    extract_latex_section,
    index_records,
    read_json_object,
    read_text,
    require_terms,
    validate_repository_file,
)


RESOLVED_REVIEW_STATES = {"accepted", "reviewed"}
BOUNDARY_CLAIMS = {
    "claim-thm-two-purchase-boundary": "ch:boundaries/thm:two-purchase",
    "claim-thm-three-purchase-boundary": "ch:boundaries/thm:three-purchase",
    "claim-thm-cash-timing-identity": "ch:boundaries/thm:cash-timing",
    "claim-thm-cash-single-crossing": "ch:boundaries/thm:cash-single-crossing",
    "claim-thm-terminal-inventory-boundary": (
        "ch:boundaries/thm:terminal-inventory"
    ),
    "claim-computational-weak-valley-falsification": (
        "ch:boundaries/sec:single-valley-limit"
    ),
    "claim-computational-cash-crossing-counterexample": (
        "ch:boundaries/sec:guardrail-feedback"
    ),
    "claim-table-theorem-scope": "ch:boundaries/tab:theorem-scope",
}
BOUNDARY_NOTATION = {
    "notation-terminal-differences": "ch:boundaries/sec:terminal-inventory",
    "notation-cash-path-difference": "ch:boundaries/sec:cash-timing",
    "notation-two-purchase-ratios": "ch:boundaries/sec:two-purchase",
    "notation-two-purchase-components": "ch:boundaries/sec:two-purchase",
    "notation-three-purchase-ratio": "ch:boundaries/sec:three-purchase",
}
BOUNDARY_NONCLAIMS = {"nonclaim-universal-superiority"}
THEOREM_SCOPE_AUTHORITIES = {
    "research/theorems/two-purchase-guarded-smartdca-boundary.md",
    "research/notes/two-purchase-dca-win-loss-boundary.md",
    "research/theorems/three-purchase-corrected-mean-effect.md",
    "research/notes/three-purchase-corrected-mean-effect.md",
    "research/theorems/arbitrary-horizon-cash-timing-identity.md",
    "research/notes/arbitrary-horizon-accounting-verification-seam.md",
    "research/theorems/reference-aligned-guardrail-cash-single-crossing.md",
    "research/notes/cash-single-crossing-mechanism.md",
    "research/theorems/arbitrary-horizon-performance-boundary.md",
    "research/notes/arbitrary-horizon-performance-boundary.md",
    "reports/experiments/weak-single-valley-falsification.md",
    "reports/experiments/cash-single-crossing-search.md",
}


class BoundaryControlError(ValueError):
    """Raised when Chapter 5 or its case appendix drifts from authority."""


def audit_finite_arbitrary_horizon_boundaries(
    repository_root: Path,
) -> dict[str, object]:
    """Audit the manuscript's boundary chapter and supporting appendix."""

    root = repository_root.resolve()
    errors: list[str] = []
    thesis = read_text(root / "manuscript/source/thesis.tex", errors)
    claims = index_records(
        read_json_object(root / "manuscript/controls/claims.json", errors)
    )
    notation = index_records(
        read_json_object(root / "manuscript/controls/notation.json", errors)
    )
    nonclaims = index_records(
        read_json_object(root / "manuscript/controls/non-claims.json", errors)
    )
    chapter = extract_latex_chapter(thesis, "Exact Performance Boundaries")
    appendix = extract_latex_chapter(thesis, "Exact Performance Cases and Witnesses")
    two_purchase = extract_latex_section(
        chapter, "Two Purchases: an Evaluation-Price Boundary"
    )
    three_purchase = extract_latex_section(
        chapter, "Three Purchases: the First Beta-Sensitive Boundary"
    )
    cash_timing = extract_latex_section(
        chapter, "Cash Timing at an Arbitrary Finite Horizon"
    )
    valley_falsification = extract_latex_section(
        chapter, "Why a Single Valley Is Not a Performance Law"
    )
    guardrail_feedback = extract_latex_section(
        chapter, "Score Crossing versus Guarded Cash Crossing"
    )
    terminal_inventory = extract_latex_section(
        chapter, "Terminal Cash and Units Give the Exact Ledger Boundary"
    )
    evidence_roles = extract_latex_section(
        chapter, "Evidence Roles and Explicit Non-Conclusions"
    )

    if not chapter:
        errors.append("missing Chapter 5 exact performance boundaries")
    if not appendix:
        errors.append("missing Appendix B exact performance cases and witnesses")

    require_terms(
        chapter,
        (
            r"\label{ch:boundaries}",
            "Realized performance starts only after the causal purchase ledgers are fixed",
            "Finite witnesses, deterministic search, arbitrary-horizon accounting, and stochastic evaluation answer different questions",
        ),
        "boundary chapter contract",
        errors,
    )
    require_terms(
        two_purchase,
        (
            r"\label{sec:two-purchase}",
            r"\label{thm:two-purchase}",
            r"q=\frac{p_2}{p_1}",
            r"y=\frac{P}{p_2}",
            r"\delta=\frac{1-\lambda}{2}",
            r"c_a=(1-a)H",
            r"W_2^c(P)-W_2^D(P)=c_a-y(c_a-g)",
            r"For $0<\lambda<1$ and $d_1+d_2>0$, one has $c_a>0$",
            r"0<y<\frac{c_a}{c_a-g}",
            "corrected rule wins exactly for",
            "ties at equality, and loses above the threshold",
            r"If $c_a-g\leq0$, every finite $y>0$ is a strict win",
            "If both deposits vanish, both policies have zero wealth",
            r"at $\lambda=1$, every discretionary interval collapses and all cases tie DCA",
            "The parameter $\\beta$ is absent at two purchases",
            "does not state a win probability or an arbitrary-horizon law",
        ),
        "two-purchase boundary",
        errors,
    )
    require_terms(
        three_purchase,
        (
            r"\label{sec:three-purchase}",
            r"\label{thm:three-purchase}",
            "positive purchase and evaluation prices, nonnegative deposits",
            r"0<\lambda\leq1",
            r"h=p_3/p_2",
            r"g=\delta d_1h(1-q)+C_2^c(1-h)",
            r"W_3^c(P)-W_3^D(P)=c_\beta-y(c_\beta-g)",
            r"T_\beta=\frac{c_\beta}{c_\beta-g}",
            r"the rule wins below $T_\beta$, ties there, and loses above it",
            r"When $c_\beta-g\leq0$, set $T_\beta=+\infty$ and the fixed slice is all-win",
            r"At $\lambda=1$, or with three zero deposits, all comparisons tie",
            "second is beta-independent",
            "observed date-three price",
            r"\beta=-1",
            r"-\frac{1}{36}",
            r"\beta=1",
            r"\frac{1}{144}",
            "existence result, not a ranking of beta values",
        ),
        "three-purchase boundary",
        errors,
    )
    require_terms(
        cash_timing,
        (
            r"\label{sec:cash-timing}",
            r"\label{thm:cash-timing}",
            r"\Delta C_t^{S,T}=C_t^S-C_t^T",
            r"W_n^S(P)-W_n^T(P)",
            r"\Delta C_n^{S,T}\left(1-\frac{P}{p_n}\right)",
            r"\sum_{t=1}^{n-1}\Delta C_t^{S,T}",
            "model-general accounting identity",
            "Relative cash carried across a price fall has a positive coefficient",
            "relative cash carried across a rise has a negative one",
            "does not assign a favorable sign",
        ),
        "cash-timing identity",
        errors,
    )
    require_terms(
        valley_falsification,
        (
            r"\label{sec:single-valley-limit}",
            r"p_1\geq\cdots\geq p_k\leq\cdots\leq p_n",
            "61,398 exact scenarios",
            r"\left(1,\frac12,\frac23,1\right)",
            r"-\frac7{32}",
            r"\left(1,\frac23,1,2\right)",
            r"-\frac{109}{8640}",
            "not probabilities",
            "finite-grid computational evidence",
        ),
        "weak-single-valley falsification",
        errors,
    )
    require_terms(
        guardrail_feedback,
        (
            r"\label{sec:guardrail-feedback}",
            r"\label{thm:cash-single-crossing}",
            "For equal reference weights, the identity transform",
            r"\alpha<1",
            r"\alpha\beta\leq0",
            "On a weak single-valley path",
            "Suppose equal positive deposits are used",
            r"\Delta C_t^{c,0}",
            r"\Delta m_t=m_t^c-m_t^0",
            r"\Delta m_t\geq0\quad(t\leq j)",
            r"\Delta m_t\leq0\quad(t>j)",
            "reference-aligned guardrail feedback",
            "is a block of minus signs followed by a block of plus signs",
            "sufficient, not necessary",
            "policy-specific clipped floors can create a second cash reversal",
            "cash single crossing does not order terminal wealth",
        ),
        "qualified cash single crossing",
        errors,
    )
    require_terms(
        terminal_inventory,
        (
            r"\label{sec:terminal-inventory}",
            r"\label{thm:terminal-inventory}",
            r"H_T=C_n^c-C_n^T",
            r"U_T=Q_n^c-Q_n^T",
            r"W_n^c(P)-W_n^T(P)=H_T+P U_T",
            r"\frac{H_T}{-U_T}",
            r"\frac{-H_T}{U_T}",
            r"$H_T>0,\ U_T\geq0$ & none & corrected wins for every $P>0$",
            r"$H_T>0,\ U_T<0$ & $\frac{H_T}{-U_T}$ & win below, tie at, and loss above the root",
            r"$H_T=0,\ U_T>0$ & none & corrected wins for every $P>0$",
            r"$H_T=0,\ U_T=0$ & none & tie for every $P>0$",
            r"$H_T=0,\ U_T<0$ & none & corrected loses for every $P>0$",
            r"$H_T<0,\ U_T>0$ & $\frac{-H_T}{U_T}$ & loss below, tie at, and win above the root",
            r"$H_T<0,\ U_T\leq0$ & none & corrected loses for every $P>0$",
            "necessary-and-sufficient realized-ledger classification",
            "purchase ledgers, not prices alone",
            r"W_n^S(P)\geq\lambda W_n^D(P)",
            "belongs to the guardrail floor",
        ),
        "terminal-inventory boundary",
        errors,
    )
    require_terms(
        evidence_roles,
        (
            r"\label{tab:theorem-scope}",
            r"Finite witness (Sections \ref{thm:two-purchase} and \ref{thm:three-purchase})",
            r"Model-general identity (Section \ref{thm:cash-timing})",
            r"Conditional mechanism theorem (Section \ref{thm:cash-single-crossing})",
            r"Realized-ledger theorem (Section \ref{thm:terminal-inventory})",
            "Finite witness",
            "Finite deterministic search",
            "Model-general identity",
            "Conditional mechanism theorem",
            "Realized-ledger theorem",
            "Stochastic questions",
        ),
        "theorem scope table",
        errors,
    )
    require_terms(
        appendix,
        (
            r"\label{app:performance-cases}",
            "This appendix retains the exact cases, witnesses, and derivations",
            r"\label{sec:appendix-two-purchase}",
            r"\label{sec:appendix-three-purchase}",
            r"\label{sec:appendix-cash-timing}",
            r"\label{sec:appendix-valley-falsification}",
            r"\label{sec:appendix-guardrail-feedback}",
            r"\label{sec:appendix-affine-boundary}",
            r"\Delta_a=\frac1{48}",
            r"\Delta_{1/2}=-\frac1{32}",
            r"R_2(-1)=\frac85",
            r"R_2(1)=\frac52",
            r"\sum_{t=1}^{n}\frac{C_{t-1}^S-C_t^S}{p_t}",
            r"C^c=\left(\frac14,\frac7{24},\frac{31}{48},\frac{79}{80}\right)",
            r"\Delta C^{c,0}=\left(0,-\frac{11}{240},\frac{101}{1728}\right)",
            r"-\frac{142575068237}{2843751301120}",
            r"(H_D,U_D)=\left(\frac{16807}{28800},-\frac{7199}{9600}\right)",
            r"W_n^c(P)-W_n^T(P)=H_T+P U_T",
        ),
        "boundary appendix contract",
        errors,
    )

    for identifier, expected_location in BOUNDARY_CLAIMS.items():
        record = claims.get(identifier)
        if record is None:
            errors.append(f"missing boundary claim {identifier!r}")
            continue
        if record.get("manuscript_location") != expected_location:
            errors.append(
                f"{identifier}: manuscript_location must be {expected_location!r}"
            )
        if record.get("mandatory") is not True:
            errors.append(f"{identifier}: boundary claim must be mandatory")
        if record.get("review_state") not in RESOLVED_REVIEW_STATES:
            errors.append(f"{identifier}: boundary claim must be resolved")
        authority = record.get("authority")
        if not isinstance(authority, list) or not authority:
            errors.append(f"{identifier}: no claim authority declared")
        else:
            for entry in authority:
                if not isinstance(entry, dict) or not isinstance(
                    entry.get("path"), str
                ):
                    errors.append(f"{identifier}: invalid claim authority")
                    continue
                validate_repository_file(root, identifier, entry["path"], errors)
        manuscript_label = expected_location.rsplit("/", 1)[-1]
        if f"\\label{{{manuscript_label}}}" not in thesis:
            errors.append(
                f"{identifier}: manuscript is missing label {manuscript_label!r}"
            )

    table_record = claims.get("claim-table-theorem-scope", {})
    if table_record.get("entry_type") != "manuscript-summary-table":
        errors.append(
            "claim-table-theorem-scope: entry_type must identify the realized "
            "manuscript-summary-table"
        )
    table_authority = table_record.get("authority", [])
    if not isinstance(table_authority, list):
        table_authority = []
    table_authority_paths = {
        entry.get("path")
        for entry in table_authority
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    for missing_path in sorted(THEOREM_SCOPE_AUTHORITIES - table_authority_paths):
        errors.append(
            "claim-table-theorem-scope: missing required authority "
            f"{missing_path!r}"
        )

    three_purchase_scope = claims.get("claim-thm-three-purchase-boundary", {}).get(
        "scope", ""
    )
    require_terms(
        three_purchase_scope if isinstance(three_purchase_scope, str) else "",
        (
            "Exactly three purchase dates",
            "positive purchase and evaluation prices",
            "nonnegative deposits",
            "lambda in (0,1]",
            "not monotone benefit from increasing beta or a parameter ranking",
        ),
        "three-purchase claim scope",
        errors,
    )

    for identifier, expected_first_use in BOUNDARY_NOTATION.items():
        record = notation.get(identifier)
        if record is None:
            errors.append(f"missing boundary notation {identifier!r}")
            continue
        if record.get("first_use") != expected_first_use:
            errors.append(
                f"{identifier}: first_use must be {expected_first_use!r}"
            )
        if record.get("mandatory") is not True:
            errors.append(f"{identifier}: notation record must be mandatory")
        if record.get("review_state") not in RESOLVED_REVIEW_STATES:
            errors.append(f"{identifier}: notation record must be resolved")
        first_use_label = expected_first_use.rsplit("/", 1)[-1]
        if f"\\label{{{first_use_label}}}" not in thesis:
            errors.append(
                f"{identifier}: manuscript is missing first-use label "
                f"{first_use_label!r}"
            )

    component_notation = notation.get("notation-two-purchase-components", {})
    if component_notation.get("manuscript_notation") != "H, c_a, g":
        errors.append(
            "notation-two-purchase-components: manuscript_notation must avoid "
            "the corrected-policy superscript collision"
        )
    reconciliation = component_notation.get("reconciliation", "")
    require_terms(
        reconciliation if isinstance(reconciliation, str) else "",
        ("Use c_a", "corrected-policy superscript c"),
        "two-purchase notation reconciliation",
        errors,
    )

    for identifier in BOUNDARY_NONCLAIMS:
        record = nonclaims.get(identifier)
        if record is None:
            errors.append(f"missing boundary non-claim {identifier!r}")
            continue
        if record.get("mandatory") is not True:
            errors.append(f"{identifier}: non-claim must be mandatory")
        if record.get("review_state") not in RESOLVED_REVIEW_STATES:
            errors.append(f"{identifier}: non-claim must be resolved")
        affected_locations = record.get("affected_locations")
        if not isinstance(affected_locations, list) or "ch:boundaries" not in affected_locations:
            errors.append(f"{identifier}: ch:boundaries must be an affected location")
        authority_paths = record.get("authority_paths")
        if not isinstance(authority_paths, list) or not authority_paths:
            errors.append(f"{identifier}: no authority paths declared")
            continue
        for path in authority_paths:
            if not isinstance(path, str):
                errors.append(f"{identifier}: invalid authority path")
                continue
            validate_repository_file(root, identifier, path, errors)

    if errors:
        raise BoundaryControlError("\n".join(errors))

    return {
        "status": "passed",
        "finite_boundary_count": 2,
        "accounting_identity_count": 1,
        "finite_search_count": 1,
        "cash_crossing_condition_count": 1,
        "ledger_classification_count": 1,
        "scope_table_count": 1,
        "appendix_section_count": 6,
        "claim_count": len(BOUNDARY_CLAIMS),
        "notation_count": len(BOUNDARY_NOTATION),
        "nonclaim_count": len(BOUNDARY_NONCLAIMS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    try:
        audit_finite_arbitrary_horizon_boundaries(args.repository_root)
    except BoundaryControlError as error:
        print(error)
        print("BOUNDARY CONTROL FAILED")
        return 1
    print("BOUNDARY CONTROL PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
