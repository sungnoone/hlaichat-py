import os
from typing import Any, Dict, Optional
from pydantic import PostgresDsn, validator
from pydantic_settings import BaseSettings
from datetime import datetime
import pytz
from pathlib import Path

# 設定台北時區
taipei_tz = pytz.timezone('Asia/Taipei')

# 取得專案根目錄路徑
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    """
    應用程式設定類別，用於載入環境變數
    """
    # 應用程式設定
    APP_NAME: str = "HLAIChat"
    SECRET_KEY: str
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # 資料庫設定
    DATABASE_URL: PostgresDsn
    
    # AD 網域設定 (基本資訊，實際帳密從資料庫讀取)
    AD_DOMAIN_NAME: Optional[str] = None
    AD_PRIMARY_DC: Optional[str] = None
    AD_SECONDARY_DCS: Optional[str] = None
    
    # 時區設定
    TIMEZONE: str = "Asia/Taipei"
    
    # 聊天功能逾時設定 (秒)
    CHAT_WEBHOOK_TIMEOUT: int = 300
    CHAT_REQUEST_TIMEOUT: int = 300
    CHAT_CONNECTION_TIMEOUT: int = 300
    
    # 前端設定 (用於整合 .env 檔案)
    VITE_API_BASE_URL: Optional[str] = None
    
    # 驗證 DATABASE_URL
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: Optional[str]) -> Any:
        if isinstance(v, str):
            # 確保使用 postgresql:// 而不是 postgres://
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql://", 1)
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user="postgres",
            password="hl69382361",
            host="192.168.1.221",
            port="5432",
            path=f"/hlaichat-py",
        )
    
    # 取得目前台北時間
    @staticmethod
    def get_taipei_now() -> datetime:
        """
        取得目前台北時間
        
        Returns:
            datetime: 目前台北時間
        """
        return datetime.now(taipei_tz)
    
    class Config:
        env_file = os.path.join(BASE_DIR, ".env")
        case_sensitive = True
        extra = "ignore"  # 允許額外的環境變數


# 建立全域設定實例
settings = Settings()
