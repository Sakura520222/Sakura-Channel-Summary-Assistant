# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from core.web_api.routes import commands
from core.web_api.schemas.commands import CommandExecuteRequest


def _request(user_id: str = "admin"):
    return SimpleNamespace(state=SimpleNamespace(user=SimpleNamespace(user_id=user_id)))


@pytest.mark.asyncio
async def test_list_commands_returns_catalog_with_executable_metadata():
    """命令目录接口应返回分类、可执行数量和高危确认文本。"""
    result = await commands.list_commands()

    assert result["success"] is True
    assert result["data"]["total"] > 0
    assert result["data"]["executable_count"] > 0
    assert result["data"]["danger_confirm_text"] == commands.DANGER_CONFIRM_TEXT

    all_items = [item for category in result["data"]["categories"] for item in category["commands"]]
    add_channel = next(item for item in all_items if item["command"] == "addchannel")
    assert add_channel["executable"] is True
    assert add_channel["parameters"][0]["name"] == "channel"


@pytest.mark.asyncio
async def test_execute_add_channel_updates_config_and_audits():
    """执行添加频道命令应更新配置并写入审计记录。"""
    config = {"channels": []}

    with (
        patch.object(commands, "get_config", return_value=config),
        patch.object(commands, "write_config") as write_config,
        patch.object(commands, "record_system_audit", new=AsyncMock()) as audit,
    ):
        result = await commands.execute_command(
            "addchannel",
            CommandExecuteRequest(params={"channel": "https://t.me/example"}),
            _request(),
        )

    assert result["success"] is True
    assert config["channels"] == ["https://t.me/example"]
    write_config.assert_called_once_with(config)
    assert audit.await_args.kwargs["action"] == "command.addchannel"
    assert audit.await_args.kwargs["success"] is True


@pytest.mark.asyncio
async def test_execute_danger_command_requires_confirmation():
    """高危命令缺少二次确认时应拒绝执行。"""
    with patch.object(commands, "record_system_audit", new=AsyncMock()) as audit:
        result = await commands.execute_command(
            "deletechannel",
            CommandExecuteRequest(params={"channel": "@example"}),
            _request(),
        )

    assert result["success"] is False
    assert result["data"]["confirm_required"] is True
    audit.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_danger_command_with_confirmation_runs_and_audits():
    """高危命令确认后应执行并写入审计记录。"""
    config = {
        "channels": ["https://t.me/example"],
        "summary_schedules": {"https://t.me/example": {}},
    }

    with (
        patch.object(commands, "get_config", return_value=config),
        patch.object(commands, "write_config") as write_config,
        patch.object(commands, "record_system_audit", new=AsyncMock()) as audit,
    ):
        result = await commands.execute_command(
            "deletechannel",
            CommandExecuteRequest(
                params={"channel": "@example"},
                confirm=True,
                confirm_text=commands.DANGER_CONFIRM_TEXT,
            ),
            _request(),
        )

    assert result["success"] is True
    assert config["channels"] == []
    assert config["summary_schedules"] == {}
    write_config.assert_called_once_with(config)
    assert audit.await_args.kwargs["action"] == "command.deletechannel"
    assert audit.await_args.kwargs["success"] is True


@pytest.mark.asyncio
async def test_execute_summary_returns_503_when_client_disconnected():
    """需要 Telegram 客户端的命令在客户端不可用时应返回 503。"""
    with (
        patch("core.telegram.client.get_active_client", return_value=None),
        patch.object(commands, "record_system_audit", new=AsyncMock()) as audit,
    ):
        with pytest.raises(Exception) as exc_info:
            await commands.execute_command(
                "summary",
                CommandExecuteRequest(params={"channel": "@example"}),
                _request(),
            )

    assert exc_info.value.status_code == 503
    assert audit.await_args.kwargs["action"] == "command.summary"
    assert audit.await_args.kwargs["success"] is False


@pytest.mark.asyncio
async def test_execute_userbot_list_uses_existing_list_method():
    """命令中心 userbot_list 应调用现有 list_joined_channels 方法。"""
    payload = {
        "success": True,
        "channels": [{"id": 1, "title": "测试频道", "username": "test_channel"}],
        "count": 1,
    }
    userbot = SimpleNamespace(list_joined_channels=AsyncMock(return_value=payload))

    with (
        patch("core.handlers.userbot_client.get_userbot_client", return_value=userbot),
        patch.object(commands, "record_system_audit", new=AsyncMock()) as audit,
    ):
        result = await commands.execute_command(
            "userbot_list",
            CommandExecuteRequest(params={}),
            _request(),
        )

    assert result == {
        "success": True,
        "message": "共 1 个频道",
        "data": {"channels": payload["channels"], "count": 1},
    }
    userbot.list_joined_channels.assert_awaited_once_with()
    assert audit.await_args.kwargs["action"] == "command.userbot_list"
