"""Exact evaluation-price boundaries and optional single-valley diagnostics."""

from dataclasses import dataclass
from fractions import Fraction

from reproducibility.arbitrary_horizon import (
    Classification,
    PolicyLedger,
    ScenarioLedger,
    classify_gap,
)
from reproducibility.weak_single_valley_search import describe_valley


ZERO = Fraction(0)
ONE = Fraction(1)


@dataclass(frozen=True)
class EvaluationPriceBoundary:
    """Exact affine wealth boundary for one pair of realized policy ledgers."""

    cash_differences: tuple[Fraction, ...]
    terminal_purchase_price: Fraction
    terminal_cash_difference: Fraction
    terminal_unit_difference: Fraction
    cash_timing_unit_difference: Fraction

    def __post_init__(self) -> None:
        if not self.cash_differences:
            raise ValueError("cash_differences must be nonempty")
        if self.terminal_purchase_price <= ZERO:
            raise ValueError("terminal_purchase_price must be positive")
        if self.terminal_cash_difference != self.cash_differences[-1]:
            raise AssertionError(
                "terminal cash difference and cash path disagree"
            )
        if self.terminal_unit_difference != self.cash_timing_unit_difference:
            raise AssertionError(
                "terminal units and cash-timing slope disagree"
            )

    @property
    def evaluation_price_intercept(self) -> Fraction:
        return self.terminal_cash_difference

    @property
    def evaluation_price_slope(self) -> Fraction:
        return self.terminal_unit_difference

    @property
    def break_even_evaluation_price(self) -> Fraction | None:
        slope = self.evaluation_price_slope
        if slope == ZERO:
            return None
        root = -self.evaluation_price_intercept / slope
        return root if root > ZERO else None

    def gap_at_evaluation_price(self, evaluation_price: Fraction) -> Fraction:
        if not isinstance(evaluation_price, Fraction):
            raise TypeError("evaluation_price must be a Fraction")
        if evaluation_price <= ZERO:
            raise ValueError("evaluation_price must be positive")
        return (
            self.evaluation_price_intercept
            + evaluation_price * self.evaluation_price_slope
        )

    def classification_at_evaluation_price(
        self, evaluation_price: Fraction
    ) -> Classification:
        return classify_gap(self.gap_at_evaluation_price(evaluation_price))


@dataclass(frozen=True)
class PerformanceBoundaryReport:
    """Universal affine boundaries exposed by one finite-horizon ledger."""

    corrected_vs_dca: EvaluationPriceBoundary
    corrected_vs_neutral: EvaluationPriceBoundary


@dataclass(frozen=True)
class ValleyComparisonBoundary:
    """Terminal-price reciprocal exposures for a single-valley comparison."""

    evaluation: EvaluationPriceBoundary
    decline_exposure: Fraction
    recovery_exposure: Fraction
    gap_at_terminal_purchase_price: Fraction

    def __post_init__(self) -> None:
        cash_timing_slope = (
            self.decline_exposure
            - self.recovery_exposure
            - self.evaluation.terminal_cash_difference
            / self.evaluation.terminal_purchase_price
        )
        if self.evaluation.cash_timing_unit_difference != cash_timing_slope:
            raise AssertionError(
                "affine slope and reciprocal-price exposures disagree"
            )
        inventory_gap = self.evaluation.gap_at_evaluation_price(
            self.evaluation.terminal_purchase_price
        )
        if self.gap_at_terminal_purchase_price != inventory_gap:
            raise AssertionError(
                "terminal-price inventory and reciprocal-exposure gaps disagree"
            )


@dataclass(frozen=True)
class ValleyPerformanceBoundaryReport:
    """Optional weak-single-valley specialization of the affine boundaries."""

    trough_period: int
    corrected_vs_dca: ValleyComparisonBoundary
    corrected_vs_neutral: ValleyComparisonBoundary


def _evaluation_price_boundary(
    prices: tuple[Fraction, ...],
    left: PolicyLedger,
    right: PolicyLedger,
) -> EvaluationPriceBoundary:
    cash_differences = tuple(
        left_step.cash - right_step.cash
        for left_step, right_step in zip(left.steps, right.steps, strict=True)
    )
    cash_timing_unit_difference = sum(
        (
            cash_differences[index]
            * (ONE / prices[index + 1] - ONE / prices[index])
            for index in range(len(prices) - 1)
        ),
        ZERO,
    ) - cash_differences[-1] / prices[-1]
    return EvaluationPriceBoundary(
        cash_differences=cash_differences,
        terminal_purchase_price=prices[-1],
        terminal_cash_difference=cash_differences[-1],
        terminal_unit_difference=left.steps[-1].units - right.steps[-1].units,
        cash_timing_unit_difference=cash_timing_unit_difference,
    )


def _valley_boundary(
    prices: tuple[Fraction, ...],
    trough_index: int,
    boundary: EvaluationPriceBoundary,
) -> ValleyComparisonBoundary:
    cash_differences = boundary.cash_differences
    decline_exposure = sum(
        (
            cash_differences[index]
            * (ONE / prices[index + 1] - ONE / prices[index])
            for index in range(trough_index)
        ),
        ZERO,
    )
    recovery_exposure = sum(
        (
            cash_differences[index]
            * (ONE / prices[index] - ONE / prices[index + 1])
            for index in range(trough_index, len(prices) - 1)
        ),
        ZERO,
    )
    return ValleyComparisonBoundary(
        evaluation=boundary,
        decline_exposure=decline_exposure,
        recovery_exposure=recovery_exposure,
        gap_at_terminal_purchase_price=(
            prices[-1] * (decline_exposure - recovery_exposure)
        ),
    )


def analyze_performance_boundary(
    ledger: ScenarioLedger,
) -> PerformanceBoundaryReport:
    """Analyze corrected gaps against DCA and neutral on any positive path."""
    prices = ledger.scenario.prices
    return PerformanceBoundaryReport(
        corrected_vs_dca=_evaluation_price_boundary(
            prices, ledger.corrected, ledger.dca
        ),
        corrected_vs_neutral=_evaluation_price_boundary(
            prices, ledger.corrected, ledger.neutral
        ),
    )


def analyze_valley_performance_boundary(
    ledger: ScenarioLedger,
) -> ValleyPerformanceBoundaryReport:
    """Specialize the universal boundaries to a weak single-valley path."""
    valley = describe_valley(ledger.scenario.prices)
    trough_index = valley.trough_period - 1
    prices = ledger.scenario.prices
    report = analyze_performance_boundary(ledger)
    return ValleyPerformanceBoundaryReport(
        trough_period=valley.trough_period,
        corrected_vs_dca=_valley_boundary(
            prices, trough_index, report.corrected_vs_dca
        ),
        corrected_vs_neutral=_valley_boundary(
            prices, trough_index, report.corrected_vs_neutral
        ),
    )
