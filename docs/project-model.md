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

## 生效优先级

质量约束按以下顺序生效，越靠前越具体：

1. chapter contract
2. `intent/author-setup.json`
3. `intent/style-profile.json`
4. `canonloom.json` project defaults

因此，项目默认值不会覆盖作者配置，作者配置也不会覆盖单章契约。章节审查应报告最终采用的值。

## State lifecycle

```text
observed → proposed → reviewed → approved → active → superseded
```

An item can also become `rejected` or `deferred` without entering active state.
