#!/usr/bin/env python3
"""Fail closed when a thesis submission candidate is not release-ready."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


DEFAULT_RELEASE_READY_STATUSES = {"approved", "verified"}
DEFAULT_PLACEHOLDER_PATTERNS = (
    ("UNRESOLVED", r"\[UNRESOLVED:"),
    ("work-marker", r"\b(?:TODO|TBD|FIXME)\b"),
    ("template-token", r"\{\{\s*[A-Z][A-Z0-9_-]{2,}\s*\}\}"),
)


def canonical_json_digest(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def strip_latex_comments(source: str) -> str:
    return re.sub(r"(?<!\\)%.*$", "", source, flags=re.MULTILINE)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="manuscript project root (default: directory containing this script)",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    contract_path = root / "contract" / "requirements.json"
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print("RELEASE CHECK FAILED")
        print(f"- contract/requirements.json: unreadable release contract ({error})")
        return 1

    release_gate = contract.get("release_gate", {})
    release_ready_statuses = set(
        release_gate.get(
            "release_ready_statuses", sorted(DEFAULT_RELEASE_READY_STATUSES)
        )
    )
    non_ready_requirements = [
        requirement
        for requirement in contract.get("requirements", [])
        if requirement.get("release_blocking")
        and (
            requirement.get("status") not in release_ready_statuses
            or requirement.get("value") is None
            or (
                isinstance(requirement.get("value"), str)
                and not requirement["value"].strip()
            )
        )
    ]
    sources = {source.get("id"): source for source in contract.get("sources", [])}

    def has_authoritative_provenance(source: dict[str, object] | None) -> bool:
        if (
            source is None
            or source.get("authority") != "official"
            or not source.get("accessed_on")
        ):
            return False
        if source.get("url"):
            return True
        local_path = source.get("local_path")
        expected_digest = source.get("sha256")
        if not isinstance(local_path, str) or not isinstance(expected_digest, str):
            return False
        retained_candidates = (root / local_path, root.parent / local_path)
        return any(
            candidate.is_file()
            and hashlib.sha256(candidate.read_bytes()).hexdigest() == expected_digest
            for candidate in retained_candidates
        )

    requirements_without_provenance = []
    for requirement in contract.get("requirements", []):
        if requirement.get("status") != "verified":
            continue
        source_ids = requirement.get("source_ids", [])
        cited_sources = [sources.get(source_id) for source_id in source_ids]
        if not cited_sources or any(
            not has_authoritative_provenance(source) for source in cited_sources
        ):
            requirements_without_provenance.append(requirement["id"])
    release_inputs = contract.get("release_inputs", {})
    text_files = release_inputs.get("text_files", [])
    configured_patterns = release_gate.get("placeholder_patterns")
    placeholder_patterns = (
        tuple(
            (entry["id"], re.compile(entry["pattern"]))
            for entry in configured_patterns
        )
        if configured_patterns is not None
        else tuple(
            (identifier, re.compile(pattern))
            for identifier, pattern in DEFAULT_PLACEHOLDER_PATTERNS
        )
    )
    placeholder_files: list[tuple[str, list[str]]] = []
    for relative_path in text_files:
        source_path = root / relative_path
        if not source_path.is_file():
            continue
        source_text = source_path.read_text(encoding="utf-8")
        matched_patterns = [
            identifier
            for identifier, pattern in placeholder_patterns
            if pattern.search(source_text)
        ]
        if matched_patterns:
            placeholder_files.append((relative_path, matched_patterns))
    missing_files = [
        relative_path
        for relative_path in release_inputs.get("required_files", [])
        if not (root / relative_path).is_file()
    ]
    mirror_blockers: list[str] = []
    mirror = contract.get("contract_mirror")
    narrative_is_required = (
        "contract/institutional-contract.md"
        in release_inputs.get("required_files", [])
    )
    if mirror is None and narrative_is_required:
        mirror_blockers.append("contract mirror digest is not declared")
    elif mirror is not None:
        narrative_path = root / mirror.get("path", "")
        expected_digest = mirror.get("sha256")
        if not narrative_path.is_file():
            mirror_blockers.append(
                f"{mirror.get('path', '<missing path>')}: contract mirror is missing"
            )
        elif not expected_digest:
            mirror_blockers.append("contract mirror digest is not declared")
        else:
            actual_digest = hashlib.sha256(narrative_path.read_bytes()).hexdigest()
            if actual_digest != expected_digest:
                mirror_blockers.append(
                    f"{mirror['path']}: contract mirror digest mismatch"
                )
        requirements_digest = canonical_json_digest(
            contract.get("requirements", [])
        )
        expected_requirements_digest = mirror.get("requirements_sha256")
        if expected_requirements_digest != requirements_digest:
            mirror_blockers.append("machine requirements digest mismatch")
        elif narrative_path.is_file():
            narrative_attestation = (
                f"Machine requirements digest: `{requirements_digest}`"
            )
            if narrative_attestation not in narrative_path.read_text(
                encoding="utf-8"
            ):
                mirror_blockers.append(
                    "narrative does not attest the machine requirements digest"
                )
    undefined_citations: list[str] = []
    unused_bibliography_entries: list[str] = []
    bibliography_path = release_inputs.get("bibliography")
    if bibliography_path and (root / bibliography_path).is_file():
        bibliography = (root / bibliography_path).read_text(encoding="utf-8")
        defined_keys = set(
            re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bibliography)
        )
        cited_keys: set[str] = set()
        for relative_path in text_files:
            source_path = root / relative_path
            if not source_path.is_file():
                continue
            source = strip_latex_comments(
                source_path.read_text(encoding="utf-8")
            )
            for citation_group in re.findall(
                r"\\(?:[A-Za-z]*cite[A-Za-z]*)\*?"
                r"(?:\s*\[[^\]]*\]){0,2}\s*\{([^}]*)\}",
                source,
            ):
                cited_keys.update(
                    key.strip()
                    for key in citation_group.split(",")
                    if key.strip() and key.strip() != "*"
                )
        undefined_citations = sorted(cited_keys - defined_keys)
        unused_bibliography_entries = sorted(defined_keys - cited_keys)

    if (
        non_ready_requirements
        or requirements_without_provenance
        or placeholder_files
        or missing_files
        or mirror_blockers
        or undefined_citations
        or unused_bibliography_entries
    ):
        print("RELEASE CHECK FAILED")
        for blocker in non_ready_requirements:
            print(
                f"- {blocker['id']} (owner: {blocker['owner']}): "
                f"status {blocker.get('status', '<missing>')} is not release-ready"
            )
        for requirement_id in requirements_without_provenance:
            print(
                f"- {requirement_id}: missing authoritative source provenance"
            )
        for relative_path, pattern_ids in placeholder_files:
            print(
                f"- {relative_path}: contains placeholder marker(s): "
                f"{', '.join(pattern_ids)}"
            )
        for relative_path in missing_files:
            print(f"- {relative_path}: missing required build input")
        for mirror_blocker in mirror_blockers:
            print(f"- {mirror_blocker}")
        for citation_key in undefined_citations:
            print(f"- {citation_key}: undefined citation")
        for bibliography_key in unused_bibliography_entries:
            print(f"- {bibliography_key}: unused bibliography entry")
        return 1

    print("RELEASE CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
