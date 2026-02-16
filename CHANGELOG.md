# CHANGELOG

本檔案記錄 Thinker News 的所有重大變更。

---

## [2.0.0] — 2026-02-16 (refactor/cleanup-v1)

大規模重構：30 輪自動化重構，涵蓋垃圾清理、程式碼重構、新功能、文件更新。

**191 個檔案變動 · +4,009 行 · -6,545 行**

### 🗑️ 移除（Phase 1: 垃圾清理）

- 移動 137 個歷史日報 HTML 至 `archive/` 目錄
- 刪除 9 個廢棄根目錄 Python 檔（`generate_daily_news_old.py`、`enhanced_news_generator.py` 等，共 2,670 行）
- 刪除 n8n/Vercel 殘留（`api/`、`vercel.json`、webhook log，共 233 行）
- 刪除 7 個過期 `.txt`/`.log`/`.md` 檔（共 407 行）
- 整理 `.gitignore`：加入 `execution_log.json`、`__pycache__`、`.env`、macOS/Node 規則
- 清理 `requirements.txt`：移除未使用的 `python-dateutil`

### ♻️ 重構（Phase 2: 程式碼重構）

- **ai_processor.py** (847→501 行, -41%)：API client 單例化、統一 `call_openai()` 介面、system prompts 抽取至 `prompts.py`
- **html_generator.py** (778→101 行, -87%)：HTML 模板抽取至 `scripts/templates/`（`daily_news.html` + `index.html`）
- **news_filter.py** (362→214 行, -41%)：篩選配置抽取至 `filter_config.py`（來源配置、關鍵字集合、標籤）
- **rss_fetcher.py** (109→145 行)：新增 INSIDE 來源、15s timeout、retry 2 次、User-Agent header
- **main.py** (272→267 行)：新增 `retry_call()` 通用重試、拆分 4 個 pipeline step 函式
- 統一 logging 格式：新增 `log_config.py`，8 個模組改用 `get_logger()`

### ✨ 新功能（Phase 3: 新功能 & 穩定性）

- **LINE Bot 指令處理** (`line_handler.py`)：`/news` 直讀 `latest.json` 不經 AI、`/help` 指令、webhook 簽名驗證
- **/news 回覆一致性** (`get_latest_news.py`)：支援 5 種格式輸出（line/notion/url/json/reply）
- **健康檢查** (`health_check.py`)：6 項檢查（env vars、packages、templates、output dirs、RSS、API），整合至 pipeline 前置步驟
- **RSS Feed 輸出** (`rss_feed.py`)：產生 RSS 2.0 `feed.xml`（最新 20 篇），模板 autodiscovery
- **錯誤通知** (`error_notifier.py`)：Pipeline 失敗時通知 Slack Webhook / LINE Push
- **SEO 基礎**：OG tags、Twitter Card、canonical URL、JSON-LD 結構化資料，AI 生成 HTML 自動注入
- **首頁改版**：動態日報列表（掃描 `archive/`）、feature grid、移除冗餘學習洞察/訂閱區塊

### 🔧 CI/CD

- GitHub Actions 加入 `health_check` 步驟
- Concurrency 控制防重複執行
- 15 分鐘 timeout
- 精確 `git add`（只 commit 產出檔）
- LINE secrets 整合至主步驟
- Failure step 觸發錯誤通知

### 📚 文件

- 全面改寫 `README.md`：移除 n8n 內容、15 模組結構、8 個 RSS 來源
- 重寫 `ARCHITECTURE.md`：完整資料流圖、可靠性機制表、外部依賴清單
- 新增 `AGENT_GUIDE.md`：thinker-news agent 指引文件
- 刪除 4 份過期文件：`OVERVIEW.md`、`DEPLOYMENT.md`、`N8N_INTEGRATION_GUIDE.md`、`FINAL_IMPLEMENTATION_GUIDE.md`（共 864 行）

### 📁 新增模組一覽

| 模組 | 用途 |
|------|------|
| `scripts/prompts.py` | AI system prompts 集中管理 |
| `scripts/filter_config.py` | 篩選配置（來源、關鍵字、標籤） |
| `scripts/log_config.py` | 統一 logging 格式 |
| `scripts/health_check.py` | Pipeline 前置健康檢查 |
| `scripts/get_latest_news.py` | /news 回覆產生器（5 種格式） |
| `scripts/line_handler.py` | LINE Bot webhook + CLI |
| `scripts/rss_feed.py` | RSS 2.0 feed 產生器 |
| `scripts/error_notifier.py` | 錯誤通知（Slack/LINE） |
| `scripts/templates/daily_news.html` | 日報 HTML 模板 |
| `scripts/templates/index.html` | 首頁 HTML 模板 |

---

## [1.0.0] — 2025 (pre-refactor)

初始版本：n8n workflow + Vercel serverless 架構。

- RSS 抓取 → AI 篩選 → AI 摘要 → HTML 日報
- n8n 驅動排程，Vercel 處理 webhook
- GitHub Pages 靜態部署
- 手動 LINE webhook 整合
