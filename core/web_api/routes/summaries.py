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
总结生成 API 路由

提供从 Web UI 触发频道总结生成的功能。
"""

import logging

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{channel:path}/summarize")
async def trigger_summary(channel: str):
    """触发指定频道的总结生成

    Args:
        channel: 频道 URL（如 https://t.me/channel_name）

    Returns:
        生成结果，包含总结文本预览、消息数等信息
    """
    try:
        from core.commands.summary_commands import generate_channel_summary
        from core.telegram.client import get_active_client

        client = get_active_client()
        if not client or not client.is_connected():
            raise HTTPException(
                status_code=503,
                detail="Telegram 客户端未连接，无法生成总结",
            )

        logger.info(f"Web UI 触发总结生成: {channel}")

        result = await generate_channel_summary(channel, client, skip_admins=True)

        if result.get("success"):
            # 截断总结文本用于预览
            summary_text = result.get("summary_text", "")
            preview = summary_text[:200] + ("..." if len(summary_text) > 200 else "")

            return {
                "success": True,
                "data": {
                    "channel_name": result.get("channel_name", channel),
                    "message_count": result.get("message_count", 0),
                    "summary_preview": preview,
                    "summary_length": len(summary_text),
                },
                "message": f"总结生成成功（{result.get('message_count', 0)} 条消息）",
            }
        else:
            return {
                "success": False,
                "message": result.get("error", "总结生成失败，请查看日志"),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"触发总结生成失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e
