# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from core import SCHEDULE_TEMPLATES, NODE_ORDER, DEFAULT_TEMPLATE

def calculate_schedule(project_start_date: datetime, template_name: str = DEFAULT_TEMPLATE):
    """
    根据项目开始日期和模板名称，计算每个节点的计划起止日期。
    支持依赖关系：
    - 设计 → 设计评审
    - 设计评审 → 四个订购任务（并行）
    - 四个订购任务全部完成后 → 成型腔预加工 → 后续串行
    """
    if template_name not in SCHEDULE_TEMPLATES:
        raise ValueError(f"未知的模板: {template_name}")

    template = SCHEDULE_TEMPLATES[template_name]
    duration_map = {node.value: template[node.value] for node in NODE_ORDER}
    
    schedule = []
    
    # 设计
    design_start = project_start_date
    design_end = design_start + timedelta(days=duration_map["模具设计"])
    schedule.append({"node_name": "模具设计", "planned_start": design_start, "planned_end": design_end, "duration": duration_map["模具设计"]})
    
    # 设计评审
    review_start = design_end
    review_end = review_start + timedelta(days=duration_map["模具设计评审"])
    schedule.append({"node_name": "模具设计评审", "planned_start": review_start, "planned_end": review_end, "duration": duration_map["模具设计评审"]})
    
    # 四个并行订购任务
    order_names = ["订购模架", "订购成型腔材料", "订购标准配件", "订购热流道"]
    order_start = review_end
    order_ends = []
    for name in order_names:
        end = order_start + timedelta(days=duration_map[name])
        schedule.append({"node_name": name, "planned_start": order_start, "planned_end": end, "duration": duration_map[name]})
        order_ends.append(end)
    
    last_order_end = max(order_ends)
    
    # 后续串行节点
    subsequent_names = [
        "成型腔预加工", "热处理", "磨床", "CNC", "线切割", "EDM", "配模抛光", "组装试模"
    ]
    current_start = last_order_end
    for name in subsequent_names:
        duration = duration_map[name]
        end = current_start + timedelta(days=duration)
        schedule.append({"node_name": name, "planned_start": current_start, "planned_end": end, "duration": duration})
        current_start = end
    
    return schedule