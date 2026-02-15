# ARCHITECTURE.md — Thinker News 系統架構

> 最終版。反映 refactor/cleanup-v1 重構後的真實架構。
> 最後更新：2026-02-16（Round 29）

## 📌 系統概述

Thinker News 是一個**每日自動生成 AI 科技新聞日報**的系統。

- **排程引擎：** GitHub Actions cron（每日 UTC 00:05 = 台灣 08:05）
- **靜態託管：** GitHub Pages
- **網站：** https://thinkercafe-tw.github.io/thinker-news/
- **目標受眾：** 台灣科技初學者

---

## 🏗️ 專案結構

```
thinker-news/
├── scripts/                    # 核心程式碼（15 模組，~3,270 行）
│   ├── main.py           (285)   主流程協調器 — retry_call + 4 個 pipeline step
│   ├── rss_fetcher.py    (144)   RSS 來源讀取 — 8 來源並行 + timeout/retry
│   ├── news_filter.py    (214)   新聞篩選 + 評分 — 引用 filter_config.py
│   ├── filter_config.py  (170)   篩選配置 — 來源權重、關鍵字、標籤
│   ├── ai_processor.py   (501)   四段式 AI 處理鏈 — 單例 client + call_openai
│   ├── prompts.py        (285)   AI System Prompts — 煉金術師/導讀人/總編輯
│   ├── html_generator.py (196)   HTML 生成 + SEO 注入 — 讀取 templates/
│   ├── rss_feed.py       (207)   RSS 2.0 輸出 feed — feed.xml 產生器
│   ├── get_latest_news.py(115)   /news 回覆 — 讀 latest.json，5 種格式輸出
│   ├── line_handler.py   (213)   LINE Bot — webhook + CLI + /news + /help
│   ├── health_check.py   (287)   健康檢查 — 6 項 env/pkg/template/dir/rss/api
│   ├── error_notifier.py (204)   錯誤通知 — Slack Webhook + LINE Push
│   ├── log_config.py      (50)   統一 logging — get_logger() 格式化
│   ├── execution_logger.py(162)  執行日誌 — execution_log.json 追蹤
│   ├── utils.py          (159)   工具函數 — 日期、JSON 驗證
│   └── templates/                HTML 模板
│       ├── daily_news.html(297)  日報模板（OG + JSON-LD + RSS autodiscovery）
│       └── index.html     (430)  首頁模板（動態日報列表 + feature grid）
├── .github/workflows/
│   └── daily-news.yml            GitHub Actions workflow（含 health_check 步驟）
├── archive/                      歷史日報 HTML（137+ 檔）
├── index.html                    首頁（每日重新生成）
├── latest.json                   最新內容 JSON（LINE bot / /news 讀取用）
├── feed.xml                      RSS 2.0 訂閱 feed
├── README.md                     專案說明
├── AGENT_GUIDE.md                Agent 操作指引
├── requirements.txt              Python 依賴（6 套件）
└── private/
    └── thinker_panel.html        管理面板
```

---

## 🔄 Pipeline 資料流

```
                          ┌─────────────────────┐
                          │   GitHub Actions     │
                          │   daily-news.yml     │
                          └──────────┬──────────┘
                                     │
                          ┌──────────▼──────────┐
                          │  Step 0: Health Check │
                          │  health_check.py     │
                          └──────────┬──────────┘
                                     │ pass
                          ┌──────────▼──────────┐
                          │  Step 1: RSS 讀取     │
                          │  rss_fetcher.py      │
                          │  8 來源 ThreadPool    │
                          └──────────┬──────────┘
                                     │ all_feeds[]
                          ┌──────────▼──────────┐
                          │  Step 2: 篩選 + 評分  │
                          │  news_filter.py      │
                          │  + filter_config.py  │
                          └──────────┬──────────┘
                                     │ filtered_news[]
                   ┌─────────────────┴─────────────────┐
                   │         Step 3: AI 處理鏈          │
                   │         ai_processor.py            │
                   │                                    │
                   │  ① 數據煉金術師 (DeepSeek-V3)      │
                   │     → 分類 + 標題轉譯               │
                   │  ② 科技導讀人 (GPT-4o)             │
                   │     → Notion 完整日報               │
                   │  ③ 總編輯 (GPT-4o)                 │
                   │     → LINE 精簡快訊                 │
                   │  ④ HTML 生成器 (DeepSeek-V3)       │
                   │     → HTML body 內容               │
                   └─────────────────┬─────────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
   ┌──────────▼────────┐  ┌─────────▼─────────┐  ┌────────▼────────┐
   │ Step 4a: HTML 生成 │  │ Step 4b: 首頁更新  │  │ Step 4c: 產出    │
   │ {date}.html        │  │ index.html         │  │ latest.json     │
   │ + SEO meta 注入    │  │ 動態日報列表       │  │ feed.xml        │
   └────────────────────┘  └───────────────────┘  └─────────────────┘
                                     │
                          ┌──────────▼──────────┐
                          │  Git commit + push   │
                          │  GitHub Pages 部署   │
                          └─────────────────────┘
```

**失敗路徑：** 任何步驟例外 → `error_notifier.py` 發送 Slack/LINE 通知 → GitHub Actions failure step 額外通知

---

## 📡 RSS 來源（8 個）

| 來源 | 代號 | 區域 | 基礎分數 | 上限 |
|------|------|------|---------|------|
| 🇹🇼 科技新報 | technews | tw | 8 | 12 則 |
| 🇹🇼 iThome | ithome | tw | 7 | 10 則 |
| 🇹🇼 INSIDE | inside | tw | 6 | 8 則 |
| 🌍 Hacker News | hackernews | intl | 0 | 8 則 |
| 🌍 TechCrunch | techcrunch | intl | 0 | 6 則 |
| 🤖 OpenAI Blog | openai | ai | 15 | 5 則 |
| 🌍 Ars Technica | arstechnica | intl | 0 | 4 則 |
| 🎓 Berkeley AI (BAIR) | bair | ai | 3 | 3 則 |

**連線設定：** timeout 15s / retry 2 次 / delay 2s / ThreadPoolExecutor 並行

---

## 🤖 AI 處理鏈

| 階段 | 名稱 | 模型 | 輸入 | 輸出 |
|------|------|------|------|------|
| 1 | 數據煉金術師 | DeepSeek-V3 | filtered_news JSON | 分類 + 標題翻譯 JSON |
| 2 | 科技導讀人 | GPT-4o | 階段 1 JSON | Notion 日報內容 JSON |
| 3 | 總編輯 | GPT-4o | 階段 2 JSON | LINE 快訊文字 JSON |
| 4 | HTML 生成器 | DeepSeek-V3 | notion + line 內容 | HTML body 字串 |

- **Client 管理：** 單例模式（OpenAI / DeepSeek 各一個 client instance）
- **統一呼叫：** `call_openai(client, model, messages)` 封裝所有 API 互動
- **Prompts：** 獨立於 `prompts.py`（煉金術師 / 導讀人 / 總編輯三組 system prompt）
- **重試：** `retry_call()` 最多 2 次，含 step 名稱追蹤
- **JSON 修復：** `json-repair` 套件自動修正 AI 不規範 JSON

---

## 📊 輸出檔案

| 檔案 | 說明 | 誰讀取 |
|------|------|--------|
| `{YYYY-MM-DD}.html` | 每日新聞頁面 | 讀者（瀏覽器） |
| `index.html` | 首頁（含歷史日報列表） | 讀者（瀏覽器） |
| `latest.json` | 最新 AI 產出 JSON | LINE Bot / /news 指令 |
| `feed.xml` | RSS 2.0 訂閱 feed（最近 20 篇） | RSS 閱讀器 |
| `execution_log.json` | 執行追蹤日誌 | 開發者除錯 |

---

## 🛡️ 可靠性機制

| 機制 | 實作 | 位置 |
|------|------|------|
| **健康檢查** | 6 項前置檢查（env/pkg/template/dir/rss/api） | health_check.py → main.py Step 0 |
| **重試** | `retry_call()` 通用 wrapper + RSS 獨立 retry | main.py + rss_fetcher.py |
| **錯誤通知** | Slack Webhook + LINE Push Message | error_notifier.py |
| **CI 通知** | GitHub Actions failure step 額外觸發 | daily-news.yml |
| **統一 logging** | `get_logger()` 統一格式，8 模組一致 | log_config.py |
| **JSON 修復** | `json-repair` 自動修正 AI 輸出 | utils.py |
| **並行防撞** | `concurrency: daily-news` 限制同時只跑一個 | daily-news.yml |
| **超時保護** | Actions 15 分鐘 timeout | daily-news.yml |

---

## 🔗 外部依賴

### Python 套件（requirements.txt）
| 套件 | 用途 |
|------|------|
| openai | OpenAI + DeepSeek API client |
| feedparser | RSS feed 解析 |
| beautifulsoup4 | HTML 內容清洗 |
| json-repair | AI JSON 輸出修復 |
| requests | HTTP 請求（Slack/LINE 通知） |
| lxml | BeautifulSoup 解析後端 |

### 外部服務
| 服務 | 用途 | 環境變數 |
|------|------|---------|
| OpenAI API | GPT-4o（導讀人 + 總編輯） | `OPENAI_API_KEY` |
| DeepSeek API | DeepSeek-V3（煉金術師 + HTML） | `DEEPSEEK_API_KEY` |
| LINE Messaging API | 推播通知 | `LINE_CHANNEL_ACCESS_TOKEN`, `LINE_CHANNEL_SECRET` |
| Slack Webhook | 錯誤通知 | `SLACK_WEBHOOK_URL` |
| GitHub Pages | 靜態託管 | — |
| GitHub Actions | CI/CD 排程 | — |

---

## 📐 設計原則

1. **模組職責單一** — 每個 .py 一個明確職責，不超過 500 行
2. **配置與邏輯分離** — prompts.py / filter_config.py / templates/ 獨立於處理邏輯
3. **確定性回覆** — /news 直讀 latest.json，不經 AI 二次加工
4. **漸進失敗** — 單一 RSS 來源失敗不影響整體；API 失敗有重試 + 通知
5. **SEO 友善** — OG tags / Twitter Card / JSON-LD / canonical URL / RSS autodiscovery
