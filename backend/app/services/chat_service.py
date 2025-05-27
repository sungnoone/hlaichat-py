import uuid
import json
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
import httpx

from app.db.models import ChatSession, ChatMessage, ChatLink, User
from app.schemas.chat_schemas import (
    ChatSessionCreate, ChatSessionUpdate, ChatSessionResponse,
    ChatMessageCreate, ChatMessageResponse, WebhookRequest,
    ChatSessionListResponse, ChatMessageListResponse, ChatSessionDetailResponse
)
from app.core.config import settings

class ChatService:
    """聊天服務類別，處理聊天會話和訊息相關業務邏輯"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, user_id: int, session_data: ChatSessionCreate) -> ChatSessionResponse:
        """建立新的聊天會話"""
        # 生成唯一的 session_id
        session_id = str(uuid.uuid4())
        
        # 檢查聊天連結是否存在且為 webhook 類型
        chat_link = self.db.query(ChatLink).filter(ChatLink.id == session_data.chat_link_id).first()
        if not chat_link:
            raise ValueError("聊天連結不存在")
        if chat_link.link_type != "n8n_webhook":
            raise ValueError("此聊天連結不支援 webhook 模式")
        
        # 建立會話
        db_session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            chat_link_id=session_data.chat_link_id,
            title=session_data.title or f"新對話 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        
        return ChatSessionResponse.model_validate(db_session)
    
    def get_user_sessions(self, user_id: int, skip: int = 0, limit: int = 50) -> ChatSessionListResponse:
        """取得使用者的聊天會話列表"""
        sessions = (
            self.db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(desc(ChatSession.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        total = self.db.query(ChatSession).filter(ChatSession.user_id == user_id).count()
        
        return ChatSessionListResponse(
            sessions=[ChatSessionResponse.model_validate(session) for session in sessions],
            total=total
        )
    
    def get_session_detail(self, session_id: str, user_id: int) -> Optional[ChatSessionDetailResponse]:
        """取得聊天會話詳細資訊，包含訊息列表"""
        session = (
            self.db.query(ChatSession)
            .filter(and_(ChatSession.session_id == session_id, ChatSession.user_id == user_id))
            .first()
        )
        
        if not session:
            return None
        
        # 取得訊息列表
        messages = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.sequence)
            .all()
        )
        
        # 取得聊天連結名稱
        chat_link = self.db.query(ChatLink).filter(ChatLink.id == session.chat_link_id).first()
        
        session_response = ChatSessionDetailResponse.model_validate(session)
        session_response.messages = [ChatMessageResponse.model_validate(msg) for msg in messages]
        session_response.chat_link_name = chat_link.name if chat_link else None
        
        return session_response
    
    def update_session(self, session_id: str, user_id: int, update_data: ChatSessionUpdate) -> Optional[ChatSessionResponse]:
        """更新聊天會話"""
        session = (
            self.db.query(ChatSession)
            .filter(and_(ChatSession.session_id == session_id, ChatSession.user_id == user_id))
            .first()
        )
        
        if not session:
            return None
        
        # 更新欄位
        if update_data.title is not None:
            session.title = update_data.title
        if update_data.is_active is not None:
            session.is_active = update_data.is_active
        
        session.updated_at = settings.get_taipei_now()
        
        self.db.commit()
        self.db.refresh(session)
        
        return ChatSessionResponse.model_validate(session)
    
    def delete_session(self, session_id: str, user_id: int) -> bool:
        """刪除聊天會話"""
        session = (
            self.db.query(ChatSession)
            .filter(and_(ChatSession.session_id == session_id, ChatSession.user_id == user_id))
            .first()
        )
        
        if not session:
            return False
        
        self.db.delete(session)
        self.db.commit()
        return True
    
    def get_next_sequence(self, session_id: str) -> int:
        """取得下一個訊息序號"""
        last_message = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(desc(ChatMessage.sequence))
            .first()
        )
        
        return (last_message.sequence + 1) if last_message else 1
    
    async def send_message(self, session_id: str, user_id: int, content: str) -> Dict[str, Any]:
        """發送訊息到 webhook 並處理回應"""
        # 檢查會話是否存在且屬於該使用者
        session = (
            self.db.query(ChatSession)
            .filter(and_(ChatSession.session_id == session_id, ChatSession.user_id == user_id))
            .first()
        )
        
        if not session:
            raise ValueError("會話不存在或無權限存取")
        
        # 取得聊天連結和使用者資訊
        chat_link = self.db.query(ChatLink).filter(ChatLink.id == session.chat_link_id).first()
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not chat_link or not chat_link.webhook_url:
            raise ValueError("聊天連結不存在或未設定 webhook 網址")
        
        if not user:
            raise ValueError("使用者不存在")
        
        # 取得下一個序號
        sequence = self.get_next_sequence(session_id)
        
        # 儲存使用者訊息
        user_message = ChatMessage(
            session_id=session_id,
            sequence=sequence,
            message_type="user",
            content=content
        )
        self.db.add(user_message)
        self.db.commit()
        self.db.refresh(user_message)
        
        # 準備 webhook 請求
        webhook_data = WebhookRequest(
            user_id=user_id,
            session_id=session_id,
            api_key=chat_link.credential.api_key if chat_link.credential else "",
            message=content,
            sequence=sequence,
            timestamp=settings.get_taipei_now().isoformat(),
            user_name=user.full_name
        )
        
        # 發送到 webhook
        start_time = time.time()
        try:
            # 使用環境變數中的逾時設定
            timeout_config = httpx.Timeout(
                connect=settings.CHAT_CONNECTION_TIMEOUT,
                read=settings.CHAT_WEBHOOK_TIMEOUT,
                write=settings.CHAT_REQUEST_TIMEOUT,
                pool=settings.CHAT_REQUEST_TIMEOUT
            )
            async with httpx.AsyncClient(timeout=timeout_config) as client:
                response = await client.post(
                    chat_link.webhook_url,
                    json=webhook_data.dict(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                processing_time = int((time.time() - start_time) * 1000)
                
                # 記錄原始回應內容以便除錯
                response_text = response.text
                print(f"Webhook 原始回應: {response_text}")
                print(f"Webhook 回應狀態碼: {response.status_code}")
                print(f"Webhook 回應標頭: {dict(response.headers)}")
                
                # 嘗試解析 JSON
                try:
                    response_data = response.json()
                    print(f"Webhook 解析後的 JSON: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                except json.JSONDecodeError as json_error:
                    print(f"JSON 解析錯誤: {json_error}")
                    print(f"無法解析的內容: {response_text}")
                    # 如果無法解析 JSON，將原始文字作為回應內容
                    response_data = {"output": response_text}
                
                # 儲存 AI 回應訊息
                ai_sequence = self.get_next_sequence(session_id)
                
                # 嘗試從不同的欄位取得回應內容
                # n8n 的 "Respond to Webhook" 節點通常使用 "output" 欄位
                ai_content = (
                    response_data.get("output") or 
                    response_data.get("message") or 
                    response_data.get("text") or 
                    response_data.get("content") or
                    "無回應內容"
                )
                
                ai_message = ChatMessage(
                    session_id=session_id,
                    sequence=ai_sequence,
                    message_type="assistant",
                    content=ai_content,
                    webhook_response=json.dumps(response_data, ensure_ascii=False),
                    processing_time=processing_time
                )
                self.db.add(ai_message)
                
                # 更新會話的最後更新時間
                session.updated_at = settings.get_taipei_now()
                
                # 如果會話還沒有標題，使用第一條訊息生成標題
                if not session.title or session.title.startswith("新對話"):
                    session.title = content[:30] + ("..." if len(content) > 30 else "")
                
                self.db.commit()
                self.db.refresh(ai_message)
                
                return {
                    "success": True,
                    "user_message": ChatMessageResponse.model_validate(user_message),
                    "ai_message": ChatMessageResponse.model_validate(ai_message),
                    "processing_time": processing_time
                }
                
        except httpx.TimeoutException:
            # 處理超時錯誤
            error_message = "請求超時，請稍後再試"
            ai_sequence = self.get_next_sequence(session_id)
            error_response = ChatMessage(
                session_id=session_id,
                sequence=ai_sequence,
                message_type="assistant",
                content=error_message,
                processing_time=int((time.time() - start_time) * 1000)
            )
            self.db.add(error_response)
            self.db.commit()
            self.db.refresh(error_response)
            
            return {
                "success": False,
                "error": "timeout",
                "user_message": ChatMessageResponse.model_validate(user_message),
                "ai_message": ChatMessageResponse.model_validate(error_response)
            }
            
        except httpx.HTTPStatusError as e:
            # 處理 HTTP 錯誤
            error_message = f"伺服器錯誤 ({e.response.status_code})"
            ai_sequence = self.get_next_sequence(session_id)
            error_response = ChatMessage(
                session_id=session_id,
                sequence=ai_sequence,
                message_type="assistant",
                content=error_message,
                processing_time=int((time.time() - start_time) * 1000)
            )
            self.db.add(error_response)
            self.db.commit()
            self.db.refresh(error_response)
            
            return {
                "success": False,
                "error": "http_error",
                "user_message": ChatMessageResponse.model_validate(user_message),
                "ai_message": ChatMessageResponse.model_validate(error_response)
            }
            
        except Exception as e:
            # 處理其他錯誤
            print(f"發送 webhook 時發生錯誤: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"錯誤堆疊: {traceback.format_exc()}")
            
            error_message = f"發生未知錯誤: {str(e)}"
            ai_sequence = self.get_next_sequence(session_id)
            error_response = ChatMessage(
                session_id=session_id,
                sequence=ai_sequence,
                message_type="assistant",
                content=error_message,
                processing_time=int((time.time() - start_time) * 1000)
            )
            self.db.add(error_response)
            self.db.commit()
            self.db.refresh(error_response)
            
            return {
                "success": False,
                "error": "unknown",
                "user_message": ChatMessageResponse.model_validate(user_message),
                "ai_message": ChatMessageResponse.model_validate(error_response)
            } 