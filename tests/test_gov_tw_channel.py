# -*- coding: utf-8 -*-
"""Tests for Taiwan government public-data helpers."""

from urllib.error import HTTPError

from agent_reach.channels.gov_tw import (
    DATA_GOV_TW_SEARCH_URL,
    FIND_BIZ_QUERY_URL,
    GovTWChannel,
    build_public_data_links,
    data_gov_search_url,
)


def test_data_gov_search_url_encodes_query():
    assert (
        data_gov_search_url("公司 登記")
        == f"{DATA_GOV_TW_SEARCH_URL}?qs=%E5%85%AC%E5%8F%B8+%E7%99%BB%E8%A8%98"
    )


def test_public_data_links_mark_confirmed_and_helper_only_sources():
    links = build_public_data_links("台積電")

    assert links == [
        {
            "platform": "gov_tw",
            "source": "data.gov.tw",
            "kind": "open_data_search",
            "query": "台積電",
            "url": data_gov_search_url("台積電"),
            "status": "confirmed_link",
        },
        {
            "platform": "gov_tw",
            "source": "findbiz.nat.gov.tw",
            "kind": "business_registry_lookup",
            "query": "台積電",
            "url": FIND_BIZ_QUERY_URL,
            "status": "helper_only",
        },
    ]


def test_gov_tw_channel_search_links_delegates_to_helper():
    channel = GovTWChannel()

    assert channel.search_links("統一編號") == build_public_data_links("統一編號")


def test_check_reports_ok_when_data_gov_search_is_reachable(monkeypatch):
    opened_urls = []

    def fake_urlopen(request, timeout):
        opened_urls.append(request.full_url)

        class Response:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        return Response()

    monkeypatch.setattr("agent_reach.channels.gov_tw.urlopen", fake_urlopen)

    channel = GovTWChannel()
    status, message = channel.check()

    assert status == "ok"
    assert "data.gov.tw search reachable" in message
    assert channel.active_backend == "data.gov.tw"
    assert opened_urls == [data_gov_search_url("公司")]


def test_check_warns_when_data_gov_search_is_blocked(monkeypatch):
    def fake_urlopen(request, timeout):
        raise HTTPError(request.full_url, 403, "Forbidden", hdrs=None, fp=None)

    monkeypatch.setattr("agent_reach.channels.gov_tw.urlopen", fake_urlopen)

    channel = GovTWChannel()
    status, message = channel.check()

    assert status == "warn"
    assert "helper-only" in message
    assert channel.active_backend is None
