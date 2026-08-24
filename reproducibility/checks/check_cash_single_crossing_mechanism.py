#!/usr/bin/env python3
"""Exact checks for the guarded cash single-crossing mechanism."""

import json

from fractions import Fraction

from reproducibility.arbitrary_horizon import RationalScenario, evaluate_scenario
from reproducibility.cash_single_crossing import analyze_cash_mechanism
from reproducibility.cash_single_crossing_search import (
    DEFAULT_CASH_CROSSING_GRID,
    CashCrossingSearchResult,
    render_json,
    run_cash_crossing_search,
)
from reproducibility.weak_single_valley_search import DEFAULT_GRID


ZERO = Fraction(0)
ONE = Fraction(1)


STRICT_DOUBLE_REVERSAL_SCENARIO = RationalScenario(
    prices=(ONE, Fraction(1, 16), ONE, Fraction(8)),
    deposits=(ONE,) * 4,
    evaluation_price=Fraction(8),
    safety_factor=Fraction(63, 64),
    alpha=-ONE,
    beta=ZERO,
)


def check_strict_cycle_cash_path_has_two_sign_changes():
    report = analyze_cash_mechanism(
        evaluate_scenario(STRICT_DOUBLE_REVERSAL_SCENARIO)
    )

    assert report.trough_period == 2
    assert report.cash_differences == (
        ZERO,
        -Fraction(12495, 1052672),
        Fraction(174032415, 616865792),
        -Fraction(142575068237, 2843751301120),
    )
    assert report.cash_sign_change_periods == (3, 4)
    assert not report.has_cash_single_crossing


def check_floor_feedback_isolates_the_second_reversal():
    guarded = analyze_cash_mechanism(
        evaluate_scenario(STRICT_DOUBLE_REVERSAL_SCENARIO)
    )
    unguarded = analyze_cash_mechanism(
        evaluate_scenario(
            STRICT_DOUBLE_REVERSAL_SCENARIO,
            guardrail_enabled=False,
        )
    )

    assert guarded.reference_crossing_boundary == 2
    assert guarded.reference_aligned_guardrail_boundary is None
    assert guarded.floor_differences == (
        ZERO,
        ZERO,
        -Fraction(12495, 65792),
        Fraction(64201365, 77108224),
    )
    assert guarded.steps[3].floor_component == -Fraction(115562457, 138855044)
    assert all(
        step.cash_difference
        == step.carry_component + step.score_component + step.floor_component
        for step in guarded.steps
    )

    assert unguarded.reference_crossing_boundary == 2
    assert unguarded.reference_aligned_guardrail_boundary == 2
    assert unguarded.cash_differences == (
        ZERO,
        -Fraction(765, 1028),
        Fraction(70545, 602408),
        Fraction(585268881, 555420176),
    )
    assert unguarded.cash_sign_change_periods == (3,)
    assert unguarded.has_cash_single_crossing


def check_common_floors_give_a_nonempty_strict_single_crossing_class():
    scenario = RationalScenario(
        prices=(ONE, Fraction(1, 2), Fraction(2, 3), ONE),
        deposits=(ONE,) * 4,
        evaluation_price=ONE,
        safety_factor=Fraction(1, 2),
        alpha=ZERO,
        beta=-ONE,
    )

    report = analyze_cash_mechanism(evaluate_scenario(scenario))

    assert report.reference_crossing_boundary == 2
    assert report.reference_aligned_guardrail_boundary == 2
    assert report.retention_differences == (
        ZERO,
        -Fraction(1, 6),
        ZERO,
        Fraction(1, 10),
    )
    assert report.floor_differences == (ZERO,) * 4
    assert report.cash_differences == (
        ZERO,
        -Fraction(7, 48),
        -Fraction(7, 96),
        Fraction(41, 320),
    )
    assert report.cash_sign_change_periods == (4,)
    assert report.has_cash_single_crossing


def check_diagonal_reference_boundary_is_exact():
    scenario = RationalScenario(
        prices=(ONE, Fraction(1, 4), Fraction(1, 2), ONE),
        deposits=(ONE,) * 4,
        evaluation_price=ONE,
        safety_factor=Fraction(1, 2),
        alpha=ZERO,
        beta=ZERO,
    )

    ledger = evaluate_scenario(scenario)
    report = analyze_cash_mechanism(ledger)

    assert tuple(step.reference for step in ledger.corrected.steps) == (
        None,
        ONE,
        Fraction(1, 2),
        Fraction(1, 2),
    )
    assert report.retention_differences == (
        ZERO,
        -Fraction(3, 10),
        ZERO,
        Fraction(1, 6),
    )
    assert report.reference_aligned_guardrail_boundary == 2
    assert report.cash_differences == (
        ZERO,
        -Fraction(39, 160),
        -Fraction(39, 320),
        Fraction(389, 1920),
    )


def check_reference_aligned_guardrail_class_has_strict_interior():
    scenario = RationalScenario(
        prices=(ONE, Fraction(1, 4), Fraction(1, 2), ONE),
        deposits=(ONE,) * 4,
        evaluation_price=ONE,
        safety_factor=Fraction(7, 8),
        alpha=ZERO,
        beta=-ONE,
    )

    ledger = evaluate_scenario(scenario)
    report = analyze_cash_mechanism(ledger)

    assert report.reference_aligned_guardrail_boundary == 2
    assert tuple(
        step.raw_guardrail_floor for step in ledger.corrected.steps
    ) == (
        Fraction(7, 8),
        Fraction(55, 64),
        Fraction(11, 20),
        Fraction(79, 180),
    )
    assert tuple(
        step.raw_guardrail_floor for step in ledger.neutral.steps
    ) == (
        Fraction(7, 8),
        Fraction(55, 64),
        Fraction(43, 64),
        Fraction(57, 128),
    )
    assert all(step.floor_active is True for step in ledger.corrected.steps)
    assert all(step.floor_active is True for step in ledger.neutral.steps)
    assert report.retention_differences == (
        ZERO,
        -Fraction(3, 10),
        Fraction(1, 18),
        Fraction(1, 5),
    )
    assert report.floor_differences == (
        ZERO,
        ZERO,
        -Fraction(39, 320),
        -Fraction(37, 5760),
    )
    assert report.cash_differences == (
        ZERO,
        -Fraction(39, 640),
        Fraction(133, 2304),
        Fraction(22903, 115200),
    )
    assert report.has_cash_single_crossing


def check_guardrail_alignment_is_not_necessary():
    scenario = RationalScenario(
        prices=(ONE, Fraction(2, 3), Fraction(1, 2), Fraction(2, 3)),
        deposits=(ONE,) * 4,
        evaluation_price=Fraction(2, 3),
        safety_factor=Fraction(3, 4),
        alpha=ZERO,
        beta=-ONE,
    )

    report = analyze_cash_mechanism(evaluate_scenario(scenario))

    assert report.reference_crossing_boundary == 3
    assert report.reference_aligned_guardrail_boundary is None
    assert report.floor_differences == (
        ZERO,
        ZERO,
        -Fraction(11, 320),
        -Fraction(1699, 18720),
    )
    assert report.steps[2].carry_component == -Fraction(11, 624)
    assert report.steps[2].score_component == -Fraction(125, 1664)
    assert report.steps[2].floor_component == Fraction(11, 832)
    assert (
        report.steps[2].score_component + report.steps[2].floor_component
        == -Fraction(103, 1664)
    )
    assert report.cash_differences == (
        ZERO,
        -Fraction(11, 240),
        -Fraction(397, 4992),
        Fraction(841, 149760),
    )
    assert report.has_cash_single_crossing


def check_declared_grid_minimizes_exact_crossing_witnesses(
    result: CashCrossingSearchResult,
):

    assert result.path_count == 559
    assert result.scenario_count == 11739
    assert result.exact_domain_rejections == 0
    assert result.multiple_sign_change_count == 27
    assert result.valley_aligned_single_crossing_failure_count == 115
    assert result.genuine_cycle_multiple_sign_change_count == 25
    assert result.strict_cycle_multiple_sign_change_count == 25
    assert result.reference_aligned_guardrail_count == 5371
    assert result.reference_aligned_guardrail_failures == 0
    assert result.grid.safety_factors == (
        Fraction(1, 2),
        Fraction(1, 4),
        Fraction(3, 4),
        Fraction(7, 8),
        Fraction(15, 16),
        Fraction(31, 32),
        Fraction(63, 64),
    )

    minimum = result.witness("smallest_multiple_cash_sign_changes")
    assert minimum.ledger.scenario.prices == (
        ONE,
        Fraction(2),
        Fraction(32),
        Fraction(32),
    )
    assert minimum.ledger.scenario.safety_factor == Fraction(31, 32)
    assert (minimum.ledger.scenario.alpha, minimum.ledger.scenario.beta) == (
        -ONE,
        ZERO,
    )
    assert minimum.report.cash_sign_change_periods == (3, 4)
    assert minimum.report.cash_differences == (
        ZERO,
        Fraction(3, 128),
        -Fraction(665, 147712),
        Fraction(3183, 308480),
    )

    genuine = result.witness(
        "smallest_genuine_cycle_multiple_cash_sign_changes"
    )

    strict = result.witness(
        "smallest_strict_cycle_multiple_cash_sign_changes"
    )
    assert strict.ledger.scenario.prices == (
        ONE,
        Fraction(1, 16),
        ONE,
        Fraction(8),
    )
    assert strict.ledger.scenario.safety_factor == Fraction(63, 64)
    assert (strict.ledger.scenario.alpha, strict.ledger.scenario.beta) == (
        -ONE,
        ZERO,
    )
    assert strict.report.cash_sign_change_periods == (3, 4)
    assert strict.unguarded_report.cash_sign_change_periods == (3,)
    assert genuine.ledger.scenario == strict.ledger.scenario
    assert genuine.report.cash_differences == strict.report.cash_differences


def check_search_result_is_machine_readable(result: CashCrossingSearchResult):
    payload = json.loads(render_json(result))

    assert payload["path_count"] == 559
    assert payload["scenario_count"] == 11739
    assert payload["multiple_sign_change_count"] == 27
    assert payload["reference_aligned_guardrail_count"] == 5371
    assert payload["reference_aligned_guardrail_failures"] == 0
    assert payload["grid"]["safety_factors"][:3] == [
        "1/2",
        "1/4",
        "3/4",
    ]
    strict = payload["witnesses"][
        "smallest_strict_cycle_multiple_cash_sign_changes"
    ]
    assert strict["prices"] == ["1", "1/16", "1", "8"]
    assert strict["cash_sign_change_periods"] == [3, 4]
    assert strict["unguarded_cash_sign_change_periods"] == [3]
    assert "not proof" in payload["scope_limit"]


def check_ticket_02_grid_survival_is_reproduced():
    result = run_cash_crossing_search(DEFAULT_GRID)

    assert result.path_count == 2274
    assert result.scenario_count == 20466
    assert result.exact_domain_rejections == 0
    assert result.multiple_sign_change_count == 0
    assert result.valley_aligned_single_crossing_failure_count == 0


def main():
    check_strict_cycle_cash_path_has_two_sign_changes()
    check_floor_feedback_isolates_the_second_reversal()
    check_common_floors_give_a_nonempty_strict_single_crossing_class()
    check_diagonal_reference_boundary_is_exact()
    check_reference_aligned_guardrail_class_has_strict_interior()
    check_guardrail_alignment_is_not_necessary()
    result = run_cash_crossing_search(DEFAULT_CASH_CROSSING_GRID)
    check_declared_grid_minimizes_exact_crossing_witnesses(result)
    check_search_result_is_machine_readable(result)
    check_ticket_02_grid_survival_is_reproduced()
    print("All cash single-crossing mechanism checks passed.")


if __name__ == "__main__":
    main()
