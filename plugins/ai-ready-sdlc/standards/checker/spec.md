# Standards Checker Specification

## Purpose

The standards checker evaluates repositories, pull requests, issues, and test plans against the AI-ready SDLC standard.

## Candidate Delivery Modes

- CLI for local and CI usage
- MCP server for assistant tool integration
- Shared backend service for organization-wide reporting

## Minimum Checks

### Repository

- Detect presence of the AI capability manifest when AI functionality exists.
- Detect standards templates or equivalent required artifacts for high-risk changes.
- Detect observability instrumentation patterns or configuration references.
- Evaluate repository readiness for bug triage and requirements-to-tests coverage.

### Pull Request

- Verify passing tests.
- Verify presence of an AI review summary artifact.
- Verify evidence of human review before merge.
- Run code quality evaluation for relevant languages when configured.

### Issue

- Verify required triage fields are present.
- Verify AI confidence is within valid range when present.

### Test Plan

- Verify happy path, edge case, and negative path coverage.
- Verify mapping from requirements to tests exists.

### Code Quality

- Detect repository languages.
- Select the relevant evaluation tools from the organization tool matrix.
- Run or request code quality, complexity, security, style, and maintainability checks.
- Normalize outputs into a shared report contract.

### Project CodeGuard Security

- Use the pinned upstream Project CodeGuard version approved in this repo.
- Read the normalized generated Project CodeGuard bundle for the current pinned version when it is available.
- Evaluate repositories for secret handling, cryptography and TLS safety, dynamic execution and injection risks, supply-chain and CI risks, and cloud or IaC risks where relevant.
- Normalize findings into a dedicated Project CodeGuard report contract.
- Include the Project CodeGuard lane in umbrella `org-standards` results.

## Output Contract

The checker should return:

- `overall_status`
- `findings`
- `evidence`
- `suggested_fixes`
- `checked_at`

For code quality evaluation, the checker should also support:

- `languages_detected`
- `tools_run`
- `dimension_scores`
- `recommendations`
- `report_location`

For Project CodeGuard security evaluation, the checker should also support:

- `profile`
- `domains_checked`
- `upstream`
- `upstream.bundle_summary`
- `files_scanned`
- `recommendations`

For full organization standards evaluation, the checker should also support:

- `areas`
- `area_statuses`
- `overall_status`
- `checked_at`

## Shared Rule

Claude, Codex, and Augment adapters should call the same checker logic or the same output contract so policy enforcement stays aligned across platforms.
