"""Public-contract checks for the seeded stochastic path-family study."""

from __future__ import annotations

import csv
import copy
import gzip
import hashlib
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

from reproducibility.empirical import (
    ExperimentValidationError,
    StudyConfig,
    load_study_config,
)
from reproducibility import stochastic_study as study_runner
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
    "78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25"
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


def _study_with_exploratory_family() -> StochasticStudy:
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
    return StochasticStudy.from_mapping(document)


def _study_with_generator_failure() -> StochasticStudy:
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
    return StochasticStudy.from_mapping(document)


class StochasticStudyContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture_directory = tempfile.TemporaryDirectory()
        fixture_root = Path(cls.fixture_directory.name)
        cls.all_family_bundle = run_stochastic_study(
            _config_with_horizons([3]),
            _all_required_family_study(),
            fixture_root / "all-families",
        )
        cls.exploratory_bundle = run_stochastic_study(
            _config_with_horizons([3]),
            _study_with_exploratory_family(),
            fixture_root / "exploratory",
        )
        cls.generator_failure_bundle = run_stochastic_study(
            _config_with_horizons([1]),
            _study_with_generator_failure(),
            fixture_root / "generator-failure",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture_directory.cleanup()

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

    def test_committed_manifest_identifies_the_complete_path_population(self) -> None:
        manifest = json.loads((COMMITTED_RUN / "manifest.json").read_text())

        self.assertEqual(
            (
                manifest["study_run_id"],
                manifest["attempted_path_count"],
                manifest["generated_path_count"],
                manifest["excluded_path_count"],
            ),
            (COMMITTED_RUN_ID, 90, 90, 0),
        )

    def test_committed_artifacts_match_the_outer_manifest(self) -> None:
        manifest = json.loads((COMMITTED_RUN / "manifest.json").read_text())
        mismatches = [
            artifact["path"]
            for artifact in manifest["artifacts"]
            if _sha256((COMMITTED_RUN / artifact["path"]).read_bytes())
            != artifact["sha256"]
        ]

        self.assertEqual(mismatches, [])

    def test_committed_ledger_package_reconstructs_the_manifested_rows(self) -> None:
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

        self.assertEqual(
            (
                compressed[9],
                _sha256(compressed),
                len(uncompressed),
                _sha256(uncompressed),
                len(uncompressed.splitlines()),
            ),
            (
                255,
                ledger_artifact["sha256"],
                ledger_artifact["uncompressed_bytes"],
                ledger_artifact["uncompressed_sha256"],
                3240,
            ),
        )

    def test_committed_validation_reports_no_failed_or_excluded_paths(self) -> None:
        validation = json.loads(
            (COMMITTED_RUN / "study-validation.json").read_text()
        )

        self.assertEqual(
            (
                validation["status"],
                validation["attempted_path_count"],
                validation["generated_path_count"],
                validation["excluded_path_count"],
                validation["failure_counts"],
            ),
            (
                "passed",
                90,
                90,
                0,
                {
                    "configuration": 0,
                    "generator": 0,
                    "input_validation": 0,
                    "numerical": 0,
                    "runner": 0,
                    "comparison": 0,
                },
            ),
        )

    def test_committed_reconciliation_covers_every_aggregate_field(self) -> None:
        reconciliation = json.loads(
            (COMMITTED_RUN / "aggregate-reconciliation.json").read_text()
        )

        self.assertEqual(
            (
                reconciliation["status"],
                reconciliation["reconciled_group_count"],
                reconciliation["study_group_field_count"],
                reconciliation["runner_group_field_count"],
                reconciliation["mismatch_count"],
            ),
            ("passed", 1080, 46, 39, 0),
        )

    def test_report_distribution_rows_are_derived_from_committed_aggregates(self) -> None:
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
        missing_rows = []
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
            if expected_row not in report:
                missing_rows.append(expected_row)

        self.assertEqual(missing_rows, [])

    def test_report_cash_unit_attribution_is_derived_from_committed_aggregates(self) -> None:
        aggregate_document = json.loads(
            (COMMITTED_RUN / "stochastic-aggregates.json").read_text()
        )

        def selected_group(config_id: str) -> dict[str, object]:
            return next(
                group
                for group in aggregate_document["groups"]
                if group["generator_config_id"] == config_id
                and group["horizon_months"] == 60
                and group["coverage"] == "0.75"
                and group["cost_scenario"] == "frictionless"
                and group["comparison"] == "corrected_guarded_vs_dca"
            )

        report = REPORT.read_text()
        missing_values = []
        for config_id in (
            "trend-positive-baseline",
            "mean-reversion-twelve-month-baseline",
        ):
            group = selected_group(config_id)
            for field in ("mean_cash_contribution", "mean_unit_contribution"):
                rendered = f"`{Decimal(group[field]):+.3f}`"
                if rendered not in report:
                    missing_values.append(rendered)

        self.assertEqual(missing_values, [])

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
        bundle = self.all_family_bundle

        self.assertEqual(
            (
                len(bundle.path_attempts),
                {row["status"] for row in bundle.path_attempts},
                {row["family"] for row in bundle.path_attempts},
                len(bundle.runner.ledgers),
                len(bundle.runner.episode_results),
                {row["policy"] for row in bundle.runner.ledgers},
                {row["comparison"] for row in bundle.runner.episode_results},
            ),
            (
                5,
                {"generated"},
                {
                    "trend",
                    "mean_reversion",
                    "stochastic_volatility",
                    "regime_switching",
                    "jump_diffusion",
                },
                180,
                180,
                {"dca", "neutral_guarded", "corrected_guarded"},
                {
                    "corrected_guarded_vs_dca",
                    "corrected_guarded_vs_neutral_guarded",
                    "neutral_guarded_vs_dca",
                },
            ),
        )

    def test_attempt_receipts_expose_realized_path_and_process_diagnostics(self) -> None:
        by_family = {
            row["family"]: row for row in self.all_family_bundle.path_attempts
        }
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

    def test_shared_runner_reports_every_accounting_invariant_passed(self) -> None:
        bundle = self.all_family_bundle
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

    def test_terminal_cash_unit_identity_holds_for_every_comparison(self) -> None:
        violations = [
            row["episode_id"]
            for row in self.all_family_bundle.runner.episode_results
            if abs(Decimal(row["identity_residual"])) > Decimal("1e-24")
        ]

        self.assertEqual(violations, [])

    def test_each_ledger_uses_only_its_cost_scenario_theorem_scope(self) -> None:
        violations = []
        for ledger in self.all_family_bundle.runner.ledgers:
            expected_scope = (
                "epsilon-dca"
                if ledger["cost_scenario"] == "frictionless"
                else "outside-current-safety-theorem"
            )
            if ledger["theorem_scope"] != expected_scope:
                violations.append(
                    (
                        ledger["episode_id"],
                        ledger["cost_scenario"],
                        ledger["policy"],
                    )
                )

        self.assertEqual(violations, [])

    def test_frictionless_guarded_ledgers_satisfy_unit_coverage_path_by_path(self) -> None:
        violations = []
        for ledger in self.all_family_bundle.runner.ledgers:
            if (
                ledger["policy"] == "dca"
                or ledger["cost_scenario"] != "frictionless"
            ):
                continue
            minimum_coverage = min(
                Decimal(step["coverage_after"]) for step in ledger["steps"]
            )
            if minimum_coverage < Decimal("-1e-24"):
                violations.append(
                    (ledger["episode_id"], ledger["coverage"], ledger["policy"])
                )

        self.assertEqual(violations, [])

    def test_manifest_binds_input_and_runtime_identities(self) -> None:
        config = _config_with_horizons([3])
        study = _all_required_family_study()
        bundle = self.all_family_bundle
        manifest = bundle.manifest

        self.assertEqual(
            (
                manifest["protocol_sha256"],
                manifest["study_spec_sha256"],
                manifest["runtime"]["implementation"],
                bool(manifest["runtime"]["python"]),
                manifest["reproduction"]["module"],
            ),
            (
                config.sha256,
                study.sha256,
                "CPython",
                True,
                "reproducibility.stochastic_study",
            ),
        )

    def test_manifest_binds_the_complete_execution_grid(self) -> None:
        manifest = self.all_family_bundle.manifest

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
    def test_runner_ledgers_use_the_deterministic_gzip_contract(self) -> None:
        bundle = self.all_family_bundle
        compressed_path = bundle.output_directory / "runner" / "ledgers.jsonl.gz"
        compressed_bytes = compressed_path.read_bytes()
        uncompressed_bytes = gzip.decompress(compressed_bytes)
        raw_ledgers_exists = (
            bundle.output_directory / "runner" / "ledgers.jsonl"
        ).exists()
        packaged_runner_manifest = json.loads(
            (bundle.output_directory / "runner" / "manifest.json").read_text()
        )
        ledger_artifact = next(
            artifact
            for artifact in packaged_runner_manifest["artifacts"]
            if artifact["path"] == "ledgers.jsonl.gz"
        )

        self.assertEqual(
            (
                raw_ledgers_exists,
                compressed_bytes[9],
                len(uncompressed_bytes.splitlines()),
                ledger_artifact["content_encoding"],
                ledger_artifact["uncompressed_bytes"],
                len(ledger_artifact["uncompressed_sha256"]),
            ),
            (
                False,
                255,
                180,
                "gzip",
                len(uncompressed_bytes),
                64,
            ),
        )

    def test_outer_manifest_inventories_every_generated_artifact(self) -> None:
        bundle = self.all_family_bundle
        actual_artifact_paths = {
            path.relative_to(bundle.output_directory).as_posix()
            for path in bundle.output_directory.rglob("*")
            if path.is_file()
            and path != bundle.output_directory / "manifest.json"
        }

        self.assertEqual(
            {artifact["path"] for artifact in bundle.manifest["artifacts"]},
            actual_artifact_paths,
        )

    def test_generator_failure_retains_its_tier_stage_and_reason(self) -> None:
        bundle = self.generator_failure_bundle
        excluded = [
            row for row in bundle.path_attempts if row["status"] == "excluded"
        ]

        self.assertEqual(
            [
                (
                    row["tier"],
                    row["failure_stage"],
                    row["exclusion_reason"],
                )
                for row in excluded
            ],
            [("exploratory", "generator", "numerical_failure")],
        )

    def test_generator_failure_is_included_in_validation_sample_counts(self) -> None:
        bundle = self.generator_failure_bundle
        validation = json.loads(
            (bundle.output_directory / "study-validation.json").read_text()
        )

        self.assertEqual(
            (
                validation["attempted_path_count"],
                validation["generated_path_count"],
                validation["excluded_path_count"],
                validation["failure_counts"],
            ),
            (
                6,
                5,
                1,
                {
                    "configuration": 0,
                    "generator": 1,
                    "input_validation": 0,
                    "numerical": 1,
                    "runner": 0,
                    "comparison": 0,
                },
            ),
        )

    def test_small_grid_reconciliation_covers_all_aggregate_fields(self) -> None:
        reconciliation = json.loads(
            (
                self.exploratory_bundle.output_directory
                / "aggregate-reconciliation.json"
            ).read_text()
        )

        self.assertEqual(
            (
                reconciliation["status"],
                reconciliation["reconciled_group_count"],
                reconciliation["study_group_field_count"],
                reconciliation["runner_group_field_count"],
                reconciliation["mismatch_count"],
            ),
            ("passed", 216, 46, 39, 0),
        )

    def test_aggregate_grid_keeps_primary_and_exploratory_tiers_separate(self) -> None:
        aggregates = json.loads(
            (
                self.exploratory_bundle.output_directory
                / "stochastic-aggregates.json"
            ).read_text()
        )

        self.assertEqual(
            (
                aggregates["group_count"],
                {group["analysis_tier"] for group in aggregates["groups"]},
            ),
            (216, {"primary", "exploratory"}),
        )

    def test_lambda_one_aggregate_retains_counts_and_zero_effects(self) -> None:
        aggregates = json.loads(
            (
                self.exploratory_bundle.output_directory
                / "stochastic-aggregates.json"
            ).read_text()
        )
        collapsed = next(
            group
            for group in aggregates["groups"]
            if group["generator_config_id"] == "trend-baseline"
            and group["coverage"] == "1"
            and group["cost_scenario"] == "frictionless"
            and group["comparison"] == "corrected_guarded_vs_dca"
        )

        self.assertEqual(
            (
                collapsed["attempted_count"],
                collapsed["sample_count"],
                collapsed["excluded_count"],
                collapsed["mean_relative_terminal_wealth_gap"],
                collapsed["downside_quantile_0.05"],
                collapsed["worst_observed_relative_shortfall"],
                collapsed["mean_identity_residual"],
            ),
            (2, 2, 0, "0", "0", "0", "0"),
        )

    def test_figure_ready_data_retains_every_generator_configuration(self) -> None:
        document = _study_with_exploratory_family().as_mapping()
        with (
            self.exploratory_bundle.output_directory
            / "stochastic-figure-ready.csv"
        ).open(encoding="utf-8", newline="") as handle:
            figure_rows = list(csv.DictReader(handle))

        self.assertEqual(
            (
                len(figure_rows),
                {row["generator_config_id"] for row in figure_rows},
            ),
            (
                216,
                {
                    configuration["config_id"]
                    for configuration in document["family_configurations"]
                },
            ),
        )

    def test_figure_ready_data_exposes_every_required_estimand(self) -> None:
        with (
            self.exploratory_bundle.output_directory
            / "stochastic-figure-ready.csv"
        ).open(encoding="utf-8", newline="") as handle:
            first_row = next(csv.DictReader(handle))

        self.assertEqual(
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
            - set(first_row),
            set(),
        )

    def test_enriched_results_retain_every_episode_and_analysis_tier(self) -> None:
        enriched_results = [
            json.loads(line)
            for line in (
                self.exploratory_bundle.output_directory
                / "stochastic-results.jsonl"
            )
            .read_text()
            .splitlines()
        ]

        self.assertEqual(
            (
                len(enriched_results),
                {row["analysis_tier"] for row in enriched_results},
            ),
            (432, {"primary", "exploratory"}),
        )

    def test_generated_tables_separate_tiers_and_bound_their_interpretation(self) -> None:
        report_tables = (
            self.exploratory_bundle.output_directory / "report-tables.txt"
        ).read_text()
        required_text = {
            "## Complete retained grid",
            "## Primary frictionless distribution slice",
            "## Exploratory sensitivity distribution slice",
            "Controlled stochastic sensitivity is not historical evidence or a proof of stochastic optimality.",
        }

        self.assertEqual(
            {text for text in required_text if text not in report_tables}, set()
        )


class StochasticFailureReceiptTest(unittest.TestCase):
    def test_invalid_saved_study_is_retained_with_zero_executed_samples(self) -> None:
        invalid_document = json.loads(STOCHASTIC_STUDY.read_text())
        invalid_document["family_configurations"][0]["parameters"][
            "annual_drift"
        ] = "0.5"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            invalid_study = root / "invalid-study.json"
            invalid_study.write_text(json.dumps(invalid_document))

            with self.assertRaises(ExperimentValidationError) as caught:
                study_runner.run_stochastic_study_from_paths(
                    PROTOCOL,
                    invalid_study,
                    root / "outputs",
                )

            receipt = json.loads(
                Path(caught.exception.failure_receipt).read_text()
            )

        self.assertEqual(
            {
                "status": receipt["status"],
                "stage": receipt["stage"],
                "code": receipt["error"]["code"],
                "declared": receipt["sample_counts"]["declared_path_count"],
                "attempted": receipt["sample_counts"]["attempted_path_count"],
                "included": receipt["sample_counts"]["included_path_count"],
                "configuration_failures": receipt["failure_counts"][
                    "configuration"
                ],
            },
            {
                "status": "failed",
                "stage": "configuration",
                "code": "invalid_parameter",
                "declared": 90,
                "attempted": 0,
                "included": 0,
                "configuration_failures": 1,
            },
        )

    def test_runner_boundary_failure_preserves_attempts_and_exclusion_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output_root = Path(temporary)
            with mock.patch.object(
                study_runner,
                "run_experiment",
                side_effect=RuntimeError("forced runner-boundary failure"),
            ):
                with self.assertRaises(RuntimeError) as caught:
                    run_stochastic_study(
                        load_study_config(PROTOCOL),
                        _one_trend_family_study(),
                        output_root,
                    )

            receipt_path = Path(caught.exception.failure_receipt)
            receipt = json.loads(receipt_path.read_text())
            retained_paths = {
                path.relative_to(receipt_path.parent).as_posix()
                for path in receipt_path.parent.rglob("*")
                if path.is_file()
            }

        self.assertEqual(
            {
                "stage": receipt["stage"],
                "runner_failures": receipt["failure_counts"]["runner"],
                "attempted": receipt["sample_counts"]["attempted_path_count"],
                "generated": receipt["sample_counts"]["generated_path_count"],
                "included": receipt["sample_counts"]["included_path_count"],
                "excluded": receipt["sample_counts"]["excluded_path_count"],
                "paths": retained_paths,
            },
            {
                "stage": "runner",
                "runner_failures": 1,
                "attempted": 3,
                "generated": 3,
                "included": 0,
                "excluded": 3,
                "paths": {"failure.json", "path-attempts.jsonl", "runner-input.json"},
            },
        )


class StochasticAggregateReconciliationSensitivityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stochastic = json.loads(
            (COMMITTED_RUN / "stochastic-aggregates.json").read_text()
        )
        cls.runner = json.loads(
            (COMMITTED_RUN / "runner" / "aggregates.json").read_text()
        )
        cls.results = tuple(
            json.loads(line)
            for line in (COMMITTED_RUN / "runner" / "episode-results.jsonl")
            .read_text()
            .splitlines()
        )
        cls.attempts = tuple(
            json.loads(line)
            for line in (COMMITTED_RUN / "path-attempts.jsonl")
            .read_text()
            .splitlines()
        )

    def assert_reconciliation_rejects(self, document: dict[str, object]) -> None:
        with self.assertRaises(AssertionError):
            study_runner.reconcile_stochastic_aggregates(
                document,
                self.runner,
                self.results,
                self.attempts,
            )

    def test_reconciliation_accepts_every_uncorrupted_aggregate_field(self) -> None:
        receipt = study_runner.reconcile_stochastic_aggregates(
            self.stochastic,
            self.runner,
            self.results,
            self.attempts,
        )

        self.assertEqual(
            {
                "status": receipt["status"],
                "groups": receipt["reconciled_group_count"],
                "study_fields": receipt["study_group_field_count"],
                "runner_fields": receipt["runner_group_field_count"],
                "mismatches": receipt["mismatch_count"],
            },
            {
                "status": "passed",
                "groups": 1080,
                "study_fields": 46,
                "runner_fields": 39,
                "mismatches": 0,
            },
        )

    def test_reconciliation_rejects_corrupt_top_level_attempt_count(self) -> None:
        corrupted = copy.deepcopy(self.stochastic)
        corrupted["attempted_path_count"] += 1

        self.assert_reconciliation_rejects(corrupted)

    def test_reconciliation_rejects_corrupt_group_generated_count(self) -> None:
        corrupted = copy.deepcopy(self.stochastic)
        corrupted["groups"][0]["generated_count"] -= 1

        self.assert_reconciliation_rejects(corrupted)

    def test_reconciliation_rejects_corrupt_exclusion_reasons(self) -> None:
        corrupted = copy.deepcopy(self.stochastic)
        corrupted["groups"][0]["exclusions_by_reason"] = {"runner_failure": 1}

        self.assert_reconciliation_rejects(corrupted)

    def test_reconciliation_rejects_corrupt_effect_size_distribution(self) -> None:
        corrupted = copy.deepcopy(self.stochastic)
        corrupted["groups"][0]["relative_terminal_wealth_gap_distribution"][0][
            "value"
        ] = "1"

        self.assert_reconciliation_rejects(corrupted)

    def test_reconciliation_rejects_corrupt_worst_shortfall(self) -> None:
        corrupted = copy.deepcopy(self.stochastic)
        corrupted["groups"][0]["worst_observed_relative_shortfall"] = "1"

        self.assert_reconciliation_rejects(corrupted)

    def test_reconciliation_rejects_corrupt_cash_contribution(self) -> None:
        corrupted = copy.deepcopy(self.stochastic)
        corrupted["groups"][0]["mean_cash_contribution"] = "1"

        self.assert_reconciliation_rejects(corrupted)

    def test_reconciliation_rejects_corrupt_identity_residual(self) -> None:
        corrupted = copy.deepcopy(self.stochastic)
        corrupted["groups"][0]["mean_identity_residual"] = "1"

        self.assert_reconciliation_rejects(corrupted)


if __name__ == "__main__":
    unittest.main()
