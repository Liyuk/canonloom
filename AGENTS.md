# CanonLoom Agent Instructions

CanonLoom is a command-driven, file-based workflow. It is not a GUI application.

## Start every task

1. Read `canonloom.json`.
2. Read `tasks/current.md` if present.
3. Run `python3 scripts/canonloom.py status`.
4. Follow the current `next_action`; do not invent a different workflow silently.

## Author-facing commands

```bash
python3 scripts/canonloom.py idea
python3 scripts/canonloom.py setup
python3 scripts/canonloom.py setup --confirm
python3 scripts/canonloom.py reference --input "path or description"
python3 scripts/canonloom.py import --input "path to manuscript"
python3 scripts/canonloom.py planning
python3 scripts/canonloom.py work
python3 scripts/canonloom.py continue
python3 scripts/canonloom.py status
python3 scripts/canonloom.py diagnose
python3 scripts/canonloom.py repair --dry-run
python3 scripts/canonloom.py repair
python3 scripts/canonloom.py gate S0 --work-id chapter-001
python3 scripts/canonloom.py gate S1 --work-id chapter-001
python3 scripts/canonloom.py validate drafts/chapter-001.md --contract plan/chapter-contracts/chapter-001.json --level quick
python3 scripts/canonloom.py context plan/chapter-contracts/chapter-001.json
python3 scripts/canonloom.py settle --work-id chapter-001
python3 scripts/canonloom.py retry S0 --work-id chapter-001 --reason "revision requires a fresh verification pass"
```

## Hard boundaries

- Do not write project facts into `canon/` without explicit author approval.
- Do not promote drafts into `manuscript/` without S6 approval.
- Do not skip a required stage because a model believes the output is good enough.
- Do not mix reference analysis, invention, manuscript import, and canon settlement in one undocumented action.
- Preserve stage logs, findings, open loops, and handoff artifacts.
- Do not run a later gate to bypass a missing earlier artifact.
- If structure is broken, run `diagnose` first; `repair` may fix only safe structure/task/config issues and must leave story content untouched.

The full protocol is in `docs/strong-constraints.md`.

Language policy: keep JSON keys, enum values, commands, paths, and stage IDs in stable English. Use the project language from `intent/author-setup.json` for prose and human-facing explanations. See `docs/language-policy.md`.
