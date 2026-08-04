# Strong-constraint production protocol

CanonLoom's production workflow is a state machine. A stage is not complete because an agent says it is complete; it is complete only when its required artifact and checks exist.

## S0–S6 pipeline

```text
S0 Contract Gate
  ↓
S1 Draft
  ↓
S2 Quick Check
  ↓
S3 Repair
  ↓
S4 Strict Check
  ↓
S5 Independent Review
  ↓
S5b Cross-Validation
  ↓
S6 Human-Approved Settlement
```

## Stage contracts

The default artifact names used by the CLI are:

```text
S0  plan/chapter-contracts/{work_id}.json
    workspace/selections/{work_id}.json
    workspace/context-packages/{work_id}.json
S1  drafts/{work_id}.md
S2  reviews/{work_id}.quick.json
S3  drafts/{work_id}.revised.md
    reviews/{work_id}.repair.json
S4  reviews/{work_id}.strict.json
S5  reviews/{work_id}.independent.json
S5b reviews/{work_id}.cross-validation.json
S6  tasks/{work_id}.approval.json
    traces/{work_id}.settlement.json
```

An adapter may use another naming scheme, but it must expose the same artifact roles.

Contracts may additionally declare `beats`, the four execution fields, bounded
length, forbidden terms/punctuation, and dialogue-ratio bounds. These are
validation inputs, not permission for an agent to invent missing facts.

| Stage | Reads | Must produce | Write boundary | Blocking rule |
|---|---|---|---|---|
| S0 | intent, current contract, relevant state, minimal canon | contract report | `plan/`, `reviews/` | no draft if contract is blocked |
| S1 | passed contract, compiled context, style policy | candidate draft + self-report | `drafts/`, `traces/` | never write canon or manuscript |
| S2 | current draft only | deterministic quick findings | `reviews/`, `traces/` | does not rewrite prose |
| S3 | draft, findings, contract, named evidence | repair draft + repair report | `drafts/`, `reviews/` | no new facts during repair |
| S4 | repaired draft | strict check result | `reviews/`, `traces/` | BLOCKER/MAJOR findings must be resolved or escalated |
| S5 | draft, contract, evidence, current state | independent review pass | `reviews/` | independent means a new review artifact with `review_id`, `reviewer_mode`, `run_id`, and `source_sha256`; it does not require a second model, but it cannot reuse the Strict review id/run |
| S5b | S4 result + S5 report | cross-validation/reconciliation report | `reviews/`, `traces/` | may compare two isolated reports from one model or multiple models; disagreement becomes human decision |
| S6 | explicitly approved draft, reports, accepted delta | handoff, settlement, indexes | `manuscript/`, `memory/`, `traces/` | no approval means no promotion |

## Status protocol

Every stage log must include these fields, even when the value is `NONE`:

```text
STATUS: COMPLETED | BLOCKED | NEEDS_REVIEW | FAILED | NOT_RUN
ACTUAL_CHANGES: <what changed>
PRESERVED_RISKS: <what remains risky>
OPEN_LOOPS: <new, closed, or unchanged open loops>
NEXT_STAGE: S0 | S1 | S2 | S3 | S4 | S5 | S5b | S6 | HUMAN_DECISION | STOP
```

## Severity

```text
BLOCKER  canon, causality, viewpoint, or project-boundary failure; blocks promotion
MAJOR    major structure, continuity, contract, or reader-promise failure; blocks promotion
MINOR    local quality issue; repair recommended
ADVISORY non-blocking style suggestion
```

`BLOCKER` and `MAJOR` findings cannot be hidden by a high overall score. A stage may end as `NEEDS_REVIEW` when the next action belongs to the author.

## Transition rules

Normal path:

```text
S0 → S1 → S2 → S3 → S4 → S5 → S5b → S6
```

Allowed repairs:

```text
S0 → HUMAN_DECISION
S2 → S3
S4 → S3
S5 → HUMAN_DECISION | S3
S5b → HUMAN_DECISION | S3
```

Never allowed:

- S0 → S6;
- S1 → S6;
- S4 → S6 when BLOCKER/MAJOR findings remain unresolved;
- any stage → Canon promotion without explicit author approval;
- a reviewer directly editing the manuscript as its only evidence.

## Settlement rules

S6 is a projection step, not a new creative step. It may:

- promote the explicitly approved draft to `manuscript/`;
- apply an approved state delta to `memory/active/`;
- create `memory/draft/` candidates;
- update indexes and handoff files;
- preserve unresolved risks and open loops.

It may not silently invent, summarize away, or approve changes. `canon/` promotion always requires an explicit author decision and an evidence reference.

## Retry policy

- S2 quick checks: one mechanical rerun after a mechanical repair.
- S3 structural repair: at most two attempts before human decision.
- S4 strict failure: return to S3; never skip strict validation.
- S5 review disagreement: preserve both reports and escalate; do not average them away.
- S6 failure: leave the approved draft and reports intact; rerun settlement only.
- An already-settled chapter must be reopened with an explicit `retry S0` (or a narrower approved retry stage). The retry preserves old artifacts and starts a fresh verification pass; it must not silently move `stage_id` backward.

## Runtime-neutral handoff

Claude Code, Codex, or another agent may own the stages. The handoff unit is:

```text
current draft + contract + current state + latest stage reports + accepted decisions
```

Never hand off hidden model memory or an untraceable summary as the only context.
