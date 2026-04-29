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
UserBot 管理 API 路由

提供 UserBot 状态查看、加入/离开频道等功能。
"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core.config import normalize_channel_id

logger = logging.getLogger(__name__)

router = APIRouter()


class ChannelRequest(BaseModel):
    """频道请求"""

    channel_url: str = Field(..., description="频道 URL")


@router.get("/status")
async def get_userbot_status():
    """获取 UserBot 状态"""
    try:
        from core.settings import get_settings

        settings = get_settings()
        enabled = settings.userbot.userbot_enabled

        connected = False
        phone = settings.userbot.userbot_phone_number
        phone_preview = ""
        if phone:
            phone_preview = f"{phone[:3]}****{phone[-2:]}" if len(phone) > 5 else "***"

        # 检查连接状态
        try:
            from core.telegram.client import get_active_client

            client = get_active_client()
            if client:
                connected = client.is_connected()
        except Exception:
            pass

        return {
            "success": True,
            "data": {
                "enabled": enabled,
                "connected": connected,
                "phone_preview": phone_preview,
                "fallback_to_bot": settings.userbot.userbot_fallback_to_bot,
            },
        }

    except Exception as e:
        logger.error(f"获取 UserBot 状态失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/join")
async def userbot_join_channel(request: ChannelRequest):
    """让 UserBot 加入指定频道"""
    try:
        from core.settings import get_settings

        settings = get_settings()
        if not settings.userbot.userbot_enabled:
            return {"success": False, "message": "UserBot 未启用"}

        channel_url = normalize_channel_id(request.channel_url)

        # 获取 UserBot 客户端
        try:
            from core.telegram.userbot_client import get_userbot_client

            userbot = get_userbot_client()
            if not userbot:
                return {"success": False, "message": "UserBot 客户端未初始化"}

            # 加入频道
            from telethon.tl.functions.channels import JoinChannelRequest

            entity = await userbot.get_entity(channel_url)
            await userbot(JoinChannelRequest(entity))
            logger.info(f"已通过 WebUI 让 UserBot 加入频道: {channel_url}")
            return {"success": True, "message": f"UserBot 已加入频道: {channel_url}"}

        except Exception as e:
            logger.error(f"UserBot 加入频道失败: {type(e).__name__}: {e}")
            return {"success": False, "message": f"加入频道失败: {e}"}

    except Exception as e:
        logger.error(f"UserBot 加入频道失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/leave")
async def userbot_leave_channel(request: ChannelRequest):
    """让 UserBot 离开指定频道"""
    try:
        from core.settings import get_settings

        settings = get_settings()
        if not settings.userbot.userbot_enabled:
            return {"success": False, "message": "UserBot 未启用"}

        channel_url = normalize_channel_id(request.channel_url)

        try:
            from core.telegram.userbot_client import get_userbot_client

            userbot = get_userbot_client()
            if not userbot:
                return {"success": False, "message": "UserBot 客户端未初始化"}

            from telethon.tl.functions.channels import LeaveChannelRequest

            entity = await userbot.get_entity(channel_url)
            await userbot(LeaveChannelRequest(entity))
            logger.info(f"已通过 WebUI 让 UserBot 离开频道: {channel_url}")
            return {"success": True, "message": f"UserBot 已离开频道: {channel_url}"}

        except Exception as e:
            logger.error(f"UserBot 离开频道失败: {type(e).__name__}: {e}")
            return {"success": False, "message": f"离开频道失败: {e}"}

    except Exception as e:
        logger.error(f"UserBot 离开频道失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e
