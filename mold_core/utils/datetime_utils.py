# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional

def parse_datetime_safe(date_str: Optional[str]) -> Optional[datetime]:
    """
    安全解析日期字符串，支持常见 ISO 8601 变体：
    - 'YYYY-MM-DDTHH:MM:SS'
    - 'YYYY-MM-DDTHH:MM:SS.fffZ'
    - 'YYYY-MM-DD'
    - 'YYYY-MM-DDTHH:MM:SS+HH:MM' (时区偏移，会忽略时区)
    解析失败时抛出 ValueError。
    """
    if not date_str:
        return None
    
    # 1. 去除末尾的 Z（UTC 标识）
    cleaned = date_str.rstrip('Z')
    
    # 2. 去除毫秒部分（从第一个 '.' 到末尾，可能有时区偏移符号）
    if '.' in cleaned:
        # 保留时区偏移符号（+/-）之前的毫秒部分，直接去掉点后面的所有内容
        # 更简单的方法：按 '.' 切分，取第一部分
        cleaned = cleaned.split('.')[0]
    
    # 3. 尝试解析（标准格式无 Z 无毫秒）
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        # 4. 如果失败，尝试仅日期格式
        try:
            return datetime.strptime(cleaned, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"无法解析日期字符串: {date_str}")