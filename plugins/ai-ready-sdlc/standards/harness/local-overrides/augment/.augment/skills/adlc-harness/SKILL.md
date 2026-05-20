---
name: adlc-harness
description: Optional workspace Auggie skill that delegates tasks to the installed ADLC plugin and shared .adlc lifecycle.
---

# ADLC Harness Local Override

Use this only when local overrides are explicitly installed. The plugin-provided commands and skills remain the primary workflow surface.

Read `.adlc/`, delegate to `/ai-ready-sdlc:steer-adlc-harness`, and require the canonical `.adlc/plans/<run>/` artifacts before implementation.
