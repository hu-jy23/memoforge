#!/usr/bin/env python3
"""
Preprocess source materials (HTML or Markdown) into clean topic-grouped text files.

Usage:
    python preprocess.py <source_path> <output_dir>
    python preprocess.py /path/to/MindSpore-mindformers ./raw_sources
    python preprocess.py /path/to/AGENTS.md ./raw_sources
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Topic grouping rules
# Each value is a list of substrings; a file matches a topic if ANY substring
# appears in its path (forward-slash normalised).
# ---------------------------------------------------------------------------

MINDFORMERS_TOPICS: dict[str, list[str]] = {
    "installation":         ["installation", "env_variables", "RELEASE"],
    "core_trainer":         ["mindformers.core", "/mindformers.html", "trainer"],
    "models":               ["mindformers.models", "models/llama", "models/glm"],
    "dataset":              ["mindformers.dataset"],
    "generation":           ["mindformers.generation"],
    "modules_attention":    ["mindformers.modules"],
    "pipeline_pet":         ["mindformers.pipeline", "mindformers.pet"],
    "tools_config":         ["mindformers.tools", "mindformers.wrapper"],
    "advanced_development": ["advanced_development/"],
}

MINDSPORE_SELECTIVE_TOPICS: dict[str, list[str]] = {
    "nn_api":           ["api_python/mindspore.nn"],
    "communication_api":["api_python/mindspore.communication"],
    "amp_api":          ["api_python/mindspore.amp"],
    "env_var_list":     ["api_python/env_var_list"],
    "device_context":   ["api_python/mindspore.device_context"],
}

SOURCE_TYPE_MAP: dict[str, dict[str, list[str]]] = {
    "MindSpore-mindformers": MINDFORMERS_TOPICS,
    "MindSpore-docs":        MINDSPORE_SELECTIVE_TOPICS,
    "MindSpore-tutorials":   {},  # skip by default
}

# Files/directories to always skip regardless of topic match
SKIP_PATTERNS = ["_modules/", "genindex", "/search", "_sources/", "__pycache__"]

# Max chars per topic file sent to the LLM (~8-12K tokens for Haiku)
MAX_CHARS_PER_TOPIC = 35_000


# ---------------------------------------------------------------------------
# HTML extraction
# ---------------------------------------------------------------------------

def _extract_html_text(html_path: Path) -> str:
    """Strip Sphinx-generated HTML to clean structured text."""
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    # Remove navigation, chrome, scripts
    for tag in soup.find_all(["nav", "script", "style", "footer"]):
        tag.decompose()
    for tag in soup.find_all(True, class_=re.compile(
        r"(sidebar|navigation|breadcrumb|toctree|footer|headerlink|"
        r"sphinxsidebar|related|clearer|versionmodified)"
    )):
        tag.decompose()

    # Prefer the main documentation body
    main = (
        soup.find("div", role="main")
        or soup.find("div", class_=re.compile(r"\b(body|document|content)\b"))
        or soup.find("article")
        or soup.find("main")
        or soup.body
        or soup
    )

    lines: list[str] = []
    _walk(main, lines)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _walk(element, lines: list[str]) -> None:
    """Recursively convert element tree to structured text lines."""
    if element is None:
        return
    name = getattr(element, "name", None)
    if name is None:
        # NavigableString — handled by parent
        return
    if name in ("h1", "h2", "h3", "h4"):
        level = int(name[1])
        text = element.get_text(strip=True)
        if text:
            lines.append(f"\n{'#' * level} {text}")
        return
    if name in ("p",):
        text = element.get_text(" ", strip=True)
        if text:
            lines.append(text)
        return
    if name == "li":
        text = element.get_text(" ", strip=True)
        if text:
            lines.append(f"- {text}")
        return
    if name in ("pre", "code"):
        text = element.get_text()
        if text.strip():
            lines.append(f"```\n{text.strip()}\n```")
        return
    if name == "table":
        _walk_table(element, lines)
        return
    if name == "dt":
        text = element.get_text(strip=True)
        if text:
            lines.append(f"\n**{text}**")
        return
    if name == "dd":
        text = element.get_text(" ", strip=True)
        if text:
            lines.append(text)
        return
    # Default: recurse into children
    for child in element.children:
        _walk(child, lines)


def _walk_table(table, lines: list[str]) -> None:
    for row in table.find_all("tr"):
        cells = [td.get_text(strip=True) for td in row.find_all(["th", "td"])]
        if cells:
            lines.append(" | ".join(cells))


# ---------------------------------------------------------------------------
# Topic classification
# ---------------------------------------------------------------------------

def _classify_file(filepath: Path, topic_map: dict[str, list[str]]) -> str | None:
    path_str = filepath.as_posix()
    if any(p in path_str for p in SKIP_PATTERNS):
        return None
    for topic, patterns in topic_map.items():
        if any(p in path_str for p in patterns):
            return topic
    return None


def _detect_topic_map(source_dir: Path) -> dict[str, list[str]]:
    name = source_dir.name
    for key, topic_map in SOURCE_TYPE_MAP.items():
        if key in name:
            return topic_map
    # Unknown source directory: put everything into a single topic named after the dir
    return {"_all": [""]}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def preprocess_sources(source_path: Path, output_dir: Path) -> dict[str, Path]:
    """
    Convert source materials to clean topic-grouped text files.

    Returns:
        {topic_name: Path to clean text file}
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    topic_parts: dict[str, list[str]] = {}

    if source_path.is_file():
        suffix = source_path.suffix.lower()
        if suffix == ".html":
            text = _extract_html_text(source_path)
        else:
            text = source_path.read_text(encoding="utf-8", errors="ignore")
        if text.strip():
            topic_parts[source_path.stem] = [text]

    elif source_path.is_dir():
        topic_map = _detect_topic_map(source_path)

        # HTML files
        for html_file in sorted(source_path.rglob("*.html")):
            topic = _classify_file(html_file, topic_map)
            if topic is None:
                continue
            text = _extract_html_text(html_file)
            if text.strip():
                header = f"\n\n--- Source: {html_file.name} ---\n"
                topic_parts.setdefault(topic, []).append(header + text)

        # Markdown files at directory root (e.g. AGENTS.md)
        for md_file in sorted(source_path.glob("*.md")):
            topic = md_file.stem
            text = md_file.read_text(encoding="utf-8", errors="ignore")
            if text.strip():
                topic_parts.setdefault(topic, []).append(text)
    else:
        raise FileNotFoundError(f"source_path not found: {source_path}")

    # Write one file per topic (truncate if too large)
    result: dict[str, Path] = {}
    for topic_name, parts in topic_parts.items():
        combined = "\n\n".join(parts)
        if len(combined) > MAX_CHARS_PER_TOPIC:
            combined = (
                combined[:MAX_CHARS_PER_TOPIC]
                + f"\n\n[truncated at {MAX_CHARS_PER_TOPIC} chars]"
            )
        out_path = output_dir / f"{topic_name}.md"
        out_path.write_text(combined, encoding="utf-8")
        result[topic_name] = out_path
        print(f"  [preprocess] {topic_name}: {len(combined):,} chars -> {out_path.name}")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: preprocess.py <source_path> <output_dir>")
        sys.exit(1)
    result = preprocess_sources(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"\nProcessed {len(result)} topic(s):")
    for topic, path in result.items():
        size = path.stat().st_size
        print(f"  {topic}: {size:,} bytes")


if __name__ == "__main__":
    main()
