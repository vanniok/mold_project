# rules/compression_rules.py

MAX_COMPRESS_DAYS = 2
UNCOMPRESSIBLE_NODES = ["试模"]
DELAY_TOLERANCE_DAYS = 2
WARNING_DAYS = 3
AI_TEMPERATURE = 0.1
AI_MAX_TOKENS = 1000

def build_compression_prompt(project_name, delayed_node, delay_days, nodes):
    node_lines = []
    for n in nodes:
        node_lines.append(
            f"{n['name']}: 原计划天数 {n.get('planned_days', 0)}天"
            f"{' (不可压缩)' if n['name'] in UNCOMPRESSIBLE_NODES else ' (可压缩)'}"
        )
    nodes_text = "\n".join(node_lines)

    prompt = f"""你是一个模具项目排程专家。项目“{project_name}”的“{delayed_node}”节点延期了 {delay_days} 天。
目标：通过压缩后续节点的计划天数来追回延期天数。
规则：
- 按顺序逐个压缩。
- 每个节点最多压缩 {MAX_COMPRESS_DAYS} 天。
- 不可压缩节点不能压缩。
- 请只输出需要压缩的节点(compress_days > 0)，不要输出不需要压缩的节点。
- 输出格式为 JSON,例如：{{"adjustments": [{{"node": "加工", "compress_days": 2}}]}}
如果无需任何压缩，返回 {{"adjustments": []}}。

后续节点（按顺序）：
{nodes_text}
请输出 JSON,不要有其他文字。"""
    return prompt