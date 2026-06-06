# -*- coding: utf-8 -*-
import pandas as pd
from pathlib import Path

def read_excel(file_path):
    """读取Excel文件，返回DataFrame和原始文件名"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    df = pd.read_excel(file_path, engine='openpyxl')
    if df.empty:
        raise ValueError("Excel文件无数据")
    return df, path.stem