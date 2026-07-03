# -*- coding: utf-8 -*-
"""Dcard Taiwan channel."""

import re
import urllib.error
import urllib.request
from urllib.parse import urlparse

from .base import Channel

_TIMEOUT = 10
_UA = "agent-reach/1.0"


def _clean_text(text: str) -> str:
    return re.sub(r"[ \t\r\f\v]+", " ", text).strip()


def _dcard_url_parts(url: str) -> tuple[str, str]:
    match = re.search(r"/f/([^/]+)/p/(\d+)", url)
    if not match:
        forum = ""
        forum_match = re.search(r"/f/([^/?#]+)", url)
        return (forum_match.group(1) if forum_match else forum, "")
    return match.group(1), match.group(2)


def _fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_public_post_text(text: str, url: str) -> dict:
    """Normalize Jina-style Dcard public text into a stable shape."""
    forum, post_id = _dcard_url_parts(url)
    lines = [line.rstrip() for line in text.splitlines()]
    title = ""
    content_lines = []
    comments = []
    in_markdown = False
    in_comments = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if in_markdown and not in_comments and content_lines:
                content_lines.append("")
            continue

        if line.startswith("Title:"):
            title = _clean_text(line.removeprefix("Title:"))
            continue
        if line == "Markdown Content:":
            in_markdown = True
            continue
        if not in_markdown:
            continue

        if line.startswith("# "):
            title = title or _clean_text(line.removeprefix("# "))
            continue
        if line == "留言":
            in_comments = True
            continue
        if in_comments:
            match = re.match(r"[-*]\s*([^：:]+)[：:]\s*(.+)", line)
            if match:
                comments.append(
                    {
                        "author": _clean_text(match.group(1)),
                        "text": _clean_text(match.group(2)),
                    }
                )
            continue

        content_lines.append(line)

    while content_lines and content_lines[-1] == "":
        content_lines.pop()

    return {
        "platform": "dcard",
        "forum": forum,
        "post_id": post_id,
        "title": title,
        "content": "\n".join(content_lines),
        "comments": comments,
        "url": url,
    }


class DcardChannel(Channel):
    name = "dcard"
    description = "Dcard"
    backends = ["public web/API", "Jina Reader fallback", "browser fallback"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        return "dcard.tw" in urlparse(url).netloc.lower()

    def check(self, config=None):
        try:
            _fetch_text("https://www.dcard.tw/f/tech")
        except urllib.error.HTTPError as e:
            if e.code == 403:
                self.active_backend = None
                return (
                    "warn",
                    "Dcard public HTTP/API 目前不可直接讀取（403）；使用 Jina Reader 或 browser fallback",
                )
            self.active_backend = None
            return "warn", f"Dcard public HTTP/API 檢查失敗：HTTP {e.code}"
        except Exception as e:
            self.active_backend = None
            return "warn", f"Dcard public HTTP/API 檢查失敗：{e}"

        self.active_backend = "public web page"
        return "warn", "Dcard public page reachable；API/parser 仍以 fallback 模式保守啟用"

    def parse_public_text(self, text: str, url: str) -> dict:
        return parse_public_post_text(text, url=url)
