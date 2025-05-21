from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# 基本操作紀錄模型
class LogBase(BaseModel):
    """
    基本操作紀錄模型
    """
    action: str
    details: Optional[str] = None
    ip_address: Optional[str] = None

# 建立操作紀錄時的請求模型
class LogCreate(LogBase):
    """
    建立操作紀錄時的請求模型
    """
    user_id: int

# 資料庫中的操作紀錄模型
class LogInDB(LogBase):
    """
    資料庫中的操作紀錄模型
    """
    id: int
    user_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# API 回應中的操作紀錄模型
class Log(LogInDB):
    """
    API 回應中的操作紀錄模型
    """
    user_username: str
    user_full_name: str

# 操作紀錄搜尋請求模型
class LogSearch(BaseModel):
    """
    操作紀錄搜尋請求模型
    """
    user_id: Optional[int] = None
    action: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    page_size: int = 10
