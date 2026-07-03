---
name: agent-reach-tw
description: Use when the user needs public Taiwan web data, PTT, Dcard, Bahamut, Taiwan news RSS, PChome/momo/Yahoo prices, data.gov.tw, company lookup links, or Agent Reach Taiwan Edition availability checks.
---

# Agent Reach Taiwan Edition Skill

台灣版 Agent Reach 的通用 AI agent skill。用途是讓 agent 讀取與搜尋台灣公開網路資料；不是登入態爬蟲、寫入工具、或 anti-bot bypass。

## 使用時機

使用者需要查：

- 台灣社群：PTT、Dcard、巴哈姆特
- 台灣新聞：RSS / 公開新聞來源
- 台灣電商：PChome、momo、Yahoo Shopping 商品頁與 TWD 價格
- 台灣政府資料：data.gov.tw、商工登記官方查詢入口
- 檢查或安裝 Agent Reach Taiwan Edition

不要用於：

- 發文、留言、按讚、私訊等寫入操作
- 登入態自動化或私人社群抓取
- CAPTCHA / anti-bot / Cloudflare bypass
- 假裝能直接抓到被 403/429 擋住的內容
- 已有更專門 skill 的平台任務（先用專門 skill）

## 開始前：先做健康檢查

正式查資料前先跑：

```bash
agent-reach doctor --json
```

依照 `status` 與 `active_backend` 選擇路徑，不要猜。

## 核心原則

1. **先 doctor，再選路徑**：不要假設 channel 現在可用。
2. **公開唯讀**：只讀公開頁面、RSS、官方查詢連結。
3. **可降級**：遇到 403/429/DNS/Cloudflare 時回報 warn 與 fallback，不要說「查無」或硬編結果。
4. **不要自己發明命令**：依 CLI、Python channel、或 references 文件走。
5. **報告限制**：清楚標示哪些是直接讀到，哪些只是 helper link / fallback。

## 快速命令

```bash
# 健康檢查
agent-reach doctor --json

# server 安裝 dry-run（不改系統）
agent-reach install --env=server --channels=tw --dry-run

# 版本
agent-reach version
```

## Python 快速用法

```python
from agent_reach.channels import get_channel

news = get_channel("taiwan_news")
result = news.read_sources(limit_per_source=3)

public_data = get_channel("gov_tw")
links = public_data.search_links("公司登記")
```

## Channel 狀態判讀

- `ok`：可直接用目前 backend。
- `warn`：可能被 403/Cloudflare/DNS/站台限制擋住；使用 fallback 或只回報官方連結。
- `off` / `error`：不要硬抓，先回報缺依賴或不可用原因。

## 已知台灣 channel

- `ptt`：PTT 看板 index / 文章 / 推噓留言 parser。
- `dcard`：公開文字 / Jina-style fallback parser；遇到 403 時清楚降級。
- `bahamut`：巴哈姆特討論串列表、文章與回覆 parser；可能需要 fallback。
- `taiwan_news`：台灣新聞 RSS normalizer，支援 per-source partial failure。
- `taiwan_ecommerce`：PChome / momo / Yahoo Shopping 商品頁 parser 與 TWD 價格正規化。
- `gov_tw`：`data.gov.tw` 搜尋 helper 與商工登記官方查詢頁 helper-only link。

## 路由表

| 使用者意圖 | 分類 | 詳細文件 |
| --- | --- | --- |
| PTT / Dcard / 巴哈姆特 | taiwan-social | [references/taiwan-social.md](references/taiwan-social.md) |
| PChome / momo / Yahoo Shopping 價格 | taiwan-commerce | [references/taiwan-commerce.md](references/taiwan-commerce.md) |
| data.gov.tw / 商工登記 / 公司資料 | taiwan-public-data | [references/taiwan-public-data.md](references/taiwan-public-data.md) |
| 一般網頁 / RSS / Jina fallback | web | [references/web.md](references/web.md) |
| 搜尋 fallback | search | [references/search.md](references/search.md) |

## 常見任務範例

### 台灣新聞 RSS

```python
from agent_reach.channels import get_channel

channel = get_channel("taiwan_news")
result = channel.read_sources(limit_per_source=5)
```

### 政府公開資料 / 公司查詢入口

```python
from agent_reach.channels import get_channel

channel = get_channel("gov_tw")
links = channel.search_links("公司登記")
```

### 台灣電商價格

先用 `agent-reach doctor --json` 確認 `taiwan_ecommerce`，再依 `references/taiwan-commerce.md` 的 parser / fallback 路徑處理。若站台擋 public HTTP，明確回報限制與 fallback，不要編價格。

## 驗證清單

- [ ] 已跑 `agent-reach doctor --json`
- [ ] 已確認 channel status / active_backend
- [ ] 只使用公開唯讀資料
- [ ] 對 403/429/Cloudflare 等限制有明確說明
- [ ] 結果有來源 URL 或官方 helper link
