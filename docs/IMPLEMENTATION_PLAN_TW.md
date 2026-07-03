# Agent Reach Taiwan Edition 實作計畫

> **給 agentic workers：** 實作本計畫時，若環境有 subagent，必須使用 `superpowers:subagent-driven-development`；否則使用 `superpowers:executing-plans`。所有步驟用 checkbox（`- [ ]`）追蹤。

**目標：** 建出 v0.1 Taiwan Edition channels，作為通用 CLI / Python capability layer，讓 generic agent runtime、Claude Code、Codex、Cursor 與其他 AI agent 都能使用。

**架構：** 保留 upstream Agent Reach 作為基底。台灣 channels 以一般 `agent_reach.channels` module 形式加入，註冊到既有 channel registry，透過 `agent-reach doctor` 顯示健康狀態，並沿用既有 skill/reference 文件模式說明用法。parser 一律 fixture-first；live probe 是輔助驗證；平台阻擋或 endpoint 變動時必須 graceful degradation。

**技術棧：** Python 3.10+、pytest、urllib/requests 或必要時 httpx、BeautifulSoup 做 HTML parsing、feedparser 做 RSS、只有在 public HTTP 無法可靠讀取時才使用 Playwright。

---

## 目前 Checkpoint

分支：`feature/taiwan-edition-mvp`

已完成：

- [x] 從 upstream Agent Reach clone/fork 到 `agent-reach-tw/`。
- [x] 加入 `docs/SPEC_TW.md`。
- [x] 加入 Taiwan v0.1 channel scaffold：`ptt`、`dcard`、`bahamut`、`taiwan_news`、`taiwan_ecommerce`、`gov_tw`。
- [x] 加入 install channel groups：`tw`、`tw-social`、`tw-commerce`。
- [x] 加入 Taiwan skill references 與 setup docs。
- [x] 實作 PTT board index / post fixture parsers 與 degraded `check()`。
- [x] 實作 Taiwan News RSS normalization 與 per-source partial failure。
- [x] 實作 Bahamut topic list / post / replies parser 與 public HTTP probe。
- [x] 實作 Dcard Jina-style public text parser 與 direct HTTP/API blocked fallback。

這份 plan 建立前的最新驗證狀態：

- 使用 workspace-local `HOME` 跑 `pytest -q`：`209 passed`。
- 新增 Taiwan files 的 targeted ruff：通過。
- `agent-reach doctor --json`：Taiwan channels 可正常輸出；網路失敗時降級為 `warn`，不會 crash。

已知剩餘缺口：

- 全量 `ruff check .` 仍會報 upstream 既有 lint 問題，範圍在 Taiwan work 之外。不要把無關 cleanup 混進 Taiwan channel commits。

---

## Phase 0：Baseline 與安全邊界

狀態：已完成。

**檔案：**

- 新增：`docs/SPEC_TW.md`
- 修改：`.gitignore`

- [x] Clone upstream Agent Reach 到 `agent-reach-tw/`。
- [x] 建立分支 `feature/taiwan-edition-mvp`。
- [x] 使用 workspace-local home 跑 baseline tests：

```bash
env HOME=<repo>/.test-home .venv/bin/python -m pytest -q
```

- [x] 加入 ignore rules：`.venv/`、`.test-home/`、`.env.*`、cookies、secrets、SQLite DBs、pycache、logs、Playwright output。

Checkpoint commit：

```bash
git add .gitignore docs/SPEC_TW.md
git commit -m "docs: add Taiwan edition spec"
```

---

## Phase 1：Taiwan Channel Registry 與 Agent Discovery

狀態：已完成。

**檔案：**

- 新增：`agent_reach/channels/ptt.py`
- 新增：`agent_reach/channels/dcard.py`
- 新增：`agent_reach/channels/bahamut.py`
- 新增：`agent_reach/channels/taiwan_news.py`
- 新增：`agent_reach/channels/taiwan_ecommerce.py`
- 新增：`agent_reach/channels/gov_tw.py`
- 修改：`agent_reach/channels/__init__.py`
- 修改：`agent_reach/cli.py`
- 修改：`agent_reach/skill/SKILL.md`
- 修改：`agent_reach/skill/SKILL_en.md`
- 新增：`agent_reach/skill/references/taiwan-social.md`
- 新增：`agent_reach/skill/references/taiwan-commerce.md`
- 新增：`agent_reach/skill/references/taiwan-public-data.md`
- 新增：`agent_reach/guides/setup-taiwan.md`
- 新增：`docs/README_zh-TW.md`
- 測試：`tests/test_taiwan_channel_scaffolding.py`
- 測試：`tests/test_cli.py`

- [x] 先寫失敗的 registry tests，檢查六個 v0.1 channel names。
- [x] 實作最小 channel classes，包含 `can_handle()` 與 degraded `check()`。
- [x] 先寫 `--channels=tw` 的失敗 CLI test。
- [x] 實作 `tw`、`tw-social`、`tw-commerce` group expansion。
- [x] 文件說明 generic agent usage；generic runtime 只是其中一個 consumer，不是專案本體形狀。

驗證：

```bash
env HOME=<repo>/.test-home .venv/bin/python -m pytest tests/test_taiwan_channel_scaffolding.py tests/test_cli.py::TestCLI::test_install_dry_run_expands_taiwan_channel_group -q
env HOME=<repo>/.test-home .venv/bin/agent-reach install --env=server --channels=tw --dry-run
```

Checkpoint commit：

```bash
git add agent_reach/channels agent_reach/cli.py agent_reach/skill docs tests/test_taiwan_channel_scaffolding.py tests/test_cli.py
git commit -m "feat: register Taiwan channel scaffolding"
```

---

## Phase 2：穩定、適合 Server 的 Channels

狀態：已完成。

### Task 2.1：PTT

**檔案：**

- 修改：`agent_reach/channels/ptt.py`
- 新增：`tests/test_ptt_channel.py`
- 新增：`tests/fixtures/ptt/index_pc_shopping.html`
- 新增：`tests/fixtures/ptt/post_with_pushes.html`
- 修改：`agent_reach/skill/references/taiwan-social.md`

- [x] 先寫 board index parsing 的 fixture test。
- [x] 跑測試並確認 RED。
- [x] 實作 `parse_board_index()`。
- [x] 跑測試並確認 GREEN。
- [x] 先寫 post metadata / content / push parsing 的 fixture test。
- [x] 跑測試並確認 RED。
- [x] 實作 `parse_post()`。
- [x] 跑測試並確認 GREEN。
- [x] 先寫 `check()` 成功與網路阻擋 warning 的 probe tests。
- [x] 實作帶 `over18=1` cookie 的 public HTTP probe。
- [x] 在 Taiwan social reference 補 Python 使用方式。

驗證：

```bash
env HOME=<repo>/.test-home .venv/bin/python -m pytest tests/test_ptt_channel.py -q
```

### Task 2.2：Taiwan News RSS

**檔案：**

- 修改：`agent_reach/channels/taiwan_news.py`
- 新增：`tests/test_taiwan_news_channel.py`
- 修改：`docs/README_zh-TW.md`
- 修改：`pyproject.toml`

- [x] 加入 default feeds 前，先手動驗證候選 RSS。
- [x] 先寫失敗的 normalization tests。
- [x] 實作 `normalize_feed_entries()`。
- [x] 先寫 partial failure test。
- [x] 實作 `read_sources()`。
- [x] 先寫 `check()` feed-count test。
- [x] 實作 per-source probe summary。

2026-07-02 以 `curl -I -L` 驗證過的 default feeds：

- `https://technews.tw/feed/`
- `https://www.inside.com.tw/feed/rss`
- `https://news.pts.org.tw/xml/newsfeed.xml`

暫不放入 default list，等重新驗證後再加入：

- `https://www.cna.com.tw/rss/aall.xml` 回傳 `404`。
- `https://www.bnext.com.tw/feed`、`/rss`、`/feed/rss` 回傳 `404`。

驗證：

```bash
env HOME=<repo>/.test-home .venv/bin/python -m pytest tests/test_ptt_channel.py tests/test_taiwan_news_channel.py -q
```

Checkpoint commit：

```bash
git add agent_reach/channels/ptt.py agent_reach/channels/taiwan_news.py tests/test_ptt_channel.py tests/test_taiwan_news_channel.py tests/fixtures/ptt agent_reach/skill/references/taiwan-social.md docs/README_zh-TW.md pyproject.toml
git commit -m "feat: add PTT and Taiwan news channels"
```

---

## Phase 3：公開社群 Read Channels

狀態：已完成。

### Task 3.1：Bahamut Public Read

**檔案：**

- 修改：`agent_reach/channels/bahamut.py`
- 新增：`tests/test_bahamut_channel.py`
- 新增：`tests/fixtures/bahamut/topic_list.html`
- 新增：`tests/fixtures/bahamut/post.html`
- 修改：`agent_reach/skill/references/taiwan-social.md`

- [x] 先寫 topic list parsing 的 fixture test。
- [x] 跑測試並確認 RED。
- [x] 實作 `parse_topic_list(html, board_url)`。
- [x] 跑測試並確認 GREEN。
- [x] 先寫 post / reply parsing 的 fixture test。
- [x] 跑測試並確認 RED。
- [x] 實作 `parse_post(html, url)`。
- [x] 加入 `check()`：用短 timeout probe 一個公開頁，若被擋則回傳 `warn`。
- [x] 文件補 Jina Reader 與 `site:forum.gamer.com.tw` fallback。

驗證：

```bash
env HOME=<repo>/.test-home .venv/bin/python -m pytest tests/test_bahamut_channel.py tests/test_taiwan_channel_scaffolding.py -q
```

### Task 3.2：Dcard Public Read

**檔案：**

- 修改：`agent_reach/channels/dcard.py`
- 新增：`tests/test_dcard_channel.py`
- 新增：`tests/fixtures/dcard/post.html`
- 新增：`tests/fixtures/dcard/forum_posts.json`，只有在確認 public endpoint 後才建立。
- 修改：`agent_reach/skill/references/taiwan-social.md`

- [x] 寫入任何 API URL 前，先驗證目前 Dcard public endpoint。
- [x] 若沒有確認穩定 endpoint，只針對 public URL / Jina-style HTML normalization 寫測試。
- [x] 先寫 post extraction fixture test。
- [x] 跑測試並確認 RED。
- [x] 實作 parser。
- [x] 加入 `check()` states：依 upstream status strings 能力回傳 `ok`、`warn`，或訊息標示 `blocked/needs_browser`。
- [x] 文件寫清楚 v0.1 不使用 user login。

驗證：

```bash
env HOME=<repo>/.test-home .venv/bin/python -m pytest tests/test_dcard_channel.py tests/test_taiwan_channel_scaffolding.py -q
```

Checkpoint commit：

```bash
git add agent_reach/channels/bahamut.py agent_reach/channels/dcard.py tests/test_bahamut_channel.py tests/test_dcard_channel.py tests/fixtures/bahamut tests/fixtures/dcard agent_reach/skill/references/taiwan-social.md
git commit -m "feat: add Bahamut and Dcard public-read channels"
```

---

## Phase 4：政府公開資料 Helpers

狀態：已完成。

**檔案：**

- 修改：`agent_reach/channels/gov_tw.py`
- 新增：`tests/test_gov_tw_channel.py`
- 修改：`agent_reach/skill/references/taiwan-public-data.md`

- [x] 手動驗證目前可用的政府公開 endpoint。
- [x] 先寫穩定官方連結建構測試。
- [x] 跑測試並確認 RED。
- [x] 實作 `data.gov.tw` search 與商工登記查詢頁的 link helper functions。
- [x] 只有在本 phase 已確認 endpoint 可用時，才加入 API caller。
- [x] 文件標清楚 confirmed APIs 與 helper-only links。

2026-07-02 手動驗證結果：

- `https://data.gov.tw/`：HTTP 200。
- `https://data.gov.tw/datasets/search?qs=公司`：HTTP 200，作為 `confirmed_link`。
- `https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do`：Cloudflare 403 challenge，僅作為 `helper_only` 官方查詢頁。

本 phase 未加入 API caller；目前沒有確認穩定 API endpoint。

驗證：

```bash
env HOME=<repo>/.test-home .venv/bin/python -m pytest tests/test_gov_tw_channel.py tests/test_taiwan_channel_scaffolding.py -q
```

Checkpoint commit：

```bash
git add agent_reach/channels/gov_tw.py tests/test_gov_tw_channel.py agent_reach/skill/references/taiwan-public-data.md
git commit -m "feat: add Taiwan public data helpers"
```

---

## Phase 5：台灣電商價格查詢

狀態：已完成。

**檔案：**

- 修改：`agent_reach/channels/taiwan_ecommerce.py`
- 新增：`tests/test_taiwan_ecommerce_channel.py`
- 新增：`tests/fixtures/ecommerce/pchome_product.html`
- 新增：`tests/fixtures/ecommerce/momo_product.html`
- 修改：`agent_reach/skill/references/taiwan-commerce.md`

- [x] 先寫 normalized product schema tests。
- [x] 跑測試並確認 RED。
- [x] 實作 schema helpers 與 currency normalization。
- [x] 先寫 PChome fixture parser test。
- [x] 跑測試並確認 RED。
- [x] 實作 PChome parser。
- [x] 先寫 momo fixture parser test。
- [x] 跑測試並確認 RED。
- [x] 實作 momo parser。
- [x] 加入 per-platform `check()` summary：所有 enabled probes 都成功才是 `ok`，部分成功為 `warn`。
- [x] 文件補 rate limits 與 no anti-bot bypass。

2026-07-02 手動驗證結果：

- `https://24h.pchome.com.tw/prod/DYAJ4B-A900H9N4K`：HTTP 200。
- `https://24h.pchome.com.tw/`：redirect loop 後回 429，因此 `check()` 不使用首頁作為 PChome probe。
- `https://www.momoshop.com.tw/`：HTTP 200。

本 phase 不做登入、不使用個人 cookie、不繞過 CAPTCHA / anti-bot。

驗證：

```bash
env HOME=<repo>/.test-home .venv/bin/python -m pytest tests/test_taiwan_ecommerce_channel.py tests/test_taiwan_channel_scaffolding.py -q
```

Checkpoint commit：

```bash
git add agent_reach/channels/taiwan_ecommerce.py tests/test_taiwan_ecommerce_channel.py tests/fixtures/ecommerce agent_reach/skill/references/taiwan-commerce.md
git commit -m "feat: add Taiwan ecommerce price channel"
```

---

## Phase 6：Agent Runtime Packaging 與 server 安裝路徑

狀態：已完成。

**檔案：**

- 修改：`agent_reach/guides/setup-taiwan.md`
- 新增：`docs/server-agent-install.md`
- 修改：`docs/README_zh-TW.md`

- [x] 撰寫 generic server install guide。
- [x] 先保持 guide generic：venv/pipx install、`agent-reach doctor --json`、不把 desktop-only channels 當必要條件。
- [x] Runtime-specific notes 只作為其中一條 consumer path。
- [x] 補 Claude Code / Codex 透過 CLI 與 skill references 使用的說明。
- [x] 可行時以 dry-run / local form 驗證安裝指令。

驗證：

```bash
env HOME=<repo>/.test-home .venv/bin/agent-reach install --env=server --channels=tw --dry-run
env HOME=<repo>/.test-home .venv/bin/agent-reach doctor --json
```

Checkpoint commit：

```bash
git add agent_reach/guides/setup-taiwan.md docs/server-agent-install.md docs/README_zh-TW.md
git commit -m "docs: add Taiwan server agent setup guide"
```

---

## Phase 7：最終驗證、Review 與交接

狀態：已完成。

- [x] 跑每個 Taiwan channel 的 targeted tests。
- [x] 跑完整 test suite。
- [x] 對 Taiwan files 跑 targeted ruff。
- [x] 跑 `agent-reach doctor --json`。
- [x] 檢查 git diff，確認沒有誤加入 secrets、cookies、cache files、SQLite DBs、`.env`、pycache，或無關 upstream cleanup。
- [x] 依 logical units commit 剩餘變更。
- [x] 準備 `generic server` deployment instructions。

收尾驗證記錄：

- Taiwan targeted tests：`35 passed`。
- Full pytest：`232 passed`。
- Taiwan targeted ruff：`All checks passed`。
- `agent-reach doctor --json`：可正常輸出 Taiwan channels；本機 DNS 失敗時各 channel 降級為 `warn`，沒有 crash。
- Secrets/cache 掃描：本次 Taiwan 檔案未命中 key/token/cookie；`.venv/`、`.test-home/`、cache、pycache 均為 ignored。

最終驗證：

```bash
env HOME=<repo>/.test-home .venv/bin/python -m pytest -q
.venv/bin/ruff check agent_reach/channels/ptt.py agent_reach/channels/dcard.py agent_reach/channels/bahamut.py agent_reach/channels/taiwan_news.py agent_reach/channels/taiwan_ecommerce.py agent_reach/channels/gov_tw.py tests/test_ptt_channel.py tests/test_dcard_channel.py tests/test_bahamut_channel.py tests/test_taiwan_news_channel.py tests/test_taiwan_ecommerce_channel.py tests/test_gov_tw_channel.py
env HOME=<repo>/.test-home .venv/bin/agent-reach doctor --json
git status --short
```

除非 `docs/SPEC_TW.md` 第 11 節的每一條 acceptance criterion 都已用 code、tests、docs 核對，否則不能宣稱 v0.1 完成。
