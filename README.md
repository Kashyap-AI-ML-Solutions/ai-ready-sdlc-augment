# AI Ready SDLC Augment Marketplace

This directory is a publishable Augment / Auggie marketplace for the `ai-ready-sdlc` plugin.

## Install

After publishing this marketplace repository to GitHub or GitHub Enterprise, install it with:

```sh
auggie plugin marketplace add Kashyap-AI-ML-Solutions/ai-ready-sdlc-augment
auggie plugin install ai-ready-sdlc@ai-ready-sdlc-augment
auggie plugin list
```

For user/global enablement, make sure `~/.augment/settings.json` includes:

```json
{
  "recommendedMarketplaces": ["Kashyap-AI-ML-Solutions/ai-ready-sdlc-augment"],
  "enabledPlugins": {
    "ai-ready-sdlc@ai-ready-sdlc-augment": true
  }
}
```

`auggie plugin list` must show `[✓] ai-ready-sdlc@ai-ready-sdlc-augment` or `[x] ai-ready-sdlc@ai-ready-sdlc-augment`. If it shows `[ ]`, confirm `~/.augment/settings.json` and rerun `auggie plugin install ai-ready-sdlc@ai-ready-sdlc-augment`.

Use project scope only when a specific repository should carry `.augment/settings.json` enablement:

```sh
auggie plugin install ai-ready-sdlc@ai-ready-sdlc-augment --project
```

To recommend the marketplace for a specific repository, add this to `.augment/settings.json`:

```json
{
  "recommendedMarketplaces": ["Kashyap-AI-ML-Solutions/ai-ready-sdlc-augment"],
  "enabledPlugins": {
    "ai-ready-sdlc@ai-ready-sdlc-augment": true
  }
}
```

## Included Workflow Surface

In Auggie 0.27.2, autocomplete renders the installed marketplace command namespace as `/ai-ready-sdlc--ai-ready-sdlc-augment:<command>`.

- `/ai-ready-sdlc--ai-ready-sdlc-augment:create-adlc-harness`
- `/ai-ready-sdlc--ai-ready-sdlc-augment:steer-adlc-harness`
- `/ai-ready-sdlc--ai-ready-sdlc-augment:adlc-harness`
- `/ai-ready-sdlc--ai-ready-sdlc-augment:adlc-feature-harness`
- `/ai-ready-sdlc--ai-ready-sdlc-augment:adlc-bugfix-harness`
- `/ai-ready-sdlc--ai-ready-sdlc-augment:adlc-remediation-harness`
- `/ai-ready-sdlc--ai-ready-sdlc-augment:adlc-org-status-harness`
- `/ai-ready-sdlc--ai-ready-sdlc-augment:run-org-standards`
- `/ai-ready-sdlc--ai-ready-sdlc-augment:run-org-repo-status`
- `/ai-ready-sdlc--ai-ready-sdlc-augment:aggregate-org-metrics`
- `/ai-ready-sdlc--ai-ready-sdlc-augment:review-code-quality`
- `/ai-ready-sdlc--ai-ready-sdlc-augment:review-project-codeguard-security`
- `/ai-ready-sdlc--ai-ready-sdlc-augment:fix-project-codeguard-findings`
- `/ai-ready-sdlc--ai-ready-sdlc-augment:fix-org-standards-findings`
- `/ai-ready-sdlc--ai-ready-sdlc-augment:explain-project-codeguard-findings`
