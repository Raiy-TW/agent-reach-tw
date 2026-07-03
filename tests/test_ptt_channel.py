# -*- coding: utf-8 -*-
"""Tests for the PTT Taiwan channel."""

from pathlib import Path
from urllib.error import URLError

from agent_reach.channels.ptt import PTTChannel, parse_board_index, parse_post

FIXTURES = Path(__file__).parent / "fixtures" / "ptt"


def test_parse_board_index_extracts_visible_posts():
    html = (FIXTURES / "index_pc_shopping.html").read_text(encoding="utf-8")

    posts = parse_board_index(html, board="PC_Shopping")

    assert posts == [
        {
            "platform": "ptt",
            "board": "PC_Shopping",
            "title": "[菜單] 40K 遊戲機菜單請益",
            "author": "builder",
            "date": "7/02",
            "push_count": "3",
            "url": "https://www.ptt.cc/bbs/PC_Shopping/M.1719900000.A.123.html",
        }
    ]


def test_parse_post_extracts_metadata_content_and_pushes():
    html = (FIXTURES / "post_with_pushes.html").read_text(encoding="utf-8")

    post = parse_post(
        html,
        board="PC_Shopping",
        url="https://www.ptt.cc/bbs/PC_Shopping/M.1719900000.A.123.html",
    )

    assert post["platform"] == "ptt"
    assert post["board"] == "PC_Shopping"
    assert post["title"] == "[菜單] 40K 遊戲機菜單請益"
    assert post["author"] == "builder (組電腦)"
    assert post["published_at"] == "Tue Jul  2 12:34:56 2026"
    assert post["url"] == "https://www.ptt.cc/bbs/PC_Shopping/M.1719900000.A.123.html"
    assert "這是文章第一段。" in post["content"]
    assert "這是文章第二段。" in post["content"]
    assert "發信站" not in post["content"]
    assert post["comments"] == [
        {
            "type": "push",
            "user": "user1",
            "text": "電源可以再抓大一點",
            "ipdatetime": "07/02 12:40",
        },
        {
            "type": "boo",
            "user": "user2",
            "text": "顯卡價格太高",
            "ipdatetime": "07/02 12:45",
        },
    ]


def test_ptt_channel_builds_board_index_url():
    assert (
        PTTChannel().board_index_url("PC_Shopping")
        == "https://www.ptt.cc/bbs/PC_Shopping/index.html"
    )


def test_ptt_check_reports_ok_when_board_index_is_reachable(monkeypatch):
    import urllib.request

    html = (FIXTURES / "index_pc_shopping.html").read_bytes()
    seen = {}

    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def read(self):
            return html

    def fake_urlopen(req, timeout=None):
        seen["url"] = req.full_url
        seen["cookie"] = req.get_header("Cookie")
        seen["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    channel = PTTChannel()
    status, message = channel.check()

    assert status == "ok"
    assert "public HTTP" in message
    assert channel.active_backend == "public HTTP"
    assert seen == {
        "url": "https://www.ptt.cc/bbs/PC_Shopping/index.html",
        "cookie": "over18=1",
        "timeout": 10,
    }


def test_ptt_check_warns_when_board_index_is_unreachable(monkeypatch):
    import urllib.request

    def fake_urlopen(req, timeout=None):
        raise URLError("blocked")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    channel = PTTChannel()
    status, message = channel.check()

    assert status == "warn"
    assert "PTT public HTTP 连接失败" in message
    assert channel.active_backend is None
