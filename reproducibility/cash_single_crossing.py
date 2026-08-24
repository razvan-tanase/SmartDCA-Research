"""Exact cash-path diagnostics for corrected versus neutral guarded policies."""

from dataclasses import dataclass
from fractions import Fraction

from reproducibility.arbitrary_horizon import ScenarioLedger
from reproducibility.weak_single_valley_search import describe_valley


ZERO = Fraction(0)
HALF = Fraction(1, 2)


@dataclass(frozen=True)
class CashMechanismStep:
    """Exact one-period decomposition of corrected-minus-neutral cash."""

    period: int
    corrected_retention: Fraction
    neutral_discretionary_cash: Fraction
    floor_difference: Fraction
    cash_difference: Fraction
    carry_component: Fraction
    score_component: Fraction
    floor_component: Fraction

    def __post_init__(self) -> None:
        if self.cash_difference != (
            self.carry_component + self.score_component + self.floor_component
        ):
            raise AssertionError("cash-difference decomposition does not balance")


@dataclass(frozen=True)
class CashMechanismReport:
    """Externally visible cash-crossing facts for one scenario ledger."""

    trough_period: int
    steps: tuple[CashMechanismStep, ...]
    cash_differences: tuple[Fraction, ...]
    cash_sign_change_periods: tuple[int, ...]
    retention_differences: tuple[Fraction, ...]
    floor_differences: tuple[Fraction, ...]
    reference_crossing_boundary: int
    reference_aligned_guardrail_boundary: int | None

    @property
    def has_cash_single_crossing(self) -> bool:
        nonzero_signs = tuple(
            _sign(value) for value in self.cash_differences if value != ZERO
        )
        return all(
            left <= right
            for left, right in zip(nonzero_signs, nonzero_signs[1:], strict=False)
        )

    @property
    def has_at_most_one_cash_sign_change(self) -> bool:
        return len(self.cash_sign_change_periods) <= 1


def _sign(value: Fraction) -> int:
    return (value > ZERO) - (value < ZERO)


def _sign_change_periods(values: tuple[Fraction, ...]) -> tuple[int, ...]:
    changes = []
    previous_sign = 0
    for period, value in enumerate(values, start=1):
        current_sign = _sign(value)
        if current_sign == 0:
            continue
        if previous_sign != 0 and current_sign != previous_sign:
            changes.append(period)
        previous_sign = current_sign
    return tuple(changes)


def _reference_crossing_boundaries(
    retention_differences: tuple[Fraction, ...], trough_period: int
) -> tuple[int, ...]:
    return tuple(
        boundary
        for boundary in range(trough_period, len(retention_differences) + 1)
        if all(value <= ZERO for value in retention_differences[:boundary])
        and all(value >= ZERO for value in retention_differences[boundary:])
    )


def _is_floor_aligned(
    floor_differences: tuple[Fraction, ...], boundary: int
) -> bool:
    return all(value >= ZERO for value in floor_differences[:boundary]) and all(
        value <= ZERO for value in floor_differences[boundary:]
    )


def analyze_cash_mechanism(ledger: ScenarioLedger) -> CashMechanismReport:
    """Analyze corrected-minus-neutral carried cash on a single-valley path."""
    valley = describe_valley(ledger.scenario.prices)
    mechanism_steps = []
    previous_cash_difference = ZERO
    for corrected, neutral in zip(
        ledger.corrected.steps,
        ledger.neutral.steps,
        strict=True,
    ):
        if corrected.discretionary_cash is None:
            raise AssertionError("corrected ledger lacks a discretionary interval")
        if neutral.discretionary_cash is None:
            raise AssertionError("neutral ledger lacks a discretionary interval")
        if corrected.guardrail_floor is None or neutral.guardrail_floor is None:
            raise AssertionError("guarded ledger lacks a floor value")

        corrected_retention = (
            HALF if corrected.score is None else Fraction(1) - corrected.score
        )
        floor_difference = (
            corrected.guardrail_floor - neutral.guardrail_floor
        )
        cash_difference = corrected.cash - neutral.cash
        carry_component = corrected_retention * previous_cash_difference
        score_component = (
            (corrected_retention - HALF) * neutral.discretionary_cash
        )
        floor_component = -corrected_retention * floor_difference
        mechanism_steps.append(
            CashMechanismStep(
                period=corrected.period,
                corrected_retention=corrected_retention,
                neutral_discretionary_cash=neutral.discretionary_cash,
                floor_difference=floor_difference,
                cash_difference=cash_difference,
                carry_component=carry_component,
                score_component=score_component,
                floor_component=floor_component,
            )
        )
        previous_cash_difference = cash_difference

    steps = tuple(mechanism_steps)
    cash_differences = tuple(step.cash_difference for step in steps)
    floor_differences = tuple(step.floor_difference for step in steps)
    retention_differences = tuple(
        step.corrected_retention - HALF for step in steps
    )
    reference_boundaries = _reference_crossing_boundaries(
        retention_differences,
        valley.trough_period,
    )
    if not reference_boundaries:
        raise AssertionError(
            "corrected retention does not single-cross on a single-valley path"
        )
    aligned_guardrail_boundary = next(
        (
            boundary
            for boundary in reference_boundaries
            if _is_floor_aligned(floor_differences, boundary)
        ),
        None,
    )
    return CashMechanismReport(
        trough_period=valley.trough_period,
        steps=steps,
        cash_differences=cash_differences,
        cash_sign_change_periods=_sign_change_periods(cash_differences),
        retention_differences=retention_differences,
        floor_differences=floor_differences,
        reference_crossing_boundary=reference_boundaries[0],
        reference_aligned_guardrail_boundary=aligned_guardrail_boundary,
    )
