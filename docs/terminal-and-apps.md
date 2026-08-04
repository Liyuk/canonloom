# Terminal、API 与 App 使用说明

CanonLoom 的核心接口是本地文件和命令，不是某个模型的隐藏记忆。它可以被终端、Codex、Claude Code 或其他能读写项目目录的 Agent 使用。

推荐运行方式是“单一主模型 + Python 检查”：模型保持创作上下文，Python 负责确定性的校验、索引、来源指纹、交接包和门禁。`record` 命令可以记录 token、延迟、重试、模型与 provider，不绑定具体模型 API。

## 最轻量方式

只需要 Python 3.9+，项目本身不依赖第三方包：

```sh
git clone <your-canonloom-repo>
cd canonloom
./bin/canonloom init ~/my-novel --name "My Novel"
cd ~/my-novel
./bin/canonloom setup
./bin/canonloom idea
./bin/canonloom continue
```

作者日常只需记住四个命令：

```sh
./bin/canonloom status       # 我现在在哪里？
./bin/canonloom continue     # 继续下一步
./bin/canonloom diagnose     # 出了什么问题？
./bin/canonloom repair       # 修复安全的结构问题
```

## CLI 命令表

| 命令 | 作用 | 是否改变内容 |
|---|---|---|
| `init` | 初始化项目目录和状态 | 创建空结构 |
| `setup` | 作者配置和 AI 识别入口 | 创建/更新 setup 任务 |
| `idea` | 开始创意探索 | 创建任务提示 |
| `reference` | 开始拆书/参考作品分析 | 创建任务提示 |
| `import` | 导入已有稿件盘点 | 创建任务提示 |
| `planning` | 进行项目、卷、篇章、章契规划 | 创建任务提示 |
| `work` | 开始一个工作单元 | 创建任务提示 |
| `continue` | 根据当前状态继续工作 | 创建任务提示 |
| `route "..."` | 将自然语言路由到工作流 | 只读 |
| `status` | 查看项目状态 | 只读 |
| `diagnose` | 检查项目结构和状态 | 只读 |
| `repair` | 修复安全、可逆的结构问题 | 只改结构/任务/配置字段 |
| `gate S0...S6` | 检查阶段产物和顺序 | 更新阶段状态 |

所有命令都支持：

```sh
./bin/canonloom --root /path/to/project status
```

## 自我修复机制

```text
diagnose → identify issue → repair safe items → diagnose again
```

`repair` 可以自动处理：

- 缺少的标准目录；
- 缺失的配置字段；
- 缺失的 `tasks/current.md`；
- 根据当前 `next_action` 恢复一个待执行任务。

它不会自动处理：

- `canon/` 中的事实冲突；
- 稿件内容和文学质量问题；
- 作者选择、审批和状态晋升；
- 缺失或不可信的审查结论；
- 通过删除文件来“修复”问题。

先预览再执行：

```sh
./bin/canonloom repair --dry-run
./bin/canonloom repair
./bin/canonloom retry S0 --work-id chapter-001 --reason "修订后重新跑全流程"
./bin/canonloom diagnose --json
./bin/canonloom handoff --work-id chapter-001 --source-stage S2 --next-action S3 --files drafts/chapter-001.md --reports reviews/chapter-001.quick.json
./bin/canonloom record --stage S2 --model my-model --input-tokens 10000 --output-tokens 1500 --latency-ms 4000
```

每次实际修复都会记录到 `logs/repairs/repair-*.json`，包含修复前状态、执行动作和修复后状态。

## S0–S6 阶段门禁

Agent 完成阶段产物后，运行：

```sh
./bin/canonloom gate S0 --work-id chapter-001
./bin/canonloom gate S1 --work-id chapter-001
./bin/canonloom settle --work-id chapter-001
```

门禁会检查产物是否存在，以及是否按顺序经过前一阶段。S6 还要求作者明确批准：

```json
{
  "approval": "AUTHOR_APPROVED",
  "action": "approve_settlement"
}
```

CLI 不会判断一章小说是否写得好，它只保证工作流没有悄悄越界。

S6 门禁会先确认 approval，并生成与当前 revised draft 绑定的 settlement trace；随后 `settle` 再确认项目已经通过 S6、approval、trace 和 revised draft 的 work_id/路径一致。直接调用 settle 不能绕过 S6。

## Terminal API 与脚本调用

CanonLoom 当前没有远程 HTTP API。Terminal API 指稳定的命令行接口和文件接口。

Shell：

```sh
./bin/canonloom --root "$PROJECT" status
./bin/canonloom --root "$PROJECT" diagnose --json
```

Python 子进程：

```python
import subprocess

subprocess.run(
    ["python3", "scripts/canonloom.py", "--root", project, "continue"],
    check=True,
)
```

机器读取状态时使用 `canonloom.json`；机器读取诊断时使用 `diagnose --json`；Agent 读取当前任务时使用 `tasks/current.md`。阶段产物的文件名和写入边界见 [strong-constraints.md](strong-constraints.md)。

## App 能力边界

### Codex App

打开或添加项目目录后，可以读取 `AGENTS.md`、`canonloom.json`、`tasks/current.md`，并在有终端/文件权限时执行 CLI、生成产物和运行门禁。

### Claude Code

打开项目后读取 `CLAUDE.md`，可以执行同样的 CLI 和文件工作流。它与 Codex 使用相同的 Markdown、JSON、阶段产物和审批边界。

### 普通 Claude / ChatGPT 聊天 App

如果没有本地目录访问或终端能力，只能读取上传的文件、给出建议或生成文本，不能可靠地运行 `diagnose`、`repair`、`gate`，也不能维护项目状态。此时应使用 Codex App、Claude Code，或手动上传必要的任务和状态文件。

### App 不能替代的部分

任何 App 都不能替作者完成最终 canon 批准。Agent 可以提出创意、写草稿、发现问题和生成修复方案，但 S6 settlement 仍然需要作者批准。
