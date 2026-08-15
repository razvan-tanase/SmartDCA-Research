# Implement the SmartDCA OKF profile and report-only validator

Type: task
Status: open
Blocked by: 12
Parent: [Find the rigorous out quasi-Gini route to a complete SmartDCA paper](../map.md)

## Question

Write the normative `docs/knowledge/okf-profile.md` for `smartdca-okf/0.1`, the detailed `docs/agents/llm-wiki-workflow.md`, and the concise root `AGENTS.md` contract. Implement `tools/okf/validate.py` with a pinned YAML dependency and automated fixtures covering the registered types, role/status/trust rules, reserved files, stable links, source IDs, actor namespace, ticket and ADR extension fields, and dependency freshness. Run it in report-only mode against the current repository and record the complete migration inventory. Do not add OKF metadata to the corpus or enable blocking CI in this ticket.

## Comments

- Created from the accepted ticket-12 architecture.
- The validator must distinguish base OKF v0.2 conformance from the stricter SmartDCA profile.
- Existing scientific checks under `reproducibility/checks/` remain separate.

## Answer

Pending.
