# Coverage Standard

## Purpose

This standard defines the minimum test coverage expectations that the shared standards runner should enforce or report.

## Coverage Thresholds

- Repository-wide line coverage should be at least 80%.
- Changed-lines coverage should be at least 90% when diff-aware coverage tooling is available.
- Critical paths should target at least 95% coverage or have a documented exception.

## Operational Rule

- If a repository has executable code but no coverage artifact, the standards workflow should flag the gap.
- If a repository coverage artifact exists and repository-wide coverage is below 80%, the standards workflow should fail the coverage check.
- Changed-lines and critical-path coverage may be reported as policy targets when the current run does not have diff-aware or path-scoped coverage inputs.
