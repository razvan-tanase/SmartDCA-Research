"""Public-contract checks for the seeded stochastic path-family study."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from reproducibility.empirical import StudyConfig, load_study_config
from reproducibility.stochastic_study import (
    StochasticStudy,
    load_stochastic_study,
    run_stochastic_study,
)


ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "experiments" / "protocols" / "safety-adaptivity-v1.json"
STOCHASTIC_STUDY = (
    ROOT / "experiments" / "inputs" / "seeded-stochastic-families-v1.json"
)
COMMITTED_RUN_ID = (
    "smartdca-stochastic-v1-"
    "73994b28bd930d35548d60497921065f5a6320068a2f371374238587a6faf065"
)
COMMITTED_RUN = ROOT / "reports" / "experiments" / "runs" / COMMITTED_RUN_ID
REPORT = ROOT / "reports" / "experiments" / "seeded-stochastic-families.md"


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _one_trend_family_study() -> StochasticStudy:
    return StochasticStudy.from_mapping(
        {
            "schema_version": "smartdca-stochastic-study/1",
            "study_id": "stochastic-contract-fixture",
            "version": "1",
            "input_id": "stochastic-contract-input",
            "input_version": "1",
            "generator_version": "smartdca-stochastic-paths/1",
            "confirmatory": False,
            "rng": "CPython random.Random MT19937 with random() and Box-Muller normals",
            "deposit": "1000",
            "start_date": "2000-01-01",
            "horizons_months": [12, 36, 60],
            "seeds": [104729],
            "required_families": ["trend"],
            "family_configurations": [
                {
                    "config_id": "trend-baseline",
                    "family": "trend",
                    "tier": "primary",
                    "description": "Six percent annual drift with moderate volatility.",
                    "parameters": {
                        "start_price": "100",
                        "annual_drift": "0.06",
                        "annual_volatility": "0.15",
                    },
                }
            ],
        }
    )


def _all_required_family_study() -> StochasticStudy:
    configurations = [
        {
            "config_id": "trend-baseline",
            "family": "trend",
            "tier": "primary",
            "description": "Six percent annual drift with moderate volatility.",
            "parameters": {
                "start_price": "100",
                "annual_drift": "0.06",
                "annual_volatility": "0.15",
            },
        },
        {
            "config_id": "mean-reversion-baseline",
            "family": "mean_reversion",
            "tier": "primary",
            "description": "Twelve-month log-price half-life around 100.",
            "parameters": {
                "start_price": "100",
                "long_run_price": "100",
                "half_life_months": "12",
                "stationary_log_volatility": "0.15",
            },
        },
        {
            "config_id": "volatility-baseline",
            "family": "stochastic_volatility",
            "tier": "primary",
            "description": "Persistent volatility around 15 percent annualized.",
            "parameters": {
                "start_price": "100",
                "annual_drift": "0.06",
                "long_run_annual_volatility": "0.15",
                "volatility_persistence": "0.9",
                "log_volatility_of_volatility": "0.2",
            },
        },
        {
            "config_id": "regime-baseline",
            "family": "regime_switching",
            "tier": "primary",
            "description": "Persistent bull and bear monthly regimes.",
            "parameters": {
                "start_price": "100",
                "initial_regime": "bull",
                "bull_annual_drift": "0.1",
                "bull_annual_volatility": "0.12",
                "bull_stay_probability": "0.96",
                "bear_annual_drift": "-0.12",
                "bear_annual_volatility": "0.25",
                "bear_stay_probability": "0.85",
            },
        },
        {
            "config_id": "jump-baseline",
            "family": "jump_diffusion",
            "tier": "primary",
            "description": "Moderate diffusion with occasional negative jumps.",
            "parameters": {
                "start_price": "100",
                "annual_drift": "0.06",
                "annual_diffusion_volatility": "0.12",
                "monthly_jump_probability": "0.04",
                "mean_log_jump": "-0.12",
                "log_jump_volatility": "0.08",
            },
        },
    ]
    return StochasticStudy.from_mapping(
        {
            "schema_version": "smartdca-stochastic-study/1",
            "study_id": "all-stochastic-family-contract-fixture",
            "version": "1",
            "input_id": "all-stochastic-family-contract-input",
            "input_version": "1",
            "generator_version": "smartdca-stochastic-paths/1",
            "confirmatory": False,
            "rng": "CPython random.Random MT19937 with random() and Box-Muller normals",
            "deposit": "1000",
            "start_date": "2000-01-01",
            "horizons_months": [3],
            "seeds": [104729],
            "required_families": [
                "trend",
                "mean_reversion",
                "stochastic_volatility",
                "regime_switching",
                "jump_diffusion",
            ],
            "family_configurations": configurations,
        }
    )


def _config_with_horizons(horizons: list[int]) -> StudyConfig:
    document = load_study_config(PROTOCOL).as_mapping()
    document["episode_design"]["horizons_months"] = horizons
    return StudyConfig.from_mapping(document)


class StochasticStudyContractTest(unittest.TestCase):
    def test_saved_design_freezes_primary_and_exploratory_family_grid(self) -> None:
        study = load_stochastic_study(STOCHASTIC_STUDY).as_mapping()

        expected_families = {
            "trend",
            "mean_reversion",
            "stochastic_volatility",
            "regime_switching",
            "jump_diffusion",
        }
        self.assertEqual(set(study["required_families"]), expected_families)
        self.assertEqual(study["horizons_months"], [12, 36, 60])
        self.assertEqual(study["seeds"], [104729, 130363, 155921])
        by_tier = {
            tier: [
                configuration
                for configuration in study["family_configurations"]
                if configuration["tier"] == tier
            ]
            for tier in ("primary", "exploratory")
        }
        self.assertEqual(
            {configuration["family"] for configuration in by_tier["primary"]},
            expected_families,
        )
        self.assertEqual(
            {configuration["family"] for configuration in by_tier["exploratory"]},
            expected_families,
        )
        self.assertEqual(len(by_tier["primary"]), 5)
        self.assertEqual(len(by_tier["exploratory"]), 5)
        self.assertEqual(
            len(study["family_configurations"])
            * len(study["seeds"])
            * len(study["horizons_months"]),
            90,
        )

    def test_committed_bundle_fingerprints_counts_and_report_claims(self) -> None:
        manifest = json.loads((COMMITTED_RUN / "manifest.json").read_text())
        self.assertEqual(manifest["study_run_id"], COMMITTED_RUN_ID)
        self.assertEqual(manifest["attempted_path_count"], 90)
        self.assertEqual(manifest["generated_path_count"], 90)
        self.assertEqual(manifest["excluded_path_count"], 0)
        for artifact in manifest["artifacts"]:
            self.assertEqual(
                _sha256((COMMITTED_RUN / artifact["path"]).read_bytes()),
                artifact["sha256"],
                msg=artifact["path"],
            )

        runner_manifest = json.loads(
            (COMMITTED_RUN / "runner" / "manifest.json").read_text()
        )
        ledger_artifact = next(
            artifact
            for artifact in runner_manifest["artifacts"]
            if artifact["path"] == "ledgers.jsonl.gz"
        )
        compressed = (COMMITTED_RUN / "runner" / "ledgers.jsonl.gz").read_bytes()
        uncompressed = gzip.decompress(compressed)
        self.assertEqual(compressed[9], 255)
        self.assertEqual(_sha256(compressed), ledger_artifact["sha256"])
        self.assertEqual(len(uncompressed), ledger_artifact["uncompressed_bytes"])
        self.assertEqual(
            _sha256(uncompressed), ledger_artifact["uncompressed_sha256"]
        )
        self.assertEqual(len(uncompressed.splitlines()), 3240)

        validation = json.loads(
            (COMMITTED_RUN / "study-validation.json").read_text()
        )
        self.assertEqual(validation["status"], "passed")
        self.assertEqual(validation["failure_counts"], {
            "configuration": 0,
            "generator": 0,
            "input_validation": 0,
            "numerical": 0,
            "runner": 0,
        })
        self.assertEqual(
            validation["aggregate_reconciliation"]["reconciled_group_count"],
            1080,
        )
        self.assertEqual(
            validation["aggregate_reconciliation"]["mismatch_count"], 0
        )

        aggregate_document = json.loads(
            (COMMITTED_RUN / "stochastic-aggregates.json").read_text()
        )

        def selected_group(config_id: str, comparison: str) -> dict[str, object]:
            return next(
                group
                for group in aggregate_document["groups"]
                if group["generator_config_id"] == config_id
                and group["horizon_months"] == 60
                and group["coverage"] == "0.75"
                and group["cost_scenario"] == "frictionless"
                and group["comparison"] == comparison
            )

        def signed_percent(value: object) -> str:
            return f"{Decimal(str(value)) * Decimal('100'):+.3f}%"

        def shortfall_percent(value: object) -> str:
            return f"{Decimal(str(value)) * Decimal('100'):.3f}%"

        report = REPORT.read_text()
        displayed_configurations = (
            ("Trend", "trend-positive-baseline"),
            ("Mean reversion", "mean-reversion-twelve-month-baseline"),
            (
                "Stochastic volatility",
                "stochastic-volatility-fifteen-percent-baseline",
            ),
            ("Regime switching", "regime-switching-baseline"),
            ("Jump diffusion", "jump-diffusion-four-percent-baseline"),
            ("Negative trend", "trend-negative-drift-sensitivity"),
            ("Faster mean reversion", "mean-reversion-three-month-sensitivity"),
            (
                "Higher volatility",
                "stochastic-volatility-thirty-five-percent-sensitivity",
            ),
            (
                "Persistent bear regime",
                "regime-switching-persistent-bear-sensitivity",
            ),
            ("More frequent jumps", "jump-diffusion-twelve-percent-sensitivity"),
        )
        for label, config_id in displayed_configurations:
            complete = selected_group(config_id, "corrected_guarded_vs_dca")
            signal = selected_group(
                config_id, "corrected_guarded_vs_neutral_guarded"
            )
            architecture = selected_group(config_id, "neutral_guarded_vs_dca")
            expected_row = (
                f"| {label} | "
                f"{signed_percent(complete['median_relative_terminal_wealth_gap'])} | "
                f"{signed_percent(complete['downside_quantile_0.05'])} | "
                f"{shortfall_percent(complete['worst_observed_relative_shortfall'])} | "
                f"{signed_percent(signal['median_relative_terminal_wealth_gap'])} | "
                f"{signed_percent(signal['downside_quantile_0.05'])} | "
                f"{shortfall_percent(signal['worst_observed_relative_shortfall'])} | "
                f"{signed_percent(architecture['median_relative_terminal_wealth_gap'])} |"
            )
            self.assertIn(expected_row, report)
        for config_id in (
            "trend-positive-baseline",
            "mean-reversion-twelve-month-baseline",
        ):
            group = selected_group(config_id, "corrected_guarded_vs_dca")
            self.assertIn(
                f"`{Decimal(group['mean_cash_contribution']):+.3f}`", report
            )
            self.assertIn(
                f"`{Decimal(group['mean_unit_contribution']):+.3f}`", report
            )

    @unittest.skipUnless(
        sys.version_info[:2] == (3, 12),
        "the frozen runtime requires CPython 3.12",
    )
    def test_committed_run_replays_all_substantive_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as output:
            replay = run_stochastic_study(
                load_study_config(PROTOCOL),
                load_stochastic_study(STOCHASTIC_STUDY),
                Path(output),
            )
            self.assertEqual(replay.study_run_id, COMMITTED_RUN_ID)
            committed_paths = {
                path.relative_to(COMMITTED_RUN).as_posix()
                for path in COMMITTED_RUN.rglob("*")
                if path.is_file()
            }
            replay_paths = {
                path.relative_to(replay.output_directory).as_posix()
                for path in replay.output_directory.rglob("*")
                if path.is_file()
            }
            self.assertEqual(replay_paths, committed_paths)
            for relative_path in committed_paths - {"manifest.json"}:
                self.assertEqual(
                    (replay.output_directory / relative_path).read_bytes(),
                    (COMMITTED_RUN / relative_path).read_bytes(),
                    msg=relative_path,
                )
            committed_manifest = json.loads(
                (COMMITTED_RUN / "manifest.json").read_text()
            )
            replay_manifest = json.loads(
                (replay.output_directory / "manifest.json").read_text()
            )
            committed_manifest["runtime"].pop("python")
            replay_manifest["runtime"].pop("python")
            self.assertEqual(replay_manifest, committed_manifest)

    def test_saved_seed_reproduces_identical_paths_and_results(self) -> None:
        config = load_study_config(PROTOCOL)
        study = _one_trend_family_study()
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_bundle = run_stochastic_study(config, study, Path(first))
            second_bundle = run_stochastic_study(config, study, Path(second))

            first_input = (first_bundle.output_directory / "runner-input.json").read_bytes()
            second_input = (second_bundle.output_directory / "runner-input.json").read_bytes()
            self.assertEqual(first_input, second_input)
            self.assertEqual(first_bundle.study_run_id, second_bundle.study_run_id)
            self.assertEqual(first_bundle.runner.episode_results, second_bundle.runner.episode_results)

            generated = json.loads(first_input)
            self.assertEqual(generated["generator_version"], "smartdca-stochastic-paths/1")
            self.assertEqual(generated["seeds"], [104729])
            episodes = {
                episode["horizon_months"]: episode for episode in generated["episodes"]
            }
            self.assertEqual(set(episodes), {12, 36, 60})
            self.assertEqual(episodes[12]["observations"][0]["price"], "100")
            short_path = [
                row["price"] for row in episodes[12]["observations"]
            ] + [episodes[12]["evaluation_price"]]
            long_prefix = [
                row["price"] for row in episodes[60]["observations"][:12]
            ] + [episodes[60]["observations"][12]["price"]]
            self.assertEqual(short_path, long_prefix)

    def test_all_declared_families_run_the_complete_shared_policy_grid(self) -> None:
        config = _config_with_horizons([3])
        study = _all_required_family_study()
        with tempfile.TemporaryDirectory() as output:
            bundle = run_stochastic_study(config, study, Path(output))

        self.assertEqual(len(bundle.path_attempts), 5)
        self.assertEqual({row["status"] for row in bundle.path_attempts}, {"generated"})
        self.assertEqual(
            {row["family"] for row in bundle.path_attempts},
            {
                "trend",
                "mean_reversion",
                "stochastic_volatility",
                "regime_switching",
                "jump_diffusion",
            },
        )
        self.assertEqual(len(bundle.runner.ledgers), 180)
        self.assertEqual(len(bundle.runner.episode_results), 180)
        self.assertEqual(
            {row["policy"] for row in bundle.runner.ledgers},
            {"dca", "neutral_guarded", "corrected_guarded"},
        )
        self.assertEqual(
            {row["comparison"] for row in bundle.runner.episode_results},
            {
                "corrected_guarded_vs_dca",
                "corrected_guarded_vs_neutral_guarded",
                "neutral_guarded_vs_dca",
            },
        )

    def test_attempt_receipts_expose_realized_path_and_process_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as output:
            bundle = run_stochastic_study(
                _config_with_horizons([3]),
                _all_required_family_study(),
                Path(output),
            )

        by_family = {row["family"]: row for row in bundle.path_attempts}
        for receipt in by_family.values():
            self.assertEqual(receipt["status"], "generated")
            self.assertEqual(len(receipt["path_sha256"]), 64)
            self.assertEqual(
                set(receipt["path_statistics"]),
                {
                    "annualized_log_return",
                    "annualized_realized_volatility",
                    "maximum_drawdown_fraction",
                    "minimum_price",
                    "maximum_price",
                    "terminal_price",
                },
            )
        self.assertEqual(
            set(by_family["regime_switching"]["process_diagnostics"]),
            {"bull_months", "bear_months", "regime_switches"},
        )
        self.assertEqual(
            set(by_family["jump_diffusion"]["process_diagnostics"]),
            {"jump_count", "jump_months", "mean_realized_log_jump"},
        )
        self.assertEqual(
            set(by_family["stochastic_volatility"]["process_diagnostics"]),
            {
                "minimum_annual_volatility",
                "mean_annual_volatility",
                "maximum_annual_volatility",
            },
        )

    def test_frictionless_invariants_and_cost_scope_hold_path_by_path(self) -> None:
        with tempfile.TemporaryDirectory() as output:
            bundle = run_stochastic_study(
                _config_with_horizons([3]),
                _all_required_family_study(),
                Path(output),
            )

        check_status = {
            check["code"]: check["status"]
            for check in bundle.runner.validation["checks"]
        }
        self.assertEqual(
            check_status,
            {
                "fully_funded": "passed",
                "causal_prefix": "passed",
                "buy_only": "passed",
                "unit_coverage": "passed",
                "direct_wealth_accounting": "passed",
                "terminal_cash_unit_identity": "passed",
                "lambda_one_collapse": "passed",
                "shared_guardrail_contract": "passed",
                "independent_dca_accounting": "passed",
                "cost_scope_separation": "passed",
            },
        )
        self.assertTrue(
            all(
                abs(Decimal(row["identity_residual"])) <= Decimal("1e-24")
                for row in bundle.runner.episode_results
            )
        )
        for ledger in bundle.runner.ledgers:
            expected_scope = (
                "epsilon-dca"
                if ledger["cost_scenario"] == "frictionless"
                else "outside-current-safety-theorem"
            )
            self.assertEqual(ledger["theorem_scope"], expected_scope)
            if ledger["policy"] != "dca" and expected_scope == "epsilon-dca":
                minimum_coverage = min(
                    Decimal(step["coverage_after"]) for step in ledger["steps"]
                )
                self.assertGreaterEqual(
                    minimum_coverage,
                    Decimal("-1e-24"),
                    msg=f"unit coverage failed for {ledger['episode_id']} {ledger['coverage']} {ledger['policy']}",
                )

    def test_manifest_binds_runtime_inputs_grid_and_replay_contract(self) -> None:
        config = _config_with_horizons([3])
        study = _all_required_family_study()
        with tempfile.TemporaryDirectory() as output:
            bundle = run_stochastic_study(config, study, Path(output))
            actual_artifact_paths = {
                path.relative_to(bundle.output_directory).as_posix()
                for path in bundle.output_directory.rglob("*")
                if path.is_file()
                and path != bundle.output_directory / "manifest.json"
            }
            compressed_ledgers = (
                bundle.output_directory / "runner" / "ledgers.jsonl.gz"
            )
            compressed_ledger_bytes = compressed_ledgers.read_bytes()
            raw_ledgers_exists = (
                bundle.output_directory / "runner" / "ledgers.jsonl"
            ).exists()
            compressed_rows = gzip.decompress(compressed_ledger_bytes)
            packaged_runner_manifest = json.loads(
                (bundle.output_directory / "runner" / "manifest.json").read_text()
            )

        manifest = bundle.manifest
        self.assertEqual(manifest["protocol_sha256"], config.sha256)
        self.assertEqual(manifest["study_spec_sha256"], study.sha256)
        self.assertEqual(manifest["runtime"]["implementation"], "CPython")
        self.assertIn("python", manifest["runtime"])
        self.assertEqual(
            manifest["execution_grid"],
            {
                "analysis_tiers": ["primary"],
                "families": [
                    "jump_diffusion",
                    "mean_reversion",
                    "regime_switching",
                    "stochastic_volatility",
                    "trend",
                ],
                "generator_configurations": [
                    "jump-baseline",
                    "mean-reversion-baseline",
                    "regime-baseline",
                    "trend-baseline",
                    "volatility-baseline",
                ],
                "seeds": [104729],
                "horizons_months": [3],
                "policies": ["corrected_guarded", "dca", "neutral_guarded"],
                "comparisons": [
                    "corrected_guarded_vs_dca",
                    "corrected_guarded_vs_neutral_guarded",
                    "neutral_guarded_vs_dca",
                ],
                "coverage": ["1", "0.9", "0.75", "0.5"],
                "corrected_mean_configurations": ["identity-a0-b0"],
                "cost_scenarios": [
                    "frictionless",
                    "proportional-10bps",
                    "fixed-1-usd",
                ],
                "theorem_scopes": [
                    "epsilon-dca",
                    "outside-current-safety-theorem",
                ],
            },
        )
        self.assertEqual(
            manifest["reproduction"]["module"],
            "reproducibility.stochastic_study",
        )
        self.assertFalse(raw_ledgers_exists)
        self.assertEqual(compressed_ledger_bytes[9], 255)
        self.assertEqual(len(compressed_rows.splitlines()), 180)
        ledger_artifact = next(
            artifact
            for artifact in packaged_runner_manifest["artifacts"]
            if artifact["path"] == "ledgers.jsonl.gz"
        )
        self.assertEqual(ledger_artifact["content_encoding"], "gzip")
        self.assertEqual(ledger_artifact["uncompressed_bytes"], len(compressed_rows))
        self.assertEqual(len(ledger_artifact["uncompressed_sha256"]), 64)
        self.assertEqual(
            {artifact["path"] for artifact in manifest["artifacts"]},
            actual_artifact_paths,
        )

    def test_generator_failure_is_retained_with_tier_and_sample_counts(self) -> None:
        document = _all_required_family_study().as_mapping()
        document["horizons_months"] = [1]
        document["family_configurations"].append(
            {
                "config_id": "trend-underflow-probe",
                "family": "trend",
                "tier": "exploratory",
                "description": "Test-only numerical underflow probe.",
                "parameters": {
                    "start_price": "1e-999",
                    "annual_drift": "0.06",
                    "annual_volatility": "0.15",
                },
            }
        )
        study = StochasticStudy.from_mapping(document)
        with tempfile.TemporaryDirectory() as output:
            bundle = run_stochastic_study(
                _config_with_horizons([1]), study, Path(output)
            )
            validation = json.loads(
                (bundle.output_directory / "study-validation.json").read_text()
            )

        excluded = [
            row for row in bundle.path_attempts if row["status"] == "excluded"
        ]
        self.assertEqual(len(excluded), 1)
        self.assertEqual(excluded[0]["tier"], "exploratory")
        self.assertEqual(excluded[0]["failure_stage"], "generator")
        self.assertEqual(excluded[0]["exclusion_reason"], "numerical_failure")
        self.assertEqual(validation["attempted_path_count"], 6)
        self.assertEqual(validation["generated_path_count"], 5)
        self.assertEqual(validation["excluded_path_count"], 1)
        self.assertEqual(
            validation["failure_counts"],
            {
                "configuration": 0,
                "generator": 1,
                "input_validation": 0,
                "numerical": 1,
                "runner": 0,
            },
        )

    def test_aggregates_reconcile_and_keep_primary_exploratory_tiers_separate(self) -> None:
        document = _all_required_family_study().as_mapping()
        document["seeds"] = [104729, 130363]
        document["family_configurations"].append(
            {
                "config_id": "trend-negative-drift-sensitivity",
                "family": "trend",
                "tier": "exploratory",
                "description": "Negative six percent drift sensitivity.",
                "parameters": {
                    "start_price": "100",
                    "annual_drift": "-0.06",
                    "annual_volatility": "0.15",
                },
            }
        )
        study = StochasticStudy.from_mapping(document)
        with tempfile.TemporaryDirectory() as output:
            bundle = run_stochastic_study(
                _config_with_horizons([3]), study, Path(output)
            )
            aggregates = json.loads(
                (bundle.output_directory / "stochastic-aggregates.json").read_text()
            )
            reconciliation = json.loads(
                (bundle.output_directory / "aggregate-reconciliation.json").read_text()
            )

        self.assertEqual(reconciliation["status"], "passed")
        self.assertEqual(reconciliation["reconciled_group_count"], 216)
        self.assertEqual(aggregates["group_count"], 216)
        self.assertEqual(
            {group["analysis_tier"] for group in aggregates["groups"]},
            {"primary", "exploratory"},
        )
        collapsed = next(
            group
            for group in aggregates["groups"]
            if group["generator_config_id"] == "trend-baseline"
            and group["coverage"] == "1"
            and group["cost_scenario"] == "frictionless"
            and group["comparison"] == "corrected_guarded_vs_dca"
        )
        self.assertEqual(collapsed["attempted_count"], 2)
        self.assertEqual(collapsed["sample_count"], 2)
        self.assertEqual(collapsed["excluded_count"], 0)
        self.assertEqual(collapsed["mean_relative_terminal_wealth_gap"], "0")
        self.assertEqual(collapsed["downside_quantile_0.05"], "0")
        self.assertEqual(collapsed["worst_observed_relative_shortfall"], "0")
        self.assertEqual(collapsed["mean_identity_residual"], "0")

    def test_report_assets_retain_every_configuration_and_required_estimand(self) -> None:
        document = _all_required_family_study().as_mapping()
        document["family_configurations"].append(
            {
                "config_id": "trend-negative-drift-sensitivity",
                "family": "trend",
                "tier": "exploratory",
                "description": "Negative six percent drift sensitivity.",
                "parameters": {
                    "start_price": "100",
                    "annual_drift": "-0.06",
                    "annual_volatility": "0.15",
                },
            }
        )
        study = StochasticStudy.from_mapping(document)
        with tempfile.TemporaryDirectory() as output:
            bundle = run_stochastic_study(
                _config_with_horizons([3]), study, Path(output)
            )
            with (bundle.output_directory / "stochastic-figure-ready.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                figure_rows = list(csv.DictReader(handle))
            enriched_results = [
                json.loads(line)
                for line in (
                    bundle.output_directory / "stochastic-results.jsonl"
                ).read_text().splitlines()
            ]
            report_tables = (
                bundle.output_directory / "report-tables.txt"
            ).read_text()

        self.assertEqual(len(figure_rows), 216)
        self.assertEqual(
            {row["generator_config_id"] for row in figure_rows},
            {
                configuration["config_id"]
                for configuration in document["family_configurations"]
            },
        )
        self.assertTrue(
            {
                "mean_relative_terminal_wealth_gap",
                "downside_quantile_0.05",
                "worst_observed_relative_shortfall",
                "mean_left_cash_drag",
                "mean_left_asset_exposure",
                "mean_left_guardrail_activation_frequency",
                "mean_left_purchase_count",
                "mean_terminal_cash_gap",
                "mean_terminal_unit_gap",
                "mean_cash_contribution",
                "mean_unit_contribution",
            }
            <= set(figure_rows[0])
        )
        self.assertEqual(len(enriched_results), 216)
        self.assertEqual(
            {row["analysis_tier"] for row in enriched_results},
            {"primary", "exploratory"},
        )
        self.assertIn("## Complete retained grid", report_tables)
        self.assertIn("## Primary frictionless distribution slice", report_tables)
        self.assertIn("## Exploratory sensitivity distribution slice", report_tables)
        self.assertIn(
            "Controlled stochastic sensitivity is not historical evidence or a proof of stochastic optimality.",
            report_tables,
        )


if __name__ == "__main__":
    unittest.main()
