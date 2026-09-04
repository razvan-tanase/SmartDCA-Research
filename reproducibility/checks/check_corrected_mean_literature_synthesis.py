"""Public-contract tests for the corrected-mean prior-theory literature slice."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from reproducibility.checks.literature_test_support import copy_literature_surface
from reproducibility.literature_controls import (
    LiteratureSynthesisError,
    audit_corrected_mean_literature_synthesis,
)


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_NOTE_PATH = "research/notes/corrected-mean-prior-theory-literature.md"


class CorrectedMeanLiteratureSynthesisTest(unittest.TestCase):
    def test_repository_literature_slice_is_complete_and_traceable(self) -> None:
        receipt = audit_corrected_mean_literature_synthesis(ROOT)

        self.assertEqual(receipt["status"], "passed")
        self.assertEqual(receipt["literature_claim_count"], 5)
        self.assertGreaterEqual(receipt["bibliography_key_count"], 8)
        self.assertEqual(
            receipt["bibliography_key_count"], receipt["cited_key_count"]
        )

    def test_undefined_primary_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_literature_surface(
                Path(temporary_directory) / "repository", EVIDENCE_NOTE_PATH
            )
            claims_path = root / "manuscript/controls/claims.json"
            claims = json.loads(claims_path.read_text(encoding="utf-8"))
            family_claim = next(
                record
                for record in claims["records"]
                if record["id"] == "claim-lit-mean-family-identification"
            )
            family_claim["citation_keys"].append("missing-primary-source")
            claims_path.write_text(
                json.dumps(claims, indent=2) + "\n", encoding="utf-8"
            )

            with self.assertRaisesRegex(
                LiteratureSynthesisError, "undefined bibliography key"
            ):
                audit_corrected_mean_literature_synthesis(root)

    def test_uncited_primary_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_literature_surface(
                Path(temporary_directory) / "repository", EVIDENCE_NOTE_PATH
            )
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace("paleszakaria2020", "paleszakaria2020-removed"),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                LiteratureSynthesisError, "not cited by the manuscript"
            ):
                audit_corrected_mean_literature_synthesis(root)

    def test_missing_claim_to_evidence_mapping_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_literature_surface(
                Path(temporary_directory) / "repository", EVIDENCE_NOTE_PATH
            )
            note_path = (
                root / "research/notes/corrected-mean-prior-theory-literature.md"
            )
            note = note_path.read_text(encoding="utf-8")
            note_path.write_text(
                note.replace(
                    "claim-lit-mean-contribution-boundary",
                    "removed-claim-identifier",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                LiteratureSynthesisError, "missing claim-to-evidence identifier"
            ):
                audit_corrected_mean_literature_synthesis(root)

    def test_claim_citations_must_appear_in_the_claim_section(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_literature_surface(
                Path(temporary_directory) / "repository", EVIDENCE_NOTE_PATH
            )
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace(
                    "\\citep{calvet2023smartdca,paleszakaria2020,aczeldaroczy1963}",
                    "",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                LiteratureSynthesisError, "not cited in manuscript section"
            ):
                audit_corrected_mean_literature_synthesis(root)

    def test_parameter_gap_uses_registered_manuscript_notation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_literature_surface(
                Path(temporary_directory) / "repository", EVIDENCE_NOTE_PATH
            )
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace(
                    r"\Delta=\alpha-\beta\ne0",
                    r"d=\alpha-\beta\ne0",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                LiteratureSynthesisError, "corrected-mean boundary"
            ):
                audit_corrected_mean_literature_synthesis(root)

    def test_mean_inputs_use_registered_manuscript_notation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_literature_surface(
                Path(temporary_directory) / "repository", EVIDENCE_NOTE_PATH
            )
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace(
                    r"\mathrm{out}}(u;w)",
                    r"\mathrm{out}}(x;w)",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                LiteratureSynthesisError, "corrected-mean boundary"
            ):
                audit_corrected_mean_literature_synthesis(root)

    def test_transform_domain_is_stated_at_first_use(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_literature_surface(
                Path(temporary_directory) / "repository", EVIDENCE_NOTE_PATH
            )
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace("positive finite transform", "positive transform", 1),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                LiteratureSynthesisError, "corrected-mean boundary"
            ):
                audit_corrected_mean_literature_synthesis(root)

    def test_unsafe_new_mean_class_claim_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = copy_literature_surface(
                Path(temporary_directory) / "repository", EVIDENCE_NOTE_PATH
            )
            source_path = root / "manuscript/source/thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace(
                    "is not a new general mean class",
                    "is a new general mean class",
                    1,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                LiteratureSynthesisError, "conservative novelty boundary"
            ):
                audit_corrected_mean_literature_synthesis(root)


if __name__ == "__main__":
    unittest.main()
