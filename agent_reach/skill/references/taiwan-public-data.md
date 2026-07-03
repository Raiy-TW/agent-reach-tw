# 台灣公開資料

Gov TW channel 用於台灣政府開放資料、公司 / 商工資料查詢輔助。v0.1 只提供已驗證官方頁面的 link helper；沒有確認穩定 API 前，不實作 API caller。

## 使用前檢查

```bash
agent-reach doctor --json
```

查看 `gov_tw` status。`ok` 代表 `data.gov.tw` 搜尋頁可連；`warn` 代表仍可輸出官方查詢連結，但 live probe 失敗或被阻擋。

## Python 使用方式

```python
from agent_reach.channels.gov_tw import GovTWChannel

channel = GovTWChannel()
links = channel.search_links("公司 登記")
```

每筆 link 會包含：

- `platform`: 固定為 `gov_tw`
- `source`: 官方來源 host
- `kind`: 查詢類型
- `query`: agent 原始查詢字串
- `url`: 官方查詢連結
- `status`: `confirmed_link` 或 `helper_only`

## 2026-07-02 已驗證連結

- `https://data.gov.tw/`：HTTP 200。
- `https://data.gov.tw/datasets/search?qs=公司`：HTTP 200。實作為 `confirmed_link`。

## Helper-only 連結

- `https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do`
  - 官方商工登記查詢頁。
  - 2026-07-02 以 `curl -I -L` 與一般 User-Agent 測試皆回 Cloudflare 403 challenge。
  - 因此 v0.1 只輸出官方查詢頁，不宣稱可由 agent 直接抓取結果。

## Confirmed APIs

目前沒有加入 confirmed API caller。若之後要加入政府資料 API，必須先補 fixture-first 測試、live endpoint 驗證與錯誤降級行為。

## 實作原則

- 只使用目前已驗證可達的公開 endpoint。
- 不確定的來源只輸出官方查詢連結與搜尋建議。
- 公司查詢可用統一編號或公司名稱，但必須標明資料來源。
- 不把政府資料 cache 進 repo；如需 cache，只能放在 `~/.agent-reach/`。
