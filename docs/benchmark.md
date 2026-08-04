# 竞品、token、耗时与 benchmark

## 先说结论

CanonLoom 当前最适合被理解为“可审计的小说生产架构”，而不是已经证明自己质量最高的生成模型或编辑器。它的优势在于状态、来源、审查、修订和作者批准被显式保存；代价是流程调用数比单次续写更多。

目前仓库没有完成外部架构的同条件实测，因此下面把事实、估算和实验计划分开。

## 架构对比

| 架构/项目 | 核心生产单元 | 主要优势 | 主要代价 | 与 CanonLoom 的关系 |
|---|---|---|---|---|
| 单次 Prompt 续写 | 一次请求 | 最快上手、token 最少 | 没有持久状态、审查和可恢复边界 | CanonLoom 增加合同、证据和门禁 |
| 全文上下文续写 | 大上下文窗口 | 信息看似完整 | 输入 token 高、噪声大、上下文仍可能遗漏 | CanonLoom 用 bounded context 替代全文注入 |
| NarrativeLoom | 多 persona 选项与协作创作 | 发散能力强、创意多样 | 多次生成、上下文同步成本高 | CanonLoom 保留 option/selection，但默认单模型 |
| NovelForge | 卡片、图谱、上下文引用和编辑器工作流 | 产品化和可视化强 | 依赖产品界面和较重的数据模型 | CanonLoom 是无 GUI、runtime-neutral 的执行协议 |
| Novel-OS / book-os | standards / novel / manuscripts 三层上下文 | 简单、易移植 | 审查证据、批准、来源追踪较弱 | CanonLoom 将三层状态扩展为可审计阶段产物 |
| autonovel | 从种子到修订的自动流水线 | 自动化程度高 | 容易把自动完成误当成作者批准 | CanonLoom 保留人工 settlement |
| graphify-novel | 人物、事件、关系图谱 | 长篇状态探索和连续性检查强 | 图谱维护成本、不能单独解决创意生产 | CanonLoom 把图谱视为 context/canon 层的一种实现 |
| oh-story-claudecode | 面向网文的技能和命令集 | 流程覆盖广、runtime 部署丰富 | 平台/类型假设较强，规则较重 | CanonLoom 抽取其流程思想，保持核心协议中立 |
| chinese-novelist-skill | 引导式整书会话 | 上手低、续写和恢复顺滑 | provenance、可逆状态和作者结算较弱 | CanonLoom 保留引导入口，强化状态边界 |
| novel-creator-skill | gates、检索、图谱、Beat、交叉审查 | 与长篇一致性最接近 | 多阶段/多 Agent 的 token 与协调开销较高 | CanonLoom 吸收其层次化流程，默认单模型 + Python |

详细来源和范围说明见 [direct-reference-comparison.md](direct-reference-comparison.md) 与 [landscape.md](landscape.md)。这些是架构对照，不是公开项目的质量排名。

## CanonLoom 的 token 估算

以下是“每章”规划区间，不是 API 账单。假设中文章节约 4,000–6,000 输出 tokens、上下文包 8,000–20,000 输入 tokens，模型和价格未固定。

| 工作模式 | 典型模型阶段 | 估算总 token | 估算模型请求耗时* | 适用场景 |
|---|---|---:|---:|---|
| 单次续写 | 1 次生成 | 15k–35k | 1–5 分钟 | 草稿试写、低风险片段 |
| 结构化单路径 | 规划 + 检索 + 生成 + 1 次审查 | 25k–55k | 3–10 分钟 | 常规章节 |
| CanonLoom Economy | 2 个 option + bounded context + 草稿 + 1 次 review | 30k–60k | 4–12 分钟 | 低风险章节 |
| CanonLoom Standard | 4 个 option + 生成 + quick/strict/independent review + 修订 | 55k–110k | 8–25 分钟 | 常规发布章节 |
| NarrativeLoom 式多模型发散 | 3–5 个 persona/option + 选择 + 生成 + review | 35k–80k | 6–18 分钟 | 创意探索、角色分歧 |
| CanonLoom Deep | 多 option + 修订 + 独立/交叉审查 + settlement | 90k–180k+ | 15–40 分钟 | 卷末、关键转折、发布候选 |

\* 耗时按串行模型请求估算；真实结果受模型服务、队列、并发、缓存和输出长度影响。Python 工具耗时应单独统计，通常不是主要成本。

### 为什么单模型 + Python 通常更省

多模型方案会重复发送相同的章契、人物状态、时间线和上下文包。若有 `n` 个模型，重复输入大致随 `n × context_tokens` 增长；而单模型方案可以让创作链共享一个上下文，Python 将规则检查从模型 token 中移出。

这不是说多模型永远更差：高风险章节可以用第二模型做隔离审查。但应把它当作额外 review 成本，而不是默认的上下文来源。

## 耗时统计方法

CanonLoom 将耗时拆成两部分：

```text
总耗时 = 模型调用耗时 + 本地确定性工具耗时 + 作者决策时间
```

运行 manifest 记录模型侧事件：

```sh
./bin/canonloom --root . retry S0 --work-id chapter-001 --reason "benchmark"
./bin/canonloom --root . record --stage S2 --model example-model \
  --input-tokens 12000 --output-tokens 1800 \
  --latency-ms 4200 --retries 0
```

测量本地工具开销：

```sh
python3 scripts/benchmark_overhead.py \
  --root /path/to/project \
  --contract plan/chapter-contracts/chapter-001.json \
  --chapter drafts/chapter-001.md
```

它只运行 Python 工具，不调用模型，输出 `reviews/benchmark-overhead.json`，包括每个工具的耗时、返回码和总耗时。

对同一章的 CanonLoom 与旧版 validator 结果汇总：

```sh
python3 scripts/benchmark_compare.py \
  --root /path/to/project --work-id chapter-001
```

它会生成 `reviews/benchmark-comparison.json` 和 `reviews/benchmark-comparison.md`。只有实际存在的 JSON 报告会被标记为 `MEASURED`；没有可执行外部 runtime 的架构会标记为 `NOT_EXECUTED`。

### 一次本地实测样例

在一个示例验证项目上，使用一章已有草稿、Python 3.9、本地文件系统运行上述命令，6 个确定性步骤总耗时为 **183.45 ms**：

| 步骤 | 耗时 |
|---|---:|
| beats | 28.51 ms |
| validate quick | 30.69 ms |
| validate strict | 30.69 ms |
| index | 30.86 ms |
| style | 30.04 ms |
| stats | 32.66 ms |

这只是一个机器、一个项目、一个章节的工具开销样例，不代表模型调用耗时，也不代表所有项目的性能上限。它说明在当前规模下，确定性 Python 层通常远小于一次模型请求；正式报告应在目标机器上重复多次并报告平均值、P95 和输入规模。

## 质量 benchmark：建议协议

要比较不同架构，固定以下变量：

1. 同一个模型、版本、temperature 和最大输出长度；
2. 同一批项目状态、章契、上一章、人物卡和时间线；
3. 同一批至少 20 个章节任务，覆盖普通章、人物转折、世界规则冲突和卷末章；
4. 同样的作者时间上限和修订次数；
5. 生成阶段与审查阶段分离，评分者盲评文本来源。

建议比较：

```text
A  单次 Prompt 续写
B  结构化单路径：章契 + bounded context + 1 次 review
C  多 persona/多模型发散
D  CanonLoom Economy
E  CanonLoom Standard
```

每个任务记录：

```text
input_tokens, output_tokens, latency_ms, retries,
tool_calls, author_minutes, revision_count,
continuity_errors, causal_errors, contract_findings,
style_findings, unresolved_blockers, author_acceptance
```

质量不要压成一个分数，至少报告：

| 维度 | 关注问题 |
|---|---|
| Continuity | 人物、时间、空间、设定是否连续 |
| Causality | 行动是否产生可理解的后果 |
| Contract fidelity | 是否完成本章变化、没有过度解决 |
| Character agency | 选择是否来自人物目标、知识和压力 |
| Reader promise | 悬念、情绪、信息和回收是否有效 |
| Style | 语气、节奏、对白区分度和 AI 痕迹 |
| Author effort | 作者选择、修订和批准耗时 |

## 当前可得的 benchmark 结论

当前仓库能直接证明的只有：

- CanonLoom 的 Python 工具不依赖第三方包；
- 本地校验、索引、上下文编译和统计可以独立运行；
- 每次 retry、工具调用和模型事件可以保存为可追溯记录；
- 当前没有足够的同条件外部运行数据，不能声称 CanonLoom 在质量、速度或 token 上击败上述项目。

首个正式 benchmark 应先跑 A–E 五组，再根据真实日志替换本页估算区间。任何跨项目表格如果没有写明模型、任务集和上下文，都只能作为架构讨论，不能作为实验结果。
