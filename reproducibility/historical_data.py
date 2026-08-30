"""Historical-source normalization and recurring-investment episode preparation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from collections import Counter
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from reproducibility.empirical import (
    ExperimentValidationError,
    RunBundle,
    StudyConfig,
    VersionedInput,
    run_experiment,
)


PARSER_VERSION = "smartdca-historical-csv/1"
HISTORICAL_ENGINE_VERSION = "smartdca-historical-preparation/1"
ZERO = Decimal("0")
MAPPING_TOLERANCE_DAYS = {
    "spy-adjusted-daily": 7,
    "btc-usd-daily": 1,
}


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


def _decimal_text(value: Decimal) -> str:
    if value == ZERO:
        return "0"
    text = format(value.normalize(), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def _utc_datetime(value: Any, field: str) -> str:
    _require(isinstance(value, str), "invalid_datetime", field, "must be ISO 8601 text")
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
    return value


@dataclass(frozen=True)
class HistoricalSourceSet:
    """Validated immutable description of exact historical source responses."""

    canonical_document: str
    sha256: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "HistoricalSourceSet":
        try:
            document = json.loads(_canonical_json(value))
        except (TypeError, ValueError) as error:
            raise ExperimentValidationError(
                "invalid_json_value", "source_set", "must contain finite JSON values"
            ) from error
        _require(
            document.get("schema_version") == "smartdca-historical-source-set/1",
            "unsupported_schema",
            "source_set.schema_version",
            "must equal smartdca-historical-source-set/1",
        )
        for field in (
            "source_set_id",
            "version",
            "mode",
            "confirmatory",
            "purpose",
            "sources",
            "episode_scope",
        ):
            _require(field in document, "missing_field", f"source_set.{field}", "is required")
        for field in ("source_set_id", "version", "purpose"):
            _require(
                isinstance(document[field], str) and bool(document[field]),
                "invalid_identifier",
                f"source_set.{field}",
                "must be nonempty text",
            )
        _require(
            document["mode"] in {"validation", "confirmatory"},
            "invalid_mode",
            "source_set.mode",
            "must be validation or confirmatory",
        )
        _require(
            isinstance(document["confirmatory"], bool),
            "invalid_type",
            "source_set.confirmatory",
            "must be boolean",
        )
        _require(
            (document["mode"] == "confirmatory") is document["confirmatory"],
            "inconsistent_analysis_tier",
            "source_set.confirmatory",
            "must be true exactly when mode is confirmatory",
        )
        if document["confirmatory"]:
            protocol_sha256 = document.get("protocol_sha256")
            acquisition = document.get("acquisition")
            _require(
                isinstance(protocol_sha256, str)
                and len(protocol_sha256) == 64
                and all(
                    character in "0123456789abcdef"
                    for character in protocol_sha256
                ),
                "unverified_confirmatory_provenance",
                "source_set.protocol_sha256",
                "confirmatory sources must bind the exact protocol bytes",
            )
            _require(
                isinstance(acquisition, dict)
                and acquisition
                == {
                    "adapter": "alpha-vantage-http",
                    "provider": "Alpha Vantage",
                    "one_response_per_dataset": True,
                    "credential_recorded": False,
                },
                "unverified_confirmatory_provenance",
                "source_set.acquisition",
                "confirmatory sources must carry the live acquisition receipt",
            )
        _require(
            isinstance(document["sources"], list) and bool(document["sources"]),
            "empty_sources",
            "source_set.sources",
            "must be a nonempty list",
        )
        for index, source in enumerate(document["sources"]):
            prefix = f"source_set.sources[{index}]"
            _require(isinstance(source, dict), "invalid_type", prefix, "must be a mapping")
            for field in (
                "dataset_id",
                "adapter",
                "path",
                "retrieved_at_utc",
                "http_status",
                "content_type",
                "expected_sha256",
                "redistribution_decision",
            ):
                _require(field in source, "missing_field", f"{prefix}.{field}", "is required")
            for field in (
                "dataset_id",
                "adapter",
                "path",
                "content_type",
                "redistribution_decision",
            ):
                _require(
                    isinstance(source[field], str) and bool(source[field]),
                    "invalid_source",
                    f"{prefix}.{field}",
                    "must be nonempty text",
                )
            _utc_datetime(source["retrieved_at_utc"], f"{prefix}.retrieved_at_utc")
            _require(
                isinstance(source["expected_sha256"], str)
                and len(source["expected_sha256"]) == 64
                and all(character in "0123456789abcdef" for character in source["expected_sha256"]),
                "invalid_fingerprint",
                f"{prefix}.expected_sha256",
                "must be a lowercase SHA-256 digest",
            )
            _require(
                isinstance(source["http_status"], int)
                and not isinstance(source["http_status"], bool),
                "invalid_source",
                f"{prefix}.http_status",
                "must be an integer",
            )
            if document["confirmatory"]:
                _require(
                    source["adapter"] == "alpha-vantage-http"
                    and isinstance(source.get("request_receipt"), dict),
                    "unverified_confirmatory_provenance",
                    prefix,
                    "confirmatory sources must come from the live provider adapter",
                )
                _require(
                    source["path"]
                    == (
                        f"{source['dataset_id']}-"
                        f"{source['expected_sha256']}.csv"
                    ),
                    "unverified_confirmatory_provenance",
                    f"{prefix}.path",
                    "confirmatory response path must be content-addressed",
                )
        if document["confirmatory"]:
            source_hashes = {
                source["dataset_id"]: source["expected_sha256"]
                for source in document["sources"]
            }
            expected_source_set_id = (
                "alpha-vantage-historical-"
                f"{_fingerprint(_canonical_json(source_hashes).encode('utf-8'))}"
            )
            _require(
                len(source_hashes) == len(document["sources"])
                and document["source_set_id"] == expected_source_set_id,
                "unverified_confirmatory_provenance",
                "source_set.source_set_id",
                "confirmatory source-set identity must derive from response hashes",
            )
        canonical = _canonical_json(document)
        return cls(canonical, _fingerprint(canonical.encode("utf-8")))

    @classmethod
    def from_json_bytes(cls, payload: bytes) -> "HistoricalSourceSet":
        document = _decode_json_document(payload, "source_set")
        validated = cls.from_mapping(document)
        return cls(validated.canonical_document, _fingerprint(payload))

    def as_mapping(self) -> dict[str, Any]:
        return json.loads(self.canonical_document)


def load_historical_source_set(path: Path) -> HistoricalSourceSet:
    """Load a source-set receipt and fingerprint its exact serialized bytes."""

    _require(
        isinstance(path, Path),
        "invalid_type",
        "source_set_path",
        "must be pathlib.Path",
    )
    try:
        payload = path.read_bytes()
    except OSError as error:
        raise ExperimentValidationError(
            "unreadable_source_set", "source_set_path", str(error)
        ) from error
    return HistoricalSourceSet.from_json_bytes(payload)


@dataclass(frozen=True)
class ProviderResponse:
    """Exact response returned by a historical-data provider adapter."""

    body: bytes
    http_status: int
    content_type: str


class HistoricalProvider(Protocol):
    """Port implemented by live and fixture historical-provider adapters."""

    def retrieve(self, dataset: Mapping[str, Any]) -> ProviderResponse:
        """Retrieve one exact response for the declared dataset."""


class AlphaVantageProvider:
    """Live adapter for the two Alpha Vantage requests frozen in the protocol."""

    def __init__(
        self,
        api_key: str,
        *,
        opener: Callable[..., Any] = urlopen,
        timeout_seconds: int = 60,
    ) -> None:
        _require(
            isinstance(api_key, str) and bool(api_key.strip()),
            "missing_credential",
            "ALPHAVANTAGE_API_KEY",
            "must be set to a nonempty value",
        )
        self._api_key = api_key
        self._opener = opener
        self._timeout_seconds = timeout_seconds

    def retrieve(self, dataset: Mapping[str, Any]) -> ProviderResponse:
        parameters = dict(dataset["request_parameters"])
        _require(
            "apikey" not in {str(key).lower() for key in parameters},
            "credential_in_protocol",
            f"config.historical_datasets.{dataset['dataset_id']}.request_parameters",
            "must omit credentials",
        )
        query = urlencode(
            {
                "function": dataset["endpoint"],
                **parameters,
                "apikey": self._api_key,
            }
        )
        request = Request(
            f"https://www.alphavantage.co/query?{query}",
            headers={"User-Agent": "SmartDCA-Research/1"},
        )
        try:
            with self._opener(request, timeout=self._timeout_seconds) as response:
                body = response.read()
                status = int(response.status)
                content_type = str(
                    response.headers.get("Content-Type", "application/octet-stream")
                ).split(";", 1)[0]
        except HTTPError as error:
            body = error.read()
            status = error.code
            content_type = str(
                error.headers.get("Content-Type", "application/octet-stream")
            ).split(";", 1)[0]
        except (OSError, URLError) as error:
            raise ExperimentValidationError(
                "provider_request_failed",
                f"provider.{dataset['dataset_id']}",
                "Alpha Vantage request failed before a response was received",
            ) from error
        return ProviderResponse(body, status, content_type)


@dataclass(frozen=True)
class PreparedHistoricalInput:
    """Auditable source receipts and normalized rows at the public seam."""

    status: str
    source_receipts: tuple[Mapping[str, Any], ...]
    normalized_datasets: Mapping[str, tuple[Mapping[str, Any], ...]]
    episode_attempts: tuple[Mapping[str, Any], ...]
    versioned_input: VersionedInput | None
    reconciliation: Mapping[str, Any]


@dataclass(frozen=True)
class HistoricalRunBundle:
    """Complete non-confirmatory historical infrastructure validation bundle."""

    run_id: str
    output_directory: Path
    manifest: Mapping[str, Any]
    source_receipts: tuple[Mapping[str, Any], ...]
    episode_attempts: tuple[Mapping[str, Any], ...]
    reconciliation: Mapping[str, Any]
    validation: Mapping[str, Any]
    runner: RunBundle


@dataclass(frozen=True)
class HistoricalPreparationBundle:
    """Full-grid input handoff produced without executing any policy."""

    run_id: str
    output_directory: Path
    manifest: Mapping[str, Any]
    prepared: PreparedHistoricalInput
    validation: Mapping[str, Any]


def acquire_historical_sources(
    config: StudyConfig,
    source_root: Path,
    provider: HistoricalProvider,
    retrieved_at_utc: str,
) -> HistoricalSourceSet:
    """Persist one exact provider response per preregistered dataset and its receipt."""

    _require(isinstance(config, StudyConfig), "invalid_type", "config", "must be StudyConfig")
    _require(isinstance(source_root, Path), "invalid_type", "source_root", "must be pathlib.Path")
    _utc_datetime(retrieved_at_utc, "retrieved_at_utc")
    source_root.mkdir(parents=True, exist_ok=True)
    receipt_path = source_root / "historical-source-set.json"
    _require(
        not receipt_path.exists(),
        "source_set_identity_collision",
        "source_root",
        "historical-source-set.json already exists",
    )
    sources: list[dict[str, Any]] = []
    for dataset in config.as_mapping()["historical_datasets"]:
        response = provider.retrieve(dataset)
        _require(
            isinstance(response, ProviderResponse),
            "invalid_provider_response",
            f"provider.{dataset['dataset_id']}",
            "must return ProviderResponse",
        )
        _require(
            isinstance(response.body, bytes),
            "invalid_provider_response",
            f"provider.{dataset['dataset_id']}.body",
            "must be exact bytes",
        )
        _require(
            isinstance(response.http_status, int)
            and not isinstance(response.http_status, bool),
            "invalid_provider_response",
            f"provider.{dataset['dataset_id']}.http_status",
            "must be an integer",
        )
        _require(
            isinstance(response.content_type, str) and bool(response.content_type),
            "invalid_provider_response",
            f"provider.{dataset['dataset_id']}.content_type",
            "must be nonempty text",
        )
        sha256 = _fingerprint(response.body)
        filename = f"{dataset['dataset_id']}-{sha256}.csv"
        raw_path = source_root / filename
        _require(
            not raw_path.exists(),
            "source_identity_collision",
            f"source_root.{filename}",
            "exact-response path already exists",
        )
        temporary_path = source_root / f".{filename}.tmp"
        _require(
            not temporary_path.exists(),
            "source_identity_collision",
            f"source_root.{temporary_path.name}",
            "temporary response path already exists",
        )
        try:
            temporary_path.write_bytes(response.body)
            os.replace(temporary_path, raw_path)
        except BaseException:
            if temporary_path.exists():
                temporary_path.unlink()
            raise
        sources.append(
            {
                "dataset_id": dataset["dataset_id"],
                "adapter": "alpha-vantage-http",
                "path": filename,
                "retrieved_at_utc": retrieved_at_utc,
                "http_status": response.http_status,
                "content_type": response.content_type,
                "expected_sha256": sha256,
                "redistribution_decision": (
                    "provider-bytes-and-normalized-observations-access-controlled-"
                    "outside-git; sanitized-receipts-only-without-written-permission"
                ),
                "request_receipt": {
                    "provider": dataset["provider"],
                    "endpoint": dataset["endpoint"],
                    "request_parameters_without_credentials": dataset[
                        "request_parameters"
                    ],
                },
            }
        )
    identity_payload = _canonical_json(
        {row["dataset_id"]: row["expected_sha256"] for row in sources}
    ).encode("utf-8")
    source_set = HistoricalSourceSet.from_mapping(
        {
            "schema_version": "smartdca-historical-source-set/1",
            "source_set_id": f"alpha-vantage-historical-{_fingerprint(identity_payload)}",
            "version": "1",
            "mode": "confirmatory",
            "confirmatory": True,
            "protocol_sha256": config.sha256,
            "acquisition": {
                "adapter": "alpha-vantage-http",
                "provider": "Alpha Vantage",
                "one_response_per_dataset": True,
                "credential_recorded": False,
            },
            "purpose": (
                "Exact preregistered provider responses retained for point-in-time "
                "historical episode construction; no policy outcome was computed."
            ),
            "sources": sources,
            "episode_scope": {"rule": "full-preregistered-grid"},
        }
    )
    receipt_path.write_text(
        source_set.canonical_document + "\n", encoding="utf-8", newline="\n"
    )
    return load_historical_source_set(receipt_path)


def _normalized_rows(
    dataset: Mapping[str, Any], payload: bytes, field: str
) -> tuple[tuple[dict[str, Any], ...], list[str], str]:
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ExperimentValidationError(
            "invalid_encoding", field, "CSV response must be UTF-8"
        ) from error
    stripped = text.lstrip()
    if stripped.startswith("{"):
        try:
            envelope = json.loads(stripped)
        except json.JSONDecodeError:
            envelope = None
        if isinstance(envelope, dict) and {
            "Error Message",
            "Information",
            "Note",
        } & set(envelope):
            raise ExperimentValidationError(
                "provider_error_payload",
                field,
                "provider returned an error envelope instead of the declared CSV",
            )
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""))
        headers = reader.fieldnames
        rows = list(reader)
    except csv.Error as error:
        raise ExperimentValidationError("malformed_csv", field, str(error)) from error
    _require(headers is not None, "malformed_csv", field, "must have a header row")
    _require(len(headers) == len(set(headers)), "malformed_csv", field, "headers must be unique")
    if dataset["dataset_id"] == "spy-adjusted-daily":
        selected_column = "adjusted_close"
        required_columns = (
            "timestamp",
            "adjusted_close",
            "dividend_amount",
            "split_coefficient",
        )
    else:
        selected_column = "close"
        required_columns = ("timestamp", "close")
    for required in required_columns:
        _require(
            required in headers,
            "series_semantics_mismatch",
            field,
            f"missing required column {required}",
        )
    normalized: list[dict[str, Any]] = []
    seen_dates: set[date] = set()
    for index, row in enumerate(rows):
        row_field = f"{field}.rows[{index}]"
        try:
            observed = date.fromisoformat(row["timestamp"])
        except (TypeError, ValueError) as error:
            raise ExperimentValidationError(
                "malformed_observation", f"{row_field}.timestamp", "must be YYYY-MM-DD"
            ) from error
        _require(
            observed.isoformat() == row["timestamp"],
            "malformed_observation",
            f"{row_field}.timestamp",
            "must use YYYY-MM-DD",
        )
        _require(
            observed not in seen_dates,
            "duplicate_observation",
            f"{row_field}.timestamp",
            "observation dates must be unique",
        )
        seen_dates.add(observed)
        try:
            price = Decimal(row[selected_column])
        except Exception as error:
            raise ExperimentValidationError(
                "malformed_observation",
                f"{row_field}.{selected_column}",
                "must be a finite decimal",
            ) from error
        _require(
            price.is_finite() and price > ZERO,
            "observation_not_strictly_positive",
            f"{row_field}.{selected_column}",
            "must be finite and positive",
        )
        normalized.append(
            {
                "observation_date": observed.isoformat(),
                "price": _decimal_text(price),
                "normalization_timezone": dataset["timezone"],
                "source_row": index + 2,
            }
        )
    _require(normalized, "empty_source", field, "must contain at least one observation")
    normalized.sort(key=lambda row: row["observation_date"])
    return tuple(normalized), headers, selected_column


def _iso_date(value: Any, field: str) -> date:
    _require(isinstance(value, str), "invalid_date", field, "must be an ISO date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ExperimentValidationError(
            "invalid_date", field, "must be a real YYYY-MM-DD calendar date"
        ) from error
    _require(parsed.isoformat() == value, "invalid_date", field, "must use YYYY-MM-DD")
    return parsed


def _add_months(value: date, months: int) -> date:
    month_index = value.year * 12 + value.month - 1 + months
    return date(month_index // 12, month_index % 12 + 1, value.day)


def _mapped_purchase(
    rows: tuple[Mapping[str, Any], ...], nominal_date: date, tolerance_days: int
) -> Mapping[str, Any] | None:
    for row in rows:
        observed = date.fromisoformat(str(row["observation_date"]))
        if observed < nominal_date:
            continue
        if (observed - nominal_date).days <= tolerance_days:
            return row
        return None
    return None


def _mapped_evaluation(
    rows: tuple[Mapping[str, Any], ...], horizon_date: date, tolerance_days: int
) -> Mapping[str, Any] | None:
    for row in reversed(rows):
        observed = date.fromisoformat(str(row["observation_date"]))
        if observed > horizon_date:
            continue
        if (horizon_date - observed).days <= tolerance_days:
            return row
        return None
    return None


def _observation_neighbors(
    rows: tuple[Mapping[str, Any], ...], target: date
) -> tuple[str | None, str | None]:
    previous: str | None = None
    following: str | None = None
    for row in rows:
        observed_text = str(row["observation_date"])
        observed = date.fromisoformat(observed_text)
        if observed < target:
            previous = observed_text
        elif observed >= target:
            following = observed_text
            break
    return previous, following


def _attempt_episode(
    dataset_id: str,
    rows: tuple[Mapping[str, Any], ...],
    nominal_start: date,
    horizon_months: int,
    deposit_amount: str,
) -> dict[str, Any]:
    tolerance_days = MAPPING_TOLERANCE_DAYS[dataset_id]
    horizon_date = _add_months(nominal_start, horizon_months)
    episode_id = (
        f"{dataset_id}-{nominal_start.isoformat()}-{horizon_months}m"
    )
    attempt: dict[str, Any] = {
        "episode_id": episode_id,
        "dataset_id": dataset_id,
        "nominal_start": nominal_start.isoformat(),
        "horizon_months": horizon_months,
        "horizon_date": horizon_date.isoformat(),
        "deposit_schedule": [],
        "evaluation_date": None,
        "evaluation_price": None,
        "evaluation_source_row": None,
        "status": "excluded",
        "exclusion_reason": None,
        "exclusion_details": None,
    }
    mapped_dates: set[str] = set()
    purchase_exclusion_reason: str | None = None
    purchase_exclusion_details: Mapping[str, Any] | None = None
    for offset in range(horizon_months):
        nominal_date = _add_months(nominal_start, offset)
        mapped = _mapped_purchase(rows, nominal_date, tolerance_days)
        if mapped is None:
            previous, following = _observation_neighbors(rows, nominal_date)
            attempt["deposit_schedule"].append(
                {
                    "nominal_date": nominal_date.isoformat(),
                    "purchase_date": None,
                    "mapping_lag_days": None,
                    "source_row": None,
                    "price": None,
                    "deposit": deposit_amount,
                }
            )
            if purchase_exclusion_reason is None:
                purchase_exclusion_reason = "unavailable_mapped_purchase_date"
                purchase_exclusion_details = {
                    "mapping": "first-observation-on-or-after",
                    "nominal_date": nominal_date.isoformat(),
                    "tolerance_days": tolerance_days,
                    "previous_observation_date": previous,
                    "next_observation_date": following,
                }
            continue
        purchase_date = str(mapped["observation_date"])
        if purchase_date in mapped_dates:
            if purchase_exclusion_reason is None:
                purchase_exclusion_reason = "duplicate_mapped_purchase_date"
                purchase_exclusion_details = {
                    "nominal_date": nominal_date.isoformat(),
                    "duplicate_purchase_date": purchase_date,
                }
        mapped_dates.add(purchase_date)
        attempt["deposit_schedule"].append(
            {
                "nominal_date": nominal_date.isoformat(),
                "purchase_date": purchase_date,
                "mapping_lag_days": (
                    date.fromisoformat(purchase_date) - nominal_date
                ).days,
                "source_row": mapped["source_row"],
                "price": mapped["price"],
                "deposit": deposit_amount,
            }
        )

    evaluation = _mapped_evaluation(rows, horizon_date, tolerance_days)
    if evaluation is not None:
        attempt.update(
            {
                "evaluation_date": evaluation["observation_date"],
                "evaluation_price": evaluation["price"],
                "evaluation_source_row": evaluation["source_row"],
            }
        )
    if purchase_exclusion_reason is not None:
        attempt["exclusion_reason"] = purchase_exclusion_reason
        attempt["exclusion_details"] = purchase_exclusion_details
        return attempt
    if evaluation is None:
        previous, following = _observation_neighbors(rows, horizon_date)
        attempt["exclusion_reason"] = "unavailable_mapped_evaluation_date"
        attempt["exclusion_details"] = {
            "mapping": "last-observation-on-or-before",
            "horizon_date": horizon_date.isoformat(),
            "tolerance_days": tolerance_days,
            "previous_observation_date": previous,
            "next_observation_date": following,
        }
        return attempt
    attempt["status"] = "included"
    return attempt


def _failed_dataset_episode(
    dataset_id: str,
    nominal_start: date,
    horizon_months: int,
    deposit_amount: str,
    failure: Mapping[str, Any],
) -> dict[str, Any]:
    horizon_date = _add_months(nominal_start, horizon_months)
    return {
        "episode_id": (
            f"{dataset_id}-{nominal_start.isoformat()}-{horizon_months}m"
        ),
        "dataset_id": dataset_id,
        "nominal_start": nominal_start.isoformat(),
        "horizon_months": horizon_months,
        "horizon_date": horizon_date.isoformat(),
        "deposit_schedule": [
            {
                "nominal_date": _add_months(nominal_start, offset).isoformat(),
                "purchase_date": None,
                "mapping_lag_days": None,
                "source_row": None,
                "price": None,
                "deposit": deposit_amount,
            }
            for offset in range(horizon_months)
        ],
        "evaluation_date": None,
        "evaluation_price": None,
        "evaluation_source_row": None,
        "status": "excluded",
        "exclusion_reason": failure["code"],
        "exclusion_details": {"dataset_failure": dict(failure)},
    }


def _episode_for_runner(
    attempt: Mapping[str, Any], mode: str, source_identity: str
) -> dict[str, Any]:
    return {
        "episode_id": attempt["episode_id"],
        "family": (
            "non-confirmatory-historical-infrastructure-validation"
            if mode == "validation"
            else "historical-recurring-investment"
        ),
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
            "dataset_source_identity": source_identity,
            "nominal_start": attempt["nominal_start"],
            "horizon_date": attempt["horizon_date"],
            "deposit_schedule": attempt["deposit_schedule"],
            "evaluation_source_row": attempt["evaluation_source_row"],
        },
    }


def _build_episodes(
    config_data: Mapping[str, Any],
    source_data: Mapping[str, Any],
    normalized_datasets: Mapping[str, tuple[Mapping[str, Any], ...]],
    source_receipts: tuple[Mapping[str, Any], ...],
    dataset_failures: Mapping[str, Mapping[str, Any]],
) -> tuple[
    tuple[Mapping[str, Any], ...],
    VersionedInput | None,
    Mapping[str, Any],
]:
    scope = source_data["episode_scope"]
    mode = source_data["mode"]
    horizons = config_data["episode_design"]["horizons_months"]
    if mode == "validation":
        start_min = _iso_date(
            scope["nominal_start_min"],
            "source_set.episode_scope.nominal_start_min",
        )
        start_max = _iso_date(
            scope["nominal_start_max"],
            "source_set.episode_scope.nominal_start_max",
        )
        _require(
            start_min.day == 1 and start_max.day == 1 and start_min <= start_max,
            "invalid_episode_scope",
            "source_set.episode_scope",
            "start bounds must be ordered first-of-month dates",
        )
        horizons = scope["horizons_months"]
        _require(
            isinstance(horizons, list)
            and bool(horizons)
            and all(
                isinstance(value, int) and not isinstance(value, bool) and value > 0
                for value in horizons
            ),
            "invalid_horizon",
            "source_set.episode_scope.horizons_months",
            "must be a nonempty list of positive integers",
        )
        declared_horizons = set(config_data["episode_design"]["horizons_months"])
        _require(
            set(horizons) <= declared_horizons,
            "undeclared_horizon",
            "source_set.episode_scope.horizons_months",
            "validation horizons must be preregistered primary horizons",
        )
    else:
        _require(
            scope == {"rule": "full-preregistered-grid"},
            "invalid_episode_scope",
            "source_set.episode_scope",
            "confirmatory preparation must use the full preregistered grid",
        )
    stride = config_data["episode_design"]["rolling_stride_months"]
    deposit_amount = str(config_data["episode_design"]["deposit_amount"])
    dataset_config = {
        row["dataset_id"]: row for row in config_data["historical_datasets"]
    }
    attempts: list[Mapping[str, Any]] = []
    for dataset_id in sorted(dataset_config):
        for horizon in horizons:
            if mode == "validation":
                nominal_start = start_min
                final_start = start_max
            else:
                eligible_start = _iso_date(
                    dataset_config[dataset_id]["eligible_start"],
                    f"config.historical_datasets.{dataset_id}.eligible_start",
                )
                nominal_start = date(eligible_start.year, eligible_start.month, 1)
                if nominal_start < eligible_start:
                    nominal_start = _add_months(nominal_start, 1)
                final_start = _iso_date(
                    dataset_config[dataset_id]["data_cutoff"],
                    f"config.historical_datasets.{dataset_id}.data_cutoff",
                )
            while nominal_start <= final_start and (
                mode == "validation"
                or _add_months(nominal_start, horizon) <= final_start
            ):
                if dataset_id in dataset_failures:
                    attempts.append(
                        _failed_dataset_episode(
                            dataset_id,
                            nominal_start,
                            horizon,
                            deposit_amount,
                            dataset_failures[dataset_id],
                        )
                    )
                else:
                    attempts.append(
                        _attempt_episode(
                            dataset_id,
                            normalized_datasets[dataset_id],
                            nominal_start,
                            horizon,
                            deposit_amount,
                        )
                    )
                nominal_start = _add_months(nominal_start, stride)

    selected: list[Mapping[str, Any]] = []
    input_ready = not dataset_failures
    if mode == "validation":
        attempts_by_key = {
            (row["dataset_id"], row["nominal_start"]): row for row in attempts
        }
        validation_starts = scope["validation_episode_starts"]
        _require(
            isinstance(validation_starts, dict)
            and set(validation_starts) == set(dataset_config),
            "incomplete_validation_selection",
            "source_set.episode_scope.validation_episode_starts",
            "must select one start for each dataset",
        )
        for dataset_id in sorted(validation_starts):
            key = (dataset_id, validation_starts[dataset_id])
            _require(
                key in attempts_by_key,
                "invalid_validation_selection",
                f"source_set.episode_scope.validation_episode_starts.{dataset_id}",
                "must name an attempted episode start",
            )
            attempt = attempts_by_key[key]
            if attempt["status"] == "included":
                selected.append(attempt)
            else:
                input_ready = False
    else:
        selected.extend(row for row in attempts if row["status"] == "included")
        input_ready = input_ready and bool(selected)

    receipt_by_dataset = {row["dataset_id"]: row for row in source_receipts}
    runner_source_receipts = [
        {
            "dataset_id": row["dataset_id"],
            "source_identity": row["source_identity"],
            "sha256": row["sha256"],
            "date_min": row["date_min"],
            "date_max": row["date_max"],
        }
        for row in source_receipts
        if row["status"] == "accepted"
    ]
    versioned_input = (
        VersionedInput.from_mapping(
            {
                "schema_version": "smartdca-versioned-input/1",
                "input_id": f"{source_data['source_set_id']}-runner-input",
                "version": source_data["version"],
                "kind": "historical",
                "confirmatory": source_data["confirmatory"],
                "purpose": source_data["purpose"],
                "source_receipts": runner_source_receipts,
                "episodes": [
                    _episode_for_runner(
                        attempt,
                        source_data["mode"],
                        str(
                            receipt_by_dataset[attempt["dataset_id"]][
                                "source_identity"
                            ]
                        ),
                    )
                    for attempt in selected
                ],
            }
        )
        if input_ready
        else None
    )
    reasons = Counter(
        str(row["exclusion_reason"])
        for row in attempts
        if row["status"] == "excluded"
    )
    reconciliation = {
        "dataset_count": len(dataset_config),
        "accepted_dataset_count": len(normalized_datasets),
        "failed_dataset_count": len(dataset_failures),
        "dataset_failures": dict(sorted(dataset_failures.items())),
        "observation_count": sum(len(rows) for rows in normalized_datasets.values()),
        "attempted_episode_count": len(attempts),
        "included_episode_count": sum(row["status"] == "included" for row in attempts),
        "excluded_episode_count": sum(row["status"] == "excluded" for row in attempts),
        "exclusion_reasons": dict(sorted(reasons.items())),
        "validation_episode_count": len(selected),
        "input_status": "accepted" if versioned_input is not None else "rejected",
    }
    return tuple(attempts), versioned_input, reconciliation


def _source_receipt_preamble(
    dataset: Mapping[str, Any], source: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "dataset_id": dataset["dataset_id"],
        "provider": dataset["provider"],
        "endpoint": dataset["endpoint"],
        "request_parameters_without_credentials": dataset["request_parameters"],
        "retrieved_at_utc": source["retrieved_at_utc"],
        "http_status": source["http_status"],
        "content_type": source["content_type"],
        "expected_sha256": source["expected_sha256"],
        "parser_version": PARSER_VERSION,
        "series": dataset["series"],
        "documentation_url": dataset["documentation_url"],
        "currency": dataset["currency"],
        "timezone": dataset["timezone"],
        "timezone_semantics": {
            "provider_timezone_metadata": "not-present-in-daily-csv",
            "normalization_timezone": dataset["timezone"],
            "normalized_observation": "calendar-date-label-only",
            "intraday_timestamp_invented": False,
        },
        "adjustment_semantics": dataset["adjustment_semantics"],
        "declared_semantics": {
            "asset": dataset["asset_semantics"],
            "currency": dataset["currency"],
            "price_field": dataset["price_field"],
            "timezone": dataset["timezone"],
            "adjustment": dataset["adjustment_semantics"],
            "eligible_start": dataset["eligible_start"],
            "data_cutoff": dataset["data_cutoff"],
        },
        "retrieval_rule": dataset["retrieval_rule"],
        "fingerprint_rule": dataset["fingerprint_rule"],
        "protocol_redistribution_rule": dataset["redistribution"],
        "redistribution_decision": source["redistribution_decision"],
        "adapter": source["adapter"],
    }


def prepare_historical_input(
    config: StudyConfig,
    source_set: HistoricalSourceSet,
    source_root: Path,
) -> PreparedHistoricalInput:
    """Validate, fingerprint, and normalize the declared exact CSV responses."""

    _require(isinstance(config, StudyConfig), "invalid_type", "config", "must be StudyConfig")
    _require(
        isinstance(source_set, HistoricalSourceSet),
        "invalid_type",
        "source_set",
        "must be HistoricalSourceSet",
    )
    _require(isinstance(source_root, Path), "invalid_type", "source_root", "must be pathlib.Path")
    config_data = config.as_mapping()
    source_data = source_set.as_mapping()
    if source_data["confirmatory"]:
        _require(
            source_data["protocol_sha256"] == config.sha256,
            "protocol_fingerprint_mismatch",
            "source_set.protocol_sha256",
            "confirmatory source set was acquired for different protocol bytes",
        )
    datasets = {row["dataset_id"]: row for row in config_data["historical_datasets"]}
    sources = {row["dataset_id"]: row for row in source_data["sources"]}
    _require(
        len(sources) == len(source_data["sources"]) and set(sources) == set(datasets),
        "incomplete_dataset_selection",
        "source_set.sources",
        "must provide each preregistered dataset exactly once",
    )

    receipts: list[dict[str, Any]] = []
    normalized_datasets: dict[str, tuple[Mapping[str, Any], ...]] = {}
    dataset_failures: dict[str, Mapping[str, Any]] = {}
    for dataset_id in sorted(datasets):
        dataset = datasets[dataset_id]
        source = sources[dataset_id]
        if source_data["confirmatory"]:
            _require(
                source["request_receipt"]
                == {
                    "provider": dataset["provider"],
                    "endpoint": dataset["endpoint"],
                    "request_parameters_without_credentials": dataset[
                        "request_parameters"
                    ],
                },
                "series_semantics_mismatch",
                f"source_set.sources.{dataset_id}.request_receipt",
                "must match the exact preregistered provider request",
            )
        receipt = _source_receipt_preamble(dataset, source)
        try:
            source_path = Path(source["path"])
            _require(
                not source_path.is_absolute() and ".." not in source_path.parts,
                "invalid_source_path",
                f"source_set.sources.{dataset_id}.path",
                "must be a relative path below source_root",
            )
            try:
                payload = (source_root / source_path).read_bytes()
            except OSError as error:
                raise ExperimentValidationError(
                    "unreadable_source",
                    f"source_set.sources.{dataset_id}.path",
                    "could not read the declared source path",
                ) from error
            actual_sha256 = _fingerprint(payload)
            receipt.update(
                {
                    "byte_length": len(payload),
                    "sha256": actual_sha256,
                    "source_identity": f"{dataset_id}-{actual_sha256}",
                }
            )
            _require(
                actual_sha256 == source["expected_sha256"],
                "content_fingerprint_mismatch",
                f"source_set.sources.{dataset_id}.expected_sha256",
                "exact source bytes do not match the immutable source-set receipt",
            )
            _require(
                source["http_status"] == 200,
                "provider_error_payload",
                f"source_set.sources.{dataset_id}.http_status",
                "must equal 200",
            )
            normalized, headers, selected_column = _normalized_rows(
                dataset, payload, f"source_set.sources.{dataset_id}"
            )
            coverage_status = "validation-fixture-not-assessed"
            receipt.update(
                {
                    "date_min": normalized[0]["observation_date"],
                    "date_max": normalized[-1]["observation_date"],
                    "row_count": len(normalized),
                    "schema": {
                        "columns": headers,
                        "selected_price_column": selected_column,
                        "normalized_fields": [
                            "observation_date",
                            "price",
                            "normalization_timezone",
                            "source_row",
                        ],
                    },
                }
            )
            if source_data["mode"] == "confirmatory":
                eligible_start = _iso_date(
                    dataset["eligible_start"],
                    f"config.historical_datasets.{dataset_id}.eligible_start",
                )
                data_cutoff = _iso_date(
                    dataset["data_cutoff"],
                    f"config.historical_datasets.{dataset_id}.data_cutoff",
                )
                observed_min = date.fromisoformat(
                    str(normalized[0]["observation_date"])
                )
                observed_max = date.fromisoformat(
                    str(normalized[-1]["observation_date"])
                )
                tolerance = MAPPING_TOLERANCE_DAYS[dataset_id]
                _require(
                    observed_min <= eligible_start
                    or (observed_min - eligible_start).days <= tolerance,
                    "incomplete_dataset_coverage",
                    f"source_set.sources.{dataset_id}",
                    "observations do not reach the preregistered eligible start",
                )
                _require(
                    observed_max >= data_cutoff
                    or (data_cutoff - observed_max).days <= tolerance,
                    "incomplete_dataset_coverage",
                    f"source_set.sources.{dataset_id}",
                    "observations do not reach the preregistered data cutoff",
                )
                coverage_status = "satisfies-preregistered-range"
            receipt.update(
                {"status": "accepted", "coverage_status": coverage_status}
            )
            normalized_datasets[dataset_id] = normalized
        except ExperimentValidationError as error:
            failure = {
                "code": error.code,
                "field": error.field,
                "message": str(error),
            }
            receipt.update(
                {
                    "status": "rejected",
                    "coverage_status": "rejected",
                    "rejection": failure,
                }
            )
            dataset_failures[dataset_id] = failure
        receipts.append(receipt)

    receipt_rows = tuple(receipts)
    attempts, versioned_input, reconciliation = _build_episodes(
        config_data,
        source_data,
        normalized_datasets,
        receipt_rows,
        dataset_failures,
    )
    return PreparedHistoricalInput(
        "accepted" if versioned_input is not None else "rejected",
        receipt_rows,
        normalized_datasets,
        attempts,
        versioned_input,
        reconciliation,
    )


def _write_json(path: Path, value: Any) -> None:
    path.write_text(_canonical_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: tuple[Mapping[str, Any], ...]) -> None:
    path.write_text(
        "".join(_canonical_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def _stage_preparation_artifacts(
    directory: Path,
    source_data: Mapping[str, Any],
    prepared: PreparedHistoricalInput,
) -> None:
    _write_json(
        directory / "source-receipts.json",
        {
            "source_set_id": source_data["source_set_id"],
            "receipts": prepared.source_receipts,
        },
    )
    _write_json(
        directory / "normalized-datasets.json",
        {
            "source_set_id": source_data["source_set_id"],
            "datasets": prepared.normalized_datasets,
        },
    )
    _write_jsonl(directory / "episode-attempts.jsonl", prepared.episode_attempts)
    if prepared.versioned_input is not None:
        (directory / "runner-input.json").write_text(
            prepared.versioned_input.canonical_document + "\n",
            encoding="utf-8",
            newline="\n",
        )
    _write_json(directory / "reconciliation.json", prepared.reconciliation)


def _historical_run_id(
    config: StudyConfig,
    source_set: HistoricalSourceSet,
    prepared: PreparedHistoricalInput,
) -> str:
    _require(
        prepared.versioned_input is not None,
        "rejected_historical_input",
        "prepared.versioned_input",
        "validation cannot run when historical preparation was rejected",
    )
    identity = _canonical_json(
        {
            "engine_version": HISTORICAL_ENGINE_VERSION,
            "historical_source_sha256": _fingerprint(Path(__file__).read_bytes()),
            "shared_runner_sha256": _fingerprint(
                Path(sys.modules[run_experiment.__module__].__file__).read_bytes()
            ),
            "config_sha256": config.sha256,
            "source_set_sha256": source_set.sha256,
            "runner_input_sha256": prepared.versioned_input.sha256,
        }
    )
    return f"smartdca-historical-validation-v1-{_fingerprint(identity.encode('utf-8'))}"


def write_historical_preparation(
    config: StudyConfig,
    source_set: HistoricalSourceSet,
    source_root: Path,
    output_root: Path,
) -> HistoricalPreparationBundle:
    """Write the confirmatory rolling-episode handoff without policy execution."""

    _require(isinstance(output_root, Path), "invalid_type", "output_root", "must be pathlib.Path")
    source_data = source_set.as_mapping()
    _require(
        source_data["mode"] == "confirmatory"
        and source_data["confirmatory"] is True,
        "invalid_mode",
        "source_set",
        "input preparation requires a confirmatory full-grid source set",
    )
    prepared = prepare_historical_input(config, source_set, source_root)
    runner_input_sha256 = (
        prepared.versioned_input.sha256
        if prepared.versioned_input is not None
        else None
    )
    identity = _canonical_json(
        {
            "engine_version": HISTORICAL_ENGINE_VERSION,
            "historical_source_sha256": _fingerprint(Path(__file__).read_bytes()),
            "config_sha256": config.sha256,
            "source_set_sha256": source_set.sha256,
            "runner_input_sha256": runner_input_sha256,
            "reconciliation": prepared.reconciliation,
        }
    )
    run_id = f"smartdca-historical-input-v1-{_fingerprint(identity.encode('utf-8'))}"
    output_root.mkdir(parents=True, exist_ok=True)
    final_directory = output_root / run_id
    _require(
        not final_directory.exists(),
        "run_identity_collision",
        "output_root",
        f"{run_id} already exists",
    )
    temporary_directory = Path(
        tempfile.mkdtemp(prefix=f".{run_id}-", dir=output_root)
    )
    try:
        _stage_preparation_artifacts(temporary_directory, source_data, prepared)
        validation: dict[str, Any] = {
            "status": "passed" if prepared.status == "accepted" else "rejected",
            "evidence_tier": "confirmatory-input-preparation",
            "policy_execution": "not-run",
            "confirmatory_aggregate_outcomes": "not-computed",
            "source_set_sha256": source_set.sha256,
            "runner_input_sha256": runner_input_sha256,
            "reconciliation": prepared.reconciliation,
        }
        _write_json(temporary_directory / "validation.json", validation)
        artifact_paths = sorted(
            path for path in temporary_directory.rglob("*") if path.is_file()
        )
        manifest: dict[str, Any] = {
            "schema_version": "smartdca-historical-input-manifest/1",
            "run_id": run_id,
            "engine_version": HISTORICAL_ENGINE_VERSION,
            "historical_source_sha256": _fingerprint(Path(__file__).read_bytes()),
            "config_sha256": config.sha256,
            "source_set_sha256": source_set.sha256,
            "runner_input_sha256": runner_input_sha256,
            "policy_execution": "not-run",
            "artifacts": [
                {
                    "path": str(path.relative_to(temporary_directory)),
                    "sha256": _fingerprint(path.read_bytes()),
                }
                for path in artifact_paths
            ],
        }
        _write_json(temporary_directory / "manifest.json", manifest)
        os.replace(temporary_directory, final_directory)
    except BaseException:
        shutil.rmtree(temporary_directory, ignore_errors=True)
        raise
    return HistoricalPreparationBundle(
        run_id=run_id,
        output_directory=final_directory,
        manifest=manifest,
        prepared=prepared,
        validation=validation,
    )


def run_historical_validation(
    config: StudyConfig,
    source_set: HistoricalSourceSet,
    source_root: Path,
    output_root: Path,
) -> HistoricalRunBundle:
    """Build and execute the declared non-confirmatory validation slice."""

    _require(isinstance(output_root, Path), "invalid_type", "output_root", "must be pathlib.Path")
    source_data = source_set.as_mapping()
    _require(
        source_data["mode"] == "validation" and source_data["confirmatory"] is False,
        "confirmatory_boundary_breached",
        "source_set",
        "historical validation must be explicitly non-confirmatory",
    )
    prepared = prepare_historical_input(config, source_set, source_root)
    _require(
        prepared.versioned_input is not None,
        "rejected_historical_input",
        "prepared.versioned_input",
        "validation source set did not produce both selected episodes",
    )
    run_id = _historical_run_id(config, source_set, prepared)
    output_root.mkdir(parents=True, exist_ok=True)
    final_directory = output_root / run_id
    _require(
        not final_directory.exists(),
        "run_identity_collision",
        "output_root",
        f"{run_id} already exists",
    )
    temporary_directory = Path(
        tempfile.mkdtemp(prefix=f".{run_id}-", dir=output_root)
    )
    try:
        _stage_preparation_artifacts(temporary_directory, source_data, prepared)
        nested_root = temporary_directory / ".runner-output"
        runner = run_experiment(config, prepared.versioned_input, nested_root)
        os.replace(runner.output_directory, temporary_directory / "runner")
        nested_root.rmdir()
        runner = RunBundle(
            run_id=runner.run_id,
            output_directory=temporary_directory / "runner",
            manifest=runner.manifest,
            ledgers=runner.ledgers,
            episode_results=runner.episode_results,
            aggregates=runner.aggregates,
            validation=runner.validation,
        )
        validation: dict[str, Any] = {
            "status": "passed",
            "evidence_tier": "non-confirmatory-infrastructure-validation",
            "confirmatory_aggregate_outcomes": "unopened-and-unreported",
            "source_set_sha256": source_set.sha256,
            "runner_input_sha256": prepared.versioned_input.sha256,
            "reconciliation": prepared.reconciliation,
            "checks": [
                {
                    "code": "exact_source_fingerprints",
                    "status": "passed",
                    "dataset_count": len(prepared.source_receipts),
                },
                {
                    "code": "declared_series_semantics",
                    "status": "passed",
                    "datasets": [row["dataset_id"] for row in prepared.source_receipts],
                },
                {
                    "code": "calendar_mapping_without_interpolation",
                    "status": "passed",
                    "attempted_episode_count": prepared.reconciliation[
                        "attempted_episode_count"
                    ],
                },
                {
                    "code": "episode_count_reconciliation",
                    "status": "passed",
                    "included": prepared.reconciliation["included_episode_count"],
                    "excluded": prepared.reconciliation["excluded_episode_count"],
                },
                {
                    "code": "policy_causal_prefix",
                    "status": "passed",
                    "source": "runner/validation.json#causal_prefix",
                },
            ],
        }
        _write_json(temporary_directory / "validation.json", validation)
        historical_source_sha256 = _fingerprint(Path(__file__).read_bytes())
        shared_runner_sha256 = _fingerprint(
            Path(sys.modules[run_experiment.__module__].__file__).read_bytes()
        )
        artifact_paths = sorted(
            path
            for path in temporary_directory.rglob("*")
            if path.is_file()
        )
        manifest: dict[str, Any] = {
            "schema_version": "smartdca-historical-run-manifest/1",
            "run_id": run_id,
            "engine_version": HISTORICAL_ENGINE_VERSION,
            "historical_source_sha256": historical_source_sha256,
            "shared_runner_sha256": shared_runner_sha256,
            "config_sha256": config.sha256,
            "source_set_sha256": source_set.sha256,
            "runner_input_sha256": prepared.versioned_input.sha256,
            "source_identities": [
                {
                    "dataset_id": row["dataset_id"],
                    "source_identity": row["source_identity"],
                    "sha256": row["sha256"],
                }
                for row in prepared.source_receipts
            ],
            "runtime": {
                "implementation": sys.implementation.name,
                "python": f"{sys.version_info.major}.{sys.version_info.minor}",
                "third_party": [],
            },
            "evidence_tier": "non-confirmatory-infrastructure-validation",
            "artifacts": [
                {
                    "path": str(path.relative_to(temporary_directory)),
                    "sha256": _fingerprint(path.read_bytes()),
                }
                for path in artifact_paths
            ],
        }
        _write_json(temporary_directory / "manifest.json", manifest)
        os.replace(temporary_directory, final_directory)
    except BaseException:
        shutil.rmtree(temporary_directory, ignore_errors=True)
        raise

    final_runner = RunBundle(
        run_id=runner.run_id,
        output_directory=final_directory / "runner",
        manifest=runner.manifest,
        ledgers=runner.ledgers,
        episode_results=runner.episode_results,
        aggregates=runner.aggregates,
        validation=runner.validation,
    )
    return HistoricalRunBundle(
        run_id=run_id,
        output_directory=final_directory,
        manifest=manifest,
        source_receipts=prepared.source_receipts,
        episode_attempts=prepared.episode_attempts,
        reconciliation=prepared.reconciliation,
        validation=validation,
        runner=final_runner,
    )


def main(argv: list[str] | None = None) -> int:
    """Run historical preparation through its reproducible command-line seam."""

    parser = argparse.ArgumentParser(
        description="Prepare or validate preregistered SmartDCA historical inputs."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser(
        "validate", help="run the non-confirmatory historical fixture slice"
    )
    validate.add_argument("--config", required=True, type=Path)
    validate.add_argument("--source-set", required=True, type=Path)
    validate.add_argument("--source-root", required=True, type=Path)
    validate.add_argument("--output-root", required=True, type=Path)
    acquire = commands.add_parser(
        "acquire", help="retrieve and fingerprint the locked provider responses"
    )
    acquire.add_argument("--config", required=True, type=Path)
    acquire.add_argument("--source-root", required=True, type=Path)
    prepare = commands.add_parser(
        "prepare", help="write the full rolling input without running policies"
    )
    prepare.add_argument("--config", required=True, type=Path)
    prepare.add_argument("--source-set", required=True, type=Path)
    prepare.add_argument("--source-root", required=True, type=Path)
    prepare.add_argument("--output-root", required=True, type=Path)
    arguments = parser.parse_args(argv)
    completion_code = 0
    completion_stream = sys.stdout
    try:
        from reproducibility.empirical import load_study_config

        if arguments.command == "validate":
            bundle = run_historical_validation(
                load_study_config(arguments.config),
                load_historical_source_set(arguments.source_set),
                arguments.source_root,
                arguments.output_root,
            )
            completion = {
                "status": "completed",
                "run_id": bundle.run_id,
                "output_directory": str(bundle.output_directory.resolve()),
                "manifest": str((bundle.output_directory / "manifest.json").resolve()),
            }
        elif arguments.command == "acquire":
            provider = AlphaVantageProvider(
                os.environ.get("ALPHAVANTAGE_API_KEY", "")
            )
            source_set = acquire_historical_sources(
                load_study_config(arguments.config),
                arguments.source_root,
                provider,
                datetime.now(timezone.utc)
                .isoformat(timespec="seconds")
                .replace("+00:00", "Z"),
            )
            completion = {
                "status": "acquired",
                "source_set": str(
                    (arguments.source_root / "historical-source-set.json").resolve()
                ),
                "source_set_sha256": source_set.sha256,
            }
        elif arguments.command == "prepare":
            preparation = write_historical_preparation(
                load_study_config(arguments.config),
                load_historical_source_set(arguments.source_set),
                arguments.source_root,
                arguments.output_root,
            )
            preparation_rejected = preparation.validation["status"] == "rejected"
            completion = {
                "status": "rejected" if preparation_rejected else "completed",
                "run_id": preparation.run_id,
                "output_directory": str(preparation.output_directory.resolve()),
                "manifest": str(
                    (preparation.output_directory / "manifest.json").resolve()
                ),
                "policy_execution": "not-run",
                "failed_dataset_count": preparation.prepared.reconciliation[
                    "failed_dataset_count"
                ],
            }
            if preparation_rejected:
                completion_code = 2
                completion_stream = sys.stderr
        else:  # argparse makes this unreachable.
            raise AssertionError(f"unsupported command: {arguments.command}")
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
    print(_canonical_json(completion), file=completion_stream)
    return completion_code


if __name__ == "__main__":
    raise SystemExit(main())
