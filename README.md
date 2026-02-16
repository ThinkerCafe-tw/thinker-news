# Thinker News 🗞️

AI 驅動的每日科技新聞日報，專為台灣讀者設計。

**🌐 網站：** https://thinkercafe-tw.github.io/thinker-news/
**📡 RSS 訂閱：** https://thinkercafe-tw.github.io/thinker-news/feed.xml

---

## 系統概述

每天早上 06:00（UTC+8）自動執行，從 8 個 RSS 來源抓取新聞，經台灣本地化篩選與 AI 多階段處理後，產出精選日報網頁並部署到 GitHub Pages。

## 架構

```
GitHub Actions (cron 排程)
  │
  ▼
main.py ─── 主流程協調器
  ├── health_check.py ─── 啟動前環境檢查
  ├── rss_fetcher.py ─── 並行抓取 8 個 RSS 來源
  ├── news_filter.py ─── 台灣本地化篩選 + 智能評分
  ├── ai_processor.py ─── 四階段 AI 處理鏈
  │     ├── 數據煉金術師 (DeepSeek) → 分類翻譯
  │     ├── 科技導讀人 (GPT-4o) → Notion 日報
  │     ├── 總編輯 (GPT-4o) → LINE 快訊
  │     └── HTML 生成器 (DeepSeek) → 網頁內容
  ├── html_generator.py ─── Jinja2 模板渲染
  ├── rss_feed.py ─── 產生 RSS 2.0 feed.xml
  └── error_notifier.py ─── 失敗通知（Slack / LINE）
```

### 資料流

```
8 個 RSS feeds → 並行抓取 → 篩選評分（20-50 則）
  → DeepSeek 分類翻譯 → GPT-4o 撰寫日報 → GPT-4o 提煉快訊
  → DeepSeek 生成 HTML → 模板渲染 → 部署 GitHub Pages
```

## RSS 來源

| 來源 | 區域 |
|------|------|
| 🇹🇼 科技新報 (technews.tw) | 台灣 |
| 🇹🇼 iThome | 台灣 |
| 🇹🇼 INSIDE | 台灣 |
| 🌍 Hacker News | 國際 |
| 🌍 TechCrunch | 國際 |
| 🌍 Ars Technica | 國際 |
| 🤖 OpenAI Blog | AI |
| 🎓 Berkeley AI Research (BAIR) | AI |

## 專案結構

```
thinker-news/
├── .github/workflows/
│   └── daily-news.yml          # GitHub Actions 排程
├── scripts/
│   ├── main.py                 # 主流程（含 retry + health check 整合）
│   ├── rss_fetcher.py          # RSS 並行抓取（timeout + retry）
│   ├── news_filter.py          # 篩選邏輯
│   ├── filter_config.py        # 篩選配置（關鍵字、來源權重）
│   ├── ai_processor.py         # 四階段 AI 處理鏈
│   ├── prompts.py              # AI system prompts（獨立管理）
│   ├── html_generator.py       # Jinja2 模板渲染
│   ├── rss_feed.py             # RSS 2.0 feed 產生器
│   ├── health_check.py         # 環境健康檢查
│   ├── error_notifier.py       # Slack + LINE 錯誤通知
│   ├── get_latest_news.py      # /news 查詢（讀 latest.json）
│   ├── line_handler.py         # LINE Bot webhook + CLI
│   ├── log_config.py           # 統一 logging 格式
│   ├── execution_logger.py     # 執行追蹤日誌
│   ├── notify_slack.py         # Slack 通知
│   ├── utils.py                # 工具函數
│   └── templates/
│       ├── daily_news.html     # 日報 Jinja2 模板
│       └── index.html          # 首頁 Jinja2 模板
├── archive/                    # 歷史日報 HTML
├── latest.json                 # 最新內容（供 bot 讀取）
├── feed.xml                    # RSS 2.0 訂閱 feed
├── index.html                  # 首頁
├── requirements.txt            # Python 依賴
├── AGENT_GUIDE.md              # Agent 整合指引
├── ARCHITECTURE.md             # 詳細架構文件
└── README.md
```

## 快速開始

### 安裝

```bash
git clone https://github.com/ThinkerCafe-tw/thinker-news.git
cd thinker-news
pip install -r requirements.txt
```

### 環境變數

| 變數 | 必要 | 說明 |
|------|------|------|
| `GOOGLE_API_KEY` | ✅ | Google Gemini API Key |
| `OPENAI_API_KEY` | ✅ | OpenAI API Key |
| `SLACK_WEBHOOK_URL` | 選填 | Slack 通知 Webhook |
| `LINE_CHANNEL_ACCESS_TOKEN` | 選填 | LINE Bot 推送 |
| `LINE_CHANNEL_SECRET` | 選填 | LINE Webhook 驗證 |

### 本地執行

```bash
export GOOGLE_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
python scripts/main.py
```

### Health Check

```bash
python scripts/health_check.py              # 基本檢查
python scripts/health_check.py --network    # 含網路連線檢查
python scripts/health_check.py --json       # JSON 格式輸出
```

## 產出檔案

每日執行後產出：

| 檔案 | 說明 |
|------|------|
| `YYYY-MM-DD.html` | 當日新聞日報 |
| `index.html` | 首頁（含歷史日報列表） |
| `latest.json` | 最新內容 JSON |
| `feed.xml` | RSS 2.0 feed |

## GitHub Actions

- **排程：** 每天 UTC 22:00（台灣 06:00）
- **手動觸發：** Actions 頁面 → Run workflow
- **功能：** Health check → Pipeline → Git commit → Deploy → 失敗通知
- **防護：** Concurrency 控制、15 分鐘 timeout

## 成本

| 項目 | 費用 |
|------|------|
| GitHub Actions | $0（免費額度） |
| DeepSeek API | ~$0.01/天 |
| OpenAI API (GPT-4o) | ~$0.05-0.10/天 |
| **月成本** | **< $3** |

## 授權

MIT License

## 聯繫

- **作者：** Cruz Tang
- **組織：** [ThinkerCafe](https://github.com/ThinkerCafe-tw)
