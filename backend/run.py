import uvicorn
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 取得專案根目錄路徑
BASE_DIR = Path(__file__).resolve().parent.parent

# 載入環境變數，從專案根目錄的 .env 檔案
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

if __name__ == "__main__":
    # 取得環境變數或使用預設值
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "True").lower() == "true"
    
    # 啟動 FastAPI 應用程式
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
    )
