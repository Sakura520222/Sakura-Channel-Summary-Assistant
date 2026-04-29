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
API 路由模块
"""

from . import (
    ai_config,
    auth,
    channels,
    dashboard,
    forwarding,
    interaction,
    schedules,
    stats,
    system,
    userbot,
)

__all__ = [
    "ai_config",
    "auth",
    "channels",
    "dashboard",
    "forwarding",
    "interaction",
    "schedules",
    "stats",
    "system",
    "userbot",
]
