from pathlib import Path

path = Path("tools/okf/tests/test_validate_cli.py")
text = path.read_text(encoding="utf-8")

marker = "    def test_a_longer_fence_is_not_closed_by_a_shorter_marker(self):\n"
if "def test_inline_code_spans_are_not_links_or_footnote_joins" not in text:
    restored = '''    def test_inline_code_spans_are_not_links_or_footnote_joins(self):
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

'''
    if marker not in text:
        raise SystemExit("longer-fence marker not found")
    text = text.replace(marker, restored + marker, 1)

empty_assertion = '        self.assertIn("SDCA043", self.codes(empty_marker))\n'
if empty_assertion not in text:
    anchor = '        self.assertIn("SDCA045", self.codes(absolute))\n'
    addition = '''

        empty_marker_files = self.valid_minimal_bundle()
        empty_marker_files["index.md"] = empty_marker_files["index.md"].replace("_None._", "", 1)
        empty_marker = self.run_validator(empty_marker_files)
        self.assertIn("SDCA043", self.codes(empty_marker))
'''
    if anchor not in text:
        raise SystemExit("absolute-index assertion not found")
    text = text.replace(anchor, anchor + addition, 1)

path.write_text(text, encoding="utf-8")
