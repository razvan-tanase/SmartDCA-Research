"""Public-contract checks for registered historical robustness execution."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from reproducibility.empirical import VersionedInput
from reproducibility.historical_robustness import (
    HistoricalCellKey,
    NormalizedSeries,
    _execute_slice,
    _quarterly_episode_design,
    _runner_episode,
    _runner_projection,
    build_monthly_robustness_input,
    build_quarterly_episode_attempt,
    classify_analysis_tier,
    load_registered_robustness_execution,
)
from reproducibility.historical_study import AcceptedHistoricalPreparation


ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "experiments/protocols/safety-adaptivity-yahoo-v2.json"
PLAN = (
    ROOT
    / "experiments/inputs/historical-yahoo-registered-robustness-v1.json"
)
ACCEPTED_MANIFEST = (
    ROOT
    / "experiments/inputs/historical-yahoo-preparation-manifest-v5.json"
)
RUN_ID = (
    "smartdca-historical-robustness-v1-"
    "0991d999e1a8070a2a6eb8046b08a91d0e42341995610a602372c52dfab14184"
)
COMMITTED_RUN = ROOT / "reports/experiments/runs" / RUN_ID
REPORT = ROOT / "reports/experiments/confirmatory-historical-evaluation.md"
AUDIT = ROOT / "research/notes/confirmatory-historical-evaluation-audit.md"


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _execution():
    return load_registered_robustness_execution(
        PLAN, PROTOCOL, ACCEPTED_MANIFEST
    )


def _included_quarterly_attempt() -> dict[str, object]:
    series = NormalizedSeries.from_rows(
        [
            {
                "observation_date": "2020-01-02",
                "price": "100",
                "source_row": 2,
            },
            {
                "observation_date": "2020-04-01",
                "price": "80",
                "source_row": 3,
            },
            {
                "observation_date": "2020-07-01",
                "price": "120",
                "source_row": 4,
            },
        ],
        "spy-adjusted-daily",
    )
    return build_quarterly_episode_attempt(
        dataset_id="spy-adjusted-daily",
        series=series,
        nominal_start=date(2020, 1, 1),
        horizon_months=6,
        deposit_amount="1000",
    )


class HistoricalRobustnessEvaluationTest(unittest.TestCase):
    def test_committed_manifest_binds_code_inputs_and_public_artifacts(
        self,
    ) -> None:
        manifest = json.loads(
            (COMMITTED_RUN / "manifest.json").read_text(encoding="utf-8")
        )

        self.assertEqual(manifest["run_id"], RUN_ID)
        self.assertEqual(manifest["protocol_sha256"], _sha256(PROTOCOL.read_bytes()))
        self.assertEqual(
            manifest["execution_plan_sha256"], _sha256(PLAN.read_bytes())
        )
        self.assertEqual(
            manifest["accepted_preparation_manifest_sha256"],
            _sha256(ACCEPTED_MANIFEST.read_bytes()),
        )
        self.assertEqual(
            manifest["source_sha256"],
            _sha256(
                (ROOT / "reproducibility/historical_robustness.py").read_bytes()
            ),
        )
        self.assertEqual(
            manifest["confirmatory_study_sha256"],
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
        private_artifacts = [
            artifact
            for artifact in manifest["artifacts"]
            if artifact["retention"] == "private-retained"
        ]
        self.assertEqual(len(public_artifacts), 5)
        self.assertEqual(len(private_artifacts), 21)
        for artifact in public_artifacts:
            self.assertEqual(
                _sha256((COMMITTED_RUN / artifact["path"]).read_bytes()),
                artifact["sha256"],
            )
        self.assertEqual(
            {path.name for path in COMMITTED_RUN.iterdir()},
            {"manifest.json", *(artifact["path"] for artifact in public_artifacts)},
        )
        self.assertTrue(
            all(
                not (COMMITTED_RUN / artifact["path"]).exists()
                for artifact in private_artifacts
            )
        )

    def test_committed_validation_reconciles_both_registered_schedules(
        self,
    ) -> None:
        validation = json.loads(
            (COMMITTED_RUN / "study-validation.json").read_text(encoding="utf-8")
        )

        self.assertEqual(validation["status"], "passed")
        self.assertEqual(validation["protocol_violations"], [])
        self.assertEqual(validation["deviations"], [])
        self.assertTrue(validation["created_after_confirmatory_outcome_access"])
        self.assertEqual(validation["confirmatory_family_change"], "none")
        self.assertEqual(validation["uncertainty_status"], "not-run-robustness")
        self.assertEqual(
            validation["analysis_tier_counts"],
            {"robustness": 792, "secondary": 18},
        )
        self.assertEqual(
            validation["sample_reconciliation"],
            {
                "source_observation_count": 12305,
                "total_attempted_episode_count": 1793,
                "total_included_episode_count": 1793,
                "total_excluded_episode_count": 0,
                "ledger_count": 108378,
                "comparison_count": 108378,
                "aggregate_group_count": 810,
                "monthly": {
                    "schedule_id": "primary-monthly-robustness-coverage",
                    "source_observation_count": 12305,
                    "attempted_episode_count": 1365,
                    "included_episode_count": 1365,
                    "excluded_episode_count": 0,
                    "exclusion_reasons": {},
                    "runner_input_episode_count": 1365,
                },
                "quarterly": {
                    "schedule_id": "robustness-quarterly-horizons",
                    "source_observation_count": 12305,
                    "attempted_episode_count": 428,
                    "included_episode_count": 428,
                    "excluded_episode_count": 0,
                    "exclusion_reasons": {},
                    "runner_input_episode_count": 428,
                },
            },
        )
        expected_slices = {
            "monthly": (324, 73710),
            "quarterly": (486, 34668),
        }
        for name, (group_count, ledger_count) in expected_slices.items():
            slice_validation = validation["slice_validation"][name]
            self.assertEqual(
                slice_validation["aggregate_reconciliation"]["group_count"],
                group_count,
            )
            self.assertEqual(
                slice_validation["shared_runner_validation"]["ledger_count"],
                ledger_count,
            )
            self.assertTrue(
                all(
                    check["status"] == "passed"
                    for check in slice_validation["shared_runner_validation"][
                        "checks"
                    ]
                )
            )

    def test_committed_outcomes_remain_descriptive_and_schedule_bounded(
        self,
    ) -> None:
        aggregates = json.loads(
            (COMMITTED_RUN / "robustness-aggregates.json").read_text(
                encoding="utf-8"
            )
        )
        groups = aggregates["groups"]

        self.assertEqual(aggregates["group_count"], 810)
        self.assertEqual(len(groups), 810)
        self.assertNotIn("confirmatory", {group["analysis_tier"] for group in groups})
        self.assertEqual(
            {group["uncertainty_status"] for group in groups},
            {"not-run-robustness"},
        )
        self.assertEqual(
            {group["corrected_mean_config"] for group in groups},
            {"identity-a0-b0"},
        )

        def selected(
            schedule: str,
            comparison: str,
            *,
            cost: str = "frictionless",
        ) -> list[dict[str, object]]:
            return [
                group
                for group in groups
                if group["schedule_id"] == schedule
                and group["comparison"] == comparison
                and group["cost_scenario"] == cost
                and group["coverage"] != "1"
            ]

        monthly_complete = selected(
            "primary-monthly-robustness-coverage",
            "corrected_guarded_vs_dca",
        )
        monthly_signal = selected(
            "primary-monthly-robustness-coverage",
            "corrected_guarded_vs_neutral_guarded",
        )
        quarterly_complete = selected(
            "robustness-quarterly-horizons",
            "corrected_guarded_vs_dca",
        )
        quarterly_signal = selected(
            "robustness-quarterly-horizons",
            "corrected_guarded_vs_neutral_guarded",
        )

        self.assertEqual(len(monthly_complete), 30)
        self.assertEqual(len(monthly_signal), 30)
        self.assertEqual(
            {group["coverage"] for group in monthly_complete},
            {"0.99", "0.95", "0.8", "0.6", "0.25"},
        )
        self.assertTrue(
            all(
                Decimal(group["median_relative_terminal_wealth_gap"]) < 0
                for group in [*monthly_complete, *monthly_signal]
            )
        )
        self.assertEqual(len(quarterly_complete), 48)
        self.assertEqual(len(quarterly_signal), 48)
        self.assertEqual(
            {group["coverage"] for group in quarterly_complete},
            {"0.99", "0.95", "0.9", "0.8", "0.75", "0.6", "0.5", "0.25"},
        )
        self.assertTrue(
            all(
                Decimal(group["median_relative_terminal_wealth_gap"]) < 0
                for group in quarterly_complete
            )
        )
        self.assertEqual(
            sum(
                Decimal(group["median_relative_terminal_wealth_gap"]) < 0
                for group in quarterly_signal
            ),
            40,
        )
        self.assertEqual(
            sum(
                Decimal(group["median_relative_terminal_wealth_gap"]) > 0
                for group in quarterly_signal
            ),
            8,
        )

        frictionless_complete = [*monthly_complete, *quarterly_complete]
        self.assertTrue(
            all(
                group["theorem_scope"] == "epsilon-dca"
                and Decimal(group["minimum_relative_terminal_wealth_gap"])
                >= Decimal(group["coverage"]) - 1
                for group in frictionless_complete
            )
        )
        net_complete = [
            group
            for group in groups
            if group["coverage"] != "1"
            and group["cost_scenario"] != "frictionless"
            and group["comparison"] == "corrected_guarded_vs_dca"
        ]
        self.assertEqual(len(net_complete), 156)
        self.assertTrue(
            all(
                Decimal(group["median_relative_terminal_wealth_gap"]) < 0
                and group["theorem_scope"] == "outside-current-safety-theorem"
                for group in net_complete
            )
        )
        collapsed = [group for group in groups if group["coverage"] == "1"]
        self.assertEqual(len(collapsed), 108)
        self.assertTrue(
            all(
                group["minimum_relative_terminal_wealth_gap"] == "0"
                and group["maximum_relative_terminal_wealth_gap"] == "0"
                for group in collapsed
            )
        )

    def test_report_and_audit_join_the_robustness_run_and_bound_claims(
        self,
    ) -> None:
        report = REPORT.read_text(encoding="utf-8")
        audit = AUDIT.read_text(encoding="utf-8")

        required_report_text = {
            RUN_ID,
            "post-confirmatory execution of preregistered robustness axes",
            "All 30 monthly robustness-coverage frictionless complete-system",
            "All 48 quarterly non-unit frictionless complete-system",
            "quarterly signal-only comparison had 40 negative medians",
            "eight positive rows are exactly",
            "No robustness row enters H1/H2",
            "not comparable across the monthly and quarterly schedules",
            "configurations remain unexecuted and deferred",
        }
        self.assertEqual(
            {text for text in required_report_text if text not in report}, set()
        )
        self.assertIn("## Registered robustness extension audit", audit)
        self.assertIn("Result: **pass**", audit)
        self.assertIn("108,378 ledgers and comparison rows", audit)
        self.assertIn("36-test Holm family is unchanged", audit)

    def test_report_robustness_summary_is_derived_from_committed_aggregates(
        self,
    ) -> None:
        groups = json.loads(
            (COMMITTED_RUN / "robustness-aggregates.json").read_text(
                encoding="utf-8"
            )
        )["groups"]
        report = REPORT.read_text(encoding="utf-8")

        def percent(value: Decimal) -> str:
            return f"{value * Decimal('100'):+.4f}%"

        missing_rows: list[str] = []
        schedules = (
            ("primary-monthly-robustness-coverage", "Monthly robustness coverage"),
            ("robustness-quarterly-horizons", "Quarterly robustness horizons"),
        )
        for schedule_id, label in schedules:
            schedule_groups = [
                group
                for group in groups
                if group["schedule_id"] == schedule_id
                and group["cost_scenario"] == "frictionless"
                and group["coverage"] != "1"
            ]
            complete = [
                group
                for group in schedule_groups
                if group["comparison"] == "corrected_guarded_vs_dca"
            ]
            signal = [
                group
                for group in schedule_groups
                if group["comparison"]
                == "corrected_guarded_vs_neutral_guarded"
            ]
            complete_medians = [
                Decimal(group["median_relative_terminal_wealth_gap"])
                for group in complete
            ]
            signal_medians = [
                Decimal(group["median_relative_terminal_wealth_gap"])
                for group in signal
            ]
            expected_row = (
                f"| {label} | {len(complete)} | "
                f"{percent(min(complete_medians))} to "
                f"{percent(max(complete_medians))} | "
                f"{sum(value < 0 for value in signal_medians)} / "
                f"{sum(value > 0 for value in signal_medians)} | "
                f"{percent(min(signal_medians))} to "
                f"{percent(max(signal_medians))} |"
            )
            if expected_row not in report:
                missing_rows.append(expected_row)

        self.assertEqual(missing_rows, [])

    def test_execution_plan_is_an_exact_post_confirmatory_projection(self) -> None:
        execution = _execution()

        self.assertTrue(
            execution.document["created_after_confirmatory_outcome_access"]
        )
        self.assertEqual(
            execution.document["monthly_coverage_extension"]["coverage"],
            execution.protocol["coverage"]["robustness"],
        )
        self.assertEqual(
            execution.document["quarterly_horizon_extension"][
                "horizons_months"
            ],
            execution.protocol["robustness_design"]["horizons_months"],
        )
        self.assertEqual(
            execution.document["quarterly_horizon_extension"]["coverage"],
            [
                *execution.protocol["coverage"]["primary"],
                *execution.protocol["coverage"]["robustness"],
            ],
        )
        self.assertEqual(
            execution.document["analysis"],
            {
                "tier": "robustness",
                "uncertainty": (
                    "descriptive-only; no confirmatory bootstrap or "
                    "multiplicity test"
                ),
                "confirmatory_family_change": "none",
                "classification_rule": (
                    "A row is robustness when its coverage, horizon, "
                    "corrected-mean configuration, cost route, or schedule is "
                    "registered outside the primary frictionless grid. Only "
                    "the sealed primary run can emit confirmatory H1/H2 rows."
                ),
            },
        )

    def test_quarterly_episode_uses_two_deposits_and_exact_calendar_mapping(
        self,
    ) -> None:
        attempt = _included_quarterly_attempt()

        self.assertEqual(attempt["status"], "included")
        self.assertEqual(attempt["horizon_date"], "2020-07-01")
        self.assertEqual(attempt["evaluation_date"], "2020-07-01")
        self.assertEqual(
            [
                (
                    row["nominal_date"],
                    row["purchase_date"],
                    row["mapping_lag_days"],
                )
                for row in attempt["deposit_schedule"]
            ],
            [
                ("2020-01-01", "2020-01-02", 1),
                ("2020-04-01", "2020-04-01", 0),
            ],
        )

    def test_quarterly_episode_retains_a_complete_missing_purchase_attempt(
        self,
    ) -> None:
        series = NormalizedSeries.from_rows(
            [
                {
                    "observation_date": "2020-01-01",
                    "price": "100",
                    "source_row": 2,
                },
                {
                    "observation_date": "2020-04-03",
                    "price": "80",
                    "source_row": 3,
                },
                {
                    "observation_date": "2020-07-01",
                    "price": "120",
                    "source_row": 4,
                },
            ],
            "btc-usd-daily",
        )

        attempt = build_quarterly_episode_attempt(
            dataset_id="btc-usd-daily",
            series=series,
            nominal_start=date(2020, 1, 1),
            horizon_months=6,
            deposit_amount="1000",
        )

        self.assertEqual(attempt["status"], "excluded")
        self.assertEqual(
            attempt["exclusion_reason"], "unavailable_mapped_purchase_date"
        )
        self.assertEqual(len(attempt["deposit_schedule"]), 2)
        self.assertEqual(
            attempt["exclusion_details"],
            {
                "mapping": "first-observation-on-or-after",
                "nominal_date": "2020-04-01",
                "tolerance_days": 1,
                "previous_observation_date": "2020-01-01",
                "next_observation_date": "2020-04-03",
            },
        )

    def test_analysis_tier_uses_every_registered_axis(self) -> None:
        protocol = _execution().protocol
        primary = HistoricalCellKey(
            "spy-adjusted-daily",
            12,
            "0.9",
            "identity-a0-b0",
            "frictionless",
            "corrected_guarded_vs_dca",
            "primary",
        )
        architecture = HistoricalCellKey(
            **{
                **primary.__dict__,
                "comparison": "neutral_guarded_vs_dca",
            }
        )
        collapse = HistoricalCellKey(**{**primary.__dict__, "coverage": "1"})
        variants = (
            HistoricalCellKey(**{**primary.__dict__, "coverage": "0.99"}),
            HistoricalCellKey(
                **{
                    **primary.__dict__,
                    "horizon_months": 6,
                    "design_tier": "robustness",
                }
            ),
            HistoricalCellKey(
                **{
                    **primary.__dict__,
                    "corrected_mean_config": "identity-a0-b1",
                }
            ),
            HistoricalCellKey(
                **{
                    **primary.__dict__,
                    "cost_scenario": "fixed-1-usd",
                }
            ),
        )

        self.assertEqual(classify_analysis_tier(primary, protocol), "confirmatory")
        self.assertEqual(
            classify_analysis_tier(architecture, protocol), "secondary"
        )
        self.assertEqual(classify_analysis_tier(collapse, protocol), "secondary")
        self.assertTrue(
            all(
                classify_analysis_tier(variant, protocol) == "robustness"
                for variant in variants
            )
        )

    def test_monthly_projection_changes_analysis_status_not_episode_bytes(
        self,
    ) -> None:
        execution = _execution()
        runner_input = VersionedInput.from_mapping(
            {
                "schema_version": "smartdca-versioned-input/1",
                "input_id": "fixture-confirmatory-input",
                "version": "1",
                "kind": "historical",
                "confirmatory": True,
                "source_receipts": [],
                "episodes": [
                    {
                        "episode_id": "fixture-12m",
                        "family": "historical-recurring-investment",
                        "dataset_id": "spy-adjusted-daily",
                        "horizon_months": 12,
                        "observations": [
                            {
                                "date": "2020-01-02",
                                "price": "100",
                                "deposit": "1000",
                            }
                        ],
                        "evaluation_date": "2021-01-01",
                        "evaluation_price": "110",
                        "historical_mapping": {
                            "nominal_start": "2020-01-01"
                        },
                    }
                ],
            }
        )
        attempt = {
            "episode_id": "fixture-12m",
            "dataset_id": "spy-adjusted-daily",
            "horizon_months": 12,
            "status": "included",
            "exclusion_reason": None,
        }
        accepted = AcceptedHistoricalPreparation(
            manifest={},
            manifest_sha256="a" * 64,
            runner_input=runner_input,
            reconciliation={
                "observation_count": 1,
                "included_episode_count": 1,
                "excluded_episode_count": 0,
                "exclusion_reasons": {},
            },
            episode_attempts=(attempt,),
            attempt_count=1,
        )

        attempts, projected, reconciliation = build_monthly_robustness_input(
            execution, accepted
        )

        source_episode = runner_input.as_mapping()["episodes"][0]
        projected_document = projected.as_mapping()
        projected_episode = projected_document["episodes"][0]
        self.assertFalse(projected_document["confirmatory"])
        self.assertEqual(
            projected_episode["observations"], source_episode["observations"]
        )
        self.assertEqual(
            projected_episode["evaluation_price"],
            source_episode["evaluation_price"],
        )
        self.assertEqual(attempts[0]["design_tier"], "primary")
        self.assertEqual(reconciliation["runner_input_episode_count"], 1)

    def test_small_quarterly_run_emits_only_robustness_cells(self) -> None:
        execution = _execution()
        attempt = _included_quarterly_attempt()
        inputs = VersionedInput.from_mapping(
            {
                "schema_version": "smartdca-versioned-input/1",
                "input_id": "quarterly-robustness-fixture",
                "version": "1",
                "kind": "historical",
                "confirmatory": False,
                "episodes": [_runner_episode(attempt, "fixture-source")],
            }
        )
        config = _runner_projection(
            execution,
            slice_id="quarterly-fixture",
            coverage=execution.document["quarterly_horizon_extension"][
                "coverage"
            ],
            episode_design=_quarterly_episode_design(execution),
        )
        with tempfile.TemporaryDirectory() as temporary:
            evidence = _execute_slice(
                directory=Path(temporary),
                name="quarterly",
                schedule_id="robustness-quarterly-horizons",
                design_tier="robustness",
                execution=execution,
                config=config,
                inputs=inputs,
                attempts=(attempt,),
                preparation_reconciliation={"runner_input_episode_count": 1},
            )

            self.assertEqual(evidence.ledger_count, 81)
            self.assertEqual(evidence.comparison_count, 81)
            self.assertEqual(evidence.aggregates["group_count"], 81)
            self.assertEqual(
                {
                    group["analysis_tier"]
                    for group in evidence.aggregates["groups"]
                },
                {"robustness"},
            )
            self.assertEqual(
                {
                    group["uncertainty_status"]
                    for group in evidence.aggregates["groups"]
                },
                {"not-run-robustness"},
            )
            packaged_manifest = json.loads(
                (
                    Path(temporary)
                    / "quarterly-runner"
                    / "manifest.json"
                ).read_text(encoding="utf-8")
            )
            self.assertIn(
                "ledgers.jsonl.gz",
                {
                    artifact["path"]
                    for artifact in packaged_manifest["artifacts"]
                },
            )


if __name__ == "__main__":
    unittest.main()
