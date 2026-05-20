#!/usr/bin/env python3
"""Create a platform-independent ADLC plan directory for a task."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


VALID_TASK_TYPES = {"feature", "bugfix", "unit-test", "remediation", "orchestration"}


@dataclass
class PlanResult:
    run_id: str
    plan_dir: Path
    written: list[str]
    skipped: list[str]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "adlc-task"


def ensure_adlc(repo_path: Path, *, dry_run: bool) -> None:
    if dry_run:
        return
    (repo_path / ".adlc" / "plans").mkdir(parents=True, exist_ok=True)


def write_if_needed(path: Path, content: str, *, force: bool, dry_run: bool, written: list[str], skipped: list[str], root: Path) -> None:
    rel = str(path.relative_to(root))
    if path.exists() and not force:
        skipped.append(rel)
        return
    written.append(rel)
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_plan(
    repo_path: Path,
    *,
    task_type: str,
    title: str,
    source_report: str,
    force: bool,
    dry_run: bool,
) -> PlanResult:
    ensure_adlc(repo_path, dry_run=dry_run)
    now = datetime.now(timezone.utc)
    base_run_id = f"{now.strftime('%Y-%m-%d')}_{slugify(title)}"
    run_id = base_run_id
    if not dry_run and not force:
        suffix = 2
        while (repo_path / ".adlc" / "plans" / run_id).exists():
            run_id = f"{base_run_id}-{suffix}"
            suffix += 1
    plan_dir = repo_path / ".adlc" / "plans" / run_id
    written: list[str] = []
    skipped: list[str] = []

    source_report_text = source_report or ""
    plan_md = f"""# ADLC Plan: {title}

## Summary

- Task type: `{task_type}`
- Created at: {now.isoformat()}
- Source report: {source_report_text or "none"}

## Intent

Describe the requested outcome, user impact, and acceptance criteria.

## Current State

Record the current repository state, relevant files, existing harnesses, and baseline evidence.

## Proposed Approach

Describe the implementation or remediation approach before changing code.

## Verification Gates

See `tests-and-evals.md`.

## Work Items

See `work-items.md`.

## Proof Requirements

- Focused validation output
- Relevant standards or security report
- Summary of residual risk
"""

    plan_yaml = f"""schema_version: 0.1.0
run_id: {json.dumps(run_id)}
title: {json.dumps(title)}
task_type: {json.dumps(task_type)}
created_at: {json.dumps(now.isoformat())}
source_report: {json.dumps(source_report_text)}
lifecycle_phase: Plan
status: draft
verification:
  tests: []
  evals: []
  standards_checks: []
  proof_required: true
"""

    tests_md = f"""# Tests And Evals: {title}

## Baseline

- [ ] Record current revision.
- [ ] Run the narrowest relevant existing test or standards check.
- [ ] Capture baseline output.

## Required Tests

- [ ] Add task-specific tests here.

## Required Evals

- [ ] Add behavioral, security, or manual evals here.

## Standards Checks

- [ ] Run relevant ADLC standards profile.
- [ ] Run Project CodeGuard security profile when remediation touches security.

## Completion Evidence

- [ ] Focused test output captured.
- [ ] Standards or security report captured.
- [ ] Residual risks recorded.
"""

    work_items_md = f"""# Work Items: {title}

- [ ] W1: Complete plan review and acceptance criteria.
- [ ] W2: Establish baseline or failing signal.
- [ ] W3: Implement the first bounded change.
- [ ] W4: Run verification gates.
- [ ] W5: Write proof and update ADLC lifecycle.
"""

    state = {
        "schema_version": "0.1.0",
        "run_id": run_id,
        "title": title,
        "task_type": task_type,
        "source_report": source_report_text,
        "created_at": now.isoformat(),
        "current_phase": "Plan",
        "status": "draft",
        "artifacts": {
            "plan": "plan.md",
            "plan_yaml": "plan.yaml",
            "tests_and_evals": "tests-and-evals.md",
            "work_items": "work-items.md",
        },
    }

    files = {
        "plan.md": plan_md,
        "plan.yaml": plan_yaml,
        "tests-and-evals.md": tests_md,
        "work-items.md": work_items_md,
        "state.json": json.dumps(state, indent=2) + "\n",
    }

    for filename, content in files.items():
        write_if_needed(plan_dir / filename, content, force=force, dry_run=dry_run, written=written, skipped=skipped, root=repo_path)

    return PlanResult(run_id=run_id, plan_dir=plan_dir, written=written, skipped=skipped)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-path", default=".", help="Target repository path.")
    parser.add_argument("--task-type", default="feature", choices=sorted(VALID_TASK_TYPES), help="ADLC task type.")
    parser.add_argument("--title", required=True, help="Human-readable task title.")
    parser.add_argument("--source-report", default="", help="Optional source report path, such as reports/project-codeguard-security.json.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing plan run directory.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned files without writing.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary.")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).expanduser().resolve()
    if not repo_path.exists():
        parser.error(f"repo path does not exist: {repo_path}")
    if not repo_path.is_dir():
        parser.error(f"repo path is not a directory: {repo_path}")

    result = create_plan(
        repo_path,
        task_type=args.task_type,
        title=args.title,
        source_report=args.source_report,
        force=args.force,
        dry_run=args.dry_run,
    )
    payload = {
        "repo_path": str(repo_path),
        "run_id": result.run_id,
        "plan_dir": str(result.plan_dir),
        "dry_run": args.dry_run,
        "force": args.force,
        "written": result.written,
        "skipped": result.skipped,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        verb = "Would write" if args.dry_run else "Wrote"
        print(f"{verb} ADLC plan {result.run_id} in {result.plan_dir}")
        if result.skipped:
            print(f"Skipped {len(result.skipped)} existing files; use --force to overwrite.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
