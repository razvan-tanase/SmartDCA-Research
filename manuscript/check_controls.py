#!/usr/bin/env python3
"""Validate the thesis architecture and evidence-control package."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


RESOLVED_REVIEW_STATES = {"accepted", "reviewed"}
UNRESOLVED_REVIEW_STATES = {"blocked", "pending", "planned", "unresolved"}
KNOWN_REVIEW_STATES = RESOLVED_REVIEW_STATES | UNRESOLVED_REVIEW_STATES
THESIS_REGISTER_NAMES = {
    "architecture",
    "claims",
    "contributions",
    "governance",
    "non_claims",
    "notation",
    "supervisor_feedback",
}
CONTRIBUTION_CATEGORIES = {
    "computational",
    "empirical",
    "integrative",
    "mathematical",
    "methodological",
}
REQUIRED_NON_CLAIMS = {
    "nonclaim-confirmed-signal-value",
    "nonclaim-frictional-safety",
    "nonclaim-new-mean-class",
    "nonclaim-universal-superiority",
}
GOVERNANCE_CONTROL_TYPES = {
    "chapter-dependencies",
    "citation-workflow",
    "generated-asset-policy",
    "release-state-transitions",
    "supervisor-feedback",
    "terminology-authority",
}
THESIS_PROFILE = "thesis-architecture-v1"


def missing_fields(record: dict[str, object], fields: tuple[str, ...]) -> list[str]:
    missing: list[str] = []
    for field in fields:
        value = record.get(field)
        if value is None or value == "" or value == []:
            missing.append(field)
    return missing


def add_missing_field_errors(
    register_name: str,
    record: dict[str, object],
    fields: tuple[str, ...],
    errors: list[str],
) -> None:
    for field in missing_fields(record, fields):
        errors.append(
            f"controls/{register_name}: {record.get('id')!r} missing required "
            f"field {field!r}"
        )


def validate_thesis_profile(
    manifest: dict[str, object],
    register_documents: dict[str, dict[str, object]],
    manuscript_root: Path,
    repository_root: Path,
    errors: list[str],
) -> None:
    architecture = register_documents.get("architecture", {}).get("records", [])
    if isinstance(architecture, list):
        spines = []
        labels: dict[str, str] = {}
        chapter_numbers: dict[object, str] = {}
        appendix_letters: dict[object, str] = {}
        for record in architecture:
            if not isinstance(record, dict):
                continue
            record_type = record.get("record_type")
            if record_type == "spine":
                spines.append(record)
                add_missing_field_errors(
                    "architecture.json",
                    record,
                    ("working_title", "narrative", "research_questions"),
                    errors,
                )
                questions = record.get("research_questions", [])
                if not isinstance(questions, list) or len(questions) != 3:
                    errors.append(
                        "controls/architecture.json: the thesis spine must contain "
                        "exactly three research questions"
                    )
                else:
                    question_ids: set[str] = set()
                    for question in questions:
                        if not isinstance(question, dict):
                            errors.append(
                                "controls/architecture.json: research question must "
                                "be an object"
                            )
                            continue
                        for field in ("id", "question", "conservative_answer"):
                            if not question.get(field):
                                errors.append(
                                    "controls/architecture.json: research question "
                                    f"missing required field {field!r}"
                                )
                        question_id = question.get("id")
                        if isinstance(question_id, str):
                            if question_id in question_ids:
                                errors.append(
                                    "controls/architecture.json: duplicate research "
                                    f"question identifier {question_id!r}"
                                )
                            question_ids.add(question_id)
            elif record_type in {"chapter", "appendix"}:
                add_missing_field_errors(
                    "architecture.json",
                    record,
                    (
                        "title",
                        "manuscript_label",
                        "purpose",
                        "prerequisites",
                        "intended_reader_outcome",
                        "placement_rule",
                    ),
                    errors,
                )
                label = record.get("manuscript_label")
                if isinstance(label, str):
                    if label in labels:
                        errors.append(
                            "controls/architecture.json: duplicate manuscript label "
                            f"{label!r}"
                        )
                    labels[label] = str(record.get("id"))
                sequence_field = "number" if record_type == "chapter" else "letter"
                sequence = record.get(sequence_field)
                sequences = (
                    chapter_numbers if record_type == "chapter" else appendix_letters
                )
                if sequence is None:
                    errors.append(
                        "controls/architecture.json: "
                        f"{record.get('id')!r} missing required field {sequence_field!r}"
                    )
                elif sequence in sequences:
                    errors.append(
                        "controls/architecture.json: duplicate "
                        f"{sequence_field} {sequence!r}"
                    )
                else:
                    sequences[sequence] = str(record.get("id"))
            else:
                errors.append(
                    "controls/architecture.json: "
                    f"{record.get('id')!r} has unknown record_type {record_type!r}"
                )
        if len(spines) != 1:
            errors.append(
                "controls/architecture.json: exactly one thesis spine is required"
            )
        if not chapter_numbers:
            errors.append("controls/architecture.json: at least one chapter is required")
        if not appendix_letters:
            errors.append("controls/architecture.json: at least one appendix is required")

        source_shell = manifest.get("source_shell")
        if not isinstance(source_shell, str) or not source_shell:
            errors.append(
                "controls/control-manifest.json: source_shell must be declared"
            )
        else:
            shell_path = resolve_within(
                manuscript_root,
                source_shell,
                "source shell path",
                errors,
            )
            if shell_path is not None:
                try:
                    shell_source = shell_path.read_text(encoding="utf-8")
                except OSError as error:
                    errors.append(f"{source_shell}: unreadable source shell ({error})")
                else:
                    shell_source = re.sub(
                        r"(?<!\\)%.*$", "", shell_source, flags=re.MULTILINE
                    )
                    for label, identifier in sorted(labels.items()):
                        if f"\\label{{{label}}}" not in shell_source:
                            errors.append(
                                f"{source_shell}: source shell missing architecture "
                                f"label {label!r} for {identifier!r}"
                            )
                    for record in architecture:
                        if not isinstance(record, dict):
                            continue
                        record_type = record.get("record_type")
                        if record_type == "spine":
                            title = record.get("working_title")
                            source_declaration = (
                                f"\\newcommand{{\\thesistitle}}{{{title}}}"
                            )
                        elif record_type in {"chapter", "appendix"}:
                            title = record.get("title")
                            source_declaration = f"\\chapter{{{title}}}"
                        else:
                            continue
                        if (
                            isinstance(title, str)
                            and title
                            and source_declaration not in shell_source
                        ):
                            errors.append(
                                f"{source_shell}: source shell missing architecture "
                                f"title {title!r} for {record.get('id')!r}"
                            )

    contributions = register_documents.get("contributions", {}).get("records", [])
    contribution_categories: set[object] = set()
    if isinstance(contributions, list):
        for record in contributions:
            if not isinstance(record, dict):
                continue
            add_missing_field_errors(
                "contributions.json",
                record,
                (
                    "category",
                    "contribution",
                    "evidence_paths",
                    "manuscript_locations",
                    "novelty_boundary",
                ),
                errors,
            )
            contribution_categories.add(record.get("category"))
    for category in sorted(CONTRIBUTION_CATEGORIES - contribution_categories):
        errors.append(
            "controls/contributions.json: missing contribution category "
            f"{category!r}"
        )

    non_claims = register_documents.get("non_claims", {}).get("records", [])
    non_claim_ids: set[object] = set()
    if isinstance(non_claims, list):
        for record in non_claims:
            if not isinstance(record, dict):
                continue
            add_missing_field_errors(
                "non-claims.json",
                record,
                (
                    "rejected_claim",
                    "required_wording",
                    "reason",
                    "authority_paths",
                    "affected_locations",
                ),
                errors,
            )
            non_claim_ids.add(record.get("id"))
    for identifier in sorted(REQUIRED_NON_CLAIMS - non_claim_ids):
        errors.append(
            f"controls/non-claims.json: missing required non-claim {identifier!r}"
        )

    claims = register_documents.get("claims", {}).get("records", [])
    canonical_claim_authority_paths: set[str] = set()
    entry_types: set[object] = set()
    if isinstance(claims, list):
        for record in claims:
            if not isinstance(record, dict):
                continue
            add_missing_field_errors(
                "claims.json",
                record,
                (
                    "entry_type",
                    "wording",
                    "claim_class",
                    "scope",
                    "authority",
                    "manuscript_location",
                    "citation_need",
                ),
                errors,
            )
            entry_types.add(record.get("entry_type"))
            if record.get("entry_type") in {"definition", "theorem"}:
                for path in authority_paths(record):
                    if isinstance(path, str):
                        canonical_claim_authority_paths.add(path)
    for entry_type in (
        "definition",
        "theorem",
        "empirical-headline",
        "planned-table",
        "planned-figure",
    ):
        if entry_type not in entry_types:
            errors.append(
                f"controls/claims.json: missing claim entry type {entry_type!r}"
            )

    coverage = manifest.get("coverage", {})
    if isinstance(coverage, dict):
        for coverage_name in ("canonical_definitions", "canonical_theorems"):
            pattern = coverage.get(coverage_name)
            if not isinstance(pattern, str) or not pattern:
                errors.append(
                    "controls/control-manifest.json: missing coverage pattern "
                    f"{coverage_name!r}"
                )
                continue
            pattern_path = Path(pattern)
            if pattern_path.is_absolute() or ".." in pattern_path.parts:
                errors.append(
                    "controls/control-manifest.json: coverage pattern must remain "
                    f"within the repository: {pattern}"
                )
                continue
            for path in sorted(repository_root.glob(pattern)):
                relative_path = path.relative_to(repository_root).as_posix()
                if relative_path not in canonical_claim_authority_paths:
                    errors.append(
                        "controls/claims.json: canonical authority is not registered: "
                        f"{relative_path}"
                    )
    else:
        errors.append("controls/control-manifest.json: coverage must be an object")

    notation = register_documents.get("notation", {}).get("records", [])
    if isinstance(notation, list):
        for record in notation:
            if isinstance(record, dict):
                add_missing_field_errors(
                    "notation.json",
                    record,
                    (
                        "symbol",
                        "meaning",
                        "repository_notation",
                        "manuscript_notation",
                        "reconciliation",
                        "first_use",
                    ),
                    errors,
                )

    governance = register_documents.get("governance", {}).get("records", [])
    governance_types: set[object] = set()
    if isinstance(governance, list):
        for record in governance:
            if not isinstance(record, dict):
                continue
            add_missing_field_errors(
                "governance.json",
                record,
                ("control_type", "rule", "authority_paths"),
                errors,
            )
            governance_types.add(record.get("control_type"))
    for control_type in sorted(GOVERNANCE_CONTROL_TYPES - governance_types):
        errors.append(
            "controls/governance.json: missing governance control "
            f"{control_type!r}"
        )

    feedback = register_documents.get("supervisor_feedback", {})
    expected_feedback_fields = {
        "affected_locations",
        "classification",
        "concern",
        "decision",
        "id",
        "mandatory",
        "owner",
        "received_on",
        "resolution_evidence",
        "review_state",
        "source",
    }
    actual_feedback_fields = feedback.get("required_entry_fields", [])
    if set(actual_feedback_fields) != expected_feedback_fields:
        errors.append(
            "controls/supervisor-feedback.json: required_entry_fields does not "
            "define the complete feedback contract"
        )
    if not feedback.get("log_state"):
        errors.append(
            "controls/supervisor-feedback.json: log_state must be non-empty"
        )


def read_json(path: Path, errors: list[str]) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{path}: unreadable JSON ({error})")
        return None


def authority_paths(record: dict[str, object]) -> list[object]:
    paths: list[object] = []
    authority = record.get("authority", [])
    if isinstance(authority, list):
        for entry in authority:
            if isinstance(entry, dict):
                paths.append(entry.get("path"))
    for field in ("authority_paths", "evidence_paths"):
        value = record.get(field, [])
        if isinstance(value, list):
            paths.extend(value)
    return paths


def resolve_within(
    base: Path,
    value: object,
    description: str,
    errors: list[str],
) -> Path | None:
    """Resolve a relative path while preventing directory escape."""
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{description} must be a non-empty relative path")
        return None
    candidate = Path(value)
    if candidate.is_absolute():
        errors.append(f"{description} must be relative: {value}")
        return None
    resolved = (base / candidate).resolve()
    try:
        resolved.relative_to(base.resolve())
    except ValueError:
        errors.append(f"{description} escapes repository root: {value}")
        return None
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="manuscript project root (default: directory containing this script)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("controls/control-manifest.json"),
        help="manifest path relative to the manuscript root",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    repository_root = root.parent
    errors: list[str] = []
    identifier_locations: dict[str, str] = {}
    register_names: set[str] = set()
    register_documents: dict[str, dict[str, object]] = {}
    manifest_path = resolve_within(
        root,
        args.manifest.as_posix(),
        "controls manifest path",
        errors,
    )
    manifest = read_json(manifest_path, errors) if manifest_path else None
    if not isinstance(manifest, dict):
        errors.append("controls/control-manifest.json: expected a JSON object")
    else:
        registers = manifest.get("registers")
        if not isinstance(registers, list) or not registers:
            errors.append("controls/control-manifest.json: registers must be non-empty")
        else:
            for descriptor in registers:
                if not isinstance(descriptor, dict):
                    errors.append("controls/control-manifest.json: invalid register entry")
                    continue
                relative_path = descriptor.get("path")
                register_name = descriptor.get("name")
                if not isinstance(register_name, str) or not register_name:
                    errors.append("controls/control-manifest.json: register name is required")
                elif register_name in register_names:
                    errors.append(
                        "controls/control-manifest.json: duplicate register name "
                        f"{register_name!r}"
                    )
                else:
                    register_names.add(register_name)
                if not isinstance(relative_path, str) or not relative_path:
                    errors.append("controls/control-manifest.json: register path is required")
                    continue
                register_path = resolve_within(
                    root,
                    relative_path,
                    f"{relative_path} register path",
                    errors,
                )
                if register_path is None:
                    continue
                register = read_json(register_path, errors)
                if not isinstance(register, dict):
                    errors.append(f"{relative_path}: expected a JSON object")
                    continue
                if register.get("register") != register_name:
                    errors.append(
                        f"{relative_path}: register name does not match "
                        f"manifest entry {register_name!r}"
                    )
                if isinstance(register_name, str):
                    register_documents[register_name] = register
                records = register.get("records")
                if not isinstance(records, list):
                    errors.append(f"{relative_path}: records must be an array")
                    continue
                for index, record in enumerate(records):
                    if not isinstance(record, dict):
                        errors.append(f"{relative_path}: record {index} must be an object")
                        continue
                    for field in ("id", "mandatory", "review_state"):
                        if field not in record:
                            errors.append(
                                f"{relative_path}: record {index} is missing {field}"
                            )
                    identifier = record.get("id")
                    if not isinstance(identifier, str) or not identifier.strip():
                        errors.append(
                            f"{relative_path}: record {index} has an invalid identifier"
                        )
                    elif identifier in identifier_locations:
                        errors.append(
                            f"{relative_path}: duplicate identifier {identifier!r}; "
                            f"first declared at {identifier_locations[identifier]}"
                        )
                    else:
                        identifier_locations[identifier] = (
                            f"{relative_path} record {index}"
                        )
                    mandatory = record.get("mandatory")
                    review_state = record.get("review_state")
                    if not isinstance(mandatory, bool):
                        errors.append(
                            f"{relative_path}: {identifier!r} mandatory must be boolean"
                        )
                    if not isinstance(review_state, str) or not review_state.strip():
                        errors.append(
                            f"{relative_path}: {identifier!r} review_state must be non-empty"
                        )
                    elif review_state not in KNOWN_REVIEW_STATES:
                        errors.append(
                            f"{relative_path}: {identifier!r} has unknown review_state "
                            f"{review_state!r}"
                        )
                    elif mandatory and review_state in UNRESOLVED_REVIEW_STATES:
                        errors.append(
                            f"{relative_path}: {identifier!r} mandatory record is "
                            f"unresolved ({review_state})"
                        )
                    for authority_path in authority_paths(record):
                        if not isinstance(authority_path, str) or not authority_path:
                            errors.append(
                                f"{relative_path}: {identifier!r} has an invalid "
                                "authority path"
                            )
                        else:
                            resolved_authority = resolve_within(
                                repository_root,
                                authority_path,
                                f"{relative_path}: {identifier!r} authority path",
                                errors,
                            )
                            if resolved_authority is not None and not resolved_authority.exists():
                                errors.append(
                                    f"{relative_path}: {identifier!r} authority path "
                                    f"does not exist: {authority_path}"
                                )
        profile = manifest.get("profile")
        if profile is not None and profile != THESIS_PROFILE:
            errors.append(
                "controls/control-manifest.json: unknown profile "
                f"{profile!r}"
            )
        if profile == THESIS_PROFILE:
            for missing_name in sorted(THESIS_REGISTER_NAMES - register_names):
                errors.append(
                    "controls/control-manifest.json: missing required register "
                    f"{missing_name!r}"
                )
            validate_thesis_profile(
                manifest,
                register_documents,
                root,
                repository_root,
                errors,
            )

    if errors:
        print("CONTROL CHECK FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("CONTROL CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
