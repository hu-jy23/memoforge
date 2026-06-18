#!/usr/bin/env python3
"""Lightweight keyword search for the HarnessVersion LLM Wiki."""

from __future__ import annotations

import argparse
from pathlib import Path


WIKI_ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {"concepts", "api", "errors", "config", "workflows"}


def iter_pages(category: str | None):
    cats = [category] if category else sorted(CATEGORIES)
    for cat in cats:
        root = WIKI_ROOT / cat
        if not root.exists():
            continue
        yield from sorted(root.glob("*.md"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Search HarnessVersion wiki pages.")
    parser.add_argument("query", help="Keyword query. Terms are AND-matched case-insensitively.")
    parser.add_argument("--category", choices=sorted(CATEGORIES), help="Restrict search to one category.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum results to print.")
    args = parser.parse_args()

    terms = [term.lower() for term in args.query.split() if term.strip()]
    if not terms:
        parser.error("query must contain at least one non-empty term")

    matches: list[tuple[int, Path, str]] = []
    for path in iter_pages(args.category):
        text = path.read_text(encoding="utf-8", errors="replace")
        haystack = text.lower()
        if all(term in haystack for term in terms):
            score = sum(haystack.count(term) for term in terms)
            first_line = next(
                (line.strip() for line in text.splitlines() if line.strip() and not line.startswith("---")),
                "",
            )
            matches.append((score, path, first_line))

    for score, path, first_line in sorted(matches, key=lambda item: (-item[0], str(item[1])))[: args.limit]:
        rel = path.relative_to(WIKI_ROOT)
        print(f"{rel} | score={score} | {first_line}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
