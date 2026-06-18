#!/usr/bin/env python3
"""Compile deterministic immutable-prefix context for MemoForge agents."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "context" / "prefix_manifest.json"


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def profile_entries(manifest: dict[str, Any], profile: str) -> list[dict[str, str]]:
    profiles = manifest.get("profiles", {})
    if profile not in profiles:
        names = ", ".join(sorted(profiles))
        raise SystemExit(f"unknown profile: {profile!r}; available: {names}")
    shared = list(manifest.get("shared", []))
    specific = list(profiles[profile])
    return specific[:1] + shared + specific[1:]


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_prefix(profile: str, manifest_path: Path) -> tuple[str, list[str]]:
    manifest = load_manifest(manifest_path)
    entries = profile_entries(manifest, profile)
    errors: list[str] = []
    sections: list[str] = []
    full_hash = hashlib.sha256()

    header = [
        f"# Compiled MemoForge Prefix: {profile}",
        "",
        f"Manifest: {manifest_path.relative_to(ROOT)}",
        f"Manifest version: {manifest.get('version')}",
        "",
        "This file is generated from deterministic source files. Do not edit generated output directly.",
        "",
    ]
    sections.append("\n".join(header))

    for index, entry in enumerate(entries, 1):
        rel = Path(entry["path"])
        abs_path = ROOT / rel
        if not abs_path.exists():
            errors.append(f"missing: {rel}")
            continue
        if not abs_path.is_file():
            errors.append(f"not a file: {rel}")
            continue
        content = abs_path.read_text(encoding="utf-8")
        digest = file_sha256(abs_path)
        full_hash.update(str(rel).encode("utf-8"))
        full_hash.update(b"\0")
        full_hash.update(abs_path.read_bytes())
        sections.append(
            "\n".join(
                [
                    f"<!-- source:{index} path={rel} sha256={digest} -->",
                    f"# Source {index}: {rel}",
                    "",
                    f"Purpose: {entry.get('purpose', '')}",
                    "",
                    content.rstrip(),
                    "",
                ]
            )
        )

    sections.append(f"<!-- compiled_sha256={full_hash.hexdigest()} -->\n")
    return "\n".join(sections), errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, help="Profile name from prefix_manifest.json")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Manifest path")
    parser.add_argument("--output", help="Output file. Defaults to stdout unless --check is used.")
    parser.add_argument("--check", action="store_true", help="Validate manifest paths without writing output")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path

    compiled, errors = compile_prefix(args.profile, manifest_path)
    if errors:
        for error in errors:
            print(error)
        return 1

    if args.check:
        line_count = len(compiled.splitlines())
        print(f"prefix_ok profile={args.profile} lines={line_count}")
        return 0

    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = ROOT / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(compiled, encoding="utf-8")
        print(f"wrote {output.relative_to(ROOT)}")
    else:
        print(compiled)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
