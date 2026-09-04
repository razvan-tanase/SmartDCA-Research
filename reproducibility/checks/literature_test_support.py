"""Shared fixture assembly for literature-synthesis public-contract tests."""

from __future__ import annotations

import shutil
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
COMMON_LITERATURE_SURFACE = (
    "manuscript/bibliography/references.bib",
    "manuscript/controls/claims.json",
    "manuscript/source/thesis.tex",
)


def copy_literature_surface(
    destination: Path,
    evidence_note_path: str,
) -> Path:
    """Copy one literature slice's public audit surface into a test repository."""

    for relative_path in (*COMMON_LITERATURE_SURFACE, evidence_note_path):
        source = REPOSITORY_ROOT / relative_path
        target = destination / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return destination
