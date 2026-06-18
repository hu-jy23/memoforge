#!/usr/bin/env python3
"""Search HarnessVersion promoted skills and potential skill candidates."""

from __future__ import annotations

import argparse
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[1]
STORE_ROOT = SKILLS_ROOT.parent
LEARNING_ROOT = STORE_ROOT / "learning"
SUPPORT_DIRS = {"data", "queries", "scripts", "__pycache__"}


def iter_skill_files() -> list[Path]:
    paths: list[Path] = []
    for path in sorted(SKILLS_ROOT.iterdir()):
        if path.name in SUPPORT_DIRS or path.name == "README.md":
            continue
        if path.is_file() and path.suffix == ".md":
            paths.append(path)
        elif path.is_dir() and (path / "SKILL.md").exists():
            paths.append(path / "SKILL.md")
    return paths


def iter_learning_candidates() -> list[Path]:
    if not LEARNING_ROOT.exists():
        return []
    candidates: list[Path] = []
    for path in sorted(LEARNING_ROOT.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        if "potential skill" in text and "yes" in text:
            candidates.append(path)
    return candidates


def first_content_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("---"):
            return line
    return ""


def search(paths: list[Path], terms: list[str], root: Path) -> list[tuple[int, Path, str]]:
    matches: list[tuple[int, Path, str]] = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        haystack = text.lower()
        if all(term in haystack for term in terms):
            score = sum(haystack.count(term) for term in terms)
            matches.append((score, path.relative_to(root), first_content_line(text)))
    return sorted(matches, key=lambda item: (-item[0], str(item[1])))


def main() -> int:
    parser = argparse.ArgumentParser(description="Search HarnessVersion skills and promotion candidates.")
    parser.add_argument("query", help="Keyword query. Terms are AND-matched case-insensitively.")
    parser.add_argument(
        "--source",
        choices=["skills", "learning", "all"],
        default="all",
        help="Search promoted skills, potential learning candidates, or both.",
    )
    parser.add_argument("--limit", type=int, default=20, help="Maximum results to print.")
    args = parser.parse_args()

    terms = [term.lower() for term in args.query.split() if term.strip()]
    if not terms:
        parser.error("query must contain at least one non-empty term")

    results: list[tuple[str, int, Path, str]] = []
    if args.source in {"skills", "all"}:
        for score, path, first_line in search(iter_skill_files(), terms, SKILLS_ROOT):
            results.append(("skill", score, path, first_line))
    if args.source in {"learning", "all"}:
        for score, path, first_line in search(iter_learning_candidates(), terms, STORE_ROOT):
            results.append(("candidate", score, path, first_line))

    for kind, score, path, first_line in sorted(results, key=lambda item: (-item[1], item[0], str(item[2])))[: args.limit]:
        print(f"{kind} | {path} | score={score} | {first_line}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
