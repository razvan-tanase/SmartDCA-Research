"""Public-contract tests for the deterministic/stochastic manuscript slice."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from reproducibility.synthetic_evaluation_assets import (
    generate_synthetic_evaluation_assets,
)
from reproducibility.synthetic_evaluation_controls import (
    audit_deterministic_stochastic_evaluation,
)


ROOT = Path(__file__).resolve().parents[2]
GENERATED_ASSETS = (
    "deterministic-evaluation.tex",
    "stochastic-evaluation.tex",
    "stochastic-mechanisms.tex",
    "synthetic-supplementary.tex",
)


class DeterministicStochasticEvaluationTest(unittest.TestCase):
    def test_stochastic_tables_report_dispersion_and_define_every_comparison(self) -> None:
        primary = (
            ROOT / "manuscript/generated/stochastic-evaluation.tex"
        ).read_text(encoding="utf-8")
        exploratory = (
            ROOT / "manuscript/generated/synthetic-supplementary.tex"
        ).read_text(encoding="utf-8")

        for asset in (primary, exploratory):
            self.assertIn(
                r"Comparison & $N$ & Median & Seed range & 5\% downside & Worst",
                asset,
            )
            for definition in (
                "C--D is corrected guarded versus DCA",
                "C--N is corrected guarded versus neutral guarded",
                "N--D is neutral guarded versus DCA",
                "Seed range is the minimum-to-maximum interval",
                "uses its named right-hand policy as denominator",
            ):
                self.assertIn(definition, asset)

    def test_lambda_one_collapse_has_a_chapter_specific_claim_record(self) -> None:
        claims = json.loads(
            (ROOT / "manuscript/controls/claims.json").read_text(encoding="utf-8")
        )["records"]
        matching = [
            record
            for record in claims
            if record.get("id")
            == "claim-empirical-synthetic-lambda-one-collapse"
        ]

        self.assertEqual(len(matching), 1)
        self.assertEqual(
            matching[0]["manuscript_location"],
            "ch:synthetic-results/sec:safety-checks",
        )

    def test_deterministic_assets_finish_before_following_interpretation(self) -> None:
        source = (ROOT / "manuscript/source/thesis.tex").read_text(encoding="utf-8")

        asset_input = source.index(
            r"\input{../generated/deterministic-evaluation.tex}"
        )
        float_barrier = source.index(r"\FloatBarrier", asset_input)
        following_interpretation = source.index("On the monotone rise", asset_input)

        self.assertIn(r"\usepackage{placeins}", source)
        self.assertLess(asset_input, float_barrier)
        self.assertLess(float_barrier, following_interpretation)

    def test_signed_dollar_interpretation_keeps_compound_terms_intact(self) -> None:
        source = (ROOT / "manuscript/source/thesis.tex").read_text(encoding="utf-8")

        self.assertIn("negative mean terminal-wealth difference", source)
        self.assertIn("positive mean terminal-wealth difference", source)

    def test_generated_mechanisms_render_in_their_owning_section(self) -> None:
        source = (ROOT / "manuscript/source/thesis.tex").read_text(encoding="utf-8")

        section_start = source.index(r"\label{sec:synthetic-mechanisms}")
        asset_input = source.index(r"\input{../generated/stochastic-mechanisms.tex}")
        section_end = source.index(r"\section{Frictionless Validation", section_start)
        self.assertLess(section_start, asset_input)
        self.assertLess(asset_input, section_end)

    def test_repository_manuscript_slice_is_complete_and_traceable(self) -> None:
        receipt = audit_deterministic_stochastic_evaluation(ROOT)

        self.assertEqual(receipt["status"], "passed")

    def test_evaluation_audit_runs_through_the_build_script_entry_point(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "reproducibility/synthetic_evaluation_controls.py"),
                "--repository-root",
                str(ROOT),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SYNTHETIC EVALUATION AUDIT PASSED", result.stdout)

    def test_canonical_build_and_workflow_run_the_evaluation_audit(self) -> None:
        build_source = (ROOT / "manuscript/build.py").read_text(encoding="utf-8")
        workflow = (ROOT / ".github/workflows/reproducibility.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn('"synthetic_evaluation_controls.py"', build_source)
        self.assertIn(
            "python -m unittest "
            "reproducibility.checks.check_deterministic_stochastic_evaluation",
            workflow,
        )

    def test_committed_manuscript_assets_regenerate_byte_for_byte(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory) / "generated"
            receipt = generate_synthetic_evaluation_assets(ROOT, output_directory)

            self.assertEqual(receipt["status"], "passed")
            self.assertEqual(receipt["deterministic_generated_path_count"], 18)
            self.assertEqual(receipt["deterministic_excluded_path_count"], 3)
            self.assertEqual(receipt["stochastic_generated_path_count"], 90)
            self.assertEqual(receipt["stochastic_excluded_path_count"], 0)
            self.assertEqual(receipt["stochastic_primary_seed_count"], 3)
            self.assertEqual(
                receipt["deterministic_run_id"],
                "smartdca-deterministic-v1-"
                "80e0f231729885a672c4f4162a35516f3cd257aa6dc71fafc01d14b03cabe9db",
            )
            self.assertEqual(
                receipt["stochastic_run_id"],
                "smartdca-stochastic-v1-"
                "78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25",
            )
            self.assertEqual(tuple(receipt["asset_names"]), GENERATED_ASSETS)
            deterministic_asset = (
                output_directory / "deterministic-evaluation.tex"
            ).read_text(encoding="utf-8")
            stochastic_asset = (
                output_directory / "stochastic-evaluation.tex"
            ).read_text(encoding="utf-8")
            mechanism_asset = (
                output_directory / "stochastic-mechanisms.tex"
            ).read_text(encoding="utf-8")
            supplementary_asset = (
                output_directory / "synthetic-supplementary.tex"
            ).read_text(encoding="utf-8")
            for term in (
                r"\label{tab:deterministic-primary}",
                r"\label{fig:deterministic-layers}",
                r"-4.712\%",
                r"+26.105\%",
            ):
                self.assertIn(term, deterministic_asset)
            for term in (
                r"\label{tab:stochastic-primary}",
                r"-0.269\%",
                r"+0.111\%",
            ):
                self.assertIn(term, stochastic_asset)
            for term in (
                r"\label{fig:stochastic-attribution}",
                r"\label{tab:stochastic-mechanisms}",
                r"\makebox[56mm][r]",
            ):
                self.assertIn(term, mechanism_asset)
            for term in (
                r"\label{tab:deterministic-coverage-ranges}",
                r"\label{tab:stochastic-sensitivity}",
                "18 fixed paths",
                "three saved seeds",
            ):
                self.assertIn(term, supplementary_asset)
            for asset_name in GENERATED_ASSETS:
                self.assertEqual(
                    (output_directory / asset_name).read_bytes(),
                    (ROOT / "manuscript/generated" / asset_name).read_bytes(),
                )


if __name__ == "__main__":
    unittest.main()
