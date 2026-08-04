# Author Guide

CanonLoom is a local file workflow. The author gives a short instruction, an agent reads the task, performs one work unit, and writes inspectable artifacts. The author makes choices and approvals at defined boundaries.

## Minimal daily loop

```sh
./bin/canonloom --root ~/my-novel status
./bin/canonloom --root ~/my-novel continue
```

For a new project:

```sh
./bin/canonloom init ~/my-novel --name "My Novel"
./bin/canonloom --root ~/my-novel setup
./bin/canonloom --root ~/my-novel setup --confirm
./bin/canonloom --root ~/my-novel idea
```

## From idea to chapter

```text
idea
  ↓
reference / import (optional)
  ↓
planning
  ↓
work
  ↓
continue + gate S0...S6
```

The author should not need to manually maintain hidden prompt state. Durable decisions belong in `intent/`, `canon/`, `plan/`, `workspace/`, `reviews/`, and `tasks/`.

## What the author controls

The author controls project boundaries, selected creative options, canon promotion, unresolved risks, and final settlement. The agent may propose prose, structure, research cards, and repair plans, but it cannot treat a proposal as approval.

## If something goes wrong

```sh
./bin/canonloom --root ~/my-novel diagnose
./bin/canonloom --root ~/my-novel repair --dry-run
./bin/canonloom --root ~/my-novel repair
./bin/canonloom --root ~/my-novel diagnose
```

`repair` only handles safe structural problems. For story contradictions or literary problems, ask the agent to create a review finding or repair plan. Do not use repair as a shortcut to rewrite canon.

## Recommended operating style

Use one primary model for the creative thread and Python for deterministic checks. Keep a second model optional and isolated for high-risk review. Always preserve the context package, selection, findings, and handoff before asking for the next stage.
