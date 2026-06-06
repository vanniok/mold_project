from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from services.compression_service import prepare_compression_data
from services.node_service import get_nodes_for_project
from utils.db_conn import SessionLocal
from models.project import Project
from models.node import Node

router = APIRouter(prefix="/ai", tags=["ai"])

class CompressRequest(BaseModel):
    project_id: int

@router.post("/compress")
async def ai_compress(req: CompressRequest):
    """
    根据项目当前节点状态，调用 AI 生成压缩建议。
    只针对第一个延期节点（status='delayed'）进行后续节点压缩分析。
    """
    db = SessionLocal()
    try:
        # 获取项目信息
        project = db.query(Project).filter(Project.id == req.project_id).first()
        if not project:
            return {"error": "项目不存在"}
        
        # 获取所有节点
        nodes = get_nodes_for_project(req.project_id)
        if not nodes:
            return {"error": "项目无节点数据"}
        
        # 找到第一个延期节点（status == 'delayed'）
        delayed_node = next((n for n in nodes if n.status == 'delayed'), None)
        if not delayed_node:
            return {"suggestions": [], "message": "暂无延期节点，无需压缩"}
        
        # 调用压缩服务
        suggestions, _ = prepare_compression_data(project.name, delayed_node, nodes)
        if not suggestions:
            return {"suggestions": [], "message": "无法生成压缩建议，请检查后续节点计划时间"}
        
        return {"suggestions": suggestions}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()