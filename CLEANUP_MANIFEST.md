# CLEANUP_MANIFEST.md — 待清理清單

> 產出時間：2026-02-15 Round 4 (PHASE_0)
> 驗證方法：grep 交叉比對 + REPO_INVENTORY.md + ARCHITECTURE.md

---

## 🗑️ 刪除清單

### 1. 廢棄根目錄 .py（9 個）

全部經 grep 確認未被 scripts/ 任何檔案引用。

| 檔案 | 理由 | 動作 |
|------|------|------|
| `generate_daily_news.py` | 舊版生成腳本，已被 scripts/main.py 取代 | `git rm` |
| `generate_daily_news_old.py` | 更舊版本 | `git rm` |
| `enhanced_news_generator.py` | 增強版生成腳本，已被 scripts/ 取代 | `git rm` |
| `email_subscription_manager.py` | 電子報訂閱功能（從未上線） | `git rm` |
| `line_insights_notifier.py` | LINE 通知腳本（已不使用） | `git rm` |
| `md2html.py` | Markdown 轉 HTML 工具 | `git rm` |
| `test_local.py` | 本地測試腳本 | `git rm` |
| `unified_webhook_service.py` | 統一 Webhook 服務（已棄用） | `git rm` |
| `webhook_receiver.py` | Webhook 接收器（已棄用） | `git rm` |

### 2. Vercel / n8n 殘留（3 個）

Vercel 已不使用，n8n 已不使用。

| 檔案 | 理由 | 動作 |
|------|------|------|
| `api/debug.js` | Vercel serverless debug endpoint | `git rm` |
| `api/line-webhook.js` | Vercel LINE webhook handler | `git rm` |
| `vercel.json` | Vercel 部署配置 | `git rm` |

### 3. 廢棄文字 / 日誌檔（5 個）

| 檔案 | 理由 | 動作 |
|------|------|------|
| `2025-09-25_line_version.txt` | 舊 LINE 版本文字，歷史產物 | `git rm` |
| `2025-09-26_line_digest.txt` | 舊 LINE 摘要文字，歷史產物 | `git rm` |
| `avery_line_20250924_081212.txt` | 個人測試檔 | `git rm` |
| `unified_webhook.log` | Webhook 日誌，不應入 repo | `git rm` |
| `webhook_receiver.log` | Webhook 日誌，不應入 repo | `git rm` |

### 4. 廢棄 Markdown（4 個）

| 檔案 | 理由 | 動作 |
|------|------|------|
| `2025-09-25_community_digest.md` | 舊社群摘要，歷史產物 | `git rm` |
| `2025-09-26_community_digest.md` | 舊社群摘要，歷史產物 | `git rm` |
| `avery_notion_20250924_081212.md` | 個人測試產物 | `git rm` |
| `memory_insights_summary.md` | 記憶摘要，已無用途 | `git rm` |

---

## 📦 移動清單

### 5. 日報 HTML → `archive/`（~137 個）

| 來源 | 目的 | 理由 |
|------|------|------|
| 根目錄 `YYYY-MM-DD.html`（135+ 個） | `archive/YYYY-MM-DD.html` | 保留歷史但清理根目錄 |
| `dashboard.html` | `archive/dashboard.html` | 舊 dashboard 頁面 |
| `test_secret_entrance.html` | `archive/test_secret_entrance.html` | 測試用 HTML |

> ⚠️ 注意：移動後需確認 GitHub Pages 路由是否受影響。
> index.html 中的日報連結可能需要更新（指向 `archive/`）。

---

## 🔧 修改清單

### 6. .gitignore 更新

新增以下規則：

```
*.log
__pycache__/
.env
*.pyc
.DS_Store
```

### 7. requirements.txt 審查

需比對實際 import 與 requirements.txt，移除不使用的依賴。

---

## ✅ 保留清單（確認不動）

| 檔案 | 理由 |
|------|------|
| `thinker_secret_entrance.js` | 被 ai_processor.py + html_generator.py 引用 |
| `email_subscription_handler.js` | 被 html_generator.py + index.html 引用 |
| `execution_log.json` | 被 scripts/main.py + execution_logger.py 活躍使用 |
| `latest.json` | LINE bot 讀取，每日更新 |
| `index.html` | 首頁，活躍 |
| `requirements.txt` | 依賴清單（待審查但保留） |
| `.env.example` | 環境變數範本 |
| `README.md` | 需更新但保留（PHASE_4） |
| `OVERVIEW.md` | PHASE_4 整理 |
| `DEPLOYMENT.md` | PHASE_4 整理 |
| `private/thinker_panel.html` | 管理面板 |

### OpenClaw 相關（絕對不動）

- `AGENTS.md`, `BOOTSTRAP.md`, `HEARTBEAT.md`, `IDENTITY.md`
- `SOUL.md`, `TOOLS.md`, `USER.md`, `MEMORY.md`
- `REFACTOR_STATE.md`, `ARCHITECTURE.md`, `REPO_INVENTORY.md`

---

## 📊 清理統計

| 類別 | 數量 | 預計釋放 |
|------|------|----------|
| 刪除廢棄 .py | 9 | ~3000 行 |
| 刪除 Vercel/n8n | 3 | ~200 行 |
| 刪除廢棄文字/日誌 | 5 | 雜檔 |
| 刪除廢棄 Markdown | 4 | 雜檔 |
| 移動日報 HTML | ~137 | 清理根目錄 |
| **總計待處理** | **~158 個檔案** | |

---

## 🚦 執行順序建議

1. ~~PHASE_0: 產出此清單~~（本輪完成）
2. PHASE_1 Round 1: 建立 `archive/` 並移動日報 HTML
3. PHASE_1 Round 2: 刪除 9 個廢棄 .py
4. PHASE_1 Round 3: 刪除 Vercel/n8n 殘留
5. PHASE_1 Round 4: 刪除廢棄 .txt/.log/.md
6. PHASE_1 Round 5: 更新 .gitignore
7. PHASE_1 Round 6: 審查 requirements.txt
