"""Seeded checks for ticket 07's homogeneity characterization."""

from __future__ import annotations

import math
import random


def corrected_mean(x, w, alpha, beta, transform):
    if abs(alpha - beta) < 1e-12:
        q = alpha
        weights = [wi * xi * transform(xi) ** (q - 1.0) for xi, wi in zip(x, w)]
        return math.exp(
            sum(ai * math.log(xi) for xi, ai in zip(x, weights)) / sum(weights)
        )

    d = alpha - beta
    numerator = sum(
        wi * xi * transform(xi) ** (alpha - 1.0) for xi, wi in zip(x, w)
    )
    denominator = sum(
        wi * xi ** (1.0 - d) * transform(xi) ** (alpha - 1.0)
        for xi, wi in zip(x, w)
    )
    return (numerator / denominator) ** (1.0 / d)


def relative_error(actual, expected):
    return abs(actual - expected) / max(1.0, abs(actual), abs(expected))


def run_seeded_checks(seed=20260815, trials=4000):
    rng = random.Random(seed)
    worst = 0.0

    # Power transforms: all off-diagonal and diagonal parameters are homogeneous.
    for _ in range(trials):
        size = rng.randint(2, 7)
        x = [math.exp(rng.uniform(-2.0, 2.0)) for _ in range(size)]
        w = [math.exp(rng.uniform(-1.0, 1.0)) for _ in range(size)]
        c = math.exp(rng.uniform(-1.5, 1.5))
        exponent = rng.choice([0.0, 0.2, 1.0, 2.3])
        constant = math.exp(rng.uniform(-1.0, 1.0))
        transform = lambda t, C=constant, r=exponent: C * t**r
        alpha = rng.uniform(-2.0, 3.0)
        if rng.random() < 0.25:
            beta = alpha
        else:
            d = rng.choice([-2.5, -1.0, -0.2, 0.3, 1.0, 2.2])
            beta = alpha - d
        lhs = corrected_mean([c * xi for xi in x], w, alpha, beta, transform)
        rhs = c * corrected_mean(x, w, alpha, beta, transform)
        worst = max(worst, relative_error(lhs, rhs))
        assert relative_error(lhs, rhs) < 2e-11

    # Exceptional alpha=q=1 line: f cancels even when it is not a power.
    nonpower = lambda t: 1.0 + t
    for beta in [-2.0, 0.0, 0.7, 1.0, 3.0]:
        x = [0.7, 1.4, 4.0]
        w = [1.0, 2.0, 0.5]
        c = 2.3
        lhs = corrected_mean([c * xi for xi in x], w, 1.0, beta, nonpower)
        rhs = c * corrected_mean(x, w, 1.0, beta, nonpower)
        worst = max(worst, relative_error(lhs, rhs))
        assert relative_error(lhs, rhs) < 2e-12

    # A concrete nonpower failure away from alpha=1.
    x = [1.0, 2.0]
    w = [1.0, 1.0]
    base = corrected_mean(x, w, 2.0, 1.0, nonpower)
    scaled = corrected_mean([2.0, 4.0], w, 2.0, 1.0, nonpower)
    assert abs(base - 8.0 / 5.0) < 1e-15
    assert abs(scaled - 13.0 / 4.0) < 1e-15
    assert abs(scaled - 2.0 * base) > 0.04

    # The same nonpower transform fails on a nonexceptional diagonal.
    diagonal_base = corrected_mean(x, w, 2.0, 2.0, nonpower)
    diagonal_scaled = corrected_mean([2.0, 4.0], w, 2.0, 2.0, nonpower)
    assert relative_error(diagonal_scaled, 2.0 * diagonal_base) > 1e-3

    return {
        "seed": seed,
        "power_and_exceptional_checks": trials + 5,
        "worst_relative_error": worst,
        "off_diagonal_counterexample": {
            "M(1,2)": base,
            "M(2,4)": scaled,
            "2*M(1,2)": 2.0 * base,
        },
        "diagonal_counterexample": {
            "M(1,2)": diagonal_base,
            "M(2,4)": diagonal_scaled,
            "2*M(1,2)": 2.0 * diagonal_base,
        },
    }


if __name__ == "__main__":
    print(run_seeded_checks())
