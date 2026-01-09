#!/bin/bash
set -e

echo "========================================"
echo "Sakura-频道总结助手 Docker 容器启动"
echo "========================================"

# 检查必要的环境变量
echo "检查环境变量配置..."
required_vars=("TELEGRAM_API_ID" "TELEGRAM_API_HASH" "TELEGRAM_BOT_TOKEN")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "错误: 以下必要的环境变量未设置:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    echo "请确保在 .env 文件中正确配置这些变量"
    exit 1
fi

# 检查AI API密钥
if [ -z "$LLM_API_KEY" ] && [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "警告: 未设置AI API密钥 (LLM_API_KEY 或 DEEPSEEK_API_KEY)"
    echo "机器人可能无法正常工作"
fi

echo "环境变量检查完成"

# 创建数据目录和文件
echo "初始化数据目录..."
mkdir -p /app/data

# 检查并创建必要的文件
if [ ! -f /app/data/config.json ]; then
    echo "创建默认 config.json 文件"
    echo '{}' > /app/data/config.json
fi

if [ ! -f /app/data/prompt.txt ]; then
    echo "创建默认 prompt.txt 文件"
    echo "请总结以下 Telegram 消息，提取核心要点并列出重要消息的链接：" > /app/data/prompt.txt
fi

if [ ! -f /app/data/.last_summary_time.json ]; then
    echo "创建默认 .last_summary_time.json 文件"
    echo '{}' > /app/data/.last_summary_time.json
fi

# 创建符号链接到数据目录
echo "创建配置文件符号链接..."
ln -sf /app/data/config.json /app/config.json
ln -sf /app/data/prompt.txt /app/prompt.txt
ln -sf /app/data/.last_summary_time.json /app/.last_summary_time.json

# 检查会话文件
if [ ! -f /app/bot_session.session ]; then
    echo "注意: 未找到会话文件 bot_session.session"
    echo "首次运行需要Telegram登录授权"
    echo "请按照提示完成登录流程"
fi

# 设置文件权限
echo "设置文件权限..."
chown -R appuser:appuser /app/data /app/bot_session.session 2>/dev/null || true

echo "========================================"
echo "启动参数: $@"
echo "========================================"

# 执行主程序
exec "$@"
