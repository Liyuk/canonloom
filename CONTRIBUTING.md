# Contributing to CanonLoom

感谢贡献。CanonLoom 的核心目标是保持工作流可读、可恢复、可审计，并且不绑定某一家模型。

## 提交前检查

```sh
python3 -m py_compile scripts/*.py
python3 -m unittest discover -s tests -q
git diff --check
```

## 设计约束

- 不把模型调用写死在核心 CLI；
- 不让 `repair` 修改 canon、正文或作者决定；
- 不跳过 S0–S6 阶段；
- 新增 JSON 产物必须有 schema 或明确的协议说明；
- 机器协议字段保持英文稳定，文档和项目内容可以本地化；
- 新增行为应补充最小可复现测试。

## Pull request 内容

请说明变更目的、影响的协议或目录、测试结果，以及是否改变了 Agent 的写入边界。不要提交真实小说、私有密钥、未授权参考文本或包含敏感路径的运行日志。
