# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime

COLUMN_MAPPING = {
    "项目名称": ("name", str),
    "客户": ("customer", str),
    "开始日期": ("start_date", lambda x: pd.to_datetime(x).to_pydatetime()),
    "模板版本": ("template_version", str),
}

def map_row_to_project(row: pd.Series) -> dict:
    project_data = {}
    for excel_col, (db_field, converter) in COLUMN_MAPPING.items():
        if excel_col in row and pd.notna(row[excel_col]):
            value = converter(row[excel_col])
            project_data[db_field] = value
        elif db_field == "template_version":
            project_data[db_field] = "标准版"
        else:
            raise ValueError(f"Excel缺少必填列: {excel_col}")
    return project_data