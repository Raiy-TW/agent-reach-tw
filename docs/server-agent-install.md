# Server Agent 安裝指南

這份文件描述如何把 Agent Reach Taiwan Edition 裝到 generic Linux server，給遠端 agent 使用。專案定位是通用 CLI + Python package，不是任何單一 runtime 專用 tool/plugin；Claude Code、Codex、Cursor，或任何 agent runtime 都應該走同一套能力層。

公開文件不要包含個人機器名稱、私有 host alias、內部服務名稱、絕對本機路徑或私有網路資訊。不要把特定私有部署名稱寫進公開文件。

## 原則

- 部署目標：generic Linux server 或本機開發環境。
- 安裝形態：通用 CLI + Python package。
- 使用者：Claude Code、Codex、Cursor，以及任何能執行 shell command 或 Python 的 agent。
- Server 預設 channel：`tw`。
- v0.1 不需要桌面瀏覽器、不需要個人登入 cookie、不繞過 CAPTCHA / anti-bot。
- 特定 runtime notes 只是一條接入方式，不是專案本體形態。

## Server 安裝流程

SSH 進目標 server 後，在 agent-reach-tw checkout 目錄內安裝。若尚未放上 repo，先用你的部署方式把這個 fork 放到 server。

### pipx

`pipx` 適合讓同一台 server 上的多個 agent 共用 `agent-reach` CLI。

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install /path/to/agent-reach-tw
agent-reach install --env=server --channels=tw --dry-run
agent-reach doctor --json
```

### venv

`venv` 適合綁在特定 checkout 或特定 user service 內。

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
agent-reach install --env=server --channels=tw --dry-run
agent-reach doctor --json
```

## Agent Runtime 接入

Agent runtime 只需要能在同一個 user session 找到 `agent-reach` CLI。建議先在 runtime user 下驗證：

```bash
which agent-reach
agent-reach doctor --json
agent-reach install --env=server --channels=tw --dry-run
```

Runtime 可以把它當 CLI tool 呼叫，也可透過 Python import channel。不要把 API key、`.env`、cookie、browser profile、私有 host alias 或本機 private config 寫進這個 repo。

## Claude Code / Codex 接入

Claude Code 與 Codex 可以直接使用：

```bash
agent-reach doctor --json
agent-reach install --env=server --channels=tw --dry-run
```

Python path 可用：

```python
from agent_reach.channels import get_channel

channel = get_channel("gov_tw")
status, message = channel.check()
```

## Server channel 邊界

`tw` v0.1 預設包含：

- `ptt`
- `dcard`
- `bahamut`
- `taiwan_news`
- `taiwan_ecommerce`
- `gov_tw`

這些 channel 都以公開、唯讀、可降級為原則。需要桌面 Chrome session 的平台應標記為 optional，不要把它們列成 server 必裝條件。

## 驗證

本機或 server 都應該能跑：

```bash
agent-reach install --env=server --channels=tw --dry-run
agent-reach doctor --json
```

`doctor` 看到部分 channel 是 `warn` 不一定代表安裝失敗。台灣站台常見 DNS、Cloudflare、403、429 或 RSS 暫時失敗；channel 應該回報 partial / fallback，而不是 crash。
