#!/usr/bin/env python3
"""Fail-closed controls for the thesis deterministic/stochastic result slice."""

from __future__ import annotations

import argparse
import sys
import tempfile
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
from reproducibility.synthetic_evaluation_assets import (  # noqa: E402
    ASSET_NAMES,
    DETERMINISTIC_RUN_ID,
    STOCHASTIC_RUN_ID,
    SyntheticEvaluationAssetError,
    generate_synthetic_evaluation_assets,
)


RESOLVED_REVIEW_STATES = {"accepted", "reviewed"}
EVIDENCE_NOTE = (
    "research/notes/deterministic-stochastic-evaluation-manuscript-audit.md"
)
SYNTHETIC_CLAIMS = {
    "claim-empirical-synthetic-populations": (
        "ch:synthetic-results/sec:synthetic-evidence"
    ),
    "claim-empirical-deterministic-mixed": (
        "ch:synthetic-results/sec:deterministic"
    ),
    "claim-empirical-stochastic-sensitive": (
        "ch:synthetic-results/sec:stochastic"
    ),
    "claim-empirical-synthetic-mechanisms": (
        "ch:synthetic-results/sec:synthetic-mechanisms"
    ),
    "claim-empirical-synthetic-lambda-one-collapse": (
        "ch:synthetic-results/sec:safety-checks"
    ),
    "claim-empirical-observed-safety-floor": (
        "ch:synthetic-results/sec:safety-checks"
    ),
    "claim-empirical-synthetic-cost-scope": (
        "ch:synthetic-results/sec:synthetic-cost-scope"
    ),
}
ASSET_CLAIMS = {
    "claim-table-deterministic-primary": (
        "ch:synthetic-results/tab:deterministic-primary",
        "manuscript/generated/deterministic-evaluation.tex",
        "generated-results-table",
    ),
    "claim-figure-deterministic-layers": (
        "ch:synthetic-results/fig:deterministic-layers",
        "manuscript/generated/deterministic-evaluation.tex",
        "generated-results-figure",
    ),
    "claim-table-stochastic-primary": (
        "ch:synthetic-results/tab:stochastic-primary",
        "manuscript/generated/stochastic-evaluation.tex",
        "generated-results-table",
    ),
    "claim-figure-stochastic-attribution": (
        "ch:synthetic-results/fig:stochastic-attribution",
        "manuscript/generated/stochastic-mechanisms.tex",
        "generated-results-figure",
    ),
    "claim-table-stochastic-mechanisms": (
        "ch:synthetic-results/tab:stochastic-mechanisms",
        "manuscript/generated/stochastic-mechanisms.tex",
        "generated-results-table",
    ),
    "claim-table-deterministic-coverage-ranges": (
        "app:supplementary-results/tab:deterministic-coverage-ranges",
        "manuscript/generated/synthetic-supplementary.tex",
        "generated-results-table",
    ),
    "claim-table-deterministic-cost-ranges": (
        "app:supplementary-results/tab:deterministic-cost-ranges",
        "manuscript/generated/synthetic-supplementary.tex",
        "generated-results-table",
    ),
    "claim-table-stochastic-sensitivity": (
        "app:supplementary-results/tab:stochastic-sensitivity",
        "manuscript/generated/synthetic-supplementary.tex",
        "generated-results-table",
    ),
    "claim-table-stochastic-coverage-diagnostics": (
        "app:supplementary-results/tab:stochastic-coverage-diagnostics",
        "manuscript/generated/synthetic-supplementary.tex",
        "generated-results-table",
    ),
    "claim-table-synthetic-validation-inventory": (
        "app:supplementary-results/tab:synthetic-validation-inventory",
        "manuscript/generated/synthetic-supplementary.tex",
        "generated-results-table",
    ),
}
ASSET_SOURCE_AUTHORITIES = {
    "claim-table-stochastic-primary": {
        f"reports/experiments/runs/{STOCHASTIC_RUN_ID}/stochastic-aggregates.json"
    },
    "claim-table-stochastic-sensitivity": {
        f"reports/experiments/runs/{STOCHASTIC_RUN_ID}/stochastic-aggregates.json"
    },
}
REQUIRED_NONCLAIMS = {
    "nonclaim-universal-superiority",
    "nonclaim-frictional-safety",
    "nonclaim-empirical-causality",
}


class SyntheticEvaluationControlError(ValueError):
    """Raised when Chapter 7 or Appendix E drifts from reviewed evidence."""


def _authority_paths(
    root: Path,
    identifier: str,
    record: dict[str, object],
    errors: list[str],
) -> set[str]:
    authority = record.get("authority")
    if not isinstance(authority, list) or not authority:
        errors.append(f"{identifier}: no authority declared")
        return set()
    paths: set[str] = set()
    for entry in authority:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            errors.append(f"{identifier}: invalid authority entry")
            continue
        path = entry["path"]
        paths.add(path)
        validate_repository_file(root, identifier, path, errors)
    return paths


def _audit_assets(root: Path, errors: list[str]) -> dict[str, object]:
    try:
        with tempfile.TemporaryDirectory() as temporary_directory:
            replay_root = Path(temporary_directory) / "generated"
            receipt = generate_synthetic_evaluation_assets(root, replay_root)
            for asset_name in ASSET_NAMES:
                committed_path = root / "manuscript/generated" / asset_name
                replay_path = replay_root / asset_name
                if not committed_path.is_file():
                    errors.append(f"missing committed generated asset {asset_name}")
                    continue
                if committed_path.read_bytes() != replay_path.read_bytes():
                    errors.append(
                        f"{asset_name}: committed bytes do not match accepted-run regeneration"
                    )
            return receipt
    except (OSError, SyntheticEvaluationAssetError) as error:
        errors.append(f"generated-asset audit failed: {error}")
        return {}


def audit_deterministic_stochastic_evaluation(
    repository_root: Path,
) -> dict[str, object]:
    """Audit Chapter 7, Appendix E, asset regeneration, and evidence mappings."""

    root = repository_root.resolve()
    errors: list[str] = []
    thesis = read_text(root / "manuscript/source/thesis.tex", errors)
    claims = index_records(
        read_json_object(root / "manuscript/controls/claims.json", errors)
    )
    nonclaims = index_records(
        read_json_object(root / "manuscript/controls/non-claims.json", errors)
    )
    evidence_note = read_text(root / EVIDENCE_NOTE, errors)
    chapter = extract_latex_chapter(thesis, "Deterministic and Stochastic Evaluation")
    appendix = extract_latex_chapter(thesis, "Supplementary Tables and Figures")
    evidence_boundary = extract_latex_section(
        chapter, "Accepted Runs and Evidential Boundary"
    )
    deterministic = extract_latex_section(
        chapter, "Deterministic and Adversarial Paths"
    )
    stochastic = extract_latex_section(chapter, "Seeded Stochastic Families")
    mechanisms = extract_latex_section(
        chapter, "Safety Diagnostics and Terminal Attribution"
    )
    cost_scope = extract_latex_section(
        chapter, "Frictionless Validation, Net Costs, and Non-Inference"
    )

    if not chapter:
        errors.append("missing Chapter 7 deterministic and stochastic evaluation")
    if not appendix:
        errors.append("missing Appendix E supplementary results")
    for label, text in (("Chapter 7", chapter), ("Appendix E", appendix)):
        if "will be placed here" in text.casefold() or "structural placeholder" in text.casefold():
            errors.append(f"{label}: unresolved structural placeholder remains")

    require_terms(
        chapter,
        (
            r"\label{ch:synthetic-results}",
            "Deterministic signs, stochastic seed summaries, and exact theorems retain different inferential units",
            "No deterministic count is combined with a stochastic replication",
            "simulation does not replace the pathwise theorem",
        ),
        "Chapter 7 evidence boundary",
        errors,
    )
    require_terms(
        evidence_boundary,
        (
            r"\label{sec:synthetic-evidence}",
            DETERMINISTIC_RUN_ID,
            STOCHASTIC_RUN_ID,
            "21 attempted deterministic configurations",
            "18 generated paths and three typed pre-policy exclusions",
            "648 policy ledgers and 648 ordered comparison rows",
            "90 attempted and generated stochastic paths",
            "3,240 policy ledgers and 3,240 comparison rows",
            "1,080 aggregate cells",
            "three saved seeds",
            "12-, 36-, and 60-month horizons",
            "one inferential unit",
        ),
        "accepted synthetic run populations",
        errors,
    )
    require_terms(
        deterministic,
        (
            r"\label{sec:deterministic}",
            r"\input{../generated/deterministic-evaluation.tex}",
            r"W^c-W^T=H_T+P U_T",
            "500 dollars of additional cash",
            "five fewer units",
            r"4.712\%",
            r"5.260\%",
            r"1.520\%",
            r"29.873\%",
            r"2.901\%",
            "200.736 dollars less cash",
            "136.684 dollars",
            "finite-regression-not-proof",
            r"\ref{thm:two-purchase}",
            r"\ref{thm:three-purchase}",
            r"\ref{thm:terminal-inventory}",
            r"Appendix Table~\ref{tab:deterministic-coverage-ranges}",
            "not observed market frequencies",
        ),
        "deterministic result interpretation",
        errors,
    )
    require_terms(
        stochastic,
        (
            r"\label{sec:stochastic}",
            r"\input{../generated/stochastic-evaluation.tex}",
            "three paths per family",
            "minimum-to-maximum seed",
            r"linearly interpolated 5\% downside",
            "positive for mean reversion and jump diffusion",
            "negative for trend, stochastic volatility, and regime switching",
            "regime-switching signal-only median is negative",
            "does not estimate a population win rate",
            r"Appendix~\ref{sec:supp-stochastic}",
            "exploratory sensitivities remain separate",
        ),
        "stochastic result interpretation",
        errors,
    )
    require_terms(
        mechanisms,
        (
            r"\label{sec:synthetic-mechanisms}",
            r"\label{sec:safety-checks}",
            r"\ref{fig:stochastic-attribution}",
            r"\ref{tab:stochastic-mechanisms}",
            "30.0",
            r"31.7\%",
            "10.6",
            r"11.1\%",
            r"3.9\%",
            "1.5",
            r"1.9\%",
            "98.3",
            r"98.4\%",
            "1,015.595",
            "-1,143.872",
            "894.404",
            "-782.925",
            "all 90 generated stochastic paths",
            "finite implementation regression, not a second proof",
            "belongs to the unit guardrail",
            r"Appendix Table~\ref{tab:stochastic-coverage-diagnostics}",
        ),
        "synthetic mechanisms and safety scope",
        errors,
    )
    require_terms(
        cost_scope,
        (
            r"\label{sec:synthetic-cost-scope}",
            r"Appendix Table~\ref{tab:deterministic-cost-ranges}",
            "2,160 stochastic fee-adjusted ledgers",
            "outside-current-safety-theorem",
            "gross frictionless theorem",
            "net empirical performance",
            "No significance test is defined",
            "expected outperformance",
            "causal superiority",
            "historical relevance",
        ),
        "frictionless and net-cost scope",
        errors,
    )
    require_terms(
        appendix,
        (
            r"\label{app:supplementary-results}",
            r"\input{../generated/synthetic-supplementary.tex}",
            r"python3.12 -m reproducibility.synthetic_evaluation_assets",
            r"python3.12 -m unittest",
            r"reproducibility.checks.check_deterministic_stochastic_evaluation",
            "generated from the accepted bundles rather than transcribed",
        ),
        "Appendix E reproducibility contract",
        errors,
    )

    deterministic_asset = read_text(
        root / "manuscript/generated/deterministic-evaluation.tex", errors
    )
    stochastic_asset = read_text(
        root / "manuscript/generated/stochastic-evaluation.tex", errors
    )
    mechanism_asset = read_text(
        root / "manuscript/generated/stochastic-mechanisms.tex", errors
    )
    supplementary_asset = read_text(
        root / "manuscript/generated/synthetic-supplementary.tex", errors
    )
    require_terms(
        deterministic_asset,
        (
            "C is the corrected guarded policy",
            "N the neutral guarded selector",
            "D DCA",
            "each X--Y relative terminal-wealth gap uses Y as its denominator",
            "frozen identity corrected mean",
        ),
        "self-contained deterministic figure caption",
        errors,
    )
    require_terms(
        stochastic_asset,
        (
            r"Comparison & $N$ & Median & Seed range & 5\% downside & Worst",
            "C--D is corrected guarded versus DCA",
            "C--N is corrected guarded versus neutral guarded",
            "N--D is neutral guarded versus DCA",
            "Seed range is the minimum-to-maximum interval",
            "uses its named right-hand policy as denominator",
        ),
        "self-contained primary stochastic summary",
        errors,
    )
    require_terms(
        mechanism_asset,
        ("mean signed terminal-wealth difference in dollars",),
        "signed stochastic attribution caption",
        errors,
    )
    require_terms(
        supplementary_asset,
        (
            r"Comparison & $N$ & Median & Seed range & 5\% downside & Worst",
            "C--D is corrected guarded versus DCA",
            "C--N is corrected guarded versus neutral guarded",
            "N--D is neutral guarded versus DCA",
            "Seed range is the minimum-to-maximum interval",
            "uses its named right-hand policy as denominator",
            "frozen identity corrected mean and frictionless costs",
            "terminal cash divided by total deposits",
            "terminal asset value divided by terminal wealth",
            "C--D is the corrected guarded versus DCA median relative terminal-wealth gap",
        ),
        "self-contained stochastic coverage-diagnostics caption",
        errors,
    )

    for identifier, expected_location in SYNTHETIC_CLAIMS.items():
        record = claims.get(identifier)
        if record is None:
            errors.append(f"missing synthetic result claim {identifier}")
            continue
        if record.get("manuscript_location") != expected_location:
            errors.append(
                f"{identifier}: manuscript_location must be {expected_location!r}"
            )
        if record.get("mandatory") is not True:
            errors.append(f"{identifier}: claim must be mandatory")
        if record.get("review_state") not in RESOLVED_REVIEW_STATES:
            errors.append(f"{identifier}: claim must be independently reviewed")
        paths = _authority_paths(root, identifier, record, errors)
        if EVIDENCE_NOTE not in paths:
            errors.append(f"{identifier}: missing manuscript evidence note authority")
        manuscript_label = expected_location.rsplit("/", 1)[-1]
        if f"\\label{{{manuscript_label}}}" not in thesis:
            errors.append(f"{identifier}: manuscript label {manuscript_label} is absent")

    for identifier, (expected_location, asset_path, expected_class) in ASSET_CLAIMS.items():
        record = claims.get(identifier)
        if record is None:
            errors.append(f"missing generated asset claim {identifier}")
            continue
        if record.get("manuscript_location") != expected_location:
            errors.append(
                f"{identifier}: manuscript_location must be {expected_location!r}"
            )
        if record.get("claim_class") != expected_class:
            errors.append(f"{identifier}: claim_class must be {expected_class!r}")
        if record.get("entry_type") not in {"manuscript-table", "manuscript-figure"}:
            errors.append(f"{identifier}: generated asset must be realized")
        if record.get("mandatory") is not True:
            errors.append(f"{identifier}: asset claim must be mandatory")
        if record.get("review_state") not in RESOLVED_REVIEW_STATES:
            errors.append(f"{identifier}: asset claim must be independently reviewed")
        paths = _authority_paths(root, identifier, record, errors)
        for required_path in {
            asset_path,
            "reproducibility/synthetic_evaluation_assets.py",
            EVIDENCE_NOTE,
            *ASSET_SOURCE_AUTHORITIES.get(identifier, set()),
        }:
            if required_path not in paths:
                errors.append(f"{identifier}: missing authority {required_path}")
        manuscript_label = expected_location.rsplit("/", 1)[-1]
        asset_text = read_text(root / asset_path, errors)
        if f"\\label{{{manuscript_label}}}" not in asset_text:
            errors.append(f"{identifier}: generated asset label is absent")

    for identifier in REQUIRED_NONCLAIMS:
        record = nonclaims.get(identifier)
        if record is None:
            errors.append(f"missing synthetic non-claim {identifier}")
            continue
        affected = record.get("affected_locations")
        if not isinstance(affected, list) or "ch:synthetic-results" not in affected:
            errors.append(f"{identifier}: Chapter 7 must be an affected location")
        if record.get("review_state") not in RESOLVED_REVIEW_STATES:
            errors.append(f"{identifier}: non-claim must be resolved")

    for identifier in (*SYNTHETIC_CLAIMS, *ASSET_CLAIMS):
        if f"`{identifier}`" not in evidence_note:
            errors.append(f"{EVIDENCE_NOTE}: missing map entry for {identifier}")
    require_terms(
        evidence_note,
        (
            "## Evidence reconciliation",
            "## Claim and scope audit",
            "## Statistical-language audit",
            "## Visual review",
            "## Independent domain review",
            "Review status: **passed**",
            DETERMINISTIC_RUN_ID,
            STOCHASTIC_RUN_ID,
            "No publication blocker remains for ticket 10",
        ),
        "synthetic evaluation manuscript evidence note",
        errors,
    )

    asset_receipt = _audit_assets(root, errors)
    if errors:
        raise SyntheticEvaluationControlError("\n".join(errors))

    return {
        "status": "passed",
        "claim_count": len(SYNTHETIC_CLAIMS),
        "asset_claim_count": len(ASSET_CLAIMS),
        "nonclaim_count": len(REQUIRED_NONCLAIMS),
        "generated_asset_count": len(ASSET_NAMES),
        "deterministic_run_id": asset_receipt["deterministic_run_id"],
        "stochastic_run_id": asset_receipt["stochastic_run_id"],
        "deterministic_generated_path_count": asset_receipt[
            "deterministic_generated_path_count"
        ],
        "stochastic_generated_path_count": asset_receipt[
            "stochastic_generated_path_count"
        ],
        "stochastic_aggregate_cell_count": asset_receipt[
            "stochastic_aggregate_cell_count"
        ],
        "independent_review_status": "passed",
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
        receipt = audit_deterministic_stochastic_evaluation(args.repository_root)
    except SyntheticEvaluationControlError as error:
        print(f"SYNTHETIC EVALUATION AUDIT FAILED\n{error}")
        return 1
    print(
        "SYNTHETIC EVALUATION AUDIT PASSED: "
        f"{receipt['claim_count']} claims, "
        f"{receipt['asset_claim_count']} generated tables/figures"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
