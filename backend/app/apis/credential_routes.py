from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.apis.deps import get_db, get_current_admin_user_dependency
from app.schemas.credential_schemas import (
    CredentialCreate, 
    CredentialUpdate, 
    CredentialResponse, 
    CredentialListResponse,
    CredentialSimple
)
from app.services.credential_service import CredentialService
from app.db.models import User, OperationLog

router = APIRouter()

@router.get("/", response_model=CredentialListResponse)
async def get_credentials(
    skip: int = Query(0, ge=0, description="跳過的記錄數"),
    limit: int = Query(100, ge=1, le=1000, description="返回的記錄數"),
    search: Optional[str] = Query(None, description="搜尋關鍵字"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user_dependency)
):
    """
    取得憑證列表 (僅管理員)
    """
    try:
        service = CredentialService(db)
        credentials, total = service.get_credentials(skip=skip, limit=limit, search=search)
        
        # 記錄操作日誌
        log = OperationLog(
            user_id=current_user.id,
            action="VIEW_CREDENTIALS",
            details=f"查看憑證列表，搜尋條件: {search or '無'}"
        )
        db.add(log)
        db.commit()
        
        return CredentialListResponse(
            credentials=credentials,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得憑證列表失敗: {str(e)}"
        )

@router.get("/simple", response_model=List[CredentialSimple])
async def get_credentials_simple(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user_dependency)
):
    """
    取得簡化憑證列表 (僅管理員) - 用於下拉選單
    """
    try:
        service = CredentialService(db)
        credentials = service.get_credentials_simple()
        return credentials
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得憑證列表失敗: {str(e)}"
        )

@router.get("/{credential_id}", response_model=CredentialResponse)
async def get_credential(
    credential_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user_dependency)
):
    """
    取得單一憑證 (僅管理員)
    """
    try:
        service = CredentialService(db)
        credential = service.get_credential(credential_id)
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="憑證不存在"
            )
        
        # 記錄操作日誌
        log = OperationLog(
            user_id=current_user.id,
            action="VIEW_CREDENTIAL",
            details=f"查看憑證: {credential.name}"
        )
        db.add(log)
        db.commit()
        
        return credential
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得憑證失敗: {str(e)}"
        )

@router.post("/", response_model=CredentialResponse)
async def create_credential(
    credential_data: CredentialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user_dependency)
):
    """
    建立憑證 (僅管理員)
    """
    try:
        service = CredentialService(db)
        credential = service.create_credential(credential_data)
        
        # 記錄操作日誌
        log = OperationLog(
            user_id=current_user.id,
            action="CREATE_CREDENTIAL",
            details=f"建立憑證: {credential.name}"
        )
        db.add(log)
        db.commit()
        
        return credential
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"建立憑證失敗: {str(e)}"
        )

@router.put("/{credential_id}", response_model=CredentialResponse)
async def update_credential(
    credential_id: int,
    credential_data: CredentialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user_dependency)
):
    """
    更新憑證 (僅管理員)
    """
    try:
        service = CredentialService(db)
        credential = service.update_credential(credential_id, credential_data)
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="憑證不存在"
            )
        
        # 記錄操作日誌
        log = OperationLog(
            user_id=current_user.id,
            action="UPDATE_CREDENTIAL",
            details=f"更新憑證: {credential.name}"
        )
        db.add(log)
        db.commit()
        
        return credential
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新憑證失敗: {str(e)}"
        )

@router.delete("/{credential_id}")
async def delete_credential(
    credential_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user_dependency)
):
    """
    刪除憑證 (僅管理員)
    """
    try:
        service = CredentialService(db)
        credential = service.get_credential(credential_id)
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="憑證不存在"
            )
        
        # 檢查是否有聊天連結正在使用此憑證
        if credential.chat_links:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"無法刪除憑證，有 {len(credential.chat_links)} 個聊天連結正在使用此憑證"
            )
        
        success = service.delete_credential(credential_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="憑證不存在"
            )
        
        # 記錄操作日誌
        log = OperationLog(
            user_id=current_user.id,
            action="DELETE_CREDENTIAL",
            details=f"刪除憑證: {credential.name}"
        )
        db.add(log)
        db.commit()
        
        return {"message": "憑證刪除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除憑證失敗: {str(e)}"
        ) 