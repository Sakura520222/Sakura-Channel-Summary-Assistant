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
数据库管理 API 路由

提供表列表、表结构查看、数据浏览与 CRUD 操作。

安全策略：
- 表名必须通过数据库管理器白名单校验。
- 搜索、排序和写入列名必须通过实际表结构校验。
- 所有写操作都会写入 WebUI 审计日志。
"""

import json
import logging
import time
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Request

from core.web_api.deps import (
    actor_from_request,
    audit_duration,
    get_database_or_none,
    maybe_await,
    record_system_audit,
)
from core.web_api.schemas.database import RowCreateRequest, RowUpdateRequest

logger = logging.getLogger(__name__)

router = APIRouter()


def _validate_table(db, table: str) -> None:
    """验证表名是否在白名单中，防止操作未授权表。"""
    if not db or not hasattr(db, "table_exists"):
        raise HTTPException(status_code=503, detail="数据库管理器不可用")
    if not db.table_exists(table):
        raise HTTPException(status_code=404, detail=f"表 '{table}' 不存在或不允许访问")


@router.get("")
async def list_tables():
    """列出所有允许访问的表及基本信息（行数、大小、引擎）。"""
    db = get_database_or_none()
    if not db:
        raise HTTPException(status_code=503, detail="数据库管理器不可用")

    try:
        tables = await maybe_await(db.list_tables())
        return {"success": True, "data": tables}
    except Exception as e:
        logger.error(f"列出数据库表失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{table}")
async def get_table_schema(table: str):
    """获取表的列信息和主键。

    Args:
        table: 表名
    """
    db = get_database_or_none()
    _validate_table(db, table)

    try:
        columns = await maybe_await(db.describe_table(table))
        pk_column = await maybe_await(db.get_primary_key(table))
        return {
            "success": True,
            "data": {
                "table_name": table,
                "columns": columns,
                "primary_key": pk_column,
            },
        }
    except Exception as e:
        logger.error(f"获取表结构失败 {table}: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{table}/rows")
async def query_table_rows(
    table: str,
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    search_column: str | None = Query(default=None, description="搜索列名"),
    search_keyword: str | None = Query(default=None, max_length=100, description="搜索关键词"),
    order_by: str | None = Query(default=None, description="排序列名"),
    order_dir: Literal["ASC", "DESC"] = Query(default="ASC", description="排序方向 ASC/DESC"),
):
    """分页浏览表数据，支持按列搜索和排序。"""
    db = get_database_or_none()
    _validate_table(db, table)

    try:
        result = await maybe_await(
            db.query_table(
                table=table,
                page=page,
                page_size=page_size,
                search_column=search_column,
                search_keyword=search_keyword,
                order_by=order_by,
                order_dir=order_dir,
            )
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"查询表数据失败 {table}: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{table}/rows")
async def create_row(table: str, request_data: RowCreateRequest, request: Request):
    """插入新行。"""
    started_at = time.perf_counter()
    actor = actor_from_request(request)
    db = get_database_or_none()
    _validate_table(db, table)

    try:
        new_id = await maybe_await(db.insert_row(table, request_data.data))
        await record_system_audit(
            action="database.row.create",
            actor=actor,
            target=table,
            params_summary=json.dumps(
                {"columns": list(request_data.data.keys())}, ensure_ascii=False
            ),
            success=True,
            message="插入成功",
            duration_ms=audit_duration(started_at),
        )
        if new_id is not None:
            return {"success": True, "message": "插入成功", "data": {"id": new_id}}
        return {"success": True, "message": "插入成功"}
    except ValueError as e:
        message = str(e)
        await record_system_audit(
            action="database.row.create",
            actor=actor,
            target=table,
            params_summary=json.dumps(
                {"columns": list(request_data.data.keys())}, ensure_ascii=False
            ),
            success=False,
            message=message,
            duration_ms=audit_duration(started_at),
        )
        raise HTTPException(status_code=400, detail=message) from e
    except Exception as e:
        message = f"插入行失败: {type(e).__name__}: {e}"
        await record_system_audit(
            action="database.row.create",
            actor=actor,
            target=table,
            params_summary=json.dumps(
                {"columns": list(request_data.data.keys())}, ensure_ascii=False
            ),
            success=False,
            message=message,
            duration_ms=audit_duration(started_at),
        )
        logger.error(f"插入行失败 {table}: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=message) from e


@router.put("/{table}/rows/{pk}")
async def update_row(
    table: str,
    pk: str,
    request_data: RowUpdateRequest,
    request: Request,
):
    """更新一行数据（以主键定位）。"""
    started_at = time.perf_counter()
    actor = actor_from_request(request)
    db = get_database_or_none()
    _validate_table(db, table)

    pk_column = await maybe_await(db.get_primary_key(table))
    if not pk_column:
        raise HTTPException(status_code=400, detail=f"表 '{table}' 没有主键，无法定位行")

    # 尝试将主键值转为整数
    pk_value: int | str
    try:
        pk_value = int(pk)
    except (ValueError, TypeError):
        pk_value = pk

    try:
        success = await maybe_await(db.update_row(table, pk_column, pk_value, request_data.data))
        if not success:
            raise HTTPException(status_code=404, detail="未找到匹配的行")
        await record_system_audit(
            action="database.row.update",
            actor=actor,
            target=f"{table}.{pk_column}={pk}",
            params_summary=json.dumps(
                {"columns": list(request_data.data.keys())}, ensure_ascii=False
            ),
            success=True,
            message="更新成功",
            duration_ms=audit_duration(started_at),
        )
        return {"success": True, "message": "更新成功"}
    except ValueError as e:
        message = str(e)
        await record_system_audit(
            action="database.row.update",
            actor=actor,
            target=f"{table}.{pk_column}={pk}",
            params_summary=json.dumps(
                {"columns": list(request_data.data.keys())}, ensure_ascii=False
            ),
            success=False,
            message=message,
            duration_ms=audit_duration(started_at),
        )
        raise HTTPException(status_code=400, detail=message) from e
    except HTTPException as e:
        await record_system_audit(
            action="database.row.update",
            actor=actor,
            target=f"{table}.{pk_column}={pk}",
            params_summary=json.dumps(
                {"columns": list(request_data.data.keys())}, ensure_ascii=False
            ),
            success=False,
            message=str(e.detail),
            duration_ms=audit_duration(started_at),
        )
        raise
    except Exception as e:
        message = f"更新行失败: {type(e).__name__}: {e}"
        await record_system_audit(
            action="database.row.update",
            actor=actor,
            target=f"{table}.{pk_column}={pk}",
            params_summary=json.dumps(
                {"columns": list(request_data.data.keys())}, ensure_ascii=False
            ),
            success=False,
            message=message,
            duration_ms=audit_duration(started_at),
        )
        logger.error(f"更新行失败 {table}: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=message) from e


@router.delete("/{table}/rows/{pk}")
async def delete_row(table: str, pk: str, request: Request):
    """删除一行数据（以主键定位）。"""
    started_at = time.perf_counter()
    actor = actor_from_request(request)
    db = get_database_or_none()
    _validate_table(db, table)

    pk_column = await maybe_await(db.get_primary_key(table))
    if not pk_column:
        raise HTTPException(status_code=400, detail=f"表 '{table}' 没有主键，无法定位行")

    pk_value: int | str
    try:
        pk_value = int(pk)
    except (ValueError, TypeError):
        pk_value = pk

    try:
        success = await maybe_await(db.delete_row(table, pk_column, pk_value))
        if not success:
            raise HTTPException(status_code=404, detail="未找到匹配的行")
        await record_system_audit(
            action="database.row.delete",
            actor=actor,
            target=f"{table}.{pk_column}={pk}",
            success=True,
            message="删除成功",
            duration_ms=audit_duration(started_at),
        )
        return {"success": True, "message": "删除成功"}
    except HTTPException as e:
        await record_system_audit(
            action="database.row.delete",
            actor=actor,
            target=f"{table}.{pk_column}={pk}",
            success=False,
            message=str(e.detail),
            duration_ms=audit_duration(started_at),
        )
        raise
    except Exception as e:
        message = f"删除行失败: {type(e).__name__}: {e}"
        await record_system_audit(
            action="database.row.delete",
            actor=actor,
            target=f"{table}.{pk_column}={pk}",
            success=False,
            message=message,
            duration_ms=audit_duration(started_at),
        )
        logger.error(f"删除行失败 {table}: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=message) from e
