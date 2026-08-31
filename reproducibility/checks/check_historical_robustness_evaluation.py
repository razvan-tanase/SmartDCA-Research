"""Public-contract checks for registered historical robustness execution."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
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
