# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可
#
# - 署名：必须提供本项目的原始来源链接
# - 相同方式共享：衍生作品必须采用相同的许可证
#
# 本项目源代码：https://github.com/Sakura520222/Sakura-Bot
# 许可证全文：参见 LICENSE 文件

"""日志配置模块

提供统一的日志配置管理，支持控制台和文件输出，支持日志轮转。
"""

import logging
import sys
from pathlib import Path

from .formatters import ColorFormatter, FileFormatter
from .handlers import SafeRotatingFileHandler

# 默认配置
DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FILE = "sakura-bot.log"
DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10MB
DEFAULT_BACKUP_COUNT = 5

# 日志格式
CONSOLE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
FILE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    log_level: int = logging.INFO,
    log_to_file: bool = True,
    log_file_path: str | None = None,
    log_file_max_size: int = DEFAULT_MAX_BYTES,
    log_file_backup_count: int = DEFAULT_BACKUP_COUNT,
    log_to_console: bool = True,
    log_colorize: bool = True,
) -> None:
    """设置日志系统

    Args:
        log_level: 日志级别
        log_to_file: 是否输出到文件
        log_file_path: 日志文件路径
        log_file_max_size: 单个日志文件最大大小
        log_file_backup_count: 保留的备份文件数量
        log_to_console: 是否输出到控制台
        log_colorize: 是否使用彩色输出
    """
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清除现有的处理器（避免重复添加）
    root_logger.handlers.clear()

    # 添加控制台处理器
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        if log_colorize and sys.stdout.isatty():
            console_handler.setFormatter(ColorFormatter(fmt=CONSOLE_FORMAT, datefmt=DATE_FORMAT))
        else:
            console_handler.setFormatter(logging.Formatter(fmt=CONSOLE_FORMAT, datefmt=DATE_FORMAT))

        root_logger.addHandler(console_handler)

    # 添加文件处理器
    if log_to_file:
        # 确定日志文件路径
        if log_file_path is None:
            log_dir = Path(DEFAULT_LOG_DIR)
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file_path = str(log_dir / DEFAULT_LOG_FILE)
        else:
            # 确保日志目录存在
            log_file_path_obj = Path(log_file_path)
            log_file_path_obj.parent.mkdir(parents=True, exist_ok=True)

        file_handler = SafeRotatingFileHandler(
            filename=log_file_path,
            maxBytes=log_file_max_size,
            backupCount=log_file_backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(FileFormatter(fmt=FILE_FORMAT, datefmt=DATE_FORMAT))

        root_logger.addHandler(file_handler)

    # 设置第三方库的日志级别（减少噪音）
    logging.getLogger("telethon").setLevel(logging.WARNING)
    logging.getLogger("telethon.client.updates").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
