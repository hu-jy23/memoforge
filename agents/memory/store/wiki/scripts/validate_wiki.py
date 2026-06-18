#!/usr/bin/env python3
"""Validate required HarnessVersion wiki structure."""

from __future__ import annotations

import re
from pathlib import Path


WIKI_ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {"concepts", "api", "errors", "config", "workflows"}
REQUIRED_FRONTMATTER = {"title", "category", "sources", "last_updated", "confidence"}
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
INDEX_ENTRY_RE = re.compile(r"^\s*-\s+\[\[([^\]]+)\]\]")


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


def index_links() -> set[str]:
    index_path = WIKI_ROOT / "index.md"
    if not index_path.exists():
        return set()
    links: set[str] = set()
    for line in index_path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = INDEX_ENTRY_RE.match(line)
        if match:
            links.add(match.group(1))
    return links


def is_wiki_page_link(link: str) -> bool:
    parts = link.split("/", 1)
    return len(parts) == 2 and parts[0] in CATEGORIES and bool(parts[1].strip())


def main() -> int:
    errors: list[str] = []
    indexed = index_links()
    seen: set[str] = set()

    for category in sorted(CATEGORIES):
        root = WIKI_ROOT / category
        if not root.exists():
            errors.append(f"missing category directory: {category}")
            continue
        for path in sorted(root.glob("*.md")):
            rel = f"{category}/{path.stem}"
            seen.add(rel)
            text = path.read_text(encoding="utf-8", errors="replace")
            frontmatter = parse_frontmatter(text)
            missing = REQUIRED_FRONTMATTER - set(frontmatter)
            if missing:
                errors.append(f"{rel}: missing frontmatter fields: {', '.join(sorted(missing))}")
            if frontmatter.get("category") and frontmatter["category"] != category:
                errors.append(f"{rel}: category mismatch: {frontmatter['category']}")
            if rel not in indexed:
                errors.append(f"{rel}: missing from index.md")

            for link in WIKILINK_RE.findall(text):
                if not is_wiki_page_link(link):
                    continue
                target = WIKI_ROOT / f"{link}.md"
                if not target.exists():
                    errors.append(f"{rel}: broken wikilink [[{link}]]")

    for link in indexed:
        if link not in seen:
            errors.append(f"index.md: indexed page not found: [[{link}]]")

    if errors:
        print("Wiki validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Wiki validation passed: {len(seen)} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
