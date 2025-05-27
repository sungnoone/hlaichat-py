from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# 基本聊天連結模型
class ChatLinkBase(BaseModel):
    """
    基本聊天連結模型
    """
    name: str
    url: Optional[str] = None
    embed_code: Optional[str] = None
    webhook_url: Optional[str] = None
    link_type: str  # 'n8n_host_chat', 'n8n_embedded_chat', 'n8n_webhook', 'flowise_chat' (未來擴展)
    description: Optional[str] = None
    credential_id: Optional[int] = None

# 建立聊天連結時的請求模型
class ChatLinkCreate(ChatLinkBase):
    """
    建立聊天連結時的請求模型
    """
    group_ids: Optional[List[int]] = None

# 更新聊天連結時的請求模型
class ChatLinkUpdate(BaseModel):
    """
    更新聊天連結時的請求模型
    """
    name: Optional[str] = None
    url: Optional[str] = None
    embed_code: Optional[str] = None
    webhook_url: Optional[str] = None
    link_type: Optional[str] = None
    description: Optional[str] = None
    credential_id: Optional[int] = None
    group_ids: Optional[List[int]] = None

# 資料庫中的聊天連結模型
class ChatLinkInDB(ChatLinkBase):
    """
    資料庫中的聊天連結模型
    """
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# API 回應中的聊天連結模型
class ChatLink(ChatLinkInDB):
    """
    API 回應中的聊天連結模型
    """
    groups: List["GroupInChatLink"] = []

# API 回應中的簡化聊天連結模型 (用於群組中顯示聊天連結)
class ChatLinkInGroup(BaseModel):
    """
    API 回應中的簡化聊天連結模型 (用於群組中顯示聊天連結)
    """
    id: int
    name: str
    link_type: str
    
    class Config:
        from_attributes = True

# 更新模型的循環引用
from app.schemas.group_schemas import GroupInChatLink
ChatLink.update_forward_refs()
