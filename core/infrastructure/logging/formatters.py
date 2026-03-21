# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可
#
# - 署名：必须提供本项目的原始来源链接
# - 相同方式共享：衍生作品必须采用相同的许可证
#
# 本项目源代码：https://github.com/Sakura520222/Sakura-Bot
# 许可证全文：参见 LICENSE 文件

"""日志格式化器

提供不同风格的日志格式化器。
"""

import logging


class ColorFormatter(logging.Formatter):
    """彩色控制台格式化器

    为不同级别的日志添加颜色，提高可读性。
    """

    # ANSI 颜色代码
    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[35m",  # 紫色
    }
    RESET = "\033[0m"

    def __init__(self, fmt: str | None = None, datefmt: str | None = None):
        """初始化格式化器"""
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录

        Args:
            record: 日志记录

        Returns:
            格式化后的日志字符串
        """
        # 保存原始级别名称
        original_levelname = record.levelname

        # 获取日志级别对应的颜色
        color = self.COLORS.get(record.levelname, "")

        # 添加颜色到级别名称
        if color:
            record.levelname = f"{color}{record.levelname}{self.RESET}"

        # 格式化消息
        result = super().format(record)

        # 恢复原始级别名称
        record.levelname = original_levelname

        return result


class FileFormatter(logging.Formatter):
    """文件日志格式化器

    提供更详细的文件日志格式，包含文件名和行号。
    """

    def __init__(self, fmt: str | None = None, datefmt: str | None = None):
        """初始化格式化器"""
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录

        Args:
            record: 日志记录

        Returns:
            格式化后的日志字符串
        """
        # 确保异常信息被正确格式化
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)

        return super().format(record)
