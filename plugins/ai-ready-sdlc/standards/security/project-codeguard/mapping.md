# Project CodeGuard Mapping

## Intent

This mapping explains how Project CodeGuard concepts map into the `AI_SDLC_Standard` shared core.

## Shared-Core Mapping

| Project CodeGuard area | AI_SDLC_Standard lane | Notes |
| --- | --- | --- |
| Secret handling | `project-codeguard-security` | Includes hardcoded credentials and unsafe secret storage patterns. |
| Cryptography and TLS | `project-codeguard-security` | Includes weak crypto, certificate handling, and disabled verification. |
| Injection and dynamic execution | `project-codeguard-security` | Includes `eval`, shell execution, and other dynamic execution patterns. |
| Supply chain and CI | `project-codeguard-security` | Includes workflow hardening and dependency or action pinning guidance. |
| Cloud, IaC, and container security | `project-codeguard-security` | Includes privileged container and deployment settings where relevant. |
| Repo-wide quality posture | `code-quality` | Remains separate from the dedicated security lane. |
| Umbrella repo assessment | `org-standards` | Includes both code quality and Project CodeGuard security. |

## Cisco Overlay Intent

Cisco-specific overlays should:

- preserve upstream rule intent,
- document where we raise or lower severity,
- add internal secure-default expectations,
- remain separately versioned from upstream content.
