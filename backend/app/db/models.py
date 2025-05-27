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
    webhook_url = Column(String, nullable=True)  # Webhook 網址
    link_type = Column(String, nullable=False)  # 'hosted', 'embedded', 'webhook'
    description = Column(Text, nullable=True)
    credential_id = Column(Integer, ForeignKey("credentials.id"), nullable=True)  # 關聯到憑證
    created_at = Column(DateTime(timezone=True), default=settings.get_taipei_now)
    
    # 關聯
    groups = relationship("Group", secondary=group_chat_link, back_populates="chat_links")
    credential = relationship("Credential", back_populates="chat_links")

class Credential(Base):
    """
    憑證模型 - 管理 API Key
    """
    __tablename__ = "credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)  # 容易記的名稱
    api_key = Column(String, nullable=False)  # API Key (明文儲存)
    description = Column(Text, nullable=True)  # 描述
    created_at = Column(DateTime(timezone=True), default=settings.get_taipei_now)
    updated_at = Column(DateTime(timezone=True), default=settings.get_taipei_now, onupdate=settings.get_taipei_now)
    
    # 關聯
    chat_links = relationship("ChatLink", back_populates="credential")

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

class ChatSession(Base):
    """
    聊天會話模型
    """
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)  # 會話唯一識別碼
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_link_id = Column(Integer, ForeignKey("chat_links.id"), nullable=False)
    title = Column(String, nullable=True)  # 會話標題，可由第一條訊息自動生成
    created_at = Column(DateTime(timezone=True), default=settings.get_taipei_now)
    updated_at = Column(DateTime(timezone=True), default=settings.get_taipei_now, onupdate=settings.get_taipei_now)
    is_active = Column(Boolean, default=True)  # 會話是否活躍
    
    # 關聯
    user = relationship("User")
    chat_link = relationship("ChatLink")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    """
    聊天訊息模型
    """
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.session_id"), nullable=False)
    sequence = Column(Integer, nullable=False)  # 訊息序號，由後端維護
    message_type = Column(String, nullable=False)  # 'user' 或 'assistant'
    content = Column(Text, nullable=False)  # 訊息內容
    timestamp = Column(DateTime(timezone=True), default=settings.get_taipei_now)
    webhook_response = Column(Text, nullable=True)  # 完整的 webhook 回應 (JSON)
    processing_time = Column(Integer, nullable=True)  # 處理時間 (毫秒)
    
    # 關聯
    session = relationship("ChatSession", back_populates="messages")

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
