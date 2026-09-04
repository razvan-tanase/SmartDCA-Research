"""Public-contract tests for the empirical-methodology manuscript slice."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from reproducibility.methodology_controls import (
    MethodologyControlError,
    audit_empirical_methodology_reproducibility,
)


ROOT = Path(__file__).resolve().parents[2]


class EmpiricalMethodologyReproducibilityTest(unittest.TestCase):
    def prepare_audit_repository(self, root: Path) -> None:
        fixed_paths = {
            "manuscript/source/thesis.tex",
            "manuscript/bibliography/references.bib",
            "manuscript/controls/claims.json",
            "manuscript/controls/notation.json",
            "manuscript/controls/non-claims.json",
            "research/notes/empirical-methodology-reproducibility-manuscript-audit.md",
            "experiments/protocols/safety-adaptivity-v1.json",
            "experiments/protocols/safety-adaptivity-yahoo-v2.json",
            "experiments/inputs/historical-yahoo-registered-robustness-v1.json",
            "experiments/inputs/historical-yahoo-receipts-v2.json",
            "experiments/inputs/historical-yahoo-preparation-manifest-v5.json",
            (
                "reports/experiments/runs/"
                "smartdca-empirical-package-review-v1-"
                "6cb6c1cd94b901be90ebd553a022c922e53984afafeb22948747be084b37c14f/"
                "review-receipt.json"
            ),
            (
                "reports/experiments/runs/"
                "smartdca-empirical-package-review-v1-"
                "6cb6c1cd94b901be90ebd553a022c922e53984afafeb22948747be084b37c14f/"
                "manifest.json"
            ),
        }
        claims = json.loads(
            (ROOT / "manuscript/controls/claims.json").read_text(encoding="utf-8")
        )
        for record in claims["records"]:
            if record["id"].startswith("claim-method-") or record["id"] in {
                "claim-table-protocol-grid",
                "claim-table-reproducibility",
            }:
                fixed_paths.update(entry["path"] for entry in record["authority"])
        nonclaims = json.loads(
            (ROOT / "manuscript/controls/non-claims.json").read_text(
                encoding="utf-8"
            )
        )
        for record in nonclaims["records"]:
            if record["id"] in {
                "nonclaim-frictional-safety",
                "nonclaim-empirical-causality",
            }:
                fixed_paths.update(record["authority_paths"])
        for relative_path in fixed_paths:
            target = root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative_path, target)

    def assert_source_mutation_is_rejected(
        self,
        *,
        marker: str,
        replacement: str,
        error_pattern: str,
        replace_last: bool = False,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "repository"
            self.prepare_audit_repository(root)
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            marker_index = source.rfind(marker) if replace_last else source.find(marker)
            self.assertNotEqual(marker_index, -1)
            source_path.write_text(
                source[:marker_index]
                + replacement
                + source[marker_index + len(marker) :],
                encoding="utf-8",
            )

            with self.assertRaisesRegex(MethodologyControlError, error_pattern):
                audit_empirical_methodology_reproducibility(root)

    def test_repository_methodology_slice_is_complete_and_traceable(self) -> None:
        receipt = audit_empirical_methodology_reproducibility(ROOT)

        self.assertEqual(receipt["status"], "passed")

    def test_public_receipt_covers_the_full_methodology_contract(self) -> None:
        receipt = audit_empirical_methodology_reproducibility(ROOT)

        self.assertEqual(receipt["policy_count"], 3)
        self.assertEqual(receipt["comparison_tier_count"], 3)
        self.assertEqual(receipt["evidence_layer_count"], 4)
        self.assertEqual(receipt["confirmatory_hypothesis_count"], 2)
        self.assertEqual(receipt["methodology_claim_count"], 7)
        self.assertEqual(receipt["methodology_table_claim_count"], 2)
        self.assertEqual(receipt["accepted_run_count"], 7)
        self.assertEqual(receipt["appendix_count"], 2)

    def test_canonical_build_runs_the_methodology_audit(self) -> None:
        build_source = (ROOT / "manuscript/build.py").read_text(encoding="utf-8")

        self.assertIn('"methodology_controls.py"', build_source)

    def test_reproducibility_workflow_runs_the_methodology_audit(self) -> None:
        workflow = (ROOT / ".github/workflows/reproducibility.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "python -m unittest "
            "reproducibility.checks.check_empirical_methodology_reproducibility",
            workflow,
        )

    def test_public_receipt_binds_the_accepted_private_boundary_metadata(self) -> None:
        receipt = audit_empirical_methodology_reproducibility(ROOT)

        self.assertEqual(
            receipt["source_receipt_sha256"],
            "346676eb699d4e64cee7f687a04f207d6ab4daff92abae780719368d259f97f4",
        )
        self.assertEqual(
            receipt["preparation_manifest_sha256"],
            "f86691e21acb8f1f70d9d9124c020f126014aae5aa631c90a0f82165814e5894",
        )
        self.assertEqual(
            receipt["independent_review_receipt_sha256"],
            "9ad1daa4c43e81232fdfbabb295c37a67b87422f11b8de7abf8c2c9b38df1e9b",
        )

    def test_public_receipt_requires_independent_manuscript_review(self) -> None:
        receipt = audit_empirical_methodology_reproducibility(ROOT)

        self.assertEqual(receipt["independent_manuscript_review_status"], "passed")

    def test_public_receipt_covers_each_cost_execution_model(self) -> None:
        receipt = audit_empirical_methodology_reproducibility(ROOT)

        self.assertEqual(receipt["cost_execution_model_count"], 3)

    def test_finite_run_p_value_cannot_drop_the_plus_one_denominator(self) -> None:
        marker = (
            r"\mathbf{1}\{|\widehat{\theta}_b-\widehat{\theta}|"
            "\n"
            r"      \geq |\widehat{\theta}|\}}{B+1}."
        )
        self.assert_source_mutation_is_rejected(
            marker=marker,
            replacement=marker.replace("{B+1}.", "{B}."),
            error_pattern="finite-run",
        )

    def test_fee_routes_cannot_inherit_the_frictionless_theorem(self) -> None:
        marker = (
            "the 10-basis-point and one-dollar routes are tagged\n"
            "\\path{outside-current-safety-theorem}"
        )
        self.assert_source_mutation_is_rejected(
            marker=marker,
            replacement=(
                "the 10-basis-point and one-dollar routes are tagged\n"
                "\\path{epsilon-dca}"
            ),
            error_pattern="fee routes",
        )

    def test_fee_target_budget_cannot_be_called_asset_notional(self) -> None:
        marker = (
            r"runner maps selected budget $\widetilde b_t^S$ to actual"
            "\n"
            r"asset notional $b_t^S$ and fee $F_t^S$"
        )
        self.assert_source_mutation_is_rejected(
            marker=marker,
            replacement=marker.replace(
                "to actual\nasset notional", "to the\nasset target"
            ),
            error_pattern="actual asset notional",
        )

    def test_claim_declared_method_citation_is_section_local(self) -> None:
        marker = r"\citep{kunsch1989blockbootstrap,politisromano1992circular}"
        self.assert_source_mutation_is_rejected(
            marker=marker,
            replacement="",
            error_pattern=(
                "claim-method-estimands-inference: methodology slice does not cite"
            ),
            replace_last=True,
        )


if __name__ == "__main__":
    unittest.main()
