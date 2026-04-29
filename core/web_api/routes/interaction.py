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
互动设置 API 路由

提供投票设置、自动投票、评论区欢迎配置等功能。
"""

import logging

from fastapi import APIRouter, HTTPException

from core.config import normalize_channel_id
from core.web_api.deps import get_config, write_config
from core.web_api.schemas.interaction import (
    AutoPollSettingsUpdate,
    CommentWelcomeUpdate,
    PollSettingsUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== 投票设置 ====================


@router.get("/poll-settings")
async def get_poll_settings():
    """获取所有频道的投票设置"""
    try:
        config = get_config()
        poll_settings = config.get("channel_poll_settings", {})

        return {
            "success": True,
            "data": {
                "settings": poll_settings,
                "enable_poll": config.get("enable_poll", True),
                "poll_regen_threshold": config.get("poll_regen_threshold", 5),
            },
        }

    except Exception as e:
        logger.error(f"获取投票设置失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/poll-settings/{channel:path}")
async def update_poll_settings(channel: str, request: PollSettingsUpdate):
    """更新指定频道的投票设置"""
    try:
        channel = normalize_channel_id(channel)
        config = get_config()

        poll_settings = config.get("channel_poll_settings", {})
        current = poll_settings.get(channel, {})

        if request.enabled is not None:
            current["enabled"] = request.enabled
        if request.send_to_channel is not None:
            current["send_to_channel"] = request.send_to_channel
        if request.public_voters is not None:
            current["public_voters"] = request.public_voters

        poll_settings[channel] = current
        config["channel_poll_settings"] = poll_settings
        write_config(config)

        logger.info(f"已通过 WebUI 更新投票设置: {channel}")
        return {"success": True, "message": f"投票设置已更新: {channel}"}

    except Exception as e:
        logger.error(f"更新投票设置失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


# ==================== 自动投票 ====================


@router.get("/auto-poll")
async def get_auto_poll_settings():
    """获取自动投票配置"""
    try:
        config = get_config()
        return {
            "success": True,
            "data": {
                "enabled": config.get("enable_auto_poll", False),
                "channel_settings": config.get("channel_auto_poll_settings", {}),
            },
        }

    except Exception as e:
        logger.error(f"获取自动投票配置失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/auto-poll")
async def update_auto_poll(request: AutoPollSettingsUpdate):
    """更新自动投票全局开关"""
    try:
        config = get_config()
        config["enable_auto_poll"] = request.enabled
        write_config(config)

        status_text = "启用" if request.enabled else "禁用"
        logger.info(f"已通过 WebUI {status_text}自动投票")
        return {"success": True, "message": f"自动投票已{status_text}"}

    except Exception as e:
        logger.error(f"更新自动投票配置失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/auto-poll/{channel:path}")
async def update_channel_auto_poll(channel: str, request: AutoPollSettingsUpdate):
    """更新指定频道的自动投票设置"""
    try:
        channel = normalize_channel_id(channel)
        config = get_config()

        auto_poll_settings = config.get("channel_auto_poll_settings", {})
        auto_poll_settings[channel] = {"enabled": request.enabled}
        config["channel_auto_poll_settings"] = auto_poll_settings
        write_config(config)

        logger.info(f"已通过 WebUI 更新频道自动投票设置: {channel}")
        return {"success": True, "message": f"频道自动投票设置已更新: {channel}"}

    except Exception as e:
        logger.error(f"更新频道自动投票设置失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


# ==================== 评论区欢迎 ====================


@router.get("/comment-welcome")
async def get_comment_welcome_config():
    """获取评论区欢迎配置"""
    try:
        config = get_config()
        return {
            "success": True,
            "data": {
                "default": config.get("comment_welcome", {}).get("default", {}),
                "channel_overrides": config.get("channel_comment_welcome", {}),
            },
        }

    except Exception as e:
        logger.error(f"获取评论区欢迎配置失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/comment-welcome/default")
async def update_default_comment_welcome(request: CommentWelcomeUpdate):
    """更新默认评论区欢迎配置"""
    try:
        config = get_config()

        if "comment_welcome" not in config:
            config["comment_welcome"] = {}
        if "default" not in config["comment_welcome"]:
            config["comment_welcome"]["default"] = {}

        default_config = config["comment_welcome"]["default"]

        if request.enabled is not None:
            default_config["enabled"] = request.enabled
        if request.welcome_message is not None:
            default_config["welcome_message"] = request.welcome_message
        if request.button_text is not None:
            default_config["button_text"] = request.button_text
        if request.button_action is not None:
            default_config["button_action"] = request.button_action

        config["comment_welcome"]["default"] = default_config
        write_config(config)

        logger.info("已通过 WebUI 更新默认评论区欢迎配置")
        return {"success": True, "message": "默认评论区欢迎配置已更新"}

    except Exception as e:
        logger.error(f"更新默认评论区欢迎配置失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/comment-welcome/{channel:path}")
async def update_channel_comment_welcome(channel: str, request: CommentWelcomeUpdate):
    """更新指定频道的评论区欢迎配置"""
    try:
        channel = normalize_channel_id(channel)
        config = get_config()

        channel_welcome = config.get("channel_comment_welcome", {})
        current = channel_welcome.get(channel, {})

        if request.enabled is not None:
            current["enabled"] = request.enabled

        channel_welcome[channel] = current
        config["channel_comment_welcome"] = channel_welcome
        write_config(config)

        logger.info(f"已通过 WebUI 更新频道评论区欢迎配置: {channel}")
        return {"success": True, "message": f"频道评论区欢迎配置已更新: {channel}"}

    except Exception as e:
        logger.error(f"更新频道评论区欢迎配置失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e
