# 项目初始化协议

CanonLoom 的初始化不是“创建目录后直接写正文”，而是先建立项目边界。

## 作者控制的配置

作者填写或确认 `intent/author-setup.json`：

- 项目标题、语言、题材和子题材；
- 目标读者；
- 视角、时态、语气方向；
- 内容边界；
- 章节字数和对白比例；
- 自动化模式和审查强度；
- 作者备注和不可妥协事项。

这些字段在 `author_confirmed=true` 之前不能被视为最终项目约束。

也可以在 init 时直接提供第一批作者输入：

```sh
./bin/canonloom init ~/my-novel --name "Sample Story" \
  --genre "都市神秘" --audience "成人读者" \
  --pov close-third --tone "冷静,潮湿" \
  --chapter-min 3000 --chapter-max 7000
```

这些参数只写入 `author-setup.json`，不会自动设置 `author_confirmed=true`。

## AI 可以识别的内容

Agent 读取作者配置、已有稿件或参考材料后，可以把识别结果写入 `intent/ai-recognition.json`：

- 候选人物、地点、组织和时间线；
- 现有稿件中的开放循环；
- 可能的题材机制和叙事技法；
- 推断出的风格候选；
- 不确定性和待作者确认的问题。

AI 识别结果只能是 `PENDING` 或 `PROPOSED`。只有作者审阅后，才能变成 `AUTHOR_CONFIRMED`，再由后续工作流选择性晋升到 `canon/`。

## 推荐流程

```text
./bin/canonloom init
  ↓
./bin/canonloom --root ~/my-novel setup
  ↓
作者确认 author-setup
  ↓
Agent 识别 ai-recognition
  ↓
作者确认候选事实与 style-profile
  ↓
idea → planning → contract → work
```

如果是全新项目，AI 可以从空白开始提出候选；如果是旧稿导入，AI 必须给每个识别结果附来源文件和置信度。

作者确认配置后运行：

```sh
./bin/canonloom --root ~/my-novel setup --confirm
```

在确认之前，CanonLoom 不允许进入 planning、work、characters、world、research、revision 或 review；idea/reference 仍可用于探索和拆解。
