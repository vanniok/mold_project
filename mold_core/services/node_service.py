# -*- coding: utf-8 -*-
from utils.db_conn import SessionLocal
from models.node import Node
from datetime import datetime, timedelta
from core import SENTINEL_DATE, OVERDUE_THRESHOLD_DAYS

def move_node_up(project_id, node_id):
    db = SessionLocal()
    try:
        node = db.query(Node).filter(Node.id == node_id, Node.project_id == project_id).first()
        if not node:
            return False
        prev = db.query(Node).filter(Node.project_id == project_id, Node.display_order < node.display_order).order_by(Node.display_order.desc()).first()
        if prev:
            prev.display_order, node.display_order = node.display_order, prev.display_order
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_nodes_for_project(project_id):
    db = SessionLocal()
    try:
        nodes = db.query(Node).filter(Node.project_id == project_id).order_by(Node.display_order).all()
        return nodes
    finally:
        db.close()

def auto_calc_progress(node):
    if node.actual_end:
        return 100
    elif node.actual_start and node.planned_start and node.planned_end:
        if node.planned_start == SENTINEL_DATE or node.planned_end == SENTINEL_DATE:
            return 0
        total_planned = (node.planned_end - node.planned_start).days
        if total_planned <= 0:
            return 0
        today = datetime.now().date()
        actual_start_date = node.actual_start.date()
        days_passed = max(0, (today - actual_start_date).days)
        progress = int(days_passed / total_planned * 100)
        return min(progress, 100)
    else:
        return 0

def calc_progress_time(node):
    if node.actual_end and node.actual_start:
        return (node.actual_end - node.actual_start).days
    elif node.actual_start and not node.actual_end:
        today = datetime.now().date()
        actual_start_date = node.actual_start.date()
        days_passed = (today - actual_start_date).days
        return max(days_passed, 0)
    else:
        return 0

def calc_theory_date(node):
    return datetime.now().date()

def update_node_from_edited_row(node, row):
    node.node_name = row["节点"]
    if row["计划开始"] is None:
        node.planned_start = SENTINEL_DATE
    else:
        node.planned_start = datetime.combine(row["计划开始"], datetime.min.time())
    if row["计划结束"] is None:
        node.planned_end = SENTINEL_DATE
    else:
        node.planned_end = datetime.combine(row["计划结束"], datetime.min.time())
    node.actual_start = datetime.combine(row["实际开始"], datetime.min.time()) if row["实际开始"] else None
    if row["实际结束"]:
        node.actual_end = datetime.combine(row["实际结束"], datetime.min.time())
    else:
        node.actual_end = None
    node.responsible_person = row["责任人"] if row["责任人"] else None
    return node

def recompute_node_status(node):
    today = datetime.now().date()
    planned_end_date = node.planned_end.date() if node.planned_end and node.planned_end != SENTINEL_DATE else None

    if node.actual_end:
        node.status = "done"
        node.progress_percent = 100
    elif node.actual_start:
        if planned_end_date and today > planned_end_date:
            days_overdue = (today - planned_end_date).days
            if days_overdue > OVERDUE_THRESHOLD_DAYS:
                node.status = "overdue"
            else:
                node.status = "delayed"
        else:
            node.status = "doing"
        if node.progress_percent is None or node.progress_percent == 0:
            node.progress_percent = auto_calc_progress(node)
    else:
        node.status = "pending"
        if node.progress_percent is None:
            node.progress_percent = 0
    if node.progress_percent is not None:
        node.progress_percent = max(0, min(100, node.progress_percent))
    return node

def recalc_planned_dates_from_node(start_node, nodes):
    try:
        idx = nodes.index(start_node)
    except ValueError:
        return
    for i in range(idx+1, len(nodes)):
        prev = nodes[i-1]
        curr = nodes[i]
        if prev.planned_end and prev.planned_end != SENTINEL_DATE:
            if curr.planned_start != SENTINEL_DATE and curr.planned_end != SENTINEL_DATE:
                duration = (curr.planned_end - curr.planned_start).days
            else:
                duration = 1
            if duration <= 0:
                duration = 1
            curr.planned_start = prev.planned_end
            curr.planned_end = curr.planned_start + timedelta(days=duration)

def move_node_down(project_id, node_id):
    db = SessionLocal()
    try:
        node = db.query(Node).filter(Node.id == node_id, Node.project_id == project_id).first()
        if not node:
            return False
        nxt = db.query(Node).filter(Node.project_id == project_id, Node.display_order > node.display_order).order_by(Node.display_order.asc()).first()
        if nxt:
            nxt.display_order, node.display_order = node.display_order, nxt.display_order
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def delete_custom_node(project_id, node_id):
    db = SessionLocal()
    try:
        node = db.query(Node).filter(Node.id == node_id, Node.project_id == project_id).first()
        if not node:
            return False
        from core import NODE_ORDER
        standard_names = {n.value for n in NODE_ORDER}
        if node.node_name in standard_names:
            raise ValueError(f"标准节点 '{node.node_name}' 不可删除")
        db.delete(node)
        remaining = db.query(Node).filter(Node.project_id == project_id).order_by(Node.display_order).all()
        for i, rn in enumerate(remaining):
            rn.display_order = i + 1
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def add_custom_node(project_id, prev_node_id, node_name, planned_days, responsible):
    db = SessionLocal()
    try:
        from models.project import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("项目不存在")
        nodes = db.query(Node).filter(Node.project_id == project_id).order_by(Node.display_order).all()
        if prev_node_id is None:
            target_order = 1
            prev_node = None
        else:
            prev_node = db.query(Node).filter(Node.id == prev_node_id, Node.project_id == project_id).first()
            if not prev_node:
                raise ValueError("前一个节点不存在")
            target_order = prev_node.display_order + 1
        if prev_node and prev_node.planned_end and prev_node.planned_end != SENTINEL_DATE:
            start = prev_node.planned_end
        else:
            start = project.start_date
        end = start + timedelta(days=planned_days)
        new_node = Node(
            project_id=project_id,
            node_name=node_name,
            planned_start=start,
            planned_end=end,
            status="pending",
            responsible_person=responsible,
            display_order=target_order,
            progress_percent=0
        )
        db.add(new_node)
        db.flush()
        later_nodes = db.query(Node).filter(Node.project_id == project_id, Node.display_order >= target_order, Node.id != new_node.id).order_by(Node.display_order).all()
        for ln in later_nodes:
            ln.display_order += 1
        db.commit()
        return new_node.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def start_node(node_id):
    db = SessionLocal()
    try:
        node = db.query(Node).filter(Node.id == node_id).first()
        if not node:
            return False
        if node.actual_start is None:
            node.actual_start = datetime.now()
            node.status = "doing"
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()