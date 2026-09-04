"""Shared fail-closed file loaders for manuscript evidence controls."""

from __future__ import annotations

import json
from pathlib import Path


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
