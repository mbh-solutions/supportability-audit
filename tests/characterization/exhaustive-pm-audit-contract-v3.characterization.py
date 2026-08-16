from __future__ import annotations

import json
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from supportability_audit import validate_repository

EXPANDED_FEATURES = (
    "FAIL_CLOSED_BOTTOM_LINE",
    "INVENTORY",
    "validate_inventory",
    "validate_report_contract",
)
expanded_flags = tuple(hasattr(validate_repository, name) for name in EXPANDED_FEATURES)
if any(expanded_flags) and not all(expanded_flags):
    raise RuntimeError("partial expanded repository-validator API")
EXPANDED = all(expanded_flags)


def validate_case(mutate: Callable[[Path], None]) -> list[str]:
    original_root = validate_repository.ROOT
    original_standard = validate_repository.STANDARD
    original_inventory = getattr(validate_repository, "INVENTORY", None)
    try:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory) / "supportability-audit"
            shutil.copytree(
                original_root,
                repository,
                ignore=shutil.ignore_patterns(".git", ".ruff_cache", "__pycache__", "*.pyc"),
            )
            validate_repository.ROOT = repository
            validate_repository.STANDARD = repository / "references" / "supportability-standard.md"
            if EXPANDED:
                validate_repository.INVENTORY = (
                    repository / "references" / "normative_clause_inventory.json"
                )
            mutate(repository)
            errors: list[str] = []
            validate_repository.validate_files(errors)
            validate_repository.validate_standard(errors)
            if EXPANDED:
                validate_repository.validate_inventory(errors)
            validate_repository.validate_frontmatter(errors)
            validate_repository.validate_links(errors)
            if EXPANDED:
                validate_repository.validate_report_contract(errors)
            validate_repository.validate_runtime_boundary(errors)
            return errors
    finally:
        validate_repository.ROOT = original_root
        validate_repository.STANDARD = original_standard
        if EXPANDED:
            validate_repository.INVENTORY = original_inventory


def unchanged(_: Path) -> None:
    return


def remove_readme(repository: Path) -> None:
    (repository / "README.md").unlink()


def alter_standard(repository: Path) -> None:
    standard = repository / "references" / "supportability-standard.md"
    standard.write_bytes(standard.read_bytes() + b"\n")


def alter_frontmatter(repository: Path) -> None:
    skill = repository / "SKILL.md"
    skill.write_text(
        skill.read_text(encoding="utf-8").replace(
            "name: supportability-audit", "name: invalid-name", 1
        ),
        encoding="utf-8",
    )


def add_broken_link(repository: Path) -> None:
    readme = repository / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + "\n[broken](missing.md)\n",
        encoding="utf-8",
    )


def add_forbidden_runtime_text(repository: Path) -> None:
    skill = repository / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "\nOpenAI\n", encoding="utf-8")


def alter_inventory(repository: Path) -> None:
    inventory = repository / "references" / "normative_clause_inventory.json"
    inventory.write_bytes(inventory.read_bytes() + b"\n")


def remove_inventory(repository: Path) -> None:
    (repository / "references" / "normative_clause_inventory.json").unlink()


def update_inventory(repository: Path, mutate: Callable[[dict[str, Any]], None]) -> None:
    path = repository / "references" / "normative_clause_inventory.json"
    inventory = json.loads(path.read_bytes())
    mutate(inventory)
    path.write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def change_standard_binding(repository: Path) -> None:
    update_inventory(
        repository,
        lambda inventory: inventory.__setitem__("standard_sha256", "0" * 64),
    )


def remove_clause(repository: Path) -> None:
    update_inventory(repository, lambda inventory: inventory["clauses"].pop())


def duplicate_clause(repository: Path) -> None:
    def duplicate(inventory: dict[str, Any]) -> None:
        inventory["clauses"][-1] = inventory["clauses"][0]

    update_inventory(repository, duplicate)


def invalidate_clause_schema(repository: Path) -> None:
    def remove_field(inventory: dict[str, Any]) -> None:
        del inventory["clauses"][0]["blocking_test"]

    update_inventory(repository, remove_field)


def remove_report_contract(repository: Path) -> None:
    report = repository / "assets" / "findings-report.md"
    report.write_text(
        report.read_text(encoding="utf-8").replace("# Product-manager summary", "# Summary", 1),
        encoding="utf-8",
    )


def remove_pm_summary_field(repository: Path) -> None:
    report = repository / "assets" / "findings-report.md"
    report.write_text(
        report.read_text(encoding="utf-8").replace(
            "- Highest-priority correction:", "- First correction:", 1
        ),
        encoding="utf-8",
    )


def remove_checklist_column(repository: Path) -> None:
    report = repository / "assets" / "findings-report.md"
    report.write_text(
        report.read_text(encoding="utf-8").replace(
            "| Evidence | Status | Finding IDs |", "| Evidence | Status |", 1
        ),
        encoding="utf-8",
    )


def remove_fail_closed_predicate(repository: Path) -> None:
    skill = repository / "SKILL.md"
    skill.write_text(
        skill.read_text(encoding="utf-8").replace(
            validate_repository.FAIL_CLOSED_BOTTOM_LINE,
            "Choose either bottom line.",
            1,
        ),
        encoding="utf-8",
    )


def add_extra_standard_status(repository: Path) -> None:
    skill = repository / "SKILL.md"
    skill.write_text(
        skill.read_text(encoding="utf-8").replace(
            "| `NOT APPLICABLE` | The clause's stated condition does not apply; "
            "a specific reason is recorded. |",
            "| `NOT APPLICABLE` | The clause's stated condition does not apply; "
            "a specific reason is recorded. |\n| `UNKNOWN` | Unsupported fifth status. |",
            1,
        ),
        encoding="utf-8",
    )


legacy_cases = {
    "accepts_clean_repository": validate_case(unchanged),
    "rejects_altered_frontmatter": validate_case(alter_frontmatter),
    "rejects_altered_standard": validate_case(alter_standard),
    "rejects_broken_link": validate_case(add_broken_link),
    "rejects_forbidden_runtime_text": validate_case(add_forbidden_runtime_text),
    "rejects_missing_required_file": validate_case(remove_readme),
}
legacy_expected = {
    "accepts_clean_repository": [],
    "rejects_altered_frontmatter": [
        "skill name must be supportability-audit",
        "skill name must match its parent directory",
    ],
    "rejects_altered_standard": [
        "bundled Standard SHA-256 mismatch: expected "
        "81653c5057c1555f8b6d41c6e5999d0b54caa178a2ca97a07216147ec16133e2, got "
        "0008d5b1df55befd22a436ee8a4a5a576f648339447e33bf49bdde74ecd256d7"
    ],
    "rejects_broken_link": ["broken relative link: README.md -> missing.md"],
    "rejects_forbidden_runtime_text": [
        "AI-vendor or product name in runtime file SKILL.md: 'OpenAI'"
    ],
    "rejects_missing_required_file": ["missing required file: README.md"],
}
if EXPANDED:
    runtime_contract_error = "runtime contract in SKILL.md differs from canonical content"
    legacy_expected["rejects_altered_frontmatter"].append(runtime_contract_error)
    legacy_expected["rejects_forbidden_runtime_text"].insert(0, runtime_contract_error)
if legacy_cases != legacy_expected:
    raise RuntimeError(
        json.dumps({"actual": legacy_cases, "expected": legacy_expected}, sort_keys=True)
    )

if EXPANDED:
    report_runtime_contract_error = (
        "runtime contract in assets/findings-report.md differs from canonical content"
    )
    expanded_cases = {
        "rejects_altered_inventory": validate_case(alter_inventory),
        "rejects_duplicate_clause": validate_case(duplicate_clause),
        "rejects_extra_standard_status": validate_case(add_extra_standard_status),
        "rejects_invalid_clause_schema": validate_case(invalidate_clause_schema),
        "rejects_missing_checklist_column": validate_case(remove_checklist_column),
        "rejects_missing_clause": validate_case(remove_clause),
        "rejects_missing_fail_closed_predicate": validate_case(remove_fail_closed_predicate),
        "rejects_missing_inventory": validate_case(remove_inventory),
        "rejects_missing_pm_summary_field": validate_case(remove_pm_summary_field),
        "rejects_missing_report_contract": validate_case(remove_report_contract),
        "rejects_wrong_standard_binding": validate_case(change_standard_binding),
    }
    expanded_expected = {
        "rejects_altered_inventory": [
            "canonical inventory SHA-256 mismatch: expected "
            "02f58effce7bb27bf57536585d42b6d0241929ba29377fdbded4d93ecfe3eb9a, got "
            "94785ef3e0729a62f9dbfd2f56f105909c4edaf8319288de8ab150aa9c46cbab"
        ],
        "rejects_duplicate_clause": [
            "canonical inventory SHA-256 mismatch: expected "
            "02f58effce7bb27bf57536585d42b6d0241929ba29377fdbded4d93ecfe3eb9a, got "
            "d22d407901dcfb9492a07666457ce412f40efc5bc04985abf22e60cb9ee4a5cf",
            "inventory clause IDs must be unique: 217 unique of 218",
        ],
        "rejects_extra_standard_status": [runtime_contract_error],
        "rejects_invalid_clause_schema": [
            "canonical inventory SHA-256 mismatch: expected "
            "02f58effce7bb27bf57536585d42b6d0241929ba29377fdbded4d93ecfe3eb9a, got "
            "0821ec95b7046d11ffd1528ec1fe3455d567577919c9ab44338cb7f9b937dae7",
            "inventory clause 0 fields must be exactly: clause_id, source_line, statement, "
            "applicability, enforcement_owner, evidence_requirement, blocking_test",
        ],
        "rejects_missing_checklist_column": [
            "missing report contract in assets/findings-report.md: | Standard section | "
            "Clause ID | Standard line | Requirement | Applicability reason | Evidence | "
            "Status | Finding IDs |",
            report_runtime_contract_error,
        ],
        "rejects_missing_clause": [
            "canonical inventory SHA-256 mismatch: expected "
            "02f58effce7bb27bf57536585d42b6d0241929ba29377fdbded4d93ecfe3eb9a, got "
            "0eefe9e3adcd90d937ae90b7ccd6f4d78fbb37ef4efe156a04da0fd9d17e90e9",
            "inventory must contain 218 clauses: got 217",
        ],
        "rejects_missing_fail_closed_predicate": [
            "missing report contract in SKILL.md: " + validate_repository.FAIL_CLOSED_BOTTOM_LINE,
            runtime_contract_error,
        ],
        "rejects_missing_inventory": [
            "missing required file: references/normative_clause_inventory.json",
            "broken relative link: SKILL.md -> references/normative_clause_inventory.json",
            "broken relative link: references/audit-rubric.md -> normative_clause_inventory.json",
        ],
        "rejects_missing_pm_summary_field": [
            "missing report contract in assets/findings-report.md: - Highest-priority correction:",
            report_runtime_contract_error,
        ],
        "rejects_missing_report_contract": [
            "missing report contract in assets/findings-report.md: # Product-manager summary",
            report_runtime_contract_error,
        ],
        "rejects_wrong_standard_binding": [
            "canonical inventory SHA-256 mismatch: expected "
            "02f58effce7bb27bf57536585d42b6d0241929ba29377fdbded4d93ecfe3eb9a, got "
            "70433694a7ce73dcec0d39b8d8e7735a8e49545a713c9f5162c5814e0eb2737b",
            "inventory Standard SHA-256 binding mismatch: expected "
            "81653c5057c1555f8b6d41c6e5999d0b54caa178a2ca97a07216147ec16133e2, got "
            "0000000000000000000000000000000000000000000000000000000000000000",
        ],
    }
    if expanded_cases != expanded_expected:
        raise RuntimeError(
            json.dumps({"actual": expanded_cases, "expected": expanded_expected}, sort_keys=True)
        )

print(
    json.dumps(
        {
            "schema_version": "1.0",
            "scenario": "exhaustive-pm-audit-contract-v3",
            "behavior": {"contract": "PASS"},
        },
        sort_keys=True,
    )
)
