# Workflow catalog and routing

CanonLoom is not one linear prompt chain. It is a set of workflows selected by the user's input and the project's current state.

## Four inputs that must not be confused

| Input | Meaning | Correct workflow | What it may produce |
|---|---|---|---|
| Idea or premise | A new possibility that does not yet belong to the project | Ideation | Candidate concepts, questions, options |
| Reference work | Someone else's finished or partial work used for learning | Text analysis /拆书 | Abstract structure, technique cards, reader-effect observations |
| Existing manuscript | The user's own text that should be continued, revised, or migrated | Import / reconstruction | Candidate project state, source map, unresolved questions |
| Current project state | Confirmed canon plus active plan and recent delivery state | Planning / chapter production | Contracts, beats, drafts, reviews, state deltas |

The same text can therefore have different authority depending on why it was supplied. A reference work is not project canon. An imported manuscript is evidence for reconstruction, but uncertain inferences still require confirmation.

## Routing table

```text
只有一个想法              → ideate
想学习某部作品怎么成立     → analyze-reference
有自己的旧稿要续写         → import
已有项目要设计下一卷       → plan-volume / plan-arc
已有章契要写下一章         → produce-chapter
已有草稿需要验收           → review / revise
```

## Workflow A: ideation

Input: a premise, question, image, theme, conflict, or constraint.

Steps:

```text
seed → clarify intent → generate alternatives → compare → author selection
```

Output:

- `intent/author-intent.md`;
- candidate premises;
- reader promise candidates;
- initial world/entity questions;
- an author decision artifact.

Ideation must not silently create canon. Its output is a proposal until the author accepts it.

## Workflow B: reference analysis / 拆书

Input: a reference work or a selected passage.

Steps:

```text
scope → extract events and structure → identify reader effects
→ analyze character / information / pacing / style techniques
→ abstract reusable patterns → design an original transfer
```

Output:

- structure map;
- chapter or scene function map;
- character and relationship mechanism notes;
- pacing and information-flow observations;
- style as abstract techniques, never author-specific imitation instructions;
- reusable pattern cards;
- an originality and boundary note.

拆书 answers “why might this work?” It does not answer “what is true in my project?”

## Workflow C: manuscript import / reconstruction

Input: the user's existing chapters, notes, or fragmented project.

Steps:

```text
inventory → segment → extract claims → build provisional entities / timeline
→ attach source locations → identify conflicts and gaps → author confirmation
```

Output:

- reconstructed canon candidates;
- chapter summaries and source anchors;
- entity and relationship candidates;
- open loops;
- unresolved conflicts;
- a migration report.

Import is not the same as reference analysis: the text may become project evidence, but no inferred fact is promoted without review.

## Workflow D: planning and production

Input: accepted intent, current state, and the relevant planning level.

Steps:

```text
plan hierarchy → validate boundary → create contract → diverge options
→ author select → compile context → draft → review → settle
```

This workflow is detailed in [planning-hierarchy.md](planning-hierarchy.md) and [workflow.md](workflow.md).

## Workflow selection rule

The agent must state which workflow it selected and why before doing substantial work. If the input is ambiguous, it should preserve the ambiguity as a routing question instead of mixing reference analysis, invention, and canon updates in one output.

The CLI exposes the complete task vocabulary from the earlier workflows:
`idea`, `reference`, `import`, `planning`, `characters`, `world`, `research`,
`work`, `review`, `revision`, `benchmark`, and `continue`.
