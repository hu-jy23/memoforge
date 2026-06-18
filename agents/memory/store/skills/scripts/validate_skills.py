#!/usr/bin/env python3
"""Validate the HarnessVersion skills store."""

from __future__ import annotations

import re
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[1]
SUPPORT_FILES = [
    "README.md",
    "data/README.md",
    "data/schema.md",
    "data/freshness.md",
    "data/provenance.md",
    "queries/README.md",
    "scripts/README.md",
    "scripts/query_skills.py",
    "scripts/validate_skills.py",
]
SUPPORT_DIRS = {"data", "queries", "scripts", "__pycache__"}
REQUIRED_FRONTMATTER = {
    "title",
    "trigger",
    "domain",
    "first_seen",
    "promoted_from",
    "promoted_date",
    "confidence",
}
ALLOWED_CONFIDENCE = {"high", "medium"}
ALLOWED_DOMAINS = {"mindspore", "ascend", "mindformers", "general"}
REQUIRED_SECTIONS = {
    "trigger condition",
    "steps",
    "why it works",
    "known limitations",
    "related wiki pages",
}
PACKAGE_ALLOWED = {"SKILL.md", "README.md", "references", "scripts", "data", "queries"}


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def markdown_sections(text: str) -> set[str]:
    sections: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"^#{2,6}\s+(.+?)\s*$", line)
        if match:
            sections.add(match.group(1).strip().lower())
    return sections


def promoted_from_count(raw: str) -> int:
    value = raw.strip()
    if not value:
        return 0
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return 0
        return len([item for item in inner.split(",") if item.strip()])
    return len([item for item in re.split(r"[, ]+", value) if item.strip()])


def validate_skill_file(path: Path, label: str, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    frontmatter = parse_frontmatter(text)
    if not frontmatter:
        errors.append(f"{label}: missing YAML frontmatter")
        return

    missing = REQUIRED_FRONTMATTER - set(frontmatter)
    if missing:
        errors.append(f"{label}: missing frontmatter fields: {', '.join(sorted(missing))}")

    confidence = frontmatter.get("confidence", "")
    if confidence and confidence not in ALLOWED_CONFIDENCE:
        errors.append(f"{label}: invalid confidence: {confidence}")

    domain = frontmatter.get("domain", "")
    if domain and domain not in ALLOWED_DOMAINS:
        errors.append(f"{label}: invalid domain: {domain}")

    promoted_from = frontmatter.get("promoted_from", "")
    if promoted_from_count(promoted_from) < 2:
        errors.append(f"{label}: promoted_from must cite at least two task ids")

    trigger = frontmatter.get("trigger", "")
    if trigger and len(trigger.split()) < 4:
        errors.append(f"{label}: trigger is too short to guide application")

    sections = markdown_sections(text)
    for section in sorted(REQUIRED_SECTIONS - sections):
        errors.append(f"{label}: missing section: {section}")

    if "[[" not in text:
        errors.append(f"{label}: missing related wiki wikilink")


def validate_package(path: Path, errors: list[str]) -> None:
    skill_path = path / "SKILL.md"
    if not skill_path.exists():
        errors.append(f"{path.name}/: missing SKILL.md")
        return
    validate_skill_file(skill_path, f"{path.name}/SKILL.md", errors)

    for child in path.iterdir():
        if child.name not in PACKAGE_ALLOWED:
            errors.append(f"{path.name}/: unexpected package entry: {child.name}")


def main() -> int:
    errors: list[str] = []

    for rel_path in SUPPORT_FILES:
        if not (SKILLS_ROOT / rel_path).exists():
            errors.append(f"missing support file: {rel_path}")

    skill_count = 0
    for path in sorted(SKILLS_ROOT.iterdir()):
        if path.name in SUPPORT_DIRS or path.name == "README.md":
            continue
        if path.is_file() and path.suffix == ".md":
            skill_count += 1
            validate_skill_file(path, path.name, errors)
            continue
        if path.is_dir():
            skill_count += 1
            validate_package(path, errors)
            continue
        errors.append(f"unexpected skills store entry: {path.name}")

    if errors:
        print("Skills validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Skills validation passed: {skill_count} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
