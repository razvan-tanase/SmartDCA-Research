"""Deterministic public runner for the preregistered SmartDCA study."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import ROUND_FLOOR, ROUND_HALF_EVEN, Decimal, localcontext
from functools import wraps
from pathlib import Path
from typing import Any, Mapping, ParamSpec, TypeVar


ENGINE_VERSION = "smartdca-empirical-runner/1"
ZERO = Decimal("0")
HALF = Decimal("0.5")
ONE = Decimal("1")
P = ParamSpec("P")
R = TypeVar("R")


class ExperimentValidationError(ValueError):
    """Externally visible pre-execution validation failure."""

    def __init__(self, code: str, field: str, message: str) -> None:
        self.code = code
        self.field = field
        super().__init__(f"{code} at {field}: {message}")


class RunIdentityCollisionError(ExperimentValidationError):
    """Raised before policy execution when a run identity already exists."""


def _fixed_decimal_context(function: Callable[P, R]) -> Callable[P, R]:
    """Make public-run arithmetic independent of the caller's Decimal context."""

    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        with localcontext() as context:
            context.prec = 60
            context.rounding = ROUND_HALF_EVEN
            return function(*args, **kwargs)

    return wrapper


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


def _require(condition: bool, code: str, field: str, message: str) -> None:
    if not condition:
        raise ExperimentValidationError(code, field, message)


def _mapping_copy(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    _require(isinstance(value, Mapping), "invalid_type", field, "must be a mapping")
    try:
        return json.loads(_canonical_json(value))
    except (TypeError, ValueError) as error:
        raise ExperimentValidationError(
            "invalid_json_value", field, "must contain only finite JSON values"
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
            "invalid_json", field, "must be one duplicate-free finite JSON document"
        ) from error
    _require(isinstance(value, dict), "invalid_type", field, "must be a JSON object")
    return value


def _decimal(value: Any, field: str) -> Decimal:
    _require(
        isinstance(value, (str, int)) and not isinstance(value, bool),
        "invalid_decimal",
        field,
        "must be an integer or a decimal string",
    )
    try:
        result = Decimal(str(value))
    except Exception as error:  # Decimal exposes several conversion subclasses.
        raise ExperimentValidationError(
            "invalid_decimal", field, "must be a finite decimal"
        ) from error
    _require(result.is_finite(), "invalid_decimal", field, "must be finite")
    return result


def _date(value: Any, field: str) -> date:
    _require(isinstance(value, str), "invalid_date", field, "must be an ISO date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ExperimentValidationError(
            "invalid_date", field, "must be a real YYYY-MM-DD calendar date"
        ) from error
    _require(parsed.isoformat() == value, "invalid_date", field, "must use YYYY-MM-DD")
    return parsed


def _cost_theorem_scope(cost: Mapping[str, Any], field: str) -> str:
    fixed = _decimal(cost.get("fixed_fee"), f"{field}.fixed_fee")
    bps = _decimal(cost.get("proportional_bps"), f"{field}.proportional_bps")
    return (
        "epsilon-dca"
        if fixed == ZERO and bps == ZERO
        else "outside-current-safety-theorem"
    )


@dataclass(frozen=True)
class StudyConfig:
    """Validated immutable semantic representation of one locked protocol."""

    canonical_document: str
    sha256: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "StudyConfig":
        document = _mapping_copy(value, "config")
        _validate_config(document)
        canonical = _canonical_json(document)
        return cls(canonical, _fingerprint(canonical.encode("utf-8")))

    @classmethod
    def from_json_bytes(cls, payload: bytes) -> "StudyConfig":
        document = _decode_json_document(payload, "config")
        _validate_config(document)
        return cls(_canonical_json(document), _fingerprint(payload))

    def as_mapping(self) -> dict[str, Any]:
        return json.loads(self.canonical_document)


@dataclass(frozen=True)
class VersionedInput:
    """Validated immutable episode input plus its content fingerprint."""

    canonical_document: str
    sha256: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "VersionedInput":
        document = _mapping_copy(value, "input")
        _validate_input(document)
        canonical = _canonical_json(document)
        return cls(canonical, _fingerprint(canonical.encode("utf-8")))

    @classmethod
    def from_json_bytes(cls, payload: bytes) -> "VersionedInput":
        document = _decode_json_document(payload, "input")
        _validate_input(document)
        return cls(_canonical_json(document), _fingerprint(payload))

    def as_mapping(self) -> dict[str, Any]:
        return json.loads(self.canonical_document)


def load_study_config(path: Path) -> StudyConfig:
    """Load and validate an immutable protocol, fingerprinting its exact bytes."""
    _require(isinstance(path, Path), "invalid_type", "config_path", "must be pathlib.Path")
    try:
        payload = path.read_bytes()
    except OSError as error:
        raise ExperimentValidationError(
            "unreadable_config", "config_path", str(error)
        ) from error
    return StudyConfig.from_json_bytes(payload)


def load_versioned_input(path: Path) -> VersionedInput:
    """Load and validate versioned episodes, fingerprinting their exact bytes."""
    _require(isinstance(path, Path), "invalid_type", "input_path", "must be pathlib.Path")
    try:
        payload = path.read_bytes()
    except OSError as error:
        raise ExperimentValidationError(
            "unreadable_input", "input_path", str(error)
        ) from error
    return VersionedInput.from_json_bytes(payload)


@dataclass(frozen=True)
class RunBundle:
    """Result returned through the public experiment-runner interface."""

    run_id: str
    output_directory: Path
    manifest: Mapping[str, Any]
    ledgers: tuple[Mapping[str, Any], ...]
    episode_results: tuple[Mapping[str, Any], ...]
    aggregates: Mapping[str, Any]
    validation: Mapping[str, Any]


def _validate_config(config: dict[str, Any]) -> None:
    _require(
        config.get("schema_version") == "smartdca-empirical-protocol/1",
        "unsupported_schema",
        "config.schema_version",
        "must equal smartdca-empirical-protocol/1",
    )
    _require(config.get("locked") is True, "unlocked_config", "config.locked", "must be true")
    _require(
        config.get("confirmatory_outcomes_accessed") is False,
        "confirmatory_boundary_breached",
        "config.confirmatory_outcomes_accessed",
        "must be false at preregistration",
    )
    for field in (
        "protocol_id",
        "protocol_version",
        "registered_at",
        "registration_statement",
        "historical_datasets",
        "retrieval_and_fingerprint",
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
    ):
        _require(field in config, "missing_field", f"config.{field}", "is required")
    _require(
        isinstance(config["protocol_id"], str) and bool(config["protocol_id"]),
        "invalid_identifier",
        "config.protocol_id",
        "must be a nonempty string",
    )
    _require(
        isinstance(config["protocol_version"], int)
        and not isinstance(config["protocol_version"], bool)
        and config["protocol_version"] >= 1,
        "invalid_version",
        "config.protocol_version",
        "must be a positive integer",
    )
    try:
        registered_at = datetime.fromisoformat(config["registered_at"].replace("Z", "+00:00"))
    except (AttributeError, ValueError) as error:
        raise ExperimentValidationError(
            "invalid_datetime",
            "config.registered_at",
            "must be an ISO 8601 datetime",
        ) from error
    _require(
        registered_at.tzinfo is not None
        and registered_at.utcoffset() == timezone.utc.utcoffset(registered_at),
        "invalid_datetime",
        "config.registered_at",
        "must carry the UTC offset",
    )

    datasets = config["historical_datasets"]
    _require(
        isinstance(datasets, list) and len(datasets) == 2,
        "incomplete_dataset_selection",
        "config.historical_datasets",
        "must contain the declared SPY and BTC/USD selections",
    )
    dataset_fields = (
        "dataset_id",
        "provider",
        "documentation_url",
        "endpoint",
        "series",
        "asset_semantics",
        "price_field",
        "currency",
        "timezone",
        "adjustment_semantics",
        "eligible_start",
        "data_cutoff",
        "retrieval_rule",
        "fingerprint_rule",
        "redistribution",
        "selection_status",
    )
    dataset_ids = []
    for index, dataset in enumerate(datasets):
        field = f"config.historical_datasets[{index}]"
        _require(isinstance(dataset, dict), "invalid_type", field, "must be a mapping")
        for required in dataset_fields:
            _require(required in dataset, "missing_field", f"{field}.{required}", "is required")
            _require(
                isinstance(dataset[required], str) and bool(dataset[required]),
                "invalid_dataset_selection",
                f"{field}.{required}",
                "must be a nonempty string",
            )
        dataset_ids.append(dataset["dataset_id"])
        _require(
            isinstance(dataset.get("request_parameters"), dict)
            and bool(dataset["request_parameters"]),
            "invalid_dataset_selection",
            f"{field}.request_parameters",
            "must be a nonempty mapping without credentials",
        )
        eligible_start = _date(dataset["eligible_start"], f"{field}.eligible_start")
        data_cutoff = _date(dataset["data_cutoff"], f"{field}.data_cutoff")
        _require(
            eligible_start <= data_cutoff,
            "invalid_date_order",
            field,
            "eligible_start must not follow data_cutoff",
        )
    _require(
        set(dataset_ids) == {"spy-adjusted-daily", "btc-usd-daily"}
        and len(dataset_ids) == len(set(dataset_ids)),
        "incomplete_dataset_selection",
        "config.historical_datasets",
        "must select each declared dataset exactly once",
    )

    episode_design = config["episode_design"]
    _require(isinstance(episode_design, dict), "invalid_type", "config.episode_design", "must be a mapping")
    for required in (
        "deposit_cadence",
        "deposit_amount",
        "deposit_count_rule",
        "episode_start_grid_rule",
        "horizon_date_rule",
        "horizons_months",
        "evaluation_convention",
        "rolling_stride_months",
        "missing_data_rule",
    ):
        _require(required in episode_design, "missing_field", f"config.episode_design.{required}", "is required")
    _require(
        isinstance(episode_design["horizons_months"], list)
        and bool(episode_design["horizons_months"])
        and all(
            isinstance(value, int) and not isinstance(value, bool) and value > 0
            for value in episode_design["horizons_months"]
        ),
        "invalid_horizon",
        "config.episode_design.horizons_months",
        "must be a nonempty list of positive integers",
    )
    _require(
        isinstance(episode_design["rolling_stride_months"], int)
        and not isinstance(episode_design["rolling_stride_months"], bool)
        and episode_design["rolling_stride_months"] > 0,
        "invalid_stride",
        "config.episode_design.rolling_stride_months",
        "must be a positive integer",
    )

    coverage_section = config["coverage"]
    _require(isinstance(coverage_section, dict), "invalid_type", "config.coverage", "must be a mapping")
    primary_coverage = coverage_section.get("primary", [])
    _require(
        isinstance(primary_coverage, list) and bool(primary_coverage),
        "empty_grid",
        "config.coverage.primary",
        "must be a nonempty list",
    )
    parsed_primary_coverage = []
    for index, value in enumerate(primary_coverage):
        coverage = _decimal(value, f"config.coverage.primary[{index}]")
        _require(
            ZERO < coverage <= ONE,
            "invalid_coverage",
            f"config.coverage.primary[{index}]",
            "must lie in (0, 1]",
        )
        parsed_primary_coverage.append(coverage)
    _require(
        len(parsed_primary_coverage) == len(set(parsed_primary_coverage)),
        "duplicate_grid_value",
        "config.coverage.primary",
        "must not contain duplicates",
    )
    _require(
        ONE in parsed_primary_coverage
        and any(ZERO < value < ONE for value in parsed_primary_coverage),
        "incomplete_coverage_grid",
        "config.coverage.primary",
        "must include lambda=1 and at least one nontrivial safety factor",
    )
    robustness_coverage = coverage_section.get("robustness", [])
    _require(
        isinstance(robustness_coverage, list) and bool(robustness_coverage),
        "empty_grid",
        "config.coverage.robustness",
        "must freeze at least one robustness value",
    )
    for index, value in enumerate(robustness_coverage):
        parsed = _decimal(value, f"config.coverage.robustness[{index}]")
        _require(
            ZERO < parsed <= ONE,
            "invalid_coverage",
            f"config.coverage.robustness[{index}]",
            "must lie in (0, 1]",
        )

    corrected_mean = config["corrected_mean"]
    _require(isinstance(corrected_mean, dict), "invalid_type", "config.corrected_mean", "must be a mapping")
    primary_means = corrected_mean.get("primary", [])
    _require(
        isinstance(primary_means, list) and bool(primary_means),
        "empty_grid",
        "config.corrected_mean.primary",
        "must not be empty",
    )
    robustness_means = corrected_mean.get("robustness", [])
    _require(
        isinstance(robustness_means, list) and bool(robustness_means),
        "empty_grid",
        "config.corrected_mean.robustness",
        "must freeze at least one robustness configuration",
    )
    mean_ids = []
    for tier, means in (("primary", primary_means), ("robustness", robustness_means)):
        for index, mean in enumerate(means):
            field = f"config.corrected_mean.{tier}[{index}]"
            _require(isinstance(mean, dict), "invalid_type", field, "must be a mapping")
            _require(
                isinstance(mean.get("config_id"), str) and bool(mean["config_id"]),
                "invalid_identifier",
                f"{field}.config_id",
                "must be a nonempty string",
            )
            mean_ids.append(mean["config_id"])
            _require(mean.get("transform") == "identity", "unsupported_transform", field, "only identity is supported")
            alpha = _decimal(mean.get("alpha"), f"{field}.alpha")
            _decimal(mean.get("beta"), f"{field}.beta")
            _require(
                tier != "primary" or alpha <= ONE,
                "unsupported_parameter",
                f"{field}.alpha",
                "primary countercyclical configurations require alpha <= 1",
            )
            _require(mean.get("weights") == "equal", "unsupported_weights", field, "only equal weights are supported")
    _require(
        len(mean_ids) == len(set(mean_ids)),
        "duplicate_grid_value",
        "config.corrected_mean",
        "config_id values must be unique",
    )

    costs = config["cost_scenarios"]
    _require(isinstance(costs, list) and costs, "empty_grid", "config.cost_scenarios", "must not be empty")
    cost_ids = []
    has_frictionless = False
    has_fixed = False
    has_proportional = False
    for index, cost in enumerate(costs):
        _require(isinstance(cost, dict), "invalid_type", f"config.cost_scenarios[{index}]", "must be a mapping")
        _require(
            isinstance(cost.get("cost_id"), str) and bool(cost["cost_id"]),
            "invalid_identifier",
            f"config.cost_scenarios[{index}].cost_id",
            "must be a nonempty string",
        )
        cost_ids.append(cost["cost_id"])
        fixed = _decimal(cost.get("fixed_fee"), f"config.cost_scenarios[{index}].fixed_fee")
        bps = _decimal(
            cost.get("proportional_bps"),
            f"config.cost_scenarios[{index}].proportional_bps",
        )
        _require(fixed >= ZERO, "invalid_cost", f"config.cost_scenarios[{index}].fixed_fee", "must be nonnegative")
        _require(bps >= ZERO, "invalid_cost", f"config.cost_scenarios[{index}].proportional_bps", "must be nonnegative")
        expected_scope = _cost_theorem_scope(
            cost, f"config.cost_scenarios[{index}]"
        )
        _require(
            cost.get("theorem_scope") == expected_scope,
            "invalid_theorem_scope",
            f"config.cost_scenarios[{index}].theorem_scope",
            f"must equal {expected_scope}",
        )
        has_frictionless |= fixed == ZERO and bps == ZERO
        has_fixed |= fixed > ZERO and bps == ZERO
        has_proportional |= fixed == ZERO and bps > ZERO
    _require(
        len(cost_ids) == len(set(cost_ids)),
        "duplicate_grid_value",
        "config.cost_scenarios",
        "cost_id values must be unique",
    )
    _require(
        has_frictionless and has_fixed and has_proportional,
        "incomplete_cost_grid",
        "config.cost_scenarios",
        "must include frictionless, fixed-fee, and proportional-fee routes",
    )

    hypotheses = config["hypotheses"]
    _require(isinstance(hypotheses, list) and hypotheses, "empty_hypotheses", "config.hypotheses", "must not be empty")
    for index, hypothesis in enumerate(hypotheses):
        field = f"config.hypotheses[{index}]"
        _require(isinstance(hypothesis, dict), "invalid_type", field, "must be a mapping")
        for required in ("hypothesis_id", "comparison", "alternative"):
            _require(required in hypothesis, "missing_field", f"{field}.{required}", "is required")

    estimands = config["estimands"]
    _require(isinstance(estimands, dict), "invalid_type", "config.estimands", "must be a mapping")
    for tier in ("primary", "secondary"):
        _require(
            isinstance(estimands.get(tier), list) and bool(estimands[tier]),
            "empty_estimands",
            f"config.estimands.{tier}",
            "must not be empty",
        )

    multiplicity = config["multiplicity"]
    _require(isinstance(multiplicity, dict), "invalid_type", "config.multiplicity", "must be a mapping")
    for required in ("family", "method", "alpha"):
        _require(required in multiplicity, "missing_field", f"config.multiplicity.{required}", "is required")
    multiplicity_alpha = _decimal(multiplicity["alpha"], "config.multiplicity.alpha")
    _require(ZERO < multiplicity_alpha < ONE, "invalid_alpha", "config.multiplicity.alpha", "must lie in (0, 1)")

    uncertainty = config["uncertainty"]
    _require(isinstance(uncertainty, dict), "invalid_type", "config.uncertainty", "must be a mapping")
    for required in (
        "method",
        "replicates",
        "seed",
        "rng",
        "cell_seed_rule",
        "block_rule",
        "block_construction",
        "replicate_statistic",
        "interval",
        "quantile_rule",
        "p_value",
        "p_value_finite_sample_rule",
        "holm_order",
    ):
        _require(required in uncertainty, "missing_field", f"config.uncertainty.{required}", "is required")
    _require(
        isinstance(uncertainty["replicates"], int)
        and not isinstance(uncertainty["replicates"], bool)
        and uncertainty["replicates"] > 0,
        "invalid_replicates",
        "config.uncertainty.replicates",
        "must be a positive integer",
    )
    _require(
        isinstance(uncertainty["seed"], int)
        and not isinstance(uncertainty["seed"], bool),
        "invalid_seed",
        "config.uncertainty.seed",
        "must be an integer",
    )

    analysis_tiers = config["analysis_tiers"]
    _require(isinstance(analysis_tiers, dict), "invalid_type", "config.analysis_tiers", "must be a mapping")
    required_tiers = {"confirmatory", "secondary", "robustness", "exploratory"}
    _require(
        required_tiers <= set(analysis_tiers)
        and all(
            isinstance(analysis_tiers[tier], list) and bool(analysis_tiers[tier])
            for tier in required_tiers
        ),
        "incomplete_analysis_tiers",
        "config.analysis_tiers",
        "must distinguish nonempty confirmatory, secondary, robustness, and exploratory tiers",
    )
    _require(
        isinstance(analysis_tiers.get("immutability_rule"), str)
        and bool(analysis_tiers["immutability_rule"]),
        "missing_immutability_rule",
        "config.analysis_tiers.immutability_rule",
        "must freeze confirmatory choices after outcome access",
    )
    _require(
        isinstance(config["exclusions"], list) and bool(config["exclusions"]),
        "empty_exclusions",
        "config.exclusions",
        "must retain at least one declared exclusion reason",
    )
    runner_contract = config["runner_contract"]
    _require(
        isinstance(runner_contract, dict),
        "invalid_type",
        "config.runner_contract",
        "must be a mapping",
    )
    _require(
        runner_contract.get("engine_version") == ENGINE_VERSION,
        "unsupported_engine",
        "config.runner_contract.engine_version",
        f"must equal {ENGINE_VERSION}",
    )


def _validate_input(inputs: dict[str, Any]) -> None:
    _require(
        inputs.get("schema_version") == "smartdca-versioned-input/1",
        "unsupported_schema",
        "input.schema_version",
        "must equal smartdca-versioned-input/1",
    )
    for field in ("input_id", "version", "kind", "confirmatory", "episodes"):
        _require(field in inputs, "missing_field", f"input.{field}", "is required")
    for field in ("input_id", "version"):
        _require(
            isinstance(inputs[field], str) and bool(inputs[field]),
            "invalid_identifier",
            f"input.{field}",
            "must be a nonempty string",
        )
    _require(
        isinstance(inputs["kind"], str)
        and inputs["kind"] in {"synthetic", "stochastic", "historical"},
        "invalid_input_kind",
        "input.kind",
        "must be synthetic, stochastic, or historical",
    )
    _require(
        isinstance(inputs["confirmatory"], bool),
        "invalid_type",
        "input.confirmatory",
        "must be boolean",
    )
    _require(
        isinstance(inputs["episodes"], list),
        "invalid_type",
        "input.episodes",
        "must be a list",
    )
    _require(inputs["episodes"], "empty_input", "input.episodes", "must not be empty")
    episode_ids: list[str] = []
    for episode_index, episode in enumerate(inputs["episodes"]):
        prefix = f"input.episodes[{episode_index}]"
        _require(isinstance(episode, dict), "invalid_type", prefix, "must be a mapping")
        for required in (
            "episode_id",
            "family",
            "dataset_id",
            "horizon_months",
            "observations",
            "evaluation_date",
            "evaluation_price",
        ):
            _require(required in episode, "missing_field", f"{prefix}.{required}", "is required")
        for identifier in ("episode_id", "family", "dataset_id"):
            _require(
                isinstance(episode[identifier], str) and bool(episode[identifier]),
                "invalid_identifier",
                f"{prefix}.{identifier}",
                "must be a nonempty string",
            )
        episode_ids.append(episode["episode_id"])
        _require(
            isinstance(episode["horizon_months"], int)
            and not isinstance(episode["horizon_months"], bool)
            and episode["horizon_months"] > 0,
            "invalid_horizon",
            f"{prefix}.horizon_months",
            "must be a positive integer",
        )
        observations = episode["observations"]
        _require(
            isinstance(observations, list),
            "invalid_type",
            f"{prefix}.observations",
            "must be a list",
        )
        _require(observations, "empty_episode", f"{prefix}.observations", "must not be empty")
        previous_date: date | None = None
        for row_index, row in enumerate(observations):
            field = f"{prefix}.observations[{row_index}]"
            _require(isinstance(row, dict), "invalid_type", field, "must be a mapping")
            for required in ("date", "price", "deposit"):
                _require(required in row, "missing_field", f"{field}.{required}", "is required")
            observed_date = _date(row.get("date"), f"{field}.date")
            _require(previous_date is None or observed_date > previous_date, "invalid_date_order", f"{field}.date", "must be strictly increasing")
            previous_date = observed_date
            _require(_decimal(row.get("price"), f"{field}.price") > ZERO, "invalid_price", f"{field}.price", "must be positive")
            _require(_decimal(row.get("deposit"), f"{field}.deposit") >= ZERO, "invalid_deposit", f"{field}.deposit", "must be nonnegative")
        evaluation_date = _date(
            episode.get("evaluation_date"), f"{prefix}.evaluation_date"
        )
        _require(
            previous_date is not None and evaluation_date >= previous_date,
            "invalid_evaluation_date",
            f"{prefix}.evaluation_date",
            "must be on or after the last purchase date",
        )
        _require(
            _decimal(episode.get("evaluation_price"), f"{prefix}.evaluation_price") > ZERO,
            "invalid_evaluation_price",
            f"{prefix}.evaluation_price",
            "must be positive",
        )
    _require(
        len(episode_ids) == len(set(episode_ids)),
        "duplicate_episode_id",
        "input.episodes",
        "episode_id values must be unique",
    )


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    if value == ZERO:
        return "0"
    text = format(value.normalize(), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def _power(base: Decimal, exponent: Decimal) -> Decimal:
    _require(base > ZERO, "invalid_power", "runner", "power base must be positive")
    with localcontext() as context:
        context.prec = 60
        return (base.ln() * exponent).exp()


def _corrected_reference(
    normalized_prices: tuple[Decimal, ...], alpha: Decimal, beta: Decimal
) -> Decimal:
    if len(normalized_prices) == 1:
        return normalized_prices[0]
    with localcontext() as context:
        context.prec = 60
        if alpha == beta:
            weights = tuple(_power(price, alpha) for price in normalized_prices)
            return (
                sum(
                    (weight * price.ln() for price, weight in zip(normalized_prices, weights, strict=True)),
                    ZERO,
                )
                / sum(weights, ZERO)
            ).exp()
        numerator = sum((_power(price, alpha) for price in normalized_prices), ZERO)
        denominator = sum((_power(price, beta) for price in normalized_prices), ZERO)
        return _power(numerator / denominator, ONE / (alpha - beta))


def _corrected_score(relative_price: Decimal, alpha: Decimal) -> Decimal:
    with localcontext() as context:
        context.prec = 60
        return ONE / (ONE + _power(relative_price, ONE - alpha))


def _execute_purchase(
    budget: Decimal, available_cash: Decimal, fixed_fee: Decimal, proportional_bps: Decimal
) -> tuple[Decimal, Decimal]:
    budget = min(max(budget, ZERO), available_cash)
    rate = proportional_bps / Decimal("10000")
    if budget <= fixed_fee:
        return ZERO, ZERO
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_FLOOR
        purchase = (budget - fixed_fee) / (ONE + rate)
        fee = fixed_fee + rate * purchase
    return purchase, fee


def _base_step(
    *,
    period: int,
    row: Mapping[str, Any],
    available_cash: Decimal,
    purchase: Decimal,
    fee: Decimal,
    cash: Decimal,
    units: Decimal,
    dca_units: Decimal,
) -> dict[str, Any]:
    return {
        "period": period,
        "date": row["date"],
        "price": _decimal_text(_decimal(row["price"], "runner.price")),
        "deposit": _decimal_text(_decimal(row["deposit"], "runner.deposit")),
        "available_cash": _decimal_text(available_cash),
        "reference": None,
        "relative_price": None,
        "score": None,
        "coverage_before": None,
        "raw_guardrail_floor": None,
        "guardrail_floor": None,
        "floor_active": None,
        "discretionary_cash": None,
        "target_purchase_budget": _decimal_text(purchase + fee),
        "purchase": _decimal_text(purchase),
        "fee": _decimal_text(fee),
        "cash": _decimal_text(cash),
        "units": _decimal_text(units),
        "dca_units": _decimal_text(dca_units),
        "coverage_after": None,
    }


def _run_dca(
    observations: list[dict[str, Any]], evaluation_price: Decimal, cost: Mapping[str, Any]
) -> dict[str, Any]:
    fixed = _decimal(cost["fixed_fee"], "cost.fixed_fee")
    bps = _decimal(cost["proportional_bps"], "cost.proportional_bps")
    cash = ZERO
    units = ZERO
    total_fees = ZERO
    steps = []
    for period, row in enumerate(observations, start=1):
        price = _decimal(row["price"], "observation.price")
        deposit = _decimal(row["deposit"], "observation.deposit")
        available = cash + deposit
        purchase, fee = _execute_purchase(available, available, fixed, bps)
        cash = available - purchase - fee
        units += purchase / price
        total_fees += fee
        steps.append(
            _base_step(
                period=period,
                row=row,
                available_cash=available,
                purchase=purchase,
                fee=fee,
                cash=cash,
                units=units,
                dca_units=units,
            )
        )
    return {
        "policy": "dca",
        "steps": steps,
        "terminal_cash": _decimal_text(cash),
        "terminal_units": _decimal_text(units),
        "terminal_asset_value": _decimal_text(evaluation_price * units),
        "terminal_wealth": _decimal_text(cash + evaluation_price * units),
        "total_fees": _decimal_text(total_fees),
    }


def _run_guarded(
    observations: list[dict[str, Any]],
    evaluation_price: Decimal,
    coverage: Decimal,
    mean: Mapping[str, Any],
    cost: Mapping[str, Any],
    dca: Mapping[str, Any],
    *,
    neutral: bool,
) -> dict[str, Any]:
    fixed = _decimal(cost["fixed_fee"], "cost.fixed_fee")
    bps = _decimal(cost["proportional_bps"], "cost.proportional_bps")
    alpha = _decimal(mean["alpha"], "corrected_mean.alpha")
    beta = _decimal(mean["beta"], "corrected_mean.beta")
    prices = tuple(_decimal(row["price"], "observation.price") for row in observations)
    anchor = prices[0]
    cash = ZERO
    units = ZERO
    dca_units_before = ZERO
    total_fees = ZERO
    steps = []
    for index, row in enumerate(observations):
        period = index + 1
        price = prices[index]
        deposit = _decimal(row["deposit"], "observation.deposit")
        available = cash + deposit
        coverage_before = units - coverage * dca_units_before
        raw_floor = coverage * deposit - price * coverage_before
        floor = max(ZERO, raw_floor)
        discretionary = available - floor
        if index == 0:
            reference = None
            relative = ONE
            score = HALF
        else:
            normalized = tuple(value / anchor for value in prices[:index])
            reference = _corrected_reference(normalized, alpha, beta)
            relative = (price / anchor) / reference
            score = HALF if neutral else _corrected_score(relative, alpha)
        target_budget = floor + score * discretionary
        purchase, fee = _execute_purchase(target_budget, available, fixed, bps)
        cash = available - purchase - fee
        units += purchase / price
        total_fees += fee
        dca_units = _decimal(dca["steps"][index]["units"], "dca.units")
        coverage_after = units - coverage * dca_units
        step = _base_step(
            period=period,
            row=row,
            available_cash=available,
            purchase=purchase,
            fee=fee,
            cash=cash,
            units=units,
            dca_units=dca_units,
        )
        step.update(
            {
                "reference": _decimal_text(reference),
                "relative_price": _decimal_text(relative),
                "score": _decimal_text(score),
                "coverage_before": _decimal_text(coverage_before),
                "raw_guardrail_floor": _decimal_text(raw_floor),
                "guardrail_floor": _decimal_text(floor),
                "floor_active": raw_floor > ZERO,
                "discretionary_cash": _decimal_text(discretionary),
                "target_purchase_budget": _decimal_text(target_budget),
                "coverage_after": _decimal_text(coverage_after),
            }
        )
        steps.append(step)
        dca_units_before = dca_units

    policy = "neutral_guarded" if neutral else "corrected_guarded"
    return {
        "policy": policy,
        "steps": steps,
        "terminal_cash": _decimal_text(cash),
        "terminal_units": _decimal_text(units),
        "terminal_asset_value": _decimal_text(evaluation_price * units),
        "terminal_wealth": _decimal_text(cash + evaluation_price * units),
        "total_fees": _decimal_text(total_fees),
    }


def _comparison(
    left: Mapping[str, Any], right: Mapping[str, Any], evaluation_price: Decimal
) -> dict[str, Any]:
    left_wealth = _decimal(left["terminal_wealth"], "left.terminal_wealth")
    right_wealth = _decimal(right["terminal_wealth"], "right.terminal_wealth")
    cash_gap = _decimal(left["terminal_cash"], "left.terminal_cash") - _decimal(
        right["terminal_cash"], "right.terminal_cash"
    )
    unit_gap = _decimal(left["terminal_units"], "left.terminal_units") - _decimal(
        right["terminal_units"], "right.terminal_units"
    )
    direct = left_wealth - right_wealth
    attributed = cash_gap + evaluation_price * unit_gap
    left_metrics = _policy_metrics(left)
    right_metrics = _policy_metrics(right)
    included = right_wealth > ZERO
    return {
        "comparison": f"{left['policy']}_vs_{right['policy']}",
        "result_status": "included" if included else "excluded",
        "exclusion_reason": (
            None if included else "comparator_terminal_wealth_nonpositive"
        ),
        "terminal_wealth_gap": _decimal_text(direct),
        "relative_terminal_wealth_gap": (
            _decimal_text(direct / right_wealth) if included else None
        ),
        "wealth_ratio": (
            _decimal_text(left_wealth / right_wealth) if included else None
        ),
        "terminal_cash_gap": _decimal_text(cash_gap),
        "terminal_unit_gap": _decimal_text(unit_gap),
        "cash_contribution": _decimal_text(cash_gap),
        "unit_contribution": _decimal_text(evaluation_price * unit_gap),
        "identity_residual": _decimal_text(direct - attributed),
        **{f"left_{key}": value for key, value in left_metrics.items()},
        **{f"right_{key}": value for key, value in right_metrics.items()},
    }


def _policy_metrics(ledger: Mapping[str, Any]) -> dict[str, Any]:
    terminal_cash = _decimal(ledger["terminal_cash"], "metrics.terminal_cash")
    terminal_asset_value = _decimal(
        ledger["terminal_asset_value"], "metrics.terminal_asset_value"
    )
    terminal_wealth = _decimal(ledger["terminal_wealth"], "metrics.terminal_wealth")
    total_deposits = sum(
        (_decimal(step["deposit"], "metrics.deposit") for step in ledger["steps"]),
        ZERO,
    )
    purchase_count = sum(
        _decimal(step["purchase"], "metrics.purchase") > ZERO
        for step in ledger["steps"]
    )
    if ledger["policy"] == "dca":
        activation_frequency = ZERO
        mean_guardrail_floor = None
    else:
        activation_frequency = Decimal(
            sum(step["floor_active"] is True for step in ledger["steps"])
        ) / Decimal(len(ledger["steps"]))
        mean_guardrail_floor = _mean(
            [
                _decimal(step["guardrail_floor"], "metrics.guardrail_floor")
                for step in ledger["steps"]
            ]
        )
    return {
        "cash_drag": (
            _decimal_text(terminal_cash / total_deposits)
            if total_deposits > ZERO
            else None
        ),
        "asset_exposure": (
            _decimal_text(terminal_asset_value / terminal_wealth)
            if terminal_wealth > ZERO
            else None
        ),
        "guardrail_activation_frequency": _decimal_text(activation_frequency),
        "mean_guardrail_floor": _decimal_text(mean_guardrail_floor),
        "purchase_count": purchase_count,
        "total_fees": ledger["total_fees"],
    }


def _mean(values: list[Decimal]) -> Decimal:
    return sum(values, ZERO) / Decimal(len(values))


def _median(values: list[Decimal]) -> Decimal:
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / Decimal(2)


def _quantile(values: list[Decimal], probability: Decimal) -> Decimal:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = Decimal(len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - Decimal(lower)
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def _aggregate_results(
    rows: tuple[Mapping[str, Any], ...]
) -> list[dict[str, Any]]:
    groups: dict[
        tuple[str, str, str, int, str, str, str, str, str],
        list[Mapping[str, Any]],
    ] = {}
    for row in rows:
        key = (
            row["input_kind"],
            row["family"],
            row["dataset_id"],
            row["horizon_months"],
            row["coverage"],
            row["corrected_mean_config"],
            row["cost_scenario"],
            row["comparison"],
            row["theorem_scope"],
        )
        groups.setdefault(key, []).append(row)

    aggregates = []
    for key in sorted(groups):
        (
            input_kind,
            family,
            dataset_id,
            horizon_months,
            coverage,
            mean_id,
            cost_id,
            comparison,
            theorem_scope,
        ) = key
        attempted_members = sorted(groups[key], key=lambda row: row["episode_id"])
        members = [
            row for row in attempted_members if row["result_status"] == "included"
        ]
        relative = [
            _decimal(row["relative_terminal_wealth_gap"], "aggregate.relative_gap")
            for row in members
            if row["relative_terminal_wealth_gap"] is not None
        ]
        wealth_gaps = [
            _decimal(row["terminal_wealth_gap"], "aggregate.wealth_gap")
            for row in members
        ]
        ratios = [
            _decimal(row["wealth_ratio"], "aggregate.wealth_ratio")
            for row in members
            if row["wealth_ratio"] is not None
        ]
        aggregate: dict[str, Any] = {
            "input_kind": input_kind,
            "family": family,
            "dataset_id": dataset_id,
            "horizon_months": horizon_months,
            "coverage": coverage,
            "corrected_mean_config": mean_id,
            "cost_scenario": cost_id,
            "comparison": comparison,
            "theorem_scope": theorem_scope,
            "attempted_count": len(attempted_members),
            "sample_count": len(relative),
            "excluded_count": len(attempted_members) - len(members),
            "mean_terminal_wealth_gap": (
                _decimal_text(_mean(wealth_gaps)) if wealth_gaps else None
            ),
            "mean_wealth_ratio": _decimal_text(_mean(ratios)) if ratios else None,
            "win_count": sum(value > ZERO for value in wealth_gaps),
            "tie_count": sum(value == ZERO for value in wealth_gaps),
            "loss_count": sum(value < ZERO for value in wealth_gaps),
            "uncertainty_status": "not-estimated-by-canonical-run",
        }
        if relative:
            aggregate.update(
                {
                    "mean_relative_terminal_wealth_gap": _decimal_text(
                        _mean(relative)
                    ),
                    "median_relative_terminal_wealth_gap": _decimal_text(
                        _median(relative)
                    ),
                    "minimum_relative_terminal_wealth_gap": _decimal_text(
                        min(relative)
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
                }
            )
        else:
            aggregate.update(
                {
                    "mean_relative_terminal_wealth_gap": None,
                    "median_relative_terminal_wealth_gap": None,
                    "minimum_relative_terminal_wealth_gap": None,
                    "maximum_relative_terminal_wealth_gap": None,
                    "downside_quantile_0.05": None,
                    "downside_quantile_0.10": None,
                    "downside_quantile_0.25": None,
                }
            )
        for field in (
            "terminal_cash_gap",
            "terminal_unit_gap",
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
            values = [
                _decimal(row[field], f"aggregate.{field}")
                for row in members
                if row[field] is not None
            ]
            aggregate_field = {
                "left_mean_guardrail_floor": "mean_left_guardrail_floor",
                "right_mean_guardrail_floor": "mean_right_guardrail_floor",
            }.get(field, f"mean_{field}")
            aggregate[aggregate_field] = (
                _decimal_text(_mean(values)) if values else None
            )
        aggregate["mean_left_purchase_count"] = (
            _decimal_text(
                _mean([Decimal(row["left_purchase_count"]) for row in members])
            )
            if members
            else None
        )
        aggregate["mean_right_purchase_count"] = (
            _decimal_text(
                _mean([Decimal(row["right_purchase_count"]) for row in members])
            )
            if members
            else None
        )
        aggregates.append(aggregate)
    return aggregates


def _passed_receipt(code: str, scope: str, details: Mapping[str, Any]) -> dict[str, Any]:
    return {"code": code, "status": "passed", "scope": scope, "details": dict(details)}


def _post_execution_receipts(
    ledgers: tuple[Mapping[str, Any], ...],
    results: tuple[Mapping[str, Any], ...],
    config: Mapping[str, Any],
    inputs: Mapping[str, Any],
) -> list[dict[str, Any]]:
    tolerance = Decimal("1e-24")
    episode_by_id = {episode["episode_id"]: episode for episode in inputs["episodes"]}
    mean_by_id = {
        mean["config_id"]: mean for mean in config["corrected_mean"]["primary"]
    }
    cost_by_id = {cost["cost_id"]: cost for cost in config["cost_scenarios"]}

    for ledger in ledgers:
        cumulative_deposits = ZERO
        cumulative_outlay = ZERO
        previous_units = ZERO
        cost = cost_by_id[ledger["cost_scenario"]]
        fixed_fee = _decimal(cost["fixed_fee"], "receipt.fixed_fee")
        fee_rate = _decimal(
            cost["proportional_bps"], "receipt.proportional_bps"
        ) / Decimal("10000")
        for step in ledger["steps"]:
            cumulative_deposits += _decimal(step["deposit"], "receipt.deposit")
            purchase = _decimal(step["purchase"], "receipt.purchase")
            fee = _decimal(step["fee"], "receipt.fee")
            cumulative_outlay += purchase
            cumulative_outlay += fee
            cash = _decimal(step["cash"], "receipt.cash")
            units = _decimal(step["units"], "receipt.units")
            if abs(cash + cumulative_outlay - cumulative_deposits) > tolerance:
                raise AssertionError("full-funding accounting failed")
            if cash < ZERO or purchase < ZERO:
                raise AssertionError("buy-only nonnegative accounting failed")
            if purchase + fee > _decimal(
                step["target_purchase_budget"], "receipt.target_purchase_budget"
            ):
                raise AssertionError("cost route spent beyond selected budget")
            expected_fee = fixed_fee + fee_rate * purchase if purchase > ZERO else ZERO
            if abs(fee - expected_fee) > tolerance:
                raise AssertionError("cost route fee formula diverged")
            if units + tolerance < previous_units:
                raise AssertionError("buy-only units decreased")
            previous_units = units
        evaluation_price = _decimal(ledger["evaluation_price"], "receipt.evaluation_price")
        direct = _decimal(ledger["terminal_cash"], "receipt.terminal_cash") + evaluation_price * _decimal(
            ledger["terminal_units"], "receipt.terminal_units"
        )
        if abs(direct - _decimal(ledger["terminal_wealth"], "receipt.terminal_wealth")) > tolerance:
            raise AssertionError("direct wealth accounting failed")

        if ledger["policy"] != "dca":
            for step in ledger["steps"]:
                raw = _decimal(step["raw_guardrail_floor"], "receipt.raw_floor")
                floor = _decimal(step["guardrail_floor"], "receipt.floor")
                coverage_before = _decimal(step["coverage_before"], "receipt.coverage_before")
                expected_raw = _decimal(ledger["coverage"], "receipt.coverage") * _decimal(
                    step["deposit"], "receipt.deposit"
                ) - _decimal(step["price"], "receipt.price") * coverage_before
                if abs(raw - expected_raw) > tolerance or abs(floor - max(ZERO, raw)) > tolerance:
                    raise AssertionError("guardrail contract diverged")
                available = _decimal(step["available_cash"], "receipt.available")
                discretionary = _decimal(step["discretionary_cash"], "receipt.discretionary")
                score = _decimal(step["score"], "receipt.score")
                target = _decimal(step["target_purchase_budget"], "receipt.target")
                if abs(available - floor - discretionary) > tolerance:
                    raise AssertionError("guardrail discretionary interval diverged")
                if abs(target - floor - score * discretionary) > tolerance:
                    raise AssertionError("guardrail selector contract diverged")
                if ledger["theorem_scope"] == "epsilon-dca" and _decimal(
                    step["coverage_after"], "receipt.coverage_after"
                ) < -tolerance:
                    raise AssertionError("frictionless unit coverage failed")

    for result in results:
        if abs(_decimal(result["identity_residual"], "receipt.identity_residual")) > tolerance:
            raise AssertionError("terminal cash/unit identity failed")

    scenario_groups: dict[tuple[str, str, str, str], dict[str, Mapping[str, Any]]] = {}
    for ledger in ledgers:
        key = (
            ledger["episode_id"],
            ledger["coverage"],
            ledger["corrected_mean_config"],
            ledger["cost_scenario"],
        )
        scenario_groups.setdefault(key, {})[ledger["policy"]] = ledger

    for key, group in scenario_groups.items():
        episode_id, coverage_text, mean_id, cost_id = key
        episode = episode_by_id[episode_id]
        evaluation_price = _decimal(episode["evaluation_price"], "receipt.evaluation_price")
        mean = mean_by_id[mean_id]
        cost = cost_by_id[cost_id]
        coverage = _decimal(coverage_text, "receipt.coverage")
        for prefix_length in range(1, len(episode["observations"]) + 1):
            prefix = episode["observations"][:prefix_length]
            prefix_dca = _run_dca(prefix, evaluation_price, cost)
            prefix_neutral = _run_guarded(
                prefix,
                evaluation_price,
                coverage,
                mean,
                cost,
                prefix_dca,
                neutral=True,
            )
            prefix_corrected = _run_guarded(
                prefix,
                evaluation_price,
                coverage,
                mean,
                cost,
                prefix_dca,
                neutral=False,
            )
            for policy, prefix_ledger in (
                ("dca", prefix_dca),
                ("neutral_guarded", prefix_neutral),
                ("corrected_guarded", prefix_corrected),
            ):
                observed = group[policy]["steps"][:prefix_length]
                if observed != prefix_ledger["steps"]:
                    raise AssertionError("policy decisions changed under a common prefix")

    collapsed_groups = [group for key, group in scenario_groups.items() if key[1] == "1"]
    for group in collapsed_groups:
        dca_path = [
            (step["purchase"], step["fee"], step["cash"], step["units"])
            for step in group["dca"]["steps"]
        ]
        for policy in ("neutral_guarded", "corrected_guarded"):
            guarded_path = [
                (step["purchase"], step["fee"], step["cash"], step["units"])
                for step in group[policy]["steps"]
            ]
            if guarded_path != dca_path:
                raise AssertionError("lambda=1 did not collapse transaction by transaction")

    dca_ledgers = [ledger for ledger in ledgers if ledger["policy"] == "dca"]
    if any(
        any(
            step[field] is not None
            for step in ledger["steps"]
            for field in (
                "reference",
                "score",
                "guardrail_floor",
                "coverage_after",
            )
        )
        for ledger in dca_ledgers
    ):
        raise AssertionError("DCA accounting leaked guarded-policy fields")

    scope = f"{len(episode_by_id)} episode(s), {len(ledgers)} ledger(s)"
    cost_adjusted_count = sum(
        ledger["theorem_scope"] == "outside-current-safety-theorem"
        for ledger in ledgers
    )
    return [
        _passed_receipt("fully_funded", scope, {"identity": "cash + purchases + fees = deposits"}),
        _passed_receipt("causal_prefix", scope, {"method": "all truncated prefixes replayed"}),
        _passed_receipt("buy_only", scope, {"cash": "nonnegative", "units": "nondecreasing"}),
        _passed_receipt("unit_coverage", scope, {"scope": "frictionless guarded ledgers"}),
        _passed_receipt("direct_wealth_accounting", scope, {"identity": "cash + evaluation price * units"}),
        _passed_receipt("terminal_cash_unit_identity", scope, {"comparisons": len(results)}),
        _passed_receipt("lambda_one_collapse", scope, {"groups": len(collapsed_groups)}),
        _passed_receipt("shared_guardrail_contract", scope, {"selectors": ["neutral", "corrected"]}),
        _passed_receipt("independent_dca_accounting", scope, {"guarded_fields": "absent"}),
        _passed_receipt(
            "cost_scope_separation",
            scope,
            {
                "frictionless": "epsilon-dca",
                "cost_adjusted": "outside-current-safety-theorem",
                "cost_adjusted_ledgers": cost_adjusted_count,
            },
        ),
    ]


def _run_id(config: StudyConfig, inputs: VersionedInput) -> str:
    source_sha = _fingerprint(Path(__file__).read_bytes())
    identity = _canonical_json(
        {
            "engine_version": ENGINE_VERSION,
            "runner_sha256": source_sha,
            "config_sha256": config.sha256,
            "input_sha256": inputs.sha256,
        }
    )
    return f"smartdca-run-v1-{_fingerprint(identity.encode('utf-8'))}"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(_canonical_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: tuple[Mapping[str, Any], ...]) -> None:
    path.write_text(
        "".join(_canonical_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field) for field in fields} for row in rows)


@_fixed_decimal_context
def run_experiment(
    config: StudyConfig, inputs: VersionedInput, output_root: Path
) -> RunBundle:
    """Execute the complete deterministic run or fail before policy execution."""
    _require(isinstance(config, StudyConfig), "invalid_type", "config", "must be StudyConfig")
    _require(isinstance(inputs, VersionedInput), "invalid_type", "inputs", "must be VersionedInput")
    _require(isinstance(output_root, Path), "invalid_type", "output_root", "must be pathlib.Path")
    config_data = config.as_mapping()
    input_data = inputs.as_mapping()
    run_id = _run_id(config, inputs)
    output_root.mkdir(parents=True, exist_ok=True)
    final_directory = output_root / run_id
    if final_directory.exists():
        raise RunIdentityCollisionError(
            "run_identity_collision",
            "output_root",
            f"{run_id} already exists",
        )

    ledgers: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    for episode in input_data["episodes"]:
        evaluation_price = _decimal(episode["evaluation_price"], "evaluation_price")
        for coverage_text in config_data["coverage"]["primary"]:
            coverage = _decimal(coverage_text, "coverage")
            for mean in config_data["corrected_mean"]["primary"]:
                for cost in config_data["cost_scenarios"]:
                    key = {
                        "episode_id": episode["episode_id"],
                        "input_kind": input_data["kind"],
                        "family": episode["family"],
                        "dataset_id": episode["dataset_id"],
                        "horizon_months": episode["horizon_months"],
                        "coverage": _decimal_text(coverage),
                        "corrected_mean_config": mean["config_id"],
                        "cost_scenario": cost["cost_id"],
                    }
                    dca = _run_dca(episode["observations"], evaluation_price, cost)
                    neutral = _run_guarded(
                        episode["observations"],
                        evaluation_price,
                        coverage,
                        mean,
                        cost,
                        dca,
                        neutral=True,
                    )
                    corrected = _run_guarded(
                        episode["observations"],
                        evaluation_price,
                        coverage,
                        mean,
                        cost,
                        dca,
                        neutral=False,
                    )
                    theorem_scope = _cost_theorem_scope(cost, "cost")
                    for ledger in (dca, neutral, corrected):
                        ledger.update(key)
                        ledger["evaluation_date"] = episode["evaluation_date"]
                        ledger["evaluation_price"] = _decimal_text(evaluation_price)
                        ledger["theorem_scope"] = theorem_scope
                        ledgers.append(ledger)
                    for left, right in ((corrected, dca), (corrected, neutral), (neutral, dca)):
                        result = {**key, **_comparison(left, right, evaluation_price)}
                        result["theorem_scope"] = theorem_scope
                        results.append(result)

    ledger_rows = tuple(ledgers)
    result_rows = tuple(results)
    aggregate_rows = _aggregate_results(result_rows)
    checks = _post_execution_receipts(
        ledger_rows, result_rows, config_data, input_data
    )
    validation: dict[str, Any] = {
        "status": "passed",
        "pre_execution": {
            "configuration": "valid-and-locked",
            "input": "valid-and-versioned",
            "run_identity": "available",
        },
        "config_sha256": config.sha256,
        "input_sha256": inputs.sha256,
        "ledger_count": len(ledger_rows),
        "episode_result_count": len(result_rows),
        "checks": checks,
    }
    aggregates: dict[str, Any] = {
        "run_id": run_id,
        "episode_count": len(input_data["episodes"]),
        "ledger_count": len(ledger_rows),
        "comparison_count": len(result_rows),
        "group_count": len(aggregate_rows),
        "groups": aggregate_rows,
    }

    temporary_directory = Path(
        tempfile.mkdtemp(prefix=f".{run_id}-", dir=output_root)
    )
    try:
        _write_jsonl(temporary_directory / "ledgers.jsonl", ledger_rows)
        _write_jsonl(temporary_directory / "episode-results.jsonl", result_rows)
        _write_json(temporary_directory / "aggregates.json", aggregates)
        _write_json(temporary_directory / "validation.json", validation)
        policy_rows = [
            {
                "episode_id": row["episode_id"],
                "input_kind": row["input_kind"],
                "family": row["family"],
                "dataset_id": row["dataset_id"],
                "horizon_months": row["horizon_months"],
                "coverage": row["coverage"],
                "corrected_mean_config": row["corrected_mean_config"],
                "cost_scenario": row["cost_scenario"],
                "policy": row["policy"],
                "terminal_wealth": row["terminal_wealth"],
                "terminal_cash": row["terminal_cash"],
                "terminal_units": row["terminal_units"],
                "total_fees": row["total_fees"],
                "mean_guardrail_floor": _policy_metrics(row)[
                    "mean_guardrail_floor"
                ],
                "theorem_scope": row["theorem_scope"],
            }
            for row in ledger_rows
        ]
        policy_fields = list(policy_rows[0])
        _write_csv(temporary_directory / "policy-summary.csv", policy_rows, policy_fields)
        figure_rows = [dict(row) for row in aggregate_rows]
        figure_fields = list(figure_rows[0])
        _write_csv(temporary_directory / "figure-ready.csv", figure_rows, figure_fields)
        artifact_names = (
            "aggregates.json",
            "episode-results.jsonl",
            "figure-ready.csv",
            "ledgers.jsonl",
            "policy-summary.csv",
            "validation.json",
        )
        manifest: dict[str, Any] = {
            "schema_version": "smartdca-run-manifest/1",
            "run_id": run_id,
            "engine_version": ENGINE_VERSION,
            "runner_sha256": _fingerprint(Path(__file__).read_bytes()),
            "runtime": {"implementation": "CPython", "python": "3.12", "third_party": []},
            "config": {
                "protocol_id": config_data["protocol_id"],
                "protocol_version": config_data["protocol_version"],
                "sha256": config.sha256,
                "confirmatory_outcomes_accessed": config_data[
                    "confirmatory_outcomes_accessed"
                ],
            },
            "inputs": [
                {
                    "input_id": input_data["input_id"],
                    "version": input_data["version"],
                    "kind": input_data["kind"],
                    "sha256": inputs.sha256,
                }
            ],
            "artifacts": [
                {
                    "path": name,
                    "sha256": _fingerprint((temporary_directory / name).read_bytes()),
                }
                for name in artifact_names
            ],
        }
        _write_json(temporary_directory / "manifest.json", manifest)
        os.replace(temporary_directory, final_directory)
    except BaseException:
        for path in sorted(temporary_directory.glob("*"), reverse=True):
            path.unlink()
        temporary_directory.rmdir()
        raise

    return RunBundle(
        run_id=run_id,
        output_directory=final_directory,
        manifest=manifest,
        ledgers=ledger_rows,
        episode_results=result_rows,
        aggregates=aggregates,
        validation=validation,
    )


def main(argv: list[str] | None = None) -> int:
    """Run the public contract from a clean command-line environment."""
    parser = argparse.ArgumentParser(
        description="Execute one immutable SmartDCA empirical run."
    )
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    arguments = parser.parse_args(argv)
    try:
        bundle = run_experiment(
            load_study_config(arguments.config),
            load_versioned_input(arguments.input),
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
                "run_id": bundle.run_id,
                "output_directory": str(bundle.output_directory.resolve()),
                "manifest": str((bundle.output_directory / "manifest.json").resolve()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
