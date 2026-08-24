#!/usr/bin/env python3
"""Exact checks for the arbitrary-horizon performance boundary."""

from fractions import Fraction

from reproducibility.arbitrary_horizon import RationalScenario, evaluate_scenario
from reproducibility.cash_single_crossing import analyze_cash_mechanism
from reproducibility.performance_boundary import (
    analyze_performance_boundary,
    analyze_valley_performance_boundary,
)


ZERO = Fraction(0)
ONE = Fraction(1)


STRICT_WIN_SCENARIO = RationalScenario(
    prices=(ONE, Fraction(2, 3), Fraction(1, 2), Fraction(2, 3)),
    deposits=(ONE,) * 4,
    evaluation_price=Fraction(2, 3),
    safety_factor=Fraction(1, 4),
    alpha=ZERO,
    beta=-ONE,
)

STRICT_LOSS_SCENARIO = RationalScenario(
    prices=(ONE, Fraction(2, 3), ONE, Fraction(2)),
    deposits=(ONE,) * 4,
    evaluation_price=Fraction(2),
    safety_factor=Fraction(3, 4),
    alpha=ZERO,
    beta=-ONE,
)

STRICT_TIE_SCENARIO = RationalScenario(
    prices=(ONE, Fraction(1, 2), Fraction(2), Fraction(16)),
    deposits=(ONE,) * 4,
    evaluation_price=Fraction(16),
    safety_factor=Fraction(3, 4),
    alpha=ZERO,
    beta=-ONE,
)

ALL_FLOORS_ACTIVE_WIN_SCENARIO = RationalScenario(
    prices=(ONE, Fraction(1, 4), Fraction(1, 2), ONE),
    deposits=(ONE,) * 4,
    evaluation_price=Fraction(1, 2),
    safety_factor=Fraction(7, 8),
    alpha=ZERO,
    beta=-ONE,
)

MISALIGNED_WIN_SCENARIO = RationalScenario(
    prices=(ONE, Fraction(2, 3), Fraction(1, 2), Fraction(2, 3)),
    deposits=(ONE,) * 4,
    evaluation_price=Fraction(2, 3),
    safety_factor=Fraction(3, 4),
    alpha=ZERO,
    beta=-ONE,
)

DOUBLE_REVERSAL_SCENARIO = RationalScenario(
    prices=(ONE, Fraction(1, 16), ONE, Fraction(8)),
    deposits=(ONE,) * 4,
    evaluation_price=Fraction(8),
    safety_factor=Fraction(63, 64),
    alpha=-ONE,
    beta=ZERO,
)

FLAT_ENDPOINT_TIE_SCENARIO = RationalScenario(
    prices=(ONE, ONE, Fraction(1, 2), Fraction(1, 2)),
    deposits=(ONE,) * 4,
    evaluation_price=Fraction(1, 2),
    safety_factor=Fraction(1, 2),
    alpha=ZERO,
    beta=-ONE,
)


def check_strict_cycle_corrected_vs_dca_balance_is_exact():
    ledger = evaluate_scenario(STRICT_WIN_SCENARIO)
    report = analyze_valley_performance_boundary(ledger)
    boundary = report.corrected_vs_dca

    assert report.trough_period == 3
    assert boundary.decline_exposure == Fraction(37, 80)
    assert boundary.recovery_exposure == Fraction(31, 104)
    assert boundary.gap_at_terminal_purchase_price == Fraction(57, 520)
    assert boundary.gap_at_terminal_purchase_price == ledger.gap(
        "corrected", "dca"
    ).direct


def check_strict_cycle_corrected_vs_neutral_balance_is_exact():
    ledger = evaluate_scenario(STRICT_WIN_SCENARIO)
    boundary = analyze_valley_performance_boundary(
        ledger
    ).corrected_vs_neutral

    assert boundary.decline_exposure == -Fraction(11, 160)
    assert boundary.recovery_exposure == -Fraction(103, 832)
    assert boundary.gap_at_terminal_purchase_price == Fraction(229, 6240)
    assert boundary.gap_at_terminal_purchase_price == ledger.gap(
        "corrected", "neutral"
    ).direct


def check_evaluation_price_boundary_is_affine_and_exact():
    terminal_ledger = evaluate_scenario(STRICT_WIN_SCENARIO)
    boundary = analyze_performance_boundary(
        terminal_ledger
    ).corrected_vs_neutral
    comparison_price = ONE
    comparison_scenario = RationalScenario(
        prices=STRICT_WIN_SCENARIO.prices,
        deposits=STRICT_WIN_SCENARIO.deposits,
        evaluation_price=comparison_price,
        safety_factor=STRICT_WIN_SCENARIO.safety_factor,
        alpha=STRICT_WIN_SCENARIO.alpha,
        beta=STRICT_WIN_SCENARIO.beta,
    )

    assert boundary.terminal_cash_difference == -Fraction(103, 832)
    assert boundary.evaluation_price_intercept == -Fraction(103, 832)
    assert boundary.evaluation_price_slope == Fraction(2003, 8320)
    assert boundary.terminal_unit_difference == Fraction(2003, 8320)
    assert boundary.terminal_unit_difference == (
        terminal_ledger.corrected.steps[-1].units
        - terminal_ledger.neutral.steps[-1].units
    )
    assert boundary.break_even_evaluation_price == Fraction(1030, 2003)
    assert boundary.classification_at_evaluation_price(Fraction(1, 2)) == "loss"
    assert boundary.classification_at_evaluation_price(
        Fraction(1030, 2003)
    ) == "tie"
    assert boundary.classification_at_evaluation_price(ONE) == "win"
    assert boundary.gap_at_evaluation_price(comparison_price) == Fraction(
        973, 8320
    )
    assert boundary.gap_at_evaluation_price(comparison_price) == evaluate_scenario(
        comparison_scenario
    ).gap("corrected", "neutral").direct


def check_reference_aligned_guardrail_feedback_does_not_sign_wealth():
    win_ledger = evaluate_scenario(STRICT_WIN_SCENARIO)
    loss_ledger = evaluate_scenario(STRICT_LOSS_SCENARIO)
    win_mechanism = analyze_cash_mechanism(win_ledger)
    loss_mechanism = analyze_cash_mechanism(loss_ledger)

    assert win_mechanism.reference_aligned_guardrail_boundary == 3
    assert loss_mechanism.reference_aligned_guardrail_boundary == 2
    assert win_ledger.gap("corrected", "dca").direct == Fraction(57, 520)
    assert win_ledger.gap("corrected", "neutral").direct == Fraction(
        229, 6240
    )
    assert loss_ledger.gap("corrected", "dca").direct == -Fraction(
        1141, 2160
    )
    assert loss_ledger.gap("corrected", "neutral").direct == -Fraction(
        109, 8640
    )

    loss_boundary = analyze_valley_performance_boundary(
        loss_ledger
    ).corrected_vs_neutral
    assert loss_boundary.decline_exposure == ZERO
    assert loss_boundary.recovery_exposure == Fraction(109, 17280)


def check_affine_boundary_reconstructs_horizons_one_through_eight():
    base_path = (
        ONE,
        Fraction(3, 4),
        Fraction(1, 2),
        Fraction(1, 2),
        Fraction(2, 3),
        ONE,
        Fraction(3, 2),
        Fraction(2),
    )
    for horizon in range(1, len(base_path) + 1):
        prices = base_path[:horizon]
        for multiplier in (Fraction(1, 2), ONE, Fraction(2)):
            scenario = RationalScenario(
                prices=prices,
                deposits=(ONE,) * horizon,
                evaluation_price=multiplier * prices[-1],
                safety_factor=Fraction(1, 2),
                alpha=ZERO,
                beta=-ONE,
            )
            ledger = evaluate_scenario(scenario)
            report = analyze_performance_boundary(ledger)
            for right, boundary in (
                ("dca", report.corrected_vs_dca),
                ("neutral", report.corrected_vs_neutral),
            ):
                assert boundary.gap_at_evaluation_price(
                    scenario.evaluation_price
                ) == ledger.gap("corrected", right).direct


def check_affine_boundary_accepts_non_valley_paths():
    scenario = RationalScenario(
        prices=(ONE, Fraction(1, 2), ONE, Fraction(2, 3), Fraction(3, 2)),
        deposits=(ONE,) * 5,
        evaluation_price=Fraction(7, 5),
        safety_factor=Fraction(1, 2),
        alpha=ZERO,
        beta=-ONE,
    )
    ledger = evaluate_scenario(scenario)
    report = analyze_performance_boundary(ledger)

    for right, boundary in (
        ("dca", report.corrected_vs_dca),
        ("neutral", report.corrected_vs_neutral),
    ):
        assert boundary.gap_at_evaluation_price(
            scenario.evaluation_price
        ) == ledger.gap("corrected", right).direct

    try:
        analyze_valley_performance_boundary(ledger)
    except ValueError:
        pass
    else:
        raise AssertionError("the valley specialization accepted a double valley")


def check_endpoint_troughs_flat_troughs_and_constant_paths():
    paths = {
        "constant": (ONE, ONE, ONE, ONE),
        "endpoint_decline": (ONE, Fraction(3, 4), Fraction(1, 2)),
        "endpoint_recovery": (ONE, Fraction(3, 2), Fraction(2)),
        "flat_trough": (ONE, Fraction(1, 2), Fraction(1, 2), ONE),
    }
    ledgers = {
        name: evaluate_scenario(
            RationalScenario(
                prices=prices,
                deposits=(ONE,) * len(prices),
                evaluation_price=prices[-1],
                safety_factor=Fraction(1, 2),
                alpha=ZERO,
                beta=-ONE,
            )
        )
        for name, prices in paths.items()
    }

    constant = analyze_valley_performance_boundary(ledgers["constant"])
    assert constant.corrected_vs_dca.gap_at_terminal_purchase_price == ZERO
    assert constant.corrected_vs_neutral.gap_at_terminal_purchase_price == ZERO

    decline = analyze_valley_performance_boundary(ledgers["endpoint_decline"])
    assert decline.trough_period == 3
    assert decline.corrected_vs_dca.recovery_exposure == ZERO
    assert decline.corrected_vs_dca.gap_at_terminal_purchase_price > ZERO

    recovery = analyze_valley_performance_boundary(
        ledgers["endpoint_recovery"]
    )
    assert recovery.trough_period == 1
    assert recovery.corrected_vs_dca.decline_exposure == ZERO
    assert recovery.corrected_vs_dca.gap_at_terminal_purchase_price < ZERO

    flat = analyze_valley_performance_boundary(ledgers["flat_trough"])
    assert flat.trough_period == 2
    assert flat.corrected_vs_dca.evaluation.gap_at_evaluation_price(
        ONE
    ) == ledgers["flat_trough"].gap("corrected", "dca").direct


def check_exact_tie_and_floor_branches_remain_visible():
    tie_ledger = evaluate_scenario(STRICT_TIE_SCENARIO)
    tie_mechanism = analyze_cash_mechanism(tie_ledger)
    tie_boundary = analyze_valley_performance_boundary(
        tie_ledger
    ).corrected_vs_neutral

    assert tie_mechanism.reference_aligned_guardrail_boundary == 2
    assert tie_boundary.gap_at_terminal_purchase_price == ZERO
    assert tie_boundary.evaluation.break_even_evaluation_price == Fraction(16)
    assert tie_boundary.recovery_exposure == ZERO

    win_ledger = evaluate_scenario(STRICT_WIN_SCENARIO)
    loss_ledger = evaluate_scenario(STRICT_LOSS_SCENARIO)
    assert tuple(step.floor_active for step in win_ledger.corrected.steps) == (
        True,
        False,
        False,
        False,
    )
    assert tuple(step.floor_active for step in loss_ledger.corrected.steps) == (
        True,
        True,
        True,
        False,
    )


def check_all_floors_active_strict_win_region_is_nonempty():
    ledger = evaluate_scenario(ALL_FLOORS_ACTIVE_WIN_SCENARIO)
    mechanism = analyze_cash_mechanism(ledger)
    report = analyze_performance_boundary(ledger)

    assert mechanism.reference_aligned_guardrail_boundary == 2
    assert all(step.floor_active is True for step in ledger.corrected.steps)
    assert all(step.floor_active is True for step in ledger.neutral.steps)
    assert ledger.gap("corrected", "dca").direct == Fraction(12017, 57600)
    assert ledger.gap("corrected", "neutral").direct == Fraction(
        30293, 230400
    )

    dca_boundary = report.corrected_vs_dca
    neutral_boundary = report.corrected_vs_neutral
    assert (
        dca_boundary.terminal_cash_difference,
        dca_boundary.terminal_unit_difference,
        dca_boundary.break_even_evaluation_price,
    ) == (
        Fraction(16807, 28800),
        -Fraction(7199, 9600),
        Fraction(16807, 21597),
    )
    assert (
        neutral_boundary.terminal_cash_difference,
        neutral_boundary.terminal_unit_difference,
        neutral_boundary.break_even_evaluation_price,
    ) == (
        Fraction(22903, 115200),
        -Fraction(5171, 38400),
        Fraction(22903, 15513),
    )
    assert ALL_FLOORS_ACTIVE_WIN_SCENARIO.evaluation_price < min(
        dca_boundary.break_even_evaluation_price,
        neutral_boundary.break_even_evaluation_price,
    )

    high_price = RationalScenario(
        prices=ALL_FLOORS_ACTIVE_WIN_SCENARIO.prices,
        deposits=ALL_FLOORS_ACTIVE_WIN_SCENARIO.deposits,
        evaluation_price=Fraction(2),
        safety_factor=ALL_FLOORS_ACTIVE_WIN_SCENARIO.safety_factor,
        alpha=ALL_FLOORS_ACTIVE_WIN_SCENARIO.alpha,
        beta=ALL_FLOORS_ACTIVE_WIN_SCENARIO.beta,
    )
    high_ledger = evaluate_scenario(high_price)
    assert high_ledger.gap("corrected", "dca").direct == -Fraction(
        26387, 28800
    )
    assert high_ledger.gap("corrected", "neutral").direct == -Fraction(
        8123, 115200
    )


def check_alignment_and_terminal_positive_cash_are_not_necessary():
    ledger = evaluate_scenario(MISALIGNED_WIN_SCENARIO)
    mechanism = analyze_cash_mechanism(ledger)
    boundary = analyze_performance_boundary(ledger).corrected_vs_neutral

    assert mechanism.reference_aligned_guardrail_boundary is None
    assert (
        boundary.terminal_cash_difference,
        boundary.terminal_unit_difference,
    ) == (
        Fraction(841, 149760),
        Fraction(841, 99840),
    )
    assert boundary.break_even_evaluation_price is None
    assert ledger.gap("corrected", "dca").direct == Fraction(389, 18720)
    assert ledger.gap("corrected", "neutral").direct == Fraction(841, 74880)

    terminal_negative = analyze_performance_boundary(
        evaluate_scenario(STRICT_WIN_SCENARIO)
    ).corrected_vs_neutral
    assert terminal_negative.terminal_cash_difference < ZERO
    assert terminal_negative.classification_at_evaluation_price(
        STRICT_WIN_SCENARIO.evaluation_price
    ) == "win"


def check_flat_endpoint_tie_and_outside_alignment_failure_are_exact():
    flat_ledger = evaluate_scenario(FLAT_ENDPOINT_TIE_SCENARIO)
    flat_boundary = analyze_performance_boundary(
        flat_ledger
    ).corrected_vs_neutral
    assert (
        flat_boundary.terminal_cash_difference,
        flat_boundary.terminal_unit_difference,
        flat_boundary.break_even_evaluation_price,
    ) == (
        -Fraction(59, 240),
        Fraction(59, 120),
        Fraction(1, 2),
    )
    assert flat_ledger.gap("corrected", "neutral").direct == ZERO
    assert flat_ledger.gap("corrected", "dca").direct == Fraction(1, 4)

    reversal_ledger = evaluate_scenario(DOUBLE_REVERSAL_SCENARIO)
    reversal_mechanism = analyze_cash_mechanism(reversal_ledger)
    assert reversal_mechanism.reference_aligned_guardrail_boundary is None
    assert reversal_mechanism.cash_sign_change_periods == (3, 4)
    assert reversal_ledger.gap("corrected", "neutral").direct == -Fraction(
        339578505, 616865792
    )


def check_lambda_one_collapses_every_boundary_to_zero():
    scenario = RationalScenario(
        prices=(ONE, Fraction(2, 3), Fraction(1, 2), Fraction(2)),
        deposits=(ONE,) * 4,
        evaluation_price=Fraction(3),
        safety_factor=ONE,
        alpha=ZERO,
        beta=-ONE,
    )
    ledger = evaluate_scenario(scenario)
    report = analyze_performance_boundary(ledger)

    for policy in (ledger.corrected, ledger.neutral):
        assert tuple(step.purchase for step in policy.steps) == (ONE,) * 4
        assert tuple(step.cash for step in policy.steps) == (ZERO,) * 4
        assert policy.terminal_wealth == ledger.dca.terminal_wealth
    for boundary in (report.corrected_vs_dca, report.corrected_vs_neutral):
        assert boundary.cash_differences == (ZERO,) * 4
        assert boundary.evaluation_price_intercept == ZERO
        assert boundary.evaluation_price_slope == ZERO
        assert boundary.gap_at_evaluation_price(Fraction(3)) == ZERO


def main():
    check_strict_cycle_corrected_vs_dca_balance_is_exact()
    check_strict_cycle_corrected_vs_neutral_balance_is_exact()
    check_evaluation_price_boundary_is_affine_and_exact()
    check_reference_aligned_guardrail_feedback_does_not_sign_wealth()
    check_affine_boundary_reconstructs_horizons_one_through_eight()
    check_affine_boundary_accepts_non_valley_paths()
    check_endpoint_troughs_flat_troughs_and_constant_paths()
    check_exact_tie_and_floor_branches_remain_visible()
    check_all_floors_active_strict_win_region_is_nonempty()
    check_alignment_and_terminal_positive_cash_are_not_necessary()
    check_flat_endpoint_tie_and_outside_alignment_failure_are_exact()
    check_lambda_one_collapses_every_boundary_to_zero()
    print("All arbitrary-horizon performance-boundary checks passed.")


if __name__ == "__main__":
    main()
