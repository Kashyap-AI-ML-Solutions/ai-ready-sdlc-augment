#!/usr/bin/env python3
"""Aggregate ADLC org standards reports into org-level metrics."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS_ORDER = {"fail": 0, "warn": 1, "pass": 2, "not_applicable": 3, "not_run": 4, "unknown": 5}
HIGH_SEVERITIES = {"critical", "high"}


def should_skip(path: Path) -> bool:
    return any(part in {".git", "node_modules", "dist", "__pycache__"} for part in path.parts)


def iter_report_paths(collection_repo: Path, include_all_runs: bool) -> list[Path]:
    paths: list[Path] = []
    for path in collection_repo.rglob("org-standards.json"):
        if should_skip(path):
            continue
        rel_parts = path.relative_to(collection_repo).parts
        if include_all_runs:
            paths.append(path)
        elif "latest" in rel_parts:
            paths.append(path)
        elif "runs" not in rel_parts:
            # Backward-compatible support for older flat collection layouts.
            paths.append(path)
    return sorted(paths)


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def repo_key(path: Path, collection_repo: Path, report: dict[str, Any]) -> str:
    rel_parts = path.relative_to(collection_repo).parts
    if "repos" in rel_parts:
        index = rel_parts.index("repos")
        if len(rel_parts) > index + 2:
            return f"{rel_parts[index + 1]}/{rel_parts[index + 2]}"
    return str(report.get("repository") or path.parent.name)


def get_area(report: dict[str, Any], area: str) -> dict[str, Any]:
    value = report.get("areas", {}).get(area, {})
    return value if isinstance(value, dict) else {}


def status_counts(reports: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(report.get("overall_status", "unknown")) for report in reports))


def coverage_info(report: dict[str, Any]) -> dict[str, Any]:
    requirements = get_area(report, "requirements_to_tests")
    observed = requirements.get("coverage_observed", {}) if isinstance(requirements.get("coverage_observed"), dict) else {}
    policy = requirements.get("coverage_policy", {}) if isinstance(requirements.get("coverage_policy"), dict) else {}
    minimum = policy.get("repository_min_percent", 80)
    percentage = observed.get("line_coverage_percent")
    artifact = observed.get("artifact")

    if percentage is None:
        return {
            "status": "missing",
            "artifact": artifact,
            "line_coverage_percent": None,
            "minimum": minimum,
        }

    try:
        percent_value = float(percentage)
        minimum_value = float(minimum)
    except (TypeError, ValueError):
        return {
            "status": "unknown",
            "artifact": artifact,
            "line_coverage_percent": percentage,
            "minimum": minimum,
        }

    return {
        "status": "pass" if percent_value >= minimum_value else "below_policy",
        "artifact": artifact,
        "line_coverage_percent": round(percent_value, 2),
        "minimum": minimum_value,
    }


def security_findings(report: dict[str, Any]) -> list[dict[str, Any]]:
    codeguard = get_area(report, "project_codeguard_security")
    findings = codeguard.get("findings", [])
    return [item for item in findings if isinstance(item, dict)]


def high_security_count(report: dict[str, Any]) -> int:
    return sum(1 for finding in security_findings(report) if str(finding.get("severity", "")).lower() in HIGH_SEVERITIES)


def area_problem_count(report: dict[str, Any]) -> int:
    statuses = report.get("area_statuses", {})
    if not isinstance(statuses, dict):
        return 0
    return sum(1 for status in statuses.values() if status in {"fail", "warn"})


def recommendation_priority_counts(report: dict[str, Any]) -> Counter[str]:
    recommendations = report.get("recommendations", [])
    counts: Counter[str] = Counter()
    for recommendation in recommendations:
        if isinstance(recommendation, dict):
            counts[str(recommendation.get("priority", "unknown"))] += 1
    return counts


def code_quality_dimensions(report: dict[str, Any]) -> dict[str, str]:
    code_quality = get_area(report, "code_quality")
    dimensions = code_quality.get("dimension_scores", {})
    if not isinstance(dimensions, dict):
        return {}
    return {str(key): str(value) for key, value in dimensions.items()}


def tool_metrics(report: dict[str, Any], tool_name: str) -> dict[str, Any]:
    code_quality = get_area(report, "code_quality")
    for run in code_quality.get("tools_run", []):
        if not isinstance(run, dict) or run.get("tool") != tool_name:
            continue
        metrics = run.get("metrics", {})
        return metrics if isinstance(metrics, dict) else {}
    return {}


def tool_install_gaps(report: dict[str, Any]) -> list[str]:
    code_quality = get_area(report, "code_quality")
    gaps: list[str] = []
    for run in code_quality.get("tools_run", []):
        if not isinstance(run, dict):
            continue
        if run.get("status") == "skipped":
            language = run.get("language", "unknown")
            tool = run.get("tool", "unknown")
            gaps.append(f"{language}:{tool}")
    return gaps


def repo_summary(path: Path, collection_repo: Path, report: dict[str, Any]) -> dict[str, Any]:
    coverage = coverage_info(report)
    security = security_findings(report)
    dimensions = code_quality_dimensions(report)
    priorities = recommendation_priority_counts(report)
    high_security = high_security_count(report)
    total_security = len(security)
    problems = area_problem_count(report)
    reported_overall = str(report.get("overall_status", "unknown"))
    required_not_run = any(
        dimensions.get(dimension) == "not_run"
        for dimension in ("code_quality", "complexity", "security", "maintainability")
    )
    overall = "fail" if required_not_run and reported_overall != "fail" else reported_overall

    return {
        "key": repo_key(path, collection_repo, report),
        "repository": report.get("repository", ""),
        "revision": report.get("revision", "unknown"),
        "report_path": str(path.relative_to(collection_repo)),
        "overall_status": overall,
        "reported_overall_status": reported_overall,
        "area_problem_count": problems,
        "coverage": coverage,
        "security_findings": total_security,
        "high_or_critical_security_findings": high_security,
        "complexity": dimensions.get("complexity", "not_run"),
        "maintainability": dimensions.get("maintainability", "not_run"),
        "complexity_metrics": tool_metrics(report, "cyclomatic-complexity"),
        "maintainability_metrics": tool_metrics(report, "fta-cli"),
        "recommendation_counts": dict(priorities),
        "recommendation_total": sum(priorities.values()),
        "tool_install_gaps": tool_install_gaps(report),
    }


def pct(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((count / total) * 100.0, 2)


def aggregate(summaries: list[dict[str, Any]], security_issue_threshold: int) -> dict[str, Any]:
    total = len(summaries)

    coverage_meeting = [item for item in summaries if item["coverage"]["status"] == "pass"]
    coverage_missing = [item for item in summaries if item["coverage"]["status"] == "missing"]
    coverage_below = [item for item in summaries if item["coverage"]["status"] == "below_policy"]
    high_security = [item for item in summaries if item["high_or_critical_security_findings"] > 0]
    too_many_security = [item for item in summaries if item["security_findings"] >= security_issue_threshold]
    complexity_risk = [item for item in summaries if item["complexity"] in {"fail", "warn"}]
    maintainability_pass = [item for item in summaries if item["maintainability"] == "pass"]
    complexity_not_run = [item for item in summaries if item["complexity"] == "not_run"]
    maintainability_not_run = [item for item in summaries if item["maintainability"] == "not_run"]
    complexity_values = [
        item["complexity_metrics"].get("max_function_complexity")
        for item in summaries
        if isinstance(item.get("complexity_metrics"), dict)
        and item["complexity_metrics"].get("max_function_complexity") is not None
    ]
    maintainability_values = [
        item["maintainability_metrics"].get("max_fta_score")
        for item in summaries
        if isinstance(item.get("maintainability_metrics"), dict)
        and item["maintainability_metrics"].get("max_fta_score") is not None
    ]

    immediate_attention = sorted(
        {item["key"]: item for item in high_security + too_many_security}.values(),
        key=lambda item: (-item["high_or_critical_security_findings"], -item["security_findings"], item["key"]),
    )
    large_gaps = [
        item
        for item in summaries
        if item["overall_status"] == "fail"
        or item["coverage"]["status"] == "below_policy"
        or item["area_problem_count"] >= 3
    ]
    large_gap_keys = {item["key"] for item in large_gaps}
    small_gaps = [
        item
        for item in summaries
        if item["overall_status"] == "warn"
        and item["high_or_critical_security_findings"] == 0
        and item["recommendation_total"] <= 3
        and item["key"] not in large_gap_keys
    ]

    tool_counter: Counter[str] = Counter()
    recommendation_counter: Counter[str] = Counter()
    for item in summaries:
        tool_counter.update(item["tool_install_gaps"])
        for priority, count in item["recommendation_counts"].items():
            recommendation_counter[priority] += int(count)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_repositories": total,
        "overall_status_counts": dict(Counter(item["overall_status"] for item in summaries)),
        "coverage": {
            "meeting_policy_count": len(coverage_meeting),
            "meeting_policy_percent": pct(len(coverage_meeting), total),
            "missing_artifact_count": len(coverage_missing),
            "below_policy_count": len(coverage_below),
            "meeting_policy_repositories": [item["key"] for item in coverage_meeting],
            "missing_artifact_repositories": [item["key"] for item in coverage_missing],
            "below_policy_repositories": [item["key"] for item in coverage_below],
        },
        "security": {
            "high_or_critical_count": len(high_security),
            "high_or_critical_percent": pct(len(high_security), total),
            "too_many_security_issues_count": len(too_many_security),
            "high_or_critical_repositories": [item["key"] for item in high_security],
            "too_many_security_issue_repositories": [item["key"] for item in too_many_security],
        },
        "gaps": {
            "large_gap_count": len(large_gaps),
            "small_gap_count": len(small_gaps),
            "immediate_attention_count": len(immediate_attention),
            "large_gap_repositories": [item["key"] for item in large_gaps],
            "small_gap_repositories": [item["key"] for item in small_gaps],
            "immediate_attention_repositories": [item["key"] for item in immediate_attention],
        },
        "complexity": {
            "risk_count": len(complexity_risk),
            "risk_repositories": [item["key"] for item in complexity_risk],
            "not_run_count": len(complexity_not_run),
            "not_run_repositories": [item["key"] for item in complexity_not_run],
            "max_function_complexity": max(complexity_values) if complexity_values else None,
        },
        "maintainability": {
            "pass_count": len(maintainability_pass),
            "pass_repositories": [item["key"] for item in maintainability_pass],
            "not_run_count": len(maintainability_not_run),
            "not_run_repositories": [item["key"] for item in maintainability_not_run],
            "max_fta_score": max(maintainability_values) if maintainability_values else None,
        },
        "tool_installation_gaps": dict(tool_counter.most_common()),
        "recommendation_priority_counts": dict(recommendation_counter),
        "repositories": sorted(summaries, key=lambda item: (STATUS_ORDER.get(item["overall_status"], 99), item["key"])),
    }


def render_markdown(metrics: dict[str, Any]) -> str:
    lines = [
        "# ADLC Organization Metrics",
        "",
        "## Summary",
        "",
        f"- Generated at: {metrics['generated_at']}",
        f"- Total repositories: {metrics['total_repositories']}",
        f"- Coverage policy met: {metrics['coverage']['meeting_policy_count']} ({metrics['coverage']['meeting_policy_percent']}%)",
        f"- High or critical security repos: {metrics['security']['high_or_critical_count']} ({metrics['security']['high_or_critical_percent']}%)",
        f"- Large gap repos: {metrics['gaps']['large_gap_count']}",
        f"- Small gap repos: {metrics['gaps']['small_gap_count']}",
        f"- Immediate attention repos: {metrics['gaps']['immediate_attention_count']}",
        "",
        "## Overall Status Counts",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]

    for status, count in sorted(metrics["overall_status_counts"].items()):
        lines.append(f"| {status} | {count} |")

    lines.extend(["", "## Immediate Attention", ""])
    if metrics["gaps"]["immediate_attention_repositories"]:
        for repo in metrics["gaps"]["immediate_attention_repositories"]:
            lines.append(f"- {repo}")
    else:
        lines.append("- None.")

    lines.extend(["", "## Coverage", ""])
    lines.append(f"- Missing coverage artifacts: {metrics['coverage']['missing_artifact_count']}")
    lines.append(f"- Below policy: {metrics['coverage']['below_policy_count']}")
    if metrics["coverage"]["below_policy_repositories"]:
        lines.append("- Below policy repositories: " + ", ".join(metrics["coverage"]["below_policy_repositories"]))
    if metrics["coverage"]["missing_artifact_repositories"]:
        lines.append("- Missing artifact repositories: " + ", ".join(metrics["coverage"]["missing_artifact_repositories"]))

    lines.extend(["", "## Complexity And Maintainability", ""])
    lines.append(f"- Complexity risk repos: {metrics['complexity']['risk_count']}")
    lines.append(f"- Complexity not-run repos: {metrics['complexity'].get('not_run_count', 0)}")
    if metrics["complexity"].get("max_function_complexity") is not None:
        lines.append(f"- Max function cyclomatic complexity: {metrics['complexity']['max_function_complexity']}")
    lines.append(f"- Maintainability pass repos: {metrics['maintainability']['pass_count']}")
    lines.append(f"- Maintainability not-run repos: {metrics['maintainability'].get('not_run_count', 0)}")
    if metrics["maintainability"].get("max_fta_score") is not None:
        lines.append(f"- Max FTA maintainability score: {metrics['maintainability']['max_fta_score']}")

    lines.extend(["", "## Tool Installation Gaps", ""])
    if metrics["tool_installation_gaps"]:
        lines.extend(["| Tool | Repos |", "| --- | ---: |"])
        for tool, count in metrics["tool_installation_gaps"].items():
            lines.append(f"| {tool} | {count} |")
    else:
        lines.append("- None.")

    lines.extend(["", "## Repository Table", ""])
    lines.extend(
        [
            "| Repository | Status | Coverage | Security findings | High security | Complexity | Maintainability | Recommendations |",
            "| --- | --- | --- | ---: | ---: | --- | --- | ---: |",
        ]
    )
    for repo in metrics["repositories"]:
        coverage = repo["coverage"]
        coverage_text = coverage["status"]
        if coverage["line_coverage_percent"] is not None:
            coverage_text = f"{coverage_text} ({coverage['line_coverage_percent']}%)"
        lines.append(
            "| {key} | {status} | {coverage} | {security} | {high_security} | {complexity} | {maintainability} | {recommendations} |".format(
                key=repo["key"],
                status=repo["overall_status"],
                coverage=coverage_text,
                security=repo["security_findings"],
                high_security=repo["high_or_critical_security_findings"],
                complexity=repo["complexity"],
                maintainability=repo["maintainability"],
                recommendations=repo["recommendation_total"],
            )
        )

    return "\n".join(lines) + "\n"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection-repo", default=".", help="Path to the ADLC org status collection repo.")
    parser.add_argument("--output", default="metrics/org-metrics.json", help="JSON metrics output path.")
    parser.add_argument("--markdown-output", default="metrics/org-metrics.md", help="Markdown metrics output path.")
    parser.add_argument("--include-all-runs", action="store_true", help="Aggregate every org-standards.json instead of latest snapshots.")
    parser.add_argument("--security-issue-threshold", type=int, default=5, help="Total security findings threshold for too-many-security-issues.")
    args = parser.parse_args()

    collection_repo = Path(args.collection_repo).expanduser().resolve()
    report_paths = iter_report_paths(collection_repo, include_all_runs=args.include_all_runs)
    summaries: list[dict[str, Any]] = []
    skipped: list[str] = []

    for path in report_paths:
        report = load_json(path)
        if report is None:
            skipped.append(str(path.relative_to(collection_repo)))
            continue
        summaries.append(repo_summary(path, collection_repo, report))

    metrics = aggregate(summaries, security_issue_threshold=args.security_issue_threshold)
    if skipped:
        metrics["skipped_reports"] = skipped

    output = (collection_repo / args.output).resolve()
    markdown_output = (collection_repo / args.markdown_output).resolve()
    ensure_parent(output)
    ensure_parent(markdown_output)
    output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    markdown_output.write_text(render_markdown(metrics), encoding="utf-8")

    print(f"Aggregated {len(summaries)} reports into {output}")
    print(f"Wrote markdown metrics to {markdown_output}")
    if skipped:
        print(f"Skipped {len(skipped)} unreadable reports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
