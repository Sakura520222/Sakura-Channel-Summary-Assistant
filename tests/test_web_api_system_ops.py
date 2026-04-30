# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可

import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.web_api.routes import system
from core.web_api.schemas.system import CleanupRequest


def _request(user_id: str = "admin"):
    return SimpleNamespace(state=SimpleNamespace(user=SimpleNamespace(user_id=user_id)))


@pytest.mark.asyncio
async def test_start_qa_bot_endpoint_calls_process_manager_and_audits():
    """启动 QA Bot 接口应调用进程管理器并写入审计记录。"""
    result_payload = {"success": True, "message": "started", "pid": 12345}

    with (
        patch("core.system.process_manager.start_qa_bot", return_value=result_payload) as start,
        patch.object(system, "record_system_audit", new=AsyncMock()) as audit,
    ):
        result = await system.start_qa_bot_endpoint(_request())

    assert result == {"success": True, "message": "started", "data": {"pid": 12345}}
    start.assert_called_once_with()
    audit.assert_awaited_once()
    audit_kwargs = audit.await_args.kwargs
    assert audit_kwargs["action"] == "qa_bot.start"
    assert audit_kwargs["success"] is True
    assert audit_kwargs["actor"] == "admin"


@pytest.mark.asyncio
async def test_check_qa_bot_health_endpoint_returns_restart_hint_and_audits():
    """QA Bot 健康检查接口应返回健康状态和是否建议重启。"""
    with (
        patch(
            "core.system.process_manager.check_qa_bot_health",
            return_value=(False, True, "process not running"),
        ),
        patch.object(system, "record_system_audit", new=AsyncMock()) as audit,
    ):
        result = await system.check_qa_bot_health_endpoint(_request())

    assert result["success"] is True
    assert result["data"] == {
        "healthy": False,
        "should_restart": True,
        "message": "process not running",
    }
    assert audit.await_args.kwargs["action"] == "qa_bot.health"


@pytest.mark.asyncio
async def test_reload_config_endpoint_updates_module_variables_and_audits():
    """配置重载接口应重新读取配置并刷新模块变量。"""
    config = {"channels": ["@a"], "log_level": "DEBUG"}

    with (
        patch("core.config.load_config", return_value=config) as load_config,
        patch("core.config.update_module_variables") as update_vars,
        patch.object(system, "record_system_audit", new=AsyncMock()) as audit,
    ):
        result = await system.reload_config_endpoint(_request())

    assert result["success"] is True
    assert result["data"]["config_keys"] == 2
    load_config.assert_called_once_with()
    update_vars.assert_called_once_with(config)
    assert audit.await_args.kwargs["action"] == "config.reload"


@pytest.mark.asyncio
async def test_discussion_cache_status_and_clear_specific_channel():
    """讨论组缓存接口应支持查看数量和清理指定频道。"""
    cache = MagicMock()
    cache.size.return_value = 2
    cache.get_all.return_value = {"@a": -1001, "@b": -1002}
    cache.delete.return_value = True

    with (
        patch("core.services.cache_manager.get_discussion_cache", return_value=cache),
        patch.object(system, "record_system_audit", new=AsyncMock()) as audit,
    ):
        status = await system.get_discussion_cache_status()
        cleared = await system.clear_discussion_cache_endpoint(_request(), channel="@a")

    assert status["data"] == {"size": 2, "channels": ["@a", "@b"]}
    assert cleared == {"success": True, "message": "已清理频道缓存: @a", "data": {"cleared": 1}}
    cache.delete.assert_called_once_with("@a")
    assert audit.await_args.kwargs["target"] == "@a"


@pytest.mark.asyncio
async def test_cleanup_forwarded_messages_calls_database_and_audits():
    """数据库清理接口应调用已有清理方法并记录删除数量。"""
    db = SimpleNamespace(cleanup_old_forwarded_messages=AsyncMock(return_value=7))

    with (
        patch.object(system, "_get_db", return_value=db),
        patch.object(system, "record_system_audit", new=AsyncMock()) as audit,
    ):
        result = await system.cleanup_forwarded_messages_endpoint(
            CleanupRequest(days=14), _request()
        )

    assert result == {
        "success": True,
        "message": "已清理 7 条旧转发记录",
        "data": {"deleted_count": 7, "days": 14},
    }
    db.cleanup_old_forwarded_messages.assert_awaited_once_with(days=14)
    assert audit.await_args.kwargs["action"] == "database.cleanup.forwarded_messages"


@pytest.mark.asyncio
async def test_recent_logs_are_limited_and_filtered():
    """最近日志接口应限制行数，并支持级别和关键词过滤。"""
    log_file = Path("logs/test-system-ops.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        await asyncio.to_thread(
            log_file.write_text,
            "\n".join(
                [
                    "2026-01-01 INFO startup complete",
                    "2026-01-01 WARNING ignored noise",
                    "2026-01-01 ERROR qa failed",
                    "2026-01-01 ERROR database failed",
                ]
            ),
            encoding="utf-8",
        )
        settings = SimpleNamespace(log=SimpleNamespace(log_file_path=str(log_file)))

        with patch("core.settings.get_settings", return_value=settings):
            result = await system.get_recent_logs(lines=2, level="ERROR", keyword="qa")
    finally:
        await asyncio.to_thread(log_file.unlink, missing_ok=True)

    assert result["success"] is True
    assert result["data"]["lines"] == ["2026-01-01 ERROR qa failed"]
    assert result["data"]["total_returned"] == 1


@pytest.mark.asyncio
async def test_audit_logs_endpoint_returns_rows_from_database():
    """审计记录接口应从数据库返回最近操作。"""
    rows = [
        {
            "id": 1,
            "action": "qa_bot.restart",
            "actor": "admin",
            "target": "",
            "params_summary": "{}",
            "success": 1,
            "message": "ok",
            "duration_ms": 10,
            "created_at": "2026-01-01 00:00:00",
        }
    ]
    db = SimpleNamespace(get_system_audit_logs=AsyncMock(return_value=rows))

    with patch.object(system, "_get_db", return_value=db):
        result = await system.get_audit_logs(limit=10)

    assert result["success"] is True
    assert result["data"]["items"][0]["action"] == "qa_bot.restart"
    assert result["data"]["items"][0]["success"] is True
    db.get_system_audit_logs.assert_awaited_once_with(limit=10)
