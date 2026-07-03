# -*- coding: utf-8 -*-
"""Tests for Taiwan edition channel scaffolding."""

from agent_reach.channels import get_channel


def test_taiwan_mvp_channels_are_registered():
    for name in (
        "ptt",
        "dcard",
        "bahamut",
        "taiwan_news",
        "taiwan_ecommerce",
        "gov_tw",
    ):
        assert get_channel(name) is not None


def test_taiwan_channels_have_basic_url_routing():
    samples = {
        "ptt": "https://www.ptt.cc/bbs/PC_Shopping/index.html",
        "dcard": "https://www.dcard.tw/f/tech",
        "bahamut": "https://forum.gamer.com.tw/B.php?bsn=60030",
        "taiwan_news": "https://www.cna.com.tw/news/aipl/202607020001.aspx",
        "taiwan_ecommerce": "https://24h.pchome.com.tw/prod/DYAJ4B-A900H9N4K",
        "gov_tw": "https://data.gov.tw/dataset/9400",
    }

    for name, url in samples.items():
        channel = get_channel(name)
        assert channel is not None
        assert channel.can_handle(url)
        assert isinstance(channel.can_handle("https://example.com"), bool)


def test_taiwan_scaffold_checks_degrade_without_crashing(tmp_path):
    from agent_reach.config import Config

    config = Config(config_path=tmp_path / "config.yaml")

    for name in (
        "ptt",
        "dcard",
        "bahamut",
        "taiwan_news",
        "taiwan_ecommerce",
        "gov_tw",
    ):
        channel = get_channel(name)
        assert channel is not None
        status, message = channel.check(config)
        assert status in {"ok", "warn", "off", "error"}
        assert message.strip()
        assert channel.active_backend is None or isinstance(channel.active_backend, str)
