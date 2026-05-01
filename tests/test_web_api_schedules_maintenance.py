# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可

import shutil
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from core.web_api.routes import schedules
from core.web_api.schemas.schedule import LastSummaryTimeUpdateRequest


def _tmp_dir(name: str) -> Path:
    """创建测试用临时目录，避开系统临时目录权限问题。"""
    path = Path("tests/.tmp_schedules_maintenance") / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.mark.asyncio
async def test_list_last_summary_times_returns_file_items():
    """上次总结时间接口应返回文件中的频道记录。"""
    time_value = datetime(2026, 1, 1, tzinfo=UTC)
    data = {
        "https://t.me/example": {
            "time": time_value,
            "summary_message_ids": [1],
            "poll_message_ids": [2],
            "button_message_ids": [],
        }
    }
    tmp_path = _tmp_dir("list_summary_times")
    try:
        summary_file = tmp_path / ".last_summary_time.json"
        summary_file.write_text("{}", encoding="utf-8")

        with (
            patch("core.summary_time_manager.load_last_summary_time", return_value=data),
            patch.object(schedules, "LAST_SUMMARY_FILE", str(summary_file)),
        ):
            result = await schedules.list_last_summary_times()
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)

    assert result["success"] is True
    assert result["data"]["total"] == 1
    assert result["data"]["items"][0]["channel"] == "https://t.me/example"
    assert result["data"]["items"][0]["time"] == time_value.isoformat()
    assert result["data"]["file_exists"] is True


@pytest.mark.asyncio
async def test_update_last_summary_time_calls_manager():
    """更新上次总结时间接口应调用 summary_time_manager 保存新格式数据。"""
    with patch("core.summary_time_manager.save_last_summary_time") as save:
        result = await schedules.update_last_summary_time(
            "@example",
            LastSummaryTimeUpdateRequest(
                time="2026-01-01T00:00:00Z",
                summary_message_ids=[10],
                poll_message_ids=[11],
                button_message_ids=[12],
            ),
        )

    assert result["success"] is True
    args = save.call_args.args
    kwargs = save.call_args.kwargs
    assert args[0] == "https://t.me/example"
    assert args[1].tzinfo is not None
    assert kwargs["summary_message_ids"] == [10]
    assert kwargs["poll_message_ids"] == [11]
    assert kwargs["button_message_ids"] == [12]


@pytest.mark.asyncio
async def test_delete_last_summary_time_removes_channel():
    """删除指定频道总结时间应只移除对应记录。"""
    tmp_path = _tmp_dir("delete_one")
    summary_file = tmp_path / ".last_summary_time.json"
    try:
        summary_file.write_text(
            '{"https://t.me/example":{"time":"2026-01-01T00:00:00+00:00"},"https://t.me/keep":{"time":"2026-01-02T00:00:00+00:00"}}',
            encoding="utf-8",
        )

        with patch.object(schedules, "LAST_SUMMARY_FILE", str(summary_file)):
            result = await schedules.delete_last_summary_time("@example")

        assert result["success"] is True
        content = summary_file.read_text(encoding="utf-8")
        assert "https://t.me/example" not in content
        assert "https://t.me/keep" in content
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.mark.asyncio
async def test_delete_all_last_summary_times_removes_file():
    """清空总结时间应删除 .last_summary_time.json 文件。"""
    tmp_path = _tmp_dir("delete_all")
    summary_file = tmp_path / ".last_summary_time.json"
    try:
        summary_file.write_text("{}", encoding="utf-8")

        with patch.object(schedules, "LAST_SUMMARY_FILE", str(summary_file)):
            result = await schedules.delete_all_last_summary_times()

        assert result["success"] is True
        assert result["data"]["removed"] is True
        assert not summary_file.exists()
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.mark.asyncio
async def test_delete_poll_regenerations_file_removes_file():
    """删除投票重生成文件接口应删除 .poll_regenerations.json。"""
    tmp_path = _tmp_dir("delete_poll")
    poll_file = tmp_path / ".poll_regenerations.json"
    try:
        poll_file.write_text("{}", encoding="utf-8")

        with patch.object(schedules, "POLL_REGENERATIONS_FILE", str(poll_file)):
            result = await schedules.delete_poll_regenerations_file()

        assert result["success"] is True
        assert result["data"]["removed"] is True
        assert not poll_file.exists()
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)
