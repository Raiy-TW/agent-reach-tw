# -*- coding: utf-8 -*-
"""Tests for the Bahamut Taiwan channel."""

from pathlib import Path
from urllib.error import URLError

from agent_reach.channels.bahamut import BahamutChannel, parse_post, parse_topic_list

FIXTURES = Path(__file__).parent / "fixtures" / "bahamut"


def test_parse_topic_list_extracts_topics():
    html = (FIXTURES / "topic_list.html").read_text(encoding="utf-8")

    topics = parse_topic_list(html, board_url="https://forum.gamer.com.tw/B.php?bsn=60030")

    assert topics == [
        {
            "platform": "bahamut",
            "board": "60030",
            "subboard": "硬體除錯",
            "title": "【問題】CS2 玩沒多久就會跳出去",
            "excerpt": "如標題，試了重新下載與檢查檔案。",
            "author": "a609267",
            "reply_count": 1,
            "gp_count": 12,
            "interaction_count": "5",
            "view_count": "1k",
            "last_reply_at": "1 小時前",
            "url": "https://forum.gamer.com.tw/C.php?bsn=60030&snA=685179&tnum=1",
        }
    ]


def test_parse_post_extracts_content_and_replies():
    html = (FIXTURES / "post.html").read_text(encoding="utf-8")

    post = parse_post(
        html,
        url="https://forum.gamer.com.tw/C.php?bsn=60030&snA=685179&tnum=1",
    )

    assert post == {
        "platform": "bahamut",
        "board": "60030",
        "title": "【問題】CS2 玩沒多久就會跳出去",
        "author": "灰羽翼",
        "author_id": "a609267",
        "published_at": "2026-07-02 20:53:35",
        "category": "硬體除錯",
        "content": "如標題，試了重新下載與檢查檔案。\n目前作業系統 WIN10。",
        "replies": [
            {
                "floor": "B3",
                "author": "約翰雷",
                "text": "檢查一下事件檢視器。",
                "published_at": "2026-07-02 21:22:53",
            }
        ],
        "url": "https://forum.gamer.com.tw/C.php?bsn=60030&snA=685179&tnum=1",
    }


def test_bahamut_check_reports_ok_when_public_board_is_reachable(monkeypatch):
    import urllib.request

    html = (FIXTURES / "topic_list.html").read_bytes()

    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def read(self):
            return html

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: FakeResponse())

    channel = BahamutChannel()
    status, message = channel.check()

    assert status == "ok"
    assert "public HTTP" in message
    assert channel.active_backend == "public HTTP"


def test_bahamut_check_warns_when_public_board_is_unreachable(monkeypatch):
    import urllib.request

    def fake_urlopen(req, timeout=None):
        raise URLError("blocked")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    channel = BahamutChannel()
    status, message = channel.check()

    assert status == "warn"
    assert "Bahamut public HTTP 連線失敗" in message
    assert channel.active_backend is None
