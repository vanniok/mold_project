# -*- coding: utf-8 -*-
# deepseek_v4_flash.py
import requests
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

# 从 rules 导入参数（注意路径）
from rules.compression_rules import AI_TEMPERATURE, AI_MAX_TOKENS

API_KEY = os.getenv("DEEPSEEK_API_KEY")
MODEL_ID = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10)
session.mount('https://', adapter)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    reraise=True
)
def _chat_with_ai(payload, headers):
    resp = session.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=70
    )
    resp.raise_for_status()
    return resp.json()

def chat_with_ai(user_input: str, history: list, temperature: float = AI_TEMPERATURE, 
                 max_tokens: int = AI_MAX_TOKENS):
    messages = history + [{"role": "user", "content": user_input}]
    payload = {
        "model": MODEL_ID,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        result = _chat_with_ai(payload, headers)
        import json
        print("=== DeepSeek API 完整返回 ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        reply = result["choices"][0]["message"]["content"]
        usage = result.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        updated_history = history.copy()
        updated_history.append({"role": "user", "content": user_input})
        updated_history.append({"role": "assistant", "content": reply})
        return reply, prompt_tokens, completion_tokens, total_tokens, updated_history
    except Exception as e:
        error_msg = f"DeepSeek API 调用失败: {str(e)}"
        print(error_msg)
        updated_history = history.copy()
        updated_history.append({"role": "user", "content": user_input})
        updated_history.append({"role": "assistant", "content": error_msg})
        return error_msg, 0, 0, 0, updated_history