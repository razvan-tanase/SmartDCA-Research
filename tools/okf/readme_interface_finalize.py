from pathlib import Path

# The semantic policy comes directly from the user's instruction, so preserve the
# profile's prior machine-generation provenance. The new human verification event
# records this policy correction separately.
profile = Path("docs/knowledge/okf-profile.md")
text = profile.read_text(encoding="utf-8")
new_generated = '''generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-23T15:45:00Z
generation_run: urn:uuid:72e21539-2841-4d26-a739-501293fbb7b1
'''
old_generated = '''generated:
  by: claude-code/smartdca-wiki-0.1
  at: 2026-08-16T10:24:00Z
generation_run: urn:uuid:51b6a4df-c98b-4784-83e4-3b068e4014ab
'''
if new_generated in text:
    text = text.replace(new_generated, old_generated, 1)
elif old_generated not in text:
    raise SystemExit("profile generation provenance block not found")
profile.write_text(text, encoding="utf-8")

# Keep the descriptive preamble outside date groups. The initial migration inserts
# the new event directly after the H1; move it after the preamble and before the
# previous newest group.
log = Path("log.md")
text = log.read_text(encoding="utf-8")
event = '- 2026-08-23T15:45:00Z | Update | Treat README as repository interface outside the OKF concept corpus | [README](README.md), [profile](docs/knowledge/okf-profile.md)'
block = f"## 2026-08-23\n{event}\n"
text = text.replace(block, "", 1)
marker = "## 2026-08-16"
if marker not in text:
    raise SystemExit("existing newest log group not found")
text = text.replace(marker, f"## 2026-08-23\n\n{event}\n\n{marker}", 1)
log.write_text(text, encoding="utf-8")
