#!/usr/bin/env python3
"""Continue an ADLC plan with a scoped org standards remediation slice."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "unknown": 4}


@dataclass(frozen=True)
class Recommendation:
    priority: str
    action: str
    area: str
    owner_hint: str
    source: str


def load_script_module(filename: str, module_name: str) -> ModuleType:
    path = SCRIPT_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load script module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_report(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"source report not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"source report is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"source report must be a JSON object: {path}")
    return payload


def normalize_priority(value: Any) -> str:
    priority = str(value or "unknown").strip().lower()
    return priority if priority else "unknown"


def recommendation_from_item(item: dict[str, Any], *, area: str, source: str) -> Recommendation | None:
    action = str(item.get("action") or item.get("summary") or "").strip()
    if not action:
        return None
    return Recommendation(
        priority=normalize_priority(item.get("priority") or item.get("severity")),
        action=action,
        area=str(item.get("area") or area or "general").strip() or "general",
        owner_hint=str(item.get("owner_hint") or item.get("owner") or "repo owner or platform engineering").strip(),
        source=source,
    )


def collect_recommendations(report: dict[str, Any]) -> list[Recommendation]:
    recommendations: list[Recommendation] = []
    seen: set[tuple[str, str]] = set()

    def add(item: Recommendation | None) -> None:
        if item is None:
            return
        key = (item.priority, item.action)
        if key in seen:
            return
        seen.add(key)
        recommendations.append(item)

    areas = report.get("areas", {})
    if isinstance(areas, dict):
        for area_name, area_payload in sorted(areas.items()):
            if not isinstance(area_payload, dict):
                continue
            for item in area_payload.get("recommendations", []):
                if isinstance(item, dict):
                    add(recommendation_from_item(item, area=area_name, source=f"areas.{area_name}.recommendations"))

    for item in report.get("recommendations", []):
        if isinstance(item, dict):
            add(recommendation_from_item(item, area=str(item.get("area") or "general"), source="recommendations"))

    return sorted(recommendations, key=lambda item: (PRIORITY_ORDER.get(item.priority, 4), item.area, item.action))


def select_recommendations(
    recommendations: list[Recommendation],
    *,
    priority: str,
    area: str,
    max_items: int,
) -> tuple[list[Recommendation], list[Recommendation]]:
    scoped = recommendations
    priority = priority.lower()
    if priority != "any":
        scoped = [item for item in scoped if item.priority == priority]
    if area:
        scoped = [item for item in scoped if item.area == area]
    selected = scoped[:max_items]
    selected_keys = {(item.priority, item.action) for item in selected}
    out_of_scope = [item for item in recommendations if (item.priority, item.action) not in selected_keys]
    return selected, out_of_scope


def bullet_recommendations(items: list[Recommendation], *, checked: bool) -> str:
    if not items:
        return "- None for this slice.\n"
    marker = " " if checked else " "
    lines = []
    for index, item in enumerate(items, start=1):
        lines.append(
            f"- [{' ' if marker == ' ' else marker}] R{index}: [{item.priority}] {item.area}: {item.action} "
            f"(owner: {item.owner_hint}; source: {item.source})"
        )
    return "\n".join(lines) + "\n"


def table_recommendations(items: list[Recommendation]) -> str:
    if not items:
        return "| Priority | Area | Action | Owner | Source |\n| --- | --- | --- | --- | --- |\n| none | none | none for this slice | none | none |\n"
    lines = ["| Priority | Area | Action | Owner | Source |", "| --- | --- | --- | --- | --- |"]
    for item in items:
        action = item.action.replace("|", "\\|")
        owner = item.owner_hint.replace("|", "\\|")
        lines.append(f"| {item.priority} | {item.area} | {action} | {owner} | {item.source} |")
    return "\n".join(lines) + "\n"


def relative_path(path: Path, root: Path) -> str:
    return str(path.relative_to(root) if path.is_relative_to(root) else path)


def get_active_plan_dir(repo_path: Path) -> Path | None:
    lifecycle_path = repo_path / ".adlc" / "lifecycle.json"
    if not lifecycle_path.exists():
        return None
    try:
        lifecycle = json.loads(lifecycle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    active_plan = str(lifecycle.get("active_plan") or "").strip()
    if not active_plan:
        return None
    plan_dir = Path(active_plan)
    if not plan_dir.is_absolute():
        plan_dir = repo_path / plan_dir
    return plan_dir if plan_dir.exists() and plan_dir.is_dir() else None


def write_plan_details(
    plan_dir: Path,
    *,
    title: str,
    source_report: str,
    priority: str,
    area: str,
    max_items: int,
    selected: list[Recommendation],
    out_of_scope: list[Recommendation],
    report: dict[str, Any],
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    repo = str(report.get("repository") or "unknown")
    revision = str(report.get("revision") or "unknown")
    overall = str(report.get("overall_status") or "unknown")
    scope = f"priority={priority}, area={area or 'any'}, max_items={max_items}"

    plan_md = f"""# ADLC Plan: {title}

## Summary

- Task type: `remediation`
- Created at: {now}
- Source report: {source_report}
- Repository: {repo}
- Revision: {revision}
- Overall status: {overall}
- Scope: {scope}
- Mode: plan only; do not edit code until this plan is approved.

## Intent

Create a bounded remediation plan from `reports/org-standards.json` without attempting to fix every standards recommendation in one run.

## Selected Recommendations

{table_recommendations(selected)}
## Out Of Scope For This Run

{table_recommendations(out_of_scope)}
## Proposed Approach

1. Confirm the selected recommendations are the intended slice.
2. For each selected item, identify the smallest repository change or environment action that would address it.
3. Add or update tests, evals, standards checks, or proof evidence before implementation.
4. Implement only approved selected work items.
5. Rerun targeted checks and `run-org-standards` after changes.

## Verification Gates

See `tests-and-evals.md`.

## Work Items

See `work-items.md`.

## Proof Requirements

- Updated `reports/org-standards.json` or focused lane report after remediation.
- Focused test or tool output for each selected work item.
- `.adlc/proofs/` notes explaining what changed and residual risk.
"""

    plan_yaml = {
        "schema_version": "0.1.0",
        "title": title,
        "task_type": "remediation",
        "source_report": source_report,
        "lifecycle_phase": "Plan",
        "status": "draft",
        "scope": {
            "priority": priority,
            "area": area or "any",
            "max_items": max_items,
            "mode": "plan_only",
        },
        "selected_recommendations": [item.__dict__ for item in selected],
        "out_of_scope_recommendations": [item.__dict__ for item in out_of_scope],
        "verification": {
            "tests": ["focused tests for approved selected work items"],
            "evals": ["manual review of selected recommendation closure"],
            "standards_checks": ["run-org-standards after implementation"],
            "proof_required": True,
        },
    }

    tests_md = f"""# Tests And Evals: {title}

## Baseline

- [ ] Record current revision `{revision}`.
- [ ] Confirm source report exists: `{source_report}`.
- [ ] Review selected recommendations in `plan.md`.

## Required Tests

- [ ] For each approved selected item, run the narrowest relevant test or tool.
- [ ] If the selected item is tool availability, verify the tool command is available or document platform ownership.
- [ ] If the selected item changes repo files, run existing focused tests before and after the change.

## Required Evals

- [ ] Confirm only selected work items are in scope.
- [ ] Confirm out-of-scope recommendations remain untouched.
- [ ] Review generated proof notes before publishing a follow-up snapshot.

## Standards Checks

- [ ] Rerun `run-org-standards` after approved remediation.
- [ ] Compare before and after `reports/org-standards.json`.

## Completion Evidence

- [ ] Focused test or tool output captured.
- [ ] Updated standards report captured.
- [ ] Residual risk recorded under `.adlc/proofs/`.
"""

    if selected:
        work_lines = []
        for index, item in enumerate(selected, start=1):
            work_lines.append(f"- [ ] W{index}: [{item.priority}] {item.area}: {item.action}")
        next_index = len(selected) + 1
    else:
        work_lines = ["- [ ] W1: Confirm no recommendations matched this requested scope and choose a different priority or area."]
        next_index = 2
    work_lines.extend(
        [
            f"- [ ] W{next_index}: Run focused verification for approved selected items.",
            f"- [ ] W{next_index + 1}: Rerun `run-org-standards` and update proof artifacts.",
            f"- [ ] W{next_index + 2}: Record out-of-scope recommendations that remain for later slices.",
        ]
    )
    work_items_md = f"""# Work Items: {title}

{chr(10).join(work_lines)}

## Explicitly Out Of Scope

{bullet_recommendations(out_of_scope, checked=False)}
"""

    state = {
        "schema_version": "0.1.0",
        "title": title,
        "task_type": "remediation",
        "source_report": source_report,
        "current_phase": "Plan",
        "status": "draft",
        "scope": {
            "priority": priority,
            "area": area or "any",
            "max_items": max_items,
            "mode": "plan_only",
        },
        "selected_count": len(selected),
        "out_of_scope_count": len(out_of_scope),
        "artifacts": {
            "plan": "plan.md",
            "plan_yaml": "plan.yaml",
            "tests_and_evals": "tests-and-evals.md",
            "work_items": "work-items.md",
        },
    }

    (plan_dir / "plan.md").write_text(plan_md, encoding="utf-8")
    (plan_dir / "plan.yaml").write_text(json.dumps(plan_yaml, indent=2) + "\n", encoding="utf-8")
    (plan_dir / "tests-and-evals.md").write_text(tests_md, encoding="utf-8")
    (plan_dir / "work-items.md").write_text(work_items_md, encoding="utf-8")
    (plan_dir / "state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def append_once(path: Path, marker: str, content: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker in existing:
        return
    separator = "\n" if existing.endswith("\n") or not existing else "\n\n"
    path.write_text(existing + separator + content, encoding="utf-8")


def write_active_plan_slice(
    plan_dir: Path,
    *,
    title: str,
    source_report: str,
    priority: str,
    area: str,
    max_items: int,
    selected: list[Recommendation],
    out_of_scope: list[Recommendation],
    report: dict[str, Any],
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    repo = str(report.get("repository") or "unknown")
    revision = str(report.get("revision") or "unknown")
    overall = str(report.get("overall_status") or "unknown")
    scope = {
        "priority": priority,
        "area": area or "any",
        "max_items": max_items,
        "mode": "continue_active_plan",
    }
    slice_payload = {
        "schema_version": "0.1.0",
        "title": title,
        "created_at": now,
        "source_report": source_report,
        "repository": repo,
        "revision": revision,
        "overall_status": overall,
        "scope": scope,
        "selected_recommendations": [item.__dict__ for item in selected],
        "out_of_scope_recommendations": [item.__dict__ for item in out_of_scope],
        "next_steps": [
            "review selected recommendations",
            "implement only approved selected work items",
            "rerun org standards after implementation",
            "publish snapshot only after review approval",
        ],
    }
    (plan_dir / "org-standards-remediation-slice.json").write_text(json.dumps(slice_payload, indent=2) + "\n", encoding="utf-8")

    slice_md = f"""# Org Standards Remediation Slice

This slice continues the active orchestration plan. It does not create a new top-level plan.

- Created at: {now}
- Source report: `{source_report}`
- Repository: `{repo}`
- Revision: `{revision}`
- Current standards status: `{overall}`
- Scope: priority={priority}, area={area or 'any'}, max_items={max_items}

## Selected Recommendations

{table_recommendations(selected)}
## Out Of Scope For This Slice

{table_recommendations(out_of_scope)}
## Next Steps

1. Review and approve the selected slice.
2. Implement only approved selected work items.
3. Rerun org standards after implementation.
4. Publish the repository snapshot only after the rerun and review are complete.
"""
    (plan_dir / "org-standards-remediation-slice.md").write_text(slice_md, encoding="utf-8")

    state_path = plan_dir / "state.json"
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            state = {}
    else:
        state = {}
    state.update(
        {
            "current_phase": "Plan",
            "status": "remediation_slice_ready",
            "updated_at": now,
            "org_standards_remediation_slice": {
                "source_report": source_report,
                "priority": priority,
                "area": area or "any",
                "max_items": max_items,
                "selected_count": len(selected),
                "out_of_scope_count": len(out_of_scope),
                "artifacts": {
                    "markdown": "org-standards-remediation-slice.md",
                    "json": "org-standards-remediation-slice.json",
                },
                "implementation_gate": "human_approval_required",
                "rerun_required": "run-org-standards",
            },
        }
    )
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    marker = "<!-- org-standards-remediation-slice -->"
    selected_lines = []
    if selected:
        for index, item in enumerate(selected, start=1):
            selected_lines.append(f"- [ ] RS{index}: [{item.priority}] {item.area}: {item.action}")
    else:
        selected_lines.append("- [ ] RS1: No matching recommendations found; choose a different scope.")
    append_once(
        plan_dir / "work-items.md",
        marker,
        f"""{marker}

## Org Standards Remediation Slice

{chr(10).join(selected_lines)}
- [ ] Rerun org standards after approved remediation work.
- [ ] Review the updated standards result before publishing the snapshot.
""",
    )
    append_once(
        plan_dir / "tests-and-evals.md",
        marker,
        f"""{marker}

## Org Standards Remediation Slice

- [ ] Review selected recommendations in `org-standards-remediation-slice.md`.
- [ ] Run focused verification for approved remediation work.
- [ ] Rerun `run-org-standards` after implementation.
- [ ] Confirm the updated standards evidence is ready before publishing.
""",
    )


def update_active_plan_lifecycle(
    repo_path: Path,
    *,
    plan_dir: Path,
    title: str,
    source_report: str,
    platform: str,
    detected: dict[str, list[str]],
) -> None:
    lifecycle_path = repo_path / ".adlc" / "lifecycle.json"
    try:
        lifecycle = json.loads(lifecycle_path.read_text(encoding="utf-8")) if lifecycle_path.exists() else {}
    except json.JSONDecodeError:
        lifecycle = {}
    now = datetime.now(timezone.utc).isoformat()
    rel_plan = relative_path(plan_dir, repo_path)
    history = lifecycle.setdefault("history", [])
    history.append(
        {
            "phase": "Plan",
            "status": "remediation_slice_ready",
            "at": now,
            "platform": platform,
            "task_type": lifecycle.get("active_task_type") or "orchestration",
            "action": "org_standards_remediation_slice",
            "title": title,
            "source_report": source_report,
            "plan": rel_plan,
            "summary": "Selected a bounded org standards remediation slice inside the active ADLC plan. Implementation waits for human approval.",
        }
    )
    lifecycle.update(
        {
            "schema_version": lifecycle.get("schema_version", "0.1.0"),
            "repository": lifecycle.get("repository", repo_path.name),
            "distribution_model": "plugin-first",
            "current_phase": "Plan",
            "active_plan": rel_plan,
            "active_source_report": source_report,
            "active_platform": platform,
            "detected_local_harnesses": detected,
            "active_remediation_slice": relative_path(plan_dir / "org-standards-remediation-slice.md", repo_path),
            "updated_at": now,
        }
    )
    lifecycle_path.parent.mkdir(parents=True, exist_ok=True)
    lifecycle_path.write_text(json.dumps(lifecycle, indent=2) + "\n", encoding="utf-8")


def append_active_slice_status(repo_path: Path, *, plan_dir: Path, title: str, source_report: str, platform: str) -> None:
    status_path = repo_path / ".adlc" / "status.md"
    now = datetime.now(timezone.utc).isoformat()
    rel_plan = relative_path(plan_dir, repo_path)
    section = f"""

## Org Standards Remediation Slice

- Updated: {now}
- Platform: `{platform}`
- Title: {title}
- Active plan: `{rel_plan}`
- Source report: `{source_report}`
- Slice artifacts: `{relative_path(plan_dir / "org-standards-remediation-slice.md", repo_path)}`, `{relative_path(plan_dir / "org-standards-remediation-slice.json", repo_path)}`
- Status: selected slice is ready for review; implementation should wait for human approval, then rerun `run-org-standards` before publishing.
"""
    status_path.parent.mkdir(parents=True, exist_ok=True)
    if status_path.exists():
        existing = status_path.read_text(encoding="utf-8").rstrip()
        status_path.write_text(existing + section + "\n", encoding="utf-8")
    else:
        status_path.write_text("# ADLC Harness Status\n" + section + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-path", default=".", help="Target repository path.")
    parser.add_argument("--source-report", default="reports/org-standards.json", help="Org standards report path, relative to repo unless absolute.")
    parser.add_argument("--priority", default="low", choices=("critical", "high", "medium", "low", "any"), help="Recommendation priority slice.")
    parser.add_argument("--area", default="", help="Optional area slice, such as code_quality or requirements_to_tests.")
    parser.add_argument("--max-items", type=int, default=3, help="Maximum selected recommendations for this plan.")
    parser.add_argument("--title", default="Org standards remediation - low priority slice", help="Plan title.")
    parser.add_argument("--platform", default="auto", choices=("auto", "claude", "codex", "augment"), help="Calling platform.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing plan run directory.")
    parser.add_argument("--new-plan", action="store_true", help="Create a separate remediation plan even when an active plan exists.")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable summary.")
    args = parser.parse_args()

    if args.max_items < 1:
        parser.error("--max-items must be at least 1")

    repo_path = Path(args.repo_path).expanduser().resolve()
    if not repo_path.exists() or not repo_path.is_dir():
        parser.error(f"repo path is not a directory: {repo_path}")
    report_path = Path(args.source_report)
    if not report_path.is_absolute():
        report_path = repo_path / report_path
    report = load_report(report_path)

    recommendations = collect_recommendations(report)
    selected, out_of_scope = select_recommendations(
        recommendations,
        priority=args.priority,
        area=args.area,
        max_items=args.max_items,
    )

    steer_module = load_script_module("steer-adlc-harness.py", "adlc_steer_harness")
    harness_module = load_script_module("create-adlc-harness.py", "adlc_create_harness")
    plan_module = load_script_module("create-adlc-plan.py", "adlc_create_plan")

    platform = steer_module.detect_platform(args.platform)
    steer_module.ensure_harness(repo_path, harness_module, dry_run=False)
    detected = harness_module.detect_local_harnesses(repo_path)
    steer_module.update_harness_yaml(repo_path / ".adlc" / "harness.yaml", detected, harness_module, dry_run=False)
    relative_source_report = relative_path(report_path, repo_path)
    active_plan_dir = None if args.new_plan else get_active_plan_dir(repo_path)
    if active_plan_dir:
        plan_result = SimpleNamespace(plan_dir=active_plan_dir, run_id=active_plan_dir.name)
        write_active_plan_slice(
            plan_result.plan_dir,
            title=args.title,
            source_report=relative_source_report,
            priority=args.priority,
            area=args.area,
            max_items=args.max_items,
            selected=selected,
            out_of_scope=out_of_scope,
            report=report,
        )
        write_mode = "continued_active_plan"
        update_active_plan_lifecycle(
            repo_path,
            plan_dir=plan_result.plan_dir,
            title=args.title,
            source_report=relative_source_report,
            platform=platform,
            detected=detected,
        )
        append_active_slice_status(
            repo_path,
            plan_dir=plan_result.plan_dir,
            title=args.title,
            source_report=relative_source_report,
            platform=platform,
        )
    else:
        plan_result = plan_module.create_plan(
            repo_path,
            task_type="remediation",
            title=args.title,
            source_report=relative_source_report,
            force=args.force,
            dry_run=False,
        )
        write_plan_details(
            plan_result.plan_dir,
            title=args.title,
            source_report=relative_source_report,
            priority=args.priority,
            area=args.area,
            max_items=args.max_items,
            selected=selected,
            out_of_scope=out_of_scope,
            report=report,
        )
        write_mode = "created_new_plan"
        steer_module.update_lifecycle(
            repo_path,
            plan_dir=plan_result.plan_dir,
            task_type="remediation",
            title=args.title,
            source_report=relative_source_report,
            platform=platform,
            detected=detected,
            dry_run=False,
        )
        steer_module.append_status(
            repo_path,
            plan_dir=plan_result.plan_dir,
            task_type="remediation",
            title=args.title,
            source_report=relative_source_report,
            platform=platform,
            dry_run=False,
        )

    payload = {
        "repo_path": str(repo_path),
        "source_report": relative_source_report,
        "plan_dir": str(plan_result.plan_dir),
        "run_id": plan_result.run_id,
        "write_mode": write_mode,
        "priority": args.priority,
        "area": args.area or "any",
        "max_items": args.max_items,
        "selected_count": len(selected),
        "out_of_scope_count": len(out_of_scope),
        "selected_recommendations": [item.__dict__ for item in selected],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        if write_mode == "continued_active_plan":
            print(f"Updated active plan with scoped org standards remediation slice: {plan_result.plan_dir}")
        else:
            print(f"Wrote scoped org standards remediation plan: {plan_result.plan_dir}")
        print(f"Selected {len(selected)} recommendation(s); left {len(out_of_scope)} out of scope.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
