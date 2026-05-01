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
定时任务 API 路由

提供频道总结定时任务的查看、设置和清除功能。
"""

import asyncio
import json
import logging
import os
from datetime import UTC, datetime

import aiofiles
import aiofiles.ospath
from fastapi import APIRouter, HTTPException

from core.config import LAST_SUMMARY_FILE, normalize_channel_id
from core.infrastructure.utils.constants import POLL_REGENERATIONS_FILE
from core.web_api.deps import get_config, write_config
from core.web_api.schemas.schedule import (
    LastSummaryTimeUpdateRequest,
    ScheduleInfo,
    ScheduleUpdateRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()

_summary_time_file_lock = asyncio.Lock()


@router.get("")
async def list_schedules():
    """获取所有频道的定时任务配置"""
    try:
        config = get_config()
        schedules = config.get("summary_schedules", {})
        channels = config.get("channels", [])

        schedule_list = []
        for channel, schedule_data in schedules.items():
            schedule_list.append(
                ScheduleInfo(
                    channel=channel,
                    frequency=schedule_data.get("frequency", "daily"),
                    hour=schedule_data.get("hour", 9),
                    minute=schedule_data.get("minute", 0),
                    days=schedule_data.get("days", []),
                ).model_dump()
            )

        # 标记没有设置定时任务的频道
        unscheduled = [ch for ch in channels if ch not in schedules]

        return {
            "success": True,
            "data": {
                "schedules": schedule_list,
                "unscheduled_channels": unscheduled,
                "total": len(schedule_list),
            },
        }

    except Exception as e:
        logger.error(f"获取定时任务列表失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


# ==================== 上次总结时间 ====================


def _serialize_summary_time_entry(channel: str, data: dict) -> dict:
    """序列化单个频道的上次总结时间记录。"""
    time_value = data.get("time")
    if isinstance(time_value, datetime):
        time_text = time_value.isoformat()
    else:
        time_text = str(time_value) if time_value is not None else ""
    return {
        "channel": channel,
        "time": time_text,
        "summary_message_ids": data.get("summary_message_ids", []),
        "poll_message_ids": data.get("poll_message_ids", []),
        "button_message_ids": data.get("button_message_ids", []),
    }


def _clean_summary_channel(channel: str) -> str:
    """清理 WebUI 自动补全可能带入的频道展示文本。"""
    channel = channel.strip()
    if " (" in channel and channel.endswith(")"):
        channel = channel.rsplit(" (", maxsplit=1)[0]
    return normalize_channel_id(channel)


@router.get("/summary-times")
async def list_last_summary_times():
    """读取所有频道的上次总结时间记录。"""
    try:
        from core.summary_time_manager import load_last_summary_time

        data = load_last_summary_time(include_report_ids=True) or {}
        items = [_serialize_summary_time_entry(channel, value) for channel, value in data.items()]
        return {
            "success": True,
            "data": {
                "items": items,
                "total": len(items),
                "file_exists": await aiofiles.ospath.exists(LAST_SUMMARY_FILE),
                "file_path": LAST_SUMMARY_FILE,
            },
        }
    except Exception as e:
        logger.error(f"读取上次总结时间失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/summary-times/{channel:path}")
async def update_last_summary_time(channel: str, request: LastSummaryTimeUpdateRequest):
    """更新指定频道的上次总结时间记录。"""
    try:
        from core.summary_time_manager import save_last_summary_time

        channel = _clean_summary_channel(channel)
        try:
            time_to_save = datetime.fromisoformat(request.time.replace("Z", "+00:00"))
        except ValueError as e:
            raise HTTPException(status_code=400, detail="时间格式无效，请使用 ISO 8601 格式") from e
        if time_to_save.tzinfo is None:
            time_to_save = time_to_save.replace(tzinfo=UTC)

        save_last_summary_time(
            channel,
            time_to_save,
            summary_message_ids=request.summary_message_ids,
            poll_message_ids=request.poll_message_ids,
            button_message_ids=request.button_message_ids,
        )
        logger.info(f"已通过 WebUI 更新上次总结时间: {channel}")
        return {"success": True, "message": f"上次总结时间已更新: {channel}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新上次总结时间失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/summary-times/{channel:path}")
async def delete_last_summary_time(channel: str):
    """删除指定频道的上次总结时间记录。"""
    try:
        channel = _clean_summary_channel(channel)
        async with _summary_time_file_lock:
            try:
                async with aiofiles.open(LAST_SUMMARY_FILE, encoding="utf-8") as f:
                    content = (await f.read()).strip()
                data = json.loads(content) if content else {}
            except FileNotFoundError:
                return {"success": False, "message": "上次总结时间文件不存在"}
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=409, detail="上次总结时间文件内容已损坏") from e

            if channel not in data:
                return {"success": False, "message": f"该频道无上次总结时间记录: {channel}"}

            del data[channel]
            try:
                if data:
                    async with aiofiles.open(LAST_SUMMARY_FILE, "w", encoding="utf-8") as f:
                        await f.write(json.dumps(data, ensure_ascii=False, indent=2))
                else:
                    await _remove_file_if_exists(LAST_SUMMARY_FILE)
            except FileNotFoundError:
                return {"success": False, "message": "上次总结时间文件已被其他进程删除"}

        logger.info(f"已通过 WebUI 删除上次总结时间: {channel}")
        return {"success": True, "message": f"上次总结时间已删除: {channel}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除上次总结时间失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/summary-times")
async def delete_all_last_summary_times():
    """删除全部上次总结时间记录文件。"""
    try:
        removed = await _remove_file_if_exists(LAST_SUMMARY_FILE)
        message = "已删除全部上次总结时间记录" if removed else "上次总结时间文件不存在"
        logger.info(f"已通过 WebUI 删除全部上次总结时间记录: removed={removed}")
        return {"success": True, "message": message, "data": {"removed": removed}}
    except Exception as e:
        logger.error(f"删除全部上次总结时间失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/poll-regenerations")
async def delete_poll_regenerations_file():
    """删除投票重新生成记录文件。"""
    try:
        removed = await _remove_file_if_exists(POLL_REGENERATIONS_FILE)
        message = "已删除投票重新生成记录文件" if removed else "投票重新生成记录文件不存在"
        logger.info(f"已通过 WebUI 删除投票重新生成记录文件: removed={removed}")
        return {"success": True, "message": message, "data": {"removed": removed}}
    except Exception as e:
        logger.error(f"删除投票重新生成记录文件失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


async def _remove_file_if_exists(path: str) -> bool:
    """异步删除文件，返回是否实际删除。"""
    try:
        await asyncio.to_thread(os.remove, path)
        return True
    except FileNotFoundError:
        return False


@router.get("/{channel:path}")
async def get_schedule(channel: str):
    """获取指定频道的定时任务配置"""
    try:
        channel = normalize_channel_id(channel)
        config = get_config()
        schedules = config.get("summary_schedules", {})

        if channel not in schedules:
            return {"success": True, "data": None, "message": "该频道未配置定时任务"}

        schedule_data = schedules[channel]
        return {
            "success": True,
            "data": ScheduleInfo(
                channel=channel,
                frequency=schedule_data.get("frequency", "daily"),
                hour=schedule_data.get("hour", 9),
                minute=schedule_data.get("minute", 0),
                days=schedule_data.get("days", []),
            ).model_dump(),
        }

    except Exception as e:
        logger.error(f"获取定时任务失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/{channel:path}")
async def update_schedule(channel: str, request: ScheduleUpdateRequest):
    """设置指定频道的定时任务"""
    try:
        channel = normalize_channel_id(channel)
        config = get_config()

        # 验证频道是否在列表中
        channels = config.get("channels", [])
        if channel not in channels:
            return {"success": False, "message": f"频道不在监控列表中: {channel}"}

        # 验证星期配置（仅 weekly 需要）
        valid_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        if request.frequency == "weekly":
            for day in request.days:
                if day.lower() not in valid_days:
                    return {"success": False, "message": f"无效的星期: {day}"}

        # 更新定时任务
        schedules = config.get("summary_schedules", {})
        schedules[channel] = {
            "frequency": request.frequency,
            "hour": request.hour,
            "minute": request.minute,
            "days": [d.lower() for d in request.days] if request.frequency == "weekly" else [],
        }
        config["summary_schedules"] = schedules
        write_config(config)

        logger.info(
            f"已通过 WebUI 设置定时任务: {channel} -> {request.frequency} {request.hour}:{request.minute:02d}"
        )
        return {"success": True, "message": f"定时任务已设置: {channel}"}

    except Exception as e:
        logger.error(f"设置定时任务失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/{channel:path}")
async def delete_schedule(channel: str):
    """清除指定频道的定时任务"""
    try:
        channel = normalize_channel_id(channel)
        config = get_config()
        schedules = config.get("summary_schedules", {})

        if channel not in schedules:
            return {"success": False, "message": f"该频道未配置定时任务: {channel}"}

        del schedules[channel]
        config["summary_schedules"] = schedules
        write_config(config)

        logger.info(f"已通过 WebUI 清除定时任务: {channel}")
        return {"success": True, "message": f"定时任务已清除: {channel}"}

    except Exception as e:
        logger.error(f"清除定时任务失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e
