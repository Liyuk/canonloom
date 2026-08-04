# Landscape and positioning

This is a directional comparison, not a benchmark ranking. Public repositories have different goals, maturity, models, prompts, and evaluation protocols.

| Project | Main idea | Strength | Difference from CanonLoom |
|---|---|---|---|
| [NarrativeLoom](https://github.com/PPYYQQ/narrativeloom-system) | Multi-persona creative improvisation with author selection | Creative diversity and co-creation research | CanonLoom adds durable state, chapter contracts, evidence review, and memory settlement |
| [NovelForge](https://github.com/RhythmicWave/NovelForge) | Card-based long-form writing app with schemas, context references, graph, and workflows | Productized editor and structured cards | CanonLoom is a runtime-neutral governance architecture rather than a full editor |
| [Novel-OS / book-os](https://github.com/forsonny/book-os) | Three context layers: standards, novel, and manuscripts | Simple workflow framing and tool portability | CanonLoom makes provenance, selection, review evidence, and state promotion explicit |
| [autonovel](https://github.com/NousResearch/autonovel) | Autonomous pipeline from seed to revision and export | End-to-end automation and evaluation loops | CanonLoom prioritizes author gates and reversible decisions over unattended completion |
| [graphify-novel](https://github.com/Anshler/graphify-novel) | Knowledge graph for characters, threads, worldbuilding, and continuity review | Strong cross-manuscript state exploration | CanonLoom treats graph/state as one layer within a broader creative and editorial loop |
| [InkOS](https://github.com/Narcooo/inkos) | Autonomous writing, auditing, revising, truth files, and human review gates | Operational writing pipeline and persistent truth files | CanonLoom is deliberately smaller and more implementation-agnostic |
| [StoryWriter](https://arxiv.org/abs/2506.16445) | Outline, planning, writing, and dynamic history compression agents | Research evidence for hierarchical multi-agent generation | CanonLoom adds explicit author selection and auditable settlement as first-class artifacts |

## Positioning statement

CanonLoom sits between a creative co-pilot and a fully autonomous writing pipeline:

```text
more structured than a chat prompt
more author-controlled than autonomous generation
more creative than a fixed outline expander
more auditable than a hidden agent memory
```

Its distinctive unit is not the generated paragraph. It is the **reviewable decision** connecting an author intent, a chapter contract, a selected creative option, an evidence package, a draft, and a state delta.

## What CanonLoom should not claim yet

- It is not currently a finished editor application.
- It does not yet have a public controlled benchmark.
- It does not guarantee consistency for an arbitrary length or genre.
- Its token and quality estimates below are planning estimates, not measured results.
