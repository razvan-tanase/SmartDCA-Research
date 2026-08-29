"""Seeded stochastic path-family orchestration over the empirical runner."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import platform
import random
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, localcontext
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


STUDY_ENGINE_VERSION = "smartdca-stochastic-study/1"
GENERATOR_VERSION = "smartdca-stochastic-paths/1"
RNG_CONTRACT = "CPython random.Random MT19937 with random() and Box-Muller normals"
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


def _iso_date(value: Any, field: str) -> date:
    _require(isinstance(value, str), "invalid_date", field, "must be an ISO date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ExperimentValidationError(
            "invalid_date", field, "must be a real YYYY-MM-DD date"
        ) from error
    _require(parsed.isoformat() == value, "invalid_date", field, "must use YYYY-MM-DD")
    return parsed


def _add_months(value: date, months: int) -> date:
    offset = value.month - 1 + months
    return date(value.year + offset // 12, offset % 12 + 1, value.day)


def _number_text(value: float) -> str:
    _require(
        math.isfinite(value) and value > 0,
        "numerical_failure",
        "generated_price",
        "generated prices must be finite and positive",
    )
    text = format(value, ".12f").rstrip("0").rstrip(".")
    return text or "0"


def _float_text(value: float) -> str:
    _require(
        math.isfinite(value),
        "numerical_failure",
        "generated_diagnostic",
        "generated diagnostics must be finite",
    )
    text = format(value, ".12f").rstrip("0").rstrip(".")
    return text or "0"


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    if value == 0:
        return "0"
    text = format(value.normalize(), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def _mean(values: list[Decimal]) -> Decimal:
    return sum(values, Decimal("0")) / Decimal(len(values))


def _median(values: list[Decimal]) -> Decimal:
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / Decimal("2")


def _quantile(values: list[Decimal], probability: Decimal) -> Decimal:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = Decimal(len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - Decimal(lower)
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def _require_parameter_set(
    parameters: Mapping[str, Any], expected: set[str], field: str
) -> None:
    _require(
        set(parameters) == expected,
        "invalid_parameter_set",
        f"{field}.parameters",
        f"must contain exactly {sorted(expected)}",
    )


def _validate_trend_parameters(
    parameters: Mapping[str, Any], field: str
) -> None:
    _require_parameter_set(
        parameters,
        {"start_price", "annual_drift", "annual_volatility"},
        field,
    )
    start = _decimal(parameters["start_price"], f"{field}.parameters.start_price")
    drift = _decimal(parameters["annual_drift"], f"{field}.parameters.annual_drift")
    volatility = _decimal(
        parameters["annual_volatility"], f"{field}.parameters.annual_volatility"
    )
    _require(
        start > 0,
        "invalid_parameter",
        f"{field}.parameters.start_price",
        "must be positive",
    )
    _require(
        Decimal("-0.25") <= drift <= Decimal("0.25"),
        "invalid_parameter",
        f"{field}.parameters.annual_drift",
        "must be between -0.25 and 0.25",
    )
    _require(
        Decimal("0.01") <= volatility <= Decimal("0.8"),
        "invalid_parameter",
        f"{field}.parameters.annual_volatility",
        "must be between 0.01 and 0.8",
    )


def _validate_mean_reversion_parameters(
    parameters: Mapping[str, Any], field: str
) -> None:
    _require_parameter_set(
        parameters,
        {
            "start_price",
            "long_run_price",
            "half_life_months",
            "stationary_log_volatility",
        },
        field,
    )
    start = _decimal(parameters["start_price"], f"{field}.parameters.start_price")
    long_run = _decimal(
        parameters["long_run_price"], f"{field}.parameters.long_run_price"
    )
    half_life = _decimal(
        parameters["half_life_months"], f"{field}.parameters.half_life_months"
    )
    volatility = _decimal(
        parameters["stationary_log_volatility"],
        f"{field}.parameters.stationary_log_volatility",
    )
    _require(
        start > 0 and long_run > 0,
        "invalid_parameter",
        f"{field}.parameters",
        "start and long-run prices must be positive",
    )
    _require(
        Decimal("1") <= half_life <= Decimal("120"),
        "invalid_parameter",
        f"{field}.parameters.half_life_months",
        "must be between 1 and 120 months",
    )
    _require(
        Decimal("0.01") <= volatility <= Decimal("1"),
        "invalid_parameter",
        f"{field}.parameters.stationary_log_volatility",
        "must be between 0.01 and 1",
    )


def _validate_stochastic_volatility_parameters(
    parameters: Mapping[str, Any], field: str
) -> None:
    _require_parameter_set(
        parameters,
        {
            "start_price",
            "annual_drift",
            "long_run_annual_volatility",
            "volatility_persistence",
            "log_volatility_of_volatility",
        },
        field,
    )
    start = _decimal(parameters["start_price"], f"{field}.parameters.start_price")
    drift = _decimal(parameters["annual_drift"], f"{field}.parameters.annual_drift")
    volatility = _decimal(
        parameters["long_run_annual_volatility"],
        f"{field}.parameters.long_run_annual_volatility",
    )
    persistence = _decimal(
        parameters["volatility_persistence"],
        f"{field}.parameters.volatility_persistence",
    )
    volatility_of_volatility = _decimal(
        parameters["log_volatility_of_volatility"],
        f"{field}.parameters.log_volatility_of_volatility",
    )
    _require(
        start > 0,
        "invalid_parameter",
        f"{field}.parameters.start_price",
        "must be positive",
    )
    _require(
        Decimal("-0.25") <= drift <= Decimal("0.25"),
        "invalid_parameter",
        f"{field}.parameters.annual_drift",
        "must be between -0.25 and 0.25",
    )
    _require(
        Decimal("0.01") <= volatility <= Decimal("0.8"),
        "invalid_parameter",
        f"{field}.parameters.long_run_annual_volatility",
        "must be between 0.01 and 0.8",
    )
    _require(
        Decimal("0") <= persistence < Decimal("0.999"),
        "invalid_parameter",
        f"{field}.parameters.volatility_persistence",
        "must be at least 0 and below 0.999",
    )
    _require(
        Decimal("0") <= volatility_of_volatility <= Decimal("1"),
        "invalid_parameter",
        f"{field}.parameters.log_volatility_of_volatility",
        "must be between 0 and 1",
    )


def _validate_regime_switching_parameters(
    parameters: Mapping[str, Any], field: str
) -> None:
    _require_parameter_set(
        parameters,
        {
            "start_price",
            "initial_regime",
            "bull_annual_drift",
            "bull_annual_volatility",
            "bull_stay_probability",
            "bear_annual_drift",
            "bear_annual_volatility",
            "bear_stay_probability",
        },
        field,
    )
    _require(
        parameters["initial_regime"] in {"bull", "bear"},
        "invalid_parameter",
        f"{field}.parameters.initial_regime",
        "must be bull or bear",
    )
    _require(
        _decimal(parameters["start_price"], f"{field}.parameters.start_price") > 0,
        "invalid_parameter",
        f"{field}.parameters.start_price",
        "must be positive",
    )
    for regime in ("bull", "bear"):
        drift = _decimal(
            parameters[f"{regime}_annual_drift"],
            f"{field}.parameters.{regime}_annual_drift",
        )
        volatility = _decimal(
            parameters[f"{regime}_annual_volatility"],
            f"{field}.parameters.{regime}_annual_volatility",
        )
        stay = _decimal(
            parameters[f"{regime}_stay_probability"],
            f"{field}.parameters.{regime}_stay_probability",
        )
        _require(
            Decimal("-0.5") <= drift <= Decimal("0.5"),
            "invalid_parameter",
            f"{field}.parameters.{regime}_annual_drift",
            "must be between -0.5 and 0.5",
        )
        _require(
            Decimal("0.01") <= volatility <= Decimal("1"),
            "invalid_parameter",
            f"{field}.parameters.{regime}_annual_volatility",
            "must be between 0.01 and 1",
        )
        _require(
            Decimal("0") <= stay <= Decimal("1"),
            "invalid_parameter",
            f"{field}.parameters.{regime}_stay_probability",
            "must be between 0 and 1",
        )


def _validate_jump_diffusion_parameters(
    parameters: Mapping[str, Any], field: str
) -> None:
    _require_parameter_set(
        parameters,
        {
            "start_price",
            "annual_drift",
            "annual_diffusion_volatility",
            "monthly_jump_probability",
            "mean_log_jump",
            "log_jump_volatility",
        },
        field,
    )
    start = _decimal(parameters["start_price"], f"{field}.parameters.start_price")
    drift = _decimal(parameters["annual_drift"], f"{field}.parameters.annual_drift")
    diffusion = _decimal(
        parameters["annual_diffusion_volatility"],
        f"{field}.parameters.annual_diffusion_volatility",
    )
    probability = _decimal(
        parameters["monthly_jump_probability"],
        f"{field}.parameters.monthly_jump_probability",
    )
    jump_mean = _decimal(
        parameters["mean_log_jump"], f"{field}.parameters.mean_log_jump"
    )
    jump_volatility = _decimal(
        parameters["log_jump_volatility"],
        f"{field}.parameters.log_jump_volatility",
    )
    _require(
        start > 0,
        "invalid_parameter",
        f"{field}.parameters.start_price",
        "must be positive",
    )
    _require(
        Decimal("-0.25") <= drift <= Decimal("0.25"),
        "invalid_parameter",
        f"{field}.parameters.annual_drift",
        "must be between -0.25 and 0.25",
    )
    _require(
        Decimal("0") <= diffusion <= Decimal("0.8"),
        "invalid_parameter",
        f"{field}.parameters.annual_diffusion_volatility",
        "must be between 0 and 0.8",
    )
    _require(
        Decimal("0") <= probability <= Decimal("0.5"),
        "invalid_parameter",
        f"{field}.parameters.monthly_jump_probability",
        "must be between 0 and 0.5",
    )
    _require(
        Decimal("-1") <= jump_mean <= Decimal("1"),
        "invalid_parameter",
        f"{field}.parameters.mean_log_jump",
        "must be between -1 and 1",
    )
    _require(
        Decimal("0") <= jump_volatility <= Decimal("1"),
        "invalid_parameter",
        f"{field}.parameters.log_jump_volatility",
        "must be between 0 and 1",
    )


def _validate_parameters(configuration: Mapping[str, Any], field: str) -> None:
    family = configuration["family"]
    parameters = configuration["parameters"]
    _require(
        isinstance(parameters, dict),
        "invalid_type",
        f"{field}.parameters",
        "must be a mapping",
    )
    definition = FAMILY_REGISTRY.get(family)
    if definition is None:
        raise ExperimentValidationError(
            "unsupported_family", f"{field}.family", f"unsupported family {family!r}"
        )
    definition.validate(parameters, field)


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
        "rng",
        "deposit",
        "start_date",
        "horizons_months",
        "seeds",
        "required_families",
        "family_configurations",
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
        "stochastic sensitivity must remain non-confirmatory",
    )
    _require(
        document["rng"] == RNG_CONTRACT,
        "unsupported_rng",
        "study.rng",
        f"must equal {RNG_CONTRACT!r}",
    )
    _require(
        _decimal(document["deposit"], "study.deposit") > 0,
        "invalid_deposit",
        "study.deposit",
        "must be positive",
    )
    start_date = _iso_date(document["start_date"], "study.start_date")
    _require(
        start_date.day == 1,
        "invalid_start_date",
        "study.start_date",
        "must be the first of a month",
    )
    horizons = document["horizons_months"]
    _require(
        isinstance(horizons, list) and bool(horizons),
        "empty_study_grid",
        "study.horizons_months",
        "must be a nonempty list",
    )
    _require(
        all(isinstance(value, int) and not isinstance(value, bool) and value > 0 for value in horizons)
        and len(horizons) == len(set(horizons)),
        "invalid_horizon_grid",
        "study.horizons_months",
        "must contain unique positive integers",
    )
    seeds = document["seeds"]
    _require(
        isinstance(seeds, list) and bool(seeds),
        "empty_study_grid",
        "study.seeds",
        "must be a nonempty list",
    )
    _require(
        all(
            isinstance(value, int)
            and not isinstance(value, bool)
            and 0 <= value < 2**63
            for value in seeds
        )
        and len(seeds) == len(set(seeds)),
        "invalid_seed_grid",
        "study.seeds",
        "must contain unique nonnegative 63-bit integers",
    )
    required = document["required_families"]
    _require(
        isinstance(required, list) and bool(required)
        and all(isinstance(value, str) and bool(value) for value in required)
        and len(required) == len(set(required)),
        "invalid_family_grid",
        "study.required_families",
        "must contain unique nonempty family identifiers",
    )
    configurations = document["family_configurations"]
    _require(
        isinstance(configurations, list) and bool(configurations),
        "empty_study_grid",
        "study.family_configurations",
        "must be a nonempty list",
    )
    config_ids: list[str] = []
    primary_families: set[str] = set()
    for index, configuration in enumerate(configurations):
        field = f"study.family_configurations[{index}]"
        _require(isinstance(configuration, dict), "invalid_type", field, "must be a mapping")
        for required_field in ("config_id", "family", "tier", "description", "parameters"):
            _require(required_field in configuration, "missing_field", f"{field}.{required_field}", "is required")
        for identifier in ("config_id", "family", "description"):
            _require(
                isinstance(configuration[identifier], str) and bool(configuration[identifier]),
                "invalid_identifier",
                f"{field}.{identifier}",
                "must be a nonempty string",
            )
        _require(
            configuration["tier"] in {"primary", "exploratory"},
            "invalid_analysis_tier",
            f"{field}.tier",
            "must be primary or exploratory",
        )
        _require(
            configuration["family"] in SUPPORTED_FAMILIES,
            "unsupported_family",
            f"{field}.family",
            f"must be one of {sorted(SUPPORTED_FAMILIES)}",
        )
        config_ids.append(configuration["config_id"])
        if configuration["tier"] == "primary":
            primary_families.add(configuration["family"])
        _validate_parameters(configuration, field)
    _require(
        len(config_ids) == len(set(config_ids)),
        "duplicate_configuration",
        "study.family_configurations",
        "config_id values must be unique",
    )
    _require(
        set(required) <= primary_families,
        "missing_required_family",
        "study.required_families",
        "every required family needs a primary configuration",
    )


@dataclass(frozen=True)
class StochasticStudy:
    """Validated immutable stochastic-family study specification."""

    canonical_document: str
    sha256: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "StochasticStudy":
        document = _mapping_copy(value, "study")
        _validate_study(document)
        canonical = _canonical_json(document)
        return cls(canonical, _fingerprint(canonical.encode("utf-8")))

    @classmethod
    def from_json_bytes(cls, payload: bytes) -> "StochasticStudy":
        document = _decode_json_document(payload, "study")
        _validate_study(document)
        return cls(_canonical_json(document), _fingerprint(payload))

    def as_mapping(self) -> dict[str, Any]:
        return json.loads(self.canonical_document)


def load_stochastic_study(path: Path) -> StochasticStudy:
    """Load and fingerprint the exact bytes of a saved stochastic study."""
    _require(isinstance(path, Path), "invalid_type", "study_path", "must be pathlib.Path")
    try:
        payload = path.read_bytes()
    except OSError as error:
        raise ExperimentValidationError(
            "unreadable_study", "study_path", str(error)
        ) from error
    return StochasticStudy.from_json_bytes(payload)


@dataclass(frozen=True)
class StochasticStudyBundle:
    """Public result of one immutable stochastic path-family study."""

    study_run_id: str
    output_directory: Path
    manifest: Mapping[str, Any]
    path_attempts: tuple[Mapping[str, Any], ...]
    runner: RunBundle


class _NormalStream:
    def __init__(self, seed: int) -> None:
        self._random = random.Random(seed)
        self._spare: float | None = None

    def uniform(self) -> float:
        return self._random.random()

    def normal(self) -> float:
        if self._spare is not None:
            value = self._spare
            self._spare = None
            return value
        first = self._random.random()
        while first == 0:
            first = self._random.random()
        second = self._random.random()
        radius = math.sqrt(-2 * math.log(first))
        angle = 2 * math.pi * second
        self._spare = radius * math.sin(angle)
        return radius * math.cos(angle)


@dataclass(frozen=True)
class _GeneratedPath:
    prices: tuple[str, ...]
    trace: tuple[Mapping[str, Any], ...]


def _generate_trend(
    parameters: Mapping[str, Any], seed: int, steps: int
) -> _GeneratedPath:
    start = float(parameters["start_price"])
    drift = float(parameters["annual_drift"])
    volatility = float(parameters["annual_volatility"])
    stream = _NormalStream(seed)
    prices = [start]
    trace: list[dict[str, Any]] = []
    log_price = math.log(start)
    monthly_drift = (drift - volatility * volatility / 2) / 12
    monthly_volatility = volatility / math.sqrt(12)
    for _ in range(steps):
        shock = stream.normal()
        log_price += monthly_drift + monthly_volatility * shock
        prices.append(math.exp(log_price))
        trace.append({"normal_shock": _float_text(shock)})
    return _GeneratedPath(
        tuple(_number_text(value) for value in prices), tuple(trace)
    )


def _generate_mean_reversion(
    parameters: Mapping[str, Any], seed: int, steps: int
) -> _GeneratedPath:
    start = float(parameters["start_price"])
    long_run = math.log(float(parameters["long_run_price"]))
    half_life = float(parameters["half_life_months"])
    stationary_volatility = float(parameters["stationary_log_volatility"])
    persistence = math.pow(0.5, 1 / half_life)
    innovation_volatility = stationary_volatility * math.sqrt(1 - persistence**2)
    stream = _NormalStream(seed)
    log_price = math.log(start)
    prices = [start]
    trace: list[dict[str, Any]] = []
    for _ in range(steps):
        shock = stream.normal()
        log_price = (
            long_run
            + persistence * (log_price - long_run)
            + innovation_volatility * shock
        )
        prices.append(math.exp(log_price))
        trace.append({"normal_shock": _float_text(shock)})
    return _GeneratedPath(
        tuple(_number_text(value) for value in prices), tuple(trace)
    )


def _generate_stochastic_volatility(
    parameters: Mapping[str, Any], seed: int, steps: int
) -> _GeneratedPath:
    start = float(parameters["start_price"])
    drift = float(parameters["annual_drift"])
    long_run_volatility = float(parameters["long_run_annual_volatility"])
    persistence = float(parameters["volatility_persistence"])
    volatility_of_volatility = float(parameters["log_volatility_of_volatility"])
    innovation_volatility = volatility_of_volatility * math.sqrt(1 - persistence**2)
    stream = _NormalStream(seed)
    log_price = math.log(start)
    log_volatility = math.log(long_run_volatility)
    prices = [start]
    trace: list[dict[str, Any]] = []
    for _ in range(steps):
        volatility_shock = stream.normal()
        log_volatility = (
            math.log(long_run_volatility)
            + persistence * (log_volatility - math.log(long_run_volatility))
            + innovation_volatility * volatility_shock
        )
        annual_volatility = math.exp(log_volatility)
        return_shock = stream.normal()
        log_price += (
            (drift - annual_volatility**2 / 2) / 12
            + annual_volatility / math.sqrt(12) * return_shock
        )
        prices.append(math.exp(log_price))
        trace.append(
            {
                "annual_volatility": _number_text(annual_volatility),
                "volatility_shock": _float_text(volatility_shock),
                "return_shock": _float_text(return_shock),
            }
        )
    return _GeneratedPath(
        tuple(_number_text(value) for value in prices), tuple(trace)
    )


def _generate_regime_switching(
    parameters: Mapping[str, Any], seed: int, steps: int
) -> _GeneratedPath:
    start = float(parameters["start_price"])
    regime = str(parameters["initial_regime"])
    stream = _NormalStream(seed)
    log_price = math.log(start)
    prices = [start]
    trace: list[dict[str, Any]] = []
    for _ in range(steps):
        current_regime = regime
        drift = float(parameters[f"{regime}_annual_drift"])
        volatility = float(parameters[f"{regime}_annual_volatility"])
        return_shock = stream.normal()
        log_price += (
            (drift - volatility**2 / 2) / 12
            + volatility / math.sqrt(12) * return_shock
        )
        prices.append(math.exp(log_price))
        switched = stream.uniform() > float(
            parameters[f"{regime}_stay_probability"]
        )
        if switched:
            regime = "bear" if regime == "bull" else "bull"
        trace.append(
            {
                "regime": current_regime,
                "return_shock": _float_text(return_shock),
                "switched_after_month": switched,
            }
        )
    return _GeneratedPath(
        tuple(_number_text(value) for value in prices), tuple(trace)
    )


def _generate_jump_diffusion(
    parameters: Mapping[str, Any], seed: int, steps: int
) -> _GeneratedPath:
    start = float(parameters["start_price"])
    drift = float(parameters["annual_drift"])
    diffusion = float(parameters["annual_diffusion_volatility"])
    jump_probability = float(parameters["monthly_jump_probability"])
    jump_mean = float(parameters["mean_log_jump"])
    jump_volatility = float(parameters["log_jump_volatility"])
    stream = _NormalStream(seed)
    log_price = math.log(start)
    prices = [start]
    trace: list[dict[str, Any]] = []
    for month in range(1, steps + 1):
        return_shock = stream.normal()
        log_return = (
            (drift - diffusion**2 / 2) / 12
            + diffusion / math.sqrt(12) * return_shock
        )
        jumped = stream.uniform() < jump_probability
        realized_jump: float | None = None
        if jumped:
            realized_jump = jump_mean + jump_volatility * stream.normal()
            log_return += realized_jump
        log_price += log_return
        prices.append(math.exp(log_price))
        trace.append(
            {
                "month": month,
                "return_shock": _float_text(return_shock),
                "jump_occurred": jumped,
                "realized_log_jump": (
                    _float_text(realized_jump) if realized_jump is not None else None
                ),
            }
        )
    return _GeneratedPath(
        tuple(_number_text(value) for value in prices), tuple(trace)
    )


def _generate_path(
    configuration: Mapping[str, Any], seed: int, steps: int
) -> _GeneratedPath:
    definition = FAMILY_REGISTRY.get(configuration["family"])
    if definition is None:
        raise ExperimentValidationError(
            "unsupported_family", "configuration.family", "family is not implemented"
        )
    return definition.generate(configuration["parameters"], seed, steps)


def _path_statistics(prices: tuple[str, ...]) -> dict[str, Any]:
    numeric = [float(value) for value in prices]
    returns = [
        math.log(right / left)
        for left, right in zip(numeric[:-1], numeric[1:], strict=True)
    ]
    mean_return = sum(returns) / len(returns)
    realized_volatility = math.sqrt(
        12 * sum((value - mean_return) ** 2 for value in returns) / len(returns)
    )
    peak = numeric[0]
    maximum_drawdown = 0.0
    for price in numeric:
        peak = max(peak, price)
        maximum_drawdown = max(maximum_drawdown, (peak - price) / peak)
    return {
        "annualized_log_return": _float_text(
            math.log(numeric[-1] / numeric[0]) * 12 / len(returns)
        ),
        "annualized_realized_volatility": _float_text(realized_volatility),
        "maximum_drawdown_fraction": _float_text(maximum_drawdown),
        "minimum_price": _number_text(min(numeric)),
        "maximum_price": _number_text(max(numeric)),
        "terminal_price": prices[-1],
    }


def _no_process_diagnostics(
    trace: tuple[Mapping[str, Any], ...]
) -> dict[str, Any]:
    return {}


def _stochastic_volatility_diagnostics(
    trace: tuple[Mapping[str, Any], ...]
) -> dict[str, Any]:
    values = [float(row["annual_volatility"]) for row in trace]
    return {
        "minimum_annual_volatility": _number_text(min(values)),
        "mean_annual_volatility": _number_text(sum(values) / len(values)),
        "maximum_annual_volatility": _number_text(max(values)),
    }


def _regime_switching_diagnostics(
    trace: tuple[Mapping[str, Any], ...]
) -> dict[str, Any]:
    return {
        "bull_months": sum(row["regime"] == "bull" for row in trace),
        "bear_months": sum(row["regime"] == "bear" for row in trace),
        "regime_switches": sum(
            row["switched_after_month"] is True for row in trace
        ),
    }


def _jump_diffusion_diagnostics(
    trace: tuple[Mapping[str, Any], ...]
) -> dict[str, Any]:
    jumps = [
        float(row["realized_log_jump"])
        for row in trace
        if row["jump_occurred"] is True
    ]
    return {
        "jump_count": len(jumps),
        "jump_months": [
            row["month"] for row in trace if row["jump_occurred"] is True
        ],
        "mean_realized_log_jump": (
            _float_text(sum(jumps) / len(jumps)) if jumps else None
        ),
    }


@dataclass(frozen=True)
class _FamilyDefinition:
    validate: Callable[[Mapping[str, Any], str], None]
    generate: Callable[[Mapping[str, Any], int, int], _GeneratedPath]
    diagnostics: Callable[[tuple[Mapping[str, Any], ...]], dict[str, Any]]


FAMILY_REGISTRY = {
    "trend": _FamilyDefinition(
        _validate_trend_parameters, _generate_trend, _no_process_diagnostics
    ),
    "mean_reversion": _FamilyDefinition(
        _validate_mean_reversion_parameters,
        _generate_mean_reversion,
        _no_process_diagnostics,
    ),
    "stochastic_volatility": _FamilyDefinition(
        _validate_stochastic_volatility_parameters,
        _generate_stochastic_volatility,
        _stochastic_volatility_diagnostics,
    ),
    "regime_switching": _FamilyDefinition(
        _validate_regime_switching_parameters,
        _generate_regime_switching,
        _regime_switching_diagnostics,
    ),
    "jump_diffusion": _FamilyDefinition(
        _validate_jump_diffusion_parameters,
        _generate_jump_diffusion,
        _jump_diffusion_diagnostics,
    ),
}
SUPPORTED_FAMILIES = frozenset(FAMILY_REGISTRY)


def _process_diagnostics(
    family: str, trace: tuple[Mapping[str, Any], ...]
) -> dict[str, Any]:
    definition = FAMILY_REGISTRY.get(family)
    if definition is None:
        raise ExperimentValidationError(
            "unsupported_family", "configuration.family", "family is not implemented"
        )
    return definition.diagnostics(trace)


def _source_sha256() -> str:
    return _fingerprint(Path(__file__).read_bytes())


def _runner_source_sha256() -> str:
    return _fingerprint(SHARED_RUNNER_SOURCE.read_bytes())


def _write_json(path: Path, value: Any) -> None:
    path.write_text(_canonical_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: tuple[Mapping[str, Any], ...]) -> None:
    path.write_text(
        "".join(_canonical_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def _write_csv(
    path: Path, rows: list[Mapping[str, Any]], fields: list[str]
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field) for field in fields} for row in rows)


def _read_jsonl(path: Path) -> tuple[dict[str, Any], ...]:
    return tuple(
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    )


def _mean_field(
    members: list[Mapping[str, Any]], field: str
) -> str | None:
    values = [
        _decimal(row[field], f"aggregate.{field}")
        for row in members
        if row[field] is not None
    ]
    return _decimal_text(_mean(values)) if values else None


def _aggregate_stochastic_results(
    config_document: Mapping[str, Any],
    study_document: Mapping[str, Any],
    results: tuple[Mapping[str, Any], ...],
    attempts: tuple[Mapping[str, Any], ...],
) -> dict[str, Any]:
    comparisons = (
        "corrected_guarded_vs_dca",
        "corrected_guarded_vs_neutral_guarded",
        "neutral_guarded_vs_dca",
    )
    result_groups: dict[tuple[str, int, str, str, str, str], list[Mapping[str, Any]]] = {}
    for result in results:
        metadata = next(
            row for row in attempts if row["attempt_id"] == result["episode_id"]
        )
        key = (
            metadata["config_id"],
            result["horizon_months"],
            result["coverage"],
            result["corrected_mean_config"],
            result["cost_scenario"],
            result["comparison"],
        )
        result_groups.setdefault(key, []).append(result)
    attempt_groups: dict[tuple[str, int], list[Mapping[str, Any]]] = {}
    for attempt in attempts:
        attempt_groups.setdefault(
            (attempt["config_id"], attempt["horizon_months"]), []
        ).append(attempt)
    groups: list[dict[str, Any]] = []
    mean_ids = [
        value["config_id"] for value in config_document["corrected_mean"]["primary"]
    ]
    for configuration in study_document["family_configurations"]:
        for horizon in study_document["horizons_months"]:
            path_attempts = attempt_groups[(configuration["config_id"], horizon)]
            for coverage in config_document["coverage"]["primary"]:
                for mean_id in mean_ids:
                    for cost in config_document["cost_scenarios"]:
                        for comparison in comparisons:
                            key = (
                                configuration["config_id"],
                                horizon,
                                coverage,
                                mean_id,
                                cost["cost_id"],
                                comparison,
                            )
                            attempted_results = sorted(
                                result_groups.get(key, []),
                                key=lambda row: row["episode_id"],
                            )
                            members = [
                                row
                                for row in attempted_results
                                if row["result_status"] == "included"
                            ]
                            relative = [
                                _decimal(
                                    row["relative_terminal_wealth_gap"],
                                    "aggregate.relative_terminal_wealth_gap",
                                )
                                for row in members
                            ]
                            wealth_gaps = [
                                _decimal(
                                    row["terminal_wealth_gap"],
                                    "aggregate.terminal_wealth_gap",
                                )
                                for row in members
                            ]
                            ratios = [
                                _decimal(row["wealth_ratio"], "aggregate.wealth_ratio")
                                for row in members
                            ]
                            exclusions: dict[str, int] = {}
                            for attempt in path_attempts:
                                if attempt["status"] == "excluded":
                                    reason = attempt["exclusion_reason"]
                                    exclusions[reason] = exclusions.get(reason, 0) + 1
                            for row in attempted_results:
                                if row["result_status"] == "excluded":
                                    reason = row["exclusion_reason"]
                                    exclusions[reason] = exclusions.get(reason, 0) + 1
                            group: dict[str, Any] = {
                                "analysis_tier": configuration["tier"],
                                "family": configuration["family"],
                                "generator_config_id": configuration["config_id"],
                                "generator_parameters": configuration["parameters"],
                                "horizon_months": horizon,
                                "coverage": coverage,
                                "corrected_mean_config": mean_id,
                                "cost_scenario": cost["cost_id"],
                                "comparison": comparison,
                                "theorem_scope": cost["theorem_scope"],
                                "attempted_count": len(path_attempts),
                                "generated_count": sum(
                                    row["status"] == "generated" for row in path_attempts
                                ),
                                "sample_count": len(members),
                                "excluded_count": len(path_attempts) - len(members),
                                "exclusions_by_reason": dict(sorted(exclusions.items())),
                                "relative_terminal_wealth_gap_distribution": [
                                    {
                                        "episode_id": row["episode_id"],
                                        "value": row["relative_terminal_wealth_gap"],
                                    }
                                    for row in members
                                ],
                                "mean_terminal_wealth_gap": (
                                    _decimal_text(_mean(wealth_gaps))
                                    if wealth_gaps
                                    else None
                                ),
                                "mean_wealth_ratio": (
                                    _decimal_text(_mean(ratios)) if ratios else None
                                ),
                                "win_count": sum(value > 0 for value in wealth_gaps),
                                "tie_count": sum(value == 0 for value in wealth_gaps),
                                "loss_count": sum(value < 0 for value in wealth_gaps),
                            }
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
                                group.update(
                                    {
                                        "mean_relative_terminal_wealth_gap": None,
                                        "median_relative_terminal_wealth_gap": None,
                                        "minimum_relative_terminal_wealth_gap": None,
                                        "maximum_relative_terminal_wealth_gap": None,
                                        "downside_quantile_0.05": None,
                                        "downside_quantile_0.10": None,
                                        "downside_quantile_0.25": None,
                                        "worst_observed_relative_shortfall": None,
                                    }
                                )
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
                            group["mean_left_purchase_count"] = (
                                _decimal_text(
                                    _mean(
                                        [
                                            Decimal(row["left_purchase_count"])
                                            for row in members
                                        ]
                                    )
                                )
                                if members
                                else None
                            )
                            group["mean_right_purchase_count"] = (
                                _decimal_text(
                                    _mean(
                                        [
                                            Decimal(row["right_purchase_count"])
                                            for row in members
                                        ]
                                    )
                                )
                                if members
                                else None
                            )
                            groups.append(group)
    return {
        "group_count": len(groups),
        "attempted_path_count": len(attempts),
        "generated_path_count": sum(row["status"] == "generated" for row in attempts),
        "excluded_path_count": sum(row["status"] == "excluded" for row in attempts),
        "groups": groups,
    }


def _independent_result_statistics(
    members: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Recompute aggregate values without using either production aggregator."""
    relative = [
        _decimal(row["relative_terminal_wealth_gap"], "reconcile.relative_gap")
        for row in members
        if row["relative_terminal_wealth_gap"] is not None
    ]
    wealth_gaps = [
        _decimal(row["terminal_wealth_gap"], "reconcile.wealth_gap")
        for row in members
    ]
    ratios = [
        _decimal(row["wealth_ratio"], "reconcile.wealth_ratio")
        for row in members
        if row["wealth_ratio"] is not None
    ]
    result: dict[str, Any] = {
        "mean_terminal_wealth_gap": (
            _decimal_text(_mean(wealth_gaps)) if wealth_gaps else None
        ),
        "mean_wealth_ratio": _decimal_text(_mean(ratios)) if ratios else None,
        "win_count": sum(value > 0 for value in wealth_gaps),
        "tie_count": sum(value == 0 for value in wealth_gaps),
        "loss_count": sum(value < 0 for value in wealth_gaps),
    }
    if relative:
        minimum = min(relative)
        result.update(
            {
                "mean_relative_terminal_wealth_gap": _decimal_text(_mean(relative)),
                "median_relative_terminal_wealth_gap": _decimal_text(
                    _median(relative)
                ),
                "minimum_relative_terminal_wealth_gap": _decimal_text(minimum),
                "maximum_relative_terminal_wealth_gap": _decimal_text(max(relative)),
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
        result.update(
            {
                "mean_relative_terminal_wealth_gap": None,
                "median_relative_terminal_wealth_gap": None,
                "minimum_relative_terminal_wealth_gap": None,
                "maximum_relative_terminal_wealth_gap": None,
                "downside_quantile_0.05": None,
                "downside_quantile_0.10": None,
                "downside_quantile_0.25": None,
                "worst_observed_relative_shortfall": None,
            }
        )
    for source_field in (
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
        }.get(source_field, f"mean_{source_field}")
        values = [
            _decimal(row[source_field], f"reconcile.{source_field}")
            for row in members
            if row[source_field] is not None
        ]
        result[output_field] = _decimal_text(_mean(values)) if values else None
    for side in ("left", "right"):
        counts = [Decimal(row[f"{side}_purchase_count"]) for row in members]
        result[f"mean_{side}_purchase_count"] = (
            _decimal_text(_mean(counts)) if counts else None
        )
    return result


def _study_group_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        row["generator_config_id"],
        row["horizon_months"],
        row["coverage"],
        row["corrected_mean_config"],
        row["cost_scenario"],
        row["comparison"],
        row["theorem_scope"],
    )


def _runner_group_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
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


def _append_mapping_mismatches(
    mismatches: list[dict[str, Any]],
    scope: str,
    key: tuple[Any, ...] | str,
    actual: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> None:
    for field in sorted(set(actual) | set(expected)):
        actual_value = actual.get(field, "<missing>")
        expected_value = expected.get(field, "<missing>")
        if actual_value != expected_value:
            mismatches.append(
                {
                    "scope": scope,
                    "group": list(key) if isinstance(key, tuple) else key,
                    "field": field,
                    "actual": actual_value,
                    "independent": expected_value,
                }
            )


def _reconcile_stochastic_aggregates(
    stochastic_aggregates: Mapping[str, Any],
    runner_aggregates: Mapping[str, Any],
    results: tuple[Mapping[str, Any], ...],
    attempts: tuple[Mapping[str, Any], ...],
) -> dict[str, Any]:
    """Independently reconcile every serialized study and runner aggregate."""
    attempt_by_episode = {
        row["episode_id"]: row for row in attempts if row["episode_id"] is not None
    }
    attempt_groups: dict[tuple[str, int], list[Mapping[str, Any]]] = {}
    for attempt in attempts:
        attempt_groups.setdefault(
            (attempt["config_id"], attempt["horizon_months"]), []
        ).append(attempt)

    study_result_groups: dict[tuple[Any, ...], list[Mapping[str, Any]]] = {}
    runner_result_groups: dict[tuple[Any, ...], list[Mapping[str, Any]]] = {}
    axes: set[tuple[Any, ...]] = set()
    for result in results:
        attempt = attempt_by_episode[result["episode_id"]]
        study_key = (
            attempt["config_id"],
            result["horizon_months"],
            result["coverage"],
            result["corrected_mean_config"],
            result["cost_scenario"],
            result["comparison"],
            result["theorem_scope"],
        )
        study_result_groups.setdefault(study_key, []).append(result)
        runner_result_groups.setdefault(_runner_group_key(result), []).append(result)
        axes.add(
            (
                result["coverage"],
                result["corrected_mean_config"],
                result["cost_scenario"],
                result["comparison"],
                result["theorem_scope"],
            )
        )

    expected_study_groups: dict[tuple[Any, ...], dict[str, Any]] = {}
    for (config_id, horizon), path_attempts in sorted(attempt_groups.items()):
        metadata = path_attempts[0]
        for coverage, mean_id, cost_id, comparison, theorem_scope in sorted(axes):
            key = (
                config_id,
                horizon,
                coverage,
                mean_id,
                cost_id,
                comparison,
                theorem_scope,
            )
            attempted_results = sorted(
                study_result_groups.get(key, []),
                key=lambda row: row["episode_id"],
            )
            members = [
                row for row in attempted_results if row["result_status"] == "included"
            ]
            exclusions: dict[str, int] = {}
            for attempt in path_attempts:
                if attempt["status"] == "excluded":
                    reason = attempt["exclusion_reason"]
                    exclusions[reason] = exclusions.get(reason, 0) + 1
            for result in attempted_results:
                if result["result_status"] == "excluded":
                    reason = result["exclusion_reason"]
                    exclusions[reason] = exclusions.get(reason, 0) + 1
            expected_study_groups[key] = {
                "analysis_tier": metadata["tier"],
                "family": metadata["family"],
                "generator_config_id": config_id,
                "generator_parameters": metadata["parameters"],
                "horizon_months": horizon,
                "coverage": coverage,
                "corrected_mean_config": mean_id,
                "cost_scenario": cost_id,
                "comparison": comparison,
                "theorem_scope": theorem_scope,
                "attempted_count": len(path_attempts),
                "generated_count": sum(
                    attempt["status"] == "generated" for attempt in path_attempts
                ),
                "sample_count": len(members),
                "excluded_count": len(path_attempts) - len(members),
                "exclusions_by_reason": dict(sorted(exclusions.items())),
                "relative_terminal_wealth_gap_distribution": [
                    {
                        "episode_id": row["episode_id"],
                        "value": row["relative_terminal_wealth_gap"],
                    }
                    for row in members
                ],
                **_independent_result_statistics(members),
            }

    expected_runner_groups: dict[tuple[Any, ...], dict[str, Any]] = {}
    runner_omitted_statistics = {
        "worst_observed_relative_shortfall",
        "mean_cash_contribution",
        "mean_unit_contribution",
        "mean_identity_residual",
    }
    for key, attempted_results in runner_result_groups.items():
        ordered_results = sorted(
            attempted_results, key=lambda row: row["episode_id"]
        )
        members = [
            row for row in ordered_results if row["result_status"] == "included"
        ]
        statistics = {
            field: value
            for field, value in _independent_result_statistics(members).items()
            if field not in runner_omitted_statistics
        }
        (
            input_kind,
            family,
            dataset_id,
            horizon,
            coverage,
            mean_id,
            cost_id,
            comparison,
            theorem_scope,
        ) = key
        expected_runner_groups[key] = {
            "input_kind": input_kind,
            "family": family,
            "dataset_id": dataset_id,
            "horizon_months": horizon,
            "coverage": coverage,
            "corrected_mean_config": mean_id,
            "cost_scenario": cost_id,
            "comparison": comparison,
            "theorem_scope": theorem_scope,
            "attempted_count": len(ordered_results),
            "sample_count": sum(
                row["relative_terminal_wealth_gap"] is not None for row in members
            ),
            "excluded_count": len(ordered_results) - len(members),
            "uncertainty_status": "not-estimated-by-canonical-run",
            **statistics,
        }

    mismatches: list[dict[str, Any]] = []
    actual_study_groups = {
        _study_group_key(group): group for group in stochastic_aggregates["groups"]
    }
    if len(actual_study_groups) != len(stochastic_aggregates["groups"]):
        mismatches.append(
            {
                "scope": "study",
                "group": "all",
                "field": "duplicate_group_key",
                "actual": len(stochastic_aggregates["groups"]),
                "independent": len(actual_study_groups),
            }
        )
    for key in sorted(set(actual_study_groups) | set(expected_study_groups)):
        _append_mapping_mismatches(
            mismatches,
            "study",
            key,
            actual_study_groups.get(key, {}),
            expected_study_groups.get(key, {}),
        )
    study_top_level = {
        field: stochastic_aggregates.get(field, "<missing>")
        for field in (
            "group_count",
            "attempted_path_count",
            "generated_path_count",
            "excluded_path_count",
        )
    }
    expected_study_top_level = {
        "group_count": len(expected_study_groups),
        "attempted_path_count": len(attempts),
        "generated_path_count": sum(row["status"] == "generated" for row in attempts),
        "excluded_path_count": sum(row["status"] == "excluded" for row in attempts),
    }
    _append_mapping_mismatches(
        mismatches,
        "study",
        "top-level",
        study_top_level,
        expected_study_top_level,
    )
    if set(stochastic_aggregates) != {
        "group_count",
        "attempted_path_count",
        "generated_path_count",
        "excluded_path_count",
        "groups",
    }:
        mismatches.append(
            {
                "scope": "study",
                "group": "top-level",
                "field": "keys",
                "actual": sorted(stochastic_aggregates),
                "independent": [
                    "attempted_path_count",
                    "excluded_path_count",
                    "generated_path_count",
                    "group_count",
                    "groups",
                ],
            }
        )

    actual_runner_groups = {
        _runner_group_key(group): group for group in runner_aggregates["groups"]
    }
    if len(actual_runner_groups) != len(runner_aggregates["groups"]):
        mismatches.append(
            {
                "scope": "runner",
                "group": "all",
                "field": "duplicate_group_key",
                "actual": len(runner_aggregates["groups"]),
                "independent": len(actual_runner_groups),
            }
        )
    for key in sorted(set(actual_runner_groups) | set(expected_runner_groups)):
        _append_mapping_mismatches(
            mismatches,
            "runner",
            key,
            actual_runner_groups.get(key, {}),
            expected_runner_groups.get(key, {}),
        )
    runner_top_level = {
        field: runner_aggregates.get(field, "<missing>")
        for field in ("episode_count", "ledger_count", "comparison_count", "group_count")
    }
    expected_runner_top_level = {
        "episode_count": len({row["episode_id"] for row in results}),
        "ledger_count": len(results),
        "comparison_count": len(results),
        "group_count": len(expected_runner_groups),
    }
    _append_mapping_mismatches(
        mismatches,
        "runner",
        "top-level",
        runner_top_level,
        expected_runner_top_level,
    )
    if set(runner_aggregates) != {
        "run_id",
        "episode_count",
        "ledger_count",
        "comparison_count",
        "group_count",
        "groups",
    }:
        mismatches.append(
            {
                "scope": "runner",
                "group": "top-level",
                "field": "keys",
                "actual": sorted(runner_aggregates),
                "independent": [
                    "comparison_count",
                    "episode_count",
                    "group_count",
                    "groups",
                    "ledger_count",
                    "run_id",
                ],
            }
        )

    if mismatches:
        raise AssertionError(
            "independent aggregate reconciliation found "
            f"{len(mismatches)} mismatch(es); first={mismatches[0]!r}"
        )
    study_field_count = len(next(iter(expected_study_groups.values())))
    runner_field_count = len(next(iter(expected_runner_groups.values())))
    return {
        "status": "passed",
        "method": "independently regrouped serialized episode results and attempts; compared every study and runner aggregate field",
        "reconciled_group_count": len(expected_study_groups),
        "study_group_field_count": study_field_count,
        "runner_group_field_count": runner_field_count,
        "reconciled_study_value_count": (
            len(expected_study_groups) * study_field_count + 4
        ),
        "reconciled_runner_value_count": (
            len(expected_runner_groups) * runner_field_count + 4
        ),
        "mismatch_count": 0,
    }


def reconcile_stochastic_aggregates(
    stochastic_aggregates: Mapping[str, Any],
    runner_aggregates: Mapping[str, Any],
    results: tuple[Mapping[str, Any], ...],
    attempts: tuple[Mapping[str, Any], ...],
) -> dict[str, Any]:
    """Independently reconcile every aggregate at the runner's precision."""
    with localcontext() as decimal_context:
        decimal_context.prec = 60
        return _reconcile_stochastic_aggregates(
            stochastic_aggregates,
            runner_aggregates,
            results,
            attempts,
        )


def _enrich_results(
    results: tuple[Mapping[str, Any], ...],
    attempts: tuple[Mapping[str, Any], ...],
) -> tuple[dict[str, Any], ...]:
    attempt_by_episode = {
        row["episode_id"]: row
        for row in attempts
        if row["status"] == "generated"
    }
    enriched = []
    for result in results:
        attempt = attempt_by_episode[result["episode_id"]]
        enriched.append(
            {
                "analysis_tier": attempt["tier"],
                "generator_config_id": attempt["config_id"],
                "generator_parameters": attempt["parameters"],
                "seed": attempt["seed"],
                "path_sha256": attempt["path_sha256"],
                "path_statistics": attempt["path_statistics"],
                "process_diagnostics": attempt["process_diagnostics"],
                **result,
            }
        )
    return tuple(enriched)


def _figure_rows(stochastic_aggregates: Mapping[str, Any]) -> list[dict[str, Any]]:
    fields = (
        "analysis_tier",
        "family",
        "generator_config_id",
        "horizon_months",
        "coverage",
        "corrected_mean_config",
        "cost_scenario",
        "comparison",
        "theorem_scope",
        "attempted_count",
        "generated_count",
        "sample_count",
        "excluded_count",
        "mean_terminal_wealth_gap",
        "mean_wealth_ratio",
        "mean_relative_terminal_wealth_gap",
        "median_relative_terminal_wealth_gap",
        "minimum_relative_terminal_wealth_gap",
        "maximum_relative_terminal_wealth_gap",
        "downside_quantile_0.05",
        "downside_quantile_0.10",
        "downside_quantile_0.25",
        "worst_observed_relative_shortfall",
        "win_count",
        "tie_count",
        "loss_count",
        "mean_terminal_cash_gap",
        "mean_terminal_unit_gap",
        "mean_cash_contribution",
        "mean_unit_contribution",
        "mean_identity_residual",
        "mean_left_cash_drag",
        "mean_right_cash_drag",
        "mean_left_asset_exposure",
        "mean_right_asset_exposure",
        "mean_left_guardrail_activation_frequency",
        "mean_right_guardrail_activation_frequency",
        "mean_left_guardrail_floor",
        "mean_right_guardrail_floor",
        "mean_left_purchase_count",
        "mean_right_purchase_count",
        "mean_left_total_fees",
        "mean_right_total_fees",
    )
    return [
        {field: group.get(field) for field in fields}
        for group in stochastic_aggregates["groups"]
    ]


def _percent(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{Decimal(str(value)) * Decimal('100'):.3f}%"


def _render_report_tables(
    study_document: Mapping[str, Any],
    stochastic_aggregates: Mapping[str, Any],
    attempts: tuple[Mapping[str, Any], ...],
) -> str:
    lines = [
        "## Complete retained grid",
        "",
        "| Tier | Family | Generator configuration | Attempted | Generated | Excluded |",
        "|---|---|---|---:|---:|---:|",
    ]
    for configuration in study_document["family_configurations"]:
        selected = [
            row for row in attempts if row["config_id"] == configuration["config_id"]
        ]
        lines.append(
            "| "
            + " | ".join(
                (
                    configuration["tier"],
                    configuration["family"],
                    configuration["config_id"],
                    str(len(selected)),
                    str(sum(row["status"] == "generated" for row in selected)),
                    str(sum(row["status"] == "excluded" for row in selected)),
                )
            )
            + " |"
        )
    maximum_horizon = max(study_document["horizons_months"])
    selected_coverage = (
        "0.75"
        if any(group["coverage"] == "0.75" for group in stochastic_aggregates["groups"])
        else next(
            group["coverage"]
            for group in stochastic_aggregates["groups"]
            if group["coverage"] != "1"
        )
    )
    for tier, heading in (
        ("primary", "Primary frictionless distribution slice"),
        ("exploratory", "Exploratory sensitivity distribution slice"),
    ):
        lines.extend(
            [
                "",
                f"## {heading}",
                "",
                f"Longest horizon ({maximum_horizon} months), lambda={selected_coverage}; every row is descriptive.",
                "",
                "| Family | Generator configuration | Comparison | N | Median gap | 5% downside | Worst shortfall | Mean cash contribution | Mean unit contribution |",
                "|---|---|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        selected_groups = [
            group
            for group in stochastic_aggregates["groups"]
            if group["analysis_tier"] == tier
            and group["horizon_months"] == maximum_horizon
            and group["coverage"] == selected_coverage
            and group["cost_scenario"] == "frictionless"
            and group["comparison"]
            in {
                "corrected_guarded_vs_dca",
                "corrected_guarded_vs_neutral_guarded",
            }
        ]
        for group in selected_groups:
            lines.append(
                "| "
                + " | ".join(
                    (
                        group["family"],
                        group["generator_config_id"],
                        group["comparison"],
                        str(group["sample_count"]),
                        _percent(group["median_relative_terminal_wealth_gap"]),
                        _percent(group["downside_quantile_0.05"]),
                        _percent(group["worst_observed_relative_shortfall"]),
                        str(group["mean_cash_contribution"]),
                        str(group["mean_unit_contribution"]),
                    )
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "Controlled stochastic sensitivity is not historical evidence or a proof of stochastic optimality.",
            "Cost-adjusted rows are empirical net-performance results outside the current epsilon-DCA theorem; only frictionless guarded rows carry that theorem scope.",
            "",
        ]
    )
    return "\n".join(lines)


def _remove_tree(path: Path) -> None:
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_file():
            child.unlink()
        else:
            child.rmdir()
    path.rmdir()


def _package_runner_ledgers(runner_directory: Path) -> dict[str, Any]:
    raw_path = runner_directory / "ledgers.jsonl"
    compressed_path = runner_directory / "ledgers.jsonl.gz"
    raw_bytes = raw_path.read_bytes()
    compressed_payload = bytearray(
        gzip.compress(raw_bytes, compresslevel=9, mtime=0)
    )
    compressed_payload[9] = 255
    compressed_bytes = bytes(compressed_payload)
    compressed_path.write_bytes(compressed_bytes)
    raw_path.unlink()
    manifest_path = runner_directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    packaged_artifacts = []
    for artifact in manifest["artifacts"]:
        if artifact["path"] != "ledgers.jsonl":
            packaged_artifacts.append(artifact)
            continue
        packaged_artifacts.append(
            {
                "path": "ledgers.jsonl.gz",
                "sha256": _fingerprint(compressed_bytes),
                "content_encoding": "gzip",
                "uncompressed_bytes": len(raw_bytes),
                "uncompressed_sha256": artifact["sha256"],
            }
        )
    manifest["artifacts"] = packaged_artifacts
    manifest["packaging"] = {
        "rule": "deterministic gzip with compresslevel=9, mtime=0, and OS byte 255",
        "reason": "preserve complete ledgers below repository per-file limits",
    }
    _write_json(manifest_path, manifest)
    return manifest


def _study_run_id(
    config: StudyConfig, study: StochasticStudy, runner_input: VersionedInput
) -> str:
    identity = _canonical_json(
        {
            "engine_version": STUDY_ENGINE_VERSION,
            "generator_sha256": _source_sha256(),
            "runner_sha256": _runner_source_sha256(),
            "protocol_sha256": config.sha256,
            "study_sha256": study.sha256,
            "runner_input_sha256": runner_input.sha256,
            "runtime": {
                "implementation": platform.python_implementation(),
                "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
            },
        }
    )
    return f"smartdca-stochastic-v1-{_fingerprint(identity.encode('utf-8'))}"


def _declared_path_count(document: Mapping[str, Any] | None) -> int | None:
    if document is None:
        return None
    configurations = document.get("family_configurations")
    seeds = document.get("seeds")
    horizons = document.get("horizons_months")
    if not all(isinstance(value, list) for value in (configurations, seeds, horizons)):
        return None
    return len(configurations) * len(seeds) * len(horizons)


def _loosely_loaded_document(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _safe_file_sha256(path: Path) -> str | None:
    try:
        return _fingerprint(path.read_bytes())
    except OSError:
        return None


def _failure_error(error: BaseException, stage: str) -> dict[str, Any]:
    code = (
        error.code
        if isinstance(error, ExperimentValidationError)
        else f"{stage}_failure"
    )
    field = error.field if isinstance(error, ExperimentValidationError) else stage
    return {
        "type": type(error).__name__,
        "code": code,
        "field": field,
        "message": str(error),
    }


def _failure_counts(stage: str, error: BaseException) -> dict[str, int]:
    counts = {
        "configuration": 0,
        "generator": 0,
        "input_validation": 0,
        "numerical": 0,
        "runner": 0,
        "comparison": 0,
    }
    category = stage if stage in counts else "runner"
    counts[category] = 1
    if (
        isinstance(error, ExperimentValidationError)
        and error.code == "numerical_failure"
    ):
        counts["numerical"] = 1
    return counts


def _failure_sample_counts(
    declared_path_count: int | None,
    attempts: tuple[Mapping[str, Any], ...],
    runner: RunBundle | None,
) -> dict[str, int | None]:
    included_episode_ids = (
        {
            row["episode_id"]
            for row in runner.episode_results
            if row["result_status"] == "included"
        }
        if runner is not None
        else set()
    )
    attempted_count = len(attempts)
    return {
        "declared_path_count": declared_path_count,
        "attempted_path_count": attempted_count,
        "generated_path_count": sum(
            row["status"] == "generated" for row in attempts
        ),
        "included_path_count": len(included_episode_ids),
        "excluded_path_count": attempted_count - len(included_episode_ids),
        "ledger_count": len(runner.ledgers) if runner is not None else 0,
        "episode_result_count": (
            len(runner.episode_results) if runner is not None else 0
        ),
    }


def _persist_failure_directory(
    output_root: Path,
    stage: str,
    error: BaseException,
    identities: Mapping[str, Any],
    sample_counts: Mapping[str, Any],
    temporary_directory: Path | None = None,
) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    failure_root = output_root / "failures"
    failure_root.mkdir(exist_ok=True)
    staging = temporary_directory or Path(
        tempfile.mkdtemp(prefix=".stochastic-failure-", dir=failure_root)
    )
    artifacts = [
        {
            "path": path.relative_to(staging).as_posix(),
            "sha256": _fingerprint(path.read_bytes()),
        }
        for path in sorted(path for path in staging.rglob("*") if path.is_file())
        if path.name != "failure.json"
    ]
    receipt_core = {
        "schema_version": "smartdca-stochastic-study-failure/1",
        "status": "failed",
        "stage": stage,
        "error": _failure_error(error, stage),
        "identities": dict(identities),
        "sample_counts": dict(sample_counts),
        "failure_counts": _failure_counts(stage, error),
        "artifacts": artifacts,
    }
    failure_id = (
        "smartdca-stochastic-failure-v1-"
        + _fingerprint(_canonical_json(receipt_core).encode("utf-8"))
    )
    receipt = {"failure_id": failure_id, **receipt_core}
    _write_json(staging / "failure.json", receipt)
    final_directory = failure_root / failure_id
    if final_directory.exists():
        existing_receipt = (final_directory / "failure.json").read_bytes()
        staged_receipt = (staging / "failure.json").read_bytes()
        if existing_receipt != staged_receipt:
            raise RunIdentityCollisionError(
                "failure_identity_collision",
                "output_root",
                f"{failure_id} exists with different receipt bytes",
            )
        _remove_tree(staging)
    else:
        os.replace(staging, final_directory)
    receipt_path = final_directory / "failure.json"
    try:
        setattr(error, "failure_receipt", str(receipt_path))
    except (AttributeError, TypeError):
        pass
    return receipt_path


def run_stochastic_study_from_paths(
    config_path: Path, study_path: Path, output_root: Path
) -> StochasticStudyBundle:
    """Load and run saved inputs while durably retaining validation failures."""
    _require(
        isinstance(output_root, Path),
        "invalid_type",
        "output_root",
        "must be pathlib.Path",
    )
    loose_study = _loosely_loaded_document(study_path)
    identities = {
        "protocol_sha256": _safe_file_sha256(config_path),
        "study_spec_sha256": _safe_file_sha256(study_path),
        "generator_sha256": _source_sha256(),
        "runner_sha256": _runner_source_sha256(),
    }
    try:
        config = load_study_config(config_path)
        study = load_stochastic_study(study_path)
    except ExperimentValidationError as error:
        _persist_failure_directory(
            output_root,
            "configuration",
            error,
            identities,
            _failure_sample_counts(
                _declared_path_count(loose_study), tuple(), None
            ),
        )
        raise
    return run_stochastic_study(config, study, output_root)


def run_stochastic_study(
    config: StudyConfig, study: StochasticStudy, output_root: Path
) -> StochasticStudyBundle:
    """Generate saved seeded paths and execute the full policy grid."""
    _require(isinstance(config, StudyConfig), "invalid_type", "config", "must be StudyConfig")
    _require(isinstance(study, StochasticStudy), "invalid_type", "study", "must be StochasticStudy")
    _require(isinstance(output_root, Path), "invalid_type", "output_root", "must be pathlib.Path")
    output_root.mkdir(parents=True, exist_ok=True)
    document = study.as_mapping()
    config_document = config.as_mapping()
    declared_path_count = _declared_path_count(document)
    identities = {
        "protocol_sha256": config.sha256,
        "study_spec_sha256": study.sha256,
        "generator_sha256": _source_sha256(),
        "runner_sha256": _runner_source_sha256(),
        "runner_input_sha256": None,
        "study_run_id": None,
        "runner_run_id": None,
    }
    try:
        _require(
            document["horizons_months"]
            == config_document["episode_design"]["horizons_months"],
            "protocol_grid_mismatch",
            "study.horizons_months",
            "must equal the preregistered primary horizon grid",
        )
    except ExperimentValidationError as error:
        _persist_failure_directory(
            output_root,
            "configuration",
            error,
            identities,
            _failure_sample_counts(declared_path_count, tuple(), None),
        )
        raise
    start = _iso_date(document["start_date"], "study.start_date")
    deposit = str(_decimal(document["deposit"], "study.deposit"))
    maximum_horizon = max(document["horizons_months"])
    episodes: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    for configuration in document["family_configurations"]:
        for seed in document["seeds"]:
            try:
                generated_path = _generate_path(
                    configuration, seed, maximum_horizon
                )
            except (ArithmeticError, OverflowError, ValueError) as raw_error:
                error = ExperimentValidationError(
                    "numerical_failure",
                    f"configuration.{configuration['config_id']}",
                    str(raw_error),
                )
                for horizon in document["horizons_months"]:
                    attempts.append(
                        {
                            "attempt_id": f"{configuration['config_id']}-s{seed}-h{horizon}",
                            "config_id": configuration["config_id"],
                            "family": configuration["family"],
                            "tier": configuration["tier"],
                            "parameters": configuration["parameters"],
                            "seed": seed,
                            "horizon_months": horizon,
                            "status": "excluded",
                            "exclusion_reason": error.code,
                            "failure_stage": "generator",
                            "validation_field": error.field,
                            "validation_message": str(error),
                            "episode_id": None,
                        }
                    )
                continue
            except ExperimentValidationError as error:
                for horizon in document["horizons_months"]:
                    attempts.append(
                        {
                            "attempt_id": f"{configuration['config_id']}-s{seed}-h{horizon}",
                            "config_id": configuration["config_id"],
                            "family": configuration["family"],
                            "tier": configuration["tier"],
                            "parameters": configuration["parameters"],
                            "seed": seed,
                            "horizon_months": horizon,
                            "status": "excluded",
                            "exclusion_reason": error.code,
                            "failure_stage": "generator",
                            "validation_field": error.field,
                            "validation_message": str(error),
                            "episode_id": None,
                        }
                    )
                continue
            full_path_sha256 = _fingerprint(
                (_canonical_json(generated_path.prices) + "\n").encode("utf-8")
            )
            for horizon in document["horizons_months"]:
                episode_id = f"{configuration['config_id']}-s{seed}-h{horizon}"
                path_prices = generated_path.prices[: horizon + 1]
                path_trace = generated_path.trace[:horizon]
                path_sha256 = _fingerprint(
                    (_canonical_json(path_prices) + "\n").encode("utf-8")
                )
                path_statistics = _path_statistics(path_prices)
                process_diagnostics = _process_diagnostics(
                    configuration["family"], path_trace
                )
                observations = [
                    {
                        "date": _add_months(start, index).isoformat(),
                        "price": path_prices[index],
                        "deposit": deposit,
                    }
                    for index in range(horizon)
                ]
                episode = {
                    "episode_id": episode_id,
                    "family": configuration["family"],
                    "dataset_id": f"stochastic-v1:{configuration['tier']}:{configuration['config_id']}",
                    "horizon_months": horizon,
                    "observations": observations,
                    "evaluation_date": _add_months(start, horizon).isoformat(),
                    "evaluation_price": path_prices[horizon],
                    "generation": {
                        "generator_version": GENERATOR_VERSION,
                        "rng": RNG_CONTRACT,
                        "config_id": configuration["config_id"],
                        "tier": configuration["tier"],
                        "parameters": configuration["parameters"],
                        "seed": seed,
                        "full_path_sha256": full_path_sha256,
                        "path_sha256": path_sha256,
                        "path_statistics": path_statistics,
                        "process_diagnostics": process_diagnostics,
                    },
                }
                episodes.append(episode)
                attempts.append(
                    {
                        "attempt_id": episode_id,
                        "config_id": configuration["config_id"],
                        "family": configuration["family"],
                        "tier": configuration["tier"],
                        "parameters": configuration["parameters"],
                        "seed": seed,
                        "horizon_months": horizon,
                        "status": "generated",
                        "exclusion_reason": None,
                        "failure_stage": None,
                        "episode_id": episode_id,
                        "full_path_sha256": full_path_sha256,
                        "path_sha256": path_sha256,
                        "path_statistics": path_statistics,
                        "process_diagnostics": process_diagnostics,
                    }
                )
    path_attempts = tuple(attempts)
    generated_families = {episode["family"] for episode in episodes}
    try:
        _require(
            set(document["required_families"]) <= generated_families,
            "missing_required_family",
            "study.required_families",
            "every required family must generate at least one path",
        )
    except ExperimentValidationError as error:
        failure_staging = Path(
            tempfile.mkdtemp(prefix=".stochastic-generator-failure-", dir=output_root)
        )
        _write_jsonl(failure_staging / "path-attempts.jsonl", path_attempts)
        _persist_failure_directory(
            output_root,
            "generator",
            error,
            identities,
            _failure_sample_counts(declared_path_count, path_attempts, None),
            failure_staging,
        )
        raise
    runner_input_document = {
        "schema_version": "smartdca-versioned-input/1",
        "input_id": document["input_id"],
        "version": document["input_version"],
        "kind": "stochastic",
        "confirmatory": False,
        "generator_version": document["generator_version"],
        "rng": document["rng"],
        "seeds": document["seeds"],
        "study_spec_sha256": study.sha256,
        "path_attempts": list(path_attempts),
        "episodes": episodes,
    }
    runner_input_payload = (_canonical_json(runner_input_document) + "\n").encode("utf-8")
    try:
        runner_input = VersionedInput.from_json_bytes(runner_input_payload)
    except ExperimentValidationError as error:
        identities["runner_input_sha256"] = _fingerprint(runner_input_payload)
        failure_staging = Path(
            tempfile.mkdtemp(prefix=".stochastic-input-failure-", dir=output_root)
        )
        (failure_staging / "runner-input.json").write_bytes(runner_input_payload)
        _write_jsonl(failure_staging / "path-attempts.jsonl", path_attempts)
        _persist_failure_directory(
            output_root,
            "input_validation",
            error,
            identities,
            _failure_sample_counts(declared_path_count, path_attempts, None),
            failure_staging,
        )
        raise
    study_run_id = _study_run_id(config, study, runner_input)
    identities["runner_input_sha256"] = runner_input.sha256
    identities["study_run_id"] = study_run_id
    final_directory = output_root / study_run_id
    if final_directory.exists():
        error = RunIdentityCollisionError(
            "run_identity_collision", "output_root", f"{study_run_id} already exists"
        )
        _persist_failure_directory(
            output_root,
            "configuration",
            error,
            identities,
            _failure_sample_counts(declared_path_count, path_attempts, None),
        )
        raise error
    temporary_directory = Path(
        tempfile.mkdtemp(prefix=f".{study_run_id}-", dir=output_root)
    )
    runner: RunBundle | None = None
    failure_stage = "runner"
    try:
        (temporary_directory / "runner-input.json").write_bytes(runner_input_payload)
        _write_jsonl(temporary_directory / "path-attempts.jsonl", path_attempts)
        runner_stage = temporary_directory / "runner-stage"
        runner = run_experiment(config, runner_input, runner_stage)
        identities["runner_run_id"] = runner.run_id
        _require(
            runner.manifest["runner_sha256"] == _runner_source_sha256(),
            "runner_source_drift",
            "runner.manifest.runner_sha256",
            "shared runner source changed after study identity derivation",
        )
        runner_directory = temporary_directory / "runner"
        os.replace(runner.output_directory, runner_directory)
        runner_stage.rmdir()
        packaged_runner_manifest = _package_runner_ledgers(runner_directory)
        serialized_results = _read_jsonl(runner_directory / "episode-results.jsonl")
        serialized_runner_aggregates = json.loads(
            (runner_directory / "aggregates.json").read_text(encoding="utf-8")
        )
        failure_stage = "comparison"
        with localcontext() as decimal_context:
            decimal_context.prec = 60
            stochastic_aggregates = _aggregate_stochastic_results(
                config_document,
                document,
                serialized_results,
                path_attempts,
            )
        reconciliation = reconcile_stochastic_aggregates(
            stochastic_aggregates,
            serialized_runner_aggregates,
            serialized_results,
            path_attempts,
        )
        enriched_results = _enrich_results(serialized_results, path_attempts)
        figure_rows = _figure_rows(stochastic_aggregates)
        _write_json(
            temporary_directory / "stochastic-aggregates.json",
            stochastic_aggregates,
        )
        _write_jsonl(
            temporary_directory / "stochastic-results.jsonl",
            enriched_results,
        )
        _write_csv(
            temporary_directory / "stochastic-figure-ready.csv",
            figure_rows,
            list(figure_rows[0]),
        )
        _write_json(
            temporary_directory / "aggregate-reconciliation.json",
            reconciliation,
        )
        (temporary_directory / "report-tables.txt").write_text(
            _render_report_tables(document, stochastic_aggregates, path_attempts),
            encoding="utf-8",
            newline="\n",
        )
        validation = {
            "status": "passed",
            "attempted_path_count": len(path_attempts),
            "generated_path_count": len(episodes),
            "excluded_path_count": len(path_attempts) - len(episodes),
            "required_families": document["required_families"],
            "generated_families": sorted(generated_families),
            "seeds": document["seeds"],
            "horizons_months": document["horizons_months"],
            "failure_counts": {
                "configuration": 0,
                "generator": sum(
                    row["status"] == "excluded"
                    and row["failure_stage"] == "generator"
                    for row in path_attempts
                ),
                "input_validation": 0,
                "numerical": sum(
                    row["status"] == "excluded"
                    and row["exclusion_reason"] == "numerical_failure"
                    for row in path_attempts
                ),
                "runner": 0,
                "comparison": 0,
            },
            "aggregate_reconciliation": reconciliation,
            "shared_runner_validation": runner.validation,
        }
        _write_json(temporary_directory / "study-validation.json", validation)
        artifacts = [
            {
                "path": artifact.relative_to(temporary_directory).as_posix(),
                "sha256": _fingerprint(artifact.read_bytes()),
            }
            for artifact in sorted(
                path for path in temporary_directory.rglob("*") if path.is_file()
            )
        ]
        manifest = {
            "schema_version": "smartdca-stochastic-study-manifest/1",
            "study_run_id": study_run_id,
            "engine_version": STUDY_ENGINE_VERSION,
            "generator_version": GENERATOR_VERSION,
            "generator_sha256": _source_sha256(),
            "runner_sha256": _runner_source_sha256(),
            "protocol_sha256": config.sha256,
            "study_spec_sha256": study.sha256,
            "runner_input_sha256": runner_input.sha256,
            "runner_run_id": runner.run_id,
            "runtime": {
                "implementation": platform.python_implementation(),
                "python": platform.python_version(),
                "protocol_runtime": config_document["runtime"],
            },
            "seeds": document["seeds"],
            "horizons_months": document["horizons_months"],
            "execution_grid": {
                "analysis_tiers": sorted(
                    {value["tier"] for value in document["family_configurations"]}
                ),
                "families": sorted(
                    {value["family"] for value in document["family_configurations"]}
                ),
                "generator_configurations": sorted(
                    value["config_id"]
                    for value in document["family_configurations"]
                ),
                "seeds": document["seeds"],
                "horizons_months": document["horizons_months"],
                "policies": sorted({ledger["policy"] for ledger in runner.ledgers}),
                "comparisons": sorted(
                    {result["comparison"] for result in runner.episode_results}
                ),
                "coverage": config_document["coverage"]["primary"],
                "corrected_mean_configurations": [
                    value["config_id"]
                    for value in config_document["corrected_mean"]["primary"]
                ],
                "cost_scenarios": [
                    value["cost_id"] for value in config_document["cost_scenarios"]
                ],
                "theorem_scopes": sorted(
                    {ledger["theorem_scope"] for ledger in runner.ledgers}
                ),
            },
            "reproduction": {
                "module": "reproducibility.stochastic_study",
                "config": f"experiments/protocols/{config_document['protocol_id']}.json",
                "study": f"experiments/inputs/{document['study_id']}.json",
                "output_root": "<new-empty-output-root>",
                "collision_rule": "The output root must not already contain this study_run_id.",
            },
            "attempted_path_count": len(path_attempts),
            "generated_path_count": len(episodes),
            "excluded_path_count": len(path_attempts) - len(episodes),
            "artifacts": artifacts,
        }
        _write_json(temporary_directory / "manifest.json", manifest)
        os.replace(temporary_directory, final_directory)
    except Exception as error:
        _persist_failure_directory(
            output_root,
            failure_stage,
            error,
            identities,
            _failure_sample_counts(declared_path_count, path_attempts, runner),
            temporary_directory,
        )
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
    return StochasticStudyBundle(
        study_run_id=study_run_id,
        output_directory=final_directory,
        manifest=manifest,
        path_attempts=path_attempts,
        runner=relocated_runner,
    )


def main(argv: list[str] | None = None) -> int:
    """Run one immutable stochastic study from a clean environment."""
    parser = argparse.ArgumentParser(
        description="Execute the seeded stochastic SmartDCA path-family study."
    )
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--study", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    arguments = parser.parse_args(argv)
    try:
        bundle = run_stochastic_study_from_paths(
            arguments.config,
            arguments.study,
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
                    "failure_receipt": getattr(error, "failure_receipt", None),
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
                    "code": f"{type(error).__name__}",
                    "message": str(error),
                    "failure_receipt": getattr(error, "failure_receipt", None),
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
                "manifest": str((bundle.output_directory / "manifest.json").resolve()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
