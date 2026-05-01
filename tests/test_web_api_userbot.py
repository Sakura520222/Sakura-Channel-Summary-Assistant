# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from core.web_api.routes.userbot import (
    ChannelRequest,
    list_userbot_channels,
    userbot_join_channel,
    userbot_leave_channel,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("channel_input", ["@test_channel", "test_channel"])
async def test_userbot_join_channel_uses_userbot_manager(channel_input: str):
    """Web API 加入频道应调用当前 UserBot 管理器，而不是旧模块路径。"""
    settings = SimpleNamespace(userbot=SimpleNamespace(userbot_enabled=True))
    userbot = SimpleNamespace(
        join_channel=AsyncMock(return_value={"success": True, "message": "加入频道成功"})
    )

    with (
        patch("core.settings.get_settings", return_value=settings),
        patch("core.handlers.userbot_client.get_userbot_client", return_value=userbot),
    ):
        result = await userbot_join_channel(ChannelRequest(channel_url=channel_input))

    assert result == {"success": True, "message": "加入频道成功"}
    userbot.join_channel.assert_awaited_once_with("https://t.me/test_channel")


@pytest.mark.asyncio
@pytest.mark.parametrize("channel_input", ["@test_channel", "test_channel"])
async def test_userbot_leave_channel_uses_userbot_manager(channel_input: str):
    """Web API 离开频道应调用当前 UserBot 管理器，而不是旧模块路径。"""
    settings = SimpleNamespace(userbot=SimpleNamespace(userbot_enabled=True))
    userbot = SimpleNamespace(
        leave_channel=AsyncMock(return_value={"success": True, "message": "离开频道成功"})
    )

    with (
        patch("core.settings.get_settings", return_value=settings),
        patch("core.handlers.userbot_client.get_userbot_client", return_value=userbot),
    ):
        result = await userbot_leave_channel(ChannelRequest(channel_url=channel_input))

    assert result == {"success": True, "message": "离开频道成功"}
    userbot.leave_channel.assert_awaited_once_with("https://t.me/test_channel")


@pytest.mark.asyncio
async def test_userbot_list_channels_uses_userbot_manager():
    """Web API 列出频道应调用 UserBot 管理器的 list_joined_channels。"""
    settings = SimpleNamespace(userbot=SimpleNamespace(userbot_enabled=True))
    payload = {
        "success": True,
        "channels": [{"id": 1, "title": "测试频道", "username": "test_channel"}],
        "count": 1,
    }
    userbot = SimpleNamespace(list_joined_channels=AsyncMock(return_value=payload))

    with (
        patch("core.settings.get_settings", return_value=settings),
        patch("core.handlers.userbot_client.get_userbot_client", return_value=userbot),
    ):
        result = await list_userbot_channels()

    assert result == payload
    userbot.list_joined_channels.assert_awaited_once_with()
