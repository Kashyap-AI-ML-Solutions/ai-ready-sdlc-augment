---
workflow: adlc-default
version: 0.1.0
workspace:
  harness_root: .adlc
  status_file: .adlc/status.md
  proof_dir: .adlc/proofs
  report_dir: reports
agent:
  max_repair_loops: 3
  requires_proof: true
  requires_standards_report: true
---

# ADLC Workflow

Use this workflow as the repository-owned contract for agentic development.

For every substantial task:

1. Read `.adlc/harness.yaml` and `.adlc/status.md`.
2. Select the closest blueprint from `.adlc/blueprints/`.
3. Convert the request into bounded work items under `.adlc/work-items/`.
4. Establish a failing or baseline validation signal before implementation when possible.
5. Implement one bounded work item at a time.
6. Run focused tests, quality checks, and the relevant ADLC standards profile.
7. Write proof under `.adlc/proofs/`.
8. Update `.adlc/status.md` with what changed, what passed, what failed, and what remains.

The human steers intent and approves judgment-heavy decisions. Agents execute bounded work, repair failures, and leave clear evidence.
