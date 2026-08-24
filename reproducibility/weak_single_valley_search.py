"""Deterministic exact-rational search over weak single-valley price paths."""

import json
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from itertools import product
from typing import Literal

from reproducibility.arbitrary_horizon import (
    ExactRationalError,
    RationalScenario,
    ScenarioLedger,
    WealthGap,
    evaluate_scenario,
)


ZERO = Fraction(0)
ONE = Fraction(1)

ComparisonName = Literal["corrected_vs_dca", "corrected_vs_neutral"]


class SearchSliceKind(str, Enum):
    """Supported ways to select a deterministic subset of search results."""

    ALL = "all"
    EVALUATION_MULTIPLIER = "evaluation_multiplier"
    GENUINE_CYCLE = "genuine_cycle"
    GENUINE_CYCLE_AT_TERMINAL_PRICE = "genuine_cycle_at_terminal_price"
    STRICT_CYCLE_AT_TERMINAL_PRICE = "strict_cycle_at_terminal_price"


@dataclass(frozen=True)
class SearchSlice:
    """Typed descriptor for one reported search slice."""

    kind: SearchSliceKind
    evaluation_multiplier: Fraction | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, SearchSliceKind):
            raise TypeError("kind must be a SearchSliceKind")
        has_multiplier = self.evaluation_multiplier is not None
        expects_multiplier = self.kind is SearchSliceKind.EVALUATION_MULTIPLIER
        if has_multiplier != expects_multiplier:
            raise ValueError(
                "only evaluation-multiplier slices require a multiplier"
            )
        if has_multiplier and (
            not isinstance(self.evaluation_multiplier, Fraction)
            or self.evaluation_multiplier <= ZERO
        ):
            raise ValueError("evaluation multiplier must be a positive Fraction")

    @classmethod
    def for_evaluation_multiplier(cls, multiplier: Fraction) -> "SearchSlice":
        return cls(SearchSliceKind.EVALUATION_MULTIPLIER, multiplier)

    @property
    def name(self) -> str:
        if self.kind is SearchSliceKind.EVALUATION_MULTIPLIER:
            return f"{self.kind.value}={self.evaluation_multiplier}"
        return self.kind.value


@dataclass(frozen=True)
class SearchGrid:
    """Finite rational domain for one deterministic falsification run."""

    horizons: tuple[int, ...]
    price_levels: tuple[Fraction, ...]
    initial_price: Fraction
    evaluation_multipliers: tuple[Fraction, ...]
    safety_factors: tuple[Fraction, ...]
    parameter_pairs: tuple[tuple[Fraction, Fraction], ...]
    equal_deposit: Fraction

    def __post_init__(self) -> None:
        if not self.horizons or any(horizon < 1 for horizon in self.horizons):
            raise ValueError("horizons must be positive")
        if tuple(sorted(set(self.horizons))) != self.horizons:
            raise ValueError("horizons must be strictly increasing")

        fraction_values = (
            self.price_levels
            + (self.initial_price,)
            + self.evaluation_multipliers
            + self.safety_factors
            + tuple(value for pair in self.parameter_pairs for value in pair)
            + (self.equal_deposit,)
        )
        if any(not isinstance(value, Fraction) for value in fraction_values):
            raise TypeError("all grid scalars must be Fraction values")
        if not self.price_levels or any(level <= ZERO for level in self.price_levels):
            raise ValueError("price_levels must be positive")
        if tuple(sorted(set(self.price_levels))) != self.price_levels:
            raise ValueError("price_levels must be strictly increasing")
        if self.initial_price not in self.price_levels:
            raise ValueError("initial_price must belong to price_levels")
        if not self.evaluation_multipliers or any(
            multiplier <= ZERO for multiplier in self.evaluation_multipliers
        ):
            raise ValueError("evaluation_multipliers must be positive")
        if not self.safety_factors or any(
            not ZERO < safety_factor < ONE
            for safety_factor in self.safety_factors
        ):
            raise ValueError("safety_factors must lie in (0, 1)")
        if not self.parameter_pairs:
            raise ValueError("parameter_pairs must be nonempty")
        if any(
            alpha >= ONE or alpha * beta > ZERO
            for alpha, beta in self.parameter_pairs
        ):
            raise ValueError(
                "parameters must have alpha < 1 and alpha * beta <= 0"
            )
        if self.equal_deposit <= ZERO:
            raise ValueError("equal_deposit must be positive")


DEFAULT_GRID = SearchGrid(
    horizons=(4, 5, 6, 7, 8),
    price_levels=(
        Fraction(1, 2),
        Fraction(2, 3),
        ONE,
        Fraction(3, 2),
        Fraction(2),
    ),
    initial_price=ONE,
    evaluation_multipliers=(ONE, Fraction(1, 2), Fraction(2)),
    safety_factors=(Fraction(1, 2), Fraction(1, 4), Fraction(3, 4)),
    parameter_pairs=(
        (ZERO, -ONE),
        (ZERO, ONE),
        (-ONE, ZERO),
    ),
    equal_deposit=ONE,
)


@dataclass(frozen=True)
class ClassificationCounts:
    win: int = 0
    tie: int = 0
    loss: int = 0

    @property
    def total(self) -> int:
        return self.win + self.tie + self.loss


@dataclass(frozen=True)
class ValleyShape:
    trough_period: int
    genuine_decline: bool
    genuine_recovery: bool
    strict_decline: bool
    strict_recovery: bool

    @property
    def genuine_cycle(self) -> bool:
        return self.genuine_decline and self.genuine_recovery

    @property
    def strict_cycle(self) -> bool:
        return self.strict_decline and self.strict_recovery


@dataclass(frozen=True)
class PathShapeCounts:
    all_paths: int
    genuine_cycle: int
    strict_cycle: int


@dataclass(frozen=True)
class SliceSummary:
    search_slice: SearchSlice
    scenario_count: int
    corrected_vs_dca: ClassificationCounts
    corrected_vs_neutral: ClassificationCounts

    @property
    def name(self) -> str:
        return self.search_slice.name


@dataclass(frozen=True)
class SearchWitness:
    name: str
    comparison: ComparisonName
    ledger: ScenarioLedger
    unguarded_ledger: ScenarioLedger
    gap: WealthGap

    @property
    def corrected_floor_periods(self) -> tuple[int, ...]:
        return tuple(
            step.period for step in self.ledger.corrected.steps if step.floor_active
        )

    @property
    def neutral_floor_periods(self) -> tuple[int, ...]:
        return tuple(
            step.period for step in self.ledger.neutral.steps if step.floor_active
        )

    @property
    def differing_floor_periods(self) -> tuple[int, ...]:
        return tuple(
            corrected.period
            for corrected, neutral in zip(
                self.ledger.corrected.steps,
                self.ledger.neutral.steps,
                strict=True,
            )
            if corrected.guardrail_floor != neutral.guardrail_floor
        )

    @property
    def unguarded_gap(self) -> WealthGap | None:
        if self.comparison != "corrected_vs_neutral":
            return None
        return self.unguarded_ledger.gap("corrected", "neutral")

    @property
    def guardrail_contribution_to_gap(self) -> Fraction | None:
        unguarded_gap = self.unguarded_gap
        if unguarded_gap is None:
            return None
        return self.gap.direct - unguarded_gap.direct

    @property
    def guardrail_contributed(self) -> bool | None:
        contribution = self.guardrail_contribution_to_gap
        return None if contribution is None else contribution != ZERO


@dataclass(frozen=True)
class SearchResult:
    grid: SearchGrid
    path_counts: tuple[tuple[int, int], ...]
    path_shapes: PathShapeCounts
    validated_path_count: int
    scenario_count: int
    exact_domain_rejections: int
    corrected_vs_dca: ClassificationCounts
    corrected_vs_neutral: ClassificationCounts
    slice_summaries: tuple[SliceSummary, ...]
    witnesses: tuple[SearchWitness, ...]

    def summary(self, search_slice: SearchSlice) -> SliceSummary:
        try:
            return next(
                summary
                for summary in self.slice_summaries
                if summary.search_slice == search_slice
            )
        except StopIteration as error:
            raise ValueError(f"unknown search slice: {search_slice.name}") from error

    def witness(self, name: str) -> SearchWitness:
        try:
            return next(witness for witness in self.witnesses if witness.name == name)
        except StopIteration as error:
            raise ValueError(f"unknown witness: {name}") from error

    def first_loss(self, comparison: ComparisonName) -> SearchWitness | None:
        if comparison not in ("corrected_vs_dca", "corrected_vs_neutral"):
            raise ValueError(f"unknown comparison: {comparison}")
        name = f"smallest_{comparison}_loss"
        return next((witness for witness in self.witnesses if witness.name == name), None)


def is_weak_single_valley(prices: tuple[Fraction, ...]) -> bool:
    """Return whether positive prices weakly fall to one trough then rise."""
    if not prices or any(
        not isinstance(price, Fraction) or price <= ZERO for price in prices
    ):
        return False

    trough = prices.index(min(prices))
    falls_to_trough = all(
        prices[index] >= prices[index + 1] for index in range(trough)
    )
    rises_after_trough = all(
        prices[index] <= prices[index + 1]
        for index in range(trough, len(prices) - 1)
    )
    return falls_to_trough and rises_after_trough


def describe_valley(prices: tuple[Fraction, ...]) -> ValleyShape:
    """Describe independently observable shape refinements of a valid path."""
    if not is_weak_single_valley(prices):
        raise ValueError("prices must form a positive weak single-valley path")

    trough_index = prices.index(min(prices))
    descent = tuple(zip(prices[:trough_index], prices[1 : trough_index + 1], strict=True))
    recovery = tuple(zip(prices[trough_index:-1], prices[trough_index + 1 :], strict=True))
    genuine_decline = any(left > right for left, right in descent)
    genuine_recovery = any(left < right for left, right in recovery)
    return ValleyShape(
        trough_period=trough_index + 1,
        genuine_decline=genuine_decline,
        genuine_recovery=genuine_recovery,
        strict_decline=bool(descent) and all(left > right for left, right in descent),
        strict_recovery=bool(recovery) and all(
            left < right for left, right in recovery
        ),
    )


def _price_complexity_key(
    prices: tuple[Fraction, ...], price_levels: tuple[Fraction, ...]
) -> tuple[object, ...]:
    level_index = {price: index for index, price in enumerate(price_levels)}
    adjacent = tuple(zip(prices[:-1], prices[1:], strict=True))
    return (
        len(set(prices)),
        sum(left != right for left, right in adjacent),
        sum((abs(left - right) for left, right in adjacent), ZERO),
        tuple(level_index[price] for price in prices),
    )


def enumerate_weak_single_valley_paths(
    grid: SearchGrid, horizon: int
) -> tuple[tuple[Fraction, ...], ...]:
    """Enumerate every normalized grid path once in declared complexity order."""
    if horizon not in grid.horizons:
        raise ValueError("horizon is outside the declared grid")

    candidates = (
        (grid.initial_price,) + tail
        for tail in product(grid.price_levels, repeat=horizon - 1)
    )
    paths = tuple(path for path in candidates if is_weak_single_valley(path))
    return tuple(
        sorted(
            paths,
            key=lambda path: _price_complexity_key(path, grid.price_levels),
        )
    )


def _new_summary_counter() -> dict[str, int]:
    return {
        "scenario_count": 0,
        "dca_win": 0,
        "dca_tie": 0,
        "dca_loss": 0,
        "neutral_win": 0,
        "neutral_tie": 0,
        "neutral_loss": 0,
    }


def _record_summary(
    counter: dict[str, int],
    dca_gap: WealthGap,
    neutral_gap: WealthGap,
) -> None:
    counter["scenario_count"] += 1
    counter[f"dca_{dca_gap.classification}"] += 1
    counter[f"neutral_{neutral_gap.classification}"] += 1


def _freeze_summary(
    search_slice: SearchSlice, counter: dict[str, int]
) -> SliceSummary:
    return SliceSummary(
        search_slice=search_slice,
        scenario_count=counter["scenario_count"],
        corrected_vs_dca=ClassificationCounts(
            win=counter["dca_win"],
            tie=counter["dca_tie"],
            loss=counter["dca_loss"],
        ),
        corrected_vs_neutral=ClassificationCounts(
            win=counter["neutral_win"],
            tie=counter["neutral_tie"],
            loss=counter["neutral_loss"],
        ),
    )


def _witness_names(
    comparison: ComparisonName,
    shape: ValleyShape,
    evaluation_multiplier: Fraction,
) -> tuple[str, ...]:
    names = [f"smallest_{comparison}_loss"]
    if shape.genuine_cycle and evaluation_multiplier == ONE:
        names.append(
            f"smallest_genuine_cycle_{comparison}_loss_at_terminal_price"
        )
    if shape.strict_cycle and evaluation_multiplier == ONE:
        names.append(f"smallest_strict_cycle_{comparison}_loss_at_terminal_price")
    return tuple(names)


def run_search(grid: SearchGrid) -> SearchResult:
    """Evaluate the complete declared grid through the public scenario seam."""
    path_counts = []
    validated_path_count = 0
    genuine_cycle_path_count = 0
    strict_cycle_path_count = 0
    scenario_count = 0
    exact_domain_rejections = 0
    all_slice = SearchSlice(SearchSliceKind.ALL)
    evaluation_slices = {
        multiplier: SearchSlice.for_evaluation_multiplier(multiplier)
        for multiplier in grid.evaluation_multipliers
    }
    genuine_cycle_slice = SearchSlice(SearchSliceKind.GENUINE_CYCLE)
    genuine_terminal_slice = SearchSlice(
        SearchSliceKind.GENUINE_CYCLE_AT_TERMINAL_PRICE
    )
    strict_terminal_slice = SearchSlice(
        SearchSliceKind.STRICT_CYCLE_AT_TERMINAL_PRICE
    )
    search_slices = (
        all_slice,
        *evaluation_slices.values(),
        genuine_cycle_slice,
        genuine_terminal_slice,
        strict_terminal_slice,
    )
    summary_counters = {
        search_slice: _new_summary_counter() for search_slice in search_slices
    }
    witnesses: dict[str, SearchWitness] = {}

    for horizon in grid.horizons:
        paths = enumerate_weak_single_valley_paths(grid, horizon)
        path_counts.append((horizon, len(paths)))
        for prices in paths:
            if not is_weak_single_valley(prices):
                raise AssertionError("generated path is not weak single-valley")
            validated_path_count += 1
            shape = describe_valley(prices)
            genuine_cycle_path_count += shape.genuine_cycle
            strict_cycle_path_count += shape.strict_cycle

            for safety_factor in grid.safety_factors:
                for alpha, beta in grid.parameter_pairs:
                    for evaluation_multiplier in grid.evaluation_multipliers:
                        scenario = RationalScenario(
                            prices=prices,
                            deposits=(grid.equal_deposit,) * horizon,
                            evaluation_price=evaluation_multiplier * prices[-1],
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
                        dca_gap = ledger.gap("corrected", "dca")
                        neutral_gap = ledger.gap("corrected", "neutral")
                        applicable_slices = [
                            all_slice,
                            evaluation_slices[evaluation_multiplier],
                        ]
                        if shape.genuine_cycle:
                            applicable_slices.append(genuine_cycle_slice)
                            if evaluation_multiplier == ONE:
                                applicable_slices.append(genuine_terminal_slice)
                        if shape.strict_cycle and evaluation_multiplier == ONE:
                            applicable_slices.append(strict_terminal_slice)
                        for search_slice in applicable_slices:
                            _record_summary(
                                summary_counters[search_slice],
                                dca_gap,
                                neutral_gap,
                            )

                        gaps: tuple[tuple[ComparisonName, WealthGap], ...] = (
                            ("corrected_vs_dca", dca_gap),
                            ("corrected_vs_neutral", neutral_gap),
                        )
                        unguarded_ledger = None
                        for comparison, gap in gaps:
                            if gap.classification != "loss":
                                continue
                            for name in _witness_names(
                                comparison, shape, evaluation_multiplier
                            ):
                                if name not in witnesses:
                                    if unguarded_ledger is None:
                                        unguarded_ledger = evaluate_scenario(
                                            scenario,
                                            guardrail_enabled=False,
                                        )
                                    witnesses[name] = SearchWitness(
                                        name=name,
                                        comparison=comparison,
                                        ledger=ledger,
                                        unguarded_ledger=unguarded_ledger,
                                        gap=gap,
                                    )

    slice_summaries = tuple(
        _freeze_summary(search_slice, summary_counters[search_slice])
        for search_slice in search_slices
    )
    all_summary = slice_summaries[0]

    return SearchResult(
        grid=grid,
        path_counts=tuple(path_counts),
        path_shapes=PathShapeCounts(
            all_paths=validated_path_count,
            genuine_cycle=genuine_cycle_path_count,
            strict_cycle=strict_cycle_path_count,
        ),
        validated_path_count=validated_path_count,
        scenario_count=scenario_count,
        exact_domain_rejections=exact_domain_rejections,
        corrected_vs_dca=all_summary.corrected_vs_dca,
        corrected_vs_neutral=all_summary.corrected_vs_neutral,
        slice_summaries=slice_summaries,
        witnesses=tuple(witnesses.values()),
    )


def _fraction_text(value: Fraction | None) -> str | None:
    return None if value is None else str(value)


def _counts_payload(counts: ClassificationCounts) -> dict[str, int]:
    return {
        "win": counts.win,
        "tie": counts.tie,
        "loss": counts.loss,
    }


def _policy_steps_payload(ledger: ScenarioLedger, policy: str) -> list[dict[str, object]]:
    steps = getattr(ledger, policy).steps
    return [
        {
            "period": step.period,
            "reference": _fraction_text(step.reference),
            "score": _fraction_text(step.score),
            "guardrail_floor": _fraction_text(step.guardrail_floor),
            "floor_active": step.floor_active,
            "purchase": str(step.purchase),
            "cash": str(step.cash),
        }
        for step in steps
    ]


def _witness_payload(witness: SearchWitness) -> dict[str, object]:
    scenario = witness.ledger.scenario
    return {
        "comparison": witness.comparison,
        "scenario": {
            "prices": [str(value) for value in scenario.prices],
            "deposits": [str(value) for value in scenario.deposits],
            "evaluation_price": str(scenario.evaluation_price),
            "safety_factor": str(scenario.safety_factor),
            "alpha": str(scenario.alpha),
            "beta": str(scenario.beta),
        },
        "gap": str(witness.gap.direct),
        "cash_timing_gap": str(witness.gap.cash_timing),
        "classification": witness.gap.classification,
        "corrected_floor_periods": list(witness.corrected_floor_periods),
        "neutral_floor_periods": list(witness.neutral_floor_periods),
        "differing_floor_periods": list(witness.differing_floor_periods),
        "unguarded_gap": _fraction_text(
            None if witness.unguarded_gap is None else witness.unguarded_gap.direct
        ),
        "guardrail_contribution_to_gap": _fraction_text(
            witness.guardrail_contribution_to_gap
        ),
        "guardrail_contributed": witness.guardrail_contributed,
        "corrected_steps": _policy_steps_payload(witness.ledger, "corrected"),
        "neutral_steps": _policy_steps_payload(witness.ledger, "neutral"),
    }


def result_payload(result: SearchResult) -> dict[str, object]:
    """Return a deterministic JSON-compatible record of one complete run."""
    return {
        "grid": {
            "horizons": list(result.grid.horizons),
            "price_levels": [str(value) for value in result.grid.price_levels],
            "initial_price": str(result.grid.initial_price),
            "evaluation_multipliers": [
                str(value) for value in result.grid.evaluation_multipliers
            ],
            "safety_factors": [
                str(value) for value in result.grid.safety_factors
            ],
            "parameter_pairs": [
                {"alpha": str(alpha), "beta": str(beta)}
                for alpha, beta in result.grid.parameter_pairs
            ],
            "equal_deposit": str(result.grid.equal_deposit),
        },
        "enumeration_order": [
            "horizon ascending",
            "price complexity: distinct levels, transitions, total variation, tuple",
            "safety-factor declaration order",
            "(alpha, beta) declaration order",
            "evaluation-multiplier declaration order",
            "unit equal-deposit normalization",
        ],
        "pruning_rules": [
            "fix the first purchase price at 1 to remove common price-scale copies",
            "fix every equal positive deposit at 1 to remove common budget-scale copies",
            "retain a price tuple exactly when the independent weak single-valley predicate holds",
        ],
        "path_counts": [
            {"horizon": horizon, "count": count}
            for horizon, count in result.path_counts
        ],
        "path_shapes": {
            "all_paths": result.path_shapes.all_paths,
            "genuine_cycle": result.path_shapes.genuine_cycle,
            "strict_cycle": result.path_shapes.strict_cycle,
        },
        "validated_path_count": result.validated_path_count,
        "scenario_count": result.scenario_count,
        "exact_domain_rejections": result.exact_domain_rejections,
        "summaries": {
            summary.name: {
                "scenario_count": summary.scenario_count,
                "corrected_vs_dca": _counts_payload(summary.corrected_vs_dca),
                "corrected_vs_neutral": _counts_payload(
                    summary.corrected_vs_neutral
                ),
            }
            for summary in result.slice_summaries
        },
        "witnesses": {
            witness.name: _witness_payload(witness) for witness in result.witnesses
        },
        "scope_limit": (
            "Exact exhaustive coverage of this finite grid is computational "
            "evidence, not proof outside the declared domain."
        ),
    }


def render_json(result: SearchResult) -> str:
    return json.dumps(result_payload(result), indent=2, sort_keys=True)


def main() -> None:
    print(render_json(run_search(DEFAULT_GRID)))


if __name__ == "__main__":
    main()
