# HLAIChat 管理平台

這是一個用於管理各種 AI 聊天流程對話網址的平台，可以依據使用者所屬群組，分配可以使用的聊天網址。

**專案起始日期**：2025年4月15日  
**最後更新日期**：2025年6月17日

## 專案目標

本專案旨在創建一個管理平台，管理各個不同用途目的 AI 聊天流程對話網址，並依使用者所屬群組，分配可以使用的聊天網址。具有以下特點：

1. **AD 網域驗證登入**：支援 AD 網域驗證登入，管理者可以搜尋 AD 使用者，並加入選定的平台群組。
2. **平台內建帳號登入**：支援平台內建帳號登入，管理者可以管理平台使用者帳號。
3. **平台群組管理**：管理者可以管理平台群組，設定群組權限。
4. **憑證管理**：管理者可以管理 API 憑證，用於連接 n8n 或 Flowise 等外部服務。
5. **AI 聊天流程對話網址管理**：管理者可以管理 AI 聊天流程對話網址，指派群組可以使用的連結。支援多種類型：
   - **n8n Host Chat**：完整的 n8n 聊天網頁，另開新分頁導向聊天網址
   - **n8n Embedded Chat**：在自訂網頁內嵌入 n8n 預設的對話元件
   - **n8n Webhook**：透過 webhook 觸發的 n8n 流程，提供仿 ChatGPT 介面，包含完整聊天歷史管理
   - **Flowise Chat**：預留支援 Flowise 聊天流程（未來功能）
6. **聊天介面設計**：
   - **Embedded 類型**：簡單的嵌入頁面，直接顯示 n8n 的對話元件
   - **Webhook 類型**：完整的 ChatGPT 風格聊天介面，包含左側聊天歷史列表、會話管理、訊息歷史等功能
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
│   │   ├── web.config      # IIS URL Rewrite 配置
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
├── scripts/                # 部署和管理腳本
│   ├── deploy_database.ps1 # 資料庫部署腳本
│   ├── deploy_backend.ps1  # 後端部署腳本
│   ├── deploy_frontend.ps1 # 前端部署腳本
│   ├── deploy_full.ps1     # 一鍵部署腳本
│   ├── manage_services.ps1 # 服務管理腳本
│   └── DEPLOYMENT_SCRIPTS.md # 腳本說明文件
├── preview-frontend/       # 前端原型
├── .env                    # 環境變數
├── README.md               # 專案說明
└── CHANGELOG.md            # 修改歷程
```

## 快速開始

### 方式一：自動化部署（推薦）

本專案提供完整的 PowerShell 部署腳本，支援一鍵部署和分步部署。

#### 🚀 一鍵部署
```powershell
# 互動式完整部署
.\scripts\deploy_full.ps1

# 自動化完整部署
.\scripts\deploy_full.ps1 -Mode Auto

# 僅部署特定組件
.\scripts\deploy_full.ps1 -SkipDatabase    # 跳過資料庫
.\scripts\deploy_full.ps1 -SkipFrontend    # 跳過前端
```

#### 🔧 分步部署
```powershell
# 分步部署（可在不同主機執行）
.\scripts\deploy_database.ps1     # 部署資料庫
.\scripts\deploy_backend.ps1      # 部署後端 API
.\scripts\deploy_frontend.ps1     # 部署前端網站

# 服務管理
.\scripts\manage_services.ps1     # 服務管理介面
```

#### 📋 系統需求
- **作業系統**: Windows Server 2019/2022 或 Windows 10/11
- **權限**: 管理員權限
- **軟體**: Python 3.9+, Node.js 16+, PostgreSQL 15+

#### 🏠 主機配置
| 主機角色 | IP 位址 | 服務 |
|---------|--------|------|
| 資料庫主機 | 192.168.1.221 | PostgreSQL (5432) |
| 後端主機 | 192.168.5.107 | FastAPI (8000) |
| 前端主機 | 192.168.5.54 | IIS (80) / Node.js (3000) |

詳細說明請參考：
- [腳本說明文件](scripts/README_SCRIPTS.md)：各個腳本的功能和使用方式
- [部署說明文件](scripts/DEPLOYMENT.md)：完整的部署指南和系統需求

### 方式二：手動開發環境設定

#### 1. 環境設定
```bash
# 複製環境變數範本
cp env-template.txt .env

# 編輯環境變數
# 設定資料庫連線、AD 設定等參數
```

#### 2. 後端啟動
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 前端啟動
```bash
cd frontend
npm install
npm run dev
```

#### 4. 存取應用程式
- 前端：http://localhost:5173
- 後端 API：http://localhost:8000
- API 文件：http://localhost:8000/docs

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

## 環境變數設定

### AD 網域設定

AD 連線帳密透過管理介面儲存在資料庫中，環境變數只需設定基本網域資訊：

```env
# AD 網域設定（基本資訊，實際帳密透過管理介面儲存在資料庫中）
AD_DOMAIN_NAME=hanlin.com.tw
AD_PRIMARY_DC=192.168.1.6
AD_SECONDARY_DCS=192.168.1.5,192.168.5.5
```

### 聊天逾時設定

可透過環境變數調整聊天功能的逾時時間：

```env
# 聊天功能逾時設定（秒）
CHAT_WEBHOOK_TIMEOUT=300      # webhook 讀取逾時（5分鐘）
CHAT_REQUEST_TIMEOUT=300      # 請求寫入逾時（5分鐘）
CHAT_CONNECTION_TIMEOUT=60    # 連線建立逾時（1分鐘）

# 前端聊天逾時設定（毫秒）
VITE_CHAT_TIMEOUT=300000      # 前端 axios 請求逾時（5分鐘）
```

### JWT Token 設定

可透過環境變數調整 Token 過期時間：

```env
# JWT Token 設定
ACCESS_TOKEN_EXPIRE_MINUTES=60    # Token 過期時間（分鐘）
```

## 部署注意事項

### Vue.js SPA 路由配置

本專案使用 Vue Router 的 History 模式，在 IIS 上部署時需要 `web.config` 檔案支援 URL Rewrite：

```xml
<!-- frontend/public/web.config -->
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="Handle History Mode and hash fallback" stopProcessing="true">
          <match url="(.*)" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

### Webhook 參數規範

每次向 n8n webhook 發送的 POST 請求包含以下參數：

```json
{
  "user_id": "當前登入使用者ID",
  "session_id": "對話 session 唯一識別碼",
  "api_key": "選定的 API Key",
  "message": "使用者輸入的訊息內容",
  "sequence": "訊息序號（由後端架構維護）",
  "timestamp": "台北時間戳記",
  "user_name": "使用者姓名"
}
```

## API 文件

啟動後端服務後，可以在瀏覽器中訪問 Swagger UI 文件：

```
http://localhost:8000/docs
```

## 安全性

### 權限控制架構

本專案採用多層次的權限控制機制，確保系統安全性：

#### 核心安全機制
- **JWT Token 驗證**：所有 API 請求都需要有效的 JWT Token
- **管理者權限檢查**：敏感的管理功能需要管理者權限
- **群組權限過濾**：使用者只能存取所屬群組有權限的資源
- **操作日誌記錄**：所有重要操作都會記錄到資料庫

#### 權限分級

**🔴 管理者專用功能**（需要 `get_current_admin_user` 權限）：
- 使用者管理（建立、修改、刪除使用者）
- 群組管理（建立、修改、刪除群組）
- 聊天連結管理（建立、修改、刪除聊天連結）
- 憑證管理（建立、修改、刪除 API 憑證）
- AD 設定管理（配置 AD 連線參數）
- 系統統計資料查看（使用者數量、群組數量等）
- 全域操作紀錄查看（所有使用者的操作記錄）

**🟡 一般使用者功能**（需要登入驗證）：
- 查看個人操作紀錄
- 查看個人聊天紀錄
- 修改個人密碼
- 使用有權限的聊天連結

**🟢 群組權限控制**：
- 使用者只能看到所屬群組有權限的聊天連結
- 聊天功能需要 `can_use_chat_links` 群組權限
- 登入功能需要 `can_login` 群組權限

#### 安全修正歷程

**2025年6月3日 - 重要安全修正**：
- 修正系統統計資料 API 未受保護的問題
- 修正最近聊天連結 API 權限過寬的問題
- 強化群組權限過濾機制
- 新增完整的操作日誌記錄

詳細的安全修正報告請參考：[SECURITY_FIXES_REPORT.md](SECURITY_FIXES_REPORT.md)

#### 安全建議

**目前安全等級**：🟢 **優秀**

**後續改進建議**：
1. **API Rate Limiting**：考慮加入請求頻率限制
2. **IP 白名單**：對管理功能加入 IP 限制
3. **密碼安全性**：目前使用明文密碼，建議後期加入雜湊機制
4. **Session 管理**：考慮加入 Session 過期和強制登出機制

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
- **✅ 已完成**：搜尋 AD 使用者功能，支援多筆結果顯示和詳細資訊
- **功能特色**：
  - **多筆搜尋結果**：可同時顯示多個符合條件的 AD 使用者
  - **詳細使用者資訊**：顯示 AD 使用者的完整資訊，包含：
    - 👤 使用者帳號 (sAMAccountName)
    - 📧 電子郵件 (mail)
    - 🏢 部門 (department)
    - 💼 職稱 (title)
    - ℹ️ 描述 (description)
    - 🏷️ 顯示名稱 (displayName)
  - **搜尋結果數量控制**：可選擇顯示 10、20、30、40、50 筆搜尋結果
  - **智慧提醒**：當搜尋結果達到上限時，提醒管理者可能還有更多符合條件的使用者
  - **視覺化資訊**：使用圖示和標籤清楚區分不同類型的使用者資訊
  - **詳細資訊卡片**：在加入使用者時顯示完整的 AD 使用者資訊供管理者確認

### 操作紀錄

- **✅ 已完成**：查詢使用者操作紀錄功能，支援多種搜尋條件
- **✅ 已完成**：依日期、使用者名稱、操作類型等條件進行搜尋
- **✅ 已完成**：分頁顯示，支援大量紀錄的高效瀏覽
- **✅ 已完成**：管理者可查看所有使用者的操作紀錄
- **✅ 已完成**：一般使用者可查看自己的操作紀錄
- **✅ 已完成**：支援使用者名稱模糊搜尋功能
- **✅ 已完成**：操作類型切換時自動重設頁碼，避免參數錯誤
- **功能特色**：
  - 即時記錄所有使用者操作，包含登入、登出、資料異動等
  - 記錄詳細資訊：操作時間、IP 位址、操作詳情
  - 支援多種操作類型：LOGIN、LOGOUT、CREATE_USER、UPDATE_USER、DELETE_USER、CREATE_GROUP、UPDATE_GROUP、DELETE_GROUP、CREATE_CHAT_LINK、UPDATE_CHAT_LINK、DELETE_CHAT_LINK、USE_CHAT_LINK、SEND_CHAT_MESSAGE、UPDATE_AD_CONFIG 等
  - 管理者介面提供完整的搜尋和過濾功能
  - 使用者介面提供個人操作歷程查詢

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

### Vue Router 路由問題 (SPA 404 錯誤)

**問題症狀**：在生產環境中重新整理頁面或直接訪問路由時出現 HTTP 404 錯誤

**問題原因**：
1. Vue.js 使用 History 模式的 SPA 需要伺服器端配置支援
2. 部署時遺失 `web.config` 檔案，IIS 無法正確處理路由

**解決方法**：
- 確認 `frontend/public/web.config` 檔案存在
- 使用 `.\deploy_frontend.ps1` 腳本進行標準化部署
- 驗證 `dist/web.config` 在建置後存在
- 確認 IIS URL Rewrite 模組已安裝

**預防措施**：
- `web.config` 現已加入版本控制，每次建置自動包含
- 使用標準化部署腳本避免檔案遺失
- 部署前檢查清單包含 `web.config` 驗證

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

# AD 網域設定 (基本資訊，實際帳密透過管理介面儲存在資料庫中)
AD_DOMAIN_NAME=hanlin.com.tw
AD_PRIMARY_DC=192.168.1.6
AD_SECONDARY_DCS=192.168.1.5,192.168.5.5

# 前端設定
VITE_API_BASE_URL=http://localhost:8000

# 時區設定 (台北時間)
TIMEZONE=Asia/Taipei

# 聊天功能逾時設定 (秒)
CHAT_WEBHOOK_TIMEOUT=300
CHAT_REQUEST_TIMEOUT=300
CHAT_CONNECTION_TIMEOUT=300

# 前端聊天逾時設定 (毫秒)
VITE_CHAT_TIMEOUT=300000
```

## 重要環境變數說明

### SECRET_KEY
- **用途**：JWT Token 的加密和解密密鑰
- **重要性**：確保只有知道密鑰的伺服器才能產生和驗證有效的登入憑證
- **安全性**：請使用足夠複雜的密鑰，避免使用預設值

### ACCESS_TOKEN_EXPIRE_MINUTES
- **用途**：設定 JWT Token 的有效期限（分鐘）
- **預設值**：60 分鐘
- **彈性調整**：可透過修改此環境變數來調整 token 過期時間，無需修改程式碼
- **影響範圍**：
  - 平台帳號登入的 token 過期時間
  - AD 帳號登入的 token 過期時間
  - 取得使用者資訊時的 token 更新過期時間
- **注意事項**：
  - 時間過短會導致使用者頻繁需要重新登入
  - 時間過長可能增加安全風險
  - 建議根據實際使用情況調整（一般建議 30-120 分鐘）

> **注意**：請確保 `.env` 檔案使用正確的編碼儲存，避免中文字符顯示亂碼。
> 
> **聊天逾時設定**：如需調整聊天功能的逾時時間，請參考 `CHAT_TIMEOUT_CONFIGURATION.md` 文件的詳細說明。

## 最新更新

- **2025-06-01**: 使用者紀錄功能修正與專案清理
  - **問題修正**：修正使用者無法查看自己操作紀錄的問題，建立專門的使用者個人資料 API 路由
  - **架構改善**：明確區分管理者專用 API 和使用者個人 API，提升權限控制的精確性
  - **專案清理**：移除冗餘檔案和除錯程式碼，保持專案結構簡潔
- **2025-05-27**: 使用者介面優化與簡化

## API 路由結構

### 認證相關
- `POST /api/auth/login` - 使用者登入
- `POST /api/auth/logout` - 使用者登出
- `GET /api/auth/me` - 取得目前使用者資訊

### 管理者專用 API
- `GET /api/users/` - 取得所有使用者 (管理者)
- `POST /api/users/` - 建立使用者 (管理者)
- `PUT /api/users/{user_id}` - 更新使用者 (管理者)
- `DELETE /api/users/{user_id}` - 刪除使用者 (管理者)
- `GET /api/groups/` - 群組管理 (管理者)
- `GET /api/chat-links/` - 聊天連結管理 (管理者)
- `GET /api/logs/` - 操作紀錄查詢 (管理者)

### 使用者個人 API
- `GET /api/user-profiles/operation-logs` - 取得自己的操作紀錄
- `GET /api/user-profiles/chat-history` - 取得自己的聊天紀錄
- `PUT /api/users/me/password` - 更新自己的密碼

### 聊天功能
- `GET /api/chat-links/{chat_link_id}` - 取得聊天連結 (使用者)
- `POST /api/chat/webhook` - Webhook 聊天
- `POST /api/chat/embedded` - Embedded 聊天

## 專業部署腳本系統

本專案提供完整的 PowerShell 部署腳本系統，支援一鍵部署和細分管理：

### 部署腳本功能

- **`deploy_full.ps1`**：一鍵部署整個專案，支援多主機和單機部署
- **`deploy_database.ps1`**：資料庫主機 PostgreSQL 安裝和設定
- **`deploy_backend.ps1`**：後端主機 Python 環境和 FastAPI 服務部署
- **`deploy_frontend.ps1`**：前端主機 Node.js 環境和 Vue.js 應用部署
- **`manage_services.ps1`**：統一管理所有服務的啟停和狀態監控

### 腳本特色

- **完整繁體中文註解**：所有腳本都包含詳細的中文說明
- **錯誤處理機制**：自動檢查前置條件和安裝狀態
- **進度顯示**：使用彩色輸出顯示執行步驟和結果
- **參數化配置**：支援自定義主機位址、路徑等參數
- **安全檢查**：管理員權限驗證和操作確認提示

### 使用範例

```powershell
# 一鍵部署所有服務（單機環境）
.\scripts\deploy_full.ps1 -Target all

# 分步部署（多主機環境）
.\scripts\deploy_database.ps1 -DatabaseHost "acmdb1.hanlin.com.tw"
.\scripts\deploy_backend.ps1 -BackendHost "acmback1.hanlin.com.tw"
.\scripts\deploy_frontend.ps1 -FrontendHost "acm1.hanlin.com.tw"

# 服務管理
.\scripts\manage_services.ps1 -Action status    # 查看所有服務狀態
.\scripts\manage_services.ps1 -Action restart   # 重啟所有服務
```

詳細說明請參考：
- [部署文件](DEPLOYMENT.md)：完整的部署指南和系統需求
- [腳本說明](scripts/README.md)：各個腳本的詳細功能和使用方式

### 傳統手動部署注意事項

如果仍使用手動部署方式，請注意以下事項：

- 修改 `.env`（API 位置等）後，必須重新 build 前端並重新部署 `dist` 內容
- `.env` 檔案僅需放在專案根目錄，Vite 會自動讀取，無需複製到 frontend/ 目錄
- 若遇到 Vite 無法讀取 .env，請檢查 vite.config.js 的 envDir 設定是否正確指向根目錄
- 後端 CORS 設定需允許前端實際網域
- 若遇到 `No 'Access-Control-Allow-Origin' header` 或 `ERR_NETWORK`，請檢查 CORS 與 API 位置設定

**建議**：使用上述專業部署腳本可自動處理這些設定，避免手動設定的錯誤。
