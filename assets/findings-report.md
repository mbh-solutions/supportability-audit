# Product-manager summary

Use this template only for the Full Standard path. For short-task guidance, use the concise output defined in the audit rubric and do not create a 218-row appendix.

- Bottom line: `<Corrections required | No supported non-passing items found in audited scope>`
- Highest-priority correction: `<plain-language correction or None>`
- Audit scope: `<target, mode, included scope, and exclusions>`
- Important limits: `<plain-language limits or None>`
- Assurance: `This audit is advisory and is not Supportability Gate certification.`

| Status | Count |
|---|---:|
| `PASS` | `<count>` |
| `FAIL` | `<count>` |
| `INCOMPLETE` | `<count>` |
| `NOT APPLICABLE` | `<count>` |
| **Total** | **218** |

Use bottom line `Corrections required` whenever any applicable clause is `FAIL` or `INCOMPLETE`. Otherwise use `No supported non-passing items found in audited scope`.

## Required corrections

### Fix first (`P1`)

- `<finding ID and one-line correction, or None>`

### Fix next (`P2`)

- `<finding ID and one-line correction, or None>`

### Required local correction (`P3`)

- `<finding ID and one-line correction, or None>`

## Findings

### F-001 — `<plain-language title>`

- What is wrong: `<plain-language problem>`
- Why it matters to the product: `<product impact>`
- Required correction: `<one recommended direction>`
- Done when: `<observable acceptance condition>`
- Affected Standard item count: `<count>`

Repeat only for distinct root causes. Keep IDs stable and order findings by impact.

Only when applicable target/change clauses contain zero `FAIL` and zero `INCOMPLETE`, replace finding blocks with exactly:

> No supported findings in the audited scope.

Follow that sentence with scope limits or unverified areas.

## Technical appendix

### Audit boundary

- Audited target: `<repository, revision, files, patch, or supplied code>`
- Mode: `<Whole repository | Proposed change | Supplied code>`
- Scope: `<included paths and restrictions>`
- Excluded scope: `<excluded paths or None>`
- Comparison baseline: `<exact revision or None established>`
- Standard applicability: `<Full Standard | Short-task guidance>` — `<reason>`

### Gate integration

- Status: `<Detected | Not detected | Not established>`
- Evidence: `<direct artifact paths, keys, workflow locations, or scope limit>`

### Evidence and limits

- Inspected: `<tracked files, configurations, revisions, diff, tests, and other evidence>`
- Limits: `<unavailable, unreadable, restricted, generated, vendored, ambiguous, or unverified areas>`
- Clause treatment: `<finding IDs for every limit affecting an applicable clause, or None>`

#### Read-only audit commands actually run

| Exact command | Purpose | Observed result |
|---|---|---|
| `<command or None>` | `<purpose>` | `<result>` |

#### Existing target-validation evidence inspected

| Gate name | Command or check identity | Configured scope | Evidence source and revision | Result | Established coverage |
|---|---|---|---|---|---|
| `<gate or None established>` | `<command or check>` | `<exact paths and exclusions>` | `<artifact and revision>` | `<Passed | Failed | Not run | Not established>` | `<files and risks covered>` |

### Full clause-level checklist

- Checklist rows: `218`
- Status reconciliation: `<PASS + FAIL + INCOMPLETE + NOT APPLICABLE = 218>`
- Mapping reconciliation: `<every FAIL/INCOMPLETE maps to a finding; every finding maps to clauses>`

Group all 218 rows by the corresponding Standard section. Every inventory clause ID appears exactly once.

| Standard section | Clause ID | Standard line | Requirement | Applicability reason | Evidence | Status | Finding IDs |
|---|---|---:|---|---|---|---|---|
| `<section>` | `<SS-0000>` | `<line>` | `<canonical requirement>` | `<why applicable or specific reason not applicable>` | `<exact evidence or missing proof>` | `<PASS | FAIL | INCOMPLETE | NOT APPLICABLE>` | `<F-000 or —>` |

### Gate coverage evidence

#### Changed files

| File | Gate name | Configured scope | Result | Established coverage | Exclusion or gap |
|---|---|---|---|---|---|
| `<file or None>` | `<gate>` | `<exact paths and exclusions>` | `<Passed | Failed | Not run | Not established>` | `<direct evidence>` | `<gap>` |

#### Highest-risk production files

| File | Risk basis | Gate name and configured scope | Result | Established coverage | Exclusion or gap |
|---|---|---|---|---|---|
| `<file or None established>` | `<reason>` | `<gate and exact paths>` | `<Passed | Failed | Not run | Not established>` | `<direct evidence>` | `<gap>` |

- Excluded production files: `<files or None established>`
- Threshold changes: `<changes or None established>`
- Gate-scope changes: `<changes or None established>`
- Files moved or renamed outside checked scopes: `<files or None established>`

### Technical finding details

#### F-001 — `<root cause>`

- Priority: `<P1 | P2 | P3>`
- Origin: `<Introduced | Pre-existing | Undetermined>`
- Clause IDs: `<one or more SS-0000 IDs>`
- Standard section: `<section number and title>`
- Evidence: `<exact file:line, symbol, configuration key, revision, command result, or supplied-code location>`
- Supportability impact: `<why safe change, testing, reasoning, or review is harder>`
- Required correction: `<smallest reasonable direction>`
- Done when: `<observable acceptance condition>`
- Confidence: `<High | Medium | Low>`
- Remaining uncertainty: `<missing evidence or None>`

### Limits and remaining uncertainty

- `<limit or uncertainty; if it affects an applicable clause, include its INCOMPLETE clause and finding IDs>`
