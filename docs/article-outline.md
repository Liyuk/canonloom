# Shareable article outline

Suggested title:

> From Prompting to Narrative Production: An Auditable Human–AI Workflow for Long-Form Fiction

Alternative Chinese title:

> 从提示词到叙事生产：长篇小说人机协作的可审计工作流

## Thesis

Long-form fiction is not primarily a larger prompt problem. It is a state, planning, decision, verification, and memory-settlement problem. A useful system must expand creative possibility while controlling which changes become durable story facts.

## Proposed structure

### 1. The failure of “write the next chapter”

Describe context overload, character drift, premature resolution, forgotten threads, and the inability to distinguish model invention from author decision.

### 2. Four tasks that look similar but are not

Explain ideation, reference analysis, manuscript import, and current-project production. Show why mixing them corrupts canon and makes evaluation impossible.

### 3. The CanonLoom model

Introduce intent, canon, state, contracts, divergence, selection, context compilation, review, and settlement.

### 4. The hierarchical planning system

Explain series → volume → arc → chapter → beat → scene. Emphasize that each level has a different responsibility and that lower-level generation cannot silently rewrite higher-level decisions.

### 5. Creative divergence and author control

Show how multiple personas generate alternatives, while the author selects or merges them before drafting. Distinguish creativity from commitment.

### 6. Evidence-based production gates

Show structure, continuity, style, reader-promise, and deterministic checks. Explain BLOCKER/MAJOR/MINOR/ADVISORY severity and why a draft is not canon.

### 7. Runtime portability

Explain how the same file-based artifacts can be used by Codex, Claude Code, OpenCode, or other agents through adapters.

### 8. Token and quality trade-offs

Compare single-pass, full-context, structured, divergent, and deep-review modes. Report estimates separately from measured experiments.

### 9. Evaluation protocol

Freeze model, seed, contract, and output budget. Compare workflows on continuity, causality, contract fidelity, character agency, reader promise, style, author effort, tokens, retries, and latency.

### 10. Limits and open questions

Discuss the cost of multiple agents, the difficulty of measuring literary quality, the risk of over-engineering, and the need for human judgment.

## Evidence policy for the article

- Use anonymized or generic examples in the public article.
- Separate observed project practice, design hypothesis, and measured result.
- Cite external tools and papers rather than presenting their ideas as original.
- Do not claim that a gate guarantees literary quality.
- Include negative results: blocked drafts, abandoned options, redundant context, and cases where the simpler workflow was better.

## Minimal public demo

The article should include one fully traceable generic example:

```text
seed → 3 options → author selection → volume goal
→ chapter contract → 4 beats → draft excerpt
→ review finding → repair → approved state delta
```

The example should contain no real manuscript, proprietary setting, or third-party copyrighted passage.
