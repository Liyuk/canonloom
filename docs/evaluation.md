# Evaluation, token budget, and quality

> 本文保留早期的评估假设；当前 benchmark、竞品矩阵、运行命令和本地工具实测见 [benchmark.md](benchmark.md)。

## Important distinction

The numbers in this document are planning estimates for a moderate chapter, not measured API bills or quality claims. Actual usage depends on model, language, output length, context size, caching, retries, tool calls, and reviewer configuration.

## Illustrative token budget per chapter

Assumptions: 4,000–6,000 output tokens for the chapter, 8–20k relevant project context, 2–4 creative options, and focused reviews. A token is counted for both input and output.

| Workflow | Typical calls | Estimated tokens | Cost/quality tendency |
|---|---:|---:|---|
| Single prompt continuation | 1 generation | 15k–35k | Cheapest; weak state control and limited diagnosis |
| Full-context continuation | 1 generation with a large manuscript window | 50k–150k | High context cost; noise and forgotten facts remain possible |
| Structured single-path | plan + retrieve + draft + one review | 25k–55k | Good efficiency; limited creative exploration |
| NarrativeLoom-style divergence | 3–5 options + author selection + draft | 35k–80k | More variety; option generation adds cost |
| CanonLoom economy | 2 options + bounded retrieval + draft + one review | 30k–60k | Best for routine chapters |
| CanonLoom standard | 4 options + selection + retrieval + draft + 3 reviews + settlement | 55k–110k | Higher control and auditability |
| CanonLoom deep review | 4–6 options + adversarial review + revision + settlement | 90k–180k+ | Highest cost; suitable for arc turns and release candidates |

## How to reduce tokens without removing the architecture

- Use two options for low-risk chapters.
- Retrieve entity and timeline snippets instead of whole chapters.
- Reuse stable context through provider caching when available.
- Run style checks deterministically before asking a model to review them.
- Use a smaller model for extraction, indexing, and first-pass checks.
- Reserve multi-agent divergence and deep review for decisions with downstream impact.

## Quality dimensions

CanonLoom should not use one “quality score” as its main claim. Evaluate at least:

1. **Continuity** — factual, temporal, spatial, relational, and rule consistency.
2. **Causality** — whether actions produce intelligible consequences.
3. **Contract fidelity** — whether the chapter fulfills its intended change without over-resolving.
4. **Character agency** — whether choices arise from current goals, knowledge, and pressure.
5. **Reader promise** — clarity, curiosity, emotional movement, and payoff timing.
6. **Style** — voice, sentence rhythm, dialogue differentiation, and unwanted generation patterns.
7. **Author effort** — time to select, correct, and approve a chapter.

## Proposed controlled comparison

For a fair experiment, freeze the same model, project seed, chapter contracts, and output budget. Compare:

```text
A. single-path prompt
B. structured plan + retrieval
C. multi-agent divergence
D. CanonLoom standard
```

Use at least 20 chapter tasks across several genres. Blind the prose when human raters score it. Report mean and variance, not only the best chapter. Log input tokens, output tokens, tool calls, retries, latency, reviewer findings, revision count, and author time.

## Expected hypotheses

These are hypotheses to test:

- B should reduce factual and temporal errors relative to A.
- C should improve novelty and option diversity relative to B, at higher token use.
- D should reduce unresolved continuity and provenance errors relative to C, especially after the middle of a long project.
- D may cost more per chapter but reduce expensive late-stage repair and author uncertainty.

No hypothesis should be presented as a result until the experiment is run.
