from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from app.db.database import get_db
from app.db.models import OperationLog, User
from app.schemas.log_schemas import Log as LogSchema, LogSearch
from app.schemas.common_schemas import PaginatedResponse, DataResponse
from app.apis.deps import get_current_admin_user, get_current_user

# 設定日誌
logger = logging.getLogger(__name__)

# 建立路由
router = APIRouter()

# 取得最近的操作紀錄
@router.get("/recent", response_model=DataResponse[List[LogSchema]])
def get_recent_logs(
    action: Optional[str] = None,
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取得最近的操作紀錄
    
    Args:
        action: 操作類型 (選擇性)
        limit: 回傳筆數上限
        current_user: 目前使用者
        db: 資料庫 session
        
    Returns:
        DataResponse[List[LogSchema]]: 最近的操作紀錄
    """
    try:
        # 建立查詢
        query = db.query(
            OperationLog,
            User.username.label("user_username"),
            User.full_name.label("user_full_name")
        ).join(
            User, OperationLog.user_id == User.id
        )
        
        # 套用過濾條件
        if action:
            query = query.filter(OperationLog.action == action)
        
        # 排序並限制筆數
        query = query.order_by(OperationLog.timestamp.desc()).limit(limit)
        
        # 取得操作紀錄列表
        results = query.all()
        
        # 處理查詢結果
        logs = []
        for log, user_username, user_full_name in results:
            log_dict = {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "details": log.details,
                "ip_address": log.ip_address,
                "timestamp": log.timestamp,  # 使用 timestamp 而不是 created_at
                "user_username": user_username,  # 直接提供 user_username
                "user_full_name": user_full_name  # 直接提供 user_full_name
            }
            logs.append(log_dict)
        
        return DataResponse(
            success=True,
            message="取得最近操作紀錄成功",
            data=logs
        )
    except Exception as e:
        logger.error(f"取得最近操作紀錄失敗: {e}", exc_info=True)
        return DataResponse(
            success=False,
            message=f"取得最近操作紀錄失敗: {str(e)}",
            data=[]
        )

# 取得操作紀錄
@router.get("/", response_model=PaginatedResponse[LogSchema])
def get_logs(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得操作紀錄
    
    Args:
        request: 請求物件
        page: 頁碼
        page_size: 每頁筆數
        user_id: 使用者 ID
        action: 操作類型
        start_date: 開始日期
        end_date: 結束日期
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        PaginatedResponse[LogSchema]: 操作紀錄列表
    """
    # 建立查詢
    query = db.query(
        OperationLog,
        User.username.label("user_username"),
        User.full_name.label("user_full_name")
    ).join(
        User, OperationLog.user_id == User.id
    )
    
    # 套用過濾條件
    if user_id:
        query = query.filter(OperationLog.user_id == user_id)
    if action:
        query = query.filter(OperationLog.action == action)
    if start_date:
        query = query.filter(OperationLog.timestamp >= start_date)
    if end_date:
        query = query.filter(OperationLog.timestamp <= end_date)
    
    # 排序
    query = query.order_by(OperationLog.timestamp.desc())
    
    # 計算總筆數
    total = query.count()
    
    # 套用分頁
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    # 取得操作紀錄列表
    results = query.all()
    
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
            "user_full_name": user_full_name,
        }
        logs.append(log_dict)
    
    # 計算總頁數
    total_pages = (total + page_size - 1) // page_size
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="GET_LOGS",
        details=f"取得操作紀錄 (頁碼: {page}, 每頁筆數: {page_size})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    return PaginatedResponse(
        success=True,
        message="取得操作紀錄成功",
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=logs,
    )

# 搜尋操作紀錄
@router.post("/search", response_model=PaginatedResponse[LogSchema])
def search_logs(
    search_data: LogSearch,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    搜尋操作紀錄
    
    Args:
        search_data: 搜尋條件
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        PaginatedResponse[LogSchema]: 操作紀錄列表
    """
    # 建立查詢
    query = db.query(
        OperationLog,
        User.username.label("user_username"),
        User.full_name.label("user_full_name")
    ).join(
        User, OperationLog.user_id == User.id
    )
    
    # 套用過濾條件
    if search_data.user_id:
        query = query.filter(OperationLog.user_id == search_data.user_id)
    if search_data.action:
        query = query.filter(OperationLog.action == search_data.action)
    if search_data.start_date:
        query = query.filter(OperationLog.timestamp >= search_data.start_date)
    if search_data.end_date:
        query = query.filter(OperationLog.timestamp <= search_data.end_date)
    
    # 排序
    query = query.order_by(OperationLog.timestamp.desc())
    
    # 計算總筆數
    total = query.count()
    
    # 套用分頁
    query = query.offset((search_data.page - 1) * search_data.page_size).limit(search_data.page_size)
    
    # 取得操作紀錄列表
    results = query.all()
    
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
            "user_full_name": user_full_name,
        }
        logs.append(log_dict)
    
    # 計算總頁數
    total_pages = (total + search_data.page_size - 1) // search_data.page_size
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="SEARCH_LOGS",
        details=f"搜尋操作紀錄 (頁碼: {search_data.page}, 每頁筆數: {search_data.page_size})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    return PaginatedResponse(
        success=True,
        message="搜尋操作紀錄成功",
        total=total,
        page=search_data.page,
        page_size=search_data.page_size,
        total_pages=total_pages,
        items=logs,
    )
