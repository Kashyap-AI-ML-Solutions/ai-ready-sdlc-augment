#!/usr/bin/env python3
"""Create an ADLC plan and advance shared lifecycle state for a task."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType


SCRIPT_DIR = Path(__file__).resolve().parent
VALID_TASK_TYPES = ("feature", "bugfix", "unit-test", "remediation", "orchestration")
PHASES = [
    "Discover",
    "Scaffold",
    "Refresh",
    "Blueprint",
    "Plan",
    "Execute",
    "Verify",
    "Repair",
    "Prove",
    "Report",
]


def load_script_module(filename: str, module_name: str) -> ModuleType:
    path = SCRIPT_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load script module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def repo_relative(repo_path: Path, path: Path) -> str:
    return str(path.relative_to(repo_path))


def detect_platform(explicit: str) -> str:
    if explicit != "auto":
        return explicit
    if os.environ.get("AUGMENT_PLUGIN_ROOT"):
        return "augment"
    if os.environ.get("CODEX_HOME"):
        return "codex"
    if os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE_ENTRYPOINT"):
        return "claude"
    return "unknown"


def load_lifecycle(path: Path, repo_name: str, detected: dict[str, list[str]]) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    now = datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": "0.1.0",
        "generated_by": "steer-adlc-harness",
        "generated_at": now,
        "repository": repo_name,
        "distribution_model": "plugin-first",
        "current_phase": "Discover",
        "phases": PHASES,
        "active_plan": None,
        "detected_local_harnesses": detected,
        "history": [],
    }


def update_harness_yaml(path: Path, detected: dict[str, list[str]], harness_module: ModuleType, *, dry_run: bool) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    block = "detected_local_harnesses:\n" + harness_module.detected_harnesses_yaml(detected) + "\n\n"
    pattern = r"(?ms)^detected_local_harnesses:\n.*?(?=^profiles:)"
    if re.search(pattern, text):
        updated = re.sub(pattern, block, text)
    else:
        updated = text.rstrip() + "\n\n" + block
    if updated == text:
        return False
    if not dry_run:
        path.write_text(updated, encoding="utf-8")
    return True


def update_lifecycle(
    repo_path: Path,
    *,
    plan_dir: Path,
    task_type: str,
    title: str,
    source_report: str,
    platform: str,
    detected: dict[str, list[str]],
    dry_run: bool,
) -> bool:
    lifecycle_path = repo_path / ".adlc" / "lifecycle.json"
    lifecycle = load_lifecycle(lifecycle_path, repo_path.name, detected)
    now = datetime.now(timezone.utc).isoformat()
    rel_plan = repo_relative(repo_path, plan_dir)
    history = lifecycle.setdefault("history", [])
    history.append(
        {
            "phase": "Plan",
            "status": "draft",
            "at": now,
            "platform": platform,
            "task_type": task_type,
            "title": title,
            "source_report": source_report or None,
            "plan": rel_plan,
            "summary": f"Created ADLC {task_type} plan for {title}.",
        }
    )
    lifecycle.update(
        {
            "schema_version": lifecycle.get("schema_version", "0.1.0"),
            "repository": lifecycle.get("repository", repo_path.name),
            "distribution_model": "plugin-first",
            "current_phase": "Plan",
            "phases": lifecycle.get("phases", PHASES),
            "active_plan": rel_plan,
            "active_task_type": task_type,
            "active_title": title,
            "active_source_report": source_report or None,
            "active_platform": platform,
            "detected_local_harnesses": detected,
            "updated_at": now,
        }
    )
    if dry_run:
        return True
    lifecycle_path.parent.mkdir(parents=True, exist_ok=True)
    lifecycle_path.write_text(json.dumps(lifecycle, indent=2) + "\n", encoding="utf-8")
    return True


def append_status(
    repo_path: Path,
    *,
    plan_dir: Path,
    task_type: str,
    title: str,
    source_report: str,
    platform: str,
    dry_run: bool,
) -> bool:
    status_path = repo_path / ".adlc" / "status.md"
    now = datetime.now(timezone.utc).isoformat()
    rel_plan = repo_relative(repo_path, plan_dir)
    section = f"""

## Active ADLC Plan

- Updated: {now}
- Platform: `{platform}`
- Task type: `{task_type}`
- Title: {title}
- Active plan: `{rel_plan}`
- Source report: `{source_report or "none"}`
- Lifecycle phase: `Plan`
- Status: draft; implementation should wait until `tests-and-evals.md` and `work-items.md` are reviewed.
"""
    if dry_run:
        return True
    status_path.parent.mkdir(parents=True, exist_ok=True)
    if status_path.exists():
        existing = status_path.read_text(encoding="utf-8").rstrip()
        status_path.write_text(existing + section + "\n", encoding="utf-8")
    else:
        status_path.write_text("# ADLC Harness Status\n" + section + "\n", encoding="utf-8")
    return True


def ensure_harness(
    repo_path: Path,
    harness_module: ModuleType,
    *,
    dry_run: bool,
) -> tuple[bool, dict]:
    harness_path = repo_path / ".adlc" / "harness.yaml"
    if harness_path.exists():
        return False, {"written": [], "skipped": []}
    result = harness_module.copy_harness(
        repo_path,
        force=False,
        dry_run=dry_run,
        include_workflow=False,
        local_overrides=[],
    )
    return True, {
        "written": result.written,
        "skipped": result.skipped,
        "detected_local_harnesses": result.detected_local_harnesses,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-path", default=".", help="Target repository path.")
    parser.add_argument("--task-type", required=True, choices=VALID_TASK_TYPES, help="ADLC task type.")
    parser.add_argument("--title", required=True, help="Human-readable task title.")
    parser.add_argument("--source-report", default="", help="Optional source report path.")
    parser.add_argument("--platform", default="auto", choices=("auto", "claude", "codex", "augment"), help="Calling platform.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing plan run directory.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned lifecycle changes without writing.")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable summary.")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).expanduser().resolve()
    if not repo_path.exists():
        parser.error(f"repo path does not exist: {repo_path}")
    if not repo_path.is_dir():
        parser.error(f"repo path is not a directory: {repo_path}")

    harness_module = load_script_module("create-adlc-harness.py", "adlc_create_harness")
    plan_module = load_script_module("create-adlc-plan.py", "adlc_create_plan")
    platform = detect_platform(args.platform)

    harness_initialized, scaffold_summary = ensure_harness(repo_path, harness_module, dry_run=args.dry_run)
    detected = harness_module.detect_local_harnesses(repo_path)
    harness_yaml_updated = update_harness_yaml(repo_path / ".adlc" / "harness.yaml", detected, harness_module, dry_run=args.dry_run)

    plan_result = plan_module.create_plan(
        repo_path,
        task_type=args.task_type,
        title=args.title,
        source_report=args.source_report,
        force=args.force,
        dry_run=args.dry_run,
    )

    lifecycle_updated = update_lifecycle(
        repo_path,
        plan_dir=plan_result.plan_dir,
        task_type=args.task_type,
        title=args.title,
        source_report=args.source_report,
        platform=platform,
        detected=detected,
        dry_run=args.dry_run,
    )
    status_updated = append_status(
        repo_path,
        plan_dir=plan_result.plan_dir,
        task_type=args.task_type,
        title=args.title,
        source_report=args.source_report,
        platform=platform,
        dry_run=args.dry_run,
    )

    payload = {
        "repo_path": str(repo_path),
        "dry_run": args.dry_run,
        "platform": platform,
        "task_type": args.task_type,
        "title": args.title,
        "source_report": args.source_report,
        "harness_initialized": harness_initialized,
        "scaffold": scaffold_summary,
        "harness_yaml_updated": harness_yaml_updated,
        "run_id": plan_result.run_id,
        "plan_dir": str(plan_result.plan_dir),
        "written": plan_result.written,
        "skipped": plan_result.skipped,
        "lifecycle_updated": lifecycle_updated,
        "status_updated": status_updated,
        "detected_local_harnesses": detected,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        verb = "Would create" if args.dry_run else "Created"
        print(f"{verb} ADLC {args.task_type} plan {plan_result.run_id}")
        print(f"Plan directory: {plan_result.plan_dir}")
        if harness_initialized:
            print("Initialized shared .adlc harness state first.")
        if plan_result.skipped:
            print(f"Skipped {len(plan_result.skipped)} existing plan files; use --force to overwrite.")
        print("Lifecycle phase: Plan")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
