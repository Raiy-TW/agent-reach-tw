# -*- coding: utf-8 -*-
"""Tests for the Taiwan news RSS channel."""

from agent_reach.channels.taiwan_news import (
    DEFAULT_NEWS_SOURCES,
    TaiwanNewsChannel,
    normalize_feed_entries,
)

SAMPLE_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Example Taiwan News</title>
    <item>
      <title>AI 新創在台灣成長</title>
      <link>https://example.com/news/1</link>
      <description>台灣 AI 新創生態持續升溫。</description>
      <pubDate>Thu, 02 Jul 2026 10:00:00 +0800</pubDate>
    </item>
    <item>
      <title>半導體供應鏈更新</title>
      <link>https://example.com/news/2</link>
      <description><![CDATA[供應鏈需求回穩。]]></description>
    </item>
  </channel>
</rss>
"""


def test_normalize_feed_entries_returns_stable_item_shape():
    items = normalize_feed_entries(SAMPLE_FEED, source_name="example")

    assert items == [
        {
            "platform": "taiwan_news",
            "source": "example",
            "title": "AI 新創在台灣成長",
            "published_at": "Thu, 02 Jul 2026 10:00:00 +0800",
            "url": "https://example.com/news/1",
            "excerpt": "台灣 AI 新創生態持續升溫。",
        },
        {
            "platform": "taiwan_news",
            "source": "example",
            "title": "半導體供應鏈更新",
            "published_at": "",
            "url": "https://example.com/news/2",
            "excerpt": "供應鏈需求回穩。",
        },
    ]


def test_read_sources_continues_when_one_feed_fails(monkeypatch):
    channel = TaiwanNewsChannel()

    def fake_fetch(url):
        if "broken" in url:
            raise OSError("blocked")
        return SAMPLE_FEED

    monkeypatch.setattr("agent_reach.channels.taiwan_news._fetch_feed", fake_fetch)

    result = channel.read_sources(
        [
            {"name": "ok", "url": "https://example.com/feed.xml"},
            {"name": "broken", "url": "https://broken.example/feed.xml"},
        ]
    )

    assert len(result["items"]) == 2
    assert result["errors"] == [{"source": "broken", "error": "blocked"}]


def test_check_reports_reachable_feed_count(monkeypatch):
    def fake_fetch(url):
        if "inside" in url:
            raise OSError("blocked")
        return SAMPLE_FEED

    monkeypatch.setattr("agent_reach.channels.taiwan_news._fetch_feed", fake_fetch)

    channel = TaiwanNewsChannel()
    status, message = channel.check()

    assert status == "warn"
    assert "2/3 feeds reachable" in message
    assert channel.active_backend == "feedparser"


def test_default_news_sources_are_verified_minimum_set():
    assert DEFAULT_NEWS_SOURCES == [
        {"name": "technews", "url": "https://technews.tw/feed/"},
        {"name": "inside", "url": "https://www.inside.com.tw/feed/rss"},
        {"name": "pts", "url": "https://news.pts.org.tw/xml/newsfeed.xml"},
    ]
