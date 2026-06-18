#!/usr/bin/env python3
"""Run MemoForge structural validation checks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFIX_PROFILES = ["planner", "coder", "verifier", "memory"]


def validate_json_file(label: str, path: str) -> int:
    print(f"== {label}")
    print(f"$ parse-json {path}")
    try:
        json.loads((ROOT / path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL {label}: {path}:{exc.lineno}:{exc.colno}: {exc.msg}")
        return 1
    print(f"PASS {label}")
    return 0


def run(label: str, command: list[str]) -> int:
    print(f"== {label}", flush=True)
    print("$ " + " ".join(command), flush=True)
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    if completed.returncode != 0:
        print(f"FAIL {label}: exit={completed.returncode}")
    else:
        print(f"PASS {label}")
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-workspace",
        action="store_true",
        help="Also validate current ephemeral workspace task artifacts and learning write-back.",
    )
    args = parser.parse_args()

    failures = 0
    py = sys.executable

    failures += validate_json_file("prefix manifest json", "context/prefix_manifest.json")
    failures += validate_json_file("runtime manifest json", "runtime/extension_manifest.json")

    for profile in PREFIX_PROFILES:
        failures += run(
            f"prefix {profile}",
            [py, "tools/compile_project_context.py", "--profile", profile, "--check"],
        )

    failures += run(
        "python compile",
        [
            py,
            "-m",
            "py_compile",
            "tools/compile_project_context.py",
            "tools/validate_goal_alignment.py",
            "tools/run_task_cycle_smoke.py",
            "tools/validate_harness.py",
            "tools/validate_runtime_extensions.py",
            "tools/validate_task_artifacts.py",
            "agents/memory/store/wiki/scripts/query_wiki.py",
            "agents/memory/store/wiki/scripts/validate_wiki.py",
            "agents/memory/store/skills/scripts/query_skills.py",
            "agents/memory/store/skills/scripts/validate_skills.py",
        ],
    )
    failures += run("wiki", [py, "agents/memory/store/wiki/scripts/validate_wiki.py"])
    failures += run("skills", [py, "agents/memory/store/skills/scripts/validate_skills.py"])
    failures += run(
        "skills query",
        [py, "agents/memory/store/skills/scripts/query_skills.py", "global norm", "--source", "all"],
    )
    failures += run("runtime extensions", [py, "tools/validate_runtime_extensions.py"])
    failures += run("goal alignment", [py, "tools/validate_goal_alignment.py"])
    failures += run("task cycle smoke", [py, "tools/run_task_cycle_smoke.py"])

    if args.include_workspace:
        failures += run(
            "task artifacts",
            [py, "tools/validate_task_artifacts.py", "--require-learning"],
        )

    if failures:
        print(f"harness_validation_fail failing_checks={failures}")
        return 1

    print("harness_validation_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
