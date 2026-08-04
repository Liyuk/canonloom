# Terminal, API, and App Usage

CanonLoom's core interface is a local CLI and a file protocol, not hidden model memory. It works with Codex, Claude Code, and other agents that can read and modify the project directory.

## Lightweight usage

Requirements: Python 3.9+. No third-party packages are required.

```sh
git clone <your-canonloom-repo>
cd canonloom
./bin/canonloom init ~/my-novel --name "My Novel" --language en-US
./bin/canonloom --root ~/my-novel setup
./bin/canonloom --root ~/my-novel setup --confirm
./bin/canonloom --root ~/my-novel idea
./bin/canonloom --root ~/my-novel continue
```

The four daily commands are:

```sh
./bin/canonloom --root ~/my-novel status
./bin/canonloom --root ~/my-novel continue
./bin/canonloom --root ~/my-novel diagnose
./bin/canonloom --root ~/my-novel repair
```

The CLI has three practical surfaces: author commands, agent/review commands, and maintainer commands. Authors can run `canonloom advanced` to inspect the latter without needing to learn them for daily writing.

For optional event, knowledge, and reveal tracking:

```sh
./bin/canonloom --root ~/my-novel state report
./bin/canonloom --root ~/my-novel state validate
```

## Command groups

| Command | Purpose | Content mutation |
|---|---|---|
| `init` | Create project structure and state | Empty structure only |
| `setup` | Author configuration and AI recognition entry | Setup task/config |
| `idea`, `reference`, `import` | Explore, analyze, or inventory material | Task artifacts |
| `planning`, `work`, `continue` | Plan or execute a work unit | Stage artifacts |
| `diagnose`, `status` | Inspect state | Read-only |
| `repair` | Fix safe structure problems | Structure/task/config only |
| `gate S0...S6` | Check artifacts and stage order | Updates stage state |
| `settle` | Promote an approved revised draft | Manuscript only after S6 |

All commands accept `--root /path/to/project`.

## Self-repair and gates

```text
diagnose → identify issue → repair safe items → diagnose again
```

Repair never changes canon, manuscript prose, review judgments, or author approval. S6 first validates the approval and creates the settlement trace; `settle` then performs the mechanical draft-to-manuscript copy. Calling `settle` directly cannot bypass S6.

## App capabilities

Codex App and Claude Code can use the workflow when they have the project directory and Terminal/file permissions. They should read `AGENTS.md` or `CLAUDE.md`, `canonloom.json`, and `tasks/current.md` before acting.

Apps without local filesystem access can analyze uploaded artifacts, but cannot reliably maintain state, run diagnostics, or pass gates.

## Terminal API

CanonLoom currently has no remote HTTP API. The stable integration surface is:

- CLI commands;
- `canonloom.json` for machine-readable state;
- `diagnose --json` for diagnostics;
- `tasks/current.md` for the current agent instruction;
- schemas and artifact paths for stage outputs.
