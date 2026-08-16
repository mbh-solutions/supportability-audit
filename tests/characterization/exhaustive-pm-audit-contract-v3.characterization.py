from __future__ import annotations

import json
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from supportability_audit import validate_repository


def validate_case(mutate: Callable[[Path], None]) -> list[str]:
    original_root = validate_repository.ROOT
    original_standard = validate_repository.STANDARD
    original_inventory = validate_repository.INVENTORY
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
            validate_repository.INVENTORY = (
                repository / "references" / "normative_clause_inventory.json"
            )
            mutate(repository)
            errors: list[str] = []
            validate_repository.validate_files(errors)
            validate_repository.validate_standard(errors)
            validate_repository.validate_inventory(errors)
            validate_repository.validate_frontmatter(errors)
            validate_repository.validate_links(errors)
            validate_repository.validate_report_contract(errors)
            validate_repository.validate_runtime_boundary(errors)
            return errors
    finally:
        validate_repository.ROOT = original_root
        validate_repository.STANDARD = original_standard
        validate_repository.INVENTORY = original_inventory


def unchanged(_: Path) -> None:
    return


def remove_readme(repository: Path) -> None:
    (repository / "README.md").unlink()


def alter_standard(repository: Path) -> None:
    standard = repository / "references" / "supportability-standard.md"
    standard.write_bytes(standard.read_bytes() + b"\n")


def alter_inventory(repository: Path) -> None:
    inventory = repository / "references" / "normative_clause_inventory.json"
    inventory.write_bytes(inventory.read_bytes() + b"\n")


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


cases = {
    "accepts_clean_repository": validate_case(unchanged),
    "rejects_altered_frontmatter": validate_case(alter_frontmatter),
    "rejects_altered_inventory": validate_case(alter_inventory),
    "rejects_altered_standard": validate_case(alter_standard),
    "rejects_broken_link": validate_case(add_broken_link),
    "rejects_duplicate_clause": validate_case(duplicate_clause),
    "rejects_extra_standard_status": validate_case(add_extra_standard_status),
    "rejects_forbidden_runtime_text": validate_case(add_forbidden_runtime_text),
    "rejects_invalid_clause_schema": validate_case(invalidate_clause_schema),
    "rejects_missing_clause": validate_case(remove_clause),
    "rejects_missing_report_contract": validate_case(remove_report_contract),
    "rejects_missing_required_file": validate_case(remove_readme),
    "rejects_wrong_standard_binding": validate_case(change_standard_binding),
}
print(
    json.dumps(
        {
            "schema_version": "1.0",
            "scenario": "exhaustive-pm-audit-contract-v3",
            "behavior": {"cases": cases},
        },
        sort_keys=True,
    )
)
