# AI-Ready SDLC Standard

## Scope

This document is the neutral source of truth for the organization's AI-ready SDLC requirements.

It defines the standards that downstream Claude, Codex, and Augment packages must reflect without changing the meaning of the policy.

## Standard Areas

### Code Review

- Every material code change should have passing tests, a human reviewer, and an AI review summary.
- AI review outputs should call out likely bugs, security or privacy concerns, test gaps, and performance risks.

### Code Quality Evaluation

- Repositories should support automated code quality evaluation using language-appropriate tooling.
- Code quality evaluation should cover code quality, complexity, security, style, and maintainability where language tooling supports those dimensions.
- Teams should be able to run the same evaluation interactively from Claude, Codex, or Augment and automatically from CI.
- Evaluation outputs should be normalized into a shared report format so repositories using different languages can still be compared at the organization level.

### Project CodeGuard Security Review

- Repositories should support a Project CodeGuard-aligned security review lane as part of the shared standards core.
- Security review should cover secret handling, cryptography and TLS practices, injection and dynamic execution risks, supply-chain and CI security, and cloud or IaC security when relevant.
- Teams should be able to run the same security review interactively from Claude, Codex, or Augment and automatically from CI.
- Security outputs should be normalized into a shared report format and rolled into the umbrella `run-org-standards` workflow.

### Bug Triage

- New bugs should be enriched with severity, component, customer impact, probable cause, and suggested owner.
- AI triage should remain reviewable and overrideable by humans.

### Test Plan to Test Scripts

- High-risk changes should map to a written test plan before completion.
- AI assistance should be used to generate or validate test cases against that plan.

### AI Capability Manifest

- Repositories with production AI behavior should declare models, tools, datasets, guardrails, and observability endpoints in a manifest.

### Observability

- AI-assisted workflows and runtime AI systems should emit traceable telemetry, including at least request correlation, latency, status, and usage where available.

### Automation Workflow

- The organization should provide automation that can run standards checks and quality evaluations without relying only on manual developer invocation.
- Interactive plugin workflows and automated CI workflows should use the same standards definitions and report contracts wherever possible.

## Adapter Rule

Claude, Codex, and Augment packages may reorganize or rephrase this policy for their platform mechanics, but they should not fork the required standard areas or weaken the required controls.
