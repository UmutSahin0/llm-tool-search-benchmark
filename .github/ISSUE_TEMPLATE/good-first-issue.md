---
name: Good first issue
about: A small, well-scoped contribution for new contributors
title: "good first issue: add a validation test for the task catalog"
labels: ["good first issue", "help wanted"]
---

## Goal

Add a small validation script or test that checks every entry in `data/tasks.json` has a unique `id`, a non-empty `prompt`, and an `expected_tool` present in the generated catalog.

## Why

The benchmark assumes task labels are valid and evaluation-only. An invalid label can make an experiment look worse without an obvious runtime failure.

## Acceptance criteria

- The check runs locally with a documented command.
- It fails with a clear message for duplicate IDs, empty required fields, or missing expected tools.
- It does not send `expected_tool` to a provider or retrieval tool.
- Add a small test fixture or test case covering one invalid task.

## Getting started

Read `CONTRIBUTING.md`, then comment on the issue before starting so work is not duplicated.
