# -*- coding: utf-8 -*-
"""Taiwan news RSS channel."""

import urllib.request
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .base import Channel

DEFAULT_NEWS_SOURCES = [
    {"name": "technews", "url": "https://technews.tw/feed/"},
    {"name": "inside", "url": "https://www.inside.com.tw/feed/rss"},
    {"name": "pts", "url": "https://news.pts.org.tw/xml/newsfeed.xml"},
]

_NEWS_HOSTS = {
    "cna.com.tw",
    "news.pts.org.tw",
    "bnext.com.tw",
    "technews.tw",
    "inside.com.tw",
}
_TIMEOUT = 10
_UA = "agent-reach/1.0"


def _strip_html(value: str) -> str:
    return BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)


def _fetch_feed(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


def normalize_feed_entries(feed_text: str, source_name: str, limit: int | None = None) -> list[dict]:
    """Normalize RSS/Atom feed entries into a stable Taiwan news shape."""
    import feedparser

    parsed = feedparser.parse(feed_text)
    entries = parsed.entries[:limit] if limit is not None else parsed.entries
    items = []

    for entry in entries:
        published_at = entry["published"] if "published" in entry else entry.get("updated", "")
        items.append(
            {
                "platform": "taiwan_news",
                "source": source_name,
                "title": entry.get("title", ""),
                "published_at": published_at,
                "url": entry.get("link", ""),
                "excerpt": _strip_html(entry.get("summary", entry.get("description", ""))),
            }
        )

    return items


class TaiwanNewsChannel(Channel):
    name = "taiwan_news"
    description = "台湾新闻 RSS"
    backends = ["feedparser", "web search fallback"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        host = urlparse(url).netloc.lower()
        return any(host == domain or host.endswith(f".{domain}") for domain in _NEWS_HOSTS)

    def _configured_sources(self, config=None) -> list[dict]:
        if config:
            configured = config.get("news_sources")
            if isinstance(configured, list):
                return [
                    {"name": str(item["name"]), "url": str(item["url"])}
                    for item in configured
                    if isinstance(item, dict) and item.get("name") and item.get("url")
                ]
        return list(DEFAULT_NEWS_SOURCES)

    def read_sources(self, sources: list[dict] | None = None, limit_per_source: int = 20) -> dict:
        """Read configured RSS sources. One broken source does not fail the batch."""
        items = []
        errors = []

        for source in sources or DEFAULT_NEWS_SOURCES:
            name = str(source["name"])
            try:
                feed_text = _fetch_feed(str(source["url"]))
                items.extend(normalize_feed_entries(feed_text, name, limit=limit_per_source))
            except Exception as e:
                errors.append({"source": name, "error": str(e)})

        return {"items": items, "errors": errors}

    def check(self, config=None):
        try:
            import feedparser  # noqa: F401
        except ImportError:
            self.active_backend = None
            return "off", "feedparser 未安装；台湾新闻 RSS 渠道无法读取 feeds"

        sources = self._configured_sources(config)
        result = self.read_sources(sources, limit_per_source=1)
        reachable = len(sources) - len(result["errors"])

        if reachable == 0:
            self.active_backend = None
            return "warn", f"0/{len(sources)} feeds reachable；保留 web search fallback"

        self.active_backend = "feedparser"
        status = "ok" if reachable == len(sources) else "warn"
        return status, f"{reachable}/{len(sources)} feeds reachable via feedparser"
