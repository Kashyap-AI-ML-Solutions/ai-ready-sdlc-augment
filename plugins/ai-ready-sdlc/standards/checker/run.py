#!/usr/bin/env python3
"""Shared standards runner for Claude, Codex, and Augment packages."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "target",
    "reports",
}

IGNORE_TOP_LEVEL_DIRS = {
    ".adlc",
    ".agents",
    ".augment",
    ".claude",
    ".claude-marketplace",
    ".codex",
    ".cursor",
    ".windsurf",
    "plugins",
}

TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".java",
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hpp",
    ".hh",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".xml",
    ".properties",
    ".gradle",
    ".kts",
    ".sh",
}

AI_INDICATORS = [
    "openai",
    "anthropic",
    "langchain",
    "llamaindex",
    "litellm",
    "gpt-",
    "responses.create",
    "chat.completions",
    "vertexai",
    "bedrock",
    "ollama",
]

OBSERVABILITY_INDICATORS = [
    "opentelemetry",
    "otel",
    "langfuse",
    "honeycomb",
    "weave",
    "telemetry",
]

GUARDRAIL_INDICATORS = [
    "guardrail",
    "moderation",
    "redaction",
    "safety",
    "content filter",
]

TRIAGE_FIELDS = [
    "severity",
    "component",
    "customer impact",
    "probable cause",
    "suggested owner",
]

LOCKFILE_NAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
}

DOC_EXTENSIONS = {".md", ".txt"}

SECURITY_RULES = [
    {
        "id": "hardcoded-credential",
        "domain": "secret_management",
        "severity": "high",
        "title": "Possible hardcoded credential",
        "patterns": [
            re.compile(
                r"(?i)\b(api[_-]?key|secret|token|password|passwd|client_secret)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]"
            ),
            re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
            re.compile(r"-----BEGIN (?:RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----"),
        ],
        "allowed_extensions": TEXT_EXTENSIONS,
    },
    {
        "id": "tls-verification-disabled",
        "domain": "crypto_tls",
        "severity": "high",
        "title": "TLS verification appears disabled",
        "patterns": [
            re.compile(r"verify\s*=\s*False"),
            re.compile(r"InsecureSkipVerify\s*:\s*true"),
            re.compile(r"rejectUnauthorized\s*:\s*false"),
            re.compile(r"NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*[\"']?0[\"']?"),
            re.compile(r"\bcurl\s+-k\b"),
        ],
        "allowed_extensions": TEXT_EXTENSIONS,
    },
    {
        "id": "weak-crypto",
        "domain": "crypto_tls",
        "severity": "medium",
        "title": "Weak cryptography primitive detected",
        "patterns": [
            re.compile(r"(?i)\bmd5\b"),
            re.compile(r"(?i)\bsha1\b"),
            re.compile(r"(?i)\bdes\b"),
            re.compile(r"(?i)\brc4\b"),
        ],
        "allowed_extensions": TEXT_EXTENSIONS,
    },
    {
        "id": "dynamic-execution",
        "domain": "input_validation_and_injection",
        "severity": "high",
        "title": "Dynamic execution pattern detected",
        "patterns": [
            re.compile(r"\beval\s*\("),
            re.compile(r"\bexec\s*\("),
            re.compile(r"new Function\s*\("),
            re.compile(r"child_process\.(?:exec|execSync)\s*\("),
            re.compile(r"os\.system\s*\("),
            re.compile(r"shell\s*=\s*True"),
        ],
        "allowed_extensions": TEXT_EXTENSIONS,
    },
    {
        "id": "unpinned-github-action",
        "domain": "supply_chain_and_ci",
        "severity": "medium",
        "title": "Unpinned GitHub Action reference",
        "patterns": [
            re.compile(r"(?m)^\s*uses:\s*[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@(main|master|latest)\b")
        ],
        "path_substrings": [".github/workflows/"],
    },
    {
        "id": "privileged-kubernetes-setting",
        "domain": "cloud_iac_and_container",
        "severity": "high",
        "title": "Privileged container or pod setting detected",
        "patterns": [
            re.compile(r"(?m)^\s*privileged:\s*true\b"),
            re.compile(r"(?m)^\s*allowPrivilegeEscalation:\s*true\b"),
            re.compile(r"(?m)^\s*hostNetwork:\s*true\b"),
        ],
        "allowed_extensions": {".yaml", ".yml"},
    },
]


@dataclass
class RepoScan:
    files: list[Path]
    file_names: set[str]
    dir_names: set[str]
    ext_counter: Counter[str]
    files_by_ext: dict[str, list[Path]]


def load_registry(repo_root: Path) -> list[dict[str, Any]]:
    registry_path = repo_root / "standards" / "tooling" / "index.json"
    with registry_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload["languages"]


def load_project_codeguard_metadata(repo_root: Path) -> dict[str, Any]:
    current_path = repo_root / "third_party" / "project-codeguard" / "current.json"
    if not current_path.exists():
        return {
            "version": "unconfigured",
            "source": "https://github.com/cosai-oasis/project-codeguard",
            "release_page": "https://github.com/cosai-oasis/project-codeguard/releases",
            "release_date": None,
        }

    with current_path.open("r", encoding="utf-8") as handle:
        current = json.load(handle)

    metadata_path = repo_root / "third_party" / "project-codeguard" / current["metadata_path"]
    if not metadata_path.exists():
        return current

    with metadata_path.open("r", encoding="utf-8") as handle:
        metadata = json.load(handle)

    bundle_path = repo_root / "standards" / "security" / "project-codeguard" / "generated" / "current-bundle.json"
    if bundle_path.exists():
        with bundle_path.open("r", encoding="utf-8") as handle:
            bundle = json.load(handle)
        metadata["bundle_summary"] = bundle.get("summary", {})

    return metadata


def load_quality_thresholds(repo_root: Path) -> dict[str, Any]:
    config_path = repo_root / "standards" / "config" / "quality-thresholds.json"
    with config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def should_ignore_path(rel_path: Path) -> bool:
    parts = rel_path.parts
    if parts and parts[0] in IGNORE_TOP_LEVEL_DIRS:
        return True
    return any(part in IGNORE_DIRS for part in parts)


def git_visible_files(repo_path: Path) -> list[Path] | None:
    if not (repo_path / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=repo_path,
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
    except OSError:
        return None

    if result.returncode != 0:
        return None

    files: list[Path] = []
    for item in result.stdout.split("\0"):
        if not item:
            continue
        rel_path = Path(item)
        if rel_path.is_absolute() or should_ignore_path(rel_path):
            continue
        if (repo_path / rel_path).is_file():
            files.append(rel_path)
    return files


def record_scanned_file(
    rel_path: Path,
    files: list[Path],
    file_names: set[str],
    dir_names: set[str],
    ext_counter: Counter[str],
    files_by_ext: dict[str, list[Path]],
) -> None:
    files.append(rel_path)
    file_names.add(rel_path.name)
    for parent in rel_path.parents:
        if parent == Path("."):
            continue
        dir_names.add(parent.as_posix())
        dir_names.add(parent.name)
    suffix = rel_path.suffix.lower()
    if suffix:
        ext_counter[suffix] += 1
        files_by_ext[suffix].append(rel_path)


def scan_repo(repo_path: Path) -> RepoScan:
    files: list[Path] = []
    file_names: set[str] = set()
    dir_names: set[str] = set()
    ext_counter: Counter[str] = Counter()
    files_by_ext: dict[str, list[Path]] = defaultdict(list)

    visible_files = git_visible_files(repo_path)
    if visible_files is not None:
        for rel_path in visible_files:
            record_scanned_file(rel_path, files, file_names, dir_names, ext_counter, files_by_ext)
        return RepoScan(
            files=files,
            file_names=file_names,
            dir_names=dir_names,
            ext_counter=ext_counter,
            files_by_ext=files_by_ext,
        )

    for root, dirs, filenames in os.walk(repo_path):
        rel_root = Path(root).relative_to(repo_path)
        if rel_root == Path("."):
            dirs[:] = [item for item in dirs if item not in IGNORE_TOP_LEVEL_DIRS]
        dirs[:] = [item for item in dirs if item not in IGNORE_DIRS]
        dir_names.update({str((rel_root / item).as_posix()) for item in dirs})
        dir_names.update(dirs)

        for filename in filenames:
            path = Path(root) / filename
            rel_path = path.relative_to(repo_path)
            if should_ignore_path(rel_path):
                continue
            record_scanned_file(rel_path, files, file_names, dir_names, ext_counter, files_by_ext)

    return RepoScan(
        files=files,
        file_names=file_names,
        dir_names=dir_names,
        ext_counter=ext_counter,
        files_by_ext=files_by_ext,
    )


def resolve_revision(repo_path: Path) -> str:
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        return "unknown"
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_path,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        revision = result.stdout.strip()
        return revision or "unknown"
    except OSError:
        return "unknown"


def detect_language(language_def: dict[str, Any], scan: RepoScan) -> bool:
    detect = language_def.get("detect", {})
    language = language_def["language"]

    file_hits = any(name in scan.file_names for name in detect.get("files", []))
    ext_hits = sum(scan.ext_counter.get(ext, 0) for ext in detect.get("extensions", []))
    path_hits = any(path in scan.dir_names for path in detect.get("paths", []))

    if language == "ansible":
        return file_hits or path_hits

    return file_hits or ext_hits > 0


def representative_files(scan: RepoScan, extensions: Iterable[str], limit: int = 25) -> list[str]:
    results: list[str] = []
    for ext in extensions:
        for path in scan.files_by_ext.get(ext, []):
            if len(results) >= limit:
                return results
            results.append(str(path))
    return results


def find_playbook(scan: RepoScan) -> str:
    preferred = [path for path in scan.files if "playbooks/" in str(path) and path.suffix in {".yml", ".yaml"}]
    if preferred:
        return str(preferred[0])
    for path in scan.files:
        lowered = str(path).lower()
        if lowered.endswith((".yml", ".yaml")) and ("playbook" in lowered or "site" in lowered):
            return str(path)
    for path in scan.files:
        if path.suffix in {".yml", ".yaml"}:
            return str(path)
    return "."


def fill_command(template: str, language_def: dict[str, Any], scan: RepoScan) -> str:
    detect = language_def.get("detect", {})
    exts = detect.get("extensions", [])
    code_files = representative_files(scan, exts)
    targets = "."
    files = " ".join(shlex.quote(item) for item in code_files) if code_files else "."
    playbook = shlex.quote(find_playbook(scan))

    command = template.replace("<targets>", targets)
    command = command.replace("<files>", files)
    command = command.replace("<playbook>", playbook)
    return command


def command_roots(language_def: dict[str, Any], scan: RepoScan) -> list[Path]:
    if language_def["language"] != "javascript-typescript":
        return [Path(".")]

    roots = sorted({path.parent for path in scan.files if path.name == "package.json"})
    return roots or [Path(".")]


def format_command(command: str, cwd: Path) -> str:
    if cwd == Path("."):
        return command
    return f"(cd {shlex.quote(cwd.as_posix())} && {command})"


def command_available(command: str, repo_path: Path, cwd: Path = Path(".")) -> bool:
    command_root = repo_path / cwd
    alternatives = [item.strip() for item in command.split("||")]
    for alternative in alternatives:
        if not alternative:
            continue
        try:
            parts = shlex.split(alternative)
        except ValueError:
            continue
        if not parts:
            continue
        executable = parts[0]
        if executable == "npx":
            package_command = next((part for part in parts[1:] if not part.startswith("-")), "")
            if package_command:
                local_bin = command_root / "node_modules" / ".bin" / package_command
                if local_bin.exists():
                    return True
            continue
        if executable.startswith("./"):
            if (command_root / executable[2:]).exists():
                return True
        elif shutil.which(executable):
            return True
    return False


def run_command(
    command: str,
    repo_path: Path,
    timeout: int,
    cwd: Path = Path("."),
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=repo_path / cwd,
        shell=True,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def truncate(text: str, limit: int = 400) -> str:
    clean = " ".join(text.strip().split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3] + "..."


def missing_tool_output(text: str) -> bool:
    lowered = text.lower()
    return (
        "command not found" in lowered
        or "not installed" in lowered
        or "no such file or directory" in lowered
        or "pyenv:" in lowered and "command not found" in lowered
    )


def dimension_from_category(category: str) -> str:
    mapping = {
        "code_quality": "code_quality",
        "quality": "code_quality",
        "complexity": "complexity",
        "security": "security",
        "style": "style",
        "syntax": "style",
        "maintainability": "maintainability",
    }
    return mapping.get(category, "code_quality")


def score_dimension(statuses: list[str]) -> str:
    if not statuses:
        return "not_applicable"
    if any(status == "failed" for status in statuses):
        return "fail"
    if all(status in {"skipped", "planned"} for status in statuses):
        return "not_run"
    if any(status == "passed" for status in statuses):
        if any(status == "skipped" for status in statuses):
            return "warn"
        return "pass"
    return "warn"


def parse_json_output(text: str) -> Any:
    stripped = text.strip()
    if not stripped:
        return None
    for opener in ("[", "{"):
        index = stripped.find(opener)
        if index >= 0:
            try:
                return json.loads(stripped[index:])
            except json.JSONDecodeError:
                return None
    return None


def summarize_cyclomatic_complexity(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, list):
        return None

    file_count = 0
    complexity_sum = 0
    max_file_complexity = 0
    max_function_complexity = 0
    level_counts: Counter[str] = Counter()

    for item in payload:
        if not isinstance(item, dict):
            continue
        file_count += 1
        try:
            file_complexity = int(item.get("complexitySum", 0))
        except (TypeError, ValueError):
            file_complexity = 0
        complexity_sum += file_complexity
        max_file_complexity = max(max_file_complexity, file_complexity)
        level_counts[str(item.get("complexityLevel", "unknown"))] += 1

        for function_item in item.get("functionComplexities", []):
            if not isinstance(function_item, dict):
                continue
            try:
                function_complexity = int(function_item.get("complexity", 0))
            except (TypeError, ValueError):
                function_complexity = 0
            max_function_complexity = max(max_function_complexity, function_complexity)

    return {
        "files_analyzed": file_count,
        "complexity_sum": complexity_sum,
        "max_file_complexity": max_file_complexity,
        "max_function_complexity": max_function_complexity,
        "level_counts": dict(level_counts),
    }


def summarize_fta(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, list):
        return None

    scores: list[float] = []
    cyclo_values: list[float] = []
    assessment_counts: Counter[str] = Counter()

    for item in payload:
        if not isinstance(item, dict):
            continue
        try:
            scores.append(float(item.get("fta_score", 0)))
        except (TypeError, ValueError):
            pass
        try:
            cyclo_values.append(float(item.get("cyclo", 0)))
        except (TypeError, ValueError):
            pass
        assessment_counts[str(item.get("assessment", "unknown"))] += 1

    average_score = round(sum(scores) / len(scores), 2) if scores else None
    return {
        "files_analyzed": len(scores),
        "max_fta_score": round(max(scores), 2) if scores else None,
        "average_fta_score": average_score,
        "max_cyclomatic_complexity": round(max(cyclo_values), 2) if cyclo_values else None,
        "assessment_counts": dict(assessment_counts),
    }


def extract_tool_metrics(tool_name: str, stdout: str) -> dict[str, Any] | None:
    payload = parse_json_output(stdout)
    if tool_name == "cyclomatic-complexity":
        return summarize_cyclomatic_complexity(payload)
    if tool_name == "fta-cli":
        return summarize_fta(payload)
    return None


def severity_for(category: str, status: str) -> str:
    if status == "failed":
        if category == "security":
            return "high"
        if category in {"code_quality", "maintainability", "complexity"}:
            return "medium"
        return "low"
    return "low"


def read_text_snippet(repo_path: Path, rel_path: Path, limit: int = 12000) -> str:
    try:
        suffix = rel_path.suffix.lower()
        if suffix and suffix not in TEXT_EXTENSIONS:
            return ""
        full_path = repo_path / rel_path
        if full_path.stat().st_size > 1_000_000:
            return ""
        return full_path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""


def find_named_files(scan: RepoScan, fragments: Iterable[str], suffixes: Iterable[str] | None = None) -> list[str]:
    lowered_fragments = [item.lower() for item in fragments]
    suffix_set = {item.lower() for item in suffixes} if suffixes else None
    hits: list[str] = []
    for rel_path in scan.files:
        rel_text = str(rel_path).lower()
        if suffix_set and rel_path.suffix.lower() not in suffix_set:
            continue
        if any(fragment in rel_text for fragment in lowered_fragments):
            hits.append(str(rel_path))
    return hits


def find_content_hits(
    repo_path: Path,
    scan: RepoScan,
    terms: Iterable[str],
    candidate_paths: Iterable[Path] | None = None,
    limit: int = 10,
) -> list[str]:
    lowered_terms = [item.lower() for item in terms]
    hits: list[str] = []
    candidates = list(candidate_paths) if candidate_paths is not None else scan.files
    for rel_path in candidates:
        text = read_text_snippet(repo_path, rel_path)
        if not text:
            continue
        lowered = text.lower()
        for term in lowered_terms:
            if term in lowered:
                hits.append(f"{rel_path}:{term}")
                break
        if len(hits) >= limit:
            break
    return hits


def select_candidate_paths(
    scan: RepoScan,
    *,
    include_suffixes: set[str] | None = None,
    include_name_fragments: tuple[str, ...] = (),
    include_path_fragments: tuple[str, ...] = (),
    exclude_suffixes: set[str] | None = None,
    exclude_names: set[str] | None = None,
) -> list[Path]:
    candidates: list[Path] = []
    for rel_path in scan.files:
        rel_text = str(rel_path).lower()
        name = rel_path.name.lower()
        suffix = rel_path.suffix.lower()

        if exclude_names and name in exclude_names:
            continue
        if exclude_suffixes and suffix in exclude_suffixes:
            continue
        if include_suffixes and suffix not in include_suffixes:
            continue
        if include_name_fragments and not any(fragment in name for fragment in include_name_fragments):
            if include_path_fragments and not any(fragment in rel_text for fragment in include_path_fragments):
                continue
            if not include_path_fragments:
                continue
        elif include_path_fragments and not any(fragment in rel_text for fragment in include_path_fragments):
            if not any(fragment in name for fragment in include_name_fragments):
                continue

        candidates.append(rel_path)
    return candidates


def summarize_statuses(statuses: Iterable[str]) -> str:
    status_list = list(statuses)
    if not status_list:
        return "not_run"
    if any(status == "fail" for status in status_list):
        return "fail"
    if any(status == "not_run" for status in status_list):
        return "fail"
    if any(status == "warn" for status in status_list):
        return "warn"
    if all(status == "not_applicable" for status in status_list):
        return "not_applicable"
    return "pass"


def check_result(name: str, status: str, summary: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "summary": summary,
        "evidence": evidence or [],
    }


def area_finding(area: str, severity: str, summary: str, evidence: str = "", tool: str = "") -> dict[str, Any]:
    finding = {
        "area": area,
        "severity": severity,
        "summary": summary,
    }
    if evidence:
        finding["evidence"] = evidence
    if tool:
        finding["tool"] = tool
    return finding


def area_recommendation(priority: str, action: str, owner_hint: str = "repo owner or platform engineering") -> dict[str, Any]:
    return {
        "priority": priority,
        "action": action,
        "owner_hint": owner_hint,
    }


def dedupe_recommendations(recommendations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    ordered: list[dict[str, Any]] = []
    for item in recommendations:
        key = (item["priority"], item["action"])
        if key in seen:
            continue
        seen.add(key)
        ordered.append(item)
    return ordered


def tool_install_text(tool: dict[str, Any]) -> str:
    install = tool.get("install", {})
    parts: list[str] = []
    developer = install.get("developer")
    ci = install.get("ci")
    location = install.get("location")
    binary = tool.get("binary")
    if developer:
        parts.append(f"Developer install: `{developer}`.")
    if ci:
        parts.append(f"CI install: `{ci}`.")
    if location:
        parts.append(location)
    if binary:
        parts.append(f"Expected binary: `{binary}` on PATH.")
    return " ".join(parts)


def build_code_quality_report(
    repo_path: Path,
    languages: list[dict[str, Any]],
    tool_runs: list[dict[str, Any]],
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    recommendations: list[dict[str, Any]] = []
    dimension_statuses: dict[str, list[str]] = defaultdict(list)

    for run in tool_runs:
        dimension = dimension_from_category(run["category"])
        dimension_statuses[dimension].append(run["status"])

        if run["status"] in {"failed", "skipped"}:
            install_help = tool_install_text({"binary": run.get("binary", ""), "install": run.get("install", {})})
            findings.append(
                area_finding(
                    run["category"],
                    severity_for(run["category"], run["status"]),
                    f"{run['tool']} {run['status']} for {run['language']}",
                    " ".join(part for part in [run.get("summary", ""), install_help] if part),
                    run["tool"],
                )
            )

            if run["status"] == "failed":
                action = f"Review and remediate issues reported by {run['tool']} for {run['language']}."
                priority = "high" if run["category"] == "security" else "medium"
            else:
                action = f"Install or enable {run['tool']} so {run['language']} repositories can be evaluated consistently. {install_help}".strip()
                priority = "medium" if run["category"] in {"security", "code_quality"} else "low"

            recommendations.append(area_recommendation(priority, action))

    dimension_scores = {
        key: score_dimension(value)
        for key, value in {
            "code_quality": dimension_statuses.get("code_quality", []),
            "complexity": dimension_statuses.get("complexity", []),
            "security": dimension_statuses.get("security", []),
            "style": dimension_statuses.get("style", []),
            "maintainability": dimension_statuses.get("maintainability", []),
        }.items()
    }

    return {
        "repository": repo_path.name,
        "revision": resolve_revision(repo_path),
        "languages_detected": [item["language"] for item in languages],
        "tools_run": tool_runs,
        "dimension_scores": dimension_scores,
        "findings": findings,
        "recommendations": recommendations,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def evaluate_code_quality(
    repo_path: Path,
    scan: RepoScan,
    registry: list[dict[str, Any]],
    include_optional: bool,
    dry_run: bool,
    timeout_seconds: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    detected_languages = [item for item in registry if detect_language(item, scan)]
    tool_runs: list[dict[str, Any]] = []

    for language_def in detected_languages:
        tools = list(language_def.get("required_tools", []))
        if include_optional:
            tools.extend(language_def.get("optional_tools", []))

        for cwd in command_roots(language_def, scan):
            for tool in tools:
                command = fill_command(tool["command"], language_def, scan)
                available = command_available(command, repo_path, cwd)

                run_record = {
                    "language": language_def["language"],
                    "tool": tool["tool"],
                    "category": tool["category"],
                    "status": "skipped",
                    "command": format_command(command, cwd),
                    "cwd": cwd.as_posix(),
                    "binary": tool.get("binary", ""),
                    "install": tool.get("install", {}),
                }

                if not available:
                    run_record["summary"] = "tool not available in current environment"
                    tool_runs.append(run_record)
                    continue

                if dry_run:
                    run_record["status"] = "planned"
                    run_record["summary"] = "tool available; command resolved but not executed"
                    tool_runs.append(run_record)
                    continue

                try:
                    completed = run_command(command, repo_path, timeout_seconds, cwd)
                except subprocess.TimeoutExpired:
                    run_record["status"] = "failed"
                    run_record["summary"] = f"timed out after {timeout_seconds} seconds"
                    tool_runs.append(run_record)
                    continue

                summary = truncate(completed.stdout or completed.stderr or "completed with no output")
                if completed.returncode == 0:
                    run_record["status"] = "passed"
                elif missing_tool_output(summary):
                    run_record["status"] = "skipped"
                else:
                    run_record["status"] = "failed"
                metrics = extract_tool_metrics(tool["tool"], completed.stdout)
                if metrics:
                    run_record["metrics"] = metrics
                run_record["summary"] = summary
                tool_runs.append(run_record)

    return detected_languages, build_code_quality_report(repo_path, detected_languages, tool_runs)


def should_scan_text_file(rel_path: Path) -> bool:
    parts = {part.lower() for part in rel_path.parts}
    if parts & {"docs", "doc", "examples"}:
        return False
    if rel_path.name.lower() in {"license", "notice"}:
        return False
    if rel_path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    return rel_path.name in {"Dockerfile", "Jenkinsfile", ".env", ".env.example"}


def iter_security_files(repo_path: Path, scan: RepoScan) -> Iterable[tuple[Path, str]]:
    for rel_path in scan.files:
        if not should_scan_text_file(rel_path):
            continue
        abs_path = repo_path / rel_path
        try:
            if abs_path.stat().st_size > 1_000_000:
                continue
            text = abs_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if text:
            yield rel_path, text


def domains_checked(scan: RepoScan, languages_detected: list[str]) -> list[str]:
    domains = {"secret_management"}
    if languages_detected:
        domains.update({"crypto_tls", "input_validation_and_injection"})
    if any(".github/workflows/" in str(path) for path in scan.files):
        domains.add("supply_chain_and_ci")
    if any(
        path.name == "Dockerfile"
        or path.suffix.lower() in {".yaml", ".yml", ".tf", ".tfvars"}
        for path in scan.files
    ):
        domains.add("cloud_iac_and_container")
    return sorted(domains)


def rule_matches_path(rule: dict[str, Any], rel_path: Path) -> bool:
    rel_value = str(rel_path).replace("\\", "/")
    if "allowed_extensions" in rule and rel_path.suffix.lower() not in rule["allowed_extensions"]:
        if rel_path.name not in {"Dockerfile", "Jenkinsfile", ".env"}:
            return False
    if "path_substrings" in rule and not any(item in rel_value for item in rule["path_substrings"]):
        return False
    return True


def recommendation_for_rule(rule_id: str) -> str:
    mapping = {
        "hardcoded-credential": "Move credentials into environment variables or a secret store and rotate any exposed values.",
        "tls-verification-disabled": "Re-enable TLS verification and use a trusted CA bundle or proper certificate configuration.",
        "weak-crypto": "Replace weak cryptographic primitives with modern approved algorithms and document compatibility impacts.",
        "dynamic-execution": "Replace dynamic execution with safer parsing or explicit command allowlists and validation.",
        "unpinned-github-action": "Pin GitHub Actions to immutable commit SHAs or approved release tags.",
        "privileged-kubernetes-setting": "Review pod privileges and move to least-privilege container and cluster settings.",
    }
    return mapping.get(rule_id, "Review and remediate the matched Project CodeGuard finding.")


def finding_is_actionable(rule_id: str, evidence: str) -> bool:
    if rule_id != "hardcoded-credential":
        return True

    placeholder_markers = (
        "${",
        "{{",
        "default(",
        "default (",
        "changeme",
        "placeholder",
        "uninitialized",
        "example",
    )
    lowered = evidence.lower()
    return not any(marker.lower() in lowered for marker in placeholder_markers)


def evaluate_project_codeguard_security(
    repo_path: Path,
    repo_root: Path,
    scan: RepoScan,
    languages: list[dict[str, Any]],
) -> dict[str, Any]:
    detected_languages = [item["language"] for item in languages]
    metadata = load_project_codeguard_metadata(repo_root)
    findings: list[dict[str, Any]] = []
    recommendations: list[dict[str, Any]] = []

    for rel_path, text in iter_security_files(repo_path, scan):
        for rule in SECURITY_RULES:
            if not rule_matches_path(rule, rel_path):
                continue
            for pattern in rule["patterns"]:
                match = pattern.search(text)
                if not match:
                    continue

                evidence = truncate(match.group(0), 180)
                if not finding_is_actionable(rule["id"], evidence):
                    continue
                findings.append(
                    {
                        "area": "project_codeguard_security",
                        "id": rule["id"],
                        "domain": rule["domain"],
                        "severity": rule["severity"],
                        "title": rule["title"],
                        "summary": f"{rule['title']} in {rel_path}",
                        "file": str(rel_path),
                        "evidence": evidence,
                    }
                )
                recommendations.append(
                    area_recommendation(
                        "high" if rule["severity"] == "high" else "medium",
                        recommendation_for_rule(rule["id"]),
                        "repo owner or security champion",
                    )
                )
                break

    status = "pass"
    if findings:
        if any(item["severity"] == "high" for item in findings):
            status = "fail"
        else:
            status = "warn"
    elif not detected_languages and not any(domain != "secret_management" for domain in domains_checked(scan, detected_languages)):
        status = "not_applicable"

    return {
        "area": "project_codeguard_security",
        "profile": "project-codeguard-security",
        "status": status,
        "upstream": metadata,
        "domains_checked": domains_checked(scan, detected_languages),
        "files_scanned": sum(1 for _ in iter_security_files(repo_path, scan)),
        "languages_detected": detected_languages,
        "checks": [
            check_result(
                "project_codeguard_rules_applied",
                "pass" if metadata.get("version") != "unconfigured" else "warn",
                (
                    f"Using pinned Project CodeGuard version {metadata.get('version', 'unknown')}"
                    f" with {metadata.get('bundle_summary', {}).get('rule_count', 'unknown')} normalized rules."
                ),
                [metadata.get("release_page", metadata.get("source", ""))],
            ),
            check_result(
                "security_findings_evaluated",
                status,
                "Security heuristics were applied across relevant repository files.",
            ),
        ],
        "findings": findings,
        "recommendations": dedupe_recommendations(recommendations),
    }


def parse_coverage_summary_json(text: str) -> float | None:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    total = payload.get("total", {})
    lines = total.get("lines", {})
    pct = lines.get("pct")
    if isinstance(pct, (int, float)):
        return float(pct)
    return None


def parse_coverage_xml(text: str) -> float | None:
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return None
    line_rate = root.attrib.get("line-rate")
    if line_rate is not None:
        try:
            value = float(line_rate)
            return value * 100 if value <= 1 else value
        except ValueError:
            return None
    coverage = root.find(".//coverage")
    if coverage is not None:
        line_rate = coverage.attrib.get("line-rate")
        if line_rate is not None:
            try:
                value = float(line_rate)
                return value * 100 if value <= 1 else value
            except ValueError:
                return None
    return None


def parse_lcov(text: str) -> float | None:
    lines_found = 0
    lines_hit = 0
    for line in text.splitlines():
        if line.startswith("LF:"):
            try:
                lines_found += int(line.split(":", 1)[1])
            except ValueError:
                pass
        elif line.startswith("LH:"):
            try:
                lines_hit += int(line.split(":", 1)[1])
            except ValueError:
                pass
    if lines_found <= 0:
        return None
    return (lines_hit / lines_found) * 100.0


def detect_coverage_artifact(repo_path: Path, scan: RepoScan) -> dict[str, Any]:
    candidates = [
        "coverage-summary.json",
        "coverage/coverage-summary.json",
        "coverage.xml",
        "coverage/coverage.xml",
        "lcov.info",
        "coverage/lcov.info",
    ]
    existing = {str(path): path for path in scan.files}
    for candidate in candidates:
        rel_path = existing.get(candidate)
        if not rel_path:
            continue
        text = read_text_snippet(repo_path, rel_path, limit=2_000_000)
        if not text:
            continue
        percentage = None
        if candidate.endswith("coverage-summary.json"):
            percentage = parse_coverage_summary_json(text)
        elif candidate.endswith(".xml"):
            percentage = parse_coverage_xml(text)
        elif candidate.endswith("lcov.info"):
            percentage = parse_lcov(text)
        return {
            "artifact": candidate,
            "line_coverage_percent": percentage,
        }
    return {
        "artifact": None,
        "line_coverage_percent": None,
    }


def evaluate_ai_readiness(repo_path: Path, scan: RepoScan, languages: list[dict[str, Any]]) -> dict[str, Any]:
    signal_candidates = select_candidate_paths(
        scan,
        exclude_suffixes=DOC_EXTENSIONS,
        exclude_names=LOCKFILE_NAMES,
    )
    manifest_hits = find_named_files(scan, ["ai_manifest"], [".yml", ".yaml", ".json"])
    ai_hits = find_content_hits(repo_path, scan, AI_INDICATORS, signal_candidates)
    observability_hits = find_content_hits(repo_path, scan, OBSERVABILITY_INDICATORS, signal_candidates)
    guardrail_hits = find_content_hits(repo_path, scan, GUARDRAIL_INDICATORS, signal_candidates)

    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    recommendations: list[dict[str, Any]] = []

    ai_usage_detected = bool(ai_hits)
    checks.append(
        check_result(
            "ai_usage_detected",
            "pass" if ai_usage_detected else "not_applicable",
            "Repository appears to use AI-related libraries or APIs." if ai_usage_detected else "No clear AI usage indicators were detected.",
            ai_hits[:5],
        )
    )

    if ai_usage_detected and not manifest_hits:
        checks.append(
            check_result(
                "ai_manifest_present",
                "fail",
                "AI usage detected but no AI capability manifest was found.",
            )
        )
        findings.append(
            area_finding(
                "ai_readiness",
                "high",
                "AI usage was detected without an AI capability manifest.",
                ", ".join(ai_hits[:5]),
            )
        )
        recommendations.append(
            area_recommendation(
                "high",
                "Add an AI capability manifest such as ai_manifest.yaml and keep it aligned to production AI behavior.",
            )
        )
    elif manifest_hits:
        checks.append(
            check_result(
                "ai_manifest_present",
                "pass",
                "AI capability manifest found.",
                manifest_hits[:5],
            )
        )
    else:
        checks.append(
            check_result(
                "ai_manifest_present",
                "not_applicable",
                "No manifest was found, but no AI usage indicators were detected.",
            )
        )

    if ai_usage_detected and not observability_hits:
        checks.append(
            check_result(
                "observability_signals_present",
                "warn",
                "AI usage detected but observability signals were not found.",
            )
        )
        findings.append(
            area_finding(
                "ai_readiness",
                "medium",
                "AI usage appears to lack observable tracing or telemetry hooks.",
                ", ".join(ai_hits[:3]),
            )
        )
        recommendations.append(
            area_recommendation(
                "medium",
                "Add observability for AI flows, such as OpenTelemetry, Langfuse, or equivalent tracing signals.",
            )
        )
    elif observability_hits:
        checks.append(
            check_result(
                "observability_signals_present",
                "pass",
                "Observability indicators were found.",
                observability_hits[:5],
            )
        )
    else:
        checks.append(
            check_result(
                "observability_signals_present",
                "not_applicable",
                "No observability signals were found and no AI usage was detected.",
            )
        )

    if ai_usage_detected and not guardrail_hits:
        checks.append(
            check_result(
                "guardrail_signals_present",
                "warn",
                "AI usage detected but no clear guardrail or moderation signals were found.",
            )
        )
        recommendations.append(
            area_recommendation(
                "low",
                "Add or document guardrails such as moderation, redaction, or safety controls for AI-enabled flows.",
            )
        )
    elif guardrail_hits:
        checks.append(
            check_result(
                "guardrail_signals_present",
                "pass",
                "Guardrail or safety indicators were found.",
                guardrail_hits[:5],
            )
        )
    else:
        checks.append(
            check_result(
                "guardrail_signals_present",
                "not_applicable",
                "No guardrail indicators were found and no AI usage was detected.",
            )
        )

    status = summarize_statuses(check["status"] for check in checks)
    return {
        "area": "ai_readiness",
        "status": status,
        "checks": checks,
        "findings": findings,
        "recommendations": recommendations,
        "languages_detected": [item["language"] for item in languages],
    }


def evaluate_bug_triage(repo_path: Path, scan: RepoScan) -> dict[str, Any]:
    template_hits = find_named_files(
        scan,
        [".github/issue_template", "bug_report", "bug-report", "issue template", "issue_templates", "bug.md"],
        [".md", ".yaml", ".yml", ".json"],
    )
    template_paths = [Path(item) for item in template_hits]
    triage_hits = find_content_hits(repo_path, scan, TRIAGE_FIELDS, template_paths if template_paths else None)
    automation_hits = find_content_hits(
        repo_path,
        scan,
        ["triage", "jira", "issue", "bug", "label", "severity"],
        [path for path in scan.files if ".github/workflows/" in str(path) or path.suffix in {".sh", ".py", ".yml", ".yaml"}],
    )

    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    recommendations: list[dict[str, Any]] = []

    if template_hits:
        checks.append(check_result("bug_template_present", "pass", "Bug report or issue template found.", template_hits[:5]))
    else:
        checks.append(check_result("bug_template_present", "warn", "No bug report or issue template was found."))
        findings.append(area_finding("bug_triage", "medium", "Repository lacks a bug or issue template for structured triage."))
        recommendations.append(area_recommendation("medium", "Add a bug report template that captures required triage fields."))

    if triage_hits:
        checks.append(
            check_result(
                "required_triage_fields_present",
                "pass",
                "Triage field signals were found in template or documentation content.",
                triage_hits[:5],
            )
        )
    else:
        checks.append(
            check_result(
                "required_triage_fields_present",
                "warn",
                "Required triage fields such as severity, component, and customer impact were not detected.",
            )
        )
        findings.append(
            area_finding(
                "bug_triage",
                "medium",
                "Required bug triage fields were not found in issue templates or supporting docs.",
            )
        )
        recommendations.append(
            area_recommendation(
                "medium",
                "Update bug templates or issue forms to include severity, component, customer impact, probable cause, and suggested owner.",
            )
        )

    if automation_hits:
        checks.append(
            check_result(
                "triage_automation_signals_present",
                "pass",
                "Workflow or script signals for issue or triage automation were found.",
                automation_hits[:5],
            )
        )
    else:
        checks.append(
            check_result(
                "triage_automation_signals_present",
                "warn",
                "No clear triage automation hooks were found in workflows or scripts.",
            )
        )
        recommendations.append(
            area_recommendation(
                "low",
                "Add workflow automation or scripts that can enrich bugs with triage metadata and routing hints.",
            )
        )

    status = summarize_statuses(check["status"] for check in checks)
    return {
        "area": "bug_triage",
        "status": status,
        "checks": checks,
        "findings": findings,
        "recommendations": recommendations,
    }


def detect_test_files(scan: RepoScan) -> list[str]:
    code_test_extensions = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".go",
        ".java",
        ".c",
        ".cc",
        ".cpp",
        ".cxx",
        ".h",
        ".hpp",
        ".hh",
    }
    hits: list[str] = []
    for rel_path in scan.files:
        lowered = str(rel_path).lower()
        name = rel_path.name.lower()
        suffix = rel_path.suffix.lower()
        if suffix not in code_test_extensions:
            continue
        if (
            "/tests/" in lowered
            or lowered.startswith("tests/")
            or "__tests__" in lowered
            or name.startswith("test_")
            or name.endswith("_test.py")
            or name.endswith("_test.go")
            or ".test." in name
            or ".spec." in name
            or lowered.startswith("src/test/")
            or lowered.startswith("test/")
        ):
            hits.append(str(rel_path))
    return hits


def evaluate_requirements_to_tests(
    repo_path: Path,
    scan: RepoScan,
    languages: list[dict[str, Any]],
    thresholds: dict[str, Any],
) -> dict[str, Any]:
    test_files = detect_test_files(scan)
    plan_file_hits = find_named_files(scan, ["test_plan", "test-plan", "qa-plan", "requirements", "spec"], [".md", ".txt", ".yaml", ".yml"])
    plan_candidates = select_candidate_paths(
        scan,
        include_suffixes={".md", ".txt", ".yaml", ".yml", ".json"},
        include_name_fragments=("test", "qa", "require", "spec", "plan"),
        include_path_fragments=("docs/", "tests/", ".github/"),
        exclude_names={"readme.md"},
    )
    plan_content_hits = find_content_hits(
        repo_path,
        scan,
        ["test plan", "acceptance criteria", "happy path", "edge case", "negative path"],
        plan_candidates,
    )
    ci_hits = find_content_hits(
        repo_path,
        scan,
        ["pytest", "go test", "npm test", "yarn test", "mvn test", "gradle test", "ctest"],
        [path for path in scan.files if ".github/workflows/" in str(path) or path.name in {"package.json", "Makefile", "pom.xml", "build.gradle", "build.gradle.kts"}],
    )
    mapping_candidates = select_candidate_paths(
        scan,
        include_suffixes={".md", ".txt", ".yaml", ".yml", ".json"},
        include_name_fragments=("test", "qa", "require", "spec", "plan", "manifest"),
        include_path_fragments=("docs/", "tests/", ".github/"),
        exclude_names={"readme.md", ".gitignore", ".dockerignore"},
    )
    mapping_hits = find_content_hits(
        repo_path,
        scan,
        ["test mapping", "requirement-to-test", "traceability", "coverage threshold", "coverage policy"],
        mapping_candidates,
    )
    coverage_info = detect_coverage_artifact(repo_path, scan)
    coverage_policy = thresholds.get("coverage", {})
    repo_min = coverage_policy.get("repository_min_percent", 80)

    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    recommendations: list[dict[str, Any]] = []

    if test_files:
        checks.append(check_result("tests_present", "pass", "Repository test files were found.", test_files[:5]))
    else:
        status = "fail" if languages else "not_applicable"
        checks.append(check_result("tests_present", status, "No repository test files were found."))
        if languages:
            findings.append(area_finding("requirements_to_tests", "high", "Repository contains source code but no test files were detected."))
            recommendations.append(area_recommendation("high", "Add automated tests for the repository codebase and make them runnable in CI."))

    if plan_file_hits or plan_content_hits:
        evidence = (plan_file_hits + plan_content_hits)[:5]
        checks.append(check_result("test_plan_artifacts_present", "pass", "Test plan or requirements coverage artifacts were found.", evidence))
    else:
        checks.append(check_result("test_plan_artifacts_present", "warn", "No test plan or requirements coverage artifacts were detected."))
        recommendations.append(area_recommendation("medium", "Add a lightweight test plan or requirements-to-tests artifact for higher-risk changes."))

    if ci_hits:
        checks.append(check_result("test_execution_signals_present", "pass", "Test execution signals were found in workflows or build files.", ci_hits[:5]))
    else:
        checks.append(check_result("test_execution_signals_present", "warn", "No clear CI or build signals for test execution were found."))
        findings.append(area_finding("requirements_to_tests", "medium", "Repository lacks obvious CI or build hooks for running tests."))
        recommendations.append(area_recommendation("medium", "Add CI or build configuration that runs repository tests automatically."))

    if mapping_hits:
        checks.append(check_result("requirements_mapping_signals_present", "pass", "Traceability or mapping signals were found.", mapping_hits[:5]))
    else:
        checks.append(check_result("requirements_mapping_signals_present", "warn", "No clear requirement-to-test mapping signals were found."))
        recommendations.append(area_recommendation("low", "Document simple traceability between requirements, risk areas, and test coverage."))

    if coverage_info["artifact"] and coverage_info["line_coverage_percent"] is not None:
        observed = round(float(coverage_info["line_coverage_percent"]), 2)
        if observed >= repo_min:
            checks.append(
                check_result(
                    "repository_coverage_threshold_met",
                    "pass",
                    f"Repository line coverage is {observed}% and meets the {repo_min}% minimum.",
                    [coverage_info["artifact"]],
                )
            )
        else:
            checks.append(
                check_result(
                    "repository_coverage_threshold_met",
                    "fail",
                    f"Repository line coverage is {observed}% and is below the {repo_min}% minimum.",
                    [coverage_info["artifact"]],
                )
            )
            findings.append(
                area_finding(
                    "requirements_to_tests",
                    "high",
                    f"Repository line coverage is {observed}%, below the required {repo_min}%.",
                    coverage_info["artifact"],
                )
            )
            recommendations.append(
                area_recommendation(
                    "high",
                    f"Increase repository line coverage to at least {repo_min}% and regenerate the coverage artifact.",
                )
            )
    else:
        checks.append(
            check_result(
                "repository_coverage_threshold_met",
                "warn",
                f"No machine-readable coverage artifact was found to evaluate the {repo_min}% repository coverage minimum.",
            )
        )
        recommendations.append(
            area_recommendation(
                "medium",
                "Generate a machine-readable coverage artifact such as coverage-summary.json, coverage.xml, or lcov.info.",
            )
        )

    status = summarize_statuses(check["status"] for check in checks)
    return {
        "area": "requirements_to_tests",
        "status": status,
        "checks": checks,
        "findings": findings,
        "recommendations": recommendations,
        "coverage_policy": coverage_policy,
        "coverage_observed": coverage_info,
    }


def overall_status(statuses: Iterable[str]) -> str:
    status_list = list(statuses)
    if not status_list:
        return "not_run"
    if any(status == "fail" for status in status_list):
        return "fail"
    if any(status == "not_run" for status in status_list):
        return "fail"
    if any(status == "warn" for status in status_list):
        return "warn"
    if all(status == "not_applicable" for status in status_list):
        return "not_applicable"
    return "pass"


def build_org_standards_report(
    repo_path: Path,
    code_quality: dict[str, Any],
    ai_readiness: dict[str, Any],
    bug_triage: dict[str, Any],
    requirements_to_tests: dict[str, Any],
    project_codeguard_security: dict[str, Any],
) -> dict[str, Any]:
    area_statuses = {
        "code_quality": overall_status(code_quality["dimension_scores"].values()),
        "ai_readiness": ai_readiness["status"],
        "bug_triage": bug_triage["status"],
        "requirements_to_tests": requirements_to_tests["status"],
        "project_codeguard_security": project_codeguard_security["status"],
    }

    findings = (
        list(code_quality["findings"])
        + ai_readiness["findings"]
        + bug_triage["findings"]
        + requirements_to_tests["findings"]
        + project_codeguard_security["findings"]
    )
    recommendations = dedupe_recommendations(
        list(code_quality["recommendations"])
        + ai_readiness["recommendations"]
        + bug_triage["recommendations"]
        + requirements_to_tests["recommendations"]
        + project_codeguard_security["recommendations"]
    )

    report = {
        "repository": repo_path.name,
        "revision": resolve_revision(repo_path),
        "profile": "org-standards",
        "overall_status": overall_status(area_statuses.values()),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "areas": {
            "code_quality": code_quality,
            "ai_readiness": ai_readiness,
            "bug_triage": bug_triage,
            "requirements_to_tests": requirements_to_tests,
            "project_codeguard_security": project_codeguard_security,
        },
        "area_statuses": area_statuses,
        "findings": findings,
        "recommendations": recommendations,
    }
    return report


def render_code_quality_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Code Quality Report",
        "",
        "## Repository Summary",
        "",
        f"- Repository: {report['repository']}",
        f"- Revision: {report['revision']}",
        f"- Languages detected: {', '.join(report['languages_detected']) or 'none'}",
        f"- Evaluation date: {report['checked_at']}",
        "",
        "## Dimension Scores",
        "",
        "| Dimension | Score |",
        "| --- | --- |",
    ]

    for dimension, score in report["dimension_scores"].items():
        lines.append(f"| {dimension} | {score} |")

    lines.extend(["", "## Tools Run", "", "| Language | Tool | Category | Status | Summary |", "| --- | --- | --- | --- | --- |"])
    for run in report["tools_run"]:
        summary = run.get("summary", "").replace("|", "/")
        lines.append(f"| {run['language']} | {run['tool']} | {run['category']} | {run['status']} | {summary} |")

    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        lines.extend(["| Severity | Area | Summary | Tool | Evidence |", "| --- | --- | --- | --- | --- |"])
        for finding in report["findings"]:
            evidence = finding.get("evidence", "").replace("|", "/")
            lines.append(f"| {finding['severity']} | {finding['area']} | {finding['summary']} | {finding.get('tool', '')} | {evidence} |")
    else:
        lines.append("- No findings.")

    lines.extend(["", "## Recommendations", ""])
    if report["recommendations"]:
        for index, recommendation in enumerate(report["recommendations"], start=1):
            lines.append(f"{index}. [{recommendation['priority']}] {recommendation['action']}")
    else:
        lines.append("- No recommendations.")

    return "\n".join(lines) + "\n"


def render_area_markdown(report: dict[str, Any], title: str) -> str:
    lines = [
        f"# {title}",
        "",
        "## Summary",
        "",
        f"- Repository: {report['repository']}",
        f"- Revision: {report['revision']}",
        f"- Status: {report['status']}",
        f"- Checked at: {report['checked_at']}",
        "",
        "## Checks",
        "",
        "| Check | Status | Summary | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for check in report["checks"]:
        evidence = ", ".join(check.get("evidence", [])[:3]).replace("|", "/")
        lines.append(f"| {check['name']} | {check['status']} | {check['summary']} | {evidence} |")

    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        for finding in report["findings"]:
            lines.append(f"- [{finding['severity']}] {finding['summary']}")
    else:
        lines.append("- No findings.")

    lines.extend(["", "## Recommendations", ""])
    if report["recommendations"]:
        for index, recommendation in enumerate(report["recommendations"], start=1):
            lines.append(f"{index}. [{recommendation['priority']}] {recommendation['action']}")
    else:
        lines.append("- No recommendations.")

    if report.get("coverage_policy"):
        lines.extend(["", "## Coverage Policy", ""])
        policy = report["coverage_policy"]
        lines.append(f"- Repository minimum: {policy.get('repository_min_percent', 'n/a')}%")
        lines.append(f"- Changed-lines minimum: {policy.get('changed_lines_min_percent', 'n/a')}%")
        lines.append(f"- Critical paths minimum: {policy.get('critical_paths_min_percent', 'n/a')}%")
        observed = report.get("coverage_observed", {})
        if observed.get("artifact"):
            lines.append(f"- Observed artifact: {observed['artifact']}")
        if observed.get("line_coverage_percent") is not None:
            lines.append(f"- Observed line coverage: {round(float(observed['line_coverage_percent']), 2)}%")

    return "\n".join(lines) + "\n"


def render_project_codeguard_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Project CodeGuard Security Report",
        "",
        "## Summary",
        "",
        f"- Repository: {report['repository']}",
        f"- Revision: {report['revision']}",
        f"- Status: {report['status']}",
        f"- Checked at: {report['checked_at']}",
        f"- Project CodeGuard version: {report['upstream'].get('version', 'unknown')}",
        (
            f"- Normalized rule count: "
            f"{report['upstream'].get('bundle_summary', {}).get('rule_count', 'unknown')}"
        ),
        f"- Domains checked: {', '.join(report.get('domains_checked', [])) or 'none'}",
        f"- Files scanned: {report.get('files_scanned', 0)}",
        "",
        "## Checks",
        "",
        "| Check | Status | Summary | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for check in report["checks"]:
        evidence = ", ".join(check.get("evidence", [])[:3]).replace("|", "/")
        lines.append(f"| {check['name']} | {check['status']} | {check['summary']} | {evidence} |")

    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        lines.extend(["| Severity | Domain | Title | File | Evidence |", "| --- | --- | --- | --- | --- |"])
        for finding in report["findings"]:
            evidence = finding.get("evidence", "").replace("|", "/")
            lines.append(
                f"| {finding['severity']} | {finding['domain']} | {finding['title']} | {finding['file']} | {evidence} |"
            )
    else:
        lines.append("- No Project CodeGuard findings detected by the current lane.")

    lines.extend(["", "## Recommendations", ""])
    if report["recommendations"]:
        for index, recommendation in enumerate(report["recommendations"], start=1):
            lines.append(f"{index}. [{recommendation['priority']}] {recommendation['action']}")
    else:
        lines.append("- No recommendations.")

    return "\n".join(lines) + "\n"


def render_org_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Organization Standards Report",
        "",
        "## Summary",
        "",
        f"- Repository: {report['repository']}",
        f"- Revision: {report['revision']}",
        f"- Overall status: {report['overall_status']}",
        f"- Checked at: {report['checked_at']}",
        "",
        "## Area Status",
        "",
        "| Area | Status |",
        "| --- | --- |",
    ]
    for area, status in report["area_statuses"].items():
        lines.append(f"| {area} | {status} |")

    code_quality = report["areas"]["code_quality"]
    lines.extend(["", "## Code Quality", "", f"- Languages detected: {', '.join(code_quality['languages_detected']) or 'none'}", ""])
    lines.extend(["| Dimension | Score |", "| --- | --- |"])
    for dimension, score in code_quality["dimension_scores"].items():
        lines.append(f"| {dimension} | {score} |")

    for area_key in ("ai_readiness", "bug_triage", "requirements_to_tests"):
        area = report["areas"][area_key]
        lines.extend(["", f"## {area_key.replace('_', ' ').title()}", "", "| Check | Status | Summary |", "| --- | --- | --- |"])
        for check in area["checks"]:
            lines.append(f"| {check['name']} | {check['status']} | {check['summary']} |")

    codeguard = report["areas"]["project_codeguard_security"]
    lines.extend(
        [
            "",
            "## Project CodeGuard Security",
            "",
            f"- Version: {codeguard['upstream'].get('version', 'unknown')}",
            f"- Domains checked: {', '.join(codeguard.get('domains_checked', [])) or 'none'}",
            f"- Files scanned: {codeguard.get('files_scanned', 0)}",
            "",
            "| Check | Status | Summary |",
            "| --- | --- | --- |",
        ]
    )
    for check in codeguard["checks"]:
        lines.append(f"| {check['name']} | {check['status']} | {check['summary']} |")

    coverage = report["areas"]["requirements_to_tests"].get("coverage_policy")
    if coverage:
        observed = report["areas"]["requirements_to_tests"].get("coverage_observed", {})
        lines.extend(
            [
                "",
                "## Coverage Policy",
                "",
                f"- Repository minimum: {coverage.get('repository_min_percent', 'n/a')}%",
                f"- Changed-lines minimum: {coverage.get('changed_lines_min_percent', 'n/a')}%",
                f"- Critical paths minimum: {coverage.get('critical_paths_min_percent', 'n/a')}%",
            ]
        )
        if observed.get("artifact"):
            lines.append(f"- Observed artifact: {observed['artifact']}")
        if observed.get("line_coverage_percent") is not None:
            lines.append(f"- Observed line coverage: {round(float(observed['line_coverage_percent']), 2)}%")

    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        for finding in report["findings"]:
            finding_area = finding.get("area", finding.get("domain", "general"))
            lines.append(f"- [{finding['severity']}] {finding_area}: {finding['summary']}")
    else:
        lines.append("- No findings.")

    lines.extend(["", "## Recommendations", ""])
    if report["recommendations"]:
        for index, recommendation in enumerate(report["recommendations"], start=1):
            lines.append(f"{index}. [{recommendation['priority']}] {recommendation['action']}")
    else:
        lines.append("- No recommendations.")

    return "\n".join(lines) + "\n"


def ensure_parent(path: Path) -> None:
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def profile_output(
    profile: str,
    repo_path: Path,
    code_quality: dict[str, Any],
    ai_readiness: dict[str, Any],
    bug_triage: dict[str, Any],
    requirements_to_tests: dict[str, Any],
    project_codeguard_security: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    if profile == "code-quality":
        return code_quality, render_code_quality_markdown(code_quality)
    if profile == "ai-readiness":
        report = {
            "repository": repo_path.name,
            "revision": resolve_revision(repo_path),
            "profile": profile,
            "status": ai_readiness["status"],
            "checked_at": datetime.now(timezone.utc).isoformat(),
            **ai_readiness,
        }
        return report, render_area_markdown(report, "AI Readiness Report")
    if profile == "triage-bugs":
        report = {
            "repository": repo_path.name,
            "revision": resolve_revision(repo_path),
            "profile": profile,
            "status": bug_triage["status"],
            "checked_at": datetime.now(timezone.utc).isoformat(),
            **bug_triage,
        }
        return report, render_area_markdown(report, "Bug Triage Readiness Report")
    if profile == "requirements-to-tests":
        report = {
            "repository": repo_path.name,
            "revision": resolve_revision(repo_path),
            "profile": profile,
            "status": requirements_to_tests["status"],
            "checked_at": datetime.now(timezone.utc).isoformat(),
            **requirements_to_tests,
        }
        return report, render_area_markdown(report, "Requirements To Tests Report")
    if profile == "project-codeguard-security":
        report = {
            "repository": repo_path.name,
            "revision": resolve_revision(repo_path),
            "profile": profile,
            "status": project_codeguard_security["status"],
            "checked_at": datetime.now(timezone.utc).isoformat(),
            **project_codeguard_security,
        }
        return report, render_project_codeguard_markdown(report)

    report = build_org_standards_report(
        repo_path,
        code_quality,
        ai_readiness,
        bug_triage,
        requirements_to_tests,
        project_codeguard_security,
    )
    return report, render_org_markdown(report)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the shared AI SDLC standards evaluator.")
    parser.add_argument("--repo-path", default=".", help="Repository path to evaluate.")
    parser.add_argument("--output", help="Write normalized JSON report to this path.")
    parser.add_argument("--markdown-output", help="Write Markdown report to this path.")
    parser.add_argument("--include-optional", action="store_true", help="Run optional tools in addition to required ones.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve commands without executing them.")
    parser.add_argument("--timeout-seconds", type=int, default=300, help="Per-tool timeout.")
    parser.add_argument(
        "--profile",
        default="code-quality",
        choices=["code-quality", "ai-readiness", "triage-bugs", "requirements-to-tests", "project-codeguard-security", "org-standards"],
        help="Which standards profile to evaluate.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    repo_path = Path(args.repo_path).resolve()
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent

    registry = load_registry(repo_root)
    thresholds = load_quality_thresholds(repo_root)
    scan = scan_repo(repo_path)
    detected_languages, code_quality = evaluate_code_quality(
        repo_path,
        scan,
        registry,
        args.include_optional,
        args.dry_run,
        args.timeout_seconds,
    )
    ai_readiness = evaluate_ai_readiness(repo_path, scan, detected_languages)
    bug_triage = evaluate_bug_triage(repo_path, scan)
    requirements_to_tests = evaluate_requirements_to_tests(repo_path, scan, detected_languages, thresholds)
    project_codeguard_security = evaluate_project_codeguard_security(repo_path, repo_root, scan, detected_languages)
    report, markdown = profile_output(
        args.profile,
        repo_path,
        code_quality,
        ai_readiness,
        bug_triage,
        requirements_to_tests,
        project_codeguard_security,
    )

    if args.output:
        output_path = Path(args.output)
        ensure_parent(output_path)
        output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.markdown_output:
        markdown_path = Path(args.markdown_output)
        ensure_parent(markdown_path)
        markdown_path.write_text(markdown, encoding="utf-8")

    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
