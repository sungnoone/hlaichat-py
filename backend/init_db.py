#!/usr/bin/env python3
"""
資料庫初始化腳本
"""

from app.db.database import init_db

if __name__ == "__main__":
    print("正在初始化資料庫...")
    init_db()
    print("資料庫初始化完成！憑證表已建立。") 