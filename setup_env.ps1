# HLAIChat Environment Setup Script
# This script generates the unified .env file for the project
# 此腳本生成專案所需的統一環境變數檔案
# 整合了後端和前端所需的所有環境變數到單一檔案中

# Define environment variable content
$envContent = @"
# HLAIChat Project Environment Settings
# Application Settings
APP_NAME=HLAIChat
SECRET_KEY=hl69382361
DEBUG=True
HOST=0.0.0.0
PORT=8000
RELOAD=True
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database Settings
DATABASE_URL=postgresql://postgres:hl69382361@192.168.1.221:5432/hlaichat-py

# AD Domain Settings
AD_DOMAIN_NAME=hanlin.com.tw
AD_PRIMARY_DC=192.168.1.6
AD_SECONDARY_DCS=192.168.1.5,192.168.5.5
AD_BIND_USERNAME=
AD_BIND_PASSWORD=

# Frontend Settings
VITE_API_BASE_URL=http://localhost:8000

# Timezone Settings (Taipei Time)
TIMEZONE=Asia/Taipei
"@

# Write to .env file with ASCII encoding
$envContent | Out-File -FilePath ".env" -Encoding ascii -Force

Write-Host "Unified environment .env file generated successfully!"
Write-Host "Environment setup completed!" 