from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db.database import get_db
from app.db.models import User, Group, OperationLog
from app.schemas.user_schemas import User as UserSchema, UserCreate, UserUpdate, UserUpdatePassword
from app.schemas.common_schemas import ResponseBase, DataResponse, PaginatedResponse
from app.apis.deps import get_current_user, get_current_admin_user

# 設定日誌
logger = logging.getLogger(__name__)

# 建立路由
router = APIRouter()

# 取得所有使用者
@router.get("/", response_model=PaginatedResponse[UserSchema])
def get_users(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
    username: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_ad_user: Optional[bool] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得所有使用者
    
    Args:
        request: 請求物件
        page: 頁碼
        page_size: 每頁筆數
        username: 使用者名稱 (模糊搜尋)
        is_active: 是否啟用
        is_ad_user: 是否為 AD 使用者
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        PaginatedResponse[UserSchema]: 使用者列表
    """
    # 建立查詢
    query = db.query(User)
    
    # 套用過濾條件
    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if is_ad_user is not None:
        query = query.filter(User.is_ad_user == is_ad_user)
    
    # 計算總筆數
    total = query.count()
    
    # 套用分頁
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    # 取得使用者列表
    users = query.all()
    
    # 計算總頁數
    total_pages = (total + page_size - 1) // page_size
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="GET_USERS",
        details=f"取得使用者列表 (頁碼: {page}, 每頁筆數: {page_size})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    return PaginatedResponse(
        success=True,
        message="取得使用者列表成功",
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=users,
    )

# 取得單一使用者
@router.get("/{user_id}", response_model=DataResponse[UserSchema])
def get_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得單一使用者
    
    Args:
        user_id: 使用者 ID
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        DataResponse[UserSchema]: 使用者資料
        
    Raises:
        HTTPException: 使用者不存在
    """
    # 查詢使用者
    user = db.query(User).filter(User.id == user_id).first()
    
    # 檢查使用者是否存在
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"使用者不存在 (ID: {user_id})",
        )
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="GET_USER",
        details=f"取得使用者資料 (ID: {user_id})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    return DataResponse(
        success=True,
        message="取得使用者資料成功",
        data=user,
    )

# 建立使用者
@router.post("/", response_model=DataResponse[UserSchema])
def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    建立使用者
    
    Args:
        user_data: 使用者資料
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        DataResponse[UserSchema]: 使用者資料
        
    Raises:
        HTTPException: 使用者名稱已存在
    """
    # 檢查使用者名稱是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"使用者名稱已存在 (使用者名稱: {user_data.username})",
        )
    
    # 建立使用者
    user = User(
        username=user_data.username,
        password=user_data.password,  # 明文密碼
        full_name=user_data.full_name,
        phone=user_data.phone,
        department=user_data.department,
        email=user_data.email,
        is_active=user_data.is_active,
        notes=user_data.notes,
        is_ad_user=user_data.is_ad_user,
        ad_guid=user_data.ad_guid,
    )
    
    # 加入群組
    if user_data.group_ids:
        groups = db.query(Group).filter(Group.id.in_(user_data.group_ids)).all()
        user.groups = groups
    
    # 儲存使用者
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="CREATE_USER",
        details=f"建立使用者 (ID: {user.id}, 使用者名稱: {user.username})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    logger.info(f"建立使用者成功: {user.username} (ID: {user.id})")
    
    return DataResponse(
        success=True,
        message="建立使用者成功",
        data=user,
    )

# 更新使用者
@router.put("/{user_id}", response_model=DataResponse[UserSchema])
def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新使用者
    
    Args:
        user_id: 使用者 ID
        user_data: 使用者資料
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        DataResponse[UserSchema]: 使用者資料
        
    Raises:
        HTTPException: 使用者不存在
    """
    # 查詢使用者
    user = db.query(User).filter(User.id == user_id).first()
    
    # 檢查使用者是否存在
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"使用者不存在 (ID: {user_id})",
        )
    
    # 更新使用者資料
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.phone is not None:
        user.phone = user_data.phone
    if user_data.department is not None:
        user.department = user_data.department
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.notes is not None:
        user.notes = user_data.notes
    
    # 更新群組
    if user_data.group_ids is not None:
        logger.info(f"更新使用者群組: 使用者ID={user_id}, 使用者名稱={user.username}, 原群組IDs={[g.id for g in user.groups]}, 新群組IDs={user_data.group_ids}")
        groups = db.query(Group).filter(Group.id.in_(user_data.group_ids)).all()
        logger.info(f"找到群組數量: {len(groups)}, 群組詳情: {[(g.id, g.name) for g in groups]}")
        user.groups = groups
    
    # 儲存使用者
    db.commit()
    db.refresh(user)
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="UPDATE_USER",
        details=f"更新使用者 (ID: {user.id}, 使用者名稱: {user.username})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    logger.info(f"更新使用者成功: {user.username} (ID: {user.id})")
    
    return DataResponse(
        success=True,
        message="更新使用者成功",
        data=user,
    )

# 更新使用者密碼
@router.put("/{user_id}/password", response_model=ResponseBase)
def update_user_password(
    user_id: int,
    password_data: UserUpdatePassword,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新使用者密碼
    
    Args:
        user_id: 使用者 ID
        password_data: 密碼資料
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        ResponseBase: 更新成功回應
        
    Raises:
        HTTPException: 使用者不存在
    """
    # 查詢使用者
    user = db.query(User).filter(User.id == user_id).first()
    
    # 檢查使用者是否存在
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"使用者不存在 (ID: {user_id})",
        )
    
    # 檢查是否為 AD 使用者
    if user.is_ad_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無法更新 AD 使用者的密碼",
        )
    
    # 更新密碼
    user.password = password_data.password  # 明文密碼
    
    # 儲存使用者
    db.commit()
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="UPDATE_USER_PASSWORD",
        details=f"更新使用者密碼 (ID: {user.id}, 使用者名稱: {user.username})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    logger.info(f"更新使用者密碼成功: {user.username} (ID: {user.id})")
    
    return ResponseBase(
        success=True,
        message="更新使用者密碼成功",
    )

# 刪除使用者
@router.delete("/{user_id}", response_model=ResponseBase)
def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    刪除使用者
    
    Args:
        user_id: 使用者 ID
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        ResponseBase: 刪除成功回應
        
    Raises:
        HTTPException: 使用者不存在
    """
    # 查詢使用者
    user = db.query(User).filter(User.id == user_id).first()
    
    # 檢查使用者是否存在
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"使用者不存在 (ID: {user_id})",
        )
    
    # 檢查是否為自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無法刪除自己的帳號",
        )
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="DELETE_USER",
        details=f"刪除使用者 (ID: {user.id}, 使用者名稱: {user.username})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    # 刪除使用者
    db.delete(user)
    db.commit()
    
    logger.info(f"刪除使用者成功: {user.username} (ID: {user.id})")
    
    return ResponseBase(
        success=True,
        message="刪除使用者成功",
    )

# 更新自己的密碼
@router.put("/me/password", response_model=ResponseBase)
def update_my_password(
    password_data: UserUpdatePassword,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新自己的密碼
    
    Args:
        password_data: 密碼資料
        request: 請求物件
        current_user: 目前使用者
        db: 資料庫 session
        
    Returns:
        ResponseBase: 更新成功回應
    """
    # 檢查是否為 AD 使用者
    if current_user.is_ad_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無法更新 AD 使用者的密碼",
        )
    
    # 更新密碼
    current_user.password = password_data.password  # 明文密碼
    
    # 儲存使用者
    db.commit()
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="UPDATE_MY_PASSWORD",
        details=f"更新自己的密碼 (ID: {current_user.id}, 使用者名稱: {current_user.username})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    logger.info(f"更新自己的密碼成功: {current_user.username} (ID: {current_user.id})")
    
    return ResponseBase(
        success=True,
        message="更新密碼成功",
    )

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
