from __future__ import annotations

import importlib
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
        shutil.copytree(ROOT, self.repository, ignore=shutil.ignore_patterns(".git", "__pycache__"))

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

    def test_rejects_missing_required_file(self) -> None:
        (self.repository / "README.md").unlink()
        self.assert_rejected("missing required file: README.md")

    def test_rejects_changed_standard(self) -> None:
        standard = self.repository / "references" / "supportability-standard.md"
        standard.write_bytes(standard.read_bytes() + b"\n")
        self.assert_rejected("bundled Standard SHA-256 mismatch")

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

    def test_characterization_drivers_are_not_runtime_surface(self) -> None:
        driver = self.repository / "tests" / "characterization" / "sample.characterization.py"
        driver.parent.mkdir(parents=True, exist_ok=True)
        driver.write_text("raise SystemExit\n", encoding="utf-8")
        with mock.patch.object(validate_repository, "ROOT", self.repository):
            self.assertNotIn(
                "tests/characterization/sample.characterization.py",
                validate_repository.repository_files(),
            )


if __name__ == "__main__":
    unittest.main()
