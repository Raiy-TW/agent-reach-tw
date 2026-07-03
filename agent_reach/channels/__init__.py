# -*- coding: utf-8 -*-
"""
Channel registry — lists all supported platforms for doctor checks.
"""

from typing import List, Optional

from .bahamut import BahamutChannel

# Import all channels
from .base import Channel
from .bilibili import BilibiliChannel
from .dcard import DcardChannel
from .exa_search import ExaSearchChannel
from .facebook import FacebookChannel
from .github import GitHubChannel
from .gov_tw import GovTWChannel
from .instagram import InstagramChannel
from .linkedin import LinkedInChannel
from .ptt import PTTChannel
from .reddit import RedditChannel
from .rss import RSSChannel
from .taiwan_ecommerce import TaiwanEcommerceChannel
from .taiwan_news import TaiwanNewsChannel
from .twitter import TwitterChannel
from .v2ex import V2EXChannel
from .web import WebChannel
from .xiaohongshu import XiaoHongShuChannel
from .xiaoyuzhou import XiaoyuzhouChannel
from .xueqiu import XueqiuChannel
from .youtube import YouTubeChannel

ALL_CHANNELS: List[Channel] = [
    GitHubChannel(),
    TwitterChannel(),
    YouTubeChannel(),
    RedditChannel(),
    FacebookChannel(),
    InstagramChannel(),
    BilibiliChannel(),
    XiaoHongShuChannel(),
    LinkedInChannel(),
    XiaoyuzhouChannel(),
    V2EXChannel(),
    XueqiuChannel(),
    RSSChannel(),
    PTTChannel(),
    DcardChannel(),
    BahamutChannel(),
    TaiwanNewsChannel(),
    TaiwanEcommerceChannel(),
    GovTWChannel(),
    ExaSearchChannel(),
    WebChannel(),
]


def get_channel(name: str) -> Optional[Channel]:
    """Get a channel by name."""
    for ch in ALL_CHANNELS:
        if ch.name == name:
            return ch
    return None


def get_all_channels() -> List[Channel]:
    """Get all registered channels."""
    return ALL_CHANNELS


__all__ = [
    "Channel",
    "ALL_CHANNELS",
    "get_channel",
    "get_all_channels",
]
