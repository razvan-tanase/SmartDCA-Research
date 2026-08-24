"""Exact-rational public scenario interface for guarded SmartDCA accounting."""

from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from typing import Literal


ZERO = Fraction(0)
HALF = Fraction(1, 2)
ONE = Fraction(1)

PolicyName = Literal["dca", "corrected", "neutral"]
Classification = Literal["win", "tie", "loss"]
RadicalKey = tuple[tuple[int, Fraction], ...]
RadicalExpression = dict[RadicalKey, Fraction]


class ExactRationalError(ValueError):
    """Raised when a valid rational input would require irrational rounding."""


@dataclass(frozen=True)
class RationalScenario:
    prices: tuple[Fraction, ...]
    deposits: tuple[Fraction, ...]
    evaluation_price: Fraction
    safety_factor: Fraction
    alpha: Fraction
    beta: Fraction

    def __post_init__(self) -> None:
        if not isinstance(self.prices, tuple) or not isinstance(self.deposits, tuple):
            raise TypeError("prices and deposits must be tuples of Fraction values")
        if not self.prices or not self.deposits:
            raise ValueError("prices and deposits must be nonempty")
        if len(self.prices) != len(self.deposits):
            raise ValueError("prices and deposits must have equal length")

        scalar_fields = (
            ("evaluation_price", self.evaluation_price),
            ("safety_factor", self.safety_factor),
            ("alpha", self.alpha),
            ("beta", self.beta),
        )
        sequence_fields = tuple(
            (f"prices[{index}]", value)
            for index, value in enumerate(self.prices)
        ) + tuple(
            (f"deposits[{index}]", value)
            for index, value in enumerate(self.deposits)
        )
        for name, value in scalar_fields + sequence_fields:
            if not isinstance(value, Fraction):
                raise TypeError(f"{name} must be a Fraction")

        if any(price <= ZERO for price in self.prices):
            raise ValueError("prices must be positive")
        if any(deposit < ZERO for deposit in self.deposits):
            raise ValueError("deposits must be nonnegative")
        if self.evaluation_price <= ZERO:
            raise ValueError("evaluation_price must be positive")
        if not ZERO < self.safety_factor <= ONE:
            raise ValueError("safety_factor must lie in (0, 1]")


@dataclass(frozen=True)
class PolicyStep:
    period: int
    price: Fraction
    deposit: Fraction
    available_cash: Fraction
    reference: Fraction | None
    relative_price: Fraction | None
    score: Fraction | None
    coverage_before: Fraction | None
    raw_guardrail_floor: Fraction | None
    guardrail_floor: Fraction | None
    floor_active: bool | None
    discretionary_cash: Fraction | None
    purchase: Fraction
    cash: Fraction
    units: Fraction
    dca_units: Fraction
    coverage_after: Fraction | None


@dataclass(frozen=True)
class PolicyLedger:
    name: PolicyName
    steps: tuple[PolicyStep, ...]
    terminal_wealth: Fraction
    cash_timing_terms: tuple[Fraction, ...]
    cash_timing_wealth: Fraction

    def __post_init__(self) -> None:
        if self.name not in ("dca", "corrected", "neutral"):
            raise ValueError(f"unknown policy: {self.name}")
        if len(self.cash_timing_terms) != len(self.steps):
            raise AssertionError("each policy step must have one cash-timing term")
        if self.terminal_wealth != self.cash_timing_wealth:
            raise AssertionError(
                "direct portfolio accounting and cash-timing accounting disagree"
            )


@dataclass(frozen=True)
class WealthGap:
    direct: Fraction
    cash_timing: Fraction

    def __post_init__(self) -> None:
        if self.direct != self.cash_timing:
            raise AssertionError(
                "direct portfolio accounting and cash-timing accounting disagree"
            )

    @property
    def classification(self) -> Classification:
        if self.direct > ZERO:
            return "win"
        if self.direct < ZERO:
            return "loss"
        return "tie"


@dataclass(frozen=True)
class ScenarioLedger:
    scenario: RationalScenario
    dca: PolicyLedger
    corrected: PolicyLedger
    neutral: PolicyLedger

    def gap(self, left: PolicyName, right: PolicyName) -> WealthGap:
        ledgers: dict[PolicyName, PolicyLedger] = {
            "dca": self.dca,
            "corrected": self.corrected,
            "neutral": self.neutral,
        }
        try:
            left_ledger = ledgers[left]
            right_ledger = ledgers[right]
        except KeyError as error:
            raise ValueError(f"unknown policy: {error.args[0]}") from error

        direct = left_ledger.terminal_wealth - right_ledger.terminal_wealth
        cash_timing = _cash_timing_gap(
            self.scenario.prices,
            self.scenario.evaluation_price,
            tuple(step.cash for step in left_ledger.steps),
            tuple(step.cash for step in right_ledger.steps),
        )
        return WealthGap(direct=direct, cash_timing=cash_timing)


def _cash_timing_gap(
    prices: tuple[Fraction, ...],
    evaluation_price: Fraction,
    left_cash: tuple[Fraction, ...],
    right_cash: tuple[Fraction, ...],
) -> Fraction:
    cash_difference = tuple(
        left - right for left, right in zip(left_cash, right_cash, strict=True)
    )
    return sum(
        _cash_timing_terms(prices, evaluation_price, cash_difference), ZERO
    )


def _cash_timing_terms(
    prices: tuple[Fraction, ...],
    evaluation_price: Fraction,
    cash_path: tuple[Fraction, ...],
) -> tuple[Fraction, ...]:
    intermediate = tuple(
        evaluation_price
        * cash_path[index]
        * (ONE / prices[index + 1] - ONE / prices[index])
        for index in range(len(prices) - 1)
    )
    terminal = cash_path[-1] * (ONE - evaluation_price / prices[-1])
    return intermediate + (terminal,)


def _dca_ledger(scenario: RationalScenario) -> PolicyLedger:
    units = ZERO
    steps = []
    for period, (price, deposit) in enumerate(
        zip(scenario.prices, scenario.deposits, strict=True), start=1
    ):
        units += deposit / price
        steps.append(
            PolicyStep(
                period=period,
                price=price,
                deposit=deposit,
                available_cash=deposit,
                reference=None,
                relative_price=None,
                score=None,
                coverage_before=None,
                raw_guardrail_floor=None,
                guardrail_floor=None,
                floor_active=None,
                discretionary_cash=None,
                purchase=deposit,
                cash=ZERO,
                units=units,
                dca_units=units,
                coverage_after=None,
            )
        )
    terminal_wealth = scenario.evaluation_price * units
    cash_timing_terms = (ZERO,) * len(steps)
    return PolicyLedger(
        name="dca",
        steps=tuple(steps),
        terminal_wealth=terminal_wealth,
        cash_timing_terms=cash_timing_terms,
        cash_timing_wealth=terminal_wealth,
    )


def _corrected_score(relative_price: Fraction, alpha: Fraction) -> Fraction:
    exponent = ONE - alpha
    odds_denominator = _exact_rational_power(relative_price, exponent)
    return ONE / (ONE + odds_denominator)


def _integer_nth_root_exact(value: int, degree: int) -> int:
    if value < 0 or degree < 1:
        raise ValueError("a nonnegative integer and positive root degree are required")
    if value in (0, 1) or degree == 1:
        return value

    lower = 0
    upper = 1
    while upper**degree < value:
        upper *= 2
    while lower + 1 < upper:
        midpoint = (lower + upper) // 2
        if midpoint**degree < value:
            lower = midpoint
        else:
            upper = midpoint
    if upper**degree != value:
        raise ExactRationalError(
            "scenario leaves the exact-rational domain: "
            f"{value} has no integer {degree}-th root"
        )
    return upper


def _exact_rational_power(base: Fraction, exponent: Fraction) -> Fraction:
    if base <= ZERO:
        raise ValueError("exact rational powers require a positive base")
    powered = base ** exponent.numerator
    return Fraction(
        _integer_nth_root_exact(powered.numerator, exponent.denominator),
        _integer_nth_root_exact(powered.denominator, exponent.denominator),
    )


@cache
def _factor_integer(value: int) -> tuple[tuple[int, int], ...]:
    """Return the prime factorization of one positive integer."""
    if value < 1:
        raise ValueError("prime factorization requires a positive integer")

    factors = []
    remaining = value
    candidate = 2
    while candidate * candidate <= remaining:
        multiplicity = 0
        while remaining % candidate == 0:
            remaining //= candidate
            multiplicity += 1
        if multiplicity:
            factors.append((candidate, multiplicity))
        candidate = 3 if candidate == 2 else candidate + 2
    if remaining > 1:
        factors.append((remaining, 1))
    return tuple(factors)


def _prime_valuations(value: Fraction) -> dict[int, int]:
    valuations = dict(_factor_integer(value.numerator))
    for prime, multiplicity in _factor_integer(value.denominator):
        valuations[prime] = valuations.get(prime, 0) - multiplicity
    return valuations


def _radical_power_expression(
    base: Fraction, exponent: Fraction
) -> RadicalExpression:
    """Represent a positive rational power in a canonical radical basis."""
    coefficient = ONE
    radical_exponents = {}
    for prime, valuation in _prime_valuations(base).items():
        power = exponent * valuation
        whole = power.numerator // power.denominator
        remainder = power - whole
        if whole >= 0:
            coefficient *= prime**whole
        else:
            coefficient /= prime ** (-whole)
        if remainder:
            radical_exponents[prime] = remainder
    return {tuple(sorted(radical_exponents.items())): coefficient}


def _add_expressions(*expressions: RadicalExpression) -> RadicalExpression:
    result: RadicalExpression = {}
    for expression in expressions:
        for key, coefficient in expression.items():
            result[key] = result.get(key, ZERO) + coefficient
            if result[key] == ZERO:
                del result[key]
    return result


def _scale_expression(
    expression: RadicalExpression, scalar: Fraction
) -> RadicalExpression:
    if scalar == ZERO:
        return {}
    return {key: scalar * coefficient for key, coefficient in expression.items()}


def _multiply_expressions(
    left: RadicalExpression, right: RadicalExpression
) -> RadicalExpression:
    products: list[RadicalExpression] = []
    for left_key, left_coefficient in left.items():
        for right_key, right_coefficient in right.items():
            exponents = dict(left_key)
            coefficient = left_coefficient * right_coefficient
            for prime, right_exponent in right_key:
                total = exponents.get(prime, ZERO) + right_exponent
                whole = total.numerator // total.denominator
                remainder = total - whole
                if whole:
                    coefficient *= prime**whole
                if remainder:
                    exponents[prime] = remainder
                else:
                    exponents.pop(prime, None)
            products.append({tuple(sorted(exponents.items())): coefficient})
    return _add_expressions(*products)


def _expression_power(
    expression: RadicalExpression, exponent: int
) -> RadicalExpression:
    if exponent < 0:
        raise ValueError("expression power must be nonnegative")
    result: RadicalExpression = {(): ONE}
    factor = expression
    remaining = exponent
    while remaining:
        if remaining % 2:
            result = _multiply_expressions(result, factor)
        remaining //= 2
        if remaining:
            factor = _multiply_expressions(factor, factor)
    return result


def _rational_quotient(
    numerator: RadicalExpression, denominator: RadicalExpression
) -> Fraction | None:
    """Return the exact rational quotient when two radical sums are proportional."""
    if not denominator:
        raise ZeroDivisionError("radical-expression denominator is zero")
    if not numerator:
        return ZERO
    if numerator.keys() != denominator.keys():
        return None

    first_key = next(iter(denominator))
    quotient = numerator[first_key] / denominator[first_key]
    if all(
        numerator[key] == quotient * coefficient
        for key, coefficient in denominator.items()
    ):
        return quotient
    return None


def _exact_radical_ratio_power(
    numerator: RadicalExpression,
    denominator: RadicalExpression,
    exponent: Fraction,
) -> Fraction:
    """Evaluate a rational result without requiring rational intermediates."""
    power = exponent.numerator
    if power < 0:
        numerator, denominator = denominator, numerator
        power = -power
    rational_power = _rational_quotient(
        _expression_power(numerator, power),
        _expression_power(denominator, power),
    )
    if rational_power is None or rational_power <= ZERO:
        raise ExactRationalError(
            "scenario leaves the exact-rational domain: "
            "the corrected reference is not rational"
        )
    return _exact_rational_power(
        rational_power, Fraction(1, exponent.denominator)
    )


def _diagonal_reference(
    normalized_lagged_prices: tuple[Fraction, ...], alpha: Fraction
) -> Fraction:
    weights = tuple(
        _radical_power_expression(price, alpha)
        for price in normalized_lagged_prices
    )
    total_weight = _add_expressions(*weights)
    valuations = tuple(
        _prime_valuations(price) for price in normalized_lagged_prices
    )
    reference = ONE
    for prime in sorted({prime for row in valuations for prime in row}):
        weighted_valuation = _add_expressions(
            *(
                _scale_expression(weight, Fraction(row.get(prime, 0)))
                for weight, row in zip(weights, valuations, strict=True)
            )
        )
        exponent = _rational_quotient(weighted_valuation, total_weight)
        if exponent is None or exponent.denominator != 1:
            raise ExactRationalError(
                "scenario leaves the exact-rational domain: "
                "the corrected reference is not rational"
            )
        if exponent >= ZERO:
            reference *= prime**exponent.numerator
        else:
            reference /= prime ** (-exponent.numerator)
    return reference


def _corrected_reference(
    normalized_lagged_prices: tuple[Fraction, ...],
    alpha: Fraction,
    beta: Fraction,
) -> Fraction:
    if len(normalized_lagged_prices) == 1:
        return normalized_lagged_prices[0]
    if alpha == beta:
        return _diagonal_reference(normalized_lagged_prices, alpha)

    numerator = _add_expressions(
        *(
            _radical_power_expression(price, alpha)
            for price in normalized_lagged_prices
        )
    )
    denominator = _add_expressions(
        *(
            _radical_power_expression(price, beta)
            for price in normalized_lagged_prices
        )
    )
    return _exact_radical_ratio_power(
        numerator, denominator, ONE / (alpha - beta)
    )


def _score_ledger(
    scenario: RationalScenario,
    dca: PolicyLedger,
    *,
    neutral: bool,
    guardrail_enabled: bool,
) -> PolicyLedger:
    cash = ZERO
    units = ZERO
    dca_units = ZERO
    steps = []
    anchor = scenario.prices[0]

    for index, (price, deposit) in enumerate(
        zip(scenario.prices, scenario.deposits, strict=True)
    ):
        coverage_before = units - scenario.safety_factor * dca_units
        available_cash = cash + deposit
        raw_floor = scenario.safety_factor * deposit - price * coverage_before
        floor = max(ZERO, raw_floor) if guardrail_enabled else ZERO
        discretionary_cash = available_cash - floor

        normalized_lagged = tuple(
            past_price / anchor for past_price in scenario.prices[:index]
        )
        if index == 0:
            reference = None
            relative_price = ONE
            score = HALF
        elif discretionary_cash == ZERO:
            reference = None
            relative_price = None
            score = HALF if neutral else None
        else:
            reference = _corrected_reference(
                normalized_lagged, scenario.alpha, scenario.beta
            )
            relative_price = (price / anchor) / reference
            score = (
                HALF
                if neutral
                else _corrected_score(relative_price, scenario.alpha)
            )
        effective_score = ZERO if score is None else score
        purchase = floor + effective_score * discretionary_cash
        cash = available_cash - purchase
        units += purchase / price
        dca_units = dca.steps[index].dca_units
        coverage_after = units - scenario.safety_factor * dca_units
        steps.append(
            PolicyStep(
                period=index + 1,
                price=price,
                deposit=deposit,
                available_cash=available_cash,
                reference=reference,
                relative_price=relative_price,
                score=score,
                coverage_before=coverage_before,
                raw_guardrail_floor=raw_floor,
                guardrail_floor=floor,
                floor_active=guardrail_enabled and raw_floor > ZERO,
                discretionary_cash=discretionary_cash,
                purchase=purchase,
                cash=cash,
                units=units,
                dca_units=dca_units,
                coverage_after=coverage_after,
            )
        )

    name: PolicyName = "neutral" if neutral else "corrected"
    terminal_wealth = cash + scenario.evaluation_price * units
    cash_timing_terms = _cash_timing_terms(
        scenario.prices,
        scenario.evaluation_price,
        tuple(step.cash for step in steps),
    )
    return PolicyLedger(
        name=name,
        steps=tuple(steps),
        terminal_wealth=terminal_wealth,
        cash_timing_terms=cash_timing_terms,
        cash_timing_wealth=dca.terminal_wealth + sum(cash_timing_terms, ZERO),
    )


def evaluate_scenario(
    scenario: RationalScenario, *, guardrail_enabled: bool = True
) -> ScenarioLedger:
    """Evaluate all policies, optionally disabling the floor for attribution."""
    if not isinstance(guardrail_enabled, bool):
        raise TypeError("guardrail_enabled must be a bool")
    dca = _dca_ledger(scenario)
    corrected = _score_ledger(
        scenario,
        dca,
        neutral=False,
        guardrail_enabled=guardrail_enabled,
    )
    neutral = _score_ledger(
        scenario,
        dca,
        neutral=True,
        guardrail_enabled=guardrail_enabled,
    )
    return ScenarioLedger(scenario, dca, corrected, neutral)
