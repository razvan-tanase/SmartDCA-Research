from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from reproducibility.safety_policy_controls import (
    SafetyPolicyControlError,
    audit_impossibility_safety_policy_architecture,
)


ROOT = Path(__file__).resolve().parents[2]


class ImpossibilitySafetyPolicyArchitectureTest(unittest.TestCase):
    def test_repository_impossibility_slice_states_the_full_model(self) -> None:
        receipt = audit_impossibility_safety_policy_architecture(ROOT)

        self.assertEqual(receipt["status"], "passed")

    def test_relative_wealth_floor_cannot_be_promoted_to_dominance(self) -> None:
        marker = (
            "For $\\varepsilon>0$, this is not dominance: a safe policy "
            "may finish below DCA"
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "repository"
            target = root / "manuscript/source/thesis.tex"
            target.parent.mkdir(parents=True)
            shutil.copy2(ROOT / "manuscript/source/thesis.tex", target)
            source = target.read_text(encoding="utf-8")
            self.assertIn(marker, source)
            target.write_text(
                source.replace(marker, "The guarded policy dominates DCA"),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                SafetyPolicyControlError, "relative-wealth floor"
            ):
                audit_impossibility_safety_policy_architecture(root)

    def test_complete_policy_and_conceptual_asset_are_audited(self) -> None:
        asset_path = ROOT / "manuscript/generated/policy-architecture.tex"
        self.assertTrue(asset_path.is_file())

        receipt = audit_impossibility_safety_policy_architecture(ROOT)

        self.assertEqual(
            receipt["policy_asset"],
            "manuscript/generated/policy-architecture.tex",
        )

    def test_complete_proof_machinery_is_retained_in_the_appendix(self) -> None:
        receipt = audit_impossibility_safety_policy_architecture(ROOT)

        self.assertEqual(receipt["appendix_proof_count"], 2)

    def test_claim_notation_nonclaim_and_citation_controls_are_traceable(self) -> None:
        receipt = audit_impossibility_safety_policy_architecture(ROOT)

        self.assertEqual(receipt["claim_count"], 4)
        self.assertEqual(receipt["notation_count"], 4)
        self.assertEqual(receipt["nonclaim_count"], 2)
        self.assertGreaterEqual(receipt["chapter_citation_count"], 3)


if __name__ == "__main__":
    unittest.main()
