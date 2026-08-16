# Supportability Audit

`supportability-audit` is a vendor-neutral, read-only [Agent Skill](https://agentskills.io/specification) for evidence-backed Supportability Standard audits. It can audit a whole repository, a proposed change or diff, or supplied code without requiring Supportability Gate or any target-repository installation.

The repository root is the installable skill directory. `SKILL.md` defines the natural-language interface; `references/` contains the governing Standard and procedural rubric; `assets/findings-report.md` defines the advisory report shape.

The skill never installs dependencies, executes target code, changes audited files, publishes review output, or performs remediation. It reports evidence-supported findings and explicit limits only.

## Standard provenance

- Source repository: [mbh-solutions/supportability-gate](https://github.com/mbh-solutions/supportability-gate)
- Source path: `docs/supportability_standard.md`
- Source commit: `9cd7d4f39cd35a3449b7b685d8798c6127f33387`
- SHA-256: `81653c5057c1555f8b6d41c6e5999d0b54caa178a2ca97a07216147ec16133e2`

`references/supportability-standard.md` is copied byte-for-byte from that source. `.gitattributes` disables text conversion for the copied file so its hash remains stable.

## Validation

Validation uses the official `skills-ref` reference validator pinned to [`69ef37e9424c0a7ea9dd2293b559e43ec8176379`](https://github.com/agentskills/agentskills/commit/69ef37e9424c0a7ea9dd2293b559e43ec8176379), the standard-library repository validator, bytecode compilation, whitespace checks, and a final Standard hash check. The workflow pins every external action and validator revision to a full commit SHA.

Local validation requires Python 3.12. Install the pinned validator directly from its source repository, run `skills-ref validate` with the absolute repository path, then run the commands documented in `.github/workflows/validate.yml` and verify the final hash against the value above.

The absolute path works around an upstream reference-validator defect in which the otherwise equivalent argument `.` has an empty path name and is rejected. No validator behavior is patched or replaced.
