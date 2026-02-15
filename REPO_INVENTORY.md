# REPO_INVENTORY.md — Thinker News Repo 完整盤點

> 產出時間：2026-02-15 Round 1 (PHASE_0)

## 📁 目錄結構

```
thinker-news/
├── scripts/              # 核心 pipeline（2773 行）
│   ├── main.py           (272 行) — 入口，串連 fetch→filter→AI→HTML
│   ├── rss_fetcher.py    (109 行) — RSS 來源抓取
│   ├── news_filter.py    (362 行) — 新聞篩選
│   ├── ai_processor.py   (847 行) — AI 摘要生成（最大檔）
│   ├── html_generator.py (778 行) — 日報 HTML 生成
│   ├── execution_logger.py (162 行) — 執行日誌
│   ├── notify_slack.py   (84 行) — Slack 通知
│   └── utils.py          (159 行) — 工具函數
├── api/                  # Vercel serverless（已廢棄？）
│   ├── debug.js
│   └── line-webhook.js
├── private/
│   └── thinker_panel.html
├── .github/workflows/
│   └── daily-news.yml    # GitHub Actions — 每日 UTC 22:00 觸發
└── 根目錄各種檔案（見下方分類）
```

## 📄 根目錄檔案分類

### ✅ 核心 / 活躍檔案
| 檔案 | 用途 | 狀態 |
|------|------|------|
| `index.html` | 首頁 | 活躍 |
| `latest.json` | 最新一期日報 JSON（LINE bot 讀取） | 活躍，每日更新 |
| `requirements.txt` | Python 依賴 | 活躍 |
| `.gitignore` | Git 忽略規則 | 活躍 |
| `.env.example` | 環境變數範本 | 活躍 |

### 📰 日報 HTML（135 個）
- 範圍：`2025-09-23.html` ~ `2026-02-11.html`
- 總計 135 個日期 HTML + `dashboard.html` + `test_secret_entrance.html`
- 建議：移至 `archive/` 目錄

### 🗑️ 疑似廢棄 .py 檔（根目錄，9 個）
| 檔案 | 推測用途 | 被引用？ |
|------|----------|----------|
| `generate_daily_news.py` | 舊版生成腳本 | ❌ |
| `generate_daily_news_old.py` | 更舊版 | ❌ |
| `enhanced_news_generator.py` | 增強版生成（被 scripts/ 取代） | ❌ |
| `email_subscription_manager.py` | 電子報訂閱 | ❌ |
| `line_insights_notifier.py` | LINE 通知 | ❌ |
| `md2html.py` | Markdown 轉 HTML | ❌ |
| `test_local.py` | 本地測試 | ❌ |
| `unified_webhook_service.py` | 統一 Webhook | ❌ |
| `webhook_receiver.py` | Webhook 接收器 | ❌ |

### ✅ 活躍 .js 檔（根目錄，被 scripts/ HTML 模板引用）
| 檔案 | 用途 | 被引用？ |
|------|------|----------|
| `thinker_secret_entrance.js` | 彩蛋入口 JS | ✅ ai_processor.py:803 + html_generator.py:273 |
| `email_subscription_handler.js` | 訂閱表單前端 | ✅ html_generator.py:761 + index.html |

### 🗑️ 廢棄文字 / 日誌檔
| 檔案 | 類型 |
|------|------|
| `2025-09-25_line_version.txt` | 舊 LINE 版本 |
| `2025-09-26_line_digest.txt` | 舊 LINE 摘要 |
| `avery_line_20250924_081212.txt` | 個人測試檔 |
| `unified_webhook.log` | Webhook 日誌 |
| `webhook_receiver.log` | Webhook 日誌 |

### 🗑️ 廢棄 Markdown
| 檔案 | 類型 |
|------|------|
| `2025-09-25_community_digest.md` | 社群摘要 |
| `2025-09-26_community_digest.md` | 社群摘要 |
| `avery_notion_20250924_081212.md` | 個人測試 |
| `memory_insights_summary.md` | 記憶摘要 |

### 🗑️ 廢棄 JSON / 配置
| 檔案 | 類型 |
|------|------|
| `vercel.json` | Vercel 配置（已不用 Vercel） |
| `execution_log.json` | 執行日誌 — ✅ 被 scripts/main.py + execution_logger.py 引用，活躍 |

### 🗑️ Vercel / n8n 殘留
| 路徑 | 說明 |
|------|------|
| `api/debug.js` | Vercel serverless debug |
| `api/line-webhook.js` | Vercel LINE webhook |
| `vercel.json` | Vercel 配置 |

### 📝 文件（需要整理）
| 檔案 | 狀態 |
|------|------|
| `README.md` | 需更新 |
| `OVERVIEW.md` | 可能過時 |
| `DEPLOYMENT.md` | 可能過時 |
| `N8N_INTEGRATION_GUIDE.md` | n8n 已不用，廢棄 |
| `FINAL_IMPLEMENTATION_GUIDE.md` | 可能過時 |

### 🤖 OpenClaw 相關（不動）
- `AGENTS.md`, `BOOTSTRAP.md`, `HEARTBEAT.md`, `IDENTITY.md`
- `SOUL.md`, `TOOLS.md`, `USER.md`, `REFACTOR_STATE.md`

---

## 🔗 核心 Pipeline 流程

```
GitHub Actions (daily-news.yml)
  └→ python scripts/main.py
       ├→ rss_fetcher.py     — 抓 RSS feeds
       ├→ news_filter.py     — 篩選 & 評分
       ├→ ai_processor.py    — DeepSeek/OpenAI 生成摘要
       ├→ html_generator.py  — 生成 YYYY-MM-DD.html + 更新 index.html
       ├→ execution_logger.py — 記錄執行結果
       └→ notify_slack.py    — Slack 通知
  
  最終產出：YYYY-MM-DD.html + latest.json + index.html
  部署：GitHub Pages（push to main → 自動部署）
```

## 📊 統計

- 總檔案數（不含 .git）：~170+
- 核心程式碼：8 個 .py（scripts/），2773 行
- 廢棄程式碼：9 個根目錄 .py + 2 個 api/ .js
- 日報 HTML：135+ 個（持續增加）
- 廢棄文件/日誌：10+ 個
