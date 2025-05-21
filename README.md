# HLAIChat 管理平台

這是一個用於管理各種 AI 聊天流程對話網址的平台，可以依據使用者所屬群組，分配可以使用的聊天網址。

## 專案目標

本專案旨在創建一個管理平台，管理各個不同用途目的 AI 聊天流程對話網址，並依使用者所屬群組，分配可以使用的聊天網址。具有以下特點：

1. **AD 網域驗證登入**：支援 AD 網域驗證登入，管理者可以搜尋 AD 使用者，並加入選定的平台群組。
2. **平台內建帳號登入**：支援平台內建帳號登入，管理者可以管理平台使用者帳號。
3. **平台群組管理**：管理者可以管理平台群組，設定群組權限。
4. **AI 聊天流程對話網址管理**：管理者可以管理 AI 聊天流程對話網址，指派群組可以使用的連結。
5. **操作紀錄**：記錄使用者的操作，提供管理者查詢分析。

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

3. 啟動後端服務：

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
- 設定聊天連結類型 (Hosted 或 Embedded)
- 指派群組可以使用的聊天連結

### AD 設定

- 設定 AD 連線參數
- 測試 AD 連線
- 搜尋 AD 使用者

### 操作紀錄

- 查詢使用者操作紀錄
- 依日期、使用者、操作類型等條件搜尋

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

### 其他常見問題

### 環境變數問題

如果 `.env` 檔案中的中文字符顯示亂碼，請使用 UTF-8 編碼重新建立檔案：

```powershell
# PowerShell 指令
Get-Content -Encoding utf8 .env | Out-File -Encoding utf8 .env.new
Move-Item -Force .env.new .env
```

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
```

> **注意**：請確保 `.env` 檔案使用正確的編碼儲存，避免中文字符顯示亂碼。

## 最新更新

- **2025-05-22**: 修復AD使用者加入平台群組時出現「Field required: password」錯誤，為AD使用者自動生成隨機密碼
- **2025-05-21**: 修復 AD 帳號登入功能無法被點擊使用的問題，確保 AD 登入功能不受 AD 設定狀態的影響
- **2025-05-18**: 在 main.js 中引入 Material Design Icons (MDI) 的 CSS 文件，修正不顯示圖示的問題
- **2025-05-18**: 升級功能圖示，使用更具代表性的圖示並優化展示效果，使側邊欄收合時清晰顯示圖示
- **2025-05-18**: 修正側邊欄收合後功能圖示不顯示的問題，移除 v-list-item 的 prepend-icon 屬性，改用 v-slot:prepend 顯示圖示
- **2025-05-17**: 修復後端啟動時的驗證錯誤，在 Settings.Config 中設定 extra = "ignore" 允許額外的環境變數
- **2025-05-17**: 整合多個 .env 檔案為一個，修改 run.py 和 config.py 以指向根目錄的 .env 檔案
- **2025-05-17**: 整合環境變數設定到單一 .env 檔案，修改 vite.config.js 使前端從根目錄讀取環境變數
