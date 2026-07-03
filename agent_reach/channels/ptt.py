# -*- coding: utf-8 -*-
"""PTT Taiwan channel."""

import re
import urllib.request
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .base import Channel

_PTT_BASE = "https://www.ptt.cc"
_TIMEOUT = 10
_UA = "agent-reach/1.0"
_PUSH_TYPES = {
    "推": "push",
    "噓": "boo",
    "→": "neutral",
}


def _clean_text(text: str) -> str:
    return re.sub(r"[ \t\r\f\v]+", " ", text).strip()


def _absolute_url(path: str) -> str:
    if path.startswith(("http://", "https://")):
        return path
    return f"{_PTT_BASE}{path}"


def _fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": _UA,
            "Cookie": "over18=1",
        },
    )
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_board_index(html: str, board: str) -> list[dict]:
    """Parse a PTT board index page into normalized post summaries."""
    soup = BeautifulSoup(html, "html.parser")
    posts = []

    for row in soup.select(".r-ent"):
        title_el = row.select_one(".title a")
        if not title_el:
            continue

        href = title_el.get("href", "").strip()
        title = _clean_text(title_el.get_text(" ", strip=True))
        if not href or not title:
            continue

        author_el = row.select_one(".meta .author")
        date_el = row.select_one(".meta .date")
        push_el = row.select_one(".nrec")

        posts.append(
            {
                "platform": "ptt",
                "board": board,
                "title": title,
                "author": _clean_text(author_el.get_text(" ", strip=True)) if author_el else "",
                "date": _clean_text(date_el.get_text(" ", strip=True)) if date_el else "",
                "push_count": _clean_text(push_el.get_text(" ", strip=True)) if push_el else "",
                "url": _absolute_url(href),
            }
        )

    return posts


def _parse_metadata(main) -> dict[str, str]:
    metadata = {}
    for line in main.select(".article-metaline"):
        tag_el = line.select_one(".article-meta-tag")
        value_el = line.select_one(".article-meta-value")
        if not tag_el or not value_el:
            continue
        metadata[_clean_text(tag_el.get_text(" ", strip=True))] = value_el.get_text(" ", strip=True)
    return metadata


def _parse_pushes(main) -> list[dict]:
    comments = []
    for push in main.select(".push"):
        tag_el = push.select_one(".push-tag")
        user_el = push.select_one(".push-userid")
        content_el = push.select_one(".push-content")
        ipdatetime_el = push.select_one(".push-ipdatetime")

        tag = _clean_text(tag_el.get_text(" ", strip=True)) if tag_el else ""
        text = content_el.get_text(" ", strip=True) if content_el else ""
        text = re.sub(r"^:\s*", "", text).strip()

        comments.append(
            {
                "type": _PUSH_TYPES.get(tag, "neutral"),
                "user": _clean_text(user_el.get_text(" ", strip=True)) if user_el else "",
                "text": text,
                "ipdatetime": (
                    _clean_text(ipdatetime_el.get_text(" ", strip=True)) if ipdatetime_el else ""
                ),
            }
        )
    return comments


def _parse_content(main) -> str:
    content_soup = BeautifulSoup(str(main), "html.parser")
    content_main = content_soup.select_one("#main-content") or content_soup

    for selector in (".article-metaline", ".article-metaline-right", ".push"):
        for el in content_main.select(selector):
            el.decompose()

    for el in content_main.select(".f2"):
        if "發信站" in el.get_text():
            el.decompose()

    lines = [
        line.strip()
        for line in content_main.get_text("\n").splitlines()
        if line.strip()
    ]
    return "\n".join(lines)


def parse_post(html: str, board: str, url: str) -> dict:
    """Parse a PTT post page into the normalized Taiwan channel shape."""
    soup = BeautifulSoup(html, "html.parser")
    main = soup.select_one("#main-content")
    if main is None:
        return {
            "platform": "ptt",
            "board": board,
            "title": "",
            "author": "",
            "published_at": "",
            "content": "",
            "comments": [],
            "url": url,
        }

    metadata = _parse_metadata(main)
    return {
        "platform": "ptt",
        "board": board,
        "title": metadata.get("標題", ""),
        "author": metadata.get("作者", ""),
        "published_at": metadata.get("時間", ""),
        "content": _parse_content(main),
        "comments": _parse_pushes(main),
        "url": url,
    }


class PTTChannel(Channel):
    name = "ptt"
    description = "PTT 批踢踢"
    backends = ["public HTTP", "over18 cookie", "Jina Reader fallback"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        return "ptt.cc" in urlparse(url).netloc.lower()

    def board_index_url(self, board: str) -> str:
        return f"{_PTT_BASE}/bbs/{board}/index.html"

    def check(self, config=None):
        try:
            html = _fetch_text(self.board_index_url("PC_Shopping"))
            parse_board_index(html, board="PC_Shopping")
        except Exception as e:
            self.active_backend = None
            return "warn", f"PTT public HTTP 连接失败，保留 Jina Reader fallback：{e}"

        self.active_backend = "public HTTP"
        return "ok", "public HTTP 可读取看板 index；over18 cookie 已启用"

    def read_board_index(self, board: str) -> list[dict]:
        return parse_board_index(_fetch_text(self.board_index_url(board)), board=board)

    def read_post(self, board: str, url: str) -> dict:
        return parse_post(_fetch_text(url), board=board, url=url)
