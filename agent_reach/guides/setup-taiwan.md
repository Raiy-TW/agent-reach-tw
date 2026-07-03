# Taiwan Edition 安裝指南

Agent Reach Taiwan Edition 是通用 CLI + Python package。它不是特定 runtime 專用 plugin；generic agent runtime、Claude Code、Codex、Cursor，或任何能執行 shell command / Python package 的 agent 都可以使用同一套能力層。

## Server / OCI 環境

Server / OCI 環境建議先裝 `tw` channel group，因為 v0.1 台灣 channels 都以公開、唯讀、可降級為原則設計。桌面瀏覽器登入態不是必要條件；需要桌面 Chrome session 的平台只能當 optional capability。

```bash
agent-reach install --env=server --channels=tw --dry-run
agent-reach install --env=server --channels=tw
agent-reach doctor --json
```

`tw` 會展開為：

- `ptt`
- `dcard`
- `bahamut`
- `taiwan_news`
- `taiwan_ecommerce`
- `gov_tw`

## pipx 安裝

若要讓多個 agent 共用同一個 CLI，優先使用 `pipx`：

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install /path/to/agent-reach-tw
agent-reach install --env=server --channels=tw --dry-run
agent-reach doctor --json
```

## venv 安裝

若要固定在單一專案或單一 agent runtime 內，使用 `venv`：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
agent-reach install --env=server --channels=tw --dry-run
agent-reach doctor --json
```

## generic agent runtime

generic agent runtime 可以把 `agent-reach` 當成外部 CLI 或 Python capability 使用。重點是讓 generic runtime 所在的 user session 找得到 `agent-reach` binary，並先跑：

```bash
agent-reach doctor --json
```

Runtime-specific notes 只是一條 consumer path，不要把 generic runtime 當成唯一 consumer，也不要把 generic runtime 設定檔、API key、cookie 或 `.env` 放進 repo。

## Claude Code / Codex

Claude Code 與 Codex 可以直接要求 shell 執行：

```bash
agent-reach doctor --json
agent-reach install --env=server --channels=tw --dry-run
```

若 agent 使用 Python，可以直接 import channel：

```python
from agent_reach.channels import get_channel

channel = get_channel("taiwan_news")
status, message = channel.check()
```

## 狀態解讀

- `ok`：channel backend 目前可用。
- `warn`：channel 存在，但平台阻擋、網路失敗，或只能 partial 使用。
- `off`：必要本機 dependency 缺失。
- `error`：channel check crash，需要修正。

不要把 cookies、`.env`、browser profiles、SQLite caches，或含私人資料的 downloaded HTML fixtures 放進 repo。
