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


class ComponentFormatter(ColorFormatter):
    """组件日志格式化器

    为日志消息添加组件前缀，便于在控制台中区分不同进程/组件。
    """

    def __init__(
        self,
        component_name: str,
        fmt: str | None = None,
        datefmt: str | None = None,
    ):
        """初始化格式化器

        Args:
            component_name: 组件名称
            fmt: 日志格式
            datefmt: 日期格式
        """
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.component_name = component_name

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        original_msg = record.msg
        if isinstance(record.msg, str) and not record.msg.startswith(f"[{self.component_name}]"):
            record.msg = f"[{self.component_name}] {record.msg}"

        try:
            return super().format(record)
        finally:
            record.msg = original_msg


def get_component_log_file_path(
    component_log_file_name: str,
    base_log_file_path: str | None = None,
) -> str:
    """获取组件日志文件路径

    Args:
        component_log_file_name: 组件日志文件名
        base_log_file_path: 主日志文件路径

    Returns:
        组件日志文件路径
    """
    if base_log_file_path:
        return str(Path(base_log_file_path).parent / component_log_file_name)

    return str(Path(DEFAULT_LOG_DIR) / component_log_file_name)


def _create_console_handler(
    log_level: int,
    log_colorize: bool,
    formatter: logging.Formatter | None = None,
) -> logging.Handler:
    """创建控制台日志处理器"""
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if formatter:
        console_handler.setFormatter(formatter)
    elif log_colorize and sys.stdout.isatty():
        console_handler.setFormatter(ColorFormatter(fmt=CONSOLE_FORMAT, datefmt=DATE_FORMAT))
    else:
        console_handler.setFormatter(logging.Formatter(fmt=CONSOLE_FORMAT, datefmt=DATE_FORMAT))

    return console_handler


def _create_file_handler(
    log_file_path: str,
    log_level: int,
    log_file_max_size: int,
    log_file_backup_count: int,
    formatter: logging.Formatter | None = None,
) -> logging.Handler:
    """创建文件日志处理器"""
    log_file_path_obj = Path(log_file_path)
    log_file_path_obj.parent.mkdir(parents=True, exist_ok=True)

    file_handler = SafeRotatingFileHandler(
        filename=str(log_file_path_obj),
        maxBytes=log_file_max_size,
        backupCount=log_file_backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter or FileFormatter(fmt=FILE_FORMAT, datefmt=DATE_FORMAT))

    return file_handler


def _configure_third_party_loggers() -> None:
    """配置第三方库日志级别，减少噪音"""
    logging.getLogger("telethon").setLevel(logging.WARNING)
    logging.getLogger("telethon.client.updates").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def _clear_handlers(target_logger: logging.Logger) -> None:
    """清理并关闭日志处理器"""
    for handler in target_logger.handlers[:]:
        target_logger.removeHandler(handler)
        handler.close()


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
    _clear_handlers(root_logger)

    # 添加控制台处理器
    if log_to_console:
        root_logger.addHandler(_create_console_handler(log_level, log_colorize))

    # 添加文件处理器
    if log_to_file:
        # 确定日志文件路径
        if log_file_path is None:
            log_dir = Path(DEFAULT_LOG_DIR)
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file_path = str(log_dir / DEFAULT_LOG_FILE)

        root_logger.addHandler(
            _create_file_handler(
                log_file_path=log_file_path,
                log_level=log_level,
                log_file_max_size=log_file_max_size,
                log_file_backup_count=log_file_backup_count,
            )
        )

    # 设置第三方库的日志级别（减少噪音）
    _configure_third_party_loggers()


def setup_component_logging(
    component_name: str,
    logger_names: list[str],
    log_level: int = logging.INFO,
    log_to_file: bool = True,
    base_log_file_path: str | None = None,
    component_log_file_name: str | None = None,
    log_file_max_size: int = DEFAULT_MAX_BYTES,
    log_file_backup_count: int = DEFAULT_BACKUP_COUNT,
    log_to_console: bool = True,
    log_colorize: bool = True,
    configure_root: bool = False,
) -> str:
    """设置组件日志

    Args:
        component_name: 组件名称，用于控制台消息前缀
        logger_names: 需要挂载组件 handler 的 logger 名称
        log_level: 日志级别
        log_to_file: 是否输出到文件
        base_log_file_path: 主日志文件路径，用于推导组件日志目录
        component_log_file_name: 组件日志文件名
        log_file_max_size: 单个日志文件最大大小
        log_file_backup_count: 保留的备份文件数量
        log_to_console: 是否输出到控制台
        log_colorize: 是否使用彩色输出
        configure_root: 是否配置根日志记录器，适用于独立进程

    Returns:
        组件日志文件路径
    """
    if component_log_file_name is None:
        component_log_file_name = f"{component_name.lower()}.log"

    component_log_file_path = get_component_log_file_path(
        component_log_file_name,
        base_log_file_path,
    )

    target_loggers = [logging.getLogger()] if configure_root else []
    target_loggers.extend(logging.getLogger(name) for name in logger_names)

    shared_handlers: list[logging.Handler] = []

    if log_to_console:
        shared_handlers.append(
            _create_console_handler(
                log_level=log_level,
                log_colorize=log_colorize,
                formatter=ComponentFormatter(
                    component_name=component_name,
                    fmt=CONSOLE_FORMAT,
                    datefmt=DATE_FORMAT,
                ),
            )
        )

    if log_to_file:
        shared_handlers.append(
            _create_file_handler(
                log_file_path=component_log_file_path,
                log_level=log_level,
                log_file_max_size=log_file_max_size,
                log_file_backup_count=log_file_backup_count,
            )
        )

    for target_logger in target_loggers:
        target_logger.setLevel(log_level)
        _clear_handlers(target_logger)

        for handler in shared_handlers:
            if handler not in target_logger.handlers:
                target_logger.addHandler(handler)

        target_logger.propagate = False

    _configure_third_party_loggers()
    return component_log_file_path
