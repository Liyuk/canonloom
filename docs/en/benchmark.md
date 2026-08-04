# Benchmark and Comparison Notes

CanonLoom should be understood as an auditable production architecture, not as a proven ranking of model quality. The repository does not currently claim a controlled, same-model comparison against every external framework.

## What the numbers mean

Keep these categories separate:

1. local measured runtime for CanonLoom's Python tools;
2. token and latency estimates derived from call structure;
3. future controlled cross-framework experiments using the same model, task, context, and evaluation rubric.

The second category must not be presented as the third.

## Trade-off

Single-prompt continuation has the lowest setup cost. CanonLoom spends more calls on contracts, bounded context, validation, review, repair, and approval. The intended benefit is recoverability, provenance, continuity, and author control rather than minimum token use.

The default recommendation remains one primary model plus Python. Multiple-model review is optional and should be isolated so that hidden context is not accidentally merged.

See the Chinese benchmark document for the current comparison table and assumptions: [benchmark.md](../benchmark.md).
