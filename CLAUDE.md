# CanonLoom Claude Code Entry

Use the repository as a command-driven writing workflow, not as a GUI product.

Before acting, run:

```bash
python3 scripts/canonloom.py status
python3 scripts/canonloom.py diagnose
python3 scripts/canonloom.py repair --dry-run
```

Then execute the task described in `tasks/current.md`. Keep all durable decisions in project files and follow the S0–S6 protocol in `docs/strong-constraints.md`.

The author-facing high-level commands are documented in `AGENTS.md`. Claude may perform the agent work behind those commands, but must leave inspectable artifacts and stop at author decision gates.

Use the generic production tools in `docs/production-tools.md` for Beat checks, bounded context compilation, chapter validation, indexing, retrieval, cross-validation, and repair plans.

Keep machine-facing protocol identifiers in English. Follow `intent/author-setup.json` for prose and review language, and consult `docs/language-policy.md` for bilingual projects.

If the project is structurally inconsistent, diagnose first and use `repair` only for the documented safe repairs. Never use repair to alter canon, manuscript prose, review judgments, or author decisions.
