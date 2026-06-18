#!/usr/bin/env python3
"""Run an isolated smoke test for the MemoForge task-cycle protocol."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "smoke-task-cycle-01"
CANDIDATE_ID = f"{TASK_ID}-candidate-01"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_validation_command(sandbox: Path, evidence_log: Path) -> int:
    command = [
        sys.executable,
        "-m",
        "py_compile",
        f"workspace/patch/{TASK_ID}/smoke_module.py",
    ]
    completed = subprocess.run(command, cwd=sandbox, text=True, capture_output=True)
    write(
        evidence_log,
        "\n".join(
            [
                "# Commands Log",
                "",
                "$ " + " ".join(command),
                f"exit_code={completed.returncode}",
                "",
                "## stdout",
                completed.stdout or "(empty)",
                "",
                "## stderr",
                completed.stderr or "(empty)",
            ]
        ),
    )
    return completed.returncode


def build_cycle(sandbox: Path) -> tuple[Path, Path]:
    workspace = sandbox / "workspace"
    learning_root = sandbox / "learning"
    patch_dir = workspace / "patch" / TASK_ID
    evidence_dir = workspace / "evidence" / TASK_ID

    write(
        workspace / "task_contract.md",
        f"""
        # Task Contract

        ## Objective

        Create a minimal smoke module and prove the MemoForge task artifact protocol can validate a complete pass cycle in an isolated workspace.

        ## Inputs / Outputs

        - Inputs: task protocol templates and validator.
        - Expected outputs: `workspace/patch/{TASK_ID}/smoke_module.py` and protocol artifacts.

        ## Constraints

        - Use only standard-library Python.
        - Keep all task artifacts inside the isolated workspace.
        - Cite evidence from `workspace/evidence/{TASK_ID}/`.

        ## Validation Command

        ```bash
        python3 -m py_compile workspace/patch/{TASK_ID}/smoke_module.py
        ```

        ## Evaluation Command

        No separate evaluation command.

        ## Promotion Criteria

        - Candidate passes Python syntax validation.
        - Candidate ledger, evidence refs, verify result, promotion decision, and learning record pass `tools/validate_task_artifacts.py --require-learning`.
        - No skill promotion from this smoke task.

        ## Out Of Scope

        - Domain runtime behavior.
        - Persistent wiki or notes write-back.
        """,
    )

    write_json(
        workspace / "plan.json",
        {
            "task_id": TASK_ID,
            "goal": "Validate a complete isolated MemoForge task cycle.",
            "subtasks": [
                {
                    "id": "contract",
                    "description": "Create task contract.",
                    "context_refs": ["workspace/task_contract.md", "docs/task_artifact_protocol.md"],
                    "depends_on": [],
                },
                {
                    "id": "implement",
                    "description": "Create smoke module.",
                    "context_refs": [f"workspace/patch/{TASK_ID}/smoke_module.py"],
                    "depends_on": ["contract"],
                },
                {
                    "id": "verify",
                    "description": "Run syntax validation and record evidence.",
                    "context_refs": [f"workspace/evidence/{TASK_ID}/commands.log"],
                    "depends_on": ["implement"],
                },
                {
                    "id": "writeback",
                    "description": "Create evidence-backed learning record.",
                    "context_refs": [
                        "workspace/candidates.jsonl",
                        "workspace/verify_result.json",
                        "workspace/promotion_decision.md",
                    ],
                    "depends_on": ["verify"],
                },
            ],
        },
    )

    write(
        patch_dir / "smoke_module.py",
        """
        def smoke_value() -> int:
            return 1
        """,
    )
    write(
        workspace / "coder_summary.md",
        f"""
        # Coder Summary

        - task_id: `{TASK_ID}`
        - candidate_id: `{CANDIDATE_ID}`
        - What changed: created `workspace/patch/{TASK_ID}/smoke_module.py`.
        - Why: provide a deterministic pass candidate for the task-cycle smoke test.
        - Open questions: none.
        - Novel pattern flag: NO.
        """,
    )

    command_log = evidence_dir / "commands.log"
    exit_code = run_validation_command(sandbox, command_log)
    if exit_code != 0:
        raise RuntimeError(f"smoke validation command failed; see {command_log}")

    candidate_entries = [
        {
            "candidate_id": CANDIDATE_ID,
            "task_id": TASK_ID,
            "parent_id": None,
            "role": "coder",
            "status": "implemented",
            "summary": "Created a minimal smoke module for isolated protocol validation.",
            "artifact_refs": [
                f"workspace/patch/{TASK_ID}/smoke_module.py",
                "workspace/coder_summary.md",
            ],
            "evidence_refs": [],
            "timestamp": "2026-05-29",
        },
        {
            "candidate_id": CANDIDATE_ID,
            "task_id": TASK_ID,
            "parent_id": None,
            "role": "verifier",
            "status": "pass",
            "summary": "Syntax validation passed and evidence was recorded.",
            "artifact_refs": [f"workspace/patch/{TASK_ID}/smoke_module.py"],
            "evidence_refs": [f"workspace/evidence/{TASK_ID}/commands.log"],
            "timestamp": "2026-05-29",
        },
    ]
    write(
        workspace / "candidates.jsonl",
        "\n".join(json.dumps(entry, separators=(",", ":")) for entry in candidate_entries),
    )

    write_json(
        workspace / "verify_result.json",
        {
            "task_id": TASK_ID,
            "candidate_id": CANDIDATE_ID,
            "status": "pass",
            "log_summary": "Python syntax validation passed for the isolated smoke module.",
            "failure_reason": "",
            "success_pattern": "A complete task cycle can be represented by task_contract, plan, candidates, evidence, verify_result, promotion_decision, and learning artifacts.",
            "potential_skill": False,
            "evidence_refs": [f"workspace/evidence/{TASK_ID}/commands.log"],
            "findings": [
                {
                    "severity": "info",
                    "item": "Protocol smoke",
                    "detail": "The isolated task cycle contains a pass candidate and concrete command evidence.",
                }
            ],
            "suggested_fix": "",
        },
    )

    write(
        workspace / "promotion_decision.md",
        f"""
        # Promotion Decision

        ## Candidate Decision

        - Decision: accept
        - Candidate ID: `{CANDIDATE_ID}`
        - Task ID: `{TASK_ID}`

        ## Evidence Summary

        - Evidence refs:
          - `workspace/evidence/{TASK_ID}/commands.log`
        - Verification result: pass

        ## Memory Write-back Recommendation

        - learning: yes
        - notes: no
        - wiki: no
        - skills: no

        ## Skill Promotion Recommendation

        - Promote to skill: no
        - Evidence threshold: smoke test only
        - Required follow-up: none

        ## Wiki / Notes Update Recommendation

        - Wiki update: no
        - Notes update: no
        - Destination: none
        - Freshness / provenance requirement: not applicable

        ## Rationale

        The smoke candidate proves protocol completeness only. It carries no domain fact worth promoting.

        ## Residual Risks

        - This smoke test does not validate a real domain runtime.
        """,
    )

    write(
        learning_root / f"{TASK_ID}.md",
        f"""
        ## {TASK_ID} | 2026-05-29 | pass

        **Summary**: Isolated smoke task proved the task artifact protocol can validate a complete pass cycle.

        **Task contract**: `workspace/task_contract.md` defines objective, constraints, validation command, and promotion criteria.

        **Candidate evidence**: Candidate `{CANDIDATE_ID}` is recorded in `workspace/candidates.jsonl`. Evidence refs:
        - `workspace/evidence/{TASK_ID}/commands.log`

        **Outcome**: pass. `workspace/verify_result.json` records the syntax validation pass.

        **Promotion decision**: `workspace/promotion_decision.md` recommends learning only and no notes, wiki, or skills promotion.

        **Domain facts**:
        - None. This is protocol smoke evidence only.

        **Potential skill**: no.
        """,
    )

    return workspace, learning_root


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="harness-task-cycle-") as raw_tmp:
        sandbox = Path(raw_tmp)
        workspace, learning_root = build_cycle(sandbox)
        command = [
            sys.executable,
            "tools/validate_task_artifacts.py",
            "--workspace",
            str(workspace),
            "--learning-root",
            str(learning_root),
            "--require-learning",
        ]
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr)
        if completed.returncode != 0:
            print(f"task_cycle_smoke_fail exit={completed.returncode}")
            return completed.returncode

    print(f"task_cycle_smoke_ok task_id={TASK_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
