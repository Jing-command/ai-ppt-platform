# AI PPT Platform - Docker 配置

## 📁 文件结构

```
docker/
├── docker-compose.yml          # 基础服务（数据库、缓存）
├── docker-compose.prod.yml     # 生产环境（包含后端、前端）
├── backend.Dockerfile          # 后端镜像构建
├── frontend.Dockerfile         # 前端镜像构建
├── .env.example                # 环境变量模板
└── README.md                   # 本文档
```

## 🚀 快速开始

### 1. 仅启动数据库（开发模式）

```bash
cd docker

# 复制环境变量
cp .env.example .env

# 启动数据库
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f postgres
```

### 2. 启动完整环境（生产模式）

```bash
cd docker

# 启动所有服务
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# 查看所有容器
docker-compose ps
```

## 📊 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| postgres | 5432 | PostgreSQL 数据库 |
| redis | 6379 | Redis 缓存/队列 |
| backend | 8000 | FastAPI 后端（仅生产模式）|
| frontend | 3000 | Next.js 前端（仅生产模式）|

## 🔧 常用命令

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据（慎用！）
docker-compose down -v

# 查看日志
docker-compose logs -f [服务名]

# 进入容器
docker-compose exec postgres psql -U postgres -d ai_ppt

# 重启服务
docker-compose restart [服务名]
```

## 🌐 环境隔离

每个项目使用独立的：
- **容器名**：`ai-ppt-xxx`
- **网络名**：`ai-ppt-network`
- **卷名**：`ai-ppt-xxx-data`

如果端口冲突，修改 `.env` 文件：
```env
POSTGRES_PORT=5433
REDIS_PORT=6380
```

## 📚 参考

- [Docker Compose 文档](https://docs.docker.com/compose/)
- [PostgreSQL Docker 镜像](https://hub.docker.com/_/postgres)
- [Redis Docker 镜像](https://hub.docker.com/_/redis)
