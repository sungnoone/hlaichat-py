from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

from app.core.config import settings

# 建立 SQLAlchemy 引擎
engine = create_engine(str(settings.DATABASE_URL))

# 建立 SessionLocal 類別
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 建立 Base 類別
Base = declarative_base()

# 取得資料庫 session
def get_db() -> Generator:
    """
    取得資料庫 session
    
    Yields:
        Generator: 資料庫 session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化資料庫
def init_db() -> None:
    """
    初始化資料庫
    """
    # 匯入模型以確保它們已註冊
    from app.db import models
    
    # 建立資料表
    Base.metadata.create_all(bind=engine)
