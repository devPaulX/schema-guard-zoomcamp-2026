# Agent roles and handoffs

These responsibilities follow [Issue #7](https://github.com/devPaulX/schema-guard-zoomcamp-2026/issues/7). Work is scoped by the [product specification, Issue #1](https://github.com/devPaulX/schema-guard-zoomcamp-2026/issues/1), and by each task such as [Issue #2](https://github.com/devPaulX/schema-guard-zoomcamp-2026/issues/2).

## Product Manager

Maintains the product specification and GitHub Issues. Defines acceptance criteria, priorities, and task boundaries. Clarifies scope before work that would alter product behavior.

## Engineer

Implements one tracked task at a time. Keeps code simple, runs tests and smoke checks, and reports changed files, commands, results, and limitations with issue IDs. Does not claim unrun checks passed.

## QA Reviewer

Independently checks implementation against the issue and specification. Exercises success and failure paths, reports defects with reproduction steps, and verifies fixes. Reviews evidence before an issue is considered complete.

## Incident Responder

Handles supported alert-driven recovery actions when incident functionality exists. Records evidence and escalates unsupported incidents. Does not make destructive corrections or claim that future recovery features are already implemented.

## Workflow

Product Manager defines an issue and acceptance criteria. Engineer implements and supplies verification evidence. QA Reviewer evaluates those criteria and returns defects for correction. Incident Responder participates when an operational incident requires supported action. Issue comments and closure are performed only with authorization.
