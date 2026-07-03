# -*- coding: utf-8 -*-
"""Taiwan ecommerce price channel."""

import json
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from .base import Channel

_ECOMMERCE_HOSTS = {
    "pchome.com.tw",
    "momoshop.com.tw",
    "buy.yahoo.com.tw",
    "tw.buy.yahoo.com",
}
_TIMEOUT = 10
_UA = "agent-reach/1.0"
_TAIPEI_TZ = timezone(timedelta(hours=8))
_PCHOME_PROBE_URL = "https://24h.pchome.com.tw/prod/DYAJ4B-A900H9N4K"
_MOMO_PROBE_URL = "https://www.momoshop.com.tw/"
_PROBE_URLS = {
    "pchome": _PCHOME_PROBE_URL,
    "momo": _MOMO_PROBE_URL,
}


def _now_taipei() -> str:
    return datetime.now(_TAIPEI_TZ).isoformat(timespec="seconds")


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_twd_price(text: str) -> int | None:
    """Normalize Taiwan dollar price text into an integer."""
    match = re.search(r"([0-9][0-9,]*)", text.replace("，", ","))
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def normalize_product(
    *,
    platform: str,
    title: str,
    price: int | None,
    url: str,
    fetched_at: str | None = None,
    currency: str = "TWD",
    stock_status: str = "unknown",
    promo: str = "",
) -> dict:
    """Return the stable Taiwan ecommerce product shape."""
    return {
        "platform": platform,
        "title": _clean_text(title),
        "price": price,
        "currency": currency or "TWD",
        "stock_status": stock_status,
        "promo": _clean_text(promo),
        "url": url,
        "fetched_at": fetched_at or _now_taipei(),
    }


def _json_ld_products(soup: BeautifulSoup) -> list[dict]:
    products = []
    for script in soup.select('script[type="application/ld+json"]'):
        raw = script.string or script.get_text()
        if not raw.strip():
            continue
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        candidates = parsed if isinstance(parsed, list) else [parsed]
        products.extend(
            item
            for item in candidates
            if isinstance(item, dict) and item.get("@type") == "Product"
        )
    return products


def _offer(product: dict) -> dict:
    offers = product.get("offers") or {}
    if isinstance(offers, list):
        return offers[0] if offers and isinstance(offers[0], dict) else {}
    return offers if isinstance(offers, dict) else {}


def _stock_status(availability: str) -> str:
    value = availability.lower()
    if "instock" in value:
        return "in_stock"
    if "outofstock" in value:
        return "out_of_stock"
    return "unknown"


def _first_text(soup: BeautifulSoup, selectors: tuple[str, ...]) -> str:
    for selector in selectors:
        node = soup.select_one(selector)
        if node:
            return _clean_text(node.get_text(" ", strip=True))
    return ""


def _meta_content(soup: BeautifulSoup, key: str) -> str:
    node = soup.select_one(f'meta[property="{key}"], meta[name="{key}"]')
    return _clean_text(node.get("content", "")) if node else ""


def parse_pchome_product(
    html: str,
    *,
    url: str = "",
    fetched_at: str | None = None,
) -> dict:
    """Parse a PChome 24h public product page."""
    soup = BeautifulSoup(html, "html.parser")
    product = (_json_ld_products(soup) or [{}])[0]
    offer = _offer(product)
    title = product.get("name") or _first_text(soup, (".c-prodInfo__title", "h1"))
    price = normalize_twd_price(str(offer.get("price", "")))
    promo = _first_text(soup, (".c-prodInfo__promo", ".promo"))

    return normalize_product(
        platform="pchome",
        title=title,
        price=price,
        url=offer.get("url") or url,
        fetched_at=fetched_at,
        currency=offer.get("priceCurrency") or "TWD",
        stock_status=_stock_status(str(offer.get("availability", ""))),
        promo=promo,
    )


def parse_momo_product(
    html: str,
    *,
    url: str,
    fetched_at: str | None = None,
) -> dict:
    """Parse a momo public product page."""
    soup = BeautifulSoup(html, "html.parser")
    title = _first_text(soup, (".prdName", "h1")) or _meta_content(soup, "og:title")
    price_text = _first_text(soup, (".price", ".prdPrice", ".special"))
    promo = _first_text(soup, (".prdNote", ".promo"))

    return normalize_product(
        platform="momo",
        title=title,
        price=normalize_twd_price(price_text),
        url=_meta_content(soup, "og:url") or url,
        fetched_at=fetched_at,
        promo=promo,
    )


def _fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": _UA})
    with urlopen(request, timeout=_TIMEOUT) as response:
        return response.read().decode("utf-8", errors="replace")


def _probe_url(url: str) -> None:
    request = Request(url, headers={"User-Agent": _UA})
    with urlopen(request, timeout=_TIMEOUT) as response:
        status = getattr(response, "status", 200)
        if status >= 400:
            raise OSError(f"HTTP {status}")


class TaiwanEcommerceChannel(Channel):
    name = "taiwan_ecommerce"
    description = "台灣電商價格"
    backends = ["public HTTP", "Playwright fallback"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        host = urlparse(url).netloc.lower()
        return any(host == domain or host.endswith(f".{domain}") for domain in _ECOMMERCE_HOSTS)

    def check(self, config=None):
        reachable = []
        errors = []

        for platform, url in _PROBE_URLS.items():
            try:
                _probe_url(url)
            except Exception as e:
                errors.append(f"{platform}: {e}")
            else:
                reachable.append(platform)

        if len(reachable) == len(_PROBE_URLS):
            self.active_backend = "public HTTP"
            return "ok", "2/2 platforms reachable via public HTTP"

        if reachable:
            self.active_backend = "public HTTP"
            return (
                "warn",
                f"{len(reachable)}/{len(_PROBE_URLS)} platforms reachable；"
                f"{'; '.join(errors)}",
            )

        self.active_backend = None
        return (
            "warn",
            f"0/{len(_PROBE_URLS)} platforms reachable；保留 Playwright fallback；"
            f"{'; '.join(errors)}",
        )

    def read_product(self, url: str, *, fetched_at: str | None = None) -> dict:
        html = _fetch_text(url)
        host = urlparse(url).netloc.lower()

        if "pchome.com.tw" in host:
            return parse_pchome_product(html, url=url, fetched_at=fetched_at)
        if "momoshop.com.tw" in host:
            return parse_momo_product(html, url=url, fetched_at=fetched_at)

        raise ValueError(f"Unsupported Taiwan ecommerce URL: {url}")
