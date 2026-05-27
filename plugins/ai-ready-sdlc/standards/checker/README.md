# Shared Checker Runner

This directory contains the first shared runner that Claude, Codex, and Augment can all call.

## Current Scope

- detect supported repository languages,
- select approved language toolchains,
- execute available tools,
- normalize outputs into a shared code quality report,
- evaluate AI readiness, bug triage readiness, and requirements-to-tests readiness,
- emit JSON and optional Markdown reports.

## Usage

```bash
python3 standards/checker/run.py \
  --repo-path . \
  --profile org-standards \
  --output reports/org-standards.json \
  --markdown-output reports/code-quality.md
```

## Notes

- Tool availability is checked at runtime.
- Missing selected tools are reported as `skipped`, not treated as runner crashes, but a required evaluation dimension with only skipped tools scores `not_run` and blocks an overall `pass`.
- The runner uses `standards/tooling/index.json` as its machine-readable registry and the YAML files under `standards/tooling/` as human-readable reference material.
- `org-standards` is the umbrella profile for the full shared engine.
- JavaScript and TypeScript repositories use package-root execution. The required matrix includes `eslint`, `tsc`, `npm audit`, `cyclomatic-complexity` for complexity metrics, and `fta-cli` for maintainability metrics.
