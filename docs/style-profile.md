# Style Profile

`intent/style-profile.json` 是项目级文风协议。它把“这个项目应该怎么写”从某一章的临时 prompt 中抽出来，供 Agent 阅读、上下文编译和 Python 检查共同使用。

它分成两层：

```text
可机械检查：字数、句段节奏、对白比例、禁用词、禁用标点
需要文学判断：叙述距离、语气、意象、对白潜台词、情绪表达
```

初始化项目会生成一个空的风格模板。项目作者应把它改成自己的 profile，例如：

```json
{
  "schema_version": "0.1",
  "profile_id": "harbor-mystery-v1",
  "name": "潮湿、克制的调查叙事",
  "narrative": {
    "viewpoint": "close-third",
    "distance": "observational",
    "tense": "past",
    "register": "restrained",
    "voice_keywords": ["冷静", "潮湿", "证据驱动"],
    "avoid_tendencies": ["直接解释情绪", "对白讲解世界观"]
  },
  "rhythm": {
    "min_avg_sentence_cjk": 8,
    "max_avg_sentence_cjk": 36,
    "max_long_sentence_cjk": 120
  },
  "dialogue": {
    "min_ratio": 0.08,
    "max_ratio": 0.25,
    "dialogue_must_change": true
  },
  "surface": {
    "forbidden_terms": ["本章", "读者"],
    "forbidden_punctuation": ["—", "……"],
    "required_patterns": []
  },
  "review_questions": ["对白是否改变信息差？", "神秘规则是否通过证据呈现？"]
}
```

不要把“冷峻”“高级”“有电影感”当作机械规则；这些应该留在 `voice_keywords` 和 `review_questions`，由 Agent/作者审查。Profile 是约束与共同上下文，不是自动文学评分器。
