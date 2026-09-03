#!/usr/bin/env python3
"""Build the thesis shell from its authoritative LaTeX source."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


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

    control_check = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().with_name("check_controls.py")),
            "--root",
            str(root),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if control_check.returncode:
        print(control_check.stdout, end="")
        print(control_check.stderr, end="")
        print("BUILD FAILED: manuscript controls are invalid")
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
