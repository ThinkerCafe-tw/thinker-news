# Thinker News 自動化系統

## 📋 專案簡介

從 n8n workflow 完整遷移到 GitHub Actions 的 AI 新聞日報自動生成系統。

### 核心特點

- ✅ **完整保留** n8n 的所有邏輯（特別是台灣本地化篩選）
- 🚀 **GitHub Actions** 原生整合，無需額外伺服器
- 💰 **成本優化** 使用 GitHub 免費額度
- 📝 **版本控制** 所有代碼納入 Git 管理
- 🔧 **易於維護** 清晰的模組化架構

## 🏗️ 系統架構

```
GitHub Actions (每天 06:00 UTC+8)
  ↓
Python 主腳本 (main.py)
  ├─ RSS 讀取 (rss_fetcher.py)
  ├─ 台灣本地化篩選 (news_filter.py)
  ├─ AI 處理鏈 (ai_processor.py)
  │   ├─ 數據煉金術師 (Gemini)
  │   ├─ 科技導讀人 (OpenAI)
  │   └─ 總編輯 (OpenAI)
  ├─ HTML 生成 (html_generator.py)
  └─ Slack 通知 (notify_slack.py)
```

## 📦 安裝與設置

### 1. 克隆專案

```bash
git clone https://github.com/ThinkerCafe-tw/thinker-news.git
cd thinker-news
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 設置環境變數

在 GitHub Repo 設置以下 Secrets：

- `GOOGLE_API_KEY` - Google Gemini API Key
- `OPENAI_API_KEY` - OpenAI API Key
- `SLACK_WEBHOOK_URL` - Slack Webhook URL（選填）

### 4. 本地測試

```bash
export GOOGLE_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
python scripts/main.py
```

## 🔄 工作流程詳解

### 步驟 1: RSS 讀取

並行讀取 7 個新聞來源：
- 🇹🇼 technews.tw
- 🇹🇼 ithome.com.tw
- 🌍 TechCrunch
- 🌍 Hacker News
- 🌍 Ars Technica
- 🤖 OpenAI Blog
- 🎓 Berkeley AI Research

### 步驟 2: 台灣本地化篩選

**核心邏輯**（完全移植自 n8n Code3）：
- 智能評分系統
- 台灣視角優先
- 來源平衡策略
- 支持本地與國際新聞混合

### 步驟 3: AI 處理鏈

**三段式處理**：

1. **數據煉金術師** (Gemini)
   - 標題轉譯
   - 完整內容摘要
   - 智慧分類
   - 價值排序

2. **科技導讀人** (OpenAI)
   - 精選 8-10 則新聞
   - 撰寫完整 Notion 日報
   - 包含學習價值分析

3. **總編輯** (OpenAI)
   - 提煉 LINE 快訊
   - 智能品管
   - 清理生成痕跡

### 步驟 4: HTML 生成

使用 Jinja2 模板生成：
- 今日新聞頁面 (`YYYY-MM-DD.html`)
- 首頁 (`index.html`)
- latest.json（API 使用）

### 步驟 5: Git 提交 & 通知

- 自動 commit 到 GitHub
- 觸發 GitHub Pages 部署
- 發送 Slack 通知

## 📁 專案結構

```
thinker-news-automation/
├── .github/
│   └── workflows/
│       └── daily-news.yml          # GitHub Actions 配置
├── scripts/
│   ├── main.py                     # 主執行腳本
│   ├── rss_fetcher.py              # RSS 讀取
│   ├── news_filter.py              # 新聞篩選（台灣本地化）
│   ├── ai_processor.py             # AI 處理鏈
│   ├── html_generator.py           # HTML 生成
│   ├── utils.py                    # 工具函數
│   └── notify_slack.py             # Slack 通知
├── requirements.txt                # Python 依賴
└── README.md                       # 本文件
```

## 🎯 與 n8n 的對應關係

| n8n 節點 | Python 模組 | 說明 |
|---------|------------|-----|
| Schedule Trigger | GitHub Actions | 每天 06:00 觸發 |
| 生成今日日期 | `utils.get_taiwan_date()` | 台灣時區日期 |
| RSS Feed Read × 7 | `rss_fetcher.py` | 並行讀取 RSS |
| Code3 | `news_filter.py` | 台灣本地化篩選 |
| Merge | 自動處理 | 合併所有新聞 |
| 數據煉金術師 | `ai_processor.process_with_data_alchemist()` | Gemini API |
| 品管員#1 | `utils.validate_json_output()` | JSON 驗證 |
| 科技導讀人 | `ai_processor.process_with_tech_narrator()` | OpenAI API |
| 品管員#2 | `utils.validate_json_output()` | JSON 驗證 |
| 總編輯 | `ai_processor.process_with_editor_in_chief()` | OpenAI API |
| 品管員#3 | `utils.validate_json_output()` | JSON 驗證 |
| 組裝 | `main.py` 邏輯 | 組裝最終輸出 |
| AI Agent × 2 | `html_generator.py` | Jinja2 模板 |
| GitHub 操作 | GitHub Actions | 原生 Git 操作 |
| Slack 通知 | `notify_slack.py` | Slack Webhook |

## 🚀 部署指南

### 部署到 GitHub Actions

1. **複製文件到 thinker-news repo**

```bash
# 複製 workflow
cp .github/workflows/daily-news.yml /path/to/thinker-news/.github/workflows/

# 複製腳本
cp -r scripts/ /path/to/thinker-news/

# 複製依賴
cp requirements.txt /path/to/thinker-news/
```

2. **設置 GitHub Secrets**

在 Repo Settings → Secrets and variables → Actions 中添加：
- `GOOGLE_API_KEY`
- `OPENAI_API_KEY`
- `SLACK_WEBHOOK_URL`

3. **測試手動觸發**

在 Actions 頁面手動觸發 workflow 進行測試。

4. **啟用自動排程**

確認 workflow 中的 cron 設置正確：
```yaml
schedule:
  - cron: '0 22 * * *'  # 每天 UTC 22:00 = 台灣 06:00
```

## 🔍 除錯與監控

### 查看日誌

```bash
# 本地測試時
tail -f news_generation.log
```

### GitHub Actions 日誌

在 Actions 頁面查看每次執行的詳細日誌。

### 常見問題

**Q: RSS 讀取失敗？**
A: 檢查網路連接和 RSS 源是否可訪問。

**Q: AI API 調用失敗？**
A: 檢查 API keys 是否正確設置，並確認配額。

**Q: JSON 解析錯誤？**
A: AI 可能返回了非純 JSON，檢查品管邏輯。

## 📊 成本分析

### GitHub Actions
- 免費額度：每月 2000 分鐘
- 預計使用：每天約 5-10 分鐘
- **成本：$0**

### API 調用
- Gemini API：免費配額充足
- OpenAI API：每天約 $0.05-0.10
- **預計月成本：$1.5-3**

### 總成本
**遠低於 n8n 的任何付費方案**

## 🎨 客製化指南

### 修改篩選邏輯

編輯 `news_filter.py` 中的 `FILTERS` 配置。

### 調整 AI 提示詞

編輯 `ai_processor.py` 中的系統提示詞。

### 更改 HTML 樣式

編輯 `html_generator.py` 中的 HTML 模板。

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License

## 📮 聯繫方式

- **作者**: Cruz Tang
- **公司**: ThinkerCafe
- **GitHub**: [@ThinkerCafe-tw](https://github.com/ThinkerCafe-tw)

---

**🎉 從 n8n 到 GitHub Actions 的完美遷移！**
