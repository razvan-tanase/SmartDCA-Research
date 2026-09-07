from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile


REPOSITORY = Path(__file__).resolve().parents[2]
MANUSCRIPT = REPOSITORY / "manuscript"


class AssemblyTests(unittest.TestCase):
    def test_package_binds_every_payload_and_rebuilds_from_export(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary = Path(temporary)
            output = temporary / "packages"
            command = [sys.executable, str(MANUSCRIPT / "assemble.py"), "--output-dir", str(output)]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            archive, = output.glob("*.zip")
            with zipfile.ZipFile(archive) as stream:
                manifest = json.loads(stream.read("manifest.json"))
                binding = manifest["binding"]
                self.assertEqual(binding["state"], "integrated-draft")
                self.assertFalse(binding["submission_gate_passed"])
                self.assertIn(b"candidate_official_name", stream.read("submission-check.txt"))
                self.assertEqual(set(binding["files"]), set(stream.namelist()) - {"manifest.json"})
                for name, expected in binding["files"].items():
                    self.assertEqual(hashlib.sha256(stream.read(name)).hexdigest(), expected, name)
                encoded = (json.dumps(binding, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
                self.assertTrue(manifest["identity"].endswith(hashlib.sha256(encoded).hexdigest()))
                exported = temporary / "exported"
                stream.extractall(exported)
                for info in stream.infolist():
                    os.chmod(exported / info.filename, (info.external_attr >> 16) & 0o777)
            second_output = temporary / "reproduced"
            second = subprocess.run(
                [sys.executable, str(exported / "source/manuscript/assemble.py"),
                 "--output-dir", str(second_output)], capture_output=True, text=True,
            )
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            reproduced, = second_output.glob("*.zip")
            self.assertEqual(archive.name, reproduced.name, "relocated clean export changed release identity")
            self.assertEqual(archive.read_bytes(), reproduced.read_bytes())
            executable = exported / "source/manuscript/assemble-clean.sh"
            executable.chmod(0o644)
            changed_mode = subprocess.run(
                [sys.executable, str(exported / "source/manuscript/assemble.py"),
                 "--output-dir", str(second_output)], capture_output=True, text=True,
            )
            self.assertEqual(changed_mode.returncode, 1)
            self.assertIn("exported source no longer matches", changed_mode.stdout)

    def test_integrated_audit_rejects_reader_visible_drift(self) -> None:
        mutations = ("unmapped-display", "duplicate-owner", "missing-restatement",
                     "stale-asset", "uncited-source", "body-placeholder")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "manuscript"
                shutil.copytree(MANUSCRIPT, root, ignore=shutil.ignore_patterns("build", "__pycache__"))
                for name in ("reproducibility", "reports", "experiments"):
                    (root.parent / name).symlink_to(REPOSITORY / name, target_is_directory=True)
                source = root / "source/thesis.tex"
                claims_path = root / "controls/claims.json"
                claims = json.loads(claims_path.read_text())
                expected = ""
                if mutation == "unmapped-display":
                    source.write_text(source.read_text().replace(r"\end{document}",
                        r"\begin{equation}1=1\label{eq:unowned}\end{equation}\end{document}"))
                    expected = "eq:unowned: expected one evidence owner"
                elif mutation == "duplicate-owner":
                    claims["records"][-1]["display_labels"] = ["eq:model-ledger"]
                    expected = "eq:model-ledger: expected one evidence owner"
                elif mutation == "missing-restatement":
                    claims["records"][0]["restatement_locations"].append("sec:absent")
                    expected = "missing location sec:absent"
                elif mutation == "stale-asset":
                    asset = root / "generated/historical-primary.tex"
                    asset.write_text(asset.read_text().replace("18", "19", 1))
                    expected = "generated asset differs: historical-primary.tex"
                elif mutation == "uncited-source":
                    bib = root / "bibliography/references.bib"
                    bib.write_text(bib.read_text() + "\n@book{absent, title={Uncited}}\n")
                    expected = "uncited bibliography entry: absent"
                else:
                    source.write_text(source.read_text().replace(r"\end{document}", "TODO\n" + r"\end{document}"))
                    expected = "unresolved manuscript content"
                claims_path.write_text(json.dumps(claims))
                result = subprocess.run(
                    [sys.executable, str(root / "assembly_controls.py"), "--root", str(root)],
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(expected, result.stdout)


if __name__ == "__main__":
    unittest.main()
