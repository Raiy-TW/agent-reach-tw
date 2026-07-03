# -*- coding: utf-8 -*-
"""Tests for Taiwan ecommerce price helpers."""

from pathlib import Path

from agent_reach.channels.taiwan_ecommerce import (
    TaiwanEcommerceChannel,
    normalize_product,
    normalize_twd_price,
    parse_momo_product,
    parse_pchome_product,
)

FIXTURES = Path(__file__).parent / "fixtures" / "ecommerce"
FETCHED_AT = "2026-07-02T22:00:00+08:00"


def test_normalize_twd_price_strips_currency_and_separators():
    assert normalize_twd_price("NT$ 1,299") == 1299
    assert normalize_twd_price("$2,990") == 2990
    assert normalize_twd_price("特價 399 元") == 399


def test_normalize_product_returns_stable_schema():
    assert normalize_product(
        platform="pchome",
        title="Apple iPhone 16 透明保護殼",
        price=1290,
        url="https://24h.pchome.com.tw/prod/DYAJ4B-A900H9N4K",
        fetched_at=FETCHED_AT,
        promo="刷卡滿額回饋",
        stock_status="in_stock",
    ) == {
        "platform": "pchome",
        "title": "Apple iPhone 16 透明保護殼",
        "price": 1290,
        "currency": "TWD",
        "stock_status": "in_stock",
        "promo": "刷卡滿額回饋",
        "url": "https://24h.pchome.com.tw/prod/DYAJ4B-A900H9N4K",
        "fetched_at": FETCHED_AT,
    }


def test_parse_pchome_product_reads_json_ld_offer():
    html = (FIXTURES / "pchome_product.html").read_text(encoding="utf-8")

    assert parse_pchome_product(html, fetched_at=FETCHED_AT) == {
        "platform": "pchome",
        "title": "Apple iPhone 16 透明保護殼",
        "price": 1290,
        "currency": "TWD",
        "stock_status": "in_stock",
        "promo": "刷卡滿額回饋",
        "url": "https://24h.pchome.com.tw/prod/DYAJ4B-A900H9N4K",
        "fetched_at": FETCHED_AT,
    }


def test_parse_momo_product_reads_public_page_fields():
    html = (FIXTURES / "momo_product.html").read_text(encoding="utf-8")

    assert parse_momo_product(
        html,
        url="https://www.momoshop.com.tw/goods/GoodsDetail.jsp?i_code=12345678",
        fetched_at=FETCHED_AT,
    ) == {
        "platform": "momo",
        "title": "Logitech MX Master 3S 無線滑鼠",
        "price": 2990,
        "currency": "TWD",
        "stock_status": "unknown",
        "promo": "限時折價券可用",
        "url": "https://www.momoshop.com.tw/goods/GoodsDetail.jsp?i_code=12345678",
        "fetched_at": FETCHED_AT,
    }


def test_check_reports_partial_platform_probe_failures(monkeypatch):
    def fake_probe(url):
        if "momoshop" in url:
            raise OSError("blocked")

    monkeypatch.setattr("agent_reach.channels.taiwan_ecommerce._probe_url", fake_probe)

    channel = TaiwanEcommerceChannel()
    status, message = channel.check()

    assert status == "warn"
    assert "1/2 platforms reachable" in message
    assert "momo: blocked" in message
    assert channel.active_backend == "public HTTP"


def test_check_reports_ok_when_all_platform_probes_pass(monkeypatch):
    monkeypatch.setattr(
        "agent_reach.channels.taiwan_ecommerce._probe_url",
        lambda url: None,
    )

    channel = TaiwanEcommerceChannel()
    status, message = channel.check()

    assert status == "ok"
    assert "2/2 platforms reachable" in message
    assert channel.active_backend == "public HTTP"


def test_channel_read_product_routes_by_host(monkeypatch):
    pchome_html = (FIXTURES / "pchome_product.html").read_text(encoding="utf-8")

    monkeypatch.setattr(
        "agent_reach.channels.taiwan_ecommerce._fetch_text",
        lambda url: pchome_html,
    )

    channel = TaiwanEcommerceChannel()
    product = channel.read_product(
        "https://24h.pchome.com.tw/prod/DYAJ4B-A900H9N4K",
        fetched_at=FETCHED_AT,
    )

    assert product["platform"] == "pchome"
    assert product["price"] == 1290
