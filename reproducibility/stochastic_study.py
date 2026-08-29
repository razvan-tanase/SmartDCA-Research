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
SUPPORTED_FAMILIES = frozenset(
    {
        "trend",
        "mean_reversion",
        "stochastic_volatility",
        "regime_switching",
        "jump_diffusion",
    }
)


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


def _validate_parameters(configuration: Mapping[str, Any], field: str) -> None:
    family = configuration["family"]
    parameters = configuration["parameters"]
    _require(
        isinstance(parameters, dict),
        "invalid_type",
        f"{field}.parameters",
        "must be a mapping",
    )
    if family == "trend":
        expected = {"start_price", "annual_drift", "annual_volatility"}
        _require(
            set(parameters) == expected,
            "invalid_parameter_set",
            f"{field}.parameters",
            f"must contain exactly {sorted(expected)}",
        )
        start = _decimal(parameters["start_price"], f"{field}.parameters.start_price")
        drift = _decimal(parameters["annual_drift"], f"{field}.parameters.annual_drift")
        volatility = _decimal(
            parameters["annual_volatility"],
            f"{field}.parameters.annual_volatility",
        )
        _require(start > 0, "invalid_parameter", f"{field}.parameters.start_price", "must be positive")
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
        return
    if family == "mean_reversion":
        expected = {
            "start_price",
            "long_run_price",
            "half_life_months",
            "stationary_log_volatility",
        }
        _require(
            set(parameters) == expected,
            "invalid_parameter_set",
            f"{field}.parameters",
            f"must contain exactly {sorted(expected)}",
        )
        start = _decimal(parameters["start_price"], f"{field}.parameters.start_price")
        long_run = _decimal(
            parameters["long_run_price"], f"{field}.parameters.long_run_price"
        )
        half_life = _decimal(
            parameters["half_life_months"],
            f"{field}.parameters.half_life_months",
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
        return
    if family == "stochastic_volatility":
        expected = {
            "start_price",
            "annual_drift",
            "long_run_annual_volatility",
            "volatility_persistence",
            "log_volatility_of_volatility",
        }
        _require(
            set(parameters) == expected,
            "invalid_parameter_set",
            f"{field}.parameters",
            f"must contain exactly {sorted(expected)}",
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
        _require(start > 0, "invalid_parameter", f"{field}.parameters.start_price", "must be positive")
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
        return
    if family == "regime_switching":
        expected = {
            "start_price",
            "initial_regime",
            "bull_annual_drift",
            "bull_annual_volatility",
            "bull_stay_probability",
            "bear_annual_drift",
            "bear_annual_volatility",
            "bear_stay_probability",
        }
        _require(
            set(parameters) == expected,
            "invalid_parameter_set",
            f"{field}.parameters",
            f"must contain exactly {sorted(expected)}",
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
        return
    if family == "jump_diffusion":
        expected = {
            "start_price",
            "annual_drift",
            "annual_diffusion_volatility",
            "monthly_jump_probability",
            "mean_log_jump",
            "log_jump_volatility",
        }
        _require(
            set(parameters) == expected,
            "invalid_parameter_set",
            f"{field}.parameters",
            f"must contain exactly {sorted(expected)}",
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
        _require(start > 0, "invalid_parameter", f"{field}.parameters.start_price", "must be positive")
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
        return
    raise ExperimentValidationError(
        "unsupported_family", f"{field}.family", f"unsupported family {family!r}"
    )


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
    if configuration["family"] == "trend":
        return _generate_trend(configuration["parameters"], seed, steps)
    if configuration["family"] == "mean_reversion":
        return _generate_mean_reversion(configuration["parameters"], seed, steps)
    if configuration["family"] == "stochastic_volatility":
        return _generate_stochastic_volatility(configuration["parameters"], seed, steps)
    if configuration["family"] == "regime_switching":
        return _generate_regime_switching(configuration["parameters"], seed, steps)
    if configuration["family"] == "jump_diffusion":
        return _generate_jump_diffusion(configuration["parameters"], seed, steps)
    raise ExperimentValidationError(
        "unsupported_family", "configuration.family", "family is not implemented"
    )


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


def _process_diagnostics(
    family: str, trace: tuple[Mapping[str, Any], ...]
) -> dict[str, Any]:
    if family == "stochastic_volatility":
        values = [float(row["annual_volatility"]) for row in trace]
        return {
            "minimum_annual_volatility": _number_text(min(values)),
            "mean_annual_volatility": _number_text(sum(values) / len(values)),
            "maximum_annual_volatility": _number_text(max(values)),
        }
    if family == "regime_switching":
        return {
            "bull_months": sum(row["regime"] == "bull" for row in trace),
            "bear_months": sum(row["regime"] == "bear" for row in trace),
            "regime_switches": sum(
                row["switched_after_month"] is True for row in trace
            ),
        }
    if family == "jump_diffusion":
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
    return {}


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


def _reconcile_runner_aggregates(
    stochastic_aggregates: Mapping[str, Any],
    runner_aggregates: Mapping[str, Any],
) -> dict[str, Any]:
    shared_fields = (
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
    study_lookup = {
        (
            group["family"],
            f"stochastic-v1:{group['analysis_tier']}:{group['generator_config_id']}",
            group["horizon_months"],
            group["coverage"],
            group["corrected_mean_config"],
            group["cost_scenario"],
            group["comparison"],
            group["theorem_scope"],
        ): group
        for group in stochastic_aggregates["groups"]
    }
    mismatches: list[dict[str, Any]] = []
    compared = 0
    for runner_group in runner_aggregates["groups"]:
        key = (
            runner_group["family"],
            runner_group["dataset_id"],
            runner_group["horizon_months"],
            runner_group["coverage"],
            runner_group["corrected_mean_config"],
            runner_group["cost_scenario"],
            runner_group["comparison"],
            runner_group["theorem_scope"],
        )
        study_group = study_lookup[key]
        compared += 1
        for field in shared_fields:
            if study_group[field] != runner_group[field]:
                mismatches.append(
                    {
                        "group": list(key),
                        "field": field,
                        "independent": study_group[field],
                        "runner": runner_group[field],
                    }
                )
    if mismatches:
        raise AssertionError(
            "independent aggregate reconciliation found "
            f"{len(mismatches)} mismatch(es); first={mismatches[0]!r}"
        )
    return {
        "status": "passed",
        "method": "recomputed from serialized episode-results.jsonl and compared field-by-field with serialized runner aggregates",
        "reconciled_group_count": compared,
        "shared_statistic_count_per_group": len(shared_fields),
        "mismatch_count": 0,
    }


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


def run_stochastic_study(
    config: StudyConfig, study: StochasticStudy, output_root: Path
) -> StochasticStudyBundle:
    """Generate saved seeded paths and execute the full policy grid."""
    _require(isinstance(config, StudyConfig), "invalid_type", "config", "must be StudyConfig")
    _require(isinstance(study, StochasticStudy), "invalid_type", "study", "must be StochasticStudy")
    _require(isinstance(output_root, Path), "invalid_type", "output_root", "must be pathlib.Path")
    document = study.as_mapping()
    config_document = config.as_mapping()
    _require(
        document["horizons_months"] == config_document["episode_design"]["horizons_months"],
        "protocol_grid_mismatch",
        "study.horizons_months",
        "must equal the preregistered primary horizon grid",
    )
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
    generated_families = {episode["family"] for episode in episodes}
    _require(
        set(document["required_families"]) <= generated_families,
        "missing_required_family",
        "study.required_families",
        "every required family must generate at least one path",
    )
    path_attempts = tuple(attempts)
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
    runner_input = VersionedInput.from_json_bytes(runner_input_payload)
    study_run_id = _study_run_id(config, study, runner_input)
    output_root.mkdir(parents=True, exist_ok=True)
    final_directory = output_root / study_run_id
    if final_directory.exists():
        raise RunIdentityCollisionError(
            "run_identity_collision", "output_root", f"{study_run_id} already exists"
        )
    temporary_directory = Path(
        tempfile.mkdtemp(prefix=f".{study_run_id}-", dir=output_root)
    )
    try:
        (temporary_directory / "runner-input.json").write_bytes(runner_input_payload)
        runner_stage = temporary_directory / "runner-stage"
        runner = run_experiment(config, runner_input, runner_stage)
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
        _write_jsonl(temporary_directory / "path-attempts.jsonl", path_attempts)
        serialized_results = _read_jsonl(runner_directory / "episode-results.jsonl")
        serialized_runner_aggregates = json.loads(
            (runner_directory / "aggregates.json").read_text(encoding="utf-8")
        )
        with localcontext() as decimal_context:
            decimal_context.prec = 60
            stochastic_aggregates = _aggregate_stochastic_results(
                config_document,
                document,
                serialized_results,
                path_attempts,
            )
        reconciliation = _reconcile_runner_aggregates(
            stochastic_aggregates,
            serialized_runner_aggregates,
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
    except BaseException:
        _remove_tree(temporary_directory)
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
        bundle = run_stochastic_study(
            load_study_config(arguments.config),
            load_stochastic_study(arguments.study),
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
                "manifest": str((bundle.output_directory / "manifest.json").resolve()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
