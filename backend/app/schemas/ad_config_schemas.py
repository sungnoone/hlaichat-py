from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# 基本 AD 設定模型
class ADConfigBase(BaseModel):
    """
    基本 AD 設定模型
    """
    domain_name: Optional[str] = None
    primary_dc: Optional[str] = None
    secondary_dcs: Optional[str] = None
    bind_username: Optional[str] = None
    bind_password: Optional[str] = None

# 更新 AD 設定時的請求模型
class ADConfigUpdate(ADConfigBase):
    """
    更新 AD 設定時的請求模型
    """
    pass

# 資料庫中的 AD 設定模型
class ADConfigInDB(ADConfigBase):
    """
    資料庫中的 AD 設定模型
    """
    id: int
    last_updated: datetime
    
    class Config:
        from_attributes = True

# API 回應中的 AD 設定模型
class ADConfig(ADConfigInDB):
    """
    API 回應中的 AD 設定模型
    """
    pass

# AD 連線測試請求模型
class ADConnectionTest(BaseModel):
    """
    AD 連線測試請求模型
    """
    domain_name: str
    primary_dc: str
    secondary_dcs: Optional[str] = None
    bind_username: str
    bind_password: str

# AD 使用者搜尋請求模型
class ADUserSearch(BaseModel):
    """
    AD 使用者搜尋請求模型
    """
    search_term: str
    max_results: int = 50

# AD 使用者模型
class ADUser(BaseModel):
    """
    AD 使用者模型
    """
    username: str  # sAMAccountName
    full_name: str  # cn (Common Name)
    display_name: Optional[str] = None  # displayName
    email: Optional[str] = None  # mail
    department: Optional[str] = None  # department
    description: Optional[str] = None  # description
    title: Optional[str] = None  # title (職稱)
    guid: str  # objectGUID
