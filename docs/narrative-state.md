# 叙事状态层

叙事状态层是 CanonLoom 的可选增强，不会自动改变原有 S0–S6 门禁。它用于记录“故事发生了什么、谁知道什么、哪些揭示仍然开放”，减少长篇创作中的状态漂移。

## 文件

```text
memory/narrative-state/
  state-policy.json
  events.jsonl
  knowledge.jsonl
  reveals.json
```

## 渐进使用

```sh
./bin/canonloom --root ~/my-novel state report
./bin/canonloom --root ~/my-novel state validate
```

新项目默认 `narrative_state.mode=optional`。建议分三步采用：

1. 先让 Agent 为关键章节记录事件，不改变门禁；
2. 用 `state validate` 检查重复 ID、状态值、来源和揭示状态；
3. 连续运行稳定后，再把指定状态检查加入章节契约或项目门禁。

## 事件

事件使用主语、动作、宾语和状态变化表达：

```json
{
  "event_id": "E-001",
  "chapter_id": "chapter-001",
  "source_ref": "manuscript/chapter-001.md",
  "subject": "protagonist",
  "action": "discovers",
  "object": "sealed letter",
  "changes": ["protagonist possesses sealed letter"],
  "knowledge_delta": ["protagonist knows the letter exists"],
  "status": "PROPOSED"
}
```

AI 可以提出 `PROPOSED` 事件；只有作者确认后，事件才可以进入 `CONFIRMED`。是否进一步写入项目 `canon/`，仍需经过对应的作者批准和结算流程。

## 知识状态与揭示

`knowledge.jsonl` 区分角色掌握的事实，`reveals.json` 区分读者、主角和作者知道的内容。它们不是普通全文记忆，不能被 Agent 当作无来源的自由背景使用。

## 与 S0–S6 的关系

当前状态层不强制加入 S0–S6，避免一次升级破坏现有项目。未来可以在章契中增加：

- `causal_change`：本章因果变化；
- `character_agency`：人物目标、选择和代价；
- `reader_effect`：打开和关闭的阅读问题；
- `reveal_updates`：本章允许的揭示变化。

字段协议见 `schemas/chapter-contract.schema.json`、`schemas/narrative-event.schema.json`、`schemas/knowledge-state.schema.json` 和 `schemas/reveal.schema.json`。
