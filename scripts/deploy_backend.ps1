# 後端部署腳本 - Backend Deployment Script
# 版本: 2.0
# 編碼: UTF-8
# 說明: 用於部署 FastAPI 後端應用程式到 Windows 伺服器

param(
    [string]$ProjectPath = "E:\projects\hlaichat-py",
    [string]$BackendHost = "192.168.5.107",
    [string]$BackendPort = "8000",
    [string]$DatabaseHost = "192.168.1.221",
    [string]$StartMode = "Service",  # Service 或 Manual
    [switch]$SkipDB,
    [switch]$ForceClean
)

# 設定控制台編碼為 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 顏色設定
$SuccessColor = "Green"
$ErrorColor = "Red"
$InfoColor = "Cyan"
$WarningColor = "Yellow"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Test-AdminRights {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Stop-OnError {
    param([string]$Message)
    Write-ColorOutput "錯誤: $Message" $ErrorColor
    exit 1
}

# 檢查管理員權限
if (-not (Test-AdminRights)) {
    Stop-OnError "需要管理員權限執行此腳本。請以管理員身份重新執行。"
}

Write-ColorOutput "===============================================" $InfoColor
Write-ColorOutput "          HLAIChat 後端部署腳本" $InfoColor
Write-ColorOutput "===============================================" $InfoColor
Write-ColorOutput "專案路徑: $ProjectPath" $InfoColor
Write-ColorOutput "後端主機: ${BackendHost}:${BackendPort}" $InfoColor
Write-ColorOutput "資料庫主機: $DatabaseHost" $InfoColor
Write-ColorOutput "啟動模式: $StartMode" $InfoColor
Write-ColorOutput "===============================================" $InfoColor

# 設定路徑
$BackendPath = Join-Path $ProjectPath "backend"
$RequirementsPath = Join-Path $BackendPath "requirements.txt"
$VenvPath = Join-Path $BackendPath "venv"

# 檢查專案目錄
if (-not (Test-Path $ProjectPath)) {
    Stop-OnError "專案目錄不存在: $ProjectPath"
}

if (-not (Test-Path $BackendPath)) {
    Stop-OnError "後端目錄不存在: $BackendPath"
}

Write-ColorOutput "`n[步驟 1] 檢查 Python 環境..." $InfoColor

# 檢查 Python
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+)") {
        $version = [Version]$matches[1]
        Write-ColorOutput "Python 版本: $pythonVersion" $SuccessColor
        
        if ($version -lt [Version]"3.9") {
            Stop-OnError "Python 版本過舊，需要 Python 3.9 或更高版本"
        }
    } else {
        Stop-OnError "無法取得 Python 版本資訊"
    }
} catch {
    Stop-OnError "Python 未安裝或不在 PATH 中"
}

# 檢查 pip
try {
    $pipVersion = pip --version
    Write-ColorOutput "pip 版本: $pipVersion" $SuccessColor
} catch {
    Stop-OnError "pip 未安裝或不在 PATH 中"
}

Write-ColorOutput "`n[步驟 2] 建立虛擬環境..." $InfoColor

# 切換到後端目錄
Set-Location $BackendPath

# 清理舊的虛擬環境 (如果需要)
if ($ForceClean -and (Test-Path $VenvPath)) {
    Write-ColorOutput "清理舊的虛擬環境..." $WarningColor
    Remove-Item $VenvPath -Recurse -Force
}

# 建立虛擬環境
if (-not (Test-Path $VenvPath)) {
    Write-ColorOutput "建立新的虛擬環境..." $InfoColor
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Stop-OnError "虛擬環境建立失敗"
    }
    Write-ColorOutput "虛擬環境建立完成" $SuccessColor
} else {
    Write-ColorOutput "虛擬環境已存在" $InfoColor
}

# 啟動虛擬環境
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    & $ActivateScript
    Write-ColorOutput "虛擬環境已啟動" $SuccessColor
} else {
    Stop-OnError "找不到虛擬環境啟動腳本"
}

Write-ColorOutput "`n[步驟 3] 安裝依賴套件..." $InfoColor

# 檢查 requirements.txt
if (-not (Test-Path $RequirementsPath)) {
    Stop-OnError "找不到 requirements.txt: $RequirementsPath"
}

# 升級 pip
Write-ColorOutput "升級 pip..." $InfoColor
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput "pip 升級失敗，嘗試繼續..." $WarningColor
}

# 安裝依賴
Write-ColorOutput "安裝 Python 套件..." $InfoColor
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Stop-OnError "依賴套件安裝失敗"
}
Write-ColorOutput "Python 套件安裝完成" $SuccessColor

Write-ColorOutput "`n[步驟 4] 檢查環境變數檔案..." $InfoColor

# 檢查 .env 檔案
$EnvFile = Join-Path $ProjectPath ".env"
if (-not (Test-Path $EnvFile)) {
    Write-ColorOutput "環境變數檔案不存在，建立基本配置..." $WarningColor
    
    # 建立基本 .env 檔案
    $envContent = @"
# 資料庫配置
DATABASE_URL=postgresql://postgres:hl69382361@$DatabaseHost:5432/hlaichat-py

# 後端伺服器配置
BACKEND_HOST=$BackendHost
BACKEND_PORT=$BackendPort

# AD 網域配置 (可選)
# AD_DOMAIN=hanlin.com.tw
# AD_SERVERS=192.168.1.6,192.168.1.5,192.168.5.5
# AD_BIND_USER=
# AD_BIND_PASSWORD=

# 應用程式設定
APP_NAME=HLAIChat
APP_VERSION=1.0.0
DEBUG=false
"@
    
    [System.IO.File]::WriteAllText($EnvFile, $envContent, [System.Text.Encoding]::UTF8)
    Write-ColorOutput "已建立基本環境變數檔案: $EnvFile" $SuccessColor
} else {
    Write-ColorOutput "環境變數檔案已存在" $SuccessColor
}

# 初始化資料庫 (除非跳過)
if (-not $SkipDB) {
    Write-ColorOutput "`n[步驟 5] 初始化資料庫..." $InfoColor
    
    # 檢查資料庫連線
    Write-ColorOutput "測試資料庫連線..." $InfoColor
    try {
        $dbTest = Test-NetConnection -ComputerName $DatabaseHost -Port 5432 -InformationLevel Quiet -ErrorAction SilentlyContinue
        if ($dbTest) {
            Write-ColorOutput "資料庫連線正常" $SuccessColor
        } else {
            Write-ColorOutput "資料庫連線失敗，跳過資料庫初始化" $WarningColor
            $SkipDB = $true
        }
    } catch {
        Write-ColorOutput "資料庫連線測試失敗: $($_.Exception.Message)" $WarningColor
        $SkipDB = $true
    }
    
    if (-not $SkipDB) {
        # 執行資料庫初始化
        $InitDBScript = Join-Path $BackendPath "init_db.py"
        if (Test-Path $InitDBScript) {
            Write-ColorOutput "執行資料庫初始化..." $InfoColor
            python init_db.py
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "資料庫初始化完成" $SuccessColor
            } else {
                Write-ColorOutput "資料庫初始化失敗，請檢查資料庫設定" $WarningColor
            }
        } else {
            Write-ColorOutput "找不到資料庫初始化腳本" $WarningColor
        }
    }
} else {
    Write-ColorOutput "`n[步驟 5] 跳過資料庫初始化" $WarningColor
}

Write-ColorOutput "`n[步驟 6] 設定防火牆規則..." $InfoColor

# 設定防火牆規則
try {
    $ruleName = "HLAIChat Backend HTTP"
    $existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    if (-not $existingRule) {
        New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Protocol TCP -LocalPort $BackendPort -Action Allow | Out-Null
        Write-ColorOutput "防火牆規則設定完成: $BackendPort" $SuccessColor
    } else {
        Write-ColorOutput "防火牆規則已存在" $InfoColor
    }
} catch {
    Write-ColorOutput "防火牆規則設定失敗: $($_.Exception.Message)" $WarningColor
}

Write-ColorOutput "`n[步驟 7] 配置服務啟動..." $InfoColor

if ($StartMode -eq "Service") {
    # Windows 服務部署
    Write-ColorOutput "設定 Windows 服務..." $InfoColor
    
    # 檢查 NSSM
    try {
        nssm version | Out-Null
        Write-ColorOutput "NSSM 已安裝" $SuccessColor
    } catch {
        Write-ColorOutput "NSSM 未安裝，正在下載..." $InfoColor
        
        # 下載 NSSM
        $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
        $nssmZip = "$env:TEMP\nssm.zip"
        $nssmPath = "C:\nssm"
        
        try {
            Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip -UseBasicParsing
            Expand-Archive -Path $nssmZip -DestinationPath $env:TEMP -Force
            
            if (-not (Test-Path $nssmPath)) {
                New-Item -ItemType Directory -Path $nssmPath -Force
            }
            
            Copy-Item "$env:TEMP\nssm-2.24\win64\nssm.exe" -Destination "$nssmPath\nssm.exe" -Force
            
            # 新增到 PATH
            $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
            if ($currentPath -notlike "*$nssmPath*") {
                [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$nssmPath", "Machine")
                $env:PATH += ";$nssmPath"
            }
            
            Write-ColorOutput "NSSM 安裝完成" $SuccessColor
        } catch {
            Write-ColorOutput "NSSM 安裝失敗，將使用手動啟動模式" $WarningColor
            $StartMode = "Manual"
        }
    }
    
    if ($StartMode -eq "Service") {
        # 停止並移除舊服務
        try {
            nssm stop "HLAIChat Backend" 2>$null
            nssm remove "HLAIChat Backend" confirm 2>$null
        } catch {
            # 忽略錯誤
        }
        
        # 建立新服務
        $pythonExe = Join-Path $VenvPath "Scripts\python.exe"
        $runScript = Join-Path $BackendPath "run.py"
        
        nssm install "HLAIChat Backend" $pythonExe $runScript
        nssm set "HLAIChat Backend" AppDirectory $BackendPath
        nssm set "HLAIChat Backend" Description "HLAIChat 後端 API 服務"
        nssm set "HLAIChat Backend" Start SERVICE_AUTO_START
        
        # 啟動服務
        nssm start "HLAIChat Backend"
        
        Write-ColorOutput "Windows 服務設定完成" $SuccessColor
        Write-ColorOutput "服務名稱: HLAIChat Backend" $InfoColor
    }
} 

if ($StartMode -eq "Manual") {
    # 手動啟動模式
    Write-ColorOutput "建立手動啟動腳本..." $InfoColor
    
    # 建立啟動腳本
    $startScript = Join-Path $BackendPath "start_backend.ps1"
    $startContent = @"
# 後端手動啟動腳本
# 編碼: UTF-8

Set-Location '$BackendPath'

# 啟動虛擬環境
if (Test-Path 'venv\Scripts\Activate.ps1') {
    & 'venv\Scripts\Activate.ps1'
    Write-Host '虛擬環境已啟動' -ForegroundColor Green
} else {
    Write-Host '找不到虛擬環境' -ForegroundColor Red
    exit 1
}

# 啟動後端服務
Write-Host '正在啟動後端服務...' -ForegroundColor Green
Write-Host '服務網址: http://$BackendHost`:$BackendPort' -ForegroundColor Cyan
Write-Host 'API 文件: http://$BackendHost`:$BackendPort/docs' -ForegroundColor Cyan

python run.py
"@
    
    [System.IO.File]::WriteAllText($startScript, $startContent, [System.Text.Encoding]::UTF8)
    Write-ColorOutput "手動啟動腳本建立完成: $startScript" $SuccessColor
    
    # 建立停止腳本
    $stopScript = Join-Path $BackendPath "stop_backend.ps1"
    $stopContent = @"
# 後端停止腳本
# 編碼: UTF-8

Write-Host '正在停止後端服務...' -ForegroundColor Yellow

# 尋找並終止 Python 程序
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    `$_.MainModule.FileName -like "*venv*" -and `$_.MainModule.FileName -like "*hlaichat*"
} | Stop-Process -Force

Write-Host '後端服務已停止' -ForegroundColor Green
"@
    
    [System.IO.File]::WriteAllText($stopScript, $stopContent, [System.Text.Encoding]::UTF8)
    Write-ColorOutput "停止腳本建立完成: $stopScript" $SuccessColor
}

Write-ColorOutput "`n[步驟 8] 部署後驗證..." $InfoColor

# 等待服務啟動
Start-Sleep -Seconds 5

# 測試後端服務
$testUrl = "http://$BackendHost`:$BackendPort"
Write-ColorOutput "測試後端服務: $testUrl" $InfoColor

try {
    $response = Invoke-WebRequest -Uri "$testUrl/health" -TimeoutSec 10 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-ColorOutput "後端服務測試成功" $SuccessColor
    } else {
        Write-ColorOutput "後端服務回應狀態碼: $($response.StatusCode)" $WarningColor
    }
} catch {
    # 嘗試測試根路徑
    try {
        $response = Invoke-WebRequest -Uri $testUrl -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "後端服務測試成功" $SuccessColor
        } else {
            Write-ColorOutput "後端服務回應狀態碼: $($response.StatusCode)" $WarningColor
        }
    } catch {
        Write-ColorOutput "後端服務測試失敗: $($_.Exception.Message)" $WarningColor
        Write-ColorOutput "服務可能仍在啟動中，請稍後再試" $InfoColor
    }
}

Write-ColorOutput "`n===============================================" $InfoColor
Write-ColorOutput "          後端部署完成" $SuccessColor
Write-ColorOutput "===============================================" $InfoColor
Write-ColorOutput "後端服務: http://$BackendHost`:$BackendPort" $SuccessColor
Write-ColorOutput "API 文件: http://$BackendHost`:$BackendPort/docs" $SuccessColor
Write-ColorOutput "部署時間: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" $InfoColor

if ($StartMode -eq "Service") {
    Write-ColorOutput "`n服務管理指令:" $InfoColor
    Write-ColorOutput "  檢視狀態: nssm status `"HLAIChat Backend`"" $InfoColor
    Write-ColorOutput "  啟動服務: nssm start `"HLAIChat Backend`"" $InfoColor
    Write-ColorOutput "  停止服務: nssm stop `"HLAIChat Backend`"" $InfoColor
    Write-ColorOutput "  重新啟動: nssm restart `"HLAIChat Backend`"" $InfoColor
} else {
    Write-ColorOutput "`n手動管理指令:" $InfoColor
    Write-ColorOutput "  啟動服務: .\start_backend.ps1" $InfoColor
    Write-ColorOutput "  停止服務: .\stop_backend.ps1" $InfoColor
}

Write-ColorOutput "===============================================" $InfoColor 