# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

def add_days(date: datetime, days: int) -> datetime:
    """增加自然日（不考虑节假日）"""
    return date + timedelta(days=days)

def format_date(date: datetime) -> str:
    return date.strftime("%Y-%m-%d") if date else ""