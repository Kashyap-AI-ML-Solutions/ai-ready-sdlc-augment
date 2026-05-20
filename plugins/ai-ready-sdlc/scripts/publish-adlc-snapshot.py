#!/usr/bin/env python3
"""Prepare a per-repository ADLC snapshot for the central org status repo."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_REPORTS = [
    "reports/org-standards.json",
    "reports/org-standards.md",
    "reports/code-quality.json",
    "reports/code-quality.md",
    "reports/project-codeguard-security.json",
    "reports/project-codeguard-security.md",
    "reports/ai-readiness.json",
    "reports/ai-readiness.md",
    "reports/bug-triage.json",
    "reports/bug-triage.md",
    "reports/requirements-to-tests.json",
    "reports/requirements-to-tests.md",
]

REQUIRED_ADLC = [
    ".adlc/harness.yaml",
    ".adlc/lifecycle.json",
    ".adlc/status.md",
]

PLAN_FILES = {
    "plan.md",
    "plan.yaml",
    "tests-and-evals.md",
    "work-items.md",
    "state.json",
}

OPTIONAL_EVIDENCE_NAMES = {
    "coverage.xml": "coverage",
    "lcov.info": "coverage",
    "junit.xml": "tests",
    "pytest-report.xml": "tests",
    "test-results.json": "tests",
}

IGNORE_PARTS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    "__pycache__",
}

MAX_OPTIONAL_EVIDENCE_BYTES = 2_000_000
SCHEMA_VERSION = "0.1.0"


@dataclass
class SnapshotFile:
    source_path: Path | None
    snapshot_path: str
    content: str
    required: bool


def run_git(repo_path: Path, args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_path,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError:
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def safe_run_id(value: str | None) -> str:
    if value:
        return value.replace("/", "-").replace(":", "-")
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def text_or_empty(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def relative_posix(path: Path) -> str:
    return path.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def active_plan_path(repo_path: Path) -> Path | None:
    lifecycle = load_json(repo_path / ".adlc" / "lifecycle.json")
    active = lifecycle.get("active_plan")
    if isinstance(active, str) and active:
        candidate = repo_path / active
        if candidate.is_dir():
            return candidate
    plans_dir = repo_path / ".adlc" / "plans"
    if not plans_dir.is_dir():
        return None
    candidates = [path for path in plans_dir.iterdir() if path.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def should_skip(path: Path) -> bool:
    return any(part in IGNORE_PARTS for part in path.parts)


def add_required_file(repo_path: Path, rel_path: str, files: list[SnapshotFile], missing: list[str]) -> None:
    source = repo_path / rel_path
    snapshot_path = rel_path[1:] if rel_path.startswith(".adlc/") else rel_path
    if not source.exists() or not source.is_file():
        missing.append(rel_path)
        return
    files.append(
        SnapshotFile(
            source_path=source,
            snapshot_path=snapshot_path,
            content=text_or_empty(source),
            required=True,
        )
    )


def add_active_plan(repo_path: Path, files: list[SnapshotFile]) -> str | None:
    plan_dir = active_plan_path(repo_path)
    if plan_dir is None:
        return None
    active_rel = relative_posix(plan_dir.relative_to(repo_path))
    for source in sorted(plan_dir.iterdir()):
        if source.is_file() and source.name in PLAN_FILES:
            files.append(
                SnapshotFile(
                    source_path=source,
                    snapshot_path=relative_posix(source.relative_to(repo_path))[1:]
                    if relative_posix(source.relative_to(repo_path)).startswith(".adlc/")
                    else relative_posix(source.relative_to(repo_path)),
                    content=text_or_empty(source),
                    required=False,
                )
            )
    return active_rel


def add_proofs(repo_path: Path, files: list[SnapshotFile]) -> None:
    proofs_dir = repo_path / ".adlc" / "proofs"
    if not proofs_dir.is_dir():
        return
    for source in sorted(proofs_dir.rglob("*")):
        if source.is_file() and not should_skip(source.relative_to(repo_path)):
            rel = relative_posix(source.relative_to(repo_path))
            files.append(
                SnapshotFile(
                    source_path=source,
                    snapshot_path=rel[1:] if rel.startswith(".adlc/") else rel,
                    content=text_or_empty(source),
                    required=False,
                )
            )


def add_optional_evidence(repo_path: Path, files: list[SnapshotFile]) -> None:
    for source in sorted(repo_path.rglob("*")):
        if not source.is_file():
            continue
        rel = source.relative_to(repo_path)
        if should_skip(rel):
            continue
        category = OPTIONAL_EVIDENCE_NAMES.get(source.name)
        if category is None:
            continue
        try:
            if source.stat().st_size > MAX_OPTIONAL_EVIDENCE_BYTES:
                continue
        except OSError:
            continue
        files.append(
            SnapshotFile(
                source_path=source,
                snapshot_path=f"evidence/{category}/{relative_posix(rel)}",
                content=text_or_empty(source),
                required=False,
            )
        )


def repo_name_from_remote(remote: str, repo_path: Path) -> str:
    if remote:
        name = remote.rstrip("/").rsplit("/", 1)[-1]
        if name.endswith(".git"):
            name = name[:-4]
        if name:
            return name
    return repo_path.name


def build_manifest(
    *,
    org: str,
    repo_name: str,
    repo_path: Path,
    run_id: str,
    active_plan: str | None,
    included: list[str],
    missing: list[str],
) -> dict[str, Any]:
    remote = run_git(repo_path, ["remote", "get-url", "origin"])
    branch = run_git(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])
    revision = run_git(repo_path, ["rev-parse", "HEAD"])
    status = run_git(repo_path, ["status", "--short"])
    return {
        "schema_version": SCHEMA_VERSION,
        "org": org,
        "repo": repo_name,
        "source_remote": remote,
        "source_branch": branch,
        "source_revision": revision,
        "source_worktree_dirty": bool(status),
        "run_id": run_id,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "publisher": "ai-ready-sdlc",
        "adlc_plugin_version": "0.1.0",
        "active_plan": active_plan,
        "reports_included": [path for path in included if path.startswith("reports/")],
        "adlc_included": [path for path in included if path.startswith("adlc/")],
        "evidence_included": [path for path in included if path.startswith("evidence/")],
        "missing_required": missing,
    }


def collect_snapshot(repo_path: Path, *, org: str, repo_name: str, run_id: str) -> tuple[list[SnapshotFile], dict[str, Any], list[str]]:
    files: list[SnapshotFile] = []
    missing: list[str] = []

    for rel_path in REQUIRED_REPORTS:
        add_required_file(repo_path, rel_path, files, missing)
    for rel_path in REQUIRED_ADLC:
        add_required_file(repo_path, rel_path, files, missing)

    active_plan = add_active_plan(repo_path, files)
    add_proofs(repo_path, files)
    add_optional_evidence(repo_path, files)

    included = sorted({item.snapshot_path for item in files})
    manifest = build_manifest(
        org=org,
        repo_name=repo_name,
        repo_path=repo_path,
        run_id=run_id,
        active_plan=active_plan,
        included=included,
        missing=missing,
    )
    files.insert(
        0,
        SnapshotFile(
            source_path=None,
            snapshot_path="manifest.json",
            content=json.dumps(manifest, indent=2) + "\n",
            required=True,
        ),
    )
    return files, manifest, missing


def central_paths(org: str, repo_name: str, run_id: str, snapshot_path: str) -> list[str]:
    base = f"repos/{org}/{repo_name}"
    return [
        f"{base}/runs/{run_id}/{snapshot_path}",
        f"{base}/latest/{snapshot_path}",
    ]


def stage_files(stage_dir: Path, org: str, repo_name: str, run_id: str, files: list[SnapshotFile]) -> list[str]:
    written: list[str] = []
    for item in files:
        for rel_path in central_paths(org, repo_name, run_id, item.snapshot_path):
            target = stage_dir / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(item.content, encoding="utf-8")
            written.append(rel_path)
    return written


def write_payload(
    payload_path: Path,
    *,
    owner: str,
    collection_repo: str,
    branch: str,
    org: str,
    repo_name: str,
    run_id: str,
    files: list[SnapshotFile],
) -> dict[str, Any]:
    payload_files = []
    for item in files:
        for rel_path in central_paths(org, repo_name, run_id, item.snapshot_path):
            payload_files.append({"path": rel_path, "content": item.content})
    payload = {
        "owner": owner,
        "repo": collection_repo,
        "branch": branch,
        "message": f"ADLC snapshot: {org}/{repo_name} {run_id}",
        "files": payload_files,
    }
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-path", default=".", help="Target repository whose ADLC evidence should be published.")
    parser.add_argument("--org", default="jasper-sw", help="Source GitHub organization name.")
    parser.add_argument("--repo-name", help="Source repository name; defaults to origin remote or directory name.")
    parser.add_argument("--collection-owner", default="jasper-sw", help="Central collection repository owner.")
    parser.add_argument("--collection-repo", default="adlc-org-status", help="Central collection repository name.")
    parser.add_argument("--collection-branch", default="main", help="Central collection branch.")
    parser.add_argument("--run-id", help="Snapshot run id; defaults to current UTC timestamp.")
    parser.add_argument("--stage-dir", help="Optional local directory to write central repo paths into.")
    parser.add_argument("--payload-output", help="Optional JSON file containing a cisco_github_server.push_files payload.")
    parser.add_argument("--strict", action="store_true", help="Fail if required reports or ADLC files are missing.")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable summary.")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).expanduser().resolve()
    if not repo_path.is_dir():
        parser.error(f"repo path is not a directory: {repo_path}")

    run_id = safe_run_id(args.run_id)
    remote = run_git(repo_path, ["remote", "get-url", "origin"])
    repo_name = args.repo_name or repo_name_from_remote(remote, repo_path)

    files, manifest, missing = collect_snapshot(repo_path, org=args.org, repo_name=repo_name, run_id=run_id)
    staged: list[str] = []
    if args.stage_dir:
        stage_dir = Path(args.stage_dir).expanduser().resolve()
        if stage_dir.exists():
            shutil.rmtree(stage_dir)
        staged = stage_files(stage_dir, args.org, repo_name, run_id, files)

    payload_summary: dict[str, Any] | None = None
    if args.payload_output:
        payload = write_payload(
            Path(args.payload_output).expanduser().resolve(),
            owner=args.collection_owner,
            collection_repo=args.collection_repo,
            branch=args.collection_branch,
            org=args.org,
            repo_name=repo_name,
            run_id=run_id,
            files=files,
        )
        payload_summary = {
            "path": str(Path(args.payload_output).expanduser().resolve()),
            "file_count": len(payload["files"]),
        }

    summary = {
        "repo_path": str(repo_path),
        "org": args.org,
        "repo_name": repo_name,
        "collection_owner": args.collection_owner,
        "collection_repo": args.collection_repo,
        "collection_branch": args.collection_branch,
        "run_id": run_id,
        "snapshot_file_count": len(files),
        "central_file_count": len(files) * 2,
        "missing_required": missing,
        "manifest": manifest,
        "staged": staged,
        "payload": payload_summary,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Prepared ADLC snapshot for {args.org}/{repo_name} ({run_id})")
        print(f"Snapshot files: {len(files)}; central files: {len(files) * 2}")
        if missing:
            print("Missing required files:")
            for item in missing:
                print(f"- {item}")
        if args.stage_dir:
            print(f"Staged central paths under {Path(args.stage_dir).expanduser().resolve()}")
        if args.payload_output:
            print(f"Wrote Cisco GitHub MCP push payload to {Path(args.payload_output).expanduser().resolve()}")

    if args.strict and missing:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
