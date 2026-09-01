"""Independent publication review for the safety-adaptivity empirical package.

The numerical replay in this module deliberately imports no SmartDCA runner.
Producer commands are executed only to test clean regeneration; their outputs
are then checked against a separately implemented Decimal ledger recurrence.
"""

from __future__ import annotations

import argparse
from bisect import bisect_left, bisect_right
import csv
import hashlib
import json
import random
import subprocess
import sys
from datetime import date
from decimal import ROUND_FLOOR, ROUND_HALF_EVEN, Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping


ZERO = Decimal("0")
HALF = Decimal("0.5")
ONE = Decimal("1")
TOLERANCE = Decimal("1e-48")
RESULT_DECIMAL_FIELDS = (
    "terminal_wealth_gap",
    "relative_terminal_wealth_gap",
    "wealth_ratio",
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
)

DETERMINISTIC_RUN_ID = (
    "smartdca-deterministic-v1-"
    "80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db"
)
STOCHASTIC_RUN_ID = (
    "smartdca-stochastic-v1-"
    "78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25"
)
HISTORICAL_RUN_ID = (
    "smartdca-historical-study-v1-"
    "5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221"
)
ROBUSTNESS_RUN_ID = (
    "smartdca-historical-robustness-v1-"
    "0991d999e1a8070a2a6eb8046b08a91d0e42341995610a602372c52dfab14184"
)
SYNTHESIS_RUN_ID = (
    "smartdca-synthesis-v1-"
    "394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26"
)
CANONICAL_RUN_ID = (
    "smartdca-run-v1-"
    "b029028a9a8e5104359c4999b26e42f1dc81207eb4eb29b1dfba9fcae83473e0"
)
HISTORICAL_VALIDATION_RUN_ID = (
    "smartdca-historical-validation-v1-"
    "d376ff1411774e40978ea1aa4c0dcf4e18603d93fbfcb017cbfa18538ea7b499"
)
RETAINED_REVIEW_REGISTRY = Path(
    "experiments/inputs/empirical-package-publication-review-v1.json"
)


class PublicationReviewError(RuntimeError):
    """An externally visible publication-review failure."""

    def __init__(self, code: str, field: str, message: str) -> None:
        self.code = code
        self.field = field
        super().__init__(f"{code} at {field}: {message}")


def _require(condition: bool, code: str, field: str, message: str) -> None:
    if not condition:
        raise PublicationReviewError(code, field, message)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _content_addressed_id(prefix: str, identity: Mapping[str, Any]) -> str:
    return prefix + _sha256(_canonical_json(identity).encode("utf-8"))


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), "invalid_json", str(path), "must be an object")
    return value


def _load_jsonl(path: Path) -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            value = json.loads(line)
            _require(
                isinstance(value, dict),
                "invalid_jsonl",
                f"{path}:{line_number}",
                "must be an object",
            )
            rows.append(value)
    return tuple(rows)


def _decimal(value: object, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except Exception as error:
        raise PublicationReviewError(
            "invalid_decimal", field, "must be a finite decimal"
        ) from error
    _require(result.is_finite(), "invalid_decimal", field, "must be finite")
    return result


def _assert_decimal(actual: Decimal, expected: object, field: str) -> None:
    expected_decimal = _decimal(expected, field)
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_HALF_EVEN
        _require(
            abs(actual - expected_decimal) <= TOLERANCE,
            "independent_replay_mismatch",
            field,
            f"expected {expected_decimal}, observed {actual}",
        )


def _power(base: Decimal, exponent: Decimal) -> Decimal:
    _require(base > ZERO, "invalid_power", "replay", "base must be positive")
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_HALF_EVEN
        return (base.ln() * exponent).exp()


def _reference(
    normalized_prices: tuple[Decimal, ...], alpha: Decimal, beta: Decimal
) -> Decimal:
    if len(normalized_prices) == 1:
        return normalized_prices[0]
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_HALF_EVEN
        if alpha == beta:
            weights = tuple(_power(price, alpha) for price in normalized_prices)
            return (
                sum(
                    (
                        weight * price.ln()
                        for price, weight in zip(
                            normalized_prices, weights, strict=True
                        )
                    ),
                    ZERO,
                )
                / sum(weights, ZERO)
            ).exp()
        numerator = sum(
            (_power(price, alpha) for price in normalized_prices), ZERO
        )
        denominator = sum(
            (_power(price, beta) for price in normalized_prices), ZERO
        )
        return _power(numerator / denominator, ONE / (alpha - beta))


def _purchase(
    budget: Decimal,
    available: Decimal,
    fixed_fee: Decimal,
    proportional_bps: Decimal,
) -> tuple[Decimal, Decimal]:
    bounded_budget = min(max(budget, ZERO), available)
    if bounded_budget <= fixed_fee:
        return ZERO, ZERO
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_FLOOR
        rate = proportional_bps / Decimal("10000")
        notional = (bounded_budget - fixed_fee) / (ONE + rate)
        return notional, fixed_fee + rate * notional


def _dca_ledger(
    observations: list[dict[str, Any]],
    evaluation_price: Decimal,
    cost: Mapping[str, Any],
) -> dict[str, Any]:
    fixed_fee = _decimal(cost["fixed_fee"], "cost.fixed_fee")
    proportional_bps = _decimal(
        cost["proportional_bps"], "cost.proportional_bps"
    )
    cash = units = total_fees = ZERO
    steps: list[dict[str, Any]] = []
    for period, row in enumerate(observations, start=1):
        price = _decimal(row["price"], "observation.price")
        deposit = _decimal(row["deposit"], "observation.deposit")
        available = cash + deposit
        notional, fee = _purchase(available, available, fixed_fee, proportional_bps)
        cash = available - notional - fee
        units += notional / price
        total_fees += fee
        steps.append(
            {
                "period": period,
                "date": row["date"],
                "price": price,
                "deposit": deposit,
                "available_cash": available,
                "target_purchase_budget": notional + fee,
                "purchase": notional,
                "fee": fee,
                "cash": cash,
                "units": units,
                "dca_units": units,
                "reference": None,
                "relative_price": None,
                "score": None,
                "coverage_before": None,
                "raw_guardrail_floor": None,
                "guardrail_floor": None,
                "floor_active": None,
                "discretionary_cash": None,
                "coverage_after": None,
            }
        )
    return {
        "policy": "dca",
        "steps": steps,
        "terminal_cash": cash,
        "terminal_units": units,
        "terminal_asset_value": evaluation_price * units,
        "terminal_wealth": cash + evaluation_price * units,
        "total_fees": total_fees,
    }


def _guarded_ledger(
    observations: list[dict[str, Any]],
    evaluation_price: Decimal,
    coverage: Decimal,
    mean: Mapping[str, Any],
    cost: Mapping[str, Any],
    dca: Mapping[str, Any],
    *,
    neutral: bool,
) -> dict[str, Any]:
    fixed_fee = _decimal(cost["fixed_fee"], "cost.fixed_fee")
    proportional_bps = _decimal(
        cost["proportional_bps"], "cost.proportional_bps"
    )
    alpha = _decimal(mean["alpha"], "mean.alpha")
    beta = _decimal(mean["beta"], "mean.beta")
    prices = tuple(
        _decimal(row["price"], "observation.price") for row in observations
    )
    anchor = prices[0]
    cash = units = dca_units_before = total_fees = ZERO
    steps: list[dict[str, Any]] = []
    for index, row in enumerate(observations):
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
            normalized = tuple(price_value / anchor for price_value in prices[:index])
            reference = _reference(normalized, alpha, beta)
            relative = (price / anchor) / reference
            score = HALF if neutral else ONE / (
                ONE + _power(relative, ONE - alpha)
            )
        target = floor + score * discretionary
        notional, fee = _purchase(target, available, fixed_fee, proportional_bps)
        cash = available - notional - fee
        units += notional / price
        total_fees += fee
        dca_units = dca["steps"][index]["units"]
        steps.append(
            {
                "period": index + 1,
                "date": row["date"],
                "price": price,
                "deposit": deposit,
                "available_cash": available,
                "target_purchase_budget": target,
                "purchase": notional,
                "fee": fee,
                "cash": cash,
                "units": units,
                "dca_units": dca_units,
                "reference": reference,
                "relative_price": relative,
                "score": score,
                "coverage_before": coverage_before,
                "raw_guardrail_floor": raw_floor,
                "guardrail_floor": floor,
                "floor_active": raw_floor > ZERO,
                "discretionary_cash": discretionary,
                "coverage_after": units - coverage * dca_units,
            }
        )
        dca_units_before = dca_units
    return {
        "policy": "neutral_guarded" if neutral else "corrected_guarded",
        "steps": steps,
        "terminal_cash": cash,
        "terminal_units": units,
        "terminal_asset_value": evaluation_price * units,
        "terminal_wealth": cash + evaluation_price * units,
        "total_fees": total_fees,
    }


def _ledger_key(ledger: Mapping[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        str(ledger["episode_id"]),
        str(ledger["coverage"]),
        str(ledger["corrected_mean_config"]),
        str(ledger["cost_scenario"]),
        str(ledger["policy"]),
    )


def _compare_ledger(
    replay: Mapping[str, Any], expected: Mapping[str, Any], field: str
) -> int:
    _require(
        replay["policy"] == expected["policy"],
        "independent_replay_mismatch",
        f"{field}.policy",
        "policy differs",
    )
    replay_steps = replay["steps"]
    expected_steps = expected["steps"]
    _require(
        len(replay_steps) == len(expected_steps),
        "independent_replay_mismatch",
        f"{field}.steps",
        "step count differs",
    )
    numeric_fields = (
        "price",
        "deposit",
        "available_cash",
        "target_purchase_budget",
        "purchase",
        "fee",
        "cash",
        "units",
        "dca_units",
        "reference",
        "relative_price",
        "score",
        "coverage_before",
        "raw_guardrail_floor",
        "guardrail_floor",
        "discretionary_cash",
        "coverage_after",
    )
    for index, (actual_step, expected_step) in enumerate(
        zip(replay_steps, expected_steps, strict=True)
    ):
        prefix = f"{field}.steps[{index}]"
        _require(
            actual_step["period"] == expected_step["period"]
            and actual_step["date"] == expected_step["date"]
            and actual_step["floor_active"] == expected_step["floor_active"],
            "independent_replay_mismatch",
            prefix,
            "period, date, or activation differs",
        )
        for name in numeric_fields:
            actual_value = actual_step[name]
            expected_value = expected_step[name]
            if actual_value is None or expected_value is None:
                _require(
                    actual_value is expected_value,
                    "independent_replay_mismatch",
                    f"{prefix}.{name}",
                    "nullability differs",
                )
            else:
                _assert_decimal(actual_value, expected_value, f"{prefix}.{name}")
    for name in (
        "terminal_cash",
        "terminal_units",
        "terminal_asset_value",
        "terminal_wealth",
        "total_fees",
    ):
        _assert_decimal(replay[name], expected[name], f"{field}.{name}")
    return len(replay_steps)


def _check_ledger_invariants(
    ledger: Mapping[str, Any],
    cost: Mapping[str, Any],
    coverage: Decimal,
) -> tuple[int, int]:
    fixed_fee = _decimal(cost["fixed_fee"], "cost.fixed_fee")
    rate = _decimal(cost["proportional_bps"], "cost.proportional_bps") / Decimal(
        "10000"
    )
    cumulative_deposits = cumulative_outlay = previous_units = ZERO
    coverage_checks = 0
    for index, step in enumerate(ledger["steps"]):
        cumulative_deposits += step["deposit"]
        cumulative_outlay += step["purchase"] + step["fee"]
        expected_fee = (
            fixed_fee + rate * step["purchase"]
            if step["purchase"] > ZERO
            else ZERO
        )
        _require(
            abs(step["cash"] + cumulative_outlay - cumulative_deposits)
            <= TOLERANCE
            and step["cash"] >= ZERO
            and step["purchase"] >= ZERO
            and step["units"] + TOLERANCE >= previous_units
            and step["purchase"] + step["fee"]
            <= step["target_purchase_budget"] + TOLERANCE
            and abs(step["fee"] - expected_fee) <= TOLERANCE,
            "independent_invariant_failure",
            f"{ledger['policy']}.steps[{index}]",
            "funding, buy-only, selected-budget, or fee invariant failed",
        )
        previous_units = step["units"]
        if ledger["policy"] == "dca":
            _require(
                all(
                    step[field] is None
                    for field in (
                        "reference",
                        "score",
                        "guardrail_floor",
                        "coverage_after",
                    )
                ),
                "independent_invariant_failure",
                f"dca.steps[{index}]",
                "guarded-policy state leaked into independent DCA",
            )
        else:
            expected_raw = (
                coverage * step["deposit"]
                - step["price"] * step["coverage_before"]
            )
            _require(
                abs(step["raw_guardrail_floor"] - expected_raw) <= TOLERANCE
                and abs(
                    step["guardrail_floor"]
                    - max(ZERO, step["raw_guardrail_floor"])
                )
                <= TOLERANCE
                and abs(
                    step["available_cash"]
                    - step["guardrail_floor"]
                    - step["discretionary_cash"]
                )
                <= TOLERANCE
                and abs(
                    step["target_purchase_budget"]
                    - step["guardrail_floor"]
                    - step["score"] * step["discretionary_cash"]
                )
                <= TOLERANCE,
                "independent_invariant_failure",
                f"{ledger['policy']}.steps[{index}]",
                "guardrail or discretionary-score contract failed",
            )
            if fixed_fee == ZERO and rate == ZERO:
                _require(
                    step["coverage_after"] >= -TOLERANCE,
                    "independent_invariant_failure",
                    f"{ledger['policy']}.steps[{index}].coverage_after",
                    "frictionless unit coverage failed",
                )
                coverage_checks += 1
    _require(
        abs(
            ledger["terminal_cash"]
            + ledger["terminal_asset_value"]
            - ledger["terminal_wealth"]
        )
        <= TOLERANCE,
        "independent_invariant_failure",
        f"{ledger['policy']}.terminal_wealth",
        "direct cash-plus-asset accounting failed",
    )
    return len(ledger["steps"]), coverage_checks


def _independent_deterministic_replay(repository_root: Path) -> dict[str, Any]:
    run = repository_root / "reports/experiments/runs" / DETERMINISTIC_RUN_ID
    inputs = _load_json(run / "runner-input.json")
    config = _load_json(
        repository_root / "experiments/protocols/safety-adaptivity-v1.json"
    )
    expected_ledgers = {
        _ledger_key(row): row for row in _load_jsonl(run / "runner/ledgers.jsonl")
    }
    _require(
        len(expected_ledgers) == 648,
        "unexpected_evidence_shape",
        "deterministic.ledgers",
        "expected 648 unique ledgers",
    )
    matched_steps = 0
    guardrail_steps = 0
    invariant_steps = 0
    coverage_steps = 0
    scenario_count = 0
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_HALF_EVEN
        for episode in inputs["episodes"]:
            observations = episode["observations"]
            evaluation_price = _decimal(
                episode["evaluation_price"], "episode.evaluation_price"
            )
            for coverage_text in config["coverage"]["primary"]:
                coverage = _decimal(coverage_text, "coverage")
                for mean in config["corrected_mean"]["primary"]:
                    for cost in config["cost_scenarios"]:
                        dca = _dca_ledger(observations, evaluation_price, cost)
                        neutral = _guarded_ledger(
                            observations,
                            evaluation_price,
                            coverage,
                            mean,
                            cost,
                            dca,
                            neutral=True,
                        )
                        corrected = _guarded_ledger(
                            observations,
                            evaluation_price,
                            coverage,
                            mean,
                            cost,
                            dca,
                            neutral=False,
                        )
                        for replay in (dca, neutral, corrected):
                            key = (
                                episode["episode_id"],
                                coverage_text,
                                mean["config_id"],
                                cost["cost_id"],
                                replay["policy"],
                            )
                            _require(
                                key in expected_ledgers,
                                "missing_evidence",
                                "deterministic.ledgers",
                                f"missing {key}",
                            )
                            matched_steps += _compare_ledger(
                                replay,
                                expected_ledgers[key],
                                "deterministic." + ".".join(key),
                            )
                            invariant_count, coverage_count = _check_ledger_invariants(
                                replay, cost, coverage
                            )
                            invariant_steps += invariant_count
                            coverage_steps += coverage_count
                        guardrail_steps += len(observations) * 2
                        scenario_count += 1
    return {
        "status": "passed",
        "implementation": "repository-independent Decimal ledger replay",
        "producer_module_imported": False,
        "episode_count": len(inputs["episodes"]),
        "scenario_count": scenario_count,
        "ledger_count": len(expected_ledgers),
        "matched_step_count": matched_steps,
        "invariant_step_count": invariant_steps,
        "frictionless_coverage_step_count": coverage_steps,
        "guardrail_step_count": guardrail_steps,
    }


def _mean(values: list[Decimal]) -> Decimal:
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_HALF_EVEN
        return sum(values, ZERO) / Decimal(len(values))


def _median(values: list[Decimal]) -> Decimal:
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_HALF_EVEN
        ordered = sorted(values)
        midpoint = len(ordered) // 2
        if len(ordered) % 2:
            return ordered[midpoint]
        return (ordered[midpoint - 1] + ordered[midpoint]) / Decimal(2)


def _quantile(values: list[Decimal], probability: Decimal) -> Decimal:
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_HALF_EVEN
        ordered = sorted(values)
        if len(ordered) == 1:
            return ordered[0]
        position = Decimal(len(ordered) - 1) * probability
        lower = int(position)
        upper = min(lower + 1, len(ordered) - 1)
        fraction = position - Decimal(lower)
        return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def _policy_metrics(ledger: Mapping[str, Any]) -> dict[str, Decimal | int | None]:
    terminal_cash = ledger["terminal_cash"]
    terminal_asset_value = ledger["terminal_asset_value"]
    terminal_wealth = ledger["terminal_wealth"]
    total_deposits = sum((step["deposit"] for step in ledger["steps"]), ZERO)
    purchase_count = sum(step["purchase"] > ZERO for step in ledger["steps"])
    if ledger["policy"] == "dca":
        activation_frequency = ZERO
        mean_floor = None
    else:
        activation_frequency = Decimal(
            sum(step["floor_active"] is True for step in ledger["steps"])
        ) / Decimal(len(ledger["steps"]))
        mean_floor = _mean([step["guardrail_floor"] for step in ledger["steps"]])
    return {
        "cash_drag": terminal_cash / total_deposits if total_deposits > ZERO else None,
        "asset_exposure": (
            terminal_asset_value / terminal_wealth if terminal_wealth > ZERO else None
        ),
        "guardrail_activation_frequency": activation_frequency,
        "mean_guardrail_floor": mean_floor,
        "purchase_count": purchase_count,
        "total_fees": ledger["total_fees"],
    }


def _comparison(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    evaluation_price: Decimal,
) -> dict[str, Decimal | int | None | str]:
    cash_gap = left["terminal_cash"] - right["terminal_cash"]
    unit_gap = left["terminal_units"] - right["terminal_units"]
    wealth_gap = left["terminal_wealth"] - right["terminal_wealth"]
    attributed = cash_gap + evaluation_price * unit_gap
    left_metrics = _policy_metrics(left)
    right_metrics = _policy_metrics(right)
    return {
        "comparison": f"{left['policy']}_vs_{right['policy']}",
        "terminal_wealth_gap": wealth_gap,
        "relative_terminal_wealth_gap": wealth_gap / right["terminal_wealth"],
        "wealth_ratio": left["terminal_wealth"] / right["terminal_wealth"],
        "terminal_cash_gap": cash_gap,
        "terminal_unit_gap": unit_gap,
        "cash_contribution": cash_gap,
        "unit_contribution": evaluation_price * unit_gap,
        "identity_residual": wealth_gap - attributed,
        **{f"left_{key}": value for key, value in left_metrics.items()},
        **{f"right_{key}": value for key, value in right_metrics.items()},
    }


def _compare_result(
    replay: Mapping[str, Any], expected: Mapping[str, Any], field: str
) -> None:
    _require(
        replay["comparison"] == expected["comparison"],
        "independent_replay_mismatch",
        f"{field}.comparison",
        "comparison differs",
    )
    for name in RESULT_DECIMAL_FIELDS:
        actual = replay[name]
        expected_value = expected[name]
        if actual is None or expected_value is None:
            _require(
                actual is None and expected_value is None,
                "independent_replay_mismatch",
                f"{field}.{name}",
                "nullability differs",
            )
        else:
            _assert_decimal(actual, expected_value, f"{field}.{name}")
    for name in ("left_purchase_count", "right_purchase_count"):
        _require(
            replay[name] == expected[name],
            "independent_replay_mismatch",
            f"{field}.{name}",
            "count differs",
        )


def _numeric_result(row: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "episode_id": row["episode_id"],
        "comparison": row["comparison"],
        "left_purchase_count": int(row["left_purchase_count"]),
        "right_purchase_count": int(row["right_purchase_count"]),
    }
    for name in RESULT_DECIMAL_FIELDS:
        result[name] = None if row[name] is None else _decimal(row[name], name)
    return result


def _verify_private_artifacts(
    repository_root: Path,
    preparation: Path,
    historical_run: Path,
) -> dict[str, Any]:
    public_preparation = (
        repository_root
        / "experiments/inputs/historical-yahoo-preparation-manifest-v5.json"
    )
    _require(
        public_preparation.read_bytes() == (preparation / "manifest.json").read_bytes(),
        "accepted_preparation_mismatch",
        str(preparation),
        "private manifest differs from accepted version 5",
    )
    public_run = repository_root / "reports/experiments/runs" / HISTORICAL_RUN_ID
    _require(
        (public_run / "manifest.json").read_bytes()
        == (historical_run / "manifest.json").read_bytes(),
        "accepted_historical_run_mismatch",
        str(historical_run),
        "private manifest differs from published manifest",
    )
    receipt = _load_json(public_run / "private-artifact-receipt.json")
    checked_preparation = 0
    for artifact in receipt["accepted_preparation_artifacts"]:
        path = preparation / artifact["path"]
        _require(path.is_file(), "missing_private_artifact", str(path), "file is absent")
        _require(
            _sha256(path.read_bytes()) == artifact["sha256"],
            "private_artifact_fingerprint_mismatch",
            str(path),
            "SHA-256 differs from public receipt",
        )
        checked_preparation += 1
    checked_run = 0
    for artifact in receipt["generated_private_artifacts"]:
        path = historical_run / artifact["path"]
        _require(path.is_file(), "missing_private_artifact", str(path), "file is absent")
        _require(
            path.stat().st_size == artifact["bytes"]
            and _sha256(path.read_bytes()) == artifact["sha256"],
            "private_artifact_fingerprint_mismatch",
            str(path),
            "size or SHA-256 differs from public receipt",
        )
        checked_run += 1
    source_receipts = _load_json(preparation / "source-receipts.json")["receipts"]
    source_root = repository_root / "data/raw/yahoo-finance-accepted-v1"
    checked_sources = 0
    for source in source_receipts:
        matches = tuple(source_root.glob(f"{source['dataset_id']}-*.csv"))
        _require(
            len(matches) == 1,
            "missing_private_source",
            source["dataset_id"],
            "expected exactly one retained canonical export",
        )
        _require(
            matches[0].stat().st_size == source["byte_length"]
            and _sha256(matches[0].read_bytes()) == source["sha256"],
            "private_source_fingerprint_mismatch",
            str(matches[0]),
            "size or SHA-256 differs from accepted source receipt",
        )
        checked_sources += 1
    return {
        "accepted_preparation_manifest_sha256": _sha256(public_preparation.read_bytes()),
        "historical_run_manifest_sha256": _sha256(
            (public_run / "manifest.json").read_bytes()
        ),
        "checked_preparation_artifact_count": checked_preparation,
        "checked_private_run_artifact_count": checked_run,
        "checked_source_export_count": checked_sources,
    }


def _validate_spy_source_joins(
    repository_root: Path, episodes: list[dict[str, Any]]
) -> int:
    source_path = next(
        (
            repository_root / "data/raw/yahoo-finance-accepted-v1"
        ).glob("spy-adjusted-daily-*.csv")
    )
    with source_path.open(newline="", encoding="utf-8") as handle:
        source_rows = list(csv.DictReader(handle))
    checked = 0
    for episode in episodes:
        mapping = episode["historical_mapping"]
        schedule = mapping["deposit_schedule"]
        _require(
            len(schedule) == len(episode["observations"]),
            "historical_source_join_mismatch",
            episode["episode_id"],
            "schedule length differs from episode observations",
        )
        for schedule_row, observation in zip(
            schedule, episode["observations"], strict=True
        ):
            raw = source_rows[int(schedule_row["source_row"]) - 2]
            _require(
                raw["timestamp"] == schedule_row["purchase_date"]
                == observation["date"]
                and _decimal(raw["adjusted_close"], "source.adjusted_close")
                == _decimal(schedule_row["price"], "schedule.price")
                == _decimal(observation["price"], "observation.price"),
                "historical_source_join_mismatch",
                episode["episode_id"],
                "purchase date or adjusted-close value differs",
            )
            checked += 1
        evaluation = source_rows[int(mapping["evaluation_source_row"]) - 2]
        _require(
            evaluation["timestamp"] == episode["evaluation_date"]
            and _decimal(evaluation["adjusted_close"], "source.adjusted_close")
            == _decimal(episode["evaluation_price"], "episode.evaluation_price"),
            "historical_source_join_mismatch",
            episode["episode_id"],
            "evaluation date or adjusted-close value differs",
        )
        checked += 1
    return checked


def _add_calendar_months(value: date, months: int) -> date:
    month_index = value.year * 12 + value.month - 1 + months
    return date(month_index // 12, month_index % 12 + 1, value.day)


def _audit_full_historical_calendar(
    repository_root: Path,
    preparation: Path,
    input_document: Mapping[str, Any],
) -> dict[str, int]:
    config = _load_json(
        repository_root / "experiments/protocols/safety-adaptivity-yahoo-v2.json"
    )
    receipts = {
        row["dataset_id"]: row
        for row in _load_json(preparation / "source-receipts.json")["receipts"]
    }
    episodes = {row["episode_id"]: row for row in input_document["episodes"]}
    _require(
        len(episodes) == len(input_document["episodes"]),
        "duplicate_historical_episode",
        "runner-input.json",
        "episode IDs must be unique",
    )
    source_root = repository_root / "data/raw/yahoo-finance-accepted-v1"
    mapping_tolerance_days = {"btc-usd-daily": 1, "spy-adjusted-daily": 7}
    matched_episodes = 0
    matched_purchases = 0
    source_observations = 0
    for dataset in sorted(config["historical_datasets"], key=lambda row: row["dataset_id"]):
        dataset_id = dataset["dataset_id"]
        receipt = receipts[dataset_id]
        matches = tuple(source_root.glob(f"{dataset_id}-*.csv"))
        _require(
            len(matches) == 1,
            "missing_private_source",
            dataset_id,
            "expected exactly one retained canonical export",
        )
        with matches[0].open(newline="", encoding="utf-8") as handle:
            raw_rows = list(csv.DictReader(handle))
        selected_column = receipt["schema"]["selected_price_column"]
        dates = [date.fromisoformat(row["timestamp"]) for row in raw_rows]
        _require(
            len(raw_rows) == receipt["row_count"]
            and dates == sorted(set(dates))
            and all(_decimal(row[selected_column], dataset_id) > ZERO for row in raw_rows),
            "historical_source_shape_mismatch",
            dataset_id,
            "row count, date order, uniqueness, or positive-price rule differs",
        )
        source_observations += len(raw_rows)
        eligible = date.fromisoformat(dataset["eligible_start"])
        first_start = date(eligible.year, eligible.month, 1)
        if first_start < eligible:
            first_start = _add_calendar_months(first_start, 1)
        cutoff = date.fromisoformat(dataset["data_cutoff"])
        tolerance = mapping_tolerance_days[dataset_id]
        for horizon in config["episode_design"]["horizons_months"]:
            nominal_start = first_start
            while _add_calendar_months(nominal_start, horizon) <= cutoff:
                episode_id = f"{dataset_id}-{nominal_start.isoformat()}-{horizon}m"
                _require(
                    episode_id in episodes,
                    "historical_calendar_mismatch",
                    episode_id,
                    "reconstructed episode is absent from runner input",
                )
                episode = episodes[episode_id]
                mapping = episode["historical_mapping"]
                expected_schedule: list[dict[str, Any]] = []
                expected_observations: list[dict[str, str]] = []
                for offset in range(horizon):
                    nominal = _add_calendar_months(nominal_start, offset)
                    source_index = bisect_left(dates, nominal)
                    _require(
                        source_index < len(raw_rows)
                        and (dates[source_index] - nominal).days <= tolerance,
                        "historical_calendar_mismatch",
                        episode_id,
                        "registered deposit has no independently eligible source row",
                    )
                    raw = raw_rows[source_index]
                    price = raw[selected_column]
                    expected_schedule.append(
                        {
                            "nominal_date": nominal.isoformat(),
                            "purchase_date": raw["timestamp"],
                            "mapping_lag_days": (dates[source_index] - nominal).days,
                            "source_row": source_index + 2,
                            "price": price,
                            "deposit": str(config["episode_design"]["deposit_amount"]),
                        }
                    )
                    expected_observations.append(
                        {
                            "date": raw["timestamp"],
                            "price": price,
                            "deposit": str(config["episode_design"]["deposit_amount"]),
                        }
                    )
                    matched_purchases += 1
                horizon_date = _add_calendar_months(nominal_start, horizon)
                evaluation_index = bisect_right(dates, horizon_date) - 1
                _require(
                    evaluation_index >= 0
                    and (horizon_date - dates[evaluation_index]).days <= tolerance,
                    "historical_calendar_mismatch",
                    episode_id,
                    "registered evaluation has no independently eligible source row",
                )
                evaluation = raw_rows[evaluation_index]
                _require(
                    episode["dataset_id"] == dataset_id
                    and episode["horizon_months"] == horizon
                    and episode["observations"] == expected_observations
                    and episode["evaluation_date"] == evaluation["timestamp"]
                    and episode["evaluation_price"] == evaluation[selected_column]
                    and mapping
                    == {
                        "dataset_source_identity": receipt["source_identity"],
                        "nominal_start": nominal_start.isoformat(),
                        "horizon_date": horizon_date.isoformat(),
                        "deposit_schedule": expected_schedule,
                        "evaluation_source_row": evaluation_index + 2,
                    },
                    "historical_calendar_mismatch",
                    episode_id,
                    "calendar, source-row, value, or runner-input record differs",
                )
                matched_episodes += 1
                nominal_start = _add_calendar_months(
                    nominal_start, config["episode_design"]["rolling_stride_months"]
                )
    _require(
        matched_episodes == len(episodes) == 1365,
        "historical_calendar_mismatch",
        "runner-input.json",
        "reconstructed and retained episode sets differ",
    )
    return {
        "full_calendar_episode_match_count": matched_episodes,
        "full_calendar_purchase_mapping_count": matched_purchases,
        "full_calendar_source_observation_count": source_observations,
    }


def _aggregate_slice(rows: list[Mapping[str, Any]]) -> dict[str, Decimal | int]:
    gaps = [row["terminal_wealth_gap"] for row in rows]
    relative = [row["relative_terminal_wealth_gap"] for row in rows]
    ratios = [row["wealth_ratio"] for row in rows]
    aggregate: dict[str, Decimal | int] = {
        "sample_count": len(rows),
        "attempted_count": len(rows),
        "runner_attempted_count": len(rows),
        "excluded_count": 0,
        "preparation_excluded_count": 0,
        "result_excluded_count": 0,
        "mean_terminal_wealth_gap": _mean(gaps),
        "mean_wealth_ratio": _mean(ratios),
        "win_count": sum(value > ZERO for value in gaps),
        "tie_count": sum(value == ZERO for value in gaps),
        "loss_count": sum(value < ZERO for value in gaps),
        "median_wealth_ratio": _median(ratios),
        "minimum_wealth_ratio": min(ratios),
        "maximum_wealth_ratio": max(ratios),
        "mean_relative_terminal_wealth_gap": _mean(relative),
        "median_relative_terminal_wealth_gap": _median(relative),
        "minimum_relative_terminal_wealth_gap": min(relative),
        "maximum_relative_terminal_wealth_gap": max(relative),
        "worst_observed_relative_shortfall": max(
            ZERO, min(relative).copy_negate()
        ),
    }
    for probability in ("0.05", "0.10", "0.25", "0.75", "0.90", "0.95"):
        aggregate[f"wealth_ratio_quantile_{probability}"] = _quantile(
            ratios, Decimal(probability)
        )
    for probability in ("0.05", "0.10", "0.25"):
        aggregate[f"downside_quantile_{probability}"] = _quantile(
            relative, Decimal(probability)
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
        "left_total_fees",
        "right_total_fees",
    ):
        aggregate[f"mean_{field}"] = _mean([row[field] for row in rows])
    for field in ("left_mean_guardrail_floor", "right_mean_guardrail_floor"):
        values = [row[field] for row in rows if row[field] is not None]
        output = "mean_" + field.replace("_mean_guardrail_floor", "_guardrail_floor")
        aggregate[output] = _mean(values) if values else None
    for side in ("left", "right"):
        aggregate[f"mean_{side}_purchase_count"] = _mean(
            [Decimal(row[f"{side}_purchase_count"]) for row in rows]
        )
    return aggregate


def _compare_aggregate(
    replay: Mapping[str, Any], expected: Mapping[str, Any], field: str
) -> None:
    for name, value in replay.items():
        expected_value = expected[name]
        if isinstance(value, int):
            _require(
                value == expected_value,
                "aggregate_reconciliation_mismatch",
                f"{field}.{name}",
                "count differs",
            )
        elif value is None or expected_value is None:
            _require(
                value is None and expected_value is None,
                "aggregate_reconciliation_mismatch",
                f"{field}.{name}",
                "nullability differs",
            )
        else:
            _assert_decimal(value, expected_value, f"{field}.{name}")


def _bootstrap(
    values: list[Decimal], *, block_length: int, replicates: int, seed: int
) -> dict[str, Any]:
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_HALF_EVEN
        generator = random.Random(seed)
        sample_count = len(values)
        blocks_per_replicate = (sample_count + block_length - 1) // block_length
        statistics: list[Decimal] = []
        for _ in range(replicates):
            resample: list[Decimal] = []
            for _ in range(blocks_per_replicate):
                start = generator.randrange(sample_count)
                resample.extend(
                    values[(start + offset) % sample_count]
                    for offset in range(block_length)
                )
            statistics.append(_median(resample[:sample_count]))
        observed = _median(values)
        tail_count = sum(
            abs(value - observed) >= abs(observed) for value in statistics
        )
        statistic_text = tuple(_decimal_text(value) for value in statistics)
        return {
            "sample_count": sample_count,
            "blocks_per_replicate": blocks_per_replicate,
            "observed_statistic": observed,
            "interval_lower": _quantile(statistics, Decimal("0.025")),
            "interval_upper": _quantile(statistics, Decimal("0.975")),
            "centered_tail_count": tail_count,
            "p_value_numerator": tail_count + 1,
            "p_value_denominator": replicates + 1,
            "replicate_statistics_sha256": _sha256(
                _canonical_json(statistic_text).encode("utf-8")
            ),
        }


def _decimal_text(value: Decimal) -> str:
    if value == ZERO:
        return "0"
    text = format(value.normalize(), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def _cell_seed(
    base_seed: int,
    dataset_id: str,
    horizon: int,
    coverage: str,
    comparison: str,
    mean_id: str,
    cost_id: str,
) -> int:
    payload = "|".join(
        str(value)
        for value in (
            base_seed,
            dataset_id,
            horizon,
            coverage,
            comparison,
            mean_id,
            cost_id,
        )
    ).encode("utf-8")
    return int(_sha256(payload)[:16], 16)


def _verify_holm(cells: list[dict[str, Any]]) -> int:
    comparison_order = {
        "corrected_guarded_vs_dca": 0,
        "corrected_guarded_vs_neutral_guarded": 1,
    }
    ordered = sorted(
        cells,
        key=lambda row: (
            Fraction(row["p_value_numerator"], row["p_value_denominator"]),
            row["dataset_id"],
            row["horizon_months"],
            Decimal(row["coverage"]),
            comparison_order[row["comparison"]],
            row["corrected_mean_config"],
            row["cost_scenario"],
        ),
    )
    running = Fraction(0, 1)
    for index, row in enumerate(ordered):
        unadjusted = Fraction(
            row["p_value_numerator"], row["p_value_denominator"]
        )
        candidate = min(Fraction(1, 1), unadjusted * (len(ordered) - index))
        running = max(running, candidate)
        _require(
            row["holm_rank"] == index + 1
            and row["holm_family_size"] == len(ordered)
            and row["holm_adjusted_p_value_numerator"] == running.numerator
            and row["holm_adjusted_p_value_denominator"] == running.denominator,
            "holm_reconciliation_mismatch",
            row["cell_id"],
            "rank or adjusted p-value differs",
        )
    return len(ordered)


def _private_historical_slice_review(
    repository_root: Path,
    preparation: Path,
    historical_run: Path,
) -> dict[str, Any]:
    artifact_audit = _verify_private_artifacts(
        repository_root, preparation, historical_run
    )
    config = _load_json(
        repository_root / "experiments/protocols/safety-adaptivity-yahoo-v2.json"
    )
    input_document = _load_json(preparation / "runner-input.json")
    calendar_audit = _audit_full_historical_calendar(
        repository_root, preparation, input_document
    )
    dataset_id = "spy-adjusted-daily"
    horizon = 12
    coverage_text = "0.75"
    mean_id = "identity-a0-b0"
    cost_id = "frictionless"
    episodes = [
        episode
        for episode in input_document["episodes"]
        if episode["dataset_id"] == dataset_id
        and episode["horizon_months"] == horizon
    ]
    _require(
        len(episodes) == 383,
        "unexpected_evidence_shape",
        "historical_slice.episodes",
        "expected 383 SPY 12-month episodes",
    )
    source_join_count = _validate_spy_source_joins(repository_root, episodes)
    all_result_rows = _load_jsonl(historical_run / "runner/episode-results.jsonl")
    expected_results: dict[tuple[str, str], dict[str, Any]] = {}
    for row in all_result_rows:
        if (
            row["dataset_id"] == dataset_id
            and row["horizon_months"] == horizon
            and row["coverage"] == coverage_text
            and row["corrected_mean_config"] == mean_id
            and row["cost_scenario"] == cost_id
        ):
            expected_results[(row["episode_id"], row["comparison"])] = row
    _require(
        len(expected_results) == 1149,
        "unexpected_evidence_shape",
        "historical_slice.results",
        "expected three comparisons for 383 episodes",
    )
    mean = next(
        row for row in config["corrected_mean"]["primary"] if row["config_id"] == mean_id
    )
    cost = next(row for row in config["cost_scenarios"] if row["cost_id"] == cost_id)
    coverage = _decimal(coverage_text, "coverage")
    replay_results: dict[str, list[dict[str, Any]]] = {
        "corrected_guarded_vs_dca": [],
        "corrected_guarded_vs_neutral_guarded": [],
        "neutral_guarded_vs_dca": [],
    }
    checked_steps = 0
    causal_prefix_count = 0
    invariant_steps = 0
    coverage_steps = 0
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_HALF_EVEN
        for episode in episodes:
            observations = episode["observations"]
            evaluation = _decimal(episode["evaluation_price"], "evaluation_price")
            dca = _dca_ledger(observations, evaluation, cost)
            neutral = _guarded_ledger(
                observations, evaluation, coverage, mean, cost, dca, neutral=True
            )
            corrected = _guarded_ledger(
                observations, evaluation, coverage, mean, cost, dca, neutral=False
            )
            checked_steps += len(observations) * 3
            for ledger in (dca, neutral, corrected):
                invariant_count, coverage_count = _check_ledger_invariants(
                    ledger, cost, coverage
                )
                invariant_steps += invariant_count
                coverage_steps += coverage_count
            for prefix_length in range(1, len(observations) + 1):
                prefix = observations[:prefix_length]
                prefix_dca = _dca_ledger(prefix, evaluation, cost)
                prefix_neutral = _guarded_ledger(
                    prefix,
                    evaluation,
                    coverage,
                    mean,
                    cost,
                    prefix_dca,
                    neutral=True,
                )
                prefix_corrected = _guarded_ledger(
                    prefix,
                    evaluation,
                    coverage,
                    mean,
                    cost,
                    prefix_dca,
                    neutral=False,
                )
                for full, replay_prefix in (
                    (dca, prefix_dca),
                    (neutral, prefix_neutral),
                    (corrected, prefix_corrected),
                ):
                    _require(
                        full["steps"][:prefix_length] == replay_prefix["steps"],
                        "causal_prefix_mismatch",
                        episode["episode_id"],
                        "decision changed when the unseen suffix was removed",
                    )
                    causal_prefix_count += 1
            comparisons = (
                _comparison(corrected, dca, evaluation),
                _comparison(corrected, neutral, evaluation),
                _comparison(neutral, dca, evaluation),
            )
            for result in comparisons:
                expected = expected_results[
                    (episode["episode_id"], result["comparison"])
                ]
                _compare_result(
                    result,
                    expected,
                    f"historical.{episode['episode_id']}.{result['comparison']}",
                )
                result["episode_id"] = episode["episode_id"]
                replay_results[result["comparison"]].append(result)

    public_aggregates = _load_json(
        repository_root
        / "reports/experiments/runs"
        / HISTORICAL_RUN_ID
        / "historical-aggregates.json"
    )["groups"]
    aggregate_matches = 0
    for comparison, rows in replay_results.items():
        expected = next(
            row
            for row in public_aggregates
            if row["dataset_id"] == dataset_id
            and row["horizon_months"] == horizon
            and row["coverage"] == coverage_text
            and row["corrected_mean_config"] == mean_id
            and row["cost_scenario"] == cost_id
            and row["comparison"] == comparison
        )
        _compare_aggregate(
            _aggregate_slice(rows), expected, f"historical_aggregate.{comparison}"
        )
        aggregate_matches += 1

    all_episodes = {
        episode["episode_id"]: episode for episode in input_document["episodes"]
    }
    primary_raw_groups: dict[
        tuple[str, int, str, str], list[dict[str, Any]]
    ] = {}
    for row in all_result_rows:
        if row["cost_scenario"] != "frictionless" or row["coverage"] == "1":
            continue
        key = (
            row["dataset_id"],
            row["horizon_months"],
            row["coverage"],
            row["comparison"],
        )
        primary_raw_groups.setdefault(key, []).append(_numeric_result(row))
    _require(
        len(primary_raw_groups) == 54,
        "unexpected_evidence_shape",
        "historical.primary_raw_groups",
        "expected 36 confirmatory and 18 architecture groups",
    )
    primary_raw_aggregate_matches = 0
    for key, rows in primary_raw_groups.items():
        group_dataset, group_horizon, group_coverage, group_comparison = key
        expected = next(
            row
            for row in public_aggregates
            if row["dataset_id"] == group_dataset
            and row["horizon_months"] == group_horizon
            and row["coverage"] == group_coverage
            and row["corrected_mean_config"] == mean_id
            and row["cost_scenario"] == cost_id
            and row["comparison"] == group_comparison
        )
        _compare_aggregate(
            _aggregate_slice(rows),
            expected,
            "primary_raw_aggregate."
            + ".".join(str(value) for value in key),
        )
        primary_raw_aggregate_matches += 1

    uncertainty_document = _load_json(
        repository_root
        / "reports/experiments/runs"
        / HISTORICAL_RUN_ID
        / "uncertainty.json"
    )
    bootstrap_matches = 0
    confirmatory_groups = {
        key: rows
        for key, rows in primary_raw_groups.items()
        if key[3]
        in {
            "corrected_guarded_vs_dca",
            "corrected_guarded_vs_neutral_guarded",
        }
    }
    _require(
        len(confirmatory_groups) == 36,
        "unexpected_evidence_shape",
        "historical.confirmatory_groups",
        "expected the registered 36-cell family",
    )
    for key, rows in sorted(
        confirmatory_groups.items(),
        key=lambda item: (
            item[0][0],
            item[0][1],
            Decimal(item[0][2]),
            item[0][3],
        ),
    ):
        group_dataset, group_horizon, group_coverage, comparison = key
        ordered_rows = sorted(
            rows,
            key=lambda row: all_episodes[row["episode_id"]]["historical_mapping"][
                "nominal_start"
            ],
        )
        seed = _cell_seed(
            int(config["uncertainty"]["seed"]),
            group_dataset,
            group_horizon,
            group_coverage,
            comparison,
            mean_id,
            cost_id,
        )
        bootstrap = _bootstrap(
            [row["relative_terminal_wealth_gap"] for row in ordered_rows],
            block_length=group_horizon,
            replicates=int(config["uncertainty"]["replicates"]),
            seed=seed,
        )
        expected = next(
            row
            for row in uncertainty_document["cells"]
            if row["dataset_id"] == group_dataset
            and row["horizon_months"] == group_horizon
            and row["coverage"] == group_coverage
            and row["comparison"] == comparison
        )
        _require(
            seed == expected["cell_seed"]
            and bootstrap["sample_count"] == expected["sample_count"]
            and bootstrap["blocks_per_replicate"] == expected["blocks_per_replicate"]
            and bootstrap["centered_tail_count"] == expected["centered_tail_count"]
            and bootstrap["p_value_numerator"] == expected["p_value_numerator"]
            and bootstrap["p_value_denominator"] == expected["p_value_denominator"]
            and bootstrap["replicate_statistics_sha256"]
            == expected["replicate_statistics_sha256"],
            "bootstrap_reconciliation_mismatch",
            expected["cell_id"],
            "seed, replicate statistics, or p-value differs",
        )
        for field in ("observed_statistic", "interval_lower", "interval_upper"):
            _assert_decimal(bootstrap[field], expected[field], f"bootstrap.{field}")
        bootstrap_matches += 1
    holm_matches = _verify_holm(uncertainty_document["cells"])
    return {
        "status": "passed",
        "dataset_id": dataset_id,
        "horizon_months": horizon,
        "coverage": coverage_text,
        "corrected_mean_config": mean_id,
        "cost_scenario": cost_id,
        "episode_count": len(episodes),
        "comparison_count": sum(len(rows) for rows in replay_results.values()),
        "checked_policy_step_count": checked_steps,
        "invariant_step_count": invariant_steps,
        "frictionless_coverage_step_count": coverage_steps,
        "causal_prefix_policy_count": causal_prefix_count,
        "source_join_count": source_join_count,
        "aggregate_match_count": aggregate_matches,
        "primary_raw_aggregate_match_count": primary_raw_aggregate_matches,
        "bootstrap_cell_match_count": bootstrap_matches,
        "holm_family_match_count": holm_matches,
        "artifact_audit": artifact_audit,
        **calendar_audit,
        "private_values_published": False,
    }


def _verify_private_robustness_artifacts(
    repository_root: Path, robustness_run: Path
) -> dict[str, Any]:
    public_run = repository_root / "reports/experiments/runs" / ROBUSTNESS_RUN_ID
    _require(
        (public_run / "manifest.json").read_bytes()
        == (robustness_run / "manifest.json").read_bytes(),
        "accepted_robustness_run_mismatch",
        str(robustness_run),
        "private manifest differs from published manifest",
    )
    receipt = _load_json(public_run / "private-artifact-receipt.json")
    checked = 0
    for artifact in receipt["generated_private_artifacts"]:
        path = robustness_run / artifact["path"]
        _require(path.is_file(), "missing_private_artifact", str(path), "file is absent")
        _require(
            path.stat().st_size == artifact["bytes"]
            and _sha256(path.read_bytes()) == artifact["sha256"],
            "private_artifact_fingerprint_mismatch",
            str(path),
            "size or SHA-256 differs from public receipt",
        )
        checked += 1
    return {
        "robustness_run_manifest_sha256": _sha256(
            (public_run / "manifest.json").read_bytes()
        ),
        "private_artifact_match_count": checked,
    }


def _review_private_robustness(
    repository_root: Path, robustness_run: Path
) -> dict[str, Any]:
    artifact_audit = _verify_private_robustness_artifacts(
        repository_root, robustness_run
    )
    public_groups = _load_json(
        repository_root
        / "reports/experiments/runs"
        / ROBUSTNESS_RUN_ID
        / "robustness-aggregates.json"
    )["groups"]
    expected = {
        (
            row["schedule_id"],
            row["dataset_id"],
            row["horizon_months"],
            row["coverage"],
            row["comparison"],
            row["corrected_mean_config"],
            row["cost_scenario"],
        ): row
        for row in public_groups
    }
    _require(
        len(expected) == len(public_groups) == 810,
        "unexpected_evidence_shape",
        "robustness.public_groups",
        "expected 810 uniquely keyed robustness groups",
    )
    result_count = 0
    aggregate_matches = 0
    schedules = (
        (
            "primary-monthly-robustness-coverage",
            robustness_run / "monthly-runner/episode-results.jsonl",
            324,
        ),
        (
            "robustness-quarterly-horizons",
            robustness_run / "quarterly-runner/episode-results.jsonl",
            486,
        ),
    )
    for schedule_id, path, expected_group_count in schedules:
        grouped: dict[tuple[object, ...], list[dict[str, Any]]] = {}
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                row = json.loads(line)
                _require(
                    isinstance(row, dict),
                    "invalid_jsonl",
                    f"{path}:{line_number}",
                    "must be an object",
                )
                _require(
                    row["result_status"] == "included"
                    and row["exclusion_reason"] is None,
                    "unexpected_robustness_exclusion",
                    f"{path}:{line_number}",
                    "registered run must contain only included result rows",
                )
                key = (
                    schedule_id,
                    row["dataset_id"],
                    row["horizon_months"],
                    row["coverage"],
                    row["comparison"],
                    row["corrected_mean_config"],
                    row["cost_scenario"],
                )
                _require(
                    key in expected,
                    "unexpected_robustness_group",
                    ".".join(str(value) for value in key),
                    "raw result has no published aggregate cell",
                )
                grouped.setdefault(key, []).append(_numeric_result(row))
                result_count += 1
        _require(
            len(grouped) == expected_group_count,
            "unexpected_evidence_shape",
            schedule_id,
            f"expected {expected_group_count} raw robustness groups",
        )
        for key, rows in grouped.items():
            _compare_aggregate(
                _aggregate_slice(rows),
                expected[key],
                "robustness_raw_aggregate." + ".".join(str(value) for value in key),
            )
            aggregate_matches += 1
    return {
        "status": "passed",
        **artifact_audit,
        "raw_result_count": result_count,
        "raw_aggregate_match_count": aggregate_matches,
        "private_values_published": False,
    }


def _verify_manifest_artifacts(directory: Path) -> dict[str, Any]:
    manifest_path = directory / "manifest.json"
    manifest = _load_json(manifest_path)
    checked = 0
    private_receipts = 0
    for artifact in manifest["artifacts"]:
        retention = artifact.get("retention")
        path = directory / artifact["path"]
        if retention == "private-retained" and not path.is_file():
            private_receipts += 1
            continue
        _require(path.is_file(), "missing_artifact", str(path), "file is absent")
        _require(
            _sha256(path.read_bytes()) == artifact["sha256"],
            "artifact_fingerprint_mismatch",
            str(path),
            "SHA-256 differs from manifest",
        )
        checked += 1
    return {
        "manifest_sha256": _sha256(manifest_path.read_bytes()),
        "checked_artifact_count": checked,
        "private_receipt_artifact_count": private_receipts,
    }


def _compare_regenerated_bundle(
    regenerated: Path, accepted: Path
) -> dict[str, Any]:
    accepted_manifest = _load_json(accepted / "manifest.json")
    compared = 0
    for artifact in accepted_manifest["artifacts"]:
        relative = Path(artifact["path"])
        accepted_path = accepted / relative
        regenerated_path = regenerated / relative
        if not accepted_path.is_file():
            continue
        _require(
            regenerated_path.is_file(),
            "missing_regenerated_artifact",
            str(regenerated_path),
            "file is absent",
        )
        _require(
            regenerated_path.read_bytes() == accepted_path.read_bytes(),
            "regeneration_mismatch",
            str(relative),
            "bytes differ from accepted artifact",
        )
        compared += 1
    _require(
        (regenerated / "manifest.json").read_bytes()
        == (accepted / "manifest.json").read_bytes(),
        "regeneration_mismatch",
        "manifest.json",
        "bytes differ from accepted manifest",
    )
    return {"status": "passed", "byte_identical_artifact_count": compared + 1}


def _run_command(repository_root: Path, arguments: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, *arguments],
        cwd=repository_root,
        check=False,
        capture_output=True,
        text=True,
    )
    _require(
        completed.returncode == 0,
        "reproduction_command_failed",
        " ".join(arguments),
        completed.stderr.strip() or completed.stdout.strip(),
    )
    value = json.loads(completed.stdout)
    _require(
        isinstance(value, dict)
        and value.get("status", "completed") == "completed",
        "invalid_reproduction_receipt",
        " ".join(arguments),
        "command did not emit a completed receipt",
    )
    return value


def _reproduce_deterministic(repository_root: Path, output_root: Path) -> dict[str, Any]:
    receipt = _run_command(
        repository_root,
        [
            "-m",
            "reproducibility.deterministic_study",
            "--config",
            "experiments/protocols/safety-adaptivity-v1.json",
            "--study",
            "experiments/inputs/deterministic-adversarial-v1.json",
            "--output-root",
            str(output_root),
        ],
    )
    _require(
        receipt["study_run_id"] == DETERMINISTIC_RUN_ID,
        "run_identity_mismatch",
        "deterministic.study_run_id",
        "unexpected regenerated identity",
    )
    regenerated = output_root / DETERMINISTIC_RUN_ID
    accepted = repository_root / "reports/experiments/runs" / DETERMINISTIC_RUN_ID
    comparison = _compare_regenerated_bundle(regenerated, accepted)
    return {"study_run_id": DETERMINISTIC_RUN_ID, **comparison}


def _reproduce_synthesis(repository_root: Path, output_root: Path) -> dict[str, Any]:
    receipt = _run_command(
        repository_root,
        [
            "-m",
            "reproducibility.safety_adaptivity_synthesis",
            "--manifest",
            "experiments/inputs/safety-adaptivity-synthesis-v1.json",
            "--output-root",
            str(output_root),
        ],
    )
    _require(
        receipt["synthesis_run_id"] == SYNTHESIS_RUN_ID,
        "run_identity_mismatch",
        "synthesis.synthesis_run_id",
        "unexpected regenerated identity",
    )
    regenerated = output_root / SYNTHESIS_RUN_ID
    accepted = repository_root / "reports/experiments/runs" / SYNTHESIS_RUN_ID
    comparison = _compare_regenerated_bundle(regenerated, accepted)
    manifest = _load_json(regenerated / "manifest.json")
    return {
        "synthesis_run_id": SYNTHESIS_RUN_ID,
        "normalized_group_count": manifest["normalized_group_count"],
        **comparison,
    }


def _audit_public_artifacts(repository_root: Path) -> dict[str, Any]:
    run_root = repository_root / "reports/experiments/runs"
    run_ids = (
        CANONICAL_RUN_ID,
        DETERMINISTIC_RUN_ID,
        STOCHASTIC_RUN_ID,
        HISTORICAL_VALIDATION_RUN_ID,
        HISTORICAL_RUN_ID,
        ROBUSTNESS_RUN_ID,
        SYNTHESIS_RUN_ID,
    )
    audits = {
        run_id: _verify_manifest_artifacts(run_root / run_id) for run_id in run_ids
    }
    return {
        "status": "passed",
        "accepted_run_count": len(audits),
        "runs": audits,
        "checked_artifact_count": sum(
            item["checked_artifact_count"] for item in audits.values()
        ),
        "private_receipt_artifact_count": sum(
            item["private_receipt_artifact_count"] for item in audits.values()
        ),
    }


def _audit_provenance(repository_root: Path) -> dict[str, Any]:
    run_root = repository_root / "reports/experiments/runs"
    manifests = {
        run_id: _load_json(run_root / run_id / "manifest.json")
        for run_id in (
            CANONICAL_RUN_ID,
            DETERMINISTIC_RUN_ID,
            STOCHASTIC_RUN_ID,
            HISTORICAL_VALIDATION_RUN_ID,
            HISTORICAL_RUN_ID,
            ROBUSTNESS_RUN_ID,
            SYNTHESIS_RUN_ID,
        )
    }
    code_bindings = (
        (
            repository_root / "reproducibility/empirical.py",
            manifests[CANONICAL_RUN_ID]["runner_sha256"],
        ),
        (
            repository_root / "reproducibility/deterministic_study.py",
            manifests[DETERMINISTIC_RUN_ID]["generator_sha256"],
        ),
        (
            repository_root / "reproducibility/empirical.py",
            manifests[DETERMINISTIC_RUN_ID]["runner_sha256"],
        ),
        (
            repository_root / "reproducibility/stochastic_study.py",
            manifests[STOCHASTIC_RUN_ID]["generator_sha256"],
        ),
        (
            repository_root / "reproducibility/empirical.py",
            manifests[STOCHASTIC_RUN_ID]["runner_sha256"],
        ),
        (
            repository_root / "reproducibility/historical_study.py",
            manifests[HISTORICAL_RUN_ID]["study_sha256"],
        ),
        (
            repository_root / "reproducibility/empirical.py",
            manifests[HISTORICAL_RUN_ID]["runner_sha256"],
        ),
        (
            repository_root / "reproducibility/historical_robustness.py",
            manifests[ROBUSTNESS_RUN_ID]["source_sha256"],
        ),
        (
            repository_root / "reproducibility/empirical.py",
            manifests[ROBUSTNESS_RUN_ID]["runner_sha256"],
        ),
        (
            repository_root / "reproducibility/safety_adaptivity_synthesis.py",
            manifests[SYNTHESIS_RUN_ID]["source_sha256"],
        ),
    )
    for path, expected in code_bindings:
        _require(
            _sha256(path.read_bytes()) == expected,
            "code_version_mismatch",
            str(path),
            "source differs from accepted manifest",
        )

    protocol_v1 = repository_root / "experiments/protocols/safety-adaptivity-v1.json"
    protocol_v2 = (
        repository_root / "experiments/protocols/safety-adaptivity-yahoo-v2.json"
    )
    deterministic_input = (
        repository_root / "experiments/inputs/deterministic-adversarial-v1.json"
    )
    stochastic_input = (
        repository_root / "experiments/inputs/seeded-stochastic-families-v1.json"
    )
    _require(
        _sha256(protocol_v1.read_bytes())
        == manifests[DETERMINISTIC_RUN_ID]["protocol_sha256"]
        == manifests[STOCHASTIC_RUN_ID]["protocol_sha256"],
        "protocol_fingerprint_mismatch",
        str(protocol_v1),
        "synthetic manifests do not bind the exact protocol",
    )
    _require(
        _sha256(deterministic_input.read_bytes())
        == manifests[DETERMINISTIC_RUN_ID]["study_spec_sha256"]
        and _sha256(stochastic_input.read_bytes())
        == manifests[STOCHASTIC_RUN_ID]["study_spec_sha256"],
        "study_fingerprint_mismatch",
        "experiments/inputs",
        "saved design differs from accepted manifest",
    )
    _require(
        _sha256(protocol_v2.read_bytes())
        == manifests[HISTORICAL_RUN_ID]["config_sha256"]
        == manifests[ROBUSTNESS_RUN_ID]["protocol_sha256"],
        "protocol_fingerprint_mismatch",
        str(protocol_v2),
        "historical manifests do not bind the exact protocol",
    )

    source_receipt_path = (
        repository_root / "experiments/inputs/historical-yahoo-receipts-v2.json"
    )
    source_receipt = _load_json(source_receipt_path)
    requirements = repository_root / "requirements-historical.txt"
    requirement_sha = _sha256(requirements.read_bytes())
    pinned_dependencies = {
        line.split("==", 1)[0]: line.split("==", 1)[1]
        for line in requirements.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }
    _require(
        source_receipt["protocol_sha256"] == _sha256(protocol_v2.read_bytes())
        and len(source_receipt["sources"]) == 2,
        "source_receipt_mismatch",
        str(source_receipt_path),
        "receipt does not bind the historical protocol and two sources",
    )
    expected_sources = {
        "spy-adjusted-daily": ("SPY", "America/New_York", "adjusted_close"),
        "btc-usd-daily": ("BTC-USD", "UTC", "close_usd"),
    }
    protocol_sources = {
        row["dataset_id"]: row for row in _load_json(protocol_v2)["historical_datasets"]
    }
    for source in source_receipt["sources"]:
        dataset_id = source["dataset_id"]
        symbol, timezone, price_field = expected_sources[dataset_id]
        metadata = source["adapter_metadata"]
        protocol_source = protocol_sources[dataset_id]
        _require(
            source["request_receipt"]["provider"] == "Yahoo Finance"
            and source["adapter"] == "yfinance-history"
            and metadata["adapter_version"] == "1.7.0"
            and metadata["client_versions"]["yfinance"] == "1.7.0"
            and metadata["dependency_lock_sha256"] == requirement_sha
            and metadata["source_timezone"] == timezone
            and source["request_receipt"]["request_parameters_without_credentials"][
                "symbol"
            ]
            == symbol
            and protocol_source["price_field"] == price_field
            and protocol_source["timezone"] == timezone
            and protocol_source["currency"] == "USD"
            and "access-controlled-outside-git"
            in source["redistribution_decision"],
            "source_semantics_mismatch",
            dataset_id,
            "provider, client, series, dependency, or retention semantics differ",
        )
        for dependency, version in metadata["client_versions"].items():
            _require(
                pinned_dependencies.get(dependency) == version,
                "dependency_version_mismatch",
                dependency,
                "source receipt differs from acquisition lock",
            )

    provider_review = (
        repository_root / "research/notes/yahoo-finance-historical-data-provider-review.md"
    ).read_text(encoding="utf-8")
    for required_text in (
        "## Dependency and redistribution decision",
        "Apache license covers `yfinance` code, not Yahoo-supplied data",
        "https://help.yahoo.com/kb/finance/SLN2310.html",
        "## Authorized runtime receipt",
    ):
        _require(
            required_text in provider_review,
            "provider_review_incomplete",
            "yahoo-finance-historical-data-provider-review.md",
            f"missing {required_text!r}",
        )

    deterministic = manifests[DETERMINISTIC_RUN_ID]
    stochastic = manifests[STOCHASTIC_RUN_ID]
    historical = manifests[HISTORICAL_RUN_ID]
    robustness = manifests[ROBUSTNESS_RUN_ID]
    synthesis = manifests[SYNTHESIS_RUN_ID]
    _require(
        (deterministic["attempted_path_count"], deterministic["generated_path_count"], deterministic["excluded_path_count"])
        == (21, 18, 3)
        and (stochastic["attempted_path_count"], stochastic["generated_path_count"], stochastic["excluded_path_count"])
        == (90, 90, 0)
        and (historical["attempted_episode_count"], historical["included_episode_count"])
        == (1365, 1365),
        "exclusion_reconciliation_mismatch",
        "accepted manifests",
        "declared, included, and excluded counts differ",
    )
    _require(
        stochastic["seeds"] == [104729, 130363, 155921]
        and deterministic["seed"] is None,
        "seed_mismatch",
        "synthetic manifests",
        "declared seeds differ",
    )
    _require(
        synthesis["reviewed_source_run_ids"]
        == [
            DETERMINISTIC_RUN_ID,
            STOCHASTIC_RUN_ID,
            HISTORICAL_RUN_ID,
            ROBUSTNESS_RUN_ID,
        ],
        "artifact_join_mismatch",
        "synthesis.reviewed_source_run_ids",
        "synthesis does not join the four accepted sources",
    )
    canonical = manifests[CANONICAL_RUN_ID]
    preparation_manifest = _load_json(
        repository_root
        / "experiments/inputs/historical-yahoo-preparation-manifest-v5.json"
    )
    execution_plan = (
        repository_root
        / "experiments/inputs/historical-yahoo-registered-robustness-v1.json"
    )
    synthesis_specification = (
        repository_root / "experiments/inputs/safety-adaptivity-synthesis-v1.json"
    )
    _require(
        canonical["config"]["sha256"] == _sha256(protocol_v1.read_bytes())
        and canonical["inputs"][0]["sha256"]
        == _sha256(
            (
                repository_root / "experiments/inputs/canonical-synthetic-v1.json"
            ).read_bytes()
        )
        and historical["accepted_preparation_manifest_sha256"]
        == _sha256(
            (
                repository_root
                / "experiments/inputs/historical-yahoo-preparation-manifest-v5.json"
            ).read_bytes()
        )
        and historical["runner_input_sha256"]
        == preparation_manifest["runner_input_sha256"]
        and robustness["execution_plan_sha256"]
        == _sha256(execution_plan.read_bytes())
        and synthesis["specification_sha256"]
        == _sha256(synthesis_specification.read_bytes()),
        "run_identity_input_mismatch",
        "accepted manifests",
        "a run-identity input differs from its retained source",
    )
    reconstructed_run_ids = {
        CANONICAL_RUN_ID: _content_addressed_id(
            "smartdca-run-v1-",
            {
                "engine_version": canonical["engine_version"],
                "runner_sha256": canonical["runner_sha256"],
                "config_sha256": canonical["config"]["sha256"],
                "input_sha256": canonical["inputs"][0]["sha256"],
            },
        ),
        DETERMINISTIC_RUN_ID: _content_addressed_id(
            "smartdca-deterministic-v1-",
            {
                "engine_version": deterministic["engine_version"],
                "generator_sha256": deterministic["generator_sha256"],
                "runner_sha256": deterministic["runner_sha256"],
                "protocol_sha256": deterministic["protocol_sha256"],
                "study_sha256": deterministic["study_spec_sha256"],
                "runner_input_sha256": deterministic["runner_input_sha256"],
                "adversarial_search_input_sha256": deterministic[
                    "adversarial_design_search"
                ]["search_input_sha256"],
            },
        ),
        STOCHASTIC_RUN_ID: _content_addressed_id(
            "smartdca-stochastic-v1-",
            {
                "engine_version": stochastic["engine_version"],
                "generator_sha256": stochastic["generator_sha256"],
                "runner_sha256": stochastic["runner_sha256"],
                "protocol_sha256": stochastic["protocol_sha256"],
                "study_sha256": stochastic["study_spec_sha256"],
                "runner_input_sha256": stochastic["runner_input_sha256"],
                "runtime": {
                    "implementation": "CPython",
                    "python_major_minor": (
                        f"{sys.version_info.major}.{sys.version_info.minor}"
                    ),
                },
            },
        ),
        HISTORICAL_RUN_ID: _content_addressed_id(
            "smartdca-historical-study-v1-",
            {
                "engine_version": historical["engine_version"],
                "study_sha256": historical["study_sha256"],
                "runner_engine_version": historical["runner_engine_version"],
                "runner_sha256": historical["runner_sha256"],
                "config_sha256": historical["config_sha256"],
                "accepted_preparation_manifest_sha256": historical[
                    "accepted_preparation_manifest_sha256"
                ],
                "runner_input_sha256": historical["runner_input_sha256"],
            },
        ),
        ROBUSTNESS_RUN_ID: _content_addressed_id(
            "smartdca-historical-robustness-v1-",
            {
                "engine_version": robustness["engine_version"],
                "source_sha256": robustness["source_sha256"],
                "confirmatory_study_sha256": robustness[
                    "confirmatory_study_sha256"
                ],
                "runner_sha256": robustness["runner_sha256"],
                "protocol_sha256": robustness["protocol_sha256"],
                "execution_plan_sha256": robustness["execution_plan_sha256"],
                "accepted_preparation_manifest_sha256": robustness[
                    "accepted_preparation_manifest_sha256"
                ],
                "monthly_config_sha256": robustness["slices"]["monthly"][
                    "config_sha256"
                ],
                "monthly_input_sha256": robustness["slices"]["monthly"][
                    "input_sha256"
                ],
                "quarterly_config_sha256": robustness["slices"]["quarterly"][
                    "config_sha256"
                ],
                "quarterly_input_sha256": robustness["slices"]["quarterly"][
                    "input_sha256"
                ],
            },
        ),
        SYNTHESIS_RUN_ID: _content_addressed_id(
            "smartdca-synthesis-v1-",
            {
                "engine_version": synthesis["engine_version"],
                "runtime": {
                    "implementation": "CPython",
                    "python": f"{sys.version_info.major}.{sys.version_info.minor}",
                },
                "source_sha256": synthesis["source_sha256"],
                "specification_sha256": synthesis["specification_sha256"],
            },
        ),
    }
    for published, reconstructed in reconstructed_run_ids.items():
        _require(
            published == reconstructed,
            "run_identity_reconstruction_mismatch",
            published,
            f"reconstructed {reconstructed}",
        )
    _require(
        sys.implementation.name == "cpython" and sys.version_info[:2] == (3, 12),
        "unsupported_runtime",
        "python",
        "publication review requires CPython 3.12",
    )
    return {
        "status": "passed",
        "accepted_run_count": len(manifests),
        "code_binding_count": len(code_bindings),
        "source_receipt_count": len(source_receipt["sources"]),
        "pinned_dependency_count": len(pinned_dependencies),
        "reconstructed_run_identity_count": len(reconstructed_run_ids),
        "reconstructed_run_ids": sorted(reconstructed_run_ids),
        "deterministic_seed": None,
        "stochastic_seeds": stochastic["seeds"],
        "historical_bootstrap_seed": _load_json(protocol_v2)["uncertainty"]["seed"],
        "provider": "Yahoo Finance",
        "client": "yfinance 1.7.0",
        "redistribution": "private retained inputs; sanitized receipts and derived aggregates in Git",
    }


def _audit_claims(repository_root: Path) -> dict[str, Any]:
    run_root = repository_root / "reports/experiments/runs"
    historical_groups = _load_json(
        run_root / HISTORICAL_RUN_ID / "historical-aggregates.json"
    )["groups"]
    uncertainty = _load_json(run_root / HISTORICAL_RUN_ID / "uncertainty.json")
    h1 = [
        row
        for row in historical_groups
        if row["analysis_tier"] == "confirmatory"
        and row["comparison"] == "corrected_guarded_vs_dca"
    ]
    h2 = [
        row
        for row in historical_groups
        if row["analysis_tier"] == "confirmatory"
        and row["comparison"] == "corrected_guarded_vs_neutral_guarded"
    ]
    architecture = [
        row
        for row in historical_groups
        if row["analysis_tier"] == "secondary"
        and row["cost_scenario"] == "frictionless"
        and row["coverage"] != "1"
        and row["comparison"] == "neutral_guarded_vs_dca"
    ]
    _require(
        len(h1) == len(h2) == len(architecture) == 18
        and all(_decimal(row["median_relative_terminal_wealth_gap"], "h1") < ZERO for row in h1)
        and sum(_decimal(row["median_relative_terminal_wealth_gap"], "h2") < ZERO for row in h2) == 17
        and sum(_decimal(row["median_relative_terminal_wealth_gap"], "h2") > ZERO for row in h2) == 1
        and all(_decimal(row["median_relative_terminal_wealth_gap"], "architecture") < ZERO for row in architecture),
        "historical_claim_mismatch",
        "historical-aggregates.json",
        "primary or secondary sign counts differ",
    )
    h1_significant = sum(
        _decimal(row["holm_adjusted_p_value"], "holm") < Decimal("0.05")
        for row in uncertainty["cells"]
        if row["hypothesis_id"] == "H1-complete-system"
    )
    h2_significant = sum(
        _decimal(row["holm_adjusted_p_value"], "holm") < Decimal("0.05")
        for row in uncertainty["cells"]
        if row["hypothesis_id"] == "H2-signal-contribution"
    )
    _require(
        uncertainty["cell_count"] == 36
        and h1_significant == 9
        and h2_significant == 0,
        "multiplicity_claim_mismatch",
        "uncertainty.json",
        "Holm family or rejection counts differ",
    )

    robustness_groups = _load_json(
        run_root / ROBUSTNESS_RUN_ID / "robustness-aggregates.json"
    )["groups"]

    def robustness_slice(schedule: str, comparison: str) -> list[dict[str, Any]]:
        return [
            row
            for row in robustness_groups
            if row["schedule_id"] == schedule
            and row["cost_scenario"] == "frictionless"
            and row["coverage"] != "1"
            and row["comparison"] == comparison
        ]

    monthly_complete = robustness_slice(
        "primary-monthly-robustness-coverage", "corrected_guarded_vs_dca"
    )
    monthly_signal = robustness_slice(
        "primary-monthly-robustness-coverage",
        "corrected_guarded_vs_neutral_guarded",
    )
    quarterly_complete = robustness_slice(
        "robustness-quarterly-horizons", "corrected_guarded_vs_dca"
    )
    quarterly_signal = robustness_slice(
        "robustness-quarterly-horizons",
        "corrected_guarded_vs_neutral_guarded",
    )
    _require(
        len(monthly_complete) == len(monthly_signal) == 30
        and len(quarterly_complete) == len(quarterly_signal) == 48
        and all(_decimal(row["median_relative_terminal_wealth_gap"], "monthly") < ZERO for row in monthly_complete + monthly_signal)
        and all(_decimal(row["median_relative_terminal_wealth_gap"], "quarterly") < ZERO for row in quarterly_complete)
        and sum(_decimal(row["median_relative_terminal_wealth_gap"], "quarterly signal") < ZERO for row in quarterly_signal) == 40
        and sum(_decimal(row["median_relative_terminal_wealth_gap"], "quarterly signal") > ZERO for row in quarterly_signal) == 8
        and all(row["analysis_tier"] in {"robustness", "secondary"} for row in robustness_groups),
        "robustness_claim_mismatch",
        "robustness-aggregates.json",
        "descriptive coverage, horizon, or sign counts differ",
    )

    normalized_path = run_root / SYNTHESIS_RUN_ID / "normalized-evidence.csv"
    with normalized_path.open(newline="", encoding="utf-8") as handle:
        normalized = list(csv.DictReader(handle))
    lambda_one = [row for row in normalized if row["coverage"] == "1"]
    frictionless_dca = [
        row
        for row in normalized
        if row["cost_scenario"] == "frictionless"
        and row["comparison"]
        in {"corrected_guarded_vs_dca", "neutral_guarded_vs_dca"}
    ]
    _require(
        len(normalized) == 2754
        and len(lambda_one) == 594
        and all(_decimal(row["median_relative_terminal_wealth_gap"], "lambda=1") == ZERO for row in lambda_one)
        and len(frictionless_dca) == 612
        and all(
            _decimal(row["minimum_relative_terminal_wealth_gap"], "minimum gap")
            >= _decimal(row["coverage"], "coverage") - ONE
            for row in frictionless_dca
        ),
        "synthesis_claim_mismatch",
        "normalized-evidence.csv",
        "cell count, collapse, or frictionless floor differs",
    )
    _require(
        all(
            row["theorem_scope"] == "outside-current-safety-theorem"
            for row in normalized
            if row["cost_scenario"] != "frictionless"
        ),
        "cost_scope_mismatch",
        "normalized-evidence.csv",
        "net-of-cost rows inherited theorem scope",
    )
    return {
        "status": "passed",
        "normalized_cell_count": len(normalized),
        "lambda_one_cell_count": len(lambda_one),
        "frictionless_floor_cell_count": len(frictionless_dca),
        "historical_primary_cell_count": len(h1),
        "h1_significant_cell_count": h1_significant,
        "h2_significant_cell_count": h2_significant,
        "holm_family_size": uncertainty["cell_count"],
        "monthly_robustness_cell_count_per_comparison": len(monthly_complete),
        "quarterly_robustness_cell_count_per_comparison": len(quarterly_complete),
    }


def _audit_publication_state(repository_root: Path) -> dict[str, Any]:
    reports = (
        "canonical-synthetic-run.md",
        "deterministic-adversarial-paths.md",
        "seeded-stochastic-families.md",
        "historical-data-episode-seam.md",
        "confirmatory-historical-evaluation.md",
        "safety-adaptivity-tradeoff-synthesis.md",
    )
    review_link = "../../research/notes/safety-adaptivity-empirical-package-review.md"
    stale_phrases = (
        "Later tickets must create",
        "remain separate open tickets",
        "Ticket 05 may consume",
        "not publication of the final empirical package",
        "not the final publication package",
        "ticket 07 remains",
    )
    for report_name in reports:
        report = (
            repository_root / "reports/experiments" / report_name
        ).read_text(encoding="utf-8")
        _require(
            "Publication status: **publication-ready**" in report
            and review_link in report
            and not any(phrase in report for phrase in stale_phrases),
            "publication_state_mismatch",
            report_name,
            "missing final review link/status or retaining stale ticket state",
        )
    review_note = (
        repository_root
        / "research/notes/safety-adaptivity-empirical-package-review.md"
    )
    _require(
        review_note.is_file(),
        "missing_review_note",
        str(review_note),
        "independent publication review is absent",
    )
    note = review_note.read_text(encoding="utf-8")
    for required in (
        "## Verdict",
        "## Independent reproduction",
        "## Provenance, dependencies, and retention",
        "## Accounting and statistical audit",
        "## Claim and writing audit",
        "## Publication conclusion",
        "Result: **pass**",
    ):
        _require(
            required in note,
            "incomplete_review_note",
            str(review_note),
            f"missing {required!r}",
        )
    ticket_path = (
        repository_root
        / ".scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/issues/07-review-publish-empirical-package.md"
    )
    effort_map_path = (
        repository_root
        / ".scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/map.md"
    )
    project_map_path = repository_root / ".scratch/smartdca/map.md"
    ticket = ticket_path.read_text(encoding="utf-8")
    checked_criteria = ticket.count("- [x]")
    _require(
        "Status: resolved" in ticket
        and checked_criteria == 10
        and "- [ ]" not in ticket
        and "## Answer\n\n_Not yet resolved._" not in ticket,
        "publication_tracker_state_mismatch",
        str(ticket_path),
        "ticket must be resolved with all ten acceptance criteria and an answer",
    )
    effort_map = effort_map_path.read_text(encoding="utf-8")
    _require(
        "[07](issues/07-review-publish-empirical-package.md) | Independently reproduce, review, and publish the empirical package. | resolved | 06 |"
        in effort_map
        and "All seven tickets are resolved" in effort_map
        and "The empirical evaluation effort is complete" in effort_map,
        "publication_tracker_state_mismatch",
        str(effort_map_path),
        "ticket row and completed effort frontier must agree",
    )
    project_map = project_map_path.read_text(encoding="utf-8")
    _require(
        "[Safety-adaptivity empirical evaluation](efforts/safety-adaptivity-empirical-evaluation/spec.md) | completed |"
        in project_map
        and "Manuscript assembly is now the project frontier" in project_map,
        "publication_tracker_state_mismatch",
        str(project_map_path),
        "effort state and manuscript-assembly frontier must agree",
    )
    return {
        "status": "passed",
        "publication_ready_report_count": len(reports),
        "review_note": review_note.relative_to(repository_root).as_posix(),
        "resolved_acceptance_criterion_count": checked_criteria,
        "effort_state": "completed",
        "project_frontier": "manuscript-assembly",
    }


def _audit_retained_private_review(repository_root: Path) -> dict[str, Any]:
    registry_path = repository_root / RETAINED_REVIEW_REGISTRY
    if not registry_path.is_file():
        return {
            "status": "not-retained",
            "registry": RETAINED_REVIEW_REGISTRY.as_posix(),
        }
    registry = _load_json(registry_path)
    relative_path = Path(str(registry.get("path", "")))
    review_id = registry.get("review_id")
    _require(
        registry.get("schema_version")
        == "smartdca-empirical-package-review-registry/1"
        and isinstance(review_id, str)
        and review_id.startswith("smartdca-empirical-package-review-v1-")
        and not relative_path.is_absolute()
        and ".." not in relative_path.parts
        and relative_path
        == Path("reports/experiments/runs") / str(review_id),
        "invalid_retained_review_registry",
        str(registry_path),
        "schema, review identity, or repository-relative bundle path differs",
    )
    manifest_path = repository_root / relative_path / "manifest.json"
    _require(
        manifest_path.is_file()
        and _sha256(manifest_path.read_bytes()) == registry.get("manifest_sha256"),
        "retained_review_manifest_fingerprint_mismatch",
        str(manifest_path),
        "manifest is absent or differs from the registered SHA-256",
    )
    manifest = _load_json(manifest_path)
    expected_manifest_keys = {
        "accepted_run_manifests",
        "artifacts",
        "checkpoint_sha256",
        "review_id",
        "review_module_sha256",
        "runtime",
        "schema_version",
    }
    _require(
        set(manifest) == expected_manifest_keys
        and manifest["schema_version"]
        == "smartdca-empirical-package-review-manifest/1"
        and manifest["review_id"] == review_id,
        "invalid_retained_review_manifest",
        str(manifest_path),
        "schema, fields, or review identity differs",
    )
    identity = {key: value for key, value in manifest.items() if key != "review_id"}
    _require(
        review_id
        == _content_addressed_id("smartdca-empirical-package-review-v1-", identity),
        "retained_review_identity_mismatch",
        str(manifest_path),
        "review ID does not address the canonical manifest identity",
    )
    checkpoint_path = (
        repository_root
        / "reproducibility/checks/check_empirical_package_publication_review.py"
    )
    _require(
        manifest["review_module_sha256"]
        == _sha256(Path(__file__).read_bytes())
        and manifest["checkpoint_sha256"] == _sha256(checkpoint_path.read_bytes())
        and manifest["runtime"]
        == {"implementation": "CPython", "python": "3.12", "third_party": []},
        "retained_review_code_binding_mismatch",
        str(manifest_path),
        "review source, checkpoint, or runtime binding differs",
    )
    accepted_run_ids = (
        CANONICAL_RUN_ID,
        DETERMINISTIC_RUN_ID,
        STOCHASTIC_RUN_ID,
        HISTORICAL_VALIDATION_RUN_ID,
        HISTORICAL_RUN_ID,
        ROBUSTNESS_RUN_ID,
        SYNTHESIS_RUN_ID,
    )
    expected_run_manifests = [
        {
            "run_id": run_id,
            "sha256": _sha256(
                (
                    repository_root
                    / "reports/experiments/runs"
                    / run_id
                    / "manifest.json"
                ).read_bytes()
            ),
        }
        for run_id in sorted(accepted_run_ids)
    ]
    _require(
        manifest["accepted_run_manifests"] == expected_run_manifests,
        "retained_review_source_binding_mismatch",
        str(manifest_path),
        "accepted run manifests differ from the private-pass binding",
    )
    artifacts = manifest["artifacts"]
    _require(
        isinstance(artifacts, list)
        and len(artifacts) == 2
        and {artifact.get("path") for artifact in artifacts}
        == {"review-receipt.json", "failure-records.jsonl"},
        "invalid_retained_review_artifacts",
        str(manifest_path),
        "must retain exactly the sanitized receipt and failure ledger",
    )
    artifact_by_path = {artifact["path"]: artifact for artifact in artifacts}
    for artifact_name, artifact in artifact_by_path.items():
        artifact_path = manifest_path.parent / artifact_name
        payload = artifact_path.read_bytes() if artifact_path.is_file() else None
        _require(
            payload is not None
            and artifact.get("bytes") == len(payload)
            and artifact.get("sha256") == _sha256(payload)
            and artifact.get("retention") == "public-sanitized",
            "retained_review_artifact_fingerprint_mismatch",
            str(artifact_path),
            "size, SHA-256, or retention class differs from the manifest",
        )
    failure_payload = (manifest_path.parent / "failure-records.jsonl").read_bytes()
    _require(
        failure_payload == b"",
        "retained_review_failure_ledger_mismatch",
        str(manifest_path.parent / "failure-records.jsonl"),
        "successful private review must retain a zero-record failure ledger",
    )
    receipt_path = manifest_path.parent / "review-receipt.json"
    receipt = _load_json(receipt_path)
    historical = receipt.get("historical_slice_review", {})
    robustness = receipt.get("historical_robustness_review", {})
    _require(
        receipt.get("schema_version")
        == "smartdca-empirical-package-publication-review/1"
        and receipt.get("status") == "passed"
        and receipt.get("review_basis") == "live-private-inputs"
        and receipt.get("failure_record_count") == 0
        and historical.get("status") == "passed"
        and historical.get("private_values_published") is False
        and historical.get("full_calendar_episode_match_count") == 1365
        and robustness.get("status") == "passed"
        and robustness.get("private_values_published") is False
        and robustness.get("private_artifact_match_count") == 21
        and robustness.get("raw_aggregate_match_count") == 810
        and receipt.get("provenance_audit", {}).get(
            "reconstructed_run_identity_count"
        )
        == 6
        and receipt.get("publication_state_audit", {}).get("status") == "passed",
        "retained_private_review_not_publication_clearing",
        str(receipt_path),
        "receipt does not record a complete, sanitized private pass",
    )
    review_note_path = (
        repository_root
        / "research/notes/safety-adaptivity-empirical-package-review.md"
    )
    review_note = review_note_path.read_text(encoding="utf-8")
    ticket = (
        repository_root
        / ".scratch/smartdca/efforts/safety-adaptivity-empirical-evaluation/issues/07-review-publish-empirical-package.md"
    ).read_text(encoding="utf-8")
    _require(
        "<CHECK_SHA256>" not in review_note
        and "<REVIEW_RECEIPT_SHA256>" not in review_note
        and manifest["checkpoint_sha256"] in review_note
        and artifact_by_path["review-receipt.json"]["sha256"] in review_note
        and review_id in review_note
        and review_id in ticket,
        "retained_review_publication_link_mismatch",
        str(review_note_path),
        "note and ticket must identify the retained review and exact evidence hashes",
    )
    return {
        "status": "passed",
        "review_id": review_id,
        "bundle": relative_path.as_posix(),
        "manifest_sha256": registry["manifest_sha256"],
        "review_receipt_sha256": artifact_by_path["review-receipt.json"]["sha256"],
        "failure_record_count": 0,
        "historical_calendar_episode_match_count": historical[
            "full_calendar_episode_match_count"
        ],
        "historical_slice_comparison_count": historical["comparison_count"],
        "robustness_raw_aggregate_match_count": robustness[
            "raw_aggregate_match_count"
        ],
    }


def _write_json(path: Path, value: object) -> None:
    path.write_text(_canonical_json(value) + "\n", encoding="utf-8", newline="\n")


def run_publication_review(
    repository_root: Path,
    output_root: Path,
    *,
    private_preparation_directory: Path | None = None,
    private_historical_run_directory: Path | None = None,
    private_robustness_run_directory: Path | None = None,
) -> dict[str, Any]:
    """Regenerate and independently audit the accepted empirical package."""

    repository_root = repository_root.resolve()
    output_root = output_root.resolve()
    _require(
        repository_root.is_dir(),
        "missing_repository_root",
        "repository_root",
        "directory is absent",
    )
    _require(
        not output_root.exists(),
        "output_root_exists",
        "output_root",
        "must be a new path",
    )
    output_root.mkdir(parents=True)
    failure_path = output_root / "failure-records.jsonl"
    failure_path.touch()
    try:
        private_paths = (
            private_preparation_directory,
            private_historical_run_directory,
            private_robustness_run_directory,
        )
        _require(
            all(path is None for path in private_paths)
            or all(path is not None for path in private_paths),
            "incomplete_private_review_paths",
            "private_inputs",
            "supply all three private paths or none",
        )
        live_private_inputs_supplied = all(path is not None for path in private_paths)
        historical_review = (
            _private_historical_slice_review(
                repository_root,
                private_preparation_directory.resolve(),
                private_historical_run_directory.resolve(),
            )
            if private_preparation_directory is not None
            and private_historical_run_directory is not None
            else {"status": "not-run-private-inputs-not-supplied"}
        )
        robustness_review = (
            _review_private_robustness(
                repository_root,
                private_robustness_run_directory.resolve(),
            )
            if private_robustness_run_directory is not None
            else {"status": "not-run-private-inputs-not-supplied"}
        )
        retained_private_review = (
            {"status": "not-required-live-private-review"}
            if live_private_inputs_supplied
            else _audit_retained_private_review(repository_root)
        )
        live_private_review_passed = (
            historical_review["status"] == "passed"
            and robustness_review["status"] == "passed"
        )
        retained_private_review_passed = retained_private_review["status"] == "passed"
        receipt = {
            "schema_version": "smartdca-empirical-package-publication-review/1",
            "status": (
                "passed"
                if live_private_review_passed or retained_private_review_passed
                else "not-cleared-private-review-not-retained"
            ),
            "review_basis": (
                "live-private-inputs"
                if live_private_review_passed
                else (
                    "retained-private-review-receipt"
                    if retained_private_review_passed
                    else "public-only-unreviewed-private-evidence"
                )
            ),
            "public_artifact_audit": _audit_public_artifacts(repository_root),
            "provenance_audit": _audit_provenance(repository_root),
            "claim_audit": _audit_claims(repository_root),
            "publication_state_audit": _audit_publication_state(repository_root),
            "deterministic_reproduction": _reproduce_deterministic(
                repository_root, output_root / "deterministic-reproduction"
            ),
            "deterministic_independent_replay": _independent_deterministic_replay(
                repository_root
            ),
            "synthesis_reproduction": _reproduce_synthesis(
                repository_root, output_root / "synthesis-reproduction"
            ),
            "historical_slice_review": historical_review,
            "historical_robustness_review": robustness_review,
            "retained_private_review": retained_private_review,
            "failure_record_count": 0,
        }
        _write_json(output_root / "review-receipt.json", receipt)
        return receipt
    except BaseException as error:
        failure = {
            "status": "failed",
            "code": getattr(error, "code", type(error).__name__),
            "field": getattr(error, "field", None),
            "message": str(error),
        }
        failure_path.write_text(
            _canonical_json(failure) + "\n", encoding="utf-8", newline="\n"
        )
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reproduce and independently review the SmartDCA empirical package."
    )
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--private-preparation-directory", type=Path)
    parser.add_argument("--private-historical-run-directory", type=Path)
    parser.add_argument("--private-robustness-run-directory", type=Path)
    arguments = parser.parse_args(argv)
    try:
        receipt = run_publication_review(
            arguments.repository_root,
            arguments.output_root,
            private_preparation_directory=arguments.private_preparation_directory,
            private_historical_run_directory=arguments.private_historical_run_directory,
            private_robustness_run_directory=arguments.private_robustness_run_directory,
        )
    except PublicationReviewError as error:
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
    print(_canonical_json(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
