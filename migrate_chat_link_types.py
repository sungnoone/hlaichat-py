#!/usr/bin/env python3
"""
聊天連結類型遷移腳本
將現有的聊天連結類型從舊格式更新為新格式，以支援未來的 Flowise 整合

舊格式 -> 新格式:
- host_chat -> n8n_host_chat
- embedded_chat -> n8n_embedded_chat  
- webhook -> n8n_webhook

執行方式: python migrate_chat_link_types.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 加入專案路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.config import settings

def migrate_chat_link_types():
    """遷移聊天連結類型"""
    
    # 建立資料庫連線
    database_url = str(settings.DATABASE_URL)
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("開始遷移聊天連結類型...")
        
        # 類型對應表
        type_mapping = {
            'host_chat': 'n8n_host_chat',
            'embedded_chat': 'n8n_embedded_chat',
            'webhook': 'n8n_webhook'
        }
        
        # 查詢需要更新的記錄
        for old_type, new_type in type_mapping.items():
            result = db.execute(
                text("SELECT COUNT(*) FROM chat_links WHERE link_type = :old_type"),
                {"old_type": old_type}
            )
            count = result.scalar()
            
            if count > 0:
                print(f"發現 {count} 個 '{old_type}' 類型的聊天連結，將更新為 '{new_type}'")
                
                # 執行更新
                db.execute(
                    text("UPDATE chat_links SET link_type = :new_type WHERE link_type = :old_type"),
                    {"new_type": new_type, "old_type": old_type}
                )
                
                print(f"已成功更新 {count} 個聊天連結")
            else:
                print(f"沒有發現 '{old_type}' 類型的聊天連結")
        
        # 提交變更
        db.commit()
        print("聊天連結類型遷移完成！")
        
        # 顯示更新後的統計
        print("\n更新後的聊天連結類型統計:")
        result = db.execute(text("SELECT link_type, COUNT(*) FROM chat_links GROUP BY link_type"))
        for row in result:
            print(f"  {row[0]}: {row[1]} 個")
            
    except Exception as e:
        print(f"遷移過程中發生錯誤: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("聊天連結類型遷移腳本")
    print("=" * 50)
    
    success = migrate_chat_link_types()
    
    if success:
        print("\n✅ 遷移成功完成！")
    else:
        print("\n❌ 遷移失敗！")
        sys.exit(1) 