from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.db_conn import SessionLocal
from models.external_task import ExternalTask
from services.external_task_service import load_external_tasks, save_external_tasks
import os
import shutil
from datetime import datetime
import uuid
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/external-tasks", tags=["external_tasks"])

# 获取项目的外协任务列表
@router.get("/{project_id}")
def get_tasks(project_id: int):
    db = SessionLocal()
    try:
        tasks = load_external_tasks(project_id)
        return [
            {
                "id": t.id,
                "task_name": t.task_name,
                "responsible": t.responsible,
                "progress_percent": t.progress_percent,
                "last_updated": t.last_updated.isoformat() if t.last_updated else None,
                "proof_image_path": t.proof_image_path,
            }
            for t in tasks
        ]
    finally:
        db.close()

# 保存外协任务列表（全量替换）
class TaskItem(BaseModel):
    id: Optional[int] = None
    task_name: str
    responsible: Optional[str] = None
    progress_percent: int = 0

@router.post("/{project_id}/save")
def save_tasks(project_id: int, tasks_data: List[TaskItem]):
    tasks_dict = [t.dict() for t in tasks_data]
    save_external_tasks(project_id, tasks_dict)
    return {"message": "保存成功"}

# 获取单个任务详情（新增）
@router.get("/task/{task_id}")
def get_task(task_id: int):
    db = SessionLocal()
    try:
        task = db.query(ExternalTask).filter(ExternalTask.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        return {
            "id": task.id,
            "task_name": task.task_name,
            "responsible": task.responsible,
            "progress_percent": task.progress_percent,
            "proof_image_path": task.proof_image_path,
        }
    finally:
        db.close()

# 更新任务进度（新增）
class ProgressUpdate(BaseModel):
    progress_percent: int

@router.put("/{task_id}/progress")
def update_progress(task_id: int, data: ProgressUpdate):
    db = SessionLocal()
    try:
        task = db.query(ExternalTask).filter(ExternalTask.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        task.progress_percent = data.progress_percent
        task.last_updated = datetime.now()
        db.commit()
        return {"message": "进度已更新"}
    finally:
        db.close()

# 上传图片凭证（原有）
@router.post("/{task_id}/upload-image")
async def upload_image(task_id: int, file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件")
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    ext = file.filename.split(".")[-1]
    new_filename = f"task_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"
    file_path = os.path.join(upload_dir, new_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    db = SessionLocal()
    try:
        task = db.query(ExternalTask).filter(ExternalTask.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        task.proof_image_path = file_path
        db.commit()
        return {"image_path": file_path}
    finally:
        db.close()

# 删除图片凭证（原有）
@router.delete("/{task_id}/image")
def delete_image(task_id: int):
    db = SessionLocal()
    try:
        task = db.query(ExternalTask).filter(ExternalTask.id == task_id).first()
        if not task or not task.proof_image_path:
            return {"message": "无图片可删除"}
        if os.path.exists(task.proof_image_path):
            os.remove(task.proof_image_path)
        task.proof_image_path = None
        db.commit()
        return {"message": "图片已删除"}
    finally:
        db.close()