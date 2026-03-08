# Infrastructure: Database layer
"""
Database abstraction layer supporting multiple backends (SQLite, MySQL).
"""

from .base import DatabaseManagerBase
from .manager import DatabaseManagerLegacy, get_db_manager, reload_db_manager
from .migrator import DatabaseMigrator
from .mysql import MySQLManager
from .sqlite import SQLiteManager

__all__ = [
    "DatabaseManagerBase",
    "MySQLManager",
    "SQLiteManager",
    "DatabaseMigrator",
    "DatabaseManagerLegacy",
    "get_db_manager",
    "reload_db_manager",
]
