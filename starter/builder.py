#!/usr/bin/env python3
"""
Wiki Builder — bootstrap the domain knowledge wiki from source documentation.

Usage:
    python builder.py --sources /path/to/domain-docs
    python builder.py --sources /path/to/AGENTS.md
    python builder.py --sources /path/to/domain-docs \\
                      --model claude-haiku-4-5-20251001 \\
                      --topics installation,core_trainer
    python builder.py --sources /path/to/domain-docs --dry-run

Outputs:
    - Wiki pages written to ../../agents/memory/store/wiki/
    - Updated index.md and log.md in the wiki directory
    - build_result.json written to this directory
    - Returns dict with pages_created, topics_processed, etc.

Supports any Anthropic model. Default: claude-haiku-4-5-20251001
For higher quality, use: claude-sonnet-4-6
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

import shutil
import subprocess

from preprocess import preprocess_sources

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

STARTER_DIR = Path(__file__).parent.resolve()
WIKI_DIR = (STARTER_DIR / "../agents/memory/store/wiki").resolve()

DEFAULT_MODEL = "claude-haiku-4-5-20251001"

# ---------------------------------------------------------------------------
# System prompt (sent as the `system` parameter in every SDK call)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a wiki builder for a domain-specific software development harness.

The harness helps AI coding agents work in a specialized engineering
environment where generic model knowledge is incomplete. Replace this paragraph
for your domain before production use. State the target framework, hardware,
toolchain, API surface, validation commands, and the ways mainstream software
knowledge does not transfer reliably.

Your job: given pre-processed source documentation for one topic, extract the
facts a developer agent MUST know and write focused wiki pages.

## What to capture (high value)
- API signatures and critical parameters with types and constraints
- Configuration field names, valid values, and common invalid mistakes
- Version compatibility tables across framework, runtime, hardware, drivers, and tools
- Installation steps and dependency ordering
- Environment variables that change runtime behaviour
- Error patterns with their root causes and fixes
- Pitfalls where the target environment differs from mainstream tools

## What to skip
- General intro prose already known by a capable developer
- Marketing comparisons
- Facts already in any standard ML/Python knowledge base
- Repeated content — write once, cross-reference with wikilinks

## Output format (STRICT)
For each wiki page output EXACTLY this block. No text outside these delimiters.

<<<WIKI_PAGE: {category}/{filename}.md>>>
---
title: {Human-readable title}
category: concepts | api | errors | config | workflows
sources: ["{short source description}"]
last_updated: {YYYY-MM-DD}
confidence: high | medium | low
---

{Markdown body.
First paragraph: ONE sentence summarising this page (copied verbatim into index.md).
Use ## for major sections, ### for subsections.
Code: ```python / ```bash / ```yaml with language tag.
Cross-references: [[category/page-name]] wikilink syntax.
No fabrication: if uncertain, use a "> **Note (low confidence):**" blockquote.}

<<<END_WIKI_PAGE>>>

Categories:
  concepts/  — terminology, hardware abstractions, architecture concepts
  api/       — API signatures, parameter semantics, behavioural quirks
  errors/    — error patterns with root causes and fixes
  config/    — YAML config fields, valid values, runtime flags
  workflows/ — multi-step procedures, training launch sequences

Write 1-5 pages per topic. Prefer narrow focused pages over one large page.
Split naturally at API module or concept boundaries.
"""

# Regex to parse wiki pages out of model output
WIKI_PAGE_RE = re.compile(
    r"<<<WIKI_PAGE:\s*(.+?)>>>\n(.*?)<<<END_WIKI_PAGE>>>",
    re.DOTALL,
)

# ---------------------------------------------------------------------------
# LLM invocation
# ---------------------------------------------------------------------------

def _ensure_claude_cli() -> str:
    """Return path to claude CLI or raise."""
    path = shutil.which("claude")
    if not path:
        raise FileNotFoundError(
            "claude CLI not found on PATH. Install Claude Code: https://claude.ai/code"
        )
    return path


def _invoke_model(
    _client: None,  # unused; kept for call-site compatibility
    model: str,
    topic_name: str,
    content: str,
) -> list[tuple[str, str]]:
    """
    Call the model for one topic batch via `claude --print` CLI.

    Returns:
        [(relative_wiki_path, page_markdown), ...]
    """
    claude_bin = _ensure_claude_cli()
    today = date.today().isoformat()

    # Combine system instructions + user content into a single prompt.
    # claude --print treats the positional argument as the initial user message;
    # prepending SYSTEM_PROMPT gives the model full instructions in one pass.
    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"---\n"
        f"Topic: {topic_name}\n"
        f"Date: {today}\n\n"
        f"## Source content\n\n{content}"
    )

    result = subprocess.run(
        [claude_bin, "--print", "--output-format", "text", "--model", model, full_prompt],
        capture_output=True,
        text=True,
        cwd=str(STARTER_DIR),
        timeout=180,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"claude --print failed (exit {result.returncode}):\n{result.stderr[:600]}"
        )

    raw = result.stdout.strip()
    pages = []
    for match in WIKI_PAGE_RE.finditer(raw):
        rel_path = match.group(1).strip()
        page_md = match.group(2).strip()
        pages.append((rel_path, page_md))

    if not pages:
        fallback_path = f"concepts/raw_{topic_name}.md"
        print(f"  [warn] No WIKI_PAGE blocks found for '{topic_name}'; saving raw output.")
        pages.append((fallback_path, raw))

    return pages


# ---------------------------------------------------------------------------
# Wiki file writing
# ---------------------------------------------------------------------------

def _write_pages(pages: list[tuple[str, str]]) -> list[str]:
    written = []
    for rel_path, content in pages:
        dest = WIKI_DIR / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        written.append(rel_path)
        print(f"  wrote {rel_path}")
    return written


def _update_index(all_pages: list[tuple[str, str]]) -> None:
    """Append new entries to wiki/index.md."""
    index_path = WIKI_DIR / "index.md"
    existing = index_path.read_text(encoding="utf-8") if index_path.exists() else ""

    # Group new pages by category
    by_category: dict[str, list[str]] = {}
    for rel_path, content in all_pages:
        parts = rel_path.split("/")
        category = parts[0] if len(parts) > 1 else "concepts"

        # Extract first non-frontmatter, non-heading paragraph as summary
        summary = _extract_summary(content)
        stem = rel_path.removesuffix(".md")
        entry = f"- [[{stem}]] — {summary}"
        by_category.setdefault(category.capitalize(), []).append(entry)

    additions = "\n".join(
        f"\n## {cat}\n" + "\n".join(entries)
        for cat, entries in sorted(by_category.items())
    )
    index_path.write_text(existing + additions + "\n", encoding="utf-8")


def _extract_summary(page_content: str) -> str:
    """Pull the first-paragraph sentence from a wiki page for the index entry."""
    in_frontmatter = False
    for line in page_content.splitlines():
        stripped = line.strip()
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        if stripped and not stripped.startswith("#") and not stripped.startswith("```"):
            return stripped[:140]
    return "(no summary)"


def _update_log(topics: list[str], page_count: int) -> None:
    log_path = WIKI_DIR / "log.md"
    today = date.today().isoformat()
    entry = (
        f"\n## [{today}] init | Starter Agent bootstrap — "
        f"topics={','.join(topics)} pages_created={page_count}\n"
    )
    existing = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    log_path.write_text(existing + entry, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main build function
# ---------------------------------------------------------------------------

def build_wiki(
    source_path: Path,
    model: str = DEFAULT_MODEL,
    topic_filter: list[str] | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Full wiki build pipeline.

    1. Pre-process source materials into topic-grouped files.
    2. For each topic, invoke the model to produce wiki pages.
    3. Write pages, update index.md and log.md.
    4. Write build_result.json and return the result dict.
    """
    raw_dir = STARTER_DIR / "raw_sources"
    raw_dir.mkdir(exist_ok=True)

    print(f"[builder] Pre-processing: {source_path}")
    topic_files = preprocess_sources(source_path, raw_dir)

    if topic_filter:
        topic_files = {k: v for k, v in topic_files.items() if k in topic_filter}

    if dry_run:
        print("\n[dry-run] Would process these topics:")
        for name, path in topic_files.items():
            chars = len(path.read_text(encoding="utf-8"))
            print(f"  {name}: {chars:,} chars")
        return {"dry_run": True, "topics": list(topic_files.keys())}

    client = None  # CLI-based invocation; no SDK client needed
    all_pages: list[tuple[str, str]] = []
    failed_topics: list[str] = []

    for topic_name, topic_file in topic_files.items():
        content = topic_file.read_text(encoding="utf-8")
        if not content.strip():
            print(f"  [skip] {topic_name}: empty after preprocessing")
            continue

        print(f"\n[builder] {topic_name} ({len(content):,} chars) → {model}")
        try:
            pages = _invoke_model(client, model, topic_name, content)
            print(f"  extracted {len(pages)} page(s)")
            _write_pages(pages)
            all_pages.extend(pages)
        except Exception as exc:
            print(f"  [error] {topic_name}: {exc}")
            failed_topics.append(topic_name)

    print("\n[builder] Updating index.md and log.md ...")
    if all_pages:
        _update_index(all_pages)
    _update_log(list(topic_files.keys()), len(all_pages))

    result = {
        "status": "success" if not failed_topics else "partial",
        "topics_processed": [t for t in topic_files if t not in failed_topics],
        "topics_failed": failed_topics,
        "pages_created": len(all_pages),
        "page_paths": [p for p, _ in all_pages],
        "wiki_dir": str(WIKI_DIR),
    }

    result_path = STARTER_DIR / "build_result.json"
    result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[builder] Done. {len(all_pages)} pages created → {result_path.name}")
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap domain wiki from source documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--sources", required=True,
        help="Path to source directory (HTML docs) or single file (.md, .html)",
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Anthropic model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--topics",
        help="Comma-separated topic filter, e.g. installation,core_trainer",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show topics and char counts without calling the model",
    )
    args = parser.parse_args()

    source_path = Path(args.sources).resolve()
    if not source_path.exists():
        print(f"ERROR: source not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    topic_filter = args.topics.split(",") if args.topics else None
    result = build_wiki(source_path, args.model, topic_filter, args.dry_run)

    if not args.dry_run:
        print("\n--- Build result ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
