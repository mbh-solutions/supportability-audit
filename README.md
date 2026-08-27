# Supportability Audit

`supportability-audit` is a vendor-neutral, read-only [Agent Skill](https://agentskills.io/specification) for evidence-backed Supportability Standard audits. It can audit a whole repository, a proposed change or diff, or supplied code without requiring Supportability Gate or any target-repository installation.

The repository root is the installable skill directory. `SKILL.md` defines the natural-language interface; `references/` contains the governing Standard, canonical clause coverage index, and procedural rubric; `assets/findings-report.md` defines the advisory report shape.

The skill never installs dependencies, executes target code, changes audited files, publishes review output, or performs remediation. It reports evidence-supported findings and explicit limits only.

## Standard provenance

- Source repository: [mbh-solutions/supportability-gate](https://github.com/mbh-solutions/supportability-gate)
- Source path: `docs/supportability_standard.md`
- Source commit: `9cd7d4f39cd35a3449b7b685d8798c6127f33387`
- SHA-256: `81653c5057c1555f8b6d41c6e5999d0b54caa178a2ca97a07216147ec16133e2`

`references/supportability-standard.md` is copied byte-for-byte from that source. `.gitattributes` disables text conversion for the copied file so its hash remains stable.

The clause coverage index has separate provenance:

- Source path: `docs/normative_clause_inventory.json`
- Inspected source commit: `7e30ad045efc13187e7a38084296e51ca4f574d5`
- SHA-256: `02f58effce7bb27bf57536585d42b6d0241929ba29377fdbded4d93ecfe3eb9a`
- Bound Standard SHA-256: `81653c5057c1555f8b6d41c6e5999d0b54caa178a2ca97a07216147ec16133e2`
- Canonical clauses: `218`

`references/normative_clause_inventory.json` is copied byte-for-byte and protected from text conversion. It is only a coverage index. The immutable Standard remains the authority for meaning and applicability.

## Usage

Run the skill against a whole repository, proposed change, or supplied code. Full Standard audits create one disposition for every canonical clause using only `PASS`, `FAIL`, `INCOMPLETE`, or `NOT APPLICABLE`; every applicable non-passing clause maps to a plain-language finding. Genuinely tiny changes use the Standard's short-task guidance and return a concise evidence-backed report without a clause ledger or Gate classification. Substantive scope always switches to the Full Standard path.

Full Standard reports lead with the product bottom line, correction order, impact, and observable completion criteria; the 218-row checklist, exact evidence, commands, limits, priorities, origins, and Gate details remain in the technical appendix. Short-task reports state applicability, exact scope, supported issues and evidence, validation evidence, limits, and the same advisory-not-certification boundary.

## Validation

Validation uses the official `skills-ref` reference validator pinned to [`69ef37e9424c0a7ea9dd2293b559e43ec8176379`](https://github.com/agentskills/agentskills/commit/69ef37e9424c0a7ea9dd2293b559e43ec8176379), the standard-library repository validator, bytecode compilation, whitespace checks, and immutable Standard/inventory checks. The repository validator also enforces inventory schema, Standard binding, clause count, unique IDs, and the shipped PM/checklist/mapping instructions. The workflow pins every external action and validator revision to a full commit SHA.

Local validation requires Python 3.12. Install the pinned validator directly from its source repository, run `skills-ref validate` with the absolute repository path, then run the commands documented in `.github/workflows/validate.yml` and verify the final hash against the value above. The repository contract validator is `src/supportability_audit/validate_repository.py`.

The absolute path works around an upstream reference-validator defect in which the otherwise equivalent argument `.` has an empty path name and is rejected. No validator behavior is patched or replaced.

## Protected delivery

Changes to `main` are protected by the repository validation rule and the organization's centrally managed Supportability Gate. The Gate workflow is maintained outside this repository and pinned by the organization ruleset.

<!-- S11 ruleset migration canary: prepared -->
