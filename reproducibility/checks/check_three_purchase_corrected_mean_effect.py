#!/usr/bin/env python3
"""Exact checks for the first beta-sensitive three-purchase DCA boundary."""

from fractions import Fraction
from itertools import product
from math import isqrt


ZERO = Fraction(0)
HALF = Fraction(1, 2)
ONE = Fraction(1)


def sign(value):
    return (value > 0) - (value < 0)


def extended_threshold(cash, shift):
    denominator = cash - shift
    return cash / denominator if denominator > 0 else None


def threshold_sign(evaluation_ratio, threshold):
    if threshold is None:
        return 1
    return sign(threshold - evaluation_ratio)


def guarded_three_purchase(
    safety_factor,
    deposits,
    second_price_ratio,
    third_over_second_ratio,
    evaluation_ratio,
    second_score,
    third_score,
):
    """Evaluate the guarded rule and its exact three-date reduction."""
    first_deposit, second_deposit, third_deposit = deposits
    first_price = ONE
    second_price = second_price_ratio
    third_price = second_price_ratio * third_over_second_ratio
    evaluation_price = evaluation_ratio * third_price
    delta = (ONE - safety_factor) / 2

    cash = ZERO
    units = ZERO
    dca_units = ZERO

    first_minimum = safety_factor * first_deposit
    first_available = first_deposit
    first_interval = first_available - first_minimum
    first_purchase = first_minimum + HALF * first_interval
    cash = first_available - first_purchase
    units += first_purchase / first_price
    dca_units += first_deposit / first_price
    coverage = units - safety_factor * dca_units

    assert first_purchase == (ONE - delta) * first_deposit
    assert cash == delta * first_deposit
    assert coverage == delta * first_deposit

    second_minimum = max(
        ZERO,
        safety_factor * second_deposit - second_price * coverage,
    )
    second_available = cash + second_deposit
    second_interval = second_available - second_minimum
    second_purchase = second_minimum + second_score * second_interval
    cash = second_available - second_purchase
    units += second_purchase / second_price
    dca_units += second_deposit / second_price
    coverage = units - safety_factor * dca_units

    expected_second_minimum = max(
        ZERO,
        safety_factor * second_deposit
        - delta * first_deposit * second_price_ratio,
    )
    expected_second_interval = (
        delta * first_deposit + second_deposit - expected_second_minimum
    )
    expected_second_cash = (ONE - second_score) * expected_second_interval
    scaled_second_coverage = second_price * coverage
    expected_scaled_coverage = max(
        ZERO,
        delta * first_deposit * second_price_ratio
        - safety_factor * second_deposit,
    ) + second_score * expected_second_interval

    assert second_minimum == expected_second_minimum
    assert second_interval == expected_second_interval
    assert cash == expected_second_cash
    assert scaled_second_coverage == expected_scaled_coverage

    third_minimum = max(
        ZERO,
        safety_factor * third_deposit - third_price * coverage,
    )
    third_available = cash + third_deposit
    third_interval = third_available - third_minimum
    third_purchase = third_minimum + third_score * third_interval
    cash = third_available - third_purchase
    units += third_purchase / third_price
    dca_units += third_deposit / third_price
    coverage = units - safety_factor * dca_units

    expected_third_minimum = max(
        ZERO,
        safety_factor * third_deposit
        - third_over_second_ratio * expected_scaled_coverage,
    )
    expected_third_interval = (
        expected_second_cash + third_deposit - expected_third_minimum
    )
    expected_terminal_cash = (ONE - third_score) * expected_third_interval
    shift = (
        delta
        * first_deposit
        * third_over_second_ratio
        * (ONE - second_price_ratio)
        + expected_second_cash * (ONE - third_over_second_ratio)
    )

    wealth = cash + evaluation_price * units
    dca_wealth = evaluation_price * dca_units
    direct_gap = wealth - dca_wealth
    formula_gap = expected_terminal_cash * (ONE - evaluation_ratio) + shift * evaluation_ratio

    assert third_minimum == expected_third_minimum
    assert third_interval == expected_third_interval
    assert cash == expected_terminal_cash
    assert coverage >= 0
    assert direct_gap == formula_gap

    return {
        "delta": delta,
        "first_purchase": first_purchase,
        "second_minimum": second_minimum,
        "second_interval": second_interval,
        "second_purchase": second_purchase,
        "second_cash": expected_second_cash,
        "scaled_second_coverage": scaled_second_coverage,
        "third_minimum": third_minimum,
        "third_interval": third_interval,
        "third_purchase": third_purchase,
        "cash": cash,
        "shift": shift,
        "units": units,
        "dca_units": dca_units,
        "gap": direct_gap,
        "threshold": extended_threshold(cash, shift),
    }


def check_exhaustive_identity_and_boundary():
    safety_factors = [Fraction(1, 4), HALF, Fraction(3, 4), ONE]
    deposit_values = [ZERO, ONE, Fraction(2)]
    second_price_ratios = [HALF, ONE, Fraction(2), Fraction(4)]
    third_over_second_ratios = [HALF, ONE, Fraction(2)]
    scores = [Fraction(1, 5), HALF, Fraction(4, 5)]
    evaluation_ratios = [Fraction(1, 3), ONE, Fraction(2), Fraction(3)]

    cases = 0
    boundary_ties = 0
    all_win_slices = 0
    strict_wins = 0
    strict_losses = 0
    second_floor_positive = 0
    second_floor_zero = 0
    third_floor_positive = 0
    third_floor_zero = 0

    base_cases = product(
        safety_factors,
        product(deposit_values, repeat=3),
        second_price_ratios,
        third_over_second_ratios,
        scores,
        scores,
    )
    for (
        safety_factor,
        deposits,
        second_price_ratio,
        third_over_second_ratio,
        second_score,
        third_score,
    ) in base_cases:
        sample = guarded_three_purchase(
            safety_factor,
            deposits,
            second_price_ratio,
            third_over_second_ratio,
            ONE,
            second_score,
            third_score,
        )
        second_floor_positive += sample["second_minimum"] > 0
        second_floor_zero += sample["second_minimum"] == 0
        third_floor_positive += sample["third_minimum"] > 0
        third_floor_zero += sample["third_minimum"] == 0

        for evaluation_ratio in evaluation_ratios:
            observed = guarded_three_purchase(
                safety_factor,
                deposits,
                second_price_ratio,
                third_over_second_ratio,
                evaluation_ratio,
                second_score,
                third_score,
            )
            cases += 1

            if safety_factor == ONE or sum(deposits) == 0:
                assert observed["gap"] == 0
                assert observed["cash"] == 0
                continue

            assert observed["third_interval"] > 0
            assert observed["cash"] > 0
            assert sign(observed["gap"]) == threshold_sign(
                evaluation_ratio, observed["threshold"]
            )
            strict_wins += observed["gap"] > 0
            strict_losses += observed["gap"] < 0

        if safety_factor < ONE and sum(deposits) > 0:
            threshold = sample["threshold"]
            if threshold is None:
                all_win_slices += 1
            else:
                tied = guarded_three_purchase(
                    safety_factor,
                    deposits,
                    second_price_ratio,
                    third_over_second_ratio,
                    threshold,
                    second_score,
                    third_score,
                )
                assert tied["gap"] == 0
                boundary_ties += 1

    assert strict_wins > 0
    assert strict_losses > 0
    assert boundary_ties > 0
    assert all_win_slices > 0
    assert second_floor_positive > 0 and second_floor_zero > 0
    assert third_floor_positive > 0 and third_floor_zero > 0
    return {
        "cases": cases,
        "boundary_ties": boundary_ties,
        "all_win_slices": all_win_slices,
        "strict_wins": strict_wins,
        "strict_losses": strict_losses,
        "second_floor_positive": second_floor_positive,
        "second_floor_zero": second_floor_zero,
        "third_floor_positive": third_floor_positive,
        "third_floor_zero": third_floor_zero,
    }


def identity_reference_alpha_zero(price_ratio, beta):
    """Exact two-input corrected reference for f(u)=u and alpha=0."""
    if beta == -1:
        return 2 * price_ratio / (ONE + price_ratio)
    if beta == 0:
        numerator_root = isqrt(price_ratio.numerator)
        denominator_root = isqrt(price_ratio.denominator)
        assert numerator_root**2 == price_ratio.numerator
        assert denominator_root**2 == price_ratio.denominator
        return Fraction(numerator_root, denominator_root)
    if beta == 1:
        return (ONE + price_ratio) / 2
    raise ValueError("this exact helper covers beta in {-1, 0, 1}")


def identity_score_alpha_zero(normalized_price, reference=ONE):
    relative_price = normalized_price / reference
    return ONE / (ONE + relative_price)


def check_constant_history_and_collapse():
    for beta in (-1, 0, 1):
        assert identity_reference_alpha_zero(ONE, beta) == ONE
        assert identity_score_alpha_zero(ONE, ONE) == HALF

    for safety_factor in (Fraction(1, 4), HALF, Fraction(3, 4)):
        win = guarded_three_purchase(
            safety_factor, (ONE, ONE, ONE), ONE, ONE, HALF, HALF, HALF
        )
        tie = guarded_three_purchase(
            safety_factor, (ONE, ONE, ONE), ONE, ONE, ONE, HALF, HALF
        )
        loss = guarded_three_purchase(
            safety_factor, (ONE, ONE, ONE), ONE, ONE, Fraction(2), HALF, HALF
        )
        assert win["gap"] > 0
        assert tie["gap"] == 0
        assert loss["gap"] < 0
        assert tie["threshold"] == ONE

    collapsed = guarded_three_purchase(
        ONE,
        (Fraction(2), Fraction(3), Fraction(4)),
        Fraction(5, 2),
        Fraction(7, 3),
        Fraction(11, 5),
        Fraction(1, 5),
        Fraction(4, 5),
    )
    assert collapsed["third_interval"] == 0
    assert collapsed["cash"] == 0
    assert collapsed["gap"] == 0

    empty = guarded_three_purchase(
        HALF, (ZERO, ZERO, ZERO), Fraction(2), HALF, Fraction(3), HALF, HALF
    )
    assert empty["cash"] == 0
    assert empty["units"] == 0
    assert empty["dca_units"] == 0
    assert empty["gap"] == 0


def check_threshold_pair(cash_one, cash_two, shift):
    threshold_one = extended_threshold(cash_one, shift)
    threshold_two = extended_threshold(cash_two, shift)
    if threshold_one == threshold_two:
        return False

    finite = [value for value in (threshold_one, threshold_two) if value is not None]
    endpoint = min(finite)
    endpoint_signs = (
        threshold_sign(endpoint, threshold_one),
        threshold_sign(endpoint, threshold_two),
    )
    assert 0 in endpoint_signs
    assert endpoint_signs[0] != endpoint_signs[1]

    if threshold_one is None or threshold_two is None:
        interior = endpoint * 2
    else:
        interior = (threshold_one + threshold_two) / 2
    assert threshold_sign(interior, threshold_one) == -threshold_sign(
        interior, threshold_two
    )
    return True


def check_exact_beta_witness():
    safety_factor = HALF
    deposits = (ONE, ONE, ONE)
    second_price_ratio = Fraction(4)
    third_over_second_ratio = HALF
    normalized_third_price = second_price_ratio * third_over_second_ratio
    evaluation_ratio = Fraction(7, 6)
    second_score = identity_score_alpha_zero(second_price_ratio)

    low_reference = identity_reference_alpha_zero(second_price_ratio, beta=-1)
    diagonal_reference = identity_reference_alpha_zero(
        second_price_ratio, beta=0
    )
    high_reference = identity_reference_alpha_zero(second_price_ratio, beta=1)
    low_score = identity_score_alpha_zero(normalized_third_price, low_reference)
    diagonal_score = identity_score_alpha_zero(
        normalized_third_price, diagonal_reference
    )
    high_score = identity_score_alpha_zero(normalized_third_price, high_reference)

    assert second_score == Fraction(1, 5)
    assert low_reference == Fraction(8, 5)
    assert diagonal_reference == Fraction(2)
    assert high_reference == Fraction(5, 2)
    assert low_score == Fraction(4, 9)
    assert diagonal_score == HALF
    assert high_score == Fraction(5, 9)

    low_beta = guarded_three_purchase(
        safety_factor,
        deposits,
        second_price_ratio,
        third_over_second_ratio,
        evaluation_ratio,
        second_score,
        low_score,
    )
    high_beta = guarded_three_purchase(
        safety_factor,
        deposits,
        second_price_ratio,
        third_over_second_ratio,
        evaluation_ratio,
        second_score,
        high_score,
    )
    diagonal_beta = guarded_three_purchase(
        safety_factor,
        deposits,
        second_price_ratio,
        third_over_second_ratio,
        evaluation_ratio,
        second_score,
        diagonal_score,
    )

    for key, expected in {
        "first_purchase": Fraction(3, 4),
        "second_minimum": ZERO,
        "second_interval": Fraction(5, 4),
        "second_purchase": Fraction(1, 4),
        "second_cash": ONE,
        "scaled_second_coverage": Fraction(3, 4),
        "third_minimum": Fraction(1, 8),
        "third_interval": Fraction(15, 8),
        "shift": Fraction(1, 8),
    }.items():
        assert low_beta[key] == expected
        assert high_beta[key] == expected

    assert low_beta["third_purchase"] == Fraction(23, 24)
    assert diagonal_beta["third_purchase"] == Fraction(17, 16)
    assert high_beta["third_purchase"] == Fraction(7, 6)
    assert low_beta["cash"] == Fraction(25, 24)
    assert diagonal_beta["cash"] == Fraction(15, 16)
    assert high_beta["cash"] == Fraction(5, 6)
    assert low_beta["threshold"] == Fraction(25, 22)
    assert diagonal_beta["threshold"] == Fraction(15, 13)
    assert high_beta["threshold"] == Fraction(20, 17)
    assert low_beta["gap"] == -Fraction(1, 36)
    assert diagonal_beta["gap"] == -Fraction(1, 96)
    assert high_beta["gap"] == Fraction(1, 144)
    assert low_beta["threshold"] < evaluation_ratio < high_beta["threshold"]

    expected_difference = (
        low_beta["third_interval"]
        * (high_score - low_score)
        * (ONE - evaluation_ratio)
    )
    assert low_beta["gap"] - high_beta["gap"] == expected_difference
    assert check_threshold_pair(low_beta["cash"], high_beta["cash"], low_beta["shift"])

    low_tie = guarded_three_purchase(
        safety_factor,
        deposits,
        second_price_ratio,
        third_over_second_ratio,
        low_beta["threshold"],
        second_score,
        low_score,
    )
    high_at_low_tie = guarded_three_purchase(
        safety_factor,
        deposits,
        second_price_ratio,
        third_over_second_ratio,
        low_beta["threshold"],
        second_score,
        high_score,
    )
    low_at_high_tie = guarded_three_purchase(
        safety_factor,
        deposits,
        second_price_ratio,
        third_over_second_ratio,
        high_beta["threshold"],
        second_score,
        low_score,
    )
    high_tie = guarded_three_purchase(
        safety_factor,
        deposits,
        second_price_ratio,
        third_over_second_ratio,
        high_beta["threshold"],
        second_score,
        high_score,
    )
    assert low_tie["gap"] == 0 < high_at_low_tie["gap"]
    assert low_at_high_tie["gap"] < 0 == high_tie["gap"]

    return {
        "low_reference": low_reference,
        "diagonal_reference": diagonal_reference,
        "high_reference": high_reference,
        "low_score": low_score,
        "diagonal_score": diagonal_score,
        "high_score": high_score,
        "low_gap": low_beta["gap"],
        "high_gap": high_beta["gap"],
        "low_threshold": low_beta["threshold"],
        "high_threshold": high_beta["threshold"],
    }


def main():
    counts = check_exhaustive_identity_and_boundary()
    check_constant_history_and_collapse()
    witness = check_exact_beta_witness()
    print("All exact three-purchase corrected-mean checks passed.")
    for key, value in counts.items():
        print(f"{key}: {value}")
    print(
        "beta witness: "
        f"R2(-1)={witness['low_reference']} "
        f"R2(0)={witness['diagonal_reference']} "
        f"R2(1)={witness['high_reference']} "
        f"a3(-1)={witness['low_score']} "
        f"a3(0)={witness['diagonal_score']} "
        f"a3(1)={witness['high_score']}"
    )
    print(
        "classification flip at y=7/6: "
        f"gap(-1)={witness['low_gap']} gap(1)={witness['high_gap']} "
        f"thresholds=({witness['low_threshold']}, {witness['high_threshold']})"
    )


if __name__ == "__main__":
    main()
