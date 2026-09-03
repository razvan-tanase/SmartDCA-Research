from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPOSITORY_ROOT / "manuscript" / "check_release.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


class ReleaseCheckTests(unittest.TestCase):
    def run_checker_at_root(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(root)],
            cwd=REPOSITORY_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def run_checker(self, fixture: str) -> subprocess.CompletedProcess[str]:
        return self.run_checker_at_root(FIXTURES / fixture)

    def copy_ready_candidate(self, temporary_directory: str) -> Path:
        candidate_root = Path(temporary_directory) / "candidate"
        shutil.copytree(FIXTURES / "ready-candidate", candidate_root)
        return candidate_root

    def test_complete_submission_candidate_passes(self) -> None:
        result = self.run_checker("ready-candidate")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RELEASE CHECK PASSED", result.stdout)

    def test_submission_candidate_is_rejected_when_required_decision_is_unresolved(self) -> None:
        result = self.run_checker("unresolved-decision")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("submission_date", result.stdout)
        self.assertIn("candidate", result.stdout)
        self.assertIn("RELEASE CHECK FAILED", result.stdout)

    def test_submission_candidate_is_rejected_when_source_contains_placeholder(self) -> None:
        result = self.run_checker("source-placeholder")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("source/main.tex", result.stdout)
        self.assertIn("UNRESOLVED", result.stdout)

    def test_submission_candidate_is_rejected_when_build_input_is_missing(self) -> None:
        result = self.run_checker("missing-build-input")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("bibliography/references.bib", result.stdout)
        self.assertIn("missing required build input", result.stdout)

    def test_submission_candidate_is_rejected_when_citation_is_undefined(self) -> None:
        result = self.run_checker("undefined-citation")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing-source", result.stdout)
        self.assertIn("undefined citation", result.stdout)

    def test_submission_candidate_is_rejected_when_verified_requirement_has_no_provenance(self) -> None:
        result = self.run_checker("missing-provenance")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("program_language", result.stdout)
        self.assertIn("missing authoritative source provenance", result.stdout)

    def test_submission_candidate_is_rejected_when_blocking_value_is_pending(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            candidate_root = self.copy_ready_candidate(temporary_directory)
            contract_path = candidate_root / "contract" / "requirements.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["requirements"][0].update({"status": "pending", "value": None})
            contract_path.write_text(
                json.dumps(contract, indent=2) + "\n", encoding="utf-8"
            )

            result = self.run_checker_at_root(candidate_root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("program_language", result.stdout)
        self.assertIn("not release-ready", result.stdout)

    def test_submission_candidate_is_rejected_when_mandatory_control_is_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            candidate_root = self.copy_ready_candidate(temporary_directory)
            contract_path = candidate_root / "contract" / "requirements.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["release_inputs"]["controls_manifest"] = (
                "controls/control-manifest.json"
            )
            contract_path.write_text(
                json.dumps(contract, indent=2) + "\n", encoding="utf-8"
            )
            controls = candidate_root / "controls"
            controls.mkdir(exist_ok=True)
            (controls / "control-manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "control_set_id": "release-controls-v1",
                        "registers": [
                            {"name": "sample", "path": "controls/sample.json"}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (controls / "sample.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "register": "sample",
                        "records": [
                            {
                                "id": "unresolved-release-control",
                                "mandatory": True,
                                "review_state": "pending",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_checker_at_root(candidate_root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("unresolved-release-control", result.stdout)
        self.assertIn("manuscript controls are invalid", result.stdout)
        self.assertIn("RELEASE CHECK FAILED", result.stdout)

    def test_submission_candidate_is_rejected_when_controls_manifest_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            candidate_root = self.copy_ready_candidate(temporary_directory)
            contract_path = candidate_root / "contract" / "requirements.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            del contract["release_inputs"]["controls_manifest"]
            contract_path.write_text(
                json.dumps(contract, indent=2) + "\n", encoding="utf-8"
            )

            result = self.run_checker_at_root(candidate_root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("controls_manifest must be declared", result.stdout)
        self.assertIn("manuscript controls are invalid", result.stdout)

    def test_submission_candidate_is_rejected_when_contract_mirror_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            candidate_root = self.copy_ready_candidate(temporary_directory)
            narrative_path = candidate_root / "contract" / "institutional-contract.md"
            narrative_path.write_text(
                narrative_path.read_text(encoding="utf-8") + "Changed without review.\n",
                encoding="utf-8",
            )

            result = self.run_checker_at_root(candidate_root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("contract mirror digest mismatch", result.stdout)

    def test_submission_candidate_is_rejected_when_machine_contract_changes_without_mirror_update(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            candidate_root = self.copy_ready_candidate(temporary_directory)
            contract_path = candidate_root / "contract" / "requirements.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["requirements"][0]["value"] = "French"
            contract_path.write_text(
                json.dumps(contract, indent=2) + "\n", encoding="utf-8"
            )

            result = self.run_checker_at_root(candidate_root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("machine requirements digest mismatch", result.stdout)

    def test_submission_candidate_is_rejected_when_bibliography_entry_is_unused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            candidate_root = self.copy_ready_candidate(temporary_directory)
            bibliography_path = candidate_root / "bibliography" / "references.bib"
            bibliography_path.write_text(
                bibliography_path.read_text(encoding="utf-8")
                + "\n@misc{unused-source,\n  title = {Unused source}\n}\n",
                encoding="utf-8",
            )

            result = self.run_checker_at_root(candidate_root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("unused-source", result.stdout)
        self.assertIn("unused bibliography entry", result.stdout)

    def test_citation_in_latex_comment_does_not_count_as_bibliography_use(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            candidate_root = self.copy_ready_candidate(temporary_directory)
            source_path = candidate_root / "source" / "main.tex"
            source_path.write_text(
                "% \\cite{official-program-page}\nNo active citation.\n",
                encoding="utf-8",
            )

            result = self.run_checker_at_root(candidate_root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("official-program-page", result.stdout)
        self.assertIn("unused bibliography entry", result.stdout)

    def test_machine_contract_captures_each_verified_narrative_rule(self) -> None:
        contract = json.loads(
            (REPOSITORY_ROOT / "manuscript" / "contract" / "requirements.json")
            .read_text(encoding="utf-8")
        )
        requirement_ids = {
            requirement["id"] for requirement in contract["requirements"]
        }

        self.assertTrue(
            {
                "public_defense",
                "evaluation_criteria",
                "registration_title_and_supervisor_fields",
                "template_cover_sequence",
                "bilingual_abstracts",
                "research_manuscript_structure",
                "figure_policy",
                "formula_policy",
                "table_policy",
                "bibliography_policy",
                "appendix_policy",
            }.issubset(requirement_ids)
        )

    def test_official_template_is_retained_at_its_recorded_digest(self) -> None:
        contract = json.loads(
            (REPOSITORY_ROOT / "manuscript" / "contract" / "requirements.json")
            .read_text(encoding="utf-8")
        )
        template_source = next(
            source
            for source in contract["sources"]
            if source["id"] == "acs-official-thesis-template-2018"
        )
        retained_path = REPOSITORY_ROOT / template_source["local_path"]

        self.assertTrue(retained_path.is_file())
        self.assertEqual(
            hashlib.sha256(retained_path.read_bytes()).hexdigest(),
            template_source["sha256"],
        )


if __name__ == "__main__":
    unittest.main()
