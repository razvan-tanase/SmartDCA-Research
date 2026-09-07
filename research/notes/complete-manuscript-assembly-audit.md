# Complete manuscript assembly audit

State: **integrated-draft; ticket 14 remains open**.

The [ticket](../../.scratch/smartdca/efforts/thesis-manuscript-assembly/issues/14-assemble-complete-manuscript-release.md)
asks for a complete release candidate with no unresolved institutional input.
The scientific manuscript is complete, but that acceptance condition is not
met. The frozen [institutional contract](../../manuscript/contract/institutional-contract.md)
still requires actual personal, supervisor, session, branding, declaration,
formatting, submission, similarity, and archival evidence. No requirement has
been waived, and no approval or signature has been inferred. Ticket 15 remains
blocked by ticket 14.

## Implemented assembly seam

The canonical build now includes the
[assembly audit](../../manuscript/assembly_controls.py), in addition to its
existing chapter-level scientific and citation controls. The public
[package command](../../manuscript/assemble.py) creates a complete public
source snapshot, PDF, claim-to-evidence CSV, rendered-location inventory,
institutional blocker list, submission-check verdict, supervisor brief, and
content-binding manifest. The ZIP identity hashes its binding object; every
payload member other than the manifest is covered. Source hashes bind actual
working bytes and executable permissions, and explicitly record the Git base
and modified state. Exported source verifies its own inventory and rebuilds
without Git history.

The [clean container route](../../manuscript/assemble-clean.sh) uses the
declared Debian/TeX/Poppler environment. The manifest records actual tool
versions. Distribution package versions are not permanently locked, so a
different toolchain can yield another valid integrated-draft identity. PDF
trailer metadata that depended on the build path is suppressed; the manifest
supplies the exact PDF hash. Assembly does not grant a release-state transition
or stand in for the complete scientific suite, ticket 15's domain audit,
supervisor feedback, similarity review, or submission approval.

## Traceability and reconciliation

The register contains 96 stable entries. The assembly seam validates every
primary and restatement location and uniquely assigns all 155 labeled
scientific displays. Supporting equations retain the corresponding existing
claim ID through `display_labels`; 15 previously unlabeled numbered equations
now have stable labels. Two previously unindexed tables receive dedicated IDs:

- `claim-table-terminal-inventory`: the seven sign cases of the existing
  arbitrary-horizon affine classification, with the strict positive evaluation
  price and fixed causal-ledger assumptions retained.
- `claim-table-three-purchase-witness`: the existing exact beta witness, with
  gaps -1/36 and 1/144, unchanged ledger values, and no monotone-beta claim.

Their authorities remain the
[terminal-inventory theorem](../theorems/arbitrary-horizon-performance-boundary.md)
and [three-purchase theorem](../theorems/three-purchase-corrected-mean-effect.md),
with their existing exact checks. New prose references connect every table and
figure to its body or appendix discussion. Retired optional Chapter 9 display
plans remain explicitly retired supplementary projections, not missing assets.

Both empirical asset generators regenerate all eight fragments from accepted
fingerprinted run bundles, and assembly requires byte agreement. The rendering
layer now uses fixed 9-point table text, wrapped text columns and headers, and
no table scaling. Five source-authored tables also use the template's 9-point
text. Scientific values, protocols, inputs, run bytes, hypotheses, inference,
and result interpretation are unchanged. Figures retain their original
generation and comparison-specific captions.

Structural ownership is not proof that every sentence is scientifically true
or that every nearby citation supports it. The existing reviewed chapter notes
remain the semantic authorities; the complete independent domain audit belongs
to ticket 15. The [supervisor brief](../../manuscript/release/supervisor-review.md)
states the narrative, contribution boundaries, evidence controls, and exact
human decisions still needed.

## Verification record

- The public package test rebuilt a relocated source export and reproduced
  identical PDF, manifest identity, and ZIP bytes under the same local tools.
- Mutation checks reject an unmapped display, duplicate evidence ownership,
  missing restatement, stale generated asset, uncited bibliography entry, and
  a body-content placeholder.
- The rendered audit checks A4 geometry, visible page content, text within page
  bounds, LaTeX warnings, citation/reference resolution, and compiled locations.
  Legacy TeX math control characters are removed only from Poppler's XML text
  for bounding-box parsing; visual review checks their rendered glyphs.
- The final 125-page PDF was visually inspected throughout. Wrapped 9-point
  tables, equations, figures, appendices, and bibliography have no observed
  clipping, overlap, or missing glyphs. The Appendix E heading now stays with
  its following table. All 96 claim locations and 155 scientific displays
  resolve in the compiled document; the rendered audit passes.
- Completed README checks include all 11 standalone scientific programs,
  the canonical and deterministic suites, the historical and synthesis suites,
  chapter and literature checks, and manuscript control, release, build, and
  assembly tests. The final release/build rerun passed 17 tests; assembly
  passed both tests, including rejection of changed exported permissions.
- The Implement skill's independent Standards and Spec reviews are complete.
  Standards identified container ownership, unbound executable permissions,
  and the omitted assembly test in the macOS helper. All three were fixed and
  rechecked, leaving no findings. Spec found no scientific drift or actionable
  defect within the achievable scope, independently regenerated all eight
  empirical fragments, and confirmed unchanged numerical tokens.
- [Clean-container verification](https://github.com/razvan-tanase/SmartDCA-Research/actions/runs/34087486136)
  passed on the published implementation commit `301548e593be82100c91a90595749c7b602641b3`,
  including the exported-source reproduction test and retained review package.
  The submission checker correctly exits 1 with the institutional blockers.
- The [full scientific replay](https://github.com/razvan-tanase/SmartDCA-Research/actions/runs/34087486111)
  records the complete scientific route for that same implementation. Its
  recorded conclusion, together with the manuscript job, is authoritative for
  that commit. Subsequent documentation-only tracking changes and their current
  check results are visible on [PR 28](https://github.com/razvan-tanase/SmartDCA-Research/pull/28).

The earlier verification attempt was interrupted by a runtime-level
`fatal library error, lookup self` during the stochastic suite. Completed
earlier checks were retained; the stochastic suite and remaining README route
were restarted explicitly. The second stochastic attempt did not complete
before the workspace process ended. Neither interrupted attempt is recorded
as a passing full-suite run; use the linked workflow for a durable result.
