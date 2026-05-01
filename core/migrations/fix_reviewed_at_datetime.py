# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可

"""
数据库迁移脚本：修复 reviewed_at 列的 datetime 格式不兼容问题

问题：最近的更新使用 datetime.now(UTC) 生成了带UTC时区的datetime对象，
      但MySQL的DATETIME列不支持ISO格式的时区信息（如 2026-04-24T15:43:57.758685+00:00）

解决方案：
1. 查找所有无法解析的 reviewed_at 值
2. 尝试从ISO格式转换为MySQL支持的格式
3. 如果无法解析，设置为NULL

版本：v1.8.5
"""

import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def fix_reviewed_at_datetime(db):
    """
    修复 submissions 表中 reviewed_at 列的 datetime 格式问题

    Args:
        db: 数据库管理器实例（MySQLManager）

    Returns:
        dict: 迁移结果
    """
    result = {"success": False, "message": "", "details": {}}

    try:
        db_type = db.__class__.__name__
        logger.info(f"开始修复 reviewed_at datetime 格式问题 (数据库类型: {db_type})")

        if db_type == "MySQLManager":
            result = await _fix_mysql(db)
        else:
            result["message"] = f"不支持的数据库类型: {db_type}"

        return result

    except Exception as e:
        logger.error(f"修复 reviewed_at datetime 格式失败: {type(e).__name__}: {e}", exc_info=True)
        result["message"] = f"修复失败: {str(e)}"
        return result


async def _fix_mysql(db):
    """修复 MySQL 数据库中的 reviewed_at 数据"""
    result = {"success": False, "message": "", "fixed_count": 0, "invalid_count": 0}

    try:
        async with db.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # 第一步：找出所有包含 'T' 的 reviewed_at 值（这些是ISO格式，不兼容MySQL）
                await cursor.execute(
                    """
                    SELECT id, reviewed_at FROM submissions
                    WHERE reviewed_at IS NOT NULL
                    AND reviewed_at LIKE '%T%'
                    """
                )
                rows = await cursor.fetchall()

                logger.info(f"找到 {len(rows)} 条需要修复的记录")

                fixed_count = 0
                invalid_count = 0

                for submission_id, reviewed_at_str in rows:
                    try:
                        # 尝试解析ISO格式的datetime（2026-04-24T15:43:57.758685+00:00）
                        # 移除时区信息并转换为MySQL格式
                        if isinstance(reviewed_at_str, str):
                            # 移除时区信息（+00:00 或 Z）
                            clean_str = reviewed_at_str.replace("+00:00", "").replace("Z", "")
                            # 如果包含毫秒，截断到秒
                            if "." in clean_str:
                                clean_str = clean_str.split(".")[0]
                            # 转换为datetime并重新格式化
                            dt = datetime.fromisoformat(clean_str)
                            formatted_dt = dt.strftime("%Y-%m-%d %H:%M:%S")

                            # 更新数据库
                            await cursor.execute(
                                "UPDATE submissions SET reviewed_at = %s WHERE id = %s",
                                (formatted_dt, submission_id),
                            )
                            fixed_count += 1
                        else:
                            # 不是字符串，设置为NULL
                            await cursor.execute(
                                "UPDATE submissions SET reviewed_at = NULL WHERE id = %s",
                                (submission_id,),
                            )
                            invalid_count += 1

                    except Exception as e:
                        logger.warning(f"无法修复 submission {submission_id} 的 reviewed_at: {e}")
                        # 无法解析则设置为NULL
                        await cursor.execute(
                            "UPDATE submissions SET reviewed_at = NULL WHERE id = %s",
                            (submission_id,),
                        )
                        invalid_count += 1

                await conn.commit()

                result["success"] = True
                result["fixed_count"] = fixed_count
                result["invalid_count"] = invalid_count
                result["message"] = (
                    f"修复完成: {fixed_count} 条记录已修复, {invalid_count} 条记录无法解析已设为NULL"
                )

                logger.info(result["message"])

    except Exception as e:
        logger.error(f"MySQL 修复过程失败: {type(e).__name__}: {e}", exc_info=True)
        result["message"] = f"MySQL 修复失败: {str(e)}"

    return result


# 便捷函数：在应用启动时自动运行迁移
async def ensure_reviewed_at_datetime_fixed(db):
    """
    确保 submissions 表的 reviewed_at 列 datetime 格式已修复

    在应用启动时调用，自动检查并执行修复

    Args:
        db: 数据库管理器实例
    """
    try:
        result = await fix_reviewed_at_datetime(db)
        if result["success"]:
            logger.info(f"✅ reviewed_at datetime 格式修复完成: {result['message']}")
        else:
            logger.error(f"❌ reviewed_at datetime 格式修复失败: {result['message']}")
    except Exception as e:
        logger.error(f"❌ reviewed_at datetime 格式修复异常: {type(e).__name__}: {e}")


# 命令行执行支持
if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

    async def main():
        from core.infrastructure.database.manager import get_db_manager

        db = get_db_manager()
        if db is None:
            print("数据库管理器未初始化")
            return

        result = await fix_reviewed_at_datetime(db)
        print(f"迁移结果: {result}")

    asyncio.run(main())
