#!/usr/bin/env python3
"""Exact checks for the two-purchase guarded SmartDCA/DCA boundary."""

from fractions import Fraction
from itertools import product


ZERO = Fraction(0)
HALF = Fraction(1, 2)
ONE = Fraction(1)


def singleton_corrected_reference(alpha, beta, transform_at_one=ONE):
    """Evaluate the corrected mean's singleton reference at the input 1."""
    if alpha == beta:
        # The diagonal extension is the weighted geometric mean of the
        # singleton, hence 1 independently of its positive function weight.
        return ONE
    numerator = ONE * transform_at_one ** (alpha - 1)
    denominator = (
        ONE ** (1 - alpha + beta) * transform_at_one ** (alpha - 1)
    )
    assert numerator == denominator
    return ONE


def identity_score(price_ratio, alpha, beta=0):
    """Canonical score for f(u)=u at the integer alphas used below."""
    reference = singleton_corrected_reference(alpha, beta)
    relative_price = price_ratio / reference
    if alpha == 0:
        return ONE / (ONE + relative_price)
    if alpha == 1:
        return HALF
    if alpha == 2:
        return relative_price / (ONE + relative_price)
    raise ValueError("this exact verifier uses alpha in {0, 1, 2}")


def sign(value):
    return (value > 0) - (value < 0)


def extended_threshold(cash, shift):
    denominator = cash - shift
    return cash / denominator if denominator > 0 else None


def threshold_sign(evaluation_ratio, threshold):
    if threshold is None:
        return 1
    return sign(threshold - evaluation_ratio)


def extended_ge(left, right):
    """Compare thresholds where None denotes positive infinity."""
    if left is None:
        return True
    if right is None:
        return False
    return left >= right


def guarded_two_purchase(
    safety_factor,
    first_deposit,
    second_deposit,
    price_ratio,
    evaluation_ratio,
    score,
):
    first_price = ONE
    second_price = price_ratio
    evaluation_price = evaluation_ratio * second_price
    delta = (ONE - safety_factor) / 2

    first_minimum = safety_factor * first_deposit
    first_purchase = first_minimum + HALF * (first_deposit - first_minimum)
    first_cash = first_deposit - first_purchase
    first_dca_units = first_deposit / first_price
    first_units = first_purchase / first_price
    first_coverage = first_units - safety_factor * first_dca_units

    assert first_purchase == (ONE - delta) * first_deposit
    assert first_cash == delta * first_deposit
    assert first_coverage == delta * first_deposit / first_price

    second_minimum = max(
        ZERO,
        safety_factor * second_deposit - second_price * first_coverage,
    )
    available = first_cash + second_deposit
    interval = available - second_minimum
    second_purchase = second_minimum + score * interval
    terminal_cash = available - second_purchase

    units = first_units + second_purchase / second_price
    dca_units = first_dca_units + second_deposit / second_price
    wealth = terminal_cash + evaluation_price * units
    dca_wealth = evaluation_price * dca_units
    direct_gap = wealth - dca_wealth

    expected_minimum = max(
        ZERO,
        safety_factor * second_deposit - delta * first_deposit * price_ratio,
    )
    expected_interval = (
        delta * first_deposit + second_deposit - expected_minimum
    )
    expected_cash = (ONE - score) * expected_interval
    shift = delta * first_deposit * (ONE - price_ratio)
    formula_gap = expected_cash * (ONE - evaluation_ratio) + shift * evaluation_ratio

    assert second_minimum == expected_minimum
    assert interval == expected_interval
    assert terminal_cash == expected_cash
    assert direct_gap == formula_gap

    return {
        "delta": delta,
        "minimum": second_minimum,
        "interval": interval,
        "cash": terminal_cash,
        "shift": shift,
        "gap": direct_gap,
        "threshold": extended_threshold(terminal_cash, shift),
    }


def check_exhaustive_identities_and_boundaries():
    safety_factors = [Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), ONE]
    deposits = [ZERO, ONE, Fraction(3)]
    price_ratios = [Fraction(1, 3), HALF, ONE, Fraction(2), Fraction(3)]
    evaluation_ratios = [Fraction(1, 4), HALF, ONE, Fraction(2), Fraction(4)]
    alphas = [0, 1, 2]

    cases = 0
    boundary_ties = 0
    strict_wins = 0
    strict_losses = 0
    all_win_slices = 0
    neutral_comparisons = 0

    for safety_factor, first_deposit, second_deposit, price_ratio, alpha in product(
        safety_factors, deposits, deposits, price_ratios, alphas
    ):
        score = identity_score(price_ratio, alpha)
        for evaluation_ratio in evaluation_ratios:
            observed = guarded_two_purchase(
                safety_factor,
                first_deposit,
                second_deposit,
                price_ratio,
                evaluation_ratio,
                score,
            )
            cases += 1

            if safety_factor == ONE or first_deposit + second_deposit == 0:
                assert observed["gap"] == 0
                assert observed["cash"] == 0
                continue

            assert observed["interval"] > 0
            assert observed["cash"] > 0
            assert sign(observed["gap"]) == threshold_sign(
                evaluation_ratio, observed["threshold"]
            )
            if observed["gap"] > 0:
                strict_wins += 1
            elif observed["gap"] < 0:
                strict_losses += 1

            neutral = guarded_two_purchase(
                safety_factor,
                first_deposit,
                second_deposit,
                price_ratio,
                evaluation_ratio,
                HALF,
            )
            expected_difference = (
                observed["interval"]
                * (HALF - score)
                * (ONE - evaluation_ratio)
            )
            assert observed["gap"] - neutral["gap"] == expected_difference
            neutral_comparisons += 1

            if alpha == 0:
                assert extended_ge(observed["threshold"], neutral["threshold"])
            elif alpha == 2:
                assert extended_ge(neutral["threshold"], observed["threshold"])
            else:
                assert observed["threshold"] == neutral["threshold"]

        sample = guarded_two_purchase(
            safety_factor,
            first_deposit,
            second_deposit,
            price_ratio,
            ONE,
            score,
        )
        if safety_factor < ONE and first_deposit + second_deposit > 0:
            threshold = sample["threshold"]
            if threshold is None:
                for evaluation_ratio in evaluation_ratios:
                    observed = guarded_two_purchase(
                        safety_factor,
                        first_deposit,
                        second_deposit,
                        price_ratio,
                        evaluation_ratio,
                        score,
                    )
                    assert observed["gap"] > 0
                all_win_slices += 1
            else:
                tied = guarded_two_purchase(
                    safety_factor,
                    first_deposit,
                    second_deposit,
                    price_ratio,
                    threshold,
                    score,
                )
                below = guarded_two_purchase(
                    safety_factor,
                    first_deposit,
                    second_deposit,
                    price_ratio,
                    threshold / 2,
                    score,
                )
                above = guarded_two_purchase(
                    safety_factor,
                    first_deposit,
                    second_deposit,
                    price_ratio,
                    threshold * 2,
                    score,
                )
                assert tied["gap"] == 0
                assert below["gap"] > 0
                assert above["gap"] < 0
                boundary_ties += 1

    assert strict_wins > 0
    assert strict_losses > 0
    assert boundary_ties > 0
    assert all_win_slices > 0
    return {
        "cases": cases,
        "boundary_ties": boundary_ties,
        "strict_wins": strict_wins,
        "strict_losses": strict_losses,
        "all_win_slices": all_win_slices,
        "neutral_comparisons": neutral_comparisons,
    }


def check_nonempty_regions_and_collapse():
    for safety_factor in (Fraction(1, 4), HALF, Fraction(3, 4)):
        for first_deposit, second_deposit in (
            (ZERO, ONE),
            (ONE, ZERO),
            (ONE, Fraction(2)),
        ):
            win = guarded_two_purchase(
                safety_factor,
                first_deposit,
                second_deposit,
                ONE,
                HALF,
                HALF,
            )
            tie = guarded_two_purchase(
                safety_factor,
                first_deposit,
                second_deposit,
                ONE,
                ONE,
                HALF,
            )
            loss = guarded_two_purchase(
                safety_factor,
                first_deposit,
                second_deposit,
                ONE,
                Fraction(2),
                HALF,
            )
            assert win["gap"] > 0
            assert tie["gap"] == 0
            assert loss["gap"] < 0

    for score in (Fraction(1, 4), HALF, Fraction(3, 4)):
        collapsed = guarded_two_purchase(
            ONE,
            Fraction(2),
            Fraction(3),
            Fraction(5, 4),
            Fraction(7, 3),
            score,
        )
        assert collapsed["interval"] == 0
        assert collapsed["cash"] == 0
        assert collapsed["gap"] == 0


def check_beta_independence():
    checked = 0
    for price_ratio, alpha, beta in product(
        (Fraction(1, 3), ONE, Fraction(3)),
        (0, 1, 2),
        (-4, 0, 7),
    ):
        assert identity_score(price_ratio, alpha, beta) == identity_score(
            price_ratio, alpha
        )
        assert singleton_corrected_reference(
            alpha, beta, transform_at_one=Fraction(2)
        ) == ONE
        checked += 1
    return checked


def check_exact_flip_and_all_win_examples():
    safety_factor = HALF
    first_deposit = ONE
    second_deposit = ONE
    price_ratio = Fraction(2)
    evaluation_ratio = Fraction(3, 4)
    score = Fraction(1, 3)

    corrected = guarded_two_purchase(
        safety_factor,
        first_deposit,
        second_deposit,
        price_ratio,
        evaluation_ratio,
        score,
    )
    neutral = guarded_two_purchase(
        safety_factor,
        first_deposit,
        second_deposit,
        price_ratio,
        evaluation_ratio,
        HALF,
    )
    assert corrected["threshold"] == Fraction(10, 13)
    assert neutral["threshold"] == Fraction(5, 7)
    assert corrected["gap"] == Fraction(1, 48)
    assert neutral["gap"] == -Fraction(1, 32)

    all_win = guarded_two_purchase(
        safety_factor,
        first_deposit,
        ZERO,
        HALF,
        Fraction(1000),
        Fraction(2, 3),
    )
    assert all_win["cash"] == Fraction(1, 12)
    assert all_win["shift"] == Fraction(1, 8)
    assert all_win["threshold"] is None
    assert all_win["gap"] == Fraction(1, 12) + Fraction(1000, 24)

    return corrected, neutral, all_win


def main():
    counts = check_exhaustive_identities_and_boundaries()
    check_nonempty_regions_and_collapse()
    beta_independence_checks = check_beta_independence()
    corrected, neutral, all_win = check_exact_flip_and_all_win_examples()
    print("All exact two-purchase DCA boundary checks passed.")
    for key, value in counts.items():
        print(f"{key}: {value}")
    print(f"beta_independence_checks: {beta_independence_checks}")
    print(
        "flip example: "
        f"corrected_gap={corrected['gap']} neutral_gap={neutral['gap']} "
        f"corrected_threshold={corrected['threshold']} "
        f"neutral_threshold={neutral['threshold']}"
    )
    print(
        "all-win example: "
        f"cash={all_win['cash']} shift={all_win['shift']} "
        f"gap_at_y_1000={all_win['gap']}"
    )


if __name__ == "__main__":
    main()
