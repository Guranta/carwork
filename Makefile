SHELL := /bin/bash
.DEFAULT_GOAL := help

.PHONY: help install dev migrate upgrade-head seed run worker compose-up compose-down lint test

help: ## 显示帮助
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## 在 backend 下创建 venv 并安装依赖
	python3 -m venv backend/.venv && \
	backend/.venv/bin/pip install --upgrade pip && \
	backend/.venv/bin/pip install -e "backend[dev]"

dev: ## 安装依赖到当前 Python（开发用）
	pip install -e "backend[dev]"

migrate: ## 生成迁移（用法: make migrate m="msg"）
	alembic -c backend/alembic.ini revision --autogenerate -m "$(m)"

upgrade-head: ## 执行迁移到最新版本
	alembic -c backend/alembic.ini upgrade head

run: ## 本地运行后端（热重载，读 .env/.env.local，依赖 Docker 里的 infra）
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker: ## 本地运行 Celery worker
	celery -A app.workers.celery_app.celery_app worker --loglevel=info

compose-up: ## 启动全栈（docker compose）
	cp -n .env.example .env 2>/dev/null; docker compose up -d --build

compose-down: ## 停止全栈
	docker compose down

lint: ## 代码检查
	cd backend && ruff check . && ruff format --check .

test: ## 运行测试
	cd backend && pytest -q
