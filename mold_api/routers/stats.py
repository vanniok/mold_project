from fastapi import APIRouter
from utils.db_conn import SessionLocal
from models.node import Node
from models.project import Project
from core import SENTINEL_DATE
from rules.compression_rules import WARNING_DAYS   # 修正导入
from datetime import datetime, date, timedelta

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/overview")
def get_overview():
    db = SessionLocal()
    try:
        total_projects = db.query(Project).count()
        delayed_count = db.query(Node).filter(Node.status == 'delayed').count()
        today = date.today()
        # 计算即将到期的节点：计划结束日期在 [today, today + WARNING_DAYS] 且未完成
        warning_count = db.query(Node).filter(
            Node.status != 'done',
            Node.planned_end != SENTINEL_DATE,
            Node.planned_end >= datetime.combine(today, datetime.min.time()),
            Node.planned_end <= datetime.combine(today + timedelta(days=WARNING_DAYS), datetime.min.time())
        ).count()
        return {
            "total_projects": total_projects,
            "delayed_count": delayed_count,
            "warning_count": warning_count
        }
    finally:
        db.close()