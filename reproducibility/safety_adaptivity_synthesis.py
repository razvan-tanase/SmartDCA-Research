"""Build the reviewed cross-layer SmartDCA safety-adaptivity synthesis."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import platform
import shutil
import tempfile
from dataclasses import dataclass
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any, Mapping, Sequence


ENGINE_VERSION = "smartdca-safety-adaptivity-synthesis/1"
SCHEMA_VERSION = "smartdca-safety-adaptivity-synthesis/1"
OUTPUT_SCHEMA_VERSION = "smartdca-safety-adaptivity-synthesis-manifest/1"

getcontext().prec = 100


class SynthesisValidationError(ValueError):
    """Raised when a synthesis input is not the exact reviewed evidence."""


class SynthesisIdentityCollisionError(FileExistsError):
    """Raised when a synthesis output identity already exists."""


@dataclass(frozen=True)
class SynthesisBundle:
    synthesis_run_id: str
    output_directory: Path
    manifest: Mapping[str, Any]


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _require(condition: bool, field: str, message: str) -> None:
    if not condition:
        raise SynthesisValidationError(f"{field}: {message}")


def _document(payload: bytes, field: str) -> dict[str, Any]:
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SynthesisValidationError(f"{field}: must be valid UTF-8 JSON") from error
    _require(isinstance(value, dict), field, "must be a JSON object")
    return value


def _nested_value(document: Mapping[str, Any], path: Any, field: str) -> Any:
    _require(
        isinstance(path, list) and path and all(isinstance(part, str) for part in path),
        field,
        "must be a nonempty array of object keys",
    )
    value: Any = document
    for part in path:
        _require(
            isinstance(value, dict) and part in value,
            field,
            f"does not resolve at {part!r}",
        )
        value = value[part]
    return value


def _repository_path(root: Path, value: Any, field: str) -> Path:
    _require(isinstance(value, str) and bool(value), field, "must be a nonempty path")
    relative = Path(value)
    _require(not relative.is_absolute(), field, "must be repository-relative")
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise SynthesisValidationError(f"{field}: escapes the repository root") from error
    _require(path.is_file(), field, "does not exist")
    return path


def _verified_bytes(root: Path, path_value: Any, digest: Any, field: str) -> tuple[Path, bytes]:
    path = _repository_path(root, path_value, f"{field}.path")
    payload = path.read_bytes()
    _require(
        isinstance(digest, str) and _sha256(payload) == digest,
        f"{field}.sha256",
        "does not match the accepted bytes",
    )
    return path, payload


def _manifest_artifact_digest(
    manifest: Mapping[str, Any], relative_path: str
) -> str | None:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        return None
    for artifact in artifacts:
        if isinstance(artifact, dict) and artifact.get("path") == relative_path:
            digest = artifact.get("sha256")
            return digest if isinstance(digest, str) else None
    return None


def _analysis_tier(source: Mapping[str, Any], row: Mapping[str, Any]) -> str:
    declared = row.get("analysis_tier")
    if isinstance(declared, str) and declared:
        return declared
    family = row.get("family")
    primary = source.get("primary_families", [])
    if family in primary:
        return "primary"
    if family == "adversarial-design-iteration":
        return "exploratory"
    return "regression"


def _decimal_string(value: Any, field: str) -> str:
    if value is None:
        return ""
    try:
        return str(Decimal(str(value)))
    except Exception as error:
        raise SynthesisValidationError(f"{field}: must be decimal-compatible") from error


def _scheduled_deposit_count(
    source: Mapping[str, Any], row: Mapping[str, Any]
) -> Decimal:
    intervals = source.get("schedule_intervals_months")
    _require(
        isinstance(intervals, dict) and intervals,
        f"{source['source_id']}.schedule_intervals_months",
        "must be a nonempty object",
    )
    schedule_id = row.get("schedule_id")
    interval_key = schedule_id if isinstance(schedule_id, str) and schedule_id else "default"
    _require(
        interval_key in intervals,
        f"{source['source_id']}.schedule_intervals_months",
        f"has no rule for {interval_key!r}",
    )
    interval = Decimal(str(intervals[interval_key]))
    horizon = Decimal(str(row.get("horizon_months")))
    _require(
        interval > 0 and interval == interval.to_integral_value(),
        f"{source['source_id']}.schedule_intervals_months.{interval_key}",
        "must be a positive integer",
    )
    _require(
        horizon > 0
        and horizon == horizon.to_integral_value()
        and horizon % interval == 0,
        "aggregate.horizon_months",
        "must be a positive integer divisible by the declared deposit interval",
    )
    return horizon / interval


NORMALIZED_FIELDS = (
    "source_id",
    "evidence_layer",
    "source_run_id",
    "episode_evidence",
    "deposit_amount",
    "analysis_tier",
    "design_tier",
    "schedule_id",
    "dataset_id",
    "family",
    "generator_config_id",
    "horizon_months",
    "coverage",
    "cost_scenario",
    "cost_scope",
    "theorem_scope",
    "comparison",
    "comparison_role",
    "corrected_mean_config",
    "sample_count",
    "attempted_count",
    "excluded_count",
    "median_relative_terminal_wealth_gap",
    "mean_relative_terminal_wealth_gap",
    "downside_quantile_0.05",
    "worst_observed_relative_shortfall",
    "minimum_relative_terminal_wealth_gap",
    "maximum_relative_terminal_wealth_gap",
    "mean_left_cash_drag",
    "mean_left_asset_exposure",
    "mean_left_guardrail_activation_frequency",
    "mean_left_guardrail_floor",
    "mean_left_guardrail_floor_per_deposit",
    "mean_left_purchase_count",
    "mean_right_purchase_count",
    "scheduled_deposit_count",
    "mean_contributed_capital",
    "mean_terminal_cash_gap",
    "mean_terminal_unit_gap",
    "mean_terminal_wealth_gap",
    "mean_cash_contribution",
    "mean_unit_contribution",
    "mean_terminal_wealth_gap_per_contributed_capital",
    "mean_cash_contribution_per_contributed_capital",
    "mean_unit_contribution_per_contributed_capital",
    "win_count",
    "tie_count",
    "loss_count",
)


DECIMAL_FIELDS = {
    "median_relative_terminal_wealth_gap",
    "mean_relative_terminal_wealth_gap",
    "downside_quantile_0.05",
    "worst_observed_relative_shortfall",
    "minimum_relative_terminal_wealth_gap",
    "maximum_relative_terminal_wealth_gap",
    "mean_left_cash_drag",
    "mean_left_asset_exposure",
    "mean_left_guardrail_activation_frequency",
    "mean_left_guardrail_floor",
    "mean_left_guardrail_floor_per_deposit",
    "mean_left_purchase_count",
    "mean_right_purchase_count",
    "scheduled_deposit_count",
    "mean_contributed_capital",
    "mean_terminal_cash_gap",
    "mean_terminal_unit_gap",
    "mean_terminal_wealth_gap",
    "mean_cash_contribution",
    "mean_unit_contribution",
    "mean_terminal_wealth_gap_per_contributed_capital",
    "mean_cash_contribution_per_contributed_capital",
    "mean_unit_contribution_per_contributed_capital",
}


def _normalize_row(
    source: Mapping[str, Any],
    row: Mapping[str, Any],
    comparison_roles: Mapping[str, Any],
    cost_scopes: Mapping[str, Any],
) -> dict[str, Any]:
    comparison = row.get("comparison")
    cost_scenario = row.get("cost_scenario")
    _require(
        comparison in comparison_roles,
        "aggregate.comparison",
        "is not declared by comparison_roles",
    )
    _require(
        cost_scenario in cost_scopes,
        "aggregate.cost_scenario",
        "is not declared by cost_scopes",
    )

    cash_contribution = row.get("mean_cash_contribution")
    if cash_contribution is None:
        cash_contribution = row.get("mean_terminal_cash_gap")
    unit_contribution = row.get("mean_unit_contribution")
    if unit_contribution is None:
        wealth_gap = Decimal(str(row.get("mean_terminal_wealth_gap", "0")))
        cash_gap = Decimal(str(row.get("mean_terminal_cash_gap", "0")))
        unit_contribution = wealth_gap - cash_gap
    deposit_amount = Decimal(str(source.get("deposit_amount")))
    left_guardrail_floor = Decimal(str(row.get("mean_left_guardrail_floor")))
    right_purchase_count = Decimal(str(row.get("mean_right_purchase_count")))
    scheduled_deposit_count = _scheduled_deposit_count(source, row)
    _require(
        deposit_amount > 0,
        f"{source['source_id']}.deposit_amount",
        "must be positive",
    )
    _require(
        Decimal(0) <= left_guardrail_floor <= deposit_amount,
        "aggregate.mean_left_guardrail_floor",
        "must fall between zero and the reviewed deposit amount",
    )
    _require(
        right_purchase_count == scheduled_deposit_count,
        "aggregate.mean_right_purchase_count",
        "does not match the deposit count implied by the reviewed schedule",
    )
    contributed_capital = deposit_amount * scheduled_deposit_count
    terminal_wealth_gap = Decimal(str(row.get("mean_terminal_wealth_gap")))
    cash_contribution_decimal = Decimal(str(cash_contribution))
    unit_contribution_decimal = Decimal(str(unit_contribution))

    normalized: dict[str, Any] = {
        "source_id": source["source_id"],
        "evidence_layer": source["evidence_layer"],
        "source_run_id": source["run_id"],
        "episode_evidence": source["episode_evidence"],
        "deposit_amount": deposit_amount,
        "analysis_tier": _analysis_tier(source, row),
        "design_tier": row.get("design_tier", ""),
        "schedule_id": row.get("schedule_id", ""),
        "dataset_id": row.get("dataset_id", ""),
        "family": row.get("family", ""),
        "generator_config_id": row.get("generator_config_id", ""),
        "horizon_months": row.get("horizon_months", ""),
        "coverage": row.get("coverage", ""),
        "cost_scenario": cost_scenario,
        "cost_scope": cost_scopes[cost_scenario],
        "theorem_scope": row.get("theorem_scope", ""),
        "comparison": comparison,
        "comparison_role": comparison_roles[comparison],
        "corrected_mean_config": row.get("corrected_mean_config", ""),
        "sample_count": row.get("sample_count", ""),
        "attempted_count": row.get("attempted_count", ""),
        "excluded_count": row.get("excluded_count", ""),
        "median_relative_terminal_wealth_gap": row.get(
            "median_relative_terminal_wealth_gap"
        ),
        "mean_relative_terminal_wealth_gap": row.get(
            "mean_relative_terminal_wealth_gap"
        ),
        "downside_quantile_0.05": row.get("downside_quantile_0.05"),
        "worst_observed_relative_shortfall": row.get(
            "worst_observed_relative_shortfall",
            max(Decimal("0"), -Decimal(str(row["minimum_relative_terminal_wealth_gap"]))),
        ),
        "minimum_relative_terminal_wealth_gap": row.get(
            "minimum_relative_terminal_wealth_gap"
        ),
        "maximum_relative_terminal_wealth_gap": row.get(
            "maximum_relative_terminal_wealth_gap"
        ),
        "mean_left_cash_drag": row.get("mean_left_cash_drag"),
        "mean_left_asset_exposure": row.get("mean_left_asset_exposure"),
        "mean_left_guardrail_activation_frequency": row.get(
            "mean_left_guardrail_activation_frequency"
        ),
        "mean_left_guardrail_floor": left_guardrail_floor,
        "mean_left_guardrail_floor_per_deposit": (
            left_guardrail_floor / deposit_amount
        ),
        "mean_left_purchase_count": row.get("mean_left_purchase_count"),
        "mean_right_purchase_count": right_purchase_count,
        "scheduled_deposit_count": scheduled_deposit_count,
        "mean_contributed_capital": contributed_capital,
        "mean_terminal_cash_gap": row.get("mean_terminal_cash_gap"),
        "mean_terminal_unit_gap": row.get("mean_terminal_unit_gap"),
        "mean_terminal_wealth_gap": row.get("mean_terminal_wealth_gap"),
        "mean_cash_contribution": cash_contribution,
        "mean_unit_contribution": unit_contribution,
        "mean_terminal_wealth_gap_per_contributed_capital": (
            terminal_wealth_gap / contributed_capital
        ),
        "mean_cash_contribution_per_contributed_capital": (
            cash_contribution_decimal / contributed_capital
        ),
        "mean_unit_contribution_per_contributed_capital": (
            unit_contribution_decimal / contributed_capital
        ),
        "win_count": row.get("win_count", ""),
        "tie_count": row.get("tie_count", ""),
        "loss_count": row.get("loss_count", ""),
    }
    for field in DECIMAL_FIELDS:
        normalized[field] = _decimal_string(normalized[field], field)
    return normalized


def _validate_source(
    root: Path,
    source: Mapping[str, Any],
    comparison_roles: Mapping[str, Any],
    cost_scopes: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    source_id = source.get("source_id")
    _require(isinstance(source_id, str) and bool(source_id), "source_id", "is required")
    _require(
        source.get("review_status") == "pass",
        f"{source_id}.review_status",
        "must equal pass",
    )
    manifest_path, manifest_payload = _verified_bytes(
        root,
        source.get("manifest_path"),
        source.get("manifest_sha256"),
        f"{source_id}.manifest",
    )
    manifest = _document(manifest_payload, f"{source_id}.manifest")
    _require(
        manifest.get("schema_version") == source.get("manifest_schema"),
        f"{source_id}.manifest.schema_version",
        "does not match the reviewed schema",
    )
    run_id_field = source.get("run_id_field")
    _require(
        isinstance(run_id_field, str) and manifest.get(run_id_field) == source.get("run_id"),
        f"{source_id}.manifest.{run_id_field}",
        "does not match the reviewed run identity",
    )

    supporting_artifacts: list[dict[str, str]] = []
    deposit_path, deposit_payload = _verified_bytes(
        root,
        source.get("deposit_evidence_path"),
        source.get("deposit_evidence_sha256"),
        f"{source_id}.deposit_evidence",
    )
    deposit_manifest_field = source.get("deposit_evidence_manifest_field")
    _require(
        isinstance(deposit_manifest_field, str)
        and manifest.get(deposit_manifest_field)
        == source.get("deposit_evidence_sha256"),
        f"{source_id}.manifest.{deposit_manifest_field}",
        "does not bind the reviewed deposit evidence",
    )
    deposit_document = _document(deposit_payload, f"{source_id}.deposit_evidence")
    reviewed_deposit = _nested_value(
        deposit_document,
        source.get("deposit_amount_json_path"),
        f"{source_id}.deposit_amount_json_path",
    )
    try:
        deposit_matches = Decimal(str(source.get("deposit_amount"))) == Decimal(
            str(reviewed_deposit)
        )
    except Exception as error:
        raise SynthesisValidationError(
            f"{source_id}.deposit_amount: must be decimal-compatible"
        ) from error
    _require(
        deposit_matches,
        f"{source_id}.deposit_amount",
        "does not match reviewed source bytes",
    )
    supporting_artifacts.append(
        {
            "kind": "deposit-evidence",
            "path": deposit_path.relative_to(root).as_posix(),
            "sha256": source["deposit_evidence_sha256"],
        }
    )

    aggregate_path, aggregate_payload = _verified_bytes(
        root,
        source.get("aggregate_path"),
        source.get("aggregate_sha256"),
        f"{source_id}.aggregate",
    )
    aggregate_relative = aggregate_path.relative_to(manifest_path.parent).as_posix()
    _require(
        _manifest_artifact_digest(manifest, aggregate_relative)
        == source.get("aggregate_sha256"),
        f"{source_id}.manifest.artifacts",
        "does not bind the selected aggregate bytes",
    )
    aggregate = _document(aggregate_payload, f"{source_id}.aggregate")
    groups = aggregate.get("groups")
    _require(isinstance(groups, list), f"{source_id}.aggregate.groups", "must be an array")
    _require(
        aggregate.get("group_count") == source.get("expected_group_count") == len(groups),
        f"{source_id}.aggregate.group_count",
        "does not match the reviewed group count",
    )

    review_path, review_payload = _verified_bytes(
        root,
        source.get("review_record_path"),
        source.get("review_record_sha256"),
        f"{source_id}.review_record",
    )
    review_text = review_payload.decode("utf-8")
    markers = source.get("required_review_markers")
    _require(
        isinstance(markers, list) and markers,
        f"{source_id}.required_review_markers",
        "must be a nonempty array",
    )
    for marker in markers:
        _require(
            isinstance(marker, str) and marker in review_text,
            f"{source_id}.review_record",
            f"is missing required acceptance marker {marker!r}",
        )

    for optional_name in ("uncertainty", "reconciliation"):
        path_key = f"{optional_name}_path"
        if path_key not in source:
            continue
        artifact_path, _ = _verified_bytes(
            root,
            source[path_key],
            source[f"{optional_name}_sha256"],
            f"{source_id}.{optional_name}",
        )
        relative = artifact_path.relative_to(manifest_path.parent).as_posix()
        _require(
            _manifest_artifact_digest(manifest, relative)
            == source[f"{optional_name}_sha256"],
            f"{source_id}.manifest.artifacts",
            f"does not bind {optional_name}",
        )
        supporting_artifacts.append(
            {
                "kind": optional_name,
                "path": artifact_path.relative_to(root).as_posix(),
                "sha256": source[f"{optional_name}_sha256"],
            }
        )

    rows = [
        _normalize_row(source, row, comparison_roles, cost_scopes)
        for row in groups
    ]
    validation = {
        "source_id": source_id,
        "evidence_layer": source.get("evidence_layer"),
        "run_id": source.get("run_id"),
        "manifest_path": manifest_path.relative_to(root).as_posix(),
        "manifest_sha256": source.get("manifest_sha256"),
        "aggregate_path": aggregate_path.relative_to(root).as_posix(),
        "aggregate_sha256": source.get("aggregate_sha256"),
        "aggregate_group_count": len(groups),
        "review_record_path": review_path.relative_to(root).as_posix(),
        "review_record_sha256": source.get("review_record_sha256"),
        "review_status": "pass",
        "episode_evidence": source.get("episode_evidence"),
        "deposit_amount": str(source.get("deposit_amount")),
        "schedule_intervals_months": source.get("schedule_intervals_months"),
        "supporting_artifacts": supporting_artifacts,
    }
    return validation, rows


def _validate_theory_sources(root: Path, sources: Any) -> list[dict[str, Any]]:
    _require(isinstance(sources, list) and sources, "theory_sources", "must be nonempty")
    receipts: list[dict[str, Any]] = []
    for index, source in enumerate(sources):
        field = f"theory_sources[{index}]"
        _require(isinstance(source, dict), field, "must be an object")
        receipt = {"claim": source.get("claim")}
        for kind in ("canonical", "evidence", "check"):
            path, _ = _verified_bytes(
                root,
                source.get(f"{kind}_path"),
                source.get(f"{kind}_sha256"),
                f"{field}.{kind}",
            )
            receipt[f"{kind}_path"] = path.relative_to(root).as_posix()
            receipt[f"{kind}_sha256"] = source[f"{kind}_sha256"]
        receipts.append(receipt)
    return receipts


def _write_json(path: Path, value: Any) -> None:
    path.write_text(_canonical_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]], fields: Sequence[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _matches(row: Mapping[str, Any], filters: Mapping[str, Any]) -> bool:
    for field, accepted in filters.items():
        _require(
            isinstance(accepted, list) and accepted,
            f"filters.{field}",
            "must be a nonempty array",
        )
        if row.get(field) not in accepted:
            return False
    return True


def _decimals(rows: Sequence[Mapping[str, Any]], field: str) -> list[Decimal]:
    values: list[Decimal] = []
    for row in rows:
        value = row.get(field)
        if value not in (None, ""):
            values.append(Decimal(str(value)))
    _require(bool(values), field, "has no values in the selected rows")
    return values


def _median(values: Sequence[Decimal]) -> Decimal:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / Decimal(2)


def _mean(values: Sequence[Decimal]) -> Decimal:
    return sum(values, Decimal(0)) / Decimal(len(values))


def _sign_counts(rows: Sequence[Mapping[str, Any]], field: str) -> tuple[int, int, int]:
    values = _decimals(rows, field)
    return (
        sum(value < 0 for value in values),
        sum(value == 0 for value in values),
        sum(value > 0 for value in values),
    )


CROSS_LAYER_FIELDS = (
    "slice_id",
    "label",
    "evidence_layer",
    "analysis_tier",
    "evidence_scope",
    "comparison",
    "comparison_role",
    "cell_count",
    "sample_count_minimum",
    "sample_count_maximum",
    "negative_median_cells",
    "zero_median_cells",
    "positive_median_cells",
    "minimum_cell_median",
    "maximum_cell_median",
    "minimum_cell_downside_0.05",
    "maximum_worst_observed_relative_shortfall",
    "holm_significant_cells",
    "holm_tested_cells",
    "inference_status",
    "sampling_boundary",
)


def _cross_layer_summaries(
    specification: Mapping[str, Any],
    rows_by_source: Mapping[str, Sequence[Mapping[str, Any]]],
    uncertainty_by_source: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    roles = specification["comparison_roles"]
    summaries: list[dict[str, Any]] = []
    slices = specification.get("summary_slices")
    _require(isinstance(slices, list) and slices, "summary_slices", "must be nonempty")
    for index, slice_spec in enumerate(slices):
        field = f"summary_slices[{index}]"
        _require(isinstance(slice_spec, dict), field, "must be an object")
        source_id = slice_spec.get("source_id")
        _require(source_id in rows_by_source, f"{field}.source_id", "is not reviewed")
        filters = slice_spec.get("filters", {})
        _require(isinstance(filters, dict), f"{field}.filters", "must be an object")
        selected = [row for row in rows_by_source[source_id] if _matches(row, filters)]
        _require(bool(selected), field, "selects no reviewed aggregate rows")
        layer = selected[0]["evidence_layer"]
        for comparison, role in roles.items():
            comparison_rows = [
                row for row in selected if row["comparison"] == comparison
            ]
            _require(bool(comparison_rows), field, f"has no {comparison} rows")
            analysis_tiers = sorted(
                {str(row["analysis_tier"]) for row in comparison_rows}
            )
            _require(
                len(analysis_tiers) == 1,
                field,
                f"mixes analysis tiers for {comparison}: {analysis_tiers}",
            )
            negative, zero, positive = _sign_counts(
                comparison_rows, "median_relative_terminal_wealth_gap"
            )
            medians = _decimals(
                comparison_rows, "median_relative_terminal_wealth_gap"
            )
            sample_counts = [int(row["sample_count"]) for row in comparison_rows]
            uncertainty_rows = [
                row
                for row in uncertainty_by_source.get(source_id, [])
                if row.get("comparison") == comparison and _matches(row, filters)
            ]
            if uncertainty_rows:
                significant = sum(
                    Decimal(str(row["holm_adjusted_p_value"])) < Decimal("0.05")
                    for row in uncertainty_rows
                )
                holm_significant: int | str = significant
                holm_tested: int | str = len(uncertainty_rows)
                inference_status = (
                    "registered dependence-aware circular moving-block bootstrap; "
                    "Holm family of 36"
                )
            else:
                holm_significant = ""
                holm_tested = ""
                inference_status = "descriptive; no registered test"
            summaries.append(
                {
                    "slice_id": slice_spec.get("slice_id"),
                    "label": slice_spec.get("label"),
                    "evidence_layer": layer,
                    "analysis_tier": analysis_tiers[0],
                    "evidence_scope": slice_spec.get("evidence_scope"),
                    "comparison": comparison,
                    "comparison_role": role,
                    "cell_count": len(comparison_rows),
                    "sample_count_minimum": min(sample_counts),
                    "sample_count_maximum": max(sample_counts),
                    "negative_median_cells": negative,
                    "zero_median_cells": zero,
                    "positive_median_cells": positive,
                    "minimum_cell_median": str(min(medians)),
                    "maximum_cell_median": str(max(medians)),
                    "minimum_cell_downside_0.05": str(
                        min(_decimals(comparison_rows, "downside_quantile_0.05"))
                    ),
                    "maximum_worst_observed_relative_shortfall": str(
                        max(
                            _decimals(
                                comparison_rows,
                                "worst_observed_relative_shortfall",
                            )
                        )
                    ),
                    "holm_significant_cells": holm_significant,
                    "holm_tested_cells": holm_tested,
                    "inference_status": inference_status,
                    "sampling_boundary": slice_spec.get("sampling_boundary"),
                }
            )
    return summaries


CURVE_FIELDS = (
    "slice_id",
    "label",
    "evidence_layer",
    "analysis_tier",
    "evidence_scope",
    "coverage",
    "comparison",
    "comparison_role",
    "cell_count",
    "sample_count_minimum",
    "sample_count_maximum",
    "median_of_cell_medians",
    "minimum_cell_median",
    "maximum_cell_median",
    "minimum_cell_downside_0.05",
    "maximum_worst_observed_relative_shortfall",
    "median_left_cash_drag",
    "median_left_asset_exposure",
    "median_left_guardrail_activation_frequency",
    "median_left_guardrail_floor_per_deposit",
    "median_left_purchase_count",
    "mean_terminal_wealth_gap_per_contributed_capital",
    "mean_cash_contribution_per_contributed_capital",
    "mean_unit_contribution_per_contributed_capital",
    "normalized_cash_unit_identity_residual",
    "cost_scope",
    "aggregation",
)


def _curve_summaries(
    specification: Mapping[str, Any],
    rows_by_source: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    slices = specification.get("curve_slices")
    _require(isinstance(slices, list) and slices, "curve_slices", "must be nonempty")
    for index, slice_spec in enumerate(slices):
        field = f"curve_slices[{index}]"
        _require(isinstance(slice_spec, dict), field, "must be an object")
        source_id = slice_spec.get("source_id")
        _require(source_id in rows_by_source, f"{field}.source_id", "is not reviewed")
        filters = slice_spec.get("filters", {})
        _require(isinstance(filters, dict), f"{field}.filters", "must be an object")
        selected = [row for row in rows_by_source[source_id] if _matches(row, filters)]
        _require(bool(selected), field, "selects no reviewed aggregate rows")
        keys = sorted(
            {(Decimal(str(row["coverage"])), row["comparison"]) for row in selected},
            key=lambda item: (item[0], item[1]),
        )
        for coverage, comparison in keys:
            cell_rows = [
                row
                for row in selected
                if Decimal(str(row["coverage"])) == coverage
                and row["comparison"] == comparison
            ]
            analysis_tiers = sorted(
                {str(row["analysis_tier"]) for row in cell_rows}
            )
            _require(
                len(analysis_tiers) == 1,
                field,
                f"mixes analysis tiers for coverage {coverage} and {comparison}",
            )
            cash = _decimals(
                cell_rows, "mean_cash_contribution_per_contributed_capital"
            )
            units = _decimals(
                cell_rows, "mean_unit_contribution_per_contributed_capital"
            )
            wealth = _decimals(
                cell_rows,
                "mean_terminal_wealth_gap_per_contributed_capital",
            )
            mean_cash = _mean(cash)
            mean_units = _mean(units)
            mean_wealth = _mean(wealth)
            sample_counts = [int(row["sample_count"]) for row in cell_rows]
            medians = _decimals(cell_rows, "median_relative_terminal_wealth_gap")
            summaries.append(
                {
                    "slice_id": slice_spec.get("slice_id"),
                    "label": slice_spec.get("label"),
                    "evidence_layer": cell_rows[0]["evidence_layer"],
                    "analysis_tier": analysis_tiers[0],
                    "evidence_scope": slice_spec.get("evidence_scope"),
                    "coverage": str(coverage),
                    "comparison": comparison,
                    "comparison_role": cell_rows[0]["comparison_role"],
                    "cell_count": len(cell_rows),
                    "sample_count_minimum": min(sample_counts),
                    "sample_count_maximum": max(sample_counts),
                    "median_of_cell_medians": str(_median(medians)),
                    "minimum_cell_median": str(min(medians)),
                    "maximum_cell_median": str(max(medians)),
                    "minimum_cell_downside_0.05": str(
                        min(_decimals(cell_rows, "downside_quantile_0.05"))
                    ),
                    "maximum_worst_observed_relative_shortfall": str(
                        max(
                            _decimals(
                                cell_rows,
                                "worst_observed_relative_shortfall",
                            )
                        )
                    ),
                    "median_left_cash_drag": str(
                        _median(_decimals(cell_rows, "mean_left_cash_drag"))
                    ),
                    "median_left_asset_exposure": str(
                        _median(_decimals(cell_rows, "mean_left_asset_exposure"))
                    ),
                    "median_left_guardrail_activation_frequency": str(
                        _median(
                            _decimals(
                                cell_rows,
                                "mean_left_guardrail_activation_frequency",
                            )
                        )
                    ),
                    "median_left_guardrail_floor_per_deposit": str(
                        _median(
                            _decimals(
                                cell_rows,
                                "mean_left_guardrail_floor_per_deposit",
                            )
                        )
                    ),
                    "median_left_purchase_count": str(
                        _median(_decimals(cell_rows, "mean_left_purchase_count"))
                    ),
                    "mean_terminal_wealth_gap_per_contributed_capital": str(
                        mean_wealth
                    ),
                    "mean_cash_contribution_per_contributed_capital": str(
                        mean_cash
                    ),
                    "mean_unit_contribution_per_contributed_capital": str(
                        mean_units
                    ),
                    "normalized_cash_unit_identity_residual": str(
                        mean_cash + mean_units - mean_wealth
                    ),
                    "cost_scope": cell_rows[0]["cost_scope"],
                    "aggregation": (
                        "descriptive across source aggregate cells; no cross-layer pooling"
                    ),
                }
            )
    return summaries


COST_FIELDS = (
    "source_id",
    "evidence_layer",
    "analysis_tier",
    "design_tier",
    "schedule_id",
    "cost_scenario",
    "cost_scope",
    "comparison",
    "comparison_role",
    "analysis_tiers",
    "cell_count",
    "negative_median_cells",
    "zero_median_cells",
    "positive_median_cells",
    "minimum_cell_median",
    "maximum_cell_median",
    "maximum_worst_observed_relative_shortfall",
    "inference_status",
)


def _cost_summaries(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    keys = sorted(
        {
            (
                row["source_id"],
                row["analysis_tier"],
                row["design_tier"],
                row["schedule_id"],
                row["cost_scenario"],
                row["comparison"],
            )
            for row in rows
            if row["cost_scenario"] != "frictionless"
            and Decimal(str(row["coverage"])) != Decimal(1)
        }
    )
    summaries = []
    for (
        source_id,
        analysis_tier,
        design_tier,
        schedule_id,
        cost_scenario,
        comparison,
    ) in keys:
        selected = [
            row
            for row in rows
            if row["source_id"] == source_id
            and row["analysis_tier"] == analysis_tier
            and row["design_tier"] == design_tier
            and row["schedule_id"] == schedule_id
            and row["cost_scenario"] == cost_scenario
            and row["comparison"] == comparison
            and Decimal(str(row["coverage"])) != Decimal(1)
        ]
        medians = _decimals(selected, "median_relative_terminal_wealth_gap")
        negative, zero, positive = _sign_counts(
            selected, "median_relative_terminal_wealth_gap"
        )
        summaries.append(
            {
                "source_id": source_id,
                "evidence_layer": selected[0]["evidence_layer"],
                "analysis_tier": analysis_tier,
                "design_tier": design_tier,
                "schedule_id": schedule_id,
                "cost_scenario": cost_scenario,
                "cost_scope": selected[0]["cost_scope"],
                "comparison": comparison,
                "comparison_role": selected[0]["comparison_role"],
                "analysis_tiers": analysis_tier,
                "cell_count": len(selected),
                "negative_median_cells": negative,
                "zero_median_cells": zero,
                "positive_median_cells": positive,
                "minimum_cell_median": str(min(medians)),
                "maximum_cell_median": str(max(medians)),
                "maximum_worst_observed_relative_shortfall": str(
                    max(
                        _decimals(
                            selected,
                            "worst_observed_relative_shortfall",
                        )
                    )
                ),
                "inference_status": (
                    "empirical net performance; outside current safety theorem; "
                    "no confirmatory inference"
                ),
            }
        )
    return summaries


def _signed_percent(value: Any, places: int = 3) -> str:
    percentage = Decimal(str(value)) * Decimal(100)
    return f"{percentage:+.{places}f}%"


def _unsigned_percent(value: Any, places: int = 3) -> str:
    percentage = Decimal(str(value)) * Decimal(100)
    return f"{percentage:.{places}f}%"


def _range_percent(row: Mapping[str, Any]) -> str:
    values = (
        Decimal(str(row["minimum_cell_median"])) * Decimal(100),
        Decimal(str(row["maximum_cell_median"])) * Decimal(100),
    )
    places = 4 if any(Decimal(0) < abs(value) < Decimal("0.001") for value in values) else 3
    return (
        f"{_signed_percent(row['minimum_cell_median'], places)} to "
        f"{_signed_percent(row['maximum_cell_median'], places)}"
    )


def _render_primary_tables(
    validations: Sequence[Mapping[str, Any]],
    cross_layer: Sequence[Mapping[str, Any]],
    curves: Sequence[Mapping[str, Any]],
    costs: Sequence[Mapping[str, Any]],
) -> str:
    lines = [
        "# Generated primary synthesis tables",
        "",
        "Every value below is generated from the exact reviewed aggregates bound by the synthesis manifest.",
        "Cells are never pooled across evidence layers, and a displayed range is not an independent-sample interval.",
        "",
        "## Reviewed evidence inventory",
        "",
        "| Evidence layer | Source | Reviewed aggregate cells | Episode-evidence route |",
        "|---|---|---:|---|",
    ]
    for row in validations:
        lines.append(
            f"| {row['evidence_layer'].title()} | `{row['source_id']}` | "
            f"{row['aggregate_group_count']} | {row['episode_evidence']} |"
        )

    lines.extend(
        [
            "",
            "## Cross-layer findings",
            "",
            "| Evidence slice | Analysis tier | Comparison | Cells | N/cell min–max | Negative / zero / positive medians | Median range | Holm significant | Boundary |",
            "|---|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in cross_layer:
        if row["holm_tested_cells"] == "":
            holm = "not registered"
        else:
            holm = f"{row['holm_significant_cells']} / {row['holm_tested_cells']}"
        lines.append(
            f"| {row['label']} | {row['analysis_tier']} | "
            f"{row['comparison_role'].capitalize()} | {row['cell_count']} | "
            f"{row['sample_count_minimum']}–{row['sample_count_maximum']} | "
            f"{row['negative_median_cells']} / {row['zero_median_cells']} / "
            f"{row['positive_median_cells']} | {_range_percent(row)} | {holm} | "
            f"{row['sampling_boundary']} |"
        )

    lines.extend(
        [
            "",
            "## Gross frictionless safety-factor curve",
            "",
            "This table uses the complete-system comparison. Each row summarizes source aggregate cells within one declared slice and coverage; it does not pool episodes.",
            "",
            "| Evidence slice | Analysis tier | λ | Cells | Median of cell medians | Minimum 5% downside | Worst observed shortfall | Cash drag | Asset exposure | Floor activation | Guardrail floor / deposit | Purchases | Mean cash / deposits | Mean unit value / deposits |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in curves:
        if row["comparison"] != "corrected_guarded_vs_dca":
            continue
        lines.append(
            f"| {row['label']} | {row['analysis_tier']} | {row['coverage']} | "
            f"{row['cell_count']} | "
            f"{_signed_percent(row['median_of_cell_medians'])} | "
            f"{_signed_percent(row['minimum_cell_downside_0.05'])} | "
            f"{_unsigned_percent(row['maximum_worst_observed_relative_shortfall'])} | "
            f"{_unsigned_percent(row['median_left_cash_drag'])} | "
            f"{_unsigned_percent(row['median_left_asset_exposure'])} | "
            f"{_unsigned_percent(row['median_left_guardrail_activation_frequency'])} | "
            f"{_unsigned_percent(row['median_left_guardrail_floor_per_deposit'])} | "
            f"{Decimal(row['median_left_purchase_count']):.1f} | "
            f"{_signed_percent(row['mean_cash_contribution_per_contributed_capital'])} | "
            f"{_signed_percent(row['mean_unit_contribution_per_contributed_capital'])} |"
        )

    lines.extend(
        [
            "",
            "## Net-of-cost empirical robustness",
            "",
            "These rows are visually and inferentially separate from gross frictionless safety. Every row is outside the current epsilon-DCA theorem and has no confirmatory test.",
            "",
            "| Evidence source | Analysis/design slice | Cost route | Comparison | Cells | Negative / zero / positive medians | Median range | Worst observed shortfall |",
            "|---|---|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in costs:
        if row["comparison"] != "corrected_guarded_vs_dca":
            continue
        tier_label = str(row["analysis_tier"])
        if row["design_tier"]:
            tier_label += f" / {row['design_tier']}"
        if row["schedule_id"]:
            tier_label += f" / {row['schedule_id']}"
        lines.append(
            f"| `{row['source_id']}` | {tier_label} | "
            f"{row['cost_scenario']} | "
            f"{row['comparison_role'].capitalize()} | {row['cell_count']} | "
            f"{row['negative_median_cells']} / {row['zero_median_cells']} / "
            f"{row['positive_median_cells']} | {_range_percent(row)} | "
            f"{_unsigned_percent(row['maximum_worst_observed_relative_shortfall'])} |"
        )

    lines.extend(
        [
            "",
            "## Analysis-tier boundary",
            "",
            "| Tier | Permitted interpretation |",
            "|---|---|",
            "| Confirmatory H1/H2 | Historical primary frictionless non-unit cells only; dependence-aware block bootstrap and the sealed 36-test Holm family apply. |",
            "| Secondary | Lambda-one collapse, safety-architecture, mechanisms, exposure, downside, cash/unit attribution, and purchases are descriptive. |",
            "| Registered robustness | Additional historical coverage, quarterly horizons, and all cost rows are descriptive and do not enter H1/H2. |",
            "| Controlled stochastic primary | Baseline stochastic families are finite sensitivity evidence over three saved seeds, not population estimates. |",
            "| Exploratory | Explicit stochastic sensitivity configurations and the deterministic design iteration remain hypothesis-generating; no historical exploratory regime result was run. |",
            "",
        ]
    )
    return "\n".join(lines)


SERIES_COLORS = (
    "#005f73",
    "#ca6702",
    "#6a4c93",
    "#2a9d8f",
    "#bb3e03",
    "#3a86ff",
    "#8338ec",
    "#8d6e63",
)


def _svg_chart(
    title: str,
    subtitle: str,
    rows: Sequence[Mapping[str, Any]],
    panels: Sequence[tuple[str, str, bool]],
    *,
    comparison: str | None = None,
) -> str:
    selected = [row for row in rows if comparison is None or row.get("comparison") == comparison]
    series_ids = list(
        dict.fromkeys(
            (str(row["slice_id"]), str(row["analysis_tier"]))
            for row in selected
        )
    )
    width = 1280
    panel_height = 280
    height = 150 + panel_height * len(panels) + 90
    left = 105
    right = 40
    plot_width = width - left - right
    output = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        f"<title>{html.escape(title)}</title>",
        f"<desc>{html.escape(subtitle)}</desc>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="40" y="42" font-family="sans-serif" font-size="26" font-weight="700">{html.escape(title)}</text>',
        f'<text x="40" y="70" font-family="sans-serif" font-size="14" fill="#444">{html.escape(subtitle)}</text>',
    ]
    legend_y = 102
    for index, series_id in enumerate(series_ids):
        x = 45 + (index % 3) * 405
        y = legend_y + (index // 3) * 22
        color = SERIES_COLORS[index % len(SERIES_COLORS)]
        label = next(
            f"{row['label']} — {row['analysis_tier']}"
            for row in selected
            if (str(row["slice_id"]), str(row["analysis_tier"])) == series_id
        )
        output.extend(
            [
                f'<line x1="{x}" y1="{y - 5}" x2="{x + 24}" y2="{y - 5}" stroke="{color}" stroke-width="3"/>',
                f'<text x="{x + 31}" y="{y}" font-family="sans-serif" font-size="12">{html.escape(label)}</text>',
            ]
        )
    top = 140 + ((len(series_ids) - 1) // 3) * 22
    for panel_index, (panel_label, metric, percent) in enumerate(panels):
        panel_rows = [row for row in selected if row.get(metric) not in (None, "")]
        values = [Decimal(str(row[metric])) for row in panel_rows]
        if percent:
            values = [value * Decimal(100) for value in values]
        low = min(values)
        high = max(values)
        if low == high:
            low -= Decimal(1)
            high += Decimal(1)
        padding = (high - low) * Decimal("0.08")
        low -= padding
        high += padding
        panel_top = top + panel_index * panel_height
        panel_bottom = panel_top + 205
        output.extend(
            [
                f'<text x="40" y="{panel_top + 15}" font-family="sans-serif" font-size="17" font-weight="600">{html.escape(panel_label)}</text>',
                f'<line x1="{left}" y1="{panel_bottom}" x2="{width - right}" y2="{panel_bottom}" stroke="#555"/>',
                f'<line x1="{left}" y1="{panel_top + 30}" x2="{left}" y2="{panel_bottom}" stroke="#555"/>',
                f'<text x="{left - 12}" y="{panel_top + 36}" text-anchor="end" font-family="monospace" font-size="11">{high:.2f}{"%" if percent else ""}</text>',
                f'<text x="{left - 12}" y="{panel_bottom}" text-anchor="end" font-family="monospace" font-size="11">{low:.2f}{"%" if percent else ""}</text>',
            ]
        )
        for tick in (Decimal("0.25"), Decimal("0.5"), Decimal("0.75"), Decimal("1")):
            x = left + float((tick - Decimal("0.25")) / Decimal("0.75")) * plot_width
            output.extend(
                [
                    f'<line x1="{x:.2f}" y1="{panel_bottom}" x2="{x:.2f}" y2="{panel_bottom + 5}" stroke="#555"/>',
                    f'<text x="{x:.2f}" y="{panel_bottom + 20}" text-anchor="middle" font-family="monospace" font-size="11">{tick}</text>',
                ]
            )
        output.append(
            f'<text x="{left + plot_width / 2:.2f}" y="{panel_bottom + 42}" text-anchor="middle" font-family="sans-serif" font-size="12">Safety factor λ</text>'
        )
        for series_index, series_id in enumerate(series_ids):
            series = sorted(
                [
                    row
                    for row in panel_rows
                    if (str(row["slice_id"]), str(row["analysis_tier"]))
                    == series_id
                ],
                key=lambda row: Decimal(str(row["coverage"])),
            )
            points = []
            for row in series:
                x_value = Decimal(str(row["coverage"]))
                y_value = Decimal(str(row[metric])) * (Decimal(100) if percent else Decimal(1))
                x = left + float((x_value - Decimal("0.25")) / Decimal("0.75")) * plot_width
                y = panel_bottom - float((y_value - low) / (high - low)) * (panel_bottom - panel_top - 30)
                points.append((x, y))
            if not points:
                continue
            color = SERIES_COLORS[series_index % len(SERIES_COLORS)]
            output.append(
                f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in points)}" fill="none" stroke="{color}" stroke-width="2.5"/>'
            )
            for x, y in points:
                output.append(
                    f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" fill="{color}"/>'
                )
    output.append(
        f'<text x="40" y="{height - 28}" font-family="sans-serif" font-size="12" fill="#444">Generated from reviewed aggregate cells. Lines connect descriptive summaries; they are not cross-layer estimates or independent-sample intervals.</text>'
    )
    output.append("</svg>")
    return "\n".join(output) + "\n"


def _render_net_cost_svg(costs: Sequence[Mapping[str, Any]]) -> str:
    rows = [row for row in costs if row["comparison"] == "corrected_guarded_vs_dca"]
    width = 1680
    height = 185 + 38 * len(rows)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<title>Net-of-cost empirical robustness: corrected guarded vs DCA</title>",
        "<desc>Cost-adjusted complete-system corrected-guarded-versus-DCA median ranges, outside current safety theorem.</desc>",
        '<rect width="100%" height="100%" fill="#fff7ed"/>',
        '<text x="38" y="40" font-family="sans-serif" font-size="26" font-weight="700">Net-of-cost empirical robustness: corrected guarded vs DCA</text>',
        '<text x="38" y="68" font-family="sans-serif" font-size="14">Complete-system comparison; all rows are outside current safety theorem and have no confirmatory inference.</text>',
        '<text x="38" y="105" font-family="sans-serif" font-size="13" font-weight="700">Reviewed source</text>',
        '<text x="490" y="105" font-family="sans-serif" font-size="13" font-weight="700">Tier / design</text>',
        '<text x="690" y="105" font-family="sans-serif" font-size="13" font-weight="700">Schedule</text>',
        '<text x="1040" y="105" font-family="sans-serif" font-size="13" font-weight="700">Cost</text>',
        '<text x="1230" y="105" font-family="sans-serif" font-size="13" font-weight="700">Median range</text>',
        '<text x="1480" y="105" font-family="sans-serif" font-size="13" font-weight="700">Neg / zero / pos</text>',
    ]
    for index, row in enumerate(rows):
        y = 140 + 38 * index
        lines.extend(
            [
                f'<text x="38" y="{y}" font-family="monospace" font-size="12">{html.escape(str(row["source_id"]))}</text>',
                f'<text x="490" y="{y}" font-family="sans-serif" font-size="11">{html.escape(str(row["analysis_tier"]) + (" / " + str(row["design_tier"]) if row["design_tier"] else ""))}</text>',
                f'<text x="690" y="{y}" font-family="monospace" font-size="11">{html.escape(str(row["schedule_id"]) if row["schedule_id"] else "not-applicable")}</text>',
                f'<text x="1040" y="{y}" font-family="sans-serif" font-size="12">{html.escape(str(row["cost_scenario"]))}</text>',
                f'<text x="1230" y="{y}" font-family="monospace" font-size="12">{html.escape(_range_percent(row))}</text>',
                f'<text x="1480" y="{y}" font-family="monospace" font-size="12">{row["negative_median_cells"]} / {row["zero_median_cells"]} / {row["positive_median_cells"]}</text>',
            ]
        )
    lines.append(
        f'<text x="38" y="{height - 22}" font-family="sans-serif" font-size="12" fill="#444">Negative / zero / positive counts describe source aggregate-cell medians; they are not pooled episode frequencies or inferential counts.</text>'
    )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def _load_uncertainty_rows(
    root: Path, source: Mapping[str, Any]
) -> list[dict[str, Any]]:
    if "uncertainty_path" not in source:
        return []
    _, payload = _verified_bytes(
        root,
        source["uncertainty_path"],
        source["uncertainty_sha256"],
        f"{source['source_id']}.uncertainty",
    )
    document = _document(payload, f"{source['source_id']}.uncertainty")
    cells = document.get("cells")
    _require(isinstance(cells, list), "uncertainty.cells", "must be an array")
    return cells


def _claim_receipts(
    cross_layer: Sequence[Mapping[str, Any]],
    normalized_rows: Sequence[Mapping[str, Any]],
    uncertainty_rows: Sequence[Mapping[str, Any]],
    boundaries: Any,
) -> dict[str, Any]:
    lambda_one_rows = [
        row for row in normalized_rows if Decimal(str(row["coverage"])) == Decimal(1)
    ]
    nonzero_lambda_one = sum(
        Decimal(str(row["median_relative_terminal_wealth_gap"])) != 0
        or Decimal(str(row["mean_relative_terminal_wealth_gap"])) != 0
        for row in lambda_one_rows
    )
    floor_rows = [
        row
        for row in normalized_rows
        if row["cost_scenario"] == "frictionless"
        and row["comparison"]
        in {"corrected_guarded_vs_dca", "neutral_guarded_vs_dca"}
    ]
    floor_violations = [
        row
        for row in floor_rows
        if Decimal(str(row["minimum_relative_terminal_wealth_gap"]))
        < Decimal(str(row["coverage"])) - Decimal(1) - Decimal("1e-45")
    ]
    h1 = [row for row in uncertainty_rows if row.get("hypothesis_id") == "H1-complete-system"]
    h2 = [row for row in uncertainty_rows if row.get("hypothesis_id") == "H2-signal-contribution"]
    significance = lambda rows: sum(
        Decimal(str(row["holm_adjusted_p_value"])) < Decimal("0.05") for row in rows
    )

    indexed = {(row["slice_id"], row["comparison"]): row for row in cross_layer}
    historical_h1 = indexed[("historical-confirmatory-nonunit", "corrected_guarded_vs_dca")]
    historical_h2 = indexed[
        ("historical-confirmatory-nonunit", "corrected_guarded_vs_neutral_guarded")
    ]
    architecture = indexed[("historical-confirmatory-nonunit", "neutral_guarded_vs_dca")]
    stochastic = indexed[("stochastic-primary-60m-lambda-075", "corrected_guarded_vs_dca")]
    deterministic = indexed[("deterministic-primary-lambda-075", "corrected_guarded_vs_dca")]
    return {
        "schema_version": "smartdca-synthesis-claim-receipts/1",
        "lambda_one": {
            "aggregate_cell_count": len(lambda_one_rows),
            "nonzero_gap_cells": nonzero_lambda_one,
            "interpretation": "aggregate receipt for the source-validated transaction-level DCA collapse",
        },
        "frictionless_relative_wealth_floor": {
            "audited_cell_count": len(floor_rows),
            "violation_count": len(floor_violations),
            "interpretation": "finite aggregate audit of the proved epsilon-DCA floor; not a new proof",
        },
        "historical_inference": {
            "holm_family_size": len(uncertainty_rows),
            "h1_significant_cells": significance(h1),
            "h2_significant_cells": significance(h2),
            "method": "registered circular moving-block bootstrap with one 36-test H1/H2 Holm family",
            "dependence_boundary": "overlapping monthly windows; no independent-sample interpretation",
        },
        "complete_system": {
            "historical_negative_median_cells": historical_h1["negative_median_cells"],
            "historical_cell_count": historical_h1["cell_count"],
            "stochastic_negative_median_families": stochastic["negative_median_cells"],
            "stochastic_positive_median_families": stochastic["positive_median_cells"],
            "deterministic_negative_median_paths": deterministic["negative_median_cells"],
            "deterministic_positive_median_paths": deterministic["positive_median_cells"],
            "conclusion": "The complete system is path-sensitive in deterministic and controlled stochastic evidence; its median relative-wealth gap was negative in all 18 non-unit primary frictionless historical cells.",
        },
        "corrected_mean_signal": {
            "historical_negative_median_cells": historical_h2["negative_median_cells"],
            "historical_positive_median_cells": historical_h2["positive_median_cells"],
            "historical_holm_significant_cells": historical_h2["holm_significant_cells"],
            "conclusion": "The corrected-mean selector has parameter- and path-sensitive finite effects, but no multiplicity-adjusted H2 evidence of incremental historical value in the sealed run.",
        },
        "safety_architecture": {
            "historical_negative_median_cells": architecture["negative_median_cells"],
            "historical_cell_count": architecture["cell_count"],
            "inference_status": architecture["inference_status"],
            "conclusion": "The guardrail supplies the model-free floor; the neutral architecture's median relative-wealth gap was negative in all 18 non-unit primary frictionless historical cells, a descriptive secondary result.",
        },
        "central_thesis_conclusion": (
            "In the project's causal, long-only, buy-only, fully funded, same-deposit, cash-inclusive comparison model, universal dominance over every finite positive price path forces DCA itself. "
            "The sharp epsilon-DCA unit guardrail preserves a chosen relative-wealth floor and creates a funded discretionary interval, while the terminal-inventory boundary shows that realized adaptive performance is fixed by terminal cash and units. "
            "The reviewed empirical layers find no universal, optimal, or confirmed incremental superiority for the corrected-mean signal."
        ),
        "interpretation_boundaries": boundaries,
    }


def _maximum_additive_residual(
    rows: Sequence[Mapping[str, Any]],
    left_field: str,
    right_field: str,
    total_field: str,
) -> Decimal:
    residuals = [
        abs(
            Decimal(str(row[left_field]))
            + Decimal(str(row[right_field]))
            - Decimal(str(row[total_field]))
        )
        for row in rows
    ]
    return max(residuals, default=Decimal(0))


def _source_sha256() -> str:
    return _sha256(Path(__file__).read_bytes())


def _runtime_identity() -> dict[str, str]:
    implementation = platform.python_implementation()
    version_components = platform.python_version().split(".")
    _require(bool(implementation), "runtime.implementation", "must be nonempty")
    _require(
        len(version_components) >= 2
        and all(component.isdigit() for component in version_components[:2]),
        "runtime.python",
        "must begin with a numeric major.minor version",
    )
    return {
        "implementation": implementation,
        "python": ".".join(version_components[:2]),
    }


def _run_id(
    specification_sha256: str,
    source_sha256: str,
    runtime_identity: Mapping[str, str],
) -> str:
    identity = {
        "engine_version": ENGINE_VERSION,
        "runtime": runtime_identity,
        "source_sha256": source_sha256,
        "specification_sha256": specification_sha256,
    }
    return "smartdca-synthesis-v1-" + _sha256(_canonical_json(identity).encode("utf-8"))


def run_synthesis(
    synthesis_path: Path,
    output_root: Path,
    *,
    repository_root: Path | None = None,
) -> SynthesisBundle:
    """Validate reviewed sources and emit one immutable synthesis bundle."""

    root = (repository_root or Path(__file__).resolve().parents[1]).resolve()
    synthesis_path = synthesis_path.resolve()
    _require(synthesis_path.is_file(), "synthesis_path", "does not exist")
    specification_payload = synthesis_path.read_bytes()
    specification = _document(specification_payload, "synthesis")
    _require(
        specification.get("schema_version") == SCHEMA_VERSION,
        "synthesis.schema_version",
        f"must equal {SCHEMA_VERSION}",
    )
    comparison_roles = specification.get("comparison_roles")
    cost_scopes = specification.get("cost_scopes")
    _require(isinstance(comparison_roles, dict), "comparison_roles", "must be an object")
    _require(isinstance(cost_scopes, dict), "cost_scopes", "must be an object")
    reviewed_sources = specification.get("reviewed_sources")
    _require(
        isinstance(reviewed_sources, list) and reviewed_sources,
        "reviewed_sources",
        "must be a nonempty array",
    )
    source_ids = [source.get("source_id") for source in reviewed_sources if isinstance(source, dict)]
    _require(
        len(source_ids) == len(reviewed_sources) == len(set(source_ids)),
        "reviewed_sources",
        "must contain unique source IDs",
    )

    validations: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    rows_by_source: dict[str, list[dict[str, Any]]] = {}
    uncertainty_by_source: dict[str, list[dict[str, Any]]] = {}
    for source in reviewed_sources:
        _require(isinstance(source, dict), "reviewed_sources", "entries must be objects")
        validation, rows = _validate_source(root, source, comparison_roles, cost_scopes)
        validations.append(validation)
        normalized_rows.extend(rows)
        rows_by_source[source["source_id"]] = rows
        uncertainty_by_source[source["source_id"]] = _load_uncertainty_rows(
            root, source
        )
    theory_receipts = _validate_theory_sources(root, specification.get("theory_sources"))
    cross_layer = _cross_layer_summaries(
        specification, rows_by_source, uncertainty_by_source
    )
    curves = _curve_summaries(specification, rows_by_source)
    costs = _cost_summaries(normalized_rows)
    uncertainty_rows = [
        row for rows in uncertainty_by_source.values() for row in rows
    ]
    claims = _claim_receipts(
        cross_layer,
        normalized_rows,
        uncertainty_rows,
        specification.get("interpretation_boundaries"),
    )

    specification_sha256 = _sha256(specification_payload)
    source_sha256 = _source_sha256()
    runtime_identity = _runtime_identity()
    synthesis_run_id = _run_id(
        specification_sha256,
        source_sha256,
        runtime_identity,
    )
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    output_directory = output_root / synthesis_run_id
    if output_directory.exists():
        raise SynthesisIdentityCollisionError(
            f"synthesis output identity already exists: {output_directory}"
        )

    temporary_directory = Path(tempfile.mkdtemp(prefix=".smartdca-synthesis-", dir=output_root))
    try:
        source_validation = {
            "schema_version": "smartdca-synthesis-source-validation/1",
            "reviewed_source_count": len(validations),
            "rejected_source_count": 0,
            "normalized_group_count": len(normalized_rows),
            "sources": validations,
            "theory_sources": theory_receipts,
        }
        _write_json(temporary_directory / "source-validation.json", source_validation)
        _write_csv(
            temporary_directory / "normalized-evidence.csv",
            normalized_rows,
            NORMALIZED_FIELDS,
        )
        _write_csv(
            temporary_directory / "cross-layer-summary.csv",
            cross_layer,
            CROSS_LAYER_FIELDS,
        )
        _write_csv(
            temporary_directory / "safety-factor-curve.csv",
            curves,
            CURVE_FIELDS,
        )
        _write_csv(
            temporary_directory / "cost-scope-summary.csv",
            costs,
            COST_FIELDS,
        )
        _write_json(temporary_directory / "claim-receipts.json", claims)
        (temporary_directory / "primary-tables.md").write_text(
            _render_primary_tables(validations, cross_layer, curves, costs),
            encoding="utf-8",
            newline="\n",
        )
        (temporary_directory / "frictionless-safety-factor.svg").write_text(
            _svg_chart(
                "Gross frictionless safety-factor curve",
                "Complete-system descriptive summaries from reviewed aggregate cells; no cross-layer pooling.",
                curves,
                (
                    ("Median of cell median relative-wealth gaps", "median_of_cell_medians", True),
                    ("Minimum cell 5% downside", "minimum_cell_downside_0.05", True),
                    (
                        "Maximum observed relative shortfall",
                        "maximum_worst_observed_relative_shortfall",
                        True,
                    ),
                ),
                comparison="corrected_guarded_vs_dca",
            ),
            encoding="utf-8",
            newline="\n",
        )
        (temporary_directory / "mechanism-curves.svg").write_text(
            _svg_chart(
                "Frictionless safety-factor mechanism curves",
                "Corrected guarded policy cash drag, exposure, floor activation frequency and size, and purchase activity.",
                curves,
                (
                    ("Median terminal cash drag", "median_left_cash_drag", True),
                    ("Median terminal asset exposure", "median_left_asset_exposure", True),
                    (
                        "Median guardrail activation frequency",
                        "median_left_guardrail_activation_frequency",
                        True,
                    ),
                    (
                        "Median guardrail floor share of deposit",
                        "median_left_guardrail_floor_per_deposit",
                        True,
                    ),
                    ("Median purchase count", "median_left_purchase_count", False),
                ),
                comparison="corrected_guarded_vs_dca",
            ),
            encoding="utf-8",
            newline="\n",
        )
        (temporary_directory / "terminal-attribution.svg").write_text(
            _svg_chart(
                "Complete-system terminal cash and unit attribution",
                "Corrected guarded vs DCA: mean ledger-conditioned cash and evaluation-price unit contribution as a share of contributed capital.",
                curves,
                (
                    (
                        "Mean cash contribution share of contributed capital",
                        "mean_cash_contribution_per_contributed_capital",
                        True,
                    ),
                    (
                        "Mean unit-value contribution share of contributed capital",
                        "mean_unit_contribution_per_contributed_capital",
                        True,
                    ),
                ),
                comparison="corrected_guarded_vs_dca",
            ),
            encoding="utf-8",
            newline="\n",
        )
        (temporary_directory / "net-cost-summary.svg").write_text(
            _render_net_cost_svg(costs),
            encoding="utf-8",
            newline="\n",
        )
        summary_reconciliation = {
            "schema_version": "smartdca-synthesis-summary-reconciliation/1",
            "normalized_source_group_count": len(normalized_rows),
            "source_group_count_sum": sum(
                row["aggregate_group_count"] for row in validations
            ),
            "cross_layer_summary_count": len(cross_layer),
            "safety_factor_curve_count": len(curves),
            "cost_scope_summary_count": len(costs),
            "cash_unit_maximum_absolute_residual": str(
                _maximum_additive_residual(
                    normalized_rows,
                    "mean_cash_contribution",
                    "mean_unit_contribution",
                    "mean_terminal_wealth_gap",
                )
            ),
            "normalized_cash_unit_maximum_absolute_residual": str(
                _maximum_additive_residual(
                    normalized_rows,
                    "mean_cash_contribution_per_contributed_capital",
                    "mean_unit_contribution_per_contributed_capital",
                    "mean_terminal_wealth_gap_per_contributed_capital",
                )
            ),
            "primary_tables_source": [
                "cross-layer-summary.csv",
                "safety-factor-curve.csv",
                "cost-scope-summary.csv",
            ],
            "manual_numeric_transcription": False,
            "cross_layer_pooling": False,
        }
        _write_json(
            temporary_directory / "summary-reconciliation.json",
            summary_reconciliation,
        )

        artifacts = []
        for path in sorted(temporary_directory.iterdir(), key=lambda item: item.name):
            payload = path.read_bytes()
            artifacts.append(
                {"path": path.name, "bytes": len(payload), "sha256": _sha256(payload)}
            )
        manifest: dict[str, Any] = {
            "schema_version": OUTPUT_SCHEMA_VERSION,
            "synthesis_run_id": synthesis_run_id,
            "synthesis_id": specification.get("synthesis_id"),
            "engine_version": ENGINE_VERSION,
            "source_sha256": source_sha256,
            "specification_path": synthesis_path.relative_to(root).as_posix(),
            "specification_sha256": specification_sha256,
            "reviewed_source_run_ids": [row["run_id"] for row in validations],
            "normalized_group_count": len(normalized_rows),
            "summary_counts": {
                "cross_layer": len(cross_layer),
                "safety_factor_curve": len(curves),
                "cost_scope": len(costs),
            },
            "artifacts": artifacts,
            "runtime": {**runtime_identity, "third_party_dependencies": []},
            "reproduction": {
                "module": "reproducibility.safety_adaptivity_synthesis",
                "arguments": [
                    "--manifest",
                    synthesis_path.relative_to(root).as_posix(),
                    "--output-root",
                    "<new-empty-output-root>",
                ],
            },
        }
        _write_json(temporary_directory / "manifest.json", manifest)
        os.replace(temporary_directory, output_directory)
    except Exception:
        shutil.rmtree(temporary_directory, ignore_errors=True)
        raise

    return SynthesisBundle(
        synthesis_run_id=synthesis_run_id,
        output_directory=output_directory,
        manifest=manifest,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the reviewed cross-layer safety-adaptivity synthesis."
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    arguments = parser.parse_args(argv)
    bundle = run_synthesis(arguments.manifest, arguments.output_root)
    print(
        _canonical_json(
            {
                "synthesis_run_id": bundle.synthesis_run_id,
                "manifest": str((bundle.output_directory / "manifest.json").resolve()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
