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

import logging

from fastapi import APIRouter, HTTPException

from core.config import normalize_channel_id
from core.web_api.deps import get_config, write_config
from core.web_api.schemas.schedule import ScheduleInfo, ScheduleUpdateRequest

logger = logging.getLogger(__name__)

router = APIRouter()


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
