from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import ValidationError

from app.core.config import settings
from app.db.database import get_db
from app.db.models import User
from app.schemas.user_schemas import UserInDB

# 簡單的 OAuth2 密碼流程
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 建立 JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    建立 JWT token
    
    Args:
        data: 要編碼的資料
        expires_delta: token 有效期限
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = settings.get_taipei_now() + expires_delta
    else:
        expire = settings.get_taipei_now() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

# 驗證 JWT token
def verify_token(token: str) -> Optional[dict]:
    """
    驗證 JWT token
    
    Args:
        token: JWT token
        
    Returns:
        Optional[dict]: 包含使用者名稱的字典，如果驗證失敗則為 None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            return None
        # 注意：這裡只是為了驗證 token，不需要完整的 UserInDB 對象
        # 只需要返回包含 username 的對象即可
        # 在 get_current_user 中會從數據庫獲取完整的用戶信息
        token_data = {"username": username}
        return token_data
    except (JWTError, ValidationError):
        return None

# 取得目前使用者
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    取得目前使用者
    
    Args:
        db: 資料庫 session
        token: JWT token
        
    Returns:
        User: 使用者資料
        
    Raises:
        HTTPException: 認證失敗
    """
    user_data = verify_token(token)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認證失敗",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.username == user_data["username"]).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者已停用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# 檢查使用者是否為管理者
def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    檢查使用者是否為管理者
    
    Args:
        current_user: 目前使用者
        
    Returns:
        User: 使用者資料
        
    Raises:
        HTTPException: 權限不足
    """
    # 檢查使用者是否屬於 admins 群組或具有管理平台權限
    for group in current_user.groups:
        if group.name == "admins" or group.can_manage_platform:
            return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="權限不足",
    )
