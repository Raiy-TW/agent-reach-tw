# Agent Reach Taiwan Edition

Agent Reach Taiwan Edition 是 Agent Reach 的台灣平台能力層。它提供通用 CLI + Python package，讓 AI agent 可以讀取台灣在地公開資訊來源，而不是綁定單一 agent runtime。

這個 fork 以公開、唯讀、可降級為原則，讓 Claude Code、Codex、Cursor，以及任何 agent runtime 都能透過 shell command 或 Python package 使用。

## 定位

- 專案形態：通用 CLI + Python package。
- 使用者：Claude Code、Codex、Cursor，以及其他 AI agent。
- 部署目標：可安裝在本機，也可安裝到 generic Linux server 環境。
- 授權：沿用上游 MIT License，保留原作者 copyright notice。
- 上游專案：[Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach)。

## v0.1 Taiwan Channels

`tw` channel group 目前包含：

- `ptt`：PTT 看板 index / 文章 / 推噓留言 parser。
- `dcard`：公開文字 / Jina-style fallback parser，遇到 403 時清楚降級。
- `bahamut`：巴哈姆特討論串列表、文章與回覆 parser。
- `taiwan_news`：台灣新聞 RSS normalizer，支援 per-source partial failure。
- `taiwan_ecommerce`：PChome / momo 商品頁 parser 與 TWD 價格正規化。
- `gov_tw`：`data.gov.tw` 搜尋 helper 與商工登記官方查詢頁 helper-only link。

所有 channel 預設唯讀。v0.1 不做發文、留言、按讚、登入自動化、CAPTCHA 繞過、私人社群抓取或 anti-bot bypass。

## 快速檢查

```bash
agent-reach doctor --json
```

`doctor` 會列出目前機器上的 channel 狀態。台灣站台若遇到 DNS、403、429、Cloudflare 或 RSS 暫時失敗，channel 應回報 `warn` / partial / fallback，不應 crash。

## Server 安裝 Dry Run

```bash
agent-reach install --env=server --channels=tw --dry-run
```

確認 dry-run OK 後再安裝：

```bash
agent-reach install --env=server --channels=tw
agent-reach doctor --json
```

Server / OCI 環境應優先使用不需要桌面瀏覽器與個人登入態的 channel。需要桌面 Chrome session 的平台只能視為 optional capability。

## Python 使用範例

```python
from agent_reach.channels import get_channel

channel = get_channel("taiwan_news")
status, message = channel.check()
```

## 文件

- 台灣版說明：[docs/README_zh-TW.md](docs/README_zh-TW.md)
- Server / Claude Code / Codex / generic agent runtime 安裝路徑：[docs/server-agent-install.md](docs/server-agent-install.md)
- 實作計畫與驗證紀錄：[docs/IMPLEMENTATION_PLAN_TW.md](docs/IMPLEMENTATION_PLAN_TW.md)
- 原始規格：[docs/SPEC_TW.md](docs/SPEC_TW.md)

## Repo 操作建議

本 fork 建議保留兩個 remote：

```bash
origin   <your-fork-url>
upstream https://github.com/Panniantong/Agent-Reach.git
```

`upstream` 只用來 fetch 原作者更新，不建議直接 push。部署到 server 時建議使用 tag，例如：

```bash
v0.1.0-tw.1
```

## 授權

本專案沿用 MIT License。MIT 允許使用、修改、發佈與商用，但需要保留原始 license 與 copyright notice。
