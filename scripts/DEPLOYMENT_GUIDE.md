# HLAIChat 管理平台部署指南

## 目錄
1. [系統概述](#系統概述)
2. [系統需求](#系統需求)
3. [部署腳本說明](#部署腳本說明)
4. [部署流程](#部署流程)
5. [服務管理](#服務管理)
6. [故障排除](#故障排除)
7. [維護指南](#維護指南)

## 系統概述

### 生產環境主機配置
- **前端主機**: acm1.hanlin.com.tw (192.168.5.54)
- **後端主機**: acmback1.hanlin.com.tw (192.168.5.107)
- **資料庫主機**: acmdb1.hanlin.com.tw (192.168.5.111)

### 架構說明
本專案採用前後端分離架構：
- **前端**: Vue.js 3 + Vuetify 3 + IIS/Node.js
- **後端**: FastAPI + SQLAlchemy + NSSM Windows Service
- **資料庫**: PostgreSQL
- **認證**: AD 網域驗證整合

## 系統需求

### 資料庫主機 (acmdb1.hanlin.com.tw)
- Windows Server 2019/2022 或 Windows 10/11
- PostgreSQL 15+ 
- 最少 8GB RAM，50GB 磁碟空間

### 後端主機 (acmback1.hanlin.com.tw)
- Windows Server 2019/2022 或 Windows 10/11
- Python 3.9-3.11 (避免 3.12)
- 最少 8GB RAM，20GB 磁碟空間

### 前端主機 (acm1.hanlin.com.tw)
- Windows Server 2019/2022 或 Windows 10/11
- Node.js 18.x+
- IIS with URL Rewrite Module (可選)
- 最少 4GB RAM，10GB 磁碟空間

## 部署腳本說明

本專案提供完整的 PowerShell 自動化部署腳本，位於 `scripts/` 目錄：

### 主要腳本

#### 1. deploy_full.ps1 - 整合部署腳本 (推薦使用)
**用途**: 提供互動式選單，支援完整或選擇性部署

**主要參數**:
```powershell
-ProjectPath "E:\projects\hlaichat-py"    # 專案路徑
-DatabaseHost "192.168.5.111"            # 資料庫主機
-BackendHost "192.168.5.107"             # 後端主機  
-FrontendHost "192.168.5.54"             # 前端主機
-Mode [Interactive|Auto]                 # 執行模式
-DeployTarget [database|backend|frontend|all]  # 部署目標
```

**功能特色**:
- ✅ 互動式選單介面
- ✅ 支援分步驟或完整部署
- ✅ 自動環境檢查
- ✅ 詳細部署日誌
- ✅ 部署時間統計
- ✅ 服務狀態驗證

#### 2. deploy_database.ps1 - 資料庫部署腳本
**用途**: PostgreSQL 資料庫初始化和配置

**功能**:
- 檢查 PostgreSQL 安裝狀態
- 設定防火牆規則 (5432 埠)
- 配置遠端連線
- 建立專案資料庫和使用者
- 初始化資料表結構

#### 3. deploy_backend.ps1 - 後端部署腳本
**用途**: FastAPI 後端應用程式部署

**主要參數**:
```powershell
-StartMode [Service|Manual]              # 啟動模式
-SkipDB                                  # 跳過資料庫初始化
-ForceClean                              # 強制清理環境
```

**功能**:
- Python 虛擬環境建立
- 依賴套件安裝
- 環境變數配置
- NSSM Windows 服務設定
- 防火牆規則設定 (8000 埠)

#### 4. deploy_frontend.ps1 - 前端部署腳本
**用途**: Vue.js 前端應用程式部署

**主要參數**:
```powershell
-WebServer [IIS|NodeJS]                  # 網頁伺服器類型
-SkipBuild                               # 跳過建置程序
-ForceClean                              # 強制清理 node_modules
```

**功能**:
- Node.js 環境檢查
- 前端依賴安裝和建置
- IIS 或 Node.js 伺服器配置
- URL Rewrite 規則設定
- 防火牆規則設定

#### 5. manage_services.ps1 - 服務管理腳本
**用途**: 系統服務的統一管理介面

**功能**:
- 服務狀態檢查
- 批次服務管理 (啟動/停止/重啟)
- 服務日誌檢視
- 效能監控

## 部署流程

### 🚀 快速開始 - 一鍵部署

```powershell
# 以管理員權限開啟 PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 進入專案目錄
cd E:\projects\hlaichat-py

# 執行完整部署
.\scripts\deploy_full.ps1 -DeployTarget all
```

### 多主機生產環境部署

#### 步驟 1: 資料庫主機部署 (192.168.5.111)
```powershell
# 在資料庫主機執行
.\scripts\deploy_full.ps1 -DeployTarget database
```

**前置作業**:
- 下載並安裝 PostgreSQL 15+
- 設定管理員密碼：`H@nlin711`
- 確認防火牆開放 5432 埠

#### 步驟 2: 後端主機部署 (192.168.5.107)
```powershell
# 在後端主機執行
.\scripts\deploy_full.ps1 -DeployTarget backend
```

**前置作業**:
- 安裝 Python 3.9-3.11
- 確保勾選 "Add Python to PATH"
- 確認與資料庫主機的網路連通性

#### 步驟 3: 前端主機部署 (192.168.5.54)
```powershell
# 在前端主機執行
.\scripts\deploy_full.ps1 -DeployTarget frontend
```

**前置作業**:
- 安裝 Node.js 18.x LTS
- 啟用 IIS 功能 (選用)
- 安裝 URL Rewrite 模組 (IIS 用)

### 單主機開發環境部署

```powershell
# 適用於開發或測試環境
.\scripts\deploy_full.ps1 -DeployTarget all -DatabaseHost "localhost" -BackendHost "localhost" -FrontendHost "localhost"
```

### 部署驗證

部署完成後，檢查各項服務：

```powershell
# 檢查所有服務狀態
.\scripts\manage_services.ps1 -Action status

# 檢查網站連線
# 前端: http://192.168.5.54 或 http://localhost:3000
# 後端 API: http://192.168.5.107:8000/docs
# 資料庫: psql -h 192.168.5.111 -U postgres -d hlaichat-py
```

## 服務管理

### 🔧 服務管理腳本使用

```powershell
# 互動式服務管理
.\scripts\manage_services.ps1

# 命令列服務管理
.\scripts\manage_services.ps1 -Action [start|stop|restart|status]
.\scripts\manage_services.ps1 -Action [start|stop|restart|status] -Service [database|backend|frontend]
```

### 手動服務管理

#### 後端服務 (NSSM Windows Service)
```powershell
nssm start hlaichat-backend      # 啟動
nssm stop hlaichat-backend       # 停止
nssm restart hlaichat-backend    # 重啟
nssm status hlaichat-backend     # 狀態查詢
nssm edit hlaichat-backend       # 編輯服務配置
```

#### 前端服務 (IIS)
```powershell
Start-Website "HLAIChat Frontend"         # 啟動網站
Stop-Website "HLAIChat Frontend"          # 停止網站
Restart-WebAppPool "HLAIChatFrontend"     # 重啟應用程式集區
Get-Website | Where-Object {$_.Name -like "*HLAIChat*"}  # 查詢網站狀態
```

#### 前端服務 (Node.js + PM2)
```powershell
pm2 start ecosystem.config.js    # 啟動
pm2 stop hlaichat-frontend      # 停止
pm2 restart hlaichat-frontend   # 重啟
pm2 status                      # 狀態查詢
pm2 logs hlaichat-frontend      # 查看日誌
```

#### 資料庫服務 (PostgreSQL)
```powershell
Start-Service postgresql*        # 啟動
Stop-Service postgresql*         # 停止
Restart-Service postgresql*      # 重啟
Get-Service postgresql*          # 狀態查詢
```

## 故障排除

### PowerShell 執行原則問題
```powershell
# 設定執行原則
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 暫時允許執行
PowerShell -ExecutionPolicy Bypass -File .\scripts\deploy_full.ps1
```

### 編碼問題
```powershell
# 設定 UTF-8 編碼
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001
```

### 網路連線問題

#### 檢查防火牆規則
```powershell
# 檢查現有規則
Get-NetFirewallRule -DisplayName "*HLAIChat*"

# 手動新增規則
New-NetFirewallRule -DisplayName "HLAIChat Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
New-NetFirewallRule -DisplayName "HLAIChat Frontend" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "PostgreSQL" -Direction Inbound -Protocol TCP -LocalPort 5432 -Action Allow
```

#### 測試連線
```powershell
# 測試後端 API
Invoke-RestMethod -Uri "http://192.168.5.107:8000/health" -Method GET

# 測試資料庫連線
Test-NetConnection -ComputerName "192.168.5.111" -Port 5432

# 測試前端網站
Invoke-WebRequest -Uri "http://192.168.5.54" -UseBasicParsing
```

### 常見錯誤解決

#### Python 相關
```powershell
# 虛擬環境建立失敗
python -m venv E:\venv\hlaichat_backend_venv --clear

# 套件安裝失敗
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### Node.js 相關
```powershell
# 清理快取
npm cache clean --force

# 重新安裝依賴
Remove-Item -Path "node_modules" -Recurse -Force
npm install
```

#### PostgreSQL 相關
```powershell
# 重設密碼
psql -U postgres -c "ALTER USER postgres PASSWORD 'hl69382361';"

# 檢查服務狀態
Get-Service postgresql*
```

## 維護指南

### 定期維護任務

#### 每日檢查
```powershell
# 檢查服務狀態
.\scripts\manage_services.ps1 -Action status

# 檢查日誌
Get-EventLog -LogName Application -Source "*HLAIChat*" -Newest 10
```

#### 每週維護
```powershell
# 資料庫備份
pg_dump -h 192.168.5.111 -U postgres -d hlaichat-py > "backup_$(Get-Date -Format 'yyyyMMdd').sql"

# 清理日誌檔案
Get-ChildItem -Path "logs\" -Filter "*.log" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
```

#### 更新部署
```powershell
# 更新後端 (不影響資料庫)
.\scripts\deploy_backend.ps1 -SkipDB

# 更新前端 (強制重建)
.\scripts\deploy_frontend.ps1 -ForceClean

# 完整更新 (保留資料)
.\scripts\deploy_full.ps1 -DeployTarget backend,frontend
```

### 效能監控

#### 系統資源監控
```powershell
# CPU 和記憶體使用率
Get-Counter "\Processor(_Total)\% Processor Time"
Get-Counter "\Memory\Available MBytes"

# 網路連線監控
Get-Counter "\Network Interface(*)\Bytes Total/sec"
```

#### 應用程式監控
```powershell
# 後端服務日誌
Get-Content -Path "backend\logs\app.log" -Tail 50 -Wait

# 前端存取日誌 (IIS)
Get-Content -Path "C:\inetpub\logs\LogFiles\W3SVC1\*.log" -Tail 20

# 資料庫連線數
psql -h 192.168.5.111 -U postgres -d hlaichat-py -c "SELECT count(*) FROM pg_stat_activity;"
```

### 災難恢復

#### 備份策略
```powershell
# 完整備份腳本
$BackupPath = "E:\Backups\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -Path $BackupPath -ItemType Directory

# 資料庫備份
pg_dump -h 192.168.5.111 -U postgres -d hlaichat-py > "$BackupPath\database.sql"

# 配置檔備份
Copy-Item -Path ".env" -Destination "$BackupPath\"
Copy-Item -Path "backend\logs" -Destination "$BackupPath\" -Recurse
```

#### 恢復程序
```powershell
# 資料庫恢復
psql -h 192.168.5.111 -U postgres -d hlaichat-py < "backup_database.sql"

# 重新部署應用程式
.\scripts\deploy_full.ps1 -DeployTarget backend,frontend
```

---

## 支援資訊

- **專案文件**: README.md
- **變更歷程**: CHANGELOG.md
- **技術支援**: 請聯繫系統管理員
- **問題回報**: 請建立詳細的錯誤報告，包含日誌檔案

---

**最後更新**: 2024年12月
**版本**: 1.0
**維護者**: HLAIChat 開發團隊 