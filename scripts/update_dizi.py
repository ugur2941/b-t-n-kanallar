from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from datetime import datetime, timezone
import re


BASE_URL = "https://tvdiziler.tv/"
TARGET_SECTIONS = {"last-episodes"}


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value or "")).strip()


class TvDizilerParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.div_depth = 0
        self.section_stack: list[tuple[str, int]] = []
        self.current_anchor: dict[str, str] | None = None
        self.capture_field: str | None = None
        self.items: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        classes = set(attrs.get("class", "").split())

        if tag == "div":
            self.div_depth += 1
            matched_section = next((name for name in TARGET_SECTIONS if name in classes), None)
            if matched_section:
                self.section_stack.append((matched_section, self.div_depth))

        if not self.in_target_section:
            return

        if tag == "a" and "data-navigo" in attrs and attrs.get("href"):
            self.current_anchor = {
                "href": attrs["href"],
                "title": "",
                "subtitle": "",
                "image": "",
            }
            self.capture_field = None
            return

        if not self.current_anchor:
            return

        if tag == "img" and not self.current_anchor["image"]:
            image = attrs.get("data-src") or attrs.get("src") or ""
            self.current_anchor["image"] = image
            return

        if tag == "h2":
            self.capture_field = "title"
            return

        if tag == "p":
            self.capture_field = "subtitle"

    def handle_endtag(self, tag: str) -> None:
        if tag in {"h2", "p"}:
            self.capture_field = None

        if tag == "a" and self.current_anchor:
            href = clean_text(self.current_anchor["href"])
            title = clean_text(self.current_anchor["title"])
            subtitle = clean_text(self.current_anchor["subtitle"])
            image = clean_text(self.current_anchor["image"])
            if href and (title or subtitle):
                self.items.append(
                    {
                        "url": urljoin(BASE_URL, href),
                        "title": title,
                        "subtitle": subtitle,
                        "image": urljoin(BASE_URL, image) if image else "",
                    }
                )
            self.current_anchor = None
            self.capture_field = None

        if tag == "div":
            while self.section_stack and self.section_stack[-1][1] == self.div_depth:
                self.section_stack.pop()
            self.div_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.current_anchor and self.capture_field:
            self.current_anchor[self.capture_field] += data

    @property
    def in_target_section(self) -> bool:
        return bool(self.section_stack)
