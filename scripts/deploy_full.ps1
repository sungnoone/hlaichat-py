# 完整部署腳本 - Full Deployment Script
# 版本: 2.0
# 編碼: UTF-8
# 說明: 用於完整部署 HLAIChat 系統的所有組件

param(
    [string]$ProjectPath = "E:\projects\hlaichat-py",
    [string]$DatabaseHost = "192.168.1.221",
    [string]$BackendHost = "192.168.5.107",
    [string]$FrontendHost = "192.168.5.54",
    [string]$Mode = "Interactive",  # Interactive 或 Auto
    [switch]$SkipDatabase,
    [switch]$SkipBackend,
    [switch]$SkipFrontend
)

# 設定控制台編碼為 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 顏色設定
$SuccessColor = "Green"
$ErrorColor = "Red"
$InfoColor = "Cyan"
$WarningColor = "Yellow"
$HeaderColor = "Magenta"

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

function Show-Banner {
    Write-ColorOutput "=================================================" $HeaderColor
    Write-ColorOutput "           HLAIChat 完整部署系統" $HeaderColor
    Write-ColorOutput "=================================================" $HeaderColor
    Write-ColorOutput "版本: 2.0" $InfoColor
    Write-ColorOutput "部署時間: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" $InfoColor
    Write-ColorOutput "=================================================" $HeaderColor
}

function Show-Menu {
    Write-ColorOutput "`n請選擇部署選項:" $InfoColor
    Write-ColorOutput "1. 完整部署 (資料庫 + 後端 + 前端)" $InfoColor
    Write-ColorOutput "2. 僅部署資料庫" $InfoColor
    Write-ColorOutput "3. 僅部署後端" $InfoColor
    Write-ColorOutput "4. 僅部署前端" $InfoColor
    Write-ColorOutput "5. 部署後端 + 前端 (跳過資料庫)" $InfoColor
    Write-ColorOutput "6. 檢查系統狀態" $InfoColor
    Write-ColorOutput "0. 退出" $InfoColor
    Write-ColorOutput "-" $InfoColor
}

function Test-SystemStatus {
    Write-ColorOutput "`n正在檢查系統狀態..." $InfoColor
    
    # 檢查資料庫
    Write-ColorOutput "`n[資料庫狀態]" $HeaderColor
    try {
        $dbTest = Test-NetConnection -ComputerName $DatabaseHost -Port 5432 -InformationLevel Quiet -ErrorAction SilentlyContinue
        if ($dbTest) {
            Write-ColorOutput "✓ 資料庫連線正常 ($DatabaseHost:5432)" $SuccessColor
        } else {
            Write-ColorOutput "✗ 資料庫連線失敗 ($DatabaseHost:5432)" $ErrorColor
        }
    } catch {
        Write-ColorOutput "✗ 資料庫連線測試失敗: $($_.Exception.Message)" $ErrorColor
    }
    
    # 檢查後端
    Write-ColorOutput "`n[後端狀態]" $HeaderColor
    try {
        $backendTest = Test-NetConnection -ComputerName $BackendHost -Port 8000 -InformationLevel Quiet -ErrorAction SilentlyContinue
        if ($backendTest) {
            Write-ColorOutput "✓ 後端服務正在運行 (${BackendHost}:8000)" $SuccessColor
            
            # 嘗試 HTTP 請求
            try {
                $response = Invoke-WebRequest -Uri "http://${BackendHost}:8000/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    Write-ColorOutput "✓ 後端 API 回應正常" $SuccessColor
                }
            } catch {
                Write-ColorOutput "⚠ 後端端口開啟但 API 無回應" $WarningColor
            }
        } else {
            Write-ColorOutput "✗ 後端服務未運行 (${BackendHost}:8000)" $ErrorColor
        }
    } catch {
        Write-ColorOutput "✗ 後端連線測試失敗: $($_.Exception.Message)" $ErrorColor
    }
    
    # 檢查前端
    Write-ColorOutput "`n[前端狀態]" $HeaderColor
    try {
        $frontendTest80 = Test-NetConnection -ComputerName $FrontendHost -Port 80 -InformationLevel Quiet -ErrorAction SilentlyContinue
        $frontendTest3000 = Test-NetConnection -ComputerName $FrontendHost -Port 3000 -InformationLevel Quiet -ErrorAction SilentlyContinue
        
        if ($frontendTest80) {
            Write-ColorOutput "✓ 前端服務 (IIS) 正在運行 (${FrontendHost}:80)" $SuccessColor
        } elseif ($frontendTest3000) {
            Write-ColorOutput "✓ 前端服務 (Node.js) 正在運行 (${FrontendHost}:3000)" $SuccessColor
        } else {
            Write-ColorOutput "✗ 前端服務未運行" $ErrorColor
        }
    } catch {
        Write-ColorOutput "✗ 前端連線測試失敗: $($_.Exception.Message)" $ErrorColor
    }
}

function Deploy-Database {
    param([string]$ScriptPath)
    
    Write-ColorOutput "`n=================================================" $HeaderColor
    Write-ColorOutput "           開始部署資料庫" $HeaderColor
    Write-ColorOutput "=================================================" $HeaderColor
    
    $DatabaseScript = Join-Path $ScriptPath "deploy_database.ps1"
    if (-not (Test-Path $DatabaseScript)) {
        Write-ColorOutput "找不到資料庫部署腳本: $DatabaseScript" $ErrorColor
        return $false
    }
    
    try {
        & $DatabaseScript -ProjectPath $ProjectPath -DatabaseHost $DatabaseHost
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "資料庫部署成功" $SuccessColor
            return $true
        } else {
            Write-ColorOutput "資料庫部署失敗" $ErrorColor
            return $false
        }
    } catch {
        Write-ColorOutput "資料庫部署過程發生錯誤: $($_.Exception.Message)" $ErrorColor
        return $false
    }
}

function Deploy-Backend {
    param([string]$ScriptPath)
    
    Write-ColorOutput "`n=================================================" $HeaderColor
    Write-ColorOutput "           開始部署後端" $HeaderColor
    Write-ColorOutput "=================================================" $HeaderColor
    
    $BackendScript = Join-Path $ScriptPath "deploy_backend.ps1"
    if (-not (Test-Path $BackendScript)) {
        Write-ColorOutput "找不到後端部署腳本: $BackendScript" $ErrorColor
        return $false
    }
    
    try {
        $skipDB = if ($SkipDatabase) { "-SkipDB" } else { "" }
        if ($skipDB) {
            & $BackendScript -ProjectPath $ProjectPath -BackendHost $BackendHost -DatabaseHost $DatabaseHost -SkipDB
        } else {
            & $BackendScript -ProjectPath $ProjectPath -BackendHost $BackendHost -DatabaseHost $DatabaseHost
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "後端部署成功" $SuccessColor
            return $true
        } else {
            Write-ColorOutput "後端部署失敗" $ErrorColor
            return $false
        }
    } catch {
        Write-ColorOutput "後端部署過程發生錯誤: $($_.Exception.Message)" $ErrorColor
        return $false
    }
}

function Deploy-Frontend {
    param([string]$ScriptPath)
    
    Write-ColorOutput "`n=================================================" $HeaderColor
    Write-ColorOutput "           開始部署前端" $HeaderColor
    Write-ColorOutput "=================================================" $HeaderColor
    
    $FrontendScript = Join-Path $ScriptPath "deploy_frontend.ps1"
    if (-not (Test-Path $FrontendScript)) {
        Write-ColorOutput "找不到前端部署腳本: $FrontendScript" $ErrorColor
        return $false
    }
    
    try {
        & $FrontendScript -ProjectPath $ProjectPath -FrontendHost $FrontendHost -BackendHost $BackendHost
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "前端部署成功" $SuccessColor
            return $true
        } else {
            Write-ColorOutput "前端部署失敗" $ErrorColor
            return $false
        }
    } catch {
        Write-ColorOutput "前端部署過程發生錯誤: $($_.Exception.Message)" $ErrorColor
        return $false
    }
}

function Show-DeploymentSummary {
    param(
        [bool]$DatabaseResult,
        [bool]$BackendResult,
        [bool]$FrontendResult,
        [DateTime]$StartTime
    )
    
    $EndTime = Get-Date
    $Duration = $EndTime - $StartTime
    
    Write-ColorOutput "`n=================================================" $HeaderColor
    Write-ColorOutput "           部署結果摘要" $HeaderColor
    Write-ColorOutput "=================================================" $HeaderColor
    
    if (-not $SkipDatabase) {
        $dbStatus = if ($DatabaseResult) { "✓ 成功" } else { "✗ 失敗" }
        $dbColor = if ($DatabaseResult) { $SuccessColor } else { $ErrorColor }
        Write-ColorOutput "資料庫部署: $dbStatus" $dbColor
    }
    
    if (-not $SkipBackend) {
        $backendStatus = if ($BackendResult) { "✓ 成功" } else { "✗ 失敗" }
        $backendColor = if ($BackendResult) { $SuccessColor } else { $ErrorColor }
        Write-ColorOutput "後端部署: $backendStatus" $backendColor
    }
    
    if (-not $SkipFrontend) {
        $frontendStatus = if ($FrontendResult) { "✓ 成功" } else { "✗ 失敗" }
        $frontendColor = if ($FrontendResult) { $SuccessColor } else { $ErrorColor }
        Write-ColorOutput "前端部署: $frontendStatus" $frontendColor
    }
    
    Write-ColorOutput "`n部署耗時: $($Duration.Minutes) 分 $($Duration.Seconds) 秒" $InfoColor
    Write-ColorOutput "完成時間: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" $InfoColor
    
    Write-ColorOutput "`n服務網址:" $InfoColor
    if ($BackendResult) {
        Write-ColorOutput "- 後端 API: http://${BackendHost}:8000" $SuccessColor
        Write-ColorOutput "- API 文件: http://${BackendHost}:8000/docs" $SuccessColor
    }
    if ($FrontendResult) {
        Write-ColorOutput "- 前端網站: http://${FrontendHost}" $SuccessColor
    }
}

# 主程式開始
if (-not (Test-AdminRights)) {
    Stop-OnError "需要管理員權限執行此腳本。請以管理員身份重新執行。"
}

Show-Banner

# 檢查專案目錄
if (-not (Test-Path $ProjectPath)) {
    Stop-OnError "專案目錄不存在: $ProjectPath"
}

$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$StartTime = Get-Date

# 初始化結果變數
$DatabaseResult = $true
$BackendResult = $true
$FrontendResult = $true

if ($Mode -eq "Interactive") {
    do {
        Show-Menu
        $choice = Read-Host "請輸入選項 (0-6)"
        
        switch ($choice) {
            "1" {
                # 完整部署
                Write-ColorOutput "開始完整部署..." $InfoColor
                if (-not $SkipDatabase) { $DatabaseResult = Deploy-Database $ScriptPath }
                if (-not $SkipBackend) { $BackendResult = Deploy-Backend $ScriptPath }
                if (-not $SkipFrontend) { $FrontendResult = Deploy-Frontend $ScriptPath }
                Show-DeploymentSummary $DatabaseResult $BackendResult $FrontendResult $StartTime
                break
            }
            "2" {
                # 僅部署資料庫
                Write-ColorOutput "開始部署資料庫..." $InfoColor
                $DatabaseResult = Deploy-Database $ScriptPath
                $BackendResult = $true
                $FrontendResult = $true
                Show-DeploymentSummary $DatabaseResult $BackendResult $FrontendResult $StartTime
                break
            }
            "3" {
                # 僅部署後端
                Write-ColorOutput "開始部署後端..." $InfoColor
                $BackendResult = Deploy-Backend $ScriptPath
                $DatabaseResult = $true
                $FrontendResult = $true
                Show-DeploymentSummary $DatabaseResult $BackendResult $FrontendResult $StartTime
                break
            }
            "4" {
                # 僅部署前端
                Write-ColorOutput "開始部署前端..." $InfoColor
                $FrontendResult = Deploy-Frontend $ScriptPath
                $DatabaseResult = $true
                $BackendResult = $true
                Show-DeploymentSummary $DatabaseResult $BackendResult $FrontendResult $StartTime
                break
            }
            "5" {
                # 部署後端 + 前端
                Write-ColorOutput "開始部署後端和前端..." $InfoColor
                $SkipDatabase = $true
                $BackendResult = Deploy-Backend $ScriptPath
                $FrontendResult = Deploy-Frontend $ScriptPath
                $DatabaseResult = $true
                Show-DeploymentSummary $DatabaseResult $BackendResult $FrontendResult $StartTime
                break
            }
            "6" {
                # 檢查系統狀態
                Test-SystemStatus
                break
            }
            "0" {
                Write-ColorOutput "退出部署程序" $InfoColor
                exit 0
            }
            default {
                Write-ColorOutput "無效選項，請重新選擇" $WarningColor
                break
            }
        }
        
        if ($choice -ne "6" -and $choice -ne "0") {
            Write-ColorOutput "`n按任意鍵繼續..." $InfoColor
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        
    } while ($choice -ne "0")
    
} else {
    # 自動模式
    Write-ColorOutput "自動部署模式啟動..." $InfoColor
    Write-ColorOutput "專案路徑: $ProjectPath" $InfoColor
    Write-ColorOutput "資料庫主機: $DatabaseHost" $InfoColor
    Write-ColorOutput "後端主機: $BackendHost" $InfoColor
    Write-ColorOutput "前端主機: $FrontendHost" $InfoColor
    
    if (-not $SkipDatabase) {
        $DatabaseResult = Deploy-Database $ScriptPath
    }
    
    if (-not $SkipBackend) {
        $BackendResult = Deploy-Backend $ScriptPath
    }
    
    if (-not $SkipFrontend) {
        $FrontendResult = Deploy-Frontend $ScriptPath
    }
    
    Show-DeploymentSummary $DatabaseResult $BackendResult $FrontendResult $StartTime
    
    # 整合測試
    Write-ColorOutput "`n正在執行整合測試..." $InfoColor
    Start-Sleep -Seconds 10
    Test-SystemStatus
}

Write-ColorOutput "`n部署程序完成！" $SuccessColor 