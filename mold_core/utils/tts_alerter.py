# -*- coding: utf-8 -*-
# utils/tts_alerter.py
import os
import uuid
import dashscope
from dotenv import load_dotenv
import logging
import requests

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def text_to_speech(text: str, voice: str = "Cherry") -> str:
    """
    使用 Qwen-TTS 将文本转为语音。
    返回生成的 mp3 文件路径，失败返回 None。
    """
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        logger.error("请在 .env 中设置 DASHSCOPE_API_KEY")
        return None
    
    dashscope.api_key = api_key

    tmp_dir = "tmp_tts"
    os.makedirs(tmp_dir, exist_ok=True)
    output_file = os.path.join(tmp_dir, f"tts_{uuid.uuid4().hex}.mp3")

    try:
        logger.info(f"调用 Qwen-TTS, 文本：{text[:30]}...")
        from dashscope import MultiModalConversation
        response = MultiModalConversation.call(
            model="qwen-tts-latest",
            text=text,
            voice=voice,
        )
        if response.status_code == 200:
            audio_obj = response.output.audio
            if hasattr(audio_obj, 'data') and audio_obj.data:
                audio_bytes = audio_obj.data
                with open(output_file, "wb") as f:
                    f.write(audio_bytes)
                logger.info(f"TTS 文件保存: {output_file}")
                return output_file
            elif hasattr(audio_obj, 'url') and audio_obj.url:
                resp = requests.get(audio_obj.url)
                if resp.status_code == 200:
                    with open(output_file, "wb") as f:
                        f.write(resp.content)
                    return output_file
                else:
                    logger.error(f"下载失败: {resp.status_code}")
                    return None
            else:
                logger.error("未知音频对象格式")
                return None
        else:
            logger.error(f"TTS 调用失败: {response.message}")
            return None
    except Exception as e:
        logger.error(f"TTS 异常: {e}")
        return None

def speak_alert(project_name: str, delayed_nodes: list, overdue_nodes: list) -> str:
    """
    合并超期和延期节点，生成语音文本：“老板老板，X个节点 A、B、C 超辣超辣。”
    """
    all_nodes = overdue_nodes + delayed_nodes
    if not all_nodes:
        return None

    count = len(all_nodes)
    nodes_str = "、".join(all_nodes[:3])
    if count > 3:
        nodes_str += f"等{count}个"

    text = f"老板老板，{count}个节点 {nodes_str} 超辣超辣。"
    return text_to_speech(text, voice="Cherry")