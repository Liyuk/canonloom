# Agent / Maintainer tools

CanonLoom includes generic execution tools that were previously embedded in project workflows. They are intentionally story-agnostic and are primarily intended for agents and maintainers. Authors normally use the smaller command surface documented in the main README.

## Tool chain

```text
chapter contract
  ↓
beats → context package → draft
  ↓
validate quick → repair plan → revised draft
  ↓
validate strict → independent review → cross-validate
  ↓
index/query → stats/style → S6 settlement
```

## Commands

```sh
./bin/canonloom beats plan/chapter-contracts/chapter-001.json
./bin/canonloom context plan/chapter-contracts/chapter-001.json --root .
./bin/canonloom validate drafts/chapter-001.md --contract plan/chapter-contracts/chapter-001.json --level quick
./bin/canonloom validate drafts/chapter-001.md --contract plan/chapter-contracts/chapter-001.json --level strict
./bin/canonloom repair-plan reviews/chapter-001.quick.json
./bin/canonloom normalize-findings reviews/legacy-validator.json --adapter-warning --output reviews/legacy-normalized.json
./bin/canonloom index --root .
./bin/canonloom query "角色在某个地点做出选择" --root .
./bin/canonloom style drafts/chapter-001.md
./bin/canonloom stats --root .
./bin/canonloom cross-validate reviews/codex.json reviews/claude.json --output reviews/cross-validation.json
./bin/canonloom handoff --work-id chapter-001 --source-stage S2 --next-action S3 --files drafts/chapter-001.md --reports reviews/chapter-001.quick.json
./bin/canonloom record --stage S2 --model my-model --input-tokens 10000 --output-tokens 1500 --latency-ms 4000
./bin/canonloom artifact-check style-profile intent/style-profile.json
./bin/canonloom settle --work-id chapter-001
```

All tools emit JSON so an Agent or shell pipeline can consume the result. They do not call an LLM.

## What was integrated from the earlier workflows

| Earlier capability | Generic CanonLoom implementation |
|---|---|
| chapter validator | `scripts/validate_chapter.py` and `canonloom validate` |
| Beat/contract validator | `scripts/beat_validator.py` and `canonloom beats` |
| merged Stage 1 prompt/context | `scripts/build_context_package.py` and `canonloom context` |
| chapter index and retrieval | `scripts/build_chapter_index.py`, `scripts/query_chapters.py` |
| independent report comparison | `scripts/cross_validate.py` |
| style fingerprint metrics | `scripts/style_fingerprint.py` |
| arc/chapter metrics | `scripts/arc_stats.py` |
| repair instructions | `scripts/repair_plan.py` and `canonloom repair-plan` |

The former projects contained richer project-specific rules, such as fixed CJK length targets, named character appearance files, particular frontmatter layouts, and proprietary story constraints. Those are not copied into the generic core. A project may add them as an adapter or encode them in its chapter contract.

## Stage integration

- S0 requires a contract, selection, and context package; `beats` and `context` produce/check those roles.
- S1 produces a draft; `validate --level quick` is available before S2.
- S2 stores quick findings; it may be `PASS` or `NEEDS_REPAIR` and should route to S3 when needed.
- S3 uses `repair-plan` and writes a revised draft without inventing canon.
- S4 requires a valid strict report with `status=PASS`, `COMPLETED`, or `AGREEMENT`.
- S5 stores an independent review with provenance (`review_id`, `reviewer_mode`, `run_id`, `source_sha256`); the same model may be used in a separate review pass.
- S5b uses `cross-validate`; disagreement is blocked and routed to human decision.
- S6 remains the only settlement and promotion gate.
- After S6 passes, `settle` performs the mechanical draft-to-manuscript copy only when the explicit approval and settlement trace exist.
- Gate reports must contain protocol-compliant Finding entries; S4 also rejects unresolved BLOCKER/MAJOR findings, and S6 binds approval/trace to the current revised draft.
- If an approved chapter is revised, use `retry S0 --work-id ...`; this preserves old artifacts and starts a new verification pass instead of silently moving the stage backward.

## Adapter rule

Do not fork the core tool merely to change a novel's name or chapter numbering. Prefer a small adapter that supplies:

- `project-root` and directory mapping;
- contract-specific length, beat, and forbidden-term fields;
- frontmatter conventions;
- project-specific deterministic checks;
- model/runtime metadata.

Run manifests are written under `runs/<work-id>/<run-id>/manifest.json`. A retry creates a new run and preserves the previous run. Context packages and chapter indexes include SHA-256 source fingerprints so an Agent can tell whether its evidence changed.
