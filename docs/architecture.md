# Architecture

## Overview

CanonLoom treats long-form writing as a controlled state-transition system rather than a single prompt-to-prose operation.

```text
Project Intent
    ↓
Canon Store ─────── Timeline / Entity / Relation / Rule / Source
    ↓
Planner ─────────── Volume → Arc → Chapter Contract → Beat Sheet
    ↓
Divergence Studio ─ Multiple options from the same contract
    ↓
Author Selection ── One selected path + rationale
    ↓
Context Compiler ── Minimal, versioned evidence package
    ↓
Generator ───────── Beats → scenes → candidate draft
    ↓
Reviewers ───────── Structure / continuity / style / reader promise
    ↓
Evidence Report ─── Finding → evidence → severity → repair
    ↓
Decision Gate ───── Author approves, revises, or defers
    ↓
State Settlement ── settlement trace / proposed delta / open issue
```

## Components

### 1. Intent layer

Stores the author's durable goals: audience, genre, tone, boundaries, themes, desired automation level, and non-negotiable creative principles. Intent is guidance, not a license for an agent to rewrite canon.

### 2. Canon and state store

The source of truth for confirmed facts and current state. A claim should carry its source, status, confidence, validity interval, affected entities, and review history. Candidate facts remain separate until the author approves them.

### 3. Planner

Builds hierarchical plans and chapter contracts. A contract constrains the causal skeleton while preserving room for prose-level invention.

### 4. Divergence Studio

Generates multiple alternatives from the same approved contract. Personas are perspectives, not independent authorities. Every option must expose its assumptions, intended effect, risks, and canon dependencies.

### 5. Author Selection Gate

The author selects, combines, edits, or rejects options. The selected option becomes an explicit decision artifact before drafting begins.

### 6. Context compiler

Builds a bounded, versioned evidence package from selected canon, workflow state, narrative state, and style constraints. It records what was included and why; deeper relevance filtering remains a later iteration.

### 7. Generator

Expands the selected beats into a candidate draft. The generator may propose state changes but cannot silently promote them to canon.

### 8. Reviewers

Reviewers are separated by concern: structure and causality, continuity and provenance, style and language, reader promise, and deterministic checks. Each produces evidence-backed findings rather than an undifferentiated score.

### 9. State settlement

Turns an approved draft into an immutable settlement trace and explicit proposed deltas. The current implementation promotes approved prose to `manuscript/` and records state-promotion decisions; narrative state remains separately reviewable until an author approves a specific delta.

## Hard boundaries

1. A draft is not canon.
2. A summary is not a source unless explicitly promoted.
3. A reviewer finding is not a fact.
4. A creative option is not a decision.
5. An agent cannot approve its own memory update.
6. Every accepted state change must point to evidence.
