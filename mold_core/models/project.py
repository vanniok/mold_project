# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from utils.db_conn import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="项目名称/模具名称")
    customer = Column(String(100), comment="客户名称")
    template_version = Column(String(50), default="标准版", comment="使用的进度模板")
    start_date = Column(DateTime, nullable=False, comment="项目开始日期")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")