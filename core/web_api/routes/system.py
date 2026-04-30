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
系统运维 API 路由

提供 Bot 状态查看、暂停/恢复、日志级别调整等功能。
"""

import logging

import aiofiles
from fastapi import APIRouter, HTTPException

from core.config import RESTART_FLAG_FILE, get_bot_state, set_bot_state
from core.web_api.schemas.system import BotStatusResponse, LogLevelUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status")
async def get_system_status():
    """获取 Bot 运行状态"""
    try:
        from core.config import load_config

        config = load_config()
        channels = config.get("channels", [])
        forwarding = config.get("forwarding", {})

        # 检查各组件状态
        userbot_connected = False
        try:
            from core.telegram.client import get_active_client

            client = get_active_client()
            userbot_connected = client is not None and client.is_connected()
        except Exception:
            pass

        qa_bot_running = False
        try:
            from core.system.process_manager import get_qa_bot_process

            proc = get_qa_bot_process()
            qa_bot_running = proc is not None and proc.poll() is None
        except Exception:
            pass

        return {
            "success": True,
            "data": BotStatusResponse(
                status=get_bot_state(),
                version="1.8.2",
                log_level=logging.getLevelName(logging.getLogger().level),
                channel_count=len(channels),
                forwarding_enabled=forwarding.get("enabled", False),
                qa_bot_running=qa_bot_running,
                userbot_connected=userbot_connected,
                uptime_seconds=0,  # TODO: 从 bootstrap 获取
            ).model_dump(),
        }

    except Exception as e:
        logger.error(f"获取系统状态失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/pause")
async def pause_bot():
    """暂停 Bot 定时任务"""
    try:
        from core.config import BOT_STATE_PAUSED

        current = get_bot_state()
        if current == BOT_STATE_PAUSED:
            return {"success": False, "message": "Bot 已处于暂停状态"}

        set_bot_state(BOT_STATE_PAUSED)
        logger.info("已通过 WebUI 暂停 Bot")
        return {"success": True, "message": "Bot 已暂停"}

    except Exception as e:
        logger.error(f"暂停 Bot 失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/resume")
async def resume_bot():
    """恢复 Bot 定时任务"""
    try:
        from core.config import BOT_STATE_RUNNING

        current = get_bot_state()
        if current == BOT_STATE_RUNNING:
            return {"success": False, "message": "Bot 已处于运行状态"}

        set_bot_state(BOT_STATE_RUNNING)
        logger.info("已通过 WebUI 恢复 Bot")
        return {"success": True, "message": "Bot 已恢复"}

    except Exception as e:
        logger.error(f"恢复 Bot 失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/log-level")
async def update_log_level(request: LogLevelUpdate):
    """修改日志级别"""
    try:
        import logging as logging_module

        # 更新根 logger 和所有 handler 的级别
        root_logger = logging_module.getLogger()
        level = getattr(logging_module, request.level)
        root_logger.setLevel(level)
        for handler in root_logger.handlers:
            handler.setLevel(level)

        # 更新配置
        from core.config import load_config, save_config

        config = load_config()
        config["log_level"] = request.level
        save_config(config)

        logger.info(f"已通过 WebUI 修改日志级别: {request.level}")
        return {"success": True, "message": f"日志级别已修改为: {request.level}"}

    except Exception as e:
        logger.error(f"修改日志级别失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/restart")
async def restart_bot():
    """立即重启 Bot（优雅关闭后用 os.execv 替换当前进程）"""
    try:
        # 写入重启标记（webui_restart 区别于 Telegram 命令的标记）
        async with aiofiles.open(RESTART_FLAG_FILE, "w") as f:
            await f.write("webui_restart")

        logger.info("已通过 WebUI 请求重启 Bot")

        # 立即触发优雅关闭流程
        from core.config import trigger_shutdown

        trigger_shutdown()

        return {"success": True, "message": "正在重启 Bot..."}

    except Exception as e:
        logger.error(f"请求重启失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e
