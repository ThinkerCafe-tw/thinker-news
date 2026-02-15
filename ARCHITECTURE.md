# ARCHITECTURE.md — Thinker News 系統架構

> 由 Phase 0 偵察產出，Round 3 建立。

## 📌 系統概述

Thinker News 是一個每日自動生成 AI 科技新聞日報的系統，從 n8n workflow 遷移到 GitHub Actions + Python pipeline。

- **部署方式：** GitHub Actions（排程 cron）+ GitHub Pages（靜態託管）
- **網站：** https://thinkercafe-tw.github.io/thinker-news/
- **目標受眾：** 台灣科技初學者

---

## 🔧 核心 Pipeline（6 檔案）

```
main.py (272行)  — 主流程協調器
  │
  ├─ rss_fetcher.py (109行)  — RSS 來源讀取
  │    └─ 7 個 RSS feeds，ThreadPoolExecutor 並行讀取
  │
  ├─ news_filter.py (362行)  — 台灣本地化篩選 + 評分
  │    └─ 關鍵字評分系統，台灣/國際平衡策略
  │
  ├─ ai_processor.py (847行)  — 四段式 AI 處理鏈
  │    ├─ ⚗️  數據煉金術師 (DeepSeek) — 標題轉譯、分類
  │    ├─ 📰 科技導讀人 (GPT-4o) — 撰寫完整 Notion 日報
  │    ├─ ✍️  總編輯 (GPT-4o) — 提煉 LINE 精簡快訊
  │    └─ 🎨 HTML 生成器 (DeepSeek) — 生成 HTML body 內容
  │
  ├─ html_generator.py (778行)  — HTML 模板 + 首頁更新
  │    ├─ generate_daily_html() — 固定 <head> + AI 生成 <body>
  │    └─ update_index_html() — 更新 index.html 首頁
  │
  ├─ utils.py (132行)  — 工具函數
  │    ├─ get_taiwan_date() — 台灣時區日期
  │    └─ validate_json_output() — AI JSON 輸出驗證 + json-repair
  │
  └─ execution_logger.py (170行)  — 執行日誌記錄器
       └─ 輸出 execution_log.json（每次執行完整追蹤）
```

---

## 🔄 資料流

```
[7 RSS feeds] ──並行讀取──→ [all_feeds: List[Dict]]
                                    │
                              ┌─────▼──────┐
                              │ 篩選 + 評分  │  ← 關鍵字匹配 + 來源權重
                              └─────┬──────┘
                                    │
                           [filtered_news: 20-50 則]
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                         │                          │
    ┌────▼─────┐            ┌──────▼──────┐           ┌───────▼───────┐
    │ DeepSeek  │            │  GPT-4o     │           │   GPT-4o      │
    │ 煉金術師  │──JSON──→   │ 科技導讀人   │──JSON──→  │   總編輯       │
    │ 分類+翻譯  │            │ Notion 日報  │           │ LINE 快訊     │
    └──────────┘            └─────────────┘           └───────┬───────┘
                                    │                          │
                                    ▼                          ▼
                          [notion_content]            [line_content]
                                    │                          │
                                    └────────┬─────────────────┘
                                             │
                                    ┌────────▼────────┐
                                    │ DeepSeek         │
                                    │ HTML 生成器      │  ← 接收 notion + line 內容
                                    │ 生成完整 HTML    │
                                    └────────┬────────┘
                                             │
                              ┌──────────────┼──────────────┐
                              │              │              │
                         {date}.html    index.html    latest.json
```

---

## 📡 RSS 來源（7 個）

| 來源 | 類型 | 基礎分數 | 上限 |
|------|------|---------|------|
| 🇹🇼 科技新報 (technews) | 台灣 | 8 | 12 則 |
| 🇹🇼 iThome | 台灣 | 7 | 10 則 |
| 🇹🇼 INSIDE | 台灣 | 6 | 8 則 |
| 🌍 Hacker News | 國際 | 0 | 8 則 |
| 🌍 TechCrunch | 國際 | 0 | 6 則 |
| 🤖 OpenAI Blog | 國際 | 15 | 5 則 |
| 🌍 Ars Technica | 國際 | 0 | 4 則 |
| 🎓 Berkeley AI (BAIR) | 學術 | 3 | 3 則 |

**注意：** INSIDE 來源有配置但 RSS_SOURCES 中未包含（只有 7 個實際來源），是潛在遺留問題。

---

## 🤖 AI 處理鏈詳解

### 四階段串行處理

| 階段 | 名稱 | 模型 | 輸入 | 輸出 |
|------|------|------|------|------|
| 1 | 數據煉金術師 | DeepSeek-V3 | filtered_news (JSON) | 分類+翻譯 JSON |
| 2 | 科技導讀人 | GPT-4o | 階段1 JSON | Notion 日報文字 |
| 3 | 總編輯 | GPT-4o | 階段2 JSON | LINE 快訊文字 |
| 4 | HTML 生成器 | DeepSeek-V3 | notion + line 文字 | 完整 HTML body |

**成本估計：** 每日 4 次 API 呼叫（2x DeepSeek + 2x GPT-4o）

### 重試機制
- `retry_on_failure` 裝飾器：最多 2 次重試，間隔 3 秒
- JSON 輸出自動修復：`json-repair` 套件

---

## 📁 輸出檔案

| 檔案 | 說明 | 更新頻率 |
|------|------|---------|
| `{YYYY-MM-DD}.html` | 每日新聞頁面 | 每日 |
| `index.html` | 首頁（含歷史連結列表） | 每日 |
| `latest.json` | 最新內容 JSON（LINE bot 讀取用） | 每日 |
| `execution_log.json` | 執行追蹤日誌 | 每日 |
| `news_generation.log` | Python logging 輸出 | 每日 |

---

## ⚠️ 已知問題 & 改進點

### 架構問題
1. **`ai_processor.py` 847 行太長** — 4 個 AI 階段 + 超長 prompt 全擠在一個檔案
2. **`html_generator.py` 778 行太長** — index.html 的完整 HTML 模板直接寫在 Python 字串裡（~600 行 HTML）
3. **每次 API 呼叫都重新 `setup_apis()`** — `call_deepseek()` 內部每次都建立新 client，浪費資源
4. **INSIDE 來源配置孤兒** — `news_filter.py` 有 INSIDE 的篩選規則，但 `rss_fetcher.py` 沒有對應 RSS URL

### 穩定性問題
5. **無 fallback 機制** — 任何一個 AI 階段失敗就整體失敗
6. **硬編碼日期邏輯** — `filter_and_score_news` 只取「昨天」的新聞，週一漏掉週末
7. **`get_taiwan_date()` 用 `datetime.utcnow()`** — 已棄用，應改用 `datetime.now(timezone.utc)`

### 維護問題
8. **135 個日報 HTML 在 repo 根目錄** — 嚴重污染目錄結構
9. **9 個廢棄 .py 在根目錄** — 歷史遺留
10. **n8n/Vercel 殘留檔案** — 已無用但仍在 repo

---

## 🗺️ 重構方向（參考）

- **Phase 1：** 清理垃圾檔案，整理目錄結構
- **Phase 2：** 拆分大檔案，修復已知 bug，改進容錯
- **Phase 3：** 新功能（RSS output、error notification、SEO）
- **Phase 4：** 文件更新、PR 合併

詳見 `REFACTOR_STATE.md`
