# Supportability Audit Findings

## Audit boundary

- Audited target: `<repository, revision, files, patch, or supplied code>`
- Mode: `<Whole repository | Proposed change | Supplied code>`
- Scope: `<included paths and restrictions>`
- Excluded scope: `<excluded paths or None>`
- Comparison baseline: `<exact revision or None established>`
- Standard applicability: `<Full Standard | Short-task guidance>` — `<reason>`

## Gate integration

- Status: `<Detected | Not detected | Not established>`
- Evidence: `<direct artifact paths, keys, workflow locations, or scope limit>`

## Evidence

- Inspected: `<tracked files, configurations, revisions, diff, tests, and other evidence>`
- Limits: `<unavailable, unreadable, restricted, generated, vendored, or unverified areas>`

### Read-only audit commands actually run

| Exact command | Purpose | Observed result |
|---|---|---|
| `<command or None>` | `<purpose>` | `<result>` |

### Existing target-validation evidence inspected

| Gate name | Command or check identity | Configured scope | Evidence source and revision | Result | Established coverage |
|---|---|---|---|---|---|
| `<gate or None established>` | `<command or check>` | `<exact paths and exclusions>` | `<artifact and revision>` | `<Passed | Failed | Not run | Not established>` | `<files and risks covered>` |

## Standard coverage

| Standard section | Evidence assessed | Finding or item-level evidence state | Limits |
|---|---|---|---|
| Cyclomatic / McCabe Complexity Control | `<evidence>` | `<finding ID or Established | Failed | Incomplete | Not established | Not applicable>` | `<limits>` |
| Separation of Concerns / Single Responsibility Principle | `<evidence>` | `<finding ID or evidence state>` | `<limits>` |
| Layered Architecture / Clean Dependency Direction / Acyclic Imports | `<evidence>` | `<finding ID or evidence state>` | `<limits>` |
| Domain-Driven Modularization / High Cohesion / Low Coupling | `<evidence>` | `<finding ID or evidence state>` | `<limits>` |
| Characterization / Golden-Master Tests | `<evidence>` | `<finding ID or evidence state>` | `<limits>` |
| Incremental Strangler-Style Refactoring | `<evidence>` | `<finding ID or evidence state>` | `<limits>` |
| Quality Gates | `<evidence>` | `<finding ID or evidence state>` | `<limits>` |
| Review Handoff / ADR-Style Reporting | `<evidence>` | `<finding ID or evidence state>` | `<limits>` |

## Gate coverage evidence

### Changed files

| File | Gate name | Configured scope | Result | Established coverage | Exclusion or gap |
|---|---|---|---|---|---|
| `<file or None>` | `<gate>` | `<exact paths and exclusions>` | `<Passed | Failed | Not run | Not established>` | `<direct evidence>` | `<gap>` |

### Highest-risk production files

| File | Risk basis | Gate name and configured scope | Result | Established coverage | Exclusion or gap |
|---|---|---|---|---|---|
| `<file or None established>` | `<reason>` | `<gate and exact paths>` | `<Passed | Failed | Not run | Not established>` | `<direct evidence>` | `<gap>` |

- Excluded production files: `<files or None established>`
- Threshold changes: `<changes or None established>`
- Gate-scope changes: `<changes or None established>`
- Files moved or renamed outside checked scopes: `<files or None established>`

## Findings

### F-001 — `<concise root cause>`

- Priority: `<P1 | P2 | P3>`
- Origin: `<Introduced | Pre-existing | Undetermined>`
- Standard section: `<section number and title>`
- Evidence: `<exact file:line, symbol, configuration key, revision, or supplied-code location>`
- Supportability impact: `<why safe change, testing, reasoning, or review is harder>`
- Smallest reasonable correction: `<bounded corrective direction>`
- Confidence: `<High | Medium | Low>`
- Remaining uncertainty: `<what evidence is still missing>`

Repeat the finding block only for distinct, supported root causes. Order findings by supportability impact.

When no supported finding exists, replace all finding blocks with exactly:

> No supported findings in the audited scope.

Follow that sentence with scope limits or unverified areas.

## Unknowns

- `<evidence or conclusion that could not be established>`
