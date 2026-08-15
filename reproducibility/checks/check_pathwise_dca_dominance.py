#!/usr/bin/env python3
"""Finite checks for ticket-04's pathwise DCA impossibility boundary."""

from __future__ import annotations

from itertools import product
from math import isclose


def terminal_wealth(prices, deposits, spends, terminal_price):
    cash = 0.0
    units = 0.0
    for price, deposit, spend in zip(prices, deposits, spends, strict=True):
        assert price > 0 and deposit >= 0
        cash += deposit
        assert -1e-12 <= spend <= cash + 1e-12
        cash -= spend
        units += spend / price
    return cash + terminal_price * units


def dca_spends(deposits):
    return tuple(float(value) for value in deposits)


def oracle_future_min_spends(prices, deposits):
    """Assign each deposit to the earliest future minimum purchase price."""
    spends = [0.0] * len(prices)
    for start, deposit in enumerate(deposits):
        minimum = min(prices[start:])
        buy_date = next(
            date for date in range(start, len(prices)) if prices[date] == minimum
        )
        spends[buy_date] += deposit
    return tuple(spends)


def wait_until_last_spends(deposits):
    return (0.0,) * (len(deposits) - 1) + (float(sum(deposits)),)


def check_gap_identity():
    cases = 0
    prices = (3.0, 1.0, 5.0)
    deposits = (2.0, 3.0, 4.0)
    terminal = 7.0
    for fractions in product((0.0, 0.25, 0.5, 1.0), repeat=3):
        cash = 0.0
        spends = []
        for deposit, fraction in zip(deposits, fractions, strict=True):
            cash += deposit
            spend = fraction * cash
            cash -= spend
            spends.append(spend)
        actual = terminal_wealth(prices, deposits, spends, terminal)
        dca = terminal_wealth(
            prices, deposits, dca_spends(deposits), terminal
        )
        identity = sum(
            (deposit - spend) * (1.0 - terminal / price)
            for price, deposit, spend in zip(
                prices, deposits, spends, strict=True
            )
        )
        assert isclose(actual - dca, identity, abs_tol=1e-10)
        cases += 1
    return cases


def check_adversarial_witness():
    cases = 0
    for price, deposit, hold_fraction, multiplier in product(
        (0.5, 1.0, 3.0, 10.0),
        (1.0, 2.5, 100.0),
        (0.1, 0.5, 1.0),
        (1.01, 2.0, 100.0),
    ):
        residual = deposit * hold_fraction
        spend = deposit - residual
        terminal = multiplier * price
        candidate = terminal_wealth(
            (price,), (deposit,), (spend,), terminal
        )
        dca = terminal_wealth(
            (price,), (deposit,), dca_spends((deposit,)), terminal
        )
        predicted_gap = residual * (1.0 - terminal / price)
        assert isclose(candidate - dca, predicted_gap, abs_tol=1e-10)
        assert candidate < dca
        cases += 1
    return cases


def check_prefix_adversarial_witness():
    """Test deviations after DCA prefixes and constant-price continuations."""
    cases = 0
    horizon = 3
    for deviation_date in range(horizon):
        later_dates = horizon - deviation_date - 1
        for current_price, current_deposit, hold_fraction, multiplier in product(
            (0.5, 3.0),
            (2.5, 100.0),
            (0.1, 0.5, 1.0),
            (1.01, 2.0, 100.0),
        ):
            terminal = multiplier * current_price
            residual = current_deposit * hold_fraction
            for future_deposits in product((0.0, 4.0), repeat=later_dates):
                for future_fractions in product(
                    (0.0, 0.5, 1.0), repeat=later_dates
                ):
                    prices = (
                        tuple(1.25 + date for date in range(deviation_date))
                        + (current_price,)
                        + (terminal,) * later_dates
                    )
                    deposits = (
                        (1.0,) * deviation_date
                        + (current_deposit,)
                        + future_deposits
                    )
                    spends = list(deposits[:deviation_date])
                    spends.append(current_deposit - residual)
                    cash = residual
                    for deposit, fraction in zip(
                        future_deposits, future_fractions, strict=True
                    ):
                        cash += deposit
                        spend = fraction * cash
                        cash -= spend
                        spends.append(spend)
                    candidate = terminal_wealth(
                        prices, deposits, spends, terminal
                    )
                    dca = terminal_wealth(
                        prices, deposits, dca_spends(deposits), terminal
                    )
                    predicted_gap = residual * (
                        1.0 - terminal / current_price
                    )
                    assert isclose(
                        candidate - dca, predicted_gap, abs_tol=1e-9
                    )
                    assert candidate < dca
                    cases += 1
    return cases


def check_oracle():
    cases = 0
    strict = 0
    price_grid = (1.0, 2.0, 4.0)
    deposit_grid = (0.0, 1.0, 3.0)
    terminal_grid = (0.5, 1.0, 3.0, 8.0)
    for prices, deposits, terminal in product(
        product(price_grid, repeat=3),
        product(deposit_grid, repeat=3),
        terminal_grid,
    ):
        oracle = terminal_wealth(
            prices,
            deposits,
            oracle_future_min_spends(prices, deposits),
            terminal,
        )
        dca = terminal_wealth(
            prices, deposits, dca_spends(deposits), terminal
        )
        assert oracle >= dca - 1e-10
        expected_strict = any(
            deposit > 0 and min(prices[start:]) < prices[start]
            for start, deposit in enumerate(deposits)
        )
        assert (oracle > dca + 1e-10) == expected_strict
        strict += int(expected_strict)
        cases += 1
    return cases, strict


def check_wait_on_nonincreasing_paths():
    cases = 0
    strict = 0
    price_paths = tuple(
        prices
        for prices in product((1.0, 2.0, 4.0), repeat=3)
        if prices[0] >= prices[1] >= prices[2]
    )
    for prices, deposits, terminal in product(
        price_paths,
        product((0.0, 1.0, 3.0), repeat=3),
        (0.5, 1.0, 3.0, 8.0),
    ):
        waiting = terminal_wealth(
            prices, deposits, wait_until_last_spends(deposits), terminal
        )
        dca = terminal_wealth(
            prices, deposits, dca_spends(deposits), terminal
        )
        assert waiting >= dca - 1e-10
        expected_strict = any(
            deposit > 0 and price > prices[-1]
            for price, deposit in zip(prices, deposits, strict=True)
        )
        assert (waiting > dca + 1e-10) == expected_strict
        strict += int(expected_strict)
        cases += 1
    return cases, strict


def main():
    identity_cases = check_gap_identity()
    witness_cases = check_adversarial_witness()
    prefix_witness_cases = check_prefix_adversarial_witness()
    oracle_cases, oracle_strict = check_oracle()
    wait_cases, wait_strict = check_wait_on_nonincreasing_paths()
    print(f"gap identity: {identity_cases} cases passed")
    print(f"adversarial witness: {witness_cases} cases passed")
    print(
        f"prefix adversarial witness: {prefix_witness_cases} cases passed"
    )
    print(
        f"future-min oracle: {oracle_cases} cases passed "
        f"({oracle_strict} strict)"
    )
    print(
        f"wait on nonincreasing paths: {wait_cases} cases passed "
        f"({wait_strict} strict)"
    )


if __name__ == "__main__":
    main()
