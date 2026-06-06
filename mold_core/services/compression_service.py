# -*- coding: utf-8 -*-
from utils.ai_compressor import get_compression_suggestions
from core import SENTINEL_DATE
from datetime import datetime

def prepare_compression_data(project_name, delayed_node, nodes):
    """准备压缩所需的数据并调用 AI"""
    if delayed_node.actual_end:
        delay_days = (delayed_node.actual_end.date() - delayed_node.planned_end.date()).days
    else:
        delay_days = (datetime.now().date() - delayed_node.planned_end.date()).days
    subsequent = [n for n in nodes if n.display_order > delayed_node.display_order]
    nodes_info = []
    for n in subsequent:
        planned_days = None
        if n.planned_start and n.planned_start != SENTINEL_DATE and n.planned_end and n.planned_end != SENTINEL_DATE:
            planned_days = (n.planned_end - n.planned_start).days
        nodes_info.append({
            "name": n.node_name,
            "planned_start": n.planned_start.strftime("%Y-%m-%d") if n.planned_start and n.planned_start != SENTINEL_DATE else None,
            "planned_end": n.planned_end.strftime("%Y-%m-%d") if n.planned_end and n.planned_end != SENTINEL_DATE else None,
            "planned_days": planned_days,
            "min_days": 1
        })
    suggestions = get_compression_suggestions(project_name, delayed_node.node_name, delay_days, nodes_info)
    return suggestions, subsequent