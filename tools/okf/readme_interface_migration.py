from pathlib import Path
import re


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise SystemExit(f"expected text not found: {label}")


# README: strip the concept frontmatter and preserve the human-facing body.
readme = Path("README.md")
text = readme.read_text(encoding="utf-8")
if text.startswith("---\n"):
    closing = text.find("\n---\n", 4)
    if closing < 0:
        raise SystemExit("README frontmatter has no closing delimiter")
    text = text[closing + 5:].lstrip("\n")
readme.write_text(text, encoding="utf-8")

# Validator: the root README is repository-interface documentation, not a concept.
validator = Path("tools/okf/validate.py")
text = validator.read_text(encoding="utf-8")
text = replace_once(
    text,
    'RESERVED_NAMES = {"index.md", "log.md"}\n',
    'RESERVED_NAMES = {"index.md", "log.md"}\nNON_CONCEPT_MARKDOWN = {"README.md"}\n',
    "validator non-concept constant",
)
text = text.replace('    "README.md": ("project-overview", "canonical", "stable"),\n', '', 1)
old = 'def markdown_files(root: Path) -> list[Path]:\n    return sorted(path for path in root.rglob("*.md") if path.is_file() and ".git" not in path.relative_to(root).parts)\n'
new = '''def markdown_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.md")
        if path.is_file()
        and ".git" not in path.relative_to(root).parts
        and path.relative_to(root).as_posix() not in NON_CONCEPT_MARKDOWN
    )
'''
text = replace_once(text, old, new, "validator markdown_files")
validator.write_text(text, encoding="utf-8")

# Index: README remains linked as the human introduction, but is not inventoried as a concept.
index = Path("index.md")
text = index.read_text(encoding="utf-8")
text, count = re.subn(
    r'\n### project-overview\n\n- \[SmartDCA Research\]\(README\.md\).*?\n(?=\n### )',
    '\n',
    text,
    count=1,
    flags=re.S,
)
if count == 0 and "### project-overview" in text:
    raise SystemExit("could not remove README project-overview index row")
index.write_text(text, encoding="utf-8")

# Normative profile: make the repository-interface exception explicit.
profile = Path("docs/knowledge/okf-profile.md")
text = profile.read_text(encoding="utf-8")
text = re.sub(
    r'generated:\n  by: [^\n]+\n  at: [^\n]+\ngeneration_run: urn:uuid:[^\n]+',
    'generated:\n  by: openai-codex/smartdca-wiki-0.1\n  at: 2026-08-23T15:45:00Z\ngeneration_run: urn:uuid:72e21539-2841-4d26-a739-501293fbb7b1',
    text,
    count=1,
)
text = replace_once(
    text,
    'The repository root is the bundle root, by the decision in [Make the repository root an OKF knowledge bundle](../adr/0002-repository-root-okf-knowledge-bundle.md)[^adr-0002]. Every UTF-8 file whose final suffix is `.md` is either a concept or a reserved file, including Markdown below hidden directories. `index.md` and `log.md` are reserved at every depth; all other Markdown files are concepts.',
    'The repository root is the bundle root, by the decision in [Make the repository root an OKF knowledge bundle](../adr/0002-repository-root-okf-knowledge-bundle.md)[^adr-0002]. The root `README.md` is repository-interface documentation for humans and GitHub and is deliberately outside the OKF concept corpus; it MUST NOT carry concept frontmatter. Every other UTF-8 file whose final suffix is `.md` is either a concept or a reserved file, including Markdown below hidden directories. `index.md` and `log.md` are reserved at every depth; all remaining Markdown files are concepts.',
    "profile bundle identity",
)
text = replace_once(
    text,
    'The base layer implements OKF v0.2 conformance without importing stricter SmartDCA rules. It requires parseable top-of-file YAML frontmatter and a non-empty `type` for every non-reserved Markdown file, plus the reserved-file structures defined by OKF.',
    'The base layer implements OKF v0.2 conformance without importing stricter SmartDCA rules. It requires parseable top-of-file YAML frontmatter and a non-empty `type` for every Markdown concept file, plus the reserved-file structures defined by OKF. The root `README.md` is not passed to base concept validation.',
    "profile base conformance",
)
text = replace_once(
    text,
    'These assignments are exhaustive and complete for profile 0.3: every registered type has a destination. A non-reserved Markdown path not matched here fails the profile even if all of its metadata is otherwise valid.',
    'These assignments are exhaustive for active concept paths in profile 0.3. The registered `project-overview` type currently has no active concept instance because the root `README.md` is repository-interface documentation rather than knowledge corpus content. A non-reserved Markdown concept path not matched here fails the profile even if all of its metadata is otherwise valid.',
    "profile path mapping introduction",
)
text = replace_once(
    text,
    '| `README.md` | `project-overview` | canonical | Stable original record after migration review. |',
    '| `README.md` | repository interface | not a concept | No YAML concept frontmatter; human/GitHub landing page only. |',
    "profile README path row",
)
text = replace_once(
    text,
    'The validator scans the complete repository tree except `.git`, validates every final-suffix `.md` file, and intentionally does not treat `.md.raw` artifacts as concepts.',
    'The validator scans the complete repository tree except `.git`, validates every final-suffix `.md` file except the root repository-interface `README.md`, and intentionally does not treat `.md.raw` artifacts as concepts.',
    "profile validator contract",
)
profile.write_text(text, encoding="utf-8")

# Validator fixtures: a valid minimal bundle now has a plain README outside the concept inventory.
tests = Path("tools/okf/tests/test_validate_cli.py")
text = tests.read_text(encoding="utf-8")
text, count = re.subn(
    r'    def project_overview\(self\):\n.*?(?=    def concept\()',
    '    def project_overview(self):\n        return "# Project overview"\n\n',
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit("project_overview fixture not found")
text, count = re.subn(
    r'    def valid_minimal_bundle\(self\):\n.*?(?=    def test_report_mode_)',
    '    def valid_minimal_bundle(self):\n        return {\n            "README.md": self.project_overview(),\n            "index.md": self.valid_index([]),\n            "log.md": self.valid_log(),\n        }\n\n',
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit("valid_minimal_bundle fixture not found")
block = re.search(
    r'(    def test_path_mapping_and_universal_fields_are_enforced\(self\):\n.*?)(?=    def test_complete_path_mapping_accepts_each_assigned_path)',
    text,
    re.S,
)
if not block:
    raise SystemExit("path mapping test not found")
replacement = block.group(1).replace('files["README.md"]', 'files["AGENTS.md"]', 1)
text = text[:block.start(1)] + replacement + text[block.end(1):]
text = re.sub(
    r'^\s*\("README\.md", "project-overview".*\n',
    '',
    text,
    count=1,
    flags=re.M,
)
marker = '    def test_complete_minimal_smartdca_bundle_passes(self):\n'
if 'def test_plain_root_readme_is_not_a_concept' not in text:
    new_test = '''    def test_plain_root_readme_is_not_a_concept(self):
        files = self.valid_minimal_bundle()
        report = self.run_validator(files)

        self.assertTrue(report["base_okf"]["ok"], report["base_okf"]["findings"])
        self.assertTrue(report["smartdca_profile"]["ok"], report["smartdca_profile"]["findings"])
        self.assertNotIn("OKF001", self.codes(report, "base_okf"))

'''
    text = text.replace(marker, new_test + marker, 1)
tests.write_text(text, encoding="utf-8")

# Record the policy correction in the immutable bundle log.
log = Path("log.md")
text = log.read_text(encoding="utf-8")
event = '- 2026-08-23T15:45:00Z | Update | Treat README as repository interface outside the OKF concept corpus | [README](README.md), [profile](docs/knowledge/okf-profile.md)\n'
if event not in text:
    heading = '# SmartDCA knowledge log\n'
    if heading not in text:
        raise SystemExit("log heading not found")
    text = text.replace(heading, heading + '\n## 2026-08-23\n' + event, 1)
log.write_text(text, encoding="utf-8")
