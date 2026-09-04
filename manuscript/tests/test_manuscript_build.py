from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT_ROOT = REPOSITORY_ROOT / "manuscript"
BUILDER = MANUSCRIPT_ROOT / "build.py"


class ManuscriptBuildTests(unittest.TestCase):
    def test_invalid_controls_stop_build_before_latex(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            controls = root / "controls"
            controls.mkdir()
            (controls / "control-manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "control_set_id": "invalid-controls-v1",
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
                                "id": "unresolved-build-control",
                                "mandatory": True,
                                "review_state": "pending",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            build = subprocess.run(
                [
                    sys.executable,
                    str(BUILDER),
                    "--root",
                    str(root),
                    "--output-dir",
                    str(root / "build"),
                ],
                cwd=REPOSITORY_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(build.returncode, 1, build.stdout + build.stderr)
        self.assertIn("unresolved-build-control", build.stdout)
        self.assertIn("BUILD FAILED: manuscript controls are invalid", build.stdout)
        self.assertNotIn("latexmk", build.stdout)

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
            for title in (
                "Introduction",
                "Literature and Research Positioning",
                "Financial Model and Corrected Signal Foundations",
                "Causal Impossibility and Safety Architecture",
                "Exact Performance Boundaries",
                "Empirical Methodology and Reproducibility",
                "Deterministic and Stochastic Evaluation",
                "Historical Evaluation and Robustness",
                "Safety, Adaptivity, and Limitations",
                "Conclusions",
                "Mathematical Proofs",
                "Exact Performance Cases and Witnesses",
                "Empirical Protocols and Statistical Controls",
                "Reproducibility and Artifact Provenance",
                "Supplementary Tables and Figures",
            ):
                self.assertIn(title, normalized_text)
            self.assertIn(
                "universal pathwise dominance forces the strategy to purchase exactly as DCA",
                normalized_text,
            )
            self.assertIn(
                "incremental value from the corrected-mean signal is not confirmed",
                normalized_text,
            )
            self.assertIn(
                "The present comparison instead models recurring investment",
                normalized_text,
            )
            self.assertIn(
                "A universal pathwise ratio, an expected-utility comparison, a probabilistic shortfall statement, and a realized backtest gap",
                normalized_text,
            )
            self.assertIn(
                "cash-inclusive terminal wealth values both the asset units and the cash deliberately left uninvested",
                normalized_text,
            )
            self.assertIn(
                "The thesis therefore calls the unverified object the out quasi-Gini functional",
                normalized_text,
            )
            self.assertIn(
                "The relevant families are nested specializations, not interchangeable names",
                normalized_text,
            )
            self.assertIn(
                "The corrected construction is not a new general mean class",
                normalized_text,
            )
            self.assertIn(
                "a non-power transform is homogeneous only on the transform-independent",
                normalized_text,
            )
            self.assertIn(
                "The financial comparison is fixed before the specialized mean theory is used",
                normalized_text,
            )
            self.assertIn(
                "DCA receives the same deposit sequence and the same evaluation horizon",
                normalized_text,
            )
            self.assertIn(
                "Average acquisition cost is therefore an accounting quantity, not a budget-equivalent performance criterion",
                normalized_text,
            )
            self.assertIn(
                "The normalized lagged reference supplies a causal signal, not a safety guarantee",
                normalized_text,
            )
            self.assertIn(
                "No economically distinct policy can be weakly better everywhere and strictly better somewhere",
                normalized_text,
            )
            self.assertIn(
                "The corrected-mean score is only the discretionary selector",
                normalized_text,
            )
            self.assertIn(
                "Net-of-cost results are finite empirical robustness evidence outside the current safety theorem",
                normalized_text,
            )
            self.assertIn(
                "Proof of the Source-Functional Classification",
                normalized_text,
            )
            self.assertIn(
                "Proof of the Homogeneity Characterization",
                normalized_text,
            )
            self.assertIn(
                "Proof of the Causal DCA Impossibility",
                normalized_text,
            )
            self.assertIn(
                "Proof of the Epsilon-DCA Guardrail",
                normalized_text,
            )
            self.assertIn("Mandatory safety branch", normalized_text)
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
            self.assertGreaterEqual(normalized_text.count("Figure 4.1"), 2)

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

            layout_path = output_directory / "layout.xml"
            subprocess.run(
                [
                    "pdftohtml",
                    "-xml",
                    "-hidden",
                    "-zoom",
                    "1.5",
                    str(pdf_path),
                    str(layout_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            layout = ET.parse(layout_path).getroot()
            font_sizes = {
                font.attrib["id"]: int(font.attrib["size"])
                for font in layout.iter("fontspec")
            }
            introduction_page = next(
                page
                for page in layout.iter("page")
                if any(
                    "".join(text.itertext()) == "INTRODUCTION"
                    for text in page.iter("text")
                )
            )
            heading = next(
                text
                for text in introduction_page.iter("text")
                if "".join(text.itertext()) == "INTRODUCTION"
            )
            heading_size = font_sizes[heading.attrib["font"]]
            body_line = min(
                (
                    text
                    for text in introduction_page.iter("text")
                    if float(text.attrib["top"]) > float(heading.attrib["top"])
                    and font_sizes[text.attrib["font"]] < heading_size
                ),
                key=lambda text: float(text.attrib["top"]),
            )
            next_body_line = min(
                (
                    text
                    for text in introduction_page.iter("text")
                    if float(text.attrib["top"]) > float(body_line.attrib["top"])
                    and text.attrib["font"] == body_line.attrib["font"]
                ),
                key=lambda text: float(text.attrib["top"]),
            )
            self.assertAlmostEqual(
                float(body_line.attrib["left"]) / 1.5,
                72.0,
                delta=1.0,
            )
            self.assertAlmostEqual(
                (float(next_body_line.attrib["top"]) - float(body_line.attrib["top"]))
                / 1.5,
                18.0,
                delta=0.75,
            )
            self.assertGreater(
                heading_size,
                font_sizes[body_line.attrib["font"]],
            )
            self.assertTrue(
                any(
                    {"SINOPSIS", "ABSTRACT"}.issubset(
                        {"".join(text.itertext()) for text in page.iter("text")}
                    )
                    for page in layout.iter("page")
                )
            )


if __name__ == "__main__":
    unittest.main()
