import json
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


VALIDATOR = Path(__file__).parents[1] / "validate.py"


class ValidatorCliTests(unittest.TestCase):
    def run_validator(self, files, baseline_files=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            if baseline_files is not None:
                self.write_files(root, baseline_files)
                for command in (
                    ["git", "init", "-q"],
                    ["git", "config", "user.name", "Validator Fixture"],
                    ["git", "config", "user.email", "fixture@example.test"],
                    ["git", "add", "."],
                    ["git", "commit", "-qm", "Add immutable source fixture"],
                ):
                    subprocess.run(command, cwd=root, check=True, capture_output=True, text=True)
            self.write_files(root, files)

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), str(root), "--format", "json"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            return json.loads(completed.stdout)

    def write_files(self, root, files):
        for relative_path, content in files.items():
            target = root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                target.write_bytes(content)
            else:
                target.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

    def codes(self, report, layer="smartdca_profile"):
        return {finding["code"] for finding in report[layer]["findings"]}

    def warning_codes(self, report, layer="base_okf"):
        return {warning["code"] for warning in report[layer]["warnings"]}

    def valid_index(self, rows):
        groups = {"canonical": [], "evidence": [], "operational": []}
        for row in rows:
            groups[row["role"]].append(
                f'- [{row["title"]}]({row["path"]}) — {row["description"]} — '
                f'type: {row["type"]}; status: {row["status"]}; '
                f'trust: {row.get("trust", "unverified")}; '
                f'provenance: {row.get("provenance", "original")}'
            )
        sections = []
        for role in ("canonical", "evidence", "operational"):
            if not groups[role]:
                entries = "_None._"
            else:
                by_type = {}
                for entry in groups[role]:
                    type_name = entry.split("type: ", 1)[1].split(";", 1)[0]
                    by_type.setdefault(type_name, []).append(entry)
                entries = "\n\n".join(
                    f"### {type_name}\n\n" + "\n".join(type_entries)
                    for type_name, type_entries in by_type.items()
                )
            sections.append(f"## {role.title()}\n\n{entries}")
        header = textwrap.dedent("""
            ---
            okf_version: "0.2"
            ---
            # SmartDCA knowledge index

            Active profile: `smartdca-okf/0.1`.

        """).lstrip()
        return header + "\n\n".join(sections) + "\n"

    def valid_log(self):
        return """
            # SmartDCA knowledge log

            ## 2026-08-15
            - 2026-08-15T12:00:00Z | Creation | Project overview | [README.md](README.md), [commit](https://example.test/commit)
        """

    def project_overview(self):
        return """
            ---
            profile: smartdca-okf/0.1
            type: project-overview
            title: Project overview
            description: The root orientation page for the research project.
            knowledge_role: canonical
            status: stable
            original_record: true
            verified:
              - by: human:github:razvan-tanase
                at: 2026-08-15T12:00:00Z
                review_run: urn:uuid:aaaaaaaa-aaaa-7aaa-8aaa-aaaaaaaaaaaa
            ---
            # Project overview
        """

    def concept(self, *, type_name, title, description, role, status, extra="", body=""):
        lines = [
            "---",
            "profile: smartdca-okf/0.1",
            f"type: {type_name}",
            f"title: {title}",
            f"description: {description}",
            f"knowledge_role: {role}",
            f"status: {status}",
            "original_record: true",
        ]
        if extra:
            lines.extend(textwrap.dedent(extra).strip().splitlines())
        lines.extend(["---", f"# {title}", ""])
        if body:
            lines.extend(textwrap.dedent(body).strip().splitlines())
        return "\n".join(lines) + "\n"

    def valid_minimal_bundle(self):
        row = {
            "path": "README.md",
            "title": "Project overview",
            "description": "The root orientation page for the research project.",
            "type": "project-overview",
            "role": "canonical",
            "status": "stable",
        }
        return {
            "README.md": self.project_overview(),
            "index.md": self.valid_index([row]),
            "log.md": self.valid_log(),
        }

    def test_report_mode_separates_base_and_profile_results(self):
        report = self.run_validator(
            {
                "concept.md": """
                    ---
                    type: Anything
                    ---
                    # Minimal concept
                """,
            }
        )

        self.assertEqual(report["mode"], "report")
        self.assertTrue(report["base_okf"]["ok"])
        self.assertFalse(report["smartdca_profile"]["ok"])

    def test_base_okf_is_deliberately_permissive(self):
        report = self.run_validator(
            {
                "mapping.md": """
                    ---
                    type: Future Type
                    unknown_extension: preserved
                    verified: {by: human:reviewer, at: 2026-08-15T12:00:00Z}
                    ---
                    See [a future concept](missing.md).
                """,
                "list.md": """
                    ---
                    type: Another Type
                    verified:
                      - {by: process:check, at: 2026-08-15T12:00:00Z}
                    ---
                    No explicit status is stable in base OKF.
                """,
            }
        )

        self.assertTrue(report["base_okf"]["ok"])
        self.assertFalse(report["base_okf"]["warnings"])

    def test_base_optional_family_problems_are_advisory_not_conformance_failures(self):
        report = self.run_validator(
            {
                "concept.md": """
                    ---
                    type: Attested Computation
                    status: accepted
                    generated: invalid
                    verified: invalid
                    sources: [{title: Missing resource}]
                    stale_after: someday
                    ---
                    # Advisory metadata fixture
                """,
            }
        )

        self.assertTrue(report["base_okf"]["ok"])
        self.assertEqual(
            self.warning_codes(report),
            {"OKFW001", "OKFW002", "OKFW003", "OKFW004", "OKFW005", "OKFW006"},
        )

    def test_new_untyped_markdown_is_reported_in_both_layers(self):
        files = self.valid_minimal_bundle()
        files["research/notes/untyped.md"] = "# Untyped new page\n"
        report = self.run_validator(files)

        self.assertIn("OKF001", self.codes(report, "base_okf"))
        self.assertIn("SDCA001", self.codes(report))

    def test_complete_minimal_smartdca_bundle_passes(self):
        report = self.run_validator(self.valid_minimal_bundle())

        self.assertTrue(report["base_okf"]["ok"])
        self.assertTrue(report["smartdca_profile"]["ok"], report["smartdca_profile"]["findings"])

    def test_path_mapping_and_universal_fields_are_enforced(self):
        files = self.valid_minimal_bundle()
        files["README.md"] = """
            ---
            profile: smartdca-okf/0.1
            type: theorem
            title: Wrong path type
            description: This path is deliberately misclassified.
            knowledge_role: evidence
            status: stable
            original_record: true
            ---
            # Wrong path type
        """
        report = self.run_validator(files)

        self.assertIn("SDCA010", self.codes(report))
        self.assertIn("SDCA011", self.codes(report))

    def test_complete_initial_path_mapping_accepts_each_assigned_path(self):
        definitions = [
            ("README.md", "project-overview", "Project", "Root orientation.", "canonical", "stable", "verified:\n  - by: human:github:razvan-tanase\n    at: 2026-08-15T12:00:00Z\n    review_run: urn:uuid:aaaaaaaa-aaaa-7aaa-8aaa-aaaaaaaaaaaa", ""),
            ("CONTEXT.md", "domain-glossary", "Context", "Canonical terminology.", "canonical", "draft", "", ""),
            ("AGENTS.md", "agent-instructions", "Agents", "Root agent invariants.", "operational", "stable", "", ""),
            ("docs/agents/domain.md", "agent-instructions", "Domain workflow", "Domain document workflow.", "operational", "stable", "", ""),
            ("docs/agents/triage-labels.md", "domain-glossary", "Triage labels", "Operational label vocabulary.", "operational", "stable", "", ""),
            ("docs/agents/issue-tracker.md", "workflow", "Issue tracker", "Ticket storage workflow.", "operational", "stable", "", ""),
            ("docs/agents/wayfinder-ticket-workflow.md", "workflow", "Wayfinder workflow", "Research ticket workflow.", "operational", "stable", "", ""),
            ("docs/agents/llm-wiki-workflow.md", "workflow", "LLM Wiki workflow", "Knowledge maintenance workflow.", "operational", "draft", "", ""),
            ("docs/knowledge/okf-profile.md", "specification", "OKF profile", "Normative local profile.", "canonical", "draft", "", ""),
            (".scratch/smartdca/map.md", "research-map", "Research map", "Authoritative project frontier.", "operational", "stable", "", ""),
            (".scratch/smartdca/issues/99-example.md", "research-ticket", "Open ticket", "Example open work item.", "operational", "draft", "ticket_type: task\nticket_status: open", "Type: task\nStatus: open"),
            ("docs/adr/0099-example.md", "decision-record", "Proposed decision", "Example proposed decision.", "canonical", "draft", "decision_status: proposed", ""),
            ("research/notes/example.md", "research-note", "Research evidence", "Example detailed evidence.", "evidence", "draft", "", ""),
        ]
        files = {}
        rows = []
        for path, type_name, title, description, role, status, extra, body in definitions:
            files[path] = self.concept(type_name=type_name, title=title, description=description, role=role, status=status, extra=extra, body=body)
            rows.append({"path": path, "title": title, "description": description, "type": type_name, "role": role, "status": status})
        files["index.md"] = self.valid_index(rows)
        files["log.md"] = self.valid_log()

        report = self.run_validator(files)
        self.assertTrue(report["smartdca_profile"]["ok"], report["smartdca_profile"]["findings"])

    def test_every_registered_type_is_recognized_before_a_path_is_assigned(self):
        registered = [
            "project-overview", "specification", "domain-glossary", "definition", "theorem",
            "research-note", "source-summary", "synthesis", "experiment-report", "decision-record",
            "research-map", "research-ticket", "workflow", "agent-instructions",
        ]
        files = {}
        rows = []
        for number, type_name in enumerate(registered):
            path = f"unassigned/{number:02d}-{type_name}.md"
            title = f"Registered {type_name}"
            description = f"Fixture for the {type_name} vocabulary entry."
            files[path] = self.concept(type_name=type_name, title=title, description=description, role="operational", status="draft")
            rows.append({"path": path, "title": title, "description": description, "type": type_name, "role": "operational", "status": "draft"})
        files["index.md"] = self.valid_index(rows)
        files["log.md"] = self.valid_log()

        report = self.run_validator(files)
        self.assertNotIn("SDCA004", self.codes(report))
        self.assertIn("SDCA012", self.codes(report))

    def test_external_sources_require_valid_raw_fingerprints_and_footnote_joins(self):
        raw = b"# Frozen upstream bytes\n"
        digest = hashlib.sha256(raw).hexdigest()
        files = {
            "research/notes/source.md": f"""
                ---
                profile: smartdca-okf/0.1
                type: research-note
                title: Source-backed note
                description: Evidence derived from a frozen external source.
                knowledge_role: evidence
                status: draft
                sources:
                  - id: upstream
                    title: Frozen upstream
                    resource: https://example.test/source
                    source_kind: external
                    retrieved_at: 2026-08-15T12:00:00Z
                    upstream_version: v1
                    sha256: {digest}
                    local_artifact: references/raw/source/v1/source.md.raw
                ---
                # Source-backed note

                A source-backed claim.[^upstream]

                [^upstream]: Frozen upstream
            """,
            "references/raw/source/v1/source.md.raw": raw,
            "log.md": self.valid_log(),
        }
        row = {
            "path": "research/notes/source.md",
            "title": "Source-backed note",
            "description": "Evidence derived from a frozen external source.",
            "type": "research-note",
            "role": "evidence",
            "status": "draft",
            "provenance": "external snapshot",
        }
        files["index.md"] = self.valid_index([row])
        passing = self.run_validator(files)
        self.assertTrue(passing["smartdca_profile"]["ok"], passing["smartdca_profile"]["findings"])

        files["research/notes/source.md"] = files["research/notes/source.md"].replace(digest, "f" * 64).replace("[^upstream]", "[^missing]", 1)
        failing = self.run_validator(files)
        self.assertIn("SDCA023", self.codes(failing))
        self.assertIn("SDCA025", self.codes(failing))

    def test_agent_generated_theorem_requires_distinct_fresh_semantic_review(self):
        theorem = """
            ---
            profile: smartdca-okf/0.1
            type: theorem
            title: Generated theorem
            description: A high-risk canonical theorem with claim provenance.
            knowledge_role: canonical
            status: stable
            sources:
              - id: proof
                title: Internal proof record
                resource: research/notes/proof
                source_kind: internal
            generated: {by: openai-codex/smartdca-wiki-0.1, at: 2026-08-15T12:00:00Z}
            generation_run: urn:uuid:11111111-1111-4111-8111-111111111111
            verified:
              - by: human:github:razvan-tanase
                at: 2026-08-15T13:00:00Z
                review_run: urn:uuid:22222222-2222-4222-8222-222222222222
            ---
            # Generated theorem

            The claim follows from its proof record.[^proof]

            [^proof]: Internal proof record
        """
        proof = """
            ---
            profile: smartdca-okf/0.1
            type: research-note
            title: Internal proof record
            description: Detailed evidence for the generated theorem.
            knowledge_role: evidence
            status: stable
            original_record: true
            verified:
              - by: human:github:razvan-tanase
                at: 2026-08-15T12:30:00Z
                review_run: urn:uuid:33333333-3333-4333-8333-333333333333
            ---
            # Internal proof record

            Reviewed through [the resolved proof ticket](/.scratch/smartdca/issues/99-proof.md).
        """
        ticket = self.concept(
            type_name="research-ticket",
            title="Resolved proof ticket",
            description="Review record for the proof evidence.",
            role="operational",
            status="stable",
            extra="ticket_type: research\nticket_status: resolved",
            body="Type: research\nStatus: resolved",
        )
        rows = [
            {"path": "knowledge/theorems/generated-theorem.md", "title": "Generated theorem", "description": "A high-risk canonical theorem with claim provenance.", "type": "theorem", "role": "canonical", "status": "stable", "trust": "human-reviewed", "provenance": "internal proof"},
            {"path": "research/notes/proof.md", "title": "Internal proof record", "description": "Detailed evidence for the generated theorem.", "type": "research-note", "role": "evidence", "status": "stable", "trust": "human-reviewed", "provenance": "original"},
            {"path": ".scratch/smartdca/issues/99-proof.md", "title": "Resolved proof ticket", "description": "Review record for the proof evidence.", "type": "research-ticket", "role": "operational", "status": "stable"},
        ]
        files = {"knowledge/theorems/generated-theorem.md": theorem, "research/notes/proof.md": proof, ".scratch/smartdca/issues/99-proof.md": ticket, "index.md": self.valid_index(rows), "log.md": self.valid_log()}
        passing = self.run_validator(files)
        self.assertEqual(self.codes(passing), {"SDCA012"})

        uncited_files = dict(files)
        uncited_files["knowledge/theorems/generated-theorem.md"] = theorem.replace(
            "The claim follows from its proof record.[^proof]",
            "The claim follows from its proof record.",
        )
        uncited = self.run_validator(uncited_files)
        self.assertIn("SDCA025", self.codes(uncited))

        files["knowledge/theorems/generated-theorem.md"] = theorem.replace("13:00:00Z", "11:00:00Z").replace("22222222-2222-4222-8222-222222222222", "11111111-1111-4111-8111-111111111111")
        failing = self.run_validator(files)
        self.assertIn("SDCA031", self.codes(failing))
        self.assertIn("SDCA032", self.codes(failing))

    def test_ticket_and_adr_extensions_mirror_body_state(self):
        ticket = """
            ---
            profile: smartdca-okf/0.1
            type: research-ticket
            title: Resolved ticket
            description: A resolved research task and its answer.
            knowledge_role: operational
            status: stable
            original_record: true
            ticket_type: task
            ticket_status: resolved
            ---
            # Resolved ticket

            Type: task
            Status: resolved
        """
        adr = """
            ---
            profile: smartdca-okf/0.1
            type: decision-record
            title: Accepted decision
            description: A reviewed architectural decision.
            knowledge_role: canonical
            status: stable
            original_record: true
            decision_status: accepted
            verified:
              - by: human:github:razvan-tanase
                at: 2026-08-15T13:00:00Z
                review_run: urn:uuid:44444444-4444-4444-8444-444444444444
            ---
            # Accepted decision
        """
        rows = [
            {"path": ".scratch/smartdca/issues/99-example.md", "title": "Resolved ticket", "description": "A resolved research task and its answer.", "type": "research-ticket", "role": "operational", "status": "stable"},
            {"path": "docs/adr/0099-example.md", "title": "Accepted decision", "description": "A reviewed architectural decision.", "type": "decision-record", "role": "canonical", "status": "stable", "trust": "human-reviewed"},
        ]
        files = {".scratch/smartdca/issues/99-example.md": ticket, "docs/adr/0099-example.md": adr, "index.md": self.valid_index(rows), "log.md": self.valid_log()}
        passing = self.run_validator(files)
        self.assertTrue(passing["smartdca_profile"]["ok"], passing["smartdca_profile"]["findings"])

        files[".scratch/smartdca/issues/99-example.md"] = ticket.replace("ticket_status: resolved", "ticket_status: open")
        files["docs/adr/0099-example.md"] = adr.replace("decision_status: accepted", "decision_status: proposed")
        failing = self.run_validator(files)
        self.assertIn("SDCA035", self.codes(failing))
        self.assertIn("SDCA036", self.codes(failing))

    def test_dependency_changes_make_a_stable_dependent_stale(self):
        dependency = """
            ---
            profile: smartdca-okf/0.1
            type: research-note
            title: Dependency
            description: Evidence changed after its dependent was reviewed.
            knowledge_role: evidence
            status: draft
            original_record: true
            generated: {by: openai-codex/smartdca-wiki-0.1, at: 2026-08-15T14:00:00Z}
            generation_run: urn:uuid:55555555-5555-4555-8555-555555555555
            verified:
              - by: human:github:razvan-tanase
                at: 2026-08-15T14:30:00Z
                review_run: urn:uuid:66666666-6666-4666-8666-666666666666
            ---
            # Dependency
        """
        dependent = """
            ---
            profile: smartdca-okf/0.1
            type: theorem
            title: Dependent theorem
            description: A theorem whose dependency changed after review.
            knowledge_role: canonical
            status: stable
            sources:
              - id: dep
                title: Dependency
                resource: research/notes/dependency
                source_kind: internal
            verified:
              - by: human:github:razvan-tanase
                at: 2026-08-15T13:00:00Z
                review_run: urn:uuid:77777777-7777-4777-8777-777777777777
              - by: process:github-actions:smartdca-wiki-ci
                at: 2026-08-15T15:00:00Z
                review_run: urn:uuid:12121212-1212-4212-8212-121212121212
            ---
            # Dependent theorem

            A dependent claim.[^dep]

            [^dep]: Dependency
        """
        rows = [
            {"path": "research/notes/dependent.md", "title": "Dependent theorem", "description": "A theorem whose dependency changed after review.", "type": "theorem", "role": "canonical", "status": "stable", "trust": "human-reviewed", "provenance": "internal"},
            {"path": "research/notes/dependency.md", "title": "Dependency", "description": "Evidence changed after its dependent was reviewed.", "type": "research-note", "role": "evidence", "status": "stable", "trust": "human-reviewed"},
        ]
        report = self.run_validator({"research/notes/dependency.md": dependency, "research/notes/dependent.md": dependent, "index.md": self.valid_index(rows), "log.md": self.valid_log()})
        self.assertIn("SDCA040", self.codes(report))

    def test_reserved_log_and_complete_role_grouped_index_are_enforced(self):
        files = self.valid_minimal_bundle()
        files["index.md"] = files["index.md"].replace("## Canonical", "## Operational")
        files["log.md"] = """
            # SmartDCA knowledge log
            ## 15-08-2026
            - Creation without a timestamp or links
        """
        report = self.run_validator(files)

        self.assertIn("OKF012", self.codes(report, "base_okf"))
        self.assertIn("SDCA043", self.codes(report))
        self.assertIn("SDCA046", self.codes(report))

    def test_existing_log_events_cannot_be_edited_or_deleted(self):
        baseline = self.valid_minimal_bundle()
        modified = dict(baseline)
        modified["log.md"] = baseline["log.md"].replace(
            "Creation | Project overview",
            "Update | Rewritten historical event",
        )

        report = self.run_validator(modified, baseline_files=baseline)
        self.assertIn("SDCA047", self.codes(report))

    def test_raw_markdown_is_preserved_below_a_non_markdown_suffix(self):
        files = self.valid_minimal_bundle()
        files["references/raw/upstream/source.md.raw"] = b"# no frontmatter because these are exact upstream bytes\n"
        report = self.run_validator(files)

        self.assertEqual(report["inventory"]["markdown_files"], 3)
        self.assertTrue(report["smartdca_profile"]["ok"], report["smartdca_profile"]["findings"])

    def test_conflict_synthesis_remains_draft_and_path_moves_keep_forwarders(self):
        evidence = """
            ---
            profile: smartdca-okf/0.1
            type: research-note
            title: Evidence {number}
            description: One side of a preserved source conflict.
            knowledge_role: evidence
            status: stable
            original_record: true
            verified:
              - by: human:github:razvan-tanase
                at: 2026-08-15T13:00:00Z
                review_run: urn:uuid:88888888-8888-4888-8888-888888888888
            ---
            # Evidence {number}

            Reviewed through [the resolved evidence ticket](/.scratch/smartdca/issues/98-evidence.md).
        """
        synthesis = """
            ---
            profile: smartdca-okf/0.1
            type: synthesis
            title: Unresolved synthesis
            description: The conflict is preserved pending independent review.
            knowledge_role: canonical
            status: draft
            sources:
              - {id: one, title: Evidence 1, resource: research/notes/evidence-1, source_kind: internal}
              - {id: two, title: Evidence 2, resource: research/notes/evidence-2, source_kind: internal}
            ---
            # Unresolved synthesis
            Evidence remains contradictory.[^one][^two]

            [^one]: Evidence 1
            [^two]: Evidence 2
        """
        successor = """
            ---
            profile: smartdca-okf/0.1
            type: research-note
            title: New concept path
            description: The current home of a moved stable concept.
            knowledge_role: evidence
            status: stable
            original_record: true
            verified:
              - by: human:github:razvan-tanase
                at: 2026-08-15T13:00:00Z
                review_run: urn:uuid:99999999-9999-4999-8999-999999999999
            ---
            # New concept path

            Reviewed through [the resolved evidence ticket](/.scratch/smartdca/issues/98-evidence.md).
        """
        forwarder = """
            ---
            profile: smartdca-okf/0.1
            type: research-note
            title: Old concept path
            description: Deprecated forwarding concept preserving stable identity.
            knowledge_role: evidence
            status: deprecated
            original_record: true
            superseded_by: research/notes/new-path
            ---
            # Moved
            See [the current concept](new-path.md).
        """
        rows = [
            {"path": "knowledge/syntheses/unresolved.md", "title": "Unresolved synthesis", "description": "The conflict is preserved pending independent review.", "type": "synthesis", "role": "canonical", "status": "draft", "provenance": "conflicting evidence"},
            {"path": "research/notes/evidence-1.md", "title": "Evidence 1", "description": "One side of a preserved source conflict.", "type": "research-note", "role": "evidence", "status": "stable", "trust": "human-reviewed"},
            {"path": "research/notes/evidence-2.md", "title": "Evidence 2", "description": "One side of a preserved source conflict.", "type": "research-note", "role": "evidence", "status": "stable", "trust": "human-reviewed"},
            {"path": "research/notes/new-path.md", "title": "New concept path", "description": "The current home of a moved stable concept.", "type": "research-note", "role": "evidence", "status": "stable"},
            {"path": "research/notes/old-path.md", "title": "Old concept path", "description": "Deprecated forwarding concept preserving stable identity.", "type": "research-note", "role": "evidence", "status": "deprecated"},
            {"path": ".scratch/smartdca/issues/98-evidence.md", "title": "Resolved evidence ticket", "description": "Review record for stable evidence concepts.", "type": "research-ticket", "role": "operational", "status": "stable"},
        ]
        ticket = self.concept(
            type_name="research-ticket",
            title="Resolved evidence ticket",
            description="Review record for stable evidence concepts.",
            role="operational",
            status="stable",
            extra="ticket_type: research\nticket_status: resolved",
            body="Type: research\nStatus: resolved",
        )
        files = {
            "research/notes/evidence-1.md": evidence.format(number=1),
            "research/notes/evidence-2.md": evidence.format(number=2),
            "knowledge/syntheses/unresolved.md": synthesis,
            "research/notes/new-path.md": successor,
            "research/notes/old-path.md": forwarder,
            ".scratch/smartdca/issues/98-evidence.md": ticket,
            "index.md": self.valid_index(rows),
            "log.md": self.valid_log(),
        }
        report = self.run_validator(files)
        self.assertEqual(self.codes(report), {"SDCA012"})

    def test_revised_external_source_uses_a_new_raw_artifact(self):
        raw_v1 = b"version one\n"
        raw_v2 = b"version two\n"
        concept = f"""
            ---
            profile: smartdca-okf/0.1
            type: research-note
            title: Versioned source summary
            description: Two immutable editions of one external source.
            knowledge_role: evidence
            status: draft
            sources:
              - id: v1
                title: Upstream v1
                resource: https://example.test/source/v1
                source_kind: external
                retrieved_at: 2026-08-14T12:00:00Z
                upstream_version: v1
                sha256: {hashlib.sha256(raw_v1).hexdigest()}
                local_artifact: references/raw/source/v1/source.md.raw
              - id: v2
                title: Upstream v2
                resource: https://example.test/source/v2
                source_kind: external
                retrieved_at: 2026-08-15T12:00:00Z
                upstream_version: v2
                sha256: {hashlib.sha256(raw_v2).hexdigest()}
                local_artifact: references/raw/source/v2/source.md.raw
            ---
            # Versioned source summary
            Compare the frozen editions.[^v1][^v2]

            [^v1]: Upstream v1
            [^v2]: Upstream v2
        """
        row = {"path": "research/notes/versioned-source.md", "title": "Versioned source summary", "description": "Two immutable editions of one external source.", "type": "research-note", "role": "evidence", "status": "draft", "provenance": "two snapshots"}
        files = {
            "research/notes/versioned-source.md": concept,
            "references/raw/source/v1/source.md.raw": raw_v1,
            "references/raw/source/v2/source.md.raw": raw_v2,
            "index.md": self.valid_index([row]),
            "log.md": self.valid_log(),
        }
        report = self.run_validator(files)
        self.assertTrue(report["smartdca_profile"]["ok"], report["smartdca_profile"]["findings"])

        overwritten = b"silently overwritten version one\n"
        modified_files = dict(files)
        modified_files["references/raw/source/v1/source.md.raw"] = overwritten
        modified_files["research/notes/versioned-source.md"] = concept.replace(
            hashlib.sha256(raw_v1).hexdigest(),
            hashlib.sha256(overwritten).hexdigest(),
        )
        history_report = self.run_validator(modified_files, baseline_files=files)
        self.assertIn("SDCA023", self.codes(history_report))

    def test_invalid_conditional_metadata_and_stable_links_are_reported(self):
        files = self.valid_minimal_bundle()
        files["README.md"] = """
            ---
            profile: smartdca-okf/0.1
            type: project-overview
            title: Project overview
            description: A deliberately invalid conditional-metadata fixture.
            knowledge_role: canonical
            status: stable
            original_record: not-a-boolean
            generated: {by: invalid-actor, at: yesterday}
            generation_run: not-a-uuid
            stale_after: 2000-01-01
            sources:
              - {id: scope, title: Scope, resource: all project queries, source_kind: scope}
              - {id: missing-resource, title: Missing resource, source_kind: internal}
            ---
            # Project overview
            See [missing](missing.md).
        """
        rows = [{"path": "README.md", "title": "Project overview", "description": "A deliberately invalid conditional-metadata fixture.", "type": "project-overview", "role": "canonical", "status": "stable"}]
        files["index.md"] = self.valid_index(rows)
        report = self.run_validator(files)

        codes = self.codes(report)
        self.assertIn("SDCA020", codes)
        self.assertIn("SDCA021", codes)
        self.assertIn("SDCA028", codes)
        self.assertIn("SDCA029", codes)
        self.assertIn("SDCA033", codes)
        self.assertIn("SDCA041", codes)
        self.assertNotIn("SDCA026", codes)

    def test_index_requires_complete_coverage_and_stable_canonical_first(self):
        files = self.valid_minimal_bundle()
        context = self.concept(type_name="domain-glossary", title="Context", description="Draft canonical terminology.", role="canonical", status="draft")
        files["CONTEXT.md"] = context
        rows = [
            {"path": "CONTEXT.md", "title": "Context", "description": "Draft canonical terminology.", "type": "domain-glossary", "role": "canonical", "status": "draft"},
            {"path": "README.md", "title": "Project overview", "description": "The root orientation page for the research project.", "type": "project-overview", "role": "canonical", "status": "stable"},
        ]
        files["index.md"] = self.valid_index(rows)
        ordering = self.run_validator(files)
        self.assertIn("SDCA043", self.codes(ordering))

        files["index.md"] = self.valid_index(rows[:1])
        coverage = self.run_validator(files)
        self.assertIn("SDCA044", self.codes(coverage))

        absolute_files = self.valid_minimal_bundle()
        absolute_files["index.md"] = absolute_files["index.md"].replace("(README.md)", "(/README.md)")
        absolute = self.run_validator(absolute_files)
        self.assertIn("SDCA045", self.codes(absolute))

        empty_marker_files = self.valid_minimal_bundle()
        empty_marker_files["index.md"] = empty_marker_files["index.md"].replace("_None._", "", 1)
        empty_marker = self.run_validator(empty_marker_files)
        self.assertIn("SDCA043", self.codes(empty_marker))


if __name__ == "__main__":
    unittest.main()
