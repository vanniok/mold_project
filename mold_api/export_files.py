# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
一键导出项目指定文件内容到 TXT 文件（保存到桌面）
自动处理编码：优先 UTF-8，失败时尝试 GBK
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# ==================== 配置区 ====================
# 需要导出的文件列表（相对路径，基于项目根目录）
FILE_LIST = [
    "main.py",
    "routers/tts.py",
    "routers/ai.py",
    "routers/external_tasks.py",
    "routers/__init__.py",
    "routers/nodes.py",
    "routers/projects.py",
    "routers/history.py",
    "routers/stats.py",
    "routers/wecom.py",
    
]

# 输出文件名（保存到桌面，可自定义名称，如 "my_export.txt"）
OUTPUT_FILENAME = "main-api.txt"   # ← 在这里修改你想要的名称（如 "项目导出.txt"）

# ==================== 函数定义 ====================

def get_desktop_path():
    """获取当前用户的桌面路径（跨平台）"""
    if sys.platform == "win32":
        return Path(os.environ.get("USERPROFILE", "~")) / "Desktop"
    else:
        return Path.home() / "Desktop"

def read_file_with_fallback(file_path):
    """
    尝试用 UTF-8 读取文件，失败则用 GBK 编码（适用于中文 Windows 旧文件）
    返回 (content, encoding_used)
    """
    encodings = ['utf-8', 'gbk']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read(), enc
        except UnicodeDecodeError:
            continue
    # 如果都失败，使用 utf-8 并忽略错误
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read(), 'utf-8 (with ignore)'

def export_files(project_root=None):
    """
    导出所有指定文件的内容到一个文本文件，保存到桌面
    :param project_root: 项目根目录（默认当前工作目录）
    """
    if project_root is None:
        project_root = Path.cwd()
    else:
        project_root = Path(project_root)

    if not project_root.exists():
        print(f"❌ 错误：项目根目录不存在 -> {project_root}")
        sys.exit(1)

    # 准备输出文件路径（桌面 + 时间戳命名）
    desktop = get_desktop_path()
    output_file = desktop / OUTPUT_FILENAME

    total_files = len(FILE_LIST)
    success_count = 0
    missing_files = []

    try:
        with open(output_file, "w", encoding="utf-8") as out_f:
            out_f.write(f"# 代码导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            out_f.write(f"# 项目根目录：{project_root}\n")
            out_f.write(f"# 共计划导出 {total_files} 个文件\n")
            out_f.write("=" * 80 + "\n\n")

            for rel_path in FILE_LIST:
                full_path = project_root / rel_path
                out_f.write(f"📁 文件：{rel_path}\n")
                out_f.write("-" * 60 + "\n")

                if not full_path.exists():
                    out_f.write(f"⚠️ 警告：文件不存在，跳过\n\n")
                    missing_files.append(rel_path)
                    continue

                try:
                    content, encoding = read_file_with_fallback(full_path)
                    out_f.write(content)
                    if not content.endswith("\n"):
                        out_f.write("\n")
                    success_count += 1
                    # 可选：在输出中标注使用的编码（调试用）
                    # out_f.write(f"\n# (编码: {encoding})\n")
                except Exception as e:
                    out_f.write(f"❌ 读取文件时出错：{e}\n\n")
                out_f.write("\n" + "=" * 80 + "\n\n")

        print(f"✅ 导出完成！")
        print(f"📂 输出文件：{output_file}")
        print(f"📊 统计：成功 {success_count} / 总计 {total_files} 个文件")
        if missing_files:
            print(f"⚠️ 缺失文件（{len(missing_files)} 个）：")
            for mf in missing_files:
                print(f"   - {mf}")
    except Exception as e:
        print(f"❌ 写入输出文件失败：{e}")
        sys.exit(1)

if __name__ == "__main__":
    # 自动使用当前终端所在目录作为项目根目录
    # 如果脚本不在项目根目录，可以手动传入绝对路径，例如：
    # export_files(Path("/你的/项目/路径"))
    export_files()