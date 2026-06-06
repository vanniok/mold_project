# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from pathlib import Path

def load_config():
    load_dotenv()  # 加载 .env 文件
    db_url = os.getenv("DB_URL")
    if not db_url:
        # 获取当前文件所在目录的父目录（即 mold_core 根目录）
        core_root = Path(__file__).parent.parent
        db_path = core_root / "mold.db"
        db_url = f"sqlite:///{db_path.as_posix()}"
    return {
        "DB_URL": db_url,
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    }