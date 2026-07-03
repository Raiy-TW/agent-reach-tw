# -*- coding: utf-8 -*-
"""Tests for the Dcard Taiwan channel."""

from pathlib import Path
from urllib.error import HTTPError, URLError

from agent_reach.channels.dcard import DcardChannel, parse_public_post_text

FIXTURES = Path(__file__).parent / "fixtures" / "dcard"


def test_parse_public_post_text_normalizes_jina_style_markdown():
    text = (FIXTURES / "post_markdown.txt").read_text(encoding="utf-8")

    post = parse_public_post_text(text, url="https://www.dcard.tw/f/tech/p/256789123")

    assert post == {
        "platform": "dcard",
        "forum": "tech",
        "post_id": "256789123",
        "title": "最近 AI 工具在工作上的使用心得",
        "content": (
            "最近在工作上開始固定用 AI 做資料整理，但還是需要人工檢查來源。\n\n"
            "我覺得最有幫助的是先整理問題，再讓工具產生不同角度。"
        ),
        "comments": [
            {"author": "匿名", "text": "同意，來源檢查很重要。"},
            {"author": "工程師", "text": "內部資料不要直接丟外部工具。"},
        ],
        "url": "https://www.dcard.tw/f/tech/p/256789123",
    }


def test_dcard_check_warns_on_cloudflare_403(monkeypatch):
    import urllib.request

    def fake_urlopen(req, timeout=None):
        raise HTTPError(req.full_url, 403, "Forbidden", hdrs=None, fp=None)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    channel = DcardChannel()
    status, message = channel.check()

    assert status == "warn"
    assert "Dcard public HTTP/API 目前不可直接讀取" in message
    assert channel.active_backend is None


def test_dcard_check_warns_on_network_error(monkeypatch):
    import urllib.request

    def fake_urlopen(req, timeout=None):
        raise URLError("blocked")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    channel = DcardChannel()
    status, message = channel.check()

    assert status == "warn"
    assert "Dcard public HTTP/API 檢查失敗" in message
    assert channel.active_backend is None


def test_dcard_check_ok_when_public_forum_page_is_reachable(monkeypatch):
    import urllib.request

    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def read(self):
            return b"<html><title>Dcard Tech</title></html>"

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: FakeResponse())

    channel = DcardChannel()
    status, message = channel.check()

    assert status == "warn"
    assert "public page reachable" in message
    assert channel.active_backend == "public web page"
