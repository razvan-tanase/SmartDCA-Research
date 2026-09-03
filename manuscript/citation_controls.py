"""Shared parsers for manuscript LaTeX citations and BibTeX entry keys."""

from __future__ import annotations

import re


_LATEX_CITATION_PATTERN = re.compile(
    r"\\(?:[A-Za-z]*cite[A-Za-z]*)\*?"
    r"(?:\s*\[[^\]]*\]){0,2}\s*\{([^}]*)\}"
)
_BIBTEX_ENTRY_PATTERN = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")


def strip_latex_comments(source: str) -> str:
    """Remove unescaped percent comments from a LaTeX source string."""

    return re.sub(r"(?<!\\)%.*$", "", source, flags=re.MULTILINE)


def extract_latex_citation_keys(source: str) -> set[str]:
    """Return the non-wildcard keys cited by a LaTeX source string."""

    keys: set[str] = set()
    for group in _LATEX_CITATION_PATTERN.findall(strip_latex_comments(source)):
        keys.update(
            key
            for item in group.split(",")
            if (key := item.strip()) and key != "*"
        )
    return keys


def extract_bibtex_keys(source: str) -> set[str]:
    """Return entry keys declared by a BibTeX source string."""

    return set(_BIBTEX_ENTRY_PATTERN.findall(source))
