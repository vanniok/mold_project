# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from rules.compression_rules import build_compression_prompt, AI_TEMPERATURE, AI_MAX_TOKENS

def get_compression_suggestions(project_name, delayed_node, delay_days, nodes):
    """
    调用 AI 获取压缩建议，并返回包含新计划日期的调整列表。
    """
    prompt = build_compression_prompt(project_name, delayed_node, delay_days, nodes)
    
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 未找到 DEEPSEEK_API_KEY")
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": AI_TEMPERATURE,
        "max_tokens": AI_MAX_TOKENS
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        print(f"DEBUG reply (first 200 chars): {reply[:200]}")
        
        if "```json" in reply:
            reply = reply.split("```json")[1].split("```")[0]
        elif "```" in reply:
            reply = reply.split("```")[1].split("```")[0]
        suggestions = json.loads(reply.strip())
        adjustments = suggestions.get("adjustments", [])
        
        result = []
        for adj in adjustments:
            node_name = adj["node"]
            compress_days = adj.get("compress_days", 0)
            if compress_days <= 0:
                continue
            node_info = next((n for n in nodes if n["name"] == node_name), None)
            if node_info:
                start = datetime.strptime(node_info["planned_start"], "%Y-%m-%d")
                end = datetime.strptime(node_info["planned_end"], "%Y-%m-%d")
                new_end = end - timedelta(days=compress_days)
                result.append({
                    "node": node_name,
                    "new_planned_start": start.strftime("%Y-%m-%d"),
                    "new_planned_end": new_end.strftime("%Y-%m-%d"),
                    "reason": f"压缩{compress_days}天"
                })
            else:
                result.append({
                    "node": node_name,
                    "new_planned_start": "",
                    "new_planned_end": "",
                    "reason": f"未找到节点 {node_name} 的原计划"
                })
        return result
    except Exception as e:
        print(f"AI 调用失败: {e}")
        return None