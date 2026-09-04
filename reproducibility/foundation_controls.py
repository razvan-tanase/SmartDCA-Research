#!/usr/bin/env python3
"""Fail-closed controls for the thesis financial-model foundation slice."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manuscript.citation_controls import (  # noqa: E402
    extract_bibtex_keys,
    extract_latex_citation_keys,
)
from reproducibility.control_support import (  # noqa: E402
    read_json_object as _read_json,
    read_text as _read_text,
)


RESOLVED_REVIEW_STATES = {"accepted", "reviewed"}
FOUNDATION_CLAIMS = {
    "claim-model-financial-comparison": "ch:model-signal/sec:comparison-model",
    "claim-accounting-average-acquisition-cost": (
        "ch:model-signal/sec:accounting-quantities"
    ),
    "claim-def-corrected-signal": "ch:model-signal/sec:corrected-signal",
    "claim-def-corrected-mean": "ch:model-signal/def:corrected-mean",
    "claim-thm-source-classification": (
        "ch:model-signal/thm:source-classification"
    ),
    "claim-thm-corrected-homogeneity": "ch:model-signal/thm:homogeneity",
}
FOUNDATION_NOTATION = {
    "notation-horizon-index": "ch:model-signal/sec:comparison-model",
    "notation-purchase-price": "ch:model-signal/sec:comparison-model",
    "notation-evaluation-price": "ch:model-signal/sec:comparison-model",
    "notation-deposit": "ch:model-signal/sec:comparison-model",
    "notation-purchase-outlay": "ch:model-signal/sec:comparison-model",
    "notation-cash": "ch:model-signal/sec:comparison-model",
    "notation-units": "ch:model-signal/sec:comparison-model",
    "notation-terminal-wealth": "ch:model-signal/sec:terminal-wealth",
    "notation-generic-strategy": "ch:model-signal/sec:comparison-model",
    "notation-policy-labels": "ch:model-signal/sec:comparators",
    "notation-dca-units": "ch:model-signal/sec:comparators",
    "notation-average-acquisition-cost": (
        "ch:model-signal/sec:accounting-quantities"
    ),
    "notation-transform": "ch:literature/sec:lit-mean-source-functional",
    "notation-mean-parameters": "ch:literature/sec:lit-mean-source-functional",
    "notation-diagonal-parameter": (
        "ch:literature/sec:lit-mean-family-identification"
    ),
    "notation-power-transform-specialization": (
        "ch:literature/sec:lit-mean-generalized-roots"
    ),
    "notation-mean-inputs": "ch:literature/sec:lit-mean-family-identification",
    "notation-mean-arity": "ch:model-signal/sec:source-functional-audit",
    "notation-source-functional": (
        "ch:literature/sec:lit-mean-source-functional"
    ),
    "notation-corrected-mean": (
        "ch:literature/sec:lit-mean-family-identification"
    ),
    "notation-bajraktarevic-generators": (
        "ch:literature/sec:lit-mean-family-identification"
    ),
    "notation-source-score-parameter": "ch:model-signal/sec:corrected-signal",
    "notation-reference-score": "ch:model-signal/sec:corrected-signal",
    "notation-constant-mean-input": (
        "ch:literature/sec:lit-mean-source-functional"
    ),
    "notation-source-diagonal-auxiliaries": (
        "app:proofs/sec:proof-source-classification"
    ),
    "notation-corrected-diagonal-proof": (
        "app:proofs/sec:proof-corrected-mean"
    ),
    "notation-homogeneity-proof": (
        "app:proofs/sec:proof-corrected-homogeneity"
    ),
}
REQUIRED_FOUNDATION_CITATIONS = {
    "aczeldaroczy1963",
    "bajraktarevic1958",
    "calvet2023smartdca",
    "matkowskiwrobel2020",
    "palespasteczka2016",
    "palespasteczka2018",
    "palespasteczka2024",
    "paleszakaria2020",
}


class FoundationControlError(ValueError):
    """Raised when Chapter 3 or its evidence controls drift from authority."""


def _normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def _chapter(source: str, title: str) -> str:
    marker = f"\\chapter{{{title}}}"
    start = source.find(marker)
    if start < 0:
        return ""
    remainder = source[start + len(marker) :]
    end = remainder.find("\\chapter{")
    return remainder if end < 0 else remainder[:end]


def _record_map(document: dict[str, object]) -> dict[str, dict[str, object]]:
    records = document.get("records", [])
    if not isinstance(records, list):
        return {}
    return {
        record["id"]: record
        for record in records
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }


def _require_terms(
    text: str,
    terms: tuple[str, ...],
    label: str,
    errors: list[str],
) -> None:
    normalized_text = _normalized(text)
    for term in terms:
        if _normalized(term) not in normalized_text:
            errors.append(f"missing {label}: {term!r}")


def _validate_authority_paths(
    root: Path,
    identifier: str,
    record: dict[str, object],
    errors: list[str],
) -> None:
    authority = record.get("authority")
    if not isinstance(authority, list) or not authority:
        errors.append(f"{identifier}: foundation claim has no authority")
        return
    for entry in authority:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            errors.append(f"{identifier}: invalid authority entry")
            continue
        relative_path = Path(entry["path"])
        candidate = (root / relative_path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            errors.append(f"{identifier}: authority path escapes repository")
            continue
        if not candidate.is_file():
            errors.append(
                f"{identifier}: authority path does not exist: {entry['path']}"
            )


def audit_financial_model_corrected_signal_foundations(
    repository_root: Path,
) -> dict[str, object]:
    """Audit Chapter 3, Appendix A, evidence mappings, notation, and citations."""

    root = repository_root.resolve()
    errors: list[str] = []
    thesis = _read_text(root / "manuscript/source/thesis.tex", errors)
    bibliography = _read_text(
        root / "manuscript/bibliography/references.bib", errors
    )
    claims = _record_map(
        _read_json(root / "manuscript/controls/claims.json", errors)
    )
    notation = _record_map(
        _read_json(root / "manuscript/controls/notation.json", errors)
    )

    chapter = _chapter(thesis, "Financial Model and Corrected Signal Foundations")
    appendix = _chapter(thesis, "Mathematical Proofs")
    if not chapter:
        errors.append("missing Chapter 3 financial-model foundation")
    if not appendix:
        errors.append("missing Appendix A mathematical proofs")

    _require_terms(
        chapter,
        (
            "finite positive price",
            "nonnegative exogenous cash deposit",
            "sequentially admissible",
            "long-only, buy-only, fully funded",
            "no leverage",
            "unused cash carries without interest",
            "common evaluation price",
            "cash-inclusive terminal wealth",
        ),
        "financial-model assumption",
        errors,
    )
    _require_terms(
        chapter,
        (
            "DCA receives the same deposit sequence and the same evaluation horizon",
            r"b_t^D=d_t",
            r"C_t^D=0",
            r"W_n^S(P)=C_n^S+P Q_n^S",
        ),
        "same-deposit comparator",
        errors,
    )
    _require_terms(
        chapter,
        (
            "Average acquisition cost is therefore an accounting quantity, not a budget-equivalent performance criterion",
            "It is undefined when no units have been acquired",
            r"AC_t^S=",
        ),
        "acquisition-cost boundary",
        errors,
    )
    _require_terms(
        chapter,
        (
            "out quasi-Gini functional",
            "source assumes that its transform is positive and increasing",
            "project's classification is stronger: it needs only positivity",
            "is a mean if and only if",
            "finite parameter-continuous extension valid on the entire diagonal",
            "identity transform",
        ),
        "source-functional classification",
        errors,
    )
    _require_terms(
        chapter,
        (
            "numerator-preserving repair",
            "weighted Bajraktarevi\\'c class",
            "not a new general mean class",
            "classical weighted Gini mean",
            "weighted Beckenbach--Gini--Lehmer form",
            "function-weighted geometric Bajraktarevi\\'c value",
            "normalized-multiplicativity condition",
        ),
        "corrected-mean boundary",
        errors,
    )
    _require_terms(
        chapter,
        (
            r"z_i=p_i/p_1",
            r"R_{t-1}",
            r"r_t=\frac{z_t}{R_{t-1}}",
            r"a_t",
            "first date set $r_1=1$",
            "The normalized lagged reference supplies a causal signal, not a safety guarantee",
            "It does not establish DCA dominance, a relative-wealth floor, or empirical forecasting value",
        ),
        "signal-safety boundary",
        errors,
    )

    ordered_labels = (
        "sec:comparison-model",
        "sec:source-functional-audit",
        "def:corrected-mean",
        "sec:corrected-signal",
    )
    positions = [chapter.find(f"\\label{{{label}}}") for label in ordered_labels]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        errors.append(
            "Chapter 3 order must be financial model, source audit, correction, signal"
        )

    _require_terms(
        appendix,
        (
            r"\label{sec:proof-source-classification}",
            r"\label{eq:appendix-source-reflexivity}",
            r"\label{sec:proof-corrected-mean}",
            r"\label{eq:appendix-corrected-diagonal-limit}",
            "along any parameter path",
            "does not depend on the approach direction",
            r"\label{sec:proof-corrected-homogeneity}",
            r"\label{eq:appendix-homogeneity-ratio}",
            "normalized multiplicativity makes the common scale factor",
        ),
        "appendix proof",
        errors,
    )

    for identifier, expected_location in FOUNDATION_CLAIMS.items():
        record = claims.get(identifier)
        if record is None:
            errors.append(f"missing foundation claim {identifier!r}")
            continue
        if record.get("manuscript_location") != expected_location:
            errors.append(
                f"{identifier}: manuscript_location must be {expected_location!r}"
            )
        if record.get("mandatory") is not True:
            errors.append(f"{identifier}: foundation claim must be mandatory")
        if record.get("review_state") not in RESOLVED_REVIEW_STATES:
            errors.append(f"{identifier}: foundation claim must be resolved")
        _validate_authority_paths(root, identifier, record, errors)

    for identifier, expected_first_use in FOUNDATION_NOTATION.items():
        record = notation.get(identifier)
        if record is None:
            errors.append(f"missing foundation notation {identifier!r}")
            continue
        if record.get("first_use") != expected_first_use:
            errors.append(
                f"{identifier}: first_use must be {expected_first_use!r}"
            )
        if record.get("mandatory") is not True:
            errors.append(f"{identifier}: notation record must be mandatory")
        if record.get("review_state") not in RESOLVED_REVIEW_STATES:
            errors.append(f"{identifier}: notation record must be resolved")
        first_use_label = expected_first_use.rsplit("/", 1)[-1]
        if f"\\label{{{first_use_label}}}" not in thesis:
            errors.append(
                f"{identifier}: manuscript is missing first-use label "
                f"{first_use_label!r}"
            )

    bibliography_keys = extract_bibtex_keys(bibliography)
    chapter_citations = extract_latex_citation_keys(chapter)
    for key in sorted(chapter_citations - bibliography_keys):
        errors.append(f"undefined Chapter 3 citation {key!r}")
    for key in sorted(REQUIRED_FOUNDATION_CITATIONS - chapter_citations):
        errors.append(f"Chapter 3 is missing required foundation citation {key!r}")
    for identifier in (
        "claim-accounting-average-acquisition-cost",
        "claim-def-corrected-signal",
    ):
        record = claims.get(identifier, {})
        citation_keys = record.get("citation_keys", [])
        if not isinstance(citation_keys, list) or not citation_keys:
            errors.append(f"{identifier}: citation_keys must be declared")
            continue
        for key in citation_keys:
            if key not in bibliography_keys:
                errors.append(f"{identifier}: undefined bibliography key {key!r}")
            if key not in chapter_citations:
                errors.append(f"{identifier}: citation {key!r} is absent from Chapter 3")

    if errors:
        raise FoundationControlError("\n".join(errors))

    return {
        "status": "passed",
        "claim_count": len(FOUNDATION_CLAIMS),
        "notation_count": len(FOUNDATION_NOTATION),
        "chapter_citation_count": len(chapter_citations),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    try:
        receipt = audit_financial_model_corrected_signal_foundations(
            args.repository_root
        )
    except FoundationControlError as error:
        print(error)
        print("FOUNDATION CONTROL FAILED")
        return 1
    print(
        "FOUNDATION CONTROL PASSED: "
        f"{receipt['claim_count']} claims, "
        f"{receipt['notation_count']} notation records, "
        f"{receipt['chapter_citation_count']} Chapter 3 citations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
