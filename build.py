import argparse
from collections import defaultdict
from html import escape
import json
from pathlib import Path
import re
from shutil import copy2, copytree
from urllib.parse import quote, unquote, urlsplit

from bs4 import BeautifulSoup
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name
from pygments.util import ClassNotFound
import yaml


SITE_NAME = "개발 노트"
SITE_DESCRIPTION = "C/C++, 그래픽스, Unreal Engine을 공부하며 쌓은 기술 노트"
EDITOR_URL = "https://app.pagescms.org/durumyisking/durumyisking.github.io/main/collection"
MARKDOWN = MarkdownIt("commonmark", {"html": True}).enable(["table", "strikethrough"])
SYNTAX = HtmlFormatter(nowrap=True)
SAFE_TAGS = set("""
    a aside audio b blockquote br caption code col colgroup dd del details div dl dt em
    figcaption figure h1 h2 h3 h4 h5 h6 hr i img kbd li mark ol p pre s samp small source
    span strong sub summary sup table tbody td tfoot th thead tr u ul video
""".split())
SAFE_ATTRIBUTES = {
    "a": {"href", "title"}, "aside": {"class"}, "audio": {"src", "controls", "preload"},
    "code": {"class"}, "div": {"class"}, "img": {"src", "alt", "loading", "decoding", "title"},
    "ol": {"start"}, "source": {"src", "type"}, "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan", "scope"}, "video": {"src", "controls", "preload"},
}


def content_html(markdown, valid_slugs):
    article = BeautifulSoup(MARKDOWN.render(markdown), "html.parser")
    for node in article.find_all(["script", "iframe", "object", "form", "style", "svg", "math"]):
        node.decompose()
    for node in list(article.find_all(True)):
        if node.name not in SAFE_TAGS:
            node.unwrap()
            continue
        node.attrs = {k: v for k, v in node.attrs.items() if k in SAFE_ATTRIBUTES.get(node.name, set())}
        for attr in ("href", "src"):
            if attr not in node.attrs:
                continue
            target = node[attr]
            parts = urlsplit(target)
            if parts.scheme not in {"", "https", "http", "mailto"} or target.startswith(("//", "\\")):
                del node[attr]
            elif attr == "href" and not parts.scheme and parts.path.endswith(".md"):
                slug = unquote(parts.path[:-3])
                if slug in valid_slugs:
                    node[attr] = quote(slug) + ".html" + ("#" + parts.fragment if parts.fragment else "")
                else:
                    node.unwrap()
    for img in article.find_all("img"):
        img["alt"] = img.get("alt", "")
        img["loading"] = "lazy"
        img["decoding"] = "async"
    headings = set()
    for heading in article.find_all(re.compile(r"^h[1-6]$")):
        heading.name = "h" + str(min(int(heading.name[1]) + 1, 6))
        slug = re.sub(r"[\W_]+", "-", heading.get_text().lower()).strip("-") or "section"
        key = slug
        suffix = 1
        while key in headings:
            suffix += 1
            key = slug + "-" + str(suffix)
        heading["id"] = key
        headings.add(key)
    for code in article.select("pre > code"):
        class_name = next(iter(code.get("class", [])), "")
        language = class_name.removeprefix("language-") if class_name.startswith("language-") else ""
        try:
            lexer = get_lexer_by_name(language) if language else TextLexer()
        except ClassNotFound:
            lexer = TextLexer()
        pre = code.parent
        pre["class"] = "code-block"
        rich = BeautifulSoup(highlight(code.get_text(), lexer, SYNTAX), "html.parser")
        code.clear()
        code.append(rich)
    return article.decode()


def flatten(items, parents=()):
    for item in items:
        if "children" in item:
            yield from flatten(item["children"], (*parents, item["title"]))
        else:
            yield item, parents


def read_entries(content):
    categories = {}
    siblings = defaultdict(list)
    bodies = {}

    def add_entry(path, fields, parent, item):
        title = fields.get("title")
        order = fields.get("order")
        if order is None:
            order = 1000
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"Missing title in {path}")
        if isinstance(order, bool) or not isinstance(order, int):
            raise ValueError(f"Expected an integer order in {path}")
        if parent is not None and (not isinstance(parent, str) or parent not in categories):
            raise ValueError(f"Unknown category {parent!r} in {path}")
        siblings[parent].append((order, title.casefold(), path.name, item | {"title": title}))

    for path in sorted((content / "categories").glob("*.json")):
        key = f"content/categories/{path.name}"
        categories[key] = (path, json.loads(path.read_text(encoding="utf-8")))
    for key, (path, fields) in categories.items():
        add_entry(path, fields, fields.get("parent") or None, {"category": key})

    for path in sorted((content / "articles").glob("*.md")):
        markdown = path.read_text(encoding="utf-8")
        frontmatter = re.match(r"\A---[^\S\n]*\n(.*?)^---[^\S\n]*(?:\n|\Z)", markdown, re.DOTALL | re.MULTILINE)
        if not frontmatter:
            raise ValueError(f"Missing article metadata in {path}")
        fields = yaml.safe_load(frontmatter[1])
        if not isinstance(fields, dict) or not fields.get("category"):
            raise ValueError(f"Missing article category in {path}")
        add_entry(path, fields, fields["category"], {"slug": path.stem})
        bodies[path.stem] = markdown[frontmatter.end():]

    visited = set()

    def nested(parent):
        items = []
        for _, _, _, item in sorted(siblings[parent]):
            if "category" in item:
                key = item["category"]
                visited.add(key)
                item["children"] = nested(key)
            items.append(item)
        return items

    catalog = nested(None)
    if visited != categories.keys():
        raise ValueError("Category cycle involving " + ", ".join(sorted(categories.keys() - visited)))
    return catalog, bodies


def nav_tree(items, prefix, selected="", current_path=(), edit_category=None):
    result = []
    if edit_category:
        link = EDITOR_URL + "/categories/edit/" + quote(edit_category, safe="")
        result.append(f'<li><small><a href="{link}">카테고리 편집</a></small></li>')
    for item in items:
        title = escape(item["title"])
        if "children" in item:
            open_state = " open" if current_path and item["title"] == current_path[0] else ""
            remaining = current_path[1:] if open_state else ()
            child_category = item["category"] if edit_category else None
            members = nav_tree(item["children"], prefix, selected, remaining, child_category)
            result.append(f"<li><details{open_state}><summary>{title}</summary>{members}</details></li>")
        else:
            slug = item["slug"]
            current = ' aria-current="page"' if slug == selected else ""
            link = prefix + "notes/" + quote(slug) + ".html"
            if edit_category:
                link = EDITOR_URL + "/articles/edit/" + quote(f"content/articles/{slug}.md", safe="")
            result.append(f'<li><a href="{link}"{current}>{title}</a></li>')
    return "<ul>" + "".join(result) + "</ul>"


def layout(title, prefix, body, description=SITE_DESCRIPTION, noindex=False):
    escaped = escape(title)
    robots = '  <meta name="robots" content="noindex">\n' if noindex else ""
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="{escape(description, quote=True)}">
{robots}  <title>{escaped}</title>
  <link rel="stylesheet" href="{prefix}assets/site.css">
</head>
<body>
  <a href="#main" class="skip">본문으로 이동</a>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="{prefix}index.html">{SITE_NAME}</a>
      <a class="header-link" href="{prefix}index.html#topics">전체 목차</a>
    </div>
  </header>
  {body}
</body>
</html>
"""


def homepage(catalog, editor=False):
    cards = []
    for i, item in enumerate(catalog):
        count = len(list(flatten(item["children"])))
        title = escape(item["title"])
        tree = nav_tree(item["children"], "", edit_category=item["category"] if editor else None)
        cards.append(
            f'<details class="topic" id="topic-{i}"><summary><span>{title}</span>'
            f'<small>{count}개 글</small></summary>{tree}</details>'
        )
    heading = "블로그 편집 목차" if editor else SITE_NAME
    intro = (
        f'<a href="{EDITOR_URL}/articles/new">새 글 작성</a>'
        if editor else SITE_DESCRIPTION + "입니다."
    )
    body = f"""
    <main id="main" class="home">
      <section class="intro">
        <h1>{heading}</h1>
        <p>{intro}</p>
      </section>
      <section id="topics" class="topics" aria-label="주제별 글 목차">
      """ + "".join(cards) + "</section></main>"
    return layout(heading, "../" if editor else "", body, noindex=editor)


def article_page(item, parents, content, catalog, position, ordered):
    title, slug = escape(item["title"]), item["slug"]
    tree = nav_tree(catalog, "../", slug, parents)
    path = "".join(f"<li>{escape(parent)}</li>" for parent in parents)
    siblings = []
    for index, label in ((position - 1, "이전 글"), (position + 1, "다음 글")):
        if 0 <= index < len(ordered) and ordered[index][1][:1] == parents[:1]:
            other = ordered[index][0]
            siblings.append(
                '<a href="' + quote(other["slug"]) + '.html"><small>' + label + "</small>"
                + escape(other["title"]) + "</a>"
            )
    adjacent = ('<nav class="adjacent" aria-label="인접 글">' + "".join(siblings) + "</nav>") if siblings else ""
    body = f"""
    <div class="reader">
      <aside class="contents">
        <details class="contents-body" open>
          <summary>전체 목차</summary>
          <nav aria-label="주제별 글 목차">{tree}</nav>
        </details>
      </aside>
      <main id="main" class="reading">
        <nav aria-label="현재 위치">
          <ol class="breadcrumbs"><li><a href="../index.html#topics">전체 목차</a></li>{path}</ol>
        </nav>
        <article class="article">
          <h1>{title}</h1>
          <div class="article-body">{content}</div>
        </article>
        {adjacent}
      </main>
    </div>
    """
    return layout(item["title"] + " | " + SITE_NAME, "../", body, " / ".join((*parents, item["title"])))


def build(content, assets, output):
    catalog, bodies = read_entries(content)
    ordered = list(flatten(catalog))
    valid = {item["slug"] for item, _ in ordered}
    notes = output / "notes"
    notes.mkdir(parents=True, exist_ok=True)
    styles = output / "assets"
    styles.mkdir(exist_ok=True)
    copy2(assets / "site.css", styles / "site.css")
    with (styles / "site.css").open("a", encoding="utf-8") as css:
        css.write("\n" + SYNTAX.get_style_defs(".code-block") + "\n")
    if (content / "media").exists():
        copytree(content / "media", output / "media", dirs_exist_ok=True)
    for note in notes.glob("*.html"):
        if note.stem not in valid:
            note.unlink()
    (output / ".nojekyll").touch()
    (output / "index.html").write_text(homepage(catalog), encoding="utf-8")
    editor = output / "edit"
    editor.mkdir(exist_ok=True)
    (editor / "index.html").write_text(homepage(catalog, editor=True), encoding="utf-8")
    for position, (item, parents) in enumerate(ordered):
        html = content_html(bodies[item["slug"]], valid)
        page = article_page(item, parents, html, catalog, position, ordered)
        (notes / (item["slug"] + ".html")).write_text(page, encoding="utf-8")
    return len(ordered)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for path in ("content", "assets", "output"):
        parser.add_argument(path, type=Path)
    args = parser.parse_args()
    print(f"Built {build(**vars(args))} articles")
