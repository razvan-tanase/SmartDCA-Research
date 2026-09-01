"""Public-contract checks for the empirical-package publication review."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from reproducibility.empirical_package_review import (
    PublicationReviewError,
    run_publication_review,
)


ROOT = Path(__file__).resolve().parents[2]
PRIVATE_PREPARATION = (
    ROOT
    / "data/raw/smartdca-historical-preparation-yahoo-v1"
    / "smartdca-historical-input-v1-4da2c9a1982b48cc821969e802118270d7a95e44cc03107e8d2846729df0e14f"
)
PRIVATE_HISTORICAL_RUN = (
    ROOT
    / "data/raw/smartdca-historical-confirmatory-yahoo-v1"
    / "smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221"
)
PRIVATE_ROBUSTNESS_RUN = (
    ROOT
    / "data/raw/smartdca-historical-robustness-yahoo-v1"
    / "smartdca-historical-robustness-v1-0991d999e1a8070a2a6eb8046b08a91d0e42341995610a602372c52dfab14184"
)
RETAINED_REVIEW_REGISTRY = Path(
    "experiments/inputs/empirical-package-publication-review-v1.json"
)


def _copy_public_repository(destination: Path) -> Path:
    return Path(
        shutil.copytree(
            ROOT,
            destination,
            copy_function=os.link,
            ignore=shutil.ignore_patterns(
                ".agents",
                ".codex",
                ".git",
                ".venv",
                "data",
                "__pycache__",
                ".pytest_cache",
            ),
        )
    )


class EmpiricalPackagePublicationReviewTest(unittest.TestCase):
    def test_one_route_reproduces_and_audits_the_public_package(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output_root = Path(temporary) / "review"
            receipt = run_publication_review(ROOT, output_root)

            self.assertEqual(receipt["status"], "passed")
            self.assertEqual(
                receipt["review_basis"], "retained-private-review-receipt"
            )
            self.assertEqual(receipt["retained_private_review"]["status"], "passed")
            self.assertEqual(
                receipt["retained_private_review"][
                    "historical_calendar_episode_match_count"
                ],
                1365,
            )
            self.assertEqual(
                receipt["retained_private_review"][
                    "robustness_raw_aggregate_match_count"
                ],
                810,
            )
            self.assertEqual(
                receipt["deterministic_reproduction"]["study_run_id"],
                "smartdca-deterministic-v1-80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db",
            )
            self.assertEqual(
                receipt["deterministic_independent_replay"]["ledger_count"],
                648,
            )
            self.assertEqual(
                receipt["synthesis_reproduction"]["normalized_group_count"],
                2754,
            )
            self.assertEqual(
                receipt["historical_slice_review"]["status"],
                "not-run-private-inputs-not-supplied",
            )
            self.assertEqual(
                receipt["historical_robustness_review"]["status"],
                "not-run-private-inputs-not-supplied",
            )
            self.assertEqual(receipt["provenance_audit"]["status"], "passed")
            self.assertEqual(receipt["provenance_audit"]["accepted_run_count"], 7)
            self.assertEqual(receipt["provenance_audit"]["source_receipt_count"], 2)
            self.assertEqual(
                receipt["provenance_audit"]["reconstructed_run_identity_count"], 6
            )
            self.assertEqual(receipt["claim_audit"]["normalized_cell_count"], 2754)
            self.assertEqual(receipt["claim_audit"]["holm_family_size"], 36)
            self.assertEqual(receipt["publication_state_audit"]["status"], "passed")
            self.assertEqual(
                receipt["publication_state_audit"][
                    "publication_ready_report_count"
                ],
                6,
            )
            self.assertEqual(
                receipt["publication_state_audit"][
                    "resolved_acceptance_criterion_count"
                ],
                10,
            )
            self.assertEqual(
                receipt["publication_state_audit"]["effort_state"], "completed"
            )
            self.assertEqual(
                receipt["publication_state_audit"]["project_frontier"],
                "manuscript-assembly",
            )
            self.assertTrue((output_root / "review-receipt.json").is_file())
            self.assertTrue((output_root / "failure-records.jsonl").is_file())

    def test_public_only_route_without_retained_private_pass_is_non_clearing(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            repository = _copy_public_repository(temporary_root / "repository")
            (repository / RETAINED_REVIEW_REGISTRY).unlink()
            receipt = run_publication_review(
                repository, temporary_root / "review-without-private-pass"
            )

            self.assertEqual(
                receipt["status"], "not-cleared-private-review-not-retained"
            )
            self.assertEqual(
                receipt["review_basis"], "public-only-unreviewed-private-evidence"
            )
            self.assertEqual(
                receipt["retained_private_review"]["status"], "not-retained"
            )

    def test_public_only_route_rejects_a_changed_retained_review_receipt(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            repository = _copy_public_repository(temporary_root / "repository")
            registry = json.loads(
                (repository / RETAINED_REVIEW_REGISTRY).read_text(encoding="utf-8")
            )
            receipt_path = repository / registry["path"] / "review-receipt.json"
            receipt_path.unlink()
            receipt_path.write_text("{}\n", encoding="utf-8")

            with self.assertRaisesRegex(
                PublicationReviewError,
                "retained_review_artifact_fingerprint_mismatch",
            ):
                run_publication_review(repository, temporary_root / "changed-review")

    @unittest.skipUnless(
        PRIVATE_PREPARATION.is_dir()
        and PRIVATE_HISTORICAL_RUN.is_dir()
        and PRIVATE_ROBUSTNESS_RUN.is_dir(),
        "provider-restricted private historical artifacts are absent",
    )
    def test_private_route_independently_replays_registered_historical_slice(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            receipt = run_publication_review(
                ROOT,
                Path(temporary) / "review",
                private_preparation_directory=PRIVATE_PREPARATION,
                private_historical_run_directory=PRIVATE_HISTORICAL_RUN,
                private_robustness_run_directory=PRIVATE_ROBUSTNESS_RUN,
            )

            historical = receipt["historical_slice_review"]
            self.assertEqual(historical["status"], "passed")
            self.assertEqual(historical["dataset_id"], "spy-adjusted-daily")
            self.assertEqual(historical["horizon_months"], 12)
            self.assertEqual(historical["coverage"], "0.75")
            self.assertEqual(historical["episode_count"], 383)
            self.assertEqual(historical["comparison_count"], 1149)
            self.assertEqual(historical["aggregate_match_count"], 3)
            self.assertEqual(historical["primary_raw_aggregate_match_count"], 54)
            self.assertEqual(historical["bootstrap_cell_match_count"], 36)
            self.assertEqual(historical["full_calendar_episode_match_count"], 1365)
            robustness = receipt["historical_robustness_review"]
            self.assertEqual(robustness["status"], "passed")
            self.assertEqual(robustness["private_artifact_match_count"], 21)
            self.assertEqual(robustness["raw_result_count"], 108378)
            self.assertEqual(robustness["raw_aggregate_match_count"], 810)
            self.assertEqual(
                receipt["retained_private_review"]["status"],
                "not-required-live-private-review",
            )

    def test_failed_route_preserves_a_machine_readable_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output_root = Path(temporary) / "review"
            with self.assertRaisesRegex(
                Exception, "incomplete_private_review_paths"
            ):
                run_publication_review(
                    ROOT,
                    output_root,
                    private_preparation_directory=Path(temporary) / "partial",
                )

            failure = (output_root / "failure-records.jsonl").read_text(
                encoding="utf-8"
            )
            self.assertIn('"code":"incomplete_private_review_paths"', failure)

    def test_retained_review_registry_cannot_escape_the_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            repository = temporary_root / "repository"
            registry = (
                repository
                / "experiments/inputs/empirical-package-publication-review-v1.json"
            )
            registry.parent.mkdir(parents=True)
            registry.write_text(
                json.dumps(
                    {
                        "schema_version": (
                            "smartdca-empirical-package-review-registry/1"
                        ),
                        "review_id": "smartdca-empirical-package-review-v1-invalid",
                        "path": "../outside",
                        "manifest_sha256": "0" * 64,
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                PublicationReviewError, "invalid_retained_review_registry"
            ):
                run_publication_review(repository, temporary_root / "output")

    def test_retained_review_manifest_must_match_the_registered_fingerprint(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            repository = temporary_root / "repository"
            review_id = "smartdca-empirical-package-review-v1-" + "1" * 64
            review_root = repository / "reports/experiments/runs" / review_id
            review_root.mkdir(parents=True)
            (review_root / "manifest.json").write_text("{}\n", encoding="utf-8")
            registry = (
                repository
                / "experiments/inputs/empirical-package-publication-review-v1.json"
            )
            registry.parent.mkdir(parents=True)
            registry.write_text(
                json.dumps(
                    {
                        "schema_version": (
                            "smartdca-empirical-package-review-registry/1"
                        ),
                        "review_id": review_id,
                        "path": f"reports/experiments/runs/{review_id}",
                        "manifest_sha256": "0" * 64,
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                PublicationReviewError,
                "retained_review_manifest_fingerprint_mismatch",
            ):
                run_publication_review(repository, temporary_root / "output")


if __name__ == "__main__":
    unittest.main()
