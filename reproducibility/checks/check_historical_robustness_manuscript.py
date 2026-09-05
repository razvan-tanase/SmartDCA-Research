"""Public-contract tests for the historical/robustness manuscript slice."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from reproducibility.historical_evaluation_assets import (
    PRIMARY_RUN_ID,
    ROBUSTNESS_RUN_ID,
    generate_historical_evaluation_assets,
)
from reproducibility.historical_evaluation_controls import (
    audit_historical_robustness_evaluation,
)


ROOT = Path(__file__).resolve().parents[2]
GENERATED_ASSETS = (
    "historical-primary.tex",
    "historical-mechanisms.tex",
    "historical-robustness.tex",
    "historical-supplementary.tex",
)


class HistoricalRobustnessManuscriptTest(unittest.TestCase):
    def test_historical_chapter_is_complete_and_traceable(self) -> None:
        receipt = audit_historical_robustness_evaluation(ROOT)

        self.assertEqual(receipt["status"], "passed")
        self.assertEqual(receipt["primary_run_id"], PRIMARY_RUN_ID)
        self.assertEqual(receipt["robustness_run_id"], ROBUSTNESS_RUN_ID)

    def test_committed_assets_regenerate_from_both_accepted_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory) / "generated"
            receipt = generate_historical_evaluation_assets(ROOT, output_directory)

            self.assertEqual(receipt["status"], "passed")
            self.assertEqual(receipt["primary_run_id"], PRIMARY_RUN_ID)
            self.assertEqual(receipt["robustness_run_id"], ROBUSTNESS_RUN_ID)
            self.assertEqual(receipt["primary_episode_count"], 1365)
            self.assertEqual(receipt["primary_confirmatory_cell_count"], 36)
            self.assertEqual(receipt["robustness_episode_count"], 1793)
            self.assertEqual(receipt["robustness_cell_count"], 810)
            self.assertEqual(tuple(receipt["asset_names"]), GENERATED_ASSETS)

            primary = (output_directory / "historical-primary.tex").read_text(
                encoding="utf-8"
            )
            mechanisms = (
                output_directory / "historical-mechanisms.tex"
            ).read_text(encoding="utf-8")
            robustness = (
                output_directory / "historical-robustness.tex"
            ).read_text(encoding="utf-8")
            supplementary = (
                output_directory / "historical-supplementary.tex"
            ).read_text(encoding="utf-8")

            for term in (
                r"\label{tab:historical-primary}",
                r"\label{fig:historical-primary-effects}",
                r"-4.593\%",
                r"-0.335\%",
                "one sealed 36-test H1/H2 family",
            ):
                self.assertIn(term, primary)
            for term in (
                r"\label{tab:historical-comparison-tiers}",
                r"\label{tab:historical-policy-mechanisms}",
                "18 positive / 18 negative",
                r"18.961\%",
            ):
                self.assertIn(term, mechanisms)
            for term in (
                r"\label{tab:registered-robustness}",
                r"\label{tab:historical-cost-robustness}",
                "40 / 8",
                "outside the current frictionless safety theorem",
            ):
                self.assertIn(term, robustness)
            for term in (
                r"\label{tab:historical-h1-cells}",
                r"\label{tab:historical-h2-cells}",
                r"\label{tab:historical-evidence-inventory}",
                "ordered overlapping starts",
                "restricted source observations are not redistributed",
            ):
                self.assertIn(term, supplementary)

            for asset_name in GENERATED_ASSETS:
                self.assertEqual(
                    (output_directory / asset_name).read_bytes(),
                    (ROOT / "manuscript/generated" / asset_name).read_bytes(),
                )

    def test_canonical_build_and_ci_run_the_historical_control(self) -> None:
        module = "reproducibility.checks.check_historical_robustness_manuscript"
        control = "historical_evaluation_controls.py"

        self.assertIn(
            control,
            (ROOT / "manuscript/build.py").read_text(encoding="utf-8"),
        )
        for path in (
            ROOT / ".github/workflows/reproducibility.yml",
            ROOT / "manuscript/verify-homebrew.sh",
            ROOT / "manuscript/README.md",
            ROOT / "README.md",
        ):
            self.assertIn(module, path.read_text(encoding="utf-8"), str(path))


if __name__ == "__main__":
    unittest.main()
