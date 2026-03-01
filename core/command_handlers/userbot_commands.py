# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可，
# 并附加非商业使用限制条款。
#
# - 署名：必须提供本项目的原始来源链接
# - 非商业：禁止任何商业用途和分发
# - 相同方式共享：衍生作品必须采用相同的许可证
#
# 本项目源代码：https://github.com/Sakura520222/Sakura-Bot
# 许可证全文：参见 LICENSE 文件

"""
UserBot 相关命令处理器

提供 UserBot 状态检查和管理功能
"""

import logging

from telethon.tl.types import Message

from ..userbot_client import get_userbot_client

logger = logging.getLogger(__name__)


async def handle_userbot_status(client, message: Message):
    """
    处理 UserBot 状态查询命令

    Args:
        client: Telegram 客户端实例
        message: 消息对象
    """
    try:
        userbot = get_userbot_client()

        if not userbot:
            # UserBot 未启用
            await message.reply(
                "❌ **UserBot 未启用**\n\n"
                "请在 `.env` 文件中配置：\n"
                "• `USERBOT_ENABLED=true`\n"
                "• `USERBOT_PHONE_NUMBER=+8613800138000`\n\n"
                "配置后重启机器人即可。",
                parse_mode="md",
            )
            return

        # 获取 UserBot 状态
        status = await userbot.get_status()

        if not status.get("available", False):
            # UserBot 初始化失败
            error = status.get("error", "未知错误")
            await message.reply(
                f"⚠️ **UserBot 不可用**\n\n错误: {error}\n\n请检查配置并重启机器人。",
                parse_mode="md",
            )
            return

        # UserBot 可用，显示简化信息（保护隐私）
        is_connected = status.get("connected", False)
        is_initialized = status.get("initialized", False)

        # 构建状态消息（简化版，不包含敏感信息）
        status_text = f"""✅ **UserBot 状态：运行中**

**连接状态**
• 已连接: {"✅ 是" if is_connected else "❌ 否"}
• 已初始化: {"✅ 是" if is_initialized else "❌ 否"}

**功能说明**
UserBot 使用您的真实 Telegram 账号，具有以下优势：
• ✅ 可访问私有频道
• ✅ 更高的消息抓取权限
• ✅ 更稳定的连接
• ✅ 支持更多高级功能"""

        await message.reply(status_text, parse_mode="md")

    except Exception as e:
        logger.error(f"处理 UserBot 状态查询失败: {type(e).__name__}: {e}", exc_info=True)
        await message.reply(
            f"❌ 查询 UserBot 状态失败: {type(e).__name__}: {e}",
            parse_mode="md",
        )
