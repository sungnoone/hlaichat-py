# HLAIChat 服務管理腳本
# 作用：統一管理 HLAIChat 相關的 Windows 服務和應用程式
# 使用方式：在任一主機上執行，可選擇管理本機或遠端服務
# 執行環境：Windows Server 2019/2022 或 Windows 10/11
# 編碼：UTF-8

param(
    [ValidateSet("start", "stop", "restart", "status", "install", "uninstall")]
    [string]$Action = "status",
    
    [ValidateSet("all", "database", "backend", "frontend")]
    [string]$Service = "all",
    
    [string]$DatabaseHost = "192.168.1.221",
    [string]$BackendHost = "192.168.5.107", 
    [string]$FrontendHost = "192.168.5.54",
    
    [switch]$Interactive = $true
)

# 設定控制台編碼為 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "HLAIChat 服務管理腳本" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# 檢查是否以管理員權限執行
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "此腳本需要以管理員權限執行！"
    Write-Host "請以管理員身分開啟 PowerShell 後重新執行。" -ForegroundColor Yellow
    pause
    exit 1
}

# 互動式選單
if ($Interactive -and $MyInvocation.BoundParameters.Count -eq 0) {
    Write-Host "請選擇要執行的操作：" -ForegroundColor Yellow
    Write-Host "1. 查看服務狀態" -ForegroundColor Green
    Write-Host "2. 啟動服務" -ForegroundColor Green
    Write-Host "3. 停止服務" -ForegroundColor Green
    Write-Host "4. 重新啟動服務" -ForegroundColor Green
    Write-Host "5. 安裝服務" -ForegroundColor Green
    Write-Host "6. 移除服務" -ForegroundColor Green
    Write-Host "0. 退出" -ForegroundColor Red
    
    $actionChoice = Read-Host "`n請輸入選項 (0-6)"
    
    switch ($actionChoice) {
        "1" { $Action = "status" }
        "2" { $Action = "start" }
        "3" { $Action = "stop" }
        "4" { $Action = "restart" }
        "5" { $Action = "install" }
        "6" { $Action = "uninstall" }
        "0" {
            Write-Host "操作取消" -ForegroundColor Yellow
            exit 0
        }
        default {
            Write-Error "無效的選項"
            exit 1
        }
    }
    
    Write-Host "`n請選擇要管理的服務：" -ForegroundColor Yellow
    Write-Host "1. 所有服務" -ForegroundColor Green
    Write-Host "2. 資料庫服務" -ForegroundColor Green
    Write-Host "3. 後端服務" -ForegroundColor Green
    Write-Host "4. 前端服務" -ForegroundColor Green
    
    $serviceChoice = Read-Host "`n請輸入選項 (1-4)"
    
    switch ($serviceChoice) {
        "1" { $Service = "all" }
        "2" { $Service = "database" }
        "3" { $Service = "backend" }
        "4" { $Service = "frontend" }
        default {
            Write-Error "無效的選項"
            exit 1
        }
    }
}

Write-Host "`n操作資訊：" -ForegroundColor White
Write-Host "- 動作：$Action" -ForegroundColor White
Write-Host "- 服務：$Service" -ForegroundColor White
Write-Host "- 資料庫主機：$DatabaseHost" -ForegroundColor White
Write-Host "- 後端主機：$BackendHost" -ForegroundColor White
Write-Host "- 前端主機：$FrontendHost" -ForegroundColor White

# 服務定義
$services = @{
    "database" = @{
        "Name" = "postgresql*"
        "DisplayName" = "PostgreSQL Database Server"
        "Host" = $DatabaseHost
        "Port" = 5432
        "Type" = "Windows Service"
    }
    "backend" = @{
        "Name" = "HLAIChatBackend"
        "DisplayName" = "HLAIChat Backend Service"
        "Host" = $BackendHost
        "Port" = 8000
        "Type" = "Custom Service"
    }
    "frontend" = @{
        "Name" = "HLAIChat Frontend"
        "DisplayName" = "HLAIChat Frontend"
        "Host" = $FrontendHost
        "Port" = 80
        "Type" = "IIS Website"
    }
}

# 取得當前主機IP
function Get-CurrentHostIPs {
    return (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.PrefixOrigin -eq "Manual" -or $_.IPAddress -match "^192\.168\."}).IPAddress
}

# 檢查是否為本機服務
function Test-IsLocalService {
    param([string]$ServiceHost)
    
    $currentIPs = Get-CurrentHostIPs
    return ($ServiceHost -eq "localhost" -or $ServiceHost -eq "127.0.0.1" -or $currentIPs -contains $ServiceHost)
}

# 管理資料庫服務
function Manage-DatabaseService {
    param([string]$Action)
    
    Write-Host "`n管理資料庫服務..." -ForegroundColor Yellow
    
    if (-not (Test-IsLocalService $DatabaseHost)) {
        Write-Warning "資料庫服務在遠端主機 $DatabaseHost，無法直接管理"
        Write-Host "請在資料庫主機上執行此腳本" -ForegroundColor Yellow
        return
    }
    
    try {
        $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue | Select-Object -First 1
        
        if (-not $pgService) {
            Write-Warning "找不到 PostgreSQL 服務"
            return
        }
        
        Write-Host "找到服務：$($pgService.Name)" -ForegroundColor Green
        
        switch ($Action) {
            "status" {
                Write-Host "服務狀態：$($pgService.Status)" -ForegroundColor $(if ($pgService.Status -eq "Running") { "Green" } else { "Red" })
                Write-Host "啟動類型：$($pgService.StartType)" -ForegroundColor White
            }
            "start" {
                if ($pgService.Status -ne "Running") {
                    Start-Service -Name $pgService.Name
                    Write-Host "資料庫服務已啟動" -ForegroundColor Green
                } else {
                    Write-Host "資料庫服務已在運行" -ForegroundColor Yellow
                }
            }
            "stop" {
                if ($pgService.Status -eq "Running") {
                    Stop-Service -Name $pgService.Name
                    Write-Host "資料庫服務已停止" -ForegroundColor Green
                } else {
                    Write-Host "資料庫服務已停止" -ForegroundColor Yellow
                }
            }
            "restart" {
                Restart-Service -Name $pgService.Name
                Write-Host "資料庫服務已重新啟動" -ForegroundColor Green
            }
        }
        
        # 測試連線
        if ($Action -ne "stop") {
            Start-Sleep -Seconds 2
            $testResult = Test-NetConnection -ComputerName $DatabaseHost -Port 5432 -InformationLevel Quiet -ErrorAction SilentlyContinue
            if ($testResult) {
                Write-Host "✓ 資料庫連線測試成功" -ForegroundColor Green
            } else {
                Write-Warning "✗ 資料庫連線測試失敗"
            }
        }
        
    } catch {
        Write-Error "資料庫服務管理失敗：$($_.Exception.Message)"
    }
}

# 管理後端服務
function Manage-BackendService {
    param([string]$Action)
    
    Write-Host "`n管理後端服務..." -ForegroundColor Yellow
    
    if (-not (Test-IsLocalService $BackendHost)) {
        Write-Warning "後端服務在遠端主機 $BackendHost，無法直接管理"
        Write-Host "請在後端主機上執行此腳本" -ForegroundColor Yellow
        return
    }
    
    try {
        $backendService = Get-Service -Name "HLAIChatBackend" -ErrorAction SilentlyContinue
        
        if (-not $backendService) {
            Write-Warning "找不到 HLAIChat 後端服務"
            Write-Host "請檢查服務是否已安裝" -ForegroundColor Yellow
            return
        }
        
        Write-Host "找到服務：$($backendService.Name)" -ForegroundColor Green
        
        switch ($Action) {
            "status" {
                Write-Host "服務狀態：$($backendService.Status)" -ForegroundColor $(if ($backendService.Status -eq "Running") { "Green" } else { "Red" })
                Write-Host "啟動類型：$($backendService.StartType)" -ForegroundColor White
            }
            "start" {
                if ($backendService.Status -ne "Running") {
                    Start-Service -Name $backendService.Name
                    Write-Host "後端服務已啟動" -ForegroundColor Green
                } else {
                    Write-Host "後端服務已在運行" -ForegroundColor Yellow
                }
            }
            "stop" {
                if ($backendService.Status -eq "Running") {
                    Stop-Service -Name $backendService.Name
                    Write-Host "後端服務已停止" -ForegroundColor Green
                } else {
                    Write-Host "後端服務已停止" -ForegroundColor Yellow
                }
            }
            "restart" {
                Restart-Service -Name $backendService.Name
                Write-Host "後端服務已重新啟動" -ForegroundColor Green
            }
        }
        
        # 測試連線
        if ($Action -ne "stop") {
            Start-Sleep -Seconds 5
            try {
                $testResponse = Invoke-WebRequest -Uri "http://$BackendHost`:8000" -TimeoutSec 10 -UseBasicParsing -ErrorAction SilentlyContinue
                if ($testResponse -and $testResponse.StatusCode -eq 200) {
                    Write-Host "✓ 後端服務連線測試成功" -ForegroundColor Green
                } else {
                    Write-Warning "✗ 後端服務連線測試失敗"
                }
            } catch {
                Write-Warning "✗ 後端服務連線測試失敗"
            }
        }
        
    } catch {
        Write-Error "後端服務管理失敗：$($_.Exception.Message)"
    }
}

# 管理前端服務
function Manage-FrontendService {
    param([string]$Action)
    
    Write-Host "`n管理前端服務..." -ForegroundColor Yellow
    
    if (-not (Test-IsLocalService $FrontendHost)) {
        Write-Warning "前端服務在遠端主機 $FrontendHost，無法直接管理"
        Write-Host "請在前端主機上執行此腳本" -ForegroundColor Yellow
        return
    }
    
    try {
        # 檢查 IIS 管理模組
        try {
            Import-Module WebAdministration -ErrorAction Stop
        } catch {
            Write-Warning "無法載入 IIS 管理模組，請確認 IIS 已安裝"
            return
        }
        
        $website = Get-Website -Name "HLAIChat Frontend" -ErrorAction SilentlyContinue
        
        if (-not $website) {
            Write-Warning "找不到 HLAIChat Frontend 網站"
            Write-Host "請檢查 IIS 網站是否已建立" -ForegroundColor Yellow
            return
        }
        
        Write-Host "找到網站：$($website.Name)" -ForegroundColor Green
        
        switch ($Action) {
            "status" {
                Write-Host "網站狀態：$($website.State)" -ForegroundColor $(if ($website.State -eq "Started") { "Green" } else { "Red" })
                Write-Host "實體路徑：$($website.PhysicalPath)" -ForegroundColor White
                Write-Host "繫結資訊：$($website.Bindings.Collection.bindingInformation)" -ForegroundColor White
            }
            "start" {
                if ($website.State -ne "Started") {
                    Start-Website -Name $website.Name
                    Write-Host "前端網站已啟動" -ForegroundColor Green
                } else {
                    Write-Host "前端網站已在運行" -ForegroundColor Yellow
                }
            }
            "stop" {
                if ($website.State -eq "Started") {
                    Stop-Website -Name $website.Name
                    Write-Host "前端網站已停止" -ForegroundColor Green
                } else {
                    Write-Host "前端網站已停止" -ForegroundColor Yellow
                }
            }
            "restart" {
                Stop-Website -Name $website.Name -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
                Start-Website -Name $website.Name
                Write-Host "前端網站已重新啟動" -ForegroundColor Green
            }
        }
        
        # 測試連線
        if ($Action -ne "stop") {
            Start-Sleep -Seconds 3
            try {
                $testResponse = Invoke-WebRequest -Uri "http://$FrontendHost" -TimeoutSec 10 -UseBasicParsing -ErrorAction SilentlyContinue
                if ($testResponse -and $testResponse.StatusCode -eq 200) {
                    Write-Host "✓ 前端網站連線測試成功" -ForegroundColor Green
                } else {
                    Write-Warning "✗ 前端網站連線測試失敗"
                }
            } catch {
                Write-Warning "✗ 前端網站連線測試失敗"
            }
        }
        
    } catch {
        Write-Error "前端服務管理失敗：$($_.Exception.Message)"
    }
}

# 安裝服務
function Install-Services {
    Write-Host "`n安裝服務..." -ForegroundColor Yellow
    Write-Host "此功能需要執行對應的部署腳本" -ForegroundColor Yellow
    
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    
    switch ($Service) {
        "all" {
            Write-Host "執行完整部署..." -ForegroundColor Green
            $fullScript = Join-Path $scriptDir "deploy_full.ps1"
            if (Test-Path $fullScript) {
                & $fullScript
            } else {
                Write-Error "找不到完整部署腳本：$fullScript"
            }
        }
        "database" {
            Write-Host "執行資料庫部署..." -ForegroundColor Green
            $dbScript = Join-Path $scriptDir "deploy_database.ps1"
            if (Test-Path $dbScript) {
                & $dbScript
            } else {
                Write-Error "找不到資料庫部署腳本：$dbScript"
            }
        }
        "backend" {
            Write-Host "執行後端部署..." -ForegroundColor Green
            $backendScript = Join-Path $scriptDir "deploy_backend.ps1"
            if (Test-Path $backendScript) {
                & $backendScript
            } else {
                Write-Error "找不到後端部署腳本：$backendScript"
            }
        }
        "frontend" {
            Write-Host "執行前端部署..." -ForegroundColor Green
            $frontendScript = Join-Path $scriptDir "deploy_frontend.ps1"
            if (Test-Path $frontendScript) {
                & $frontendScript
            } else {
                Write-Error "找不到前端部署腳本：$frontendScript"
            }
        }
    }
}

# 移除服務
function Uninstall-Services {
    Write-Host "`n移除服務..." -ForegroundColor Yellow
    
    $confirm = Read-Host "確定要移除服務嗎？這將刪除所有相關設定 (y/N)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "操作取消" -ForegroundColor Yellow
        return
    }
    
    if ($Service -eq "all" -or $Service -eq "backend") {
        try {
            $backendService = Get-Service -Name "HLAIChatBackend" -ErrorAction SilentlyContinue
            if ($backendService) {
                Stop-Service -Name "HLAIChatBackend" -ErrorAction SilentlyContinue
                
                # 使用 NSSM 移除服務
                $nssmPath = (Get-Command nssm.exe -ErrorAction SilentlyContinue).Source
                if ($nssmPath) {
                    & nssm remove HLAIChatBackend confirm
                    Write-Host "後端服務已移除" -ForegroundColor Green
                } else {
                    Write-Warning "找不到 NSSM，請手動移除服務"
                }
            }
        } catch {
            Write-Warning "移除後端服務失敗：$($_.Exception.Message)"
        }
    }
    
    if ($Service -eq "all" -or $Service -eq "frontend") {
        try {
            Import-Module WebAdministration -ErrorAction SilentlyContinue
            $website = Get-Website -Name "HLAIChat Frontend" -ErrorAction SilentlyContinue
            if ($website) {
                Remove-Website -Name "HLAIChat Frontend"
                Write-Host "前端網站已移除" -ForegroundColor Green
            }
            
            $appPool = Get-IISAppPool -Name "HLAIChatFrontend" -ErrorAction SilentlyContinue
            if ($appPool) {
                Remove-WebAppPool -Name "HLAIChatFrontend"
                Write-Host "應用程式集區已移除" -ForegroundColor Green
            }
        } catch {
            Write-Warning "移除前端服務失敗：$($_.Exception.Message)"
        }
    }
}

# 主要執行邏輯
Write-Host "`n執行操作：$Action" -ForegroundColor Cyan

switch ($Action) {
    "install" {
        Install-Services
    }
    "uninstall" {
        Uninstall-Services
    }
    default {
        if ($Service -eq "all") {
            Manage-DatabaseService $Action
            Manage-BackendService $Action
            Manage-FrontendService $Action
        } else {
            switch ($Service) {
                "database" { Manage-DatabaseService $Action }
                "backend" { Manage-BackendService $Action }
                "frontend" { Manage-FrontendService $Action }
            }
        }
    }
}

# 顯示整體狀態摘要
if ($Action -eq "status") {
    Write-Host "`n=======================================" -ForegroundColor Cyan
    Write-Host "服務狀態摘要" -ForegroundColor Cyan
    Write-Host "=======================================" -ForegroundColor Cyan
    
    # 檢查資料庫連線
    try {
        $dbTest = Test-NetConnection -ComputerName $DatabaseHost -Port 5432 -InformationLevel Quiet -ErrorAction SilentlyContinue
        Write-Host "資料庫連線：$(if ($dbTest) { '正常' } else { '失敗' })" -ForegroundColor $(if ($dbTest) { "Green" } else { "Red" })
    } catch {
        Write-Host "資料庫連線：無法測試" -ForegroundColor Yellow
    }
    
    # 檢查後端服務
    try {
        $backendResponse = Invoke-WebRequest -Uri "http://$BackendHost`:8000" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
        Write-Host "後端服務：$(if ($backendResponse -and $backendResponse.StatusCode -eq 200) { '正常' } else { '異常' })" -ForegroundColor $(if ($backendResponse -and $backendResponse.StatusCode -eq 200) { "Green" } else { "Red" })
    } catch {
        Write-Host "後端服務：無法連線" -ForegroundColor Red
    }
    
    # 檢查前端服務
    try {
        $frontendResponse = Invoke-WebRequest -Uri "http://$FrontendHost" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
        Write-Host "前端服務：$(if ($frontendResponse -and $frontendResponse.StatusCode -eq 200) { '正常' } else { '異常' })" -ForegroundColor $(if ($frontendResponse -and $frontendResponse.StatusCode -eq 200) { "Green" } else { "Red" })
    } catch {
        Write-Host "前端服務：無法連線" -ForegroundColor Red
    }
    
    Write-Host "`n存取網址：" -ForegroundColor Yellow
    Write-Host "前端網站：http://$FrontendHost" -ForegroundColor Green
    Write-Host "後端 API：http://$BackendHost`:8000" -ForegroundColor Green
    Write-Host "API 文件：http://$BackendHost`:8000/docs" -ForegroundColor Green
}

Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "服務管理完成" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan

Write-Host "`n常用指令：" -ForegroundColor Yellow
Write-Host "查看所有服務狀態：.\manage_services.ps1 -Action status -Service all" -ForegroundColor Yellow
Write-Host "啟動所有服務：.\manage_services.ps1 -Action start -Service all" -ForegroundColor Yellow
Write-Host "重啟所有服務：.\manage_services.ps1 -Action restart -Service all" -ForegroundColor Yellow
Write-Host "停止所有服務：.\manage_services.ps1 -Action stop -Service all" -ForegroundColor Yellow

pause 