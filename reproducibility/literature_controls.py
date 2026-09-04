"""Deterministic controls for the thesis literature-synthesis slices."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manuscript.citation_controls import (  # noqa: E402
    extract_bibtex_keys,
    extract_latex_citation_keys,
)


@dataclass(frozen=True)
class LiteratureSliceRequirements:
    """Declarative traceability contract for one manuscript literature slice."""

    claim_sections: Mapping[str, str]
    evidence_note_path: str
    required_note_headings: tuple[str, ...]
    required_manuscript_terms: tuple[str, ...]
    missing_manuscript_term_label: str
    required_comparison_columns: tuple[str, ...] = ()
    citations_must_be_section_local: bool = False
    conservative_novelty_statement: str | None = None
    section_required_terms: tuple[tuple[str, tuple[str, ...]], ...] = ()
    claim_required_terms: tuple[tuple[str, str, tuple[str, ...]], ...] = ()


DCA_LITERATURE_REQUIREMENTS = LiteratureSliceRequirements(
    claim_sections={
        "claim-lit-dca-scope": "sec:lit-dca-scope",
        "claim-lit-adaptive-accumulation": "sec:lit-adaptive-accumulation",
        "claim-lit-online-decisions": "sec:lit-online-decisions",
        "claim-lit-safety-objectives": "sec:lit-safety-objectives",
        "claim-lit-project-boundary": "sec:lit-project-boundary",
    },
    evidence_note_path="research/notes/dca-adaptive-causal-safety-literature.md",
    required_note_headings=(
        "## Search protocol",
        "## Inclusion and exclusion boundaries",
        "## Comparative synthesis",
        "## Claim-to-evidence map",
        "## Novelty and citation verdict",
    ),
    required_manuscript_terms=(
        "lump-sum timing",
        "rebalancing",
        "retrospectively budget-matched",
        "individualized investment advice",
        "universal",
        "expected",
        "probabilistic",
        "realized",
        "sequential admissibility",
        "same-deposit",
        "cash-inclusive terminal wealth",
    ),
    missing_manuscript_term_label="required distinction",
    required_comparison_columns=(
        "information timing",
        "funding",
        "comparator",
        "performance criterion",
        "guarantee type",
    ),
)

CORRECTED_MEAN_LITERATURE_REQUIREMENTS = LiteratureSliceRequirements(
    claim_sections={
        "claim-lit-mean-source-functional": "sec:lit-mean-source-functional",
        "claim-lit-mean-generalized-roots": "sec:lit-mean-generalized-roots",
        "claim-lit-mean-family-identification": "sec:lit-mean-family-identification",
        "claim-lit-mean-property-boundaries": "sec:lit-mean-property-boundaries",
        "claim-lit-mean-contribution-boundary": "sec:lit-mean-contribution-boundary",
    },
    evidence_note_path="research/notes/corrected-mean-prior-theory-literature.md",
    required_note_headings=(
        "## Search protocol and limits",
        "## Primary-source coverage",
        "## Property boundaries",
        "## Claim-to-evidence map",
        "## Citation and novelty verdict",
    ),
    required_manuscript_terms=(
        "out quasi-gini functional",
        "weighted bajraktarevi",
        "weighted gini",
        "beckenbach--gini--lehmer",
        "weighted lehmer mean",
        "continuity",
        "homogeneity",
        "coordinatewise monotonicity",
        "transform-independent",
        "correction",
        "classification",
        "characterization",
        "prior theory",
    ),
    missing_manuscript_term_label="corrected-mean boundary",
    citations_must_be_section_local=True,
    conservative_novelty_statement="is not a new general mean class",
    section_required_terms=(
        (
            "sec:lit-mean-source-functional",
            (
                "finite positive inputs",
                "positive finite transform",
                r"\delta=\alpha-\beta\ne0",
            ),
        ),
        (
            "sec:lit-mean-family-identification",
            (r"\mathrm{out}}(u;w)", "positive external weights"),
        ),
    ),
)

METHODOLOGY_LITERATURE_REQUIREMENTS = LiteratureSliceRequirements(
    claim_sections={
        "claim-lit-method-registration": "sec:lit-method-registration",
        "claim-lit-method-overlap-resampling": (
            "sec:lit-method-overlap-resampling"
        ),
        "claim-lit-method-multiplicity-reporting": (
            "sec:lit-method-multiplicity-reporting"
        ),
        "claim-lit-method-computational-reproducibility": (
            "sec:lit-method-computational-reproducibility"
        ),
        "claim-lit-method-provenance-release": (
            "sec:lit-method-provenance-release"
        ),
    },
    evidence_note_path=(
        "research/notes/"
        "reproducible-computational-finance-statistical-methodology.md"
    ),
    required_note_headings=(
        "## Search protocol and limits",
        "## Authoritative source coverage",
        "## Statistical-method synthesis",
        "## Reproducibility and provenance synthesis",
        "## Claim-to-evidence map",
        "## Citation and statistical-language verdict",
    ),
    required_manuscript_terms=(
        "outcome-blind",
        "confirmatory",
        "exploratory",
        "descriptive robustness",
        "overlapping episodes",
        "circular moving-block bootstrap",
        "dependence-aware uncertainty",
        "does not create causal identification",
        "holm",
        "family-wise error",
        "inferential unit",
        "effect sizes",
        "deterministic regeneration",
        "independent reconciliation",
        "provider-data receipt",
        "public redistribution",
        "software engineering",
        "financial evidence",
    ),
    missing_manuscript_term_label="methodological boundary",
    citations_must_be_section_local=True,
    section_required_terms=(
        (
            "sec:lit-method-registration",
            (
                "before confirmatory outcome access",
                "descriptive robustness",
                "not a preregistration deposited in a third-party registry",
            ),
        ),
        (
            "sec:lit-method-overlap-resampling",
            (
                "ordered monthly episode start",
                "does not create causal identification",
            ),
        ),
        (
            "sec:lit-method-multiplicity-reporting",
            (
                "family-wise error",
                "effect sizes",
                "inferential unit",
            ),
        ),
        (
            "sec:lit-method-computational-reproducibility",
            (
                "deterministic regeneration",
                "independent reconciliation",
                "it is not independent-data replication",
            ),
        ),
        (
            "sec:lit-method-provenance-release",
            (
                "provider-data receipt",
                "public redistribution",
                "do not by themselves grant public redistribution",
                "does not establish a financial result",
            ),
        ),
    ),
    claim_required_terms=(
        (
            "claim-lit-method-multiplicity-reporting",
            "wording",
            (
                "treats ordered rolling starts as the sampling units and "
                "consecutive circular blocks as the resampling units",
            ),
        ),
        (
            "claim-lit-method-multiplicity-reporting",
            "scope",
            (
                "the family-wise error guarantee is conditional on valid "
                "cellwise unadjusted p-values",
            ),
        ),
    ),
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


def _latex_section_after_label(source: str, label: str) -> str:
    """Return one labelled LaTeX section, stopping at the next heading."""

    marker = f"\\label{{{label}}}"
    marker_position = source.find(marker)
    if marker_position < 0:
        return ""
    section = source[marker_position + len(marker) :]
    heading_positions = [
        position
        for heading in ("\\subsection{", "\\section{", "\\chapter{")
        if (position := section.find(heading)) >= 0
    ]
    if heading_positions:
        return section[: min(heading_positions)]
    return section


def _audit_literature_slice(
    repository_root: Path,
    requirements: LiteratureSliceRequirements,
) -> dict[str, object]:
    """Validate one literature slice across its manuscript and evidence surfaces."""

    root = repository_root.resolve()
    errors: list[str] = []
    note = _read_text(root / requirements.evidence_note_path, errors)
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

    for identifier, section_label in requirements.claim_sections.items():
        record = by_identifier.get(identifier)
        if not isinstance(record, dict):
            errors.append(f"missing literature claim record {identifier!r}")
            continue
        if record.get("entry_type") != "literature-positioning":
            errors.append(
                f"{identifier}: entry_type must be 'literature-positioning'"
            )
        if (
            record.get("mandatory") is not True
            or record.get("review_state") != "reviewed"
        ):
            errors.append(
                f"{identifier}: literature claim must be mandatory and reviewed"
            )
        expected_location = f"ch:literature/{section_label}"
        if record.get("manuscript_location") != expected_location:
            errors.append(
                f"{identifier}: manuscript_location must be {expected_location!r}"
            )
        for label in ("ch:literature", section_label):
            if f"\\label{{{label}}}" not in thesis:
                errors.append(f"{identifier}: manuscript is missing label {label!r}")
        section_citations = (
            extract_latex_citation_keys(
                _latex_section_after_label(thesis, section_label)
            )
            if requirements.citations_must_be_section_local
            else None
        )
        authority = record.get("authority", [])
        authority_paths = (
            {
                entry.get("path")
                for entry in authority
                if isinstance(entry, dict) and isinstance(entry.get("path"), str)
            }
            if isinstance(authority, list)
            else set()
        )
        if requirements.evidence_note_path not in authority_paths:
            errors.append(f"{identifier}: missing literature evidence-note authority")
        citation_keys = record.get("citation_keys", [])
        if not isinstance(citation_keys, list) or not citation_keys or not all(
            isinstance(key, str) and key for key in citation_keys
        ):
            errors.append(
                f"{identifier}: citation_keys must be a non-empty string array"
            )
            continue
        for key in citation_keys:
            literature_keys.add(key)
            if key not in bibliography_keys:
                errors.append(f"{identifier}: undefined bibliography key {key!r}")
            if key not in manuscript_citations:
                errors.append(
                    f"{identifier}: key {key!r} is not cited by the manuscript"
                )
            elif section_citations is not None and key not in section_citations:
                errors.append(
                    f"{identifier}: key {key!r} is not cited in manuscript section "
                    f"{section_label!r}"
                )
            if f"`{key}`" not in note:
                errors.append(f"{identifier}: evidence note does not name key {key!r}")
        if identifier not in note:
            errors.append(
                f"{requirements.evidence_note_path}: missing claim-to-evidence "
                f"identifier {identifier!r}"
            )

    for heading in requirements.required_note_headings:
        if heading not in note:
            errors.append(
                f"{requirements.evidence_note_path}: missing heading {heading!r}"
            )

    comparison_header = next(
        (
            line.lower()
            for line in note.splitlines()
            if line.lstrip().startswith("|")
            and all(
                column in line.lower()
                for column in requirements.required_comparison_columns
            )
        ),
        "",
    )
    if requirements.required_comparison_columns and not comparison_header:
        errors.append(
            f"{requirements.evidence_note_path}: missing the five-column "
            "strategy comparison contract"
        )

    thesis_lower = " ".join(thesis.lower().split())
    for term in requirements.required_manuscript_terms:
        if term not in thesis_lower:
            errors.append(
                "manuscript/source/thesis.tex: missing "
                f"{requirements.missing_manuscript_term_label} {term!r}"
            )

    for section_label, required_terms in requirements.section_required_terms:
        section_lower = " ".join(
            _latex_section_after_label(thesis, section_label).lower().split()
        )
        for term in required_terms:
            if term not in section_lower:
                errors.append(
                    "manuscript/source/thesis.tex: section "
                    f"{section_label!r} is missing "
                    f"{requirements.missing_manuscript_term_label} {term!r}"
                )

    for identifier, field, required_terms in requirements.claim_required_terms:
        record = by_identifier.get(identifier)
        if not isinstance(record, dict):
            continue
        field_value = record.get(field)
        normalized_value = (
            " ".join(field_value.lower().split())
            if isinstance(field_value, str)
            else ""
        )
        for term in required_terms:
            if term not in normalized_value:
                errors.append(
                    f"{identifier}: {field} is missing required claim term {term!r}"
                )

    if (
        requirements.conservative_novelty_statement is not None
        and requirements.conservative_novelty_statement not in thesis_lower
    ):
        errors.append(
            "manuscript/source/thesis.tex: missing conservative novelty boundary"
        )

    note_lower = note.lower()
    if "not exhaustive" not in note_lower:
        errors.append(
            f"{requirements.evidence_note_path}: search boundary must state that "
            "it is not exhaustive"
        )
    if "does not establish novelty" not in note_lower:
        errors.append(
            f"{requirements.evidence_note_path}: novelty verdict is not "
            "sufficiently bounded"
        )

    if errors:
        raise LiteratureSynthesisError("\n".join(errors))

    receipt: dict[str, object] = {
        "status": "passed",
        "literature_claim_count": len(requirements.claim_sections),
        "bibliography_key_count": len(literature_keys),
        "cited_key_count": len(literature_keys & manuscript_citations),
        "evidence_note": requirements.evidence_note_path,
    }
    if requirements.required_comparison_columns:
        receipt["comparison_column_count"] = len(
            requirements.required_comparison_columns
        )
    return receipt


def audit_dca_literature_synthesis(repository_root: Path) -> dict[str, object]:
    """Validate the DCA/adaptive/causal-safety literature slice."""

    return _audit_literature_slice(repository_root, DCA_LITERATURE_REQUIREMENTS)


def audit_corrected_mean_literature_synthesis(
    repository_root: Path,
) -> dict[str, object]:
    """Validate the corrected-mean prior-theory literature slice."""

    return _audit_literature_slice(
        repository_root,
        CORRECTED_MEAN_LITERATURE_REQUIREMENTS,
    )


def audit_methodology_literature_synthesis(
    repository_root: Path,
) -> dict[str, object]:
    """Validate the computational-finance methods literature slice."""

    return _audit_literature_slice(
        repository_root,
        METHODOLOGY_LITERATURE_REQUIREMENTS,
    )


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
        dca_receipt = audit_dca_literature_synthesis(args.repository_root)
        mean_receipt = audit_corrected_mean_literature_synthesis(
            args.repository_root
        )
        methodology_receipt = audit_methodology_literature_synthesis(
            args.repository_root
        )
    except LiteratureSynthesisError as error:
        print("LITERATURE SYNTHESIS CHECK FAILED")
        for item in str(error).splitlines():
            print(f"- {item}")
        return 1
    print(
        "LITERATURE SYNTHESIS CHECK PASSED: "
        f"{dca_receipt['literature_claim_count']} DCA claims and "
        f"{mean_receipt['literature_claim_count']} corrected-mean claims; "
        f"{dca_receipt['bibliography_key_count']} DCA sources and "
        f"{mean_receipt['bibliography_key_count']} corrected-mean sources; "
        f"{methodology_receipt['literature_claim_count']} methodology claims and "
        f"{methodology_receipt['bibliography_key_count']} methodology sources"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
