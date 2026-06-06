# 详细设计

## 数据库设计

### 表 `projects`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(200) | 项目名称 |
| customer | VARCHAR(100) | 客户名称 |
| template_version | VARCHAR(50) | 模板版本（标准版/加急版） |
| start_date | DATETIME | 项目开始日期 |
| created_at | DATETIME | 创建时间 |

### 表 `nodes`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| project_id | INTEGER | 外键关联 projects |
| node_name | VARCHAR(50) | 节点名称 |
| planned_start | DATETIME | 计划开始时间 |
| planned_end | DATETIME | 计划结束时间 |
| actual_start | DATETIME | 实际开始时间 |
| actual_end | DATETIME | 实际结束时间 |
| status | VARCHAR(20) | pending/doing/done/delayed/overdue |
| responsible_person | VARCHAR(50) | 责任人 |
| progress_percent | INTEGER | 进度百分比 0-100 |
| display_order | INTEGER | 显示顺序 |
| reminder_last | DATETIME | 上次点击“暂不处理”的时间 |
| reminder_muted | BOOLEAN | 是否永久静默 |

### 表 `external_tasks`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| project_id | INTEGER | 外键 |
| task_name | VARCHAR(100) | 任务名称 |
| responsible | VARCHAR(50) | 责任人（外协厂） |
| progress_percent | INTEGER | 进度 |
| proof_image_path | VARCHAR(500) | 凭证图片路径 |
| last_updated | DATETIME | 最后更新时间（外协上报时更新） |

### 表 `operation_log` (审计日志)

记录节点和外协任务的增删改操作，用于追溯。

## 核心算法

### 1. 节点状态自动计算

规则：
- 如果有 `actual_end` → status = `done`, progress = 100
- 否则如果有 `actual_start`:
  - 如果当前日期 > `planned_end` + 逾期阈值(2天) → status = `overdue`
  - 如果当前日期 > `planned_end` 且 ≤ 阈值 → status = `delayed`
  - 否则 status = `doing`
- 否则 status = `pending`

进度自动计算（如果未手工填写）：
- 已结束：100%
- 进行中：`(当前日期 - actual_start) / (planned_end - planned_start) * 100`，上限100%

### 2. 排程引擎

输入：开始日期 `start_date`，模板名称
输出：每个节点的 `planned_start`, `planned_end`

依赖关系：
- 设计 → 设计评审 → 4个并行订购任务（模架、材料、配件、热流道）→ 后续串行加工工序
- 并行任务取最大结束日期作为后续开始的基准

### 3. AI 压缩建议

- 找出项目中第一个延期节点（`status='delayed'`）
- 计算延期天数 `delay_days`
- 收集后续节点，提取原计划天数
- 构造 Prompt（包含不可压缩节点列表、最大压缩天数等）
- 调用 DeepSeek API，解析返回的 JSON，生成压缩后的新计划结束日期
- 前端展示建议，不自动应用（用户需手动调整）

### 4. 逾期提醒策略

- 每天扫描节点，逾期且未完成且未静默的节点展示在顶部
- 用户点击“暂不处理”：记录当前时间到 `reminder_last`，下次提醒将在逾期≥10天且距离上次暂不处理≥10天后
- 用户点击“不再提醒”：设置 `reminder_muted=true`，永久不提醒
- 用户点击“标记完成”：自动设置 `actual_end` 为当前时间，状态变为 `done`，进度100%

### 5. 外协任务图片上传

- 前端使用 `multipart/form-data` 上传图片
- 后端保存到 `uploads/` 目录，文件名格式 `task_{task_id}_{timestamp}_{uuid}.ext`
- 前端访问图片时通过 `/uploads/` 静态路由

### 6. 企业微信回调加密/解密

- 使用企业微信提供的 AES 加解密方案
- 收到回调 XML，提取 `<Encrypt>` 节点，解密得到明文
- 解析 `MsgType`，仅处理 `text` 消息
- 正则匹配 `([\u4e00-\u9fa5a-zA-Z0-9]+)\s*(\d{1,3})%?` 提取任务名和进度
- 更新数据库，返回加密回复 `success`

## 安全与隐私

- 环境变量存储 API Key，`.env` 文件不提交到 Git
- 上传的图片对外提供访问路径，但需注意权限控制（可后续增加登录验证）
- 企业微信回调签名校验，防止伪造请求

## 异常处理

- 后端所有 API 返回 `{"error": "..."}` 而非抛出异常
- 前端使用 TanStack Query 的 `onError` 显示错误提示
- TTS 生成失败时前端提示，不阻塞其他功能
- AI 请求超时时返回建议列表为空，并提示用户