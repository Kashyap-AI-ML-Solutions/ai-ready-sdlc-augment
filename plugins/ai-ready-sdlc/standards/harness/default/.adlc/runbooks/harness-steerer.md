# Harness Steerer Runbook

Use this runbook when turning a request into executable ADLC work.

## Steps

1. Read `.adlc/harness.yaml`.
2. Read `.adlc/lifecycle.json` and `.adlc/status.md`.
3. Identify whether the task is a feature, bug fix, unit-test expansion, remediation, or orchestration task.
4. Create a platform-independent plan directory under `.adlc/plans/<YYYY-MM-DD>_<task-slug>/`.
5. Copy the closest blueprint from `.adlc/blueprints/` into the plan context.
6. Fill in acceptance criteria, validation commands, tests, evals, and proof requirements.
7. Create bounded work items in the plan directory.
8. Establish a baseline or failing signal when practical.
9. Implement one bounded work item.
10. Run validation.
11. If validation fails, repair within the same bounded scope and retry up to the configured limit.
12. Write proof and update status and lifecycle.

## Completion Rule

Do not call the task complete until there is a plan under `.adlc/plans/`, evidence in `.adlc/proofs/`, and `.adlc/status.md` has an updated handoff.
