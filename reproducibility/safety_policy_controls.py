#!/usr/bin/env python3
"""Fail-closed controls for the thesis impossibility-to-safety policy slice."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manuscript.citation_controls import (  # noqa: E402
    extract_bibtex_keys,
    extract_latex_citation_keys,
)
from reproducibility.control_support import (  # noqa: E402
    extract_latex_chapter as _chapter,
    index_records as _record_map,
    read_json_object,
    read_text,
    require_terms as _require_terms,
    validate_repository_file,
)


RESOLVED_REVIEW_STATES = {"accepted", "reviewed"}
SAFETY_CLAIMS = {
    "claim-thm-causal-dca-impossibility": "ch:safety/thm:dca-impossibility",
    "claim-thm-epsilon-guardrail": "ch:safety/thm:epsilon-guardrail",
    "claim-def-guarded-policy": "ch:safety/def:guarded-policy",
    "claim-figure-policy-architecture": "ch:safety/fig:policy-architecture",
}
SAFETY_NOTATION = {
    "notation-safety-factor": "ch:safety/sec:safety-relaxation",
    "notation-coverage-cushion": "ch:safety/sec:unit-guardrail",
    "notation-available-cash": "ch:safety/sec:unit-guardrail",
    "notation-mandatory-floor": "ch:safety/sec:unit-guardrail",
}
SAFETY_NONCLAIMS = {
    "nonclaim-universal-superiority",
    "nonclaim-frictional-safety",
}
REQUIRED_CHAPTER_CITATIONS = {
    "blackperold1992",
    "burzoni2019",
    "conttankov2009",
    "grossmanzhou1993",
}


class SafetyPolicyControlError(ValueError):
    """Raised when Chapter 4 or its proof appendix drifts from authority."""


def _validate_paths(
    root: Path,
    identifier: str,
    paths: object,
    errors: list[str],
) -> None:
    if not isinstance(paths, list) or not paths:
        errors.append(f"{identifier}: no authority paths declared")
        return
    for value in paths:
        if not isinstance(value, str):
            errors.append(f"{identifier}: invalid authority path")
            continue
        validate_repository_file(root, identifier, value, errors)


def _validate_claim_authority(
    root: Path,
    identifier: str,
    record: dict[str, object],
    errors: list[str],
) -> None:
    authority = record.get("authority")
    if not isinstance(authority, list) or not authority:
        errors.append(f"{identifier}: no claim authority declared")
        return
    paths: list[str] = []
    for entry in authority:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            errors.append(f"{identifier}: invalid claim authority")
            continue
        paths.append(entry["path"])
    _validate_paths(root, identifier, paths, errors)


def audit_impossibility_safety_policy_architecture(
    repository_root: Path,
) -> dict[str, object]:
    """Audit the full comparison model and impossibility result in Chapter 4."""

    root = repository_root.resolve()
    errors: list[str] = []
    thesis = read_text(root / "manuscript/source/thesis.tex", errors)
    bibliography = read_text(
        root / "manuscript/bibliography/references.bib", errors
    )
    claims = _record_map(
        read_json_object(root / "manuscript/controls/claims.json", errors)
    )
    notation = _record_map(
        read_json_object(root / "manuscript/controls/notation.json", errors)
    )
    nonclaims = _record_map(
        read_json_object(root / "manuscript/controls/non-claims.json", errors)
    )
    chapter = _chapter(thesis, "Causal Impossibility and Safety Architecture")
    appendix = _chapter(thesis, "Mathematical Proofs")
    if not chapter:
        errors.append("missing Chapter 4 impossibility-to-safety architecture")
    if not appendix:
        errors.append("missing Appendix A mathematical proofs")

    _require_terms(
        chapter,
        (
            r"\label{thm:dca-impossibility}",
            "every finite positive price path",
            "every nonnegative exogenous deposit sequence",
            "causal",
            "long-only, buy-only, fully funded",
            "same deposits and horizon",
            "no borrowing or leverage",
            "cash carries without interest",
            "terminal wealth includes unused cash",
            "common evaluation price",
            r"W_n^S(P)\geq W_n^D(P)",
            "DCA transaction by transaction",
        ),
        "impossibility-model assumption",
        errors,
    )
    _require_terms(
        chapter,
        (
            r"\label{sec:safety-relaxation}",
            r"\lambda=1-\varepsilon",
            r"\varepsilon\in[0,1)",
            r"W_n^S(P)\geq\lambda W_n^D(P)",
            "for every admissible price path and deposit sequence",
            "For $\\varepsilon>0$, this is not dominance: a safe policy may finish below DCA",
            "economically distinct causal rule that retains a universal DCA-relative floor",
            r"\label{sec:unit-guardrail}",
            r"K_{t-1}^S=Q_{t-1}^S-\lambda Q_{t-1}^D",
            r"B_t^S=C_{t-1}^S+d_t",
            r"m_t^S(\lambda)=\left[\lambda d_t-p_tK_{t-1}^S\right]_+",
            r"0\leq m_t^S(\lambda)\leq\lambda d_t\leq d_t\leq B_t^S",
            r"b_t^S=m_t^S(\lambda)+a_t\left(B_t^S-m_t^S(\lambda)\right)",
            r"0\leq a_t\leq1",
            "funded discretionary allocation",
            r"\label{thm:epsilon-guardrail}",
        ),
        "relative-wealth floor or unit guardrail",
        errors,
    )
    _require_terms(
        chapter,
        (
            r"\label{def:guarded-policy}",
            r"\input{../generated/policy-architecture.tex}",
            "The corrected-mean score is only the discretionary selector",
            "causal, fully funded, long-only, and buy-only",
            r"0\leq m_t^c(\lambda)\leq b_t^c\leq B_t^c",
            r"C_t^c=(1-a_t)\left(B_t^c-m_t^c(\lambda)\right)\geq0",
            r"K_t^c &=K_{t-1}^c+\frac{b_t^c-\lambda d_t}{p_t}",
            r"W_t^c(P)-\lambda W_t^D(P)=C_t^c+P K_t^c\geq0",
            "At $\\lambda=1$ the discretionary interval collapses",
            "regardless of the corrected-mean score",
            "The safety theorem is frictionless",
            "Net-of-cost results are finite empirical robustness evidence outside the current safety theorem",
        ),
        "complete guarded-policy property",
        errors,
    )

    asset_relative_path = "manuscript/generated/policy-architecture.tex"
    asset = read_text(root / asset_relative_path, errors)
    _require_terms(
        asset,
        (
            "claim-figure-policy-architecture",
            "candidate-created conceptual diagram",
            r"\label{fig:policy-architecture}",
            "mandatory safety branch",
            "discretionary signal branch",
            "funded purchase",
        ),
        "policy-architecture asset",
        errors,
    )
    _require_terms(
        appendix,
        (
            r"\label{sec:proof-dca-impossibility}",
            r"\label{eq:appendix-dca-gap}",
            "induction applies after every external history",
            r"r\left(1-\frac{M}{p_t}\right)<0",
            r"\label{sec:proof-epsilon-guardrail}",
            "Prefix coverage is sufficient",
            "Prefix coverage is necessary",
            r"\label{eq:appendix-prefix-deficit-bound}",
            r"L\delta>2(B+F)",
            "Local floor equivalence and feasibility",
            r"b_t^S\geq\left[\lambda d_t-p_tK_{t-1}^S\right]_+",
            r"a_t=\frac{b_t^S-m_t^S}{B_t^S-m_t^S}",
            "Exact worst-case factor",
            r"\Gamma(S)",
            "fixed reserve rule",
        ),
        "appendix impossibility or guardrail proof",
        errors,
    )

    ordered_labels = (
        "thm:dca-impossibility",
        "sec:safety-relaxation",
        "thm:epsilon-guardrail",
        "def:guarded-policy",
        "sec:frictionless-safety-boundary",
    )
    positions = [chapter.find(f"\\label{{{label}}}") for label in ordered_labels]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        errors.append(
            "Chapter 4 order must be impossibility, safety relaxation, "
            "guardrail, guarded policy, and frictionless boundary"
        )

    for identifier, expected_location in SAFETY_CLAIMS.items():
        record = claims.get(identifier)
        if record is None:
            errors.append(f"missing safety-policy claim {identifier!r}")
            continue
        if record.get("manuscript_location") != expected_location:
            errors.append(
                f"{identifier}: manuscript_location must be {expected_location!r}"
            )
        if record.get("mandatory") is not True:
            errors.append(f"{identifier}: safety-policy claim must be mandatory")
        if record.get("review_state") not in RESOLVED_REVIEW_STATES:
            errors.append(f"{identifier}: safety-policy claim must be resolved")
        _validate_claim_authority(root, identifier, record, errors)

    figure_record = claims.get("claim-figure-policy-architecture", {})
    if figure_record.get("entry_type") != "conceptual-figure":
        errors.append(
            "claim-figure-policy-architecture: entry_type must identify a "
            "realized conceptual-figure"
        )
    figure_authority = figure_record.get("authority", [])
    figure_paths = {
        entry.get("path")
        for entry in figure_authority
        if isinstance(entry, dict)
    }
    if asset_relative_path not in figure_paths:
        errors.append(
            "claim-figure-policy-architecture: generated asset authority is missing"
        )

    for identifier, expected_first_use in SAFETY_NOTATION.items():
        record = notation.get(identifier)
        if record is None:
            errors.append(f"missing safety-policy notation {identifier!r}")
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

    for identifier in SAFETY_NONCLAIMS:
        record = nonclaims.get(identifier)
        if record is None:
            errors.append(f"missing safety-policy non-claim {identifier!r}")
            continue
        if record.get("mandatory") is not True:
            errors.append(f"{identifier}: non-claim must be mandatory")
        if record.get("review_state") not in RESOLVED_REVIEW_STATES:
            errors.append(f"{identifier}: non-claim must be resolved")
        affected_locations = record.get("affected_locations", [])
        if not isinstance(affected_locations, list) or "ch:safety" not in affected_locations:
            errors.append(f"{identifier}: ch:safety must be an affected location")
        _validate_paths(root, identifier, record.get("authority_paths"), errors)

    bibliography_keys = extract_bibtex_keys(bibliography)
    chapter_citations = extract_latex_citation_keys(chapter)
    for key in sorted(chapter_citations - bibliography_keys):
        errors.append(f"undefined Chapter 4 citation {key!r}")
    for key in sorted(REQUIRED_CHAPTER_CITATIONS - chapter_citations):
        errors.append(f"Chapter 4 is missing required citation {key!r}")
    for identifier in (
        "claim-thm-causal-dca-impossibility",
        "claim-thm-epsilon-guardrail",
    ):
        record = claims.get(identifier, {})
        citation_keys = record.get("citation_keys", [])
        if not isinstance(citation_keys, list) or not citation_keys:
            errors.append(f"{identifier}: citation_keys must be declared")
            continue
        for key in citation_keys:
            if key not in bibliography_keys:
                errors.append(f"{identifier}: undefined bibliography key {key!r}")
            if key not in chapter_citations:
                errors.append(f"{identifier}: citation {key!r} is absent from Chapter 4")

    if errors:
        raise SafetyPolicyControlError("\n".join(errors))

    return {
        "status": "passed",
        "policy_asset": asset_relative_path,
        "appendix_proof_count": 2,
        "claim_count": len(SAFETY_CLAIMS),
        "notation_count": len(SAFETY_NOTATION),
        "nonclaim_count": len(SAFETY_NONCLAIMS),
        "chapter_citation_count": len(chapter_citations),
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
        audit_impossibility_safety_policy_architecture(args.repository_root)
    except SafetyPolicyControlError as error:
        print(error)
        print("SAFETY POLICY CONTROL FAILED")
        return 1
    print("SAFETY POLICY CONTROL PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
