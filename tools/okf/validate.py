#!/usr/bin/env python3
"""Report OKF v0.2 and SmartDCA profile findings for a knowledge bundle."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
import sys
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml


PROFILE_VERSION = "smartdca-okf/0.3"
RESERVED_NAMES = {"index.md", "log.md"}
NON_CONCEPT_MARKDOWN = {"README.md"}
REGISTERED_TYPES = {
    "project-overview", "specification", "domain-glossary", "definition", "theorem",
    "research-note", "source-summary", "synthesis", "experiment-report", "decision-record",
    "research-map", "research-ticket", "workflow", "agent-instructions",
}
KNOWLEDGE_ROLES = {"canonical", "evidence", "operational"}
LIFECYCLE_STATUSES = {"draft", "stable", "deprecated"}
SOURCE_KINDS = {"internal", "external", "scope"}
TICKET_TYPES = {"research", "prototype", "grilling", "task"}
TICKET_STATUSES = {"open", "claimed", "resolved"}
DECISION_STATUSES = {"proposed", "accepted", "deprecated", "superseded"}
HIGH_RISK_TYPES = {"domain-glossary", "definition", "theorem", "synthesis", "decision-record"}
SEMANTIC_CI_ACTOR = "process:github-actions:smartdca-wiki-ci"
EXACT_PATH_RULES = {
    "CONTEXT.md": ("domain-glossary", "canonical", None),
    "AGENTS.md": ("agent-instructions", "operational", "stable"),
    "docs/agents/domain.md": ("agent-instructions", "operational", "stable"),
    "docs/agents/triage-labels.md": ("domain-glossary", "operational", "stable"),
    "docs/agents/issue-tracker.md": ("workflow", "operational", "stable"),
    "docs/agents/wayfinder-ticket-workflow.md": ("workflow", "operational", "stable"),
    "docs/agents/llm-wiki-workflow.md": ("workflow", "operational", None),
    "docs/knowledge/okf-profile.md": ("specification", "canonical", None),
    ".scratch/smartdca/map.md": ("research-map", "operational", "stable"),
}

UUID_URN = re.compile(r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
ACTOR = re.compile(r"^(?:human:[^\s]+|process:[^\s]+|[^\s/:]+/[^\s/]+)$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
DATE_HEADING = re.compile(r"^## (\d{4}-\d{2}-\d{2})$")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FOOTNOTE = re.compile(r"\[\^([^\]]+)\]")
INDEX_ROW = re.compile(
    r"^- \[(?P<title>[^\]]+)\]\((?P<path>[^)]+)\) — (?P<description>.+) — "
    r"type: (?P<type>[^;]+); status: (?P<status>[^;]+); "
    r"trust: (?P<trust>[^;]+); provenance: (?P<provenance>.+)$"
)
LOG_ROW = re.compile(
    r"^- (?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) \| "
    r"(?P<operation>[^|]+) \| (?P<title>[^|]+) \| (?P<links>.+)$"
)


@dataclass(frozen=True, order=True)
class Finding:
    code: str
    path: str
    message: str


CODE_FENCE = re.compile(r"\s*(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"(`+)(?:(?!\1).)*?\1")


@dataclass
class Document:
    path: Path
    relative: str
    metadata: dict[str, Any] | None
    body: str

    @property
    def concept_id(self) -> str:
        return self.relative.removesuffix(".md")

    @property
    def prose_lines(self) -> list[str]:
        """The body lines with code removed.

        Links and footnote labels inside a fenced block or an inline code span
        are illustrative syntax, not references, so link and provenance checks
        must ignore them. A fence closes only on a marker of the same character
        that is at least as long as the one that opened it.
        """
        lines: list[str] = []
        opening: str | None = None
        for line in self.body.splitlines():
            marker = CODE_FENCE.match(line)
            fence = marker.group(1) if marker else None
            if opening is None:
                if fence is None:
                    lines.append(CODE_SPAN.sub(" ", line))
                else:
                    opening = fence
            elif fence is not None and fence[0] == opening[0] and len(fence) >= len(opening):
                opening = None
        return lines

    @property
    def prose(self) -> str:
        return "\n".join(self.prose_lines)


def add(findings: list[Finding], code: str, path: str, message: str) -> None:
    findings.append(Finding(code=code, path=path, message=message))


def load_frontmatter(path: Path, relative: str, findings: list[Finding]) -> Document:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        add(findings, "OKF006", relative, "Markdown documents must be valid UTF-8")
        return Document(path, relative, None, "")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        add(findings, "OKF001", relative, "concept must start with YAML frontmatter")
        return Document(path, relative, None, text)
    closing = next((i for i, line in enumerate(lines[1:], 1) if line.rstrip("\r\n") == "---"), None)
    if closing is None:
        add(findings, "OKF002", relative, "frontmatter is missing its closing delimiter")
        return Document(path, relative, None, text)
    try:
        parsed = yaml.safe_load("".join(lines[1:closing]))
    except yaml.YAMLError as error:
        add(findings, "OKF003", relative, f"frontmatter is not parseable YAML: {error}")
        return Document(path, relative, None, "".join(lines[closing + 1:]))
    if not isinstance(parsed, dict):
        add(findings, "OKF004", relative, "frontmatter must be a YAML mapping")
        parsed = None
    return Document(path, relative, parsed, "".join(lines[closing + 1:]))


def markdown_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.md")
        if path.is_file()
        and ".git" not in path.relative_to(root).parts
        and path.relative_to(root).as_posix() not in NON_CONCEPT_MARKDOWN
    )


def validate_base_log(relative: str, body: str, findings: list[Finding]) -> None:
    dates: list[date] = []
    in_group = False
    for line in body.splitlines():
        if line.startswith("## "):
            match = DATE_HEADING.fullmatch(line)
            if not match:
                add(findings, "OKF012", relative, "log date headings must use ## YYYY-MM-DD")
                continue
            try:
                dates.append(date.fromisoformat(match.group(1)))
            except ValueError:
                add(findings, "OKF012", relative, "log date heading is not a real calendar date")
            in_group = True
        elif in_group and line.strip() and not line.startswith(("- ", "* ")):
            add(findings, "OKF013", relative, "log date groups must contain a flat bullet list")
    if not dates:
        add(findings, "OKF012", relative, "log must contain at least one ## YYYY-MM-DD date group")
    elif dates != sorted(dates, reverse=True):
        add(findings, "OKF013", relative, "log date groups must be newest first")


def parse_reserved(root: Path, path: Path, findings: list[Finding]) -> Document:
    relative = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8")
    metadata = None
    body = text
    if text.startswith("---\n"):
        parsed = load_frontmatter(path, relative, findings)
        metadata, body = parsed.metadata, parsed.body
        if path.name == "log.md" or relative != "index.md":
            add(findings, "OKF010", relative, "frontmatter is permitted only in the bundle-root index.md")
        elif metadata is not None and set(metadata) - {"okf_version"}:
            add(findings, "OKF011", relative, "root index frontmatter may contain only okf_version")
    if path.name == "index.md":
        if not re.search(r"^#{1,6} \S", body, re.M):
            add(findings, "OKF011", relative, "index body must group entries under Markdown headings")
    else:
        validate_base_log(relative, body, findings)
    return Document(path, relative, metadata, body)


def validate_base_optional(document: Document, warnings: list[Finding]) -> None:
    metadata = document.metadata or {}
    status = metadata.get("status")
    if status is not None and status not in LIFECYCLE_STATUSES:
        add(warnings, "OKFW001", document.relative, "optional status should be draft, stable, or deprecated")
    generated = metadata.get("generated")
    if generated is not None:
        if not isinstance(generated, dict) or not valid_actor(generated.get("by")):
            add(warnings, "OKFW002", document.relative, "generated should be a mapping with a valid by actor")
        elif generated.get("at") is not None and as_datetime(generated.get("at")) is None:
            add(warnings, "OKFW002", document.relative, "generated.at should be an ISO 8601 datetime")
    verified = metadata.get("verified")
    if verified is not None:
        events = verified if isinstance(verified, list) else [verified] if isinstance(verified, dict) else []
        if not events or any(
            not isinstance(event, dict)
            or not valid_actor(event.get("by"))
            or as_datetime(event.get("at")) is None
            for event in events
        ):
            add(warnings, "OKFW003", document.relative, "verified should be a mapping or list of events with by and at")
    sources = metadata.get("sources")
    if sources is not None:
        if not isinstance(sources, list) or any(
            not isinstance(source, dict)
            or not isinstance(source.get("resource"), str)
            or not source["resource"].strip()
            for source in sources
        ):
            add(warnings, "OKFW004", document.relative, "each optional sources entry should contain a non-empty resource")
    stale_after = metadata.get("stale_after")
    if stale_after is not None and as_date(stale_after) is None:
        add(warnings, "OKFW005", document.relative, "stale_after should be an absolute YYYY-MM-DD date")
    if metadata.get("type") == "Attested Computation" and not metadata.get("runtime"):
        add(warnings, "OKFW006", document.relative, "Attested Computation should declare runtime")


def validate_base(root: Path) -> tuple[list[Finding], list[Finding], list[Document]]:
    findings: list[Finding] = []
    warnings: list[Finding] = []
    documents: list[Document] = []
    for path in markdown_files(root):
        relative = path.relative_to(root).as_posix()
        if path.name in RESERVED_NAMES:
            documents.append(parse_reserved(root, path, findings))
            continue
        document = load_frontmatter(path, relative, findings)
        documents.append(document)
        if document.metadata is not None:
            value = document.metadata.get("type")
            if not isinstance(value, str) or not value.strip():
                add(findings, "OKF005", relative, "frontmatter requires a non-empty type string")
            validate_base_optional(document, warnings)
    return sorted(set(findings)), sorted(set(warnings)), documents


def expected_path_rule(relative: str) -> tuple[str, str, str | None] | None:
    if relative in EXACT_PATH_RULES:
        return EXACT_PATH_RULES[relative]
    if re.fullmatch(r"docs/adr/[^/]+\.md", relative):
        return "decision-record", "canonical", None
    if re.fullmatch(r"research/notes/[^/]+\.md", relative):
        return "research-note", "evidence", None
    if re.fullmatch(r"research/definitions/[^/]+\.md", relative):
        return "definition", "canonical", None
    if re.fullmatch(r"research/theorems/[^/]+\.md", relative):
        return "theorem", "canonical", None
    if re.fullmatch(r"reports/experiments/[^/]+\.md", relative):
        return "experiment-report", "evidence", None
    if re.fullmatch(r"research/synthesis/[^/]+\.md", relative):
        return "synthesis", "canonical", None
    if re.fullmatch(r"references/summaries/[^/]+\.md", relative):
        return "source-summary", "evidence", None
    if re.fullmatch(r"\.scratch/smartdca/issues/[^/]+\.md", relative):
        return "research-ticket", "operational", None
    return None


def as_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        result = value
    elif isinstance(value, str):
        try:
            result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None
    if result.tzinfo is None:
        return None
    return result.astimezone(timezone.utc)


def as_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def valid_actor(value: Any) -> bool:
    return isinstance(value, str) and ACTOR.fullmatch(value) is not None


def valid_run(value: Any) -> bool:
    return isinstance(value, str) and UUID_URN.fullmatch(value) is not None


def internal_target(document: Document, resource: str, by_id: dict[str, Document]) -> Document | None:
    path = resource.split("#", 1)[0]
    if not path:
        return document
    normalized = path.lstrip("/")
    candidates = [normalized if normalized.endswith(".md") else normalized + ".md"]
    if not path.startswith("/"):
        joined = (PurePosixPath(document.relative).parent / path).as_posix()
        candidates.append(joined if joined.endswith(".md") else joined + ".md")
    for candidate in candidates:
        target = by_id.get(candidate.removesuffix(".md"))
        if target is not None:
            return target
    return None


def local_link_target(root: Path, document: Document, target: str) -> Path | None:
    split = urlsplit(target)
    if split.scheme or split.netloc or target.startswith(("mailto:", "#")):
        return None
    raw_path = unquote(split.path)
    if not raw_path:
        return None
    return root / raw_path.lstrip("/") if raw_path.startswith("/") else document.path.parent / raw_path


def run_git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def is_git_bundle_root(root: Path) -> bool:
    top_level = run_git(root, "rev-parse", "--show-toplevel")
    return (
        top_level is not None
        and top_level.returncode == 0
        and Path(top_level.stdout.strip()).resolve() == root.resolve()
    )


def tracked_artifact_was_modified(root: Path, artifact: str) -> bool:
    if not is_git_bundle_root(root):
        return False
    history = run_git(root, "log", "--follow", "--format=%H", "--", artifact)
    commits = history.stdout.splitlines() if history is not None and history.returncode == 0 else []
    if len(commits) > 1:
        return True
    if len(commits) == 1:
        status = run_git(root, "status", "--porcelain", "--untracked-files=no", "--", artifact)
        return status is not None and status.returncode == 0 and bool(status.stdout.strip())
    return False


def git_file_versions(root: Path, relative: str) -> list[str]:
    if not is_git_bundle_root(root):
        return []
    history = run_git(root, "log", "--format=%H", "--", relative)
    versions = []
    for commit in history.stdout.splitlines() if history is not None and history.returncode == 0 else []:
        snapshot = run_git(root, "show", f"{commit}:{relative}")
        if snapshot is not None and snapshot.returncode == 0:
            versions.append(snapshot.stdout)
    return versions


def is_subsequence(earlier: list[str], current: list[str]) -> bool:
    position = 0
    for line in current:
        if position < len(earlier) and line == earlier[position]:
            position += 1
    return position == len(earlier)


def linked_concepts(document: Document, by_relative: dict[str, Document]) -> list[Document]:
    linked: list[Document] = []
    for target in MARKDOWN_LINK.findall(document.prose):
        split = urlsplit(target)
        if split.scheme or split.netloc or not split.path.endswith(".md"):
            continue
        if split.path.startswith("/"):
            relative = split.path.lstrip("/")
        else:
            relative = posixpath.normpath(
                (PurePosixPath(document.relative).parent / unquote(split.path)).as_posix()
            )
        linked_document = by_relative.get(relative)
        if linked_document is not None:
            linked.append(linked_document)
    return linked


def verification_events(document: Document, metadata: dict[str, Any], findings: list[Finding], require_review_run: bool) -> list[tuple[dict[str, Any], datetime]]:
    raw = metadata.get("verified")
    if raw is None:
        return []
    if require_review_run and not isinstance(raw, list):
        add(findings, "SDCA030", document.relative, "verified must be a list for reviewed SmartDCA concepts")
        raw_events = [raw]
    elif isinstance(raw, list):
        raw_events = raw
    elif isinstance(raw, dict):
        raw_events = [raw]
    else:
        add(findings, "SDCA030", document.relative, "verified must be a mapping or list of mappings")
        return []
    parsed = []
    for event in raw_events:
        at = as_datetime(event.get("at")) if isinstance(event, dict) else None
        if not isinstance(event, dict) or not valid_actor(event.get("by")) or at is None:
            add(findings, "SDCA030", document.relative, "verification events require a valid actor and ISO 8601 at datetime")
            continue
        if require_review_run and not valid_run(event.get("review_run")):
            add(findings, "SDCA030", document.relative, "semantic verification events require review_run as a UUID URN")
        parsed.append((event, at))
    return parsed


def validate_sources(root: Path, document: Document, metadata: dict[str, Any], by_id: dict[str, Document], findings: list[Finding]) -> list[Document]:
    role = metadata.get("knowledge_role")
    original = metadata.get("original_record", False)
    if "original_record" in metadata and not isinstance(original, bool):
        add(findings, "SDCA020", document.relative, "original_record must be a boolean")
        original = False
    sources = metadata.get("sources")
    if role in {"canonical", "evidence"} and not original and not sources:
        add(findings, "SDCA020", document.relative, "canonical and evidence concepts require sources unless original_record is true")
        return []
    if sources is None:
        return []
    if not isinstance(sources, list) or not sources:
        add(findings, "SDCA020", document.relative, "sources must be a non-empty list of mappings")
        return []
    ids: set[str] = set()
    dependencies: list[Document] = []
    external_ids: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            add(findings, "SDCA021", document.relative, "each source must be a mapping")
            continue
        for field in ("id", "title", "resource", "source_kind"):
            if not isinstance(source.get(field), str) or not source[field].strip():
                add(findings, "SDCA021", document.relative, f"each source requires a non-empty {field} string")
        source_id = source.get("id")
        if isinstance(source_id, str):
            if source_id in ids:
                add(findings, "SDCA024", document.relative, f"duplicate source id: {source_id}")
            ids.add(source_id)
        kind = source.get("source_kind")
        if kind not in SOURCE_KINDS:
            add(findings, "SDCA026", document.relative, "source_kind must be internal, external, or scope")
            continue
        resource = source.get("resource")
        if not isinstance(resource, str) or not resource.strip():
            continue
        author = source.get("author")
        if author is not None and not valid_actor(author):
            add(findings, "SDCA021", document.relative, "source author must follow the OKF actor convention")
        if kind == "internal":
            dependency = internal_target(document, resource, by_id)
            if dependency is None:
                add(findings, "SDCA027", document.relative, f"internal source does not resolve to a concept: {resource}")
            else:
                dependencies.append(dependency)
        elif kind == "external":
            if isinstance(source_id, str):
                external_ids.add(source_id)
            retrieved = as_datetime(source.get("retrieved_at"))
            upstream = source.get("upstream_version")
            digest = source.get("sha256")
            if urlsplit(resource).scheme not in {"http", "https"}:
                add(findings, "SDCA022", document.relative, "external source resource must be an authoritative HTTP(S) URL")
            if retrieved is None or not isinstance(upstream, str) or not upstream.strip() or not isinstance(digest, str) or SHA256.fullmatch(digest) is None:
                add(findings, "SDCA022", document.relative, "external sources require retrieved_at, upstream_version, and lowercase SHA-256")
            artifact = source.get("local_artifact")
            if artifact is not None:
                if not isinstance(artifact, str) or artifact.endswith(".md") or artifact.startswith("/") or ".." in PurePosixPath(artifact).parts:
                    add(findings, "SDCA023", document.relative, "local_artifact must be a safe bundle-relative non-.md path")
                else:
                    artifact_path = root / artifact
                    if artifact_path.is_symlink():
                        add(findings, "SDCA023", document.relative, f"local artifact must not be a symlink: {artifact}")
                    elif not artifact_path.is_file():
                        add(findings, "SDCA023", document.relative, f"local artifact does not exist: {artifact}")
                    elif isinstance(digest, str) and SHA256.fullmatch(digest):
                        if hashlib.sha256(artifact_path.read_bytes()).hexdigest() != digest:
                            add(findings, "SDCA023", document.relative, f"local artifact fingerprint does not match: {artifact}")
                        elif tracked_artifact_was_modified(root, artifact):
                            add(findings, "SDCA023", document.relative, f"immutable local artifact has been modified in Git history or the worktree: {artifact}")
    references: set[str] = set()
    for line in document.prose_lines:
        if not re.match(r"^\s*\[\^[^\]]+\]:", line):
            references.update(FOOTNOTE.findall(line))
    missing = references - ids
    uncited_external = external_ids - references
    high_risk_canonical = role == "canonical" and metadata.get("type") in HIGH_RISK_TYPES
    uncited_high_risk = ids - references - external_ids if high_risk_canonical else set()
    if missing:
        add(findings, "SDCA025", document.relative, f"footnotes have no matching source id: {', '.join(sorted(missing))}")
    if uncited_external:
        add(findings, "SDCA025", document.relative, f"external sources are not joined from body footnotes: {', '.join(sorted(uncited_external))}")
    if uncited_high_risk:
        add(findings, "SDCA025", document.relative, f"high-risk canonical sources are not joined from body footnotes: {', '.join(sorted(uncited_high_risk))}")
    return dependencies


def validate_ticket(document: Document, metadata: dict[str, Any], findings: list[Finding]) -> None:
    ticket_type = metadata.get("ticket_type")
    ticket_status = metadata.get("ticket_status")
    body_type = re.search(r"^Type: (\S+)\s*$", document.body, re.M)
    body_status = re.search(r"^Status: (\S+)\s*$", document.body, re.M)
    if ticket_type not in TICKET_TYPES or ticket_status not in TICKET_STATUSES:
        add(findings, "SDCA035", document.relative, "ticket_type and ticket_status must use registered workflow values")
    if not body_type or not body_status or ticket_type != body_type.group(1) or ticket_status != body_status.group(1):
        add(findings, "SDCA035", document.relative, "ticket extensions must mirror the Type and Status body fields")
    expected = "stable" if ticket_status == "resolved" else "draft"
    if metadata.get("status") != expected:
        add(findings, "SDCA035", document.relative, f"{ticket_status} tickets must use OKF status {expected}")


def validate_decision(document: Document, metadata: dict[str, Any], findings: list[Finding]) -> None:
    decision = metadata.get("decision_status")
    if decision not in DECISION_STATUSES:
        add(findings, "SDCA036", document.relative, "decision_status must use the registered ADR vocabulary")
    elif decision == "proposed" and metadata.get("status") != "draft":
        add(findings, "SDCA036", document.relative, "proposed decisions must remain draft")
    elif decision == "accepted" and metadata.get("status") not in {"draft", "stable"}:
        add(findings, "SDCA036", document.relative, "accepted decisions must be draft or stable")
    elif decision in {"deprecated", "superseded"} and metadata.get("status") != "deprecated":
        add(findings, "SDCA036", document.relative, f"{decision} decisions must be deprecated")


def validate_supersession(document: Document, metadata: dict[str, Any], by_id: dict[str, Document], findings: list[Finding]) -> None:
    successor = metadata.get("superseded_by")
    if successor is None:
        return
    if metadata.get("status") != "deprecated" or not isinstance(successor, str) or successor.endswith(".md") or successor.startswith("/"):
        add(findings, "SDCA037", document.relative, "superseded_by requires a deprecated concept and repository-relative Concept ID without .md")
    elif successor not in by_id:
        add(findings, "SDCA038", document.relative, f"superseded_by target does not exist: {successor}")


def validate_stable_links(root: Path, document: Document, metadata: dict[str, Any], findings: list[Finding]) -> None:
    if metadata.get("status") != "stable":
        return
    for target in MARKDOWN_LINK.findall(document.prose):
        resolved = local_link_target(root, document, target)
        if resolved is None:
            continue
        try:
            resolved.resolve().relative_to(root.resolve())
        except ValueError:
            add(findings, "SDCA041", document.relative, f"stable concept link escapes the bundle: {target}")
            continue
        if not resolved.exists():
            add(findings, "SDCA041", document.relative, f"stable concept has a broken local link: {target}")


def validate_profile_index(reserved: dict[str, Document], concepts: list[Document], findings: list[Finding]) -> None:
    index = reserved.get("index.md")
    if index is None:
        add(findings, "SDCA007", "index.md", "the SmartDCA profile requires a root index")
        return
    if index.metadata != {"okf_version": "0.2"}:
        add(findings, "SDCA042", "index.md", "root index frontmatter must declare only okf_version: 0.2")
    if f"`{PROFILE_VERSION}`" not in index.body:
        add(findings, "SDCA042", "index.md", "root index body must declare the active SmartDCA profile")
    index_lines = index.body.splitlines()
    role_headings = [
        (line.removeprefix("## ").lower(), position)
        for position, line in enumerate(index_lines)
        if line in {"## Canonical", "## Evidence", "## Operational"}
    ]
    found_headings = [role for role, _ in role_headings]
    if found_headings != ["canonical", "evidence", "operational"]:
        add(findings, "SDCA043", "index.md", "index must contain Canonical, Evidence, and Operational sections in that order")
    else:
        for heading_index, (role, start) in enumerate(role_headings):
            end = role_headings[heading_index + 1][1] if heading_index + 1 < len(role_headings) else len(index_lines)
            section_lines = index_lines[start + 1:end]
            has_entries = any(line.startswith("- [") for line in section_lines)
            empty_marker_count = sum(line.strip() == "_None._" for line in section_lines)
            if (has_entries and empty_marker_count != 0) or (not has_entries and empty_marker_count != 1):
                add(findings, "SDCA043", "index.md", f"{role} section must contain entries or exactly one _None._ marker")
    current_role = None
    current_type = None
    rows: dict[str, tuple[dict[str, str], str]] = {}
    canonical_statuses: list[str] = []
    for line_number, line in enumerate(index_lines, 1):
        if line in {"## Canonical", "## Evidence", "## Operational"}:
            current_role = line.removeprefix("## ").lower()
            current_type = None
            continue
        if line.startswith("### "):
            current_type = line.removeprefix("### ").strip(" `")
            if current_role is None or current_type not in REGISTERED_TYPES:
                add(findings, "SDCA043", "index.md", f"invalid type subgroup at row {line_number}")
            continue
        if not line.startswith("- ["):
            continue
        match = INDEX_ROW.fullmatch(line)
        if not match or current_role is None or current_type is None:
            add(findings, "SDCA045", "index.md", f"index row {line_number} does not follow the profile row format")
            continue
        values = {key: value.strip() for key, value in match.groupdict().items()}
        if values["type"] != current_type:
            add(findings, "SDCA045", "index.md", f"index row {line_number} is not grouped under its type")
        if values["path"].startswith("/"):
            add(findings, "SDCA045", "index.md", f"index row {line_number} must use a bundle-relative link without a leading slash")
        path = values["path"].lstrip("/")
        if (
            not path.endswith(".md")
            or ".." in PurePosixPath(path).parts
            or path != posixpath.normpath(path)
        ):
            add(findings, "SDCA045", "index.md", f"index row {line_number} must link a safe bundle-relative .md path")
            continue
        if path in rows:
            add(findings, "SDCA044", "index.md", f"concept is listed more than once: {path}")
        rows[path] = (values, current_role)
        if current_role == "canonical":
            canonical_statuses.append(values["status"])
    seen_nonstable = False
    for status in canonical_statuses:
        if status != "stable":
            seen_nonstable = True
        elif seen_nonstable:
            add(findings, "SDCA043", "index.md", "stable canonical concepts must precede other canonical lifecycle states")
            break
    concept_paths = {document.relative for document in concepts}
    if set(rows) != concept_paths:
        missing = concept_paths - set(rows)
        extra = set(rows) - concept_paths
        details = []
        if missing:
            details.append("missing " + ", ".join(sorted(missing)))
        if extra:
            details.append("unknown " + ", ".join(sorted(extra)))
        add(findings, "SDCA044", "index.md", "index coverage is incomplete: " + "; ".join(details))
    for document in concepts:
        row = rows.get(document.relative)
        if row is None or document.metadata is None:
            continue
        values, role = row
        expected = {"title": document.metadata.get("title"), "description": document.metadata.get("description"), "type": document.metadata.get("type"), "status": document.metadata.get("status")}
        if role != document.metadata.get("knowledge_role") or any(values[key] != value for key, value in expected.items()):
            add(findings, "SDCA045", "index.md", f"index metadata does not match concept: {document.relative}")
        if not values["trust"] or not values["provenance"]:
            add(findings, "SDCA045", "index.md", f"index row lacks trust or provenance indicator: {document.relative}")


def validate_profile_log(root: Path, reserved: dict[str, Document], findings: list[Finding]) -> None:
    log = reserved.get("log.md")
    if log is None:
        add(findings, "SDCA046", "log.md", "the SmartDCA profile requires a root event log")
        return
    current_date = None
    groups = []
    for line in log.body.splitlines():
        date_match = DATE_HEADING.fullmatch(line)
        if date_match:
            current_date = date_match.group(1)
            groups.append(current_date)
        elif line.startswith(("- ", "* ")):
            match = LOG_ROW.fullmatch(line)
            if not match or current_date is None:
                add(findings, "SDCA046", "log.md", "each log bullet needs UTC timestamp, operation, title, and links")
            elif not match.group("timestamp").startswith(current_date) or not MARKDOWN_LINK.search(match.group("links")):
                add(findings, "SDCA046", "log.md", "log timestamp date must match its group and links must be Markdown")
    if not groups or groups != sorted(groups, reverse=True):
        add(findings, "SDCA046", "log.md", "log date groups must exist and be newest first")
    current_events = [line for line in log.body.splitlines() if line.startswith("- ")]
    for prior in git_file_versions(root, "log.md"):
        prior_events = [line for line in prior.splitlines() if line.startswith("- ")]
        if not is_subsequence(prior_events, current_events):
            add(findings, "SDCA047", "log.md", "existing log events were edited, deleted, or reordered")
            break


def validate_profile(root: Path, documents: list[Document]) -> list[Finding]:
    findings: list[Finding] = []
    concepts = [doc for doc in documents if Path(doc.relative).name not in RESERVED_NAMES]
    reserved = {doc.relative: doc for doc in documents if doc.relative in RESERVED_NAMES}
    by_id = {doc.concept_id: doc for doc in concepts}
    by_relative = {doc.relative: doc for doc in concepts}
    dependencies: dict[str, list[Document]] = {}
    verifications: dict[str, list[tuple[dict[str, Any], datetime]]] = {}
    for document in concepts:
        metadata = document.metadata
        if metadata is None:
            add(findings, "SDCA001", document.relative, "concept cannot satisfy the profile without frontmatter")
            continue
        for key in ("profile", "type", "title", "description", "knowledge_role", "status"):
            value = metadata.get(key)
            if not isinstance(value, str) or not value.strip():
                add(findings, "SDCA002", document.relative, f"profile requires a non-empty {key} string")
        if isinstance(metadata.get("description"), str) and "\n" in metadata["description"]:
            add(findings, "SDCA002", document.relative, "description must be one line")
        if metadata.get("profile") != PROFILE_VERSION:
            add(findings, "SDCA003", document.relative, f"profile must equal {PROFILE_VERSION}")
        if metadata.get("type") not in REGISTERED_TYPES:
            add(findings, "SDCA004", document.relative, "type is not registered by the SmartDCA profile")
        if metadata.get("knowledge_role") not in KNOWLEDGE_ROLES:
            add(findings, "SDCA005", document.relative, "knowledge_role must be canonical, evidence, or operational")
        if metadata.get("status") not in LIFECYCLE_STATUSES:
            add(findings, "SDCA006", document.relative, "status must be draft, stable, or deprecated")
        expected = expected_path_rule(document.relative)
        if expected is None:
            add(findings, "SDCA012", document.relative, "Markdown path is not assigned by the SmartDCA profile")
        else:
            expected_type, expected_role, expected_status = expected
            if metadata.get("type") != expected_type:
                add(findings, "SDCA010", document.relative, f"path requires type {expected_type}")
            if metadata.get("knowledge_role") != expected_role:
                add(findings, "SDCA011", document.relative, f"path requires knowledge_role {expected_role}")
            if expected_status is not None and metadata.get("status") != expected_status:
                add(findings, "SDCA013", document.relative, f"the path mapping requires status {expected_status}")
        if document.relative == "CONTEXT.md" and metadata.get("status") == "stable" and not metadata.get("sources"):
            add(findings, "SDCA014", document.relative, "stable canonical terminology requires recorded bootstrap sources")
        generated = metadata.get("generated")
        generated_at = None
        generation_run = metadata.get("generation_run")
        if generated is not None:
            if not isinstance(generated, dict) or not valid_actor(generated.get("by")) or as_datetime(generated.get("at")) is None:
                add(findings, "SDCA028", document.relative, "generated requires a valid actor and ISO 8601 at datetime")
            else:
                generated_at = as_datetime(generated["at"])
            if not valid_run(generation_run):
                add(findings, "SDCA029", document.relative, "agent generation requires generation_run as a UUID URN")
        elif generation_run is not None:
            add(findings, "SDCA029", document.relative, "generation_run is valid only with generated")
        high_risk = metadata.get("knowledge_role") == "canonical" and metadata.get("type") in HIGH_RISK_TYPES
        reviewed_note = metadata.get("type") == "research-note" and metadata.get("status") == "stable"
        require_review = metadata.get("status") == "stable" and (
            high_risk
            or reviewed_note
            or document.relative
            in {"README.md", "docs/knowledge/okf-profile.md", "docs/agents/llm-wiki-workflow.md"}
        )
        events = verification_events(document, metadata, findings, require_review)
        verifications[document.concept_id] = events
        if require_review:
            qualifying = [(event, at) for event, at in events if event.get("by") != SEMANTIC_CI_ACTOR and (generated_at is None or at >= generated_at)]
            if not qualifying:
                add(findings, "SDCA031", document.relative, "stable reviewed concept lacks a qualifying semantic verification after its last meaningful change")
            if valid_run(generation_run) and any(event.get("review_run") == generation_run for event, _ in events):
                add(findings, "SDCA032", document.relative, "review_run must be distinct from generation_run")
        stale_after = metadata.get("stale_after")
        if stale_after is not None:
            stale_date = as_date(stale_after)
            if stale_date is None:
                add(findings, "SDCA033", document.relative, "stale_after must be an absolute YYYY-MM-DD date")
            elif metadata.get("status") == "stable" and date.today() >= stale_date:
                add(findings, "SDCA033", document.relative, "stable concept is past stale_after")
        dependencies[document.concept_id] = validate_sources(root, document, metadata, by_id, findings)
        validate_supersession(document, metadata, by_id, findings)
        validate_stable_links(root, document, metadata, findings)
        if metadata.get("type") == "research-ticket":
            validate_ticket(document, metadata, findings)
        if metadata.get("type") == "decision-record":
            validate_decision(document, metadata, findings)
    for document in concepts:
        metadata = document.metadata
        if metadata is None or metadata.get("status") != "stable":
            continue
        latest = max(
            (
                at
                for event, at in verifications.get(document.concept_id, [])
                if event.get("by") != SEMANTIC_CI_ACTOR
            ),
            default=None,
        )
        for dependency in dependencies.get(document.concept_id, []):
            dep_meta = dependency.metadata or {}
            if dep_meta.get("status") != "stable":
                add(findings, "SDCA040", document.relative, f"stable concept depends on non-stable concept: {dependency.relative}")
                continue
            generated = dep_meta.get("generated")
            changed = as_datetime(generated.get("at")) if isinstance(generated, dict) else None
            if changed is not None and (latest is None or changed > latest):
                add(findings, "SDCA040", document.relative, f"dependency changed after the concept's latest verification: {dependency.relative}")
        if metadata.get("type") == "research-note":
            related = dependencies.get(document.concept_id, []) + linked_concepts(document, by_relative)
            has_resolved_ticket = any(
                (related_document.metadata or {}).get("type") == "research-ticket"
                and (related_document.metadata or {}).get("ticket_status") == "resolved"
                for related_document in related
            )
            if not has_resolved_ticket:
                add(findings, "SDCA034", document.relative, "stable research note must link a resolved research ticket")
    validate_profile_index(reserved, concepts, findings)
    validate_profile_log(root, reserved, findings)
    return sorted(set(findings))


def section(findings: list[Finding], warnings: list[Finding] | None = None) -> dict[str, Any]:
    warning_list = warnings or []
    return {
        "ok": not findings,
        "finding_count": len(findings),
        "findings": [asdict(finding) for finding in findings],
        "warning_count": len(warning_list),
        "warnings": [asdict(warning) for warning in warning_list],
    }


def build_report(root: Path, strict: bool = False) -> dict[str, Any]:
    base_findings, base_warnings, documents = validate_base(root)
    profile_findings = validate_profile(root, documents)
    return {
        "mode": "strict" if strict else "report", "root": str(root),
        "base_okf": section(base_findings, base_warnings),
        "smartdca_profile": section(profile_findings),
        "inventory": {
            "markdown_files": len(documents),
            "concepts": sum(Path(doc.relative).name not in RESERVED_NAMES for doc in documents),
            "reserved_files": sum(Path(doc.relative).name in RESERVED_NAMES for doc in documents),
        },
    }


def render_text(report: dict[str, Any]) -> str:
    strict = report["mode"] == "strict"
    lines = [f"SmartDCA OKF validation ({'blocking' if strict else 'report only'})"]
    for key, label in (("base_okf", "Base OKF v0.2"), ("smartdca_profile", PROFILE_VERSION)):
        result = report[key]
        lines.append(f"\n{label}: {'PASS' if result['ok'] else 'FINDINGS'} ({result['finding_count']})")
        for finding in result["findings"]:
            lines.append(f"- {finding['code']} {finding['path']}: {finding['message']}")
        for warning in result["warnings"]:
            lines.append(f"- {warning['code']} {warning['path']}: {warning['message']} (advisory)")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail with status 1 when either layer reports a conformance finding",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if not args.root.is_dir():
        print(f"error: bundle root is not a directory: {args.root}", file=sys.stderr)
        return 2
    report = build_report(args.root, strict=args.strict)
    if args.format == "json":
        json.dump(report, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_text(report))
    if args.strict and not (report["base_okf"]["ok"] and report["smartdca_profile"]["ok"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
