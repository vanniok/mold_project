import pytest
import sys
from pathlib import Path
from datetime import date

# 将项目根目录加入 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.db_conn import Base
from services.project_service import create_project, get_all_projects
import utils.db_conn  # 用于 monkeypatch

@pytest.fixture(scope="function")
def test_db_session(monkeypatch):
    # 创建内存引擎
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 临时替换 utils.db_conn.SessionLocal
    monkeypatch.setattr(utils.db_conn, "SessionLocal", TestingSessionLocal)
    
    # 返回一个会话供测试使用（但实际测试中可能不需要直接使用）
    db = TestingSessionLocal()
    yield db
    db.close()

def test_create_and_get_projects(test_db_session):
    # 创建项目
    proj_id = create_project("测试项目", "测试客户", "标准版", date(2026,1,1))
    # 获取所有项目
    projects = get_all_projects()
    assert len(projects) == 1
    assert projects[0].name == "测试项目"