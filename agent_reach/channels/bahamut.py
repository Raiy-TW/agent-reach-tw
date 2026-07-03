# -*- coding: utf-8 -*-
"""Bahamut Taiwan channel."""

import re
import urllib.request
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup

from .base import Channel

_BAHAMUT_BASE = "https://forum.gamer.com.tw/"
_TIMEOUT = 10
_UA = "agent-reach/1.0"


def _clean_text(text: str) -> str:
    return re.sub(r"[ \t\r\f\v]+", " ", text).strip()


def _fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _query_value(url: str, key: str) -> str:
    values = parse_qs(urlparse(url).query).get(key, [])
    return values[0] if values else ""


def _absolute_url(href: str) -> str:
    return urljoin(_BAHAMUT_BASE, href)


def _parse_int(value: str) -> int:
    digits = re.sub(r"\D+", "", value or "")
    return int(digits) if digits else 0


def parse_topic_list(html: str, board_url: str) -> list[dict]:
    """Parse a Bahamut board topic list page."""
    soup = BeautifulSoup(html, "html.parser")
    board = _query_value(board_url, "bsn")
    topics = []

    for row in soup.select("tr.b-list__row.b-list-item"):
        title_el = row.select_one(".b-list__main__title")
        if title_el is None:
            continue

        href = title_el.get("href") or ""
        if not href:
            wrapper_link = title_el.find_parent("a", href=True)
            href = wrapper_link.get("href", "") if wrapper_link else ""
        if not href:
            continue

        url = _absolute_url(href)
        subboard_el = row.select_one(".b-list__summary__sort a")
        gp_el = row.select_one(".b-list__summary__gp")
        brief_el = row.select_one(".b-list__brief")
        author_el = row.select_one(".b-list__count__user a")
        count_spans = row.select(".b-list__count__number span")
        last_reply_el = row.select_one(".b-list__time__edittime a")

        interaction_count = _clean_text(count_spans[0].get_text(" ", strip=True)) if count_spans else ""
        view_count = _clean_text(count_spans[1].get_text(" ", strip=True)) if len(count_spans) > 1 else ""

        topics.append(
            {
                "platform": "bahamut",
                "board": board or _query_value(url, "bsn"),
                "subboard": (
                    _clean_text(subboard_el.get_text(" ", strip=True)) if subboard_el else ""
                ),
                "title": _clean_text(title_el.get_text(" ", strip=True)),
                "excerpt": _clean_text(brief_el.get_text(" ", strip=True)) if brief_el else "",
                "author": _clean_text(author_el.get_text(" ", strip=True)) if author_el else "",
                "reply_count": _parse_int(_query_value(url, "tnum")),
                "gp_count": _parse_int(gp_el.get_text(" ", strip=True)) if gp_el else 0,
                "interaction_count": interaction_count,
                "view_count": view_count,
                "last_reply_at": (
                    _clean_text(last_reply_el.get_text(" ", strip=True)) if last_reply_el else ""
                ),
                "url": url,
            }
        )

    return topics


def _content_text(content_el) -> str:
    content_soup = BeautifulSoup(str(content_el), "html.parser")
    for el in content_soup.select("script, style, img"):
        el.decompose()
    lines = [
        line.strip()
        for line in content_soup.get_text("\n").splitlines()
        if line.strip()
    ]
    return "\n".join(lines)


def _reply_time(reply) -> str:
    for time_el in reply.select(".reply-content__footer .edittime"):
        value = time_el.get("data-tippy-content", "")
        if value.startswith("留言時間 "):
            return value.removeprefix("留言時間 ").strip()
    return ""


def parse_post(html: str, url: str) -> dict:
    """Parse a Bahamut post page into normalized post + replies."""
    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.select_one(".c-post__header__title")
    author_el = soup.select_one(".c-post__header__author .username")
    author_id_el = soup.select_one(".c-post__header__author .userid")
    time_el = soup.select_one(".c-post__header__info .edittime")
    category_el = soup.select_one(".tag-category .tag-category_item")
    content_el = soup.select_one(".c-article__content")

    replies = []
    for reply in soup.select(".c-reply__item"):
        floor_el = reply.select_one('[name="comment_floor"]')
        user_el = reply.select_one(".reply-content__user")
        text_el = reply.select_one(".comment_content")
        replies.append(
            {
                "floor": _clean_text(floor_el.get_text(" ", strip=True)) if floor_el else "",
                "author": _clean_text(user_el.get_text(" ", strip=True)) if user_el else "",
                "text": _clean_text(text_el.get_text(" ", strip=True)) if text_el else "",
                "published_at": _reply_time(reply),
            }
        )

    return {
        "platform": "bahamut",
        "board": _query_value(url, "bsn"),
        "title": _clean_text(title_el.get_text(" ", strip=True)) if title_el else "",
        "author": _clean_text(author_el.get_text(" ", strip=True)) if author_el else "",
        "author_id": _clean_text(author_id_el.get_text(" ", strip=True)) if author_id_el else "",
        "published_at": time_el.get("data-mtime", "") if time_el else "",
        "category": _clean_text(category_el.get_text(" ", strip=True)) if category_el else "",
        "content": _content_text(content_el) if content_el else "",
        "replies": replies,
        "url": url,
    }


class BahamutChannel(Channel):
    name = "bahamut"
    description = "巴哈姆特"
    backends = ["public HTTP", "Jina Reader fallback", "web search fallback"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        host = urlparse(url).netloc.lower()
        return host.endswith("gamer.com.tw")

    def board_url(self, board: str) -> str:
        return f"{_BAHAMUT_BASE}B.php?bsn={board}"

    def check(self, config=None):
        try:
            url = self.board_url("60030")
            html = _fetch_text(url)
            parse_topic_list(html, board_url=url)
        except Exception as e:
            self.active_backend = None
            return "warn", f"Bahamut public HTTP 連線失敗，保留 Jina Reader / web search fallback：{e}"

        self.active_backend = "public HTTP"
        return "ok", "public HTTP 可讀取巴哈姆特看板列表與文章頁"

    def read_topic_list(self, board: str) -> list[dict]:
        url = self.board_url(board)
        return parse_topic_list(_fetch_text(url), board_url=url)

    def read_post(self, url: str) -> dict:
        return parse_post(_fetch_text(url), url=url)
