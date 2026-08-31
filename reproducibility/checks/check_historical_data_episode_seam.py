"""Public-contract checks for the historical data and episode seam."""

from __future__ import annotations

import contextlib
import hashlib
import io
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
    YFinanceProvider,
    acquire_historical_sources,
    load_historical_source_set,
    main as historical_main,
    prepare_historical_input,
    run_historical_validation,
    write_historical_preparation,
)


ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "experiments" / "protocols" / "safety-adaptivity-v1.json"
YAHOO_PROTOCOL = (
    ROOT / "experiments" / "protocols" / "safety-adaptivity-yahoo-v2.json"
)
YAHOO_SOURCE_RECEIPT = (
    ROOT / "experiments" / "inputs" / "historical-yahoo-receipts-v2.json"
)
YAHOO_NORMALIZATION_RECEIPTS = (
    ROOT
    / "experiments"
    / "inputs"
    / "historical-yahoo-normalization-receipts-v2.json"
)
YAHOO_PREPARATION_VALIDATION = (
    ROOT
    / "experiments"
    / "inputs"
    / "historical-yahoo-preparation-validation-v2.json"
)
YAHOO_PREPARATION_MANIFEST = (
    ROOT
    / "experiments"
    / "inputs"
    / "historical-yahoo-preparation-manifest-v3.json"
)
COMMITTED_SOURCE_SET = (
    ROOT / "experiments" / "inputs" / "historical-validation-sources-v1.json"
)
COMMITTED_RUN_ID = (
    "smartdca-historical-validation-v1-"
    "9523135380007cb4597b991600acb7d5b0c244e955fb17b36d244d6158155a10"
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


class _FixtureProvider:
    def __init__(self, spy: bytes = SPY_CSV, btc: bytes = BTC_CSV) -> None:
        self._responses = {
            "spy-adjusted-daily": spy,
            "btc-usd-daily": btc,
        }

    def retrieve(self, dataset):
        return ProviderResponse(self._responses[dataset["dataset_id"]], 200, "text/csv")


class _YahooFixtureProvider:
    def retrieve(self, dataset):
        body = SPY_CSV if dataset["dataset_id"] == "spy-adjusted-daily" else BTC_CSV
        return ProviderResponse(
            body,
            None,
            "text/csv",
            {
                "adapter": "yfinance-history",
                "adapter_version": "1.7.0",
                "client_versions": {
                    "yfinance": "1.7.0",
                    "pandas": "3.0.5",
                    "numpy": "2.5.2",
                    "curl_cffi": "0.16.2",
                },
                "source_timezone": dataset["timezone"],
                "source_currency": dataset["currency"],
                "provider_http_metadata_exposed": False,
                "export_format": "smartdca-canonical-csv/1",
                "cache_policy": "acquisition-source-root-local",
                "client_source_commit": "3d9d2f0cacb662bff689874cd6113bae3a30a885",
                "dependency_lock_sha256": "3a53181ceea7b7b79a80f3005c3b2bd0dbdefab25152ff07826ee1a2ab438a76",
                "http_backend": "curl_cffi",
            },
        )


def _acquire_confirmatory_sources(
    config: StudyConfig,
    source_root: Path,
    *,
    spy: bytes = SPY_CSV,
    btc: bytes = BTC_CSV,
) -> HistoricalSourceSet:
    return acquire_historical_sources(
        config,
        source_root,
        _FixtureProvider(spy, btc),
        "2026-08-30T00:00:00Z",
    )


class HistoricalDataEpisodeSeamTest(unittest.TestCase):
    def test_yahoo_replacement_is_a_new_locked_protocol_before_data_access(self) -> None:
        original = load_study_config(PROTOCOL).as_mapping()
        replacement = load_study_config(YAHOO_PROTOCOL).as_mapping()

        self.assertEqual(replacement["protocol_id"], "safety-adaptivity-yahoo-v2")
        self.assertEqual(replacement["protocol_version"], 2)
        self.assertEqual(replacement["supersedes_protocol_id"], "safety-adaptivity-v1")
        self.assertFalse(replacement["confirmatory_outcomes_accessed"])
        self.assertEqual(
            {dataset["provider"] for dataset in replacement["historical_datasets"]},
            {"Yahoo Finance"},
        )
        self.assertEqual(
            {
                dataset["dataset_id"]: dataset["request_parameters"]
                for dataset in replacement["historical_datasets"]
            },
            {
                "spy-adjusted-daily": {
                    "symbol": "SPY",
                    "start": "1993-02-01",
                    "end": "2026-01-01",
                    "interval": "1d",
                    "auto_adjust": False,
                    "actions": True,
                    "repair": False,
                    "keepna": True,
                    "prepost": False,
                    "rounding": False,
                    "timeout": 60,
                },
                "btc-usd-daily": {
                    "symbol": "BTC-USD",
                    "start": "2015-01-01",
                    "end": "2026-01-01",
                    "interval": "1d",
                    "auto_adjust": False,
                    "actions": True,
                    "repair": False,
                    "keepna": True,
                    "prepost": False,
                    "rounding": False,
                    "timeout": 60,
                },
            },
        )
        for field in (
            "episode_design",
            "coverage",
            "corrected_mean",
            "cost_scenarios",
            "hypotheses",
            "estimands",
            "multiplicity",
            "uncertainty",
            "analysis_tiers",
            "exclusions",
            "robustness_design",
            "canonical_run",
            "runner_contract",
        ):
            self.assertEqual(replacement[field], original[field], field)

    def test_yfinance_adapter_uses_locked_arguments_and_canonicalizes_its_export(self) -> None:
        captured = {}

        def history_loader(symbol, parameters, cache_directory):
            captured["symbol"] = symbol
            captured["parameters"] = parameters
            captured["cache_directory"] = cache_directory
            return {
                "source_timezone": "America/New_York",
                "source_currency": "USD",
                "client_versions": {
                    "yfinance": "1.7.0",
                    "pandas": "3.0.5",
                    "numpy": "2.5.2",
                    "curl_cffi": "0.16.2",
                },
                "rows": [
                    {
                        "timestamp": "2020-01-02",
                        "Open": "11.25",
                        "High": "12.5",
                        "Low": "9",
                        "Close": "10",
                        "Adj Close": "9.75",
                        "Volume": "100",
                        "Dividends": "0.5",
                        "Stock Splits": "0",
                        "Capital Gains": "0.25",
                    }
                ],
            }

        dataset = load_study_config(YAHOO_PROTOCOL).as_mapping()[
            "historical_datasets"
        ][0]
        cache_directory = Path("ignored-yfinance-cache")
        response = YFinanceProvider(
            cache_directory=cache_directory,
            authorization="true",
            history_loader=history_loader,
        ).retrieve(dataset)

        self.assertEqual(captured["symbol"], "SPY")
        self.assertEqual(captured["cache_directory"], cache_directory)
        self.assertEqual(
            captured["parameters"],
            {
                "start": "1993-02-01",
                "end": "2026-01-01",
                "interval": "1d",
                "auto_adjust": False,
                "actions": True,
                "repair": False,
                "keepna": True,
                "prepost": False,
                "rounding": False,
                "timeout": 60,
            },
        )
        self.assertEqual(
            response.body,
            b"timestamp,open,high,low,close,adjusted_close,volume,"
            b"dividend_amount,split_coefficient,capital_gains\n"
            b"2020-01-02,11.25,12.5,9,10,9.75,100,0.5,0,0.25\n",
        )
        self.assertIsNone(response.http_status)
        self.assertEqual(response.content_type, "text/csv")
        self.assertEqual(
            response.metadata,
            {
                "adapter": "yfinance-history",
                "adapter_version": "1.7.0",
                "client_versions": {
                    "yfinance": "1.7.0",
                    "pandas": "3.0.5",
                    "numpy": "2.5.2",
                    "curl_cffi": "0.16.2",
                },
                "source_timezone": "America/New_York",
                "source_currency": "USD",
                "provider_http_metadata_exposed": False,
                "export_format": "smartdca-canonical-csv/1",
                "cache_policy": "acquisition-source-root-local",
                "client_source_commit": "3d9d2f0cacb662bff689874cd6113bae3a30a885",
                "dependency_lock_sha256": "3a53181ceea7b7b79a80f3005c3b2bd0dbdefab25152ff07826ee1a2ab438a76",
                "http_backend": "curl_cffi",
            },
        )

    def test_yfinance_acquisition_is_protocol_bound_and_episode_ready(self) -> None:
        config_mapping = load_study_config(YAHOO_PROTOCOL).as_mapping()
        config_mapping["episode_design"]["horizons_months"] = [12]
        for dataset in config_mapping["historical_datasets"]:
            dataset["eligible_start"] = "2020-01-01"
            dataset["data_cutoff"] = "2021-02-01"
        config = StudyConfig.from_mapping(config_mapping)

        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            acquired = acquire_historical_sources(
                config,
                source_root,
                _YahooFixtureProvider(),
                "2026-08-31T10:00:00Z",
            )
            prepared = prepare_historical_input(config, acquired, source_root)

        source_mapping = acquired.as_mapping()
        self.assertEqual(
            source_mapping["acquisition"],
            {
                "adapter": "yfinance-history",
                "adapter_version": "1.7.0",
                "provider": "Yahoo Finance",
                "one_export_per_dataset": True,
                "credential_recorded": False,
                "authorization_attested": True,
                "provider_http_metadata_exposed": False,
            },
        )
        self.assertTrue(
            source_mapping["source_set_id"].startswith("yahoo-finance-historical-")
        )
        self.assertEqual(source_mapping["version"], "2")
        self.assertEqual(
            {
                source["redistribution_decision"]
                for source in source_mapping["sources"]
            },
            {
                "canonical-client-export-and-normalized-observations-"
                "access-controlled-outside-git; sanitized-receipts-only-"
                "without-written-permission"
            },
        )
        self.assertEqual(
            {source["adapter"] for source in source_mapping["sources"]},
            {"yfinance-history"},
        )
        self.assertEqual(
            {source["http_status"] for source in source_mapping["sources"]},
            {None},
        )
        receipts = {row["dataset_id"]: row for row in prepared.source_receipts}
        self.assertEqual(prepared.status, "accepted")
        self.assertEqual(receipts["spy-adjusted-daily"]["adapter_version"], "1.7.0")
        self.assertEqual(
            receipts["btc-usd-daily"]["source_timezone"], "UTC"
        )
        self.assertEqual(receipts["btc-usd-daily"]["source_currency"], "USD")
        self.assertEqual(
            receipts["btc-usd-daily"]["http_backend"], "curl_cffi"
        )
        self.assertFalse(
            receipts["spy-adjusted-daily"]["provider_http_metadata_exposed"]
        )

    def test_committed_yahoo_receipts_bind_input_without_exposing_outcomes(self) -> None:
        source_receipt = load_historical_source_set(YAHOO_SOURCE_RECEIPT)
        normalization = json.loads(
            YAHOO_NORMALIZATION_RECEIPTS.read_text(encoding="utf-8")
        )
        validation = json.loads(
            YAHOO_PREPARATION_VALIDATION.read_text(encoding="utf-8")
        )
        manifest = json.loads(
            YAHOO_PREPARATION_MANIFEST.read_text(encoding="utf-8")
        )

        self.assertEqual(
            source_receipt.sha256,
            "346676eb699d4e64cee7f687a04f207d6ab4daff92abae780719368d259f97f4",
        )
        self.assertEqual(
            source_receipt.as_mapping()["protocol_sha256"],
            load_study_config(YAHOO_PROTOCOL).sha256,
        )
        receipts = {
            row["dataset_id"]: row for row in normalization["receipts"]
        }
        self.assertEqual(
            {
                dataset_id: (
                    receipt["row_count"],
                    receipt["date_min"],
                    receipt["date_max"],
                    receipt["schema"]["selected_price_column"],
                )
                for dataset_id, receipt in receipts.items()
            },
            {
                "spy-adjusted-daily": (
                    8287,
                    "1993-02-01",
                    "2025-12-31",
                    "adjusted_close",
                ),
                "btc-usd-daily": (
                    4018,
                    "2015-01-01",
                    "2025-12-31",
                    "close",
                ),
            },
        )
        self.assertEqual(validation["policy_execution"], "not-run")
        self.assertEqual(validation["confirmatory_aggregate_outcomes"], "not-computed")
        self.assertEqual(
            validation["reconciliation"],
            {
                "accepted_dataset_count": 2,
                "attempted_episode_count": 1365,
                "dataset_count": 2,
                "dataset_failures": {},
                "excluded_episode_count": 0,
                "exclusion_reasons": {},
                "failed_dataset_count": 0,
                "included_episode_count": 1365,
                "input_status": "accepted",
                "observation_count": 12305,
                "runner_input_episode_count": 1365,
                "validation_episode_count": 0,
            },
        )
        self.assertEqual(
            manifest["run_id"],
            "smartdca-historical-input-v1-"
            "c4e1222c907ffcffe6fd237fd34d97987566a415e45903577cc507fffff12d0f",
        )
        self.assertEqual(
            manifest["runner_input_sha256"],
            "d49a5a6e0304a7da213082698990d46bec7f7cac2399533990f84a40183bec88",
        )
        for path in (
            YAHOO_SOURCE_RECEIPT,
            YAHOO_NORMALIZATION_RECEIPTS,
            YAHOO_PREPARATION_VALIDATION,
            YAHOO_PREPARATION_MANIFEST,
        ):
            retained = path.read_bytes()
            self.assertNotIn(b'"price":', retained)
            self.assertNotIn(b'"terminal_wealth":', retained)
            self.assertNotIn(b'"aggregates":', retained)

    def test_yfinance_adapter_requires_researcher_authorization_before_loading(self) -> None:
        with self.assertRaises(ExperimentValidationError) as caught:
            YFinanceProvider(
                Path("ignored-yfinance-cache"),
                authorization="",
            )

        self.assertEqual(caught.exception.code, "missing_authorization")
        self.assertEqual(
            caught.exception.field,
            "YAHOO_FINANCE_AUTOMATED_ACCESS_AUTHORIZED",
        )

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
                "accepted_dataset_count": 2,
                "failed_dataset_count": 0,
                "dataset_failures": {},
                "observation_count": 29,
                "attempted_episode_count": 6,
                "included_episode_count": 4,
                "excluded_episode_count": 2,
                "exclusion_reasons": {"unavailable_mapped_evaluation_date": 2},
                "runner_input_episode_count": 2,
                "validation_episode_count": 2,
                "input_status": "accepted",
            },
        )
        runner_input = prepared.versioned_input.as_mapping()
        self.assertFalse(runner_input["confirmatory"])
        self.assertEqual(len(runner_input["episodes"]), 2)

    def test_changed_source_bytes_reject_and_retain_every_episode_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            (source_root / "spy.csv").write_bytes(SPY_CSV + b"\n")
            (source_root / "btc.csv").write_bytes(BTC_CSV)

            prepared = prepare_historical_input(
                load_study_config(PROTOCOL), _source_set(), source_root
            )

        spy_receipt = next(
            row
            for row in prepared.source_receipts
            if row["dataset_id"] == "spy-adjusted-daily"
        )
        self.assertEqual(spy_receipt["rejection"]["code"], "content_fingerprint_mismatch")
        self.assertEqual(
            spy_receipt["rejection"]["field"],
            "source_set.sources.spy-adjusted-daily.expected_sha256",
        )
        self.assertEqual(
            [
                row["exclusion_reason"]
                for row in prepared.episode_attempts
                if row["dataset_id"] == "spy-adjusted-daily"
            ],
            ["content_fingerprint_mismatch"] * 3,
        )

    def test_source_set_mode_and_confirmatory_label_must_agree(self) -> None:
        source_mapping = _source_set().as_mapping()
        source_mapping["confirmatory"] = True

        with self.assertRaises(ExperimentValidationError) as caught:
            HistoricalSourceSet.from_mapping(source_mapping)

        self.assertEqual(caught.exception.code, "inconsistent_analysis_tier")

    def test_fixture_provenance_cannot_be_relabelled_confirmatory(self) -> None:
        source_mapping = _source_set().as_mapping()
        source_mapping["mode"] = "confirmatory"
        source_mapping["confirmatory"] = True
        source_mapping["episode_scope"] = {"rule": "full-preregistered-grid"}

        with self.assertRaises(ExperimentValidationError) as caught:
            HistoricalSourceSet.from_mapping(source_mapping)

        self.assertEqual(caught.exception.code, "unverified_confirmatory_provenance")

    def test_http_200_provider_error_envelope_is_not_parsed_as_market_data(self) -> None:
        error_payload = b'{"Note":"request frequency limit reached"}\n'
        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            (source_root / "spy.csv").write_bytes(error_payload)
            (source_root / "btc.csv").write_bytes(BTC_CSV)

            prepared = prepare_historical_input(
                load_study_config(PROTOCOL),
                _source_set(
                    hashlib.sha256(error_payload).hexdigest(),
                    hashlib.sha256(BTC_CSV).hexdigest(),
                ),
                source_root,
            )

        spy_receipt = next(
            row
            for row in prepared.source_receipts
            if row["dataset_id"] == "spy-adjusted-daily"
        )
        self.assertEqual(spy_receipt["rejection"]["code"], "provider_error_payload")

    def test_adjusted_series_without_event_schema_is_rejected(self) -> None:
        incomplete_spy = SPY_CSV.replace(b",split_coefficient\n", b"\n", 1)
        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            (source_root / "spy.csv").write_bytes(incomplete_spy)
            (source_root / "btc.csv").write_bytes(BTC_CSV)
            prepared = prepare_historical_input(
                load_study_config(PROTOCOL),
                _source_set(
                    hashlib.sha256(incomplete_spy).hexdigest(),
                    hashlib.sha256(BTC_CSV).hexdigest(),
                ),
                source_root,
            )

        spy_receipt = next(
            row
            for row in prepared.source_receipts
            if row["dataset_id"] == "spy-adjusted-daily"
        )
        self.assertEqual(spy_receipt["rejection"]["code"], "series_semantics_mismatch")
        self.assertIn("split_coefficient", spy_receipt["rejection"]["message"])

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

    def test_excluded_episode_retains_its_complete_nominal_deposit_schedule(self) -> None:
        missing_first_btc = BTC_CSV.replace(
            b"2020-01-01,11,12,9,10,10\n", b""
        )
        source_mapping = _source_set(
            hashlib.sha256(SPY_CSV).hexdigest(),
            hashlib.sha256(missing_first_btc).hexdigest(),
        ).as_mapping()
        source_mapping["episode_scope"]["validation_episode_starts"][
            "btc-usd-daily"
        ] = "2020-02-01"
        sources = HistoricalSourceSet.from_mapping(source_mapping)
        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            (source_root / "spy.csv").write_bytes(SPY_CSV)
            (source_root / "btc.csv").write_bytes(missing_first_btc)
            prepared = prepare_historical_input(
                load_study_config(PROTOCOL), sources, source_root
            )

        attempt = next(
            row
            for row in prepared.episode_attempts
            if row["episode_id"] == "btc-usd-daily-2020-01-01-12m"
        )
        self.assertEqual(attempt["exclusion_reason"], "unavailable_mapped_purchase_date")
        self.assertEqual(len(attempt["deposit_schedule"]), 12)
        self.assertIsNone(attempt["deposit_schedule"][0]["purchase_date"])
        self.assertEqual(
            attempt["deposit_schedule"][1]["purchase_date"], "2020-02-01"
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
        self.assertEqual(bundle.manifest["runtime"]["python"], "3.12")
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

        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            sources = _acquire_confirmatory_sources(config, source_root)
            prepared = prepare_historical_input(config, sources, source_root)

        self.assertTrue(prepared.versioned_input.as_mapping()["confirmatory"])
        self.assertEqual(prepared.reconciliation["attempted_episode_count"], 4)
        self.assertEqual(prepared.reconciliation["included_episode_count"], 4)
        self.assertEqual(prepared.reconciliation["runner_input_episode_count"], 4)
        self.assertEqual(prepared.reconciliation["validation_episode_count"], 0)
        self.assertEqual(len(prepared.versioned_input.as_mapping()["episodes"]), 4)

    def test_confirmatory_preparation_retains_incomplete_dataset_attempts(self) -> None:
        config_mapping = load_study_config(PROTOCOL).as_mapping()
        config_mapping["episode_design"]["horizons_months"] = [12]
        for dataset in config_mapping["historical_datasets"]:
            dataset["eligible_start"] = "2020-01-01"
            dataset["data_cutoff"] = "2021-02-01"
        config = StudyConfig.from_mapping(config_mapping)
        incomplete_btc = BTC_CSV.replace(
            b"2021-02-01,141,142,139,140,10\n", b""
        )

        with tempfile.TemporaryDirectory() as directory:
            source_root = Path(directory)
            sources = _acquire_confirmatory_sources(
                config, source_root, btc=incomplete_btc
            )
            prepared = prepare_historical_input(config, sources, source_root)

        self.assertEqual(prepared.status, "rejected")
        self.assertIsNone(prepared.versioned_input)
        btc_attempts = [
            row
            for row in prepared.episode_attempts
            if row["dataset_id"] == "btc-usd-daily"
        ]
        self.assertEqual(len(btc_attempts), 2)
        self.assertTrue(
            all(
                row["exclusion_reason"] == "incomplete_dataset_coverage"
                and len(row["deposit_schedule"]) == 12
                for row in btc_attempts
            )
        )
        btc_receipt = next(
            row
            for row in prepared.source_receipts
            if row["dataset_id"] == "btc-usd-daily"
        )
        self.assertEqual(btc_receipt["status"], "rejected")
        self.assertEqual(
            btc_receipt["rejection"]["code"], "incomplete_dataset_coverage"
        )
        self.assertEqual(prepared.reconciliation["failed_dataset_count"], 1)

    def test_failed_preparation_writes_immutable_attempt_and_rejection_artifacts(self) -> None:
        config_mapping = load_study_config(PROTOCOL).as_mapping()
        config_mapping["episode_design"]["horizons_months"] = [12]
        for dataset in config_mapping["historical_datasets"]:
            dataset["eligible_start"] = "2020-01-01"
            dataset["data_cutoff"] = "2021-02-01"
        config = StudyConfig.from_mapping(config_mapping)
        incomplete_btc = BTC_CSV.replace(
            b"2021-02-01,141,142,139,140,10\n", b""
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = _acquire_confirmatory_sources(
                config, root, btc=incomplete_btc
            )
            bundle = write_historical_preparation(
                config, sources, root, root / "outputs"
            )
            attempt_lines = (
                bundle.output_directory / "episode-attempts.jsonl"
            ).read_text(encoding="utf-8").splitlines()
            runner_input_exists = (
                bundle.output_directory / "runner-input.json"
            ).exists()

        self.assertEqual(bundle.validation["status"], "rejected")
        self.assertEqual(bundle.validation["policy_execution"], "not-run")
        self.assertEqual(len(attempt_lines), 4)
        self.assertFalse(runner_input_exists)
        self.assertEqual(bundle.manifest["runner_input_sha256"], None)

    def test_rejected_bundle_identity_binds_the_actual_rejected_bytes(self) -> None:
        config_mapping = load_study_config(PROTOCOL).as_mapping()
        config_mapping["episode_design"]["horizons_months"] = [12]
        for dataset in config_mapping["historical_datasets"]:
            dataset["eligible_start"] = "2020-01-01"
            dataset["data_cutoff"] = "2021-02-01"
        config = StudyConfig.from_mapping(config_mapping)
        run_ids = []
        actual_hashes = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for label, corrupt_body in (("a", b"corrupt-a"), ("b", b"corrupt-b")):
                source_root = root / label
                sources = _acquire_confirmatory_sources(config, source_root)
                source_mapping = sources.as_mapping()
                spy_source = next(
                    row
                    for row in source_mapping["sources"]
                    if row["dataset_id"] == "spy-adjusted-daily"
                )
                (source_root / spy_source["path"]).write_bytes(corrupt_body)
                bundle = write_historical_preparation(
                    config, sources, source_root, source_root / "outputs"
                )
                run_ids.append(bundle.run_id)
                spy_receipt = next(
                    row
                    for row in bundle.prepared.source_receipts
                    if row["dataset_id"] == "spy-adjusted-daily"
                )
                actual_hashes.append(spy_receipt["sha256"])

        self.assertNotEqual(run_ids[0], run_ids[1])
        self.assertEqual(
            actual_hashes,
            [
                hashlib.sha256(b"corrupt-a").hexdigest(),
                hashlib.sha256(b"corrupt-b").hexdigest(),
            ],
        )

    def test_failed_prepare_command_returns_machine_readable_bundle_receipt(self) -> None:
        config_mapping = load_study_config(PROTOCOL).as_mapping()
        config_mapping["episode_design"]["horizons_months"] = [12]
        for dataset in config_mapping["historical_datasets"]:
            dataset["eligible_start"] = "2020-01-01"
            dataset["data_cutoff"] = "2021-02-01"
        config = StudyConfig.from_mapping(config_mapping)
        incomplete_btc = BTC_CSV.replace(
            b"2021-02-01,141,142,139,140,10\n", b""
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "config.json"
            config_path.write_text(config.canonical_document, encoding="utf-8")
            loaded_config = load_study_config(config_path)
            sources = _acquire_confirmatory_sources(
                loaded_config, root, btc=incomplete_btc
            )
            source_set_path = root / "historical-source-set.json"
            error_output = io.StringIO()
            with contextlib.redirect_stderr(error_output):
                return_code = historical_main(
                    [
                        "prepare",
                        "--config",
                        str(config_path),
                        "--source-set",
                        str(source_set_path),
                        "--source-root",
                        str(root),
                        "--output-root",
                        str(root / "outputs"),
                    ]
                )

        self.assertEqual(return_code, 2)
        rejection = json.loads(error_output.getvalue())
        self.assertEqual(rejection["status"], "rejected")
        self.assertEqual(rejection["policy_execution"], "not-run")
        self.assertEqual(rejection["failed_dataset_count"], 1)

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

    def test_yahoo_acquisition_cli_requires_authorization_before_client_import(self) -> None:
        environment = dict(os.environ)
        environment.pop("YAHOO_FINANCE_AUTOMATED_ACCESS_AUTHORIZED", None)
        with tempfile.TemporaryDirectory() as directory:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "reproducibility.historical_data",
                    "acquire",
                    "--config",
                    str(YAHOO_PROTOCOL),
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
        self.assertEqual(rejection["code"], "missing_authorization")
        self.assertEqual(
            rejection["field"],
            "YAHOO_FINANCE_AUTOMATED_ACCESS_AUTHORIZED",
        )

    def test_prepare_cli_writes_confirmatory_handoff_without_policy_outputs(self) -> None:
        config_mapping = load_study_config(PROTOCOL).as_mapping()
        config_mapping["episode_design"]["horizons_months"] = [12]
        for dataset in config_mapping["historical_datasets"]:
            dataset["eligible_start"] = "2020-01-01"
            dataset["data_cutoff"] = "2021-02-01"

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "config.json"
            config_document = StudyConfig.from_mapping(config_mapping).canonical_document
            config_path.write_text(config_document, encoding="utf-8")
            _acquire_confirmatory_sources(load_study_config(config_path), root)
            source_set_path = root / "historical-source-set.json"
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
