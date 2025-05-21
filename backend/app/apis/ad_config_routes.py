from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import logging
from ldap3 import Server, Connection, ALL, SUBTREE, ALL_ATTRIBUTES
from ldap3.core.exceptions import LDAPBindError, LDAPSocketOpenError, LDAPExceptionError
from typing import List

from app.db.database import get_db
from app.db.models import ADConfig, User, OperationLog
from app.schemas.ad_config_schemas import ADConfig as ADConfigSchema, ADConfigUpdate, ADConnectionTest, ADUserSearch, ADUser
from app.schemas.common_schemas import ResponseBase, DataResponse
from app.apis.deps import get_current_admin_user

# 設定日誌
logger = logging.getLogger(__name__)

# 建立路由
router = APIRouter()

# 取得 AD 設定狀態
@router.get("/status", response_model=DataResponse)
def get_ad_config_status(db: Session = Depends(get_db)):
    """
    取得 AD 設定狀態
    
    Args:
        db: 資料庫 session
        
    Returns:
        DataResponse: AD 設定狀態
    """
    # 查詢 AD 設定
    ad_config = db.query(ADConfig).first()
    
    # 檢查設定是否完整
    configured = (
        ad_config is not None and
        ad_config.domain_name and
        ad_config.primary_dc and
        ad_config.bind_username and
        ad_config.bind_password
    )
    
    return DataResponse(
        success=True,
        message="取得 AD 設定狀態成功",
        data={"configured": configured}
    )

# 取得 AD 設定
@router.get("/", response_model=DataResponse[ADConfigSchema])
def get_ad_config(
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取得 AD 設定
    
    Args:
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        DataResponse[ADConfigSchema]: AD 設定資料
    """
    # 查詢 AD 設定
    ad_config = db.query(ADConfig).first()
    
    # 如果不存在，則建立一個空的設定
    if not ad_config:
        ad_config = ADConfig()
        db.add(ad_config)
        db.commit()
        db.refresh(ad_config)
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="GET_AD_CONFIG",
        details="取得 AD 設定",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    return DataResponse(
        success=True,
        message="取得 AD 設定成功",
        data=ad_config,
    )

# 更新 AD 設定
@router.put("/", response_model=DataResponse[ADConfigSchema])
def update_ad_config(
    ad_config_data: ADConfigUpdate,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新 AD 設定
    
    Args:
        ad_config_data: AD 設定資料
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        DataResponse[ADConfigSchema]: AD 設定資料
    """
    # 查詢 AD 設定
    ad_config = db.query(ADConfig).first()
    
    # 如果不存在，則建立一個新的設定
    if not ad_config:
        ad_config = ADConfig()
        db.add(ad_config)
    
    # 更新 AD 設定資料
    if ad_config_data.domain_name is not None:
        ad_config.domain_name = ad_config_data.domain_name
    if ad_config_data.primary_dc is not None:
        ad_config.primary_dc = ad_config_data.primary_dc
    if ad_config_data.secondary_dcs is not None:
        ad_config.secondary_dcs = ad_config_data.secondary_dcs
    if ad_config_data.bind_username is not None:
        ad_config.bind_username = ad_config_data.bind_username
    if ad_config_data.bind_password is not None:
        ad_config.bind_password = ad_config_data.bind_password
    
    # 儲存 AD 設定
    db.commit()
    db.refresh(ad_config)
    
    # 記錄操作
    client_ip = request.client.host if request.client else None
    log = OperationLog(
        user_id=current_user.id,
        action="UPDATE_AD_CONFIG",
        details="更新 AD 設定",
        ip_address=client_ip,
    )
    db.add(log)
    db.commit()
    
    logger.info(f"更新 AD 設定成功")
    
    return DataResponse(
        success=True,
        message="更新 AD 設定成功",
        data=ad_config,
    )

# 測試 AD 連線
@router.post("/test-connection", response_model=ResponseBase)
def test_ad_connection(
    connection_data: ADConnectionTest,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    測試 AD 連線
    
    Args:
        connection_data: AD 連線資料
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        ResponseBase: 測試結果
    """
    try:
        # 建立 LDAP 伺服器
        server = Server(connection_data.primary_dc, get_info=ALL)
        
        # 建立 LDAP 連線
        bind_user = f"{connection_data.bind_username}@{connection_data.domain_name}"
        conn = Connection(
            server,
            user=bind_user,
            password=connection_data.bind_password,
            auto_bind=True
        )
        
        # 記錄操作
        client_ip = request.client.host if request.client else None
        log = OperationLog(
            user_id=current_user.id,
            action="TEST_AD_CONNECTION",
            details=f"測試 AD 連線 (網域: {connection_data.domain_name}, DC: {connection_data.primary_dc})",
            ip_address=client_ip,
        )
        db.add(log)
        db.commit()
        
        logger.info(f"測試 AD 連線成功 (網域: {connection_data.domain_name}, DC: {connection_data.primary_dc})")
        
        # 關閉連線
        conn.unbind()
        
        return ResponseBase(
            success=True,
            message="AD 連線測試成功",
        )
    except LDAPBindError:
        logger.error(f"測試 AD 連線失敗: 帳號或密碼錯誤 (網域: {connection_data.domain_name}, DC: {connection_data.primary_dc})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AD 連線測試失敗: 帳號或密碼錯誤",
        )
    except LDAPSocketOpenError:
        logger.error(f"測試 AD 連線失敗: 無法連線到伺服器 (網域: {connection_data.domain_name}, DC: {connection_data.primary_dc})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AD 連線測試失敗: 無法連線到伺服器",
        )
    except Exception as e:
        logger.error(f"測試 AD 連線失敗: {str(e)} (網域: {connection_data.domain_name}, DC: {connection_data.primary_dc})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"AD 連線測試失敗: {str(e)}",
        )

# 搜尋 AD 使用者
@router.post("/search-users", response_model=DataResponse[List[ADUser]])
def search_ad_users(
    search_data: ADUserSearch,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    搜尋 AD 使用者
    
    Args:
        search_data: 搜尋資料
        request: 請求物件
        current_user: 目前使用者 (需為管理者)
        db: 資料庫 session
        
    Returns:
        DataResponse[List[ADUser]]: AD 使用者列表
    """
    # 查詢 AD 設定
    ad_config = db.query(ADConfig).first()
    
    # 檢查 AD 設定是否存在
    if not ad_config or not ad_config.domain_name or not ad_config.primary_dc or not ad_config.bind_username or not ad_config.bind_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AD 設定不完整，請先設定 AD 連線資訊",
        )
    
    try:
        # 建立 LDAP 伺服器
        server = Server(ad_config.primary_dc, get_info=ALL)
        
        # 建立 LDAP 連線
        bind_user = f"{ad_config.bind_username}@{ad_config.domain_name}"
        conn = Connection(
            server,
            user=bind_user,
            password=ad_config.bind_password,
            auto_bind=True
        )
        
        # 建立搜尋條件
        search_filter = f"(&(objectClass=user)(objectCategory=person)(|(cn=*{search_data.search_term}*)(sAMAccountName=*{search_data.search_term}*)(mail=*{search_data.search_term}*)))"
        
        # 設定要取得的屬性
        attrs = ["sAMAccountName", "cn", "mail", "department", "objectGUID"]
        
        # 搜尋 AD 使用者
        base_dn = f"dc={ad_config.domain_name.replace('.', ',dc=')}"
        conn.search(
            search_base=base_dn,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=attrs,
            size_limit=search_data.max_results
        )
        
        # 處理搜尋結果
        ad_users = []
        for entry in conn.entries:
            username = entry.sAMAccountName.value if hasattr(entry, 'sAMAccountName') else ""
            full_name = entry.cn.value if hasattr(entry, 'cn') else ""
            email = entry.mail.value if hasattr(entry, 'mail') else None
            department = entry.department.value if hasattr(entry, 'department') else None
            guid = ""
            
            # 安全處理 objectGUID，檢查是否有 hex 方法
            if hasattr(entry, 'objectGUID'):
                guid_value = entry.objectGUID.value
                if hasattr(guid_value, 'hex'):
                    guid = guid_value.hex()
                elif isinstance(guid_value, str):
                    guid = guid_value
            
            ad_users.append(ADUser(
                username=username,
                full_name=full_name,
                email=email,
                department=department,
                guid=guid,
            ))
        
        # 關閉連線
        conn.unbind()
        
        # 記錄操作
        client_ip = request.client.host if request.client else None
        log = OperationLog(
            user_id=current_user.id,
            action="SEARCH_AD_USERS",
            details=f"搜尋 AD 使用者 (關鍵字: {search_data.search_term}, 結果數: {len(ad_users)})",
            ip_address=client_ip,
        )
        db.add(log)
        db.commit()
        
        logger.info(f"搜尋 AD 使用者成功 (關鍵字: {search_data.search_term}, 結果數: {len(ad_users)})")
        
        return DataResponse(
            success=True,
            message="搜尋 AD 使用者成功",
            data=ad_users,
        )
    except LDAPBindError:
        logger.error(f"搜尋 AD 使用者失敗: 帳號或密碼錯誤 (關鍵字: {search_data.search_term})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="搜尋 AD 使用者失敗: 帳號或密碼錯誤",
        )
    except LDAPSocketOpenError:
        logger.error(f"搜尋 AD 使用者失敗: 無法連線到伺服器 (關鍵字: {search_data.search_term})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="搜尋 AD 使用者失敗: 無法連線到伺服器",
        )
    except Exception as e:
        logger.error(f"搜尋 AD 使用者失敗: {str(e)} (關鍵字: {search_data.search_term})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"搜尋 AD 使用者失敗: {str(e)}",
        )
