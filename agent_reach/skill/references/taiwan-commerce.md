# 台灣電商

台灣電商 channel 用於公開價格查詢與競品監控。v0.1 目標平台是 PChome 24h 與 momo；Yahoo Shopping 先保留為候選，不在本版 parser 範圍內。

## 使用前檢查

```bash
agent-reach doctor --json
```

查看 `taiwan_ecommerce` 的 status。若只支援部分平台，doctor message 會標示 partial，不要假裝全部可用。

## Python 使用方式

```python
from agent_reach.channels.taiwan_ecommerce import TaiwanEcommerceChannel

channel = TaiwanEcommerceChannel()
product = channel.read_product("https://24h.pchome.com.tw/prod/DYAJ4B-A900H9N4K")
```

## 輸出資料形狀

```json
{
  "platform": "pchome",
  "title": "...",
  "price": 399,
  "currency": "TWD",
  "stock_status": "unknown",
  "promo": "...",
  "url": "...",
  "fetched_at": "2026-07-02T22:00:00+08:00"
}
```

## 支援平台

- PChome 24h：讀取公開商品頁，優先解析 JSON-LD Product / Offer。
- momo：讀取公開商品頁，解析頁面標題、價格與促銷文字。

## Rate Limits 與安全邊界

- 只讀取公開頁面或公開 endpoint。
- 不繞過 CAPTCHA、Cloudflare challenge 或 anti-bot。
- 不登入使用者帳號，不使用個人 cookie。
- 不做高頻輪詢；應由呼叫端控制速率，建議同平台請求間隔至少數秒。
- 單一平台 blocked 時回報 partial，保留其他平台結果。
- 價格與庫存提示必須附 `fetched_at`，避免 agent 把舊價格當即時價格。
