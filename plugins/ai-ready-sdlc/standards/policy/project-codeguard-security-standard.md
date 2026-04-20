# Project CodeGuard Security Standard

## Purpose

This document defines how `AI_SDLC_Standard` integrates Project CodeGuard into the shared standards core.

## Standard Requirements

- The repository standard must pin one approved upstream Project CodeGuard release at a time.
- Project CodeGuard security checks must be available through the shared checker and through the Claude, Codex, and Augment plugin surfaces.
- The security lane must roll into the umbrella `run-org-standards` workflow.
- Findings must be normalized into a shared security report format so results are comparable across repositories.

## Minimum Coverage Areas

- secret management and credential handling
- cryptography and TLS practices
- dynamic execution and injection risks
- supply chain and CI security
- cloud, IaC, and container security when relevant

## Versioning Rule

- Do not follow upstream `latest` during repository checks.
- Pin an approved release in `third_party/project-codeguard/`.
- Validate new upstream releases on the demo repos before promoting them as the new default.

## Adapter Rule

Claude, Codex, and Augment may expose different commands, skills, or agent entry points, but they must call the same underlying security lane or the same output contract so policy does not drift between platforms.
