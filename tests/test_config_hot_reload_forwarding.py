# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from core.config.events import ConfigChangedEvent
from core.forwarding.forwarding_handler import ForwardingHandler
from core.initializers.forwarding_initializer import ForwardingInitializer
from core.web_api import deps


@pytest.mark.asyncio
async def test_webui_write_config_schedules_config_reload():
    """WebUI 保存配置后应显式安排配置热重载。"""
    config_manager = SimpleNamespace(reload_config=AsyncMock(return_value=(True, "")))
    deps.configure_config_manager(config_manager)

    with patch.object(deps, "save_config") as save_config:
        deps.write_config({"forwarding": {"enabled": True, "rules": []}})
        await asyncio.sleep(0)

    save_config.assert_called_once()
    config_manager.reload_config.assert_awaited_once()
    deps.configure_config_manager(None)


@pytest.mark.asyncio
async def test_forwarding_handler_on_config_updated_updates_runtime_config():
    """配置事件应更新转发处理器运行时配置。"""
    handler = ForwardingHandler(Mock(), Mock(), Mock())
    handler.enabled = False
    handler.set_config({"enabled": False, "rules": []})

    event = ConfigChangedEvent(
        config={
            "forwarding": {
                "enabled": True,
                "rules": [
                    {
                        "source_channel": "https://t.me/source_channel",
                        "target_channel": "https://t.me/target_channel",
                    }
                ],
            }
        },
        version=1,
        changed_fields={"forwarding.rules"},
    )

    await handler.on_config_updated(event)

    assert handler.enabled is True
    assert len(handler.config["rules"]) == 1
    assert handler.config["rules"][0]["source_channel"] == "https://t.me/source_channel"


def test_forwarding_initializer_reads_current_source_channels_from_handler_config():
    """转发监听源频道应从处理器当前配置动态读取。"""
    initializer = ForwardingInitializer()
    handler = SimpleNamespace(
        config={
            "rules": [
                {
                    "source_channel": "https://t.me/new_source",
                    "target_channel": "https://t.me/target",
                }
            ]
        }
    )
    initializer.forwarding_handler = handler

    assert initializer._get_current_source_channels() == {"new_source"}

    handler.config = {
        "rules": [
            {
                "source_channel": "https://t.me/another_source",
                "target_channel": "https://t.me/target",
            }
        ]
    }

    assert initializer._get_current_source_channels() == {"another_source"}
