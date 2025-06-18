# HLAIChat 資料庫部署腳本
# 作用：在資料庫主機上設置 PostgreSQL 和專案資料庫
# 使用方式：在資料庫主機上以管理員權限執行此腳本
# 執行環境：Windows Server 2019/2022 或 Windows 10/11
# 編碼：UTF-8

param(
    [string]$DatabaseHost = "192.168.5.111",
    [string]$DatabaseUser = "postgres", 
    [string]$DatabasePassword = "H@nlin711",
    [string]$DatabaseName = "hlaichat-py",
    [string]$PostgreSQLVersion = "15"
)

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "HLAIChat 資料庫部署腳本" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# 檢查是否以管理員權限執行
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "此腳本需要以管理員權限執行！"
    Write-Host "請以管理員身分開啟 PowerShell 後重新執行。" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "步驟 1: 檢查 PostgreSQL 安裝狀態..." -ForegroundColor Green

# 檢查 PostgreSQL 是否已安裝
$postgresService = Get-Service postgresql* -ErrorAction SilentlyContinue
if ($postgresService) {
    Write-Host "PostgreSQL 服務已存在：$($postgresService.Name)" -ForegroundColor Yellow
    Write-Host "狀態：$($postgresService.Status)" -ForegroundColor Yellow
} else {
    Write-Host "未偵測到 PostgreSQL 服務" -ForegroundColor Red
    Write-Host "請先從官網下載並安裝 PostgreSQL:" -ForegroundColor Yellow
    Write-Host "https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    Write-Host "安裝時請設定管理員密碼為：$DatabasePassword" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "步驟 2: 啟動 PostgreSQL 服務..." -ForegroundColor Green

# 啟動 PostgreSQL 服務
try {
    Start-Service $postgresService.Name -ErrorAction Stop
    Write-Host "PostgreSQL 服務啟動成功" -ForegroundColor Green
} catch {
    Write-Error "PostgreSQL 服務啟動失敗：$($_.Exception.Message)"
    pause
    exit 1
}

Write-Host "步驟 3: 設定防火牆規則..." -ForegroundColor Green

# 設定防火牆規則，允許 PostgreSQL 連線
try {
    $firewallRule = Get-NetFirewallRule -DisplayName "PostgreSQL" -ErrorAction SilentlyContinue
    if (-not $firewallRule) {
        New-NetFirewallRule -DisplayName "PostgreSQL" -Direction Inbound -Protocol TCP -LocalPort 5432 -Action Allow
        Write-Host "防火牆規則設定完成" -ForegroundColor Green
    } else {
        Write-Host "防火牆規則已存在" -ForegroundColor Yellow
    }
} catch {
    Write-Warning "防火牆規則設定失敗：$($_.Exception.Message)"
}

Write-Host "步驟 4: 配置 PostgreSQL 連線設定..." -ForegroundColor Green

# 尋找 PostgreSQL 安裝路徑
$postgresPath = ""
$possiblePaths = @(
    "C:\Program Files\PostgreSQL\$PostgreSQLVersion",
    "C:\Program Files\PostgreSQL\14",
    "C:\Program Files\PostgreSQL\13",
    "C:\Program Files (x86)\PostgreSQL\$PostgreSQLVersion"
)

foreach ($path in $possiblePaths) {
    if (Test-Path "$path\data\postgresql.conf") {
        $postgresPath = $path
        break
    }
}

if (-not $postgresPath) {
    Write-Warning "找不到 PostgreSQL 安裝路徑，請手動配置 postgresql.conf 和 pg_hba.conf"
    Write-Host "需要修改的設定："
    Write-Host "postgresql.conf: listen_addresses = '*'" -ForegroundColor Yellow
    Write-Host "pg_hba.conf: 新增允許的主機連線規則" -ForegroundColor Yellow
} else {
    Write-Host "找到 PostgreSQL 安裝路徑：$postgresPath" -ForegroundColor Green
    
    # 備份原始配置檔案
    $configPath = "$postgresPath\data\postgresql.conf"
    $hbaPath = "$postgresPath\data\pg_hba.conf"
    
    if (Test-Path $configPath) {
        Copy-Item $configPath "$configPath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')" -Force
        Write-Host "已備份 postgresql.conf" -ForegroundColor Green
    }
    
    if (Test-Path $hbaPath) {
        Copy-Item $hbaPath "$hbaPath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')" -Force
        Write-Host "已備份 pg_hba.conf" -ForegroundColor Green
    }
    
    # 修改 postgresql.conf
    try {
        $configContent = Get-Content $configPath
        $configContent = $configContent -replace "^#?listen_addresses = .*", "listen_addresses = '*'"
        $configContent = $configContent -replace "^#?port = .*", "port = 5432"
        $configContent | Set-Content $configPath
        Write-Host "postgresql.conf 配置完成" -ForegroundColor Green
    } catch {
        Write-Warning "postgresql.conf 配置失敗：$($_.Exception.Message)"
    }
    
    # 修改 pg_hba.conf，新增允許的主機連線
    try {
        $hbaContent = Get-Content $hbaPath
        $newRules = @(
            "# HLAIChat 專案主機連線規則",
            "host    all             all             192.168.5.107/32        md5",
            "host    all             all             192.168.5.54/32         md5"
        )
        
        # 檢查規則是否已存在
        if ($hbaContent -notcontains $newRules[1]) {
            $hbaContent += $newRules
            $hbaContent | Set-Content $hbaPath
            Write-Host "pg_hba.conf 配置完成" -ForegroundColor Green
        } else {
            Write-Host "pg_hba.conf 規則已存在" -ForegroundColor Yellow
        }
    } catch {
        Write-Warning "pg_hba.conf 配置失敗：$($_.Exception.Message)"
    }
}

Write-Host "步驟 5: 重新啟動 PostgreSQL 服務..." -ForegroundColor Green

# 重新啟動 PostgreSQL 以套用設定
try {
    Restart-Service $postgresService.Name -Force
    Start-Sleep -Seconds 5
    Write-Host "PostgreSQL 服務重新啟動完成" -ForegroundColor Green
} catch {
    Write-Error "PostgreSQL 服務重新啟動失敗：$($_.Exception.Message)"
    pause
    exit 1
}

Write-Host "步驟 6: 建立專案資料庫..." -ForegroundColor Green

# 尋找 psql 執行檔
$psqlPath = ""
if ($postgresPath) {
    $psqlPath = "$postgresPath\bin\psql.exe"
}

if (-not (Test-Path $psqlPath)) {
    Write-Warning "找不到 psql 執行檔，請手動建立資料庫"
    Write-Host "請執行以下 SQL 指令："
    Write-Host "CREATE DATABASE `"$DatabaseName`" WITH ENCODING 'UTF8';" -ForegroundColor Yellow
} else {
    # 設定密碼環境變數
    $env:PGPASSWORD = $DatabasePassword
    
    # 檢查資料庫是否已存在
    $checkDbCmd = "SELECT 1 FROM pg_database WHERE datname='$DatabaseName';"
    $dbExists = & $psqlPath -h localhost -U $DatabaseUser -t -c $checkDbCmd 2>$null
    
    if ($dbExists -match "1") {
        Write-Host "資料庫 '$DatabaseName' 已存在" -ForegroundColor Yellow
    } else {
        # 建立資料庫
        $createDbCmd = "CREATE DATABASE `"$DatabaseName`" WITH ENCODING 'UTF8';"
        $result = & $psqlPath -h localhost -U $DatabaseUser -c $createDbCmd 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "資料庫 '$DatabaseName' 建立成功" -ForegroundColor Green
        } else {
            Write-Error "資料庫建立失敗：$result"
            pause
            exit 1
        }
    }
    
    # 清除密碼環境變數
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
}

Write-Host "步驟 7: 測試資料庫連線..." -ForegroundColor Green

# 測試本地連線
try {
    $testConnection = Test-NetConnection -ComputerName localhost -Port 5432 -InformationLevel Quiet
    if ($testConnection) {
        Write-Host "本地資料庫連線測試成功" -ForegroundColor Green
    } else {
        Write-Warning "本地資料庫連線測試失敗"
    }
} catch {
    Write-Warning "連線測試失敗：$($_.Exception.Message)"
}

# 測試遠端連線（從其他主機測試）
Write-Host "步驟 8: 建立備份目錄..." -ForegroundColor Green

# 建立備份目錄
$backupDir = "E:\Backups"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force
    Write-Host "備份目錄建立完成：$backupDir" -ForegroundColor Green
} else {
    Write-Host "備份目錄已存在：$backupDir" -ForegroundColor Yellow
}

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "資料庫部署完成！" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan

Write-Host "部署結果摘要：" -ForegroundColor White
Write-Host "- 資料庫主機：$DatabaseHost" -ForegroundColor White
Write-Host "- 資料庫名稱：$DatabaseName" -ForegroundColor White
Write-Host "- 資料庫使用者：$DatabaseUser" -ForegroundColor White
Write-Host "- 連線埠號：5432" -ForegroundColor White
Write-Host "- 備份目錄：$backupDir" -ForegroundColor White

Write-Host "`n後續步驟：" -ForegroundColor Yellow
Write-Host "1. 請在後端主機執行 deploy_backend.ps1 腳本" -ForegroundColor Yellow
Write-Host "2. 測試從後端主機連線到此資料庫" -ForegroundColor Yellow
Write-Host "3. 如有防火牆或網路問題，請檢查網路設定" -ForegroundColor Yellow

Write-Host "`n連線字串範例：" -ForegroundColor Cyan
Write-Host "postgresql://$DatabaseUser`:$DatabasePassword@$DatabaseHost`:5432/$DatabaseName" -ForegroundColor Cyan

pause 