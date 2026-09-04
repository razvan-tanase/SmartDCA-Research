from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from reproducibility.boundary_controls import (
    BOUNDARY_CLAIMS,
    BOUNDARY_NONCLAIMS,
    BoundaryControlError,
    audit_finite_arbitrary_horizon_boundaries,
)


ROOT = Path(__file__).resolve().parents[2]


class FiniteArbitraryHorizonBoundariesTest(unittest.TestCase):
    def prepare_audit_repository(self, root: Path) -> None:
        for relative_path in (
            "manuscript/source/thesis.tex",
            "manuscript/controls/claims.json",
            "manuscript/controls/notation.json",
            "manuscript/controls/non-claims.json",
        ):
            target = root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative_path, target)

        claims = json.loads(
            (ROOT / "manuscript/controls/claims.json").read_text(encoding="utf-8")
        )
        nonclaims = json.loads(
            (ROOT / "manuscript/controls/non-claims.json").read_text(
                encoding="utf-8"
            )
        )
        authority_paths = {
            entry["path"]
            for record in claims["records"]
            if record["id"] in BOUNDARY_CLAIMS
            for entry in record["authority"]
        }
        authority_paths.update(
            path
            for record in nonclaims["records"]
            if record["id"] in BOUNDARY_NONCLAIMS
            for path in record["authority_paths"]
        )
        for relative_path in authority_paths:
            target = root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative_path, target)

    def assert_source_mutation_rejected(
        self,
        marker: str,
        replacement: str,
        expected_error: str,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "repository"
            self.prepare_audit_repository(root)
            target = root / "manuscript/source/thesis.tex"
            source = target.read_text(encoding="utf-8")
            self.assertIn(marker, source)
            target.write_text(
                source.replace(marker, replacement, 1),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(BoundaryControlError, expected_error):
                audit_finite_arbitrary_horizon_boundaries(root)

    def test_repository_boundary_slice_passes_its_public_audit(self) -> None:
        receipt = audit_finite_arbitrary_horizon_boundaries(ROOT)

        self.assertEqual(receipt["status"], "passed")

    def test_two_and_three_purchase_boundaries_are_audited(self) -> None:
        receipt = audit_finite_arbitrary_horizon_boundaries(ROOT)

        self.assertEqual(receipt["finite_boundary_count"], 2)

    def test_cash_timing_theorem_and_valley_falsification_are_distinct(self) -> None:
        receipt = audit_finite_arbitrary_horizon_boundaries(ROOT)

        self.assertEqual(receipt["accounting_identity_count"], 1)
        self.assertEqual(receipt["finite_search_count"], 1)

    def test_qualified_cash_single_crossing_condition_is_audited(self) -> None:
        receipt = audit_finite_arbitrary_horizon_boundaries(ROOT)

        self.assertEqual(receipt["cash_crossing_condition_count"], 1)

    def test_terminal_inventory_classification_and_scope_map_are_audited(self) -> None:
        receipt = audit_finite_arbitrary_horizon_boundaries(ROOT)

        self.assertEqual(receipt["ledger_classification_count"], 1)
        self.assertEqual(receipt["scope_table_count"], 1)

    def test_detailed_proofs_cases_and_witnesses_are_in_appendix_b(self) -> None:
        receipt = audit_finite_arbitrary_horizon_boundaries(ROOT)

        self.assertEqual(receipt["appendix_section_count"], 6)

    def test_claim_notation_and_nonclaim_controls_are_traceable(self) -> None:
        receipt = audit_finite_arbitrary_horizon_boundaries(ROOT)

        self.assertEqual(receipt["claim_count"], 8)
        self.assertEqual(receipt["notation_count"], 5)
        self.assertEqual(receipt["nonclaim_count"], 1)

    def test_sufficient_guardrail_feedback_cannot_be_promoted_to_necessity(self) -> None:
        marker = "Condition (\\ref{eq:reference-aligned-feedback}) is sufficient, not necessary."
        self.assert_source_mutation_rejected(
            marker,
            "The alignment condition is necessary.",
            "qualified cash single crossing",
        )

    def test_cash_crossing_scope_cannot_drop_equal_positive_deposits(self) -> None:
        self.assert_source_mutation_rejected(
            "Suppose equal positive deposits are used",
            "Suppose arbitrary deposits are used",
            "qualified cash single crossing",
        )

    def test_affine_win_loss_direction_is_audited(self) -> None:
        self.assert_source_mutation_rejected(
            "win below, tie at, and loss above the root",
            "loss below, tie at, and win above the root",
            "terminal-inventory boundary",
        )

    def test_two_purchase_lambda_one_endpoint_is_audited(self) -> None:
        self.assert_source_mutation_rejected(
            "at $\\lambda=1$, every discretionary interval",
            "at $\\lambda=1$, the corrected rule wins and every discretionary interval",
            "two-purchase boundary",
        )

    def test_scope_table_requires_canonical_and_detailed_authorities(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "repository"
            self.prepare_audit_repository(root)
            claims_path = root / "manuscript/controls/claims.json"
            claims = json.loads(claims_path.read_text(encoding="utf-8"))
            table_record = next(
                record
                for record in claims["records"]
                if record["id"] == "claim-table-theorem-scope"
            )
            removed = table_record["authority"].pop()
            claims_path.write_text(
                json.dumps(claims, indent=2) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                BoundaryControlError,
                f"missing required authority.*{removed['path']}",
            ):
                audit_finite_arbitrary_horizon_boundaries(root)


if __name__ == "__main__":
    unittest.main()
