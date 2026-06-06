from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from utils.tts_alerter import speak_alert
from services.node_service import get_nodes_for_project
from utils.db_conn import SessionLocal
from models.node import Node

router = APIRouter(prefix="/tts", tags=["tts"])

class SpeakRequest(BaseModel):
    project_id: int

@router.post("/speak")
async def speak_alert_api(req: SpeakRequest):
    db = SessionLocal()
    try:
        nodes = get_nodes_for_project(req.project_id)
        # 收集 delayed 和 overdue 节点名称
        delayed = [n.node_name for n in nodes if n.status == 'delayed']
        overdue = [n.node_name for n in nodes if n.status == 'overdue']
        if not delayed and not overdue:
            return {"audio": None, "message": "当前没有延期或超期节点"}
        audio_path = speak_alert("", delayed, overdue)  # project_name 未使用
        if audio_path:
            # 返回音频文件的 base64 或路径，前端需要能访问。为了简单，我们返回音频文件的 URL
            # 因为前端代理 /uploads 到后端，但音频文件在 tmp_tts 目录，我们需要将其移动或提供静态访问。
            # 简单做法：读取文件并返回 base64
            import base64, os
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode()
            return {"audio_base64": audio_base64, "message": "语音生成成功"}
        else:
            return {"audio": None, "message": "语音生成失败"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()