from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[2]
STANDARD = ROOT / "references" / "supportability-standard.md"
EXPECTED_STANDARD_SHA256 = (
    "81653c5057c1555f8b6d41c6e5999d0b54caa178a2ca97a07216147ec16133e2"
)
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
    "references/audit-rubric.md",
    "references/supportability-standard.md",
    "src/supportability_audit/__init__.py",
    "src/supportability_audit/validate_repository.py",
    "tests/test_validate_repository.py",
}
RUNTIME_FILES = {
    "SKILL.md",
    "assets/findings-report.md",
    "references/audit-rubric.md",
    "references/supportability-standard.md",
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
)


def repository_files() -> set[str]:
    files: set[str] = set()
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if ".git" in relative.parts or "__pycache__" in relative.parts:
            continue
        if relative.parts[:2] == ("tests", "characterization"):
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
            f"bundled Standard SHA-256 mismatch: expected {EXPECTED_STANDARD_SHA256}, "
            f"got {digest}"
        )
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    if attributes != "references/supportability-standard.md -text -whitespace\n":
        errors.append(".gitattributes must preserve Standard bytes and whitespace")


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
    values = dict(fields)
    if values["name"] != "supportability-audit":
        errors.append("skill name must be supportability-audit")
    if ROOT.name != values["name"]:
        errors.append("skill name must match its parent directory")
    if values["description"] != EXPECTED_DESCRIPTION:
        errors.append("skill description differs from the public interface contract")


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


def validate_runtime_boundary(errors: list[str]) -> None:
    runtime_text: dict[str, str] = {}
    for relative in sorted(RUNTIME_FILES):
        path = ROOT / relative
        if path.is_file():
            runtime_text[relative] = path.read_text(encoding="utf-8")
    for label, pattern in FORBIDDEN_RUNTIME_PATTERNS.items():
        for relative, text in runtime_text.items():
            match = pattern.search(text)
            if match is not None:
                errors.append(f"{label} in runtime file {relative}: {match.group(0)!r}")
    skill = runtime_text.get("SKILL.md", "")
    for guard in REQUIRED_GUARDS:
        if guard not in skill:
            errors.append(f"missing read-only runtime guard: {guard}")
    if "No supported findings in the audited scope." not in skill:
        errors.append("SKILL.md lacks the exact no-findings sentence")
    if (ROOT / "scripts").exists():
        errors.append("runtime scripts are prohibited")
    if (ROOT / "agents").exists():
        errors.append("plugin or client metadata is prohibited")


def main() -> int:
    errors: list[str] = []
    validate_files(errors)
    validate_standard(errors)
    validate_frontmatter(errors)
    validate_links(errors)
    validate_runtime_boundary(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
