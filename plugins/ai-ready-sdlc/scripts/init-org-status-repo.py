#!/usr/bin/env python3
"""Initialize the ADLC org status collection repository layout."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class InitResult:
    written: list[str]
    skipped: list[str]


def write_file(path: Path, content: str, *, force: bool, dry_run: bool, root: Path, result: InitResult) -> None:
    rel = str(path.relative_to(root))
    if path.exists() and not force:
        result.skipped.append(rel)
        return
    result.written.append(rel)
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def init_layout(repo_path: Path, *, org: str, force: bool, dry_run: bool) -> InitResult:
    generated_at = datetime.now(timezone.utc).isoformat()
    result = InitResult(written=[], skipped=[])

    files = {
        "README.md": f"""# ADLC Org Status

Generated: {generated_at}

This repository collects ADLC standards reports, harness status, proof artifacts, and org-level metrics.

Primary directories:

- `inventory/`: rollout scope and ownership metadata
- `repos/`: per-org and per-repo latest snapshots and historical runs
- `metrics/`: generated org metrics
- `dashboards/`: curated markdown dashboards
- `plans/`: remediation, tool installation, and harness rollout plans
""",
        "inventory/repos.yaml": f"""generated_at: "{generated_at}"
orgs:
  - name: {org}
    repositories: []
""",
        "inventory/owners.yaml": f"""generated_at: "{generated_at}"
owners: []
""",
        "metrics/.gitkeep": "",
        "dashboards/coverage.md": "# Coverage Dashboard\n\nGenerated metrics will populate this dashboard.\n",
        "dashboards/security.md": "# Security Dashboard\n\nGenerated metrics will populate this dashboard.\n",
        "dashboards/complexity.md": "# Complexity Dashboard\n\nGenerated metrics will populate this dashboard.\n",
        "dashboards/maintainability.md": "# Maintainability Dashboard\n\nGenerated metrics will populate this dashboard.\n",
        "dashboards/quick-wins.md": "# Quick Wins Dashboard\n\nGenerated metrics will populate this dashboard.\n",
        "plans/remediation-plan.md": "# Remediation Plan\n\nUse org metrics to prioritize repo remediation.\n",
        "plans/tool-installation-plan.md": "# Tool Installation Plan\n\nUse tool gap metrics to plan standard tool rollout.\n",
        "plans/harness-rollout-plan.md": "# Harness Rollout Plan\n\nTrack default ADLC harness adoption by repository.\n",
    }

    for rel_path, content in files.items():
        write_file(repo_path / rel_path, content, force=force, dry_run=dry_run, root=repo_path, result=result)

    if not dry_run:
        (repo_path / "repos" / org).mkdir(parents=True, exist_ok=True)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-path", default=".", help="Collection repo path to initialize.")
    parser.add_argument("--org", default="example-org", help="Initial organization name for inventory and repos directory.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing starter files.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned files without writing.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary.")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).expanduser().resolve()
    if not args.dry_run:
        repo_path.mkdir(parents=True, exist_ok=True)

    result = init_layout(repo_path, org=args.org, force=args.force, dry_run=args.dry_run)
    payload = {
        "repo_path": str(repo_path),
        "org": args.org,
        "dry_run": args.dry_run,
        "force": args.force,
        "written": result.written,
        "skipped": result.skipped,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        verb = "Would write" if args.dry_run else "Wrote"
        print(f"{verb} {len(result.written)} ADLC org status files in {repo_path}")
        if result.skipped:
            print(f"Skipped {len(result.skipped)} existing files; use --force to overwrite.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
