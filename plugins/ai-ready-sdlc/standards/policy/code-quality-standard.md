# Automated Code Quality Evaluation Standard

## Purpose

This standard defines how repositories should be evaluated for code quality across multiple languages while keeping results comparable at the organization level.

## Required Outcome

Repositories should be able to produce a shared code quality report that includes:

- detected language set,
- tools used per language,
- install guidance for required tools,
- code quality findings,
- security findings,
- complexity indicators,
- maintainability or style indicators where supported,
- test coverage status against the organization threshold,
- prioritized remediation guidance.

## Required Workflow

1. Detect the language or languages present in the repository.
2. Select the approved toolchain for each detected language from the organization tool matrix.
3. Run the language-specific evaluators.
4. Normalize raw outputs into the shared code quality report schema.
5. Produce a detailed engineering report and a concise summary suitable for pull requests, issues, or leadership dashboards.

## Supported Dimensions

- Code quality
- Complexity
- Security
- Style and formatting
- Maintainability

## Execution Surfaces

- Interactive invocation from Claude
- Interactive invocation from Codex
- Automated invocation from CI or scheduled workflows

## Rule

Platform-specific plugins may differ in how developers invoke the workflow, but they should use the same language tool matrix and normalized report contract.
