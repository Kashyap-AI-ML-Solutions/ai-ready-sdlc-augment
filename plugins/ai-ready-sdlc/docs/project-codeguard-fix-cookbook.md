# Project CodeGuard Fix Cookbook

## Hardcoded Credentials

Preferred fix:

- move secrets into environment variables or a managed secret store
- remove committed values from code and config
- rotate any exposed credentials

## Disabled TLS Verification

Preferred fix:

- re-enable certificate verification
- use a trusted CA bundle
- document any local-development-only exceptions explicitly

## Weak Cryptography

Preferred fix:

- replace weak algorithms like MD5, SHA-1, DES, or RC4
- use current approved libraries and algorithms
- note any backward-compatibility implications

## Dynamic Execution

Preferred fix:

- remove `eval`, raw shell execution, or equivalent dynamic execution where possible
- replace with explicit command allowlists, safer parsing, or typed interfaces

## Unpinned GitHub Actions

Preferred fix:

- pin actions to immutable commit SHAs or approved version tags
- review workflow permissions and third-party action trust

## Privileged Kubernetes Or Deployment Settings

Preferred fix:

- move to least-privilege defaults
- avoid privileged containers unless there is a documented exception
- review `allowPrivilegeEscalation`, `hostNetwork`, and related settings
