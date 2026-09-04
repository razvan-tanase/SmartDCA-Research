from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from reproducibility.foundation_controls import (
    FoundationControlError,
    audit_financial_model_corrected_signal_foundations,
)


ROOT = Path(__file__).resolve().parents[2]
SURFACE_PATHS = (
    "manuscript/bibliography/references.bib",
    "manuscript/controls/claims.json",
    "manuscript/controls/notation.json",
    "manuscript/source/thesis.tex",
    "research/definitions/corrected-out-quasi-gini-mean.md",
    "research/definitions/guarded-corrected-mean-smartdca-rule.md",
    "research/notes/guarded-corrected-mean-smartdca.md",
    "research/notes/pathwise-dca-dominance-under-causal-budget.md",
    "research/notes/prior-theory-corrected-out-quasi-gini.md",
    "research/notes/source-out-quasi-gini-audit.md",
    "research/notes/ticket-07-homogeneity-primary-sources.md",
    "research/theorems/causal-dca-dominance-impossibility.md",
    "research/theorems/corrected-mean-homogeneity-characterization.md",
    "research/theorems/source-out-functional-mean-classification.md",
    "reproducibility/checks/check_corrected_out_quasi_gini_homogeneity.py",
    "reproducibility/checks/check_guarded_corrected_mean_smartdca.py",
    "reproducibility/checks/check_pathwise_dca_dominance.py",
)


def copy_foundation_surface(destination: Path) -> Path:
    for relative_path in SURFACE_PATHS:
        source = ROOT / relative_path
        target = destination / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return destination


class FinancialModelCorrectedSignalFoundationsTest(unittest.TestCase):
    def test_repository_foundation_slice_is_complete_and_traceable(self) -> None:
        receipt = audit_financial_model_corrected_signal_foundations(ROOT)

        self.assertEqual(receipt["status"], "passed")
        self.assertEqual(receipt["claim_count"], 6)
        self.assertGreaterEqual(receipt["notation_count"], 18)
        self.assertGreaterEqual(receipt["chapter_citation_count"], 6)

    def test_missing_financial_model_assumption_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_foundation_surface(Path(temporary_directory) / "repository")
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace(
                    "long-only, buy-only, fully funded",
                    "fully funded",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                FoundationControlError, "financial-model assumption"
            ):
                audit_financial_model_corrected_signal_foundations(root)

    def test_same_deposit_dca_contract_is_rejected_when_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_foundation_surface(Path(temporary_directory) / "repository")
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace(
                    "DCA receives the same deposit\nsequence and the same "
                    "evaluation horizon",
                    "DCA supplies a comparison policy",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                FoundationControlError, "same-deposit comparator"
            ):
                audit_financial_model_corrected_signal_foundations(root)

    def test_missing_claim_mapping_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_foundation_surface(Path(temporary_directory) / "repository")
            claims_path = root / "manuscript/controls/claims.json"
            claims = json.loads(claims_path.read_text(encoding="utf-8"))
            signal_claim = next(
                record
                for record in claims["records"]
                if record["id"] == "claim-def-corrected-signal"
            )
            signal_claim["id"] = "removed-signal-claim"
            claims_path.write_text(
                json.dumps(claims, indent=2) + "\n", encoding="utf-8"
            )

            with self.assertRaisesRegex(
                FoundationControlError, "missing foundation claim"
            ):
                audit_financial_model_corrected_signal_foundations(root)

    def test_signal_first_use_must_match_the_notation_register(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_foundation_surface(Path(temporary_directory) / "repository")
            notation_path = root / "manuscript/controls/notation.json"
            notation = json.loads(notation_path.read_text(encoding="utf-8"))
            signal_notation = next(
                record
                for record in notation["records"]
                if record["id"] == "notation-reference-score"
            )
            signal_notation["first_use"] = "ch:safety/sec:adaptive-selector"
            notation_path.write_text(
                json.dumps(notation, indent=2) + "\n", encoding="utf-8"
            )

            with self.assertRaisesRegex(
                FoundationControlError, "notation-reference-score.*first_use"
            ):
                audit_financial_model_corrected_signal_foundations(root)

    def test_acquisition_cost_cannot_be_promoted_to_performance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_foundation_surface(Path(temporary_directory) / "repository")
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace(
                    "an\naccounting quantity, not a budget-equivalent "
                    "performance criterion",
                    "a budget-equivalent performance criterion",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                FoundationControlError, "acquisition-cost boundary"
            ):
                audit_financial_model_corrected_signal_foundations(root)

    def test_signal_safety_disclaimer_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_foundation_surface(Path(temporary_directory) / "repository")
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace(
                    "The normalized lagged reference supplies a causal signal, "
                    "not a safety\n"
                    "guarantee.",
                    "The normalized lagged reference supplies a causal signal.",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                FoundationControlError, "signal-safety boundary"
            ):
                audit_financial_model_corrected_signal_foundations(root)

    def test_detailed_homogeneity_proof_is_required_in_the_appendix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_foundation_surface(Path(temporary_directory) / "repository")
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace(
                    "\\label{sec:proof-corrected-homogeneity}",
                    "\\label{sec:removed-homogeneity-proof}",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                FoundationControlError, "appendix proof"
            ):
                audit_financial_model_corrected_signal_foundations(root)

    def test_source_assumption_is_distinguished_from_project_generalization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_foundation_surface(Path(temporary_directory) / "repository")
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace(
                    "The source assumes that its transform is positive\n"
                    "and increasing. The project's classification is stronger: "
                    "it needs only\n"
                    "positivity.",
                    "The transform is positive.",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                FoundationControlError, "source-functional classification"
            ):
                audit_financial_model_corrected_signal_foundations(root)

    def test_diagonal_proof_must_cover_every_parameter_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_foundation_surface(Path(temporary_directory) / "repository")
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace(
                    "along any parameter path",
                    "with beta fixed",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                FoundationControlError, "appendix proof"
            ):
                audit_financial_model_corrected_signal_foundations(root)

    def test_undefined_chapter_citation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_foundation_surface(Path(temporary_directory) / "repository")
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            marker = "\\citep{calvet2023smartdca}. One-point"
            source_path.write_text(
                source.replace(
                    marker,
                    "\\citep{calvet2023smartdca,missing-foundation-source}. "
                    "One-point",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                FoundationControlError, "undefined Chapter 3 citation"
            ):
                audit_financial_model_corrected_signal_foundations(root)


if __name__ == "__main__":
    unittest.main()
