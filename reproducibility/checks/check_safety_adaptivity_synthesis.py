"""Public-contract checks for the cross-layer safety-adaptivity synthesis."""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from reproducibility.safety_adaptivity_synthesis import (
    SynthesisIdentityCollisionError,
    SynthesisValidationError,
    run_synthesis,
)


ROOT = Path(__file__).resolve().parents[2]
SYNTHESIS = ROOT / "experiments/inputs/safety-adaptivity-synthesis-v1.json"
RUN_ID = (
    "smartdca-synthesis-v1-"
    "394aa4d22f52ec12aca69679780670d49caa671d5935963869f41c1b5b557f26"
)
COMMITTED_RUN = ROOT / "reports/experiments/runs" / RUN_ID
REPORT = ROOT / "reports/experiments/safety-adaptivity-tradeoff-synthesis.md"
AUDIT = ROOT / "research/notes/safety-adaptivity-tradeoff-synthesis-audit.md"
WORKFLOW = ROOT / ".github/workflows/verification.yml"
README = ROOT / "README.md"


class SafetyAdaptivitySynthesisContractTest(unittest.TestCase):
    def test_reviewed_sources_generate_role_separated_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = run_synthesis(
                SYNTHESIS,
                Path(directory),
                repository_root=ROOT,
            )

            validation = json.loads(
                (bundle.output_directory / "source-validation.json").read_text()
            )
            self.assertEqual(validation["reviewed_source_count"], 4)
            self.assertEqual(validation["rejected_source_count"], 0)
            self.assertEqual(
                {row["evidence_layer"] for row in validation["sources"]},
                {"deterministic", "stochastic", "historical"},
            )
            self.assertTrue(all(row["review_status"] == "pass" for row in validation["sources"]))
            self.assertTrue(
                all(
                    any(
                        artifact["kind"] == "reconciliation"
                        for artifact in row["supporting_artifacts"]
                    )
                    for row in validation["sources"]
                )
            )

            with (bundle.output_directory / "normalized-evidence.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(len(rows), 2754)
            self.assertIn("scheduled_deposit_count", rows[0])
            self.assertIn("mean_contributed_capital", rows[0])
            self.assertIn("mean_left_guardrail_floor", rows[0])
            self.assertIn("mean_left_guardrail_floor_per_deposit", rows[0])
            self.assertTrue(
                all(
                    Decimal("0")
                    <= Decimal(row["mean_left_guardrail_floor_per_deposit"])
                    <= Decimal("1")
                    for row in rows
                )
            )
            self.assertEqual(
                {row["comparison_role"] for row in rows},
                {
                    "complete-system performance",
                    "corrected-mean signal contribution",
                    "safety-architecture behavior",
                },
            )
            self.assertEqual(
                {row["cost_scope"] for row in rows},
                {
                    "gross frictionless; epsilon-DCA theorem scope for guarded policies",
                    "net of proportional costs; outside current safety theorem",
                    "net of fixed costs; outside current safety theorem",
                },
            )

            specification = json.loads(SYNTHESIS.read_text())
            for source in specification["reviewed_sources"]:
                aggregate_path = ROOT / source["aggregate_path"]
                source_groups = json.loads(aggregate_path.read_text())["groups"]
                normalized_groups = [
                    row for row in rows if row["source_id"] == source["source_id"]
                ]
                self.assertEqual(len(normalized_groups), len(source_groups))
                deposit = Decimal(source["deposit_amount"])
                for source_row, normalized_row in zip(
                    source_groups,
                    normalized_groups,
                    strict=True,
                ):
                    for field in (
                        "comparison",
                        "cost_scenario",
                        "coverage",
                        "horizon_months",
                        "family",
                        "dataset_id",
                        "generator_config_id",
                        "schedule_id",
                    ):
                        self.assertEqual(
                            normalized_row[field],
                            str(source_row.get(field, "")),
                        )
                    raw_floor = Decimal(source_row["mean_left_guardrail_floor"])
                    floor_share = Decimal(
                        normalized_row["mean_left_guardrail_floor_per_deposit"]
                    )
                    self.assertEqual(
                        Decimal(normalized_row["mean_left_guardrail_floor"]),
                        raw_floor,
                    )
                    self.assertEqual(floor_share, raw_floor / deposit)
                    self.assertLessEqual(
                        floor_share,
                        Decimal(normalized_row["coverage"]),
                    )

    def test_one_manifest_generates_tables_curves_figures_and_claim_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = run_synthesis(
                SYNTHESIS,
                Path(directory),
                repository_root=ROOT,
            )

            expected_artifacts = {
                "claim-receipts.json",
                "cost-scope-summary.csv",
                "cross-layer-summary.csv",
                "frictionless-safety-factor.svg",
                "manifest.json",
                "mechanism-curves.svg",
                "net-cost-summary.svg",
                "normalized-evidence.csv",
                "primary-tables.md",
                "safety-factor-curve.csv",
                "source-validation.json",
                "summary-reconciliation.json",
                "terminal-attribution.svg",
            }
            self.assertEqual(
                {path.name for path in bundle.output_directory.iterdir()},
                expected_artifacts,
            )

            with (bundle.output_directory / "safety-factor-curve.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                curve_rows = list(csv.DictReader(handle))
            self.assertEqual(len(curve_rows), 81)
            self.assertTrue(
                all(row["aggregation"] == "descriptive across source aggregate cells; no cross-layer pooling" for row in curve_rows)
            )
            self.assertEqual(
                {
                    "analysis_tier",
                    "median_of_cell_medians",
                    "minimum_cell_downside_0.05",
                    "maximum_worst_observed_relative_shortfall",
                    "median_left_cash_drag",
                    "median_left_asset_exposure",
                    "median_left_guardrail_activation_frequency",
                    "median_left_guardrail_floor_per_deposit",
                    "median_left_purchase_count",
                    "mean_cash_contribution_per_contributed_capital",
                    "mean_unit_contribution_per_contributed_capital",
                    "mean_terminal_wealth_gap_per_contributed_capital",
                }
                - set(curve_rows[0]),
                set(),
            )
            monthly_curve = [
                row
                for row in curve_rows
                if row["slice_id"] == "historical-monthly-robustness"
            ]
            self.assertEqual(
                {row["analysis_tier"] for row in monthly_curve if row["coverage"] == "1"},
                {"secondary"},
            )
            self.assertEqual(
                {row["analysis_tier"] for row in monthly_curve if row["coverage"] != "1"},
                {"robustness"},
            )
            self.assertNotIn("mean_cash_contribution", curve_rows[0])
            self.assertNotIn("mean_unit_contribution", curve_rows[0])
            self.assertTrue(
                all(
                    abs(
                        float(row["mean_cash_contribution_per_contributed_capital"])
                        + float(row["mean_unit_contribution_per_contributed_capital"])
                        - float(
                            row[
                                "mean_terminal_wealth_gap_per_contributed_capital"
                            ]
                        )
                    )
                    < 1e-12
                    for row in curve_rows
                )
            )
            curve_keyed = {
                (row["slice_id"], row["coverage"], row["comparison"]): row
                for row in curve_rows
            }
            self.assertEqual(
                curve_keyed[
                    (
                        "historical-primary",
                        "0.75",
                        "corrected_guarded_vs_dca",
                    )
                ]["median_left_guardrail_floor_per_deposit"],
                "0.0724748204530593825152922880162685916232314644690469932830587",
            )
            self.assertEqual(
                curve_keyed[
                    (
                        "historical-quarterly-robustness",
                        "0.75",
                        "corrected_guarded_vs_dca",
                    )
                ]["median_left_guardrail_floor_per_deposit"],
                "0.3120349192261540510068048942879505682805578985331072602279935",
            )

            with (bundle.output_directory / "cross-layer-summary.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                summaries = list(csv.DictReader(handle))
            keyed = {(row["slice_id"], row["comparison"]): row for row in summaries}
            historical_h1 = keyed[
                ("historical-confirmatory-nonunit", "corrected_guarded_vs_dca")
            ]
            self.assertEqual(historical_h1["analysis_tier"], "confirmatory")
            self.assertEqual(
                (
                    historical_h1["cell_count"],
                    historical_h1["negative_median_cells"],
                    historical_h1["holm_significant_cells"],
                    historical_h1["minimum_cell_median"],
                    historical_h1["maximum_cell_median"],
                ),
                (
                    "18",
                    "18",
                    "9",
                    "-0.0459315460329597585944088669914816089333859199860058448171075",
                    "-0.00335266351298036186677439396225895454280836618257622733904455",
                ),
            )
            historical_h2 = keyed[
                (
                    "historical-confirmatory-nonunit",
                    "corrected_guarded_vs_neutral_guarded",
                )
            ]
            self.assertEqual(historical_h2["analysis_tier"], "confirmatory")
            self.assertEqual(
                (
                    historical_h2["negative_median_cells"],
                    historical_h2["positive_median_cells"],
                    historical_h2["holm_significant_cells"],
                ),
                ("17", "1", "0"),
            )
            self.assertEqual(
                keyed[
                    (
                        "historical-confirmatory-nonunit",
                        "neutral_guarded_vs_dca",
                    )
                ]["analysis_tier"],
                "secondary",
            )
            deterministic_signal = keyed[
                (
                    "deterministic-primary-lambda-075",
                    "corrected_guarded_vs_neutral_guarded",
                )
            ]
            self.assertEqual(
                (
                    deterministic_signal["negative_median_cells"],
                    deterministic_signal["zero_median_cells"],
                    deterministic_signal["positive_median_cells"],
                ),
                ("5", "1", "8"),
            )
            stochastic_complete = keyed[
                ("stochastic-primary-60m-lambda-075", "corrected_guarded_vs_dca")
            ]
            self.assertEqual(
                (
                    stochastic_complete["negative_median_cells"],
                    stochastic_complete["positive_median_cells"],
                ),
                ("3", "2"),
            )
            quarterly_complete = keyed[
                (
                    "historical-quarterly-robustness-nonunit",
                    "corrected_guarded_vs_dca",
                )
            ]
            self.assertEqual(
                (
                    quarterly_complete["sample_count_minimum"],
                    quarterly_complete["sample_count_maximum"],
                ),
                ("4", "130"),
            )

            with (bundle.output_directory / "cost-scope-summary.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                cost_rows = list(csv.DictReader(handle))
            self.assertEqual(len(cost_rows), 48)
            self.assertTrue(all(";" not in row["analysis_tiers"] for row in cost_rows))
            self.assertTrue(
                all(row["analysis_tier"] in {"primary", "regression", "exploratory", "robustness"} for row in cost_rows)
            )
            historical_costs = [
                row
                for row in cost_rows
                if row["source_id"] == "historical-confirmatory-v1"
                and row["comparison"] == "corrected_guarded_vs_dca"
            ]
            self.assertEqual(len(historical_costs), 2)
            self.assertTrue(
                all(
                    (
                        row["cell_count"],
                        row["negative_median_cells"],
                        row["zero_median_cells"],
                        row["positive_median_cells"],
                    )
                    == ("18", "18", "0", "0")
                    for row in historical_costs
                )
            )

            claims = json.loads(
                (bundle.output_directory / "claim-receipts.json").read_text()
            )
            self.assertEqual(claims["lambda_one"]["nonzero_gap_cells"], 0)
            self.assertEqual(
                claims["frictionless_relative_wealth_floor"]["violation_count"], 0
            )
            self.assertEqual(claims["historical_inference"]["holm_family_size"], 36)
            self.assertEqual(
                claims["historical_inference"]["h1_significant_cells"], 9
            )
            self.assertEqual(
                claims["historical_inference"]["h2_significant_cells"], 0
            )

            tables = (bundle.output_directory / "primary-tables.md").read_text()
            self.assertIn("Complete-system performance", tables)
            self.assertIn("Corrected-mean signal contribution", tables)
            self.assertIn("Safety-architecture behavior", tables)
            self.assertIn("Gross frictionless safety-factor curve", tables)
            self.assertIn("Net-of-cost empirical robustness", tables)
            self.assertIn("Guardrail floor / deposit", tables)
            self.assertIn("not an independent-sample interval", tables)

            gross_figure = (
                bundle.output_directory / "frictionless-safety-factor.svg"
            ).read_text()
            net_figure = (
                bundle.output_directory / "net-cost-summary.svg"
            ).read_text()
            attribution_figure = (
                bundle.output_directory / "terminal-attribution.svg"
            ).read_text()
            self.assertIn("Gross frictionless safety-factor curve", gross_figure)
            self.assertIn("Net-of-cost empirical robustness", net_figure)
            self.assertIn("outside current safety theorem", net_figure)
            self.assertIn(
                "Median guardrail floor share of deposit",
                (bundle.output_directory / "mechanism-curves.svg").read_text(),
            )
            self.assertIn("primary-monthly-robustness-coverage", net_figure)
            self.assertIn("robustness-quarterly-horizons", net_figure)
            self.assertIn("share of contributed capital", attribution_figure)

    def test_pending_review_state_is_rejected_before_output(self) -> None:
        specification = json.loads(SYNTHESIS.read_text())
        specification["reviewed_sources"][0]["review_status"] = "pending"
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            manifest = temporary_root / "pending-review.json"
            manifest.write_text(json.dumps(specification), encoding="utf-8")

            with self.assertRaisesRegex(
                SynthesisValidationError,
                "review_status: must equal pass",
            ):
                run_synthesis(
                    manifest,
                    temporary_root / "output",
                    repository_root=ROOT,
                )
            self.assertFalse((temporary_root / "output").exists())

    def test_deposit_amount_must_match_reviewed_source_bytes(self) -> None:
        specification = json.loads(SYNTHESIS.read_text())
        specification["reviewed_sources"][0]["deposit_amount"] = "999"
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            manifest = temporary_root / "wrong-deposit.json"
            manifest.write_text(json.dumps(specification), encoding="utf-8")

            with self.assertRaisesRegex(
                SynthesisValidationError,
                "deposit_amount: does not match reviewed source bytes",
            ):
                run_synthesis(
                    manifest,
                    temporary_root / "output",
                    repository_root=ROOT,
                )
            self.assertFalse((temporary_root / "output").exists())

    def test_same_manifest_replays_byte_for_byte_and_never_overwrites(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_bundle = run_synthesis(SYNTHESIS, Path(first), repository_root=ROOT)
            second_bundle = run_synthesis(SYNTHESIS, Path(second), repository_root=ROOT)

            self.assertEqual(first_bundle.synthesis_run_id, second_bundle.synthesis_run_id)
            first_files = {
                path.name: path.read_bytes()
                for path in first_bundle.output_directory.iterdir()
            }
            second_files = {
                path.name: path.read_bytes()
                for path in second_bundle.output_directory.iterdir()
            }
            self.assertEqual(first_files, second_files)

            manifest = json.loads(first_files["manifest.json"])
            self.assertEqual(
                {artifact["path"] for artifact in manifest["artifacts"]},
                set(first_files) - {"manifest.json"},
            )
            for artifact in manifest["artifacts"]:
                payload = first_files[artifact["path"]]
                self.assertEqual(artifact["bytes"], len(payload))
                self.assertEqual(
                    artifact["sha256"], hashlib.sha256(payload).hexdigest()
                )

            with self.assertRaises(SynthesisIdentityCollisionError):
                run_synthesis(SYNTHESIS, Path(first), repository_root=ROOT)

    def test_runtime_patch_is_normalized_and_runtime_family_is_identity_bound(self) -> None:
        with (
            tempfile.TemporaryDirectory() as first,
            tempfile.TemporaryDirectory() as second,
            tempfile.TemporaryDirectory() as third,
            tempfile.TemporaryDirectory() as fourth,
        ):
            with (
                patch(
                    "reproducibility.safety_adaptivity_synthesis.platform.python_implementation",
                    return_value="CPython",
                ),
                patch(
                    "reproducibility.safety_adaptivity_synthesis.platform.python_version",
                    return_value="3.12.14",
                ),
            ):
                first_bundle = run_synthesis(
                    SYNTHESIS, Path(first), repository_root=ROOT
                )
            with (
                patch(
                    "reproducibility.safety_adaptivity_synthesis.platform.python_implementation",
                    return_value="CPython",
                ),
                patch(
                    "reproducibility.safety_adaptivity_synthesis.platform.python_version",
                    return_value="3.12.99",
                ),
            ):
                second_bundle = run_synthesis(
                    SYNTHESIS, Path(second), repository_root=ROOT
                )
            with (
                patch(
                    "reproducibility.safety_adaptivity_synthesis.platform.python_implementation",
                    return_value="PyPy",
                ),
                patch(
                    "reproducibility.safety_adaptivity_synthesis.platform.python_version",
                    return_value="3.12.14",
                ),
            ):
                third_bundle = run_synthesis(
                    SYNTHESIS, Path(third), repository_root=ROOT
                )
            with (
                patch(
                    "reproducibility.safety_adaptivity_synthesis.platform.python_implementation",
                    return_value="CPython",
                ),
                patch(
                    "reproducibility.safety_adaptivity_synthesis.platform.python_version",
                    return_value="3.13.0",
                ),
            ):
                fourth_bundle = run_synthesis(
                    SYNTHESIS, Path(fourth), repository_root=ROOT
                )

            self.assertEqual(first_bundle.synthesis_run_id, second_bundle.synthesis_run_id)
            self.assertNotEqual(first_bundle.synthesis_run_id, third_bundle.synthesis_run_id)
            self.assertNotEqual(first_bundle.synthesis_run_id, fourth_bundle.synthesis_run_id)
            self.assertEqual(
                first_bundle.manifest["runtime"],
                {
                    "implementation": "CPython",
                    "python": "3.12",
                    "third_party_dependencies": [],
                },
            )
            self.assertEqual(
                {
                    path.name: path.read_bytes()
                    for path in first_bundle.output_directory.iterdir()
                },
                {
                    path.name: path.read_bytes()
                    for path in second_bundle.output_directory.iterdir()
                },
            )

    def test_committed_package_report_and_repository_gate_agree(self) -> None:
        manifest = json.loads((COMMITTED_RUN / "manifest.json").read_text())
        self.assertEqual(manifest["synthesis_run_id"], RUN_ID)
        self.assertEqual(
            manifest["specification_sha256"],
            hashlib.sha256(SYNTHESIS.read_bytes()).hexdigest(),
        )
        source_path = ROOT / "reproducibility/safety_adaptivity_synthesis.py"
        self.assertEqual(
            manifest["source_sha256"],
            hashlib.sha256(source_path.read_bytes()).hexdigest(),
        )
        for artifact in manifest["artifacts"]:
            payload = (COMMITTED_RUN / artifact["path"]).read_bytes()
            self.assertEqual(len(payload), artifact["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])

        generated = (COMMITTED_RUN / "primary-tables.md").read_text()
        cross_layer_table = generated.split("## Cross-layer findings\n\n", 1)[1].split(
            "\n\n## Gross frictionless safety-factor curve", 1
        )[0]
        report = REPORT.read_text()
        audit = AUDIT.read_text()
        self.assertIn(cross_layer_table, report)
        for required in (
            RUN_ID,
            "all 18 non-unit primary frictionless",
            "full 36-cell H1/H2 family",
            "no Holm-significant H2 result",
            "not evidence of equivalence",
            "not a causal decomposition",
            "outside the current epsilon-DCA theorem",
            "frictionless-safety-factor.svg",
            "mechanism-curves.svg",
            "terminal-attribution.svg",
            "net-cost-summary.svg",
            "conditional size given activation",
            "separately approved effort",
        ):
            self.assertIn(required, report)
        for required in (
            RUN_ID,
            "Result: **pass**, with no blocking scientific issue.",
            "source-bound deposit evidence",
            "all four sources",
            "only four eligible episodes",
            "Six earlier bundles remain preserved",
            "not a conditional size given activation",
        ):
            self.assertIn(required, audit)

        verification_command = (
            "python -m unittest "
            "reproducibility.checks.check_safety_adaptivity_synthesis"
        )
        self.assertIn(verification_command, WORKFLOW.read_text())
        self.assertIn(
            "python -m unittest reproducibility.checks.check_safety_adaptivity_synthesis",
            README.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
