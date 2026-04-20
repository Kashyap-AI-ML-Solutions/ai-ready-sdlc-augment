# Project CodeGuard Rule Mapping

## Upstream To Shared-Core Mapping

| Shared domain | What we check in Phase 1 | Example finding types |
| --- | --- | --- |
| `secret_management` | hardcoded secrets and private keys | tokens, passwords, embedded private keys |
| `crypto_tls` | weak crypto and disabled verification | `md5`, `sha1`, `verify=False`, `InsecureSkipVerify: true` |
| `input_validation_and_injection` | dynamic execution patterns | `eval`, `exec`, shell execution |
| `supply_chain_and_ci` | CI workflow hygiene | unpinned GitHub Actions |
| `cloud_iac_and_container` | risky deployment settings | privileged pods, host networking |

## Shared-Core Policy Mapping

- dedicated security profile: `project-codeguard-security`
- umbrella standards profile: `org-standards`
- pinned upstream reference: `third_party/project-codeguard/`
- normalized generated bundle: `standards/security/project-codeguard/generated/current-bundle.json`

## Cisco Overlay Direction

Later phases can add Cisco-specific overlays for:

- internal secure-defaults expectations
- severity adjustments with justification
- repo-class-specific findings and fix text
