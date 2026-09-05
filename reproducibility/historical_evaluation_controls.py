#!/usr/bin/env python3
"""Fail-closed controls for the thesis historical and robustness result slice."""

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
from reproducibility.historical_evaluation_assets import (  # noqa: E402
    ASSET_NAMES,
    PRIMARY_RUN_ID,
    ROBUSTNESS_RUN_ID,
    HistoricalEvaluationAssetError,
    generate_historical_evaluation_assets,
)


RESOLVED_REVIEW_STATES = {"accepted", "reviewed"}
EVIDENCE_NOTE = "research/notes/historical-robustness-evaluation-manuscript-audit.md"
FINAL_REVIEW_MARKER = (
    "Review status: **passed** independent domain, statistical-language, "
    "reproducibility, and rendered-visual review on 2026-09-05."
)
ASSET_GENERATOR = "reproducibility/historical_evaluation_assets.py"
PRIMARY_ROOT = f"reports/experiments/runs/{PRIMARY_RUN_ID}"
ROBUSTNESS_ROOT = f"reports/experiments/runs/{ROBUSTNESS_RUN_ID}"
HISTORICAL_CLAIMS = {
    "claim-empirical-historical-populations": (
        "ch:historical-results/sec:historical-evidence"
    ),
    "claim-empirical-historical-complete-system": (
        "ch:historical-results/sec:primary-complete-system"
    ),
    "claim-empirical-historical-signal": (
        "ch:historical-results/sec:primary-signal"
    ),
    "claim-empirical-historical-architecture-mechanisms": (
        "ch:historical-results/sec:historical-mechanisms"
    ),
    "claim-empirical-historical-safety-regressions": (
        "ch:historical-results/sec:historical-mechanisms"
    ),
    "claim-empirical-robustness": (
        "ch:historical-results/sec:registered-robustness"
    ),
    "claim-empirical-cost-scope": (
        "ch:historical-results/sec:cost-robustness"
    ),
}
ASSET_CLAIMS = {
    "claim-table-historical-primary": (
        "ch:historical-results/tab:historical-primary",
        "manuscript/generated/historical-primary.tex",
        "generated-confirmatory-table",
    ),
    "claim-figure-historical-primary-effects": (
        "ch:historical-results/fig:historical-primary-effects",
        "manuscript/generated/historical-primary.tex",
        "generated-results-figure",
    ),
    "claim-table-historical-comparison-tiers": (
        "ch:historical-results/tab:historical-comparison-tiers",
        "manuscript/generated/historical-mechanisms.tex",
        "generated-results-table",
    ),
    "claim-table-historical-policy-mechanisms": (
        "ch:historical-results/tab:historical-policy-mechanisms",
        "manuscript/generated/historical-mechanisms.tex",
        "generated-results-table",
    ),
    "claim-table-historical-risk-attribution": (
        "ch:historical-results/tab:historical-risk-attribution",
        "manuscript/generated/historical-mechanisms.tex",
        "generated-results-table",
    ),
    "claim-table-registered-robustness": (
        "ch:historical-results/tab:registered-robustness",
        "manuscript/generated/historical-robustness.tex",
        "generated-descriptive-table",
    ),
    "claim-table-historical-cost-robustness": (
        "ch:historical-results/tab:historical-cost-robustness",
        "manuscript/generated/historical-robustness.tex",
        "generated-descriptive-table",
    ),
    "claim-table-historical-h1-cells": (
        "app:supplementary-results/tab:historical-h1-cells",
        "manuscript/generated/historical-supplementary.tex",
        "generated-confirmatory-table",
    ),
    "claim-table-historical-h2-cells": (
        "app:supplementary-results/tab:historical-h2-cells",
        "manuscript/generated/historical-supplementary.tex",
        "generated-confirmatory-table",
    ),
    "claim-table-historical-architecture-cells": (
        "app:supplementary-results/tab:historical-architecture-cells",
        "manuscript/generated/historical-supplementary.tex",
        "generated-descriptive-table",
    ),
    "claim-table-historical-monthly-robustness-ranges": (
        "app:supplementary-results/tab:historical-monthly-robustness-ranges",
        "manuscript/generated/historical-supplementary.tex",
        "generated-descriptive-table",
    ),
    "claim-table-historical-quarterly-robustness-ranges": (
        "app:supplementary-results/tab:historical-quarterly-robustness-ranges",
        "manuscript/generated/historical-supplementary.tex",
        "generated-descriptive-table",
    ),
    "claim-table-historical-evidence-inventory": (
        "app:supplementary-results/tab:historical-evidence-inventory",
        "manuscript/generated/historical-supplementary.tex",
        "generated-validation-table",
    ),
}
ASSET_SOURCE_AUTHORITIES = {
    "claim-table-historical-primary": {
        f"{PRIMARY_ROOT}/historical-aggregates.json",
        f"{PRIMARY_ROOT}/uncertainty.json",
    },
    "claim-figure-historical-primary-effects": {
        f"{PRIMARY_ROOT}/historical-aggregates.json"
    },
    "claim-table-registered-robustness": {
        f"{ROBUSTNESS_ROOT}/robustness-aggregates.json"
    },
    "claim-table-historical-cost-robustness": {
        f"{PRIMARY_ROOT}/historical-aggregates.json",
        f"{ROBUSTNESS_ROOT}/robustness-aggregates.json",
    },
    "claim-table-historical-h1-cells": {
        f"{PRIMARY_ROOT}/uncertainty.json"
    },
    "claim-table-historical-h2-cells": {
        f"{PRIMARY_ROOT}/uncertainty.json"
    },
    "claim-table-historical-monthly-robustness-ranges": {
        f"{ROBUSTNESS_ROOT}/robustness-aggregates.json"
    },
    "claim-table-historical-quarterly-robustness-ranges": {
        f"{ROBUSTNESS_ROOT}/robustness-aggregates.json"
    },
}
REQUIRED_NONCLAIMS = {
    "nonclaim-universal-superiority",
    "nonclaim-confirmed-signal-value",
    "nonclaim-frictional-safety",
    "nonclaim-empirical-causality",
}


class HistoricalEvaluationControlError(ValueError):
    """Raised when Chapter 8 or Appendix E drifts from reviewed evidence."""


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
            receipt = generate_historical_evaluation_assets(root, replay_root)
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
    except (OSError, HistoricalEvaluationAssetError) as error:
        errors.append(f"generated-asset audit failed: {error}")
        return {}


def audit_historical_robustness_evaluation(
    repository_root: Path,
) -> dict[str, object]:
    """Audit Chapter 8, Appendix E, regeneration, and evidence mappings."""

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
    chapter = extract_latex_chapter(thesis, "Historical Evaluation and Robustness")
    appendix = extract_latex_chapter(thesis, "Supplementary Tables and Figures")
    evidence_boundary = extract_latex_section(
        chapter, "Accepted Runs, Populations, and Boundaries"
    )
    primary = extract_latex_section(chapter, "Primary Complete-System Finding")
    signal = extract_latex_section(chapter, "Signal-Only H2 Finding")
    mechanisms = extract_latex_section(
        chapter, "Architecture, Safety, and Terminal Mechanisms"
    )
    robustness = extract_latex_section(chapter, "Separately Registered Robustness")
    cost_scope = extract_latex_section(chapter, "Costs, Inference, and Data Limits")

    if not chapter:
        errors.append("missing Chapter 8 historical evaluation and robustness")
    if not appendix:
        errors.append("missing Appendix E supplementary results")
    for label, source in (("Chapter 8", chapter), ("Appendix E", appendix)):
        if (
            "will be placed here" in source.casefold()
            or "structural placeholder" in source.casefold()
        ):
            errors.append(f"{label}: unresolved structural placeholder remains")

    require_terms(
        chapter,
        (
            r"\label{ch:historical-results}",
            "The result is substantively negative and is retained as such",
            "the second is not an equivalence result",
            "universal, causal, optimal, or expected performance claims",
        ),
        "Chapter 8 evidential boundary",
        errors,
    )
    require_terms(
        evidence_boundary,
        (
            r"\label{sec:historical-evidence}",
            PRIMARY_RUN_ID,
            ROBUSTNESS_RUN_ID,
            "8{,}287",
            "4{,}018",
            "1,365 attempted episodes",
            "zero exclusions, failures, protocol deviations, or violations",
            "49,140 ledgers",
            "216 aggregate cells",
            "1,793 were included",
            "108,378 ledgers and comparison rows",
            "792 robustness cells and 18 compatibility cells",
            "neither redistributes them nor validates the financial interpretation",
        ),
        "accepted historical populations and source boundary",
        errors,
    )
    require_terms(
        primary,
        (
            r"\label{sec:primary-complete-system}",
            r"\lambda\in\{0.5,0.75,0.9\}",
            "All 18 medians were negative",
            r"$-4.593\%$ to $-0.335\%$",
            r"All 18 cellwise 95\% circular-block bootstrap percentile intervals lay below zero",
            "Nine cells rejected",
            "complete registered 36-cell H1/H2 family",
            r"\input{../generated/historical-primary.tex}",
            "eighteen negative cells are not eighteen independent markets",
            "not a proof of universal or causal inferiority",
        ),
        "primary complete-system finding",
        errors,
    )
    require_terms(
        signal,
        (
            r"\label{sec:primary-signal}",
            "holding the guardrail architecture fixed",
            "Seventeen of 18 medians were negative and one was positive",
            r"$-0.545\%$ to $+0.052\%$",
            "Seven cellwise percentile intervals lay wholly below zero",
            "no H2 cell was Holm-significant",
            "did not confirm incremental historical value",
            "did not establish that the two selectors are equivalent",
            "complete-system rejections do not become signal-only rejections",
        ),
        "signal-only H2 finding",
        errors,
    )
    require_terms(
        mechanisms,
        (
            r"\label{sec:historical-mechanisms}",
            r"\input{../generated/historical-mechanisms.tex}",
            "18 non-unit primary frictionless medians were all negative",
            r"$-4.365\%$ to $-0.340\%$",
            "does not causally attribute H1 to the guardrail",
            "All 54 corresponding primary aggregate rows were exact ties",
            "no observed corrected-guarded-versus-DCA or neutral-guarded-versus-DCA episode gap crossed",
            "not a second proof and not DCA dominance",
            r"$2.126\%$ to $11.482\%$",
            r"$91.698\%$ to $98.909\%$",
            r"$3.990\%$ to $100\%$",
            "one positive purchase per scheduled deposit",
            "terminal cash contribution was positive",
            "evaluation-price-valued unit contribution was negative",
            "not a causal explanation",
        ),
        "architecture, safety, and mechanism findings",
        errors,
    )
    require_terms(
        robustness,
        (
            r"\label{sec:registered-robustness}",
            "does not amend the primary run",
            "All 30 frictionless corrected-versus-DCA medians were negative",
            r"$-4.8134\%$ to $-0.0335\%$",
            "All 30 signal-only medians were also negative",
            "2, 8, and 40 deposits",
            "All 48 non-unit frictionless corrected-versus-DCA medians were negative",
            "40 negative and eight positive cells",
            "only four overlapping starts",
            r"\texttt{not-run-robustness}",
            "Raw terminal wealth is not compared across monthly and quarterly cadences",
            "Four declared alternate corrected-mean configurations remain unexecuted",
            r"\input{../generated/historical-robustness.tex}",
        ),
        "separately registered robustness",
        errors,
    )
    require_terms(
        cost_scope,
        (
            r"\label{sec:cost-robustness}",
            "All 36 medians were negative",
            "156 non-unit cost-adjusted complete-system cells",
            r"\path{outside-current-safety-theorem}",
            "not a confirmatory cost test",
            "10,000 circular moving-block replicates per cell",
            "one 36-cell Holm family",
            "Robustness has no uncertainty procedure",
            "No post-hoc regime label",
            "restricted observations are not independently redistributable",
        ),
        "cost, inference, and data limits",
        errors,
    )
    require_terms(
        appendix,
        (
            r"\label{app:supplementary-results}",
            r"\label{sec:supp-historical}",
            r"\input{../generated/historical-supplementary.tex}",
            r"\label{sec:supp-historical-regeneration}",
            r"python3.12 -m reproducibility.historical_evaluation_assets",
            r"reproducibility.checks.check_historical_robustness_manuscript",
            "contain no restricted source observation or row-level outcome",
            "remain unchanged",
        ),
        "Appendix E historical reproducibility contract",
        errors,
    )

    primary_asset = read_text(
        root / "manuscript/generated/historical-primary.tex", errors
    )
    mechanism_asset = read_text(
        root / "manuscript/generated/historical-mechanisms.tex", errors
    )
    robustness_asset = read_text(
        root / "manuscript/generated/historical-robustness.tex", errors
    )
    supplementary_asset = read_text(
        root / "manuscript/generated/historical-supplementary.tex", errors
    )
    require_terms(
        primary_asset,
        (
            "H1 is corrected guarded versus DCA",
            "H2 is corrected guarded versus the neutral guarded selector",
            "each relative gap uses its named right-hand policy as denominator",
            "one sealed 36-test H1/H2 family",
            "point estimates rather than confidence intervals",
            "zero line",
        ),
        "self-contained primary historical assets",
        errors,
    )
    require_terms(
        mechanism_asset,
        (
            "Complete-system significance is never transferred",
            "terminal policy cash divided by contributed deposits",
            "terminal asset value divided by that policy's cash-inclusive terminal wealth",
            "mean share of purchase dates",
            "18 positive / 18 negative",
            "The signs describe ledger-conditioned accounting, not a causal explanation",
        ),
        "self-contained historical mechanism tables",
        errors,
    )
    require_terms(
        robustness_asset,
        (
            "Separately registered post-confirmatory robustness results under frictionless accounting",
            "raw wealth is not compared across monthly and quarterly schedules because their deposit counts differ",
            "outside the current frictionless safety theorem",
            "no registered interval",
            "no multiplicity adjustment",
        ),
        "self-contained robustness and cost tables",
        errors,
    )
    require_terms(
        supplementary_asset,
        (
            "ordered overlapping starts within one cell",
            "Holm values are adjusted once over the complete 36-cell H1/H2 family",
            "An interval excluding zero is not substituted",
            "Non-rejection does not establish equivalence",
            "do not causally decompose H1",
            "do not enter H1/H2 or permit raw-wealth comparison with another cadence",
            "restricted source observations are not redistributed",
        ),
        "self-contained historical supplementary tables",
        errors,
    )

    for identifier, expected_location in HISTORICAL_CLAIMS.items():
        record = claims.get(identifier)
        if record is None:
            errors.append(f"missing historical result claim {identifier}")
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
            ASSET_GENERATOR,
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
            errors.append(f"missing historical non-claim {identifier}")
            continue
        affected = record.get("affected_locations")
        if not isinstance(affected, list) or "ch:historical-results" not in affected:
            errors.append(f"{identifier}: Chapter 8 must be an affected location")
        if record.get("review_state") not in RESOLVED_REVIEW_STATES:
            errors.append(f"{identifier}: non-claim must be resolved")

    for identifier in (*HISTORICAL_CLAIMS, *ASSET_CLAIMS):
        if f"`{identifier}`" not in evidence_note:
            errors.append(f"{EVIDENCE_NOTE}: missing map entry for {identifier}")
    require_terms(
        evidence_note,
        (
            "## Evidence reconciliation",
            "## Claim and scope audit",
            "## Statistical-language audit",
            "## Reproducibility review",
            "## Visual review",
            "## Independent domain review",
            FINAL_REVIEW_MARKER,
            "Status: **passed** by independent statistical-language review",
            "Status: **passed** by independent reproducibility review",
            "Status: **passed** by independent rendered-visual review",
            "Status: **passed** by independent domain review",
            PRIMARY_RUN_ID,
            ROBUSTNESS_RUN_ID,
        ),
        "historical evaluation manuscript evidence note",
        errors,
    )

    asset_receipt = _audit_assets(root, errors)
    if errors:
        raise HistoricalEvaluationControlError("\n".join(errors))

    return {
        "status": "passed",
        "claim_count": len(HISTORICAL_CLAIMS),
        "asset_claim_count": len(ASSET_CLAIMS),
        "nonclaim_count": len(REQUIRED_NONCLAIMS),
        "generated_asset_count": len(ASSET_NAMES),
        "primary_run_id": asset_receipt["primary_run_id"],
        "robustness_run_id": asset_receipt["robustness_run_id"],
        "primary_episode_count": asset_receipt["primary_episode_count"],
        "primary_confirmatory_cell_count": asset_receipt[
            "primary_confirmatory_cell_count"
        ],
        "robustness_episode_count": asset_receipt["robustness_episode_count"],
        "robustness_cell_count": asset_receipt["robustness_cell_count"],
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
        receipt = audit_historical_robustness_evaluation(args.repository_root)
    except HistoricalEvaluationControlError as error:
        print(f"HISTORICAL EVALUATION AUDIT FAILED\n{error}")
        return 1
    print(
        "HISTORICAL EVALUATION AUDIT PASSED: "
        f"{receipt['claim_count']} claims, "
        f"{receipt['asset_claim_count']} generated tables/figures"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
