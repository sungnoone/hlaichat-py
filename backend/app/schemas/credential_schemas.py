from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CredentialBase(BaseModel):
    """
    憑證基礎模型
    """
    name: str = Field(..., description="憑證名稱")
    api_key: str = Field(..., description="API Key")
    description: Optional[str] = Field(None, description="描述")

class CredentialCreate(CredentialBase):
    """
    建立憑證模型
    """
    pass

class CredentialUpdate(BaseModel):
    """
    更新憑證模型
    """
    name: Optional[str] = Field(None, description="憑證名稱")
    api_key: Optional[str] = Field(None, description="API Key")
    description: Optional[str] = Field(None, description="描述")

class CredentialResponse(CredentialBase):
    """
    憑證回應模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CredentialListResponse(BaseModel):
    """
    憑證列表回應模型
    """
    credentials: List[CredentialResponse]
    total: int

class CredentialSimple(BaseModel):
    """
    簡化憑證模型 - 用於下拉選單
    """
    id: int
    name: str
    
    class Config:
        from_attributes = True 