"""Immutable confirmatory evaluation of accepted historical episode inputs."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import random
import shutil
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from reproducibility.empirical import (
    ENGINE_VERSION as RUNNER_ENGINE_VERSION,
    ExperimentValidationError,
    RunBundle,
    RunIdentityCollisionError,
    VersionedInput,
    load_study_config,
    run_experiment,
)


STUDY_ENGINE_VERSION = "smartdca-historical-study/1"
REQUIRED_PREPARATION_ARTIFACTS = {
    "episode-attempts.jsonl",
    "normalized-datasets.json",
    "reconciliation.json",
    "runner-input.json",
    "source-receipts.json",
    "validation.json",
}
PUBLIC_DERIVED_ARTIFACTS = {
    "aggregate-reconciliation.json",
    "historical-aggregates.json",
    "historical-figure-ready.csv",
    "private-artifact-receipt.json",
    "report-tables.md",
    "study-validation.json",
    "uncertainty.json",
}


def _fingerprint(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _require(condition: bool, code: str, field: str, message: str) -> None:
    if not condition:
        raise ExperimentValidationError(code, field, message)


def _read_bytes(path: Path, field: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as error:
        raise ExperimentValidationError("unreadable_artifact", field, str(error)) from error


def _decode_document(payload: bytes, field: str) -> dict[str, Any]:
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ExperimentValidationError(
            "invalid_json", field, "must be one UTF-8 JSON document"
        ) from error
    _require(isinstance(value, dict), "invalid_type", field, "must be a JSON object")
    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _write_json(path: Path, value: Any) -> None:
    path.write_text(_canonical_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: tuple[Mapping[str, Any], ...]) -> None:
    path.write_text(
        "".join(_canonical_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def _write_csv(path: Path, rows: list[Mapping[str, Any]]) -> None:
    identifier_fields = [
        "analysis_tier",
        "dataset_id",
        "horizon_months",
        "coverage",
        "corrected_mean_config",
        "cost_scenario",
        "comparison",
        "theorem_scope",
    ]
    fields = identifier_fields + sorted(
        {field for row in rows for field in row} - set(identifier_fields)
    )
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(
            {
                field: (
                    _canonical_json(row[field])
                    if isinstance(row.get(field), (dict, list))
                    else row.get(field)
                )
                for field in fields
            }
            for row in rows
        )


def _runner_source_sha256() -> str:
    module_path = Path(sys.modules[run_experiment.__module__].__file__)
    return _fingerprint(module_path.read_bytes())


def _source_sha256() -> str:
    return _fingerprint(Path(__file__).read_bytes())


@dataclass(frozen=True)
class AcceptedHistoricalPreparation:
    """Accepted full-grid preparation validated before policy execution."""

    manifest: Mapping[str, Any]
    manifest_sha256: str
    runner_input: VersionedInput
    reconciliation: Mapping[str, Any]
    episode_attempts: tuple[Mapping[str, Any], ...]
    attempt_count: int


@dataclass(frozen=True)
class HistoricalStudyBundle:
    """Complete immutable historical study plus the shared runner bundle."""

    study_run_id: str
    output_directory: Path
    publication_directory: Path | None
    manifest: Mapping[str, Any]
    aggregates: Mapping[str, Any]
    uncertainty: Mapping[str, Any]
    validation: Mapping[str, Any]
    runner: RunBundle


@dataclass(frozen=True)
class BootstrapResult:
    """One reproducible circular moving-block median bootstrap."""

    observed_statistic: Decimal
    replicate_statistics: tuple[Decimal, ...]
    interval_lower: Decimal
    interval_upper: Decimal
    centered_tail_count: int
    p_value_numerator: int
    p_value_denominator: int
    sample_count: int
    block_length: int
    blocks_per_replicate: int
    replicates: int
    seed: int


def _median(values: tuple[Decimal, ...]) -> Decimal:
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / Decimal(2)


def _quantile(values: tuple[Decimal, ...], probability: Decimal) -> Decimal:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = Decimal(len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - Decimal(lower)
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def _mean(values: tuple[Decimal, ...]) -> Decimal:
    return sum(values, Decimal("0")) / Decimal(len(values))


def _decimal(value: Any, field: str) -> Decimal:
    _require(
        isinstance(value, (str, int)) and not isinstance(value, bool),
        "invalid_decimal",
        field,
        "must be an integer or decimal string",
    )
    try:
        result = Decimal(str(value))
    except Exception as error:
        raise ExperimentValidationError(
            "invalid_decimal", field, "must be finite"
        ) from error
    _require(result.is_finite(), "invalid_decimal", field, "must be finite")
    return result


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    if value == 0:
        return "0"
    text = format(value.normalize(), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def _mean_field(members: list[Mapping[str, Any]], field: str) -> str | None:
    values = tuple(
        _decimal(row[field], f"aggregate.{field}")
        for row in members
        if row[field] is not None
    )
    return _decimal_text(_mean(values)) if values else None


def _analysis_tier(
    comparison: str, coverage: str, cost_scenario: str
) -> str:
    if cost_scenario != "frictionless":
        return "robustness"
    if coverage != "1" and comparison in {
        "corrected_guarded_vs_dca",
        "corrected_guarded_vs_neutral_guarded",
    }:
        return "confirmatory"
    return "secondary"


def _aggregate_historical_results(
    config: Mapping[str, Any],
    results: tuple[Mapping[str, Any], ...],
    attempts: tuple[Mapping[str, Any], ...],
) -> dict[str, Any]:
    result_groups: dict[
        tuple[str, int, str, str, str, str], list[Mapping[str, Any]]
    ] = {}
    for result in results:
        key = (
            str(result["dataset_id"]),
            int(result["horizon_months"]),
            str(result["coverage"]),
            str(result["corrected_mean_config"]),
            str(result["cost_scenario"]),
            str(result["comparison"]),
        )
        result_groups.setdefault(key, []).append(result)
    attempt_groups: dict[tuple[str, int], list[Mapping[str, Any]]] = {}
    for attempt in attempts:
        attempt_groups.setdefault(
            (str(attempt["dataset_id"]), int(attempt["horizon_months"])), []
        ).append(attempt)
    comparisons = (
        "corrected_guarded_vs_dca",
        "corrected_guarded_vs_neutral_guarded",
        "neutral_guarded_vs_dca",
    )
    groups: list[dict[str, Any]] = []
    for dataset_id, horizon_months in sorted(attempt_groups):
        cell_attempts = attempt_groups[(dataset_id, horizon_months)]
        for coverage in config["coverage"]["primary"]:
            for mean in config["corrected_mean"]["primary"]:
                for cost in config["cost_scenarios"]:
                    for comparison in comparisons:
                        key = (
                            dataset_id,
                            horizon_months,
                            coverage,
                            mean["config_id"],
                            cost["cost_id"],
                            comparison,
                        )
                        attempted_results = sorted(
                            result_groups.get(key, []),
                            key=lambda row: str(row["episode_id"]),
                        )
                        members = [
                            row
                            for row in attempted_results
                            if row["result_status"] == "included"
                        ]
                        relative = tuple(
                            _decimal(
                                row["relative_terminal_wealth_gap"],
                                "aggregate.relative_terminal_wealth_gap",
                            )
                            for row in members
                        )
                        gaps = tuple(
                            _decimal(
                                row["terminal_wealth_gap"],
                                "aggregate.terminal_wealth_gap",
                            )
                            for row in members
                        )
                        ratios = tuple(
                            _decimal(row["wealth_ratio"], "aggregate.wealth_ratio")
                            for row in members
                        )
                        exclusions = Counter(
                            str(attempt["exclusion_reason"])
                            for attempt in cell_attempts
                            if attempt["status"] == "excluded"
                        )
                        exclusions.update(
                            str(row["exclusion_reason"])
                            for row in attempted_results
                            if row["result_status"] == "excluded"
                        )
                        group: dict[str, Any] = {
                            "analysis_tier": _analysis_tier(
                                comparison, coverage, cost["cost_id"]
                            ),
                            "dataset_id": dataset_id,
                            "horizon_months": horizon_months,
                            "coverage": coverage,
                            "corrected_mean_config": mean["config_id"],
                            "cost_scenario": cost["cost_id"],
                            "comparison": comparison,
                            "theorem_scope": cost["theorem_scope"],
                            "attempted_count": len(cell_attempts),
                            "preparation_excluded_count": sum(
                                attempt["status"] == "excluded"
                                for attempt in cell_attempts
                            ),
                            "runner_attempted_count": len(attempted_results),
                            "result_excluded_count": sum(
                                row["result_status"] == "excluded"
                                for row in attempted_results
                            ),
                            "sample_count": len(members),
                            "excluded_count": len(cell_attempts) - len(members),
                            "exclusions_by_reason": dict(sorted(exclusions.items())),
                            "mean_terminal_wealth_gap": (
                                _decimal_text(_mean(gaps)) if gaps else None
                            ),
                            "mean_wealth_ratio": (
                                _decimal_text(_mean(ratios)) if ratios else None
                            ),
                            "win_count": sum(value > 0 for value in gaps),
                            "tie_count": sum(value == 0 for value in gaps),
                            "loss_count": sum(value < 0 for value in gaps),
                        }
                        if ratios:
                            group.update(
                                {
                                    "median_wealth_ratio": _decimal_text(
                                        _median(ratios)
                                    ),
                                    "minimum_wealth_ratio": _decimal_text(min(ratios)),
                                    "maximum_wealth_ratio": _decimal_text(max(ratios)),
                                    "wealth_ratio_quantile_0.05": _decimal_text(
                                        _quantile(ratios, Decimal("0.05"))
                                    ),
                                    "wealth_ratio_quantile_0.10": _decimal_text(
                                        _quantile(ratios, Decimal("0.10"))
                                    ),
                                    "wealth_ratio_quantile_0.25": _decimal_text(
                                        _quantile(ratios, Decimal("0.25"))
                                    ),
                                    "wealth_ratio_quantile_0.75": _decimal_text(
                                        _quantile(ratios, Decimal("0.75"))
                                    ),
                                    "wealth_ratio_quantile_0.90": _decimal_text(
                                        _quantile(ratios, Decimal("0.90"))
                                    ),
                                    "wealth_ratio_quantile_0.95": _decimal_text(
                                        _quantile(ratios, Decimal("0.95"))
                                    ),
                                }
                            )
                        else:
                            for field in (
                                "median_wealth_ratio",
                                "minimum_wealth_ratio",
                                "maximum_wealth_ratio",
                                "wealth_ratio_quantile_0.05",
                                "wealth_ratio_quantile_0.10",
                                "wealth_ratio_quantile_0.25",
                                "wealth_ratio_quantile_0.75",
                                "wealth_ratio_quantile_0.90",
                                "wealth_ratio_quantile_0.95",
                            ):
                                group[field] = None
                        if relative:
                            minimum = min(relative)
                            group.update(
                                {
                                    "mean_relative_terminal_wealth_gap": _decimal_text(
                                        _mean(relative)
                                    ),
                                    "median_relative_terminal_wealth_gap": _decimal_text(
                                        _median(relative)
                                    ),
                                    "minimum_relative_terminal_wealth_gap": _decimal_text(
                                        minimum
                                    ),
                                    "maximum_relative_terminal_wealth_gap": _decimal_text(
                                        max(relative)
                                    ),
                                    "downside_quantile_0.05": _decimal_text(
                                        _quantile(relative, Decimal("0.05"))
                                    ),
                                    "downside_quantile_0.10": _decimal_text(
                                        _quantile(relative, Decimal("0.10"))
                                    ),
                                    "downside_quantile_0.25": _decimal_text(
                                        _quantile(relative, Decimal("0.25"))
                                    ),
                                    "worst_observed_relative_shortfall": _decimal_text(
                                        max(Decimal("0"), -minimum)
                                    ),
                                }
                            )
                        else:
                            for field in (
                                "mean_relative_terminal_wealth_gap",
                                "median_relative_terminal_wealth_gap",
                                "minimum_relative_terminal_wealth_gap",
                                "maximum_relative_terminal_wealth_gap",
                                "downside_quantile_0.05",
                                "downside_quantile_0.10",
                                "downside_quantile_0.25",
                                "worst_observed_relative_shortfall",
                            ):
                                group[field] = None
                        for field in (
                            "terminal_cash_gap",
                            "terminal_unit_gap",
                            "cash_contribution",
                            "unit_contribution",
                            "identity_residual",
                            "left_cash_drag",
                            "right_cash_drag",
                            "left_asset_exposure",
                            "right_asset_exposure",
                            "left_guardrail_activation_frequency",
                            "right_guardrail_activation_frequency",
                            "left_mean_guardrail_floor",
                            "right_mean_guardrail_floor",
                            "left_total_fees",
                            "right_total_fees",
                        ):
                            output_field = {
                                "left_mean_guardrail_floor": "mean_left_guardrail_floor",
                                "right_mean_guardrail_floor": "mean_right_guardrail_floor",
                            }.get(field, f"mean_{field}")
                            group[output_field] = _mean_field(members, field)
                        for side in ("left", "right"):
                            counts = tuple(
                                Decimal(row[f"{side}_purchase_count"])
                                for row in members
                            )
                            group[f"mean_{side}_purchase_count"] = (
                                _decimal_text(_mean(counts)) if counts else None
                            )
                        groups.append(group)
    return {
        "group_count": len(groups),
        "attempted_episode_count": len(attempts),
        "included_episode_count": sum(
            attempt["status"] == "included" for attempt in attempts
        ),
        "excluded_episode_count": sum(
            attempt["status"] == "excluded" for attempt in attempts
        ),
        "groups": groups,
    }


def _aggregate_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        row["dataset_id"],
        row["horizon_months"],
        row["coverage"],
        row["corrected_mean_config"],
        row["cost_scenario"],
        row["comparison"],
    )


def reconcile_historical_aggregates(
    historical_aggregates: Mapping[str, Any],
    runner_aggregates: Mapping[str, Any],
) -> dict[str, Any]:
    """Reconcile independently calculated historical and runner aggregates."""

    historical_groups = {
        _aggregate_key(row): row for row in historical_aggregates["groups"]
    }
    runner_groups = {_aggregate_key(row): row for row in runner_aggregates["groups"]}
    _require(
        len(historical_groups) == int(historical_aggregates["group_count"]),
        "aggregate_reconciliation_mismatch",
        "historical_aggregates.group_count",
        "must equal the number of unique historical cells",
    )
    _require(
        len(runner_groups) == int(runner_aggregates["group_count"]),
        "aggregate_reconciliation_mismatch",
        "runner_aggregates.group_count",
        "must equal the number of unique runner cells",
    )
    _require(
        set(runner_groups) <= set(historical_groups),
        "aggregate_reconciliation_mismatch",
        "aggregate_groups",
        "every runner cell must have one historical aggregate",
    )
    compared_fields = (
        "sample_count",
        "mean_terminal_wealth_gap",
        "mean_wealth_ratio",
        "win_count",
        "tie_count",
        "loss_count",
        "mean_relative_terminal_wealth_gap",
        "median_relative_terminal_wealth_gap",
        "minimum_relative_terminal_wealth_gap",
        "maximum_relative_terminal_wealth_gap",
        "downside_quantile_0.05",
        "downside_quantile_0.10",
        "downside_quantile_0.25",
        "mean_terminal_cash_gap",
        "mean_terminal_unit_gap",
        "mean_left_cash_drag",
        "mean_right_cash_drag",
        "mean_left_asset_exposure",
        "mean_right_asset_exposure",
        "mean_left_guardrail_activation_frequency",
        "mean_right_guardrail_activation_frequency",
        "mean_left_guardrail_floor",
        "mean_right_guardrail_floor",
        "mean_left_total_fees",
        "mean_right_total_fees",
        "mean_left_purchase_count",
        "mean_right_purchase_count",
    )
    for key, runner_group in runner_groups.items():
        historical_group = historical_groups[key]
        _require(
            historical_group["runner_attempted_count"]
            == runner_group["attempted_count"],
            "aggregate_reconciliation_mismatch",
            f"aggregate.{key}.runner_attempted_count",
            "must match the shared runner",
        )
        _require(
            historical_group["result_excluded_count"]
            == runner_group["excluded_count"],
            "aggregate_reconciliation_mismatch",
            f"aggregate.{key}.result_excluded_count",
            "must match the shared runner",
        )
        for field in compared_fields:
            _require(
                historical_group[field] == runner_group[field],
                "aggregate_reconciliation_mismatch",
                f"aggregate.{key}.{field}",
                "independent historical and shared-runner values differ",
            )
    empty_historical_cells = [
        key for key in historical_groups if key not in runner_groups
    ]
    _require(
        all(
            historical_groups[key]["runner_attempted_count"] == 0
            and historical_groups[key]["sample_count"] == 0
            for key in empty_historical_cells
        ),
        "aggregate_reconciliation_mismatch",
        "aggregate_groups",
        "a historical-only cell must contain preparation exclusions only",
    )
    return {
        "status": "passed",
        "group_count": len(historical_groups),
        "runner_group_count": len(runner_groups),
        "preparation_only_group_count": len(empty_historical_cells),
        "compared_fields": list(compared_fields),
    }


def circular_moving_block_bootstrap(
    values: tuple[Decimal, ...],
    *,
    block_length: int,
    replicates: int,
    seed: int,
) -> BootstrapResult:
    """Apply the registered circular-block bootstrap to one ordered cell."""

    _require(
        isinstance(values, tuple) and values,
        "invalid_bootstrap_sample",
        "values",
        "must be a nonempty tuple",
    )
    _require(
        all(isinstance(value, Decimal) and value.is_finite() for value in values),
        "invalid_bootstrap_sample",
        "values",
        "must contain finite Decimal values",
    )
    _require(
        isinstance(block_length, int)
        and not isinstance(block_length, bool)
        and block_length > 0,
        "invalid_block_length",
        "block_length",
        "must be a positive integer",
    )
    _require(
        isinstance(replicates, int)
        and not isinstance(replicates, bool)
        and replicates > 0,
        "invalid_replicates",
        "replicates",
        "must be a positive integer",
    )
    _require(
        isinstance(seed, int) and not isinstance(seed, bool),
        "invalid_seed",
        "seed",
        "must be an integer",
    )
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_HALF_EVEN
        sample_count = len(values)
        blocks_per_replicate = (sample_count + block_length - 1) // block_length
        generator = random.Random(seed)
        statistics: list[Decimal] = []
        for _ in range(replicates):
            resample: list[Decimal] = []
            for _ in range(blocks_per_replicate):
                start = generator.randrange(sample_count)
                resample.extend(
                    values[(start + offset) % sample_count]
                    for offset in range(block_length)
                )
            statistics.append(_median(tuple(resample[:sample_count])))
        observed = _median(values)
        replicate_statistics = tuple(statistics)
        tail_count = sum(
            abs(value - observed) >= abs(observed)
            for value in replicate_statistics
        )
        return BootstrapResult(
            observed_statistic=observed,
            replicate_statistics=replicate_statistics,
            interval_lower=_quantile(replicate_statistics, Decimal("0.025")),
            interval_upper=_quantile(replicate_statistics, Decimal("0.975")),
            centered_tail_count=tail_count,
            p_value_numerator=tail_count + 1,
            p_value_denominator=replicates + 1,
            sample_count=sample_count,
            block_length=block_length,
            blocks_per_replicate=blocks_per_replicate,
            replicates=replicates,
            seed=seed,
        )


def confirmatory_cell_seed(
    base_seed: int,
    *,
    dataset_id: str,
    horizon_months: int,
    coverage: str,
    comparison: str,
    corrected_mean_config: str,
    cost_scenario: str,
) -> int:
    """Derive the protocol-registered order-independent bootstrap seed."""

    components = (
        base_seed,
        dataset_id,
        horizon_months,
        coverage,
        comparison,
        corrected_mean_config,
        cost_scenario,
    )
    _require(
        isinstance(base_seed, int)
        and not isinstance(base_seed, bool)
        and all(isinstance(value, (str, int)) for value in components[1:]),
        "invalid_cell_seed_input",
        "uncertainty.cell_seed",
        "must use the registered integer and string fields",
    )
    payload = "|".join(str(value) for value in components).encode("utf-8")
    return int(_fingerprint(payload)[:16], 16)


def _fraction_text(value: Fraction) -> str:
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_HALF_EVEN
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def _uncertainty_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        row["dataset_id"],
        row["horizon_months"],
        row["coverage"],
        row["corrected_mean_config"],
        row["cost_scenario"],
        row["comparison"],
    )


def _holm_tie_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        row["dataset_id"],
        row["horizon_months"],
        Decimal(str(row["coverage"])),
        {
            "corrected_guarded_vs_dca": 0,
            "corrected_guarded_vs_neutral_guarded": 1,
        }[str(row["comparison"])],
        row["corrected_mean_config"],
        row["cost_scenario"],
    )


def _apply_holm(cells: list[dict[str, Any]]) -> None:
    ordered = sorted(
        cells,
        key=lambda row: (
            Fraction(
                int(row["p_value_numerator"]),
                int(row["p_value_denominator"]),
            ),
            _holm_tie_key(row),
        ),
    )
    family_size = len(ordered)
    running = Fraction(0, 1)
    for index, row in enumerate(ordered):
        unadjusted = Fraction(
            int(row["p_value_numerator"]), int(row["p_value_denominator"])
        )
        candidate = min(Fraction(1, 1), unadjusted * (family_size - index))
        running = max(running, candidate)
        row["holm_rank"] = index + 1
        row["holm_family_size"] = family_size
        row["holm_adjusted_p_value_numerator"] = running.numerator
        row["holm_adjusted_p_value_denominator"] = running.denominator
        row["holm_adjusted_p_value"] = _fraction_text(running)


def _confirmatory_uncertainty(
    config: Mapping[str, Any],
    input_document: Mapping[str, Any],
    results: tuple[Mapping[str, Any], ...],
) -> tuple[dict[str, Any], tuple[Mapping[str, Any], ...]]:
    uncertainty = config["uncertainty"]
    base_seed = int(uncertainty["seed"])
    replicates = int(uncertainty["replicates"])
    episodes = {
        episode["episode_id"]: episode for episode in input_document["episodes"]
    }
    groups: dict[tuple[Any, ...], list[Mapping[str, Any]]] = {}
    for row in results:
        if _analysis_tier(
            str(row["comparison"]),
            str(row["coverage"]),
            str(row["cost_scenario"]),
        ) != "confirmatory":
            continue
        groups.setdefault(_uncertainty_key(row), []).append(row)
    cells: list[dict[str, Any]] = []
    replicate_rows: list[Mapping[str, Any]] = []
    for key in sorted(
        groups,
        key=lambda value: (
            value[0],
            value[1],
            Decimal(str(value[2])),
            {"corrected_guarded_vs_dca": 0, "corrected_guarded_vs_neutral_guarded": 1}[
                value[5]
            ],
            value[3],
            value[4],
        ),
    ):
        dataset_id, horizon, coverage, mean_id, cost_id, comparison = key
        ordered_members = sorted(
            (
                row
                for row in groups[key]
                if row["result_status"] == "included"
            ),
            key=lambda row: str(
                episodes[row["episode_id"]]["historical_mapping"]["nominal_start"]
            ),
        )
        _require(
            bool(ordered_members),
            "empty_confirmatory_cell",
            "uncertainty",
            f"{key} has no included estimand",
        )
        values = tuple(
            _decimal(
                row["relative_terminal_wealth_gap"],
                "uncertainty.relative_terminal_wealth_gap",
            )
            for row in ordered_members
        )
        cell_seed = confirmatory_cell_seed(
            base_seed,
            dataset_id=str(dataset_id),
            horizon_months=int(horizon),
            coverage=str(coverage),
            comparison=str(comparison),
            corrected_mean_config=str(mean_id),
            cost_scenario=str(cost_id),
        )
        bootstrap = circular_moving_block_bootstrap(
            values,
            block_length=int(horizon),
            replicates=replicates,
            seed=cell_seed,
        )
        statistic_text = tuple(
            _decimal_text(value) for value in bootstrap.replicate_statistics
        )
        p_value = Fraction(
            bootstrap.p_value_numerator, bootstrap.p_value_denominator
        )
        cell_id = _fingerprint(
            "|".join(str(value) for value in key).encode("utf-8")
        )
        cell = {
            "cell_id": cell_id,
            "hypothesis_id": (
                "H1-complete-system"
                if comparison == "corrected_guarded_vs_dca"
                else "H2-signal-contribution"
            ),
            "dataset_id": dataset_id,
            "horizon_months": horizon,
            "coverage": coverage,
            "corrected_mean_config": mean_id,
            "cost_scenario": cost_id,
            "comparison": comparison,
            "method": uncertainty["method"],
            "sample_count": bootstrap.sample_count,
            "sampling_unit": uncertainty["sampling_unit"],
            "nominal_start_min": episodes[ordered_members[0]["episode_id"]][
                "historical_mapping"
            ]["nominal_start"],
            "nominal_start_max": episodes[ordered_members[-1]["episode_id"]][
                "historical_mapping"
            ]["nominal_start"],
            "block_length": bootstrap.block_length,
            "blocks_per_replicate": bootstrap.blocks_per_replicate,
            "block_construction": uncertainty["block_construction"],
            "replicates": bootstrap.replicates,
            "base_seed": base_seed,
            "cell_seed": cell_seed,
            "rng": uncertainty["rng"],
            "observed_statistic": _decimal_text(bootstrap.observed_statistic),
            "interval": uncertainty["interval"],
            "interval_lower": _decimal_text(bootstrap.interval_lower),
            "interval_upper": _decimal_text(bootstrap.interval_upper),
            "quantile_rule": uncertainty["quantile_rule"],
            "centered_tail_count": bootstrap.centered_tail_count,
            "p_value_rule": uncertainty["p_value"],
            "p_value_finite_sample_rule": uncertainty["p_value_finite_sample_rule"],
            "p_value_numerator": p_value.numerator,
            "p_value_denominator": p_value.denominator,
            "unadjusted_p_value": _fraction_text(p_value),
            "replicate_statistics_sha256": _fingerprint(
                _canonical_json(statistic_text).encode("utf-8")
            ),
        }
        cells.append(cell)
        replicate_rows.append(
            {
                "cell_id": cell_id,
                "cell_seed": cell_seed,
                "replicate_statistics": statistic_text,
            }
        )
    _apply_holm(cells)
    return (
        {
            "method": uncertainty["method"],
            "replicates": replicates,
            "base_seed": base_seed,
            "cell_seed_rule": uncertainty["cell_seed_rule"],
            "holm_order": uncertainty["holm_order"],
            "cell_count": len(cells),
            "cells": cells,
        },
        tuple(replicate_rows),
    )


def _attach_uncertainty(
    aggregates: dict[str, Any], uncertainty: Mapping[str, Any]
) -> None:
    cells = {_uncertainty_key(cell): cell for cell in uncertainty["cells"]}
    for group in aggregates["groups"]:
        key = _uncertainty_key(group)
        cell = cells.get(key)
        if cell is None:
            group["uncertainty_status"] = "not-applicable"
            continue
        group.update(
            {
                "uncertainty_status": "estimated-circular-moving-block-bootstrap",
                "interval_lower": cell["interval_lower"],
                "interval_upper": cell["interval_upper"],
                "unadjusted_p_value": cell["unadjusted_p_value"],
                "holm_adjusted_p_value": cell["holm_adjusted_p_value"],
            }
        )


def _gzip_artifact(path: Path) -> dict[str, Any]:
    compressed_path = path.with_name(path.name + ".gz")
    uncompressed_sha256 = _file_fingerprint(path)
    uncompressed_bytes = path.stat().st_size
    with path.open("rb") as source, compressed_path.open("wb") as target:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=target,
            compresslevel=9,
            mtime=0,
        ) as compressed:
            shutil.copyfileobj(source, compressed, length=1024 * 1024)
    with compressed_path.open("r+b") as handle:
        handle.seek(9)
        handle.write(bytes((255,)))
    path.unlink()
    return {
        "path": compressed_path.name,
        "sha256": _file_fingerprint(compressed_path),
        "content_encoding": "gzip",
        "uncompressed_bytes": uncompressed_bytes,
        "uncompressed_sha256": uncompressed_sha256,
    }


def _package_runner_ledgers(runner_directory: Path) -> dict[str, Any]:
    ledger_metadata = _gzip_artifact(runner_directory / "ledgers.jsonl")
    manifest_path = runner_directory / "manifest.json"
    manifest = _decode_document(manifest_path.read_bytes(), "runner.manifest")
    artifacts: list[Mapping[str, Any]] = []
    for artifact in manifest["artifacts"]:
        if artifact["path"] == "ledgers.jsonl":
            artifacts.append(ledger_metadata)
        else:
            artifacts.append(artifact)
    manifest["artifacts"] = artifacts
    manifest["packaging"] = {
        "rule": "deterministic gzip with compresslevel=9, mtime=0, and OS byte 255",
        "reason": "retain complete price-bearing ledgers only in private storage",
    }
    _write_json(manifest_path, manifest)
    return manifest


def _comparison_label(value: str) -> str:
    return {
        "corrected_guarded_vs_dca": "complete system vs DCA",
        "corrected_guarded_vs_neutral_guarded": "signal only vs neutral guarded",
        "neutral_guarded_vs_dca": "safety architecture vs DCA",
    }[value]


def _render_report_tables(
    aggregates: Mapping[str, Any], uncertainty: Mapping[str, Any]
) -> str:
    lines = [
        "# Generated historical evaluation tables",
        "",
        "These tables are generated from the immutable run; they are not a manual transcription.",
        "",
        "## Confirmatory frictionless effects",
        "",
        "| Dataset | Horizon | λ | Comparison | N | Median relative gap | 95% block-bootstrap interval | Holm-adjusted p |",
        "| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for cell in uncertainty["cells"]:
        lines.append(
            "| "
            + " | ".join(
                (
                    str(cell["dataset_id"]),
                    str(cell["horizon_months"]),
                    str(cell["coverage"]),
                    _comparison_label(str(cell["comparison"])),
                    str(cell["sample_count"]),
                    str(cell["observed_statistic"]),
                    f"[{cell['interval_lower']}, {cell['interval_upper']}]",
                    str(cell["holm_adjusted_p_value"]),
                )
            )
            + " |"
        )
    lines.extend(
        (
            "",
            "## Scope boundary",
            "",
            "Confirmatory rows are the registered frictionless H1/H2 cells. Cost-adjusted rows and mechanism summaries remain separately labeled in `historical-aggregates.json` and `historical-figure-ready.csv`; they are not covered by the epsilon-DCA theorem.",
            "",
            f"The aggregate artifact contains {aggregates['group_count']} cells across complete-system, signal-only, and safety-architecture comparisons.",
            "",
        )
    )
    return "\n".join(lines)


def _artifact_record(
    root: Path, relative: str, retention: str
) -> dict[str, Any]:
    path = root / relative
    record: dict[str, Any] = {
        "path": relative,
        "sha256": _file_fingerprint(path),
        "bytes": path.stat().st_size,
        "retention": retention,
    }
    if relative.endswith(".gz"):
        record["content_encoding"] = "gzip"
    return record


def _write_private_artifact_receipt(
    directory: Path, preparation: AcceptedHistoricalPreparation
) -> None:
    generated_private = [
        _artifact_record(directory, path.relative_to(directory).as_posix(), "private-retained")
        for path in sorted(directory.rglob("*"))
        if path.is_file()
        and path.relative_to(directory).as_posix() not in PUBLIC_DERIVED_ARTIFACTS
        and path.relative_to(directory).as_posix() != "manifest.json"
    ]
    receipt = {
        "schema_version": "smartdca-private-artifact-receipt/1",
        "redistribution_boundary": (
            "Yahoo canonical exports, normalized observations, episode schedules, "
            "episode-level outcomes, and price-bearing ledgers remain access-controlled "
            "outside Git; only derived aggregate evidence and cryptographic receipts publish."
        ),
        "accepted_preparation_manifest_sha256": preparation.manifest_sha256,
        "accepted_preparation_artifacts": preparation.manifest["artifacts"],
        "generated_private_artifacts": generated_private,
    }
    _write_json(directory / "private-artifact-receipt.json", receipt)


def _validate_accepted_preparation(
    config_path: Path,
    accepted_manifest_path: Path,
    preparation_directory: Path,
) -> AcceptedHistoricalPreparation:
    accepted_payload = _read_bytes(accepted_manifest_path, "accepted_manifest")
    prepared_payload = _read_bytes(
        preparation_directory / "manifest.json", "preparation.manifest"
    )
    _require(
        prepared_payload == accepted_payload,
        "preparation_manifest_mismatch",
        "preparation.manifest",
        "must match the accepted preparation manifest byte for byte",
    )
    manifest = _decode_document(accepted_payload, "accepted_manifest")
    _require(
        manifest.get("schema_version") == "smartdca-historical-input-manifest/1",
        "unsupported_schema",
        "accepted_manifest.schema_version",
        "must equal smartdca-historical-input-manifest/1",
    )
    _require(
        manifest.get("policy_execution") == "not-run",
        "preparation_outcome_boundary_opened",
        "accepted_manifest.policy_execution",
        "must equal not-run",
    )
    _require(
        _fingerprint(_read_bytes(config_path, "config"))
        == manifest.get("config_sha256"),
        "config_fingerprint_mismatch",
        "config",
        "exact configuration bytes do not match the accepted preparation",
    )
    artifacts = manifest.get("artifacts")
    _require(
        isinstance(artifacts, list),
        "invalid_type",
        "accepted_manifest.artifacts",
        "must be a list",
    )
    artifact_names: set[str] = set()
    for index, artifact in enumerate(artifacts):
        field = f"accepted_manifest.artifacts[{index}]"
        _require(isinstance(artifact, dict), "invalid_type", field, "must be a mapping")
        relative = artifact.get("path")
        expected = artifact.get("sha256")
        _require(
            isinstance(relative, str)
            and relative
            and not PurePosixPath(relative).is_absolute()
            and ".." not in PurePosixPath(relative).parts,
            "invalid_artifact_path",
            f"{field}.path",
            "must be a safe nonempty relative POSIX path",
        )
        _require(
            isinstance(expected, str) and len(expected) == 64,
            "invalid_fingerprint",
            f"{field}.sha256",
            "must be a SHA-256 hexadecimal digest",
        )
        artifact_names.add(relative)
        observed = _fingerprint(
            _read_bytes(preparation_directory / relative, f"preparation.{relative}")
        )
        _require(
            observed == expected,
            "artifact_fingerprint_mismatch",
            f"preparation.{relative}",
            f"expected {expected}, observed {observed}",
        )
    _require(
        REQUIRED_PREPARATION_ARTIFACTS <= artifact_names,
        "incomplete_preparation_manifest",
        "accepted_manifest.artifacts",
        "must inventory every accepted preparation artifact",
    )

    runner_document = _decode_document(
        _read_bytes(preparation_directory / "runner-input.json", "preparation.runner-input"),
        "preparation.runner-input",
    )
    runner_input = VersionedInput.from_mapping(runner_document)
    _require(
        runner_input.sha256 == manifest.get("runner_input_sha256"),
        "runner_input_identity_mismatch",
        "preparation.runner-input",
        "canonical input identity does not match the accepted preparation",
    )
    input_document = runner_input.as_mapping()
    _require(
        input_document["kind"] == "historical" and input_document["confirmatory"] is True,
        "invalid_confirmatory_input",
        "preparation.runner-input",
        "must be a confirmatory historical input",
    )

    validation = _decode_document(
        _read_bytes(preparation_directory / "validation.json", "preparation.validation"),
        "preparation.validation",
    )
    _require(
        validation.get("status") == "passed"
        and validation.get("policy_execution") == "not-run"
        and validation.get("confirmatory_aggregate_outcomes") == "not-computed",
        "invalid_preparation_validation",
        "preparation.validation",
        "must preserve the accepted outcome-blind preparation boundary",
    )
    _require(
        validation.get("runner_input_sha256") == runner_input.sha256,
        "runner_input_identity_mismatch",
        "preparation.validation.runner_input_sha256",
        "must match the accepted canonical input identity",
    )
    reconciliation = _decode_document(
        _read_bytes(
            preparation_directory / "reconciliation.json",
            "preparation.reconciliation",
        ),
        "preparation.reconciliation",
    )
    attempt_lines = [
        line
        for line in _read_bytes(
            preparation_directory / "episode-attempts.jsonl",
            "preparation.episode-attempts",
        ).splitlines()
        if line
    ]
    episode_attempts = tuple(
        _decode_document(line, f"preparation.episode-attempts[{index}]")
        for index, line in enumerate(attempt_lines)
    )
    _require(
        validation.get("reconciliation") == reconciliation,
        "preparation_reconciliation_mismatch",
        "preparation.validation.reconciliation",
        "must match the accepted reconciliation artifact",
    )
    _require(
        all(
            attempt.get("status") in {"included", "excluded"}
            and isinstance(attempt.get("episode_id"), str)
            for attempt in episode_attempts
        ),
        "invalid_episode_attempt",
        "preparation.episode-attempts",
        "each attempt must have an identifier and included or excluded status",
    )
    attempt_ids = [str(attempt["episode_id"]) for attempt in episode_attempts]
    _require(
        len(attempt_ids) == len(set(attempt_ids)),
        "duplicate_episode_attempt",
        "preparation.episode-attempts",
        "episode identifiers must be unique",
    )
    included_attempt_ids = {
        str(attempt["episode_id"])
        for attempt in episode_attempts
        if attempt["status"] == "included"
    }
    input_episode_ids = {
        str(episode["episode_id"]) for episode in input_document["episodes"]
    }
    _require(
        included_attempt_ids == input_episode_ids,
        "preparation_episode_mismatch",
        "preparation.runner-input.episodes",
        "must contain exactly the included preparation attempts",
    )
    actual_included = len(included_attempt_ids)
    actual_excluded = len(episode_attempts) - actual_included
    actual_reasons = dict(
        sorted(
            Counter(
                str(attempt.get("exclusion_reason"))
                for attempt in episode_attempts
                if attempt["status"] == "excluded"
            ).items()
        )
    )
    _require(
        reconciliation.get("attempted_episode_count") == len(attempt_lines),
        "preparation_count_mismatch",
        "preparation.reconciliation.attempted_episode_count",
        "must equal the preserved episode-attempt count",
    )
    _require(
        reconciliation.get("included_episode_count") == actual_included
        and reconciliation.get("excluded_episode_count") == actual_excluded
        and reconciliation.get("exclusion_reasons") == actual_reasons,
        "preparation_count_mismatch",
        "preparation.reconciliation",
        "included, excluded, and reason counts must match preserved attempts",
    )
    _require(
        reconciliation.get("runner_input_episode_count")
        == len(input_document["episodes"]),
        "preparation_count_mismatch",
        "preparation.reconciliation.runner_input_episode_count",
        "must equal the canonical runner-input episode count",
    )
    return AcceptedHistoricalPreparation(
        manifest=manifest,
        manifest_sha256=_fingerprint(accepted_payload),
        runner_input=runner_input,
        reconciliation=reconciliation,
        episode_attempts=episode_attempts,
        attempt_count=len(attempt_lines),
    )


def _study_run_id(
    config_sha256: str, preparation: AcceptedHistoricalPreparation
) -> str:
    identity = _canonical_json(
        {
            "engine_version": STUDY_ENGINE_VERSION,
            "study_sha256": _source_sha256(),
            "runner_engine_version": RUNNER_ENGINE_VERSION,
            "runner_sha256": _runner_source_sha256(),
            "config_sha256": config_sha256,
            "accepted_preparation_manifest_sha256": preparation.manifest_sha256,
            "runner_input_sha256": preparation.runner_input.sha256,
        }
    )
    return f"smartdca-historical-study-v1-{_fingerprint(identity.encode('utf-8'))}"


def run_historical_study_from_paths(
    config_path: Path,
    accepted_manifest_path: Path,
    preparation_directory: Path,
    output_root: Path,
    *,
    publication_root: Path | None = None,
) -> HistoricalStudyBundle:
    """Execute the accepted preparation through the confirmatory study seam."""

    for value, field in (
        (config_path, "config_path"),
        (accepted_manifest_path, "accepted_manifest_path"),
        (preparation_directory, "preparation_directory"),
        (output_root, "output_root"),
    ):
        _require(isinstance(value, Path), "invalid_type", field, "must be pathlib.Path")
    if publication_root is not None:
        _require(
            isinstance(publication_root, Path),
            "invalid_type",
            "publication_root",
            "must be pathlib.Path or None",
        )
        _require(
            publication_root.resolve() != output_root.resolve(),
            "invalid_publication_root",
            "publication_root",
            "must differ from the private output root",
        )
    preparation = _validate_accepted_preparation(
        config_path, accepted_manifest_path, preparation_directory
    )
    config = load_study_config(config_path)
    study_run_id = _study_run_id(config.sha256, preparation)
    final_directory = output_root / study_run_id
    publication_directory = (
        publication_root / study_run_id if publication_root is not None else None
    )
    if final_directory.exists():
        raise RunIdentityCollisionError(
            "run_identity_collision",
            "output_root",
            f"{study_run_id} already exists",
        )
    if publication_directory is not None and publication_directory.exists():
        raise RunIdentityCollisionError(
            "run_identity_collision",
            "publication_root",
            f"{study_run_id} already exists",
        )
    output_root.mkdir(parents=True, exist_ok=True)
    temporary_directory = Path(
        tempfile.mkdtemp(prefix=f".{study_run_id}-", dir=output_root)
    )
    publication_temporary: Path | None = None
    private_finalized = False
    try:
        runner_stage = temporary_directory / "runner-stage"
        runner = run_experiment(config, preparation.runner_input, runner_stage)
        runner_directory = temporary_directory / "runner"
        os.replace(runner.output_directory, runner_directory)
        runner_stage.rmdir()
        config_document = config.as_mapping()
        input_document = preparation.runner_input.as_mapping()
        with localcontext() as context:
            context.prec = 60
            context.rounding = ROUND_HALF_EVEN
            aggregates = _aggregate_historical_results(
                config.as_mapping(),
                runner.episode_results,
                preparation.episode_attempts,
            )
            uncertainty, bootstrap_replicates = _confirmatory_uncertainty(
                config.as_mapping(), input_document, runner.episode_results
            )
            _attach_uncertainty(aggregates, uncertainty)
        _write_json(
            temporary_directory / "historical-aggregates.json", aggregates
        )
        _write_json(temporary_directory / "uncertainty.json", uncertainty)
        _write_jsonl(
            temporary_directory / "bootstrap-replicates.jsonl",
            bootstrap_replicates,
        )
        aggregate_reconciliation = reconcile_historical_aggregates(
            aggregates, runner.aggregates
        )
        _write_json(
            temporary_directory / "aggregate-reconciliation.json",
            aggregate_reconciliation,
        )
        sample_reconciliation = {
            "source_observation_count": preparation.reconciliation[
                "observation_count"
            ],
            "attempted_episode_count": preparation.reconciliation[
                "attempted_episode_count"
            ],
            "included_episode_count": preparation.reconciliation[
                "included_episode_count"
            ],
            "excluded_episode_count": preparation.reconciliation[
                "excluded_episode_count"
            ],
            "runner_episode_count": runner.aggregates["episode_count"],
            "runner_comparison_count": runner.aggregates["comparison_count"],
            "confirmatory_uncertainty_cell_count": uncertainty["cell_count"],
        }
        _require(
            sample_reconciliation["included_episode_count"]
            == sample_reconciliation["runner_episode_count"],
            "sample_reconciliation_mismatch",
            "study_validation.sample_reconciliation",
            "included preparation episodes must equal runner episodes",
        )
        _require(
            all(check["status"] == "passed" for check in runner.validation["checks"]),
            "runner_validation_failure",
            "runner.validation.checks",
            "every shared-runner invariant must pass",
        )
        validation: dict[str, Any] = {
            "status": "passed",
            "accepted_preparation": {
                "manifest_sha256": preparation.manifest_sha256,
                "runner_input_sha256": preparation.runner_input.sha256,
                "policy_execution_before_run": "not-run",
            },
            "sample_reconciliation": sample_reconciliation,
            "aggregate_reconciliation": aggregate_reconciliation,
            "uncertainty_validation": {
                "method": uncertainty["method"],
                "replicates": uncertainty["replicates"],
                "base_seed": uncertainty["base_seed"],
                "cell_count": uncertainty["cell_count"],
                "holm_family_size": uncertainty["cell_count"],
            },
            "protocol_violations": [],
            "deviations": [],
            "shared_runner_validation": runner.validation,
        }
        _write_json(
            temporary_directory / "study-validation.json", validation
        )
        _write_csv(
            temporary_directory / "historical-figure-ready.csv",
            [dict(group) for group in aggregates["groups"]],
        )
        (temporary_directory / "report-tables.md").write_text(
            _render_report_tables(aggregates, uncertainty),
            encoding="utf-8",
            newline="\n",
        )
        shutil.copyfile(
            accepted_manifest_path,
            temporary_directory / "accepted-preparation-manifest.json",
        )
        packaged_runner_manifest = _package_runner_ledgers(runner_directory)
        _gzip_artifact(temporary_directory / "bootstrap-replicates.jsonl")
        _write_private_artifact_receipt(temporary_directory, preparation)
        artifact_paths = sorted(
            path for path in temporary_directory.rglob("*") if path.is_file()
        )
        artifacts = [
            _artifact_record(
                temporary_directory,
                path.relative_to(temporary_directory).as_posix(),
                (
                    "public-derived"
                    if path.relative_to(temporary_directory).as_posix()
                    in PUBLIC_DERIVED_ARTIFACTS
                    else "private-retained"
                ),
            )
            for path in artifact_paths
            if path.relative_to(temporary_directory).as_posix() != "manifest.json"
        ]
        manifest: dict[str, Any] = {
            "schema_version": "smartdca-historical-study-manifest/1",
            "study_run_id": study_run_id,
            "engine_version": STUDY_ENGINE_VERSION,
            "study_sha256": _source_sha256(),
            "runner_engine_version": RUNNER_ENGINE_VERSION,
            "runner_sha256": _runner_source_sha256(),
            "config_sha256": config.sha256,
            "protocol_id": config_document["protocol_id"],
            "accepted_preparation_manifest_sha256": preparation.manifest_sha256,
            "accepted_preparation_run_id": preparation.manifest["run_id"],
            "runner_input_sha256": preparation.runner_input.sha256,
            "runner_run_id": runner.run_id,
            "attempted_episode_count": preparation.attempt_count,
            "included_episode_count": len(input_document["episodes"]),
            "aggregate_group_count": aggregates["group_count"],
            "confirmatory_uncertainty_cell_count": uncertainty["cell_count"],
            "runtime": {
                "implementation": "CPython",
                "python": f"{sys.version_info.major}.{sys.version_info.minor}",
                "third_party": [],
            },
            "execution_grid": {
                "datasets": sorted(
                    {episode["dataset_id"] for episode in input_document["episodes"]}
                ),
                "horizons_months": sorted(
                    {episode["horizon_months"] for episode in input_document["episodes"]}
                ),
                "coverage": config_document["coverage"]["primary"],
                "corrected_mean_configurations": [
                    value["config_id"]
                    for value in config_document["corrected_mean"]["primary"]
                ],
                "cost_scenarios": [
                    value["cost_id"] for value in config_document["cost_scenarios"]
                ],
                "policies": sorted({ledger["policy"] for ledger in runner.ledgers}),
                "comparisons": sorted(
                    {result["comparison"] for result in runner.episode_results}
                ),
            },
            "reproduction": {
                "module": "reproducibility.historical_study",
                "config": f"experiments/protocols/{config_document['protocol_id']}.json",
                "accepted_preparation_manifest": "<accepted-preparation-manifest-path>",
                "preparation_directory": "<private-accepted-preparation-directory>",
                "output_root": "<new-empty-private-output-root>",
                "publication_root": "<new-empty-publication-root-or-omit>",
            },
            "retention": {
                "private": "complete source-bearing and episode-level run outside Git",
                "public": "derived aggregates, uncertainty, validations, tables, and receipts",
                "public_artifacts": sorted(PUBLIC_DERIVED_ARTIFACTS),
            },
            "artifacts": artifacts,
        }
        _write_json(temporary_directory / "manifest.json", manifest)
        if publication_directory is not None:
            assert publication_root is not None
            publication_root.mkdir(parents=True, exist_ok=True)
            publication_temporary = Path(
                tempfile.mkdtemp(prefix=f".{study_run_id}-", dir=publication_root)
            )
            for relative in sorted(PUBLIC_DERIVED_ARTIFACTS):
                shutil.copyfile(
                    temporary_directory / relative,
                    publication_temporary / relative,
                )
            shutil.copyfile(
                temporary_directory / "manifest.json",
                publication_temporary / "manifest.json",
            )
        os.replace(temporary_directory, final_directory)
        private_finalized = True
        if publication_directory is not None:
            assert publication_temporary is not None
            os.replace(publication_temporary, publication_directory)
    except BaseException:
        shutil.rmtree(temporary_directory, ignore_errors=True)
        if publication_temporary is not None:
            shutil.rmtree(publication_temporary, ignore_errors=True)
        if private_finalized and publication_directory is not None:
            shutil.rmtree(final_directory, ignore_errors=True)
        raise
    relocated_runner = RunBundle(
        run_id=runner.run_id,
        output_directory=final_directory / "runner",
        manifest=packaged_runner_manifest,
        ledgers=runner.ledgers,
        episode_results=runner.episode_results,
        aggregates=runner.aggregates,
        validation=runner.validation,
    )
    return HistoricalStudyBundle(
        study_run_id=study_run_id,
        output_directory=final_directory,
        publication_directory=publication_directory,
        manifest=manifest,
        aggregates=aggregates,
        uncertainty=uncertainty,
        validation=validation,
        runner=relocated_runner,
    )


def main(argv: list[str] | None = None) -> int:
    """Run one accepted confirmatory historical evaluation."""

    parser = argparse.ArgumentParser(
        description="Execute the frozen SmartDCA confirmatory historical study."
    )
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument(
        "--accepted-preparation-manifest", required=True, type=Path
    )
    parser.add_argument("--preparation-directory", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--publication-root", type=Path)
    arguments = parser.parse_args(argv)
    try:
        bundle = run_historical_study_from_paths(
            arguments.config,
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
                "study_run_id": bundle.study_run_id,
                "output_directory": str(bundle.output_directory.resolve()),
                "manifest": str(
                    (bundle.output_directory / "manifest.json").resolve()
                ),
                "publication_manifest": (
                    str((bundle.publication_directory / "manifest.json").resolve())
                    if bundle.publication_directory is not None
                    else None
                ),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
