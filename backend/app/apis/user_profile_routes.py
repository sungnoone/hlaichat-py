from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db.database import get_db
from app.db.models import User, OperationLog, ChatSession, ChatMessage, ChatLink
from app.schemas.common_schemas import DataResponse
from app.apis.deps import get_current_user

# 設定日誌
logger = logging.getLogger(__name__)

# 建立路由
router = APIRouter()

# 取得自己的操作紀錄
@router.get("/operation-logs", response_model=DataResponse[List[dict]])
def get_my_operation_logs(
    request: Request,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取得自己的操作紀錄
    
    Args:
        request: 請求物件
        limit: 回傳筆數上限
        current_user: 目前使用者
        db: 資料庫 session
        
    Returns:
        DataResponse[List[dict]]: 操作紀錄列表
    """
    logger.info(f"使用者 {current_user.username} (ID: {current_user.id}) 請求操作紀錄")
    
    try:
        # 建立查詢
        query = db.query(
            OperationLog,
            User.username.label("user_username"),
            User.full_name.label("user_full_name")
        ).join(
            User, OperationLog.user_id == User.id
        )
        
        # 只查詢自己的操作紀錄
        query = query.filter(OperationLog.user_id == current_user.id)
        
        # 排序並限制筆數
        query = query.order_by(OperationLog.timestamp.desc()).limit(limit)
        
        # 取得操作紀錄列表
        results = query.all()
        logger.info(f"找到 {len(results)} 筆操作紀錄")
        
        # 處理查詢結果
        logs = []
        for log, user_username, user_full_name in results:
            log_dict = {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "details": log.details,
                "ip_address": log.ip_address,
                "timestamp": log.timestamp,
                "user_username": user_username,
                "user_full_name": user_full_name
            }
            logs.append(log_dict)
        
        logger.info(f"回傳 {len(logs)} 筆操作紀錄給使用者 {current_user.username}")
        
        return DataResponse(
            success=True,
            message="取得操作紀錄成功",
            data=logs
        )
    except Exception as e:
        logger.error(f"取得操作紀錄失敗: {e}", exc_info=True)
        return DataResponse(
            success=False,
            message=f"取得操作紀錄失敗: {str(e)}",
            data=[]
        )

# 取得自己的聊天紀錄
@router.get("/chat-history", response_model=DataResponse[List[dict]])
def get_my_chat_history(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取得自己的聊天紀錄
    
    Args:
        request: 請求物件
        limit: 回傳筆數上限
        current_user: 目前使用者
        db: 資料庫 session
        
    Returns:
        DataResponse[List[dict]]: 聊天紀錄列表
    """
    logger.info(f"使用者 {current_user.username} (ID: {current_user.id}) 請求聊天紀錄")
    
    try:
        # 建立查詢，取得使用者的聊天訊息
        query = db.query(
            ChatMessage,
            ChatSession.title.label("session_title"),
            ChatLink.name.label("chat_link_name")
        ).join(
            ChatSession, ChatMessage.session_id == ChatSession.session_id
        ).join(
            ChatLink, ChatSession.chat_link_id == ChatLink.id
        ).filter(
            ChatSession.user_id == current_user.id,
            ChatMessage.message_type == "user"  # 只顯示使用者的訊息
        )
        
        # 排序並限制筆數
        query = query.order_by(ChatMessage.timestamp.desc()).limit(limit)
        
        # 取得聊天紀錄列表
        results = query.all()
        logger.info(f"找到 {len(results)} 筆聊天紀錄")
        
        # 處理查詢結果
        chat_history = []
        for message, session_title, chat_link_name in results:
            chat_dict = {
                "id": message.id,
                "session_id": message.session_id,
                "message": message.content[:100] + ("..." if len(message.content) > 100 else ""),  # 限制顯示長度
                "full_message": message.content,
                "session_title": session_title,
                "chat_link_name": chat_link_name,
                "created_at": message.timestamp
            }
            chat_history.append(chat_dict)
        
        logger.info(f"回傳 {len(chat_history)} 筆聊天紀錄給使用者 {current_user.username}")
        
        return DataResponse(
            success=True,
            message="取得聊天紀錄成功",
            data=chat_history
        )
    except Exception as e:
        logger.error(f"取得聊天紀錄失敗: {e}", exc_info=True)
        return DataResponse(
            success=False,
            message=f"取得聊天紀錄失敗: {str(e)}",
            data=[]
        ) 