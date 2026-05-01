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
统计数据 API 路由

提供总结统计、历史记录、频道排名等数据查询。
"""

import logging

from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
async def get_stats():
    """获取总体统计数据"""
    try:
        db = _get_db()
        if not db:
            return {"success": False, "message": "数据库未连接"}

        stats_data = await db.get_statistics()
        return {"success": True, "data": stats_data}

    except Exception as e:
        logger.error(f"获取统计数据失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/summaries")
async def list_summaries(
    channel: str | None = Query(None, description="频道 URL 过滤"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
):
    """获取总结列表（分页）"""
    try:
        db = _get_db()
        if not db:
            return {"success": False, "message": "数据库未连接"}

        total = await db.count_summaries(channel_id=channel)
        summaries = await db.get_summaries(channel_id=channel, limit=limit, offset=offset)
        return {
            "success": True,
            "data": {
                "summaries": summaries or [],
                "total": total,
                "limit": limit,
                "offset": offset,
            },
        }

    except Exception as e:
        logger.error(f"获取总结列表失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/ranking")
async def get_channel_ranking():
    """获取频道排名"""
    try:
        db = _get_db()
        if not db:
            return {"success": False, "message": "数据库未连接"}

        ranking = await db.get_channel_ranking()
        return {"success": True, "data": ranking or []}

    except Exception as e:
        logger.error(f"获取频道排名失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/export")
async def export_summaries():
    """导出所有总结数据"""
    try:
        db = _get_db()
        if not db:
            return {"success": False, "message": "数据库未连接"}

        data = await db.export_summaries()
        return {"success": True, "data": data}

    except Exception as e:
        logger.error(f"导出总结数据失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


def _get_db():
    """安全获取数据库管理器"""
    try:
        from core.infrastructure.database.manager import get_db_manager

        return get_db_manager()
    except Exception:
        return None
