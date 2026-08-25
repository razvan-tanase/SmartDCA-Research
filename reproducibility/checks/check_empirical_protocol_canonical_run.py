#!/usr/bin/env python3
"""Contract checks for the preregistered empirical runner seam."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal, getcontext, localcontext, setcontext
from pathlib import Path

from reproducibility.empirical import (
    ExperimentValidationError,
    RunIdentityCollisionError,
    StudyConfig,
    VersionedInput,
    load_study_config,
    load_versioned_input,
    run_experiment,
)


ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "experiments/protocols/safety-adaptivity-v1.json"
CANONICAL_INPUT = ROOT / "experiments/inputs/canonical-synthetic-v1.json"


def _minimal_config() -> StudyConfig:
    return StudyConfig.from_mapping(
        {
            "schema_version": "smartdca-empirical-protocol/1",
            "protocol_id": "test-protocol",
            "protocol_version": 1,
            "locked": True,
            "registered_at": "2026-08-25T08:00:00Z",
            "confirmatory_outcomes_accessed": False,
            "registration_statement": "locked before confirmatory outcome access",
            "historical_datasets": [
                {
                    "dataset_id": "spy-adjusted-daily",
                    "provider": "Alpha Vantage",
                    "documentation_url": "https://www.alphavantage.co/documentation/#dailyadj",
                    "endpoint": "TIME_SERIES_DAILY_ADJUSTED",
                    "request_parameters": {"symbol": "SPY"},
                    "series": "SPY",
                    "asset_semantics": "investable S&P 500 proxy",
                    "price_field": "adjusted_close",
                    "currency": "USD",
                    "timezone": "America/New_York",
                    "adjustment_semantics": "split-and-dividend-adjusted",
                    "eligible_start": "1993-02-01",
                    "data_cutoff": "2025-12-31",
                    "retrieval_rule": "one frozen full-history CSV response",
                    "fingerprint_rule": "sha256 of exact response bytes",
                    "redistribution": "receipt-only pending license review",
                    "selection_status": "selected-not-retrieved",
                },
                {
                    "dataset_id": "btc-usd-daily",
                    "provider": "Alpha Vantage",
                    "documentation_url": "https://www.alphavantage.co/documentation/#currency-daily",
                    "endpoint": "DIGITAL_CURRENCY_DAILY",
                    "request_parameters": {"symbol": "BTC", "market": "USD"},
                    "series": "BTC",
                    "asset_semantics": "Bitcoin spot quoted in USD",
                    "market": "USD",
                    "price_field": "close_usd",
                    "currency": "USD",
                    "timezone": "UTC",
                    "adjustment_semantics": "unadjusted spot quote",
                    "eligible_start": "2015-01-01",
                    "data_cutoff": "2025-12-31",
                    "retrieval_rule": "one frozen full-history CSV response",
                    "fingerprint_rule": "sha256 of exact response bytes",
                    "redistribution": "receipt-only pending license review",
                    "selection_status": "selected-not-retrieved",
                },
            ],
            "retrieval_and_fingerprint": {"one_response_per_dataset": True},
            "episode_design": {
                "deposit_cadence": "monthly-first-eligible-observation",
                "deposit_amount": "1000",
                "deposit_count_rule": "exactly H deposits before the horizon date",
                "episode_start_grid_rule": "every eligible first-of-month start",
                "horizon_date_rule": "nominal start plus H calendar months",
                "horizons_months": [12, 36, 60],
                "evaluation_convention": "last observation on or before horizon date",
                "rolling_stride_months": 1,
                "missing_data_rule": "no interpolation; exclude after mapping tolerance",
            },
            "coverage": {"primary": ["1", "0.75"], "robustness": ["0.9"]},
            "corrected_mean": {
                "primary": [
                    {
                        "config_id": "identity-a0-b0",
                        "transform": "identity",
                        "alpha": "0",
                        "beta": "0",
                        "weights": "equal",
                    }
                ],
                "robustness": [
                    {
                        "config_id": "identity-a0-b-1",
                        "transform": "identity",
                        "alpha": "0",
                        "beta": "-1",
                        "weights": "equal",
                    }
                ],
            },
            "cost_scenarios": [
                {
                    "cost_id": "frictionless",
                    "fixed_fee": "0",
                    "proportional_bps": "0",
                    "theorem_scope": "epsilon-dca",
                },
                {
                    "cost_id": "fixed-test",
                    "fixed_fee": "0.10",
                    "proportional_bps": "0",
                    "theorem_scope": "outside-current-safety-theorem",
                },
                {
                    "cost_id": "proportional-test",
                    "fixed_fee": "0",
                    "proportional_bps": "100",
                    "theorem_scope": "outside-current-safety-theorem",
                },
            ],
            "hypotheses": [
                {
                    "hypothesis_id": "complete-system",
                    "comparison": "corrected_vs_dca",
                    "alternative": "two-sided",
                }
            ],
            "estimands": {
                "primary": ["relative_terminal_wealth_gap", "wealth_ratio"],
                "secondary": ["terminal_cash", "terminal_units"],
            },
            "multiplicity": {
                "family": "all primary asset-horizon-lambda comparisons",
                "method": "holm",
                "alpha": "0.05",
            },
            "uncertainty": {
                "method": "circular-moving-block-bootstrap",
                "replicates": 10000,
                "seed": 20260825,
                "rng": "test RNG",
                "cell_seed_rule": "test cell seed",
                "block_rule": "episode horizon in monthly-start units",
                "block_construction": "circular blocks truncated to N",
                "replicate_statistic": "registered cell statistic",
                "interval": "two-sided percentile interval",
                "quantile_rule": "linear interpolation at (B-1)*p",
                "p_value": "two-sided centered tail count",
                "p_value_finite_sample_rule": "(1+count)/(B+1)",
                "holm_order": "p-value then frozen cell key",
            },
            "analysis_tiers": {
                "confirmatory": ["primary historical hypotheses"],
                "secondary": ["mechanism attribution"],
                "robustness": ["predeclared alternate grids and costs"],
                "exploratory": ["post-hoc regime descriptions"],
                "immutability_rule": "confirmatory choices require a new identity after outcome access",
            },
            "exclusions": [
                "invalid input",
                "unavailable mapped purchase or evaluation date",
                "failed accounting invariant",
                "comparator_terminal_wealth_nonpositive",
            ],
            "robustness_design": {"horizons_months": [6]},
            "canonical_run": {"input_id": "synthetic-test-episode"},
            "runner_contract": {"engine_version": "smartdca-empirical-runner/1"},
        }
    )


def _single_episode_input() -> VersionedInput:
    return VersionedInput.from_mapping(
        {
            "schema_version": "smartdca-versioned-input/1",
            "input_id": "synthetic-test-episode",
            "version": "1",
            "kind": "synthetic",
            "confirmatory": False,
            "episodes": [
                {
                    "episode_id": "three-period-valley",
                    "dataset_id": "synthetic-test",
                    "horizon_months": 3,
                    "observations": [
                        {"date": "2020-01-01", "price": "1", "deposit": "1"},
                        {"date": "2020-02-01", "price": "4", "deposit": "1"},
                        {"date": "2020-03-01", "price": "2", "deposit": "1"},
                    ],
                    "evaluation_date": "2020-04-01",
                    "evaluation_price": "2.3333333333333333333333333333333333333333333333333",
                    "family": "non-confirmatory-test",
                }
            ],
        }
    )


class EmpiricalRunnerContractTest(unittest.TestCase):
    def test_runner_emits_one_complete_three_policy_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = run_experiment(
                _minimal_config(), _single_episode_input(), Path(directory)
            )

            self.assertTrue(run.run_id.startswith("smartdca-run-v1-"))
            self.assertEqual(
                {ledger["policy"] for ledger in run.ledgers},
                {"dca", "neutral_guarded", "corrected_guarded"},
            )
            self.assertEqual(
                {path.name for path in run.output_directory.iterdir()},
                {
                    "aggregates.json",
                    "episode-results.jsonl",
                    "figure-ready.csv",
                    "ledgers.jsonl",
                    "manifest.json",
                    "policy-summary.csv",
                    "validation.json",
                },
            )

    def test_frictionless_receipts_cover_the_guardrail_and_accounting_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = run_experiment(
                _minimal_config(), _single_episode_input(), Path(directory)
            )

        required_step_fields = {
            "deposit",
            "purchase",
            "fee",
            "cash",
            "units",
            "reference",
            "score",
            "guardrail_floor",
            "floor_active",
            "coverage_after",
        }
        frictionless_ledgers = [
            ledger for ledger in run.ledgers if ledger["cost_scenario"] == "frictionless"
        ]
        for ledger in frictionless_ledgers:
            self.assertTrue(required_step_fields <= set(ledger["steps"][0]))
            self.assertEqual(ledger["theorem_scope"], "epsilon-dca")

        receipt_codes = {
            receipt["code"]
            for receipt in run.validation["checks"]
            if receipt["status"] == "passed"
        }
        self.assertTrue(
            {
                "fully_funded",
                "causal_prefix",
                "buy_only",
                "unit_coverage",
                "direct_wealth_accounting",
                "terminal_cash_unit_identity",
                "lambda_one_collapse",
                "shared_guardrail_contract",
                "independent_dca_accounting",
            }
            <= receipt_codes
        )

        collapsed = [ledger for ledger in frictionless_ledgers if ledger["coverage"] == "1"]
        dca = next(ledger for ledger in collapsed if ledger["policy"] == "dca")
        expected = [
            (step["purchase"], step["fee"], step["cash"], step["units"])
            for step in dca["steps"]
        ]
        for ledger in collapsed:
            self.assertEqual(
                [
                    (step["purchase"], step["fee"], step["cash"], step["units"])
                    for step in ledger["steps"]
                ],
                expected,
            )

    def test_fixed_and_proportional_costs_are_accounted_outside_the_theorem(self) -> None:
        config = _minimal_config().as_mapping()
        config["cost_scenarios"] = [
            {
                "cost_id": "frictionless",
                "fixed_fee": "0",
                "proportional_bps": "0",
                "theorem_scope": "epsilon-dca",
            },
            {
                "cost_id": "fixed-0.10",
                "fixed_fee": "0.10",
                "proportional_bps": "0",
                "theorem_scope": "outside-current-safety-theorem",
            },
            {
                "cost_id": "proportional-100bps",
                "fixed_fee": "0",
                "proportional_bps": "100",
                "theorem_scope": "outside-current-safety-theorem",
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            run = run_experiment(
                StudyConfig.from_mapping(config),
                _single_episode_input(),
                Path(directory),
            )

        net_ledgers = [
            ledger
            for ledger in run.ledgers
            if ledger["cost_scenario"] != "frictionless"
        ]
        self.assertTrue(net_ledgers)
        self.assertTrue(
            all(
                ledger["theorem_scope"] == "outside-current-safety-theorem"
                for ledger in net_ledgers
            )
        )
        self.assertTrue(any(ledger["total_fees"] != "0" for ledger in net_ledgers))
        for ledger in net_ledgers:
            cost = next(
                value
                for value in config["cost_scenarios"]
                if value["cost_id"] == ledger["cost_scenario"]
            )
            fixed = Decimal(cost["fixed_fee"])
            rate = Decimal(cost["proportional_bps"]) / Decimal("10000")
            for step in ledger["steps"]:
                budget = Decimal(step["target_purchase_budget"])
                purchase = Decimal(step["purchase"])
                fee = Decimal(step["fee"])
                self.assertGreaterEqual(Decimal(step["cash"]), Decimal(0))
                with localcontext() as context:
                    context.prec = 60
                    self.assertLessEqual(purchase + fee, budget)
                    if purchase > 0:
                        self.assertLess(
                            abs(fee - (fixed + rate * purchase)),
                            Decimal("1e-50"),
                        )
        self.assertIn(
            "cost_scope_separation",
            {receipt["code"] for receipt in run.validation["checks"]},
        )

    def test_fixed_fee_small_cash_and_zero_purchase_boundary_are_explicit(self) -> None:
        inputs = VersionedInput.from_mapping(
            {
                "schema_version": "smartdca-versioned-input/1",
                "input_id": "fixed-fee-boundaries",
                "version": "1",
                "kind": "synthetic",
                "confirmatory": False,
                "episodes": [
                    {
                        "episode_id": "cash-below-fixed-fee",
                        "family": "cost-boundary",
                        "dataset_id": "synthetic-cost",
                        "horizon_months": 1,
                        "observations": [
                            {"date": "2020-01-01", "price": "1", "deposit": "0.05"}
                        ],
                        "evaluation_date": "2020-02-01",
                        "evaluation_price": "1",
                    },
                    {
                        "episode_id": "cash-equals-fixed-fee",
                        "family": "cost-boundary",
                        "dataset_id": "synthetic-cost",
                        "horizon_months": 1,
                        "observations": [
                            {"date": "2020-01-01", "price": "1", "deposit": "0.10"}
                        ],
                        "evaluation_date": "2020-02-01",
                        "evaluation_price": "1",
                    },
                ],
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            run = run_experiment(_minimal_config(), inputs, Path(directory))

        fixed_ledgers = [
            ledger
            for ledger in run.ledgers
            if ledger["cost_scenario"] == "fixed-test"
        ]
        self.assertTrue(fixed_ledgers)
        for ledger in fixed_ledgers:
            step = ledger["steps"][0]
            self.assertEqual(step["purchase"], "0")
            self.assertEqual(step["fee"], "0")
            self.assertEqual(step["cash"], step["deposit"])

    def test_invalid_inputs_and_identity_collisions_fail_with_reason_codes(self) -> None:
        invalid_config = _minimal_config().as_mapping()
        invalid_config["coverage"]["primary"] = ["0"]
        with self.assertRaises(ExperimentValidationError) as coverage_error:
            StudyConfig.from_mapping(invalid_config)
        self.assertEqual(coverage_error.exception.code, "invalid_coverage")

        invalid_cost = _minimal_config().as_mapping()
        invalid_cost["cost_scenarios"][0]["fixed_fee"] = "-0.01"
        with self.assertRaises(ExperimentValidationError) as cost_error:
            StudyConfig.from_mapping(invalid_cost)
        self.assertEqual(cost_error.exception.code, "invalid_cost")

        invalid_parameter = _minimal_config().as_mapping()
        invalid_parameter["corrected_mean"]["primary"][0]["alpha"] = "NaN"
        with self.assertRaises(ExperimentValidationError) as parameter_error:
            StudyConfig.from_mapping(invalid_parameter)
        self.assertEqual(parameter_error.exception.code, "invalid_decimal")

        invalid_input = _single_episode_input().as_mapping()
        invalid_input["episodes"][0]["observations"][1]["date"] = "2020-02-30"
        with self.assertRaises(ExperimentValidationError) as date_error:
            VersionedInput.from_mapping(invalid_input)
        self.assertEqual(date_error.exception.code, "invalid_date")

        invalid_price = _single_episode_input().as_mapping()
        invalid_price["episodes"][0]["observations"][0]["price"] = "0"
        with self.assertRaises(ExperimentValidationError) as price_error:
            VersionedInput.from_mapping(invalid_price)
        self.assertEqual(price_error.exception.code, "invalid_price")

        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory)
            run_experiment(_minimal_config(), _single_episode_input(), output_root)
            with self.assertRaises(RunIdentityCollisionError) as collision_error:
                run_experiment(_minimal_config(), _single_episode_input(), output_root)
        self.assertEqual(collision_error.exception.code, "run_identity_collision")

    def test_named_exact_rational_regressions_survive_the_empirical_runner(self) -> None:
        config = _minimal_config().as_mapping()
        config["coverage"]["primary"] = ["1", "0.5"]
        config["corrected_mean"]["primary"] = [
            {
                "config_id": f"identity-a0-b{beta}",
                "transform": "identity",
                "alpha": "0",
                "beta": beta,
                "weights": "equal",
            }
            for beta in ("-1", "0", "1")
        ]
        config["corrected_mean"]["robustness"] = [
            {
                "config_id": "identity-a-1-b2",
                "transform": "identity",
                "alpha": "-1",
                "beta": "2",
                "weights": "equal",
            }
        ]
        inputs = VersionedInput.from_mapping(
            {
                "schema_version": "smartdca-versioned-input/1",
                "input_id": "named-exact-rational-regressions",
                "version": "1",
                "kind": "synthetic",
                "confirmatory": False,
                "episodes": [
                    {
                        "episode_id": "two-purchase-corrected-neutral-flip",
                        "dataset_id": "synthetic-regression",
                        "horizon_months": 2,
                        "observations": [
                            {"date": "2020-01-01", "price": "1", "deposit": "1"},
                            {"date": "2020-02-01", "price": "2", "deposit": "1"},
                        ],
                        "evaluation_date": "2020-03-01",
                        "evaluation_price": "1.5",
                        "family": "exact-rational-regression",
                    },
                    {
                        "episode_id": "three-purchase-beta-flip",
                        "dataset_id": "synthetic-regression",
                        "horizon_months": 3,
                        "observations": [
                            {"date": "2020-01-01", "price": "1", "deposit": "1"},
                            {"date": "2020-02-01", "price": "4", "deposit": "1"},
                            {"date": "2020-03-01", "price": "2", "deposit": "1"},
                        ],
                        "evaluation_date": "2020-04-01",
                        "evaluation_price": "2.3333333333333333333333333333333333333333333333333",
                        "family": "exact-rational-regression",
                    },
                    {
                        "episode_id": "constant-five-purchase-repeated-floor",
                        "dataset_id": "synthetic-regression",
                        "horizon_months": 5,
                        "observations": [
                            {
                                "date": f"2020-0{month}-01",
                                "price": "1",
                                "deposit": "1",
                            }
                            for month in range(1, 6)
                        ],
                        "evaluation_date": "2020-06-01",
                        "evaluation_price": "1",
                        "family": "exact-rational-regression",
                    },
                ],
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            run = run_experiment(StudyConfig.from_mapping(config), inputs, Path(directory))

        def ledger(episode: str, mean: str, policy: str):
            return next(
                row
                for row in run.ledgers
                if row["episode_id"] == episode
                and row["coverage"] == "0.5"
                and row["corrected_mean_config"] == mean
                and row["cost_scenario"] == "frictionless"
                and row["policy"] == policy
            )

        tolerance = Decimal("1e-24")
        two = ledger(
            "two-purchase-corrected-neutral-flip",
            "identity-a0-b0",
            "corrected_guarded",
        )
        self.assertLess(
            abs(Decimal(two["steps"][1]["purchase"]) - Decimal(5) / Decimal(12)),
            tolerance,
        )
        two_result = next(
            row
            for row in run.episode_results
            if row["episode_id"] == "two-purchase-corrected-neutral-flip"
            and row["coverage"] == "0.5"
            and row["corrected_mean_config"] == "identity-a0-b0"
            and row["comparison"] == "corrected_guarded_vs_dca"
        )
        self.assertLess(
            abs(Decimal(two_result["terminal_wealth_gap"]) - Decimal(1) / Decimal(48)),
            tolerance,
        )

        low = ledger(
            "three-purchase-beta-flip", "identity-a0-b-1", "corrected_guarded"
        )
        high = ledger(
            "three-purchase-beta-flip", "identity-a0-b1", "corrected_guarded"
        )
        self.assertLess(
            abs(Decimal(low["steps"][2]["purchase"]) - Decimal(23) / Decimal(24)),
            tolerance,
        )
        self.assertLess(
            abs(Decimal(high["steps"][2]["purchase"]) - Decimal(7) / Decimal(6)),
            tolerance,
        )

        constant = ledger(
            "constant-five-purchase-repeated-floor",
            "identity-a0-b-1",
            "corrected_guarded",
        )
        self.assertEqual(
            [step["guardrail_floor"] for step in constant["steps"]],
            ["0.5", "0.25", "0", "0", "0"],
        )
        self.assertEqual(constant["terminal_wealth"], "5")

    def test_committed_preregistration_drives_the_canonical_nonconfirmatory_run(self) -> None:
        config = load_study_config(PROTOCOL)
        inputs = load_versioned_input(CANONICAL_INPUT)
        config_snapshot = config.as_mapping()
        input_snapshot = inputs.as_mapping()

        self.assertTrue(config_snapshot["locked"])
        self.assertFalse(config_snapshot["confirmatory_outcomes_accessed"])
        self.assertEqual(
            {dataset["dataset_id"] for dataset in config_snapshot["historical_datasets"]},
            {"spy-adjusted-daily", "btc-usd-daily"},
        )
        self.assertEqual(input_snapshot["kind"], "synthetic")
        self.assertFalse(input_snapshot["confirmatory"])

        with tempfile.TemporaryDirectory() as directory:
            run = run_experiment(config, inputs, Path(directory))

        self.assertEqual(len(run.ledgers), 36)
        self.assertEqual(len(run.episode_results), 36)
        self.assertEqual(run.manifest["inputs"][0]["kind"], "synthetic")
        self.assertFalse(run.manifest["config"]["confirmatory_outcomes_accessed"])
        self.assertEqual(
            {ledger["cost_scenario"] for ledger in run.ledgers},
            {"frictionless", "fixed-1-usd", "proportional-10bps"},
        )

        episode_design = config_snapshot["episode_design"]
        self.assertEqual(
            episode_design["deposit_count_rule"],
            "For horizon H, include exactly H deposits at nominal start plus k calendar months for k=0 through H-1; the horizon date receives no deposit.",
        )
        self.assertEqual(
            episode_design["episode_start_grid_rule"],
            "For each dataset and horizon H, use every first-of-month nominal start on or after eligible_start whose nominal start plus H calendar months is on or before data_cutoff.",
        )
        uncertainty = config_snapshot["uncertainty"]
        self.assertIn("block_construction", uncertainty)
        self.assertIn("cell_seed_rule", uncertainty)
        self.assertIn("p_value_finite_sample_rule", uncertainty)
        self.assertIn("quantile_rule", uncertainty)

    def test_protocol_validation_rejects_an_unfrozen_analysis_boundary(self) -> None:
        missing_series_semantics = _minimal_config().as_mapping()
        del missing_series_semantics["historical_datasets"][0]["price_field"]
        with self.assertRaises(ExperimentValidationError) as dataset_error:
            StudyConfig.from_mapping(missing_series_semantics)
        self.assertEqual(dataset_error.exception.code, "missing_field")

        no_lambda_one = _minimal_config().as_mapping()
        no_lambda_one["coverage"]["primary"] = ["0.75"]
        with self.assertRaises(ExperimentValidationError) as coverage_error:
            StudyConfig.from_mapping(no_lambda_one)
        self.assertEqual(coverage_error.exception.code, "incomplete_coverage_grid")

        missing_tier = _minimal_config().as_mapping()
        del missing_tier["analysis_tiers"]["exploratory"]
        with self.assertRaises(ExperimentValidationError) as tier_error:
            StudyConfig.from_mapping(missing_tier)
        self.assertEqual(tier_error.exception.code, "incomplete_analysis_tiers")

        no_cost_route = _minimal_config().as_mapping()
        no_cost_route["cost_scenarios"] = [
            {
                "cost_id": "frictionless",
                "fixed_fee": "0",
                "proportional_bps": "0",
                "theorem_scope": "epsilon-dca",
            }
        ]
        with self.assertRaises(ExperimentValidationError) as cost_error:
            StudyConfig.from_mapping(no_cost_route)
        self.assertEqual(cost_error.exception.code, "incomplete_cost_grid")

    def test_episode_estimands_reconcile_to_report_ready_aggregates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = run_experiment(
                _minimal_config(), _single_episode_input(), Path(directory)
            )

        required_estimands = {
            "terminal_wealth_gap",
            "relative_terminal_wealth_gap",
            "wealth_ratio",
            "terminal_cash_gap",
            "terminal_unit_gap",
            "identity_residual",
            "left_cash_drag",
            "right_cash_drag",
            "left_asset_exposure",
            "right_asset_exposure",
            "left_guardrail_activation_frequency",
            "right_guardrail_activation_frequency",
            "left_mean_guardrail_floor",
            "right_mean_guardrail_floor",
            "left_purchase_count",
            "right_purchase_count",
            "left_total_fees",
            "right_total_fees",
        }
        self.assertTrue(
            all(required_estimands <= set(row) for row in run.episode_results)
        )
        self.assertEqual(
            len(run.aggregates["groups"]),
            len(run.episode_results),
        )
        for aggregate in run.aggregates["groups"]:
            self.assertEqual(aggregate["sample_count"], 1)
            self.assertEqual(
                aggregate["mean_relative_terminal_wealth_gap"],
                aggregate["median_relative_terminal_wealth_gap"],
            )
            self.assertEqual(
                aggregate["minimum_relative_terminal_wealth_gap"],
                aggregate["maximum_relative_terminal_wealth_gap"],
            )
            self.assertIn("mean_left_guardrail_floor", aggregate)
            self.assertIn("mean_right_guardrail_floor", aggregate)

    def test_nonpositive_comparator_is_retained_with_reason_and_excluded_from_counts(self) -> None:
        inputs = VersionedInput.from_mapping(
            {
                "schema_version": "smartdca-versioned-input/1",
                "input_id": "zero-comparator",
                "version": "1",
                "kind": "synthetic",
                "confirmatory": False,
                "episodes": [
                    {
                        "episode_id": "zero-deposit-episode",
                        "family": "exclusion-boundary",
                        "dataset_id": "synthetic-exclusion",
                        "horizon_months": 1,
                        "observations": [
                            {"date": "2020-01-01", "price": "1", "deposit": "0"}
                        ],
                        "evaluation_date": "2020-02-01",
                        "evaluation_price": "1",
                    }
                ],
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            run = run_experiment(_minimal_config(), inputs, Path(directory))

        self.assertTrue(run.episode_results)
        for row in run.episode_results:
            self.assertEqual(row["result_status"], "excluded")
            self.assertEqual(
                row["exclusion_reason"],
                "comparator_terminal_wealth_nonpositive",
            )
        for aggregate in run.aggregates["groups"]:
            self.assertEqual(aggregate["attempted_count"], 1)
            self.assertEqual(aggregate["sample_count"], 0)
            self.assertEqual(aggregate["excluded_count"], 1)
            self.assertEqual(aggregate["win_count"], 0)
            self.assertEqual(aggregate["tie_count"], 0)
            self.assertEqual(aggregate["loss_count"], 0)
            self.assertIsNone(aggregate["mean_terminal_wealth_gap"])

    def test_aggregate_cells_preserve_input_family_asset_and_horizon_strata(self) -> None:
        input_mapping = _single_episode_input().as_mapping()
        first = input_mapping["episodes"][0]
        first["family"] = "family-a"
        first["dataset_id"] = "asset-a"
        first["horizon_months"] = 12
        second = json.loads(json.dumps(first))
        second["episode_id"] = "three-period-valley-b"
        second["family"] = "family-b"
        second["dataset_id"] = "asset-b"
        second["horizon_months"] = 36
        input_mapping["episodes"].append(second)

        with tempfile.TemporaryDirectory() as directory:
            run = run_experiment(
                _minimal_config(),
                VersionedInput.from_mapping(input_mapping),
                Path(directory),
            )

        self.assertEqual(len(run.aggregates["groups"]), 36)
        self.assertEqual(
            {
                (row["input_kind"], row["family"], row["dataset_id"], row["horizon_months"])
                for row in run.aggregates["groups"]
            },
            {
                ("synthetic", "family-a", "asset-a", 12),
                ("synthetic", "family-b", "asset-b", 36),
            },
        )

    def test_versioned_input_identity_is_typed_and_unambiguous(self) -> None:
        wrong_container = _single_episode_input().as_mapping()
        wrong_container["episodes"] = "bad"
        with self.assertRaises(ExperimentValidationError) as container_error:
            VersionedInput.from_mapping(wrong_container)
        self.assertEqual(container_error.exception.code, "invalid_type")

        missing_id = _single_episode_input().as_mapping()
        del missing_id["episodes"][0]["episode_id"]
        with self.assertRaises(ExperimentValidationError) as missing_error:
            VersionedInput.from_mapping(missing_id)
        self.assertEqual(missing_error.exception.code, "missing_field")

        duplicate = _single_episode_input().as_mapping()
        duplicate["episodes"].append(json.loads(json.dumps(duplicate["episodes"][0])))
        with self.assertRaises(ExperimentValidationError) as duplicate_error:
            VersionedInput.from_mapping(duplicate)
        self.assertEqual(duplicate_error.exception.code, "duplicate_episode_id")

    def test_run_identity_receipts_and_artifact_bytes_are_deterministic(self) -> None:
        config = load_study_config(PROTOCOL)
        inputs = load_versioned_input(CANONICAL_INPUT)
        self.assertEqual(config.sha256, hashlib.sha256(PROTOCOL.read_bytes()).hexdigest())
        self.assertEqual(
            inputs.sha256,
            hashlib.sha256(CANONICAL_INPUT.read_bytes()).hexdigest(),
        )

        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            left = run_experiment(config, inputs, Path(first))
            right = run_experiment(config, inputs, Path(second))
            self.assertEqual(left.run_id, right.run_id)
            self.assertEqual(
                {
                    path.name: path.read_bytes()
                    for path in left.output_directory.iterdir()
                },
                {
                    path.name: path.read_bytes()
                    for path in right.output_directory.iterdir()
                },
            )
            for receipt in left.manifest["artifacts"]:
                self.assertEqual(
                    receipt["sha256"],
                    hashlib.sha256(
                        (left.output_directory / receipt["path"]).read_bytes()
                    ).hexdigest(),
                )

    def test_module_command_exposes_success_and_validation_failures(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            command = [
                sys.executable,
                "-m",
                "reproducibility.empirical",
                "--config",
                str(PROTOCOL),
                "--input",
                str(CANONICAL_INPUT),
                "--output-root",
                directory,
            ]
            completed = subprocess.run(
                command,
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            receipt = json.loads(completed.stdout)
            self.assertEqual(receipt["status"], "completed")
            self.assertTrue(Path(receipt["output_directory"]).is_dir())

            collision = subprocess.run(
                command,
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(collision.returncode, 2)
            failure = json.loads(collision.stderr)
            self.assertEqual(failure["code"], "run_identity_collision")

    def test_committed_canonical_bundle_reproduces_byte_for_byte(self) -> None:
        config = load_study_config(PROTOCOL)
        inputs = load_versioned_input(CANONICAL_INPUT)
        with tempfile.TemporaryDirectory() as directory:
            reproduced = run_experiment(config, inputs, Path(directory))
            committed = (
                ROOT / "reports/experiments/runs" / reproduced.run_id
            )
            self.assertTrue(committed.is_dir(), f"missing canonical run {committed}")
            self.assertEqual(
                {
                    path.name: path.read_bytes()
                    for path in reproduced.output_directory.iterdir()
                },
                {
                    path.name: path.read_bytes()
                    for path in committed.iterdir()
                },
            )

    def test_caller_decimal_context_cannot_change_identity_outputs(self) -> None:
        config = load_study_config(PROTOCOL)
        inputs = load_versioned_input(CANONICAL_INPUT)
        saved_context = getcontext().copy()
        try:
            with tempfile.TemporaryDirectory() as low_root, tempfile.TemporaryDirectory() as normal_root:
                getcontext().prec = 9
                low_precision = run_experiment(config, inputs, Path(low_root))
                getcontext().prec = 50
                normal_precision = run_experiment(config, inputs, Path(normal_root))
                self.assertEqual(low_precision.run_id, normal_precision.run_id)
                self.assertEqual(
                    {
                        path.name: path.read_bytes()
                        for path in low_precision.output_directory.iterdir()
                    },
                    {
                        path.name: path.read_bytes()
                        for path in normal_precision.output_directory.iterdir()
                    },
                )
        finally:
            setcontext(saved_context)


if __name__ == "__main__":
    unittest.main()
