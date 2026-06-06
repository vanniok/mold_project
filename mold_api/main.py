import sys
sys.path.insert(0, r'Z:\mold_core')

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware
from routers import projects, nodes, external_tasks, ai, tts, history, stats, wecom  # 添加 ai 和 wecom

app = FastAPI()

# 确保 uploads 目录存在
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(nodes.router)
app.include_router(external_tasks.router)
app.include_router(ai.router)
app.include_router(tts.router)  # 新增
app.include_router(history.router)
app.include_router(stats.router)
app.include_router(wecom.router)   # 企业微信回调