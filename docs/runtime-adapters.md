# Runtime adapters

## Compatibility answer

Yes. CanonLoom is intended to run with both Codex and Claude Code, as well as OpenCode and other agents that can inspect and modify local project files.

The architecture is runtime-neutral because it separates:

- **portable layer**: Markdown, JSON, schemas, contracts, evidence reports, and state deltas;
- **adapter layer**: commands, agent definitions, hooks, model selection, and orchestration syntax.

## Codex adapter

The adapter can expose the workflow through repository instructions and skills. A minimal mapping is:

```text
plan        → read intent + canon + current state; write a chapter contract
diverge     → create independent option files
select      → record the author's chosen option
draft       → compile context and generate a candidate
review      → write evidence-backed findings
settle      → apply an approved state delta
```

Codex-specific files can live under `.agents/skills/` or another supported project instruction directory. They should call the same schemas and preserve the same trace artifacts.

## Claude Code adapter

The adapter can expose the same operations through `SKILL.md`, project instructions, custom agents, and optional hooks. Suggested roles are:

- `story-architect` — contracts and plan boundaries;
- `creative-diverger` — independent alternatives;
- `context-compiler` — evidence package construction;
- `narrative-writer` — candidate prose;
- `continuity-reviewer` — state and provenance checks;
- `style-reviewer` — language and voice checks;
- `settlement-editor` — proposed deltas, never unilateral approval.

## Strong-constraint execution

Recommended default: use one primary model for the creative thread and Python for deterministic checks. This reduces duplicated context and token synchronization while keeping the model choice portable between Codex and Claude. S5 is an isolated review pass and S5b is report reconciliation; neither requires a second model. A second model is optional for isolated, high-risk review; compare its report without merging hidden or mutable memory.

Both adapters should implement the same S0–S6 protocol in [strong-constraints.md](strong-constraints.md). The runtime may vary, but it must not change the stage boundaries:

```text
S0 contract gate → S1 draft → S2 quick → S3 repair
→ S4 strict → S5 independent review → S5b cross-validation
→ S6 human-approved settlement
```

At S6, the gate validates the author approval and creates the settlement trace. The settlement command then performs the mechanical promotion. This avoids a circular dependency between the gate and the settlement trace.

The lightweight checker runs without third-party dependencies:

```bash
python3 scripts/canonloom_check.py stage-log templates/workflows/stage-log.json
python3 scripts/canonloom_check.py transition S0 S1
python3 scripts/canonloom_check.py boundary S1 drafts/chapter-001.md traces/S1.json
```

`canonloom_check.py` is a low-level maintainer/adapter checker. It is not part of the normal author path; use `canonloom advanced` to discover the supported advanced surface.

The checker is a guardrail, not a substitute for literary review. A passing mechanical check never approves a draft.

The generic production tools are available to both runtimes through the same CLI: chapter validation, Beat validation, context compilation, chapter indexing, retrieval, cross-validation, style metrics, statistics, and repair-plan generation. See [production-tools.md](production-tools.md).

## Portability rules

1. Never encode the only copy of canon inside a prompt.
2. Never depend on a model-specific hidden memory.
3. Save the selected option and compiled context before drafting.
4. Save model/runtime metadata with each candidate and review.
5. Keep human approval outside the generator's authority.

## Model substitution

If model substitution is used, comparisons should record model, version, temperature or equivalent settings, input evidence, output length, latency, and retry count. The portable `canonloom record` command can store these metrics without binding CanonLoom to a model API:

```bash
./bin/canonloom record --stage S2 --model my-model --provider provider \
  --input-tokens 12000 --output-tokens 1800 --latency-ms 4200 --retries 0
```
