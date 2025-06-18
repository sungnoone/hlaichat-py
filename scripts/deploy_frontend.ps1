# 前端部署腳本 - Frontend Deployment Script
# 版本: 2.1
# 編碼: UTF-8
# 說明: 用於部署 Vue.js 前端應用程式到 IIS 或 Node.js 伺服器

param(
    [string]$ProjectPath = "E:\projects\hlaichat-py",
    [string]$FrontendHost = "192.168.5.54",
    [string]$BackendHost = "192.168.5.107",
    [string]$WebServer = "NodeJS",  # IIS 或 NodeJS
    [switch]$SkipBuild,
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
Write-ColorOutput "          HLAIChat 前端部署腳本" $InfoColor
Write-ColorOutput "===============================================" $InfoColor
Write-ColorOutput "專案路徑: $ProjectPath" $InfoColor
Write-ColorOutput "前端主機: $FrontendHost" $InfoColor
Write-ColorOutput "後端主機: $BackendHost" $InfoColor
Write-ColorOutput "網頁伺服器: $WebServer" $InfoColor
Write-ColorOutput "===============================================" $InfoColor

# 設定路徑
$FrontendPath = Join-Path $ProjectPath "frontend"
$DistPath = Join-Path $FrontendPath "dist"

# 檢查專案目錄
if (-not (Test-Path $ProjectPath)) {
    Stop-OnError "專案目錄不存在: $ProjectPath"
}

if (-not (Test-Path $FrontendPath)) {
    Stop-OnError "前端目錄不存在: $FrontendPath"
}

# 切換到前端目錄
Set-Location $FrontendPath

Write-ColorOutput "`n[步驟 1] 檢查 Node.js 環境..." $InfoColor

# 檢查 Node.js
try {
    $nodeVersion = node --version
    Write-ColorOutput "Node.js 版本: $nodeVersion" $SuccessColor
} catch {
    Stop-OnError "Node.js 未安裝或不在 PATH 中"
}

# 檢查 npm
try {
    $npmVersion = npm --version
    Write-ColorOutput "npm 版本: $npmVersion" $SuccessColor
} catch {
    Stop-OnError "npm 未安裝或不在 PATH 中"
}

Write-ColorOutput "`n[步驟 2] 安裝依賴套件..." $InfoColor

# 清理 node_modules (如果需要)
if ($ForceClean -and (Test-Path "node_modules")) {
    Write-ColorOutput "清理舊的 node_modules..." $WarningColor
    Remove-Item "node_modules" -Recurse -Force
}

# 安裝依賴
Write-ColorOutput "安裝 npm 套件..." $InfoColor
npm install
if ($LASTEXITCODE -ne 0) {
    Stop-OnError "npm install 失敗"
}
Write-ColorOutput "npm 套件安裝完成" $SuccessColor

# 建置前端 (除非跳過)
if (-not $SkipBuild) {
    Write-ColorOutput "`n[步驟 3] 建置前端應用程式..." $InfoColor
    
    # 清理舊的建置檔案
    if (Test-Path $DistPath) {
        Write-ColorOutput "清理舊的建置檔案..." $WarningColor
        Remove-Item $DistPath -Recurse -Force
    }
    
    # 設定環境變數
    $env:VITE_API_BASE_URL = "http://${BackendHost}:8000"
    
    # 執行建置
    Write-ColorOutput "執行 npm run build..." $InfoColor
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Stop-OnError "npm run build 失敗"
    }
    
    # 檢查建置結果
    if (-not (Test-Path $DistPath)) {
        Stop-OnError "建置失敗，dist 目錄不存在"
    }
    
    Write-ColorOutput "前端建置完成" $SuccessColor
} else {
    Write-ColorOutput "`n[步驟 3] 跳過建置步驟" $WarningColor
}

Write-ColorOutput "`n[步驟 4] 部署到網頁伺服器..." $InfoColor

if ($WebServer -eq "IIS") {
    # IIS 部署
    Write-ColorOutput "部署到 IIS..." $InfoColor
    
    # 檢查 IIS 模組
    $iisFeature = Get-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole
    if ($iisFeature.State -ne "Enabled") {
        Stop-OnError "IIS 未安裝。請先安裝 IIS 功能。"
    }
    
    # 匯入 WebAdministration 模組
    Import-Module WebAdministration -ErrorAction SilentlyContinue
    
    # 設定站台和應用程式集區名稱
    $siteName = "hlaichat"
    $appPoolName = "hlaichat"
    
    # 設定 IIS 站台路徑 - 直接指向 dist 資料夾
    $IISSitePath = $DistPath
    
    # 檢查 dist 資料夾是否存在
    if (-not (Test-Path $IISSitePath)) {
        Stop-OnError "建置目錄不存在: $IISSitePath，請先執行建置"
    }
    
    Write-ColorOutput "IIS 站台路徑: $IISSitePath" $InfoColor
    
    # 停止並刪除所有佔用 80 埠的站台
    try {
        $allSites = Get-IISSite
        foreach ($site in $allSites) {
            $hasPort80 = $false
            foreach ($binding in $site.Bindings.Collection) {
                if ($binding.bindingInformation -like "*:80:*") {
                    $hasPort80 = $true
                    break
                }
            }
            
            if ($hasPort80 -and $site.Name -ne $siteName) {
                Write-ColorOutput "停用站台 '$($site.Name)' 以釋放 80 埠..." $WarningColor
                try {
                    Stop-IISSite -Name $site.Name -Confirm:$false -ErrorAction SilentlyContinue
                    Remove-IISSite -Name $site.Name -Confirm:$false -ErrorAction SilentlyContinue
                    Write-ColorOutput "站台 '$($site.Name)' 已刪除" $SuccessColor
                } catch {
                    Write-ColorOutput "無法刪除站台 '$($site.Name)': $($_.Exception.Message)" $WarningColor
                }
            }
        }
    } catch {
        Write-ColorOutput "處理現有站台時發生錯誤: $($_.Exception.Message)" $WarningColor
    }
    
    # 建立應用程式集區
    try {
        $existingAppPool = Get-IISAppPool -Name $appPoolName -ErrorAction SilentlyContinue
        if ($existingAppPool) {
            Write-ColorOutput "停止現有應用程式集區: $appPoolName" $InfoColor
            Stop-WebAppPool -Name $appPoolName -ErrorAction SilentlyContinue
        } else {
            Write-ColorOutput "建立應用程式集區: $appPoolName" $InfoColor
            New-WebAppPool -Name $appPoolName
        }
        
        # 設定應用程式集區屬性
        Set-ItemProperty -Path "IIS:\AppPools\$appPoolName" -Name "processModel.identityType" -Value "ApplicationPoolIdentity"
        Set-ItemProperty -Path "IIS:\AppPools\$appPoolName" -Name "managedRuntimeVersion" -Value ""
        
        # 啟動應用程式集區
        Start-WebAppPool -Name $appPoolName
        Write-ColorOutput "應用程式集區配置完成" $SuccessColor
    } catch {
        Stop-OnError "建立應用程式集區失敗: $($_.Exception.Message)"
    }
    
    # 建立或更新 IIS 站台
    try {
        $existingSite = Get-IISSite -Name $siteName -ErrorAction SilentlyContinue
        if ($existingSite) {
            Write-ColorOutput "刪除現有站台: $siteName" $InfoColor
            Remove-IISSite -Name $siteName -Confirm:$false
        }
        
        Write-ColorOutput "建立新的 IIS 站台: $siteName" $InfoColor
        # 使用 -Force 參數強制建立站台，即使 80 埠有衝突
        New-IISSite -Name $siteName -BindingInformation "*:80:" -PhysicalPath $IISSitePath -Force
        
        # 確保站台存在後再設定應用程式集區
        Start-Sleep -Seconds 2
        $createdSite = Get-IISSite -Name $siteName -ErrorAction SilentlyContinue
        if ($createdSite) {
            Set-ItemProperty -Path "IIS:\Sites\$siteName" -Name "applicationPool" -Value $appPoolName
            Write-ColorOutput "IIS 站台建立完成" $SuccessColor
        } else {
            throw "站台建立後無法找到"
        }
    } catch {
        Stop-OnError "建立 IIS 站台失敗: $($_.Exception.Message)"
    }
    
    # 檢查 web.config 是否存在
    $webConfigPath = Join-Path $IISSitePath "web.config"
    if (-not (Test-Path $webConfigPath)) {
        Write-ColorOutput "web.config 不存在，將從 public 資料夾複製..." $WarningColor
        $sourceWebConfig = Join-Path $FrontendPath "public\web.config"
        if (Test-Path $sourceWebConfig) {
            Copy-Item $sourceWebConfig -Destination $webConfigPath
            Write-ColorOutput "web.config 複製完成" $SuccessColor
        } else {
            Write-ColorOutput "警告: 找不到 web.config 檔案" $WarningColor
        }
    }
    
    Write-ColorOutput "IIS 部署完成" $SuccessColor
    Write-ColorOutput "網站網址: http://$FrontendHost/" $SuccessColor
    
} elseif ($WebServer -eq "NodeJS") {
    # Node.js 伺服器部署
    Write-ColorOutput "設定 Node.js 伺服器..." $InfoColor
    
    # 建立伺服器檔案
    $serverPath = Join-Path $FrontendPath "server.js"
    $serverContent = @"
const express = require('express');
const path = require('path');
const app = express();
const port = process.env.PORT || 3000;

// 設定靜態檔案目錄
app.use(express.static(path.join(__dirname, 'dist')));

// 處理 SPA 路由
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(port, '0.0.0.0', () => {
  console.log('前端伺服器運行於 http://0.0.0.0:' + port);
});
"@
    
    [System.IO.File]::WriteAllText($serverPath, $serverContent, [System.Text.Encoding]::UTF8)
    Write-ColorOutput "伺服器檔案建立完成: $serverPath" $SuccessColor
    
    # 安裝 express
    npm install express --save
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "express 安裝失敗，嘗試繼續..." $WarningColor
    }
    
    # 檢查是否需要安裝 PM2
    try {
        pm2 --version | Out-Null
        Write-ColorOutput "PM2 已安裝" $SuccessColor
    } catch {
        Write-ColorOutput "安裝 PM2..." $InfoColor
        npm install -g pm2
        if ($LASTEXITCODE -ne 0) {
            Write-ColorOutput "PM2 安裝失敗，將使用手動啟動" $WarningColor
        }
    }
    
    # 停止現有的 PM2 應用程式
    try {
        pm2 stop hlaichat-frontend 2>$null
        pm2 delete hlaichat-frontend 2>$null
    } catch {
        # 忽略錯誤
    }
    
    # 啟動新的應用程式
    try {
        pm2 start $serverPath --name "hlaichat-frontend" --port 3000
        Write-ColorOutput "PM2 服務啟動成功" $SuccessColor
        pm2 save
        pm2 startup
    } catch {
        Write-ColorOutput "PM2 啟動失敗，建立手動啟動腳本..." $WarningColor
        
        # 建立手動啟動腳本
        $startScript = Join-Path $FrontendPath "start_frontend.ps1"
        $startContent = @"
# 前端手動啟動腳本
Set-Location '$FrontendPath'
Write-Host '啟動前端伺服器...' -ForegroundColor Green
node server.js
"@
        [System.IO.File]::WriteAllText($startScript, $startContent, [System.Text.Encoding]::UTF8)
        Write-ColorOutput "手動啟動腳本: $startScript" $InfoColor
    }
    
    Write-ColorOutput "Node.js 伺服器部署完成" $SuccessColor
    Write-ColorOutput "網站網址: http://$FrontendHost:3000/" $SuccessColor
}

Write-ColorOutput "`n[步驟 5] 部署後驗證..." $InfoColor

# 測試網站可用性
if ($WebServer -eq "IIS") {
    $testUrl = "http://$FrontendHost/"
} else {
    $testUrl = "http://$FrontendHost:3000/"
}

Write-ColorOutput "測試網站連線: $testUrl" $InfoColor
try {
    $response = Invoke-WebRequest -Uri $testUrl -TimeoutSec 10 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-ColorOutput "網站連線測試成功" $SuccessColor
    } else {
        Write-ColorOutput "網站回應狀態碼: $($response.StatusCode)" $WarningColor
    }
} catch {
    Write-ColorOutput "網站連線測試失敗: $($_.Exception.Message)" $WarningColor
}

Write-ColorOutput "`n===============================================" $InfoColor
Write-ColorOutput "          前端部署完成" $SuccessColor
Write-ColorOutput "===============================================" $InfoColor
Write-ColorOutput "網站網址: $testUrl" $SuccessColor
Write-ColorOutput "部署時間: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" $InfoColor

if ($WebServer -eq "NodeJS") {
    Write-ColorOutput "`n管理指令:" $InfoColor
    Write-ColorOutput "  檢視狀態: pm2 status" $InfoColor
    Write-ColorOutput "  檢視日誌: pm2 logs hlaichat-frontend" $InfoColor
    Write-ColorOutput "  重新啟動: pm2 restart hlaichat-frontend" $InfoColor
    Write-ColorOutput "  停止服務: pm2 stop hlaichat-frontend" $InfoColor
}

Write-ColorOutput "===============================================" $InfoColor 