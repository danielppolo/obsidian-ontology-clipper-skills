"""Simple HTML to Markdown fallback utilities."""

from __future__ import annotations

from html.parser import HTMLParser
import re


class SimpleMarkdownParser(HTMLParser):
    block_tags = {"p", "div", "section", "article", "br", "li", "ul", "ol", "h1", "h2", "h3"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.href_stack: list[str | None] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag in {"h1", "h2", "h3"}:
            self.parts.append("\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag == "a":
            self.href_stack.append(attrs_dict.get("href"))
            self.parts.append("[")
        elif tag == "img" and attrs_dict.get("src"):
            alt = attrs_dict.get("alt", "")
            self.parts.append(f"![{alt}]({attrs_dict['src']})")
        elif tag == "br":
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.href_stack:
            href = self.href_stack.pop()
            self.parts.append(f"]({href})" if href else "]")
        elif tag in self.block_tags:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        text = re.sub(r"\s+", " ", data)
        if text.strip():
            self.parts.append(text)


def html_to_markdown(html: str) -> str:
    parser = SimpleMarkdownParser()
    parser.feed(html)
    text = "".join(parser.parts)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + ("\n" if text.strip() else "")


def readable_text(html: str) -> str:
    text = re.sub(r"<(script|style).*?</\1>", "", html, flags=re.I | re.S)
    return html_to_markdown(text)
