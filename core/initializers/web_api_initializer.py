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
WebUI API 初始化器

在 AppBootstrap 中启动 FastAPI Web 服务器，与 Bot 共享事件循环。
"""

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uvicorn import Server

logger = logging.getLogger(__name__)


def _setup_webui_logging() -> str:
    """初始化 WebUI 独立日志

    Returns:
        WebUI 日志文件路径
    """
    from core.infrastructure.logging import setup_component_logging
    from core.settings import get_settings

    settings = get_settings()
    return setup_component_logging(
        component_name="WebUI",
        logger_names=[
            "core.web_api",
            "core.web_api.access",
            "uvicorn",
            "uvicorn.error",
            "uvicorn.access",
        ],
        log_level=settings.log.logging_level,
        log_to_file=settings.log.log_to_file,
        base_log_file_path=settings.log.log_file_path,
        component_log_file_name="webui.log",
        log_file_max_size=settings.log.log_file_max_size,
        log_file_backup_count=settings.log.log_file_backup_count,
        log_to_console=settings.log.log_to_console,
        log_colorize=settings.log.log_colorize,
    )


class WebAPIInitializer:
    """WebUI API 服务器初始化器"""

    def __init__(self, config_manager=None):
        self._config_manager = config_manager
        self._server: Server | None = None
        self._task: asyncio.Task | None = None

    async def initialize(self) -> bool:
        """启动 WebUI API 服务器

        Returns:
            bool: 是否成功启动
        """
        try:
            from core.settings import get_settings

            settings = get_settings()
            webui_settings = getattr(settings, "webui", None)

            if not webui_settings:
                logger.info("WebUI 未配置，跳过初始化（设置 WEBUI_ENABLED=true 启用）")
                return False

            if not getattr(webui_settings, "enabled", False):
                logger.info("WebUI 已禁用，跳过初始化")
                return False

            host = getattr(webui_settings, "host", "0.0.0.0")
            port = getattr(webui_settings, "port", 8080)

            log_file_path = _setup_webui_logging()
            logger.info(f"WebUI 日志已启用: {log_file_path}")

            await self._start_server(host, port)
            return True

        except Exception as e:
            logger.error(f"WebUI 初始化失败: {type(e).__name__}: {e}", exc_info=True)
            return False

    async def _start_server(self, host: str, port: int) -> None:
        """启动 uvicorn 服务器（在后台任务中运行）

        Args:
            host: 监听地址
            port: 监听端口
        """
        import uvicorn

        from core.web_api.app import create_app
        from core.web_api.deps import configure_config_manager

        configure_config_manager(self._config_manager)
        app = create_app()

        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_level="warning",
            access_log=False,
        )
        self._server = uvicorn.Server(config)

        # 在后台任务中运行服务器
        self._task = asyncio.create_task(self._server.serve())
        logger.info(f"🌐 WebUI API 服务器已启动: http://{host}:{port}")

        # 输出管理 Token 信息
        try:
            import hashlib

            from core.settings import get_settings

            bot_token = get_settings().telegram.bot_token
            if bot_token:
                admin_token = hashlib.sha256(bot_token.encode()).hexdigest()[:16]
                logger.info(f"🔑 WebUI 管理 Token: {admin_token}")
            else:
                logger.warning("⚠️ Bot Token 未配置，WebUI 登录功能不可用")
        except Exception:
            pass

    async def shutdown(self) -> None:
        """关闭 WebUI API 服务器"""
        if self._server:
            self._server.should_exit = True
            logger.info("正在关闭 WebUI API 服务器...")

            if self._task and not self._task.done():
                try:
                    await asyncio.wait_for(self._task, timeout=5.0)
                except TimeoutError:
                    self._task.cancel()
                    logger.warning("WebUI API 服务器关闭超时，已强制取消")

            logger.info("WebUI API 服务器已关闭")

    @property
    def is_running(self) -> bool:
        """服务器是否正在运行"""
        return self._server is not None and not self._server.should_exit
