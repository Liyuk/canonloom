# CanonLoom 0.2.0 论文结构

## 1. 论文定位

这篇论文应被定位为：

> 面向长篇小说人机协作的、文件协议驱动的、可审计工作流架构。

它不是“单一模型生成小说质量最好”的论文，也不是新的语言模型或新的文学评分模型。论文的核心问题是：如何让 Agent 在长篇叙事生产中持续工作，同时控制状态漂移、未经批准的事实晋升、上下文膨胀和审查不可追溯。

## 2. 建议题目

中文题目：

> 从提示词到叙事生产：CanonLoom 0.2.0 的可审计长篇小说人机协作架构

英文题目：

> From Prompting to Narrative Production: CanonLoom 0.2.0, an Auditable Workflow Architecture for Human–AI Long-Form Fiction

备选题目：

> State, Gates, and Settlement: A File-Based Workflow for Reliable Human–AI Long-Form Story Production

## 3. 摘要结构

摘要建议按五句话组织：

1. 长篇小说生成的困难不只是上下文长度，还包括状态漂移、因果断裂、角色动机漂移和未经批准的故事事实进入正文。
2. 现有系统通常把规划、生成、记忆和审查耦合在一个 Agent 或多 Agent 对话中，难以恢复、复核和追踪决策来源。
3. CanonLoom 0.2.0 提出一个文件协议驱动的工作流，把作者意图、层级规划、章契、Beat、受限上下文、审查 Finding、叙事状态和作者批准结算分离。
4. 系统通过 S0–S6 阶段门禁、来源指纹、审查 provenance、可选叙事状态层和单模型 + Python 运行策略实现跨 Agent 的可恢复执行。
5. 本文通过消融实验、流程可靠性指标和原创章节案例评估该架构，重点衡量一致性、因果变化、角色能动性、状态可追踪性、token、延迟和作者负担，而不将机械指标等同于文学质量。

## 4. 论文贡献

建议只声明以下四项贡献：

### C1：长篇叙事生产的状态转换模型

将长篇写作建模为：

```text
author intent
→ plan
→ contract
→ bounded context
→ draft
→ review
→ repair
→ author-approved settlement
```

重点是区分：

- candidate 与 canon；
- draft 与 manuscript；
- finding 与 story fact；
- proposal 与 author decision；
- narrative state 与 active memory。

### C2：S0–S6 可审计生产协议

定义阶段产物、写入边界、状态转换、失败回退和作者批准点，使工作流可以从中断中恢复，并保留每次重试的 run manifest。

### C3：轻量叙事状态层

使用事件、知识状态和揭示状态表达：

- 发生了什么；
- 谁知道什么；
- 读者和主角分别知道什么；
- 哪些揭示仍然开放。

该层默认可选，不强迫所有项目一次性采用复杂知识图谱。

### C4：可靠性优先的运行策略

提出“单一主模型 + Python 确定性工具”的默认策略，并将多模型限制为隔离审查，而不是让多个模型共享可变隐式记忆。

## 5. 研究问题

### RQ1：结构化工作流能否减少跨章节状态错误？

比较单提示续写、结构化单路径和 CanonLoom 工作流在以下错误上的差异：

- 时间线冲突；
- 人物目标漂移；
- 未授权事实进入正文；
- 前章开放问题被无意解决；
- 章节出口状态与章契不一致。

### RQ2：显式章契和 Beat 是否提高可控性？

比较只有提纲、章契、章契 + Beat、章契 + Beat + causal/agency 字段的合同遵循率和人工修订量。

### RQ3：叙事状态层是否改善上下文选择？

比较全文上下文、目录级上下文、章契引用上下文和章契 + narrative state 上下文的：

- 输入 token；
- 状态问答准确率；
- 角色知识泄露率；
- 连贯性错误率；
- Agent 恢复成功率。

### RQ4：独立审查与 provenance 是否提升错误发现的可信度？

比较单次审查、同模型隔离审查、双模型隔离审查，并报告审查一致性、重复审查成本和误报率。

### RQ5：强约束带来的额外成本是否值得？

同时报告 token、延迟、重试次数、作者等待时间和人工修订时间，避免只报告生成质量或单章节最佳结果。

## 6. 背景与问题定义

### 6.1 长篇生成不是单次生成任务

说明长篇小说的状态具有：

- 跨章节持久性；
- 局部视角可见性；
- 时间顺序和因果约束；
- 作者批准和版本变更；
- 开放循环与延迟揭示。

### 6.2 现有工作流的四类失败

1. 上下文失败：上下文太长或混入不相关材料；
2. 状态失败：人物、设定、时间线漂移；
3. 决策失败：模型建议被误当成作者决定；
4. 评估失败：审查意见没有变成具体可回退的修订任务。

### 6.3 设计目标与非目标

目标：

- 可恢复；
- 可审计；
- 跨 Agent；
- 低依赖；
- 作者控制；
- 能逐步启用复杂能力。

非目标：

- 不保证文学质量；
- 不自动替作者批准 canon；
- 不默认采用多模型或多 Agent；
- 不把机械分数作为文学价值；
- 不提供 GUI 小说编辑器。

## 7. 系统架构

### 7.1 文件协议

介绍项目目录和关键 artifact：

```text
intent/
canon/
plan/
workspace/
drafts/
reviews/
memory/narrative-state/
manuscript/
traces/
handoffs/
```

说明 JSON Schema、Markdown 正文、JSONL 状态和 SHA-256 provenance 的职责边界。

### 7.2 层级规划

```text
project → volume → arc → chapter contract → beat → scene
```

解释为什么不同层级不能互相静默覆盖。

### 7.3 章契与状态变化

章契不仅描述“本章写什么”，还描述：

- required changes；
- forbidden changes；
- exit state；
- causal change；
- character agency；
- reader effect；
- reveal updates。

### 7.4 叙事状态层

说明三种状态文件：

- narrative events；
- knowledge state；
- reveal tracking。

强调 `optional`、`required`、`disabled` 三种采用模式。

### 7.5 上下文编译

说明上下文包如何记录：

- included files；
- excluded files；
- source hashes；
- authority；
- selection reason；
- current narrative state。

### 7.6 S0–S6 阶段门禁

用一个表格说明每个阶段的输入、输出、写入边界和失败路径。

特别说明：

- S5 的独立性是 review artifact/run 的独立，不等于必须使用第二个模型；
- S6 只在作者批准后执行；
- narrative state 不会自动晋升为 canon。

## 8. 运行策略

### 8.1 单模型 + Python

模型负责：

- 创意；
- 规划；
- 生成；
- 文学判断；
- 解释审查结果。

Python 负责：

- 文件和 Schema 检查；
- 字数和对白比例；
- Beat 证据检查；
- 索引和查询；
- provenance；
- 状态门禁；
- 运行记录。

### 8.2 多模型的边界

多模型只作为隔离的高风险 review pass。不得共享未记录的隐式记忆，也不得自动合并不同模型提出的状态。

### 8.3 三种运行深度

- economy：作者和 Agent 使用最少的 review；
- standard：完整章契、quick、strict 和独立审查；
- deep：关键章节使用额外审查和人工复核。

三种模式不改变作者批准和状态晋升边界。

## 9. 实现与可移植性

### 9.1 Agent 适配

说明 Codex、Claude Code、OpenCode 等系统只需要：

- 读取 `AGENTS.md` 或 `CLAUDE.md`；
- 读取 `tasks/current.md`；
- 执行 CLI；
- 写入协议目录。

### 9.2 无第三方依赖设计

说明为什么核心保持 Python 标准库和 Markdown/JSON/JSONL：便于安装、迁移、审计和恢复。

### 9.3 升级与兼容

说明 `canonloom upgrade` 只补齐安全结构，不改正文、canon、审查判断和作者决定。

## 10. 评估设计

### 10.1 数据集

不要使用真实私人小说或未授权文本。构建原创、匿名、跨题材的小型长篇任务集，每个项目包含：

- 作者意图；
- 世界规则；
- 人物卡；
- 前置章节摘要；
- 当前章契；
- 目标 Beat；
- 允许和禁止的状态变化。

### 10.2 对照组

建议至少包含：

1. single-prompt continuation；
2. outline-only workflow；
3. structured single-path；
4. CanonLoom without narrative state；
5. CanonLoom with narrative state；
6. CanonLoom deep review。

### 10.3 指标

可靠性：

- contract fidelity；
- beat evidence coverage；
- causal consistency；
- character agency consistency；
- knowledge leakage；
- reveal control；
- state recovery success。

成本：

- input tokens；
- output tokens；
- model calls；
- deterministic tool latency；
- end-to-end latency；
- retries；
- author edit time。

质量：

- 人工盲评连贯性；
- 人工盲评角色可信度；
- 人工盲评读者问题和悬念；
- 人工盲评语言和场景质量。

质量指标必须与机械指标分开报告。

### 10.4 消融实验

至少进行：

- 去掉 chapter contract；
- 去掉 Beat；
- 去掉 narrative state；
- 去掉 S5 独立审查；
- 去掉 bounded context；
- 单模型与多模型隔离审查对比。

### 10.5 运行记录

每个实验冻结：

- 模型和版本；
- system/developer prompt；
- 项目 seed；
- 章节 contract；
- 最大输出；
- temperature 或等效参数；
- context package hash；
- reviewer 配置。

结果报告均值、方差、失败案例和作者修改量，不只报告最佳章节。

## 11. 案例研究

使用一个完全原创的匿名示例，展示：

```text
seed
→ 3 个创意候选
→ 作者选择
→ 卷/篇章目标
→ 章契
→ Beat
→ context package
→ draft
→ finding
→ repair
→ proposed state delta
→ author-approved settlement
```

案例应展示至少一个失败的草稿和一次回退，证明门禁不是装饰性流程。

## 12. 讨论

讨论以下取舍：

- 更强约束可能减少创作速度和即兴性；
- provenance 和状态文件增加维护成本；
- 单模型减少上下文分叉，但可能降低审查多样性；
- 多模型提高观点多样性，但增加 token 和状态同步风险；
- 状态层提高可见性，但不等于自动理解文学因果；
- 机械验证能保证协议，不保证好小说。

## 13. 局限性

必须主动承认：

- 当前状态检索仍然是轻量文件级检索；
- Beat 的机械检查仍可能受措辞影响；
- 角色能动性和戏剧冲突依赖 Agent/作者判断；
- 小规模 benchmark 不能证明普遍文学质量提升；
- 不同 Agent 的文件遵循度可能不同；
- 作者审阅时间难以标准化。

## 14. 伦理、版权与安全

- 不将未授权作品作为公开 benchmark；
- 参考作品只提取抽象结构，不复制表达；
- 不把模型生成内容自动声明为事实；
- 保留作者批准和来源记录；
- 不在运行日志中提交 API key、私人路径和私人稿件。

## 15. 可复现性与附录

附录建议包含：

- 完整项目目录；
- chapter contract schema；
- narrative event schema；
- knowledge state schema；
- reveal schema；
- S0–S6 artifact examples；
- review provenance 示例；
- 一次失败运行的日志；
- token/延迟统计表；
- 运行命令和版本信息。

## 16. 结论

结论不要说 CanonLoom “解决了长篇小说生成”。更准确的结论是：

> CanonLoom 将长篇小说生产从不可追踪的 prompt continuation 转化为可分阶段、可恢复、可审计、作者可批准的状态转换流程。0.2.0 的主要价值在于明确边界和可靠性基础，而不是引入更多模型或更复杂的自动化。

## 17. 论文中必须避免的表述

- “保证生成高质量小说”；
- “自动解决长篇一致性”；
- “多 Agent 一定优于单模型”；
- “token 更少所以质量更高”；
- “通过 Schema 即可证明文学质量”；
- “S6 自动把所有状态写入 canon”。
