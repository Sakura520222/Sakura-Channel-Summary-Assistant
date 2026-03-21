# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可
#
# - 署名：必须提供本项目的原始来源链接
# - 相同方式共享：衍生作品必须采用相同的许可证
#
# 本项目源代码：https://github.com/Sakura520222/Sakura-Bot
# 许可证全文：参见 LICENSE 文件

"""数据库管理器模块

提供数据库管理器的工厂函数，仅支持MySQL数据库。
"""

import logging

from core.settings import get_settings

logger = logging.getLogger(__name__)

# 全局数据库管理器实例
db_manager = None


def get_db_manager():
    """
    获取全局数据库管理器实例（仅MySQL）

    注意：初始化由调用者在异步上下文中处理，以避免事件循环问题
    """
    global db_manager
    if db_manager is not None:
        return db_manager

    settings = get_settings()

    from .mysql import MySQLManager

    logger.info("使用 MySQL 数据库管理器")
    db_manager = MySQLManager(
        host=settings.database.mysql_host,
        port=settings.database.mysql_port,
        user=settings.database.mysql_user,
        password=settings.database.mysql_password,
        database=settings.database.mysql_database,
        charset=settings.database.mysql_charset,
        pool_size=settings.database.mysql_pool_size,
        max_overflow=settings.database.mysql_max_overflow,
        pool_timeout=settings.database.mysql_pool_timeout,
    )

    return db_manager


async def reload_db_manager():
    """重新加载数据库管理器（用于配置变更后）"""
    global db_manager

    # 关闭旧的连接池
    if db_manager is not None and hasattr(db_manager, "pool"):
        if db_manager.pool is not None:
            db_manager.pool.close()
            await db_manager.pool.wait_closed()
            logger.info("旧的MySQL连接池已关闭")

    # 重置实例
    db_manager = None

    # 获取新的实例
    new_manager = get_db_manager()
    await new_manager.init_database()

    logger.info("数据库管理器已重新加载")
    return new_manager
