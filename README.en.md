# CanonLoom

> A command-driven, author-controlled, auditable workflow for long-form fiction.

[中文 README](README.md)

Version: `0.1.0` · [Changelog](CHANGELOG.md)

CanonLoom is not a GUI writing application and not a black box that claims to generate an entire novel from one prompt. It turns novel production into inspectable, resumable tasks: ideation, reference analysis, planning, chapter contracts, beats, bounded context, drafting, revision, review, and settlement.

The author runs simple commands. Codex, Claude Code, or another file-capable agent performs the creative work. Python handles deterministic validation, indexing, provenance, run records, repair plans, and stage gates.

## Why it exists

Long fiction usually breaks between chapters: motivations drift, timelines contradict each other, unapproved assumptions enter the manuscript, context grows without control, and review comments never become concrete repair work.

CanonLoom uses a strict separation:

```text
an idea is not canon
a candidate is not a decision
a draft is not a manuscript
a review finding is not a story fact
unapproved memory is not active memory
```

Important changes should be traceable to author intent, a chapter contract, a selected option, bounded evidence, review findings, and explicit approval.

## Architecture

```text
author intent
      ↓
project / volume / arc / chapter contract / beats
      ↓
bounded context package + provenance
      ↓
draft → quick validation → repair plan
      ↓
strict validation → independent review → optional cross-validation
      ↓
author approval → settlement → manuscript / active memory
```

The production protocol is S0–S6:

```text
S0 Contract
  ↓
S1 Draft → S2 Quick Check → S3 Repair
  ↓
S4 Strict Check → S5 Independent Review → S5b Cross-Validation
  ↓
S6 Human-Approved Settlement
```

Stages cannot be skipped. Without an explicit S6 approval, a draft is not promoted to `manuscript/` or `memory/`.

## Recommended runtime: one model plus Python

The default recommendation is one primary model for ideation, planning, drafting, revision, and review, with Python handling deterministic work. This preserves creative continuity and reduces duplicated context and token synchronization.

Multiple models remain possible for isolated high-risk review, but their reports should be compared without merging hidden or mutable memory.

## Language policy

CanonLoom separates the language of the machine protocol from the language of the novel:

- JSON keys, enum values, commands, paths, and stage IDs remain stable English identifiers;
- repository instructions may be bilingual;
- prose, author intent, and human-facing review explanations follow `intent/author-setup.json`;
- an agent may explain decisions in the author's preferred language, but must preserve paths, schemas, and approval states.

See [docs/language-policy.md](docs/language-policy.md).

## Quick start

Requirements: Python 3.9+. No third-party dependencies are required.

```sh
git clone <your-canonloom-repo>
cd canonloom

./bin/canonloom init ~/my-novel --name "My Novel" \
  --language en-US --genre "speculative mystery" \
  --audience "adult readers" --pov close-third
cd ~/my-novel

./bin/canonloom setup
./bin/canonloom setup --confirm
./bin/canonloom idea
./bin/canonloom continue
```

Initialization intentionally separates author-confirmed configuration from AI recognition:

```text
author confirmation → intent/author-setup.json
AI recognition      → intent/ai-recognition.json
style constraints   → intent/style-profile.json
then                → idea / planning / work
```

AI recognition is a proposal layer. It does not silently promote facts into `canon/`.

## Everyday commands

```sh
canonloom status       # Where am I?
canonloom continue     # Follow next_action
canonloom diagnose     # What is structurally wrong?
canonloom repair       # Repair safe structural issues
canonloom --version    # Show framework version
```

Run the minimal end-to-end smoke test with:

```sh
examples/minimal-project/smoke.sh
```

Creation and analysis entry points include `setup`, `idea`, `reference`, `import`, `planning`, `work`, `characters`, `world`, `research`, `revision`, and `review`.

## Recovery and observability

Each fresh verification run gets its own manifest:

```text
runs/<work-id>/<run-id>/manifest.json
```

It can record stage, runtime strategy, tool calls, input/output tokens, latency, retries, and events. Context packages and indexes record SHA-256 source fingerprints.

```sh
canonloom retry S0 --work-id chapter-001 --reason "revision needs a fresh pass"
canonloom record --stage S2 --model my-model \
  --input-tokens 10000 --output-tokens 1500 \
  --latency-ms 4000 --retries 0
```

`diagnose → repair → diagnose` only repairs safe structure, configuration, and task artifacts. It does not rewrite canon, manuscript prose, review judgments, or author approvals.

## Runtime compatibility

CanonLoom is designed for Codex, Claude Code, OpenCode, and other agents that can read and modify local files. The portable layer is Markdown, JSON, schemas, contracts, reports, and traces. Runtime-specific instructions live in `AGENTS.md`, `CLAUDE.md`, or an adapter layer.

Apps without local filesystem and Terminal access can still analyze uploaded artifacts, but cannot reliably maintain project state or run gates.

## Public-repository checklist

Before publishing a project based on CanonLoom:

- include a clear license and versioning policy;
- include a small original example project;
- document supported Python versions and runtime assumptions;
- add contribution and issue templates if accepting outside users;
- keep novels, private keys, unauthorized reference text, and sensitive logs out of Git;
- explain what the agent may write and where author approval is required.

Run the repository checks before release:

```sh
python3 -m py_compile scripts/*.py
python3 -m unittest discover -s tests -q
python3 scripts/public_check.py --root .
git diff --check
```

## Documentation

- [Initialization protocol](docs/en/initialization.md)
- [Workflow overview](docs/workflow.md)
- [Architecture](docs/architecture.md)
- [Strong S0–S6 constraints](docs/strong-constraints.md)
- [Terminal, API, and App usage](docs/en/terminal-and-apps.md)
- [Runtime adapters](docs/runtime-adapters.md)
- [Style Profile](docs/style-profile.md)
- [Benchmark and comparison notes](docs/en/benchmark.md)

## Scope

CanonLoom provides executable workflow conventions, file protocols, validators, gates, and audit traces. Model calls, literary judgment, and final canon approval remain the responsibility of the connected agent and the author.

## License

MIT — see [LICENSE](LICENSE).

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md) for contribution and security guidance.
