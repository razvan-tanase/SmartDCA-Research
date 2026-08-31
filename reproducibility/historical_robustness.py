"""Execute the registered post-confirmatory historical robustness extensions."""

from __future__ import annotations

import argparse
import bisect
import csv
import gc
import hashlib
import json
import os
import shutil
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from reproducibility import historical_study as confirmatory_study
from reproducibility.empirical import (
    ExperimentValidationError,
    RunIdentityCollisionError,
    StudyConfig,
    VersionedInput,
    run_experiment,
)
from reproducibility.historical_data import MAPPING_TOLERANCE_DAYS


ENGINE_VERSION = "smartdca-historical-robustness/1"
PLAN_SCHEMA = "smartdca-historical-robustness-execution/1"
ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DERIVED_ARTIFACTS = {
    "private-artifact-receipt.json",
    "report-tables.md",
    "robustness-aggregates.json",
    "robustness-figure-ready.csv",
    "study-validation.json",
}
ZERO = Decimal("0")


def _require(condition: bool, code: str, field: str, message: str) -> None:
    if not condition:
        raise ExperimentValidationError(code, field, message)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _fingerprint(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _repository_relative(path: Path, field: str) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError as error:
        raise ExperimentValidationError(
            "path_outside_repository", field, "must resolve below the repository root"
        ) from error


def _read_bytes(path: Path, field: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as error:
        raise ExperimentValidationError("unreadable_artifact", field, str(error)) from error


def _decode_document(payload: bytes, field: str) -> dict[str, Any]:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ExperimentValidationError(
            "invalid_encoding", field, "must be UTF-8"
        ) from error

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON constant: {value}")

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate key: {key}")
            result[key] = value
        return result

    try:
        value = json.loads(
            text,
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (json.JSONDecodeError, ValueError) as error:
        raise ExperimentValidationError(
            "invalid_json", field, "must be one duplicate-free finite JSON document"
        ) from error
    _require(isinstance(value, dict), "invalid_type", field, "must be a JSON object")
    return value


def _write_json(path: Path, value: Any) -> None:
    path.write_text(_canonical_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: tuple[Mapping[str, Any], ...]) -> None:
    path.write_text(
        "".join(_canonical_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def _write_csv(path: Path, rows: list[Mapping[str, Any]]) -> None:
    _require(bool(rows), "empty_output", str(path), "must have at least one row")
    fields = list(rows[0])
    _require(
        all(list(row) == fields for row in rows),
        "inconsistent_output_schema",
        str(path),
        "all rows must use one ordered field schema",
    )
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _add_months(value: date, months: int) -> date:
    month_index = value.year * 12 + value.month - 1 + months
    return date(month_index // 12, month_index % 12 + 1, value.day)


def _utc_datetime(value: Any, field: str) -> datetime:
    _require(isinstance(value, str), "invalid_datetime", field, "must be ISO text")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ExperimentValidationError(
            "invalid_datetime", field, "must be an ISO 8601 datetime"
        ) from error
    _require(
        parsed.tzinfo is not None
        and parsed.utcoffset() == timezone.utc.utcoffset(parsed),
        "invalid_datetime",
        field,
        "must carry the UTC offset",
    )
    return parsed


@dataclass(frozen=True)
class RegisteredRobustnessExecution:
    """Exact post-outcome projection of fields frozen in the parent protocol."""

    document: Mapping[str, Any]
    sha256: str
    protocol: Mapping[str, Any]
    protocol_sha256: str


def load_registered_robustness_execution(
    plan_path: Path,
    protocol_path: Path,
    accepted_manifest_path: Path,
) -> RegisteredRobustnessExecution:
    """Load the execution plan and prove every analysis choice comes from its parent."""

    plan_payload = _read_bytes(plan_path, "execution_plan")
    plan = _decode_document(plan_payload, "execution_plan")
    protocol_payload = _read_bytes(protocol_path, "protocol")
    protocol = _decode_document(protocol_payload, "protocol")
    accepted_payload = _read_bytes(accepted_manifest_path, "accepted_manifest")
    protocol_sha = _fingerprint(protocol_payload)
    plan_sha = _fingerprint(plan_payload)

    _require(
        plan.get("schema_version") == PLAN_SCHEMA,
        "unsupported_schema",
        "execution_plan.schema_version",
        f"must equal {PLAN_SCHEMA}",
    )
    _require(plan.get("locked") is True, "unlocked_plan", "execution_plan.locked", "must be true")
    _require(
        plan.get("created_after_confirmatory_outcome_access") is True,
        "invalid_analysis_boundary",
        "execution_plan.created_after_confirmatory_outcome_access",
        "must disclose post-confirmatory construction",
    )
    created_at = _utc_datetime(plan.get("created_at"), "execution_plan.created_at")
    registered_at = _utc_datetime(protocol.get("registered_at"), "protocol.registered_at")
    _require(
        created_at > registered_at,
        "invalid_analysis_boundary",
        "execution_plan.created_at",
        "must follow the parent protocol registration",
    )
    parent = plan.get("parent_protocol")
    _require(isinstance(parent, dict), "invalid_type", "execution_plan.parent_protocol", "must be a mapping")
    _require(
        parent
        == {
            "path": _repository_relative(protocol_path, "protocol_path"),
            "protocol_id": protocol.get("protocol_id"),
            "sha256": protocol_sha,
        },
        "protocol_fingerprint_mismatch",
        "execution_plan.parent_protocol",
        "must bind the exact parent protocol path, ID, and bytes",
    )
    _require(
        protocol.get("locked") is True
        and protocol.get("confirmatory_outcomes_accessed") is False,
        "invalid_parent_protocol",
        "protocol",
        "must preserve the locked registration-time state",
    )
    accepted = plan.get("accepted_preparation")
    _require(
        isinstance(accepted, dict),
        "invalid_type",
        "execution_plan.accepted_preparation",
        "must be a mapping",
    )
    accepted_manifest = _decode_document(accepted_payload, "accepted_manifest")
    _require(
        accepted.get("manifest_path")
        == _repository_relative(accepted_manifest_path, "accepted_manifest_path")
        and accepted.get("manifest_sha256") == _fingerprint(accepted_payload)
        and accepted.get("run_id") == accepted_manifest.get("run_id")
        and accepted.get("runner_input_sha256")
        == accepted_manifest.get("runner_input_sha256"),
        "preparation_fingerprint_mismatch",
        "execution_plan.accepted_preparation",
        "must bind the exact accepted preparation",
    )

    primary_mean_ids = [
        value["config_id"] for value in protocol["corrected_mean"]["primary"]
    ]
    robustness_mean_ids = [
        value["config_id"] for value in protocol["corrected_mean"]["robustness"]
    ]
    cost_ids = [value["cost_id"] for value in protocol["cost_scenarios"]]
    shared = plan.get("shared_grid")
    _require(isinstance(shared, dict), "invalid_type", "execution_plan.shared_grid", "must be a mapping")
    _require(
        shared.get("corrected_mean_configurations") == primary_mean_ids
        and shared.get("cost_scenarios") == cost_ids
        and shared.get("policies")
        == ["dca", "neutral_guarded", "corrected_guarded"]
        and shared.get("comparisons")
        == [
            "corrected_guarded_vs_dca",
            "corrected_guarded_vs_neutral_guarded",
            "neutral_guarded_vs_dca",
        ],
        "grid_projection_mismatch",
        "execution_plan.shared_grid",
        "must use the registered primary policy and cost grid",
    )

    monthly = plan.get("monthly_coverage_extension")
    quarterly = plan.get("quarterly_horizon_extension")
    _require(isinstance(monthly, dict), "invalid_type", "execution_plan.monthly_coverage_extension", "must be a mapping")
    _require(isinstance(quarterly, dict), "invalid_type", "execution_plan.quarterly_horizon_extension", "must be a mapping")
    primary_coverage = protocol["coverage"]["primary"]
    robustness_coverage = protocol["coverage"]["robustness"]
    _require(
        monthly.get("design_tier") == "primary"
        and monthly.get("deposit_interval_months") == 1
        and monthly.get("rolling_stride_months")
        == protocol["episode_design"]["rolling_stride_months"]
        and monthly.get("horizons_months")
        == protocol["episode_design"]["horizons_months"]
        and monthly.get("coverage") == robustness_coverage
        and monthly.get("runner_compatibility_coverage")
        == ["1", *robustness_coverage],
        "grid_projection_mismatch",
        "execution_plan.monthly_coverage_extension",
        "must project primary episodes over every registered robustness coverage",
    )
    combined_coverage = list(dict.fromkeys([*primary_coverage, *robustness_coverage]))
    _require(
        quarterly.get("design_tier") == "robustness"
        and quarterly.get("deposit_interval_months") == 3
        and quarterly.get("rolling_stride_months")
        == protocol["robustness_design"]["rolling_stride_months"]
        and quarterly.get("horizons_months")
        == protocol["robustness_design"]["horizons_months"]
        and quarterly.get("coverage") == combined_coverage
        and all(value % 3 == 0 for value in quarterly["horizons_months"]),
        "grid_projection_mismatch",
        "execution_plan.quarterly_horizon_extension",
        "must project every registered coverage over the quarterly robustness design",
    )
    analysis = plan.get("analysis")
    _require(
        isinstance(analysis, dict)
        and analysis.get("tier") == "robustness"
        and analysis.get("confirmatory_family_change") == "none"
        and str(analysis.get("uncertainty", "")).startswith("descriptive-only"),
        "invalid_analysis_boundary",
        "execution_plan.analysis",
        "must prohibit confirmatory inference",
    )
    deferred = plan.get("registered_but_not_required_here")
    _require(
        isinstance(deferred, dict)
        and deferred.get("corrected_mean_robustness_configurations")
        == robustness_mean_ids,
        "grid_projection_mismatch",
        "execution_plan.registered_but_not_required_here",
        "must inventory every non-primary corrected-mean configuration",
    )
    return RegisteredRobustnessExecution(plan, plan_sha, protocol, protocol_sha)


@dataclass(frozen=True)
class NormalizedSeries:
    """Sorted normalized observations with explicit calendar lookup methods."""

    rows: tuple[Mapping[str, Any], ...]
    dates: tuple[date, ...]

    @classmethod
    def from_rows(
        cls, rows: list[Mapping[str, Any]], dataset_id: str
    ) -> "NormalizedSeries":
        _require(bool(rows), "empty_dataset", dataset_id, "must contain observations")
        parsed_dates: list[date] = []
        for index, row in enumerate(rows):
            field = f"normalized.{dataset_id}[{index}]"
            try:
                observed = date.fromisoformat(str(row["observation_date"]))
                price = Decimal(str(row["price"]))
            except (KeyError, ValueError) as error:
                raise ExperimentValidationError(
                    "invalid_normalized_observation", field, str(error)
                ) from error
            _require(price > ZERO, "invalid_price", f"{field}.price", "must be positive")
            _require(
                not parsed_dates or observed > parsed_dates[-1],
                "invalid_date_order",
                f"{field}.observation_date",
                "must be strictly increasing",
            )
            parsed_dates.append(observed)
        return cls(tuple(rows), tuple(parsed_dates))

    def first_on_or_after(
        self, nominal: date, tolerance_days: int
    ) -> Mapping[str, Any] | None:
        index = bisect.bisect_left(self.dates, nominal)
        if index == len(self.dates):
            return None
        return (
            self.rows[index]
            if (self.dates[index] - nominal).days <= tolerance_days
            else None
        )

    def last_on_or_before(
        self, nominal: date, tolerance_days: int
    ) -> Mapping[str, Any] | None:
        index = bisect.bisect_right(self.dates, nominal) - 1
        if index < 0:
            return None
        return (
            self.rows[index]
            if (nominal - self.dates[index]).days <= tolerance_days
            else None
        )

    def neighbors(self, nominal: date) -> tuple[str | None, str | None]:
        index = bisect.bisect_left(self.dates, nominal)
        previous = self.dates[index - 1].isoformat() if index else None
        following = self.dates[index].isoformat() if index < len(self.dates) else None
        return previous, following


def build_quarterly_episode_attempt(
    *,
    dataset_id: str,
    series: NormalizedSeries,
    nominal_start: date,
    horizon_months: int,
    deposit_amount: str,
    deposit_interval_months: int = 3,
) -> dict[str, Any]:
    """Build one fully preserved quarterly attempt under registered mappings."""

    _require(
        horizon_months > 0 and horizon_months % deposit_interval_months == 0,
        "invalid_horizon",
        "horizon_months",
        "must be a positive multiple of the deposit interval",
    )
    _require(nominal_start.day == 1, "invalid_nominal_start", "nominal_start", "must be first of month")
    _require(
        dataset_id in MAPPING_TOLERANCE_DAYS,
        "unknown_dataset",
        "dataset_id",
        "must have a registered mapping tolerance",
    )
    tolerance = MAPPING_TOLERANCE_DAYS[dataset_id]
    offsets = tuple(range(0, horizon_months, deposit_interval_months))
    horizon_date = _add_months(nominal_start, horizon_months)
    attempt: dict[str, Any] = {
        "episode_id": (
            f"{dataset_id}-quarterly-{nominal_start.isoformat()}-{horizon_months}m"
        ),
        "dataset_id": dataset_id,
        "schedule_id": "robustness-quarterly-horizons",
        "design_tier": "robustness",
        "nominal_start": nominal_start.isoformat(),
        "horizon_months": horizon_months,
        "horizon_date": horizon_date.isoformat(),
        "deposit_interval_months": deposit_interval_months,
        "deposit_schedule": [
            {
                "nominal_date": _add_months(nominal_start, offset).isoformat(),
                "purchase_date": None,
                "mapping_lag_days": None,
                "source_row": None,
                "price": None,
                "deposit": deposit_amount,
            }
            for offset in offsets
        ],
        "evaluation_date": None,
        "evaluation_price": None,
        "evaluation_source_row": None,
        "status": "excluded",
        "exclusion_reason": None,
        "exclusion_details": None,
    }
    mapped_dates: set[str] = set()
    for index, offset in enumerate(offsets):
        nominal = _add_months(nominal_start, offset)
        row = series.first_on_or_after(nominal, tolerance)
        if row is None:
            if attempt["exclusion_reason"] is None:
                previous, following = series.neighbors(nominal)
                attempt["exclusion_reason"] = "unavailable_mapped_purchase_date"
                attempt["exclusion_details"] = {
                    "mapping": "first-observation-on-or-after",
                    "nominal_date": nominal.isoformat(),
                    "tolerance_days": tolerance,
                    "previous_observation_date": previous,
                    "next_observation_date": following,
                }
            continue
        purchase_date = str(row["observation_date"])
        if purchase_date in mapped_dates and attempt["exclusion_reason"] is None:
            attempt["exclusion_reason"] = "duplicate_mapped_purchase_date"
            attempt["exclusion_details"] = {
                "nominal_date": nominal.isoformat(),
                "duplicate_purchase_date": purchase_date,
            }
        mapped_dates.add(purchase_date)
        attempt["deposit_schedule"][index].update(
            {
                "purchase_date": purchase_date,
                "mapping_lag_days": (
                    date.fromisoformat(purchase_date) - nominal
                ).days,
                "source_row": row["source_row"],
                "price": row["price"],
            }
        )

    evaluation = series.last_on_or_before(horizon_date, tolerance)
    if evaluation is None and attempt["exclusion_reason"] is None:
        previous, following = series.neighbors(horizon_date)
        attempt["exclusion_reason"] = "unavailable_mapped_evaluation_date"
        attempt["exclusion_details"] = {
            "mapping": "last-observation-on-or-before",
            "horizon_date": horizon_date.isoformat(),
            "tolerance_days": tolerance,
            "previous_observation_date": previous,
            "next_observation_date": following,
        }
    elif evaluation is not None:
        attempt.update(
            {
                "evaluation_date": evaluation["observation_date"],
                "evaluation_price": evaluation["price"],
                "evaluation_source_row": evaluation["source_row"],
            }
        )
    if attempt["exclusion_reason"] is None:
        attempt["status"] = "included"
    return attempt


def _runner_episode(
    attempt: Mapping[str, Any], source_identity: str
) -> dict[str, Any]:
    return {
        "episode_id": attempt["episode_id"],
        "family": "historical-recurring-investment-robustness-quarterly",
        "dataset_id": attempt["dataset_id"],
        "horizon_months": attempt["horizon_months"],
        "observations": [
            {
                "date": row["purchase_date"],
                "price": row["price"],
                "deposit": row["deposit"],
            }
            for row in attempt["deposit_schedule"]
        ],
        "evaluation_date": attempt["evaluation_date"],
        "evaluation_price": attempt["evaluation_price"],
        "historical_mapping": {
            "schedule_id": attempt["schedule_id"],
            "design_tier": attempt["design_tier"],
            "nominal_start": attempt["nominal_start"],
            "horizon_date": attempt["horizon_date"],
            "deposit_interval_months": attempt["deposit_interval_months"],
            "dataset_source_identity": source_identity,
            "purchase_mappings": [
                {
                    "nominal_date": row["nominal_date"],
                    "purchase_date": row["purchase_date"],
                    "mapping_lag_days": row["mapping_lag_days"],
                    "source_row": row["source_row"],
                }
                for row in attempt["deposit_schedule"]
            ],
            "evaluation_source_row": attempt["evaluation_source_row"],
        },
    }


def build_quarterly_robustness_input(
    execution: RegisteredRobustnessExecution,
    normalized_document: Mapping[str, Any],
    source_receipts: list[Mapping[str, Any]],
) -> tuple[tuple[Mapping[str, Any], ...], VersionedInput, Mapping[str, Any]]:
    """Construct every registered quarterly rolling episode and exclusion."""

    datasets = normalized_document.get("datasets")
    _require(isinstance(datasets, dict), "invalid_type", "normalized.datasets", "must be a mapping")
    protocol_datasets = {
        value["dataset_id"]: value
        for value in execution.protocol["historical_datasets"]
    }
    _require(
        set(datasets) == set(protocol_datasets),
        "dataset_mismatch",
        "normalized.datasets",
        "must contain exactly the registered datasets",
    )
    series = {
        dataset_id: NormalizedSeries.from_rows(rows, dataset_id)
        for dataset_id, rows in datasets.items()
    }
    design = execution.document["quarterly_horizon_extension"]
    attempts: list[Mapping[str, Any]] = []
    for dataset_id in sorted(protocol_datasets):
        dataset = protocol_datasets[dataset_id]
        eligible = date.fromisoformat(dataset["eligible_start"])
        nominal_start = date(eligible.year, eligible.month, 1)
        if nominal_start < eligible:
            nominal_start = _add_months(nominal_start, 1)
        cutoff = date.fromisoformat(dataset["data_cutoff"])
        for horizon in design["horizons_months"]:
            start = nominal_start
            while _add_months(start, horizon) <= cutoff:
                attempts.append(
                    build_quarterly_episode_attempt(
                        dataset_id=dataset_id,
                        series=series[dataset_id],
                        nominal_start=start,
                        horizon_months=horizon,
                        deposit_amount=str(
                            execution.protocol["episode_design"]["deposit_amount"]
                        ),
                        deposit_interval_months=design["deposit_interval_months"],
                    )
                )
                start = _add_months(start, design["rolling_stride_months"])
    receipt_by_dataset = {
        str(value["dataset_id"]): value for value in source_receipts
    }
    _require(
        set(receipt_by_dataset) == set(protocol_datasets),
        "source_receipt_mismatch",
        "source_receipts",
        "must bind each registered dataset",
    )
    included = [attempt for attempt in attempts if attempt["status"] == "included"]
    _require(bool(included), "empty_input", "quarterly_attempts", "must include at least one episode")
    versioned_input = VersionedInput.from_mapping(
        {
            "schema_version": "smartdca-versioned-input/1",
            "input_id": (
                f"{execution.document['execution_id']}-quarterly-runner-input"
            ),
            "version": execution.document["version"],
            "kind": "historical",
            "confirmatory": False,
            "purpose": execution.document["purpose"],
            "schedule_id": design["schedule_id"],
            "source_receipts": source_receipts,
            "episodes": [
                _runner_episode(
                    attempt,
                    str(
                        receipt_by_dataset[str(attempt["dataset_id"])][
                            "source_identity"
                        ]
                    ),
                )
                for attempt in included
            ],
        }
    )
    reasons = Counter(
        str(attempt["exclusion_reason"])
        for attempt in attempts
        if attempt["status"] == "excluded"
    )
    reconciliation = {
        "schedule_id": design["schedule_id"],
        "source_observation_count": sum(len(value) for value in datasets.values()),
        "attempted_episode_count": len(attempts),
        "included_episode_count": len(included),
        "excluded_episode_count": len(attempts) - len(included),
        "exclusion_reasons": dict(sorted(reasons.items())),
        "runner_input_episode_count": len(included),
    }
    return tuple(attempts), versioned_input, reconciliation


def build_monthly_robustness_input(
    execution: RegisteredRobustnessExecution,
    accepted: confirmatory_study.AcceptedHistoricalPreparation,
) -> tuple[tuple[Mapping[str, Any], ...], VersionedInput, Mapping[str, Any]]:
    """Project accepted primary monthly episodes into a non-confirmatory input."""

    document = accepted.runner_input.as_mapping()
    document.update(
        {
            "input_id": f"{execution.document['execution_id']}-monthly-runner-input",
            "version": execution.document["version"],
            "confirmatory": False,
            "purpose": execution.document["purpose"],
            "schedule_id": execution.document["monthly_coverage_extension"][
                "schedule_id"
            ],
        }
    )
    for episode in document["episodes"]:
        episode["family"] = "historical-recurring-investment-robustness-monthly"
        episode["historical_mapping"]["schedule_id"] = execution.document[
            "monthly_coverage_extension"
        ]["schedule_id"]
        episode["historical_mapping"]["design_tier"] = "primary"
    attempts = tuple(
        {
            **dict(attempt),
            "schedule_id": execution.document["monthly_coverage_extension"][
                "schedule_id"
            ],
            "design_tier": "primary",
        }
        for attempt in accepted.episode_attempts
    )
    reconciliation = {
        "schedule_id": execution.document["monthly_coverage_extension"][
            "schedule_id"
        ],
        "source_observation_count": accepted.reconciliation["observation_count"],
        "attempted_episode_count": accepted.attempt_count,
        "included_episode_count": accepted.reconciliation[
            "included_episode_count"
        ],
        "excluded_episode_count": accepted.reconciliation[
            "excluded_episode_count"
        ],
        "exclusion_reasons": accepted.reconciliation["exclusion_reasons"],
        "runner_input_episode_count": len(document["episodes"]),
    }
    return attempts, VersionedInput.from_mapping(document), reconciliation


@dataclass(frozen=True, order=True)
class HistoricalCellKey:
    """Named identity for one historical aggregate cell."""

    dataset_id: str
    horizon_months: int
    coverage: str
    corrected_mean_config: str
    cost_scenario: str
    comparison: str
    design_tier: str

    @classmethod
    def from_group(
        cls, group: Mapping[str, Any], design_tier: str
    ) -> "HistoricalCellKey":
        return cls(
            dataset_id=str(group["dataset_id"]),
            horizon_months=int(group["horizon_months"]),
            coverage=str(group["coverage"]),
            corrected_mean_config=str(group["corrected_mean_config"]),
            cost_scenario=str(group["cost_scenario"]),
            comparison=str(group["comparison"]),
            design_tier=design_tier,
        )


COMPARISON_METADATA = {
    "corrected_guarded_vs_dca": {
        "hypothesis_id": "H1-complete-system",
        "label": "complete system vs DCA",
        "order": 0,
    },
    "corrected_guarded_vs_neutral_guarded": {
        "hypothesis_id": "H2-signal-contribution",
        "label": "signal only vs neutral guarded",
        "order": 1,
    },
    "neutral_guarded_vs_dca": {
        "hypothesis_id": None,
        "label": "safety architecture vs DCA",
        "order": 2,
    },
}


def classify_analysis_tier(
    key: HistoricalCellKey, protocol: Mapping[str, Any]
) -> str:
    """Classify a cell from every registered analysis axis."""

    _require(
        key.comparison in COMPARISON_METADATA,
        "unknown_comparison",
        "cell.comparison",
        "must be a registered comparison",
    )
    robustness_axis = (
        key.design_tier == "robustness"
        or key.horizon_months in protocol["robustness_design"]["horizons_months"]
        or key.coverage in protocol["coverage"]["robustness"]
        or key.corrected_mean_config
        in {
            value["config_id"]
            for value in protocol["corrected_mean"]["robustness"]
        }
        or key.cost_scenario != "frictionless"
    )
    if robustness_axis:
        return "robustness"
    _require(
        key.design_tier == "primary"
        and key.horizon_months in protocol["episode_design"]["horizons_months"]
        and key.coverage in protocol["coverage"]["primary"]
        and key.corrected_mean_config
        in {
            value["config_id"] for value in protocol["corrected_mean"]["primary"]
        },
        "unregistered_primary_cell",
        "cell",
        "must be primary or carry a registered robustness axis",
    )
    if (
        key.coverage == "1"
        or COMPARISON_METADATA[key.comparison]["hypothesis_id"] is None
    ):
        return "secondary"
    return "confirmatory"


def _runner_projection(
    execution: RegisteredRobustnessExecution,
    *,
    slice_id: str,
    coverage: list[str],
    episode_design: Mapping[str, Any],
) -> StudyConfig:
    document = json.loads(_canonical_json(execution.protocol))
    document.update(
        {
            "protocol_id": f"{execution.document['execution_id']}-{slice_id}",
            "protocol_version": 1,
            "registered_at": execution.document["created_at"],
            "registration_statement": (
                "Shared-runner compatibility projection of values registered in "
                f"{execution.protocol['protocol_id']}; the outer robustness "
                "manifest is authoritative for post-confirmatory analysis status."
            ),
            "execution_projection": {
                "parent_protocol_id": execution.protocol["protocol_id"],
                "parent_protocol_sha256": execution.protocol_sha256,
                "execution_plan_sha256": execution.sha256,
                "created_after_confirmatory_outcome_access": True,
                "analysis_tier": "robustness",
                "confirmatory_outcomes_accessed_field": (
                    "Inherited registration-time value required by the sealed "
                    "shared-runner schema; not a claim about execution time."
                ),
            },
        }
    )
    document["coverage"]["primary"] = coverage
    document["corrected_mean"]["primary"] = [
        value
        for value in execution.protocol["corrected_mean"]["primary"]
        if value["config_id"]
        in execution.document["shared_grid"]["corrected_mean_configurations"]
    ]
    document["episode_design"] = dict(episode_design)
    return StudyConfig.from_mapping(document)


def _quarterly_episode_design(
    execution: RegisteredRobustnessExecution,
) -> Mapping[str, Any]:
    design = dict(execution.protocol["episode_design"])
    robustness = execution.document["quarterly_horizon_extension"]
    design.update(
        {
            "deposit_cadence": "quarterly-first-eligible-observation",
            "deposit_count_rule": robustness["deposit_count_rule"],
            "episode_start_grid_rule": robustness["episode_start_grid_rule"],
            "purchase_mapping": (
                "first eligible observation on or after each nominal quarterly "
                "deposit date"
            ),
            "horizons_months": robustness["horizons_months"],
            "rolling_stride_months": robustness["rolling_stride_months"],
        }
    )
    return design


@dataclass(frozen=True)
class SliceEvidence:
    schedule_id: str
    design_tier: str
    runner_run_id: str
    input_sha256: str
    config_sha256: str
    aggregates: Mapping[str, Any]
    reconciliation: Mapping[str, Any]
    validation: Mapping[str, Any]
    ledger_count: int
    comparison_count: int


def _execute_slice(
    *,
    directory: Path,
    name: str,
    schedule_id: str,
    design_tier: str,
    execution: RegisteredRobustnessExecution,
    config: StudyConfig,
    inputs: VersionedInput,
    attempts: tuple[Mapping[str, Any], ...],
    preparation_reconciliation: Mapping[str, Any],
) -> SliceEvidence:
    _write_json(directory / f"{name}-runner-config.json", config.as_mapping())
    _write_json(directory / f"{name}-runner-input.json", inputs.as_mapping())
    _write_jsonl(directory / f"{name}-episode-attempts.jsonl", attempts)
    runner_root = directory / f".{name}-runner"
    runner = run_experiment(config, inputs, runner_root)
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_HALF_EVEN
        historical = confirmatory_study._aggregate_historical_results(
            config.as_mapping(), runner.episode_results, attempts
        )
    reconciliation = confirmatory_study.reconcile_historical_aggregates(
        historical, runner.aggregates
    )
    groups = []
    for source_group in historical["groups"]:
        group = dict(source_group)
        key = HistoricalCellKey.from_group(group, design_tier)
        group["analysis_tier"] = classify_analysis_tier(key, execution.protocol)
        group["schedule_id"] = schedule_id
        group["design_tier"] = design_tier
        group["uncertainty_status"] = "not-run-robustness"
        groups.append(group)
    historical = {
        **historical,
        "groups": groups,
        "group_count": len(groups),
        "schedule_id": schedule_id,
        "design_tier": design_tier,
    }
    _require(
        all(group["analysis_tier"] != "confirmatory" for group in groups),
        "confirmatory_contamination",
        name,
        "a robustness execution emitted a confirmatory cell",
    )
    _require(
        int(preparation_reconciliation["runner_input_episode_count"])
        == runner.aggregates["episode_count"],
        "sample_reconciliation_mismatch",
        name,
        "prepared and executed episode counts must match",
    )
    final_runner = directory / f"{name}-runner"
    os.replace(runner.output_directory, final_runner)
    runner_root.rmdir()
    packaged_manifest = confirmatory_study._package_runner_ledgers(final_runner)
    validation = dict(runner.validation)
    ledger_count = int(validation["ledger_count"])
    comparison_count = int(validation["episode_result_count"])
    evidence = SliceEvidence(
        schedule_id=schedule_id,
        design_tier=design_tier,
        runner_run_id=runner.run_id,
        input_sha256=inputs.sha256,
        config_sha256=config.sha256,
        aggregates=historical,
        reconciliation=reconciliation,
        validation=validation,
        ledger_count=ledger_count,
        comparison_count=comparison_count,
    )
    del runner
    del packaged_manifest
    gc.collect()
    return evidence


def _render_report_tables(aggregates: Mapping[str, Any]) -> str:
    lines = [
        "# Generated registered historical robustness tables",
        "",
        "These descriptive tables are generated from the immutable robustness run.",
        "They do not enter the confirmatory H1/H2 family.",
        "",
        "## Frictionless median ranges",
        "",
        "| Schedule | Dataset | Horizon | Comparison | N | Coverage cells | Median range |",
        "|---|---|---:|---|---:|---:|---:|",
    ]
    groups: dict[tuple[str, str, int, str], list[Mapping[str, Any]]] = {}
    for group in aggregates["groups"]:
        if (
            group["cost_scenario"] == "frictionless"
            and group["coverage"] != "1"
        ):
            key = (
                str(group["schedule_id"]),
                str(group["dataset_id"]),
                int(group["horizon_months"]),
                str(group["comparison"]),
            )
            groups.setdefault(key, []).append(group)
    for key in sorted(
        groups,
        key=lambda value: (
            value[0],
            value[1],
            value[2],
            COMPARISON_METADATA[value[3]]["order"],
        ),
    ):
        members = groups[key]
        medians = [
            Decimal(str(member["median_relative_terminal_wealth_gap"]))
            for member in members
        ]
        lines.append(
            "| "
            + " | ".join(
                (
                    key[0],
                    key[1],
                    str(key[2]),
                    str(COMPARISON_METADATA[key[3]]["label"]),
                    str(members[0]["sample_count"]),
                    str(len(members)),
                    f"{min(medians)} to {max(medians)}",
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Scope boundary",
            "",
            (
                f"The artifact contains {aggregates['group_count']} descriptive "
                "cells. No robustness row has confirmatory analysis status or "
                "confirmatory uncertainty."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _artifact_record(root: Path, relative: str, retention: str) -> dict[str, Any]:
    path = root / relative
    record: dict[str, Any] = {
        "path": relative,
        "retention": retention,
        "bytes": path.stat().st_size,
        "sha256": _file_fingerprint(path),
    }
    if relative.endswith(".gz"):
        record["content_encoding"] = "gzip"
    return record


def _write_private_receipt(
    directory: Path,
    execution: RegisteredRobustnessExecution,
    accepted_manifest_sha256: str,
) -> None:
    private_records = [
        _artifact_record(directory, path.relative_to(directory).as_posix(), "private-retained")
        for path in sorted(directory.rglob("*"))
        if path.is_file()
        and path.relative_to(directory).as_posix() != "manifest.json"
        and path.relative_to(directory).as_posix()
        != "private-artifact-receipt.json"
        and path.relative_to(directory).as_posix()
        not in PUBLIC_DERIVED_ARTIFACTS
    ]
    _write_json(
        directory / "private-artifact-receipt.json",
        {
            "schema_version": "smartdca-historical-robustness-private-receipt/1",
            "execution_plan_sha256": execution.sha256,
            "accepted_preparation_manifest_sha256": accepted_manifest_sha256,
            "redistribution_boundary": (
                "Normalized observations, schedules, episode outcomes, and "
                "price-bearing ledgers remain access-controlled outside Git."
            ),
            "generated_private_artifacts": private_records,
        },
    )


def _robustness_run_id(
    execution: RegisteredRobustnessExecution,
    accepted_manifest_sha256: str,
    monthly_config: StudyConfig,
    monthly_input: VersionedInput,
    quarterly_config: StudyConfig,
    quarterly_input: VersionedInput,
) -> str:
    identity = {
        "engine_version": ENGINE_VERSION,
        "source_sha256": _fingerprint(Path(__file__).read_bytes()),
        "confirmatory_study_sha256": _fingerprint(
            Path(confirmatory_study.__file__).read_bytes()
        ),
        "runner_sha256": _fingerprint(
            (Path(__file__).parent / "empirical.py").read_bytes()
        ),
        "protocol_sha256": execution.protocol_sha256,
        "execution_plan_sha256": execution.sha256,
        "accepted_preparation_manifest_sha256": accepted_manifest_sha256,
        "monthly_config_sha256": monthly_config.sha256,
        "monthly_input_sha256": monthly_input.sha256,
        "quarterly_config_sha256": quarterly_config.sha256,
        "quarterly_input_sha256": quarterly_input.sha256,
    }
    return f"smartdca-historical-robustness-v1-{_fingerprint(_canonical_json(identity).encode('utf-8'))}"


def run_registered_historical_robustness(
    protocol_path: Path,
    execution_plan_path: Path,
    accepted_manifest_path: Path,
    preparation_directory: Path,
    output_root: Path,
    *,
    publication_root: Path | None = None,
) -> Path:
    """Execute both registered robustness extensions into immutable bundles."""

    _require(
        sys.implementation.name == "cpython" and sys.version_info[:2] == (3, 12),
        "invalid_runtime",
        "runtime",
        "must be CPython 3.12",
    )
    execution = load_registered_robustness_execution(
        execution_plan_path, protocol_path, accepted_manifest_path
    )
    accepted = confirmatory_study._validate_accepted_preparation(
        protocol_path, accepted_manifest_path, preparation_directory
    )
    _require(
        accepted.manifest_sha256
        == execution.document["accepted_preparation"]["manifest_sha256"],
        "preparation_fingerprint_mismatch",
        "accepted_manifest",
        "must match the execution plan",
    )
    normalized = _decode_document(
        _read_bytes(
            preparation_directory / "normalized-datasets.json",
            "preparation.normalized-datasets",
        ),
        "preparation.normalized-datasets",
    )
    source_receipts = accepted.runner_input.as_mapping().get("source_receipts")
    _require(
        isinstance(source_receipts, list),
        "invalid_type",
        "preparation.runner-input.source_receipts",
        "must be a list",
    )
    monthly_attempts, monthly_input, monthly_preparation = (
        build_monthly_robustness_input(execution, accepted)
    )
    quarterly_attempts, quarterly_input, quarterly_preparation = (
        build_quarterly_robustness_input(execution, normalized, source_receipts)
    )
    monthly_config = _runner_projection(
        execution,
        slice_id="monthly-coverage",
        coverage=execution.document["monthly_coverage_extension"][
            "runner_compatibility_coverage"
        ],
        episode_design=execution.protocol["episode_design"],
    )
    quarterly_config = _runner_projection(
        execution,
        slice_id="quarterly-horizons",
        coverage=execution.document["quarterly_horizon_extension"]["coverage"],
        episode_design=_quarterly_episode_design(execution),
    )
    run_id = _robustness_run_id(
        execution,
        accepted.manifest_sha256,
        monthly_config,
        monthly_input,
        quarterly_config,
        quarterly_input,
    )
    output_root.mkdir(parents=True, exist_ok=True)
    final_directory = output_root / run_id
    publication_directory = (
        publication_root / run_id if publication_root is not None else None
    )
    if final_directory.exists() or (
        publication_directory is not None and publication_directory.exists()
    ):
        raise RunIdentityCollisionError(
            "run_identity_collision",
            "output_root",
            f"{run_id} already exists",
        )
    temporary = Path(tempfile.mkdtemp(prefix=f".{run_id}-", dir=output_root))
    publication_temporary: Path | None = None
    private_finalized = False
    try:
        shutil.copyfile(
            accepted_manifest_path,
            temporary / "accepted-preparation-manifest.json",
        )
        monthly = _execute_slice(
            directory=temporary,
            name="monthly",
            schedule_id=execution.document["monthly_coverage_extension"][
                "schedule_id"
            ],
            design_tier="primary",
            execution=execution,
            config=monthly_config,
            inputs=monthly_input,
            attempts=monthly_attempts,
            preparation_reconciliation=monthly_preparation,
        )
        quarterly = _execute_slice(
            directory=temporary,
            name="quarterly",
            schedule_id=execution.document["quarterly_horizon_extension"][
                "schedule_id"
            ],
            design_tier="robustness",
            execution=execution,
            config=quarterly_config,
            inputs=quarterly_input,
            attempts=quarterly_attempts,
            preparation_reconciliation=quarterly_preparation,
        )
        groups = sorted(
            [
                *monthly.aggregates["groups"],
                *quarterly.aggregates["groups"],
            ],
            key=lambda group: HistoricalCellKey.from_group(
                group, str(group["design_tier"])
            ),
        )
        aggregates = {
            "attempted_episode_count": (
                monthly_preparation["attempted_episode_count"]
                + quarterly_preparation["attempted_episode_count"]
            ),
            "included_episode_count": (
                monthly_preparation["included_episode_count"]
                + quarterly_preparation["included_episode_count"]
            ),
            "excluded_episode_count": (
                monthly_preparation["excluded_episode_count"]
                + quarterly_preparation["excluded_episode_count"]
            ),
            "group_count": len(groups),
            "groups": groups,
        }
        _write_json(temporary / "robustness-aggregates.json", aggregates)
        _write_csv(
            temporary / "robustness-figure-ready.csv",
            [dict(group) for group in groups],
        )
        (temporary / "report-tables.md").write_text(
            _render_report_tables(aggregates),
            encoding="utf-8",
            newline="\n",
        )
        tier_counts = dict(
            sorted(Counter(group["analysis_tier"] for group in groups).items())
        )
        _require(
            "confirmatory" not in tier_counts,
            "confirmatory_contamination",
            "robustness-aggregates",
            "must not add to the sealed confirmatory family",
        )
        validation = {
            "status": "passed",
            "created_after_confirmatory_outcome_access": True,
            "confirmatory_family_change": "none",
            "uncertainty_status": "not-run-robustness",
            "protocol_violations": [],
            "deviations": [],
            "sample_reconciliation": {
                "source_observation_count": monthly_preparation[
                    "source_observation_count"
                ],
                "monthly": monthly_preparation,
                "quarterly": quarterly_preparation,
                "total_attempted_episode_count": aggregates[
                    "attempted_episode_count"
                ],
                "total_included_episode_count": aggregates[
                    "included_episode_count"
                ],
                "total_excluded_episode_count": aggregates[
                    "excluded_episode_count"
                ],
                "ledger_count": monthly.ledger_count + quarterly.ledger_count,
                "comparison_count": (
                    monthly.comparison_count + quarterly.comparison_count
                ),
                "aggregate_group_count": len(groups),
            },
            "analysis_tier_counts": tier_counts,
            "slice_validation": {
                "monthly": {
                    "runner_run_id": monthly.runner_run_id,
                    "input_sha256": monthly.input_sha256,
                    "config_sha256": monthly.config_sha256,
                    "aggregate_reconciliation": monthly.reconciliation,
                    "shared_runner_validation": monthly.validation,
                },
                "quarterly": {
                    "runner_run_id": quarterly.runner_run_id,
                    "input_sha256": quarterly.input_sha256,
                    "config_sha256": quarterly.config_sha256,
                    "aggregate_reconciliation": quarterly.reconciliation,
                    "shared_runner_validation": quarterly.validation,
                },
            },
        }
        _write_json(temporary / "study-validation.json", validation)
        _write_private_receipt(
            temporary, execution, accepted.manifest_sha256
        )
        artifacts = [
            _artifact_record(
                temporary,
                path.relative_to(temporary).as_posix(),
                (
                    "public-derived"
                    if path.relative_to(temporary).as_posix()
                    in PUBLIC_DERIVED_ARTIFACTS
                    else "private-retained"
                ),
            )
            for path in sorted(temporary.rglob("*"))
            if path.is_file()
        ]
        manifest = {
            "schema_version": "smartdca-historical-robustness-manifest/1",
            "run_id": run_id,
            "engine_version": ENGINE_VERSION,
            "source_sha256": _fingerprint(Path(__file__).read_bytes()),
            "confirmatory_study_sha256": _fingerprint(
                Path(confirmatory_study.__file__).read_bytes()
            ),
            "runner_sha256": _fingerprint(
                (Path(__file__).parent / "empirical.py").read_bytes()
            ),
            "protocol_id": execution.protocol["protocol_id"],
            "protocol_sha256": execution.protocol_sha256,
            "execution_plan_id": execution.document["execution_id"],
            "execution_plan_sha256": execution.sha256,
            "accepted_preparation_manifest_sha256": accepted.manifest_sha256,
            "created_after_confirmatory_outcome_access": True,
            "analysis_tier": "robustness",
            "confirmatory_family_change": "none",
            "uncertainty_status": "not-run-robustness",
            "runtime": {
                "implementation": "CPython",
                "python": f"{sys.version_info.major}.{sys.version_info.minor}",
                "third_party": [],
            },
            "slices": {
                "monthly": {
                    "schedule_id": monthly.schedule_id,
                    "runner_run_id": monthly.runner_run_id,
                    "config_sha256": monthly.config_sha256,
                    "input_sha256": monthly.input_sha256,
                },
                "quarterly": {
                    "schedule_id": quarterly.schedule_id,
                    "runner_run_id": quarterly.runner_run_id,
                    "config_sha256": quarterly.config_sha256,
                    "input_sha256": quarterly.input_sha256,
                },
            },
            "execution_grid": {
                "monthly_horizons_months": execution.document[
                    "monthly_coverage_extension"
                ]["horizons_months"],
                "monthly_coverage": execution.document[
                    "monthly_coverage_extension"
                ]["coverage"],
                "quarterly_horizons_months": execution.document[
                    "quarterly_horizon_extension"
                ]["horizons_months"],
                "quarterly_coverage": execution.document[
                    "quarterly_horizon_extension"
                ]["coverage"],
                **execution.document["shared_grid"],
            },
            "retention": execution.document["retention"],
            "reproduction": {
                "module": "reproducibility.historical_robustness",
                "protocol": execution.document["parent_protocol"]["path"],
                "execution_plan": execution_plan_path.as_posix(),
                "accepted_preparation_manifest": accepted_manifest_path.as_posix(),
                "preparation_directory": "<private-accepted-preparation-directory>",
                "output_root": "<new-empty-private-output-root>",
                "publication_root": "<new-empty-publication-root-or-omit>",
            },
            "artifacts": artifacts,
        }
        _write_json(temporary / "manifest.json", manifest)
        if publication_directory is not None:
            assert publication_root is not None
            publication_root.mkdir(parents=True, exist_ok=True)
            publication_temporary = Path(
                tempfile.mkdtemp(prefix=f".{run_id}-", dir=publication_root)
            )
            for relative in sorted(PUBLIC_DERIVED_ARTIFACTS):
                shutil.copyfile(
                    temporary / relative, publication_temporary / relative
                )
            shutil.copyfile(
                temporary / "manifest.json",
                publication_temporary / "manifest.json",
            )
        os.replace(temporary, final_directory)
        private_finalized = True
        if publication_directory is not None:
            assert publication_temporary is not None
            os.replace(publication_temporary, publication_directory)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        if publication_temporary is not None:
            shutil.rmtree(publication_temporary, ignore_errors=True)
        if private_finalized:
            shutil.rmtree(final_directory, ignore_errors=True)
        raise
    return final_directory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Execute registered post-confirmatory historical robustness."
    )
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--execution-plan", required=True, type=Path)
    parser.add_argument("--accepted-preparation-manifest", required=True, type=Path)
    parser.add_argument("--preparation-directory", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--publication-root", type=Path)
    arguments = parser.parse_args(argv)
    try:
        output = run_registered_historical_robustness(
            arguments.config,
            arguments.execution_plan,
            arguments.accepted_preparation_manifest,
            arguments.preparation_directory,
            arguments.output_root,
            publication_root=arguments.publication_root,
        )
    except ExperimentValidationError as error:
        print(
            _canonical_json(
                {
                    "status": "rejected",
                    "code": error.code,
                    "field": error.field,
                    "message": str(error),
                }
            ),
            file=sys.stderr,
        )
        return 2
    except Exception as error:
        print(
            _canonical_json(
                {
                    "status": "failed",
                    "code": type(error).__name__,
                    "message": str(error),
                }
            ),
            file=sys.stderr,
        )
        return 1
    print(
        _canonical_json(
            {
                "status": "completed",
                "output_directory": str(output.resolve()),
                "manifest": str((output / "manifest.json").resolve()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
