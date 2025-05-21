from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db.database import get_db
from app.db.models import ChatLink, Group, User, OperationLog
from app.schemas.chat_link_schemas import ChatLink as ChatLinkSchema, ChatLinkCreate, ChatLinkUpdate
from app.schemas.common_schemas import ResponseBase, DataResponse, PaginatedResponse
from app.apis.deps import get_current_user, get_current_admin_user, check_user_can_use_chat_links

# 設定日誌
logger = logging.getLogger(__name__)

# 建立路由
router = APIRouter()

# 取得最近的聊天連結
@router.get("/recent", response_model=DataResponse[List[ChatLinkSchema]])
def get_recent_chat_links(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取得最近的聊天連結
    
    Args:
        limit: 回傳筆數上限
        current_user: 目前使用者
        db: 資料庫 session
        
    Returns:
        DataResponse[List[ChatLinkSchema]]: 最近的聊天連結
    """
    try:
        # 建立查詢
        query = db.query(ChatLink)
        
        # 排序並限制筆數
        query = query.order_by(ChatLink.created_at.desc()).limit(limit)
        
        # 取得聊天連結列表
        chat_links = query.all()
        
        return DataResponse(
            success=True,
            message="取得最近聊天連結成功",
            data=chat_links
        )
    except Exception as e:
        logger.error(f"取得最近聊天連結失敗: {e}", exc_info=True)
        return DataResponse(
            success=False,
            message=f"取得最近聊天連結失敗: {str(e)}",
            data=[]
        )

# 取得所有聊天連結 (管理者)
@router.get("/admin", response_model=PaginatedResponse[ChatLinkSchema])
def get_chat_links_admin(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    link_type: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得所有聊天連結 (管理者)
    
    Args:
        request: 請求物件
        page: 頁碼
        page_size: 每頁筆數
        name: 聊天連結名稱 (模糊搜尋)
        link_type: 連結類型 ('hosted' 或 'embedded')
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        PaginatedResponse[ChatLinkSchema]: 聊天連結列表
    """
    # 建立查詢
    query = db.query(ChatLink)
    
    # 套用過濾條件
    if name:
        query = query.filter(ChatLink.name.ilike(f"%{name}%"))
    if link_type:
        query = query.filter(ChatLink.link_type == link_type)
    
    # 計算總筆數
    total = query.count()
    
    # 套用分頁
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    # 取得聊天連結列表
    chat_links = query.all()
    
    # 計算總頁數
    total_pages = (total + page_size - 1) // page_size
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="GET_CHAT_LINKS_ADMIN",
        details=f"取得所有聊天連結 (頁碼: {page}, 每頁筆數: {page_size})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    return PaginatedResponse(
        success=True,
        message="取得聊天連結列表成功",
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=chat_links,
    )

# 取得使用者可用的聊天連結
@router.get("/", response_model=PaginatedResponse[ChatLinkSchema])
def get_chat_links(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    link_type: Optional[str] = None,
    current_user: User = Depends(check_user_can_use_chat_links),
    db: Session = Depends(get_db)
):
    """
    取得使用者可用的聊天連結
    
    Args:
        request: 請求物件
        page: 頁碼
        page_size: 每頁筆數
        name: 聊天連結名稱 (模糊搜尋)
        link_type: 連結類型 ('hosted' 或 'embedded')
        current_user: 目前使用者 (需有使用聊天連結權限)
        db: 資料庫 session
        
    Returns:
        PaginatedResponse[ChatLinkSchema]: 聊天連結列表
    """
    # 取得使用者所屬群組的 ID 列表
    group_ids = [group.id for group in current_user.groups]
    
    # 建立查詢
    query = db.query(ChatLink).join(
        ChatLink.groups
    ).filter(
        Group.id.in_(group_ids)
    )
    
    # 套用過濾條件
    if name:
        query = query.filter(ChatLink.name.ilike(f"%{name}%"))
    if link_type:
        query = query.filter(ChatLink.link_type == link_type)
    
    # 計算總筆數
    total = query.count()
    
    # 套用分頁
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    # 取得聊天連結列表
    chat_links = query.all()
    
    # 計算總頁數
    total_pages = (total + page_size - 1) // page_size
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="GET_CHAT_LINKS",
        details=f"取得可用聊天連結 (頁碼: {page}, 每頁筆數: {page_size})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    return PaginatedResponse(
        success=True,
        message="取得聊天連結列表成功",
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=chat_links,
    )

# 取得單一聊天連結 (管理者)
@router.get("/admin/{chat_link_id}", response_model=DataResponse[ChatLinkSchema])
def get_chat_link_admin(
    chat_link_id: int,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得單一聊天連結 (管理者)
    
    Args:
        chat_link_id: 聊天連結 ID
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        DataResponse[ChatLinkSchema]: 聊天連結資料
        
    Raises:
        HTTPException: 聊天連結不存在
    """
    # 查詢聊天連結
    chat_link = db.query(ChatLink).filter(ChatLink.id == chat_link_id).first()
    
    # 檢查聊天連結是否存在
    if not chat_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"聊天連結不存在 (ID: {chat_link_id})",
        )
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="GET_CHAT_LINK_ADMIN",
        details=f"取得聊天連結資料 (ID: {chat_link_id})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    return DataResponse(
        success=True,
        message="取得聊天連結資料成功",
        data=chat_link,
    )

# 取得單一聊天連結 (使用者)
@router.get("/{chat_link_id}", response_model=DataResponse[ChatLinkSchema])
def get_chat_link(
    chat_link_id: int,
    request: Request,
    current_user: User = Depends(check_user_can_use_chat_links),
    db: Session = Depends(get_db)
):
    """
    取得單一聊天連結 (使用者)
    
    Args:
        chat_link_id: 聊天連結 ID
        request: 請求物件
        current_user: 目前使用者 (需有使用聊天連結權限)
        db: 資料庫 session
        
    Returns:
        DataResponse[ChatLinkSchema]: 聊天連結資料
        
    Raises:
        HTTPException: 聊天連結不存在或無權限
    """
    # 取得使用者所屬群組的 ID 列表
    group_ids = [group.id for group in current_user.groups]
    
    # 查詢聊天連結
    chat_link = db.query(ChatLink).filter(
        ChatLink.id == chat_link_id
    ).join(
        ChatLink.groups
    ).filter(
        Group.id.in_(group_ids)
    ).first()
    
    # 檢查聊天連結是否存在且使用者有權限
    if not chat_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"聊天連結不存在或無權限 (ID: {chat_link_id})",
        )
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="GET_CHAT_LINK",
        details=f"取得聊天連結資料 (ID: {chat_link_id})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    return DataResponse(
        success=True,
        message="取得聊天連結資料成功",
        data=chat_link,
    )

# 建立聊天連結
@router.post("/", response_model=DataResponse[ChatLinkSchema])
def create_chat_link(
    chat_link_data: ChatLinkCreate,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    建立聊天連結
    
    Args:
        chat_link_data: 聊天連結資料
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        DataResponse[ChatLinkSchema]: 聊天連結資料
        
    Raises:
        HTTPException: 參數錯誤
    """
    # 檢查連結類型
    if chat_link_data.link_type not in ["hosted", "embedded"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"連結類型錯誤 (應為 'hosted' 或 'embedded')",
        )
    
    # 檢查連結類型對應的欄位
    if chat_link_data.link_type == "hosted" and not chat_link_data.url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hosted Chat 類型必須提供 url",
        )
    
    if chat_link_data.link_type == "embedded" and not chat_link_data.embed_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Embedded Chat 類型必須提供 embed_code",
        )
    
    # 建立聊天連結
    chat_link = ChatLink(
        name=chat_link_data.name,
        url=chat_link_data.url,
        embed_code=chat_link_data.embed_code,
        link_type=chat_link_data.link_type,
        description=chat_link_data.description,
    )
    
    # 加入群組
    if chat_link_data.group_ids:
        groups = db.query(Group).filter(Group.id.in_(chat_link_data.group_ids)).all()
        chat_link.groups = groups
    
    # 儲存聊天連結
    db.add(chat_link)
    db.commit()
    db.refresh(chat_link)
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="CREATE_CHAT_LINK",
        details=f"建立聊天連結 (ID: {chat_link.id}, 名稱: {chat_link.name})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    logger.info(f"建立聊天連結成功: {chat_link.name} (ID: {chat_link.id})")
    
    return DataResponse(
        success=True,
        message="建立聊天連結成功",
        data=chat_link,
    )

# 更新聊天連結
@router.put("/{chat_link_id}", response_model=DataResponse[ChatLinkSchema])
def update_chat_link(
    chat_link_id: int,
    chat_link_data: ChatLinkUpdate,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新聊天連結
    
    Args:
        chat_link_id: 聊天連結 ID
        chat_link_data: 聊天連結資料
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        DataResponse[ChatLinkSchema]: 聊天連結資料
        
    Raises:
        HTTPException: 聊天連結不存在或參數錯誤
    """
    # 查詢聊天連結
    chat_link = db.query(ChatLink).filter(ChatLink.id == chat_link_id).first()
    
    # 檢查聊天連結是否存在
    if not chat_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"聊天連結不存在 (ID: {chat_link_id})",
        )
    
    # 檢查連結類型
    if chat_link_data.link_type is not None and chat_link_data.link_type not in ["hosted", "embedded"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"連結類型錯誤 (應為 'hosted' 或 'embedded')",
        )
    
    # 更新聊天連結資料
    if chat_link_data.name is not None:
        chat_link.name = chat_link_data.name
    if chat_link_data.url is not None:
        chat_link.url = chat_link_data.url
    if chat_link_data.embed_code is not None:
        chat_link.embed_code = chat_link_data.embed_code
    if chat_link_data.link_type is not None:
        chat_link.link_type = chat_link_data.link_type
    if chat_link_data.description is not None:
        chat_link.description = chat_link_data.description
    
    # 更新群組
    if chat_link_data.group_ids is not None:
        groups = db.query(Group).filter(Group.id.in_(chat_link_data.group_ids)).all()
        chat_link.groups = groups
    
    # 儲存聊天連結
    db.commit()
    db.refresh(chat_link)
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="UPDATE_CHAT_LINK",
        details=f"更新聊天連結 (ID: {chat_link.id}, 名稱: {chat_link.name})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    logger.info(f"更新聊天連結成功: {chat_link.name} (ID: {chat_link.id})")
    
    return DataResponse(
        success=True,
        message="更新聊天連結成功",
        data=chat_link,
    )

# 刪除聊天連結
@router.delete("/{chat_link_id}", response_model=ResponseBase)
def delete_chat_link(
    chat_link_id: int,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    刪除聊天連結
    
    Args:
        chat_link_id: 聊天連結 ID
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        ResponseBase: 刪除成功回應
        
    Raises:
        HTTPException: 聊天連結不存在
    """
    # 查詢聊天連結
    chat_link = db.query(ChatLink).filter(ChatLink.id == chat_link_id).first()
    
    # 檢查聊天連結是否存在
    if not chat_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"聊天連結不存在 (ID: {chat_link_id})",
        )
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="DELETE_CHAT_LINK",
        details=f"刪除聊天連結 (ID: {chat_link.id}, 名稱: {chat_link.name})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    # 刪除聊天連結
    db.delete(chat_link)
    db.commit()
    
    logger.info(f"刪除聊天連結成功: {chat_link.name} (ID: {chat_link.id})")
    
    return ResponseBase(
        success=True,
        message="刪除聊天連結成功",
    )
