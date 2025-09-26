# 📡 n8n 工作流程整合指南

## 🎯 目標
將你現有的 n8n 新聞工作流程與本地發布系統整合，實現：
- n8n 完成處理後自動回調本地系統
- 本地系統接收內容並自動發布到 GitHub Pages
- 完整的錯誤處理與日誌記錄

## 🔧 當前設置

### Webhook 服務資訊
- **服務 URL**: `https://voted-irrigation-sega-hills.trycloudflare.com`
- **回調端點**: `/webhook/n8n/news-complete`
- **認證方式**: Bearer Token
- **安全密鑰**: `thinker-cafe-secret-2025`

### 完整回調 URL
```
https://voted-irrigation-sega-hills.trycloudflare.com/webhook/n8n/news-complete
```

## 📝 n8n 工作流程修改步驟

### 步驟 1: 修改「組裝」節點後的設定

將你現有的 `Respond to Webhook` 節點，修改為 `HTTP Request` 節點：

**節點配置:**
```json
{
  "node": "HTTP Request",
  "method": "POST",
  "url": "https://voted-irrigation-sega-hills.trycloudflare.com/webhook/n8n/news-complete",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer thinker-cafe-secret-2025"
  },
  "body": "{{ JSON.stringify($json) }}"
}
```

### 步驟 2: 具體節點設定截圖

**HTTP Request 節點設定:**

1. **基本設定**
   - Method: `POST`
   - URL: `https://voted-irrigation-sega-hills.trycloudflare.com/webhook/n8n/news-complete`

2. **Headers 設定**
   ```
   Name: Content-Type       Value: application/json
   Name: Authorization      Value: Bearer thinker-cafe-secret-2025
   ```

3. **Body 設定**
   - Body Type: `JSON`
   - Body Content: `{{ JSON.stringify($json) }}`

### 步驟 3: 連線設定

將工作流程最後的連線修改為：
```
組裝節點 → HTTP Request 節點 → (結束)
```

移除原本的 `Respond to Webhook` 節點。

## 📋 期望的資料格式

你的「組裝」節點應該輸出以下格式的資料：

```json
{
  "final_date": "2025-09-26",
  "notion_version_for_storage": "完整的新聞內容...",
  "line_version_for_publishing": "LINE版本內容..."
}
```

## ✅ 測試流程

### 1. 測試 Webhook 連通性
```bash
curl -X GET "https://voted-irrigation-sega-hills.trycloudflare.com/health"
```

### 2. 測試認證機制
```bash
curl -X POST "https://voted-irrigation-sega-hills.trycloudflare.com/webhook/test" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer thinker-cafe-secret-2025" \
     -d '{"test": "data"}'
```

### 3. 手動測試 n8n 回調
在 n8n 中手動執行工作流程，檢查是否成功呼叫本地系統。

## 🔍 完整工作流程

1. **你觸發 n8n**：手動執行或定時觸發
2. **n8n 處理**：數據煉金術師 → 科技導讀人 → 總編輯 → 組裝
3. **n8n 回調**：HTTP Request 節點將結果發送到本地系統
4. **本地處理**：
   - 接收並保存 markdown 內容
   - 使用 Gemini Layout Agent 生成 HTML
   - 更新首頁
   - 提交並推送到 GitHub
5. **完成發布**：網站自動更新

## 📊 監控與除錯

### 檢查本地服務狀態
```bash
curl -X GET "https://voted-irrigation-sega-hills.trycloudflare.com/"
```

### 查看服務日誌
本地系統會記錄所有操作到 `unified_webhook.log` 檔案。

### 常見問題排解

**問題 1**: n8n 顯示 HTTP Request 失敗
- 檢查 URL 是否正確
- 確認 Authorization header 格式正確
- 檢查本地服務是否正常運行

**問題 2**: 內容接收但未發布
- 檢查本地日誌檔案
- 確認 GitHub 權限正常
- 驗證 Gemini API 金鑰有效

**問題 3**: Cloudflare Tunnel 斷線
- 重新執行 `cloudflared tunnel --url http://localhost:5002`
- 更新 n8n 中的 URL

## 🚀 下一步行動

1. **立即行動**: 修改你的 n8n 工作流程，加入 HTTP Request 節點
2. **測試驗證**: 手動執行一次，確認整個流程正常
3. **設定定時**: 配置每日自動觸發（如果需要）
4. **監控設定**: 定期檢查服務狀態

---

## 📞 支援資訊

如遇問題，可檢查：
1. 本地 `unified_webhook.log` 檔案
2. n8n 執行歷史記錄
3. GitHub Pages 部署狀態

**設定完成後，你的新聞發布流程將完全自動化！** 🎉