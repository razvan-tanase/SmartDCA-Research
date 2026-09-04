#!/usr/bin/env python3
"""Fail-closed controls for the thesis empirical-methodology slice."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manuscript.citation_controls import (  # noqa: E402
    extract_bibtex_keys,
    extract_latex_citation_keys,
)
from reproducibility.control_support import (  # noqa: E402
    extract_latex_chapter,
    index_records,
    normalize_whitespace,
    read_json_object,
    read_text,
    require_terms,
    validate_repository_file,
)


RESOLVED_REVIEW_STATES = {"accepted", "reviewed"}
METHODOLOGY_NOTE = (
    "research/notes/empirical-methodology-reproducibility-manuscript-audit.md"
)
METHODOLOGY_CLAIMS = {
    "claim-method-policy-comparisons": (
        "ch:methodology/sec:method-policy-comparisons"
    ),
    "claim-method-evidence-layers": (
        "ch:methodology/sec:method-evidence-layers"
    ),
    "claim-method-historical-source": (
        "ch:methodology/sec:method-historical-source"
    ),
    "claim-method-frozen-grid": "ch:methodology/sec:method-frozen-grid",
    "claim-method-estimands-inference": "ch:methodology/sec:method-inference",
    "claim-method-analysis-scope": (
        "ch:methodology/sec:method-analysis-tiers"
    ),
    "claim-method-reproducibility": (
        "ch:methodology/sec:method-reproducibility"
    ),
}
METHODOLOGY_TABLE_CLAIMS = {
    "claim-table-protocol-grid": (
        "app:protocols/tab:protocol-grid",
        (
            "The protocol-grid table defines the frozen primary execution axes "
            "and identifies the registered coverage, corrected-mean, schedule, "
            "horizon, cost, and comparison extensions outside the confirmatory "
            "family."
        ),
    ),
    "claim-table-reproducibility": (
        "app:reproducibility/tab:artifact-inventory",
        (
            "The reproducibility inventory distinguishes four versioned artifact "
            "layers—accepted protocols, inputs or receipts, run bundles, and "
            "narrative reports—by repository authority and by their different "
            "identity, overwrite, and revision rules."
        ),
    ),
}
METHODOLOGY_NOTATION = {
    "notation-relative-gap": "ch:methodology/sec:estimands",
    "notation-historical-bootstrap": "ch:methodology/sec:method-inference",
    "notation-empirical-cost-execution": (
        "ch:methodology/sec:method-policy-comparisons"
    ),
}
METHODOLOGY_NONCLAIMS = {
    "nonclaim-frictional-safety",
    "nonclaim-empirical-causality",
}
OUTCOME_RELEVANT_PROTOCOL_FIELDS = {
    "episode_design",
    "coverage",
    "corrected_mean",
    "cost_scenarios",
    "hypotheses",
    "estimands",
    "multiplicity",
    "uncertainty",
    "analysis_tiers",
    "exclusions",
    "robustness_design",
    "canonical_run",
    "runner_contract",
}
EXPECTED_PROTOCOL_HASHES = {
    "experiments/protocols/safety-adaptivity-v1.json": (
        "a508b4f064dcb3930f137e7754180ca0ec43749680278acb5b42fe2345c8d6e4"
    ),
    "experiments/protocols/safety-adaptivity-yahoo-v2.json": (
        "a5194248f7b55073e60b357c01c4993c1e50ed20c9c9672daf4780db1127f2be"
    ),
}
EXPECTED_RECEIPT_HASHES = {
    "experiments/inputs/historical-yahoo-receipts-v2.json": (
        "346676eb699d4e64cee7f687a04f207d6ab4daff92abae780719368d259f97f4"
    ),
    "experiments/inputs/historical-yahoo-preparation-manifest-v5.json": (
        "f86691e21acb8f1f70d9d9124c020f126014aae5aa631c90a0f82165814e5894"
    ),
    (
        "reports/experiments/runs/"
        "smartdca-empirical-package-review-v1-"
        "6cb6c1cd94b901be90ebd553a022c922e53984afafeb22948747be084b37c14f/"
        "review-receipt.json"
    ): "9ad1daa4c43e81232fdfbabb295c37a67b87422f11b8de7abf8c2c9b38df1e9b",
}
EXPECTED_RUN_IDS = {
    "smartdca-run-v1-b029028a9a8e5104359c4999b26e42f1dc81207eb4eb29b1dfba9fcae83473e0",
    "smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db",
    "smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25",
    "smartdca-historical-validation-v1-d376ff1411774e40978ea1aa4c0dcf4e18603d93fbfcb017cbfa18538ea7b499",
    "smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221",
    "smartdca-historical-robustness-v1-0991d999e1a8070a2a6eb8046b08a91d0e42341995610a602372c52dfab14184",
    "smartdca-synthesis-v1-394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26",
}
REQUIRED_CITATIONS = {
    "farrell2013rfc6920",
    "hernanrobins2020",
    "holm1979",
    "kunsch1989blockbootstrap",
    "moreaumissier2013prov",
    "nasem2019reproducibility",
    "peng2011reproducible",
    "politisromano1992circular",
    "richardsonsmith1991overlap",
    "wilkinson2016fair",
    "yahoo2026adjustedclose",
    "yahoo2026providers",
    "yahoo2026terms",
    "yfinance2026history",
}


class MethodologyControlError(ValueError):
    """Raised when the empirical-methodology manuscript drifts from authority."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_authority_paths(
    root: Path,
    identifier: str,
    record: dict[str, object],
    errors: list[str],
) -> None:
    authority = record.get("authority")
    if not isinstance(authority, list) or not authority:
        errors.append(f"{identifier}: methodology claim has no authority")
        return
    paths: set[str] = set()
    for entry in authority:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            errors.append(f"{identifier}: invalid authority entry")
            continue
        path = entry["path"]
        paths.add(path)
        validate_repository_file(root, identifier, path, errors)
    if METHODOLOGY_NOTE not in paths:
        errors.append(
            f"{identifier}: missing manuscript-slice authority {METHODOLOGY_NOTE}"
        )


def _require_exact(
    actual: object,
    expected: object,
    label: str,
    errors: list[str],
) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, found {actual!r}")


def audit_empirical_methodology_reproducibility(
    repository_root: Path,
) -> dict[str, object]:
    """Audit Chapter 6, Appendices C--D, frozen design, and traceability."""

    root = repository_root.resolve()
    errors: list[str] = []
    thesis = read_text(root / "manuscript/source/thesis.tex", errors)
    bibliography = read_text(
        root / "manuscript/bibliography/references.bib", errors
    )
    claims = index_records(
        read_json_object(root / "manuscript/controls/claims.json", errors)
    )
    notation = index_records(
        read_json_object(root / "manuscript/controls/notation.json", errors)
    )
    nonclaims = index_records(
        read_json_object(root / "manuscript/controls/non-claims.json", errors)
    )
    evidence_note = read_text(root / METHODOLOGY_NOTE, errors)
    protocol_v1 = read_json_object(
        root / "experiments/protocols/safety-adaptivity-v1.json", errors
    )
    protocol_v2 = read_json_object(
        root / "experiments/protocols/safety-adaptivity-yahoo-v2.json", errors
    )
    robustness_plan = read_json_object(
        root / "experiments/inputs/historical-yahoo-registered-robustness-v1.json",
        errors,
    )
    source_receipt = read_json_object(
        root / "experiments/inputs/historical-yahoo-receipts-v2.json", errors
    )
    preparation_manifest = read_json_object(
        root / "experiments/inputs/historical-yahoo-preparation-manifest-v5.json",
        errors,
    )
    review_root = (
        root
        / "reports/experiments/runs/"
        "smartdca-empirical-package-review-v1-"
        "6cb6c1cd94b901be90ebd553a022c922e53984afafeb22948747be084b37c14f"
    )
    review_receipt = read_json_object(review_root / "review-receipt.json", errors)
    review_manifest = read_json_object(review_root / "manifest.json", errors)

    chapter = extract_latex_chapter(
        thesis, "Empirical Methodology and Reproducibility"
    )
    protocol_appendix = extract_latex_chapter(
        thesis, "Empirical Protocols and Statistical Controls"
    )
    reproducibility_appendix = extract_latex_chapter(
        thesis, "Reproducibility and Artifact Provenance"
    )
    if not chapter:
        errors.append("missing Chapter 6 empirical methodology")
    if not protocol_appendix:
        errors.append("missing Appendix C empirical protocols")
    if not reproducibility_appendix:
        errors.append("missing Appendix D reproducibility provenance")
    for label, text in (
        ("Chapter 6", chapter),
        ("Appendix C", protocol_appendix),
        ("Appendix D", reproducibility_appendix),
    ):
        if "will be placed here" in text.casefold():
            errors.append(f"{label}: unresolved structural placeholder remains")

    require_terms(
        chapter,
        (
            r"\label{sec:method-policy-comparisons}",
            "DCA, denoted by $D$",
            "neutral guarded policy, denoted by $0$",
            "corrected guarded policy, denoted by $c$",
            "differ only through the discretionary selector",
            "fee-inclusive target budget",
            r"$\widetilde b_t^D=B_t^D$",
            (
                r"runner maps selected budget $\widetilde b_t^S$ to actual "
                r"asset notional $b_t^S$ and fee $F_t^S$"
            ),
            r"\label{eq:method-cost-execution}",
            r"\widetilde b_t^S\leq F_0",
            "60-digit",
            "rounds the asset-notional division downward",
            "With fees, actual notional can fall below",
            "DCA unit history produced by the same cost route",
            "validates equality of actual purchase, fee, cash, and units",
            "not equality of that diagnostic field",
            "identical realized price path",
            "deposit schedule",
            "evaluation price",
            "safety factor",
            "cost scenario",
            "complete system",
            "signal only",
            "architecture only",
            "different denominators",
            "not arithmetically additive",
            "causal decomposition",
        ),
        "three-policy comparison contract",
        errors,
    )
    require_terms(
        chapter,
        (
            r"\label{sec:method-evidence-layers}",
            "Deterministic paths",
            "Seeded stochastic families",
            "Primary rolling history",
            "Registered robustness",
            "Their signs and win counts are not probabilities",
            "Three paths per configuration",
            "cannot revise H1 or H2",
            "without pooling their rows into a new test",
            "supporting infrastructure rather than fifth performance layers",
        ),
        "four-layer inferential boundary",
        errors,
    )
    require_terms(
        chapter,
        (
            r"\label{sec:method-historical-source}",
            "historical source service is Yahoo Finance",
            r"\texttt{yfinance==1.7.0}",
            "acquisition client, not the provider",
            "returned adjusted close",
            "dividends are therefore not added again",
            "BTC-USD series uses the unadjusted returned USD",
            "venue and aggregation semantics are not independently established",
            "America/New\\_York",
            "first eligible observation on or after",
            "last eligible observation on or before",
            "There is no interpolation or price carry",
            "one typed exclusion reason",
            r"\texttt{policy\_execution=not-run}",
            "remain access-controlled outside Git",
            "does not change that boundary",
        ),
        "historical source or retention rule",
        errors,
    )
    require_terms(
        chapter,
        (
            r"\label{sec:method-frozen-grid}",
            r"\lambda\in\{1,0.9,0.75,0.5\}",
            "identity-a0-b0",
            r"$\alpha=0$",
            r"$\beta=0$",
            "equal weights",
            "frictionless",
            "proportional 10 bps",
            "fixed USD 1",
            r"\{0.99,0.95,0.8,0.6,0.25\}",
            "quarterly first-eligible schedules",
            "6-, 24-, and 120-month horizons",
            "Four alternate corrected-mean configurations were declared but remain unexecuted",
            "run-identity collisions",
            "theorem-scope validations",
        ),
        "frozen grid or validation rule",
        errors,
    )
    require_terms(
        chapter,
        (
            r"\label{sec:estimands}",
            r"g_s^{S,T}=\frac{W_s^S-W_s^T}{W_s^T}",
            r"\texttt{comparator\_terminal\_wealth\_nonpositive}",
            "primary cell estimand is the median",
            "5th, 10th, and 25th percentiles",
            "worst relative shortfall",
            "terminal cash drag is terminal cash divided by total deposits",
            "Terminal asset exposure is terminal asset value divided by terminal wealth",
            "Guardrail activation frequency",
            "positive purchase count and total fees",
            r"W_s^S-W_s^T",
            "exact ledger accounting",
        ),
        "estimand or mechanism definition",
        errors,
    )
    require_terms(
        chapter,
        (
            r"\label{sec:method-inference}",
            "H1 tests the complete-system median gap",
            "H2 tests the signal-only median gap",
            "Both alternatives are two-sided",
            r"$2\times3\times3\times2=36$ hypotheses",
            "not a 37th test",
            "sampling unit is one ordered nominal monthly episode start",
            "consecutive circular block of starts is the resampling unit",
            r"$B=10{,}000$ replicates",
            "base seed is $20260825$",
            "first 16 hexadecimal digits of SHA-256",
            "two-sided 95\\% percentile interval",
            r"\frac{1+\sum_{b=1}^{B}",
            "H1 before H2",
            "registered family-wise alpha is $0.05$",
            "strictly below $0.05$",
            "validity remains conditional on the adequacy of the ordered",
            "stationary/dependence approximation",
            "cellwise interval, not a simultaneous or Holm-adjusted one",
            "does not make overlapping episodes independent",
            "create causal identification",
        ),
        "registered statistical procedure",
        errors,
    )
    finite_run_marker = (
        r"\mathbf{1}\{|\widehat{\theta}_b-\widehat{\theta}| "
        r"\geq |\widehat{\theta}|\}}{B+1}."
    )
    if normalize_whitespace(finite_run_marker) not in normalize_whitespace(chapter):
        errors.append(
            "finite-run p-value must retain the plus-one numerator and denominator"
        )
    require_terms(
        chapter,
        (
            r"\label{sec:method-analysis-tiers}",
            "Confirmatory language is reserved for H1 and H2",
            "Prespecified secondary analyses",
            "Registered robustness",
            "Exploratory interpretation",
            "Only a frictionless ledger is tagged",
            "outside-current-safety-theorem",
            "neither inherit that guarantee nor invalidate it",
            "no universal, expected, causal, or market-wide policy ordering",
            r"\label{sec:method-reproducibility}",
            "accepted evaluation runtime is CPython 3.12",
            "Authorized acquisition is a separate CPython 3.12 environment",
            "not a test dependency",
            "four versioned layers",
            "revisable narrative reports",
            "Narrative reports may be revised",
            "collision targets, not update targets",
            "independent reconciliation on the same retained observations",
            "not independent-data replication",
            "not submission readiness",
        ),
        "analysis-tier, theorem-scope, or reproduction boundary",
        errors,
    )
    fee_scope_marker = (
        "the 10-basis-point and one-dollar routes are tagged\n"
        r"\path{outside-current-safety-theorem}"
    )
    if fee_scope_marker not in chapter:
        errors.append(
            "fee routes must remain outside the current frictionless safety theorem"
        )

    require_terms(
        protocol_appendix,
        (
            r"\label{sec:appendix-protocol-identities}",
            EXPECTED_PROTOCOL_HASHES[
                "experiments/protocols/safety-adaptivity-v1.json"
            ],
            EXPECTED_PROTOCOL_HASHES[
                "experiments/protocols/safety-adaptivity-yahoo-v2.json"
            ],
            r"\label{tab:protocol-grid}",
            r"\label{sec:appendix-episode-mapping}",
            "exhaustive protocol exclusion vocabulary",
            r"\label{sec:appendix-hypotheses-estimands}",
            r"\label{sec:appendix-bootstrap-holm}",
            "plus-one numerator and denominator",
            "exact Holm tie order",
            "registered family-wise alpha is $0.05$",
            "ordered stationary/dependence approximation",
            r"\label{sec:appendix-tier-scope}",
            "no confirmatory bootstrap or multiplicity test",
            "outside-current-safety-theorem",
        ),
        "Appendix C protocol control",
        errors,
    )
    require_terms(
        reproducibility_appendix,
        (
            r"\label{sec:appendix-software-environments}",
            "CPython 3.12.14 on macOS arm64",
            "debian:bookworm-20260824-slim",
            r"distribution \texttt{python3}",
            "does not regenerate them",
            r"\label{tab:artifact-inventory}",
            (
                "Four versioned artifact layers and their distinct identity and "
                "retention rules"
            ),
            "Revisable; keeps artifact links and publication state accurate",
            "yahoo-finance-historical-8b6758e9",
            "smartdca-historical-input-v1-4da2c9",
            r"\label{sec:appendix-run-identities}",
            "accepts exactly these seven publication run identities",
            "smartdca-empirical-package-review-v1-6cb6c1cd",
            "9ad1daa4c43e81232fdfbabb295c37a67b87422f11b8de7abf8c2c9b38df1e9b",
            r"\label{sec:appendix-public-reproduction}",
            "reproducibility.empirical",
            "canonical-synthetic-v1.json",
            "check_empirical_protocol_canonical_run",
            "reproducibility.deterministic_study",
            "reproducibility.stochastic_study",
            "reproducibility.safety_adaptivity_synthesis",
            "reproducibility.empirical_package_review",
            r"\label{sec:appendix-private-reconciliation}",
            "receipt-bound directories",
            r"\label{sec:appendix-clean-manuscript}",
            "check_empirical_methodology_reproducibility",
            "manuscript/build-clean.sh",
        ),
        "Appendix D reproducibility control",
        errors,
    )
    for run_id in EXPECTED_RUN_IDS:
        if run_id not in reproducibility_appendix:
            errors.append(f"Appendix D: missing accepted run identity {run_id}")

    require_terms(
        evidence_note,
        (
            "## Scope and governing authorities",
            "## Frozen-design reconstruction",
            "## Claim-to-evidence map",
            "## Artifact preservation audit",
            "## Independent domain review",
            "Source/control follow-up result on 2026-09-04: pass.",
            "Rendered-output follow-up result on 2026-09-04: pass.",
        ),
        "methodology evidence-note heading",
        errors,
    )
    for claim_id in (*METHODOLOGY_CLAIMS, *METHODOLOGY_TABLE_CLAIMS):
        if f"`{claim_id}`" not in evidence_note:
            errors.append(f"{METHODOLOGY_NOTE}: missing claim map for {claim_id}")

    for identifier, expected_location in METHODOLOGY_CLAIMS.items():
        record = claims.get(identifier)
        if record is None:
            errors.append(f"missing methodology claim {identifier}")
            continue
        _require_exact(
            record.get("manuscript_location"),
            expected_location,
            f"{identifier} manuscript location",
            errors,
        )
        if record.get("review_state") not in RESOLVED_REVIEW_STATES:
            errors.append(f"{identifier}: methodology claim is not reviewed")
        _validate_authority_paths(root, identifier, record, errors)

    for identifier, (expected_location, expected_wording) in (
        METHODOLOGY_TABLE_CLAIMS.items()
    ):
        table_claim = claims.get(identifier)
        if table_claim is None:
            errors.append(f"missing methodology table claim {identifier}")
            continue
        _require_exact(
            table_claim.get("manuscript_location"),
            expected_location,
            f"{identifier} manuscript location",
            errors,
        )
        _require_exact(
            table_claim.get("wording"),
            expected_wording,
            f"{identifier} wording",
            errors,
        )
        _require_exact(
            table_claim.get("entry_type"),
            "manuscript-table",
            f"{identifier} entry type",
            errors,
        )
        if table_claim.get("review_state") not in RESOLVED_REVIEW_STATES:
            errors.append(f"{identifier}: methodology table claim is not reviewed")
        _validate_authority_paths(root, identifier, table_claim, errors)

    for identifier, expected_location in METHODOLOGY_NOTATION.items():
        record = notation.get(identifier)
        if record is None:
            errors.append(f"missing methodology notation {identifier}")
            continue
        _require_exact(
            record.get("first_use"),
            expected_location,
            f"{identifier} first use",
            errors,
        )
        if record.get("review_state") not in RESOLVED_REVIEW_STATES:
            errors.append(f"{identifier}: methodology notation is not reviewed")

    for identifier in METHODOLOGY_NONCLAIMS:
        record = nonclaims.get(identifier)
        if record is None:
            errors.append(f"missing methodology non-claim {identifier}")
            continue
        affected = record.get("affected_locations")
        if not isinstance(affected, list) or "ch:methodology" not in affected:
            errors.append(f"{identifier}: Chapter 6 is not an affected location")
        for path in record.get("authority_paths", []):
            if isinstance(path, str):
                validate_repository_file(root, identifier, path, errors)

    for relative_path, expected_hash in EXPECTED_PROTOCOL_HASHES.items():
        path = root / relative_path
        try:
            actual_hash = _sha256(path)
        except OSError as error:
            errors.append(f"{relative_path}: cannot fingerprint ({error})")
            continue
        _require_exact(
            actual_hash,
            expected_hash,
            f"{relative_path} SHA-256",
            errors,
        )
    for relative_path, expected_hash in EXPECTED_RECEIPT_HASHES.items():
        path = root / relative_path
        try:
            actual_hash = _sha256(path)
        except OSError as error:
            errors.append(f"{relative_path}: cannot fingerprint ({error})")
            continue
        _require_exact(
            actual_hash,
            expected_hash,
            f"{relative_path} SHA-256",
            errors,
        )
    _require_exact(protocol_v1.get("locked"), True, "v1 protocol lock", errors)
    _require_exact(protocol_v2.get("locked"), True, "v2 protocol lock", errors)
    _require_exact(
        protocol_v2.get("confirmatory_outcomes_accessed"),
        False,
        "v2 registration-time outcome access",
        errors,
    )
    for field in sorted(OUTCOME_RELEVANT_PROTOCOL_FIELDS):
        _require_exact(
            protocol_v2.get(field),
            protocol_v1.get(field),
            f"provider replacement inherited {field}",
            errors,
        )

    episode_design = protocol_v2.get("episode_design", {})
    coverage = protocol_v2.get("coverage", {})
    corrected_mean = protocol_v2.get("corrected_mean", {})
    cost_scenarios = protocol_v2.get("cost_scenarios", [])
    uncertainty = protocol_v2.get("uncertainty", {})
    multiplicity = protocol_v2.get("multiplicity", {})
    if isinstance(episode_design, dict):
        _require_exact(
            episode_design.get("deposit_amount"),
            "1000",
            "historical deposit amount",
            errors,
        )
        _require_exact(
            episode_design.get("horizons_months"),
            [12, 36, 60],
            "primary historical horizons",
            errors,
        )
        _require_exact(
            episode_design.get("rolling_stride_months"),
            1,
            "primary rolling stride",
            errors,
        )
    if isinstance(coverage, dict):
        _require_exact(
            coverage.get("primary"),
            ["1", "0.9", "0.75", "0.5"],
            "primary coverage",
            errors,
        )
        _require_exact(
            coverage.get("robustness"),
            ["0.99", "0.95", "0.8", "0.6", "0.25"],
            "robustness coverage",
            errors,
        )
    if isinstance(corrected_mean, dict):
        primary_means = corrected_mean.get("primary")
        if not isinstance(primary_means, list) or len(primary_means) != 1:
            errors.append("primary corrected-mean grid must contain one item")
        else:
            expected_mean = {
                "config_id": "identity-a0-b0",
                "transform": "identity",
                "alpha": "0",
                "beta": "0",
                "weights": "equal",
                "selection_reason": (
                    "the theoretically admissible countercyclical diagonal "
                    "baseline, fixed without historical outcome access"
                ),
            }
            _require_exact(
                primary_means[0], expected_mean, "primary corrected mean", errors
            )
    expected_cost_scenarios = [
        {
            "cost_id": "frictionless",
            "fixed_fee": "0",
            "proportional_bps": "0",
            "accounting_rule": "asset notional equals the selected cash budget",
            "theorem_scope": "epsilon-dca",
        },
        {
            "cost_id": "proportional-10bps",
            "fixed_fee": "0",
            "proportional_bps": "10",
            "accounting_rule": (
                "fee equals 10 basis points of asset notional and notional "
                "plus fee cannot exceed the selected cash budget"
            ),
            "theorem_scope": "outside-current-safety-theorem",
        },
        {
            "cost_id": "fixed-1-usd",
            "fixed_fee": "1",
            "proportional_bps": "0",
            "accounting_rule": (
                "a one-dollar fee applies only when the selected cash budget "
                "exceeds one dollar; otherwise no purchase or fee occurs"
            ),
            "theorem_scope": "outside-current-safety-theorem",
        },
    ]
    _require_exact(
        cost_scenarios,
        expected_cost_scenarios,
        "cost execution models",
        errors,
    )
    if isinstance(uncertainty, dict):
        _require_exact(
            uncertainty.get("method"),
            "circular-moving-block-bootstrap",
            "uncertainty method",
            errors,
        )
        _require_exact(
            uncertainty.get("replicates"), 10000, "bootstrap replicates", errors
        )
        _require_exact(
            uncertainty.get("seed"), 20260825, "bootstrap base seed", errors
        )
    if isinstance(multiplicity, dict):
        _require_exact(
            multiplicity.get("method"), "holm", "multiplicity method", errors
        )
        _require_exact(
            multiplicity.get("alpha"), "0.05", "multiplicity alpha", errors
        )

    hypotheses = protocol_v2.get("hypotheses", [])
    confirmatory_hypotheses = (
        [item for item in hypotheses if item.get("tier") == "confirmatory"]
        if isinstance(hypotheses, list)
        else []
    )
    _require_exact(
        [item.get("hypothesis_id") for item in confirmatory_hypotheses],
        ["H1-complete-system", "H2-signal-contribution"],
        "confirmatory hypotheses",
        errors,
    )

    _require_exact(
        robustness_plan.get("created_after_confirmatory_outcome_access"),
        True,
        "robustness timing",
        errors,
    )
    analysis = robustness_plan.get("analysis", {})
    if isinstance(analysis, dict):
        _require_exact(
            analysis.get("uncertainty"),
            "descriptive-only; no confirmatory bootstrap or multiplicity test",
            "robustness uncertainty",
            errors,
        )
        _require_exact(
            analysis.get("confirmatory_family_change"),
            "none",
            "robustness family change",
            errors,
        )

    _require_exact(
        source_receipt.get("source_set_id"),
        "yahoo-finance-historical-8b6758e9ad215699e21cd8907e233e00407a70c1b13b13b5490e1578921e260b",
        "accepted Yahoo source-set identity",
        errors,
    )
    sources = source_receipt.get("sources", [])
    expected_source_hashes = {
        "spy-adjusted-daily": (
            "eaf69d50bef6d77ff68fb6a52e0cc162c12eded8d8f00ef48d79922d0784458d"
        ),
        "btc-usd-daily": (
            "add11cc84321e32785034c07eced636fc01be8c7202867926b9e2ee77e23b3ee"
        ),
    }
    actual_source_hashes = (
        {
            item.get("dataset_id"): item.get("expected_sha256")
            for item in sources
            if isinstance(item, dict)
        }
        if isinstance(sources, list)
        else {}
    )
    _require_exact(
        actual_source_hashes,
        expected_source_hashes,
        "accepted source export fingerprints",
        errors,
    )
    _require_exact(
        preparation_manifest.get("run_id"),
        "smartdca-historical-input-v1-4da2c9a1982b48cc821969e802118270d7a95e44cc03107e8d2846729df0e14f",
        "accepted preparation identity",
        errors,
    )
    _require_exact(
        preparation_manifest.get("policy_execution"),
        "not-run",
        "accepted preparation policy state",
        errors,
    )
    _require_exact(
        preparation_manifest.get("runner_input_sha256"),
        "d49a5a6e0304a7da213082698990d46bec7f7cac2399533990f84a40183bec88",
        "accepted runner-input fingerprint",
        errors,
    )

    accepted_manifests = review_manifest.get("accepted_run_manifests", [])
    accepted_run_ids = (
        {
            item.get("run_id")
            for item in accepted_manifests
            if isinstance(item, dict) and isinstance(item.get("run_id"), str)
        }
        if isinstance(accepted_manifests, list)
        else set()
    )
    _require_exact(
        accepted_run_ids, EXPECTED_RUN_IDS, "accepted publication runs", errors
    )
    _require_exact(review_receipt.get("status"), "passed", "review receipt", errors)
    provenance_audit = review_receipt.get("provenance_audit", {})
    if isinstance(provenance_audit, dict):
        _require_exact(
            provenance_audit.get("accepted_run_count"),
            7,
            "reviewed run count",
            errors,
        )
    _require_exact(
        review_manifest.get("review_id"),
        "smartdca-empirical-package-review-v1-6cb6c1cd94b901be90ebd553a022c922e53984afafeb22948747be084b37c14f",
        "independent review identity",
        errors,
    )

    bibliography_keys = extract_bibtex_keys(bibliography)
    cited_keys = extract_latex_citation_keys(
        chapter + protocol_appendix + reproducibility_appendix
    )
    declared_citation_keys: set[str] = set()
    for identifier in METHODOLOGY_CLAIMS:
        record = claims.get(identifier, {})
        citation_keys = record.get("citation_keys", [])
        if not isinstance(citation_keys, list) or not all(
            isinstance(key, str) for key in citation_keys
        ):
            errors.append(f"{identifier}: invalid citation_keys")
            continue
        declared_citation_keys.update(citation_keys)
        for citation in citation_keys:
            if citation not in bibliography_keys:
                errors.append(f"{identifier}: missing bibliography key {citation}")
            if citation not in cited_keys:
                errors.append(f"{identifier}: methodology slice does not cite {citation}")
    _require_exact(
        declared_citation_keys,
        REQUIRED_CITATIONS,
        "methodology claim citation-key set",
        errors,
    )
    for citation in sorted(REQUIRED_CITATIONS):
        if citation not in bibliography_keys:
            errors.append(f"missing methodology bibliography key {citation}")
        if citation not in cited_keys:
            errors.append(f"methodology slice does not cite {citation}")

    if errors:
        raise MethodologyControlError("\n".join(errors))

    return {
        "status": "passed",
        "policy_count": 3,
        "comparison_tier_count": 3,
        "evidence_layer_count": 4,
        "confirmatory_hypothesis_count": len(confirmatory_hypotheses),
        "methodology_claim_count": len(METHODOLOGY_CLAIMS),
        "methodology_table_claim_count": len(METHODOLOGY_TABLE_CLAIMS),
        "accepted_run_count": len(accepted_run_ids),
        "cost_execution_model_count": len(cost_scenarios),
        "independent_manuscript_review_status": "passed",
        "appendix_count": sum(
            bool(value) for value in (protocol_appendix, reproducibility_appendix)
        ),
        "protocol_sha256": {
            relative_path: expected_hash
            for relative_path, expected_hash in EXPECTED_PROTOCOL_HASHES.items()
        },
        "source_receipt_count": len(actual_source_hashes),
        "citation_count": len(REQUIRED_CITATIONS),
        "source_receipt_sha256": EXPECTED_RECEIPT_HASHES[
            "experiments/inputs/historical-yahoo-receipts-v2.json"
        ],
        "preparation_manifest_sha256": EXPECTED_RECEIPT_HASHES[
            "experiments/inputs/historical-yahoo-preparation-manifest-v5.json"
        ],
        "independent_review_receipt_sha256": EXPECTED_RECEIPT_HASHES[
            "reports/experiments/runs/"
            "smartdca-empirical-package-review-v1-"
            "6cb6c1cd94b901be90ebd553a022c922e53984afafeb22948747be084b37c14f/"
            "review-receipt.json"
        ],
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
        receipt = audit_empirical_methodology_reproducibility(
            args.repository_root
        )
    except MethodologyControlError as error:
        print(f"EMPIRICAL METHODOLOGY AUDIT FAILED\n{error}")
        return 1
    print(
        "EMPIRICAL METHODOLOGY AUDIT PASSED: "
        f"{receipt['methodology_claim_count']} claims, "
        f"{receipt['accepted_run_count']} accepted runs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
