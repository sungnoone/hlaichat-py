from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uvicorn
import logging
from typing import List

from app.core.config import settings
from app.core.security import get_current_admin_user
from app.db.database import get_db, init_db
from app.db.models import User, Group, ChatLink, Credential, OperationLog
from app.apis import auth_routes, user_routes, group_routes, chat_link_routes, ad_config_routes, log_routes, credential_routes, chat_routes, user_profile_routes
from app.schemas.common_schemas import ErrorResponse, DataResponse

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 建立 FastAPI 應用程式
app = FastAPI(
    title=settings.APP_NAME,
    description="AI 聊天流程對話網址管理平台",
    version="0.1.0",
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://127.0.0.1:5173", 
        "http://127.0.0.1:3000",
        "http://192.168.1.12:3000",  # 新增 IP 位址存取
        "http://192.168.1.12:5173",  # 新增 IP 位址存取
        "http://acm1.hanlin.com.tw" #生產環境實際主機FQDN
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有方法
    allow_headers=["*"],  # 允許所有標頭
)

# 全域例外處理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全域例外: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            message="伺服器內部錯誤",
            details=str(exc)
        ).dict(),
    )

# 根路由
@app.get("/")
def read_root():
    return {"message": f"歡迎使用 {settings.APP_NAME} API"}

# 健康檢查
@app.get("/health")
def health_check():
    return {"status": "ok"}

# 取得系統統計資料
@app.get("/api/stats", response_model=DataResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    取得系統統計資料 (僅管理者)
    
    Args:
        db: 資料庫 session
        current_user: 目前使用者 (需為管理者)
        
    Returns:
        DataResponse: 統計資料
    """
    try:
        # 查詢使用者數量
        user_count = db.query(User).count()
        
        # 查詢群組數量
        group_count = db.query(Group).count()
        
        # 查詢聊天連結數量
        chat_link_count = db.query(ChatLink).count()
        
        # 查詢憑證數量
        credential_count = db.query(Credential).count()
        
        # 記錄操作
        log = OperationLog(
            user_id=current_user.id,
            action="GET_STATS",
            details="取得系統統計資料",
        )
        db.add(log)
        db.commit()
        
        return DataResponse(
            success=True,
            message="取得統計資料成功",
            data={
                "userCount": user_count,
                "groupCount": group_count,
                "chatLinkCount": chat_link_count,
                "credentialCount": credential_count
            }
        )
    except Exception as e:
        logger.error(f"取得統計資料失敗: {e}", exc_info=True)
        return DataResponse(
            success=False,
            message=f"取得統計資料失敗: {str(e)}",
            data={
                "userCount": 0,
                "groupCount": 0,
                "chatLinkCount": 0,
                "credentialCount": 0
            }
        )

# 註冊 API 路由
app.include_router(auth_routes.router, prefix="/api/auth", tags=["認證"])
app.include_router(user_routes.router, prefix="/api/users", tags=["使用者"])
app.include_router(group_routes.router, prefix="/api/groups", tags=["群組"])
app.include_router(chat_link_routes.router, prefix="/api/chat-links", tags=["聊天連結"])
app.include_router(credential_routes.router, prefix="/api/credentials", tags=["憑證管理"])
app.include_router(ad_config_routes.router, prefix="/api/ad-config", tags=["AD 設定"])
app.include_router(log_routes.router, prefix="/api/logs", tags=["操作紀錄"])
app.include_router(chat_routes.router, prefix="/api", tags=["聊天"])
app.include_router(user_profile_routes.router, prefix="/api/user-profiles", tags=["使用者個人資料"])

# 啟動事件
@app.on_event("startup")
async def startup_event():
    logger.info(f"{settings.APP_NAME} 啟動中...")
    
    # 初始化資料庫
    init_db()
    
    # 建立預設管理者帳號和群組
    db = next(get_db())
    try:
        # 檢查是否已存在 admins 群組
        admin_group = db.query(Group).filter(Group.name == "admins").first()
        if not admin_group:
            admin_group = Group(
                name="admins",
                description="管理者群組",
                can_login=True,
                can_manage_platform=True,
                can_use_chat_links=True,
            )
            db.add(admin_group)
            db.commit()
            db.refresh(admin_group)
            logger.info("已建立 admins 群組")
        
        # 檢查是否已存在 admin 使用者
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                password="admin",  # 明文密碼
                full_name="系統管理員",
                is_active=True,
            )
            admin_user.groups.append(admin_group)
            db.add(admin_user)
            db.commit()
            logger.info("已建立 admin 使用者")
    except Exception as e:
        logger.error(f"建立預設管理者帳號和群組時發生錯誤: {e}", exc_info=True)
    finally:
        db.close()
    
    logger.info(f"{settings.APP_NAME} 已啟動")

# 關閉事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"{settings.APP_NAME} 關閉中...")
    logger.info(f"{settings.APP_NAME} 已關閉")

# 主程式入口點
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
