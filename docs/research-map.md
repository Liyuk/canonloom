# Research map

## NarrativeLoom (2026)

[NarrativeLoom: Enhancing Creative Storytelling through Multi-Persona Collaborative Improvisation](https://arxiv.org/abs/2603.07155) studies specialized personas that generate diverse alternatives while the user acts as creative director. It is the direct inspiration for CanonLoom's Divergence Studio and Author Selection Gate. CanonLoom extends that idea with durable canon, chapter contracts, evidence reports, and approved state settlement.

## StoryWriter (2025)

[StoryWriter: A Multi-Agent Framework for Long Story Generation](https://arxiv.org/abs/2506.16445) separates outline, planning, and writing agents and uses dynamic history compression. CanonLoom aligns with its hierarchical planning and bounded context ideas, but makes author selection, provenance, and reversible state promotion explicit.

## Lost in Stories / ConStory-Bench (2026)

[Lost in Stories: Consistency Bugs in Long Story Generation by LLMs](https://arxiv.org/abs/2603.05890) introduces a benchmark and taxonomy for long-form consistency errors, including factual and temporal problems, and grounds checking in textual evidence. This supports CanonLoom's decision to treat evidence-backed review and state tracking as core infrastructure rather than post-processing polish.

## From Personas to Plot (2026)

[From Personas to Plot: Character-Grounded Multi-Agent Story Generation for Long-Form Narratives](https://arxiv.org/abs/2607.00918) describes goal-driven character agents sharing world state and a graph-based verification pipeline. It is close to CanonLoom's combination of entity state, multi-agent generation, and verification. CanonLoom's additional emphasis is the human decision gate and portability across runtimes.

## Research gap CanonLoom targets

The papers above address complementary pieces: creative diversity, hierarchical generation, consistency measurement, and world-state verification. CanonLoom proposes an engineering layer that connects them into an author-governed lifecycle:

```text
author intent → state → contract → alternatives → selection
→ context compilation → draft → evidence review → settlement
```

The open question is not whether one pipeline can produce a good sample. It is whether a writer can repeatedly make, inspect, reverse, and approve long-form decisions while controlling token use and preserving authorship.
