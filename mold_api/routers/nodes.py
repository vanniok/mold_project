from fastapi import APIRouter
from utils.db_conn import SessionLocal
from services.node_service import get_nodes_for_project, move_node_up, move_node_down, delete_custom_node, add_custom_node, recompute_node_status
from models.node import Node
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from core import NODE_ORDER
from utils.datetime_utils import parse_datetime_safe

router = APIRouter(prefix="/projects", tags=["nodes"])

# 获取项目的节点列表
@router.get("/{project_id}/nodes")
def list_nodes(project_id: int):
    db = SessionLocal()
    try:
        nodes = get_nodes_for_project(project_id)
        return [
            {
                "id": n.id,
                "node_name": n.node_name,
                "planned_start": n.planned_start.isoformat() if n.planned_start else None,
                "planned_end": n.planned_end.isoformat() if n.planned_end else None,
                "actual_start": n.actual_start.isoformat() if n.actual_start else None,
                "actual_end": n.actual_end.isoformat() if n.actual_end else None,
                "status": n.status,
                "responsible_person": n.responsible_person,
                "progress_percent": n.progress_percent,
                "display_order": n.display_order
            }
            for n in nodes
        ]
    finally:
        db.close()

# 更新节点
class NodeUpdate(BaseModel):
    node_name: Optional[str] = None
    planned_start: Optional[str] = None
    planned_end: Optional[str] = None
    actual_start: Optional[str] = None
    actual_end: Optional[str] = None
    responsible_person: Optional[str] = None
    progress_percent: Optional[int] = None

@router.put("/nodes/{node_id}")
def update_node(node_id: int, node_update: NodeUpdate):
    db = SessionLocal()
    try:
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            return {"error": "节点不存在"}
        
        # 只处理前端实际传递的字段（使用 exclude_unset）
        update_data = node_update.model_dump(exclude_unset=True)
        
        if "node_name" in update_data:
            node.node_name = update_data["node_name"]
        if "planned_start" in update_data:
            node.planned_start = parse_datetime_safe(update_data["planned_start"])
        if "planned_end" in update_data:
            node.planned_end = parse_datetime_safe(update_data["planned_end"])
        if "actual_start" in update_data:
            # 注意：前端可能传递 null 或空字符串，都视为清空
            actual_start_val = update_data["actual_start"]
            node.actual_start = parse_datetime_safe(actual_start_val) if actual_start_val else None
        if "actual_end" in update_data:
            actual_end_val = update_data["actual_end"]
            node.actual_end = parse_datetime_safe(actual_end_val) if actual_end_val else None
        if "responsible_person" in update_data:
            node.responsible_person = update_data["responsible_person"]
        if "progress_percent" in update_data:
            node.progress_percent = update_data["progress_percent"]
        
        node = recompute_node_status(node)
        db.commit()
        return {"message": "更新成功"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

# 移动节点
@router.post("/nodes/{node_id}/move")
def move_node(node_id: int, direction: str):  # direction: "up" or "down"
    db = SessionLocal()
    try:
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            return {"error": "节点不存在"}
        project_id = node.project_id
        if direction == "up":
            success = move_node_up(project_id, node_id)
        elif direction == "down":
            success = move_node_down(project_id, node_id)
        else:
            return {"error": "无效的方向"}
        if not success:
            return {"error": "移动失败（已在边界）"}
        db.commit()
        return {"message": "移动成功"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

# 删除节点
@router.delete("/nodes/{node_id}")
def delete_node(node_id: int):
    db = SessionLocal()
    try:
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            return {"error": "节点不存在"}
        standard_names = {n.value for n in NODE_ORDER}
        if node.node_name in standard_names:
            return {"error": f"标准节点 '{node.node_name}' 不可删除"}
        db.delete(node)
        remaining = db.query(Node).filter(Node.project_id == node.project_id).order_by(Node.display_order).all()
        for idx, n in enumerate(remaining, start=1):
            n.display_order = idx
        db.commit()
        return {"message": "删除成功"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

# 添加自定义节点
class AddNodeRequest(BaseModel):
    node_name: str
    planned_days: int
    responsible: Optional[str] = None
    prev_node_id: Optional[int] = None

@router.post("/{project_id}/nodes")
def add_node(project_id: int, req: AddNodeRequest):
    db = SessionLocal()
    try:
        new_id = add_custom_node(project_id, req.prev_node_id, req.node_name, req.planned_days, req.responsible)
        if not new_id:
            return {"error": "添加失败"}
        return {"id": new_id, "message": "添加成功"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

# 追加的新接口
from core import SENTINEL_DATE, SCHEDULE_TEMPLATES, DEFAULT_TEMPLATE
from schedule_engine.planner import calculate_schedule
from datetime import date

@router.post("/{project_id}/init-blank")
def init_blank_nodes(project_id: int):
    db = SessionLocal()
    try:
        from models.project import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"error": "项目不存在"}
        template = project.template_version or DEFAULT_TEMPLATE
        start_date = project.start_date
        nodes_schedule = calculate_schedule(start_date, template)
        nodes = db.query(Node).filter(Node.project_id == project_id).all()
        node_map = {n.node_name: n for n in nodes}
        updated_count = 0
        for ns in nodes_schedule:
            node_name = ns["node_name"]
            if node_name in node_map:
                node = node_map[node_name]
                if node.planned_start == SENTINEL_DATE or node.planned_end == SENTINEL_DATE:
                    node.planned_start = ns["planned_start"]
                    node.planned_end = ns["planned_end"]
                    updated_count += 1
        db.commit()
        return {"updated": updated_count}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

@router.post("/{project_id}/reset-planned")
def reset_planned(project_id: int):
    db = SessionLocal()
    try:
        nodes = db.query(Node).filter(Node.project_id == project_id).all()
        for node in nodes:
            node.planned_start = SENTINEL_DATE
            node.planned_end = SENTINEL_DATE
        db.commit()
        return {"message": "ok"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

@router.post("/{project_id}/reset-actual")
def reset_actual(project_id: int):
    db = SessionLocal()
    try:
        nodes = db.query(Node).filter(Node.project_id == project_id).all()
        for node in nodes:
            node.actual_start = None
            node.actual_end = None
            node.progress_percent = 0
            node.status = "pending"
        db.commit()
        return {"message": "ok"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

@router.post("/{project_id}/complete-overdue")
def complete_overdue(project_id: int):
    db = SessionLocal()
    try:
        today = date.today()
        overdue_nodes = db.query(Node).filter(
            Node.project_id == project_id,
            Node.status != 'done',
            Node.planned_end != SENTINEL_DATE,
            Node.planned_end < datetime.combine(today, datetime.min.time())
        ).all()
        for node in overdue_nodes:
            node.actual_end = datetime.now()
            node.status = "done"
            node.progress_percent = 100
            node.reminder_last = None
            node.reminder_muted = False
        db.commit()
        return {"completed": len(overdue_nodes)}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

# 暂不处理逾期提醒
@router.post("/nodes/{node_id}/remind-snooze")
def remind_snooze(node_id: int):
    db = SessionLocal()
    try:
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            return {"error": "节点不存在"}
        node.reminder_last = datetime.now()
        db.commit()
        return {"message": "已暂不处理，下次提醒将在逾期≥10天且距离上次暂不处理≥10天后"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

# 不再提醒（永久静默）
@router.post("/nodes/{node_id}/remind-mute")
def remind_mute(node_id: int):
    db = SessionLocal()
    try:
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            return {"error": "节点不存在"}
        node.reminder_muted = True
        node.reminder_last = None  # 清除暂不处理记录
        db.commit()
        return {"message": "已不再提醒"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()