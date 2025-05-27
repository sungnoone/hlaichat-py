from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from fastapi import HTTPException

from app.db.models import Credential
from app.schemas.credential_schemas import CredentialCreate, CredentialUpdate

class CredentialService:
    """
    憑證服務類別
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_credential(self, credential_data: CredentialCreate) -> Credential:
        """
        建立新憑證
        """
        # 檢查名稱是否重複
        existing = self.db.query(Credential).filter(Credential.name == credential_data.name).first()
        if existing:
            raise ValueError("憑證名稱已存在")
        
        credential = Credential(**credential_data.dict())
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        return credential
    
    def get_credential(self, credential_id: int) -> Optional[Credential]:
        """
        根據 ID 取得憑證
        """
        return self.db.query(Credential).filter(Credential.id == credential_id).first()
    
    def get_credential_by_name(self, name: str) -> Optional[Credential]:
        """
        根據名稱取得憑證
        """
        return self.db.query(Credential).filter(Credential.name == name).first()
    
    def get_credentials(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> tuple[List[Credential], int]:
        """
        取得憑證列表
        """
        query = self.db.query(Credential)
        
        # 搜尋條件
        if search:
            query = query.filter(
                Credential.name.ilike(f"%{search}%") |
                Credential.description.ilike(f"%{search}%")
            )
        
        # 計算總數
        total = query.count()
        
        # 分頁
        credentials = query.order_by(Credential.created_at.desc()).offset(skip).limit(limit).all()
        
        return credentials, total
    
    def get_credentials_simple(self) -> List[Credential]:
        """
        取得簡化憑證列表 - 用於下拉選單
        """
        return self.db.query(Credential).order_by(Credential.name).all()
    
    def update_credential(self, credential_id: int, credential_data: CredentialUpdate) -> Optional[Credential]:
        """
        更新憑證
        """
        credential = self.db.query(Credential).filter(Credential.id == credential_id).first()
        if not credential:
            return None
        
        # 檢查名稱是否重複（排除自己）
        if credential_data.name and credential_data.name != credential.name:
            existing = self.db.query(Credential).filter(
                and_(Credential.name == credential_data.name, Credential.id != credential_id)
            ).first()
            if existing:
                raise ValueError("憑證名稱已存在")
        
        # 更新欄位
        update_data = credential_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(credential, field, value)
        
        self.db.commit()
        self.db.refresh(credential)
        return credential
    
    def delete_credential(self, credential_id: int) -> bool:
        """
        刪除憑證
        """
        credential = self.db.query(Credential).filter(Credential.id == credential_id).first()
        if not credential:
            return False
        
        # 檢查是否有聊天連結正在使用此憑證
        if credential.chat_links:
            raise ValueError(f"無法刪除憑證，有 {len(credential.chat_links)} 個聊天連結正在使用此憑證")
        
        self.db.delete(credential)
        self.db.commit()
        return True 