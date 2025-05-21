from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db.database import get_db
from app.db.models import Group, User, ChatLink, OperationLog
from app.schemas.group_schemas import Group as GroupSchema, GroupCreate, GroupUpdate
from app.schemas.common_schemas import ResponseBase, DataResponse, PaginatedResponse
from app.apis.deps import get_current_user, get_current_admin_user

# 設定日誌
logger = logging.getLogger(__name__)

# 建立路由
router = APIRouter()

# 取得所有群組
@router.get("/", response_model=PaginatedResponse[GroupSchema])
def get_groups(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得所有群組
    
    Args:
        request: 請求物件
        page: 頁碼
        page_size: 每頁筆數
        name: 群組名稱 (模糊搜尋)
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        PaginatedResponse[GroupSchema]: 群組列表
    """
    # 建立查詢
    query = db.query(Group)
    
    # 套用過濾條件
    if name:
        query = query.filter(Group.name.ilike(f"%{name}%"))
    
    # 計算總筆數
    total = query.count()
    
    # 套用分頁
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    # 取得群組列表
    groups = query.all()
    
    # 計算總頁數
    total_pages = (total + page_size - 1) // page_size
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="GET_GROUPS",
        details=f"取得群組列表 (頁碼: {page}, 每頁筆數: {page_size})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    return PaginatedResponse(
        success=True,
        message="取得群組列表成功",
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=groups,
    )

# 取得單一群組
@router.get("/{group_id}", response_model=DataResponse[GroupSchema])
def get_group(
    group_id: int,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得單一群組
    
    Args:
        group_id: 群組 ID
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        DataResponse[GroupSchema]: 群組資料
        
    Raises:
        HTTPException: 群組不存在
    """
    # 查詢群組
    group = db.query(Group).filter(Group.id == group_id).first()
    
    # 檢查群組是否存在
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"群組不存在 (ID: {group_id})",
        )
    
    # 記錄群組成員資訊
    logger.info(f"獲取群組資料: 群組ID={group_id}, 群組名稱={group.name}, 成員數量={len(group.users)}")
    if len(group.users) > 0:
        logger.info(f"群組成員詳情: {[(u.id, u.username) for u in group.users]}")
    else:
        logger.info(f"群組沒有成員")
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="GET_GROUP",
        details=f"取得群組資料 (ID: {group_id})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    return DataResponse(
        success=True,
        message="取得群組資料成功",
        data=group,
    )

# 建立群組
@router.post("/", response_model=DataResponse[GroupSchema])
def create_group(
    group_data: GroupCreate,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    建立群組
    
    Args:
        group_data: 群組資料
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        DataResponse[GroupSchema]: 群組資料
        
    Raises:
        HTTPException: 群組名稱已存在
    """
    # 檢查群組名稱是否已存在
    existing_group = db.query(Group).filter(Group.name == group_data.name).first()
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"群組名稱已存在 (群組名稱: {group_data.name})",
        )
    
    # 建立群組
    group = Group(
        name=group_data.name,
        description=group_data.description,
        can_login=group_data.can_login,
        can_manage_platform=group_data.can_manage_platform,
        can_use_chat_links=group_data.can_use_chat_links,
    )
    
    # 加入使用者
    if group_data.user_ids:
        users = db.query(User).filter(User.id.in_(group_data.user_ids)).all()
        group.users = users
    
    # 加入聊天連結
    if group_data.chat_link_ids:
        chat_links = db.query(ChatLink).filter(ChatLink.id.in_(group_data.chat_link_ids)).all()
        group.chat_links = chat_links
    
    # 儲存群組
    db.add(group)
    db.commit()
    db.refresh(group)
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="CREATE_GROUP",
        details=f"建立群組 (ID: {group.id}, 群組名稱: {group.name})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    logger.info(f"建立群組成功: {group.name} (ID: {group.id})")
    
    return DataResponse(
        success=True,
        message="建立群組成功",
        data=group,
    )

# 更新群組
@router.put("/{group_id}", response_model=DataResponse[GroupSchema])
def update_group(
    group_id: int,
    group_data: GroupUpdate,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新群組
    
    Args:
        group_id: 群組 ID
        group_data: 群組資料
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        DataResponse[GroupSchema]: 群組資料
        
    Raises:
        HTTPException: 群組不存在
    """
    # 查詢群組
    group = db.query(Group).filter(Group.id == group_id).first()
    
    # 檢查群組是否存在
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"群組不存在 (ID: {group_id})",
        )
    
    # 檢查是否為 admins 群組
    if group.name == "admins" and group_data.name and group_data.name != "admins":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無法更改 admins 群組的名稱",
        )
    
    # 檢查群組名稱是否已存在
    if group_data.name and group_data.name != group.name:
        existing_group = db.query(Group).filter(Group.name == group_data.name).first()
        if existing_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"群組名稱已存在 (群組名稱: {group_data.name})",
            )
    
    # 更新群組資料
    if group_data.name is not None:
        group.name = group_data.name
    if group_data.description is not None:
        group.description = group_data.description
    if group_data.can_login is not None:
        group.can_login = group_data.can_login
    if group_data.can_manage_platform is not None:
        # 檢查是否為 admins 群組
        if group.name == "admins" and not group_data.can_manage_platform:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無法移除 admins 群組的管理平台權限",
            )
        group.can_manage_platform = group_data.can_manage_platform
    if group_data.can_use_chat_links is not None:
        group.can_use_chat_links = group_data.can_use_chat_links
    
    # 更新使用者
    if group_data.user_ids is not None:
        users = db.query(User).filter(User.id.in_(group_data.user_ids)).all()
        group.users = users
    
    # 更新聊天連結
    if group_data.chat_link_ids is not None:
        chat_links = db.query(ChatLink).filter(ChatLink.id.in_(group_data.chat_link_ids)).all()
        group.chat_links = chat_links
    
    # 儲存群組
    db.commit()
    db.refresh(group)
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="UPDATE_GROUP",
        details=f"更新群組 (ID: {group.id}, 群組名稱: {group.name})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    logger.info(f"更新群組成功: {group.name} (ID: {group.id})")
    
    return DataResponse(
        success=True,
        message="更新群組成功",
        data=group,
    )

# 刪除群組
@router.delete("/{group_id}", response_model=ResponseBase)
def delete_group(
    group_id: int,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    刪除群組
    
    Args:
        group_id: 群組 ID
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        ResponseBase: 刪除成功回應
        
    Raises:
        HTTPException: 群組不存在
    """
    # 查詢群組
    group = db.query(Group).filter(Group.id == group_id).first()
    
    # 檢查群組是否存在
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"群組不存在 (ID: {group_id})",
        )
    
    # 檢查是否為 admins 群組
    if group.name == "admins":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無法刪除 admins 群組",
        )
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="DELETE_GROUP",
        details=f"刪除群組 (ID: {group.id}, 群組名稱: {group.name})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    # 刪除群組
    db.delete(group)
    db.commit()
    
    logger.info(f"刪除群組成功: {group.name} (ID: {group.id})")
    
    return ResponseBase(
        success=True,
        message="刪除群組成功",
    )
