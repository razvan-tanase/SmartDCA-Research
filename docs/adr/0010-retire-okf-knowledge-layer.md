# Retire the OKF knowledge layer

SmartDCA previously treated nearly every Markdown file as a versioned OKF
concept with mandatory metadata, exhaustive path registration, duplicate
index and log records, and a custom validator. The machinery added roughly
3,000 lines of governance code and 2,600 lines of frontmatter, and ordinary
documentation changes could require profile migrations unrelated to the
research.

The repository therefore retires the OKF profile and bundle model without
replacing them with another schema. Markdown files use ordinary
repository-relative paths; `README.md` provides research navigation, and the
project map records tracked work. Scientific claims still require linked
evidence and executable checks. Retained scientific source bytes, accepted
protocols and inputs, and run bundles remain immutable, and substantive
scientific conclusions still receive independent review.

This decision supersedes ADRs 0002 through 0006 and ADR 0009. Those records and
the OKF-only tickets, source ingests, validation tooling, index, and event log
are removed; Git retains their history. ADRs 0001, 0007, and 0008 remain after
their knowledge-profile-specific clauses are removed.
