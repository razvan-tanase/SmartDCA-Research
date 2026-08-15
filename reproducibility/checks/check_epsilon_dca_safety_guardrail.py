#!/usr/bin/env python3
"""Exact finite checks for the sharp epsilon-DCA safety guardrail."""

from fractions import Fraction
from itertools import product


LAMBDAS = (Fraction(0), Fraction(1, 2), Fraction(3, 4), Fraction(1))
PRICES = (1, 2, 4)
DEPOSITS = (0, 1, 2)
EVALUATIONS = (1, 3, 9)


def feasible_schedules(deposits):
    """Yield integer-grid fully funded purchase schedules."""
    schedules = [((), 0)]
    for deposit in deposits:
        extended = []
        for purchases, cash in schedules:
            available = cash + deposit
            for purchase in range(available + 1):
                extended.append((purchases + (purchase,), available - purchase))
        schedules = extended
    for purchases, _ in schedules:
        yield purchases


def states(deposits, prices, purchases, lam):
    cash = 0
    units = Fraction(0)
    dca_units = Fraction(0)
    rows = []
    for deposit, price, purchase in zip(deposits, prices, purchases):
        available = cash + deposit
        assert 0 <= purchase <= available
        cushion = units - lam * dca_units
        minimum = max(Fraction(0), lam * deposit - price * cushion)
        cash = available - purchase
        units += Fraction(purchase, price)
        dca_units += Fraction(deposit, price)
        rows.append(
            {
                "available": Fraction(available),
                "minimum": minimum,
                "cash": Fraction(cash),
                "units": units,
                "dca_units": dca_units,
                "covered": units >= lam * dca_units,
                "guarded": purchase >= minimum,
            }
        )
    return rows


def terminal(row, evaluation):
    candidate = row["cash"] + evaluation * row["units"]
    dca = evaluation * row["dca_units"]
    return candidate, dca


def exhaustive_checks():
    schedules_checked = 0
    guarded_paths_checked = 0
    terminal_floors_checked = 0
    constant_paths_checked = 0
    adversarial_prefixes_checked = 0

    for horizon in (1, 2, 3):
        for deposits in product(DEPOSITS, repeat=horizon):
            for prices in product(PRICES, repeat=horizon):
                for purchases in feasible_schedules(deposits):
                    schedules_checked += 1
                    for lam in LAMBDAS:
                        rows = states(deposits, prices, purchases, lam)
                        prefix_coverage = True
                        prefix_guard = True
                        for t, row in enumerate(rows):
                            if prefix_coverage:
                                assert Fraction(0) <= row["minimum"] <= lam * deposits[t]
                                assert row["minimum"] <= row["available"]
                            assert row["covered"] == row["guarded"]
                            prefix_coverage = prefix_coverage and row["covered"]
                            prefix_guard = prefix_guard and row["guarded"]
                            assert prefix_coverage == prefix_guard

                            if not row["covered"] and lam > 0:
                                deficit = lam * row["dca_units"] - row["units"]
                                assert deficit > 0
                                remaining_dates = horizon - t - 1
                                future_deposits = remaining_dates
                                budget = row["cash"] + future_deposits
                                p = 2
                                while p * deficit <= 2 * budget:
                                    p *= 2
                                upper_gap = budget - p * deficit + Fraction(budget, p)
                                assert upper_gap < 0
                                adversarial_prefixes_checked += 1

                        if prefix_coverage:
                            guarded_paths_checked += 1
                            for evaluation in EVALUATIONS:
                                candidate, dca = terminal(rows[-1], evaluation)
                                assert candidate >= lam * dca
                                terminal_floors_checked += 1

                        if lam == 1 and prefix_coverage:
                            assert purchases == deposits
                        if lam == 0:
                            assert prefix_coverage

                    if len(set(prices)) == 1:
                        evaluation = prices[0]
                        row = states(deposits, prices, purchases, Fraction(1))[ -1]
                        candidate, dca = terminal(row, evaluation)
                        assert candidate == dca == sum(deposits)
                        constant_paths_checked += 1

    return {
        "schedules": schedules_checked,
        "guarded_path_lambda_cases": guarded_paths_checked,
        "terminal_floor_checks": terminal_floors_checked,
        "constant_price_checks": constant_paths_checked,
        "adversarial_prefix_checks": adversarial_prefixes_checked,
    }


def construction_checks():
    cases = 0
    strict_wins = 0
    strict_losses = 0
    for horizon in (1, 2, 3):
        for deposits in product(DEPOSITS, repeat=horizon):
            for prices in product(PRICES, repeat=horizon):
                for lam in LAMBDAS:
                    purchases = tuple(lam * deposit for deposit in deposits)
                    cash = Fraction(0)
                    units = Fraction(0)
                    dca_units = Fraction(0)
                    for deposit, price, purchase in zip(deposits, prices, purchases):
                        available = cash + deposit
                        cushion = units - lam * dca_units
                        minimum = max(Fraction(0), lam * deposit - price * cushion)
                        assert purchase == minimum
                        assert purchase <= available
                        cash = available - purchase
                        units += purchase / price
                        dca_units += Fraction(deposit, price)
                        assert units == lam * dca_units

                    for evaluation in EVALUATIONS:
                        candidate = cash + evaluation * units
                        dca = evaluation * dca_units
                        assert candidate >= lam * dca
                        if candidate > dca:
                            strict_wins += 1
                        elif candidate < dca:
                            strict_losses += 1
                        cases += 1
    assert strict_wins > 0
    assert strict_losses > 0
    return cases, strict_wins, strict_losses


def sharpness_checks():
    for lam in (Fraction(1, 10), Fraction(1, 2), Fraction(9, 10)):
        previous = None
        for evaluation in (10, 100, 1000, 10000):
            ratio = lam + (Fraction(1) - lam) / evaluation
            assert ratio > lam
            if previous is not None:
                assert ratio < previous
            previous = ratio
        assert previous - lam == (Fraction(1) - lam) / 10000


def numerical_examples():
    lam = Fraction(9, 10)
    deposits = (100, 100)
    purchases = (90, 90)
    examples = []
    for prices, evaluation in (((100, 80), 70), ((100, 120), 130)):
        row = states(deposits, prices, purchases, lam)[-1]
        candidate, dca = terminal(row, evaluation)
        assert candidate >= lam * dca
        examples.append((prices, evaluation, candidate, dca, lam * dca))
    assert examples[0][2] > examples[0][3]
    assert examples[1][2] < examples[1][3]
    return examples


def main():
    counts = exhaustive_checks()
    construction = construction_checks()
    sharpness_checks()
    examples = numerical_examples()

    print("All exact epsilon-DCA guardrail checks passed.")
    for name, count in counts.items():
        print(f"{name}: {count}")
    print(f"construction cases: {construction[0]}")
    print(f"construction strict wins/losses: {construction[1]}/{construction[2]}")
    for prices, evaluation, candidate, dca, floor in examples:
        print(
            "example",
            f"prices={prices}",
            f"evaluation={evaluation}",
            f"candidate={float(candidate):.6f}",
            f"dca={float(dca):.6f}",
            f"floor={float(floor):.6f}",
        )


if __name__ == "__main__":
    main()
