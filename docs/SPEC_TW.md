# Agent Reach Taiwan Edition SPEC.md

> **For Codex / Antigravity:** Implement this spec by cloning/forking `https://github.com/Panniantong/Agent-Reach`, preserving its capability-layer architecture, and adding Taiwan-focused channels. Do not rewrite from scratch unless a specific upstream abstraction blocks progress.

**Goal:** Build a Taiwan-focused AI agent internet capability layer for market research, social listening, content ideation, ecommerce price checks, and public-data lookup.

**Architecture:** Start from Agent Reach as the base. Keep the existing `channels/`, `doctor`, `install`, `config`, and skill/reference documentation pattern. Add Taiwan-specific channels as first-class modules with backend probing, command guidance, tests, and graceful fallback.

**Tech Stack:** Python 3.10+, CLI app, pytest, requests/httpx where needed, BeautifulSoup/lxml for HTML parsing, feedparser for feeds, Playwright only for pages that cannot be accessed reliably by plain HTTP. Prefer public endpoints and read-only access.

---

## 1. Product Positioning

### Working name

Recommended repo name:

- `agent-reach-tw`

Alternative names:

- `taiwan-reach`
- `agent-reach-taiwan`

### One-line positioning

Give AI agents Taiwan-specific internet reach: PTT, Dcard, Threads, Bahamut, Taiwanese ecommerce prices, news, government open data, and business registry lookup.

### Target users

- Solo AI consultants serving Taiwanese SMEs
- Ecommerce operators monitoring competitors and prices
- Content operators researching Taiwan social trends
- Agents that need Taiwan-local context beyond global web search

### Primary use cases

1. **Competitor monitoring**
   - Track product prices on momo / PChome / Shopee / Yahoo Shopping where legally and technically feasible.
   - Compare titles, prices, stock hints, ratings, promotions, and URLs.

2. **Social listening**
   - Search/read PTT, Dcard, Bahamut, Threads public content when possible.
   - Extract posts, comments/replies, timestamps, engagement signals, and URLs.

3. **Content ideation**
   - Pull Taiwan-local discussion topics and turn them into structured research material.
   - Support agents writing Threads / LinkedIn / blog posts for local audiences.

4. **Business intelligence**
   - Query company registration/public government data.
   - Monitor Taiwanese news/RSS sources.

5. **Agent capability bootstrap**
   - Let Codex / Claude Code / generic runtime / Cursor know which command or library to use per Taiwan platform.
   - Run `doctor` to show what works on the current machine.

---

## 2. Strategic Decision: Fork First, Rewrite Later

### Decision

Use Agent Reach as the starting point. Do not build from scratch for v0.1.

### Rationale

Agent Reach already has the hard generic parts:

- Channel registry
- Backend probing
- `doctor` status output
- Install flow
- Config directory conventions
- Skill/reference documentation pattern
- Tests for channel contracts

The Taiwan version mainly needs new platform modules and Taiwan-specific usage docs. Rewriting the base now would delay validation and recreate solved infrastructure.

### Long-term migration option

If the fork proves valuable, gradually extract a cleaner independent package after v0.3:

- Keep public interface compatible.
- Move Taiwan channels into a separate package if upstream merge is undesirable.
- Remove China-heavy defaults only after Taiwan channels are stable.

---

## 3. Scope

### v0.1 MVP channels

Implement these first:

1. `ptt`
2. `dcard`
3. `bahamut`
4. `taiwan_news`
5. `taiwan_ecommerce` with at least PChome and momo probes
6. `gov_tw` for government open data / business registry links and simple lookups

### v0.2 channels

1. `threads_tw`
2. `shopee_tw`
3. `plurk`
4. `mobile01`
5. `104_jobs` or `yourator`

### v0.3 channels

1. `instagram_tw` via OpenCLI if desktop login is available
2. `facebook_tw` via OpenCLI if desktop login is available
3. `line_openchat` only if a compliant, read-only, user-owned access path exists

### Explicit non-goals for v0.1

- No posting, commenting, liking, following, or account operations.
- No CAPTCHA bypass.
- No scraping behind paywalls or private groups.
- No collection of personal data beyond public post metadata required for research.
- No stealth anti-bot evasion. Respect rate limits and fail gracefully.
- No promise that every Taiwan platform works on a server. Some should be desktop-only.

---

## 4. Taiwan Channel Requirements

Every channel must follow the same contract where possible:

```python
class Channel:
    name: str
    def probe(self) -> ProbeResult: ...
    def capabilities(self) -> list[str]: ...
```

Recommended capability names:

- `search`
- `read_post`
- `read_comments`
- `hot`
- `rss`
- `price_lookup`
- `company_lookup`
- `news_search`

Each channel should document:

- What works out of the box
- What needs browser/cookie/login
- Whether server environment is supported
- Rate-limit cautions
- Example commands or Python usage
- Fallback strategy

---

## 5. Channel Design Details

### 5.1 PTT channel

**Module:** `agent_reach/channels/ptt.py`

**MVP capabilities:**

- Read board index pages
- Read individual posts
- Extract title, author, date, content, push comments, URL
- Support popular boards such as `Gossiping`, `Stock`, `Tech_Job`, `PC_Shopping`, `e-shopping`

**Backend priority:**

1. Plain HTTP requests to `https://www.ptt.cc/bbs/{board}/index.html`
2. If age gate appears, use `over18=1` cookie
3. Optional fallback: RSS if available or board-specific public mirrors, but mark as fallback and cite source

**Data shape:**

```json
{
  "platform": "ptt",
  "board": "PC_Shopping",
  "title": "...",
  "author": "...",
  "published_at": "...",
  "content": "...",
  "comments": [
    {"type": "push", "user": "...", "text": "...", "ipdatetime": "..."}
  ],
  "url": "https://www.ptt.cc/bbs/..."
}
```

**Tests:**

- Parse fixture HTML for board index.
- Parse fixture HTML for post body and pushes.
- Probe should not fail if live network blocks; return degraded status with fix guidance.

---

### 5.2 Dcard channel

**Module:** `agent_reach/channels/dcard.py`

**MVP capabilities:**

- Search/read public posts when accessible
- Read forum latest/popular posts if public endpoints are available
- Extract title, excerpt/content, forum, author nickname if public, reaction/comment count, URL

**Backend priority:**

1. Public web/API endpoint if accessible without auth
2. Jina Reader for public post URLs
3. Playwright/browser fallback only if needed and legally acceptable

**Cautions:**

- Dcard API behavior changes frequently.
- Do not use user login for v0.1.
- If blocked, degrade to URL reading via Jina Reader or browser-rendered public page.

**Tests:**

- Fixture parser tests.
- Probe differentiates `ready`, `blocked`, and `needs_browser`.

---

### 5.3 Bahamut channel

**Module:** `agent_reach/channels/bahamut.py`

**MVP capabilities:**

- Read forum board topics
- Read post content and replies
- Search via public web search fallback if native search is unreliable

**Useful boards/use cases:**

- Games and anime trend research
- Product sentiment for gaming hardware
- Youth/community language observation

**Backend priority:**

1. Plain HTTP public pages
2. Jina Reader for URLs
3. Search engine query fallback: `site:forum.gamer.com.tw keyword`

**Tests:**

- Parse topic list fixture.
- Parse post/reply fixture.

---

### 5.4 Taiwan news channel

**Module:** `agent_reach/channels/taiwan_news.py`

**MVP capabilities:**

- Read configured RSS feeds
- Search via web search fallback
- Normalize item title, source, published_at, URL, excerpt

**Default source candidates:**

- CNA / 中央社 RSS if available
- 公視新聞網 RSS if available
- Business Next / 數位時代 RSS if available
- TechNews 科技新報 RSS if available
- Inside RSS if available
- 經理人 / 商周 only if public feeds are available

**Implementation note:**

Use a config file:

```yaml
news_sources:
  - name: cna
    url: "..."
  - name: technews
    url: "..."
```

Do not hard-fail if one source feed disappears.

---

### 5.5 Taiwan ecommerce channel

**Module:** `agent_reach/channels/taiwan_ecommerce.py`

**MVP capabilities:**

- Search products or read product URL
- Normalize title, price, original price if available, seller/platform, stock hint, promo text, URL, timestamp

**v0.1 platform priority:**

1. PChome 24h
2. momo
3. Yahoo Shopping if easy

**v0.2 platform priority:**

1. Shopee Taiwan
2. Books.com.tw
3. Rakuten Taiwan

**Backend priority:**

- Prefer public pages and documented/public endpoints.
- Use Playwright only where static HTML is insufficient.
- Do not bypass anti-bot systems.

**Data shape:**

```json
{
  "platform": "pchome",
  "query": "iPhone 16 case",
  "items": [
    {
      "title": "...",
      "price": 399,
      "currency": "TWD",
      "stock_status": "unknown|in_stock|out_of_stock",
      "promo": "...",
      "url": "...",
      "fetched_at": "2026-07-02T00:00:00+08:00"
    }
  ]
}
```

**Tests:**

- Fixture parser for PChome product card.
- Fixture parser for momo product card.
- Currency normalization test.
- Probe returns partial readiness per platform.

---

### 5.6 Government / business registry channel

**Module:** `agent_reach/channels/gov_tw.py`

**MVP capabilities:**

- Provide reliable links and query helpers for Taiwan public data.
- Company lookup by name or 統一編號 if a public API/source is available.
- Government open data search helper.

**Candidate sources to verify during implementation:**

- data.gov.tw
- 經濟部商工登記公示資料查詢服務
- 政府資料開放平台 APIs

**Important:**

Do not invent API endpoints. The implementer must verify current public endpoints before coding. If no stable endpoint exists, implement a documented search/link helper instead.

---

### 5.7 Threads Taiwan channel

**Module:** `agent_reach/channels/threads_tw.py`

**Version:** v0.2

**MVP capabilities:**

- Read public profile/post URLs if available
- Search public posts only via web search fallback if no stable CLI/API exists

**Backend priority:**

1. Jina Reader for public URLs
2. Web search fallback: `site:threads.net keyword 台灣`
3. Desktop browser/OpenCLI path only if stable

**Caution:**

Threads is important for Taiwan content, but unstable for direct scraping. Keep v0.1 focused on more reliable sources.

---

## 6. CLI / Command Design

Preserve upstream CLI style. Add Taiwan-specific channel names.

### New install examples

```bash
agent-reach install --env=auto --channels=tw
agent-reach install --env=auto --channels=ptt,dcard,bahamut,taiwan_news,taiwan_ecommerce,gov_tw
agent-reach install --env=auto --channels=tw-social
agent-reach install --env=auto --channels=tw-commerce
```

### Channel groups

```yaml
channel_groups:
  tw:
    - ptt
    - dcard
    - bahamut
    - taiwan_news
    - taiwan_ecommerce
    - gov_tw
  tw-social:
    - ptt
    - dcard
    - bahamut
    - threads_tw
  tw-commerce:
    - taiwan_ecommerce
    - gov_tw
```

### Doctor output example

```text
🇹🇼 Agent Reach TW Status
========================================
✅ Ready:
  ✅ PTT — public boards readable, over18 cookie supported
  ✅ Taiwan News RSS — 5/6 feeds reachable
  ✅ Gov TW — data.gov.tw reachable

⚠️ Partial:
  ⚠️ Dcard — public URL reading works; search endpoint blocked or changed
  ⚠️ Ecommerce — PChome ready, momo needs parser update

⬜ Optional / Desktop:
  ⬜ Threads — web-search fallback only
  ⬜ Facebook/Instagram TW — requires desktop Chrome + OpenCLI

Status: 4 ready, 2 partial, 2 optional
```

---

## 7. File Structure

Expected files to add or modify:

```text
agent_reach/
  channels/
    ptt.py
    dcard.py
    bahamut.py
    taiwan_news.py
    taiwan_ecommerce.py
    gov_tw.py
    threads_tw.py              # v0.2
  skill/
    references/
      taiwan-social.md
      taiwan-commerce.md
      taiwan-public-data.md
  guides/
    setup-taiwan.md

tests/
  fixtures/
    ptt/
    dcard/
    bahamut/
    ecommerce/
  test_ptt_channel.py
  test_dcard_channel.py
  test_bahamut_channel.py
  test_taiwan_news_channel.py
  test_taiwan_ecommerce_channel.py
  test_gov_tw_channel.py

docs/
  README_zh-TW.md
  taiwan-platforms.md
```

Modify:

```text
agent_reach/channels/__init__.py
agent_reach/doctor.py
agent_reach/cli.py
agent_reach/config.py
README.md or docs/README_en.md
pyproject.toml if new deps are needed
```

---

## 8. Implementation Plan

### Task 1: Fork/clone and rename docs minimally

**Objective:** Create a working local repo based on Agent Reach.

**Steps:**

1. Clone upstream.
2. Create a new branch: `feat/taiwan-edition-mvp`.
3. Add this spec as `docs/SPEC_TW.md`.
4. Add `docs/README_zh-TW.md` with product positioning and MVP scope.
5. Run existing tests before changes.

**Verification:**

- Existing test suite passes or existing failures are documented.
- `docs/SPEC_TW.md` exists.

**Commit:**

```bash
git add docs/SPEC_TW.md docs/README_zh-TW.md
git commit -m "docs: add Taiwan edition spec"
```

---

### Task 2: Add Taiwan channel registry scaffolding

**Objective:** Register Taiwan channels without implementing full scraping yet.

**Files:**

- Modify `agent_reach/channels/__init__.py`
- Create empty channel modules for v0.1
- Add basic probe tests

**Steps:**

1. Create modules with minimal channel classes.
2. Add each to channel registry.
3. Ensure `doctor` can show them as `not_configured` or `partial` instead of crashing.
4. Add tests for channel discovery.

**Verification:**

- `pytest tests/test_channels.py tests/test_doctor.py -q` passes.
- `agent-reach doctor` does not crash.

**Commit:**

```bash
git add agent_reach/channels tests
git commit -m "feat: register Taiwan channel scaffolding"
```

---

### Task 3: Implement PTT channel

**Objective:** Make PTT board and post reading work.

**Files:**

- Create/modify `agent_reach/channels/ptt.py`
- Create `tests/test_ptt_channel.py`
- Add fixtures under `tests/fixtures/ptt/`

**Steps:**

1. Add fixture tests for index parsing.
2. Add fixture tests for post parsing and push comments.
3. Implement parser functions independent of network.
4. Add live probe with timeout and `over18=1` cookie.
5. Add examples to `agent_reach/skill/references/taiwan-social.md`.

**Verification:**

- PTT parser tests pass.
- Live probe returns ready/partial with useful message.

**Commit:**

```bash
git add agent_reach/channels/ptt.py tests/test_ptt_channel.py tests/fixtures/ptt agent_reach/skill/references/taiwan-social.md
git commit -m "feat: add PTT reading channel"
```

---

### Task 4: Implement Taiwan news RSS channel

**Objective:** Provide stable Taiwan news/RSS monitoring.

**Files:**

- `agent_reach/channels/taiwan_news.py`
- `tests/test_taiwan_news_channel.py`
- Config defaults file if project has one

**Steps:**

1. Add configurable RSS source list.
2. Parse feeds with `feedparser`.
3. Normalize fields.
4. Probe each source independently.
5. Do not fail the whole channel if one feed fails.

**Verification:**

- Fixture/feed tests pass.
- Doctor shows count of reachable feeds.

**Commit:**

```bash
git add agent_reach/channels/taiwan_news.py tests/test_taiwan_news_channel.py
git commit -m "feat: add Taiwan news RSS channel"
```

---

### Task 5: Implement Taiwan ecommerce v0.1

**Objective:** Support price lookup/read for PChome and momo where feasible.

**Files:**

- `agent_reach/channels/taiwan_ecommerce.py`
- `tests/test_taiwan_ecommerce_channel.py`
- fixtures under `tests/fixtures/ecommerce/`
- `agent_reach/skill/references/taiwan-commerce.md`

**Steps:**

1. Implement shared normalized product schema.
2. Add fixture tests for PChome parser.
3. Add fixture tests for momo parser.
4. Implement live probe with short timeout.
5. Return `partial` if one platform works and another fails.
6. Document rate limits and no anti-bot bypass policy.

**Verification:**

- Product parser tests pass.
- Doctor shows per-platform readiness.

**Commit:**

```bash
git add agent_reach/channels/taiwan_ecommerce.py tests/test_taiwan_ecommerce_channel.py tests/fixtures/ecommerce agent_reach/skill/references/taiwan-commerce.md
git commit -m "feat: add Taiwan ecommerce price channel"
```

---

### Task 6: Implement Dcard and Bahamut as public-read channels

**Objective:** Add social/community sources with graceful degradation.

**Files:**

- `agent_reach/channels/dcard.py`
- `agent_reach/channels/bahamut.py`
- `tests/test_dcard_channel.py`
- `tests/test_bahamut_channel.py`

**Steps:**

1. Write parsers against fixtures first.
2. Add URL reading helpers.
3. Add search fallback guidance using web search if native search is unstable.
4. Probe live endpoints but avoid hard failure.

**Verification:**

- Tests pass.
- Doctor marks each channel ready/partial/blocked accurately.

**Commit:**

```bash
git add agent_reach/channels/dcard.py agent_reach/channels/bahamut.py tests/test_dcard_channel.py tests/test_bahamut_channel.py tests/fixtures/dcard tests/fixtures/bahamut
git commit -m "feat: add Dcard and Bahamut public-read channels"
```

---

### Task 7: Implement gov_tw helper channel

**Objective:** Provide verified public-data helpers without inventing endpoints.

**Files:**

- `agent_reach/channels/gov_tw.py`
- `tests/test_gov_tw_channel.py`
- `agent_reach/skill/references/taiwan-public-data.md`

**Steps:**

1. Verify current government/public-data endpoints manually.
2. Implement only endpoints that are confirmed reachable.
3. For uncertain sources, provide search/link helpers instead of fake API calls.
4. Add tests around URL construction and response normalization.

**Verification:**

- Tests pass.
- Documentation clearly marks confirmed vs helper-only sources.

**Commit:**

```bash
git add agent_reach/channels/gov_tw.py tests/test_gov_tw_channel.py agent_reach/skill/references/taiwan-public-data.md
git commit -m "feat: add Taiwan public data helper channel"
```

---

### Task 8: Add Taiwan install groups and docs

**Objective:** Make Taiwan channels discoverable and easy to install.

**Files:**

- `agent_reach/cli.py`
- `agent_reach/config.py`
- `docs/taiwan-platforms.md`
- `agent_reach/guides/setup-taiwan.md`
- `README.md` or docs README

**Steps:**

1. Add `tw`, `tw-social`, `tw-commerce` channel groups.
2. Add examples to docs.
3. Add setup guide explaining desktop vs server behavior.
4. Add security note: use read-only, avoid main accounts for browser-session platforms.

**Verification:**

- `agent-reach install --env=auto --channels=tw --dry-run` lists expected channels.
- Docs mention limitations clearly.

**Commit:**

```bash
git add agent_reach/cli.py agent_reach/config.py docs/taiwan-platforms.md agent_reach/guides/setup-taiwan.md README.md
git commit -m "docs: add Taiwan install groups and setup guide"
```

---

## 9. Testing Strategy

### Required tests

- Unit parser tests using fixtures.
- Channel registry tests.
- Doctor output tests.
- Probe result shape tests.
- Network tests should be optional and skipped by default unless `RUN_LIVE_TESTS=1`.

### Commands

```bash
pytest -q
RUN_LIVE_TESTS=1 pytest tests/test_ptt_channel.py tests/test_taiwan_ecommerce_channel.py -q
python -m agent_reach.cli doctor
```

### Live test policy

Live tests must:

- Use short timeouts.
- Avoid high request volume.
- Never require login for v0.1.
- Skip gracefully if blocked.

---

## 10. Data & Safety Policy

### Read-only by default

All Taiwan channels are read-only unless explicitly approved in a future spec.

### No bypass policy

Do not implement:

- CAPTCHA solving
- Anti-bot bypass
- Private group scraping
- Login automation for personal accounts
- Posting/commenting/liking

### Rate limits

Default to conservative delays when batching:

- 1–3 seconds between requests for social/community sites
- Stop on 403/429 and report degraded status

### Privacy

- Do not store cookies in repo.
- If cookies are later supported, store only under `~/.agent-reach/`.
- Recommend secondary accounts for browser-session integrations.

---

## 11. Acceptance Criteria for v0.1

v0.1 is complete when:

- `agent-reach doctor` shows Taiwan channels without crashing.
- PTT channel can parse fixture and at least probe public board access.
- Taiwan news RSS can read at least 3 configured public feeds or report partial status.
- Taiwan ecommerce normalizes at least one PChome or momo product/search fixture.
- Dcard/Bahamut either read public URLs or clearly degrade to search/Jina fallback.
- Gov TW docs distinguish confirmed APIs from helper-only links.
- `pytest -q` passes.
- `docs/README_zh-TW.md` explains how to use the Taiwan version.
- No secrets, cookies, cache files, pycache, SQLite DBs, or `.env` are committed.

---

## 12. Recommended `.gitignore` additions

Ensure the repo ignores:

```gitignore
.env
.env.*
*.sqlite
*.sqlite3
*.db
__pycache__/
.pytest_cache/
.ruff_cache/
.mypy_cache/
.agent-reach/
playwright-report/
test-results/
*.log
cookies*.txt
secrets*.json
```

---

## 13. Suggested Codex / Antigravity Prompt

Use this prompt locally:

```text
You are implementing Agent Reach Taiwan Edition.

Start by cloning/forking https://github.com/Panniantong/Agent-Reach.
Read docs/SPEC_TW.md fully before editing.
Do not rewrite from scratch. Preserve the upstream channel/doctor/install architecture.
Implement v0.1 only: PTT, Dcard, Bahamut, Taiwan News, Taiwan Ecommerce, Gov TW.
Use fixture-first tests. Live network tests must be optional and skipped unless RUN_LIVE_TESTS=1.
Do not add login, posting, CAPTCHA bypass, or private-content scraping.
Keep all integrations read-only.
Before first commit, update .gitignore to exclude env, cookies, sqlite/db, cache, pycache, logs, and secrets.
Run pytest -q after each task and commit only passing or clearly documented partial work.
```

---

## 14. Implementation Notes / Tradeoffs

- PTT is high-value and relatively feasible, so it should be first.
- Dcard and Threads are important for Taiwan but may be unstable; degrade gracefully.
- Facebook/Instagram matter commercially, but should be desktop/OpenCLI optional, not server MVP.
- Ecommerce is high business value but likely brittle; use normalized schema and per-platform partial status.
- Government data should prioritize verified sources over fake convenience APIs.
- The fork should stay close enough to upstream that future Agent Reach improvements can be merged.
