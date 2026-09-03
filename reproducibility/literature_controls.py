"""Deterministic controls for the DCA literature-synthesis manuscript slice."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manuscript.citation_controls import (  # noqa: E402
    extract_bibtex_keys,
    extract_latex_citation_keys,
)


REQUIRED_CLAIMS = {
    "claim-lit-dca-scope": "sec:lit-dca-scope",
    "claim-lit-adaptive-accumulation": "sec:lit-adaptive-accumulation",
    "claim-lit-online-decisions": "sec:lit-online-decisions",
    "claim-lit-safety-objectives": "sec:lit-safety-objectives",
    "claim-lit-project-boundary": "sec:lit-project-boundary",
}
EVIDENCE_NOTE = "research/notes/dca-adaptive-causal-safety-literature.md"
REQUIRED_NOTE_HEADINGS = (
    "## Search protocol",
    "## Inclusion and exclusion boundaries",
    "## Comparative synthesis",
    "## Claim-to-evidence map",
    "## Novelty and citation verdict",
)
REQUIRED_COMPARISON_COLUMNS = (
    "information timing",
    "funding",
    "comparator",
    "performance criterion",
    "guarantee type",
)
REQUIRED_DISTINCTIONS = (
    "lump-sum timing",
    "rebalancing",
    "retrospectively budget-matched",
    "individualized investment advice",
)
REQUIRED_CLAIM_MODES = ("universal", "expected", "probabilistic", "realized")
REQUIRED_MATERIAL_TERMS = (
    "sequential admissibility",
    "same-deposit",
    "cash-inclusive terminal wealth",
)


class LiteratureSynthesisError(ValueError):
    """Raised when the literature slice is incomplete or internally inconsistent."""


def _read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"{path}: unreadable ({error})")
        return ""


def _read_json(path: Path, errors: list[str]) -> dict[str, object]:
    text = _read_text(path, errors)
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


def audit_dca_literature_synthesis(repository_root: Path) -> dict[str, object]:
    """Validate the source, bibliography, evidence note, and claim register together."""

    root = repository_root.resolve()
    errors: list[str] = []
    note = _read_text(root / EVIDENCE_NOTE, errors)
    thesis = _read_text(root / "manuscript/source/thesis.tex", errors)
    bibliography = _read_text(
        root / "manuscript/bibliography/references.bib", errors
    )
    claims_document = _read_json(
        root / "manuscript/controls/claims.json", errors
    )

    records = claims_document.get("records", [])
    if not isinstance(records, list):
        errors.append("manuscript/controls/claims.json: records must be an array")
        records = []
    by_identifier = {
        record.get("id"): record
        for record in records
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }

    bibliography_keys = extract_bibtex_keys(bibliography)
    manuscript_citations = extract_latex_citation_keys(thesis)
    literature_keys: set[str] = set()

    for identifier, section_label in REQUIRED_CLAIMS.items():
        record = by_identifier.get(identifier)
        if not isinstance(record, dict):
            errors.append(f"missing literature claim record {identifier!r}")
            continue
        if record.get("entry_type") != "literature-positioning":
            errors.append(
                f"{identifier}: entry_type must be 'literature-positioning'"
            )
        if record.get("mandatory") is not True or record.get("review_state") != "reviewed":
            errors.append(f"{identifier}: literature claim must be mandatory and reviewed")
        expected_location = f"ch:literature/{section_label}"
        if record.get("manuscript_location") != expected_location:
            errors.append(
                f"{identifier}: manuscript_location must be {expected_location!r}"
            )
        for label in ("ch:literature", section_label):
            if f"\\label{{{label}}}" not in thesis:
                errors.append(f"{identifier}: manuscript is missing label {label!r}")
        authority = record.get("authority", [])
        authority_paths = {
            entry.get("path")
            for entry in authority
            if isinstance(entry, dict) and isinstance(entry.get("path"), str)
        } if isinstance(authority, list) else set()
        if EVIDENCE_NOTE not in authority_paths:
            errors.append(f"{identifier}: missing literature evidence-note authority")
        citation_keys = record.get("citation_keys", [])
        if not isinstance(citation_keys, list) or not citation_keys or not all(
            isinstance(key, str) and key for key in citation_keys
        ):
            errors.append(f"{identifier}: citation_keys must be a non-empty string array")
            continue
        for key in citation_keys:
            literature_keys.add(key)
            if key not in bibliography_keys:
                errors.append(f"{identifier}: undefined bibliography key {key!r}")
            if key not in manuscript_citations:
                errors.append(f"{identifier}: key {key!r} is not cited by the manuscript")
            if f"`{key}`" not in note:
                errors.append(f"{identifier}: evidence note does not name key {key!r}")
        if identifier not in note:
            errors.append(
                f"{EVIDENCE_NOTE}: missing claim-to-evidence identifier {identifier!r}"
            )

    for heading in REQUIRED_NOTE_HEADINGS:
        if heading not in note:
            errors.append(f"{EVIDENCE_NOTE}: missing heading {heading!r}")

    comparison_header = next(
        (
            line.lower()
            for line in note.splitlines()
            if line.lstrip().startswith("|")
            and all(column in line.lower() for column in REQUIRED_COMPARISON_COLUMNS)
        ),
        "",
    )
    if not comparison_header:
        errors.append(
            f"{EVIDENCE_NOTE}: missing the five-column strategy comparison contract"
        )

    thesis_lower = thesis.lower()
    for term in (*REQUIRED_DISTINCTIONS, *REQUIRED_CLAIM_MODES, *REQUIRED_MATERIAL_TERMS):
        if term not in thesis_lower:
            errors.append(f"manuscript/source/thesis.tex: missing required distinction {term!r}")

    note_lower = note.lower()
    if "not exhaustive" not in note_lower:
        errors.append(f"{EVIDENCE_NOTE}: search boundary must state that it is not exhaustive")
    if "does not establish novelty" not in note_lower:
        errors.append(f"{EVIDENCE_NOTE}: novelty verdict is not sufficiently bounded")

    if errors:
        raise LiteratureSynthesisError("\n".join(errors))

    return {
        "status": "passed",
        "literature_claim_count": len(REQUIRED_CLAIMS),
        "bibliography_key_count": len(literature_keys),
        "cited_key_count": len(literature_keys & manuscript_citations),
        "comparison_column_count": len(REQUIRED_COMPARISON_COLUMNS),
        "evidence_note": EVIDENCE_NOTE,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (default: parent of the reproducibility package)",
    )
    args = parser.parse_args()
    try:
        receipt = audit_dca_literature_synthesis(args.repository_root)
    except LiteratureSynthesisError as error:
        print("DCA LITERATURE SYNTHESIS CHECK FAILED")
        for item in str(error).splitlines():
            print(f"- {item}")
        return 1
    print(
        "DCA LITERATURE SYNTHESIS CHECK PASSED: "
        f"{receipt['literature_claim_count']} claims, "
        f"{receipt['bibliography_key_count']} cited sources"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
