#!/usr/bin/env python3
"""Build the thesis shell from its authoritative LaTeX source."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_validation(command: list[str], failure_message: str) -> bool:
    """Run one fail-closed pre-build gate and forward useful diagnostics."""

    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True
    print(result.stdout, end="")
    print(result.stderr, end="")
    print(failure_message)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="manuscript project root (default: directory containing this script)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="derived-output directory (default: ROOT/build)",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    output_directory = (args.output_dir or root / "build").resolve()
    source = root / "source" / "thesis.tex"

    if not run_validation(
        [
            sys.executable,
            str(Path(__file__).resolve().with_name("check_controls.py")),
            "--root",
            str(root),
        ],
        "BUILD FAILED: manuscript controls are invalid",
    ):
        return 1

    manifest_path = root / "controls" / "control-manifest.json"
    try:
        control_profile = json.loads(manifest_path.read_text(encoding="utf-8")).get(
            "profile"
        )
    except (OSError, json.JSONDecodeError):
        control_profile = None
    if control_profile == "thesis-architecture-v1" and not run_validation(
        [
            sys.executable,
            str(
                Path(__file__).resolve().parents[1]
                / "reproducibility"
                / "literature_controls.py"
            ),
            "--repository-root",
            str(root.parent),
        ],
        "BUILD FAILED: DCA literature synthesis is invalid",
    ):
        return 1

    latexmk = shutil.which("latexmk")
    if latexmk is None:
        print("BUILD FAILED: latexmk is not installed")
        return 2
    if not source.is_file():
        print(f"BUILD FAILED: missing authoritative source {source}")
        return 2

    output_directory.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment.update(
        {
            "BIBINPUTS": str(root / "bibliography")
            + os.pathsep
            + environment.get("BIBINPUTS", ""),
            "FORCE_SOURCE_DATE": "1",
            "SOURCE_DATE_EPOCH": "1788220800",
            "TZ": "UTC",
        }
    )
    command = [
        latexmk,
        "-pdf",
        "-bibtex",
        "-cd",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        f"-outdir={output_directory}",
        str(source),
    ]
    result = subprocess.run(
        command,
        cwd=root,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        print("BUILD FAILED")
        print(result.stdout)
        print(result.stderr)
        return result.returncode

    pdf_path = output_directory / "thesis.pdf"
    if not pdf_path.is_file():
        print(f"BUILD FAILED: latexmk did not create {pdf_path}")
        return 2
    print(f"BUILD PASSED: {pdf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
