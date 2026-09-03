from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT_ROOT = REPOSITORY_ROOT / "manuscript"
CHECKER = REPOSITORY_ROOT / "manuscript" / "check_controls.py"


class ManuscriptControlTests(unittest.TestCase):
    def write_json(self, path: Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def run_checker(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(root)],
            cwd=REPOSITORY_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_well_formed_control_package_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.write_json(
                root / "controls" / "control-manifest.json",
                {
                    "schema_version": 1,
                    "control_set_id": "test-controls-v1",
                    "registers": [
                        {"name": "sample", "path": "controls/sample.json"}
                    ],
                },
            )
            self.write_json(
                root / "controls" / "sample.json",
                {
                    "schema_version": 1,
                    "register": "sample",
                    "records": [
                        {
                            "id": "sample-record",
                            "mandatory": True,
                            "review_state": "accepted",
                        }
                    ],
                },
            )

            result = self.run_checker(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CONTROL CHECK PASSED", result.stdout)

    def test_repository_control_package_passes(self) -> None:
        result = self.run_checker(MANUSCRIPT_ROOT)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CONTROL CHECK PASSED", result.stdout)

    def test_duplicate_stable_identifier_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.write_json(
                root / "controls" / "control-manifest.json",
                {
                    "schema_version": 1,
                    "control_set_id": "test-controls-v1",
                    "registers": [
                        {"name": "sample", "path": "controls/sample.json"}
                    ],
                },
            )
            self.write_json(
                root / "controls" / "sample.json",
                {
                    "schema_version": 1,
                    "register": "sample",
                    "records": [
                        {
                            "id": "duplicate-id",
                            "mandatory": True,
                            "review_state": "accepted",
                        },
                        {
                            "id": "duplicate-id",
                            "mandatory": False,
                            "review_state": "planned",
                        },
                    ],
                },
            )

            result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("duplicate-id", result.stdout)
        self.assertIn("duplicate identifier", result.stdout)
        self.assertIn("CONTROL CHECK FAILED", result.stdout)

    def test_unresolved_mandatory_record_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.write_json(
                root / "controls" / "control-manifest.json",
                {
                    "schema_version": 1,
                    "control_set_id": "test-controls-v1",
                    "registers": [
                        {"name": "sample", "path": "controls/sample.json"}
                    ],
                },
            )
            self.write_json(
                root / "controls" / "sample.json",
                {
                    "schema_version": 1,
                    "register": "sample",
                    "records": [
                        {
                            "id": "mandatory-decision",
                            "mandatory": True,
                            "review_state": "pending",
                        }
                    ],
                },
            )

            result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("mandatory-decision", result.stdout)
        self.assertIn("mandatory record is unresolved", result.stdout)
        self.assertIn("CONTROL CHECK FAILED", result.stdout)

    def test_unknown_mandatory_review_state_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.write_json(
                root / "controls" / "control-manifest.json",
                {
                    "schema_version": 1,
                    "control_set_id": "test-controls-v1",
                    "registers": [
                        {"name": "sample", "path": "controls/sample.json"}
                    ],
                },
            )
            self.write_json(
                root / "controls" / "sample.json",
                {
                    "schema_version": 1,
                    "register": "sample",
                    "records": [
                        {
                            "id": "misspelled-review-state",
                            "mandatory": True,
                            "review_state": "acceppted",
                        }
                    ],
                },
            )

            result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("misspelled-review-state", result.stdout)
        self.assertIn("unknown review_state", result.stdout)

    def test_missing_evidence_authority_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository_root = Path(temporary_directory) / "repository"
            root = repository_root / "manuscript"
            self.write_json(
                root / "controls" / "control-manifest.json",
                {
                    "schema_version": 1,
                    "control_set_id": "test-controls-v1",
                    "registers": [
                        {"name": "claims", "path": "controls/claims.json"}
                    ],
                },
            )
            self.write_json(
                root / "controls" / "claims.json",
                {
                    "schema_version": 1,
                    "register": "claims",
                    "records": [
                        {
                            "id": "claim-with-missing-authority",
                            "mandatory": True,
                            "review_state": "reviewed",
                            "authority": [
                                {
                                    "role": "canonical-theorem",
                                    "path": "research/theorems/missing.md",
                                }
                            ],
                        }
                    ],
                },
            )

            result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("research/theorems/missing.md", result.stdout)
        self.assertIn("authority path does not exist", result.stdout)

    def test_repository_escape_in_evidence_authority_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository_root = Path(temporary_directory) / "repository"
            root = repository_root / "manuscript"
            self.write_json(
                root / "controls" / "control-manifest.json",
                {
                    "schema_version": 1,
                    "control_set_id": "test-controls-v1",
                    "registers": [
                        {"name": "claims", "path": "controls/claims.json"}
                    ],
                },
            )
            self.write_json(
                root / "controls" / "claims.json",
                {
                    "schema_version": 1,
                    "register": "claims",
                    "records": [
                        {
                            "id": "claim-outside-repository",
                            "mandatory": True,
                            "review_state": "reviewed",
                            "authority": [
                                {
                                    "role": "canonical-theorem",
                                    "path": "../outside.md",
                                }
                            ],
                        }
                    ],
                },
            )
            (repository_root / "outside.md").write_text(
                "This file is outside the repository root used by the checker.\n",
                encoding="utf-8",
            )

            result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("claim-outside-repository", result.stdout)
        self.assertIn("escapes repository root", result.stdout)

    def test_thesis_profile_requires_every_control_register(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.write_json(
                root / "controls" / "control-manifest.json",
                {
                    "schema_version": 1,
                    "control_set_id": "incomplete-thesis-controls-v1",
                    "profile": "thesis-architecture-v1",
                    "registers": [
                        {"name": "sample", "path": "controls/sample.json"}
                    ],
                },
            )
            self.write_json(
                root / "controls" / "sample.json",
                {
                    "schema_version": 1,
                    "register": "sample",
                    "records": [],
                },
            )

            result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing required register", result.stdout)
        self.assertIn("architecture", result.stdout)

    def test_thesis_profile_rejects_incomplete_claim_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "manuscript"
            shutil.copytree(MANUSCRIPT_ROOT / "controls", root / "controls")
            claims_path = root / "controls" / "claims.json"
            claims = json.loads(claims_path.read_text(encoding="utf-8"))
            del claims["records"][0]["wording"]
            claims_path.write_text(
                json.dumps(claims, indent=2) + "\n", encoding="utf-8"
            )

            result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("claim-def-corrected-mean", result.stdout)
        self.assertIn("missing required field 'wording'", result.stdout)

    def test_thesis_profile_rejects_shell_missing_architecture_label(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "manuscript"
            shutil.copytree(MANUSCRIPT_ROOT / "controls", root / "controls")
            (root / "source").mkdir()
            (root / "source" / "thesis.tex").write_text(
                "\\chapter{Unrelated chapter}\n\\label{ch:unrelated}\n",
                encoding="utf-8",
            )

            result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("source shell missing architecture label", result.stdout)
        self.assertIn("ch:introduction", result.stdout)

    def test_thesis_profile_rejects_shell_title_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "manuscript"
            shutil.copytree(MANUSCRIPT_ROOT / "controls", root / "controls")
            shutil.copytree(MANUSCRIPT_ROOT / "source", root / "source")
            source_path = root / "source" / "thesis.tex"
            source = source_path.read_text(encoding="utf-8")
            source_path.write_text(
                source.replace(
                    "\\chapter{Introduction}",
                    "\\chapter{Drifted Introduction}",
                    1,
                ),
                encoding="utf-8",
            )

            result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("source shell missing architecture title", result.stdout)
        self.assertIn("Introduction", result.stdout)

    def test_thesis_profile_requires_every_canonical_theorem_in_claim_register(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository_root = Path(temporary_directory) / "repository"
            root = repository_root / "manuscript"
            shutil.copytree(MANUSCRIPT_ROOT / "controls", root / "controls")
            shutil.copytree(MANUSCRIPT_ROOT / "source", root / "source")
            shutil.copytree(
                REPOSITORY_ROOT / "research" / "definitions",
                repository_root / "research" / "definitions",
            )
            shutil.copytree(
                REPOSITORY_ROOT / "research" / "theorems",
                repository_root / "research" / "theorems",
            )
            claims_path = root / "controls" / "claims.json"
            claims = json.loads(claims_path.read_text(encoding="utf-8"))
            claims["records"] = [
                record
                for record in claims["records"]
                if record["id"] != "claim-thm-cash-timing-identity"
            ]
            claims_path.write_text(
                json.dumps(claims, indent=2) + "\n", encoding="utf-8"
            )

            result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "canonical authority is not registered: "
            "research/theorems/arbitrary-horizon-cash-timing-identity.md",
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
