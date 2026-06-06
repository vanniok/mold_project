from utils.db_conn import SessionLocal
from models.project import Project
from models.node import Node
from models.external_task import ExternalTask
from datetime import datetime, timedelta
from core import SENTINEL_DATE, NODE_ORDER

def create_project(name, customer, template_version, start_date):
    """创建新项目并生成标准节点"""
    db = SessionLocal()
    try:
        existing = db.query(Project).filter(Project.name == name).first()
        if existing:
            raise ValueError(f"项目 '{name}' 已存在")
        project = Project(
            name=name,
            customer=customer,
            template_version=template_version,
            start_date=datetime.combine(start_date, datetime.min.time())
        )
        db.add(project)
        db.flush()
        standard_node_names = [node.value for node in NODE_ORDER]
        for idx, node_name in enumerate(standard_node_names):
            node = Node(
                project_id=project.id,
                node_name=node_name,
                planned_start=SENTINEL_DATE,
                planned_end=SENTINEL_DATE,
                status="pending",
                display_order=idx+1,
                progress_percent=0
            )
            db.add(node)
        db.commit()
        return project.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_all_projects():
    db = SessionLocal()
    try:
        projects = db.query(Project).order_by(Project.created_at.desc()).all()
        return projects
    finally:
        db.close()

def get_project_by_id(project_id):
    db = SessionLocal()
    try:
        return db.query(Project).filter(Project.id == project_id).first()
    finally:
        db.close()

def save_project_info(project_id, new_name=None, new_customer=None, new_start_date=None):
    db = SessionLocal()
    try:
        proj = db.query(Project).filter(Project.id == project_id).first()
        if proj:
            if new_name is not None:
                proj.name = new_name
            if new_customer is not None:
                proj.customer = new_customer
            if new_start_date is not None:
                proj.start_date = datetime.combine(new_start_date, datetime.min.time())
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def delete_project(project_id):
    db = SessionLocal()
    try:
        db.query(ExternalTask).filter(ExternalTask.project_id == project_id).delete()
        db.query(Node).filter(Node.project_id == project_id).delete()
        db.query(Project).filter(Project.id == project_id).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()