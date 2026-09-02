from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT_ROOT = REPOSITORY_ROOT / "manuscript"
BUILDER = MANUSCRIPT_ROOT / "build.py"


class ManuscriptBuildTests(unittest.TestCase):
    def test_candidate_can_build_template_conformant_manuscript_shell(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory)
            build = subprocess.run(
                [
                    sys.executable,
                    str(BUILDER),
                    "--root",
                    str(MANUSCRIPT_ROOT),
                    "--output-dir",
                    str(output_directory),
                ],
                cwd=REPOSITORY_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            pdf_path = output_directory / "thesis.pdf"
            self.assertTrue(pdf_path.is_file(), build.stdout + build.stderr)

            text = subprocess.run(
                ["pdftotext", str(pdf_path), "-"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            normalized_text = " ".join(text.split())
            normalized_upper = normalized_text.upper()
            self.assertIn("Minimal manuscript body", normalized_text)
            self.assertIn("Generated-asset placeholder", normalized_text)
            self.assertIn("Appendix", normalized_text)
            self.assertIn("BIBLIOGRAPHY", normalized_text)
            self.assertIn("Originality declaration placeholder", normalized_text)
            self.assertIn("LUCRARE DE DISERTA", normalized_upper)
            self.assertIn("MASTER", normalized_upper)
            self.assertIn("DISSERTATION", normalized_upper)
            self.assertIn("SINOPSIS", normalized_upper)
            self.assertIn("ABSTRACT", normalized_upper)
            self.assertIn(
                "COMPUTER SCIENCE AND ENGINEERING DEPARTMENT", normalized_upper
            )
            self.assertIn("public presentation and defense", normalized_text)
            self.assertIn("online hand-in", normalized_text)
            self.assertIn("similarity review", normalized_text)
            self.assertGreaterEqual(normalized_text.count("Figure 1.1"), 2)

            contract = json.loads(
                (MANUSCRIPT_ROOT / "contract" / "requirements.json").read_text(
                    encoding="utf-8"
                )
            )
            values = {
                requirement["id"]: requirement["value"]
                for requirement in contract["requirements"]
            }
            self.assertIn(
                values["institution_name"].split(" / ")[1].upper(), normalized_upper
            )
            self.assertIn(
                values["faculty_name"].split(" / ")[1].upper(), normalized_upper
            )
            self.assertIn(values["program_name"].upper(), normalized_upper)

            pdf_info = subprocess.run(
                ["pdfinfo", str(pdf_path)],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertIn(
                "Title:           Safe Adaptivity in Dollar-Cost Averaging:",
                pdf_info,
            )
            self.assertIn("Author:          [UNRESOLVED:", pdf_info)
            self.assertRegex(
                pdf_info,
                r"Page size:\s+595(?:\.\d+)? x 84[12](?:\.\d+)? pts \(A4\)",
            )

            bounding_boxes = subprocess.run(
                ["pdftotext", "-bbox", str(pdf_path), "-"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            body_start = re.search(
                r'<word xMin="([0-9.]+)" yMin="([0-9.]+)" '
                r'xMax="[0-9.]+" yMax="([0-9.]+)">Continuous</word>',
                bounding_boxes,
            )
            self.assertIsNotNone(body_start)
            self.assertAlmostEqual(float(body_start.group(1)), 72.0, delta=1.0)
            next_body_line = re.search(
                r'<word xMin="[0-9.]+" yMin="([0-9.]+)" '
                r'xMax="[0-9.]+" yMax="[0-9.]+">exercise</word>',
                bounding_boxes,
            )
            self.assertIsNotNone(next_body_line)
            self.assertAlmostEqual(
                float(next_body_line.group(1)) - float(body_start.group(2)),
                18.0,
                delta=0.75,
            )
            heading = re.search(
                r'<word xMin="[0-9.]+" yMin="([0-9.]+)" '
                r'xMax="[0-9.]+" yMax="([0-9.]+)">MINIMAL</word>',
                bounding_boxes,
            )
            self.assertIsNotNone(heading)
            self.assertGreater(
                float(heading.group(2)) - float(heading.group(1)),
                float(body_start.group(3)) - float(body_start.group(2)),
            )
            rendered_pages = re.findall(
                r"<page [^>]+>(.*?)</page>", bounding_boxes, flags=re.DOTALL
            )
            self.assertTrue(
                any(
                    ">SINOPSIS</word>" in page and ">ABSTRACT</word>" in page
                    for page in rendered_pages
                )
            )


if __name__ == "__main__":
    unittest.main()
