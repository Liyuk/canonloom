# CanonLoom

> 一个命令驱动、作者掌舵、可审计的长篇小说生产框架。

[English README](README.en.md)

版本：`0.2.1` · [变更记录](CHANGELOG.md)

CanonLoom 不是 GUI 写作软件，也不是“一句话自动生成整本小说”的黑箱。它把小说生产拆成一组可恢复、可检查、可交接的任务：创意、拆书、规划、章契、Beat、上下文编译、生成、修订、审查和结算。

作者只需要执行简单指令；Codex、Claude Code 或其他 Agent 读取任务文件并完成具体创作；Python 脚本负责确定性检查、索引、来源追踪、运行记录和阶段门禁。

## 语言策略

CanonLoom 不把“AI 使用语言”和“小说产物语言”混成一个约束：

- JSON schema、状态值、命令和路径使用稳定的英文键名，方便跨模型和跨语言工具处理；
- `AGENTS.md`、`CLAUDE.md` 和任务提示可以中英双语；
- 小说正文、作者意图、审查意见默认跟随 `intent/author-setup.json` 的 `language`；
- Agent 可以用作者更容易确认的语言解释，但必须保持 JSON 协议、目录边界和审批状态不变。

详细规则见 [Language Policy](docs/language-policy.md)。

## 它解决什么问题？

长篇小说最容易坏在章节之间：人物动机漂移、时间线断裂、设定未经批准就进入正文、上下文越来越大、审查意见没有转化成修订任务。

CanonLoom 的核心原则是：

```text
创意不是 canon
候选不是决定
草稿不是定稿
审查意见不是事实
记忆候选不是 active memory
```

每个重要故事变化都应该能追溯到：作者意图、章契、选中的方案、上下文来源、审查 Finding 和作者批准。

## 当前架构

```text
author intent
      ↓
project / volume / arc / chapter contract / beats
      ↓
bounded context package + provenance
      ↓
draft → quick validation → repair plan
      ↓
strict validation → independent review → optional cross-review
      ↓
author approval → settlement → manuscript + state settlement trace
```

强约束阶段为 S0–S6：

```text
S0 Contract
  ↓
S1 Draft → S2 Quick Check → S3 Repair
  ↓
S4 Strict Check → S5 Independent Review → S5b Cross-Validation
  ↓
S6 Human-Approved Settlement
```

阶段不能跳过。S6 没有作者批准文件时，系统不会把草稿晋升到 `manuscript/`；叙事状态也不会自动晋升为 canon。

## 推荐运行方式：单一模型 + Python

默认建议是一个主模型贯穿创意、规划、写作、修订和审查，再由 Python 执行确定性工作：

```text
一个模型：保持创作上下文和人物/风格连续性
Python：校验、索引、上下文 provenance、handoff、token/耗时记录、gate
```

这样可以减少多个模型重复读取上下文造成的 token 浪费，也减少不同模型对 canon 的理解分叉。多模型交叉仍可作为高风险章节的可选实验，但不建议作为默认工作流；如果使用，应保持上下文隔离，只比较报告，不合并隐式记忆。

## 两分钟开始

要求：Python 3.9+，无第三方依赖。

```sh
git clone <your-canonloom-repo>
cd canonloom

./bin/canonloom init ~/my-novel --name "My Novel"
./bin/canonloom --root ~/my-novel setup
./bin/canonloom --root ~/my-novel idea
./bin/canonloom --root ~/my-novel continue
```

`init` 之后先完成 setup：作者配置题材、受众、视角、文风方向和内容边界；Agent 再把已有材料识别成候选人物、世界、线索和技法。作者配置与 AI 识别分开保存，AI 推断不会自动进入 canon。

```text
作者确认 → intent/author-setup.json
AI 识别提案 → intent/ai-recognition.json
文风约束 → intent/style-profile.json
确认后 → idea / planning / work
```

作者确认初始化配置：

```sh
./bin/canonloom --root ~/my-novel setup --confirm
```

作者日常最常用的命令：

```sh
./bin/canonloom --root ~/my-novel status       # 当前处于什么阶段？
./bin/canonloom --root ~/my-novel continue     # 按 next_action 继续
./bin/canonloom --root ~/my-novel diagnose     # 检查结构和状态
./bin/canonloom --root ~/my-novel repair       # 修复安全的结构问题
./bin/canonloom --root ~/my-novel upgrade      # 将旧项目补齐到当前协议结构
./bin/canonloom --version                      # 查看框架版本
./bin/canonloom --root ~/my-novel state report # 汇总可选叙事状态
./bin/canonloom --root ~/my-novel state validate # 校验事件、知识与揭示
./bin/canonloom advanced                       # 查看 Agent/维护层工具
```

最小示例可以直接运行：

```sh
examples/minimal-project/smoke.sh
```

创作入口：

```sh
./bin/canonloom --root ~/my-novel setup      # 完成作者配置和 AI 识别入口
./bin/canonloom --root ~/my-novel idea         # 创意产生
./bin/canonloom --root ~/my-novel reference    # 拆书/分析参考作品
./bin/canonloom --root ~/my-novel import       # 导入已有稿件
./bin/canonloom --root ~/my-novel planning     # 项目 → 卷 → 篇章 → 章契 → Beat
./bin/canonloom --root ~/my-novel work         # 开始一个工作单元
./bin/canonloom --root ~/my-novel characters   # 人物校准
./bin/canonloom --root ~/my-novel world        # 世界规则推演
./bin/canonloom --root ~/my-novel research     # 资料核验
./bin/canonloom --root ~/my-novel revision     # 问题驱动修订
./bin/canonloom --root ~/my-novel review       # 审查
```

命令只负责准备可读的任务文件。Agent 读取 `tasks/current.md`，执行任务并把产物写入约定目录。

普通作者不需要学习 `gate`、`context`、`handoff`、`artifact-check` 等内部工具。它们仍然存在，主要由 Agent 或维护者调用；运行 `canonloom advanced` 可以查看完整列表。

## 运行记录与自我修复

每次重新验证都会创建独立运行目录：

```text
runs/<work-id>/<run-id>/manifest.json
```

其中记录阶段、运行策略、工具调用、输入/输出 token、延迟、重试和事件。上下文包、章节索引也会记录来源文件的 SHA-256 指纹。

```sh
./bin/canonloom --root ~/my-novel retry S0 --work-id chapter-001 --reason "修订后重新验证"
./bin/canonloom --root ~/my-novel record --stage S2 --model my-model \
  --input-tokens 10000 --output-tokens 1500 \
  --latency-ms 4000 --retries 0
./bin/canonloom --root ~/my-novel handoff --work-id chapter-001 \
  --source-stage S2 --next-action S3
```

`diagnose → repair → diagnose` 只修复目录、配置字段、任务文件等安全结构问题，不会替作者改 canon、正文、审查结论或批准状态。`upgrade` 是面向旧项目的显式入口，当前只执行同一组安全迁移。

## Codex、Claude 和其他 Agent

项目通过普通文件工作，不依赖某个模型的隐藏记忆：

- `AGENTS.md`：Codex、OpenCode 等 Agent 的入口说明；
- `CLAUDE.md`：Claude Code 的入口说明；
- `canonloom.json`：项目状态和工作流配置；
- `tasks/current.md`：当前可执行任务；
- `schemas/`：配置、章契、Finding、handoff、run manifest 等协议；
- `scripts/`：无第三方依赖的确定性工具。

Codex App 和 Claude Code 在拥有项目目录、文件权限和 Terminal 时可以直接运行。没有本地文件/Terminal 权限的普通聊天 App，只能处理上传的文件，不能可靠维护项目状态。

## 竞品与 benchmark

CanonLoom 当前不宣称已经完成跨项目的受控质量排名。不同项目的模型、提示词、上下文、任务和版本并不相同，直接拿公开样例比较会误导。

当前定位和参考架构对比见：

- [竞品与参考架构对比](docs/benchmark.md)
- [三个直接参考项目的详细比较](docs/direct-reference-comparison.md)
- [项目生态概览](docs/landscape.md)

benchmark 文档区分三类数字：

1. CanonLoom Python 工具的本地实测耗时；
2. 基于调用结构的 token/耗时估算；
3. 未来在同一模型、同一任务集下进行的跨架构实测。

目前不能把第 2 类数字写成第 3 类结果。

## 文档入口

- [完整使用说明：Terminal、API 与 App](docs/terminal-and-apps.md)
- [作者使用指南](docs/user-guide.md)
- [工作流总览](docs/workflow.md)
- [系统架构](docs/architecture.md)
- [强约束 S0–S6](docs/strong-constraints.md)
- [生产工具](docs/production-tools.md)
- [运行时适配](docs/runtime-adapters.md)
- [Style Profile 文风协议](docs/style-profile.md)
- [竞品、token、耗时与 benchmark](docs/benchmark.md)
- [Schemas](schemas/)
- [叙事状态层](docs/narrative-state.md)
- [社区项目与论文评审](docs/research-review.md)
- [0.2.0 论文结构](docs/paper-0.2.0/outline.md)
- [0.2.0 完整论文初稿](docs/paper-0.2.0/paper.md)
- [迭代路线与 P2 方案](docs/iteration-roadmap.md)

## 项目边界

CanonLoom 提供可执行的流程、文件协议、检查器、门禁和审计轨迹；模型调用、文学判断和最终 canon 批准仍由连接的 Agent 与作者负责。

这不是“去 AI 化”项目，而是“AI 解耦”项目：Agent 负责创意、规划、写作和解释；Python 负责确定性校验、阶段迁移、来源追踪和审计；作者负责正式配置、选择和最终批准。AI 输出默认是候选或 Finding，不会自动成为 canon。

## 对外使用前检查

公开仓库建议补充自己的 `LICENSE`、示例项目、贡献指南和版本说明；不要把真实小说、私有 API key、未授权参考文本或运行日志中的敏感路径提交到仓库。推荐先运行：

```sh
python3 -m py_compile scripts/*.py
python3 -m unittest discover -s tests -q
python3 scripts/public_check.py --root .
git diff --check
```

## License

MIT — see [LICENSE](LICENSE).

对外贡献与安全说明见 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [SECURITY.md](SECURITY.md)。
