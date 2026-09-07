#!/usr/bin/env python3
"""Export the thesis and its TeX inputs as a portable editor-upload ZIP."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import zipfile


def export_latex(root: Path, output: Path) -> None:
    """Relocate source-relative inputs without changing their retained bytes."""
    root = root.resolve()
    source = root / "source/thesis.tex"
    members: dict[str, bytes] = {}

    def relocate(match: re.Match[str]) -> str:
        command, reference = match.group("command", "path")
        suffix = ".bib" if command == "bibliography" else ""
        directory = root / "bibliography" if command == "bibliography" else source.parent
        dependency = (directory / (reference + suffix)).resolve()
        relative = dependency.relative_to(root)
        if relative.parts[0] == "source":
            relative = relative.relative_to("source")
        destination = relative.as_posix()
        members[destination] = dependency.read_bytes()
        target = destination.removesuffix(suffix) if suffix else destination
        return match.group(0).replace("{" + reference + "}", "{" + target + "}")

    # The authoritative source uses literal paths for these three commands;
    # generated fragments have no further file inputs. Compile the relocated
    # project in the build tests to catch any new dependency convention.
    tex = re.sub(
        r"\\(?P<command>input|includegraphics|bibliography)"
        r"(?:\[[^\]]*\])?\{(?P<path>[^}]+)\}",
        relocate,
        source.read_text(encoding="utf-8"),
    )
    # Replace the checkout-specific build comments in this derived copy only.
    tex = tex[tex.index(r"\documentclass"):]
    members["thesis.tex"] = (
        "% Portable copy. Compile with: latexmk -pdf -bibtex thesis.tex\n" + tex
    ).encode("utf-8")
    members["README.txt"] = (
        "SmartDCA thesis: portable LaTeX project\n\n"
        "Upload this entire ZIP to your LaTeX editor. Select thesis.tex as the\n"
        "main document and pdfLaTeX as the compiler. Keep assets/, generated/,\n"
        "and bibliography/ alongside thesis.tex. Recompile from scratch if an\n"
        "earlier upload left failed auxiliary files.\n\n"
        "Local build from the extracted directory:\n"
        "  latexmk -pdf -bibtex thesis.tex\n"
        "Or run pdflatex thesis.tex, bibtex thesis, then pdflatex thesis.tex\n"
        "twice. References and citations resolve after the final passes.\n\n"
        "This is a derived integrated draft, not a submission approval.\n"
        "Make lasting edits in manuscript/source/thesis.tex in the repository\n"
        "and regenerate with python manuscript/export_latex.py. The canonical\n"
        "validated build remains python manuscript/build.py.\n"
    ).encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as stream:
        for name, data in sorted(members.items()):
            info = zipfile.ZipInfo(name, (2026, 9, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            stream.writestr(info, data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.root / "build/smartdca-thesis-latex.zip"
    try:
        export_latex(args.root, output)
    except (OSError, ValueError) as error:
        print(f"LATEX EXPORT FAILED: {error}")
        return 1
    print(f"LATEX PROJECT EXPORTED: {output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
