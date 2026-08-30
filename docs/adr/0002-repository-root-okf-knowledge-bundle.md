---
profile: smartdca-okf/0.5
type: decision-record
title: "Make the repository root an OKF knowledge bundle"
description: "Decision anchoring the SmartDCA bundle namespace at repository root, narrowed in profile 0.5 to a declared bundle view."
knowledge_role: canonical
status: stable
original_record: true
decision_status: accepted
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-30T09:57:10Z
generation_run: urn:uuid:eb95df4b-cddd-4d8f-987c-dca42e3ecc68
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T07:38:00Z
    review_run: urn:uuid:16bd7b25-9e03-4aef-9c9a-5301cb317903
  - by: openai-codex/spec-review-0.1
    at: 2026-08-30T10:09:30Z
    review_run: urn:uuid:0423e158-4c18-4bb7-bfe3-ba3e7b07b882
---
# Make the repository root an OKF knowledge bundle

The original decision made the SmartDCA repository itself the LLM-Wiki and described its root as a conformant Open Knowledge Format v0.2 Knowledge Bundle, rather than containing a separate bundle subtree. It deliberately made every non-reserved Markdown file—including research tickets and agent workflows—a typed concept so the complete project would be navigable as knowledge; a SmartDCA profile and validation would keep canonical research, supporting evidence, and operational records distinct.

Profile 0.5 narrows this decision through [ADR 0009](0009-exclude-agents-tooling-from-knowledge-bundle.md): the repository root now anchors a declared SmartDCA bundle view, while root `.git/` and `.agents/` are non-bundle infrastructure. The raw repository root is no longer claimed as an unqualified conformant OKF bundle; role separation and inclusion of authoritative workflows under `docs/agents/` remain unchanged.
