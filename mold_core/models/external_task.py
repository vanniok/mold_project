# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from utils.db_conn import Base

class ExternalTask(Base):
    __tablename__ = "external_tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    task_name = Column(String(100), nullable=False, comment="任务名称")
    responsible = Column(String(50), nullable=True, comment="责任人（外协厂）")
    progress_percent = Column(Integer, default=0, comment="进度百分比 0-100")
    created_at = Column(DateTime, server_default=func.now())
    last_updated = Column(DateTime, nullable=True, comment="最后更新时间（外协端点击保存时更新）")
    proof_image_path = Column(String(500), nullable=True, comment="凭证图片路径")