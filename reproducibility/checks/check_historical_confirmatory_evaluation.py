"""Public-contract checks for the confirmatory historical evaluation."""

from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from decimal import Decimal
from pathlib import Path

from reproducibility.empirical import ExperimentValidationError
from reproducibility.historical_study import (
    confirmatory_cell_seed,
    circular_moving_block_bootstrap,
    main as historical_study_main,
    run_historical_study_from_paths,
)


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/protocols/safety-adaptivity-yahoo-v2.json"
RUN_ID = (
    "smartdca-historical-study-v1-"
    "5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221"
)
COMMITTED_RUN = ROOT / "reports/experiments/runs" / RUN_ID
REPORT = ROOT / "reports/experiments/confirmatory-historical-evaluation.md"
AUDIT = ROOT / "research/notes/confirmatory-historical-evaluation-audit.md"


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _write_preparation_fixture(root: Path) -> tuple[Path, Path]:
    preparation = root / "preparation"
    preparation.mkdir()
    prices = ("100", "95", "90", "85", "92", "105", "110", "102", "97", "108", "115", "120")
    observations = [
        {
            "date": f"2020-{month:02d}-01",
            "price": price,
            "deposit": "1000",
        }
        for month, price in enumerate(prices, start=1)
    ]
    runner_document = {
        "schema_version": "smartdca-versioned-input/1",
        "input_id": "accepted-historical-fixture",
        "version": "1",
        "kind": "historical",
        "confirmatory": True,
        "episodes": [
            {
                "episode_id": "fixture-2020-01-01-12m",
                "family": "historical-recurring-investment",
                "dataset_id": "fixture-daily",
                "horizon_months": 12,
                "observations": observations,
                "evaluation_date": "2021-01-01",
                "evaluation_price": "125",
                "historical_mapping": {
                    "nominal_start": "2020-01-01",
                    "horizon_date": "2021-01-01",
                    "dataset_source_identity": "fixture-source",
                },
            }
        ],
    }
    runner_payload = (_canonical_json(runner_document) + "\n").encode("utf-8")
    (preparation / "runner-input.json").write_bytes(runner_payload)
    attempt = {
        "episode_id": "fixture-2020-01-01-12m",
        "dataset_id": "fixture-daily",
        "nominal_start": "2020-01-01",
        "horizon_months": 12,
        "status": "included",
        "exclusion_reason": None,
    }
    (preparation / "episode-attempts.jsonl").write_text(
        _canonical_json(attempt) + "\n", encoding="utf-8", newline="\n"
    )
    documents = {
        "normalized-datasets.json": {"source_set_id": "fixture", "datasets": {}},
        "reconciliation.json": {
            "dataset_count": 1,
            "accepted_dataset_count": 1,
            "failed_dataset_count": 0,
            "dataset_failures": {},
            "observation_count": 12,
            "attempted_episode_count": 1,
            "included_episode_count": 1,
            "excluded_episode_count": 0,
            "exclusion_reasons": {},
            "runner_input_episode_count": 1,
            "validation_episode_count": 0,
            "input_status": "accepted",
        },
        "source-receipts.json": {"source_set_id": "fixture", "receipts": []},
    }
    canonical_input_sha = _sha256(_canonical_json(runner_document).encode("utf-8"))
    documents["validation.json"] = {
        "status": "passed",
        "evidence_tier": "confirmatory-input-preparation",
        "policy_execution": "not-run",
        "confirmatory_aggregate_outcomes": "not-computed",
        "runner_input_sha256": canonical_input_sha,
        "reconciliation": documents["reconciliation.json"],
    }
    for name, document in documents.items():
        (preparation / name).write_text(
            _canonical_json(document) + "\n", encoding="utf-8", newline="\n"
        )
    artifact_names = sorted(["runner-input.json", "episode-attempts.jsonl", *documents])
    manifest = {
        "schema_version": "smartdca-historical-input-manifest/1",
        "run_id": "fixture-preparation",
        "engine_version": "smartdca-historical-preparation/1",
        "config_sha256": _sha256(CONFIG.read_bytes()),
        "source_set_sha256": "1" * 64,
        "runner_input_sha256": canonical_input_sha,
        "prepared_evidence_sha256": "2" * 64,
        "policy_execution": "not-run",
        "artifacts": [
            {
                "path": name,
                "sha256": _sha256((preparation / name).read_bytes()),
            }
            for name in artifact_names
        ],
    }
    manifest_payload = (_canonical_json(manifest) + "\n").encode("utf-8")
    (preparation / "manifest.json").write_bytes(manifest_payload)
    accepted_manifest = root / "accepted-manifest.json"
    accepted_manifest.write_bytes(manifest_payload)
    return preparation, accepted_manifest


def _reseal_preparation(preparation: Path, accepted_manifest: Path) -> None:
    manifest = json.loads((preparation / "manifest.json").read_text(encoding="utf-8"))
    for artifact in manifest["artifacts"]:
        artifact["sha256"] = _sha256((preparation / artifact["path"]).read_bytes())
    payload = (_canonical_json(manifest) + "\n").encode("utf-8")
    (preparation / "manifest.json").write_bytes(payload)
    accepted_manifest.write_bytes(payload)


class ConfirmatoryHistoricalEvaluationTest(unittest.TestCase):
    def test_committed_manifest_binds_code_inputs_and_public_artifacts(self) -> None:
        manifest = json.loads(
            (COMMITTED_RUN / "manifest.json").read_text(encoding="utf-8")
        )

        self.assertEqual(manifest["study_run_id"], RUN_ID)
        self.assertEqual(manifest["config_sha256"], _sha256(CONFIG.read_bytes()))
        self.assertEqual(
            manifest["accepted_preparation_manifest_sha256"],
            _sha256(
                (
                    ROOT
                    / "experiments/inputs/historical-yahoo-preparation-manifest-v5.json"
                ).read_bytes()
            ),
        )
        self.assertEqual(
            manifest["study_sha256"],
            _sha256((ROOT / "reproducibility/historical_study.py").read_bytes()),
        )
        self.assertEqual(
            manifest["runner_sha256"],
            _sha256((ROOT / "reproducibility/empirical.py").read_bytes()),
        )
        public_artifacts = [
            artifact
            for artifact in manifest["artifacts"]
            if artifact["retention"] == "public-derived"
        ]
        self.assertEqual(len(public_artifacts), 7)
        for artifact in public_artifacts:
            self.assertEqual(
                _sha256((COMMITTED_RUN / artifact["path"]).read_bytes()),
                artifact["sha256"],
            )
        self.assertEqual(
            {path.name for path in COMMITTED_RUN.iterdir()},
            {"manifest.json", *(artifact["path"] for artifact in public_artifacts)},
        )
        self.assertFalse((COMMITTED_RUN / "runner").exists())

    def test_committed_validation_reconciles_the_complete_execution(self) -> None:
        validation = json.loads(
            (COMMITTED_RUN / "study-validation.json").read_text(encoding="utf-8")
        )

        self.assertEqual(validation["status"], "passed")
        self.assertEqual(validation["protocol_violations"], [])
        self.assertEqual(validation["deviations"], [])
        self.assertEqual(
            validation["sample_reconciliation"],
            {
                "source_observation_count": 12305,
                "attempted_episode_count": 1365,
                "included_episode_count": 1365,
                "excluded_episode_count": 0,
                "runner_episode_count": 1365,
                "runner_comparison_count": 49140,
                "confirmatory_uncertainty_cell_count": 36,
            },
        )
        self.assertEqual(
            validation["aggregate_reconciliation"]["status"], "passed"
        )
        self.assertEqual(
            validation["aggregate_reconciliation"]["group_count"], 216
        )
        self.assertTrue(
            all(
                check["status"] == "passed"
                for check in validation["shared_runner_validation"]["checks"]
            )
        )

    def test_committed_outcomes_keep_analysis_tiers_and_claims_bounded(self) -> None:
        aggregates = json.loads(
            (COMMITTED_RUN / "historical-aggregates.json").read_text(
                encoding="utf-8"
            )
        )
        uncertainty = json.loads(
            (COMMITTED_RUN / "uncertainty.json").read_text(encoding="utf-8")
        )
        h1 = [
            group
            for group in aggregates["groups"]
            if group["analysis_tier"] == "confirmatory"
            and group["comparison"] == "corrected_guarded_vs_dca"
        ]
        h2 = [
            group
            for group in aggregates["groups"]
            if group["analysis_tier"] == "confirmatory"
            and group["comparison"] == "corrected_guarded_vs_neutral_guarded"
        ]
        net = [
            group
            for group in aggregates["groups"]
            if group["cost_scenario"] != "frictionless"
            and group["coverage"] != "1"
            and group["comparison"] == "corrected_guarded_vs_dca"
        ]
        architecture = [
            group
            for group in aggregates["groups"]
            if group["cost_scenario"] == "frictionless"
            and group["coverage"] != "1"
            and group["comparison"] == "neutral_guarded_vs_dca"
        ]
        collapsed = [
            group for group in aggregates["groups"] if group["coverage"] == "1"
        ]

        self.assertEqual(len(h1), 18)
        self.assertTrue(
            all(Decimal(group["median_relative_terminal_wealth_gap"]) < 0 for group in h1)
        )
        self.assertEqual(
            min(Decimal(group["median_relative_terminal_wealth_gap"]) for group in h1),
            Decimal(
                "-0.0459315460329597585944088669914816089333859199860058448171075"
            ),
        )
        self.assertEqual(len(h2), 18)
        self.assertEqual(
            sum(
                Decimal(group["median_relative_terminal_wealth_gap"]) < 0
                for group in h2
            ),
            17,
        )
        self.assertEqual(len(architecture), 18)
        self.assertTrue(
            all(
                Decimal(group["median_relative_terminal_wealth_gap"]) < 0
                for group in architecture
            )
        )
        self.assertEqual(len(net), 36)
        self.assertTrue(
            all(Decimal(group["median_relative_terminal_wealth_gap"]) < 0 for group in net)
        )
        self.assertTrue(
            all(
                Decimal(group["minimum_relative_terminal_wealth_gap"])
                >= Decimal(group["coverage"]) - 1
                for group in net
            )
        )
        self.assertTrue(
            all(
                group["analysis_tier"] == "robustness"
                and group["theorem_scope"] == "outside-current-safety-theorem"
                for group in net
            )
        )
        self.assertEqual(len(collapsed), 54)
        self.assertTrue(
            all(
                group["minimum_relative_terminal_wealth_gap"] == "0"
                and group["maximum_relative_terminal_wealth_gap"] == "0"
                for group in collapsed
            )
        )
        h1_uncertainty = [
            cell
            for cell in uncertainty["cells"]
            if cell["hypothesis_id"] == "H1-complete-system"
        ]
        self.assertEqual(len(h1_uncertainty), 18)
        self.assertTrue(
            all(Decimal(cell["interval_upper"]) < 0 for cell in h1_uncertainty)
        )
        self.assertEqual(
            sum(
                Decimal(cell["holm_adjusted_p_value"]) < Decimal("0.05")
                for cell in uncertainty["cells"]
                if cell["hypothesis_id"] == "H1-complete-system"
            ),
            9,
        )
        self.assertEqual(
            sum(
                Decimal(cell["holm_adjusted_p_value"]) < Decimal("0.05")
                for cell in uncertainty["cells"]
                if cell["hypothesis_id"] == "H2-signal-contribution"
            ),
            0,
        )
        self.assertEqual(
            {
                (
                    cell["dataset_id"],
                    cell["horizon_months"],
                    cell["coverage"],
                )
                for cell in h1_uncertainty
                if Decimal(cell["holm_adjusted_p_value"]) < Decimal("0.05")
            },
            {
                ("btc-usd-daily", 36, "0.9"),
                ("btc-usd-daily", 60, "0.5"),
                ("btc-usd-daily", 60, "0.9"),
                ("spy-adjusted-daily", 12, "0.5"),
                ("spy-adjusted-daily", 12, "0.75"),
                ("spy-adjusted-daily", 12, "0.9"),
                ("spy-adjusted-daily", 36, "0.5"),
                ("spy-adjusted-daily", 36, "0.75"),
                ("spy-adjusted-daily", 36, "0.9"),
            },
        )

    def test_report_and_audit_join_the_run_and_bound_the_claims(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        audit = AUDIT.read_text(encoding="utf-8")

        required_report_text = {
            RUN_ID,
            "18 non-unit primary frictionless cells",
            "full 36-cell H1/H2",
            "does not establish that the signal is zero or equivalent",
            "cellwise and not multiplicity-adjusted",
            "not covered by the current safety theorem",
            "This run did not execute the protocol's separate robustness",
            "realized associations among overlapping historical windows",
            "../../research/notes/yahoo-finance-historical-data-provider-review.md",
            "../../research/theorems/epsilon-dca-safety-unit-guardrail.md",
            "../../research/theorems/arbitrary-horizon-performance-boundary.md",
            "../../docs/adr/0008-place-empirical-protocol-input-run-layers.md",
        }
        self.assertEqual(
            {text for text in required_report_text if text not in report}, set()
        )
        self.assertIn("## Independent domain review", audit)
        self.assertIn("Result: **pass**", audit)
        self.assertIn("recomputed every bootstrap seed", audit)
        self.assertIn("unexecuted robustness grids are not claimed", audit)

    def test_report_summary_tables_are_derived_from_committed_aggregates(self) -> None:
        aggregates = json.loads(
            (COMMITTED_RUN / "historical-aggregates.json").read_text(
                encoding="utf-8"
            )
        )["groups"]
        uncertainty = json.loads(
            (COMMITTED_RUN / "uncertainty.json").read_text(encoding="utf-8")
        )["cells"]
        report = REPORT.read_text(encoding="utf-8")

        def percent(value: object, *, signed: bool = True) -> str:
            sign = "+" if signed else ""
            return f"{Decimal(str(value)) * Decimal('100'):{sign}.3f}%"

        dataset_labels = {
            "btc-usd-daily": "BTC-USD",
            "spy-adjusted-daily": "SPY",
        }
        missing_rows: list[str] = []
        for dataset_id, horizon in (
            ("btc-usd-daily", 12),
            ("btc-usd-daily", 36),
            ("btc-usd-daily", 60),
            ("spy-adjusted-daily", 12),
            ("spy-adjusted-daily", 36),
            ("spy-adjusted-daily", 60),
        ):
            cells = [
                group
                for group in aggregates
                if group["analysis_tier"] == "confirmatory"
                and group["dataset_id"] == dataset_id
                and group["horizon_months"] == horizon
            ]
            h1 = [
                group
                for group in cells
                if group["comparison"] == "corrected_guarded_vs_dca"
            ]
            h2 = [
                group
                for group in cells
                if group["comparison"]
                == "corrected_guarded_vs_neutral_guarded"
            ]

            def median_range(groups: list[dict[str, object]]) -> str:
                medians = [
                    Decimal(str(group["median_relative_terminal_wealth_gap"]))
                    for group in groups
                ]
                return f"{percent(min(medians))} to {percent(max(medians))}"

            def significant_coverages(hypothesis_id: str) -> str:
                coverages = sorted(
                    (
                        Decimal(str(cell["coverage"]))
                        for cell in uncertainty
                        if cell["hypothesis_id"] == hypothesis_id
                        and cell["dataset_id"] == dataset_id
                        and cell["horizon_months"] == horizon
                        and Decimal(str(cell["holm_adjusted_p_value"]))
                        < Decimal("0.05")
                    )
                )
                return ", ".join(format(value, "f") for value in coverages) or "none"

            expected_row = (
                f"| {dataset_labels[dataset_id]} | {horizon} months | "
                f"{h1[0]['sample_count']} | {median_range(h1)} | "
                f"{significant_coverages('H1-complete-system')} | "
                f"{median_range(h2)} | "
                f"{significant_coverages('H2-signal-contribution')} |"
            )
            if expected_row not in report:
                missing_rows.append(expected_row)

        cost_labels = {
            "proportional-10bps": "Proportional 10 bps",
            "fixed-1-usd": "Fixed USD 1 per purchase",
        }
        for cost_id in ("proportional-10bps", "fixed-1-usd"):
            cells = [
                group
                for group in aggregates
                if group["cost_scenario"] == cost_id
                and group["coverage"] != "1"
                and group["comparison"] == "corrected_guarded_vs_dca"
            ]
            medians = [
                Decimal(str(group["median_relative_terminal_wealth_gap"]))
                for group in cells
            ]
            worst = max(
                Decimal(str(group["worst_observed_relative_shortfall"]))
                for group in cells
            )
            expected_row = (
                f"| {cost_labels[cost_id]} | {len(cells)} | "
                f"{percent(min(medians))} to {percent(max(medians))} | "
                f"{percent(worst, signed=False)} |"
            )
            if expected_row not in report:
                missing_rows.append(expected_row)

        self.assertEqual(missing_rows, [])

    def test_reconciliation_mismatch_stops_before_policy_execution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            preparation, accepted_manifest = _write_preparation_fixture(root)
            reconciliation_path = preparation / "reconciliation.json"
            reconciliation = json.loads(reconciliation_path.read_text(encoding="utf-8"))
            reconciliation["included_episode_count"] = 0
            reconciliation_path.write_text(
                _canonical_json(reconciliation) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            validation_path = preparation / "validation.json"
            validation = json.loads(validation_path.read_text(encoding="utf-8"))
            validation["reconciliation"] = reconciliation
            validation_path.write_text(
                _canonical_json(validation) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            _reseal_preparation(preparation, accepted_manifest)
            output_root = root / "outcomes"

            with self.assertRaises(ExperimentValidationError) as caught:
                run_historical_study_from_paths(
                    CONFIG,
                    accepted_manifest,
                    preparation,
                    output_root,
                )

            self.assertEqual(caught.exception.code, "preparation_count_mismatch")
            self.assertFalse(output_root.exists())

    def test_module_command_executes_the_accepted_study(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            preparation, accepted_manifest = _write_preparation_fixture(root)
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                return_code = historical_study_main(
                    [
                        "--config",
                        str(CONFIG),
                        "--accepted-preparation-manifest",
                        str(accepted_manifest),
                        "--preparation-directory",
                        str(preparation),
                        "--output-root",
                        str(root / "outcomes"),
                        "--publication-root",
                        str(root / "published"),
                    ]
                )

            receipt = json.loads(stdout.getvalue())
            self.assertEqual(return_code, 0)
            self.assertEqual(receipt["status"], "completed")
            self.assertTrue(Path(receipt["manifest"]).is_file())
            self.assertTrue(Path(receipt["publication_manifest"]).is_file())

    def test_confirmatory_cell_seed_matches_registered_literal(self) -> None:
        self.assertEqual(
            confirmatory_cell_seed(
                20260825,
                dataset_id="spy-adjusted-daily",
                horizon_months=12,
                coverage="0.9",
                comparison="corrected_guarded_vs_dca",
                corrected_mean_config="identity-a0-b0",
                cost_scenario="frictionless",
            ),
            8587834312629207422,
        )

    def test_circular_block_bootstrap_matches_hand_computed_fixture(self) -> None:
        result = circular_moving_block_bootstrap(
            (Decimal("-0.4"), Decimal("-0.2"), Decimal("-0.1"), Decimal("0.4")),
            block_length=2,
            replicates=5,
            seed=17,
        )

        self.assertEqual(result.observed_statistic, Decimal("-0.15"))
        self.assertEqual(
            result.replicate_statistics,
            (
                Decimal("0.15"),
                Decimal("0.15"),
                Decimal("-0.1"),
                Decimal("-0.3"),
                Decimal("-0.15"),
            ),
        )
        self.assertEqual(result.interval_lower, Decimal("-0.285"))
        self.assertEqual(result.interval_upper, Decimal("0.15"))
        self.assertEqual(result.centered_tail_count, 3)
        self.assertEqual(result.p_value_numerator, 4)
        self.assertEqual(result.p_value_denominator, 6)

    def test_input_artifact_mismatch_stops_before_outcome_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            preparation = root / "preparation"
            preparation.mkdir()
            runner_input = preparation / "runner-input.json"
            runner_input.write_text("{}\n", encoding="utf-8", newline="\n")
            manifest = {
                "schema_version": "smartdca-historical-input-manifest/1",
                "run_id": "fixture-preparation",
                "config_sha256": _sha256(CONFIG.read_bytes()),
                "runner_input_sha256": "0" * 64,
                "policy_execution": "not-run",
                "artifacts": [
                    {
                        "path": "runner-input.json",
                        "sha256": _sha256(runner_input.read_bytes()),
                    }
                ],
            }
            manifest_payload = (_canonical_json(manifest) + "\n").encode("utf-8")
            (preparation / "manifest.json").write_bytes(manifest_payload)
            accepted_manifest = root / "accepted-manifest.json"
            accepted_manifest.write_bytes(manifest_payload)
            runner_input.write_text(
                '{"changed":true}\n', encoding="utf-8", newline="\n"
            )
            output_root = root / "outcomes"

            with self.assertRaises(ExperimentValidationError) as caught:
                run_historical_study_from_paths(
                    CONFIG,
                    accepted_manifest,
                    preparation,
                    output_root,
                )

            self.assertEqual(caught.exception.code, "artifact_fingerprint_mismatch")
            self.assertFalse(output_root.exists())

    def test_accepted_preparation_runs_the_complete_shared_policy_grid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            preparation, accepted_manifest = _write_preparation_fixture(root)

            bundle = run_historical_study_from_paths(
                CONFIG,
                accepted_manifest,
                preparation,
                root / "outcomes",
                publication_root=root / "published",
            )

            self.assertTrue(bundle.output_directory.is_dir())
            self.assertEqual(bundle.manifest["config_sha256"], _sha256(CONFIG.read_bytes()))
            self.assertEqual(
                bundle.manifest["runner_input_sha256"],
                json.loads((preparation / "manifest.json").read_text())["runner_input_sha256"],
            )
            self.assertEqual(bundle.runner.validation["ledger_count"], 36)
            self.assertEqual(bundle.runner.validation["episode_result_count"], 36)
            self.assertEqual(
                {ledger["policy"] for ledger in bundle.runner.ledgers},
                {"dca", "neutral_guarded", "corrected_guarded"},
            )
            self.assertEqual(
                {ledger["cost_scenario"] for ledger in bundle.runner.ledgers},
                {"frictionless", "proportional-10bps", "fixed-1-usd"},
            )
            self.assertEqual(bundle.aggregates["group_count"], 36)
            collapsed = next(
                group
                for group in bundle.aggregates["groups"]
                if group["coverage"] == "1"
                and group["cost_scenario"] == "frictionless"
                and group["comparison"] == "corrected_guarded_vs_dca"
            )
            self.assertEqual(collapsed["sample_count"], 1)
            self.assertEqual(collapsed["median_relative_terminal_wealth_gap"], "0")
            self.assertEqual(collapsed["mean_terminal_cash_gap"], "0")
            self.assertEqual(collapsed["mean_terminal_unit_gap"], "0")
            self.assertEqual(collapsed["worst_observed_relative_shortfall"], "0")
            self.assertEqual(collapsed["median_wealth_ratio"], "1")
            self.assertEqual(collapsed["minimum_wealth_ratio"], "1")
            self.assertEqual(collapsed["maximum_wealth_ratio"], "1")
            self.assertEqual(collapsed["wealth_ratio_quantile_0.05"], "1")
            self.assertEqual(collapsed["wealth_ratio_quantile_0.95"], "1")
            self.assertEqual(
                (collapsed["win_count"], collapsed["tie_count"], collapsed["loss_count"]),
                (0, 1, 0),
            )
            self.assertTrue(
                (bundle.output_directory / "historical-aggregates.json").is_file()
            )
            self.assertEqual(bundle.uncertainty["cell_count"], 6)
            for cell in bundle.uncertainty["cells"]:
                self.assertEqual(cell["method"], "circular-moving-block-bootstrap")
                self.assertEqual(cell["replicates"], 10000)
                self.assertEqual(cell["block_length"], 12)
                self.assertEqual(cell["sample_count"], 1)
                self.assertEqual(
                    cell["interval_lower"], cell["observed_statistic"]
                )
                self.assertEqual(
                    cell["interval_upper"], cell["observed_statistic"]
                )
                self.assertIsInstance(cell["holm_adjusted_p_value"], str)
            self.assertTrue((bundle.output_directory / "uncertainty.json").is_file())
            self.assertEqual(bundle.validation["status"], "passed")
            self.assertEqual(
                bundle.validation["aggregate_reconciliation"]["status"], "passed"
            )
            self.assertEqual(
                bundle.validation["aggregate_reconciliation"]["group_count"], 36
            )
            self.assertEqual(
                bundle.validation["sample_reconciliation"],
                {
                    "source_observation_count": 12,
                    "attempted_episode_count": 1,
                    "included_episode_count": 1,
                    "excluded_episode_count": 0,
                    "runner_episode_count": 1,
                    "runner_comparison_count": 36,
                    "confirmatory_uncertainty_cell_count": 6,
                },
            )
            self.assertTrue(
                (bundle.output_directory / "study-validation.json").is_file()
            )
            self.assertIsNotNone(bundle.publication_directory)
            publication = bundle.publication_directory
            assert publication is not None
            self.assertEqual(
                (publication / "manifest.json").read_bytes(),
                (bundle.output_directory / "manifest.json").read_bytes(),
            )
            self.assertFalse((publication / "runner").exists())
            self.assertFalse((publication / "bootstrap-replicates.jsonl.gz").exists())
            public_paths = {
                artifact["path"]
                for artifact in bundle.manifest["artifacts"]
                if artifact["retention"] == "public-derived"
            }
            private_paths = {
                artifact["path"]
                for artifact in bundle.manifest["artifacts"]
                if artifact["retention"] == "private-retained"
            }
            self.assertEqual(
                public_paths,
                {
                    "aggregate-reconciliation.json",
                    "historical-aggregates.json",
                    "historical-figure-ready.csv",
                    "private-artifact-receipt.json",
                    "report-tables.md",
                    "study-validation.json",
                    "uncertainty.json",
                },
            )
            self.assertIn("runner/ledgers.jsonl.gz", private_paths)
            self.assertIn("runner/episode-results.jsonl", private_paths)
            for artifact in bundle.manifest["artifacts"]:
                root_directory = (
                    publication
                    if artifact["retention"] == "public-derived"
                    else bundle.output_directory
                )
                self.assertEqual(
                    _sha256((root_directory / artifact["path"]).read_bytes()),
                    artifact["sha256"],
                )


if __name__ == "__main__":
    unittest.main()
