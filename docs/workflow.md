# Workflow

## A. Project initialization

1. Capture author intent and project boundaries.
2. Create an empty project model.
3. Add only confirmed initial canon.
4. Define the review policy and human decision points.

## B. Planning

1. Build or update the hierarchy from project goals.
2. Define the next chapter contract.
3. Check that the contract does not exceed the current state or resolve more than intended.

## C. Creative divergence

For each contract, several specialized perspectives generate alternatives. A useful default set is:

- **Architect** — causal structure and downstream consequences.
- **Character** — motivation, agency, and relationship pressure.
- **Reader** — curiosity, clarity, and emotional movement.
- **Style** — voice, scene texture, and restraint.
- **Contrarian** — cliché, contradiction, pacing, and risk detection.

Each option is a structured artifact:

```text
option_id
contract_id
summary
beats
intended_reader_effect
canon_dependencies
new_assumptions
risks
open_questions
```

## D. Selection

The author records one of: `select`, `merge`, `edit`, `reject`, or `defer`. Selection includes a short rationale so later revisions can distinguish an author decision from an agent suggestion.

## E. Drafting

The context compiler assembles a bounded input package. The generator expands the selected beats and emits:

- candidate prose;
- beat execution notes;
- proposed state delta;
- unresolved questions;
- provenance metadata.

## F. Review and repair

Reviewers inspect the current draft against the contract and compiled evidence. Blocking findings must be repaired or explicitly deferred by the author before settlement.

## G. Settlement

After approval, the system applies the accepted delta to the appropriate layer:

```text
canon/       confirmed, durable facts
memory/active/   current working state
memory/draft/    proposed facts awaiting review
memory/archive/  superseded or historical material
issues/      unresolved conflicts and questions
```

## Two cooperating loops

```text
Creative loop:      diverge → compare → select → compose
Governance loop:    retrieve → verify → review → settle
```

The creative loop increases possibility. The governance loop controls commitment.

For production, these loops run inside the [S0–S6 strong-constraint protocol](strong-constraints.md). Creative divergence belongs before S1 drafting; evidence review and state settlement remain gated after drafting.
