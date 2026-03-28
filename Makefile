SHELL := /bin/bash

.PHONY: help local-up local-down local-restart local-status docker-build docker-up docker-down docker-restart docker-logs

help:
	@printf '%s\n' \
		'make local-up       # 直接启动前后端' \
		'make local-down     # 停止本地启动的前后端' \
		'make local-restart  # 重启本地前后端' \
		'make local-status   # 查看本地前后端状态' \
		'make docker-build   # 仅构建 docker 镜像' \
		'make docker-up      # 构建并启动 docker compose' \
		'make docker-down    # 停止 docker compose' \
		'make docker-restart # 重启 docker compose' \
		'make docker-logs    # 查看 docker compose 日志'

local-up:
	@./scripts/start-local.sh

local-down:
	@./scripts/stop-local.sh

local-restart: local-down local-up

local-status:
	@./scripts/status-local.sh

docker-build:
	@./scripts/docker-build.sh

docker-up:
	@./scripts/docker-up.sh

docker-down:
	@./scripts/docker-down.sh

docker-restart: docker-down docker-up

docker-logs:
	@./scripts/docker-logs.sh
