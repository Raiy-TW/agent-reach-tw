---
name: agent-reach-tw
description: Use when the user needs Taiwan public web data, PTT, Dcard, Bahamut, Taiwan news RSS, PChome/momo/Yahoo Shopping prices, data.gov.tw, company lookup links, or Agent Reach Taiwan Edition availability checks.
---

# Agent Reach Taiwan Edition Skill

Generic AI agent skill for Agent Reach Taiwan Edition. It helps agents read and search Taiwan public web data. It is not a login-backed scraper, write tool, or anti-bot bypass layer.

## When to use

Use this skill when the user needs:

- Taiwan social/community sources: PTT, Dcard, Bahamut
- Taiwan news: RSS and public news sources
- Taiwan ecommerce: PChome, momo, Yahoo Shopping product pages and TWD prices
- Taiwan government/public data: data.gov.tw and official business registry helper links
- Installation or availability checks for Agent Reach Taiwan Edition

Do not use it for:

- Posting, commenting, liking, messaging, or any write operation
- Login automation or private community scraping
- CAPTCHA / anti-bot / Cloudflare bypass
- Pretending blocked 403/429 content was fetched directly
- Tasks that already have a more specialized installed skill

## Start with a health check

Before real data collection, run:

```bash
agent-reach doctor --json
```

Pick the path from each channel's `status` and `active_backend`. Do not guess.

## Core rules

1. **Doctor first, then route**: never assume a channel is currently usable.
2. **Public read-only**: only read public pages, RSS feeds, and official helper links.
3. **Fallback-aware**: report 403/429/DNS/Cloudflare limits honestly; use fallback paths where documented.
4. **Do not invent commands**: use the CLI, Python channels, or reference docs.
5. **State limitations**: distinguish directly fetched data from helper links or fallback output.

## Quick commands

```bash
# Health check
agent-reach doctor --json

# Server dry-run install (no system changes)
agent-reach install --env=server --channels=tw --dry-run

# Version
agent-reach version
```

## Python quick usage

```python
from agent_reach.channels import get_channel

news = get_channel("taiwan_news")
result = news.read_sources(limit_per_source=3)

public_data = get_channel("gov_tw")
links = public_data.search_links("company registration")
```

## Channel status semantics

- `ok`: use the current backend directly.
- `warn`: the site may be blocked by 403/Cloudflare/DNS/rate limits; use fallback or report official helper links only.
- `off` / `error`: do not force scraping; report the missing dependency or unavailable state.

## Known Taiwan channels

- `ptt`: PTT board index, posts, and push-comment parser.
- `dcard`: public text / Jina-style fallback parser; degrades clearly on 403.
- `bahamut`: Bahamut topic list, post, and reply parser; may need fallback.
- `taiwan_news`: Taiwan news RSS normalizer with per-source partial failure handling.
- `taiwan_ecommerce`: PChome / momo / Yahoo Shopping product parser and TWD price normalization.
- `gov_tw`: `data.gov.tw` search helper plus official business registry helper-only link.

## Routing table

| User intent | Category | Details |
| --- | --- | --- |
| PTT / Dcard / Bahamut | taiwan-social | [references/taiwan-social.md](references/taiwan-social.md) |
| PChome / momo / Yahoo Shopping prices | taiwan-commerce | [references/taiwan-commerce.md](references/taiwan-commerce.md) |
| data.gov.tw / business registry / company data | taiwan-public-data | [references/taiwan-public-data.md](references/taiwan-public-data.md) |
| Web pages / RSS / Jina fallback | web | [references/web.md](references/web.md) |
| Search fallback | search | [references/search.md](references/search.md) |

## Common task examples

### Taiwan news RSS

```python
from agent_reach.channels import get_channel

channel = get_channel("taiwan_news")
result = channel.read_sources(limit_per_source=5)
```

### Government public data / company lookup entry points

```python
from agent_reach.channels import get_channel

channel = get_channel("gov_tw")
links = channel.search_links("company registration")
```

### Taiwan ecommerce prices

Run `agent-reach doctor --json` first to check `taiwan_ecommerce`, then follow the parser/fallback paths in `references/taiwan-commerce.md`. If a site blocks public HTTP, report the limitation and fallback path; do not fabricate prices.

## Verification checklist

- [ ] Ran `agent-reach doctor --json`
- [ ] Confirmed channel status / active_backend
- [ ] Used only public read-only data
- [ ] Explained 403/429/Cloudflare limitations where relevant
- [ ] Returned source URLs or official helper links
