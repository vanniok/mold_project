# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from utils.db_conn import Base

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    node_name = Column(String(50), nullable=False, comment="节点名称：设计/备料...")
    planned_start = Column(DateTime, nullable=False, comment="计划开始时间")
    planned_end = Column(DateTime, nullable=False, comment="计划结束时间")
    actual_start = Column(DateTime, nullable=True, comment="实际开始时间")
    actual_end = Column(DateTime, nullable=True, comment="实际结束时间")
    status = Column(String(20), default="pending", comment="pending/doing/done/delayed")
    responsible_person = Column(String(50), nullable=True, comment="责任人")
    progress_percent = Column(Integer, default=0, comment="进度百分比 0-100") 
    display_order = Column(Integer, default=0, comment="节点显示顺序")
    
    reminder_last = Column(DateTime, nullable=True, comment="上次逾期提醒点击暂不处理的时间")
    reminder_muted = Column(Boolean, default=False, comment="是否永久静默逾期提醒")

    project = relationship("Project", backref="nodes")
    vendor_responsible = Column(String(50), nullable=True, comment="外协责任人")
    vendor_progress = Column(Integer, default=0, comment="外协上报进度百分比 0-100")