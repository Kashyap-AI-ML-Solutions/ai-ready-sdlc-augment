---
name: repo-quality-orchestrator
description: Coordinate language-aware code quality evaluation across the repository.
---

Use this skill when a repository needs a language-aware code quality evaluation.

Workflow:

1. Detect repository languages from file structure and build metadata.
2. Read the corresponding tool matrix under `../../standards/tooling/`.
3. Run or request the appropriate evaluators.
4. Normalize findings into the shared code quality report format.
5. Hand the result to the code quality reviewer or remediation planner when deeper reporting is needed.
