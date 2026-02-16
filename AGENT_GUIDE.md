# AGENTS.md — Thinker News Agent 指引

> 此檔案供 AI agent（如 OpenClaw）在處理 thinker-news 相關指令時參考。

## 專案概述

Thinker News 是一個 **每日 AI 新聞自動生成系統**，面向台灣科技學習者。

- **核心 pipeline:** `main.py` → `rss_fetcher` → `news_filter` → `ai_processor` → `html_generator`
- **輸出:** 每日 HTML 日報 + `latest.json`（快取最新一期的各格式內容）
- **部署:** GitHub Pages (`thinkercafe-tw.github.io/thinker-news/`)
- **Branch:** 開發用 `refactor/cleanup-v1`，穩定版 `main`

## 目錄結構

```
scripts/           核心程式碼
  main.py          主流程入口
  rss_fetcher.py   RSS 來源抓取
  news_filter.py   篩選 + 評分
  filter_config.py 篩選配置（來源、關鍵字、標籤）
  ai_processor.py  AI 處理鏈（DeepSeek + OpenAI）
  prompts.py       System prompts 集中管理
  html_generator.py HTML 頁面生成（模板渲染）
  get_latest_news.py /news 查詢模組
  line_handler.py  LINE /news 確定性處理（webhook + CLI）
  health_check.py  系統健康檢查
  log_config.py    統一 logging
  utils.py         共用工具
  execution_logger.py 執行紀錄
  notify_slack.py  Slack 通知
  templates/       HTML 模板
    daily_news.html
    index.html
archive/           歷史日報 HTML
latest.json        最新一期日報快取
```

## `/news` 指令處理

當用戶在 LINE 或其他平台發送 `/news` 時：

1. **不要用 AI 重新生成或改寫內容**
2. 直接讀取 `latest.json`
3. 使用 `get_latest_news.py` 的 `format_news_reply()` 回傳

### LINE Webhook 確定性處理

`scripts/line_handler.py` 提供 LINE `/news` 指令的確定性回覆：

- **`/news`** → 直接讀 `latest.json`，原文照發
- **`/help`** → 顯示可用指令
- **其他訊息** → 不回覆（回傳 None）

```bash
# 測試指令
python scripts/line_handler.py --test '/news'

# 啟動 Webhook 伺服器（需 flask）
python scripts/line_handler.py --serve --port 5000
# Webhook endpoint: POST /webhook/line
```

### 程式碼引用

```python
# 簡單取得回覆文字
from scripts.line_handler import handle_command
reply = handle_command("/news")  # 確定性，不經 AI

# 完整 LINE 事件處理
from scripts.line_handler import handle_line_event
handle_line_event(event, access_token)
```

### 底層 API

```python
from scripts.get_latest_news import get_latest_news, format_news_reply

data = get_latest_news("all")
reply = format_news_reply(data)
```

### latest.json 結構

```json
{
  "date": "2026-02-11",
  "line_content": "LINE 精華版（短文字）",
  "notion_content": "Notion 詳細版（長 markdown）",
  "website_url": "https://thinkercafe-tw.github.io/thinker-news/YYYY-MM-DD.html",
  "generated_at": "ISO 時間戳"
}
```

### 格式選擇

| 需求 | 格式參數 | 說明 |
|------|---------|------|
| LINE / Telegram 回覆 | `"reply"` 或用 `format_news_reply()` | 精華 + 連結 |
| LINE 原始內容 | `"line"` | 短版精華文字 |
| Notion / 詳細閱讀 | `"notion"` | 完整 markdown |
| 網頁連結 | `"url"` | HTML 頁面網址 |
| Debug | `"json"` | 原始 JSON |

## 執行日報生成

```bash
cd ~/Documents/thinker-news
python scripts/main.py
```

需要環境變數（`.env`）：
- `OPENAI_API_KEY`
- `DEEPSEEK_API_KEY`

## 健康檢查

```bash
python scripts/health_check.py           # 基本檢查
python scripts/health_check.py --network # 含網路連線檢查
python scripts/health_check.py --json    # JSON 輸出
```

## 注意事項

- **不要直接修改 `scripts/` 核心邏輯**，除非完全理解 pipeline
- **日報 HTML 在 `archive/`**，不要刪除
- **`latest.json` 是 runtime 產物**，已加入 `.gitignore`
- **commit message 用中文**
- **刪檔用 `git rm` 或 `trash`**，不用 `rm`
