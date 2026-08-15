---
status: accepted
---

# Preserve path-based concept identity through supersession

Repository-relative paths without `.md` are durable Concept IDs once the SmartDCA OKF migration establishes them. Later restructuring creates new concepts instead of silently moving stable ones; a replaced concept remains at its original path with deprecated status, a reason, and a `superseded_by` link so citations and provenance survive cleanup.
