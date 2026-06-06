# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from utils.db_conn import SessionLocal
from utils.logger import get_logger
from models.project import Project
from models.node import Node
from schedule_engine.planner import calculate_schedule
from .excel_reader import read_excel
from .mapper import map_row_to_project

logger = get_logger(__name__)

def import_from_excel(file_path: str) -> int:
    df, _ = read_excel(file_path)
    if len(df) == 0:
        raise ValueError("Excel没有数据行")
    row = df.iloc[0]
    
    project_data = map_row_to_project(row)
    
    db: Session = SessionLocal()
    try:
        existing = db.query(Project).filter(Project.name == project_data["name"]).first()
        if existing:
            raise ValueError(f"项目 '{project_data['name']}' 已存在，请勿重复导入")
        
        project = Project(**project_data)
        db.add(project)
        db.flush()
        
        start_date = project_data["start_date"]
        template = project_data.get("template_version", "标准版")
        nodes_schedule = calculate_schedule(start_date, template)
        
        for order, ns in enumerate(nodes_schedule, start=1):
            node = Node(
                project_id=project.id,
                node_name=ns["node_name"],
                planned_start=ns["planned_start"],
                planned_end=ns["planned_end"],
                status="pending",
                display_order=order
            )
            db.add(node)
        
        db.commit()
        logger.info(f"成功导入项目: {project.name} (ID={project.id})")
        return project.id
    except Exception as e:
        db.rollback()
        logger.error(f"导入失败: {str(e)}")
        raise
    finally:
        db.close()