---
profile: smartdca-okf/0.5
type: decision-record
title: "Make the repository root an OKF knowledge bundle"
description: "Decision making the repository root itself the conformant OKF v0.2 knowledge bundle."
knowledge_role: canonical
status: stable
original_record: true
decision_status: accepted
verified:
  - by: claude-code/smartdca-wiki-0.1
    at: 2026-08-16T07:38:00Z
    review_run: urn:uuid:16bd7b25-9e03-4aef-9c9a-5301cb317903
---
# Make the repository root an OKF knowledge bundle

The SmartDCA repository itself is the LLM-Wiki and its root is a conformant Open Knowledge Format v0.2 Knowledge Bundle, rather than containing a separate bundle subtree. This deliberately makes every non-reserved Markdown file—including research tickets and agent workflows—a typed concept so the complete project is navigable as knowledge; a SmartDCA profile and validation must keep canonical research, supporting evidence, and operational records distinct.
