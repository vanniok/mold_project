# -*- coding: utf-8 -*-
from datetime import datetime
from utils.db_conn import SessionLocal
from models.external_task import ExternalTask

def load_external_tasks(project_id):
    db = SessionLocal()
    try:
        tasks = db.query(ExternalTask).filter(ExternalTask.project_id == project_id).all()
        return tasks
    finally:
        db.close()

def save_external_tasks(project_id, tasks_data):
    db = SessionLocal()
    try:
        existing_ids = [t.id for t in db.query(ExternalTask.id).filter(ExternalTask.project_id == project_id).all()]
        new_ids = [t["id"] for t in tasks_data if t["id"] is not None]
        for eid in existing_ids:
            if eid not in new_ids:
                db.query(ExternalTask).filter(ExternalTask.id == eid).delete()
        for t in tasks_data:
            if t["id"] is not None:
                task = db.query(ExternalTask).filter(ExternalTask.id == t["id"]).first()
                if task:
                    task.task_name = t["task_name"]
                    task.responsible = t["responsible"]
                    task.progress_percent = t["progress_percent"]
                    task.last_updated = datetime.now()
            else:
                new_task = ExternalTask(
                    project_id=project_id,
                    task_name=t["task_name"],
                    responsible=t["responsible"],
                    progress_percent=t["progress_percent"],
                    last_updated=datetime.now()
                )
                db.add(new_task)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()