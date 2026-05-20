#!/usr/bin/env python3
"""Initialize or refresh shared ADLC harness state in a target repository."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_HARNESS = ROOT / "standards" / "harness" / "default"
LOCAL_OVERRIDES = ROOT / "standards" / "harness" / "local-overrides"
SUPPORTED_LOCAL_OVERRIDES = ("claude", "codex", "augment")


@dataclass
class CopyResult:
    written: list[str]
    skipped: list[str]
    detected_local_harnesses: dict[str, list[str]]
    local_overrides_requested: list[str]


def detect_local_harnesses(repo_path: Path) -> dict[str, list[str]]:
    patterns = {
        "claude": [
            ".claude/commands/*harness*.md",
            ".claude/agents/*harness*",
            ".claude/skills/*harness*",
        ],
        "codex": [
            ".codex/skills/*harness*/SKILL.md",
            ".codex/commands/*harness*.md",
            ".codex/scripts/*harness*.py",
        ],
        "augment": [
            ".augment/**/*harness*",
            ".augment/**/*adlc*",
        ],
        "superpowers": [
            "docs/superpowers/plans/*.md",
            "docs/superpowers/specs/*.md",
        ],
    }
    detected: dict[str, list[str]] = {}
    for platform, globs in patterns.items():
        hits: list[str] = []
        for pattern in globs:
            for path in sorted(repo_path.glob(pattern)):
                if path.is_file():
                    hits.append(str(path.relative_to(repo_path)))
        detected[platform] = sorted(set(hits))
    return detected


def yaml_list(values: list[str], indent: int = 2) -> str:
    spaces = " " * indent
    if not values:
        return f"{spaces}[]"
    return "\n".join(f"{spaces}- {json.dumps(value)}" for value in values)


def detected_harnesses_yaml(detected: dict[str, list[str]]) -> str:
    lines: list[str] = []
    for platform in ("claude", "codex", "augment", "superpowers"):
        values = detected.get(platform, [])
        if values:
            lines.append(f"  {platform}:")
            lines.append(yaml_list(values, indent=4))
        else:
            lines.append(f"  {platform}: []")
    return "\n".join(lines)


def detected_harnesses_markdown(detected: dict[str, list[str]]) -> str:
    lines: list[str] = []
    for platform in ("claude", "codex", "augment", "superpowers"):
        values = detected.get(platform, [])
        if values:
            lines.append(f"- {platform}:")
            lines.extend(f"  - `{value}`" for value in values)
        else:
            lines.append(f"- {platform}: none detected")
    return "\n".join(lines)


def render_template(text: str, repo_path: Path, detected: dict[str, list[str]]) -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    return (
        text.replace("{{generated_at}}", generated_at)
        .replace("{{repo_name}}", repo_path.name)
        .replace("{{detected_harnesses_yaml}}", detected_harnesses_yaml(detected))
        .replace("{{detected_harnesses_json}}", json.dumps(detected, indent=2))
        .replace("{{detected_harnesses_markdown}}", detected_harnesses_markdown(detected))
    )


def copy_template_tree(
    source_root: Path,
    repo_path: Path,
    *,
    force: bool,
    dry_run: bool,
    detected: dict[str, list[str]],
    written: list[str],
    skipped: list[str],
    include_workflow: bool = True,
) -> None:
    for source in sorted(source_root.rglob("*")):
        if source.is_dir():
            continue
        rel_path = source.relative_to(source_root)
        if rel_path == Path("README.md"):
            continue
        if rel_path == Path("WORKFLOW.md") and not include_workflow:
            skipped.append(str(rel_path))
            continue
        target = repo_path / rel_path

        if target.exists() and not force:
            skipped.append(str(rel_path))
            continue

        text = source.read_text(encoding="utf-8")
        rendered = render_template(text, repo_path, detected)
        written.append(str(rel_path))

        if dry_run:
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")


def parse_local_overrides(raw_values: list[str]) -> list[str]:
    requested: list[str] = []
    for raw_value in raw_values:
        for value in raw_value.split(","):
            normalized = value.strip().lower()
            if not normalized:
                continue
            if normalized == "all":
                requested.extend(SUPPORTED_LOCAL_OVERRIDES)
            else:
                requested.append(normalized)
    return sorted(set(requested))


def copy_harness(
    repo_path: Path,
    *,
    force: bool,
    dry_run: bool,
    include_workflow: bool,
    local_overrides: list[str] | None = None,
) -> CopyResult:
    written: list[str] = []
    skipped: list[str] = []
    detected = detect_local_harnesses(repo_path)
    requested_overrides = sorted(set(local_overrides or []))

    copy_template_tree(
        DEFAULT_HARNESS,
        repo_path,
        force=force,
        dry_run=dry_run,
        detected=detected,
        written=written,
        skipped=skipped,
        include_workflow=include_workflow,
    )

    for platform in requested_overrides:
        source_root = LOCAL_OVERRIDES / platform
        if not source_root.exists():
            skipped.append(f"local-overrides/{platform}")
            continue
        copy_template_tree(
            source_root,
            repo_path,
            force=force,
            dry_run=dry_run,
            detected=detected,
            written=written,
            skipped=skipped,
        )

    return CopyResult(
        written=written,
        skipped=skipped,
        detected_local_harnesses=detected,
        local_overrides_requested=requested_overrides,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-path", default=".", help="Target repository path.")
    parser.add_argument("--include-workflow", action="store_true", help="Also write WORKFLOW.md if it is missing.")
    parser.add_argument(
        "--install-local-overrides",
        action="append",
        default=[],
        help="Optional comma-separated platform override files to install: claude,codex,augment, or all.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing harness files.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned changes without writing files.")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable summary.")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).expanduser().resolve()
    if not repo_path.exists():
        parser.error(f"repo path does not exist: {repo_path}")
    if not repo_path.is_dir():
        parser.error(f"repo path is not a directory: {repo_path}")
    if not DEFAULT_HARNESS.exists():
        parser.error(f"default harness scaffold missing: {DEFAULT_HARNESS}")
    local_overrides = parse_local_overrides(args.install_local_overrides)
    unsupported = sorted(set(local_overrides) - set(SUPPORTED_LOCAL_OVERRIDES))
    if unsupported:
        parser.error(f"unsupported local override platform(s): {', '.join(unsupported)}")

    result = copy_harness(
        repo_path,
        force=args.force,
        dry_run=args.dry_run,
        include_workflow=args.include_workflow,
        local_overrides=local_overrides,
    )

    payload = {
        "repo_path": str(repo_path),
        "harness_source": str(DEFAULT_HARNESS),
        "dry_run": args.dry_run,
        "force": args.force,
        "include_workflow": args.include_workflow,
        "install_local_overrides": result.local_overrides_requested,
        "written": result.written,
        "skipped": result.skipped,
        "detected_local_harnesses": result.detected_local_harnesses,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        verb = "Would write" if args.dry_run else "Wrote"
        print(f"{verb} {len(result.written)} shared ADLC harness files in {repo_path}")
        if result.skipped:
            print(f"Skipped {len(result.skipped)} existing files; use --force to overwrite.")
        if result.local_overrides_requested:
            print(f"Requested local override platforms: {', '.join(result.local_overrides_requested)}")
        detected_count = sum(len(values) for values in result.detected_local_harnesses.values())
        print(f"Detected {detected_count} existing local harness files.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
