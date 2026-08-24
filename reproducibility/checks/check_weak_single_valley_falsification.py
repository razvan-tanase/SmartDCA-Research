#!/usr/bin/env python3
"""Exact end-to-end checks for the weak single-valley falsification search."""

import json
from fractions import Fraction

from reproducibility.arbitrary_horizon import RationalScenario, evaluate_scenario
from reproducibility.weak_single_valley_search import (
    DEFAULT_GRID,
    ClassificationCounts,
    PathShapeCounts,
    SearchGrid,
    SearchSlice,
    SearchSliceKind,
    SearchWitness,
    SliceSummary,
    describe_valley,
    enumerate_weak_single_valley_paths,
    is_weak_single_valley,
    render_json,
    run_search,
)


ZERO = Fraction(0)
HALF = Fraction(1, 2)
ONE = Fraction(1)
TWO = Fraction(2)


def small_four_date_grid() -> SearchGrid:
    return SearchGrid(
        horizons=(4,),
        price_levels=(HALF, ONE, TWO),
        initial_price=ONE,
        evaluation_multipliers=(ONE,),
        safety_factors=(HALF,),
        parameter_pairs=((ZERO, -ONE),),
        equal_deposit=ONE,
    )


def check_floor_disabled_counterfactual_attribution():
    scenario = RationalScenario(
        prices=(ONE, Fraction(2, 3), ONE, TWO),
        deposits=(ONE,) * 4,
        evaluation_price=TWO,
        safety_factor=Fraction(3, 4),
        alpha=ZERO,
        beta=-ONE,
    )

    unguarded = evaluate_scenario(scenario, guardrail_enabled=False)
    assert unguarded.gap("corrected", "neutral").direct == Fraction(49, 360)
    assert not any(
        step.floor_active
        for ledger in (unguarded.corrected, unguarded.neutral)
        for step in ledger.steps
    )

    equal_floor_scenario = RationalScenario(
        prices=(ONE, HALF),
        deposits=(ONE, ONE),
        evaluation_price=ONE,
        safety_factor=HALF,
        alpha=ZERO,
        beta=-ONE,
    )
    guarded_equal_floors = evaluate_scenario(equal_floor_scenario)
    unguarded_equal_floors = evaluate_scenario(
        equal_floor_scenario,
        guardrail_enabled=False,
    )
    equal_floor_gap = guarded_equal_floors.gap("corrected", "neutral")
    equal_floor_witness = SearchWitness(
        name="equal_floor_attribution_regression",
        comparison="corrected_vs_neutral",
        ledger=guarded_equal_floors,
        unguarded_ledger=unguarded_equal_floors,
        gap=equal_floor_gap,
    )

    assert equal_floor_witness.differing_floor_periods == ()
    assert equal_floor_gap.direct == Fraction(7, 48)
    assert equal_floor_witness.unguarded_gap is not None
    assert equal_floor_witness.unguarded_gap.direct == Fraction(1, 4)
    assert equal_floor_witness.guardrail_contribution_to_gap == -Fraction(5, 48)
    assert equal_floor_witness.guardrail_contributed


def check_weak_single_valley_path_boundary():
    valid_paths = (
        (ONE,),
        (ONE, ONE, ONE, ONE),
        (TWO, ONE, HALF),
        (HALF, ONE, TWO),
        (TWO, ONE, ONE, TWO),
        (TWO, TWO, ONE, ONE),
    )
    invalid_paths = (
        (),
        (ZERO, ONE),
        (ONE, TWO, ONE),
        (TWO, ONE, TWO, ONE),
    )

    assert all(is_weak_single_valley(path) for path in valid_paths)
    assert not any(is_weak_single_valley(path) for path in invalid_paths)

    flat_trough = describe_valley((ONE, HALF, HALF, ONE))
    assert (
        flat_trough.trough_period,
        flat_trough.genuine_decline,
        flat_trough.genuine_recovery,
        flat_trough.strict_cycle,
    ) == (2, True, True, False)

    strict_cycle = describe_valley((ONE, HALF, ONE, TWO))
    assert strict_cycle.genuine_cycle
    assert strict_cycle.strict_cycle


def check_four_date_enumeration_is_complete_and_deterministic():
    grid = small_four_date_grid()
    paths = enumerate_weak_single_valley_paths(grid, 4)

    assert len(paths) == 14
    assert paths == enumerate_weak_single_valley_paths(grid, 4)
    assert all(is_weak_single_valley(path) for path in paths)
    assert paths[0] == (ONE, ONE, ONE, ONE)
    assert paths[-1] == (ONE, HALF, ONE, TWO)


def check_four_date_search_aggregates_both_comparisons():
    grid = small_four_date_grid()
    result = run_search(grid)

    assert result.path_counts == ((4, 14),)
    assert result.validated_path_count == 14
    assert result.scenario_count == 14
    assert result.exact_domain_rejections == 0
    assert result.corrected_vs_dca == ClassificationCounts(win=4, tie=1, loss=9)
    assert result.corrected_vs_neutral == ClassificationCounts(
        win=7, tie=7, loss=0
    )

    dca_loss = result.first_loss("corrected_vs_dca")
    assert dca_loss is not None
    assert dca_loss.ledger.scenario.prices == (ONE, ONE, ONE, TWO)
    assert dca_loss.gap.direct == -Fraction(3, 4)
    assert dca_loss.corrected_floor_periods == (1, 2)
    assert dca_loss.neutral_floor_periods == (1, 2)
    assert dca_loss.differing_floor_periods == ()
    assert result.first_loss("corrected_vs_neutral") is None


def check_search_result_is_machine_readable():
    grid = small_four_date_grid()
    result = run_search(grid)
    payload = json.loads(render_json(result))

    assert payload["grid"]["horizons"] == [4]
    assert payload["grid"]["price_levels"] == ["1/2", "1", "2"]
    assert payload["validated_path_count"] == 14
    witness = payload["witnesses"]["smallest_corrected_vs_dca_loss"]
    assert witness["scenario"]["prices"] == ["1", "1", "1", "2"]
    assert witness["gap"] == "-3/4"
    assert witness["unguarded_gap"] is None
    assert witness["guardrail_contribution_to_gap"] is None
    assert witness["guardrail_contributed"] is None


def check_declared_full_search_and_named_witnesses():
    result = run_search(DEFAULT_GRID)

    assert result.path_counts == (
        (4, 53),
        (5, 134),
        (6, 301),
        (7, 616),
        (8, 1170),
    )
    assert result.path_shapes == PathShapeCounts(
        all_paths=2274,
        genuine_cycle=2059,
        strict_cycle=30,
    )
    assert result.validated_path_count == 2274
    assert result.scenario_count == 61398
    assert result.exact_domain_rejections == 0

    all_slice = SearchSlice(SearchSliceKind.ALL)
    assert result.summary(all_slice) == SliceSummary(
        search_slice=all_slice,
        scenario_count=61398,
        corrected_vs_dca=ClassificationCounts(win=23210, tie=56, loss=38132),
        corrected_vs_neutral=ClassificationCounts(
            win=44329, tie=1036, loss=16033
        ),
    )
    terminal_evaluation_slice = SearchSlice.for_evaluation_multiplier(ONE)
    assert result.summary(terminal_evaluation_slice) == SliceSummary(
        search_slice=terminal_evaluation_slice,
        scenario_count=20466,
        corrected_vs_dca=ClassificationCounts(win=3250, tie=55, loss=17161),
        corrected_vs_neutral=ClassificationCounts(win=16122, tie=945, loss=3399),
    )
    half_evaluation_slice = SearchSlice.for_evaluation_multiplier(HALF)
    assert result.summary(half_evaluation_slice) == SliceSummary(
        search_slice=half_evaluation_slice,
        scenario_count=20466,
        corrected_vs_dca=ClassificationCounts(win=19472, tie=0, loss=994),
        corrected_vs_neutral=ClassificationCounts(win=18777, tie=45, loss=1644),
    )
    double_evaluation_slice = SearchSlice.for_evaluation_multiplier(TWO)
    assert result.summary(double_evaluation_slice) == SliceSummary(
        search_slice=double_evaluation_slice,
        scenario_count=20466,
        corrected_vs_dca=ClassificationCounts(win=488, tie=1, loss=19977),
        corrected_vs_neutral=ClassificationCounts(win=9430, tie=46, loss=10990),
    )
    genuine_terminal_slice = SearchSlice(
        SearchSliceKind.GENUINE_CYCLE_AT_TERMINAL_PRICE
    )
    assert result.summary(genuine_terminal_slice) == SliceSummary(
        search_slice=genuine_terminal_slice,
        scenario_count=18531,
        corrected_vs_dca=ClassificationCounts(win=2305, tie=10, loss=16216),
        corrected_vs_neutral=ClassificationCounts(win=16122, tie=0, loss=2409),
    )
    strict_terminal_slice = SearchSlice(
        SearchSliceKind.STRICT_CYCLE_AT_TERMINAL_PRICE
    )
    assert result.summary(strict_terminal_slice) == SliceSummary(
        search_slice=strict_terminal_slice,
        scenario_count=270,
        corrected_vs_dca=ClassificationCounts(win=9, tie=0, loss=261),
        corrected_vs_neutral=ClassificationCounts(win=227, tie=0, loss=43),
    )

    dca_minimum = result.witness("smallest_corrected_vs_dca_loss")
    assert dca_minimum.ledger.scenario.prices == (ONE,) * 4
    assert dca_minimum.ledger.scenario.evaluation_price == TWO
    assert dca_minimum.gap.direct == -Fraction(7, 8)
    assert dca_minimum.differing_floor_periods == ()

    neutral_minimum = result.witness("smallest_corrected_vs_neutral_loss")
    assert neutral_minimum.ledger.scenario.prices == (
        ONE,
        Fraction(2, 3),
        Fraction(2, 3),
        Fraction(2, 3),
    )
    assert neutral_minimum.ledger.scenario.evaluation_price == Fraction(1, 3)
    assert neutral_minimum.gap.direct == -Fraction(273, 5984)
    assert neutral_minimum.corrected_floor_periods == (1, 2)
    assert neutral_minimum.neutral_floor_periods == (1, 2, 3)
    assert neutral_minimum.differing_floor_periods == (3,)
    assert neutral_minimum.unguarded_gap is not None
    assert neutral_minimum.unguarded_gap.direct == -Fraction(373, 5984)
    assert neutral_minimum.guardrail_contribution_to_gap == Fraction(25, 1496)
    assert neutral_minimum.guardrail_contributed

    genuine_dca = result.witness(
        "smallest_genuine_cycle_corrected_vs_dca_loss_at_terminal_price"
    )
    assert genuine_dca.ledger.scenario.prices == (
        ONE,
        Fraction(2, 3),
        Fraction(2, 3),
        ONE,
    )
    assert genuine_dca.ledger.scenario.evaluation_price == ONE
    assert genuine_dca.ledger.scenario.safety_factor == HALF
    assert (
        genuine_dca.ledger.scenario.alpha,
        genuine_dca.ledger.scenario.beta,
    ) == (ZERO, -ONE)
    assert genuine_dca.gap.direct == -Fraction(49, 264)

    genuine_neutral = result.witness(
        "smallest_genuine_cycle_corrected_vs_neutral_loss_at_terminal_price"
    )
    assert genuine_neutral.ledger.scenario.prices == (
        ONE,
        Fraction(2, 3),
        ONE,
        TWO,
    )
    assert genuine_neutral.ledger.scenario.evaluation_price == TWO
    assert genuine_neutral.ledger.scenario.safety_factor == Fraction(3, 4)
    assert (
        genuine_neutral.ledger.scenario.alpha,
        genuine_neutral.ledger.scenario.beta,
    ) == (ZERO, -ONE)
    assert genuine_neutral.gap.direct == -Fraction(109, 8640)

    strict_dca = result.witness(
        "smallest_strict_cycle_corrected_vs_dca_loss_at_terminal_price"
    )
    assert strict_dca.ledger.scenario.prices == (
        ONE,
        HALF,
        Fraction(2, 3),
        ONE,
    )
    assert strict_dca.gap.direct == -Fraction(7, 32)
    assert strict_dca.differing_floor_periods == ()

    strict_neutral = result.witness(
        "smallest_strict_cycle_corrected_vs_neutral_loss_at_terminal_price"
    )
    assert strict_neutral.ledger.scenario.prices == (
        ONE,
        Fraction(2, 3),
        ONE,
        TWO,
    )
    assert strict_neutral.ledger.scenario.safety_factor == Fraction(3, 4)
    assert strict_neutral.gap.direct == -Fraction(109, 8640)
    assert strict_neutral.corrected_floor_periods == (1, 2, 3)
    assert strict_neutral.neutral_floor_periods == (1, 2, 3)
    assert strict_neutral.differing_floor_periods == (3,)
    assert strict_neutral.unguarded_gap is not None
    assert strict_neutral.unguarded_gap.direct == Fraction(49, 360)
    assert strict_neutral.guardrail_contribution_to_gap == -Fraction(257, 1728)
    assert strict_neutral.guardrail_contributed


def main():
    check_floor_disabled_counterfactual_attribution()
    check_weak_single_valley_path_boundary()
    check_four_date_enumeration_is_complete_and_deterministic()
    check_four_date_search_aggregates_both_comparisons()
    check_search_result_is_machine_readable()
    check_declared_full_search_and_named_witnesses()
    print("All weak single-valley falsification checks passed.")


if __name__ == "__main__":
    main()
