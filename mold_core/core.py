# -*- coding: utf-8 -*-
from enum import Enum
from datetime import datetime, timedelta

# 模具流程节点（状态机）—— 新流程
class MoldNode(Enum):
    DESIGN = "模具设计"
    DESIGN_REVIEW = "模具设计评审"
    ORDER_FRAME = "订购模架"
    ORDER_MATERIAL = "订购成型腔材料"
    ORDER_STANDARD = "订购标准配件"
    ORDER_HOT_RUNNER = "订购热流道"
    PRE_MACHINING = "成型腔预加工"
    HEAT_TREAT = "热处理"
    GRINDING = "磨床"
    CNC = "CNC"
    WIRE_EDM = "线切割"
    EDM = "EDM"
    POLISHING = "配模抛光"
    ASSEMBLY_TRIAL = "组装试模"

# 节点顺序（按工艺流程）
NODE_ORDER = [
    MoldNode.DESIGN,
    MoldNode.DESIGN_REVIEW,
    MoldNode.ORDER_FRAME,
    MoldNode.ORDER_MATERIAL,
    MoldNode.ORDER_STANDARD,
    MoldNode.ORDER_HOT_RUNNER,
    MoldNode.PRE_MACHINING,
    MoldNode.HEAT_TREAT,
    MoldNode.GRINDING,
    MoldNode.CNC,
    MoldNode.WIRE_EDM,
    MoldNode.EDM,
    MoldNode.POLISHING,
    MoldNode.ASSEMBLY_TRIAL,
]

# 标准版工期（单位：天）
SCHEDULE_TEMPLATES = {
    "标准版": {
        "模具设计": 7,
        "模具设计评审": 3,
        "订购模架": 15,
        "订购成型腔材料": 7,
        "订购标准配件": 13,
        "订购热流道": 15,
        "成型腔预加工": 3,
        "热处理": 5,
        "磨床": 3,
        "CNC": 5,
        "线切割": 4,
        "EDM": 5,
        "配模抛光": 7,
        "组装试模": 3,
    },
    "加急版": {
        "模具设计": 5,
        "模具设计评审": 2,
        "订购模架": 12,
        "订购成型腔材料": 5,
        "订购标准配件": 10,
        "订购热流道": 12,
        "成型腔预加工": 2,
        "热处理": 4,
        "磨床": 2,
        "CNC": 4,
        "线切割": 3,
        "EDM": 4,
        "配模抛光": 5,
        "组装试模": 2,
    }
}

DEFAULT_TEMPLATE = "标准版"
OVERDUE_THRESHOLD_DAYS = 2
SENTINEL_DATE = datetime(2026, 1, 1)