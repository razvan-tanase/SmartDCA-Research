#!/usr/bin/env python3
"""Reproducible checks for the guarded corrected-mean SmartDCA rule."""

from fractions import Fraction
from itertools import product
from math import exp, fsum, isclose, isfinite, log, nextafter


MIN_OFF_DIAGONAL_GAP = 1e-10


def logsumexp(log_terms):
    largest = max(log_terms)
    return largest + log(fsum(exp(term - largest) for term in log_terms))


def corrected_mean(values, alpha, beta, transform, weights=None):
    if weights is None:
        weights = [1.0] * len(values)
    if not values or len(values) != len(weights):
        raise ValueError("positive values and matching positive weights required")
    if any(not isfinite(value) or value <= 0 for value in values):
        raise ValueError("finite positive values required")
    if any(not isfinite(weight) or weight <= 0 for weight in weights):
        raise ValueError("finite positive weights required")
    transform_values = [transform(value) for value in values]
    if any(not isfinite(value) or value <= 0 for value in transform_values):
        raise ValueError("transform must return finite positive values")

    if alpha == beta:
        q = alpha
        log_mean_weights = [
            log(weight) + log(value) + (q - 1.0) * log(transform_value)
            for value, weight, transform_value in zip(values, weights, transform_values)
        ]
        largest = max(log_mean_weights)
        scaled_weights = [exp(term - largest) for term in log_mean_weights]
        return exp(
            fsum(weight * log(value) for value, weight in zip(values, scaled_weights))
            / fsum(scaled_weights)
        )

    difference = alpha - beta
    if abs(difference) < MIN_OFF_DIAGONAL_GAP:
        raise ValueError(
            "off-diagonal parameters are too close for this binary64 verifier; "
            "use arbitrary-precision evaluation"
        )
    log_numerator_terms = [
        log(weight) + log(value) + (alpha - 1.0) * log(transform_value)
        for value, weight, transform_value in zip(values, weights, transform_values)
    ]
    log_denominator_terms = [
        log(weight)
        + (1.0 - alpha + beta) * log(value)
        + (alpha - 1.0) * log(transform_value)
        for value, weight, transform_value in zip(values, weights, transform_values)
    ]
    log_mean = (
        logsumexp(log_numerator_terms) - logsumexp(log_denominator_terms)
    ) / difference
    return exp(log_mean)


def bounded_score(price_history, alpha, beta, transform):
    if not price_history or any(price <= 0 for price in price_history):
        raise ValueError("a nonempty positive price history is required")
    if len(price_history) == 1:
        return 0.5

    anchor = price_history[0]
    lagged = [price / anchor for price in price_history[:-1]]
    current = price_history[-1] / anchor
    reference = corrected_mean(lagged, alpha, beta, transform)
    relative_price = current / reference
    transformed_relative_price = transform(relative_price)
    transformed_neutral_price = transform(1.0)
    if (
        not isfinite(transformed_relative_price)
        or transformed_relative_price <= 0.0
        or not isfinite(transformed_neutral_price)
        or transformed_neutral_price <= 0.0
    ):
        raise ValueError("transform must return finite positive values")
    log_odds = (alpha - 1.0) * (
        log(transformed_relative_price) - log(transformed_neutral_price)
    )
    if log_odds >= 0.0:
        score = 1.0 / (1.0 + exp(-log_odds))
    else:
        odds = exp(log_odds)
        score = odds / (1.0 + odds)
    # Preserve the mathematical open interval in binary64 at extreme logits.
    return min(nextafter(1.0, 0.0), max(nextafter(0.0, 1.0), score))


def guarded_path(prices, deposits, safety_factor, alpha, beta, transform):
    if not prices or len(prices) != len(deposits):
        raise ValueError("prices and deposits must be nonempty and have equal length")
    if any(not isfinite(price) or price <= 0 for price in prices):
        raise ValueError("prices must be finite and positive")
    if any(not isfinite(deposit) or deposit < 0 for deposit in deposits):
        raise ValueError("deposits must be finite and nonnegative")
    if not 0.0 < safety_factor <= 1.0:
        raise ValueError("safety_factor must lie in (0, 1]")

    cash = 0.0
    units = 0.0
    dca_units = 0.0
    total_deposits = 0.0
    total_spent = 0.0
    rows = []

    for index, (price, deposit) in enumerate(zip(prices, deposits)):
        coverage = units - safety_factor * dca_units
        available = cash + deposit
        minimum = max(0.0, safety_factor * deposit - price * coverage)
        score = bounded_score(prices[: index + 1], alpha, beta, transform)
        purchase = minimum + score * (available - minimum)
        cash = available - purchase
        units += purchase / price
        dca_units += deposit / price
        total_deposits += deposit
        total_spent += purchase
        new_coverage = units - safety_factor * dca_units
        rows.append(
            {
                "price": price,
                "deposit": deposit,
                "score": score,
                "minimum": minimum,
                "purchase": purchase,
                "cash": cash,
                "units": units,
                "dca_units": dca_units,
                "coverage": new_coverage,
                "total_deposits": total_deposits,
                "total_spent": total_spent,
                "average_cost": total_spent / units if units > 0.0 else None,
            }
        )
    return rows


def check_special_cases():
    values = [0.5, 1.25, 3.0, 7.0]
    weights = [1.0, 2.0, 1.5, 0.75]
    identity = lambda value: value
    alpha, beta = 0.4, -0.8
    observed = corrected_mean(values, alpha, beta, identity, weights)
    expected = (
        sum(weight * value**alpha for value, weight in zip(values, weights))
        / sum(weight * value**beta for value, weight in zip(values, weights))
    ) ** (1.0 / (alpha - beta))
    assert isclose(observed, expected, rel_tol=1e-12)

    transform = lambda value: 1.0 + value
    alpha, beta = 0.25, -0.75
    observed = corrected_mean(values, alpha, beta, transform, weights)
    expected = sum(
        weight * value * transform(value) ** (alpha - 1.0)
        for value, weight in zip(values, weights)
    ) / sum(
        weight * transform(value) ** (alpha - 1.0)
        for value, weight in zip(values, weights)
    )
    assert isclose(observed, expected, rel_tol=1e-12)


def check_score_properties():
    transform = lambda value: 1.0 + value
    alpha, beta = 0.25, -0.5

    assert bounded_score([100.0], alpha, beta, transform) == 0.5
    for length in range(1, 9):
        assert isclose(
            bounded_score([37.0] * length, alpha, beta, transform),
            0.5,
            abs_tol=1e-14,
        )

    histories = [
        [100.0, 85.0],
        [100.0, 85.0, 120.0],
        [100.0, 85.0, 120.0, 72.0],
    ]
    for history in histories:
        original = bounded_score(history, alpha, beta, transform)
        scaled = bounded_score([11.0 * price for price in history], alpha, beta, transform)
        assert isclose(original, scaled, rel_tol=1e-13, abs_tol=1e-13)

    for alpha_value in (-2.0, 0.25, 1.0, 2.0):
        for beta_value in (-1.0, 0.25, 1.5):
            for current in (1e-5, 1.0, 70.0, 1e5):
                score = bounded_score(
                    [100.0, 75.0, 125.0, current],
                    alpha_value,
                    beta_value,
                    transform,
                )
                assert 0.0 < score < 1.0

    extreme_scores = [
        bounded_score([1.0, 1e300], -100.0, -101.0, lambda value: value),
        bounded_score([1.0, 1e-300], -100.0, -101.0, lambda value: value),
    ]
    assert all(0.0 < score < 1.0 for score in extreme_scores)

    try:
        corrected_mean([1.0, 2.0], 1.0, 1.0 - 1e-12, transform)
    except ValueError as error:
        assert "arbitrary-precision" in str(error)
    else:
        raise AssertionError("near-diagonal binary64 evaluation must not be silent")

    past = [100.0, 75.0, 125.0]
    current_prices = [40.0, 60.0, 90.0, 130.0, 200.0]
    scores = [
        bounded_score(past + [price], alpha, beta, transform)
        for price in current_prices
    ]
    assert all(left > right for left, right in zip(scores, scores[1:]))

    safety_factor = 0.9
    deposit = 100.0
    cash = 25.0
    coverage = 0.8
    available = cash + deposit
    purchases = []
    for price, score in zip(current_prices, scores):
        minimum = max(0.0, safety_factor * deposit - price * coverage)
        purchases.append(minimum + score * (available - minimum))
    assert all(left >= right for left, right in zip(purchases, purchases[1:]))


def check_exact_guardrail_accounting():
    prices = [Fraction(1), Fraction(2), Fraction(3)]
    deposits = [Fraction(0), Fraction(1), Fraction(2)]
    scores = [Fraction(0), Fraction(1, 2), Fraction(1)]
    safety_factors = [Fraction(1, 2), Fraction(3, 4), Fraction(1)]
    checked_paths = 0
    checked_terminal_values = 0

    for safety_factor in safety_factors:
        for price_path in product(prices, repeat=3):
            for deposit_path in product(deposits, repeat=3):
                for score_path in product(scores, repeat=3):
                    cash = Fraction(0)
                    units = Fraction(0)
                    dca_units = Fraction(0)
                    total_deposits = Fraction(0)
                    total_spent = Fraction(0)
                    spent_units = Fraction(0)

                    for price, deposit, score in zip(price_path, deposit_path, score_path):
                        old_coverage = units - safety_factor * dca_units
                        assert old_coverage >= 0
                        available = cash + deposit
                        minimum = max(
                            Fraction(0),
                            safety_factor * deposit - price * old_coverage,
                        )
                        assert Fraction(0) <= minimum <= available
                        purchase = minimum + score * (available - minimum)
                        assert minimum <= purchase <= available

                        cash = available - purchase
                        units += purchase / price
                        dca_units += deposit / price
                        coverage = units - safety_factor * dca_units
                        expected_coverage = max(
                            Fraction(0),
                            old_coverage - safety_factor * deposit / price,
                        ) + score * (available - minimum) / price
                        assert coverage == expected_coverage
                        assert coverage >= 0

                        total_deposits += deposit
                        total_spent += purchase
                        spent_units += purchase / price
                        assert cash == total_deposits - total_spent
                        assert units == spent_units

                    for evaluation_price in (Fraction(1, 2), Fraction(1), Fraction(4)):
                        wealth = cash + evaluation_price * units
                        dca_wealth = evaluation_price * dca_units
                        coverage = units - safety_factor * dca_units
                        assert wealth - safety_factor * dca_wealth == cash + evaluation_price * coverage
                        assert wealth >= safety_factor * dca_wealth
                        checked_terminal_values += 1
                    checked_paths += 1

    return checked_paths, checked_terminal_values


def check_nontrivial_path():
    prices = [100.0, 78.0, 122.0, 69.0]
    deposits = [100.0, 100.0, 100.0, 100.0]
    rows = guarded_path(
        prices,
        deposits,
        safety_factor=0.9,
        alpha=0.25,
        beta=-0.5,
        transform=lambda value: 1.0 + value,
    )
    assert all(0.0 < row["score"] < 1.0 for row in rows)
    assert all(row["coverage"] >= -1e-12 for row in rows)
    assert all(row["cash"] >= -1e-12 for row in rows)

    cumulative_spent_units = 0.0
    for row in rows:
        cumulative_spent_units += row["purchase"] / row["price"]
        assert isclose(row["cash"], row["total_deposits"] - row["total_spent"], abs_tol=1e-12)
        assert isclose(row["units"], cumulative_spent_units, abs_tol=1e-12)
        assert isclose(
            row["coverage"],
            row["units"] - 0.9 * row["dca_units"],
            abs_tol=1e-12,
        )
        assert isclose(
            row["average_cost"],
            row["total_spent"] / row["units"],
            abs_tol=1e-12,
        )
        for evaluation_price in (1e-3, 50.0, 1e4):
            wealth = row["cash"] + evaluation_price * row["units"]
            dca_wealth = evaluation_price * row["dca_units"]
            assert isclose(
                wealth - 0.9 * dca_wealth,
                row["cash"] + evaluation_price * row["coverage"],
                rel_tol=1e-12,
                abs_tol=1e-10,
            )

    prefix_rows = guarded_path(
        prices[:3],
        deposits[:3],
        safety_factor=0.9,
        alpha=0.25,
        beta=-0.5,
        transform=lambda value: 1.0 + value,
    )
    for full_row, prefix_row in zip(rows[:3], prefix_rows):
        for field in ("score", "minimum", "purchase", "cash", "units", "coverage"):
            assert isclose(full_row[field], prefix_row[field], abs_tol=1e-12)

    zero_row = guarded_path(
        [100.0],
        [0.0],
        safety_factor=0.9,
        alpha=0.25,
        beta=-0.5,
        transform=lambda value: 1.0 + value,
    )[0]
    assert zero_row["units"] == 0.0
    assert zero_row["average_cost"] is None
    return rows


def main():
    check_special_cases()
    check_score_properties()
    checked_paths, checked_terminal_values = check_exact_guardrail_accounting()
    rows = check_nontrivial_path()
    print("special-case, edge-case, scale, causality, boundedness, and monotonicity checks passed")
    print(
        f"exact accounting passed on {checked_paths:,} guarded paths and "
        f"{checked_terminal_values:,} terminal valuations"
    )
    print("nontrivial path:")
    for index, row in enumerate(rows, start=1):
        print(
            f"  t={index}: p={row['price']:.2f}, a={row['score']:.6f}, "
            f"m={row['minimum']:.6f}, x={row['purchase']:.6f}, "
            f"C={row['cash']:.6f}, K={row['coverage']:.9f}"
        )


if __name__ == "__main__":
    main()
