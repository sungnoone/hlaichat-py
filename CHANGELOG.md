# 修改歷程

本文件記錄 HLAIChat 管理平台的所有重要變更。

## [未發布]

### 部署文件整合優化 (2025-06-17)

- **問題解決**：`scripts/` 目錄內的部署文件過多，維護和理解困難
- **文件整合**：
  - **創建統一部署指南**：建立 `scripts/DEPLOYMENT_GUIDE.md` 完整部署指南
  - **內容整合**：將 `README_SCRIPTS.md`、`DEPLOYMENT_SCRIPTS.md`、`DEPLOYMENT.md` 三個文件的內容全部整合
  - **冗餘清理**：刪除整合後的重複文件，避免文件碎片化
  - **結構優化**：重新組織章節結構，從系統概述到維護指南的完整流程

- **新部署指南特色**：
  - **完整覆蓋**：包含系統概述、需求、腳本說明、部署流程、服務管理、故障排除、維護指南
  - **實用性強**：提供詳細的 PowerShell 指令範例和參數說明
  - **分級指導**：支援快速部署、多主機部署、單主機部署等不同情境
  - **維護友好**：包含定期維護任務、效能監控、災難恢復等進階內容
  - **問題解決**：詳細的故障排除指南，包含 PowerShell、網路、Python、Node.js、PostgreSQL 等各種問題

- **文件結構最終狀態**：
  - ✅ `scripts/DEPLOYMENT_GUIDE.md`：統一完整的部署指南（新建）
  - ❌ `scripts/DEPLOYMENT.md`：已刪除
  - ❌ `scripts/DEPLOYMENT_SCRIPTS.md`：已刪除  
  - ❌ `scripts/README_SCRIPTS.md`：已刪除
  - ✅ `scripts/deploy_*.ps1`：保留所有部署腳本
  - ✅ `scripts/manage_services.ps1`：保留服務管理腳本

- **後續維護**：
  - 單一文件維護，降低文件同步成本
  - 完整的部署和維護指導，提升系統可維護性
  - 明確的腳本使用說明，降低學習成本

### 部署腳本系統優化和文件整理 (2025-06-17)

- **部署腳本重構**：以 UTF-8 編碼重新產生所有正確的部署腳本
  - **編碼統一**：所有 PowerShell 腳本統一使用 UTF-8 編碼，設定 `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`
  - **語法修正**：修正所有 PowerShell 腳本的語法錯誤，包括變數引用格式、字串結尾等問題
  - **冗餘清理**：移除 `deploy_frontend_fixed.ps1`、`deploy_frontend_clean.ps1`、`fix_encoding.ps1` 等有問題的冗餘腳本
  - **功能完整**：重新創建完整的 5 個核心部署腳本，總計約 70KB 代碼
  - **參數化改進**：改善腳本參數化和功能模組化，支援更彈性的配置選項

- **文件結構整理**：將專案文件集中管理，提升維護性
  - **文件移動**：將 `DEPLOYMENT.md` 移動到 `scripts/` 目錄內，保持部署相關文件的集中管理
  - **文件更新**：更新 `README.md` 中的部署說明，整合主要部署資訊和快速開始指南
  - **文檔優化**：更新 `scripts/README_SCRIPTS.md`，提供詳細的腳本功能說明和使用範例
  - **引用修正**：修正所有相關的檔案引用連結，確保文件間的正確關聯

- **腳本品質提升**：
  - **錯誤處理**：統一錯誤處理和彩色輸出格式，提升使用者體驗
  - **編碼處理**：使用 `[System.IO.File]::WriteAllText()` 確保檔案以 UTF-8 編碼保存
  - **語法驗證**：所有腳本通過 PowerShell 語法檢查，確保執行可靠性
  - **功能測試**：驗證腳本的主要功能，包括部署流程和服務管理

- **最終腳本清單**：
  - `deploy_backend.ps1` (14.6 KB)：後端部署腳本
  - `deploy_database.ps1` (9.6 KB)：資料庫部署腳本
  - `deploy_frontend.ps1` (10.3 KB)：前端部署腳本
  - `deploy_full.ps1` (14.8 KB)：完整部署腳本
  - `manage_services.ps1` (20.7 KB)：服務管理腳本

### PowerShell 部署腳本語法修正和整理 (2025-06-17)

- **問題解決**：前端部署腳本存在語法錯誤和編碼問題，導致部署失敗
  - **語法錯誤修正**：修正 try-catch 語句結構、未預期的語彙基元、字串結尾字元遺漏等問題
  - **編碼問題解決**：解決 PowerShell ISE 中繁體中文顯示亂碼問題，統一使用 UTF-8 編碼
  - **JavaScript 衝突修復**：使用 here-string 語法避免 PowerShell 解析 JavaScript 代碼衝突

- **腳本整理和優化**：
  - **移除冗餘檔案**：刪除有問題的 `deploy_frontend.ps1` 和 `deploy_frontend_fixed.ps1`
  - **保留最終版本**：`deploy_frontend_final.ps1` 已測試成功，語法完全正確
  - **創建主要入口**：新建 `deploy_frontend.ps1` 作為指向最終版本的入口腳本
  - **統一腳本品質**：確保所有部署腳本都符合相同的語法和編碼標準

- **腳本功能驗證**：
  - ✅ **Node.js 環境檢查**：自動檢查 Node.js 和 npm 版本
  - ✅ **依賴套件安裝**：支援清理重新安裝，包含重試機制
  - ✅ **前端建置**：成功建置，輸出大小 5.95 MB
  - ✅ **IIS 配置**：完整的應用程式集區和網站設定
  - ✅ **防火牆規則**：自動設定 HTTP/HTTPS 規則
  - ✅ **後端連線測試**：成功連接到後端服務

- **新增腳本說明文件**：
  - 創建 `scripts/README_SCRIPTS.md` 詳細說明所有腳本用途
  - 提供完整的使用範例和參數說明
  - 包含疑難排解指南和版本歷史
  - 明確標示已測試腳本狀態

- **執行原則和編碼支援**：
  - 提供多種執行原則解決方案
  - 所有腳本自動設定 UTF-8 編碼
  - 支援繁體中文顯示和輸出
  - 完善的錯誤處理和使用者友好的訊息

- **部署成功驗證**：
  - 前端網站成功部署到 IIS
  - 所有服務狀態正常
  - 後端 API 連線測試通過
  - 適用於 Windows Server 2019/2022 和 Windows 10/11

### 專案文件結構優化 (2025-06-17)

- **問題解決**：專案根目錄文件過於分散，不利於維護和理解
- **檔案整合**：
  - 將 `scripts/README.md` 重新命名為 `scripts/DEPLOYMENT_SCRIPTS.md`
  - 將重要技術資訊整合到 `README.md` 中（環境變數設定、部署注意事項、Webhook 參數規範）
  - 將修復和改進歷程整合到 `CHANGELOG.md` 中
  - 清理不必要的零散文件，保持專案根目錄簡潔
- **日期修正**：
  - 修正所有早於專案起始日期（2025年4月15日）的不合理日期
  - `佈署腳本系統重構`：2025-01-03 → 2025-05-15
  - `部署計畫標準化修正`：2025-12-XX → 2025-05-20
  - `聊天功能超時配置與憑證選擇驗證`：2025-01-26 → 2025-05-28
  - `未發布項目`：2024-12-19 → 2025-04-20
  - 確保所有日期記錄符合專案實際開發時程
- **改善效果**：
  - 減少根目錄文件數量，提升專案結構清晰度
  - 將相關資訊集中管理，便於查找和維護
  - 避免檔名混亂，明確區分不同類型的文件
  - 提升專案的專業度和可維護性
- **影響範圍**：
  - 文件結構重新組織，重要資訊集中到主要文件中
  - 更新所有相關的檔案引用連結
  - 建立更清晰的專案文件架構
- **清理的文件**：
  - `AD_ENVIRONMENT_CLEANUP.md` → 內容整合到 CHANGELOG.md
  - `CHAT_LINK_TYPES_MIGRATION.md` → 內容整合到 README.md 和 CHANGELOG.md
  - `CHAT_TIMEOUT_CONFIGURATION.md` → 內容整合到 README.md 和 CHANGELOG.md
  - `CREDENTIAL_SELECTION_VERIFICATION.md` → 內容整合到 CHANGELOG.md
  - `JWT_TOKEN_EXPIRE_MINUTES_FIX.md` → 內容整合到 README.md 和 CHANGELOG.md
  - `SECURITY_FIXES_REPORT.md` → 內容整合到 CHANGELOG.md
  - `test_ad_search_functionality.md` → 內容整合到 CHANGELOG.md
  - `test_chat_functionality.md` → 內容整合到 README.md
  - `VUE_ROUTER_SPA_ISSUES.md` → 內容整合到 README.md 和 CHANGELOG.md
- **保留的核心文件**：
  - `README.md`：專案主要說明文件
  - `CHANGELOG.md`：修改歷程記錄
  - `DEPLOYMENT.md`：部署指南
  - `scripts/DEPLOYMENT_SCRIPTS.md`：部署腳本說明

### 佈署腳本系統重構 (2025-05-15)

- **重大改進**：將原本冗長的部署文件重構為專業的可執行 PowerShell 腳本系統
  - **問題背景**：原本的 `DEPLOYMENT.md` 檔案長達 1327 行，包含大量程式碼片段，不便閱讀和維護
  - **解決方案**：抽取所有部署程式碼成為獨立的 PowerShell 腳本，並重新整理文件結構
  
- **新增專業部署腳本系統**：在 `scripts/` 目錄下建立 5 個完整的 PowerShell 腳本
  - **`deploy_database.ps1` (240 行)**：
    - 作用：在資料庫主機上設置 PostgreSQL 和專案資料庫
    - 功能：檢查 PostgreSQL 安裝、設定防火牆規則、配置連線設定、建立資料庫、建立備份目錄
    - 特色：自動化檢查和設定，包含完整錯誤處理機制
  - **`deploy_backend.ps1` (382 行)**：
    - 作用：在後端主機上設置 Python 環境、安裝依賴套件、配置服務
    - 功能：檢查 Python 環境、建立虛擬環境、安裝依賴、設定環境變數、初始化資料庫、安裝 NSSM Windows 服務
    - 特色：支援參數化配置，自動化服務管理和狀態檢查
  - **`deploy_frontend.ps1` (469 行)**：
    - 作用：在前端主機上設置 Node.js 環境、建置前端應用、配置 Web 伺服器
    - 功能：檢查 Node.js 環境、安裝依賴、建置應用、配置 IIS、設定防火牆規則
    - 特色：支援 IIS 和 Node.js 伺服器兩種部署選項，自動處理 Vue Router SPA 配置
  - **`deploy_full.ps1` (277 行)**：
    - 作用：一鍵部署整個專案，支援多主機和單機部署
    - 功能：自動識別主機類型、顯示部署計畫、按順序執行部署腳本、顯示結果總結
    - 特色：支援 `database`/`backend`/`frontend`/`all` 四種部署目標，智慧化部署流程
  - **`manage_services.ps1` (429 行)**：
    - 作用：統一管理專案相關的所有服務（資料庫、後端、前端）
    - 功能：管理 PostgreSQL、NSSM 後端服務、IIS 前端網站，支援 `start`/`stop`/`restart`/`status` 操作
    - 特色：提供服務狀態總覽和連線測試，一鍵式服務管理

- **建立腳本說明文件**：
  - **`scripts/README.md` (283 行)**：詳細說明每個腳本的作用、功能、參數
  - 提供 5 種不同情境的使用範例（一鍵部署、分步部署、單機部署、服務管理、故障排除）
  - 包含注意事項、故障排除指南、相關文件連結

- **簡化主要部署文件**：
  - 將原本 1327 行的 `DEPLOYMENT.md` 精簡為 287 行
  - 重新整理文件結構，重點說明腳本使用方式而非程式碼細節
  - 新增部署概述、系統需求、快速部署、分步部署、服務管理、故障排除等完整章節

- **技術特色**：
  - **完整繁體中文註解**：所有腳本都包含詳細的中文說明和註解
  - **錯誤處理機制**：自動檢查前置條件和安裝狀態，提供詳細錯誤訊息
  - **進度顯示**：使用彩色輸出顯示執行步驟和結果，提升使用者體驗
  - **參數化配置**：支援自定義主機位址、路徑、服務名稱等參數
  - **安全檢查**：管理員權限驗證和操作確認提示，避免誤操作
  - **智慧部署**：自動識別主機類型和環境狀態，選擇適當的部署策略

- **部署架構支援**：
  - **多主機部署**：支援資料庫、後端、前端分別部署在不同主機
  - **單機部署**：支援所有服務部署在同一台主機
  - **混合部署**：彈性支援部分服務合併部署的情境
  - **服務管理**：統一的服務啟停管理，支援狀態監控和故障排除

- **文件結構優化**：
  - 部署文件變得簡潔易讀，重點突出腳本使用方式
  - 腳本具備完整功能和註解，可獨立執行和維護
  - 提供了完整的腳本說明文件和使用範例
  - 支援一鍵部署和細分管理，大幅提升部署便利性

- **影響範圍**：
  - 新增 `scripts/` 目錄及 5 個 PowerShell 腳本
  - 新增 `scripts/README.md` 腳本說明文件
  - 重構 `DEPLOYMENT.md` 部署文件（從 1327 行精簡至 287 行）
  - 提升專案部署的專業度和便利性

### 聊天連結類型系統重構 (2025-05-24)

- **重大改進**：重構聊天連結類型命名系統，為未來的 Flowise 整合做準備
- **問題背景**：原本的類型命名（`host_chat`、`embedded_chat`、`webhook`）無法明確區分不同 AI 平台
- **新類型系統**：
  - `host_chat` → `n8n_host_chat`：n8n Host Chat 完整網頁
  - `embedded_chat` → `n8n_embedded_chat`：n8n Embedded Chat 嵌入組件
  - `webhook` → `n8n_webhook`：n8n Webhook 觸發流程
  - 新增 `flowise_chat`：預留給 Flowise 聊天流程（未來功能）
- **自動遷移**：提供 `migrate_chat_link_types.py` 腳本自動遷移現有資料
- **測試驗證**：建立 `test_chat_link_types.py` 腳本驗證系統正確性
- **向後相容**：API 拒絕舊格式類型，提供清晰錯誤訊息
- **擴展性設計**：支援未來新增其他 AI 平台類型

### 憑證選擇功能修復 (2025-05-26)

- **問題修復**：解決聊天連結管理中憑證選擇下拉選單無法顯示憑證的問題
- **根本原因**：
  - 前端 API 服務路徑錯誤：`/api/credentials/all` → `/api/credentials/simple`
  - 聊天連結管理頁面直接使用 axios 而非 API 服務
  - 錯誤的回應格式檢查
- **修復內容**：
  - 修正 `frontend/src/services/api.js` 中的 `getAllCredentials()` 方法
  - 修正 `frontend/src/views/admin/ChatLinks.vue` 中的 `fetchCredentials()` 函數
  - 統一使用 API 服務而非直接 axios 調用
- **功能驗證**：憑證選擇功能完全修復，使用者可正常選擇預設憑證

### 聊天逾時設定系統 (2025-05-27)

- **功能新增**：建立完整的聊天逾時設定架構，支援環境變數配置
- **環境變數支援**：
  - `CHAT_WEBHOOK_TIMEOUT`：webhook 讀取逾時（預設 300 秒）
  - `CHAT_REQUEST_TIMEOUT`：請求寫入逾時（預設 300 秒）
  - `CHAT_CONNECTION_TIMEOUT`：連線建立逾時（預設 60 秒）
  - `VITE_CHAT_TIMEOUT`：前端請求逾時（預設 300000 毫秒）
- **彈性配置**：可根據 n8n workflow 複雜度調整逾時時間
- **錯誤處理**：完善的逾時錯誤處理和使用者提示
- **統一管理**：所有逾時參數統一在 `.env` 檔案中設定

### Vue Router 路由問題修復 (2025-06-13)

- **問題修復**：解決生產環境 Vue.js SPA 路由 404 錯誤
  - **問題原因**：重新部署時遺失 `web.config` 檔案，導致 IIS 無法正確處理 Vue Router 路由
  - **症狀**：重新整理頁面或直接訪問路由時出現 HTTP 404.0 - Not Found 錯誤
  - **影響範圍**：生產環境 acm1.hanlin.com.tw，開發環境 192.168.1.12:3000 正常
- **根本解決方案**：
  - 新增 `frontend/public/web.config` 到版本控制
  - 建立標準化前端部署腳本 `deploy_frontend.ps1`
  - 更新部署文件和檢查清單
- **預防措施**：
  - `web.config` 現在會在每次 `npm run build` 時自動包含在 `dist` 目錄
  - 部署腳本會自動驗證 `web.config` 存在
  - 更新部署檢查清單，強調 `web.config` 的重要性
- **技術細節**：
  - 配置 IIS URL Rewrite 規則支援 Vue Router History 模式
  - 新增靜態檔案 MIME 類型支援
  - 配置 404 錯誤處理重定向到根路徑

### 部署計畫重構

- 2025-05-20: 部署計畫標準化修正
  - **路徑結構統一**：修正部署計畫中的路徑配置，遵循專案指引規範
    - **前端路徑修正**：從 `E:\hlaichat-py-frontend` 修正為 `E:\hlaichat-py\frontend`
    - **環境變數統一**：移除獨立的 `.env.production` 檔案，統一使用 `E:\hlaichat-py\.env`
    - **虛擬環境標準化**：明確定義虛擬環境路徑為 `E:\venv\hlaichat_backend_venv`
    - **日誌路徑統一**：NSSM 服務日誌統一存放於 `E:\logs`
  - **部署腳本增強**：更新快速部署腳本，支援前後端統一部署
    - 新增 `-IncludeFrontend` 參數，支援前端自動部署
    - 新增 Node.js 環境檢查和前端建置流程
    - 新增統一環境變數檔案檢查和驗證
    - 改善錯誤處理和狀態回饋
  - **路徑結構圖更新**：完善專案目錄結構說明
    ```
    E:\
    ├── venv\hlaichat_backend_venv\     # Python 虛擬環境
    ├── hlaichat-py\
    │   ├── backend\                    # 後端應用程式
    │   ├── frontend\                   # 前端應用程式
    │   └── .env                        # 統一環境變數檔案
    └── logs\                           # NSSM 服務日誌
    ```
  - **故障排除完善**：新增前端專用的故障排除章節
    - 新增前端依賴套件問題排除
    - 新增前端建置失敗排除
    - 新增前後端連線問題排除
    - 改善環境變數檢查流程
  - **部署檢查清單更新**：完善部署前、中、後的檢查項目
    - 新增前端路徑檢查
    - 新增統一環境變數檔案檢查
    - 新增前端建置成功檢查
    - 新增 Vue Router 功能檢查
  - **影響範圍**：
    - `DEPLOYMENT.md`：完整更新部署計畫文件
    - 前後端路徑配置標準化
    - 環境變數管理統一化
    - 部署腳本功能增強

### AD 搜尋功能改進 (2025-06-03)

- **功能增強**：大幅改進 AD 使用者搜尋功能的穩定性和使用體驗
- **錯誤修復**：
  - 修正前端 `v-for` 迴圈中 `user.guid` 可能為 `undefined` 導致的 TypeError
  - 增強後端 GUID 處理邏輯，確保總是有有效的識別符
- **功能新增**：
  - 新增搜尋結果數量控制（10-50 筆）
  - 新增詳細使用者資訊顯示（帳號、郵件、部門、職稱、描述）
  - 新增智慧提醒功能，當搜尋結果達到上限時提醒管理者
- **使用者體驗提升**：
  - 使用圖示化資訊展示
  - 職稱標籤顯示
  - 分隔線區分不同使用者
- **LDAP 屬性擴充**：搜尋時取得更多 AD 屬性資訊，包含 `displayName`、`mail`、`department`、`title`、`description`

### 清理

- 2025-06-03: 移除無用的 AD 環境變數參數
  - **問題確認**：經檢查確認 `.env` 檔案中的 `AD_BIND_USERNAME` 和 `AD_BIND_PASSWORD` 參數已完全沒有作用
  - **架構說明**：AD 連線帳密現在完全透過管理介面儲存在資料庫的 `ad_config` 資料表中，不再使用環境變數
  - **清理範圍**：
    - 從 `backend/app/core/config.py` 中移除 `AD_BIND_USERNAME` 和 `AD_BIND_PASSWORD` 的定義
    - 從 `env-template.txt` 中移除這兩個無用參數
    - 從 `setup_env.ps1` 中移除這兩個無用參數
    - 從 `README.md` 中移除這兩個無用參數的說明
    - 從 `DEPLOYMENT.md` 中移除這兩個無用參數
    - 更新 `CHANGELOG.md` 中的 AD 網域設定說明
  - **註解改善**：在所有相關檔案中加上清楚的註解說明：`(基本資訊，實際帳密透過管理介面儲存在資料庫中)`
  - **架構優勢**：
    - 管理者可透過網頁介面動態管理 AD 連線設定
    - 不需要修改檔案或重啟服務即可更新 AD 帳密
    - 環境變數檔案更加簡潔，只保留必要的基本網域資訊
    - 避免敏感帳密資訊存放在檔案系統中

### 修復

- 2025-06-03: 修正 JWT Token 過期時間硬編碼問題
  - **問題描述**：程式碼中多處使用硬編碼的 `timedelta(minutes=60)`，未使用環境變數 `ACCESS_TOKEN_EXPIRE_MINUTES`
  - **修正內容**：
    - **後端登入 API**：修正 `backend/app/apis/auth_routes.py` 中三個函數的硬編碼問題
      - `login` 函數：平台帳號登入的 token 過期時間
      - `ad_login` 函數：AD 帳號登入的 token 過期時間  
      - `get_me` 函數：取得使用者資訊時的 token 過期時間
    - **安全模組**：修正 `backend/app/core/security.py` 中 `create_access_token` 函數的預設過期時間
  - **改進效果**：
    - 現在可以透過修改 `.env` 檔案中的 `ACCESS_TOKEN_EXPIRE_MINUTES` 值來調整 token 有效期限
    - 不需要修改程式碼就能彈性調整認證 token 的過期時間
    - 統一使用環境變數管理，符合專案配置集中化原則
  - **影響範圍**：
    - `backend/app/apis/auth_routes.py`：三處硬編碼修正為 `settings.ACCESS_TOKEN_EXPIRE_MINUTES`
    - `backend/app/core/security.py`：一處硬編碼修正為 `settings.ACCESS_TOKEN_EXPIRE_MINUTES`

### 安全修正

- 2025-06-03: 後端API權限控制強化
  - **重要安全修正**：修正兩個關鍵的權限控制問題，防止未授權存取敏感資訊
  - **修正項目**：
    - **系統統計資料API** (`/api/stats`)：
      - **問題**：任何人都可以取得系統統計資料，包含使用者數量、群組數量等敏感資訊
      - **修正**：加入 `get_current_admin_user` 權限檢查，只有管理者才能存取
      - **新增**：操作日誌記錄，追蹤管理者查看統計資料的行為
    - **最近聊天連結API** (`/api/chat-links/recent`)：
      - **問題**：任何登入使用者都可以查看所有最近的聊天連結
      - **修正**：改用 `check_user_can_use_chat_links` 權限檢查
      - **新增**：群組權限過濾邏輯，只顯示使用者有權限的聊天連結
      - **新增**：操作日誌記錄，追蹤使用者查看聊天連結的行為
  - **權限架構確認**：
    - ✅ 所有管理功能（使用者、群組、聊天連結、憑證、AD設定、操作紀錄）都有適當的管理者權限保護
    - ✅ 一般使用者權限正確設定（個人操作紀錄、聊天紀錄、可用聊天連結、密碼修改）
    - ✅ 群組權限過濾機制完善，確保使用者只能存取有權限的資源
  - **安全等級提升**：從「良好但需改進」提升至「優秀」
  - **影響範圍**：
    - `backend/app/main.py`：系統統計資料API權限控制
    - `backend/app/apis/chat_link_routes.py`：最近聊天連結API權限控制
    - 新增完整的操作日誌記錄機制
  - **建立文件**：`SECURITY_FIXES_REPORT.md` 詳細記錄安全修正過程和建議

### 新增

- 2025-05-29: 左側導覽列釘選功能實現
  - **新增釘選按鈕**：在左側導覽列標題區域新增釘選按鈕，位於收合按鈕旁邊
  - **釘選狀態視覺回饋**：釘選時顯示實心圖釘圖示（橙色），未釘選時顯示空心圖釘圖示（灰色）
  - **智慧展開收合邏輯**：
    - 未釘選狀態：滑鼠移入自動展開，移出自動收合（原有行為）
    - 釘選狀態：滑鼠移入自動展開，移出時保持展開不收合
    - 手動收合：即使在釘選狀態下，點擊收合按鈕仍可手動收合導覽列
    - 釘選後收合：釘選狀態下手動收合後，滑鼠移入仍會自動展開，但移出時保持展開
  - **使用者體驗改善**：提供更靈活的導覽列控制方式，滿足不同使用習慣
  - **影響範圍**：
    - `frontend/src/components/AdminLayout.vue`：管理者介面導覽列釘選功能
    - `frontend/src/components/UserLayout.vue`：使用者介面導覽列釘選功能
    - 新增 `isPinned` 響應式狀態管理釘選狀態
    - 修改 `handleMouseEnter` 和 `handleMouseLeave` 事件處理邏輯
    - 新增 `togglePin` 方法處理釘選狀態切換

- 2025-05-29: 導覽列logo顯示優化
  - **介面簡化**：移除左側導覽列左上方的圓形logo顯示，保持介面簡潔
  - **登入頁面logo保持**：登入頁面下方仍使用原來的橫幅logo.png
  - **使用者體驗改善**：避免圓形logo顯示異常的問題，讓導覽列更加清爽
  - **功能保留**：導覽列的收合/展開功能和標題文字顯示正常運作
  - **影響範圍**：
    - `frontend/src/components/AdminLayout.vue`：移除管理者介面導覽列logo
    - `frontend/src/components/UserLayout.vue`：移除使用者介面導覽列logo
    - `frontend/src/views/Login.vue`：保持登入頁面橫幅logo不變
    - 清理相關CSS樣式，移除不再需要的logo控制樣式

- 2025-05-27: 調整聊天連線逾時設定
  - **重要變更**：將 `CHAT_CONNECTION_TIMEOUT` 從 60 秒調整為 300 秒 (5分鐘)
  - **影響範圍**：更新所有相關檔案以保持一致性
    - `.env` 檔案：主要環境變數設定
    - `env-template.txt`：環境變數範本檔案
    - `setup_env.ps1`：環境設定腳本
    - `backend/app/core/config.py`：後端配置檔案
    - `CHAT_TIMEOUT_CONFIGURATION.md`：逾時設定說明文件
    - `README.md`：專案說明文件
  - **目的**：提供更充裕的連線建立時間，避免網路環境較差時的連線逾時問題
  - **編碼規範**：確保所有檔案使用 UTF-8 編碼，避免中文註解亂碼問題

- 2025-05-27: n8n webhook 聊天介面新增可調整分隔器功能
  - **使用者體驗改善**：新增可拖拽的分隔器，讓使用者能夠彈性調整聊天歷史與當前對話區域的寬度比例
  - **功能特色**：
    - 可拖拽的垂直分隔器，支援滑鼠拖拽調整
    - 設定最小寬度 200px 和最大寬度 600px，確保介面可用性
    - 分隔器懸停和拖拽時的視覺回饋效果
    - 自動儲存使用者偏好設定到 localStorage，下次開啟時保持相同寬度
    - 防止拖拽時意外選中文字的保護機制
    - 輸入區域寬度自動跟隨右側對話區域調整
  - **技術實作**：
    - 使用 Vue 3 響應式系統管理分隔器狀態
    - CSS flexbox 佈局支援動態寬度調整
    - 滑鼠事件處理實現拖拽功能
    - localStorage 整合保存使用者偏好

- 2025-05-27: 移除冗餘的聊天對話導航連結
  - **介面簡化**：移除使用者導航欄中的「聊天對話」連結，因為功能已重複
  - **使用者體驗改善**：使用者現在直接從「我的聊天機器人」頁面點擊各個聊天連結進入對話
  - **架構優化**：每個聊天機器人都有自己的專屬介面，不需要通用的聊天頁面
  - **導航簡潔**：使用者導航現在只包含「我的聊天機器人」和「使用紀錄」兩個主要功能

- 2025-05-27: 修正 webhook 聊天介面佈局問題
  - **重要修正**：修正 WebhookChatInterface 組件的佈局結構，解決使用者反映的問題
    - 修正頂部藍色標題欄遮住新增對話按鈕的問題：將標題欄改為固定在頂部，左側邊欄標題獨立顯示
    - 修正輸入框位置問題：將輸入框固定在頁面底部，符合 ChatGPT 的使用習慣
    - 優化整體佈局結構：使用 flexbox 佈局，確保各區域正確分配空間
    - 改善視覺層次：調整 z-index 確保元素正確堆疊，避免遮擋問題
  - **佈局改進**：
    - 頂部標題欄固定在頁面頂部，包含返回按鈕、聊天機器人名稱和清除對話按鈕
    - 左側邊欄獨立的標題區域，包含「對話記錄」標題和新增對話按鈕
    - 右側聊天區域分為訊息顯示區和固定底部輸入區
    - 訊息區域自動滾動，為底部輸入框預留空間
    - 輸入框固定在頁面底部，寬度對應右側聊天區域

- 2025-05-27: 重構聊天介面架構，明確區分 embedded 和 webhook 類型
  - **重要變更**：重新設計聊天介面架構，明確區分兩種不同的聊天類型
    - **n8n embedded chat 類型**：只是在自訂網頁內嵌入 n8n 預設的對話元件
    - **n8n webhook 類型**：完整的自訂聊天介面，仿 ChatGPT 設計，包含聊天歷史管理功能
  - 建立 `EmbeddedChatInterface.vue` 組件，專門處理 embedded 類型的簡單嵌入頁面
  - 建立 `WebhookChatInterface.vue` 組件，專門處理 webhook 類型的 ChatGPT 風格聊天介面
  - 修改 `UserChat.vue` 作為路由組件，根據查詢參數決定載入哪個聊天介面
  - 修改 `UserDashboard.vue` 的連結處理邏輯：
    - **hosted 類型**：另開新分頁導向聊天網址
    - **embedded 類型**：進入嵌入 n8n 對話元件的頁面
    - **webhook 類型**：進入專屬自訂的 ChatGPT 風格對話介面
  - 移除原本的 `ChatInterface.vue`，避免混淆
  - 修改後端 `send_embedded_message` 方法，明確說明 embedded 類型應直接使用 n8n 嵌入元件
  - **WebhookChatInterface 功能特色**：
    - 左側聊天歷史列表，支援會話管理
    - 右側 ChatGPT 風格對話區域
    - 支援新建、重新命名、刪除會話
    - 完整的訊息歷史記錄和顯示
    - 即時的載入狀態和錯誤處理
    - 響應式設計，適應不同螢幕尺寸

- 2025-05-27: 確認 .env 檔案參數完整性
  - 經檢查確認 .env 檔案所有參數都已正確設定，包括：
    - 應用程式設定：APP_NAME、SECRET_KEY、DEBUG、HOST、PORT、RELOAD、ACCESS_TOKEN_EXPIRE_MINUTES
    - 資料庫設定：DATABASE_URL
    - AD 網域設定：AD_DOMAIN_NAME、AD_PRIMARY_DC、AD_SECONDARY_DCS (實際帳密透過管理介面儲存在資料庫中)
    - 前端設定：VITE_API_BASE_URL
    - 時區設定：TIMEZONE
    - 聊天功能逾時設定：CHAT_WEBHOOK_TIMEOUT、CHAT_REQUEST_TIMEOUT、CHAT_CONNECTION_TIMEOUT
    - 前端聊天逾時設定：VITE_CHAT_TIMEOUT
  - 中文註解顯示正常，無編碼問題
  - 更新 setup_env.ps1 腳本使用 UTF-8 編碼並包含完整的聊天逾時參數

- 2025-05-27: 修復 n8n webhook 回應解析問題
  - 修正後端 `chat_service.py` 中的 webhook 回應處理邏輯
  - 支援多種回應格式：優先解析 `output` 欄位，其次為 `message`、`text`、`content` 欄位
  - 新增詳細的 webhook 回應日誌記錄，包含原始回應內容、狀態碼和標頭資訊
  - 改善 JSON 解析錯誤處理，當無法解析 JSON 時將原始文字作為回應內容
  - 新增完整的錯誤堆疊追蹤，便於除錯和問題診斷
  - **問題解決**：聊天介面現在能正確顯示 n8n "Respond to Webhook" 節點的回應內容

- 2025-05-27: 聊天逾時設定優化
  - 將所有聊天相關的逾時參數移至 `.env` 檔案統一管理
  - 新增後端逾時參數：`CHAT_WEBHOOK_TIMEOUT`、`CHAT_REQUEST_TIMEOUT`、`CHAT_CONNECTION_TIMEOUT`
  - 新增前端逾時參數：`VITE_CHAT_TIMEOUT`
  - 修改後端 `chat_service.py` 使用環境變數中的逾時設定，取代硬編碼的 30 秒逾時
  - 修改前端 `ChatInterface.vue` 使用環境變數中的逾時設定
  - 建立詳細的逾時設定說明文件 `CHAT_TIMEOUT_CONFIGURATION.md`
  - 更新 `env-template.txt` 包含新的逾時參數
  - 確保 n8n workflow 有足夠時間處理複雜的 AI 請求

- 2025-05-27: 修復 .env 檔案中文亂碼問題
  - 使用 UTF-8 編碼重新建立 `.env` 檔案，解決中文註解顯示亂碼問題
  - 確保檔案包含完整的環境變數參數，包括新增的聊天逾時設定
  - 同步更新 `env-template.txt` 檔案格式，保持範本與實際檔案一致
  - 改進 README.md 中的編碼問題說明，提供更詳細的解決方案

- 2025-05-24: 完善 webhook trigger workflow 仿 ChatGPT 聊天介面設計
  - 新增聊天會話和訊息資料模型 (ChatSession, ChatMessage)
  - 建立聊天相關的 Pydantic 模型和 API 路由
  - 實作聊天服務類別，支援會話管理和 webhook 整合
  - 建立仿 ChatGPT 的前端聊天介面組件
  - 支援多會話管理、訊息歷程記錄和即時對話
  - 整合 n8n webhook 參數傳遞規範
  - 新增聊天功能到使用者導航選單
  - 更新資料庫遷移腳本，支援聊天相關表格建立

- 2025-05-24: 聊天連結類型重構，支援未來 Flowise 整合
  - **重要變更**: 重新設計聊天連結類型命名系統，避免日後混淆
    - `host_chat` → `n8n_host_chat`
    - `embedded_chat` → `n8n_embedded_chat`
    - `webhook` → `n8n_webhook`
    - 預留 `flowise_chat` 類型供未來擴展
  - 建立並執行資料庫遷移腳本 `migrate_chat_link_types.py`
  - 成功更新 2 個現有聊天連結的類型
  - 更新前後端所有相關的類型檢查和顯示邏輯
  - 建立測試腳本 `test_chat_link_types.py` 驗證系統正確性
  - 更新測試功能文件，新增類型系統測試指引
  - 建立詳細的遷移說明文件 `CHAT_LINK_TYPES_MIGRATION.md`
  - 確保類型系統具備良好的擴展性和向後相容性

- 初始專案架構設定
- 資料庫模型定義
- API 路由實作
  - 使用者管理 API
  - 群組管理 API
  - 聊天連結管理 API
  - AD 設定 API
  - 操作紀錄 API
  - 憑證管理 API (2025-05-23)
- 認證與授權機制
- AD 網域整合
- 操作紀錄功能
- 憑證管理功能 (2025-05-23)
  - 後端憑證管理 API，包含 CRUD 操作
  - 前端憑證管理介面，支援新增、編輯、刪除憑證
  - API Key 顯示/隱藏和複製功能
  - 憑證與聊天連結的關聯管理
  - 完整的操作日誌記錄
- 前端介面開發完成
  - 登入頁面
  - 管理員儀表板
  - 使用者管理頁面
  - 群組管理頁面
  - 聊天連結管理頁面
  - AD 設定頁面
  - 操作紀錄頁面
  - 個人設定頁面
  - 一般使用者儀表板
  - 一般使用者個人資料頁面
  - 一般使用者使用紀錄頁面
  - 憑證管理頁面 (2025-05-23)
- 前後端整合測試完成
- 從原型設計中複製 logo 到正式前端
- 新增網站圖示 (favicon) 系列檔案
  - favicon.ico
  - apple-touch-icon.png
  - favicon-16x16.png
  - favicon-32x32.png
  - android-chrome-192x192.png
  - android-chrome-512x512.png
- 新增 site.webmanifest 檔案，提供 PWA 支援
- 新增 index.html 檔案，包含所有必要的圖示連結
- 2025-05-19: 優化使用者管理頁面中的群組管理功能
  - 新增搜尋功能，便於在多個群組中查找特定群組
  - 改進群組選擇界面，顯示群組權限資訊
  - 新增已選擇群組的視覺摘要
  - 新增清除所有選擇的功能
- 2025-05-19: 優化群組管理頁面中的成員管理功能
  - 新增篩選功能，可快速查看所有用戶、成員或非成員
  - 新增批量加入和移除成員的功能
  - 改進成員切換的視覺體驗，使用直觀的按鈕替代複選框
  - 新增加載狀態顯示，提供更好的用戶反饋
  - 新增重新整理功能，可以重新獲取最新的用戶列表

### 修正

- 2025-05-26: 專案清理和冗餘檔案移除
  - 移除所有 Python 編譯快取檔案 (__pycache__ 目錄和 .pyc 檔案)
  - 移除重複的遷移腳本 `backend/migrate_chat_link_types.py`（保留根目錄的最新版本）
  - 移除重複的開發指引檔案 `.clinerules/hlaichat-py.md`（保留 `.cursor/rules/hlaichat-py.mdc`）
  - 移除前端重複的 README 檔案 `frontend/README.md`（保留根目錄的完整版本）
  - 移除 `.gitignore` 檔案，避免妨礙開發中的讀寫動作
  - 保留除錯用的 console.log 語句以利日後除錯
  - 確保專案結構簡潔，移除冗餘檔案但保持功能完整性
- 2025-05-26: 修復聊天連結管理中憑證選擇功能
  - 修正前端 API 服務中的憑證路徑，將 `/api/credentials/all` 改為 `/api/credentials/simple`
  - 修正聊天連結管理頁面中的憑證載入邏輯，使用正確的 API 服務方法
  - 確保新增 webhook 類型聊天連結時能正確顯示和選擇預設的憑證
  - 改善前端錯誤處理，移除不必要的回應格式檢查
  - **功能驗證完成**：新增 webhook 類型連結已可選到預先設定的憑證
- 2025-05-23: 修復憑證服務類別的方法調用問題
  - 將 CredentialService 中的靜態方法改為實例方法，支援依賴注入模式
  - 修正服務類別的初始化方式，接受資料庫 session 參數
  - 統一錯誤處理方式，使用 ValueError 替代 HTTPException
  - 確保憑證管理 API 能正常返回資料
- 2025-05-23: 修復資料庫結構不一致問題
  - 建立資料庫遷移腳本 migrate_db.py，自動檢查並新增缺少的欄位
  - 新增 chat_links 表的 webhook_url 和 credential_id 欄位
  - 新增 credentials 表的外鍵約束
  - 修復前端 Dashboard 頁面因資料庫欄位缺失導致的錯誤
- 2025-05-23: 修復前端依賴問題
  - 安裝缺少的 lodash-es 套件，解決 Credentials.vue 中 debounce 函數的導入錯誤
  - 確保前端開發服務器能正常啟動
- 2025-05-23: 修復憑證管理功能的導入錯誤
  - 修正 credential_routes.py 中的 require_admin 導入錯誤，改為使用 get_current_admin_user_dependency
  - 移除不存在的 LogService 依賴，改為直接使用 OperationLog 模型記錄日誌
  - 確保憑證管理 API 能正常運行並與其他模組保持一致
- 2025-05-21: 修復 AD 帳號登入功能無法被點擊使用的問題
  - 移除 Login.vue 中 AD 標籤的 disabled 屬性，使 AD 標籤始終可點擊
  - 修正 onMounted 函數中獲取 AD 設定狀態的程式碼，確保正確處理 API 回應
  - 確保 AD 登入功能不受 AD 設定狀態的影響，提高使用者體驗
- 2025-05-21: 專案程式碼清理
  - 移除所有 __pycache__ 目錄和編譯檔案，減少專案體積
  - 為空的 services/__init__.py 添加模組說明註釋，提高程式碼可讀性
  - 保留前端原型設計及介面，以備日後參考
- 2025-05-20: 修復群組成員管理功能中的 422 錯誤問題
  - 修正後端 API 參數限制，將 `/api/users` 端點的 `page_size` 參數上限從 100 調整為 1000
  - 修正前端獲取使用者的方式，使用正確的分頁參數
  - 增加分頁處理，支援獲取超過單頁限制的使用者
  - 增加詳細的錯誤處理和日誌輸出
- 2025-05-20: 增強群組成員管理功能的穩定性和可靠性
  - 修改 `fetchGroupUsers` 函數，增加錯誤處理和更詳細的日誌
  - 新增資料一致性檢查，當發現群組有成員但顯示為空時，嘗試直接從 API 獲取群組詳情
  - 重置成員 ID 列表，確保每次打開對話框時都是最新資料
  - 增加診斷功能，顯示資料處理的每個步驟
- 2025-05-19: 改進使用者管理介面中的群組選擇功能，現在可更清楚顯示每個群組的權限資訊
- 2025-05-19: 改進群組管理介面中的成員管理功能，優化使用者體驗和效能
- 2025-05-18: 升級功能圖示，使用更具代表性的圖示並優化展示效果，使側邊欄收合時清晰顯示圖示
- 2025-05-18: 修正側邊欄收合後功能圖示不顯示的問題，移除 v-list-item 的 prepend-icon 屬性，改用 v-slot:prepend 顯示圖示
- 2025-05-17: 修復後端啟動時的驗證錯誤，在 Settings.Config 中設定 extra = "ignore" 允許額外的環境變數
- 2025-05-17: 整合多個 .env 檔案為一個，修改 run.py 和 config.py 以指向根目錄的 .env 檔案
- 2025-05-17: 整合環境變數設定到單一 .env 檔案，修改 vite.config.js 使前端從根目錄讀取環境變數
- 2025-05-16: 整合環境變數設定，建立 setup_env.ps1 腳本自動生成 .env 檔案，確保所有設定集中管理
- 2025-05-15: 修改前端程式碼，使其從環境變數讀取 API 基礎 URL，避免硬編碼
- 2025-05-15: 修正前端操作紀錄頁面，使其與後端 API 的新資料結構一致
- 2025-05-15: 修正操作紀錄 API 的資料格式問題，解決 ResponseValidationError
- 2025-05-15: 修正用戶操作紀錄 API 的資料結構，確保與其他操作紀錄 API 一致
- 2025-05-15: 修正前端 UserHistory.vue 中的代碼，使其正確處理後端回傳的操作紀錄資料
- 2025-05-15: 修正 .env 檔案的編碼問題，確保正確讀取環境變數
- 2025-05-15: 更新後端 CORS 設定，允許更多前端來源 (localhost 和 127.0.0.1 的不同端口)
- 2025-05-15: 改進前端 token 處理邏輯，增加 token 過期檢查
- 2025-05-15: 增強前端錯誤處理和日誌記錄，提供更詳細的錯誤訊息
- 2025-05-06: 將 python-ldap 改為 ldap3，解決 Windows 環境下安裝需要 Microsoft Visual C++ 14.0 或更高版本的問題
- 2025-05-06: 添加 pydantic-settings 套件，解決 BaseSettings 已經從 pydantic 移動到 pydantic-settings 套件的問題
- 2025-05-06: 添加 pytz 套件，解決時區處理相關的依賴問題
- 2025-05-06: 在 Settings 類別中添加缺少的環境變數欄位，解決 pydantic 驗證錯誤
- 2025-05-06: 修改資料庫連線字串處理邏輯，將 postgres:// 協議改為 postgresql://，以符合 SQLAlchemy 的要求
- 2025-05-07: 將所有 schema 文件中的 `orm_mode = True` 替換為 `from_attributes = True`，以適應 Pydantic v2 的變化
- 2025-05-07: 修改 `security.py` 中的 `verify_token` 函數，使其返回一個簡單的字典而不是嘗試創建一個不完整的 `UserInDB` 對象，解決 `/api/auth/login` 端點的錯誤
- 2025-05-14: 在前端 main.js 中添加 axios 全局配置，設置基本 URL 和請求/響應攔截器
- 2025-05-14: 修改 Login.vue 組件，使用全局註冊的 axios 進行 API 調用
- 2025-05-14: 創建環境變數文件 .env，配置必要的後端參數

### 已完成

- 後端 API 開發 (2025-05-07)
  - 使用者管理 API
  - 群組管理 API
  - 聊天連結管理 API
  - AD 設定 API
  - 操作紀錄 API
  - 認證與授權機制
- 前端介面開發 (2025-05-14)
  - 管理員介面
  - 使用者介面
  - 前後端整合
- 錯誤修復與優化 (2025-05-15)
  - 環境變數編碼問題
  - CORS 設定優化
  - Token 處理邏輯改進
  - 錯誤處理增強
  - 操作紀錄 API 修正
  - 前端操作紀錄頁面修正
- 環境變數整合 (2025-05-17)
  - 整合多個 .env 檔案為單一檔案
  - 優化前端和後端的環境變數讀取方式
  - 修復環境變數驗證錯誤
- 使用者和群組管理功能優化 (2025-05-19)
  - 使用者管理介面中的群組選擇功能優化
  - 群組管理介面中的成員管理功能優化
  - 批量操作功能實作
  - 使用者體驗改進
- 群組成員管理功能修復 (2025-05-20)
  - 修復 422 錯誤問題
  - 增強功能穩定性和可靠性
  - 改進錯誤處理和診斷

### 待開發

- 資料庫遷移腳本
- 單元測試
- 部署文件
- 效能優化
- 安全性增強
  - 密碼加密存儲
  - CORS 設定優化
  - 輸入驗證強化

## [2025-06-01] - 使用者紀錄功能修正與專案清理

### 🐛 問題修正
- **修正使用者無法查看自己操作紀錄的問題**
  - 問題原因：使用者紀錄 API 路由使用了管理者權限檢查 (`get_current_admin_user`)，導致一般使用者無法存取
  - 解決方案：建立新的路由檔案 `user_profile_routes.py`，專門處理使用者個人資料相關 API
  - 新增路由：`/api/user-profiles/operation-logs` 和 `/api/user-profiles/chat-history`
  - 使用 `get_current_user` 權限檢查，允許一般使用者存取自己的資料

### 🔧 架構改善
- **API 路由重構**
  - 將使用者個人資料相關 API 從 `/api/users/` 移至 `/api/user-profiles/`
  - 明確區分管理者專用 API (`/api/users/`) 和使用者個人 API (`/api/user-profiles/`)
  - 移除 `user_routes.py` 中重複的個人資料 API

### 🧹 專案清理
- **移除冗餘檔案**
  - 刪除臨時測試檔案：`test_api.py`
  - 刪除已完成的遷移檔案：
    - `migrate_chat_link_types.py`
    - `test_chat_link_types.py`
    - `backend/migrate_chat_tables.py`
    - `backend/migrate_db.py`
  - 移除前端除錯程式碼：清理 `UserHistory.vue` 中的 console.log 語句

### ✅ 功能驗證
- 使用者現在可以正常查看自己的操作紀錄和聊天紀錄
- 管理者仍可查看所有使用者的操作紀錄
- API 權限控制正確運作
- 前後端架構分工明確

### 📁 檔案異動
- 新增：`backend/app/apis/user_profile_routes.py`
- 修改：`backend/app/main.py` (新增路由註冊)
- 修改：`frontend/src/views/user/UserHistory.vue` (更新 API 路徑)
- 修改：`backend/app/apis/user_routes.py` (移除重複 API)
- 刪除：多個冗餘檔案

---

## [2025-05-28] - 聊天功能超時配置與憑證選擇驗證

## [未發布] - 2025-04-20

### 移除
- **移除冗餘依賴套件**: 清理專案中不必要的依賴，簡化部署流程
  - 從 `backend/requirements.txt` 移除 `requests==2.31.0` (專案使用 httpx 替代)
  - 從 `backend/requirements.txt` 移除 `email-validator==2.1.0` (專案未使用電子郵件驗證功能)
  - 從 `backend/requirements.txt` 移除 `alembic==1.12.1` (專案使用 SQLAlchemy create_all() 方法)
  - 更新 `DEPLOYMENT.md` 中的套件驗證指令，移除已刪除的套件
  - 簡化資料庫初始化說明，移除 alembic 相關註解
- **移除不必要的 aiohttp 依賴**: 專案實際使用 httpx 處理 HTTP 請求，aiohttp 為冗餘套件
  - 從 `backend/requirements.txt` 移除 `aiohttp==3.9.0`
  - 從 `DEPLOYMENT.md` 移除所有 aiohttp 編譯錯誤的解決方案說明
  - 簡化部署流程，避免不必要的編譯問題

- 2025-06-13: 新增佈署注意事項
  - 明確記錄前端環境變數（API 位置）修改後需重新 build
  - 新增後端 CORS 設定需允許前端網域的說明
  - 新增常見錯誤（CORS、API 位置）排查步驟
