# -*- coding: utf-8 -*-
from utils.db_conn import SessionLocal
from sqlalchemy import text

def get_historical_cases(project_name: str, customer: str, limit: int = 2):
    db = SessionLocal()
    try:
        query = text("""
            SELECT project_name, customer, problem_node, solution, delay_days
            FROM historical_cases
            WHERE project_name LIKE :p1 OR customer LIKE :p2
            ORDER BY delay_days DESC
            LIMIT :limit
        """)
        result = db.execute(query, {
            "p1": f"%{project_name}%",
            "p2": f"%{customer}%",
            "limit": limit
        }).fetchall()
        return [dict(row._mapping) for row in result]
    except Exception as e:
        print(f"历史案例检索失败: {e}")
        return []
    finally:
        db.close()