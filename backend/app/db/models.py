from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base
from app.core.config import settings

# 使用者與群組的多對多關聯表
user_group = Table(
    "user_group",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True),
)

# 群組與聊天連結的多對多關聯表
group_chat_link = Table(
    "group_chat_link",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True),
    Column("chat_link_id", Integer, ForeignKey("chat_links.id"), primary_key=True),
)

class User(Base):
    """
    使用者模型
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # 明文密碼
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    department = Column(String, nullable=True)
    email = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=settings.get_taipei_now)
    is_ad_user = Column(Boolean, default=False)
    ad_guid = Column(String, nullable=True)
    
    # 關聯
    groups = relationship("Group", secondary=user_group, back_populates="users")
    logs = relationship("OperationLog", back_populates="user")

class Group(Base):
    """
    群組模型
    """
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    can_login = Column(Boolean, default=True)
    can_manage_platform = Column(Boolean, default=False)
    can_use_chat_links = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=settings.get_taipei_now)
    
    # 關聯
    users = relationship("User", secondary=user_group, back_populates="groups")
    chat_links = relationship("ChatLink", secondary=group_chat_link, back_populates="groups")

class ChatLink(Base):
    """
    聊天連結模型
    """
    __tablename__ = "chat_links"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=True)  # Hosted Chat 網址
    embed_code = Column(Text, nullable=True)  # Embedded Chat 嵌入代碼
    link_type = Column(String, nullable=False)  # 'hosted' 或 'embedded'
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=settings.get_taipei_now)
    
    # 關聯
    groups = relationship("Group", secondary=group_chat_link, back_populates="chat_links")

class OperationLog(Base):
    """
    操作紀錄模型
    """
    __tablename__ = "operation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)  # 例如: LOGIN, CREATE_USER
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=settings.get_taipei_now)
    ip_address = Column(String, nullable=True)
    
    # 關聯
    user = relationship("User", back_populates="logs")

class ADConfig(Base):
    """
    AD 設定模型
    """
    __tablename__ = "ad_config"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_name = Column(String, nullable=True)
    primary_dc = Column(String, nullable=True)
    secondary_dcs = Column(String, nullable=True)  # 逗號分隔
    bind_username = Column(String, nullable=True)
    bind_password = Column(String, nullable=True)  # 明文密碼
    last_updated = Column(DateTime(timezone=True), default=settings.get_taipei_now, onupdate=settings.get_taipei_now)
