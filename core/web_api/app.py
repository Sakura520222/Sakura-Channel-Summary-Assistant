# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可
#
# - 署名：必须提供本项目的原始来源链接
# - 相同方式共享：衍生作品必须采用相同的许可证
#
# 本项目源代码：https://github.com/Sakura520222/Sakura-Bot
# 许可证全文：参见 LICENSE 文件

"""
FastAPI 应用工厂

创建和配置 FastAPI 应用实例，注册路由和中间件。
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes import (
    ai_config,
    channels,
    dashboard,
    forwarding,
    interaction,
    schedules,
    stats,
    system,
    userbot,
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例"""

    app = FastAPI(
        title="Sakura-Bot WebUI API",
        description="Sakura-Bot Telegram 频道管理助手 Web 管理界面 API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册 API 路由
    app.include_router(dashboard.router, prefix="/api", tags=["仪表板"])
    app.include_router(channels.router, prefix="/api/channels", tags=["频道管理"])
    app.include_router(ai_config.router, prefix="/api/ai", tags=["AI 配置"])
    app.include_router(schedules.router, prefix="/api/schedules", tags=["定时任务"])
    app.include_router(forwarding.router, prefix="/api/forwarding", tags=["转发规则"])
    app.include_router(system.router, prefix="/api/system", tags=["系统运维"])
    app.include_router(stats.router, prefix="/api/stats", tags=["统计数据"])
    app.include_router(interaction.router, prefix="/api/interaction", tags=["互动设置"])
    app.include_router(userbot.router, prefix="/api/userbot", tags=["UserBot 管理"])

    # 注册健康检查端点
    @app.get("/api/health", tags=["健康检查"])
    async def health_check():
        return {"status": "ok", "service": "sakura-bot-webui"}

    # 挂载静态文件（前端构建产物）
    static_dir = Path(__file__).parent.parent.parent / "web" / "dist"
    if static_dir.exists():
        app.mount(
            "/",
            StaticFiles(directory=str(static_dir), html=True),
            name="static",
        )
        logger.info(f"已挂载前端静态文件: {static_dir}")
    else:
        logger.debug(f"前端静态文件目录不存在: {static_dir}，跳过挂载")

    logger.info("FastAPI 应用创建完成")
    return app
