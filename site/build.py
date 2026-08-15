#!/usr/bin/env python3
"""
CanonLoom site builder.

Zero-dependency (Python standard library only) static site generator for the
CanonLoom landing page and documentation site.

Layout
------
site/src/               source for the site itself
  assets/               site.css, site.js
  landing.html          hand-authored product landing page
  templates/            Jinja-less HTML templates used by this builder
site/dist/              build output (what GitHub Pages serves) -- gitignored
site/build.py           this builder

Inputs
------
repo docs/              all Markdown files become rendered pages; non-Markdown
                        files (e.g. SVG figures) are copied through as-is so
                        relative image links keep working.
repo VERSION            current CanonLoom version (shown in nav/footer)

Usage
-----
python3 site/build.py [--clean]     build into site/dist/
python3 site/build.py --serve [port]  build then serve locally (stdlib http.server)
"""

from __future__ import annotations

import argparse
import html
import http.server
import os
import posixpath
import re
import shutil
import socketserver
import sys
from pathlib import Path

escape = html.escape

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = Path(__file__).resolve().parent / "src"
DIST = Path(__file__).resolve().parent / "dist"
DOCS = REPO_ROOT / "docs"

SITE_NAME = "CanonLoom"
SITE_TAGLINE = "命令驱动、作者掌舵、可审计的长篇小说生产框架"
REPO_URL = "https://github.com/Liyuk/canonloom"
VERSION = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()

# ---------------------------------------------------------------------------
# Markdown renderer (small, deliberate subset)
# ---------------------------------------------------------------------------


def _inline_callback(match: re.Match) -> str:
    """Handle one inline token in source order (code/math spans are protected)."""
    if match.group(1) is not None:  # $...$ inline math
        return f'<span class="math">${escape(match.group(2))}$</span>'
    img_alt, img_src = match.group(3), match.group(4)
    if img_src is not None:
        return f'<img src="{img_src}" alt="{img_alt}" loading="lazy">'
    link_text, link_url = match.group(5), match.group(6)
    if link_text is not None:
        href = rewrite_link(link_url)
        return f'<a href="{href}">{_inline(link_text)}</a>'
    code = match.group(8)
    if code is not None:
        return f"<code>{escape(code)}</code>"
    if match.group(9) is not None:  # **bold**
        return f"<strong>{_inline(match.group(10))}</strong>"
    if match.group(11) is not None:  # __bold__
        return f"<strong>{_inline(match.group(12))}</strong>"
    if match.group(13) is not None:  # *em*
        return f"<em>{_inline(match.group(14))}</em>"
    if match.group(15) is not None:  # _em_
        return f"<em>{_inline(match.group(16))}</em>"
    url = match.group(17)
    if url is not None:  # bare http(s) URL
        return f'<a href="{url}">{escape(url)}</a>'
    return escape(match.group(0))


# Combined alternation. Group layout:
#  1,2 $inline math$  3 img alt  4 img src  5 link text  6 link url
#  7,8 code fence char + body  9,10 **bold**  11,12 __bold__  13,14 *em*
#  15,16 _em_  17 bare URL
_INLINE_TOKENS = re.compile(
    r"(\$)([^$\n]+?)\1"
    r"|!\[([^\]]*)\]\(([^)]*)\)"
    r"|\[([^\]]+)\]\(([^)\s]+)(?:\s+[^)]*)?\)"
    r"|(`+)([^`]+?)\7"
    r"|(\*\*)(.+?)\9"
    r"|(__)(.+?)\11"
    r"|(\*)(?![ *])([^*\n]+?)(?<!\*)\13"
    r"|(_)(?![ _])([^_\n]+?)(?<!_)\15"
    r"|((?:https?|ftp)://[\w:/.?=&%+~@\-\[\]]+)"
)

LINK_TARGETS = {}  # source md path -> built html url (filled by the builder)
_CURRENT_SRC: Path | None = None  # source file being rendered (for relative links)
_ANCHOR_RE = re.compile(r"^(.*?\.md)(?:#(.+))?$")


def rewrite_link(href: str) -> str:
    """Rewrite internal .md links to built .html URLs; leave the rest alone."""
    if not href or href.startswith(("http://", "https://", "mailto:", "#")):
        return html.escape(href)
    if "#" in href and not href.startswith("#"):
        path, anchor = href.split("#", 1)
    else:
        path, anchor = href, None
    if path.endswith(".md"):
        target = LINK_TARGETS.get(path)
        if not target and _CURRENT_SRC is not None:
            target = resolve_source_link(_CURRENT_SRC, path)
        if target:
            url = target
            if anchor:
                url += "#" + anchor
            return html.escape(url)
    return html.escape(href)


def _inline(text: str) -> str:
    """Render inline markdown on raw text; the callback escapes each part once."""
    return _INLINE_TOKENS.sub(_inline_callback, text)


def _slugify(text: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z一-鿿\- ]", "", text).strip().lower()
    slug = slug.replace(" ", "-")
    return slug or "section"


def _render_heading(line: str) -> str:
    m = re.match(r"^(#{1,6})\s+(.*)$", line)
    level = len(m.group(1))
    text = _inline(m.group(2).strip())
    slug = _slugify(re.sub(r"<[^>]+>", "", m.group(2)))
    return f'<h{level} id="{slug}">{text}</h{level}>'


def _render_code_block(lang: str, body: str) -> str:
    cls = f' class="language-{escape(lang)}"' if lang else ""
    return f"<pre><code{cls}>{escape(body)}</code></pre>"


def _render_table(rows: list[list[str]]) -> str:
    out = ["<div class='table-wrap'><table>"]
    for i, row in enumerate(rows):
        tag = "th" if i == 0 else "td"
        out.append("<tr>" + "".join(f"<{tag}>{_inline(c.strip())}</{tag}>" for c in row) + "</tr>")
    out.append("</table></div>")
    return "\n".join(out)


def _is_table_sep(line: str) -> bool:
    cells = [c for c in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c.strip()) for c in cells)


def render_markdown(md: str) -> str:
    """Render the supported Markdown subset to HTML."""
    out: list[str] = []
    i, n = 0, len(md.splitlines())
    lines = md.splitlines()

    while i < n:
        line = lines[i]

        if re.match(r"^```", line):
            lang = line.strip()[3:]
            buf = []
            i += 1
            while i < n and not re.match(r"^```", lines[i]):
                buf.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            out.append(_render_code_block(lang, "\n".join(buf)))
            continue

        if line.startswith(r"\["):
            buf = []
            i += 1  # skip the opening \[
            while i < n and not re.match(r"^\\\]", lines[i].strip()):
                buf.append(lines[i])
                i += 1
            i += 1  # skip closing \]
            out.append('<div class="math-block">' + escape("\n".join(buf).strip()) + "</div>")
            continue

        if re.match(r"^#{1,6}\s+", line):
            out.append(_render_heading(line))
            i += 1
            continue

        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", line.strip()):
            out.append("<hr>")
            i += 1
            continue

        if line.startswith(">"):
            buf = []
            while i < n and (lines[i].startswith(">") or lines[i].strip() == ""):
                if lines[i].startswith(">"):
                    buf.append(re.sub(r"^>\s?", "", lines[i]))
                else:
                    buf.append("")
                i += 1
            paras = [p for p in _inline("\n".join(buf).strip()).split("\n") if p.strip()]
            out.append("<blockquote>" + "\n".join(f"<p>{p}</p>" for p in paras) + "</blockquote>")
            continue

        # pipe table
        if line.lstrip().startswith("|") and i + 1 < n and _is_table_sep(lines[i + 1]):
            rows = []
            header = [c for c in line.strip().strip("|").split("|")]
            rows.append(header)
            i += 2
            while i < n and lines[i].lstrip().startswith("|"):
                rows.append([c for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append(_render_table(rows))
            continue

        # list block
        if re.match(r"^(\s*)([-*+]|\d+\.)\s+", line):
            indent_stack = []
            buf = []
            while i < n:
                m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", lines[i])
                if not m and lines[i].strip():
                    break
                if not m:
                    i += 1
                    continue
                indent = len(m.group(1).replace("\t", "    "))
                while indent_stack and indent <= indent_stack[-1]:
                    buf.append("</ul>")
                    indent_stack.pop()
                if not indent_stack:
                    buf.append("<ul>")
                    indent_stack.append(indent)
                # loose/compact: a trailing blank splits paragraphs; keep simple
                buf.append(f"<li>{_inline(m.group(3))}")
                i += 1
                # capture a single following paragraph continuation
                while i < n and lines[i].strip() and not re.match(r"^(\s*)([-*+]|\d+\.)\s+", lines[i]) and not re.match(r"^#{1,6}\s", lines[i]):
                    buf.append("<br>" + _inline(lines[i]))
                    i += 1
                buf.append("</li>")
            while indent_stack:
                buf.append("</ul>")
                indent_stack.pop()
            out.append("".join(buf))
            continue

        # paragraph
        buf = []
        while (
            i < n
            and lines[i].strip()
            and not re.match(r"^```|^#{1,6}\s|^-{3,}$|^\*{3,}$|^>{1}",
                             lines[i])
            and not re.match(r"^(\s*)([-*+]|\d+\.)\s+", lines[i])
            and not lines[i].lstrip().startswith("|")
        ):
            buf.append(lines[i])
            i += 1
        if buf:
            out.append(f"<p>{_inline(' '.join(x.strip() for x in buf if x.strip()))}</p>")
            continue

        i += 1

    return "\n".join(out)


# ---------------------------------------------------------------------------
# Site model
# ---------------------------------------------------------------------------

NAV = [
    ("/", "首页"),
    ("/docs/", "文档"),
    ("/docs/blog/", "博客"),
    (REPO_URL, "GitHub"),
]

# Core documentation, ordered for the docs landing page "Guides" section.
GUIDES = [
    ("docs/en/user-guide.md", "快速上手", "最小作者路径：init → setup → idea → work", "EN"),
    ("docs/user-guide.md", "作者使用指南", "日常命令、工作模式与审批流程", "中文"),
    ("docs/en/terminal-and-apps.md", "Terminal 与 App", "CLI、Codex / Claude Code / App 三种运行方式", "EN"),
    ("docs/en/initialization.md", "初始化协议", "canonloom init 生成的目录与配置", "EN"),
    ("docs/strong-constraints.md", "强约束 S0–S6", "阶段门禁、严重级、结算与重试规则", "English"),
    ("docs/en/style-profile.md", "文风协议", "Style Profile 的内容与写法", "EN"),
    ("docs/language-policy.md", "语言策略", "协议键名 vs 人类语言的边界", "中文"),
    ("docs/en/narrative-state.md", "叙事状态层", "事件 / 知识 / 揭示三样状态文件", "EN"),
]

REFERENCE = [
    ("docs/architecture.md", "系统架构", "从意图到可审计结算的组件图", "English"),
    ("docs/workflow.md", "工作流总览", "规划 → 分歧 → 选择 → 草稿 → 结算", "English"),
    ("docs/planning-hierarchy.md", "规划层级", "project → volume → arc → contract → beat", "English"),
    ("docs/runtime-adapters.md", "运行时适配", "模型、CLI 与文件协议解耦", "English"),
    ("docs/benchmark.md", "Benchmark 与竞品", "三类数字的区分与受控实验协议", "中 / EN"),
    ("docs/landscape.md", "项目生态", "同类工具的定位对比", "中文"),
    ("docs/paper-0.2.0/paper.md", "0.2.0 系统论文", "完整设计、评估协议与参考文献", "中文"),
    ("docs/iteration-roadmap.md", "迭代路线", "当前边界与下一步", "中文"),
]


def collect_docs() -> list[Path]:
    docs = []
    for path in sorted(DOCS.rglob("*.md")):
        if "figures" in path.parts:
            continue
        docs.append(path)
    return docs


def page_url(src: Path) -> str:
    """Map a docs source file to its built URL (mirrors the tree).

    A README.md renders as index.html within its own directory so a section
    has a landing page. The exception is the docs/ root README, which stays
    README.html because /docs/index.html is reserved for the curated landing.
    """
    rel = src.relative_to(DOCS)
    if rel.name == "README.md":
        if len(rel.parts) == 1:  # docs/README.md
            name = "README.html"
        else:
            name = "index.html"
    else:
        name = rel.with_suffix(".html").name
    parts = list(rel.parts[:-1]) + [name]
    return "/docs/" + "/".join(parts)


def build_link_targets(docs: list[Path]) -> None:
    for src in docs:
        rel = src.relative_to(DOCS)
        LINK_TARGETS[rel.as_posix()] = page_url(src)
    # root README links that reference ../../README.md from docs/ pages
    LINK_TARGETS["../../README.md"] = "/"


def resolve_source_link(src: Path, href: str) -> str:
    """Resolve a .md href that is relative to src's directory, including .. paths."""
    base = src.parent
    for suffix in ("", ".md"):
        cand = (base / (href + suffix)).resolve()
        if cand.is_file():
            rel = cand.relative_to(DOCS.resolve())
            return LINK_TARGETS.get(rel.as_posix(), href)
    return href


def page_title(md: str) -> str:
    for line in md.splitlines():
        if line.startswith("# "):
            return _inline(line[2:].strip())
    return "CanonLoom"


def page_toc(md: str) -> list[tuple[str, str, str]]:
    """Return [(level, slug, text)] for h2/h3 headings."""
    toc = []
    for line in md.splitlines():
        m = re.match(r"^(#{2,3})\s+(.*)$", line)
        if not m:
            continue
        text = re.sub(r"[`*\[\]]", "", m.group(2))
        toc.append((m.group(1), _slugify(text), _inline(text)))
    return toc


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

LAYOUT = """<!doctype html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · CanonLoom</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title} · CanonLoom">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:url" content="{repo_url}{canonical}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="/">
      <span class="brand-mark" aria-hidden="true">⏳</span>
      <span class="brand-name">CanonLoom</span>
      <span class="brand-ver">v{version}</span>
    </a>
    <nav class="site-nav" aria-label="主导航">
      {nav_links}
    </nav>
    <button class="nav-toggle" aria-label="切换导航" aria-expanded="false">☰</button>
  </div>
</header>
<main>
{content}
</main>
<footer class="site-footer">
  <div class="container footer-inner">
    <div>
      <strong>CanonLoom</strong> v{version} — {tagline}
    </div>
    <div class="footer-links">
      <a href="{repo_url}">GitHub</a>
      <a href="/docs/">文档</a>
      <a href="/docs/blog/">博客</a>
      <a href="{repo_url}/blob/main/LICENSE">MIT License</a>
    </div>
  </div>
</footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""


def _nav_link(url: str, text: str, canonical: str) -> str:
    current = url.startswith("/") and canonical.startswith(url.rstrip("/"))
    cls = ' class="current"' if current else ""
    return f'<a href="{url}"{cls}>{text}</a>'


def render_layout(title: str, description: str, content: str, canonical: str) -> str:
    nav_links = "\n      ".join(
        _nav_link(u, t, canonical)
        for u, t in NAV[:-1]
    )
    return LAYOUT.format(
        title=html.escape(title),
        description=html.escape(description),
        content=content,
        canonical=canonical,
        nav_links=nav_links,
        repo_url=REPO_URL,
        version=VERSION,
        tagline=SITE_TAGLINE,
    )


def render_docs_page(src: Path, md: str, body: str) -> str:
    title = page_title(md)
    toc = page_toc(md)
    url = page_url(src)
    rel = src.relative_to(DOCS)

    toc_html = ""
    if toc:
        items = "\n".join(
            f'<li class="toc-{level}"><a href="#{slug}">{text}</a></li>'
            for level, slug, text in toc
        )
        toc_html = f"<details class='page-toc'><summary>本页目录</summary><ul>{items}</ul></details>"

    # Breadcrumb: 首页 / docs / [section dirs] / page. Intermediate crumbs link
    # to the section's index.html when one exists, else render as plain text.
    # Breadcrumb: 首页 / docs / [section dirs] / page. A section crumb links
    # only when that directory has a landing page (a README.md source or the
    # curated blog index); otherwise it renders as plain text.
    crumbs: list[tuple[str, str]] = [("/docs/", "文档")]
    for d in rel.parts[:-1]:
        dir_url = "/docs/" + "/".join(rel.parts[: rel.parts.index(d) + 1]) + "/"
        crumbs.append((dir_url, d))
    leaf_label = rel.stem.replace("README", "index").replace("-", " ")
    crumbs.append((url, leaf_label))

    def _crumb_linkable(cu: str) -> bool:
        if cu == "/docs/":
            return True
        if cu == "/docs/blog/":
            return True
        # section index.html exists when the section dir has a README.md
        sec = cu.removeprefix("/docs/").strip("/")
        if sec and (DOCS / sec / "README.md").is_file():
            return True
        return False

    breadcrumb = '<nav class="breadcrumb" aria-label="面包屑"><a href="/">首页</a>'
    for cu, ct in crumbs:
        if _crumb_linkable(cu):
            breadcrumb += f'<span>/</span><a href="{cu}">{ct}</a>'
        else:
            breadcrumb += f'<span>/</span><span>{ct}</span>'
    breadcrumb += "</nav>"

    content = f"""
    <div class="container docs-layout">
      <div class="docs-main">
        {breadcrumb}
        <h1>{title}</h1>
        {toc_html}
        <article class="docs-content">
        {body}
        </article>
      </div>
    </div>
    """
    return render_layout(title, "CanonLoom 文档：" + title, content, url)


def render_docs_index() -> str:
    def cards(section: str, items: list[tuple]) -> str:
        card_html = ""
        for path, title, desc, lang in items:
            rel = path.split("/", 1)[1] if path.startswith("docs/") else path
            card_html += (
                f'<a class="doc-card" href="{page_url(DOCS / rel)}">'
                f'<span class="doc-card-top"><strong>{title}</strong>'
                f'<span class="lang-tag">{lang}</span></span>'
                f"<span class=\"doc-card-desc\">{desc}</span></a>"
            )
        return f"<section class='docs-section'><h2>{section}</h2><div class='doc-grid'>{card_html}</div></section>"

    content = """
    <div class="container docs-layout">
      <div class="docs-main">
        <nav class="breadcrumb" aria-label="面包屑"><a href="/">首页</a><span>/</span><span>文档</span></nav>
        <h1>文档</h1>
        <p class="lead">CanonLoom 的协议、命令与设计文档。机器协议保持英文键名，人类指南提供中英双语入口。</p>
    """ + cards("指南", GUIDES) + cards("参考与设计", REFERENCE) + """
        <section class="docs-section">
          <h2>协议文件</h2>
          <p>项目以可读文件承载状态：<code>canonloom.json</code>（工作流状态机）、
          <code>tasks/current.md</code>（当前任务）、<code>schemas/</code>（协议）、
          <code>scripts/</code>（确定性工具）。完整目录结构见
          <a href="/docs/en/initialization.html">初始化协议</a>。</p>
        </section>
      </div>
    </div>
    """
    return render_layout("文档", "CanonLoom 文档索引", content, "/docs/")


def render_blog_index() -> str:
    blog_dir = DOCS / "blog"
    items = []
    for path in sorted(blog_dir.glob("*.md"), reverse=True):
        md = path.read_text(encoding="utf-8")
        title = page_title(md)
        # short description = first blockquote ">" line if present, else lead sentence
        desc = ""
        for line in md.splitlines():
            if line.startswith(">"):
                desc = line.lstrip("> ").strip()
                break
        date = path.stem[:10]
        items.append((page_url(path), date, title, desc))

    cards = "\n".join(
        f'<a class="blog-card" href="{url}">'
        f'<time datetime="{date}">{date}</time>'
        f"<h2>{title}</h2>"
        f"<p>{desc}</p></a>"
        for url, date, title, desc in items
    )
    content = f"""
    <div class="container docs-layout">
      <div class="docs-main">
        <nav class="breadcrumb" aria-label="面包屑"><a href="/">首页</a><span>/</span><span>博客</span></nav>
        <h1>博客</h1>
        <p class="lead">发布公告、实操指南与设计思考。</p>
        <div class="blog-grid">{cards}</div>
      </div>
    </div>
    """
    return render_layout("博客", "CanonLoom 博客", content, "/docs/blog/")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def copy_assets() -> None:
    for path in (SRC / "assets").rglob("*"):
        if path.is_file():
            dst = DIST / "assets" / path.relative_to(SRC / "assets")
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dst)


def copy_docs_assets() -> None:
    """Copy non-Markdown files under docs/ (figures, etc.) preserving paths."""
    for path in DOCS.rglob("*"):
        if path.is_file() and path.suffix.lower() != ".md":
            dst = DIST / "docs" / path.relative_to(DOCS)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dst)


def build(clean: bool = False) -> None:
    if clean and DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)

    docs = collect_docs()
    build_link_targets(docs)

    # landing page
    landing = (SRC / "landing.html").read_text(encoding="utf-8")
    (DIST / "index.html").write_text(landing, encoding="utf-8")

    # docs pages
    for src in docs:
        global _CURRENT_SRC
        _CURRENT_SRC = src
        md = src.read_text(encoding="utf-8").lstrip("﻿")
        body = render_markdown(md)
        html_out = render_docs_page(src, md, body)
        url = page_url(src)  # e.g. /docs/strong-constraints.html or /docs/README.html
        dst = DIST / url.lstrip("/")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(html_out, encoding="utf-8")

    # curated docs landing page (reserves /docs/index.html)
    (DIST / "docs" / "index.html").write_text(render_docs_index(), encoding="utf-8")

    # blog index
    (DIST / "docs" / "blog" / "index.html").write_text(render_blog_index(), encoding="utf-8")

    copy_assets()
    copy_docs_assets()
    print(f"Built {len(docs)} doc pages + landing page into {DIST}")


def serve(port: int = 8000) -> None:
    build(clean=True)
    os.chdir(DIST)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self) -> None:
            self.send_header("Cache-Control", "no-cache")
            super().end_headers()

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        print(f"Serving {DIST} at http://127.0.0.1:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the CanonLoom site")
    parser.add_argument("--clean", action="store_true", help="wipe site/dist first")
    parser.add_argument("--serve", nargs="?", const=8000, type=int, metavar="PORT",
                        help="build then serve locally")
    args = parser.parse_args()
    if args.serve is not None:
        serve(args.serve)
    else:
        build(clean=args.clean)


if __name__ == "__main__":
    main()
