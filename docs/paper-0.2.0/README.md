 # CanonLoom 0.2.0 论文

这是 CanonLoom 0.2.0 的独立系统设计论文目录。

## 文档

- [完整论文定稿版](paper.md)
- [论文结构提纲](outline.md)

## 图表

- [总体架构图](figures/canonloom-architecture.svg)
- [S0–S6 工作流图](figures/canonloom-stages.svg)
- [叙事状态图](figures/narrative-state.svg)

## 论文定位

本文是系统设计论文，不是已经完成跨架构文学质量对比的 benchmark 论文。当前版本报告协议、CLI、测试和最小项目路径的工程验证；文学质量、token 收益和作者体验需要按照论文第 10 节的受控实验方案单独采集。

## 发布约定（论文双份维护）

本目录的 `paper.md` 是论文的**源文件**，个人站 liyuk.github.io 的 `research` 集合是**发布版**（全文拷贝）：

| 位置 | 角色 |
|---|---|
| 本仓库 `docs/paper-0.2.0/paper.md` | 论文**源**（正文 + 图表 + 代码） |
| liyuk.github.io `src/content/research/2026/08/canonloom-auditable-narrative-production/zh.md` | 论文**发布版**（全文 + Astro frontmatter） |

**修改论文时，两处必须同步更新。** 已知的发布侧差异（已存在，勿回退）：

- liyuk 版开头多一段 Astro frontmatter（`title`/`description`/`createdAt`/`version`/`status`/`repositoryUrl`/`paperUrl`/`tags`）；
- liyuk 版多 `**日期：**` 行；
- liyuk 版末尾有一段发布侧导航附加（「完整论文与外部链接」）——这不是正文，同步正文时无需并入仓库源；
- 引号风格、图片路径按各自仓库约定（个人站用 `./images/` 打包图，仓库用 `figures/`），正文内容必须一致。

同步时可 `diff` 两个文件确认只差上述发布侧差异。
