"""Public-contract checks for the historical data and episode seam."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from reproducibility.empirical import (
    ExperimentValidationError,
    StudyConfig,
    load_study_config,
    run_experiment,
)
from reproducibility.historical_data import (
    AlphaVantageProvider,
    HistoricalSourceSet,
    ProviderResponse,
    acquire_historical_sources,
    load_historical_source_set,
    prepare_historical_input,
    run_historical_validation,
)


ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "experiments" / "protocols" / "safety-adaptivity-v1.json"
COMMITTED_SOURCE_SET = (
    ROOT / "experiments" / "inputs" / "historical-validation-sources-v1.json"
)
COMMITTED_RUN_ID = (
    "smartdca-historical-validation-v1-"
    "dccb2033929ec8ccb4e90245582fe3b73126c57d16c5bbb0355a47329cca132a"
)
COMMITTED_RUN = ROOT / "reports" / "experiments" / "runs" / COMMITTED_RUN_ID

SPY_CSV = b"""timestamp,open,high,low,close,adjusted_close,volume,dividend_amount,split_coefficient
2021-02-01,281,282,279,280,140,10,0,2.0
2021-01-04,131,132,129,130,130,10,0,1.0
2020-12-31,126,127,124,125,125,10,0,1.0
2020-12-01,121,122,119,120,120,10,0,1.0
2020-11-02,111,112,109,110,110,10,0,1.0
2020-10-01,101,102,99,100,100,10,0,1.0
2020-09-01,91,92,89,90,90,10,0,1.0
2020-08-03,81,82,79,80,80,10,0,1.0
2020-07-01,71,72,69,70,70,10,0,1.0
2020-06-01,61,62,59,60,60,10,0,1.0
2020-05-01,51,52,49,50,50,10,0,1.0
2020-04-01,41,42,39,40,40,10,0,1.0
2020-03-02,31,32,29,30,30,10,0,1.0
2020-02-03,21,22,19,20,20,10,0,1.0
2020-01-02,11,12,9,10,10,10,0,1.0
"""

BTC_CSV = b"""timestamp,open,high,low,close,volume
2021-02-01,141,142,139,140,10
2021-01-01,131,132,129,130,10
2020-12-01,121,122,119,120,10
2020-11-01,111,112,109,110,10
2020-10-01,101,102,99,100,10
2020-09-01,91,92,89,90,10
2020-08-01,81,82,79,80,10
2020-07-01,71,72,69,70,10
2020-06-01,61,62,59,60,10
2020-05-01,51,52,49,50,10
2020-04-01,41,42,39,40,10
2020-03-01,31,32,29,30,10
2020-02-01,21,22,19,20,10
2020-01-01,11,12,9,10,10
"""


def _source_set(
    spy_sha256: str = "ef89a54abb12a7c074bf8d6fdc4ee0ce9dce0f1bedcabf6bccc3d4d0944a0df4",
    btc_sha256: str = "9b0342e9c39a0be17ac2ae7ff61485541a4eb3422b8f48377cd0a815bfefcd74",
) -> HistoricalSourceSet:
    return HistoricalSourceSet.from_mapping(
        {
            "schema_version": "smartdca-historical-source-set/1",
            "source_set_id": "historical-seam-test",
            "version": "1",
            "mode": "validation",
            "confirmatory": False,
            "purpose": "Hand-authored non-confirmatory contract fixture.",
            "sources": [
                {
                    "dataset_id": "spy-adjusted-daily",
                    "adapter": "hand-authored-fixture",
                    "path": "spy.csv",
                    "retrieved_at_utc": "2026-08-30T00:00:00Z",
                    "http_status": 200,
                    "content_type": "text/csv",
                    "expected_sha256": spy_sha256,
                    "redistribution_decision": "synthetic-fixture-approved-for-repository",
                },
                {
                    "dataset_id": "btc-usd-daily",
                    "adapter": "hand-authored-fixture",
                    "path": "btc.csv",
                    "retrieved_at_utc": "2026-08-30T00:00:00Z",
                    "http_status": 200,
                    "content_type": "text/csv",
                    "expected_sha256": btc_sha256,
                    "redistribution_decision": "synthetic-fixture-approved-for-repository",
                },
            ],
            "episode_scope": {
                "horizons_months": [12],
                "nominal_start_min": "2020-01-01",
                "nominal_start_max": "2020-03-01",
                "validation_episode_starts": {
                    "spy-adjusted-daily": "2020-01-01",
                    "btc-usd-daily": "2020-01-01",
                },
            },
        }
    )


class HistoricalDataEpisodeSeamTest(unittest.TestCase):
    def test_live_adapter_builds_the_locked_request_and_returns_untouched_bytes(self) -> None:
        captured = {}

        class Response:
            status = 200
            headers = {"Content-Type": "text/csv; charset=utf-8"}

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                return SPY_CSV

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["timeout"] = timeout
            return Response()

        dataset = load_study_config(PROTOCOL).as_mapping()["historical_datasets"][0]
        response = AlphaVantageProvider("secret-key", opener=opener).retrieve(dataset)

        query = parse_qs(urlparse(captured["url"]).query)
        self.assertEqual(
            query,
            {
                "function": ["TIME_SERIES_DAILY_ADJUSTED"],
                "symbol": ["SPY"],
                "outputsize": ["full"],
                "datatype": ["csv"],
                "apikey": ["secret-key"],
            },
        )
        self.assertEqual(captured["timeout"], 60)
        self.assertEqual(response, ProviderResponse(SPY_CSV, 200, "text/csv"))

    def test_acquisition_persists_exact_responses_and_credential_free_receipt(self) -> None:
        class FixtureProvider:
            def __init__(self) -> None:
                self.dataset_ids: list[str] = []
                self.api_key = "must-not-appear"

            def retrieve(self, dataset):
                self.dataset_ids.append(dataset["dataset_id"])
                body = (
                    SPY_CSV
                    if dataset["dataset_id"] == "spy-adjusted-daily"
                    else BTC_CSV
                )
                return ProviderResponse(body, 200, "text/csv")

        provider = FixtureProvider()
        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            acquired = acquire_historical_sources(
                load_study_config(PROTOCOL),
                source_root,
                provider,
                "2026-08-30T12:34:56Z",
            )
            source_set_path = source_root / "historical-source-set.json"
            receipt_bytes = source_set_path.read_bytes()
            saved_sources = acquired.as_mapping()["sources"]
            saved_payloads = {
                source["dataset_id"]: (source_root / source["path"]).read_bytes()
                for source in saved_sources
            }

        self.assertEqual(
            provider.dataset_ids,
            ["spy-adjusted-daily", "btc-usd-daily"],
        )
        self.assertEqual(saved_payloads["spy-adjusted-daily"], SPY_CSV)
        self.assertEqual(saved_payloads["btc-usd-daily"], BTC_CSV)
        self.assertNotIn(b"must-not-appear", receipt_bytes)
        self.assertEqual(
            {source["expected_sha256"] for source in saved_sources},
            {
                "ef89a54abb12a7c074bf8d6fdc4ee0ce9dce0f1bedcabf6bccc3d4d0944a0df4",
                "9b0342e9c39a0be17ac2ae7ff61485541a4eb3422b8f48377cd0a815bfefcd74",
            },
        )

    def test_exact_source_bytes_produce_auditable_declared_price_series(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            (source_root / "spy.csv").write_bytes(SPY_CSV)
            (source_root / "btc.csv").write_bytes(BTC_CSV)

            prepared = prepare_historical_input(
                load_study_config(PROTOCOL), _source_set(), source_root
            )

        receipts = {row["dataset_id"]: row for row in prepared.source_receipts}
        self.assertEqual(
            receipts["spy-adjusted-daily"]["sha256"],
            "ef89a54abb12a7c074bf8d6fdc4ee0ce9dce0f1bedcabf6bccc3d4d0944a0df4",
        )
        self.assertEqual(
            receipts["btc-usd-daily"]["sha256"],
            "9b0342e9c39a0be17ac2ae7ff61485541a4eb3422b8f48377cd0a815bfefcd74",
        )
        self.assertEqual(
            receipts["spy-adjusted-daily"]["schema"]["selected_price_column"],
            "adjusted_close",
        )
        self.assertEqual(
            receipts["btc-usd-daily"]["schema"]["selected_price_column"],
            "close",
        )
        spy_rows = {
            row["observation_date"]: row["price"]
            for row in prepared.normalized_datasets["spy-adjusted-daily"]
        }
        self.assertEqual(spy_rows["2021-02-01"], "140")

    def test_receipts_join_frozen_semantics_to_the_redistribution_decision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            (source_root / "spy.csv").write_bytes(SPY_CSV)
            (source_root / "btc.csv").write_bytes(BTC_CSV)
            prepared = prepare_historical_input(
                load_study_config(PROTOCOL), _source_set(), source_root
            )

        receipts = {row["dataset_id"]: row for row in prepared.source_receipts}
        self.assertEqual(
            receipts["spy-adjusted-daily"]["declared_semantics"],
            {
                "asset": "SPDR S&P 500 ETF Trust as an investable S&P 500 proxy",
                "currency": "USD",
                "price_field": "adjusted_close",
                "timezone": "America/New_York",
                "adjustment": "provider adjusted close incorporating historical split and dividend events",
                "eligible_start": "1993-02-01",
                "data_cutoff": "2025-12-31",
            },
        )
        self.assertEqual(
            receipts["btc-usd-daily"]["series"], "BTC/USD"
        )
        self.assertEqual(
            receipts["btc-usd-daily"]["redistribution_decision"],
            "synthetic-fixture-approved-for-repository",
        )
        self.assertEqual(
            receipts["btc-usd-daily"]["documentation_url"],
            "https://www.alphavantage.co/documentation/#currency-daily",
        )
        self.assertIn("persist its exact response body", receipts["btc-usd-daily"]["retrieval_rule"])
        self.assertEqual(receipts["spy-adjusted-daily"]["row_count"], 15)
        self.assertEqual(
            receipts["spy-adjusted-daily"]["timezone_semantics"],
            {
                "provider_timezone_metadata": "not-present-in-daily-csv",
                "normalization_timezone": "America/New_York",
                "normalized_observation": "calendar-date-label-only",
                "intraday_timestamp_invented": False,
            },
        )

    def test_rolling_episodes_expose_calendar_mapping_and_reconcile_exclusions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            (source_root / "spy.csv").write_bytes(SPY_CSV)
            (source_root / "btc.csv").write_bytes(BTC_CSV)

            prepared = prepare_historical_input(
                load_study_config(PROTOCOL), _source_set(), source_root
            )

        attempts = {row["episode_id"]: row for row in prepared.episode_attempts}
        spy_january = attempts["spy-adjusted-daily-2020-01-01-12m"]
        self.assertEqual(spy_january["status"], "included")
        self.assertEqual(
            spy_january["deposit_schedule"][0],
            {
                "nominal_date": "2020-01-01",
                "purchase_date": "2020-01-02",
                "mapping_lag_days": 1,
                "source_row": 16,
                "price": "10",
                "deposit": "1000",
            },
        )
        self.assertEqual(spy_january["horizon_date"], "2021-01-01")
        self.assertEqual(spy_january["evaluation_date"], "2020-12-31")
        btc_january = attempts["btc-usd-daily-2020-01-01-12m"]
        self.assertEqual(
            btc_january["deposit_schedule"][1]["purchase_date"], "2020-02-01"
        )
        spy_february = attempts["spy-adjusted-daily-2020-02-01-12m"]
        january_dates = {
            row["purchase_date"] for row in spy_january["deposit_schedule"]
        }
        february_dates = {
            row["purchase_date"] for row in spy_february["deposit_schedule"]
        }
        self.assertEqual(len(january_dates & february_dates), 11)
        self.assertEqual(
            attempts["spy-adjusted-daily-2020-03-01-12m"]["exclusion_reason"],
            "unavailable_mapped_evaluation_date",
        )
        self.assertEqual(
            prepared.reconciliation,
            {
                "dataset_count": 2,
                "observation_count": 29,
                "attempted_episode_count": 6,
                "included_episode_count": 4,
                "excluded_episode_count": 2,
                "exclusion_reasons": {"unavailable_mapped_evaluation_date": 2},
                "validation_episode_count": 2,
            },
        )
        runner_input = prepared.versioned_input.as_mapping()
        self.assertFalse(runner_input["confirmatory"])
        self.assertEqual(len(runner_input["episodes"]), 2)

    def test_changed_source_bytes_are_rejected_before_episode_construction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            (source_root / "spy.csv").write_bytes(SPY_CSV + b"\n")
            (source_root / "btc.csv").write_bytes(BTC_CSV)

            with self.assertRaises(ExperimentValidationError) as caught:
                prepare_historical_input(
                    load_study_config(PROTOCOL), _source_set(), source_root
                )

        self.assertEqual(caught.exception.code, "content_fingerprint_mismatch")
        self.assertEqual(
            caught.exception.field,
            "source_set.sources.spy-adjusted-daily.expected_sha256",
        )

    def test_source_set_mode_and_confirmatory_label_must_agree(self) -> None:
        source_mapping = _source_set().as_mapping()
        source_mapping["confirmatory"] = True

        with self.assertRaises(ExperimentValidationError) as caught:
            HistoricalSourceSet.from_mapping(source_mapping)

        self.assertEqual(caught.exception.code, "inconsistent_analysis_tier")

    def test_http_200_provider_error_envelope_is_not_parsed_as_market_data(self) -> None:
        error_payload = b'{"Note":"request frequency limit reached"}\n'
        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            (source_root / "spy.csv").write_bytes(error_payload)
            (source_root / "btc.csv").write_bytes(BTC_CSV)

            with self.assertRaises(ExperimentValidationError) as caught:
                prepare_historical_input(
                    load_study_config(PROTOCOL),
                    _source_set(
                        hashlib.sha256(error_payload).hexdigest(),
                        hashlib.sha256(BTC_CSV).hexdigest(),
                    ),
                    source_root,
                )

        self.assertEqual(caught.exception.code, "provider_error_payload")

    def test_adjusted_series_without_event_schema_is_rejected(self) -> None:
        incomplete_spy = SPY_CSV.replace(b",split_coefficient\n", b"\n", 1)
        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            (source_root / "spy.csv").write_bytes(incomplete_spy)
            (source_root / "btc.csv").write_bytes(BTC_CSV)
            with self.assertRaises(ExperimentValidationError) as caught:
                prepare_historical_input(
                    load_study_config(PROTOCOL),
                    _source_set(
                        hashlib.sha256(incomplete_spy).hexdigest(),
                        hashlib.sha256(BTC_CSV).hexdigest(),
                    ),
                    source_root,
                )

        self.assertEqual(caught.exception.code, "series_semantics_mismatch")
        self.assertIn("split_coefficient", str(caught.exception))

    def test_missing_purchase_is_retained_with_observed_endpoint_details(self) -> None:
        missing_btc_endpoint = BTC_CSV.replace(
            b"2021-02-01,141,142,139,140,10\n", b""
        )
        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            (source_root / "spy.csv").write_bytes(SPY_CSV)
            (source_root / "btc.csv").write_bytes(missing_btc_endpoint)
            prepared = prepare_historical_input(
                load_study_config(PROTOCOL),
                _source_set(
                    hashlib.sha256(SPY_CSV).hexdigest(),
                    hashlib.sha256(missing_btc_endpoint).hexdigest(),
                ),
                source_root,
            )

        attempt = next(
            row
            for row in prepared.episode_attempts
            if row["episode_id"] == "btc-usd-daily-2020-03-01-12m"
        )
        self.assertEqual(attempt["exclusion_reason"], "unavailable_mapped_purchase_date")
        self.assertEqual(
            attempt["exclusion_details"],
            {
                "mapping": "first-observation-on-or-after",
                "nominal_date": "2021-02-01",
                "tolerance_days": 1,
                "previous_observation_date": "2021-01-01",
                "next_observation_date": None,
            },
        )
        self.assertEqual(
            prepared.reconciliation["exclusion_reasons"],
            {
                "unavailable_mapped_evaluation_date": 2,
                "unavailable_mapped_purchase_date": 1,
            },
        )

    def test_future_rows_reidentify_input_without_changing_earlier_decisions(self) -> None:
        future_spy = SPY_CSV + b"2022-01-03,301,302,299,300,300,10,0,1.0\n"
        future_btc = BTC_CSV + b"2022-01-01,301,302,299,300,10\n"
        config = load_study_config(PROTOCOL)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base_sources = root / "base"
            base_sources.mkdir()
            (base_sources / "spy.csv").write_bytes(SPY_CSV)
            (base_sources / "btc.csv").write_bytes(BTC_CSV)
            base = prepare_historical_input(config, _source_set(), base_sources)

            future_sources = root / "future"
            future_sources.mkdir()
            (future_sources / "spy.csv").write_bytes(future_spy)
            (future_sources / "btc.csv").write_bytes(future_btc)
            extended = prepare_historical_input(
                config,
                _source_set(
                    hashlib.sha256(future_spy).hexdigest(),
                    hashlib.sha256(future_btc).hexdigest(),
                ),
                future_sources,
            )

            base_run = run_experiment(config, base.versioned_input, root / "base-run")
            extended_run = run_experiment(
                config, extended.versioned_input, root / "future-run"
            )

        self.assertNotEqual(base.versioned_input.sha256, extended.versioned_input.sha256)
        base_steps = [ledger["steps"] for ledger in base_run.ledgers]
        extended_steps = [ledger["steps"] for ledger in extended_run.ledgers]
        self.assertEqual(base_steps, extended_steps)

    def test_nonconfirmatory_slice_emits_a_complete_labeled_historical_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "spy.csv").write_bytes(SPY_CSV)
            (root / "btc.csv").write_bytes(BTC_CSV)

            bundle = run_historical_validation(
                load_study_config(PROTOCOL), _source_set(), root, root / "outputs"
            )

            self.assertEqual(
                {path.name for path in bundle.output_directory.iterdir()},
                {
                    "episode-attempts.jsonl",
                    "manifest.json",
                    "normalized-datasets.json",
                    "reconciliation.json",
                    "runner",
                    "runner-input.json",
                    "source-receipts.json",
                    "validation.json",
                },
            )
            self.assertEqual(
                {path.name for path in (bundle.output_directory / "runner").iterdir()},
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

        self.assertTrue(bundle.run_id.startswith("smartdca-historical-validation-v1-"))
        self.assertEqual(
            {ledger["policy"] for ledger in bundle.runner.ledgers},
            {"dca", "neutral_guarded", "corrected_guarded"},
        )
        self.assertEqual(bundle.runner.manifest["inputs"][0]["kind"], "historical")
        self.assertEqual(bundle.validation["status"], "passed")
        self.assertEqual(
            bundle.validation["evidence_tier"],
            "non-confirmatory-infrastructure-validation",
        )
        self.assertEqual(
            bundle.validation["confirmatory_aggregate_outcomes"],
            "unopened-and-unreported",
        )
        self.assertEqual(bundle.manifest["source_set_sha256"], _source_set().sha256)
        self.assertEqual(len(bundle.runner.ledgers), 72)
        self.assertIn(
            "runner/manifest.json",
            {artifact["path"] for artifact in bundle.manifest["artifacts"]},
        )

    def test_confirmatory_sources_build_the_full_grid_without_running_policies(self) -> None:
        config_mapping = load_study_config(PROTOCOL).as_mapping()
        config_mapping["episode_design"]["horizons_months"] = [12]
        for dataset in config_mapping["historical_datasets"]:
            dataset["eligible_start"] = "2020-01-01"
            dataset["data_cutoff"] = "2021-02-01"
        config = StudyConfig.from_mapping(config_mapping)
        source_mapping = _source_set().as_mapping()
        source_mapping["mode"] = "confirmatory"
        source_mapping["confirmatory"] = True
        source_mapping["episode_scope"] = {"rule": "full-preregistered-grid"}
        sources = HistoricalSourceSet.from_mapping(source_mapping)

        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            (source_root / "spy.csv").write_bytes(SPY_CSV)
            (source_root / "btc.csv").write_bytes(BTC_CSV)
            prepared = prepare_historical_input(config, sources, source_root)

        self.assertTrue(prepared.versioned_input.as_mapping()["confirmatory"])
        self.assertEqual(prepared.reconciliation["attempted_episode_count"], 4)
        self.assertEqual(prepared.reconciliation["included_episode_count"], 4)
        self.assertEqual(len(prepared.versioned_input.as_mapping()["episodes"]), 4)

    def test_confirmatory_preparation_rejects_incomplete_dataset_coverage(self) -> None:
        config_mapping = load_study_config(PROTOCOL).as_mapping()
        config_mapping["episode_design"]["horizons_months"] = [12]
        for dataset in config_mapping["historical_datasets"]:
            dataset["eligible_start"] = "2020-01-01"
            dataset["data_cutoff"] = "2021-02-01"
        config = StudyConfig.from_mapping(config_mapping)
        source_mapping = _source_set().as_mapping()
        source_mapping["mode"] = "confirmatory"
        source_mapping["confirmatory"] = True
        source_mapping["episode_scope"] = {"rule": "full-preregistered-grid"}
        incomplete_btc = BTC_CSV.replace(
            b"2021-02-01,141,142,139,140,10\n", b""
        )
        source_mapping["sources"][1]["expected_sha256"] = hashlib.sha256(
            incomplete_btc
        ).hexdigest()
        sources = HistoricalSourceSet.from_mapping(source_mapping)

        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            (source_root / "spy.csv").write_bytes(SPY_CSV)
            (source_root / "btc.csv").write_bytes(incomplete_btc)
            with self.assertRaises(ExperimentValidationError) as caught:
                prepare_historical_input(config, sources, source_root)

        self.assertEqual(caught.exception.code, "incomplete_dataset_coverage")
        self.assertEqual(caught.exception.field, "source_set.sources.btc-usd-daily")

    def test_command_line_replays_the_validation_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "spy.csv").write_bytes(SPY_CSV)
            (root / "btc.csv").write_bytes(BTC_CSV)
            source_set_path = root / "source-set.json"
            source_set_path.write_text(
                _source_set().canonical_document + "\n", encoding="utf-8"
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "reproducibility.historical_data",
                    "validate",
                    "--config",
                    str(PROTOCOL),
                    "--source-set",
                    str(source_set_path),
                    "--source-root",
                    str(root),
                    "--output-root",
                    str(root / "outputs"),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        receipt = json.loads(completed.stdout)
        self.assertEqual(receipt["status"], "completed")
        self.assertTrue(
            receipt["run_id"].startswith("smartdca-historical-validation-v1-")
        )

    def test_committed_validation_bundle_replays_byte_for_byte(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            replay = run_historical_validation(
                load_study_config(PROTOCOL),
                load_historical_source_set(COMMITTED_SOURCE_SET),
                ROOT,
                Path(directory),
            )

            self.assertEqual(replay.run_id, COMMITTED_RUN_ID)
            committed_paths = {
                path.relative_to(COMMITTED_RUN)
                for path in COMMITTED_RUN.rglob("*")
                if path.is_file()
            }
            replay_paths = {
                path.relative_to(replay.output_directory)
                for path in replay.output_directory.rglob("*")
                if path.is_file()
            }
            self.assertEqual(replay_paths, committed_paths)
            for relative_path in sorted(committed_paths):
                self.assertEqual(
                    (replay.output_directory / relative_path).read_bytes(),
                    (COMMITTED_RUN / relative_path).read_bytes(),
                    str(relative_path),
                )

    def test_acquisition_cli_reports_a_missing_credential_without_network_access(self) -> None:
        environment = dict(os.environ)
        environment.pop("ALPHAVANTAGE_API_KEY", None)
        with tempfile.TemporaryDirectory() as directory:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "reproducibility.historical_data",
                    "acquire",
                    "--config",
                    str(PROTOCOL),
                    "--source-root",
                    directory,
                ],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(completed.returncode, 2)
        rejection = json.loads(completed.stderr)
        self.assertEqual(rejection["code"], "missing_credential")
        self.assertEqual(rejection["field"], "ALPHAVANTAGE_API_KEY")

    def test_prepare_cli_writes_confirmatory_handoff_without_policy_outputs(self) -> None:
        config_mapping = load_study_config(PROTOCOL).as_mapping()
        config_mapping["episode_design"]["horizons_months"] = [12]
        for dataset in config_mapping["historical_datasets"]:
            dataset["eligible_start"] = "2020-01-01"
            dataset["data_cutoff"] = "2021-02-01"
        source_mapping = _source_set().as_mapping()
        source_mapping["mode"] = "confirmatory"
        source_mapping["confirmatory"] = True
        source_mapping["episode_scope"] = {"rule": "full-preregistered-grid"}

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "spy.csv").write_bytes(SPY_CSV)
            (root / "btc.csv").write_bytes(BTC_CSV)
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config_mapping), encoding="utf-8")
            source_set_path = root / "source-set.json"
            source_set_path.write_text(json.dumps(source_mapping), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "reproducibility.historical_data",
                    "prepare",
                    "--config",
                    str(config_path),
                    "--source-set",
                    str(source_set_path),
                    "--source-root",
                    str(root),
                    "--output-root",
                    str(root / "outputs"),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            receipt = json.loads(completed.stdout)
            output_directory = Path(receipt["output_directory"])
            output_names = {path.name for path in output_directory.iterdir()}

        self.assertEqual(
            output_names,
            {
                "episode-attempts.jsonl",
                "manifest.json",
                "normalized-datasets.json",
                "reconciliation.json",
                "runner-input.json",
                "source-receipts.json",
                "validation.json",
            },
        )
        self.assertEqual(receipt["policy_execution"], "not-run")


if __name__ == "__main__":
    unittest.main()
