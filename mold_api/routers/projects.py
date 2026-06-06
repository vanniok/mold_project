# Z:\mold_api\routers\projects.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import date
from services.project_service import (
    get_all_projects,
    get_project_by_id,
    create_project,
    save_project_info,
    delete_project as delete_project_service
)

router = APIRouter(prefix="/projects", tags=["projects"])

# ---------- 请求体模型 ----------
class CreateProjectRequest(BaseModel):
    name: str
    customer: str
    template_version: str = "标准版"
    start_date: date

class UpdateProjectRequest(BaseModel):
    name: Optional[str] = None
    customer: Optional[str] = None

class StartDateUpdate(BaseModel):
    start_date: date

# ---------- 路由 ----------
@router.get("")
def list_projects():
    """获取所有项目（含开始日期）"""
    projects = get_all_projects()
    return [
        {
            "id": p.id,
            "name": p.name,
            "customer": p.customer,
            "start_date": p.start_date.isoformat() if p.start_date else None
        }
        for p in projects
    ]

@router.get("/{project_id}")
def get_project(project_id: int):
    proj = get_project_by_id(project_id)
    if not proj:
        return {"error": "项目不存在"}
    return {
        "id": proj.id,
        "name": proj.name,
        "customer": proj.customer,
        "start_date": proj.start_date.isoformat() if proj.start_date else None,
        "template_version": proj.template_version
    }

@router.post("")
def create_project_route(req: CreateProjectRequest):
    try:
        project_id = create_project(req.name, req.customer, req.template_version, req.start_date)
        return {"id": project_id, "message": "项目创建成功"}
    except Exception as e:
        return {"error": str(e)}

@router.put("/{project_id}")
def update_project_route(project_id: int, req: UpdateProjectRequest):
    success = save_project_info(project_id, new_name=req.name, new_customer=req.customer)
    if success:
        return {"message": "更新成功"}
    return {"error": "项目不存在"}

@router.put("/{project_id}/start-date")
def update_start_date(project_id: int, data: StartDateUpdate):
    success = save_project_info(project_id, new_start_date=data.start_date)
    if success:
        return {"message": "开始日期已更新"}
    return {"error": "项目不存在"}

@router.delete("/{project_id}")
def delete_project_route(project_id: int):
    try:
        delete_project_service(project_id)
        return {"message": "删除成功"}
    except Exception as e:
        return {"error": str(e)}