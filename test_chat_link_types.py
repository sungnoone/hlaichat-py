#!/usr/bin/env python3
"""
聊天連結類型系統測試腳本
驗證新的類型命名系統是否正常工作

執行方式: python test_chat_link_types.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 加入專案路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.config import settings

def test_chat_link_types():
    """測試聊天連結類型系統"""
    
    # 建立資料庫連線
    database_url = str(settings.DATABASE_URL)
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("開始測試聊天連結類型系統...")
        
        # 檢查現有的聊天連結類型
        print("\n1. 檢查現有聊天連結類型:")
        result = db.execute(text("SELECT id, name, link_type FROM chat_links ORDER BY id"))
        chat_links = result.fetchall()
        
        if not chat_links:
            print("   沒有找到任何聊天連結")
        else:
            for link in chat_links:
                print(f"   ID: {link[0]}, 名稱: {link[1]}, 類型: {link[2]}")
        
        # 檢查類型是否符合新的命名規範
        print("\n2. 檢查類型命名規範:")
        valid_types = ['n8n_host_chat', 'n8n_embedded_chat', 'n8n_webhook', 'flowise_chat']
        invalid_types = []
        
        for link in chat_links:
            if link[2] not in valid_types:
                invalid_types.append((link[0], link[1], link[2]))
        
        if not invalid_types:
            print("   ✅ 所有聊天連結類型都符合新的命名規範")
        else:
            print("   ❌ 發現不符合規範的類型:")
            for link_id, name, link_type in invalid_types:
                print(f"      ID: {link_id}, 名稱: {name}, 類型: {link_type}")
        
        # 檢查各類型的統計
        print("\n3. 類型統計:")
        for valid_type in valid_types:
            result = db.execute(
                text("SELECT COUNT(*) FROM chat_links WHERE link_type = :type"),
                {"type": valid_type}
            )
            count = result.scalar()
            if count > 0:
                print(f"   {valid_type}: {count} 個")
        
        # 檢查是否有 webhook_url 和 credential_id 欄位
        print("\n4. 檢查資料庫結構:")
        try:
            result = db.execute(text("SELECT webhook_url, credential_id FROM chat_links LIMIT 1"))
            print("   ✅ webhook_url 和 credential_id 欄位存在")
        except Exception as e:
            print(f"   ❌ 資料庫結構問題: {e}")
        
        # 測試 API 類型驗證（模擬）
        print("\n5. 測試類型驗證邏輯:")
        test_types = [
            ('n8n_host_chat', True),
            ('n8n_embedded_chat', True),
            ('n8n_webhook', True),
            ('flowise_chat', True),
            ('host_chat', False),  # 舊格式，應該無效
            ('embedded_chat', False),  # 舊格式，應該無效
            ('webhook', False),  # 舊格式，應該無效
            ('invalid_type', False)
        ]
        
        valid_api_types = ["n8n_host_chat", "n8n_embedded_chat", "n8n_webhook"]
        
        for test_type, should_be_valid in test_types:
            is_valid = test_type in valid_api_types
            status = "✅" if is_valid == should_be_valid else "❌"
            expected = "有效" if should_be_valid else "無效"
            actual = "有效" if is_valid else "無效"
            print(f"   {status} {test_type}: 預期 {expected}, 實際 {actual}")
        
        print("\n聊天連結類型系統測試完成！")
        return True
        
    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("聊天連結類型系統測試")
    print("=" * 60)
    
    success = test_chat_link_types()
    
    if success:
        print("\n✅ 測試完成！")
    else:
        print("\n❌ 測試失敗！")
        sys.exit(1) 