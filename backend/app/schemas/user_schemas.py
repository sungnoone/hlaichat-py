from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, validator
from datetime import datetime

# 基本使用者模型
class UserBase(BaseModel):
    """
    基本使用者模型
    """
    username: str
    full_name: str
    phone: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None
    is_ad_user: bool = False
    ad_guid: Optional[str] = None

# 建立使用者時的請求模型
class UserCreate(UserBase):
    """
    建立使用者時的請求模型
    """
    password: str
    group_ids: Optional[List[int]] = None

# 更新使用者時的請求模型
class UserUpdate(BaseModel):
    """
    更新使用者時的請求模型
    """
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    group_ids: Optional[List[int]] = None

# 更新使用者密碼的請求模型
class UserUpdatePassword(BaseModel):
    """
    更新使用者密碼的請求模型
    """
    password: str

# 資料庫中的使用者模型
class UserInDB(UserBase):
    """
    資料庫中的使用者模型
    """
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# API 回應中的使用者模型
class User(UserInDB):
    """
    API 回應中的使用者模型
    """
    groups: List["GroupInUser"] = []

# API 回應中的簡化使用者模型 (用於群組中顯示使用者)
class UserInGroup(BaseModel):
    """
    API 回應中的簡化使用者模型 (用於群組中顯示使用者)
    """
    id: int
    username: str
    full_name: str
    is_active: bool
    is_ad_user: bool
    
    class Config:
        from_attributes = True

# API 回應中的簡化群組模型 (用於使用者中顯示群組)
class GroupInUser(BaseModel):
    """
    API 回應中的簡化群組模型 (用於使用者中顯示群組)
    """
    id: int
    name: str
    can_login: bool
    can_manage_platform: bool
    can_use_chat_links: bool
    
    class Config:
        from_attributes = True

# 登入請求模型
class UserLogin(BaseModel):
    """
    登入請求模型
    """
    username: str
    password: str

# AD登入請求模型
class ADUserLogin(BaseModel):
    """
    AD登入請求模型
    """
    username: str
    password: str

# 登入回應模型
class Token(BaseModel):
    """
    登入回應模型
    """
    access_token: str
    token_type: str = "bearer"
    user: User

# 更新模型的循環引用
from app.schemas.group_schemas import GroupInUser
User.update_forward_refs()
