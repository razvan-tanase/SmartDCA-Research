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
    def run_cli(self, files, *arguments, baseline_files=None):
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
                [sys.executable, str(VALIDATOR), str(root), "--format", "json", *arguments],
                check=False,
                capture_output=True,
                text=True,
            )
            return completed.returncode, json.loads(completed.stdout)

    def run_validator(self, files, baseline_files=None):
        status, report = self.run_cli(files, baseline_files=baseline_files)
        self.assertEqual(status, 0, report)
        return report

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

            Active profile: `smartdca-okf/0.5`.

        """).lstrip()
        return header + "\n\n".join(sections) + "\n"

    def valid_log(self):
        return """
            # SmartDCA knowledge log

            ## 2026-08-15
            - 2026-08-15T12:00:00Z | Creation | Project overview | [README.md](README.md), [commit](https://example.test/commit)
        """

    def project_overview(self):
        return "# Project overview"

    def concept(self, *, type_name, title, description, role, status, extra="", body=""):
        lines = [
            "---",
            "profile: smartdca-okf/0.5",
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
        return {
            "README.md": self.project_overview(),
            "index.md": self.valid_index([]),
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

    def test_plain_root_readme_is_not_a_concept(self):
        files = self.valid_minimal_bundle()
        report = self.run_validator(files)

        self.assertTrue(report["base_okf"]["ok"], report["base_okf"]["findings"])
        self.assertTrue(report["smartdca_profile"]["ok"], report["smartdca_profile"]["findings"])
        self.assertNotIn("OKF001", self.codes(report, "base_okf"))

    def test_agents_tree_is_outside_both_validation_layers(self):
        path = ".agents/skills/implement/SKILL.md"
        skill = """
            ---
            name: implement
            description: "Implement a piece of work based on a spec or set of tickets."
            disable-model-invocation: true
            ---

            Implement the work described by the user in the spec or tickets.
        """
        files = self.valid_minimal_bundle()
        files[path] = skill

        report = self.run_validator(files)

        self.assertEqual(report["inventory"], {"markdown_files": 2, "concepts": 0, "reserved_files": 2})
        self.assertTrue(report["base_okf"]["ok"], report["base_okf"]["findings"])
        self.assertTrue(report["smartdca_profile"]["ok"], report["smartdca_profile"]["findings"])

    def test_non_agent_hidden_directories_remain_in_the_bundle(self):
        files = self.valid_minimal_bundle()
        files[".hidden/untyped.md"] = "# Untyped hidden concept\n"

        report = self.run_validator(files)

        self.assertEqual(report["inventory"], {"markdown_files": 3, "concepts": 1, "reserved_files": 2})
        self.assertIn("OKF001", self.codes(report, "base_okf"))
        self.assertIn("SDCA001", self.codes(report))

    def test_agents_tree_cannot_be_listed_in_the_root_index(self):
        path = ".agents/skills/example/guide.md"
        row = {
            "path": path,
            "title": "Example skill guide",
            "description": "Supporting instructions for a repository-local skill.",
            "type": "agent-instructions",
            "role": "operational",
            "status": "stable",
        }
        files = self.valid_minimal_bundle()
        files[path] = self.concept(
            type_name="agent-instructions",
            title="Example skill guide",
            description="Supporting instructions for a repository-local skill.",
            role="operational",
            status="stable",
        )
        files["index.md"] = self.valid_index([row])

        report = self.run_validator(files)

        self.assertTrue(report["base_okf"]["ok"], report["base_okf"]["findings"])
        self.assertEqual(self.codes(report), {"SDCA044"})

    def test_complete_minimal_smartdca_bundle_passes(self):
        report = self.run_validator(self.valid_minimal_bundle())

        self.assertTrue(report["base_okf"]["ok"])
        self.assertTrue(report["smartdca_profile"]["ok"], report["smartdca_profile"]["findings"])

    def test_path_mapping_and_universal_fields_are_enforced(self):
        files = self.valid_minimal_bundle()
        files["AGENTS.md"] = """
            ---
            profile: smartdca-okf/0.5
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

    def test_complete_path_mapping_accepts_each_assigned_path(self):
        definitions = [
            ("CONTEXT.md", "domain-glossary", "Context", "Canonical terminology.", "canonical", "draft", "", ""),
            ("AGENTS.md", "agent-instructions", "Agents", "Root agent invariants.", "operational", "stable", "", ""),
            ("docs/agents/domain.md", "agent-instructions", "Domain workflow", "Domain document workflow.", "operational", "stable", "", ""),
            ("docs/agents/triage-labels.md", "domain-glossary", "Triage labels", "Operational label vocabulary.", "operational", "stable", "", ""),
            ("docs/agents/issue-tracker.md", "workflow", "Issue tracker", "Ticket storage workflow.", "operational", "stable", "", ""),
            ("docs/agents/wayfinder-ticket-workflow.md", "workflow", "Wayfinder workflow", "Research ticket workflow.", "operational", "stable", "", ""),
            ("docs/agents/llm-wiki-workflow.md", "workflow", "LLM Wiki workflow", "Knowledge maintenance workflow.", "operational", "draft", "", ""),
            ("docs/knowledge/okf-profile.md", "specification", "OKF profile", "Normative local profile.", "canonical", "draft", "", ""),
            (".scratch/smartdca/map.md", "research-map", "Research map", "Authoritative project frontier.", "operational", "stable", "", ""),
            (".scratch/smartdca/issues/99-example.md", "research-ticket", "Resolved legacy ticket", "Example archived work item.", "operational", "stable", "ticket_type: task\nticket_status: resolved", "Type: task\nStatus: resolved"),
            (".scratch/smartdca/efforts/example/spec.md", "work-specification", "Example effort specification", "Approved contract for an active effort.", "operational", "stable", "", ""),
            (".scratch/smartdca/efforts/example/map.md", "research-map", "Example effort map", "Current state inside an active effort.", "operational", "stable", "", ""),
            (".scratch/smartdca/efforts/example/issues/01-example.md", "research-ticket", "Open effort ticket", "Example active work item.", "operational", "draft", "ticket_type: task\nticket_status: open", "Type: task\nStatus: open\nBlocked by: none"),
            ("docs/adr/0099-example.md", "decision-record", "Proposed decision", "Example proposed decision.", "canonical", "draft", "decision_status: proposed", ""),
            ("research/notes/example.md", "research-note", "Research evidence", "Example detailed evidence.", "evidence", "draft", "", ""),
            ("references/summaries/example.md", "source-summary", "Ingested source", "Example single-source summary.", "evidence", "draft", "", ""),
            ("research/synthesis/example.md", "synthesis", "Cross-source synthesis", "Example cross-source integration.", "canonical", "draft", "", ""),
            ("research/definitions/example.md", "definition", "Named construction", "Example canonical definition.", "canonical", "draft", "", ""),
            ("research/theorems/example.md", "theorem", "Proved statement", "Example canonical theorem.", "canonical", "draft", "", ""),
            ("reports/experiments/example.md", "experiment-report", "Executed run", "Example experiment report.", "evidence", "draft", "", ""),
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

    def test_profile_05_semantic_paths_pin_their_type_and_role(self):
        """Each 0.5 path must report the exact rule it breaks, per path.

        Asserting the codes only in aggregate would still pass if one path
        were mapped to the wrong type and role entirely, so every case is
        checked against the findings recorded for its own file.
        """
        cases = [
            ("research/theorems/wrong.md", "research-note", "evidence", {"SDCA010", "SDCA011"}),
            ("research/definitions/wrong.md", "theorem", "canonical", {"SDCA010"}),
            ("reports/experiments/wrong.md", "experiment-report", "canonical", {"SDCA011"}),
        ]
        for path, type_name, role, expected in cases:
            with self.subTest(path=path):
                title = f"Misplaced {type_name}"
                description = f"Fixture placing a {type_name} at {path}."
                row = {
                    "path": "README.md",
                    "title": "Project overview",
                    "description": "The root orientation page for the research project.",
                    "type": "project-overview",
                    "role": "canonical",
                    "status": "stable",
                }
                misplaced_row = {"path": path, "title": title, "description": description, "type": type_name, "role": role, "status": "draft"}
                files = self.valid_minimal_bundle()
                files[path] = self.concept(type_name=type_name, title=title, description=description, role=role, status="draft")
                files["index.md"] = self.valid_index([row, misplaced_row])
                report = self.run_validator(files)

                reported = {
                    finding["code"]
                    for finding in report["smartdca_profile"]["findings"]
                    if finding["path"] == path
                }
                self.assertEqual(reported & {"SDCA010", "SDCA011"}, expected)
                self.assertNotIn("SDCA012", reported)

    def test_every_registered_type_is_recognized_before_a_path_is_assigned(self):
        registered = [
            "project-overview", "specification", "work-specification", "domain-glossary", "definition", "theorem",
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

    def test_effort_tickets_require_a_specification_and_map(self):
        files = self.valid_minimal_bundle()
        path = ".scratch/smartdca/efforts/example/issues/01-example.md"
        files[path] = self.concept(
            type_name="research-ticket",
            title="Open effort ticket",
            description="An active ticket without its effort anchors.",
            role="operational",
            status="draft",
            extra="ticket_type: task\nticket_status: open",
            body="Type: task\nStatus: open\nBlocked by: none",
        )
        files["index.md"] = self.valid_index([{
            "path": path,
            "title": "Open effort ticket",
            "description": "An active ticket without its effort anchors.",
            "type": "research-ticket",
            "role": "operational",
            "status": "draft",
        }])

        report = self.run_validator(files)
        self.assertIn("SDCA049", self.codes(report))

    def test_legacy_ticket_directory_accepts_only_resolved_history(self):
        files = self.valid_minimal_bundle()
        path = ".scratch/smartdca/issues/99-open.md"
        files[path] = self.concept(
            type_name="research-ticket",
            title="Open legacy ticket",
            description="An active ticket in the historical archive.",
            role="operational",
            status="draft",
            extra="ticket_type: task\nticket_status: open",
            body="Type: task\nStatus: open\nBlocked by: none",
        )
        files["index.md"] = self.valid_index([{
            "path": path,
            "title": "Open legacy ticket",
            "description": "An active ticket in the historical archive.",
            "type": "research-ticket",
            "role": "operational",
            "status": "draft",
        }])

        report = self.run_validator(files)
        self.assertIn("SDCA048", self.codes(report))

    def test_effort_tickets_require_an_approved_stable_specification(self):
        files = self.valid_minimal_bundle()
        spec_path = ".scratch/smartdca/efforts/example/spec.md"
        map_path = ".scratch/smartdca/efforts/example/map.md"
        ticket_path = ".scratch/smartdca/efforts/example/issues/01-example.md"
        files[spec_path] = self.concept(
            type_name="work-specification",
            title="Draft effort specification",
            description="An effort contract still awaiting approval.",
            role="operational",
            status="draft",
        )
        files[map_path] = self.concept(
            type_name="research-map",
            title="Example effort map",
            description="The state map for the example effort.",
            role="operational",
            status="stable",
        )
        files[ticket_path] = self.concept(
            type_name="research-ticket",
            title="Premature effort ticket",
            description="A ticket published before its effort contract was approved.",
            role="operational",
            status="draft",
            extra="ticket_type: task\nticket_status: open",
            body="Type: task\nStatus: open",
        )
        rows = [
            {"path": spec_path, "title": "Draft effort specification", "description": "An effort contract still awaiting approval.", "type": "work-specification", "role": "operational", "status": "draft"},
            {"path": map_path, "title": "Example effort map", "description": "The state map for the example effort.", "type": "research-map", "role": "operational", "status": "stable"},
            {"path": ticket_path, "title": "Premature effort ticket", "description": "A ticket published before its effort contract was approved.", "type": "research-ticket", "role": "operational", "status": "draft"},
        ]
        files["index.md"] = self.valid_index(rows)

        report = self.run_validator(files)
        self.assertIn("SDCA050", self.codes(report))

    def test_effort_ticket_filename_must_use_local_number_and_slug(self):
        files = self.valid_minimal_bundle()
        spec_path = ".scratch/smartdca/efforts/example/spec.md"
        map_path = ".scratch/smartdca/efforts/example/map.md"
        bad_path = ".scratch/smartdca/efforts/example/issues/accounting.md"
        files[spec_path] = self.concept(type_name="work-specification", title="Example specification", description="The approved example contract.", role="operational", status="stable")
        files[map_path] = self.concept(type_name="research-map", title="Example map", description="The example effort state.", role="operational", status="stable")
        files[bad_path] = self.concept(
            type_name="research-ticket",
            title="Malformed ticket",
            description="An active ticket with a malformed path.",
            role="operational",
            status="draft",
            extra="ticket_type: task\nticket_status: open",
            body="Type: task\nStatus: open\nBlocked by: none",
        )
        rows = [
            {"path": spec_path, "title": "Example specification", "description": "The approved example contract.", "type": "work-specification", "role": "operational", "status": "stable"},
            {"path": map_path, "title": "Example map", "description": "The example effort state.", "type": "research-map", "role": "operational", "status": "stable"},
            {"path": bad_path, "title": "Malformed ticket", "description": "An active ticket with a malformed path.", "type": "research-ticket", "role": "operational", "status": "draft"},
        ]
        files["index.md"] = self.valid_index(rows)

        report = self.run_validator(files)
        self.assertIn("SDCA012", self.codes(report))

    def test_effort_ticket_blocker_must_resolve(self):
        files = self.valid_minimal_bundle()
        spec_path = ".scratch/smartdca/efforts/example/spec.md"
        map_path = ".scratch/smartdca/efforts/example/map.md"
        ticket_path = ".scratch/smartdca/efforts/example/issues/01-accounting.md"
        files[spec_path] = self.concept(type_name="work-specification", title="Example specification", description="The approved example contract.", role="operational", status="stable")
        files[map_path] = self.concept(type_name="research-map", title="Example map", description="The example effort state.", role="operational", status="stable")
        files[ticket_path] = self.concept(
            type_name="research-ticket",
            title="Blocked ticket",
            description="An active ticket with an unresolved blocker.",
            role="operational",
            status="draft",
            extra="ticket_type: task\nticket_status: open",
            body="Type: task\nStatus: open\nBlocked by: 99",
        )
        rows = [
            {"path": spec_path, "title": "Example specification", "description": "The approved example contract.", "type": "work-specification", "role": "operational", "status": "stable"},
            {"path": map_path, "title": "Example map", "description": "The example effort state.", "type": "research-map", "role": "operational", "status": "stable"},
            {"path": ticket_path, "title": "Blocked ticket", "description": "An active ticket with an unresolved blocker.", "type": "research-ticket", "role": "operational", "status": "draft"},
        ]
        files["index.md"] = self.valid_index(rows)

        report = self.run_validator(files)
        self.assertIn("SDCA051", self.codes(report))

    def test_external_sources_require_valid_raw_fingerprints_and_footnote_joins(self):
        raw = b"# Frozen upstream bytes\n"
        digest = hashlib.sha256(raw).hexdigest()
        files = {
            "research/notes/source.md": f"""
                ---
                profile: smartdca-okf/0.5
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
            profile: smartdca-okf/0.5
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
            profile: smartdca-okf/0.5
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
            profile: smartdca-okf/0.5
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
            profile: smartdca-okf/0.5
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
            profile: smartdca-okf/0.5
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
            profile: smartdca-okf/0.5
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

        self.assertEqual(report["inventory"]["markdown_files"], 2)
        self.assertTrue(report["smartdca_profile"]["ok"], report["smartdca_profile"]["findings"])

    def test_conflict_synthesis_remains_draft_and_path_moves_keep_forwarders(self):
        evidence = """
            ---
            profile: smartdca-okf/0.5
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
            profile: smartdca-okf/0.5
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
            profile: smartdca-okf/0.5
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
            profile: smartdca-okf/0.5
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
            profile: smartdca-okf/0.5
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
        files["research/notes/invalid.md"] = """
            ---
            profile: smartdca-okf/0.5
            type: research-note
            title: Invalid research note
            description: A deliberately invalid conditional-metadata fixture.
            knowledge_role: evidence
            status: stable
            original_record: not-a-boolean
            generated: {by: invalid-actor, at: yesterday}
            generation_run: not-a-uuid
            stale_after: 2000-01-01
            sources:
              - {id: scope, title: Scope, resource: all project queries, source_kind: scope}
              - {id: missing-resource, title: Missing resource, source_kind: internal}
            ---
            # Invalid research note
            See [missing](missing.md).
        """
        rows = [{"path": "research/notes/invalid.md", "title": "Invalid research note", "description": "A deliberately invalid conditional-metadata fixture.", "type": "research-note", "role": "evidence", "status": "stable"}]
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

    def test_fenced_examples_are_not_links_or_footnote_joins(self):
        files = self.valid_minimal_bundle()
        prose = """
            ```markdown
            [missing](missing.md)
            [^missing]
            ```
            Inline code `[also missing](also-missing.md)` and `[^also-missing]` are examples.
        """
        files["AGENTS.md"] = self.concept(
            type_name="agent-instructions",
            title="Agents",
            description="Root agent invariants.",
            role="operational",
            status="stable",
            body=prose,
        )
        files["index.md"] = self.valid_index([
            {"path": "AGENTS.md", "title": "Agents", "description": "Root agent invariants.", "type": "agent-instructions", "role": "operational", "status": "stable"},
        ])
        report = self.run_validator(files)

        self.assertTrue(report["smartdca_profile"]["ok"], report["smartdca_profile"]["findings"])

    def test_inline_code_spans_are_not_links_or_footnote_joins(self):
        files = self.valid_minimal_bundle()
        prose = "Inline code `[missing](missing.md)` and `[^missing]` are examples."
        files["AGENTS.md"] = self.concept(
            type_name="agent-instructions",
            title="Agents",
            description="Root agent invariants.",
            role="operational",
            status="stable",
            body=prose,
        )
        files["index.md"] = self.valid_index([
            {"path": "AGENTS.md", "title": "Agents", "description": "Root agent invariants.", "type": "agent-instructions", "role": "operational", "status": "stable"},
        ])
        report = self.run_validator(files)

        self.assertTrue(report["smartdca_profile"]["ok"], report["smartdca_profile"]["findings"])

    def test_a_longer_fence_is_not_closed_by_a_shorter_marker(self):
        files = self.valid_minimal_bundle()
        fenced = """
            ````markdown
            ```
            - [concept](path.md) stays inside the outer fence
            ```
            ````

            A real [glossary](CONTEXT.md) link follows the block.
        """
        files["AGENTS.md"] = self.concept(
            type_name="agent-instructions",
            title="Agents",
            description="Root agent invariants.",
            role="operational",
            status="stable",
            body=fenced,
        )
        files["CONTEXT.md"] = self.concept(
            type_name="domain-glossary",
            title="Context",
            description="Draft canonical terminology.",
            role="canonical",
            status="draft",
        )
        files["index.md"] = self.valid_index([
            {"path": "CONTEXT.md", "title": "Context", "description": "Draft canonical terminology.", "type": "domain-glossary", "role": "canonical", "status": "draft"},
            {"path": "AGENTS.md", "title": "Agents", "description": "Root agent invariants.", "type": "agent-instructions", "role": "operational", "status": "stable"},
        ])
        report = self.run_validator(files)

        self.assertTrue(report["smartdca_profile"]["ok"], report["smartdca_profile"]["findings"])

    def test_strict_mode_blocks_a_nonconformant_bundle_while_report_mode_does_not(self):
        conformant = self.valid_minimal_bundle()
        status, report = self.run_cli(conformant, "--strict")
        self.assertEqual(status, 0, report)
        self.assertEqual(report["mode"], "strict")

        nonconformant = dict(conformant)
        nonconformant["research/notes/untyped.md"] = "# Untyped new page\n"
        strict_status, strict_report = self.run_cli(nonconformant, "--strict")
        self.assertEqual(strict_status, 1)
        self.assertFalse(strict_report["base_okf"]["ok"])
        self.assertFalse(strict_report["smartdca_profile"]["ok"])

        report_status, report_only = self.run_cli(nonconformant)
        self.assertEqual(report_status, 0)
        self.assertEqual(report_only["mode"], "report")
        self.assertEqual(report_only["smartdca_profile"]["findings"], strict_report["smartdca_profile"]["findings"])

    def test_strict_mode_blocks_a_profile_only_violation(self):
        files = self.valid_minimal_bundle()
        files["AGENTS.md"] = self.concept(
            type_name="agent-instructions",
            title="Agents",
            description="Root agent invariants.",
            role="operational",
            status="stable",
        ).replace("profile: smartdca-okf/0.5", "profile: smartdca-okf/0.9")
        files["index.md"] = self.valid_index([
            {"path": "AGENTS.md", "title": "Agents", "description": "Root agent invariants.", "type": "agent-instructions", "role": "operational", "status": "stable"},
        ])
        status, report = self.run_cli(files, "--strict")

        self.assertEqual(status, 1)
        self.assertTrue(report["base_okf"]["ok"])
        self.assertIn("SDCA003", self.codes(report))

    def test_strict_mode_still_rejects_an_invalid_invocation(self):
        with tempfile.TemporaryDirectory() as directory:
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), str(Path(directory) / "missing"), "--strict"],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(completed.returncode, 2)

    def test_index_requires_complete_coverage_and_stable_canonical_first(self):
        files = self.valid_minimal_bundle()
        context = self.concept(
            type_name="domain-glossary",
            title="Context",
            description="Draft canonical terminology.",
            role="canonical",
            status="draft",
        )
        definition = self.concept(
            type_name="definition",
            title="Stable definition",
            description="A stable canonical definition used for ordering tests.",
            role="canonical",
            status="stable",
            extra="""
                verified:
                  - by: human:reviewer
                    at: 2026-08-15T12:00:00Z
                    review_run: urn:uuid:99999999-9999-4999-8999-999999999999
            """,
        )
        files["CONTEXT.md"] = context
        files["research/definitions/stable.md"] = definition
        rows = [
            {"path": "CONTEXT.md", "title": "Context", "description": "Draft canonical terminology.", "type": "domain-glossary", "role": "canonical", "status": "draft"},
            {"path": "research/definitions/stable.md", "title": "Stable definition", "description": "A stable canonical definition used for ordering tests.", "type": "definition", "role": "canonical", "status": "stable"},
        ]
        files["index.md"] = self.valid_index(rows)
        ordering = self.run_validator(files)
        self.assertIn("SDCA043", self.codes(ordering))

        files["index.md"] = self.valid_index(rows[:1])
        coverage = self.run_validator(files)
        self.assertIn("SDCA044", self.codes(coverage))

        absolute_files = self.valid_minimal_bundle()
        absolute_files["AGENTS.md"] = self.concept(
            type_name="agent-instructions",
            title="Agents",
            description="Root agent invariants.",
            role="operational",
            status="stable",
        )
        absolute_files["index.md"] = self.valid_index([
            {"path": "AGENTS.md", "title": "Agents", "description": "Root agent invariants.", "type": "agent-instructions", "role": "operational", "status": "stable"},
        ]).replace("(AGENTS.md)", "(/AGENTS.md)")
        absolute = self.run_validator(absolute_files)
        self.assertIn("SDCA045", self.codes(absolute))


        empty_marker_files = self.valid_minimal_bundle()
        empty_marker_files["index.md"] = empty_marker_files["index.md"].replace("_None._", "", 1)
        empty_marker = self.run_validator(empty_marker_files)
        self.assertIn("SDCA043", self.codes(empty_marker))
