# Agent Reach Taiwan Edition

Agent Reach Taiwan Edition 是 Agent Reach 的台灣平台能力層。目標是讓 AI agent 用同一套 CLI / Python library 讀取台灣在地公開資訊來源，而不是綁定單一 agent runtime。

## 定位

- 核心形態：通用 CLI + Python package。
- 使用者：generic agent runtime、Claude Code、Codex、Cursor，以及任何能呼叫 shell command 或 Python package 的 agent。
- 主要能力：PTT、Dcard、巴哈姆特、台灣新聞 RSS、台灣電商價格、政府開放資料與商工登記查詢輔助。

## v0.1 範圍

- `ptt`
- `dcard`
- `bahamut`
- `taiwan_news`
- `taiwan_ecommerce`
- `gov_tw`

所有 channel 預設唯讀。v0.1 不做發文、留言、按讚、追蹤、登入自動化、CAPTCHA 繞過、私人社群抓取或 stealth anti-bot evasion。

## Agent 使用方式

先用 doctor 確認目前機器可用能力：

```bash
agent-reach doctor
```

Server 環境，例如 OCI 上的 generic agent runtime，應優先使用不需要桌面瀏覽器與個人登入的 channel。需要桌面 Chrome session 的平台應標記為 optional，而不是遠端部署必備能力。

Server 安裝與遠端 agent 接入請看 `docs/server-agent-install.md`。這份 guide 涵蓋 Claude Code、Codex 與其他 generic agent runtime；特定私有部署名稱不應寫進公開文件。

## 開發狀態

目前已加入 v0.1 台灣 channel scaffold，並已實作：

- PTT board index / post parser、over18 public HTTP probe。
- Taiwan News RSS normalizer、預設 3 個已驗證 feed、per-source partial failure。
- Bahamut topic list / post / replies parser、public HTTP probe。
- Dcard Jina-style public text parser、403/blocked graceful fallback。
- Gov TW `data.gov.tw` 搜尋 helper、商工登記官方查詢頁 helper-only fallback。
- Taiwan Ecommerce PChome / momo 商品頁 parser、TWD 價格正規化、per-platform partial probe。

v0.1 的剩餘工作請依 `docs/IMPLEMENTATION_PLAN_TW.md` 的 Phase 7 驗證與交接清單追蹤。
