"""Public-contract tests for the computational-finance methods literature slice."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from reproducibility.checks.literature_test_support import copy_literature_surface
from reproducibility.literature_controls import (
    LiteratureSynthesisError,
    audit_methodology_literature_synthesis,
)


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_NOTE_PATH = (
    "research/notes/reproducible-computational-finance-statistical-methodology.md"
)


class MethodologyLiteratureSynthesisTest(unittest.TestCase):
    def test_repository_literature_slice_is_complete_and_traceable(self) -> None:
        receipt = audit_methodology_literature_synthesis(ROOT)

        self.assertEqual(receipt["status"], "passed")
        self.assertEqual(receipt["literature_claim_count"], 5)
        self.assertGreaterEqual(receipt["bibliography_key_count"], 12)
        self.assertEqual(
            receipt["bibliography_key_count"], receipt["cited_key_count"]
        )

    def test_sampling_and_resampling_units_are_not_conflated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_literature_surface(
                Path(temporary_directory) / "repository", EVIDENCE_NOTE_PATH
            )
            claims_path = root / "manuscript/controls/claims.json"
            claims = json.loads(claims_path.read_text(encoding="utf-8"))
            reporting_claim = next(
                record
                for record in claims["records"]
                if record["id"] == "claim-lit-method-multiplicity-reporting"
            )
            reporting_claim["wording"] = reporting_claim["wording"].replace(
                (
                    "treats ordered rolling starts as the sampling units and "
                    "consecutive circular blocks as the resampling units"
                ),
                (
                    "treats ordered rolling starts and consecutive circular "
                    "blocks as resampling units"
                ),
            )
            claims_path.write_text(
                json.dumps(claims, indent=2) + "\n", encoding="utf-8"
            )

            with self.assertRaisesRegex(
                LiteratureSynthesisError, "sampling units"
            ):
                audit_methodology_literature_synthesis(root)

    def test_same_data_reconciliation_is_not_called_replication(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_literature_surface(
                Path(temporary_directory) / "repository", EVIDENCE_NOTE_PATH
            )
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace(
                    "it is not independent-data replication",
                    "it is independent-data replication",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                LiteratureSynthesisError, "independent-data replication"
            ):
                audit_methodology_literature_synthesis(root)

    def test_receipt_and_hash_do_not_grant_public_redistribution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_literature_surface(
                Path(temporary_directory) / "repository", EVIDENCE_NOTE_PATH
            )
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace(
                    "do not by themselves grant public redistribution",
                    "therefore grant public redistribution",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                LiteratureSynthesisError, "grant public redistribution"
            ):
                audit_methodology_literature_synthesis(root)

    def test_repository_registration_is_not_relabelled_preregistration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_literature_surface(
                Path(temporary_directory) / "repository", EVIDENCE_NOTE_PATH
            )
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace(
                    "not a preregistration",
                    "a preregistration",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                LiteratureSynthesisError, "third-party registry"
            ):
                audit_methodology_literature_synthesis(root)

    def test_holm_guarantee_is_conditional_on_valid_cell_p_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_literature_surface(
                Path(temporary_directory) / "repository", EVIDENCE_NOTE_PATH
            )
            claims_path = root / "manuscript/controls/claims.json"
            claims = json.loads(claims_path.read_text(encoding="utf-8"))
            reporting_claim = next(
                record
                for record in claims["records"]
                if record["id"] == "claim-lit-method-multiplicity-reporting"
            )
            reporting_claim["scope"] = reporting_claim["scope"].replace(
                (
                    "the family-wise error guarantee is conditional on valid "
                    "cellwise unadjusted p-values"
                ),
                (
                    "the family-wise error procedure uses valid cellwise "
                    "unadjusted p-values"
                ),
            )
            claims_path.write_text(
                json.dumps(claims, indent=2) + "\n", encoding="utf-8"
            )

            with self.assertRaisesRegex(
                LiteratureSynthesisError, "guarantee is conditional"
            ):
                audit_methodology_literature_synthesis(root)


if __name__ == "__main__":
    unittest.main()
