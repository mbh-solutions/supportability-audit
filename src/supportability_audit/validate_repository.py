from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
STANDARD = ROOT / "references" / "supportability-standard.md"
INVENTORY = ROOT / "references" / "normative_clause_inventory.json"
EXPECTED_STANDARD_SHA256 = "81653c5057c1555f8b6d41c6e5999d0b54caa178a2ca97a07216147ec16133e2"
EXPECTED_INVENTORY_SHA256 = "02f58effce7bb27bf57536585d42b6d0241929ba29377fdbded4d93ecfe3eb9a"
EXPECTED_INVENTORY_CLAUSES = 218
EXPECTED_DESCRIPTION = (
    "Perform a read-only, evidence-backed Supportability Standard audit of an entire "
    "repository, a proposed change or diff, or supplied code, whether or not "
    "Supportability Gate is installed. Use for supportability, maintainability, "
    "complexity, responsibility-boundary, architecture, characterization, quality-gate "
    "coverage, or review-evidence audits. Produce advisory findings only and never "
    "modify the audited target."
)
REQUIRED_FILES = {
    ".gitattributes",
    ".github/workflows/validate.yml",
    ".supportability-characterization.json",
    ".supportability-review.toml",
    ".supportability.toml",
    "README.md",
    "SKILL.md",
    "assets/findings-report.md",
    "pyproject.toml",
    "references/audit-rubric.md",
    "references/normative_clause_inventory.json",
    "references/supportability-standard.md",
    "src/supportability_audit/__init__.py",
    "src/supportability_audit/validate_repository.py",
    "tests/characterization/exhaustive-pm-audit-contract-v3.characterization.py",
    "tests/characterization/exhaustive-pm-audit-contract-v3.golden.json",
    "tests/test_validate_repository.py",
}
RUNTIME_FILES = {
    "SKILL.md",
    "assets/findings-report.md",
    "references/audit-rubric.md",
    "references/normative_clause_inventory.json",
    "references/supportability-standard.md",
}
EXPECTED_ATTRIBUTES = (
    "references/supportability-standard.md -text -whitespace\n"
    "references/normative_clause_inventory.json -text -whitespace\n"
)
INVENTORY_FIELDS = ("schema_version", "standard_sha256", "clauses")
CLAUSE_FIELDS = (
    "clause_id",
    "source_line",
    "statement",
    "applicability",
    "enforcement_owner",
    "evidence_requirement",
    "blocking_test",
)
APPLICABILITY_FIELDS = ("profiles", "condition")
RUNTIME_CONTRACT_SHA256 = {
    "SKILL.md": "90c03046c6ed590e6421e5991e45cf4a6d972f83cebc308b7f6486d13aab422a",
    "references/audit-rubric.md": (
        "52398b2ece8bf81e2c95629b5709fd5dc6f842d751fb823b12acab4aaa53a07b"
    ),
    "assets/findings-report.md": (
        "731ca57c79293ff1d812e6ea426267cb80217319702f25dc4ccd1bc73bbd422d"
    ),
}
FAIL_CLOSED_BOTTOM_LINE = (
    "Use bottom line `Corrections required` whenever any applicable clause is `FAIL` or "
    "`INCOMPLETE`. Otherwise use `No supported non-passing items found in audited scope`."
)
RUBRIC_FAIL_CLOSED_BOTTOM_LINE = (
    "Use bottom line `Corrections required` when any applicable clause is `FAIL` or "
    "`INCOMPLETE`; otherwise use `No supported non-passing items found in audited scope`."
)
NO_FINDINGS_CONDITION = (
    "Only when all applicable clauses have zero `FAIL` and zero `INCOMPLETE` dispositions"
)
NO_FINDINGS_SENTENCE = "> No supported findings in the audited scope."
REPORT_CONTRACT = {
    "SKILL.md": (
        "## Build the complete checklist",
        "All 218 clause IDs must appear exactly once.",
        "Every `FAIL` and `INCOMPLETE` clause must reference at least one finding ID.",
        "Every finding must reference one or more clause IDs.",
        "a product-manager summary first",
        "No other Standard status is permitted.",
        FAIL_CLOSED_BOTTOM_LINE,
        NO_FINDINGS_CONDITION,
        NO_FINDINGS_SENTENCE,
    ),
    "references/audit-rubric.md": (
        "## 2. Create the clause ledger",
        "| `PASS` | Direct evidence proves the applicable requirement is satisfied. |",
        "| `FAIL` | Direct evidence proves the applicable requirement is unmet. |",
        "| `INCOMPLETE` | Required proof is absent, unavailable, restricted, "
        "or inconclusive, so `PASS` cannot be supported. |",
        "| `NOT APPLICABLE` | The clause's stated condition does not apply; "
        "the row states the specific reason. |",
        "Status totals must reconcile to 218.",
        "Every finding must reference one or more clause IDs.",
        "No other Standard status is permitted.",
        RUBRIC_FAIL_CLOSED_BOTTOM_LINE,
        NO_FINDINGS_CONDITION,
        NO_FINDINGS_SENTENCE,
    ),
    "assets/findings-report.md": (
        "# Product-manager summary",
        "- Bottom line:",
        "- Highest-priority correction:",
        "- Audit scope:",
        "- Important limits:",
        "- Assurance:",
        "| Status | Count |",
        "| `PASS` | `<count>` |",
        "| `FAIL` | `<count>` |",
        "| `INCOMPLETE` | `<count>` |",
        "| `NOT APPLICABLE` | `<count>` |",
        "| **Total** | **218** |",
        FAIL_CLOSED_BOTTOM_LINE,
        "## Required corrections",
        "### Fix first (`P1`)",
        "### Fix next (`P2`)",
        "### Required local correction (`P3`)",
        "## Findings",
        "- What is wrong:",
        "- Why it matters to the product:",
        "- Required correction:",
        "- Done when:",
        "- Affected Standard item count:",
        "## Technical appendix",
        "### Full clause-level checklist",
        "- Checklist rows: `218`",
        "- Status reconciliation:",
        "- Mapping reconciliation:",
        "| Standard section | Clause ID | Standard line | Requirement | Applicability reason "
        "| Evidence | Status | Finding IDs |",
        "Every inventory clause ID appears exactly once.",
        NO_FINDINGS_CONDITION,
        NO_FINDINGS_SENTENCE,
        "This audit is advisory and is not Supportability Gate certification.",
        "<PASS | FAIL | INCOMPLETE | NOT APPLICABLE>",
        "<every FAIL/INCOMPLETE maps to a finding; every finding maps to clauses>",
    ),
}
RELATIVE_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
REFERENCE_LINK = re.compile(r"(?m)^\s{0,3}\[[^\]]+\]:\s*(\S+)")
FORBIDDEN_RUNTIME_PATTERNS = {
    "AI-vendor or product name": re.compile(
        r"\b(?:alibaba cloud|amazon bedrock|anthropic|azure ai|bedrock|chatgpt|claude|"
        r"codex|cohere|copilot|cursor|deepmind|deepseek|gemini|google vertex|groq|grok|"
        r"hugging face|meta ai|mistral|ollama|openai|openrouter|perplexity|qwen|vertex ai|"
        r"xai)\b",
        re.IGNORECASE,
    ),
    "model identifier": re.compile(
        r"\b(?:gpt[- ]?\d[\w.-]*|claude[- ]?\d[\w.-]*|gemini[- ]?\d[\w.-]*|"
        r"llama[- ]?\d[\w.-]*|qwen[- ]?\d[\w.-]*|deepseek[- ]?[a-z0-9][\w.-]*|"
        r"gemma[- ]?\d[\w.-]*|phi[- ]?\d[\w.-]*|o[134](?:-[\w.-]+)?)\b",
        re.IGNORECASE,
    ),
    "connector instruction": re.compile(r"\b(?:connector|mcp)\b", re.IGNORECASE),
    "vendor-specific path or tool syntax": re.compile(
        r"(?:\.(?:anthropic|claude|codex|cursor|gemini|openai)(?:[\\/]|\b)|"
        r"claude_desktop_config|mcpServers|mcp__|codex_apps|openaiDeveloperDocs)",
        re.IGNORECASE,
    ),
    "automatic-remediation behavior": re.compile(
        r"(?:\bautomat(?:ic|ically)[ -]+(?:apply|change|correct|edit|fix|modify|"
        r"remediat|repair|rewrite|write)\w*|"
        r"\b(?:apply|change|correct|edit|fix|modify|remediat\w*|repair|rewrite|write)\b"
        r"[^\n.]{0,100}\bautomatically\b|"
        r"^\s*(?:[-*]\s*)?(?:after[^,\n]{0,40},\s*)?"
        r"(?:apply|change|correct|edit|fix|modify|remediate|repair|rewrite|write)\b"
        r"[^\n]{0,100}\b(?:audited target|target files?|source files?|code)\b|"
        r"\b(?:must|should|will)\s+(?:automatically\s+)?"
        r"(?:apply|change|correct|edit|fix|modify|remediate|repair|rewrite|write)\b)",
        re.IGNORECASE | re.MULTILINE,
    ),
}
REQUIRED_GUARDS = (
    "Never install dependencies or execute target code, builds, tests, package scripts, "
    "hooks, or repository-supplied executables.",
    "Never modify the audited target.",
    "If audit and remediation are requested together, perform only the audit and leave "
    "remediation for separate authorization.",
    "Do not emit terminal gate verdicts, compliance certification, or equivalent claims.",
    "Do not create another Gate or rules engine.",
)


def repository_files() -> set[str]:
    files: set[str] = set()
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if ".git" in relative.parts or "__pycache__" in relative.parts:
            continue
        if path.is_file() and path.suffix != ".pyc":
            files.add(relative.as_posix())
    return files


def validate_files(errors: list[str]) -> None:
    present = repository_files()
    for path in sorted(REQUIRED_FILES - present):
        errors.append(f"missing required file: {path}")
    for path in sorted(present - REQUIRED_FILES):
        errors.append(f"unexpected file or runtime surface: {path}")


def validate_standard(errors: list[str]) -> None:
    if not STANDARD.is_file():
        return
    digest = hashlib.sha256(STANDARD.read_bytes()).hexdigest()
    if digest != EXPECTED_STANDARD_SHA256:
        errors.append(
            f"bundled Standard SHA-256 mismatch: expected {EXPECTED_STANDARD_SHA256}, got {digest}"
        )
    attributes_path = ROOT / ".gitattributes"
    if attributes_path.is_file():
        attributes = attributes_path.read_text(encoding="utf-8")
        if attributes != EXPECTED_ATTRIBUTES:
            errors.append(".gitattributes must preserve Standard and inventory bytes")


def validate_exact_fields(
    errors: list[str], value: Any, expected: tuple[str, ...], label: str
) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{label} must be a JSON object")
        return False
    if set(value) != set(expected):
        errors.append(f"{label} fields must be exactly: {', '.join(expected)}")
        return False
    return True


def validate_required_strings(
    errors: list[str], value: dict[str, Any], fields: tuple[str, ...], label: str
) -> None:
    for field in fields:
        if not isinstance(value[field], str) or not value[field].strip():
            errors.append(f"{label} {field} must be a non-empty string")


def validate_applicability(errors: list[str], value: Any, label: str) -> None:
    if not validate_exact_fields(errors, value, APPLICABILITY_FIELDS, label):
        return
    profiles = value["profiles"]
    if (
        not isinstance(profiles, list)
        or not profiles
        or not all(isinstance(profile, str) and profile for profile in profiles)
    ):
        errors.append(f"{label} profiles must be a non-empty string array")
    if not isinstance(value["condition"], str) or not value["condition"].strip():
        errors.append(f"{label} condition must be a non-empty string")


def validate_clause(errors: list[str], value: Any, index: int) -> str | None:
    label = f"inventory clause {index}"
    if not validate_exact_fields(errors, value, CLAUSE_FIELDS, label):
        return None
    validate_required_strings(
        errors,
        value,
        (
            "clause_id",
            "statement",
            "enforcement_owner",
            "evidence_requirement",
            "blocking_test",
        ),
        label,
    )
    raw_clause_id = value["clause_id"]
    clause_id: str | None = raw_clause_id if isinstance(raw_clause_id, str) else None
    if clause_id is None or re.fullmatch(r"SS-\d{4}", clause_id) is None:
        errors.append(f"{label} clause_id must match SS-0000")
        clause_id = None
    if not isinstance(value["source_line"], int) or isinstance(value["source_line"], bool):
        errors.append(f"{label} source_line must be an integer")
    validate_applicability(errors, value["applicability"], f"{label} applicability")
    return clause_id


def validate_inventory_document(errors: list[str], value: Any) -> None:
    if not validate_exact_fields(errors, value, INVENTORY_FIELDS, "inventory"):
        return
    if value["schema_version"] != "1.0":
        errors.append("inventory schema_version must be '1.0'")
    if value["standard_sha256"] != EXPECTED_STANDARD_SHA256:
        errors.append(
            "inventory Standard SHA-256 binding mismatch: "
            f"expected {EXPECTED_STANDARD_SHA256}, got {value['standard_sha256']}"
        )
    clauses = value["clauses"]
    if not isinstance(clauses, list):
        errors.append("inventory clauses must be an array")
        return
    if len(clauses) != EXPECTED_INVENTORY_CLAUSES:
        errors.append(
            f"inventory must contain {EXPECTED_INVENTORY_CLAUSES} clauses: got {len(clauses)}"
        )
    clause_ids = [
        clause_id
        for index, clause in enumerate(clauses)
        if (clause_id := validate_clause(errors, clause, index)) is not None
    ]
    if len(set(clause_ids)) != len(clause_ids):
        errors.append(
            "inventory clause IDs must be unique: "
            f"{len(set(clause_ids))} unique of {len(clause_ids)}"
        )


def validate_inventory(errors: list[str]) -> None:
    if not INVENTORY.is_file():
        return
    raw = INVENTORY.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_INVENTORY_SHA256:
        errors.append(
            "canonical inventory SHA-256 mismatch: "
            f"expected {EXPECTED_INVENTORY_SHA256}, got {digest}"
        )
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        errors.append(f"canonical inventory is not valid UTF-8 JSON: {error}")
        return
    validate_inventory_document(errors, value)


def validate_report_contract(errors: list[str]) -> None:
    for relative, required_text in REPORT_CONTRACT.items():
        path = ROOT / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for item in required_text:
            if item not in text:
                errors.append(f"missing report contract in {relative}: {item}")
        validate_runtime_contract(errors, relative, text)


def validate_runtime_contract(errors: list[str], relative: str, text: str) -> None:
    digest = hashlib.sha256(text.encode()).hexdigest()
    if digest != RUNTIME_CONTRACT_SHA256[relative]:
        errors.append(f"runtime contract in {relative} differs from canonical content")


def validate_frontmatter_values(errors: list[str], fields: list[tuple[str, str]]) -> None:
    values = dict(fields)
    if values["name"] != "supportability-audit":
        errors.append("skill name must be supportability-audit")
    if ROOT.name != values["name"]:
        errors.append("skill name must match its parent directory")
    if values["description"] != EXPECTED_DESCRIPTION:
        errors.append("skill description differs from the public interface contract")


def validate_frontmatter(errors: list[str]) -> None:
    skill_path = ROOT / "SKILL.md"
    if not skill_path.is_file():
        return
    lines = skill_path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        errors.append("SKILL.md must start with YAML frontmatter")
        return
    try:
        end = lines.index("---", 1)
    except ValueError:
        errors.append("SKILL.md frontmatter is not closed")
        return
    fields: list[tuple[str, str]] = []
    for line in lines[1:end]:
        match = re.fullmatch(r"([a-z-]+):\s*(.+)", line)
        if match is None:
            errors.append(f"unsupported frontmatter syntax: {line!r}")
            continue
        fields.append((match.group(1), match.group(2)))
    if [key for key, _ in fields] != ["name", "description"]:
        errors.append("frontmatter must contain only name then description")
        return
    validate_frontmatter_values(errors, fields)


def validate_links(errors: list[str]) -> None:
    for relative in sorted(REQUIRED_FILES):
        if not relative.endswith(".md"):
            continue
        path = ROOT / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        targets = RELATIVE_LINK.findall(text) + REFERENCE_LINK.findall(text)
        for raw_target in targets:
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
                continue
            resolved = (path.parent / unquote(target)).resolve()
            if not resolved.is_relative_to(ROOT.resolve()):
                errors.append(f"relative link escapes skill root: {relative} -> {raw_target}")
            elif not resolved.exists():
                errors.append(f"broken relative link: {relative} -> {raw_target}")


def validate_skill_guards(errors: list[str], skill: str) -> None:
    for guard in REQUIRED_GUARDS:
        if guard not in skill:
            errors.append(f"missing read-only runtime guard: {guard}")
    if "No supported findings in the audited scope." not in skill:
        errors.append("SKILL.md lacks the exact no-findings sentence")


def validate_runtime_boundary(errors: list[str]) -> None:
    runtime_text: dict[str, str] = {}
    for relative in sorted(RUNTIME_FILES):
        path = ROOT / relative
        if path.is_file():
            try:
                runtime_text[relative] = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
    for label, pattern in FORBIDDEN_RUNTIME_PATTERNS.items():
        for relative, text in runtime_text.items():
            match = pattern.search(text)
            if match is not None:
                errors.append(f"{label} in runtime file {relative}: {match.group(0)!r}")
    validate_skill_guards(errors, runtime_text.get("SKILL.md", ""))
    if (ROOT / "scripts").exists():
        errors.append("runtime scripts are prohibited")
    if (ROOT / "agents").exists():
        errors.append("plugin or client metadata is prohibited")


def main() -> int:
    errors: list[str] = []
    validate_files(errors)
    validate_standard(errors)
    validate_inventory(errors)
    validate_frontmatter(errors)
    validate_links(errors)
    validate_report_contract(errors)
    validate_runtime_boundary(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
