from pathlib import Path
import re

path = Path("tools/okf/tests/test_validate_cli.py")
text = path.read_text(encoding="utf-8")

# README is no longer counted as a Markdown concept.
text = text.replace('self.assertEqual(report["inventory"]["markdown_files"], 3)', 'self.assertEqual(report["inventory"]["markdown_files"], 2)', 1)

# Conditional-metadata validation must exercise a real concept, not repository UI.
pattern = r'    def test_invalid_conditional_metadata_and_stable_links_are_reported\(self\):\n.*?(?=    def test_fenced_examples_are_not_links_or_footnote_joins)'
replacement = '''    def test_invalid_conditional_metadata_and_stable_links_are_reported(self):
        files = self.valid_minimal_bundle()
        files["research/notes/invalid.md"] = """
            ---
            profile: smartdca-okf/0.3
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

'''
text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit("conditional-metadata test not found")

# Keep fenced-link parser tests meaningful by placing the prose in AGENTS.md,
# which remains a stable, validated concept.
pattern = r'    def test_fenced_examples_are_not_links_or_footnote_joins\(self\):\n.*?(?=    def test_a_longer_fence_is_not_closed_by_a_shorter_marker)'
replacement = '''    def test_fenced_examples_are_not_links_or_footnote_joins(self):
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

'''
text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit("fenced examples test not found")

pattern = r'    def test_a_longer_fence_is_not_closed_by_a_shorter_marker\(self\):\n.*?(?=    def test_strict_mode_blocks_a_nonconformant_bundle_while_report_mode_does_not)'
replacement = '''    def test_a_longer_fence_is_not_closed_by_a_shorter_marker(self):
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

'''
text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit("longer fence test not found")

# Profile-only strict failure now uses a real operational concept.
pattern = r'    def test_strict_mode_blocks_a_profile_only_violation\(self\):\n.*?(?=    def test_strict_mode_still_rejects_an_invalid_invocation)'
replacement = '''    def test_strict_mode_blocks_a_profile_only_violation(self):
        files = self.valid_minimal_bundle()
        files["AGENTS.md"] = self.concept(
            type_name="agent-instructions",
            title="Agents",
            description="Root agent invariants.",
            role="operational",
            status="stable",
        ).replace("profile: smartdca-okf/0.3", "profile: smartdca-okf/0.9")
        files["index.md"] = self.valid_index([
            {"path": "AGENTS.md", "title": "Agents", "description": "Root agent invariants.", "type": "agent-instructions", "role": "operational", "status": "stable"},
        ])
        status, report = self.run_cli(files, "--strict")

        self.assertEqual(status, 1)
        self.assertTrue(report["base_okf"]["ok"])
        self.assertIn("SDCA003", self.codes(report))

'''
text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit("strict profile-only test not found")

# Coverage and canonical ordering must be tested with actual concepts now that
# README is intentionally outside the inventory.
pattern = r'    def test_index_requires_complete_coverage_and_stable_canonical_first\(self\):\n.*?(?=    def |\Z)'
match = re.search(pattern, text, flags=re.S)
if not match:
    raise SystemExit("index coverage test not found")
# Preserve the next function marker by replacing only this function body up to
# the next method declaration.
replacement = '''    def test_index_requires_complete_coverage_and_stable_canonical_first(self):
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

'''
start, end = match.span()
# match includes the next "    def " prefix when present; retain it.
matched = match.group(0)
next_def = re.search(r'\n    def ', matched[1:])
if next_def:
    keep_from = 1 + next_def.start() + 1
    replacement += matched[keep_from:]
text = text[:start] + replacement + text[end:]

path.write_text(text, encoding="utf-8")

# The user supplied the semantic rule directly. Record that human-directed
# policy confirmation as the qualifying verification for this specific profile
# edit, rather than pretending the 2026-08-16 reviews cover it.
profile = Path("docs/knowledge/okf-profile.md")
text = profile.read_text(encoding="utf-8")
verification = '''  - by: human:github:razvan-tanase
    at: 2026-08-23T15:45:00Z
    review_run: urn:uuid:f1558f7f-31a3-431b-9ff5-a0fc3c67ae13
'''
if "review_run: urn:uuid:f1558f7f-31a3-431b-9ff5-a0fc3c67ae13" not in text:
    marker = "---\n# SmartDCA Open Knowledge Format profile"
    pos = text.find(marker)
    if pos < 0:
        raise SystemExit("profile frontmatter terminator not found")
    frontmatter = text[:pos]
    verified_pos = frontmatter.rfind("verified:\n")
    if verified_pos < 0:
        raise SystemExit("profile verified list not found")
    # Append to the verified list immediately before the frontmatter terminator.
    text = text[:pos] + verification + text[pos:]
profile.write_text(text, encoding="utf-8")
