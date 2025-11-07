# 快速部署指南

## 🚀 30分鐘完成遷移

### 步驟 1: 準備工作（5分鐘）

1. **確認你有以下 API Keys**
   - [ ] Google Gemini API Key
   - [ ] OpenAI API Key
   - [ ] Slack Webhook URL（選填）

2. **確認 GitHub Repo 權限**
   - [ ] thinker-news repo 的寫入權限
   - [ ] 可以設置 GitHub Secrets

### 步驟 2: 複製文件（5分鐘）

```bash
# 1. 進入你的 thinker-news repo
cd /path/to/thinker-news

# 2. 創建必要目錄
mkdir -p .github/workflows
mkdir -p scripts

# 3. 從自動化項目複製文件
cp /Users/thinkercafe/Desktop/thinker-news-automation/.github/workflows/daily-news.yml .github/workflows/
cp /Users/thinkercafe/Desktop/thinker-news-automation/scripts/*.py scripts/
cp /Users/thinkercafe/Desktop/thinker-news-automation/requirements.txt .
cp /Users/thinkercafe/Desktop/thinker-news-automation/.gitignore .

# 4. 提交到 Git
git add .
git commit -m "🤖 遷移: n8n → GitHub Actions"
git push
```

### 步驟 3: 設置 GitHub Secrets（5分鐘）

1. 前往: `https://github.com/ThinkerCafe-tw/thinker-news/settings/secrets/actions`

2. 點擊 "New repository secret" 添加以下 secrets：

   - **Name**: `GOOGLE_API_KEY`  
     **Value**: `你的 Gemini API Key`

   - **Name**: `OPENAI_API_KEY`  
     **Value**: `你的 OpenAI API Key`

   - **Name**: `SLACK_WEBHOOK_URL`  
     **Value**: `你的 Slack Webhook URL`

### 步驟 4: 測試運行（10分鐘）

1. **手動觸發 workflow**
   - 前往: `https://github.com/ThinkerCafe-tw/thinker-news/actions`
   - 選擇 "每日 AI 新聞自動生成"
   - 點擊 "Run workflow"

2. **查看執行日誌**
   - 觀察每個步驟的執行情況
   - 確認無錯誤

3. **檢查輸出**
   - 確認生成了 HTML 文件
   - 確認 index.html 更新正確
   - 確認 latest.json 生成正確

### 步驟 5: 驗證與監控（5分鐘）

1. **訪問網站**
   ```
   https://thinkercafe-tw.github.io/thinker-news/
   ```

2. **檢查 Slack 通知**
   - 確認收到通知訊息

3. **設置監控**
   - 在 GitHub Actions 設置失敗通知

## ✅ 部署完成檢查清單

- [ ] 所有文件已複製到 thinker-news repo
- [ ] GitHub Secrets 已設置
- [ ] workflow 手動測試成功
- [ ] HTML 文件生成正確
- [ ] 網站訪問正常
- [ ] Slack 通知收到
- [ ] 排程設置正確（每天 06:00 UTC+8）

## 🔄 切換流程

### 停用 n8n workflow

1. 登入 n8n
2. 找到 "每日新聞" workflow
3. 點擊 "Inactive" 停用
4. **不要立即刪除**，保留作為備份

### 並行運行測試（建議）

1. 第一週：同時運行 n8n 和 GitHub Actions
2. 比對兩邊的輸出
3. 確認 GitHub Actions 版本穩定後
4. 完全停用 n8n

### 完全遷移

確認 GitHub Actions 運行穩定 1 週後：
1. 停用 n8n workflow
2. 導出 n8n workflow JSON 作為備份
3. 慶祝遷移成功！ 🎉

## 🐛 常見問題排查

### 問題 1: workflow 無法觸發

**症狀**: Actions 頁面看不到任何執行記錄

**解決方案**:
```bash
# 檢查 workflow 文件路徑
ls -la .github/workflows/daily-news.yml

# 確認文件格式正確
cat .github/workflows/daily-news.yml
```

### 問題 2: API 調用失敗

**症狀**: 日誌顯示 API 錯誤

**解決方案**:
1. 檢查 Secrets 是否設置正確
2. 確認 API Keys 沒有過期
3. 檢查 API 配額

### 問題 3: 篩選結果為空

**症狀**: 日誌顯示 "沒有新聞通過篩選"

**解決方案**:
1. 檢查 RSS 源是否正常
2. 調整篩選邏輯的評分閾值
3. 手動測試日期計算邏輯

### 問題 4: HTML 生成失敗

**症狀**: 沒有生成 HTML 文件

**解決方案**:
1. 檢查模板語法
2. 確認數據格式正確
3. 查看詳細錯誤日誌

## 📞 需要幫助？

如果遇到無法解決的問題：

1. **查看詳細日誌**
   - GitHub Actions 頁面有完整的執行日誌

2. **本地測試**
   ```bash
   # 設置環境變數後本地運行
   python scripts/main.py
   ```

3. **聯繫開發者**
   - 提交 GitHub Issue
   - 描述問題 + 附上日誌

## 🎓 學習資源

- [GitHub Actions 文檔](https://docs.github.com/en/actions)
- [Jinja2 模板文檔](https://jinja.palletsprojects.com/)
- [Gemini API 文檔](https://ai.google.dev/docs)
- [OpenAI API 文檔](https://platform.openai.com/docs)

---

**祝部署順利！** 🚀
