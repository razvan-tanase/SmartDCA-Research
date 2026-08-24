"""Deterministic exact search for guarded cash-path sign reversals."""

import json
from dataclasses import dataclass
from fractions import Fraction
from typing import Literal, TypeAlias

from reproducibility.arbitrary_horizon import (
    ExactRationalError,
    RationalScenario,
    ScenarioLedger,
    evaluate_scenario,
)
from reproducibility.cash_single_crossing import (
    CashMechanismReport,
    analyze_cash_mechanism,
)
from reproducibility.weak_single_valley_search import (
    SearchGrid,
    describe_valley,
    enumerate_weak_single_valley_paths,
)


ZERO = Fraction(0)
ONE = Fraction(1)


DEFAULT_CASH_CROSSING_GRID = SearchGrid(
    horizons=(4,),
    price_levels=(
        Fraction(1, 16),
        Fraction(1, 8),
        Fraction(1, 4),
        Fraction(1, 2),
        Fraction(2, 3),
        ONE,
        Fraction(3, 2),
        Fraction(2),
        Fraction(4),
        Fraction(8),
        Fraction(16),
        Fraction(32),
    ),
    initial_price=ONE,
    evaluation_multipliers=(ONE,),
    safety_factors=(
        Fraction(1, 2),
        Fraction(1, 4),
        Fraction(3, 4),
        Fraction(7, 8),
        Fraction(15, 16),
        Fraction(31, 32),
        Fraction(63, 64),
    ),
    parameter_pairs=(
        (ZERO, -ONE),
        (ZERO, ONE),
        (-ONE, ZERO),
    ),
    equal_deposit=ONE,
)


CashCrossingWitnessName: TypeAlias = Literal[
    "smallest_multiple_cash_sign_changes",
    "smallest_genuine_cycle_multiple_cash_sign_changes",
    "smallest_strict_cycle_multiple_cash_sign_changes",
]


@dataclass(frozen=True)
class CashCrossingWitness:
    name: CashCrossingWitnessName
    ledger: ScenarioLedger
    report: CashMechanismReport
    unguarded_report: CashMechanismReport


@dataclass(frozen=True)
class CashCrossingSearchResult:
    grid: SearchGrid
    path_count: int
    scenario_count: int
    exact_domain_rejections: int
    multiple_sign_change_count: int
    valley_aligned_single_crossing_failure_count: int
    genuine_cycle_multiple_sign_change_count: int
    strict_cycle_multiple_sign_change_count: int
    reference_aligned_guardrail_count: int
    reference_aligned_guardrail_failures: int
    witnesses: tuple[CashCrossingWitness, ...]

    def witness(self, name: CashCrossingWitnessName) -> CashCrossingWitness:
        try:
            return next(witness for witness in self.witnesses if witness.name == name)
        except StopIteration as error:
            raise ValueError(f"unknown cash-crossing witness: {name}") from error


def _witness_names(
    *, genuine_cycle: bool, strict_cycle: bool
) -> tuple[CashCrossingWitnessName, ...]:
    names: list[CashCrossingWitnessName] = [
        "smallest_multiple_cash_sign_changes"
    ]
    if genuine_cycle:
        names.append("smallest_genuine_cycle_multiple_cash_sign_changes")
    if strict_cycle:
        names.append("smallest_strict_cycle_multiple_cash_sign_changes")
    return tuple(names)


def _rational_complexity_key(value: Fraction) -> tuple[object, ...]:
    """Order rational parameters by height, size, then numeric value."""
    return (
        max(abs(value.numerator), value.denominator),
        abs(value.numerator) + value.denominator,
        value,
    )


def _parameter_pair_complexity_key(
    pair: tuple[Fraction, Fraction],
) -> tuple[object, ...]:
    """Prefer the simplest score exponent, reference gap, and rationals."""
    alpha, beta = pair
    return (
        ONE - alpha,
        abs(alpha - beta),
        _rational_complexity_key(alpha),
        _rational_complexity_key(beta),
        alpha,
        beta,
    )


def _ordered_safety_factors(grid: SearchGrid) -> tuple[Fraction, ...]:
    return tuple(sorted(grid.safety_factors, key=_rational_complexity_key))


def _ordered_parameter_pairs(
    grid: SearchGrid,
) -> tuple[tuple[Fraction, Fraction], ...]:
    return tuple(
        sorted(grid.parameter_pairs, key=_parameter_pair_complexity_key)
    )


def run_cash_crossing_search(grid: SearchGrid) -> CashCrossingSearchResult:
    """Search the declared rational grid through the public ledger seam."""
    paths = tuple(
        path
        for horizon in grid.horizons
        for path in enumerate_weak_single_valley_paths(grid, horizon)
    )
    scenario_count = 0
    exact_domain_rejections = 0
    multiple_count = 0
    valley_aligned_failure_count = 0
    genuine_count = 0
    strict_count = 0
    aligned_count = 0
    aligned_failures = 0
    witnesses: dict[CashCrossingWitnessName, CashCrossingWitness] = {}

    for prices in paths:
        shape = describe_valley(prices)
        for safety_factor in _ordered_safety_factors(grid):
            for alpha, beta in _ordered_parameter_pairs(grid):
                scenario = RationalScenario(
                    prices=prices,
                    deposits=(grid.equal_deposit,) * len(prices),
                    evaluation_price=prices[-1],
                    safety_factor=safety_factor,
                    alpha=alpha,
                    beta=beta,
                )
                try:
                    ledger = evaluate_scenario(scenario)
                except ExactRationalError:
                    exact_domain_rejections += 1
                    continue

                scenario_count += 1
                report = analyze_cash_mechanism(ledger)
                if not report.has_cash_single_crossing:
                    valley_aligned_failure_count += 1
                if report.reference_aligned_guardrail_boundary is not None:
                    aligned_count += 1
                    if not report.has_cash_single_crossing:
                        aligned_failures += 1

                if report.has_at_most_one_cash_sign_change:
                    continue

                multiple_count += 1
                genuine_count += shape.genuine_cycle
                strict_count += shape.strict_cycle
                for name in _witness_names(
                    genuine_cycle=shape.genuine_cycle,
                    strict_cycle=shape.strict_cycle,
                ):
                    if name in witnesses:
                        continue
                    unguarded_report = analyze_cash_mechanism(
                        evaluate_scenario(scenario, guardrail_enabled=False)
                    )
                    witnesses[name] = CashCrossingWitness(
                        name=name,
                        ledger=ledger,
                        report=report,
                        unguarded_report=unguarded_report,
                    )

    return CashCrossingSearchResult(
        grid=grid,
        path_count=len(paths),
        scenario_count=scenario_count,
        exact_domain_rejections=exact_domain_rejections,
        multiple_sign_change_count=multiple_count,
        valley_aligned_single_crossing_failure_count=(
            valley_aligned_failure_count
        ),
        genuine_cycle_multiple_sign_change_count=genuine_count,
        strict_cycle_multiple_sign_change_count=strict_count,
        reference_aligned_guardrail_count=aligned_count,
        reference_aligned_guardrail_failures=aligned_failures,
        witnesses=tuple(witnesses.values()),
    )


def _witness_payload(witness: CashCrossingWitness) -> dict[str, object]:
    scenario = witness.ledger.scenario
    return {
        "prices": [str(value) for value in scenario.prices],
        "deposits": [str(value) for value in scenario.deposits],
        "evaluation_price": str(scenario.evaluation_price),
        "safety_factor": str(scenario.safety_factor),
        "alpha": str(scenario.alpha),
        "beta": str(scenario.beta),
        "cash_differences": [
            str(value) for value in witness.report.cash_differences
        ],
        "cash_sign_change_periods": list(
            witness.report.cash_sign_change_periods
        ),
        "floor_differences": [
            str(value) for value in witness.report.floor_differences
        ],
        "reference_crossing_boundary": (
            witness.report.reference_crossing_boundary
        ),
        "reference_aligned_guardrail_boundary": (
            witness.report.reference_aligned_guardrail_boundary
        ),
        "unguarded_cash_differences": [
            str(value) for value in witness.unguarded_report.cash_differences
        ],
        "unguarded_cash_sign_change_periods": list(
            witness.unguarded_report.cash_sign_change_periods
        ),
    }


def result_payload(result: CashCrossingSearchResult) -> dict[str, object]:
    """Return the deterministic search record as JSON-compatible values."""
    return {
        "grid": {
            "horizons": list(result.grid.horizons),
            "price_levels": [str(value) for value in result.grid.price_levels],
            "initial_price": str(result.grid.initial_price),
            "safety_factors": [
                str(value) for value in _ordered_safety_factors(result.grid)
            ],
            "parameter_pairs": [
                {"alpha": str(alpha), "beta": str(beta)}
                for alpha, beta in _ordered_parameter_pairs(result.grid)
            ],
            "equal_deposit": str(result.grid.equal_deposit),
            "evaluation_price_rule": "P = p_n",
        },
        "enumeration_order": [
            "horizon ascending",
            "price complexity: distinct levels, transitions, total variation, tuple",
            "parameter complexity: safety-factor rational height, size, value",
            "parameter complexity: score exponent, reference gap, rational height, size, value",
            "unit equal-deposit normalization",
        ],
        "pruning_rules": [
            "fix the first purchase price at 1",
            "fix every equal positive deposit at 1",
            "retain exactly the independently validated weak single-valley paths",
        ],
        "path_count": result.path_count,
        "scenario_count": result.scenario_count,
        "exact_domain_rejections": result.exact_domain_rejections,
        "multiple_sign_change_count": result.multiple_sign_change_count,
        "valley_aligned_single_crossing_failure_count": (
            result.valley_aligned_single_crossing_failure_count
        ),
        "genuine_cycle_multiple_sign_change_count": (
            result.genuine_cycle_multiple_sign_change_count
        ),
        "strict_cycle_multiple_sign_change_count": (
            result.strict_cycle_multiple_sign_change_count
        ),
        "reference_aligned_guardrail_count": (
            result.reference_aligned_guardrail_count
        ),
        "reference_aligned_guardrail_failures": (
            result.reference_aligned_guardrail_failures
        ),
        "witnesses": {
            witness.name: _witness_payload(witness)
            for witness in result.witnesses
        },
        "scope_limit": (
            "Exact exhaustive coverage of this finite grid is computational "
            "evidence, not proof outside the declared domain."
        ),
    }


def render_json(result: CashCrossingSearchResult) -> str:
    return json.dumps(result_payload(result), indent=2, sort_keys=True)


def main() -> None:
    print(render_json(run_cash_crossing_search(DEFAULT_CASH_CROSSING_GRID)))


if __name__ == "__main__":
    main()
