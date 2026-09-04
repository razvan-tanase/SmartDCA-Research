"""Shared fail-closed file loaders for manuscript evidence controls."""

from __future__ import annotations

import json
from pathlib import Path


def normalize_whitespace(text: str) -> str:
    """Case-fold text and collapse whitespace for prose-contract matching."""

    return " ".join(text.casefold().split())


def extract_latex_chapter(source: str, title: str) -> str:
    """Return one chapter body from a report-style LaTeX source."""

    marker = f"\\chapter{{{title}}}"
    start = source.find(marker)
    if start < 0:
        return ""
    remainder = source[start + len(marker) :]
    end = remainder.find("\\chapter{")
    return remainder if end < 0 else remainder[:end]


def index_records(document: dict[str, object]) -> dict[str, dict[str, object]]:
    """Index dictionary records by stable string identifier."""

    records = document.get("records", [])
    if not isinstance(records, list):
        return {}
    return {
        record["id"]: record
        for record in records
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }


def require_terms(
    text: str,
    terms: tuple[str, ...],
    label: str,
    errors: list[str],
) -> None:
    """Append one diagnostic for each required term absent from normalized text."""

    normalized_text = normalize_whitespace(text)
    for term in terms:
        if normalize_whitespace(term) not in normalized_text:
            errors.append(f"missing {label}: {term!r}")


def validate_repository_file(
    root: Path,
    identifier: str,
    relative_path: str,
    errors: list[str],
) -> None:
    """Require one authority path to stay inside the repository and name a file."""

    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        errors.append(f"{identifier}: authority path escapes repository")
        return
    if not candidate.is_file():
        errors.append(
            f"{identifier}: authority path does not exist: {relative_path}"
        )


def read_text(path: Path, errors: list[str]) -> str:
    """Read UTF-8 text, appending a diagnostic and returning empty on failure."""

    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"{path}: unreadable ({error})")
        return ""


def read_json_object(path: Path, errors: list[str]) -> dict[str, object]:
    """Read a JSON object, appending a diagnostic and returning empty on failure."""

    text = read_text(path, errors)
    if not text:
        return {}
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        errors.append(f"{path}: invalid JSON ({error})")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path}: expected a JSON object")
        return {}
    return value
