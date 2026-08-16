from __future__ import annotations

import json
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path

from supportability_audit import validate_repository


def validate_case(mutate: Callable[[Path], None]) -> list[str]:
    original_root = validate_repository.ROOT
    original_standard = validate_repository.STANDARD
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
            mutate(repository)
            errors: list[str] = []
            validate_repository.validate_files(errors)
            validate_repository.validate_standard(errors)
            validate_repository.validate_frontmatter(errors)
            validate_repository.validate_links(errors)
            validate_repository.validate_runtime_boundary(errors)
            return errors
    finally:
        validate_repository.ROOT = original_root
        validate_repository.STANDARD = original_standard


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


cases = {
    "accepts_clean_repository": validate_case(unchanged),
    "rejects_altered_frontmatter": validate_case(alter_frontmatter),
    "rejects_altered_standard": validate_case(alter_standard),
    "rejects_broken_link": validate_case(add_broken_link),
    "rejects_forbidden_runtime_text": validate_case(add_forbidden_runtime_text),
    "rejects_missing_required_file": validate_case(remove_readme),
}
print(
    json.dumps(
        {
            "schema_version": "1.0",
            "scenario": "repository-contract-validation-v2",
            "behavior": {"cases": cases},
        },
        sort_keys=True,
    )
)
