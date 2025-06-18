from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.apis.deps import get_current_user
from app.schemas.user_schemas import User
from app.schemas.chat_schemas import (
    ChatSessionCreate, ChatSessionUpdate, ChatSessionResponse,
    ChatMessageCreate, ChatSessionListResponse, ChatSessionDetailResponse,
    EmbeddedChatRequest, WebhookChatRequest, ChatResponse
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["聊天"])

@router.post("/embedded", response_model=ChatResponse, summary="發送訊息到 Embedded Chat")
async def send_embedded_message(
    request: EmbeddedChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    發送訊息到 n8n Embedded Chat
    
    - **link_id**: 聊天連結ID (必須是 n8n_embedded_chat 類型)
    - **message**: 使用者訊息內容
    - **session_id**: 對話 session 唯一識別碼
    """
    try:
        chat_service = ChatService(db)
        result = await chat_service.send_embedded_message(
            current_user.id, 
            request.link_id, 
            request.message, 
            request.session_id
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"發送訊息失敗: {str(e)}"
        )

@router.post("/webhook", response_model=ChatResponse, summary="發送訊息到 Webhook")
async def send_webhook_message(
    request: WebhookChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    發送訊息到 n8n Webhook
    
    - **link_id**: 聊天連結ID (必須是 n8n_webhook 類型)
    - **message**: 使用者訊息內容
    - **session_id**: 對話 session 唯一識別碼
    - **user_id**: 當前登入使用者ID
    - **user_name**: 使用者姓名
    """
    try:
        chat_service = ChatService(db)
        result = await chat_service.send_webhook_message(
            current_user.id,
            request.link_id,
            request.message,
            request.session_id,
            request.user_name
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"發送訊息失敗: {str(e)}"
        )

@router.post("/sessions", response_model=ChatSessionResponse, summary="建立新的聊天會話")
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    建立新的聊天會話
    
    - **chat_link_id**: 聊天連結ID (必須是 webhook 類型)
    - **title**: 會話標題 (可選，預設會自動生成)
    """
    try:
        chat_service = ChatService(db)
        return chat_service.create_session(current_user.id, session_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"建立會話失敗: {str(e)}"
        )

@router.get("/sessions", response_model=ChatSessionListResponse, summary="取得使用者的聊天會話列表")
async def get_user_chat_sessions(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取得當前使用者的聊天會話列表
    
    - **skip**: 跳過的記錄數 (分頁用)
    - **limit**: 每頁記錄數 (最大 100)
    """
    if limit > 100:
        limit = 100
    
    try:
        chat_service = ChatService(db)
        return chat_service.get_user_sessions(current_user.id, skip, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得會話列表失敗: {str(e)}"
        )

@router.get("/sessions/{session_id}", response_model=ChatSessionDetailResponse, summary="取得聊天會話詳細資訊")
async def get_chat_session_detail(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取得聊天會話詳細資訊，包含所有訊息
    
    - **session_id**: 會話唯一識別碼
    """
    try:
        chat_service = ChatService(db)
        session_detail = chat_service.get_session_detail(session_id, current_user.id)
        
        if not session_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="會話不存在或無權限存取"
            )
        
        return session_detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得會話詳細資訊失敗: {str(e)}"
        )

@router.put("/sessions/{session_id}", response_model=ChatSessionResponse, summary="更新聊天會話")
async def update_chat_session(
    session_id: str,
    update_data: ChatSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新聊天會話資訊
    
    - **session_id**: 會話唯一識別碼
    - **title**: 新的會話標題 (可選)
    - **is_active**: 會話是否活躍 (可選)
    """
    try:
        chat_service = ChatService(db)
        updated_session = chat_service.update_session(session_id, current_user.id, update_data)
        
        if not updated_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="會話不存在或無權限存取"
            )
        
        return updated_session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新會話失敗: {str(e)}"
        )

@router.delete("/sessions/{session_id}", summary="刪除聊天會話")
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    刪除聊天會話及其所有訊息
    
    - **session_id**: 會話唯一識別碼
    """
    try:
        chat_service = ChatService(db)
        success = chat_service.delete_session(session_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="會話不存在或無權限存取"
            )
        
        return {"message": "會話已成功刪除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除會話失敗: {str(e)}"
        )

@router.post("/sessions/{session_id}/messages", summary="發送訊息")
async def send_message(
    session_id: str,
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    發送訊息到指定的聊天會話
    
    - **session_id**: 會話唯一識別碼
    - **content**: 訊息內容
    
    此 API 會：
    1. 儲存使用者訊息
    2. 發送到對應的 webhook
    3. 儲存 AI 回應
    4. 返回完整的對話結果
    """
    try:
        # 驗證 session_id 是否一致
        if message_data.session_id != session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="路徑中的 session_id 與請求體中的 session_id 不一致"
            )
        
        chat_service = ChatService(db)
        result = await chat_service.send_message(session_id, current_user.id, message_data.content)
        
        return result
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
            detail=f"發送訊息失敗: {str(e)}"
        )

@router.get("/webhook-links", summary="取得可用的 Webhook 聊天連結")
async def get_webhook_chat_links(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取得當前使用者可以使用的 webhook 類型聊天連結
    """
    try:
        from app.db.models import ChatLink, Group
        from app.db.models import group_chat_link, user_group
        
        # 查詢使用者可以使用的 webhook 類型聊天連結
        webhook_links = (
            db.query(ChatLink)
            .join(group_chat_link, ChatLink.id == group_chat_link.c.chat_link_id)
            .join(Group, Group.id == group_chat_link.c.group_id)
            .join(user_group, Group.id == user_group.c.group_id)
            .filter(user_group.c.user_id == current_user.id)
            .filter(ChatLink.link_type == "n8n_webhook")
            .filter(ChatLink.webhook_url.isnot(None))
            .distinct()
            .all()
        )
        
        return [
            {
                "id": link.id,
                "name": link.name,
                "description": link.description,
                "webhook_url": link.webhook_url,
                "credential_name": link.credential.name if link.credential else None
            }
            for link in webhook_links
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得聊天連結失敗: {str(e)}"
        ) 