# HLAIChat 管理平台

這是一個用於管理各種 AI 聊天流程對話網址的平台，可以依據使用者所屬群組，分配可以使用的聊天網址。

## 專案目標

本專案旨在創建一個管理平台，管理各個不同用途目的 AI 聊天流程對話網址，並依使用者所屬群組，分配可以使用的聊天網址。具有以下特點：

1. **AD 網域驗證登入**：支援 AD 網域驗證登入，管理者可以搜尋 AD 使用者，並加入選定的平台群組。
2. **平台內建帳號登入**：支援平台內建帳號登入，管理者可以管理平台使用者帳號。
3. **平台群組管理**：管理者可以管理平台群組，設定群組權限。
4. **憑證管理**：管理者可以管理 API 憑證，用於連接 n8n 或 Flowise 等外部服務。
5. **AI 聊天流程對話網址管理**：管理者可以管理 AI 聊天流程對話網址，指派群組可以使用的連結。支援多種類型：
   - **n8n Host Chat**：完整的 n8n 聊天網頁
   - **n8n Embedded Chat**：可嵌入的 n8n 聊天組件
   - **n8n Webhook**：透過 webhook 觸發的 n8n 流程，提供仿 ChatGPT 介面
   - **Flowise Chat**：預留支援 Flowise 聊天流程（未來功能）
6. **仿 ChatGPT 聊天介面**：提供使用者友善的聊天介面，支援 webhook trigger workflow 整合。
7. **操作紀錄**：記錄使用者的操作，提供管理者查詢分析。

## 技術架構

### 後端

- **框架**：FastAPI
- **ORM**：SQLAlchemy
- **資料驗證**：Pydantic
- **資料庫**：PostgreSQL
- **認證**：JWT Token
- **AD 整合**：LDAP3

### 前端

- **框架**：Vue.js 3
- **UI 元件**：Vuetify 3
- **路由**：Vue Router
- **HTTP 請求**：Axios
- **圖標**：Font Awesome 6 和 Material Design Icons
- **構建工具**：Vite
- **圖示與 Logo**：使用翰林雲端 Logo 作為網站圖示，支援各種尺寸的 favicon

## 專案結構

```
hlaichat-py/
├── backend/                # 後端程式碼
│   ├── app/                # 應用程式主目錄
│   │   ├── apis/           # API 路由
│   │   ├── core/           # 核心功能
│   │   ├── db/             # 資料庫相關
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── services/       # 業務邏輯服務
│   │   └── main.py         # 應用程式入口點
│   ├── requirements.txt    # Python 套件依賴
│   └── run.py              # 啟動腳本
├── frontend/               # 前端程式碼
│   ├── public/             # 靜態資源
│   │   ├── icons/          # 網站圖示
│   │   │   ├── apple-touch-icon.png     # iOS 裝置圖示
│   │   │   ├── favicon-16x16.png        # 16x16 圖示
│   │   │   ├── favicon-32x32.png        # 32x32 圖示
│   │   │   ├── android-chrome-192x192.png  # Android 圖示
│   │   │   └── android-chrome-512x512.png  # Android 大圖示
│   │   ├── favicon.ico     # 網站圖示
│   │   ├── logo.png        # 網站 Logo
│   │   └── site.webmanifest # PWA 網站資訊
│   ├── src/                # 源代碼
│   │   ├── assets/         # 靜態資源
│   │   ├── components/     # 組件
│   │   ├── router/         # 路由配置
│   │   ├── views/          # 視圖
│   │   │   ├── admin/      # 管理員視圖
│   │   │   └── user/       # 使用者視圖
│   │   ├── App.vue         # 根組件
│   │   └── main.js         # 入口文件
│   ├── index.html          # HTML 模板
│   ├── package.json        # 依賴配置
│   └── vite.config.js      # Vite 配置
├── preview-frontend/       # 前端原型
├── .env                    # 環境變數
├── README.md               # 專案說明
└── CHANGELOG.md            # 修改歷程
```

## 安裝與執行

### 後端

1. 安裝 Python 套件：

```bash
cd backend
pip install -r requirements.txt
```

2. 設定環境變數：

可以使用專案提供的腳本自動生成環境變數檔案：

```powershell
./setup_env.ps1
```

或手動編輯 `.env` 文件，設定資料庫連線字串和其他參數。**注意：請確保使用 UTF-8 編碼儲存此檔案，避免中文字符顯示亂碼。**

```
# 資料庫連線設定
DATABASE_URL=postgresql://postgres:hl69382361@192.168.1.221:5432/hlaichat-py

# 應用程式設定
APP_NAME=HLAIChat
SECRET_KEY=your_secret_key
DEBUG=True
HOST=0.0.0.0
PORT=8000
RELOAD=True
ACCESS_TOKEN_EXPIRE_MINUTES=60

# AD 網域設定 (若未設定，則不啟用AD驗證)
AD_DOMAIN_NAME=hanlin.com.tw
AD_PRIMARY_DC=192.168.1.6
AD_SECONDARY_DCS=192.168.1.5,192.168.5.5
AD_BIND_USERNAME=
AD_BIND_PASSWORD=

# 前端設定
VITE_API_BASE_URL=http://localhost:8000

# 時區設定 (台北時間)
TIMEZONE=Asia/Taipei
```

3. 初始化資料庫：

首次安裝或更新後，需要執行資料庫初始化或遷移：

```bash
# 初始化資料庫（首次安裝）
python init_db.py

# 或執行資料庫遷移（更新現有資料庫）
python migrate_db.py

# 建立聊天相關表格（新功能）
python migrate_chat_tables.py

# 更新聊天連結類型（重要：支援未來 Flowise 整合）
python migrate_chat_link_types.py

# 驗證類型系統正確性（可選）
python test_chat_link_types.py
```

資料庫遷移腳本會自動：
- 檢查並建立缺少的表格
- 新增缺少的欄位
- 建立必要的索引和外鍵約束
- 確保資料庫結構與程式碼模型一致
- 建立聊天會話和訊息相關表格

4. 啟動後端服務：

在 Windows PowerShell 中：
```powershell
cd backend
python -m app.main
```

在 Linux/macOS 中：
```bash
cd backend
python -m app.main
```

### 前端

1. 安裝 Node.js 套件：

```bash
cd frontend
npm install
```

2. 啟動開發伺服器：

```bash
npm run dev
```

3. 構建生產版本：

```bash
npm run build
```

## 聊天連結類型系統

### 類型命名規範

為了支援未來的 Flowise 整合並避免混淆，本專案採用明確的類型命名系統：

| 類型名稱 | 說明 | 用途 |
|---------|------|------|
| `n8n_host_chat` | n8n Host Chat | 完整的 n8n 聊天網頁 |
| `n8n_embedded_chat` | n8n Embedded Chat | 可嵌入的 n8n 聊天組件 |
| `n8n_webhook` | n8n Webhook | 透過 webhook 觸發的 n8n 流程 |
| `flowise_chat` | Flowise Chat | 預留給 Flowise 聊天流程（未來功能） |

### 類型遷移

如果您從舊版本升級，系統會自動將舊的類型名稱遷移到新格式：

- `host_chat` → `n8n_host_chat`
- `embedded_chat` → `n8n_embedded_chat`
- `webhook` → `n8n_webhook`

執行遷移腳本：
```bash
python migrate_chat_link_types.py
```

### 擴展性設計

這個類型系統的設計考慮了未來的擴展需求：

1. **平台區分**：明確區分不同 AI 平台（n8n、Flowise 等）
2. **功能區分**：在同一平台內區分不同的使用方式
3. **向後相容**：提供自動遷移機制，確保現有資料不受影響
4. **未來準備**：預留空間支援新的 AI 平台和功能

### 測試驗證

執行類型系統測試腳本驗證系統正確性：
```bash
python test_chat_link_types.py
```

測試腳本會驗證：
- 所有聊天連結類型符合新的命名規範
- 資料庫結構完整性（webhook_url 和 credential_id 欄位）
- API 類型驗證邏輯正確性
- 舊格式類型被正確拒絕

## 重要設定

### CORS 設定

後端已配置 CORS 設定，允許以下來源訪問 API：
- http://localhost:5173
- http://localhost:3000
- http://127.0.0.1:5173
- http://127.0.0.1:3000

如需添加其他來源，請修改 `backend/app/main.py` 中的 `allow_origins` 參數。

### Token 處理

前端使用 localStorage 存儲 JWT token，並在每次請求時添加到請求頭中。Token 處理邏輯包括：
- 檢查 token 是否存在
- 驗證 token 是否過期
- 處理認證錯誤 (401) 和權限錯誤 (403)

### 錯誤處理

前端已配置全局錯誤處理邏輯，會在控制台輸出詳細的錯誤訊息，並根據錯誤類型執行相應操作：
- 認證錯誤：重定向到登入頁面
- 權限錯誤：顯示權限不足訊息
- 伺服器錯誤：顯示伺服器錯誤訊息
- 網路錯誤：提示檢查網路連線

## API 文件

啟動後端服務後，可以在瀏覽器中訪問 Swagger UI 文件：

```
http://localhost:8000/docs
```

## 功能說明

### 已完成

- 後端 API 開發 (2025-05-07)
  - 使用者管理 API
  - 群組管理 API
  - 聊天連結管理 API
  - AD 設定 API
  - 操作紀錄 API
  - 認證與授權機制
- 憑證管理功能開發 (2025-05-23)
  - 憑證管理 API，包含完整的 CRUD 操作
  - 前端憑證管理介面，支援新增、編輯、刪除憑證
  - API Key 顯示/隱藏和複製功能
  - 憑證與聊天連結的關聯管理
  - 完整的操作日誌記錄
  - 資料庫遷移腳本，確保資料庫結構一致性
- 前端介面開發 (2025-05-14)
  - 管理員介面
  - 使用者介面
  - 前後端整合

### 使用者管理

- 建立、編輯、刪除使用者
- 設定使用者群組
  - 透過直觀的界面選擇使用者所屬群組
  - 搜尋群組功能，便於從大量群組中找到特定群組
  - 清晰顯示群組權限資訊，幫助管理者了解每個群組的權限
  - 已選擇群組的視覺摘要，一目了然查看已選擇的群組
  - 一鍵清除所有選擇功能，便於重新選擇
- 變更使用者密碼
- 支援平台內建帳號和 AD 帳號

### 群組管理

- 建立、編輯、刪除群組
- 設定群組權限
- 指派使用者到群組
  - 直觀的成員管理界面，清晰顯示群組中的成員
  - 篩選功能，可快速查看所有用戶、成員或非成員
  - 批量操作功能，可一次性加入或移除多個使用者
  - 使用直觀的按鈕進行成員切換，提供更好的視覺反饋
  - 實時顯示成員數量和操作狀態
  - 重新整理功能，便於獲取最新使用者資訊
- 指派聊天連結到群組

### 聊天連結管理

- 建立、編輯、刪除聊天連結
- 支援多種聊天連結類型：
  - **n8n Host Chat**：完整的 n8n 聊天網頁，直接開啟 n8n 提供的聊天介面
  - **n8n Embedded Chat**：可嵌入的 n8n 聊天組件，提供嵌入代碼供其他網站使用
  - **n8n Webhook**：透過 webhook 觸發的 n8n 流程，提供仿 ChatGPT 的聊天介面
  - **Flowise Chat**：預留支援 Flowise 聊天流程（未來功能）
- 指派群組可以使用的聊天連結
- **✅ 已完成**：為 webhook 類型連結配置 API 憑證（可從憑證管理中選擇）
- 支援聊天會話管理和訊息歷程記錄（webhook 類型）

### AD 設定

- 設定 AD 連線參數
- 測試 AD 連線
- 搜尋 AD 使用者

### 操作紀錄

- 查詢使用者操作紀錄
- 依日期、使用者、操作類型等條件搜尋

### 憑證管理

- 建立、編輯、刪除 API 憑證
- API Key 顯示/隱藏和複製功能
- 憑證與聊天連結的關聯管理
- **✅ 已完成**：在新增 webhook 類型聊天連結時可選擇預設的憑證
- 完整的操作日誌記錄

## 預設帳號

系統初始化時會自動建立預設管理員帳號：

- 使用者名稱：admin
- 密碼：admin
- 群組：admins (具有完整管理權限)

## 常見問題排解

### AD 登入功能問題

如果在登入頁面中，AD 帳號標籤無法點擊，可能是因為以下原因：

1. 前端未能正確處理 AD 設定狀態的 API 回應
2. 後端 AD 設定狀態 API 返回的資料結構與前端預期不符

解決方法：
- 我們已修正此問題，移除了 AD 標籤的 disabled 屬性，使 AD 標籤始終可點擊
- 修正了 onMounted 函數中獲取 AD 設定狀態的程式碼，確保正確處理 API 回應
- 確保 AD 登入功能不受 AD 設定狀態的影響，提高使用者體驗

### 群組成員管理問題

如果在群組管理頁面中，點擊「管理成員」後成員列表為空，但實際上該群組應該有成員，可能是因為以下原因：

1. 使用者數量超過了 API 的分頁限制
2. 資料不一致問題

解決方法：
- 刷新頁面後重試
- 檢查瀏覽器控制台是否有 422 錯誤
- 如果問題持續，可以嘗試重啟後端服務

### CORS 錯誤

如果遇到 CORS 錯誤，請確認：
1. 前端訪問的 URL 是否在後端的 `allow_origins` 列表中
2. 後端服務是否正常運行
3. 前端請求是否包含正確的 `withCredentials` 設定

### 資料庫連接錯誤

如果遇到資料庫連接錯誤，請確認：
1. PostgreSQL 服務是否正在運行
2. 資料庫連線字串是否正確
3. 資料庫使用者是否有足夠的權限

### 資料庫結構不一致錯誤

如果遇到類似以下的資料庫欄位錯誤：
```
(psycopg2.errors.UndefinedColumn) column chat_links.webhook_url does not exist
```

這表示資料庫結構與程式碼模型不一致，解決方法：

1. 執行資料庫遷移腳本：
```bash
cd backend
python migrate_db.py
```

2. 如果遷移失敗，可以嘗試重新初始化資料庫：
```bash
python init_db.py
```

3. 檢查遷移結果：
遷移腳本會自動檢查並報告：
- 缺少的表格和欄位
- 需要建立的索引和約束
- 遷移的執行結果

常見的資料庫結構問題：
- `chat_links` 表缺少 `webhook_url` 或 `credential_id` 欄位
- `credentials` 表不存在
- 外鍵約束缺失

### 憑證管理 API 錯誤

如果在憑證管理頁面遇到 500 內部伺服器錯誤，可能的原因和解決方法：

1. **服務類別方法調用錯誤**：
   - 確認 CredentialService 類別使用實例方法而非靜態方法
   - 檢查服務類別是否正確初始化並接受資料庫 session

2. **資料庫結構問題**：
   - 執行資料庫遷移腳本：`python migrate_db.py`
   - 確認 credentials 表已正確建立

3. **前端依賴問題**：
   - 確認已安裝 lodash-es 套件：`npm install lodash-es`
   - 檢查前端控制台是否有導入錯誤

4. **權限問題**：
   - 確認使用管理員帳號登入
   - 檢查使用者是否屬於具有管理權限的群組

### 聊天功能問題

#### n8n Webhook 回應解析錯誤

如果在聊天介面中收到錯誤訊息，如 "發生未知錯誤: Expecting value: line 1 column 1 (char 0)"，這通常是由於 webhook 回應格式解析問題導致的。

**常見原因和解決方法**：

1. **n8n "Respond to Webhook" 節點回應格式**：
   - n8n 的 "Respond to Webhook" 節點通常使用 `output` 欄位而非 `message` 欄位
   - 系統已優化支援多種回應格式：`output`、`message`、`text`、`content`

2. **JSON 解析錯誤**：
   - 檢查 n8n workflow 是否正確設定 "Respond to Webhook" 節點
   - 確認回應內容是有效的 JSON 格式
   - 系統會自動處理非 JSON 格式的回應，將原始文字作為回應內容

3. **除錯方法**：
   - 查看後端控制台日誌，會顯示詳細的 webhook 回應內容
   - 檢查 n8n 執行歷程，確認 workflow 正常完成
   - 驗證 webhook URL 和 API Key 設定正確

4. **測試建議**：
   - 先使用簡單的文字回應測試 webhook 連接
   - 確認 n8n workflow 的 "Respond to Webhook" 節點設定正確
   - 檢查網路連線和防火牆設定

### 其他常見問題

### 環境變數問題

#### .env 檔案中文亂碼

如果 `.env` 檔案中的中文字符顯示亂碼，這通常是由於檔案編碼格式不正確導致的。解決方法：

**方法一：使用專案提供的腳本重新建立**
```powershell
# 執行環境變數設定腳本（推薦）
.\setup_env.ps1
```

**方法二：手動修復編碼**
```powershell
# 備份現有檔案
Copy-Item .env .env.backup

# 使用 UTF-8 編碼重新建立檔案
Get-Content -Encoding utf8 .env | Out-File -Encoding utf8 .env.new
Move-Item -Force .env.new .env
```

**方法三：從範本重新建立**
```powershell
# 從範本檔案重新建立 .env 檔案
Get-Content env-template.txt -Encoding UTF8 | Out-File -FilePath .env -Encoding UTF8
```

**驗證修復結果**
```powershell
# 檢查檔案是否正確顯示中文
Get-Content .env -Encoding UTF8
```

如果修復後仍有問題，請確認：
1. 檔案確實使用 UTF-8 編碼儲存
2. 包含所有必要的環境變數參數
3. 中文註解能正確顯示

### 專案清理

如果需要清理專案中的暫存檔案，可以執行以下命令：

```powershell
# 移除 Python 編譯緩存檔案
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force

# 移除其他臨時檔案
Get-ChildItem -Path . -Include "*.pyc", "*.pyo", "*.bak", "*.swp", "*.tmp", "*.log" -Recurse -Force | Remove-Item -Force
```

注意：請勿刪除 `preview-frontend` 目錄，該目錄包含前端原型設計及介面，用於日後參考。

## 授權

本專案為內部使用，未經授權不得外流。

## AD功能使用須知

### AD使用者搜尋

搜尋AD使用者時，系統會安全處理AD返回的objectGUID屬性。由於不同AD設定可能返回不同類型的GUID值，系統現已能夠處理以下情況：

1. 當objectGUID為二進位物件時，系統會使用`.hex()`方法轉換為字串
2. 當objectGUID直接為字串時，系統會直接使用該字串值
3. 若無法獲取objectGUID，系統會使用空字串作為預設值

這樣的處理邏輯確保了系統能夠適應不同AD環境的配置，提高了系統的穩定性和兼容性。

### AD使用者加入平台

將AD使用者加入平台群組時，由於系統模型設計，資料庫中的使用者表格要求密碼欄位不能為空。但AD使用者實際上不需要本地密碼，因為他們使用AD認證登入。為解決這個問題：

1. 系統會在將AD使用者加入平台時自動生成一個隨機密碼
2. 此密碼僅用於滿足資料庫模型要求，實際不會被使用
3. AD使用者將始終透過AD認證進行登入，不需記住或使用此隨機密碼

此解決方案確保AD使用者可以被成功添加到平台，同時保持數據模型的完整性，避免出現「Field required: password」的錯誤。

# 環境變數設定

本專案採用單一 `.env` 檔案管理所有環境變數，包括後端和前端共用的設定。這樣可以簡化設定流程，確保配置的一致性。

- **後端**：通過以下方式處理環境變數
  - 在 `run.py` 中使用 `python-dotenv` 套件讀取根目錄的 `.env` 檔案
  - 在 `config.py` 中使用 `pydantic-settings` 套件讀取環境變數，並設定 `extra = "ignore"` 允許額外的前端環境變數
- **前端**：通過 Vite 的配置 (`vite.config.js`)，設定 `envDir` 指向根目錄，使前端也能讀取同一個 `.env` 檔案

可以使用專案提供的腳本自動生成環境變數檔案：

```powershell
./setup_env.ps1
```

`.env` 檔案包含以下環境變數：

```
# 應用程式設定
APP_NAME=HLAIChat
SECRET_KEY=your_secret_key
DEBUG=True
HOST=0.0.0.0
PORT=8000
RELOAD=True
ACCESS_TOKEN_EXPIRE_MINUTES=60

# 資料庫設定
DATABASE_URL=postgresql://postgres:hl69382361@192.168.1.221:5432/hlaichat-py

# AD 網域設定 (若未設定，則不啟用AD驗證)
AD_DOMAIN_NAME=hanlin.com.tw
AD_PRIMARY_DC=192.168.1.6
AD_SECONDARY_DCS=192.168.1.5,192.168.5.5
AD_BIND_USERNAME=
AD_BIND_PASSWORD=

# 前端設定
VITE_API_BASE_URL=http://localhost:8000

# 時區設定 (台北時間)
TIMEZONE=Asia/Taipei

# 聊天功能逾時設定 (秒)
CHAT_WEBHOOK_TIMEOUT=300
CHAT_REQUEST_TIMEOUT=300
CHAT_CONNECTION_TIMEOUT=60

# 前端聊天逾時設定 (毫秒)
VITE_CHAT_TIMEOUT=300000
```

> **注意**：請確保 `.env` 檔案使用正確的編碼儲存，避免中文字符顯示亂碼。
> 
> **聊天逾時設定**：如需調整聊天功能的逾時時間，請參考 `CHAT_TIMEOUT_CONFIGURATION.md` 文件的詳細說明。

## 最新更新

- **2025-05-27**: n8n Webhook 回應解析問題修復
  - **問題解決**：修復聊天介面顯示 "發生未知錯誤: Expecting value: line 1 column 1 (char 0)" 的問題
  - **回應格式支援**：優化 webhook 回應處理邏輯，支援多種回應格式（`output`、`message`、`text`、`content`）
  - **除錯增強**：新增詳細的 webhook 回應日誌記錄，包含原始回應內容、狀態碼和標頭資訊
  - **錯誤處理改善**：改善 JSON 解析錯誤處理，當無法解析 JSON 時將原始文字作為回應內容
  - **故障排除文件**：更新 README.md 和測試文件，新增 webhook 回應解析問題的解決方案
- **2025-05-27**: 聊天逾時設定優化與環境變數修復
  - **逾時設定優化**：將所有聊天相關的逾時參數移至 `.env` 檔案統一管理
  - 新增後端逾時參數：`CHAT_WEBHOOK_TIMEOUT`、`CHAT_REQUEST_TIMEOUT`、`CHAT_CONNECTION_TIMEOUT`
  - 新增前端逾時參數：`VITE_CHAT_TIMEOUT`
  - 修改後端和前端程式碼使用環境變數中的逾時設定，取代硬編碼的逾時值
  - 建立詳細的逾時設定說明文件 `CHAT_TIMEOUT_CONFIGURATION.md`
  - **環境變數修復**：修復 `.env` 檔案中文亂碼問題，使用 UTF-8 編碼重新建立檔案
  - 改進 README.md 中的編碼問題說明，提供多種解決方案和驗證方法
  - 確保 n8n workflow 有足夠時間處理複雜的 AI 請求
- **2025-05-26**: 專案清理和結構優化
  - 移除冗餘檔案：Python 編譯快取、重複的遷移腳本、重複的文件
  - 移除 `.gitignore` 檔案，避免妨礙開發中的讀寫動作
  - 保留除錯用的 console.log 語句以利日後維護
  - 確保專案結構簡潔但功能完整，符合開發指引要求
- **2025-05-24**: 聊天連結類型重構，支援未來 Flowise 整合
  - 重新設計類型命名系統：`host_chat` → `n8n_host_chat`、`embedded_chat` → `n8n_embedded_chat`、`webhook` → `n8n_webhook`
  - 建立資料庫遷移腳本 `migrate_chat_link_types.py`，成功更新 2 個現有聊天連結
  - 建立測試腳本 `test_chat_link_types.py` 驗證系統正確性
  - 更新前後端所有相關的類型檢查和顯示邏輯
  - 更新測試功能文件，新增類型系統測試指引
- **2025-05-24**: 完善 webhook trigger workflow 仿 ChatGPT 聊天介面設計
  - 新增聊天會話和訊息資料模型，建立完整的聊天功能
  - 實作聊天服務類別，支援會話管理和 webhook 整合
  - 建立仿 ChatGPT 的前端聊天介面組件
  - 支援多會話管理、訊息歷程記錄和即時對話
- **2025-05-23**: 修復憑證服務類別的方法調用問題，確保憑證管理功能完全正常運作
- **2025-05-23**: 修復資料庫結構不一致問題，建立資料庫遷移腳本自動檢查並新增缺少的欄位
- **2025-05-23**: 修復前端依賴問題，安裝缺少的 lodash-es 套件，解決 Credentials.vue 中的導入錯誤
- **2025-05-23**: 完成憑證管理功能開發，包含後端 API 和前端管理介面
- **2025-05-22**: 修復AD使用者加入平台群組時出現「Field required: password」錯誤，為AD使用者自動生成隨機密碼
- **2025-05-21**: 修復 AD 帳號登入功能無法被點擊使用的問題，確保 AD 登入功能不受 AD 設定狀態的影響
- **2025-05-18**: 在 main.js 中引入 Material Design Icons (MDI) 的 CSS 文件，修正不顯示圖示的問題
- **2025-05-18**: 升級功能圖示，使用更具代表性的圖示並優化展示效果，使側邊欄收合時清晰顯示圖示
- **2025-05-18**: 修正側邊欄收合後功能圖示不顯示的問題，移除 v-list-item 的 prepend-icon 屬性，改用 v-slot:prepend 顯示圖示
- **2025-05-17**: 修復後端啟動時的驗證錯誤，在 Settings.Config 中設定 extra = "ignore" 允許額外的環境變數
- **2025-05-17**: 整合多個 .env 檔案為一個，修改 run.py 和 config.py 以指向根目錄的 .env 檔案
- **2025-05-17**: 整合環境變數設定到單一 .env 檔案，修改 vite.config.js 使前端從根目錄讀取環境變數
