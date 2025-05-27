"""
資料庫遷移腳本
用於更新現有資料庫結構，新增缺少的欄位和表格
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.database import engine, get_db
from app.db.models import Base
from app.core.config import settings

def migrate_database():
    """
    執行資料庫遷移
    """
    print("開始資料庫遷移...")
    
    try:
        with engine.connect() as connection:
            # 設定自動提交模式
            connection = connection.execution_options(autocommit=True)
            # 檢查並新增 credentials 表
            print("檢查 credentials 表...")
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'credentials'
                );
            """))
            
            if not result.scalar():
                print("建立 credentials 表...")
                connection.execute(text("""
                    CREATE TABLE credentials (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR UNIQUE NOT NULL,
                        api_key VARCHAR NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """))
                
                # 建立索引
                connection.execute(text("""
                    CREATE INDEX ix_credentials_id ON credentials (id);
                    CREATE INDEX ix_credentials_name ON credentials (name);
                """))
                print("credentials 表建立完成")
            else:
                print("credentials 表已存在")
            
            # 檢查並新增 chat_links 表的 webhook_url 欄位
            print("檢查 chat_links.webhook_url 欄位...")
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'chat_links' 
                    AND column_name = 'webhook_url'
                );
            """))
            
            if not result.scalar():
                print("新增 chat_links.webhook_url 欄位...")
                connection.execute(text("""
                    ALTER TABLE chat_links 
                    ADD COLUMN webhook_url VARCHAR;
                """))
                print("webhook_url 欄位新增完成")
            else:
                print("webhook_url 欄位已存在")
            
            # 檢查並新增 chat_links 表的 credential_id 欄位
            print("檢查 chat_links.credential_id 欄位...")
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'chat_links' 
                    AND column_name = 'credential_id'
                );
            """))
            
            if not result.scalar():
                print("新增 chat_links.credential_id 欄位...")
                connection.execute(text("""
                    ALTER TABLE chat_links 
                    ADD COLUMN credential_id INTEGER;
                """))
                print("credential_id 欄位新增完成")
            else:
                print("credential_id 欄位已存在")
            
            # 新增外鍵約束（如果不存在）
            print("檢查外鍵約束...")
            try:
                connection.execute(text("""
                    ALTER TABLE chat_links 
                    ADD CONSTRAINT fk_chat_links_credential_id 
                    FOREIGN KEY (credential_id) REFERENCES credentials (id);
                """))
                print("外鍵約束新增完成")
            except Exception as e:
                if "already exists" in str(e):
                    print("外鍵約束已存在")
                else:
                    print(f"新增外鍵約束時發生錯誤: {e}")
            
            # 檢查並新增 chat_sessions 表
            print("檢查 chat_sessions 表...")
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'chat_sessions'
                );
            """))
            
            if not result.scalar():
                print("建立 chat_sessions 表...")
                connection.execute(text("""
                    CREATE TABLE chat_sessions (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR UNIQUE NOT NULL,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        chat_link_id INTEGER NOT NULL REFERENCES chat_links(id),
                        title VARCHAR,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        is_active BOOLEAN DEFAULT TRUE
                    );
                """))
                
                # 建立索引
                connection.execute(text("""
                    CREATE INDEX ix_chat_sessions_id ON chat_sessions (id);
                    CREATE INDEX ix_chat_sessions_session_id ON chat_sessions (session_id);
                    CREATE INDEX ix_chat_sessions_user_id ON chat_sessions (user_id);
                """))
                print("chat_sessions 表建立完成")
            else:
                print("chat_sessions 表已存在")
            
            # 檢查並新增 chat_messages 表
            print("檢查 chat_messages 表...")
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'chat_messages'
                );
            """))
            
            if not result.scalar():
                print("建立 chat_messages 表...")
                connection.execute(text("""
                    CREATE TABLE chat_messages (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
                        sequence INTEGER NOT NULL,
                        message_type VARCHAR NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        webhook_response TEXT,
                        processing_time INTEGER
                    );
                """))
                
                # 建立索引
                connection.execute(text("""
                    CREATE INDEX ix_chat_messages_id ON chat_messages (id);
                    CREATE INDEX ix_chat_messages_session_id ON chat_messages (session_id);
                    CREATE INDEX ix_chat_messages_sequence ON chat_messages (sequence);
                """))
                print("chat_messages 表建立完成")
            else:
                print("chat_messages 表已存在")
            
            print("資料庫遷移完成！")
            
    except Exception as e:
        print(f"資料庫遷移失敗: {e}")
        raise

if __name__ == "__main__":
    migrate_database() 