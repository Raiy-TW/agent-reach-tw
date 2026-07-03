# -*- coding: utf-8 -*-
"""Taiwan government public-data helpers."""

from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from .base import Channel

DATA_GOV_TW_SEARCH_URL = "https://data.gov.tw/datasets/search"
FIND_BIZ_QUERY_URL = "https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do"
_TIMEOUT = 10
_UA = "agent-reach/1.0"


def data_gov_search_url(query: str) -> str:
    """Build a confirmed data.gov.tw search URL."""
    return f"{DATA_GOV_TW_SEARCH_URL}?{urlencode({'qs': query.strip()})}"


def build_public_data_links(query: str) -> list[dict[str, str]]:
    """Return official Taiwan public-data helper links for an agent query."""
    normalized_query = query.strip()
    return [
        {
            "platform": "gov_tw",
            "source": "data.gov.tw",
            "kind": "open_data_search",
            "query": normalized_query,
            "url": data_gov_search_url(normalized_query),
            "status": "confirmed_link",
        },
        {
            "platform": "gov_tw",
            "source": "findbiz.nat.gov.tw",
            "kind": "business_registry_lookup",
            "query": normalized_query,
            "url": FIND_BIZ_QUERY_URL,
            "status": "helper_only",
        },
    ]


def _probe_url(url: str) -> None:
    request = Request(url, headers={"User-Agent": _UA})
    with urlopen(request, timeout=_TIMEOUT) as response:
        status = getattr(response, "status", 200)
        if status >= 400:
            raise OSError(f"HTTP {status}")


class GovTWChannel(Channel):
    name = "gov_tw"
    description = "台灣政府開放資料"
    backends = ["data.gov.tw", "verified public links"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        host = urlparse(url).netloc.lower()
        return host.endswith("gov.tw")

    def search_links(self, query: str) -> list[dict[str, str]]:
        return build_public_data_links(query)

    def check(self, config=None):
        try:
            _probe_url(data_gov_search_url("公司"))
        except Exception as e:
            self.active_backend = None
            return (
                "warn",
                "data.gov.tw search probe failed; "
                f"gov_tw remains helper-only for official links: {e}",
            )

        self.active_backend = "data.gov.tw"
        return "ok", "data.gov.tw search reachable; findbiz remains helper-only"
