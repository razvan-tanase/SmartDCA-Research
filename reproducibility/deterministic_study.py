"""Deterministic path-study orchestration over the shared empirical runner."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from itertools import product
from pathlib import Path
from typing import Any, Mapping

from reproducibility.empirical import (
    ExperimentValidationError,
    RunBundle,
    RunIdentityCollisionError,
    StudyConfig,
    VersionedInput,
    load_study_config,
    run_experiment,
)


STUDY_ENGINE_VERSION = "smartdca-deterministic-study/1"
GENERATOR_VERSION = "smartdca-deterministic-paths/1"
SHARED_RUNNER_SOURCE = Path(__file__).with_name("empirical.py")


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


def _runner_source_sha256() -> str:
    return _fingerprint(SHARED_RUNNER_SOURCE.read_bytes())


def _require(condition: bool, code: str, field: str, message: str) -> None:
    if not condition:
        raise ExperimentValidationError(code, field, message)


def _mapping_copy(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    _require(isinstance(value, Mapping), "invalid_type", field, "must be a mapping")
    try:
        return json.loads(_canonical_json(value))
    except (TypeError, ValueError) as error:
        raise ExperimentValidationError(
            "invalid_json_value",
            field,
            "must contain only finite JSON values",
        ) from error


def _decode_json_document(payload: bytes, field: str) -> dict[str, Any]:
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
            "invalid_json",
            field,
            "must be one duplicate-free finite JSON document",
        ) from error
    _require(isinstance(value, dict), "invalid_type", field, "must be a JSON object")
    return value


def _decimal(value: Any, field: str) -> Decimal:
    _require(
        isinstance(value, (str, int)) and not isinstance(value, bool),
        "invalid_decimal",
        field,
        "must be an integer or decimal string",
    )
    try:
        parsed = Decimal(str(value))
    except Exception as error:
        raise ExperimentValidationError(
            "invalid_decimal", field, "must be a finite decimal"
        ) from error
    _require(parsed.is_finite(), "invalid_decimal", field, "must be finite")
    return parsed


def _date(value: Any, field: str) -> date:
    _require(isinstance(value, str), "invalid_date", field, "must be an ISO date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ExperimentValidationError(
            "invalid_date", field, "must be a real YYYY-MM-DD date"
        ) from error
    _require(parsed.isoformat() == value, "invalid_date", field, "must use YYYY-MM-DD")
    return parsed


def _next_month(value: date) -> date:
    year = value.year + (1 if value.month == 12 else 0)
    month = 1 if value.month == 12 else value.month + 1
    return date(year, month, value.day)


def _validate_study(document: dict[str, Any]) -> None:
    _require(
        document.get("schema_version") == STUDY_ENGINE_VERSION,
        "unsupported_schema",
        "study.schema_version",
        f"must equal {STUDY_ENGINE_VERSION}",
    )
    for field in (
        "study_id",
        "version",
        "input_id",
        "input_version",
        "generator_version",
        "confirmatory",
        "seed",
        "deposit",
        "start_date",
        "required_families",
        "required_boundary_fixtures",
        "attempts",
    ):
        _require(field in document, "missing_field", f"study.{field}", "is required")
    for field in ("study_id", "version", "input_id", "input_version"):
        _require(
            isinstance(document[field], str) and bool(document[field]),
            "invalid_identifier",
            f"study.{field}",
            "must be a nonempty string",
        )
    _require(
        document["generator_version"] == GENERATOR_VERSION,
        "unsupported_generator",
        "study.generator_version",
        f"must equal {GENERATOR_VERSION}",
    )
    _require(
        document["confirmatory"] is False,
        "invalid_study_scope",
        "study.confirmatory",
        "deterministic study must be non-confirmatory",
    )
    _require(
        document["seed"] is None,
        "invalid_seed",
        "study.seed",
        "deterministic enumeration must record a null seed",
    )
    _require(
        _decimal(document["deposit"], "study.deposit") >= 0,
        "invalid_deposit",
        "study.deposit",
        "must be nonnegative",
    )
    _date(document["start_date"], "study.start_date")
    for field in ("required_families", "required_boundary_fixtures", "attempts"):
        _require(
            isinstance(document[field], list) and bool(document[field]),
            "empty_study_grid",
            f"study.{field}",
            "must be a nonempty list",
        )
    attempt_ids: list[str] = []
    for index, attempt in enumerate(document["attempts"]):
        prefix = f"study.attempts[{index}]"
        _require(isinstance(attempt, dict), "invalid_type", prefix, "must be a mapping")
        for field in (
            "attempt_id",
            "family",
            "predicate",
            "parameters",
            "boundary_fixtures",
            "mechanisms",
        ):
            _require(field in attempt, "missing_field", f"{prefix}.{field}", "is required")
        for field in ("attempt_id", "family", "predicate"):
            _require(
                isinstance(attempt[field], str) and bool(attempt[field]),
                "invalid_identifier",
                f"{prefix}.{field}",
                "must be a nonempty string",
            )
        attempt_ids.append(attempt["attempt_id"])
        _require(
            isinstance(attempt["parameters"], dict),
            "invalid_type",
            f"{prefix}.parameters",
            "must be a mapping",
        )
        for field in ("boundary_fixtures", "mechanisms"):
            _require(
                isinstance(attempt[field], list),
                "invalid_type",
                f"{prefix}.{field}",
                "must be a list",
            )
    _require(
        len(attempt_ids) == len(set(attempt_ids)),
        "duplicate_attempt_id",
        "study.attempts",
        "attempt_id values must be unique",
    )
    search = document.get("adversarial_design_search")
    if search is not None:
        _require(
            isinstance(search, dict),
            "invalid_type",
            "study.adversarial_design_search",
            "must be a mapping",
        )
        for field in (
            "search_id",
            "price_grid",
            "purchase_count",
            "evaluation_price",
            "minimum_direction_changes",
            "coverage",
            "corrected_mean_config",
            "cost_scenario",
            "comparison",
            "objective",
            "tie_break",
            "selected_attempt_id",
        ):
            _require(
                field in search,
                "missing_field",
                f"study.adversarial_design_search.{field}",
                "is required",
            )
        _require(
            isinstance(search["search_id"], str) and bool(search["search_id"]),
            "invalid_identifier",
            "study.adversarial_design_search.search_id",
            "must be a nonempty string",
        )
        grid = search["price_grid"]
        _require(
            isinstance(grid, list) and len(grid) >= 2,
            "invalid_search_grid",
            "study.adversarial_design_search.price_grid",
            "must contain at least two prices",
        )
        parsed_grid = [
            _decimal(
                value,
                f"study.adversarial_design_search.price_grid[{index}]",
            )
            for index, value in enumerate(grid)
        ]
        _require(
            all(value > 0 for value in parsed_grid)
            and len(parsed_grid) == len(set(parsed_grid)),
            "invalid_search_grid",
            "study.adversarial_design_search.price_grid",
            "prices must be positive and unique",
        )
        for field, minimum in (("purchase_count", 3), ("minimum_direction_changes", 2)):
            _require(
                isinstance(search[field], int)
                and not isinstance(search[field], bool)
                and search[field] >= minimum,
                "invalid_search_parameter",
                f"study.adversarial_design_search.{field}",
                f"must be an integer at least {minimum}",
            )
        _require(
            _decimal(
                search["evaluation_price"],
                "study.adversarial_design_search.evaluation_price",
            )
            > 0,
            "invalid_evaluation_price",
            "study.adversarial_design_search.evaluation_price",
            "must be positive",
        )
        _require(
            search["comparison"] == "corrected_guarded_vs_neutral_guarded"
            and search["objective"] == "minimize_relative_terminal_wealth_gap"
            and search["tie_break"] == "lexicographic_price_sequence",
            "unsupported_search_rule",
            "study.adversarial_design_search",
            "must use the registered signal-downside objective and tie break",
        )
        _require(
            search["selected_attempt_id"] in attempt_ids,
            "unknown_selected_attempt",
            "study.adversarial_design_search.selected_attempt_id",
            "must identify a saved attempt",
        )
    contracts = document.get("boundary_contracts", [])
    _require(
        isinstance(contracts, list),
        "invalid_type",
        "study.boundary_contracts",
        "must be a list",
    )
    contract_ids: list[str] = []
    contract_fixtures: set[str] = set()
    for index, contract in enumerate(contracts):
        prefix = f"study.boundary_contracts[{index}]"
        _require(
            isinstance(contract, dict),
            "invalid_type",
            prefix,
            "must be a mapping",
        )
        for field in (
            "contract_id",
            "fixture",
            "source_check",
            "target",
            "episode_id",
            "coverage",
            "corrected_mean_config",
            "cost_scenario",
            "expected",
        ):
            _require(
                field in contract,
                "missing_field",
                f"{prefix}.{field}",
                "is required",
            )
        for field in (
            "contract_id",
            "fixture",
            "source_check",
            "target",
            "episode_id",
            "coverage",
            "corrected_mean_config",
            "cost_scenario",
        ):
            _require(
                isinstance(contract[field], str) and bool(contract[field]),
                "invalid_identifier",
                f"{prefix}.{field}",
                "must be a nonempty string",
            )
        _require(
            contract["source_check"].startswith("reproducibility/checks/"),
            "invalid_boundary_source",
            f"{prefix}.source_check",
            "must identify an executable repository check",
        )
        _require(
            contract["fixture"] in document["required_boundary_fixtures"],
            "unknown_boundary_fixture",
            f"{prefix}.fixture",
            "must name a required boundary fixture",
        )
        _require(
            contract["episode_id"] in attempt_ids,
            "unknown_boundary_episode",
            f"{prefix}.episode_id",
            "must identify a saved attempt",
        )
        _require(
            contract["target"] in {"episode-result", "policy-ledger"},
            "unsupported_boundary_target",
            f"{prefix}.target",
            "must be episode-result or policy-ledger",
        )
        expected = contract["expected"]
        _require(
            isinstance(expected, dict) and bool(expected),
            "invalid_boundary_expectation",
            f"{prefix}.expected",
            "must be a nonempty mapping",
        )
        if contract["target"] == "episode-result":
            _require(
                isinstance(contract.get("comparison"), str)
                and bool(contract["comparison"]),
                "missing_field",
                f"{prefix}.comparison",
                "is required for an episode-result contract",
            )
            _require(
                all(isinstance(value, str) for value in expected.values()),
                "invalid_boundary_expectation",
                f"{prefix}.expected",
                "episode-result expected values must be strings",
            )
        else:
            _require(
                isinstance(contract.get("policy"), str)
                and bool(contract["policy"]),
                "missing_field",
                f"{prefix}.policy",
                "is required for a policy-ledger contract",
            )
            _require(
                set(expected) == {"guardrail_floors"}
                and isinstance(expected["guardrail_floors"], list)
                and all(
                    isinstance(value, str)
                    for value in expected["guardrail_floors"]
                ),
                "invalid_boundary_expectation",
                f"{prefix}.expected",
                "policy-ledger contracts must declare string guardrail floors",
            )
        contract_ids.append(contract["contract_id"])
        contract_fixtures.add(contract["fixture"])
    _require(
        len(contract_ids) == len(set(contract_ids)),
        "duplicate_boundary_contract",
        "study.boundary_contracts",
        "contract_id values must be unique",
    )
    if contracts:
        _require(
            set(document["required_boundary_fixtures"]) <= contract_fixtures,
            "missing_boundary_contract",
            "study.boundary_contracts",
            "every required boundary fixture must have an executable contract",
        )


@dataclass(frozen=True)
class DeterministicStudy:
    """Validated immutable deterministic-path study specification."""

    canonical_document: str
    sha256: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "DeterministicStudy":
        document = _mapping_copy(value, "study")
        _validate_study(document)
        canonical = _canonical_json(document)
        return cls(canonical, _fingerprint(canonical.encode("utf-8")))

    @classmethod
    def from_json_bytes(cls, payload: bytes) -> "DeterministicStudy":
        document = _decode_json_document(payload, "study")
        _validate_study(document)
        return cls(_canonical_json(document), _fingerprint(payload))

    def as_mapping(self) -> dict[str, Any]:
        return json.loads(self.canonical_document)


def load_deterministic_study(path: Path) -> DeterministicStudy:
    """Load a versioned deterministic study and fingerprint its exact bytes."""
    _require(
        isinstance(path, Path),
        "invalid_type",
        "study_path",
        "must be pathlib.Path",
    )
    try:
        payload = path.read_bytes()
    except OSError as error:
        raise ExperimentValidationError(
            "unreadable_study", "study_path", str(error)
        ) from error
    return DeterministicStudy.from_json_bytes(payload)


@dataclass(frozen=True)
class DeterministicStudyBundle:
    """Public result of one immutable deterministic path study."""

    study_run_id: str
    output_directory: Path
    manifest: Mapping[str, Any]
    path_attempts: tuple[Mapping[str, Any], ...]
    runner: RunBundle


def _valley_index(prices: list[Decimal], *, strict: bool) -> int | None:
    for index in range(1, len(prices) - 1):
        left_pairs = list(zip(prices[:index], prices[1 : index + 1], strict=True))
        right_pairs = list(zip(prices[index:-1], prices[index + 1 :], strict=True))
        if strict:
            left = all(right < left for left, right in left_pairs)
            right = all(right > left for left, right in right_pairs)
        else:
            left = all(right <= left for left, right in left_pairs)
            right = all(right >= left for left, right in right_pairs)
        if (
            left
            and right
            and any(right < left for left, right in left_pairs)
            and any(right > left for left, right in right_pairs)
        ):
            return index
    return None


def _strict_peak_index(prices: list[Decimal]) -> int | None:
    for index in range(1, len(prices) - 1):
        if all(
            right > left
            for left, right in zip(prices[:index], prices[1 : index + 1], strict=True)
        ) and all(
            right < left
            for left, right in zip(prices[index:-1], prices[index + 1 :], strict=True)
        ):
            return index
    return None


def _direction_changes(prices: list[Decimal]) -> int:
    signs = []
    for left, right in zip(prices, prices[1:]):
        difference = right - left
        if difference != 0:
            signs.append(1 if difference > 0 else -1)
    return sum(left != right for left, right in zip(signs, signs[1:]))


def _maximum_flat_run(prices: list[Decimal]) -> int:
    maximum = 1
    current = 1
    for left, right in zip(prices, prices[1:]):
        current = current + 1 if right == left else 1
        maximum = max(maximum, current)
    return maximum


def _maximum_drawdown_fraction(prices: list[Decimal]) -> Decimal:
    peak = prices[0]
    worst = Decimal("1")
    for price in prices:
        peak = max(peak, price)
        worst = min(worst, price / peak)
    return worst


def _longest_drawdown(prices: list[Decimal]) -> int:
    peak = prices[0]
    current = 0
    longest = 0
    for price in prices[1:]:
        if price >= peak:
            peak = price
            current = 0
        else:
            current += 1
            longest = max(longest, current)
    return longest


def _predicate_receipt(
    predicate: str,
    prices: list[Decimal],
    evaluation_price: Decimal,
    parameters: Mapping[str, Any],
) -> dict[str, Any]:
    strict_valley = _valley_index(prices, strict=True)
    weak_valley = _valley_index(prices, strict=False)
    strict_peak = _strict_peak_index(prices)
    local_valleys = sum(
        prices[index] < prices[index - 1] and prices[index] < prices[index + 1]
        for index in range(1, len(prices) - 1)
    )
    direction_changes = _direction_changes(prices)
    flat_run = _maximum_flat_run(prices)
    drawdown_fraction = _maximum_drawdown_fraction(prices)
    longest_drawdown = _longest_drawdown(prices)
    details: dict[str, Any] = {
        "purchase_count": len(prices),
        "distinct_purchase_prices": len(set(prices)),
        "minimum_price": str(min(prices)),
        "maximum_price": str(max(prices)),
        "evaluation_price": str(evaluation_price),
        "weak_valley_index": weak_valley,
        "strict_valley_index": strict_valley,
        "strict_peak_index": strict_peak,
        "strict_local_valley_count": local_valleys,
        "direction_change_count": direction_changes,
        "maximum_flat_run": flat_run,
        "minimum_peak_fraction": str(drawdown_fraction),
        "longest_drawdown_periods": longest_drawdown,
    }
    if predicate == "constant":
        passed = all(value == prices[0] for value in prices)
    elif predicate == "monotone-rise":
        passed = all(right > left for left, right in zip(prices, prices[1:]))
    elif predicate == "monotone-decline":
        passed = all(right < left for left, right in zip(prices, prices[1:]))
    elif predicate == "weak-single-valley":
        passed = weak_valley is not None
    elif predicate == "strict-single-valley":
        passed = strict_valley is not None
    elif predicate == "strict-single-peak":
        passed = strict_peak is not None
    elif predicate == "incomplete-recovery":
        passed = weak_valley is not None and min(prices) < prices[-1] < prices[0] and evaluation_price < prices[0]
    elif predicate == "completed-recovery":
        passed = weak_valley is not None and prices[-1] >= prices[0] and evaluation_price >= prices[0]
    elif predicate == "multiple-valleys":
        required = parameters.get("minimum_valley_count", 2)
        passed = (
            isinstance(required, int)
            and not isinstance(required, bool)
            and required >= 2
            and local_valleys >= required
        )
        details["required_local_valley_count"] = required
    elif predicate == "crash":
        threshold = _decimal(
            parameters.get("maximum_peak_fraction"),
            "attempt.parameters.maximum_peak_fraction",
        )
        passed = Decimal("0") < threshold < Decimal("1") and drawdown_fraction <= threshold
        details["required_maximum_peak_fraction"] = str(threshold)
    elif predicate == "sudden-rebound":
        threshold = _decimal(
            parameters.get("minimum_rebound_ratio"),
            "attempt.parameters.minimum_rebound_ratio",
        )
        rebound_ratios = [
            right / left for left, right in zip(prices, prices[1:])
        ]
        passed = (
            threshold > Decimal("1")
            and min(prices[:-1]) < prices[0]
            and max(rebound_ratios) >= threshold
        )
        details["maximum_one_period_rebound_ratio"] = str(max(rebound_ratios))
        details["required_minimum_rebound_ratio"] = str(threshold)
    elif predicate == "prolonged-drawdown":
        required = parameters.get("minimum_periods_below_peak")
        passed = (
            isinstance(required, int)
            and not isinstance(required, bool)
            and required > 0
            and longest_drawdown >= required
        )
        details["required_drawdown_periods"] = required
    elif predicate == "flat-segments":
        required = parameters.get("minimum_flat_run")
        passed = (
            isinstance(required, int)
            and not isinstance(required, bool)
            and required >= 2
            and flat_run >= required
        )
        details["required_flat_run"] = required
    elif predicate == "hostile-carried-cash":
        passed = (
            all(right > left for left, right in zip(prices, prices[1:]))
            and evaluation_price > prices[-1]
        )
    elif predicate == "hostile-adaptive-timing":
        required = parameters.get("minimum_direction_changes")
        passed = (
            isinstance(required, int)
            and not isinstance(required, bool)
            and required >= 2
            and direction_changes >= required
            and evaluation_price < min(prices)
        )
        details["required_direction_changes"] = required
    else:
        raise ExperimentValidationError(
            "unsupported_path_predicate",
            "attempt.predicate",
            f"{predicate} is not registered",
        )
    return {
        "status": "passed" if passed else "failed",
        "details": details,
    }


def _attempt_metadata(attempt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        field: attempt[field]
        for field in (
            "attempt_id",
            "family",
            "predicate",
            "parameters",
            "boundary_fixtures",
            "mechanisms",
        )
    }


def _generate_attempt(
    attempt: Mapping[str, Any],
    *,
    deposit: str,
    start_date: date,
) -> tuple[dict[str, Any], dict[str, Any]]:
    parameters = attempt["parameters"]
    prices_raw = parameters.get("prices")
    _require(
        isinstance(prices_raw, list) and bool(prices_raw),
        "invalid_path_parameters",
        f"attempt.{attempt['attempt_id']}.parameters.prices",
        "must be a nonempty list",
    )
    prices = [
        _decimal(value, f"attempt.{attempt['attempt_id']}.parameters.prices[{index}]")
        for index, value in enumerate(prices_raw)
    ]
    _require(
        all(value > 0 for value in prices),
        "invalid_price",
        f"attempt.{attempt['attempt_id']}.parameters.prices",
        "prices must be positive",
    )
    evaluation_price = _decimal(
        parameters.get("evaluation_price"),
        f"attempt.{attempt['attempt_id']}.parameters.evaluation_price",
    )
    _require(
        evaluation_price > 0,
        "invalid_evaluation_price",
        f"attempt.{attempt['attempt_id']}.parameters.evaluation_price",
        "must be positive",
    )
    receipt = _predicate_receipt(
        attempt["predicate"], prices, evaluation_price, parameters
    )
    _require(
        receipt["status"] == "passed",
        "path_predicate_failed",
        f"attempt.{attempt['attempt_id']}.predicate",
        f"generated prices do not satisfy {attempt['predicate']}",
    )

    observations = []
    current = start_date
    for price in prices:
        observations.append(
            {
                "date": current.isoformat(),
                "price": str(price),
                "deposit": deposit,
            }
        )
        current = _next_month(current)
    episode = {
        "episode_id": attempt["attempt_id"],
        "family": attempt["family"],
        "dataset_id": "deterministic-adversarial-v1",
        "horizon_months": len(observations),
        "observations": observations,
        "evaluation_date": current.isoformat(),
        "evaluation_price": str(evaluation_price),
        "generation": {
            "generator_version": GENERATOR_VERSION,
            "predicate": attempt["predicate"],
            "parameters": parameters,
            "predicate_receipt": receipt,
            "boundary_fixtures": attempt["boundary_fixtures"],
            "mechanisms": attempt["mechanisms"],
        },
    }
    attempt_receipt = {
        **_attempt_metadata(attempt),
        "status": "generated",
        "exclusion_reason": None,
        "predicate_status": receipt["status"],
        "predicate_details": receipt["details"],
        "episode_id": episode["episode_id"],
    }
    return episode, attempt_receipt


def _write_json(path: Path, value: Any) -> None:
    path.write_text(_canonical_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: tuple[Mapping[str, Any], ...]) -> None:
    path.write_text(
        "".join(_canonical_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def _write_mechanism_attribution(
    path: Path,
    rows: tuple[Mapping[str, Any], ...],
    receipts: tuple[Mapping[str, Any], ...],
) -> None:
    receipt_by_episode = {
        row["episode_id"]: row for row in receipts if row["status"] == "generated"
    }
    fields = [
        "episode_id",
        "family",
        "coverage",
        "cost_scenario",
        "comparison",
        "theorem_scope",
        "terminal_wealth_gap",
        "relative_terminal_wealth_gap",
        "terminal_cash_gap",
        "terminal_unit_gap",
        "cash_contribution",
        "unit_contribution",
        "left_cash_drag",
        "right_cash_drag",
        "left_asset_exposure",
        "right_asset_exposure",
        "left_guardrail_activation_frequency",
        "right_guardrail_activation_frequency",
        "left_purchase_count",
        "right_purchase_count",
        "mechanisms",
        "boundary_fixtures",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            receipt = receipt_by_episode[row["episode_id"]]
            writer.writerow(
                {
                    **{field: row.get(field) for field in fields},
                    "mechanisms": "|".join(receipt["mechanisms"]),
                    "boundary_fixtures": "|".join(receipt["boundary_fixtures"]),
                }
            )


def _evaluate_boundary_contracts(
    document: Mapping[str, Any],
    runner: RunBundle,
) -> tuple[dict[str, Any], ...]:
    receipts: list[dict[str, Any]] = []
    for contract in document.get("boundary_contracts", []):
        common = (
            ("episode_id", contract["episode_id"]),
            ("coverage", contract["coverage"]),
            ("corrected_mean_config", contract["corrected_mean_config"]),
            ("cost_scenario", contract["cost_scenario"]),
        )
        if contract["target"] == "episode-result":
            matches = [
                row
                for row in runner.episode_results
                if all(row[field] == value for field, value in common)
                and row["comparison"] == contract["comparison"]
                and row["result_status"] == "included"
            ]
            _require(
                len(matches) == 1,
                "boundary_regression_missing",
                f"study.boundary_contracts.{contract['contract_id']}",
                "must identify exactly one included episode result",
            )
            result = matches[0]
            _require(
                all(field in result for field in contract["expected"]),
                "unknown_boundary_metric",
                f"study.boundary_contracts.{contract['contract_id']}.expected",
                "must name emitted episode-result fields",
            )
            observed = {
                field: result[field] for field in contract["expected"]
            }
        else:
            matches = [
                row
                for row in runner.ledgers
                if all(row[field] == value for field, value in common)
                and row["policy"] == contract["policy"]
            ]
            _require(
                len(matches) == 1,
                "boundary_regression_missing",
                f"study.boundary_contracts.{contract['contract_id']}",
                "must identify exactly one policy ledger",
            )
            observed = {
                "guardrail_floors": [
                    step["guardrail_floor"] for step in matches[0]["steps"]
                ]
            }
        _require(
            observed == contract["expected"],
            "boundary_regression_failed",
            f"study.boundary_contracts.{contract['contract_id']}",
            f"observed {observed!r}; expected {contract['expected']!r}",
        )
        receipts.append(
            {
                **contract,
                "observed": observed,
                "status": "passed",
            }
        )
    return tuple(receipts)


def _signed_percent(value: Any) -> str:
    percentage = _decimal(value, "report.relative_terminal_wealth_gap") * 100
    if percentage == 0:
        return "0.000%"
    return f"{percentage:+.3f}%"


def _unsigned_percent(value: Any, places: int = 1) -> str:
    percentage = _decimal(value, "report.rate") * 100
    return f"{percentage:.{places}f}%"


def _render_report_tables(
    config_document: Mapping[str, Any],
    study_document: Mapping[str, Any],
    rows: tuple[Mapping[str, Any], ...],
    receipts: tuple[Mapping[str, Any], ...],
) -> str:
    primary_config = config_document["corrected_mean"]["primary"][0]["config_id"]
    primary_coverage = config_document["coverage"]["primary"]
    featured_coverage = (
        study_document.get("adversarial_design_search", {}).get("coverage")
        or next(value for value in primary_coverage if value != "1")
    )
    generated_by_family = {
        receipt["family"]: receipt
        for receipt in receipts
        if receipt["status"] == "generated"
        and receipt["family"] in study_document["required_families"]
    }

    def select(
        *,
        episode_id: str | None = None,
        coverage: str,
        cost_scenario: str,
        comparison: str,
    ) -> list[Mapping[str, Any]]:
        return [
            row
            for row in rows
            if (episode_id is None or row["episode_id"] == episode_id)
            and row["coverage"] == coverage
            and row["corrected_mean_config"] == primary_config
            and row["cost_scenario"] == cost_scenario
            and row["comparison"] == comparison
            and row["result_status"] == "included"
        ]

    lines = [
        "### Primary family table",
        "",
        "| Family | Complete system: corrected vs DCA | Signal only: corrected vs neutral | Safety architecture: neutral vs DCA | Corrected cash drag | Corrected asset exposure | Floor activation |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for family in study_document["required_families"]:
        receipt = generated_by_family[family]
        episode_id = receipt["episode_id"]
        complete = select(
            episode_id=episode_id,
            coverage=featured_coverage,
            cost_scenario="frictionless",
            comparison="corrected_guarded_vs_dca",
        )
        signal = select(
            episode_id=episode_id,
            coverage=featured_coverage,
            cost_scenario="frictionless",
            comparison="corrected_guarded_vs_neutral_guarded",
        )
        architecture = select(
            episode_id=episode_id,
            coverage=featured_coverage,
            cost_scenario="frictionless",
            comparison="neutral_guarded_vs_dca",
        )
        _require(
            len(complete) == len(signal) == len(architecture) == 1,
            "incomplete_report_table",
            f"report.primary.{family}",
            "must have one included row for every comparison",
        )
        left = complete[0]
        lines.append(
            "| "
            + " | ".join(
                (
                    family.replace("-", " ").capitalize(),
                    _signed_percent(complete[0]["relative_terminal_wealth_gap"]),
                    _signed_percent(signal[0]["relative_terminal_wealth_gap"]),
                    _signed_percent(
                        architecture[0]["relative_terminal_wealth_gap"]
                    ),
                    _unsigned_percent(left["left_cash_drag"]),
                    _unsigned_percent(left["left_asset_exposure"]),
                    _unsigned_percent(
                        left["left_guardrail_activation_frequency"]
                    ),
                )
            )
            + " |"
        )

    comparison_labels = {
        "corrected_guarded_vs_dca": "Corrected vs DCA",
        "corrected_guarded_vs_neutral_guarded": "Corrected vs neutral",
        "neutral_guarded_vs_dca": "Neutral vs DCA",
    }
    comparison_order = tuple(comparison_labels)

    def range_line(
        group_rows: list[Mapping[str, Any]],
    ) -> tuple[str, str, str]:
        values = [
            _decimal(
                row["relative_terminal_wealth_gap"],
                "report.relative_terminal_wealth_gap",
            )
            for row in group_rows
        ]
        _require(
            bool(values),
            "incomplete_report_table",
            "report.range",
            "must contain at least one included result",
        )
        counts = (
            sum(value < 0 for value in values),
            sum(value == 0 for value in values),
            sum(value > 0 for value in values),
        )
        return (
            _signed_percent(str(min(values))),
            _signed_percent(str(max(values))),
            " / ".join(str(value) for value in counts),
        )

    lines.extend(
        (
            "",
            "### Coverage ranges across the fixed catalog",
            "",
            "| Coverage | Comparison | Minimum | Maximum | Loss / tie / win |",
            "|---:|---|---:|---:|---:|",
        )
    )
    for coverage in primary_coverage:
        if coverage == "1":
            continue
        for comparison in comparison_order:
            minimum, maximum, counts = range_line(
                select(
                    coverage=coverage,
                    cost_scenario="frictionless",
                    comparison=comparison,
                )
            )
            lines.append(
                f"| {coverage} | {comparison_labels[comparison]} | "
                f"{minimum} | {maximum} | {counts} |"
            )

    cost_labels = {
        "frictionless": "Frictionless",
        "proportional-10bps": "Proportional 10 bps",
        "fixed-1-usd": "Fixed USD 1",
    }
    lines.extend(
        (
            "",
            f"### Cost ranges at coverage {featured_coverage}",
            "",
            "| Cost | Comparison | Minimum | Maximum | Loss / tie / win |",
            "|---|---|---:|---:|---:|",
        )
    )
    for cost in config_document["cost_scenarios"]:
        cost_id = cost["cost_id"]
        for comparison in comparison_order:
            minimum, maximum, counts = range_line(
                select(
                    coverage=featured_coverage,
                    cost_scenario=cost_id,
                    comparison=comparison,
                )
            )
            lines.append(
                f"| {cost_labels.get(cost_id, cost_id)} | "
                f"{comparison_labels[comparison]} | {minimum} | {maximum} | "
                f"{counts} |"
            )
    return "\n".join(lines) + "\n"


def _build_adversarial_search_input(
    document: Mapping[str, Any],
    *,
    study_sha256: str,
    start_date: date,
) -> tuple[
    VersionedInput,
    bytes,
    tuple[dict[str, Any], ...],
    dict[str, tuple[str, ...]],
]:
    search = document["adversarial_design_search"]
    rows: list[dict[str, Any]] = []
    episodes: list[dict[str, Any]] = []
    prices_by_episode: dict[str, tuple[str, ...]] = {}
    for grid_index, sequence in enumerate(
        product(search["price_grid"], repeat=search["purchase_count"]),
        start=1,
    ):
        prices = tuple(str(value) for value in sequence)
        candidate_id = f"{search['search_id']}-{grid_index:03d}"
        parameters = {
            "prices": list(prices),
            "evaluation_price": search["evaluation_price"],
            "minimum_direction_changes": search["minimum_direction_changes"],
        }
        predicate = _predicate_receipt(
            "hostile-adaptive-timing",
            [
                _decimal(
                    value,
                    f"study.adversarial_design_search.candidate[{grid_index}]",
                )
                for value in prices
            ],
            _decimal(
                search["evaluation_price"],
                "study.adversarial_design_search.evaluation_price",
            ),
            parameters,
        )
        row = {
            "candidate_id": candidate_id,
            "prices": list(prices),
            "evaluation_price": search["evaluation_price"],
            "predicate": "hostile-adaptive-timing",
            "predicate_status": predicate["status"],
            "predicate_details": predicate["details"],
            "status": (
                "eligible" if predicate["status"] == "passed" else "excluded"
            ),
            "exclusion_reason": (
                None
                if predicate["status"] == "passed"
                else "path_predicate_failed"
            ),
            "relative_terminal_wealth_gap": None,
            "terminal_cash_gap": None,
            "terminal_unit_gap": None,
        }
        rows.append(row)
        if predicate["status"] != "passed":
            continue
        episode, _ = _generate_attempt(
            {
                "attempt_id": candidate_id,
                "family": "adversarial-design-search",
                "predicate": "hostile-adaptive-timing",
                "parameters": parameters,
                "boundary_fixtures": [],
                "mechanisms": ["exhaustive-adversarial-design-search"],
            },
            deposit=document["deposit"],
            start_date=start_date,
        )
        episodes.append(episode)
        prices_by_episode[candidate_id] = prices
    _require(
        bool(episodes),
        "empty_adversarial_search",
        "study.adversarial_design_search",
        "the predicate filter must retain at least one candidate",
    )
    input_document = {
        "schema_version": "smartdca-versioned-input/1",
        "input_id": f"{document['input_id']}-adversarial-search",
        "version": document["input_version"],
        "kind": "synthetic",
        "confirmatory": False,
        "seed": document["seed"],
        "generator_version": document["generator_version"],
        "study_spec_sha256": study_sha256,
        "adversarial_design_search": search,
        "episodes": episodes,
    }
    payload = (_canonical_json(input_document) + "\n").encode("utf-8")
    return (
        VersionedInput.from_json_bytes(payload),
        payload,
        tuple(rows),
        prices_by_episode,
    )


def _source_sha256() -> str:
    return _fingerprint(Path(__file__).read_bytes())


def _study_run_id(
    config: StudyConfig,
    study: DeterministicStudy,
    runner_input: VersionedInput,
    adversarial_search_input: VersionedInput | None,
) -> str:
    identity = _canonical_json(
        {
            "engine_version": STUDY_ENGINE_VERSION,
            "generator_sha256": _source_sha256(),
            "runner_sha256": _runner_source_sha256(),
            "protocol_sha256": config.sha256,
            "study_sha256": study.sha256,
            "runner_input_sha256": runner_input.sha256,
            "adversarial_search_input_sha256": (
                adversarial_search_input.sha256
                if adversarial_search_input is not None
                else None
            ),
        }
    )
    return f"smartdca-deterministic-v1-{_fingerprint(identity.encode('utf-8'))}"


def run_deterministic_study(
    config: StudyConfig,
    study: DeterministicStudy,
    output_root: Path,
) -> DeterministicStudyBundle:
    """Generate validated paths and execute them through the shared runner."""
    _require(isinstance(config, StudyConfig), "invalid_type", "config", "must be StudyConfig")
    _require(
        isinstance(study, DeterministicStudy),
        "invalid_type",
        "study",
        "must be DeterministicStudy",
    )
    _require(
        isinstance(output_root, Path),
        "invalid_type",
        "output_root",
        "must be pathlib.Path",
    )
    document = study.as_mapping()
    config_document = config.as_mapping()
    start_date = _date(document["start_date"], "study.start_date")
    episodes: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    for attempt in document["attempts"]:
        try:
            episode, receipt = _generate_attempt(
                attempt,
                deposit=document["deposit"],
                start_date=start_date,
            )
        except ExperimentValidationError as error:
            receipts.append(
                {
                    **_attempt_metadata(attempt),
                    "status": "excluded",
                    "exclusion_reason": error.code,
                    "validation_field": error.field,
                    "validation_message": str(error),
                    "predicate_status": (
                        "failed"
                        if error.code == "path_predicate_failed"
                        else "not-evaluated"
                    ),
                    "predicate_details": None,
                    "episode_id": None,
                }
            )
        else:
            episodes.append(episode)
            receipts.append(receipt)
    generated_receipts = [
        receipt for receipt in receipts if receipt["status"] == "generated"
    ]
    generated_families = {receipt["family"] for receipt in generated_receipts}
    _require(
        set(document["required_families"]) <= generated_families,
        "missing_required_family",
        "study.required_families",
        "every required family must have a generated path",
    )
    generated_fixtures = {
        fixture
        for receipt in generated_receipts
        for fixture in receipt["boundary_fixtures"]
    }
    _require(
        set(document["required_boundary_fixtures"]) <= generated_fixtures,
        "missing_boundary_fixture",
        "study.required_boundary_fixtures",
        "every required boundary fixture must be represented",
    )
    path_attempts = tuple(receipts)
    runner_input_document = {
        "schema_version": "smartdca-versioned-input/1",
        "input_id": document["input_id"],
        "version": document["input_version"],
        "kind": "synthetic",
        "confirmatory": False,
        "seed": document["seed"],
        "generator_version": document["generator_version"],
        "study_spec_sha256": study.sha256,
        "path_attempts": list(path_attempts),
        "episodes": episodes,
    }
    runner_input_payload = (
        _canonical_json(runner_input_document) + "\n"
    ).encode("utf-8")
    runner_input = VersionedInput.from_json_bytes(runner_input_payload)
    adversarial_search_input: VersionedInput | None = None
    adversarial_search_payload: bytes | None = None
    adversarial_search_rows: tuple[dict[str, Any], ...] = ()
    adversarial_search_prices: dict[str, tuple[str, ...]] = {}
    if "adversarial_design_search" in document:
        (
            adversarial_search_input,
            adversarial_search_payload,
            adversarial_search_rows,
            adversarial_search_prices,
        ) = _build_adversarial_search_input(
            document,
            study_sha256=study.sha256,
            start_date=start_date,
        )
    study_run_id = _study_run_id(
        config,
        study,
        runner_input,
        adversarial_search_input,
    )
    output_root.mkdir(parents=True, exist_ok=True)
    final_directory = output_root / study_run_id
    if final_directory.exists():
        raise RunIdentityCollisionError(
            "run_identity_collision",
            "output_root",
            f"{study_run_id} already exists",
        )

    temporary_directory = Path(
        tempfile.mkdtemp(prefix=f".{study_run_id}-", dir=output_root)
    )
    adversarial_search_manifest: dict[str, Any] | None = None
    try:
        (temporary_directory / "runner-input.json").write_bytes(runner_input_payload)
        runner_stage = temporary_directory / "runner-stage"
        runner = run_experiment(config, runner_input, runner_stage)
        _require(
            runner.manifest["runner_sha256"] == _runner_source_sha256(),
            "runner_source_drift",
            "runner.manifest.runner_sha256",
            "shared runner source changed after the study identity was derived",
        )
        runner_directory = temporary_directory / "runner"
        os.replace(runner.output_directory, runner_directory)
        runner_stage.rmdir()
        if adversarial_search_input is not None:
            _require(
                adversarial_search_payload is not None,
                "missing_adversarial_search_payload",
                "study.adversarial_design_search",
                "validated search input must have a serialized payload",
            )
            search = document["adversarial_design_search"]
            _require(
                search["coverage"] in config_document["coverage"]["primary"],
                "search_grid_mismatch",
                "study.adversarial_design_search.coverage",
                "must be in the preregistered primary coverage grid",
            )
            _require(
                search["corrected_mean_config"]
                in {
                    value["config_id"]
                    for value in config_document["corrected_mean"]["primary"]
                },
                "search_grid_mismatch",
                "study.adversarial_design_search.corrected_mean_config",
                "must be a preregistered primary configuration",
            )
            _require(
                search["cost_scenario"]
                in {
                    value["cost_id"]
                    for value in config_document["cost_scenarios"]
                },
                "search_grid_mismatch",
                "study.adversarial_design_search.cost_scenario",
                "must be a preregistered cost scenario",
            )
            (
                temporary_directory / "adversarial-search-input.json"
            ).write_bytes(adversarial_search_payload)
            search_stage = temporary_directory / "adversarial-search-stage"
            search_runner = run_experiment(
                config,
                adversarial_search_input,
                search_stage,
            )
            _require(
                search_runner.manifest["runner_sha256"]
                == _runner_source_sha256(),
                "runner_source_drift",
                "adversarial_search.runner.manifest.runner_sha256",
                "shared runner source changed during adversarial search",
            )
            search_directory = temporary_directory / "adversarial-search-runner"
            os.replace(search_runner.output_directory, search_directory)
            search_stage.rmdir()
            row_by_id = {
                row["candidate_id"]: row
                for row in adversarial_search_rows
                if row["status"] == "eligible"
            }
            objective_results = [
                result
                for result in search_runner.episode_results
                if result["coverage"] == search["coverage"]
                and result["corrected_mean_config"]
                == search["corrected_mean_config"]
                and result["cost_scenario"] == search["cost_scenario"]
                and result["comparison"] == search["comparison"]
                and result["result_status"] == "included"
            ]
            _require(
                len(objective_results) == len(row_by_id),
                "incomplete_adversarial_search",
                "study.adversarial_design_search",
                "every eligible candidate must have one objective result",
            )
            for result in objective_results:
                row = row_by_id[result["episode_id"]]
                row["relative_terminal_wealth_gap"] = result[
                    "relative_terminal_wealth_gap"
                ]
                row["terminal_cash_gap"] = result["terminal_cash_gap"]
                row["terminal_unit_gap"] = result["terminal_unit_gap"]
            selected = min(
                objective_results,
                key=lambda result: (
                    _decimal(
                        result["relative_terminal_wealth_gap"],
                        "adversarial_search.relative_terminal_wealth_gap",
                    ),
                    tuple(
                        _decimal(value, "adversarial_search.price")
                        for value in adversarial_search_prices[
                            result["episode_id"]
                        ]
                    ),
                ),
            )
            selected_prices = list(
                adversarial_search_prices[selected["episode_id"]]
            )
            selected_attempt = next(
                attempt
                for attempt in document["attempts"]
                if attempt["attempt_id"] == search["selected_attempt_id"]
            )
            _require(
                selected_attempt["parameters"]["prices"] == selected_prices
                and selected_attempt["parameters"]["evaluation_price"]
                == search["evaluation_price"],
                "adversarial_selection_mismatch",
                "study.adversarial_design_search.selected_attempt_id",
                "saved hostile path must equal the declared search result",
            )
            _write_jsonl(
                temporary_directory / "adversarial-search.jsonl",
                adversarial_search_rows,
            )
            adversarial_search_manifest = {
                **search,
                "attempted_grid_count": len(adversarial_search_rows),
                "candidate_count": len(objective_results),
                "predicate_excluded_count": (
                    len(adversarial_search_rows) - len(objective_results)
                ),
                "search_input_sha256": adversarial_search_input.sha256,
                "runner_run_id": search_runner.run_id,
                "selected_candidate_id": selected["episode_id"],
                "selected_prices": selected_prices,
                "selected_relative_terminal_wealth_gap": selected[
                    "relative_terminal_wealth_gap"
                ],
            }
        _write_jsonl(temporary_directory / "path-attempts.jsonl", path_attempts)
        boundary_contracts = _evaluate_boundary_contracts(document, runner)
        boundary = {
            "required": document["required_boundary_fixtures"],
            "represented": sorted(generated_fixtures),
            "fixtures": [
                {
                    "fixture": fixture,
                    "episode_ids": sorted(
                        receipt["episode_id"]
                        for receipt in generated_receipts
                        if fixture in receipt["boundary_fixtures"]
                    ),
                }
                for fixture in document["required_boundary_fixtures"]
            ],
            "regression_contracts": list(boundary_contracts),
            "evidence_scope": "finite-regression-not-proof",
            "limitation": (
                "These finite paths reconnect the empirical implementation to "
                "accepted boundary results; they do not prove performance on "
                "unobserved deterministic, stochastic, or historical paths."
            ),
            "status": "passed" if boundary_contracts else "represented",
        }
        _write_json(temporary_directory / "boundary-fixtures.json", boundary)
        _write_mechanism_attribution(
            temporary_directory / "mechanism-attribution.csv",
            runner.episode_results,
            path_attempts,
        )
        (temporary_directory / "report-tables.txt").write_text(
            _render_report_tables(
                config_document,
                document,
                runner.episode_results,
                path_attempts,
            ),
            encoding="utf-8",
            newline="\n",
        )
        validation = {
            "status": "passed",
            "seed": document["seed"],
            "attempted_path_count": len(path_attempts),
            "generated_path_count": len(episodes),
            "excluded_path_count": len(path_attempts) - len(episodes),
            "predicate_pass_count": len(episodes),
            "required_families": document["required_families"],
            "generated_families": sorted(generated_families),
            "required_boundary_fixtures": document["required_boundary_fixtures"],
            "represented_boundary_fixtures": sorted(generated_fixtures),
            "boundary_regression_contract_count": len(boundary_contracts),
            "shared_runner_validation": runner.validation,
            "adversarial_design_search": adversarial_search_manifest,
        }
        _write_json(temporary_directory / "study-validation.json", validation)
        artifacts = []
        for artifact in sorted(
            path
            for path in temporary_directory.rglob("*")
            if path.is_file()
        ):
            artifacts.append(
                {
                    "path": artifact.relative_to(temporary_directory).as_posix(),
                    "sha256": _fingerprint(artifact.read_bytes()),
                }
            )
        manifest = {
            "schema_version": "smartdca-deterministic-study-manifest/1",
            "study_run_id": study_run_id,
            "engine_version": STUDY_ENGINE_VERSION,
            "generator_version": GENERATOR_VERSION,
            "generator_sha256": _source_sha256(),
            "runner_sha256": _runner_source_sha256(),
            "seed": document["seed"],
            "protocol_sha256": config.sha256,
            "study_spec_sha256": study.sha256,
            "runner_input_sha256": runner_input.sha256,
            "runner_run_id": runner.run_id,
            "adversarial_design_search": adversarial_search_manifest,
            "execution_grid": {
                "policies": sorted(
                    {ledger["policy"] for ledger in runner.ledgers}
                ),
                "comparisons": sorted(
                    {result["comparison"] for result in runner.episode_results}
                ),
                "coverage": config_document["coverage"]["primary"],
                "corrected_mean_configurations": [
                    value["config_id"]
                    for value in config_document["corrected_mean"]["primary"]
                ],
                "cost_scenarios": [
                    value["cost_id"]
                    for value in config_document["cost_scenarios"]
                ],
                "theorem_scopes": sorted(
                    {ledger["theorem_scope"] for ledger in runner.ledgers}
                ),
            },
            "attempted_path_count": len(path_attempts),
            "generated_path_count": len(episodes),
            "excluded_path_count": len(path_attempts) - len(episodes),
            "artifacts": artifacts,
        }
        _write_json(temporary_directory / "manifest.json", manifest)
        os.replace(temporary_directory, final_directory)
    except BaseException:
        for path in sorted(temporary_directory.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            else:
                path.rmdir()
        temporary_directory.rmdir()
        raise

    relocated_runner = RunBundle(
        run_id=runner.run_id,
        output_directory=final_directory / "runner",
        manifest=runner.manifest,
        ledgers=runner.ledgers,
        episode_results=runner.episode_results,
        aggregates=runner.aggregates,
        validation=runner.validation,
    )
    return DeterministicStudyBundle(
        study_run_id=study_run_id,
        output_directory=final_directory,
        manifest=manifest,
        path_attempts=path_attempts,
        runner=relocated_runner,
    )


def main(argv: list[str] | None = None) -> int:
    """Run one immutable deterministic study from a clean environment."""
    parser = argparse.ArgumentParser(
        description="Execute the deterministic SmartDCA path study."
    )
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--study", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    arguments = parser.parse_args(argv)
    try:
        bundle = run_deterministic_study(
            load_study_config(arguments.config),
            load_deterministic_study(arguments.study),
            arguments.output_root,
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
    print(
        _canonical_json(
            {
                "status": "completed",
                "study_run_id": bundle.study_run_id,
                "output_directory": str(bundle.output_directory.resolve()),
                "manifest": str(
                    (bundle.output_directory / "manifest.json").resolve()
                ),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
