# 聊天逾時設定說明

## 概述

本文件說明如何設定和調整 HLAIChat 專案中的聊天逾時參數，確保 n8n workflow 有足夠的時間處理請求並回應。

## 環境變數設定

所有逾時參數都統一在 `.env` 檔案中設定，作為唯一的參數來源。

### 後端逾時參數 (單位：秒)

```env
# 聊天功能逾時設定 (秒)
CHAT_WEBHOOK_TIMEOUT=300      # webhook 讀取逾時 (5分鐘)
CHAT_REQUEST_TIMEOUT=300      # 請求寫入逾時 (5分鐘)
CHAT_CONNECTION_TIMEOUT=60    # 連線建立逾時 (1分鐘)
```

### 前端逾時參數 (單位：毫秒)

```env
# 前端聊天逾時設定 (毫秒)
VITE_CHAT_TIMEOUT=300000      # 前端 axios 請求逾時 (5分鐘)
```

## 參數說明

### CHAT_WEBHOOK_TIMEOUT
- **用途**: 等待 n8n webhook 回應的最大時間
- **預設值**: 300 秒 (5分鐘)
- **建議值**: 根據 n8n workflow 的複雜度調整，複雜的 AI 處理可能需要更長時間

### CHAT_REQUEST_TIMEOUT
- **用途**: 發送請求到 n8n webhook 的最大時間
- **預設值**: 300 秒 (5分鐘)
- **建議值**: 通常與 CHAT_WEBHOOK_TIMEOUT 相同

### CHAT_CONNECTION_TIMEOUT
- **用途**: 建立與 n8n webhook 連線的最大時間
- **預設值**: 60 秒 (1分鐘)
- **建議值**: 通常不需要調整，除非網路環境特殊

### VITE_CHAT_TIMEOUT
- **用途**: 前端等待後端 API 回應的最大時間
- **預設值**: 300000 毫秒 (5分鐘)
- **建議值**: 應該略大於後端的逾時設定，以確保能收到後端的錯誤回應

## 如何調整逾時設定

1. **編輯 `.env` 檔案**
   ```bash
   # 將逾時時間調整為 10 分鐘
   CHAT_WEBHOOK_TIMEOUT=600
   CHAT_REQUEST_TIMEOUT=600
   VITE_CHAT_TIMEOUT=600000
   ```

2. **重新啟動服務**
   - 後端：重新啟動 FastAPI 服務
   - 前端：重新啟動 Vite 開發服務器

## 程式碼實作位置

### 後端實作
- **設定檔**: `backend/app/core/config.py`
- **使用位置**: `backend/app/services/chat_service.py` 的 `send_message` 方法

```python
# 使用環境變數中的逾時設定
timeout_config = httpx.Timeout(
    connect=settings.CHAT_CONNECTION_TIMEOUT,
    read=settings.CHAT_WEBHOOK_TIMEOUT,
    write=settings.CHAT_REQUEST_TIMEOUT,
    pool=settings.CHAT_REQUEST_TIMEOUT
)
```

### 前端實作
- **使用位置**: `frontend/src/components/ChatInterface.vue` 的 `sendMessage` 方法

```javascript
// 使用環境變數中的逾時設定，預設為 5 分鐘
const chatTimeout = import.meta.env.VITE_CHAT_TIMEOUT || 300000
const response = await axios.post(url, data, {
  timeout: parseInt(chatTimeout)
})
```

## 錯誤處理

當發生逾時錯誤時：

1. **後端**: 會捕獲 `httpx.TimeoutException` 並儲存錯誤訊息到資料庫
2. **前端**: 會顯示錯誤訊息給使用者
3. **使用者訊息**: 即使發生逾時，使用者的訊息仍會被保存

## 建議的逾時設定值

| 使用情境 | WEBHOOK_TIMEOUT | REQUEST_TIMEOUT | VITE_CHAT_TIMEOUT |
|---------|-----------------|-----------------|-------------------|
| 簡單對話 | 60秒 | 60秒 | 60000毫秒 |
| 一般 AI 處理 | 300秒 | 300秒 | 300000毫秒 |
| 複雜 AI 處理 | 600秒 | 600秒 | 600000毫秒 |
| 無逾時限制 | 0 (不建議) | 0 (不建議) | 0 (不建議) |

## 注意事項

1. **統一來源**: 所有逾時參數都必須在 `.env` 檔案中設定，不可在程式碼中硬編碼
2. **單位一致**: 後端使用秒，前端使用毫秒
3. **合理設定**: 過長的逾時可能導致資源浪費，過短的逾時可能導致正常請求失敗
4. **環境同步**: 確保開發、測試、生產環境的逾時設定一致

## 疑難排解

### 問題：仍然出現逾時錯誤
1. 檢查 `.env` 檔案是否正確設定
2. 確認服務已重新啟動
3. 檢查 n8n workflow 的實際處理時間
4. 考慮增加逾時時間

### 問題：前端沒有讀取到環境變數
1. 確認環境變數名稱以 `VITE_` 開頭
2. 重新啟動 Vite 開發服務器
3. 檢查 `vite.config.js` 的環境變數設定

### 問題：.env 檔案中文註解顯示亂碼
1. 檢查檔案編碼是否為 UTF-8
2. 使用以下指令修復編碼問題：
   ```powershell
   # 使用專案腳本重新建立（推薦）
   .\setup_env.ps1
   
   # 或手動修復編碼
   Get-Content .env -Encoding UTF8 | Out-File -FilePath .env.new -Encoding UTF8
   Move-Item -Force .env.new .env
   ```
3. 驗證修復結果：
   ```powershell
   Get-Content .env -Encoding UTF8
   ```

## 更新歷程

- **2025-05-27**: 初始版本，將硬編碼的逾時設定移至環境變數
  - 建立完整的逾時設定架構
  - 新增後端和前端逾時設定支援
  - 建立詳細的設定說明和疑難排解指引 