# CanonLoom 网站源码

CanonLoom 的落地页与文档站，零第三方依赖，Python 标准库生成。

## 结构

```text
site/
  build.py       静态站点生成器（Python 标准库，无依赖）
  src/
    landing.html   产品落地页（中文，含 S0–S6 流水线与交互式演示）
    landing.en.html产品落地页（英文，/en/）
    assets/       site.css / site.js / favicon.svg
  dist/          构建产物（GitHub Pages 部署内容，已 gitignore）
```

`docs/` 下的所有 Markdown 会被渲染成对应 HTML 页面（镜像目录结构）；
`docs/` 下的非 Markdown 文件（如论文 SVG 图）按原样复制，保持相对链接可用。

## 构建与预览

```sh
python3 site/build.py            # 构建到 site/dist/（默认带 /canonloom 前缀）
CANONLOOM_SITE_BASE="" python3 site/build.py   # 根路径构建（自定义域名场景）
python3 site/build.py --clean    # 先清空 dist 再构建
python3 site/build.py --serve    # 本地预览（根路径模式）
```

GitHub Pages 项目站部署在子路径 `/canonloom/`，构建器默认给所有内部链接加该前缀；
`--serve` 与 `CANONLOOM_SITE_BASE=""` 会去掉前缀，方便本地根路径预览。

## 双语

- `/`（中文落地页）与 `/en/`（英文落地页）通过右上角语言开关互相跳转；
- 每个文档页根据 `docs/`（中文）↔ `docs/en/`（英文）自动生成对照链接；
- 博客与论文当前仅中文，语言开关指向英文落地页。

## 部署

`.github/workflows/deploy.yml` 在 `main` 分支推送时自动构建并部署到
GitHub Pages：https://liyuk.github.io/canonloom/

## 支持的 Markdown 子集

渲染器按 docs/ 实际使用情况实现了一个精挑的子集：

- ATX 标题 `#`–`####`（生成锚点 id 与页内目录）
- 行内 `**bold**`、`*em*`、`` `code` ``、`[link](url)`、`![alt](src)`、裸 URL
- 行内数学 `$...$` 与展示数学 `\[...\]`（论文使用，原样保留）
- 围栏代码块（` ```text|sh|bash|json|jsonc|python`）
- 顶层列表（`-` / `*` / 数字）、块引用、分隔线、单行表

`.md` 内部链接会自动改写为构建后的 `.html` 地址；`docs/README.md`
渲染为 `docs/README.html`（`/docs/` 保留给手写的文档卡片落地页）。
