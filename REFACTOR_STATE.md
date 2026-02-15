# REFACTOR_STATE.md — Thinker News 重構狀態機

> 此檔案由 cron job 自動讀寫，是跨 session 的記憶接力棒。
> 每輪開始時讀取，結束時更新。

## 🏁 Overall Progress

- **Total Rounds:** 31 / 100
- **Current Phase:** PHASE_4
- **Status:** IN_PROGRESS
- **Last Run:** 2026-02-16 02:49 (Round 31)
- **Branch:** refactor/cleanup-v1

---

## 📋 Phase Definitions

### PHASE_0: 偵察與盤點 (Rounds 1-5)
- [x] 完整掃描 repo 結構，列出所有檔案用途
- [x] 識別廢棄檔案（不被任何 scripts/ 引用的 .py/.js）
- [x] 識別可清理的歷史產物（舊 HTML、logs、n8n/vercel 殘留）
- [x] 讀懂核心 pipeline：main.py → rss_fetcher → news_filter → ai_processor → html_generator
- [x] 產出 CLEANUP_MANIFEST.md（待刪清單 + 理由）
- [x] 產出 ARCHITECTURE.md（現有架構圖 + 問題診斷）

### PHASE_1: 垃圾清理 (Rounds 6-15)
- [x] 建立 refactor branch
- [x] 把 137 個日報 HTML 移到 `archive/` 目錄
- [x] 刪除廢棄根目錄 .py 檔（generate_daily_news_old.py, enhanced_news_generator.py, etc.）
- [x] 刪除 n8n/vercel 殘留（api/, vercel.json, webhook_receiver.*, unified_webhook.*）
- [x] 刪除過期 .txt/.log 檔（含 4 個廢棄 .md）
- [x] 清理 .gitignore（加入 *.log, __pycache__, .env 等）
- [x] 整理 requirements.txt（移除不需要的 deps）
- [x] 每步都 git commit，commit message 清楚

### PHASE_2: 程式碼重構 (Rounds 16-50)
- [x] ai_processor.py (623→501行) — API 單例化、統一呼叫介面、移除重複程式碼（✅ prompts.py + 單例 client + call_openai）
- [x] html_generator.py (778行) — 模板化、移除 hardcoded 樣式（✅ HTML 模板已抽取至 scripts/templates/，778→101 行）
- [x] news_filter.py (362行) — 評審篩選邏輯、更新關鍵字（✅ 篩選配置已抽取至 filter_config.py，362→214 行）
- [x] rss_fetcher.py (109行) — 新增 RSS 來源、改進容錯（✅ 新增 INSIDE 來源 + timeout/retry，109→145 行）
- [x] main.py (272行) — 簡化流程、加入更好的 retry/fallback（✅ 新增 retry_call + 拆分 4 個 step 函式，272→267 行）
- [x] 加入 /news 回覆一致性修復（讀 latest.json → 原文照發）（✅ get_latest_news.py，5 種格式輸出）
- [x] 統一 logging 格式（✅ 新增 log_config.py，8 模組統一用 get_logger()）
- [x] 加入基本 health check 機制（✅ 新增 health_check.py，檢查 env/套件/模板/目錄/網路，整合至 main.py）

### PHASE_3: 新功能 & 穩定性 (Rounds 51-80)
- [x] 建立 AGENTS.md for thinker-news agent（讓 /news 回覆穩定）（✅ 改名 AGENT_GUIDE.md 避免 .gitignore 衝突）
- [x] 加入 LINE /news 指令的確定性處理（不經 AI 加工）（✅ line_handler.py — webhook + CLI + /help，Python 3.9 相容）
- [x] SEO 基礎：OG tags、meta description、結構化資料（✅ OG + Twitter Card + canonical + JSON-LD，模板 + AI 生成路徑皆覆蓋）
- [x] 改進 index.html 首頁設計（✅ 動態日報列表、feature grid、移除冗餘學習洞察/訂閱區塊）
- [x] 加入 RSS output feed（讓別人訂閱）（✅ rss_feed.py 產生 RSS 2.0 feed.xml，20 篇日報，整合至 pipeline + 模板 autodiscovery）
- [x] 加入 error notification（生成失敗時通知 Cruz）（✅ error_notifier.py 支援 Slack+LINE，整合至 main.py + GitHub Actions failure step）
- [x] GitHub Actions workflow 優化（✅ 加入 health_check 步驟、concurrency 控制、15 分鐘 timeout、精確 git add、LINE secrets 整合）

### PHASE_4: 文件與收尾 (Rounds 81-100)
- [x] 更新 README.md（反映新架構）（✅ 全面改寫：移除 n8n 內容、更新 15 個模組結構、8 個 RSS 來源、新增 health check/RSS feed/LINE Bot 段落）
- [x] 清理舊文件（OVERVIEW.md, DEPLOYMENT.md, N8N_INTEGRATION_GUIDE.md, FINAL_IMPLEMENTATION_GUIDE.md）（✅ git rm 4 個過期文件，共 864 行刪除）
- [x] 產出最終 ARCHITECTURE.md（✅ 全面重寫：15 模組結構、8 RSS 來源、Pipeline 資料流圖、可靠性機制表、外部依賴清單、設計原則）
- [x] 產出 CHANGELOG.md（✅ 完整記錄 v1.0→v2.0：移除/重構/新功能/CI/文件，含 10 個新模組一覽表）
- [x] 確認所有功能正常（✅ 11 模組語法通過、2 模板渲染通過、CI YAML 合法、跨模組引用正確、git 乾淨）
- [ ] 準備 PR 合回 main

---

## 📝 Round Log

<!-- 每輪結束時在此追加一條紀錄 -->
<!-- 格式: | Round | Time | Phase | Action | Result | -->

| Round | Time | Phase | Action | Result |
|-------|------|-------|--------|--------|
| 1 | 2026-02-15 21:49 | PHASE_0 | 完整掃描 repo 結構 | 產出 REPO_INVENTORY.md，盤點 170+ 檔案，識別 9 廢棄 .py、135 日報 HTML、Vercel/n8n 殘留 |
| 2 | 2026-02-15 22:00 | PHASE_0 | 驗證廢棄檔案 + 歷史產物 | grep 交叉驗證：9 .py 全確認孤兒、2 .js 仍被 scripts/ 引用（保留）、api/ 2 檔 + vercel.json 確認廢棄、5 txt/log + 4 md 確認孤兒、execution_log.json 仍活躍 |
| 3 | 2026-02-15 22:09 | PHASE_0 | 讀懂核心 pipeline + 產出 ARCHITECTURE.md | 完整分析 6 個核心檔案：main.py→rss_fetcher→news_filter→ai_processor→html_generator→utils，繪製資料流圖，識別 10 個已知問題（API client 重複建立、INSIDE 來源孤兒、無 fallback 等） |
| 4 | 2026-02-15 22:19 | PHASE_0 | 產出 CLEANUP_MANIFEST.md | 列出 21 個待刪檔案（9 .py + 3 Vercel + 5 txt/log + 4 md）+ 137 個日報 HTML 移動計畫，PHASE_0 全部完成 ✅ |
| 5 | 2026-02-15 22:29 | PHASE_1 | 移動 137 個日報 HTML 至 archive/ | git mv 137 個 HTML（含 dashboard.html、test_secret_entrance.html）至 archive/，根目錄大幅瘦身，branch 已就緒 |
| 6 | 2026-02-15 22:39 | PHASE_1 | 刪除 9 個廢棄根目錄 .py 檔 | git rm 9 個未被引用的 .py（generate_daily_news*.py、enhanced_news_generator.py、email_subscription_manager.py 等），共刪 2670 行 |
| 7 | 2026-02-15 22:49 | PHASE_1 | 刪除 n8n/Vercel 殘留 | git rm api/（debug.js、line-webhook.js）、vercel.json、webhook_receiver.log、unified_webhook.log，共刪 233 行 |
| 8 | 2026-02-15 22:59 | PHASE_1 | 刪除過期 .txt/.log + 廢棄 .md | git rm 7 個孤兒檔（3 txt + 4 md），共刪 407 行，CLEANUP_MANIFEST 清單 3+4 全部完成 |
| 9 | 2026-02-15 23:09 | PHASE_1 | 清理 .gitignore | 加入 execution_log.json、OpenClaw workspace 檔案、macOS/Node 忽略規則；untrack execution_log.json（runtime 產物不入 repo） |
| 10 | 2026-02-15 23:19 | PHASE_1 | 整理 requirements.txt | 移除未使用的 python-dateutil（grep 驗證無 import），保留 6 個實際依賴。PHASE_1 全部完成 ✅ |
| 11 | 2026-02-15 23:29 | PHASE_2 | 抽取 system prompts 至 prompts.py | 新增 scripts/prompts.py，3 大 prompt 從 ai_processor.py 移出，847→623 行（-224 行），import 驗證通過 |
| 12 | 2026-02-15 23:39 | PHASE_2 | 抽取 HTML 模板至獨立檔案 | 新增 scripts/templates/（daily_news.html + index.html），html_generator.py 從 778→101 行（-87%），模板渲染驗證通過 |
| 13 | 2026-02-15 23:49 | PHASE_2 | 抽取篩選配置至 filter_config.py | 新增 scripts/filter_config.py（來源配置+關鍵字集合+標籤），news_filter.py 從 362→214 行（-41%），import 驗證通過 |
| 14 | 2026-02-15 23:59 | PHASE_2 | 重構 rss_fetcher.py | 新增 INSIDE 來源（修復 filter_config 孤兒）、urllib timeout 15s、retry 2 次、User-Agent header、失敗來源記錄，109→145 行 |
| 15 | 2026-02-16 00:09 | PHASE_2 | 重構 main.py | 新增 retry_call() 通用重試、拆分 4 個 pipeline step 函式、簡化 exec_logger 整合，272→267 行 |
| 16 | 2026-02-16 00:19 | PHASE_2 | 重構 ai_processor.py | API client 單例化（不再每次呼叫重建）、新增 call_openai() 統一介面、HTML prompt 改用 prompts.py、移除冗餘 try/except，623→501 行（-20%） |
| 17 | 2026-02-16 00:31 | PHASE_2 | 統一 logging 格式 | 新增 log_config.py（統一格式+單次初始化），8 個模組移除 import logging 改用 get_logger()，補勾 html_generator + news_filter checkbox |
| 18 | 2026-02-16 00:39 | PHASE_2 | /news 回覆一致性修復 | 新增 get_latest_news.py，讀 latest.json 原文照發，支援 line/notion/url/json/reply 五種格式，含 format_news_reply() 供訊息平台直接使用 |
| 19 | 2026-02-16 00:50 | PHASE_2 | 加入 health check 機制 | 新增 scripts/health_check.py（6 項檢查：env vars、packages、templates、output dirs、RSS、API），整合至 main.py 步驟 0，支援 CLI 獨立執行（--network --json），PHASE_2 全部完成 ✅ |
| 20 | 2026-02-16 01:00 | PHASE_3 | 建立 AGENT_GUIDE.md | 新增專案 agent 指引文件（專案概述、目錄結構、/news 處理流程、latest.json 結構、健康檢查用法），避免與 OpenClaw AGENTS.md 衝突改用 AGENT_GUIDE.md |
| 21 | 2026-02-16 01:09 | PHASE_3 | LINE /news 確定性處理 | 新增 line_handler.py（webhook + CLI），/news 直讀 latest.json 不經 AI、/help 指令、LINE 簽名驗證、修復 get_latest_news.py Python 3.9 相容性 |
| 22 | 2026-02-16 01:21 | PHASE_3 | SEO 基礎建設 | 兩個模板加入 OG tags + Twitter Card + canonical + JSON-LD；html_generator.py 新增 _inject_seo_meta() 自動注入 AI 生成 HTML，含冪等檢查 |
| 23 | 2026-02-16 01:31 | PHASE_3 | 改進 index.html 首頁設計 | 模板重設計：今日亮點卡片 + 動態日報列表（掃描 archive/）+ feature grid，移除硬編碼學習洞察/訂閱/明日預告，header 顯示總期數 |
| 24 | 2026-02-16 01:39 | PHASE_3 | 新增 RSS output feed | rss_feed.py 產生 RSS 2.0 feed.xml（20 篇），整合至 main.py pipeline，模板 + SEO 注入加入 autodiscovery，首頁新增 RSS 訂閱卡片 |
| 25 | 2026-02-16 01:49 | PHASE_3 | 新增錯誤通知機制 | error_notifier.py 支援 Slack Webhook + LINE Push，main.py 整合（Pipeline 例外 + 健檢失敗），GitHub Actions 新增 failure step |
| 26 | 2026-02-16 01:59 | PHASE_3 | 優化 GitHub Actions workflow | 加入 health_check 步驟、concurrency 防重複、15 分鐘 timeout、精確 git add（只 commit 產出檔）、LINE secrets 整合至主步驟，PHASE_3 全部完成 ✅ |
| 27 | 2026-02-16 02:09 | PHASE_4 | 更新 README.md | 全面改寫：移除 n8n 遷移內容、更新 15 模組專案結構、8 個 RSS 來源、新增 health check/RSS feed/LINE Bot/錯誤通知說明，116 行新增 215 行刪除 |
| 28 | 2026-02-16 02:19 | PHASE_4 | 清理舊文件 | git rm 4 份過期文件（OVERVIEW/DEPLOYMENT/N8N_INTEGRATION_GUIDE/FINAL_IMPLEMENTATION_GUIDE），共刪 864 行，被新 README.md 完全取代 |
| 29 | 2026-02-16 02:29 | PHASE_4 | 重寫 ARCHITECTURE.md | 全面更新：15 模組結構圖（含行數）、Pipeline 5 步驟資料流、8 RSS 來源表、AI 處理鏈 4 階段、可靠性機制 8 項、外部依賴清單、設計原則 5 條，Phase 0 舊版完全取代 |
| 30 | 2026-02-16 02:39 | PHASE_4 | 產出 CHANGELOG.md | 完整記錄 v1.0→v2.0 變更：6 大段落（移除/重構/新功能/CI/文件）、10 個新模組一覽表、diffstat 摘要 |
| 31 | 2026-02-16 02:49 | PHASE_4 | 確認所有功能正常 | 11 模組 py_compile 通過、2 Jinja2 模板通過、CI YAML 合法、跨模組引用零斷鏈、git 乾淨 51 commits、產出 VERIFICATION_REPORT.md |

---

## 💬 Human Feedback Queue

<!-- Cruz 在群組裡的 feedback 記錄在此，下一輪讀取並執行 -->

(empty)

---

## ⚠️ Known Issues / Blockers

(none yet)
