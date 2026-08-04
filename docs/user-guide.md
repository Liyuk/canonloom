# 作者使用指南

CanonLoom 是本地文件工作流。作者发出简单指令，Agent 读取任务、执行一个工作单元、写入可检查的产物；作者在关键节点做选择和批准。

## 最小日常循环

```sh
./bin/canonloom --root ~/my-novel status
./bin/canonloom --root ~/my-novel continue
```

如果是新项目：

```sh
./bin/canonloom init ~/my-novel --name "My Novel"
./bin/canonloom --root ~/my-novel idea
```

## 从创意到章节

```text
idea
  ↓
reference / import（可选）
  ↓
planning
  ↓
work
  ↓
continue + gate S0...S6
```

具体命令：

```sh
./bin/canonloom --root ~/my-novel idea --input "我想写一个关于选择的长篇故事"
./bin/canonloom --root ~/my-novel reference --input "分析参考作品的结构和节奏"
./bin/canonloom --root ~/my-novel import --input "盘点已有稿件，不要晋升为 canon"
./bin/canonloom --root ~/my-novel planning --work-id volume-001
./bin/canonloom --root ~/my-novel work --work-id chapter-001
./bin/canonloom --root ~/my-novel characters --input "校准本卷主要人物的目标和关系"
./bin/canonloom --root ~/my-novel world --input "推演当前规则下的三个事件分支"
./bin/canonloom --root ~/my-novel research --input "核验这一段现实资料及其使用边界"
./bin/canonloom --root ~/my-novel revision --work-id chapter-001
./bin/canonloom --root ~/my-novel review --work-id chapter-001
./bin/canonloom --root ~/my-novel continue
```

每个开始命令都会更新 `canonloom.json` 并生成 `tasks/current.md`。Agent 应先读取这两个文件，再执行任务。

## 三种工作模式

- `economy`：少量创意选项，适合普通章节。
- `standard`：多方案、有限上下文、阶段审查，默认推荐。
- `deep`：对关键卷、重大转折和出版前版本做更完整的交叉审查。

初始化时选择：

```sh
./bin/canonloom init ~/my-novel --mode economy
```

## 出问题时

```sh
./bin/canonloom --root ~/my-novel diagnose
./bin/canonloom --root ~/my-novel diagnose --json
./bin/canonloom --root ~/my-novel repair --dry-run
./bin/canonloom --root ~/my-novel repair
```

`repair` 只修复缺目录、缺配置字段和缺失任务文件，并在 `logs/repairs/` 留痕。内容冲突、事实错误、审查失败和作者决策不会被自动处理。

## 作者决策点

作者需要明确决定：

- 选择、合并或拒绝哪些创意方案；
- 哪些新事实可以进入候选记忆或 canon；
- 审查问题是否阻断交付；
- 是否批准 S6 settlement；
- 是否改变已经确认的规划。

## 数据层

```text
intent/                 作者意图和审查政策
canon/                  已确认事实
plan/                   项目、卷、篇章和章契规划
workspace/              方案、选择和上下文包
drafts/                 候选草稿
reviews/                审查报告
memory/active/          当前工作状态
memory/draft/           待确认候选事实
manuscript/             已批准稿件
issues/                 未解决问题
traces/                 阶段轨迹
```

原则是：草稿不是 canon，摘要不是来源，Agent 的建议不是作者决定。

## 运行时说明

Codex App 和 Claude Code 可以在有本地目录和终端权限时直接使用项目；普通聊天 App 只能在上传文件后提供建议，不能可靠地运行命令或维护项目状态。更完整的说明见 [Terminal、API 与 App](terminal-and-apps.md) 和 [Runtime adapters](runtime-adapters.md)。
