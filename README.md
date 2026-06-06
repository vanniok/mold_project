# 模具项目进度管理系统

## 简介

模具项目进度管理系统是一个面向模具制造行业的全栈Web应用，帮助企业管理模具开发项目的节点进度、外协任务跟踪、逾期提醒、AI压缩建议、语音播报等功能。

## 技术栈

- **后端**: FastAPI (Python 3.10+), SQLAlchemy, SQLite
- **前端**: React 19 + TypeScript + Vite, TanStack Query, Axios
- **AI集成**: DeepSeek API (压缩建议), 阿里云DashScope (TTS语音播报)
- **企业微信**: 回调接口，支持外协厂商通过微信上报进度

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 后端启动

```bash
cd mold_api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # 填写 API Key 等配置
python main.py
默认运行在 http://localhost:8000。

前端启动
bash
cd mold_frontend
npm install
npm run dev
默认运行在 http://localhost:5173。

生产部署
后端可使用 systemd 或 supervisor 守护 uvicorn

前端 npm run build 后使用 Nginx 托管静态文件，并配置 /api 代理到后端

主要功能
项目创建、编辑、删除

模具标准节点模板（设计、备料、加工、试模等）

节点计划/实际日期编辑，支持自定义节点

甘特图可视化展示计划与实际进度

外协任务管理（任务名称、责任人、进度、凭证图片）

企业微信回调：外协厂商发送“任务名 进度%”更新进度

逾期节点自动提醒（可暂不处理/永久静音）

AI 智能压缩建议（调用 DeepSeek 分析延期节点，给出后续节点压缩方案）

TTS 语音播报逾期节点（阿里云DashScope）

历史案例检索（基于延期记录）

目录结构
text
mold_api/          # FastAPI 后端
mold_core/         # 核心业务逻辑、模型、工具
mold_frontend/     # React 前端
详细文档请见 architecture.md、design.md。

许可证
私有项目，未经授权不得使用。

text

校准点说明：
- 每个代码块前后均用三个反引号单独成行，且标明语言（`bash`）。
- 删除结尾无意义的 `text` 标记和横线。
- 补全“前端启动”与“后端启动”之间的空行，保持可读性。
- 统一缩进与换行。