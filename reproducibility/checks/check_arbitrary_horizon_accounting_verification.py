#!/usr/bin/env python3
"""Exact end-to-end checks for the arbitrary-horizon scenario seam."""

from fractions import Fraction

from reproducibility.arbitrary_horizon import (
    ExactRationalError,
    RationalScenario,
    evaluate_scenario,
)


ZERO = Fraction(0)
HALF = Fraction(1, 2)
ONE = Fraction(1)


def check_one_purchase_exact_ledger():
    ledger = evaluate_scenario(
        RationalScenario(
            prices=(ONE,),
            deposits=(Fraction(2),),
            evaluation_price=Fraction(3),
            safety_factor=HALF,
            alpha=ZERO,
            beta=ZERO,
        )
    )

    corrected = ledger.corrected.steps[0]
    assert (
        corrected.reference,
        corrected.relative_price,
        corrected.score,
        corrected.guardrail_floor,
        corrected.floor_active,
        corrected.purchase,
        corrected.cash,
        corrected.units,
    ) == (None, ONE, HALF, ONE, True, Fraction(3, 2), HALF, Fraction(3, 2))

    assert ledger.dca.steps[0].purchase == Fraction(2)
    assert ledger.neutral.steps[0] == corrected

    gap = ledger.gap("corrected", "dca")
    assert (gap.direct, gap.cash_timing) == (-ONE, -ONE)


def check_two_purchase_corrected_neutral_flip():
    ledger = evaluate_scenario(
        RationalScenario(
            prices=(ONE, Fraction(2)),
            deposits=(ONE, ONE),
            evaluation_price=Fraction(3, 2),
            safety_factor=HALF,
            alpha=ZERO,
            beta=ZERO,
        )
    )

    corrected = ledger.corrected.steps[1]
    assert (
        corrected.reference,
        corrected.relative_price,
        corrected.score,
        corrected.guardrail_floor,
        corrected.floor_active,
        corrected.purchase,
        corrected.cash,
        corrected.units,
        corrected.coverage_after,
    ) == (
        ONE,
        Fraction(2),
        Fraction(1, 3),
        ZERO,
        False,
        Fraction(5, 12),
        Fraction(5, 6),
        Fraction(23, 24),
        Fraction(5, 24),
    )

    neutral = ledger.neutral.steps[1]
    assert (neutral.score, neutral.purchase, neutral.cash, neutral.units) == (
        HALF,
        Fraction(5, 8),
        Fraction(5, 8),
        Fraction(17, 16),
    )

    corrected_gap = ledger.gap("corrected", "dca")
    neutral_gap = ledger.gap("neutral", "dca")
    assert (corrected_gap.direct, corrected_gap.cash_timing) == (
        Fraction(1, 48),
        Fraction(1, 48),
    )
    assert (neutral_gap.direct, neutral_gap.cash_timing) == (
        -Fraction(1, 32),
        -Fraction(1, 32),
    )
    assert corrected_gap.classification == "win"
    assert neutral_gap.classification == "loss"


def check_two_purchase_win_tie_loss_and_all_win():
    common = {
        "prices": (ONE, ONE),
        "deposits": (ONE, ONE),
        "safety_factor": HALF,
        "alpha": ZERO,
        "beta": ZERO,
    }
    win = evaluate_scenario(
        RationalScenario(evaluation_price=HALF, **common)
    ).gap("corrected", "dca")
    tie = evaluate_scenario(
        RationalScenario(evaluation_price=ONE, **common)
    ).gap("corrected", "dca")
    loss = evaluate_scenario(
        RationalScenario(evaluation_price=Fraction(2), **common)
    ).gap("corrected", "dca")
    assert (win.direct, win.classification) == (Fraction(1, 4), "win")
    assert (tie.direct, tie.classification) == (ZERO, "tie")
    assert (loss.direct, loss.classification) == (-HALF, "loss")

    all_win = evaluate_scenario(
        RationalScenario(
            prices=(ONE, HALF),
            deposits=(ONE, ZERO),
            evaluation_price=Fraction(500),
            safety_factor=HALF,
            alpha=ZERO,
            beta=ZERO,
        )
    )
    all_win_gap = all_win.gap("corrected", "dca")
    assert all_win.corrected.steps[-1].cash == Fraction(1, 12)
    assert (all_win_gap.direct, all_win_gap.cash_timing) == (
        Fraction(167, 4),
        Fraction(167, 4),
    )
    assert all_win_gap.classification == "win"


def check_three_purchase_beta_flip_witness():
    common = {
        "prices": (ONE, Fraction(4), Fraction(2)),
        "deposits": (ONE, ONE, ONE),
        "evaluation_price": Fraction(7, 3),
        "safety_factor": HALF,
        "alpha": ZERO,
    }
    low = evaluate_scenario(RationalScenario(beta=-ONE, **common))
    high = evaluate_scenario(RationalScenario(beta=ONE, **common))

    assert tuple(step.purchase for step in low.corrected.steps[:2]) == (
        Fraction(3, 4),
        Fraction(1, 4),
    )
    assert low.corrected.steps[:2] == high.corrected.steps[:2]

    low_third = low.corrected.steps[2]
    high_third = high.corrected.steps[2]
    assert (
        low_third.reference,
        low_third.relative_price,
        low_third.score,
        low_third.guardrail_floor,
        low_third.floor_active,
        low_third.purchase,
        low_third.cash,
    ) == (
        Fraction(8, 5),
        Fraction(5, 4),
        Fraction(4, 9),
        Fraction(1, 8),
        True,
        Fraction(23, 24),
        Fraction(25, 24),
    )
    assert (
        high_third.reference,
        high_third.relative_price,
        high_third.score,
        high_third.guardrail_floor,
        high_third.floor_active,
        high_third.purchase,
        high_third.cash,
    ) == (
        Fraction(5, 2),
        Fraction(4, 5),
        Fraction(5, 9),
        Fraction(1, 8),
        True,
        Fraction(7, 6),
        Fraction(5, 6),
    )

    low_gap = low.gap("corrected", "dca")
    high_gap = high.gap("corrected", "dca")
    assert (low_gap.direct, low_gap.cash_timing) == (
        -Fraction(1, 36),
        -Fraction(1, 36),
    )
    assert (high_gap.direct, high_gap.cash_timing) == (
        Fraction(1, 144),
        Fraction(1, 144),
    )

    assert tuple(step.purchase for step in low.neutral.steps) == tuple(
        step.purchase for step in high.neutral.steps
    )
    neutral_gap = low.gap("neutral", "dca")
    assert (neutral_gap.direct, neutral_gap.cash_timing) == (
        -Fraction(5, 24),
        -Fraction(5, 24),
    )


def check_three_purchase_diagonal_reference():
    ledger = evaluate_scenario(
        RationalScenario(
            prices=(ONE, Fraction(4), Fraction(2)),
            deposits=(ONE, ONE, ONE),
            evaluation_price=Fraction(7, 3),
            safety_factor=HALF,
            alpha=ZERO,
            beta=ZERO,
        )
    )

    third = ledger.corrected.steps[2]
    assert (
        third.reference,
        third.relative_price,
        third.score,
        third.purchase,
        third.cash,
    ) == (
        Fraction(2),
        ONE,
        HALF,
        Fraction(17, 16),
        Fraction(15, 16),
    )
    gap = ledger.gap("corrected", "dca")
    assert (gap.direct, gap.cash_timing) == (
        -Fraction(1, 96),
        -Fraction(1, 96),
    )


def check_fractional_parameters_remain_exact():
    ledger = evaluate_scenario(
        RationalScenario(
            prices=(ONE, Fraction(4), Fraction(8)),
            deposits=(ONE, ONE, ONE),
            evaluation_price=Fraction(8),
            safety_factor=HALF,
            alpha=HALF,
            beta=-HALF,
        )
    )

    third = ledger.corrected.steps[2]
    assert (third.reference, third.relative_price, third.score) == (
        Fraction(2),
        Fraction(4),
        Fraction(1, 3),
    )
    gap = ledger.gap("corrected", "dca")
    assert gap.direct == gap.cash_timing


def check_final_rational_references_survive_irrational_terms():
    diagonal = evaluate_scenario(
        RationalScenario(
            prices=(ONE, Fraction(4), Fraction(2), Fraction(2)),
            deposits=(ONE,) * 4,
            evaluation_price=Fraction(2),
            safety_factor=HALF,
            alpha=ZERO,
            beta=ZERO,
        )
    )
    assert diagonal.corrected.steps[3].reference == Fraction(2)

    off_diagonal = evaluate_scenario(
        RationalScenario(
            prices=(ONE, Fraction(4), Fraction(2), Fraction(2)),
            deposits=(ONE,) * 4,
            evaluation_price=Fraction(2),
            safety_factor=HALF,
            alpha=HALF,
            beta=-HALF,
        )
    )
    assert off_diagonal.corrected.steps[3].reference == Fraction(2)


def check_invalid_and_nonrational_scenarios_are_rejected():
    invalid_cases = (
        (
            ValueError,
            "nonempty",
            lambda: RationalScenario((), (), ONE, HALF, ZERO, ZERO),
        ),
        (
            ValueError,
            "equal length",
            lambda: RationalScenario((ONE,), (ONE, ONE), ONE, HALF, ZERO, ZERO),
        ),
        (
            ValueError,
            "positive",
            lambda: RationalScenario((ZERO,), (ONE,), ONE, HALF, ZERO, ZERO),
        ),
        (
            ValueError,
            "nonnegative",
            lambda: RationalScenario((ONE,), (-ONE,), ONE, HALF, ZERO, ZERO),
        ),
        (
            ValueError,
            "evaluation_price",
            lambda: RationalScenario((ONE,), (ONE,), ZERO, HALF, ZERO, ZERO),
        ),
        (
            ValueError,
            "safety_factor",
            lambda: RationalScenario((ONE,), (ONE,), ONE, ZERO, ZERO, ZERO),
        ),
        (
            TypeError,
            "Fraction",
            lambda: RationalScenario((1.0,), (ONE,), ONE, HALF, ZERO, ZERO),
        ),
    )
    for error_type, message, build in invalid_cases:
        try:
            build()
        except error_type as error:
            assert message in str(error)
        else:
            raise AssertionError(f"expected {error_type.__name__}: {message}")

    irrational = RationalScenario(
        prices=(ONE, Fraction(2), ONE),
        deposits=(ONE, ONE, ONE),
        evaluation_price=ONE,
        safety_factor=HALF,
        alpha=ZERO,
        beta=ZERO,
    )
    try:
        evaluate_scenario(irrational)
    except ExactRationalError as error:
        assert "exact-rational" in str(error)
    else:
        raise AssertionError("an irrational corrected reference must not be rounded")


def check_five_purchase_repeated_floor_and_constant_price_identity():
    ledger = evaluate_scenario(
        RationalScenario(
            prices=(ONE,) * 5,
            deposits=(ONE,) * 5,
            evaluation_price=ONE,
            safety_factor=HALF,
            alpha=ZERO,
            beta=-ONE,
        )
    )

    corrected = ledger.corrected
    assert tuple(step.floor_active for step in corrected.steps) == (
        True,
        True,
        False,
        False,
        False,
    )
    assert tuple(step.guardrail_floor for step in corrected.steps) == (
        HALF,
        Fraction(1, 4),
        ZERO,
        ZERO,
        ZERO,
    )
    assert tuple(step.score for step in corrected.steps) == (HALF,) * 5
    assert corrected.terminal_wealth == Fraction(5)
    assert corrected.cash_timing_wealth == Fraction(5)
    assert corrected.cash_timing_terms == (ZERO,) * 5

    for left, right in (
        ("corrected", "dca"),
        ("neutral", "dca"),
        ("corrected", "neutral"),
    ):
        gap = ledger.gap(left, right)
        assert (gap.direct, gap.cash_timing) == (ZERO, ZERO)


def check_six_purchase_nonconstant_identity():
    ledger = evaluate_scenario(
        RationalScenario(
            prices=(
                ONE,
                Fraction(4),
                Fraction(2),
                Fraction(3),
                Fraction(3, 2),
                Fraction(6),
            ),
            deposits=(ONE, ZERO, Fraction(2), ONE, ZERO, Fraction(3)),
            evaluation_price=Fraction(5, 2),
            safety_factor=Fraction(3, 4),
            alpha=ZERO,
            beta=-ONE,
        )
    )

    for policy in (ledger.dca, ledger.corrected, ledger.neutral):
        assert policy.terminal_wealth == policy.cash_timing_wealth
        assert all(step.cash >= ZERO for step in policy.steps)
        assert all(step.units >= ZERO for step in policy.steps)

    for policy in (ledger.corrected, ledger.neutral):
        assert all(
            step.guardrail_floor <= step.purchase <= step.available_cash
            for step in policy.steps
        )
        assert all(step.coverage_after >= ZERO for step in policy.steps)

    for left, right in (
        ("corrected", "dca"),
        ("neutral", "dca"),
        ("corrected", "neutral"),
    ):
        gap = ledger.gap(left, right)
        assert gap.direct == gap.cash_timing


def check_zero_deposits_and_lambda_one_collapse():
    zero_deposits = evaluate_scenario(
        RationalScenario(
            prices=(ONE, Fraction(2), Fraction(4)),
            deposits=(ZERO, ZERO, ZERO),
            evaluation_price=Fraction(3),
            safety_factor=HALF,
            alpha=ZERO,
            beta=-ONE,
        )
    )
    for policy in (zero_deposits.dca, zero_deposits.corrected, zero_deposits.neutral):
        assert policy.terminal_wealth == ZERO
        assert all(step.purchase == step.cash == step.units == ZERO for step in policy.steps)

    collapsed = evaluate_scenario(
        RationalScenario(
            prices=(ONE, Fraction(4), Fraction(2)),
            deposits=(Fraction(2), Fraction(3), Fraction(4)),
            evaluation_price=Fraction(11, 5),
            safety_factor=ONE,
            alpha=ZERO,
            beta=-ONE,
        )
    )
    dca_purchases = tuple(step.purchase for step in collapsed.dca.steps)
    assert tuple(step.purchase for step in collapsed.corrected.steps) == dca_purchases
    assert tuple(step.purchase for step in collapsed.neutral.steps) == dca_purchases
    assert all(
        collapsed.gap(policy, "dca").classification == "tie"
        for policy in ("corrected", "neutral")
    )

    irrational_reference_boundaries = (
        (ZERO, ZERO, ZERO),
        (ONE, ONE, ONE),
    )
    for deposits in irrational_reference_boundaries:
        boundary = evaluate_scenario(
            RationalScenario(
                prices=(ONE, Fraction(2), ONE),
                deposits=deposits,
                evaluation_price=ONE,
                safety_factor=ONE,
                alpha=ZERO,
                beta=ZERO,
            )
        )
        assert tuple(step.purchase for step in boundary.corrected.steps) == deposits
        assert boundary.corrected.steps[2].reference is None
        assert boundary.corrected.steps[2].relative_price is None
        assert boundary.corrected.steps[2].score is None
        assert boundary.gap("corrected", "dca").classification == "tie"


def main():
    check_one_purchase_exact_ledger()
    check_two_purchase_corrected_neutral_flip()
    check_two_purchase_win_tie_loss_and_all_win()
    check_three_purchase_beta_flip_witness()
    check_three_purchase_diagonal_reference()
    check_fractional_parameters_remain_exact()
    check_final_rational_references_survive_irrational_terms()
    check_invalid_and_nonrational_scenarios_are_rejected()
    check_five_purchase_repeated_floor_and_constant_price_identity()
    check_six_purchase_nonconstant_identity()
    check_zero_deposits_and_lambda_one_collapse()
    print("All exact arbitrary-horizon accounting seam checks passed.")


if __name__ == "__main__":
    main()
