# Generic project model

CanonLoom projects are content-agnostic. The architecture does not assume a particular genre, language, platform, existing intellectual property, or publishing model.

```text
project/
├── intent/
│   ├── author-intent.md
│   └── review-policy.md
├── canon/
│   ├── entities/
│   ├── rules/
│   ├── timeline/
│   └── sources/
├── plan/
│   ├── hierarchy.md
│   ├── arcs/
│   └── chapter-contracts/
├── workspace/
│   ├── options/
│   ├── selections/
│   ├── beats/
│   └── context-packages/
├── drafts/
├── reviews/
├── memory/
│   ├── active/
│   ├── draft/
│   └── archive/
├── issues/
└── traces/
```

The model is intentionally compatible with Markdown-first projects. Structured sidecar files can be added where validation, indexing, or automation requires them.

## State lifecycle

```text
observed → proposed → reviewed → approved → active → superseded
```

An item can also become `rejected` or `deferred` without entering active state.
