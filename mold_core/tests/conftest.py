# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'Z:\mold_core')

from services.project_service import get_all_projects
from models.project import Project
from utils.db_conn import SessionLocal

try:
    db = SessionLocal()
    projects = get_all_projects()
    print(f"成功连接到数据库，共找到 {len(projects)} 个项目。")
    for p in projects:
        print(f"项目: {p.name}, 客户: {p.customer}")
except Exception as e:
    print(f"错误: {e}")
finally:
    db.close()