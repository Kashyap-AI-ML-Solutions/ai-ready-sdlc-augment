# Validation Loop

Use this validation loop for feature, bug, unit-test, and remediation work.

## Baseline

- Record the current revision.
- Run the narrowest relevant test or quality command.
- Capture failure output or baseline output.
- Record the baseline in the active `.adlc/plans/<run>/tests-and-evals.md`.

## Repair Loop

Repeat up to three times:

1. Make the smallest scoped change needed.
2. Run the focused validation command.
3. If it fails, write the failure context into `.adlc/status.md`.
4. Repair only the bounded work item unless the blueprint is wrong.

## Final Gates

- Run focused tests.
- Run relevant quality or security checks.
- Run `org-standards` when the change is substantial.
- Write proof with command output summaries and residual risks.
- Update `.adlc/lifecycle.json` to `Report` when all gates have passed.
