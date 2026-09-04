from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from reproducibility.boundary_controls import (
    BoundaryControlError,
    audit_finite_arbitrary_horizon_boundaries,
)


ROOT = Path(__file__).resolve().parents[2]


class FiniteArbitraryHorizonBoundariesTest(unittest.TestCase):
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
        self.assertEqual(receipt["notation_count"], 4)
        self.assertEqual(receipt["nonclaim_count"], 1)

    def test_sufficient_guardrail_feedback_cannot_be_promoted_to_necessity(self) -> None:
        marker = "Condition (\\ref{eq:reference-aligned-feedback}) is sufficient, not necessary."
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "repository"
            target = root / "manuscript/source/thesis.tex"
            target.parent.mkdir(parents=True)
            shutil.copy2(ROOT / "manuscript/source/thesis.tex", target)
            source = target.read_text(encoding="utf-8")
            self.assertIn(marker, source)
            target.write_text(
                source.replace(marker, "The alignment condition is necessary."),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                BoundaryControlError, "qualified cash single crossing"
            ):
                audit_finite_arbitrary_horizon_boundaries(root)


if __name__ == "__main__":
    unittest.main()
