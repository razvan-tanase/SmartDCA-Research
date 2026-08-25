#!/usr/bin/env python3
"""Independent exact replay for the arbitrary-horizon publication review.

This file intentionally imports no SmartDCA repository module.  It implements
the f=id guarded corrected-mean and neutral ledgers directly from the public
financial-policy definitions, verifies the cash-timing and terminal-inventory
identities against direct portfolio accounting, and asserts the decisive
ticket 01--04 witness values quoted by the ticket-05 review.

The decisive witness set uses integer alpha/beta and the q=0 diagonal.  The
small exact-power helper rejects any non-rational intermediate instead of
rounding it.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


ExactFraction = Fraction
ZERO = ExactFraction(0)
HALF = ExactFraction(1, 2)
ONE = ExactFraction(1)


def exact_nth_root(value: int, degree: int) -> int:
    assert value >= 0 and degree >= 1
    if value in (0, 1):
        return value
    lo, hi = 0, 1
    while hi**degree < value:
        hi *= 2
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid**degree < value:
            lo = mid
        else:
            hi = mid
    if hi**degree != value:
        raise ArithmeticError(f"{value} has no exact {degree}-th root")
    return hi


def exact_power(base: ExactFraction, exponent: ExactFraction) -> ExactFraction:
    assert base > 0
    powered = base ** exponent.numerator
    return ExactFraction(
        exact_nth_root(powered.numerator, exponent.denominator),
        exact_nth_root(powered.denominator, exponent.denominator),
    )


def corrected_reference(values: tuple[ExactFraction, ...], alpha: ExactFraction, beta: ExactFraction) -> ExactFraction:
    assert values and all(value > 0 for value in values)
    if len(values) == 1:
        return values[0]
    if alpha == beta:
        # Every decisive diagonal witness has q=0, hence equal geometric weights.
        assert alpha == ZERO
        product = ONE
        for value in values:
            product *= value
        return exact_power(product, ExactFraction(1, len(values)))
    numerator = sum((exact_power(value, alpha) for value in values), ZERO)
    denominator = sum((exact_power(value, beta) for value in values), ZERO)
    return exact_power(numerator / denominator, ONE / (alpha - beta))


def corrected_score(relative_price: ExactFraction, alpha: ExactFraction) -> ExactFraction:
    return ONE / (ONE + exact_power(relative_price, ONE - alpha))


@dataclass(frozen=True)
class Policy:
    purchases: tuple[ExactFraction, ...]
    cash: tuple[ExactFraction, ...]
    units: tuple[ExactFraction, ...]
    raw_floors: tuple[ExactFraction | None, ...]
    floors: tuple[ExactFraction | None, ...]
    references: tuple[ExactFraction | None, ...]
    scores: tuple[ExactFraction | None, ...]
    wealth: ExactFraction


@dataclass(frozen=True)
class Replay:
    prices: tuple[ExactFraction, ...]
    deposits: tuple[ExactFraction, ...]
    evaluation_price: ExactFraction
    dca: Policy
    corrected: Policy
    neutral: Policy


def make_dca(prices: tuple[ExactFraction, ...], deposits: tuple[ExactFraction, ...], evaluation: ExactFraction) -> Policy:
    units = ZERO
    unit_path: list[ExactFraction] = []
    for price, deposit in zip(prices, deposits, strict=True):
        units += deposit / price
        unit_path.append(units)
    return Policy(
        purchases=deposits,
        cash=(ZERO,) * len(prices),
        units=tuple(unit_path),
        raw_floors=(None,) * len(prices),
        floors=(None,) * len(prices),
        references=(None,) * len(prices),
        scores=(None,) * len(prices),
        wealth=evaluation * units,
    )


def make_selector(
    prices: tuple[ExactFraction, ...],
    deposits: tuple[ExactFraction, ...],
    evaluation: ExactFraction,
    safety: ExactFraction,
    alpha: ExactFraction,
    beta: ExactFraction,
    dca: Policy,
    *,
    neutral: bool,
    guardrail: bool,
) -> Policy:
    cash = units = ZERO
    purchases: list[ExactFraction] = []
    cash_path: list[ExactFraction] = []
    unit_path: list[ExactFraction] = []
    raw_floors: list[ExactFraction] = []
    floors: list[ExactFraction] = []
    references: list[ExactFraction | None] = []
    scores: list[ExactFraction | None] = []
    anchor = prices[0]

    for index, (price, deposit) in enumerate(zip(prices, deposits, strict=True)):
        dca_units_before = ZERO if index == 0 else dca.units[index - 1]
        coverage_before = units - safety * dca_units_before
        available = cash + deposit
        raw_floor = safety * deposit - price * coverage_before
        floor = max(ZERO, raw_floor) if guardrail else ZERO
        discretionary = available - floor
        assert ZERO <= floor <= available

        if index == 0:
            reference = None
            score = HALF
        elif discretionary == ZERO:
            reference = None
            score = HALF if neutral else None
        else:
            lagged = tuple(past / anchor for past in prices[:index])
            reference = corrected_reference(lagged, alpha, beta)
            relative = (price / anchor) / reference
            score = HALF if neutral else corrected_score(relative, alpha)

        purchase = floor + (ZERO if score is None else score) * discretionary
        previous_cash = cash
        cash = available - purchase
        units += purchase / price
        assert purchase == deposit + previous_cash - cash
        assert cash >= ZERO
        if guardrail:
            assert units - safety * dca.units[index] >= ZERO

        purchases.append(purchase)
        cash_path.append(cash)
        unit_path.append(units)
        raw_floors.append(raw_floor)
        floors.append(floor)
        references.append(reference)
        scores.append(score)

    return Policy(
        purchases=tuple(purchases),
        cash=tuple(cash_path),
        units=tuple(unit_path),
        raw_floors=tuple(raw_floors),
        floors=tuple(floors),
        references=tuple(references),
        scores=tuple(scores),
        wealth=cash + evaluation * units,
    )


def replay(
    prices: tuple[ExactFraction, ...],
    evaluation: ExactFraction,
    safety: ExactFraction,
    alpha: ExactFraction,
    beta: ExactFraction,
    deposits: tuple[ExactFraction, ...] | None = None,
    *,
    guardrail: bool = True,
) -> Replay:
    deposits = deposits if deposits is not None else (ONE,) * len(prices)
    assert prices and len(prices) == len(deposits)
    assert all(price > ZERO for price in prices)
    assert all(deposit >= ZERO for deposit in deposits)
    assert evaluation > ZERO and ZERO < safety <= ONE
    dca = make_dca(prices, deposits, evaluation)
    corrected = make_selector(
        prices, deposits, evaluation, safety, alpha, beta, dca,
        neutral=False, guardrail=guardrail,
    )
    neutral = make_selector(
        prices, deposits, evaluation, safety, alpha, beta, dca,
        neutral=True, guardrail=guardrail,
    )
    result = Replay(prices, deposits, evaluation, dca, corrected, neutral)
    verify_identity_routes(result)
    return result


def policy(result: Replay, name: str) -> Policy:
    return {"dca": result.dca, "corrected": result.corrected, "neutral": result.neutral}[name]


def cash_timing_gap(result: Replay, left: str, right: str) -> ExactFraction:
    differences = tuple(
        a - b
        for a, b in zip(policy(result, left).cash, policy(result, right).cash, strict=True)
    )
    intermediate = sum(
        (
            result.evaluation_price
            * differences[index]
            * (ONE / result.prices[index + 1] - ONE / result.prices[index])
            for index in range(len(result.prices) - 1)
        ),
        ZERO,
    )
    terminal = differences[-1] * (ONE - result.evaluation_price / result.prices[-1])
    return intermediate + terminal


def direct_gap(result: Replay, left: str, right: str) -> ExactFraction:
    return policy(result, left).wealth - policy(result, right).wealth


def boundary(result: Replay, left: str, right: str) -> tuple[ExactFraction, ExactFraction]:
    left_policy, right_policy = policy(result, left), policy(result, right)
    cash_differences = tuple(
        a - b for a, b in zip(left_policy.cash, right_policy.cash, strict=True)
    )
    h_value = cash_differences[-1]
    reconstructed_u = sum(
        (
            cash_differences[index]
            * (ONE / result.prices[index + 1] - ONE / result.prices[index])
            for index in range(len(result.prices) - 1)
        ),
        ZERO,
    ) - cash_differences[-1] / result.prices[-1]
    unit_difference = left_policy.units[-1] - right_policy.units[-1]
    assert reconstructed_u == unit_difference
    assert direct_gap(result, left, right) == h_value + result.evaluation_price * unit_difference
    return h_value, unit_difference


def verify_identity_routes(result: Replay) -> None:
    for left, right in (
        ("corrected", "dca"),
        ("neutral", "dca"),
        ("corrected", "neutral"),
    ):
        assert direct_gap(result, left, right) == cash_timing_gap(result, left, right)
        boundary(result, left, right)


def cash_difference(result: Replay) -> tuple[ExactFraction, ...]:
    return tuple(
        corrected - neutral
        for corrected, neutral in zip(result.corrected.cash, result.neutral.cash, strict=True)
    )


def active_periods(item: Policy) -> tuple[int, ...]:
    return tuple(
        index
        for index, raw in enumerate(item.raw_floors, start=1)
        if raw is not None and raw > ZERO
    )


def classify(h_value: ExactFraction, u_value: ExactFraction, evaluation: ExactFraction) -> str:
    gap = h_value + evaluation * u_value
    return "win" if gap > ZERO else "loss" if gap < ZERO else "tie"


def check_accounting_seam() -> None:
    one = replay((ONE,), ExactFraction(3), HALF, ZERO, ZERO, (ExactFraction(2),))
    assert one.corrected.purchases == (ExactFraction(3, 2),)
    assert one.corrected.cash == (HALF,)
    assert direct_gap(one, "corrected", "dca") == -ONE

    flip = replay((ONE, ExactFraction(2)), ExactFraction(3, 2), HALF, ZERO, ZERO)
    assert flip.corrected.raw_floors[1] == ZERO  # exact clipping boundary
    assert direct_gap(flip, "corrected", "dca") == ExactFraction(1, 48)
    assert direct_gap(flip, "neutral", "dca") == -ExactFraction(1, 32)

    constant_gaps = tuple(
        direct_gap(replay((ONE, ONE), price, HALF, ZERO, ZERO), "corrected", "dca")
        for price in (HALF, ONE, ExactFraction(2))
    )
    assert constant_gaps == (ExactFraction(1, 4), ZERO, -HALF)

    all_win = replay((ONE, HALF), ExactFraction(500), HALF, ZERO, ZERO, (ONE, ZERO))
    assert all_win.corrected.cash[-1] == ExactFraction(1, 12)
    assert direct_gap(all_win, "corrected", "dca") == ExactFraction(167, 4)

    beta_common = ((ONE, ExactFraction(4), ExactFraction(2)), ExactFraction(7, 3), HALF, ZERO)
    beta_low = replay(*beta_common, -ONE)
    beta_high = replay(*beta_common, ONE)
    beta_diag = replay(*beta_common, ZERO)
    assert (
        beta_low.corrected.references[2],
        beta_low.corrected.scores[2],
        direct_gap(beta_low, "corrected", "dca"),
    ) == (ExactFraction(8, 5), ExactFraction(4, 9), -ExactFraction(1, 36))
    assert (
        beta_high.corrected.references[2],
        beta_high.corrected.scores[2],
        direct_gap(beta_high, "corrected", "dca"),
    ) == (ExactFraction(5, 2), ExactFraction(5, 9), ExactFraction(1, 144))
    assert (
        beta_diag.corrected.references[2],
        beta_diag.corrected.scores[2],
        direct_gap(beta_diag, "corrected", "dca"),
    ) == (ExactFraction(2), HALF, -ExactFraction(1, 96))


def check_falsification_witnesses() -> None:
    minimum_dca = replay((ONE,) * 4, ExactFraction(2), HALF, ZERO, -ONE)
    assert direct_gap(minimum_dca, "corrected", "dca") == -ExactFraction(7, 8)

    minimum_neutral = replay((ONE, ExactFraction(2, 3), ExactFraction(2, 3), ExactFraction(2, 3)), ExactFraction(1, 3), HALF, ZERO, -ONE)
    minimum_neutral_open = replay(
        minimum_neutral.prices, ExactFraction(1, 3), HALF, ZERO, -ONE, guardrail=False
    )
    guarded_gap = direct_gap(minimum_neutral, "corrected", "neutral")
    open_gap = direct_gap(minimum_neutral_open, "corrected", "neutral")
    assert (guarded_gap, open_gap, guarded_gap - open_gap) == (
        -ExactFraction(273, 5984), -ExactFraction(373, 5984), ExactFraction(25, 1496)
    )
    assert active_periods(minimum_neutral.corrected) == (1, 2)
    assert active_periods(minimum_neutral.neutral) == (1, 2, 3)

    genuine_dca = replay((ONE, ExactFraction(2, 3), ExactFraction(2, 3), ONE), ONE, HALF, ZERO, -ONE)
    strict_dca = replay((ONE, HALF, ExactFraction(2, 3), ONE), ONE, HALF, ZERO, -ONE)
    assert direct_gap(genuine_dca, "corrected", "dca") == -ExactFraction(49, 264)
    assert direct_gap(strict_dca, "corrected", "dca") == -ExactFraction(7, 32)

    strict_neutral = replay((ONE, ExactFraction(2, 3), ONE, ExactFraction(2)), ExactFraction(2), ExactFraction(3, 4), ZERO, -ONE)
    strict_neutral_open = replay(
        strict_neutral.prices, ExactFraction(2), ExactFraction(3, 4), ZERO, -ONE, guardrail=False
    )
    guarded_gap = direct_gap(strict_neutral, "corrected", "neutral")
    open_gap = direct_gap(strict_neutral_open, "corrected", "neutral")
    assert (guarded_gap, open_gap, guarded_gap - open_gap) == (
        -ExactFraction(109, 8640), ExactFraction(49, 360), -ExactFraction(257, 1728)
    )


def check_cash_mechanism_witnesses() -> None:
    minimum = replay((ONE, ExactFraction(2), ExactFraction(32), ExactFraction(32)), ExactFraction(32), ExactFraction(31, 32), -ONE, ZERO)
    assert cash_difference(minimum) == (ZERO, ExactFraction(3, 128), -ExactFraction(665, 147712), ExactFraction(3183, 308480))

    strict = replay((ONE, ExactFraction(1, 16), ONE, ExactFraction(8)), ExactFraction(8), ExactFraction(63, 64), -ONE, ZERO)
    strict_open = replay(strict.prices, ExactFraction(8), ExactFraction(63, 64), -ONE, ZERO, guardrail=False)
    assert cash_difference(strict) == (
        ZERO,
        -ExactFraction(12495, 1052672),
        ExactFraction(174032415, 616865792),
        -ExactFraction(142575068237, 2843751301120),
    )
    assert cash_difference(strict_open) == (
        ZERO, -ExactFraction(765, 1028), ExactFraction(70545, 602408), ExactFraction(585268881, 555420176)
    )

    common = replay((ONE, HALF, ExactFraction(2, 3), ONE), ONE, HALF, ZERO, -ONE)
    assert common.corrected.floors == common.neutral.floors
    assert cash_difference(common) == (ZERO, -ExactFraction(7, 48), -ExactFraction(7, 96), ExactFraction(41, 320))

    diagonal = replay((ONE, ExactFraction(1, 4), HALF, ONE), ONE, HALF, ZERO, ZERO)
    assert cash_difference(diagonal) == (ZERO, -ExactFraction(39, 160), -ExactFraction(39, 320), ExactFraction(389, 1920))

    aligned = replay((ONE, ExactFraction(1, 4), HALF, ONE), ONE, ExactFraction(7, 8), ZERO, -ONE)
    assert active_periods(aligned.corrected) == (1, 2, 3, 4)
    assert active_periods(aligned.neutral) == (1, 2, 3, 4)
    assert cash_difference(aligned) == (ZERO, -ExactFraction(39, 640), ExactFraction(133, 2304), ExactFraction(22903, 115200))

    nonnecessary = replay((ONE, ExactFraction(2, 3), HALF, ExactFraction(2, 3)), ExactFraction(2, 3), ExactFraction(3, 4), ZERO, -ONE)
    assert cash_difference(nonnecessary) == (ZERO, -ExactFraction(11, 240), -ExactFraction(397, 4992), ExactFraction(841, 149760))
    # Direct replay of the date-three score/floor forcing components.
    d_before = cash_difference(nonnecessary)[1]
    score_component = (
        (ONE - nonnecessary.corrected.scores[2])
        - (ONE - nonnecessary.neutral.scores[2])
    ) * (
        nonnecessary.neutral.cash[1] + ONE - nonnecessary.neutral.floors[2]
    )
    floor_component = (
        nonnecessary.neutral.floors[2] - nonnecessary.corrected.floors[2]
    ) * (ONE - nonnecessary.corrected.scores[2])
    # The decomposition is asserted by its independently reproduced exact values.
    assert d_before == -ExactFraction(11, 240)
    assert (score_component, floor_component) == (-ExactFraction(125, 1664), ExactFraction(11, 832))


def check_performance_boundary_witnesses() -> None:
    aligned = replay((ONE, ExactFraction(1, 4), HALF, ONE), HALF, ExactFraction(7, 8), ZERO, -ONE)
    assert boundary(aligned, "corrected", "dca") == (ExactFraction(16807, 28800), -ExactFraction(7199, 9600))
    assert boundary(aligned, "corrected", "neutral") == (ExactFraction(22903, 115200), -ExactFraction(5171, 38400))
    assert (
        direct_gap(aligned, "corrected", "dca"),
        direct_gap(aligned, "corrected", "neutral"),
    ) == (ExactFraction(12017, 57600), ExactFraction(30293, 230400))

    aligned_high = replay(aligned.prices, ExactFraction(2), ExactFraction(7, 8), ZERO, -ONE)
    assert (
        direct_gap(aligned_high, "corrected", "dca"),
        direct_gap(aligned_high, "corrected", "neutral"),
    ) == (-ExactFraction(26387, 28800), -ExactFraction(8123, 115200))

    aligned_loss = replay((ONE, ExactFraction(2, 3), ONE, ExactFraction(2)), ExactFraction(2), ExactFraction(3, 4), ZERO, -ONE)
    assert (
        direct_gap(aligned_loss, "corrected", "dca"),
        direct_gap(aligned_loss, "corrected", "neutral"),
    ) == (-ExactFraction(1141, 2160), -ExactFraction(109, 8640))

    all_price = replay((ONE, ExactFraction(2, 3), HALF, ExactFraction(2, 3)), ExactFraction(2, 3), ExactFraction(3, 4), ZERO, -ONE)
    assert boundary(all_price, "corrected", "neutral") == (ExactFraction(841, 149760), ExactFraction(841, 99840))
    assert (
        direct_gap(all_price, "corrected", "dca"),
        direct_gap(all_price, "corrected", "neutral"),
    ) == (ExactFraction(389, 18720), ExactFraction(841, 74880))

    terminal_negative = replay((ONE, ExactFraction(2, 3), HALF, ExactFraction(2, 3)), ExactFraction(2, 3), ExactFraction(1, 4), ZERO, -ONE)
    assert boundary(terminal_negative, "corrected", "neutral") == (-ExactFraction(103, 832), ExactFraction(2003, 8320))
    assert (
        direct_gap(terminal_negative, "corrected", "dca"),
        direct_gap(terminal_negative, "corrected", "neutral"),
    ) == (ExactFraction(57, 520), ExactFraction(229, 6240))

    flat_tie = replay((ONE, ONE, HALF, HALF), HALF, HALF, ZERO, -ONE)
    assert boundary(flat_tie, "corrected", "neutral") == (-ExactFraction(59, 240), ExactFraction(59, 120))
    assert (
        direct_gap(flat_tie, "corrected", "dca"),
        direct_gap(flat_tie, "corrected", "neutral"),
    ) == (ExactFraction(1, 4), ZERO)

    reversal = replay((ONE, ExactFraction(1, 16), ONE, ExactFraction(8)), ExactFraction(8), ExactFraction(63, 64), -ONE, ZERO)
    assert direct_gap(reversal, "corrected", "neutral") == -ExactFraction(339578505, 616865792)

    collapsed = replay((ONE, ExactFraction(2, 3), HALF, ExactFraction(2)), ExactFraction(3), ONE, ZERO, -ONE)
    for item in (collapsed.corrected, collapsed.neutral):
        assert item.purchases == collapsed.deposits
        assert item.cash == (ZERO,) * 4
    for right in ("dca", "neutral"):
        assert boundary(collapsed, "corrected", right) == (ZERO, ZERO)
        assert direct_gap(collapsed, "corrected", right) == ZERO

    # Exhaust the affine sign/zero branches independently of any witness.
    assert [classify(ONE, -ONE, price) for price in (HALF, ONE, ExactFraction(2))] == ["win", "tie", "loss"]
    assert [classify(-ONE, ONE, price) for price in (HALF, ONE, ExactFraction(2))] == ["loss", "tie", "win"]
    assert classify(ONE, ONE, ExactFraction(100)) == "win"
    assert classify(-ONE, -ONE, ExactFraction(100)) == "loss"
    assert classify(ZERO, ONE, ONE) == "win" and classify(ZERO, -ONE, ONE) == "loss"
    assert classify(ONE, ZERO, ONE) == "win" and classify(-ONE, ZERO, ONE) == "loss"
    assert classify(ZERO, ZERO, ONE) == "tie"


def check_additional_scope_routes() -> None:
    # Unequal deposits and a non-valley path; this is an identity audit, not a
    # performance-sign assertion.
    replay(
        (ONE, ExactFraction(4), ExactFraction(2), ExactFraction(3), ExactFraction(3, 2), ExactFraction(6)),
        ExactFraction(5, 2),
        ExactFraction(3, 4),
        ZERO,
        -ONE,
        (ONE, ZERO, ExactFraction(2), ONE, ZERO, ExactFraction(3)),
    )


def main() -> None:
    check_accounting_seam()
    check_falsification_witnesses()
    check_cash_mechanism_witnesses()
    check_performance_boundary_witnesses()
    check_additional_scope_routes()
    print("Independent arbitrary-horizon publication-review replay passed.")


if __name__ == "__main__":
    main()
