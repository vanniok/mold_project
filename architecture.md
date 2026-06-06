# 系统架构

## 整体架构图

[浏览器] <--(HTTP/WebSocket)--> [React前端 (Vite)]
                                  |
                                  | /api 代理
                                  v
                         [Nginx (生产环境)]
                                  |
                                  v
                         [FastAPI 后端 (Uvicorn)]
                                  |
                                  +--[SQLite]
                                  +--[DeepSeek API]
                                  +--[阿里云 DashScope TTS]
                                  +--[企业微信回调]

## 模块划分

### 后端模块 (mold_api)

- main.py: FastAPI 应用入口，CORS 配置，静态文件挂载。
- routers/: 路由层
  - projects.py: 项目 CRUD
  - nodes.py: 节点 CRUD、移动、自定义节点、批量重置
  - external_tasks.py: 外协任务管理、图片上传
  - ai.py: AI 压缩建议
  - tts.py: 语音播报
  - history.py: 历史案例检索
  - stats.py: 全局统计
  - wecom.py: 企业微信回调处理
- services/: 业务逻辑层
  - project_service.py: 项目创建、节点初始化
  - node_service.py: 节点排序、进度计算、状态更新
  - compression_service.py: 准备压缩数据
  - external_task_service.py: 外协任务持久化
- models/: SQLAlchemy ORM 模型
- utils/: 数据库连接、日志、DeepSeek 调用、TTS、日期解析
- schedule_engine/: 排程引擎，根据模板生成节点计划日期
- core.py: 节点枚举、工期模板、常量定义
- rules/: 压缩规则（最大压缩天数、不可压缩节点等）

### 前端模块 (mold_frontend)

- src/pages/: 页面组件
  - Dashboard.tsx: 主控台（项目列表 + 节点表格 + 甘特图）
  - VendorPage.tsx: 外协厂商独立页面（通过 ?task_id=xx 访问）
- src/components/: 可复用组件
  - ProjectSidebar.tsx: 项目侧边栏
  - NodeTable.tsx: 节点编辑表格（支持行内编辑、批量保存）
  - GanttChart.tsx: 甘特图（基于 Plotly）
  - ExternalTasks.tsx: 外协任务管理
  - AIButtons.tsx: AI 压缩建议按钮
  - VoiceAlert.tsx: 语音播报按钮
  - OverdueReminders.tsx: 逾期节点提醒条
  - HistorySearch.tsx: 历史案例检索
  - GlobalStats.tsx: 全局统计
  - NewProjectForm.tsx: 新建项目表单
- src/contexts/ProjectContext.tsx: 全局项目状态（当前项目、刷新触发器）
- src/api/: Axios 封装，与后端交互

### 核心业务层 (mold_core)

- core.py: 节点枚举 MoldNode，标准工期模板（标准版/加急版）
- schedule_engine/planner.py: 根据项目开始日期和模板计算每个节点的计划起止日期
- rules/compression_rules.py: AI 压缩提示词模板
- utils/ai_compressor.py: 调用 DeepSeek API 获取压缩建议
- utils/tts_alerter.py: 调用阿里云 TTS 生成语音
- database/db.py: 数据库初始化和基本操作（可选，实际大部分在 services 中）

## 数据流

### 项目创建流程
1. 前端提交项目名称、客户、模板版本、开始日期
2. 后端 projects.py 调用 create_project
3. 在 projects 表插入记录
4. 根据模板在 nodes 表插入标准节点（计划日期为占位符 SENTINEL_DATE）
5. 返回项目 ID，前端更新上下文

### 节点计划日期初始化
- 用户点击“一键初始化（仅空白）” → 后端根据开始日期和模板，重新计算每个节点的 planned_start 和 planned_end，覆盖占位符。

### 外协进度更新（企业微信）
1. 外协厂商在企业微信中发送消息，格式 任务名 60%
2. 企业微信回调到 /wxwork/callback
3. 后端解析 XML，解密，提取任务名和进度
4. 在 external_tasks 表中模糊匹配任务名，更新进度及 last_updated
5. 返回加密回复“已更新”

### AI 压缩建议
1. 前端点击“AI 压缩建议”，传递 project_id
2. 后端找出第一个延期节点，获取延期天数
3. 收集后续节点信息（名称、剩余计划天数等）
4. 调用 DeepSeek API，按规则输出需要压缩的节点及天数
5. 返回建议列表，前端展示

## 技术选型理由

- FastAPI: 异步高性能，自动生成 OpenAPI 文档，便于调试
- React + TypeScript: 强类型，组件化，适合复杂交互界面
- SQLite: 轻量级，适合中小项目，无需额外数据库服务
- TanStack Query: 管理服务端状态，自动缓存、重新获取
- Plotly: 甘特图可视化效果好，交互友好
- DeepSeek API: 成本低，响应快，适合中文压缩逻辑
- 阿里云 DashScope: TTS 音色自然，支持实时生成语音

## 部署架构

- 开发环境: 前后端分离，Vite 代理 /api 到 FastAPI
- 生产环境: Nginx 托管前端构建产物，反向代理 /api 到后端，后端使用 systemd 管理 Uvicorn 进程