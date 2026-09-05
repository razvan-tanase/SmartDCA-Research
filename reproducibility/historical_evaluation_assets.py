#!/usr/bin/env python3
"""Generate Chapter 8 and Appendix E assets from accepted historical runs."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable


PRIMARY_RUN_ID = (
    "smartdca-historical-study-v1-"
    "5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221"
)
ROBUSTNESS_RUN_ID = (
    "smartdca-historical-robustness-v1-"
    "0991d999e1a8070a2a6eb8046b08a91d0e42341995610a602372c52dfab14184"
)
PRIMARY_MANIFEST_SHA256 = (
    "d94b94375ede88757b3e485b7db0f09393778dbaed7477914c846766da6d9184"
)
ROBUSTNESS_MANIFEST_SHA256 = (
    "48dcdf94979b216b29f6cafa64349d5917c42042bc92a2ef4ac039a544e9f567"
)
ASSET_NAMES = (
    "historical-primary.tex",
    "historical-mechanisms.tex",
    "historical-robustness.tex",
    "historical-supplementary.tex",
)
DATASETS = (
    ("btc-usd-daily", "BTC-USD"),
    ("spy-adjusted-daily", "SPY"),
)
PRIMARY_HORIZONS = (12, 36, 60)
PRIMARY_COVERAGES = ("0.5", "0.75", "0.9")
COMPARISONS = (
    ("corrected_guarded_vs_dca", "H1", "Corrected--DCA"),
    (
        "corrected_guarded_vs_neutral_guarded",
        "H2",
        "Corrected--neutral",
    ),
    ("neutral_guarded_vs_dca", "S1", "Neutral--DCA"),
)
MONTHLY_ROBUSTNESS_SCHEDULE = "primary-monthly-robustness-coverage"
QUARTERLY_ROBUSTNESS_SCHEDULE = "robustness-quarterly-horizons"


class HistoricalEvaluationAssetError(ValueError):
    """Raised when accepted evidence cannot produce the historical assets."""


@dataclass(frozen=True)
class HistoricalCellKey:
    """Typed identity shared by an aggregate and its uncertainty record."""

    dataset_id: str
    horizon_months: int
    coverage: str
    comparison: str
    corrected_mean_config: str
    cost_scenario: str


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise HistoricalEvaluationAssetError(f"cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise HistoricalEvaluationAssetError(f"expected JSON object in {path}")
    return value


def _require(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise HistoricalEvaluationAssetError(
            f"{label}: expected {expected!r}, found {actual!r}"
        )


def _verify_manifest_artifact(
    run_root: Path,
    manifest: dict[str, object],
    relative_path: str,
) -> Path:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise HistoricalEvaluationAssetError("run manifest has no artifact inventory")
    matches = [
        item
        for item in artifacts
        if isinstance(item, dict) and item.get("path") == relative_path
    ]
    if len(matches) != 1 or not isinstance(matches[0].get("sha256"), str):
        raise HistoricalEvaluationAssetError(
            f"manifest does not identify exactly one {relative_path} artifact"
        )
    path = run_root / relative_path
    _require(
        _sha256(path),
        matches[0]["sha256"],
        f"accepted artifact fingerprint for {relative_path}",
    )
    return path


def _objects(value: object, label: str) -> list[dict[str, object]]:
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise HistoricalEvaluationAssetError(f"{label}: expected a list of objects")
    return value


def _decimal(value: object, label: str) -> Decimal:
    if not isinstance(value, str):
        raise HistoricalEvaluationAssetError(f"{label}: expected a decimal string")
    try:
        return Decimal(value)
    except ArithmeticError as error:
        raise HistoricalEvaluationAssetError(
            f"{label}: invalid decimal {value!r}"
        ) from error


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


def _range(rows: Iterable[dict[str, object]], key: str) -> tuple[Decimal, Decimal]:
    values = [_decimal(row.get(key), key) for row in rows]
    if not values:
        raise HistoricalEvaluationAssetError(f"cannot take empty range for {key}")
    return min(values), max(values)


def _sign_counts(
    rows: Iterable[dict[str, object]], key: str = "median_relative_terminal_wealth_gap"
) -> tuple[int, int, int]:
    values = [_decimal(row.get(key), key) for row in rows]
    return (
        sum(value < 0 for value in values),
        sum(value == 0 for value in values),
        sum(value > 0 for value in values),
    )


def _cell_key(row: dict[str, object]) -> HistoricalCellKey:
    string_fields = {
        name: row.get(name)
        for name in (
            "dataset_id",
            "coverage",
            "comparison",
            "corrected_mean_config",
            "cost_scenario",
        )
    }
    invalid = [name for name, value in string_fields.items() if not isinstance(value, str)]
    horizon = row.get("horizon_months")
    if not isinstance(horizon, int):
        invalid.append("horizon_months")
    if invalid:
        raise HistoricalEvaluationAssetError(
            f"historical cell has invalid coordinates: {', '.join(invalid)}"
        )
    return HistoricalCellKey(
        dataset_id=string_fields["dataset_id"],
        horizon_months=horizon,
        coverage=string_fields["coverage"],
        comparison=string_fields["comparison"],
        corrected_mean_config=string_fields["corrected_mean_config"],
        cost_scenario=string_fields["cost_scenario"],
    )


def _sorted_cells(rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    dataset_order = {identifier: index for index, (identifier, _) in enumerate(DATASETS)}
    comparison_order = {
        identifier: index for index, (identifier, _, _) in enumerate(COMPARISONS)
    }
    return sorted(
        rows,
        key=lambda row: (
            dataset_order.get(str(row.get("dataset_id")), 99),
            int(row.get("horizon_months", 0)),
            Decimal(str(row.get("coverage"))),
            comparison_order.get(str(row.get("comparison")), 99),
        ),
    )


def _primary_cells(
    groups: list[dict[str, object]], comparison: str
) -> list[dict[str, object]]:
    rows = [
        group
        for group in groups
        if group.get("analysis_tier") == "confirmatory"
        and group.get("comparison") == comparison
        and group.get("corrected_mean_config") == "identity-a0-b0"
        and group.get("cost_scenario") == "frictionless"
        and group.get("coverage") in PRIMARY_COVERAGES
    ]
    _require(len(rows), 18, f"primary {comparison} cell count")
    return _sorted_cells(rows)


def _architecture_cells(
    groups: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows = [
        group
        for group in groups
        if group.get("analysis_tier") == "secondary"
        and group.get("comparison") == "neutral_guarded_vs_dca"
        and group.get("corrected_mean_config") == "identity-a0-b0"
        and group.get("cost_scenario") == "frictionless"
        and group.get("coverage") in PRIMARY_COVERAGES
    ]
    _require(len(rows), 18, "primary architecture-only cell count")
    return _sorted_cells(rows)


def _robustness_cells(
    groups: list[dict[str, object]],
    *,
    schedule: str,
    comparison: str,
    cost_scenario: str = "frictionless",
) -> list[dict[str, object]]:
    rows = [
        group
        for group in groups
        if group.get("analysis_tier") == "robustness"
        and group.get("schedule_id") == schedule
        and group.get("comparison") == comparison
        and group.get("corrected_mean_config") == "identity-a0-b0"
        and group.get("cost_scenario") == cost_scenario
        and group.get("coverage") != "1"
    ]
    expected = 30 if schedule == MONTHLY_ROBUSTNESS_SCHEDULE else 48
    _require(len(rows), expected, f"{schedule}/{comparison}/{cost_scenario} count")
    return _sorted_cells(rows)


def _dataset_label(identifier: object) -> str:
    labels = dict(DATASETS)
    try:
        return labels[str(identifier)]
    except KeyError as error:
        raise HistoricalEvaluationAssetError(
            f"unknown historical dataset {identifier!r}"
        ) from error


def _coverage_label(value: object) -> str:
    coverage = Decimal(str(value))
    return _number(coverage, 2).rstrip("0").rstrip(".")


def _comparison_label(identifier: object) -> str:
    labels = {key: label for key, _, label in COMPARISONS}
    try:
        return labels[str(identifier)]
    except KeyError as error:
        raise HistoricalEvaluationAssetError(
            f"unknown historical comparison {identifier!r}"
        ) from error


def _header(run_ids: str, source_sha256: str) -> list[str]:
    return [
        "% Generated by reproducibility.historical_evaluation_assets; do not edit.",
        f"% Accepted source run(s): {run_ids}",
        f"% Accepted source artifact digest: {source_sha256}",
        "",
    ]


def _bar_cell(value: Decimal, scale_mm: Decimal = Decimal("4")) -> str:
    width = abs(value) * scale_mm
    width_text = _number(width, 2)
    if value < 0:
        return (
            f"\\makebox[21mm][r]{{\\rule{{{width_text}mm}}{{1.05ex}}}}"
            r"\vrule height 1.45ex\makebox[3mm][l]{}"
        )
    return (
        r"\makebox[21mm][r]{}\vrule height 1.45ex"
        f"\\makebox[3mm][l]{{\\rule{{{width_text}mm}}{{1.05ex}}}}"
    )


def _uncertainty_index(
    cells: list[dict[str, object]],
) -> dict[HistoricalCellKey, dict[str, object]]:
    index: dict[HistoricalCellKey, dict[str, object]] = {}
    for cell in cells:
        key = _cell_key(cell)
        if key in index:
            raise HistoricalEvaluationAssetError(f"duplicate uncertainty cell {key}")
        index[key] = cell
    return index


def _render_primary_asset(
    h1: list[dict[str, object]],
    h2: list[dict[str, object]],
    uncertainty: dict[HistoricalCellKey, dict[str, object]],
    source_sha256: str,
) -> str:
    lines = _header(PRIMARY_RUN_ID, source_sha256)
    lines.extend(
        [
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \setlength{\tabcolsep}{3.0pt}",
            r"  \renewcommand{\arraystretch}{1.12}",
            r"  \resizebox{\textwidth}{!}{%",
            r"  \begin{tabular}{lrrrrrr}",
            r"    \hline",
            r"    Dataset & Horizon & $N$ & H1 median range & H1 rejected $\lambda$ & H2 median range & H2 rejected $\lambda$ \\",
            r"    \hline",
        ]
    )
    for dataset_id, dataset_label in DATASETS:
        for horizon in PRIMARY_HORIZONS:
            h1_group = [
                row
                for row in h1
                if row["dataset_id"] == dataset_id
                and row["horizon_months"] == horizon
            ]
            h2_group = [
                row
                for row in h2
                if row["dataset_id"] == dataset_id
                and row["horizon_months"] == horizon
            ]
            h1_range = _range(h1_group, "median_relative_terminal_wealth_gap")
            h2_range = _range(h2_group, "median_relative_terminal_wealth_gap")
            sample_counts = {row["sample_count"] for row in h1_group + h2_group}
            _require(len(sample_counts), 1, f"{dataset_id}/{horizon} sample count")
            significant = []
            for row in h1_group:
                adjusted = _decimal(
                    uncertainty[_cell_key(row)].get("holm_adjusted_p_value"),
                    "Holm-adjusted p-value",
                )
                if adjusted < Decimal("0.05"):
                    significant.append(_coverage_label(row["coverage"]))
            lines.append(
                "    "
                + " & ".join(
                    (
                        dataset_label,
                        str(horizon),
                        str(next(iter(sample_counts))),
                        f"{_percent(h1_range[0])} to {_percent(h1_range[1])}",
                        ", ".join(significant) if significant else "none",
                        f"{_percent(h2_range[0])} to {_percent(h2_range[1])}",
                        "none",
                    )
                )
                + r" \\"
            )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            r"  \caption{Sealed primary monthly historical results under the frozen identity corrected mean, frictionless accounting, and non-unit $\lambda\in\{0.5,0.75,0.9\}$. $N$ is the number of ordered overlapping episode starts in each individual cell, not an independent-history count. H1 is corrected guarded versus DCA; H2 is corrected guarded versus the neutral guarded selector, and each relative gap uses its named right-hand policy as denominator. Ranges are over the three coverage-specific medians. Rejected values use two-sided $p<0.05$ after Holm adjustment over one sealed 36-test H1/H2 family; no H2 cell was rejected. Cellwise intervals and adjusted values appear in Appendix Tables~\ref{tab:historical-h1-cells}--\ref{tab:historical-h2-cells}.}",
            r"  \label{tab:historical-primary}",
            r"\end{table}",
            "",
            r"\begin{figure}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \renewcommand{\arraystretch}{1.05}",
            r"  \begin{tabular}{llcr}",
            r"    \hline",
            r"    Cell & $\lambda$ & \multicolumn{1}{c}{H1 median gap (zero is the centre line)} & Median \\",
            r"    \hline",
        ]
    )
    for row in h1:
        value = _decimal(
            row["median_relative_terminal_wealth_gap"], "H1 median relative gap"
        )
        lines.append(
            f"    {_dataset_label(row['dataset_id'])} {row['horizon_months']} months & "
            f"{_coverage_label(row['coverage'])} & {_bar_cell(value * 100)} & "
            f"{_percent(value)} \\\\"
        )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}",
            r"  \caption{All eighteen H1 complete-system median relative terminal-wealth gaps in the sealed primary frictionless run. Each bar is corrected guarded minus DCA divided by DCA wealth for one dataset--horizon--coverage cell; all bars share a zero line and a common four-millimetres-per-percentage-point scale. The ordered overlapping starts within a cell are dependent, the bars are point estimates rather than confidence intervals, and their signs do not establish universal or causal inferiority.}",
            r"  \label{fig:historical-primary-effects}",
            r"\end{figure}",
            r"\FloatBarrier",
            "",
        ]
    )
    return "\n".join(lines)


def _render_mechanism_asset(
    h1: list[dict[str, object]],
    h2: list[dict[str, object]],
    architecture: list[dict[str, object]],
    source_sha256: str,
) -> str:
    lines = _header(PRIMARY_RUN_ID, source_sha256)
    lines.extend(
        [
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \setlength{\tabcolsep}{3.2pt}",
            r"  \renewcommand{\arraystretch}{1.12}",
            r"  \resizebox{\textwidth}{!}{%",
            r"  \begin{tabular}{llrrrrl}",
            r"    \hline",
            r"    Tier & Comparison & Cells & Negative & Zero & Positive & Median range / role \\",
            r"    \hline",
        ]
    )
    tier_rows = (
        ("H1", "Corrected--DCA", h1, "registered complete system"),
        ("H2", "Corrected--neutral", h2, "registered signal only"),
        ("S1", "Neutral--DCA", architecture, "descriptive architecture only"),
    )
    for tier, comparison, rows, role in tier_rows:
        negative, zero, positive = _sign_counts(rows)
        lower, upper = _range(rows, "median_relative_terminal_wealth_gap")
        lines.append(
            f"    {tier} & {comparison} & {len(rows)} & {negative} & {zero} & {positive} & "
            f"{_percent(lower)} to {_percent(upper)}; {role} \\\\"
        )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            r"  \caption{Comparison-tier separation for the eighteen non-unit primary frictionless cells. Corrected--DCA uses DCA wealth as denominator; corrected--neutral uses neutral guarded wealth; neutral--DCA uses DCA wealth. H1 and H2 share the registered Holm family, whereas S1 has no significance decision and is not a causal decomposition. Complete-system significance is never transferred to the signal-only or architecture-only tier.}",
            r"  \label{tab:historical-comparison-tiers}",
            r"\end{table}",
            "",
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \setlength{\tabcolsep}{3.2pt}",
            r"  \renewcommand{\arraystretch}{1.12}",
            r"  \resizebox{\textwidth}{!}{%",
            r"  \begin{tabular}{lrrrr}",
            r"    \hline",
            r"    Guarded policy & Cells & Mean cash drag & Mean asset exposure & Mean floor activation \\",
            r"    \hline",
        ]
    )
    for policy_label, rows in (
        ("Corrected", h1),
        ("Neutral", architecture),
    ):
        cash_drag = _range(rows, "mean_left_cash_drag")
        exposure = _range(rows, "mean_left_asset_exposure")
        activation = _range(rows, "mean_left_guardrail_activation_frequency")
        lines.append(
            f"    {policy_label} & {len(rows)} & "
            f"{_percent(cash_drag[0], signed=False)}--{_percent(cash_drag[1], signed=False)} & "
            f"{_percent(exposure[0], signed=False)}--{_percent(exposure[1], signed=False)} & "
            f"{_percent(activation[0], signed=False)}--{_percent(activation[1], signed=False)} \\\\"
        )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            r"  \caption{Policy mechanisms across the eighteen non-unit primary frictionless cells. Cash drag is terminal policy cash divided by contributed deposits, asset exposure is terminal asset value divided by that policy's cash-inclusive terminal wealth, and floor activation is the mean share of purchase dates with an active clipped guardrail floor. The corrected row comes from H1 left-policy ledgers and the neutral row from S1 left-policy ledgers; these mechanism ranges are descriptive and do not determine a performance ordering.}",
            r"  \label{tab:historical-policy-mechanisms}",
            r"\end{table}",
            "",
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \setlength{\tabcolsep}{3.4pt}",
            r"  \renewcommand{\arraystretch}{1.12}",
            r"  \resizebox{\textwidth}{!}{%",
            r"  \begin{tabular}{lrrrr}",
            r"    \hline",
            r"    Comparison population & Cells & Lowest 5\% gap & Largest shortfall & Mean cash / valued-unit signs \\",
            r"    \hline",
        ]
    )
    lowest_downside = min(
        _decimal(row["downside_quantile_0.05"], "5 percent downside") for row in h1
    )
    largest_shortfall = max(
        _decimal(row["worst_observed_relative_shortfall"], "worst shortfall")
        for row in h1
    )
    positive_cash = _sign_counts(h1, "mean_cash_contribution")[2]
    negative_units = _sign_counts(h1, "mean_unit_contribution")[0]
    lines.extend(
        [
            (
                f"    Corrected--DCA, primary frictionless & {len(h1)} & "
                f"{_percent(lowest_downside)} & "
                f"{_percent(largest_shortfall, signed=False)} & "
                f"{positive_cash} positive / {negative_units} negative \\\\"
            ),
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            r"  \caption{Downside and terminal-inventory attribution for the corrected guarded policy against DCA. The 5\% value is the lowest linearly interpolated cellwise quantile, and largest shortfall is the maximum observed episode loss magnitude. Mean cash contribution is $C^c-C^D$ and the valued-unit contribution is $P(Q^c-Q^D)$; their sum is the mean dollar wealth gap in every cell. The signs describe ledger-conditioned accounting, not a causal explanation.}",
            r"  \label{tab:historical-risk-attribution}",
            r"\end{table}",
            r"\FloatBarrier",
            "",
        ]
    )
    return "\n".join(lines)


def _render_robustness_asset(
    primary_groups: list[dict[str, object]],
    robustness_groups: list[dict[str, object]],
    source_sha256: str,
) -> str:
    monthly_complete_system = _robustness_cells(
        robustness_groups,
        schedule=MONTHLY_ROBUSTNESS_SCHEDULE,
        comparison="corrected_guarded_vs_dca",
    )
    monthly_signal_only = _robustness_cells(
        robustness_groups,
        schedule=MONTHLY_ROBUSTNESS_SCHEDULE,
        comparison="corrected_guarded_vs_neutral_guarded",
    )
    quarterly_complete_system = _robustness_cells(
        robustness_groups,
        schedule=QUARTERLY_ROBUSTNESS_SCHEDULE,
        comparison="corrected_guarded_vs_dca",
    )
    quarterly_signal_only = _robustness_cells(
        robustness_groups,
        schedule=QUARTERLY_ROBUSTNESS_SCHEDULE,
        comparison="corrected_guarded_vs_neutral_guarded",
    )
    lines = _header(f"{PRIMARY_RUN_ID}; {ROBUSTNESS_RUN_ID}", source_sha256)
    lines.extend(
        [
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \setlength{\tabcolsep}{3.0pt}",
            r"  \renewcommand{\arraystretch}{1.12}",
            r"  \resizebox{\textwidth}{!}{%",
            r"  \begin{tabular}{llrrrr}",
            r"    \hline",
            r"    Registered schedule & Comparison & Cells & Negative / positive & Median range & Uncertainty \\",
            r"    \hline",
        ]
    )
    rows_to_render = (
        ("Monthly extra coverage", "Corrected--DCA", monthly_complete_system),
        ("Monthly extra coverage", "Corrected--neutral", monthly_signal_only),
        ("Quarterly horizons", "Corrected--DCA", quarterly_complete_system),
        ("Quarterly horizons", "Corrected--neutral", quarterly_signal_only),
    )
    for schedule_label, comparison_label, rows in rows_to_render:
        negative, _, positive = _sign_counts(rows)
        lower, upper = _range(rows, "median_relative_terminal_wealth_gap")
        lines.append(
            f"    {schedule_label} & {comparison_label} & {len(rows)} & "
            f"{negative} / {positive} & {_percent(lower, 4)} to {_percent(upper, 4)} & "
            r"descriptive only \\"
        )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            r"  \caption{Separately registered post-confirmatory robustness results under frictionless accounting. Monthly rows use only the five additional coverage values on the sealed monthly episodes; quarterly rows use all eight non-unit primary and robustness coverage values at 6, 24, and 120 months. Counts are dataset--horizon--coverage cells, not episodes. Every comparison stays within one cadence and uses its named right-hand denominator; raw wealth is not compared across monthly and quarterly schedules because their deposit counts differ. No row has a bootstrap interval, $p$-value, or multiplicity decision, and none revises H1 or H2.}",
            r"  \label{tab:registered-robustness}",
            r"\end{table}",
            "",
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \setlength{\tabcolsep}{3.0pt}",
            r"  \renewcommand{\arraystretch}{1.12}",
            r"  \resizebox{\textwidth}{!}{%",
            r"  \begin{tabular}{llrrr}",
            r"    \hline",
            r"    Evidence slice & Cost route & Corrected--DCA cells & Median range & Largest shortfall \\",
            r"    \hline",
        ]
    )
    cost_labels = {
        "proportional-10bps": "Proportional 10 bps",
        "fixed-1-usd": "Fixed USD 1",
    }
    for cost_scenario, cost_label in cost_labels.items():
        primary_cost = [
            group
            for group in primary_groups
            if group.get("analysis_tier") == "robustness"
            and group.get("comparison") == "corrected_guarded_vs_dca"
            and group.get("cost_scenario") == cost_scenario
            and group.get("coverage") in PRIMARY_COVERAGES
        ]
        _require(
            len(primary_cost),
            18,
            f"primary {cost_scenario} corrected-versus-DCA cell count",
        )
        for slice_label, rows in (
            ("Primary monthly grid", primary_cost),
            (
                "Monthly extra coverage",
                _robustness_cells(
                    robustness_groups,
                    schedule=MONTHLY_ROBUSTNESS_SCHEDULE,
                    comparison="corrected_guarded_vs_dca",
                    cost_scenario=cost_scenario,
                ),
            ),
            (
                "Quarterly horizons",
                _robustness_cells(
                    robustness_groups,
                    schedule=QUARTERLY_ROBUSTNESS_SCHEDULE,
                    comparison="corrected_guarded_vs_dca",
                    cost_scenario=cost_scenario,
                ),
            ),
        ):
            lower, upper = _range(rows, "median_relative_terminal_wealth_gap")
            worst = max(
                _decimal(row["worst_observed_relative_shortfall"], "shortfall")
                for row in rows
            )
            lines.append(
                f"    {slice_label} & {cost_label} & {len(rows)} & "
                f"{_percent(lower, 4)} to {_percent(upper, 4)} & "
                f"{_percent(worst, 3, signed=False)} \\\\"
            )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            r"  \caption{Complete-system cost robustness for corrected guarded versus DCA. All displayed medians are negative, but these proportional- and fixed-fee calculations are finite descriptive evidence outside the current frictionless safety theorem. They carry no confirmatory cost hypothesis, no registered interval, and no multiplicity adjustment; an observed numerical floor check under fees is not a frictional guarantee.}",
            r"  \label{tab:historical-cost-robustness}",
            r"\end{table}",
            r"\FloatBarrier",
            "",
        ]
    )
    return "\n".join(lines)


def _render_confirmatory_cell_table(
    rows: list[dict[str, object]],
    uncertainty: dict[HistoricalCellKey, dict[str, object]],
    *,
    hypothesis: str,
    label: str,
    comparator: str,
) -> list[str]:
    percentage_places = 4 if hypothesis == "H2" else 3
    inference_note = (
        " Non-rejection does not establish equivalence."
        if hypothesis == "H2"
        else ""
    )
    lines = [
        r"\begin{table}[htbp]",
        r"  \centering",
        r"  \tiny",
        r"  \setlength{\tabcolsep}{2.2pt}",
        r"  \renewcommand{\arraystretch}{1.04}",
        r"  \resizebox{\textwidth}{!}{%",
        r"  \begin{tabular}{lrrrrrl}",
        r"    \hline",
        r"    Dataset & Horizon & $\lambda$ & $N$ & Median & Cellwise 95\% interval & Holm $p$ / decision \\",
        r"    \hline",
    ]
    for row in rows:
        cell = uncertainty[_cell_key(row)]
        adjusted = _decimal(
            cell["holm_adjusted_p_value"], "Holm-adjusted p-value"
        )
        decision = "reject (negative)" if adjusted < Decimal("0.05") else "not rejected"
        interval = (
            f"[{_percent(cell['interval_lower'], percentage_places)}, "
            f"{_percent(cell['interval_upper'], percentage_places)}]"
        )
        lines.append(
            f"    {_dataset_label(row['dataset_id'])} & {row['horizon_months']} & "
            f"{_coverage_label(row['coverage'])} & {row['sample_count']} & "
            f"{_percent(row['median_relative_terminal_wealth_gap'], percentage_places)} & {interval} & "
            f"{_number(adjusted, 4)} / {decision} \\\\"
        )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            f"  \\caption{{Complete {hypothesis} cell results for {comparator} in the sealed primary monthly frictionless run. $N$ counts ordered overlapping starts within one cell; intervals are cellwise two-sided percentile intervals from 10,000 circular moving-block replicates with horizon-length blocks. Holm values are adjusted once over the complete 36-cell H1/H2 family. An interval excluding zero is not substituted for the registered adjusted decision.{inference_note}}}",
            f"  \\label{{{label}}}",
            r"\end{table}",
            r"\FloatBarrier",
            "",
        ]
    )
    return lines


def _render_robustness_range_table(
    groups: list[dict[str, object]],
    *,
    schedule: str,
    title: str,
    label: str,
) -> list[str]:
    rows = [
        group
        for group in groups
        if group.get("analysis_tier") == "robustness"
        and group.get("schedule_id") == schedule
        and group.get("cost_scenario") == "frictionless"
        and group.get("coverage") != "1"
    ]
    lines = [
        r"\begin{table}[htbp]",
        r"  \centering",
        r"  \tiny",
        r"  \setlength{\tabcolsep}{2.4pt}",
        r"  \renewcommand{\arraystretch}{1.04}",
        r"  \resizebox{\textwidth}{!}{%",
        r"  \begin{tabular}{lrlrrr}",
        r"    \hline",
        r"    Dataset & Horizon & Comparison & $N$ & Coverage cells & Median range \\",
        r"    \hline",
    ]
    for dataset_id, dataset_label in DATASETS:
        horizons = sorted(
            {
                int(row["horizon_months"])
                for row in rows
                if row["dataset_id"] == dataset_id
            }
        )
        for horizon in horizons:
            for comparison, _, comparison_label in COMPARISONS:
                cell_rows = [
                    row
                    for row in rows
                    if row["dataset_id"] == dataset_id
                    and row["horizon_months"] == horizon
                    and row["comparison"] == comparison
                ]
                if not cell_rows:
                    continue
                sample_counts = {row["sample_count"] for row in cell_rows}
                _require(
                    len(sample_counts),
                    1,
                    f"{schedule}/{dataset_id}/{horizon}/{comparison} sample count",
                )
                lower, upper = _range(
                    cell_rows, "median_relative_terminal_wealth_gap"
                )
                lines.append(
                    f"    {dataset_label} & {horizon} & {comparison_label} & "
                    f"{next(iter(sample_counts))} & {len(cell_rows)} & "
                    f"{_percent(lower, 4)} to {_percent(upper, 4)} \\\\"
                )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            f"  \\caption{{{title} Each range is over the declared non-unit coverage cells within one dataset--horizon--comparison coordinate. $N$ is the number of ordered overlapping episode starts in each cell. All rows are post-confirmatory descriptive robustness with uncertainty status \\texttt{{not-run-robustness}}; they do not enter H1/H2 or permit raw-wealth comparison with another cadence.}}",
            f"  \\label{{{label}}}",
            r"\end{table}",
            r"\FloatBarrier",
            "",
        ]
    )
    return lines


def _render_supplementary_asset(
    h1: list[dict[str, object]],
    h2: list[dict[str, object]],
    architecture: list[dict[str, object]],
    uncertainty: dict[HistoricalCellKey, dict[str, object]],
    robustness_groups: list[dict[str, object]],
    primary_validation: dict[str, object],
    robustness_validation: dict[str, object],
    source_sha256: str,
) -> str:
    lines = _header(f"{PRIMARY_RUN_ID}; {ROBUSTNESS_RUN_ID}", source_sha256)
    lines.extend(
        _render_confirmatory_cell_table(
            h1,
            uncertainty,
            hypothesis="H1",
            label="tab:historical-h1-cells",
            comparator="corrected guarded versus DCA",
        )
    )
    lines.extend(
        _render_confirmatory_cell_table(
            h2,
            uncertainty,
            hypothesis="H2",
            label="tab:historical-h2-cells",
            comparator="corrected guarded versus neutral guarded",
        )
    )
    lines.extend(
        [
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \tiny",
            r"  \setlength{\tabcolsep}{2.5pt}",
            r"  \renewcommand{\arraystretch}{1.04}",
            r"  \resizebox{\textwidth}{!}{%",
            r"  \begin{tabular}{lrrrrrr}",
            r"    \hline",
            r"    Dataset & Horizon & $\lambda$ & $N$ & Median neutral--DCA gap & 5\% downside & Worst shortfall \\",
            r"    \hline",
        ]
    )
    for row in architecture:
        lines.append(
            f"    {_dataset_label(row['dataset_id'])} & {row['horizon_months']} & "
            f"{_coverage_label(row['coverage'])} & {row['sample_count']} & "
            f"{_percent(row['median_relative_terminal_wealth_gap'])} & "
            f"{_percent(row['downside_quantile_0.05'])} & "
            f"{_percent(row['worst_observed_relative_shortfall'], signed=False)} \\\\"
        )
    lines.extend(
        [
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            r"  \caption{Complete S1 architecture-only distribution summaries for neutral guarded versus DCA across the non-unit primary frictionless grid. Each relative gap uses DCA wealth as denominator. $N$ counts ordered overlapping starts within one cell. These prespecified secondary rows share the same episode populations but carry no bootstrap or Holm decision and do not causally decompose H1.}",
            r"  \label{tab:historical-architecture-cells}",
            r"\end{table}",
            r"\FloatBarrier",
            "",
        ]
    )
    lines.extend(
        _render_robustness_range_table(
            robustness_groups,
            schedule=MONTHLY_ROBUSTNESS_SCHEDULE,
            title="Monthly additional-coverage robustness on the sealed episode schedules.",
            label="tab:historical-monthly-robustness-ranges",
        )
    )
    lines.extend(
        _render_robustness_range_table(
            robustness_groups,
            schedule=QUARTERLY_ROBUSTNESS_SCHEDULE,
            title="Quarterly-horizon robustness with deposits every three months.",
            label="tab:historical-quarterly-robustness-ranges",
        )
    )

    primary_sample = primary_validation["sample_reconciliation"]
    robustness_sample = robustness_validation["sample_reconciliation"]
    robustness_slices = robustness_validation["slice_validation"]
    if not all(
        isinstance(value, dict)
        for value in (primary_sample, robustness_sample, robustness_slices)
    ):
        raise HistoricalEvaluationAssetError("validation reconciliation objects missing")
    monthly_validation = robustness_slices["monthly"]
    quarterly_validation = robustness_slices["quarterly"]
    if not isinstance(monthly_validation, dict) or not isinstance(
        quarterly_validation, dict
    ):
        raise HistoricalEvaluationAssetError("robustness slice validation missing")
    lines.extend(
        [
            r"\begin{table}[htbp]",
            r"  \centering",
            r"  \scriptsize",
            r"  \setlength{\tabcolsep}{2.8pt}",
            r"  \renewcommand{\arraystretch}{1.10}",
            r"  \resizebox{\textwidth}{!}{%",
            r"  \begin{tabular}{lrrrrrl}",
            r"    \hline",
            r"    Evidence slice & Attempted & Included & Excluded & Ledgers / comparisons & Aggregate cells & Uncertainty \\",
            r"    \hline",
            (
                f"    Sealed primary monthly & {primary_sample['attempted_episode_count']} & "
                f"{primary_sample['included_episode_count']} & {primary_sample['excluded_episode_count']} & "
                f"{primary_sample['runner_comparison_count']} / {primary_sample['runner_comparison_count']} & "
                r"216 & 36 confirmatory cells \\"
            ),
            (
                f"    Registered monthly coverage & {robustness_sample['monthly']['attempted_episode_count']} & "
                f"{robustness_sample['monthly']['included_episode_count']} & {robustness_sample['monthly']['excluded_episode_count']} & "
                f"{monthly_validation['shared_runner_validation']['ledger_count']} / "
                f"{monthly_validation['shared_runner_validation']['episode_result_count']} & "
                r"324 & descriptive only \\"
            ),
            (
                f"    Registered quarterly horizons & {robustness_sample['quarterly']['attempted_episode_count']} & "
                f"{robustness_sample['quarterly']['included_episode_count']} & {robustness_sample['quarterly']['excluded_episode_count']} & "
                f"{quarterly_validation['shared_runner_validation']['ledger_count']} / "
                f"{quarterly_validation['shared_runner_validation']['episode_result_count']} & "
                r"486 & descriptive only \\"
            ),
            r"    \hline",
            r"  \end{tabular}%",
            r"  }",
            r"  \caption{Historical evidence inventory and completeness reconciliation. Attempts and inclusions are schedule-specific episodes; ledgers and ordered comparison results have the same counts because three policies produce three comparisons. Both validations record zero exclusions, empty protocol-deviation and violation lists, and passed accounting checks. Public bundles contain derived aggregates, uncertainty where registered, validation, tables, figure-ready data, manifests, and cryptographic receipts; restricted source observations are not redistributed.}",
            r"  \label{tab:historical-evidence-inventory}",
            r"\end{table}",
            r"\clearpage",
            "",
        ]
    )
    return "\n".join(lines)


def _validate_evidence(
    primary_manifest: dict[str, object],
    robustness_manifest: dict[str, object],
    primary_aggregates: dict[str, object],
    robustness_aggregates: dict[str, object],
    uncertainty_document: dict[str, object],
    primary_validation: dict[str, object],
    robustness_validation: dict[str, object],
    primary_receipt: dict[str, object],
    robustness_receipt: dict[str, object],
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    dict[HistoricalCellKey, dict[str, object]],
]:
    _require(primary_manifest.get("study_run_id"), PRIMARY_RUN_ID, "primary run identity")
    _require(robustness_manifest.get("run_id"), ROBUSTNESS_RUN_ID, "robustness run identity")
    _require(
        (primary_manifest.get("attempted_episode_count"), primary_manifest.get("included_episode_count"), primary_manifest.get("aggregate_group_count"), primary_manifest.get("confirmatory_uncertainty_cell_count")),
        (1365, 1365, 216, 36),
        "primary manifest counts",
    )
    _require(
        (
            robustness_aggregates.get("attempted_episode_count"),
            robustness_aggregates.get("included_episode_count"),
            robustness_aggregates.get("excluded_episode_count"),
            robustness_aggregates.get("group_count"),
        ),
        (1793, 1793, 0, 810),
        "robustness aggregate counts",
    )
    _require(primary_validation.get("status"), "passed", "primary validation status")
    _require(
        robustness_validation.get("status"), "passed", "robustness validation status"
    )
    _require(primary_validation.get("deviations"), [], "primary deviations")
    _require(
        primary_validation.get("protocol_violations"), [], "primary protocol violations"
    )
    _require(robustness_validation.get("deviations"), [], "robustness deviations")
    _require(
        robustness_validation.get("protocol_violations"),
        [],
        "robustness protocol violations",
    )
    _require(
        robustness_validation.get("confirmatory_family_change"),
        "none",
        "robustness confirmatory-family boundary",
    )
    _require(
        robustness_validation.get("uncertainty_status"),
        "not-run-robustness",
        "robustness uncertainty boundary",
    )
    _require(
        robustness_validation.get("analysis_tier_counts"),
        {"robustness": 792, "secondary": 18},
        "robustness tier counts",
    )
    for label, receipt in (
        ("primary", primary_receipt),
        ("robustness", robustness_receipt),
    ):
        boundary = receipt.get("redistribution_boundary")
        if not isinstance(boundary, str) or "remain" not in boundary.casefold():
            raise HistoricalEvaluationAssetError(
                f"{label} private receipt has no redistribution boundary"
            )

    primary_groups = _objects(primary_aggregates.get("groups"), "primary groups")
    robustness_groups = _objects(
        robustness_aggregates.get("groups"), "robustness groups"
    )
    _require(len(primary_groups), 216, "primary aggregate-cell count")
    _require(len(robustness_groups), 810, "robustness aggregate-cell count")
    uncertainty_cells = _objects(
        uncertainty_document.get("cells"), "confirmatory uncertainty cells"
    )
    _require(
        (
            uncertainty_document.get("cell_count"),
            uncertainty_document.get("base_seed"),
            uncertainty_document.get("replicates"),
            uncertainty_document.get("method"),
        ),
        (36, 20260825, 10000, "circular-moving-block-bootstrap"),
        "registered uncertainty contract",
    )
    _require(len(uncertainty_cells), 36, "uncertainty cell count")
    uncertainty = _uncertainty_index(uncertainty_cells)

    h1 = _primary_cells(primary_groups, "corrected_guarded_vs_dca")
    h2 = _primary_cells(
        primary_groups, "corrected_guarded_vs_neutral_guarded"
    )
    architecture = _architecture_cells(primary_groups)
    for row in h1 + h2:
        cell = uncertainty.get(_cell_key(row))
        if cell is None:
            raise HistoricalEvaluationAssetError(
                f"missing uncertainty cell for {_cell_key(row)}"
            )
        _require(
            cell.get("observed_statistic"),
            row.get("median_relative_terminal_wealth_gap"),
            f"uncertainty statistic for {_cell_key(row)}",
        )
        _require(
            cell.get("sample_count"),
            row.get("sample_count"),
            f"uncertainty sample count for {_cell_key(row)}",
        )
        _require(cell.get("holm_family_size"), 36, "Holm family size")

    _require(_sign_counts(h1), (18, 0, 0), "H1 median signs")
    _require(_sign_counts(h2), (17, 0, 1), "H2 median signs")
    _require(_sign_counts(architecture), (18, 0, 0), "S1 median signs")
    _require(
        _range(h1, "median_relative_terminal_wealth_gap"),
        (
            Decimal("-0.0459315460329597585944088669914816089333859199860058448171075"),
            Decimal("-0.00335266351298036186677439396225895454280836618257622733904455"),
        ),
        "H1 median range",
    )
    _require(
        _range(h2, "median_relative_terminal_wealth_gap"),
        (
            Decimal("-0.00545342713737186257617090539443406886427217667683250453271505"),
            Decimal("0.00051799033724719057717082244865511868391588961045313337115452"),
        ),
        "H2 median range",
    )
    h1_uncertainty = [uncertainty[_cell_key(row)] for row in h1]
    h2_uncertainty = [uncertainty[_cell_key(row)] for row in h2]
    _require(
        sum(
            _decimal(cell["holm_adjusted_p_value"], "Holm value")
            < Decimal("0.05")
            for cell in h1_uncertainty
        ),
        9,
        "H1 Holm rejection count",
    )
    _require(
        sum(
            _decimal(cell["holm_adjusted_p_value"], "Holm value")
            < Decimal("0.05")
            for cell in h2_uncertainty
        ),
        0,
        "H2 Holm rejection count",
    )
    _require(
        sum(
            _decimal(cell["interval_upper"], "interval upper") < 0
            for cell in h1_uncertainty
        ),
        18,
        "H1 wholly negative interval count",
    )
    _require(
        sum(
            _decimal(cell["interval_upper"], "interval upper") < 0
            for cell in h2_uncertainty
        ),
        7,
        "H2 wholly negative interval count",
    )
    _require(_sign_counts(h1, "mean_cash_contribution"), (0, 0, 18), "H1 cash signs")
    _require(_sign_counts(h1, "mean_unit_contribution"), (18, 0, 0), "H1 unit signs")

    lambda_one_primary = [group for group in primary_groups if group.get("coverage") == "1"]
    lambda_one_robustness = [
        group for group in robustness_groups if group.get("coverage") == "1"
    ]
    _require(len(lambda_one_primary), 54, "primary lambda-one row count")
    _require(len(lambda_one_robustness), 108, "robustness lambda-one row count")
    _require(_sign_counts(lambda_one_primary), (0, 54, 0), "primary lambda-one ties")
    _require(
        _sign_counts(lambda_one_robustness),
        (0, 108, 0),
        "robustness lambda-one ties",
    )

    monthly_complete_system = _robustness_cells(
        robustness_groups,
        schedule=MONTHLY_ROBUSTNESS_SCHEDULE,
        comparison="corrected_guarded_vs_dca",
    )
    monthly_signal_only = _robustness_cells(
        robustness_groups,
        schedule=MONTHLY_ROBUSTNESS_SCHEDULE,
        comparison="corrected_guarded_vs_neutral_guarded",
    )
    quarterly_complete_system = _robustness_cells(
        robustness_groups,
        schedule=QUARTERLY_ROBUSTNESS_SCHEDULE,
        comparison="corrected_guarded_vs_dca",
    )
    quarterly_signal_only = _robustness_cells(
        robustness_groups,
        schedule=QUARTERLY_ROBUSTNESS_SCHEDULE,
        comparison="corrected_guarded_vs_neutral_guarded",
    )
    _require(
        _sign_counts(monthly_complete_system),
        (30, 0, 0),
        "monthly robustness corrected-versus-DCA signs",
    )
    _require(
        _sign_counts(monthly_signal_only),
        (30, 0, 0),
        "monthly robustness corrected-versus-neutral signs",
    )
    _require(
        _sign_counts(quarterly_complete_system),
        (48, 0, 0),
        "quarterly robustness corrected-versus-DCA signs",
    )
    _require(
        _sign_counts(quarterly_signal_only),
        (40, 0, 8),
        "quarterly robustness corrected-versus-neutral signs",
    )
    positive_quarterly_signal_only = [
        row
        for row in quarterly_signal_only
        if _decimal(row["median_relative_terminal_wealth_gap"], "median") > 0
    ]
    _require(
        {
            (row["dataset_id"], row["horizon_months"])
            for row in positive_quarterly_signal_only
        },
        {("btc-usd-daily", 6)},
        "positive quarterly signal-only coordinate",
    )
    for cost_scenario in ("proportional-10bps", "fixed-1-usd"):
        cost_extension = _robustness_cells(
            robustness_groups,
            schedule=MONTHLY_ROBUSTNESS_SCHEDULE,
            comparison="corrected_guarded_vs_dca",
            cost_scenario=cost_scenario,
        ) + _robustness_cells(
            robustness_groups,
            schedule=QUARTERLY_ROBUSTNESS_SCHEDULE,
            comparison="corrected_guarded_vs_dca",
            cost_scenario=cost_scenario,
        )
        _require(
            _sign_counts(cost_extension),
            (78, 0, 0),
            f"{cost_scenario} extension corrected-versus-DCA signs",
        )

    return h1, h2, architecture, uncertainty


def generate_historical_evaluation_assets(
    repository_root: Path, output_directory: Path
) -> dict[str, object]:
    """Regenerate historical presentation assets from accepted public evidence."""

    root = repository_root.resolve()
    runs = root / "reports/experiments/runs"
    primary_root = runs / PRIMARY_RUN_ID
    robustness_root = runs / ROBUSTNESS_RUN_ID
    primary_manifest_path = primary_root / "manifest.json"
    robustness_manifest_path = robustness_root / "manifest.json"
    _require(
        _sha256(primary_manifest_path),
        PRIMARY_MANIFEST_SHA256,
        "primary manifest fingerprint",
    )
    _require(
        _sha256(robustness_manifest_path),
        ROBUSTNESS_MANIFEST_SHA256,
        "robustness manifest fingerprint",
    )
    primary_manifest = _read_json(primary_manifest_path)
    robustness_manifest = _read_json(robustness_manifest_path)

    primary_aggregate_path = _verify_manifest_artifact(
        primary_root, primary_manifest, "historical-aggregates.json"
    )
    uncertainty_path = _verify_manifest_artifact(
        primary_root, primary_manifest, "uncertainty.json"
    )
    primary_validation_path = _verify_manifest_artifact(
        primary_root, primary_manifest, "study-validation.json"
    )
    primary_receipt_path = _verify_manifest_artifact(
        primary_root, primary_manifest, "private-artifact-receipt.json"
    )
    robustness_aggregate_path = _verify_manifest_artifact(
        robustness_root, robustness_manifest, "robustness-aggregates.json"
    )
    robustness_validation_path = _verify_manifest_artifact(
        robustness_root, robustness_manifest, "study-validation.json"
    )
    robustness_receipt_path = _verify_manifest_artifact(
        robustness_root, robustness_manifest, "private-artifact-receipt.json"
    )

    primary_aggregates = _read_json(primary_aggregate_path)
    robustness_aggregates = _read_json(robustness_aggregate_path)
    uncertainty_document = _read_json(uncertainty_path)
    primary_validation = _read_json(primary_validation_path)
    robustness_validation = _read_json(robustness_validation_path)
    primary_receipt = _read_json(primary_receipt_path)
    robustness_receipt = _read_json(robustness_receipt_path)
    h1, h2, architecture, uncertainty = _validate_evidence(
        primary_manifest,
        robustness_manifest,
        primary_aggregates,
        robustness_aggregates,
        uncertainty_document,
        primary_validation,
        robustness_validation,
        primary_receipt,
        robustness_receipt,
    )
    primary_groups = _objects(primary_aggregates["groups"], "primary groups")
    robustness_groups = _objects(
        robustness_aggregates["groups"], "robustness groups"
    )
    combined_digest = hashlib.sha256(
        primary_aggregate_path.read_bytes()
        + uncertainty_path.read_bytes()
        + robustness_aggregate_path.read_bytes()
        + primary_validation_path.read_bytes()
        + robustness_validation_path.read_bytes()
    ).hexdigest()
    assets = {
        "historical-primary.tex": _render_primary_asset(
            h1, h2, uncertainty, _sha256(primary_aggregate_path)
        ),
        "historical-mechanisms.tex": _render_mechanism_asset(
            h1, h2, architecture, _sha256(primary_aggregate_path)
        ),
        "historical-robustness.tex": _render_robustness_asset(
            primary_groups, robustness_groups, combined_digest
        ),
        "historical-supplementary.tex": _render_supplementary_asset(
            h1,
            h2,
            architecture,
            uncertainty,
            robustness_groups,
            primary_validation,
            robustness_validation,
            combined_digest,
        ),
    }
    output = output_directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    for asset_name in ASSET_NAMES:
        (output / asset_name).write_text(assets[asset_name], encoding="utf-8")

    return {
        "status": "passed",
        "primary_run_id": PRIMARY_RUN_ID,
        "robustness_run_id": ROBUSTNESS_RUN_ID,
        "primary_episode_count": primary_aggregates["included_episode_count"],
        "primary_confirmatory_cell_count": len(uncertainty),
        "robustness_episode_count": robustness_aggregates[
            "included_episode_count"
        ],
        "robustness_cell_count": len(robustness_groups),
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
        receipt = generate_historical_evaluation_assets(
            args.repository_root, args.output_directory
        )
    except HistoricalEvaluationAssetError as error:
        print(f"HISTORICAL MANUSCRIPT ASSET GENERATION FAILED\n{error}")
        return 1
    print(
        "HISTORICAL MANUSCRIPT ASSET GENERATION PASSED: "
        f"{len(receipt['asset_names'])} assets"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
