"""Public-contract checks for the deterministic adversarial study."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from reproducibility.deterministic_study import (
    DeterministicStudy,
    load_deterministic_study,
    run_deterministic_study,
)
from reproducibility.empirical import RunIdentityCollisionError, load_study_config


ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "experiments" / "protocols" / "safety-adaptivity-v1.json"
DETERMINISTIC_STUDY = (
    ROOT / "experiments" / "inputs" / "deterministic-adversarial-v1.json"
)
REPORT = ROOT / "reports" / "experiments" / "deterministic-adversarial-paths.md"
WORKFLOW = ROOT / ".github" / "workflows" / "reproducibility.yml"
MANUSCRIPT_WORKFLOW = ROOT / ".github" / "workflows" / "verification.yml"
COMMITTED_RUN_ID = (
    "smartdca-deterministic-v1-"
    "80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db"
)
COMMITTED_RUN = ROOT / "reports" / "experiments" / "runs" / COMMITTED_RUN_ID


def _one_constant_path_study() -> DeterministicStudy:
    return DeterministicStudy.from_mapping(
        {
            "schema_version": "smartdca-deterministic-study/1",
            "study_id": "deterministic-path-contract-test",
            "version": "1",
            "input_id": "deterministic-path-contract-test-input",
            "input_version": "1",
            "generator_version": "smartdca-deterministic-paths/1",
            "confirmatory": False,
            "seed": None,
            "deposit": "1000",
            "start_date": "2020-01-01",
            "required_families": ["constant"],
            "required_boundary_fixtures": ["constant"],
            "attempts": [
                {
                    "attempt_id": "constant-two-purchase",
                    "family": "constant",
                    "predicate": "constant",
                    "parameters": {
                        "prices": ["100", "100"],
                        "evaluation_price": "100",
                    },
                    "boundary_fixtures": ["constant"],
                    "mechanisms": ["neutral-score-on-constant-history"],
                }
            ],
        }
    )


def _all_required_family_study() -> DeterministicStudy:
    paths = [
        ("constant", ["100", "100", "100", "100"], "100", {}),
        ("monotone-rise", ["80", "90", "105", "120", "140"], "150", {}),
        ("monotone-decline", ["140", "125", "110", "90", "70"], "65", {}),
        (
            "weak-single-valley",
            ["120", "100", "100", "80", "80", "95", "110"],
            "115",
            {},
        ),
        (
            "strict-single-valley",
            ["130", "105", "80", "60", "75", "100", "125"],
            "130",
            {},
        ),
        ("incomplete-recovery", ["120", "90", "60", "75", "95"], "100", {}),
        ("completed-recovery", ["120", "90", "60", "95", "120"], "125", {}),
        (
            "multiple-valleys",
            ["100", "70", "95", "60", "90", "65", "105"],
            "100",
            {"minimum_valley_count": 2},
        ),
        (
            "crash",
            ["120", "118", "115", "55", "58", "60"],
            "62",
            {"maximum_peak_fraction": "0.5"},
        ),
        (
            "sudden-rebound",
            ["100", "95", "55", "110", "112"],
            "115",
            {"minimum_rebound_ratio": "1.5"},
        ),
        (
            "prolonged-drawdown",
            ["120", "100", "85", "80", "78", "82", "88"],
            "90",
            {"minimum_periods_below_peak": 6},
        ),
        (
            "flat-segments",
            ["100", "100", "100", "80", "80", "95"],
            "100",
            {"minimum_flat_run": 2},
        ),
        (
            "hostile-carried-cash",
            ["80", "90", "100", "115", "130"],
            "150",
            {},
        ),
        (
            "hostile-adaptive-timing",
            ["100", "60", "110", "50", "100", "40"],
            "30",
            {"minimum_direction_changes": 4},
        ),
    ]
    attempts = []
    for family, prices, evaluation_price, extra_parameters in paths:
        attempts.append(
            {
                "attempt_id": f"{family}-primary",
                "family": family,
                "predicate": family,
                "parameters": {
                    "prices": prices,
                    "evaluation_price": evaluation_price,
                    **extra_parameters,
                },
                "boundary_fixtures": (
                    ["constant"] if family == "constant" else []
                ),
                "mechanisms": [f"{family}-mechanism"],
            }
        )
    return DeterministicStudy.from_mapping(
        {
            "schema_version": "smartdca-deterministic-study/1",
            "study_id": "all-required-deterministic-families",
            "version": "1",
            "input_id": "all-required-deterministic-families-input",
            "input_version": "1",
            "generator_version": "smartdca-deterministic-paths/1",
            "confirmatory": False,
            "seed": None,
            "deposit": "1000",
            "start_date": "2020-01-01",
            "required_families": [family for family, *_ in paths],
            "required_boundary_fixtures": ["constant"],
            "attempts": attempts,
        }
    )


class DeterministicStudyContractTest(unittest.TestCase):
    def test_complete_study_run_retains_path_receipt_and_shared_runner_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = run_deterministic_study(
                load_study_config(PROTOCOL),
                _one_constant_path_study(),
                Path(directory),
            )
            artifact_names = {path.name for path in run.output_directory.iterdir()}

        self.assertTrue(run.study_run_id.startswith("smartdca-deterministic-v1-"))
        self.assertEqual(len(run.path_attempts), 1)
        self.assertEqual(run.path_attempts[0]["status"], "generated")
        self.assertEqual(run.path_attempts[0]["predicate_status"], "passed")
        self.assertEqual(
            {ledger["policy"] for ledger in run.runner.ledgers},
            {"dca", "neutral_guarded", "corrected_guarded"},
        )
        self.assertEqual(
            artifact_names,
            {
                "boundary-fixtures.json",
                "manifest.json",
                "mechanism-attribution.csv",
                "path-attempts.jsonl",
                "report-tables.txt",
                "runner",
                "runner-input.json",
                "study-validation.json",
            },
        )

    def test_all_declared_families_pass_policy_independent_path_predicates(self) -> None:
        study = _all_required_family_study()
        with tempfile.TemporaryDirectory() as directory:
            run = run_deterministic_study(
                load_study_config(PROTOCOL),
                study,
                Path(directory),
            )

        self.assertEqual(len(run.path_attempts), 14)
        self.assertEqual(
            {row["family"] for row in run.path_attempts},
            set(study.as_mapping()["required_families"]),
        )
        self.assertTrue(
            all(
                row["status"] == "generated"
                and row["predicate_status"] == "passed"
                and row["parameters"]["prices"]
                for row in run.path_attempts
            )
        )

    def test_attempted_validation_failures_are_retained_without_selection(self) -> None:
        document = _all_required_family_study().as_mapping()
        document["attempts"].extend(
            [
                {
                    "attempt_id": "rejected-predicate-mismatch",
                    "family": "validation-fixture",
                    "predicate": "monotone-rise",
                    "parameters": {
                        "prices": ["100", "90"],
                        "evaluation_price": "100",
                    },
                    "boundary_fixtures": [],
                    "mechanisms": ["predicate-validation"],
                },
                {
                    "attempt_id": "rejected-nonpositive-price",
                    "family": "validation-fixture",
                    "predicate": "constant",
                    "parameters": {
                        "prices": ["100", "0"],
                        "evaluation_price": "100",
                    },
                    "boundary_fixtures": [],
                    "mechanisms": ["price-validation"],
                },
                {
                    "attempt_id": "rejected-missing-evaluation",
                    "family": "validation-fixture",
                    "predicate": "constant",
                    "parameters": {"prices": ["100", "100"]},
                    "boundary_fixtures": [],
                    "mechanisms": ["parameter-validation"],
                },
            ]
        )
        study = DeterministicStudy.from_mapping(document)

        with tempfile.TemporaryDirectory() as directory:
            run = run_deterministic_study(
                load_study_config(PROTOCOL),
                study,
                Path(directory),
            )
            validation = json.loads(
                (run.output_directory / "study-validation.json").read_text(
                    encoding="utf-8"
                )
            )

        rejected = [row for row in run.path_attempts if row["status"] == "excluded"]
        self.assertEqual(len(run.path_attempts), 17)
        self.assertEqual(len(rejected), 3)
        self.assertEqual(
            {row["exclusion_reason"] for row in rejected},
            {"path_predicate_failed", "invalid_price", "invalid_decimal"},
        )
        self.assertEqual(validation["attempted_path_count"], 17)
        self.assertEqual(validation["generated_path_count"], 14)
        self.assertEqual(validation["excluded_path_count"], 3)
        self.assertEqual(len(run.runner.ledgers), 504)
        self.assertEqual(len(run.runner.episode_results), 504)

    def test_manifest_freezes_the_shared_three_policy_execution_grid(self) -> None:
        protocol = load_study_config(PROTOCOL)
        with tempfile.TemporaryDirectory() as directory:
            run = run_deterministic_study(
                protocol,
                _one_constant_path_study(),
                Path(directory),
            )

        self.assertEqual(
            run.manifest["execution_grid"],
            {
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
            {receipt["code"] for receipt in run.runner.validation["checks"]},
            {
                "buy_only",
                "causal_prefix",
                "cost_scope_separation",
                "direct_wealth_accounting",
                "fully_funded",
                "independent_dca_accounting",
                "lambda_one_collapse",
                "shared_guardrail_contract",
                "terminal_cash_unit_identity",
                "unit_coverage",
            },
        )

    def test_boundary_fixtures_replay_exact_cases_without_claiming_proof(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = run_deterministic_study(
                load_study_config(PROTOCOL),
                load_deterministic_study(DETERMINISTIC_STUDY),
                Path(directory),
            )
            boundary = json.loads(
                (run.output_directory / "boundary-fixtures.json").read_text(
                    encoding="utf-8"
                )
            )

        self.assertEqual(boundary["status"], "passed")
        self.assertEqual(
            {row["fixture"] for row in boundary["fixtures"]},
            {
                "constant",
                "two-purchase",
                "three-purchase",
                "single-valley",
                "repeated-floor-activation",
                "arbitrary-horizon",
            },
        )
        self.assertEqual(boundary["evidence_scope"], "finite-regression-not-proof")
        contracts = boundary["regression_contracts"]
        self.assertTrue(contracts)
        self.assertTrue(all(row["status"] == "passed" for row in contracts))
        self.assertEqual(
            {row["fixture"] for row in contracts},
            {
                "constant",
                "two-purchase",
                "three-purchase",
                "single-valley",
                "repeated-floor-activation",
                "arbitrary-horizon",
            },
        )
        self.assertTrue(
            all((ROOT / row["source_check"]).is_file() for row in contracts)
        )
        two_purchase = next(
            row
            for row in contracts
            if row["contract_id"] == "two-purchase-corrected-exact-gap"
        )
        self.assertEqual(
            two_purchase["observed"]["terminal_wealth_gap"],
            "20.83333333333333333333333333333333333333333333333333333333",
        )
        repeated_floor = next(
            ledger
            for ledger in run.runner.ledgers
            if ledger["episode_id"] == "constant-five-repeated-floor"
            and ledger["coverage"] == "0.5"
            and ledger["cost_scenario"] == "frictionless"
            and ledger["policy"] == "corrected_guarded"
        )
        self.assertEqual(
            [step["guardrail_floor"] for step in repeated_floor["steps"]],
            ["500", "250", "0", "0", "0"],
        )

    def test_outer_manifest_binds_shared_runner_source_and_seed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = run_deterministic_study(
                load_study_config(PROTOCOL),
                _one_constant_path_study(),
                Path(directory),
            )

        self.assertEqual(
            run.manifest["runner_sha256"],
            run.runner.manifest["runner_sha256"],
        )
        self.assertIsNone(run.manifest["seed"])

    def test_exact_study_bytes_and_artifacts_have_immutable_replay_identity(self) -> None:
        document = _one_constant_path_study().as_mapping()
        payload = (json.dumps(document, indent=2) + "\n").encode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            study_path = root / "study.json"
            study_path.write_bytes(payload)
            study = load_deterministic_study(study_path)
            first = run_deterministic_study(
                load_study_config(PROTOCOL), study, root / "first"
            )
            second = run_deterministic_study(
                load_study_config(PROTOCOL), study, root / "second"
            )
            first_files = {
                path.relative_to(first.output_directory).as_posix(): path.read_bytes()
                for path in first.output_directory.rglob("*")
                if path.is_file()
            }
            second_files = {
                path.relative_to(second.output_directory).as_posix(): path.read_bytes()
                for path in second.output_directory.rglob("*")
                if path.is_file()
            }
            with self.assertRaises(RunIdentityCollisionError):
                run_deterministic_study(
                    load_study_config(PROTOCOL), study, root / "first"
                )

        self.assertEqual(study.sha256, hashlib.sha256(payload).hexdigest())
        self.assertEqual(first.study_run_id, second.study_run_id)
        self.assertEqual(first_files, second_files)

    def test_module_command_exposes_success_and_typed_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid_path = root / "valid-study.json"
            valid_path.write_text(
                json.dumps(_one_constant_path_study().as_mapping()),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "reproducibility.deterministic_study",
                    "--config",
                    str(PROTOCOL),
                    "--study",
                    str(valid_path),
                    "--output-root",
                    str(root / "output"),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            invalid_document = _one_constant_path_study().as_mapping()
            invalid_document["confirmatory"] = True
            invalid_path = root / "invalid-study.json"
            invalid_path.write_text(json.dumps(invalid_document), encoding="utf-8")
            rejected = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "reproducibility.deterministic_study",
                    "--config",
                    str(PROTOCOL),
                    "--study",
                    str(invalid_path),
                    "--output-root",
                    str(root / "rejected-output"),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        completion_receipt = json.loads(completed.stdout)
        self.assertEqual(completion_receipt["status"], "completed")
        self.assertTrue(completion_receipt["study_run_id"].startswith("smartdca-"))
        self.assertEqual(rejected.returncode, 2)
        rejection_receipt = json.loads(rejected.stderr)
        self.assertEqual(rejection_receipt["status"], "rejected")
        self.assertEqual(rejection_receipt["code"], "invalid_study_scope")

    def test_committed_study_executes_every_saved_attempt_and_boundary(self) -> None:
        study = load_deterministic_study(DETERMINISTIC_STUDY)
        with tempfile.TemporaryDirectory() as directory:
            run = run_deterministic_study(
                load_study_config(PROTOCOL),
                study,
                Path(directory),
            )

        generated = [row for row in run.path_attempts if row["status"] == "generated"]
        excluded = [row for row in run.path_attempts if row["status"] == "excluded"]
        self.assertEqual(len(run.path_attempts), 21)
        self.assertEqual(len(generated), 18)
        self.assertEqual(len(excluded), 3)
        self.assertEqual(len(run.runner.ledgers), 648)
        self.assertEqual(len(run.runner.episode_results), 648)
        self.assertEqual(run.manifest["generated_path_count"], 18)
        self.assertEqual(run.manifest["excluded_path_count"], 3)
        self.assertEqual(len(run.manifest["artifacts"]), 22)
        self.assertEqual(
            set(study.as_mapping()["required_boundary_fixtures"]),
            {
                "constant",
                "two-purchase",
                "three-purchase",
                "single-valley",
                "repeated-floor-activation",
                "arbitrary-horizon",
            },
        )

    def test_adversarial_design_search_retains_every_eligible_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = run_deterministic_study(
                load_study_config(PROTOCOL),
                load_deterministic_study(DETERMINISTIC_STUDY),
                Path(directory),
            )
            search_rows = [
                json.loads(line)
                for line in (
                    run.output_directory / "adversarial-search.jsonl"
                ).read_text(encoding="utf-8").splitlines()
            ]

        search = run.manifest["adversarial_design_search"]
        self.assertEqual(search["candidate_count"], 42)
        self.assertEqual(search["attempted_grid_count"], 729)
        self.assertEqual(search["predicate_excluded_count"], 687)
        self.assertEqual(len(search_rows), 729)
        self.assertEqual(
            sum(row["status"] == "eligible" for row in search_rows),
            42,
        )
        self.assertEqual(
            search["selected_prices"],
            ["150", "100", "150", "100", "150", "60"],
        )
        self.assertLess(float(search["selected_relative_terminal_wealth_gap"]), 0)
        self.assertEqual(
            len({tuple(row["prices"]) for row in search_rows}),
            len(search_rows),
        )

    def test_committed_bundle_reproduces_byte_for_byte(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            replay = run_deterministic_study(
                load_study_config(PROTOCOL),
                load_deterministic_study(DETERMINISTIC_STUDY),
                Path(directory),
            )
            replay_files = {
                path.relative_to(replay.output_directory).as_posix(): path.read_bytes()
                for path in replay.output_directory.rglob("*")
                if path.is_file()
            }

        committed_directory = ROOT / "reports" / "experiments" / "runs" / replay.study_run_id
        self.assertTrue(committed_directory.is_dir())
        committed_files = {
            path.relative_to(committed_directory).as_posix(): path.read_bytes()
            for path in committed_directory.rglob("*")
            if path.is_file()
        }
        self.assertEqual(replay_files, committed_files)

    def test_hostile_fixtures_expose_cash_and_signal_downside_separately(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = run_deterministic_study(
                load_study_config(PROTOCOL),
                load_deterministic_study(DETERMINISTIC_STUDY),
                Path(directory),
            )

        carried_cash = next(
            row
            for row in run.runner.episode_results
            if row["episode_id"] == "hostile-carried-cash-primary"
            and row["coverage"] == "0.75"
            and row["cost_scenario"] == "frictionless"
            and row["comparison"] == "corrected_guarded_vs_dca"
        )
        adaptive_timing = next(
            row
            for row in run.runner.episode_results
            if row["episode_id"] == "hostile-adaptive-timing-primary"
            and row["coverage"] == "0.75"
            and row["cost_scenario"] == "frictionless"
            and row["comparison"] == "corrected_guarded_vs_neutral_guarded"
        )
        self.assertLess(float(carried_cash["relative_terminal_wealth_gap"]), 0)
        self.assertLess(float(adaptive_timing["relative_terminal_wealth_gap"]), 0)

    def test_report_joins_the_complete_run_and_bounds_its_claims(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn(COMMITTED_RUN_ID, report)
        self.assertIn("21 attempted path configurations", report)
        self.assertIn("18 generated paths", report)
        self.assertIn("3 retained exclusions", report)
        self.assertIn("all 729 six-purchase sequences", report)
        self.assertIn("admitted 42 sequences", report)
        self.assertIn("excluded 687", report)
        self.assertIn("Complete system", report)
        self.assertIn("Signal only", report)
        self.assertIn("Safety architecture", report)
        self.assertIn("outside the current safety theorem", report)
        self.assertIn("cannot establish historical or stochastic performance", report)
        self.assertIn("Seed: `none`", report)
        self.assertIn(
            "a508b4f064dcb3930f137e7754180ca0ec43749680278acb5b42fe2345c8d6e4",
            report,
        )
        self.assertIn(
            "../../experiments/inputs/deterministic-adversarial-v1.json",
            report,
        )
        self.assertIn(
            "../../docs/adr/0008-place-empirical-protocol-input-run-layers.md",
            report,
        )
        generated_tables = (COMMITTED_RUN / "report-tables.txt").read_text(
            encoding="utf-8"
        )
        for section in generated_tables.strip().split("\n\n### "):
            table = section[section.index("|") :].strip()
            self.assertIn(table, report)
        episode_results = [
            json.loads(line)
            for line in (COMMITTED_RUN / "runner" / "episode-results.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        hostile = next(
            row
            for row in episode_results
            if row["episode_id"] == "hostile-adaptive-timing-primary"
            and row["coverage"] == "0.75"
            and row["cost_scenario"] == "frictionless"
            and row["comparison"] == "corrected_guarded_vs_neutral_guarded"
        )
        report_flat = " ".join(report.split())
        self.assertIn(
            f"`{abs(Decimal(hostile['terminal_cash_gap'])):.3f}` less cash",
            report_flat,
        )
        self.assertIn(
            f"`{Decimal(hostile['terminal_unit_gap']):.3f}` more units",
            report_flat,
        )
        self.assertIn(
            f"`{Decimal(hostile['unit_contribution']):.3f}`",
            report_flat,
        )
        design_iteration = next(
            row
            for row in episode_results
            if row["episode_id"] == "hostile-adaptive-timing-design-iteration"
            and row["coverage"] == "0.75"
            and row["cost_scenario"] == "frictionless"
            and row["comparison"] == "corrected_guarded_vs_neutral_guarded"
        )
        self.assertIn(
            f"{Decimal(design_iteration['relative_terminal_wealth_gap']) * 100:+.3f}% "
            "signal effect",
            report_flat,
        )
        for source_id in (
            "effort-spec",
            "guarded-rule",
            "guardrail-theorem",
            "performance-boundary",
            "empirical-layers",
        ):
            self.assertGreaterEqual(report.count(f"[^{source_id}]"), 2)

        study = load_deterministic_study(DETERMINISTIC_STUDY).as_mapping()
        self.assertIn("fully retained performance-based", study["purpose"])
        self.assertNotIn("without performance-based selection", study["purpose"])

    def test_repository_reproducibility_workflow_runs_the_deterministic_checkpoint(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        for path in ("research/**", "reproducibility/**", "experiments/**", "reports/**"):
            self.assertIn(f'      - "{path}"', workflow)
        self.assertIn(
            "python -m unittest "
            "reproducibility.checks.check_deterministic_adversarial_study",
            workflow,
        )
        self.assertNotIn(
            "python -m unittest "
            "reproducibility.checks.check_deterministic_adversarial_study",
            MANUSCRIPT_WORKFLOW.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
