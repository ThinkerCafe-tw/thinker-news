# REFACTOR_STATE.md — Thinker News 重構狀態機

> 此檔案由 cron job 自動讀寫，是跨 session 的記憶接力棒。
> 每輪開始時讀取，結束時更新。

## 🏁 Overall Progress

- **Total Rounds:** 12 / 100
- **Current Phase:** PHASE_2
- **Status:** IN_PROGRESS
- **Last Run:** 2026-02-15 23:39 (Round 12)
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
- [ ] ai_processor.py (623行) — 拆分、簡化 prompt、改進錯誤處理（✅ prompts 已抽取至 prompts.py）
- [ ] html_generator.py (778行) — 模板化、移除 hardcoded 樣式（✅ HTML 模板已抽取至 scripts/templates/，778→101 行）
- [ ] news_filter.py (362行) — 評審篩選邏輯、更新關鍵字
- [ ] rss_fetcher.py (109行) — 新增 RSS 來源、改進容錯
- [ ] main.py (272行) — 簡化流程、加入更好的 retry/fallback
- [ ] 加入 /news 回覆一致性修復（讀 latest.json → 原文照發）
- [ ] 統一 logging 格式
- [ ] 加入基本 health check 機制

### PHASE_3: 新功能 & 穩定性 (Rounds 51-80)
- [ ] 建立 AGENTS.md for thinker-news agent（讓 /news 回覆穩定）
- [ ] 加入 LINE /news 指令的確定性處理（不經 AI 加工）
- [ ] SEO 基礎：OG tags、meta description、結構化資料
- [ ] 改進 index.html 首頁設計
- [ ] 加入 RSS output feed（讓別人訂閱）
- [ ] 加入 error notification（生成失敗時通知 Cruz）
- [ ] GitHub Actions workflow 優化

### PHASE_4: 文件與收尾 (Rounds 81-100)
- [ ] 更新 README.md（反映新架構）
- [ ] 清理舊文件（OVERVIEW.md, DEPLOYMENT.md, N8N_INTEGRATION_GUIDE.md, FINAL_IMPLEMENTATION_GUIDE.md）
- [ ] 產出最終 ARCHITECTURE.md
- [ ] 產出 CHANGELOG.md
- [ ] 確認所有功能正常
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

---

## 💬 Human Feedback Queue

<!-- Cruz 在群組裡的 feedback 記錄在此，下一輪讀取並執行 -->

(empty)

---

## ⚠️ Known Issues / Blockers

(none yet)
