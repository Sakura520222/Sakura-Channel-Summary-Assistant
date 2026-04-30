# 使用Python 3.13 slim镜像作为基础
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量和时区
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai

# 安装系统依赖并设置时区
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    tzdata \
    && ln -sf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# ====== 阶段 1: 构建前端 ======
FROM node:20-slim AS web-builder
WORKDIR /web
COPY web/package.json web/package-lock.json* ./
RUN npm install --registry=https://registry.npmmirror.com
COPY web/ ./
RUN npm run build

# ====== 阶段 2: 构建后端 ======
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    tzdata \
    && ln -sf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码和启动脚本
COPY . .
COPY docker-entrypoint.sh .

# 从前端构建阶段复制构建产物
COPY --from=web-builder /web/dist /app/web/dist

# 设置启动脚本权限
RUN chmod +x docker-entrypoint.sh

# 创建必要的目录和文件，并设置权限
RUN mkdir -p /app/data/sessions && \
    chmod 755 /app/data /app/data/sessions && \
    touch /app/data/config.json /app/data/prompt.txt /app/data/poll_prompt.txt /app/data/.last_summary_time.json /app/data/.poll_regenerations.json

# 设置数据卷
VOLUME ["/app/data"]

# WebUI 端口
EXPOSE 8080

# 设置入口点
ENTRYPOINT ["./docker-entrypoint.sh"]

# 默认命令
CMD ["python", "main.py"]
