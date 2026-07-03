# 台灣社群

PTT、Dcard、巴哈姆特。全部以公開、唯讀內容為邊界。

## 使用前檢查

```bash
agent-reach doctor --json
```

讀取 `ptt`、`dcard`、`bahamut` 的 `status` 與 `message`。若 status 不是 `ok`，依照 message 裡的 fallback 處理；不要自行繞過 CAPTCHA、登入牆或私人內容限制。

## PTT

目前可用能力：

- 讀取看板 index。
- 讀取文章正文。
- 解析標題、作者、日期、正文、推文、URL。
- 支援 `Gossiping`、`Stock`、`Tech_Job`、`PC_Shopping`、`e-shopping` 等常用看板。

Python 使用方式：

```python
from agent_reach.channels.ptt import PTTChannel

ptt = PTTChannel()
posts = ptt.read_board_index("PC_Shopping")
post = ptt.read_post("PC_Shopping", posts[0]["url"])
```

輸出欄位：

- board index: `platform`, `board`, `title`, `author`, `date`, `push_count`, `url`
- post: `platform`, `board`, `title`, `author`, `published_at`, `content`, `comments`, `url`

後端順序：

1. `https://www.ptt.cc/bbs/{board}/index.html`
2. age gate 出現時使用 `over18=1` cookie。
3. 必要時才使用公開 mirror 或 Jina Reader fallback，並標明來源。

## Dcard

目前可用能力：

- direct public HTTP/API 目前容易回 403。
- 提供 Jina-style public text parser，可把公開文章文字整理成穩定 shape。
- `doctor` 會明確回報 fallback 狀態，不假裝 server 端可直接抓 Dcard。

Python 使用方式：

```python
from agent_reach.channels.dcard import DcardChannel

dcard = DcardChannel()
post = dcard.parse_public_text(markdown_text, "https://www.dcard.tw/f/tech/p/256789123")
```

輸出欄位：

- post: `platform`, `forum`, `post_id`, `title`, `content`, `comments`, `url`

限制：

- v0.1 不使用使用者登入。
- Dcard endpoint 變動頻繁；寫入任何 API URL 前都要重新驗證。
- Server 環境若 direct public access 被擋，應改走 Jina Reader、browser-rendered public page，或回報 `needs_browser`。

## 巴哈姆特

目前可用能力：

- 讀取公開看板主題列表。
- 讀取公開文章正文。
- 解析回覆留言。
- native search 不穩定時，改用 `site:forum.gamer.com.tw keyword` 搜尋 fallback。

Python 使用方式：

```python
from agent_reach.channels.bahamut import BahamutChannel

bahamut = BahamutChannel()
topics = bahamut.read_topic_list("60030")
post = bahamut.read_post(topics[0]["url"])
```

輸出欄位：

- topic list: `platform`, `board`, `subboard`, `title`, `excerpt`, `author`, `reply_count`, `gp_count`, `interaction_count`, `view_count`, `last_reply_at`, `url`
- post: `platform`, `board`, `title`, `author`, `author_id`, `published_at`, `category`, `content`, `replies`, `url`

後端順序：

1. public HTTP 讀取 `https://forum.gamer.com.tw/B.php?bsn={board}`。
2. 文章頁 public HTTP 讀取 `C.php` URL。
3. 被擋時保留 Jina Reader / web search fallback。

## 安全邊界

- 不發文、不留言、不按讚。
- 不抓私人社團、付費內容或登入牆後的內容。
- 403/429 時停止並回報 degraded status。
- 批次請求預設間隔 1-3 秒。
