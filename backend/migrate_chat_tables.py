"""
聊天表格遷移腳本
專門用於建立聊天會話和訊息相關的表格
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.database import engine

def create_chat_tables():
    """
    建立聊天相關的表格
    """
    print("開始建立聊天相關表格...")
    
    try:
        with engine.begin() as connection:
            # 檢查並建立 chat_sessions 表
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
                """))
                connection.execute(text("""
                    CREATE INDEX ix_chat_sessions_session_id ON chat_sessions (session_id);
                """))
                connection.execute(text("""
                    CREATE INDEX ix_chat_sessions_user_id ON chat_sessions (user_id);
                """))
                print("chat_sessions 表建立完成")
            else:
                print("chat_sessions 表已存在")
            
            # 檢查並建立 chat_messages 表
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
                """))
                connection.execute(text("""
                    CREATE INDEX ix_chat_messages_session_id ON chat_messages (session_id);
                """))
                connection.execute(text("""
                    CREATE INDEX ix_chat_messages_sequence ON chat_messages (sequence);
                """))
                print("chat_messages 表建立完成")
            else:
                print("chat_messages 表已存在")
            
            print("聊天表格遷移完成！")
            
    except Exception as e:
        print(f"聊天表格遷移失敗: {e}")
        raise

if __name__ == "__main__":
    create_chat_tables() 