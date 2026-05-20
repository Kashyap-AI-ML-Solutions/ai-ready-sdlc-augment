# Project CodeGuard Integration Plan

Date: 2026-04-15

## Objective

Extend `AI_SDLC_Standard` so the shared standards core also enforces and reports on Project CodeGuard security guidance across Claude, Codex, and Augment, without creating policy drift between platforms.

This integration should:

- keep `AI_SDLC_Standard` as the single source of truth for our org-wide agentic SDLC standard,
- add a first-class security lane powered by Project CodeGuard,
- expose the same security workflows to Claude, Codex, and Augment users,
- support repeatable demos on:
  - `webex-messaging-mcp-server`
  - `cdr-dedup`
  - `smi-cluster-deployer`

## Research Summary

Project CodeGuard is an open-source, model-agnostic security framework from CoSAI/OASIS that embeds secure-by-default skills and rules into AI coding workflows. The repository contains:

- a Claude plugin surface via `.claude-plugin/`,
- Codex-compatible skills under `skills/`,
- unified security rule sources under `sources/`,
- conversion tooling under `src/convert_to_ide_formats.py`,
- validators such as `validate_unified_rules.py` and `validate_versions.py`,
- installation and customization docs under `docs/`.

Important release signals:

- latest release observed: `v1.3.1` on March 11, 2026,
- `v1.3.1` is described as packaging/tooling only and explicitly adds `ide-rules-codex.zip` and `ide-rules-opencode.zip`,
- `v1.3.0` on January 30, 2026 marks the transition into the `cosai-oasis` repository.

Important product signals:

- Project CodeGuard already supports Claude Code installation through `/plugin marketplace add cosai-oasis/project-codeguard` and `/plugin install codeguard-security@project-codeguard`,
- Project CodeGuard already supports Codex via the `software-security` skill,
- Project CodeGuard supports custom source folders and tagged rule builds, which is useful for Cisco-specific overlays.

## Recommendation

Do not treat Project CodeGuard as a separate sidecar tool that teams install manually in parallel with our standard.

Instead:

1. Integrate Project CodeGuard into the `AI_SDLC_Standard` shared core as the official security lane.
2. Pin an upstream CodeGuard version in our repo.
3. Wrap that pinned content with our own checker, reporting, workflow, and demo docs.
4. Expose the same security lane through our Claude, Codex, and Augment plugins.

This keeps:

- one standards product,
- one rollout motion,
- one umbrella workflow,
- one reporting shape,
- and no Claude/Codex/Augment policy drift.

## How To Integrate Project CodeGuard Into Our Standards Core

### 1. Add a pinned upstream dependency model

Create a pinned CodeGuard integration area inside `AI_SDLC_Standard`:

```text
third_party/
  project-codeguard/
    v1.3.1/
      upstream/
      metadata.json
standards/
  security/
    project-codeguard/
      mapping.md
      policy.md
      version-policy.md
```

Recommended rule:

- pin to `v1.3.1` first,
- do not depend on live remote fetches during repo checks,
- track the pinned release in a metadata file containing:
  - upstream repo URL,
  - pinned release tag,
  - release date,
  - included assets,
  - sync date,
  - known local overrides.

### 2. Add a new shared standards lane

Extend the shared checker so `run-org-standards` includes a new lane:

- `project-codeguard-security`

This lane should assess:

- hardcoded credentials and secret handling,
- cryptography and certificate practices,
- input validation and injection prevention,
- authentication and authorization patterns,
- data protection and logging practices,
- supply chain / CI / dependency security,
- cloud / IaC / container / Kubernetes security when relevant.

### 3. Normalize CodeGuard findings into our report model

Add new shared artifacts:

```text
standards/schemas/project_codeguard_report.schema.yaml
standards/templates/project_codeguard_report.md
standards/policy/project-codeguard-security-standard.md
```

Reporting should include:

- overall security status,
- applicable CodeGuard domains,
- matched rule families,
- findings by severity,
- fix recommendations,
- confidence,
- repo-specific next steps,
- whether the result should fail, warn, or pass.

### 4. Add a Cisco overlay model

Project CodeGuard supports custom sources. We should use that pattern conceptually, but keep our Cisco overlay separate from upstream core content.

Recommended approach:

- upstream CodeGuard rules remain intact,
- Cisco-specific overlays live in our repo,
- overlays map to:
  - Cisco security policies,
  - internal repo hygiene expectations,
  - AI-agent rollout expectations,
  - secure defaults for common internal stacks.

Suggested path:

```text
standards/security/project-codeguard/cisco-overlays/
```

### 5. Keep CodeGuard inside the umbrella workflow

`run-org-standards` should become:

- code quality
- AI readiness
- bug triage readiness
- requirements-to-tests readiness
- coverage policy
- Project CodeGuard security review
- combined standards reporting

That is the right operator experience for teams.

## New Shared-Core Deliverables

### Policies and mappings

- `standards/policy/project-codeguard-security-standard.md`
- `standards/security/project-codeguard/mapping.md`
- `standards/security/project-codeguard/cisco-overlays/`

### Schemas and templates

- `standards/schemas/project_codeguard_report.schema.yaml`
- `standards/templates/project_codeguard_report.md`

### Checker and runner work

- extend `standards/checker/run.py` with a `project-codeguard-security` profile
- include the lane in `org-standards`
- emit:
  - `reports/project-codeguard-security.json`
  - `reports/project-codeguard-security.md`

### Sync and validation tooling

- `scripts/sync-project-codeguard.py`
- `scripts/build-project-codeguard-bundle.py`
- `scripts/run-project-codeguard-check.sh`
- `scripts/update-project-codeguard-version.py`

## Release Update Process For New Project CodeGuard Versions

We should make Project CodeGuard updates deliberate and repeatable, not ad hoc.

### Update trigger

Check for upstream releases on:

- `https://github.com/cosai-oasis/project-codeguard/releases`

Recommended trigger points:

- before a major internal demo,
- on a regular maintenance cadence,
- when an upstream release contains security-rule updates we want quickly,
- when we need new IDE / agent packaging support from upstream.

### Standard update flow

For every new upstream release:

1. Review the release notes and assets.
2. Decide whether to:
   - adopt immediately,
   - stage in a preview branch,
   - or defer.
3. Update our pinned version metadata.
4. Sync the upstream content into:
   - `third_party/project-codeguard/<version>/upstream/`
5. Rebuild our internal CodeGuard bundle and rule mappings.
6. Run validation on our 3 demo repos:
   - `webex-messaging-mcp-server`
   - `cdr-dedup`
   - `smi-cluster-deployer`
7. Compare:
   - new findings,
   - removed findings,
   - severity shifts,
   - false-positive changes.
8. Update our docs, fix cookbook, and demo playbook if behavior changed.
9. Promote the new version into the default `AI_SDLC_Standard` release only after validation passes.

### Required scripts and metadata for updates

The integration should include an explicit update path:

- `scripts/update-project-codeguard-version.py`
  - accepts a target upstream version,
  - updates `third_party/project-codeguard/<version>/metadata.json`,
  - refreshes the current-version pointer used by our checker,
  - records release date, source URL, sync date, and local overlay version.
- `scripts/sync-project-codeguard.py`
  - syncs the pinned upstream artifacts into our repo,
  - validates expected folders and rule files,
  - fails if the upstream package shape changes unexpectedly.
- `scripts/build-project-codeguard-bundle.py`
  - prepares the normalized internal bundle our shared checker will consume.

### Version policy

Recommended version policy:

- pin one approved upstream release at a time,
- never auto-follow `latest` in repo checks,
- keep at least one prior pinned version available for rollback comparison,
- document local Cisco overlays separately from upstream content,
- require demo-repo validation before changing the default pinned version.

### README and operator docs for updates

The root README and Project CodeGuard docs should include:

- where to check for new upstream releases,
- the exact update command sequence,
- what validation must be run after an update,
- how to roll back to the prior pinned version,
- how to explain version changes in release notes to plugin users.

### Demo-readiness gate for updates

A new upstream Project CodeGuard version should not become our default until:

- the shared checker passes with the new pinned content,
- Claude, Codex, and Augment surfaces all still expose the expected workflows,
- the 3 demo repos produce understandable and defensible output,
- any materially new findings have corresponding remediation guidance.

## New Claude Plugin Support

### New commands

- `/ai-ready-sdlc:review-project-codeguard-security`
- `/ai-ready-sdlc:fix-project-codeguard-findings`
- `/ai-ready-sdlc:explain-project-codeguard-findings`

The fix command is gated by the ADLC conductor. It should call `scripts/steer-adlc-harness.py --task-type remediation --source-report reports/project-codeguard-security.json` and create `.adlc/plans/<run>/` before any code edits.

### New agents

- `project-codeguard-security-reviewer`
- `project-codeguard-remediation-planner`

### New skills

- `project-codeguard-security`
- `project-codeguard-fix-patterns`
- `project-codeguard-rule-mapper`

### Claude docs changes

Update the Claude plugin docs so users understand:

- CodeGuard is part of the umbrella standards flow,
- they can run the dedicated security command when needed,
- the Claude package still uses `Claude Opus 4.6` / `opus` tier with high effort.

## New Codex Plugin Support

### New skills

- `project-codeguard-security`
- `project-codeguard-fix-patterns`
- `project-codeguard-rule-mapper`

### New workflow prompts

- `Use the ai-ready-sdlc plugin and review Project CodeGuard security on this repository.`
- `Use the ai-ready-sdlc plugin and fix Project CodeGuard findings in this repository.`
- `Explain the Project CodeGuard findings and recommended remediations for this repository.`

### New scripts

- `packages/codex/plugins/ai-ready-sdlc/scripts/run_project_codeguard_security.py`
- optional fixer helper for standardized remediation output

### Codex metadata updates

Update plugin prompts and docs so Codex users see Project CodeGuard as a first-class capability in the same plugin surface.

## README And Docs Work Required

### Root README

Add:

- Project CodeGuard under `What The Standard Checks`
- new report outputs
- new Claude command
- new Codex workflow prompts
- update the demo and rollout sections

### New docs

Create:

- `docs/project-codeguard-usage.md`
- `docs/project-codeguard-demo-playbook.md`
- `docs/project-codeguard-fix-cookbook.md`
- `docs/project-codeguard-rule-mapping.md`

### What those docs should cover

`project-codeguard-usage.md`

- what the CodeGuard lane checks,
- when to run the dedicated security workflow,
- how it differs from general code quality,
- how it rolls into `run-org-standards`.

`project-codeguard-demo-playbook.md`

- exact commands/prompts for the 3 demo repos,
- what findings to expect by repo type,
- which repo is best for which story.

`project-codeguard-fix-cookbook.md`

- common fix patterns:
  - secrets to env vars / secret stores,
  - parameterized queries,
  - safe crypto choices,
  - authz checks,
  - secure logging,
  - dependency and CI hardening.

`project-codeguard-rule-mapping.md`

- upstream CodeGuard domains,
- our standards-core mapping,
- Cisco-specific overlays,
- report severity policy.

## Demo Plan For The Three Repos

### 1. `webex-messaging-mcp-server`

Primary demo story:

- JavaScript / TypeScript repo
- good target for:
  - secrets handling,
  - API authn/authz,
  - input validation,
  - dependency / CI checks,
  - secure logging and data handling

Suggested demo:

- run `run-org-standards`
- run dedicated Project CodeGuard review
- show security-specific findings and remediations

### 2. `cdr-dedup`

Primary demo story:

- Go repo
- good target for:
  - crypto choices,
  - network/service validation,
  - authn/authz checks,
  - serialization / input safety,
  - secure service defaults

Suggested demo:

- use Claude first
- show umbrella flow plus dedicated CodeGuard review
- show Go-specific secure coding recommendations

### 3. `smi-cluster-deployer`

Primary demo story:

- mixed repo: Node.js + Python + Ansible / Helm / deployment artifacts
- strongest target for:
  - IaC and deployment security,
  - supply chain and CI,
  - secrets handling,
  - container / Kubernetes security,
  - multi-language coverage

Suggested demo:

- use Codex or Claude with `run-org-standards`
- show why Project CodeGuard belongs in the shared core for mixed repos

## Implementation Phases

### Phase 1: Planning and pinning

- pin upstream CodeGuard `v1.3.1`
- add metadata and source mapping docs
- define report schema and severity mapping

### Phase 2: Shared-core implementation

- add `project-codeguard-security` checker profile
- add report outputs
- add umbrella integration in `run-org-standards`

### Phase 3: Plugin delivery

- add Claude commands, agents, skills
- add Codex skills, prompts, scripts
- update plugin metadata and README

### Phase 4: Demo hardening

- run on the 3 target repos
- tune false positives
- add fix cookbook examples from real findings

## Acceptance Criteria

- `run-org-standards` includes Project CodeGuard security results
- Claude, Codex, and Augment all expose a dedicated CodeGuard security workflow
- reports include both umbrella output and dedicated CodeGuard output
- docs clearly explain how to check and fix CodeGuard findings
- the 3 demo repos produce usable, defensible output for a stakeholder demo

## Recommended First Implementation Choice

Start with:

- pinned upstream `v1.3.1`,
- dedicated `project-codeguard-security` checker profile,
- dedicated report schema/template,
- one Claude command,
- one Codex skill,
- one demo playbook doc.

That gives us a fast, credible first increment without overbuilding.

## Sources

- Project repo: https://github.com/cosai-oasis/project-codeguard
- Releases: https://github.com/cosai-oasis/project-codeguard/releases
- README: https://raw.githubusercontent.com/cosai-oasis/project-codeguard/main/README.md
- Getting started: https://raw.githubusercontent.com/cosai-oasis/project-codeguard/main/docs/getting-started.md
- Claude plugin doc: https://raw.githubusercontent.com/cosai-oasis/project-codeguard/main/docs/claude-code-skill-plugin.md
- Custom rules doc: https://raw.githubusercontent.com/cosai-oasis/project-codeguard/main/docs/custom-rules.md
- Claude plugin manifest: https://raw.githubusercontent.com/cosai-oasis/project-codeguard/main/.claude-plugin/plugin.json
- Claude marketplace: https://github.com/cosai-oasis/project-codeguard/blob/main/.claude-plugin/marketplace.json
- Codex / agent skills: https://raw.githubusercontent.com/cosai-oasis/project-codeguard/main/skills/software-security/SKILL.md
- Security review skill: https://raw.githubusercontent.com/cosai-oasis/project-codeguard/main/skills/security-review/SKILL.md
- Converter: https://raw.githubusercontent.com/cosai-oasis/project-codeguard/main/src/convert_to_ide_formats.py
