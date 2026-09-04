#!/usr/bin/env python3
"""Generate Chapter 7 and Appendix E assets from accepted synthetic runs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable


DETERMINISTIC_RUN_ID = (
    "smartdca-deterministic-v1-"
    "80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db"
)
STOCHASTIC_RUN_ID = (
    "smartdca-stochastic-v1-"
    "78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25"
)
DETERMINISTIC_MANIFEST_SHA256 = (
    "faf91057ab859c0d32c28ef61875f5095fe7fd470e5ddd939d3de48eccf4769e"
)
STOCHASTIC_MANIFEST_SHA256 = (
    "c9198fa41e9bc1e5114b8c7c5ee8fd9a8549f5ca241ebed3e8637cd984d5ad5b"
)
ASSET_NAMES = (
    "deterministic-evaluation.tex",
    "stochastic-evaluation.tex",
    "stochastic-mechanisms.tex",
    "synthetic-supplementary.tex",
)

PRIMARY_DETERMINISTIC_EPISODES = (
    ("constant-primary", "Constant"),
    ("monotone-rise-primary", "Monotone rise"),
    ("monotone-decline-primary", "Monotone decline"),
    ("weak-single-valley-primary", "Weak single valley"),
    ("strict-single-valley-primary", "Strict single valley"),
    ("incomplete-recovery-primary", "Incomplete recovery"),
    ("completed-recovery-primary", "Completed recovery"),
    ("multiple-valleys-primary", "Multiple valleys"),
    ("crash-primary", "Crash"),
    ("sudden-rebound-primary", "Sudden rebound"),
    ("prolonged-drawdown-primary", "Prolonged drawdown"),
    ("flat-segments-primary", "Flat segments"),
    ("hostile-carried-cash-primary", "Hostile carried cash"),
    ("hostile-adaptive-timing-primary", "Hostile adaptive timing"),
)
DETERMINISTIC_FIGURE_EPISODES = (
    ("monotone-rise-primary", "Monotone rise"),
    ("monotone-decline-primary", "Monotone decline"),
    ("multiple-valleys-primary", "Multiple valleys"),
    ("hostile-adaptive-timing-primary", "Hostile adaptive timing"),
)
STOCHASTIC_FAMILIES = (
    ("trend", "trend-positive-baseline", "Trend"),
    (
        "mean_reversion",
        "mean-reversion-twelve-month-baseline",
        "Mean reversion",
    ),
    (
        "stochastic_volatility",
        "stochastic-volatility-fifteen-percent-baseline",
        "Stochastic volatility",
    ),
    ("regime_switching", "regime-switching-baseline", "Regime switching"),
    ("jump_diffusion", "jump-diffusion-four-percent-baseline", "Jump diffusion"),
)
STOCHASTIC_SENSITIVITIES = (
    ("trend", "trend-negative-drift-sensitivity", "Negative trend"),
    (
        "mean_reversion",
        "mean-reversion-three-month-sensitivity",
        "Faster mean reversion",
    ),
    (
        "stochastic_volatility",
        "stochastic-volatility-thirty-five-percent-sensitivity",
        "Higher volatility",
    ),
    (
        "regime_switching",
        "regime-switching-persistent-bear-sensitivity",
        "Persistent bear regime",
    ),
    (
        "jump_diffusion",
        "jump-diffusion-twelve-percent-sensitivity",
        "More frequent jumps",
    ),
)
COMPARISONS = (
    ("corrected_guarded_vs_dca", "Corrected--DCA", "C--D"),
    (
        "corrected_guarded_vs_neutral_guarded",
        "Corrected--neutral",
        "C--N",
    ),
    ("neutral_guarded_vs_dca", "Neutral--DCA", "N--D"),
)


class SyntheticEvaluationAssetError(ValueError):
    """Raised when accepted evidence cannot produce the manuscript assets."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SyntheticEvaluationAssetError(f"cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise SyntheticEvaluationAssetError(f"expected JSON object in {path}")
    return value


def _require(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise SyntheticEvaluationAssetError(
            f"{label}: expected {expected!r}, found {actual!r}"
        )


def _verify_manifest_artifact(
    run_root: Path,
    manifest: dict[str, object],
    relative_path: str,
) -> Path:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise SyntheticEvaluationAssetError("run manifest has no artifact inventory")
    matches = [
        item
        for item in artifacts
        if isinstance(item, dict) and item.get("path") == relative_path
    ]
    if len(matches) != 1 or not isinstance(matches[0].get("sha256"), str):
        raise SyntheticEvaluationAssetError(
            f"manifest does not identify exactly one {relative_path} artifact"
        )
    artifact_path = run_root / relative_path
    _require(
        _sha256(artifact_path),
        matches[0]["sha256"],
        f"accepted artifact fingerprint for {relative_path}",
    )
    return artifact_path


def _decimal(value: object, label: str) -> Decimal:
    if not isinstance(value, str):
        raise SyntheticEvaluationAssetError(f"{label}: expected decimal string")
    try:
        return Decimal(value)
    except ArithmeticError as error:
        raise SyntheticEvaluationAssetError(f"{label}: invalid decimal {value!r}") from error


def _number(value: Decimal, places: int, *, signed: bool = False) -> str:
    quantum = Decimal(1).scaleb(-places)
    rounded = value.quantize(quantum, rounding=ROUND_HALF_UP)
    if rounded == 0:
        rounded = abs(rounded)
    prefix = "+" if signed and rounded > 0 else ""
    return f"{prefix}{rounded:.{places}f}"


def _percent(value: object, places: int = 3, *, signed: bool = True) -> str:
    decimal_value = value if isinstance(value, Decimal) else _decimal(value, "percentage")
    return f"{_number(decimal_value * 100, places, signed=signed)}\\%"


def _dollars(value: object) -> str:
    decimal_value = value if isinstance(value, Decimal) else _decimal(value, "dollars")
    rounded = decimal_value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    if rounded == 0:
        return "0"
    return f"{rounded:+.0f}"


def _load_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))
    except OSError as error:
        raise SyntheticEvaluationAssetError(f"cannot read {path}: {error}") from error


def _one_deterministic_row(
    rows: Iterable[dict[str, str]],
    *,
    episode_id: str,
    comparison: str,
    coverage: str = "0.75",
    cost_scenario: str = "frictionless",
) -> dict[str, str]:
    matches = [
        row
        for row in rows
        if row.get("episode_id") == episode_id
        and row.get("comparison") == comparison
        and row.get("coverage") == coverage
        and row.get("cost_scenario") == cost_scenario
    ]
    if len(matches) != 1:
        raise SyntheticEvaluationAssetError(
            "deterministic slice is not unique for "
            f"{episode_id}/{comparison}/{coverage}/{cost_scenario}"
        )
    return matches[0]


def _one_stochastic_group(
    groups: Iterable[dict[str, object]],
    *,
    analysis_tier: str,
    family: str,
    generator_config_id: str,
    comparison: str,
    coverage: str = "0.75",
    cost_scenario: str = "frictionless",
    horizon_months: int = 60,
) -> dict[str, object]:
    matches = [
        group
        for group in groups
        if group.get("analysis_tier") == analysis_tier
        and group.get("family") == family
        and group.get("generator_config_id") == generator_config_id
        and group.get("comparison") == comparison
        and group.get("coverage") == coverage
        and group.get("cost_scenario") == cost_scenario
        and group.get("horizon_months") == horizon_months
    ]
    if len(matches) != 1:
        raise SyntheticEvaluationAssetError(
            "stochastic slice is not unique for "
            f"{analysis_tier}/{generator_config_id}/{comparison}/{coverage}/"
            f"{cost_scenario}/{horizon_months}"
        )
    return matches[0]


def _header(run_id: str, source_sha256: str) -> list[str]:
    return [
        "% Generated by reproducibility.synthetic_evaluation_assets; do not edit.",
        f"% Accepted source run: {run_id}",
        f"% Accepted source artifact SHA-256: {source_sha256}",
        "",
    ]


def _bar_cell(
    value: Decimal,
    scale_mm: Decimal,
    *,
    negative_lane_mm: int = 25,
    positive_lane_mm: int = 62,
) -> str:
    width = abs(value) * scale_mm
    width_text = _number(width, 2)
    if value < 0:
        return (
            f"\\makebox[{negative_lane_mm}mm][r]{{\\rule{{{width_text}mm}}{{1.1ex}}}}"
            f"\\vrule height 1.5ex\\makebox[{positive_lane_mm}mm][l]{{}}"
        )
    return (
        f"\\makebox[{negative_lane_mm}mm][r]{{}}\\vrule height 1.5ex"
        f"\\makebox[{positive_lane_mm}mm][l]{{\\rule{{{width_text}mm}}{{1.1ex}}}}"
    )


def _render_deterministic_asset(
    rows: list[dict[str, str]], source_sha256: str
) -> str:
    lines = _header(DETERMINISTIC_RUN_ID, source_sha256)
    lines.extend(
        [
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \setlength{\tabcolsep}{2.8pt}",
            r"  \renewcommand{\arraystretch}{1.10}",
            r"  \resizebox{\textwidth}{!}{%",
            r"  \begin{tabular}{lrrrrrrr}",
            r"    \hline",
            r"    Family & Dates & C--D & C--N & N--D & Cash drag & Asset exposure & Floor active \\",
            r"    \hline",
        ]
    )
    for episode_id, family_label in PRIMARY_DETERMINISTIC_EPISODES:
        comparison_rows = {
            comparison: _one_deterministic_row(
                rows, episode_id=episode_id, comparison=comparison
            )
            for comparison, _, _ in COMPARISONS
        }
        complete = comparison_rows["corrected_guarded_vs_dca"]
        lines.append(
            "    "
            + " & ".join(
                (
                    family_label,
                    complete["left_purchase_count"],
                    _percent(complete["relative_terminal_wealth_gap"]),
                    _percent(
                        comparison_rows["corrected_guarded_vs_neutral_guarded"][
                            "relative_terminal_wealth_gap"
                        ]
                    ),
                    _percent(
                        comparison_rows["neutral_guarded_vs_dca"][
                            "relative_terminal_wealth_gap"
                        ]
                    ),
                    _percent(complete["left_cash_drag"], 1, signed=False),
                    _percent(complete["left_asset_exposure"], 1, signed=False),
                    _percent(
                        complete["left_guardrail_activation_frequency"],
                        1,
                        signed=False,
                    ),
                )
            )
            + r" \\"
        )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            r"  \caption{Primary deterministic catalog at frictionless $\lambda=0.75$ with the frozen identity corrected mean and one fixed episode per row. Dates is the number of purchase dates. C--D is the complete corrected policy versus DCA, C--N is its signal-only comparison with the neutral guarded selector, and N--D is the safety-architecture comparison; each relative gap uses its named right-hand policy as denominator and the three columns are not additive. Cash drag is terminal corrected cash divided by deposits, asset exposure is corrected asset value divided by terminal wealth, and floor active is the corrected policy's share of purchase dates with an active clipped floor. These fourteen designed paths are a finite catalog, not a probability sample.}",
            r"  \label{tab:deterministic-primary}",
            r"\end{table}",
            "",
            r"\begin{figure}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \resizebox{0.98\textwidth}{!}{%",
            r"  \begin{tabular}{llcr}",
            r"    \hline",
            r"    Path & Comparison & \multicolumn{1}{c}{Relative-gap bar (zero is the centre line)} & Gap \\",
            r"    \hline",
        ]
    )
    comparison_labels = {item[0]: item[2] for item in COMPARISONS}
    for episode_id, family_label in DETERMINISTIC_FIGURE_EPISODES:
        for comparison, _, _ in COMPARISONS:
            row = _one_deterministic_row(
                rows, episode_id=episode_id, comparison=comparison
            )
            value = _decimal(row["relative_terminal_wealth_gap"], "relative gap")
            lines.append(
                f"    {family_label} & {comparison_labels[comparison]} & "
                f"{_bar_cell(value * 100, Decimal('2'))} & "
                f"{_percent(value)} \\\\"
            )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            r"  \caption{Layer signs on four mechanism-representative deterministic paths from Table~\ref{tab:deterministic-primary}. C is the corrected guarded policy, N the neutral guarded selector, and D DCA; each X--Y relative terminal-wealth gap uses Y as its denominator. Bars share a zero line and a common two-millimetres-per-percentage-point scale, but the three comparisons are not an additive decomposition. Every row is one frictionless fixed path at $\lambda=0.75$ with the frozen identity corrected mean; selection for exposition does not create frequencies or inference.}",
            r"  \label{fig:deterministic-layers}",
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _render_stochastic_assets(
    groups: list[dict[str, object]], source_sha256: str
) -> tuple[str, str]:
    primary: dict[str, dict[str, dict[str, object]]] = {}
    for family, config_id, _ in STOCHASTIC_FAMILIES:
        primary[family] = {
            comparison: _one_stochastic_group(
                groups,
                analysis_tier="primary",
                family=family,
                generator_config_id=config_id,
                comparison=comparison,
            )
            for comparison, _, _ in COMPARISONS
        }

    lines = _header(STOCHASTIC_RUN_ID, source_sha256)
    lines.extend(
        [
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \setlength{\tabcolsep}{2.4pt}",
            r"  \renewcommand{\arraystretch}{1.12}",
            r"  \resizebox{\textwidth}{!}{%",
            r"  \begin{tabular}{lrrrrrrrr}",
            r"    \hline",
            r"    Family & $N$ & \multicolumn{3}{c}{Corrected--DCA} & \multicolumn{3}{c}{Corrected--neutral} & Neutral--DCA \\",
            r"    & & Median & 5\% downside & Worst & Median & 5\% downside & Worst & Median \\",
            r"    \hline",
        ]
    )
    for family, _, family_label in STOCHASTIC_FAMILIES:
        complete = primary[family]["corrected_guarded_vs_dca"]
        signal = primary[family]["corrected_guarded_vs_neutral_guarded"]
        architecture = primary[family]["neutral_guarded_vs_dca"]
        lines.append(
            "    "
            + " & ".join(
                (
                    family_label,
                    str(complete["sample_count"]),
                    _percent(complete["median_relative_terminal_wealth_gap"]),
                    _percent(complete["downside_quantile_0.05"]),
                    _percent(
                        complete["worst_observed_relative_shortfall"],
                        signed=False,
                    ),
                    _percent(signal["median_relative_terminal_wealth_gap"]),
                    _percent(signal["downside_quantile_0.05"]),
                    _percent(
                        signal["worst_observed_relative_shortfall"],
                        signed=False,
                    ),
                    _percent(architecture["median_relative_terminal_wealth_gap"]),
                )
            )
            + r" \\"
        )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            r"  \caption{Primary seeded-stochastic 60-month frictionless slice at $\lambda=0.75$ and the frozen identity corrected mean. Each family has $N=3$ saved paths, one per seed; medians and linearly interpolated 5\% quantiles are descriptive. Worst is the largest observed relative shortfall and is zero when all three gaps are nonnegative. Each percentage uses the named right-hand policy as denominator. The five controlled families are not calibrated market populations and do not support a win probability, expected return, or significance claim.}",
            r"  \label{tab:stochastic-primary}",
            r"\end{table}",
            "",
        ]
    )
    primary_asset = "\n".join(lines)

    lines = _header(STOCHASTIC_RUN_ID, source_sha256)
    lines.extend(
        [
            r"\begin{figure}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \resizebox{0.98\textwidth}{!}{%",
            r"  \begin{tabular}{llcr}",
            r"    \hline",
            r"    Family & Component & \multicolumn{1}{c}{Mean contribution in USD (zero is the centre line)} & USD \\",
            r"    \hline",
        ]
    )
    for family, _, family_label in STOCHASTIC_FAMILIES:
        complete = primary[family]["corrected_guarded_vs_dca"]
        for key, component in (
            ("mean_cash_contribution", "Terminal cash"),
            ("mean_unit_contribution", "$P$ times unit gap"),
        ):
            value = _decimal(complete[key], key)
            lines.append(
                f"    {family_label} & {component} & "
                f"{_bar_cell(value, Decimal('0.035'), negative_lane_mm=56, positive_lane_mm=45)} & "
                f"{_dollars(value)} \\\\"
            )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            r"  \caption{Terminal cash--unit attribution for corrected guarded versus DCA in the five primary 60-month stochastic cells. Each bar is the mean across the same three saved seeds at frictionless $\lambda=0.75$; terminal cash contribution plus the evaluation-price value of the terminal-unit gap reconstructs the mean signed terminal-wealth difference in dollars. Text values keep the sign and round only for display. The identity explains these realized ledgers but does not identify a market process.}",
            r"  \label{fig:stochastic-attribution}",
            r"\end{figure}",
            "",
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \renewcommand{\arraystretch}{1.12}",
            r"  \resizebox{\textwidth}{!}{%",
            r"  \begin{tabular}{lrrrrr}",
            r"    \hline",
            r"    Family & Floor active & Cash drag & Asset exposure & Cash contribution & Unit contribution \\",
            r"    \hline",
        ]
    )
    for family, _, family_label in STOCHASTIC_FAMILIES:
        complete = primary[family]["corrected_guarded_vs_dca"]
        lines.append(
            "    "
            + " & ".join(
                (
                    family_label,
                    _percent(
                        complete["mean_left_guardrail_activation_frequency"],
                        1,
                        signed=False,
                    ),
                    _percent(complete["mean_left_cash_drag"], 1, signed=False),
                    _percent(complete["mean_left_asset_exposure"], 1, signed=False),
                    f"{_dollars(complete['mean_cash_contribution'])} USD",
                    f"{_dollars(complete['mean_unit_contribution'])} USD",
                )
            )
            + r" \\"
        )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            r"  \caption{Corrected-policy mechanism diagnostics for the same five primary 60-month, frictionless, $\lambda=0.75$ cells as Table~\ref{tab:stochastic-primary}. Floor active is the mean share of 60 purchase dates with an active clipped floor; cash drag is terminal cash divided by deposits; asset exposure is asset value divided by terminal wealth; cash and unit columns are mean corrected-minus-DCA terminal-wealth contributions across three saved seeds.}",
            r"  \label{tab:stochastic-mechanisms}",
            r"\end{table}",
            "",
        ]
    )
    return primary_asset, "\n".join(lines)


def _sign_counts(values: Iterable[Decimal]) -> tuple[int, int, int]:
    materialized = list(values)
    return (
        sum(value < 0 for value in materialized),
        sum(value == 0 for value in materialized),
        sum(value > 0 for value in materialized),
    )


def _render_supplementary_asset(
    deterministic_rows: list[dict[str, str]],
    stochastic_groups: list[dict[str, object]],
    deterministic_manifest: dict[str, object],
    stochastic_manifest: dict[str, object],
    deterministic_validation: dict[str, object],
    stochastic_validation: dict[str, object],
    source_sha256: str,
) -> str:
    lines = _header(
        f"{DETERMINISTIC_RUN_ID} + {STOCHASTIC_RUN_ID}", source_sha256
    )
    lines.extend(
        [
            r"\section{Complete Deterministic Catalog Summaries}",
            r"\label{sec:supp-deterministic}",
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \renewcommand{\arraystretch}{1.10}",
            r"  \begin{tabular}{rllrrr}",
            r"    \hline",
            r"    Coverage & Comparison & Minimum & Maximum & \multicolumn{2}{c}{Loss / tie / win} \\",
            r"    \hline",
        ]
    )
    comparison_labels = {item[0]: item[1] for item in COMPARISONS}
    for coverage in ("0.9", "0.75", "0.5"):
        for comparison, _, _ in COMPARISONS:
            values = [
                _decimal(row["relative_terminal_wealth_gap"], "relative gap")
                for row in deterministic_rows
                if row["coverage"] == coverage
                and row["cost_scenario"] == "frictionless"
                and row["comparison"] == comparison
            ]
            _require(len(values), 18, f"deterministic catalog size at {coverage}")
            loss, tie, win = _sign_counts(values)
            lines.append(
                f"    {coverage} & {comparison_labels[comparison]} & "
                f"{_percent(min(values))} & {_percent(max(values))} & "
                f"\\multicolumn{{2}}{{c}}{{{loss} / {tie} / {win}}} \\\\"
            )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}",
            r"  \caption{Frictionless ranges and exact sign counts over all 18 fixed paths in the accepted deterministic catalog, including fourteen primary families, three boundary regressions, and one retained design iteration. Every row uses the frozen identity corrected mean; counts are finite catalog descriptions, not estimates of a path distribution.}",
            r"  \label{tab:deterministic-coverage-ranges}",
            r"\end{table}",
            "",
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \renewcommand{\arraystretch}{1.10}",
            r"  \begin{tabular}{llrrr}",
            r"    \hline",
            r"    Cost scope & Comparison & Minimum & Maximum & Loss / tie / win \\",
            r"    \hline",
        ]
    )
    cost_labels = {
        "frictionless": "Frictionless",
        "proportional-10bps": "Proportional 10 bps",
        "fixed-1-usd": "Fixed USD 1",
    }
    for cost_scenario in ("frictionless", "proportional-10bps", "fixed-1-usd"):
        for comparison, _, _ in COMPARISONS:
            values = [
                _decimal(row["relative_terminal_wealth_gap"], "relative gap")
                for row in deterministic_rows
                if row["coverage"] == "0.75"
                and row["cost_scenario"] == cost_scenario
                and row["comparison"] == comparison
            ]
            _require(len(values), 18, f"deterministic cost catalog {cost_scenario}")
            loss, tie, win = _sign_counts(values)
            lines.append(
                f"    {cost_labels[cost_scenario]} & {comparison_labels[comparison]} & "
                f"{_percent(min(values))} & {_percent(max(values))} & "
                f"{loss} / {tie} / {win} \\\\"
            )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}",
            r"  \caption{Net-of-cost range sensitivity at $\lambda=0.75$ over the same 18 fixed deterministic paths. The frictionless row is theorem-compatible finite validation. The proportional and fixed-fee rows are empirical net-performance calculations outside the current epsilon-DCA theorem; no frictional safety guarantee is asserted.}",
            r"  \label{tab:deterministic-cost-ranges}",
            r"\end{table}",
            "",
            r"\clearpage",
            r"\section{Seeded-Stochastic Sensitivities and Validation}",
            r"\label{sec:supp-stochastic}",
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \setlength{\tabcolsep}{2.4pt}",
            r"  \renewcommand{\arraystretch}{1.12}",
            r"  \resizebox{\textwidth}{!}{%",
            r"  \begin{tabular}{lrrrrrrrr}",
            r"    \hline",
            r"    Sensitivity & $N$ & \multicolumn{3}{c}{Corrected--DCA} & \multicolumn{3}{c}{Corrected--neutral} & Neutral--DCA \\",
            r"    & & Median & 5\% downside & Worst & Median & 5\% downside & Worst & Median \\",
            r"    \hline",
        ]
    )
    for family, config_id, label in STOCHASTIC_SENSITIVITIES:
        group_map = {
            comparison: _one_stochastic_group(
                stochastic_groups,
                analysis_tier="exploratory",
                family=family,
                generator_config_id=config_id,
                comparison=comparison,
            )
            for comparison, _, _ in COMPARISONS
        }
        complete = group_map["corrected_guarded_vs_dca"]
        signal = group_map["corrected_guarded_vs_neutral_guarded"]
        architecture = group_map["neutral_guarded_vs_dca"]
        lines.append(
            "    "
            + " & ".join(
                (
                    label,
                    str(complete["sample_count"]),
                    _percent(complete["median_relative_terminal_wealth_gap"]),
                    _percent(complete["downside_quantile_0.05"]),
                    _percent(
                        complete["worst_observed_relative_shortfall"],
                        signed=False,
                    ),
                    _percent(signal["median_relative_terminal_wealth_gap"]),
                    _percent(signal["downside_quantile_0.05"]),
                    _percent(
                        signal["worst_observed_relative_shortfall"],
                        signed=False,
                    ),
                    _percent(architecture["median_relative_terminal_wealth_gap"]),
                )
            )
            + r" \\"
        )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            r"  \caption{Exploratory stochastic sensitivities at the same 60-month, frictionless, $\lambda=0.75$ slice as Table~\ref{tab:stochastic-primary}. Each row has three saved seeds and remains separate from its primary family; the five rows are controlled process changes, not replacements selected after outcome access and not a pooled inferential sample.}",
            r"  \label{tab:stochastic-sensitivity}",
            r"\end{table}",
            "",
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \renewcommand{\arraystretch}{1.10}",
            r"  \begin{tabular}{rrrrr}",
            r"    \hline",
            r"    Coverage & Floor-active range & Cash-drag range & Asset-exposure range & C--D median range \\",
            r"    \hline",
        ]
    )
    for coverage in ("0.9", "0.75", "0.5"):
        groups_at_coverage = [
            _one_stochastic_group(
                stochastic_groups,
                analysis_tier="primary",
                family=family,
                generator_config_id=config_id,
                comparison="corrected_guarded_vs_dca",
                coverage=coverage,
            )
            for family, config_id, _ in STOCHASTIC_FAMILIES
        ]
        activation = [
            _decimal(group["mean_left_guardrail_activation_frequency"], "activation")
            for group in groups_at_coverage
        ]
        cash_drag = [
            _decimal(group["mean_left_cash_drag"], "cash drag")
            for group in groups_at_coverage
        ]
        exposure = [
            _decimal(group["mean_left_asset_exposure"], "exposure")
            for group in groups_at_coverage
        ]
        medians = [
            _decimal(group["median_relative_terminal_wealth_gap"], "median")
            for group in groups_at_coverage
        ]
        lines.append(
            f"    {coverage} & {_percent(min(activation), 1, signed=False)}--"
            f"{_percent(max(activation), 1, signed=False)} & "
            f"{_percent(min(cash_drag), 1, signed=False)}--"
            f"{_percent(max(cash_drag), 1, signed=False)} & "
            f"{_percent(min(exposure), 1, signed=False)}--"
            f"{_percent(max(exposure), 1, signed=False)} & "
            f"{_percent(min(medians))}--{_percent(max(medians))} \\\\"
        )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}",
            r"  \caption{Safety-factor diagnostics across the five primary 60-month stochastic families under the frozen identity corrected mean and frictionless costs. Each range is over five family summaries, each based on the same three saved seeds. Floor active is the mean share of 60 purchase dates at which the corrected guarded policy's clipped floor binds; cash drag is its terminal cash divided by total deposits; and asset exposure is its terminal asset value divided by terminal wealth. C--D is the corrected guarded versus DCA median relative terminal-wealth gap, with DCA as denominator. Lower coverage reduced observed floor activation in this grid, while the complete-system median range changed non-monotonically; the family summaries are not pooled into a new sample or test.}",
            r"  \label{tab:stochastic-coverage-diagnostics}",
            r"\end{table}",
            "",
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \renewcommand{\arraystretch}{1.12}",
            r"  \resizebox{\textwidth}{!}{%",
            r"  \begin{tabular}{lrrrrl}",
            r"    \hline",
            r"    Layer & Attempted paths & Generated & Excluded & Ledgers / comparisons & Declared role \\",
            r"    \hline",
            (
                "    Deterministic & "
                f"{deterministic_manifest['attempted_path_count']} & "
                f"{deterministic_manifest['generated_path_count']} & "
                f"{deterministic_manifest['excluded_path_count']} & "
                f"{deterministic_validation['ledger_count']} / "
                f"{deterministic_validation['episode_result_count']} & "
                r"finite catalog and exact regressions \\"
            ),
            (
                "    Seeded stochastic & "
                f"{stochastic_manifest['attempted_path_count']} & "
                f"{stochastic_manifest['generated_path_count']} & "
                f"{stochastic_manifest['excluded_path_count']} & "
                f"{stochastic_validation['ledger_count']} / "
                f"{stochastic_validation['episode_result_count']} & "
                r"controlled three-seed sensitivity \\"
            ),
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            r"  \caption{Accepted synthetic evidence inventory. Deterministic exclusions are three typed pre-policy input or predicate rejections; the stochastic run has none. Ledgers and three ordered comparison rows share the same counts because each scenario executes three policies and emits the three declared comparisons. Counts remain within their layer and are never combined into a significance claim.}",
            r"  \label{tab:synthetic-validation-inventory}",
            r"\end{table}",
            r"\clearpage",
            "",
        ]
    )
    return "\n".join(lines)


def generate_synthetic_evaluation_assets(
    repository_root: Path, output_directory: Path
) -> dict[str, object]:
    """Regenerate presentation assets from the two accepted immutable bundles."""

    root = repository_root.resolve()
    deterministic_root = root / "reports/experiments/runs" / DETERMINISTIC_RUN_ID
    stochastic_root = root / "reports/experiments/runs" / STOCHASTIC_RUN_ID
    deterministic_manifest_path = deterministic_root / "manifest.json"
    stochastic_manifest_path = stochastic_root / "manifest.json"
    _require(
        _sha256(deterministic_manifest_path),
        DETERMINISTIC_MANIFEST_SHA256,
        "deterministic manifest fingerprint",
    )
    _require(
        _sha256(stochastic_manifest_path),
        STOCHASTIC_MANIFEST_SHA256,
        "stochastic manifest fingerprint",
    )
    deterministic_manifest = _read_json(deterministic_manifest_path)
    stochastic_manifest = _read_json(stochastic_manifest_path)
    _require(
        deterministic_manifest.get("study_run_id"),
        DETERMINISTIC_RUN_ID,
        "deterministic run identity",
    )
    _require(
        stochastic_manifest.get("study_run_id"),
        STOCHASTIC_RUN_ID,
        "stochastic run identity",
    )
    _require(
        (
            deterministic_manifest.get("attempted_path_count"),
            deterministic_manifest.get("generated_path_count"),
            deterministic_manifest.get("excluded_path_count"),
        ),
        (21, 18, 3),
        "deterministic population counts",
    )
    _require(
        (
            stochastic_manifest.get("attempted_path_count"),
            stochastic_manifest.get("generated_path_count"),
            stochastic_manifest.get("excluded_path_count"),
        ),
        (90, 90, 0),
        "stochastic population counts",
    )
    seeds = stochastic_manifest.get("seeds")
    _require(seeds, [104729, 130363, 155921], "stochastic saved seeds")

    deterministic_csv = _verify_manifest_artifact(
        deterministic_root, deterministic_manifest, "mechanism-attribution.csv"
    )
    deterministic_boundary = _verify_manifest_artifact(
        deterministic_root, deterministic_manifest, "boundary-fixtures.json"
    )
    stochastic_aggregates_path = _verify_manifest_artifact(
        stochastic_root, stochastic_manifest, "stochastic-aggregates.json"
    )
    deterministic_validation_path = _verify_manifest_artifact(
        deterministic_root, deterministic_manifest, "runner/validation.json"
    )
    stochastic_validation_path = _verify_manifest_artifact(
        stochastic_root, stochastic_manifest, "runner/validation.json"
    )
    deterministic_rows = _load_csv(deterministic_csv)
    stochastic_aggregates = _read_json(stochastic_aggregates_path)
    stochastic_groups = stochastic_aggregates.get("groups")
    if not isinstance(stochastic_groups, list) or not all(
        isinstance(group, dict) for group in stochastic_groups
    ):
        raise SyntheticEvaluationAssetError("stochastic aggregate groups are invalid")
    _require(len(stochastic_groups), 1080, "stochastic aggregate-cell count")
    _require(
        stochastic_aggregates.get("group_count"),
        1080,
        "stochastic declared aggregate-cell count",
    )
    boundary_receipt = _read_json(deterministic_boundary)
    _require(boundary_receipt.get("status"), "passed", "boundary receipt status")
    _require(
        boundary_receipt.get("evidence_scope"),
        "finite-regression-not-proof",
        "boundary receipt scope",
    )
    deterministic_validation = _read_json(deterministic_validation_path)
    stochastic_validation = _read_json(stochastic_validation_path)
    _require(
        (deterministic_validation.get("status"), deterministic_validation.get("ledger_count"), deterministic_validation.get("episode_result_count")),
        ("passed", 648, 648),
        "deterministic runner validation",
    )
    _require(
        (stochastic_validation.get("status"), stochastic_validation.get("ledger_count"), stochastic_validation.get("episode_result_count")),
        ("passed", 3240, 3240),
        "stochastic runner validation",
    )

    stochastic_primary_asset, stochastic_mechanism_asset = (
        _render_stochastic_assets(
            stochastic_groups, _sha256(stochastic_aggregates_path)
        )
    )
    assets = {
        "deterministic-evaluation.tex": _render_deterministic_asset(
            deterministic_rows, _sha256(deterministic_csv)
        ),
        "stochastic-evaluation.tex": stochastic_primary_asset,
        "stochastic-mechanisms.tex": stochastic_mechanism_asset,
        "synthetic-supplementary.tex": _render_supplementary_asset(
            deterministic_rows,
            stochastic_groups,
            deterministic_manifest,
            stochastic_manifest,
            deterministic_validation,
            stochastic_validation,
            hashlib.sha256(
                deterministic_csv.read_bytes()
                + stochastic_aggregates_path.read_bytes()
                + deterministic_boundary.read_bytes()
            ).hexdigest(),
        ),
    }
    output = output_directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    for asset_name in ASSET_NAMES:
        (output / asset_name).write_text(assets[asset_name], encoding="utf-8")

    return {
        "status": "passed",
        "deterministic_run_id": DETERMINISTIC_RUN_ID,
        "stochastic_run_id": STOCHASTIC_RUN_ID,
        "deterministic_generated_path_count": deterministic_manifest[
            "generated_path_count"
        ],
        "deterministic_excluded_path_count": deterministic_manifest[
            "excluded_path_count"
        ],
        "stochastic_generated_path_count": stochastic_manifest[
            "generated_path_count"
        ],
        "stochastic_excluded_path_count": stochastic_manifest[
            "excluded_path_count"
        ],
        "stochastic_primary_seed_count": len(seeds),
        "stochastic_aggregate_cell_count": len(stochastic_groups),
        "asset_names": list(ASSET_NAMES),
        "asset_sha256": {
            asset_name: _sha256(output / asset_name) for asset_name in ASSET_NAMES
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "manuscript/generated",
    )
    args = parser.parse_args()
    try:
        receipt = generate_synthetic_evaluation_assets(
            args.repository_root, args.output_directory
        )
    except SyntheticEvaluationAssetError as error:
        print(f"SYNTHETIC MANUSCRIPT ASSET GENERATION FAILED\n{error}")
        return 1
    print(
        "SYNTHETIC MANUSCRIPT ASSET GENERATION PASSED: "
        f"{len(receipt['asset_names'])} assets"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
