from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
validate_repository = importlib.import_module("supportability_audit.validate_repository")

ROOT = Path(__file__).resolve().parents[1]


class RepositoryValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary_directory.name) / "supportability-audit"
        shutil.copytree(
            ROOT,
            self.repository,
            ignore=shutil.ignore_patterns(".git", ".ruff_cache", "__pycache__", "*.pyc"),
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "src/supportability_audit/validate_repository.py"],
            cwd=self.repository,
            capture_output=True,
            text=True,
            check=False,
        )

    def assert_rejected(self, expected_error: str) -> None:
        result = self.run_validator()
        self.assertEqual(1, result.returncode, result.stdout)
        self.assertIn(expected_error, result.stderr)

    def read_inventory(self) -> dict[str, object]:
        path = self.repository / "references" / "normative_clause_inventory.json"
        return json.loads(path.read_bytes())

    def write_inventory(self, inventory: dict[str, object]) -> None:
        path = self.repository / "references" / "normative_clause_inventory.json"
        path.write_text(
            json.dumps(inventory, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    def test_accepts_clean_repository(self) -> None:
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Repository validation passed.", result.stdout)

    def test_rejects_missing_required_file(self) -> None:
        (self.repository / "README.md").unlink()
        self.assert_rejected("missing required file: README.md")

    def test_rejects_changed_standard(self) -> None:
        standard = self.repository / "references" / "supportability-standard.md"
        standard.write_bytes(standard.read_bytes() + b"\n")
        self.assert_rejected("bundled Standard SHA-256 mismatch")

    def test_rejects_missing_inventory(self) -> None:
        (self.repository / "references" / "normative_clause_inventory.json").unlink()
        self.assert_rejected("missing required file: references/normative_clause_inventory.json")

    def test_rejects_altered_inventory(self) -> None:
        inventory = self.repository / "references" / "normative_clause_inventory.json"
        inventory.write_bytes(inventory.read_bytes() + b"\n")
        self.assert_rejected("canonical inventory SHA-256 mismatch")

    def test_rejects_wrong_standard_binding(self) -> None:
        inventory = self.read_inventory()
        inventory["standard_sha256"] = "0" * 64
        self.write_inventory(inventory)
        self.assert_rejected("inventory Standard SHA-256 binding mismatch")

    def test_rejects_missing_clause(self) -> None:
        inventory = self.read_inventory()
        clauses = inventory["clauses"]
        self.assertIsInstance(clauses, list)
        clauses.pop()
        self.write_inventory(inventory)
        self.assert_rejected("inventory must contain 218 clauses: got 217")

    def test_rejects_duplicate_clause(self) -> None:
        inventory = self.read_inventory()
        clauses = inventory["clauses"]
        self.assertIsInstance(clauses, list)
        clauses[-1] = clauses[0]
        self.write_inventory(inventory)
        self.assert_rejected("inventory clause IDs must be unique: 217 unique of 218")

    def test_rejects_invalid_inventory_schema(self) -> None:
        inventory = self.read_inventory()
        clauses = inventory["clauses"]
        self.assertIsInstance(clauses, list)
        first_clause = clauses[0]
        self.assertIsInstance(first_clause, dict)
        del first_clause["blocking_test"]
        self.write_inventory(inventory)
        self.assert_rejected("inventory clause 0 fields must be exactly")

    def test_rejects_missing_report_contract(self) -> None:
        report = self.repository / "assets" / "findings-report.md"
        report.write_text(
            report.read_text(encoding="utf-8").replace("# Product-manager summary", "# Summary", 1),
            encoding="utf-8",
        )
        self.assert_rejected(
            "missing report contract in assets/findings-report.md: # Product-manager summary"
        )

    def test_rejects_missing_pm_summary_field(self) -> None:
        report = self.repository / "assets" / "findings-report.md"
        report.write_text(
            report.read_text(encoding="utf-8").replace(
                "- Highest-priority correction:", "- First correction:", 1
            ),
            encoding="utf-8",
        )
        self.assert_rejected(
            "missing report contract in assets/findings-report.md: - Highest-priority correction:"
        )

    def test_rejects_missing_checklist_column(self) -> None:
        report = self.repository / "assets" / "findings-report.md"
        report.write_text(
            report.read_text(encoding="utf-8").replace(
                "| Evidence | Status | Finding IDs |",
                "| Evidence | Status |",
                1,
            ),
            encoding="utf-8",
        )
        self.assert_rejected(
            "missing report contract in assets/findings-report.md: "
            "| Standard section | Clause ID | Standard line | Requirement | "
            "Applicability reason | Evidence | Status | Finding IDs |"
        )

    def test_rejects_extra_standard_status(self) -> None:
        skill = self.repository / "SKILL.md"
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
        self.assert_rejected("status table in SKILL.md must contain exactly")

    def test_rejects_invalid_frontmatter(self) -> None:
        skill = self.repository / "SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8").replace(
                "name: supportability-audit", "name: invalid-name", 1
            ),
            encoding="utf-8",
        )
        self.assert_rejected("skill name must be supportability-audit")

    def test_rejects_broken_relative_link(self) -> None:
        readme = self.repository / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8") + "\n[broken](missing.md)\n",
            encoding="utf-8",
        )
        self.assert_rejected("broken relative link: README.md -> missing.md")

    def test_rejects_forbidden_runtime_text(self) -> None:
        skill = self.repository / "SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8") + "\nOpenAI\n",
            encoding="utf-8",
        )
        self.assert_rejected("AI-vendor or product name in runtime file SKILL.md")

    def test_rejects_unexpected_characterization_file(self) -> None:
        orphan = self.repository / "tests" / "characterization" / "orphan.golden.json"
        orphan.write_text("{}\n", encoding="utf-8")
        with mock.patch.object(validate_repository, "ROOT", self.repository):
            self.assertIn(
                "tests/characterization/orphan.golden.json",
                validate_repository.repository_files(),
            )
        self.assert_rejected(
            "unexpected file or runtime surface: tests/characterization/orphan.golden.json"
        )


if __name__ == "__main__":
    unittest.main()
