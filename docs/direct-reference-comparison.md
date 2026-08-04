# Direct reference comparison

These are the three external projects previously retained as local references during the architecture research. They are closer to CanonLoom's intended tool/workflow layer than general AI writing applications.

## At a glance

| Project | Primary unit | Main strength | Main trade-off | CanonLoom's response |
|---|---|---|---|---|
| [oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode) | Skill and command toolbox | Broad commercial-fiction workflow: market scanning, text analysis, long/short writing, import, review, de-AI editing, and multi-runtime deployment | Large surface area and strong genre/platform assumptions; many rules are operational rather than a neutral data model | Keep the reusable workflow ideas, but make the state model, evidence, contracts, and runtime adapter explicit and portable |
| [chinese-novelist-skill](https://github.com/PenglongHuang/chinese-novelist-skill) | Guided full-book session | Low-friction onboarding, preference memory, interruption recovery, serial/parallel/Teams modes, automatic checking and repair | Optimized for getting a user from idea to completed Chinese novel; less emphasis on provenance, reversible state, and author settlement | Keep the guided onboarding and recovery concepts; separate author decisions, candidate memory, and approved canon |
| [novel-creator-skill](https://github.com/leenbj/novel-creator-skill) | File-based long-form production system | Explicit five-layer consistency approach: gates, retrieval, graph, outline anchors, and cross-agent review | Strong automation claims and many hard rules can become expensive or block production; the architecture is closely tied to one skill/runtime shape | Keep bounded context, multi-step beats, review gates, and cross-agent checks; add decision artifacts, evidence traces, and configurable modes |

## 1. oh-story-claudecode

The project presents itself as an all-in-one skill pack for web fiction. Its public workflow covers setup, market scanning, text analysis, writing, import, review, de-AI editing, and cover generation. It also provides adapters for several agent runtimes, including Claude Code and Codex. See the [project README](https://github.com/worldwonderer/oh-story-claudecode).

### Ideas CanonLoom adopts

- Separate preparation, analysis, writing, review, and de-AI editing rather than one giant prompt.
- Use skills and project files as a portable interface between agents.
- Support both new projects and reverse import of existing manuscripts.
- Treat chapter position, genre, pacing, and reader expectation as explicit inputs.

### Ideas CanonLoom changes

CanonLoom is not a commercial web-fiction playbook. It does not prescribe a particular platform, genre formula, market strategy, or set of slash commands. The portable core is instead:

```text
intent → state → contract → option → selection → draft → evidence → settlement
```

Genre and platform modules can be added above this core without changing the state lifecycle.

## 2. chinese-novelist-skill

This project emphasizes completion: progressive questions, preference memory, interruption recovery, selectable writing modes, automatic checking, and repair. Its public README describes a flow from initialization and questions to planning, full drafting, validation, and automatic rewrite.

### Ideas CanonLoom adopts

- Ask only the questions needed to establish a project.
- Make interruption and resumption first-class operations.
- Offer serial and parallel modes according to the user's risk and speed preference.
- Turn validation failures into an actionable repair path.

### Ideas CanonLoom changes

CanonLoom separates “the system can continue” from “the author has approved the result.” A resumed project may continue from a saved state, but a proposed fact remains a proposal until it passes the decision gate. This avoids treating automatic completion as equivalent to authorial acceptance.

## 3. novel-creator-skill

This is the closest reference to CanonLoom's long-form consistency architecture. It describes a five-layer system: per-chapter gates, retrieval, a knowledge graph, outline anchors, and cross-agent review. It also uses a beat pipeline and bounded context. See the [project README](https://github.com/leenbj/novel-creator-skill).

### Ideas CanonLoom adopts

- A chapter should be a bounded execution unit.
- Retrieval should return a small relevant package rather than the entire manuscript.
- Beat-level expansion can control narrative scope.
- Review should be separated from generation.
- Long-form state needs more than a flat summary.

### Ideas CanonLoom changes

CanonLoom treats hard rules as policy profiles rather than universal laws. A routine chapter may use Economy mode; an arc turn may use Deep Review. This reduces unnecessary token use and prevents a quality system from becoming a production bottleneck.

CanonLoom also distinguishes four artifacts that are often conflated:

```text
creative option  ≠ author decision
draft             ≠ canon
review finding    ≠ fact
memory candidate  ≠ active memory
```

## Synthesis

The three references contribute different layers:

```text
oh-story-claudecode   → breadth, genre workflow, runtime deployment
chinese-novelist      → onboarding, recovery, completion-oriented UX
novel-creator         → state, retrieval, gates, beats, multi-agent review
```

CanonLoom combines them around a stricter invariant:

> Every durable story change must be attributable to an author decision and supported by evidence.

That invariant is the main distinction between CanonLoom and a collection of writing prompts or autonomous chapter generators.

## Source and scope note

This comparison describes the public repositories and the local reference copies used during the architecture research. Feature sets and versions may change. It is not a claim that one project is universally better; each optimizes for a different point on the spectrum from guided completion to configurable, auditable infrastructure.
