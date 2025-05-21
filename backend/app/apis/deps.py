from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Generator, Optional

from app.core.security import get_current_user, get_current_admin_user
from app.db.database import get_db
from app.db.models import User

# 重新導出資料庫 session 依賴
get_db_session = get_db

# 重新導出使用者依賴
get_current_user_dependency = get_current_user
get_current_admin_user_dependency = get_current_admin_user

# 取得目前使用者 ID
def get_current_user_id(current_user: User = Depends(get_current_user)) -> int:
    """
    取得目前使用者 ID
    
    Args:
        current_user: 目前使用者
        
    Returns:
        int: 使用者 ID
    """
    return current_user.id

# 檢查使用者是否可以登入
def check_user_can_login(current_user: User = Depends(get_current_user)) -> User:
    """
    檢查使用者是否可以登入
    
    Args:
        current_user: 目前使用者
        
    Returns:
        User: 使用者資料
        
    Raises:
        HTTPException: 權限不足
    """
    # 檢查使用者是否屬於具有登入權限的群組
    for group in current_user.groups:
        if group.can_login:
            return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="使用者無登入權限",
    )

# 檢查使用者是否可以使用聊天連結
def check_user_can_use_chat_links(current_user: User = Depends(get_current_user)) -> User:
    """
    檢查使用者是否可以使用聊天連結
    
    Args:
        current_user: 目前使用者
        
    Returns:
        User: 使用者資料
        
    Raises:
        HTTPException: 權限不足
    """
    # 檢查使用者是否屬於具有使用聊天連結權限的群組
    for group in current_user.groups:
        if group.can_use_chat_links:
            return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="使用者無使用聊天連結權限",
    )
