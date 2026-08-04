# 社区项目与论文评审

这份文档不是项目致谢列表，而是 CanonLoom 的架构采纳记录：每个外部方向都区分“吸收什么、暂缓什么、为什么”。论文中的效果不能直接等价为工程效果；社区项目中的功能也不代表适合 CanonLoom 的无 GUI、单模型优先定位。

## 采纳原则

1. 先采用可解释、可回退、无第三方依赖的文件协议；
2. 再采用确定性检查，不把文学判断伪装成机械分数；
3. 多 Agent 先抽象成单模型多角色，不默认增加上下文同步成本；
4. 图谱先用 JSONL 和索引验证，出现性能瓶颈后再引入数据库；
5. 所有 AI 推断都经过候选、作者确认和正式状态晋升。

## 论文方向

| 论文 | 关键贡献 | 对 CanonLoom 的启发 | 当前决策 |
|---|---|---|---|
| [DOC](https://aclanthology.org/2023.acl-long.190/) | 详细分层大纲与生成控制，提高长篇情节连贯性 | 章契需要绑定可见状态变化，而不只是文本目标 | 已有层级规划，继续增加状态字段 |
| [Creating Suspenseful Stories](https://aclanthology.org/2024.eacl-long.147/) | 以叙事理论和迭代规划维持悬念 | 增加 reader question、reveal、setup/payoff 状态 | 部分采纳，先做揭示记录 |
| [DOME](https://aclanthology.org/2025.naacl-long.63/) | 动态层级大纲、记忆增强、时间冲突分析 | 计划要和实际状态做差异比较 | 已采纳可选状态层，暂不引入完整时间图数据库 |
| [StoryWriter](https://arxiv.org/abs/2506.16445) | outline、planning、writing 分离，并动态压缩历史 | 保留项目→章契→Beat，并增加章节状态摘要 | 吸收结构，不采用默认多 Agent |
| [Long Story Generation via Knowledge Graph and Literary Theory](https://arxiv.org/abs/2508.03137) | 长短期记忆、知识图谱、主题障碍和读者反馈 | 分离 active memory、draft memory、narrative state | 采纳分层思想，暂缓主题评分自动化 |
| [STORYTELLER](https://aclanthology.org/2025.findings-acl.1071/) | SVO 情节节点与叙事实体知识图谱持续交互 | 事件使用 subject/action/object 与 changes | 已落地 narrative-event schema |
| [Collective Critics](https://aclanthology.org/2024.emnlp-main.1046/) | 集体批评者优化创造性、连贯性和读者参与 | 需要多维 review rubric | 采用单模型多角色审查，不默认多模型 |
| [Can LLMs Generate Good Stories?](https://arxiv.org/abs/2506.10161) | 评估因果合理性、角色意图和戏剧冲突 | 章契需有 causal_change 和 character_agency | 已加入可选章契字段 |
| [Text-to-Text Automatic Story Generation Survey](https://aclanthology.org/2026.eacl-srw.39/) | 总结连贯性、一致性、多样性和评价缺口 | 机械检查与文学 rubric 必须分层 | 已纳入评估路线 |
| [Narrative World Model](https://arxiv.org/abs/2607.05577) | 叙事类型时间状态图、查询条件混合检索、多跳记忆评估 | 需要谁知道什么、何时知道、何时揭示 | 作为 P1，先用 JSONL，不直接上图数据库 |
| [MAGNET / ATLAS](https://arxiv.org/abs/2607.00918) | 角色目标驱动 Agent 与图状态一致性检查 | 角色目标、共享状态、跨场景检查有价值 | 吸收状态检查，暂缓角色 Agent 社会 |
| [SuperWriter-Agent](https://aclanthology.org/2026.findings-acl.428/) | 显式规划和反思式长文生成 | 增加计划偏差报告和修订循环 | 吸收反思产物，不强制增加模型轮次 |
| [Lost in Stories](https://aclanthology.org/2026.findings-acl.410/) | 针对长故事一致性 bug 的评测方向 | CanonLoom 需要公开、可复现的状态问答基准 | P1，先建立小型原创 benchmark |

## GitHub 社区方向

| 项目 | 社区实践 | CanonLoom 可吸收部分 | 不直接照搬的部分 |
|---|---|---|---|
| [autonovel](https://github.com/NousResearch/autonovel) | 从种子到成书、修订、排版、插图和发布，使用 modify-evaluate-keep/discard | 运行 manifest、候选版本、可重复实验 | 不把完整自动出版流水线放进核心 |
| [creative-writing-skills](https://github.com/haowjy/creative-writing-skills) | 文风文件、连续性检查、探索/批评/修订技能和知识库 | Agent skill 入口、风格 profile、工作模式 | 不绑定特定插件管理器 |
| [story-skills](https://github.com/danjdewhurst/story-skills) | Markdown + YAML frontmatter，兼容多种 Agent | 跨 Agent 文件协议、简单命令入口 | 不把 skill 安装机制当作核心状态机 |
| [novel-creator-skill](https://github.com/leenbj/novel-creator-skill) | 门禁、RAG、知识图谱、大纲锚点、跨 Agent 审核 | 多层约束、检索、事件图和回归检查 | 不默认五层系统全部启用 |
| [book-os / Novel-OS](https://github.com/forsonny/book-os) | Standards、Novel、Manuscripts 三层上下文 | 清晰区分项目标准、小说状态和正文 | CanonLoom 已有类似分层，继续加强迁移规则 |
| [authorclaw](https://github.com/Ckokoski/authorclaw) | 动态任务规划、技能选择、日志和完整出版 pipeline | 可审计任务日志、恢复和技能目录 | 不引入 dashboard、Telegram 或 API 依赖 |
| [inkos](https://github.com/Narcooo/inkos) | SQLite 时序记忆、相关性检索、通用规则和类型规则 | 将 JSONL 状态层演进为可选索引后端 | SQLite 作为可选后端，不进入第一阶段核心 |
| [NovelWriter](https://github.com/EdwardAThomson/NovelWriter) | GUI、多个模型后端、场景/章节/批量审查和质量趋势 | 批量审查、质量趋势和模型元数据 | 不改变 CanonLoom 的无 GUI 定位 |
| [GPTAuthor](https://github.com/dylanhogg/gptauthor) | prompt → synopsis → 人工审核 → 逐章生成 | 人工审阅大纲再进入正文 | CanonLoom 已将其扩展为章契和 S0–S6 |
| [agent-skills](https://github.com/jwynia/agent-skills) | 大量可复用的叙事、修订、研究和风格技能 | 将工作模式做成可选 skill | 不让技能隐式修改 canon |

## CanonLoom 当前差距

### 已经较强

- 作者批准和状态晋升边界；
- 单模型 + Python 的低耦合运行策略；
- context package、provenance、handoff 和 S0–S6；
- 纯文件、无 GUI、跨 Codex/Claude 的可移植性；
- 初始化时区分作者配置和 AI 识别提案。

### 仍然薄弱

- 事件、知识和揭示的结构化状态刚刚开始；
- 当前 `query` 主要是文本检索，不是查询条件的叙事检索；
- 质量报告更偏流程和表层指标，角色能动性与戏剧冲突仍依赖 Agent/作者；
- 没有公开的原创长篇一致性 benchmark；
- 还没有正式的 Codex/Claude/OpenCode adapter 包。

## 推荐迭代路线

### Phase 1：状态可见化

- narrative events、knowledge state、reveals；
- 事件重复 ID、来源、状态和揭示状态检查；
- 章契增加因果变化、角色能动性、读者状态；
- 不改变默认 S0–S6，保证兼容。

### Phase 2：状态驱动生产

- 章节完成后生成 planned-vs-actual deviation report；
- 查询按 fact、knowledge、reveal、setup/payoff 分类；
- 章节上下文只注入当前角色允许知道的内容；
- 将高风险状态检查作为可选 gate profile。

### Phase 3：可复现评估

- 建立原创小型长篇 benchmark；
- 评估因果、能动性、连贯、悬念、揭示控制和状态问答；
- 同模型、同上下文、同章节契约比较不同流程；
- 同时记录 token、延迟、重试和人工编辑量。

### Phase 4：可选后端和适配器

- SQLite/图数据库作为可选索引后端；
- Codex、Claude Code、OpenCode 的独立 adapter；
- 不改变核心 Markdown/JSON 协议。

## 结论

CanonLoom 不应该把论文中的多 Agent、图数据库、自动评分和复杂记忆一次性全部实现。更可靠的演进顺序是：

```text
显式状态
  → 状态验证
  → 状态驱动上下文
  → 可复现评估
  → 可选复杂后端
```

这样每一步都能单独运行、回退和评估，不会把一个轻量的作者工作流变成难以维护的自动化平台。
