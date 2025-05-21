from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import logging
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPBindError, LDAPSocketOpenError

from app.core.security import create_access_token
from app.core.config import settings
from app.db.database import get_db
from app.db.models import User, OperationLog, ADConfig
from app.schemas.user_schemas import Token, UserLogin, ADUserLogin
from app.schemas.common_schemas import ResponseBase
from app.apis.deps import get_current_user

# 設定日誌
logger = logging.getLogger(__name__)

# 建立路由
router = APIRouter()

# 登入
@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    使用者登入
    
    Args:
        request: 請求物件
        form_data: 登入表單資料
        db: 資料庫 session
        
    Returns:
        Token: 登入成功回應
        
    Raises:
        HTTPException: 登入失敗
    """
    # 查詢使用者
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # 驗證使用者
    if not user or user.password != form_data.password:  # 明文密碼比對
        logger.warning(f"登入失敗: 使用者名稱或密碼錯誤 (使用者名稱: {form_data.username})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者名稱或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 檢查使用者是否啟用
    if not user.is_active:
        logger.warning(f"登入失敗: 使用者已停用 (使用者名稱: {form_data.username})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者已停用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 檢查使用者是否有登入權限
    has_login_permission = False
    for group in user.groups:
        if group.can_login:
            has_login_permission = True
            break
    
    if not has_login_permission:
        logger.warning(f"登入失敗: 使用者無登入權限 (使用者名稱: {form_data.username})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="使用者無登入權限",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 建立 JWT token
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    
    # 記錄登入操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=user.id,
        action="LOGIN",
        details=f"使用者登入 (IP: {client_ip})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    logger.info(f"登入成功: {user.username} (ID: {user.id})")
    
    # 回傳 token
    # 將 SQLAlchemy 模型轉換為 Pydantic 模型
    from app.schemas.user_schemas import User as UserSchema
    user_schema = UserSchema.from_orm(user)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_schema,
    )

# AD 登入
@router.post("/ad-login", response_model=Token)
def ad_login(
    request: Request,
    form_data: ADUserLogin,
    db: Session = Depends(get_db)
):
    """
    AD 使用者登入
    
    Args:
        request: 請求物件
        form_data: 登入表單資料
        db: 資料庫 session
        
    Returns:
        Token: 登入成功回應
        
    Raises:
        HTTPException: 登入失敗
    """
    # 查詢 AD 設定
    ad_config = db.query(ADConfig).first()
    
    # 檢查 AD 設定是否存在及完整
    if not ad_config or not ad_config.domain_name or not ad_config.primary_dc:
        logger.warning(f"AD登入失敗: AD 設定不完整 (使用者名稱: {form_data.username})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AD 設定不完整，請聯絡系統管理員",
        )
    
    try:
        # 嘗試使用 AD 帳號密碼連線
        server = Server(ad_config.primary_dc, get_info=ALL)
        bind_user = f"{form_data.username}@{ad_config.domain_name}"
        
        # 嘗試驗證 AD 使用者
        conn = Connection(
            server,
            user=bind_user,
            password=form_data.password,
            auto_bind=True
        )
        
        # AD 驗證成功，取得使用者資訊
        conn.search(
            search_base=f"dc={ad_config.domain_name.replace('.', ',dc=')}",
            search_filter=f"(&(objectClass=user)(objectCategory=person)(sAMAccountName={form_data.username}))",
            attributes=["sAMAccountName", "cn", "mail", "department"]
        )
        
        if not conn.entries:
            logger.warning(f"AD登入失敗: 找不到使用者資訊 (使用者名稱: {form_data.username})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="AD 登入失敗: 找不到使用者資訊",
            )
        
        ad_user_info = conn.entries[0]
        full_name = str(ad_user_info.cn) if hasattr(ad_user_info, 'cn') else form_data.username
        email = str(ad_user_info.mail) if hasattr(ad_user_info, 'mail') else None
        department = str(ad_user_info.department) if hasattr(ad_user_info, 'department') else None
        
        # 關閉連線
        conn.unbind()
        
        # 檢查平台上是否已有此使用者
        user = db.query(User).filter(User.username == form_data.username).first()
        
        # 如果使用者不存在，則建立一個新的使用者
        if not user:
            # 使用者存在但無群組，表示可能是第一次登入或尚未被管理員配置群組
            logger.warning(f"AD登入失敗: 使用者尚未被配置到平台群組 (使用者名稱: {form_data.username})")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您的帳號尚未被配置權限，請聯絡系統管理員",
            )
        
        # 檢查使用者是否啟用
        if not user.is_active:
            logger.warning(f"登入失敗: 使用者已停用 (使用者名稱: {form_data.username})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="使用者已停用",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 檢查使用者是否有登入權限
        has_login_permission = False
        for group in user.groups:
            if group.can_login:
                has_login_permission = True
                break
        
        if not has_login_permission:
            logger.warning(f"登入失敗: 使用者無登入權限 (使用者名稱: {form_data.username})")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="使用者無登入權限",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 更新使用者資訊
        user.full_name = full_name
        user.email = email or user.email
        user.department = department or user.department
        user.is_ad_user = True
        db.commit()
        
        # 建立 JWT token
        access_token_expires = timedelta(minutes=60)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires,
        )
        
        # 記錄登入操作
        client_ip = request.client.host if request.client else None
        log = OperationLog(
            user_id=user.id,
            action="AD_LOGIN",
            details=f"AD 使用者登入 (IP: {client_ip})",
            ip_address=client_ip,
        )
        db.add(log)
        db.commit()
        
        logger.info(f"AD登入成功: {user.username} (ID: {user.id})")
        
        # 回傳 token
        # 將 SQLAlchemy 模型轉換為 Pydantic 模型
        from app.schemas.user_schemas import User as UserSchema
        user_schema = UserSchema.from_orm(user)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_schema,
        )
    except LDAPBindError:
        logger.warning(f"AD登入失敗: 帳號或密碼錯誤 (使用者名稱: {form_data.username})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="AD 登入失敗: 帳號或密碼錯誤",
        )
    except LDAPSocketOpenError:
        logger.warning(f"AD登入失敗: 無法連線到 AD 伺服器 (使用者名稱: {form_data.username})")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AD 登入失敗: 無法連線到 AD 伺服器",
        )
    except Exception as e:
        logger.error(f"AD登入失敗: {str(e)} (使用者名稱: {form_data.username})")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AD 登入失敗: {str(e)}",
        )

# 登出
@router.post("/logout", response_model=ResponseBase)
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    使用者登出
    
    Args:
        request: 請求物件
        current_user: 目前使用者
        db: 資料庫 session
        
    Returns:
        ResponseBase: 登出成功回應
    """
    # 記錄登出操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="LOGOUT",
        details=f"使用者登出 (IP: {client_ip})",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    logger.info(f"登出成功: {current_user.username} (ID: {current_user.id})")
    
    return ResponseBase(message="登出成功")

# 取得目前使用者資訊
@router.get("/me", response_model=Token)
def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    取得目前使用者資訊
    
    Args:
        current_user: 目前使用者
        
    Returns:
        Token: 使用者資訊
    """
    # 建立 JWT token
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": current_user.username},
        expires_delta=access_token_expires,
    )
    
    # 將 SQLAlchemy 模型轉換為 Pydantic 模型
    from app.schemas.user_schemas import User as UserSchema
    user_schema = UserSchema.from_orm(current_user)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_schema,
    )
