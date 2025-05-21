from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# 基本群組模型
class GroupBase(BaseModel):
    """
    基本群組模型
    """
    name: str
    description: Optional[str] = None
    can_login: bool = True
    can_manage_platform: bool = False
    can_use_chat_links: bool = True

# 建立群組時的請求模型
class GroupCreate(GroupBase):
    """
    建立群組時的請求模型
    """
    user_ids: Optional[List[int]] = None
    chat_link_ids: Optional[List[int]] = None

# 更新群組時的請求模型
class GroupUpdate(BaseModel):
    """
    更新群組時的請求模型
    """
    name: Optional[str] = None
    description: Optional[str] = None
    can_login: Optional[bool] = None
    can_manage_platform: Optional[bool] = None
    can_use_chat_links: Optional[bool] = None
    user_ids: Optional[List[int]] = None
    chat_link_ids: Optional[List[int]] = None

# 資料庫中的群組模型
class GroupInDB(GroupBase):
    """
    資料庫中的群組模型
    """
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# API 回應中的群組模型
class Group(GroupInDB):
    """
    API 回應中的群組模型
    """
    users: List["UserInGroup"] = []
    chat_links: List["ChatLinkInGroup"] = []

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

# API 回應中的簡化群組模型 (用於聊天連結中顯示群組)
class GroupInChatLink(BaseModel):
    """
    API 回應中的簡化群組模型 (用於聊天連結中顯示群組)
    """
    id: int
    name: str
    
    class Config:
        from_attributes = True

# 更新模型的循環引用
from app.schemas.user_schemas import UserInGroup
from app.schemas.chat_link_schemas import ChatLinkInGroup
Group.update_forward_refs()
