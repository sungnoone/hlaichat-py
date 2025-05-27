from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# 聊天會話相關模型
class ChatSessionCreate(BaseModel):
    """建立聊天會話的請求模型"""
    chat_link_id: int = Field(..., description="聊天連結ID")
    title: Optional[str] = Field(None, description="會話標題")

class ChatSessionUpdate(BaseModel):
    """更新聊天會話的請求模型"""
    title: Optional[str] = Field(None, description="會話標題")
    is_active: Optional[bool] = Field(None, description="會話是否活躍")

class ChatSessionResponse(BaseModel):
    """聊天會話回應模型"""
    id: int
    session_id: str
    user_id: int
    chat_link_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# 聊天訊息相關模型
class ChatMessageCreate(BaseModel):
    """建立聊天訊息的請求模型"""
    session_id: str = Field(..., description="會話ID")
    content: str = Field(..., description="訊息內容")

class ChatMessageResponse(BaseModel):
    """聊天訊息回應模型"""
    id: int
    session_id: str
    sequence: int
    message_type: str
    content: str
    timestamp: datetime
    processing_time: Optional[int]
    
    class Config:
        from_attributes = True

# Webhook 請求模型
class WebhookRequest(BaseModel):
    """發送到 n8n webhook 的請求模型"""
    user_id: int = Field(..., description="當前登入使用者ID")
    session_id: str = Field(..., description="對話 session 唯一識別碼")
    api_key: str = Field(..., description="選定的 API Key")
    message: str = Field(..., description="使用者輸入的訊息內容")
    sequence: int = Field(..., description="訊息序號")
    timestamp: str = Field(..., description="台北時間戳記")
    user_name: str = Field(..., description="使用者姓名")

# 聊天會話列表回應模型
class ChatSessionListResponse(BaseModel):
    """聊天會話列表回應模型"""
    sessions: List[ChatSessionResponse]
    total: int

# 聊天訊息列表回應模型
class ChatMessageListResponse(BaseModel):
    """聊天訊息列表回應模型"""
    messages: List[ChatMessageResponse]
    total: int

# 聊天會話詳細資訊回應模型
class ChatSessionDetailResponse(ChatSessionResponse):
    """聊天會話詳細資訊回應模型，包含訊息列表"""
    messages: List[ChatMessageResponse] = []
    chat_link_name: Optional[str] = None 