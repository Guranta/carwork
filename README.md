# Carwork —— 保险理赔 + 车后市场 AI 平台

一套底座，两个产品：保险理赔 AI（视觉定损 / 单证 OCR / 全流程理赔助手）与车后市场 AI（门店 SaaS / 配件供应链 / 维保档案 / 导修客服 / 技师辅助）。

> 架构与路线图见 [PROJECT_PLAN.md](./PROJECT_PLAN.md)。

## 技术栈

- **后端**：Python 3.11+ / FastAPI / SQLAlchemy 2.0 / Alembic
- **数据层**：PostgreSQL 16 + pgvector / Redis / MinIO
- **异步**：Celery
- **AI**：调用国内商业 API（DeepSeek / 通义 DashScope / GLM），多供应商路由 + 技能编排 + 全链路日志
- **部署**：Docker Compose（CPU 服务器即可，无需 GPU）

## 目录结构

```
carwork/
├── backend/                 # FastAPI 后端（单服务，模块化分层）
│   ├── app/
│   │   ├── core/            # 配置 / 日志 / 安全 / 依赖
│   │   ├── db/              # 引擎 / Session / Base
│   │   ├── models/          # 共享底座数据模型
│   │   ├── schemas/         # Pydantic
│   │   ├── platform/        # 平台底座服务（车辆/单证/存储）
│   │   ├── domains/         # 产品域（理赔 / 车后）
│   │   ├── ai/              # ★ AI 编排层（providers/skills/rag/orchestrator）
│   │   ├── api/v1/          # REST 路由
│   │   ├── workers/         # Celery 任务
│   │   └── main.py
│   ├── alembic/             # 数据库迁移
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── deploy/nginx/            # Nginx 配置
├── docker-compose.yml       # 全栈一键起
├── .env.example
└── Makefile
```

## 快速开始

### 1. Docker 全栈启动（推荐）

```bash
cp .env.example .env            # 填入至少一个 LLM API Key（如 DEEPSEEK_API_KEY）
make compose-up                 # 构建 + 启动 postgres/redis/minio/backend/worker/nginx
make upgrade-head               # 执行数据库迁移（首次）
```

访问：
- H5 车主端：http://localhost
- API 文档：http://localhost/docs （或 http://localhost/api/v1/health）
- MinIO 控制台：http://localhost:9001 （minioadmin / minioadmin）

如需在 Docker 中启用真实 Agent 对话，请新建 `.env.docker.local`，只写容器可用的私有覆盖项，例如：

```bash
DEEPSEEK_API_KEY=你的-key
MAAS_API_KEY=你的-key
```

不要直接把主机开发用 `.env.local` 作为 Docker env_file；它通常包含 `localhost:5433` 这类仅主机可用的数据库地址。

### 2. 本地开发

```bash
make dev                       # 安装依赖
make upgrade-head              # 迁移
make run                       # 启动 API（热重载）
make worker                    # 另开终端启动 worker

# H5 车主端
cd h5
npm install
npm run dev                    # http://localhost:5174
```

## 核心 AI 能力（技能）

| 技能 | 说明 |
|------|------|
| `ocr_extract` | OCR 文本 → 结构化字段抽取（行驶证/驾驶证/发票） |
| `damage_assessment` | 车损照片 → 损伤识别 + 维修方案 + 估价 |
| `chat` | 导修客服 / 技师辅助 / 配件匹配问答 |

调用统一走 `Orchestrator.invoke(skill, ...)`，自动记录到 `ai_call_log`（成本、耗时、置信度、人工复核闭环）。

## 关键 API 示例

```bash
# 注册拿 token
curl -X POST localhost/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"name":"张三","phone":"13800000000","password":"123456"}'

# 上传单证 + AI 抽取
curl -X POST localhost/api/v1/documents/upload \
  -H "Authorization: Bearer <token>" -F file=@license.jpg -F doc_type=driving_license
curl -X POST localhost/api/v1/documents/<id>/extract -H "Authorization: Bearer <token>"

# 视觉定损
curl -X POST localhost/api/v1/claims/<id>/assess-damage \
  -H "Authorization: Bearer <token>" -H 'Content-Type: application/json' \
  -d '{"image_urls":["https://.../damage1.jpg"]}'
```

## 开发命令

```
make help        # 查看全部命令
make lint        # ruff 检查
make test        # pytest
make migrate m="init tables"
```

## 安全提示

- 生产环境务必修改 `.env` 中的 `SECRET_KEY`、数据库密码、MinIO 凭据
- 敏感单证（保单/证件）建议本地脱敏后再送外部 API
- `ai_call_log` 中的 prompt/response 仅记录摘要，避免明文留存敏感信息（生产前需清洗）

## 路线图

详见 [PROJECT_PLAN.md](./PROJECT_PLAN.md)：Phase 0 验证 → Phase 1 理赔 MVP → Phase 2 理赔全流程 + 车后 MVP → Phase 3 车后深化。
